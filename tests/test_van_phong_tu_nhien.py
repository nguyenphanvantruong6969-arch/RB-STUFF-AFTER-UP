"""Mọi câu chữ người dùng nhìn thấy phải đọc như người viết, không như máy.

Quy tắc (lấy trang báo lỗi của Google làm mẫu: nói chuyện gì xảy ra, rồi
nên làm gì, bằng lời thường):
  1. Không dùng gạch ngang dài để nối câu. Dùng dấu chấm hoặc dấu phẩy.
  2. Không xưng hô: không "em", "các em", "bạn"; tiếng Anh không "you",
     "your"... Cần chủ ngữ thì gọi thẳng tên sự vật ("học sinh", "tệp này").
  3. Không viết HOA cả chữ để nhấn mạnh.
  4. Không dùng từ kỹ thuật nội bộ: STB, seed, app.db, pipeline, và tên cột
     student_id/club_id (trừ khi nằm trong ngoặc kép, tức tên cột thật mà
     tệp phải dùng).
  5. Không dán chi tiết lỗi thô ({detail}) vào câu. Chi tiết đó nằm riêng
     dưới mục "Chi tiết kỹ thuật" có thể mở ra.

File này quét toàn bộ i18n_errors.MESSAGES và UI_STRINGS trong i18n.js,
để lần sửa sau không vô tình đưa lối viết cũ quay lại.
"""

import json
import os
import re
import shutil
import subprocess

import pytest

from i18n_errors import MESSAGES

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_LAY_UI = """
const fs = require("fs");
const src = fs.readFileSync(process.argv[1], "utf8");
const start = src.indexOf("const UI_STRINGS = {");
const b = src.indexOf("{", start);
let d = 0, i = b;
for (; i < src.length; i++) {
  if (src[i] === "{") d++;
  else if (src[i] === "}") { d--; if (d === 0) { i++; break; } }
}
process.stdout.write(JSON.stringify(eval("(" + src.slice(b, i) + ")")));
"""

# Chữ viết hoa hợp lệ: từ viết tắt thật, không phải để nhấn mạnh.
VIET_TAT = {"CLB", "CSV", "UTF", "XLSX", "RB", "DA", "EN", "VI", "HS", "ID"}


def _ui_strings():
    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available in this environment")
    out = subprocess.run([node, "-e", _LAY_UI, "--", os.path.join(GOC, "i18n.js")],
                         capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(out.stdout)


def _moi_cau():
    """(nguồn, khoá, ngôn ngữ, câu) cho mọi câu hiện ra màn hình."""
    for code, bang in MESSAGES.items():
        for lang in ("vi", "en"):
            yield "i18n_errors", code, lang, bang[lang]
    ui = _ui_strings()
    for lang in ("vi", "en"):
        for khoa, cau in ui[lang].items():
            yield "UI_STRINGS", khoa, lang, cau


def _bo_cho_trong(cau):
    return re.sub(r"\{\w+\}", "", cau)


def _loi_van(lang, cau):
    loi = []
    if "{detail}" in cau:
        loi.append("dán chi tiết lỗi thô {detail}")
    tho = _bo_cho_trong(cau)
    if "—" in tho or re.search(r"\s[–-]{1,2}\s", tho):
        loi.append("gạch ngang nối câu")
    if lang == "vi" and re.search(r"(?<!\w)(em|các em|bạn)(?!\w)", tho, re.I):
        loi.append("xưng hô (em/bạn)")
    if lang == "en" and re.search(r"\b(you|your|yours)\b", tho, re.I):
        loi.append("xưng hô (you)")
    ngoai_ngoac = re.sub(r"\"[^\"]*\"", "", tho)
    if re.search(r"\bSTB\b|\bseed\b|app\.db|pipeline", ngoai_ngoac, re.I):
        loi.append("từ kỹ thuật nội bộ")
    if re.search(r"\b(student_id|club_id)\b", ngoai_ngoac):
        loi.append("tên cột kỹ thuật ngoài ngoặc kép")
    for tu in tho.split():
        if re.search(r"[_/\\]|\.\w", tu):
            continue  # đường dẫn tệp, tên tệp: giữ nguyên như trên đĩa
        for chu in re.findall(r"[^\W\d_]{3,}", tu):
            if chu.isupper() and chu not in VIET_TAT:
                loi.append("viết HOA để nhấn mạnh: %s" % chu)
    return loi


def test_moi_cau_hien_thi_deu_viet_tu_nhien():
    sai = []
    for nguon, khoa, lang, cau in _moi_cau():
        for l in _loi_van(lang, cau):
            sai.append("%s.%s [%s] %s: %r" % (nguon, khoa, lang, l, cau))
    assert not sai, "\n".join(sai)


@pytest.mark.parametrize("lang,cau", [
    ("vi", "Lỗi đọc nhật ký: {detail}"),
    ("vi", "Không xoá được — thử lại."),
    ("vi", "Các em này sẽ không được xét."),
    ("vi", "Dữ liệu KHÔNG hợp lệ."),
    ("en", "Could not read app.db."),
    ("en", "Check that you picked the right file."),
    ("en", "Scores are NOT imported."),
    ("en", "Missing student_id column."),
])
def test_bo_loc_bat_duoc_loi_van_cu(lang, cau):
    """Kiểm tra chính bộ lọc: câu viết theo lối cũ phải bị bắt."""
    assert _loi_van(lang, cau)


def test_bo_loc_khong_bat_nham_cau_tot():
    assert not _loi_van("vi", "Không tìm thấy học sinh {student_id}. Hãy thử lại.")
    assert not _loi_van("en", "Name the columns \"student_id\" and \"club_id\".")
    assert not _loi_van("vi", "Lưu tệp ở dạng CSV UTF-8 rồi nạp lại.")
