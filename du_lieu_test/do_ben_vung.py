"""
do_ben_vung.py
==============
"Ổn định" theo nghĩa BỀN: rung dữ liệu một chút thì kết quả đổi bao nhiêu?

    python3 du_lieu_test/do_ben_vung.py
    python3 du_lieu_test/do_ben_vung.py --so-seed 30

CÂU HỎI ĐANG TRẢ LỜI — và một chỗ dễ lẫn phải nói trước
-------------------------------------------------------
Chữ *"ổn định"* trong dự án này có HAI nghĩa, và chúng không liên quan gì
nhau:

  1. **Ổn định (stable)** — thuật ngữ lý thuyết ghép cặp: không tồn tại cặp
     (học sinh, CLB) nào cùng muốn phá kết quả. `verify_stability` đo cái
     này. Đây là tính chất ĐÚNG/SAI, và đã đo: 0 cặp phá vỡ.

  2. **Bền (robust)** — nghĩa thường ngày: sửa dữ liệu đầu vào một chút thì
     kết quả có nhảy lung tung không. Đây là tính chất ĐỊNH LƯỢNG, và **chưa
     từng được đo** ngoài phần đổi seed.

Nghĩa thứ hai mới là cái người dùng phần mềm quan tâm: *"nhập nhầm điểm một
em rồi sửa lại thì có mấy chục em bị xáo chỗ không?"*, *"thêm một em vào
danh sách muộn thì kết quả cũ còn dùng được không?"*

BỐN LOẠI NHIỄU ĐƯỢC ĐO
----------------------
| Nhiễu | Cách gây | Vì sao đáng đo |
|---|---|---|
| Chỉ tiêu ±1 | quét TỪNG CLB | CLB xin thêm/bớt một suất là chuyện thường |
| Thêm 1 học sinh | quét nhiều em giả | học sinh đăng ký muộn |
| Bớt 1 học sinh | quét nhiều em thật | học sinh rút hồ sơ |
| Nhiễu điểm ±0,1 và ±0,5 | quét nhiều seed nhiễu | chấm lệch tay, làm tròn |

Với mỗi nhiễu, đếm: bao nhiêu em ĐỔI CLB, bao nhiêu em ĐỔI KẾT CỤC có suất /
không suất, và — quan trọng nhất — **có sinh ra cặp phá vỡ nào không**. Nghĩa
(1) phải giữ nguyên ở MỌI nhiễu; nếu có nhiễu nào làm xuất hiện cặp phá vỡ
thì đó là LỖI, không phải phát hiện.

KHÔNG đụng `app.db` thật. Ba bộ dữ liệu đều là MÔ PHỎNG.
"""

import argparse
import json
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rbda_priority_pipeline as loi  # noqa: E402
from do_toi_uu_on_dinh import HAT_SINH, SEED_MOC, nap_ba_bo  # noqa: E402

SO_SEED_NHIEU = 20
SO_EM_QUET = 30

GOC = os.path.dirname(os.path.abspath(__file__))
DUONG_JSON = os.path.join(GOC, "so_lieu_ben_vung.json")


def _chay(du_lieu, seed=SEED_MOC):
    """Chạy RB-DA, trả về (xếp chỗ, số cặp phá vỡ)."""
    students, clubs, scores, app, prefs = du_lieu
    stb = loi.generate_stb_lottery(sorted(students), seed)
    elig = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda(students, clubs, scores, app, prefs, stb, elig)
    pha_vo = loi.verify_stability(kq, clubs, prefs, elig)
    return dict(kq.assignment), len(pha_vo)


def _so_sanh(goc, moi, ds_em_chung):
    """(số em đổi CLB, số em đổi kết cục có suất / không suất)."""
    doi_clb = sum(1 for s in ds_em_chung if goc.get(s) != moi.get(s))
    doi_suat = sum(1 for s in ds_em_chung
                   if (goc.get(s) is None) != (moi.get(s) is None))
    return doi_clb, doi_suat


# ---------------------------------------------------------------------------
# NHIỄU 1 — CHỈ TIÊU ±1
# ---------------------------------------------------------------------------

def nhieu_chi_tieu(du_lieu):
    students, clubs, scores, app, prefs = du_lieu
    goc, pv_goc = _chay(du_lieu)
    ds_em = sorted(students)
    ban_ghi = []
    for cid in sorted(clubs):
        for delta in (-1, +1):
            cap_moi = clubs[cid]["capacity"] + delta
            if cap_moi < 1:
                continue
            clubs_moi = {c: dict(i) for c, i in clubs.items()}
            clubs_moi[cid]["capacity"] = cap_moi
            clubs_moi[cid]["reserve_capacity"] = min(
                clubs_moi[cid]["reserve_capacity"], cap_moi)
            moi, pv = _chay((students, clubs_moi, scores, app, prefs))
            d_clb, d_suat = _so_sanh(goc, moi, ds_em)
            ban_ghi.append({"club": cid, "delta": delta, "doi_clb": d_clb,
                            "doi_suat": d_suat, "pha_vo": pv})
    return _tom_tat(ban_ghi, len(ds_em), pv_goc)


