# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata

datas = [('Overview.py', '.'), ('pages', 'pages'), ('utils', 'utils'), ('.streamlit', '.streamlit'), ('DB', 'DB'), ('logo.svg', '.'), ('C:\\Users\\20030497\\logistics-cost-estimation\\venv\\Lib\\site-packages\\streamlit\\static', 'streamlit\\static')]
binaries = []
hiddenimports = ['streamlit', 'streamlit.web.cli', 'streamlit.runtime', 'streamlit.runtime.scriptrunner', 'streamlit.runtime.state', 'openpyxl.utils.dataframe', 'dotenv', 'validators']
datas += collect_data_files('streamlit')
datas += copy_metadata('streamlit')
datas += copy_metadata('click')
datas += copy_metadata('altair')
datas += copy_metadata('validators')
datas += copy_metadata('toml')
hiddenimports += collect_submodules('streamlit')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('numpy')
tmp_ret = collect_all('streamlit')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pyarrow')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('protobuf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tornado')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('watchdog')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:\\Users\\20030497\\logistics-cost-estimation\\run_streamlit_bootstrap.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['C:\\Users\\20030497\\logistics-cost-estimation\\pyi_hooks'],
    hooksconfig={},
    runtime_hooks=['C:\\Users\\20030497\\logistics-cost-estimation\\pyi_hooks\\rth_streamlit_version_shim.py'],
    excludes=['streamlit.external.langchain', 'tests', 'pytest', 'unittest'],
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
    name='logistics_app',
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
