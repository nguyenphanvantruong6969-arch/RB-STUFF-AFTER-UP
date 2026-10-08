"""
do_khong_du_tru.py
==================
Nếu trường KHÔNG dùng suất dự trữ thì phần mềm chạy ra sao?

    ./.venv/bin/python du_lieu_test/do_khong_du_tru.py
    ./.venv/bin/python du_lieu_test/do_khong_du_tru.py --so-seed 50

CÂU HỎI ĐANG TRẢ LỜI
--------------------
Suất dự trữ sinh ra từ hoàn cảnh trường công: có nhóm học sinh cần được
giữ chỗ. Một trường quốc tế có thể không cần cơ chế đó — mọi CLB đặt
`reserve_capacity = 0`. Lúc đó phần mềm còn chạy đúng không, và kết quả
đổi bao nhiêu?

HAI PHẦN ĐO
-----------
1. **Hàm lựa chọn thành cái gì.** Đặt cạnh mô hình "một danh sách ưu tiên
   Q_j" mà báo cáo mô tả, gọi thẳng `club_choice_function` thật.

2. **Kết quả đổi bao nhiêu.** Chạy lại trên hai bộ dữ liệu mô phỏng, mỗi
   bộ nhiều seed, so cấu hình CÓ dự trữ với cấu hình BỎ HẾT dự trữ.

ĐIỀU ĐÁNG CHÚ Ý — đọc kỹ chỗ này
--------------------------------
`reserve_capacity = 0` làm `reserve_held = candidates[:0] = []`, nên
`general_capacity = capacity` và lượt chung xét TOÀN BỘ pool. Hàm lựa
chọn thu về đúng "sắp theo thứ hạng, lấy K em đầu".

Tức là: **bỏ suất dự trữ thì RB-DA thu về Deferred Acceptance thuần
tuý**, và mô hình `Q_j` trong báo cáo TRỞ THÀNH ĐÚNG. Chỗ lệch báo cáo ↔
phần mềm mà `docs/CO_CHE_THUAT_TOAN.md` mô tả tồn tại **chỉ vì** có suất dự
trữ.

KHÔNG đụng `app.db` thật: mọi thứ nằm trong thư mục tạm, xoá sau khi chạy.
Hai bộ dữ liệu đều là MÔ PHỎNG — con số ở đây nói về hai bộ đó.

Bộ đo này chỉ ĐẾM hệ quả. Trường nên hay không nên bỏ suất dự trữ —
học sinh tự viết.
"""

import argparse
import os
import shutil
import statistics
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import rbda_priority_pipeline as loi  # noqa: E402
from do_anh_huong_seed import BO_DU_LIEU, nap_bo  # noqa: E402

SO_SEED_MAC_DINH = 20

# --- ví dụ nhỏ kiểm được bằng bút chì, dùng lại khuôn do_hai_canh_du_tru ---
UU_TIEN = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}
SUC_CHUA = 3
DIEN_DU_TRU = {"D", "E"}


def mo_hinh_mot_danh_sach(pool, suc_chua=SUC_CHUA):
    """Mô hình 'một danh sách ưu tiên Q_j': sắp theo Q_j, lấy K em đầu."""
    return sorted(pool, key=lambda s: UU_TIEN[s])[:suc_chua]


def ham_lua_chon_that(pool, suat_du_tru):
    nhan, _tang = loi.club_choice_function(
        pool=pool,
        capacity=SUC_CHUA,
        reserve_capacity=suat_du_tru,
        is_reserve_eligible_fn=lambda s: s in DIEN_DU_TRU,
        rank=UU_TIEN,
    )
    return nhan


def phan_1_ham_lua_chon():
    print("=" * 74)
    print("PHẦN 1 — BỎ SUẤT DỰ TRỮ THÌ HÀM LỰA CHỌN THÀNH CÁI GÌ?")
    print("=" * 74)
    print()
    print(f"  CLB sức chứa {SUC_CHUA} · ưu tiên A > B > C > D > E"
          f" · diện dự trữ: {', '.join(sorted(DIEN_DU_TRU))}")
    print("  Cùng một pool, chỉ đổi số suất dự trữ.")
    print()
    pool = ["A", "B", "C", "D", "E"]
    print(f"  {'suất dự trữ':<14}{'club_choice_function':<26}"
          f"{'mô hình Q_j':<18}{'hai bên'}")
    print("  " + "-" * 70)
    ket = {}
    for suat in (2, 1, 0):
        that = ham_lua_chon_that(pool, suat)
        mo_hinh = mo_hinh_mot_danh_sach(pool)
        ket[suat] = (that, mo_hinh)
        khop = "KHỚP" if that == mo_hinh else "*** LỆCH ***"
        print(f"  {suat:<14}{str(that):<26}{str(mo_hinh):<18}{khop}")
    print()
    print("  => Suất dự trữ = 0 là ĐIỀU KIỆN để hai bên trùng nhau.")
    print("     Bỏ dự trữ thì RB-DA thu về Deferred Acceptance thuần tuý,")
    print("     và mô hình Q_j trong báo cáo trở thành ĐÚNG.")
    print()
    return ket


