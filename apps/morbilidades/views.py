# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import BitacoraAuditoria
from apps.morbilidades.models import Morbilidad, Especialidad, Especialista
from apps.jornadas.models import Jornada
from apps.morbilidades.forms import EmergenciaForm, EspecialistaForm, EcosonogramaForm, EspecialidadForm, EmergenciaForm as MorbilidadUnificadaForm


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_morbilidades_view(request, tipo=None):
    """Vista unificada para listar morbilidades con filtros por tipo de movimiento"""
    query = request.GET.get('q', '')
    # Si se pasa tipo por URL (alias), se usa, si no, se busca en GET
    tipo = tipo or request.GET.get('tipo', '')
    
    registros = Morbilidad.objects.filter(activo=True).select_related('paciente', 'medico', 'especialidad', 'usuario_registro')


    if request.user.rol != 'ADMIN' or request.session.get('dashboard_vista') == 'personal':
        registros = registros.filter(usuario_registro=request.user)

    if tipo:
        registros = registros.filter(tipo_modulo=tipo)

    if query:
        registros = registros.filter(
            Q(paciente__nombre_completo__icontains=query) |
            Q(paciente__cedula__icontains=query) |
            Q(diagnostico__icontains=query)
        )

    paginator = Paginator(registros, 15)
    page = request.GET.get('page')
    registros = paginator.get_page(page)

    return render(request, 'morbilidades/lista.html', {
        'registros': registros,
        'query': query,
        'tipo_actual': tipo,
        'tipos_choices': Morbilidad.TipoMovimiento.choices
    })


from apps.morbilidades.forms import EmergenciaForm, EspecialistaForm, EcosonogramaForm

FORMS_MAP = {
    'EMERGENCIA': EmergenciaForm,
    'CONSULTA_ESPECIALISTA': EspecialistaForm,
    'ECOSONOGRAMA': EcosonogramaForm,
}

LIST_MAP = {
    'EMERGENCIA': 'lista_emergencias',
    'CONSULTA_ESPECIALISTA': 'lista_morbilidad_especialistas',
    'ECOSONOGRAMA': 'lista_ecosonogramas',
    'NO_ASISTIDO': 'lista_no_asistidos',
}

@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def crear_morbilidad_view(request, tipo=None):
    tipo = tipo or request.GET.get('tipo', 'EMERGENCIA')
    form_class = FORMS_MAP.get(tipo, EmergenciaForm)
    cancel_url_name = LIST_MAP.get(tipo, 'lista_morbilidades')
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.tipo_modulo = tipo
            reg.usuario_registro = request.user
            reg.save()
            messages.success(request, 'Registro creado.')
            return redirect(cancel_url_name)
    else:
        form = form_class(initial={'tipo_modulo': tipo})
    
    return render(request, 'morbilidades/form.html', {
        'form': form, 
        'titulo': 'Nuevo Registro',
        'cancel_url_name': cancel_url_name
    })



@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def editar_morbilidad_view(request, pk):
    """Editar un registro existente de morbilidad"""
    reg = get_object_or_404(Morbilidad, pk=pk)
    cancel_url_name = LIST_MAP.get(reg.tipo_modulo, 'lista_morbilidades')
    
    if request.user.rol != 'ADMIN' and reg.usuario_registro != request.user:
        messages.error(request, 'No tiene permiso para editar este registro.')
        return redirect('lista_morbilidades')

    if request.method == 'POST':
        form = MorbilidadUnificadaForm(request.POST, instance=reg)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Morbilidad editada: {reg.paciente.nombre_completo}', request, 'morbilidades'
            )
            messages.success(request, 'Registro actualizado exitosamente.')
            return redirect(cancel_url_name)
    else:
        form = MorbilidadUnificadaForm(instance=reg)

    return render(request, 'morbilidades/form.html', {
        'form': form,
        'titulo': 'Editar Registro de Morbilidad',
        'cancel_url_name': cancel_url_name
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def eliminar_morbilidad_view(request, pk):
    """Archivar (soft delete) un registro de morbilidad"""
    reg = get_object_or_404(Morbilidad, pk=pk)
    if request.user.rol != 'ADMIN' and reg.usuario_registro != request.user:
        messages.error(request, 'No tiene permiso para archivar este registro.')
        return redirect('lista_morbilidades')

    if request.method == 'POST':
        nombre = reg.paciente.nombre_completo if reg.paciente else 'Desconocido'
        reg.activo = False
        reg.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Morbilidad archivada: {nombre}', request, 'morbilidades'
        )
        messages.success(request, f'Registro de "{nombre}" archivado exitosamente.')
        return redirect('lista_morbilidades')

    return render(request, 'morbilidades/eliminar.html', {'registro': reg})


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def limpiar_morbilidades_view(request, tipo=None):
    if request.method == 'POST':
        tipo = tipo or request.POST.get('tipo', '')
        if request.user.rol == 'ADMIN':
            queryset = Morbilidad.objects.filter(activo=True)
        else:
            queryset = Morbilidad.objects.filter(activo=True, usuario_registro=request.user)
        
        if tipo:
            queryset = queryset.filter(tipo_modulo=tipo)
            
        total = queryset.count()
        for reg in queryset:
            reg.activo = False
            reg.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Morbilidades archivadas masivamente ({tipo or "Todas"}): {total} registros', request, 'morbilidades'
        )
        messages.success(request, f'{total} registros archivados exitosamente.')
    return redirect('lista_morbilidades')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_entrada_view(request):
    if request.method == 'POST':
        especialista_id = request.POST.get('especialista_id')
        if not especialista_id and request.user.rol == 'ESPECIALISTA':
            especialista_id = request.user.especialista_perfil.pk
        
        if especialista_id:
            especialista = get_object_or_404(Especialista, pk=especialista_id)
            Jornada.objects.create(especialista=especialista, hora_entrada=timezone.now())
            messages.success(request, 'Entrada registrada.')
        else:
            messages.error(request, 'Especialista no válido.')
    return redirect('lista_jornadas')

