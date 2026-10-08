"""
do_boc_tham.py
==============
Trong ba thiết kế bốc thăm cho thời khoá biểu tuần, thiết kế nào tốt nhất?

    python3 du_lieu_test/do_boc_tham.py
    python3 du_lieu_test/do_boc_tham.py --so-seed 50 --nhanh

CÂU HỎI ĐANG TRẢ LỜI
--------------------
Khi phần mềm xếp CLB cho cả TUẦN, mỗi buổi là một lần chạy RB-DA độc lập.
Nhưng bộ số bốc thăm dùng cho các buổi thì có ba cách dựng, và ba cách đó
cho ba kết quả khác nhau về CÔNG BẰNG:

  A1 `stb_tuan`   — bốc một lần, dùng cho cả tuần. Em bốc phải số xấu thì
                    xấu ở MỌI buổi: may rủi CỘNG DỒN.
  A2 `stb_ngay`   — mỗi buổi một hoán vị dẫn xuất từ (seed, tên buổi).
                    May rủi ĐỘC LẬP giữa các buổi.
  A3 `stb_co_bu`  — trước mỗi buổi đánh lại số theo (số CLB đã có, số gốc):
                    em đang ít CLB được lên trước.

Tệp này đo bốn câu, theo đúng thứ tự mà một kết luận cần chúng:

  TN7a. Trên dữ liệu 5 buổi của bộ mẫu, ba thiết kế khác nhau bao nhiêu —
        và khoảng tin cậy có chứa 0 không?
  TN7b. Khi BỎ HẲN ĐIỂM (bốc thăm quyết định tất), ba thiết kế khác nhau
        bao nhiêu, ở mọi mức tỉ lệ chọi?
  TN7c. Lợi thế của A2 thay đổi thế nào khi tỉ lệ em có điểm chạy từ 0%
        lên 100%? Đây là thí nghiệm CAN THIỆP, nó kiểm trực tiếp lời giải
        thích cho kết quả rỗng ở TN7a.
  TN7d. A3 có thật sự mở kênh khai gian không, và kênh đó rộng bao nhiêu?

HAI LỖI ĐÃ MẮC TRONG LẦN ĐO TRƯỚC — và cách tệp này chặn chúng
--------------------------------------------------------------
1. **Kết luận trên MỘT seed.** Một seed không đủ để so ba thiết kế bốc
   thăm, vì chính cái đang đo là tác động của may rủi. Ở đây mọi con số
   đều là trung bình trên nhiều seed, ghép cặp theo seed, kèm khoảng tin
   cậy bootstrap.

2. **In SAI CHIỀU hiệu số.** Bảng cũ ghi nhãn "(âm = A2 tốt hơn)" cho hiệu
   `A1 - A2` trên số em trắng tay, trong khi âm nghĩa là A1 ÍT em trắng
   tay hơn, tức A1 tốt hơn. Nhãn bị viết tay nên nó không đi theo công
   thức. Ở đây nhãn do `mo_ta_chieu()` SINH RA từ chính các biến đã dùng
   để tính hiệu, và `tests/test_boc_tham.py` có một test riêng canh chiều
   dấu đó.

CÁCH ĐO — GHÉP CẶP THEO SEED
----------------------------
Với mỗi seed: dựng dữ liệu (TN7b/c) hoặc lấy bộ mẫu (TN7a), bốc MỘT bộ số
`stb` duy nhất, rồi chạy CẢ BA thiết kế trên đúng bộ số đó. Nên chênh lệch
giữa ba cột là chênh lệch của THIẾT KẾ, không phải của dữ liệu hay của may
rủi — hai thứ đó đã bị giữ cố định trong mỗi cặp.

KHÔNG đụng `app.db` thật. Bộ mẫu 5 buổi được nạp vào CSDL tạm rồi xoá; dữ
liệu TN7b/c/d là MÔ PHỎNG hoàn toàn.
"""

import argparse
import itertools
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

GOC = os.path.dirname(os.path.abspath(__file__))
DUONG_JSON = os.path.join(GOC, "so_lieu_boc_tham.json")
BO_MAU = os.path.join(GOC, "bo_nhieu_buoi")
TEP_MAU = [
    "NHIEUBUOI_01_danh_sach_CLB.csv",
    "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
    "NHIEUBUOI_03_xep_hang_nguyen_vong.csv",
]

HAT_SINH = 20250911          # cố định để chạy lại ra đúng số cũ
SO_SEED_MAC_DINH = 200       # TN7a
SO_SEED_LUOI = 30            # TN7b, TN7c — mỗi ô
SO_LAN_BOOTSTRAP = 10000

CHE_DO = [
    ("A1 một lần cả tuần", "stb_tuan"),
    ("A2 bốc lại mỗi buổi", "stb_ngay"),
    ("A3 có bù", "stb_co_bu"),
]


# ===========================================================================
# PHẦN 1 — CHẠY MỘT TUẦN VÀ CHẤM KẾT QUẢ
# ===========================================================================

def nap_bo_mau():
    """Nạp bộ mẫu 5 buổi vào CSDL tạm, trả về dữ liệu trong bộ nhớ.

    Đi qua ĐÚNG đường mà giao diện đi (CSV -> import_csv_auto -> CSDL ->
    load_from_sqlite), không đọc tắt bằng csv.reader — để con số nói về
    đường dữ liệu thật chứ không về một bản sao gần đúng của nó.
    """
    from api import PipelineAPI

    thu_muc = tempfile.mkdtemp()
    try:
        duong_db = os.path.join(thu_muc, "app.db")
        api = PipelineAPI(duong_db, thu_muc_xuat=thu_muc)
        for ten in TEP_MAU:
            with open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
                kq = api.import_csv_auto(f.read())
            if not kq["ok"]:
                raise SystemExit("Nap %s that bai: %r" % (ten, kq["errors"]))
        st, cl, sc, ap, pr, _stb = loi.load_from_sqlite(duong_db)
    finally:
        shutil.rmtree(thu_muc, ignore_errors=True)
    return st, cl, sc, ap, pr


