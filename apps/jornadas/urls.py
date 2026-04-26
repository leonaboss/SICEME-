"""SICEME - URLs de Jornadas"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_jornadas_view, name='lista_jornadas'),
    path('entrada/', views.registrar_entrada_view, name='registrar_entrada'),
    path('salida/<int:pk>/', views.registrar_salida_view, name='registrar_salida'),
    path('pausa-inicio/<int:pk>/', views.registrar_pausa_inicio_view, name='registrar_pausa_inicio'),
    path('pausa-fin/<int:pk>/', views.registrar_pausa_fin_view, name='registrar_pausa_fin'),
]
