"""Đo tầng GIAO DIỆN: bảng Kết quả vẽ bao lâu khi có nhiều học sinh.

    xvfb-run -a ./.venv/bin/python du_lieu_test/thu_tai/do_giao_dien.py

Màn hình Kết quả (js/03_ket_qua.js) vẽ THẲNG mọi dòng ra DOM, không phân trang,
không ảo hoá:

    res.data.forEach((r) => { ... body.appendChild(tr); });

Thuật toán chạy trong phần nghìn giây, nhưng đây mới là chỗ người dùng
NGỒI CHỜ. Đo bằng Chromium thật, không phải ước lượng.
"""

import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import browser_host
from api import PipelineAPI
from chay_thu_tai import sinh_csv

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QUY_MO = [(200, 10), (500, 25), (1000, 50), (2000, 50)]


def dung(n_hs, n_clb):
    d = tempfile.mkdtemp()
    api = PipelineAPI(os.path.join(d, "app.db"))
    for text in sinh_csv(n_hs, n_clb, 5, 1.08):
        api.import_csv_auto(text)
    api.run_pipeline(seed=42)
    return api


def main():
    from playwright.sync_api import sync_playwright

    print("%-22s %14s %14s %14s" % ("Quy mô", "gọi backend", "vẽ bảng", "TỔNG người chờ"))
    print("-" * 68)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME, args=["--no-proxy-server"])
        for n_hs, n_clb in QUY_MO:
            api = dung(n_hs, n_clb)
            url = browser_host.serve(api, GOC, "index.html", open_browser=False)
            pg = br.new_page(viewport={"width": 1600, "height": 900})
            pg.goto(url, wait_until="domcontentloaded")
            pg.wait_for_timeout(700)

            # Do NHIEU LAN lay TRUNG VI: mot lan do don le nhieu tap
            # den muc 1000 em co the "cham hon" 2000 em, va so nhu vay
            # thi khong dung de ket luan gi.
            lan = []
            for _ in range(7):
                lan.append(pg.evaluate("""async () => {
                const t0 = performance.now();
                const res = await window.pywebview.api.get_match_results("");
                const t1 = performance.now();
                const body = document.getElementById("resultsTableBody");
                body.replaceChildren();
                res.data.forEach((r) => {
                    const tr = document.createElement("tr");
                    tr.innerHTML =
                      `<td>${r.student_id}</td><td>${r.name}</td>` +
                      `<td><span class="club-tag">${r.club_id || "—"}</span></td>` +
                      `<td>${r.matched_tier || "—"}</td><td>${r.rank_in_student_pref ?? "—"}</td>`;
                    body.appendChild(tr);
                });
                // ep trinh duyet TINH LAI bo cuc that su, khong chi xep hang doi
                body.offsetHeight;
                const t2 = performance.now();
                return {goi: t1 - t0, ve: t2 - t1, n: res.data.length};
            }"""))
            import statistics as _st
            goi = _st.median(x["goi"] for x in lan)
            ve = _st.median(x["ve"] for x in lan)
            print("%-22s %11.0f ms %11.0f ms %11.0f ms"
                  % ("%d em / %d CLB" % (n_hs, n_clb), goi, ve, goi + ve))
            pg.close()
            time.sleep(0.5)
        br.close()
    print("-" * 68)
    print("Do bang Chromium that duoi Xvfb. May giam khao co the nhanh hoac cham hon,")
    print("nhung TY LE giua cac quy mo thi giu nguyen.")


if __name__ == "__main__":
    main()
