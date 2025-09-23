#!/usr/bin/env python3
"""
Script para obtener la IP local de la computadora para acceso desde otros dispositivos
"""
import socket
import subprocess
import sys

def get_local_ip():
    """Obtiene la IP local de la computadora"""
    try:
        # Crear un socket para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error obteniendo IP: {e}")
        return None

def get_network_interfaces():
    """Obtiene todas las interfaces de red disponibles"""
    try:
        if sys.platform == "win32":
            # En Windows, usar ipconfig
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
            return result.stdout
        else:
            # En Linux/Mac, usar ifconfig o ip
            try:
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                return result.stdout
            except FileNotFoundError:
                result = subprocess.run(['ip', 'addr'], capture_output=True, text=True)
                return result.stdout
    except Exception as e:
        print(f"Error obteniendo interfaces de red: {e}")
        return None

def main():
    print("=== Configuracion de Red para Control Agricola ===\n")
    
    # Obtener IP local
    local_ip = get_local_ip()
    if local_ip:
        print(f"[IP] Tu IP local es: {local_ip}")
        print(f"[ACCESO] Para acceder desde otros dispositivos usa:")
        print(f"   Frontend: http://{local_ip}:3000")
        print(f"   API Backend: http://{local_ip}:5000")
        print(f"   API Docs: http://{local_ip}:5000/docs/")
        
        print(f"\n[CONFIG] Configuracion para .env del frontend:")
        print(f"   VITE_API_URL=http://{local_ip}:5000")
        
        print(f"\n[PASOS] Pasos para habilitar acceso externo:")
        print(f"   1. Crear archivo .env en frontend/ con:")
        print(f"      VITE_API_URL=http://{local_ip}:5000")
        print(f"   2. Asegurate de que el firewall permita conexiones en puertos 3000 y 5000")
        print(f"   3. Ejecuta el backend: python app.py")
        print(f"   4. Ejecuta el frontend: npm run dev")
        print(f"   5. Accede desde otros dispositivos usando http://{local_ip}:3000")
        
    else:
        print("[ERROR] No se pudo obtener la IP local")
    
    print(f"\n[INFO] Informacion de red completa:")
    interfaces = get_network_interfaces()
    if interfaces:
        print(interfaces)
    
    print(f"\n[IMPORTANTE] Notas importantes:")
    print(f"   - Asegurate de estar en la misma red WiFi/LAN")
    print(f"   - Verifica que el firewall no bloquee los puertos 3000 y 5000")
    print(f"   - En Windows, puede ser necesario permitir acceso en Windows Defender")

if __name__ == "__main__":
    main()
