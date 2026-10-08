# =====================================================================
#  ky_va_tin_cay.ps1
#  ---------------------------------------------------------------
#  Ky file PhanBoCauLacBo.exe bang chung chi TU KY, va cai chung chi
#  do vao kho tin cay cua may — de Windows khong con bao "khong co
#  chu ky so hop le" moi lan chay app.
#
#  CHAY THE NAO:
#    1. Bam chuot phai vao Start -> Windows PowerShell (Admin)
#    2. Go:  cd "duong\dan\den\thu\muc\chua\file\nay"
#    3. Go:  .\ky_va_tin_cay.ps1
#
#    Neu Windows chan script, chay lenh nay TRUOC (chi anh huong
#    phien PowerShell hien tai, khong doi cai dat may):
#       Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#
#  CHAY MAY LAN CUNG DUOC: script tim chung chi cu truoc, chi tao moi
#  khi chua co. Ky lai file da ky cung khong sao.
#
#  PHAM VI: chung chi tu ky chi duoc TIN TREN MAY DA CAI NO. Mang file
#  .exe sang may khac thi may do van bao canh bao — do la ban chat cua
#  chung chi tu ky, khong phai loi script. Muon het canh bao tren MOI
#  may thi phai mua chung chi thuong mai (xem HUONG_DAN_CAI_DAT.md).
# =====================================================================

$ErrorActionPreference = "Stop"

# Ten chung chi. Giu nguyen giua cac lan chay de dung lai chung chi cu,
# khong tao chung chi moi moi lan.
$TenChungChi = "RB-DA Kiosk - Phan bo Cau lac bo"
$SubjectCN   = "CN=$TenChungChi"

function Buoc($so, $chu) {
    Write-Host ""
    Write-Host "[$so] $chu" -ForegroundColor Cyan
}
function Xong($chu) { Write-Host "    OK: $chu" -ForegroundColor Green }
function Loi($chu)  { Write-Host "    LOI: $chu" -ForegroundColor Red }
function Nhac($chu) { Write-Host "    $chu" -ForegroundColor Yellow }

Write-Host ""
Write-Host "=====================================================" -ForegroundColor White
Write-Host " Ky va tin cay ung dung Phan bo Cau lac bo (RB-DA)" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor White

# ---------------------------------------------------------------------
# BUOC 1 — Kiem tra quyen Administrator
#
# Kiem tra NGAY DAU chu khong de chay nua chung roi hong: viec cai
# chung chi vao kho LocalMachine bat buoc phai co quyen nay.
# ---------------------------------------------------------------------
Buoc 1 "Kiem tra quyen Administrator"

$dinhDanh = [Security.Principal.WindowsIdentity]::GetCurrent()
$vaiTro   = New-Object Security.Principal.WindowsPrincipal($dinhDanh)
if (-not $vaiTro.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Loi "Cua so PowerShell nay KHONG co quyen Administrator."
    Write-Host ""
    Nhac "Cach mo dung:"
    Nhac "  1. Bam chuot phai vao nut Start"
    Nhac "  2. Chon 'Windows PowerShell (Admin)' hoac 'Terminal (Admin)'"
    Nhac "  3. Chay lai script nay"
    Write-Host ""
    Nhac "KHONG co quyen Administrator? App van chay duoc binh thuong —"
    Nhac "chi can bam 'More info' -> 'Run anyway' o canh bao dau tien."
    Nhac "Xem HUONG_DAN_CAI_DAT.md."
    exit 1
}
Xong "Dang chay voi quyen Administrator"

# ---------------------------------------------------------------------
# BUOC 2 — Tim file .exe can ky
# ---------------------------------------------------------------------
Buoc 2 "Tim file PhanBoCauLacBo.exe"

$ungVien = @(
    (Join-Path $PSScriptRoot "PhanBoCauLacBo.exe"),
    (Join-Path $PSScriptRoot "PhanBoCauLacBo\PhanBoCauLacBo.exe"),
    (Join-Path $PSScriptRoot "dist\PhanBoCauLacBo\PhanBoCauLacBo.exe")
)
$duongDanExe = $ungVien | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $duongDanExe) {
    Loi "Khong tim thay PhanBoCauLacBo.exe"
    Write-Host ""
    Nhac "Da tim o cac vi tri sau:"
    $ungVien | ForEach-Object { Nhac "  - $_" }
    Write-Host ""
    Nhac "Hay chep file ky_va_tin_cay.ps1 nay vao CUNG THU MUC voi"
    Nhac "PhanBoCauLacBo.exe (thu muc vua giai nen), roi chay lai."
    exit 1
}
Xong "Tim thay: $duongDanExe"

