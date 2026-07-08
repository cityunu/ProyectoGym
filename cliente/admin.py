from django.contrib import admin
from .models import Membresia, CodigoQR, CarritoItem


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'fecha_inicio', 'fecha_fin', 'activa')
    list_filter = ('activa', 'tipo')
    search_fields = ('usuario__username', 'usuario__first_name')


@admin.register(CodigoQR)
class CodigoQRAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'codigo', 'fecha_generado')
    search_fields = ('usuario__username',)


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'producto', 'cantidad', 'fecha_agregado')