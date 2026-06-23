# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for TetrioCoach."""

import os
import sys

block_cipher = None

a = Analysis(
    ['tetrio_coach.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('training/models/*.pkl', 'training/models'),
        ('training/models/*.json', 'training/models'),
        ('locales/*.json', 'locales'),
    ],
    hiddenimports=[
        'training',
        'training.feedback_generator',
        'training.evaluator',
        'training.build_patterns',
        'training.ml_model',
        'training.cold_clear_engine',
        'training.board_simulator',
        'sklearn',
        'sklearn.ensemble',
        'sklearn.ensemble._forest',
        'sklearn.ensemble._gb',
        'sklearn.ensemble._gradient_boosting',
        'sklearn.preprocessing',
        'sklearn.preprocessing._data',
        'sklearn.tree',
        'sklearn.tree._classes',
        'sklearn.utils._typedefs',
        'numpy',
        'numpy._core',
        'i18n',
        '_paths',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'training.collect_top_players',
        'training.train_from_kaggle',
        'torch', 'torchvision', 'torchaudio',
        'tensorflow', 'keras',
        'IPython', 'jupyter', 'notebook', 'nbformat', 'nbconvert',
        'jedi', 'parso', 'pygments',
        'zmq', 'tornado',
        'scipy.spatial', 'scipy.signal', 'scipy.integrate', 'scipy.interpolate',
        'scipy.optimize', 'scipy.io.matlab',
        'cryptography',
        'win32com', 'pythoncom', 'pywintypes',
        'psutil',
        'PIL.ImageFilter', 'PIL.SpiderImagePlugin',
        'sympy',
        'transformers', 'huggingface_hub', 'tokenizers', 'safetensors',
        'pydantic',
        'fsspec',
        'narwhals',
        'kagglehub',
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
    [],
    exclude_binaries=True,
    name='TetrioCoach',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='assets/tetrio_coach.ico' if os.path.exists('assets/tetrio_coach.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TetrioCoach',
)
