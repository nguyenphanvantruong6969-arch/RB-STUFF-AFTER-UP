# -*- coding: utf-8 -*-
"""Kết quả xếp CLB trên các bộ dữ liệu mẫu phải giữ nguyên TỪNG EM.

Các test khác kiểm TÍNH CHẤT của kết quả: ổn định, không vượt sức chứa,
đúng tầng dự trữ. Chúng không kiểm "em A vẫn vào đúng CLB X". Một lần sửa
cấu trúc mã có thể đổi ai vào đâu mà vẫn giữ nguyên mọi tính chất đó —
và không test nào đỏ.

Tệp này chốt đúng điều ấy: nạp từng bộ mẫu vào CSDL mới, chạy với hạt
giống 42, băm toàn bộ bảng `match_results` đã sắp. Một em đổi CLB là băm
đổi.

Chỉ được cập nhật một giá trị băm khi thay đổi đó CỐ Ý đổi kết quả, và
commit phải nói rõ vì sao. Mã băm hiện tại chốt từ commit 70e07ac.

ĐỐI CHỨNG NGƯỢC đã chạy thật: đảo khoá xếp Tầng 1 trong
`compute_club_priority` thành điểm TĂNG dần → cả sáu test ĐỎ. Khôi phục →
xanh lại.
"""

import hashlib
import io
import os

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BO_MAU = {
    "bo_sach": ("du_lieu_test/bo_sach", "SACH_0%d_%s.csv"),
    "bo_can_bang": ("du_lieu_test/bo_can_bang", "CANBANG_0%d_%s.csv"),
    "bo_nhieu_buoi": ("du_lieu_test/bo_nhieu_buoi", "NHIEUBUOI_0%d_%s.csv"),
    "bo_sau_buoi": ("du_lieu_test/bo_sau_buoi", "SAUBUOI_0%d_%s.csv"),
    "vi_du_huong_dan": ("du_lieu_test/vi_du_huong_dan", "VIDU_0%d_%s.csv"),
    "vi_du_day_du": ("mau_csv/vi_du_day_du", "0%d_%s.csv"),
}
TEN_TEP = ["danh_sach_CLB", "chon_CLB_muon_thi", "xep_hang_nguyen_vong"]

BAM_MONG_DOI = {
    "bo_sach": "b267730be3963b19058096ad98e3895224a013a7611d5552b278abb003a32747",
    "bo_can_bang": "9a3d5f04a32067c1ba38d1874a4a3f18e1209f0fc78cfed46b549662293fdc74",
    "bo_nhieu_buoi": "9bf94b80a2d35e5fabc6a732d0377faf70983e59b3e49b55922b458fab0a22f3",
    "bo_sau_buoi": "dfd955de442fb51da6e831c758c693d5b4de2800fc2deed8af224d442a64e8f3",
    "vi_du_huong_dan": "0306924fe367540bf98632c1ea58f32a81465af556c7a26ba4a6c3c68324a897",
    "vi_du_day_du": "2600700b96508e61cf66c69e84941d4114dd663c65ec392e987d4fbdefeea20b",
}


def bam_ket_qua(api) -> str:
    """Băm SHA-256 của match_results, sắp theo (student_id, buoi)."""
    import sqlite3

    conn = sqlite3.connect(api.db_path)
    try:
        dong = conn.execute(
            "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref "
            "FROM match_results ORDER BY student_id, buoi"
        ).fetchall()
    finally:
        conn.close()
    return hashlib.sha256(repr(dong).encode("utf-8")).hexdigest()


def chay_bo(api, ten_bo: str) -> str:
    thu_muc, mau = BO_MAU[ten_bo]
    for i, ten in enumerate(TEN_TEP, start=1):
        duong_dan = os.path.join(GOC, thu_muc, mau % (i, ten))
        with io.open(duong_dan, encoding="utf-8-sig") as f:
            kq = api.import_csv_auto(f.read())
        assert kq["ok"], (duong_dan, kq.get("errors"))
    kq = api.run_pipeline(seed=42)
    assert kq["ok"], kq.get("errors")
    return bam_ket_qua(api)


@pytest.mark.parametrize("ten_bo", sorted(BO_MAU))
def test_ket_qua_tung_em_khong_doi(api, ten_bo):
    assert chay_bo(api, ten_bo) == BAM_MONG_DOI[ten_bo]