def chay_tuan(du_lieu, seed, che_do):
    """Một lần chạy cả tuần. Trả về (KetQuaTuan, bộ số đã bốc, hàm dự trữ)."""
    students, clubs, scores, app, prefs = du_lieu
    stb = loi.generate_stb_lottery(sorted(students), seed)
    elig = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda_nhieu_buoi(
        students, clubs, scores, app, prefs, stb, elig,
        che_do_boc_tham=che_do, seed=seed,
    )
    return kq, stb, elig


def cham_ket_qua(kq, du_lieu, elig=None, kiem_on_dinh=True):
    """Chấm một kết quả tuần thành các chỉ số so sánh được.

    "Trắng tay" chỉ tính trên những em CÓ KHAI ít nhất một nguyện vọng.
    Em không khai gì thì không thiết kế bốc thăm nào cứu được, đưa các em
    đó vào mẫu số chỉ làm loãng đúng cái đang đo.
    """
    _students, clubs, _scores, _app, prefs = du_lieu
    co_khai = [sid for sid, ds in prefs.items() if ds]
    so_clb = kq.so_clb_moi_em()
    dem = [so_clb.get(sid, 0) for sid in co_khai]

    hang = []
    for buoi in kq.ds_buoi:
        r = kq.per_buoi[buoi]
        for sid, cid in r.assignment.items():
            if cid is not None:
                h = r.rank_in_student_pref.get(sid)
                if h is not None:
                    hang.append(h)

    cap_pha_vo = None
    if kiem_on_dinh and elig is not None:
        van_de = loi.verify_stability_tuan(kq, clubs, prefs, elig)
        cap_pha_vo = sum(len(v) for v in van_de.values())

    return {
        "so_em_co_khai": len(co_khai),
        "trang_tay": sum(1 for d in dem if d == 0),
        "clb_tb": round(statistics.mean(dem), 4) if dem else 0.0,
        "do_lech": round(statistics.pstdev(dem), 4) if len(dem) > 1 else 0.0,
        "tong_suat": sum(dem),
        "hang_tb": round(statistics.mean(hang), 4) if hang else 0.0,
        "cap_pha_vo": cap_pha_vo,
    }


# ===========================================================================
# PHẦN 2 — THỐNG KÊ: HIỆU THEO CẶP, KHOẢNG TIN CẬY, VÀ CHIỀU DẤU
# ===========================================================================

def mo_ta_chieu(ten_a, ten_b, cang_nho_cang_tot):
    """Sinh nhãn chiều dấu TỪ CHÍNH các biến đã dùng để tính hiệu.

    Đây là chỗ sửa lỗi đã mắc lần trước. Nhãn cũ được gõ tay vào chuỗi in
    ra, nên khi công thức là `a - b` mà nhãn nói "âm = b tốt hơn" thì
    không có gì phát hiện ra — mã vẫn chạy, số vẫn đúng, chỉ câu chữ dẫn
    người đọc sang kết luận ngược.

    Hàm này nhận đúng ba thứ quyết định chiều: tên hai cột và chỉ số đó
    càng nhỏ càng tốt hay càng lớn càng tốt. Không có tham số nào khác,
    nên không có đường nào để nhãn lệch khỏi công thức.
    """
    ben_am = ten_a if cang_nho_cang_tot else ten_b
    ben_duong = ten_b if cang_nho_cang_tot else ten_a
    return ("hiệu = (%s) − (%s); âm = %s tốt hơn, dương = %s tốt hơn"
            % (ten_a, ten_b, ben_am, ben_duong))


def khoang_tin_cay(hieu, so_lan=SO_LAN_BOOTSTRAP, hat=HAT_SINH):
    """Khoảng tin cậy 95% kiểu bootstrap phân vị cho trung bình của `hieu`.

    Bootstrap chứ không phải công thức t: số em trắng tay là biến đếm,
    phân phối lệch và bị chặn dưới, nên giả định chuẩn của t không chắc
    đúng ở cỡ mẫu 30. Bootstrap không cần giả định đó.
    """
    n = len(hieu)
    if n < 2:
        return (None, None)
    rng = random.Random(hat)
    tb = []
    for _ in range(so_lan):
        tb.append(sum(hieu[rng.randrange(n)] for _ in range(n)) / n)
    tb.sort()
    return (round(tb[int(0.025 * so_lan)], 4), round(tb[int(0.975 * so_lan) - 1], 4))


def hieu_theo_cap(ten_a, ten_b, mau_a, mau_b, cang_nho_cang_tot=True,
                  so_lan=SO_LAN_BOOTSTRAP, hat=HAT_SINH):
    """So hai thiết kế trên cùng bộ seed. `mau_a[i]` và `mau_b[i]` cùng seed.

    Kết luận được SUY RA từ khoảng tin cậy và từ `cang_nho_cang_tot`, không
    viết tay: khoảng chứa 0 thì kết luận là "không phân biệt được", bất kể
    trung bình nghiêng về bên nào. Chênh 0,45 trên 160 em mà gọi tên người
    thắng là đọc nhiễu thành tín hiệu.
    """
    if len(mau_a) != len(mau_b):
        raise ValueError("hai mau phai cung so seed: %d vs %d" % (len(mau_a), len(mau_b)))
    hieu = [x - y for x, y in zip(mau_a, mau_b)]
    thap, cao = khoang_tin_cay(hieu, so_lan=so_lan, hat=hat)

    if cang_nho_cang_tot:
        a_thang = sum(1 for d in hieu if d < 0)
        b_thang = sum(1 for d in hieu if d > 0)
    else:
        a_thang = sum(1 for d in hieu if d > 0)
        b_thang = sum(1 for d in hieu if d < 0)

    if thap is None or (thap <= 0 <= cao):
        ket_luan = "không phân biệt được"
    else:
        nghieng_am = cao < 0
        thang = (ten_a if nghieng_am == cang_nho_cang_tot else ten_b)
        ket_luan = "%s tốt hơn" % thang

    return {
        "ten_a": ten_a,
        "ten_b": ten_b,
        "so_seed": len(hieu),
        "trung_binh_hieu": round(statistics.mean(hieu), 4),
        "ci95_thap": thap,
        "ci95_cao": cao,
        "so_seed_a_thang": a_thang,
        "so_seed_b_thang": b_thang,
        "so_seed_hoa": len(hieu) - a_thang - b_thang,
        "nhan_chieu": mo_ta_chieu(ten_a, ten_b, cang_nho_cang_tot),
        "ket_luan": ket_luan,
    }


