@echo off
echo ========================================
echo Building Single-File EXE
echo ========================================

REM Activate virtual environment if exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Install required packages
pip install pyinstaller

REM Convert PNG icon to ICO
python scripts/convert_icon.py

REM Clean previous build
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build single-file executable
pyinstaller --onefile ^
    --windowed ^
    --name "IA_Duplicate_Image_Detector" ^
    --icon "assets\logo.ico" ^
    --add-data "config.yaml;." ^
    --add-data "assets\logo.png;assets" ^
    --add-data ".env;." ^
    --hidden-import "transformers" ^
    --hidden-import "torch" ^
    --hidden-import "torchvision" ^
    --hidden-import "cv2" ^
    --hidden-import "PIL" ^
    --hidden-import "imagehash" ^
    --hidden-import "faiss" ^
    --hidden-import "sklearn" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --hidden-import "yaml" ^
    --hidden-import "dotenv" ^
    --exclude-module "matplotlib" ^
    --exclude-module "notebook" ^
    --exclude-module "jupyter" ^
    --exclude-module "pytest" ^
    main.py

echo.
echo ========================================
echo Single-file build complete!
echo Executable is in the 'dist' folder
echo ========================================
pause