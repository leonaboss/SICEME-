"""
SICEME - Modelos de Morbilidades
Emergencias, Especialistas, Pacientes No Asistidos
"""
from django.db import models
from django.conf import settings
from apps.especialistas.models import Especialidad, Especialista


class MorbilidadEmergencia(models.Model):
    """Registro de morbilidad de pacientes en emergencias"""

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'

    cedula = models.CharField(max_length=20, verbose_name='Cédula')
    nombre_apellido = models.CharField(max_length=200, verbose_name='Nombre y Apellido')
    edad = models.IntegerField(verbose_name='Edad')
    sexo = models.CharField(max_length=1, choices=Sexo.choices, verbose_name='Sexo')
    dependencia = models.CharField(max_length=150, blank=True, default='', verbose_name='Dependencia')
    telefono = models.CharField(max_length=20, blank=True, default='', verbose_name='Teléfono')
    codigo = models.CharField(max_length=50, blank=True, default='', verbose_name='Código')
    medico = models.CharField(max_length=150, verbose_name='Médico')
    diagnostico = models.TextField(verbose_name='Diagnóstico', blank=True, default='')
    fecha_diagnostico = models.DateField(verbose_name='Fecha de Diagnóstico')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='emergencias_registradas', verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'morbilidad_emergencias'
        verbose_name = 'Morbilidad Emergencia'
        verbose_name_plural = 'Morbilidades Emergencias'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['fecha_diagnostico']),
            models.Index(fields=['activo', '-created_at']),
            models.Index(fields=['activo', 'fecha_diagnostico']),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inicial_activo = self.activo

    def __str__(self):
        return f"{self.nombre_apellido} - {self.medico} ({self.fecha_diagnostico})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if self.medico:
            from apps.especialistas.models import Especialidad, Especialista, EstadisticaEspecialidad
            
            # 1. Obtener o crear especialidad de Emergencias
            esp, _ = Especialidad.objects.get_or_create(
                nombre__iexact='Emergencias',
                defaults={'nombre': 'Emergencias'}
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
            mes = self.fecha_diagnostico.month if self.fecha_diagnostico else self.created_at.month
            anio = self.fecha_diagnostico.year if self.fecha_diagnostico else self.created_at.year
            
            stat, _ = EstadisticaEspecialidad.objects.get_or_create(
                especialidad=esp,
                medico=med,
                mes=mes,
                anio=anio,
                defaults={'total_pacientes': 0}
            )

            # Lógica de actualización:
            # - Si es nuevo y activo: +1
            # - Si pasó de inactivo a activo: +1
            # - Si pasó de activo a inactivo: -1
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


class MorbilidadEspecialista(models.Model):
    """Registro de morbilidad de pacientes atendidos por especialistas"""

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'

    nombre_apellido = models.CharField(max_length=200, verbose_name='Nombre y Apellido')
    edad = models.IntegerField(verbose_name='Edad')
    sexo = models.CharField(max_length=1, choices=Sexo.choices, verbose_name='Sexo')
    motivo_consulta = models.TextField(verbose_name='Motivo de Consulta')
    diagnostico = models.TextField(verbose_name='Diagnóstico')
    proxima_cita = models.DateField(null=True, blank=True, verbose_name='Próxima Cita')
    especialista = models.CharField(max_length=150, verbose_name='Especialista')
    especialidad = models.CharField(max_length=150, verbose_name='Especialidad')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='morbilidades_esp_registradas', verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'morbilidad_especialistas'
        verbose_name = 'Morbilidad Especialista'
        verbose_name_plural = 'Morbilidades Especialistas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['especialidad']),
            models.Index(fields=['activo', '-created_at']),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inicial_activo = self.activo

    def __str__(self):
        return f"{self.nombre_apellido} - {self.especialista}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if self.especialista and self.especialidad:
            from apps.especialistas.models import Especialidad, Especialista, EstadisticaEspecialidad
            
            # 1. Obtener o crear especialidad
            esp, _ = Especialidad.objects.get_or_create(
                nombre__iexact=self.especialidad.strip(),
                defaults={'nombre': self.especialidad.strip().title()}
            )
            
            # 2. Obtener o crear el especialista
            med, _ = Especialista.objects.get_or_create(
                nombre_completo__iexact=self.especialista.strip(),
                defaults={
                    'nombre_completo': self.especialista.strip().title(),
                    'especialidad': esp
                }
            )
            
            # 3. Registrar o actualizar estadística
            fecha = self.created_at if self.created_at else None
            # fallback en caso de bulk creates / etc
            import datetime
            hoy = datetime.date.today()
            mes = fecha.month if fecha else hoy.month
            anio = fecha.year if fecha else hoy.year
            
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


class PacienteNoAsistido(models.Model):
    """Registro de pacientes que no asistieron a su cita"""

    class Sexo(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'

    nombre_completo = models.CharField(max_length=200, verbose_name='Nombre Completo')
    edad = models.IntegerField(verbose_name='Edad')
    sexo = models.CharField(max_length=1, choices=Sexo.choices, verbose_name='Sexo')
    medico = models.CharField(max_length=150, verbose_name='Médico')
    especialidad = models.CharField(max_length=150, verbose_name='Especialidad')
    fecha_cita = models.DateField(verbose_name='Fecha de Cita')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='no_asistidos_registrados', verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'pacientes_no_asistidos'
        verbose_name = 'Paciente No Asistido'
        verbose_name_plural = 'Pacientes No Asistidos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['activo', '-created_at']),
            models.Index(fields=['activo', 'fecha_cita']),
        ]

    def __str__(self):
        return f"{self.nombre_completo} - No asistió ({self.fecha_cita})"
