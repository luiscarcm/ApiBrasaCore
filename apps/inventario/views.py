from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CategoriaIngrediente, Ingrediente, RecetaProducto, MovimientoInventario
from .serializers import (
    CategoriaIngredienteSerializer,
    IngredienteSerializer,
    RecetaProductoSerializer,
    MovimientoInventarioSerializer,
    AjusteManualSerializer,
    EntradaStockSerializer,
)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class IsAdminOrCajeroReadOnly(permissions.BasePermission):
    """Admin: lectura y escritura. Cajero: solo lectura."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.rol == 'admin':
            return True
        if request.user.rol == 'cajero' and request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return False


class CategoriaIngredienteViewSet(viewsets.ModelViewSet):
    queryset = CategoriaIngrediente.objects.all()
    serializer_class = CategoriaIngredienteSerializer
    permission_classes = [IsAdmin]


class IngredienteViewSet(viewsets.ModelViewSet):
    queryset = Ingrediente.objects.select_related('categoria').all()
    serializer_class = IngredienteSerializer
    permission_classes = [IsAdminOrCajeroReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        activo = self.request.query_params.get('activo')
        estado = self.request.query_params.get('estado')
        categoria = self.request.query_params.get('categoria')

        if activo is not None:
            qs = qs.filter(activo=activo.lower() == 'true')
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        if estado == 'critico':
            # stock_actual <= stock_critico
            from django.db.models import F
            qs = qs.filter(stock_actual__lte=F('stock_critico'))
        elif estado == 'bajo':
            from django.db.models import F
            qs = qs.filter(stock_actual__lte=F('stock_minimo'))
        return qs

    @action(detail=True, methods=['post'], url_path='entrada', permission_classes=[IsAdmin])
    def entrada(self, request, pk=None):
        """Registra una entrada de stock (compra/reposición)."""
        ingrediente = self.get_object()
        serializer = EntradaStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cantidad = serializer.validated_data['cantidad']
        notas = serializer.validated_data.get('notas', '')

        with transaction.atomic():
            ing = Ingrediente.objects.select_for_update().get(pk=ingrediente.pk)
            ing.stock_actual = ing.stock_actual + cantidad
            ing.save(update_fields=['stock_actual'])

            MovimientoInventario.objects.create(
                ingrediente=ing,
                tipo='entrada',
                cantidad=cantidad,
                stock_resultante=ing.stock_actual,
                usuario=request.user,
                notas=notas,
            )

        return Response(IngredienteSerializer(ing).data)

    @action(detail=True, methods=['post'], url_path='ajustar', permission_classes=[IsAdmin])
    def ajustar(self, request, pk=None):
        """Ajuste manual de stock (corrección de inventario físico)."""
        ingrediente = self.get_object()
        serializer = AjusteManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nuevo_stock = serializer.validated_data['nuevo_stock']
        notas = serializer.validated_data.get('notas', '')

        with transaction.atomic():
            ing = Ingrediente.objects.select_for_update().get(pk=ingrediente.pk)
            diferencia = nuevo_stock - ing.stock_actual
            ing.stock_actual = nuevo_stock
            ing.save(update_fields=['stock_actual'])

            MovimientoInventario.objects.create(
                ingrediente=ing,
                tipo='ajuste_manual',
                cantidad=abs(diferencia),
                stock_resultante=ing.stock_actual,
                usuario=request.user,
                notas=notas or f'Ajuste manual: {diferencia:+.3f}',
            )

        return Response(IngredienteSerializer(ing).data)

    @action(detail=True, methods=['get'], url_path='movimientos')
    def movimientos(self, request, pk=None):
        """Lista los movimientos de un ingrediente específico."""
        ingrediente = self.get_object()
        qs = MovimientoInventario.objects.filter(
            ingrediente=ingrediente
        ).select_related('usuario')
        return Response(MovimientoInventarioSerializer(qs, many=True).data)


class RecetaProductoViewSet(viewsets.ModelViewSet):
    queryset = RecetaProducto.objects.select_related('producto', 'ingrediente').all()
    serializer_class = RecetaProductoSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        producto = self.request.query_params.get('producto')
        if producto:
            qs = qs.filter(producto_id=producto)
        return qs


class MovimientoInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MovimientoInventario.objects.select_related(
        'ingrediente', 'usuario', 'referencia_pedido'
    ).all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAdminOrCajeroReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        ingrediente = self.request.query_params.get('ingrediente')
        tipo = self.request.query_params.get('tipo')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        if ingrediente:
            qs = qs.filter(ingrediente_id=ingrediente)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if fecha_inicio:
            qs = qs.filter(creado_en__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(creado_en__date__lte=fecha_fin)
        return qs


class AlertasViewSet(viewsets.ViewSet):
    """
    GET /api/inventario/alertas/
    Retorna ingredientes con stock bajo o crítico.
    """
    permission_classes = [IsAdminOrCajeroReadOnly]

    def list(self, request):
        from django.db.models import F
        criticos = Ingrediente.objects.filter(
            activo=True, stock_actual__lte=F('stock_critico')
        ).select_related('categoria')
        bajos = Ingrediente.objects.filter(
            activo=True,
            stock_actual__gt=F('stock_critico'),
            stock_actual__lte=F('stock_minimo'),
        ).select_related('categoria')

        return Response({
            'criticos': IngredienteSerializer(criticos, many=True).data,
            'bajos': IngredienteSerializer(bajos, many=True).data,
            'total_alertas': criticos.count() + bajos.count(),
        })


class ReporteInventarioView(viewsets.ViewSet):
    """
    GET /api/inventario/reporte/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
    Resumen de movimientos del período.
    """
    permission_classes = [IsAdmin]

    def list(self, request):
        from django.db.models import Sum, Count
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')

        qs = MovimientoInventario.objects.all()
        if fecha_inicio:
            qs = qs.filter(creado_en__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(creado_en__date__lte=fecha_fin)

        entradas = (
            qs.filter(tipo='entrada')
            .values('ingrediente__nombre', 'ingrediente__unidad_medida')
            .annotate(total=Sum('cantidad'), movimientos=Count('id'))
            .order_by('-total')
        )
        salidas = (
            qs.filter(tipo='salida_pedido')
            .values('ingrediente__nombre', 'ingrediente__unidad_medida')
            .annotate(total=Sum('cantidad'), movimientos=Count('id'))
            .order_by('-total')
        )
        ajustes = (
            qs.filter(tipo='ajuste_manual')
            .values('ingrediente__nombre', 'ingrediente__unidad_medida')
            .annotate(total=Sum('cantidad'), movimientos=Count('id'))
        )

        # Stock actual de todos los ingredientes activos
        stock_actual = IngredienteSerializer(
            Ingrediente.objects.filter(activo=True).select_related('categoria'),
            many=True
        ).data

        return Response({
            'periodo': {'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin},
            'entradas': list(entradas),
            'consumo_por_pedidos': list(salidas),
            'ajustes_manuales': list(ajustes),
            'stock_actual': stock_actual,
        })
