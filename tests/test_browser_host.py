"""Tests for browser_host — chế độ chạy dự phòng bằng trình duyệt, dùng
khi pywebview/pythonnet không khởi động được trên máy người dùng.

Điều quan trọng nhất phải bảo đảm: cầu nối HTTP này gọi ĐÚNG vào
PipelineAPI thật (không phải bản giả), và KHÔNG mở toang thứ gì ra ngoài
— chỉ nghe trên 127.0.0.1, bắt buộc có token, và không cho gọi phương
thức nội bộ (bắt đầu bằng dấu gạch dưới).
"""

import json
import os
import time
import urllib.error
import urllib.request

import pytest

import browser_host

RESOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def hosted(api):
    """Khởi động browser_host trước một PipelineAPI thật (không mở trình
    duyệt), trả về (url_goc, token)."""
    url = browser_host.serve(api, RESOURCE_DIR, "index.html", open_browser=False)
    base, token = url.split("/index.html?t=")
    return base, token


def _post(base, token, method, args=None, extra_headers=None):
    req = urllib.request.Request(
        f"{base}/__api__/{method}",
        data=json.dumps({"args": args or []}).encode(),
        headers={"Content-Type": "application/json",
                 **({"X-Kiosk-Token": token} if token else {}),
                 **(extra_headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def test_api_call_reaches_the_real_pipeline_api(hosted, api):
    base, token = hosted
    api.create_or_update_club("A", "Club A", 5, 0, "")
    api.create_student_if_missing("s1", "Student 1")
    api.submit_preferences("s1", ["A"])

    res = _post(base, token, "get_dashboard_status")
    assert res["ok"] is True
    # đúng dữ liệu vừa tạo qua đối tượng Python, đọc lại qua HTTP
    assert res["data"]["n_students"] == 1
    assert res["data"]["n_clubs"] == 1


def test_api_call_passes_arguments_through(hosted, api):
    base, token = hosted
    res = _post(base, token, "create_student_if_missing", ["s9", "Nguyen Van A"])
    assert res["ok"] is True
    # thật sự đã ghi vào DB, không phải trả lời cho có
    assert api.get_dashboard_status()["data"]["n_students"] == 1


def test_request_without_token_is_rejected(hosted):
    base, _ = hosted
    with pytest.raises(urllib.error.HTTPError) as exc:
        _post(base, None, "get_dashboard_status")
    assert exc.value.code == 403


def test_request_with_wrong_token_is_rejected(hosted):
    base, _ = hosted
    with pytest.raises(urllib.error.HTTPError) as exc:
        _post(base, "sai-token-hoan-toan", "get_dashboard_status")
    assert exc.value.code == 403


def test_private_methods_are_not_exposed(hosted):
    """_backup_db, _move_corrupt_db_aside... phải nằm ngoài tầm với của HTTP."""
    base, token = hosted
    with pytest.raises(urllib.error.HTTPError) as exc:
        _post(base, token, "_backup_db")
    assert exc.value.code == 404


def test_unknown_method_returns_404_not_a_crash(hosted):
    base, token = hosted
    with pytest.raises(urllib.error.HTTPError) as exc:
        _post(base, token, "khong_ton_tai")
    assert exc.value.code == 404


def test_exception_in_api_becomes_a_normal_error_response(hosted):
    """Lỗi trong backend phải trả về {ok: false} để UI hiện được, chứ
    không làm sập cả máy chủ."""
    base, token = hosted
    # submit_preferences thiếu tham số -> TypeError bên trong
    res = _post(base, token, "submit_preferences", [])
    assert res["ok"] is False
    assert res["errors"]


def test_html_is_served_with_the_pywebview_shim_injected(hosted):
    """Đây là mấu chốt khiến js/*.js/recovery.js chạy y nguyên, không sửa gì."""
    base, token = hosted
    with urllib.request.urlopen(f"{base}/index.html?t={token}") as r:
        html = r.read().decode("utf-8")
    assert "window.pywebview" in html
    assert "/__api__/" in html
    # chèn TRƯỚC </head> để window.pywebview tồn tại trước khi js/*.js chạy
    assert html.index("window.pywebview") < html.index("</head>")
    # và nội dung gốc vẫn còn nguyên
    assert 'src="js/00_nen.js"' in html


def test_recovery_page_also_gets_the_shim(hosted):
    base, token = hosted
    with urllib.request.urlopen(f"{base}/recovery.html?t={token}") as r:
        html = r.read().decode("utf-8")
    assert "window.pywebview" in html
    assert 'src="recovery.js"' in html


def test_static_assets_are_served_unmodified(hosted):
    base, _ = hosted
    with urllib.request.urlopen(f"{base}/js/00_nen.js") as r:
        js_byte = r.read()
    # Tệp .js phải được phục vụ NGUYÊN VĂN — chỉ .html mới bị chèn shim
    assert "callApi" in js_byte.decode("utf-8")
    # So NGUYÊN BYTE, không so chuỗi đã giải mã. Mở tệp ở chế độ văn bản
    # thì Python tự đổi CRLF thành LF, mà trên Windows git lấy về đúng
    # CRLF — so chuỗi sẽ báo lệch ở MỌI dòng dù máy chủ phục vụ đúng từng
    # byte. So byte vừa hết lệ thuộc hệ điều hành, vừa chặt hơn: nó bắt
    # được cả những sửa đổi mà phép giải mã làm mờ đi.
    with open(os.path.join(RESOURCE_DIR, "js", "00_nen.js"), "rb") as f:
        assert js_byte == f.read()
    # style.css cũng phải phục vụ được, nếu không giao diện sẽ trắng trơn
    with urllib.request.urlopen(f"{base}/style.css") as r:
        assert "--ink" in r.read().decode("utf-8")


def test_server_binds_only_to_loopback(hosted):
    """Không được lắng nghe ra ngoài mạng — đây là máy kiosk chứa dữ liệu
    học sinh."""
    base, _ = hosted
    assert base.startswith("http://127.0.0.1:")


# ------------------------------------------------------------------ #
# Chế độ CỬA SỔ RIÊNG (app mode)
#
# Yêu cầu: app phải mở như một ứng dụng riêng — cửa sổ riêng, KHÔNG
# thanh địa chỉ, KHÔNG tab — chứ không phải một tab lẫn trong trình
# duyệt người dùng đang mở. Đây là phần mềm kiosk đặt ở trường: học
# sinh không được nhìn thấy thanh địa chỉ để gõ sang trang khác.
# ------------------------------------------------------------------ #


def test_app_window_command_asks_for_a_separate_window():
    cmd = browser_host.build_app_window_command(
        "/usr/bin/chromium",
        "http://127.0.0.1:9/index.html?t=abc",
        "/tmp/ho-so",
        1280, 800,
    )
    assert cmd[0] == "/usr/bin/chromium"
    # --app= là cờ DUY NHẤT tạo cửa sổ không thanh địa chỉ, không tab.
    assert "--app=http://127.0.0.1:9/index.html?t=abc" in cmd
    # hồ sơ riêng: không dính extension/lịch sử/tab cũ của người dùng
    assert "--user-data-dir=/tmp/ho-so" in cmd
    assert "--window-size=1280,800" in cmd
    # tuyệt đối không được mở thành tab
    assert not any(c.startswith("--new-tab") for c in cmd)


def test_browser_lookup_prefers_env_override(monkeypatch, tmp_path):
    """Cho phép người vận hành chỉ định trình duyệt cụ thể khi máy
    trường cài ở đường dẫn lạ."""
    fake = tmp_path / "trinh-duyet"
    fake.write_text("")
    fake.chmod(0o755)
    monkeypatch.setenv("RBDA_BROWSER", str(fake))
    assert browser_host.find_app_window_browser() == str(fake)


def test_browser_lookup_ignores_env_override_that_does_not_exist(monkeypatch):
    """Đường dẫn rác phải bị bỏ qua, nếu không Popen sẽ ném lỗi."""
    monkeypatch.setenv("RBDA_BROWSER", "/khong/he/ton/tai/browser.exe")
    assert browser_host.find_app_window_browser() != "/khong/he/ton/tai/browser.exe"


def test_open_ui_falls_back_to_normal_browser_when_none_found(monkeypatch):
    monkeypatch.setattr(browser_host, "find_app_window_browser", lambda: None)
    opened = []
    monkeypatch.setattr(browser_host.webbrowser, "open", opened.append)
    browser_host.open_ui("http://x/y", 1280, 800)
    # Thà mở tab thường còn hơn không mở được gì.
    assert opened == ["http://x/y"]


def test_open_ui_falls_back_when_launching_the_browser_fails(monkeypatch):
    monkeypatch.setattr(
        browser_host, "find_app_window_browser", lambda: "/khong/ton/tai"
    )
    opened = []
    monkeypatch.setattr(browser_host.webbrowser, "open", opened.append)
    browser_host.open_ui("http://x/y", 1280, 800)
    assert opened == ["http://x/y"]


def test_open_ui_uses_app_window_when_a_browser_exists(monkeypatch):
    calls = []
    monkeypatch.setattr(browser_host, "find_app_window_browser", lambda: "/bin/echo")
    monkeypatch.setattr(
        browser_host.subprocess, "Popen", lambda cmd, **kw: calls.append(cmd)
    )
    monkeypatch.setattr(
        browser_host.webbrowser, "open",
        lambda u: pytest.fail("khong duoc mo tab trinh duyet thuong"),
    )
    browser_host.open_ui("http://x/y", 1280, 800)
    assert calls
    assert any(c.startswith("--app=") for c in calls[0])


# ------------------------------------------------------------------ #
# TẮT ĐÚNG LÚC — không tắt nhầm khi thu nhỏ, tắt ngay khi đóng thật
#
# Cách đếm ping ĐÃ HỎNG THẬT trên máy học sinh ngày 30/08: trình duyệt
# không bóp thưa bộ đếm giờ của trang bị che, nó ĐÓNG BĂNG hẳn (Chromium
# intensive throttling, Edge còn thêm Efficiency mode). Ping ngừng hẳn,
# máy chủ tự tắt trong khi cửa sổ VẪN MỞ, và mọi thao tác sau đó báo
# "TypeError: Failed to fetch" mà không nói vì sao.
#
# Nay tín hiệu chính là một KẾT NỐI MỞ (EventSource): trình duyệt không
# đóng băng socket, chỉ đóng băng bộ đếm giờ. Ping chỉ còn là lưới đỡ khi
# kết nối đó không dùng được.
# ------------------------------------------------------------------ #


def test_ping_timeout_outlasts_browser_throttling():
    """Lưới đỡ khi không có kết nối sống nào thì vẫn phải rộng rãi."""
    assert browser_host._PING_TIMEOUT_SECONDS >= 90


def _mo_ket_noi_song(base, token):
    """Mở kết nối EventSource và GIỮ nguyên — không đọc tới hết."""
    return urllib.request.urlopen(f"{base}/__alive__?t={token}", timeout=5)


def test_ket_noi_song_can_dung_token(hosted):
    base, _ = hosted
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(f"{base}/__alive__?t=sai", timeout=5)
    assert e.value.code == 403


def test_shim_mo_ket_noi_song(hosted):
    base, token = hosted
    with urllib.request.urlopen(f"{base}/index.html?t={token}") as r:
        html = r.read().decode("utf-8")
    assert "EventSource" in html
    assert "/__alive__" in html


def test_cua_so_mo_thi_khong_tat_du_ping_bi_dong_bang(monkeypatch, api):
    """Đây chính là lỗi học sinh gặp: trang bị đóng băng, ping ngừng hẳn,
    máy chủ tắt trong khi cửa sổ vẫn mở. Kết nối sống phải giữ được nó."""
    monkeypatch.setattr(browser_host, "_PING_TIMEOUT_SECONDS", 1)
    monkeypatch.setattr(browser_host, "_GRACE_SECONDS", 1)
    monkeypatch.setattr(browser_host, "_ALIVE_BEAT_SECONDS", 0.2)
    url = browser_host.serve(api, RESOURCE_DIR, "index.html", open_browser=False)
    base, token = url.split("/index.html?t=")

    song = _mo_ket_noi_song(base, token)
    try:
        # Một ping duy nhất rồi im hẳn — đúng như trang bị đóng băng.
        urllib.request.urlopen(urllib.request.Request(
            f"{base}/__ping__", data=b"", method="POST"), timeout=5).read()
        time.sleep(8)          # quá xa ngưỡng ping (1 giây)
        res = _post(base, token, "get_dashboard_status")
        assert res["ok"] is True, "máy chủ đã tắt dù cửa sổ còn mở"
    finally:
        song.close()


def test_dong_cua_so_thi_may_chu_tat(monkeypatch, api):
    """Mặt còn lại: đóng thật thì phải tắt, không để tiến trình chạy ngầm."""
    monkeypatch.setattr(browser_host, "_PING_TIMEOUT_SECONDS", 1)
    monkeypatch.setattr(browser_host, "_GRACE_SECONDS", 1)
    monkeypatch.setattr(browser_host, "_ALIVE_BEAT_SECONDS", 0.2)
    url = browser_host.serve(api, RESOURCE_DIR, "index.html", open_browser=False)
    base, token = url.split("/index.html?t=")

    song = _mo_ket_noi_song(base, token)
    urllib.request.urlopen(urllib.request.Request(
        f"{base}/__ping__", data=b"", method="POST"), timeout=5).read()
    song.close()               # cửa sổ đóng

    for _ in range(40):        # tối đa 20 giây
        time.sleep(0.5)
        try:
            urllib.request.urlopen(f"{base}/index.html?t={token}", timeout=2).read()
        except urllib.error.HTTPError:
            raise              # máy chủ còn sống mà trả lỗi -> test sai
        except Exception:
            return             # đã tắt — đúng
    pytest.fail("máy chủ vẫn chạy sau khi cửa sổ đóng")


def test_shim_reports_the_window_closing(hosted):
    base, token = hosted
    with urllib.request.urlopen(f"{base}/index.html?t={token}") as r:
        html = r.read().decode("utf-8")
    # Đóng cửa sổ -> báo ngay, không phải chờ hết ngưỡng.
    assert "pagehide" in html
    assert "sendBeacon" in html
    assert "/__closed__" in html


def test_closing_the_window_shuts_the_server_down(hosted):
    base, token = hosted
    req = urllib.request.Request(
        f"{base}/__closed__?t={token}", data=b"", method="POST"
    )
    with urllib.request.urlopen(req) as r:
        assert json.loads(r.read())["ok"] is True

    # Máy chủ phải thật sự ngừng phục vụ (chứ không chỉ trả lời cho có).
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"{base}/index.html?t={token}", timeout=1)
        except urllib.error.HTTPError:
            raise
        except Exception:
            return
        time.sleep(0.2)
    pytest.fail("may chu van con phuc vu sau khi cua so da dong")


def test_close_request_without_the_token_is_ignored(hosted):
    """Không để một trang web khác trong cùng máy tắt được app."""
    base, token = hosted
    req = urllib.request.Request(f"{base}/__closed__?t=sai", data=b"", method="POST")
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req)
    assert exc.value.code == 403
    # và máy chủ vẫn sống
    with urllib.request.urlopen(f"{base}/index.html?t={token}") as r:
        assert r.status == 200


# ------------------------------------------------------------------ #
# KHÔNG LỘ DỮ LIỆU QUA MÁY CHỦ TĨNH
#
# Chạy từ mã nguồn thì thư mục tài nguyên CHÍNH LÀ thư mục chứa app.db.
# Trước bản vá, `GET /app.db` trả nguyên cơ sở dữ liệu học sinh, không cần
# token. Các test dưới đây dựng đúng tình huống đó: một thư mục tài nguyên
# có app.db, bản sao lưu, log và tệp kết quả nằm cạnh index.html.
# ------------------------------------------------------------------ #


@pytest.fixture
def hosted_canh_du_lieu(api, tmp_path):
    goc = tmp_path / "goc"
    goc.mkdir()
    (goc / "js").mkdir()
    for ten in ("index.html", "js/00_nen.js", "style.css"):
        with open(os.path.join(RESOURCE_DIR, ten), "rb") as f:
            (goc / ten).write_bytes(f.read())
    for ten in ("app.db", "app.db.bak-20260101_000000_000000",
                "loi_khoi_dong.txt", "ket_qua_phan_bo.csv", "api.py"):
        (goc / ten).write_text("DU LIEU HOC SINH", encoding="utf-8")
    (tmp_path / "ngoai.html").write_text("<p>ngoai</p>", encoding="utf-8")
    url = browser_host.serve(api, str(goc), "index.html", open_browser=False)
    return url.split("/index.html?t=")


def _get(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}),
                                timeout=5) as r:
        return r.status, r.read()


