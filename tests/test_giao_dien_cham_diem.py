"""Ô nhập điểm — đo bằng TRÌNH DUYỆT THẬT (Playwright + Chromium).

Tầng Python **mù hoàn toàn** với lỗi này. Ô điểm từng là
`<input type="number">`, và trình duyệt **nuốt mất dấu phẩy** rồi báo là
hợp lệ: gõ `8,5` thì `.value` trả về `"85"` và `validity.valid` là
`true`. API chưa bao giờ nhìn thấy dấu phẩy — nó chỉ nhận `"85"` và lưu
đúng như thế. Không test Python nào có thể phát hiện.

Mà `8,5` là **cách viết thập phân bình thường của tiếng Việt**. Không
phải gõ nhầm — gõ đúng thói quen mà máy hiểu sai, và sai gấp 10 lần.

Vì thế mọi phép kiểm ở đây nhìn vào **giá trị trong CSDL**, không nhìn
`.value` của ô — chính `.value` là chỗ lỗi ẩn nấp.
"""

import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def api_co_thi_sinh(api):
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    for sid in ("HS01", "HS02"):
        api.create_student_if_missing(sid, "Học sinh " + sid)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
    return api


@pytest.fixture
def man_cham_diem(api_co_thi_sinh):
    """Mở thẳng tab Chấm điểm của clb_a, trả về (page, hàm gõ-và-lưu, api)."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api_co_thi_sinh, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        # locale tiếng Việt: đúng môi trường máy trường sẽ chạy.
        page = br.new_page(locale="vi-VN")
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="scoring"]').click()
        page.wait_for_selector(".btn-row-link")
        page.locator(".btn-row-link").first.click()
        page.wait_for_selector(".score-input")

        def go_va_luu(chu):
            o = page.locator(".score-input").first
            o.click()
            o.fill("")
            o.type(chu)
            trong_o = o.input_value()
            page.locator("#btnSaveScores").click()
            page.wait_for_timeout(700)
            return trong_o

        yield page, go_va_luu, api_co_thi_sinh, loi
        br.close()


def _diem_trong_csdl(api, sid="HS01"):
    conn = sqlite3.connect(api.db_path)
    r = conn.execute(
        "SELECT score FROM club_scores WHERE student_id = ? AND club_id = 'clb_a'",
        (sid,),
    ).fetchone()
    conn.close()
    return r[0] if r else None


def test_go_dau_phay_kieu_viet_luu_dung_gia_tri(man_cham_diem):
    """Test quan trọng nhất của cả file.

    Kiểm CSDL, không kiểm ô nhập: trước bản vá ô nhập trả về "85" và
    trình duyệt còn khẳng định đó là giá trị hợp lệ."""
    page, go_va_luu, api, loi = man_cham_diem
    go_va_luu("8,5")
    assert _diem_trong_csdl(api) == 8.5, \
        "go '8,5' ma CSDL luu %r — dau phay bi nuot" % _diem_trong_csdl(api)
    assert not loi, loi


def test_o_nhap_giu_nguyen_dau_phay(man_cham_diem):
    """Trình duyệt không được sửa thứ người dùng vừa gõ."""
    page, go_va_luu, api, loi = man_cham_diem
    trong_o = go_va_luu("8,5")
    assert trong_o == "8,5", "trinh duyet da sua thanh %r" % trong_o


def test_dau_cham_van_dung(man_cham_diem):
    """Hai cách viết đều phải nhận — không đánh đổi cách này lấy cách kia."""
    page, go_va_luu, api, loi = man_cham_diem
    go_va_luu("8.5")
    assert _diem_trong_csdl(api) == 8.5


def test_so_nguyen_van_dung(man_cham_diem):
    page, go_va_luu, api, loi = man_cham_diem
    go_va_luu("9")
    assert _diem_trong_csdl(api) == 9.0


def test_chu_thi_bi_tu_choi_va_khong_ghi_de_diem_cu(man_cham_diem):
    """Gõ bậy không được phép xoá mất điểm đã chấm đúng trước đó."""
    page, go_va_luu, api, loi = man_cham_diem
    go_va_luu("7,5")
    assert _diem_trong_csdl(api) == 7.5

    go_va_luu("abc")
    assert _diem_trong_csdl(api) == 7.5, "diem cu bi hong sau khi go bay"
    assert not loi, loi


def test_o_bi_bo_qua_duoc_to_do_va_khong_bao_xanh(man_cham_diem):
    """Ô không hợp lệ bị bỏ qua thì phải TÔ ĐỎ đúng ô đó và nói rõ.

    Trước bản vá: dòng chữ xanh "Đã lưu điểm cho N học sinh", cộng một thông
    báo 3,6 giây chỉ nêu lý do của ô ĐẦU TIÊN. Người chấm tưởng đã lưu hết.
    """
    page, _go, api, loi = man_cham_diem
    o = page.locator(".score-input")
    o.nth(0).fill("abc")
    o.nth(1).fill("-2")
    page.locator("#btnSaveScores").click()
    page.wait_for_selector(".toast.is-warn")

    assert o.nth(0).get_attribute("class").split().count("is-invalid") == 1
    assert o.nth(1).get_attribute("class").split().count("is-invalid") == 1
    assert o.nth(0).get_attribute("title"), "ô đỏ phải kèm lý do"
    phan_hoi = page.locator("#scoringFeedback")
    assert "is-error" in phan_hoi.get_attribute("class")
    assert "2" in phan_hoi.inner_text()
    thong_bao = page.locator(".toast.is-warn").inner_text()
    assert "HS01" in thong_bao and "HS02" in thong_bao, "phải nêu HẾT các ô bị bỏ qua"

    # Sửa đúng rồi lưu lại -> hết đỏ.
    o.nth(0).fill("8")
    o.nth(1).fill("7")
    page.locator("#btnSaveScores").click()
    page.wait_for_function(
        "!document.querySelector('.score-input.is-invalid')", timeout=5000)
    assert _diem_trong_csdl(api) == 8.0
    assert not loi, loi
