"""Dữ liệu có HÌNH THÙ LẠ vẫn phải cho kết quả đúng.

`du_lieu_test/thu_tai/` đã quét 204 cấu hình tới 5000 em — nhưng chỉ đổi
QUY MÔ, dữ liệu vẫn bình thường. Lỗi thật hiếm khi nấp ở chỗ "nhiều quá";
nó nấp ở chỗ dữ liệu có hình thù mà người viết không nghĩ tới.

Tệp này là bản NHANH của `du_lieu_test/thu_tai/thu_nghich_canh.py` (bản
đầy đủ chạy tới 2000 em, quá chậm cho mỗi lần chạy test). Cùng những hình
thù đó, quy mô nhỏ hơn, chạy dưới một giây.

Mỗi kịch bản kiểm ba điều: `run_pipeline` trả `ok`, **0 cặp phá vỡ** đọc
lại độc lập từ CSDL, và số vòng dưới trần.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbda_priority_pipeline as loi  # noqa: E402

TRAN_VONG = 1000


def _chay_va_kiem(api):
    kq = api.run_pipeline(seed=42)
    assert kq["ok"] is True, kq["errors"]
    students, clubs, diem, uv, nv, stb = loi.load_from_sqlite(api.db_path)
    fn = loi.default_reserve_eligible_fn(students, clubs)
    res = loi.run_rbda(students, clubs, diem, uv, nv, stb, fn)
    assert loi.verify_stability(res, clubs, nv, fn) == []
    assert res.rounds_run < TRAN_VONG
    return res


def test_moi_em_chi_mot_nguyen_vong_vao_cung_mot_clb(api):
    """Chuỗi từ chối dài nhất: 60 em tranh 5 chỗ, không ai có chỗ lui."""
    api.create_or_update_club("clb_hot", "CLB Hot", 5, 0, "")
    for i in range(60):
        sid = "HS%03d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["clb_hot"])
    res = _chay_va_kiem(api)
    assert sum(1 for v in res.assignment.values() if v) == 5


def test_moi_clb_dung_mot_cho(api):
    """Đẩy dây chuyền tối đa — mỗi lần nhận một em là đẩy một em ra."""
    for j in range(8):
        api.create_or_update_club("c%d" % j, "CLB %d" % j, 1, 0, "")
    for i in range(40):
        sid = "HS%03d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["c%d" % ((i + k) % 8) for k in range(5)])
    res = _chay_va_kiem(api)
    assert sum(1 for v in res.assignment.values() if v) == 8


def test_ca_truong_hoa_diem(api):
    """Cùng một điểm ở mọi CLB — bốc thăm gánh toàn bộ việc phá hoà."""
    for j in range(4):
        api.create_or_update_club("c%d" % j, "CLB %d" % j, 5, 0, "")
    for i in range(40):
        sid = "HS%03d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        ds = ["c%d" % ((i + k) % 4) for k in range(3)]
        api.submit_test_selection(sid, ds)
        for c in ds:
            api.submit_club_scores(c, [{"student_id": sid, "score": 8.0}])
        api.submit_preferences(sid, ds)
    _chay_va_kiem(api)


def test_khong_ai_duoc_cham_diem(api):
    """Toàn Tầng 2 — nhánh ít được chạy nhất của compute_club_priority."""
    for j in range(4):
        api.create_or_update_club("c%d" % j, "CLB %d" % j, 6, 0, "")
    for i in range(40):
        sid = "HS%03d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["c%d" % ((i + k) % 4) for k in range(3)])
    res = _chay_va_kiem(api)
    assert all(t == "general" for t in res.matched_tier.values())


def test_clb_khong_ai_dang_ky_va_em_khong_nguyen_vong(api):
    """Những chỗ dễ chia cho 0 hoặc lấy phần tử của danh sách rỗng."""
    api.create_or_update_club("clb_vang", "Không ai vào", 10, 0, "")
    api.create_or_update_club("clb_vua", "Vừa khít", 1, 0, "")
    api.create_student_if_missing("HS_trong", "Em không nguyện vọng")
    api.create_student_if_missing("HS_co", "Em có nguyện vọng")
    api.submit_preferences("HS_co", ["clb_vua"])
    res = _chay_va_kiem(api)
    assert res.assignment["HS_co"] == "clb_vua"
    assert res.assignment["HS_trong"] is None


def test_suat_du_tru_bang_toan_bo_suc_chua(api):
    """`reserve_capacity == capacity` — lượt chung không còn chỗ nào."""
    for j in range(3):
        api.create_or_update_club("c%d" % j, "CLB %d" % j, 4, 4, "uu_tien")
    for i in range(30):
        sid = "HS%03d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["c%d" % ((i + k) % 3) for k in range(2)])
        if i % 3 == 0:
            api.set_student_reserve_group(sid, "uu_tien")
    res = _chay_va_kiem(api)
    # Suất dự trữ mềm: không đủ em thuộc diện thì phần thừa vẫn lấp được
    assert sum(1 for v in res.assignment.values() if v) == 12


def test_nap_theo_dot_giu_nguyen_thu_tu_em_cu(api):
    """Bản nhanh của kịch bản quan trọng nhất: nạp → chạy → nạp thêm →
    chạy lại. Đường chèn ngẫu nhiên cho em vào sau phải giữ thứ tự tương
    đối của em cũ qua MỌI đợt, không chỉ đợt đầu."""
    import sqlite3
    for j in range(5):
        api.create_or_update_club("c%d" % j, "CLB %d" % j, 8, 0, "")

    def bo_so():
        conn = sqlite3.connect(api.db_path)
        try:
            return dict(conn.execute(
                "SELECT student_id, stb_number FROM students "
                "WHERE stb_number IS NOT NULL"))
        finally:
            conn.close()

    truoc = {}
    for d in range(4):
        for i in range(d * 25, (d + 1) * 25):
            sid = "HS%03d" % i
            api.create_student_if_missing(sid, "Em %d" % i)
            api.submit_preferences(sid, ["c%d" % ((i + k) % 5) for k in range(3)])
        _chay_va_kiem(api)
        sau = bo_so()
        if truoc:
            cu = sorted(truoc)
            assert sorted(cu, key=lambda s: truoc[s]) == sorted(cu, key=lambda s: sau[s]), (
                "đợt %d đảo thứ tự tương đối của các em đã có" % (d + 1))
        truoc = sau
    assert len(truoc) == 100


@pytest.mark.parametrize("ten", [
    "Nguyễn Văn Ðạt", "=1+1", "@SUM(A1:A9)", "A" * 300, "Lê\tMinh\nCường", "☃ ⚡ 学生",
])
def test_ten_hoc_sinh_hiem_van_chay_tron_vong(api, ten):
    """Tên trông như công thức Excel, có tab/xuống dòng, rất dài, hoặc
    ngoài bảng mã thông dụng — vẫn phải đi trọn vòng nạp → chạy → xuất."""
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    api.create_student_if_missing("HS01", ten)
    api.submit_preferences("HS01", ["clb_a"])
    _chay_va_kiem(api)
    xuat = api.export_csv()
    assert xuat["ok"] is True, xuat["errors"]
    assert os.path.isfile(xuat["data"]["path"])
