from django.db import models


class TipoMembresia(models.Model):
    OPCIONES = [
        ('basica', 'Solo Mensualidad'),
        ('entrenador', 'Mensualidad + Entrenador'),
        ('completa', 'Mensualidad + Entrenador + Nutriólogo'),
    ]

    nombre = models.CharField(max_length=10, choices=OPCIONES, unique=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
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