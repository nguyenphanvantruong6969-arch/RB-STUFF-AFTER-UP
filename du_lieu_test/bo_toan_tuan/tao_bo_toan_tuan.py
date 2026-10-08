# -*- coding: utf-8 -*-
"""Sinh bộ TOÀN TUẦN — cả 7 buổi phần mềm nhận ra, kín trần ở MỌI buổi.

Khác `bo_kich_tran` ở hai điểm, và cả hai đều cố ý:

  * `bo_kich_tran` — 3 buổi, có ca biên (em bận một buổi, em khai ngắn,
    em không dự thi). Bộ đó dạy phần mềm xử ĐÚNG những trường hợp lệch.
  * `bo_toan_tuan` — 7 buổi, KHÔNG một ca lệch nào. Mọi em kín trần
    10 nguyện vọng và 5 CLB dự thi ở CẢ BẢY buổi. Bộ này đo đúng một
    thứ: trần tuyệt đối của phần mềm khi không có chỗ nào dôi ra.

Trần tuyệt đối mỗi em: 7 × 10 = 70 nguyện vọng, 7 × 5 = 35 lượt dự thi.
Không cấu hình hợp lệ nào vượt được con số đó, vì `BUOI_CHUAN` chỉ có
bảy nhãn và trần là trần MỖI BUỔI.

Bảy nhãn đó — thu_2..thu_7, chu_nhat — đều nằm trong bảng `_SO_CUA_THU`
của `rbda_priority_pipeline`, nên màn hình Kết quả sắp chúng đúng thứ
tự trong tuần chứ không sắp theo vần (chu_nhat mang số 8, đứng cuối).

Chạy
====
    python du_lieu_test/bo_toan_tuan/tao_bo_toan_tuan.py
"""

import os
import random
import sys

_GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts"))

import sinh_du_lieu as sdl  # noqa: E402

SEED = 7070
SO_HOC_SINH = 200
BUOI = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7", "chu_nhat"]

SO_NV_MOI_BUOI = sdl.TRAN_NGUYEN_VONG_MOI_BUOI   # 10
SO_THI_MOI_BUOI = sdl.TRAN_CLB_THI_MOI_BUOI      # 5

# Mỗi buổi 12 CLB. Phải TRÊN 10, nếu không trần thật là số CLB của buổi
# chứ không phải con số 10 — và bộ này mất lý do tồn tại.
CLB_MOI_BUOI = 12

# Hồ sơ dùng chung cho cả bảy buổi: sức chứa và độ hút NGƯỢC nhau — CLB
# hút nhất lại chật nhất. Trải đều thì ai cũng vừa ý ngay vòng đầu và
# thuật toán không phải đẩy dây chuyền lần nào.
SUC_CHUA = [8, 10, 12, 12, 14, 14, 14, 16, 16, 16, 20, 22]   # tổng 174
DO_HUT = [10.0, 8.5, 7.0, 6.0, 5.0, 4.0, 3.2, 2.6, 2.1, 1.7, 1.3, 1.0]
# Hai chỗ đặt suất dự trữ mỗi buổi, đều là CLB đông — đặt ở CLB còn thừa
# chỗ thì suất đó vô dụng vì ai cũng vào được.
DU_TRU = {0: (2, "chinh_sach"), 2: (3, "khoi_10")}

