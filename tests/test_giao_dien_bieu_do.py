"""Biểu đồ "Tỉ lệ lấp đầy theo club" — đo bằng TRÌNH DUYỆT THẬT.

Biểu đồ này chưa bao giờ vẽ được thanh chính. `.fill-bar` là một `<span>`
mà CSS không đặt `display`, nên nó ở trạng thái inline — và `width` /
`height` **không áp dụng cho phần tử inline**. CLB đầy 14/14 vẫn hiện ra
một máng trắng trơn. Riêng thanh dự trữ vẽ được, chỉ vì JS gắn
`position:absolute` nội tuyến, mà absolute thì bị ép thành block.

Không test nào của dự án bắt được: `test_api.py` và
`test_kich_ban_nhap_tay.py` chỉ gọi API Python, mà API trả về đúng số.
Sai nằm ở tầng CSS, nơi tầng Python mù hoàn toàn.

Nên mọi phép đo ở đây dùng **bề rộng vẽ ra thật**
(`getBoundingClientRect`), tuyệt đối không dùng thuộc tính CSS. Chính
`width:100%` mà vẽ ra 0 px là cái bẫy đã giấu lỗi này từ đầu.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def api_da_chay(api):
    """Ba CLB, mỗi CLB minh hoạ một ca khác nhau của biểu đồ.

      clb_day  — đầy 100%, KHÔNG có suất dự trữ  -> chỉ một đoạn xanh
      clb_nua  — lấp đúng 50%                    -> nửa máng
      clb_dt   — đầy, có 1 em vào bằng dự trữ    -> hai đoạn
    """
    api.create_or_update_club("clb_day", "CLB Đầy", 2, 0, "")
    api.create_or_update_club("clb_nua", "CLB Nửa", 4, 0, "")
    api.create_or_update_club("clb_dt", "CLB Dự trữ", 2, 1, "chinh_sach")

    def them(sid, nhom, clb, diem):
        api.create_student_if_missing(sid, "Em " + sid)
        if nhom:
            api.set_student_reserve_group(sid, nhom)
        api.submit_test_selection(sid, [clb])
        api.submit_preferences(sid, [clb])
        api.submit_club_scores(clb, [{"student_id": sid, "score": diem}])

    them("HS01", "", "clb_day", 9.0)
    them("HS02", "", "clb_day", 8.0)
    them("HS03", "", "clb_nua", 9.0)
    them("HS04", "", "clb_nua", 8.0)
    them("HS05", "", "clb_dt", 9.0)
    them("HS06", "chinh_sach", "clb_dt", 5.0)   # điểm thấp nhất, vào bằng dự trữ
    assert api.run_pipeline(seed=42)["ok"]
    return api


@pytest.fixture
def bieu_do(api_da_chay):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    url = browser_host.serve(api_da_chay, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="results"]').click()
        page.wait_for_function("document.querySelectorAll('.fill-row').length === 3")
        # Mọi mục ở thẻ Kết quả đóng sẵn — mở mục lấp đầy thì mới đo được
        # bề rộng thanh (mục đóng thì mọi thứ bên trong rộng 0 px).
        page.click("#fillPanel .panel-toggle")
        page.wait_for_timeout(300)
        yield _doc_cac_dong(page), loi
        br.close()


def _doc_cac_dong(page):
    """Trả về {tên CLB: {...}} với bề rộng ĐO ĐƯỢC, không phải CSS."""
    rows = page.evaluate("""() => {
      const ra = {};
      for (const r of document.querySelectorAll('.fill-row')) {
        const track = r.querySelector('.fill-track');
        ra[r.querySelector('.fill-name').textContent.trim()] = {
          so: r.querySelector('.fill-count').textContent.trim(),
          // clientWidth = HOP NOI DUNG. Cac doan an theo % cua hop noi
          // dung, con getBoundingClientRect() tra hop VIEN — lech dung
          // 2px vi mang co vien 1px moi ben. Doi chieu voi hop vien la
          // do sai moc.
          rong_mang: track.clientWidth,
          doan: [...r.querySelectorAll('.fill-bar')].map(b => ({
            du_tru: b.classList.contains('is-reserve'),
            display: getComputedStyle(b).display,
            rong: b.getBoundingClientRect().width,
          })),
        };
      }
      return ra;
    }""")
    return rows


def test_clb_day_thi_thanh_phu_kin_mang(bieu_do):
    """Ca hỏng rõ nhất: 2/2 mà máng trắng trơn."""
    dong, loi = bieu_do
    c = dong["CLB Đầy"]
    assert c["so"] == "2/2"
    tong = sum(d["rong"] for d in c["doan"])
    assert tong == pytest.approx(c["rong_mang"], abs=2), \
        "CLB day 100%% ma thanh chi ve ra %.0f/%.0f px" % (tong, c["rong_mang"])
    assert not loi, loi


def test_clb_lap_mot_nua_thi_thanh_dai_mot_nua(bieu_do):
    dong, _ = bieu_do
    c = dong["CLB Nửa"]
    assert c["so"] == "2/4"
    tong = sum(d["rong"] for d in c["doan"])
    assert tong == pytest.approx(c["rong_mang"] / 2, abs=3)


def test_khong_doan_nao_con_o_trang_thai_inline(bieu_do):
    """Nguyên nhân gốc. Inline thì width bị bỏ qua, thanh vẽ ra 0 px."""
    dong, _ = bieu_do
    for ten, c in dong.items():
        for d in c["doan"]:
            assert d["display"] != "inline", "%s: doan van con inline" % ten
            assert d["rong"] > 0, "%s: doan ve ra 0 px" % ten


def test_clb_co_du_tru_hien_hai_doan_cong_lai_dung_ti_le(bieu_do):
    """Đoạn vàng phải là số em VÀO BẰNG suất dự trữ, không phải chỉ tiêu
    dự trữ của CLB. Ở đây: 2/2 em, trong đó 1 em vào bằng dự trữ."""
    dong, _ = bieu_do
    c = dong["CLB Dự trữ"]
    assert c["so"] == "2/2"
    assert len(c["doan"]) == 2, "phai co dung hai doan, dang co %d" % len(c["doan"])

    vang = [d for d in c["doan"] if d["du_tru"]]
    xanh = [d for d in c["doan"] if not d["du_tru"]]
    assert len(vang) == 1 and len(xanh) == 1
    assert vang[0]["rong"] == pytest.approx(c["rong_mang"] / 2, abs=3)
    assert sum(d["rong"] for d in c["doan"]) == pytest.approx(c["rong_mang"], abs=2)


def test_clb_khong_co_du_tru_chi_hien_mot_doan(bieu_do):
    """Không được vẽ đoạn vàng rộng 0 px cho CLB không có ai diện dự trữ."""
    dong, _ = bieu_do
    for ten in ("CLB Đầy", "CLB Nửa"):
        doan = dong[ten]["doan"]
        assert len(doan) == 1, "%s: phai chi co mot doan, dang co %d" % (ten, len(doan))
        assert not doan[0]["du_tru"]
