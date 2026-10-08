# -*- coding: utf-8 -*-
"""Các ca hiếm của vòng NẠP → XUẤT, tìm ra ngày 30/08 bằng cách chạy thử.

Cả ba lỗi ở đây đều IM LẶNG: phần mềm báo thành công, người dùng không
thấy dấu hiệu nào, mà dữ liệu đã sai.
"""

import csv
import io
import os

import pytest


@pytest.fixture
def api_co_club(api):
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    return api


def doc(path):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


# ------------------------------------------------------------------ #
# 1. Ô có dấu nháy kép bị csv.Sniffer đọc sai
# ------------------------------------------------------------------ #
def test_ten_co_dau_nhay_va_dau_phay_van_nap_dung(api_co_club):
    """csv.Sniffer đoán doublequote=False, làm vỡ quy ước "" của CSV.
    Ô tên bị cắt ngay dấu phẩy, phần đuôi trôi sang cột kế bên và bị hiểu
    là mã club — cả dòng bị bỏ, kèm cảnh báo "club không tồn tại" chẳng
    liên quan gì tới nguyên nhân thật."""
    ten = 'Trần "Bo" Văn A, Jr.'
    r = api_co_club.import_csv_auto(
        'student_id,name,test_club_1\nHS1,"%s",clb_a\n' % ten.replace('"', '""')
    )
    assert r["ok"], r["errors"]
    assert r["data"]["n_students_with_selection_written"] == 1, r["data"]
    rows = api_co_club.list_students_admin()["data"]["rows"]
    assert [x["name"] for x in rows] == [ten]


def test_ten_club_co_dau_nhay_van_nap_dung(api):
    """Tên CLB tiếng Việt rất hay có dấu nháy: CLB "Vì Cộng Đồng"."""
    ten = 'CLB "Vì Cộng Đồng"'
    r = api.import_csv_auto(
        'club_id,name,capacity\nclb_vcd,"%s",10\n' % ten.replace('"', '""')
    )
    assert r["ok"], r["errors"]
    assert [c["name"] for c in api.list_clubs()["data"]] == [ten]


@pytest.mark.parametrize("dau", [",", ";", "\t"])
def test_van_tu_nhan_ra_dau_phan_cach(api, dau):
    """Sửa cách dùng Sniffer thì KHÔNG được làm mất khả năng nhận ; và Tab
    — Excel bản tiếng Việt hay lưu ra dấu chấm phẩy."""
    r = api.import_csv_auto(
        dau.join(["club_id", "name", "capacity"]) + "\n" +
        dau.join(["clb_x", "CLB X", "7"]) + "\n"
    )
    assert r["ok"], r["errors"]
    assert r["data"]["n_clubs_created"] == 1


# ------------------------------------------------------------------ #
# 2. Excel coi ô bắt đầu bằng = + - @ là công thức
# ------------------------------------------------------------------ #
def _chay_mot_em(api, ten):
    api.import_csv_auto('student_id,name,test_club_1\nHS1,"%s",clb_a\n' % ten)
    api.import_csv_auto('student_id,name,pref_1\nHS1,"%s",clb_a\n' % ten)
    api.submit_club_scores("clb_a", [{"student_id": "HS1", "score": 9}])
    assert api.run_pipeline(seed=42)["ok"]
    return api.export_csv()["data"]["path"]


@pytest.mark.parametrize("ten", ["=1+1", "+84901234567", "-Anh", "@Nam"])
def test_o_giong_cong_thuc_duoc_chan_truoc_khi_xuat(api_co_club, ten):
    """Không chặn thì Excel TÍNH ô đó: học sinh tên '=1+1' hiện ra là 2,
    và giáo viên không có cách nào biết tên thật."""
    path = _chay_mot_em(api_co_club, ten)
    tho = io.open(path, encoding="utf-8-sig").read().splitlines()[1]
    o_ten = next(iter(csv.reader([tho])))[1]
    assert o_ten.startswith("'"), "ô %r chưa được chặn" % o_ten
    assert o_ten[1:] == ten


