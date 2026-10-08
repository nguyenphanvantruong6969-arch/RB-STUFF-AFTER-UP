# -*- coding: utf-8 -*-
"""Bốn hàm đọc mới của thẻ Kết quả: nhu cầu từng câu lạc bộ, danh sách thành
viên, phân bố nguyện vọng, em chưa có chỗ, và mức dùng suất dự trữ.

CÁI BẪY TRUNG TÂM. `preferences.rank` là số **1..n chạy suốt** qua tất cả các
buổi nối liền nhau, không phải thứ hạng trong từng buổi — chính
`import_preferences_csv` ghi vậy. Nên câu truy vấn tự nhiên nhất cho "bao
nhiêu em đặt câu lạc bộ này làm nguyện vọng 1", tức `WHERE p.rank = 1`, là
SAI, và sai âm thầm: nó chỉ bắt được nguyện vọng đầu tiên của cả tuần.

Đo trên bộ `bo_nhieu_buoi` (160 em, 5 buổi), tính thẳng từ tệp CSV không qua
phần mềm:

    buổi     `WHERE rank=1` đếm ra     số em THẬT SỰ đặt NV1 ở buổi đó
    thứ 2              111                        111
    thứ 3               44                        135
    thứ 4                5                        132
    thứ 5                0                        121
    thứ 6                0                         57

Thứ Năm và thứ Sáu sẽ hiện SỐ KHÔNG — một bảng nói rằng không em nào tha
thiết với hai buổi ấy, trong khi thật ra có 178 em. `test_dat_nv1_khong_rong_o_moi_buoi`
ghim đúng năm con số cột phải, nên hạ về `WHERE rank = 1` là đỏ ngay.

Hai trường hợp bộ dữ liệu lớn KHÔNG chạm tới nên phải dựng riêng:

* **nguyện vọng 4 trở lên** — bộ lớn dừng ở nguyện vọng 3, nên nhóm "4+"
  luôn bằng 0 và việc gộp đúng hay sai đều cho cùng kết quả;
* **suất dự trữ bị bỏ phí** — bộ lớn dùng hết sạch suất dự trữ
  (`con_thua = 0` ở cả 6 câu lạc bộ), nên con số đáng giá nhất của mục ấy
  chưa từng khác 0.

ĐỐI CHỨNG NGƯỢC đã chạy thật — kết quả ghi ở cuối tệp.
"""

import csv
import io
import os
import re

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_NHIEU_BUOI = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")
# KHONG PHAI vi_du_day_du: bo do co cot `buoi` voi ba gia tri, tuc la mot
# truong BA BUOI. `bo_sach` khong co cot `buoi` nao ca — day moi la truong
# mot buoi that, va la bo duy nhat di qua duoc duong `COALESCE(buoi, ...)`.
BO_MOT_BUOI = os.path.join(GOC, "du_lieu_test", "bo_sach")

# Do doc lap tu tep CSV (xem docstring). Ghim ca nam de mot thay doi im
# lang o cach xep hang khong the troi qua.
NV1_THEO_BUOI = {"thu_2": 111, "thu_3": 135, "thu_4": 132,
                 "thu_5": 121, "thu_6": 57}


def _nap(api, thu_muc, tep):
    for ten in tep:
        with io.open(os.path.join(thu_muc, ten), encoding="utf-8-sig") as f:
            kq = api.import_csv_auto(f.read())
        assert kq["ok"], (ten, kq)


