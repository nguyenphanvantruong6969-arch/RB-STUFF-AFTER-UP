"""Xuất dữ liệu — đo bằng TRÌNH DUYỆT THẬT (Playwright + Chromium).

Test Python (`test_xuat_du_lieu.py`, `test_thay_doi_ket_qua.py`,
`test_xuat_hoc_sinh.py`) khoá hành vi của API. File này khoá phần NỐI:
mỗi nút, mỗi ô tick trên màn hình gọi đúng hàm và tệp thật sự nằm trên đĩa.

  * thẻ Kết quả: ba ô tuỳ chọn -> đúng ba bộ tệp;
  * chọn học sinh qua hai lần tìm kiếm khác nhau -> tệp có ĐÚNG hai em đó;
  * thẻ 04: đánh dấu -> xuất;
  * dải "kết quả có thể đã cũ" bật khi sửa điểm, tắt khi chạy lại.
"""

import csv
import glob
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def api_hai_lan_chay(api):
    """Chạy hai lần, giữa hai lần đổi điểm -> có đúng 2 em đổi CLB."""
    api.create_or_update_club("clb_a", "CLB A", 1, 0, "")
    api.create_or_update_club("clb_b", "CLB B", 5, 0, "")
    for sid, ten in (("HS01", "Ngô Văn An"), ("HS02", "Lê Thị Bình"), ("HS03", "Trần Chi")):
        api.create_student_if_missing(sid, ten)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a", "clb_b"])
    api.submit_club_scores("clb_a", [
        {"student_id": "HS01", "score": 5}, {"student_id": "HS02", "score": 9},
        {"student_id": "HS03", "score": 4}])
    assert api.run_pipeline(42)["ok"]
    api.submit_club_scores("clb_a", [{"student_id": "HS01", "score": 10}])
    assert api.run_pipeline(42)["ok"]
    return api


@pytest.fixture
def trang(api_hai_lan_chay):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api_hai_lan_chay, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(locale="vi-VN", bypass_csp=True)
        # Mọi mục ở thẻ Kết quả đóng sẵn; các test ở đây làm việc với danh
        # sách xếp CLB nên mở sẵn đúng mục đó, như người dùng đã bấm mở.
        page.add_init_script(
            "try { localStorage.setItem('rbda_thu_gon_ket_qua_v2',"
            " JSON.stringify({dsXepPanel: true})); } catch (e) {}")
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="results"]').click()
        page.wait_for_selector("#resultsTableBody .chon-hs")
        yield page, api_hai_lan_chay, loi
        br.close()


def tai_ve():
    return os.environ["RBDA_THU_MUC_TAI_VE"]


