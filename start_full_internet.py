#!/usr/bin/env python3
"""
Script para hacer tanto frontend como backend accesibles desde internet
"""
import subprocess
import time
import requests
import json
import os

def start_ngrok_multiple():
    """Iniciar múltiples túneles ngrok"""
    print("=== Configuración Completa para Internet ===\n")
    
    print("[INFO] Iniciando túneles ngrok...")
    print("[INFO] Backend: Puerto 5000")
    print("[INFO] Frontend: Puerto 3000")
    
    # Crear archivo de configuración ngrok
    ngrok_config = """
version: "2"
authtoken: ""
tunnels:
  backend:
    addr: 5000
    proto: http
  frontend:
    addr: 3000
    proto: http
"""
    
    # Escribir configuración
    with open('ngrok.yml', 'w') as f:
        f.write(ngrok_config)
    
    print("[CONFIG] Archivo de configuración creado")
    
    # Iniciar ngrok con múltiples túneles
    try:
        print("[START] Iniciando túneles...")
        process = subprocess.Popen(['./ngrok.exe', 'start', '--all', '--config', 'ngrok.yml'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        time.sleep(5)
        
        # Obtener URLs
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            tunnels = response.json()
            
            backend_url = None
            frontend_url = None
            
            for tunnel in tunnels['tunnels']:
                if tunnel['config']['addr'] == 'http://localhost:5000':
                    backend_url = tunnel['public_url']
                elif tunnel['config']['addr'] == 'http://localhost:3000':
                    frontend_url = tunnel['public_url']
            
            if backend_url and frontend_url:
                print(f"[SUCCESS] Túneles activos!")
                print(f"[BACKEND] API: {backend_url}")
                print(f"[FRONTEND] Web: {frontend_url}")
                
                # Actualizar configuración del frontend
                update_frontend_config(backend_url)
                
                print(f"\n[SHARE] URLs para compartir:")
                print(f"   🌐 Interfaz Web: {frontend_url}")
                print(f"   🔧 API: {backend_url}")
                print(f"   📚 Docs: {backend_url}/docs/")
                
                return backend_url, frontend_url, process
            else:
                print("[ERROR] No se pudieron obtener las URLs")
                return None, None, process
                
        except Exception as e:
            print(f"[ERROR] Error obteniendo URLs: {e}")
            return None, None, process
            
    except Exception as e:
        print(f"[ERROR] Error iniciando ngrok: {e}")
        return None, None, None

def update_frontend_config(backend_url):
    """Actualizar configuración del frontend"""
    try:
        env_content = f"""# Configuración para acceso desde internet
VITE_API_URL={backend_url}
"""
        
        with open('frontend/.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"[OK] Frontend configurado para usar: {backend_url}")
        
    except Exception as e:
        print(f"[WARNING] No se pudo actualizar frontend/.env: {e}")

def main():
    # Verificar si ya hay túneles activos
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            tunnels = response.json()
            if tunnels['tunnels']:
                print("[INFO] Ya hay túneles activos:")
                for tunnel in tunnels['tunnels']:
                    print(f"   {tunnel['public_url']} -> {tunnel['config']['addr']}")
                return
    except:
        pass
    
    # Iniciar túneles
    backend_url, frontend_url, process = start_ngrok_multiple()
    
    if backend_url and frontend_url:
        print(f"\n[IMPORTANT] Mantén esta ventana abierta")
        print(f"[NEXT] Inicia tus servidores:")
        print(f"   1. Backend: python app.py")
        print(f"   2. Frontend: cd frontend && npm run dev")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print(f"\n[STOP] Deteniendo túneles...")
            process.terminate()
    else:
        print("[ERROR] No se pudieron configurar los túneles")

if __name__ == "__main__":
    main()
