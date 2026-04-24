from django.db import models
from apps.users.models import Usuario


class ConfigCaja(models.Model):
    base_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actualizado_por = models.ForeignKey(
        Usuario, null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de caja'


class CierreCaja(models.Model):
    ESTADO_CHOICES = [('abierta', 'Abierta'), ('cerrada', 'Cerrada')]
    cajero = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='cierres_caja')
    apertura_en = models.DateTimeField(auto_now_add=True)
    cierre_en = models.DateTimeField(null=True, blank=True)
    base_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_tarjeta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_transferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    efectivo_contado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notas = models.TextField(blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='abierta')

    class Meta:
        ordering = ['-apertura_en']
        verbose_name = 'Cierre de caja'
        verbose_name_plural = 'Cierres de caja'
