"""Canh nút đổi ngôn ngữ bằng TRÌNH DUYỆT THẬT (Playwright + Chromium).

Tầng Python mù hoàn toàn với loại lỗi này. Chuỗi giao diện được dịch ở
`js/*.js` bằng `t()`, và bệnh kinh điển là **dịch một lần rồi cất câu đã
dịch** — vẽ lại bao nhiêu lần cũng ra nguyên tiếng cũ.

Ba chỗ đã tái hiện được trước khi vá, đều nằm ở ô nạp tệp, tức là chỗ
người dùng chạm vào đầu tiên:

  1. Hàng chờ vẫn ghi "Nhận diện: Danh sách CLB" sau khi sang tiếng Anh
  2. Tóm tắt sau khi nhập vẫn ghi "Xong: 5 CLB mới, 0 cập nhật…"
  3. Nút xoá đang chờ xác nhận vẫn ghi "Bấm lần nữa để xoá…"

Máy nào không có playwright/Chromium thì bỏ qua cả file.
"""

import os
import re
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAU = os.path.join(GOC, "mau_csv")
SO_VI_DU = os.path.join(MAU, "vi_du_day_du", "SO_NHAP_CLB_vi_du.xlsx")

from _trinh_duyet import CHROMIUM  # noqa: E402
from _so_nhap_mau import CHO_SAN_SANG, tha_va_nhap  # noqa: E402


def _cap_chuoi_vi_en():
    """Đọc UI_STRINGS trong i18n.js, trả về {khoá: câu tiếng Việt} cho
    những khoá mà bản tiếng Anh khác hẳn — dùng để soát chuỗi còn sót."""
    src = open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    ui = src[src.index("const UI_STRINGS"):]
    # Neo vao DAU DONG: tim tron "en: {" se trung ca khoa ket thuc bang
    # "...en" (vd. "loi_ngoai_du_kien: {") trong bang ma loi phia tren.
    vi_tri_vi = ui.index("\n    vi: {")
    vi_tri_en = ui.index("\n    en: {")
    khoi_vi = ui[vi_tri_vi:vi_tri_en]
    khoi_en = ui[vi_tri_en:]
    lay = lambda d: dict(  # noqa: E731
        re.findall(r'^\s{6}([a-z0-9_]+):\s*"((?:[^"\\]|\\.)*)"', d, re.M)
    )
    vi, en = lay(khoi_vi), lay(khoi_en)
    # Chuỗi ngắn dễ trùng với dữ liệu trường nhập (tên CLB…) nên bỏ qua.
    return {k: v for k, v in vi.items()
            if en.get(k) and en[k] != v and len(v) > 12}


@pytest.fixture
def api_co_du_lieu(api):
    api.create_or_update_club("clb_a", "CLB A", 3, 1, "chinh_sach")
    for sid in ("HS01", "HS02"):
        api.create_student_if_missing(sid, "Học sinh " + sid)
        api.set_student_reserve_group(sid, "chinh_sach")
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
        api.submit_club_scores("clb_a", [{"student_id": sid, "score": 8.0}])
    return api


@pytest.fixture
def trang(api_co_du_lieu):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api_co_du_lieu, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        yield page, loi, api_co_du_lieu
        br.close()


def _sang_tieng_anh(page):
    page.locator("#btnLangToggle").click()
    page.wait_for_function("document.documentElement.lang === 'en'")


def _dem_hoc_sinh(api):
    conn = sqlite3.connect(api.db_path)
    n = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    return n


def test_hang_cho_nap_tep_doi_ngon_ngu(trang):
    """Thả sổ rồi đổi ngôn ngữ: dòng tóm tắt phải sang tiếng Anh.

    Hàng chờ không thuộc tab nào nên vòng lặp vẽ-lại-theo-tab không chạm
    tới. Trước bản vá nó đứng nguyên tiếng Việt."""
    page, loi, _ = trang
    page.locator("#fileAny").set_input_files([SO_VI_DU])
    page.wait_for_function(CHO_SAN_SANG)
    truoc = page.locator("#importQueue").inner_text()
    assert "Sẵn sàng" in truoc, truoc

    _sang_tieng_anh(page)
    page.wait_for_function(
        "document.querySelector('#importQueue').innerText.indexOf('Sẵn sàng') === -1",
        timeout=8000,
    )
    sau = page.locator("#importQueue").inner_text()
    assert "Ready to import" in sau, sau
    # Tên tệp là dữ liệu, không phải chuỗi giao diện — phải giữ nguyên.
    assert "SO_NHAP_CLB_vi_du.xlsx" in sau
    assert not loi, loi


