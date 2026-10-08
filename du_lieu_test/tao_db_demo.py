"""Dựng sẵn một cơ sở dữ liệu ĐÃ NẠP VÀ ĐÃ CHẤM ĐIỂM để demo.

    ./.venv/bin/python du_lieu_test/tao_db_demo.py

⚠️  DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT.

VÌ SAO CẦN TỆP NÀY
Bộ ba tệp Excel nay đã kèm sẵn điểm chấm (cột score_*), nên nạp tệp là
chạy được ngay. Tệp .db này chỉ để tiết kiệm thêm bước nạp: hôm trình
bày chép nó vào cạnh app là mở lên bấm "Chạy phân bổ" luôn.

CỐ Ý DỪNG TRƯỚC KHI CHẠY PHÂN BỔ. Phần đáng xem nhất là lúc thuật toán
chạy và kết quả hiện ra — nếu dựng sẵn cả phần đó thì không còn gì để xem.
"""

import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import PipelineAPI

THU_MUC = os.path.dirname(os.path.abspath(__file__))
DICH = os.path.join(THU_MUC, "app_DEMO_da_cham_diem.db")

TEP = [
    "TEST_01_danh_sach_CLB.xlsx",
    "TEST_02_chon_CLB_muon_thi.xlsx",
    "TEST_03_xep_hang_nguyen_vong.xlsx",
]


def doc_xlsx(api, ten):
    with open(os.path.join(THU_MUC, ten), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = api.xlsx_to_csv_text(b64)
    if not r["ok"]:
        raise SystemExit("khong doc duoc %s: %r" % (ten, r["errors"]))
    d = r["data"]
    return d["csv_text"] if isinstance(d, dict) else d


def main():
    if os.path.exists(DICH):
        os.remove(DICH)
    api = PipelineAPI(DICH)

    for ten in TEP:
        r = api.import_csv_auto(doc_xlsx(api, ten))
        if not r["ok"]:
            raise SystemExit("nhap that bai %s: %r" % (ten, r["errors"]))
        print("  nap  %-38s ok" % ten)

    # KHONG cham diem o day nua: diem den thang tu cot score_* trong
    # TEST_02. Cham them o day se ghi de len diem that cua tep.
    hr = api.get_data_health_report()["data"]
    print("\nCanh bao du lieu con lai: %d (nghiem trong: %d)"
          % (hr["n_warnings"], hr["n_high"]))
    for w in hr["warnings"]:
        print("   %s" % w["code"])

    print("\nDa dung: %s" % DICH)
    print("CHUA chay phan bo — de danh cho luc demo.")


if __name__ == "__main__":
    main()