@pytest.mark.parametrize("ten", [
    "app.db", "app.db.bak-20260101_000000_000000", "loi_khoi_dong.txt",
    "ket_qua_phan_bo.csv", "api.py",
])
def test_tep_du_lieu_canh_giao_dien_khong_bi_phuc_vu(hosted_canh_du_lieu, ten):
    base, token = hosted_canh_du_lieu
    # Kể cả khi có token: token là để gọi API, không phải để tải tệp.
    for url in (f"{base}/{ten}", f"{base}/{ten}?t={token}"):
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get(url)
        assert exc.value.code == 404


def test_tep_giao_dien_van_duoc_phuc_vu(hosted_canh_du_lieu):
    base, token = hosted_canh_du_lieu
    assert _get(f"{base}/js/00_nen.js")[0] == 200
    assert _get(f"{base}/style.css")[0] == 200
    assert _get(f"{base}/index.html?t={token}")[0] == 200
    # "/" mở trang đầu, như cửa sổ ứng dụng vẫn làm
    assert b"window.pywebview" in _get(f"{base}/?t={token}")[1]


def test_khong_thoat_ra_ngoai_thu_muc_tai_nguyen(hosted_canh_du_lieu):
    """urllib tự gộp `..` nên phải gửi đường dẫn thô qua http.client."""
    import http.client

    base, token = hosted_canh_du_lieu
    cong = int(base.rsplit(":", 1)[1])
    for duong in (f"/../ngoai.html?t={token}", f"/%2e%2e/ngoai.html?t={token}"):
        c = http.client.HTTPConnection("127.0.0.1", cong, timeout=5)
        c.request("GET", duong)
        r = c.getresponse()
        assert r.status == 404, duong
        assert b"ngoai" not in r.read()
        c.close()


