# -*- coding: utf-8 -*-
"""Thu gọn / mở rộng từng mục ở thẻ Kết quả — kiểm bằng TRÌNH DUYỆT THẬT.

Thẻ Kết quả xếp năm mục chồng nhau và mục dài nhất có một dòng cho mỗi em
mỗi buổi, nên từng mục phải đóng lại được. Tính năng nghe đơn giản, nhưng nó
đứng ngay trên ba cái bẫy mà kho này đã sập một lần rồi — và cả ba chỉ tồn
tại trong trình duyệt, không tầng Python nào thấy được.

BẪY 1 — `applyStaticText()` xoá sạch con của mọi `[data-i18n]`.
    `i18n.js` gán `elm.textContent = t(key)`, nên một nút mũi tên đặt TRONG
    `<h2 data-i18n="…">` sẽ biến mất ngay lần đổi ngôn ngữ đầu tiên. Mũi tên
    ở đây vẽ bằng CSS `::before` trên một nút ANH EM của `<h2>`, không phải
    phần tử con.

BẪY 2 — nhãn nút "Thu gọn tất cả" là chữ ĐỘNG.
    Nó lật sang "Mở rộng tất cả" theo trạng thái, nên `applyStaticText()`
    không dịch nổi: phải vẽ lại trong `reapplyDynamicTextForLangChange()`.
    Con số ở tiêu đề mục cũng vậy.

BẪY 3 — "đang đóng" không phải "chưa có dữ liệu".
    `#doPhuPanel` / `#tkbPanel` / `#thamPanel` đã dùng thuộc tính `hidden`
    trên chính `.panel` để nói *chưa chạy nên chưa có gì*. Nếu thu gọn cũng
    mượn `hidden` trên cùng phần tử ấy thì "Mở rộng tất cả" sẽ lôi cả một
    mục rỗng ra giữa màn hình. Thu gọn chỉ chạm `.panel-body` bên trong.

ĐỐI CHỨNG NGƯỢC đã chạy thật — kết quả ghi ở cuối tệp này.

Máy nào không có playwright/Chromium thì bỏ qua cả tệp.
"""

import io
import json
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_MAU = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")

from _trinh_duyet import CHROMIUM  # noqa: E402

NAM_MUC = ["fillPanel", "clbPanel", "duTruPanel", "doPhuPanel", "nvPanel",
           "chuaCoChoPanel", "tkbPanel", "thamPanel", "dsXepPanel"]

# Lần đầu mở: TẤT CẢ các mục đều đóng — xem MAC_DINH_DONG trong
# js/03_ket_qua.js. Nhà trường chọn vậy (27/09): vừa mở thẻ mà "Tỉ lệ lấp
# đầy" 84 dòng và "Danh sách xếp CLB" đã bung ra là một bức tường chữ.
DONG_SAN = set(NAM_MUC)
KHOA = "rbda_thu_gon_ket_qua_v2"


def _nap(api):
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]


def _mo_the_ket_qua(page, url):
    page.goto(url)
    page.click('.nav-item[data-tab="results"]')
    page.wait_for_selector("#dsXepPanel .panel-toggle")
    return page


def _mo_trang(api):
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    # Ngữ cảnh DỰNG TƯỜNG MINH, không dùng br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1: test tính bền của
    # lựa chọn cần mở một trang THỨ HAI dùng chung kho lưu trữ, mà ngữ cảnh
    # ẩn do br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1 tạo ra chỉ chứa được đúng một trang.
    ctx = br.new_context()
    page = ctx.new_page()
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    _mo_the_ket_qua(page, url)
    return pw, br, ctx, page, loi, url


@pytest.fixture
def trang(api):
    """Đã nhập dữ liệu VÀ đã chạy phân bổ — cả năm mục đều có dữ liệu."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    _nap(api)
    assert api.run_pipeline(seed=42)["ok"]
    pw, br, ctx, page, loi, url = _mo_trang(api)
    page.wait_for_selector("#tkbPanel:not([hidden])")
    yield page, loi, api, ctx, url
    br.close()
    pw.stop()


@pytest.fixture
def trang_chua_chay(api):
    """Đã nhập dữ liệu nhưng CHƯA chạy — ba mục vẫn đang `hidden`."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    _nap(api)
    pw, br, ctx, page, loi, url = _mo_trang(api)
    yield page, loi, api
    br.close()
    pw.stop()


