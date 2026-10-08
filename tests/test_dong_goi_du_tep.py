"""Mọi tệp giao diện mà trang HTML nạp phải có mặt trong bản đóng gói.

Thêm một tệp .js (như chung.js) mà quên khai trong kiosk.spec thì bản
chạy từ mã nguồn vẫn chạy, bộ test vẫn xanh — chỉ bản .exe là trắng trang.
Lỗi đó chỉ lộ ra trên máy nhà trường. Test này bắt nó ngay ở đây.
"""

import os
import re

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _doc(ten):
    with open(os.path.join(GOC, ten), encoding="utf-8") as f:
        return f.read()


def _tep_trang_nap():
    tep = set()
    for trang in ("index.html", "recovery.html"):
        tep.add(trang)
        for duong in re.findall(r'(?:src|href)="([^"#:]+)"', _doc(trang)):
            tep.add(duong)
    return tep


def test_moi_tep_trang_nap_deu_duoc_dong_goi():
    spec = _doc("kiosk.spec")
    khai = set(re.findall(r'\("([^"]+)",\s*"[^"]*"\)', spec))
    thieu = []
    for tep in _tep_trang_nap():
        if tep in khai:
            continue
        # thư mục được khai nguyên cụm (vd assets/fonts)
        if any(tep.startswith(d.rstrip("/") + "/") for d in khai):
            continue
        thieu.append(tep)
    assert thieu == [], f"kiosk.spec thieu: {thieu}"


def test_buoc_soat_ban_dong_goi_kiem_moi_tep_o_goc():
    """Bước soát SHA256 trong workflow phải kiểm cả tệp mới."""
    wf = _doc(".github/workflows/build-windows-exe.yml")
    danh_sach = re.search(r'foreach \(\$f in @\(([^)]*)\)\)', wf, re.S).group(1)
    kiem = set(re.findall(r'"([^"]+)"', danh_sach))
    o_goc = {t for t in _tep_trang_nap() if "/" not in t}
    assert o_goc - kiem == set(), o_goc - kiem
