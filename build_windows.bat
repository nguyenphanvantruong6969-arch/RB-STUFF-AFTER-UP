@echo off
REM build_windows.bat — chay tren May Windows co Python 3.10+
REM Ket qua: dist\PhanBoCauLacBo\PhanBoCauLacBo.exe

REM Moi buoc hong thi DUNG NGAY va bao loi. Truoc day script cu chay tiep
REM roi in "XONG" ke ca khi pip hay pyinstaller that bai — nguoi build
REM mang di mot thu muc dist cu ma tuong la ban moi.

python -m venv .venv_build
if errorlevel 1 goto :loi
call .venv_build\Scripts\activate.bat
if errorlevel 1 goto :loi

pip install -r requirements-build.txt
if errorlevel 1 goto :loi

REM Chay bo test truoc khi dong goi: ban build tu ma dang hong thi dung
REM build lam gi.
pip install "pytest>=8.0,<10"
if errorlevel 1 goto :loi
python -m pytest -q
if errorlevel 1 goto :loi

pyinstaller kiosk.spec --noconfirm
if errorlevel 1 goto :loi

echo.
echo ============================================================
echo  XONG. File chay duoc nam o:
echo  dist\PhanBoCauLacBo\PhanBoCauLacBo.exe
echo  (phai copy CA THU MUC PhanBoCauLacBo, khong chi rieng .exe,
echo   vi no can thu muc _internal di kem)
echo ============================================================
pause
exit /b 0

:loi
echo.
echo ============================================================
echo  LOI: build DUNG LAI o buoc tren. KHONG dung thu muc dist\
echo  hien co — co the la ban build CU. Doc thong bao loi o tren.
echo ============================================================
pause
exit /b 1
