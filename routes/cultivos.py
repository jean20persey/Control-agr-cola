from flask import request, jsonify
from flask_restx import Resource, fields
from app import api, db
from models import Cultivo

# Namespace para cultivos
cultivos_ns = api.namespace('cultivos', description='Gestión de cultivos')

# Modelos para documentación automática
cultivo_model = api.model('Cultivo', {
    'nombre': fields.String(required=True, description='Nombre del cultivo'),
    'variedad': fields.String(required=True, description='Variedad del cultivo'),
    'tipo': fields.String(required=True, description='Tipo de cultivo (cereales, hortalizas, etc.)'),
    'ciclo_dias': fields.Integer(required=True, description='Duración del ciclo en días'),
    'rendimiento_esperado': fields.Float(required=True, description='Rendimiento esperado en kg/hectárea'),
    'descripcion': fields.String(description='Descripción del cultivo')
})

cultivo_response = api.model('CultivoResponse', {
    'id': fields.Integer(description='ID del cultivo'),
    'nombre': fields.String(description='Nombre del cultivo'),
    'variedad': fields.String(description='Variedad del cultivo'),
    'tipo': fields.String(description='Tipo de cultivo'),
    'ciclo_dias': fields.Integer(description='Duración del ciclo en días'),
    'rendimiento_esperado': fields.Float(description='Rendimiento esperado en kg/hectárea'),
    'descripcion': fields.String(description='Descripción del cultivo'),
    'activo': fields.Boolean(description='Estado del cultivo'),
    'fecha_creacion': fields.String(description='Fecha de creación')
})

@cultivos_ns.route('/')
class CultivosList(Resource):
    @cultivos_ns.doc('listar_cultivos')
    @cultivos_ns.marshal_list_with(cultivo_response)
    def get(self):
        """Obtener todos los cultivos"""
        try:
            cultivos = Cultivo.query.filter_by(activo=True).all()
            return [cultivo.to_dict() for cultivo in cultivos], 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @cultivos_ns.doc('crear_cultivo')
    @cultivos_ns.expect(cultivo_model)
    @cultivos_ns.marshal_with(cultivo_response, code=201)
    def post(self):
        """Crear un nuevo cultivo"""
        try:
            data = request.get_json()
            
            # Validar que no exista un cultivo con el mismo nombre
            if Cultivo.query.filter_by(nombre=data['nombre']).first():
                return {'error': 'Ya existe un cultivo con ese nombre'}, 400
            
            cultivo = Cultivo(
                nombre=data['nombre'],
                variedad=data['variedad'],
                tipo=data['tipo'],
                ciclo_dias=data['ciclo_dias'],
                rendimiento_esperado=data['rendimiento_esperado'],
                descripcion=data.get('descripcion', '')
            )
            
            db.session.add(cultivo)
            db.session.commit()
            
            return cultivo.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@cultivos_ns.route('/<int:cultivo_id>')
class CultivoDetail(Resource):
    @cultivos_ns.doc('obtener_cultivo')
    @cultivos_ns.marshal_with(cultivo_response)
    def get(self, cultivo_id):
        """Obtener un cultivo específico"""
        try:
            cultivo = Cultivo.query.get_or_404(cultivo_id)
            return cultivo.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @cultivos_ns.doc('actualizar_cultivo')
    @cultivos_ns.expect(cultivo_model)
    @cultivos_ns.marshal_with(cultivo_response)
    def put(self, cultivo_id):
        """Actualizar un cultivo"""
        try:
            cultivo = Cultivo.query.get_or_404(cultivo_id)
            data = request.get_json()
            
            # Validar nombre único (excluyendo el cultivo actual)
            existing = Cultivo.query.filter(
                Cultivo.nombre == data['nombre'],
                Cultivo.id != cultivo_id
            ).first()
            
            if existing:
                return {'error': 'Ya existe un cultivo con ese nombre'}, 400
            
            cultivo.nombre = data['nombre']
            cultivo.variedad = data['variedad']
            cultivo.tipo = data['tipo']
            cultivo.ciclo_dias = data['ciclo_dias']
            cultivo.rendimiento_esperado = data['rendimiento_esperado']
            cultivo.descripcion = data.get('descripcion', cultivo.descripcion)
            
            db.session.commit()
            return cultivo.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @cultivos_ns.doc('eliminar_cultivo')
    def delete(self, cultivo_id):
        """Eliminar (desactivar) un cultivo"""
        try:
            cultivo = Cultivo.query.get_or_404(cultivo_id)
            cultivo.activo = False
            db.session.commit()
            return {'message': 'Cultivo eliminado correctamente'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

@cultivos_ns.route('/tipos')
class CultivosTipos(Resource):
    @cultivos_ns.doc('obtener_tipos_cultivos')
    def get(self):
        """Obtener tipos de cultivos disponibles"""
        try:
            tipos = db.session.query(Cultivo.tipo).distinct().all()
            return {'tipos': [tipo[0] for tipo in tipos]}, 200
        except Exception as e:
            return {'error': str(e)}, 500

@cultivos_ns.route('/buscar')
class CultivosBuscar(Resource):
    @cultivos_ns.doc('buscar_cultivos')
    @cultivos_ns.param('q', 'Término de búsqueda')
    @cultivos_ns.param('tipo', 'Filtrar por tipo de cultivo')
    def get(self):
        """Buscar cultivos por nombre, variedad o tipo"""
        try:
            query = request.args.get('q', '')
            tipo = request.args.get('tipo', '')
            
            cultivos_query = Cultivo.query.filter_by(activo=True)
            
            if query:
                cultivos_query = cultivos_query.filter(
                    db.or_(
                        Cultivo.nombre.ilike(f'%{query}%'),
                        Cultivo.variedad.ilike(f'%{query}%')
                    )
                )
            
            if tipo:
                cultivos_query = cultivos_query.filter_by(tipo=tipo)
            
            cultivos = cultivos_query.all()
            return [cultivo.to_dict() for cultivo in cultivos], 200
        except Exception as e:
            return {'error': str(e)}, 500