# ===========================================================================
# PHẦN 3 — SINH DỮ LIỆU MÔ PHỎNG CÓ ĐIỀU KHIỂN
# ===========================================================================

# Sức hút của ba CLB trong một buổi. LỆCH CÓ CHỦ ĐÍCH, và chỗ lệch này là
# thứ làm cả TN7b có nội dung: nếu ba CLB đều được ưa như nhau và số chỗ
# chia đều, thì chỉ cần đủ chỗ là không em nào trắng tay, bốc thăm thế nào
# cũng vậy. Trường học không như thế — luôn có CLB đông và CLB vắng, mà số
# chỗ thì theo phòng học chứ không theo độ đông. Nên ở đây CLB đầu đông gấp
# năm CLB cuối, còn CHỖ thì CHIA ĐỀU.
SUC_HUT = (3.0, 1.5, 0.6)

# Độ dài danh sách nguyện vọng trong một buổi. Nghiêng về danh sách NGẮN:
# em chỉ khai một CLB là kiểu khai phổ biến nhất ngoài đời, và cũng đúng là
# nhóm dễ trắng tay nhất — nhóm mà thiết kế bốc thăm có hay không có tác
# dụng thì thấy rõ nhất.
TRONG_SO_DO_DAI = ((1, 0.50), (2, 0.30), (3, 0.20))


def _boc_theo_trong_so(rng, ds, trong_so, k):
    """Bốc k phần tử KHÔNG hoàn lại theo trọng số. Thứ tự bốc = thứ tự hạng."""
    ds, trong_so = list(ds), list(trong_so)
    ra = []
    for _ in range(min(k, len(ds))):
        tong = sum(trong_so)
        if tong <= 0:
            break
        moc, acc = rng.uniform(0, tong), 0.0
        for i, w in enumerate(trong_so):
            acc += w
            if acc >= moc:
                ra.append(ds.pop(i))
                trong_so.pop(i)
                break
    return ra


def sinh_bo_tong_hop(rng, so_em=200, so_buoi=5, so_clb_moi_buoi=3,
                     ti_le_choi=1.0, so_buoi_khai=5, ti_le_tier1=0.0,
                     thang_diem=(6.0, 7.0, 8.0, 9.0)):
    """Dựng một bài toán tuần với các tham số điều khiển được.

    Args:
        ti_le_choi: SỐ EM KHAI BUỔI ĐÓ / SỐ CHỖ BUỔI ĐÓ — đúng định nghĩa
            mà `api.get_tai_theo_buoi` dùng trên giao diện. Số chỗ được
            tính NGƯỢC từ số em đã khai, nên tỉ lệ chọi ra đúng bằng tham
            số này ở mọi buổi, không phải xấp xỉ.
        so_buoi_khai: mỗi em khai bao nhiêu buổi (bốc ngẫu nhiên).
        ti_le_tier1: tỉ lệ em CÓ ĐIỂM. 0,0 nghĩa là mọi em đều Tầng 2 và
            bốc thăm quyết định tất — đó là điều kiện của TN7b.
        thang_diem: tập điểm rời rạc. Tập càng nhỏ càng nhiều em hoà điểm,
            mà hoà điểm là chỗ duy nhất bốc thăm chen vào được trong Tầng 1.

    Không CLB nào có suất dự trữ. Suất dự trữ là một cơ chế ưu tiên riêng,
    nó sẽ chồng lên đúng cái đang đo; TN7 hỏi về bốc thăm nên phải tắt nó.
    """
    ds_buoi = ["buoi_%d" % i for i in range(1, so_buoi + 1)]
    ds_em = ["E%04d" % i for i in range(1, so_em + 1)]
    clb_cua_buoi = {
        b: ["%s_clb%d" % (b, j + 1) for j in range(so_clb_moi_buoi)]
        for b in ds_buoi
    }
    suc_hut = [SUC_HUT[j % len(SUC_HUT)] for j in range(so_clb_moi_buoi)]

    do_dai = [d for d, _ in TRONG_SO_DO_DAI]
    w_do_dai = [w for _, w in TRONG_SO_DO_DAI]

    preferences = {}
    for sid in ds_em:
        khai = rng.sample(ds_buoi, min(so_buoi_khai, so_buoi))
        ds = []
        for b in ds_buoi:                       # duyệt theo thứ tự buổi cho ổn định
            if b not in khai:
                continue
            k = min(rng.choices(do_dai, weights=w_do_dai)[0], so_clb_moi_buoi)
            ds += _boc_theo_trong_so(rng, clb_cua_buoi[b], suc_hut, k)
        preferences[sid] = ds

    # Số chỗ tính NGƯỢC từ số em đã khai, rồi CHIA ĐỀU cho các CLB trong buổi.
    clubs = {}
    for b in ds_buoi:
        tap = set(clb_cua_buoi[b])
        so_em_khai = sum(1 for ds in preferences.values() if any(c in tap for c in ds))
        tong_cho = max(so_clb_moi_buoi, int(round(so_em_khai / ti_le_choi)))
        goc, du = divmod(tong_cho, so_clb_moi_buoi)
        for j, cid in enumerate(clb_cua_buoi[b]):
            clubs[cid] = {
                "capacity": goc + (1 if j < du else 0),
                "reserve_capacity": 0,
                "reserve_group": None,
                "buoi": b,
            }

    students = {sid: {"reserve_group": None} for sid in ds_em}
    applicants = {cid: [] for cid in clubs}
    for sid in ds_em:
        for cid in preferences[sid]:
            applicants[cid].append(sid)

    tested_scores = {cid: {} for cid in clubs}
    so_tier1 = int(round(ti_le_tier1 * so_em))
    for sid in sorted(rng.sample(ds_em, so_tier1)):
        for cid in preferences[sid]:
            tested_scores[cid][sid] = rng.choice(thang_diem)

    return students, clubs, tested_scores, applicants, preferences


# ===========================================================================
# TN7a — BỘ MẪU 5 BUỔI CỦA TRƯỜNG, CÓ KHOẢNG TIN CẬY
# ===========================================================================

