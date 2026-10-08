# -*- coding: utf-8 -*-
"""Sinh và soát bộ dữ liệu đầu vào cho phần mềm phân bổ câu lạc bộ (RB-DA).

Ba chế độ:

    python sinh_du_lieu.py tao   --spec truong.json --ra ./bo_moi
    python sinh_du_lieu.py ngau  --ra ./bo_moi  --hoc-sinh 180 --buoi thu_2,thu_4,thu_6
    python sinh_du_lieu.py soat  ./bo_moi

`tao`  — dựng từ một bản khai báo JSON tường minh (bạn nắm toàn quyền).
`ngau` — dựng một trường ngẫu nhiên nhưng HỢP LỆ, tất định theo `--seed`.
`soat` — soát một bộ đã có, không sửa gì.

Đầu ra là MỘT tệp: `SO_NHAP_CLB.xlsx` — Sổ nhập CLB, đúng tệp phần mềm nhận
(xem `so_nhap.py` ở gốc kho mã). `soat` đọc được cả sổ lẫn bộ ba CSV cũ.

NGUYÊN TẮC: sổ luôn đi ra từ MỘT nguồn trong bộ nhớ, và mọi phép soát chạy
TRƯỚC khi ghi. Sai một điều là không ghi gì — sinh ra một bộ dữ liệu hỏng
còn tệ hơn không sinh gì, vì nó trông y như thật.

Đoạn mã này KHÔNG tự sửa dữ liệu sai. Sửa giúp là giấu mất chỗ sai.
"""

import argparse
import csv
import io
import json
import os
import random
import sys

# so_nhap.py (định nghĩa Sổ nhập CLB) nằm ở gốc kho mã; bản đóng gói (.zip)
# để một bản sao ngay cạnh script này — ưu tiên bản cạnh script.
_DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_DAY, "..", "..", "..", "..")))
sys.path.insert(0, _DAY)
import so_nhap  # noqa: E402

# Trần do chính phần mềm áp, không phải do đoạn mã này nghĩ ra.
# Xem `rbda_priority_pipeline.TRAN_NGUYEN_VONG_MOI_BUOI` / `TRAN_CLB_THI_MOI_BUOI`.
TRAN_NGUYEN_VONG_MOI_BUOI = 10   # = giới hạn câu hỏi Ranking của Microsoft Forms
TRAN_CLB_THI_MOI_BUOI = 5

# Tệp ghi ra.
TEN_SO = "SO_NHAP_CLB.xlsx"

# Bộ ba tệp CSV cũ — chỉ còn để `soat` đọc các bộ đã có.
TEN_TEP = {
    "clb": "01_danh_sach_CLB.csv",
    "thi": "02_chon_CLB_muon_thi.csv",
    "nv": "03_xep_hang_nguyen_vong.csv",
}

# Nhãn buổi phần mềm nhận ra được (còn nhận nhiều cách viết khác; đây là
# cách viết chuẩn nên dùng khi sinh mới).
BUOI_CHUAN = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7", "chu_nhat"]


# ---------------------------------------------------------------------------
# SOÁT — dùng chung cho cả sinh mới lẫn kiểm bộ đã có
# ---------------------------------------------------------------------------

