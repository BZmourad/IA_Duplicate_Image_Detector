@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Building EXE (Multi-file mode)
echo ========================================


REM Build executable (multi-file mode)
echo Building executable...
pyinstaller --noconfirm --clean ^
    --windowed ^
    --name "IA_Duplicate_Image_Detector" ^
    --icon "assets\logo.ico" ^
    --add-data "config.yaml;." ^
    --add-data "assets\logo.png;assets" ^
    --add-data ".env;." ^
    --additional-hooks-dir "hooks" ^
    --hidden-import "torch" ^
    --hidden-import "torch.nn" ^
    --hidden-import "torch.nn.functional" ^
    --hidden-import "cv2" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "imagehash" ^
    --hidden-import "faiss" ^
    --hidden-import "sklearn" ^
    --hidden-import "sklearn.cluster" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --hidden-import "yaml" ^
    --hidden-import "dotenv" ^
    --hidden-import "numpy" ^
    --hidden-import "src" ^
    --hidden-import "src.app_config" ^
    --hidden-import "src.gui" ^
    --hidden-import "src.gui.main_window" ^
    --hidden-import "src.gui.results_widget" ^
    --hidden-import "src.gui.workers" ^
    --hidden-import "src.gui.styles" ^
    --hidden-import "src.image_loader" ^
    --hidden-import "src.hashing" ^
    --hidden-import "src.perceptual_hash" ^
    --hidden-import "src.embedding_model" ^
    --hidden-import "src.color_analyzer" ^
    --hidden-import "src.similarity" ^
    --hidden-import "src.grouping" ^
    --hidden-import "src.cache" ^
    --hidden-import "src.report" ^
    --hidden-import "src.utils" ^
    --exclude-module "torchvision" ^
    --exclude-module "torchvision.ops" ^
    --exclude-module "torchvision.models" ^
    --exclude-module "matplotlib" ^
    --exclude-module "notebook" ^
    --exclude-module "jupyter" ^
    --exclude-module "pytest" ^
    --exclude-module "IPython" ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    pause
    exit /b 1
)

REM Create release directory
echo Creating release directory...
if not exist "release" mkdir "release"

REM Copy entire dist folder
xcopy "dist\IA_Duplicate_Image_Detector\*" "release\" /E /I /Y

REM Copy config files
copy "config.yaml" "release\"
copy ".env" "release\"
copy "README.md" "release\"

echo.
echo ========================================
echo Build complete!
echo Application is in the 'release' folder
echo ========================================
pause