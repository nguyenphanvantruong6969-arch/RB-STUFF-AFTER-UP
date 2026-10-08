"""Kiểm tra ĐỊNH DẠNG CSV nhập vào phần mềm và các FILE MẪU đi kèm.

Hai việc file này bảo đảm:

1. **File thật từ Excel nhập được.** Khi giáo viên mở file mẫu bằng Excel
   rồi bấm Lưu, Excel ghi ra "CSV UTF-8" — kèm BOM ở đầu file. Microsoft
   Forms xuất ra cũng vậy. Nếu không xử lý, tên cột đầu tiên đọc lên
   thành "﻿student_id" và phần mềm báo THIẾU CỘT student_id, dù nhìn
   bằng mắt file hoàn toàn đúng.

2. **File mẫu trong mau_csv/ luôn khớp với code.** Mẫu nằm cùng repo với
   code đọc nó, nên phải được nhập thử THẬT trong test — nếu sau này ai
   đổi tên cột mà quên sửa mẫu, test này đỏ ngay.
"""

import os

import pytest

MAU_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mau_csv"
)


def doc_mau(ten_file: str) -> str:
    with open(os.path.join(MAU_DIR, ten_file), encoding="utf-8-sig") as f:
        return f.read()


@pytest.fixture
def api_co_club(api):
    """Bộ club đúng bằng bộ club dùng trong file mẫu."""
    api.create_or_update_club("clb_bongro", "CLB Bóng rổ", 20, 0, "")
    api.create_or_update_club("clb_tienganh", "CLB Tiếng Anh", 25, 5, "chinh_sach")
    api.create_or_update_club("clb_robotics", "CLB Robotics", 15, 0, "")
    api.create_or_update_club("clb_amnhac", "CLB Âm nhạc", 20, 0, "")
    api.create_or_update_club("clb_mythuat", "CLB Mỹ thuật", 18, 3, "chinh_sach")
    return api


# ------------------------------------------------------------------ #
# BOM — thứ Excel và Microsoft Forms luôn thêm vào
# ------------------------------------------------------------------ #


def test_csv_luu_tu_excel_co_bom_van_nhap_duoc(api_co_club):
    """Đây CHÍNH LÀ file mà Excel ghi ra khi bấm Lưu dạng CSV UTF-8."""
    csv_co_bom = (
        "﻿student_id,name,club_id\n"
        "HS001,Nguyen Van A,clb_bongro\n"
    )
    res = api_co_club.import_test_selection_csv(csv_co_bom)
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_students_with_selection_written"] == 1


def test_bom_khong_lam_hong_dinh_dang_rong(api_co_club):
    csv_co_bom = (
        "﻿student_id,name,pref_1,pref_2\n"
        "HS001,Nguyen Van A,clb_bongro,clb_amnhac\n"
    )
    res = api_co_club.import_preferences_csv(csv_co_bom)
    assert res["ok"] is True, res["errors"]
    state = api_co_club.get_student_entry_state("HS001")["data"]
    assert state["ranked_clubs"] == ["clb_bongro", "clb_amnhac"]


def test_preview_cung_doc_duoc_file_co_bom(api_co_club):
    """Xem trước mà đã hỏng thì giáo viên không dám bấm nhập."""
    csv_co_bom = "﻿student_id,name,pref_1\nHS001,Nguyen Van A,clb_bongro\n"
    res = api_co_club.preview_import_csv(csv_co_bom, "preferences")
    assert res["ok"] is True
    assert res["data"]["format"] == "wide"
    assert "student_id" in res["data"]["fieldnames"]


# ------------------------------------------------------------------ #
# CÁC FILE MẪU THẬT trong mau_csv/
# ------------------------------------------------------------------ #


