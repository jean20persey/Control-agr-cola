from django.urls import path
from .views import (
    RegistroProduccionListCreateView,
    RegistroProduccionDetailView,
    registros_anomalias_view,
    estadisticas_temporada_view,
    serie_temporal_parcela_view,
    PrediccionCosechaListView,
    crear_prediccion_view,
    validar_prediccion_view
)

urlpatterns = [
    # CRUD de registros de producción
    path('registros/', RegistroProduccionListCreateView.as_view(), name='registro-produccion-list-create'),
    path('registros/<int:pk>/', RegistroProduccionDetailView.as_view(), name='registro-produccion-detail'),
    
    # Análisis de anomalías
    path('registros/anomalias/', registros_anomalias_view, name='registros-anomalias'),
    
    # Estadísticas y análisis
    path('estadisticas/temporada/<str:temporada>/', estadisticas_temporada_view, name='estadisticas-temporada'),
    path('series-temporales/parcela/<int:parcela_id>/', serie_temporal_parcela_view, name='serie-temporal-parcela'),
    
    # Predicciones de cosecha
    path('predicciones/', PrediccionCosechaListView.as_view(), name='predicciones-list'),
    path('predicciones/crear/', crear_prediccion_view, name='crear-prediccion'),
    path('predicciones/<int:prediccion_id>/validar/', validar_prediccion_view, name='validar-prediccion'),
]
