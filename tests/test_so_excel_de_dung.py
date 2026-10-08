"""Sổ Excel kết quả — MỘT tệp, mở ra là dùng được.

Ban giám khảo nhận xét: phần xuất kết quả quá rối, cần gọn lại và dễ dùng
như một tệp Excel. Trước bản sửa này, một lần bấm "Xuất" đẻ ra tới sáu tệp
rời và hai thư mục; tệp `.xlsx` có nhưng thông báo không nhắc tới, danh sách
từng CLB — thứ giáo viên cần nhất — lại không có trong sổ.

Giờ nút xuất trên giao diện gọi `export_ket_qua`: ra MỘT tệp `.xlsx` sáu
trang, theo thứ tự người đọc cần. Các tệp `.csv` rời chỉ ra khi đánh dấu
"Kèm các tệp CSV rời".
"""

import io
import os
import zipfile

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_NHIEU_BUOI = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")
BO_MOT_BUOI = os.path.join(GOC, "du_lieu_test", "bo_sach")

CAC_TRANG = ["Hướng dẫn", "Danh sách học sinh", "Theo CLB",
             "Chưa có chỗ", "Thống kê", "Dấu vết (kỹ thuật)"]


def _nap(api, thu_muc, tep):
    for ten in tep:
        with io.open(os.path.join(thu_muc, ten), encoding="utf-8-sig") as f:
            kq = api.import_csv_auto(f.read())
        assert kq["ok"], (ten, kq)


@pytest.fixture
def api_mot_buoi(api):
    _nap(api, BO_MOT_BUOI, ("SACH_01_danh_sach_CLB.csv",
                            "SACH_02_chon_CLB_muon_thi.csv",
                            "SACH_03_xep_hang_nguyen_vong.csv"))
    assert api.run_pipeline(seed=42)["ok"]
    return api


@pytest.fixture
def api_nhieu_buoi(api):
    _nap(api, BO_NHIEU_BUOI, ("NHIEUBUOI_01_danh_sach_CLB.csv",
                              "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
                              "NHIEUBUOI_03_xep_hang_nguyen_vong.csv"))
    assert api.run_pipeline(seed=42)["ok"]
    return api


@pytest.fixture
def api_thieu_cho(api):
    """CLB một chỗ, hai em cùng muốn -> chắc chắn có một em chưa có chỗ."""
    api.create_or_update_club("clb_a", "CLB A", 1, 0, "")
    api.create_or_update_club("clb_b", "CLB B", 3, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1\n"
        "HS001,Nguyễn Văn An,clb_a\n"
        "HS002,Trần Thị Bình,clb_a\n"
        "HS003,Lê Minh Cường,clb_b\n"
    )
    assert api.run_pipeline(seed=42)["ok"]
    return api


def _thu_muc_tai_ve():
    return os.environ["RBDA_THU_MUC_TAI_VE"]


def _ket_qua(api):
    with api._ket_noi_doc() as cur:
        return [dict(r) for r in cur.execute(
            "SELECT student_id, buoi, club_id FROM match_results")]


def _hang_du_lieu(ws):
    """Các dòng dưới dòng tiêu đề cột (dòng ngay trên ô khoá cuộn)."""
    dong_dau = ws[ws.freeze_panes].row
    return [list(r) for r in ws.iter_rows(min_row=dong_dau, values_only=True)
            if any(o not in (None, "") for o in r)]


def _tieu_de_cot(ws):
    dong = ws[ws.freeze_panes].row - 1
    return [c.value for c in ws[dong]]


# ------------------------------------------------------------------ #
# 1. MỘT TỆP, KHÔNG RẢI TỆP RỜI
# ------------------------------------------------------------------ #

def test_mac_dinh_chi_ra_dung_mot_tep_excel(api_mot_buoi):
    kq = api_mot_buoi.export_ket_qua("")
    assert kq["ok"], kq
    d = kq["data"]
    assert d["path"].endswith(".xlsx")
    assert os.path.isfile(d["path"])
    assert sorted(os.listdir(_thu_muc_tai_ve())) == [os.path.basename(d["path"])]


def test_xuat_lan_hai_khong_ghi_de_lan_dau(api_mot_buoi):
    p1 = api_mot_buoi.export_ket_qua("")["data"]["path"]
    p2 = api_mot_buoi.export_ket_qua("")["data"]["path"]
    assert p1 != p2 and os.path.isfile(p1) and os.path.isfile(p2)


