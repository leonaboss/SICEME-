"""SICEME - Vistas de Ecosonogramas"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from apps.usuarios.decorators import rol_requerido
from apps.usuarios.models import BitacoraAuditoria
from .models import MorbilidadEcosonograma
from .forms import EcosonogramaForm


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def lista_ecosonogramas_view(request):
    query = request.GET.get('q', '')
    registros = MorbilidadEcosonograma.objects.filter(activo=True).select_related('usuario')
    if request.user.rol != 'ADMIN' or request.session.get('dashboard_vista') == 'personal':
        registros = registros.filter(usuario=request.user)
    if query:
        registros = registros.filter(
            Q(nombre_apellido__icontains=query) | Q(cedula__icontains=query) | Q(tipo_eco__icontains=query)
        )
    paginator = Paginator(registros, 15)
    page = request.GET.get('page')
    registros = paginator.get_page(page)
    return render(request, 'ecosonogramas/lista.html', {'registros': registros, 'query': query})


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def crear_ecosonograma_view(request):
    if request.method == 'POST':
        form = EcosonogramaForm(request.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.usuario = request.user
            reg.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Ecosonograma: {reg.nombre_apellido}', request, 'ecosonogramas'
            )
            messages.success(request, 'Ecosonograma registrado.')
            return redirect('lista_ecosonogramas')
    else:
        form = EcosonogramaForm()
    return render(request, 'ecosonogramas/form.html', {'form': form, 'titulo': 'Nuevo Ecosonograma'})


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def editar_ecosonograma_view(request, pk):
    reg = get_object_or_404(MorbilidadEcosonograma, pk=pk)
    if request.user.rol != 'ADMIN' and reg.usuario != request.user:
        return redirect('lista_ecosonogramas')
    if request.method == 'POST':
        form = EcosonogramaForm(request.POST, instance=reg)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Ecosonograma editado: {reg.nombre_apellido}', request, 'ecosonogramas'
            )
            messages.success(request, 'Registro actualizado.')
            return redirect('lista_ecosonogramas')
    else:
        form = EcosonogramaForm(instance=reg)
    return render(request, 'ecosonogramas/form.html', {'form': form, 'titulo': 'Editar Ecosonograma'})


@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA', 'PUBLICO')
def eliminar_ecosonograma_view(request, pk):
    reg = get_object_or_404(MorbilidadEcosonograma, pk=pk)
    
    # Refuerzo de Seguridad: Validar propiedad
    if request.user.rol != 'ADMIN' and reg.usuario != request.user:
        messages.error(request, 'No tiene permiso para archivar este registro.')
        return redirect('lista_ecosonogramas')

    if request.method == 'POST':
        nombre = reg.nombre_apellido
        reg.activo = False
        reg.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Ecosonograma archivado: {nombre}', request, 'ecosonogramas'
        )
        messages.success(request, f'Registro de "{nombre}" archivado exitosamente.')
        return redirect('lista_ecosonogramas')
    return render(request, 'ecosonogramas/eliminar.html', {'registro': reg})


# ═════════════════════════════════════════════
# LIMPIAR (ARCHIVAR TODOS)
# ═════════════════════════════════════════════
@login_required
@rol_requerido('ADMIN', 'ESPECIALISTA')
def limpiar_ecosonogramas_view(request):
    if request.method == 'POST':
        if request.user.rol == 'ADMIN':
            queryset = MorbilidadEcosonograma.objects.filter(activo=True)
        else:
            queryset = MorbilidadEcosonograma.objects.filter(activo=True, usuario=request.user)
        
        total = queryset.count()
        for reg in queryset:
            reg.activo = False
            reg.save()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.ELIMINAR,
            f'Ecosonogramas archivados masivamente: {total} registros', request, 'ecosonogramas'
        )
        messages.success(request, f'{total} ecosonogramas archivados exitosamente.')
    return redirect('lista_ecosonogramas')
