"""Khoá các lỗi P1 tìm được trong đợt rà soát toàn chương trình (26/09).

Mỗi test dưới đây dựng ĐÚNG tình huống đã làm hỏng bản cũ, và đã được
chạy ngược trên mã trước bản vá để chắc chắn nó ĐỎ vì đúng lý do.
"""

import os
import sqlite3
import threading
import time

import pytest

import rbda_priority_pipeline as rp
from recovery import RecoveryAPI


# ------------------------------------------------------------------ #
# B1 — tệp nguyện vọng dạng dài có dòng thiếu ô cuối
# ------------------------------------------------------------------ #


def test_dong_ngan_trong_tep_nguyen_vong_dang_dai_khong_lam_hong_ca_lan_nhap(api):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_or_update_club("B", "CLB B", 5, 0, "")
    # Dòng cuối thiếu ô rank: DictReader điền None, bản cũ gọi None.isdigit().
    res = api.import_preferences_csv(
        "student_id,name,club_id,rank\n"
        "hs1,An,A,1\n"
        "hs1,An,B\n"
    )
    assert res["ok"] is True, res["errors"]
    with sqlite3.connect(api.db_path) as c:
        thu_tu = [r[0] for r in c.execute(
            "SELECT club_id FROM preferences WHERE student_id='hs1' ORDER BY rank")]
    assert thu_tu == ["A", "B"]


# ------------------------------------------------------------------ #
# B2 — tick trùng một CLB
# ------------------------------------------------------------------ #


def test_tick_trung_mot_clb_khong_lam_hong_ca_lan_luu(api):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_student_if_missing("hs1", "An")
    res = api.submit_test_selection("hs1", ["A", "A"])
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_selected"] == 1


# ------------------------------------------------------------------ #
# B3 — lỗi giữa chừng không được để kết nối mở
# ------------------------------------------------------------------ #


def test_muc_diem_sai_kieu_bi_bo_qua_chu_khong_nem_loi(api):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_student_if_missing("hs1", "An")
    api.submit_test_selection("hs1", ["A"])
    res = api.submit_club_scores("A", ["khong-phai-dict", {"student_id": "hs1", "score": 8}])
    assert res["ok"] is True, res["errors"]
    assert res["data"]["n_saved"] == 1
    assert res["data"]["warnings"]


@pytest.mark.parametrize("ten_ham, tham_so", [
    ("submit_test_selection", ("hs1", ["A"])),
    ("submit_preferences", ("hs1", ["A"])),
    ("reset_student_entry", ("hs1",)),
    ("delete_student", ("hs1",)),
    ("set_student_reserve_group", ("hs1", "x")),
    ("delete_club", ("A",)),
    ("submit_club_scores", ("A", [{"student_id": "hs1", "score": 1}])),
])
def test_ham_ghi_luon_dong_ket_noi_ke_ca_khi_loi(api, monkeypatch, ten_ham, tham_so):
    """Đếm kết nối mở/đóng quanh một lời gọi hỏng giữa chừng.

    Bản cũ tự gọi connect_db rồi đóng ở cuối khối try: lỗi ở giữa là kết
    nối (và tệp app.db trên Windows) bị bỏ mở.
    """
    import api as api_mod

    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_student_if_missing("hs1", "An")
    api.submit_test_selection("hs1", ["A"])

    that = api_mod.connect_db
    dang_mo = []

    class _KetNoi:
        def __init__(self, conn):
            self._c = conn
            dang_mo.append(self)

        def cursor(self):
            c = self._c.cursor()

            class _Tro:
                def __getattr__(_, ten):
                    if ten in ("execute", "executemany"):
                        def no(sql, *a, **k):
                            if sql.lstrip().upper().startswith(("DELETE", "INSERT", "UPDATE")):
                                raise sqlite3.OperationalError("gia vo o day")
                            return getattr(c, ten)(sql, *a, **k)
                        return no
                    return getattr(c, ten)
            return _Tro()

        def close(self):
            dang_mo.remove(self)
            self._c.close()

        def __getattr__(self, ten):
            return getattr(self._c, ten)

    monkeypatch.setattr(api_mod, "connect_db", lambda p: _KetNoi(that(p)))
    res = getattr(api, ten_ham)(*tham_so)
    assert res["ok"] is False
    assert dang_mo == [], "ket noi con mo sau loi"


# ------------------------------------------------------------------ #
# B4/B5 — hai lời gọi ghi song song phải xếp hàng
# ------------------------------------------------------------------ #


