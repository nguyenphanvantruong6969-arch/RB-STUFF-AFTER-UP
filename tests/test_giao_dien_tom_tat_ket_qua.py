"""Dải "Tóm tắt lần xếp", cách sắp xếp biểu đồ lấp đầy và chú thích nổi —
đo bằng TRÌNH DUYỆT THẬT.

Ba điều canh ở đây:

1. Ô tóm tắt nói ĐÚNG con số mà các hàm đọc trả về. Một ô tóm tắt lệch
   khỏi mục chi tiết ngay bên dưới còn tệ hơn không có ô nào.
2. Đổi cách sắp xếp thì thứ tự dòng đổi theo, và lựa chọn đó được nhớ.
3. Rê chuột (hoặc Tab) vào một dòng thì chú thích hiện đúng số của CLB đó.
"""

import io
import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_NHIEU_BUOI = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def api_da_chay(api):
    """Bốn CLB một buổi, mỗi CLB một ca của biểu đồ:

      clb_day  — đầy 2/2
      clb_nua  — 2/4, đúng 50% nên KHÔNG mang nhãn "Còn nhiều chỗ"
      clb_it   — 1/4, dưới một nửa -> nhãn "Còn nhiều chỗ"
      clb_dt   — 2/2, có 1 em vào bằng dự trữ; 1 suất dự trữ -> dùng hết
    HS07 chỉ khai clb_day, điểm thấp nhất -> trắng tay.
    """
    api.create_or_update_club("clb_day", "CLB Đầy", 2, 0, "")
    api.create_or_update_club("clb_nua", "CLB Nửa", 4, 0, "")
    api.create_or_update_club("clb_it", "CLB Ít", 4, 0, "")
    api.create_or_update_club("clb_dt", "CLB Dự trữ", 2, 1, "chinh_sach")

    def them(sid, nhom, clbs, diem):
        api.create_student_if_missing(sid, "Em " + sid)
        if nhom:
            api.set_student_reserve_group(sid, nhom)
        api.submit_test_selection(sid, clbs)
        api.submit_preferences(sid, clbs)
        for c in clbs:
            api.submit_club_scores(c, [{"student_id": sid, "score": diem}])

    them("HS01", "", ["clb_day"], 9.0)
    them("HS02", "", ["clb_day"], 8.0)
    them("HS03", "", ["clb_nua"], 9.0)
    them("HS04", "", ["clb_nua"], 8.0)
    them("HS05", "", ["clb_dt"], 9.0)
    them("HS06", "chinh_sach", ["clb_dt"], 5.0)
    them("HS08", "", ["clb_it"], 7.0)
    them("HS07", "", ["clb_day"], 1.0)
    assert api.run_pipeline(seed=42)["ok"]
    return api


def _mo_trang(api):
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    # Ngữ cảnh tường minh: test "lựa chọn được nhớ" mở một trang THỨ HAI
    # dùng chung kho lưu trữ (xem test_giao_dien_thu_gon_ket_qua.py — tải
    # lại trang thì vé một lần của browser_host đã dùng mất).
    # bypass_csp: CSP chan eval cua wait_for_function; test CSP rieng o
    # test_giao_dien_sua_loi_p1.
    page = br.new_context(viewport={"width": 1400, "height": 1000},
                          bypass_csp=True).new_page()
    page.url_goc = url
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone")
    page.locator('[data-tab="results"]').click()
    page.wait_for_selector(".kpi-o")
    page.wait_for_function("document.querySelectorAll('.fill-row').length > 0")
    # Mọi mục ở thẻ Kết quả đóng sẵn: mở mục lấp đầy thì dòng mới hiện ra
    # để rê chuột và bấm Tab tới.
    page.click("#fillPanel .panel-toggle")
    page.wait_for_timeout(200)
    return pw, br, page, loi


@pytest.fixture
def trang(api_da_chay):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    pw, br, page, loi = _mo_trang(api_da_chay)
    yield page, loi, api_da_chay
    br.close()
    pw.stop()


