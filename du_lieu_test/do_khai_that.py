"""
do_khai_that.py
===============
Khai thật có phải là cách tốt nhất cho học sinh không?

    python3 du_lieu_test/do_khai_that.py
    python3 du_lieu_test/do_khai_that.py --so-the-hien 200 --so-em-mau 60

CÂU HỎI ĐANG TRẢ LỜI — và vì sao nó quan trọng nhất trong cả bộ đo
------------------------------------------------------------------
Mọi con số kiểu *"59% số em được nguyện vọng 1"* chỉ có nghĩa NẾU nguyện
vọng ghi trên tờ khai là nguyện vọng THẬT. Nếu một em có thể ghi sai thứ tự
rồi được CLB tốt hơn, thì:

  * con số "được nguyện vọng 1" đo cái khác chứ không đo sự hài lòng;
  * em nào biết mẹo thì lợi, em nào khai thật thì thiệt — đó là bất công
    ở đúng chỗ khó nhìn thấy nhất;
  * dữ liệu nguyện vọng thu về không dùng để nghiên cứu gì được nữa.

`compute_club_priority` có ghi một ràng buộc ở dòng 63–72: hàm này KHÔNG
được nhận thứ hạng nguyện vọng. Ràng buộc đó tồn tại chính vì lý do trên.
Nhưng nó mới là một dòng ghi chú — tệp này ĐO xem nó có thật sự chặn được
việc khai gian không.

CÁCH ĐO
-------
Với mỗi em: **giữ nguyên khai báo của mọi em khác**, thử mọi cách khai khác
cho riêng em đó, rồi chấm kết quả bằng nguyện vọng THẬT của em.

Không gian khai gian được thử: **mọi hoán vị** của danh sách nguyện vọng
thật, và **mọi cách cắt ngắn** của từng hoán vị (khai 1 nguyện vọng, 2, 3...).
Đó là toàn bộ cách một em có thể nói dối bằng tờ khai — trừ việc thêm CLB
mình không thích, mà thêm vào thì không bao giờ có lợi (CLB đó chấm theo
nguyện vọng thật là *không có suất*).

Điểm thi và việc tick chọn CLB muốn thi GIỮ NGUYÊN. Trong phần mềm này đó
là hai bước tách rời khỏi bước xếp hạng, và điểm đến từ chấm mù. Tệp này chỉ
đo khả năng gian ở bước XẾP HẠNG NGUYỆN VỌNG.

ĐỐI CHỨNG NGƯỢC — phần bắt buộc phải có
---------------------------------------
Một bộ dò khai gian mà lúc nào cũng báo "không tìm thấy" thì vô dụng: có thể
nó hỏng chứ không phải cơ chế tốt. Nên bộ đo chạy CÙNG phép dò trên cơ chế
**Boston/nhận ngay** — cơ chế mà lý thuyết nói là thưởng cho khai gian. Nếu
Boston cũng ra 0 thì bộ dò hỏng, và mọi số trong tệp này phải bỏ đi.

KHÔNG đụng `app.db` thật. Ba bộ dữ liệu đều là MÔ PHỎNG.
"""

import argparse
import itertools
import json
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rbda_priority_pipeline as loi  # noqa: E402
import co_che_doi_chung as cc  # noqa: E402
from do_toi_uu_on_dinh import (  # noqa: E402
    HAT_SINH, SEED_MOC, chay_rbda, nap_ba_bo, sinh_the_hien_nho,
)

SO_THE_HIEN_MAC_DINH = 200
SO_EM_MAU_MAC_DINH = 40
SO_KHAI_TOI_DA = 2000        # trần không gian tìm kiếm trên bộ dữ liệu lớn

GOC = os.path.dirname(os.path.abspath(__file__))
DUONG_JSON = os.path.join(GOC, "so_lieu_khai_that.json")


# ---------------------------------------------------------------------------
# BỌC CÁC CƠ CHẾ VỀ CÙNG MỘT CHỮ KÝ
# ---------------------------------------------------------------------------

