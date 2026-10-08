"""Các sửa hiệu năng (rà soát 26/09) — khoá HÀNH VI, không đo thời gian.

Đo thời gian thì chập chờn theo máy. Ở đây khoá điều kiện làm nên tốc độ:
chỉ mục có mặt, truy vấn báo cáo chạy đúng một lần mỗi lần xuất, và bước
bỏ qua CLB đứng yên trong vòng DA không đổi kết quả.
"""

import random
import sqlite3

import rbda_priority_pipeline as rp
from api import PipelineAPI
from api_chung import _nho_trong_luc_xuat


def test_chi_muc_theo_club_id_co_mat(api):
    with sqlite3.connect(api.db_path) as c:
        ten = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    for can in ("idx_club_test_selection_club", "idx_club_scores_club",
                "idx_preferences_club", "idx_match_results_club"):
        assert can in ten


def test_truy_van_loc_theo_club_dung_chi_muc(api):
    with sqlite3.connect(api.db_path) as c:
        ke_hoach = " ".join(r[-1] for r in c.execute(
            "EXPLAIN QUERY PLAN SELECT student_id FROM preferences WHERE club_id = 'x'"))
    assert "idx_preferences_club" in ke_hoach


def test_moi_lan_xuat_chi_tinh_thong_ke_lap_day_mot_lan(api, tmp_path, monkeypatch):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.import_preferences_csv("student_id,name,pref_1\nhs1,An,A\n")
    api.run_pipeline(seed=1)

    dem = {"n": 0}
    goc = PipelineAPI.get_club_fill_stats.__wrapped__

    def dem_goi(self, *a):
        dem["n"] += 1
        return goc(self, *a)

    monkeypatch.setattr(PipelineAPI, "get_club_fill_stats", _nho_trong_luc_xuat(dem_goi))
    assert api.export_csv(str(tmp_path / "kq.csv"))["ok"]
    assert dem["n"] == 1
    # Ngoài lúc xuất thì không nhớ gì — màn hình luôn thấy dữ liệu mới.
    api.get_club_fill_stats()
    api.get_club_fill_stats()
    assert dem["n"] == 3


def test_bo_qua_clb_dung_yen_khong_doi_ket_qua():
    """So với cách tính lại MỌI CLB mỗi vòng, trên 200 bộ dữ liệu ngẫu nhiên."""

    def run_tinh_lai_het(students, clubs, sc, app, prefs, stb, el):
        # Bản tham chiếu: vòng DA như cũ, gọi hàm lựa chọn cho mọi CLB.
        base_rank = {c: {s: i for i, s in enumerate(rp.compute_club_priority(
            c, app.get(c, []), sc.get(c, {}), stb))} for c in clubs}
        held = {c: [] for c in clubs}
        tier = {c: {} for c in clubs}
        idx = {s: 0 for s in students}
        cho = [s for s in students if prefs.get(s)]
        while cho:
            de = {c: [] for c in clubs}
            con = []
            for s in cho:
                if idx[s] >= len(prefs[s]):
                    continue
                de[prefs[s][idx[s]]].append(s)
            for c, moi in de.items():
                pool = held[c] + moi
                nhan, tier[c] = rp.club_choice_function(
                    pool, clubs[c]["capacity"], clubs[c]["reserve_capacity"],
                    lambda s, _c=c: el(s, _c), base_rank[c])
                held[c] = nhan
                for s in pool:
                    if s not in nhan:
                        idx[s] += 1
                        con.append(s)
            cho = [s for s in con if idx[s] < len(prefs[s])]
        return ({s: c for c, ds in held.items() for s in ds},
                {s: tier[c][s] for c, ds in held.items() for s in ds})

    for seed in range(200):
        r = random.Random(seed)
        ns, nc = r.randint(3, 40), r.randint(2, 6)
        clubs = {}
        for i in range(nc):
            cap = r.randint(1, 6)
            clubs[f"c{i}"] = {"capacity": cap, "reserve_capacity": r.randint(0, cap)}
        nhom = {s: r.choice([True, False]) for s in (f"s{i}" for i in range(ns))}
        students = {s: {} for s in nhom}
        prefs = {s: r.sample(list(clubs), r.randint(0, nc)) for s in students}
        app = {c: [s for s in students if c in prefs[s]] for c in clubs}
        sc = {c: {s: float(r.randint(0, 10)) for s in app[c] if r.random() < 0.5} for c in clubs}
        stb = rp.generate_stb_lottery(list(students), seed)
        el = lambda s, c: nhom[s]  # noqa: E731

        kq = rp.run_rbda(students, clubs, sc, app, prefs, stb, el)
        gan, tang = run_tinh_lai_het(students, clubs, sc, app, prefs, stb, el)
        assert {s: c for s, c in kq.assignment.items() if c} == gan, seed
        assert kq.matched_tier == tang, seed
