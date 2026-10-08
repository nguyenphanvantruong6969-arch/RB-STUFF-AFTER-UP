"""Test nút Chạy và thông báo bằng TRÌNH DUYỆT THẬT (Playwright + Chromium).

LỖI 1 — bấm đúp lần chạy đầu tiên là chạy HAI lần.
    `runPipelineFlow` hỏi phần lõi "đã có kết quả chưa" rồi mới khoá nút.
    Lần chạy đầu không cần xác nhận, nên cú bấm thứ hai lọt qua khoảng hở
    đó và gọi `run_pipeline` lần nữa: hai dòng lịch sử cho một lần bấm.

LỖI 2 — trong lúc chạy, màn hình đứng yên ở "Chưa chạy".
    Mọi bước bị đặt về "Chưa chạy" và chỉ vẽ lại khi phần lõi trả về.
    Nhìn như treo; vùng thả tệp và bộ chọn buổi vẫn bấm được giữa chừng.

LỖI 3 — thông báo tự tắt sau 3,6 giây, kể cả lỗi.
    Người dùng chưa đọc xong đã mất; đường dẫn tệp vừa xuất cũng vậy.

LỖI 4 — bước sao lưu và bước hoàn tác không bao giờ hiện ra.
    `renderSteps` bỏ qua mọi bước không có dòng dựng sẵn: sao lưu hỏng
    vẫn báo thành công xanh, và câu trấn an "dữ liệu đã quay về trạng thái
    trước khi chạy" không bao giờ tới mắt người dùng.

Máy nào không có playwright/Chromium thì bỏ qua cả tệp.
"""

import io
import os
import time

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import api as api_module  # noqa: E402
import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_MAU = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")

from _trinh_duyet import CHROMIUM  # noqa: E402
from _so_nhap_mau import CHO_SAN_SANG, clb, ghi_so  # noqa: E402


def _nap_du_lieu(api):
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]