def test_trang_html_chua_token_phai_xin_bang_token(hosted):
    """Ai đọc được trang là đọc được token trong shim -> gọi được mọi API."""
    base, token = hosted
    for url in (f"{base}/index.html", f"{base}/index.html?t=sai", f"{base}/"):
        with pytest.raises(urllib.error.HTTPError) as exc:
            _get(url)
        assert exc.value.code == 403
    _, html = _get(f"{base}/index.html?t={token}")
    assert token.encode() in html


def test_host_la_bi_chan_dns_rebinding(hosted):
    """Trang lạ trỏ tên miền của nó về 127.0.0.1: trình duyệt gửi Host là
    tên miền lạ. Phải từ chối cả trang lẫn API, kể cả khi có token."""
    base, token = hosted
    la = {"Host": "ke-xau.example:" + base.rsplit(":", 1)[1]}
    with pytest.raises(urllib.error.HTTPError) as exc:
        _get(f"{base}/index.html?t={token}", la)
    assert exc.value.code == 403
    with pytest.raises(urllib.error.HTTPError) as exc:
        _post(base, token, "get_dashboard_status", extra_headers=la)
    assert exc.value.code == 403


def test_host_localhost_van_dung_duoc(hosted):
    base, token = hosted
    cong = base.rsplit(":", 1)[1]
    assert _get(f"{base}/index.html?t={token}", {"Host": f"localhost:{cong}"})[0] == 200


