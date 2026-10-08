"""Trợ năng (rà soát 26/09) — kiểm bằng trình duyệt thật và bằng số đo.

  - ngôn ngữ đã lưu phải khớp <html lang> ngay khi mở
  - tab Nhập tại chỗ dùng được bằng bàn phím
  - mọi ô nhập đều có tên đọc được, không chỉ dựa vào placeholder
  - thông báo được đọc lên (aria-live), lỗi dùng role=alert
  - thanh bên nói thẻ nào đang mở (aria-current)
  - các cặp màu chữ/nền đạt WCAG AA 4,5:1
"""

import os
import re

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ------------------------------------------------------------------ #
# Tương phản — không cần trình duyệt
# ------------------------------------------------------------------ #


def _do_sang(hex_):
    h = hex_.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def _ti_le(a, b):
    a, b = _do_sang(a), _do_sang(b)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


@pytest.fixture(scope="module")
def token():
    css = open(os.path.join(GOC, "style.css"), encoding="utf-8").read()
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9A-Fa-f]{6})", css))


@pytest.mark.parametrize("chu, nen", [
    ("gold-text", "gold-soft"),
    ("rust-text", "rust-soft"),
    ("rust-text", "paper"),
    ("gold-text", "paper-raised"),
    ("ink", "paper"),
])
def test_cap_mau_chu_nen_dat_wcag_aa(token, chu, nen):
    assert _ti_le(token[chu], token[nen]) >= 4.5, (chu, nen)


def test_chu_vang_goc_khong_con_dung_tren_nen_vang_nhat():
    """Cặp cũ chỉ 2,2:1. Không được quay lại."""
    css = open(os.path.join(GOC, "style.css"), encoding="utf-8").read()
    for dong in css.splitlines():
        if "background: var(--gold-soft)" in dong:
            assert not re.search(r"(?<![-\w])color: var\(--gold\)", dong), dong


# ------------------------------------------------------------------ #
# Trình duyệt thật
# ------------------------------------------------------------------ #

pw_mod = pytest.importorskip("playwright.sync_api", reason="chưa cài playwright")
sync_playwright = pw_mod.sync_playwright

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def api_co_du_lieu(api):
    api.create_or_update_club("clb_a", "CLB A", 3, 0, "")
    api.create_or_update_club("clb_b", "CLB B", 3, 0, "")
    api.create_student_if_missing("HS01", "An")
    return api


@pytest.fixture
def mo_trang(api_co_du_lieu):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api_co_du_lieu, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

        def _mo(ngon_ngu=None):
            page = br.new_page(bypass_csp=True)
            if ngon_ngu:
                page.add_init_script(
                    f"try {{ localStorage.setItem('rbda_lang', '{ngon_ngu}'); }} catch (e) {{}}")
            page.goto(url)
            page.wait_for_selector("#dropZone")
            return page

        yield _mo
        br.close()


def test_ngon_ngu_da_luu_khop_lang_ngay_khi_mo(mo_trang):
    page = mo_trang("en")
    assert page.evaluate("document.documentElement.lang") == "en"


def test_tab_nhap_tai_cho_dung_duoc_bang_ban_phim(mo_trang):
    page = mo_trang()
    page.locator('.nav-item[data-tab="fallback"]').click()
    hang = page.locator(".hs-card").first
    hang.wait_for()
    assert hang.get_attribute("role") == "button"
    hang.focus()
    page.keyboard.press("Enter")
    page.wait_for_selector("#fallbackWorkArea:not([hidden])")

    o = page.locator("#testSelectionGrid .option-row").first
    assert o.get_attribute("role") == "checkbox"
    assert o.get_attribute("aria-checked") == "false"
    o.focus()
    page.keyboard.press(" ")
    assert o.get_attribute("aria-checked") == "true"


def test_moi_o_nhap_deu_co_ten_doc_duoc(mo_trang):
    page = mo_trang()
    thieu = page.evaluate("""() => Array.from(
        document.querySelectorAll('input:not([type=hidden]):not([hidden]), select')
      ).filter((o) => !(o.labels && o.labels.length)
                      && !o.getAttribute('aria-label')
                      && !o.closest('label'))
       .map((o) => o.id || o.className)""")
    assert thieu == []


def test_thong_bao_duoc_doc_len(mo_trang):
    page = mo_trang()
    assert page.locator("#toastStack").get_attribute("aria-live") == "polite"
    page.evaluate("document.getElementById('btnImportAll').click()")
    # Không có tệp -> một phản hồi lỗi trong vùng aria-live
    assert page.locator("#feedbackImportAll").get_attribute("aria-live") == "polite"


def test_the_dang_mo_co_aria_current(mo_trang):
    page = mo_trang()
    page.locator('.nav-item[data-tab="admin"]').click()
    assert page.locator('.nav-item[data-tab="admin"]').get_attribute("aria-current") == "page"
    assert page.locator('.nav-item[data-tab="pipeline"]').get_attribute("aria-current") is None
