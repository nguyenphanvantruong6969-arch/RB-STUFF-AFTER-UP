"""`list_students_admin` phải trả TÊN CLB em đã chọn, để thẻ tìm kiếm ở
thẻ Nhập tại chỗ nói được em chọn NHỮNG CLB nào, không chỉ bao nhiêu."""


def _dung(api):
    api.create_or_update_club("robot", "CLB Robot", 5, 0, "", "thu_3")
    api.create_or_update_club("ve", "CLB Vẽ", 5, 0, "", "thu_5")
    api.create_student_if_missing("HS01", "An")
    api.create_student_if_missing("HS02", "Bình")
    assert api.submit_test_selection("HS01", ["ve", "robot"])["ok"]
    assert api.submit_preferences("HS01", ["ve", "robot"])["ok"]


def test_tra_ten_clb_thi_va_nguyen_vong_theo_thu_tu(api):
    _dung(api)
    rows = {r["student_id"]: r for r in api.list_students_admin("", 1, 50)["data"]["rows"]}
    hs = rows["HS01"]
    assert sorted(c["name"] for c in hs["tested_clubs"]) == ["CLB Robot", "CLB Vẽ"]
    assert [(c["club_id"], c["rank"]) for c in hs["ranked_clubs"]] == [("ve", 1), ("robot", 2)]
    assert {c["buoi"] for c in hs["ranked_clubs"]} == {"thu_3", "thu_5"}
    # Trường cũ vẫn còn cho thẻ Quản lý.
    assert hs["n_tested"] == 2 and hs["n_ranked"] == 2


def test_em_chua_chon_gi_nhan_danh_sach_rong(api):
    _dung(api)
    rows = {r["student_id"]: r for r in api.list_students_admin("", 1, 50)["data"]["rows"]}
    assert rows["HS02"]["tested_clubs"] == []
    assert rows["HS02"]["ranked_clubs"] == []


def test_chi_lay_cho_em_khop_tim_kiem(api):
    _dung(api)
    rows = api.list_students_admin("Bình", 1, 50)["data"]["rows"]
    assert [r["student_id"] for r in rows] == ["HS02"]
