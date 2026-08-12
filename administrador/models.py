from django.db import models
from django.conf import settings


class TipoMembresia(models.Model):
    OPCIONES = [
        ('basica', 'Solo Mensualidad'),
        ('entrenador', 'Mensualidad + Entrenador'),
        ('completa', 'Mensualidad + Entrenador + Nutriólogo'),
    ]

    nombre = models.CharField(max_length=10, choices=OPCIONES, unique=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    duracion_dias = models.PositiveIntegerField(default=30, help_text='Duración en días')
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_nombre_display()} — ${self.precio}"

    class Meta:
        verbose_name = 'Tipo de Membresía'
        verbose_name_plural = 'Tipos de Membresía'


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def disponible(self):
        return self.activo and self.stock > 0

    def __str__(self):
        return f"{self.nombre} — Stock: {self.stock}"

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class Venta(models.Model):
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.pk} — ${self.total} — {self.fecha.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_venta'
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} — ${self.subtotal}"

    class Meta:
        verbose_name = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'