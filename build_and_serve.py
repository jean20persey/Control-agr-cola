#!/usr/bin/env python3
"""
Script para construir el frontend y servirlo desde Flask
"""
import subprocess
import os
import shutil
from pathlib import Path

def build_frontend():
    """Construir el frontend para producción"""
    print("[BUILD] Construyendo frontend...")
    
    try:
        # Cambiar al directorio del frontend
        os.chdir('frontend')
        
        # Construir el frontend
        result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Frontend construido exitosamente")
            return True
        else:
            print(f"[ERROR] Error construyendo frontend: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False
    finally:
        # Volver al directorio principal
        os.chdir('..')

def copy_build_to_static():
    """Copiar build del frontend a carpeta static de Flask"""
    print("[COPY] Copiando archivos del frontend...")
    
    try:
        # Crear carpeta static si no existe
        static_dir = Path('static')
        static_dir.mkdir(exist_ok=True)
        
        # Crear carpeta templates si no existe
        templates_dir = Path('templates')
        templates_dir.mkdir(exist_ok=True)
        
        # Copiar archivos del build
        build_dir = Path('frontend/dist')
        
        if build_dir.exists():
            # Copiar archivos estáticos
            for item in build_dir.iterdir():
                if item.is_file():
                    if item.suffix == '.html':
                        # Copiar HTML a templates
                        shutil.copy2(item, templates_dir / item.name)
                        print(f"[COPY] {item.name} -> templates/")
                    else:
                        # Copiar otros archivos a static
                        shutil.copy2(item, static_dir / item.name)
                        print(f"[COPY] {item.name} -> static/")
                elif item.is_dir():
                    # Copiar directorios completos a static
                    dest_dir = static_dir / item.name
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    shutil.copytree(item, dest_dir)
                    print(f"[COPY] {item.name}/ -> static/{item.name}/")
            
            print("[OK] Archivos copiados exitosamente")
            return True
        else:
            print("[ERROR] No se encontró la carpeta dist del frontend")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error copiando archivos: {e}")
        return False

def update_app_for_frontend():
    """Actualizar app.py para servir el frontend"""
    print("[UPDATE] Actualizando app.py...")
    
    try:
        # Leer app.py actual
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Agregar ruta para servir el frontend
        frontend_route = '''
# Servir frontend
@app.route('/')
def serve_frontend():
    return render_template('index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory('static', path)
'''
        
        # Buscar donde agregar las rutas
        if '@app.route(\'/\')' not in content:
            # Agregar import de render_template y send_from_directory
            if 'from flask import Flask, jsonify, request' in content:
                content = content.replace(
                    'from flask import Flask, jsonify, request',
                    'from flask import Flask, jsonify, request, render_template, send_from_directory'
                )
            
            # Agregar las rutas antes del error handler
            if '@app.errorhandler(404)' in content:
                content = content.replace('@app.errorhandler(404)', frontend_route + '\n@app.errorhandler(404)')
            else:
                # Agregar antes del if __name__ == '__main__':
                content = content.replace('if __name__ == \'__main__\':', frontend_route + '\nif __name__ == \'__main__\':')
        
        # Escribir el archivo actualizado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] app.py actualizado")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error actualizando app.py: {e}")
        return False

def main():
    print("=== Configuración Frontend + Backend en una URL ===\n")
    
    # Paso 1: Construir frontend
    if not build_frontend():
        return
    
    # Paso 2: Copiar archivos
    if not copy_build_to_static():
        return
    
    # Paso 3: Actualizar app.py
    if not update_app_for_frontend():
        return
    
    print(f"\n[SUCCESS] ¡Configuración completada!")
    print(f"\n[INFO] Ahora tu URL pública servirá:")
    print(f"   - Frontend: https://tu-url-ngrok.ngrok.io")
    print(f"   - API: https://tu-url-ngrok.ngrok.io/cultivos")
    print(f"   - Docs: https://tu-url-ngrok.ngrok.io/docs/")
    
    print(f"\n[NEXT] Próximos pasos:")
    print(f"   1. Reinicia tu backend: python app.py")
    print(f"   2. Tu URL pública mostrará la interfaz completa")
    print(f"   3. Comparte: https://tu-url-ngrok.ngrok.io")

if __name__ == "__main__":
    main()
