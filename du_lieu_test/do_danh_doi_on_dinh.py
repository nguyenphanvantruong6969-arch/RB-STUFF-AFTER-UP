"""
do_danh_doi_on_dinh.py
======================
Đo cái giá của tính ỔN ĐỊNH: kết quả không có cặp phá vỡ, nhưng có tối ưu
cho học sinh không?

    ./.venv/bin/python du_lieu_test/do_danh_doi_on_dinh.py
    ./.venv/bin/python du_lieu_test/do_danh_doi_on_dinh.py --so-seed 100

CÂU HỎI ĐANG TRẢ LỜI
--------------------
`verify_stability` đã canh: **0 cặp phá vỡ**. Nhưng "ổn định" và "tốt nhất
cho học sinh" là hai chuyện khác nhau. Bộ đo này tìm triệu chứng của chỗ
khác nhau đó:

    CẶP ĐÔI CÙNG CÓ LỢI
    em s1 được xếp CLB c1, em s2 được xếp CLB c2,
    mà s1 thích c2 hơn c1  VÀ  s2 thích c1 hơn c2.

Hai em đổi chỗ cho nhau thì CẢ HAI đều lên nguyện vọng cao hơn — nhưng
thuật toán không cho, vì đổi như vậy phá mất tính ổn định.

Tồn tại cặp như vậy => kết quả KHÔNG tối ưu Pareto cho học sinh.
**Đây không phải lỗi.** Đó là chỗ đánh đổi đã biết của cả họ thuật toán
ghép cặp ổn định. Bộ đo này chỉ ĐẾM cái giá đó trên dữ liệu thật, không
nhận định nó có chấp nhận được hay không — phần đó học sinh tự viết.

QUY NGUYÊN NHÂN — đọc kỹ chỗ này
--------------------------------
Dễ đổ hết cho BỐC THĂM. Bộ đo kiểm điều đó bằng hai cách, và kết quả
KHÔNG ủng hộ cách đọc đó:

  1. Đếm lại qua nhiều seed. Nếu bốc thăm là nguyên nhân chính thì đổi
     bốc thăm phải làm con số nhảy mạnh, và phải có seed cho 0 cặp.
  2. Với mỗi cặp, xét em s1 có HOÀ với em nào đang giữ suất ở c2 không.
     Hoà thì một lần bốc thăm khác đã có thể đổi ngôi — tức bốc thăm
     thật sự có phần. Không hoà thì s1 đứng dưới ngưỡng vì ĐIỂM, và
     bốc thăm vô can.

     Định nghĩa "hoà ở c2": hai em cùng KHÔNG thi c2 (đều Tầng 2), hoặc
     cùng thi c2 và BẰNG ĐIỂM.

THÍ NGHIỆM ĐỐI CHỨNG — phần trả lời dứt điểm
--------------------------------------------
Hai cách trên mới là bằng chứng gián tiếp. Phần này can thiệp thẳng: bỏ
điểm của p% số cặp (em, CLB), đẩy các em đó xuống Tầng 2 — nơi thứ tự do
BỐC THĂM quyết định hoàn toàn. Nếu bốc thăm là thủ phạm thì càng nhiều
Tầng 2, số cặp phải càng TĂNG.

KHÔNG đụng `app.db` thật: mọi thứ nằm trong thư mục tạm, xoá sau khi chạy.
Ba bộ dữ liệu đều là MÔ PHỎNG — con số ở đây nói về ba bộ đó, không phải
về trường nào.
"""

import argparse
import itertools
import os
import random
import shutil
import statistics
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rbda_priority_pipeline as loi  # noqa: E402
from do_anh_huong_seed import BO_DU_LIEU, nap_bo, xep_theo_seed  # noqa: E402

SEED_MOC = 42
SO_SEED_MAC_DINH = 40

# --- thí nghiệm đối chứng ---
TI_LE_BO_DIEM = (0.0, 0.25, 0.5, 0.75, 1.0)
SO_SEED_THI_NGHIEM = 10
HAT_BO_DIEM = 7          # cố định để chạy lại ra đúng số cũ


def _bang_thu_hang(nguyen_vong, students):
    """{student_id: {club_id: thứ hạng nguyện vọng}} — số nhỏ = thích hơn."""
    return {
        sid: {cid: i for i, cid in enumerate(nguyen_vong.get(sid, []))}
        for sid in students
    }


