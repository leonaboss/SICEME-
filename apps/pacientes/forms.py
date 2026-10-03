# -*- coding: utf-8 -*-
from django import forms
from apps.pacientes.models import Paciente

class PacienteForm(forms.ModelForm):
    """Formulario para la gestión directa de pacientes"""
    class Meta:
        model = Paciente
        fields = ['cedula', 'nombre_completo', 'edad', 'sexo', 'telefono', 'dependencia']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula de Identidad', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'}),
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y Apellido'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'dependencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dependencia'}),
        }
