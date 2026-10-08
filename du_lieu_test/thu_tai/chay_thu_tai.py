"""Thử tải: đo phần mềm ở nhiều quy mô khác nhau.

    ./.venv/bin/python du_lieu_test/thu_tai/chay_thu_tai.py

⚠️  DỮ LIỆU MÔ PHỎNG do máy sinh, không phải khảo sát học sinh có thật.

Đi ĐÚNG con đường người dùng đi — import_csv_auto → run_pipeline →
export_csv — chứ không gọi thẳng vào trong thuật toán. Gọi thẳng sẽ đo
được một con số đẹp hơn nhưng không phải con số người dùng gặp.

RÀNG BUỘC THIẾT KẾ (do học sinh đặt ra):
  Số CLB mỗi em DỰ THI giữ cố định ở 4, không tăng theo số CLB — bắt một
  em thi 50 kỳ thi là vô nghĩa. Còn số NGUYỆN VỌNG thì quét 3/5/10.
  Xếp 10 nguyện vọng mà chỉ thi 4 CLB thì 6 nguyện vọng còn lại rơi
  xuống Tầng 2, chỉ xét bằng số bốc thăm.
"""

import csv
import os
import sys
import time
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import random
import tempfile

from api import PipelineAPI

THU_MUC = os.path.dirname(os.path.abspath(__file__))
SEED = 2026
SO_CLB_DU_THI = 4          # cố định — xem ghi chú đầu tệp

# Lưới quét. Bỏ các ô vô nghĩa (100 CLB cho 200 em thì mỗi CLB 2 chỗ).
HOC_SINH = [200, 500, 1000, 2000, 5000]
SO_CLB = [10, 25, 50, 100]
SO_NGUYEN_VONG = [3, 5, 10]
TY_LE_CHO = [1.00, 1.08]
# Cach chia chi tieu cho tung CLB. "theo_nhu_cau" = CLB hot to hon
# (cung khop cau san). "chia_deu" = moi CLB bang nhau, giong truong
# that hon — va chinh cho lech cung/cau nay sinh ra tac nghen.
CACH_CHIA = ["chia_deu", "theo_nhu_cau"]


def hop_le(n_hs, n_clb):
    """Bỏ ô mà mỗi CLB chưa nổi 8 chỗ — không còn giống một trường thật."""
    return n_hs / n_clb >= 8


def trong_so_zipf(n):
    """Nhu cầu dồn: CLB thứ i hút ~1/i. Giống bộ dữ liệu thật, ở đó vài
    CLB đông gấp nhiều lần chỉ tiêu còn vài CLB gần như không ai chọn."""
    return [1.0 / (i + 1) for i in range(n)]


def boc_theo_trong_so(rng, ung_vien, ts, k):
    con = list(range(len(ung_vien)))
    ra = []
    for _ in range(min(k, len(con))):
        tong = sum(ts[i] for i in con)
        moc = rng.uniform(0, tong)
        chay = 0.0
        for i in con:
            chay += ts[i]
            if chay >= moc:
                ra.append(ung_vien[i])
                con.remove(i)
                break
    return ra


