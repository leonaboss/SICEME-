"""
SICEME - Vistas de Usuarios
Login, Logout, Registro, 2FA, RBAC, Gestión de usuarios
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Usuario, BitacoraAuditoria
from .forms import (
    LoginForm, OTPForm, RegistroUsuarioForm, AdminRegistroUsuarioForm, EditarUsuarioForm,
    CambiarPasswordForm, ReautenticarForm, RecuperarPasswordForm,
    NuevoPasswordForm, PerfilUsuarioForm
)
from .decorators import rol_requerido

logger = logging.getLogger('siceme')


# ─────────────────────────────────────────────
# LOGIN (Directo, el 2FA ahora es al registro/reset)
# ─────────────────────────────────────────────
def login_view(request):
    """Vista de inicio de sesión directa"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                usuario = Usuario.objects.get(username=username)
            except Usuario.DoesNotExist:
                messages.error(request, 'Credenciales incorrectas.')
                BitacoraAuditoria.registrar(
                    None, BitacoraAuditoria.Accion.LOGIN_FALLIDO,
                    f'Usuario no encontrado: {username}', request, 'usuarios'
                )
                return render(request, 'usuarios/login.html', {'form': form})

            # Verificar si está bloqueado
            if usuario.is_locked:
                messages.error(
                    request,
                    'Su cuenta está bloqueada. Contacte al administrador.'
                )
                return render(request, 'usuarios/login.html', {'form': form})

            # Autenticar
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user.resetear_intentos()
                BitacoraAuditoria.registrar(
                    user, BitacoraAuditoria.Accion.LOGIN,
                    'Login exitoso', request, 'usuarios'
                )
                messages.success(request, f'Bienvenido/a, {user.get_full_name() or user.username}.')
                return redirect('dashboard')
            else:
                # Intentos fallidos
                usuario.registrar_intento_fallido()
                remaining = settings.ACCOUNT_MAX_LOGIN_ATTEMPTS - usuario.failed_attempts

                if usuario.is_locked:
                    BitacoraAuditoria.registrar(
                        usuario, BitacoraAuditoria.Accion.CUENTA_BLOQUEADA,
                        'Cuenta bloqueada por intentos fallidos', request, 'usuarios'
                    )
                    messages.error(
                        request,
                        'Su cuenta ha sido bloqueada por múltiples intentos fallidos. Contacte al administrador.'
                    )
                else:
                    BitacoraAuditoria.registrar(
                        usuario, BitacoraAuditoria.Accion.LOGIN_FALLIDO,
                        f'Intento fallido #{usuario.failed_attempts}', request, 'usuarios'
                    )
                    messages.error(
                        request,
                        f'Credenciales incorrectas. Le quedan {remaining} intento(s).'
                    )
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})


