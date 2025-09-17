from flask import request, jsonify
from flask_restx import Resource, fields
from app import api, db
from models import Parcela, Cultivo
from datetime import datetime, date

# Namespace para parcelas
parcelas_ns = api.namespace('parcelas', description='Gestión de parcelas')

# Modelos para documentación automática
ubicacion_model = api.model('Ubicacion', {
    'lat': fields.Float(description='Latitud'),
    'lng': fields.Float(description='Longitud')
})

parcela_model = api.model('Parcela', {
    'codigo': fields.String(required=True, description='Código único de la parcela'),
    'nombre': fields.String(required=True, description='Nombre de la parcela'),
    'area_hectareas': fields.Float(required=True, description='Área en hectáreas'),
    'ubicacion_lat': fields.Float(description='Latitud'),
    'ubicacion_lng': fields.Float(description='Longitud'),
    'tipo_suelo': fields.String(description='Tipo de suelo'),
    'ph_suelo': fields.Float(description='pH del suelo'),
    'cultivo_id': fields.Integer(description='ID del cultivo asignado'),
    'fecha_siembra': fields.String(description='Fecha de siembra (YYYY-MM-DD)'),
    'fecha_cosecha_estimada': fields.String(description='Fecha estimada de cosecha (YYYY-MM-DD)')
})

parcela_response = api.model('ParcelaResponse', {
    'id': fields.Integer(description='ID de la parcela'),
    'codigo': fields.String(description='Código único de la parcela'),
    'nombre': fields.String(description='Nombre de la parcela'),
    'area_hectareas': fields.Float(description='Área en hectáreas'),
    'ubicacion': fields.Nested(ubicacion_model),
    'tipo_suelo': fields.String(description='Tipo de suelo'),
    'ph_suelo': fields.Float(description='pH del suelo'),
    'cultivo_id': fields.Integer(description='ID del cultivo asignado'),
    'fecha_siembra': fields.String(description='Fecha de siembra'),
    'fecha_cosecha_estimada': fields.String(description='Fecha estimada de cosecha'),
    'activa': fields.Boolean(description='Estado de la parcela'),
    'fecha_creacion': fields.String(description='Fecha de creación')
})

@parcelas_ns.route('/')
class ParcelasList(Resource):
    @parcelas_ns.doc('listar_parcelas')
    @parcelas_ns.marshal_list_with(parcela_response)
    def get(self):
        """Obtener todas las parcelas activas"""
        try:
            parcelas = Parcela.query.filter_by(activa=True).all()
            return [parcela.to_dict() for parcela in parcelas], 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @parcelas_ns.doc('crear_parcela')
    @parcelas_ns.expect(parcela_model)
    @parcelas_ns.marshal_with(parcela_response, code=201)
    def post(self):
        """Crear una nueva parcela"""
        try:
            data = request.get_json()
            
            # Validar que no exista una parcela con el mismo código
            if Parcela.query.filter_by(codigo=data['codigo']).first():
                return {'error': 'Ya existe una parcela con ese código'}, 400
            
            # Validar cultivo si se proporciona
            if data.get('cultivo_id'):
                cultivo = Cultivo.query.get(data['cultivo_id'])
                if not cultivo or not cultivo.activo:
                    return {'error': 'El cultivo especificado no existe o no está activo'}, 400
            
            parcela = Parcela(
                codigo=data['codigo'],
                nombre=data['nombre'],
                area_hectareas=data['area_hectareas'],
                ubicacion_lat=data.get('ubicacion_lat'),
                ubicacion_lng=data.get('ubicacion_lng'),
                tipo_suelo=data.get('tipo_suelo'),
                ph_suelo=data.get('ph_suelo'),
                cultivo_id=data.get('cultivo_id')
            )
            
            # Procesar fechas si se proporcionan
            if data.get('fecha_siembra'):
                parcela.fecha_siembra = datetime.strptime(data['fecha_siembra'], '%Y-%m-%d').date()
            
            if data.get('fecha_cosecha_estimada'):
                parcela.fecha_cosecha_estimada = datetime.strptime(data['fecha_cosecha_estimada'], '%Y-%m-%d').date()
            
            db.session.add(parcela)
            db.session.commit()
            
            return parcela.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@parcelas_ns.route('/<int:parcela_id>')
