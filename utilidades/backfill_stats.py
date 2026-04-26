import os
import django
import sys

# Add project root to path
sys.path.append(r'c:\Users\Leonardo Revilla\Desktop\Morbilidades')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siceme.settings')
django.setup()

from apps.emergencias.models import MorbilidadEmergencia, MorbilidadEspecialista
from apps.ecosonogramas.models import MorbilidadEcosonograma
from apps.especialistas.models import EstadisticaEspecialidad, Especialista, Especialidad
import datetime

print("Iniciando backfill de estadísticas...")
EstadisticaEspecialidad.objects.all().delete()

for m in MorbilidadEmergencia.objects.all():
    esp, _ = Especialidad.objects.get_or_create(nombre='Emergencias')
    med, _ = Especialista.objects.get_or_create(nombre_completo=m.medico.title(), defaults={'especialidad': esp})
    mes = m.fecha_diagnostico.month if m.fecha_diagnostico else m.created_at.month
    anio = m.fecha_diagnostico.year if m.fecha_diagnostico else m.created_at.year
    stat, _ = EstadisticaEspecialidad.objects.get_or_create(especialidad=esp, medico=med, mes=mes, anio=anio)
    stat.total_pacientes += 1
    stat.save()

for m in MorbilidadEspecialista.objects.all():
    esp, _ = Especialidad.objects.get_or_create(nombre=m.especialidad.title())
    med, _ = Especialista.objects.get_or_create(nombre_completo=m.especialista.title(), defaults={'especialidad': esp})
    mes = m.created_at.month
    anio = m.created_at.year
    stat, _ = EstadisticaEspecialidad.objects.get_or_create(especialidad=esp, medico=med, mes=mes, anio=anio)
    stat.total_pacientes += 1
    stat.save()

for m in MorbilidadEcosonograma.objects.all():
    esp, _ = Especialidad.objects.get_or_create(nombre='Ecosonogramas')
    med, _ = Especialista.objects.get_or_create(nombre_completo=m.medico.title(), defaults={'especialidad': esp})
    mes = m.fecha.month if m.fecha else m.created_at.month
    anio = m.fecha.year if m.fecha else m.created_at.year
    stat, _ = EstadisticaEspecialidad.objects.get_or_create(especialidad=esp, medico=med, mes=mes, anio=anio)
    stat.total_pacientes += 1
    stat.save()

print("Backfill finalizado exitosamente!")
