# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs
from PyInstaller.utils.hooks import copy_metadata

datas = [('D:\\Python\\Lib\\site-packages\\Cython\\Utility', 'Cython/Utility'),
           ('D:\\Python\\Lib\\asyncio\\__pycache__\\windows_utils.cpython-313.pyc', 'runtime/asyncio')]
binaries = []
datas += collect_data_files('paddlex')
datas += copy_metadata('aiohttp')
datas += copy_metadata('bce-python-sdk')
datas += copy_metadata('beautifulsoup4')
datas += copy_metadata('chardet')
datas += copy_metadata('colorlog')
datas += copy_metadata('decord')
datas += copy_metadata('einops')
datas += copy_metadata('faiss-cpu')
datas += copy_metadata('fastapi')
datas += copy_metadata('filelock')
datas += copy_metadata('filetype')
datas += copy_metadata('ftfy')
datas += copy_metadata('GPUtil')
datas += copy_metadata('imagesize')
datas += copy_metadata('Jinja2')
datas += copy_metadata('joblib')
datas += copy_metadata('langchain')
datas += copy_metadata('langchain-community')
datas += copy_metadata('langchain-core')
datas += copy_metadata('langchain-openai')
datas += copy_metadata('lxml')
datas += copy_metadata('matplotlib')
datas += copy_metadata('modelscope')
datas += copy_metadata('numpy')
datas += copy_metadata('openai')
datas += copy_metadata('opencv-contrib-python')
datas += copy_metadata('openpyxl')
datas += copy_metadata('packaging')
datas += copy_metadata('pandas')
datas += copy_metadata('pillow')
datas += copy_metadata('premailer')
datas += copy_metadata('prettytable')
datas += copy_metadata('pyclipper')
datas += copy_metadata('pycocotools')
datas += copy_metadata('pydantic')
datas += copy_metadata('pypdfium2')
datas += copy_metadata('PyYAML')
datas += copy_metadata('py-cpuinfo')
datas += copy_metadata('regex')
datas += copy_metadata('requests')
datas += copy_metadata('ruamel.yaml')
datas += copy_metadata('scikit-image')
datas += copy_metadata('scikit-learn')
datas += copy_metadata('shapely')
datas += copy_metadata('soundfile')
datas += copy_metadata('starlette')
datas += copy_metadata('tiktoken')
datas += copy_metadata('tokenizers')
datas += copy_metadata('tqdm')
datas += copy_metadata('ujson')
datas += copy_metadata('uvicorn')
datas += copy_metadata('yarl')
binaries += collect_dynamic_libs('paddle')


SmartSheetPY_a = Analysis(
    ['..\\SmartSheetPY.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
SmartSheetPY_pyz = PYZ(SmartSheetPY_a.pure)

SmartSheetPY_exe = EXE(
    SmartSheetPY_pyz,
    SmartSheetPY_a.scripts,
    [],
    exclude_binaries=True,
    name='SmartSheetPY',
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
)

EmailDownloader_a = Analysis(
    ['..\\EmailDownloader.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
EmailDownloader_pyz = PYZ(EmailDownloader_a.pure)

EmailDownloader_exe = EXE(
    EmailDownloader_pyz,
    EmailDownloader_a.scripts,
    [],
    exclude_binaries=True,
    name='EmailDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

a = Analysis(
    ['..\\ToolSearchingMain.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='ToolSearchingMain',
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
)





coll = COLLECT(
    SmartSheetPY_exe,
    SmartSheetPY_a.binaries,
    SmartSheetPY_a.datas,
    EmailDownloader_exe,
    EmailDownloader_a.binaries,
    EmailDownloader_a.datas,
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartSheetALL',
)
