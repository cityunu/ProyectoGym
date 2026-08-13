import json
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Sum

from .models import Producto, TipoMembresia, Venta
from .forms import ProductoForm, TipoMembresiaForm, AsignarMembresiaForm
from cliente.models import CodigoQR, Membresia, Acceso

from .models import Producto, TipoMembresia, Venta
from cliente.models import CodigoQR, Membresia, Acceso
from django.db.models import Q, Sum

from core.utils import registrar_evento
from .forms import ProductoForm, TipoMembresiaForm, AsignarMembresiaForm, ClienteForm

Usuario = get_user_model()


def solo_staff(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in ['administrador', 'recepcionista', 'entrenador']:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def solo_admin_recepcion(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.rol not in ['administrador', 'recepcionista']:
            messages.error(request, 'No tienes permisos para esta acción.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@solo_staff
def inicio(request):
    total_productos = Producto.objects.filter(activo=True).count()
    total_membresias = Membresia.objects.filter(activa=True).count()
    productos_sin_stock = Producto.objects.filter(activo=True, stock=0).count()
    clientes_sin_membresia = Usuario.objects.filter(rol='cliente').exclude(
        membresia__isnull=False
    ).count()
    return render(request, 'administrador/inicio.html', {
        'total_productos': total_productos,
        'total_membresias': total_membresias,
        'productos_sin_stock': productos_sin_stock,
        'clientes_sin_membresia': clientes_sin_membresia,
    })


@solo_admin_recepcion
def lista_productos(request):
    productos = Producto.objects.all().order_by('-fecha_creacion')
    return render(request, 'administrador/productos/lista.html', {'productos': productos})


@solo_admin_recepcion
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado correctamente.')
            return redirect('administrador:lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'administrador/productos/form.html', {'form': form, 'titulo': 'Agregar Producto'})


@solo_admin_recepcion
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('administrador:lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'administrador/productos/form.html', {'form': form, 'titulo': 'Editar Producto'})


@solo_admin_recepcion
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        registrar_evento(
            request.user,
            'Eliminar producto',
            f'Se eliminó el producto "{nombre}".'
        )
        messages.success(request, 'Producto eliminado.')
        return redirect('administrador:lista_productos')
    return render(request, 'administrador/productos/confirmar_eliminar.html', {'producto': producto})


@solo_admin_recepcion
def gestionar_membresias(request):
    tipos = TipoMembresia.objects.all()
    if request.method == 'POST':
        tipo_id = request.POST.get('tipo_id')
        tipo = get_object_or_404(TipoMembresia, pk=tipo_id)
        form = TipoMembresiaForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Precio de "{tipo.get_nombre_display()}" actualizado.')
            return redirect('administrador:gestionar_membresias')
    else:
        form = TipoMembresiaForm()

    return render(request, 'administrador/membresias/gestionar.html', {
        'tipos': tipos,
        'form': form,
    })


@solo_admin_recepcion
def asignar_membresia(request):
    """Asigna la primera membresía a un cliente que aún no tiene una"""
    clientes_sin_membresia = Usuario.objects.filter(rol='cliente').exclude(
        membresia__isnull=False
    )

    if request.method == 'POST':
        form = AsignarMembresiaForm(request.POST)
        form.fields['usuario'].queryset = clientes_sin_membresia
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            tipo = form.cleaned_data['tipo']
            hoy = timezone.now().date()
            Membresia.objects.create(
                usuario=usuario,
                tipo=tipo,
                fecha_inicio=hoy,
                fecha_fin=hoy + timedelta(days=tipo.duracion_dias),
                activa=True,
            )
            registrar_evento(
                request.user,
                'Asignar membresía',
                f'Se asignó "{tipo.get_nombre_display()}" a {usuario.get_full_name() or usuario.username}.'
            )
            messages.success(
                request,
                f'Membresía "{tipo.get_nombre_display()}" asignada a '
                f'{usuario.get_full_name() or usuario.username}.'
            )
            return redirect('administrador:gestionar_membresias')


@solo_staff
def lector_qr(request):
    return render(request, 'administrador/qr/lector.html')


@csrf_exempt
@solo_staff
def verificar_qr(request):
    """Recibe el código QR escaneado, verifica membresía y registra el acceso"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo = data.get('codigo', '').strip()

            qr = CodigoQR.objects.select_related('usuario').filter(
                codigo=codigo,
                fecha_generado__date=timezone.now().date()
            ).first()

            if not qr:
                # Registrar intento fallido sin usuario (no se puede asociar)
                return JsonResponse({
                    'valido': False,
                    'mensaje': 'QR inválido o expirado. El cliente no tiene acceso.'
                })

            usuario = qr.usuario

            membresia = Membresia.objects.filter(
                usuario=usuario,
                activa=True,
                fecha_fin__gte=timezone.now().date()
            ).first()

            if membresia:
                Acceso.objects.create(
                    usuario=usuario,
                    valido=True,
                    motivo='Acceso permitido — membresía vigente.'
                )
                return JsonResponse({
                    'valido': True,
                    'mensaje': f'✅ Acceso permitido — {usuario.get_full_name() or usuario.username}',
                    'cliente': usuario.get_full_name() or usuario.username,
                    'membresia': membresia.tipo.get_nombre_display(),
                    'vence': membresia.fecha_fin.strftime('%d/%m/%Y'),
                })
            else:
                Acceso.objects.create(
                    usuario=usuario,
                    valido=False,
                    motivo='Membresía inactiva o vencida.'
                )
                return JsonResponse({
                    'valido': False,
                    'mensaje': f'❌ Membresía inactiva o vencida — {usuario.get_full_name() or usuario.username}',
                })

        except Exception as e:
            return JsonResponse({'valido': False, 'mensaje': f'Error: {str(e)}'})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@solo_staff
def historial_accesos(request):
    accesos = Acceso.objects.select_related('usuario')[:200]
    return render(request, 'administrador/qr/historial.html', {'accesos': accesos})

@solo_staff
def historial_ventas(request):
    ventas = Venta.objects.select_related('cliente').prefetch_related('detalles__producto')[:200]
    return render(request, 'administrador/ventas/historial.html', {'ventas': ventas})

@solo_admin_recepcion
def lista_clientes(request):
    """Listado y búsqueda de clientes"""
    q = request.GET.get('q', '').strip()

    clientes = Usuario.objects.filter(rol='cliente').order_by('first_name', 'last_name', 'username')

    if q:
        clientes = clientes.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(telefono__icontains=q)
        )

    return render(request, 'administrador/clientes/lista.html', {
        'clientes': clientes,
        'q': q,
    })

@solo_admin_recepcion
def detalle_cliente(request, usuario_id):
    """Detalle de cliente con membresía y QR"""
    usuario = get_user_model().objects.get(pk=usuario_id, rol='cliente')
    try:
        membresia = usuario.membresia
    except Membresia.DoesNotExist:
        membresia = None
    try:
        qr = usuario.codigo_qr
    except CodigoQR.DoesNotExist:
        qr = None

    return render(request, 'administrador/clientes/detalle.html', {
        'cliente': usuario,
        'membresia': membresia,
        'qr': qr,
    })


@solo_admin_recepcion
def editar_cliente(request, usuario_id):
    """Editar datos básicos de cliente"""
    usuario = get_object_or_404(Usuario, pk=usuario_id, rol='cliente')

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            registrar_evento(
                request.user,
                'Editar cliente',
                f'Se actualizaron datos de {usuario.get_full_name() or usuario.username}.'
            )
            messages.success(request, 'Datos del cliente actualizados correctamente.')
            return redirect('administrador:detalle_cliente', usuario_id=usuario.pk)
    else:
        form = ClienteForm(instance=usuario)

    return render(request, 'administrador/clientes/form.html', {
        'cliente': usuario,
        'form': form,
    })

@solo_staff
def reporte_ingresos(request):
    hoy = timezone.now().date()
    desde = request.GET.get('desde') or str(hoy.replace(day=1))
    hasta = request.GET.get('hasta') or str(hoy)

    ventas = Venta.objects.filter(
        fecha__date__range=[desde, hasta]
    ).select_related('cliente').prefetch_related('detalles__producto').order_by('-fecha')

    total_periodo = ventas.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'administrador/ventas/reporte_ingresos.html', {
        'ventas': ventas,
        'total_periodo': total_periodo,
        'desde': desde,
        'hasta': hasta,
    })

@solo_staff
def reporte_asistencias(request):
    """Reporte de asistencias basadas en accesos válidos"""
    hoy = timezone.now().date()
    desde = request.GET.get('desde') or str(hoy.replace(day=1))  # inicio de mes
    hasta = request.GET.get('hasta') or str(hoy)

    accesos = Acceso.objects.filter(
        fecha_hora__date__range=[desde, hasta],
        valido=True
    ).select_related('usuario').order_by('-fecha_hora')

    total_asistencias = accesos.count()

    # Agrupar por usuario para mostrar cuántas asistencias tiene cada uno
    from django.db.models import Count
    asistencias_por_cliente = (
        Acceso.objects.filter(
            fecha_hora__date__range=[desde, hasta],
            valido=True
        )
        .values('usuario__id', 'usuario__first_name', 'usuario__last_name', 'usuario__username')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    return render(request, 'administrador/qr/reporte_asistencias.html', {
        'accesos': accesos,
        'total_asistencias': total_asistencias,
        'asistencias_por_cliente': asistencias_por_cliente,
        'desde': desde,
        'hasta': hasta,
    })

@solo_staff
def bitacora(request):
    eventos = Bitacora.objects.select_related('usuario')[:200]
    return render(request, 'administrador/bitacora/lista.html', {'eventos': eventos})