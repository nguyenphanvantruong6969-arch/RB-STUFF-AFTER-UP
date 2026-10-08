"""Test khối "Vùng nguy hiểm" bằng TRÌNH DUYỆT THẬT (Playwright + Chromium).

Có một loại lỗi mà không test Python nào bắt được: đặt chuỗi giao diện
nhầm sang bảng mã lỗi (hoặc ngược lại) trong `i18n.js`. Khi đó `t()` trả
về đúng cái KHOÁ chứ không phải câu tiếng Việt, và người dùng nhìn thấy
`btn_reset_all` in ra trên nút. Dự án đã dính đúng lỗi này một lần và
chỉ phát hiện khi mở app thật.

Nên file này kiểm tra hai điều mà tầng Python mù tịt:
  1. Nhãn nút và tiêu đề khối hiện ra bằng tiếng người, không phải khoá.
  2. Xác nhận hai bước thật sự chặn: bấm MỘT lần không được xoá gì.

Máy nào không có playwright/Chromium thì bỏ qua cả file — đây là lớp
kiểm tra thêm, không phải điều kiện để chạy bộ test.
"""

import os
import sqlite3

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402
from _so_nhap_mau import CHO_SAN_SANG, clb, ghi_so  # noqa: E402


@pytest.fixture
def api_co_du_lieu(api):
    api.create_or_update_club("clb_a", "CLB A", 2, 0, "")
    for sid in ("HS01", "HS02"):
        api.create_student_if_missing(sid, "Học sinh " + sid)
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
        page.locator('[data-tab="admin"]').click()
        page.wait_for_selector("#btnResetAll")
        yield page, loi, api_co_du_lieu
        br.close()


def _dem_hoc_sinh(api):
    conn = sqlite3.connect(api.db_path)
    n = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    return n


def test_nhan_hien_ra_bang_tieng_viet_khong_phai_khoa_i18n(trang):
    """Chuỗi giao diện phải nằm trong UI_STRINGS. Đặt nhầm sang bảng mã
    lỗi thì chỗ này in ra đúng chữ 'btn_reset_all'."""
    page, loi, _ = trang
    for chon in ("#btnResetStudents", "#btnResetAll"):
        chu = page.locator(chon).inner_text().strip()
        assert chu, chon
        assert "_" not in chu, "hien ra khoa i18n thay vi cau chu: %r" % chu

    khoi = page.locator('[data-i18n="danger_zone_title"]')
    assert "Vùng nguy hiểm" in khoi.inner_text()
    an_toan = page.locator('[data-i18n="danger_zone_safety"]').inner_text()
    # Canh hai LỜI HỨA, không canh tên bảng trong cơ sở dữ liệu: câu này
    # từng ghi thẳng "run_history" và đã được viết lại thành "nhật ký các
    # lần chạy" cho đúng luật chữ tiếng Việt sạch
    # (tests/test_giao_dien_tieng_viet_sach.py). Canh theo tên bảng thì hai
    # test canh nhau, và bên thua là bên nào chạy sau.
    assert "sao lưu" in an_toan, an_toan
    assert "Lịch sử các lần sắp xếp được giữ lại" in an_toan, an_toan
    assert not loi, loi


def test_bam_mot_lan_khong_xoa_gi(trang):
    """Bước xác nhận thứ nhất chỉ đổi nhãn nút, tuyệt đối không gọi API."""
    page, loi, api = trang
    assert _dem_hoc_sinh(api) == 2

    nut = page.locator("#btnResetAll")
    nhan_goc = nut.inner_text()
    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetAll').classList.contains('is-confirming')"
    )
    assert nut.inner_text() != nhan_goc
    assert _dem_hoc_sinh(api) == 2, "bam mot lan da xoa mat du lieu"
    assert not loi, loi


def test_bam_lan_hai_moi_xoa_that_va_bao_ten_tep_sao_luu(trang):
    page, loi, api = trang
    nut = page.locator("#btnResetStudents")
    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetStudents').classList.contains('is-confirming')"
    )
    nut.click()

    page.wait_for_function("document.querySelectorAll('.toast').length > 0", timeout=10000)
    thong_bao = page.locator(".toast").first.inner_text()
    assert ".bak-" in thong_bao, "toast phai noi ro da sao luu vao tep nao: %r" % thong_bao
    assert "{" not in thong_bao, "con cho trong chua thay: %r" % thong_bao

    assert _dem_hoc_sinh(api) == 0
    # Pham vi "hoc_sinh" nen CLB phai con nguyen.
    conn = sqlite3.connect(api.db_path)
    assert conn.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 1
    conn.close()
    assert not loi, loi


