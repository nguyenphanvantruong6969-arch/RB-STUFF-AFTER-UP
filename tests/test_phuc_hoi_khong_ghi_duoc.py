"""Màn hình phục hồi khi chương trình KHÔNG GHI ĐƯỢC vào thư mục của nó.

Gặp thật trên máy Windows (27/09): giải nén vào một thư mục mà Windows chặn
ghi ("Quyền truy cập thư mục được kiểm soát"/OneDrive). app.db không tạo
được, và màn hình phục hồi báo "cơ sở dữ liệu gặp sự cố" kèm hai nút khôi
phục — sai nguyên nhân, và không nút nào giúp được. Giờ nó phải nói thẳng:
thư mục không ghi được, dời sang C:\\RBDA hoặc cho phép ứng dụng.
"""

import os

import pytest

import recovery
from recovery import RecoveryAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_thu_muc_binh_thuong_ghi_duoc(tmp_path):
    thu_muc = tmp_path / "chuong_trinh"
    thu_muc.mkdir()
    assert recovery.thu_muc_ghi_duoc(str(thu_muc)) is True
    # và không để lại tệp thử nào
    assert os.listdir(thu_muc) == []


def test_thu_muc_khong_ton_tai_la_khong_ghi_duoc(tmp_path):
    assert recovery.thu_muc_ghi_duoc(str(tmp_path / "khong" / "co")) is False


def test_trang_thai_bao_thu_muc_va_co_ghi_duoc(tmp_path, monkeypatch):
    rec = RecoveryAPI(str(tmp_path / "app.db"), "unable to open database file")
    d = rec.get_status()["data"]
    assert d["ghi_duoc"] is True
    assert d["thu_muc"] == str(tmp_path)

    monkeypatch.setattr(recovery, "thu_muc_ghi_duoc", lambda _: False)
    assert rec.get_status()["data"]["ghi_duoc"] is False


# ------------------------------------------------------------------ #
# Trình duyệt thật: màn hình phải đổi hẳn nội dung
# ------------------------------------------------------------------ #

pw = pytest.importorskip("playwright.sync_api", reason="chưa cài playwright")

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402


def _mo(tmp_path, ghi_duoc, monkeypatch):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    monkeypatch.setattr(recovery, "thu_muc_ghi_duoc", lambda _: ghi_duoc)
    rec = RecoveryAPI(str(tmp_path / "app.db"), "sqlite3.OperationalError: unable to open database file")
    return browser_host.serve(rec, GOC, "recovery.html", open_browser=False)


def _chay(url, ham):
    with pw.sync_playwright() as p:
        br = p.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        try:
            page = br.new_page(bypass_csp=True)
            loi = []
            page.on("pageerror", lambda e: loi.append(str(e)))
            page.goto(url)
            page.wait_for_selector("body[data-app-init='1']")
            page.wait_for_timeout(300)
            ham(page)
            assert loi == []
        finally:
            br.close()


def test_khong_ghi_duoc_thi_noi_dung_nguyen_nhan_va_cach_sua(tmp_path, monkeypatch):
    url = _mo(tmp_path, False, monkeypatch)

    def kiem(page):
        assert page.locator("#khongGhiDuoc").is_visible()
        # hai nút khôi phục vô ích -> ẩn
        assert not page.locator("#btnStartFresh").is_visible()
        assert not page.locator("#btnRestoreBackup").is_visible()
        chu = page.locator("body").inner_text()
        assert "không lưu được dữ liệu vào thư mục này" in chu
        assert "C:\\RBDA" in chu
        assert "Quyền truy cập thư mục được kiểm soát" in chu
        assert str(tmp_path) in chu
        assert "tệp dữ liệu bị lỗi" not in page.locator("#recoveryIntro").inner_text()

        # đổi ngôn ngữ: vẫn là thông điệp đúng, không quay về câu chung chung
        page.locator("#btnLangToggle").click()
        page.wait_for_timeout(200)
        assert "cannot save data in this folder" in page.locator("#recoveryHeading").inner_text()
        assert "Controlled folder access" in page.locator("body").inner_text()

        page.locator("#btnKiemLaiThuMuc").click()
        page.wait_for_timeout(300)
        assert "still not writable" in page.locator("#recoveryStatus").inner_text()

    _chay(url, kiem)


def test_ghi_duoc_thi_van_la_man_hinh_phuc_hoi_binh_thuong(tmp_path, monkeypatch):
    url = _mo(tmp_path, True, monkeypatch)

    def kiem(page):
        assert not page.locator("#khongGhiDuoc").is_visible()
        assert page.locator("#btnStartFresh").is_visible()
        assert "tệp dữ liệu bị lỗi" in page.locator("#recoveryIntro").inner_text()

    _chay(url, kiem)