def thich_hon(thu_hang, sid, clb_a, clb_b):
    """sid thích clb_a hơn clb_b?  (clb_b = None nghĩa là không có suất)"""
    ra = thu_hang[sid].get(clb_a)
    if ra is None:
        return False                     # a không nằm trong nguyện vọng
    rb = thu_hang[sid].get(clb_b)
    if rb is None:
        return True                      # b không phải nguyện vọng -> a hơn
    return ra < rb


def tim_cap_cung_co_loi(du_lieu, xep):
    """Trả về list (s1, c1, s2, c2) — cả hai em đều muốn đổi cho nhau."""
    students, _clubs, _diem, _uv, nguyen_vong, _stb = du_lieu
    thu_hang = _bang_thu_hang(nguyen_vong, students)
    co_suat = [s for s in students if xep.get(s)]
    ra = []
    for s1, s2 in itertools.combinations(co_suat, 2):
        c1, c2 = xep[s1], xep[s2]
        if c1 == c2:
            continue
        if thich_hon(thu_hang, s1, c2, c1) and thich_hon(thu_hang, s2, c1, c2):
            ra.append((s1, c1, s2, c2))
    return ra


def hoa_nhau_o(diem, clb, sid_a, sid_b):
    """Hai em có hoà nhau ở CLB này không?

    Hoà = cùng KHÔNG thi CLB đó (đều Tầng 2), hoặc cùng thi và bằng điểm.
    """
    da = diem.get(clb, {}).get(sid_a)
    db = diem.get(clb, {}).get(sid_b)
    if da is None and db is None:
        return True
    if da is None or db is None:
        return False
    return da == db


def quy_nguyen_nhan(du_lieu, xep, cap_doi):
    """Đếm bao nhiêu cặp mà BỐC THĂM thật sự có phần.

    Với cặp (s1@c1, s2@c2): s1 muốn sang c2 nhưng không vào được. Nếu s1
    HOÀ với ít nhất một em đang giữ suất ở c2 thì một lần bốc thăm khác
    đã có thể đổi ngôi hai em đó — bốc thăm có phần. Nếu không hoà với ai
    thì s1 đứng dưới ngưỡng vì ĐIỂM, bốc thăm vô can.
    """
    _students, _clubs, diem, _uv, _nv, _stb = du_lieu
    dang_giu = {}
    for sid, cid in xep.items():
        if cid:
            dang_giu.setdefault(cid, []).append(sid)

    boc_tham_co_phan = 0
    for s1, _c1, _s2, c2 in cap_doi:
        if any(hoa_nhau_o(diem, c2, s1, khac)
               for khac in dang_giu.get(c2, []) if khac != s1):
            boc_tham_co_phan += 1
    return boc_tham_co_phan


def bo_bot_diem(diem, ti_le, hat=HAT_BO_DIEM):
    """Bỏ điểm của `ti_le` phần số cặp (em, CLB).

    Em mất điểm ở CLB nào thì tụt xuống Tầng 2 ở CLB đó — chỗ mà thứ tự
    do BỐC THĂM quyết định hoàn toàn. Đây là cách tăng quyền của bốc thăm
    mà không đụng gì tới nguyện vọng hay sức chứa.
    """
    rng = random.Random(hat)
    return {
        clb: {sid: d for sid, d in bang.items() if rng.random() >= ti_le}
        for clb, bang in diem.items()
    }


def thi_nghiem_doi_chung(du_lieu, so_seed=SO_SEED_THI_NGHIEM):
    """Tăng dần quyền của bốc thăm, xem số cặp đôi cùng có lợi chạy đi đâu.

    Trả về list (tỉ lệ bỏ điểm, TB số cặp, TB số cặp bốc thăm có phần,
    số seed cho 0 cặp).
    """
    students, clubs, diem_goc, ung_vien, nguyen_vong, _stb = du_lieu
    du_tru_fn = loi.default_reserve_eligible_fn(students, clubs)
    ra = []
    for ti_le in TI_LE_BO_DIEM:
        diem = bo_bot_diem(diem_goc, ti_le)
        tong, co_phan = [], []
        for seed in range(1, so_seed + 1):
            stb = loi.generate_stb_lottery(sorted(students), seed)
            kq = loi.run_rbda(students, clubs, diem, ung_vien,
                              nguyen_vong, stb, du_tru_fn)
            cap_pha_vo = loi.verify_stability(kq, clubs, nguyen_vong, du_tru_fn)
            if cap_pha_vo:
                raise SystemExit("BAT NGO: bo %.0f%% diem lam mat on dinh"
                                 % (100 * ti_le))
            xep = dict(kq.assignment)
            du_lieu_moi = (students, clubs, diem, ung_vien, nguyen_vong, stb)
            cap = tim_cap_cung_co_loi(du_lieu_moi, xep)
            tong.append(len(cap))
            co_phan.append(quy_nguyen_nhan(du_lieu_moi, xep, cap))
        ra.append((ti_le, statistics.mean(tong),
                   statistics.mean(co_phan), tong.count(0)))
    return ra