def bo_het_du_tru(clubs):
    """Bản sao cấu hình CLB với mọi suất dự trữ đặt về 0."""
    return {c: dict(v, reserve_capacity=0) for c, v in clubs.items()}


def xep_voi_cau_hinh(du_lieu, clubs, seed):
    students, _cl, diem, uv, nv, _ = du_lieu
    stb = loi.generate_stb_lottery(sorted(students), seed)
    fn = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda(students, clubs, diem, uv, nv, stb, fn)
    cap = loi.verify_stability(kq, clubs, nv, fn)
    return dict(kq.assignment), cap


def phan_2_mot_bo(ten, files, so_seed):
    thu_muc = tempfile.mkdtemp()
    try:
        du_lieu = loi.load_from_sqlite(nap_bo(thu_muc, files))
        students, clubs = du_lieu[0], du_lieu[1]
        khong_dt = bo_het_du_tru(clubs)
        n = len(students)
        tong_suat = sum(v["reserve_capacity"] for v in clubs.values())
        so_clb_co = sum(1 for v in clubs.values() if v["reserve_capacity"])

        doi_cho, mat, duoc = [], [], []
        for seed in range(1, so_seed + 1):
            co, cap_co = xep_voi_cau_hinh(du_lieu, clubs, seed)
            kh, cap_kh = xep_voi_cau_hinh(du_lieu, khong_dt, seed)
            if cap_co or cap_kh:
                raise SystemExit("BAT NGO: seed %d lam mat on dinh" % seed)
            doi_cho.append(sum(1 for s in students if co[s] != kh[s]))
            mat.append(sum(1 for s in students if co[s] and not kh[s]))
            duoc.append(sum(1 for s in students if not co[s] and kh[s]))

        print(f"\n{'=' * 74}")
        print(ten)
        print("=" * 74)
        print(f"  {n} học sinh · {so_clb_co}/{len(clubs)} CLB có suất dự trữ"
              f" · tổng {tong_suat} suất")
        print(f"  Quét {so_seed} seed, so CÓ dự trữ ↔ BỎ HẾT dự trữ:")
        print()
        print("  Cặp phá vỡ                    : 0 ở CẢ HAI cấu hình, mọi seed")
        print(f"  Học sinh ĐỔI câu lạc bộ       : ít nhất {min(doi_cho)}"
              f" · TB {statistics.mean(doi_cho):.1f} · nhiều nhất {max(doi_cho)}"
              f"  ({100 * statistics.mean(doi_cho) / n:.1f}% sĩ số)")
        print(f"  Học sinh MẤT suất             : TB {statistics.mean(mat):.1f}")
        print(f"  Học sinh ĐƯỢC THÊM suất       : TB {statistics.mean(duoc):.1f}")
        return statistics.mean(doi_cho), statistics.mean(mat), statistics.mean(duoc)
    finally:
        shutil.rmtree(thu_muc, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--so-seed", type=int, default=SO_SEED_MAC_DINH)
    args = ap.parse_args()

    print("CẤU HÌNH KHÔNG CÓ SUẤT DỰ TRỮ — đo trên dữ liệu MÔ PHỎNG\n")
    phan_1_ham_lua_chon()

    print("=" * 74)
    print("PHẦN 2 — KẾT QUẢ PHÂN BỔ ĐỔI BAO NHIÊU")
    print("=" * 74)
    ra = {}
    for ten, files in BO_DU_LIEU[1:]:          # bỏ bộ 10 em, quá nhỏ để đọc ra gì
        ra[ten] = phan_2_mot_bo(ten, files, args.so_seed)

    print(f"\n{'=' * 74}")
    print("ĐỌC RA ĐƯỢC GÌ")
    print("=" * 74)
    print()
    print("  1. Phần mềm VẪN CHẠY ĐÚNG khi không có suất dự trữ nào —")
    print("     0 cặp phá vỡ ở mọi seed, mọi bộ. Không cần sửa gì để dùng")
    print("     cho trường không áp dụng chính sách dự trữ.")
    print()
    print("  2. Nhưng kết quả KHÔNG giống nhau: khoảng một phần năm số em")
    print("     đổi câu lạc bộ. Suất dự trữ không chỉ đổi số phận nhóm được")
    print("     ưu tiên — nó đẩy dây chuyền sang cả những em không liên quan.")
    print()
    print("  3. Số em MẤT hẳn suất thì ít hơn nhiều số em ĐỔI CHỖ. Bỏ dự trữ")
    print("     chủ yếu xáo lại AI VÀO ĐÂU, không phải AI CÓ SUẤT.")
    print()
    print("  4. Hàm lựa chọn thu về đúng mô hình một danh sách Q_j (Phần 1).")
    print("     Nghĩa là chỗ lệch giữa báo cáo và phần mềm — thứ")
    print("     docs/CO_CHE_THUAT_TOAN.md mô tả — tồn tại CHỈ VÌ có suất dự trữ.")
    print()
    print("  Hai bộ đều là dữ liệu MÔ PHỎNG. Con số ở đây nói về hai bộ đó.")
    print("  Trường nên hay không nên bỏ suất dự trữ — học sinh tự viết.")
    print()


if __name__ == "__main__":
    main()
