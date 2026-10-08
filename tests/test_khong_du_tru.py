"""Phần mềm phải chạy đúng cả khi KHÔNG có suất dự trữ nào.

Suất dự trữ sinh ra từ hoàn cảnh trường công. Một trường quốc tế có thể
không cần cơ chế đó và đặt `reserve_capacity = 0` ở mọi CLB. Tệp này khoá
hai mệnh đề:

  1. **Hàm lựa chọn thu về mô hình một danh sách `Q_j`.** Đây không phải
     chuyện làm đẹp: chỗ lệch giữa báo cáo và phần mềm mà
     `docs/CO_CHE_THUAT_TOAN.md` mô tả tồn tại CHỈ VÌ có suất dự trữ. Bỏ dự
     trữ đi thì mô hình trong báo cáo trở thành ĐÚNG.

  2. **Kết quả vẫn ỔN ĐỊNH** — 0 cặp phá vỡ, trên dữ liệu thật, nhiều seed.

Con số bộ đo `du_lieu_test/do_khong_du_tru.py` in ra cũng được khoá ở đây.
"""

import importlib.util
import os
import random
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_DO = os.path.join(GOC, "du_lieu_test", "do_khong_du_tru.py")
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

from rbda_priority_pipeline import club_choice_function  # noqa: E402


@pytest.fixture(scope="module")
def bo_do():
    spec = importlib.util.spec_from_file_location("do_khong_du_tru", BO_DO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------
# 1. MỆNH ĐỀ TRUNG TÂM — không dự trữ thì hàm lựa chọn LÀ mô hình Q_j
# --------------------------------------------------------------------------

def test_khong_du_tru_thi_dung_bang_sap_theo_hang_lay_K_em_dau():
    """Kiểm trên 200 pool ngẫu nhiên, không phải một ví dụ may mắn."""
    rng = random.Random(2026)
    for _ in range(200):
        n = rng.randint(1, 20)
        ma = ["HS%02d" % i for i in range(n)]
        rank = {s: i for i, s in enumerate(rng.sample(ma, n))}
        suc_chua = rng.randint(1, n)
        # diện dự trữ vẫn có người — nhưng suất dự trữ bằng 0
        dien = set(rng.sample(ma, rng.randint(0, n)))

        nhan, tang = club_choice_function(
            pool=list(ma), capacity=suc_chua, reserve_capacity=0,
            is_reserve_eligible_fn=lambda s: s in dien, rank=rank,
        )
        mo_hinh_Qj = sorted(ma, key=lambda s: rank[s])[:suc_chua]
        assert nhan == mo_hinh_Qj
        assert set(tang.values()) <= {"general"}, (
            "không còn suất dự trữ thì không em nào được xếp diện dự trữ")


def test_co_du_tru_thi_KHONG_bang_mo_hinh_Qj():
    """Mệnh đề đối chứng. Nếu thiếu, test trên xanh một cách vô nghĩa —
    nó sẽ xanh cả khi cơ chế dự trữ bị gỡ mất hoàn toàn."""
    rank = {"A": 0, "B": 1, "C": 2, "D": 3}
    nhan, _ = club_choice_function(
        pool=["A", "B", "C", "D"], capacity=3, reserve_capacity=1,
        is_reserve_eligible_fn=lambda s: s == "D", rank=rank,
    )
    assert nhan != ["A", "B", "C"]
    assert nhan == ["D", "A", "B"]


def test_bang_phan_1_cua_bo_do_giu_nguyen(bo_do):
    """Bảng ba dòng mà tài liệu trích: 2 suất LỆCH · 1 suất LỆCH · 0 KHỚP."""
    pool = ["A", "B", "C", "D", "E"]
    mo_hinh = bo_do.mo_hinh_mot_danh_sach(pool)
    assert mo_hinh == ["A", "B", "C"]
    assert bo_do.ham_lua_chon_that(pool, 2) == ["D", "E", "A"]
    assert bo_do.ham_lua_chon_that(pool, 1) == ["D", "A", "B"]
    assert bo_do.ham_lua_chon_that(pool, 0) == mo_hinh, (
        "suất dự trữ 0 phải cho ĐÚNG mô hình Q_j — đây là cả luận điểm")


# --------------------------------------------------------------------------
# 2. Trên dữ liệu thật: vẫn ổn định, và đổi bao nhiêu
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def bo_sach(bo_do, tmp_path_factory):
    import rbda_priority_pipeline as loi
    ten, files = bo_do.BO_DU_LIEU[1]
    assert ten.startswith("bo_sach")
    thu_muc = str(tmp_path_factory.mktemp("bo_sach"))
    return loi.load_from_sqlite(bo_do.nap_bo(thu_muc, files))


def test_bo_het_du_tru_van_cho_ket_qua_on_dinh(bo_do, bo_sach):
    """Điều quan trọng nhất: gỡ cả cơ chế dự trữ ra thì thuật toán vẫn
    đúng. Trường không dùng dự trữ KHÔNG phải sửa gì."""
    khong_dt = bo_do.bo_het_du_tru(bo_sach[1])
    assert all(v["reserve_capacity"] == 0 for v in khong_dt.values())
    for seed in range(1, 6):
        _xep, cap = bo_do.xep_voi_cau_hinh(bo_sach, khong_dt, seed)
        assert cap == [], "seed %d: %d cặp phá vỡ khi bỏ dự trữ" % (seed, len(cap))


def test_bo_het_du_tru_khong_lam_hong_cau_hinh_goc(bo_do, bo_sach):
    """`bo_het_du_tru` phải trả BẢN SAO — sửa vào bản gốc là mọi phép đo
    sau đó trong cùng tiến trình đều sai mà không ai thấy."""
    goc = {c: v["reserve_capacity"] for c, v in bo_sach[1].items()}
    bo_do.bo_het_du_tru(bo_sach[1])
    assert {c: v["reserve_capacity"] for c, v in bo_sach[1].items()} == goc
    assert sum(goc.values()) > 0, "bộ sạch phải CÓ suất dự trữ thì test mới có nghĩa"


def test_con_so_tai_lieu_trich_giu_nguyen(bo_do, bo_sach):
    """TB 32,3 em đổi CLB trên bộ sạch, 20 seed — con số
    docs/CO_CHE_THUAT_TOAN.md và BAN_GIAO.md đang trích."""
    import statistics
    khong_dt = bo_do.bo_het_du_tru(bo_sach[1])
    doi_cho = []
    for seed in range(1, 21):
        co, _ = bo_do.xep_voi_cau_hinh(bo_sach, bo_sach[1], seed)
        kh, _ = bo_do.xep_voi_cau_hinh(bo_sach, khong_dt, seed)
        doi_cho.append(sum(1 for s in bo_sach[0] if co[s] != kh[s]))
    assert round(statistics.mean(doi_cho), 1) == 32.3
    assert (min(doi_cho), max(doi_cho)) == (29, 35)


def test_bo_do_khong_dung_toi_du_lieu_that():
    src = open(BO_DO, encoding="utf-8").read()
    assert '"app.db"' not in src and "'app.db'" not in src
    assert "tempfile.mkdtemp" in src and "shutil.rmtree" in src