def test_kem_csv_thi_moi_ra_bo_csv_cu(api_mot_buoi):
    d = api_mot_buoi.export_ket_qua("", True)["data"]
    assert d["path"].endswith(".xlsx") and os.path.isfile(d["path"])
    assert d["csv_path"] and os.path.isfile(d["csv_path"])
    assert os.path.isdir(d["per_club_dir"])
    assert os.path.isfile(d["tong_hop_path"])
    # CSV va so Excel cung mot ten goc -> nguoi dung biet chung di cung nhau
    assert os.path.splitext(d["csv_path"])[0] == os.path.splitext(d["path"])[0]


def test_khong_kem_csv_thi_khong_co_khoa_csv(api_mot_buoi):
    d = api_mot_buoi.export_ket_qua("")["data"]
    assert d["csv_path"] is None and d["per_club_dir"] is None


def test_excel_hong_thi_bao_loi_chu_khong_im_lang(api_mot_buoi, monkeypatch):
    def no(*a, **k):
        raise RuntimeError("gia vo hong")
    monkeypatch.setattr(type(api_mot_buoi), "_ghi_so_excel", no)
    kq = api_mot_buoi.export_ket_qua("")
    assert kq["ok"] is False
    assert os.listdir(_thu_muc_tai_ve()) == []


# ------------------------------------------------------------------ #
# 2. CÁC TRANG, ĐÚNG THỨ TỰ NGƯỜI ĐỌC CẦN
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("ten_fixture", ["api_mot_buoi", "api_nhieu_buoi", "api_thieu_cho"])
def test_sau_trang_dung_thu_tu(request, ten_fixture):
    api = request.getfixturevalue(ten_fixture)
    wb = openpyxl.load_workbook(api.export_ket_qua("")["data"]["path"])
    assert wb.sheetnames == CAC_TRANG
    assert wb.active.title == "Hướng dẫn"


def test_trang_huong_dan_co_lien_ket_toi_moi_trang(api_mot_buoi):
    ws = openpyxl.load_workbook(api_mot_buoi.export_ket_qua("")["data"]["path"])["Hướng dẫn"]
    dich = {c.hyperlink.location for r in ws.iter_rows() for c in r if c.hyperlink}
    for t in CAC_TRANG[1:]:
        assert "'%s'!A1" % t in dich, (t, dich)


def test_trang_huong_dan_co_so_lieu_chinh(api_thieu_cho):
    ws = openpyxl.load_workbook(api_thieu_cho.export_ket_qua("")["data"]["path"])["Hướng dẫn"]
    gia_tri = {r[0]: r[1] for r in ws.iter_rows(values_only=True) if r and r[0]}
    assert gia_tri["Số học sinh"] == 3
    assert gia_tri["Số em đã có câu lạc bộ"] == 2
    assert gia_tri["Số em chưa có chỗ"] == 1


def test_trang_huong_dan_canh_bao_khi_ket_qua_da_cu(api_thieu_cho):
    api_thieu_cho.create_or_update_club("clb_b", "CLB B", 5, 0, "")
    ws = openpyxl.load_workbook(api_thieu_cho.export_ket_qua("")["data"]["path"])["Hướng dẫn"]
    chu = " ".join(str(o) for r in ws.iter_rows(values_only=True) for o in r if o)
    assert "chạy lại" in chu.lower()


# ------------------------------------------------------------------ #
# 3. DANH SÁCH HỌC SINH
# ------------------------------------------------------------------ #

def test_danh_sach_mot_buoi_moi_em_mot_dong(api_mot_buoi):
    ws = openpyxl.load_workbook(api_mot_buoi.export_ket_qua("")["data"]["path"])["Danh sách học sinh"]
    kq = _ket_qua(api_mot_buoi)
    dong = _hang_du_lieu(ws)
    cot = _tieu_de_cot(ws)
    assert "Mã học sinh" in cot and "Tên CLB" in cot
    assert len(dong) == len(kq)
    assert ws.auto_filter.ref, "phai co bo loc de giao vien loc theo CLB"
    i_ma, i_clb = cot.index("Mã học sinh"), cot.index("Mã CLB")
    assert sorted((str(r[i_ma]), r[i_clb] or None) for r in dong) == \
        sorted((k["student_id"], k["club_id"]) for k in kq)


