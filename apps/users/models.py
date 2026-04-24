import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('mesero', 'Mesero'),
        ('cajero', 'Cajero'),
        ('admin', 'Administrador'),
        ('cocina', 'Cocina'),
    ]
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='mesero')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.created_at + timedelta(hours=1)

    class Meta:
        verbose_name = 'Token de Recuperación'
        verbose_name_plural = 'Tokens de Recuperación'
