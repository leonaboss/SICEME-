"""SICEME - Modelo de Ecosonogramas"""
from django.db import models
from django.conf import settings
from apps.especialistas.models import Especialista


class MorbilidadEcosonograma(models.Model):
    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'

    nombre_apellido = models.CharField(max_length=200, verbose_name='Nombre y Apellido')
    edad = models.IntegerField(verbose_name='Edad')
    sexo = models.CharField(max_length=1, choices=Sexo.choices, verbose_name='Sexo')
    cedula = models.CharField(max_length=20, verbose_name='Cédula')
    procedencia = models.CharField(max_length=150, blank=True, default='', verbose_name='Procedencia')
    tipo_eco = models.CharField(max_length=150, verbose_name='Tipo de Ecosonograma')
    numero_cedula = models.CharField(max_length=20, blank=True, default='', verbose_name='Número de Cédula')
    diagnostico = models.TextField(verbose_name='Diagnóstico')
    medico = models.CharField(max_length=150, verbose_name='Médico')
    fecha = models.DateField(verbose_name='Fecha')
    planes = models.CharField(max_length=200, blank=True, default='', verbose_name='Planes')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='ecosonogramas_registrados', verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'morbilidad_ecos'
        verbose_name = 'Ecosonograma'
        verbose_name_plural = 'Ecosonogramas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['activo', '-created_at']),
            models.Index(fields=['activo', 'fecha']),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inicial_activo = self.activo

    def __str__(self):
        return f"{self.nombre_apellido} - {self.tipo_eco} ({self.fecha})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if self.medico:
            from apps.especialistas.models import Especialidad, Especialista, EstadisticaEspecialidad
            
            # 1. Obtener o crear especialidad "Ecosonogramas"
            esp, _ = Especialidad.objects.get_or_create(
                nombre__iexact='Ecosonogramas',
                defaults={'nombre': 'Ecosonogramas'}
            )
            
            # 2. Obtener o crear el especialista
            med, _ = Especialista.objects.get_or_create(
                nombre_completo__iexact=self.medico.strip(),
                defaults={
                    'nombre_completo': self.medico.strip().title(),
                    'especialidad': esp
                }
            )
            
            # 3. Registrar o actualizar estadística
            mes = self.fecha.month if self.fecha else self.created_at.month
            anio = self.fecha.year if self.fecha else self.created_at.year
            
            stat, _ = EstadisticaEspecialidad.objects.get_or_create(
                especialidad=esp,
                medico=med,
                mes=mes,
                anio=anio,
                defaults={'total_pacientes': 0}
            )

            # Lógica de actualización:
            if is_new and self.activo:
                stat.total_pacientes += 1
                stat.save()
            elif not is_new and self._inicial_activo != self.activo:
                if self.activo:
                    stat.total_pacientes += 1
                else:
                    stat.total_pacientes = max(0, stat.total_pacientes - 1)
                stat.save()
        
        self._inicial_activo = self.activo
