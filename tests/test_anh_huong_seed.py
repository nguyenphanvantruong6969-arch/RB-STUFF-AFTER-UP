"""Seed đổi thì kết quả đổi tới đâu — và tới đâu thì KHÔNG được đổi.

Khoá xếp hạng của mỗi CLB là `(-điểm, số_bốc_thăm)`
(`rbda_priority_pipeline.club_priority_order`). Điểm đứng TRƯỚC, nên seed
chỉ chen vào được đúng hai chỗ:

  * hai em HOÀ ĐIỂM ở cùng một CLB
  * em dự tuyển CLB mà mình KHÔNG THI (tier 2, xếp thuần theo bốc thăm)

File này canh mệnh đề ngược lại, cái quan trọng hơn: **chỗ nào điểm đã
quyết định thì seed không được đụng vào**. Nếu một ngày nào đó ai đó đổi
khoá xếp hạng thành `(số_bốc_thăm, -điểm)` — hoặc lỡ tay bỏ dấu trừ — thì
điểm thi mất tác dụng, và đó là loại lỗi phá hỏng toàn bộ ý nghĩa của
chương trình mà nhìn kết quả thì không thấy ngay.

Số đo thực tế trên ba bộ dữ liệu: `du_lieu_test/do_anh_huong_seed.py`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbda_priority_pipeline as loi  # noqa: E402


def _chay(api, seed):
    """Chạy RB-DA với một seed, KHÔNG ghi gì vào CSDL (nên không đụng
    stb_lock, và seed sau không thấy dấu vết seed trước)."""
    students, clubs, diem, ung_vien, nv, _ = loi.load_from_sqlite(api.db_path)
    stb = loi.generate_stb_lottery(sorted(students), seed)
    du_tru_fn = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda(students, clubs, diem, ung_vien, nv, stb, du_tru_fn)
    cap = loi.verify_stability(kq, clubs, nv, du_tru_fn)
    return dict(kq.assignment), cap


def _dung_du_lieu(api, diem_theo_em, suc_chua=2):
    """Một CLB, `suc_chua` suất, mọi em cùng nguyện vọng duy nhất là nó."""
    api.create_or_update_club("clb_a", "CLB A", suc_chua, 0, "")
    for sid, d in diem_theo_em.items():
        api.create_student_if_missing(sid, "Học sinh " + sid)
        api.submit_test_selection(sid, ["clb_a"])
        api.submit_preferences(sid, ["clb_a"])
        api.submit_club_scores("clb_a", [{"student_id": sid, "score": d}])


# --------------------------------------------------------------------------
# 1. Cùng seed -> cùng kết quả. (Tái lập: khác với test_stb_khong_phu_thuoc
#    _thu_tu.py, ở đó canh thứ tự NHẬP; ở đây canh chính con số seed.)
# --------------------------------------------------------------------------

def test_cung_seed_chay_hai_lan_ra_giong_het(api):
    _dung_du_lieu(api, {"HS01": 9.0, "HS02": 8.0, "HS03": 7.0})
    assert _chay(api, 42)[0] == _chay(api, 42)[0]


def test_seed_khac_nhau_thi_bo_boc_tham_khac_nhau(api):
    """Canh chính cái máy bốc thăm: nếu đổi seed mà bộ số y nguyên thì mọi
    test dưới đây xanh một cách vô nghĩa."""
    ds = ["HS%02d" % i for i in range(1, 21)]
    assert loi.generate_stb_lottery(ds, 1) != loi.generate_stb_lottery(ds, 2)
    assert loi.generate_stb_lottery(ds, 7) == loi.generate_stb_lottery(ds, 7)


# --------------------------------------------------------------------------
# 2. MỆNH ĐỀ THEN CHỐT — điểm khác nhau thì seed vô can.
# --------------------------------------------------------------------------

def test_diem_khac_nhau_thi_doi_seed_khong_doi_mot_em_nao(api):
    """Ba em, ba điểm khác nhau, hai suất. Hai em điểm cao PHẢI vào, em
    điểm thấp nhất PHẢI trượt — với MỌI seed. Không có chỗ nào cho may rủi."""
    _dung_du_lieu(api, {"HS01": 9.0, "HS02": 8.0, "HS03": 7.0}, suc_chua=2)

    for seed in range(1, 101):
        xep, cap = _chay(api, seed)
        assert cap == [], "seed %d cho kết quả không ổn định" % seed
        assert xep["HS01"] == "clb_a", "seed %d đẩy em điểm cao nhất ra" % seed
        assert xep["HS02"] == "clb_a", "seed %d đẩy em điểm nhì ra" % seed
        assert xep["HS03"] is None, (
            "seed %d cho em điểm thấp nhất vào — điểm thi mất tác dụng" % seed)


def test_hoa_diem_thi_seed_moi_duoc_quyet_dinh(api):
    """Ngược lại: hai em HOÀ điểm tranh một suất. Chạy 100 seed thì phải
    thấy CẢ HAI em đều từng vào — nếu chỉ một em luôn thắng thì bốc thăm
    đang thiên vị, và đó cũng là lỗi."""
    _dung_du_lieu(api, {"HS01": 8.0, "HS02": 8.0}, suc_chua=1)

    nguoi_thang = set()
    for seed in range(1, 101):
        xep, cap = _chay(api, seed)
        assert cap == []
        nguoi_thang.add("HS01" if xep["HS01"] else "HS02")
    assert nguoi_thang == {"HS01", "HS02"}, (
        "Chỉ %s thắng trong 100 seed — bốc thăm thiên vị." % nguoi_thang)


# --------------------------------------------------------------------------
# 3. Mọi seed đều cho kết quả ỔN ĐỊNH. Đây là bảo đảm của họ Gale–Shapley:
#    seed đổi AI được suất, chứ không bao giờ đổi TÍNH ĐÚNG của kết quả.
# --------------------------------------------------------------------------

def test_moi_seed_deu_cho_ket_qua_on_dinh(api):
    api.create_or_update_club("clb_a", "CLB A", 2, 0, "")
    api.create_or_update_club("clb_b", "CLB B", 2, 0, "")
    for i in range(1, 9):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Học sinh " + sid)
        api.submit_test_selection(sid, ["clb_a", "clb_b"])
        api.submit_preferences(sid, ["clb_a", "clb_b"] if i % 2 else ["clb_b", "clb_a"])
        # Cố ý CHIA ĐÔI thành hai mức điểm -> có hoà, tức có chỗ cho seed.
        api.submit_club_scores("clb_a", [{"student_id": sid, "score": 8.0 if i <= 4 else 7.0}])
        api.submit_club_scores("clb_b", [{"student_id": sid, "score": 7.0 if i <= 4 else 8.0}])

    for seed in range(1, 51):
        _, cap = _chay(api, seed)
        assert cap == [], "seed %d: %d cặp phá vỡ" % (seed, len(cap))
