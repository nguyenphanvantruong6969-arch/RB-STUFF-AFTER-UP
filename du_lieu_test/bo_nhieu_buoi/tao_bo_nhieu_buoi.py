# -*- coding: utf-8 -*-
"""Sinh bộ dữ liệu mẫu 5 BUỔI để thử tính năng thời khoá biểu tuần.

    python3 du_lieu_test/bo_nhieu_buoi/tao_bo_nhieu_buoi.py

VÌ SAO PHẢI LÀ BỘ RIÊNG, KHÔNG SỬA `bo_sach`
--------------------------------------------
`bo_sach`, `vi_du_huong_dan` và `TEST_0*` là dữ liệu mà toàn bộ số liệu
trong `docs/NGHIEN_CUU_TOI_UU.md` và `SO_LIEU_DA_KIEM_CHUNG.md` đang nói tới.
Thêm một cột `buoi` vào đó là làm mọi con số đã công bố nói về một bộ dữ
liệu không còn tồn tại. Bộ nhiều buổi vì thế là một thư mục MỚI, và ba bộ
cũ không bị đụng một ký tự nào.

BỘ NÀY ĐƯỢC DỰNG CỐ Ý LỆCH TẢI
------------------------------
Thứ 3 cố tình chật (nhiều em muốn, ít chỗ) còn Thứ 6 cố tình rộng. Không
phải để mô phỏng một trường có thật mà để **Bảng tải theo buổi có cái để
chỉ ra**: nhìn bảng là thấy nên dời một câu lạc bộ sang Thứ 6.

⚠️ DỮ LIỆU MÔ PHỎNG — 160 cái tên dưới đây do máy sinh (hạt giống cố định
7788), không phải học sinh có thật. Trình bày chúng như số liệu khảo sát
là bịa đặt dữ liệu.
"""

import os
import sys
import random

GOC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(GOC))
from ghi_du_lieu_chung import ghi_csv, ten_ngau_nhien  # noqa: E402
HAT = 7788
SO_HOC_SINH = 160

BUOI = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6"]

# Tỉ lệ học sinh có khai nguyện vọng cho từng buổi. Thứ 4 và Thứ 5 ít chỗ
# mà đông em muốn -> chật; Thứ 6 nhiều chỗ mà ít em quan tâm -> rộng.
TI_LE_KHAI = {"thu_2": 0.70, "thu_3": 0.85, "thu_4": 0.80,
              "thu_5": 0.75, "thu_6": 0.45}

# (club_id, tên, sức chứa, suất dự trữ, nhóm dự trữ, buổi, sức hút)
# "Sức hút" là trọng số để bốc nguyện vọng — càng cao càng nhiều em chọn.
CLB = [
    ("clb_covua",     "CLB Cờ vua",       18, 0, "",           "thu_2", 1.0),
    ("clb_vanhoc",    "CLB Văn học",      16, 3, "khoi_10",    "thu_2", 0.8),
    ("clb_nhiepanh",  "CLB Nhiếp ảnh",    14, 0, "",           "thu_2", 1.2),

    ("clb_bongda",    "CLB Bóng đá",      20, 5, "chinh_sach", "thu_3", 3.0),
    ("clb_mythuat",   "CLB Mỹ thuật",     14, 3, "khoi_10",    "thu_3", 2.2),
    ("clb_tienganh",  "CLB Tiếng Anh",    16, 2, "chinh_sach", "thu_3", 2.6),

    ("clb_robotics",  "CLB Robotics",     12, 0, "",           "thu_4", 1.6),
    ("clb_khoahoc",   "CLB Khoa học",     14, 2, "khoi_10",    "thu_4", 1.1),

    ("clb_tinhoc",    "CLB Tin học",      16, 4, "chinh_sach", "thu_5", 1.8),
    ("clb_amnhac",    "CLB Âm nhạc",      15, 0, "",           "thu_5", 1.4),

    ("clb_tinhnguyen", "CLB Tình nguyện", 22, 0, "",           "thu_6", 0.5),
    ("clb_bongro",    "CLB Bóng rổ",      20, 0, "",           "thu_6", 0.7),
    ("clb_lamvuon",   "CLB Làm vườn",     18, 0, "",           "thu_6", 0.4),
]

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ"]
DEM = ["Văn", "Thị", "Hoài", "Minh", "Anh", "Quốc", "Thanh", "Ngọc", "Gia", "Khánh"]
TEN = ["An", "Bình", "Chi", "Dũng", "Giang", "Hà", "Hải", "Hương", "Khanh", "Lan",
       "Linh", "Mai", "Nam", "Ngân", "Phúc", "Quân", "Sơn", "Thảo", "Tuấn", "Vy"]


def _ten(rng):
    return ten_ngau_nhien(rng, HO, DEM, TEN)


def _ghi(ten_tep, header, rows):
    # Đọc GOC lúc GỌI (không bắt sẵn lúc định nghĩa) để test đổi được nơi ghi.
    return ghi_csv(GOC, ten_tep, header, rows)