def registro_publico_view(request):
    """Vista de registro público con verificación 2FA inmediata"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # El rol ya fue validado en el formulario (con el código secreto si es ADMIN)
            user.is_verified = False # Obligatorio verificar por OTP
            user.save()
            
            # Generar y enviar OTP inmediatamente
            otp_code = user.generar_otp()
            try:
                send_mail(
                    'SICEME - Código de Verificación',
                    f'Hola {user.username},\n\n'
                    f'Tu código de verificación es: {otp_code}\n'
                    f'Ingresa este código para activar tu cuenta. Expira en {settings.OTP_EXPIRY_MINUTES} minutos.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                logger.info(f'OTP enviado a {user.email} para el usuario {user.username}')
                BitacoraAuditoria.registrar(
                    user, BitacoraAuditoria.Accion.CREAR,
                    f'Registro: {user.username}. OTP enviado.', request, 'usuarios'
                )
                request.session['pre_otp_user_id'] = user.pk
                request.session['pre_otp_username'] = user.username
                messages.success(request, f'Código de verificación enviado a {user.email}.')
                return redirect('verificar_otp')
            except Exception as e:
                logger.error(f'Error crítico enviando email a {user.email}: {e}')
                messages.warning(request, 'Cuenta creada, pero no pudimos enviarte el código. Por favor, solicita un reenvío o contacta al administrador.')
                return redirect('login')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'usuarios/registro_publico.html', {'form': form})


def verificar_otp_view(request):
    """Vista para verificar código OTP tras el registro"""
    user_id = request.session.get('pre_otp_user_id')
    if not user_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['otp_code']
            if usuario.verificar_otp(codigo):
                usuario.is_verified = True
                usuario.save(update_fields=['is_verified'])
                
                # Login automático tras verificar
                login(request, usuario)
                usuario.resetear_intentos()

                BitacoraAuditoria.registrar(
                    usuario, BitacoraAuditoria.Accion.VERIFICACION_2FA,
                    'Verificación de registro exitosa', request, 'usuarios'
                )

                del request.session['pre_otp_user_id']
                del request.session['pre_otp_username']

                messages.success(request, f'¡Cuenta verificada! Bienvenido/a, {usuario.username}.')
                return redirect('dashboard')
            else:
                messages.error(request, 'Código inválido o expirado.')
    else:
        form = OTPForm()

    return render(request, 'usuarios/verificar_otp.html', {
        'form': form,
        'username': request.session.get('pre_otp_username', '')
    })


def reenviar_otp_view(request):
    """Reenvía el código OTP al correo del usuario"""
    user_id = request.session.get('pre_otp_user_id')
    if not user_id:
        return redirect('login')

    try:
        usuario = Usuario.objects.get(pk=user_id)
        otp_code = usuario.generar_otp()
        send_mail(
            'SICEME - Nuevo Código de Verificación',
            f'Su nuevo código de verificación es: {otp_code}\n\n'
            f'Este código expira en {settings.OTP_EXPIRY_MINUTES} minutos.',
            settings.DEFAULT_FROM_EMAIL,
            [usuario.email],
            fail_silently=True,
        )
        logger.info(f'OTP reenviado para {usuario.username}: {otp_code}')
        messages.success(request, 'Se ha enviado un nuevo código de verificación.')
    except Exception as e:
        logger.error(f'Error reenviando OTP: {e}')
        messages.error(request, 'Error al reenviar el código.')

    return redirect('verificar_otp')


# ─────────────────────────────────────────────
# ACTIVAR / DESACTIVAR USUARIO
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def toggle_estado_usuario_view(request, pk):
    """Activa o desactiva (is_active) a un usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Evitar que el administrador se desactive a sí mismo
    if usuario == request.user:
        messages.warning(request, 'No puedes desactivar tu propia cuenta actual.')
        return redirect('lista_usuarios')

    if request.method == 'POST':
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
        
        estado_texto = "activado" if usuario.is_active else "desactivado"
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.EDITAR,
            f'Usuario {estado_texto}: {usuario.username}', request, 'usuarios'
        )
        messages.success(request, f'La cuenta de "{usuario.username}" ha sido {estado_texto}.')
        
    return redirect('lista_usuarios')


