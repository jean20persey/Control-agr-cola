#!/usr/bin/env python3
"""
Script para compartir la aplicación completa (frontend + backend) desde internet
"""
import subprocess
import time
import requests
import socket
import os

def get_local_ip():
    """Obtener IP local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.56"

def get_ngrok_url():
    """Obtener URL actual de ngrok"""
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=3)
        tunnels = response.json()
        
        if tunnels['tunnels']:
            return tunnels['tunnels'][0]['public_url']
        else:
            return None
    except:
        return None

def update_frontend_env(ngrok_url):
    """Actualizar .env del frontend"""
    env_content = f"""# Configuración para acceso desde internet
VITE_API_URL={ngrok_url}

# Configuración anterior (red local)
# VITE_API_URL=http://{get_local_ip()}:5000
"""
    
    with open('frontend/.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"[OK] Frontend configurado para: {ngrok_url}")

def main():
    print("=== Compartir Aplicación Completa ===\n")
    
    # Verificar si ngrok está corriendo
    ngrok_url = get_ngrok_url()
    
    if not ngrok_url:
        print("[ERROR] Ngrok no está corriendo o no tiene túneles activos")
        print("[INFO] Primero ejecuta: .\\ngrok.exe http 5000")
        return
    
    print(f"[FOUND] URL de ngrok: {ngrok_url}")
    
    # Actualizar configuración del frontend
    update_frontend_env(ngrok_url)
    
    print(f"\n[SUCCESS] ¡Configuración completada!")
    print(f"\n[SHARE] URLs para compartir:")
    print(f"   🌐 API Backend: {ngrok_url}")
    print(f"   📚 Documentación: {ngrok_url}/docs/")
    print(f"   💚 Health Check: {ngrok_url}/health")
    
    print(f"\n[FRONTEND] Para la interfaz web:")
    print(f"   🏠 Local: http://localhost:3000")
    print(f"   🌐 Red local: http://{get_local_ip()}:3000")
    
    print(f"\n[IMPORTANT] Cómo compartir:")
    print(f"   1. Backend API: Comparte {ngrok_url}")
    print(f"   2. Interfaz Web: Comparte http://{get_local_ip()}:3000")
    print(f"      (Solo funciona para dispositivos en tu red WiFi)")
    
    print(f"\n[ALTERNATIVE] Para acceso completo desde internet:")
    print(f"   - Usa servicios como Railway, Netlify, o Vercel")
    print(f"   - Ejecuta: python deploy_railway.py")
    
    print(f"\n[CURRENT] Estado actual:")
    print(f"   ✅ Backend: Accesible desde internet")
    print(f"   ✅ Frontend: Accesible desde red local")
    print(f"   ✅ API: Completamente funcional")

if __name__ == "__main__":
    main()
