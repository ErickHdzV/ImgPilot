@echo off
echo Construyendo ejecutable de ImgPilot...
echo.

REM Verificar que PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller no está instalado. Instalando...
    pip install pyinstaller
)

echo.
echo Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Construyendo ejecutable...
pyinstaller ImgPilot.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: La construcción falló.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ¡Ejecutable creado exitosamente!
echo ========================================
echo.
echo El ejecutable se encuentra en: dist\ImgPilot.exe
echo.
pause