def test_danh_sach_nhieu_buoi_la_thoi_khoa_bieu(api_nhieu_buoi):
    ws = openpyxl.load_workbook(api_nhieu_buoi.export_ket_qua("")["data"]["path"])["Danh sách học sinh"]
    with api_nhieu_buoi._ket_noi_doc() as cur:
        ds_buoi = api_nhieu_buoi._ds_buoi(cur)
        so_em = cur.execute(
            "SELECT COUNT(DISTINCT student_id) FROM match_results").fetchone()[0]
    cot = _tieu_de_cot(ws)
    for b in ds_buoi:
        assert b in cot, (b, cot)
    assert len(_hang_du_lieu(ws)) == so_em


# ------------------------------------------------------------------ #
# 4. THEO CLB — mọi CLB một trang tính, ngắt trang giữa các CLB
# ------------------------------------------------------------------ #

def _doc_theo_clb(ws):
    """{club_id: [student_id, ...]} đọc lại từ trang Theo CLB."""
    ra, hien_tai, cot_ma = {}, None, None
    for r in ws.iter_rows(values_only=True):
        a = r[0]
        if isinstance(a, str) and "Mã CLB: " in a:
            hien_tai = next(p[len("Mã CLB: "):] for p in a.split(" · ")
                            if p.startswith("Mã CLB: "))
            ra[hien_tai] = []
            cot_ma = None
        elif hien_tai and "Mã học sinh" in r:
            cot_ma = list(r).index("Mã học sinh")
        elif hien_tai and cot_ma is not None and r[cot_ma] not in (None, ""):
            ra[hien_tai].append(str(r[cot_ma]))
    return ra


@pytest.mark.parametrize("ten_fixture", ["api_mot_buoi", "api_nhieu_buoi"])
def test_theo_clb_moi_em_dung_mot_lan_dung_clb(request, ten_fixture):
    api = request.getfixturevalue(ten_fixture)
    ws = openpyxl.load_workbook(api.export_ket_qua("")["data"]["path"])["Theo CLB"]
    doc = _doc_theo_clb(ws)
    mong = {}
    for k in _ket_qua(api):
        if k["club_id"]:
            mong.setdefault(k["club_id"], []).append(k["student_id"])
    assert {c: sorted(v) for c, v in doc.items() if v} == {c: sorted(v) for c, v in mong.items()}
    # Moi CLB deu co khoi, ke ca CLB chua ai vao
    assert set(doc) == {c["club_id"] for c in api.get_club_fill_stats()["data"]}


def test_theo_clb_ngat_trang_giua_cac_clb(api_mot_buoi):
    ws = openpyxl.load_workbook(api_mot_buoi.export_ket_qua("")["data"]["path"])["Theo CLB"]
    so_clb = len(api_mot_buoi.get_club_fill_stats()["data"])
    assert len(ws.row_breaks.brk) == so_clb - 1


# ------------------------------------------------------------------ #
# 5. CHƯA CÓ CHỖ, THỐNG KÊ, DẤU VẾT
# ------------------------------------------------------------------ #

def test_chua_co_cho_liet_ke_dich_danh(api_thieu_cho):
    ws = openpyxl.load_workbook(api_thieu_cho.export_ket_qua("")["data"]["path"])["Chưa có chỗ"]
    chua = [k["student_id"] for k in _ket_qua(api_thieu_cho) if not k["club_id"]]
    assert len(chua) == 1
    dong = _hang_du_lieu(ws)
    assert [str(r[0]) for r in dong] == chua


def test_chua_co_cho_khi_moi_em_deu_co_cho_van_noi_ro(api):
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nHS001,An,clb_a\n")
    api.run_pipeline(seed=42)
    ws = openpyxl.load_workbook(api.export_ket_qua("")["data"]["path"])["Chưa có chỗ"]
    chu = " ".join(str(o) for r in ws.iter_rows(values_only=True) for o in r if o)
    assert "mọi em đều" in chu.lower()


def test_thong_ke_giu_so_that(api_nhieu_buoi):
    ws = openpyxl.load_workbook(api_nhieu_buoi.export_ket_qua("")["data"]["path"])["Thống kê"]
    dong = [list(r) for r in ws.iter_rows(values_only=True)]
    i = next(n for n, r in enumerate(dong) if "Tỉ lệ chọi" in r)
    cot = dong[i].index("Tỉ lệ chọi")
    so_clb = len(api_nhieu_buoi.get_club_fill_stats()["data"])
    gia_tri = [r[cot] for r in dong[i + 1:i + 1 + so_clb]]
    assert all(isinstance(v, (int, float)) or v is None for v in gia_tri), gia_tri