def soat(clb, hs):
    """Trả về danh sách lỗi. Rỗng = hợp lệ.

    `clb`: [{club_id, name, capacity, reserve_capacity, reserve_group, buoi}]
    `hs` : [{student_id, name, reserve_group, nguyen_vong: {buoi: [club_id]},
             diem: {club_id: float|str}}]
    """
    loi = []

    ma = [c["club_id"] for c in clb]
    if len(ma) != len(set(ma)):
        loi.append("có mã câu lạc bộ bị trùng trong danh sách")
    tap_ma = set(ma)
    buoi_cua = {c["club_id"]: (c.get("buoi") or "") for c in clb}

    for c in clb:
        if not c["club_id"]:
            loi.append("có câu lạc bộ thiếu mã")
        try:
            suc = int(c["capacity"])
        except (TypeError, ValueError):
            loi.append("%s: sức chứa không phải số" % c["club_id"])
            continue
        if suc <= 0:
            loi.append("%s: sức chứa phải lớn hơn 0" % c["club_id"])
        du = int(c.get("reserve_capacity") or 0)
        if du < 0:
            loi.append("%s: chỉ tiêu dự trữ âm" % c["club_id"])
        if du > suc:
            loi.append("%s: chỉ tiêu dự trữ (%d) lớn hơn sức chứa (%d)"
                       % (c["club_id"], du, suc))
        if du > 0 and not (c.get("reserve_group") or "").strip():
            loi.append("%s: có chỉ tiêu dự trữ nhưng không ghi nhóm dự trữ"
                       % c["club_id"])

    # Khai buổi thì phải khai cho MỌI câu lạc bộ. Khai một nửa thì những câu
    # lạc bộ bỏ trống bị gom chung một buổi, và học sinh chỉ vào được một
    # trong số chúng — phần mềm cảnh báo đúng chuyện này.
    co_buoi = [c["club_id"] for c in clb if (c.get("buoi") or "").strip()]
    if co_buoi and len(co_buoi) != len(clb):
        loi.append("chỉ %d/%d câu lạc bộ khai buổi — khai thì phải khai hết, "
                   "hoặc bỏ trống hết" % (len(co_buoi), len(clb)))

    ma_hs = [h["student_id"] for h in hs]
    if len(ma_hs) != len(set(ma_hs)):
        loi.append("có mã học sinh bị trùng")

    for h in hs:
        sid = h["student_id"]
        if not sid:
            loi.append("có học sinh thiếu mã")
            continue

        for b, ds in (h.get("nguyen_vong") or {}).items():
            if len(ds) != len(set(ds)):
                loi.append("%s · %s: nguyện vọng trùng nhau" % (sid, b))
            if len(ds) > TRAN_NGUYEN_VONG_MOI_BUOI:
                loi.append("%s · %s: %d nguyện vọng, vượt trần %d mỗi buổi"
                           % (sid, b, len(ds), TRAN_NGUYEN_VONG_MOI_BUOI))
            for cid in ds:
                if cid not in tap_ma:
                    loi.append("%s · %s: mã '%s' không có trong danh sách câu lạc bộ"
                               % (sid, b, cid))
                elif buoi_cua[cid] != b:
                    loi.append("%s: %s nằm ở cột buổi %s nhưng sinh hoạt %s"
                               % (sid, cid, b, buoi_cua[cid] or "(không khai)"))

        theo_buoi = {}
        for cid in (h.get("diem") or {}):
            if cid not in tap_ma:
                loi.append("%s: chấm điểm cho mã '%s' không có thật" % (sid, cid))
                continue
            b = buoi_cua[cid]
            theo_buoi.setdefault(b, []).append(cid)
            # Diem cho mot CLB em khong xep nguyen vong la diem khong dung
            # toi — va gan nhu chac chan la go lech cot.
            if cid not in (h.get("nguyen_vong") or {}).get(b, []):
                loi.append("%s: dự thi %s nhưng không xếp nguyện vọng câu lạc bộ đó"
                           % (sid, cid))
        for b, ds in theo_buoi.items():
            if len(ds) > TRAN_CLB_THI_MOI_BUOI:
                loi.append("%s · %s: dự thi %d câu lạc bộ, vượt trần %d mỗi buổi"
                           % (sid, b, len(ds), TRAN_CLB_THI_MOI_BUOI))

    # Canh bao muc do "khong hong nhung nen biet" — van tra ve de nguoi dung
    # thay, nhung khong chan viec ghi.
    return loi


def canh_bao_men(clb, hs):
    """Những điều không sai nhưng nên biết trước khi chạy."""
    ra = []

    # Hai phia phai chuan hoa nhan buoi GIONG NHAU. Truong mot buoi thi cau
    # lac bo mang nhan rong con nguyen vong cung mang nhan rong; doi mot phia
    # thanh "__mac_dinh__" la hai ben khong con gap nhau, va bang canh bao noi
    # "0 em / 69 cho" — mot cau vo nghia, va vo nghia theo kieu nghe rat that.
    def nhan(b):
        return b or "__mac_dinh__"

    tong_cho = {}
    for c in clb:
        b = nhan(c.get("buoi"))
        tong_cho[b] = tong_cho.get(b, 0) + int(c["capacity"])
    muon = {}
    for h in hs:
        for b, ds in (h.get("nguyen_vong") or {}).items():
            if ds:
                muon[nhan(b)] = muon.get(nhan(b), 0) + 1
    for b in sorted(set(tong_cho) | set(muon)):
        cho, em = tong_cho.get(b, 0), muon.get(b, 0)
        if cho and em / cho > 3:
            ra.append("buổi %s chọi %.1f lần (%d em / %d chỗ) — sẽ có nhiều "
                      "em trượt buổi đó" % (b, em / cho, em, cho))
        if cho and em < cho * 0.5:
            ra.append("buổi %s thừa chỗ (%d em / %d chỗ)" % (b, em, cho))
    khong_nv = [h["student_id"] for h in hs
                if not any((h.get("nguyen_vong") or {}).values())]
    if khong_nv:
        ra.append("%d em không khai nguyện vọng nào cả tuần — các em đó chắc "
                  "chắn trắng tay" % len(khong_nv))
    return ra


