#!/usr/bin/env python3
"""
Script para preparar el proyecto para despliegue en Railway
"""
import os
import json
from pathlib import Path

def create_procfile():
    """Crear Procfile para Railway"""
    procfile_content = """web: python app.py
"""
    
    with open('Procfile', 'w') as f:
        f.write(procfile_content)
    
    print("✅ Procfile creado")

def update_app_for_production():
    """Actualizar app.py para producción"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la línea del puerto y reemplazarla
        old_run = """    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )"""
        
        new_run = """    # Usar puerto de entorno para Railway
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )"""
        
        if old_run in content:
            content = content.replace(old_run, new_run)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ app.py actualizado para producción")
            return True
        else:
            print("⚠️  No se encontró la configuración del puerto para actualizar")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando app.py: {e}")
        return False

def create_railway_config():
    """Crear configuración específica para Railway"""
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python app.py",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 100,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ railway.json creado")

def update_database_config():
    """Actualizar configuración de base de datos para Railway"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la configuración de la base de datos
        old_db_config = "app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456789@localhost:5432/control_agricola'"
        
        new_db_config = """# Configuración de base de datos para Railway
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Railway proporciona DATABASE_URL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Configuración local para desarrollo
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456789@localhost:5432/control_agricola'"""
        
        if old_db_config in content:
            content = content.replace(old_db_config, new_db_config)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Configuración de base de datos actualizada para Railway")
            return True
        else:
            print("⚠️  No se encontró la configuración de base de datos para actualizar")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando configuración de base de datos: {e}")
        return False

def create_nixpacks_config():
    """Crear configuración para Nixpacks (build system de Railway)"""
    nixpacks_config = """[phases.setup]
nixPkgs = ['python39', 'postgresql']

[phases.install]
cmds = ['pip install -r requirements.txt']

[phases.build]
cmds = ['echo "Build completed"']

[start]
cmd = 'python app.py'
"""
    
    with open('nixpacks.toml', 'w') as f:
        f.write(nixpacks_config)
    
    print("✅ nixpacks.toml creado")

def update_cors_for_production():
    """Actualizar CORS para permitir dominios de Railway"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar configuración CORS actual
        old_cors = """CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://0.0.0.0:3000', 'http://192.168.1.56:3000'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)"""
        
        new_cors = """# Configurar CORS para producción y desarrollo
allowed_origins = [
    'http://localhost:3000', 
    'http://127.0.0.1:3000', 
    'http://0.0.0.0:3000', 
    'http://192.168.1.56:3000'
]

# Agregar dominios de Railway si están configurados
frontend_url = os.environ.get('FRONTEND_URL')
if frontend_url:
    allowed_origins.append(frontend_url)

# Permitir todos los dominios de Railway en desarrollo
if os.environ.get('RAILWAY_ENVIRONMENT'):
    allowed_origins.append('https://*.railway.app')

CORS(app, 
     origins=allowed_origins,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)"""
        
        if old_cors in content:
            content = content.replace(old_cors, new_cors)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ CORS actualizado para Railway")
            return True
        else:
            print("⚠️  No se encontró la configuración CORS para actualizar")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando CORS: {e}")
        return False

def create_env_example():
    """Crear archivo .env.example para Railway"""
    env_example = """# Variables de entorno para Railway

# Base de datos (Railway la proporciona automáticamente)
DATABASE_URL=postgresql://user:password@host:port/database

# Configuración de la aplicación
FLASK_ENV=production
JWT_SECRET_KEY=tu-clave-secreta-muy-segura-aqui

# URL del frontend (opcional)
FRONTEND_URL=https://tu-frontend.railway.app

# Puerto (Railway lo asigna automáticamente)
PORT=5000
"""
    
    with open('.env.railway.example', 'w') as f:
        f.write(env_example)
    
    print("✅ .env.railway.example creado")

def create_deployment_guide():
    """Crear guía de despliegue"""
    guide = """# 🚀 Guía de Despliegue en Railway

## Pasos para desplegar:

### 1. Preparar el proyecto
```bash
python deploy_railway.py
```

### 2. Subir a GitHub
```bash
git add .
git commit -m "Preparar para Railway"
git push origin main
```

### 3. Configurar Railway
1. Ve a https://railway.app
2. Conecta tu cuenta de GitHub
3. Crea nuevo proyecto desde GitHub
4. Selecciona tu repositorio

### 4. Configurar variables de entorno
En Railway dashboard:
- `FLASK_ENV=production`
- `JWT_SECRET_KEY=tu-clave-secreta-muy-segura`

### 5. Agregar base de datos
1. En Railway, agregar PostgreSQL plugin
2. Railway configurará DATABASE_URL automáticamente

### 6. Desplegar frontend
1. Crear nuevo servicio en Railway
2. Configurar build command: `npm run build`
3. Configurar start command: `npm run preview`
4. Configurar FRONTEND_URL en el backend

## URLs resultantes:
- Backend: https://tu-backend.railway.app
- Frontend: https://tu-frontend.railway.app
- API Docs: https://tu-backend.railway.app/docs/

## Configuración del frontend:
Actualizar `frontend/.env`:
```
VITE_API_URL=https://tu-backend.railway.app
```
"""
    
    with open('RAILWAY_DEPLOY.md', 'w') as f:
        f.write(guide)
    
    print("✅ RAILWAY_DEPLOY.md creado")

def main():
    print("=== Preparación para Despliegue en Railway ===\n")
    
    print("🚀 Preparando proyecto para Railway...")
    
    # Crear archivos necesarios
    create_procfile()
    create_railway_config()
    create_nixpacks_config()
    create_env_example()
    create_deployment_guide()
    
    # Actualizar configuraciones
    update_app_for_production()
    update_database_config()
    update_cors_for_production()
    
    print(f"\n✅ ¡Proyecto preparado para Railway!")
    print(f"\n📋 Próximos pasos:")
    print(f"   1. Sube el código a GitHub:")
    print(f"      git add .")
    print(f"      git commit -m 'Preparar para Railway'")
    print(f"      git push origin main")
    print(f"   2. Ve a https://railway.app y conecta tu repositorio")
    print(f"   3. Configura las variables de entorno")
    print(f"   4. Agrega PostgreSQL plugin")
    print(f"   5. ¡Tu API estará disponible en internet!")
    
    print(f"\n📖 Ver guía completa: RAILWAY_DEPLOY.md")
    print(f"🌐 Ver opciones adicionales: ACCESO_INTERNET.md")

if __name__ == "__main__":
    main()