# ─────────────────────────────────────────────
# PROMOVER USUARIO A ADMIN
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def promover_admin_usuario_view(request, pk):
    """Cambia el rol de un usuario a ADMIN de forma rápida"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        if usuario.rol == 'ADMIN':
            messages.info(request, f'El usuario "{usuario.username}" ya tiene rol de Administrador.')
        else:
            usuario.rol = 'ADMIN'
            usuario.save(update_fields=['rol'])
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Usuario promovido a Administrador: {usuario.username}', request, 'usuarios'
            )
            messages.success(request, f'"{usuario.username}" ahora es Administrador del sistema.')
            
    return redirect('lista_usuarios')

@login_required
def logout_view(request):
    """Cierre de sesión con registro en bitácora"""
    BitacoraAuditoria.registrar(
        request.user, BitacoraAuditoria.Accion.LOGOUT,
        'Cierre de sesión', request, 'usuarios'
    )
    logout(request)
    messages.info(request, 'Ha cerrado sesión correctamente.')
    return redirect('login')


# ─────────────────────────────────────────────
# REGISTRO (Solo Admin)
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def registro_view(request):
    """Registro de nuevos usuarios (solo admin)"""
    if request.method == 'POST':
        form = AdminRegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_verified = False # También requiere verificación para mayor seguridad
            usuario.save()
            
            # Generar y enviar OTP al nuevo usuario
            otp_code = usuario.generar_otp()
            try:
                send_mail(
                    'SICEME - Código de Activación de Cuenta',
                    f'Hola {usuario.username},\n\n'
                    f'Un administrador ha creado tu cuenta en SICEME.\n'
                    f'Tu código de activación es: {otp_code}\n'
                    f'Usa este código para verificar tu cuenta al iniciar sesión.',
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.email],
                    fail_silently=False,
                )
                messages.success(request, f'Usuario "{usuario.username}" creado. Se envió un código a {usuario.email}.')
            except Exception as e:
                logger.error(f'Error enviando email en registro admin: {e}')
                messages.warning(request, f'Usuario creado, pero no se pudo enviar el correo a {usuario.email}.')
            
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CREAR,
                f'Usuario creado por admin: {usuario.username}',
                request, 'usuarios'
            )
            return redirect('lista_usuarios')
    else:
        form = AdminRegistroUsuarioForm()

    return render(request, 'usuarios/registro.html', {'form': form})


# ─────────────────────────────────────────────
# CRUD USUARIOS (Solo Admin)
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def lista_usuarios_view(request):
    """Listado de todos los usuarios"""
    query = request.GET.get('q', '')
    usuarios = Usuario.objects.all()

    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    paginator = Paginator(usuarios, 15)
    page = request.GET.get('page')
    usuarios = paginator.get_page(page)

    return render(request, 'usuarios/lista.html', {
        'usuarios': usuarios,
        'query': query
    })


@login_required
@rol_requerido('ADMIN')
def editar_usuario_view(request, pk):
    """Editar un usuario existente"""
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                f'Usuario editado: {usuario.username}', request, 'usuarios'
            )
            messages.success(request, f'Usuario "{usuario.username}" actualizado.')
            return redirect('lista_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar.html', {
        'form': form,
        'usuario_editado': usuario
    })


@login_required
@rol_requerido('ADMIN')
def eliminar_usuario_view(request, pk):
    """Eliminar un usuario con reautenticación"""
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = ReautenticarForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            # Verificar contraseña del admin actual
            if request.user.check_password(password):
                username = usuario.username
                BitacoraAuditoria.registrar(
                    request.user, BitacoraAuditoria.Accion.ELIMINAR,
                    f'Usuario eliminado: {username}', request, 'usuarios'
                )
                usuario.delete()
                messages.success(request, f'Usuario "{username}" eliminado correctamente.')
                return redirect('lista_usuarios')
            else:
                messages.error(request, 'Contraseña incorrecta. No se pudo eliminar el usuario.')
    else:
        form = ReautenticarForm()

    return render(request, 'usuarios/eliminar.html', {
        'form': form,
        'usuario_editado': usuario
    })


# ─────────────────────────────────────────────
# BLOQUEO / DESBLOQUEO
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def desbloquear_usuario_view(request, pk):
    """Desbloquear cuenta de un usuario (solo admin)"""
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        usuario.desbloquear()
        BitacoraAuditoria.registrar(
            request.user, BitacoraAuditoria.Accion.CUENTA_DESBLOQUEADA,
            f'Cuenta desbloqueada: {usuario.username}', request, 'usuarios'
        )
        messages.success(request, f'Cuenta de "{usuario.username}" desbloqueada.')

    return redirect('lista_usuarios')


# ─────────────────────────────────────────────
# CAMBIO DE CONTRASEÑA
# ─────────────────────────────────────────────
@login_required
def cambiar_password_view(request):
    """Cambio de contraseña del usuario actual"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.CAMBIO_PASSWORD,
                'Contraseña cambiada', request, 'usuarios'
            )
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('dashboard')
    else:
        form = CambiarPasswordForm(request.user)

    return render(request, 'usuarios/cambiar_password.html', {'form': form})


# ─────────────────────────────────────────────
# PERFIL
# ─────────────────────────────────────────────
@login_required
def perfil_view(request):
    """Vista del perfil del usuario actual (Edición)"""
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=request.user)
        
        # Lógica para eliminar foto
        if 'eliminar_foto' in request.POST and request.POST['eliminar_foto'] == '1':
            if request.user.imagen_perfil:
                request.user.imagen_perfil.delete(save=False)
                request.user.save(update_fields=['imagen_perfil'])
                BitacoraAuditoria.registrar(
                    request.user, BitacoraAuditoria.Accion.EDITAR,
                    'Eliminación de foto de perfil', request, 'usuarios'
                )
                messages.success(request, 'Tu foto de perfil ha sido eliminada.')
                return redirect('perfil')

        if form.is_valid():

            form.save()
            BitacoraAuditoria.registrar(
                request.user, BitacoraAuditoria.Accion.EDITAR,
                'Actualización de perfil personal', request, 'usuarios'
            )
            messages.success(request, 'Tu perfil ha sido actualizado correctamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor corrige los errores del formulario.')
    else:
        form = PerfilUsuarioForm(instance=request.user)

    return render(request, 'usuarios/perfil.html', {'form': form})


