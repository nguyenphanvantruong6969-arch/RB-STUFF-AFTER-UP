"""Chữ đọc được phải dùng Be Vietnam Pro, không dùng phông "mã" đơn cách.

Lỗi thật (27/09, ảnh chụp của người dùng): tên CLB và tên học sinh ở tab
Kết quả hiện bằng IBM Plex Mono — mọi chữ rộng bằng nhau nên tên tiếng Việt
thưa, dấu chồng chật, "CLB Bóng bầu dục" gãy thành hai dòng. Be Vietnam Pro
được vẽ riêng cho tiếng Việt; số vẫn thẳng cột nhờ tabular-nums. Phông đơn
cách chỉ còn cho MÃ (HS001, clb_bongro, tên tệp, seed).
"""

import os
import re

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHONG = os.path.join(GOC, "assets", "fonts")


def _doc(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def test_bien_phong_than_la_be_vietnam_pro():
    css = _doc(os.path.join(GOC, "style.css"))
    m = re.search(r"--font-body:\s*([^;]+);", css)
    assert m and m.group(1).strip().startswith('"Be Vietnam Pro"')


def test_net_400_co_tep_va_duoc_khai_bao():
    css = _doc(os.path.join(PHONG, "fonts.css"))
    for bo in ("vietnamese", "latin"):
        ten = "be-vietnam-pro-%s-400-normal.woff2" % bo
        assert os.path.getsize(os.path.join(PHONG, ten)) > 1000
        assert ten in css


def test_moi_tep_fonts_css_tro_toi_deu_ton_tai():
    css = _doc(os.path.join(PHONG, "fonts.css"))
    for ten in re.findall(r"url\(['\"]?([^'\")]+)", css):
        assert os.path.exists(os.path.join(PHONG, ten)), ten
    assert "IBM Plex Sans" not in css


# ------------------------------------------------------------------ #
# Trình duyệt thật: chữ thực sự vẽ bằng Be Vietnam Pro
# ------------------------------------------------------------------ #

pw = pytest.importorskip("playwright.sync_api", reason="chưa cài playwright")

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_bong_bau_duc", "CLB Bóng bầu dục", 3, 0, "")
    for i in range(1, 4):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Nguyễn Thị Ánh %02d" % i)
        api.submit_preferences(sid, ["clb_bong_bau_duc"])
    assert api.run_pipeline(seed=1)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with pw.sync_playwright() as p:
        br = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('.nav-item[data-tab="results"]').click()
        page.evaluate("document.fonts.ready")
        yield page
        br.close()


def _phong(page, sel):
    return page.evaluate(
        "s => getComputedStyle(document.querySelector(s)).fontFamily", sel)


def _mo(page, panel, cho):
    page.wait_for_selector("#%s .panel-toggle" % panel)
    page.click("#%s .panel-toggle" % panel)
    page.wait_for_selector(cho)


def test_ten_clb_o_bang_lap_day_dung_be_vietnam_pro(trang):
    _mo(trang, "fillPanel", ".fill-name")
    assert _phong(trang, ".fill-name").startswith('"Be Vietnam Pro"')


def test_ten_hoc_sinh_o_danh_sach_xep_dung_be_vietnam_pro(trang):
    _mo(trang, "dsXepPanel", "#resultsTableBody tr td")
    o = trang.locator("#resultsTableBody tr").first.locator("td")
    ten = o.nth(1).evaluate("e => getComputedStyle(e).fontFamily")
    ma = o.nth(0).evaluate("e => getComputedStyle(e).fontFamily")
    assert ten.startswith('"Be Vietnam Pro"')
    assert "Mono" in ma                    # mã HS vẫn giữ đơn cách


def test_phong_be_vietnam_pro_400_thuc_su_nap_duoc(trang):
    ok = trang.evaluate(
        "async () => { await document.fonts.load('400 16px \"Be Vietnam Pro\"', 'ầể');"
        " return document.fonts.check('400 16px \"Be Vietnam Pro\"', 'ầể'); }")
    assert ok
