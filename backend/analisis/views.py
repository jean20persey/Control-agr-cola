from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import datetime
import json

from .models import AnalisisComparativo, ClasificacionRendimiento, AnalisisSeriesTemporal
from .serializers import (
    AnalisisComparativoSerializer,
    ComparacionVariedadesSerializer,
    ClasificacionRendimientoSerializer,
    ClasificarPorRendimientoSerializer,
    AnalisisSeriesTemporalSerializer,
    AnalizarSerieTemporalSerializer,
    EstadisticasGeneralesSerializer
)
from produccion.models import RegistroProduccion
from cultivos.models import Cultivo
from parcelas.models import Parcela

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_generales_view(request):
    """Obtener estadísticas generales del sistema"""
    
    # Estadísticas básicas
    total_registros = RegistroProduccion.objects.count()
    total_parcelas = Parcela.objects.filter(activa=True).count()
    total_cultivos = Cultivo.objects.filter(activo=True).count()
    
    # Producción y rendimiento
    produccion_stats = RegistroProduccion.objects.aggregate(
        produccion_total=Sum('cantidad_kg'),
        rendimiento_promedio=Avg('rendimiento_hectarea')
    )
    
    # Anomalías
    anomalias_total = RegistroProduccion.objects.filter(anomalia_detectada=True).count()
    porcentaje_anomalias = (anomalias_total / total_registros * 100) if total_registros > 0 else 0
    
    # Distribución por temporadas
    temporadas = RegistroProduccion.objects.values('temporada').annotate(
        registros=Count('id'),
        produccion_total=Sum('cantidad_kg')
    ).order_by('-registros')[:10]
    
    # Top cultivos por rendimiento
    top_cultivos = RegistroProduccion.objects.values(
        'cultivo__nombre'
    ).annotate(
        rendimiento_promedio=Avg('rendimiento_hectarea'),
        registros=Count('id')
    ).filter(registros__gte=3).order_by('-rendimiento_promedio')[:5]
    
    # Distribución de calidades
    calidades = RegistroProduccion.objects.exclude(
        calidad__isnull=True
    ).values('calidad').annotate(
        cantidad=Count('id')
    )
    distribucion_calidades = {item['calidad']: item['cantidad'] for item in calidades}
    
    # Eficiencia promedio
    eficiencia_promedio = RegistroProduccion.objects.aggregate(
        eficiencia=Avg('rendimiento_hectarea')
    )['eficiencia'] or 0
    
    data = {
        'total_registros': total_registros,
        'total_parcelas': total_parcelas,
        'total_cultivos': total_cultivos,
        'produccion_total': float(produccion_stats['produccion_total'] or 0),
        'rendimiento_promedio': float(produccion_stats['rendimiento_promedio'] or 0),
        'anomalias_total': anomalias_total,
        'porcentaje_anomalias': float(porcentaje_anomalias),
        'distribucion_temporadas': list(temporadas),
        'top_cultivos_rendimiento': list(top_cultivos),
        'distribucion_calidades': distribucion_calidades,
        'eficiencia_promedio': float(eficiencia_promedio)
    }
    
    serializer = EstadisticasGeneralesSerializer(data)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comparar_variedades_view(request):
    """Comparar rendimiento entre variedades usando pruebas de hipótesis"""
    
    serializer = ComparacionVariedadesSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    cultivo_ids = data['cultivo_ids']
    temporada = data.get('temporada')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    tipo_analisis = data['tipo_analisis']
    nivel_significancia = data['nivel_significancia']
    
    try:
        # Importar librerías estadísticas
        import numpy as np
        from scipy import stats
        
        # Obtener datos para cada cultivo
        cultivos_data = {}
        for cultivo_id in cultivo_ids:
            query = RegistroProduccion.objects.filter(cultivo_id=cultivo_id)
            
            if temporada:
                query = query.filter(temporada=temporada)
            if fecha_inicio:
                query = query.filter(fecha_registro__gte=fecha_inicio)
            if fecha_fin:
                query = query.filter(fecha_registro__lte=fecha_fin)
            
            registros = query.all()
            if len(registros) < 2:
                return Response({
                    'error': f'Se necesitan al menos 2 registros por cultivo para el análisis'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            rendimientos = [r.rendimiento_hectarea for r in registros]
            cultivo = Cultivo.objects.get(id=cultivo_id)
            
            cultivos_data[cultivo_id] = {
                'nombre': cultivo.nombre,
                'variedad': cultivo.variedad,
                'rendimientos': rendimientos,
                'n_muestras': len(rendimientos),
                'media': np.mean(rendimientos),
                'mediana': np.median(rendimientos),
                'desviacion_estandar': np.std(rendimientos),
                'minimo': np.min(rendimientos),
                'maximo': np.max(rendimientos)
            }
        
        # Realizar análisis estadístico
        if len(cultivo_ids) == 2:
            # Comparación entre dos grupos
            grupo1 = cultivos_data[cultivo_ids[0]]['rendimientos']
            grupo2 = cultivos_data[cultivo_ids[1]]['rendimientos']
            
            if tipo_analisis == 't_test':
                estadistico, p_valor = stats.ttest_ind(grupo1, grupo2)
                nombre_prueba = 'Prueba T de Student'
            else:  # mann_whitney
                estadistico, p_valor = stats.mannwhitneyu(grupo1, grupo2, alternative='two-sided')
                nombre_prueba = 'Prueba Mann-Whitney U'
        
        else:
            # Comparación entre múltiples grupos
            grupos = [cultivos_data[cid]['rendimientos'] for cid in cultivo_ids]
            
            if tipo_analisis == 'anova':
                estadistico, p_valor = stats.f_oneway(*grupos)
                nombre_prueba = 'Análisis de Varianza (ANOVA)'
            else:  # kruskal_wallis
                estadistico, p_valor = stats.kruskal(*grupos)
                nombre_prueba = 'Prueba Kruskal-Wallis'
        
        # Determinar significancia
        diferencia_significativa = p_valor < nivel_significancia
        
        # Crear nombre del análisis
        cultivos_nombres = [cultivos_data[cid]['nombre'] for cid in cultivo_ids]
        nombre_analisis = f"Comparación: {' vs '.join(cultivos_nombres)}"
        
        # Guardar análisis
        analisis = AnalisisComparativo.objects.create(
            nombre_analisis=nombre_analisis,
            descripcion=f"Análisis comparativo usando {nombre_prueba}",
            tipo_analisis=tipo_analisis,
            temporada=temporada,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estadistico=float(estadistico),
            p_valor=float(p_valor),
            nivel_significancia=nivel_significancia,
            diferencia_significativa=diferencia_significativa,
            resultados_detallados={
                'cultivos_data': cultivos_data,
                'nombre_prueba': nombre_prueba,
                'interpretacion': 'Hay diferencia significativa entre los rendimientos' if diferencia_significativa else 'No hay diferencia significativa entre los rendimientos'
            },
            creado_por=request.user
        )
        
        # Agregar cultivos al análisis
        analisis.cultivos.set(cultivo_ids)
        
        serializer_response = AnalisisComparativoSerializer(analisis)
        return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        
    except ImportError:
        return Response({
            'error': 'Librerías estadísticas no disponibles'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'Error en el análisis: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clasificar_por_rendimiento_view(request):
    """Clasificar parcelas por rendimiento usando algoritmos de clasificación"""
    
    serializer = ClasificarPorRendimientoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    algoritmo = data['algoritmo']
    cultivo_id = data.get('cultivo_id')
    temporada = data.get('temporada')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    try:
        import numpy as np
        from sklearn.cluster import KMeans
        
        # Construir consulta
        query = RegistroProduccion.objects.all()
        
        if cultivo_id:
            query = query.filter(cultivo_id=cultivo_id)
        if temporada:
            query = query.filter(temporada=temporada)
        if fecha_inicio:
            query = query.filter(fecha_registro__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha_registro__lte=fecha_fin)
        
        # Agrupar por parcela y calcular rendimiento promedio
        parcelas_rendimiento = query.values(
            'parcela_id', 'parcela__codigo', 'parcela__nombre'
        ).annotate(
            rendimiento_promedio=Avg('rendimiento_hectarea'),
            total_registros=Count('id'),
            desviacion_estandar=Avg('rendimiento_hectarea')  # Simplificado
        ).filter(total_registros__gte=2)
        
        if not parcelas_rendimiento:
            return Response({
                'error': 'No se encontraron datos suficientes para la clasificación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extraer rendimientos
        rendimientos = [p['rendimiento_promedio'] for p in parcelas_rendimiento]
        rendimientos_array = np.array(rendimientos)
        
        # Aplicar algoritmo de clasificación
        if algoritmo == 'quartiles':
            q1 = np.percentile(rendimientos, 25)
            q2 = np.percentile(rendimientos, 50)
            q3 = np.percentile(rendimientos, 75)
            
            def clasificar_quartil(rendimiento):
                if rendimiento >= q3:
                    return 'excelente'
                elif rendimiento >= q2:
                    return 'bueno'
                elif rendimiento >= q1:
                    return 'regular'
                else:
                    return 'bajo'
            
            parametros = {'q1': q1, 'q2': q2, 'q3': q3}
            
        elif algoritmo == 'percentiles':
            p90 = np.percentile(rendimientos, 90)
            p70 = np.percentile(rendimientos, 70)
            p30 = np.percentile(rendimientos, 30)
            
            def clasificar_quartil(rendimiento):
                if rendimiento >= p90:
                    return 'excelente'
                elif rendimiento >= p70:
                    return 'bueno'
                elif rendimiento >= p30:
                    return 'regular'
                else:
                    return 'bajo'
            
            parametros = {'p90': p90, 'p70': p70, 'p30': p30}
            
        elif algoritmo == 'zscore':
            media = np.mean(rendimientos)
            std = np.std(rendimientos)
            
            def clasificar_quartil(rendimiento):
                zscore = (rendimiento - media) / std if std > 0 else 0
                if zscore >= 1.5:
                    return 'excelente'
                elif zscore >= 0.5:
                    return 'bueno'
                elif zscore >= -0.5:
                    return 'regular'
                else:
                    return 'bajo'
            
            parametros = {'media': media, 'desviacion_estandar': std}
            
        else:  # kmeans
            kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(rendimientos_array.reshape(-1, 1))
            
            # Mapear clusters a categorías basándose en los centroides
            centroides = kmeans.cluster_centers_.flatten()
            orden_centroides = np.argsort(centroides)
            mapeo_clusters = {
                orden_centroides[0]: 'bajo',
                orden_centroides[1]: 'regular',
                orden_centroides[2]: 'bueno',
                orden_centroides[3]: 'excelente'
            }
            
            def clasificar_quartil(rendimiento, idx):
                return mapeo_clusters[clusters[idx]]
            
            parametros = {'centroides': centroides.tolist(), 'mapeo': mapeo_clusters}
        
        # Clasificar parcelas
        parcelas_clasificadas = []
        for i, parcela in enumerate(parcelas_rendimiento):
            if algoritmo == 'kmeans':
                categoria = clasificar_quartil(parcela['rendimiento_promedio'], i)
            else:
                categoria = clasificar_quartil(parcela['rendimiento_promedio'])
            
            parcelas_clasificadas.append({
                'parcela_id': parcela['parcela_id'],
                'codigo': parcela['parcela__codigo'],
                'nombre': parcela['parcela__nombre'],
                'rendimiento_promedio': parcela['rendimiento_promedio'],
                'total_registros': parcela['total_registros'],
                'categoria': categoria,
                'ranking': i + 1
            })
        
        # Ordenar por rendimiento descendente
        parcelas_clasificadas.sort(key=lambda x: x['rendimiento_promedio'], reverse=True)
        
        # Actualizar ranking
        for i, parcela in enumerate(parcelas_clasificadas):
            parcela['ranking'] = i + 1
        
        # Estadísticas generales
        total_parcelas = len(parcelas_clasificadas)
        rendimiento_general = np.mean(rendimientos)
        
        distribucion_categorias = {}
        for parcela in parcelas_clasificadas:
            categoria = parcela['categoria']
            distribucion_categorias[categoria] = distribucion_categorias.get(categoria, 0) + 1
        
        # Crear nombre de clasificación
        filtros = []
        if cultivo_id:
            cultivo = Cultivo.objects.get(id=cultivo_id)
            filtros.append(f"Cultivo: {cultivo.nombre}")
        if temporada:
            filtros.append(f"Temporada: {temporada}")
        
        nombre_clasificacion = f"Clasificación por {algoritmo.title()}"
        if filtros:
            nombre_clasificacion += f" ({', '.join(filtros)})"
        
        # Guardar clasificación
        clasificacion = ClasificacionRendimiento.objects.create(
            nombre_clasificacion=nombre_clasificacion,
            algoritmo_utilizado=algoritmo,
            cultivo_id=cultivo_id,
            temporada=temporada,
            parametros_algoritmo=parametros,
            resultados_clasificacion={
                'parcelas_clasificadas': parcelas_clasificadas,
                'top_5_parcelas': parcelas_clasificadas[:5],
                'bottom_5_parcelas': parcelas_clasificadas[-5:] if len(parcelas_clasificadas) >= 5 else []
            },
            estadisticas_generales={
                'total_parcelas': total_parcelas,
                'rendimiento_promedio_general': float(rendimiento_general),
                'distribucion_categorias': distribucion_categorias
            },
            creado_por=request.user
        )
        
        serializer_response = ClasificacionRendimientoSerializer(clasificacion)
        return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        
    except ImportError:
        return Response({
            'error': 'Librerías de machine learning no disponibles'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'Error en la clasificación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analizar_serie_temporal_view(request):
    """Analizar serie temporal de una parcela"""
    
    serializer = AnalizarSerieTemporalSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    parcela_id = data['parcela_id']
    cultivo_id = data.get('cultivo_id')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    try:
        import pandas as pd
        import numpy as np
        from sklearn.linear_model import LinearRegression
        
        # Obtener registros
        query = RegistroProduccion.objects.filter(parcela_id=parcela_id)
        
        if cultivo_id:
            query = query.filter(cultivo_id=cultivo_id)
        if fecha_inicio:
            query = query.filter(fecha_registro__gte=fecha_inicio)
        if fecha_fin:
            query = query.filter(fecha_registro__lte=fecha_fin)
        
        registros = query.order_by('fecha_registro')
        
        if len(registros) < 4:
            return Response({
                'error': 'Se necesitan al menos 4 registros para el análisis de series temporales'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear DataFrame
        df = pd.DataFrame([{
            'fecha': r.fecha_registro,
            'rendimiento': r.rendimiento_hectarea,
            'temporada': r.temporada
        } for r in registros])
        
        # Análisis de tendencia
        X = np.arange(len(df)).reshape(-1, 1)
        y = df['rendimiento'].values
        
        modelo_tendencia = LinearRegression()
        modelo_tendencia.fit(X, y)
        
        pendiente = modelo_tendencia.coef_[0]
        r_cuadrado = modelo_tendencia.score(X, y)
        
        # Determinar tipo de tendencia
        if pendiente > 0.1:
            tipo_tendencia = 'creciente'
        elif pendiente < -0.1:
            tipo_tendencia = 'decreciente'
        else:
            tipo_tendencia = 'estable'
        
        # Estadísticas descriptivas
        rendimiento_promedio = df['rendimiento'].mean()
        desviacion_estandar = df['rendimiento'].std()
        coeficiente_variacion = (desviacion_estandar / rendimiento_promedio) * 100
        rendimiento_minimo = df['rendimiento'].min()
        rendimiento_maximo = df['rendimiento'].max()
        
        # Detectar outliers
        Q1 = df['rendimiento'].quantile(0.25)
        Q3 = df['rendimiento'].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        outliers = df[(df['rendimiento'] < limite_inferior) | (df['rendimiento'] > limite_superior)]
        outliers_detalle = outliers[['fecha', 'rendimiento', 'temporada']].to_dict('records')
        
        # Análisis por temporadas
        analisis_temporadas = df.groupby('temporada')['rendimiento'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).to_dict('index')
        
        # Guardar análisis
        parcela = Parcela.objects.get(id=parcela_id)
        cultivo = Cultivo.objects.get(id=cultivo_id) if cultivo_id else None
        
        analisis = AnalisisSeriesTemporal.objects.create(
            parcela=parcela,
            cultivo=cultivo,
            fecha_inicio=fecha_inicio or df['fecha'].min(),
            fecha_fin=fecha_fin or df['fecha'].max(),
            total_registros=len(df),
            tipo_tendencia=tipo_tendencia,
            pendiente=float(pendiente),
            r_cuadrado=float(r_cuadrado),
            rendimiento_promedio=float(rendimiento_promedio),
            desviacion_estandar=float(desviacion_estandar),
            coeficiente_variacion=float(coeficiente_variacion),
            rendimiento_minimo=float(rendimiento_minimo),
            rendimiento_maximo=float(rendimiento_maximo),
            outliers_detectados=len(outliers),
            outliers_detalle=outliers_detalle,
            analisis_temporadas=analisis_temporadas,
            creado_por=request.user
        )
        
        serializer_response = AnalisisSeriesTemporalSerializer(analisis)
        return Response(serializer_response.data, status=status.HTTP_201_CREATED)
        
    except ImportError:
        return Response({
            'error': 'Librerías de análisis no disponibles'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'Error en el análisis: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Vistas para listar análisis guardados
class AnalisisComparativoListView(generics.ListAPIView):
    """Vista para listar análisis comparativos"""
    
    queryset = AnalisisComparativo.objects.all()
    serializer_class = AnalisisComparativoSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_analisis']

class ClasificacionRendimientoListView(generics.ListAPIView):
    """Vista para listar clasificaciones de rendimiento"""
    
    queryset = ClasificacionRendimiento.objects.all()
    serializer_class = ClasificacionRendimientoSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_clasificacion']

class AnalisisSeriesTemporalListView(generics.ListAPIView):
    """Vista para listar análisis de series temporales"""
    
    queryset = AnalisisSeriesTemporal.objects.all()
    serializer_class = AnalisisSeriesTemporalSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-fecha_analisis']