def test_ten_binh_thuong_khong_bi_them_dau_nhay(api_co_club):
    path = _chay_mot_em(api_co_club, "Nguyễn Văn An")
    assert doc(path)[1][1] == "Nguyễn Văn An"


# ------------------------------------------------------------------ #
# 3. Tệp của lần xuất trước còn sót lại
# ------------------------------------------------------------------ #
def _hai_lan_xuat(api):
    for cid in ("clb_a", "clb_b"):
        api.create_or_update_club(cid, "CLB " + cid[-1].upper(), 5, 0, "")
    api.import_csv_auto(
        "student_id,name,test_club_1,test_club_2\n"
        "HS1,An,clb_a,clb_b\nHS2,Binh,clb_a,clb_b\n")
    api.import_csv_auto("student_id,name,pref_1\nHS1,An,clb_b\nHS2,Binh,clb_b\n")
    for c in ("clb_a", "clb_b"):
        api.submit_club_scores(c, [{"student_id": "HS1", "score": 9},
                                   {"student_id": "HS2", "score": 8}])
    api.run_pipeline(seed=42)
    # Xuất vào ĐÚNG MỘT chỗ cả hai lần. Khi người dùng không tự chọn
    # đường dẫn, phần mềm tránh ghi đè bằng hậu tố "(2)" nên mỗi lần xuất
    # là một thư mục riêng — lúc đó không có tệp cũ nào để lẫn. Việc dọn
    # tệp cũ chỉ áp dụng khi CÙNG một chỗ bị xuất đè lên, và đó chính là
    # thứ test này canh.
    dich = os.path.join(os.path.dirname(api.db_path), "ket_qua.csv")
    thu_muc = api.export_csv(dich)["data"]["per_club_dir"]
    # Trường sửa lại nguyện vọng: không ai chọn clb_b nữa.
    api.import_csv_auto("student_id,name,pref_1\nHS1,An,clb_a\nHS2,Binh,clb_a\n")
    api.run_pipeline(seed=42)
    api.export_csv(dich)
    return thu_muc


def test_khong_con_tep_cua_lan_xuat_truoc(api):
    """CLB không còn ai vào mà tệp cũ vẫn nằm đó, trông y hệt tệp thật —
    giáo viên cầm nhầm đi tổ chức một CLB không còn học sinh nào."""
    thu_muc = _hai_lan_xuat(api)
    assert sorted(os.listdir(thu_muc)) == ["clb_a.csv"]


def test_khong_xoa_tep_khac_cua_nguoi_dung(api):
    """Dọn tệp cũ là thao tác XOÁ — chỉ được đụng vào .csv do phần mềm
    sinh ra, không được đụng bất cứ thứ gì khác người dùng để trong đó."""
    for cid in ("clb_a",):
        api.create_or_update_club(cid, "CLB A", 5, 0, "")
    api.import_csv_auto("student_id,name,test_club_1\nHS1,An,clb_a\n")
    api.import_csv_auto("student_id,name,pref_1\nHS1,An,clb_a\n")
    api.submit_club_scores("clb_a", [{"student_id": "HS1", "score": 9}])
    api.run_pipeline(seed=42)
    dich = os.path.join(os.path.dirname(api.db_path), "ket_qua.csv")
    thu_muc = api.export_csv(dich)["data"]["per_club_dir"]
    ghi_chu = os.path.join(thu_muc, "ghi_chu_cua_thay.txt")
    io.open(ghi_chu, "w", encoding="utf-8").write("đừng xoá tôi")
    api.export_csv(dich)
    assert os.path.exists(ghi_chu), "đã xoá nhầm tệp của người dùng"
    assert io.open(ghi_chu, encoding="utf-8").read() == "đừng xoá tôi"