def ma_trong_tep(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        # Tệp "thay đổi" có dòng đầu nói so với lần nào và một dòng trống.
        return {r[0] for r in list(csv.reader(f))[1:] if r and r[0].startswith("HS")}


def cho_phan_hoi(page):
    page.wait_for_function(
        "() => document.getElementById('xuatFeedback').textContent.trim().length > 0")
    return page.text_content("#xuatFeedback")


def test_ba_tuy_chon_ra_ba_bo_tep(trang):
    page, api, loi = trang
    page.wait_for_function(
        "() => document.getElementById('xuatThayDoiDem').textContent.includes('2 thay đổi')")
    assert page.is_checked("#xuatKetQua")
    page.check("#xuatDauVao")
    page.check("#xuatThayDoi")
    page.click("#btnXuatTuyChon")
    chu = cho_phan_hoi(page)
    assert "Không xuất được" not in chu, chu
    assert "is-error" not in page.get_attribute("#xuatFeedback", "class")

    # Ket qua: MOT tep Excel, khong rai bo .csv roi khi khong danh dau.
    assert os.path.exists(os.path.join(tai_ve(), "ket_qua_phan_bo.xlsx"))
    assert not os.path.exists(os.path.join(tai_ve(), "ket_qua_phan_bo.csv"))
    assert "Excel" in chu and "Theo CLB" in chu, chu
    # Dữ liệu đầu vào: MỘT Sổ nhập CLB, nạp lại được.
    so = glob.glob(os.path.join(tai_ve(), "SO_NHAP_CLB_*.xlsx"))
    assert len(so) == 1
    assert ma_trong_tep(os.path.join(tai_ve(), "thay_doi_ket_qua.csv")) >= {"HS01", "HS02"}
    assert not loi, loi


def test_kem_csv_thi_ra_ca_bo_csv_cung_ten(trang):
    page, api, loi = trang
    assert not page.is_checked("#xuatKemCsv"), "mac dinh chi xuat Excel"
    page.check("#xuatKemCsv")
    page.click("#btnXuatTuyChon")
    chu = cho_phan_hoi(page)
    assert "Không xuất được" not in chu, chu
    assert os.path.exists(os.path.join(tai_ve(), "ket_qua_phan_bo.xlsx"))
    assert os.path.exists(os.path.join(tai_ve(), "ket_qua_phan_bo.csv"))
    assert os.path.isdir(os.path.join(tai_ve(), "ket_qua_phan_bo_theo_club"))
    assert "CSV" in chu, chu
    assert not loi, loi


def test_csv_hong_van_chi_ra_tep_excel(trang, monkeypatch):
    """CSV rời hỏng (vd tệp cũ đang mở trong Excel) thì vẫn phải thấy đường
    dẫn tệp Excel đã ghi và nút Mở thư mục, kèm câu nói phần CSV hỏng."""
    page, api, loi = trang

    def no(*a, **k):
        raise PermissionError("tep dang mo")
    monkeypatch.setattr(api, "_ghi_bo_csv", no)
    page.check("#xuatKemCsv")
    page.click("#btnXuatTuyChon")
    chu = cho_phan_hoi(page)
    assert "ket_qua_phan_bo.xlsx" in chu, chu
    assert "Tệp Excel đã ghi xong" in chu, chu
    assert "is-error" in page.get_attribute("#xuatFeedback", "class")
    assert page.locator("#xuatFeedback .nut-mo-thu-muc").count() == 1
    assert os.path.exists(os.path.join(tai_ve(), "ket_qua_phan_bo.xlsx"))
    assert not loi, loi


def test_bo_ket_qua_thi_kem_csv_bi_khoa(trang):
    page, api, loi = trang
    page.check("#xuatKemCsv")
    page.uncheck("#xuatKetQua")
    assert page.is_disabled("#xuatKemCsv") and not page.is_checked("#xuatKemCsv")
    page.check("#xuatKetQua")
    assert page.is_enabled("#xuatKemCsv")


def test_khong_tick_muc_nao_thi_bao_loi_khong_xuat(trang):
    page, api, loi = trang
    page.uncheck("#xuatKetQua")
    page.click("#btnXuatTuyChon")
    page.wait_for_function(
        "() => [...document.querySelectorAll('#toastStack .toast')]"
        ".some(t => t.textContent.includes('Chưa chọn mục nào'))")
    assert not os.listdir(tai_ve())


def test_chon_hai_em_qua_hai_lan_tim_roi_xuat_dung_hai_em(trang):
    page, api, loi = trang
    assert page.is_disabled("#btnXuatHsDaChon")

    def tim(chu, ma):
        page.fill("#resultsSearch", chu)
        page.wait_for_function(
            "(ma) => { const c = document.querySelectorAll('#resultsTableBody .chon-hs');"
            " return c.length === 1 && c[0].dataset.studentId === ma; }", arg=ma)
        page.locator("#resultsTableBody .chon-hs").first.check()

    tim("HS01", "HS01")
    tim("binh", "HS02")           # tìm không dấu, và HS01 vẫn phải còn trong tập chọn
    assert "Đã chọn 2 học sinh" in page.text_content("#hsDaChonDem")

    # Xoá ô tìm -> cả ba em hiện lại, đúng hai ô đang tick.
    page.fill("#resultsSearch", "")
    page.wait_for_function(
        "() => document.querySelectorAll('#resultsTableBody .chon-hs').length === 3")
    tick = page.eval_on_selector_all(
        "#resultsTableBody .chon-hs:checked", "els => els.map(e => e.dataset.studentId)")
    assert sorted(tick) == ["HS01", "HS02"]

    page.click("#btnXuatHsDaChon")
    cho_phan_hoi(page)
    p = os.path.join(tai_ve(), "hoc_sinh_da_chon_2_em.csv")
    assert ma_trong_tep(p) == {"HS01", "HS02"}

    page.click("#btnBoChonHs")
    assert page.is_disabled("#btnXuatHsDaChon")
    assert not page.eval_on_selector_all("#resultsTableBody .chon-hs:checked", "e => e.length")
    assert not loi, loi


def test_chon_tat_ca_chi_chon_cac_em_dang_hien(trang):
    page, api, loi = trang
    page.fill("#resultsSearch", "HS0")
    page.wait_for_function(
        "() => document.querySelectorAll('#resultsTableBody .chon-hs').length === 3")
    page.fill("#resultsSearch", "chi")
    page.wait_for_function(
        "() => document.querySelectorAll('#resultsTableBody .chon-hs').length === 1")
    page.check("#chonTatCaKetQua")
    assert "Đã chọn 1 học sinh" in page.text_content("#hsDaChonDem")


def test_the_04_danh_dau_roi_xuat(trang):
    page, api, loi = trang
    page.locator('[data-tab="admin"]').click()
    page.wait_for_selector(".admin-row-checkbox")
    page.locator('.admin-row-checkbox[data-student-id="HS03"]').check()
    page.click("#btnAdminXuatHs")
    page.wait_for_function(
        "() => [...document.querySelectorAll('#toastStack .toast')]"
        ".some(t => t.textContent.includes('Hồ sơ 1 học sinh'))")
    assert ma_trong_tep(os.path.join(tai_ve(), "hoc_sinh_HS03.csv")) == {"HS03"}

    page.check("#adminChonTatCa")
    assert page.eval_on_selector_all(".admin-row-checkbox:checked", "e => e.length") == 3
    assert not loi, loi


def test_dai_ket_qua_cu_bat_khi_sua_tat_khi_chay_lai(trang):
    page, api, loi = trang

    def mo_lai_ket_qua():
        page.locator('[data-tab="scoring"]').click()
        page.locator('[data-tab="results"]').click()
        page.wait_for_timeout(500)

    assert page.is_hidden("#ketQuaCuBanner")
    api.submit_club_scores("clb_a", [{"student_id": "HS03", "score": 7}])
    mo_lai_ket_qua()
    page.wait_for_selector("#ketQuaCuBanner", state="visible")
    api.run_pipeline(42)
    mo_lai_ket_qua()
    page.wait_for_selector("#ketQuaCuBanner", state="hidden")
    assert not loi, loi


def test_bang_ket_qua_so_o_hien_khop_so_cot_tieu_de(trang):
    """Trường một buổi: ô "Buổi" của TỪNG DÒNG phải ẩn cùng tiêu đề. Trước
    đây chỉ tiêu đề ẩn, nên mọi cột dữ liệu lệch sang phải một ô."""
    page, api, loi = trang
    dem = page.evaluate("""() => {
        const hien = (e) => e.offsetParent !== null;
        const th = [...document.querySelectorAll('#dsXepPanel thead th')].filter(hien).length;
        const td = [...document.querySelectorAll('#resultsTableBody tr')].map(
            (tr) => [...tr.children].filter(hien).length);
        return {th, td};
    }""")
    assert dem["td"] and all(n == dem["th"] for n in dem["td"]), dem
