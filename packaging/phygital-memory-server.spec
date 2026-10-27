# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/app.html', 'phygital_memory'), ('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/closeask.html', 'phygital_memory'), ('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/web', 'phygital_memory/web'), ('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/engram_config.json', 'phygital_memory'), ('/Users/you/Desktop/Phygital-Memory-Test/core/phygital_memory/vault/words_en.txt', 'phygital_memory/vault')]
binaries = []
hiddenimports = []
hiddenimports += collect_submodules('phygital_memory')
hiddenimports += collect_submodules('cheroot')
tmp_ret = collect_all('wsgidav')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['entry.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
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
    [],
    exclude_binaries=True,
    name='phygital-memory-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='phygital-memory-server',
)
