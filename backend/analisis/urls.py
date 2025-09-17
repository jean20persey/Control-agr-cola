from django.urls import path
from .views import (
    estadisticas_generales_view,
    comparar_variedades_view,
    clasificar_por_rendimiento_view,
    analizar_serie_temporal_view,
    AnalisisComparativoListView,
    ClasificacionRendimientoListView,
    AnalisisSeriesTemporalListView
)

urlpatterns = [
    # Estadísticas generales
    path('estadisticas-generales/', estadisticas_generales_view, name='estadisticas-generales'),
    
    # Análisis comparativos
    path('comparar-variedades/', comparar_variedades_view, name='comparar-variedades'),
    path('analisis-comparativos/', AnalisisComparativoListView.as_view(), name='analisis-comparativos-list'),
    
    # Clasificación por rendimiento
    path('clasificar-rendimiento/', clasificar_por_rendimiento_view, name='clasificar-rendimiento'),
    path('clasificaciones/', ClasificacionRendimientoListView.as_view(), name='clasificaciones-list'),
    
    # Análisis de series temporales
    path('analizar-serie-temporal/', analizar_serie_temporal_view, name='analizar-serie-temporal'),
    path('series-temporales/', AnalisisSeriesTemporalListView.as_view(), name='series-temporales-list'),
]
