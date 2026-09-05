@echo off
echo ========================================
echo Building IA Duplicate Image Detector EXE
echo ========================================

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

REM Convert PNG icon to ICO
echo Converting icon...
python scripts/convert_icon.py

REM Clean previous build
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
echo Building executable...
pyinstaller --clean --noconfirm duplicate_detector.spec

REM Create output folder
echo Creating distribution folder...
if not exist "release" mkdir "release"

REM Copy necessary files
copy "dist\IA_Duplicate_Image_Detector.exe" "release\"
copy "config.yaml" "release\"
copy ".env" "release\"
copy "README.md" "release\"

echo.
echo ========================================
echo Build complete!
echo Executable is in the 'release' folder
echo ========================================
pause