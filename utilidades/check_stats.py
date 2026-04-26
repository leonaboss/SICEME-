import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siceme.settings')
django.setup()

from apps.emergencias.models import MorbilidadEspecialista
from apps.especialistas.models import EstadisticaEspecialidad

print("--- Diagnóstico de Estadísticas ---")

# 1. Buscar un registro para probar
reg = MorbilidadEspecialista.objects.filter(activo=True).first()
if not reg:
    print("No hay registros activos para probar.")
else:
    print(f"Probando con: {reg.nombre_apellido} (Especialidad: {reg.especialidad}, Médico: {reg.especialista})")
    
    # Obtener estadística actual
    from django.utils import timezone
    hoy = timezone.now()
    stat = EstadisticaEspecialidad.objects.filter(
        especialidad__nombre__iexact=reg.especialidad.strip(),
        medico__nombre_completo__iexact=reg.especialista.strip(),
        anio=reg.created_at.year,
        mes=reg.created_at.month
    ).first()
    
    if stat:
        valor_inicial = stat.total_pacientes
        print(f"Valor inicial en EstadisticaEspecialidad: {valor_inicial}")
        
        # Archivar
        print("Archivando...")
        reg.activo = False
        reg.save()
        
        stat.refresh_from_db()
        print(f"Valor tras archivar: {stat.total_pacientes}")
        
        # Restaurar
        print("Restaurando...")
        reg.activo = True
        reg.save()
        
        stat.refresh_from_db()
        print(f"Valor tras restaurar: {stat.total_pacientes}")
        
        if stat.total_pacientes == valor_inicial:
            print("¡ÉXITO! La sincronización de modelos funciona correctamente.")
        else:
            print("ERROR: El valor final no coincide con el inicial.")
    else:
        print("No se encontró un registro de EstadisticaEspecialidad coincidente.")
