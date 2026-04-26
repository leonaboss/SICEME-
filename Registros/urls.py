"""SICEME URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('apps.usuarios.urls')),
    path('especialistas/', include('apps.especialistas.urls')),
    path('emergencias/', include('apps.emergencias.urls')),
    path('ecosonogramas/', include('apps.ecosonogramas.urls')),
    path('jornadas/', include('apps.jornadas.urls')),
    path('reportes/', include('apps.reportes.urls')),
    path('', include('apps.reportes.urls')),  # Dashboard como página principal
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
