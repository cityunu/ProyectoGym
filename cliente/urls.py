from django.urls import path
from . import views

app_name = 'cliente'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('mi-qr/', views.mi_qr, name='mi_qr'),
    path('membresia/', views.mi_membresia, name='mi_membresia'),
    path('membresia/cambiar/', views.cambiar_membresia, name='cambiar_membresia'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_pk>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_pk>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/comprar/', views.confirmar_compra, name='confirmar_compra'),
    path('tienda/', views.tienda, name='tienda'),
]