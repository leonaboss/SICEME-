
"""
SICEME - Modelo de Pacientes
"""
from django.db import models

class Paciente(models.Model):
    """Información demográfica de un paciente."""

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'

    cedula = models.CharField(max_length=20, unique=True, verbose_name='Cédula')
    nombre_completo = models.CharField(max_length=200, verbose_name='Nombre Completo')
    edad = models.IntegerField(verbose_name='Edad') # Considerar Fecha de Nacimiento para calcular edad
    sexo = models.CharField(max_length=1, choices=Sexo.choices, verbose_name='Sexo')
    telefono = models.CharField(max_length=20, blank=True, default='', verbose_name='Teléfono')
    dependencia = models.CharField(max_length=150, blank=True, default='', verbose_name='Dependencia')
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'pacientes'
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['nombre_completo']
        indexes = [
            models.Index(fields=['cedula']),
            models.Index(fields=['nombre_completo']),
            models.Index(fields=['activo', '-created_at']),
        ]

    def __str__(self):
        return f"{self.nombre_completo} ({self.cedula})"
