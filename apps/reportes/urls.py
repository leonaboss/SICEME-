"""SICEME - URLs de Reportes y Dashboard"""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='home'),
    path('menu/', views.dashboard_view, name='dashboard'),

    # API endpoints para gráficos
    path('api/dashboard-data/', views.api_dashboard_data, name='api_dashboard_data'),
    path('api/estadisticas-especialidad/', views.api_estadisticas_especialidad, name='api_estadisticas_especialidad'),

    # Reportes
    path('reportes/especialidades/', views.reporte_especialidades_view, name='reporte_especialidades'),
    path('reportes/emergencias-mes/', views.reporte_emergencias_mes_view, name='reporte_emergencias_mes'),
    path('reportes/ecosonogramas-enfermedades/', views.reporte_ecosonogramas_enfermedades_view, name='reporte_ecosonogramas_enfermedades'),
    path('reportes/no-asistidos/', views.reporte_no_asistidos_view, name='reporte_no_asistidos'),
    path('reportes/top-medicos/', views.reporte_top_medicos_view, name='reporte_top_medicos'),
    path('reportes/periodo/', views.reporte_periodo_view, name='reporte_periodo'),
    path('reportes/periodo/exportar/', views.exportar_reporte_periodo_excel_view, name='exportar_reporte_periodo'),

    # Exportación / Importación
    path('reportes/exportar-excel/', views.exportar_excel_view, name='exportar_excel'),
    path('reportes/importar-excel/', views.importar_excel_view, name='importar_excel'),

    # Movimientos y Monitoreo
    path('movimientos/', views.movimientos_view, name='movimientos'),
    path('monitor/', views.monitor_view, name='monitor'),
    path('movimientos/restaurar/', views.restaurar_registro_view, name='restaurar_registro'),
    path('movimientos/limpiar-actividad/', views.limpiar_actividad_global_view, name='limpiar_actividad_global'),
    path('movimientos/restaurar-masivo/', views.restaurar_masivo_view, name='restaurar_masivo'),

    # Biblioteca Histórica (Admin)
    path('biblioteca/', views.biblioteca_view, name='biblioteca'),
    path('biblioteca/cerrar-mes/', views.cerrar_mes_view, name='cerrar_mes'),
    path('biblioteca/auto-organizar-todo/', views.auto_organizar_biblioteca_view, name='auto_organizar_biblioteca'),
]
