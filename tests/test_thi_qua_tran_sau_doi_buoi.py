# -*- coding: utf-8 -*-
"""Số CLB đăng ký thi trong MỘT buổi vượt trần sau khi CLB đổi buổi.

VẤN ĐỀ. Trần "tối đa 5 CLB thi mỗi buổi" chỉ được kiểm ở CỬA NHẬP
(`submit_test_selection`, `import_test_selection_csv`). Sau đó
`load_from_sqlite` trộn ô tick thi với nguyện vọng thành một `applicants`
duy nhất, nên `validate_data_integrity` không còn tách ra được để kiểm lại.

Mà dữ liệu đã nhập vẫn đổi được về sau: màn Quản lý cho đổi buổi của CLB
(`create_or_update_club`). Em tick 3 CLB thứ Hai + 3 CLB thứ Ba — hợp lệ —
rồi nhà trường chuyển 3 CLB thứ Ba sang thứ Hai là em đó đang thi 6 CLB
trong một buổi, và không màn hình nào nói ra. Nguyện vọng vượt trần theo
cùng đường ấy thì bị chặn (`pref_too_many_buoi`); ô tick thi thì không.

Thi thêm CLB là thêm chỗ được xét ở Tầng 1, nên đây là chuyện công bằng,
không chỉ là chuyện hình thức. Nhưng thuật toán vẫn chạy đúng với dữ liệu
đó, nên đây là CẢNH BÁO (bảng sức khoẻ dữ liệu), không phải lỗi chặn chạy.
"""


import rbda_priority_pipeline as loi


def _ma(bao_cao):
    return [w["code"] for w in bao_cao["data"]["warnings"]]


def _canh_bao(bao_cao, ma):
    return [w for w in bao_cao["data"]["warnings"] if w["code"] == ma]


def _dung(api, buoi_a="thu_2", buoi_b="thu_3"):
    for i in range(1, 4):
        assert api.create_or_update_club("a%d" % i, "A%d" % i, 5, 0, "", buoi_a)["ok"]
        assert api.create_or_update_club("b%d" % i, "B%d" % i, 5, 0, "", buoi_b)["ok"]
    for sid in ("HS1", "HS2"):
        assert api.create_student_if_missing(sid, "Em " + sid)["ok"]
    sau = ["a1", "a2", "a3", "b1", "b2", "b3"]
    assert api.submit_test_selection("HS1", sau)["ok"]
    assert api.submit_test_selection("HS2", ["a1", "b1"])["ok"]
    return sau


def _doi_buoi(api, ds, buoi):
    for cid in ds:
        assert api.create_or_update_club(cid, cid.upper(), 5, 0, "", buoi)["ok"]


def test_hop_le_luc_nhap_thi_khong_canh_bao(api):
    _dung(api)
    assert "health_thi_qua_tran_buoi" not in _ma(api.get_data_health_report())
    assert "health_thi_qua_tran" not in _ma(api.get_data_health_report())


def test_doi_buoi_lam_vuot_tran_thi_canh_bao_neu_ten_em_va_buoi(api):
    _dung(api)
    _doi_buoi(api, ["b1", "b2", "b3"], "thu_2")
    cb = _canh_bao(api.get_data_health_report(), "health_thi_qua_tran_buoi")
    assert len(cb) == 1
    assert cb[0]["severity"] == "high"
    assert cb[0]["params"]["buoi"] == "thu_2"
    assert cb[0]["params"]["n"] == 1
    assert cb[0]["params"]["tran"] == loi.TRAN_CLB_THI_MOI_BUOI
    assert "HS1 (6)" in cb[0]["params"]["sample"]
    assert "HS2" not in cb[0]["params"]["sample"]


def test_truong_mot_buoi_khong_neu_ten_buoi_noi_bo(api):
    """Bỏ trống buổi của mọi CLB = trường một buổi. Câu cảnh báo không được
    đọc lên cái nhãn nội bộ `__mac_dinh__`."""
    _dung(api)
    _doi_buoi(api, ["a1", "a2", "a3", "b1", "b2", "b3"], "")
    bao_cao = api.get_data_health_report()
    assert "health_thi_qua_tran_buoi" not in _ma(bao_cao)
    cb = _canh_bao(bao_cao, "health_thi_qua_tran")
    assert len(cb) == 1
    assert "buoi" not in cb[0]["params"]
    assert "HS1 (6)" in cb[0]["params"]["sample"]


def test_canh_bao_khong_chan_chay(api):
    _dung(api)
    for sid, ds in (("HS1", ["a1", "b1"]), ("HS2", ["a1"])):
        assert api.submit_preferences(sid, ds)["ok"]
    _doi_buoi(api, ["b1", "b2", "b3"], "thu_2")
    assert api.run_pipeline(seed=42)["ok"]


def test_load_from_sqlite_tach_ro_hai_khai_niem(api):
    """`hop_ung_vien` là chỗ DUY NHẤT trộn ô tick thi với nguyện vọng."""
    dang_ky_thi = {"c1": ["HS1"], "c2": []}
    nguyen_vong = {"HS2": ["c1", "c2"], "HS1": ["c1"]}
    ra = loi.hop_ung_vien(dang_ky_thi, nguyen_vong)
    assert ra == {"c1": ["HS1", "HS2"], "c2": ["HS2"]}
    # Không sửa đầu vào.
    assert dang_ky_thi == {"c1": ["HS1"], "c2": []}


def test_sua_theo_loi_chi_dan_thi_het_canh_bao(api):
    """Câu cảnh báo bảo sửa ở màn Nhập tại chỗ — con đường đó phải đi được:
    bỏ bớt ô thi về đúng trần là lưu được và cảnh báo biến mất."""
    _dung(api)
    _doi_buoi(api, ["b1", "b2", "b3"], "thu_2")
    assert api.get_student_entry_state("HS1")["ok"]
    assert api.submit_test_selection("HS1", ["a1", "a2", "a3", "b1", "b2"])["ok"]
    bao_cao = api.get_data_health_report()
    assert "health_thi_qua_tran_buoi" not in _ma(bao_cao)
