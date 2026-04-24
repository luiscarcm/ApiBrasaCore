from django.db import models


class Mesa(models.Model):
    ESTADO_CHOICES = [
        ('libre', 'Libre'),
        ('ocupada', 'Ocupada'),
        ('pagada', 'Pagada'),
    ]
    numero = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField(default=4)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='libre')

    class Meta:
        ordering = ['numero']
        verbose_name = 'Mesa'
        verbose_name_plural = 'Mesas'

    def __str__(self):
        return f"Mesa {self.numero} - {self.estado}"
