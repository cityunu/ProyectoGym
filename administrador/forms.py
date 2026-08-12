from django import forms
from django.contrib.auth import get_user_model
from .models import Producto, TipoMembresia

Usuario = get_user_model()


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'imagen', 'stock', 'precio', 'activo']


class TipoMembresiaForm(forms.ModelForm):
    class Meta:
        model = TipoMembresia
        fields = ['precio', 'duracion_dias', 'descripcion', 'activo']


class AsignarMembresiaForm(forms.Form):
    usuario = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        label='Cliente',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    tipo = forms.ModelChoiceField(
        queryset=TipoMembresia.objects.filter(activo=True),
        label='Tipo de membresía',
        widget=forms.Select(attrs={'class': 'form-input'})
    )