def _o_kpi(page):
    return page.eval_on_selector_all(
        ".kpi-o",
        """os => Object.fromEntries(os.map(o => [o.dataset.muc, {
             so: o.querySelector('.kpi-so').textContent.trim(),
             phu: o.querySelector('.kpi-phu').textContent.trim(),
             lop: o.className,
           }]))""")


def _ten_cac_dong(page):
    return page.eval_on_selector_all(
        ".fill-row", "rs => rs.map(r => r.querySelector('.fill-name').textContent.trim())")


# ------------------------------------------------------------------ #
# 1. Ô TÓM TẮT = SỐ HÀM ĐỌC TRẢ VỀ
# ------------------------------------------------------------------ #

def test_o_tom_tat_khop_ham_doc(trang):
    page, loi, api = trang
    o = _o_kpi(page)

    cho = api.get_em_chua_co_cho()["data"]
    tong, trang_tay = cho["tong_hoc_sinh"], cho["so_em"]
    assert trang_tay == 1
    assert o["dsXepPanel"]["so"] == "%d/%d" % (tong - trang_tay, tong)

    lap = api.get_club_fill_stats()["data"]
    trong = sum(max(0, c["capacity"] - c["matched"]) for c in lap)
    assert o["fillPanel"]["so"] == str(trong)

    assert o["chuaCoChoPanel"]["so"] == "1"
    assert "is-nguy" in o["chuaCoChoPanel"]["lop"]
    # Trạng thái không bao giờ chỉ là màu: phải có ký hiệu kèm chữ.
    assert o["chuaCoChoPanel"]["phu"].startswith("⚠")

    du_tru = api.get_suat_du_tru()["data"]
    thua = sum(c["con_thua"] for c in du_tru)
    assert o["duTruPanel"]["so"] == "%d/%d" % (
        thua, sum(c["reserve_capacity"] for c in du_tru))
    assert "is-on" in o["duTruPanel"]["lop"] and thua == 0

    nv = api.get_phan_bo_nguyen_vong()["data"]
    assert nv["phan_bo"][0]["so_em"] == nv["tong_da_xep"]
    assert o["nvPanel"]["so"] == "100%"
    assert not loi, loi


def test_bam_o_tom_tat_mo_muc_chi_tiet(trang):
    """Mục "Em chưa có chỗ nào" đóng sẵn; bấm ô tóm tắt phải mở nó ra."""
    page, loi, _ = trang
    assert page.locator("#chuaCoChoPanelBody").is_hidden()
    page.click('.kpi-o[data-muc="chuaCoChoPanel"]')
    page.wait_for_selector("#chuaCoChoPanelBody", state="visible")
    assert page.locator("#chuaCoChoBody tr").count() == 1
    assert not loi, loi


