@echo off
echo ========================================
echo   Building FileManager Pro Executable
echo ========================================

:: Clean up previous builds
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Compiling with PyInstaller...
:: --onefile: Bundles everything into a single EXE
:: --windowed: Hides the console window on launch
:: --name: Sets the output filename
:: --add-data: Bundles assets or external files if needed
:: Note: config.json is auto-created by the app if missing, so we don't need to bundle a specific one.

pyinstaller --onefile --windowed --name "FileManager Pro" src/main.py

echo.
echo ========================================
echo   Build Complete!
echo   Output location: dist/FileManager Pro.exe
echo ========================================
pause