@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_pausa_inicio_view(request, pk):
    jornada = get_object_or_404(Jornada, pk=pk)
    jornada.pausa_inicio = timezone.now()
    jornada.save()
    messages.success(request, 'Pausa iniciada.')
    return redirect('lista_jornadas')

@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_pausa_fin_view(request, pk):
    jornada = get_object_or_404(Jornada, pk=pk)
    jornada.pausa_fin = timezone.now()
    jornada.save()
    messages.success(request, 'Pausa finalizada.')
    return redirect('lista_jornadas')

@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def registrar_salida_view(request, pk):
    jornada = get_object_or_404(Jornada, pk=pk)
    jornada.hora_salida = timezone.now()
    jornada.calcular_horas()
    messages.success(request, 'Salida registrada.')
    return redirect('lista_jornadas')

# ═════════════════════════════════════════════
# CRUD ESPECIALISTAS Y ESPECIALIDADES
# ═════════════════════════════════════════════

@login_required
@rol_requerido('ADMIN')
def crud_especialidades_view(request):
    """Listado y gestión de especialidades"""
    registros = Especialidad.objects.all()
    return render(request, 'especialistas/lista_especialidades.html', {'registros': registros})

@login_required
@rol_requerido('ADMIN')
def crud_especialistas_view(request):
    """Listado y gestión de especialistas"""
    registros = Especialista.objects.all().select_related('especialidad')
    return render(request, 'especialistas/lista_especialistas.html', {'registros': registros})

@login_required
@rol_requerido('ADMIN')
def crear_especialista_view(request):
    if request.method == 'POST':
        form = EspecialistaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialista creado exitosamente.')
            return redirect('crud_especialistas')
    else:
        form = EspecialistaForm()
    return render(request, 'especialistas/form_especialista.html', {'form': form, 'titulo': 'Crear Especialista'})

@login_required
@rol_requerido('ADMIN')
def editar_especialista_view(request, pk):
    especialista = get_object_or_404(Especialista, pk=pk)
    if request.method == 'POST':
        form = EspecialistaForm(request.POST, instance=especialista)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialista actualizado exitosamente.')
            return redirect('crud_especialistas')
    else:
        form = EspecialistaForm(instance=especialista)
    return render(request, 'especialistas/form_especialista.html', {'form': form, 'titulo': 'Editar Especialista'})

@login_required
@rol_requerido('ADMIN')
def eliminar_especialista_view(request, pk):
    especialista = get_object_or_404(Especialista, pk=pk)
    if request.method == 'POST':
        especialista.delete()
        messages.success(request, 'Especialista eliminado.')
        return redirect('crud_especialistas')
    return render(request, 'especialistas/eliminar_especialista.html', {'especialista': especialista})

@login_required
@rol_requerido('ADMIN')
def crear_especialidad_view(request):
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidad creada exitosamente.')
            return redirect('crud_especialidades')
    else:
        form = EspecialidadForm()
    return render(request, 'especialistas/form_especialidad.html', {'form': form, 'titulo': 'Crear Especialidad'})

@login_required
@rol_requerido('ADMIN')
def editar_especialidad_view(request, pk):
    especialidad = get_object_or_404(Especialidad, pk=pk)
    if request.method == 'POST':
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Especialidad actualizada exitosamente.')
            return redirect('crud_especialidades')
    else:
        form = EspecialidadForm(instance=especialidad)
    return render(request, 'especialistas/form_especialidad.html', {'form': form, 'titulo': 'Editar Especialidad'})

@login_required
@rol_requerido('ADMIN')
def eliminar_especialidad_view(request, pk):
    especialidad = get_object_or_404(Especialidad, pk=pk)
    if request.method == 'POST':
        especialidad.delete()
        messages.success(request, 'Especialidad eliminada.')
        return redirect('crud_especialidades')
    return render(request, 'especialistas/eliminar_especialidad.html', {'especialidad': especialidad})

@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_jornadas_view(request):
    """Listado de jornadas laborales"""
    registros = Jornada.objects.all().select_related('especialista')
    especialistas_lista = Especialista.objects.filter(activo=True)
    
    # Cálculos para dashboard
    total_horas = registros.aggregate(models.Sum('total_horas'))['total_horas__sum'] or 0
    
    paginator = Paginator(registros, 20)
    page = request.GET.get('page')
    registros = paginator.get_page(page)
    
    return render(request, 'jornadas/lista.html', {
        'jornadas': registros,
        'especialistas_lista': especialistas_lista,
        'total_horas': total_horas
    })

