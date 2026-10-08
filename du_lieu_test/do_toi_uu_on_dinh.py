"""
do_toi_uu_on_dinh.py
====================
Thuật toán có thật sự đưa ra các cặp ghép TỐT NHẤT không?

    python3 du_lieu_test/do_toi_uu_on_dinh.py
    python3 du_lieu_test/do_toi_uu_on_dinh.py --so-the-hien 500

CÂU HỎI ĐANG TRẢ LỜI
--------------------
`verify_stability` đã canh được **0 cặp phá vỡ** — kết quả ỔN ĐỊNH. Nhưng
"ổn định" mới là *không ai phá được*, chưa phải *tốt nhất*. Tệp này hỏi bốn
câu mà toàn bộ tài liệu hiện có chưa trả lời:

  TN1. Trong TOÀN BỘ các cách ghép ổn định, kết quả của phần mềm có phải cách
       TỐT NHẤT cho học sinh không? (vét cạn, không suy luận)
  TN2. Nếu để CLB đề xuất thay vì học sinh đề xuất thì học sinh thiệt bao
       nhiêu? (đầu kia của dàn ổn định)
  TN4. So với bốn cơ chế khác trên cùng dữ liệu, phần mềm hơn kém chỗ nào?
  TN5. Còn cách nào làm nhiều em cùng lên nguyện vọng cao hơn không, và
       phải trả bằng bao nhiêu cặp phá vỡ?

VÌ SAO CÂU TN1 KHÔNG HIỂN NHIÊN
-------------------------------
Định lý Gale–Shapley nói DA do học sinh đề xuất cho ma trận ổn định tốt nhất
cho học sinh. Nhưng định lý đó giả định mỗi CLB có MỘT danh sách ưu tiên cố
định. `do_hai_canh_du_tru.py` đã đo được rằng hàm lựa chọn thật của phần mềm
**không phải** một thứ tự tuyến tính — suất dự trữ làm nó phụ thuộc vào việc
ai đang có mặt. Nên định lý kinh điển **không tự động áp dụng**, và câu trả
lời phải đến từ phép đo chứ không từ trích dẫn.

CÁCH ĐO TN1 — vét cạn, không lấy mẫu
------------------------------------
Với thể hiện đủ nhỏ, liệt kê MỌI phép gán khả dĩ, lọc lấy tập ổn định bằng
đúng `club_choice_function` của phần mềm, rồi so kết quả RB-DA với TỪNG phần
tử của tập đó. Không có chỗ nào cho may rủi: hoặc RB-DA được mọi em yếu-thích
hơn mọi ma trận ổn định khác, hoặc có phản ví dụ và phản ví dụ đó được in ra.

KHÔNG đụng `app.db` thật: mọi thứ nằm trong thư mục tạm, xoá sau khi chạy.
Ba bộ dữ liệu đều là MÔ PHỎNG — con số ở đây nói về ba bộ đó, không phải về
trường nào.
"""

import argparse
import json
import os
import random
import shutil
import statistics
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rbda_priority_pipeline as loi  # noqa: E402
import co_che_doi_chung as cc  # noqa: E402
from do_anh_huong_seed import BO_DU_LIEU, nap_bo  # noqa: E402

SEED_MOC = 42
SO_THE_HIEN_MAC_DINH = 300
SO_SEED_QUET = 20
HAT_SINH = 20250909          # cố định để chạy lại ra đúng số cũ

GOC = os.path.dirname(os.path.abspath(__file__))
DUONG_JSON = os.path.join(GOC, "so_lieu_toi_uu.json")


# ---------------------------------------------------------------------------
# NẠP DỮ LIỆU
# ---------------------------------------------------------------------------

def nap_ba_bo():
    """Nạp cả ba bộ dữ liệu vào bộ nhớ, trả về list (tên, dữ liệu)."""
    ra = []
    for ten, files in BO_DU_LIEU:
        thu_muc = tempfile.mkdtemp()
        try:
            db = nap_bo(thu_muc, files)
            students, clubs, scores, app, prefs, _stb = loi.load_from_sqlite(db)
        finally:
            shutil.rmtree(thu_muc)
        ra.append((ten.strip(), (students, clubs, scores, app, prefs)))
    return ra


