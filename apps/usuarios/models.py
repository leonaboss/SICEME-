"""
SICEME - Modelos de Usuarios
Incluye: Usuario personalizado, BitácoraAuditoría
"""
import pyotp
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


class Usuario(AbstractUser):
    """Modelo de usuario personalizado con soporte RBAC, 2FA y bloqueo"""

    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        ESPECIALISTA = 'ESPECIALISTA', 'Especialista'
        PUBLICO = 'PUBLICO', 'Público'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.PUBLICO,
        verbose_name='Rol'
    )
    is_locked = models.BooleanField(
        default=False,
        verbose_name='Cuenta bloqueada'
    )
    failed_attempts = models.IntegerField(
        default=0,
        verbose_name='Intentos fallidos'
    )
    otp_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name='Código OTP'
    )
    otp_expiry = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expiración OTP'
    )
    otp_secret = models.CharField(
        max_length=32,
        blank=True,
        default='',
        verbose_name='Secreto OTP'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        default='',
        verbose_name='Teléfono'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Cuenta verificada (2FA)'
    )
    imagen_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True,
        verbose_name='Imagen de perfil'
    )


    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN

    @property
    def es_especialista(self):
        return self.rol == self.Rol.ESPECIALISTA

    @property
    def es_publico(self):
        return self.rol == self.Rol.PUBLICO

    def generar_otp(self):
        """Genera un código OTP de 6 dígitos y lo guarda"""
        import random
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timedelta(
            minutes=getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
        )
        self.save(update_fields=['otp_code', 'otp_expiry'])
        return self.otp_code

    def verificar_otp(self, codigo):
        """Verifica el código OTP ingresado"""
        if (self.otp_code and
                self.otp_code == codigo and
                self.otp_expiry and
                timezone.now() <= self.otp_expiry):
            self.otp_code = None
            self.otp_expiry = None
            self.save(update_fields=['otp_code', 'otp_expiry'])
            return True
        return False

    def registrar_intento_fallido(self):
        """Incrementa intentos fallidos y bloquea si supera el máximo"""
        self.failed_attempts += 1
        max_attempts = getattr(settings, 'ACCOUNT_MAX_LOGIN_ATTEMPTS', 3)
        if self.failed_attempts >= max_attempts:
            self.is_locked = True
        self.save(update_fields=['failed_attempts', 'is_locked'])

    def resetear_intentos(self):
        """Resetea el contador de intentos fallidos"""
        self.failed_attempts = 0
        self.save(update_fields=['failed_attempts'])

    def desbloquear(self):
        """Desbloquea la cuenta del usuario"""
        self.is_locked = False
        self.failed_attempts = 0
        self.save(update_fields=['is_locked', 'failed_attempts'])


class BitacoraAuditoria(models.Model):
    """Registro inmutable de acciones del sistema"""

    class Accion(models.TextChoices):
        LOGIN = 'LOGIN', 'Inicio de sesión'
        LOGOUT = 'LOGOUT', 'Cierre de sesión'
        LOGIN_FALLIDO = 'LOGIN_FALLIDO', 'Intento de login fallido'
        CUENTA_BLOQUEADA = 'CUENTA_BLOQUEADA', 'Cuenta bloqueada'
        CUENTA_DESBLOQUEADA = 'CUENTA_DESBLOQUEADA', 'Cuenta desbloqueada'
        CREAR = 'CREAR', 'Creación de registro'
        EDITAR = 'EDITAR', 'Edición de registro'
        ELIMINAR = 'ELIMINAR', 'Eliminación de registro'
        ACCESO_DENEGADO = 'ACCESO_DENEGADO', 'Acceso denegado'
        CAMBIO_PASSWORD = 'CAMBIO_PASSWORD', 'Cambio de contraseña'
        VERIFICACION_2FA = 'VERIFICACION_2FA', 'Verificación 2FA'
        EXPORTAR = 'EXPORTAR', 'Exportación de datos'

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bitacora',
        verbose_name='Usuario'
    )
    accion = models.CharField(
        max_length=30,
        choices=Accion.choices,
        verbose_name='Acción'
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name='Descripción'
    )
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora'
    )
    direccion_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    modulo = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Módulo'
    )
    user_agent = models.TextField(
        blank=True,
        default='',
        verbose_name='User Agent'
    )

    class Meta:
        db_table = 'bitacora_auditoria'
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Bitácora de Auditoría'
        ordering = ['-fecha_hora']
        # Inmutable: no se permite edición
        managed = True

    def __str__(self):
        return f"[{self.fecha_hora}] {self.usuario} - {self.get_accion_display()}"

    @classmethod
    def registrar(cls, usuario, accion, descripcion='', request=None, modulo=''):
        """Método helper para registrar una acción en la bitácora"""
        ip = None
        user_agent = ''
        if request:
            ip = cls.obtener_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            descripcion=descripcion,
            direccion_ip=ip,
            modulo=modulo,
            user_agent=user_agent
        )

    @staticmethod
    def obtener_ip(request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

# Fin de archivo (Actualización forzada para el editor)
