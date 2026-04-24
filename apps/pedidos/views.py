from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Pedido, DetallePedido
from .serializers import PedidoSerializer, PedidoCreateSerializer, DetallePedidoSerializer
from apps.productos.models import Producto


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.select_related('mesa', 'mesero').prefetch_related('detalles__producto').all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCreateSerializer
        return PedidoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        estado = self.request.query_params.get('estado')
        mesa = self.request.query_params.get('mesa')

        # Meseros only see their own orders; kitchen/cajero/admin see all
        if user.rol == 'mesero':
            qs = qs.filter(mesero=user)

        if estado:
            qs = qs.filter(estado=estado)
        if mesa:
            qs = qs.filter(mesa_id=mesa)

        return qs

    @action(detail=True, methods=['patch'], url_path='estado')
    def cambiar_estado(self, request, pk=None):
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado')
        estados_validos = [e[0] for e in Pedido.ESTADO_CHOICES]

        if nuevo_estado not in estados_validos:
            return Response({'error': 'Estado inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Role-based state transitions
        user = request.user
        if nuevo_estado in ['en_preparacion', 'listo'] and user.rol not in ['cocina', 'admin']:
            return Response(
                {'error': 'Solo cocina puede cambiar a este estado.'},
                status=status.HTTP_403_FORBIDDEN
            )
        if nuevo_estado == 'pagado' and user.rol not in ['cajero', 'admin']:
            return Response(
                {'error': 'Solo cajero puede marcar como pagado.'},
                status=status.HTTP_403_FORBIDDEN
            )

        pedido.estado = nuevo_estado
        if nuevo_estado == 'en_preparacion' and not pedido.en_preparacion_en:
            pedido.en_preparacion_en = timezone.now()
        elif nuevo_estado == 'listo' and not pedido.listo_en:
            pedido.listo_en = timezone.now()
        elif nuevo_estado == 'entregado' and not pedido.entregado_en:
            pedido.entregado_en = timezone.now()
        pedido.save()
        return Response(PedidoSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='remover_item')
    def remover_item(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado not in ['pendiente', 'en_preparacion']:
            return Response(
                {'error': 'Solo se pueden eliminar ítems de pedidos pendientes o en preparación.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        detalle_id = request.data.get('detalle_id')
        if not detalle_id:
            return Response({'error': 'detalle_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            detalle = pedido.detalles.get(id=detalle_id)
        except DetallePedido.DoesNotExist:
            return Response({'error': 'Ítem no encontrado en este pedido.'}, status=status.HTTP_404_NOT_FOUND)

        if pedido.detalles.count() <= 1:
            return Response(
                {'error': 'No se puede eliminar el único ítem del pedido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        detalle.delete()
        return Response(PedidoSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='devolver_item')
    def devolver_item(self, request, pk=None):
        pedido = self.get_object()
        detalle_id = request.data.get('detalle_id')
        if not detalle_id:
            return Response({'error': 'detalle_id es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            detalle = pedido.detalles.get(id=detalle_id)
        except DetallePedido.DoesNotExist:
            return Response({'error': 'Ítem no encontrado en este pedido.'}, status=status.HTTP_404_NOT_FOUND)

        if not detalle.entregado:
            return Response({'error': 'Este ítem no ha sido entregado todavía.'}, status=status.HTTP_400_BAD_REQUEST)

        detalle.entregado = False
        detalle.save()

        # Si el pedido estaba completamente entregado, volver a listo
        if pedido.estado == 'entregado':
            pedido.estado = 'listo'
            pedido.entregado_en = None
            pedido.save()

        return Response(PedidoSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='agregar_items')
    def agregar_items(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden agregar ítems a pedidos pendientes.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        detalles_data = request.data.get('detalles', [])
        if not detalles_data:
            return Response({'error': 'detalles es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        for d in detalles_data:
            try:
                producto = Producto.objects.get(id=d['producto'])
            except Producto.DoesNotExist:
                return Response(
                    {'error': f'Producto {d["producto"]} no encontrado.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=max(int(d.get('cantidad', 1)), 1),
                precio_unitario=producto.precio,
                observaciones=d.get('observaciones', ''),
            )

        return Response(PedidoSerializer(pedido, context={'request': request}).data)

    @action(detail=True, methods=['post'], url_path='entregar_items')
    def entregar_items(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado not in ['pendiente', 'listo', 'en_preparacion', 'entregado']:
            return Response(
                {'error': 'Solo se pueden entregar ítems de pedidos activos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        detalle_ids = request.data.get('detalle_ids', [])
        if not detalle_ids:
            return Response({'error': 'detalle_ids es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ítems de cocina solo se pueden entregar cuando el pedido está listo
        if pedido.estado not in ['listo', 'entregado']:
            cocina_ids = list(
                pedido.detalles.filter(id__in=detalle_ids, producto__requiere_cocina=True).values_list('id', flat=True)
            )
            if cocina_ids:
                return Response(
                    {'error': 'Los ítems de cocina solo se pueden entregar cuando el pedido está listo.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Mark requested items as delivered
        pedido.detalles.filter(id__in=detalle_ids).update(entregado=True)

        # If all items are now delivered, move pedido to entregado
        if not pedido.detalles.filter(entregado=False).exists():
            pedido.estado = 'entregado'
            if not pedido.entregado_en:
                pedido.entregado_en = timezone.now()
            pedido.save()

        return Response(PedidoSerializer(pedido, context={'request': request}).data)
