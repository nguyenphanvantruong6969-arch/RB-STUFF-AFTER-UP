"""Các lỗi giao diện P1 (rà soát 26/09), kiểm bằng TRÌNH DUYỆT THẬT.

  B13 — kết quả tìm kiếm cũ về muộn đè lên kết quả mới
  B14 — xoá hàng chờ rồi mà tệp đang đọc dở vẫn quay lại
  B15 — nút lưu/xuất bấm đúp gửi hai lần
  B16 — đổi ngôn ngữ làm mất điểm chưa lưu và ô đã tick
  B17 — seed 0 không dùng được

Máy nào không có playwright/Chromium thì bỏ qua cả file.
"""

import json
import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAU = os.path.join(GOC, "mau_csv")

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def api_co_du_lieu(api):
    api.create_or_update_club("clb_a", "CLB A", 3, 0, "")
    for i in range(1, 13):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Học sinh %02d" % i)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
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


def _sang_tab(page, tab):
    page.locator(f'.nav-item[data-tab="{tab}"]').click()


def _doi_ngon_ngu(page):
    truoc = page.evaluate("document.documentElement.lang")
    page.locator("#btnLangToggle").click()
    page.wait_for_function(f"document.documentElement.lang !== '{truoc}'")


# ------------------------------------------------------------------ #
# B16
# ------------------------------------------------------------------ #


def test_doi_ngon_ngu_giu_diem_da_go_chua_luu(trang):
    page, loi, _ = trang
    _sang_tab(page, "scoring")
    page.locator("#scoringOverviewBody .btn-row-link").first.click()
    page.wait_for_selector("#scoringTableBody .score-input")
    o = page.locator('#scoringTableBody .score-input[data-student-id="HS03"]')
    o.fill("7,5")

    _doi_ngon_ngu(page)
    page.wait_for_timeout(400)
    assert o.input_value() == "7,5"
    assert loi == []


def test_doi_ngon_ngu_giu_o_da_tick_va_trang_dang_xem(trang):
    page, loi, _ = trang
    _sang_tab(page, "admin")
    page.wait_for_selector(".admin-row-checkbox")
    page.locator('.admin-row-checkbox[data-student-id="HS02"]').check()

    _doi_ngon_ngu(page)
    page.wait_for_timeout(400)
    assert page.locator('.admin-row-checkbox[data-student-id="HS02"]').is_checked()
    assert loi == []


def test_doi_ngon_ngu_ve_lai_tab_nhap_tai_cho(trang):
    """Nút "Bỏ" trong danh sách xếp hạng từng kẹt ở tiếng cũ."""
    page, loi, _ = trang
    _sang_tab(page, "fallback")
    page.wait_for_selector(".hs-card")
    page.locator(".hs-card").first.click()
    page.wait_for_selector("#rankingList li button")
    truoc = page.locator("#rankingList li button").first.inner_text()

    _doi_ngon_ngu(page)
    page.wait_for_timeout(400)
    sau = page.locator("#rankingList li button").first.inner_text()
    assert sau != truoc
    assert loi == []


# ------------------------------------------------------------------ #
# B17
# ------------------------------------------------------------------ #


def test_seed_0_duoc_gui_dung_la_0(trang):
    page, loi, api = trang
    page.locator("#seedInput").fill("0")
    page.locator("#btnRun").click()
    xac_nhan = page.locator("#runConfirmBar button.btn-primary")
    try:
        xac_nhan.first.click(timeout=1500)
    except Exception:
        pass
    page.wait_for_function(
        "document.querySelector('.step[data-step=\"write_results\"]')"
        " && document.querySelector('.step[data-step=\"write_results\"]').dataset.status === 'done'",
        timeout=15000,
    )
    with sqlite3.connect(api.db_path) as c:
        seed = c.execute("SELECT seed FROM run_history ORDER BY rowid DESC LIMIT 1").fetchone()[0]
    assert seed == 0
    assert loi == []


# ------------------------------------------------------------------ #
# B13 — kết quả cũ về muộn
# ------------------------------------------------------------------ #


