"""Đo tầng CSDL ở quy mô lớn — và xem chỉ mục giúp được bao nhiêu.

    ./.venv/bin/python du_lieu_test/thu_tai/do_csdl.py

Lược đồ hiện tại KHÔNG có chỉ mục phụ nào. Khoá chính của
club_test_selection và club_scores đều là (student_id, club_id), nên mọi
truy vấn lọc theo club_id ĐỨNG MỘT MÌNH — màn hình Chấm điểm chính là
loại đó — không dùng được khoá và phải quét bảng.

Tệp này CHỈ ĐO. Chỉ mục được tạo trên một BẢN SAO tạm, lược đồ thật
không bị đụng tới.
"""

import os
import shutil
import sqlite3
import statistics
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import PipelineAPI
from chay_thu_tai import sinh_csv

N_HS, N_CLB, N_NV = 2000, 50, 5
CHI_MUC = [
    "CREATE INDEX IF NOT EXISTS ix_tuyen_chon_club ON club_test_selection(club_id)",
    "CREATE INDEX IF NOT EXISTS ix_diem_club       ON club_scores(club_id)",
    "CREATE INDEX IF NOT EXISTS ix_ket_qua_club    ON match_results(club_id)",
    "CREATE INDEX IF NOT EXISTS ix_nguyen_vong_clb ON preferences(club_id)",
]


def do(ham, lan=5):
    """Chạy nhiều lần, lấy TRUNG VỊ — lần đầu luôn chậm vì bộ đệm nguội."""
    sos = []
    for _ in range(lan):
        t = time.perf_counter()
        ham()
        sos.append((time.perf_counter() - t) * 1000)
    return statistics.median(sos)


def dung_du_lieu(duong_db):
    api = PipelineAPI(duong_db)
    for text in sinh_csv(N_HS, N_CLB, N_NV, 1.08):
        api.import_csv_auto(text)
    api.run_pipeline(seed=42)
    return api


def cac_phep_do(api):
    mot_clb = api.list_clubs()["data"][0]["club_id"]
    return [
        ("Màn hình Chấm điểm (1 CLB)", lambda: api.get_club_applicants_for_scoring(mot_clb)),
        ("Tiến độ chấm điểm (mọi CLB)", lambda: api.get_scoring_overview()),
        ("Bảng Cảnh báo dữ liệu", lambda: api.get_data_health_report()),
        ("Bảng Kết quả (mọi học sinh)", lambda: api.get_match_results()),
        ("Tỉ lệ lấp đầy theo CLB", lambda: api.get_club_fill_stats()),
        ("Danh sách học sinh (1 trang)", lambda: api.list_students_admin("", 1, 100)),
    ]


def main():
    d = tempfile.mkdtemp()
    duong_db = os.path.join(d, "app.db")
    print("Dung du lieu %d hoc sinh / %d CLB..." % (N_HS, N_CLB))
    api = dung_du_lieu(duong_db)

    truoc = [(ten, do(f)) for ten, f in cac_phep_do(api)]

    # Bản sao, thêm chỉ mục, đo lại.
    duong_db2 = os.path.join(tempfile.mkdtemp(), "app.db")
    shutil.copy(duong_db, duong_db2)
    conn = sqlite3.connect(duong_db2)
    for cau in CHI_MUC:
        conn.execute(cau)
    conn.commit()
    conn.close()
    api2 = PipelineAPI(duong_db2)
    sau = dict((ten, do(f)) for ten, f in cac_phep_do(api2))

    print("\n%-32s %12s %12s %10s" % ("Truy vấn", "hiện nay", "có chỉ mục", "nhanh hơn"))
    print("-" * 70)
    for ten, ms in truoc:
        ms2 = sau[ten]
        print("%-32s %9.1f ms %9.1f ms %8.1fx"
              % (ten, ms, ms2, ms / ms2 if ms2 else 0))
    print("-" * 70)
    print("Kich thuoc .db: %.1f MB | co chi muc: %.1f MB"
          % (os.path.getsize(duong_db) / 1048576,
             os.path.getsize(duong_db2) / 1048576))
    print("\nLUU Y: chi muc chi tao tren BAN SAO tam. Luoc do that KHONG bi doi.")


if __name__ == "__main__":
    main()
