"""Đọc thẳng file Excel (.xlsx), không bắt người dùng chuyển sang CSV.

VÌ SAO: Microsoft Forms xuất kết quả ra .xlsx. Trước đây người vận hành
phải mở Excel → File → Save As → chọn đúng "CSV UTF-8" → rồi mới nạp
được. Bước thừa đó lại chính là bước dễ sai nhất: chọn nhầm "CSV
(Comma delimited)" thường là tên tiếng Việt hỏng hết dấu, và Excel còn
chèn thêm BOM khiến bản cũ báo thiếu cột student_id.

Bỏ hẳn bước chuyển đổi thì cả lớp lỗi đó biến mất.

Các quy tắc dưới đây khoá đúng những chỗ .xlsx khác CSV: ô số đọc lên
là số chứ không phải chuỗi, sổ tính có nhiều sheet, và ô trống là None
chứ không phải "".
"""

import base64
import io

import pytest

openpyxl = pytest.importorskip("openpyxl", reason="chưa cài openpyxl")


def lam_xlsx(rows, ten_sheet="Sheet1", them_sheet=None):
    """Dựng một file .xlsx trong bộ nhớ, trả về chuỗi base64 như trình
    duyệt gửi lên."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = ten_sheet
    for r in rows:
        ws.append(r)
    if them_sheet:
        ws2 = wb.create_sheet(them_sheet[0])
        for r in them_sheet[1]:
            ws2.append(r)
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.fixture
def api_co_club(api):
    for cid, ten in [("clb_bongro", "CLB Bóng rổ"), ("clb_amnhac", "CLB Âm nhạc"),
                     ("clb_tienganh", "CLB Tiếng Anh")]:
        api.create_or_update_club(cid, ten, 20, 5, "chinh_sach")
    return api


# ------------------------------------------------------------------ #
# ĐỌC FILE
# ------------------------------------------------------------------ #


def test_doc_xlsx_ra_dung_noi_dung_csv(api):
    b64 = lam_xlsx([
        ["student_id", "name", "pref_1"],
        ["HS001", "Nguyễn Văn An", "clb_bongro"],
    ])
    res = api.xlsx_to_csv_text(b64)
    assert res["ok"] is True, res["errors"]
    text = res["data"]["csv_text"]
    assert "student_id,name,pref_1" in text
    assert "HS001,Nguyễn Văn An,clb_bongro" in text


def test_o_SO_khong_bien_thanh_20_0(api):
    """Excel lưu chỉ tiêu là số thực; đọc thô ra sẽ thành '20.0' và
    int('20.0') ném ValueError -> cả dòng CLB bị bỏ qua."""
    b64 = lam_xlsx([
        ["club_id", "name", "capacity", "reserve_capacity"],
        ["clb_a", "CLB A", 20, 5],
    ])
    text = api.xlsx_to_csv_text(b64)["data"]["csv_text"]
    assert "clb_a,CLB A,20,5" in text
    assert "20.0" not in text


def test_o_trong_thanh_chuoi_rong_chu_khong_phai_chu_None(api):
    b64 = lam_xlsx([
        ["student_id", "name", "pref_1", "pref_2"],
        ["HS001", "Nguyễn Văn An", "clb_bongro", None],
    ])
    text = api.xlsx_to_csv_text(b64)["data"]["csv_text"]
    assert "None" not in text
    assert text.strip().endswith("clb_bongro,")


def test_bo_qua_dong_trong_hoan_toan(api):
    """Excel hay để lại vài dòng rỗng ở cuối bảng."""
    b64 = lam_xlsx([
        ["student_id", "name", "pref_1"],
        ["HS001", "Nguyễn Văn An", "clb_bongro"],
        [None, None, None],
        [None, None, None],
    ])
    text = api.xlsx_to_csv_text(b64)["data"]["csv_text"]
    assert len([d for d in text.strip().split("\n") if d.strip(",")]) == 2


def test_khoang_trang_thua_hai_dau_bi_cat(api):
    b64 = lam_xlsx([
        ["student_id ", " name"],
        [" HS001", "Nguyễn Văn An "],
    ])
    text = api.xlsx_to_csv_text(b64)["data"]["csv_text"]
    assert "student_id,name" in text
    assert "HS001,Nguyễn Văn An" in text


def test_lay_sheet_dau_tien_khi_so_tinh_co_nhieu_sheet(api):
    b64 = lam_xlsx(
        [["student_id", "name", "pref_1"], ["HS001", "A", "clb_bongro"]],
        ten_sheet="Ket qua",
        them_sheet=("Ghi chu", [["cot la"], ["du lieu khac"]]),
    )
    res = api.xlsx_to_csv_text(b64)
    assert res["ok"] is True
    assert "student_id" in res["data"]["csv_text"]
    assert "cot la" not in res["data"]["csv_text"]
    assert res["data"]["sheet_name"] == "Ket qua"
    assert res["data"]["sheet_names"] == ["Ket qua", "Ghi chu"]


def test_chon_duoc_sheet_theo_ten(api):
    b64 = lam_xlsx(
        [["cot la"], ["bo qua"]],
        ten_sheet="Bia",
        them_sheet=("Du lieu", [["student_id", "pref_1"], ["HS001", "clb_bongro"]]),
    )
    res = api.xlsx_to_csv_text(b64, sheet_name="Du lieu")
    assert res["ok"] is True
    assert "student_id" in res["data"]["csv_text"]


def test_file_khong_phai_xlsx_bao_loi_ro_rang(api):
    res = api.xlsx_to_csv_text(base64.b64encode(b"day khong phai excel").decode())
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "xlsx_read_failed"


def test_so_tinh_rong_bao_loi_chu_khong_sap(api):
    res = api.xlsx_to_csv_text(lam_xlsx([]))
    assert res["ok"] is False


# ------------------------------------------------------------------ #
# NỐI VÀO LUỒNG NHẬP CÓ SẴN
# ------------------------------------------------------------------ #


def test_nhan_dien_loai_file_hoat_dong_tren_du_lieu_tu_xlsx(api_co_club):
    b64 = lam_xlsx([
        ["student_id", "name", "pref_1", "pref_2"],
        ["HS001", "Nguyễn Văn An", "clb_bongro", "clb_amnhac"],
    ])
    text = api_co_club.xlsx_to_csv_text(b64)["data"]["csv_text"]
    d = api_co_club.detect_csv_kind(text)["data"]
    assert d["kind"] == "preferences"
    assert d["confident"] is True


def test_nap_thang_tu_xlsx_vao_dung_bang(api_co_club):
    b64 = lam_xlsx([
        ["student_id", "name", "reserve_group", "pref_1", "pref_2"],
        ["HS001", "Nguyễn Văn An", "chinh_sach", "clb_bongro", "clb_amnhac"],
    ])
    text = api_co_club.xlsx_to_csv_text(b64)["data"]["csv_text"]
    res = api_co_club.import_csv_auto(text)
    assert res["ok"] is True, res["errors"]
    assert res["data"]["kind"] == "preferences"

    st = api_co_club.get_student_entry_state("HS001")["data"]
    assert st["ranked_clubs"] == ["clb_bongro", "clb_amnhac"]
    rows = api_co_club.list_students_admin("HS001")["data"]["rows"]
    assert rows[0]["reserve_group"] == "chinh_sach"


def test_danh_sach_CLB_tu_xlsx_nhap_duoc_ca_chi_tieu_so(api):
    b64 = lam_xlsx([
        ["club_id", "name", "capacity", "reserve_capacity", "reserve_group"],
        ["clb_bongro", "CLB Bóng rổ", 20, 0, None],
        ["clb_tienganh", "CLB Tiếng Anh", 25, 5, "chinh_sach"],
    ])
    text = api.xlsx_to_csv_text(b64)["data"]["csv_text"]
    res = api.import_csv_auto(text)
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_clubs_created"] == 2
    clubs = {c["club_id"]: c for c in api.list_clubs_admin()["data"]}
    assert clubs["clb_tienganh"]["capacity"] == 25
    assert clubs["clb_tienganh"]["reserve_capacity"] == 5
    assert clubs["clb_tienganh"]["reserve_group"] == "chinh_sach"
    assert clubs["clb_bongro"]["reserve_group"] in (None, "")


# ------------------------------------------------------------------ #
# MẪU .xlsx trong mau_csv/ nay là Sổ nhập CLB (một tệp, hai trang).
# Mẫu và sổ ví dụ được canh ở tests/test_so_nhap.py.
# ------------------------------------------------------------------ #


def test_sheet_huong_dan_cua_so_nhap_KHONG_lan_vao_du_lieu(api):
    """Sổ có trang Hướng dẫn phía sau; phần mềm chỉ đọc hai trang dữ liệu."""
    import os
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "mau_csv", "vi_du_day_du", "SO_NHAP_CLB_vi_du.xlsx")
    with open(p, "rb") as f:
        res = api.xem_truoc_so_nhap(base64.b64encode(f.read()).decode("ascii"))
    assert res["ok"], res
    assert res["data"]["loi"] == []
    assert (res["data"]["n_clb"], res["data"]["n_hoc_sinh"]) == (9, 24)


# ------------------------------------------------------------------ #
# TRẦN CỠ TỆP — chặn zip bomb làm treo máy kiosk
# ------------------------------------------------------------------ #


def test_tep_qua_lon_bi_tu_choi_truoc_khi_mo(api, monkeypatch):
    monkeypatch.setattr(type(api), "_TRAN_TEP_XLSX_MB", 0)
    res = api.xlsx_to_csv_text(lam_xlsx([["student_id"], ["hs1"]]))
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "file_too_large"


def test_tep_bung_ra_qua_lon_bi_tu_choi(api):
    """Zip bomb: tệp nén nhỏ xíu nhưng khai bung ra quá trần."""
    import zipfile

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("xl/worksheets/sheet1.xml", b"0" * (201 * 1024 * 1024))
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    assert len(b64) < 2 * 1024 * 1024       # tệp gửi lên vẫn nhỏ
    res = api.xlsx_to_csv_text(b64)
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "file_too_large"


def test_tep_binh_thuong_van_doc_duoc_sau_khi_co_tran(api):
    res = api.xlsx_to_csv_text(lam_xlsx([["student_id"], ["hs1"]]))
    assert res["ok"] is True


def test_loi_khong_dua_traceback_len_giao_dien_ma_ghi_vao_log(api, monkeypatch):
    """Vết ngăn xếp lộ đường dẫn máy cho bất kỳ ai đứng trước kiosk. Nó phải
    nằm trong loi_ung_dung.txt cạnh app.db, không nằm trên màn hình."""
    import os

    def no(*a, **k):
        raise RuntimeError("gia vo hong")
    monkeypatch.setattr(type(api), "_o_excel_thanh_chu", staticmethod(no))

    res = api.xlsx_to_csv_text(lam_xlsx([["student_id"], ["hs1"]]))
    assert res["ok"] is False
    assert not any("Traceback" in str(e) for e in res["errors"])
    log = os.path.join(os.path.dirname(os.path.abspath(api.db_path)), "loi_ung_dung.txt")
    with open(log, encoding="utf-8") as f:
        noi_dung = f.read()
    assert "Traceback" in noi_dung and "gia vo hong" in noi_dung
