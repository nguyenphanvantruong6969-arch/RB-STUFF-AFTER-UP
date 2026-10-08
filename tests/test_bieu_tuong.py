# -*- coding: utf-8 -*-
"""Canh phần biểu tượng ứng dụng.

Biểu tượng hỏng thì không có test nào khác đỏ — phần mềm vẫn chạy đúng,
chỉ là hiện ra quả địa cầu mặc định. Loại lỗi im lặng đó chỉ phát hiện
được khi đã build xong và mở lên xem, tức là mất trọn một vòng.
"""

import os
import re

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def doc(ten):
    with open(os.path.join(GOC, ten), encoding="utf-8") as f:
        return f.read()


@pytest.mark.parametrize("ten", ["logo.png", "logo.ico", "logo.svg"])
def test_tep_bieu_tuong_ton_tai(ten):
    p = os.path.join(GOC, ten)
    assert os.path.exists(p), "thiếu %s — chạy tao_logo.py" % ten
    assert os.path.getsize(p) > 500, "%s rỗng hoặc hỏng" % ten


@pytest.mark.parametrize("trang", ["index.html", "recovery.html"])
def test_trang_web_tro_toi_bieu_tuong(trang):
    s = doc(trang)
    assert 'rel="icon"' in s, "%s chưa khai báo biểu tượng" % trang
    assert "logo.png" in s, "%s chưa trỏ tới logo.png" % trang


def test_logo_ico_co_du_cac_co():
    """Windows lấy cỡ khác nhau cho thanh tác vụ, cửa sổ và danh sách tệp.
    Thiếu cỡ nào thì Windows tự phóng to cỡ khác, ra hình vỡ."""
    # Cùng quy ước với nhóm test giao diện: thiếu gói phụ thì BỎ QUA chứ
    # không làm đỏ. Pillow nằm trong requirements-dev.txt, không nằm trong
    # requirements.txt vì phần mềm chạy không cần tới nó.
    Image = pytest.importorskip("PIL.Image", reason="chưa cài Pillow")
    with Image.open(os.path.join(GOC, "logo.ico")) as im:
        co = {kt[0] for kt in im.info.get("sizes", set())}
    for can in (16, 32, 48, 256):
        assert can in co, "logo.ico thiếu cỡ %dx%d (đang có: %s)" % (can, can, sorted(co))


def test_kiosk_spec_gan_bieu_tuong_vao_exe():
    s = doc("kiosk.spec")
    assert re.search(r'icon\s*=\s*"logo\.ico"', s), "kiosk.spec chưa gắn logo.ico vào .exe"


def test_moi_tep_khai_bao_trong_kiosk_spec_deu_co_that():
    """Khai báo một tệp không tồn tại thì PyInstaller dừng giữa chừng —
    biết trước ở đây rẻ hơn nhiều so với biết sau 5 phút build."""
    s = doc("kiosk.spec")
    khoi = s[s.index("datas = ["):s.index("binaries = [")]
    thieu = [t for t in re.findall(r'\("([^"]+)",\s*"[^"]*"\)', khoi)
             if not os.path.exists(os.path.join(GOC, t))]
    assert not thieu, "kiosk.spec khai báo tệp không tồn tại: %s" % thieu
