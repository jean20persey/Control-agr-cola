# 🌐 Acceso desde Internet - Control Agrícola

Esta guía te ayudará a configurar el sistema para que sea accesible desde **cualquier lugar del mundo** a través de internet, no solo desde tu red local.

## 🚀 Opción 1: Ngrok (Recomendada para Desarrollo)

### ✅ Ventajas:
- ⚡ Configuración en minutos
- 🔒 Túnel seguro HTTPS automático
- 🆓 Plan gratuito disponible
- 🔧 No requiere configurar router

### ⚠️ Limitaciones:
- 🕐 Túnel temporal (se reinicia al cerrar)
- 📊 Límites en plan gratuito
- 🌐 URL cambia en cada reinicio

### 📋 Configuración Automática:

```bash
# Ejecutar script automático
python setup_internet_access.py
```

### 📋 Configuración Manual:

#### 1. Instalar Ngrok
```bash
# Descargar desde: https://ngrok.com/download
# O usar el script automático
```

#### 2. Configurar Authtoken
```bash
# 1. Registrarse en https://dashboard.ngrok.com/
# 2. Obtener authtoken
# 3. Configurar:
ngrok config add-authtoken TU_AUTHTOKEN_AQUI
```

#### 3. Iniciar Túnel
```bash
# Terminal 1: Iniciar backend
python app.py

# Terminal 2: Iniciar túnel ngrok
ngrok http 5000
```

#### 4. Configurar Frontend
Crear/actualizar `frontend/.env`:
```env
VITE_API_URL=https://abc123.ngrok.io
```

#### 5. Actualizar CORS
En `app.py`, agregar la URL de ngrok:
```python
CORS(app, 
     origins=[
         'http://localhost:3000',
         'https://abc123.ngrok.io'  # URL de ngrok
     ])
```

## 🏠 Opción 2: Port Forwarding

### ✅ Ventajas:
- 🆓 Completamente gratuito
- 🔄 Permanente (no se reinicia)
- 🎯 Control total

### ⚠️ Limitaciones:
- 🔧 Requiere configurar router
- 🔒 Necesita configurar seguridad
- 🌐 Requiere IP pública estática

### 📋 Configuración:

#### 1. Obtener IP Pública
```bash
# Verificar tu IP pública
curl ifconfig.me
```

#### 2. Configurar Router
1. Acceder a configuración del router (ej: 192.168.1.1)
2. Buscar "Port Forwarding" o "Virtual Servers"
3. Agregar reglas:
   - Puerto externo: 5000 → IP interna: 192.168.1.56:5000
   - Puerto externo: 3000 → IP interna: 192.168.1.56:3000

#### 3. Configurar Frontend
```env
VITE_API_URL=http://TU_IP_PUBLICA:5000
```

#### 4. Configurar Firewall
```bash
# Windows Defender: Permitir puertos 3000 y 5000
# Router: Abrir puertos en firewall
```

## ☁️ Opción 3: Servicios en la Nube

### Plataformas Recomendadas:

#### 🚀 Railway (Recomendada)
- ✅ Fácil despliegue
- ✅ Base de datos incluida
- ✅ HTTPS automático
- 💰 Plan gratuito generoso

#### 🟣 Heroku
- ✅ Muy popular
- ✅ Muchos addons
- 💰 Plan gratuito limitado

#### 🌊 DigitalOcean App Platform
- ✅ Escalable
- ✅ Buen rendimiento
- 💰 Desde $5/mes

### 📋 Despliegue en Railway:

#### 1. Preparar Proyecto
```bash
# Crear Procfile
echo "web: python app.py" > Procfile

# Actualizar app.py para usar puerto de entorno
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

#### 2. Desplegar
1. Conectar repositorio GitHub a Railway
2. Configurar variables de entorno
3. Desplegar automáticamente

## 🔒 Consideraciones de Seguridad

### ⚠️ IMPORTANTE para Acceso desde Internet:

#### 1. Autenticación Robusta
```python
# Implementar JWT con expiración corta
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Requerir autenticación en todos los endpoints
@jwt_required()
def protected_endpoint():
    pass
```

#### 2. Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)
```

#### 3. HTTPS Obligatorio
```python
# Forzar HTTPS en producción
@app.before_request
def force_https():
    if not request.is_secure and app.env != 'development':
        return redirect(request.url.replace('http://', 'https://'))
```

#### 4. Validación de Entrada
```python
# Validar todos los inputs
from marshmallow import Schema, fields, validate

class CultivoSchema(Schema):
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # ... más validaciones
```

#### 5. Logging y Monitoreo
```python
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log de accesos
@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.url} from {request.remote_addr}")
```

## 🚦 Comandos de Inicio

### Opción 1: Ngrok
```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Túnel
python setup_internet_access.py

# Terminal 3: Frontend
cd frontend && npm run dev
```

### Opción 2: Port Forwarding
```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend
cd frontend && npm run dev

# Acceso: http://TU_IP_PUBLICA:3000
```

## 📱 URLs de Acceso

### Con Ngrok:
- **Frontend:** La URL que muestre Vite (ej: http://localhost:3000)
- **API:** https://abc123.ngrok.io
- **Docs:** https://abc123.ngrok.io/docs/

### Con Port Forwarding:
- **Frontend:** http://TU_IP_PUBLICA:3000
- **API:** http://TU_IP_PUBLICA:5000
- **Docs:** http://TU_IP_PUBLICA:5000/docs/

### Con Servicios en la Nube:
- **Frontend:** https://tu-app.railway.app
- **API:** https://tu-api.railway.app
- **Docs:** https://tu-api.railway.app/docs/

## 🔧 Solución de Problemas

### ❌ Ngrok no funciona
1. Verificar authtoken configurado
2. Comprobar límites del plan gratuito
3. Reiniciar túnel

### ❌ Port Forwarding no funciona
1. Verificar configuración del router
2. Comprobar firewall local y del router
3. Verificar IP pública

### ❌ Errores de CORS
1. Agregar URL pública a configuración CORS
2. Reiniciar backend después de cambios
3. Limpiar caché del navegador

## 💡 Recomendaciones

### Para Desarrollo:
- 🚀 Usar **Ngrok** para pruebas rápidas
- 🔒 Implementar autenticación básica
- 📊 Monitorear uso y accesos

### Para Producción:
- ☁️ Usar **servicios en la nube** profesionales
- 🔐 Implementar seguridad completa
- 📈 Configurar monitoreo y alertas
- 💾 Configurar backups automáticos

### Para Demostración:
- 🚇 **Ngrok** es perfecto para mostrar el proyecto
- 📱 Funciona en cualquier dispositivo con internet
- 🔗 Compartir URL temporal con otros

## 📞 Soporte

Si tienes problemas:
1. Ejecutar `python setup_internet_access.py` para diagnóstico
2. Verificar logs del backend y frontend
3. Comprobar configuración de red y firewall
4. Revisar documentación de la plataforma elegida
