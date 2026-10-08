# -*- coding: utf-8 -*-
"""Sinh bộ dữ liệu KỊCH TRẦN — ba buổi, mỗi em 10 nguyện vọng và 5 CLB dự
thi MỖI BUỔI, đúng bằng hai trần của phần mềm.

Vì sao bộ này tồn tại
=====================
Không một bộ mẫu nào trong `du_lieu_test/` đứng sát trần:

    bo_sach          6 nguyện vọng · 4 dự thi   (một buổi)
    bo_nhieu_buoi    3 nguyện vọng · 3 dự thi   (năm buổi)
    vi_du_day_du     2 nguyện vọng · 1 dự thi   (ba buổi)
    TEST_01..04      5 nguyện vọng · 5 dự thi   (một buổi)

Trần 10 nguyện vọng mỗi buổi vì thế chỉ được khoá bằng test đơn vị, chưa
bao giờ được thả vào phần mềm thật. Bộ này lấp đúng chỗ đó: nó đứng ĐÚNG
10 và ĐÚNG 5, không có suất dự phòng nào. Đổi `TRAN_*` trong
`rbda_priority_pipeline.py` mà quên sửa đây là bộ này vỡ ngay khi soát.

Muốn 10 nguyện vọng trong một buổi thì buổi đó phải có TRÊN 10 câu lạc bộ,
nếu không thì trần thật là số câu lạc bộ chứ không phải số 10. Ở đây mỗi
buổi 12 câu lạc bộ, nên xếp 10 vẫn là một lựa chọn thật: em bỏ lại 2.

Chạy
====
    python du_lieu_test/bo_kich_tran/tao_bo_kich_tran.py

Ba tệp đi ra từ MỘT nguồn trong bộ nhớ và chỉ được ghi sau khi chín phép
soát của `.claude/skills/sinh-du-lieu-clb` trả về rỗng. Sai một điều là
không tệp nào được ghi.
"""

import os
import random
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts"))

import sinh_du_lieu as sdl  # noqa: E402  (phải chèn đường dẫn trước)

SEED = 1010
SO_HOC_SINH = 150
BUOI = ["thu_2", "thu_4", "thu_6"]

# Đúng bằng trần của phần mềm — lấy thẳng từ đó, không gõ lại con số.
SO_NV_MOI_BUOI = sdl.TRAN_NGUYEN_VONG_MOI_BUOI   # 10
SO_THI_MOI_BUOI = sdl.TRAN_CLB_THI_MOI_BUOI      # 5

# 12 CLB mỗi buổi. Cột cuối là ĐỘ HÚT — nhu cầu cố ý dồn vào vài CLB, nếu
# trải đều thì ai cũng vừa ý và thuật toán không phải làm gì.
#
#   (club_id, tên, sức chứa, dự trữ, nhóm dự trữ, độ hút)
CLB = {
    "thu_2": [
        ("clb_tinhoc",     "CLB Tin học",         12, 3, "chinh_sach", 10.0),
        ("clb_bongro",     "CLB Bóng rổ",         12, 0, "",            8.0),
        ("clb_tranbien",   "CLB Tranh biện",      10, 2, "khoi_10",     7.0),
        ("clb_nhiepanh",   "CLB Nhiếp ảnh",       10, 0, "",            5.0),
        ("clb_amnhac",     "CLB Âm nhạc",         12, 0, "",            5.0),
        ("clb_lamphim",    "CLB Làm phim",         8, 0, "",            4.0),
        ("clb_covua",      "CLB Cờ vua",           8, 0, "",            3.0),
        ("clb_thienvan",   "CLB Thiên văn",       10, 0, "",            2.5),
        ("clb_vanhoc",     "CLB Văn học",         10, 0, "",            2.0),
        ("clb_bongban",    "CLB Bóng bàn",        12, 0, "",            1.5),
        ("clb_tiengnhat",  "CLB Tiếng Nhật",      12, 0, "",            1.2),
        ("clb_yoga",       "CLB Yoga",            12, 0, "",            1.0),
    ],
    "thu_4": [
        ("clb_robotics",   "CLB Robotics",        10, 2, "chinh_sach", 10.0),
        ("clb_bongda",     "CLB Bóng đá",         14, 3, "chinh_sach",  8.5),
        ("clb_mythuat",    "CLB Mỹ thuật",        10, 2, "khoi_10",     7.0),
        ("clb_tienganh",   "CLB Tiếng Anh",       12, 0, "",            6.0),
        ("clb_gamedev",    "CLB Lập trình game",   8, 0, "",            5.0),
        ("clb_sankhau",    "CLB Sân khấu",        10, 0, "",            3.5),
        ("clb_nauan",      "CLB Nấu ăn",          12, 0, "",            3.0),
        ("clb_caulong",    "CLB Cầu lông",        12, 0, "",            2.5),
        ("clb_khoahoc",    "CLB Khoa học",        10, 0, "",            2.0),
        ("clb_khoinghiep", "CLB Khởi nghiệp",     10, 0, "",            1.5),
        ("clb_thuphap",    "CLB Thư pháp",        10, 0, "",            1.2),
        ("clb_dienkinh",   "CLB Điền kinh",       12, 0, "",            1.0),
    ],
    "thu_6": [
        ("clb_guitar",     "CLB Guitar",          10, 2, "khoi_10",    10.0),
        ("clb_nhayhiendai","CLB Nhảy hiện đại",   10, 0, "",            8.0),
        ("clb_baochi",     "CLB Báo chí",         10, 2, "chinh_sach",  6.5),
        ("clb_boiloi",     "CLB Bơi lội",         12, 0, "",            5.5),
        ("clb_toanhoc",    "CLB Toán học",        10, 0, "",            4.5),
        ("clb_hoahoc",     "CLB Hoá học",          8, 0, "",            3.5),
        ("clb_tinhnguyen", "CLB Tình nguyện",     14, 0, "",            3.0),
        ("clb_lamvuon",    "CLB Làm vườn",        12, 0, "",            2.0),
        ("clb_cotuong",    "CLB Cờ tướng",        10, 0, "",            1.8),
        ("clb_thucong",    "CLB Thủ công",        10, 0, "",            1.5),
        ("clb_dulich",     "CLB Du lịch",         12, 0, "",            1.2),
        ("clb_duongsinh",  "CLB Dưỡng sinh",      12, 0, "",            1.0),
    ],
}

