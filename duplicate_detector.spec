# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path('.')
assets_dir = project_root / 'assets'

# Ensure assets directory exists
if not assets_dir.exists():
    assets_dir.mkdir(parents=True, exist_ok=True)

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('assets/logo.png', 'assets'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'transformers',
        'torch',
        'torchvision',
        'cv2',
        'PIL',
        'imagehash',
        'faiss',
        'sklearn',
        'pandas',
        'openpyxl',
        'yaml',
        'dotenv',
        'PySide6',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'notebook',
        'jupyter',
        'IPython',
        'pytest',
        'setuptools',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IA_Duplicate_Image_Detector',  # Application name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico',  # Icon file (must be .ico for Windows)
)