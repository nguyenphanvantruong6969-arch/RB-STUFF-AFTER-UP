"""
Test canh cho bộ đo tính TỐI ƯU (`du_lieu_test/do_toi_uu_on_dinh.py`,
`do_khai_that.py`, `do_ben_vung.py` và thư viện `co_che_doi_chung.py`).

Theo thông lệ của dự án: mỗi bảng số công bố phải có test canh, và test phải
canh được cả hai chiều — cái đúng phải xanh, mà **bộ đo hỏng phải đỏ**. Nên
ngoài các mệnh đề thuận, tệp này có một nhóm ĐỐI CHỨNG NGƯỢC: nếu bộ đếm cặp
phá vỡ hoặc bộ dò khai gian bị hỏng thành "lúc nào cũng báo 0" thì nhóm đó
đỏ ngay.

Nhóm test                                   Canh mệnh đề nào
------------------------------------------  ------------------------------
TestVetCanTapOnDinh                         RB-DA là ma trận ổn định tốt
                                            nhất cho học sinh
TestDaClbDeXuat                             bản CLB đề xuất là bản THẬT,
                                            không phải bản sao run_rbda
TestDoiChungNguoc                           bộ đếm cặp phá vỡ có thật sự
                                            bắt được kết quả không ổn định
TestChuTrinhPareto                          bộ tìm chu trình khớp với bộ
                                            đếm cặp đôi có sẵn
TestKhaiThat                                khai thật là tốt nhất dưới
                                            RB-DA, và KHÔNG phải dưới Boston
TestDoBen                                   nhiễu không sinh cặp phá vỡ
TestSoLieuKhopTepJson                       số công bố = số chạy lại được

ĐÃ THỬ LÀM HỎNG PHẦN MỀM ĐỂ XEM BỘ TEST CÓ BẮT ĐƯỢC KHÔNG
----------------------------------------------------------
Một bộ test luôn xanh chưa chứng minh được gì. Hai lần phá hoại có chủ đích,
cả hai đều bị bắt:

| Phá cái gì | Kết quả |
|---|---|
| Đảo hai khoá xếp hạng trong `compute_club_priority` (bốc thăm lên trước điểm) | **3 test đỏ** |
| Làm bộ đếm cặp phá vỡ luôn trả 0 | **6 test đỏ**, trong đó cả ba test `TestDoiChungNguoc` |

Lần thứ hai là lần quan trọng: nó mô phỏng đúng kiểu hỏng nguy hiểm nhất — bộ
đo báo "0 cặp phá vỡ" cho mọi thứ, khiến kết quả trông hoàn hảo. Nhóm
`TestDoiChungNguoc` tồn tại chỉ để bắt kiểu hỏng đó.
"""

import json
import os
import random
import shutil
import sys
import tempfile

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import rbda_priority_pipeline as loi  # noqa: E402
import co_che_doi_chung as cc  # noqa: E402
import do_khai_that as dkt  # noqa: E402
import do_toi_uu_on_dinh as dtu  # noqa: E402
from do_anh_huong_seed import BO_DU_LIEU, nap_bo  # noqa: E402

SO_THE_HIEN_TEST = 40      # đủ để bắt lỗi, đủ nhanh để chạy trong bộ test


# ---------------------------------------------------------------------------
# FIXTURE
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def bo_sach():
    """Bộ dữ liệu 140 em / 12 CLB, nạp một lần cho cả module."""
    thu_muc = tempfile.mkdtemp()
    try:
        db = nap_bo(thu_muc, BO_DU_LIEU[1][1])
        students, clubs, scores, app, prefs, _ = loi.load_from_sqlite(db)
    finally:
        shutil.rmtree(thu_muc)
    return students, clubs, scores, app, prefs


@pytest.fixture(scope="module")
def bo_sach_da_chay(bo_sach):
    students, clubs, scores, app, prefs = bo_sach
    stb = loi.generate_stb_lottery(sorted(students), dtu.SEED_MOC)
    elig = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda(students, clubs, scores, app, prefs, stb, elig)
    br = cc.tinh_base_rank(clubs, scores, app, stb)
    return dict(kq.assignment), stb, elig, br, cc._ham_chon(clubs, br, elig)