def test_tom_tat_sau_khi_nhap_doi_ngon_ngu(trang):
    """Nhập xong rồi đổi ngôn ngữ: dòng "Xong: … " phải sang tiếng Anh.

    Đây là ca khó hơn: kết quả được cất SAU khi nhập, nên phải cất khoá +
    tham số chứ không cất câu đã dịch."""
    page, loi, _ = trang
    tha_va_nhap(page, SO_VI_DU)
    assert "Xong" in page.locator("#importQueue").inner_text()

    _sang_tieng_anh(page)
    page.wait_for_function(
        "document.querySelector('#importQueue').innerText.indexOf('Xong') === -1",
        timeout=8000,
    )
    sau = page.locator("#importQueue").inner_text()
    assert "Done" in sau, sau
    # Con số phải giữ nguyên, chỉ câu chữ đổi.
    assert "9 club" in sau and "24 student" in sau, sau
    assert not loi, loi


def test_nut_dang_cho_xac_nhan_duoc_nha_ra(trang):
    """Đổi ngôn ngữ khi một nút xoá đang chờ xác nhận.

    Phần quan trọng nhất KHÔNG phải cái nhãn: nhả nhãn mà quên nhả trạng
    thái là biến nút hai bước thành nút MỘT bước — bấm một phát sau đó là
    xoá thật. Test kiểm tra cả hai."""
    page, loi, api = trang
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector("#btnResetAll")
    nut = page.locator("#btnResetAll")
    nhan_goc_vi = nut.inner_text()

    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetAll').classList.contains('is-confirming')"
    )
    assert nut.inner_text() != nhan_goc_vi

    # Hạn 1,5 giây là CỐ Ý. armTwoStepConfirm tự nhả sau 4 giây, nên hạn
    # rộng hơn thì test xanh nhờ bộ đếm đó chứ không phải nhờ việc đổi
    # ngôn ngữ — đúng cái bẫy đã làm bản test đầu tiên xanh giả.
    _sang_tieng_anh(page)
    page.wait_for_function(
        "!document.querySelector('#btnResetAll').classList.contains('is-confirming')",
        timeout=1500,
    )
    nhan_sau = nut.inner_text()
    assert "Bấm lần nữa" not in nhan_sau, nhan_sau
    assert "Delete all data" in nhan_sau, nhan_sau

    # Nút đã nhả THẬT: bấm một phát không được xoá gì.
    assert _dem_hoc_sinh(api) == 2
    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetAll').classList.contains('is-confirming')"
    )
    assert _dem_hoc_sinh(api) == 2, "mot cu bam da xoa — nut hai buoc bi nha mat trang thai"
    assert not loi, loi


def test_khong_tab_nao_con_sot_chuoi_tieng_viet(trang):
    """Quét cả 5 tab, đối chiếu toàn bộ cặp chuỗi vi/en trong i18n.js.

    Đây là lưới an toàn cho tương lai: thêm màn hình mới mà quên dịch
    phần động thì test này đỏ, không cần ai nhớ ra."""
    page, loi, _ = trang
    khac = _cap_chuoi_vi_en()
    assert len(khac) > 100, "doc i18n.js that bai, chi lay duoc %d chuoi" % len(khac)

    _sang_tieng_anh(page)
    sot_tat_ca = {}
    for tab in ("pipeline", "results", "fallback", "admin", "scoring"):
        page.locator('[data-tab="%s"]' % tab).click()
        page.wait_for_timeout(400)
        chu = page.locator("body").inner_text()
        sot = {k: v for k, v in khac.items() if v in chu}
        if sot:
            sot_tat_ca[tab] = sot
    assert not sot_tat_ca, sot_tat_ca
    assert not loi, loi
