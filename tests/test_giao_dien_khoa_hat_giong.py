"""Ô hạt giống trong TRÌNH DUYỆT THẬT khi bộ số bốc thăm đã khoá.

Backend đã chặn chạy lại bằng hạt giống khác (`hat_giong_da_khoa`, xem
tests/test_khoa_hat_giong.py). Tệp này canh phần người dùng nhìn thấy:

  * đã khoá thì ô hạt giống hiện ĐÚNG hạt giống đã khoá và không sửa được,
    kèm một dòng nói vì sao và phải bấm nút nào — người dùng không phải gõ
    rồi chạy rồi mới biết là không được;
  * bấm "Vẽ lại số bốc thăm…" thì ô mở ra để nhập hạt giống mới;
  * vẽ lại xong, ô khoá lại ở hạt giống MỚI;
  * đổi ngôn ngữ thì dòng giải thích đổi theo.

Máy nào không có playwright/Chromium thì bỏ qua cả tệp.
"""

import io
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_MAU = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")

from _trinh_duyet import CHROMIUM  # noqa: E402


def _mo(api):
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#stbLockLine .lock-dot")
    return pw, br, page, loi


@pytest.fixture
def api_co_du_lieu(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]
    return api


def test_chua_khoa_thi_o_hat_giong_sua_tu_do(api_co_du_lieu):
    pw, br, page, loi = _mo(api_co_du_lieu)
    try:
        o = page.locator("#seedInput")
        assert o.get_attribute("readonly") is None
        assert page.locator("#seedLockHint").is_hidden()
        o.fill("7")
        assert o.input_value() == "7"
        assert loi == []
    finally:
        br.close()
        pw.stop()


def test_da_khoa_thi_o_hat_giong_chi_doc_va_hien_hat_giong_da_khoa(api_co_du_lieu):
    assert api_co_du_lieu.run_pipeline(seed=13)["ok"]
    pw, br, page, loi = _mo(api_co_du_lieu)
    try:
        o = page.locator("#seedInput")
        page.wait_for_function(
            "document.getElementById('seedInput').readOnly === true")
        assert o.input_value() == "13"
        goi_y = page.locator("#seedLockHint")
        assert goi_y.is_visible()
        assert "13" in goi_y.inner_text()
        assert "Bốc thăm lại" in goi_y.inner_text()
        # Gõ vào ô chỉ đọc không đổi được giá trị.
        o.press_sequentially("9")
        assert o.input_value() == "13"
        assert loi == []
    finally:
        br.close()
        pw.stop()


def test_bam_ve_lai_thi_mo_o_va_ve_xong_thi_khoa_o_hat_giong_moi(api_co_du_lieu):
    assert api_co_du_lieu.run_pipeline(seed=13)["ok"]
    pw, br, page, loi = _mo(api_co_du_lieu)
    try:
        page.wait_for_function(
            "document.getElementById('seedInput').readOnly === true")
        page.locator("#stbLockLine .redraw-toggle").click()
        page.wait_for_function(
            "document.getElementById('seedInput').readOnly === false")
        page.locator("#seedInput").fill("21")
        page.locator("#btnRun").click()
        page.locator("#runConfirmBar .btn-primary").click()
        page.wait_for_function(
            "document.getElementById('seedInput').readOnly === true"
            " && document.getElementById('seedInput').value === '21'")
        assert api_co_du_lieu.get_stb_lock_status()["data"]["seed"] == 21
        assert "21" in page.locator("#seedLockHint").inner_text()
        assert loi == []
    finally:
        br.close()
        pw.stop()


def test_doi_ngon_ngu_thi_dong_giai_thich_doi_theo(api_co_du_lieu):
    assert api_co_du_lieu.run_pipeline(seed=13)["ok"]
    pw, br, page, loi = _mo(api_co_du_lieu)
    try:
        page.wait_for_function(
            "document.getElementById('seedInput').readOnly === true")
        page.locator("#btnLangToggle").click()
        page.wait_for_function(
            "document.getElementById('seedLockHint').innerText"
            ".indexOf('Redraw lottery') !== -1")
        assert "13" in page.locator("#seedLockHint").inner_text()
        assert loi == []
    finally:
        br.close()
        pw.stop()
