from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('membresias/', views.gestionar_membresias, name='gestionar_membresias'),
    path('lector-qr/', views.lector_qr, name='lector_qr'),
    path('verificar-qr/', views.verificar_qr, name='verificar_qr'),
]