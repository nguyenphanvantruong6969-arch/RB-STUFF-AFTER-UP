# -*- coding: utf-8 -*-
"""Sinh bộ dữ liệu mẫu 6 BUỔI theo hình dáng một trường có thật.

    python3 du_lieu_test/bo_can_bang/tao_bo_can_bang.py

KHÁC BỘ `bo_sau_buoi` Ở CHỖ NÀO
-------------------------------
`bo_sau_buoi` dựng cố ý chật để bộ chọn buổi và bảng tải có cái chỉ ra.
Nó làm tốt việc đó, nhưng cầu gấp 4 lần cung nên 45 trên 180 em trắng
tay — một con số đúng về mặt cơ chế mà nhìn vào thì người xem nghi phần
mềm, chứ không nghi dữ liệu.

Bộ này sửa hai giả định đã làm méo bộ kia:

1. KHÔNG PHẢI CÂU LẠC BỘ NÀO CŨNG THI. Trường thật chỉ tổ chức thi cho
   vài câu lạc bộ tuyển chọn; phần còn lại ai đăng ký cũng vào, hết chỗ
   thì bốc thăm. Ở đây 6 trên 24 CLB có thi, 18 CLB còn lại thuần bốc
   thăm. Điều này quan trọng vì ưu tiên hai tầng xếp em ĐÃ THI trên em
   CHƯA THI: câu lạc bộ nào cũng thi thì em không thi bị đẩy xuống đáy
   ở mọi hàng đợi cùng lúc, và đó chính là thứ đã tạo ra 45 em kia.

2. EM KHAI CLB CÓ THI THÌ GẦN NHƯ CHẮC CHẮN CÓ ĐI THI. Nhà trường nói
   trước là không thi thì không xét, nên tỉ lệ đi thi là 92%, không phải
   một con số ngẫu nhiên rời rạc với nguyện vọng.

Kết quả: cung sát cầu, phần lớn em có 3–4 CLB, và số em trắng tay rơi
về đúng nhóm KHÔNG ĐĂNG KÝ GÌ — nhóm trường nào cũng có.

⚠️ DỮ LIỆU MÔ PHỎNG — 200 cái tên dưới đây do máy sinh (hạt giống cố
định 31415), không phải học sinh có thật. Trình bày chúng như số liệu
khảo sát là bịa đặt dữ liệu.
"""

import os
import sys
import random

GOC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(GOC))
from ghi_du_lieu_chung import ghi_csv, ten_ngau_nhien  # noqa: E402
HAT = 31415
SO_HOC_SINH = 200

BUOI = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7"]

# Em không đăng ký buổi nào cả. Trường nào cũng có nhóm này — bận việc
# nhà, học thêm, hoặc đơn giản là không quan tâm. Để tỉ lệ này bằng 0 là
# vẽ ra một trường không tồn tại.
TI_LE_KHONG_DANG_KY = 0.06

# Trong số em CÓ đăng ký, tỉ lệ khai nguyện vọng cho từng buổi.
TI_LE_KHAI = {"thu_2": 0.82, "thu_3": 0.86, "thu_4": 0.84,
              "thu_5": 0.80, "thu_6": 0.72, "thu_7": 0.48}

# Em khai một CLB CÓ THI thì có đi thi hay không.
TI_LE_DI_THI = 0.92

# TRẦN CỦA PHẦN MỀM, KHÔNG PHẢI LỰA CHỌN THẨM MỸ.
#
# `api.py` từng đếm nguyện vọng cho CẢ TUẦN và BỎ QUA TRỌN học sinh vượt
# trần — không cắt bớt, mà loại hẳn khỏi đợt xếp. Trần đó viết cho trường
# MỘT buổi; với sáu buổi thì em nào chọn 2 CLB mỗi buổi đã là 12 và rơi ra
# ngoài. Bộ này khi ấy phải tự cắt xuống 10 cho cả tuần, tức tự bóp méo
# chính thứ nó sinh ra để đo.
#
# Trần nay tính THEO TỪNG BUỔI, nên con số dưới đây cũng là mỗi buổi. Với
# bốn câu lạc bộ mỗi buổi thì nó không bao giờ chạm tới — giữ lại là để
# bộ sinh này vẫn tự vệ nếu ai đó thêm câu lạc bộ vào một buổi.
TRAN_NGUYEN_VONG_MOI_BUOI = 10

