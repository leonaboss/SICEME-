"""SICEME - URLs de Ecosonogramas"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_ecosonogramas_view, name='lista_ecosonogramas'),
    path('crear/', views.crear_ecosonograma_view, name='crear_ecosonograma'),
    path('editar/<int:pk>/', views.editar_ecosonograma_view, name='editar_ecosonograma'),
    path('eliminar/<int:pk>/', views.eliminar_ecosonograma_view, name='eliminar_ecosonograma'),
    path('limpiar/', views.limpiar_ecosonogramas_view, name='limpiar_ecosonogramas'),
]
