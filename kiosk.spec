# -*- mode: python ; coding: utf-8 -*-
"""
kiosk.spec
==========
Đóng gói ứng dụng kiosk thành 1 file thực thi độc lập bằng PyInstaller.

QUAN TRỌNG: PyInstaller đóng gói CHO ĐÚNG HỆ ĐIỀU HÀNH ĐANG CHẠY LỆNH.
Muốn có file .exe cho Windows, LỆNH `pyinstaller kiosk.spec` PHẢI CHẠY
TRÊN MÁY WINDOWS (hoặc máy ảo/CI chạy Windows) — không build chéo được
từ Linux/macOS ra .exe.

Cách dùng (trên Windows, đã cài Python 3.10+ và requirements-build.txt):
    pip install -r requirements-build.txt
    pyinstaller kiosk.spec
    # -> dist/PhanBoCauLacBo/PhanBoCauLacBo.exe

Cách dùng (trên Linux/macOS — build ra file thực thi cho CHÍNH hệ đó,
hữu ích để tự kiểm tra cấu hình đóng gói không lỗi trước khi build
Windows thật):
    pyinstaller kiosk.spec
"""

import sys

from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas = [
    ("index.html", "."),
    ("style.css", "."),
    ("js", "js"),
    ("i18n_loi.js", "."),
    ("i18n.js", "."),
    ("chung.js", "."),
    ("recovery.html", "."),
    ("recovery.js", "."),
    ("logo.png", "."),
    ("logo.ico", "."),
    ("assets/fonts", "assets/fonts"),
]

binaries = []
hiddenimports = ["webview", "openpyxl"]

# openpyxl doc file .xlsx nguoi dung tha vao. No import dong mot so
# module con (reader/writer theo dinh dang), nen khai bao ro de
# PyInstaller khong bo sot khi phan tich tinh.
pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all("openpyxl")
datas += pkg_datas
binaries += pkg_binaries
hiddenimports += pkg_hiddenimports

# pywebview chọn backend GUI khác nhau theo hệ điều hành. Khai báo rõ để
# PyInstaller không bỏ sót khi phân tích tĩnh (static analysis đôi khi
# không thấy import động bên trong thư viện webview).
if sys.platform.startswith("win"):
    # QUAN TRỌNG: trên Windows, backend DUY NHẤT của pywebview
    # (webview/platforms/winforms.py) LUÔN cần pythonnet để bắc cầu
    # sang .NET/WinForms — kể cả khi hiển thị bằng EdgeChromium/WebView2
    # (lựa chọn engine hiển thị là nội bộ bên trong winforms.py, không
    # phải một backend "edgechromium" riêng — module đó không tồn tại,
    # đã bỏ khỏi hiddenimports).
    #
    # ĐÃ GẶP LỖI THẬT khi chạy bản build:
    #   "RuntimeError: Failed to resolve Python.Runtime.Loader.Initialize
    #    from ...\_internal\pythonnet\runtime\Python.Runtime.dll"
    # Đây là lỗi đóng gói rất phổ biến (nhiều issue trên GitHub của
    # pywebview/PyInstaller) — PyInstaller không tự gom đủ file phụ trợ
    # của pythonnet khi chỉ khai báo hiddenimports suông. collect_all()
    # gom đúng như một PyInstaller hook chính thức sẽ làm (data files +
    # DLL nhị phân + sub-module), khắc phục tận gốc thay vì đoán thiếu
    # file nào.
    hiddenimports += ["webview.platforms.winforms", "clr"]
    for pkg in ("pythonnet", "clr_loader"):
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas += pkg_datas
        binaries += pkg_binaries
        hiddenimports += pkg_hiddenimports
elif sys.platform == "darwin":
    hiddenimports += ["webview.platforms.cocoa"]
else:
    hiddenimports += ["webview.platforms.gtk", "webview.platforms.qt"]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="PhanBoCauLacBo",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    # UPX (nén file thực thi) đã gây ra ĐÚNG lỗi "Failed to resolve
    # Python.Runtime.Loader.Initialize" ở lần build trước — UPX có thể
    # làm hỏng bảng export của các DLL .NET interop như
    # Python.Runtime.dll. Tắt hẳn UPX để đổi lấy đúng đắn (file .exe
    # lớn hơn một chút, không đáng kể với phần mềm kiosk chạy nội bộ).
    upx=False,
    console=False,   # False = khong hien cua so console den phia sau kiosk
    # Bieu tuong tren tep .exe, tren thanh tac vu va trong cua so
    # "Properties" cua Windows. Sinh tu logo.svg bang tao_logo.py.
    icon="logo.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="PhanBoCauLacBo",
)
