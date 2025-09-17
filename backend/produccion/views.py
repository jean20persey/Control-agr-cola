from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import RegistroProduccion, PrediccionCosecha
from .serializers import (
    RegistroProduccionSerializer,
    RegistroProduccionCreateSerializer,
    RegistroProduccionListSerializer,
    PrediccionCosechaSerializer,
    PrediccionCreateSerializer,
    EstadisticasProduccionSerializer,
    SerieTemporalSerializer
)

class RegistroProduccionListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear registros de producción"""
    
    queryset = RegistroProduccion.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parcela', 'cultivo', 'temporada', 'calidad', 'anomalia_detectada']
    search_fields = ['parcela__codigo', 'cultivo__nombre', 'temporada']
    ordering_fields = ['fecha_registro', 'rendimiento_hectarea', 'cantidad_kg']
    ordering = ['-fecha_registro']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegistroProduccionCreateSerializer
        return RegistroProduccionListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros adicionales por fecha
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_registro__gte=fecha_inicio)
            except ValueError:
                pass
        
        if fecha_fin:
            try:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_registro__lte=fecha_fin)
            except ValueError:
                pass
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            registro = serializer.save()
            response_serializer = RegistroProduccionSerializer(registro)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistroProduccionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un registro específico"""
    
    queryset = RegistroProduccion.objects.all()
    serializer_class = RegistroProduccionSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def registros_anomalias_view(request):
    """Obtener registros con anomalías detectadas"""
    registros = RegistroProduccion.objects.filter(
        anomalia_detectada=True
    ).order_by('-fecha_registro')
    
    serializer = RegistroProduccionListSerializer(registros, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_temporada_view(request, temporada):
    """Obtener estadísticas de producción por temporada"""
    registros = RegistroProduccion.objects.filter(temporada=temporada)
    
    if not registros.exists():
        return Response({
            'error': 'No se encontraron registros para la temporada especificada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Calcular estadísticas
    stats = registros.aggregate(
        total_registros=Count('id'),
        produccion_total=Sum('cantidad_kg'),
        rendimiento_promedio=Avg('rendimiento_hectarea'),
        anomalias_detectadas=Count('id', filter=Q(anomalia_detectada=True))
    )
    
    # Porcentaje de anomalías
    porcentaje_anomalias = (stats['anomalias_detectadas'] / stats['total_registros']) * 100
    
    # Distribución por calidad
    calidades = registros.exclude(calidad__isnull=True).values('calidad').annotate(
        cantidad=Count('id')
    )
    distribucion_calidad = {item['calidad']: item['cantidad'] for item in calidades}
    
    # Top 5 parcelas por rendimiento
    top_parcelas = registros.values(
        'parcela__codigo', 'parcela__nombre'
    ).annotate(
        rendimiento_promedio=Avg('rendimiento_hectarea')
    ).order_by('-rendimiento_promedio')[:5]
    
    data = {
        'temporada': temporada,
        'total_registros': stats['total_registros'],
        'produccion_total': float(stats['produccion_total'] or 0),
        'rendimiento_promedio': float(stats['rendimiento_promedio'] or 0),
        'anomalias_detectadas': stats['anomalias_detectadas'],
        'porcentaje_anomalias': porcentaje_anomalias,
        'distribucion_calidad': distribucion_calidad,
        'top_parcelas': list(top_parcelas)
    }
    
    serializer = EstadisticasProduccionSerializer(data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def serie_temporal_parcela_view(request, parcela_id):
    """Obtener serie temporal de producción para una parcela"""
    limite = request.query_params.get('limite', 50)
    
    try:
        limite = int(limite)
    except ValueError:
        limite = 50
    
    registros = RegistroProduccion.objects.filter(
        parcela_id=parcela_id
    ).order_by('fecha_registro')[:limite]
    
    if not registros.exists():
        return Response({
            'error': 'No se encontraron registros para la parcela especificada'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Crear serie temporal
    serie_temporal = []
    for registro in registros:
        serie_temporal.append({
            'fecha': registro.fecha_registro,
            'rendimiento': registro.rendimiento_hectarea,
            'cantidad': registro.cantidad_kg,
            'temporada': registro.temporada,
            'anomalia': registro.anomalia_detectada,
            'temperatura': registro.temperatura_promedio,
            'precipitacion': registro.precipitacion_mm
        })
    
    serializer = SerieTemporalSerializer(serie_temporal, many=True)
    
    return Response({
        'parcela_id': parcela_id,
        'total_puntos': len(serie_temporal),
        'serie_temporal': serializer.data
    })

# Vistas para Predicciones
class PrediccionCosechaListView(generics.ListAPIView):
    """Vista para listar predicciones de cosecha"""
    
    queryset = PrediccionCosecha.objects.all()
    serializer_class = PrediccionCosechaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['parcela', 'cultivo', 'modelo_utilizado']
    ordering = ['-fecha_prediccion']

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_prediccion_view(request):
    """Crear predicción de cosecha usando modelos numéricos"""
    serializer = PrediccionCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    parcela_id = data['parcela_id']
    cultivo_id = data['cultivo_id']
    temporada_objetivo = data['temporada_objetivo']
    tipo_modelo = data['modelo']
    
    # Obtener datos históricos
    registros = RegistroProduccion.objects.filter(
        parcela_id=parcela_id,
        cultivo_id=cultivo_id
    ).order_by('fecha_registro')
    
    if registros.count() < 5:
        return Response({
            'error': 'Se necesitan al menos 5 registros históricos para crear predicciones'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Importar librerías de ML
        import pandas as pd
        import numpy as np
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
        
        # Preparar datos
        df = pd.DataFrame([{
            'dias_desde_inicio': (r.fecha_registro - registros.first().fecha_registro).days,
            'temperatura': r.temperatura_promedio or 20,
            'precipitacion': r.precipitacion_mm or 50,
            'humedad': r.humedad_relativa or 60,
            'rendimiento': r.rendimiento_hectarea
        } for r in registros])
        
        # Características y target
        X = df[['dias_desde_inicio', 'temperatura', 'precipitacion', 'humedad']].values
        y = df['rendimiento'].values
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        if tipo_modelo == 'random_forest':
            modelo = RandomForestRegressor(n_estimators=100, random_state=42)
        else:  # linear por defecto
            modelo = LinearRegression()
        
        modelo.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = modelo.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        # Hacer predicción
        temp_promedio = df['temperatura'].mean()
        precip_promedio = df['precipitacion'].mean()
        humedad_promedio = df['humedad'].mean()
        dias_futuros = df['dias_desde_inicio'].max() + 180
        
        X_prediccion = np.array([[dias_futuros, temp_promedio, precip_promedio, humedad_promedio]])
        rendimiento_predicho = modelo.predict(X_prediccion)[0]
        
        # Calcular intervalos de confianza
        error_estandar = rmse
        margen_error = 1.96 * error_estandar
        rango_minimo = max(0, rendimiento_predicho - margen_error)
        rango_maximo = rendimiento_predicho + margen_error
        
        # Guardar predicción
        from parcelas.models import Parcela
        from cultivos.models import Cultivo
        
        prediccion = PrediccionCosecha.objects.create(
            parcela_id=parcela_id,
            cultivo_id=cultivo_id,
            temporada_objetivo=temporada_objetivo,
            rendimiento_predicho=rendimiento_predicho,
            confianza_prediccion=r2,
            rango_minimo=rango_minimo,
            rango_maximo=rango_maximo,
            modelo_utilizado=tipo_modelo,
            parametros_modelo={
                'r2_score': float(r2),
                'rmse': float(rmse),
                'registros_entrenamiento': len(registros),
                'condiciones_promedio': {
                    'temperatura': float(temp_promedio),
                    'precipitacion': float(precip_promedio),
                    'humedad': float(humedad_promedio)
                }
            }
        )
        
        serializer_response = PrediccionCosechaSerializer(prediccion)
        return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        
    except ImportError:
        return Response({
            'error': 'Librerías de machine learning no disponibles'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'Error al crear predicción: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validar_prediccion_view(request, prediccion_id):
    """Validar predicción con resultado real"""
    try:
        prediccion = PrediccionCosecha.objects.get(id=prediccion_id)
        rendimiento_real = request.data.get('rendimiento_real')
        
        if not rendimiento_real:
            return Response({
                'error': 'Se requiere el rendimiento real'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        prediccion.rendimiento_real = float(rendimiento_real)
        precision = prediccion.calcular_precision()
        
        serializer = PrediccionCosechaSerializer(prediccion)
        return Response({
            'message': 'Predicción validada correctamente',
            'precision': precision,
            'prediccion': serializer.data
        })
        
    except PrediccionCosecha.DoesNotExist:
        return Response({
            'error': 'Predicción no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({
            'error': 'Rendimiento real debe ser un número válido'
        }, status=status.HTTP_400_BAD_REQUEST)