# ---------------------------------------------------------------------------
# GHI
# ---------------------------------------------------------------------------

def thanh_so(clb, hs):
    """(clb, hs) của skill -> (clubs, students) cho `so_nhap.ghi_so_nhap`.

    Nguyện vọng các buổi nối thành MỘT danh sách theo thứ tự buổi: sổ nhập
    không chia cột theo buổi, phần mềm tự chia theo buổi của từng CLB.
    Điểm đặt ngay cạnh nguyện vọng của CLB đó.
    """
    ds_buoi = []
    for c in clb:                      # giu thu tu xuat hien, khong sap lai
        b = c.get("buoi") or ""
        if b not in ds_buoi:
            ds_buoi.append(b)
    clubs = [{
        "club_id": c["club_id"], "name": c.get("name") or c["club_id"],
        "capacity": int(c["capacity"]),
        "reserve_capacity": int(c.get("reserve_capacity") or 0),
        "reserve_group": c.get("reserve_group") or "", "buoi": c.get("buoi") or "",
    } for c in clb]
    students = []
    for h in hs:
        nv = h.get("nguyen_vong") or {}
        diem = h.get("diem") or {}
        thu_tu = [cid for b in ds_buoi + [b for b in nv if b not in ds_buoi]
                  for cid in nv.get(b, [])]
        students.append({
            "student_id": h["student_id"], "name": h.get("name") or "",
            "reserve_group": h.get("reserve_group") or "",
            "nv": [{"club_id": cid, "thi": cid in diem, "diem": diem.get(cid, "")}
                   for cid in thu_tu],
        })
    return clubs, students


def ghi_bo(thu_muc, clb, hs):
    """Ghi Sổ nhập CLB. GỌI SAU KHI soát() đã trả về rỗng. Trả [đường dẫn]."""
    os.makedirs(thu_muc, exist_ok=True)
    p = os.path.join(thu_muc, TEN_SO)
    clubs, students = thanh_so(clb, hs)
    so_nhap.ghi_so_nhap(p, clubs, students)
    return [p]


# ---------------------------------------------------------------------------
# ĐỌC LẠI một bộ đã có (cho chế độ `soat`)
# ---------------------------------------------------------------------------

def doc_so(duong):
    """Đọc một Sổ nhập CLB về đúng dạng (clb, hs) mà `soat` dùng."""
    import openpyxl

    wb = openpyxl.load_workbook(duong, read_only=True, data_only=True)
    try:
        if not so_nhap.la_so_nhap(wb.sheetnames):
            raise SystemExit("%s không phải Sổ nhập CLB" % duong)
        du = so_nhap.doc_so_nhap(wb)
    finally:
        wb.close()
    if du["loi"]:
        import i18n_errors
        raise SystemExit("Sổ nhập có lỗi:\n" + "\n".join(
            "   ✗ " + d for d in i18n_errors.format_all(du["loi"])))
    clb = [{k: c[k] for k in ("club_id", "name", "capacity", "reserve_capacity",
                              "reserve_group", "buoi")} for c in du["clubs"]]
    buoi_cua = {c["club_id"]: c["buoi"] for c in clb}
    hs = []
    for s in du["students"]:
        nv, diem = {}, {}
        for x in s["nv"]:
            nv.setdefault(buoi_cua.get(x["club_id"], ""), []).append(x["club_id"])
            if x["thi"]:
                diem[x["club_id"]] = x["diem"]
        hs.append({"student_id": s["student_id"], "name": s["name"],
                   "reserve_group": s["reserve_group"] or "", "nguyen_vong": nv, "diem": diem})
    return clb, hs