# ─────────────────────────────────────────────
# BITÁCORA DE AUDITORÍA
# ─────────────────────────────────────────────
@login_required
@rol_requerido('ADMIN')
def bitacora_view(request):
    """Vista de la bitácora de auditoría"""
    registros = BitacoraAuditoria.objects.select_related('usuario').all()

    # Filtros
    usuario_id = request.GET.get('usuario')
    accion = request.GET.get('accion')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    busqueda = request.GET.get('q')

    if busqueda:
        from django.db.models import Q
        registros = registros.filter(
            Q(descripcion__icontains=busqueda) |
            Q(usuario__username__icontains=busqueda) |
            Q(modulo__icontains=busqueda) |
            Q(direccion_ip__icontains=busqueda)
        )

    if usuario_id:
        registros = registros.filter(usuario_id=usuario_id)
    if accion:
        registros = registros.filter(accion=accion)
    if fecha_desde:
        registros = registros.filter(fecha_hora__date__gte=fecha_desde)
    if fecha_hasta:
        registros = registros.filter(fecha_hora__date__lte=fecha_hasta)

    paginator = Paginator(registros, 25)
    page = request.GET.get('page')
    registros = paginator.get_page(page)

    usuarios = Usuario.objects.all().order_by('username')
    acciones = BitacoraAuditoria.Accion.choices

    return render(request, 'usuarios/bitacora.html', {
        'registros': registros,
        'usuarios_lista': usuarios,
        'acciones': acciones,
        'filtros': {
            'usuario': usuario_id or '',
            'accion': accion or '',
            'fecha_desde': fecha_desde or '',
            'fecha_hasta': fecha_hasta or '',
            'q': busqueda or '',
        }
    })


# ─────────────────────────────────────────────
# RECUPERACIÓN DE CONTRASEÑA POR OTP
# ─────────────────────────────────────────────

def password_reset_request_view(request):
    """Paso 1: Solicitar reset y enviar OTP"""
    if request.method == 'POST':
        form = RecuperarPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                # Usamos filter().first() por si hay correos duplicados accidentalmente
                user = Usuario.objects.filter(email=email).first()
                
                if user:
                    otp_code = user.generar_otp()
                    
                    # Asegurar un remitente válido para Gmail
                    remitente = settings.DEFAULT_FROM_EMAIL
                    if 'noreply@siceme.com' in remitente or not remitente:
                        remitente = settings.EMAIL_HOST_USER
                    
                    send_mail(
                        'SICEME - Código de Recuperación',
                        f'Has solicitado restablecer tu contraseña.\n'
                        f'Tu código de verificación es: {otp_code}\n'
                        f'Este código expira en {settings.OTP_EXPIRY_MINUTES} minutos.',
                        remitente,
                        [email],
                        fail_silently=False,
                    )
                    
                    request.session['reset_otp_user_id'] = user.pk
                    messages.info(request, f'Se ha enviado un código a {email}.')
                    return redirect('password_reset_otp')
                else:
                    # El correo no existe en la base de datos
                    messages.info(request, 'Si el correo está registrado, recibirás un código.')
                    return redirect('login')
                    
            except Exception as e:
                # Logueamos el error exacto para que el usuario pueda verlo en consola
                logger.error(f'Error detallado enviando email de reset: {e}')
                print(f"DEBUG ERROR SMTP: {e}") # Para que lo vea en la terminal negra
                messages.error(request, f'Error al enviar el código: {str(e)[:50]}...')
    else:
        form = RecuperarPasswordForm()
    
    return render(request, 'usuarios/password_reset.html', {'form': form})


def password_reset_otp_view(request):
    """Paso 2: Verificar OTP para el reset"""
    user_id = request.session.get('reset_otp_user_id')
    if not user_id:
        return redirect('password_reset')

    try:
        user = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        return redirect('password_reset')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['otp_code']
            if user.verificar_otp(codigo):
                request.session['otp_verified_for_reset'] = True
                return redirect('password_reset_change')
            else:
                messages.error(request, 'Código inválido o expirado.')
    else:
        form = OTPForm()

    return render(request, 'usuarios/verificar_otp.html', {
        'form': form,
        'username': user.email,
        'reset_mode': True # Para ajustar textos en el template
    })


def password_reset_change_view(request):
    """Paso 3: Establecer nueva contraseña"""
    user_id = request.session.get('reset_otp_user_id')
    verified = request.session.get('otp_verified_for_reset')

    if not user_id or not verified:
        return redirect('password_reset')

    try:
        user = Usuario.objects.get(pk=user_id)
    except Usuario.DoesNotExist:
        return redirect('password_reset')

    if request.method == 'POST':
        form = NuevoPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            
            # Limpiar sesión
            del request.session['reset_otp_user_id']
            del request.session['otp_verified_for_reset']
            
            BitacoraAuditoria.registrar(
                user, BitacoraAuditoria.Accion.CAMBIO_PASSWORD,
                'Reset de contraseña exitoso por OTP', request, 'usuarios'
            )
            messages.success(request, 'Tu contraseña ha sido actualizada. Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = NuevoPasswordForm(user)

    return render(request, 'usuarios/password_reset_confirm.html', {'form': form})
