# -*- coding: utf-8 -*-
"""Mục "Theo từng câu lạc bộ" và danh sách thành viên mở ra dưới nó.

Cả phần mềm trước đây chỉ trả lời được MỘT chiều — *em này vào câu lạc bộ
nào*. Chiều ngược lại, *câu lạc bộ này có những em nào*, đã được xuất ra tệp
từ lâu nhưng không có đường nào lên màn hình, nên cách duy nhất để xem là
bấm Xuất rồi mở từng tệp. Tệp này canh chiều ngược ấy trong TRÌNH DUYỆT
THẬT, vì bốn thứ dưới đây không tầng Python nào thấy được:

1. **Danh sách phải ĐỔI HẲN, không cộng dồn.** Bấm câu lạc bộ thứ hai mà
   bảng cũ còn nguyên bên dưới thì thầy cô phụ trách điểm danh nhầm lớp —
   và không có gì trên màn hình cho thấy điều đó.
2. **Số trên màn hình phải bằng số hàm đọc trả về**, không phải "gần bằng".
3. **Thứ Năm và thứ Sáu phải khác 0 ở cột "Đặt nguyện vọng 1"** — xem
   `tests/test_du_lieu_ket_qua.py` để biết vì sao con số ấy là cái bẫy trung
   tâm của cả tính năng. Test này kiểm nó ở nơi người dùng thật nhìn thấy.
4. **Nút phải lật nhãn** giữa "Xem danh sách" và "Đóng danh sách" — một nút
   không lật là một nút nói dối về việc bấm nó sẽ làm gì.

ĐỐI CHỨNG NGƯỢC đã chạy thật — kết quả ghi ở cuối tệp.

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


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]
    assert api.run_pipeline(seed=42)["ok"]

    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.click('.nav-item[data-tab="results"]')
    # Mục này THU GỌN SẴN (xem MAC_DINH_DONG), nên phải mở ra trước: một
    # hàng nằm trong thân đang đóng thì Playwright coi là chưa hiện, và
    # `wait_for_selector` sẽ chờ hết giờ chứ không báo gì rõ ràng.
    page.wait_for_selector("#clbPanel .panel-toggle")
    page.click("#clbPanel .panel-toggle")
    page.wait_for_selector("#clbBody tr")
    yield page, loi, api
    br.close()
    pw.stop()


def _dong_clb(page):
    """[(ma_clb, so_dang_ky, so_dat_nv1, da_xep)] đọc từ màn hình."""
    return page.eval_on_selector_all(
        "#clbBody tr",
        "rs => rs.map(r => [...r.children].map(c => c.textContent.trim()))")


# ------------------------------------------------------------------ #
# 1. SỐ TRÊN MÀN HÌNH = SỐ HÀM ĐỌC TRẢ VỀ
# ------------------------------------------------------------------ #

def test_moi_cau_lac_bo_mot_dong_va_so_khop_ham_doc(trang):
    page, _, api = trang
    tu_ham = {c["club_id"]: c for c in api.get_club_fill_stats()["data"]}
    dong = _dong_clb(page)
    assert len(dong) == len(tu_ham), (len(dong), len(tu_ham))

    for o in dong:
        c = tu_ham[o[1]]
        assert o[3] == str(c["so_dang_ky"]), o
        assert o[4] == str(c["so_dat_nv1"]), o
        assert o[5] == str(c["capacity"]), o
        assert o[6] == str(c["matched"]), o


def test_dat_nv1_khac_khong_o_moi_buoi_tren_man_hinh(trang):
    """Cái bẫy trung tâm, kiểm ở nơi người dùng thật nhìn thấy: một câu
    truy vấn ngây thơ sẽ làm thứ Năm và thứ Sáu hiện SỐ KHÔNG."""
    page, _, _ = trang
    theo_buoi = {}
    for o in _dong_clb(page):
        theo_buoi[o[0]] = theo_buoi.get(o[0], 0) + int(o[4])

    assert set(theo_buoi) >= {"thu_5", "thu_6"}, theo_buoi
    for b, n in theo_buoi.items():
        assert n > 0, "buoi %s hien 0 em dat nguyen vong 1" % b


def test_ti_le_choi_viet_theo_kieu_viet_nam(trang):
    page, _, _ = trang
    so = [o[7] for o in _dong_clb(page)]
    assert any("," in x for x in so), so
    assert not any("." in x for x in so), so


# ------------------------------------------------------------------ #
# 2. DANH SÁCH THÀNH VIÊN
# ------------------------------------------------------------------ #

def test_bam_mot_cau_lac_bo_thi_hien_dung_so_thanh_vien(trang):
    page, _, api = trang
    assert page.eval_on_selector("#clbDsArea", "e => e.hidden") is True

    page.click("#clbBody tr:first-child button")
    page.wait_for_selector("#clbDsArea:not([hidden])")

    ma = _dong_clb(page)[0][1]
    mong_doi = len(api.get_danh_sach_clb(ma)["data"]["thanh_vien"])
    assert mong_doi > 0
    assert page.eval_on_selector_all("#clbDsBody tr", "e => e.length") == mong_doi
    assert ma in [c["club_id"] for c in api.get_club_fill_stats()["data"]]


def test_bam_cau_lac_bo_khac_thi_danh_sach_doi_han_khong_cong_don(trang):
    """Bảng cũ còn nguyên bên dưới = thầy cô phụ trách điểm danh nhầm lớp."""
    page, _, api = trang
    page.click("#clbBody tr:first-child button")
    page.wait_for_selector("#clbDsArea:not([hidden])")
    truoc = page.inner_text("#clbDsBody")
    tieu_de_truoc = page.inner_text("#clbDsTieuDe")

    page.click("#clbBody tr:nth-child(2) button")
    page.wait_for_timeout(600)
    sau = page.inner_text("#clbDsBody")

    assert sau != truoc
    assert page.inner_text("#clbDsTieuDe") != tieu_de_truoc
    ma2 = _dong_clb(page)[1][1]
    assert (page.eval_on_selector_all("#clbDsBody tr", "e => e.length")
            == len(api.get_danh_sach_clb(ma2)["data"]["thanh_vien"]))


def test_nut_lat_nhan_va_bam_lai_thi_dong(trang):
    page, _, _ = trang
    page.click("#clbBody tr:first-child button")
    page.wait_for_selector("#clbDsArea:not([hidden])")
    assert page.inner_text("#clbBody tr:first-child button").strip() == "Đóng danh sách"

    page.click("#clbBody tr:first-child button")
    page.wait_for_timeout(400)
    assert page.eval_on_selector("#clbDsArea", "e => e.hidden") is True
    assert page.inner_text("#clbBody tr:first-child button").strip() == "Xem danh sách"


def test_danh_sach_thanh_vien_co_hang_nguyen_vong_va_dien(trang):
    """Đây là thẻ Kết quả, không phải thẻ Chấm điểm: ở đây được phép hiện
    thứ hạng nguyện vọng. Thẻ 05 vẫn chấm mù và không đụng tới hàm này."""
    page, _, _ = trang
    page.click("#clbBody tr:first-child button")
    page.wait_for_selector("#clbDsArea:not([hidden])")
    dong = page.inner_text("#clbDsBody tr:first-child")
    assert "Tổng quát" in dong or "Dự trữ" in dong, dong


def test_doi_ngon_ngu_thi_tieu_de_danh_sach_cung_dich(trang):
    """Tiêu đề mang TÊN câu lạc bộ nên là chữ động — applyStaticText()
    không dịch nổi, phải mở lại như thẻ 05 vẫn làm."""
    page, _, _ = trang
    page.click("#clbBody tr:first-child button")
    page.wait_for_selector("#clbDsArea:not([hidden])")
    assert page.inner_text("#clbDsTieuDe").startswith("Thành viên")

    page.click("#btnLangToggle")
    page.wait_for_function(
        "() => document.querySelector('#clbDsTieuDe')"
        ".textContent.trim().startsWith('Members of')")


def test_khong_mot_loi_javascript_nao(trang):
    page, loi, _ = trang
    page.click("#clbBody tr:first-child button")
    page.wait_for_timeout(400)
    page.click("#clbBody tr:nth-child(2) button")
    page.wait_for_timeout(400)
    page.click("#btnLangToggle")
    page.wait_for_timeout(600)
    assert loi == [], loi


# ------------------------------------------------------------------ #
# 3. HAI LỖI TÌM RA KHI SOÁT LẠI, KHÔNG PHẢI KHI VIẾT
# ------------------------------------------------------------------ #

@pytest.fixture
def trang_chay_mot_buoi(api):
    """Trường HAI buổi nhưng chỉ chạy MỘT buổi — `match_results` khi ấy chỉ
    có một buổi, còn danh sách câu lạc bộ vẫn có hai."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_y", "CLB Y", 3, 0, "", "thu_2")
    api.create_or_update_club("clb_z", "CLB Z", 3, 0, "", "thu_4")
    for i in range(5):
        api.create_student_if_missing("HS%d" % i, "Em %d" % i)
        api.submit_preferences("HS%d" % i, ["clb_y", "clb_z"])
    assert api.run_pipeline(seed=1, chi_buoi=["thu_2"])["ok"]

    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.click('.nav-item[data-tab="results"]')
    page.wait_for_selector("#clbPanel .panel-toggle")
    page.click("#clbPanel .panel-toggle")
    page.wait_for_selector("#clbBody tr")
    yield page, loi, api
    br.close()
    pw.stop()


