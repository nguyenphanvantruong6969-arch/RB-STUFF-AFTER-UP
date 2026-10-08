"""Học sinh thêm vào SAU khi khoá bốc thăm phải được chèn NGẪU NHIÊN.

Bản đầu cấp cho em mới số `MAX(stb)+1` với lý do ghi trong mã là "tránh
trùng số". Vì số nhỏ = ưu tiên cao (`compute_club_priority`), cách đó đặt
em mới đứng sau MỌI em cũ, ở MỌI câu lạc bộ, vĩnh viễn — với nhóm đó bốc
thăm không còn tồn tại.

Đo được trước khi sửa: 20 em cũ + 10 em mới tranh 10 suất (đều Tầng 2,
thuần bốc thăm) -> **em mới được 0 suất**, công bằng thì kỳ vọng ~3,3.

Tệp này canh cả hai vế, và vế thứ hai mới là vế dễ mất:

  1. Em mới THẬT SỰ có cơ hội — không còn bị đẩy xuống cuối.
  2. Em cũ KHÔNG bị xáo trộn — thứ tự tương đối giữ nguyên tuyệt đối.
     Đó mới là lời hứa thật của việc khoá bộ số. ("Số tuyệt đối không
     đổi" chưa bao giờ là lời hứa có ý nghĩa, vì số tuyệt đối không hiện
     ở đâu cho ai thấy.)
"""

import os
import sqlite3
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rbda_priority_pipeline import chen_stb_cho_hoc_sinh_moi  # noqa: E402

CU = ["HS%02d" % i for i in range(1, 11)]      # đã sắp theo số bốc thăm
MOI = ["HS%02d" % i for i in range(90, 95)]


# --------------------------------------------------------------------------
# 1. Hai tính chất bảo đảm
# --------------------------------------------------------------------------

def test_thu_tu_tuong_doi_cua_em_cu_khong_bao_gio_doi():
    """Lời hứa thật của việc khoá bộ số. Mất cái này là mất tính minh bạch."""
    for seed in range(1, 51):
        ra = chen_stb_cho_hoc_sinh_moi(CU, MOI, seed)
        assert sorted(CU, key=ra.get) == CU, (
            "seed %d làm đảo thứ tự em cũ" % seed)


def test_ket_qua_luon_la_hoan_vi_lien_tuc():
    """Giống generate_stb_lottery: không trùng số, không hụt số."""
    for seed in range(1, 21):
        ra = chen_stb_cho_hoc_sinh_moi(CU, MOI, seed)
        assert set(ra) == set(CU) | set(MOI)
        assert sorted(ra.values()) == list(range(len(CU) + len(MOI)))


def test_em_moi_KHONG_bi_don_het_xuong_cuoi():
    """MỆNH ĐỀ TRUNG TÂM — test này đỏ nếu ai trả lại cách MAX+1.

    Cách cũ luôn cho em mới toàn bộ các số cuối. Chèn ngẫu nhiên thì qua
    nhiều seed phải có lúc em mới đứng trên em cũ.
    """
    day_xuong_cuoi = 0
    for seed in range(1, 51):
        ra = chen_stb_cho_hoc_sinh_moi(CU, MOI, seed)
        if min(ra[m] for m in MOI) > max(ra[c] for c in CU):
            day_xuong_cuoi += 1
    assert day_xuong_cuoi < 5, (
        "%d/50 seed dồn hết em mới xuống cuối — trông như cách MAX+1 cũ"
        % day_xuong_cuoi)


def test_em_moi_tung_dung_o_ca_dau_va_cuoi_dan_so():
    """Phân bố đều thì qua nhiều seed phải có lúc em mới bốc được số 0."""
    tung_dan_dau = any(
        min(chen_stb_cho_hoc_sinh_moi(CU, MOI, s)[m] for m in MOI) == 0
        for s in range(1, 51))
    assert tung_dan_dau, "không seed nào cho em mới đứng đầu — chưa phải ngẫu nhiên"


# --------------------------------------------------------------------------
# 2. Tái lập và không phụ thuộc thứ tự nhập
# --------------------------------------------------------------------------

def test_cung_seed_thi_ra_dung_bo_so_cu():
    assert chen_stb_cho_hoc_sinh_moi(CU, MOI, 42) == chen_stb_cho_hoc_sinh_moi(CU, MOI, 42)


def test_doi_seed_thi_bo_so_doi():
    assert chen_stb_cho_hoc_sinh_moi(CU, MOI, 1) != chen_stb_cho_hoc_sinh_moi(CU, MOI, 2)


def test_thu_tu_nhap_cua_nhom_em_moi_khong_anh_huong():
    """Cùng hạng lỗi với lỗi 19: `missing` đến từ thứ tự CHÈN trong CSDL.
    Không sắp trước khi xáo thì thứ tự nhập lén quyết định ai được số tốt."""
    assert (chen_stb_cho_hoc_sinh_moi(CU, MOI, 42)
            == chen_stb_cho_hoc_sinh_moi(CU, list(reversed(MOI)), 42))


