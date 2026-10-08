"""Kiểm tra FILE KẾT QUẢ mà nhà trường nhận được sau khi chạy pipeline.

Trước đây file xuất ra chỉ có hai cột mã: `student_id,club_id`. Nhìn vào
đó không biết em nào tên gì, đỗ CLB nào, đỗ nguyện vọng thứ mấy — tức là
không dán bảng, không gửi phụ huynh, không phát cho giáo viên phụ trách
CLB được. Toàn bộ dữ liệu đó ĐÃ nằm sẵn trong DB, chỉ là câu lệnh xuất
không lấy.

File này khoá ba thứ: đủ cột để dùng được, Excel mở đúng tiếng Việt, và
người dùng biết file nằm ở đâu.
"""

import csv
import os

import pytest


@pytest.fixture
def api_da_chay(api, tmp_path):
    """Một lần chạy hoàn chỉnh: club, học sinh, điểm, pipeline."""
    api.create_or_update_club("clb_bongro", "CLB Bóng rổ", 2, 0, "")
    api.create_or_update_club("clb_amnhac", "CLB Âm nhạc", 5, 2, "chinh_sach")

    api.import_preferences_csv(
        "student_id,name,pref_1,pref_2\n"
        "HS001,Nguyễn Văn An,clb_bongro,clb_amnhac\n"
        "HS002,Trần Thị Bình,clb_bongro,clb_amnhac\n"
        "HS003,Lê Minh Cường,clb_amnhac,\n"
    )
    api.bulk_set_reserve_group(["HS003"], "chinh_sach")
    for c in api.get_scoring_overview()["data"]:
        ds = api.get_club_applicants_for_scoring(c["club_id"])["data"]["applicants"]
        if ds:
            api.submit_club_scores(
                c["club_id"],
                [{"student_id": u["student_id"], "score": 9.0 - i} for i, u in enumerate(ds)],
            )
    api.run_pipeline(seed=42)
    return api


