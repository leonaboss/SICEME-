"""
SICEME - Modelos de Especialistas y Especialidades
"""
from django.db import models
from django.conf import settings


class Especialidad(models.Model):
    """Especialidad médica"""
    nombre = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nombre'
    )
    es_vigilancia_centinela = models.BooleanField(
        default=False,
        verbose_name='Vigilancia Centinela'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'especialidades'
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Especialista(models.Model):
    """Especialista médico"""
    nombre_completo = models.CharField(
        max_length=200,
        verbose_name='Nombre Completo'
    )
    cedula = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Cédula'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Teléfono'
    )
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        related_name='especialistas',
        verbose_name='Especialidad'
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='especialista_perfil',
        verbose_name='Usuario del Sistema'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'especialistas'
        verbose_name = 'Especialista'
        verbose_name_plural = 'Especialistas'
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} - {self.especialidad.nombre}"


class EstadisticaEspecialidad(models.Model):
    """Tabla de estadísticas por especialidad y médico (stock dinámico)"""
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.CASCADE,
        related_name='estadisticas',
        verbose_name='Especialidad'
    )
    medico = models.ForeignKey(
        Especialista,
        on_delete=models.CASCADE,
        related_name='estadisticas',
        verbose_name='Médico'
    )
    total_pacientes = models.IntegerField(
        default=0,
        verbose_name='Total Pacientes'
    )
    mes = models.IntegerField(verbose_name='Mes')
    anio = models.IntegerField(verbose_name='Año')

    class Meta:
        db_table = 'estadisticas_especialidad'
        verbose_name = 'Estadística por Especialidad'
        verbose_name_plural = 'Estadísticas por Especialidad'
        unique_together = ['especialidad', 'medico', 'mes', 'anio']
        ordering = ['-anio', '-mes']

    def __str__(self):
        return (
            f"{self.medico.nombre_completo} - {self.especialidad.nombre}: "
            f"{self.total_pacientes} pacientes ({self.mes}/{self.anio})"
        )