def test_moi_o_so_tren_man_hinh_cap_nhat_ngay_sau_khi_xoa(trang):
    """Sau khi xoá, KHÔNG chỗ nào trên màn hình được nói số cũ nữa.

    Thanh bên luôn hiện dù đang ở tab nào. Trước bản vá, ngay sau khi
    xoá nó vẫn ghi "Chạy gần nhất: … 2/2 xếp được" cho một lần chạy mà
    dữ liệu đằng sau đã bị xoá sạch — màn hình nói một điều không đúng,
    ngay sau thao tác nguy hiểm nhất trong app.
    """
    page, loi, api = trang
    assert api.run_pipeline(seed=42)["ok"]
    page.locator('[data-tab="pipeline"]').click()
    page.wait_for_function(
        "document.querySelector('#statStudents').textContent !== '—'"
    )
    assert page.locator("#statStudents").inner_text() == "2"
    assert "Chạy gần nhất" in page.locator("#lastRunLine").inner_text()

    page.locator('[data-tab="admin"]').click()
    nut = page.locator("#btnResetStudents")
    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetStudents').classList.contains('is-confirming')"
    )
    nut.click()
    page.wait_for_function("document.querySelectorAll('.toast').length > 0", timeout=10000)

    # Vẫn đang đứng ở tab Quản lý — không được bắt người dùng chuyển tab
    # mới thấy sự thật.
    page.wait_for_function(
        "document.querySelector('#lastRunLine').textContent.indexOf('gần nhất') === -1",
        timeout=10000,
    )
    page.wait_for_function(
        "document.querySelector('#statStudents').textContent === '0'", timeout=10000
    )
    assert page.locator("#statMatched").inner_text() == "0"
    # CLB giữ nguyên vì phạm vi là "học sinh".
    assert page.locator("#statClubs").inner_text() == "1"
    assert not loi, loi


def test_em_da_tim_truoc_khi_xoa_khong_con_tren_man_hinh(trang):
    """Tìm một em ở thẻ Nhập tại chỗ, mở em đó, rồi xoá toàn bộ dữ liệu.

    Trước bản vá, quay lại thẻ Nhập tại chỗ vẫn thấy nguyên chữ đã gõ, thẻ
    kết quả và vùng làm việc của một em không còn tồn tại."""
    page, loi, _ = trang
    page.locator('[data-tab="fallback"]').click()
    page.fill("#studentSearchInput", "HS01")
    page.wait_for_selector('.hs-card[data-student-id="HS01"]')
    page.locator('.hs-card[data-student-id="HS01"]').click()
    page.wait_for_selector("#fallbackWorkArea:not([hidden])")

    page.locator('[data-tab="admin"]').click()
    nut = page.locator("#btnResetAll")
    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetAll').classList.contains('is-confirming')"
    )
    nut.click()
    page.wait_for_function("document.querySelectorAll('.toast').length > 0", timeout=10000)

    page.locator('[data-tab="fallback"]').click()
    page.wait_for_selector("#studentSearchResults .empty-state", timeout=10000)
    assert page.input_value("#studentSearchInput") == ""
    assert page.locator("#fallbackWorkArea").is_hidden()
    assert page.locator(".hs-card").count() == 0
    assert page.input_value("#adminStudentSearch") == ""
    assert not loi, loi


def test_the_tim_kiem_noi_ro_em_da_chon_clb_nao(trang):
    """Thẻ kết quả tìm kiếm phải hiện TÊN CLB đã chọn thi và thứ tự
    nguyện vọng, không chỉ con số."""
    page, loi, _ = trang
    page.locator('[data-tab="fallback"]').click()
    the = page.locator('.hs-card[data-student-id="HS01"]')
    the.wait_for()
    chu = the.inner_text()
    assert "Học sinh HS01" in chu
    assert "CLB DỰ THI" in chu.upper() and "NGUYỆN VỌNG" in chu.upper()
    assert the.locator(".hs-card-dong").nth(0).locator(".hs-chip").inner_text() == "CLB A"
    chip_nv = the.locator(".hs-card-dong").nth(1).locator(".hs-chip")
    assert chip_nv.locator(".hs-chip-hang").inner_text() == "1"
    assert "CLB A" in chip_nv.inner_text()
    assert the.locator(".hs-trang-thai").inner_text() == "Đã nhập đủ"
    assert not loi, loi


