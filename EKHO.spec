# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('assets\\icons\\logo-ekho.ico', 'assets\\icons'), ('web', 'web'), ('src', 'src')]
binaries = []
hiddenimports = ['pywebview', 'pygame', 'mutagen', 'moviepy', 'moviepy.editor', 'requests', 'yt_dlp', 'pytubefix', 'model.spotify2mp3_model', 'model.youtube2mp3_model', 'model.soundcloud2mp3', 'controller.music_controller', 'model.music_library', 'databaseManager.db']
datas += collect_data_files('pykakasi')
datas += copy_metadata('imageio')
tmp_ret = collect_all('spotdl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['app.py'],
    pathex=[],
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
    a.binaries,
    a.datas,
    [],
    name='EKHO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icons\\logo-ekho.ico'],
)
