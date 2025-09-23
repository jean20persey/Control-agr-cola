#!/usr/bin/env python3
"""
Script para iniciar el sistema Control Agrícola con acceso desde otros dispositivos
"""
import socket
import os
import subprocess
import sys
from pathlib import Path

def get_local_ip():
    """Obtiene la IP local de la computadora"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error obteniendo IP: {e}")
        return None

def create_env_file(ip_address):
    """Crea el archivo .env en el frontend con la IP correcta"""
    frontend_path = Path("frontend")
    env_file = frontend_path / ".env"
    
    env_content = f"""# Configuración automática para acceso externo
VITE_API_URL=http://{ip_address}:5000
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ Archivo .env creado en frontend/ con IP: {ip_address}")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo .env: {e}")
        return False

def update_cors_config(ip_address):
    """Actualiza la configuración de CORS en app.py para incluir la IP externa"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar la línea de CORS y actualizarla
        old_cors = "origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://0.0.0.0:3000']"
        new_cors = f"origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://0.0.0.0:3000', 'http://{ip_address}:3000']"
        
        if old_cors in content:
            content = content.replace(old_cors, new_cors)
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Configuración CORS actualizada para IP: {ip_address}")
            return True
        else:
            print("⚠️  No se encontró la configuración CORS para actualizar")
            return False
            
    except Exception as e:
        print(f"❌ Error actualizando CORS: {e}")
        return False

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    # Verificar Python dependencies
    try:
        import flask
        import flask_sqlalchemy
        import flask_cors
        print("✅ Dependencias de Python OK")
    except ImportError as e:
        print(f"❌ Falta instalar dependencias de Python: {e}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    
    # Verificar Node.js dependencies
    frontend_path = Path("frontend")
    node_modules = frontend_path / "node_modules"
    
    if not node_modules.exists():
        print("❌ Dependencias de Node.js no instaladas")
        print("   Ve a la carpeta frontend/ y ejecuta: npm install")
        return False
    else:
        print("✅ Dependencias de Node.js OK")
    
    return True

def main():
    print("=== Iniciador de Control Agrícola para Acceso Externo ===\n")
    
    # Verificar dependencias
    if not check_dependencies():
        return
    
    # Obtener IP local
    local_ip = get_local_ip()
    if not local_ip:
        print("❌ No se pudo obtener la IP local")
        return
    
    print(f"🌐 IP local detectada: {local_ip}")
    
    # Crear archivo .env
    if not create_env_file(local_ip):
        return
    
    # Actualizar CORS
    if not update_cors_config(local_ip):
        return
    
    print(f"\n🚀 Configuración completada!")
    print(f"📱 URLs de acceso:")
    print(f"   Frontend: http://{local_ip}:3000")
    print(f"   API: http://{local_ip}:5000")
    print(f"   Documentación: http://{local_ip}:5000/docs/")
    
    print(f"\n📋 Próximos pasos:")
    print(f"   1. Ejecuta el backend: python app.py")
    print(f"   2. En otra terminal, ve a frontend/ y ejecuta: npm run dev")
    print(f"   3. Accede desde otros dispositivos usando http://{local_ip}:3000")
    
    print(f"\n⚠️  Importante:")
    print(f"   - Asegúrate de que todos los dispositivos estén en la misma red")
    print(f"   - Verifica que el firewall permita conexiones en puertos 3000 y 5000")
    
    # Preguntar si quiere iniciar automáticamente
    response = input(f"\n¿Quieres iniciar el backend automáticamente? (y/n): ")
    if response.lower() in ['y', 'yes', 's', 'si']:
        print(f"\n🚀 Iniciando backend...")
        try:
            subprocess.run([sys.executable, 'app.py'])
        except KeyboardInterrupt:
            print(f"\n👋 Backend detenido")

if __name__ == "__main__":
    main()
