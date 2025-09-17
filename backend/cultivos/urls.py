from django.urls import path
from .views import (
    CultivoListCreateView,
    CultivoDetailView,
    cultivos_tipos_view,
    cultivos_stats_view,
    cultivos_por_tipo_view,
    cultivo_activar_view,
    cultivos_buscar_view
)

urlpatterns = [
    # CRUD básico
    path('', CultivoListCreateView.as_view(), name='cultivo-list-create'),
    path('<int:pk>/', CultivoDetailView.as_view(), name='cultivo-detail'),
    
    # Endpoints adicionales
    path('tipos/', cultivos_tipos_view, name='cultivos-tipos'),
    path('stats/', cultivos_stats_view, name='cultivos-stats'),
    path('distribucion/', cultivos_por_tipo_view, name='cultivos-por-tipo'),
    path('<int:pk>/activar/', cultivo_activar_view, name='cultivo-activar'),
    path('buscar/', cultivos_buscar_view, name='cultivos-buscar'),
]