def _the_hien(n=SO_THE_HIEN_TEST, co_du_tru=True, hat=dtu.HAT_SINH):
    """Sinh n thể hiện nhỏ kèm bộ số bốc thăm — cùng hạt giống mỗi lần chạy."""
    rng = random.Random(hat)
    ra = []
    for _ in range(n):
        th = dtu.sinh_the_hien_nho(rng, co_du_tru=co_du_tru)
        stb = loi.generate_stb_lottery(sorted(th[0]), rng.randint(1, 10 ** 6))
        elig = loi.default_reserve_eligible_fn(th[0], th[1])
        ra.append((th, stb, elig))
    return ra


# ---------------------------------------------------------------------------
# 1 — RB-DA CÓ PHẢI MA TRẬN ỔN ĐỊNH TỐT NHẤT CHO HỌC SINH KHÔNG
# ---------------------------------------------------------------------------

class TestVetCanTapOnDinh:

    @pytest.mark.parametrize("co_du_tru", [False, True])
    def test_rbda_nam_trong_tap_on_dinh(self, co_du_tru):
        """Kết quả RB-DA phải là MỘT phần tử của tập ổn định vét cạn.

        Đây là phép kiểm độc lập với `verify_stability`: tập ổn định được
        dựng bằng cách liệt kê mọi phép gán rồi lọc, không đi qua thuật toán.
        """
        for th, stb, elig in _the_hien(co_du_tru=co_du_tru):
            students, clubs, scores, app, prefs = th
            tap = cc.liet_ke_ghep_on_dinh(students, clubs, scores, app, prefs, stb, elig)
            if not tap:
                continue
            xep = dict(loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment)
            assert any(all(m.get(s) == xep.get(s) for s in students) for m in tap)

    @pytest.mark.parametrize("co_du_tru", [False, True])
    def test_rbda_toi_uu_cho_hoc_sinh(self, co_du_tru):
        """Không một em nào thích một ma trận ổn định KHÁC hơn kết quả RB-DA.

        Đây là mệnh đề trung tâm của cả nghiên cứu. Nó KHÔNG hiển nhiên: định
        lý Gale–Shapley giả định mỗi CLB có một danh sách ưu tiên cố định, mà
        hàm lựa chọn ở đây không phải thế khi có suất dự trữ (xem
        `du_lieu_test/do_hai_canh_du_tru.py`).
        """
        for th, stb, elig in _the_hien(co_du_tru=co_du_tru):
            students, clubs, scores, app, prefs = th
            tap = cc.liet_ke_ghep_on_dinh(students, clubs, scores, app, prefs, stb, elig)
            if not tap:
                continue
            xep = dict(loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment)
            for m in tap:
                assert cc.yeu_thich_hon_moi_em(xep, m, prefs), (
                    "Co ma tran on dinh mot em thich hon ket qua RB-DA: %r" % m)

    def test_tap_em_co_suat_bat_bien(self):
        """Định lý bệnh viện nông thôn: 'ai có suất' giống nhau ở MỌI ma trận
        ổn định. Chỉ 'vào CLB nào' mới đổi.

        Hệ quả thực tế: đổi sang một cơ chế ổn định khác KHÔNG cứu được em
        nào đang trượt.
        """
        for th, stb, elig in _the_hien():
            students, clubs, scores, app, prefs = th
            tap = cc.liet_ke_ghep_on_dinh(students, clubs, scores, app, prefs, stb, elig)
            if len(tap) < 2:
                continue
            tap_co_suat = {frozenset(s for s, c in m.items() if c is not None) for m in tap}
            assert len(tap_co_suat) == 1

    def test_co_the_hien_nhieu_hon_mot_ma_tran_on_dinh(self):
        """Bộ sinh thể hiện phải tạo ra được ca KHÓ.

        Nếu mọi thể hiện chỉ có đúng một ma trận ổn định thì hai test ở trên
        đúng một cách tầm thường và không canh được gì. Test này canh chính
        bộ sinh dữ liệu.
        """
        nhieu = 0
        for th, stb, elig in _the_hien(n=120):
            students, clubs, scores, app, prefs = th
            tap = cc.liet_ke_ghep_on_dinh(students, clubs, scores, app, prefs, stb, elig)
            if len(tap) > 1:
                nhieu += 1
        assert nhieu >= 5, "Bo sinh the hien khong tao ra ca kho nao"


# ---------------------------------------------------------------------------
# 2 — DA DO CLB ĐỀ XUẤT LÀ BẢN THẬT
# ---------------------------------------------------------------------------

