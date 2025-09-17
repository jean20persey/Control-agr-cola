from flask import request, jsonify
from flask_restx import Resource, fields
from app import api, db
from models import RegistroProduccion, Parcela, Cultivo
from datetime import datetime, date
from sqlalchemy import and_, or_, func

# Namespace para producción
produccion_ns = api.namespace('produccion', description='Registro de producción agrícola')

# Modelos para documentación automática
condiciones_ambientales_model = api.model('CondicionesAmbientales', {
    'temperatura_promedio': fields.Float(description='Temperatura promedio en °C'),
    'precipitacion_mm': fields.Float(description='Precipitación en mm'),
    'humedad_relativa': fields.Float(description='Humedad relativa en %')
})

registro_produccion_model = api.model('RegistroProduccion', {
    'parcela_id': fields.Integer(required=True, description='ID de la parcela'),
    'cultivo_id': fields.Integer(required=True, description='ID del cultivo'),
    'fecha_registro': fields.String(required=True, description='Fecha del registro (YYYY-MM-DD)'),
    'temporada': fields.String(required=True, description='Temporada (ej: 2024-1)'),
    'cantidad_kg': fields.Float(required=True, description='Cantidad producida en kg'),
    'calidad': fields.String(description='Calidad del producto (A, B, C)'),
    'temperatura_promedio': fields.Float(description='Temperatura promedio en °C'),
    'precipitacion_mm': fields.Float(description='Precipitación en mm'),
    'humedad_relativa': fields.Float(description='Humedad relativa en %'),
    'notas_anomalia': fields.String(description='Notas sobre anomalías detectadas')
})

registro_response = api.model('RegistroProduccionResponse', {
    'id': fields.Integer(description='ID del registro'),
    'parcela_id': fields.Integer(description='ID de la parcela'),
    'cultivo_id': fields.Integer(description='ID del cultivo'),
    'fecha_registro': fields.String(description='Fecha del registro'),
    'temporada': fields.String(description='Temporada'),
    'cantidad_kg': fields.Float(description='Cantidad producida en kg'),
    'rendimiento_hectarea': fields.Float(description='Rendimiento por hectárea'),
    'calidad': fields.String(description='Calidad del producto'),
    'condiciones_ambientales': fields.Nested(condiciones_ambientales_model),
    'anomalia_detectada': fields.Boolean(description='Si se detectó anomalía'),
    'desviacion_esperada': fields.Float(description='Desviación del rendimiento esperado'),
    'fecha_creacion': fields.String(description='Fecha de creación del registro')
})

