import json
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Producto, TipoMembresia
from .forms import ProductoForm, TipoMembresiaForm, AsignarMembresiaForm
from cliente.models import CodigoQR, Membresia

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
        producto.delete()
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
            messages.success(
                request,
                f'Membresía "{tipo.get_nombre_display()}" asignada a '
                f'{usuario.get_full_name() or usuario.username}.'
            )
            return redirect('administrador:gestionar_membresias')
    else:
        form = AsignarMembresiaForm()
        form.fields['usuario'].queryset = clientes_sin_membresia

    return render(request, 'administrador/membresias/asignar.html', {
        'form': form,
        'clientes_sin_membresia': clientes_sin_membresia,
    })


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
    """Historial de accesos recientes"""
    accesos = Acceso.objects.select_related('usuario')[:200]
    return render(request, 'administrador/qr/historial.html', {'accesos': accesos})

@solo_staff
def historial_ventas(request):
    """Historial de ventas de productos"""
    ventas = Venta.objects.select_related('cliente').prefetch_related('detalles__producto')[:200]
    return render(request, 'administrador/ventas/historial.html', {'ventas': ventas})