from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from .models import ConfigCaja, CierreCaja
from .serializers import ConfigCajaSerializer, CierreCajaSerializer
from apps.facturacion.models import Factura


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class IsCajeroOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['cajero', 'admin']


class ConfigCajaView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAdmin()]
        return [IsCajeroOrAdmin()]

    def get(self, request):
        config, _ = ConfigCaja.objects.get_or_create(id=1)
        return Response(ConfigCajaSerializer(config).data)

    def put(self, request):
        config, _ = ConfigCaja.objects.get_or_create(id=1)
        serializer = ConfigCajaSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(actualizado_por=request.user)
        return Response(serializer.data)


class CierreCajaViewSet(viewsets.ModelViewSet):
    serializer_class = CierreCajaSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        return [IsCajeroOrAdmin()]

    def get_queryset(self):
        qs = CierreCaja.objects.select_related('cajero').all()
        if self.request.user.rol != 'admin':
            qs = qs.filter(cajero=self.request.user)
        return qs

    def perform_create(self, serializer):
        if CierreCaja.objects.filter(estado='abierta').exists():
            raise ValidationError('Ya hay una caja abierta. Ciérrala antes de abrir una nueva.')
        config, _ = ConfigCaja.objects.get_or_create(id=1)
        serializer.save(cajero=self.request.user, base_efectivo=config.base_efectivo)

    @action(detail=False, methods=['get'], url_path='actual')
    def actual(self, request):
        caja = CierreCaja.objects.filter(estado='abierta').first()
        if not caja:
            return Response({'abierta': False})
        return Response(CierreCajaSerializer(caja).data)

    @action(detail=True, methods=['get'], url_path='preview')
    def preview(self, request, pk=None):
        caja = self.get_object()
        now = timezone.now()
        facturas = Factura.objects.filter(
            creado_en__gte=caja.apertura_en,
            creado_en__lte=now,
        )
        totales = {
            t['metodo_pago']: float(t['suma'])
            for t in facturas.values('metodo_pago').annotate(suma=Sum('total'))
        }
        return Response({
            'base_efectivo': float(caja.base_efectivo),
            'total_efectivo': totales.get('efectivo', 0),
            'total_tarjeta': totales.get('tarjeta', 0),
            'total_transferencia': totales.get('transferencia', 0),
        })

    @action(detail=True, methods=['post'], url_path='cerrar')
    def cerrar(self, request, pk=None):
        caja = self.get_object()
        if caja.estado == 'cerrada':
            return Response({'detail': 'Esta caja ya está cerrada.'}, status=400)

        efectivo_contado = request.data.get('efectivo_contado')
        notas = request.data.get('notas', '')

        if efectivo_contado is None:
            return Response({'detail': 'efectivo_contado es requerido.'}, status=400)

        now = timezone.now()
        facturas = Factura.objects.filter(
            creado_en__gte=caja.apertura_en,
            creado_en__lte=now,
        )
        totales = {
            t['metodo_pago']: Decimal(str(t['suma']))
            for t in facturas.values('metodo_pago').annotate(suma=Sum('total'))
        }

        total_efectivo = totales.get('efectivo', Decimal('0'))
        total_tarjeta = totales.get('tarjeta', Decimal('0'))
        total_transferencia = totales.get('transferencia', Decimal('0'))
        efectivo_contado_dec = Decimal(str(efectivo_contado))
        diferencia = efectivo_contado_dec - (caja.base_efectivo + total_efectivo)

        caja.cierre_en = now
        caja.total_efectivo = total_efectivo
        caja.total_tarjeta = total_tarjeta
        caja.total_transferencia = total_transferencia
        caja.efectivo_contado = efectivo_contado_dec
        caja.diferencia = diferencia
        caja.notas = notas
        caja.estado = 'cerrada'
        caja.save()

        return Response(CierreCajaSerializer(caja).data)
