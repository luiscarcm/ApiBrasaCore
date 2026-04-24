from django.db import models
from apps.users.models import Usuario
from apps.mesas.models import Mesa
from apps.productos.models import Producto


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo'),
        ('entregado', 'Entregado'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name='pedidos')
    mesero = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='pedidos')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    en_preparacion_en = models.DateTimeField(null=True, blank=True)
    listo_en = models.DateTimeField(null=True, blank=True)
    entregado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido #{self.id} - Mesa {self.mesa.numero} ({self.estado})"

    def calcular_subtotal(self):
        return sum(d.precio_unitario * d.cantidad for d in self.detalles.all())


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True)
    entregado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
