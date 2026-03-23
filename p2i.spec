# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# Force PyInstaller to use the correct Tcl/Tk from this conda env,
# not from C:\Python313 which has a different version (8.6.15 vs 8.6.13).
conda_prefix = os.path.dirname(sys.executable)
tcl_dir = os.path.join(conda_prefix, 'Library', 'lib', 'tcl8.6')
tk_dir = os.path.join(conda_prefix, 'Library', 'lib', 'tk8.6')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        (tcl_dir, 'tcl/tcl8.6'),
        (tk_dir, 'tcl/tk8.6'),
    ],
    hiddenimports=['styles'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

# Remove any Tcl/Tk data entries that PyInstaller auto-collected from the
# wrong location (e.g. C:\Python313\tcl) to avoid version conflicts.
a.datas = [
    entry for entry in a.datas
    if not (
        entry[0].startswith('tcl\\') and
        'Python313' in entry[1]
    )
]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='p2i',
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
    icon=['resources/icon/app_icon.ico'],
)
