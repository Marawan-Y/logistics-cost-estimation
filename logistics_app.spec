# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\20030497\\logistics-cost-estimation\\run_streamlit_bootstrap.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=['C:\\Users\\20030497\\logistics-cost-estimation\\pyi_hooks'],
    hooksconfig={},
    runtime_hooks=['C:\\Users\\20030497\\logistics-cost-estimation\\pyi_hooks\\rth_streamlit_version_shim.py'],
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
    name='logistics_app',
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
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='logistics_app',
)
