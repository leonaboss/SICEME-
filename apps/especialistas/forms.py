"""SICEME - Formularios de Especialistas"""
from django import forms
from .models import Especialidad, Especialista


class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre', 'es_vigilancia_centinela']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la especialidad',
                'id': 'especialidad-nombre'
            }),
            'es_vigilancia_centinela': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'especialidad-centinela'
            }),
        }


class EspecialistaForm(forms.ModelForm):
    especialidad_texto = forms.CharField(
        label='Especialidad',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'especialidad-input',
            'list': 'especialidades-list',
            'placeholder': 'Escriba o seleccione de la lista...',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Especialista
        fields = ['nombre_completo', 'cedula', 'telefono', 'usuario']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo del especialista',
                'id': 'especialista-nombre'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. V-12345678',
                'id': 'especialista-cedula'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+58 4XX-XXXXXXX',
                'id': 'especialista-telefono'
            }),
            'usuario': forms.Select(attrs={
                'class': 'form-select',
                'id': 'especialista-usuario'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se está editando y tiene especialidad, precargar el nombre en el campo texto
        if self.instance and self.instance.pk and self.instance.especialidad:
            self.fields['especialidad_texto'].initial = self.instance.especialidad.nombre

    def save(self, commit=True):
        instance = super().save(commit=False)
        esp_texto = self.cleaned_data.get('especialidad_texto')
        if esp_texto:
            # Buscar si la especialidad existe ignorando mayúsculas/minúsculas, sino la crea
            esp, created = Especialidad.objects.get_or_create(
                nombre__iexact=esp_texto.strip(),
                defaults={'nombre': esp_texto.strip().title()}
            )
            instance.especialidad = esp
        
        if commit:
            instance.save()
        return instance