def test_luu_nguyen_vong_trong_luc_dang_chay_phai_cho_chu_khong_chen_vao(api, monkeypatch):
    """Nguyện vọng lưu ĐÚNG LÚC pipeline đang chạy từng bị kết quả tính
    từ dữ liệu cũ đè lên. Giờ nó phải chờ lần chạy xong rồi mới ghi."""
    import api as api_mod

    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_or_update_club("B", "CLB B", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nhs1,An,A\n")
    # Chạy một lần để số bốc thăm được KHOÁ: lần chạy sau không vẽ lại,
    # nên không mở giao dịch SQLite nào trong lúc tính — đúng tình huống
    # mà chỉ khoá của SQLite không che được.
    api.run_pipeline(seed=1)

    trong_luc_chay = threading.Event()
    goc = api_mod.run_rbda_nhieu_buoi

    def cham(*a, **k):
        trong_luc_chay.set()
        time.sleep(0.5)
        return goc(*a, **k)

    monkeypatch.setattr(api_mod, "run_rbda_nhieu_buoi", cham)
    thu_tu = []

    def chay():
        api.run_pipeline(seed=1)
        thu_tu.append("chay_xong")

    t = threading.Thread(target=chay)
    t.start()
    assert trong_luc_chay.wait(5)
    api.submit_preferences("hs1", ["B"])
    thu_tu.append("luu_xong")
    t.join(10)
    assert thu_tu == ["chay_xong", "luu_xong"]


def test_hai_lan_bam_chay_cung_luc_khong_ve_so_boc_tham_hai_lan(api, monkeypatch):
    import api as api_mod

    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nhs1,An,A\nhs2,Binh,A\n")
    dem = {"ve": 0}
    goc = api_mod.generate_stb_lottery

    def dem_ve(*a, **k):
        dem["ve"] += 1
        time.sleep(0.3)
        return goc(*a, **k)

    monkeypatch.setattr(api_mod, "generate_stb_lottery", dem_ve)
    ts = [threading.Thread(target=api.run_pipeline, kwargs={"seed": 1}) for _ in range(2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(20)
    # Lần đầu vẽ rồi KHOÁ; lần hai thấy đã khoá nên dùng lại.
    assert dem["ve"] == 1


# ------------------------------------------------------------------ #
# B6 — suất dự trữ âm
# ------------------------------------------------------------------ #


def test_ham_lua_chon_tu_choi_suc_chua_sai_thay_vi_cat_bang_so_am():
    with pytest.raises(ValueError):
        rp.club_choice_function(["a", "b", "c"], 2, -1, lambda s: True,
                                {"a": 0, "b": 1, "c": 2})


def test_kiem_du_lieu_bat_du_tru_am():
    loi = rp.validate_data_integrity(
        {}, {"c": {"capacity": 2, "reserve_capacity": -1}}, {}, {})
    assert [e["code"] for e in loi] == ["club_reserve_negative"]


def test_form_clb_tu_choi_du_tru_am(api):
    res = api.create_or_update_club("A", "CLB A", 5, -1, "")
    assert res["ok"] is False
    assert res["errors"][0]["code"] == "reserve_capacity_negative"


def test_tep_clb_bo_qua_dong_du_tru_am(api):
    res = api.import_clubs_csv(
        "club_id,name,capacity,reserve_capacity\nA,CLB A,5,-1\nB,CLB B,5,1\n")
    with sqlite3.connect(api.db_path) as c:
        ma = {r[0] for r in c.execute("SELECT club_id FROM clubs")}
    assert ma == {"B"}, res


def test_form_clb_tra_ve_ma_da_cat_khoang_trang(api):
    res = api.create_or_update_club("  A  ", " CLB A ", 5, 0, "")
    assert res["data"]["club_id"] == "A"


# ------------------------------------------------------------------ #
# B7 — số bốc thăm trùng hoặc rỗng
# ------------------------------------------------------------------ #


def test_so_boc_tham_trung_khong_de_thu_tu_nhap_quyet_dinh():
    xuoi = rp.compute_club_priority("c", ["b", "a"], {"a": 5, "b": 5}, {"a": 1, "b": 1})
    nguoc = rp.compute_club_priority("c", ["a", "b"], {"a": 5, "b": 5}, {"a": 1, "b": 1})
    assert xuoi == nguoc == ["a", "b"]


def test_so_boc_tham_none_bao_thieu_chu_khong_nem_typeerror():
    with pytest.raises(ValueError, match="thiếu số bốc"):
        rp.compute_club_priority("c", ["a", "b"], {}, {"a": None, "b": 1})


def test_ma_lap_khong_de_lo_trong_day_so_boc_tham():
    so = rp.generate_stb_lottery(["a", "a", "b"], seed=1)
    assert sorted(so.values()) == [0, 1]


# ------------------------------------------------------------------ #
# B8 — hợp đồng {ok, data, errors: [...]}
# ------------------------------------------------------------------ #


def test_that_bai_cua_pipeline_van_tra_errors_la_danh_sach(api, monkeypatch):
    import api as api_mod

    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nhs1,An,A\n")

    def no(*a, **k):
        raise RuntimeError("gia vo hong")
    monkeypatch.setattr(api_mod, "run_rbda_nhieu_buoi", no)
    res = api.run_pipeline(seed=1)
    assert res["ok"] is False
    assert isinstance(res["errors"], list)
    assert any(s["status"] == "error" for s in res["data"]["steps"])


# ------------------------------------------------------------------ #
# B9 — màn hình phục hồi
# ------------------------------------------------------------------ #


def test_phuc_hoi_khong_doi_ten_csdl_con_tot(api):
    """Lỗi khởi động vì quyền ghi hay tệp bị khoá cũng mở màn hình này.
    CSDL còn nguyên thì không được dời đi."""
    rec = RecoveryAPI(api.db_path, "PermissionError gia lap")
    for ham in (rec.start_fresh, rec.restore_from_backup):
        res = ham()
        assert res["ok"] is False
        assert res["errors"][0]["code"] == "recovery_db_is_healthy"
    assert os.path.exists(api.db_path)
    assert not [f for f in os.listdir(os.path.dirname(api.db_path)) if ".corrupt-" in f]


def test_phuc_hoi_doi_ca_tep_journal_di_kem(tmp_path):
    """Journal để sót lại sẽ bị SQLite "phục hồi" vào app.db mới chép vào."""
    db = tmp_path / "app.db"
    db.write_bytes(b"hong hoan toan")
    (tmp_path / "app.db-journal").write_bytes(b"journal cu")
    aside = RecoveryAPI(str(db), "hong")._move_corrupt_db_aside()
    assert not (tmp_path / "app.db-journal").exists()
    with open(aside + "-journal", "rb") as f:
        assert f.read() == b"journal cu"


def test_bat_dau_lai_dung_lai_neu_khong_doi_ten_duoc(tmp_path, monkeypatch):
    import recovery

    db = tmp_path / "app.db"
    db.write_bytes(b"hong hoan toan")

    def khoa(*a, **k):
        raise PermissionError("tep dang bi khoa")
    monkeypatch.setattr(recovery.shutil, "move", khoa)
    res = RecoveryAPI(str(db), "hong").start_fresh()
    assert res["ok"] is False
    # Phải dừng VÌ không dời được tệp, không phải vì init_db vấp tệp hỏng.
    assert "tep dang bi khoa" in res["errors"][0]["params"]["detail"]
    assert db.read_bytes() == b"hong hoan toan"


# ------------------------------------------------------------------ #
# B10 — bản sao lưu dở dang
# ------------------------------------------------------------------ #


def test_sao_luu_hong_khong_de_lai_tep_do_dang(api, monkeypatch):
    import api as api_mod

    class _Hong:
        def __init__(self, conn):
            self._c = conn

        def backup(self, dst):
            dst.execute("CREATE TABLE x(a)")
            dst.commit()
            raise OSError("dia day")

        def close(self):
            self._c.close()

    that = api_mod.connect_db
    monkeypatch.setattr(api_mod, "connect_db", lambda p: _Hong(that(p)))
    with pytest.raises(OSError):
        api._backup_db()
    thu_muc = os.path.dirname(api.db_path)
    assert not [f for f in os.listdir(thu_muc) if ".bak-" in f]


# ------------------------------------------------------------------ #
# B11 — tên tệp theo CLB
# ------------------------------------------------------------------ #


def test_ten_tep_theo_clb_khong_de_nhau_khi_chi_khac_hoa_thuong(api, tmp_path):
    api.create_or_update_club("clb_a", "CLB a thường", 5, 0, "")
    api.create_or_update_club("CLB_A", "CLB A hoa", 5, 0, "")
    api.create_or_update_club("CON", "CLB tên cấm", 5, 0, "")
    api.import_preferences_csv(
        "student_id,name,pref_1\nhs1,An,clb_a\nhs2,Binh,CLB_A\nhs3,Chi,CON\n")
    api.run_pipeline(seed=1)
    d = api.export_csv(str(tmp_path / "kq.csv"))["data"]
    thu_muc = str(tmp_path / "kq_theo_club")
    ten = sorted(os.listdir(thu_muc))
    thuong = [t.casefold() for t in ten]
    assert len(thuong) == len(set(thuong)), ten
    assert "CON.csv" not in ten and "_CON.csv" in ten
    assert d["path"]


# ------------------------------------------------------------------ #
# B12 — CLB lạ phải báo "CLB lạ", không báo "quá nhiều"
# ------------------------------------------------------------------ #


def test_clb_la_bao_dung_loi(api):
    api.create_student_if_missing("hs1", "An")
    res = api.submit_preferences("hs1", ["x%d" % i for i in range(12)])
    assert res["errors"][0]["code"] == "unknown_clubs"
