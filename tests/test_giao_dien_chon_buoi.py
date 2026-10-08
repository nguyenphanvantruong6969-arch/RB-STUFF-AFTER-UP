"""Test bộ chọn buổi bằng TRÌNH DUYỆT THẬT (Playwright + Chromium).

Ba lỗi dưới đây không tầng Python nào bắt được, vì chúng nằm ở khoảng cách
giữa CÂU PHẦN MỀM HỨA và VIỆC PHẦN MỀM LÀM — mà câu hứa chỉ tồn tại trong
trình duyệt.

LỖI 1 — thanh xác nhận hứa một phạm vi, chạy một phạm vi khác.
    `runPipelineFlow` dựng câu hứa từ `buoiGuiDi()`, rồi nút Xác nhận gọi
    `executeRun`, mà `executeRun` GỌI LẠI `buoiGuiDi()` lúc gửi. Đổi lựa
    chọn ở giữa hai thời điểm đó thì hai bên nói hai chuyện khác nhau:
    chọn thứ Năm → bấm Chạy → bấm Chọn tất cả → bấm Xác nhận = GHI ĐÈ CẢ
    TUẦN, trong khi hộp thoại vừa hứa các buổi khác giữ nguyên. Hứa sai về
    phạm vi của một việc không hoàn tác được là đúng thứ tính năng này sinh
    ra để tránh.

LỖI 2 — không chọn buổi nào vẫn hiện hộp xác nhận trống.
    `buoiGuiDi()` trả `[]`, mà `[]` là TRUTHY trong JavaScript, nên nhánh
    "chạy một phần" chạy với danh sách rỗng và `{buoi}` thành chuỗi trắng.

LỖI 3 — đổi ngôn ngữ xoá mất dòng nhắc.
    `#chonBuoiNhac` từng mang cả `data-i18n` lẫn nội dung do JavaScript ghi,
    nên `applyStaticText()` ghi đè câu động bằng câu tĩnh và dòng nêu ĐÍCH
    DANH buổi nào được giữ nguyên biến mất, trong khi dải thẻ vẫn hiện một
    lựa chọn một phần.

LỖI 4 — hai ô "Từ/Đến" nói hẹp hơn các thẻ lúc mới nạp.
    `loadChonBuoi()` bật MỌI thẻ rồi dựng lại hai ô dải, mà một `<select>`
    vừa dựng luôn dừng ở lựa chọn đầu tiên. Bộ chọn nói hai điều khác nhau về
    cùng một thứ, và điều SAI lại là điều hẹp hơn.

LỖI 5 — nhập xong, buổi mới không có thẻ nào.
    `loadChonBuoi` chỉ nằm trong `loadPipelineTab()`, mà vùng thả tệp ở CÙNG
    thẻ đó. Nhập một tệp câu lạc bộ mang buổi mới rồi không chuyển thẻ thì
    buổi ấy vô hình với bộ chọn — và nếu người vận hành đã bỏ chọn vài buổi
    từ trước, nó bị loại khỏi lần chạy mà không ai thấy.

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
from _so_nhap_mau import clb, ghi_so, tha_va_nhap  # noqa: E402


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]
    api.run_pipeline(seed=42)     # có kết quả cũ -> bấm Chạy sẽ hỏi xác nhận

    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#chonBuoiChip .buoi-chip")
        yield page, loi, api
        br.close()


def _the(page, nhan):
    return page.locator("#chonBuoiChip .buoi-chip", has_text=nhan).first


class TestThanhXacNhanKhongHuaSai:

    def test_doi_lua_chon_thi_thanh_xac_nhan_bi_go(self, trang):
        page, loi, _api = trang
        # Bỏ chọn hai buổi -> còn một lựa chọn một phần
        _the(page, "thu_6").click()
        _the(page, "thu_5").click()
        page.click("#btnRun")
        page.wait_for_selector("#runConfirmBar")

        # Đổi ý: chọn hết. Câu hứa cũ lập tức sai.
        page.click("#btnChonTatCaBuoi")
        assert page.locator("#runConfirmBar").count() == 0, (
            "thanh xác nhận còn treo với câu hứa đã sai"
        )
        assert loi == []

    def test_bam_the_cung_go_thanh_xac_nhan(self, trang):
        page, loi, _api = trang
        _the(page, "thu_6").click()
        page.click("#btnRun")
        page.wait_for_selector("#runConfirmBar")
        _the(page, "thu_2").click()
        assert page.locator("#runConfirmBar").count() == 0
        assert loi == []

    def test_cau_hua_neu_dich_danh_buoi_se_ghi_de(self, trang):
        page, loi, _api = trang
        _the(page, "thu_6").click()
        page.click("#btnRun")
        page.wait_for_selector("#runConfirmBar")
        cau = page.locator("#runConfirmBar span").inner_text()
        assert "thu_2" in cau and "thu_6" not in cau, cau
        assert loi == []


class TestKhongChonBuoiNao:

    def test_bo_chon_het_thi_bao_ngay_khong_dung_thanh(self, trang):
        page, loi, _api = trang
        for nhan in ("thu_2", "thu_3", "thu_4", "thu_5", "thu_6"):
            _the(page, nhan).click()
        page.click("#btnRun")
        page.wait_for_timeout(300)
        assert page.locator("#runConfirmBar").count() == 0, (
            "dựng hộp xác nhận cho một lựa chọn rỗng"
        )
        assert loi == []


class TestDoiNgonNguGiuDongNhac:

    def test_dong_nhac_van_neu_dung_buoi_sau_khi_doi_ngon_ngu(self, trang):
        page, loi, _api = trang
        _the(page, "thu_6").click()
        truoc = page.locator("#chonBuoiNhac").inner_text()
        assert "thu_6" in truoc, truoc

        page.locator("#btnLangToggle").click()
        page.wait_for_function("document.documentElement.lang === 'en'")
        page.wait_for_timeout(200)

        sau = page.locator("#chonBuoiNhac").inner_text()
        assert sau != truoc, "không đổi ngôn ngữ thì test này không canh được gì"
        # Nhãn buổi là mã thô ở cả hai thứ tiếng; CÂU quanh nó mới đổi.
        assert "thu_6" in sau, sau
        assert loi == []


class TestDaiBuoiKhopVoiThe:
    """Hai ô "Từ/Đến" phải nói đúng điều các thẻ đang nói.

    `loadChonBuoi()` bật MỌI thẻ rồi dựng lại hai ô dải, mà một `<select>`
    vừa dựng luôn dừng ở lựa chọn ĐẦU TIÊN. Nên lúc mới nạp, các thẻ nói
    "cả tuần" trong khi hai ô nói "thứ Hai đến thứ Hai" — và điều sai lại
    là điều HẸP hơn, tức là điều đáng sợ hơn nếu người vận hành tin nó.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ lời gọi `dongBoDaiVoiChip()` trong
    `loadChonBuoi` → test này ĐỎ (ô "Đến" là thu_2 thay vì thu_6).
    """

    def test_luc_nap_hai_o_dai_phu_het_tuan(self, trang):
        page, loi, _api = trang
        ds = page.eval_on_selector_all(
            "#chonBuoiChip .buoi-chip", "els => els.map(e => e.textContent)")

        assert page.input_value("#chonBuoiTu") == ds[0]
        assert page.input_value("#chonBuoiDen") == ds[-1]
        assert loi == []


class TestNhapXongThiBoChonBuoiCapNhat:
    """Buổi mới do một lần nhập sinh ra phải hiện ra ngay, không đợi đổi thẻ.

    `loadChonBuoi` chỉ nằm trong `loadPipelineTab()`, mà vùng thả tệp ở CÙNG
    thẻ đó. Nhập xong không chuyển thẻ thì danh sách buổi còn là danh sách
    trước khi nhập: buổi mới không có thẻ nào, và nếu người vận hành đã bỏ
    chọn vài buổi từ trước thì buổi mới bị loại khỏi lần chạy mà không ai
    thấy.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ lời gọi `loadChonBuoi()` trong
    `nhapTatCa` → test này ĐỎ (vẫn 5 thẻ, không có thu_7).
    """

    def test_them_buoi_moi_thi_hien_the_moi(self, trang, tmp_path):
        page, loi, _api = trang
        assert page.locator("#chonBuoiChip .buoi-chip").count() == 5

        them = ghi_so(tmp_path, "clb_thu_bay.xlsx",
                      [clb("clb_moi_t7", "CLB Thu Bay", buoi="thu_7")])
        tha_va_nhap(page, them)

        # KHONG chuyen the, KHONG nap lai trang.
        page.wait_for_function(
            "document.querySelectorAll('#chonBuoiChip .buoi-chip').length === 6",
            timeout=5000)
        nhan = page.eval_on_selector_all(
            "#chonBuoiChip .buoi-chip", "els => els.map(e => e.textContent)")
        assert nhan[-1] == "thu_7", nhan
        assert loi == []


@pytest.fixture
def trang_tron_buoi(api):
    """Trường khai buổi cho một số câu lạc bộ và BỎ TRỐNG ở số khác.

    Phần mềm chỉ CẢNH BÁO chứ không chặn, nên `__mac_dinh__` có mặt thật
    trong bộ chọn — và đó là nhãn DUY NHẤT có dịch (`nhanBuoi` trả
    `t("buoi_chua_chia")`). Mọi nhãn khác là chữ thô do trường đặt.
    """
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_a", "CLB A", 10, 0, "", buoi="thu_2")
    api.create_or_update_club("clb_b", "CLB B", 10, 0, "", buoi="thu_4")
    api.create_or_update_club("clb_c", "CLB C", 10, 0, "", buoi="")

    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#chonBuoiChip .buoi-chip")
        yield page, loi
        br.close()


class TestDoiNgonNguGiuHaiODai:
    """Đổi ngôn ngữ phải dựng lại cả hai ô "Từ/Đến", và giữ nguyên lựa chọn.

    `reapplyDynamicTextForLangChange` vẽ lại dải thẻ nhưng không gọi
    `veChonBuoiDai()` — hàm đó chỉ có đúng một chỗ gọi là `loadChonBuoi`.
    Phần lớn trường không thấy gì vì nhãn buổi là chữ thô, nhưng
    `nhanBuoi("__mac_dinh__")` trả về chuỗi CÓ DỊCH.

    Đo được trước khi sửa: sau khi chuyển sang tiếng Anh, dải thẻ nói
    "No session set" trong khi hai ô vẫn nói "Chưa chia buổi".

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ `veChonBuoiDai()` khỏi
    `reapplyDynamicTextForLangChange` → `test_option_doi_theo_ngon_ngu` ĐỎ;
    bỏ hai dòng trả lại giá trị → `test_gia_tri_dang_chon_con_nguyen` ĐỎ.
    """

    def _chup(self, page):
        return {
            "the": page.eval_on_selector_all(
                "#chonBuoiChip .buoi-chip", "e => e.map(x => x.textContent)"),
            "option": page.eval_on_selector_all(
                "#chonBuoiTu option", "e => e.map(x => x.textContent)"),
            "tu": page.input_value("#chonBuoiTu"),
            "den": page.input_value("#chonBuoiDen"),
        }

    def _doi_sang_tieng_anh(self, page):
        page.locator("#btnLangToggle").click()
        page.wait_for_function("document.documentElement.lang === 'en'")
        page.wait_for_timeout(300)

    def test_option_doi_theo_ngon_ngu(self, trang_tron_buoi):
        page, loi = trang_tron_buoi
        truoc = self._chup(page)
        assert truoc["the"] == truoc["option"], truoc

        self._doi_sang_tieng_anh(page)
        sau = self._chup(page)

        assert sau["the"] != truoc["the"], "khong doi ngon ngu thi khong canh duoc gi"
        assert sau["option"] == sau["the"], (
            "hai o noi khac dai the: %r vs %r" % (sau["option"], sau["the"]))
        assert loi == []

    def test_gia_tri_dang_chon_con_nguyen(self, trang_tron_buoi):
        """Dựng lại `<option>` sẽ xoá giá trị — phải chụp trước, trả lại sau."""
        page, loi = trang_tron_buoi
        page.select_option("#chonBuoiTu", "thu_2")
        page.select_option("#chonBuoiDen", "thu_4")
        page.wait_for_timeout(200)
        truoc = self._chup(page)

        self._doi_sang_tieng_anh(page)
        sau = self._chup(page)

        assert (sau["tu"], sau["den"]) == (truoc["tu"], truoc["den"]), (
            "doi ngon ngu lam mat lua chon: %r -> %r"
            % ((truoc["tu"], truoc["den"]), (sau["tu"], sau["den"])))
        assert loi == []


def _dang_chon(page):
    return page.eval_on_selector_all(
        "#chonBuoiChip .buoi-chip.is-chon", "els => els.map(e => e.textContent)")


class TestChuyenTheGiuLuaChon:
    """Chọn một buổi, sang thẻ khác xem, quay lại: lựa chọn phải còn nguyên.

    Trước bản vá, `loadPipelineTab()` gọi `loadChonBuoi()` mỗi lần mở thẻ,
    và hàm đó đặt lại thành CHỌN HẾT. Người vận hành chọn thứ Năm, sang thẻ
    Kết quả xem, quay về bấm Chạy — và ghi đè cả tuần, kể cả những buổi đã
    công bố. Thanh xác nhận khi ấy cũng chỉ còn câu chung chung.
    """

    def test_quay_lai_the_van_chi_chon_thu_5(self, trang):
        page, loi, _api = trang
        for nhan in ("thu_2", "thu_3", "thu_4", "thu_6"):
            _the(page, nhan).click()
        assert _dang_chon(page) == ["thu_5"]

        page.click('.nav-item[data-tab="results"]')
        page.click('.nav-item[data-tab="pipeline"]')
        page.wait_for_timeout(800)       # để loadChonBuoi kịp trả về

        assert _dang_chon(page) == ["thu_5"], "chuyển thẻ làm mất lựa chọn buổi"
        page.click("#btnRun")
        page.wait_for_selector("#runConfirmBar")
        cau = page.locator("#runConfirmBar span").inner_text()
        assert "thu_5" in cau and "thu_2" not in cau, cau
        assert loi == []

    def test_nhap_tep_van_chon_lai_het(self, trang, tmp_path):
        """Sau khi nhập tệp vẫn chọn lại cả tuần — hướng an toàn cũ giữ nguyên."""
        page, loi, _api = trang
        _the(page, "thu_6").click()
        assert "thu_6" not in _dang_chon(page)

        tep = ghi_so(tmp_path, "clb_them.xlsx",
                     [clb("clb_them_t2", "CLB Them", buoi="thu_2")])
        tha_va_nhap(page, tep)
        page.wait_for_function(
            "document.querySelectorAll('#chonBuoiChip .buoi-chip.is-chon').length === 5",
            timeout=5000)
        assert loi == []
