#!/usr/bin/env python3
"""
Script para configurar acceso desde internet usando diferentes métodos
"""
import subprocess
import sys
import os
import requests
import json
from pathlib import Path

def check_ngrok_installed():
    """Verifica si ngrok está instalado"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Ngrok ya esta instalado")
            return True
        else:
            print("[ERROR] Ngrok no esta instalado")
            return False
    except FileNotFoundError:
        print("[ERROR] Ngrok no esta instalado")
        return False

def install_ngrok():
    """Instala ngrok automáticamente"""
    print("[DOWNLOAD] Descargando e instalando ngrok...")
    
    try:
        # Descargar ngrok para Windows
        import zipfile
        import urllib.request
        
        ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
        ngrok_zip = "ngrok.zip"
        
        print("[DOWNLOAD] Descargando ngrok...")
        urllib.request.urlretrieve(ngrok_url, ngrok_zip)
        
        print("[EXTRACT] Extrayendo ngrok...")
        with zipfile.ZipFile(ngrok_zip, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Limpiar archivo zip
        os.remove(ngrok_zip)
        
        print("[OK] Ngrok instalado correctamente")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error instalando ngrok: {e}")
        print("[INFO] Instala manualmente desde: https://ngrok.com/download")
        return False

def setup_ngrok_auth():
    """Configura la autenticación de ngrok"""
    print("\n[CONFIG] Configuracion de Ngrok:")
    print("1. Ve a https://dashboard.ngrok.com/get-started/your-authtoken")
    print("2. Regístrate o inicia sesión")
    print("3. Copia tu authtoken")
    
    authtoken = input("\n[INPUT] Pega tu authtoken de ngrok aqui: ").strip()
    
    if authtoken:
        try:
            result = subprocess.run(['ngrok', 'config', 'add-authtoken', authtoken], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("[OK] Authtoken configurado correctamente")
                return True
            else:
                print(f"[ERROR] Error configurando authtoken: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return False
    else:
        print("[ERROR] No se proporciono authtoken")
        return False

def start_ngrok_tunnel(port=5000):
    """Inicia el túnel de ngrok"""
    print(f"\n[TUNNEL] Iniciando tunel ngrok para puerto {port}...")
    
    try:
        # Iniciar ngrok en background
        process = subprocess.Popen(['ngrok', 'http', str(port)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Esperar un poco para que ngrok se inicie
        import time
        time.sleep(3)
        
        # Obtener la URL pública
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            tunnels = response.json()
            
            if tunnels['tunnels']:
                public_url = tunnels['tunnels'][0]['public_url']
                print(f"[OK] Tunel ngrok activo!")
                print(f"[URL] URL publica: {public_url}")
                return public_url, process
            else:
                print("[ERROR] No se pudo obtener la URL publica")
                return None, process
                
        except Exception as e:
            print(f"[WARNING] Tunel iniciado pero no se pudo obtener URL automaticamente")
            print(f"   Revisa http://localhost:4040 para ver la URL")
            return "check_localhost_4040", process
            
    except Exception as e:
        print(f"[ERROR] Error iniciando tunel: {e}")
        return None, None

def update_frontend_config(public_url):
    """Actualiza la configuración del frontend con la URL pública"""
    if not public_url or public_url == "check_localhost_4040":
        print("[WARNING] No se pudo actualizar automaticamente la configuracion del frontend")
        return False
    
    try:
        frontend_env = Path("frontend/.env")
        
        # Crear contenido del .env
        env_content = f"""# Configuración para acceso desde internet
VITE_API_URL={public_url}

# Configuración anterior (red local)
# VITE_API_URL=http://192.168.1.56:5000
"""
        
        with open(frontend_env, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"[OK] Frontend configurado para usar: {public_url}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error actualizando configuracion del frontend: {e}")
        return False

def update_cors_config(public_url):
    """Actualiza CORS para permitir la URL pública"""
    if not public_url or public_url == "check_localhost_4040":
        print("[WARNING] Actualiza manualmente CORS en app.py con la URL de ngrok")
        return False
    
    try:
        # Leer app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la línea de CORS y actualizarla
        old_origins = "origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://0.0.0.0:3000', 'http://192.168.1.56:3000']"
        
        # Extraer dominio de la URL pública
        if public_url.startswith('https://'):
            domain = public_url
        else:
            domain = public_url.replace('http://', 'https://')
        
        new_origins = f"origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://0.0.0.0:3000', 'http://192.168.1.56:3000', '{domain}']"
        
        if old_origins in content:
            content = content.replace(old_origins, new_origins)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"[OK] CORS actualizado para permitir: {domain}")
            return True
        else:
            print("[WARNING] No se encontro la configuracion CORS para actualizar")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error actualizando CORS: {e}")
        return False

def main():
    print("=== Configuración de Acceso desde Internet ===\n")
    
    print("[INTERNET] Configurando acceso desde internet usando Ngrok...")
    print("   Ngrok crea un tunel seguro desde internet hacia tu computadora\n")
    
    # Verificar si ngrok está instalado
    if not check_ngrok_installed():
        install_choice = input("¿Quieres instalar ngrok automáticamente? (y/n): ")
        if install_choice.lower() in ['y', 'yes', 's', 'si']:
            if not install_ngrok():
                return
        else:
            print("[INFO] Instala ngrok manualmente desde: https://ngrok.com/download")
            return
    
    # Configurar authtoken si es necesario
    auth_choice = input("\n¿Ya tienes configurado tu authtoken de ngrok? (y/n): ")
    if auth_choice.lower() not in ['y', 'yes', 's', 'si']:
        if not setup_ngrok_auth():
            return
    
    # Iniciar túnel
    public_url, process = start_ngrok_tunnel()
    
    if public_url:
        # Actualizar configuraciones
        update_frontend_config(public_url)
        update_cors_config(public_url)
        
        print(f"\n[SUCCESS] Configuracion completada!")
        print(f"[INFO] Tu API es ahora accesible desde internet:")
        print(f"   Backend API: {public_url}")
        print(f"   Documentación: {public_url}/docs/")
        
        print(f"\n[FRONTEND] Para acceder al frontend:")
        print(f"   1. Inicia el frontend: cd frontend && npm run dev")
        print(f"   2. El frontend se conectará automáticamente a {public_url}")
        
        print(f"\n[IMPORTANTE] IMPORTANTE:")
        print(f"   - El tunel estara activo mientras este script este corriendo")
        print(f"   - Presiona Ctrl+C para detener el tunel")
        print(f"   - La URL publica cambiara cada vez que reinicies ngrok")
        
        print(f"\n[SECURITY] Consideraciones de seguridad:")
        print(f"   - Tu API ahora es accesible desde internet")
        print(f"   - Considera implementar autenticacion robusta")
        print(f"   - Solo para desarrollo/pruebas, no para produccion")
        
        # Mantener el script corriendo
        try:
            print(f"\n[ACTIVE] Tunel activo... Presiona Ctrl+C para detener")
            process.wait()
        except KeyboardInterrupt:
            print(f"\n[STOP] Deteniendo tunel...")
            process.terminate()
    
    else:
        print("[ERROR] No se pudo establecer el tunel")

if __name__ == "__main__":
    main()
