from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver


def _descontar_stock_detalle(detalle):
    """Descuenta del inventario los ingredientes usados en un DetallePedido."""
    from .models import RecetaProducto, MovimientoInventario, Ingrediente

    receta = RecetaProducto.objects.filter(
        producto_id=detalle.producto_id
    ).select_related('ingrediente')
    if not receta.exists():
        return

    with transaction.atomic():
        for item in receta:
            ingrediente = (
                Ingrediente.objects
                .select_for_update()
                .get(pk=item.ingrediente_id)
            )
            cantidad_usada = item.cantidad * detalle.cantidad
            ingrediente.stock_actual = max(
                ingrediente.stock_actual - cantidad_usada, 0
            )
            ingrediente.save(update_fields=['stock_actual'])

            MovimientoInventario.objects.create(
                ingrediente=ingrediente,
                tipo='salida_pedido',
                cantidad=cantidad_usada,
                stock_resultante=ingrediente.stock_actual,
                referencia_pedido_id=detalle.pedido_id,
                referencia_detalle_id=detalle.pk,
                notas=f'Pedido #{detalle.pedido_id} — ítem {detalle.pk}',
            )


def _restaurar_stock_detalle(detalle, tipo='devolucion_pedido', notas=''):
    """Restaura al inventario los ingredientes de un DetallePedido."""
    from .models import RecetaProducto, MovimientoInventario, Ingrediente

    receta = RecetaProducto.objects.filter(
        producto_id=detalle.producto_id
    ).select_related('ingrediente')
    if not receta.exists():
        return

    pedido_id = getattr(detalle, 'pedido_id', None)

    with transaction.atomic():
        for item in receta:
            ingrediente = (
                Ingrediente.objects
                .select_for_update()
                .get(pk=item.ingrediente_id)
            )
            cantidad_restaurada = item.cantidad * detalle.cantidad
            ingrediente.stock_actual = ingrediente.stock_actual + cantidad_restaurada
            ingrediente.save(update_fields=['stock_actual'])

            MovimientoInventario.objects.create(
                ingrediente=ingrediente,
                tipo=tipo,
                cantidad=cantidad_restaurada,
                stock_resultante=ingrediente.stock_actual,
                referencia_pedido_id=pedido_id,
                notas=notas or f'Restauración — pedido #{pedido_id}',
            )


# ── DetallePedido signals ─────────────────────────────────────────────────────

def _get_detalle_pedido_model():
    from apps.pedidos.models import DetallePedido
    return DetallePedido


def _get_pedido_model():
    from apps.pedidos.models import Pedido
    return Pedido


def connect_signals():
    """Called from AppConfig.ready() to bind signals after all models load."""
    DetallePedido = _get_detalle_pedido_model()
    Pedido = _get_pedido_model()

    @receiver(post_save, sender=DetallePedido, weak=False)
    def detalle_creado(sender, instance, created, **kwargs):
        if created:
            _descontar_stock_detalle(instance)

    @receiver(pre_delete, sender=DetallePedido, weak=False)
    def detalle_pre_delete(sender, instance, **kwargs):
        # Cache pedido estado before potential cascade removes the row
        try:
            instance._pedido_estado_cache = instance.pedido.estado
        except Exception:
            instance._pedido_estado_cache = None

    @receiver(post_delete, sender=DetallePedido, weak=False)
    def detalle_eliminado(sender, instance, **kwargs):
        # Skip if the pedido was already cancelled (stock restored by pedido signal)
        if getattr(instance, '_pedido_estado_cache', None) == 'cancelado':
            return
        _restaurar_stock_detalle(
            instance,
            tipo='devolucion_pedido',
            notas=f'Ítem removido — pedido #{getattr(instance, "pedido_id", "?")}',
        )

    @receiver(pre_save, sender=Pedido, weak=False)
    def pedido_pre_save(sender, instance, **kwargs):
        if instance.pk:
            try:
                instance._estado_anterior = (
                    Pedido.objects
                    .values_list('estado', flat=True)
                    .get(pk=instance.pk)
                )
            except Pedido.DoesNotExist:
                instance._estado_anterior = None
        else:
            instance._estado_anterior = None

    @receiver(post_save, sender=Pedido, weak=False)
    def pedido_cancelado(sender, instance, created, **kwargs):
        if created:
            return
        estado_anterior = getattr(instance, '_estado_anterior', None)
        if estado_anterior != 'cancelado' and instance.estado == 'cancelado':
            for detalle in instance.detalles.all():
                _restaurar_stock_detalle(
                    detalle,
                    tipo='devolucion_pedido',
                    notas=f'Pedido #{instance.pk} cancelado',
                )
