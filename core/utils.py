from django.contrib.auth import get_user_model
from .models import Bitacora

Usuario = get_user_model()


def registrar_evento(usuario, accion, detalle=''):
    """Registra un evento en la bitácora."""
    Bitacora.objects.create(
        usuario=usuario if usuario and isinstance(usuario, Usuario) else None,
        accion=accion,
        detalle=detalle,
    )