def doc_bo(thu_muc):
    """Đọc Sổ nhập CLB (tệp .xlsx, hoặc thư mục có SO_NHAP_CLB.xlsx), hoặc
    bộ ba CSV cũ trong thư mục."""
    if thu_muc.lower().endswith((".xlsx", ".xlsm")):
        return doc_so(thu_muc)
    if os.path.exists(os.path.join(thu_muc, TEN_SO)):
        return doc_so(os.path.join(thu_muc, TEN_SO))

    def doc(ten):
        p = os.path.join(thu_muc, ten)
        if not os.path.exists(p):
            raise SystemExit("Không thấy %s" % p)
        with io.open(p, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    clb = []
    for r in doc(TEN_TEP["clb"]):
        clb.append({
            "club_id": (r.get("club_id") or "").strip(),
            "name": (r.get("name") or "").strip(),
            "capacity": (r.get("capacity") or "0").strip(),
            "reserve_capacity": (r.get("reserve_capacity") or "0").strip() or 0,
            "reserve_group": (r.get("reserve_group") or "").strip(),
            "buoi": (r.get("buoi") or "").strip(),
        })

    hs = {}
    for r in doc(TEN_TEP["nv"]):
        sid = (r.get("student_id") or "").strip()
        em = hs.setdefault(sid, {"student_id": sid,
                                 "name": (r.get("name") or "").strip(),
                                 "reserve_group": (r.get("reserve_group") or "").strip(),
                                 "nguyen_vong": {}, "diem": {}})
        for k, v in r.items():
            if not k or not v or "_pref_" not in k:
                continue
            b = k.rsplit("_pref_", 1)[0]
            em["nguyen_vong"].setdefault(b, []).append(v.strip())

    for r in doc(TEN_TEP["thi"]):
        sid = (r.get("student_id") or "").strip()
        em = hs.setdefault(sid, {"student_id": sid, "name": "", "reserve_group": "",
                                 "nguyen_vong": {}, "diem": {}})
        for k, v in r.items():
            if k and k.startswith("test_club_") and v:
                so = k[len("test_club_"):]
                em["diem"][v.strip()] = (r.get("score_" + so) or "").strip()

    return clb, list(hs.values())


# ---------------------------------------------------------------------------
# SINH NGẪU NHIÊN nhưng HỢP LỆ
# ---------------------------------------------------------------------------

_HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đỗ", "Bùi", "Ngô",
       "Dương", "Lý", "Hồ", "Đặng", "Phan", "Trịnh", "Mai", "Chu", "Tạ"]
_DEM = ["Văn", "Thị", "Minh", "Gia", "Bảo", "Khánh", "Hoài", "Quốc", "Thanh", "Anh"]
_TEN = ["An", "Bình", "Chi", "Dũng", "Giang", "Hà", "Huy", "Khanh", "Lan",
        "Mai", "Nam", "Ngân", "Nhi", "Phúc", "Quân", "Sương", "Tuấn", "Uyên",
        "Việt", "Xuân", "Yến", "Linh", "Thảo", "Vy"]

_CHU_DE = [
    ("clb_bongro", "CLB Bóng rổ"), ("clb_bongda", "CLB Bóng đá"),
    ("clb_covua", "CLB Cờ vua"), ("clb_vanhoc", "CLB Văn học"),
    ("clb_tinhoc", "CLB Tin học"), ("clb_robotics", "CLB Robotics"),
    ("clb_mythuat", "CLB Mỹ thuật"), ("clb_amnhac", "CLB Âm nhạc"),
    ("clb_nauan", "CLB Nấu ăn"), ("clb_lamvuon", "CLB Làm vườn"),
    ("clb_tienganh", "CLB Tiếng Anh"), ("clb_khoahoc", "CLB Khoa học"),
    ("clb_nhiepanh", "CLB Nhiếp ảnh"), ("clb_khieuvu", "CLB Khiêu vũ"),
    ("clb_tranhbien", "CLB Tranh biện"), ("clb_tinhnguyen", "CLB Tình nguyện"),
    ("clb_dangian", "CLB Trò chơi dân gian"), ("clb_thuvien", "CLB Thư viện"),
    ("clb_bcs", "CLB Báo chí"), ("clb_coking", "CLB Cờ tướng"),
]


