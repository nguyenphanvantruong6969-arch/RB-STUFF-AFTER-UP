# -*- coding: utf-8 -*-
"""Số bốc thăm không được phụ thuộc THỨ TỰ NHẬP học sinh.

Cả dự án đứng trên một lời hứa: *cùng dữ liệu và cùng `seed` thì luôn
ra cùng kết quả, ai cầm dữ liệu cũng dựng lại được để kiểm chứng*. Lời
hứa đó viết trong `HUONG_DAN_SU_DUNG.md` mục 06.

`random.shuffle` xáo **đúng danh sách được đưa vào**, và
`load_from_sqlite` đọc bảng `students` không có `ORDER BY` nên trả về
theo thứ tự chèn. Không sắp xếp trước khi xáo thì lời hứa trên chỉ đúng
khi thứ tự nhập cũng giống nhau — một điều kiện không ai ghi lại và
không màn hình nào hiển thị.

Lỗi thuộc loại ẩn cho tới đúng lúc cần: người ta chỉ chạy lại pipeline
khi MUỐN KIỂM CHỨNG, mà lúc đó thường là vừa nhập lại dữ liệu.
"""

import sqlite3

import pytest

from rbda_priority_pipeline import generate_stb_lottery

HOC_SINH = [("HS%02d" % i, "Học sinh %02d" % i) for i in range(1, 11)]


def _dung(api, thu_tu):
    """Dựng cùng một trường, chỉ khác THỨ TỰ tạo học sinh.

    Điểm để bằng nhau hết, có chủ ý: khi mọi em cùng điểm thì thứ hạng
    hoàn toàn do số bốc thăm quyết định, nên nếu bốc thăm lệch là kết
    quả lệch theo ngay — không bị điểm che mất.
    """
    api.create_or_update_club("clb_a", "CLB A", 3, 0, "")
    api.create_or_update_club("clb_b", "CLB B", 3, 0, "")
    for sid, ten in thu_tu:
        api.create_student_if_missing(sid, ten)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a", "clb_b"])
        api.submit_club_scores("clb_a", [{"student_id": sid, "score": 8.0}])
    assert api.run_pipeline(seed=42)["ok"]
    conn = sqlite3.connect(api.db_path)
    kq = dict(conn.execute(
        "SELECT student_id, COALESCE(club_id, '') FROM match_results").fetchall())
    stb = dict(conn.execute("SELECT student_id, stb_number FROM students").fetchall())
    conn.close()
    return kq, stb


def test_hai_thu_tu_nhap_nguoc_nhau_cho_cung_ket_qua(api, tmp_path):
    """Đây là test chính. Trước bản vá: 6/10 em được xếp khác CLB."""
    from api import PipelineAPI

    xuoi_kq, xuoi_stb = _dung(api, HOC_SINH)
    api2 = PipelineAPI(str(tmp_path / "nguoc.db"))
    nguoc_kq, nguoc_stb = _dung(api2, list(reversed(HOC_SINH)))

    khac = {sid for sid in xuoi_kq if xuoi_kq[sid] != nguoc_kq.get(sid)}
    assert not khac, "nhap nguoc thu tu ra ket qua khac o: %s" % sorted(khac)
    assert xuoi_stb == nguoc_stb


def test_ham_boc_tham_chi_phu_thuoc_TAP_ma_hoc_sinh(api):
    """Kiểm thẳng ở tầng hàm, không qua CSDL."""
    ma = ["HS%02d" % i for i in range(1, 13)]
    assert generate_stb_lottery(ma, 42) == generate_stb_lottery(list(reversed(ma)), 42)
    import random
    xao = ma[:]
    random.Random(999).shuffle(xao)
    assert generate_stb_lottery(ma, 42) == generate_stb_lottery(xao, 42)


def test_van_la_boc_tham_that_chu_khong_phai_xep_theo_ma(api):
    """Chặn cách hiểu sai: “số bốc thăm dựa trên mã học sinh”.

    Sắp xếp chỉ để danh sách đầu vào có một trật tự cố định; xáo xong
    thì mã không còn vai trò gì. Nếu ai đó lỡ bỏ mất bước xáo, hàm sẽ
    trả về đúng thứ tự mã — và test này đỏ.
    """
    ma = ["HS%02d" % i for i in range(1, 13)]
    stb = generate_stb_lottery(ma, 42)

    assert sorted(stb.values()) == list(range(len(ma)))      # mỗi em một số
    assert [stb[m] for m in ma] != list(range(len(ma))), \
        "so boc tham dang trung khop thu tu ma — buoc xao da bi mat"
    assert stb[ma[0]] != 0, "ma nho nhat khong duoc mac dinh nhan so uu tien nhat"


def test_doi_seed_thi_doi_ket_qua_boc_tham(api):
    """Vá quá tay thành cố định thì test này đỏ: seed phải còn tác dụng."""
    ma = ["HS%02d" % i for i in range(1, 13)]
    a, b = generate_stb_lottery(ma, 42), generate_stb_lottery(ma, 7)
    giu_nguyen = sum(1 for m in ma if a[m] == b[m])
    assert giu_nguyen < len(ma) // 2, "doi seed ma bo so gan nhu khong doi"


@pytest.mark.parametrize("seed", [0, 1, 42, 2026])
def test_moi_seed_deu_sinh_bo_so_hop_le(api, seed):
    ma = ["HS%03d" % i for i in range(1, 51)]
    stb = generate_stb_lottery(ma, seed)
    assert set(stb) == set(ma)
    assert sorted(stb.values()) == list(range(len(ma)))
