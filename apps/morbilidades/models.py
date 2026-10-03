# -*- coding: utf-8 -*-
"""
SICEME - Modelo Maestro y Unificado de Morbilidades
Centraliza absolutamente todos los eventos de salud en una sola tabla,
relacionados con Pacientes, Especialistas y Especialidades.
"""
from django.db import models
from django.conf import settings
from apps.pacientes.models import Paciente
import datetime


class Especialidad(models.Model):
    """Catálogo maestro de especialidades médicas"""
    nombre = models.CharField(max_length=150, unique=True, verbose_name='Nombre')
    es_vigilancia_centinela = models.BooleanField(default=False, verbose_name='Vigilancia Centinela')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'especialidades'
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Especialista(models.Model):
    """Catálogo maestro de especialistas médicos"""
    nombre_completo = models.CharField(max_length=200, verbose_name='Nombre Completo')
    cedula = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name='Cédula')
    telefono = models.CharField(max_length=20, blank=True, default='', verbose_name='Teléfono')
    especialidad = models.ForeignKey(
        Especialidad, on_delete=models.PROTECT,
        related_name='especialistas', verbose_name='Especialidad'
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='especialista_perfil', verbose_name='Usuario del Sistema'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'especialistas'
        verbose_name = 'Especialista'
        verbose_name_plural = 'Especialistas'
        ordering = ['nombre_completo']

    def __str__(self):
        return self.nombre_completo


class EstadisticaEspecialidad(models.Model):
    """Estadísticas dinámicas por especialidad y médico"""
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='estadisticas', verbose_name='Especialidad')
    medico = models.ForeignKey(Especialista, on_delete=models.CASCADE, related_name='estadisticas', verbose_name='Médico')
    total_pacientes = models.IntegerField(default=0, verbose_name='Total Pacientes')
    mes = models.IntegerField(verbose_name='Mes')
    anio = models.IntegerField(verbose_name='Año')

    class Meta:
        db_table = 'estadisticas_especialidad'
        verbose_name = 'Estadística por Especialidad'
        verbose_name_plural = 'Estadísticas por Especialidad'
        unique_together = ['especialidad', 'medico', 'mes', 'anio']
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"{self.medico.nombre_completo} - {self.especialidad.nombre}: {self.total_pacientes} ({self.mes}/{self.anio})"

# ═════════════════════════════════════════════
# Modelo de Morbilidad Centralizada
# ═════════════════════════════════════════════

class Morbilidad(models.Model):
    """
    TABLA MAESTRA UNIFICADA DE MORBILIDADES.
    Concentra Emergencias, Consultas de Especialistas, Ecosonogramas y Pacientes No Asistidos.
    """
    class TipoMovimiento(models.TextChoices):
        EMERGENCIA = 'EMERGENCIA', 'Emergencia'
        CONSULTA_ESPECIALISTA = 'CONSULTA_ESPECIALISTA', 'Consulta por Especialista'
        ECOSONOGRAMA = 'ECOSONOGRAMA', 'Ecosonograma'
        NO_ASISTIDO = 'NO_ASISTIDO', 'Paciente No Asistido'

    # Datos relacionales clave
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='morbilidades', verbose_name='Paciente')
    tipo_modulo = models.CharField(max_length=30, choices=TipoMovimiento.choices, verbose_name='Tipo de Módulo', default='EMERGENCIA')
    
    medico = models.ForeignKey(Especialista, on_delete=models.PROTECT, related_name='morbilidades_atendidas', null=True, blank=True, verbose_name='Médico Atendiente')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.PROTECT, related_name='morbilidades_por_especialidad', null=True, blank=True, verbose_name='Especialidad')

    # Campos unificados para todos los tipos de registros médicos
    diagnostico = models.TextField(blank=True, default='', verbose_name='Diagnóstico')
    fecha_evento = models.DateField(verbose_name='Fecha del Evento')
    
    # Específicos por módulo
    motivo_consulta = models.TextField(blank=True, default='', verbose_name='Motivo de Consulta')
    proxima_cita = models.DateField(null=True, blank=True, verbose_name='Próxima Cita')
    codigo_emergencia = models.CharField(max_length=50, blank=True, default='', verbose_name='Código de Emergencia')
    procedencia = models.CharField(max_length=150, blank=True, default='', verbose_name='Procedencia')
    tipo_ecosonograma = models.CharField(max_length=150, blank=True, default='', verbose_name='Tipo de Ecosonograma')
    planes = models.CharField(max_length=200, blank=True, default='', verbose_name='Planes / Tratamiento')

    # Auditoría y estado
    usuario_registro = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='morbilidades_registradas', verbose_name='Registrado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'morbilidades'
        verbose_name = 'Morbilidad'
        verbose_name_plural = 'Morbilidades'
        ordering = ['-fecha_evento', '-created_at']
        indexes = [
            models.Index(fields=['paciente']),
            models.Index(fields=['tipo_modulo']),
            models.Index(fields=['fecha_evento']),
            models.Index(fields=['activo', '-fecha_evento']),
            models.Index(fields=['especialidad']),
        ]

    def __str__(self):
        return f"[{self.get_tipo_modulo_display()}] {self.paciente.nombre_completo} - {self.fecha_evento}"