@pytest.fixture
def api_nhieu_buoi(api):
    _nap(api, BO_NHIEU_BUOI, ("NHIEUBUOI_01_danh_sach_CLB.csv",
                              "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                              "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"))
    assert api.run_pipeline(seed=42)["ok"]
    return api


@pytest.fixture
def api_mot_buoi(api):
    _nap(api, BO_MOT_BUOI, ("SACH_01_danh_sach_CLB.csv",
                            "SACH_02_chon_CLB_muon_thi.csv",
                            "SACH_03_xep_hang_nguyen_vong.csv"))
    assert api.run_pipeline(seed=42)["ok"]
    return api


# ------------------------------------------------------------------ #
# 1. XẾP HẠNG PHẢI TÍNH THEO TỪNG BUỔI
# ------------------------------------------------------------------ #

def test_dat_nv1_khong_rong_o_moi_buoi(api_nhieu_buoi):
    """Test giết câu truy vấn ngây thơ. `WHERE rank = 1` cho thứ 5 và thứ 6
    ra 0; con số đúng là 121 và 57."""
    lap = api_nhieu_buoi.get_club_fill_stats()
    assert lap["ok"], lap

    theo_buoi = {}
    for c in lap["data"]:
        theo_buoi[c["buoi"]] = theo_buoi.get(c["buoi"], 0) + c["so_dat_nv1"]

    assert theo_buoi == NV1_THEO_BUOI, theo_buoi
    for b, n in theo_buoi.items():
        assert n > 0, "buoi %s bao 0 em dat nguyen vong 1" % b


def test_dat_nv1_khop_voi_so_em_khai_o_buoi_do(api_nhieu_buoi):
    """Mỗi em khai nguyện vọng ở một buổi thì có ĐÚNG MỘT nguyện vọng 1 ở
    buổi ấy. Nên tổng cột NV1 của một buổi phải bằng số em khai gì đó ở
    buổi ấy — tính lại bằng một đường hoàn toàn khác."""
    with api_nhieu_buoi._ket_noi_doc() as cur:
        that = dict(cur.execute("""
            SELECT COALESCE(c.buoi, '__mac_dinh__') AS b,
                   COUNT(DISTINCT p.student_id)
            FROM preferences p JOIN clubs c ON c.club_id = p.club_id
            GROUP BY b
        """).fetchall())

    tu_ham = {}
    for c in api_nhieu_buoi.get_club_fill_stats()["data"]:
        tu_ham[c["buoi"]] = tu_ham.get(c["buoi"], 0) + c["so_dat_nv1"]

    assert tu_ham == that, (tu_ham, that)


def test_so_dang_ky_dem_theo_em_khong_theo_luot(api_nhieu_buoi):
    for c in api_nhieu_buoi.get_club_fill_stats()["data"]:
        with api_nhieu_buoi._ket_noi_doc() as cur:
            n = cur.execute(
                "SELECT COUNT(DISTINCT student_id) FROM preferences WHERE club_id = ?",
                (c["club_id"],)).fetchone()[0]
        assert c["so_dang_ky"] == n, c["club_id"]
        assert c["so_dat_nv1"] <= c["so_dang_ky"], c["club_id"]


def test_ti_le_choi_la_none_khi_khong_co_chi_tieu(api):
    """0 ở cột tỉ lệ chọi đọc ra nghĩa ngược hẳn với 'không có chỗ nào'."""
    api.create_or_update_club("clb_rong", "CLB Rỗng", capacity=1)
    with api._ket_noi_ghi() as cur:
        # CSDL mới từ chối sức chứa 0 (CHECK); CSDL cũ chưa di trú vẫn có thể
        # còn dòng đó, nên tắt CHECK để dựng lại đúng tình huống.
        cur.execute("PRAGMA ignore_check_constraints = ON")
        cur.execute("UPDATE clubs SET capacity = 0 WHERE club_id = 'clb_rong'")
    c = [x for x in api.get_club_fill_stats()["data"]
         if x["club_id"] == "clb_rong"][0]
    assert c["ti_le_choi"] is None


# ------------------------------------------------------------------ #
# 2. DANH SÁCH THÀNH VIÊN — PHẢI KHỚP HAI CHIỀU
# ------------------------------------------------------------------ #

def test_danh_sach_clb_khop_hai_chieu_voi_bang_ket_qua(api_nhieu_buoi):
    """Hai chiều của cùng một sự thật. Lệch một em là một em bị bỏ quên khi
    thầy cô phụ trách điểm danh."""
    theo_clb = {}
    for r in api_nhieu_buoi.get_match_results()["data"]:
        if r["club_id"]:
            theo_clb.setdefault(r["club_id"], set()).add(r["student_id"])

    assert theo_clb, "khong co ket qua nao de doi chieu"
    for clb, mong_doi in theo_clb.items():
        kq = api_nhieu_buoi.get_danh_sach_clb(clb)
        assert kq["ok"], (clb, kq)
        that = {t["student_id"] for t in kq["data"]["thanh_vien"]}
        assert that == mong_doi, (clb, that ^ mong_doi)


def test_so_thanh_vien_khop_cot_da_xep(api_nhieu_buoi):
    for c in api_nhieu_buoi.get_club_fill_stats()["data"]:
        kq = api_nhieu_buoi.get_danh_sach_clb(c["club_id"])
        assert len(kq["data"]["thanh_vien"]) == c["matched"], c["club_id"]


def test_danh_sach_clb_bao_loi_khi_ma_khong_co_that(api_nhieu_buoi):
    kq = api_nhieu_buoi.get_danh_sach_clb("clb_khong_ton_tai")
    assert not kq["ok"]


# ------------------------------------------------------------------ #
# 3. PHÂN BỐ NGUYỆN VỌNG
# ------------------------------------------------------------------ #

def test_phan_bo_nguyen_vong_cong_khop_so_cho_da_xep(api_nhieu_buoi):
    d = api_nhieu_buoi.get_phan_bo_nguyen_vong()["data"]
    with api_nhieu_buoi._ket_noi_doc() as cur:
        da_xep = cur.execute(
            "SELECT COUNT(*) FROM match_results WHERE club_id IS NOT NULL"
        ).fetchone()[0]
    assert sum(h["so_em"] for h in d["phan_bo"]) + d["khong_ro"] == da_xep
    assert d["tong_da_xep"] == da_xep


def test_nhom_bon_tro_len_gop_ca_hang_5_den_10(api):
    """Trường cho khai tới 10 nguyện vọng mỗi buổi. Gộp "4 trở lên" bằng
    cách lấy đúng hạng 4 thì bảng này hụt mất người — mà bộ dữ liệu lớn
    dừng ở hạng 3 nên không bao giờ lộ ra.

    Dựng năm câu lạc bộ sức chứa 1 và năm em xếp hạng y hệt nhau: em cuối
    cùng chắc chắn phải nhận nguyện vọng thứ 5.
    """
    ds = ["clb_a", "clb_b", "clb_c", "clb_d", "clb_e"]
    for i, c in enumerate(ds):
        assert api.create_or_update_club(c, "CLB %d" % i, capacity=1)["ok"]
    for i in range(5):
        sid = "HS%02d" % i
        assert api.create_student_if_missing(sid, "Em %d" % i)["ok"]
        assert api.submit_preferences(sid, ds)["ok"]
    assert api.run_pipeline(seed=1)["ok"]

    d = api.get_phan_bo_nguyen_vong()["data"]
    gop = [h for h in d["phan_bo"] if h["gop"]][0]
    assert gop["so_em"] == 2, d["phan_bo"]      # hang 4 va hang 5
    assert d["tong_da_xep"] == 5


# ------------------------------------------------------------------ #
# 4. EM CHƯA CÓ CHỖ
# ------------------------------------------------------------------ #

def test_em_chua_co_cho_khop_con_so_cua_do_phu(api_nhieu_buoi):
    """Hai mục nằm cạnh nhau trên cùng một màn hình. Nói hai con số khác
    nhau cho cùng một câu hỏi là hỏng, kể cả khi cả hai đều 'gần đúng'."""
    a = api_nhieu_buoi.get_em_chua_co_cho()["data"]
    b = api_nhieu_buoi.get_do_phu()["data"]
    assert a["so_em"] == b["so_em_trang_tay"]
    assert {e["student_id"] for e in a["danh_sach"]} >= {
        e["student_id"] for e in b["em_trang_tay"]}


def test_em_chua_co_cho_that_su_khong_co_cho_nao(api_nhieu_buoi):
    co_cho = {r["student_id"]
              for r in api_nhieu_buoi.get_match_results()["data"] if r["club_id"]}
    for e in api_nhieu_buoi.get_em_chua_co_cho()["data"]["danh_sach"]:
        assert e["student_id"] not in co_cho, e["student_id"]


def test_em_chua_co_cho_kem_dung_nguyen_vong_da_khai(api_nhieu_buoi):
    """Danh sách tên rồi im lặng thì nhà trường không xử lý tiếp được."""
    ds = api_nhieu_buoi.get_em_chua_co_cho()["data"]["danh_sach"]
    assert ds, "bo du lieu nay phai co em trang tay"
    for e in ds:
        with api_nhieu_buoi._ket_noi_doc() as cur:
            n = cur.execute(
                "SELECT COUNT(*) FROM preferences WHERE student_id = ?",
                (e["student_id"],)).fetchone()[0]
        assert e["so_nguyen_vong"] == n == len(e["da_khai"]), e["student_id"]
    # Ti le choi phai di kem, neu khong khong biet em ay truot vi sao.
    co_choi = [k for e in ds for k in e["da_khai"] if k["ti_le_choi"] is not None]
    assert co_choi, "khong nguyen vong nao kem ti le choi"


# ------------------------------------------------------------------ #
# 5. SUẤT DỰ TRỮ
# ------------------------------------------------------------------ #

def test_suat_du_tru_cong_khop_chi_tieu(api_nhieu_buoi):
    ds = api_nhieu_buoi.get_suat_du_tru()["data"]
    assert ds, "bo du lieu nay phai co CLB co du tru"
    for r in ds:
        assert r["da_dung"] + r["con_thua"] == r["reserve_capacity"], r["club_id"]
        assert r["reserve_capacity"] > 0


def test_suat_du_tru_bi_bo_phi_thi_dem_duoc(api):
    """Con số đáng giá nhất của mục này là SUẤT BỊ BỎ PHÍ — mà bộ dữ liệu
    lớn dùng hết sạch suất dự trữ nên nó chưa từng khác 0 ở đó.

    Một câu lạc bộ để dành 3 suất cho một nhóm KHÔNG EM NÀO thuộc về: cơ
    chế vẫn chạy đúng, ba suất lặng lẽ thành suất thường, và không gì báo
    cho nhà trường biết ý định chính sách vừa bốc hơi.
    """
    assert api.create_or_update_club(
        "clb_x", "CLB X", capacity=5,
        reserve_capacity=3, reserve_group="khong_ai_thuoc")["ok"]
    for i in range(4):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["clb_x"])
    assert api.run_pipeline(seed=1)["ok"]

    r = api.get_suat_du_tru()["data"][0]
    assert r["nhom_dang_ky"] == 0
    assert r["da_dung"] == 0
    assert r["con_thua"] == 3, r


# ------------------------------------------------------------------ #
# 6. TRƯỜNG MỘT BUỔI CŨNG PHẢI CHẠY
# ------------------------------------------------------------------ #

def test_ca_bon_ham_chay_duoc_o_truong_mot_buoi(api_mot_buoi):
    """Trường một buổi KHÔNG CÓ cột `buoi` trong tệp câu lạc bộ, nên cột ấy
    trong cơ sở dữ liệu là NULL. Mọi câu truy vấn ở đây phải `COALESCE` nó
    về nhãn mặc định — bỏ sót một chỗ thì cả trường rơi ra ngoài bảng mà
    không có lỗi nào.

    Bộ dùng ở đây phải là `bo_sach`. `vi_du_day_du` trông như một bộ "đơn
    giản" nhưng có cột `buoi` với ba giá trị, nên nó KHÔNG đi qua đường
    NULL và một test dùng nó sẽ xanh dù `COALESCE` có bị bỏ hay không.
    """
    with api_mot_buoi._ket_noi_doc() as cur:
        n_null = cur.execute(
            "SELECT COUNT(*) FROM clubs WHERE buoi IS NULL OR buoi = ''"
        ).fetchone()[0]
    assert n_null > 0, "bo du lieu nay khong con di qua duong NULL nua"

    lap = api_mot_buoi.get_club_fill_stats()
    assert lap["ok"] and lap["data"]
    assert all(c["buoi"] for c in lap["data"]), "co CLB roi ra ngoai vi buoi rong"
    assert sum(c["so_dang_ky"] for c in lap["data"]) > 0

    assert api_mot_buoi.get_phan_bo_nguyen_vong()["ok"]
    assert api_mot_buoi.get_em_chua_co_cho()["ok"]
    assert api_mot_buoi.get_suat_du_tru()["ok"]
    clb = lap["data"][0]["club_id"]
    assert api_mot_buoi.get_danh_sach_clb(clb)["ok"]


# ------------------------------------------------------------------ #
# 7. TỆP XUẤT RA PHẢI NÓI CÙNG CON SỐ VỚI MÀN HÌNH
#
# Đây đúng loại lệch kho này đã gặp một lần: ba tài liệu cùng dẫn một con
# số TN7a đã cũ. Màn hình và tệp đọc chung bốn hàm ở trên, và test này canh
# rằng chúng thật sự chung.
# ------------------------------------------------------------------ #

def test_tep_tong_hop_co_du_bon_muc_moi(api_nhieu_buoi, tmp_path):
    d = api_nhieu_buoi.export_csv(str(tmp_path / "kq.csv"))["data"]
    with io.open(d["tong_hop_path"], encoding="utf-8-sig") as f:
        noi_dung = f.read()

    for tieu_de in ("TỪNG CÂU LẠC BỘ",
                    "NGUYỆN VỌNG THỨ MẤY THÌ ĐƯỢC",
                    "SUẤT DỰ TRỮ DÙNG TỚI ĐÂU",
                    "HỌC SINH CHƯA CÓ CÂU LẠC BỘ NÀO"):
        assert tieu_de in noi_dung, tieu_de

    # Cau canh bao phai di CUNG bang, khong phai nam o mot tai lieu khac.
    assert "KHÔNG cộng dồn" in noi_dung


def test_con_so_trong_tep_khop_con_so_ham_doc_tra_ve(api_nhieu_buoi, tmp_path):
    d = api_nhieu_buoi.export_csv(str(tmp_path / "kq.csv"))["data"]
    with io.open(d["tong_hop_path"], encoding="utf-8-sig") as f:
        dong = list(csv.reader(f))

    # KHOANH DUNG PHAN. Phan "suat du tru" cung co ma cau lac bo o cot 1
    # nhung y nghia cac cot sau khac han; quet ca tep thi phan sau de len
    # phan truoc va test doc nham bang. (Da vap dung cai nay mot lan.)
    dau = next(i for i, r in enumerate(dong)
               if r and r[0].startswith("TỪNG CÂU LẠC BỘ"))
    cuoi = next(i for i in range(dau + 2, len(dong)) if not dong[i])

    theo_ma = {r[1]: r for r in dong[dau + 2:cuoi]}
    assert len(theo_ma) == len(api_nhieu_buoi.get_club_fill_stats()["data"])
    for c in api_nhieu_buoi.get_club_fill_stats()["data"]:
        r = theo_ma.get(c["club_id"])
        assert r, c["club_id"]
        assert r[3] == str(c["so_dang_ky"]), (c["club_id"], r[3])
        assert r[4] == str(c["so_dat_nv1"]), (c["club_id"], r[4])
        assert r[6] == str(c["matched"]), (c["club_id"], r[6])


def _bang_clb_trong_thong_ke(ws):
    """(tiêu đề cột, các dòng) của bảng "Từng câu lạc bộ" trên trang Thống kê."""
    dong = [list(r) for r in ws.iter_rows(values_only=True)]
    i = next(n for n, r in enumerate(dong) if "Tỉ lệ chọi" in r)
    j = next((n for n in range(i + 1, len(dong)) if not any(dong[n])), len(dong))
    return dong[i], dong[i + 1:j]


def test_so_excel_co_trang_thong_ke_va_chua_co_cho(api_nhieu_buoi, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    d = api_nhieu_buoi.export_csv(str(tmp_path / "kq.csv"))["data"]
    assert d["excel_path"], "khong xuat duoc so Excel"
    wb = openpyxl.load_workbook(d["excel_path"])
    for trang in ("Thống kê", "Chưa có chỗ"):
        assert trang in wb.sheetnames, (trang, wb.sheetnames)

    # Bang "Tung cau lac bo" phai du dong cho MOI cau lac bo.
    _, dong = _bang_clb_trong_thong_ke(wb["Thống kê"])
    assert len(dong) == len(api_nhieu_buoi.get_club_fill_stats()["data"])


# ------------------------------------------------------------------ #
# 8. SỐ TRONG TỆP PHẢI VIẾT THEO KIỂU VIỆT NAM
#
# Tệp `.csv` này mở bằng Excel trên máy cài tiếng Việt, mà ở đó dấu CHẤM là
# dấu phân cách HÀNG NGHÌN. Màn hình viết `2,33` còn tệp viết `2.33` là hai
# bên nói hai con số khác nhau về cùng một thứ — và bên sai là bên người ta
# mang đi họp.
# ------------------------------------------------------------------ #

def test_khong_so_thap_phan_nao_trong_tep_dung_dau_cham(api_nhieu_buoi, tmp_path):
    d = api_nhieu_buoi.export_csv(str(tmp_path / "kq.csv"))["data"]
    with io.open(d["tong_hop_path"], encoding="utf-8-sig") as f:
        dong = list(csv.reader(f))

    xau = []
    for r in dong:
        for o in r:
            # Chi soi nhung o TOAN LA SO (ke ca kem dau %): ten tep, mo ta,
            # nhan buoi... duoc phep co dau cham.
            lot = o.strip().rstrip("%")
            if lot and re.fullmatch(r"\d+\.\d+", lot):
                xau.append(o)
    assert xau == [], "cac o dung dau cham thap phan: %s" % xau[:10]


def test_ti_le_choi_va_phan_tram_van_doc_ra_dung_so(api_nhieu_buoi, tmp_path):
    """Đổi dấu không được làm mất con số: `4,61` phải vẫn là 4,61."""
    d = api_nhieu_buoi.export_csv(str(tmp_path / "kq.csv"))["data"]
    with io.open(d["tong_hop_path"], encoding="utf-8-sig") as f:
        dong = list(csv.reader(f))

    dau = next(i for i, r in enumerate(dong)
               if r and r[0].startswith("TỪNG CÂU LẠC BỘ"))
    cuoi = next(i for i in range(dau + 2, len(dong)) if not dong[i])
    theo_ma = {r[1]: r for r in dong[dau + 2:cuoi]}

    for c in api_nhieu_buoi.get_club_fill_stats()["data"]:
        if c["ti_le_choi"] is None:
            continue
        assert theo_ma[c["club_id"]][5] == str(c["ti_le_choi"]).replace(".", ","), (
            c["club_id"], theo_ma[c["club_id"]][5], c["ti_le_choi"])


def test_so_excel_van_giu_so_that_khong_bien_thanh_chu(api_nhieu_buoi, tmp_path):
    """Chỉ tệp `.csv` đổi sang dấu phẩy. Trang dữ liệu trong sổ Excel phải
    giữ kiểu SỐ — biến thành chữ là làm hỏng sắp xếp và tính toán, mà Excel
    vốn tự hiển thị theo máy người dùng nên không cần đổi gì."""
    openpyxl = pytest.importorskip("openpyxl")
    d = api_nhieu_buoi.export_csv(str(tmp_path / "kq.csv"))["data"]
    tieu_de, dong = _bang_clb_trong_thong_ke(
        openpyxl.load_workbook(d["excel_path"])["Thống kê"])
    cot = tieu_de.index("Tỉ lệ chọi")
    gia_tri = [r[cot] for r in dong]
    assert gia_tri and all(isinstance(v, (int, float)) for v in gia_tri), gia_tri


# ====================================================================== #
# ĐỐI CHỨNG NGƯỢC — đã chạy thật trên 15 test của tệp này.
#
#   1. `ROW_NUMBER() OVER (PARTITION BY student_id, buoi)` -> `p.rank`
#      -> 2 ĐỎ, đúng hai test xếp hạng theo buổi. Đây là cái bẫy trung
#         tâm mô tả ở đầu tệp, và nó đỏ vì đúng lý do: thứ 5 và thứ 6 tụt
#         về 0.
#
#   2. Bỏ `COALESCE` ở cột `buoi` (giữ nguyên số tham số, để lỗi là lỗi
#      NGỮ NGHĨA chứ không phải lỗi ràng buộc tham số)
#      -> 1 ĐỎ, đúng test trường một buổi.
#
#      Lần chạy ĐẦU của đối chứng này cho 7 đỏ và em đã ghi nhầm đó là
#      "cột ấy được nhiều chỗ dựa vào hơn là nhìn code thấy được". Sai:
#      bỏ một `?` làm lệch số tham số, câu truy vấn ném lỗi, và 7 test đỏ
#      vì CÂU TRUY VẤN HỎNG chứ không vì `buoi` sai. Phá đúng chỗ thì chỉ
#      1 đỏ — và đó mới là con số nói lên điều gì.
#
#      Cùng lúc đó lộ ra một lỗi trong chính bộ test này: fixture
#      `api_mot_buoi` dùng `mau_csv/vi_du_day_du`, mà bộ ấy có cột `buoi`
#      với BA giá trị. Test mang tên "trường một buổi" nhưng chưa từng đi
#      qua đường NULL. Đã đổi sang `du_lieu_test/bo_sach` (không có cột
#      `buoi`) và thêm một assert canh rằng bộ dữ liệu còn đi qua đường ấy
#      thật, để lần sau đổi bộ mà quên thì test tự kêu.
#
#   3. Gộp "4 trở lên" bằng `dem.get(4)` thay vì tổng các hạng >= 4
#      -> 1 ĐỎ, đúng test dựng riêng cho nó. Bộ dữ liệu lớn dừng ở hạng 3
#         nên KHÔNG test nào khác thấy được — đúng lý do phải dựng một
#         trường năm câu lạc bộ sức chứa 1.
#
#   5. Bỏ đổi dấu thập phân trong `_so_vn` (quay lại viết `2.33`)
#      -> 2 ĐỎ. Lỗi này CÓ SẴN từ trước ở bảng "Tải từng buổi", không phải
#         do lượt này gây ra — nhưng sửa một chỗ mà bỏ chỗ kia thì tự tạo
#         ra lệch mới, nên sửa cả hai trong cùng một lượt.
#
# Khôi phục cả năm -> 21 xanh.
# ====================================================================== #
