"""SICEME - Formularios de Ecosonogramas"""
from django import forms
from .models import MorbilidadEcosonograma

class EcosonogramaForm(forms.ModelForm):
    class Meta:
        model = MorbilidadEcosonograma
        fields = [
            'nombre_apellido', 'edad', 'sexo',
            'procedencia', 'tipo_eco', 'numero_cedula',
            'diagnostico', 'medico', 'fecha', 'planes'
        ]
        widgets = {
            'nombre_apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y Apellido'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),

            'procedencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Procedencia'}),
            'tipo_eco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de ecosonograma'}),
            'numero_cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'medico': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Médico'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'planes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Planes'}),
        }