def tn7a_bo_mau(so_seed, so_seed_kiem_on_dinh=20, in_ra=True):
    """Ba thiết kế trên bộ mẫu 5 buổi, ghép cặp theo seed.

    Bộ mẫu CÓ ĐIỂM — khoảng 2/3 số em có điểm ở ít nhất một CLB. Đó là
    điều kiện của một trường thật, và cũng là lý do bảng này gần như không
    phân biệt được ba thiết kế. TN7c mới là chỗ kiểm lời giải thích đó.
    """
    du_lieu = nap_bo_mau()
    mau = {nhan: [] for nhan, _ in CHE_DO}
    phu = {nhan: [] for nhan, _ in CHE_DO}
    tong_cap_pha_vo = {nhan: 0 for nhan, _ in CHE_DO}

    for i in range(so_seed):
        seed = HAT_SINH + i
        for nhan, ma in CHE_DO:
            kq, _stb, elig = chay_tuan(du_lieu, seed, ma)
            kiem = i < so_seed_kiem_on_dinh
            t = cham_ket_qua(kq, du_lieu, elig=elig, kiem_on_dinh=kiem)
            mau[nhan].append(t["trang_tay"])
            phu[nhan].append(t)
            if t["cap_pha_vo"]:
                tong_cap_pha_vo[nhan] += t["cap_pha_vo"]

    def _gop(ten_chi_so, lam_tron=4):
        return {
            nhan: round(statistics.mean([t[ten_chi_so] for t in phu[nhan]]), lam_tron)
            for nhan, _ in CHE_DO
        }

    ket = {
        "so_seed": so_seed,
        "so_seed_kiem_on_dinh": so_seed_kiem_on_dinh,
        "so_em_co_khai": phu[CHE_DO[0][0]][0]["so_em_co_khai"],
        "theo_che_do": {
            nhan: {
                "trang_tay_tb": round(statistics.mean(mau[nhan]), 4),
                "trang_tay_min": min(mau[nhan]),
                "trang_tay_max": max(mau[nhan]),
                "clb_tb": round(statistics.mean([t["clb_tb"] for t in phu[nhan]]), 4),
                "do_lech_tb": round(statistics.mean([t["do_lech"] for t in phu[nhan]]), 4),
                "hang_tb": round(statistics.mean([t["hang_tb"] for t in phu[nhan]]), 4),
                "tong_cap_pha_vo": tong_cap_pha_vo[nhan],
            }
            for nhan, _ in CHE_DO
        },
        "hieu": {
            "A1_vs_A2": hieu_theo_cap(CHE_DO[0][0], CHE_DO[1][0],
                                      mau[CHE_DO[0][0]], mau[CHE_DO[1][0]]),
            "A1_vs_A3": hieu_theo_cap(CHE_DO[0][0], CHE_DO[2][0],
                                      mau[CHE_DO[0][0]], mau[CHE_DO[2][0]]),
        },
        "tong_suat_tb": _gop("tong_suat"),
    }

    if in_ra:
        print("\n" + "=" * 78)
        print("TN7a — BỘ MẪU 5 BUỔI (160 em / 13 CLB), %d seed, ghép cặp" % so_seed)
        print("=" * 78)
        print("%-22s %10s %6s %6s %9s %9s %8s"
              % ("Thiết kế", "Trắng tay", "min", "max", "CLB TB", "Độ lệch", "Phá vỡ"))
        print("-" * 78)
        for nhan, _ in CHE_DO:
            t = ket["theo_che_do"][nhan]
            print("%-22s %10.2f %6d %6d %9.3f %9.3f %8d"
                  % (nhan, t["trang_tay_tb"], t["trang_tay_min"], t["trang_tay_max"],
                     t["clb_tb"], t["do_lech_tb"], t["tong_cap_pha_vo"]))
        print("\nCặp phá vỡ PHẢI bằng 0 ở cả ba cột (%d seed đầu được kiểm). Khác 0"
              % so_seed_kiem_on_dinh)
        print("là lỗi cài đặt, và mọi số còn lại trong tệp này vô nghĩa.\n")
        for khoa in ("A1_vs_A2", "A1_vs_A3"):
            h = ket["hieu"][khoa]
            print("  %s" % h["nhan_chieu"])
            print("    trung bình %+.2f em · CI95 [%+.2f, %+.2f] · thắng %d–%d, hoà %d"
                  % (h["trung_binh_hieu"], h["ci95_thap"], h["ci95_cao"],
                     h["so_seed_a_thang"], h["so_seed_b_thang"], h["so_seed_hoa"]))
            print("    -> %s\n" % h["ket_luan"].upper())
    return ket


# ===========================================================================
# TN7b — LƯỚI ĐỐI CHỨNG: BỎ HẲN ĐIỂM, BỐC THĂM QUYẾT ĐỊNH TẤT
# ===========================================================================

TI_LE_CHOI_QUET = (0.5, 1.0, 1.5, 2.0, 4.0)
SO_BUOI_KHAI_QUET = (5, 3)


def _chay_mot_o(tao_du_lieu, so_seed, chi_so="trang_tay", kiem_on_dinh=0):
    """Chạy một ô của lưới: `so_seed` lần, mỗi lần cả ba thiết kế.

    `tao_du_lieu(i)` dựng bài toán cho lần thứ i. Bài toán được dựng MỘT
    lần rồi dùng cho cả ba thiết kế, nên chênh lệch giữa ba cột không thể
    đến từ dữ liệu — chỉ từ thiết kế.
    """
    mau = {nhan: [] for nhan, _ in CHE_DO}
    phu = {nhan: [] for nhan, _ in CHE_DO}
    cap_pha_vo = 0
    for i in range(so_seed):
        du_lieu = tao_du_lieu(i)
        for nhan, ma in CHE_DO:
            kq, _stb, elig = chay_tuan(du_lieu, HAT_SINH + i, ma)
            t = cham_ket_qua(kq, du_lieu, elig=elig, kiem_on_dinh=i < kiem_on_dinh)
            mau[nhan].append(t[chi_so])
            phu[nhan].append(t)
            cap_pha_vo += t["cap_pha_vo"] or 0
    return mau, phu, cap_pha_vo


