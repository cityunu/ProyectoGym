from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
        ('recepcionista', 'Recepcionista'),
        ('entrenador', 'Entrenador'),
    ]

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='cliente'
    )
    telefono = models.CharField(max_length=15, blank=True, null=True)
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True
    )

    def es_cliente(self):
        return self.rol == 'cliente'

    def es_staff_gym(self):
        return self.rol in ['administrador', 'recepcionista', 'entrenador']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"


class Bitacora(models.Model):
    usuario = models.ForeignKey(
        'core.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos'
    )
    accion = models.CharField(max_length=150)
    detalle = models.TextField(blank=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.fecha_hora.strftime('%d/%m/%Y %H:%M')}] {self.accion}"

    class Meta:
        verbose_name = 'Evento de bitácora'
        verbose_name_plural = 'Bitácora'
        ordering = ['-fecha_hora']