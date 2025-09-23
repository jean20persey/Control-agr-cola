# 🚀 Ngrok - Inicio Rápido

## 📋 Pasos para obtener tu URL pública:

### 1. Configurar Authtoken (Solo la primera vez)
```bash
# Ve a: https://dashboard.ngrok.com/get-started/your-authtoken
# Regístrate gratis y copia tu authtoken

# Configurar authtoken:
.\ngrok.exe config add-authtoken TU_AUTHTOKEN_AQUI
```

### 2. Iniciar Túnel Automático
```bash
python start_ngrok.py
```

### 3. Iniciar Servidores
```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend  
cd frontend
npm run dev
```

## 🌐 Tu URL Pública

Después de ejecutar `python start_ngrok.py`, verás algo como:

```
[SUCCESS] Túnel ngrok activo!
[URL] URL pública: https://abc123-def456.ngrok.io

[INFO] URLs de acceso:
   API Backend: https://abc123-def456.ngrok.io
   API Docs: https://abc123-def456.ngrok.io/docs/
   Panel Ngrok: http://localhost:4040
```

## 📱 Acceso desde Cualquier Dispositivo

Con la URL pública, cualquier persona puede acceder desde:
- **Teléfonos:** https://abc123-def456.ngrok.io
- **Tablets:** https://abc123-def456.ngrok.io  
- **Computadoras:** https://abc123-def456.ngrok.io
- **Desde cualquier país:** https://abc123-def456.ngrok.io

## 🔧 Comandos Útiles

```bash
# Ver túneles activos
.\ngrok.exe tunnel list

# Detener todos los túneles
.\ngrok.exe tunnel stop-all

# Ver panel web de ngrok
# http://localhost:4040
```

## ⚠️ Notas Importantes

- 🔄 **La URL cambia** cada vez que reinicias ngrok
- 🕐 **Mantén la ventana abierta** para que el túnel siga activo
- 🆓 **Plan gratuito:** Límites de conexiones y tiempo
- 🔒 **Solo para desarrollo:** No usar en producción

## 🆘 Solución de Problemas

### ❌ Error: "authtoken required"
```bash
# Configurar authtoken
.\ngrok.exe config add-authtoken TU_AUTHTOKEN_AQUI
```

### ❌ Error: "tunnel not found"  
```bash
# Reiniciar ngrok
python start_ngrok.py
```

### ❌ No aparece la URL
- Espera 10-15 segundos
- Revisa http://localhost:4040
- Verifica que el puerto 5000 esté libre

## 🎯 Ejemplo Completo

```bash
# 1. Configurar authtoken (solo primera vez)
.\ngrok.exe config add-authtoken 2abc123def456ghi789jkl

# 2. Iniciar túnel
python start_ngrok.py
# Resultado: https://abc123.ngrok.io

# 3. Iniciar backend (nueva terminal)
python app.py

# 4. Iniciar frontend (nueva terminal)  
cd frontend && npm run dev

# 5. ¡Listo! Accede desde cualquier dispositivo:
# https://abc123.ngrok.io
```
