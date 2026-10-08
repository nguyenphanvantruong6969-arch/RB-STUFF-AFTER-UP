"""Chụp ảnh giao diện THẬT của phần mềm cho poster.

    python poster/chup_giao_dien.py

Dùng CSDL demo `du_lieu_test/app_DEMO_da_cham_diem.db` (DỮ LIỆU MÔ PHỎNG,
120 học sinh, 10 CLB, đã chấm điểm), chép sang thư mục tạm rồi chạy sắp xếp
với seed 42 — tệp gốc không bị đụng. Ảnh ra ở poster/hinh/.
"""

import glob
import os
import shutil
import sys
import tempfile

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)

from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from api import PipelineAPI  # noqa: E402

RA = os.path.join(GOC, "poster", "hinh")


def chromium():
    for c in ["/opt/pw-browsers/chromium"] + sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome")):
        if os.path.isfile(c):
            return c
    return None


def main():
    os.makedirs(RA, exist_ok=True)
    tam = tempfile.mkdtemp()
    os.environ["RBDA_THU_MUC_TAI_VE"] = tam
    db = os.path.join(tam, "app.db")
    shutil.copy(os.path.join(GOC, "du_lieu_test", "app_DEMO_da_cham_diem.db"), db)
    api = PipelineAPI(db)
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)

    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
        page = br.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        page.goto(url)
        page.wait_for_selector("#dropZone")
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(RA, "giao_dien_van_hanh.png"))

        page.locator('[data-tab="results"]').click()
        page.wait_for_timeout(1200)
        page.screenshot(path=os.path.join(RA, "giao_dien_ket_qua.png"))

        page.locator('[data-tab="scoring"]').click()
        page.wait_for_timeout(800)
        page.screenshot(path=os.path.join(RA, "giao_dien_cham_diem.png"))
        br.close()
    shutil.rmtree(tam, ignore_errors=True)
    print("Đã chụp vào", RA)


if __name__ == "__main__":
    main()