# 84 câu lạc bộ, 12 mỗi buổi, mã không trùng nhau một cái nào.
TEN_CLB = {
    "thu_2": [
        ("clb_tinhoc", "CLB Tin học"), ("clb_bongro", "CLB Bóng rổ"),
        ("clb_tranbien", "CLB Tranh biện"), ("clb_nhiepanh", "CLB Nhiếp ảnh"),
        ("clb_amnhac", "CLB Âm nhạc"), ("clb_lamphim", "CLB Làm phim"),
        ("clb_covua", "CLB Cờ vua"), ("clb_thienvan", "CLB Thiên văn"),
        ("clb_vanhoc", "CLB Văn học"), ("clb_bongban", "CLB Bóng bàn"),
        ("clb_tiengnhat", "CLB Tiếng Nhật"), ("clb_yoga", "CLB Yoga"),
    ],
    "thu_3": [
        ("clb_laptrinh", "CLB Lập trình"), ("clb_caulong", "CLB Cầu lông"),
        ("clb_mythuatso", "CLB Mỹ thuật số"), ("clb_guitar", "CLB Guitar"),
        ("clb_hungbien", "CLB Hùng biện"), ("clb_covay", "CLB Cờ vây"),
        ("clb_kichnoi", "CLB Kịch nói"), ("clb_sinhhoc", "CLB Sinh học"),
        ("clb_tienghan", "CLB Tiếng Hàn"), ("clb_leonui", "CLB Leo núi"),
        ("clb_origami", "CLB Origami"), ("clb_khieuvu", "CLB Khiêu vũ"),
    ],
    "thu_4": [
        ("clb_robotics", "CLB Robotics"), ("clb_bongda", "CLB Bóng đá"),
        ("clb_mythuat", "CLB Mỹ thuật"), ("clb_tienganh", "CLB Tiếng Anh"),
        ("clb_gamedev", "CLB Lập trình game"), ("clb_sankhau", "CLB Sân khấu"),
        ("clb_nauan", "CLB Nấu ăn"), ("clb_khoahoc", "CLB Khoa học"),
        ("clb_khoinghiep", "CLB Khởi nghiệp"), ("clb_thuphap", "CLB Thư pháp"),
        ("clb_dienkinh", "CLB Điền kinh"), ("clb_lambanh", "CLB Làm bánh"),
    ],
    "thu_5": [
        ("clb_toanhoc", "CLB Toán học"), ("clb_boiloi", "CLB Bơi lội"),
        ("clb_hoihoa", "CLB Hội hoạ"), ("clb_piano", "CLB Piano"),
        ("clb_tiengphap", "CLB Tiếng Pháp"), ("clb_mohinh", "CLB Mô hình"),
        ("clb_thehinh", "CLB Thể hình"), ("clb_tamly", "CLB Tâm lý học"),
        ("clb_dohoa", "CLB Thiết kế đồ hoạ"), ("clb_camhoa", "CLB Cắm hoa"),
        ("clb_dacau", "CLB Đá cầu"), ("clb_docsach", "CLB Đọc sách"),
    ],
    "thu_6": [
        ("clb_baochi", "CLB Báo chí"), ("clb_nhayhiendai", "CLB Nhảy hiện đại"),
        ("clb_hoahoc", "CLB Hoá học"), ("clb_tinhnguyen", "CLB Tình nguyện"),
        ("clb_lamvuon", "CLB Làm vườn"), ("clb_cotuong", "CLB Cờ tướng"),
        ("clb_thucong", "CLB Thủ công"), ("clb_dulich", "CLB Du lịch"),
        ("clb_duongsinh", "CLB Dưỡng sinh"), ("clb_violin", "CLB Violin"),
        ("clb_tiengtrung", "CLB Tiếng Trung"), ("clb_bongchuyen", "CLB Bóng chuyền"),
    ],
    "thu_7": [
        ("clb_dienanh", "CLB Điện ảnh"), ("clb_marketing", "CLB Marketing"),
        ("clb_vatly", "CLB Vật lý"), ("clb_taekwondo", "CLB Taekwondo"),
        ("clb_hopxuong", "CLB Hợp xướng"), ("clb_truyentranh", "CLB Vẽ truyện tranh"),
        ("clb_moitruong", "CLB Môi trường"), ("clb_lichsu", "CLB Lịch sử"),
        ("clb_boardgame", "CLB Boardgame"), ("clb_trong", "CLB Trống"),
        ("clb_bongnem", "CLB Bóng ném"), ("clb_theu", "CLB Thêu"),
    ],
    "chu_nhat": [
        ("clb_camtrai", "CLB Cắm trại"), ("clb_podcast", "CLB Podcast"),
        ("clb_dangoai", "CLB Dã ngoại"), ("clb_xedap", "CLB Xe đạp"),
        ("clb_nauchay", "CLB Nấu chay"), ("clb_kynangsong", "CLB Kỹ năng sống"),
        ("clb_vetuong", "CLB Vẽ tường"), ("clb_suachua", "CLB Sửa chữa"),
        ("clb_chamsocthu", "CLB Chăm sóc thú"), ("clb_thiennhien", "CLB Thiên nhiên"),
        ("clb_caphesach", "CLB Cà phê sách"), ("clb_bongbauduc", "CLB Bóng bầu dục"),
    ],
}

DIEM_TB = {"": 7.6, "chinh_sach": 6.5, "khoi_10": 6.8}
DIEM_LECH = 1.3