def tn7b_luoi_thuan_boc_tham(so_seed, in_ra=True):
    """Không em nào có điểm -> mọi thứ tự ưu tiên đều do bốc thăm quyết định.

    Đây là điều kiện mà ba thiết kế bốc thăm được nghĩ ra để phục vụ. Nếu
    ở đây chúng cũng không khác nhau thì hoặc cài đặt sai, hoặc cả ý tưởng
    sai — nên ô nào cũng phải xem, không chỉ ô có kết quả đẹp.
    """
    ket = {}
    for ti_le in TI_LE_CHOI_QUET:
        for so_buoi_khai in SO_BUOI_KHAI_QUET:
            def tao(i, _t=ti_le, _b=so_buoi_khai):
                rng = random.Random(HAT_SINH + 7919 * i + int(_t * 100) + _b)
                return sinh_bo_tong_hop(
                    rng, ti_le_choi=_t, so_buoi_khai=_b, ti_le_tier1=0.0)

            mau, phu, cpv = _chay_mot_o(tao, so_seed, kiem_on_dinh=2)
            khoa = "choi_%.1f_khai_%d" % (ti_le, so_buoi_khai)
            ket[khoa] = {
                "ti_le_choi": ti_le,
                "so_buoi_khai": so_buoi_khai,
                "trang_tay_tb": {
                    nhan: round(statistics.mean(mau[nhan]), 4) for nhan, _ in CHE_DO
                },
                "clb_tb": {
                    nhan: round(statistics.mean([t["clb_tb"] for t in phu[nhan]]), 4)
                    for nhan, _ in CHE_DO
                },
                "tong_cap_pha_vo": cpv,
                "hieu_A1_vs_A2": hieu_theo_cap(
                    CHE_DO[0][0], CHE_DO[1][0], mau[CHE_DO[0][0]], mau[CHE_DO[1][0]]),
            }

    if in_ra:
        print("\n" + "=" * 78)
        print("TN7b — BỎ HẲN ĐIỂM: 200 em / 5 buổi / %d seed mỗi ô" % so_seed)
        print("=" * 78)
        print("Mọi em Tầng 2, không CLB nào có suất dự trữ -> bốc thăm quyết định tất.\n")
        print("%5s %6s %10s %10s %10s %12s %-22s"
              % ("Chọi", "Khai", "A1", "A2", "A3", "A2 cứu", "Kết luận A1 vs A2"))
        print("-" * 78)
        for khoa, o in ket.items():
            tt = o["trang_tay_tb"]
            a1, a2, a3 = (tt[nhan] for nhan, _ in CHE_DO)
            print("%5.1f %6d %10.2f %10.2f %10.2f %12.2f %-22s"
                  % (o["ti_le_choi"], o["so_buoi_khai"], a1, a2, a3, a1 - a2,
                     o["hieu_A1_vs_A2"]["ket_luan"]))
        print("\nCột 'A2 cứu' = số em trắng tay ở A1 trừ đi ở A2. Dương = A2 cứu")
        print("được ngần ấy em trên 200. Số CLB trung bình mỗi em gần như KHÔNG")
        print("đổi giữa ba cột — A2 không tạo thêm chỗ, nó chỉ đổi cách chia.")
        print("\n%5s %6s %10s %10s %10s" % ("Chọi", "Khai", "CLB TB A1", "A2", "A3"))
        print("-" * 78)
        for khoa, o in ket.items():
            c = o["clb_tb"]
            print("%5.1f %6d %10.3f %10.3f %10.3f"
                  % (o["ti_le_choi"], o["so_buoi_khai"],
                     *[c[nhan] for nhan, _ in CHE_DO]))
    return ket


# ===========================================================================
# TN7c — THÍ NGHIỆM CƠ CHẾ: VÌ SAO DỮ LIỆU CÓ ĐIỂM LẠI LÀM BA THIẾT KẾ
#        GẦN NHƯ TRÙNG NHAU?
# ===========================================================================

TI_LE_TIER1_QUET = (0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.00)
# Thang điểm từ RẤT THÔ (mọi em cùng một điểm -> hoà hết) tới RẤT MỊN
# (gần như không ai hoà điểm với ai).
THANG_DIEM_QUET = (
    ("1 mức", (7.0,)),
    ("2 mức", (6.0, 8.0)),
    ("4 mức", (6.0, 7.0, 8.0, 9.0)),
    ("11 mức", tuple(round(5.0 + 0.5 * i, 1) for i in range(11))),
    ("61 mức", tuple(round(4.0 + 0.1 * i, 1) for i in range(61))),
)


def _ti_le_loi_the(a1, a2):
    """Lợi thế của A2 tính theo PHẦN TRĂM số em trắng tay của A1.

    Cần cột này vì cột tuyệt đối có một chỗ dễ đọc nhầm: khi tỉ lệ Tầng 1
    tăng thì số em trắng tay của CẢ HAI thiết kế cùng giảm, nên lợi thế
    tuyệt đối giảm theo mà chưa chắc vì bốc thăm hết việc. Cột tỉ lệ hỏi
    đúng câu cần hỏi: trong số em mà A1 bỏ lại, A2 cứu được bao nhiêu phần?
    """
    tb1 = statistics.mean(a1)
    if tb1 <= 0:
        return None
    return round(100 * (tb1 - statistics.mean(a2)) / tb1, 2)