class TestDaClbDeXuat:

    def test_khac_ban_hoc_sinh_de_xuat_o_vi_du_kinh_dien(self):
        """Ví dụ hai em hai CLB có nguyện vọng ngược hẳn ưu tiên.

        Đây là test QUAN TRỌNG NHẤT của nhóm: nếu `da_clb_de_xuat` chỉ là
        bản sao của `run_rbda` thì mọi bảng so sánh dàn ổn định trở thành
        vô nghĩa, mà bảng đó lại đang toàn 'giống hệt nhau'. Test này chứng
        minh 'giống hệt' là tính chất của DỮ LIỆU, không phải của bộ đo.
        """
        students = {"s1": {}, "s2": {}}
        clubs = {"c1": {"capacity": 1, "reserve_capacity": 0},
                 "c2": {"capacity": 1, "reserve_capacity": 0}}
        scores = {"c1": {"s2": 9.0, "s1": 1.0}, "c2": {"s1": 9.0, "s2": 1.0}}
        app = {"c1": ["s1", "s2"], "c2": ["s1", "s2"]}
        prefs = {"s1": ["c1", "c2"], "s2": ["c2", "c1"]}
        stb = {"s1": 0, "s2": 1}
        elig = lambda s, c: False  # noqa: E731

        hs = dict(loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment)
        clb = cc.da_clb_de_xuat(students, clubs, scores, app, prefs, stb, elig)

        assert hs == {"s1": "c1", "s2": "c2"}    # mỗi em được nguyện vọng 1
        assert clb == {"s1": "c2", "s2": "c1"}   # mỗi em được nguyện vọng 2
        assert hs != clb

        tap = cc.liet_ke_ghep_on_dinh(students, clubs, scores, app, prefs, stb, elig)
        assert len(tap) == 2                     # đúng hai đầu của dàn ổn định

    def test_ket_qua_luon_on_dinh(self):
        """Đổi bên đề xuất thì vẫn phải ra một ma trận ỔN ĐỊNH."""
        for th, stb, elig in _the_hien():
            students, clubs, scores, app, prefs = th
            xep = cc.da_clb_de_xuat(students, clubs, scores, app, prefs, stb, elig)
            br = cc.tinh_base_rank(clubs, scores, app, stb)
            assert cc.la_ghep_on_dinh(xep, clubs, prefs, br, cc._ham_chon(clubs, br, elig))

    def test_hoc_sinh_khong_bao_gio_thich_ban_clb_hon(self):
        """Bản do học sinh đề xuất phải được mọi em yếu-thích hơn bản CLB."""
        for th, stb, elig in _the_hien():
            students, clubs, scores, app, prefs = th
            hs = dict(loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment)
            clb = cc.da_clb_de_xuat(students, clubs, scores, app, prefs, stb, elig)
            assert cc.yeu_thich_hon_moi_em(hs, clb, prefs)


# ---------------------------------------------------------------------------
# 3 — ĐỐI CHỨNG NGƯỢC: BỘ ĐẾM CẶP PHÁ VỠ CÓ THẬT SỰ BẮT ĐƯỢC LỖI KHÔNG
# ---------------------------------------------------------------------------

