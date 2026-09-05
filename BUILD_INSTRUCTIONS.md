# Instructions pour générer le fichier EXE

## Prérequis

1. Python 3.11+ installé
2. Les dépendances installées (`pip install -r requirements.txt`)
3. Un logo PNG dans `assets/logo.png` (ou utilisez le script pour créer un logo par défaut)

## Étapes

### 1. Installer les dépendances
pip install -r requirements.txt
pip install pyinstaller python-dotenv


### Convertir le logo en format ICO
python scripts/convert_icon.py

### Générer l'exécutable
Option A : Build standard (plus rapide au démarrage)

build_exe.bat
Option B : Build single-file (un seul fichier EXE)

build_exe_onefile.bat

### Résultat
L'exécutable sera généré dans :

Option A : release/IA_Duplicate_Image_Detector.exe

Option B : dist/IA_Duplicate_Image_Detector.exe

### Configuration
Le fichier .env contient :

env
APP_NAME=IA Duplicate Image Detector
APP_VERSION=1.0.0
APP_ICON=assets/logo.png