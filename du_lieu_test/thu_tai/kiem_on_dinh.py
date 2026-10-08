"""Ở quy mô lớn, kết quả có còn ĐÚNG không — không chỉ nhanh?

    ./.venv/bin/python du_lieu_test/thu_tai/kiem_on_dinh.py

Chạy nhanh mà kết quả sai thì không tính là chạy được. Tệp này kiểm
tính ỔN ĐỊNH (stability) của kết quả ở 2 000 học sinh / 50 CLB:

  Một cặp (học sinh S, câu lạc bộ C) gọi là "cặp phá vỡ" nếu S thích C
  hơn CLB đang được xếp, VÀ C — nếu được chọn lại — sẽ nhận S. Tồn tại
  một cặp như vậy nghĩa là hai bên đều muốn đổi, tức kết quả không bền.

  Thuật toán họ Gale–Shapley bảo đảm KHÔNG có cặp nào như vậy. Đây là
  phép kiểm trực tiếp lời bảo đảm đó, ở quy mô lớn.
"""

import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rbda_priority_pipeline as loi
from api import PipelineAPI
from chay_thu_tai import sinh_csv

QUY_MO = [(500, 25), (2000, 50), (5000, 100)]


def main():
    print("%-20s %10s %14s %16s" % ("Quy mô", "số vòng", "cặp phá vỡ", "thời gian kiểm"))
    print("-" * 64)
    for n_hs, n_clb in QUY_MO:
        d = tempfile.mkdtemp()
        duong_db = os.path.join(d, "app.db")
        api = PipelineAPI(duong_db)
        for text in sinh_csv(n_hs, n_clb, 5, 1.08):
            api.import_csv_auto(text)
        run = api.run_pipeline(seed=42)

        (students, clubs, diem, ung_vien,
         nguyen_vong, stb) = loi.load_from_sqlite(duong_db)
        du_tru_fn = loi.default_reserve_eligible_fn(students, clubs)
        kq = loi.run_rbda(students, clubs, diem, ung_vien, nguyen_vong, stb, du_tru_fn)

        t = time.perf_counter()
        cap = loi.verify_stability(kq, clubs, nguyen_vong, du_tru_fn)
        t_kiem = time.perf_counter() - t

        print("%-20s %10d %14s %13.2f s"
              % ("%d em / %d CLB" % (n_hs, n_clb), run["data"]["rounds_run"],
                 "0  ✓" if not cap else "%d  *** LOI ***" % len(cap), t_kiem))
        if cap:
            for c in cap[:3]:
                print("    ", c)
            raise SystemExit("KET QUA KHONG ON DINH — day la loi nghiem trong.")
    print("-" * 64)
    print("Khong co cap pha vo nao o moi quy mo: ket qua ON DINH.")


if __name__ == "__main__":
    main()
