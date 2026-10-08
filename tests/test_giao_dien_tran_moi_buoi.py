"""Trần theo buổi ở màn hình NHẬP TẠI CHỖ, kiểm bằng TRÌNH DUYỆT THẬT.

Hai lưới nhập là nơi duy nhất trần này gặp người dùng trực tiếp, và là nơi
tầng Python mù tịt: con số trần nằm trong `js/*.js`, câu thông báo nằm trong
`i18n.js`, còn việc đếm thì đếm trên DOM.

Lưới xếp hạng từng chặn ở `currentRanking.length >= 10` — tổng CẢ TUẦN. Với
sáu buổi thì em nào chọn 2 câu lạc bộ mỗi buổi đã chạm trần ở câu lạc bộ thứ
11 mà không hiểu vì sao, trong khi mỗi buổi em mới chọn có hai.

Lưới tick câu lạc bộ dự thi thì trước KHÔNG chặn gì cả.

Máy nào không có playwright/Chromium thì bỏ qua cả tệp.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402

BUOI = ("thu_2", "thu_3")


@pytest.fixture
def trang(api):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    for b in BUOI:
        for i in range(12):
            cid = "%s_c%02d" % (b, i)
            api.create_or_update_club(cid, "CLB %s %d" % (b, i), 30, 0, "", buoi=b)
    api.create_student_if_missing("HS001", "Em Thử")

    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(bypass_csp=True)  # CSP chan eval cua wait_for_function; test CSP rieng o test_giao_dien_sua_loi_p1
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.locator('[data-tab="fallback"]').click()
        page.fill("#studentSearchInput", "HS001")
        page.click("#btnStudentSearch")
        page.wait_for_selector("#studentSearchResults >> text=HS001")
        page.locator("#studentSearchResults >> text=HS001").first.click()
        page.wait_for_selector("#testSelectionGrid .option-row")
        yield page, loi, api
        br.close()


def _o_thi(page, cid):
    return page.locator('#testSelectionGrid .option-row[data-club-id="%s"]' % cid)


class TestTranClbThiTrenManHinh:

    def test_nam_clb_mot_buoi_duoc_tick(self, trang):
        page, loi, _ = trang
        for i in range(5):
            _o_thi(page, "thu_2_c%02d" % i).click()
        assert page.locator("#testSelectionGrid .option-row.is-checked").count() == 5
        assert loi == []

    def test_clb_thu_sau_cung_buoi_bi_chan(self, trang):
        page, loi, _ = trang
        for i in range(6):
            _o_thi(page, "thu_2_c%02d" % i).click()
        assert page.locator("#testSelectionGrid .option-row.is-checked").count() == 5, (
            "câu lạc bộ thứ 6 cùng buổi vẫn được tick"
        )
        assert loi == []

    def test_buoi_khac_khong_bi_tinh_chung(self, trang):
        """Đây là điều trần CŨ làm sai: đếm gộp mọi buổi."""
        page, loi, _ = trang
        for i in range(5):
            _o_thi(page, "thu_2_c%02d" % i).click()
        for i in range(5):
            _o_thi(page, "thu_3_c%02d" % i).click()
        assert page.locator("#testSelectionGrid .option-row.is-checked").count() == 10
        assert loi == []

    def test_bo_tick_luon_duoc_du_da_day(self, trang):
        """Chặn chỉ áp khi ĐANG BẬT THÊM — bỏ tick thì luôn cho."""
        page, loi, _ = trang
        for i in range(5):
            _o_thi(page, "thu_2_c%02d" % i).click()
        _o_thi(page, "thu_2_c00").click()
        assert page.locator("#testSelectionGrid .option-row.is-checked").count() == 4
        assert loi == []


class TestTranNguyenVongTrenManHinh:

    def _bam_nv(self, page, cid):
        page.locator('#rankingSourceGrid .option-row[data-club-id="%s"]' % cid).click()

    def test_muoi_moi_buoi_qua_hai_buoi_deu_duoc(self, trang):
        """20 nguyện vọng — trần cũ chặn ở cái thứ 11."""
        page, loi, _ = trang
        for b in BUOI:
            for i in range(10):
                self._bam_nv(page, "%s_c%02d" % (b, i))
        assert page.locator("#rankingList li, #rankingList .rank-row").count() == 20
        assert loi == []

    def test_nguyen_vong_thu_muoi_mot_cung_buoi_bi_chan(self, trang):
        page, loi, _ = trang
        for i in range(11):
            self._bam_nv(page, "thu_2_c%02d" % i)
        assert page.locator("#rankingList li, #rankingList .rank-row").count() == 10
        assert loi == []
