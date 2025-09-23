# 📱 Acceso Externo - Control Agrícola

Esta guía te ayudará a configurar el sistema para que sea accesible desde otros dispositivos en tu red local (teléfonos, tablets, otras computadoras).

## 🚀 Configuración Automática (Recomendado)

### Opción 1: Script Automático
```bash
python start_external.py
```

Este script:
- ✅ Detecta automáticamente tu IP local
- ✅ Crea el archivo `.env` en el frontend
- ✅ Actualiza la configuración CORS
- ✅ Te muestra las URLs de acceso
- ✅ Opcionalmente inicia el backend

### Opción 2: Solo Obtener IP
```bash
python get_ip.py
```

## ⚙️ Configuración Manual

### 1. Obtener tu IP Local

**Windows:**
```cmd
ipconfig
```
Busca tu "Dirección IPv4" (ejemplo: 192.168.1.100)

**Linux/Mac:**
```bash
ifconfig
# o
ip addr show
```

### 2. Configurar Frontend

Crea el archivo `frontend/.env`:
```env
VITE_API_URL=http://TU_IP_AQUI:5000
```

Ejemplo:
```env
VITE_API_URL=http://192.168.1.100:5000
```

### 3. Actualizar CORS (Opcional)

En `app.py`, línea 28-32, agrega tu IP:
```python
CORS(app, 
     origins=[
         'http://localhost:3000', 
         'http://127.0.0.1:3000', 
         'http://0.0.0.0:3000',
         'http://TU_IP_AQUI:3000'  # Agregar esta línea
     ],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)
```

## 🚦 Iniciar el Sistema

### 1. Iniciar Backend
```bash
python app.py
```

### 2. Iniciar Frontend
```bash
cd frontend
npm run dev
```

## 📱 URLs de Acceso

Reemplaza `TU_IP` con tu IP local (ejemplo: 192.168.1.100):

- **Frontend (App Principal):** `http://TU_IP:3000`
- **API Backend:** `http://TU_IP:5000`
- **Documentación API:** `http://TU_IP:5000/docs/`

## 🔧 Solución de Problemas

### ❌ No puedo acceder desde otros dispositivos

1. **Verificar Firewall:**
   - Windows: Permitir puertos 3000 y 5000 en Windows Defender
   - Mac: Verificar configuración en Preferencias del Sistema > Seguridad
   - Linux: Configurar iptables o ufw

2. **Verificar Red:**
   - Todos los dispositivos deben estar en la misma red WiFi/LAN
   - Algunos routers bloquean comunicación entre dispositivos

3. **Verificar IP:**
   - La IP puede cambiar si usas DHCP
   - Ejecuta `python get_ip.py` para verificar la IP actual

### ❌ Error de CORS

Si ves errores de CORS en la consola del navegador:

1. Verifica que la IP esté en la configuración CORS de `app.py`
2. Reinicia el backend después de cambios
3. Limpia la caché del navegador

### ❌ Error de conexión API

1. Verifica que el archivo `.env` tenga la IP correcta
2. Asegúrate de que el backend esté corriendo en puerto 5000
3. Verifica que no haya otro servicio usando el puerto

## 🔒 Consideraciones de Seguridad

⚠️ **Importante:** Esta configuración es solo para desarrollo y redes locales confiables.

Para producción:
- Usar HTTPS
- Configurar autenticación robusta
- Implementar rate limiting
- Usar un servidor web como Nginx
- Configurar firewall apropiado

## 📋 Comandos Útiles

```bash
# Ver IP actual
python get_ip.py

# Configurar automáticamente
python start_external.py

# Verificar puertos en uso
netstat -an | findstr :3000
netstat -an | findstr :5000

# Reiniciar servicios
# Ctrl+C para detener
# python app.py para reiniciar backend
# npm run dev para reiniciar frontend
```

## 📞 Soporte

Si tienes problemas:

1. Ejecuta `python get_ip.py` para diagnosticar
2. Verifica que todos los servicios estén corriendo
3. Revisa los logs en la consola para errores específicos
4. Asegúrate de que las dependencias estén instaladas:
   - `pip install -r requirements.txt`
   - `cd frontend && npm install`
