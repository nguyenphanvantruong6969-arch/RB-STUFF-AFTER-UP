# -*- coding: utf-8 -*-
"""Giao diện tiếng Việt không được lẫn tiếng Anh.

Phần mềm chạy cho giáo viên và học sinh Việt Nam. Nút ghi "Chạy pipeline"
thì người dùng không đoán được nó làm gì — và tệ hơn, giao diện đang nói
khác hướng dẫn: `HUONG_DAN_SU_DUNG.md` bước 4 viết *"Bấm **Chạy phân
bổ**"*, còn nút thật thì ghi "Chạy pipeline".

Tệp này là lưới chắn để lần sau thêm chuỗi mới không lẫn tiếng Anh trở
lại. Nó quét ba nơi mà người dùng THẬT SỰ đọc:

  * `i18n.js` khối `vi` — chữ động js/*.js dựng lúc chạy
  * `i18n_errors.py` khối `vi` — câu báo lỗi
  * `index.html` — chữ mặc định hiện ra TRƯỚC khi i18n kịp chạy

CHỖ ĐƯỢC PHÉP GIỮ TIẾNG ANH, và vì sao:

  * `(STB)` và `(seed)` trong ngoặc đơn — để người đọc báo cáo hoặc mã
    nguồn nối được với nút trên màn hình. Đây là quyết định của học sinh.
  * `{seed}`, `{club_id}`, `{reserve_group}` … — ô điền tham số, không
    phải chữ hiển thị.
  * `capacity`, `reserve_capacity`, `reserve_group`, `club_id` — TÊN CỘT
    THẬT trong tệp CSV người dùng tự gõ. Dịch chúng là chỉ sai chỗ cần
    sửa: người dùng mở tệp ra sẽ không thấy cột nào tên như vậy.
  * Tên riêng: Microsoft Forms, Excel, CSV, RB-DA, Windows.
"""

import io
import os
import re

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Từ nào lọt vào chữ hiển thị tiếng Việt là hỏng.
CAM = ["pipeline", "club", "clubs", "seed", "tab", "kiosk", "hardcode",
       "file", "form", "checkbox", "import", "export", "upload", "backup"]

# Bỏ những thứ KHÔNG phải chữ người dùng đọc trước khi tìm từ cấm.
BO_QUA = [
    r"\{[^}]*\}",            # ô điền tham số: {club_id}, {seed}, {n} …
    r"\(STB\)", r"\(seed\)", # ngoặc đơn đối chiếu — cố ý giữ
    r"<[^>]+>",              # thẻ HTML trong chuỗi _html
    r"\.\w{2,5}\b",          # đuôi tệp: .xlsx .csv .py .db
    r"\b\w+_\w+\b",          # tên cột / mã định danh: reserve_group, club_id
    r"\bMicrosoft Forms\b", r"\bExcel\b", r"\bCSV\b", r"\bRB-DA\b",
    r"\bcapacity\b",         # tên cột thật trong tệp CSV
]


def _con_tu_cam(chuoi: str):
    sach = chuoi
    for mau in BO_QUA:
        sach = re.sub(mau, " ", sach)
    return [t for t in CAM if re.search(r"\b" + t + r"\b", sach, re.I)]


def _chuoi_vi_trong_i18n_js():
    s = io.open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    ra = {}
    khoi = s[s.index("  vi: {"):s.index("  en: {")]
    for m in re.finditer(r'^\s*([A-Za-z0-9_]+):\s*"((?:[^"\\]|\\.)*)"', khoi, re.M):
        ra["UI/" + m.group(1)] = m.group(2)
    # Bảng lỗi phía trình duyệt giờ nằm ở i18n_loi.js (sinh từ
    # i18n_errors.py) — quét luôn tệp đó để không bỏ sót chữ hiển thị.
    loi = io.open(os.path.join(GOC, "i18n_loi.js"), encoding="utf-8").read()
    for m in re.finditer(r'"vi":\s*"((?:[^"\\]|\\.)*)"', loi):
        ra["LOI_JS/%d" % len(ra)] = m.group(1)
    return ra


def _chuoi_vi_trong_i18n_errors():
    s = io.open(os.path.join(GOC, "i18n_errors.py"), encoding="utf-8").read()
    return {
        "LOI_PY/" + m.group(1): m.group(2)
        for m in re.finditer(
            r'"([a-z0-9_]+)":\s*\{\s*\n\s*"vi":\s*"((?:[^"\\]|\\.)*)"', s, re.M)
    }


def _chu_mac_dinh_trong_index_html():
    s = io.open(os.path.join(GOC, "index.html"), encoding="utf-8").read()
    ra = {}
    for i, m in enumerate(re.finditer(r'>([^<>]{2,400})<', s)):
        chu = m.group(1).strip()
        if chu:
            ra["HTML/%d" % i] = chu
    for m in re.finditer(r'placeholder="([^"]{2,200})"', s):
        ra["HTML_PH/%s" % m.group(1)[:20]] = m.group(1)
    return ra


@pytest.mark.parametrize("lay", [
    _chuoi_vi_trong_i18n_js,
    _chuoi_vi_trong_i18n_errors,
    _chu_mac_dinh_trong_index_html,
], ids=["i18n.js", "i18n_errors.py", "index.html"])
def test_khong_con_tu_tieng_anh_trong_chu_hien_thi(lay):
    ban = []
    for khoa, chuoi in lay().items():
        con = _con_tu_cam(chuoi)
        if con:
            ban.append("%s: %s  ->  %s" % (khoa, con, chuoi[:90]))
    assert not ban, "còn tiếng Anh trong giao diện tiếng Việt:\n" + "\n".join(ban)


def test_luoi_chan_nay_that_su_bat_duoc():
    """Test cho chính test: nếu bộ lọc BO_QUA quá rộng thì test trên xanh
    một cách vô nghĩa."""
    assert _con_tu_cam("Chạy pipeline") == ["pipeline"]
    assert _con_tu_cam("đã xếp club") == ["club"]
    assert _con_tu_cam("Kéo thả file Excel") == ["file"]
    # còn đây là những chỗ ĐƯỢC PHÉP, không được báo nhầm
    assert _con_tu_cam("Số bốc thăm (STB) đã khoá") == []
    assert _con_tu_cam("Hạt giống bốc thăm (seed)") == []
    assert _con_tu_cam("CLB {club_id} có capacity <= 0") == []
    assert _con_tu_cam("Nhãn dự trữ reserve_group không khớp") == []


def test_nut_chay_khop_voi_huong_dan_su_dung():
    """Hướng dẫn bước 4 bảo bấm nút Chạy bằng đúng tên in đậm. Nút thật phải
    ghi đúng như vậy — trước đây nút ghi 'Chạy pipeline' và hai bên lệch nhau."""
    nut = _chuoi_vi_trong_i18n_js()["UI/btn_run_pipeline"]
    huong_dan = io.open(os.path.join(GOC, "HUONG_DAN_SU_DUNG.md"),
                        encoding="utf-8").read()
    assert f"**{nut}**" in huong_dan
