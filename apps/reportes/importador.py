import openpyxl
from datetime import datetime
from apps.emergencias.models import MorbilidadEmergencia, MorbilidadEspecialista, PacienteNoAsistido
from apps.ecosonogramas.models import MorbilidadEcosonograma
from django.db import transaction

def parse_fecha(valor, default=None):
    if not valor:
        return default
    if isinstance(valor, datetime):
        return valor.date()
    try:
        # Intenta parsear desde string DD/MM/YYYY
        return datetime.strptime(str(valor).strip(), '%d/%m/%Y').date()
    except ValueError:
        try:
            return datetime.strptime(str(valor).strip(), '%Y-%m-%d').date()
        except ValueError:
            return default

def parse_sexo(valor, default='M'):
    v = str(valor).strip().upper()
    if v in ['M', 'MASCULINO']:
        return 'M'
    elif v in ['F', 'FEMENINO']:
        return 'F'
    return default

def procesar_importacion_excel(archivo_xlsx, tipo, usuario):
    """
    Lee un archivo excel y crea registros. 
    Soporta múltiples hojas si el tipo es 'consolidado' o procesa la activa por defecto.
    """
    wb = openpyxl.load_workbook(archivo_xlsx, data_only=True)
    creados_total = 0
    errores_total = []

    # Si es consolidado, recorremos todas las hojas, si no, solo la activa
    hojas_a_procesar = wb.sheetnames if tipo == 'consolidado' else [wb.active.title]

    for nombre_hoja in hojas_a_procesar:
        ws = wb[nombre_hoja]
        filas = list(ws.iter_rows(values_only=True))
        if len(filas) <= 1: continue # Saltear si está vacía
        
        datos = filas[1:] # Omitir encabezado
        
        # Intentar detectar el tipo por nombre de hoja si es consolidado
        tipo_actual = tipo
        if tipo == 'consolidado':
            n = nombre_hoja.lower()
            if 'emergencia' in n: tipo_actual = 'emergencias'
            elif 'especialista' in n: tipo_actual = 'morbilidad_especialista'
            elif 'eco' in n: tipo_actual = 'ecosonogramas'
            elif 'no asistido' in n or 'no_asistido' in n: tipo_actual = 'no_asistidos'
            else: continue # Saltar hojas que no reconozca

        try:
            with transaction.atomic():
                for i, row in enumerate(datos, start=2):
                    if not row or len(row) < 3: continue
                    if not row[1] and not row[2]: continue # Fila vacía
                    
                    try:
                        if tipo_actual == 'emergencias':
                            MorbilidadEmergencia.objects.create(
                                usuario=usuario,
                                cedula=str(row[1]).strip() if row[1] else "",
                                nombre_apellido=str(row[2]).strip(),
                                edad=int(row[3]) if row[3] else 0,
                                sexo=parse_sexo(row[4]),
                                dependencia=str(row[5]).strip() if row[5] else "",
                                telefono=str(row[6]).strip() if row[6] else "",
                                codigo=str(row[7]).strip() if row[7] else "",
                                medico=str(row[8]).strip() if row[8] else "No asignado",
                                fecha_diagnostico=parse_fecha(row[9], datetime.now().date())
                            )
                        elif tipo_actual == 'morbilidad_especialista':
                            MorbilidadEspecialista.objects.create(
                                usuario=usuario,
                                nombre_apellido=str(row[1]).strip(),
                                edad=int(row[2]) if row[2] else 0,
                                sexo=parse_sexo(row[3]),
                                motivo_consulta=str(row[4]).strip() if row[4] else "",
                                diagnostico=str(row[5]).strip() if row[5] else "",
                                proxima_cita=parse_fecha(row[6]),
                                especialista=str(row[7]).strip() if row[7] else "No asignado",
                                especialidad=str(row[8]).strip() if row[8] else "General"
                            )
                        elif tipo_actual == 'no_asistidos':
                            PacienteNoAsistido.objects.create(
                                usuario=usuario,
                                nombre_completo=str(row[1]).strip(),
                                edad=int(row[2]) if row[2] else 0,
                                sexo=parse_sexo(row[3]),
                                medico=str(row[4]).strip() if row[4] else "No asignado",
                                especialidad=str(row[5]).strip() if row[5] else "General",
                                fecha_cita=parse_fecha(row[6], datetime.now().date())
                            )
                        elif tipo_actual == 'ecosonogramas':
                            MorbilidadEcosonograma.objects.create(
                                usuario=usuario,
                                nombre_apellido=str(row[1]).strip(),
                                edad=int(row[2]) if row[2] else 0,
                                sexo=parse_sexo(row[3]),
                                cedula=str(row[4]).strip() if row[4] else "",
                                procedencia=str(row[5]).strip() if row[5] else "",
                                tipo_eco=str(row[6]).strip() if row[6] else "No especificado",
                                numero_cedula=str(row[7]).strip() if row[7] else "",
                                diagnostico=str(row[8]).strip() if row[8] else "",
                                medico=str(row[9]).strip() if row[9] else "No asignado",
                                fecha=parse_fecha(row[10], datetime.now().date()),
                                planes=str(row[11]).strip() if len(row) > 11 and row[11] else ""
                            )
                        creados_total += 1
                    except Exception as e:
                        errores_total.append(f"Hoja {nombre_hoja}, Fila {i}: {str(e)}")
        except Exception as e:
            errores_total.append(f"Error crítico en hoja {nombre_hoja}: {str(e)}")

    return creados_total, errores_total