def test_dau_vet_co_hat_giong(api_mot_buoi):
    ws = openpyxl.load_workbook(api_mot_buoi.export_ket_qua("")["data"]["path"])["Dấu vết (kỹ thuật)"]
    gia_tri = {r[0]: r[1] for r in ws.iter_rows(values_only=True) if r and r[0]}
    assert gia_tri.get("Hạt giống bốc thăm") == 42


def test_dau_vet_nhieu_buoi_co_so_boc_tham(api_nhieu_buoi):
    ws = openpyxl.load_workbook(api_nhieu_buoi.export_ket_qua("")["data"]["path"])["Dấu vết (kỹ thuật)"]
    chu = [o for r in ws.iter_rows(values_only=True) for o in r if isinstance(o, str)]
    assert any(o.startswith("SỐ BỐC THĂM") for o in chu)


# ------------------------------------------------------------------ #
# 6. IN ĐƯỢC, VÀ AN TOÀN
# ------------------------------------------------------------------ #

def test_moi_trang_in_vua_mot_kho_giay(api_mot_buoi):
    wb = openpyxl.load_workbook(api_mot_buoi.export_ket_qua("")["data"]["path"])
    for ws in wb.worksheets:
        assert str(ws.page_setup.paperSize) == ws.PAPERSIZE_A4, ws.title
        assert ws.sheet_properties.pageSetUpPr.fitToPage, ws.title
        assert ws.page_setup.fitToWidth == 1 and ws.page_setup.fitToHeight == 0, ws.title
        assert "&P" in (ws.oddFooter.center.text or ""), ws.title


def test_ten_doc_khong_thanh_cong_thuc(api):
    ten = '=HYPERLINK("http://ke-xau.example","Bấm vào đây")'
    api.create_or_update_club("clb_a", "=1+1", 5, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1\n"
        f'HS001,"{ten.replace(chr(34), chr(34) * 2)}",clb_a\n')
    api.run_pipeline(seed=42)
    p = api.export_ket_qua("")["data"]["path"]
    with zipfile.ZipFile(p) as z:
        xml = "".join(z.read(n).decode("utf-8") for n in z.namelist()
                      if n.startswith("xl/worksheets/"))
    assert "<f>" not in xml and "<f " not in xml
    gia_tri = {o for ws in openpyxl.load_workbook(p).worksheets
               for r in ws.iter_rows(values_only=True) for o in r}
    assert ten in gia_tri and "=1+1" in gia_tri


def test_chua_chay_thi_van_xuat_duoc(api):
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    kq = api.export_ket_qua("")
    assert kq["ok"], kq
    assert openpyxl.load_workbook(kq["data"]["path"]).sheetnames == CAC_TRANG


