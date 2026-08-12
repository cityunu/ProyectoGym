import qrcode
import io
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Membresia, CodigoQR, CarritoItem
from administrador.models import Producto, TipoMembresia



def solo_cliente(view_func):
    """Decorador: solo clientes pueden acceder"""
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol != 'cliente':
            messages.error(request, 'Esta sección es solo para clientes.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def generar_imagen_qr(codigo_uuid):
    """Genera la imagen PNG del QR y la retorna como ContentFile"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(codigo_uuid))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue())


@solo_cliente
def inicio(request):
    """Dashboard del cliente"""
    try:
        membresia = request.user.membresia
    except Membresia.DoesNotExist:
        membresia = None

    items_carrito = CarritoItem.objects.filter(usuario=request.user).count()

    return render(request, 'cliente/inicio.html', {
        'membresia': membresia,
        'items_carrito': items_carrito,
    })


@solo_cliente
def mi_qr(request):
    """Muestra el QR diario del cliente — regenera si es de otro día"""
    try:
        qr_obj = request.user.codigo_qr
        # Si el QR es de un día anterior, regenerar
        if qr_obj.fecha_generado.date() < timezone.now().date():
            import uuid
            qr_obj.codigo = uuid.uuid4()
            imagen = generar_imagen_qr(qr_obj.codigo)
            qr_obj.imagen_qr.save(f'qr_{request.user.pk}.png', imagen, save=False)
            qr_obj.save()
    except CodigoQR.DoesNotExist:
        # Crear QR por primera vez
        import uuid
        nuevo_codigo = uuid.uuid4()
        qr_obj = CodigoQR(usuario=request.user, codigo=nuevo_codigo)
        imagen = generar_imagen_qr(nuevo_codigo)
        qr_obj.imagen_qr.save(f'qr_{request.user.pk}.png', imagen, save=False)
        qr_obj.save()

    return render(request, 'cliente/mi_qr.html', {'qr': qr_obj})


@solo_cliente
def mi_membresia(request):
    """Muestra la membresía actual del cliente"""
    try:
        membresia = request.user.membresia
    except Membresia.DoesNotExist:
        membresia = None

    tipos = TipoMembresia.objects.filter(activo=True)
    return render(request, 'cliente/membresia.html', {
        'membresia': membresia,
        'tipos': tipos,
    })


@solo_cliente
def cambiar_membresia(request):
    """Permite al cliente cambiar/renovar su tipo de membresía"""
    if request.method == 'POST':
        tipo_id = request.POST.get('tipo_id')
        tipo = get_object_or_404(TipoMembresia, pk=tipo_id, activo=True)
        hoy = timezone.now().date()

        try:
            membresia = request.user.membresia
            membresia.tipo = tipo
            membresia.fecha_inicio = hoy
            membresia.fecha_fin = hoy + timedelta(days=tipo.duracion_dias)
            membresia.activa = True
            membresia.save()
            messages.success(
                request,
                f'Membresía cambiada a: {tipo.get_nombre_display()} — vence el {membresia.fecha_fin.strftime("%d/%m/%Y")}.'
            )
        except Membresia.DoesNotExist:
            messages.error(
                request,
                'No tienes una membresía activa. Pide en recepción que te asignen una la primera vez.'
            )

        return redirect('cliente:mi_membresia')

    return redirect('cliente:mi_membresia')


@solo_cliente
def tienda(request):
    """Lista de productos disponibles"""
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    return render(request, 'cliente/tienda.html', {'productos': productos})


@solo_cliente
def ver_carrito(request):
    """Muestra el carrito del cliente"""
    items = CarritoItem.objects.filter(
        usuario=request.user
    ).select_related('producto')

    total = sum(item.subtotal() for item in items)
    return render(request, 'cliente/carrito.html', {'items': items, 'total': total})


@solo_cliente
def agregar_al_carrito(request, producto_pk):
    producto = get_object_or_404(Producto, pk=producto_pk, activo=True)

    if producto.stock == 0:
        messages.error(request, 'Producto sin stock disponible.')
        return redirect('cliente:tienda')

    item, creado = CarritoItem.objects.get_or_create(
        usuario=request.user,
        producto=producto,
        defaults={'cantidad': 1}
    )

    if not creado:
        if item.cantidad < producto.stock:
            item.cantidad += 1
            item.save()
            messages.success(request, f'Se agregó una unidad más de {producto.nombre}.')
        else:
            messages.warning(request, f'No hay más stock de {producto.nombre}.')
    else:
        messages.success(request, f'{producto.nombre} agregado al carrito.')

    return redirect('cliente:tienda')


@solo_cliente
def eliminar_del_carrito(request, item_pk):
    item = get_object_or_404(CarritoItem, pk=item_pk, usuario=request.user)
    item.delete()
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('cliente:ver_carrito')


@solo_cliente
def confirmar_compra(request):
    """Procesa la compra: descuenta stock, guarda la venta y limpia el carrito"""
    items = CarritoItem.objects.filter(
        usuario=request.user
    ).select_related('producto')

    if not items.exists():
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('cliente:ver_carrito')

    # Verificar stock antes de procesar
    errores = []
    for item in items:
        if item.cantidad > item.producto.stock:
            errores.append(f'{item.producto.nombre}: solo hay {item.producto.stock} en stock.')

    if errores:
        for error in errores:
            messages.error(request, error)
        return redirect('cliente:ver_carrito')

    # Calcular total y crear venta
    total = sum(item.subtotal() for item in items)
    venta = Venta.objects.create(
        cliente=request.user,
        total=total,
    )

    # Procesar la compra: descontar stock y crear detalles
    items_comprados = []
    for item in items:
        producto = item.producto
        producto.stock -= item.cantidad
        producto.save()

        detalle = DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=item.cantidad,
            precio_unitario=producto.precio,
            subtotal=item.subtotal(),
        )
        # Guardar para mostrar en pantalla
        items_comprados.append(detalle)

    # Vaciar carrito
    items.delete()

    messages.success(
        request,
        f'¡Compra realizada! Total: ${total}. Recoge tus productos en recepción.'
    )
    return render(request, 'cliente/compra_exitosa.html', {
        'items': items_comprados,
        'total': total,
    })