def sinh_ngau_nhien(n_hs, ds_buoi, clb_moi_buoi, seed, do_choi=1.15,
                    ti_le_du_tru=0.35, ti_le_co_thi=0.34):
    """Một trường ngẫu nhiên nhưng luôn hợp lệ. Tất định theo `seed`.

    `do_choi` — tổng chỗ so với số học sinh. 1.15 nghĩa là chỗ nhiều hơn nhu
    cầu 15%, đủ chật để kết quả có ý nghĩa, đủ rộng để không quá nửa trường
    trắng tay.
    """
    rnd = random.Random(seed)
    if clb_moi_buoi * len(ds_buoi) > len(_CHU_DE):
        raise SystemExit("Chỉ có %d chủ đề câu lạc bộ sẵn, không đủ cho %d câu lạc bộ"
                         % (len(_CHU_DE), clb_moi_buoi * len(ds_buoi)))

    chu_de = _CHU_DE[:]
    rnd.shuffle(chu_de)
    nhom_du_tru = ["chinh_sach", "khoi_10"]

    clb, k = [], 0
    for b in ds_buoi:
        # Tong cho moi buoi ~ n_hs * do_choi / so buoi, chia deu cho cac CLB
        cho_buoi = max(clb_moi_buoi, int(round(n_hs * do_choi / len(ds_buoi))))
        phan = [cho_buoi // clb_moi_buoi] * clb_moi_buoi
        for i in range(cho_buoi - sum(phan)):
            phan[i] += 1
        for i in range(clb_moi_buoi):
            cid, ten = chu_de[k]; k += 1
            suc = max(2, phan[i])
            co_du = rnd.random() < ti_le_du_tru
            clb.append({
                "club_id": cid, "name": ten, "capacity": suc,
                "reserve_capacity": max(1, int(suc * 0.2)) if co_du else 0,
                "reserve_group": rnd.choice(nhom_du_tru) if co_du else "",
                "buoi": b,
            })

    theo_buoi = {}
    for c in clb:
        theo_buoi.setdefault(c["buoi"], []).append(c["club_id"])
    co_thi = {c["club_id"] for c in clb if rnd.random() < ti_le_co_thi}

    # CHI GAN NHOM MA CO CAU LAC BO THAT SU DANH SUAT CHO.
    #
    # Gan bua tu bang `nhom_du_tru` thi gap truong hop khong cau lac bo nao
    # dat suat cho "khoi_10" — luc do nhung em mang nhan do co mot cai nhan
    # khong dem lai gi o bat ky dau. Phan mem goi do la "nhom mo coi" va
    # canh bao muc CAO, dung. Do duoc: truong 3 cau lac bo, 40 em -> 9 em
    # mang nhan mo coi va 2 canh bao khi nhap.
    nhom_co_that = sorted({c["reserve_group"] for c in clb if c["reserve_group"]})

    hs = []
    for i in range(1, n_hs + 1):
        sid = "HS%03d" % i
        ten = "%s %s %s" % (rnd.choice(_HO), rnd.choice(_DEM), rnd.choice(_TEN))
        nhom = (rnd.choice(nhom_co_that)
                if nhom_co_that and rnd.random() < 0.22 else "")
        nv, diem = {}, {}
        for b, ds in theo_buoi.items():
            # Mot so em bo trong ca mot buoi — ngay do em ban. Day la du lieu
            # HOP LE, khong phai thieu sot.
            if rnd.random() < 0.12:
                nv[b] = []
                continue
            k_nv = min(len(ds), rnd.randint(1, min(3, len(ds))))
            chon = rnd.sample(ds, k_nv)
            nv[b] = chon
            # Chi cham diem cho CLB em CO khai nguyen vong va CLB do co thi
            for cid in chon:
                if cid in co_thi and rnd.random() < 0.8:
                    if len([c for c in diem if c in theo_buoi[b]]) < TRAN_CLB_THI_MOI_BUOI:
                        # Dau phay thap phan — dung cach Excel ban tieng Viet luu
                        diem[cid] = "%.1f" % rnd.uniform(4.0, 10.0).__round__(1)
                        diem[cid] = diem[cid].replace(".", ",")

        # MOI EM PHAI KHAI IT NHAT MOT NGUYEN VONG CA TUAN.
        #
        # Bo trong MOT buoi la "ngay do em ban" — hop le. Bo trong MOI buoi
        # la "em khong dang ky gi ca", va phan mem canh bao dung: em do chac
        # chan trang tay, khong phai vi thua ai ma vi chua bao gio vao cuoc.
        # O truong mot buoi, xac suat 12% ay ap len ca "tuan", nen khong chan
        # thi cu 100 em lai co ~12 em nhu vay.
        if not any(nv.values()):
            b = rnd.choice(list(theo_buoi))
            nv[b] = [rnd.choice(theo_buoi[b])]

        hs.append({"student_id": sid, "name": ten, "reserve_group": nhom,
                   "nguyen_vong": nv, "diem": diem})

    # VA CHIEU NGUOC LAI: moi nhom co cau lac bo dat suat thi phai co NGUOI.
    #
    # Day la mat guong cua khoi tren. Mot cau lac bo giu 1 cho cho
    # "chinh_sach" ma ca truong khong em nao thuoc dien do thi cho ay khong
    # ai nhan duoc — phan mem canh bao `health_club_group_no_students`, dung.
    # Truong it hoc sinh moi gap: 20 em, moi em 22% co nhom, boc ra toan
    # "khoi_10" la chuyen binh thuong. Do duoc: 1 tren 90 cau hinh da thu.
    for g in nhom_co_that:
        if any(h["reserve_group"] == g for h in hs):
            continue
        # Uu tien em CHUA co nhom de khong cuop nhan cua nhom khac.
        chua = [h for h in hs if not h["reserve_group"]] or hs
        rnd.choice(chua)["reserve_group"] = g

    return clb, hs


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _in_ket_qua(clb, hs, loi, canh_bao):
    if loi:
        print("KHÔNG HỢP LỆ — %d lỗi:" % len(loi), file=sys.stderr)
        for e in loi:
            print("   ✗", e, file=sys.stderr)
        return 1
    print("Hợp lệ: %d câu lạc bộ · %d buổi · %d học sinh · %d ô điểm"
          % (len(clb), len({c.get("buoi") or "" for c in clb}), len(hs),
             sum(len(h.get("diem") or {}) for h in hs)))
    for w in canh_bao:
        print("   ⚠", w)
    return 0


def main(argv=None):
    # Cua so lenh / ong dan tren Windows mac dinh la cp1252: in tieng Viet
    # se nem UnicodeEncodeError va script thoat voi ma 1.
    for _luong in (sys.stdout, sys.stderr):
        if hasattr(_luong, "reconfigure"):
            _luong.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="lenh", required=True)

    a = sub.add_parser("tao", help="dựng từ bản khai báo JSON")
    a.add_argument("--spec", required=True)
    a.add_argument("--ra", required=True)

    b = sub.add_parser("ngau", help="dựng một trường ngẫu nhiên nhưng hợp lệ")
    b.add_argument("--ra", required=True)
    b.add_argument("--hoc-sinh", type=int, default=120)
    b.add_argument("--buoi", default="", help="vd thu_2,thu_4,thu_6 — bỏ trống = một buổi")
    b.add_argument("--clb-moi-buoi", type=int, default=3)
    b.add_argument("--seed", type=int, default=42)
    b.add_argument("--do-choi", type=float, default=1.15)

    c = sub.add_parser("soat", help="soát một sổ nhập (hoặc bộ ba CSV cũ), không sửa gì")
    c.add_argument("thu_muc", help="tệp SO_NHAP_CLB.xlsx, hoặc thư mục chứa nó / bộ ba CSV")

    ns = p.parse_args(argv)

    if ns.lenh == "soat":
        clb, hs = doc_bo(ns.thu_muc)
        return _in_ket_qua(clb, hs, soat(clb, hs), canh_bao_men(clb, hs))

    if ns.lenh == "tao":
        with io.open(ns.spec, encoding="utf-8") as f:
            spec = json.load(f)
        clb, hs = spec["cau_lac_bo"], spec["hoc_sinh"]
    else:
        ds_buoi = [x.strip() for x in ns.buoi.split(",") if x.strip()] or [""]
        la = [b for b in ds_buoi if b and b not in BUOI_CHUAN]
        if la:
            print("Nhãn buổi lạ: %s (nên dùng: %s)" % (", ".join(la),
                  ", ".join(BUOI_CHUAN)), file=sys.stderr)
        clb, hs = sinh_ngau_nhien(ns.hoc_sinh, ds_buoi, ns.clb_moi_buoi,
                                  ns.seed, ns.do_choi)

    loi = soat(clb, hs)
    ma = _in_ket_qua(clb, hs, loi, canh_bao_men(clb, hs))
    if ma:
        print("\nKhông ghi tệp nào.", file=sys.stderr)
        return ma
    for d in ghi_bo(ns.ra, clb, hs):
        print("   →", d)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
