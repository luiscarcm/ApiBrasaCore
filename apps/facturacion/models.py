from django.db import models
from apps.users.models import Usuario
from apps.pedidos.models import Pedido


class Factura(models.Model):
    METODO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]
    pedido = models.OneToOneField(Pedido, on_delete=models.PROTECT, related_name='factura')
    cajero = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='facturas')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)   # percentage
    propina = models.DecimalField(max_digits=5, decimal_places=2, default=0)     # percentage
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=19)        # percentage (19% Colombia)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=15, choices=METODO_CHOICES)
    extras = models.JSONField(default=list)          # [{descripcion, valor, cantidad, tipo}]
    extras_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f"Factura #{self.id} - Pedido #{self.pedido_id} - ${self.total}"


class AlertaCajero(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name='alertas')
    cajero = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='alertas')
    descripcion = models.TextField()
    items_removidos = models.JSONField(default=list)  # [{nombre, cantidad, precio_unitario}]
    leido = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Alerta de Cajero'
        verbose_name_plural = 'Alertas de Cajero'

    def __str__(self):
        return f"Alerta #{self.id} - Pedido #{self.pedido_id} - {'Leída' if self.leido else 'Sin leer'}"