def test_the_van_hanh_sach_het_sau_khi_xoa_toan_bo(trang, tmp_path):
    """Xoá toàn bộ dữ liệu thì thẻ đầu tiên (Vận hành) phải trắng như lúc
    mới mở app với CSDL trống.

    Trước bản vá, các ô số về 0 nhưng mọi thứ khác vẫn nằm nguyên: danh
    sách tệp ghi "Đã nhập", cảnh báo nhập, các bước "Xong" của lần chạy cũ,
    số khởi tạo cũ đang bị khoá — nhìn như dữ liệu chưa hề bị xoá."""
    page, loi, api = trang
    page.locator('[data-tab="pipeline"]').click()

    # Một Sổ nhập CLB nạp qua vùng thả tệp -> hàng đợi có dòng "đã nhập".
    tep = ghi_so(tmp_path, "so.xlsx", [clb("clb_b", "CLB B", 3)])
    page.set_input_files("#fileAny", tep)
    page.wait_for_function(CHO_SAN_SANG, timeout=10000)
    page.locator("#btnImportAll").click()
    page.wait_for_function(
        "document.querySelector('#feedbackImportAll').textContent.trim() !== ''",
        timeout=10000,
    )

    # Chạy sắp xếp với số khởi tạo khác mặc định -> stepper ghi "Xong",
    # bốc thăm bị khoá và ô số khởi tạo bị khoá theo.
    page.fill("#seedInput", "7")
    page.locator("#btnRun").click()
    page.wait_for_function(
        "document.querySelector('#stepper .step[data-step=\"write_results\"]')"
        ".dataset.status === 'done'",
        timeout=20000,
    )
    page.wait_for_function(
        "document.querySelector('#seedInput').readOnly === true", timeout=10000
    )

    page.locator('[data-tab="admin"]').click()
    nut = page.locator("#btnResetAll")
    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetAll').classList.contains('is-confirming')"
    )
    nut.click()
    page.wait_for_function("document.querySelectorAll('.toast').length > 0", timeout=10000)

    page.locator('[data-tab="pipeline"]').click()
    page.wait_for_function(
        "document.querySelector('#statClubs').textContent === '0'", timeout=10000
    )
    page.wait_for_function(
        "document.querySelector('#seedInput').readOnly === false", timeout=10000
    )
    # Bốn ô số ở đầu thẻ đều về 0.
    for o in ("#statStudents", "#statClubs", "#statPrefs", "#statMatched"):
        assert page.locator(o).inner_text() == "0", o
    assert page.locator("#importQueue .queue-row").count() == 0
    assert page.locator("#importWarnings").is_hidden()
    assert page.locator("#feedbackImportAll").inner_text().strip() == ""
    trang_thai = page.eval_on_selector_all(
        "#stepper .step", "ds => ds.map(li => li.dataset.status || '')"
    )
    assert trang_thai and all(s == "" for s in trang_thai), trang_thai
    assert page.locator("#logPanel").is_hidden()
    assert page.input_value("#seedInput") == "42"
    assert page.locator("#seedLockHint").is_hidden()
    assert page.locator("#runConfirmBar").count() == 0
    assert not loi, loi


def test_khong_xoa_duoc_khi_dang_nhap_tep(trang, tmp_path):
    """Đang nhập tệp thì nút xoá phải từ chối.

    Không chặn thì chuỗi nhập vẫn chạy tiếp sau khi xoá: các tệp còn lại
    nạp vào CSDL vừa xoá, rồi ghi "Đã nhập xong" đè lên thẻ Vận hành vừa
    dọn sạch."""
    page, loi, api = trang
    page.locator('[data-tab="pipeline"]').click()
    tep = ghi_so(tmp_path, "so.xlsx", [clb("clb_b", "CLB B", 3)])
    page.set_input_files("#fileAny", tep)
    page.wait_for_function(CHO_SAN_SANG, timeout=10000)

    cho = []
    page.route("**/__api__/import_so_nhap", lambda r: cho.append(r))
    page.locator("#btnImportAll").click()
    page.wait_for_function("document.querySelector('#btnImportAll').disabled")
    assert cho, "yeu cau nhap khong bi giu — test khong kiem duoc gi"

    page.locator('[data-tab="admin"]').click()
    nut = page.locator("#btnResetAll")
    nut.click()
    page.wait_for_function(
        "document.querySelector('#btnResetAll').classList.contains('is-confirming')"
    )
    nut.click()
    page.wait_for_function("document.querySelectorAll('.toast').length > 0", timeout=10000)
    assert "Chờ xong" in page.locator(".toast").first.inner_text()
    assert _dem_hoc_sinh(api) == 2, "da xoa du lieu giua luc dang nhap tep"

    cho[0].continue_()
    page.wait_for_function(
        "!document.querySelector('#btnImportAll').disabled", timeout=10000
    )
    conn = sqlite3.connect(api.db_path)
    assert conn.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 2
    conn.close()
    assert not loi, loi