class TestDoiChungNguoc:

    def test_rbda_khong_co_cap_pha_vo(self, bo_sach, bo_sach_da_chay):
        _students, clubs, _sc, _app, prefs = bo_sach
        xep, _stb, _elig, br, chon = bo_sach_da_chay
        assert cc.thong_ke(xep, clubs, prefs, br, chon)["cap_pha_vo"] == 0

    @pytest.mark.parametrize("ten_co_che", ["boston", "boc_tham", "ttc"])
    def test_co_che_khong_on_dinh_PHAI_co_cap_pha_vo(self, bo_sach, bo_sach_da_chay,
                                                     ten_co_che):
        """Ba cơ chế này lý thuyết nói KHÔNG ổn định — bộ đếm phải thấy điều đó.

        Nếu test này đỏ thì bộ đếm cặp phá vỡ đang trả 0 cho mọi thứ, và câu
        '0 cặp phá vỡ' nói về RB-DA mất hết giá trị.
        """
        students, clubs, scores, app, prefs = bo_sach
        _xep, stb, elig, br, chon = bo_sach_da_chay
        fn = {"boston": cc.co_che_boston,
              "boc_tham": cc.co_che_thu_tu_boc_tham,
              "ttc": cc.co_che_ttc}[ten_co_che]
        xep = fn(students, clubs, scores, app, prefs, stb, elig)
        assert cc.thong_ke(xep, clubs, prefs, br, chon)["cap_pha_vo"] > 0

    def test_bo_dem_bat_duoc_ket_qua_bi_lam_hong(self, bo_sach, bo_sach_da_chay):
        """Cố ý đổi chỗ hai em cho nhau -> phải sinh ra cặp phá vỡ.

        Đây là phép thử trực tiếp nhất: lấy kết quả ĐÚNG rồi phá nó.
        """
        _students, clubs, _sc, _app, prefs = bo_sach
        xep, _stb, _elig, br, chon = bo_sach_da_chay
        hong = dict(xep)
        co_suat = [s for s, c in hong.items() if c is not None]
        a, b = co_suat[0], next(s for s in co_suat if hong[s] != hong[co_suat[0]])
        hong[a], hong[b] = hong[b], hong[a]
        assert cc.thong_ke(hong, clubs, prefs, br, chon)["cap_pha_vo"] > 0


# ---------------------------------------------------------------------------
# 4 — CHU TRÌNH PARETO
# ---------------------------------------------------------------------------

class TestChuTrinhPareto:

    def test_khop_voi_bo_dem_cap_doi_co_san(self, bo_sach, bo_sach_da_chay):
        """Có cặp đôi cùng có lợi <=> có chu trình.

        `do_danh_doi_on_dinh.py` đếm được 85 cặp đôi trên bộ này. Bản đầu của
        `chu_trinh_pareto` báo 0 chu trình — hai con số không thể cùng đúng.
        Test này canh đúng chỗ đó: hễ tồn tại một cặp đôi cùng có lợi thì bộ
        tìm chu trình PHẢI tìm ra ít nhất một chu trình.
        """
        _students, _clubs, _sc, _app, prefs = bo_sach
        xep, _stb, _elig, _br, _chon = bo_sach_da_chay
        bang = cc.bang_thu_hang_nguyen_vong(prefs)

        co_cap_doi = any(
            cc.thich_hon(bang, s1, xep[s2], xep[s1]) and
            cc.thich_hon(bang, s2, xep[s1], xep[s2])
            for s1 in xep if xep[s1] for s2 in xep if xep[s2] and s2 != s1
        )
        ct, _sau = cc.chu_trinh_pareto(xep, prefs)
        assert co_cap_doi == (len(ct) > 0)
        assert len(ct) > 0, "Bo nay CO cap doi cung co loi, phai tim ra chu trinh"

    def test_moi_em_tren_chu_trinh_deu_len_hang(self, bo_sach, bo_sach_da_chay):
        """Định nghĩa của chu trình cùng có lợi: KHÔNG ai bị thiệt."""
        _students, _clubs, _sc, _app, prefs = bo_sach
        xep, _stb, _elig, _br, _chon = bo_sach_da_chay
        ct, sau = cc.chu_trinh_pareto(xep, prefs)
        bang = cc.bang_thu_hang_nguyen_vong(prefs)
        for chu_trinh in ct:
            for sid in chu_trinh:
                assert sau[sid] != xep[sid]
        for sid in xep:
            assert not cc.thich_hon(bang, sid, xep[sid], sau[sid]), (
                "Em %s bi THIET sau khi doi cho — khong con la cai tien Pareto" % sid)

    def test_doi_xong_thi_het_chu_trinh(self, bo_sach, bo_sach_da_chay):
        """Chạy lại trên kết quả đã đổi phải ra 0 chu trình (đã Pareto tối ưu)."""
        _students, _clubs, _sc, _app, prefs = bo_sach
        xep, _stb, _elig, _br, _chon = bo_sach_da_chay
        _ct, sau = cc.chu_trinh_pareto(xep, prefs)
        ct2, _ = cc.chu_trinh_pareto(sau, prefs)
        assert ct2 == []

    def test_gia_cua_viec_doi_cho_la_mat_on_dinh(self, bo_sach, bo_sach_da_chay):
        """Đổi chỗ theo chu trình làm học sinh lên hạng NHƯNG sinh cặp phá vỡ.

        Đây là toàn bộ nội dung của phần 'cái giá của tính ổn định': hai điều
        đó không thể có cùng lúc.
        """
        _students, clubs, _sc, _app, prefs = bo_sach
        xep, _stb, _elig, br, chon = bo_sach_da_chay
        _ct, sau = cc.chu_trinh_pareto(xep, prefs)
        truoc = cc.thong_ke(xep, clubs, prefs, br, chon)
        sau_tk = cc.thong_ke(sau, clubs, prefs, br, chon)
        assert truoc["cap_pha_vo"] == 0
        assert sau_tk["cap_pha_vo"] > 0
        assert sau_tk["thu_hang_tb"] < truoc["thu_hang_tb"]