@produccion_ns.route('/')
class RegistrosProduccionList(Resource):
    @produccion_ns.doc('listar_registros_produccion')
    @produccion_ns.param('parcela_id', 'Filtrar por ID de parcela')
    @produccion_ns.param('cultivo_id', 'Filtrar por ID de cultivo')
    @produccion_ns.param('temporada', 'Filtrar por temporada')
    @produccion_ns.param('fecha_inicio', 'Fecha de inicio (YYYY-MM-DD)')
    @produccion_ns.param('fecha_fin', 'Fecha de fin (YYYY-MM-DD)')
    @produccion_ns.marshal_list_with(registro_response)
    def get(self):
        """Obtener registros de producción con filtros opcionales"""
        try:
            query = RegistroProduccion.query
            
            # Aplicar filtros
            parcela_id = request.args.get('parcela_id', type=int)
            if parcela_id:
                query = query.filter_by(parcela_id=parcela_id)
            
            cultivo_id = request.args.get('cultivo_id', type=int)
            if cultivo_id:
                query = query.filter_by(cultivo_id=cultivo_id)
            
            temporada = request.args.get('temporada')
            if temporada:
                query = query.filter_by(temporada=temporada)
            
            fecha_inicio = request.args.get('fecha_inicio')
            if fecha_inicio:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                query = query.filter(RegistroProduccion.fecha_registro >= fecha_inicio)
            
            fecha_fin = request.args.get('fecha_fin')
            if fecha_fin:
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
                query = query.filter(RegistroProduccion.fecha_registro <= fecha_fin)
            
            registros = query.order_by(RegistroProduccion.fecha_registro.desc()).all()
            return [registro.to_dict() for registro in registros], 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @produccion_ns.doc('crear_registro_produccion')
    @produccion_ns.expect(registro_produccion_model)
    @produccion_ns.marshal_with(registro_response, code=201)
    def post(self):
        """Crear un nuevo registro de producción"""
        try:
            data = request.get_json()
            
            # Validar que existan la parcela y el cultivo
            parcela = Parcela.query.get(data['parcela_id'])
            if not parcela or not parcela.activa:
                return {'error': 'La parcela especificada no existe o no está activa'}, 400
            
            cultivo = Cultivo.query.get(data['cultivo_id'])
            if not cultivo or not cultivo.activo:
                return {'error': 'El cultivo especificado no existe o no está activo'}, 400
            
            # Calcular rendimiento por hectárea
            rendimiento_hectarea = data['cantidad_kg'] / parcela.area_hectareas
            
            # Calcular desviación del rendimiento esperado
            desviacion_esperada = rendimiento_hectarea - cultivo.rendimiento_esperado
            
            # Detectar anomalías (desviación mayor al 20% del rendimiento esperado)
            umbral_anomalia = cultivo.rendimiento_esperado * 0.2
            anomalia_detectada = abs(desviacion_esperada) > umbral_anomalia
            
            registro = RegistroProduccion(
                parcela_id=data['parcela_id'],
                cultivo_id=data['cultivo_id'],
                fecha_registro=datetime.strptime(data['fecha_registro'], '%Y-%m-%d').date(),
                temporada=data['temporada'],
                cantidad_kg=data['cantidad_kg'],
                rendimiento_hectarea=rendimiento_hectarea,
                calidad=data.get('calidad'),
                temperatura_promedio=data.get('temperatura_promedio'),
                precipitacion_mm=data.get('precipitacion_mm'),
                humedad_relativa=data.get('humedad_relativa'),
                desviacion_esperada=desviacion_esperada,
                anomalia_detectada=anomalia_detectada,
                notas_anomalia=data.get('notas_anomalia')
            )
            
            db.session.add(registro)
            db.session.commit()
            
            return registro.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@produccion_ns.route('/<int:registro_id>')