def tn7c_quet_ti_le_tier1(so_seed, in_ra=True):
    """Lợi thế của A2 thay đổi thế nào khi số em CÓ ĐIỂM tăng dần?

    LỜI GIẢI THÍCH ĐANG BỊ KIỂM. Trên bộ mẫu của trường, ba thiết kế gần
    như không phân biệt được. Lời giải thích đưa ra là: *điểm lấn át bốc
    thăm* — Tầng 1 luôn đứng trên Tầng 2, và một em không có điểm ở CLB
    nào thì là Tầng 2 ở MỌI buổi, nên rủi ro của em đã bị tương quan sẵn
    qua điểm chứ không qua bộ số thăm; bốc lại thăm mỗi buổi không gỡ được
    mối tương quan đó.

    Đó mới là quan sát tương quan (25/38 em trắng tay thuộc Tầng 2 thuần).
    Ở đây nó thành thí nghiệm CAN THIỆP: giữ nguyên mọi thứ, chỉ vặn một
    núm — tỉ lệ em có điểm — rồi xem lợi thế của A2 có tắt dần không.

    Hai lưới, vì "điểm lấn át" có hai nghĩa khác nhau và phải tách ra:
      c1. Bao nhiêu em CÓ điểm (Tầng 1 / Tầng 2). Núm này tạo ra loại
          tương quan mà lời giải thích nói tới.
      c2. Điểm MỊN tới đâu, khi mọi em đều có điểm. Núm này quyết định
          còn bao nhiêu ca hoà điểm cho bốc thăm chen vào.

    Nếu lợi thế A2 tắt dần ở c1 thì lời giải thích đứng vững. Nếu không
    tắt thì lời giải thích SAI và phải viết lại kết luận — không được lờ đi.
    """
    c1 = {}
    for ti_le in TI_LE_TIER1_QUET:
        def tao(i, _p=ti_le):
            rng = random.Random(HAT_SINH + 104729 * i + int(_p * 1000))
            return sinh_bo_tong_hop(
                rng, ti_le_choi=1.5, so_buoi_khai=5, ti_le_tier1=_p)

        mau, _phu, cpv = _chay_mot_o(tao, so_seed, kiem_on_dinh=2)
        a1, a2 = mau[CHE_DO[0][0]], mau[CHE_DO[1][0]]
        c1["tier1_%.2f" % ti_le] = {
            "ti_le_tier1": ti_le,
            "trang_tay_tb": {
                nhan: round(statistics.mean(mau[nhan]), 4) for nhan, _ in CHE_DO
            },
            "loi_the_A2": round(statistics.mean(a1) - statistics.mean(a2), 4),
            "loi_the_A2_ti_le": _ti_le_loi_the(a1, a2),
            "tong_cap_pha_vo": cpv,
            "hieu_A1_vs_A2": hieu_theo_cap(CHE_DO[0][0], CHE_DO[1][0], a1, a2),
        }

    c2 = {}
    for ten_thang, thang in THANG_DIEM_QUET:
        def tao(i, _t=thang):
            rng = random.Random(HAT_SINH + 15485863 * i + len(_t))
            return sinh_bo_tong_hop(
                rng, ti_le_choi=1.5, so_buoi_khai=5, ti_le_tier1=1.0,
                thang_diem=_t)

        mau, _phu, cpv = _chay_mot_o(tao, so_seed, kiem_on_dinh=2)
        a1, a2 = mau[CHE_DO[0][0]], mau[CHE_DO[1][0]]
        c2[ten_thang] = {
            "so_muc_diem": len(thang),
            "trang_tay_tb": {
                nhan: round(statistics.mean(mau[nhan]), 4) for nhan, _ in CHE_DO
            },
            "loi_the_A2": round(statistics.mean(a1) - statistics.mean(a2), 4),
            "loi_the_A2_ti_le": _ti_le_loi_the(a1, a2),
            "tong_cap_pha_vo": cpv,
            "hieu_A1_vs_A2": hieu_theo_cap(CHE_DO[0][0], CHE_DO[1][0], a1, a2),
        }

    if in_ra:
        print("\n" + "=" * 78)
        print("TN7c-1 — VẶN NÚM 'BAO NHIÊU EM CÓ ĐIỂM' (chọi 1,5× · 5 buổi · %d seed)"
              % so_seed)
        print("=" * 78)
        print("%12s %8s %8s %8s %11s %9s %-18s"
              % ("Tỉ lệ Tầng 1", "A1", "A2", "A3", "Lợi thế A2",
                 "= % của A1", "Kết luận A1 vs A2"))
        print("-" * 78)
        for o in c1.values():
            tt = o["trang_tay_tb"]
            tl = o["loi_the_A2_ti_le"]
            print("%11.0f%% %8.2f %8.2f %8.2f %11.2f %8s %-18s"
                  % (100 * o["ti_le_tier1"], *[tt[n] for n, _ in CHE_DO],
                     o["loi_the_A2"], "—" if tl is None else "%.0f%%" % tl,
                     o["hieu_A1_vs_A2"]["ket_luan"]))

        print("\n" + "=" * 78)
        print("TN7c-2 — VẶN NÚM 'ĐIỂM MỊN TỚI ĐÂU' (mọi em đều có điểm)")
        print("=" * 78)
        print("%12s %8s %8s %8s %11s %9s %-18s"
              % ("Thang điểm", "A1", "A2", "A3", "Lợi thế A2",
                 "= % của A1", "Kết luận A1 vs A2"))
        print("-" * 78)
        for ten, o in c2.items():
            tt = o["trang_tay_tb"]
            tl = o["loi_the_A2_ti_le"]
            print("%12s %8.2f %8.2f %8.2f %11.2f %8s %-18s"
                  % (ten, *[tt[n] for n, _ in CHE_DO],
                     o["loi_the_A2"], "—" if tl is None else "%.0f%%" % tl,
                     o["hieu_A1_vs_A2"]["ket_luan"]))
        print("\nHai bảng này đo CÙNG một điều bằng hai núm khác nhau: còn bao nhiêu")
        print("chỗ cho bốc thăm quyết định. Còn nhiều -> thiết kế bốc thăm quan")
        print("trọng. Còn ít -> ba thiết kế trùng nhau, và việc chọn cái nào không")
        print("còn là câu hỏi về công bằng nữa.")

    return {"theo_ti_le_tier1": c1, "theo_do_min_cua_diem": c2}


# ===========================================================================
# TN7d — A3 CÓ THẬT SỰ MỞ KÊNH KHAI GIAN KHÔNG?
# ===========================================================================

def _tach_theo_buoi(ds_nguyen_vong, buoi_cua):
    """[club_id] -> {buoi: [club_id]}, giữ nguyên thứ tự trong từng buổi."""
    ra = {}
    for cid in ds_nguyen_vong:
        ra.setdefault(buoi_cua[cid], []).append(cid)
    return ra


def _gop_theo_buoi(theo_buoi, thu_tu_buoi):
    ds = []
    for b in thu_tu_buoi:
        ds += theo_buoi.get(b, [])
    return ds