# ---------------------------------------------------------------------------
# 5 — KHAI THẬT
# ---------------------------------------------------------------------------

class TestKhaiThat:

    def test_rbda_khong_khai_gian_duoc(self):
        """Vét cạn mọi cách khai: không em nào lợi được dưới RB-DA."""
        for th, stb, elig in _the_hien():
            r = dkt.do_mot_the_hien(th, stb, elig, dkt._rbda, sorted(th[0]),
                                    rng=random.Random(1))
            assert r["so_em_khai_gian_duoc"] == 0, (
                "Tim thay cach khai gian co loi duoi RB-DA: %r" % r["vi_du"])

    def test_boston_PHAI_khai_gian_duoc(self):
        """Đối chứng ngược. Boston thưởng cho khai gian — lý thuyết nói vậy.

        Nếu test này đỏ thì bộ dò khai gian hỏng, và con số '0 em khai gian
        được dưới RB-DA' chỉ chứng minh bộ dò không hoạt động.
        """
        tong = 0
        for th, stb, elig in _the_hien():
            r = dkt.do_mot_the_hien(th, stb, elig, cc.co_che_boston, sorted(th[0]),
                                    rng=random.Random(1))
            tong += r["so_em_khai_gian_duoc"]
        assert tong > 0

    def test_them_clb_khong_thich_khong_bao_gio_co_loi(self):
        """Chấm kết cục theo nguyện vọng THẬT: CLB ngoài danh sách = trượt."""
        that = ["c1", "c2", "c3"]
        assert dkt.diem_ket_cuc("c1", that) == 0
        assert dkt.diem_ket_cuc("c3", that) == 2
        assert dkt.diem_ket_cuc("c9", that) == len(that) + 1
        assert dkt.diem_ket_cuc(None, that) == len(that) + 1

    def test_khong_gian_khai_co_du_cach_cat_ngan(self):
        """Cắt ngắn danh sách thật là kiểu khai gian dễ nghĩ nhất — phải luôn
        có mặt trong không gian tìm kiếm, kể cả khi bị chặn trần."""
        that = ["a", "b", "c", "d"]
        cach = dkt.cac_cach_khai(that, tran=5, rng=random.Random(0))
        for k in range(1, len(that)):
            assert tuple(that[:k]) in cach


# ---------------------------------------------------------------------------
# 6 — ĐỘ BỀN
# ---------------------------------------------------------------------------

class TestDoBen:

    def test_nhieu_khong_bao_gio_sinh_cap_pha_vo(self, bo_sach):
        """Rung chỉ tiêu và rung điểm được phép đổi ai vào đâu, nhưng KHÔNG
        được phép làm kết quả mất tính ổn định."""
        students, clubs, scores, app, prefs = bo_sach
        for cid in list(clubs)[:4]:
            for delta in (-1, +1):
                cap = clubs[cid]["capacity"] + delta
                if cap < 1:
                    continue
                clubs_moi = {c: dict(i) for c, i in clubs.items()}
                clubs_moi[cid]["capacity"] = cap
                clubs_moi[cid]["reserve_capacity"] = min(
                    clubs_moi[cid]["reserve_capacity"], cap)
                stb = loi.generate_stb_lottery(sorted(students), dtu.SEED_MOC)
                elig = loi.default_reserve_eligible_fn(students, clubs_moi)
                kq = loi.run_rbda(students, clubs_moi, scores, app, prefs, stb, elig)
                assert loi.verify_stability(kq, clubs_moi, prefs, elig) == []

    def test_nhieu_diem_nho_doi_it_hon_nhieu_diem_lon(self, bo_sach):
        """Độ bền phải ĐƠN ĐIỆU: nhiễu ±0,1 không được xáo nhiều hơn ±0,5.

        Nếu nhiễu bé mà xáo nhiều hơn nhiễu lớn thì kết quả đang phụ thuộc
        vào thứ gì đó không phải điểm.
        """
        students, clubs, scores, app, prefs = bo_sach

        def dem(bien_do, seed):
            rng = random.Random(seed)
            sc = {c: {s: max(0.0, min(10.0, d + rng.uniform(-bien_do, bien_do)))
                      for s, d in m.items()} for c, m in scores.items()}
            stb = loi.generate_stb_lottery(sorted(students), dtu.SEED_MOC)
            elig = loi.default_reserve_eligible_fn(students, clubs)
            goc = loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment
            moi = loi.run_rbda(students, clubs, sc, app, prefs, stb, elig).assignment
            return sum(1 for s in students if goc[s] != moi[s])

        nho = sum(dem(0.1, s) for s in range(1, 11))
        lon = sum(dem(0.5, s) for s in range(1, 11))
        assert nho < lon


