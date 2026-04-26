"""SICEME - Vistas de Emergencias y Morbilidades"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import BitacoraAuditoria
from .models import MorbilidadEmergencia, MorbilidadEspecialista, PacienteNoAsistido
from .forms import MorbilidadEmergenciaForm, MorbilidadEspecialistaForm, PacienteNoAsistidoForm


# ═════════════════════════════════════════════
# CRUD MORBILIDAD EMERGENCIAS
# ═════════════════════════════════════════════
@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_emergencias_view(request):
    query = request.GET.get('q', '')
    registros = MorbilidadEmergencia.objects.filter(activo=True).select_related('usuario')

    # Filtrar por usuario si es personal (o no es admin)
    if request.user.rol != 'ADMIN' or request.session.get('dashboard_vista') == 'personal':
        registros = registros.filter(usuario=request.user)

    if query:
        registros = registros.filter(
            Q(nombre_apellido__icontains=query) |
            Q(cedula__icontains=query)
        )

    # Filtros adicionales
    especialidad_id = request.GET.get('especialidad')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    sexo = request.GET.get('sexo')

    if fecha_desde:
        registros = registros.filter(fecha_diagnostico__gte=fecha_desde)
    if fecha_hasta:
        registros = registros.filter(fecha_diagnostico__lte=fecha_hasta)
    if sexo:
        registros = registros.filter(sexo=sexo)

    paginator = Paginator(registros, 15)
    page = request.GET.get('page')
    registros = paginator.get_page(page)

    return render(request, 'emergencias/lista.html', {
        'registros': registros, 'query': query,
        'filtros': {
            'fecha_desde': fecha_desde or '',
            'fecha_hasta': fecha_hasta or '',
            'sexo': sexo or '',
        }
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def crear_emergencia_view(request):
    if request.method == 'POST':
        form = MorbilidadEmergenciaForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Emergencia registrada: {registro.nombre_apellido}', request, 'emergencias'
            )
            messages.success(request, 'Registro de emergencia creado exitosamente.')
            return redirect('lista_emergencias')
    else:
        form = MorbilidadEmergenciaForm()
    return render(request, 'emergencias/form.html', {
        'form': form, 'titulo': 'Nuevo Registro de Emergencia'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def editar_emergencia_view(request, pk):
    registro = get_object_or_404(MorbilidadEmergencia, pk=pk)
    if request.user.rol != 'ADMIN' and registro.usuario != request.user:
        return redirect('lista_emergencias')

    if request.method == 'POST':
        form = MorbilidadEmergenciaForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Emergencia editada: {registro.nombre_apellido}', request, 'emergencias'
            )
            messages.success(request, 'Registro actualizado.')
            return redirect('lista_emergencias')
    else:
        form = MorbilidadEmergenciaForm(instance=registro)
    return render(request, 'emergencias/form.html', {
        'form': form, 'titulo': 'Editar Registro de Emergencia'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def eliminar_emergencia_view(request, pk):
    registro = get_object_or_404(MorbilidadEmergencia, pk=pk)
    
    # Refuerzo de Seguridad: Validar propiedad
    if request.user.rol != 'ADMIN' and registro.usuario != request.user:
        messages.error(request, 'No tiene permiso para archivar este registro.')
        return redirect('lista_emergencias')

    if request.method == 'POST':
        nombre = registro.nombre_apellido
        registro.activo = False
        registro.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Emergencia archivada: {nombre}', request, 'emergencias'
        )
        messages.success(request, f'Registro de "{nombre}" archivado exitosamente.')
        return redirect('lista_emergencias')
    return render(request, 'emergencias/eliminar.html', {'registro': registro})


# ═════════════════════════════════════════════
# CRUD MORBILIDAD ESPECIALISTAS
# ═════════════════════════════════════════════
@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_morbilidad_especialistas_view(request):
    query = request.GET.get('q', '')
    registros = MorbilidadEspecialista.objects.filter(activo=True).select_related('usuario')

    if request.user.rol != 'ADMIN' or request.session.get('dashboard_vista') == 'personal':
        registros = registros.filter(usuario=request.user)

    if query:
        registros = registros.filter(
            Q(nombre_apellido__icontains=query) |
            Q(especialidad__icontains=query)
        )

    paginator = Paginator(registros, 15)
    page = request.GET.get('page')
    registros = paginator.get_page(page)

    return render(request, 'emergencias/lista_morbilidad_especialistas.html', {
        'registros': registros, 'query': query
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def crear_morbilidad_especialista_view(request):
    if request.method == 'POST':
        form = MorbilidadEspecialistaForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Morbilidad especialista: {registro.nombre_apellido}', request, 'emergencias'
            )
            messages.success(request, 'Registro de morbilidad creado.')
            return redirect('lista_morbilidad_especialistas')
    else:
        form = MorbilidadEspecialistaForm()
    return render(request, 'emergencias/form_morbilidad_especialista.html', {
        'form': form, 'titulo': 'Nuevo Registro Morbilidad Especialista'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def editar_morbilidad_especialista_view(request, pk):
    registro = get_object_or_404(MorbilidadEspecialista, pk=pk)
    if request.user.rol != 'ADMIN' and registro.usuario != request.user:
        return redirect('lista_morbilidad_especialistas')

    if request.method == 'POST':
        form = MorbilidadEspecialistaForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Morbilidad editada: {registro.nombre_apellido}', request, 'emergencias'
            )
            messages.success(request, 'Registro actualizado.')
            return redirect('lista_morbilidad_especialistas')
    else:
        form = MorbilidadEspecialistaForm(instance=registro)
    return render(request, 'emergencias/form_morbilidad_especialista.html', {
        'form': form, 'titulo': 'Editar Morbilidad Especialista'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def eliminar_morbilidad_especialista_view(request, pk):
    registro = get_object_or_404(MorbilidadEspecialista, pk=pk)
    
    # Refuerzo de Seguridad: Validar propiedad
    if request.user.rol != 'ADMIN' and registro.usuario != request.user:
        messages.error(request, 'No tiene permiso para archivar este registro.')
        return redirect('lista_morbilidad_especialistas')

    if request.method == 'POST':
        nombre = registro.nombre_apellido
        registro.activo = False
        registro.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Morbilidad especialista archivada: {nombre}', request, 'emergencias'
        )
        messages.success(request, f'Registro de "{nombre}" archivado exitosamente.')
        return redirect('lista_morbilidad_especialistas')
    return render(request, 'emergencias/eliminar.html', {'registro': registro})


# ═════════════════════════════════════════════
# CRUD PACIENTES NO ASISTIDOS
# ═════════════════════════════════════════════
@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_no_asistidos_view(request):
    query = request.GET.get('q', '')
    registros = PacienteNoAsistido.objects.filter(activo=True).select_related('usuario')

    if request.user.rol != 'ADMIN' or request.session.get('dashboard_vista') == 'personal':
        registros = registros.filter(usuario=request.user)

    if query:
        registros = registros.filter(
            Q(nombre_completo__icontains=query) |
            Q(especialidad__icontains=query)
        )

    paginator = Paginator(registros, 15)
    page = request.GET.get('page')
    registros = paginator.get_page(page)

    return render(request, 'emergencias/lista_no_asistidos.html', {
        'registros': registros, 'query': query
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def crear_no_asistido_view(request):
    if request.method == 'POST':
        form = PacienteNoAsistidoForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'No asistido: {registro.nombre_completo}', request, 'emergencias'
            )
            messages.success(request, 'Paciente no asistido registrado.')
            return redirect('lista_no_asistidos')
    else:
        form = PacienteNoAsistidoForm()
    return render(request, 'emergencias/form_no_asistido.html', {
        'form': form, 'titulo': 'Nuevo Paciente No Asistido'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def editar_no_asistido_view(request, pk):
    registro = get_object_or_404(PacienteNoAsistido, pk=pk)
    if request.user.rol != 'ADMIN' and registro.usuario != request.user:
        return redirect('lista_no_asistidos')

    if request.method == 'POST':
        form = PacienteNoAsistidoForm(request.POST, instance=registro)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'No asistido editado: {registro.nombre_completo}', request, 'emergencias'
            )
            messages.success(request, 'Registro actualizado.')
            return redirect('lista_no_asistidos')
    else:
        form = PacienteNoAsistidoForm(instance=registro)
    return render(request, 'emergencias/form_no_asistido.html', {
        'form': form, 'titulo': 'Editar Paciente No Asistido'
    })


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def eliminar_no_asistido_view(request, pk):
    registro = get_object_or_404(PacienteNoAsistido, pk=pk)
    
    # Refuerzo de Seguridad: Validar propiedad
    if request.user.rol != 'ADMIN' and registro.usuario != request.user:
        messages.error(request, 'No tiene permiso para archivar este registro.')
        return redirect('lista_no_asistidos')

    if request.method == 'POST':
        nombre = registro.nombre_completo
        registro.activo = False
        registro.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'No asistido archivado: {nombre}', request, 'emergencias'
        )
        messages.success(request, f'Registro de "{nombre}" archivado exitosamente.')
        return redirect('lista_no_asistidos')
    return render(request, 'emergencias/eliminar.html', {'registro': registro})


# ═════════════════════════════════════════════
# LIMPIAR (ARCHIVAR TODOS) - Soft Delete masivo
# ═════════════════════════════════════════════
@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def limpiar_emergencias_view(request):
    if request.method == 'POST':
        if request.user.rol == 'ADMIN':
            queryset = MorbilidadEmergencia.objects.filter(activo=True)
        else:
            queryset = MorbilidadEmergencia.objects.filter(activo=True, usuario=request.user)
        
        total = queryset.count()
        for reg in queryset:
            reg.activo = False
            reg.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Emergencias archivadas masivamente: {total} registros', request, 'emergencias'
        )
        messages.success(request, f'{total} registros de emergencia archivados exitosamente.')
    return redirect('lista_emergencias')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def limpiar_especialistas_view(request):
    if request.method == 'POST':
        if request.user.rol == 'ADMIN':
            queryset = MorbilidadEspecialista.objects.filter(activo=True)
        else:
            queryset = MorbilidadEspecialista.objects.filter(activo=True, usuario=request.user)
        
        total = queryset.count()
        for reg in queryset:
            reg.activo = False
            reg.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Morbilidades especialista archivadas masivamente: {total} registros', request, 'emergencias'
        )
        messages.success(request, f'{total} registros de especialistas archivados exitosamente.')
    return redirect('lista_morbilidad_especialistas')


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def limpiar_no_asistidos_view(request):
    if request.method == 'POST':
        if request.user.rol == 'ADMIN':
            queryset = PacienteNoAsistido.objects.filter(activo=True)
        else:
            queryset = PacienteNoAsistido.objects.filter(activo=True, usuario=request.user)
        
        total = queryset.count()
        for reg in queryset:
            reg.activo = False
            reg.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'No asistidos archivados masivamente: {total} registros', request, 'emergencias'
        )
        messages.success(request, f'{total} registros de no asistidos archivados exitosamente.')
    return redirect('lista_no_asistidos')