# (club_id, tên, sức chứa, dự trữ, nhóm dự trữ, buổi, sức hút, CÓ THI)
CLB = [
    ("clb_covua",      "CLB Cờ vua",            24, 0, "",           "thu_2", 1.0, False),
    ("clb_vanhoc",     "CLB Văn học",           22, 4, "khoi_10",    "thu_2", 0.9, False),
    ("clb_nhiepanh",   "CLB Nhiếp ảnh",         20, 0, "",           "thu_2", 1.3, False),
    ("clb_bongban",    "CLB Bóng bàn",          26, 0, "",           "thu_2", 1.1, False),

    ("clb_bongda",     "CLB Bóng đá",           28, 6, "chinh_sach", "thu_3", 2.0, True),
    ("clb_mythuat",    "CLB Mỹ thuật",          22, 4, "khoi_10",    "thu_3", 1.5, True),
    ("clb_tienganh",   "CLB Tiếng Anh",         26, 4, "chinh_sach", "thu_3", 1.8, True),
    ("clb_thuvien",    "CLB Thư viện",          24, 0, "",           "thu_3", 0.7, False),

    ("clb_robotics",   "CLB Robotics",          20, 0, "",           "thu_4", 1.7, True),
    ("clb_khoahoc",    "CLB Khoa học",          24, 4, "khoi_10",    "thu_4", 1.1, False),
    ("clb_tranhbien",  "CLB Tranh biện",        22, 3, "chinh_sach", "thu_4", 1.3, False),
    ("clb_coVay",      "CLB Cờ vây",            20, 0, "",           "thu_4", 0.8, False),

    ("clb_tinhoc",     "CLB Tin học",           26, 5, "chinh_sach", "thu_5", 1.6, True),
    ("clb_amnhac",     "CLB Âm nhạc",           22, 0, "",           "thu_5", 1.4, True),
    ("clb_khieuvu",    "CLB Khiêu vũ",          22, 0, "",           "thu_5", 1.1, False),
    ("clb_thucong",    "CLB Thủ công",          24, 0, "",           "thu_5", 0.8, False),

    ("clb_tinhnguyen", "CLB Tình nguyện",       30, 0, "",           "thu_6", 0.8, False),
    ("clb_bongro",     "CLB Bóng rổ",           26, 0, "",           "thu_6", 1.2, False),
    ("clb_lamvuon",    "CLB Làm vườn",          24, 0, "",           "thu_6", 0.6, False),
    ("clb_dienanh",    "CLB Điện ảnh",          26, 0, "",           "thu_6", 1.0, False),

    ("clb_nauan",      "CLB Nấu ăn",            24, 0, "",           "thu_7", 1.0, False),
    ("clb_dangian",    "CLB Trò chơi dân gian", 28, 0, "",           "thu_7", 0.5, False),
    ("clb_caulong",    "CLB Cầu lông",          24, 0, "",           "thu_7", 0.9, False),
    ("clb_dando",      "CLB Đan đồ",            20, 0, "",           "thu_7", 0.4, False),
]

CO_THI = {c[0] for c in CLB if c[7]}

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ",
      "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Tô"]
DEM = ["Văn", "Thị", "Hoài", "Minh", "Anh", "Quốc", "Thanh", "Ngọc", "Gia", "Khánh",
       "Bảo", "Nhật", "Hữu", "Xuân"]