def _dang_mo(page, muc):
    return page.eval_on_selector(
        "#" + muc + "Body", "e => !e.hidden")


def _trang_thai(page):
    return {m: _dang_mo(page, m) for m in NAM_MUC}


# ------------------------------------------------------------------ #
# 1. KHUNG DỰNG ĐÚNG
# ------------------------------------------------------------------ #

def test_moi_muc_deu_co_nut_thu_gon_va_than_rieng(trang):
    page, _, _, _, _ = trang
    for muc in NAM_MUC:
        assert page.query_selector("#" + muc + " .panel-toggle"), muc
        assert page.query_selector("#" + muc + "Body"), muc


def test_mac_dinh_moi_muc_deu_dong(trang):
    """Lần đầu mở: không mục nào bung ra, chỉ tiêu đề kèm con số."""
    page, _, _, _, _ = trang
    tt = _trang_thai(page)
    assert {m for m, mo in tt.items() if not mo} == DONG_SAN, tt
    # nút chung phải mời MỞ, không phải mời thu gọn
    assert page.inner_text("#btnThuGonTatCa").strip() == "Mở rộng tất cả"


def test_ban_chup_mac_dinh_cu_khong_lam_muc_bung_ra_lai(trang):
    """Máy đã bấm thu gọn/mở rộng một lần là đã LƯU cả chín mục theo mặc
    định CŨ ("lấp đầy" và "danh sách xếp CLB" đang mở). Bản ghi đó nằm ở
    khoá cũ và không được làm hai mục ấy bung ra lại."""
    page, _, _, ctx, url = trang
    page.evaluate(
        "() => window.localStorage.setItem('rbda_thu_gon_ket_qua', JSON.stringify("
        "{fillPanel: true, dsXepPanel: true, doPhuPanel: true}))")
    trang_moi = ctx.new_page()
    _mo_the_ket_qua(trang_moi, url)
    trang_moi.wait_for_selector("#tkbPanel:not([hidden])")
    assert all(not mo for mo in _trang_thai(trang_moi).values())


# ------------------------------------------------------------------ #
# 2. ĐÓNG / MỞ
# ------------------------------------------------------------------ #

def test_bam_mot_nut_chi_doi_dung_mot_muc(trang):
    page, _, _, _, _ = trang
    truoc = _trang_thai(page)
    page.click("#dsXepPanel .panel-toggle")
    sau = _trang_thai(page)

    assert sau["dsXepPanel"] is not truoc["dsXepPanel"]
    for m in NAM_MUC:
        if m != "dsXepPanel":
            assert sau[m] == truoc[m], m


def test_hidden_nam_tren_than_muc_khong_phai_tren_chinh_muc(trang):
    """BẪY 3. `hidden` trên `.panel` có nghĩa 'chưa có dữ liệu'. Thu gọn mà
    mượn đúng thuộc tính ấy trên đúng phần tử ấy là trộn hai nghĩa vào một
    chỗ, và không cách nào gỡ ra sau này."""
    page, _, _, _, _ = trang
    # đóng sẵn
    assert page.eval_on_selector("#dsXepPanelBody", "e => e.hidden") is True
    assert page.eval_on_selector("#dsXepPanel", "e => e.hidden") is False
    assert page.get_attribute("#dsXepPanel .panel-toggle", "aria-expanded") == "false"

    page.click("#dsXepPanel .panel-toggle")
    assert page.eval_on_selector("#dsXepPanelBody", "e => e.hidden") is False
    assert page.get_attribute("#dsXepPanel .panel-toggle", "aria-expanded") == "true"

    page.click("#dsXepPanel .panel-toggle")
    assert page.eval_on_selector("#dsXepPanelBody", "e => e.hidden") is True


def test_bam_o_tim_kiem_khong_lam_muc_dong_sap_lai(trang):
    """Cả vùng tiêu đề bấm được, nhưng ô tìm kiếm nằm trong vùng ấy — bấm
    vào ô để gõ mà mục sập lại là một cái bẫy."""
    page, _, _, _, _ = trang
    page.click("#dsXepPanel .panel-toggle")     # mở (đóng sẵn)
    page.click("#resultsSearch")
    assert _dang_mo(page, "dsXepPanel") is True


