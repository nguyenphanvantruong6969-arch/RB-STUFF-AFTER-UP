"""Canh CỔNG KHỞI ĐỘNG bằng TRÌNH DUYỆT THẬT, mô phỏng đúng cách pywebview
dựng cầu nối.

VÌ SAO PHẢI CÓ FILE NÀY RIÊNG
Mọi test giao diện khác đi qua `browser_host.serve(...)`, mà `browser_host`
chèn cầu nối giả lập TRƯỚC `</head>` — `window.pywebview` có sẵn, đồng bộ,
`api` là Proxy luôn trả về hàm. Nghĩa là mọi test đều rơi vào nhánh
"sẵn sàng ngay lập tức". **Không test nào từng chạy qua con đường mà người
dùng Windows thật đi**, nên cả bộ 381 test mù hoàn toàn với lỗi dưới đây.

pywebview KHÔNG dựng `window.pywebview` trong một nhịp. Đọc mã nguồn
pywebview 6.2.1 (đang nằm trong .venv):

  webview/js/api.js      ->  window.pywebview = { …, api: {} }      (nhịp 1)
  webview/js/finish.js   ->  _createApi(…); dispatch pywebviewready (nhịp 2)

  webview/util.py:225    ->  def generate_js_object():
                                 window.run_js(js_code)        # nhịp 1
                                 func_list = generate_func()   # phản chiếu Python
                                 window.run_js(finish_script)  # nhịp 2

HAI lệnh run_js tách rời, trên một luồng riêng, có phản chiếu Python xen
giữa. Trong khe hở đó `window.pywebview` ĐÃ CÓ THẬT nhưng `api` còn RỖNG —
gọi hàm nào cũng trượt. Trên Windows việc này còn chạy sau khi trang đã tải
xong (webview/platforms/edgechromium.py:389, trong on_navigation_completed).

Cổng khởi động cũ chỉ hỏi `if (window.pywebview)` và hẹn giờ MỘT phát 300 ms,
nên có ba khả năng — hai trong ba là hỏng:

  A. 300ms < T1        -> đúng (chỉ xảy ra khi máy chậm)
  B. T1 < 300ms < T3   -> init() với api RỖNG -> "Backend not ready yet"
  C. T3 < 300ms        -> init() chạy HAI LẦN (cờ appInit chỉ đặt ở nhánh
                          hẹn giờ, nên đường sự kiện không đánh dấu gì)

Ca B là lỗi người dùng báo khi mới cài. Ca C làm mọi nút bị gắn hai lần —
trong đó nút đổi ngôn ngữ gọi setLang hai lượt (vi→en→vi) nên TRÔNG NHƯ CHẾT.

Máy nào không có playwright/Chromium thì bỏ qua cả file.
"""

import functools
import http.server
import os
import threading

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

# Hạn chờ mà js/*.js dùng trong test. Bản chạy thật là 20 giây; để nguyên thì
# riêng ca "backend không bao giờ tới" phải ngồi đợi 20 giây.
HAN_TEST_MS = 1500


# --------------------------------------------------------------------------
# Máy chủ tĩnh — CỐ TÌNH không dùng browser_host, vì browser_host dựng sẵn
# cầu nối và như thế là xoá mất chính cuộc đua ta cần đo.
# --------------------------------------------------------------------------