class ParcelaDetail(Resource):
    @parcelas_ns.doc('obtener_parcela')
    @parcelas_ns.marshal_with(parcela_response)
    def get(self, parcela_id):
        """Obtener una parcela específica"""
        try:
            parcela = Parcela.query.get_or_404(parcela_id)
            return parcela.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @parcelas_ns.doc('actualizar_parcela')
    @parcelas_ns.expect(parcela_model)
    @parcelas_ns.marshal_with(parcela_response)
    def put(self, parcela_id):
        """Actualizar una parcela"""
        try:
            parcela = Parcela.query.get_or_404(parcela_id)
            data = request.get_json()
            
            # Validar código único (excluyendo la parcela actual)
            existing = Parcela.query.filter(
                Parcela.codigo == data['codigo'],
                Parcela.id != parcela_id
            ).first()
            
            if existing:
                return {'error': 'Ya existe una parcela con ese código'}, 400
            
            # Validar cultivo si se proporciona
            if data.get('cultivo_id'):
                cultivo = Cultivo.query.get(data['cultivo_id'])
                if not cultivo or not cultivo.activo:
                    return {'error': 'El cultivo especificado no existe o no está activo'}, 400
            
            # Actualizar campos
            parcela.codigo = data['codigo']
            parcela.nombre = data['nombre']
            parcela.area_hectareas = data['area_hectareas']
            parcela.ubicacion_lat = data.get('ubicacion_lat')
            parcela.ubicacion_lng = data.get('ubicacion_lng')
            parcela.tipo_suelo = data.get('tipo_suelo')
            parcela.ph_suelo = data.get('ph_suelo')
            parcela.cultivo_id = data.get('cultivo_id')
            
            # Procesar fechas
            if data.get('fecha_siembra'):
                parcela.fecha_siembra = datetime.strptime(data['fecha_siembra'], '%Y-%m-%d').date()
            
            if data.get('fecha_cosecha_estimada'):
                parcela.fecha_cosecha_estimada = datetime.strptime(data['fecha_cosecha_estimada'], '%Y-%m-%d').date()
            
            db.session.commit()
            return parcela.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @parcelas_ns.doc('eliminar_parcela')
    def delete(self, parcela_id):
        """Eliminar (desactivar) una parcela"""
        try:
            parcela = Parcela.query.get_or_404(parcela_id)
            parcela.activa = False
            db.session.commit()
            return {'message': 'Parcela eliminada correctamente'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@parcelas_ns.route('/codigo/<string:codigo>')
class ParcelaPorCodigo(Resource):
    @parcelas_ns.doc('obtener_parcela_por_codigo')
    @parcelas_ns.marshal_with(parcela_response)
    def get(self, codigo):
        """Obtener parcela por código (acceso rápido con índice hash)"""
        try:
            parcela = Parcela.query.filter_by(codigo=codigo, activa=True).first_or_404()
            return parcela.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 500

@parcelas_ns.route('/cultivo/<int:cultivo_id>')
class ParcelasPorCultivo(Resource):
    @parcelas_ns.doc('obtener_parcelas_por_cultivo')
    @parcelas_ns.marshal_list_with(parcela_response)
    def get(self, cultivo_id):
        """Obtener todas las parcelas de un cultivo específico"""
        try:
            parcelas = Parcela.query.filter_by(cultivo_id=cultivo_id, activa=True).all()
            return [parcela.to_dict() for parcela in parcelas], 200
        except Exception as e:
            return {'error': str(e)}, 500

@parcelas_ns.route('/disponibles')
class ParcelasDisponibles(Resource):
    @parcelas_ns.doc('obtener_parcelas_disponibles')
    @parcelas_ns.marshal_list_with(parcela_response)
    def get(self):
        """Obtener parcelas sin cultivo asignado"""
        try:
            parcelas = Parcela.query.filter_by(cultivo_id=None, activa=True).all()
            return [parcela.to_dict() for parcela in parcelas], 200
        except Exception as e:
            return {'error': str(e)}, 500

@parcelas_ns.route('/estadisticas')
class ParcelasEstadisticas(Resource):
    @parcelas_ns.doc('obtener_estadisticas_parcelas')
    def get(self):
        """Obtener estadísticas generales de parcelas"""
        try:
            total_parcelas = Parcela.query.filter_by(activa=True).count()
            area_total = db.session.query(db.func.sum(Parcela.area_hectareas)).filter_by(activa=True).scalar() or 0
            parcelas_con_cultivo = Parcela.query.filter(Parcela.cultivo_id.isnot(None), Parcela.activa == True).count()
            parcelas_disponibles = total_parcelas - parcelas_con_cultivo
            
            # Distribución por tipo de suelo
            tipos_suelo = db.session.query(
                Parcela.tipo_suelo, 
                db.func.count(Parcela.id).label('cantidad')
            ).filter_by(activa=True).group_by(Parcela.tipo_suelo).all()
            
            return {
                'total_parcelas': total_parcelas,
                'area_total_hectareas': float(area_total),
                'parcelas_con_cultivo': parcelas_con_cultivo,
                'parcelas_disponibles': parcelas_disponibles,
                'distribucion_tipos_suelo': [
                    {'tipo': tipo[0] or 'No especificado', 'cantidad': tipo[1]} 
                    for tipo in tipos_suelo
                ]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500
