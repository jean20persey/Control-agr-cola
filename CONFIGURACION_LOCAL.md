# 🌱 Control Agrícola - Configuración Local

Este documento explica cómo configurar y ejecutar el sistema Control Agrícola en modo local para desarrollo.

## 📋 Requisitos Previos

### 1. Software Necesario
- **Python 3.8+** con pip
- **Node.js 16+** con npm
- **PostgreSQL 12+**
- **Git** (opcional)

### 2. Base de Datos
Asegúrate de tener PostgreSQL ejecutándose con:
- **Host:** localhost
- **Puerto:** 5432
- **Base de datos:** control_agricola
- **Usuario:** postgres
- **Contraseña:** 123456789

```sql
-- Crear la base de datos (ejecutar en psql)
CREATE DATABASE control_agricola;
```

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias del Backend
```bash
# En el directorio raíz del proyecto
pip install -r requirements.txt
```

### 2. Instalar Dependencias del Frontend
```bash
# En el directorio frontend/
cd frontend
npm install
```

### 3. Configuración de Variables de Entorno
Los archivos de configuración ya están configurados para desarrollo local:

**Backend (app.py):**
- Host: `127.0.0.1` (localhost)
- Puerto: `5000`
- Base de datos: `postgresql://postgres:123456789@localhost:5432/control_agricola`
- CORS: Solo permite `localhost:3000`

**Frontend (.env.local):**
```env
VITE_API_URL=http://localhost:5000
VITE_PORT=3000
```

## 🎯 Ejecución del Sistema

### Opción 1: Script Automático (Recomendado)

#### En Windows:
```bash
# Doble clic en el archivo o ejecutar en cmd
start_local.bat
```

#### En Linux/Mac:
```bash
python start_local.py
```

### Opción 2: Manual

#### Terminal 1 - Backend:
```bash
# En el directorio raíz
python app.py
```

#### Terminal 2 - Frontend:
```bash
# En el directorio frontend/
cd frontend
npm run dev
```

## 🌐 Acceso al Sistema

Una vez iniciado, puedes acceder a:

- **🎨 Frontend:** http://localhost:3000
- **🔧 Backend API:** http://localhost:5000
- **📚 Documentación API:** http://localhost:5000/docs/
- **❤️ Health Check:** http://localhost:5000/health

## 🔧 Configuración Técnica

### Backend (Flask)
```python
# Configuración en app.py
app.run(
    host='127.0.0.1',  # Solo localhost
    port=5000,
    debug=True
)
```

### Frontend (Vite)
```typescript
// Configuración en vite.config.ts
server: {
  port: 3000,
  host: 'localhost',  // Solo localhost
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
    }
  }
}
```

### CORS
```python
# Solo permite acceso desde localhost
allowed_origins = [
    'http://localhost:3000', 
    'http://127.0.0.1:3000'
]
```

## 🛠️ Solución de Problemas

### Error de Base de Datos
```
❌ Error de conexión a la base de datos
```
**Solución:**
1. Verificar que PostgreSQL esté ejecutándose
2. Crear la base de datos `control_agricola`
3. Verificar credenciales (postgres/123456789)

### Error de Puerto Ocupado
```
❌ Port 5000 is already in use
```
**Solución:**
1. Cerrar otras aplicaciones que usen el puerto 5000
2. O cambiar el puerto en `app.py`

### Error de Dependencias
```
❌ ModuleNotFoundError: No module named 'flask'
```
**Solución:**
```bash
pip install -r requirements.txt
```

### Error de Node.js
```
❌ 'npm' is not recognized
```
**Solución:**
1. Instalar Node.js desde https://nodejs.org/
2. Reiniciar terminal/cmd

## 📁 Estructura de Archivos

```
Control_agricola/
├── app.py                 # Servidor Flask (Backend)
├── models.py             # Modelos de base de datos
├── requirements.txt      # Dependencias Python
├── start_local.py        # Script de inicio automático
├── start_local.bat       # Script Windows
├── CONFIGURACION_LOCAL.md # Esta documentación
├── frontend/
│   ├── src/
│   ├── package.json      # Dependencias Node.js
│   ├── vite.config.ts    # Configuración Vite
│   ├── .env.local        # Variables de entorno
│   └── .env.development  # Variables de desarrollo
└── routes/               # Rutas de la API
```

## 🔄 Diferencias con Configuración Externa

| Aspecto | Local | Externa |
|---------|-------|---------|
| Host Backend | `127.0.0.1` | `0.0.0.0` |
| Host Frontend | `localhost` | `0.0.0.0` |
| CORS | Solo localhost | Múltiples orígenes |
| Proxy | `localhost:5000` | URL externa/ngrok |
| Acceso | Solo desde tu PC | Desde cualquier dispositivo |

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs en la terminal
2. Verifica que todos los servicios estén ejecutándose
3. Consulta la documentación de la API en `/docs/`

---

**¡Listo para desarrollar! 🚀**