# ---------------------------------------------------------------------
# BUOC 3 — Tim signtool.exe
#
# signtool nam trong Windows SDK. Duong dan khac nhau theo phien ban
# nen phai quet nhieu cho. Neu may chua cai SDK thi khong co cong cu
# nay — script se noi ro cach xu ly thay vi bao loi kho hieu.
# ---------------------------------------------------------------------
Buoc 3 "Tim cong cu ky signtool.exe"

$signtool = $null

# Uu tien signtool da co san trong PATH
$trongPath = Get-Command signtool.exe -ErrorAction SilentlyContinue
if ($trongPath) { $signtool = $trongPath.Source }

# Neu chua co, quet cac thu muc Windows Kits (nhieu phien ban SDK)
if (-not $signtool) {
    $goc = @(
        "${env:ProgramFiles(x86)}\Windows Kits\10\bin",
        "${env:ProgramFiles}\Windows Kits\10\bin",
        "${env:ProgramFiles(x86)}\Windows Kits\8.1\bin"
    ) | Where-Object { $_ -and (Test-Path $_) }

    foreach ($thuMuc in $goc) {
        $timThay = Get-ChildItem -Path $thuMuc -Filter "signtool.exe" -Recurse -ErrorAction SilentlyContinue |
                   Where-Object { $_.FullName -match "x64" } |
                   Sort-Object FullName -Descending |
                   Select-Object -First 1
        if ($timThay) { $signtool = $timThay.FullName; break }
    }
}

if (-not $signtool) {
    Loi "Khong tim thay signtool.exe tren may nay."
    Write-Host ""
    Nhac "signtool nam trong bo Windows SDK. Hai cach xu ly:"
    Write-Host ""
    Nhac "  CACH 1 (khuyen nghi voi de tai du thi) — BO QUA viec ky."
    Nhac "  App van chay day du, khong thieu tinh nang nao. Chi can bam"
    Nhac "  'More info' -> 'Run anyway' o canh bao dau tien. Xem"
    Nhac "  HUONG_DAN_CAI_DAT.md."
    Write-Host ""
    Nhac "  CACH 2 — cai Windows SDK (dung luong lon, mat thoi gian):"
    Nhac "  https://developer.microsoft.com/windows/downloads/windows-sdk/"
    Nhac "  Khi cai chi can tich muc 'Windows SDK Signing Tools'."
    exit 1
}
Xong "Tim thay: $signtool"

Write-Host ""
Nhac "LUU Y: tai khoan dang chay script se giu khoa ky ma CA MAY tin."
Nhac "Chi chay bang tai khoan quan tri rieng, khong dung chung."

# ---------------------------------------------------------------------
# BUOC 4 — Tao (hoac dung lai) chung chi tu ky
#
# Tim chung chi cu TRUOC. Tao moi moi lan chay se khien may tich tu
# hang dong chung chi rac, va ban build sau lai phai cai lai chung chi.
#
# RUI RO PHAI BIET: buoc 5 cai chung chi nay vao kho tin cay cua CA MAY,
# con khoa bi mat nam trong kho CUA NGUOI DANG CHAY script. Ai dung duoc
# tai khoan Windows do (ke ca phan mem doc hai chay duoi ten no) deu ky
# duoc MOI tep .exe ma ca may se tin. Vi vay:
#   - khoa tao ra la NonExportable: khong xuat ra tep .pfx de mang sang
#     may khac ky duoc;
#   - chi chay script bang tai khoan quan tri RIENG cua nguoi phu trach
#     may, khong chay bang tai khoan dung chung cua phong may.
# Chung chi tao TRUOC ban nay van xuat duoc khoa — muon siet lai thi xoa
# no trong certmgr.msc (Personal, Trusted Root, Trusted Publishers) roi
# chay lai script.
# ---------------------------------------------------------------------
Buoc 4 "Chuan bi chung chi tu ky"

$chungChi = Get-ChildItem Cert:\CurrentUser\My |
            Where-Object { $_.Subject -eq $SubjectCN -and $_.NotAfter -gt (Get-Date) } |
            Sort-Object NotAfter -Descending |
            Select-Object -First 1

if ($chungChi) {
    Xong "Dung lai chung chi da tao truoc day (het han $($chungChi.NotAfter.ToString('dd/MM/yyyy')))"
} else {
    try {
        $chungChi = New-SelfSignedCertificate `
            -Subject $SubjectCN `
            -Type CodeSigningCert `
            -KeyUsage DigitalSignature `
            -KeyAlgorithm RSA `
            -KeyLength 2048 `
            -KeyExportPolicy NonExportable `
            -CertStoreLocation "Cert:\CurrentUser\My" `
            -NotAfter (Get-Date).AddYears(5)
        Xong "Da tao chung chi moi, han dung 5 nam"
    } catch {
        Loi "Khong tao duoc chung chi: $($_.Exception.Message)"
        exit 1
    }
}