TEN = ["An", "Bình", "Chi", "Dũng", "Giang", "Hà", "Hải", "Hương", "Khanh", "Lan",
       "Linh", "Mai", "Nam", "Ngân", "Phúc", "Quân", "Sơn", "Thảo", "Tuấn", "Vy",
       "Duy", "Trang", "Kiên", "Nhi", "Đạt", "Hiền", "Long", "Yến"]


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

    khong_dang_ky = {sid for sid in ds_em if rng.random() < TI_LE_KHONG_DANG_KY}
    clb_theo_buoi = {b: [c for c in CLB if c[5] == b] for b in BUOI}

    # --- 01: danh sách CLB (tệp DUY NHẤT mang cột `buoi`) ---
    _ghi("CANBANG_01_danh_sach_CLB.csv",
         ["club_id", "name", "capacity", "reserve_capacity", "reserve_group", "buoi"],
         [[c[0], c[1], c[2], c[3], c[4], c[5]] for c in CLB])

    # --- Nguyện vọng: mỗi buổi một danh sách xếp hạng riêng ---
    nguyen_vong = {}
    for sid in ds_em:
        theo_buoi = {}
        if sid not in khong_dang_ky:
            for b in BUOI:
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

            # Cắt cho vừa trần TỪNG BUỔI: bỏ nguyện vọng CUỐI của buổi nào
            # vượt. Bỏ cuối chứ không bỏ đầu, vì đó là lựa chọn em ít tha
            # thiết nhất.
            for b, ds in theo_buoi.items():
                del ds[TRAN_NGUYEN_VONG_MOI_BUOI:]
            theo_buoi = {b: ds for b, ds in theo_buoi.items() if ds}
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
    _ghi("CANBANG_03_xep_hang_nguyen_vong.csv", header, rows)

    # --- 02: dự thi + điểm ---
    # CHỈ những CLB có tổ chức thi, và chỉ những em đã khai CLB đó. Nhà
    # trường nói trước "không thi thì không xét", nên hầu hết đều đi thi.
    max_thi = 0
    du_thi = {}
    for sid in ds_em:
        ung = [cid for ds in nguyen_vong[sid].values() for cid in ds if cid in CO_THI]
        chon = [cid for cid in ung if rng.random() < TI_LE_DI_THI]
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
    _ghi("CANBANG_02_chon_CLB_muon_thi.csv", header2, rows2)

    tong_cho = sum(c[2] for c in CLB)
    # Bội số có nghĩa là SỐ LƯỢT BUỔI được khai so với số chỗ — mỗi em chỉ
    # nhận tối đa MỘT CLB mỗi buổi, nên đếm tổng nguyện vọng sẽ thổi phồng
    # cầu lên vài lần và nói sai mức chật thật sự.
    tong_luot = sum(1 for nv in nguyen_vong.values() for _ in nv)
    tong_nv = sum(len(ds) for nv in nguyen_vong.values() for ds in nv.values())
    print("Đã sinh bộ %d học sinh / %d câu lạc bộ / %d buổi / %d chỗ"
          % (SO_HOC_SINH, len(CLB), len(BUOI), tong_cho))
    print("  %d CLB có thi · %d CLB thuần bốc thăm · %d em không đăng ký gì"
          % (len(CO_THI), len(CLB) - len(CO_THI), len(khong_dang_ky)))
    print("  %d lượt buổi được khai / %d chỗ — bội số cầu/cung %.2f×"
          % (tong_luot, tong_cho, tong_luot / tong_cho))
    qua_tran = sum(1 for nv in nguyen_vong.values()
                   if any(len(v) > TRAN_NGUYEN_VONG_MOI_BUOI for v in nv.values()))
    print("  Tổng nguyện vọng %d · em vượt trần MỖI BUỔI %d (phải là 0)"
          % (tong_nv, qua_tran))
    for b in BUOI:
        cho = sum(c[2] for c in clb_theo_buoi[b])
        em_muon = sum(1 for nv in nguyen_vong.values() if nv.get(b))
        print("  %-7s %2d CLB · %3d chỗ · %3d em muốn · chọi %.2f×"
              % (b, len(clb_theo_buoi[b]), cho, em_muon,
                 em_muon / cho if cho else 0))


if __name__ == "__main__":
    sinh()