def doc_csv(path):
    """Đọc như Excel đọc — utf-8-sig để nuốt BOM nếu có."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


# ------------------------------------------------------------------ #
# FILE TỔNG
# ------------------------------------------------------------------ #


def test_file_tong_co_ten_hoc_sinh_va_ten_club_chu_khong_chi_ma(api_da_chay, tmp_path):
    out = str(tmp_path / "ket_qua.csv")
    res = api_da_chay.export_csv(out)
    assert res["ok"] is True, res["errors"]

    rows = doc_csv(out)
    header = rows[0]
    # Đây chính là thứ trước đây thiếu.
    assert "Họ tên" in header
    assert "Tên CLB" in header
    assert "Nguyện vọng thứ" in header
    assert "Diện trúng tuyển" in header

    data = {r[0]: dict(zip(header, r)) for r in rows[1:]}
    assert data["HS001"]["Họ tên"] == "Nguyễn Văn An"
    assert data["HS001"]["Tên CLB"] == "CLB Bóng rổ"


def test_file_tong_ghi_ro_nguyen_vong_thu_may(api_da_chay, tmp_path):
    out = str(tmp_path / "ket_qua.csv")
    api_da_chay.export_csv(out)
    rows = doc_csv(out)
    header = rows[0]
    data = {r[0]: dict(zip(header, r)) for r in rows[1:]}
    # HS003 chỉ có 1 nguyện vọng (clb_amnhac) -> phải là nguyện vọng 1
    assert data["HS003"]["Nguyện vọng thứ"] == "1"


def test_dien_trung_tuyen_ghi_bang_tieng_Viet_khong_phai_ma_may(api_da_chay, tmp_path):
    """'reserve'/'general' là mã nội bộ — giáo viên không phải đoán."""
    out = str(tmp_path / "ket_qua.csv")
    api_da_chay.export_csv(out)
    rows = doc_csv(out)
    dien = {r[0]: dict(zip(rows[0], r))["Diện trúng tuyển"] for r in rows[1:]}
    assert set(dien.values()) <= {"Dự trữ", "Thường", ""}
    # HS003 thuộc nhóm chinh_sach, club Âm nhạc có 2 suất dự trữ
    assert dien["HS003"] == "Dự trữ"


def test_hoc_sinh_chua_duoc_xep_van_co_trong_file_va_ghi_ro(api_da_chay, tmp_path):
    """Bỏ sót các em chưa được xếp là bỏ sót đúng nhóm cần xử lý tiếp."""
    out = str(tmp_path / "ket_qua.csv")
    api_da_chay.export_csv(out)
    rows = doc_csv(out)
    assert len(rows) - 1 == 3  # đủ cả 3 em, không rơi em nào


def test_file_mo_bang_Excel_khong_loi_font(api_da_chay, tmp_path):
    """Không có BOM thì Excel hiện 'Nguyá»…n VÄƒn An'."""
    out = str(tmp_path / "ket_qua.csv")
    api_da_chay.export_csv(out)
    with open(out, "rb") as f:
        assert f.read(3) == b"\xef\xbb\xbf"


# ------------------------------------------------------------------ #
# NGƯỜI DÙNG PHẢI BIẾT FILE NẰM Ở ĐÂU
# ------------------------------------------------------------------ #


def test_xuat_vao_thu_muc_tai_ve_chu_khong_vao_thu_muc_phan_mem(tmp_path, api_da_chay):
    """Tệp kết quả phải rơi vào thư mục Tải xuống.

    Trước đây nó nằm CẠNH app.db — tìm được, nhưng nằm trong thư mục cài
    đặt, lẫn với .exe và dữ liệu. Không phải chỗ để tệp cho người ta mang
    đi. Ràng buộc cũ vẫn giữ nguyên: KHÔNG BAO GIỜ rơi vào thư mục làm
    việc của tiến trình, thứ có thể là bất kỳ đâu khi chạy .exe qua
    shortcut.
    """
    tai_ve = tmp_path / "TaiXuong"
    tai_ve.mkdir()
    api_da_chay.thu_muc_xuat = str(tai_ve)

    res = api_da_chay.export_csv("ket_qua.csv")
    assert res["ok"] is True
    duong_dan = res["data"]["path"]
    assert os.path.isabs(duong_dan), "phải trả về đường dẫn ĐẦY ĐỦ để hiện cho người dùng"
    assert os.path.dirname(duong_dan) == str(tai_ve)
    assert os.path.dirname(duong_dan) != os.path.dirname(api_da_chay.db_path)
    assert os.path.isfile(duong_dan)


def test_duong_dan_tuyet_doi_van_duoc_ton_trong_nguyen_van(tmp_path, api_da_chay):
    """Bên gọi tự chọn chỗ thì phần mềm không được tự ý dời đi nơi khác."""
    api_da_chay.thu_muc_xuat = str(tmp_path / "TaiXuong")
    cho_muon = tmp_path / "cho_rieng"
    cho_muon.mkdir()
    dich = cho_muon / "bao_cao.csv"

    res = api_da_chay.export_csv(str(dich))
    assert res["ok"] is True
    assert res["data"]["path"] == str(dich)
    assert dich.is_file()


def test_xuat_hai_lan_khong_ghi_de_tep_cu(tmp_path, api_da_chay):
    """Thư mục Tải xuống là thư mục của NGƯỜI DÙNG — ghi đè im lặng ở đó
    là xoá mất tệp họ có thể đang cần. Cư xử như trình duyệt: (2), (3)…"""
    tai_ve = tmp_path / "TaiXuong"
    tai_ve.mkdir()
    api_da_chay.thu_muc_xuat = str(tai_ve)

    lan_1 = api_da_chay.export_csv("")["data"]
    lan_2 = api_da_chay.export_csv("")["data"]

    assert lan_1["path"] != lan_2["path"], "lần xuất thứ hai đã ghi đè lần đầu"
    assert os.path.isfile(lan_1["path"]) and os.path.isfile(lan_2["path"])
    # thư mục theo CLB phải đi theo đúng tệp tổng của nó, không lẫn vào nhau
    assert lan_1["per_club_dir"] != lan_2["per_club_dir"]
    assert os.path.isdir(lan_1["per_club_dir"])
    assert os.path.isdir(lan_2["per_club_dir"])


def test_khong_tim_duoc_thu_muc_tai_ve_thi_lui_ve_canh_app_db(api_da_chay):
    """Không bao giờ để việc xuất kết quả THẤT BẠI chỉ vì chuyện chỗ để
    tệp. Không tìm được thư mục Tải xuống thì quay về hành vi cũ."""
    api_da_chay.thu_muc_xuat = "/khong/he/ton/tai/o/dau/ca"

    res = api_da_chay.export_csv("")
    assert res["ok"] is True, res["errors"]
    assert os.path.dirname(res["data"]["path"]) == os.path.dirname(api_da_chay.db_path)
    assert os.path.isfile(res["data"]["path"])


def test_khong_truyen_ten_file_van_xuat_duoc(tmp_path, api_da_chay):
    tai_ve = tmp_path / "TaiXuong"
    tai_ve.mkdir()
    api_da_chay.thu_muc_xuat = str(tai_ve)
    res = api_da_chay.export_csv()
    assert res["ok"] is True
    assert os.path.isfile(res["data"]["path"])


# ------------------------------------------------------------------ #
# TÁCH RIÊNG TỪNG CLB
# ------------------------------------------------------------------ #


def test_moi_club_mot_file_rieng_de_phat_cho_giao_vien_phu_trach(api_da_chay, tmp_path):
    out = str(tmp_path / "ket_qua.csv")
    res = api_da_chay.export_csv(out)
    thu_muc = res["data"]["per_club_dir"]
    assert os.path.isdir(thu_muc)

    ten_file = set(os.listdir(thu_muc))
    assert "clb_bongro.csv" in ten_file
    assert "clb_amnhac.csv" in ten_file

    rows = doc_csv(os.path.join(thu_muc, "clb_bongro.csv"))
    ma_hs = [r[0] for r in rows[1:]]
    # club Bóng rổ chỉ 2 suất -> đúng 2 em, và KHÔNG lẫn em của club khác
    assert len(ma_hs) == 2
    for sid in ma_hs:
        assert sid in ("HS001", "HS002")


def test_file_tung_club_co_ten_hoc_sinh(api_da_chay, tmp_path):
    out = str(tmp_path / "ket_qua.csv")
    res = api_da_chay.export_csv(out)
    rows = doc_csv(os.path.join(res["data"]["per_club_dir"], "clb_bongro.csv"))
    assert "Họ tên" in rows[0]
    assert any("Nguyễn Văn An" in r or "Trần Thị Bình" in r for r in rows[1:])


def test_hoc_sinh_chua_duoc_xep_co_file_rieng(api, tmp_path):
    """Nhà trường cần biết còn em nào chưa vào CLB nào để xử lý tiếp."""
    api.create_or_update_club("clb_bongro", "CLB Bóng rổ", 1, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1\n"
        "HS001,Nguyễn Văn An,clb_bongro\n"
        "HS002,Trần Thị Bình,clb_bongro\n"
    )
    ds = api.get_club_applicants_for_scoring("clb_bongro")["data"]["applicants"]
    api.submit_club_scores(
        "clb_bongro",
        [{"student_id": u["student_id"], "score": 9.0 - i} for i, u in enumerate(ds)],
    )
    api.run_pipeline(seed=42)

    res = api.export_csv(str(tmp_path / "ket_qua.csv"))
    thu_muc = res["data"]["per_club_dir"]
    chua_xep = os.path.join(thu_muc, "_chua_duoc_xep.csv")
    assert os.path.isfile(chua_xep), os.listdir(thu_muc)
    assert len(doc_csv(chua_xep)) - 1 == 1  # đúng 1 em trượt


def test_club_id_co_ky_tu_duong_dan_khong_ghi_file_ra_ngoai_thu_muc(api, tmp_path):
    """club_id do trường tự đặt và KHÔNG bị giới hạn ký tự (xem
    create_or_update_club). Một mã như '../ngoai' không được phép làm
    file rơi ra ngoài thư mục kết quả."""
    api.create_or_update_club("../ngoai", "CLB Lạ", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nHS001,Nguyễn Văn An,../ngoai\n")
    api.submit_club_scores("../ngoai", [{"student_id": "HS001", "score": 8.0}])
    api.run_pipeline(seed=42)

    res = api.export_csv(str(tmp_path / "ket_qua.csv"))
    assert res["ok"] is True
    thu_muc = os.path.realpath(res["data"]["per_club_dir"])
    for ten in os.listdir(thu_muc):
        that = os.path.realpath(os.path.join(thu_muc, ten))
        assert that.startswith(thu_muc + os.sep), f"{ten} thoát ra ngoài thư mục"


# ------------------------------------------------------------------ #
# TỆP TỔNG HỢP — kết quả này đến từ đâu, và còn gì phải làm
#
# Mọi tệp xuất ra trước đây đều nói *ai vào câu lạc bộ nào*, không tệp nào
# nói *kết quả này tính thế nào*. Hai lần chạy khác hạt giống cho ra hai bộ
# tệp trông y hệt: cùng cột, cùng số dòng, cùng hình dạng. Mà cả thiết kế
# của phần mềm dựa trên lời hứa "ai cũng tính lại được" — lời hứa ấy cần
# hạt giống, bộ số đã khoá và cách bốc thăm, và trước bản vá này KHÔNG thứ
# nào đi theo tệp kết quả ra khỏi phần mềm.
#
# ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ lời gọi `_bang_tong_hop()` khỏi
# `export_csv` → bốn test đầu ĐỎ.
# ------------------------------------------------------------------ #


def _doc_tho(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def test_tep_tong_hop_duoc_xuat_kem(api_da_chay, tmp_path):
    d = api_da_chay.export_csv(str(tmp_path / "kq.csv"))["data"]
    assert d["tong_hop_path"], "khong xuat tep tong hop"
    assert os.path.exists(d["tong_hop_path"])


def test_tong_hop_mang_du_ba_thu_de_tinh_lai(api_da_chay, tmp_path):
    """Hạt giống, cách bốc thăm, thời điểm khoá bộ số — thiếu một là mất
    khả năng tái lập, mà đó là trụ của cả thiết kế."""
    d = api_da_chay.export_csv(str(tmp_path / "kq.csv"))["data"]
    noi_dung = _doc_tho(d["tong_hop_path"])

    assert "Hạt giống bốc thăm" in noi_dung
    assert "Cách bốc thăm" in noi_dung
    assert "Bộ số bốc thăm khoá lúc" in noi_dung
    # Va gia tri THAT, khong phai chi cai nhan
    assert "42" in noi_dung
    assert "stb_ngay" in noi_dung


def test_hai_lan_chay_khac_hat_giong_cho_ra_hai_tep_KHAC_nhau(api_da_chay, tmp_path):
    """Đây chính là cái hỏng mà tệp này sinh ra để chặn."""
    a = _doc_tho(api_da_chay.export_csv(
        str(tmp_path / "a.csv"))["data"]["tong_hop_path"])

    api_da_chay.run_pipeline(seed=7, force_redraw_stb=True)
    b = _doc_tho(api_da_chay.export_csv(
        str(tmp_path / "b.csv"))["data"]["tong_hop_path"])

    assert "42" in a and "7" in b
    assert a != b, "hai lan chay khac hat giong ma tep tong hop y het nhau"


def test_tong_hop_neu_dich_danh_em_chua_co_cho_nao(api_da_chay, tmp_path):
    """Nhóm nhà trường phải xử lý tiếp phải nằm trong tệp mang đi họp,
    không nằm trong một tab phải mở phần mềm mới thấy."""
    d = api_da_chay.export_csv(str(tmp_path / "kq.csv"))["data"]
    noi_dung = _doc_tho(d["tong_hop_path"])
    assert "HỌC SINH CHƯA CÓ CÂU LẠC BỘ NÀO" in noi_dung


def test_tong_hop_khong_bao_gio_cat_am_tham_danh_sach_em_trang_tay(api, tmp_path):
    """`get_do_phu` cắt danh sách còn 200 để giao diện không phải vẽ vô hạn.
    Tệp xuất ra mà cắt im lặng thì người đọc tưởng đã hết.

    Bản trước đọc từ `get_do_phu` nên PHẢI cắt, và chỉ có thể vá bằng một
    dòng "(còn N em nữa)". Bản này đọc từ `get_em_chua_co_cho` — không cắt
    gì cả — nên test siết chặt hơn hẳn: đòi có MẶT từng em, kể cả em cuối
    cùng nằm sau mốc 200 cũ. Một dòng chú thích không còn đủ để qua được.
    """
    api.create_or_update_club("clb_nho", "CLB Nhỏ", 1, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1\n"
        + "".join("HS%03d,Em %d,clb_nho\n" % (i, i) for i in range(1, 260))
    )
    api.run_pipeline(seed=42)

    d = api.export_csv(str(tmp_path / "kq.csv"))["data"]
    noi_dung = _doc_tho(d["tong_hop_path"])

    trang_tay = {e["student_id"]
                 for e in api.get_em_chua_co_cho()["data"]["danh_sach"]}
    assert len(trang_tay) == 258, len(trang_tay)
    thieu = [sid for sid in trang_tay if sid not in noi_dung]
    assert thieu == [], "tep bo sot %d em, vi du %s" % (len(thieu), thieu[:5])
    assert "HS259" in noi_dung, "em cuoi cung — nam sau moc cat 200 cu"


# ------------------------------------------------------------------ #
# TỆP EXCEL GỘP
#
# `export_csv` (bộ .csv rời) vẫn ghi kèm sổ Excel cùng tên gốc — chính là
# sổ sáu trang của `export_ket_qua` (xem tests/test_so_excel_de_dung.py).
#
# ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ lời gọi `_ghi_so_excel` → ba test dưới ĐỎ.
# ------------------------------------------------------------------ #


def test_xuat_kem_mot_tep_excel(api_da_chay, tmp_path):
    d = api_da_chay.export_csv(str(tmp_path / "kq.csv"))["data"]
    assert d["excel_path"], "khong xuat tep Excel"
    assert os.path.exists(d["excel_path"])
    assert d["excel_path"].endswith(".xlsx")


def test_excel_co_trang_huong_dan_va_danh_sach(api_da_chay, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    d = api_da_chay.export_csv(str(tmp_path / "kq.csv"))["data"]
    wb = openpyxl.load_workbook(d["excel_path"])
    assert "Hướng dẫn" in wb.sheetnames
    assert "Danh sách học sinh" in wb.sheetnames


def test_excel_khoa_dong_tieu_de_cua_bang_du_lieu(api_da_chay, tmp_path):
    """Cuộn xuống dòng 300 vẫn phải biết cột nào là cột nào — đúng lý do
    người ta ngại đọc một tệp .csv dài."""
    openpyxl = pytest.importorskip("openpyxl")
    d = api_da_chay.export_csv(str(tmp_path / "kq.csv"))["data"]
    wb = openpyxl.load_workbook(d["excel_path"])
    ws = wb["Danh sách học sinh"]
    # Dong 1-2 la ten trang, dong 4 la tieu de cot -> khoa ngay duoi no.
    assert ws.freeze_panes == "A5"
    assert ws["A4"].value == "Mã học sinh"


def test_excel_va_bang_tong_csv_noi_cung_mot_dieu(api_da_chay, tmp_path):
    """Hai định dạng phải đi ra từ MỘT nguồn, không phải hai đường tính
    song song rồi trôi khỏi nhau."""
    openpyxl = pytest.importorskip("openpyxl")
    d = api_da_chay.export_csv(str(tmp_path / "kq.csv"))["data"]
    tu_csv = doc_csv(d["path"])
    ws = openpyxl.load_workbook(d["excel_path"])["Danh sách học sinh"]
    tu_excel = [
        ["" if o is None else str(o) for o in r]
        for r in ws.iter_rows(min_row=4, values_only=True)   # tu dong tieu de cot
    ]
    assert tu_excel == tu_csv


def test_xuat_excel_hong_khong_lam_hong_ca_lan_xuat(api_da_chay, tmp_path, monkeypatch):
    """Các tệp .csv đã ghi xong và vẫn dùng được — báo lại bằng đường dẫn
    None chứ không ném lỗi ra ngoài."""
    def no(*a, **k):
        raise RuntimeError("gia vo hong")
    monkeypatch.setattr(type(api_da_chay), "_ghi_so_excel", no)

    kq = api_da_chay.export_csv(str(tmp_path / "kq.csv"))
    assert kq["ok"], kq
    assert kq["data"]["excel_path"] is None
    assert os.path.exists(kq["data"]["path"])


# ------------------------------------------------------------------ #
# CHẶN CÔNG THỨC TRONG TỆP EXCEL (CSV/formula injection)
#
# Bản .csv đã chặn từ trước (an_toan_cho_excel), bản .xlsx thì chưa:
# openpyxl coi mọi chuỗi bắt đầu bằng "=" là công thức, nên một học sinh
# tên "=HYPERLINK(...)" thành một liên kết sống trong tệp giáo viên mở.
# ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ khối ép kiểu trong `so_excel.Trang.o` →
# test dưới ĐỎ.
# ------------------------------------------------------------------ #

TEN_DOC = '=HYPERLINK("http://ke-xau.example","Bấm vào đây")'


@pytest.fixture
def api_co_ten_doc(api):
    api.create_or_update_club("clb_a", "=1+1", 5, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1\n"
        f'HS001,"{TEN_DOC.replace(chr(34), chr(34) * 2)}",clb_a\n'
    )
    api.run_pipeline(seed=42)
    return api


def test_excel_khong_co_cong_thuc_nao_tu_du_lieu_nhap(api_co_ten_doc, tmp_path):
    import zipfile

    d = api_co_ten_doc.export_csv(str(tmp_path / "kq.csv"))["data"]
    with zipfile.ZipFile(d["excel_path"]) as z:
        xml = "".join(z.read(n).decode("utf-8") for n in z.namelist()
                      if n.startswith("xl/worksheets/"))
    # <f> là thẻ công thức trong định dạng .xlsx — không được có cái nào.
    assert "<f>" not in xml and "<f " not in xml


def test_excel_giu_nguyen_van_ten_khong_them_dau_nhay(api_co_ten_doc, tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    d = api_co_ten_doc.export_csv(str(tmp_path / "kq.csv"))["data"]
    ws = openpyxl.load_workbook(d["excel_path"])["Danh sách học sinh"]
    gia_tri = [o for r in ws.iter_rows(values_only=True) for o in r]
    assert TEN_DOC in gia_tri
    assert "=1+1" in gia_tri


@pytest.mark.parametrize("dau", ["\t", "\r"])
def test_csv_chan_ca_tab_va_xuong_dong_o_dau_o(api, tmp_path, dau):
    """Excel/LibreOffice bỏ qua tab hay xuống dòng ở đầu ô rồi đọc tiếp như
    công thức — nên chúng cũng phải được chặn như = + - @.

    Các đường nhập hiện nay đều cắt khoảng trắng hai đầu, nên tên kiểu này
    chỉ tới được CSDL bằng đường khác (dữ liệu cũ, đường nhập sau này). Ghi
    thẳng vào CSDL để khoá lớp chặn ở đầu ra, không phụ thuộc đầu vào."""
    import sqlite3

    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nHS001,An,clb_a\n")
    with sqlite3.connect(api.db_path) as c:
        c.execute("UPDATE clubs SET name = ? WHERE club_id = 'clb_a'", (dau + "=1+1",))
    api.run_pipeline(seed=42)
    d = api.export_csv(str(tmp_path / "kq.csv"))["data"]
    with open(d["path"], encoding="utf-8-sig", newline="") as f:
        noi_dung = f.read()
    assert "'" + dau + "=1+1" in noi_dung
