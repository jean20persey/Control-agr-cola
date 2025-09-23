#!/usr/bin/env python3
"""
Script simplificado para iniciar el sistema Control Agrícola en modo local
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Mostrar banner del sistema"""
    print("=" * 60)
    print("CONTROL AGRICOLA - MODO LOCAL")
    print("=" * 60)
    print("Configuracion: Desarrollo Local")
    print("Backend: http://localhost:5000")
    print("Frontend: http://localhost:3000")
    print("API Docs: http://localhost:5000/docs/")
    print("=" * 60)

def check_requirements():
    """Verificar que los requisitos estén instalados"""
    print("\nVerificando requisitos...")
    
    # Verificar Python y pip
    try:
        import flask
        print("OK - Flask instalado")
    except ImportError:
        print("ERROR - Flask no instalado. Ejecuta: pip install -r requirements.txt")
        return False
    
    # Verificar Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"OK - Node.js instalado: {result.stdout.strip()}")
        else:
            print("ERROR - Node.js no encontrado")
            return False
    except FileNotFoundError:
        print("ERROR - Node.js no encontrado")
        return False
    
    return True

def start_backend():
    """Iniciar el servidor backend"""
    print("\nIniciando servidor backend...")
    try:
        # Cambiar al directorio raíz del proyecto
        os.chdir(Path(__file__).parent)
        
        # Iniciar Flask
        process = subprocess.Popen([
            sys.executable, 'app.py'
        ])
        
        return process
    except Exception as e:
        print(f"ERROR - Error iniciando backend: {e}")
        return None

def start_frontend():
    """Iniciar el servidor frontend"""
    print("Iniciando servidor frontend...")
    try:
        frontend_path = Path("frontend")
        
        # Verificar si node_modules existe
        if not (frontend_path / "node_modules").exists():
            print("Instalando dependencias del frontend...")
            subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
        
        # Iniciar Vite
        process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], cwd=frontend_path)
        
        return process
    except Exception as e:
        print(f"ERROR - Error iniciando frontend: {e}")
        return None

def main():
    """Función principal"""
    print_banner()
    
    # Verificar requisitos
    if not check_requirements():
        print("\nERROR - Faltan requisitos. Instala las dependencias y vuelve a intentar.")
        input("Presiona Enter para salir...")
        return 1
    
    print("\nIniciando servidores...")
    
    # Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        print("ERROR - No se pudo iniciar el backend")
        input("Presiona Enter para salir...")
        return 1
    
    # Esperar un poco para que el backend se inicie
    time.sleep(3)
    
    # Iniciar frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("ERROR - No se pudo iniciar el frontend")
        backend_process.terminate()
        input("Presiona Enter para salir...")
        return 1
    
    print("\nOK - Servidores iniciados exitosamente!")
    print("\nAccede a la aplicacion:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:5000")
    print("   Documentacion: http://localhost:5000/docs/")
    print("\nPresiona Ctrl+C para detener los servidores")
    
    try:
        # Esperar hasta que el usuario presione Ctrl+C
        while True:
            time.sleep(1)
            
            # Verificar si los procesos siguen ejecutándose
            if backend_process.poll() is not None:
                print("ERROR - El backend se detuvo inesperadamente")
                break
            
            if frontend_process.poll() is not None:
                print("ERROR - El frontend se detuvo inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n\nDeteniendo servidores...")
        
        # Terminar procesos
        try:
            backend_process.terminate()
            frontend_process.terminate()
            
            # Esperar a que terminen
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
        except subprocess.TimeoutExpired:
            # Forzar terminación si no responden
            backend_process.kill()
            frontend_process.kill()
        
        print("OK - Servidores detenidos correctamente")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
