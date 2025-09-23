from flask_sqlalchemy import SQLAlchemy

# Crear instancia de db que será inicializada por la app
db = SQLAlchemy()
from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

class Cultivo(db.Model):
    """Modelo para gestión de cultivos"""
    __tablename__ = 'cultivos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    variedad = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # cereales, hortalizas, frutales, etc.
    ciclo_dias = db.Column(db.Integer, nullable=False)  # duración del ciclo en días
    rendimiento_esperado = db.Column(db.Float, nullable=False)  # kg/hectárea
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    parcelas = db.relationship('Parcela', backref='cultivo', lazy=True)
    registros_produccion = db.relationship('RegistroProduccion', backref='cultivo', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'variedad': self.variedad,
            'tipo': self.tipo,
            'ciclo_dias': self.ciclo_dias,
            'rendimiento_esperado': self.rendimiento_esperado,
            'descripcion': self.descripcion,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }

class Parcela(db.Model):
    """Modelo para gestión de parcelas - con índices hash para acceso rápido"""
    __tablename__ = 'parcelas'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), nullable=False, unique=True, index=True)  # Índice hash
    nombre = db.Column(db.String(100), nullable=False)
    area_hectareas = db.Column(db.Float, nullable=False)
    ubicacion_lat = db.Column(db.Float)
    ubicacion_lng = db.Column(db.Float)
    tipo_suelo = db.Column(db.String(50))
    ph_suelo = db.Column(db.Float)
    cultivo_id = db.Column(db.Integer, db.ForeignKey('cultivos.id'), nullable=True)
    fecha_siembra = db.Column(db.Date)
    fecha_cosecha_estimada = db.Column(db.Date)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    registros_produccion = db.relationship('RegistroProduccion', backref='parcela', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'area_hectareas': self.area_hectareas,
            'ubicacion': {
                'lat': self.ubicacion_lat,
                'lng': self.ubicacion_lng
            },
            'tipo_suelo': self.tipo_suelo,
            'ph_suelo': self.ph_suelo,
            'cultivo_id': self.cultivo_id,
            'fecha_siembra': self.fecha_siembra.isoformat() if self.fecha_siembra else None,
            'fecha_cosecha_estimada': self.fecha_cosecha_estimada.isoformat() if self.fecha_cosecha_estimada else None,
            'activa': self.activa,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }

class RegistroProduccion(db.Model):
    """Modelo para registro y análisis de producción"""
    __tablename__ = 'registros_produccion'
    
    id = db.Column(db.Integer, primary_key=True)
    parcela_id = db.Column(db.Integer, db.ForeignKey('parcelas.id'), nullable=False, index=True)
    cultivo_id = db.Column(db.Integer, db.ForeignKey('cultivos.id'), nullable=False, index=True)
    fecha_registro = db.Column(db.Date, nullable=False, index=True)  # Para series temporales
    temporada = db.Column(db.String(20), nullable=False, index=True)  # ej: "2024-1", "2024-2"
    
    # Datos de producción
    cantidad_kg = db.Column(db.Float, nullable=False)
    rendimiento_hectarea = db.Column(db.Float, nullable=False)  # kg/hectárea
    calidad = db.Column(db.String(20))  # A, B, C, etc.
    
    # Condiciones ambientales
    temperatura_promedio = db.Column(db.Float)
    precipitacion_mm = db.Column(db.Float)
    humedad_relativa = db.Column(db.Float)
    
    # Datos para análisis estadístico
    desviacion_esperada = db.Column(db.Float)  # Diferencia vs rendimiento esperado
    anomalia_detectada = db.Column(db.Boolean, default=False)
    notas_anomalia = db.Column(db.Text)
    
    # Metadatos
    datos_adicionales = db.Column(JSONB)  # Para datos flexibles
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'parcela_id': self.parcela_id,
            'cultivo_id': self.cultivo_id,
            'fecha_registro': self.fecha_registro.isoformat(),
            'temporada': self.temporada,
            'cantidad_kg': self.cantidad_kg,
            'rendimiento_hectarea': self.rendimiento_hectarea,
            'calidad': self.calidad,
            'condiciones_ambientales': {
                'temperatura_promedio': self.temperatura_promedio,
                'precipitacion_mm': self.precipitacion_mm,
                'humedad_relativa': self.humedad_relativa
            },
            'analisis': {
                'desviacion_esperada': self.desviacion_esperada,
                'anomalia_detectada': self.anomalia_detectada,
                'notas_anomalia': self.notas_anomalia
            },
            'datos_adicionales': self.datos_adicionales,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }

class PrediccionCosecha(db.Model):
    """Modelo para almacenar predicciones de cosechas futuras"""
    __tablename__ = 'predicciones_cosecha'
    
    id = db.Column(db.Integer, primary_key=True)
    parcela_id = db.Column(db.Integer, db.ForeignKey('parcelas.id'), nullable=False)
    cultivo_id = db.Column(db.Integer, db.ForeignKey('cultivos.id'), nullable=False)
    fecha_prediccion = db.Column(db.Date, nullable=False)
    temporada_objetivo = db.Column(db.String(20), nullable=False)
    
    # Predicciones
    rendimiento_predicho = db.Column(db.Float, nullable=False)
    confianza_prediccion = db.Column(db.Float, nullable=False)  # 0-1
    rango_minimo = db.Column(db.Float)
    rango_maximo = db.Column(db.Float)
    
    # Modelo utilizado
    modelo_utilizado = db.Column(db.String(50))  # linear_regression, xgboost, etc.
    parametros_modelo = db.Column(JSONB)
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'parcela_id': self.parcela_id,
            'cultivo_id': self.cultivo_id,
            'fecha_prediccion': self.fecha_prediccion.isoformat(),
            'temporada_objetivo': self.temporada_objetivo,
            'prediccion': {
                'rendimiento_predicho': self.rendimiento_predicho,
                'confianza': self.confianza_prediccion,
                'rango_minimo': self.rango_minimo,
                'rango_maximo': self.rango_maximo
            },
            'modelo': {
                'tipo': self.modelo_utilizado,
                'parametros': self.parametros_modelo
            },
            'fecha_creacion': self.fecha_creacion.isoformat()
        }

# Índices compuestos para optimizar consultas de series temporales
Index('idx_produccion_temporal', RegistroProduccion.parcela_id, RegistroProduccion.fecha_registro)
Index('idx_produccion_temporada', RegistroProduccion.cultivo_id, RegistroProduccion.temporada)
Index('idx_parcela_codigo_hash', Parcela.codigo)  # Índice hash para acceso rápido