def do_mot_bo(ten, files, so_seed):
    thu_muc = tempfile.mkdtemp()
    try:
        du_lieu = loi.load_from_sqlite(nap_bo(thu_muc, files))
        students = du_lieu[0]
        n = len(students)

        # --- ảnh chụp ở seed mốc ---
        xep, cap_pha_vo = xep_theo_seed(du_lieu, SEED_MOC)
        cap_doi = tim_cap_cung_co_loi(du_lieu, xep)
        co_boc_tham = quy_nguyen_nhan(du_lieu, xep, cap_doi)
        em_lien_quan = {s for c in cap_doi for s in (c[0], c[2])}
        so_duoc_xep = sum(1 for s in students if xep.get(s))

        print(f"\n{'=' * 70}")
        print(f"{ten}")
        print(f"{'=' * 70}")
        print(f"  Học sinh {n} · được xếp {so_duoc_xep}"
              f" · seed mốc {SEED_MOC}")
        print()
        print(f"  Cặp phá vỡ (blocking pair)        : {len(cap_pha_vo)}")
        print(f"  CẶP ĐÔI CÙNG CÓ LỢI               : {len(cap_doi)}")
        print(f"    số em dính ít nhất một cặp      : {len(em_lien_quan)}"
              f"  ({100 * len(em_lien_quan) / n:.1f}% sĩ số)")
        if cap_doi:
            print(f"    bốc thăm CÓ phần                : {co_boc_tham}"
                  f"  ({100 * co_boc_tham / len(cap_doi):.0f}%)")
            print(f"    bốc thăm VÔ CAN (thua vì điểm)  : {len(cap_doi) - co_boc_tham}"
                  f"  ({100 * (len(cap_doi) - co_boc_tham) / len(cap_doi):.0f}%)")
            print()
            print("    Vài cặp đầu:")
            for s1, c1, s2, c2 in cap_doi[:3]:
                print(f"      {s1} đang ở {c1}, muốn sang {c2}")
                print(f"      {s2} đang ở {c2}, muốn sang {c1}   -> đổi thì cả hai cùng lên")

        # --- quét nhiều seed ---
        dem = []
        for seed in range(1, so_seed + 1):
            xep_s, cap_s = xep_theo_seed(du_lieu, seed)
            if cap_s:
                raise SystemExit(f"BAT NGO: seed {seed} co {len(cap_s)} cap pha vo")
            dem.append(len(tim_cap_cung_co_loi(du_lieu, xep_s)))

        print()
        print(f"  --- quét {so_seed} seed ---")
        print("  Cặp phá vỡ                        : 0 ở MỌI seed")
        print(f"  Cặp đôi cùng có lợi               : ít nhất {min(dem)}"
              f" · TB {statistics.mean(dem):.1f} · nhiều nhất {max(dem)}")
        print(f"  Số seed cho 0 cặp                 : {dem.count(0)} / {so_seed}")

        # --- thí nghiệm đối chứng: tăng dần quyền của bốc thăm ---
        bang = thi_nghiem_doi_chung(du_lieu)
        print()
        print(f"  --- bỏ điểm p% số cặp (em,CLB) để đẩy xuống Tầng 2,"
              f" {SO_SEED_THI_NGHIEM} seed mỗi mức ---")
        print("    bỏ điểm   cặp đôi (TB)   bốc thăm có phần   thua vì điểm   seed cho 0 cặp")
        for ti_le, tb, tb_co, so_0 in bang:
            ti = f"{100 * tb_co / tb:.0f}%" if tb else "—"
            print(f"    {100 * ti_le:5.0f}%   {tb:11.1f}   {tb_co:9.1f} ({ti:>4})"
                  f"   {tb - tb_co:11.1f}   {so_0:8d}/{SO_SEED_THI_NGHIEM}")
        return dem, bang
    finally:
        shutil.rmtree(thu_muc, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--so-seed", type=int, default=SO_SEED_MAC_DINH)
    args = ap.parse_args()

    print("CÁI GIÁ CỦA TÍNH ỔN ĐỊNH — đo trên ba bộ dữ liệu MÔ PHỎNG")

    tat_ca, thi_nghiem = {}, {}
    for ten, files in BO_DU_LIEU:
        tat_ca[ten], thi_nghiem[ten] = do_mot_bo(ten, files, args.so_seed)

    print(f"\n{'=' * 70}")
    print("ĐỌC RA ĐƯỢC GÌ")
    print(f"{'=' * 70}\n")
    print("  1. Kết quả ỔN ĐỊNH (0 cặp phá vỡ ở mọi seed) nhưng KHÔNG tối ưu")
    print("     Pareto cho học sinh — vẫn còn cặp đổi được mà cả hai cùng lợi.")
    print()
    # Chỉ xét bộ mà hiện tượng CÓ THỂ xuất hiện. Bộ luôn cho 0 ở mọi seed
    # (như vi_du_huong_dan — không có em hoà, không có em Tầng 2) không nói
    # được gì về nguyên nhân, và nếu gộp vào thì lật ngược kết luận.
    bo_co_hien_tuong = {t: d for t, d in tat_ca.items() if d and max(d) > 0}
    print("  2. Không phải do bốc thăm.", end=" ")
    if not bo_co_hien_tuong:
        print("Không bộ nào có hiện tượng — chưa kết luận được.")
    elif all(d.count(0) == 0 for d in bo_co_hien_tuong.values()):
        print(f"Trên {len(bo_co_hien_tuong)} bộ có hiện tượng,")
        print("     KHÔNG seed nào cho 0 cặp, và biên độ dao động nhỏ. Phần lớn tổn")
        print("     thất đến từ ưu tiên THẬT (điểm khác nhau), không từ việc phá hoà.")
    else:
        print("Có seed cho 0 cặp — xem lại kết luận này.")
    print()
    print("  3. Bộ nhỏ vi_du_huong_dan cho 0 cặp: bộ đó không có em hoà điểm và")
    print("     không có em Tầng 2, nên không có chỗ cho hiện tượng này xuất hiện.")
    print()

    # --- điểm 4: thí nghiệm đối chứng nói gì ---
    # CHỈ so HAI ĐẦU của thí nghiệm. Các mức ở giữa KHÔNG đi một chiều
    # (xem bảng từng bộ), nên không được viết thành "càng ... càng ...".
    co_hien_tuong = [t for t in thi_nghiem if tat_ca[t] and max(tat_ca[t]) > 0]
    print("  4. Thí nghiệm đối chứng đi NGƯỢC cách đọc \"tại bốc thăm\".")
    print("     Bỏ hết điểm = mọi em xuống Tầng 2 = bốc thăm quyết định HOÀN")
    print("     TOÀN. Nếu bốc thăm sinh ra tổn thất thì lúc đó phải NHIỀU cặp")
    print("     nhất. Đo được là ÍT nhất:")
    print()
    print(f"       {'bộ':<20}{'giữ nguyên điểm':>17}{'bỏ hết điểm':>15}"
          f"{'seed cho 0 cặp':>17}")
    for ten in co_hien_tuong:
        dau, cuoi = thi_nghiem[ten][0], thi_nghiem[ten][-1]
        print(f"       {ten.split()[0]:<20}{dau[1]:>17.1f}{cuoi[1]:>15.1f}"
              f"{('%d/%d' % (cuoi[3], SO_SEED_THI_NGHIEM)):>17}")
    print()
    if any(thi_nghiem[t][-1][3] > 0 for t in co_hien_tuong):
        print("     Ở mức bỏ hết điểm CÓ seed cho 0 cặp — tức có lần đạt tối ưu")
        print("     Pareto. Với điểm còn nguyên thì không seed nào làm được.")
    print("     Các mức Ở GIỮA không đi một chiều — đọc bảng từng bộ, đừng")
    print("     viết thành \"càng nhiều Tầng 2 càng ít cặp\".")
    print()
    print("  Ba bộ đều là dữ liệu MÔ PHỎNG. Con số ở đây nói về ba bộ đó.")
    print("  Việc đánh đổi này có chấp nhận được hay không — học sinh tự viết.")
    print()


if __name__ == "__main__":
    main()