# Điểm trung bình theo nhóm. Nhóm dự trữ thấp hơn một chút — nếu bằng nhau
# thì suất dự trữ không đổi kết quả và cả cơ chế dự trữ thành vô hình.
DIEM_TB = {"": 7.6, "chinh_sach": 6.5, "khoi_10": 6.8}
DIEM_LECH = 1.3

# --- Các ca biên, cố định theo mã học sinh để README nói được tên ---
# Bỏ trống HẲN một buổi — "ngày đó em bận". Dữ liệu HỢP LỆ.
BAN_MOT_BUOI = {"HS141": "thu_2", "HS142": "thu_4", "HS143": "thu_6",
                "HS144": "thu_2", "HS145": "thu_4", "HS146": "thu_6"}
# Xếp nguyện vọng NGẮN ở một buổi — trần là trần trên, không phải chỉ tiêu.
NGUYEN_VONG_NGAN = {"HS147": ("thu_2", 3), "HS148": ("thu_4", 5),
                    "HS149": ("thu_6", 6), "HS150": ("thu_2", 1)}
# Xếp đủ 10 nhưng KHÔNG dự thi CLB nào ở buổi đó — cả 10 xét ở Tier 2.
KHONG_THI_MOT_BUOI = {"HS131": "thu_4", "HS132": "thu_4", "HS133": "thu_6",
                      "HS134": "thu_6", "HS135": "thu_2"}


def boc_theo_trong_so(rng, ma, hut, k):
    """Bốc `k` mã khác nhau, xác suất tỉ lệ với độ hút. Giữ thứ tự bốc —
    thứ tự bốc CHÍNH LÀ thứ hạng nguyện vọng, nên không được sắp lại."""
    con = list(ma)
    ra = []
    for _ in range(min(k, len(con))):
        tong = sum(hut[c] for c in con)
        moc = rng.uniform(0, tong)
        don = 0.0
        for c in con:
            don += hut[c]
            if don >= moc:
                ra.append(c)
                con.remove(c)
                break
    return ra


def sinh_diem(rng, nhom):
    d = rng.gauss(DIEM_TB.get(nhom, DIEM_TB[""]), DIEM_LECH)
    # Dấu PHẨY thập phân — đúng cách Excel bản tiếng Việt lưu ra.
    return ("%.1f" % round(min(10.0, max(4.0, d)), 1)).replace(".", ",")