def sinh():
    rng = random.Random(HAT)
    ds_em = ["HS%03d" % i for i in range(1, SO_HOC_SINH + 1)]
    ten_em = {sid: _ten(rng) for sid in ds_em}

    nhom = {}
    for sid in ds_em:
        r = rng.random()
        nhom[sid] = "chinh_sach" if r < 0.14 else ("khoi_10" if r < 0.30 else "")

    clb_theo_buoi = {b: [c for c in CLB if c[5] == b] for b in BUOI}

    # --- 01: danh sách CLB ---
    _ghi("NHIEUBUOI_01_danh_sach_CLB.csv",
         ["club_id", "name", "capacity", "reserve_capacity", "reserve_group", "buoi"],
         [[c[0], c[1], c[2], c[3], c[4], c[5]] for c in CLB])

    # --- Nguyện vọng: mỗi buổi một danh sách xếp hạng riêng ---
    nguyen_vong = {}
    for sid in ds_em:
        theo_buoi = {}
        for b in BUOI:
            # Không em nào cũng khai đủ 5 buổi. Một số em chỉ rảnh vài buổi,
            # và cách khai "em bận thứ 5" chính là BỎ TRỐNG danh sách thứ 5.
            # Tỉ lệ khai khác nhau theo buổi để bộ dữ liệu LỆCH TẢI thật —
            # có buổi chật, có buổi rộng, để Bảng tải theo buổi có cái chỉ ra.
            if rng.random() > TI_LE_KHAI[b]:
                continue
            ung_vien = clb_theo_buoi[b][:]
            trong_so = [c[6] for c in ung_vien]
            k = min(len(ung_vien), rng.randint(1, len(ung_vien)))
            chon = []
            for _ in range(k):
                tong = sum(trong_so)
                if tong <= 0:
                    break
                moc = rng.uniform(0, tong)
                acc = 0.0
                for i, w in enumerate(trong_so):
                    acc += w
                    if acc >= moc:
                        chon.append(ung_vien[i][0])
                        del ung_vien[i]
                        del trong_so[i]
                        break
            if chon:
                theo_buoi[b] = chon
        nguyen_vong[sid] = theo_buoi

    max_moi_buoi = {
        b: max((len(nv.get(b, [])) for nv in nguyen_vong.values()), default=0)
        for b in BUOI
    }
    header = ["student_id", "name", "reserve_group"]
    for b in BUOI:
        header += ["%s_pref_%d" % (b, i + 1) for i in range(max_moi_buoi[b])]
    rows = []
    for sid in ds_em:
        dong = [sid, ten_em[sid], nhom[sid]]
        for b in BUOI:
            ds = nguyen_vong[sid].get(b, [])
            dong += [ds[i] if i < len(ds) else "" for i in range(max_moi_buoi[b])]
        rows.append(dong)
    _ghi("NHIEUBUOI_03_xep_hang_nguyen_vong.csv", header, rows)

    # --- 02: chọn CLB muốn thi + điểm ---
    # Em chỉ thi những CLB mình có khai nguyện vọng — thi một CLB không định
    # vào là chuyện không ai làm.
    max_thi = 0
    du_thi = {}
    for sid in ds_em:
        tat_ca = [cid for ds in nguyen_vong[sid].values() for cid in ds]
        rng.shuffle(tat_ca)
        chon = tat_ca[: rng.randint(0, min(4, len(tat_ca)))]
        du_thi[sid] = [(cid, round(rng.uniform(4.0, 10.0), 1)) for cid in chon]
        max_thi = max(max_thi, len(chon))

    header2 = ["student_id", "name", "reserve_group"]
    for i in range(max_thi):
        header2 += ["test_club_%d" % (i + 1), "score_%d" % (i + 1)]
    rows2 = []
    for sid in ds_em:
        dong = [sid, ten_em[sid], nhom[sid]]
        for i in range(max_thi):
            if i < len(du_thi[sid]):
                dong += [du_thi[sid][i][0], du_thi[sid][i][1]]
            else:
                dong += ["", ""]
        rows2.append(dong)
    _ghi("NHIEUBUOI_02_chon_CLB_muon_thi.csv", header2, rows2)

    tong_cho = sum(c[2] for c in CLB)
    print("Đã sinh bộ %d học sinh / %d câu lạc bộ / %d buổi / %d chỗ"
          % (SO_HOC_SINH, len(CLB), len(BUOI), tong_cho))
    for b in BUOI:
        cho = sum(c[2] for c in clb_theo_buoi[b])
        em_muon = sum(1 for nv in nguyen_vong.values() if nv.get(b))
        print("  %-7s %2d CLB · %3d chỗ · %3d em muốn · chọi %.2f×"
              % (b, len(clb_theo_buoi[b]), cho, em_muon,
                 em_muon / cho if cho else 0))


if __name__ == "__main__":
    sinh()