def cac_cach_khai_tuan(theo_buoi, thu_tu_buoi):
    """Không gian khai gian THEO TUẦN — chỉ đúng một kênh: GIẤU BỚT.

    Hai họ khai gian, và chỉ hai:

      F1. Giấu hẳn một tập con các buổi (không khai buổi đó).
      F2. Cắt ngắn danh sách trong đúng một buổi.

    Vì sao KHÔNG thử hoán vị thứ tự nguyện vọng: trong mỗi buổi, phần mềm
    chạy đúng `run_rbda`, và `do_khai_that.py` đã vét cạn mọi hoán vị lẫn
    mọi cách cắt ngắn TRONG một buổi, ra 0 em khai gian được. Kênh mới mà
    nhiều buổi mở ra là kênh khác hẳn: ở `stb_co_bu`, kết cục buổi trước
    sinh ra ưu tiên buổi sau, nên GIẤU buổi sớm để giữ "số CLB đã có" bằng
    0 là cách kiếm số thăm tốt hơn cho buổi mình thật sự muốn. Đó đúng là
    hai họ trên.

    PHẠM VI: "không tìm thấy" ở đây YẾU HƠN "không tồn tại" — không gian
    này bị giới hạn có chủ đích. Với A1 và A2 thì kết quả 0 còn có lý
    thuyết đỡ lưng (các buổi độc lập, mỗi buổi strategy-proof). Với A3 thì
    chỉ cần tìm THẤY một cách là đủ kết luận, nên giới hạn không gian
    không làm yếu kết luận về A3.
    """
    ds_buoi_da_khai = [b for b in thu_tu_buoi if theo_buoi.get(b)]
    ra = []

    # F1 — giấu một tập con. Bỏ tập rỗng (đó là khai thật) và bỏ trường hợp
    # giấu hết (chắc chắn ra 0 CLB, không thể tốt hơn).
    for r in range(1, len(ds_buoi_da_khai)):
        for to_hop in itertools.combinations(ds_buoi_da_khai, r):
            giau = set(to_hop)
            ra.append({b: list(v) for b, v in theo_buoi.items() if b not in giau})

    # F2 — cắt ngắn danh sách trong đúng một buổi.
    for b in ds_buoi_da_khai:
        for k in range(1, len(theo_buoi[b])):
            m = {bb: list(v) for bb, v in theo_buoi.items()}
            m[b] = theo_buoi[b][:k]
            ra.append(m)

    return ra


def _diem_tung_buoi(assignment_cua_em, theo_buoi_that):
    """Điểm của em ở từng buổi, chấm theo nguyện vọng THẬT. Lớn = tốt hơn.

    Nguyện vọng 1 trong danh sách L món được L điểm, nguyện vọng cuối được
    1 điểm, không có suất được 0. Thang này chỉ dùng để XẾP HƠN KÉM trong
    cùng một buổi, nên hình dạng cụ thể của nó không ảnh hưởng kết luận
    "trội hơn hoàn toàn" ở dưới.
    """
    ra = {}
    for b, ds in theo_buoi_that.items():
        cid = (assignment_cua_em or {}).get(b)
        ra[b] = (len(ds) - ds.index(cid)) if (cid in ds) else 0
    return ra


def do_khai_gian_mot_the_hien(du_lieu, seed, che_do, ds_em_thu):
    """Với mỗi em trong `ds_em_thu`, tìm cách giấu bớt có lợi (nếu có)."""
    students, clubs, scores, app, prefs = du_lieu
    buoi_cua = loi.buoi_cua_club(clubs)
    thu_tu_buoi = list(loi.nhom_theo_buoi(clubs))

    kq_that, _stb, _elig = chay_tuan(du_lieu, seed, che_do)

    loi_tong = 0
    troi_hoan_toan = 0
    vi_du = None
    for sid in ds_em_thu:
        that = prefs.get(sid, [])
        if len(that) < 2:
            continue
        theo_buoi_that = _tach_theo_buoi(that, buoi_cua)
        diem_that = _diem_tung_buoi(kq_that.assignment.get(sid), theo_buoi_that)
        tong_that = sum(diem_that.values())

        co_loi_tong = False
        co_troi = False
        for khai in cac_cach_khai_tuan(theo_buoi_that, thu_tu_buoi):
            prefs_thu = dict(prefs)
            prefs_thu[sid] = _gop_theo_buoi(khai, thu_tu_buoi)
            kq = chay_tuan((students, clubs, scores, app, prefs_thu), seed, che_do)[0]
            diem = _diem_tung_buoi(kq.assignment.get(sid), theo_buoi_that)

            hon_tong = sum(diem.values()) > tong_that
            if hon_tong and not co_loi_tong:
                co_loi_tong = True
                if vi_du is None:
                    vi_du = {
                        "student_id": sid,
                        "nguyen_vong_that": {b: list(v) for b, v in theo_buoi_that.items()},
                        "khai_gian": {b: list(v) for b, v in khai.items()},
                        "diem_khi_khai_that": diem_that,
                        "diem_khi_khai_gian": diem,
                        "tong_khi_khai_that": tong_that,
                        "tong_khi_khai_gian": sum(diem.values()),
                    }
            if (all(diem[b] >= diem_that[b] for b in theo_buoi_that)
                    and any(diem[b] > diem_that[b] for b in theo_buoi_that)):
                co_troi = True
            if co_loi_tong and co_troi:
                break

        loi_tong += int(co_loi_tong)
        troi_hoan_toan += int(co_troi)

    return {"so_em_thu": len(ds_em_thu), "loi_tong": loi_tong,
            "troi_hoan_toan": troi_hoan_toan, "vi_du": vi_du}


