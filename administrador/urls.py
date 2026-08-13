from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/<int:usuario_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:usuario_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('membresias/', views.gestionar_membresias, name='gestionar_membresias'),
    path('membresias/asignar/', views.asignar_membresia, name='asignar_membresia'),
    path('lector-qr/', views.lector_qr, name='lector_qr'),
    path('verificar-qr/', views.verificar_qr, name='verificar_qr'),
    path('accesos/', views.historial_accesos, name='historial_accesos'),
    path('accesos/reporte/', views.reporte_asistencias, name='reporte_asistencias'),
    path('ventas/', views.historial_ventas, name='historial_ventas'),
    path('ventas/ingresos/', views.reporte_ingresos, name='reporte_ingresos'),
     path('bitacora/', views.bitacora, name='bitacora'),
]