def test_mau_chon_club_thi_dang_rong(api_co_club):
    res = api_co_club.import_test_selection_csv(doc_mau("01_chon_club_thi_dang_rong.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_students_created"] == 5
    assert res["data"]["n_students_skipped"] == 0
    # HS001 tick 3 club, để trống ô thứ 4 -> chỉ nhận 3
    state = api_co_club.get_student_entry_state("HS001")["data"]
    assert sorted(state["tested_clubs"]) == ["clb_amnhac", "clb_bongro", "clb_tienganh"]


def test_mau_chon_club_thi_dang_dai(api_co_club):
    res = api_co_club.import_test_selection_csv(doc_mau("02_chon_club_thi_dang_dai.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_students_created"] == 5
    assert res["data"]["n_students_skipped"] == 0


def test_hai_dang_cua_cung_du_lieu_cho_ket_qua_GIONG_HET_NHAU(api):
    """Dạng 'rộng' và dạng 'dài' chỉ khác cách trình bày — nhập vào phải
    ra cùng một kết quả, nếu không thì tài liệu đang nói dối."""
    def nap_club(a):
        a.create_or_update_club("clb_bongro", "CLB Bóng rổ", 20, 0, "")
        a.create_or_update_club("clb_tienganh", "CLB Tiếng Anh", 25, 5, "chinh_sach")
        a.create_or_update_club("clb_robotics", "CLB Robotics", 15, 0, "")
        a.create_or_update_club("clb_amnhac", "CLB Âm nhạc", 20, 0, "")
        a.create_or_update_club("clb_mythuat", "CLB Mỹ thuật", 18, 3, "chinh_sach")

    nap_club(api)
    api.import_test_selection_csv(doc_mau("01_chon_club_thi_dang_rong.csv"))
    rong = {
        sid: sorted(api.get_student_entry_state(sid)["data"]["tested_clubs"])
        for sid in ("HS001", "HS002", "HS003", "HS004", "HS005")
    }

    api.import_test_selection_csv(doc_mau("02_chon_club_thi_dang_dai.csv"))
    dai = {
        sid: sorted(api.get_student_entry_state(sid)["data"]["tested_clubs"])
        for sid in ("HS001", "HS002", "HS003", "HS004", "HS005")
    }
    assert rong == dai


def test_mau_nguyen_vong_dang_rong(api_co_club):
    res = api_co_club.import_preferences_csv(doc_mau("03_nguyen_vong_dang_rong.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_students_skipped"] == 0
    # Thứ tự nguyện vọng là thứ tự cột pref_1, pref_2, ...
    state = api_co_club.get_student_entry_state("HS001")["data"]
    assert state["ranked_clubs"] == ["clb_bongro", "clb_amnhac", "clb_tienganh"]


def test_mau_nguyen_vong_dang_dai(api_co_club):
    res = api_co_club.import_preferences_csv(doc_mau("04_nguyen_vong_dang_dai.csv"))
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_students_skipped"] == 0
    # Cột rank quyết định thứ tự, KHÔNG phải thứ tự dòng trong file
    state = api_co_club.get_student_entry_state("HS001")["data"]
    assert state["ranked_clubs"] == ["clb_bongro", "clb_amnhac", "clb_tienganh"]


def test_hai_dang_nguyen_vong_cho_ket_qua_GIONG_HET_NHAU(api_co_club):
    api_co_club.import_preferences_csv(doc_mau("03_nguyen_vong_dang_rong.csv"))
    rong = {
        sid: api_co_club.get_student_entry_state(sid)["data"]["ranked_clubs"]
        for sid in ("HS001", "HS002", "HS003", "HS004", "HS005")
    }
    api_co_club.import_preferences_csv(doc_mau("04_nguyen_vong_dang_dai.csv"))
    dai = {
        sid: api_co_club.get_student_entry_state(sid)["data"]["ranked_clubs"]
        for sid in ("HS001", "HS002", "HS003", "HS004", "HS005")
    }
    assert rong == dai


def test_moi_club_id_trong_file_mau_deu_co_that(api_co_club):
    """Mẫu mà chứa club_id không tồn tại thì học sinh bị BỎ QUA lặng lẽ —
    đúng cái bẫy tài liệu phải tránh."""
    for ten in ("01_chon_club_thi_dang_rong.csv", "02_chon_club_thi_dang_dai.csv"):
        res = api_co_club.import_test_selection_csv(doc_mau(ten))
        assert res["data"]["n_students_skipped"] == 0, f"{ten}: {res['data']['warnings']}"
    for ten in ("03_nguyen_vong_dang_rong.csv", "04_nguyen_vong_dang_dai.csv"):
        res = api_co_club.import_preferences_csv(doc_mau(ten))
        assert res["data"]["n_students_skipped"] == 0, f"{ten}: {res['data']['warnings']}"


# ------------------------------------------------------------------ #
# CÁC QUY TẮC ĐÃ VIẾT TRONG HUONG_DAN_CSV.md
#
# Mỗi test dưới đây khoá một câu khẳng định trong tài liệu. Tài liệu sai
# còn nguy hiểm hơn không có tài liệu: giáo viên tin theo rồi nhập nhầm
# dữ liệu phân bổ học sinh.
# ------------------------------------------------------------------ #


def test_dau_cham_phay_cung_dung_duoc(api_co_club):
    """Excel bản tiếng Việt/châu Âu hay lưu CSV bằng dấu chấm phẩy."""
    res = api_co_club.import_preferences_csv(
        "student_id;name;pref_1;pref_2\nHS900;Test;clb_bongro;clb_amnhac\n"
    )
    assert res["ok"] is True
    state = api_co_club.get_student_entry_state("HS900")["data"]
    assert state["ranked_clubs"] == ["clb_bongro", "clb_amnhac"]


def test_club_id_khong_ton_tai_thi_BO_QUA_CA_HOC_SINH(api_co_club):
    """Không nhập một phần — bỏ qua cả học sinh và báo rõ, để không ai
    tưởng đã nhập xong trong khi nguyện vọng bị thiếu."""
    res = api_co_club.import_preferences_csv(
        "student_id,name,pref_1,pref_2\nHS901,Test,clb_bongro,clb_sai_ten\n"
    )
    assert res["data"]["n_students_skipped"] == 1
    assert res["data"]["warnings"][0]["code"] == "csv_unknown_clubs_skipped"
    assert api_co_club.get_student_entry_state("HS901")["ok"] is False


def test_club_trung_nhau_bi_loai_giu_lan_xuat_hien_dau(api_co_club):
    res = api_co_club.import_preferences_csv(
        "student_id,name,pref_1,pref_2,pref_3\n"
        "HS902,Test,clb_bongro,clb_bongro,clb_amnhac\n"
    )
    assert res["ok"] is True
    state = api_co_club.get_student_entry_state("HS902")["data"]
    assert state["ranked_clubs"] == ["clb_bongro", "clb_amnhac"]
    assert any(w["code"] == "csv_pref_duplicate_deduped" for w in res["data"]["warnings"])


def test_qua_10_nguyen_vong_thi_bo_qua_ca_hoc_sinh_chu_khong_cat_bot(api):
    """Giới hạn tính SAU khi loại trùng, và vượt thì bỏ qua toàn bộ học
    sinh — KHÔNG âm thầm cắt còn 10."""
    for i in range(1, 13):
        api.create_or_update_club(f"clb_{i:02d}", f"CLB {i}", 20, 0, "")

    cols = ",".join(f"pref_{i}" for i in range(1, 12))
    vals = ",".join(f"clb_{i:02d}" for i in range(1, 12))
    res = api.import_preferences_csv(f"student_id,name,{cols}\nHS910,T,{vals}\n")
    assert res["data"]["n_students_skipped"] == 1
    assert any(w["code"] == "csv_pref_too_many_skipped" for w in res["data"]["warnings"])

    cols = ",".join(f"pref_{i}" for i in range(1, 11))
    vals = ",".join(f"clb_{i:02d}" for i in range(1, 11))
    res = api.import_preferences_csv(f"student_id,name,{cols}\nHS911,T,{vals}\n")
    assert res["data"]["n_students_skipped"] == 0
    assert len(api.get_student_entry_state("HS911")["data"]["ranked_clubs"]) == 10


def test_cot_rank_quyet_dinh_thu_tu_chu_khong_phai_thu_tu_dong(api_co_club):
    res = api_co_club.import_preferences_csv(
        "student_id,name,club_id,rank\n"
        "HS904,T,clb_amnhac,2\n"
        "HS904,T,clb_bongro,1\n"
    )
    assert res["ok"] is True
    state = api_co_club.get_student_entry_state("HS904")["data"]
    assert state["ranked_clubs"] == ["clb_bongro", "clb_amnhac"]


def test_dang_dai_thieu_cot_rank_thi_dung_thu_tu_dong(api_co_club):
    res = api_co_club.import_preferences_csv(
        "student_id,name,club_id\nHS905,T,clb_amnhac\nHS905,T,clb_bongro\n"
    )
    assert res["ok"] is True
    state = api_co_club.get_student_entry_state("HS905")["data"]
    assert state["ranked_clubs"] == ["clb_amnhac", "clb_bongro"]


def test_nhap_lai_GHI_DE_HOAN_TOAN_nguyen_vong_cu(api_co_club):
    """Nhập lại là thay thế, KHÔNG phải cộng dồn — nếu không, sửa một
    nguyện vọng sẽ để lại rác của lần nhập trước."""
    api_co_club.import_preferences_csv(
        "student_id,name,pref_1,pref_2\nHS906,T,clb_bongro,clb_tienganh\n"
    )
    api_co_club.import_preferences_csv("student_id,name,pref_1\nHS906,T,clb_amnhac\n")
    state = api_co_club.get_student_entry_state("HS906")["data"]
    assert state["ranked_clubs"] == ["clb_amnhac"]


def test_hoc_sinh_tao_bang_CSV_KHONG_co_nhom_du_tru(api_co_club):
    """Khoảng trống đã biết, phải nêu rõ trong tài liệu: nhập CSV không
    gán được reserve_group, phải vào màn hình 04 gán riêng. Quên bước
    này thì toàn bộ cơ chế dự trữ của RB-DA không có tác dụng."""
    api_co_club.import_preferences_csv("student_id,name,pref_1\nHS907,T,clb_bongro\n")
    rows = api_co_club.list_students_admin("HS907")["data"]["rows"]
    assert rows[0]["reserve_group"] in (None, "")


# ------------------------------------------------------------------ #
# BỘ MẪU NHIỀU BUỔI — mục 3.7 của HUONG_DAN_CSV.md
# ------------------------------------------------------------------ #
#
# Ba tệp này là thứ ĐẦU TIÊN trường mở ra khi xếp cả tuần. Chúng nằm
# ngoài mọi đường chạy của phần mềm, nên không test thì hỏng âm thầm:
# đổi tên một mã CLB, đổi cách đặt tên cột, hay siết một trần nào đó là
# mẫu sai mà không gì báo.

MAU_NHIEU_BUOI = [
    "06_danh_sach_club_nhieu_buoi.csv",
    "07_chon_club_thi_nhieu_buoi.csv",
    "08_nguyen_vong_nhieu_buoi.csv",
]


def test_bo_mau_nhieu_buoi_nap_sach_khong_mot_canh_bao(api):
    """Nạp đúng thứ tự, không cảnh báo nào, không em nào bị bỏ.

    "Không cảnh báo nào" là điều kiện chặt hơn "nạp được": một tệp mẫu mà
    kêu cảnh báo là tệp mẫu dạy người dùng làm sai.
    """
    for ten in MAU_NHIEU_BUOI:
        kq = api.import_csv_auto(doc_mau(ten))
        assert kq["ok"], (ten, kq)
        d = kq["data"]
        assert d.get("n_students_skipped", 0) == 0, (ten, d)
        assert d.get("n_buoi_bo_qua", 0) == 0, (ten, d)
        assert d["warnings"] == [], (ten, d["warnings"])


def test_bo_mau_nhieu_buoi_xep_duoc_ca_tuan(api):
    for ten in MAU_NHIEU_BUOI:
        api.import_csv_auto(doc_mau(ten))

    d = api.get_danh_sach_buoi()["data"]
    assert d["nhieu_buoi"] is True
    assert d["ds_buoi"] == ["thu_2", "thu_4", "thu_6"]

    kq = api.run_pipeline(seed=42)
    assert kq["ok"], kq
    assert kq["data"]["n_matched"] == kq["data"]["n_total"], (
        "bộ mẫu cố ý dư chỗ — mọi em phải có ít nhất một CLB"
    )


def test_moi_clb_trong_tep_nguyen_vong_deu_dung_buoi_cua_cot(api):
    """Canh đúng lỗi gõ tay mà mục 3.7 cảnh báo.

    Cột `thu_2_pref_*` mà điền một CLB thuộc `thu_4` thì phần mềm bỏ riêng ô
    đó và kêu `nguyen_vong_lech_buoi`. Tệp mẫu KHÔNG được dính lỗi nó đang
    dạy người ta tránh.
    """
    api.import_csv_auto(doc_mau("06_danh_sach_club_nhieu_buoi.csv"))
    kq = api.import_csv_auto(doc_mau("08_nguyen_vong_nhieu_buoi.csv"))
    assert kq["data"]["n_nguyen_vong_lech_buoi"] == 0, kq["data"]["warnings"]


def test_huong_dan_va_tep_mau_noi_cung_mot_bo_ma_clb(api):
    """Hướng dẫn trích mã CLB nào thì tệp mẫu phải có đúng mã đó."""
    import csv as _csv
    import io as _io
    import re as _re

    ma = {
        r["club_id"]
        for r in _csv.DictReader(
            _io.StringIO(doc_mau("06_danh_sach_club_nhieu_buoi.csv")))
    }
    huong_dan = doc_mau("HUONG_DAN_CSV.md")
    muc = huong_dan[huong_dan.index("### 3.7."):]
    muc = muc[:muc.index("\n---\n")]
    la = set(_re.findall(r"clb_[a-z_]+", muc)) - ma
    assert not la, "mục 3.7 nhắc mã CLB không có trong tệp mẫu: %r" % sorted(la)
