from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm


def landing(request):
    """Página informativa pública del gym"""

    servicios = [
        {'nombre': 'Entrenamiento personalizado', 'descripcion': 'Rutinas adaptadas a tu nivel y objetivos.', 'icono': 'dumbbell'},
        {'nombre': 'Clases grupales', 'descripcion': 'Sesiones dinámicas de alta energía en grupo.', 'icono': 'users'},
        {'nombre': 'Nutrición y seguimiento', 'descripcion': 'Asesoría para acompañar tu progreso físico.', 'icono': 'apple'},
    ]

    planes = [
        {
            'nombre': 'Básico',
            'precio': 399,
            'descripcion': 'Acceso completo al gimnasio para entrenar por tu cuenta.',
            'destacado': False,
            'beneficios': [
                'Acceso ilimitado a área de pesas y cardio',
                'Uso de vestidores y regaderas',
                'Horario completo lunes a domingo',
                'Sin permanencia forzosa',
            ],
        },
        {
            'nombre': 'Pro',
            'precio': 649,
            'descripcion': 'Todo lo básico más acompañamiento profesional.',
            'destacado': True,
            'beneficios': [
                'Todo lo del plan Básico',
                '2 sesiones al mes con coach personal',
                'Acceso a clases grupales',
                'Plan de entrenamiento mensual',
                'Evaluación física inicial',
            ],
        },
        {
            'nombre': 'Elite',
            'precio': 999,
            'descripcion': 'Experiencia completa con seguimiento cercano.',
            'destacado': False,
            'beneficios': [
                'Todo lo del plan Pro',
                'Coach personal asignado',
                'Plan de nutrición incluido',
                'Seguimiento semanal de progreso',
                'Acceso prioritario a eventos',
            ],
        },
    ]

    categorias_maquinas = [
        {'slug': 'todas', 'nombre': 'Todas'},
        {'slug': 'fuerza', 'nombre': 'Fuerza'},
        {'slug': 'cardio', 'nombre': 'Cardio'},
        {'slug': 'funcional', 'nombre': 'Funcional'},
    ]

    maquinas = [
        {
            'nombre': 'Rack de pesas libres',
            'descripcion': 'Barras, discos y racks para movimientos compuestos.',
            'categoria': 'fuerza',
            'categoria_label': 'Fuerza',
            'icono': 'dumbbell',
            'imagen': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/303d30b8d0e66d5d9c1830053312022126b5d390.jpg',
        },
        {
            'nombre': 'Máquina de poleas',
            'descripcion': 'Cable crossover para trabajo de pecho, espalda y brazos.',
            'categoria': 'fuerza',
            'categoria_label': 'Fuerza',
            'icono': 'move-vertical',
            'imagen': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/a9c7380eed917a33d235059fcdfd5fda1fefbd28.jpg',
        },
        {
            'nombre': 'Máquina de jalón',
            'descripcion': 'Estación de jalón y remo para desarrollo de espalda.',
            'categoria': 'fuerza',
            'categoria_label': 'Fuerza',
            'icono': 'anchor',
            'imagen': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/9b3163f8bc8af0e73b9df5551c4483d07d07e350.jpg',
        },
        {
            'nombre': 'Remo (rowing machine)',
            'descripcion': 'Cardio de bajo impacto trabajando todo el cuerpo.',
            'categoria': 'cardio',
            'categoria_label': 'Cardio',
            'icono': 'activity',
            'imagen': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/9665057482474f6ee6800f4e28b7b83f28b38a45.jpg',
        },
        {
            'nombre': 'SkiErg',
            'descripcion': 'Máquina de resistencia por cable para tren superior.',
            'categoria': 'cardio',
            'categoria_label': 'Cardio',
            'icono': 'zap',
            'imagen': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/71ffe901ebb476ea8aadd2ef4c5624bcd22e95fa.jpg',
        },
        {
            'nombre': 'Área de entrenamiento funcional',
            'descripcion': 'Zona de turf para trabajo dinámico y movilidad.',
            'categoria': 'funcional',
            'categoria_label': 'Funcional',
            'icono': 'flame',
            'imagen': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/66e654f83ea7910fee91e0231a00fc10a60b29a4.jpg',
        },
        {
            'nombre': 'Zona de agilidad',
            'descripcion': 'Escaleras, kettlebells y trabajo de coordinación.',
            'categoria': 'funcional',
            'categoria_label': 'Funcional',
            'icono': 'wind',
            'imagen': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/3320f82734639b4e28f198d59f5ddd6dfa97a697.jpg',
        },
    ]

    coaches = [
        {
            'nombre': 'Marco Ibarra',
            'especialidad': 'Fuerza e hipertrofia',
            'bio': 'Especialista en entrenamiento de fuerza con más de 8 años de experiencia.',
            'foto': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/2f7d4744c62351a4e9ece9eee5d946020ea1ceae.jpg',
            'certificaciones': ['NSCA-CPT', 'Powerlifting Coach'],
        },
        {
            'nombre': 'Renata Cruz',
            'especialidad': 'Composición corporal',
            'bio': 'Compite en fisicoculturismo y guía a clientas en transformación física.',
            'foto': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/711aa26add39d8dae528523a6c296cad3c66c9ea.jpg',
            'certificaciones': ['IFBB Pro', 'Nutrición Deportiva'],
        },
        {
            'nombre': 'Diego Salas',
            'especialidad': 'Entrenamiento funcional',
            'bio': 'Enfocado en movilidad, acondicionamiento y prevención de lesiones.',
            'foto': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/13b912fef60fee24d84f17468174e361c7381ef4.jpg',
            'certificaciones': ['CrossFit L2', 'Movilidad Funcional'],
        },
        {
            'nombre': 'Valentina Ríos',
            'especialidad': 'Alto rendimiento',
            'bio': 'Atleta competitiva enfocada en fuerza explosiva y resistencia.',
            'foto': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/aeae0d8c8bbae07a82ff7854b2aa24b77409662d.jpg',
            'certificaciones': ['ACE-CPT', 'Bodybuilding Coach'],
        },
    ]

    galeria = [
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/17abae195c60fa8cb3fe209db9fb0a8d22852e57.jpg', 'alt': 'Interior moderno del gimnasio'},
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/2e9d048dbc1c527d04e4e925db861c2c1ca7ce70.jpg', 'alt': 'Área de pesas y máquinas'},
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/65997af450f1b6f536b2cb7d214f6d64c724d8ff.jpg', 'alt': 'Zona de entrenamiento amplia'},
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/cb7145f103d3e3ea1fe681a444367e3e938fe811.jpg', 'alt': 'Área de pesas libres'},
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/f42037c41ca25e90e094b1f545d8e0c16de2d066.jpg', 'alt': 'Zona funcional con turf'},
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/3320f82734639b4e28f198d59f5ddd6dfa97a697.jpg', 'alt': 'Área de agilidad'},
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/9b2d3181e215fbdbb30e5c4abf50b201c7330bf2.jpg', 'alt': 'Atleta entrenando'},
        {'url': 'https://pplx-res.cloudinary.com/image/upload/pplx_search_images/d1c71a1a398ee18327cd5916af4d2f0c4563cffe.jpg', 'alt': 'Vista general del gimnasio'},
    ]

    testimonios = [
        {'texto': 'Llevo 6 meses entrenando aquí y el ambiente es increíble, se nota la disciplina.', 'nombre': 'Andrea López', 'inicial': 'A', 'tiempo': 'Miembro Pro · 6 meses'},
        {'texto': 'Los coaches realmente saben lo que hacen, mi técnica mejoró muchísimo.', 'nombre': 'Jorge Medina', 'inicial': 'J', 'tiempo': 'Miembro Elite · 1 año'},
        {'texto': 'El equipo está siempre en buen estado y nunca hay saturación.', 'nombre': 'Paola Ruiz', 'inicial': 'P', 'tiempo': 'Miembro Básico · 3 meses'},
    ]

    context = {
        'servicios': servicios,
        'planes': planes,
        'categorias_maquinas': categorias_maquinas,
        'maquinas': maquinas,
        'coaches': coaches,
        'galeria': galeria,
        'testimonios': testimonios,
    }

    return render(request, 'core/landing.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'core/login.html')


@login_required
def dashboard_redirect(request):
    """Redirige al dashboard según el rol del usuario"""
    rol = request.user.rol
    if rol == 'cliente':
        return redirect('cliente:inicio')
    elif rol in ['administrador', 'recepcionista']:
        return redirect('administrador:inicio')
    elif rol == 'entrenador':
        return redirect('administrador:inicio')
    return redirect('landing')


def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})