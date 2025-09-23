# 🚀 Guía de Despliegue en Railway

## Pasos para desplegar tu aplicación completa:

### 1. Preparar el proyecto ✅
Los archivos ya están listos:
- ✅ Procfile
- ✅ railway.json  
- ✅ nixpacks.toml
- ✅ app.py actualizado para producción
- ✅ CORS configurado para Railway

### 2. Subir a GitHub
```bash
git add .
git commit -m "Preparar para Railway - Backend y Frontend"
git push origin main
```

### 3. Desplegar Backend en Railway

#### 3.1 Crear cuenta y proyecto
1. Ve a https://railway.app
2. Conecta tu cuenta de GitHub
3. Crea "New Project" → "Deploy from GitHub repo"
4. Selecciona tu repositorio

#### 3.2 Configurar variables de entorno
En Railway dashboard → Variables:
```
FLASK_ENV=production
JWT_SECRET_KEY=control-agricola-super-secret-key-2024
```

#### 3.3 Agregar PostgreSQL
1. En tu proyecto Railway: "New Service" → "Database" → "PostgreSQL"
2. Railway configurará DATABASE_URL automáticamente

### 4. Desplegar Frontend en Railway

#### 4.1 Crear segundo servicio
1. En el mismo proyecto: "New Service" → "GitHub Repo"
2. Selecciona tu repositorio nuevamente
3. En Settings → "Root Directory" → `frontend`

#### 4.2 Configurar build del frontend
En Variables del servicio frontend:
```
VITE_API_URL=https://tu-backend.railway.app
```

### 5. URLs resultantes:
- **Backend:** https://control-agricola-backend.railway.app
- **Frontend:** https://control-agricola-frontend.railway.app  
- **API Docs:** https://control-agricola-backend.railway.app/docs/

## 🎯 Configuración del frontend local

Mientras despliegas, actualiza tu frontend local:

```bash
# En frontend/.env
VITE_API_URL=https://tu-backend.railway.app
```

## 🔧 Comandos útiles

```bash
# Ver logs en Railway
railway logs

# Conectar a base de datos
railway connect postgresql

# Variables de entorno
railway variables
```

## 📱 Resultado Final

Después del despliegue tendrás:

### 🌐 URLs Públicas (Accesibles desde Internet):
- **Aplicación Web:** https://tu-frontend.railway.app
- **API:** https://tu-backend.railway.app
- **Documentación:** https://tu-backend.railway.app/docs/

### 💻 URLs Locales (Para desarrollo):
- **Frontend:** http://localhost:3000
- **API:** http://localhost:5000

## 🎉 ¡Listo para Compartir!

Una vez desplegado, puedes compartir:

```
¡Hola! 👋

Mira mi Sistema de Control Agrícola:

🌐 Aplicación Web: https://tu-frontend.railway.app
📚 API: https://tu-backend.railway.app
📖 Documentación: https://tu-backend.railway.app/docs/

¡Funciona desde cualquier dispositivo en el mundo!
```

## 🆘 Solución de problemas

### Error de build:
- Verifica que requirements.txt esté actualizado
- Revisa los logs en Railway dashboard

### Error de conexión:
- Verifica que VITE_API_URL apunte a la URL correcta
- Revisa configuración CORS

### Error de base de datos:
- Verifica que PostgreSQL esté agregado
- Revisa que DATABASE_URL esté configurada