def test_chua_chay_thi_khong_hien_tom_tat(api):
    """Chưa chạy lần nào mà hiện "0 em chưa có chỗ · Ổn" là nói sai theo
    hướng yên lòng nhất."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    api.create_or_update_club("clb_a", "CLB A", 2, 0, "")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="results"]').click()
        page.wait_for_selector(".fill-row", state="attached")
        page.wait_for_timeout(300)
        assert page.locator("#tomTatKetQua").is_hidden()
        br.close()


# ------------------------------------------------------------------ #
# 2. SẮP XẾP VÀ NHÃN CẦN ĐỂ Ý
# ------------------------------------------------------------------ #

def test_sap_xep_vang_nhat_dua_clb_it_len_dau_va_duoc_nho(trang):
    page, loi, _ = trang
    assert _ten_cac_dong(page)[0] != "CLB Ít"
    page.select_option("#fillSapXep", "vang_nhat")
    assert _ten_cac_dong(page)[:2] == ["CLB Ít", "CLB Nửa"]
    page.select_option("#fillSapXep", "day_nhat")
    assert _ten_cac_dong(page)[-1] == "CLB Ít"

    page.select_option("#fillSapXep", "vang_nhat")
    moi = page.context.new_page()
    moi.goto(page.url_goc)
    moi.locator('[data-tab="results"]').click()
    moi.wait_for_function("document.querySelectorAll('.fill-row').length > 0")
    assert moi.input_value("#fillSapXep") == "vang_nhat"
    assert _ten_cac_dong(moi)[0] == "CLB Ít"
    assert _ten_cac_dong(page)[0] == "CLB Ít"
    assert not loi, loi


def test_bam_o_cho_trong_chuyen_sang_vang_nhat(trang):
    page, _, _ = trang
    page.click('.kpi-o[data-muc="fillPanel"]')
    assert page.input_value("#fillSapXep") == "vang_nhat"
    assert _ten_cac_dong(page)[0] == "CLB Ít"


def test_nhan_can_de_y_chi_o_clb_duoi_mot_nua(trang):
    page, _, _ = trang
    nhan = page.eval_on_selector_all(
        ".fill-row",
        """rs => Object.fromEntries(rs.map(r => [
             r.querySelector('.fill-name').textContent.trim(),
             (r.querySelector('.fill-tag') || {}).textContent || '']))""")
    assert nhan["CLB Ít"].startswith("○")
    for ten in ("CLB Đầy", "CLB Nửa", "CLB Dự trữ"):
        assert nhan[ten] == "", (ten, nhan[ten])


def test_mot_buoi_thi_khong_co_tieu_de_nhom(trang):
    page, _, _ = trang
    assert page.locator(".fill-nhom").count() == 0


# ------------------------------------------------------------------ #
# 3. CHÚ THÍCH NỔI
# ------------------------------------------------------------------ #

def _doc_tooltip(page):
    return page.evaluate("""() => {
      const h = document.getElementById('bieuDoTooltip');
      return {
        an: h.hidden,
        dau: (h.querySelector('.bd-tooltip-dau') || {}).textContent || '',
        dong: Object.fromEntries([...h.querySelectorAll('.bd-tooltip-dong')]
          .map(d => [d.querySelector('span').textContent.trim(),
                     d.querySelector('b').textContent.trim()])),
      };
    }""")


def test_re_chuot_hien_dung_so_cua_clb(trang):
    page, loi, _ = trang
    assert _doc_tooltip(page)["an"]
    page.locator('.fill-row[data-clb="clb_dt"]').hover()
    tt = _doc_tooltip(page)
    assert not tt["an"]
    assert tt["dau"] == "CLB Dự trữ"
    assert tt["dong"]["Đã xếp"] == "2/2 · 100%"
    assert tt["dong"]["· Suất thường"] == "1"
    assert tt["dong"]["· Vào bằng suất dự trữ"] == "1/1"
    assert tt["dong"]["Còn trống"] == "0"

    page.mouse.move(5, 5)
    assert _doc_tooltip(page)["an"]
    assert not loi, loi


def test_ban_phim_toi_dong_cung_hien_chu_thich(trang):
    page, _, _ = trang
    page.focus('.fill-row[data-clb="clb_it"]')
    tt = _doc_tooltip(page)
    assert not tt["an"] and tt["dau"] == "CLB Ít"
    assert tt["dong"]["Còn trống"] == "3"


def test_doan_du_tru_va_doan_chung_van_cong_dung_ti_le(trang):
    """Khe 2px giữa hai đoạn là bóng đổ, không được ăn vào bề rộng."""
    page, _, _ = trang
    r = page.evaluate("""() => {
      const row = document.querySelector('.fill-row[data-clb="clb_dt"]');
      const track = row.querySelector('.fill-track');
      return { mang: track.clientWidth,
               tong: [...row.querySelectorAll('.fill-bar')]
                        .reduce((s, b) => s + b.getBoundingClientRect().width, 0) };
    }""")
    assert r["tong"] == pytest.approx(r["mang"], abs=1)


def test_doi_ngon_ngu_thi_tom_tat_va_chu_thich_doi_theo(trang):
    page, loi, _ = trang
    page.click("#btnLangToggle")
    page.wait_for_function(
        "document.querySelector('#tomTatTieuDe').textContent === 'Run summary'")
    page.wait_for_function(
        "[...document.querySelectorAll('.kpi-nhan')].some(n => n.textContent === 'Students placed')")
    page.locator('.fill-row[data-clb="clb_dt"]').hover()
    assert "Placed" in _doc_tooltip(page)["dong"]
    assert not loi, loi


# ------------------------------------------------------------------ #
# 4. NHIỀU BUỔI: NHÓM THEO BUỔI
# ------------------------------------------------------------------ #

def test_nhieu_buoi_thi_nhom_theo_buoi_co_tong_tung_buoi(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_NHIEU_BUOI, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]
    assert api.run_pipeline(seed=42)["ok"]

    pw, br, page, loi = _mo_trang(api)
    try:
        lap = api.get_club_fill_stats()["data"]
        ds_buoi = sorted({c["buoi"] for c in lap})
        assert page.locator(".fill-nhom").count() == len(ds_buoi)

        tong = page.eval_on_selector_all(
            ".fill-nhom-so", "ns => ns.map(n => n.textContent.trim())")
        for b, chu in zip(ds_buoi, tong):
            xep = sum(c["matched"] for c in lap if c["buoi"] == b)
            cho = sum(c["capacity"] for c in lap if c["buoi"] == b)
            assert chu.startswith("%d/%d" % (xep, cho)), (b, chu)

        # Sắp theo cách khác thì bỏ nhóm, và mỗi dòng mang chip buổi.
        page.select_option("#fillSapXep", "choi_cao")
        assert page.locator(".fill-nhom").count() == 0
        assert page.locator(".fill-chip-buoi").count() == len(lap)
        choi = [c["ti_le_choi"] for c in lap]
        assert page.eval_on_selector(
            ".fill-row", "r => r.dataset.clb") == max(
                lap, key=lambda c: c["ti_le_choi"] or -1)["club_id"]
        assert max(choi) > 0
        assert not loi, loi
    finally:
        br.close()
        pw.stop()


# ------------------------------------------------------------------ #
# 5. MỨC ĐÁP ỨNG NGUYỆN VỌNG: TÊN MỚI + VÀNH KHUYÊN
# ------------------------------------------------------------------ #

def _doc_donut(page):
    """Độ dài cung ĐỌC TỪ THUỘC TÍNH stroke-dasharray, không suy ra từ CSS."""
    return page.evaluate("""() => {
      const cs = [...document.querySelectorAll('#nvDonut .nv-cung')];
      const r = +document.querySelector('#nvDonut .nv-cung, #nvDonut circle').getAttribute('r');
      return {
        chu_vi: 2 * Math.PI * r,
        cung: cs.map(c => ({
          dai: parseFloat(c.getAttribute('stroke-dasharray').split(' ')[0]),
          so_em: +c.dataset.soEm,
          lop: c.getAttribute('class'),
        })),
        giua: document.querySelector('#nvDonut .nv-donut-so').textContent.trim(),
        chu_giai: [...document.querySelectorAll('#nvDonutChuGiai li')]
          .map(li => li.textContent.trim()),
      };
    }""")


def test_ten_muc_moi_ca_hai_ngon_ngu(trang):
    page, loi, _ = trang
    assert page.inner_text("#nvPanel h2").strip() == "Mức đáp ứng nguyện vọng"
    page.click("#btnLangToggle")
    page.wait_for_function(
        "document.querySelector('#nvPanel h2').textContent === 'How well choices were met'")
    assert not loi, loi


def test_mot_thu_hang_thi_mot_cung_phu_kin_vong(trang):
    """Bộ nhỏ: mọi chỗ đều là NV1 -> đúng một cung, không khe, kín vòng,
    và số giữa vành khớp ô tóm tắt."""
    page, _, _ = trang
    d = _doc_donut(page)
    assert len(d["cung"]) == 1
    assert "is-h1" in d["cung"][0]["lop"]
    assert d["cung"][0]["dai"] == pytest.approx(d["chu_vi"], abs=0.01)
    assert d["giua"] == "100%"
    o = _o_kpi(page)
    assert d["giua"] == o["nvPanel"]["so"]
    # Chú giải liệt kê MỌI thứ hạng, kể cả thứ hạng 0 chỗ không có cung.
    assert len(d["chu_giai"]) == 4


def test_nhieu_thu_hang_thi_cung_dung_ti_le_va_cong_du_vong(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    for ten in ("NHIEUBUOI_01_danh_sach_CLB.csv",
                "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"):
        with io.open(os.path.join(BO_NHIEU_BUOI, ten), encoding="utf-8-sig") as f:
            assert api.import_csv_auto(f.read())["ok"]
    assert api.run_pipeline(seed=42)["ok"]

    pw, br, page, loi = _mo_trang(api)
    try:
        nv = api.get_phan_bo_nguyen_vong()["data"]
        tong = nv["tong_da_xep"]
        co_so = [h for h in nv["phan_bo"] if h["so_em"] > 0]
        assert len(co_so) >= 2, "bo mau phai co it nhat hai thu hang"

        d = _doc_donut(page)
        assert [c["so_em"] for c in d["cung"]] == [h["so_em"] for h in co_so]
        KHE = 2
        assert sum(c["dai"] for c in d["cung"]) + KHE * len(d["cung"]) == \
            pytest.approx(d["chu_vi"], abs=0.01)
        for c in d["cung"]:
            assert (c["dai"] + KHE) / d["chu_vi"] == \
                pytest.approx(c["so_em"] / tong, abs=0.005)

        nv1 = nv["phan_bo"][0]["so_em"]
        assert d["giua"] == ("%.1f" % (nv1 * 100.0 / tong)).rstrip("0").rstrip(".") \
            .replace(".", ",") + "%"

        # Rê chuột vào một cung -> chú thích đúng số của cung đó.
        page.click("#nvPanel .panel-toggle")
        page.wait_for_selector("#nvPanelBody", state="visible")
        # Rê vào ĐIỂM GIỮA CỦA CUNG trên nét vòng. `locator.hover()` nhắm
        # tâm khung bao — với vành khuyên đó là lỗ giữa, nơi không có cung.
        diem = page.evaluate("""() => {
          const cs = [...document.querySelectorAll('#nvDonut .nv-cung')];
          const i = cs.findIndex(c => c.classList.contains('is-h2'));
          const C = 2 * Math.PI * 70;
          let bd = 0;
          for (let k = 0; k < i; k++) bd += +cs[k].dataset.soEm;
          const tong = cs.reduce((s, c) => s + +c.dataset.soEm, 0);
          const goc = ((bd + +cs[i].dataset.soEm / 2) / tong) * 2 * Math.PI;
          const svg = document.querySelector('#nvDonut svg').getBoundingClientRect();
          const k = svg.width / 180;
          return { x: svg.left + (90 + 70 * Math.sin(goc)) * k,
                   y: svg.top + (90 - 70 * Math.cos(goc)) * k };
        }""")
        page.mouse.move(diem["x"], diem["y"])
        page.wait_for_timeout(100)
        tt = _doc_tooltip(page)
        assert not tt["an"]
        assert tt["dau"] == "Nguyện vọng 2"
        assert tt["dong"]["Số chỗ"] == str(nv["phan_bo"][1]["so_em"])
        assert page.evaluate(
            "document.querySelector('#nvDonut svg').classList.contains('is-dang-chi')")
        assert not loi, loi
    finally:
        br.close()
        pw.stop()