# ---------------------------------------------------------------------------
# NHIỄU 2 — THÊM / BỚT MỘT HỌC SINH
# ---------------------------------------------------------------------------

def nhieu_bot_hoc_sinh(du_lieu, so_em_quet, rng):
    students, clubs, scores, app, prefs = du_lieu
    goc, pv_goc = _chay(du_lieu)
    ds = sorted(students)
    mau = ds if len(ds) <= so_em_quet else sorted(rng.sample(ds, so_em_quet))
    ban_ghi = []
    for sid in mau:
        st = {s: v for s, v in students.items() if s != sid}
        pr = {s: v for s, v in prefs.items() if s != sid}
        ap = {c: [s for s in ds_c if s != sid] for c, ds_c in app.items()}
        sc = {c: {s: d for s, d in m.items() if s != sid} for c, m in scores.items()}
        moi, pv = _chay((st, clubs, sc, ap, pr))
        # So trên tập em CÒN LẠI — em bị bớt thì không có gì để so.
        d_clb, d_suat = _so_sanh(goc, moi, sorted(st))
        ban_ghi.append({"em": sid, "doi_clb": d_clb, "doi_suat": d_suat, "pha_vo": pv})
    return _tom_tat(ban_ghi, len(ds) - 1, pv_goc)


def nhieu_them_hoc_sinh(du_lieu, so_em_quet, rng):
    """Thêm một em MỚI với nguyện vọng và điểm ngẫu nhiên.

    Chú ý: bộ số bốc thăm ĐƯỢC VẼ LẠI cho cả trường ở đây, vì `_chay` gọi
    `generate_stb_lottery` trên tập mã mới. Đó là kịch bản XẤU NHẤT —
    `GIAI_DAP_BOC_THAM` mục 3 đã đo rằng thêm một em làm đổi số của gần như
    mọi người. Phần mềm thật KHÔNG làm thế (nó khoá bộ số rồi chèn riêng cho
    em mới bằng `chen_stb_cho_hoc_sinh_moi`), nên con số ở đây là CẬN TRÊN
    của mức xáo trộn, không phải mức xáo trộn thật.
    """
    students, clubs, scores, app, prefs = du_lieu
    goc, pv_goc = _chay(du_lieu)
    ds = sorted(students)
    ds_clb = sorted(clubs)
    ban_ghi = []
    for i in range(so_em_quet):
        moi_id = "ZZMOI%03d" % i
        st = dict(students)
        st[moi_id] = {"reserve_group": None}
        k = rng.randint(1, min(4, len(ds_clb)))
        chon = rng.sample(ds_clb, k)
        pr = dict(prefs)
        pr[moi_id] = chon
        ap = {c: list(v) for c, v in app.items()}
        sc = {c: dict(v) for c, v in scores.items()}
        for c in chon:
            ap[c].append(moi_id)
            if rng.random() < 0.6:
                sc[c][moi_id] = round(rng.uniform(5.0, 10.0), 1)
        moi, pv = _chay((st, clubs, sc, ap, pr))
        d_clb, d_suat = _so_sanh(goc, moi, ds)
        ban_ghi.append({"em": moi_id, "doi_clb": d_clb, "doi_suat": d_suat, "pha_vo": pv})
    return _tom_tat(ban_ghi, len(ds), pv_goc)


# ---------------------------------------------------------------------------
# NHIỄU 3 — RUNG ĐIỂM
# ---------------------------------------------------------------------------

def nhieu_diem(du_lieu, bien_do, so_seed):
    students, clubs, scores, app, prefs = du_lieu
    goc, pv_goc = _chay(du_lieu)
    ds = sorted(students)
    ban_ghi = []
    for seed in range(1, so_seed + 1):
        rng = random.Random(HAT_SINH + seed)
        sc = {
            c: {s: max(0.0, min(10.0, d + rng.uniform(-bien_do, bien_do)))
                for s, d in m.items()}
            for c, m in scores.items()
        }
        moi, pv = _chay((students, clubs, sc, app, prefs))
        d_clb, d_suat = _so_sanh(goc, moi, ds)
        ban_ghi.append({"seed": seed, "doi_clb": d_clb, "doi_suat": d_suat, "pha_vo": pv})
    return _tom_tat(ban_ghi, len(ds), pv_goc)


# ---------------------------------------------------------------------------
# NHIỄU 4 — ĐỔI SEED BỐC THĂM (mốc so sánh, số cũ đã có ở SO_LIEU mục 3c)
# ---------------------------------------------------------------------------