# ------------------------------------------------------------------ #
# 7. THỬ SỨC (du_lieu_test/thu_tai/stress_xuat_excel.py) — lỗi đã bắt được
#
# openpyxl từ chối ký tự điều khiển (\x00-\x08, \x0b, \x0c, \x0e-\x1f) bằng
# IllegalCharacterError. Nạp CSV để lọt chúng vào (dán từ Word/Forms), và vì
# hỏng sổ Excel giờ là hỏng cả lần xuất, MỘT ký tự vô hình trong tên MỘT em
# từng chặn cả trường khỏi kết quả.
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("ky_tu", ["\x00", "\x01", "\x0b", "\x0c", "\x1f"])
def test_ky_tu_dieu_khien_khong_lam_hong_lan_xuat(api, ky_tu):
    api.create_or_update_club("clb_a", "CLB" + ky_tu + "A", 5, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1\nHS001,An%sBình,clb_a\n" % ky_tu)
    api.run_pipeline(seed=42)
    kq = api.export_ket_qua("")
    assert kq["ok"], kq
    gia_tri = {o for ws in openpyxl.load_workbook(kq["data"]["path"]).worksheets
               for r in ws.iter_rows(values_only=True) for o in r}
    assert "AnBình" in gia_tri       # bo ky tu vo hinh, giu phan con lai


def test_qua_nhieu_clb_khong_vuot_gioi_han_ngat_trang_cua_excel(api):
    """Excel chỉ nhận 1.026 ngắt trang thủ công mỗi trang tính; vượt là tệp
    phải "sửa chữa" khi mở. CLB thứ 1.028 trở đi in nối tiếp, không ngắt."""
    for i in range(1030):
        api.create_or_update_club("c%04d" % i, "CLB %d" % i, 5, 0, "")
    ws = openpyxl.load_workbook(api.export_ket_qua("")["data"]["path"])["Theo CLB"]
    assert len(ws.row_breaks.brk) <= 1026


def test_ten_clb_rat_dai_van_giu_ma_clb_tren_dong_dau_khoi(api):
    api.create_or_update_club("clb_a", "B" * 40000, 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nHS001,An,clb_a\n")
    api.run_pipeline(seed=42)
    ws = openpyxl.load_workbook(api.export_ket_qua("")["data"]["path"])["Theo CLB"]
    dau = [r[0] for r in ws.iter_rows(values_only=True)
           if isinstance(r[0], str) and "Mã CLB: clb_a" in r[0]]
    assert dau and "Đã xếp 1/5 chỗ" in dau[0] and len(dau[0]) < 300


def test_csv_hong_van_giu_so_excel_va_bao_duong_dan(api_mot_buoi, monkeypatch):
    """Sổ Excel ghi xong rồi mới tới bộ .csv. CSV hỏng (vd giáo viên đang mở
    tệp CSV cũ trong Excel) không được xoá công của sổ: vẫn báo ok kèm đường
    dẫn sổ, và nói rõ phần CSV không ghi được."""
    def no(*a, **k):
        raise PermissionError("tep dang mo")
    monkeypatch.setattr(type(api_mot_buoi), "_ghi_bo_csv", no)
    kq = api_mot_buoi.export_ket_qua("", True)
    assert kq["ok"], kq
    d = kq["data"]
    assert d["path"].endswith(".xlsx") and os.path.isfile(d["path"])
    assert d["csv_path"] is None
    assert d["loi_csv"]["code"] == "error_exporting_csv"


# ------------------------------------------------------------------ #
# 8. KHÔNG GHI ĐÈ / KHÔNG XOÁ TỆP CÓ SẴN (rà soát mã PR #6)
# ------------------------------------------------------------------ #

def test_export_csv_khong_ghi_de_so_excel_da_co_trong_tai_ve(api_mot_buoi):
    """Nút trên giao diện để lại `ket_qua_phan_bo.xlsx`; `export_csv("")` sau
    đó chỉ soát tên `.csv` rồi ghi `<gốc>.xlsx` — từng ghi đè sổ cũ."""
    cu = api_mot_buoi.export_ket_qua("")["data"]["path"]
    with open(cu, "rb") as f:
        noi_dung_cu = f.read()
    d = api_mot_buoi.export_csv("")["data"]
    assert d["excel_path"] != cu
    with open(cu, "rb") as f:
        assert f.read() == noi_dung_cu


def test_xuat_hong_khong_xoa_tep_co_san_o_duong_dan_tuyet_doi(api_mot_buoi, tmp_path, monkeypatch):
    thu_muc = tmp_path / "cua_toi"
    thu_muc.mkdir()
    p = thu_muc / "bao_cao_cua_toi.xlsx"
    p.write_bytes(b"TEP CU QUAN TRONG")

    def no(*a, **k):
        raise RuntimeError("gia vo hong")
    monkeypatch.setattr(type(api_mot_buoi), "_ghi_so_excel", no)
    assert api_mot_buoi.export_ket_qua(str(p))["ok"] is False
    assert p.read_bytes() == b"TEP CU QUAN TRONG"
    assert os.listdir(thu_muc) == ["bao_cao_cua_toi.xlsx"]   # khong de tep tam


def test_ghi_do_dang_khong_de_lai_tep_hong(api_mot_buoi, monkeypatch):
    """Sổ hỏng giữa chừng (vd đầy đĩa) không được để lại tệp .xlsx dở ở Tải xuống."""
    def ghi_do_dang(self, path, du):
        with open(path, "wb") as f:
            f.write(b"PK\x03\x04 do dang")
        raise OSError("het cho trong")
    monkeypatch.setattr(type(api_mot_buoi), "_ghi_so_excel", ghi_do_dang)
    assert api_mot_buoi.export_ket_qua("")["ok"] is False
    assert os.listdir(_thu_muc_tai_ve()) == []
    assert api_mot_buoi.export_csv("")["data"]["excel_path"] is None
    assert not [f for f in os.listdir(_thu_muc_tai_ve()) if f.endswith(".xlsx")]


@pytest.mark.skipif(os.name == "nt", reason="quyen tep kieu POSIX")
def test_so_excel_mang_quyen_tep_binh_thuong(api_mot_buoi):
    """Ghi qua tệp tạm không được làm sổ chỉ chủ máy đọc được (0600)."""
    p = api_mot_buoi.export_ket_qua("")["data"]["path"]
    mask = os.umask(0)
    os.umask(mask)
    assert os.stat(p).st_mode & 0o777 == 0o666 & ~mask
