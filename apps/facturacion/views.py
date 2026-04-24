from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from datetime import date
from .models import Factura, AlertaCajero
from .serializers import FacturaSerializer, FacturaCreateSerializer, AlertaCajeroSerializer


class IsCajeroOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['cajero', 'admin']


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.select_related(
        'pedido__mesa', 'cajero'
    ).prefetch_related('pedido__detalles__producto').all()
    permission_classes = [IsCajeroOrAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return FacturaCreateSerializer
        return FacturaSerializer

    @action(detail=False, methods=['get'], url_path='reporte')
    def reporte(self, request):
        fecha_inicio = request.query_params.get('fecha_inicio', date.today().isoformat())
        fecha_fin = request.query_params.get('fecha_fin', date.today().isoformat())

        facturas = Factura.objects.filter(
            creado_en__date__gte=fecha_inicio,
            creado_en__date__lte=fecha_fin
        )

        total_ventas = facturas.aggregate(total=Sum('total'))['total'] or 0
        cantidad_ventas = facturas.count()

        por_dia = facturas.annotate(dia=TruncDate('creado_en')).values('dia').annotate(
            total=Sum('total'), cantidad=Count('id')
        ).order_by('dia')

        # Top products
        from apps.pedidos.models import DetallePedido
        top_productos = (
            DetallePedido.objects.filter(pedido__factura__in=facturas)
            .values('producto__nombre')
            .annotate(total_vendido=Sum('cantidad'))
            .order_by('-total_vendido')[:10]
        )

        return Response({
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'total_ventas': float(total_ventas),
            'cantidad_ventas': cantidad_ventas,
            'por_dia': list(por_dia),
            'top_productos': list(top_productos),
        })


class AlertaCajeroViewSet(viewsets.ModelViewSet):
    queryset = AlertaCajero.objects.select_related('pedido__mesa', 'cajero').all()
    serializer_class = AlertaCajeroSerializer

    def get_permissions(self):
        # Cajero/admin pueden crear; solo admin puede listar y marcar leído
        if self.action == 'create':
            return [IsCajeroOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.rol not in ['admin']:
            qs = qs.filter(cajero=self.request.user)
        solo_no_leidas = self.request.query_params.get('no_leidas')
        if solo_no_leidas:
            qs = qs.filter(leido=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(cajero=self.request.user)

    @action(detail=True, methods=['patch'], url_path='marcar_leida')
    def marcar_leida(self, request, pk=None):
        alerta = self.get_object()
        alerta.leido = True
        alerta.save()
        return Response(AlertaCajeroSerializer(alerta).data)
