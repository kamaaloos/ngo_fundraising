# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for NGO Fundraising (Windows customer build).

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None
ROOT = Path(SPECPATH)

datas = [
    (str(ROOT / "app" / "assets"), "app/assets"),
]
binaries = []
hiddenimports = [
    "matplotlib",
    "matplotlib.figure",
    "matplotlib.pyplot",
    "matplotlib.backends.backend_qtagg",
    "matplotlib.backends.backend_agg",
    "matplotlib.backends.backend_pdf",
    "matplotlib.backends.qt_compat",
    "matplotlib.backends.backend_qt",
    "matplotlib.backends.backend_qt5agg",
    "PIL",
    "PIL.Image",
    "openpyxl",
    "reportlab",
    "reportlab.pdfbase",
    "reportlab.pdfbase.ttfonts",
    "reportlab.platypus",
    "sqlalchemy.dialects.sqlite",
    "PySide6.QtPrintSupport",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "PySide6.QtCore",
    "numpy",
    "contourpy",
    "cycler",
    "kiwisolver",
    "pyparsing",
    "dateutil",
    "packaging",
]

# Bundle full matplotlib (datas + binaries + package imports) for frozen charts.
for pkg in ("matplotlib", "contourpy"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

datas += collect_data_files("matplotlib")

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / "packaging" / "pyi_rth_ngo.py")],
    excludes=["pytest", "tkinter"],
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
    name="NGOFundraising",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "app" / "assets" / "app.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="NGOFundraising",
)
