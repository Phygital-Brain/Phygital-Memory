# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('phygital_memory')


a = Analysis(
    ['entry.py'],
    pathex=['.'],
    binaries=[],
    datas=[('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/app.html', 'phygital_memory'), ('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/web', 'phygital_memory/web'), ('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/engram_config.json', 'phygital_memory'), ('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/vault/words_en.txt', 'phygital_memory/vault')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='phygital-memory-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
