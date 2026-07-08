from django import forms
from .models import Producto, TipoMembresia


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ('nombre', 'imagen', 'stock', 'precio', 'activo')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TipoMembresiaForm(forms.ModelForm):
    class Meta:
        model = TipoMembresia
        fields = ('nombre', 'precio', 'descripcion', 'activo')
        widgets = {
            'nombre': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }