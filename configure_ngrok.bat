@echo off
echo ========================================
echo  Configuracion de Ngrok
echo ========================================
echo.
echo 1. Ve a: https://dashboard.ngrok.com/get-started/your-authtoken
echo 2. Registrate gratis (30 segundos)
echo 3. Copia tu authtoken
echo.
set /p authtoken="Pega tu authtoken aqui: "
echo.
echo Configurando authtoken...
.\ngrok.exe config add-authtoken %authtoken%
echo.
echo Authtoken configurado correctamente!
echo.
echo Ahora ejecuta: python start_ngrok.py
pause