def dung_bo():
    rng = random.Random(SEED)

    clb = []
    for b in BUOI:
        for cid, ten, suc, du, nhom, _hut in CLB[b]:
            clb.append({"club_id": cid, "name": ten, "capacity": suc,
                        "reserve_capacity": du, "reserve_group": nhom,
                        "buoi": b})

    ma_theo_buoi = {b: [c[0] for c in CLB[b]] for b in BUOI}
    hut = {c[0]: c[5] for b in BUOI for c in CLB[b]}

    hs = []
    for i in range(1, SO_HOC_SINH + 1):
        sid = "HS%03d" % i
        ten = "%s %s %s" % (rng.choice(sdl._HO), rng.choice(sdl._DEM),
                            rng.choice(sdl._TEN))
        r = rng.random()
        nhom = "chinh_sach" if r < 0.13 else ("khoi_10" if r < 0.23 else "")

        nv, diem = {}, {}
        for b in BUOI:
            if BAN_MOT_BUOI.get(sid) == b:
                nv[b] = []
                continue

            k = SO_NV_MOI_BUOI
            if NGUYEN_VONG_NGAN.get(sid, (None,))[0] == b:
                k = NGUYEN_VONG_NGAN[sid][1]
            nv[b] = boc_theo_trong_so(rng, ma_theo_buoi[b], hut, k)

            if KHONG_THI_MOT_BUOI.get(sid) == b:
                continue
            # Dự thi = một tập con của nguyện vọng buổi đó, thiên về đầu
            # bảng. Thi một CLB mình không xếp nguyện vọng là lượt thi bỏ
            # phí — chính phép soát số 8 chặn chuyện đó.
            so_thi = min(SO_THI_MOI_BUOI, len(nv[b]))
            uu_tien = {c: 1.0 / (j + 1) for j, c in enumerate(nv[b])}
            for cid in boc_theo_trong_so(rng, nv[b], uu_tien, so_thi):
                diem[cid] = sinh_diem(rng, nhom)

        hs.append({"student_id": sid, "name": ten, "reserve_group": nhom,
                   "nguyen_vong": nv, "diem": diem})

    # Mọi nhóm có CLB đặt suất dự trữ thì phải có NGƯỜI thuộc nhóm đó, nếu
    # không suất ấy không ai nhận được và phần mềm cảnh báo — đúng.
    for g in sorted({c["reserve_group"] for c in clb if c["reserve_group"]}):
        if not any(h["reserve_group"] == g for h in hs):
            chua = [h for h in hs if not h["reserve_group"]] or hs
            rng.choice(chua)["reserve_group"] = g

    return clb, hs


def main():
    thu_muc = os.path.dirname(os.path.abspath(__file__))
    clb, hs = dung_bo()

    loi = sdl.soat(clb, hs)
    if loi:
        print("KHÔNG HỢP LỆ — %d lỗi, KHÔNG ghi tệp nào:" % len(loi),
              file=sys.stderr)
        for e in loi:
            print("   ✗", e, file=sys.stderr)
        return 1

    # Hai phép soát riêng của bộ này: nó phải ĐỨNG ĐÚNG trần, không chỉ là
    # "không vượt trần". Bộ kịch trần mà tụt xuống 9 thì mất lý do tồn tại.
    cham_nv = max(len(ds) for h in hs for ds in h["nguyen_vong"].values())
    buoi_cua = {c["club_id"]: c["buoi"] for c in clb}
    cham_thi = 0
    for h in hs:
        theo = {}
        for cid in h["diem"]:
            theo[buoi_cua[cid]] = theo.get(buoi_cua[cid], 0) + 1
        cham_thi = max([cham_thi] + list(theo.values()))
    if cham_nv != SO_NV_MOI_BUOI or cham_thi != SO_THI_MOI_BUOI:
        print("Bộ này phải chạm ĐÚNG trần %d/%d, đang là %d/%d — KHÔNG ghi."
              % (SO_NV_MOI_BUOI, SO_THI_MOI_BUOI, cham_nv, cham_thi),
              file=sys.stderr)
        return 1

    sdl.ghi_bo(thu_muc, clb, hs)
    for cu, moi in (("01_danh_sach_CLB.csv", "KICHTRAN_01_danh_sach_CLB.csv"),
                    ("02_chon_CLB_muon_thi.csv", "KICHTRAN_02_chon_CLB_muon_thi.csv"),
                    ("03_xep_hang_nguyen_vong.csv", "KICHTRAN_03_xep_hang_nguyen_vong.csv")):
        os.replace(os.path.join(thu_muc, cu), os.path.join(thu_muc, moi))

    print("Hợp lệ: %d CLB · %d buổi · %d học sinh · %d ô điểm"
          % (len(clb), len(BUOI), len(hs), sum(len(h["diem"]) for h in hs)))
    print("Chạm trần: %d nguyện vọng/buổi · %d dự thi/buổi" % (cham_nv, cham_thi))
    for w in sdl.canh_bao_men(clb, hs):
        print("   ⚠", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