def _rbda(students, clubs, scores, app, prefs, stb, elig):
    return dict(loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment)


CO_CHE_THU = [
    ("RB-DA (phần mềm)", _rbda),
    ("Boston / nhận ngay", cc.co_che_boston),
    ("Xét theo bốc thăm", cc.co_che_thu_tu_boc_tham),
    ("TTC", cc.co_che_ttc),
]


# ---------------------------------------------------------------------------
# KHÔNG GIAN KHAI GIAN
# ---------------------------------------------------------------------------

def cac_cach_khai(nguyen_vong_that, tran=None, rng=None):
    """Mọi hoán vị của danh sách nguyện vọng, và mọi cách cắt ngắn của chúng.

    Với danh sách dài L thì số cách là L! x L — 6 nguyện vọng đã là 4320
    cách cho MỘT em. Trên bộ dữ liệu lớn phải chặn bằng `tran`; khi chặn thì
    LUÔN giữ nguyên nhóm "cắt ngắn danh sách thật" (đó là kiểu khai gian dễ
    nghĩ ra nhất trong đời thực: *chỉ ghi CLB mình chắc đỗ*), rồi mới bốc
    ngẫu nhiên phần còn lại.
    """
    L = len(nguyen_vong_that)
    if L == 0:
        return []

    # Nhóm 1 — cắt ngắn chính danh sách thật. Luôn giữ, không bao giờ bốc bỏ.
    cach = [tuple(nguyen_vong_that[:k]) for k in range(1, L)]

    con_lai = []
    for hv in itertools.permutations(nguyen_vong_that):
        for k in range(1, L + 1):
            ct = hv[:k]
            if ct != tuple(nguyen_vong_that) and ct not in cach:
                con_lai.append(ct)
        if tran is not None and len(con_lai) > tran * 4:
            break

    con_lai = list(dict.fromkeys(con_lai))
    if tran is not None and len(cach) + len(con_lai) > tran:
        con_lai = (rng or random.Random(0)).sample(con_lai, max(0, tran - len(cach)))
    return cach + con_lai


def diem_ket_cuc(cid, nguyen_vong_that):
    """Chấm kết cục theo nguyện vọng THẬT. Số nhỏ = tốt hơn.

    CLB không nằm trong danh sách thật bị chấm bằng "không có suất" — em
    không muốn vào đó, nên được xếp vào đó không phải là lợi.
    """
    if cid is None or cid not in nguyen_vong_that:
        return len(nguyen_vong_that) + 1
    return nguyen_vong_that.index(cid)


# ---------------------------------------------------------------------------
# PHÉP DÒ CHÍNH
# ---------------------------------------------------------------------------

def do_mot_the_hien(du_lieu, stb, elig, co_che_fn, ds_em_thu, tran=None, rng=None):
    """Với mỗi em trong `ds_em_thu`, tìm cách khai gian có lợi (nếu có).

    Returns:
        {"so_em_thu", "so_em_khai_gian_duoc", "muc_loi": [...], "vi_du": {...}}
    """
    students, clubs, scores, app, prefs = du_lieu
    goc = co_che_fn(students, clubs, scores, app, prefs, stb, elig)

    khai_gian_duoc, muc_loi, vi_du = 0, [], None
    for sid in ds_em_thu:
        that = prefs.get(sid, [])
        if len(that) < 2:
            continue                       # 1 nguyện vọng thì không có gì để đổi
        diem_goc = diem_ket_cuc(goc.get(sid), that)
        if diem_goc == 0:
            continue                       # đã được nguyện vọng 1 -> không thể hơn

        tot_nhat = diem_goc
        khai_tot_nhat = None
        for khai in cac_cach_khai(that, tran=tran, rng=rng):
            prefs_thu = dict(prefs)
            prefs_thu[sid] = list(khai)
            kq = co_che_fn(students, clubs, scores, app, prefs_thu, stb, elig)
            d = diem_ket_cuc(kq.get(sid), that)
            if d < tot_nhat:
                tot_nhat = d
                khai_tot_nhat = list(khai)

        if khai_tot_nhat is not None:
            khai_gian_duoc += 1
            muc_loi.append(diem_goc - tot_nhat)
            if vi_du is None:
                vi_du = {
                    "student_id": sid,
                    "nguyen_vong_that": that,
                    "khai_gian": khai_tot_nhat,
                    "hang_khi_khai_that": diem_goc + 1,
                    "hang_khi_khai_gian": tot_nhat + 1,
                }

    return {
        "so_em_thu": len(ds_em_thu),
        "so_em_khai_gian_duoc": khai_gian_duoc,
        "muc_loi_tb": round(statistics.mean(muc_loi), 2) if muc_loi else 0.0,
        "muc_loi_lon_nhat": max(muc_loi) if muc_loi else 0,
        "vi_du": vi_du,
    }


