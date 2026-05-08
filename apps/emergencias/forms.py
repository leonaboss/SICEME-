"""SICEME - Formularios de Emergencias y Morbilidades"""
from django import forms
from .models import MorbilidadEmergencia, MorbilidadEspecialista, PacienteNoAsistido
from apps.especialistas.models import Especialidad, Especialista


class MorbilidadEmergenciaForm(forms.ModelForm):
    class Meta:
        model = MorbilidadEmergencia
        fields = [
            'cedula', 'nombre_apellido', 'edad', 'sexo',
            'dependencia', 'telefono', 'codigo',
            'medico', 'diagnostico', 'fecha_diagnostico'
        ]
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'V-12345678'}),
            'nombre_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y Apellido'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'dependencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dependencia'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+58 4XX-XXXXXXX'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código'}),
            'medico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Médico'}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Diagnóstico del paciente'}),
            'fecha_diagnostico': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class MorbilidadEspecialistaForm(forms.ModelForm):
    class Meta:
        model = MorbilidadEspecialista
        fields = [
            'nombre_apellido', 'edad', 'sexo',
            'motivo_consulta', 'diagnostico', 'proxima_cita',
            'especialista', 'especialidad'
        ]
        widgets = {
            'nombre_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y Apellido'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proxima_cita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'especialista': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Especialista'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especialidad'}),
        }


class PacienteNoAsistidoForm(forms.ModelForm):
    class Meta:
        model = PacienteNoAsistido
        fields = [
            'nombre_completo', 'edad', 'sexo',
            'medico', 'especialidad', 'fecha_cita'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre Completo'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'medico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Médico'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especialidad'}),
            'fecha_cita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