# ---------------------------------------------------------------------------
# 7 — SỐ CÔNG BỐ PHẢI LÀ SỐ CHẠY LẠI ĐƯỢC
# ---------------------------------------------------------------------------

class TestSoLieuKhopTepJson:
    """Chặn việc số trong báo cáo bị sửa tay cho đẹp.

    Ba tệp JSON là nguồn sự thật duy nhất cho `docs/NGHIEN_CUU_TOI_UU.md` và
    `.html`. Test này chạy lại một phần phép đo rồi đối chiếu.
    """

    @pytest.mark.parametrize("ten_tep", [
        "so_lieu_toi_uu.json", "so_lieu_khai_that.json", "so_lieu_ben_vung.json",
    ])
    def test_tep_ton_tai_va_doc_duoc(self, ten_tep):
        duong = os.path.join(GOC, "du_lieu_test", ten_tep)
        assert os.path.exists(duong), "Chua chay bo do — thieu %s" % ten_tep
        with open(duong, encoding="utf-8") as f:
            assert json.load(f)

    def test_bang_so_co_che_chay_lai_ra_dung_so_cu(self, bo_sach, bo_sach_da_chay):
        """Bảng năm cơ chế trên `bo_sach` phải tái lập từng con số."""
        duong = os.path.join(GOC, "du_lieu_test", "so_lieu_toi_uu.json")
        with open(duong, encoding="utf-8") as f:
            so_lieu = json.load(f)
        khoa = next(k for k in so_lieu["tn24_so_co_che"] if k.startswith("bo_sach"))
        da_luu = so_lieu["tn24_so_co_che"][khoa]

        students, clubs, scores, app, prefs = bo_sach
        xep_rbda, stb, elig, br, chon = bo_sach_da_chay
        for nhan, fn in dtu.CO_CHE:
            xep = xep_rbda if fn is None else fn(students, clubs, scores, app,
                                                 prefs, stb, elig)
            tk = cc.thong_ke(xep, clubs, prefs, br, chon)
            for cot in ("nv1", "nv2", "nv3_tro_len", "khong_suat",
                        "thu_hang_tb", "cap_pha_vo"):
                assert tk[cot] == da_luu[nhan][cot], (
                    "%s / %s: tep JSON ghi %r, chay lai ra %r"
                    % (nhan, cot, da_luu[nhan][cot], tk[cot]))

    def test_khong_co_phan_vi_du_nao_trong_tn1(self):
        """`phan_vi_du` chỉ được ghi khi TÌM THẤY ca RB-DA không tối ưu.

        Danh sách đó phải rỗng. Nếu một ngày nó không rỗng nữa thì kết luận
        chính của nghiên cứu đã sai và phải viết lại — test này bắt trước.
        """
        duong = os.path.join(GOC, "du_lieu_test", "so_lieu_toi_uu.json")
        with open(duong, encoding="utf-8") as f:
            so_lieu = json.load(f)
        for nhan in ("khong_du_tru", "co_du_tru"):
            t = so_lieu["tn1_toi_uu_hoc_sinh"][nhan]
            assert t["phan_vi_du"] == []
            assert t["rbda_toi_uu_cho_hoc_sinh"] == t["so_the_hien"]
            assert t["rbda_nam_trong_tap_on_dinh"] == t["so_the_hien"]