def test_nut_chung_mo_het_roi_dong_het(trang):
    page, _, _, _, _ = trang
    # đóng sẵn -> nút đang là "Mở rộng tất cả"
    page.click("#btnThuGonTatCa")
    assert all(_trang_thai(page).values())
    assert page.inner_text("#btnThuGonTatCa").strip() == "Thu gọn tất cả"

    page.click("#btnThuGonTatCa")
    assert all(not mo for mo in _trang_thai(page).values())
    assert page.inner_text("#btnThuGonTatCa").strip() == "Mở rộng tất cả"


def test_mo_rong_tat_ca_khong_loi_muc_chua_co_du_lieu_ra(trang_chua_chay):
    """BẪY 3, mặt còn lại: chưa chạy phân bổ thì ba mục kia chưa có gì để
    nói. 'Mở rộng tất cả' không được biến chúng thành ba khung rỗng."""
    page, _, _ = trang_chua_chay
    for muc in ("doPhuPanel", "tkbPanel", "thamPanel"):
        assert page.eval_on_selector("#" + muc, "e => e.hidden") is True, muc

    page.click("#btnThuGonTatCa")          # đóng sẵn -> mở hết

    for muc in ("doPhuPanel", "tkbPanel", "thamPanel"):
        assert page.eval_on_selector("#" + muc, "e => e.hidden") is True, muc


# ------------------------------------------------------------------ #
# 3. TRẠNG THÁI PHẢI SỐNG SÓT
# ------------------------------------------------------------------ #

def test_doi_ngon_ngu_giu_trang_thai_va_dich_ca_hai_nhan(trang):
    """BẪY 1 + BẪY 2 trong một test.

    Đổi ngôn ngữ phải dịch nhãn nút chung (chữ động) và con số ở tiêu đề
    mục, mà KHÔNG được thổi bay lựa chọn đóng/mở người dùng vừa đặt."""
    page, _, _, _, _ = trang
    page.click("#tkbPanel .panel-toggle")      # mở bảng thời khoá biểu
    truoc = _trang_thai(page)
    assert truoc["tkbPanel"] is True and truoc["dsXepPanel"] is False

    page.click("#btnLangToggle")
    page.wait_for_function(
        "() => document.querySelector('#btnThuGonTatCa')"
        ".textContent.trim() === 'Collapse all'")

    assert _trang_thai(page) == truoc, "doi ngon ngu lam mat trang thai"
    assert page.query_selector("#tkbPanel .panel-toggle"), "nut mui ten bi xoa"
    assert "students" in page.inner_text("#tkbPanelDem")


def test_ve_lai_du_lieu_khong_lam_mat_trang_thai(trang):
    """Gõ vào ô tìm kiếm là vẽ lại bảng. Mục đang đóng phải vẫn đóng."""
    page, _, _, _, _ = trang
    assert _dang_mo(page, "dsXepPanel") is False   # đóng sẵn

    page.fill("#resultsSearch", "HS0")
    page.wait_for_timeout(500)                  # qua debounce 250ms
    assert _dang_mo(page, "dsXepPanel") is False


def test_mo_lai_phan_mem_van_giu_trang_thai(trang):
    """Mở lại chương trình phải thấy đúng những mục mình đã đóng.

    Kiểm bằng một CỬA SỔ THỨ HAI cùng ngữ cảnh chứ không phải `page.reload()`:
    máy chủ cục bộ `browser_host` cấp vé một lần cho mỗi lượt mở, nên một
    lần tải lại thì mọi lời gọi phần mềm đều hỏng và bảng nào cũng trắng —
    test sẽ đỏ vì lý do chẳng liên quan gì tới thu gọn."""
    page, _, _, ctx, url = trang
    page.click("#thamPanel .panel-toggle")      # mở
    truoc = _trang_thai(page)

    luu = json.loads(page.evaluate(
        "() => window.localStorage.getItem('%s')" % KHOA))
    assert luu["dsXepPanel"] is False and luu["thamPanel"] is True, luu
    assert luu["tkbPanel"] is False, luu

    trang_moi = ctx.new_page()
    _mo_the_ket_qua(trang_moi, url)
    trang_moi.wait_for_selector("#tkbPanel:not([hidden])")
    assert _trang_thai(trang_moi) == truoc