# ---------------------------------------------------------------------------
# TN3a — VÉT CẠN TRÊN THỂ HIỆN NHỎ
# ---------------------------------------------------------------------------

def tn3a_the_hien_nho(so_the_hien, in_ra=True):
    """Vét cạn: mọi em, mọi cách khai, không cắt xén không gian tìm kiếm.

    Đây là phần cho kết luận MẠNH NHẤT — không có chỗ nào cho việc "có thể
    bộ đo bỏ sót cách khai gian nào đó", vì nó thử hết.
    """
    ket = {}
    for nhan_cc, fn in CO_CHE_THU:
        rng = random.Random(HAT_SINH)
        tong_em = tong_gian = 0
        cac_muc_loi = []
        vi_du = None
        the_hien_co_gian = 0
        for _ in range(so_the_hien):
            th = sinh_the_hien_nho(rng, co_du_tru=True)
            students, clubs, scores, app, prefs = th
            stb = loi.generate_stb_lottery(sorted(students), rng.randint(1, 10 ** 6))
            elig = loi.default_reserve_eligible_fn(students, clubs)
            r = do_mot_the_hien(th, stb, elig, fn, sorted(students), rng=rng)
            tong_em += r["so_em_thu"]
            tong_gian += r["so_em_khai_gian_duoc"]
            the_hien_co_gian += int(r["so_em_khai_gian_duoc"] > 0)
            if r["so_em_khai_gian_duoc"]:
                cac_muc_loi.append(r["muc_loi_tb"])
                if vi_du is None:
                    vi_du = r["vi_du"]
        ket[nhan_cc] = {
            "so_the_hien": so_the_hien,
            "so_the_hien_co_em_khai_gian_duoc": the_hien_co_gian,
            "tong_em_thu": tong_em,
            "tong_em_khai_gian_duoc": tong_gian,
            "ti_le_phan_tram": round(100 * tong_gian / tong_em, 2) if tong_em else 0.0,
            "muc_loi_tb": round(statistics.mean(cac_muc_loi), 2) if cac_muc_loi else 0.0,
            "vi_du": vi_du,
        }

    if in_ra:
        print("\n" + "=" * 78)
        print("TN3a — VÉT CẠN KHÔNG GIAN KHAI GIAN (%d thể hiện nhỏ, 7 em / 4 CLB)"
              % so_the_hien)
        print("=" * 78)
        print("Mỗi em: thử MỌI hoán vị và MỌI cách cắt ngắn danh sách nguyện vọng.\n")
        print("%-22s %10s %14s %12s %10s"
              % ("Cơ chế", "Em đã thử", "Khai gian được", "Tỉ lệ", "Lợi TB"))
        print("-" * 78)
        for nhan_cc, _ in CO_CHE_THU:
            t = ket[nhan_cc]
            print("%-22s %10d %14d %11.2f%% %10.2f"
                  % (nhan_cc, t["tong_em_thu"], t["tong_em_khai_gian_duoc"],
                     t["ti_le_phan_tram"], t["muc_loi_tb"]))
        print("\nĐỐI CHỨNG NGƯỢC: Boston PHẢI ra khác 0. Nếu Boston cũng bằng 0 thì")
        print("bộ dò hỏng, và mọi số trong bảng này vô nghĩa.")
        vd = ket["Boston / nhận ngay"]["vi_du"]
        if vd:
            print("\nMột ví dụ khai gian có lợi dưới Boston:")
            print("  em %s khai thật %s -> được nguyện vọng thứ %d"
                  % (vd["student_id"], vd["nguyen_vong_that"], vd["hang_khi_khai_that"]))
            print("  cùng em đó khai %s   -> được nguyện vọng thứ %d"
                  % (vd["khai_gian"], vd["hang_khi_khai_gian"]))
    return ket


