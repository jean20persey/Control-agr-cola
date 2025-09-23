from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api, Resource, fields
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

# Configuración de base de datos para Railway
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Railway proporciona DATABASE_URL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Configuración local para desarrollo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456789@localhost:5432/control_agricola'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'control-agricola-secret-key-2024'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Importar e inicializar extensiones
from models import db
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
# Configurar CORS para desarrollo local
allowed_origins = [
    'http://localhost:3000', 
    'http://127.0.0.1:3000'
]

CORS(app, 
     origins=allowed_origins,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)

# Configurar API con documentación automática
api = Api(
    app,
    version='1.0',
    title='Control Agrícola API',
    description='API REST para gestión y análisis de producción agrícola',
    doc='/docs/'
)

# Importar y registrar rutas
from routes.cultivos import cultivos_ns
from routes.parcelas import parcelas_ns  
from routes.produccion import produccion_ns
from routes.analisis import analisis_ns

# Registrar namespaces
api.add_namespace(cultivos_ns, path='/cultivos')
api.add_namespace(parcelas_ns, path='/parcelas')
api.add_namespace(produccion_ns, path='/produccion')
api.add_namespace(analisis_ns, path='/analisis')

# Endpoint de salud de la API
@api.route('/health')
class HealthCheck(Resource):
    def get(self):
        """Verificar el estado de la API"""
        return {
            'status': 'OK',
            'message': 'API de Control Agrícola funcionando correctamente',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0'
        }

# Endpoint raíz
@app.route('/')
def index():
    return jsonify({
        'message': 'Bienvenido a la API de Control Agrícola',
        'version': '1.0',
        'documentation': '/docs/',
        'endpoints': {
            'health': '/health',
            'cultivos': '/cultivos',
            'parcelas': '/parcelas',
            'produccion': '/produccion',
            'analisis': '/analisis'
        }
    })

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint no encontrado',
        'message': 'La ruta solicitada no existe'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Ha ocurrido un error inesperado'
    }), 500

if __name__ == '__main__':
    # Importar modelos (después de la inicialización de la app)
    from models import Cultivo, Parcela, RegistroProduccion, PrediccionCosecha
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    # Configuración para desarrollo local
    port = 5000
    debug = True
    
    # Ejecutar la aplicación en localhost
    app.run(
        host='127.0.0.1',
        port=port,
        debug=debug
    )