class RegistroProduccionDetail(Resource):
    @produccion_ns.doc('obtener_registro_produccion')
    @produccion_ns.marshal_with(registro_response)
    def get(self, registro_id):
        """Obtener un registro de producción específico"""
        try:
            registro = RegistroProduccion.query.get_or_404(registro_id)
            return registro.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @produccion_ns.doc('actualizar_registro_produccion')
    @produccion_ns.expect(registro_produccion_model)
    @produccion_ns.marshal_with(registro_response)
    def put(self, registro_id):
        """Actualizar un registro de producción"""
        try:
            registro = RegistroProduccion.query.get_or_404(registro_id)
            data = request.get_json()
            
            # Validar parcela y cultivo
            parcela = Parcela.query.get(data['parcela_id'])
            if not parcela or not parcela.activa:
                return {'error': 'La parcela especificada no existe o no está activa'}, 400
            
            cultivo = Cultivo.query.get(data['cultivo_id'])
            if not cultivo or not cultivo.activo:
                return {'error': 'El cultivo especificado no existe o no está activo'}, 400
            
            # Recalcular métricas
            rendimiento_hectarea = data['cantidad_kg'] / parcela.area_hectareas
            desviacion_esperada = rendimiento_hectarea - cultivo.rendimiento_esperado
            umbral_anomalia = cultivo.rendimiento_esperado * 0.2
            anomalia_detectada = abs(desviacion_esperada) > umbral_anomalia
            
            # Actualizar registro
            registro.parcela_id = data['parcela_id']
            registro.cultivo_id = data['cultivo_id']
            registro.fecha_registro = datetime.strptime(data['fecha_registro'], '%Y-%m-%d').date()
            registro.temporada = data['temporada']
            registro.cantidad_kg = data['cantidad_kg']
            registro.rendimiento_hectarea = rendimiento_hectarea
            registro.calidad = data.get('calidad')
            registro.temperatura_promedio = data.get('temperatura_promedio')
            registro.precipitacion_mm = data.get('precipitacion_mm')
            registro.humedad_relativa = data.get('humedad_relativa')
            registro.desviacion_esperada = desviacion_esperada
            registro.anomalia_detectada = anomalia_detectada
            registro.notas_anomalia = data.get('notas_anomalia')
            
            db.session.commit()
            return registro.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @produccion_ns.doc('eliminar_registro_produccion')
    def delete(self, registro_id):
        """Eliminar un registro de producción"""
        try:
            registro = RegistroProduccion.query.get_or_404(registro_id)
            db.session.delete(registro)
            db.session.commit()
            return {'message': 'Registro eliminado correctamente'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@produccion_ns.route('/anomalias')
class RegistrosAnomalias(Resource):
    @produccion_ns.doc('obtener_registros_con_anomalias')
    @produccion_ns.marshal_list_with(registro_response)
    def get(self):
        """Obtener todos los registros con anomalías detectadas"""
        try:
            registros = RegistroProduccion.query.filter_by(anomalia_detectada=True).order_by(
                RegistroProduccion.fecha_registro.desc()
            ).all()
            return [registro.to_dict() for registro in registros], 200
        except Exception as e:
            return {'error': str(e)}, 500

@produccion_ns.route('/estadisticas/temporada/<string:temporada>')
class EstadisticasTemporada(Resource):
    @produccion_ns.doc('obtener_estadisticas_temporada')
    def get(self, temporada):
        """Obtener estadísticas de producción por temporada"""
        try:
            registros = RegistroProduccion.query.filter_by(temporada=temporada).all()
            
            if not registros:
                return {'error': 'No se encontraron registros para la temporada especificada'}, 404
            
            # Calcular estadísticas
            total_produccion = sum(r.cantidad_kg for r in registros)
            rendimiento_promedio = sum(r.rendimiento_hectarea for r in registros) / len(registros)
            anomalias_count = sum(1 for r in registros if r.anomalia_detectada)
            
            # Distribución por calidad
            calidades = {}
            for registro in registros:
                if registro.calidad:
                    calidades[registro.calidad] = calidades.get(registro.calidad, 0) + 1
            
            # Top 5 parcelas por rendimiento
            parcelas_rendimiento = {}
            for registro in registros:
                if registro.parcela_id not in parcelas_rendimiento:
                    parcelas_rendimiento[registro.parcela_id] = []
                parcelas_rendimiento[registro.parcela_id].append(registro.rendimiento_hectarea)
            
            top_parcelas = []
            for parcela_id, rendimientos in parcelas_rendimiento.items():
                promedio = sum(rendimientos) / len(rendimientos)
                parcela = Parcela.query.get(parcela_id)
                top_parcelas.append({
                    'parcela_id': parcela_id,
                    'parcela_nombre': parcela.nombre if parcela else 'Desconocida',
                    'rendimiento_promedio': promedio
                })
            
            top_parcelas.sort(key=lambda x: x['rendimiento_promedio'], reverse=True)
            
            return {
                'temporada': temporada,
                'total_registros': len(registros),
                'total_produccion_kg': total_produccion,
                'rendimiento_promedio_hectarea': rendimiento_promedio,
                'anomalias_detectadas': anomalias_count,
                'porcentaje_anomalias': (anomalias_count / len(registros)) * 100,
                'distribucion_calidad': calidades,
                'top_5_parcelas': top_parcelas[:5]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500

@produccion_ns.route('/series-temporales/<int:parcela_id>')
class SeriesTemporales(Resource):
    @produccion_ns.doc('obtener_series_temporales_parcela')
    @produccion_ns.param('limite', 'Número máximo de registros a retornar')
    def get(self, parcela_id):
        """Obtener serie temporal de producción para una parcela específica"""
        try:
            limite = request.args.get('limite', 50, type=int)
            
            registros = RegistroProduccion.query.filter_by(parcela_id=parcela_id).order_by(
                RegistroProduccion.fecha_registro.asc()
            ).limit(limite).all()
            
            if not registros:
                return {'error': 'No se encontraron registros para la parcela especificada'}, 404
            
            serie_temporal = []
            for registro in registros:
                serie_temporal.append({
                    'fecha': registro.fecha_registro.isoformat(),
                    'rendimiento_hectarea': registro.rendimiento_hectarea,
                    'cantidad_kg': registro.cantidad_kg,
                    'temporada': registro.temporada,
                    'anomalia': registro.anomalia_detectada,
                    'temperatura': registro.temperatura_promedio,
                    'precipitacion': registro.precipitacion_mm
                })
            
            return {
                'parcela_id': parcela_id,
                'total_puntos': len(serie_temporal),
                'serie_temporal': serie_temporal
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500