# ---------------------------------------------------------------------------
# TN3b — TRÊN BỘ DỮ LIỆU THẬT (lấy mẫu học sinh, chặn không gian tìm kiếm)
# ---------------------------------------------------------------------------

def tn3b_bo_du_lieu_that(so_em_mau, tran, in_ra=True):
    ket = {}
    for ten, du_lieu in nap_ba_bo():
        students, clubs, scores, app, prefs = du_lieu
        _xep, stb, elig, _ = chay_rbda(du_lieu, SEED_MOC)
        rng = random.Random(HAT_SINH)
        ds = sorted(students)
        mau = ds if len(ds) <= so_em_mau else rng.sample(ds, so_em_mau)
        mau = sorted(mau)

        bo = {}
        for nhan_cc, fn in CO_CHE_THU:
            t0 = time.time()
            r = do_mot_the_hien(du_lieu, stb, elig, fn, mau, tran=tran, rng=random.Random(1))
            r["giay"] = round(time.time() - t0, 1)
            bo[nhan_cc] = r
        ket[ten] = bo

    if in_ra:
        print("\n" + "=" * 78)
        print("TN3b — TRÊN BA BỘ DỮ LIỆU THẬT (mẫu %d em, tối đa %d cách khai/em)"
              % (so_em_mau, tran))
        print("=" * 78)
        for ten, bo in ket.items():
            print("\n### %s" % ten)
            print("%-22s %10s %16s %10s %8s"
                  % ("Cơ chế", "Em đã thử", "Khai gian được", "Lợi TB", "Giây"))
            print("-" * 78)
            for nhan_cc, _ in CO_CHE_THU:
                t = bo[nhan_cc]
                print("%-22s %10d %16d %10.2f %8.1f"
                      % (nhan_cc, t["so_em_thu"], t["so_em_khai_gian_duoc"],
                         t["muc_loi_tb"], t["giay"]))
        print("\nLƯU Ý VỀ PHẠM VI: bảng này CHẶN không gian tìm kiếm (danh sách 6")
        print("nguyện vọng có 4320 cách khai). 'Không tìm thấy' ở đây yếu hơn")
        print("'không tồn tại' — phần kết luận mạnh nằm ở TN3a, nơi vét cạn.")
    return ket


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Đo khả năng khai gian nguyện vọng")
    ap.add_argument("--so-the-hien", type=int, default=SO_THE_HIEN_MAC_DINH)
    ap.add_argument("--so-em-mau", type=int, default=SO_EM_MAU_MAC_DINH)
    ap.add_argument("--tran-khai", type=int, default=SO_KHAI_TOI_DA)
    ap.add_argument("--json", default=DUONG_JSON)
    args = ap.parse_args()

    t0 = time.time()
    so_lieu = {
        "_ghi_chu": "Sinh bởi du_lieu_test/do_khai_that.py — KHÔNG sửa tay.",
        "so_the_hien": args.so_the_hien,
        "so_em_mau": args.so_em_mau,
        "tran_khai": args.tran_khai,
        "tn3a_vet_can": tn3a_the_hien_nho(args.so_the_hien),
        "tn3b_bo_that": tn3b_bo_du_lieu_that(args.so_em_mau, args.tran_khai),
    }
    so_lieu["giay_chay"] = round(time.time() - t0, 2)
    with open(args.json, "w", encoding="utf-8") as f:
        json.dump(so_lieu, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("\nĐã ghi số liệu thô: %s  (%.1fs)" % (args.json, so_lieu["giay_chay"]))


if __name__ == "__main__":
    main()
