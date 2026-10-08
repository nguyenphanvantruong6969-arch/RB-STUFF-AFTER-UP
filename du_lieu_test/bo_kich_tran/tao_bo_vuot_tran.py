# -*- coding: utf-8 -*-
"""Sinh bộ VƯỢT TRẦN — cố ý sai, để xem phần mềm từ chối đúng chỗ.

Bộ `bo_kich_tran` trả lời "đứng đúng trần thì nhận chứ?". Bộ này trả lời
nửa còn lại: "quá trần một đơn vị thì bỏ ĐÚNG phần nào?". Không có bộ này
thì chỉ mới kiểm được một phía của ranh giới.

Điều phải thấy khi nhập: phần mềm bỏ **riêng buổi sai của riêng em sai**,
các buổi khác của chính em đó vẫn vào, và các em khác không bị ảnh hưởng.
Bỏ cả em hoặc bỏ cả tệp đều là sai.

⚠ ĐÂY LÀ TỆP CỐ Ý SAI. Đừng thả chung với `bo_kich_tran` rồi kết luận bộ
kia bẩn — cảnh báo sinh ra là của bộ này.

Chạy
====
    python du_lieu_test/bo_kich_tran/tao_bo_vuot_tran.py
"""

import os
import random
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sinh_du_lieu as sdl               # noqa: E402
import tao_bo_kich_tran as goc           # noqa: E402

SEED = 2020
BUOI = goc.BUOI


def dung_bo():
    rng = random.Random(SEED)

    clb = []
    for b in BUOI:
        for cid, ten, suc, du, nhom, _h in goc.CLB[b]:
            clb.append({"club_id": cid, "name": ten, "capacity": suc,
                        "reserve_capacity": du, "reserve_group": nhom,
                        "buoi": b})
    ma = {b: [c[0] for c in goc.CLB[b]] for b in BUOI}

    # Mỗi em một ca, ghi rõ ngay đây để README không phải đoán.
    #   so_nv[buoi]  — số nguyện vọng khai ở buổi đó
    #   so_thi[buoi] — số CLB dự thi ở buổi đó (luôn là tập con của nguyện vọng)
    CA = [
        ("HS001", "vượt nguyện vọng ở thu_2",
         {"thu_2": 11, "thu_4": 10, "thu_6": 10}, {"thu_2": 5, "thu_4": 5, "thu_6": 5}),
        ("HS002", "vượt dự thi ở thu_4",
         {"thu_2": 10, "thu_4": 10, "thu_6": 10}, {"thu_2": 5, "thu_4": 6, "thu_6": 5}),
        ("HS003", "vượt CẢ HAI ở cùng một buổi (thu_6)",
         {"thu_2": 10, "thu_4": 10, "thu_6": 12}, {"thu_2": 5, "thu_4": 5, "thu_6": 7}),
        ("HS004", "vượt nguyện vọng ở CẢ BA buổi — em này mất trắng",
         {"thu_2": 11, "thu_4": 11, "thu_6": 11}, {"thu_2": 5, "thu_4": 5, "thu_6": 5}),
        ("HS005", "đứng ĐÚNG trần — phải vào trọn vẹn, không một cảnh báo",
         {"thu_2": 10, "thu_4": 10, "thu_6": 10}, {"thu_2": 5, "thu_4": 5, "thu_6": 5}),
        ("HS006", "đối chứng, khai vừa phải",
         {"thu_2": 4, "thu_4": 3, "thu_6": 5}, {"thu_2": 2, "thu_4": 3, "thu_6": 1}),
    ]

    hs = []
    for sid, _mota, so_nv, so_thi in CA:
        ten = "%s %s %s" % (rng.choice(sdl._HO), rng.choice(sdl._DEM),
                            rng.choice(sdl._TEN))
        nv, diem = {}, {}
        for b in BUOI:
            k = min(so_nv[b], len(ma[b]))
            nv[b] = rng.sample(ma[b], k)
            for cid in nv[b][:so_thi[b]]:
                diem[cid] = goc.sinh_diem(rng, "")
        hs.append({"student_id": sid, "name": ten, "reserve_group": "",
                   "nguyen_vong": nv, "diem": diem})
    return clb, hs


def main():
    thu_muc = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vuot_tran")
    clb, hs = dung_bo()

    # Phép soát NGƯỢC: bộ này phải SAI, và sai đúng những chỗ đã thiết kế.
    # Soát sạch nghĩa là ca biên đã tuột mất, và bộ này thành vô dụng.
    loi = sdl.soat(clb, hs)
    mong_doi = [
        ("HS001", "vượt trần 10"), ("HS002", "vượt trần 5"),
        ("HS003", "vượt trần 10"), ("HS003", "vượt trần 5"),
        ("HS004", "vượt trần 10"),
    ]
    for sid, manh in mong_doi:
        if not any(sid in e and manh in e for e in loi):
            print("Thiếu lỗi mong đợi: %s · %s — KHÔNG ghi tệp nào." % (sid, manh),
                  file=sys.stderr)
            return 1
    if any("HS005" in e or "HS006" in e for e in loi):
        print("HS005/HS006 phải HỢP LỆ mà đang bị báo lỗi — KHÔNG ghi tệp nào.",
              file=sys.stderr)
        return 1

    sdl.ghi_bo(thu_muc, clb, hs)
    for cu, moi in (("01_danh_sach_CLB.csv", "VUOTTRAN_01_danh_sach_CLB.csv"),
                    ("02_chon_CLB_muon_thi.csv", "VUOTTRAN_02_chon_CLB_muon_thi.csv"),
                    ("03_xep_hang_nguyen_vong.csv", "VUOTTRAN_03_xep_hang_nguyen_vong.csv")):
        os.replace(os.path.join(thu_muc, cu), os.path.join(thu_muc, moi))

    print("Đã ghi bộ CỐ Ý SAI: %d CLB · %d học sinh" % (len(clb), len(hs)))
    print("%d lỗi đúng như thiết kế:" % len(loi))
    for e in loi:
        print("   ✗", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