def test_ket_qua_tim_kiem_cu_ve_muon_khong_de_len_ket_qua_moi(trang):
    page, loi, _ = trang
    _sang_tab(page, "fallback")
    page.wait_for_selector(".hs-card")

    cho = []

    def cham_yeu_cau_dau(route):
        than = json.loads(route.request.post_data or "{}")
        # Yêu cầu cho "HS0" bị giữ lại, về SAU yêu cầu cho "HS01".
        if than.get("args", [None])[0] == "HS0" and not cho:
            cho.append(route)
            return
        route.continue_()

    page.route("**/__api__/list_students_admin", cham_yeu_cau_dau)
    o = page.locator("#studentSearchInput")
    o.fill("HS0")
    page.wait_for_timeout(500)          # qua debounce -> yêu cầu "HS0" bị giữ
    o.fill("HS01")
    page.wait_for_function(
        "document.querySelectorAll('.hs-card').length === 1")
    assert cho, "yeu cau dau khong bi giu — test khong kiem duoc gi"
    cho[0].continue_()                  # giờ mới để kết quả cũ về
    page.wait_for_timeout(600)
    assert page.locator(".hs-card").count() == 1
    assert "HS01" in page.locator(".hs-card").first.inner_text()
    assert loi == []


# ------------------------------------------------------------------ #
# B14 — xoá hàng chờ
# ------------------------------------------------------------------ #


def test_xoa_hang_cho_thi_tep_dang_doc_do_khong_quay_lai(trang):
    page, loi, _ = trang
    cho = []
    page.route("**/__api__/xem_truoc_so_nhap", lambda r: cho.append(r))
    page.locator("#fileAny").set_input_files(
        [os.path.join(MAU, "vi_du_day_du", "SO_NHAP_CLB_vi_du.xlsx")])
    page.wait_for_timeout(400)
    assert cho, "yeu cau nhan dien khong bi giu — test khong kiem duoc gi"
    page.locator("#btnClearQueue").click()
    cho[0].continue_()
    page.wait_for_timeout(600)
    assert page.locator(".queue-row").count() == 0
    assert loi == []


# ------------------------------------------------------------------ #
# B15 — bấm đúp
# ------------------------------------------------------------------ #


def test_bam_dup_luu_diem_chi_gui_mot_lan(trang):
    page, loi, _ = trang
    _sang_tab(page, "scoring")
    page.locator("#scoringOverviewBody .btn-row-link").first.click()
    page.wait_for_selector("#scoringTableBody .score-input")
    page.locator('#scoringTableBody .score-input[data-student-id="HS01"]').fill("8")

    dem = []

    def dem_goi(route):
        dem.append(1)
        route.continue_()

    page.route("**/__api__/submit_club_scores", dem_goi)
    page.locator("#btnSaveScores").dblclick()
    page.wait_for_timeout(800)
    assert len(dem) == 1
    # và nút mở lại sau khi xong
    assert page.locator("#btnSaveScores").is_enabled()
    assert loi == []


# ------------------------------------------------------------------ #
# CSP không được làm hỏng chính giao diện
# ------------------------------------------------------------------ #


def test_csp_khong_chan_thu_gi_cua_giao_dien(api_co_du_lieu):
    """Mở đủ năm tab: không một vi phạm CSP nào. Có vi phạm nghĩa là một
    phần giao diện (script, phông, kiểu) đã bị trình duyệt chặn.

    Trang RIÊNG, KHÔNG bypass_csp — các test khác phải tắt CSP vì
    wait_for_function của Playwright dùng eval trong trang."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api_co_du_lieu, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        try:
            page = br.new_page()
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            _kiem_csp(page, url, loi)
        finally:
            br.close()


def _kiem_csp(page, url, loi):
    vi_pham = []
    page.on("console", lambda m: vi_pham.append(m.text)
            if "Content Security Policy" in m.text else None)
    page.goto(url)
    page.wait_for_selector("#dropZone")
    for tab in ("results", "fallback", "admin", "scoring", "pipeline"):
        _sang_tab(page, tab)
        page.wait_for_timeout(300)
    page.reload()
    page.wait_for_selector("#dropZone")
    page.wait_for_timeout(300)
    assert vi_pham == []
    assert loi == []
    # Và cầu nối vẫn chạy dưới CSP: nhãn chế độ đã được đặt.
    assert page.evaluate("window.__CHE_DO_HIEN_THI") == "trinh_duyet"