def test_cot_buoi_khong_bi_bang_khac_tat_ho(trang_chay_mot_buoi):
    """LỖI THẬT, đã đo trước khi sửa.

    `loadMatchResults` quét `#view-results .cot-buoi` rồi bật/tắt theo số
    buổi có trong KẾT QUẢ. Bảng này đếm theo DANH SÁCH CÂU LẠC BỘ. Hai quy
    tắc khác nhau ghi lên cùng một lớp CSS thì bên chạy sau thắng — và vì
    hai hàm chạy bất đồng bộ, "bên chạy sau" không cố định.

    Trường hai buổi chạy riêng một buổi: cột Buổi ở đây biến mất, bảng còn
    hai dòng mà không nói nổi dòng nào thuộc buổi nào. Lớp riêng
    `.cot-buoi-clb` cắt hẳn chỗ chạm nhau ấy.
    """
    page, _, _ = trang_chay_mot_buoi
    so_buoi = page.eval_on_selector_all(
        "#clbBody tr", "rs => new Set(rs.map(r => r.children[0].textContent)).size")
    assert so_buoi == 2, so_buoi

    assert page.eval_on_selector(
        "#clbTable thead .cot-buoi-clb", "e => e.hidden") is False
    assert page.eval_on_selector(
        "#clbBody tr:first-child .cot-buoi-clb", "e => e.hidden") is False


