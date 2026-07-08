from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import password_validators_help_text_html
from .models import Usuario


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput()
    )

    first_name = forms.CharField(
        max_length=50,
        label='Nombre',
        widget=forms.TextInput()
    )

    last_name = forms.CharField(
        max_length=50,
        label='Apellido',
        widget=forms.TextInput()
    )

    telefono = forms.CharField(
        max_length=15,
        required=False,
        label='Teléfono',
        widget=forms.TextInput()
    )

    password1 = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(),
        help_text=password_validators_help_text_html()
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        strip=False,
        widget=forms.PasswordInput(),
        help_text='Escribe la misma contraseña para confirmar.'
    )

    class Meta:
        model = Usuario
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'telefono',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        common = {
            'class': 'auth-input',
        }

        self.fields['username'].widget = forms.TextInput(attrs={
            **common,
            'placeholder': 'Crea tu usuario',
            'autocomplete': 'username',
            'autofocus': True,
        })

        self.fields['first_name'].widget = forms.TextInput(attrs={
            **common,
            'placeholder': 'Tu nombre',
            'autocomplete': 'given-name',
        })

        self.fields['last_name'].widget = forms.TextInput(attrs={
            **common,
            'placeholder': 'Tu apellido',
            'autocomplete': 'family-name',
        })

        self.fields['email'].widget = forms.EmailInput(attrs={
            **common,
            'placeholder': 'tu@email.com',
            'autocomplete': 'email',
        })

        self.fields['telefono'].widget = forms.TextInput(attrs={
            **common,
            'placeholder': 'Tu teléfono',
            'autocomplete': 'tel',
        })

        self.fields['password1'].widget = forms.PasswordInput(attrs={
            **common,
            'placeholder': 'Crea una contraseña',
            'autocomplete': 'new-password',
        })

        self.fields['password2'].widget = forms.PasswordInput(attrs={
            **common,
            'placeholder': 'Confirma tu contraseña',
            'autocomplete': 'new-password',
        })

        self.fields['username'].help_text = 'Usa un nombre de usuario único.'
        self.fields['telefono'].help_text = 'Opcional.'
        self.fields['password2'].help_text = 'Debe coincidir exactamente con la contraseña anterior.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'cliente'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telefono = self.cleaned_data['telefono']

        if commit:
            user.save()
        return user