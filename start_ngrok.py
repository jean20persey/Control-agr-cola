#!/usr/bin/env python3
"""
Script simplificado para iniciar túnel ngrok
"""
import subprocess
import time
import requests
import json
import os

def start_ngrok():
    print("=== Iniciando Túnel Ngrok ===\n")
    
    # Verificar si ya hay un túnel activo
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
        if response.status_code == 200:
            tunnels = response.json()
            if tunnels['tunnels']:
                public_url = tunnels['tunnels'][0]['public_url']
                print(f"[INFO] Ya hay un túnel activo: {public_url}")
                return public_url
    except:
        pass
    
    print("[INFO] Iniciando nuevo túnel ngrok...")
    print("[INFO] Si es la primera vez, necesitarás configurar tu authtoken")
    print("[INFO] Ve a: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("")
    
    # Iniciar ngrok
    try:
        process = subprocess.Popen(['./ngrok.exe', 'http', '5000'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print("[WAIT] Esperando que ngrok se inicie...")
        time.sleep(5)
        
        # Obtener URL pública
        for attempt in range(10):
            try:
                response = requests.get('http://localhost:4040/api/tunnels')
                tunnels = response.json()
                
                if tunnels['tunnels']:
                    public_url = tunnels['tunnels'][0]['public_url']
                    print(f"[SUCCESS] Túnel ngrok activo!")
                    print(f"[URL] URL pública: {public_url}")
                    
                    # Actualizar frontend config
                    update_frontend_config(public_url)
                    
                    print(f"\n[INFO] URLs de acceso:")
                    print(f"   API Backend: {public_url}")
                    print(f"   API Docs: {public_url}/docs/")
                    print(f"   Panel Ngrok: http://localhost:4040")
                    
                    print(f"\n[NEXT] Próximos pasos:")
                    print(f"   1. Inicia el backend: python app.py")
                    print(f"   2. Inicia el frontend: cd frontend && npm run dev")
                    print(f"   3. Accede desde cualquier dispositivo usando: {public_url}")
                    
                    print(f"\n[IMPORTANT] Mantén esta ventana abierta para que el túnel siga activo")
                    
                    # Mantener el proceso corriendo
                    try:
                        process.wait()
                    except KeyboardInterrupt:
                        print(f"\n[STOP] Deteniendo túnel...")
                        process.terminate()
                    
                    return public_url
                else:
                    time.sleep(2)
                    
            except Exception as e:
                time.sleep(2)
        
        print("[ERROR] No se pudo obtener la URL pública")
        print("[INFO] Revisa http://localhost:4040 para ver el estado")
        return None
        
    except Exception as e:
        print(f"[ERROR] Error iniciando ngrok: {e}")
        print(f"[INFO] Asegúrate de haber configurado tu authtoken:")
        print(f"       ./ngrok.exe config add-authtoken TU_AUTHTOKEN_AQUI")
        return None

def update_frontend_config(public_url):
    """Actualizar configuración del frontend"""
    try:
        env_content = f"""# Configuración para acceso desde internet via ngrok
VITE_API_URL={public_url}

# Configuración anterior (red local)
# VITE_API_URL=http://192.168.1.56:5000
"""
        
        with open('frontend/.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"[OK] Frontend configurado para usar: {public_url}")
        
    except Exception as e:
        print(f"[WARNING] No se pudo actualizar frontend/.env: {e}")

if __name__ == "__main__":
    start_ngrok()
