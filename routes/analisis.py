from flask import request, jsonify
from flask_restx import Resource, fields
from app import api, db
from models import RegistroProduccion, Parcela, Cultivo, PrediccionCosecha
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from datetime import datetime, date, timedelta
import json

# Namespace para análisis
analisis_ns = api.namespace('analisis', description='Análisis estadístico y predicciones')

# Modelos para documentación automática
comparacion_variedades_model = api.model('ComparacionVariedades', {
    'cultivo_id_1': fields.Integer(required=True, description='ID del primer cultivo'),
    'cultivo_id_2': fields.Integer(required=True, description='ID del segundo cultivo'),
    'temporada': fields.String(description='Temporada específica para comparar')
})

prediccion_model = api.model('PrediccionCosecha', {
    'parcela_id': fields.Integer(required=True, description='ID de la parcela'),
    'cultivo_id': fields.Integer(required=True, description='ID del cultivo'),
    'temporada_objetivo': fields.String(required=True, description='Temporada objetivo (ej: 2024-2)'),
    'modelo': fields.String(description='Tipo de modelo (linear, random_forest)', default='linear')
})

@analisis_ns.route('/estadisticas-generales')
class EstadisticasGenerales(Resource):
    @analisis_ns.doc('obtener_estadisticas_generales')
    def get(self):
        """Obtener estadísticas generales del sistema"""
        try:
            # Estadísticas básicas
            total_registros = RegistroProduccion.query.count()
            total_parcelas = Parcela.query.filter_by(activa=True).count()
            total_cultivos = Cultivo.query.filter_by(activo=True).count()
            
            # Producción total
            produccion_total = db.session.query(
                func.sum(RegistroProduccion.cantidad_kg)
            ).scalar() or 0
            
            # Rendimiento promedio general
            rendimiento_promedio = db.session.query(
                func.avg(RegistroProduccion.rendimiento_hectarea)
            ).scalar() or 0
            
            # Anomalías detectadas
            anomalias_total = RegistroProduccion.query.filter_by(anomalia_detectada=True).count()
            porcentaje_anomalias = (anomalias_total / total_registros * 100) if total_registros > 0 else 0
            
            # Distribución por temporadas
            temporadas = db.session.query(
                RegistroProduccion.temporada,
                func.count(RegistroProduccion.id).label('registros'),
                func.sum(RegistroProduccion.cantidad_kg).label('produccion_total')
            ).group_by(RegistroProduccion.temporada).all()
            
            # Top cultivos por rendimiento
            top_cultivos = db.session.query(
                Cultivo.nombre,
                func.avg(RegistroProduccion.rendimiento_hectarea).label('rendimiento_promedio')
            ).join(RegistroProduccion).group_by(Cultivo.id, Cultivo.nombre).order_by(
                func.avg(RegistroProduccion.rendimiento_hectarea).desc()
            ).limit(5).all()
            
            return {
                'resumen': {
                    'total_registros': total_registros,
                    'total_parcelas': total_parcelas,
                    'total_cultivos': total_cultivos,
                    'produccion_total_kg': float(produccion_total),
                    'rendimiento_promedio_hectarea': float(rendimiento_promedio),
                    'anomalias_detectadas': anomalias_total,
                    'porcentaje_anomalias': float(porcentaje_anomalias)
                },
                'por_temporadas': [
                    {
                        'temporada': temp[0],
                        'registros': temp[1],
                        'produccion_kg': float(temp[2] or 0)
                    } for temp in temporadas
                ],
                'top_cultivos_rendimiento': [
                    {
                        'cultivo': cultivo[0],
                        'rendimiento_promedio': float(cultivo[1])
                    } for cultivo in top_cultivos
                ]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

@analisis_ns.route('/comparar-variedades')
class CompararVariedades(Resource):
    @analisis_ns.doc('comparar_variedades')
    @analisis_ns.expect(comparacion_variedades_model)
    def post(self):
        """Comparar rendimiento entre dos variedades de cultivos (prueba de hipótesis)"""
        try:
            data = request.get_json()
            cultivo_id_1 = data['cultivo_id_1']
            cultivo_id_2 = data['cultivo_id_2']
            temporada = data.get('temporada')
            
            # Obtener datos de ambos cultivos
            query1 = RegistroProduccion.query.filter_by(cultivo_id=cultivo_id_1)
            query2 = RegistroProduccion.query.filter_by(cultivo_id=cultivo_id_2)
            
            if temporada:
                query1 = query1.filter_by(temporada=temporada)
                query2 = query2.filter_by(temporada=temporada)
            
            registros1 = query1.all()
            registros2 = query2.all()
            
            if len(registros1) < 2 or len(registros2) < 2:
                return {'error': 'Se necesitan al menos 2 registros por cultivo para la comparación'}, 400
            
            # Extraer rendimientos
            rendimientos1 = [r.rendimiento_hectarea for r in registros1]
            rendimientos2 = [r.rendimiento_hectarea for r in registros2]
            
            # Estadísticas descriptivas
            stats1 = {
                'media': np.mean(rendimientos1),
                'mediana': np.median(rendimientos1),
                'desviacion_estandar': np.std(rendimientos1),
                'minimo': np.min(rendimientos1),
                'maximo': np.max(rendimientos1),
                'n_muestras': len(rendimientos1)
            }
            
            stats2 = {
                'media': np.mean(rendimientos2),
                'mediana': np.median(rendimientos2),
                'desviacion_estandar': np.std(rendimientos2),
                'minimo': np.min(rendimientos2),
                'maximo': np.max(rendimientos2),
                'n_muestras': len(rendimientos2)
            }
            
            # Prueba t de Student para comparar medias
            t_stat, p_value = stats.ttest_ind(rendimientos1, rendimientos2)
            
            # Prueba de Mann-Whitney U (no paramétrica)
            u_stat, u_p_value = stats.mannwhitneyu(rendimientos1, rendimientos2, alternative='two-sided')
            
            # Interpretación de resultados
            alpha = 0.05
            diferencia_significativa = p_value < alpha
            
            cultivo1 = Cultivo.query.get(cultivo_id_1)
            cultivo2 = Cultivo.query.get(cultivo_id_2)
            
            return {
                'cultivos_comparados': {
                    'cultivo_1': {
                        'id': cultivo_id_1,
                        'nombre': cultivo1.nombre if cultivo1 else 'Desconocido',
                        'variedad': cultivo1.variedad if cultivo1 else 'Desconocida'
                    },
                    'cultivo_2': {
                        'id': cultivo_id_2,
                        'nombre': cultivo2.nombre if cultivo2 else 'Desconocido',
                        'variedad': cultivo2.variedad if cultivo2 else 'Desconocida'
                    }
                },
                'temporada': temporada or 'Todas las temporadas',
                'estadisticas_descriptivas': {
                    'cultivo_1': stats1,
                    'cultivo_2': stats2
                },
                'pruebas_hipotesis': {
                    'prueba_t': {
                        'estadistico_t': float(t_stat),
                        'p_valor': float(p_value),
                        'diferencia_significativa': diferencia_significativa,
                        'interpretacion': 'Hay diferencia significativa entre los rendimientos' if diferencia_significativa else 'No hay diferencia significativa entre los rendimientos'
                    },
                    'prueba_mann_whitney': {
                        'estadistico_u': float(u_stat),
                        'p_valor': float(u_p_value),
                        'diferencia_significativa': u_p_value < alpha
                    }
                },
                'diferencia_medias': float(stats1['media'] - stats2['media']),
                'mejor_rendimiento': 'cultivo_1' if stats1['media'] > stats2['media'] else 'cultivo_2'
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

@analisis_ns.route('/series-temporales/analisis/<int:parcela_id>')
class AnalisisSeriesTemporales(Resource):
    @analisis_ns.doc('analizar_series_temporales')
    def get(self, parcela_id):
        """Análisis de series temporales para detectar tendencias y estacionalidad"""
        try:
            registros = RegistroProduccion.query.filter_by(parcela_id=parcela_id).order_by(
                RegistroProduccion.fecha_registro.asc()
            ).all()
            
            if len(registros) < 4:
                return {'error': 'Se necesitan al menos 4 registros para el análisis de series temporales'}, 400
            
            # Crear DataFrame
            df = pd.DataFrame([{
                'fecha': r.fecha_registro,
                'rendimiento': r.rendimiento_hectarea,
                'temporada': r.temporada
            } for r in registros])
            
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha')
            
            # Análisis de tendencia (regresión lineal simple)
            X = np.arange(len(df)).reshape(-1, 1)
            y = df['rendimiento'].values
            
            modelo_tendencia = LinearRegression()
            modelo_tendencia.fit(X, y)
            
            tendencia = modelo_tendencia.predict(X)
            pendiente = modelo_tendencia.coef_[0]
            
            # Calcular estadísticas de la serie
            media_rendimiento = df['rendimiento'].mean()
            desviacion_estandar = df['rendimiento'].std()
            coef_variacion = (desviacion_estandar / media_rendimiento) * 100
            
            # Detectar valores atípicos (outliers)
            Q1 = df['rendimiento'].quantile(0.25)
            Q3 = df['rendimiento'].quantile(0.75)
            IQR = Q3 - Q1
            limite_inferior = Q1 - 1.5 * IQR
            limite_superior = Q3 + 1.5 * IQR
            
            outliers = df[(df['rendimiento'] < limite_inferior) | (df['rendimiento'] > limite_superior)]
            
            # Análisis por temporadas
            stats_temporadas = df.groupby('temporada')['rendimiento'].agg([
                'count', 'mean', 'std', 'min', 'max'
            ]).to_dict('index')
            
            parcela = Parcela.query.get(parcela_id)
            
            return {
                'parcela': {
                    'id': parcela_id,
                    'nombre': parcela.nombre if parcela else 'Desconocida',
                    'codigo': parcela.codigo if parcela else 'Desconocido'
                },
                'periodo_analisis': {
                    'fecha_inicio': df['fecha'].min().isoformat(),
                    'fecha_fin': df['fecha'].max().isoformat(),
                    'total_registros': len(df)
                },
                'estadisticas_generales': {
                    'rendimiento_promedio': float(media_rendimiento),
                    'desviacion_estandar': float(desviacion_estandar),
                    'coeficiente_variacion': float(coef_variacion),
                    'rendimiento_minimo': float(df['rendimiento'].min()),
                    'rendimiento_maximo': float(df['rendimiento'].max())
                },
                'analisis_tendencia': {
                    'pendiente': float(pendiente),
                    'interpretacion': 'Tendencia creciente' if pendiente > 0.1 else 'Tendencia decreciente' if pendiente < -0.1 else 'Tendencia estable',
                    'r_cuadrado': float(modelo_tendencia.score(X, y))
                },
                'valores_atipicos': {
                    'cantidad': len(outliers),
                    'registros': outliers[['fecha', 'rendimiento', 'temporada']].to_dict('records')
                },
                'analisis_por_temporadas': {
                    temporada: {
                        'registros': int(stats['count']),
                        'rendimiento_promedio': float(stats['mean']),
                        'desviacion_estandar': float(stats['std']) if not pd.isna(stats['std']) else 0,
                        'minimo': float(stats['min']),
                        'maximo': float(stats['max'])
                    } for temporada, stats in stats_temporadas.items()
                }
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

@analisis_ns.route('/predicciones/crear')
class CrearPrediccion(Resource):
    @analisis_ns.doc('crear_prediccion_cosecha')
    @analisis_ns.expect(prediccion_model)
    def post(self):
        """Crear predicción de cosecha usando modelos numéricos"""
        try:
            data = request.get_json()
            parcela_id = data['parcela_id']
            cultivo_id = data['cultivo_id']
            temporada_objetivo = data['temporada_objetivo']
            tipo_modelo = data.get('modelo', 'linear')
            
            # Obtener datos históricos
            registros = RegistroProduccion.query.filter_by(
                parcela_id=parcela_id,
                cultivo_id=cultivo_id
            ).order_by(RegistroProduccion.fecha_registro.asc()).all()
            
            if len(registros) < 5:
                return {'error': 'Se necesitan al menos 5 registros históricos para crear predicciones'}, 400
            
            # Preparar datos para el modelo
            df = pd.DataFrame([{
                'fecha': r.fecha_registro,
                'rendimiento': r.rendimiento_hectarea,
                'temperatura': r.temperatura_promedio or 20,  # valor por defecto
                'precipitacion': r.precipitacion_mm or 50,
                'humedad': r.humedad_relativa or 60,
                'dias_desde_inicio': (r.fecha_registro - registros[0].fecha_registro).days
            } for r in registros])
            
            # Características (features) para el modelo
            X = df[['dias_desde_inicio', 'temperatura', 'precipitacion', 'humedad']].values
            y = df['rendimiento'].values
            
            # Dividir datos para entrenamiento y validación
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Entrenar modelo según el tipo especificado
            if tipo_modelo == 'random_forest':
                modelo = RandomForestRegressor(n_estimators=100, random_state=42)
            else:  # linear por defecto
                modelo = LinearRegression()
            
            modelo.fit(X_train, y_train)
            
            # Evaluar modelo
            y_pred_test = modelo.predict(X_test)
            r2 = r2_score(y_test, y_pred_test)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
            
            # Hacer predicción para la temporada objetivo
            # Usar promedios históricos para las condiciones ambientales
            temp_promedio = df['temperatura'].mean()
            precip_promedio = df['precipitacion'].mean()
            humedad_promedio = df['humedad'].mean()
            
            # Estimar días desde inicio para la temporada objetivo
            ultimo_registro = max(r.fecha_registro for r in registros)
            dias_futuros = (ultimo_registro - registros[0].fecha_registro).days + 180  # aproximación
            
            X_prediccion = np.array([[dias_futuros, temp_promedio, precip_promedio, humedad_promedio]])
            rendimiento_predicho = modelo.predict(X_prediccion)[0]
            
            # Calcular intervalo de confianza (aproximado)
            error_estandar = rmse
            confianza = 0.95
            z_score = 1.96  # para 95% de confianza
            margen_error = z_score * error_estandar
            
            rango_minimo = max(0, rendimiento_predicho - margen_error)
            rango_maximo = rendimiento_predicho + margen_error
            
            # Guardar predicción en la base de datos
            prediccion = PrediccionCosecha(
                parcela_id=parcela_id,
                cultivo_id=cultivo_id,
                fecha_prediccion=date.today(),
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
            
            db.session.add(prediccion)
            db.session.commit()
            
            parcela = Parcela.query.get(parcela_id)
            cultivo = Cultivo.query.get(cultivo_id)
            
            return {
                'prediccion_id': prediccion.id,
                'parcela': {
                    'id': parcela_id,
                    'nombre': parcela.nombre if parcela else 'Desconocida'
                },
                'cultivo': {
                    'id': cultivo_id,
                    'nombre': cultivo.nombre if cultivo else 'Desconocido'
                },
                'temporada_objetivo': temporada_objetivo,
                'prediccion': {
                    'rendimiento_predicho': float(rendimiento_predicho),
                    'rango_minimo': float(rango_minimo),
                    'rango_maximo': float(rango_maximo),
                    'confianza': float(r2)
                },
                'modelo': {
                    'tipo': tipo_modelo,
                    'r2_score': float(r2),
                    'rmse': float(rmse),
                    'registros_utilizados': len(registros)
                },
                'fecha_prediccion': date.today().isoformat()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@analisis_ns.route('/predicciones')
class ListarPredicciones(Resource):
    @analisis_ns.doc('listar_predicciones')
    @analisis_ns.param('parcela_id', 'Filtrar por ID de parcela')
    @analisis_ns.param('cultivo_id', 'Filtrar por ID de cultivo')
    def get(self):
        """Obtener todas las predicciones de cosecha"""
        try:
            query = PrediccionCosecha.query
            
            parcela_id = request.args.get('parcela_id', type=int)
            if parcela_id:
                query = query.filter_by(parcela_id=parcela_id)
            
            cultivo_id = request.args.get('cultivo_id', type=int)
            if cultivo_id:
                query = query.filter_by(cultivo_id=cultivo_id)
            
            predicciones = query.order_by(PrediccionCosecha.fecha_prediccion.desc()).all()
            
            return [prediccion.to_dict() for prediccion in predicciones], 200
        except Exception as e:
            return {'error': str(e)}, 500

@analisis_ns.route('/clasificacion-rendimiento')
class ClasificacionRendimiento(Resource):
    @analisis_ns.doc('clasificar_parcelas_por_rendimiento')
    @analisis_ns.param('temporada', 'Temporada específica para clasificar')
    @analisis_ns.param('cultivo_id', 'ID del cultivo para filtrar')
    def get(self):
        """Clasificar y ordenar parcelas por rendimiento (algoritmo de clasificación)"""
        try:
            temporada = request.args.get('temporada')
            cultivo_id = request.args.get('cultivo_id', type=int)
            
            # Construir consulta base
            query = db.session.query(
                RegistroProduccion.parcela_id,
                Parcela.nombre.label('parcela_nombre'),
                Parcela.codigo.label('parcela_codigo'),
                func.avg(RegistroProduccion.rendimiento_hectarea).label('rendimiento_promedio'),
                func.count(RegistroProduccion.id).label('total_registros'),
                func.stddev(RegistroProduccion.rendimiento_hectarea).label('desviacion_estandar')
            ).join(Parcela, RegistroProduccion.parcela_id == Parcela.id)
            
            if temporada:
                query = query.filter(RegistroProduccion.temporada == temporada)
            
            if cultivo_id:
                query = query.filter(RegistroProduccion.cultivo_id == cultivo_id)
            
            resultados = query.group_by(
                RegistroProduccion.parcela_id, 
                Parcela.nombre, 
                Parcela.codigo
            ).all()
            
            if not resultados:
                return {'error': 'No se encontraron datos para los filtros especificados'}, 404
            
            # Clasificar parcelas por rendimiento
            parcelas_clasificadas = []
            for resultado in resultados:
                rendimiento = float(resultado.rendimiento_promedio)
                desviacion = float(resultado.desviacion_estandar or 0)
                
                # Clasificación por rendimiento
                if rendimiento >= 8000:
                    categoria = 'Excelente'
                    color = '#4CAF50'
                elif rendimiento >= 6000:
                    categoria = 'Bueno'
                    color = '#8BC34A'
                elif rendimiento >= 4000:
                    categoria = 'Regular'
                    color = '#FFC107'
                else:
                    categoria = 'Bajo'
                    color = '#F44336'
                
                # Clasificación por consistencia (basada en desviación estándar)
                coef_variacion = (desviacion / rendimiento) * 100 if rendimiento > 0 else 0
                if coef_variacion <= 10:
                    consistencia = 'Muy consistente'
                elif coef_variacion <= 20:
                    consistencia = 'Consistente'
                elif coef_variacion <= 30:
                    consistencia = 'Moderadamente consistente'
                else:
                    consistencia = 'Inconsistente'
                
                parcelas_clasificadas.append({
                    'parcela_id': resultado.parcela_id,
                    'nombre': resultado.parcela_nombre,
                    'codigo': resultado.parcela_codigo,
                    'rendimiento_promedio': rendimiento,
                    'total_registros': resultado.total_registros,
                    'desviacion_estandar': desviacion,
                    'coeficiente_variacion': coef_variacion,
                    'categoria_rendimiento': categoria,
                    'categoria_color': color,
                    'consistencia': consistencia
                })
            
            # Ordenar por rendimiento descendente
            parcelas_clasificadas.sort(key=lambda x: x['rendimiento_promedio'], reverse=True)
            
            # Agregar ranking
            for i, parcela in enumerate(parcelas_clasificadas, 1):
                parcela['ranking'] = i
            
            # Estadísticas generales de la clasificación
            total_parcelas = len(parcelas_clasificadas)
            rendimiento_general = sum(p['rendimiento_promedio'] for p in parcelas_clasificadas) / total_parcelas
            
            distribucion_categorias = {}
            for parcela in parcelas_clasificadas:
                categoria = parcela['categoria_rendimiento']
                distribucion_categorias[categoria] = distribucion_categorias.get(categoria, 0) + 1
            
            return {
                'filtros_aplicados': {
                    'temporada': temporada or 'Todas las temporadas',
                    'cultivo_id': cultivo_id or 'Todos los cultivos'
                },
                'estadisticas_generales': {
                    'total_parcelas': total_parcelas,
                    'rendimiento_promedio_general': float(rendimiento_general),
                    'distribucion_categorias': distribucion_categorias
                },
                'clasificacion_parcelas': parcelas_clasificadas,
                'top_5_parcelas': parcelas_clasificadas[:5],
                'bottom_5_parcelas': parcelas_clasificadas[-5:] if len(parcelas_clasificadas) >= 5 else []
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500
