@echo off
echo ========================================
echo  Control Agricola - Inicio de Servidores
echo ========================================
echo.

echo [1/3] Verificando configuracion...
python get_ip.py

echo.
echo [2/3] Iniciando backend en puerto 5000...
echo Presiona Ctrl+C para detener
echo.

start "Backend - Control Agricola" cmd /k "python app.py"

timeout /t 3 /nobreak >nul

echo [3/3] Para iniciar el frontend:
echo 1. Abre otra terminal
echo 2. Ve a la carpeta frontend: cd frontend
echo 3. Ejecuta: npm run dev
echo.

echo URLs de acceso:
echo - Frontend: http://192.168.1.56:3000
echo - API: http://192.168.1.56:5000
echo - Documentacion: http://192.168.1.56:5000/docs/
echo.

pause