def sinh_csv(n_hs, n_clb, n_nv, ty_le, cach_chia="chia_deu"):
    """Trả về (csv_clb, csv_thi, csv_nv). Có seed nên tái lập được."""
    rng = random.Random(SEED)
    ma_clb = ["c%03d" % i for i in range(n_clb)]
    ts = trong_so_zipf(n_clb)

    tong_cho = int(round(n_hs * ty_le))
    if cach_chia == "theo_nhu_cau":
        # CLB càng đông người thích thì chỉ tiêu càng lớn. Cung khớp cầu
        # gần như hoàn hảo — trường hợp DỄ NHẤT.
        tong_ts = sum(ts)
        cho = [max(4, int(round(tong_cho * t / tong_ts))) for t in ts]
    else:
        # Mọi CLB chỉ tiêu bằng nhau, trong khi nhu cầu rất lệch. Đây mới
        # là hình dạng của một trường thật: không ai mở CLB to gấp mười
        # lần chỉ vì nhiều em thích nó. Chính chỗ lệch giữa cung và cầu
        # sinh ra tắc nghẽn.
        moi_clb = max(4, tong_cho // n_clb)
        cho = [moi_clb] * n_clb
    # 20% số CLB có suất dự trữ, đặt ở các CLB HOT (đầu danh sách).
    n_du_tru = max(1, n_clb // 5)
    dong_clb = ["club_id,name,capacity,reserve_capacity,reserve_group"]
    for i, cid in enumerate(ma_clb):
        r = max(1, cho[i] // 5) if i < n_du_tru else 0
        dong_clb.append("%s,CLB %d,%d,%d,%s" % (cid, i, cho[i], r,
                                                "chinh_sach" if r else ""))

    cot_thi = ["student_id,name,reserve_group"]
    for i in range(1, SO_CLB_DU_THI + 1):
        cot_thi.append("test_club_%d,score_%d" % (i, i))
    dong_thi = [",".join(cot_thi[:1] + cot_thi[1:])]
    dong_nv = ["student_id,name,reserve_group," +
               ",".join("pref_%d" % i for i in range(1, n_nv + 1))]

    for i in range(n_hs):
        sid = "S%06d" % i
        nhom = "chinh_sach" if rng.random() < 0.20 else ""
        nv = boc_theo_trong_so(rng, ma_clb, ts, n_nv)
        thi = nv[:SO_CLB_DU_THI]          # chỉ thi 4 nguyện vọng đầu
        tb = 6.3 if nhom else 7.6
        o = [sid, "HS %d" % i, nhom]
        for j in range(SO_CLB_DU_THI):
            if j < len(thi):
                o += [thi[j], "%.1f" % min(10.0, max(4.0, rng.gauss(tb, 1.15)))]
            else:
                o += ["", ""]
        dong_thi.append(",".join(o))
        dong_nv.append(",".join([sid, "HS %d" % i, nhom] + nv +
                                [""] * (n_nv - len(nv))))

    return "\n".join(dong_clb), "\n".join(dong_thi), "\n".join(dong_nv)


def mot_lan(n_hs, n_clb, n_nv, ty_le, cach_chia="chia_deu"):
    csv_clb, csv_thi, csv_nv = sinh_csv(n_hs, n_clb, n_nv, ty_le, cach_chia)
    d = tempfile.mkdtemp()
    duong_db = os.path.join(d, "app.db")
    api = PipelineAPI(duong_db)

    tracemalloc.start()
    t = time.perf_counter()
    for text in (csv_clb, csv_thi, csv_nv):
        r = api.import_csv_auto(text)
        if not r["ok"]:
            raise SystemExit("nap that bai: %r" % r["errors"])
    t_nap = time.perf_counter() - t

    t = time.perf_counter()
    run = api.run_pipeline(seed=42)
    t_chay = time.perf_counter() - t
    if not run["ok"]:
        raise SystemExit("chay that bai: %r" % run["errors"])

    t = time.perf_counter()
    ex = api.export_csv()
    t_xuat = time.perf_counter() - t
    _, dinh_bo_nho = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Xếp được nhờ CÓ ĐIỂM THI, hay chỉ nhờ bốc thăm (Tầng 2)?
    import sqlite3
    conn = sqlite3.connect(duong_db)
    co_diem = conn.execute("""
        SELECT COUNT(*) FROM match_results m
        JOIN club_scores s ON s.student_id = m.student_id AND s.club_id = m.club_id
        WHERE m.club_id IS NOT NULL
    """).fetchone()[0]
    kich_thuoc = os.path.getsize(duong_db)
    conn.close()

    n_xep = run["data"]["n_matched"]
    return {
        "hoc_sinh": n_hs, "so_clb": n_clb, "nguyen_vong": n_nv,
        "ty_le_cho": ty_le, "cach_chia_chi_tieu": cach_chia,
        "clb_du_thi": SO_CLB_DU_THI,
        "t_nap_giay": round(t_nap, 4),
        "t_phan_bo_giay": round(t_chay, 4),
        "t_xuat_giay": round(t_xuat, 4),
        "so_vong": run["data"]["rounds_run"],
        "xep_duoc": n_xep,
        "ty_le_xep": round(n_xep / n_hs * 100, 2),
        "chua_xep": n_hs - n_xep,
        "xep_nho_co_diem": co_diem,
        "xep_chi_nho_boc_tham": n_xep - co_diem,
        "db_MB": round(kich_thuoc / 1048576, 2),
        "dinh_bo_nho_MB": round(dinh_bo_nho / 1048576, 1),
        "so_tep_xuat": ex["data"]["n_club_files"],
    }


def main():
    o = [(a, b, c, d, e) for a in HOC_SINH for b in SO_CLB
         for c in SO_NGUYEN_VONG for d in TY_LE_CHO for e in CACH_CHIA
         if hop_le(a, b)]
    print("Se chay %d lan do. Bat dau...\n" % len(o))
    ket_qua = []
    t0 = time.perf_counter()
    for i, (a, b, c, d, e) in enumerate(o, 1):
        kq = mot_lan(a, b, c, d, e)
        ket_qua.append(kq)
        print("[%3d/%d] %5d em / %3d CLB / %2d NV / cho %d%% / %-13s -> "
              "phan bo %6.3fs · %2d vong · xep %5.1f%%"
              % (i, len(o), a, b, c, int(d * 100), e,
                 kq["t_phan_bo_giay"], kq["so_vong"], kq["ty_le_xep"]))

    p = os.path.join(THU_MUC, "ket_qua_thu_tai.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(ket_qua[0].keys()))
        w.writeheader()
        w.writerows(ket_qua)
    print("\nXong sau %.0f giay. Ghi %d dong vao %s"
          % (time.perf_counter() - t0, len(ket_qua), p))


if __name__ == "__main__":
    main()
