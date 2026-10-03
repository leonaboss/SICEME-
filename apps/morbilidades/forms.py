# -*- coding: utf-8 -*-
from django import forms
from apps.morbilidades.models import Morbilidad, Especialista, Especialidad
from apps.pacientes.models import Paciente
from apps.morbilidades.utils import normalizar_especialista, normalizar_especialidad

class BaseMorbilidadForm(forms.ModelForm):
    """Base para campos de paciente comunes"""
    cedula = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'}))
    nombre_apellido = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    edad = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sexo = forms.ChoiceField(choices=Paciente.Sexo.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    telefono = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dependencia = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Morbilidad
        fields = ['cedula', 'nombre_apellido', 'edad', 'sexo', 'telefono', 'dependencia']

    def save_paciente(self, commit=True):
        paciente, _ = Paciente.objects.update_or_create(
            cedula=self.cleaned_data.get('cedula'),
            defaults={
                'nombre_completo': self.cleaned_data.get('nombre_apellido'),
                'edad': self.cleaned_data.get('edad'),
                'sexo': self.cleaned_data.get('sexo'),
                'telefono': self.cleaned_data.get('telefono', ''),
                'dependencia': self.cleaned_data.get('dependencia', ''),
            }
        )
        self.instance.paciente = paciente

class EmergenciaForm(BaseMorbilidadForm):
    # Re-declaramos los campos para forzar el orden exacto solicitado para Emergencias
    cedula = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'}))
    nombre_apellido = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    edad = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sexo = forms.ChoiceField(choices=Paciente.Sexo.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    telefono = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dependencia = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_modulo = forms.CharField(widget=forms.HiddenInput(), initial='EMERGENCIA')
    
    fecha_evento = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    codigo_emergencia = forms.CharField(label="Código de Emergencia", widget=forms.TextInput(attrs={'class': 'form-control'}))
    medico_nombre = forms.CharField(label="Médico", widget=forms.TextInput(attrs={'class': 'form-control'}))
    diagnostico = forms.CharField(label="Diagnóstico", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))

    class Meta(BaseMorbilidadForm.Meta):
        fields = ['cedula', 'nombre_apellido', 'edad', 'sexo', 'telefono', 'dependencia', 'tipo_modulo', 'fecha_evento', 'codigo_emergencia', 'medico_nombre', 'diagnostico']

    def save(self, commit=True):
        self.save_paciente(commit=False)
        self.instance.medico = normalizar_especialista(self.cleaned_data.get('medico_nombre'))
        self.instance.tipo_modulo = 'EMERGENCIA'
        return super().save(commit=commit)

class EspecialistaForm(BaseMorbilidadForm):
    # Re-declaramos los campos para forzar el orden y visibilidad correcta para Especialistas
    cedula = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'pattern': '[0-9]*', 'onkeypress': 'return event.charCode >= 48 && event.charCode <= 57'}))
    nombre_apellido = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    edad = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sexo = forms.ChoiceField(choices=Paciente.Sexo.choices, widget=forms.Select(attrs={'class': 'form-select'}))
    telefono = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dependencia = forms.CharField(required=False, max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    tipo_modulo = forms.CharField(widget=forms.HiddenInput(), initial='CONSULTA_ESPECIALISTA')
    
    fecha_evento = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    medico_nombre = forms.CharField(label="Especialista", widget=forms.TextInput(attrs={'class': 'form-control'}))
    especialidad_nombre = forms.CharField(label="Especialidad", widget=forms.TextInput(attrs={'class': 'form-control'}))
    motivo_consulta = forms.CharField(label="Motivo de Consulta", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    diagnostico = forms.CharField(label="Diagnóstico", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    proxima_cita = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    
    class Meta(BaseMorbilidadForm.Meta):
        fields = ['cedula', 'nombre_apellido', 'edad', 'sexo', 'telefono', 'dependencia', 'tipo_modulo', 'fecha_evento', 'medico_nombre', 'especialidad_nombre', 'motivo_consulta', 'diagnostico', 'proxima_cita']

class EcosonogramaForm(BaseMorbilidadForm):
    medico_nombre = forms.CharField(label="Médico", widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta(BaseMorbilidadForm.Meta):
        fields = BaseMorbilidadForm.Meta.fields + ['tipo_modulo', 'fecha_evento', 'tipo_ecosonograma', 'procedencia', 'diagnostico', 'planes', 'medico_nombre']
        widgets = {'fecha_evento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})}

    def save(self, commit=True):
        self.save_paciente(commit=False)
        self.instance.medico = normalizar_especialista(self.cleaned_data.get('medico_nombre'))
        return super().save(commit=commit)

class EspecialidadForm(forms.ModelForm):
    class Meta:
        model = Especialidad
        fields = ['nombre', 'es_vigilancia_centinela', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'es_vigilancia_centinela': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