def nhieu_seed(du_lieu, so_seed):
    goc, pv_goc = _chay(du_lieu, SEED_MOC)
    ds = sorted(du_lieu[0])
    ban_ghi = []
    for seed in range(1, so_seed + 1):
        if seed == SEED_MOC:
            continue
        moi, pv = _chay(du_lieu, seed)
        d_clb, d_suat = _so_sanh(goc, moi, ds)
        ban_ghi.append({"seed": seed, "doi_clb": d_clb, "doi_suat": d_suat, "pha_vo": pv})
    return _tom_tat(ban_ghi, len(ds), pv_goc)


# ---------------------------------------------------------------------------
# TÓM TẮT
# ---------------------------------------------------------------------------

def _tom_tat(ban_ghi, tong_em, pha_vo_goc):
    if not ban_ghi:
        return None
    dc = [b["doi_clb"] for b in ban_ghi]
    ds = [b["doi_suat"] for b in ban_ghi]
    return {
        "so_phep_thu": len(ban_ghi),
        "tong_em": tong_em,
        "doi_clb_it_nhat": min(dc),
        "doi_clb_tb": round(statistics.mean(dc), 2),
        "doi_clb_nhieu_nhat": max(dc),
        "doi_clb_tb_phan_tram": round(100 * statistics.mean(dc) / tong_em, 2),
        "doi_suat_tb": round(statistics.mean(ds), 2),
        "doi_suat_nhieu_nhat": max(ds),
        "phep_thu_khong_doi_gi": sum(1 for x in dc if x == 0),
        "pha_vo_goc": pha_vo_goc,
        "pha_vo_lon_nhat": max(b["pha_vo"] for b in ban_ghi),
        "tong_pha_vo": sum(b["pha_vo"] for b in ban_ghi),
    }


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Đo độ bền của kết quả trước nhiễu")
    ap.add_argument("--so-seed", type=int, default=SO_SEED_NHIEU)
    ap.add_argument("--so-em-quet", type=int, default=SO_EM_QUET)
    ap.add_argument("--json", default=DUONG_JSON)
    args = ap.parse_args()

    t0 = time.time()
    ket = {}
    for ten, du_lieu in nap_ba_bo():
        rng = random.Random(HAT_SINH)
        ket[ten] = {
            "chi_tieu_1": nhieu_chi_tieu(du_lieu),
            "bot_1_hoc_sinh": nhieu_bot_hoc_sinh(du_lieu, args.so_em_quet, rng),
            "them_1_hoc_sinh": nhieu_them_hoc_sinh(du_lieu, args.so_em_quet, rng),
            "diem_0_1": nhieu_diem(du_lieu, 0.1, args.so_seed),
            "diem_0_5": nhieu_diem(du_lieu, 0.5, args.so_seed),
            "doi_seed": nhieu_seed(du_lieu, args.so_seed),
        }

    NHAN = [
        ("chi_tieu_1", "Chỉ tiêu ±1 (mỗi CLB)"),
        ("bot_1_hoc_sinh", "Bớt 1 học sinh"),
        ("them_1_hoc_sinh", "Thêm 1 học sinh"),
        ("diem_0_1", "Nhiễu điểm ±0,1"),
        ("diem_0_5", "Nhiễu điểm ±0,5"),
        ("doi_seed", "Đổi seed bốc thăm"),
    ]
    print("\n" + "=" * 78)
    print("TN6 — ĐỘ BỀN: RUNG DỮ LIỆU MỘT CHÚT THÌ KẾT QUẢ ĐỔI BAO NHIÊU?")
    print("=" * 78)
    for ten, bo in ket.items():
        print("\n### %s" % ten)
        print("%-24s %7s %20s %9s %9s"
              % ("Nhiễu", "Phép thử", "Đổi CLB ít/TB/nhiều", "% đổi TB", "Phá vỡ"))
        print("-" * 78)
        for khoa, nhan in NHAN:
            t = bo[khoa]
            if t is None:
                continue
            print("%-24s %7d %6d /%5.1f /%-6d %8.1f%% %9d"
                  % (nhan, t["so_phep_thu"], t["doi_clb_it_nhat"], t["doi_clb_tb"],
                     t["doi_clb_nhieu_nhat"], t["doi_clb_tb_phan_tram"],
                     t["tong_pha_vo"]))
    print("\nCột 'Phá vỡ' là TỔNG số cặp phá vỡ trên MỌI phép thử của dòng đó.")
    print("Cột này PHẢI bằng 0 ở mọi dòng: nhiễu được phép làm đổi ai vào đâu,")
    print("nhưng KHÔNG được phép làm kết quả mất tính ổn định. Khác 0 = LỖI.")

    so_lieu = {
        "_ghi_chu": "Sinh bởi du_lieu_test/do_ben_vung.py — KHÔNG sửa tay.",
        "so_seed": args.so_seed,
        "so_em_quet": args.so_em_quet,
        "ket_qua": ket,
        "giay_chay": round(time.time() - t0, 2),
    }
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(so_lieu, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("\nĐã ghi số liệu thô: %s  (%.1fs)" % (args.json, so_lieu["giay_chay"]))


if __name__ == "__main__":
    main()