def tn7d_khai_gian(so_the_hien=12, so_em_mau=25, so_em=60, so_buoi=4, in_ra=True):
    """Dò kênh khai gian trên cả ba thiết kế.

    KỲ VỌNG GHI TRƯỚC KHI CHẠY: A1 = 0, A2 = 0, A3 > 0.

    Vì sao bảng này phải có: câu "đừng bao giờ dùng A3" cho tới lúc này mới
    là suy luận từ cách cài đặt. Nếu A3 cũng ra 0 thì câu đó phải hạ xuống
    thành một lo ngại lý thuyết, chứ không được giữ nguyên giọng.

    A3 cũng chính là ĐỐI CHỨNG NGƯỢC cho bộ dò: một bộ dò lúc nào cũng báo
    "không tìm thấy" thì không phân biệt được với một bộ dò hỏng. A3 là
    thiết kế mà lý thuyết nói là dò PHẢI thấy.

    Dữ liệu: mọi em Tầng 2 (bốc thăm quyết định tất) — đó là điều kiện mà
    `stb_co_bu` thật sự đổi thứ tự ưu tiên, nên cũng là nơi kênh khai gian
    của nó rộng nhất.
    """
    ket = {}
    for nhan, ma in CHE_DO:
        tong_em = tong_loi = tong_troi = 0
        vi_du = None
        for i in range(so_the_hien):
            rng = random.Random(HAT_SINH + 31337 * i)
            du_lieu = sinh_bo_tong_hop(
                rng, so_em=so_em, so_buoi=so_buoi, ti_le_choi=1.5,
                so_buoi_khai=so_buoi, ti_le_tier1=0.0)
            ds = sorted(du_lieu[0])
            mau = sorted(random.Random(HAT_SINH + i).sample(ds, min(so_em_mau, len(ds))))
            r = do_khai_gian_mot_the_hien(du_lieu, HAT_SINH + i, ma, mau)
            tong_em += r["so_em_thu"]
            tong_loi += r["loi_tong"]
            tong_troi += r["troi_hoan_toan"]
            if vi_du is None:
                vi_du = r["vi_du"]
        ket[nhan] = {
            "so_the_hien": so_the_hien,
            "tong_em_thu": tong_em,
            "so_em_loi_tong_diem": tong_loi,
            "so_em_troi_hoan_toan": tong_troi,
            "ti_le_troi_phan_tram": round(100 * tong_troi / tong_em, 2) if tong_em else 0.0,
            "vi_du": vi_du,
        }

    if in_ra:
        print("\n" + "=" * 78)
        print("TN7d — GIẤU BỚT BUỔI CÓ LỢI KHÔNG? (%d thể hiện × %d em, %d em / %d buổi)"
              % (so_the_hien, so_em_mau, so_em, so_buoi))
        print("=" * 78)
        print("%-22s %10s %16s %18s %9s"
              % ("Thiết kế", "Em đã thử", "Lợi tổng điểm", "Trội hoàn toàn", "Tỉ lệ"))
        print("-" * 78)
        for nhan, _ in CHE_DO:
            t = ket[nhan]
            print("%-22s %10d %16d %18d %8.2f%%"
                  % (nhan, t["tong_em_thu"], t["so_em_loi_tong_diem"],
                     t["so_em_troi_hoan_toan"], t["ti_le_troi_phan_tram"]))
        print("\nCột đáng đọc là 'Lợi tổng điểm'. ĐỐI CHỨNG NGƯỢC nằm ở đó: A3 PHẢI")
        print("khác 0, còn A1/A2 phải bằng 0. A3 bằng 0 nghĩa là bộ dò hỏng, và")
        print("hai số 0 của A1/A2 khi đó không nói lên điều gì.")
        print("\nCột 'Trội hoàn toàn' (không kém buổi nào, hơn ít nhất một buổi) ra 0")
        print("ở cả ba, và số 0 đó KHÔNG phải bằng chứng A3 an toàn — nó là hệ quả")
        print("của chính cách khai gian: muốn giữ 'số CLB đã có' bằng 0 để lên trước")
        print("ở buổi sau thì phải BỎ một suất ở buổi trước. Kênh của A3 là kênh")
        print("ĐÁNH ĐỔI, không phải kênh lợi không mất gì. Nó vẫn đủ hỏng: em nào")
        print("biết mẹo thì đổi được, em nào khai thật thì không, và dữ liệu nguyện")
        print("vọng thu về không còn là nguyện vọng thật nữa.")
        vd = ket[CHE_DO[2][0]]["vi_du"]
        if vd:
            print("\nMột ví dụ giấu bớt có lợi dưới A3 (em %s):" % vd["student_id"])
            print("  khai thật  %s" % vd["nguyen_vong_that"])
            print("             -> điểm từng buổi %s, tổng %d"
                  % (vd["diem_khi_khai_that"], vd["tong_khi_khai_that"]))
            print("  giấu bớt   %s" % vd["khai_gian"])
            print("             -> điểm từng buổi %s, tổng %d"
                  % (vd["diem_khi_khai_gian"], vd["tong_khi_khai_gian"]))
    return ket


# ===========================================================================
# MAIN
# ===========================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Đo ba thiết kế bốc thăm cho thời khoá biểu tuần")
    ap.add_argument("--so-seed", type=int, default=SO_SEED_MAC_DINH,
                    help="số seed cho TN7a (bộ mẫu của trường)")
    ap.add_argument("--so-seed-luoi", type=int, default=SO_SEED_LUOI,
                    help="số seed mỗi ô cho TN7b và TN7c")
    ap.add_argument("--so-the-hien-khai-gian", type=int, default=12)
    ap.add_argument("--nhanh", action="store_true",
                    help="chạy bản rút gọn để soát nhanh, KHÔNG dùng để trích số")
    ap.add_argument("--json", default=DUONG_JSON)
    args = ap.parse_args()

    if args.nhanh:
        args.so_seed, args.so_seed_luoi, args.so_the_hien_khai_gian = 20, 5, 3

    t0 = time.time()
    so_lieu = {
        "_ghi_chu": "Sinh bởi du_lieu_test/do_boc_tham.py — KHÔNG sửa tay.",
        "_ban_rut_gon": bool(args.nhanh),
        "hat_sinh": HAT_SINH,
        "so_seed_tn7a": args.so_seed,
        "so_seed_moi_o": args.so_seed_luoi,
        "tn7a_bo_mau": tn7a_bo_mau(args.so_seed),
        "tn7b_thuan_boc_tham": tn7b_luoi_thuan_boc_tham(args.so_seed_luoi),
        "tn7c_co_che": tn7c_quet_ti_le_tier1(args.so_seed_luoi),
        "tn7d_khai_gian": tn7d_khai_gian(so_the_hien=args.so_the_hien_khai_gian),
    }
    so_lieu["giay_chay"] = round(time.time() - t0, 2)
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(so_lieu, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("\nĐã ghi số liệu thô: %s  (%.1fs)" % (args.json, so_lieu["giay_chay"]))


if __name__ == "__main__":
    main()
