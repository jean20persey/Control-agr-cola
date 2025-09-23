# 🌾 Control Agrícola - Sistema de Gestión y Análisis de Producción Agrícola

<div align="center">

![Control Agrícola Logo](https://img.shields.io/badge/CONTROL%20AGR%C3%8DCOLA-Sistema%20de%20Gesti%C3%B3n%20Agr%C3%ADcola-1a9f0b?style=for-the-badge&logo=agriculture)

**Sistema completo de gestión agrícola con Django REST Framework y React + TypeScript**

[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django)](https://djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?style=flat&logo=typescript)](https://typescriptlang.org/)
[![Material-UI](https://img.shields.io/badge/Material--UI-5.14-0081CB?style=flat&logo=mui)](https://mui.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)](https://postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 🌾 Características Principales

### 🌱 **Gestión de Cultivos**
- CRUD completo para diferentes tipos de cultivos y variedades

## 🛠️ Tecnologías

### Backend
- **Django 5.2** - Framework web robusto
- **Django REST Framework 3.14** - API REST completa
- **PostgreSQL** - Base de datos relacional
- **JWT** - Autenticación segura
- **Python 3.8+** - Lenguaje de programación
- **JWT Authentication** - Autenticación segura
- **Pandas & NumPy** - Análisis de datos
- **Scikit-learn** - Machine Learning
- **SciPy** - Análisis estadístico

### 🎨 **Frontend**
- **React 19** - Biblioteca de interfaz de usuario
- **TypeScript** - JavaScript tipado
- **Material-UI (MUI)** - Componentes de diseño
- **Vite** - Build tool rápido
- **React Router** - Navegación SPA
- **Axios** - Cliente HTTP

### 🛠️ **Herramientas de Desarrollo**
- **Concurrently** - Ejecución paralela de procesos
- **Git** - Control de versiones
- **PostgreSQL** - Base de datos principal

## 📋 Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

## 🚀 Instalación y Configuración

### 🏠 Modo Local (Recomendado para Desarrollo)

#### Inicio Rápido
```bash
# Windows - Doble clic o ejecutar en cmd
start_local.bat

# Linux/Mac
python start_local.py
```

#### Configuración Manual

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Control_agricola
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias del backend
```bash
pip install -r requirements.txt
```

### 4. Instalar dependencias del frontend
```bash
cd frontend
npm install
```

### 5. Configurar PostgreSQL
1. Crear la base de datos:
```sql
CREATE DATABASE control_agricola;
```

2. Las credenciales están configuradas para desarrollo local:
```
postgresql://postgres:123456789@localhost:5432/control_agricola
```

### 6. Ejecutar el sistema

#### Opción A: Script Automático
```bash
python start_local.py
```

#### Opción B: Manual (2 terminales)
```bash
# Terminal 1 - Backend
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 🌐 Acceso Local
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **Documentación:** http://localhost:5000/docs/

📖 **Documentación completa:** [CONFIGURACION_LOCAL.md](CONFIGURACION_LOCAL.md)

## 📚 Documentación de la API

### Swagger UI
Accede a la documentación interactiva en: `http://localhost:5000/docs/`

### Endpoints Principales

#### 🌱 Cultivos (`/cultivos`)
- `GET /cultivos` - Listar todos los cultivos
- `POST /cultivos` - Crear nuevo cultivo
- `GET /cultivos/{id}` - Obtener cultivo específico
- `PUT /cultivos/{id}` - Actualizar cultivo
- `DELETE /cultivos/{id}` - Eliminar cultivo
- `GET /cultivos/buscar` - Buscar cultivos
- `GET /cultivos/tipos` - Obtener tipos de cultivos

#### 🏞️ Parcelas (`/parcelas`)
- `GET /parcelas` - Listar todas las parcelas
- `POST /parcelas` - Crear nueva parcela
- `GET /parcelas/{id}` - Obtener parcela específica
- `PUT /parcelas/{id}` - Actualizar parcela
- `DELETE /parcelas/{id}` - Eliminar parcela
- `GET /parcelas/codigo/{codigo}` - Buscar por código (acceso rápido)
- `GET /parcelas/cultivo/{cultivo_id}` - Parcelas por cultivo
- `GET /parcelas/estadisticas` - Estadísticas generales

#### 📊 Producción (`/produccion`)
- `GET /produccion` - Listar registros con filtros
- `POST /produccion` - Crear registro de producción
- `GET /produccion/{id}` - Obtener registro específico
- `PUT /produccion/{id}` - Actualizar registro
- `DELETE /produccion/{id}` - Eliminar registro
- `GET /produccion/anomalias` - Registros con anomalías
- `GET /produccion/estadisticas/temporada/{temporada}` - Stats por temporada
- `GET /produccion/series-temporales/{parcela_id}` - Serie temporal

#### 🔬 Análisis (`/analisis`)
- `GET /analisis/estadisticas-generales` - Estadísticas del sistema
- `POST /analisis/comparar-variedades` - Comparación estadística
- `GET /analisis/series-temporales/analisis/{parcela_id}` - Análisis temporal
- `POST /analisis/predicciones/crear` - Crear predicción
- `GET /analisis/predicciones` - Listar predicciones
- `GET /analisis/clasificacion-rendimiento` - Clasificar parcelas

## 🧪 Pruebas con Postman

### Colección de Postman
Importa la siguiente colección para probar todos los endpoints:

#### 1. Crear Cultivo
```json
POST /cultivos
{
    "nombre": "Maíz Amarillo",
    "variedad": "Pioneer 30F35",
    "tipo": "cereales",
    "ciclo_dias": 120,
    "rendimiento_esperado": 8500.0,
    "descripcion": "Maíz híbrido de alto rendimiento"
}
```

#### 2. Crear Parcela
```json
POST /parcelas
{
    "codigo": "P001",
    "nombre": "Parcela Norte",
    "area_hectareas": 5.5,
    "ubicacion_lat": -12.0464,
    "ubicacion_lng": -77.0428,
    "tipo_suelo": "Franco arcilloso",
    "ph_suelo": 6.8,
    "cultivo_id": 1,
    "fecha_siembra": "2024-03-15"
}
```

#### 3. Registrar Producción
```json
POST /produccion
{
    "parcela_id": 1,
    "cultivo_id": 1,
    "fecha_registro": "2024-07-15",
    "temporada": "2024-1",
    "cantidad_kg": 42500.0,
    "calidad": "A",
    "temperatura_promedio": 24.5,
    "precipitacion_mm": 85.2,
    "humedad_relativa": 68.0
}
```

#### 4. Comparar Variedades
```json
POST /analisis/comparar-variedades
{
    "cultivo_id_1": 1,
    "cultivo_id_2": 2,
    "temporada": "2024-1"
}
```

#### 5. Crear Predicción
```json
POST /analisis/predicciones/crear
{
    "parcela_id": 1,
    "cultivo_id": 1,
    "temporada_objetivo": "2024-2",
    "modelo": "random_forest"
}
```

### Variables de Entorno para Postman
```
base_url: http://localhost:5000
```

## 🔍 Funcionalidades Avanzadas

### Análisis Estadístico
- **Pruebas de Hipótesis**: Comparación de medias entre variedades
- **Análisis de Varianza**: Evaluación de diferencias significativas
- **Detección de Outliers**: Identificación de valores atípicos
- **Coeficiente de Variación**: Medida de consistencia en el rendimiento

### Modelos Predictivos
- **Regresión Lineal**: Para tendencias simples
- **Random Forest**: Para patrones complejos
- **Intervalos de Confianza**: Rangos de predicción
- **Validación Cruzada**: Evaluación de precisión del modelo

### Optimización de Rendimiento
- **Índices Hash**: Acceso rápido por código de parcela
- **Índices Compuestos**: Consultas optimizadas por fecha y parcela
- **Paginación**: Manejo eficiente de grandes volúmenes de datos
- **Cache**: Almacenamiento temporal de consultas frecuentes

## 🏗️ Arquitectura del Sistema

```
Control_agricola/
├── app.py                    # Aplicación Flask principal
├── models.py                 # Modelos de base de datos
├── requirements.txt          # Dependencias Python
├── .env                     # Variables de entorno
├── start_local.bat          # Script de inicio Windows
├── start_local_simple.py    # Script de inicio automático
├── routes/                  # Endpoints organizados
│   ├── __init__.py
│   ├── cultivos.py          # CRUD de cultivos
│   ├── parcelas.py          # CRUD de parcelas
│   ├── produccion.py        # Registro de producción
│   └── analisis.py          # Análisis y predicciones
├── frontend/                # Aplicación React + TypeScript
│   ├── src/
│   ├── package.json         # Dependencias Node.js
│   ├── vite.config.ts       # Configuración Vite
│   └── .env.local           # Variables de entorno frontend
├── CONFIGURACION_LOCAL.md   # Guía de configuración local
└── README.md               # Documentación principal
```

## 🌐 Configuración para Producción

Para desplegar el sistema en producción, considera las siguientes opciones:

### ☁️ Servicios en la Nube
- **Heroku**: Para aplicaciones Flask + React
- **Railway**: Despliegue automático desde Git
- **DigitalOcean**: VPS con control completo
- **AWS/GCP**: Servicios empresariales

### 🏠 Servidor Propio
- Configurar servidor web (Nginx/Apache)
- Usar WSGI server (Gunicorn)
- Configurar SSL/TLS
- Implementar base de datos PostgreSQL

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/base_datos

# Aplicación
FLASK_ENV=production  # para producción
FLASK_DEBUG=False     # para producción

# Seguridad
JWT_SECRET_KEY=tu-clave-secreta-muy-segura
```

### Configuración de Producción
Para despliegue en producción, considera:
- Usar un servidor WSGI como Gunicorn
- Configurar un proxy reverso (Nginx)
- Implementar SSL/TLS
- Configurar logging apropiado
- Usar variables de entorno seguras

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**Desarrollado para el control y análisis inteligente de producción agrícola** 🌾
