from django.contrib import admin
from .models import TipoMembresia, Producto


@admin.register(TipoMembresia)
class TipoMembresiaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo')
    list_editable = ('precio', 'activo')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'activo')
    list_editable = ('precio', 'stock', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)