import uuid
from django.db import models
from django.conf import settings
from administrador.models import TipoMembresia


class Membresia(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='membresia'
    )
    tipo = models.ForeignKey(
        TipoMembresia,
        on_delete=models.PROTECT,
        related_name='membresias'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} — {self.tipo.get_nombre_display()}"

    class Meta:
        verbose_name = 'Membresía'
        verbose_name_plural = 'Membresías'


class CodigoQR(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='codigo_qr'
    )
    codigo = models.UUIDField(default=uuid.uuid4, unique=True)
    fecha_generado = models.DateTimeField(auto_now_add=True)
    imagen_qr = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def __str__(self):
        return f"QR de {self.usuario.username} — {self.fecha_generado.date()}"

    class Meta:
        verbose_name = 'Código QR'
        verbose_name_plural = 'Códigos QR'


class CarritoItem(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    producto = models.ForeignKey(
        'administrador.Producto',
        on_delete=models.CASCADE,
        related_name='en_carritos'
    )
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.producto.precio * self.cantidad

    def __str__(self):
        return f"{self.usuario.username} — {self.producto.nombre} x{self.cantidad}"

    class Meta:
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ('usuario', 'producto')