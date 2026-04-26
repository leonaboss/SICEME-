"""
SICEME - Formularios de Usuarios
Login, Registro, 2FA, Recuperación de contraseña
"""
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm,
    PasswordResetForm, SetPasswordForm
)
from django.core.exceptions import ValidationError
from .models import Usuario


class LoginForm(forms.Form):
    """Formulario de inicio de sesión"""
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nombre de usuario',
            'autofocus': True,
            'id': 'login-username'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Contraseña',
            'id': 'login-password'
        })
    )


class OTPForm(forms.Form):
    """Formulario para verificación de segundo factor"""
    otp_code = forms.CharField(
        label='Código de verificación',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '000000',
            'autofocus': True,
            'autocomplete': 'off',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'id': 'otp-code'
        })
    )


class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro de usuarios"""
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com',
            'id': 'registro-email'
        })
    )
    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre',
            'id': 'registro-nombre'
        })
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido',
            'id': 'registro-apellido'
        })
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+58 4XX-XXXXXXX',
            'id': 'registro-telefono'
        })
    )
    rol = forms.ChoiceField(
        label='Rol',
        choices=Usuario.Rol.choices,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'registro-rol'
        })
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'telefono', 'rol', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario',
                'id': 'registro-username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mínimo 16 caracteres',
            'id': 'registro-password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repetir contraseña',
            'id': 'registro-password2'
        })
        self.fields['password1'].help_text = 'La contraseña debe tener al menos 16 caracteres.'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Ya existe un usuario con este correo electrónico.')
        return email


class EditarUsuarioForm(forms.ModelForm):
    """Formulario para editar usuarios (admin)"""

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'telefono', 'rol', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PerfilUsuarioForm(forms.ModelForm):
    """Formulario para que el usuario edite su propio perfil"""

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'imagen_perfil']

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+58 4XX-XXXXXXX'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificar si otro usuario (distinto al actual) ya tiene este correo
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Ya existe otro usuario con este correo electrónico.')
        return email


class CambiarPasswordForm(PasswordChangeForm):
    """Formulario para cambio de contraseña"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (mínimo 16 caracteres)'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repetir nueva contraseña'
        })


class ReautenticarForm(forms.Form):
    """Formulario para reautenticación antes de eliminar usuario"""
    password = forms.CharField(
        label='Confirme su contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña para confirmar',
            'id': 'reauth-password'
        })
    )


class RecuperarPasswordForm(PasswordResetForm):
    """Formulario de recuperación de contraseña"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Correo electrónico registrado',
            'id': 'recuperar-email'
        })


class NuevoPasswordForm(SetPasswordForm):
    """Formulario para establecer nueva contraseña"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (mínimo 16 caracteres)'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Repetir nueva contraseña'
        })