def test_truong_mot_buoi_van_giau_cot_buoi(api):
    """Mặt còn lại: trường một buổi thì cột ấy phải ẩn, không phải luôn hiện."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_a", "CLB A", 3)
    api.create_student_if_missing("HS1", "Em Một")
    api.submit_preferences("HS1", ["clb_a"])
    assert api.run_pipeline(seed=1)["ok"]

    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
        page.goto(url)
        page.click('.nav-item[data-tab="results"]')
        page.wait_for_selector("#clbPanel .panel-toggle")
        page.click("#clbPanel .panel-toggle")
        page.wait_for_selector("#clbBody tr")
        assert page.eval_on_selector(
            "#clbTable thead .cot-buoi-clb", "e => e.hidden") is True
        br.close()


def test_cau_lac_bo_bi_xoa_thi_dong_danh_sach_chu_khong_bao_loi_do(trang):
    """LỖI THẬT thứ hai. Mở danh sách một câu lạc bộ rỗng, rồi xoá nó ở thẻ
    Quản lý: quay lại thẻ Kết quả, phần mềm ném một hộp lỗi đỏ lên màn hình
    — tức đang báo động về một việc người dùng vừa CỐ Ý làm.

    (Nhánh xử lý lỗi ấy còn đọc `res.error`, một trường KHÔNG TỒN TẠI —
    trường đúng là `res.errors`, một danh sách. Nên ngay cả thông báo lỗi
    cũng sai.)
    """
    page, loi, api = trang
    assert api.create_or_update_club("clb_rong_moi", "CLB Rỗng Mới", 5)["ok"]
    # Chuyen the roi quay lai de `loadResultsTab` chay lai. KHONG dung
    # `page.reload()`: may chu cuc bo `browser_host` cap ve mot lan cho moi
    # luot mo, tai lai thi moi loi goi phan mem deu hong va bang nao cung
    # trang — test se do vi ly do chang lien quan gi toi loi dang kiem.
    page.click('.nav-item[data-tab="pipeline"]')
    page.click('.nav-item[data-tab="results"]')
    page.wait_for_function(
        "() => [...document.querySelectorAll('#clbBody tr')]"
        ".some(r => r.children[1].textContent.trim() === 'clb_rong_moi')")

    dong = _dong_clb(page)
    vt = [i for i, o in enumerate(dong) if o[1] == "clb_rong_moi"][0]
    page.click("#clbBody tr:nth-child(%d) button" % (vt + 1))
    page.wait_for_selector("#clbDsArea:not([hidden])")

    assert api.delete_club("clb_rong_moi")["ok"]
    page.click('.nav-item[data-tab="pipeline"]')
    page.click('.nav-item[data-tab="results"]')
    page.wait_for_timeout(900)

    assert page.eval_on_selector("#clbDsArea", "e => e.hidden") is True
    assert page.eval_on_selector_all(".toast", "e => e.length") == 0, "co hop loi do"
    assert loi == [], loi


# ====================================================================== #
# ĐỐI CHỨNG NGƯỢC — đã chạy thật trên 9 test của tệp này.
#
#   1. Bỏ `clear(body)` trước khi vẽ danh sách thành viên (tức cộng dồn
#      thay vì vẽ lại)  -> 1 ĐỎ, đúng test "đổi hẳn, không cộng dồn".
#
#   2. Bỏ `if (clbDangMo) moDanhSachCLB(clbDangMo)` khỏi `loadResultsTab`
#      -> 1 ĐỎ, đúng test đổi ngôn ngữ: tiêu đề kẹt lại ở tiếng cũ ngay
#         cạnh một trang đã dịch xong.
#
#   3. Dùng chung lớp `.cot-buoi` với bảng danh sách xếp CLB
#      -> 2 ĐỎ. Trường hai buổi chạy riêng một buổi thì cột Buổi biến mất;
#         và mặt còn lại, trường một buổi thì cột ấy lại hiện ra.
#
#   4. Luôn hiện hộp lỗi đỏ thay vì đóng danh sách khi câu lạc bộ đã bị xoá
#      -> 1 ĐỎ.
#
# Một lỗi THẬT do chính bộ test này tìm ra, không phải do đọc lại mã:
# `dongDanhSachCLB()` bản đầu chỉ ẩn vùng danh sách mà không đụng tới nút,
# nên đóng xong nút vẫn ghi "Đóng danh sách" — một nút nói dối về việc bấm
# nó sẽ làm gì. Sửa bằng `capNhatNhanNutDanhSach()`, và nhân đó bỏ luôn
# một lượt gọi lại `get_club_fill_stats` vốn chỉ để lật một cái nhãn.
# ====================================================================== #
