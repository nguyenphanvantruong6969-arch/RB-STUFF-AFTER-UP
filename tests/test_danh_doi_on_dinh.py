"""Canh bộ đo `du_lieu_test/do_danh_doi_on_dinh.py`.

Bộ đo đó trả lời một câu học sinh sẽ bị hỏi trước hội đồng: kết quả ổn
định rồi, nhưng có TỐT NHẤT cho học sinh không? Câu trả lời đo được là
KHÔNG — vẫn còn **cặp đôi cùng có lợi** (hai em đổi chỗ thì cả hai cùng
lên nguyện vọng cao hơn).

Hai loại test ở đây, và loại thứ hai mới là loại khó bỏ qua:

  1. Từng hàm nhỏ, ví dụ dựng tay, kiểm được bằng bút chì.
  2. Con số CHÍNH XÁC mà `docs/CO_CHE_THUAT_TOAN.md` và `BAN_GIAO.md` đang
     trích. Đổi thuật toán mà quên sửa tài liệu thì test này đỏ TRƯỚC
     khi giám khảo đọc phải con số sai.

CHÚ Ý VỀ TÊN GỌI — đừng gộp hai khái niệm:
  * **cặp phá vỡ** (blocking pair): học sinh + CLB, CLB *muốn nhận* em
    đó. Có cặp phá vỡ = kết quả KHÔNG ổn định = LỖI.
  * **cặp đôi cùng có lợi**: hai HỌC SINH đổi chỗ cho nhau. Có cặp như
    vậy = kết quả không tối ưu Pareto = ĐÁNH ĐỔI đã biết, KHÔNG phải lỗi.
"""

import importlib.util
import os
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BO_DO = os.path.join(GOC, "du_lieu_test", "do_danh_doi_on_dinh.py")

sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))


