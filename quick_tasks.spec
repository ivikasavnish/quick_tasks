# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Quick Tasks.
Build with: pyinstaller quick_tasks.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Get the project directory
PROJECT_DIR = Path(SPECPATH)

# Collect all Python files
datas = [
    # Include config directory structure
    (str(PROJECT_DIR / 'config'), 'config'),
]

# Include icon if exists
icon_path = PROJECT_DIR / 'resources' / 'icon.ico'
if icon_path.exists():
    datas.append((str(PROJECT_DIR / 'resources'), 'resources'))
    icon_file = str(icon_path)
else:
    icon_file = None

a = Analysis(
    [str(PROJECT_DIR / 'main.py')],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtNetwork',
        'google.auth.transport.requests',
        'google_auth_oauthlib.flow',
        'googleapiclient.discovery',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='QuickTasks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
    version='version_info.txt' if (PROJECT_DIR / 'version_info.txt').exists() else None,
)