def test_lua_chon_da_luu_duoc_ton_trong(trang):
    """Người dùng đã mở "lấp đầy" và "độ phủ" thì lần sau vẫn thấy chúng
    mở; mục người ấy chưa từng chạm theo mặc định (đóng)."""
    page, _, _, ctx, url = trang
    page.evaluate(
        "() => window.localStorage.setItem('%s',"
        " JSON.stringify({fillPanel: true, doPhuPanel: true}))" % KHOA)

    trang_moi = ctx.new_page()
    _mo_the_ket_qua(trang_moi, url)
    trang_moi.wait_for_selector("#tkbPanel:not([hidden])")
    tt = _trang_thai(trang_moi)
    assert tt["fillPanel"] is True and tt["doPhuPanel"] is True
    for muc in NAM_MUC:
        if muc not in ("fillPanel", "doPhuPanel"):
            assert tt[muc] is False, muc


# ------------------------------------------------------------------ #
# 4. ĐÓNG LẠI KHÔNG ĐƯỢC TRÔNG NHƯ MẤT BẢNG
# ------------------------------------------------------------------ #

def test_muc_dang_dong_van_noi_no_chua_bao_nhieu(trang):
    page, _, api, _, _ = trang
    tong = len(api.get_thoi_khoa_bieu()["data"]["hoc_sinh"])
    assert tong > 0

    assert _dang_mo(page, "tkbPanel") is False          # đóng sẵn
    assert page.inner_text("#tkbPanelDem").strip() == "%d học sinh" % tong

    n_clb = len(api.get_club_fill_stats()["data"])
    assert page.inner_text("#fillPanelDem").strip() == "%d câu lạc bộ" % n_clb


def test_khong_mot_loi_javascript_nao(trang):
    page, loi, _, _, _ = trang
    page.click("#btnThuGonTatCa")
    page.click("#btnThuGonTatCa")
    page.click("#btnLangToggle")
    page.wait_for_timeout(300)
    assert loi == [], loi


# ====================================================================== #
# ĐỐI CHỨNG NGƯỢC — đã chạy thật trên 12 test của tệp này.
#
#   1. Đặt nút mũi tên VÀO TRONG `<h2 data-i18n="tkb_title">`
#      -> 5 ĐỎ. Không phải chỉ test đổi ngôn ngữ: `applyStaticText()` chạy
#         ngay lúc nạp trang nên nút bị xoá TRƯỚC KHI ai kịp bấm, mục đó
#         mất luôn cách đóng mở. Đúng bẫy 1.
#
#   2. Gắn `data-i18n="btn_thu_gon_tat_ca"` cho nút chung
#      -> 0 ĐỎ. Đo được thì phải ghi đúng: hôm nay thuộc tính ấy KHÔNG gây
#         hại, vì `applyStaticText()` chạy TRƯỚC `capNhatNutTatCa()` nên
#         chữ động ghi đè lại chữ tĩnh. Cái đang giữ nhãn đúng là LỜI GỌI
#         VẼ LẠI, không phải việc thiếu thuộc tính — nên đối chứng thật cho
#         bẫy 2 là số 3 dưới đây, không phải số này.
#
#   3. Bỏ `capNhatNutTatCa()` + `veLaiCacDemMuc()` khỏi
#      `reapplyDynamicTextForLangChange()`
#      -> 1 ĐỎ (test đổi ngôn ngữ). Nhãn nút và con số kẹt lại ở tiếng cũ
#         ngay cạnh một trang đã dịch xong. Đúng bẫy 2.
#
#   4. Chuyển `hidden` từ `.panel-body` sang chính `.panel` trong `datMuc`
#      -> 9 ĐỎ, trong đó có test mục-chưa-có-dữ-liệu: "Mở rộng tất cả" lôi
#         cả ba khung rỗng ra giữa màn hình. Đúng bẫy 3.
#
#   5. Đọc bản ghi dạng mảng cũ theo kiểu "không có trong mảng = đang mở"
#      -> 1 ĐỎ, đúng test bẫy di trú: bốn mục mới mở toang với người đã
#         dùng bản trước.
#
#      Lần đầu em nhắm đối chứng này vào đường GHI (quay lại lưu mảng) và
#      nó đỏ ở một test khác vì `TypeError` — đỏ, nhưng vì lý do sai. Bẫy
#      nằm ở đường ĐỌC, nên đối chứng phải phá đường đọc.
#
# Khôi phục cả năm -> 13 xanh.
# ====================================================================== #
