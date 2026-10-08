"""
Canh bảng hai cảnh trong du_lieu_test/do_hai_canh_du_tru.py.

Bảng đó được in vào docs/CO_CHE_THUAT_TOAN.md/.html và học sinh sẽ chạy lại
trước hội đồng. Nếu ai sửa club_choice_function mà bảng đổi, test này đỏ
TRƯỚC khi tài liệu nói sai.

Phần lớn test ở đây khoá đúng CON SỐ, không chỉ khoá "chạy không lỗi".
"""

import importlib.util
import io
import os
from contextlib import redirect_stdout

import pytest

from rbda_priority_pipeline import club_choice_function

BO_DO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "du_lieu_test",
    "do_hai_canh_du_tru.py",
)


@pytest.fixture(scope="module")
def bo_do():
    spec = importlib.util.spec_from_file_location("do_hai_canh_du_tru", BO_DO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# Bảng phải giữ nguyên
# --------------------------------------------------------------------------

def test_canh_1_phan_mem_nhan_D_A_B(bo_do):
    """Cảnh 1 — D đỗ, C trượt, dù C xếp TRÊN D.

    Đây là con số cả tài liệu đứng trên. Đổi là tài liệu nói sai.
    """
    assert bo_do.ham_lua_chon_that(["A", "B", "C", "D"]) == ["D", "A", "B"]


def test_canh_1_mo_hinh_mot_danh_sach_nhan_A_B_C(bo_do):
    assert bo_do.mo_hinh_mot_danh_sach(["A", "B", "C", "D"]) == ["A", "B", "C"]


def test_canh_1_hai_ben_LECH(bo_do):
    """Chỗ lệch phải còn đó — nếu hết lệch thì cả tài liệu mất lý do tồn tại."""
    pool = ["A", "B", "C", "D"]
    assert bo_do.ham_lua_chon_that(pool) != bo_do.mo_hinh_mot_danh_sach(pool)


def test_canh_2_hai_ben_KHOP(bo_do):
    """Cảnh 2 — không có ai thuộc diện dự trữ thì hai bên trùng nhau.

    Cảnh đối chứng: chứng minh chỗ lệch ở cảnh 1 đến TỪ suất dự trữ,
    không phải từ một khác biệt lặt vặt nào khác.
    """
    pool = ["A", "B", "C"]
    assert bo_do.ham_lua_chon_that(pool) == bo_do.mo_hinh_mot_danh_sach(pool)
    assert bo_do.ham_lua_chon_that(pool) == ["A", "B", "C"]


def test_C_doi_so_phan_giua_hai_canh(bo_do):
    """Luận điểm trung tâm: cùng em, cùng hạng, khác pool -> khác kết cục."""
    assert "C" not in bo_do.ham_lua_chon_that(["A", "B", "C", "D"])
    assert "C" in bo_do.ham_lua_chon_that(["A", "B", "C"])


def test_uu_tien_nen_giong_nhau_o_ca_hai_canh(bo_do):
    """Canh chính cái làm ví dụ có sức thuyết phục.

    Nếu ai đó sửa ví dụ thành 'mỗi cảnh một thứ hạng khác nhau' thì nó
    không còn chứng minh được gì — lúc đó kết quả khác nhau là đương nhiên.
    """
    assert bo_do.UU_TIEN == {"A": 0, "B": 1, "C": 2, "D": 3}
    assert bo_do.SUC_CHUA == 3
    assert bo_do.SUAT_DU_TRU == 1
    assert bo_do.DIEN_DU_TRU == {"D"}


# --------------------------------------------------------------------------
# Tính chất của hàm lựa chọn, không phụ thuộc ví dụ cụ thể
# --------------------------------------------------------------------------

def test_suat_du_tru_thua_tu_chuyen_sang_luot_chung():
    """'Mềm' nghĩa là suất dự trữ không dùng hết thì trả lại cho lượt chung.

    Nếu bị khoá cứng, CLB đây sẽ chỉ nhận 2 em dù sức chứa 3.
    """
    rank = {"A": 0, "B": 1, "C": 2}
    nhan, _ = club_choice_function(
        pool=["A", "B", "C"],
        capacity=3,
        reserve_capacity=1,
        is_reserve_eligible_fn=lambda s: False,   # không ai thuộc diện dự trữ
        rank=rank,
    )
    assert nhan == ["A", "B", "C"], "suất dự trữ thừa phải chuyển sang lượt chung"


def test_khong_bao_gio_nhan_qua_suc_chua():
    rank = {c: i for i, c in enumerate("ABCDEFGH")}
    nhan, _ = club_choice_function(
        pool=list("ABCDEFGH"),
        capacity=3,
        reserve_capacity=1,
        is_reserve_eligible_fn=lambda s: s in {"G", "H"},
        rank=rank,
    )
    assert len(nhan) == 3


def test_em_dien_du_tru_van_vao_duoc_bang_luot_chung():
    """Em thuộc diện dự trữ mà ưu tiên cao thì chiếm suất CHUNG, không
    tiêu mất suất dự trữ của nhóm mình."""
    rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    nhan, tang = club_choice_function(
        pool=["A", "B", "C", "D"],
        capacity=3,
        reserve_capacity=1,
        is_reserve_eligible_fn=lambda s: s in {"A", "D"},
        rank=rank,
    )
    # A ưu tiên cao nhất và thuộc diện dự trữ -> A lấy suất dự trữ,
    # phần còn lại xét chung.
    assert nhan[0] == "A" and tang["A"] == "reserve"
    assert len(nhan) == 3


# --------------------------------------------------------------------------
# Bộ đo chạy được và in ra đúng những mốc tài liệu trích
# --------------------------------------------------------------------------

def test_chay_duoc_va_in_dung_moc(bo_do):
    buf = io.StringIO()
    with redirect_stdout(buf):
        bo_do.main()
    ra = buf.getvalue()

    assert "*** LỆCH ***" in ra, "cảnh 1 phải báo LỆCH"
    assert "KHỚP" in ra, "cảnh 2 phải báo KHỚP"
    assert "['D', 'A', 'B']" in ra
    assert "['A', 'B', 'C']" in ra
    # Không được lẫn dữ liệu học sinh thật vào ví dụ.
    assert "HS0" not in ra


def test_bo_do_khong_doc_du_lieu_hoc_sinh():
    """Ví dụ phải tự chứa — không mở app.db, không đọc tệp dữ liệu nào."""
    src = open(BO_DO, encoding="utf-8").read()
    for cam in ["app.db", "load_from_sqlite", "connect_db", "open("]:
        assert cam not in src, f"bộ đo không được đụng tới {cam}"