def test_than_yeu_cau_qua_lon_bi_tu_choi(hosted, monkeypatch):
    base, token = hosted
    monkeypatch.setattr(browser_host, "_TRAN_THAN_YEU_CAU", 10)
    with pytest.raises(urllib.error.HTTPError) as exc:
        _post(base, token, "get_dashboard_status", ["x" * 50])
    assert exc.value.code == 413


def test_loi_api_khong_tra_traceback(hosted):
    base, token = hosted
    res = _post(base, token, "submit_preferences", [])
    assert res["ok"] is False
    assert not any("Traceback" in str(e) for e in res["errors"])


def test_head_khong_di_vong_qua_lop_chan(hosted_canh_du_lieu):
    base, _ = hosted_canh_du_lieu
    req = urllib.request.Request(f"{base}/app.db", method="HEAD")
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(req, timeout=5)
    assert exc.value.code == 405


def test_trang_html_co_csp_va_shim_mang_dung_nonce(hosted):
    """Token nằm trong JS của trang, nên chỉ script của chính máy chủ và
    đúng đoạn shim (mang nonce) mới được chạy."""
    import re

    base, token = hosted
    with urllib.request.urlopen(f"{base}/index.html?t={token}") as r:
        csp = r.headers.get("Content-Security-Policy", "")
        html = r.read().decode("utf-8")
    assert "script-src 'self' 'nonce-" in csp
    assert "unsafe-inline" not in csp.split("script-src", 1)[1].split(";", 1)[0]
    nonce = re.search(r"'nonce-([^']+)'", csp).group(1)
    assert f'<script nonce="{nonce}">' in html
    # Mỗi lần tải một nonce mới — đoán trước được thì vô dụng.
    with urllib.request.urlopen(f"{base}/index.html?t={token}") as r:
        assert nonce not in r.headers.get("Content-Security-Policy", "")




def test_loi_bat_ngo_qua_http_khong_tra_traceback(hosted, api):
    """Phương thức ném lỗi thẳng ra ngoài (không qua _fail): browser_host
    từng gửi nguyên `traceback.format_exc()` về giao diện."""
    import chan_doan

    def hong():
        raise RuntimeError("hong qua http")
    api.get_dashboard_status = hong

    base, token = hosted
    res = _post(base, token, "get_dashboard_status")
    assert res["ok"] is False
    assert "Traceback" not in json.dumps(res, ensure_ascii=False), res
    assert [e["code"] for e in res["errors"]] == ["loi_ngoai_du_kien", "xem_nhat_ky"]
    log = os.path.join(os.path.dirname(api.db_path), chan_doan.TEN_LOG_UNG_DUNG)
    with open(log, encoding="utf-8") as f:
        assert "hong qua http" in f.read()