def chay_rbda(du_lieu, seed):
    students, clubs, scores, app, prefs = du_lieu
    stb = loi.generate_stb_lottery(sorted(students), seed)
    elig = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda(students, clubs, scores, app, prefs, stb, elig)
    return dict(kq.assignment), stb, elig, kq


def bo_du_tru(du_lieu):
    """Bản sao của bộ dữ liệu với mọi `reserve_capacity` = 0."""
    students, clubs, scores, app, prefs = du_lieu
    clubs_moi = {
        cid: dict(info, reserve_capacity=0) for cid, info in clubs.items()
    }
    return students, clubs_moi, scores, app, prefs


# ---------------------------------------------------------------------------
# SINH THỂ HIỆN NHỎ ĐỂ VÉT CẠN
# ---------------------------------------------------------------------------

def sinh_the_hien_nho(rng, so_em=7, so_clb=4, co_du_tru=True):
    """Sinh một bài toán nhỏ đủ để liệt kê TOÀN BỘ tập ổn định.

    Ba lựa chọn có chủ đích, đều nhằm làm tập ổn định CÓ CƠ HỘI chứa nhiều
    hơn một phần tử — vì nếu mọi thể hiện chỉ có đúng một cách ghép ổn định
    thì câu hỏi "có phải cách tốt nhất không" tự động đúng và rỗng nghĩa:

      1. **Chật**: tổng chỉ tiêu nhỏ hơn số học sinh, nên CLB phải loại người.
      2. **Nhiều hoà điểm**: điểm lấy từ tập {5, 6, 7, 8}, nên bốc thăm và
         suất dự trữ có chỗ để làm đổi kết cục.
      3. **Nguyện vọng dài** (2 tới 4 CLB): danh sách càng dài thì nguyện
         vọng học sinh càng có cơ hội lệch khỏi ưu tiên của CLB — mà chính
         chỗ lệch đó mới sinh ra nhiều ma trận ổn định.

    Đo được với cấu hình này: khoảng **12%** thể hiện có nhiều hơn một ma
    trận ổn định. Ở 6 em / 3 CLB con số đó chỉ còn ~7%.
    """
    ds_em = ["E%02d" % i for i in range(so_em)]
    ds_clb = ["C%d" % i for i in range(so_clb)]

    tong_cho = rng.randint(max(2, so_em // 2), so_em - 1)
    suc_chua = {c: 0 for c in ds_clb}
    for _ in range(tong_cho):
        suc_chua[rng.choice(ds_clb)] += 1
    for c in ds_clb:
        suc_chua[c] = max(1, suc_chua[c])

    nhom = "nhom_a"
    students = {s: {"reserve_group": nhom if rng.random() < 0.3 else None}
                for s in ds_em}

    clubs = {}
    for c in ds_clb:
        cap = suc_chua[c]
        res = rng.randint(1, cap) if (co_du_tru and rng.random() < 0.5) else 0
        clubs[c] = {
            "capacity": cap,
            "reserve_capacity": res,
            "reserve_group": nhom if res else None,
        }

    preferences, applicants, scores = {}, {c: [] for c in ds_clb}, {c: {} for c in ds_clb}
    for s in ds_em:
        k = rng.randint(2, so_clb)
        chon = rng.sample(ds_clb, k)
        preferences[s] = chon
        for c in chon:
            applicants[c].append(s)
            if rng.random() < 0.6:
                scores[c][s] = float(rng.randint(5, 8))   # tập nhỏ -> nhiều hoà
    return students, clubs, scores, applicants, preferences


# ---------------------------------------------------------------------------
# TN1 — CÓ PHẢI MA TRẬN ỔN ĐỊNH TỐT NHẤT CHO HỌC SINH KHÔNG?
# ---------------------------------------------------------------------------

def tn1_toi_uu_hoc_sinh(so_the_hien, muc_tieu_nhieu=120, in_ra=True):
    """Vét cạn tập ổn định, kiểm RB-DA có phải phần tử tốt nhất cho học sinh.

    LẤY MẪU CÓ ĐIỀU KIỆN — đọc kỹ chỗ này trước khi trích số.
    Phần lớn thể hiện ngẫu nhiên chỉ có ĐÚNG MỘT ma trận ổn định. Trên
    những thể hiện đó, câu "RB-DA là ma trận tốt nhất" đúng một cách tầm
    thường: nó là ma trận DUY NHẤT. Chúng không nói được gì.

    Nên vòng lặp chạy tới khi đủ CẢ HAI: `so_the_hien` thể hiện bất kỳ (để
    biết tỉ lệ nền), VÀ `muc_tieu_nhieu` thể hiện có **nhiều hơn một** ma
    trận ổn định — đó mới là nhóm mà câu hỏi có nội dung. Cả hai nhóm đều
    được báo cáo riêng.
    """
    rng = random.Random(HAT_SINH)
    ket = {}

    for nhan, co_du_tru in (("khong_du_tru", False), ("co_du_tru", True)):
        t = {
            "so_the_hien": 0,
            "so_the_hien_nhieu_hon_1_on_dinh": 0,
            "tong_ma_tran_on_dinh": 0,
            "nhieu_nhat": 0,
            "rbda_nam_trong_tap_on_dinh": 0,
            "rbda_toi_uu_cho_hoc_sinh": 0,
            "rural_hospital_giu_nguyen": 0,
            # Chỉ tính trên nhóm CÓ nhiều hơn một ma trận ổn định:
            "nhom_kho_toi_uu": 0,
            "nhom_kho_trong_tap": 0,
            "nhom_kho_rural_hospital": 0,
            "phan_vi_du": [],
        }
        while t["so_the_hien"] < so_the_hien or \
                t["so_the_hien_nhieu_hon_1_on_dinh"] < muc_tieu_nhieu:
            th = sinh_the_hien_nho(rng, co_du_tru=co_du_tru)
            students, clubs, scores, app, prefs = th
            stb = loi.generate_stb_lottery(sorted(students), rng.randint(1, 10 ** 6))
            elig = loi.default_reserve_eligible_fn(students, clubs)
            try:
                tap = cc.liet_ke_ghep_on_dinh(students, clubs, scores, app, prefs, stb, elig)
            except ValueError:
                continue
            if not tap:
                continue                       # không có ma trận ổn định nào -> bỏ

            xep = dict(loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment)
            nhieu = len(tap) > 1
            trong_tap = any(all(m.get(s) == xep.get(s) for s in students) for m in tap)
            toi_uu = all(cc.yeu_thich_hon_moi_em(xep, m, prefs) for m in tap)
            tap_co_suat = {frozenset(s for s, c in m.items() if c is not None) for m in tap}
            bat_bien = len(tap_co_suat) == 1

            t["so_the_hien"] += 1
            t["tong_ma_tran_on_dinh"] += len(tap)
            t["nhieu_nhat"] = max(t["nhieu_nhat"], len(tap))
            t["rbda_nam_trong_tap_on_dinh"] += int(trong_tap)
            t["rbda_toi_uu_cho_hoc_sinh"] += int(toi_uu)
            t["rural_hospital_giu_nguyen"] += int(bat_bien)
            if nhieu:
                t["so_the_hien_nhieu_hon_1_on_dinh"] += 1
                t["nhom_kho_toi_uu"] += int(toi_uu)
                t["nhom_kho_trong_tap"] += int(trong_tap)
                t["nhom_kho_rural_hospital"] += int(bat_bien)

            if (not toi_uu or not trong_tap) and len(t["phan_vi_du"]) < 3:
                t["phan_vi_du"].append({
                    "clubs": {c: {k: v for k, v in i.items() if k != "reserve_group"}
                              for c, i in clubs.items()},
                    "preferences": prefs,
                    "rbda": xep,
                    "so_ma_tran_on_dinh": len(tap),
                    "trong_tap": trong_tap,
                })
        t["ti_le_nhieu_hon_1_phan_tram"] = round(
            100 * t["so_the_hien_nhieu_hon_1_on_dinh"] / t["so_the_hien"], 1)
        ket[nhan] = t

    # Vét cạn thêm trên bộ dữ liệu thật nhỏ nhất của dự án.
    ket["vi_du_huong_dan"] = {}
    for ten, du_lieu in nap_ba_bo():
        if not ten.startswith("vi_du"):
            continue
        students, clubs, scores, app, prefs = du_lieu
        xep, stb, elig, _ = chay_rbda(du_lieu, SEED_MOC)
        tap = cc.liet_ke_ghep_on_dinh(students, clubs, scores, app, prefs, stb, elig)
        ket["vi_du_huong_dan"] = {
            "so_ma_tran_on_dinh": len(tap),
            "rbda_trong_tap": any(all(m.get(s) == xep.get(s) for s in students) for m in tap),
            "rbda_toi_uu": all(cc.yeu_thich_hon_moi_em(xep, m, prefs) for m in tap),
        }

    if in_ra:
        print("\n" + "=" * 78)
        print("TN1 — RB-DA CÓ PHẢI MA TRẬN ỔN ĐỊNH TỐT NHẤT CHO HỌC SINH KHÔNG?")
        print("=" * 78)
        print("Vét cạn TOÀN BỘ tập ổn định (7 em / 4 CLB), so RB-DA với TỪNG phần tử.\n")
        print("%-14s %8s %9s %8s %8s %10s %10s"
              % ("Cấu hình", "Thể hiện", ">1 ổn đ.", "TB số MT", "Nh.nhất",
                 "Tối ưu", "Bất biến"))
        print("-" * 78)
        for nhan in ("khong_du_tru", "co_du_tru"):
            t = ket[nhan]
            n = t["so_the_hien"]
            print("%-14s %8d %4d(%4.1f%%) %8.2f %8d %10s %10s"
                  % (nhan, n, t["so_the_hien_nhieu_hon_1_on_dinh"],
                     t["ti_le_nhieu_hon_1_phan_tram"],
                     t["tong_ma_tran_on_dinh"] / n, t["nhieu_nhat"],
                     "%d/%d" % (t["rbda_toi_uu_cho_hoc_sinh"], n),
                     "%d/%d" % (t["rural_hospital_giu_nguyen"], n)))
        print("\nCHỈ TÍNH TRÊN NHÓM KHÓ — thể hiện có NHIỀU HƠN MỘT ma trận ổn định")
        print("(trên nhóm chỉ có một ma trận, câu hỏi đúng một cách tầm thường):")
        print("-" * 78)
        print("%-14s %12s %14s %14s" % ("Cấu hình", "Thể hiện khó", "RB-DA tối ưu",
                                        "Bất biến ai có suất"))
        for nhan in ("khong_du_tru", "co_du_tru"):
            t = ket[nhan]
            k = t["so_the_hien_nhieu_hon_1_on_dinh"]
            print("%-14s %12d %14s %14s"
                  % (nhan, k, "%d/%d" % (t["nhom_kho_toi_uu"], k),
                     "%d/%d" % (t["nhom_kho_rural_hospital"], k)))
        print("\n'Tối ưu'   = RB-DA được MỌI em yếu-thích hơn hoặc bằng MỌI ma trận ổn định khác.")
        print("'Bất biến' = tập em CÓ SUẤT giống hệt nhau ở mọi ma trận ổn định")
        print("             (định lý bệnh viện nông thôn — 'ai có suất' không phụ thuộc")
        print("             chọn ma trận ổn định nào; chỉ 'vào CLB nào' mới đổi).")
        v = ket["vi_du_huong_dan"]
        print("\nBộ vi_du_huong_dan (10 em / 4 CLB), vét cạn: %d ma trận ổn định · "
              "RB-DA nằm trong tập: %s · tối ưu: %s"
              % (v["so_ma_tran_on_dinh"], v["rbda_trong_tap"], v["rbda_toi_uu"]))
    return ket


# ---------------------------------------------------------------------------
# TN2 + TN4 — SO NĂM CƠ CHẾ
# ---------------------------------------------------------------------------

CO_CHE = [
    ("RB-DA (phần mềm)", None),
    ("DA do CLB đề xuất", cc.da_clb_de_xuat),
    ("Boston / nhận ngay", cc.co_che_boston),
    ("Xét theo bốc thăm", cc.co_che_thu_tu_boc_tham),
    ("TTC", cc.co_che_ttc),
]


def tn24_so_co_che(in_ra=True):
    ket = {}
    for ten, du_lieu in nap_ba_bo():
        students, clubs, scores, app, prefs = du_lieu
        xep_rbda, stb, elig, _ = chay_rbda(du_lieu, SEED_MOC)
        br = cc.tinh_base_rank(clubs, scores, app, stb)
        chon = cc._ham_chon(clubs, br, elig)

        bang_bo = {}
        for nhan, fn in CO_CHE:
            t0 = time.time()
            xep = xep_rbda if fn is None else fn(students, clubs, scores, app, prefs, stb, elig)
            giay = time.time() - t0
            tk = cc.thong_ke(xep, clubs, prefs, br, chon)
            tk["giay"] = round(giay, 4)
            tk["so_em_khac_rbda"] = sum(
                1 for s in students if xep.get(s) != xep_rbda.get(s))
            bang_bo[nhan] = tk
        ket[ten] = bang_bo

    if in_ra:
        print("\n" + "=" * 78)
        print("TN2 + TN4 — NĂM CƠ CHẾ TRÊN CÙNG DỮ LIỆU, CÙNG BỘ SỐ BỐC THĂM")
        print("=" * 78)
        for ten, bang_bo in ket.items():
            print("\n### %s   (seed %d)" % (ten, SEED_MOC))
            print("%-20s %5s %5s %6s %6s %7s %8s %7s"
                  % ("Cơ chế", "NV1", "NV2", "NV3+", "Trượt", "TB hạng",
                     "Phá vỡ", "Khác"))
            print("-" * 78)
            for nhan, _ in CO_CHE:
                t = bang_bo[nhan]
                print("%-20s %5d %5d %6d %6d %7s %8d %7d"
                      % (nhan, t["nv1"], t["nv2"], t["nv3_tro_len"],
                         t["khong_suat"], t["thu_hang_tb"], t["cap_pha_vo"],
                         t["so_em_khac_rbda"]))
        print("\n'Phá vỡ' = số cặp (học sinh, CLB) phá vỡ kết quả — khác 0 nghĩa là")
        print("           cơ chế đó KHÔNG ổn định. 'Khác' = số em xếp khác RB-DA.")
    return ket


def tn2_quet_seed(so_seed=SO_SEED_QUET, in_ra=True):
    """DA do CLB đề xuất có BAO GIỜ khác DA do học sinh đề xuất không?

    Nếu hai đầu của dàn ổn định trùng nhau thì tập ổn định chỉ có MỘT phần
    tử — và khi đó "tối ưu cho học sinh" là hiển nhiên nhưng cũng rỗng
    nghĩa. Quét nhiều seed để biết đó là tính chất của dữ liệu hay là may.
    """
    ket = {}
    for ten, du_lieu in nap_ba_bo():
        students, clubs, scores, app, prefs = du_lieu
        so_khac, chi_tiet = 0, []
        for seed in range(1, so_seed + 1):
            xep_hs, stb, elig, _ = chay_rbda(du_lieu, seed)
            xep_clb = cc.da_clb_de_xuat(students, clubs, scores, app, prefs, stb, elig)
            n = sum(1 for s in students if xep_hs.get(s) != xep_clb.get(s))
            chi_tiet.append(n)
            so_khac += int(n > 0)
        ket[ten] = {
            "so_seed": so_seed,
            "so_seed_hai_dau_khac_nhau": so_khac,
            "em_khac_nhieu_nhat": max(chi_tiet),
        }
    if in_ra:
        print("\n" + "=" * 78)
        print("TN2b — HAI ĐẦU CỦA DÀN ỔN ĐỊNH CÓ TRÙNG NHAU KHÔNG? (%d seed)" % so_seed)
        print("=" * 78)
        print("%-34s %14s %16s" % ("Bộ dữ liệu", "Seed cho KHÁC", "Em khác nhiều nhất"))
        print("-" * 78)
        for ten, t in ket.items():
            print("%-34s %10d/%-3d %16d"
                  % (ten, t["so_seed_hai_dau_khac_nhau"], t["so_seed"],
                     t["em_khac_nhieu_nhat"]))
        print("\n0 seed cho khác nghĩa là tập ổn định chỉ có MỘT phần tử trên bộ đó:")
        print("mọi cơ chế ổn định đều buộc phải cho ra đúng kết quả này.")
    return ket


# ---------------------------------------------------------------------------
# TN5 — CHU TRÌNH PARETO MỌI ĐỘ DÀI, VÀ CÁI GIÁ ĐỂ ĐI TỚI PARETO
# ---------------------------------------------------------------------------

def tn5_chu_trinh_pareto(so_seed=SO_SEED_QUET, in_ra=True):
    ket = {}
    for ten, du_lieu in nap_ba_bo():
        students, clubs, scores, app, prefs = du_lieu
        moc = None
        quet = []
        for seed in range(1, so_seed + 1):
            xep, stb, elig, _ = chay_rbda(du_lieu, seed)
            br = cc.tinh_base_rank(clubs, scores, app, stb)
            chon = cc._ham_chon(clubs, br, elig)
            ct, sau = cc.chu_trinh_pareto(xep, prefs)
            bang = cc.bang_thu_hang_nguyen_vong(prefs)
            len_hang = sum(1 for s in students
                           if cc.thich_hon(bang, s, sau.get(s), xep.get(s)))
            tk_sau = cc.thong_ke(sau, clubs, prefs, br, chon)
            tk_truoc = cc.thong_ke(xep, clubs, prefs, br, chon)
            ban_ghi = {
                "so_chu_trinh": len(ct),
                "do_dai": sorted(set(len(c) for c in ct)),
                "chu_trinh_dai_hon_2": sum(1 for c in ct if len(c) > 2),
                "em_len_hang": len_hang,
                "pha_vo_truoc": tk_truoc["cap_pha_vo"],
                "pha_vo_sau": tk_sau["cap_pha_vo"],
                "hang_tb_truoc": tk_truoc["thu_hang_tb"],
                "hang_tb_sau": tk_sau["thu_hang_tb"],
            }
            if seed == SEED_MOC or (moc is None and seed == 1):
                pass
            quet.append(ban_ghi)
        xep, stb, elig, _ = chay_rbda(du_lieu, SEED_MOC)
        br = cc.tinh_base_rank(clubs, scores, app, stb)
        chon = cc._ham_chon(clubs, br, elig)
        ct, sau = cc.chu_trinh_pareto(xep, prefs)
        bang = cc.bang_thu_hang_nguyen_vong(prefs)
        tk_sau = cc.thong_ke(sau, clubs, prefs, br, chon)
        tk_truoc = cc.thong_ke(xep, clubs, prefs, br, chon)
        ket[ten] = {
            "moc_seed_42": {
                "so_chu_trinh": len(ct),
                "do_dai": sorted(set(len(c) for c in ct)),
                "chu_trinh_dai_hon_2": sum(1 for c in ct if len(c) > 2),
                "em_len_hang": sum(1 for s in students
                                   if cc.thich_hon(bang, s, sau.get(s), xep.get(s))),
                "pha_vo_truoc": tk_truoc["cap_pha_vo"],
                "pha_vo_sau": tk_sau["cap_pha_vo"],
                "hang_tb_truoc": tk_truoc["thu_hang_tb"],
                "hang_tb_sau": tk_sau["thu_hang_tb"],
            },
            "quet_seed": {
                "so_seed": so_seed,
                "chu_trinh_it_nhat": min(q["so_chu_trinh"] for q in quet),
                "chu_trinh_tb": round(statistics.mean(q["so_chu_trinh"] for q in quet), 2),
                "chu_trinh_nhieu_nhat": max(q["so_chu_trinh"] for q in quet),
                "seed_cho_0_chu_trinh": sum(1 for q in quet if q["so_chu_trinh"] == 0),
                "co_chu_trinh_dai_hon_2": sum(1 for q in quet if q["chu_trinh_dai_hon_2"] > 0),
                "pha_vo_sau_khi_doi_tb": round(
                    statistics.mean(q["pha_vo_sau"] for q in quet), 1),
            },
        }

    if in_ra:
        print("\n" + "=" * 78)
        print("TN5 — CÒN CÁCH NÀO PARETO TỐT HƠN KHÔNG, VÀ GIÁ BAO NHIÊU?")
        print("=" * 78)
        print("Chu trình đổi chỗ: MỌI em trên chu trình cùng lên nguyện vọng cao hơn.")
        print("Bộ đo cũ (do_danh_doi_on_dinh.py) chỉ đếm được chu trình ĐỘ DÀI 2.\n")
        print("%-34s %7s %10s %9s %9s %9s"
              % ("Bộ dữ liệu", "Chu tr.", "Độ dài", "Em lên", "Phá vỡ→", "Hạng TB→"))
        print("-" * 78)
        for ten, t in ket.items():
            m = t["moc_seed_42"]
            print("%-34s %7d %10s %9d %4d→%-4d %4s→%-4s"
                  % (ten, m["so_chu_trinh"], m["do_dai"] or "—", m["em_len_hang"],
                     m["pha_vo_truoc"], m["pha_vo_sau"],
                     m["hang_tb_truoc"], m["hang_tb_sau"]))
        print("\nQuét %d seed:" % so_seed)
        print("%-34s %22s %12s %10s"
              % ("Bộ dữ liệu", "Chu trình ít/TB/nhiều", "Seed cho 0", "Có ct >2"))
        print("-" * 78)
        for ten, t in ket.items():
            q = t["quet_seed"]
            print("%-34s %8d / %5.1f / %-5d %8d/%-3d %10d"
                  % (ten, q["chu_trinh_it_nhat"], q["chu_trinh_tb"],
                     q["chu_trinh_nhieu_nhat"], q["seed_cho_0_chu_trinh"],
                     q["so_seed"], q["co_chu_trinh_dai_hon_2"]))
    return ket


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    ap.add_argument("--so-the-hien", type=int, default=SO_THE_HIEN_MAC_DINH,
                    help="số thể hiện nhỏ vét cạn cho TN1 (mặc định %d)"
                         % SO_THE_HIEN_MAC_DINH)
    ap.add_argument("--so-seed", type=int, default=SO_SEED_QUET,
                    help="số seed quét cho TN2b và TN5 (mặc định %d)" % SO_SEED_QUET)
    ap.add_argument("--json", default=DUONG_JSON,
                    help="nơi ghi số liệu thô (mặc định %s)" % DUONG_JSON)
    args = ap.parse_args()

    t0 = time.time()
    so_lieu = {
        "_ghi_chu": "Sinh bởi du_lieu_test/do_toi_uu_on_dinh.py — KHÔNG sửa tay. "
                    "Mọi bảng trong docs/NGHIEN_CUU_TOI_UU.md/.html đọc từ tệp này.",
        "seed_moc": SEED_MOC,
        "so_the_hien_tn1": args.so_the_hien,
        "so_seed_quet": args.so_seed,
        "tn1_toi_uu_hoc_sinh": tn1_toi_uu_hoc_sinh(args.so_the_hien),
        "tn24_so_co_che": tn24_so_co_che(),
        "tn2b_dan_on_dinh": tn2_quet_seed(args.so_seed),
        "tn5_chu_trinh_pareto": tn5_chu_trinh_pareto(args.so_seed),
    }
    so_lieu["giay_chay"] = round(time.time() - t0, 2)

    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(so_lieu, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("\nĐã ghi số liệu thô: %s  (%.1fs)" % (args.json, so_lieu["giay_chay"]))


if __name__ == "__main__":
    main()
