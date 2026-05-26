# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('.ENV', '.'), ('web', 'web'), ('assets\\icons', 'assets\\icons'), ('assets\\portadas', 'assets\\portadas'), ('data\\BDD\\ekho.db', 'data\\BDD')]
<<<<<<< HEAD
binaries = []
hiddenimports = ['tls_client', 'spotapi', 'SpotipyFree', 'spotdl', 'spotdl.search.song_gatherer', 'pykakasi', 'moviepy.editor', 'imageio', 'pygame', 'ytmusicapi', 'model.spotify2mp3_model', 'model.youtube2mp3_model', 'model.soundcloud2mp3', 'model.music_library', 'model.conversor_model', 'model.playlist_model', 'model.db_adapter', 'controller.music_controller', 'controller.playlist_controller', 'controller.conversor_controller', 'controller.spotify2mp3_controller', 'controller.youtube2mp3_controller', 'controller.soundcloud2mp3_controller', 'databaseManager.db', 'databaseManager.BDD', 'frozen_utils', 'mutagen', 'mutagen.mp3', 'mutagen.id3', 'requests']
datas += copy_metadata('imageio')
datas += copy_metadata('imageio-ffmpeg')
datas += copy_metadata('moviepy')
datas += copy_metadata('mutagen')
datas += copy_metadata('requests')
datas += copy_metadata('yt-dlp')
datas += copy_metadata('spotdl')
datas += copy_metadata('tls-client')
datas += copy_metadata('pytubefix')
datas += copy_metadata('pygame')
datas += copy_metadata('pykakasi')
datas += copy_metadata('pywebview')
tmp_ret = collect_all('yt_dlp')
=======
binaries = [('C:\\Users\\albag\\Documents\\Visual\\Spotifah\\.venv\\Lib\\site-packages\\tls_client\\dependencies\\tls-client-64.dll', 'tls_client\\dependencies')]
hiddenimports = ['moviepy.editor', 'imageio.v2', 'imageio_ffmpeg', 'pygame', 'ytmusicapi', 'tls_client', 'model.spotify2mp3_model', 'model.youtube2mp3_model', 'model.soundcloud2mp3', 'controller.music_controller', 'databaseManager.db', 'gettext']
datas += copy_metadata('imageio')
datas += copy_metadata('imageio-ffmpeg')
datas += copy_metadata('moviepy')
tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pytubefix')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('webview')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('spotdl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pykakasi')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('moviepy')
>>>>>>> 24f0487b80bc3ff424c1bfde05cb3c0da55c5690
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('imageio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('imageio-ffmpeg')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('numpy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('requests')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('babel')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('spotdl')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('spotipy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('click')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tls_client')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
<<<<<<< HEAD
tmp_ret = collect_all('webview')
=======
tmp_ret = collect_all('moviepy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('imageio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('imageio_ffmpeg')
>>>>>>> 24f0487b80bc3ff424c1bfde05cb3c0da55c5690
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['app.py'],
    pathex=['src'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
<<<<<<< HEAD
    hookspath=[''],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['spotdl.web', 'spotdl.console', 'torch', 'transformers', 'scipy'],
=======
    hookspath=['C:\\Users\\albag\\Documents\\Visual\\Spotifah\\.venv\\Lib\\site-packages\\webview\\__pyinstaller'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'transformers', 'scipy'],
>>>>>>> 24f0487b80bc3ff424c1bfde05cb3c0da55c5690
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EKHO',
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
    icon=['assets\\icons\\logo-ekho.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EKHO',
)