@pytest.fixture(scope="module")
def bo_do():
    spec = importlib.util.spec_from_file_location("do_danh_doi_on_dinh", BO_DO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _du_lieu(nguyen_vong, diem=None):
    """Dựng đúng hình dạng tuple mà `load_from_sqlite` trả về.

    Chỉ ba ô được dùng tới: students (để duyệt), diem, nguyen_vong.
    """
    students = {sid: {"stb": 0.0, "reserve_group": ""} for sid in nguyen_vong}
    return (students, {}, diem or {}, {}, nguyen_vong, {})


# --------------------------------------------------------------------------
# 1. thich_hon — nền của mọi thứ phía sau
# --------------------------------------------------------------------------

def test_thich_hon_doc_dung_thu_tu_nguyen_vong(bo_do):
    thu_hang = {"HS01": {"clb_a": 0, "clb_b": 1}}
    assert bo_do.thich_hon(thu_hang, "HS01", "clb_a", "clb_b") is True
    assert bo_do.thich_hon(thu_hang, "HS01", "clb_b", "clb_a") is False


def test_thich_hon_clb_ngoai_nguyen_vong_thi_khong_bao_gio_hon(bo_do):
    """Em không đăng ký CLB đó thì không thể 'muốn sang' CLB đó."""
    thu_hang = {"HS01": {"clb_a": 0}}
    assert bo_do.thich_hon(thu_hang, "HS01", "clb_la", "clb_a") is False


def test_thich_hon_chua_co_suat_thi_bat_ky_nguyen_vong_nao_cung_hon(bo_do):
    """Chỗ hiện tại là None (chưa có suất) -> mọi CLB trong nguyện vọng
    đều hơn. Nếu chỗ này sai thì em chưa có suất bị bỏ sót khỏi phép đếm."""
    thu_hang = {"HS01": {"clb_a": 3}}
    assert bo_do.thich_hon(thu_hang, "HS01", "clb_a", None) is True


# --------------------------------------------------------------------------
# 2. hoa_nhau_o — hàm quyết định việc quy nguyên nhân
# --------------------------------------------------------------------------

def test_hoa_khi_ca_hai_cung_khong_thi(bo_do):
    """Cả hai đều Tầng 2 -> xếp thuần bốc thăm -> hoà, bốc thăm có quyền."""
    assert bo_do.hoa_nhau_o({"clb_a": {}}, "clb_a", "HS01", "HS02") is True


def test_hoa_khi_cung_thi_va_bang_diem(bo_do):
    diem = {"clb_a": {"HS01": 8.0, "HS02": 8.0}}
    assert bo_do.hoa_nhau_o(diem, "clb_a", "HS01", "HS02") is True


def test_khong_hoa_khi_khac_diem(bo_do):
    diem = {"clb_a": {"HS01": 9.0, "HS02": 7.0}}
    assert bo_do.hoa_nhau_o(diem, "clb_a", "HS01", "HS02") is False


def test_khong_hoa_khi_mot_em_thi_mot_em_khong(bo_do):
    """Tầng 1 luôn đứng TRỌN trước Tầng 2 — không bao giờ hoà nhau."""
    diem = {"clb_a": {"HS01": 5.0}}
    assert bo_do.hoa_nhau_o(diem, "clb_a", "HS01", "HS02") is False
    assert bo_do.hoa_nhau_o(diem, "clb_a", "HS02", "HS01") is False


# --------------------------------------------------------------------------
# 3. tim_cap_cung_co_loi — ví dụ nhỏ, biết trước đáp án
# --------------------------------------------------------------------------

def test_hai_em_muon_doi_cho_nhau_thi_dem_duoc_dung_mot_cap(bo_do):
    """HS01 ở A nhưng thích B; HS02 ở B nhưng thích A. Đổi thì cả hai lên."""
    du_lieu = _du_lieu({
        "HS01": ["clb_b", "clb_a"],
        "HS02": ["clb_a", "clb_b"],
    })
    xep = {"HS01": "clb_a", "HS02": "clb_b"}
    assert bo_do.tim_cap_cung_co_loi(du_lieu, xep) == [
        ("HS01", "clb_a", "HS02", "clb_b")
    ]


def test_mot_ben_muon_doi_thi_KHONG_tinh(bo_do):
    """Đây là chỗ dễ viết sai nhất: chỉ một em có lợi thì đổi chỗ làm em
    kia thiệt. `and` chứ không phải `or`."""
    du_lieu = _du_lieu({
        "HS01": ["clb_b", "clb_a"],
        "HS02": ["clb_b", "clb_a"],   # HS02 đang ở B, đúng nguyện vọng 1
    })
    xep = {"HS01": "clb_a", "HS02": "clb_b"}
    assert bo_do.tim_cap_cung_co_loi(du_lieu, xep) == []


def test_hai_em_cung_mot_clb_thi_khong_co_gi_de_doi(bo_do):
    du_lieu = _du_lieu({
        "HS01": ["clb_b", "clb_a"],
        "HS02": ["clb_b", "clb_a"],
    })
    xep = {"HS01": "clb_a", "HS02": "clb_a"}
    assert bo_do.tim_cap_cung_co_loi(du_lieu, xep) == []


def test_em_chua_co_suat_khong_bi_dem_thanh_mot_ve_cua_cap(bo_do):
    """Không có suất thì không có gì để đem đổi."""
    du_lieu = _du_lieu({
        "HS01": ["clb_b", "clb_a"],
        "HS02": ["clb_a", "clb_b"],
    })
    xep = {"HS01": "clb_a", "HS02": None}
    assert bo_do.tim_cap_cung_co_loi(du_lieu, xep) == []


# --------------------------------------------------------------------------
# 4. quy_nguyen_nhan — hai kịch bản đối nhau
# --------------------------------------------------------------------------

def _canh_mot_cap(bo_do, diem):
    """Đúng một cặp đôi cùng có lợi, dựng sẵn — để chỉ còn ĐIỂM là biến."""
    du_lieu = _du_lieu({
        "HS01": ["clb_b", "clb_a"],
        "HS02": ["clb_a", "clb_b"],
    }, diem)
    xep = {"HS01": "clb_a", "HS02": "clb_b"}
    cap = [("HS01", "clb_a", "HS02", "clb_b")]
    assert bo_do.tim_cap_cung_co_loi(du_lieu, xep) == cap
    return du_lieu, xep, cap


def test_thua_vi_HOA_thi_tinh_la_boc_tham_co_phan(bo_do):
    """HS01 muốn sang B; ở B đang có HS02 BẰNG ĐIỂM với mình. Một lần bốc
    thăm khác đã có thể đổi ngôi hai em -> bốc thăm có phần."""
    diem = {"clb_b": {"HS01": 8.0, "HS02": 8.0}}
    du_lieu, xep, cap = _canh_mot_cap(bo_do, diem)
    assert bo_do.quy_nguyen_nhan(du_lieu, xep, cap) == 1


def test_thua_vi_DIEM_thi_boc_tham_vo_can(bo_do):
    """Cùng thế nhưng HS01 kém HS02 hẳn 4 điểm ở B. Bốc thăm không chen
    vào được — có bốc lại nghìn lần HS01 vẫn đứng dưới."""
    diem = {"clb_b": {"HS01": 5.0, "HS02": 9.0}}
    du_lieu, xep, cap = _canh_mot_cap(bo_do, diem)
    assert bo_do.quy_nguyen_nhan(du_lieu, xep, cap) == 0


def test_ca_hai_deu_khong_thi_thi_boc_tham_co_phan(bo_do):
    """Tầng 2 hoàn toàn: không ai có điểm ở B, thứ tự thuần bốc thăm."""
    du_lieu, xep, cap = _canh_mot_cap(bo_do, {})
    assert bo_do.quy_nguyen_nhan(du_lieu, xep, cap) == 1


# --------------------------------------------------------------------------
# 5. CON SỐ TÀI LIỆU ĐANG TRÍCH — phần quan trọng nhất tệp này
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def bo_sach(bo_do, tmp_path_factory):
    """Nạp bộ sạch MỘT lần cho cả tệp — nạp CSV là phần chậm nhất."""
    import rbda_priority_pipeline as loi
    thu_muc = str(tmp_path_factory.mktemp("bo_sach"))
    ten, files = bo_do.BO_DU_LIEU[1]
    assert ten.startswith("bo_sach"), "thứ tự BO_DU_LIEU đã đổi"
    return loi.load_from_sqlite(bo_do.nap_bo(thu_muc, files))


def test_bo_sach_seed_moc_dung_con_so_tai_lieu(bo_do, bo_sach):
    """85 cặp / 34 em / 18 cặp bốc thăm có phần, ở seed 42.

    Đổi con số này thì docs/CO_CHE_THUAT_TOAN.md, BAN_GIAO.md mục 5 và
    SO_LIEU_DA_KIEM_CHUNG.md mục 3d đang nói sai — sửa cả ba.
    """
    xep, cap_pha_vo = bo_do.xep_theo_seed(bo_sach, bo_do.SEED_MOC)
    cap_doi = bo_do.tim_cap_cung_co_loi(bo_sach, xep)
    em_dinh = {s for c in cap_doi for s in (c[0], c[2])}

    assert cap_pha_vo == [], "kết quả phải ỔN ĐỊNH — đây mới là lỗi thật"
    assert len(cap_doi) == 85, "tài liệu đang ghi 85 cặp đôi cùng có lợi"
    assert len(em_dinh) == 34, "tài liệu đang ghi 34 em dính ít nhất một cặp"
    assert bo_do.quy_nguyen_nhan(bo_sach, xep, cap_doi) == 18, (
        "tài liệu đang ghi 18/85 cặp là bốc thăm CÓ phần")


def test_vi_du_huong_dan_khong_co_cap_nao(bo_do, tmp_path):
    """Bộ đối chứng. Bộ 10 em không có em hoà điểm, không có em Tầng 2 ->
    0 cặp. Nếu bộ này bỗng ra khác 0 thì hiện tượng đến từ chỗ khác chứ
    không phải chỗ tài liệu đang giải thích."""
    import rbda_priority_pipeline as loi
    ten, files = bo_do.BO_DU_LIEU[0]
    assert ten.startswith("vi_du_huong_dan")
    du_lieu = loi.load_from_sqlite(bo_do.nap_bo(str(tmp_path), files))
    xep, cap_pha_vo = bo_do.xep_theo_seed(du_lieu, bo_do.SEED_MOC)
    assert cap_pha_vo == []
    assert bo_do.tim_cap_cung_co_loi(du_lieu, xep) == []


def test_khong_seed_nao_lam_hien_tuong_bien_mat(bo_do, bo_sach):
    """MỆNH ĐỀ CHỐNG QUY SAI NGUYÊN NHÂN.

    Nếu bốc thăm là nguyên nhân chính thì phải tồn tại seed cho 0 cặp.
    Tài liệu khẳng định 0/40 seed cho 0 cặp; ở đây kiểm 5 seed cho nhanh —
    chỉ cần MỘT seed cho 0 cặp là khẳng định đó sai và test phải đỏ.
    """
    for seed in range(1, 6):
        xep, cap_pha_vo = bo_do.xep_theo_seed(bo_sach, seed)
        assert cap_pha_vo == [], "seed %d làm kết quả mất ổn định" % seed
        so_cap = len(bo_do.tim_cap_cung_co_loi(bo_sach, xep))
        assert so_cap > 0, (
            "seed %d cho 0 cặp — tài liệu đang viết KHÔNG seed nào cho 0" % seed)


# --------------------------------------------------------------------------
# 6. Vệ sinh
# --------------------------------------------------------------------------

def test_bo_do_khong_dung_toi_du_lieu_that():
    """Bộ đo chỉ được chạy trong thư mục tạm. Nó KHÔNG được mở app.db của
    học sinh — dữ liệu thật không bao giờ đi vào một bài đo."""
    src = open(BO_DO, encoding="utf-8").read()
    assert '"app.db"' not in src and "'app.db'" not in src, (
        "bộ đo không được nhắc tên tệp CSDL nào — đường dẫn chỉ đến từ nap_bo")
    assert "loi.load_from_sqlite(nap_bo(" in src, (
        "CSDL duy nhất bộ đo mở phải là CSDL tạm do nap_bo dựng")
    assert "tempfile.mkdtemp" in src
    assert "shutil.rmtree" in src


def test_bo_do_khong_goi_cap_doi_la_cap_pha_vo():
    """Ràng buộc câu chữ, không phải ràng buộc mã. Gọi lẫn hai khái niệm
    là sai về mặt thuật ngữ và giám khảo bắt được ngay."""
    src = open(BO_DO, encoding="utf-8").read()
    assert "CẶP ĐÔI CÙNG CÓ LỢI" in src
    assert "blocking pair" in src, "phải còn chỗ phân biệt hai khái niệm"


# --------------------------------------------------------------------------
# 7. Thí nghiệm đối chứng — phần bác thẳng cách đọc "tại bốc thăm"
# --------------------------------------------------------------------------

def test_bo_bot_diem_hai_dau_dung_nhu_ten_goi(bo_do):
    diem = {"clb_a": {"HS01": 8.0, "HS02": 7.0}, "clb_b": {"HS01": 9.0}}
    assert bo_do.bo_bot_diem(diem, 0.0) == diem, "bỏ 0% phải giữ nguyên"
    assert bo_do.bo_bot_diem(diem, 1.0) == {"clb_a": {}, "clb_b": {}}, (
        "bỏ 100% phải đẩy MỌI em xuống Tầng 2")


def test_bo_bot_diem_chay_lai_ra_dung_bo_cu(bo_do):
    """Hạt cố định — nếu không, con số trong tài liệu không chạy lại được."""
    diem = {"clb_a": {"HS%02d" % i: 5.0 + i for i in range(30)}}
    assert bo_do.bo_bot_diem(diem, 0.5) == bo_do.bo_bot_diem(diem, 0.5)


def test_bo_bot_diem_khong_sua_bo_goc(bo_do):
    goc = {"clb_a": {"HS01": 8.0, "HS02": 7.0}}
    bo_do.bo_bot_diem(goc, 1.0)
    assert goc == {"clb_a": {"HS01": 8.0, "HS02": 7.0}}


def test_bo_hết_diem_thi_KHONG_nhieu_cap_hon_ma_it_hon(bo_do, bo_sach):
    """MỆNH ĐỀ TRUNG TÂM của cả bộ đo.

    Bỏ hết điểm = mọi em xuống Tầng 2 = BỐC THĂM quyết định hoàn toàn.
    Nếu bốc thăm là thứ sinh ra tổn thất thì lúc đó số cặp phải NHIỀU
    NHẤT. Đo được là ít nhất — 90,2 xuống 4,1 trên bộ sạch.

    Đây là con số docs/CO_CHE_THUAT_TOAN.md và BAN_GIAO.md mục 5 đang trích.
    """
    bang = bo_do.thi_nghiem_doi_chung(bo_sach)
    assert [hang[0] for hang in bang] == list(bo_do.TI_LE_BO_DIEM)

    giu_nguyen, bo_het = bang[0], bang[-1]
    assert round(giu_nguyen[1], 1) == 90.2, "tài liệu ghi TB 90,2 khi giữ điểm"
    assert round(bo_het[1], 1) == 4.1, "tài liệu ghi TB 4,1 khi bỏ hết điểm"
    assert bo_het[1] < giu_nguyen[1] / 10, (
        "bỏ hết điểm phải làm số cặp SỤT hẳn — nếu tăng thì kết luận về "
        "nguyên nhân trong tài liệu đã sai")


def test_moi_muc_cua_thi_nghiem_van_giu_tinh_on_dinh(bo_do, bo_sach):
    """`thi_nghiem_doi_chung` tự dừng nếu gặp cặp phá vỡ. Test này canh cái
    chốt đó còn nguyên: bỏ điểm là đổi ưu tiên, và đổi ưu tiên KHÔNG được
    phép phá tính ổn định."""
    src = open(BO_DO, encoding="utf-8").read()
    assert "verify_stability" in src and "BAT NGO" in src
    bo_do.thi_nghiem_doi_chung(bo_sach, so_seed=2)   # không được ném lỗi
