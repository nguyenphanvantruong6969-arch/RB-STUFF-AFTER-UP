"""Đối chứng bộ đo: nó có đo đúng thứ nó nói không?

    ./.venv/bin/python du_lieu_test/thu_tai/doi_chung.py

Một bộ đo sai thì mọi con số trong báo cáo đều sai theo, mà nhìn vẫn
rất thuyết phục. Nên trước khi tin bất cứ số nào, cho nó đo lại một thứ
ĐÃ BIẾT KẾT QUẢ: bộ 120 học sinh thật trong du_lieu_test/, phải ra đúng
108/120 như SO_LIEU_DA_KIEM_CHUNG.md đã ghi.

LƯU Ý: KHÔNG so số của bộ đo với số của bộ 120 em ở cùng quy mô — hai
bên sinh dữ liệu theo hai cách khác nhau (Zipf so với bảng CLB tay), nên
lệch nhau là ĐÚNG. Cái phải giống là ĐƯỜNG ĐO, không phải dữ liệu.
"""

import base64
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api import PipelineAPI

THU_MUC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHO_DOI = {"xep_duoc": 108, "tong": 120, "so_vong": 7}


def main():
    d = tempfile.mkdtemp()
    api = PipelineAPI(os.path.join(d, "app.db"))

    t = time.perf_counter()
    for ten in ("TEST_01_danh_sach_CLB.xlsx", "TEST_02_chon_CLB_muon_thi.xlsx",
                "TEST_03_xep_hang_nguyen_vong.xlsx"):
        with open(os.path.join(THU_MUC, ten), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        du = api.xlsx_to_csv_text(b64)["data"]
        csv_text = du["csv_text"] if isinstance(du, dict) else du
        r = api.import_csv_auto(csv_text)
        if not r["ok"]:
            raise SystemExit("nap that bai %s: %r" % (ten, r["errors"]))
    t_nap = time.perf_counter() - t

    t = time.perf_counter()
    run = api.run_pipeline(seed=42)
    t_chay = time.perf_counter() - t

    that = {"xep_duoc": run["data"]["n_matched"],
            "tong": run["data"]["n_total"],
            "so_vong": run["data"]["rounds_run"]}

    print("Do lai bo 120 hoc sinh THAT bang dung duong ma bo do dung:")
    print("  thoi gian nap    : %.3f s" % t_nap)
    print("  thoi gian phan bo: %.3f s" % t_chay)
    print()
    lech = False
    for k, mong in CHO_DOI.items():
        ok = that[k] == mong
        lech = lech or not ok
        print("  %-10s do duoc %4d | tai lieu ghi %4d   %s"
              % (k, that[k], mong, "khop" if ok else "*** LECH ***"))

    if lech:
        raise SystemExit("\nBO DO SAI — dung tin so nao trong bao cao cho toi khi sua xong.")
    print("\nBo do khop voi so da cong bo. Cac phep do quy mo lon dung duoc.")


if __name__ == "__main__":
    main()