class _ImLang(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def goc_url():
    handler = functools.partial(_ImLang, directory=GOC)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d/" % srv.server_address[1]
    srv.shutdown()


# --------------------------------------------------------------------------
# Mô phỏng hai nhịp của pywebview, có kiểm soát thời điểm.
#
# Chạy bằng add_init_script nên nó thực thi TRƯỚC js/*.js — mốc thời gian vì
# thế tin cậy được (hai đồng hồ bắt đầu cách nhau vài mili giây).
#
#   t = -1  -> nhịp đó KHÔNG BAO GIỜ chạy
#   t =  0  -> chạy NGAY, đồng bộ (giống cầu nối của browser_host)
#   t >  0  -> chạy sau t mili giây
# --------------------------------------------------------------------------

_KICH_BAN = """
(function () {
  "use strict";
  window.__demGoi = {};
  window.__HAN_BACKEND_MS = %(han)d;

  /* Nhịp 1 — Y HỆT webview/js/api.js: đối tượng có thật, api RỖNG. */
  function nhip1() {
    window.pywebview = { token: "test", platform: "edgechromium", api: {} };
  }

  /* Nhịp 2 — y hệt webview/js/finish.js: đổ hàm vào rồi mới bắn sự kiện. */
  function nhip2() {
    if (!window.pywebview) nhip1();
    window.pywebview.api = new Proxy({}, {
      has: function () { return true; },
      get: function (_t, ten) {
        if (typeof ten !== "string") return undefined;
        return function () {
          window.__demGoi[ten] = (window.__demGoi[ten] || 0) + 1;
          return Promise.resolve({ ok: true, data: {}, errors: [] });
        };
      },
    });
    window.dispatchEvent(new CustomEvent("pywebviewready"));
  }

  var T1 = %(t1)d, T2 = %(t2)d;
  if (T1 === 0) nhip1(); else if (T1 > 0) setTimeout(nhip1, T1);
  if (T2 === 0) nhip2(); else if (T2 > 0) setTimeout(nhip2, T2);
})();
"""


class _Trang:
    """Trang đã mở + danh sách lỗi JS, để test nào cũng soát được lỗi trang."""

    def __init__(self, page, loi):
        self.page = page
        self.loi = loi

    def chu(self):
        return self.page.inner_text("body")

    def dem(self, ten_ham):
        return self.page.evaluate(
            "(t) => (window.__demGoi[t] || 0)", ten_ham)


@pytest.fixture
def mo(goc_url):
    """mo(t1, t2, cho_ms) -> _Trang. Đóng trình duyệt khi test xong."""
    dong = []

    def _mo(t1, t2, cho_ms=1200, trang_html="index.html"):
        if CHROMIUM is None:
            pytest.skip("khong tim thay Chromium")
        pw = sync_playwright().start()
        dong.append(pw.stop)
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append(br.close)
        page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.add_init_script(
            _KICH_BAN % {"t1": t1, "t2": t2, "han": HAN_TEST_MS})
        page.goto(goc_url + trang_html)
        # Chờ QUA mốc 300 ms của cổng cũ — nếu chờ ngắn hơn thì bản chưa vá
        # sẽ xanh vì chưa kịp hỏng, tức test đúng vì lý do sai.
        page.wait_for_timeout(cho_ms)
        return _Trang(page, loi)

    yield _mo
    for f in reversed(dong):
        f()


# --------------------------------------------------------------------------
# 1. CA B — khe hở giữa hai nhịp trùm lên mốc 300 ms.
#    Đây đúng là ca người dùng gặp khi mới cài: máy lạnh, khe hở rộng.
# --------------------------------------------------------------------------

def test_khe_ho_giua_hai_nhip_khong_duoc_lam_hien_loi_tieng_anh(mo):
    trang = mo(t1=100, t2=600, cho_ms=1600)
    chu = trang.chu()
    assert "Backend not ready" not in chu, (
        "Cổng khởi động chạy init() trong lúc window.pywebview.api còn RỖNG. "
        "Người dùng thấy câu lỗi tiếng Anh của lập trình viên trong phần mềm "
        "tiếng Việt.\n--- nội dung trang ---\n" + chu)


def test_khe_ho_giua_hai_nhip_van_khoi_dong_duoc_khi_backend_toi(mo):
    """Vá xong không được sinh ra bệnh mới: chờ lâu là được, chờ mãi không
    khởi động thì lại là một lỗi khác."""
    trang = mo(t1=100, t2=600, cho_ms=1600)
    assert trang.dem("get_last_run_info") == 1
    assert trang.dem("get_data_health_report") == 1


# --------------------------------------------------------------------------
# 2 & 3. CA C — hai nhịp xong sớm hơn mốc 300 ms (mọi máy nhanh).
#        Cờ appInit chỉ được đặt trong nhánh hẹn giờ, nên đường sự kiện
#        khởi động mà không đánh dấu gì, và hẹn giờ khởi động lần hai.
# --------------------------------------------------------------------------

def test_backend_toi_som_thi_init_chi_chay_dung_mot_lan(mo):
    trang = mo(t1=20, t2=60)
    n = trang.dem("get_last_run_info")
    assert n == 1, (
        "init() chạy %d lần. Cả 40 chỗ gắn sự kiện trong js/*.js đều dùng "
        "addEventListener (không chỗ nào dùng .onclick), nên khởi động hai "
        "lần là gắn đôi TOÀN BỘ nút." % n)


def test_nut_doi_ngon_ngu_bam_mot_cai_thi_doi_mot_lan(mo):
    """Triệu chứng người dùng báo: 'switching between English and Vietnamese
    is glitchy'. Gắn đôi thì một cú bấm gọi setLang hai lượt — vi→en→vi —
    nên nút TRÔNG NHƯ CHẾT."""
    trang = mo(t1=20, t2=60)
    assert trang.page.evaluate("() => window.I18N.getLang()") == "vi"
    trang.page.click("#btnLangToggle")
    assert trang.page.evaluate("() => window.I18N.getLang()") == "en", (
        "Bấm một cái mà ngôn ngữ không đổi — nút bị gắn hai trình xử lý.")


def test_nut_hai_buoc_chi_gan_mot_trinh_xu_ly(mo):
    """armTwoStepConfirm gắn hai lần thì sinh hai bao đóng, mỗi cái một biến
    `armed` riêng. Bấm lần hai là onConfirmed() chạy HAI LƯỢT — với nút
    'Xoá toàn bộ dữ liệu' thì reset_data chạy hai lần, và bản sao lưu thứ
    hai chụp CSDL ĐÃ RỖNG, ăn mất một suất trong _MAX_BACKUPS = 10."""
    trang = mo(t1=20, t2=60)
    trang.page.click('.nav-item[data-tab="admin"]')
    trang.page.click("#btnResetAll")   # lần 1: chỉ lên nòng
    trang.page.click("#btnResetAll")   # lần 2: mới thật sự xoá
    trang.page.wait_for_timeout(200)
    n = trang.dem("reset_data")
    assert n == 1, "reset_data chạy %d lần cho một chuỗi bấm hai bước." % n


# --------------------------------------------------------------------------
# 4. Backend KHÔNG BAO GIỜ tới — phải nói bằng tiếng Việt, không được để
#    trang câm hoặc phun chuỗi tiếng Anh.
# --------------------------------------------------------------------------

def test_backend_khong_toi_thi_bao_bang_tieng_viet(mo):
    trang = mo(t1=-1, t2=-1, cho_ms=HAN_TEST_MS + 800)
    chu = trang.chu()
    assert "Backend not ready" not in chu
    assert "loi_khoi_dong.txt" in chu, (
        "Quá hạn mà không chỉ cho người dùng tệp nhật ký nào để gửi đi thì "
        "lần sau vẫn phải ĐOÁN nguyên nhân.\n--- nội dung trang ---\n" + chu)


def test_dang_cho_thi_noi_la_dang_cho(mo):
    """Giữa lúc chờ, trang không được câm — người dùng phải biết nó đang
    làm gì chứ không phải đang treo."""
    trang = mo(t1=-1, t2=-1, cho_ms=800)   # sau mốc 400 ms, trước hạn
    assert "Backend not ready" not in trang.chu()
    assert trang.page.inner_text("#healthSummary").strip() != ""


# --------------------------------------------------------------------------
# 5. Chống hồi quy đường CHẾ ĐỘ TRÌNH DUYỆT: browser_host dựng cầu nối
#    đồng bộ trước </head>, tức cả hai nhịp xong trước khi js/*.js chạy.
# --------------------------------------------------------------------------

def test_cau_noi_co_san_tu_dau_van_khoi_dong_dung_mot_lan(mo):
    trang = mo(t1=0, t2=0)
    assert trang.dem("get_last_run_info") == 1
    assert "Backend not ready" not in trang.chu()


def test_khong_co_loi_javascript_nao_o_moi_kich_ban(mo):
    trang = mo(t1=100, t2=600, cho_ms=1600)
    assert trang.loi == []


# --------------------------------------------------------------------------
# 6. MÀN HÌNH PHỤC HỒI — recovery.js là BẢN SAO NGUYÊN VĂN của cùng cổng
#    khởi động. Đây là màn hình hiện ra KHI CSDL ĐÃ HỎNG (main.py bắt lỗi
#    PipelineAPI rồi mở recovery.html), nên hỏng nốt ở đây là hết đường.
# --------------------------------------------------------------------------

def test_phuc_hoi_khe_ho_giua_hai_nhip_khong_hien_loi_tieng_anh(mo):
    trang = mo(t1=100, t2=600, cho_ms=1600, trang_html="recovery.html")
    assert "Backend not ready" not in trang.chu()
    assert trang.dem("get_status") == 1


def test_phuc_hoi_nut_bat_dau_lai_chi_chay_mot_lan(mo):
    """Gắn đôi thì `start_fresh` — nút XOÁ SẠCH để bắt đầu với CSDL trống —
    chạy hai lượt cho một chuỗi bấm hai bước."""
    trang = mo(t1=20, t2=60, trang_html="recovery.html")
    trang.page.click("#btnStartFresh")   # lần 1: chỉ lên nòng
    trang.page.click("#btnStartFresh")   # lần 2: mới thật sự chạy
    trang.page.wait_for_timeout(200)
    n = trang.dem("start_fresh")
    assert n == 1, "start_fresh chạy %d lần cho một chuỗi bấm hai bước." % n