# ---------------------------------------------------------------------
# BUOC 5 — Cai chung chi vao kho tin cay cua may
#
# Day moi la buoc lam Windows het canh bao. Ky khong thoi chua du:
# Windows phai TIN don vi cap chung chi, ma chung chi tu ky thi chinh
# no la don vi cap.
#
# Can hai kho:
#   Root               — de he thong tin chung chi
#   TrustedPublisher   — de SmartScreen/AppLocker chap nhan nha phat hanh
# ---------------------------------------------------------------------
Buoc 5 "Cai chung chi vao kho tin cay cua may"

$tepTam = Join-Path $env:TEMP "rbda_chungchi_$([guid]::NewGuid().ToString('N')).cer"
try {
    Export-Certificate -Cert $chungChi -FilePath $tepTam -Force | Out-Null

    foreach ($kho in @("Root", "TrustedPublisher")) {
        $duongDanKho = "Cert:\LocalMachine\$kho"
        $daCo = Get-ChildItem $duongDanKho -ErrorAction SilentlyContinue |
                Where-Object { $_.Thumbprint -eq $chungChi.Thumbprint }
        if ($daCo) {
            Xong "Kho $kho — da co san, khong cai lai"
        } else {
            Import-Certificate -FilePath $tepTam -CertStoreLocation $duongDanKho | Out-Null
            Xong "Kho $kho — da cai"
        }
    }
} catch {
    Loi "Khong cai duoc chung chi: $($_.Exception.Message)"
    exit 1
} finally {
    if (Test-Path $tepTam) { Remove-Item $tepTam -Force -ErrorAction SilentlyContinue }
}

# ---------------------------------------------------------------------
# BUOC 6 — Ky file .exe
#
# Dung dau thoi gian (timestamp) cua DigiCert: khong co no thi chu ky
# het hieu luc ngay khi chung chi het han. Co timestamp thi chu ky van
# hop le mai ve sau.
# ---------------------------------------------------------------------
Buoc 6 "Ky file PhanBoCauLacBo.exe"

$ketQua = & $signtool sign `
    /sha1 $chungChi.Thumbprint `
    /fd SHA256 `
    /tr "http://timestamp.digicert.com" `
    /td SHA256 `
    $duongDanExe 2>&1

if ($LASTEXITCODE -ne 0) {
    # Khong co mang thi buoc dong dau that bai — thu lai khong dong dau,
    # van tot hon la khong ky duoc gi.
    Nhac "Khong dong dau thoi gian duoc (may co dang offline?). Thu ky khong dong dau..."
    $ketQua = & $signtool sign /sha1 $chungChi.Thumbprint /fd SHA256 $duongDanExe 2>&1

    if ($LASTEXITCODE -ne 0) {
        Loi "Ky that bai."
        Write-Host ""
        Nhac "Thong bao goc tu signtool:"
        $ketQua | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
        Write-Host ""
        Nhac "App van chay duoc binh thuong du khong ky — xem HUONG_DAN_CAI_DAT.md."
        exit 1
    }
    Xong "Da ky (khong co dau thoi gian — chu ky het hieu luc khi chung chi het han)"
} else {
    Xong "Da ky, co dau thoi gian"
}

# ---------------------------------------------------------------------
# BUOC 7 — Kiem chung lai
# ---------------------------------------------------------------------
Buoc 7 "Kiem tra lai chu ky vua ky"

$kiemTra = Get-AuthenticodeSignature -FilePath $duongDanExe
if ($kiemTra.Status -eq "Valid") {
    Xong "Windows xac nhan chu ky HOP LE"
} else {
    Nhac "Trang thai chu ky: $($kiemTra.Status)"
    Nhac "$($kiemTra.StatusMessage)"
    Nhac "Neu trang thai la UnknownError hoac NotTrusted, thu khoi dong lai may"
    Nhac "roi kiem tra lai — Windows doi khi cache danh sach chung chi tin cay."
}

Write-Host ""
Write-Host "=====================================================" -ForegroundColor White
Write-Host " XONG" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor White
Write-Host ""
Nhac "Buoc tiep theo: chay thu PhanBoCauLacBo.exe."
Nhac "Canh bao 'nha phat hanh khong xac dinh' phai KHONG con hien."
Write-Host ""
Nhac "LUU Y: chung chi nay chi duoc tin TREN MAY NAY. Mang file .exe"
Nhac "sang may khac thi may do van canh bao — chay lai script nay tren"
Nhac "may do, hoac dung cach bam qua trong HUONG_DAN_CAI_DAT.md."
Write-Host ""