@pytest.fixture
def mo_trang(api):
    """Trả về hàm mở trang; gọi SAU khi đã vá `api` theo ý từng test."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    _nap_du_lieu(api)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])

        def mo():
            url = browser_host.serve(api, GOC, "index.html", open_browser=False)
            page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("#chonBuoiChip .buoi-chip")
            return page, loi

        yield mo
        br.close()


def _cham(ham, giay):
    """Bọc một phương thức API cho nó chậm lại — để thấy trạng thái giữa chừng."""
    def boc(*a, **k):
        time.sleep(giay)
        return ham(*a, **k)
    return boc


def _bo_chon_het_buoi(page):
    for n in page.locator("#chonBuoiChip .buoi-chip").all():
        n.click()


def _so_lan_chay(api):
    return len(api.get_run_history(50)["data"])


class TestKhongChayHaiLan:

    def test_bam_dup_lan_chay_dau_chi_chay_mot_lan(self, api, mo_trang):
        # Hỏi "đã có kết quả chưa" chậm một chút: đúng khoảng hở cũ.
        api.get_pipeline_run_warning = _cham(api.get_pipeline_run_warning, 0.4)
        page, loi = mo_trang()
        assert _so_lan_chay(api) == 0
        page.dblclick("#btnRun")
        page.wait_for_function(
            "!document.querySelector('#btnRun').disabled "
            "&& document.querySelector('.toast.is-success')", timeout=20000)
        page.wait_for_timeout(500)
        assert _so_lan_chay(api) == 1, "một cú bấm đúp chạy sắp xếp hai lần"
        assert loi == [], loi

    def test_nut_chay_khoa_ngay_khi_bam(self, api, mo_trang):
        api.get_pipeline_run_warning = _cham(api.get_pipeline_run_warning, 0.6)
        page, loi = mo_trang()
        page.click("#btnRun")
        assert page.eval_on_selector("#btnRun", "b => b.disabled") is True
        assert loi == [], loi


class TestDangChayThayDuoc:

    def test_trong_luc_chay_cac_buoc_hien_dang_chay_va_bi_khoa(self, api, mo_trang):
        api.run_pipeline = _cham(api.run_pipeline, 1.5)
        page, loi = mo_trang()
        nhan_truoc = page.locator("#btnRun").inner_text()
        page.click("#btnRun")
        page.wait_for_function(
            "document.querySelector('#stepper .step[data-status=\"running\"]')")
        assert page.locator("#btnRun").inner_text() != nhan_truoc
        assert page.eval_on_selector("#btnRun", "b => b.disabled") is True
        assert page.eval_on_selector("#btnValidate", "b => b.disabled") is True
        assert page.eval_on_selector("#btnImportAll", "b => b.disabled") is True
        assert page.eval_on_selector_all(
            "#chonBuoiChip .buoi-chip", "ns => ns.every(n => n.disabled)") is True
        assert page.get_attribute("#dropZone", "aria-disabled") == "true"

        page.wait_for_function(
            "!document.querySelector('#btnRun').disabled", timeout=20000)
        assert page.locator("#btnRun").inner_text() == nhan_truoc
        assert page.locator('#stepper .step[data-status="running"]').count() == 0, (
            "còn bước treo ở 'đang chạy' sau khi đã xong")
        assert page.eval_on_selector_all(
            "#chonBuoiChip .buoi-chip", "ns => ns.every(n => !n.disabled)") is True
        assert loi == [], loi

    def test_huy_thanh_xac_nhan_thi_nut_chay_mo_lai(self, api, mo_trang):
        assert api.run_pipeline(seed=42)["ok"]      # có kết quả cũ -> phải xác nhận
        page, loi = mo_trang()
        page.click("#btnRun")
        page.wait_for_selector("#runConfirmBar")
        assert page.eval_on_selector("#btnRun", "b => b.disabled") is True
        page.click("#runConfirmBar .btn-ghost")
        assert page.eval_on_selector("#btnRun", "b => b.disabled") is False
        # Đổi buổi cũng gỡ thanh xác nhận -> nút Chạy cũng phải mở lại.
        page.click("#btnRun")
        page.wait_for_selector("#runConfirmBar")
        page.locator("#chonBuoiChip .buoi-chip").first.click()
        assert page.locator("#runConfirmBar").count() == 0
        assert page.eval_on_selector("#btnRun", "b => b.disabled") is False
        assert loi == [], loi


class TestThongBaoDocDuoc:

    def test_loi_o_lai_toi_khi_bam_dong(self, api, mo_trang):
        page, loi = mo_trang()
        # Bỏ chọn hết buổi rồi bấm Chạy -> một thông báo lỗi.
        _bo_chon_het_buoi(page)
        page.click("#btnRun")
        page.wait_for_selector(".toast.is-error")
        page.wait_for_timeout(5000)       # quá 3,6 giây cũ
        assert page.locator(".toast.is-error").count() == 1, "lỗi tự tắt trước khi đọc xong"
        assert page.get_attribute(".toast.is-error", "role") == "alert"
        page.click(".toast.is-error .toast-close")
        page.wait_for_function("!document.querySelector('.toast.is-error')")
        assert loi == [], loi

    def test_thong_bao_thanh_cong_van_tu_tat(self, api, mo_trang):
        page, loi = mo_trang()
        page.evaluate("() => document.querySelector('#toastStack').innerHTML = ''")
        page.click("#btnRun")
        page.wait_for_selector(".toast.is-success", timeout=20000)
        page.wait_for_function("!document.querySelector('.toast')", timeout=12000)
        assert loi == [], loi

    def test_vung_thong_bao_duoc_doc_len(self, api, mo_trang):
        page, _ = mo_trang()
        assert page.get_attribute("#toastStack", "aria-live") == "polite"

    def test_khong_de_qua_bon_thong_bao(self, api, mo_trang):
        page, loi = mo_trang()
        _bo_chon_het_buoi(page)
        for _ in range(6):
            page.click("#btnRun")
        page.wait_for_timeout(400)
        assert page.locator(".toast:not(.is-leaving)").count() <= 4
        assert loi == [], loi

    def test_nhac_ve_lai_con_hien_khi_che_do_con_bat(self, api, mo_trang):
        assert api.run_pipeline(seed=42)["ok"]      # có khoá -> có nút vẽ lại
        page, loi = mo_trang()
        page.wait_for_selector("#stbLockLine .redraw-toggle")
        page.click("#stbLockLine .redraw-toggle")
        page.wait_for_selector(".toast.is-warn")
        page.wait_for_timeout(5000)
        assert page.locator(".toast.is-warn").count() == 1
        # Bấm lần nữa = tắt chế độ -> lời nhắc phải biến mất theo.
        page.click("#stbLockLine .redraw-toggle")
        page.wait_for_function("!document.querySelector('.toast.is-warn:not(.is-leaving)')")
        assert loi == [], loi


class TestNhacVeLaiKhongMatKhiConBat:
    """Lời nhắc "sẽ vẽ lại số bốc thăm" phải còn chừng nào chế độ còn bật.

    Giới hạn 4 thông báo từng gỡ luôn lời nhắc này (lỗi và cảnh báo nay ở
    lại tới khi bấm ×, nên dễ chồng lên), trong khi chế độ vẫn bật: bấm
    Chạy là vẽ lại toàn bộ số mà không còn gì trên màn hình báo trước.
    """

    def test_nhieu_thong_bao_khac_khong_go_loi_nhac(self, api, mo_trang):
        assert api.run_pipeline(seed=42)["ok"]
        page, loi = mo_trang()
        page.wait_for_selector("#stbLockLine .redraw-toggle")
        page.click("#stbLockLine .redraw-toggle")
        page.wait_for_selector(".toast.is-warn")
        _bo_chon_het_buoi(page)
        for _ in range(6):
            page.click("#btnRun")      # không chọn buổi nào -> mỗi lần một lỗi
        page.wait_for_timeout(400)
        assert page.locator(".toast.is-warn:not(.is-leaving)").count() == 1, (
            "lời nhắc vẽ lại bị gỡ trong khi chế độ vẫn bật")
        assert page.locator(".toast:not(.is-leaving)").count() <= 5
        assert loi == [], loi

    def test_bam_dong_loi_nhac_la_tat_che_do(self, api, mo_trang):
        assert api.run_pipeline(seed=42)["ok"]
        page, loi = mo_trang()
        page.wait_for_selector("#stbLockLine .redraw-toggle")
        page.click("#stbLockLine .redraw-toggle")
        page.click(".toast.is-warn .toast-close")
        page.click("#btnRun")
        page.wait_for_selector("#runConfirmBar")
        cau = page.locator("#runConfirmBar span").inner_text()
        assert "VẼ LẠI" not in cau, "đã đóng lời nhắc mà chế độ vẽ lại vẫn bật: " + cau
        assert loi == [], loi


class TestBuocSaoLuuVaHoanTac:

    def test_sao_luu_hong_thi_khong_bao_thanh_cong_xanh(self, api, mo_trang):
        def hong():
            raise OSError("dia day")
        api._backup_db = hong
        page, loi = mo_trang()
        page.click("#btnRun")
        page.wait_for_selector(".toast.is-warn", timeout=20000)
        assert page.locator(".toast.is-success").count() == 0
        # Loi goc nam o "Chi tiet ky thuat" (dong san) cua chinh thong bao do.
        assert "dia day" in page.locator(".toast.is-warn .chi-tiet-ky-thuat").text_content()
        assert page.get_attribute('#stepper .step[data-step="backup"]', "data-status") == "error"
        assert loi == [], loi

    def test_hoan_tac_hien_ra_khi_chay_hong(self, api, mo_trang, monkeypatch):
        def hong(*a, **k):
            raise RuntimeError("hong giua chung")
        monkeypatch.setattr(api_module, "generate_stb_lottery", hong)
        page, loi = mo_trang()
        page.click("#btnRun")
        page.wait_for_selector('#stepper .step[data-step="rollback"]', timeout=20000)
        dong = page.locator('#stepper .step[data-step="rollback"]')
        assert dong.get_attribute("data-status") == "done"
        assert dong.locator(".step-title").inner_text().strip() not in ("", "step_title_rollback")
        assert page.locator('#stepper .step[data-step="unknown"]').count() == 1

        # Chạy lại (không hỏng) thì dòng thêm phải biến mất.
        monkeypatch.undo()
        page.click("#btnRun")
        page.wait_for_selector(".toast.is-success", timeout=20000)
        assert page.locator('#stepper .step[data-step="rollback"]').count() == 0
        assert loi == [], loi


class TestHatGiong:
    """Ô hạt giống phải nói đúng số lần chạy trước đã dùng.

    Trước bản vá, ô luôn là 42 sau khi mở app, và `parseInt(...) || 42`
    biến ô trống, số 0 hay "1.5" thành 42 mà không nói gì.
    """

    def test_mo_lai_thi_o_hien_hat_giong_lan_truoc(self, api, mo_trang):
        assert api.run_pipeline(seed=2026)["ok"]
        page, loi = mo_trang()
        page.wait_for_function("document.querySelector('#seedInput').value === '2026'",
                               timeout=5000)
        assert loi == [], loi

    def test_chua_chay_lan_nao_thi_giu_42(self, api, mo_trang):
        page, loi = mo_trang()
        page.wait_for_timeout(500)
        assert page.input_value("#seedInput") == "42"
        assert loi == [], loi

    def test_so_nguoi_dung_go_khong_bi_ghi_de_khi_chuyen_the(self, api, mo_trang):
        assert api.run_pipeline(seed=2026)["ok"]
        page, loi = mo_trang()
        page.wait_for_function("document.querySelector('#seedInput').value === '2026'")
        # Hạt giống khoá cùng bộ số bốc thăm: chỉ gõ được khi đã bật "Vẽ lại".
        page.click("#stbLockLine .redraw-toggle")
        page.fill("#seedInput", "7")
        page.click('.nav-item[data-tab="results"]')
        page.click('.nav-item[data-tab="pipeline"]')
        page.wait_for_timeout(600)
        assert page.input_value("#seedInput") == "7"
        assert loi == [], loi

    @pytest.mark.parametrize("go", ["", "1.5"])
    def test_hat_giong_khong_hop_le_thi_khong_chay(self, api, mo_trang, go):
        page, loi = mo_trang()
        page.fill("#seedInput", go)
        page.click("#btnRun")
        page.wait_for_selector(".toast.is-error")
        page.wait_for_timeout(800)
        assert _so_lan_chay(api) == 0, "chạy với một hạt giống người dùng không chọn"
        assert page.eval_on_selector("#btnRun", "b => b.disabled") is False
        assert loi == [], loi

    def test_hat_giong_0_duoc_dung_that(self, api, mo_trang):
        page, loi = mo_trang()
        page.fill("#seedInput", "0")
        page.click("#btnRun")
        page.wait_for_selector(".toast.is-success", timeout=20000)
        assert api.get_last_run_info()["data"]["seed"] == 0, "0 bị đổi thành 42"
        assert loi == [], loi


class TestThongBaoNoiDungSuThat:
    """Thông báo xanh chỉ khi mọi thứ thật sự ổn.

    Trước bản vá: nhập xong luôn báo xanh "Đã nhập xong {n} tệp" kể cả khi
    có tệp lỗi; "Kiểm tra dữ liệu" báo xanh "hợp lệ" ngay dưới một ô Cảnh
    báo đang nêu lỗi nghiêm trọng.
    """

    def test_nhap_so_loi_thi_bao_loi_khong_bao_xanh(self, api, mo_trang, tmp_path):
        api.import_so_nhap = lambda *a, **k: api_module._fail(
            api_module.err("loi_nap_so_nhap", detail="hong"))

        page, loi = mo_trang()
        so = ghi_so(tmp_path, "so.xlsx", [clb("clb_tot", "CLB Tot", buoi="thu_2")])
        page.locator("#fileAny").set_input_files([so])
        page.wait_for_function(CHO_SAN_SANG)
        page.click("#btnImportAll")
        page.wait_for_selector(".toast.is-error", timeout=15000)

        assert "is-error" in page.get_attribute("#feedbackImportAll", "class")
        assert page.locator(".toast.is-success").count() == 0, "vẫn báo xanh khi nạp lỗi"
        assert loi == [], loi

    def test_nhap_het_tot_van_bao_xanh(self, api, mo_trang, tmp_path):
        page, loi = mo_trang()
        so = ghi_so(tmp_path, "tot.xlsx", [clb("clb_tot", "CLB Tot", buoi="thu_2")])
        page.locator("#fileAny").set_input_files([so])
        page.wait_for_function(CHO_SAN_SANG)
        page.click("#btnImportAll")
        page.wait_for_selector(".toast.is-success", timeout=15000)
        assert page.locator(".toast.is-error").count() == 0
        assert loi == [], loi

    def test_hop_le_nhung_con_canh_bao_nghiem_trong_thi_khong_bao_xanh(self, api, mo_trang):
        # Một em đăng ký thi nhưng câu lạc bộ chưa chấm điểm ai -> cảnh báo "high".
        clb = api.list_clubs()["data"][0]["club_id"]
        assert api.submit_test_selection("HS001", [clb])["ok"]
        n_high = api.get_data_health_report()["data"]["n_high"]
        assert n_high > 0, "dữ liệu test không tạo được cảnh báo nghiêm trọng"

        page, loi = mo_trang()
        page.click("#btnValidate")
        page.wait_for_selector(".toast.is-warn, .toast.is-success", timeout=15000)
        assert page.locator(".toast.is-success").count() == 0, "báo xanh cạnh cảnh báo nghiêm trọng"
        assert str(n_high) in page.locator(".toast.is-warn").inner_text()
        assert loi == [], loi

    def test_hop_le_va_sach_thi_van_bao_xanh(self, api, mo_trang):
        assert api.get_data_health_report()["data"]["n_high"] == 0
        page, loi = mo_trang()
        page.click("#btnValidate")
        page.wait_for_selector(".toast.is-success", timeout=15000)
        assert page.locator(".toast.is-warn").count() == 0
        assert loi == [], loi


class TestKhongLoChuoiKyThuat:

    def test_loi_goi_phan_loi_hien_cau_tieng_viet(self, api, mo_trang):
        """`callApi` từng trả nguyên `String(e)` — ví dụ "TypeError: Failed
        to fetch" — thẳng lên thông báo."""
        page, loi = mo_trang()
        # Cầu nối trình duyệt là một Proxy: bọc nó, cho riêng export_ket_qua hỏng
        # đúng kiểu mất kết nối (fetch bị từ chối).
        page.evaluate("""() => {
            const goc = window.pywebview.api;
            window.pywebview.api = new Proxy({}, {
                get: (_t, ten) => ten === "export_ket_qua"
                    ? () => Promise.reject(new TypeError("Failed to fetch"))
                    : goc[ten],
            });
        }""")
        page.click('.nav-item[data-tab="results"]')
        page.click("#btnXuatTuyChon")   # "Kết quả sắp xếp" được chọn sẵn
        page.wait_for_selector(".toast.is-error")
        chu = page.locator(".toast.is-error").inner_text()
        assert "TypeError" not in chu and "Failed to fetch" not in chu, chu
        assert "phần lõi" in chu, chu
        assert loi == [], loi

    def test_chay_hong_khong_hien_traceback(self, api, mo_trang, monkeypatch):
        def hong(*a, **k):
            raise RuntimeError("hong giua chung")
        monkeypatch.setattr(api_module, "generate_stb_lottery", hong)
        page, loi = mo_trang()
        page.click("#btnRun")
        page.wait_for_selector("#logPanel:not([hidden])", timeout=20000)
        nhat_ky = page.locator("#logBox").inner_text()
        assert "Traceback" not in nhat_ky and 'File "' not in nhat_ky, nhat_ky
        assert "loi_ung_dung.txt" in nhat_ky, nhat_ky
        assert loi == [], loi
