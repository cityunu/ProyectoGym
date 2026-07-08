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