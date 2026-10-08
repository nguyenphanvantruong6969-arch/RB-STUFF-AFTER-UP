# -*- coding: utf-8 -*-
"""Hiệu ứng rê chuột lên khung và nút tắt hiệu ứng — kiểm bằng TRÌNH DUYỆT THẬT.

Ba điều phải đúng:

  1. Mặc định hiệu ứng BẬT: rê chuột lên một `.panel` thì khung nhấc lên
     (có `transform`) và có bóng.
  2. Bấm nút "Hiệu ứng" thì tắt: rê chuột lên khung không còn nhấc, không
     còn chuyển tiếp nào chạy — lựa chọn còn nguyên sau khi tải lại trang.
  3. Nhãn nút là chữ ĐỘNG (bật/tắt), nên đổi ngôn ngữ phải dịch lại nó.

Máy nào không có playwright/Chromium thì bỏ qua cả tệp.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("không có Chromium")
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#btnMotionToggle")
    yield page, loi
    br.close()
    pw.stop()


def _khung_khi_re_chuot(page):
    khung = page.locator("#view-pipeline .panel").first
    khung.hover()
    page.wait_for_timeout(400)  # chờ chuyển tiếp 220ms chạy xong
    return khung.evaluate(
        "e => { const s = getComputedStyle(e);"
        " return {transform: s.transform, shadow: s.boxShadow,"
        " transition: s.transitionDuration}; }")


def test_mac_dinh_bat_hieu_ung(trang):
    page, loi = trang
    nut = page.locator("#btnMotionToggle")
    assert nut.get_attribute("aria-pressed") == "true"
    assert nut.inner_text() == "Hiệu ứng: bật"
    s = _khung_khi_re_chuot(page)
    assert s["transform"] != "none"
    assert s["shadow"] != "none"
    assert loi == []


def test_tat_hieu_ung_va_nho_sau_khi_tai_lai(trang):
    page, loi = trang
    page.click("#btnMotionToggle")
    nut = page.locator("#btnMotionToggle")
    assert nut.get_attribute("aria-pressed") == "false"
    assert nut.inner_text() == "Hiệu ứng: tắt"
    s = _khung_khi_re_chuot(page)
    assert s["transform"] == "none"
    assert s["shadow"] == "none"
    assert s["transition"] == "0s"

    page.reload()
    page.wait_for_selector("#btnMotionToggle")
    assert page.locator("html.tat-hieu-ung").count() == 1
    assert page.locator("#btnMotionToggle").get_attribute("aria-pressed") == "false"

    page.click("#btnMotionToggle")
    assert page.locator("html.tat-hieu-ung").count() == 0
    assert loi == []


def test_nhan_nut_doi_theo_ngon_ngu(trang):
    page, loi = trang
    page.click("#btnLangToggle")
    assert page.locator("#btnMotionToggle").inner_text() == "Animations: on"
    page.click("#btnMotionToggle")
    assert page.locator("#btnMotionToggle").inner_text() == "Animations: off"
    page.click("#btnLangToggle")
    assert page.locator("#btnMotionToggle").inner_text() == "Hiệu ứng: tắt"
    assert loi == []