def test_khong_co_em_moi_thi_giu_nguyen_thu_tu_cu():
    ra = chen_stb_cho_hoc_sinh_moi(CU, [], 42)
    assert ra == {sid: i for i, sid in enumerate(CU)}


# --------------------------------------------------------------------------
# 3. Đi qua đường thật của phần mềm
# --------------------------------------------------------------------------

def _dung_hai_dot(api, seed, n_cu=20, n_moi=10, suc_chua=10):
    """Đợt 1 chạy rồi khoá; đợt 2 thêm sau. Mọi em đều Tầng 2 (không thi)
    nên thứ tự HOÀN TOÀN do bốc thăm — chỗ duy nhất đo được công bằng."""
    api.create_or_update_club("clb_a", "CLB A", suc_chua, 0, "")
    for i in range(1, n_cu + 1):
        sid = "HS%03d" % i
        api.create_student_if_missing(sid, "Em " + sid)
        api.submit_preferences(sid, ["clb_a"])
    api.run_pipeline(seed=seed)
    truoc = dict(sqlite3.connect(api.db_path).execute(
        "SELECT student_id, stb_number FROM students"))

    for i in range(101, 101 + n_moi):
        sid = "HS%03d" % i
        api.create_student_if_missing(sid, "Em " + sid)
        api.submit_preferences(sid, ["clb_a"])
    api.run_pipeline(seed=seed)

    conn = sqlite3.connect(api.db_path)
    sau = dict(conn.execute("SELECT student_id, stb_number FROM students"))
    co_suat = [r[0] for r in conn.execute(
        "SELECT student_id FROM match_results "
        "WHERE club_id IS NOT NULL AND club_id != ''")]
    conn.close()
    return truoc, sau, co_suat


def test_em_vao_sau_gianh_duoc_suat_qua_duong_that(api):
    """Trước khi sửa: 0 suất ở MỌI seed. Test này là lưới chắn chống hồi quy."""
    _truoc, _sau, co_suat = _dung_hai_dot(api, seed=7)
    n_moi = sum(1 for s in co_suat if int(s[2:]) >= 100)
    assert n_moi > 0, (
        "em vào sau không giành được suất nào — cách MAX+1 cũ đã quay lại")


def test_trung_binh_nhieu_seed_gan_voi_ti_le_cong_bang(api_factory):
    """10 em mới trên 30 em tranh 10 suất -> công bằng thì ~3,3 suất."""
    dem = []
    for seed in range(1, 11):
        _, _, co_suat = _dung_hai_dot(api_factory(), seed=seed)
        dem.append(sum(1 for s in co_suat if int(s[2:]) >= 100))
    tb = statistics.mean(dem)
    assert 1.5 <= tb <= 5.5, "trung bình %.1f suất — lệch xa mức công bằng ~3,3" % tb


def test_thu_tu_tuong_doi_em_cu_giu_nguyen_qua_duong_that(api):
    truoc, sau, _ = _dung_hai_dot(api, seed=7)
    assert sorted(truoc, key=truoc.get) == sorted(truoc, key=lambda k: sau[k])


def test_chay_lai_ma_KHONG_co_em_moi_thi_khong_doi_so_cua_ai(api):
    """Ràng buộc bắt buộc: chèn chỉ được xảy ra khi thật sự có em mới."""
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    for i in range(1, 9):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Em " + sid)
        api.submit_preferences(sid, ["clb_a"])
    api.run_pipeline(seed=42)
    truoc = dict(sqlite3.connect(api.db_path).execute(
        "SELECT student_id, stb_number FROM students"))
    api.run_pipeline(seed=42)
    sau = dict(sqlite3.connect(api.db_path).execute(
        "SELECT student_id, stb_number FROM students"))
    assert truoc == sau


def _buoc_bo_tham(res):
    """Danh sách steps có cả dòng 'running' lẫn 'done' cho cùng một bước —
    chỉ dòng 'done' mới mang detail."""
    return [s for s in res["data"]["steps"]
            if s["step"] == "stb_lottery" and s["status"] == "done"][0]


def test_thong_bao_noi_dung_khop_voi_viec_that_su_lam(api):
    """Câu thông báo phải nói đúng việc: CHÈN, không phải 'vẽ bổ sung nối
    đuôi'. Và không có em mới thì phải báo TÁI SỬ DỤNG, không phải chèn 0 em."""
    api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
    for i in range(1, 5):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, "Em " + sid)
        api.submit_preferences(sid, ["clb_a"])
    api.run_pipeline(seed=42)

    res = api.run_pipeline(seed=42)          # không thêm ai
    chi_tiet = _buoc_bo_tham(res)
    assert chi_tiet["detail"]["code"] == "stb_reused"

    api.create_student_if_missing("HS90", "Em moi")
    api.submit_preferences("HS90", ["clb_a"])
    res = api.run_pipeline(seed=42)
    chi_tiet = _buoc_bo_tham(res)
    assert chi_tiet["detail"]["code"] == "stb_supplemented"
    assert chi_tiet["detail"]["params"]["n"] == 1
