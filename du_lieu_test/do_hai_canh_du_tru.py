"""
do_hai_canh_du_tru.py
=====================
Đo một câu hỏi duy nhất:

    Hàm lựa chọn của câu lạc bộ có phải là MỘT danh sách ưu tiên cố định không?

Trả lời: KHÔNG. Và đây là bộ đo chứng minh điều đó, gọi thẳng hàm thật
`club_choice_function` trong rbda_priority_pipeline.py — không mô phỏng lại,
không chép số.

VÌ SAO CẦN BỘ ĐO NÀY
--------------------
Mô hình toán thường viết: mỗi CLB c_j có MỘT danh sách ưu tiên Q_j và một
sức chứa K_j; CLB giữ K_j em đứng đầu Q_j trong số em đang nộp.

Phần mềm này KHÔNG làm vậy. Nó chạy hai lượt — lượt dự trữ trước, lượt chung
sau — và việc phân nhóm dự trữ/chung phải tính LẠI ở mỗi vòng, theo đúng tập
em đang có mặt lúc đó.

Hệ quả đo được: cùng một em, cùng thứ hạng ưu tiên, cùng CLB, cùng sức chứa
— lúc có suất lúc không, tuỳ vào AI KHÁC đang nộp cùng lúc.

CHẠY
----
    python du_lieu_test/do_hai_canh_du_tru.py

Có test canh bảng này: tests/test_hai_canh_du_tru.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rbda_priority_pipeline import club_choice_function  # noqa: E402


# --- Cấu hình ví dụ -------------------------------------------------------
# Cố ý giữ nhỏ để kiểm được bằng bút chì. Không dùng dữ liệu học sinh nào.

SUC_CHUA = 3
SUAT_DU_TRU = 1

# Thứ hạng ưu tiên NỀN — số nhỏ hơn = ưu tiên cao hơn.
# GIỮ NGUYÊN Ở CẢ HAI CẢNH: đây là điểm mấu chốt, thứ hạng không đổi mà
# kết quả vẫn đổi.
UU_TIEN = {"A": 0, "B": 1, "C": 2, "D": 3}

# D thuộc diện dự trữ. Trong phần mềm thật, "diện dự trữ" nghĩa là
# students[sid]['reserve_group'] trùng clubs[cid]['reserve_group']
# (xem default_reserve_eligible_fn).
DIEN_DU_TRU = {"D"}

CANH = [
    ("Cảnh 1", ["A", "B", "C", "D"], "D có mặt — đang nộp vào CLB này"),
    ("Cảnh 2", ["A", "B", "C"], "D vắng mặt — đã được giữ ở CLB khác"),
]


def mo_hinh_mot_danh_sach(pool: list[str]) -> list[str]:
    """Mô hình 'một danh sách ưu tiên Q_j': sắp theo Q_j, lấy K em đầu.

    KHÔNG phải cái phần mềm chạy. Ở đây để đặt cạnh cho thấy chỗ lệch.
    """
    return sorted(pool, key=lambda s: UU_TIEN[s])[:SUC_CHUA]


def ham_lua_chon_that(pool: list[str]) -> list[str]:
    """Gọi thẳng hàm thật trong rbda_priority_pipeline.py."""
    nhan, _tang = club_choice_function(
        pool=pool,
        capacity=SUC_CHUA,
        reserve_capacity=SUAT_DU_TRU,
        is_reserve_eligible_fn=lambda s: s in DIEN_DU_TRU,
        rank=UU_TIEN,
    )
    return nhan


def main() -> None:
    print("=" * 74)
    print("HÀM LỰA CHỌN CỦA CLB CÓ PHẢI MỘT DANH SÁCH ƯU TIÊN CỐ ĐỊNH KHÔNG?")
    print("=" * 74)
    print()
    print(f"  Câu lạc bộ:   sức chứa {SUC_CHUA}, trong đó {SUAT_DU_TRU} suất dự trữ")
    print("  Ưu tiên nền:  " + " > ".join(
        f"{s}({r + 1})" for s, r in sorted(UU_TIEN.items(), key=lambda kv: kv[1])
    ))
    print(f"  Diện dự trữ:  {', '.join(sorted(DIEN_DU_TRU))}")
    print()
    print("  Ưu tiên nền GIỮ NGUYÊN ở cả hai cảnh. Chỉ đổi: ai đang có mặt.")
    print()

    ket_qua = {}
    for ten, pool, ghi_chu in CANH:
        that = ham_lua_chon_that(pool)
        mot_ds = mo_hinh_mot_danh_sach(pool)
        ket_qua[ten] = (that, mot_ds)

        print("-" * 74)
        print(f"{ten} — {ghi_chu}")
        print(f"  Đang nộp:                       {pool}")
        print(f"  Mô hình 'một danh sách Q_j' ->  {mot_ds}")
        print(f"  club_choice_function()      ->  {that}")
        khop = "KHỚP" if that == mot_ds else "*** LỆCH ***"
        print(f"  Hai bên:                        {khop}")
        print(f"  Em C có suất?                   "
              f"{'CÓ' if 'C' in that else 'KHÔNG'} (theo phần mềm)  ·  "
              f"{'CÓ' if 'C' in mot_ds else 'KHÔNG'} (theo mô hình một danh sách)")
        print()

    # --- Kết luận rút ra từ chính số đo trên -----------------------------
    c1_that, c1_ds = ket_qua["Cảnh 1"]
    c2_that, _c2_ds = ket_qua["Cảnh 2"]

    print("=" * 74)
    print("ĐỌC RA ĐƯỢC GÌ")
    print("=" * 74)
    print()
    print(f"  1. Cảnh 1: C xếp TRÊN D (hạng {UU_TIEN['C'] + 1} so với {UU_TIEN['D'] + 1}),")
    print(f"     CLB lấy {SUC_CHUA} em — mà D đỗ còn C trượt.")
    print(f"     Mô hình một danh sách cho {c1_ds}; phần mềm cho {c1_that}.")
    print()
    print("  2. So hai cảnh: CÙNG em C, CÙNG thứ hạng, CÙNG CLB, CÙNG sức chứa.")
    print(f"     Cảnh 1 C {'có' if 'C' in c1_that else 'KHÔNG có'} suất; "
          f"cảnh 2 C {'có' if 'C' in c2_that else 'không có'} suất.")
    print("     Cái đổi duy nhất: D có mặt hay không.")
    print()
    print("  => Số phận của C không chỉ phụ thuộc thứ hạng của C, mà còn phụ")
    print("     thuộc AI KHÁC đang nộp cùng lúc. Vì thế không viết ra được")
    print("     một danh sách ưu tiên Q_j cố định rồi đọc ra kết quả.")
    print()
    print("  Đây KHÔNG phải lỗi. Đó là điều suất dự trữ sinh ra, và là lý do")
    print("  verify_stability() phải kiểm cặp phá vỡ bằng chính hàm lựa chọn")
    print("  thay vì so với một bảng ưu tiên tĩnh (xem ghi chú dòng 120–134")
    print("  trong rbda_priority_pipeline.py).")
    print()


if __name__ == "__main__":
    main()