def boc_theo_trong_so(rng, ma, hut, k):
    """Bốc `k` mã khác nhau, xác suất tỉ lệ độ hút. Thứ tự bốc CHÍNH LÀ
    thứ hạng nguyện vọng, nên không được sắp lại."""
    con = list(ma)
    ra = []
    for _ in range(min(k, len(con))):
        moc = rng.uniform(0, sum(hut[c] for c in con))
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

    clb, hut = [], {}
    for b in BUOI:
        ds = TEN_CLB[b]
        assert len(ds) == CLB_MOI_BUOI, (b, len(ds))
        for i, (cid, ten) in enumerate(ds):
            du, nhom = DU_TRU.get(i, (0, ""))
            clb.append({"club_id": cid, "name": ten, "capacity": SUC_CHUA[i],
                        "reserve_capacity": du, "reserve_group": nhom,
                        "buoi": b})
            hut[cid] = DO_HUT[i]
    ma_theo_buoi = {b: [c[0] for c in TEN_CLB[b]] for b in BUOI}

    hs = []
    for i in range(1, SO_HOC_SINH + 1):
        sid = "HS%03d" % i
        ten = "%s %s %s" % (rng.choice(sdl._HO), rng.choice(sdl._DEM),
                            rng.choice(sdl._TEN))
        r = rng.random()
        nhom = "chinh_sach" if r < 0.13 else ("khoi_10" if r < 0.23 else "")

        nv, diem = {}, {}
        for b in BUOI:
            # KÍN TRẦN Ở MỌI BUỔI — không một ca lệch nào. Đó là toàn bộ
            # điểm khác biệt của bộ này so với `bo_kich_tran`.
            nv[b] = boc_theo_trong_so(rng, ma_theo_buoi[b], hut, SO_NV_MOI_BUOI)
            uu_tien = {c: 1.0 / (j + 1) for j, c in enumerate(nv[b])}
            for cid in boc_theo_trong_so(rng, nv[b], uu_tien, SO_THI_MOI_BUOI):
                diem[cid] = sinh_diem(rng, nhom)

        hs.append({"student_id": sid, "name": ten, "reserve_group": nhom,
                   "nguyen_vong": nv, "diem": diem})

    # Nhóm nào có CLB đặt suất dự trữ thì phải có NGƯỜI thuộc nhóm đó.
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
        print("KHÔNG HỢP LỆ — %d lỗi, KHÔNG ghi tệp nào:" % len(loi), file=sys.stderr)
        for e in loi:
            print("   ✗", e, file=sys.stderr)
        return 1

    # Bộ này phải kín trần ở MỌI em, MỌI buổi — không chỉ "có em chạm".
    # Chùng một ô là nó thành một bộ mẫu bình thường nữa, mà chùng thì
    # không cảnh báo nào kêu: phần mềm chỉ hỏi "có quá không".
    buoi_cua = {c["club_id"]: c["buoi"] for c in clb}
    for h in hs:
        for b in BUOI:
            n = len(h["nguyen_vong"][b])
            if n != SO_NV_MOI_BUOI:
                print("%s · %s: %d nguyện vọng, phải đúng %d — KHÔNG ghi."
                      % (h["student_id"], b, n, SO_NV_MOI_BUOI), file=sys.stderr)
                return 1
        theo = {}
        for cid in h["diem"]:
            theo[buoi_cua[cid]] = theo.get(buoi_cua[cid], 0) + 1
        for b in BUOI:
            if theo.get(b, 0) != SO_THI_MOI_BUOI:
                print("%s · %s: dự thi %d CLB, phải đúng %d — KHÔNG ghi."
                      % (h["student_id"], b, theo.get(b, 0), SO_THI_MOI_BUOI),
                      file=sys.stderr)
                return 1

    sdl.ghi_bo(thu_muc, clb, hs)
    for cu, moi in (("01_danh_sach_CLB.csv", "TOANTUAN_01_danh_sach_CLB.csv"),
                    ("02_chon_CLB_muon_thi.csv", "TOANTUAN_02_chon_CLB_muon_thi.csv"),
                    ("03_xep_hang_nguyen_vong.csv", "TOANTUAN_03_xep_hang_nguyen_vong.csv")):
        os.replace(os.path.join(thu_muc, cu), os.path.join(thu_muc, moi))

    print("Hợp lệ: %d CLB · %d buổi · %d học sinh" % (len(clb), len(BUOI), len(hs)))
    print("Mỗi em: %d nguyện vọng (%d × %d) · %d lượt dự thi (%d × %d)"
          % (len(BUOI) * SO_NV_MOI_BUOI, len(BUOI), SO_NV_MOI_BUOI,
             len(BUOI) * SO_THI_MOI_BUOI, len(BUOI), SO_THI_MOI_BUOI))
    print("Tổng: %d nguyện vọng · %d ô điểm · %d suất"
          % (sum(len(d) for h in hs for d in h["nguyen_vong"].values()),
             sum(len(h["diem"]) for h in hs),
             sum(c["capacity"] for c in clb)))
    for w in sdl.canh_bao_men(clb, hs):
        print("   ⚠", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
