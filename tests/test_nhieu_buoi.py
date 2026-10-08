# -*- coding: utf-8 -*-
"""Test canh cho tính năng NHIỀU BUỔI SINH HOẠT trong tuần.

Mệnh đề trung tâm của cả tính năng: vì mỗi câu lạc bộ sinh hoạt đúng một
buổi, mỗi em tối đa một câu lạc bộ mỗi buổi, và không có trần số câu lạc bộ
mỗi tuần, nên **các buổi độc lập hoàn toàn**. Bài toán tuần là N bản sao độc
lập của bài toán đã giải, không phải một bài toán lớn hơn.

Tệp này canh đúng mệnh đề đó và các hệ quả của nó.

Nhóm test                  Canh mệnh đề nào
-------------------------  ---------------------------------------------
TestTrungKhit              MỘT buổi ⇒ kết quả Y HỆT phần mềm trước khi có
                           tính năng này. Đây là test QUAN TRỌNG NHẤT
TestRangBuocBuoi           ≤1 câu lạc bộ mỗi buổi · 0 cặp phá vỡ mỗi buổi
TestBaCachBocTham          ba cách cho kết quả KHÁC nhau, và cách nào cũng
                           tái lập được giữa hai tiến trình
TestDiTru                  cơ sở dữ liệu lược đồ cũ mở được, không mất gì
TestNhapDuLieu             cột `buoi`, bộ cột nguyện vọng theo buổi, và hai
                           phép soát cảnh báo
TestMotThietKeDuyNhat      phần mềm chỉ chạy `stb_ngay`, không mở lại lựa chọn
TestChayDayDu              đường chạy đầy đủ qua API, xuất thời khoá biểu
TestSoBocThamTheoBuoi      bảng thứ tự từng buổi phải đúng tới từng ô
TestThuTuNgayTrongTuan     sắp buổi theo THỨ TỰ NGÀY, không theo vần chữ cái
TestChonBuoi               chạy riêng một buổi ra ĐÚNG kết quả của buổi đó
                           khi chạy cả tuần
TestChonBuoiQuaAPI         buổi không chọn GIỮ NGUYÊN kết quả cũ
TestCauLacBoDoiBuoi        câu lạc bộ dời buổi thì dòng cũ của nó biến mất
                           theo, kể cả khi buổi cũ vẫn còn câu lạc bộ khác
TestXuatTepSauKhiChayMotPhan
                           tệp xuất ra nói về CƠ SỞ DỮ LIỆU, nên chạy một
                           phần không cắt mất các ngày đã công bố

ĐÃ THỬ LÀM HỎNG ĐỂ XEM TEST CÓ BẮT ĐƯỢC KHÔNG
---------------------------------------------
| Phá cái gì | Kết quả |
|---|---|
| Bỏ lọc theo buổi trong `cat_du_lieu_theo_buoi` | **2 test đỏ** ở `TestRangBuocBuoi` |
| Cài `stb_ngay` thành `stb_tuan` (bỏ nhánh hoán vị) | **1 test đỏ** ở `TestBaCachBocTham` |
| Dùng `hash()` thay `zlib.crc32` trong `_seed_cua_buoi` | **1 test đỏ** — đúng test dựng riêng cho chuyện đó |
| Thêm lại tham số `che_do_boc_tham` vào `api.run_pipeline` | **1 test đỏ** ở `TestMotThietKeDuyNhat` |
| Đổi mặc định ngược về `stb_tuan` | **4 test đỏ** ở ba lớp khác nhau |
| Truyền danh sách buổi ĐÃ LỌC vào `sinh_stb_theo_buoi` | **1 test đỏ** — đúng cái bất biến của `chi_buoi` |
| Xoá `match_results` không điều kiện | **2 test đỏ** ở `TestChonBuoiQuaAPI` |
| Sắp buổi theo vần chữ cái như bản cũ | **2 test đỏ** ở `TestThuTuNgayTrongTuan` |
| Bỏ chặn vẽ lại số bốc thăm khi chạy một phần | **1 test đỏ** |

Hai chuyện học được khi làm phép thử này, cả hai đều đã sửa:

**Phép phá thứ nhất lúc đầu chỉ làm đỏ MỘT test.** Lý do: `run_rbda` vốn
đã bỏ qua nguyện vọng trỏ tới câu lạc bộ không có trong tập được truyền
vào, nên bỏ lọc đi thì chỗ xếp ai vào đâu vẫn đúng. Cái hỏng nằm chỗ khác
và im hơn nhiều: **thứ hạng nguyện vọng** bị đếm theo cả tuần thay vì
trong buổi, nên một em được đúng câu lạc bộ mình thích nhất buổi Thứ 5 lại
bị ghi là "nguyện vọng 3". Đã thêm
`test_thu_hang_nguyen_vong_tinh_TRONG_BUOI` để canh, và giờ phép phá đó
làm đỏ hai test.

**Phép phá thứ ba không hiện ra trong một lần chạy pytest.** `hash()` của
chuỗi bị ngẫu nhiên hoá theo từng tiến trình, nên mọi test trong cùng tiến
trình đều thấy cùng một giá trị và đều xanh. Chỉ phép so giữa HAI tiến
trình mới bắt được — đó là lý do test ấy phải gọi `subprocess` và ép
`PYTHONHASHSEED` khác nhau.

**Phép phá thứ tư phải soát CHỮ KÝ hàm, không soát hành vi.** Ai đó thêm
lại tham số `che_do_boc_tham` với mặc định `'stb_ngay'` sẽ qua được mọi
test hành vi — kết quả vẫn đúng — trong khi giao diện hoặc một lời gọi
khác đã có thể truyền `'stb_co_bu'` vào. Cái phải chặn là sự tồn tại của
lựa chọn, nên test phải nhìn vào `inspect.signature`.

**Phép phá thứ năm là phép phá tinh vi nhất trong tệp này.** Truyền danh
sách buổi ĐÃ LỌC vào `sinh_stb_theo_buoi` trông hoàn toàn hợp lý — đang
chạy buổi nào thì sinh số cho buổi ấy. Nhưng hàm đó ngắn mạch khi danh
sách chỉ có một phần tử, nên chạy riêng thứ Năm sẽ dùng bộ số GỐC thay vì
hoán vị của thứ Năm. Kết quả vẫn ổn định, vẫn 0 cặp phá vỡ, chỉ khác kết
quả của chính buổi đó khi chạy cả tuần — không test nào về ràng buộc hay
ổn định bắt được. Phải có một test so THẲNG hai đường với nhau.
"""

import csv
import inspect
import io
import json
import os
import re
import sqlite3
import subprocess
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import rbda_priority_pipeline as loi  # noqa: E402
from api import PipelineAPI  # noqa: E402

BO_MAU = os.path.join(GOC, "du_lieu_test", "bo_nhieu_buoi")
TEP_MAU = [
    "NHIEUBUOI_01_danh_sach_CLB.csv",
    "NHIEUBUOI_02_chon_CLB_muon_thi.csv",
    "NHIEUBUOI_03_xep_hang_nguyen_vong.csv",
]


# ---------------------------------------------------------------------------
# FIXTURE
# ---------------------------------------------------------------------------

def _nap_bo_mau(api):
    for ten in TEP_MAU:
        with open(os.path.join(BO_MAU, ten), encoding="utf-8-sig") as f:
            kq = api.import_csv_auto(f.read())
        assert kq["ok"], kq


@pytest.fixture
def api_nhieu_buoi(tmp_path):
    """API đã nạp sẵn bộ dữ liệu mẫu 5 buổi."""
    api = PipelineAPI(str(tmp_path / "app.db"), thu_muc_xuat=str(tmp_path))
    _nap_bo_mau(api)
    return api


@pytest.fixture
def du_lieu_nhieu_buoi(api_nhieu_buoi):
    """(students, clubs, scores, applicants, preferences, stb, reserve_fn)."""
    api_nhieu_buoi.run_pipeline(seed=42)
    st, cl, sc, ap, pr, _ = loi.load_from_sqlite(api_nhieu_buoi.db_path)
    stb = {sid: info["stb"] for sid, info in st.items()}
    return st, cl, sc, ap, pr, stb, loi.default_reserve_eligible_fn(st, cl)


def _bo_mot_buoi(tmp_path, ten_bo):
    """Nạp một trong ba bộ dữ liệu CŨ (đều chỉ có một buổi)."""
    from do_anh_huong_seed import BO_DU_LIEU, nap_bo

    # Ten bo du lieu "TEST_0*" co dau sao, ma Windows KHONG cho dat ten
    # thu muc chua ky tu do — os.makedirs nem WinError 123. Ten thu muc o
    # day chi de tach cac bo ra cho khoi dam, khong mang y nghia gi, nen
    # thay ky tu cam la duoc.
    thu_muc = str(tmp_path / re.sub(r'[<>:"/\\|?*]', "_", ten_bo))
    os.makedirs(thu_muc, exist_ok=True)
    duong = dict(
        (ten.strip().split()[0], files) for ten, files in BO_DU_LIEU
    )[ten_bo]
    db = nap_bo(thu_muc, duong)
    return loi.load_from_sqlite(db)


# ---------------------------------------------------------------------------
# 1 — TRÙNG KHÍT: MỘT BUỔI PHẢI RA ĐÚNG KẾT QUẢ CŨ
# ---------------------------------------------------------------------------

class TestTrungKhit:
    """Test quan trọng nhất của cả tệp.

    Toàn bộ `docs/NGHIEN_CUU_TOI_UU.md` — 2 088 thể hiện vét cạn, 1 400 lượt thử
    khai gian, 392 phép thử nhiễu — đo trên dữ liệu MỘT buổi. Những con số
    đó chỉ còn nói về phần mềm đang chạy nếu đường mới cho ra đúng kết quả
    của đường cũ trên dữ liệu ấy. Nhóm test này là chỗ mệnh đề đó được canh.
    """

    @pytest.mark.parametrize("ten_bo", ["vi_du_huong_dan", "bo_sach", "TEST_0*"])
    def test_mot_buoi_cho_ket_qua_y_het_run_rbda(self, tmp_path, ten_bo):
        students, clubs, scores, app, prefs, _ = _bo_mot_buoi(tmp_path, ten_bo)
        elig = loi.default_reserve_eligible_fn(students, clubs)

        for seed in range(1, 21):
            stb = loi.generate_stb_lottery(sorted(students), seed)
            cu = loi.run_rbda(students, clubs, scores, app, prefs, stb, elig)
            # KHÔNG truyền chế độ: phải đi qua đúng MẶC ĐỊNH mà phần mềm
            # dùng. Ghim cứng 'stb_tuan' ở đây thì test vẫn xanh sau một
            # lần đổi mặc định làm hỏng đường chạy thật — mà đây là test
            # giữ hiệu lực cho mọi con số trong docs/NGHIEN_CUU_TOI_UU.md.
            moi = loi.run_rbda_nhieu_buoi(
                students, clubs, scores, app, prefs, stb, elig, seed=seed,
            )
            assert moi.ds_buoi == [loi.BUOI_MAC_DINH]
            gop = {
                sid: theo_buoi[loi.BUOI_MAC_DINH]
                for sid, theo_buoi in moi.assignment.items()
            }
            assert gop == dict(cu.assignment), (
                "seed %d: duong nhieu buoi lech khoi run_rbda tren du lieu mot buoi"
                % seed
            )

    def test_mot_buoi_giu_nguyen_ca_tang_va_thu_hang(self, tmp_path):
        """Không chỉ 'vào câu lạc bộ nào' mà cả diện trúng tuyển và thứ hạng
        nguyện vọng cũng phải trùng — tệp xuất ra dùng cả ba cột đó."""
        students, clubs, scores, app, prefs, _ = _bo_mot_buoi(tmp_path, "bo_sach")
        elig = loi.default_reserve_eligible_fn(students, clubs)
        stb = loi.generate_stb_lottery(sorted(students), 42)

        cu = loi.run_rbda(students, clubs, scores, app, prefs, stb, elig)
        moi = loi.run_rbda_nhieu_buoi(
            students, clubs, scores, app, prefs, stb, elig, seed=42)
        mot = moi.per_buoi[loi.BUOI_MAC_DINH]

        assert mot.matched_tier == cu.matched_tier
        assert mot.rank_in_student_pref == cu.rank_in_student_pref
        assert mot.rounds_run == cu.rounds_run

    def test_mot_buoi_thi_ba_cach_boc_tham_cho_cung_ket_qua(self, tmp_path):
        """Một buổi thì không có gì để 'san đều qua các ngày' — ba cách phải
        trùng nhau. Khác nhau ở đây nghĩa là một cách nào đó đang tự bốc lại
        số ngoài tầm khoá bốc thăm."""
        students, clubs, scores, app, prefs, _ = _bo_mot_buoi(tmp_path, "bo_sach")
        elig = loi.default_reserve_eligible_fn(students, clubs)
        stb = loi.generate_stb_lottery(sorted(students), 42)

        kq = {
            cd: loi.run_rbda_nhieu_buoi(
                students, clubs, scores, app, prefs, stb, elig,
                che_do_boc_tham=cd, seed=42).assignment
            for cd in loi.CHE_DO_BOC_THAM
        }
        assert kq["stb_tuan"] == kq["stb_ngay"] == kq["stb_co_bu"]

    @pytest.mark.parametrize("ten_bo", ["vi_du_huong_dan", "bo_sach"])
    def test_duong_api_mot_buoi_van_trung_khit(self, tmp_path, ten_bo):
        """Trùng khít phải đúng trên ĐƯỜNG THẬT, không chỉ ở tầng thuật toán.

        `api.run_pipeline` mới là thứ trường bấm. Nó không còn nhận tham số
        chế độ, nên test này là chỗ duy nhất canh được rằng cái mặc định nó
        dùng vẫn cho đúng kết quả của bản trước khi có tính năng nhiều buổi.
        """
        from do_anh_huong_seed import BO_DU_LIEU, nap_bo

        thu_muc = str(tmp_path / ten_bo)
        os.makedirs(thu_muc, exist_ok=True)
        duong = dict(
            (ten.strip().split()[0], files) for ten, files in BO_DU_LIEU
        )[ten_bo]
        db = nap_bo(thu_muc, duong)

        from api import PipelineAPI

        api = PipelineAPI(db, thu_muc_xuat=thu_muc)
        assert api.run_pipeline(seed=42)["ok"]

        students, clubs, scores, app, prefs, stb = loi.load_from_sqlite(db)
        elig = loi.default_reserve_eligible_fn(students, clubs)
        cu = loi.run_rbda(students, clubs, scores, app, prefs, stb, elig)

        conn = sqlite3.connect(db)
        try:
            rows = conn.execute(
                "SELECT student_id, buoi, club_id FROM match_results").fetchall()
        finally:
            conn.close()
        assert {b for _, b, _ in rows} == {loi.BUOI_MAC_DINH}
        assert {sid: cid for sid, _, cid in rows} == dict(cu.assignment)
# ---------------------------------------------------------------------------

class TestRangBuocBuoi:

    def test_khong_em_nao_co_hai_clb_cung_buoi(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        kq = loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig, seed=42)
        cua = loi.buoi_cua_club(cl)
        for sid, theo_buoi in kq.assignment.items():
            da_dung = [cua[c] for c in theo_buoi.values() if c is not None]
            assert len(da_dung) == len(set(da_dung)), (
                "em %s bi xep hai CLB trung buoi: %r" % (sid, theo_buoi))

    def test_moi_buoi_deu_khong_co_cap_pha_vo(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        for che_do in loi.CHE_DO_BOC_THAM:
            kq = loi.run_rbda_nhieu_buoi(
                st, cl, sc, ap, pr, stb, elig, che_do_boc_tham=che_do, seed=42)
            theo_buoi = loi.verify_stability_tuan(kq, cl, pr, elig)
            assert all(v == [] for v in theo_buoi.values()), (
                "%s: co cap pha vo %r" % (che_do, theo_buoi))

    def test_chi_xep_vao_clb_em_co_khai(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        kq = loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig, seed=42)
        for sid, theo_buoi in kq.assignment.items():
            for cid in theo_buoi.values():
                if cid is not None:
                    assert cid in pr.get(sid, []), (
                        "em %s bi xep vao %s ma khong he khai" % (sid, cid))

    def test_cat_nguyen_vong_giu_nguyen_thu_tu(self):
        """Lọc theo buổi phải giữ thứ tự nguyện vọng gốc.

        Đây là chỗ cả thiết kế dựa vào: lọc một dãy đã sắp thì phần còn lại
        vẫn đúng thứ tự, nên không cần đánh số lại rank theo buổi, và dữ
        liệu nhập bằng bộ cột cũ vẫn chạy đúng.
        """
        clubs = {
            "a": {"capacity": 1, "reserve_capacity": 0, "buoi": "t3"},
            "b": {"capacity": 1, "reserve_capacity": 0, "buoi": "t5"},
            "c": {"capacity": 1, "reserve_capacity": 0, "buoi": "t3"},
            "d": {"capacity": 1, "reserve_capacity": 0, "buoi": "t5"},
        }
        prefs = {"s1": ["b", "a", "d", "c"]}
        _cl, _sc, _ap, pr_t3 = loi.cat_du_lieu_theo_buoi(
            "t3", ["a", "c"], clubs, {}, {}, prefs)
        _cl, _sc, _ap, pr_t5 = loi.cat_du_lieu_theo_buoi(
            "t5", ["b", "d"], clubs, {}, {}, prefs)
        assert pr_t3["s1"] == ["a", "c"]
        assert pr_t5["s1"] == ["b", "d"]

    def test_thu_hang_nguyen_vong_tinh_TRONG_BUOI(self):
        """Cột "Nguyện vọng thứ" phải đếm trong buổi, không đếm cả tuần.

        Em xếp Thứ 5 là nguyện vọng 1 của buổi Thứ 5 thì trên thời khoá
        biểu phải ghi "nguyện vọng 1", dù trong danh sách chung cả tuần nó
        đứng thứ ba. Ghi số toàn cục vào đó là nói với em rằng em tụt
        nguyện vọng trong khi thực ra em được đúng thứ mình muốn nhất ở
        buổi ấy — và nhà trường đọc bảng tổng kết cũng ra một bức tranh
        xấu hơn sự thật.
        """
        students = {"s1": {}}
        clubs = {
            "t3_a": {"capacity": 1, "reserve_capacity": 0, "buoi": "t3"},
            "t3_b": {"capacity": 1, "reserve_capacity": 0, "buoi": "t3"},
            "t5_a": {"capacity": 1, "reserve_capacity": 0, "buoi": "t5"},
        }
        app = {cid: ["s1"] for cid in clubs}
        # Trong danh sach chung, t5_a dung THU BA. Nhung trong buoi t5 no
        # la nguyen vong DAU TIEN.
        prefs = {"s1": ["t3_a", "t3_b", "t5_a"]}
        kq = loi.run_rbda_nhieu_buoi(
            students, clubs, {}, app, prefs, {"s1": 0},
            lambda s, c: False, seed=1)

        assert kq.assignment["s1"] == {"t3": "t3_a", "t5": "t5_a"}
        assert kq.per_buoi["t3"].rank_in_student_pref["s1"] == 1
        assert kq.per_buoi["t5"].rank_in_student_pref["s1"] == 1

    def test_clb_khong_khai_buoi_gom_vao_buoi_mac_dinh(self):
        clubs = {
            "a": {"capacity": 1, "reserve_capacity": 0, "buoi": None},
            "b": {"capacity": 1, "reserve_capacity": 0},
            "c": {"capacity": 1, "reserve_capacity": 0, "buoi": ""},
        }
        assert loi.nhom_theo_buoi(clubs) == {loi.BUOI_MAC_DINH: ["a", "b", "c"]}


# ---------------------------------------------------------------------------
# 3 — BA CÁCH BỐC THĂM
# ---------------------------------------------------------------------------

class TestBaCachBocTham:

    def test_ba_cach_cho_ket_qua_khac_nhau_khi_co_nhieu_buoi(self, du_lieu_nhieu_buoi):
        """Đối chứng ngược cho bộ chọn chế độ.

        Nếu ba cách cho kết quả giống hệt nhau trên dữ liệu NHIỀU buổi thì
        bộ chọn đang không có tác dụng gì, và bảng đối chiếu trên giao diện
        chỉ là ba bản sao của cùng một con số.
        """
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        xep = {
            cd: loi.run_rbda_nhieu_buoi(
                st, cl, sc, ap, pr, stb, elig, che_do_boc_tham=cd, seed=42).assignment
            for cd in loi.CHE_DO_BOC_THAM
        }
        assert xep["stb_tuan"] != xep["stb_ngay"]
        assert xep["stb_tuan"] != xep["stb_co_bu"]

    def test_chay_lai_ra_dung_ket_qua_cu(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        for cd in loi.CHE_DO_BOC_THAM:
            lan1 = loi.run_rbda_nhieu_buoi(
                st, cl, sc, ap, pr, stb, elig, che_do_boc_tham=cd, seed=42).assignment
            lan2 = loi.run_rbda_nhieu_buoi(
                st, cl, sc, ap, pr, stb, elig, che_do_boc_tham=cd, seed=42).assignment
            assert lan1 == lan2

    def test_seed_cua_buoi_tai_lap_duoc_giua_hai_tien_trinh(self):
        """Chặn `hash()` của Python lọt vào chỗ sinh seed.

        `hash()` của chuỗi bị ngẫu nhiên hoá theo từng tiến trình, nên lỗi
        này KHÔNG hiện ra trong một lần chạy pytest — mọi test trong cùng
        tiến trình đều thấy cùng giá trị. Phải so giữa HAI tiến trình, và
        phải ép PYTHONHASHSEED khác nhau để chắc chắn.
        """
        ma = (
            "import sys; sys.path.insert(0, %r); "
            "import rbda_priority_pipeline as loi; "
            "import json; print(json.dumps("
            "[loi._seed_cua_buoi(42, b) for b in ['thu_2','thu_3','thu_6']]))"
            % GOC
        )
        ket = []
        for hat in ("0", "1", "12345"):
            moi_truong = dict(os.environ, PYTHONHASHSEED=hat)
            ra = subprocess.run([sys.executable, "-c", ma], capture_output=True,
                                text=True, check=True, env=moi_truong)
            ket.append(json.loads(ra.stdout))
        assert ket[0] == ket[1] == ket[2], (
            "seed dan xuat doi giua cac tien trinh: %r — co phai dang dung hash()?"
            % ket
        )

    def test_stb_ngay_van_la_hoan_vi_hop_le(self, du_lieu_nhieu_buoi):
        """Mỗi buổi phải là một hoán vị đủ 0..n-1: không trùng số, không sót
        em nào. Trùng số là hai em hoà nhau ở chỗ lẽ ra phải phá hoà."""
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        ds_buoi = list(loi.nhom_theo_buoi(cl))
        theo_buoi = loi.sinh_stb_theo_buoi(stb, ds_buoi, 42, "stb_ngay")
        for buoi, bo_so in theo_buoi.items():
            assert set(bo_so) == set(stb), "buoi %s thieu hoac thua hoc sinh" % buoi
            assert sorted(bo_so.values()) == list(range(len(stb)))

    def test_stb_co_bu_dua_em_trang_tay_len_truoc(self):
        """Em chưa có câu lạc bộ nào phải đứng trước em đã có, bất kể số bốc
        thăm gốc — đó là toàn bộ định nghĩa của cách bốc thăm có bù."""
        stb_goc = {"a": 0, "b": 1, "c": 2}
        moi = loi._stb_co_bu(stb_goc, {"a": 2, "b": 0, "c": 1})
        assert moi["b"] < moi["c"] < moi["a"]

    def test_che_do_la_thi_bao_loi_ngay(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        with pytest.raises(ValueError):
            loi.run_rbda_nhieu_buoi(
                st, cl, sc, ap, pr, stb, elig, che_do_boc_tham="khong_co_that")


# ---------------------------------------------------------------------------
# 4 — DI TRÚ CƠ SỞ DỮ LIỆU CŨ
# ---------------------------------------------------------------------------

LUOC_DO_CU = """
CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT,
                       stb_number INTEGER, reserve_group TEXT);
CREATE TABLE clubs (club_id TEXT PRIMARY KEY, name TEXT, capacity INTEGER NOT NULL,
                    reserve_capacity INTEGER NOT NULL DEFAULT 0, reserve_group TEXT);
CREATE TABLE match_results (student_id TEXT PRIMARY KEY, club_id TEXT,
                            round_num INTEGER, matched_tier TEXT,
                            rank_in_student_pref INTEGER);
CREATE TABLE run_meta (id INTEGER PRIMARY KEY CHECK (id = 1), seed INTEGER,
                       run_at TEXT, rounds_run INTEGER, n_matched INTEGER,
                       n_total INTEGER);
CREATE TABLE run_history (run_id INTEGER PRIMARY KEY AUTOINCREMENT, seed INTEGER,
                          run_at TEXT, rounds_run INTEGER, n_matched INTEGER,
                          n_total INTEGER, stb_redrawn INTEGER NOT NULL DEFAULT 0);
CREATE TABLE stb_lock (id INTEGER PRIMARY KEY CHECK (id = 1),
                       is_locked INTEGER NOT NULL DEFAULT 0,
                       locked_at TEXT, unlocked_at TEXT);
CREATE TABLE club_test_selection (student_id TEXT NOT NULL, club_id TEXT NOT NULL,
                                  PRIMARY KEY (student_id, club_id));
CREATE TABLE club_scores (student_id TEXT NOT NULL, club_id TEXT NOT NULL,
                          score REAL NOT NULL, PRIMARY KEY (student_id, club_id));
CREATE TABLE preferences (student_id TEXT NOT NULL, club_id TEXT NOT NULL,
                          rank INTEGER NOT NULL, PRIMARY KEY (student_id, club_id));
"""


@pytest.fixture
def db_luoc_do_cu(tmp_path):
    """Một app.db dựng đúng theo lược đồ TRƯỚC khi có tính năng nhiều buổi."""
    duong = str(tmp_path / "cu.db")
    conn = sqlite3.connect(duong)
    conn.executescript(LUOC_DO_CU)
    conn.execute("INSERT INTO stb_lock VALUES (1, 1, '2025-01-01', NULL)")
    conn.execute("INSERT INTO clubs VALUES ('clb_a', 'CLB A', 5, 1, 'khoi_10')")
    conn.execute("INSERT INTO students VALUES ('HS1', 'An', 0, NULL)")
    conn.execute("INSERT INTO students VALUES ('HS2', 'Binh', 1, 'khoi_10')")
    conn.execute("INSERT INTO match_results VALUES ('HS1', 'clb_a', 3, 'general', 1)")
    conn.execute("INSERT INTO match_results VALUES ('HS2', NULL, 3, NULL, NULL)")
    conn.executemany(
        "INSERT INTO run_history (seed, run_at, rounds_run, n_matched, n_total, stb_redrawn) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        [(42, "2025-01-01", 3, 1, 2, 1), (43, "2025-01-02", 3, 1, 2, 0)],
    )
    conn.commit()
    conn.close()
    return duong


class TestDiTru:

    def test_di_tru_giu_nguyen_ket_qua_cu(self, db_luoc_do_cu):
        da_lam = loi.di_tru_schema(db_luoc_do_cu)
        assert "match_results.buoi" in da_lam
        assert "clubs.buoi" in da_lam

        conn = sqlite3.connect(db_luoc_do_cu)
        rows = conn.execute(
            "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref "
            "FROM match_results ORDER BY student_id"
        ).fetchall()
        conn.close()
        assert rows == [
            ("HS1", loi.BUOI_MAC_DINH, "clb_a", "general", 1),
            ("HS2", loi.BUOI_MAC_DINH, None, None, None),
        ]

    def test_di_tru_KHONG_DUNG_toi_nhat_ky_chay(self, db_luoc_do_cu):
        """`run_history` là dấu vết kiểm toán — đến chức năng xoá dữ liệu
        cũng không đụng tới nó. Di trú lại càng không."""
        conn = sqlite3.connect(db_luoc_do_cu)
        truoc = conn.execute(
            "SELECT run_id, seed, run_at, stb_redrawn FROM run_history ORDER BY run_id"
        ).fetchall()
        conn.close()

        loi.di_tru_schema(db_luoc_do_cu)

        conn = sqlite3.connect(db_luoc_do_cu)
        sau = conn.execute(
            "SELECT run_id, seed, run_at, stb_redrawn FROM run_history ORDER BY run_id"
        ).fetchall()
        conn.close()
        assert sau == truoc

    def test_di_tru_chay_lai_khong_lam_gi_them(self, db_luoc_do_cu):
        loi.di_tru_schema(db_luoc_do_cu)
        assert loi.di_tru_schema(db_luoc_do_cu) == []

    def test_csdl_cu_dung_duoc_ngay_sau_khi_di_tru(self, db_luoc_do_cu):
        """Không chỉ mở được mà phải CHẠY được — di trú xong là dùng tiếp."""
        api = PipelineAPI(db_luoc_do_cu)
        assert api.get_match_results()["ok"]
        assert api.get_thoi_khoa_bieu()["ok"]
        assert api.list_clubs_admin()["ok"]
        assert api.get_tai_theo_buoi()["ok"]


# ---------------------------------------------------------------------------
# 5 — NHẬP DỮ LIỆU CÓ BUỔI
# ---------------------------------------------------------------------------

class TestNhapDuLieu:

    def test_nhap_clb_co_cot_buoi(self, tmp_path):
        api = PipelineAPI(str(tmp_path / "app.db"))
        kq = api.import_clubs_csv(
            "club_id,name,capacity,buoi\nclb_a,CLB A,5,thu_3\nclb_b,CLB B,5,thu_5\n")
        assert kq["ok"] and kq["data"]["n_clubs_co_buoi"] == 2
        assert api.get_danh_sach_buoi()["data"]["ds_buoi"] == ["thu_3", "thu_5"]
        assert api.get_danh_sach_buoi()["data"]["nhieu_buoi"] is True

    def test_khong_khai_buoi_thi_KHONG_coi_la_nhieu_buoi(self, tmp_path):
        """Trường chưa dùng buổi thì giao diện phải trông y hệt bản cũ."""
        api = PipelineAPI(str(tmp_path / "app.db"))
        api.import_clubs_csv("club_id,name,capacity\nclb_a,CLB A,5\nclb_b,CLB B,5\n")
        assert api.get_danh_sach_buoi()["data"]["nhieu_buoi"] is False

    def test_tron_co_buoi_va_khong_buoi_thi_canh_bao(self, tmp_path):
        """Tình huống nguy hiểm nhất của bước nhập này: những CLB bỏ trống
        buổi bị gom hết vào một buổi, tức là bị coi là TRÙNG GIỜ với nhau,
        mà không có gì trên màn hình nói ra."""
        api = PipelineAPI(str(tmp_path / "app.db"))
        kq = api.import_clubs_csv(
            "club_id,name,capacity,buoi\nclb_a,CLB A,5,thu_3\nclb_b,CLB B,5,\n")
        ma = [w["code"] for w in kq["data"]["warnings"]]
        assert "clb_thieu_buoi" in ma

    def test_nhap_nguyen_vong_theo_tung_buoi(self, tmp_path):
        api = PipelineAPI(str(tmp_path / "app.db"))
        api.import_clubs_csv(
            "club_id,name,capacity,buoi\n"
            "clb_a,CLB A,5,thu_3\nclb_c,CLB C,5,thu_3\nclb_b,CLB B,5,thu_5\n")
        kq = api.import_preferences_csv(
            "student_id,name,thu_3_pref_1,thu_3_pref_2,thu_5_pref_1\n"
            "HS1,An,clb_a,clb_c,clb_b\n")
        assert kq["ok"] and kq["data"]["n_nguyen_vong_lech_buoi"] == 0

        _st, _cl, _sc, _ap, pr, _ = loi.load_from_sqlite(api.db_path)
        assert pr["HS1"] == ["clb_a", "clb_c", "clb_b"]

    def test_nguyen_vong_lech_buoi_bi_bao_va_bi_bo(self, tmp_path):
        """Ghi câu lạc bộ Thứ 5 vào cột Thứ 3 là lỗi gõ tay dễ xảy ra nhất.
        Im lặng nhận vào thì kết quả sai mà không ai biết vì sao."""
        api = PipelineAPI(str(tmp_path / "app.db"))
        api.import_clubs_csv(
            "club_id,name,capacity,buoi\nclb_a,CLB A,5,thu_3\nclb_b,CLB B,5,thu_5\n")
        kq = api.import_preferences_csv(
            "student_id,name,thu_3_pref_1,thu_5_pref_1\nHS1,An,clb_b,clb_a\n")
        assert kq["data"]["n_nguyen_vong_lech_buoi"] == 2
        ma = [w["code"] for w in kq["data"]["warnings"]]
        assert ma[0] == "nguyen_vong_lech_buoi"

        _st, _cl, _sc, _ap, pr, _ = loi.load_from_sqlite(api.db_path)
        assert pr.get("HS1", []) == []

    def test_tu_nhan_dien_duoc_bo_cot_theo_buoi(self, tmp_path):
        api = PipelineAPI(str(tmp_path / "app.db"))
        d = api.detect_csv_kind("student_id,thu_3_pref_1,thu_5_pref_1\nHS1,a,b\n")["data"]
        assert d["kind"] == "preferences" and d["confident"] is True

    def test_bo_cot_cu_van_nhan_dien_dung(self, tmp_path):
        """`pref_1` không được lẫn sang nhánh theo buổi."""
        api = PipelineAPI(str(tmp_path / "app.db"))
        d = api.detect_csv_kind("student_id,pref_1,pref_2\nHS1,a,b\n")["data"]
        assert (d["kind"], d["format"]) == ("preferences", "wide")

    def test_chuan_hoa_buoi_gom_cac_cach_viet_ve_mot(self, tmp_path):
        """"Thứ 3" và "thu 3" và "thu_3" phải ra cùng một buổi — không thì
        hai câu lạc bộ cùng giờ bị coi là hai buổi và học sinh trúng cả hai."""
        api = PipelineAPI(str(tmp_path / "app.db"))
        assert api.chuan_hoa_buoi("  Thu 3 ") == api.chuan_hoa_buoi("thu_3")
        assert api.chuan_hoa_buoi("") == ""


# ---------------------------------------------------------------------------
# 6 — MỘT THIẾT KẾ BỐC THĂM DUY NHẤT
# ---------------------------------------------------------------------------

def _chup_csdl(duong):
    """Ảnh chụp những thứ một hàm CHỈ ĐỌC không được phép làm đổi."""
    conn = sqlite3.connect(duong)
    try:
        return (
            conn.execute("SELECT COUNT(*) FROM match_results").fetchone()[0],
            conn.execute("SELECT COUNT(*) FROM run_history").fetchone()[0],
            conn.execute("SELECT is_locked, locked_at FROM stb_lock WHERE id=1").fetchone(),
            conn.execute(
                "SELECT student_id, stb_number FROM students ORDER BY student_id"
            ).fetchall(),
        )
    finally:
        conn.close()


class TestMotThietKeDuyNhat:
    """Phần mềm chạy DUY NHẤT `stb_ngay` — không còn bộ chọn, không còn
    đường nào từ api.py tới `stb_tuan` hay `stb_co_bu`.

    Căn cứ của quyết định là TN7 (`du_lieu_test/do_boc_tham.py`): `stb_ngay`
    không thua ở ô nào đã đo và hơn hẳn ở mọi vùng bốc thăm thật sự quyết
    định, còn `stb_co_bu` mở kênh khai gian có thật (113/300 em).

    Nhóm test này canh đúng một việc: không ai lặng lẽ mở lại lựa chọn đó.
    Thêm lại tham số `che_do_boc_tham` vào `run_pipeline` là test đầu tiên
    ĐỎ — đã thử thật, xem docstring đầu tệp.
    """

    def test_run_pipeline_khong_nhan_tham_so_che_do(self):
        """Chữ ký hàm là chỗ duy nhất chặn được việc mở lại lựa chọn.

        Kiểm hành vi thì không đủ: ai đó thêm tham số với mặc định
        'stb_ngay' sẽ qua được mọi test hành vi, trong khi giao diện hay
        một lời gọi khác đã có thể truyền 'stb_co_bu' vào.
        """
        from api import PipelineAPI

        ts = list(inspect.signature(PipelineAPI.run_pipeline).parameters)
        # Canh HAI dieu khac nhau:
        #   1. Khong tham so nao lien quan toi cach boc tham — day moi la
        #      dieu phai giu, va no dung du chu ky ham co doi vi ly do khac.
        #   2. Chu ky dung y nguyen danh sach duoi day — de mot tham so moi
        #      them vao lang le phai di qua mot lan sua test co chu y.
        assert not [t for t in ts if "che_do" in t or "boc_tham" in t], ts
        assert ts == ["self", "seed", "force_redraw_stb", "chi_buoi"], ts

    def test_khong_con_ham_so_sanh_boc_tham(self):
        """Bảng đối chiếu ba cách sinh ra để giúp CHỌN. Không còn gì để chọn
        thì nó chỉ làm người vận hành phân vân về một việc đã quyết."""
        from api import PipelineAPI

        assert not hasattr(PipelineAPI, "so_sanh_boc_tham")

    def test_chay_mac_dinh_thi_ghi_dung_stb_ngay(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            assert conn.execute(
                "SELECT che_do_boc_tham FROM run_meta WHERE id=1"
            ).fetchone()[0] == "stb_ngay"
        finally:
            conn.close()

    def test_ba_che_do_van_con_trong_thuat_toan_de_TN7_do_duoc(self):
        """Xoá `stb_tuan`/`stb_co_bu` khỏi thuật toán thì `do_boc_tham.py`
        không chạy được nữa, và mọi con số TN7 trong docs/NGHIEN_CUU_TOI_UU.md
        mất khả năng tái lập — chúng là DỤNG CỤ ĐO, không phải lựa chọn."""
        assert set(loi.CHE_DO_BOC_THAM) == {"stb_tuan", "stb_ngay", "stb_co_bu"}
        assert loi.CHE_DO_BOC_THAM_MAC_DINH == "stb_ngay"


# ---------------------------------------------------------------------------
# 7 — ĐƯỜNG CHẠY ĐẦY ĐỦ QUA API
# ---------------------------------------------------------------------------

class TestChayDayDu:

    def test_chay_va_xuat_thoi_khoa_bieu(self, api_nhieu_buoi, tmp_path):
        kq = api_nhieu_buoi.run_pipeline(seed=42)
        assert kq["ok"], kq["errors"]

        tkb = api_nhieu_buoi.get_thoi_khoa_bieu()["data"]
        assert len(tkb["ds_buoi"]) == 5
        assert tkb["hoc_sinh"], "thoi khoa bieu rong"
        for em in tkb["hoc_sinh"]:
            assert set(em["theo_buoi"]) == set(tkb["ds_buoi"])

        xuat = api_nhieu_buoi.export_csv()["data"]
        assert xuat["nhieu_buoi"] is True
        assert os.path.exists(xuat["thoi_khoa_bieu_path"])
        assert os.path.isdir(os.path.splitext(xuat["path"])[0] + "_theo_buoi")

    def test_ghi_lai_cach_boc_tham_da_dung(self, api_nhieu_buoi):
        """Không ghi lại thì sau này không truy được kết quả cũ chạy bằng
        cách nào — mà ba cách cho kết quả khác nhau.

        Cột này vẫn phải ghi dù phần mềm chỉ còn một cách: một cơ sở dữ liệu
        có thể chứa cả dòng cũ ghi 'stb_tuan' lẫn dòng mới ghi 'stb_ngay',
        và `get_so_boc_tham_theo_buoi` đọc chính cột này để dựng lại đúng
        thứ tự mà lần chạy đó đã dùng."""
        api_nhieu_buoi.run_pipeline(seed=42)
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            assert conn.execute(
                "SELECT che_do_boc_tham, so_buoi FROM run_meta WHERE id=1"
            ).fetchone() == ("stb_ngay", 5)
            assert conn.execute(
                "SELECT che_do_boc_tham FROM run_history ORDER BY run_id DESC LIMIT 1"
            ).fetchone()[0] == "stb_ngay"
        finally:
            conn.close()

    def test_do_phu_dem_dung_em_trang_tay(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        d = api_nhieu_buoi.get_do_phu()["data"]
        assert d["so_em_trang_tay"] == d["phan_bo"][0]["so_em"]
        assert sum(p["so_em"] for p in d["phan_bo"]) == d["tong_hoc_sinh"]
        assert len(d["phan_bo"]) == len(d["ds_buoi"]) + 1

    def test_tai_theo_buoi_tinh_choi_theo_SO_HOC_SINH(self, api_nhieu_buoi):
        """Mỗi em chỉ lấy được một chỗ trong một buổi, nên mẫu số của tỉ lệ
        chọi phải là số học sinh, không phải số lượt nguyện vọng."""
        for t in api_nhieu_buoi.get_tai_theo_buoi()["data"]:
            if t["tong_cho"]:
                assert t["ti_le_choi"] == round(t["so_hoc_sinh"] / t["tong_cho"], 2)


# ---------------------------------------------------------------------------
# 8 — SỐ BỐC THĂM THEO BUỔI: THỨ TRƯỜNG PHẢI GIẢI THÍCH ĐƯỢC
# ---------------------------------------------------------------------------

class TestSoBocThamTheoBuoi:
    """Phần mềm xáo lại thứ tự ở mỗi buổi, nên sẽ có phụ huynh hỏi *"vì sao
    con tôi thứ Ba đứng thứ 30 mà thứ Sáu đứng thứ 120?"*. Bảng này là câu
    trả lời, và nó phải ĐÚNG tới từng ô — một bảng gần đúng còn tệ hơn không
    có bảng, vì nó trông như bằng chứng."""

    def test_khop_tung_o_voi_lan_chay_that(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        d = api_nhieu_buoi.get_so_boc_tham_theo_buoi()["data"]

        st, cl, sc, ap, pr, stb = loi.load_from_sqlite(api_nhieu_buoi.db_path)
        kq = loi.run_rbda_nhieu_buoi(
            st, cl, sc, ap, pr, stb,
            loi.default_reserve_eligible_fn(st, cl), seed=42)

        assert d["da_chay"] is True
        assert d["hoc_sinh"], "bang rong"
        for em in d["hoc_sinh"]:
            for b in d["ds_buoi"]:
                assert em["so"][b] == kq.stb_theo_buoi[b][em["student_id"]]

    def test_moi_buoi_la_mot_hoan_vi_day_du(self, api_nhieu_buoi):
        """Thứ tự trong một buổi phải là hoán vị của CẢ DÀN. Thiếu hay trùng
        số nghĩa là có em không có chỗ đứng, hoặc hai em cùng một chỗ."""
        api_nhieu_buoi.run_pipeline(seed=42)
        d = api_nhieu_buoi.get_so_boc_tham_theo_buoi()["data"]
        n = d["tong_hoc_sinh"]
        for b in d["ds_buoi"]:
            assert sorted(em["so"][b] for em in d["hoc_sinh"]) == list(range(n))

    def test_tim_kiem_khong_doi_thu_hang(self, api_nhieu_buoi):
        """Lọc rồi mới xáo thì con số hiện ra là thứ hạng trong NHÓM ĐÃ LỌC —
        một con số không có thật, và trông y hệt thật."""
        api_nhieu_buoi.run_pipeline(seed=42)
        day_du = api_nhieu_buoi.get_so_boc_tham_theo_buoi()["data"]
        mot_em = day_du["hoc_sinh"][7]
        loc = api_nhieu_buoi.get_so_boc_tham_theo_buoi(
            search=mot_em["student_id"])["data"]
        assert len(loc["hoc_sinh"]) == 1
        assert loc["hoc_sinh"][0]["so"] == mot_em["so"]
        assert loc["tong_hoc_sinh"] == day_du["tong_hoc_sinh"]

    def test_lan_chay_cu_bang_cach_cu_thi_hien_dung_cach_cu(self, api_nhieu_buoi):
        """Cơ sở dữ liệu đã chạy bằng bản trước (ghi 'stb_tuan') mà hiển thị
        theo cách mới thì bảng khoe một thứ tự CHƯA TỪNG được dùng để xếp ai
        vào đâu."""
        api_nhieu_buoi.run_pipeline(seed=42)
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            conn.execute("UPDATE run_meta SET che_do_boc_tham='stb_tuan' WHERE id=1")
            conn.commit()
        finally:
            conn.close()

        d = api_nhieu_buoi.get_so_boc_tham_theo_buoi()["data"]
        assert d["cach_cu"] is True
        assert d["che_do"] == "stb_tuan"
        # Một bộ số cho cả tuần -> mọi cột của một em phải trùng nhau.
        for em in d["hoc_sinh"][:20]:
            assert len(set(em["so"].values())) == 1

    def test_chua_chay_lan_nao_thi_bang_rong(self, api_nhieu_buoi):
        d = api_nhieu_buoi.get_so_boc_tham_theo_buoi()["data"]
        assert d["da_chay"] is False
        assert d["hoc_sinh"] == []

    def test_chi_doc_khong_ghi_gi(self, api_nhieu_buoi):
        """Hàm này dựng lại thứ tự bằng cách TÍNH LẠI. Lỡ ghi xuống cơ sở dữ
        liệu thì nó vừa đổi kết quả đã công bố, vừa để lại dấu vết trông như
        một lần chạy thật — mà nó chỉ được gọi để xem."""
        api_nhieu_buoi.run_pipeline(seed=42)
        truoc = _chup_csdl(api_nhieu_buoi.db_path)
        assert api_nhieu_buoi.get_so_boc_tham_theo_buoi()["ok"]
        assert api_nhieu_buoi.get_so_boc_tham_theo_buoi(search="HS01")["ok"]
        assert _chup_csdl(api_nhieu_buoi.db_path) == truoc

    def test_xuat_them_tep_so_boc_tham(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        xuat = api_nhieu_buoi.export_csv()["data"]
        duong = xuat["so_boc_tham_path"]
        assert duong and os.path.exists(duong)
        assert xuat["n_so_boc_tham_rows"] == 160
        with open(duong, encoding="utf-8-sig") as f:
            dong = f.read().splitlines()
        assert dong[0].startswith("Mã học sinh,Họ tên,thu_2")
        assert len(dong) == 161                       # 1 dòng tiêu đề + 160 em

    def test_mot_buoi_thi_khong_xuat_tep_do(self, tmp_path):
        """Một buổi thì bảng này không nói thêm điều gì so với bộ số đã khoá."""
        from api import PipelineAPI

        api = PipelineAPI(str(tmp_path / "app.db"), thu_muc_xuat=str(tmp_path))
        for ten in ("VIDU_01_danh_sach_CLB.csv", "VIDU_02_chon_CLB_muon_thi.csv",
                    "VIDU_03_xep_hang_nguyen_vong.csv"):
            duong = os.path.join(GOC, "du_lieu_test", "vi_du_huong_dan", ten)
            with open(duong, encoding="utf-8-sig") as f:
                assert api.import_csv_auto(f.read())["ok"]
        api.run_pipeline(seed=42)
        xuat = api.export_csv()["data"]
        assert xuat["nhieu_buoi"] is False
        assert xuat["so_boc_tham_path"] is None


# ---------------------------------------------------------------------------
# 9 — CHẠY RIÊNG MỘT SỐ BUỔI
# ---------------------------------------------------------------------------

class TestThuTuNgayTrongTuan:
    """Nhãn buổi là chữ tự do, nhưng gần như trường nào cũng đặt theo ngày.

    Sắp theo vần chữ cái thì "Thứ Hai / Thứ Ba / Thứ Tư / Thứ Năm" ra Ba,
    Hai, Năm, Tư. Trên màn hình đã khó đọc; ở bộ chọn KHOẢNG buổi thì nó
    chọn ra một tập khác hẳn điều người dùng định nói.
    """

    @pytest.mark.parametrize("nhan,mong_doi", [
        ("thu_2", 2), ("thu 3", 3), ("Thứ Hai", 2), ("thứ_năm", 5),
        ("t6", 6), ("thu_3_tiet_9", 3), ("monday", 2), ("cn", 8),
    ])
    def test_nhan_ra_ngay_trong_tuan(self, nhan, mong_doi):
        assert loi.so_thu_trong_tuan(nhan) == mong_doi

    @pytest.mark.parametrize("nhan", [
        "buoi_1", "ngoai_khoa", "sang", "__mac_dinh__", "",
        # Hai nhãn dưới là lý do luật nhận diện phải siết: cho cắt đuôi ở
        # nhãn KHÔNG có tiền tố "thứ" thì "sau_gio" thành thứ Sáu và
        # "tu_chon" thành thứ Tư — nhận nhầm im lặng.
        "sau_gio", "tu_chon",
    ])
    def test_khong_doan_bua_nhan_la(self, nhan):
        assert loi.so_thu_trong_tuan(nhan) is None

    def test_sap_theo_ngay_chu_khong_theo_van(self):
        vietnam = ["Thứ Tư", "Thứ Hai", "Thứ Năm", "Thứ Ba"]
        assert loi.sap_buoi(vietnam) == ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm"]
        assert sorted(vietnam) != loi.sap_buoi(vietnam), (
            "neu hai cach sap trung nhau thi test nay khong canh duoc gi"
        )

    def test_nhan_khong_nhan_ra_xep_sau_va_theo_van(self):
        tron = ["ngoai_khoa", "thu_5", "abc", "thu_2"]
        assert loi.sap_buoi(tron) == ["thu_2", "thu_5", "abc", "ngoai_khoa"]


class TestChonBuoi:
    """Chạy riêng một buổi, hoặc một dải buổi trong tuần."""

    def test_chay_rieng_mot_buoi_giong_chay_ca_tuan(self, du_lieu_nhieu_buoi):
        """BẤT BIẾN QUAN TRỌNG NHẤT của cả tính năng.

        Kết quả thứ Năm không được phụ thuộc vào việc hôm đó người vận hành
        bấm chạy cả tuần hay chạy riêng thứ Năm. Hỏng điều này thì kết quả
        không tái lập được và không giải thích được với phụ huynh.

        Chỗ dễ hỏng: `sinh_stb_theo_buoi` ngắn mạch khi danh sách buổi chỉ
        có một phần tử. Truyền danh sách ĐÃ LỌC vào đó thì chạy riêng một
        buổi rơi vào nhánh ngắn mạch và dùng bộ số gốc thay vì hoán vị của
        buổi ấy. Đã thử phá đúng chỗ đó — xem docstring đầu tệp.
        """
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        ca_tuan = loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig, seed=42)
        assert len(ca_tuan.ds_buoi) == 5

        for buoi in ca_tuan.ds_buoi:
            rieng = loi.run_rbda_nhieu_buoi(
                st, cl, sc, ap, pr, stb, elig, seed=42, chi_buoi=[buoi])
            assert rieng.ds_buoi == [buoi]
            for sid in st:
                assert rieng.assignment[sid][buoi] == ca_tuan.assignment[sid][buoi], (
                    "buoi %s lech khi chay rieng" % buoi)

    def test_chay_mot_dai_giong_chay_ca_tuan(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        ca_tuan = loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig, seed=42)
        dai = loi.run_rbda_nhieu_buoi(
            st, cl, sc, ap, pr, stb, elig, seed=42,
            chi_buoi=["thu_2", "thu_3", "thu_4"])
        assert dai.ds_buoi == ["thu_2", "thu_3", "thu_4"]
        for sid in st:
            for b in dai.ds_buoi:
                assert dai.assignment[sid][b] == ca_tuan.assignment[sid][b]

    def test_thu_tu_chon_khong_doi_ket_qua(self, du_lieu_nhieu_buoi):
        """Truyền ['thu_4','thu_2'] phải giống ['thu_2','thu_4']."""
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        a = loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig, seed=42,
                                    chi_buoi=["thu_4", "thu_2"])
        b = loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig, seed=42,
                                    chi_buoi=["thu_2", "thu_4"])
        assert a.ds_buoi == b.ds_buoi == ["thu_2", "thu_4"]
        assert a.assignment == b.assignment

    def test_buoi_khong_ton_tai_thi_bao_loi(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        with pytest.raises(ValueError):
            loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig,
                                    chi_buoi=["thu_9"])

    def test_chon_rong_thi_bao_loi(self, du_lieu_nhieu_buoi):
        st, cl, sc, ap, pr, stb, elig = du_lieu_nhieu_buoi
        with pytest.raises(ValueError):
            loi.run_rbda_nhieu_buoi(st, cl, sc, ap, pr, stb, elig, chi_buoi=[])


class TestChonBuoiQuaAPI:
    """Đường chạy thật: giữ nguyên kết quả các buổi không chọn."""

    def _dem_theo_buoi(self, api):
        conn = sqlite3.connect(api.db_path)
        try:
            return dict(conn.execute(
                "SELECT buoi, COUNT(*) FROM match_results "
                "WHERE club_id IS NOT NULL GROUP BY buoi"))
        finally:
            conn.close()

    def _chup_o(self, api):
        conn = sqlite3.connect(api.db_path)
        try:
            return dict(conn.execute(
                "SELECT student_id || '|' || buoi, COALESCE(club_id, '') "
                "FROM match_results"))
        finally:
            conn.close()

    def test_giu_nguyen_ket_qua_buoi_khong_chon(self, api_nhieu_buoi):
        """Câu `DELETE FROM match_results` không điều kiện của bản trước sẽ
        xoá sạch kết quả các ngày đã công bố. Mất dữ liệu, im lặng, và chỉ
        lấy lại được từ bản sao lưu."""
        api_nhieu_buoi.run_pipeline(seed=42)
        truoc = self._chup_o(api_nhieu_buoi)
        assert len(self._dem_theo_buoi(api_nhieu_buoi)) == 5

        assert api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])["ok"]
        sau = self._chup_o(api_nhieu_buoi)

        assert set(truoc) == set(sau), "mat dong match_results cua buoi khac"
        assert len(self._dem_theo_buoi(api_nhieu_buoi)) == 5
        # Cùng seed, cùng dữ liệu -> thứ Năm cũng phải ra y hệt.
        assert truoc == sau

    def test_ghi_lai_buoi_da_chay(self, api_nhieu_buoi):
        """Kết quả trong cơ sở dữ liệu giờ có thể là hợp của nhiều lần chạy.
        Không ghi lại lần nào phủ buổi nào thì mất khả năng truy nguồn."""
        api_nhieu_buoi.run_pipeline(seed=42)
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_3", "thu_2"])
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            assert conn.execute(
                "SELECT buoi_da_chay FROM run_meta WHERE id=1"
            ).fetchone()[0] == "thu_2,thu_3"
            lich_su = [r[0] for r in conn.execute(
                "SELECT buoi_da_chay FROM run_history ORDER BY run_id")]
        finally:
            conn.close()
        assert lich_su == ["thu_2,thu_3,thu_4,thu_5,thu_6", "thu_2,thu_3"]

    def test_chon_het_bang_chay_ca_tuan(self, api_nhieu_buoi):
        """Tích hết các buổi thì phải giống hệt không tích gì — cùng một ý
        định, không được ra hai đường chạy khác nhau."""
        assert api_nhieu_buoi.run_pipeline(
            seed=42, chi_buoi=["thu_2", "thu_3", "thu_4", "thu_5", "thu_6"])["ok"]
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            assert conn.execute(
                "SELECT so_buoi FROM run_meta WHERE id=1").fetchone()[0] == 5
        finally:
            conn.close()

    def test_khong_cho_ve_lai_tham_khi_chay_mot_phan(self, api_nhieu_buoi):
        """Vẽ lại số bốc thăm là đổi thứ tự ưu tiên của MỌI buổi, kể cả
        những buổi đang giữ kết quả cũ — kết quả cũ đó lập tức không còn
        giải thích được bằng bộ số mới. Phải chặn bằng LỖI, không phải
        bằng cảnh báo: đây là thứ không sửa lại được sau khi đã chạy."""
        api_nhieu_buoi.run_pipeline(seed=42)
        kq = api_nhieu_buoi.run_pipeline(
            seed=42, chi_buoi=["thu_5"], force_redraw_stb=True)
        assert not kq["ok"]
        assert kq["errors"][0]["code"] == "khong_ve_lai_tham_khi_chay_mot_phan"

    def test_ve_lai_tham_van_duoc_khi_chon_het(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        assert api_nhieu_buoi.run_pipeline(
            seed=42, force_redraw_stb=True,
            chi_buoi=["thu_2", "thu_3", "thu_4", "thu_5", "thu_6"])["ok"]

    def test_buoi_la_va_chon_rong_bi_tu_choi(self, api_nhieu_buoi):
        for chi_buoi, ma in ((["thu_9"], "buoi_khong_ton_tai"),
                             ([], "chua_chon_buoi_nao")):
            kq = api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=chi_buoi)
            assert not kq["ok"]
            assert kq["errors"][0]["code"] == ma

    def test_cau_bao_loi_liet_ke_buoi_theo_thu_tu_ngay(self, api_nhieu_buoi):
        """Chuỗi "các buổi đang có" là chữ NGƯỜI ĐỌC, nên phải theo thứ tự
        ngày.

        Trên `thu_2`..`thu_6` thì vần trùng ngày, nên phải thêm nhãn mà hai
        cách sắp cho ra KHÁC nhau: `chu_nhat` đứng ĐẦU nếu sắp theo vần, đứng
        CUỐI nếu sắp theo ngày."""
        api_nhieu_buoi.create_or_update_club(
            "clb_t7", "CLB thứ Bảy", 10, 0, "", buoi="thu_bay")  # luu thanh thu_7
        api_nhieu_buoi.create_or_update_club(
            "clb_cn", "CLB Chủ nhật", 10, 0, "", buoi="chu_nhat")

        kq = api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_9"])
        assert not kq["ok"]
        assert kq["errors"][0]["params"]["dang_co"] == (
            "thu_2, thu_3, thu_4, thu_5, thu_6, thu_7, chu_nhat")

    def test_nhan_buoi_duoc_chuan_hoa(self, api_nhieu_buoi):
        """Giao diện gửi đúng nhãn trong cơ sở dữ liệu, nhưng lời gọi từ
        chỗ khác có thể gõ hoa/thường hay thừa khoảng trắng."""
        api_nhieu_buoi.run_pipeline(seed=42)
        assert api_nhieu_buoi.run_pipeline(
            seed=42, chi_buoi=["Thu_2", " thu 3 "])["ok"]
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            assert conn.execute(
                "SELECT buoi_da_chay FROM run_meta WHERE id=1"
            ).fetchone()[0] == "thu_2,thu_3"
        finally:
            conn.close()

    def test_da_xep_dem_tren_CA_CSDL_khong_chi_lan_chay_nay(self, api_nhieu_buoi):
        """Chạy riêng thứ Năm không được làm con số "đã xếp CLB" trên bảng
        điều khiển tụt xuống còn số em có CLB thứ Năm."""
        api_nhieu_buoi.run_pipeline(seed=42)
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            ca_tuan = conn.execute(
                "SELECT n_matched FROM run_meta WHERE id=1").fetchone()[0]
        finally:
            conn.close()

        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            mot_buoi = conn.execute(
                "SELECT n_matched FROM run_meta WHERE id=1").fetchone()[0]
        finally:
            conn.close()
        assert mot_buoi == ca_tuan

    def test_danh_sach_buoi_sap_theo_ngay_va_kem_so_thu(self, api_nhieu_buoi):
        d = api_nhieu_buoi.get_danh_sach_buoi()["data"]
        assert d["ds_buoi"] == ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6"]
        assert d["thu_trong_tuan"] == {
            "thu_2": 2, "thu_3": 3, "thu_4": 4, "thu_5": 5, "thu_6": 6}


class TestXuatTepSauKhiChayMotPhan:
    """Bước 6 phải xuất từ CƠ SỞ DỮ LIỆU, không từ kết quả trong bộ nhớ.

    `export_match_results(result, ...)` đi qua `cac_dong_match_results(result)`
    — đúng cái generator dựng câu `INSERT` CÓ PHẠM VI ở bước 5. Nên chạy riêng
    thứ Năm thì tệp bị ghi đè còn đúng một buổi, trong khi nhật ký bước 6 vẫn
    báo `done` kèm đường dẫn. Cơ sở dữ liệu đủ; chỉ tệp mất các ngày trường đã
    in ra dán bảng.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: trả bước 6 về
    `export_match_results(result, export_path)` → ba trong bốn test dưới đây
    đỏ. Đo trên bộ `bo_nhieu_buoi`: chạy cả tuần ra **800 dòng**, chạy riêng
    thứ Năm ngay sau đó ghi đè tệp còn **160 dòng** — mất 4 trên 5 ngày, mà
    bước 6 vẫn báo `done`. Khôi phục → xanh lại.
    """

    def _duong_tep(self, api):
        return os.path.join(os.path.dirname(api.db_path), "match_results.csv")

    def _doc(self, api):
        with open(self._duong_tep(api), encoding="utf-8") as f:
            return f.read()

    def test_chay_mot_phan_khong_cat_cac_buoi_khac(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        ca_tuan = self._doc(api_nhieu_buoi)

        assert api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])["ok"]
        sau = self._doc(api_nhieu_buoi)

        # Cung du lieu, cung hat giong, chay mot phan khong doi ket qua buoi
        # nao — nen tep phai TRUNG KHIT ban chay ca tuan.
        assert sau == ca_tuan

    def test_moi_buoi_deu_con_trong_tep(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])

        buoi_trong_tep = {
            d.split(",")[1] for d in self._doc(api_nhieu_buoi).splitlines()[1:]
        }
        assert buoi_trong_tep == {"thu_2", "thu_3", "thu_4", "thu_5", "thu_6"}

    def test_tep_khop_tung_o_voi_bang_match_results(self, api_nhieu_buoi):
        """Tệp là bản sao của bảng, không phải một cách đọc khác."""
        api_nhieu_buoi.run_pipeline(seed=42)
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_3", "thu_4"])

        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            trong_bang = sorted(
                (r[0], r[1], r[2] or "")
                for r in conn.execute(
                    "SELECT student_id, buoi, club_id FROM match_results")
            )
        finally:
            conn.close()

        doc = csv.reader(io.StringIO(self._doc(api_nhieu_buoi)))
        next(doc)
        trong_tep = sorted((d[0], d[1], d[2]) for d in doc)
        assert trong_tep == trong_bang

    def test_chay_ca_tuan_van_ra_dung_tep_nhu_cu(self, api_nhieu_buoi):
        """Đường cũ (`export_match_results`) và đường mới phải cho CÙNG tệp khi
        chạy cả tuần — nếu lệch thì bản vá đã đổi nhiều hơn phần cần đổi."""
        api_nhieu_buoi.run_pipeline(seed=42)
        moi = self._doc(api_nhieu_buoi)

        st, cl, sc, ap, pr, _ = loi.load_from_sqlite(api_nhieu_buoi.db_path)
        stb = {sid: info["stb"] for sid, info in st.items()}
        kq = loi.run_rbda_nhieu_buoi(
            st, cl, sc, ap, pr, stb,
            loi.default_reserve_eligible_fn(st, cl), seed=42)
        duong_cu = os.path.join(
            os.path.dirname(api_nhieu_buoi.db_path), "cach_cu.csv")
        loi.export_match_results(kq, duong_cu)
        with open(duong_cu, encoding="utf-8") as f:
            assert f.read() == moi


# ---------------------------------------------------------------------------
# 12 — LỖI DO CHÍNH TÍNH NĂNG CHỌN BUỔI SINH RA
# ---------------------------------------------------------------------------

class TestDongMoCoi:
    """Buổi biến mất khỏi danh sách CLB thì kết quả cũ của nó phải biến mất theo.

    Lệnh xoá có phạm vi chỉ xoá những buổi ĐANG chạy, mà danh sách đó suy từ
    bảng CLB hiện tại. Trường dời lịch — chuyển mọi CLB thứ Sáu sang thứ Năm —
    thì không buổi nào còn tên `thu_6`, nên không lệnh xoá nào chạm tới dòng
    cũ của nó.

    Đo được trên bộ 6 buổi trước khi sửa: **180 dòng `thu_6` sống sót** qua một
    lần chạy LẠI CẢ TUẦN. Tệ hơn dữ liệu rác, vì `get_club_fill_stats` nối
    theo `club_id` không kèm điều kiện buổi nên cộng dồn cả hai: bảng lấp đầy
    báo `clb_bongro` **40/20 chỗ**, `clb_lamvuon` **36/18**. Bản xoá vô điều
    kiện cũ KHÔNG thể gây ra chuyện này.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ lệnh quét dòng mồ côi trong `api.py` →
    cả hai test dưới đây ĐỎ.
    """

    def _doi_buoi(self, api, tu, den):
        conn = sqlite3.connect(api.db_path)
        try:
            conn.execute("UPDATE clubs SET buoi=? WHERE buoi=?", (den, tu))
            conn.commit()
        finally:
            conn.close()

    def _dem_dong(self, api, buoi):
        conn = sqlite3.connect(api.db_path)
        try:
            return conn.execute(
                "SELECT COUNT(*) FROM match_results WHERE buoi=?", (buoi,)
            ).fetchone()[0]
        finally:
            conn.close()

    def test_doi_buoi_roi_chay_ca_tuan_khong_con_dong_cua_buoi_cu(
            self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        assert self._dem_dong(api_nhieu_buoi, "thu_6") > 0, "bộ mẫu phải có thứ Sáu"

        self._doi_buoi(api_nhieu_buoi, "thu_6", "thu_5")
        api_nhieu_buoi.run_pipeline(seed=42)

        assert self._dem_dong(api_nhieu_buoi, "thu_6") == 0
        assert "thu_6" not in api_nhieu_buoi.get_danh_sach_buoi()["data"]["ds_buoi"]

    def test_khong_clb_nao_hien_qua_suc_chua_sau_khi_doi_buoi(
            self, api_nhieu_buoi):
        """Đây là thứ NGƯỜI DÙNG nhìn thấy — dòng mồ côi tự nó vô hình."""
        api_nhieu_buoi.run_pipeline(seed=42)
        self._doi_buoi(api_nhieu_buoi, "thu_6", "thu_5")
        api_nhieu_buoi.run_pipeline(seed=42)

        qua = [r for r in api_nhieu_buoi.get_club_fill_stats()["data"]
               if r["matched"] > r["capacity"]]
        assert qua == [], "CLB hiện quá sức chứa: %r" % qua

    def test_chay_mot_phan_cung_quet_dong_mo_coi(self, api_nhieu_buoi):
        """Buổi đã biến mất không phải "buổi không chọn".

        Lời hứa giữ nguyên các buổi khác chỉ áp cho buổi CÒN TỒN TẠI. Một
        buổi không CLB nào sinh hoạt nữa thì không kết quả nào được phép ở
        lại đó, dù lần chạy này chỉ đụng một buổi khác.
        """
        api_nhieu_buoi.run_pipeline(seed=42)
        self._doi_buoi(api_nhieu_buoi, "thu_6", "thu_5")
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_2"])
        assert self._dem_dong(api_nhieu_buoi, "thu_6") == 0

    def test_n_total_la_tong_so_hoc_sinh_khong_phai_so_em_cua_lan_chay(
            self, api_nhieu_buoi):
        """Canh đúng mệnh đề một bản soát mã đã đọc nhầm.

        Có nhận xét cho rằng `n_matched` đếm trên cả cơ sở dữ liệu còn
        `n_total` đếm theo lần chạy, nên hai số không còn nói về cùng một tập
        người. Không đúng: `n_total = len(result.assignment)`, mà
        `run_rbda_nhieu_buoi` khởi tạo `assignment` cho MỌI học sinh. Test này
        ghim mệnh đề đó lại để lần sau không ai "sửa" một thứ không hỏng.
        """
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            n_matched, n_total = conn.execute(
                "SELECT n_matched, n_total FROM run_meta WHERE id=1").fetchone()
            tong_em = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        finally:
            conn.close()
        assert n_total == tong_em
        assert n_matched <= n_total


class TestChenThamKhiChayMotPhan:
    """Thêm học sinh mới giữa chừng không được đánh lại số bốc thăm của mọi buổi.

    `force_redraw_stb` đã bị chặn khi chạy một phần, đúng vì lý do này. Nhánh
    cấp số cho học sinh mới ngay bên cạnh thì không, và nó gây đúng thiệt hại
    ấy: chỉ số tuyệt đối của số bốc thăm chính là đầu vào của
    `sinh_stb_theo_buoi`, nên đánh lại số là đổi thứ tự của MỌI buổi — kể cả
    buổi vừa hứa giữ nguyên.

    Đo được trên bộ 6 buổi trước khi sửa: thêm MỘT em rồi chạy riêng thứ Năm
    → **17 trên 180 số đổi**, và **27 trên 900 ô giữ lại không còn tái lập
    được** từ bộ số đã khoá cộng hạt giống. Đó là lúc lời hứa "ai cũng tính
    lại được" gãy, và bảng Số bốc thăm theo buổi bắt đầu hiện những con số
    chưa từng dùng để xếp ai vào đâu.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ điều kiện `chi_buoi_chuan is not None`
    ở nhánh chèn số trong `api.py` → hai test đầu ĐỎ.
    """

    def _them_em_moi(self, api, sid="HS999"):
        conn = sqlite3.connect(api.db_path)
        try:
            conn.execute(
                "INSERT INTO students (student_id, name, reserve_group) "
                "VALUES (?, ?, ?)", (sid, "Em Mới", ""))
            conn.commit()
        finally:
            conn.close()

    def _anh_stb(self, api):
        conn = sqlite3.connect(api.db_path)
        try:
            return dict(conn.execute("SELECT student_id, stb_number FROM students"))
        finally:
            conn.close()

    def test_chay_mot_phan_voi_em_chua_co_tham_bi_tu_choi(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        self._them_em_moi(api_nhieu_buoi)

        kq = api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])
        assert not kq["ok"]
        ds = kq["errors"]
        assert any(e["code"] == "khong_chen_tham_khi_chay_mot_phan" for e in ds), ds

    def test_bi_tu_choi_thi_khong_mot_so_nao_bi_danh_lai(self, api_nhieu_buoi):
        """Từ chối phải là từ chối SẠCH — không để lại nửa vời."""
        api_nhieu_buoi.run_pipeline(seed=42)
        truoc = self._anh_stb(api_nhieu_buoi)
        self._them_em_moi(api_nhieu_buoi)

        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])

        sau = self._anh_stb(api_nhieu_buoi)
        doi = [s for s in truoc if truoc[s] != sau.get(s)]
        assert doi == [], "%d số bốc thăm bị đánh lại dù lần chạy đã bị từ chối" % len(doi)

    def test_chay_ca_tuan_voi_em_moi_van_duoc_nhan(self, api_nhieu_buoi):
        """Chặn phải là chặn ĐÚNG CHỖ, không chặn luôn đường hợp lệ."""
        api_nhieu_buoi.run_pipeline(seed=42)
        self._them_em_moi(api_nhieu_buoi)

        assert api_nhieu_buoi.run_pipeline(seed=42)["ok"]
        assert self._anh_stb(api_nhieu_buoi)["HS999"] is not None


class TestCauLacBoDoiBuoi:
    """Câu lạc bộ dời sang buổi khác thì dòng cũ của nó phải biến mất theo.

    Câu quét mồ côi đầu tiên bắt theo TÊN BUỔI, nên nó chỉ dọn được khi một
    buổi biến mất HẲN. Trường dời lịch cho ĐÚNG MỘT câu lạc bộ — chuyển nó từ
    thứ Sáu sang thứ Ba trong khi các câu lạc bộ khác vẫn ở thứ Sáu — thì tên
    `thu_6` còn nguyên và dòng cũ không ai chạm tới.

    Chạy CẢ TUẦN thì lệnh xoá có phạm vi dọn được. Chạy MỘT PHẦN không gồm
    thứ Sáu thì không. Đo được trên bộ `bo_sau_buoi` trước khi sửa: dời
    `clb_tinhnguyen` (22 em) sang thứ Ba rồi chạy riêng thứ Ba → **22 dòng
    thứ Sáu sống sót**, câu lạc bộ đó có **44 dòng cho 22 chỗ**, và bảng lấp
    đầy báo **44/22** vì `get_club_fill_stats` nối theo `club_id` không kèm
    điều kiện buổi.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ câu quét theo cặp trong `api.py` → hai
    test đầu ĐỎ (22 dòng sót, bảng lấp đầy 44/22).
    """

    def _doi_buoi(self, api, club_id, buoi_moi):
        conn = sqlite3.connect(api.db_path)
        conn.row_factory = sqlite3.Row
        try:
            r = conn.execute(
                "SELECT * FROM clubs WHERE club_id = ?", (club_id,)).fetchone()
        finally:
            conn.close()
        assert api.create_or_update_club(
            club_id, r["name"], r["capacity"], r["reserve_capacity"],
            r["reserve_group"] or "", buoi=buoi_moi)["ok"]

    def _mot_clb_cua(self, api, buoi):
        """Câu lạc bộ đông nhất của buổi đó, và buổi đó phải còn CLB khác."""
        conn = sqlite3.connect(api.db_path)
        try:
            dem = dict(conn.execute(
                "SELECT club_id, COUNT(*) FROM match_results "
                "WHERE buoi = ? AND club_id IS NOT NULL GROUP BY club_id",
                (buoi,)))
        finally:
            conn.close()
        assert len(dem) >= 2, "buoi nay chi co mot CLB — khong thu duoc"
        return max(dem, key=dem.get)

    def _dong_cua(self, api, club_id, buoi=None):
        conn = sqlite3.connect(api.db_path)
        try:
            if buoi is None:
                return conn.execute(
                    "SELECT COUNT(*) FROM match_results WHERE club_id = ?",
                    (club_id,)).fetchone()[0]
            return conn.execute(
                "SELECT COUNT(*) FROM match_results WHERE club_id = ? AND buoi = ?",
                (club_id, buoi)).fetchone()[0]
        finally:
            conn.close()

    def test_chay_mot_phan_khong_de_lai_dong_cua_buoi_cu(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        cid = self._mot_clb_cua(api_nhieu_buoi, "thu_6")
        assert self._dong_cua(api_nhieu_buoi, cid, "thu_6") > 0

        self._doi_buoi(api_nhieu_buoi, cid, "thu_3")
        assert api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_3"])["ok"]

        assert self._dong_cua(api_nhieu_buoi, cid, "thu_6") == 0, (
            "con dong cua buoi cu, trong khi CLB da doi sang buoi khac")

    def test_bang_lap_day_khong_vuot_suc_chua(self, api_nhieu_buoi):
        """Hệ quả người dùng NHÌN THẤY, không phải chuyện bảng nào có dòng nào."""
        api_nhieu_buoi.run_pipeline(seed=42)
        cid = self._mot_clb_cua(api_nhieu_buoi, "thu_6")
        self._doi_buoi(api_nhieu_buoi, cid, "thu_3")
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_3"])

        for c in api_nhieu_buoi.get_club_fill_stats()["data"]:
            assert c["matched"] <= c["capacity"], (
                "%s bao %s/%s cho" % (c["club_id"], c["matched"], c["capacity"]))

    def test_buoi_khong_chon_van_giu_nguyen_tung_o(self, api_nhieu_buoi):
        """Bản vá không được lấn sang lời hứa chính của tính năng.

        Câu lạc bộ KHÔNG dời thì dòng của nó ở buổi không chọn phải còn
        nguyên vẹn — kể cả dòng `club_id IS NULL` của em không được suất nào
        buổi đó, vì một câu lạc bộ dời đi nơi khác không làm câu ấy sai.
        """
        api_nhieu_buoi.run_pipeline(seed=42)
        cid = self._mot_clb_cua(api_nhieu_buoi, "thu_6")

        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            truoc = sorted(conn.execute(
                "SELECT student_id, buoi, COALESCE(club_id,'') "
                "FROM match_results WHERE buoi = 'thu_6' AND "
                "COALESCE(club_id,'') != ?", (cid,)))
        finally:
            conn.close()
        assert truoc, "khong co dong nao de canh"

        self._doi_buoi(api_nhieu_buoi, cid, "thu_3")
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_3"])

        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            sau = sorted(conn.execute(
                "SELECT student_id, buoi, COALESCE(club_id,'') "
                "FROM match_results WHERE buoi = 'thu_6' AND "
                "COALESCE(club_id,'') != ?", (cid,)))
        finally:
            conn.close()
        assert sau == truoc

    def test_chay_ca_tuan_sau_khi_doi_buoi_van_dung(self, api_nhieu_buoi):
        """Không hồi quy: chạy cả tuần vẫn ra đúng một dòng mỗi em mỗi buổi."""
        api_nhieu_buoi.run_pipeline(seed=42)
        cid = self._mot_clb_cua(api_nhieu_buoi, "thu_6")
        self._doi_buoi(api_nhieu_buoi, cid, "thu_3")
        assert api_nhieu_buoi.run_pipeline(seed=42)["ok"]

        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            trung = conn.execute(
                "SELECT student_id, buoi, COUNT(*) FROM match_results "
                "GROUP BY student_id, buoi HAVING COUNT(*) > 1").fetchall()
            o_buoi_cu = conn.execute(
                "SELECT COUNT(*) FROM match_results WHERE club_id = ? "
                "AND buoi = 'thu_6'", (cid,)).fetchone()[0]
        finally:
            conn.close()
        assert trung == []
        assert o_buoi_cu == 0


class TestHatGiongKhiChayMotPhan:
    """Đổi hạt giống cũng là đổi thứ tự ưu tiên của mọi buổi.

    Ô hạt giống trên màn hình sửa tự do, và hạt giống chính là thứ dẫn xuất
    hoán vị riêng cho từng buổi (`sinh_stb_theo_buoi` với 'stb_ngay'). Chạy
    riêng thứ Năm bằng một hạt giống khác thì các buổi VỪA ĐƯỢC HỨA GIỮ
    NGUYÊN vẫn giữ dòng kết quả cũ, trong khi `run_meta.seed` đã bị ghi đè —
    mà `get_so_boc_tham_theo_buoi` dựng lại thứ tự từng buổi TỪ CHÍNH CỘT ĐÓ.

    Đo được trước khi sửa trên bộ `bo_nhieu_buoi`: chạy cả tuần hạt giống 42,
    rồi chạy riêng thứ Năm hạt giống 7 → **640 ô** kết quả của bốn buổi kia
    được giữ nguyên, trong khi **638 trên 640** số bốc thăm của chính bốn
    buổi đó đổi giá trị, và `run_meta.seed` thành 7. Bảng Số bốc thăm theo
    buổi từ đó giải thích kết quả cũ bằng một thứ tự chưa bao giờ được dùng
    để xếp ai vào đâu. Đúng cái hỏng mà hai khối chặn bên cạnh sinh ra để
    tránh, chỉ khác đường vào.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ điều kiện `seed_cu != seed` trong
    `api.run_pipeline` → hai test đầu ĐỎ. Bỏ điều kiện `con_giu` thay vào đó
    → `test_chua_giu_buoi_nao_thi_hat_giong_nao_cung_duoc` ĐỎ.
    """

    def _ma_loi(self, kq):
        ds = kq["errors"]
        return [e["code"] for e in ds if isinstance(e, dict)]

    def test_doi_hat_giong_khi_chay_mot_phan_bi_tu_choi(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)

        kq = api_nhieu_buoi.run_pipeline(seed=7, chi_buoi=["thu_5"])
        assert not kq["ok"]
        assert "khong_doi_hat_giong_khi_chay_mot_phan" in self._ma_loi(kq)

    def test_bi_tu_choi_thi_khong_o_nao_va_khong_dong_nhat_ky_nao_doi(
        self, api_nhieu_buoi
    ):
        """Từ chối phải SẠCH: không kết quả, không `run_meta`, không nhật ký."""
        api_nhieu_buoi.run_pipeline(seed=42)
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            truoc = sorted(conn.execute(
                "SELECT student_id, buoi, COALESCE(club_id,'') FROM match_results"))
            meta_truoc = conn.execute(
                "SELECT seed, buoi_da_chay FROM run_meta WHERE id=1").fetchone()
            lich_su_truoc = conn.execute(
                "SELECT COUNT(*) FROM run_history").fetchone()[0]
        finally:
            conn.close()

        api_nhieu_buoi.run_pipeline(seed=7, chi_buoi=["thu_5"])

        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            assert sorted(conn.execute(
                "SELECT student_id, buoi, COALESCE(club_id,'') "
                "FROM match_results")) == truoc
            assert conn.execute(
                "SELECT seed, buoi_da_chay FROM run_meta WHERE id=1"
            ).fetchone() == meta_truoc
            assert conn.execute(
                "SELECT COUNT(*) FROM run_history").fetchone()[0] == lich_su_truoc
        finally:
            conn.close()

    def test_cung_hat_giong_thi_chay_mot_phan_van_duoc(self, api_nhieu_buoi):
        """Chặn phải chặn ĐÚNG CHỖ, không chặn luôn đường hợp lệ."""
        api_nhieu_buoi.run_pipeline(seed=42)
        assert api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])["ok"]

    def test_chua_giu_buoi_nao_thi_hat_giong_nao_cung_duoc(self, api_nhieu_buoi):
        """Chưa có kết quả nào bị bỏ lại thì không có gì để mâu thuẫn.

        Chặn ở đây là cấm một việc không hỏng gì — điều kiện phải là CÓ BUỔI
        ĐANG ĐƯỢC GIỮ, không phải "đã từng chạy".
        """
        # Chua chay lan nao: khong dong nao bi bo lai.
        assert api_nhieu_buoi.run_pipeline(seed=7, chi_buoi=["thu_5"])["ok"]

        # Da chay, roi ket qua bi xoa sach: `run_meta.seed` van con 7, nhung
        # khong con o nao de mau thuan voi no — chan CUA CHAY MOT PHAN
        # khong duoc no ra.
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            conn.execute("DELETE FROM match_results")
            conn.commit()
        finally:
            conn.close()
        kq = api_nhieu_buoi.run_pipeline(seed=11, chi_buoi=["thu_3"])
        assert "khong_doi_hat_giong_khi_chay_mot_phan" not in self._ma_loi(kq)
        # Nhung bo so boc tham VAN KHOA cung hat giong 7, nen doi hat giong
        # van bi chan — boi luat khoa, khong phai boi luat chay mot phan
        # (tests/test_khoa_hat_giong.py).
        assert "hat_giong_da_khoa" in self._ma_loi(kq)

        # Mo khoa (dieu `reset_data` lam) thi khong con gi rang buoc: hat
        # giong nao cung dung duoc.
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            conn.execute("UPDATE stb_lock SET is_locked = 0")
            conn.commit()
        finally:
            conn.close()
        assert api_nhieu_buoi.run_pipeline(seed=11, chi_buoi=["thu_3"])["ok"]

    def test_chon_het_thi_doi_hat_giong_van_duoc(self, api_nhieu_buoi):
        """Chọn hết = chạy cả tuần: không buổi nào bị bỏ lại, nên chặn CỦA
        CHẠY MỘT PHẦN không nổ ra, và vẽ lại được như chạy cả tuần.

        Đổi hạt giống mà KHÔNG vẽ lại thì vẫn bị chặn — bởi luật khoá hạt
        giống cùng bộ số (tests/test_khoa_hat_giong.py), không phải bởi luật
        chạy một phần. Trước luật khoá, lời gọi thứ hai ở đây chạy được và
        lặng lẽ đổi thứ tự ưu tiên của mọi buổi đã công bố.
        """
        tat_ca = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6"]
        api_nhieu_buoi.run_pipeline(seed=42)
        kq = api_nhieu_buoi.run_pipeline(seed=7, chi_buoi=tat_ca)
        assert "khong_doi_hat_giong_khi_chay_mot_phan" not in self._ma_loi(kq)
        assert "hat_giong_da_khoa" in self._ma_loi(kq)
        assert api_nhieu_buoi.run_pipeline(
            seed=7, force_redraw_stb=True, chi_buoi=tat_ca)["ok"]


class TestDongKetNoiKhiTuChoi:
    """Đường `return` giữa chừng không được bỏ lại kết nối đang mở.

    `run_pipeline` mở kết nối ghi ở bước 3 rồi vẫn còn `return _fail(...)` ở
    giữa — chỗ từ chối chèn số bốc thăm khi chạy một phần. `except` chỉ chạy
    khi có exception, nên trước khi có khối `finally` thì đường đó rơi ra
    ngoài với kết nối CÒN MỞ. Trên Windows đó là một thẻ giữ `app.db`.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ khối `finally` trong `api.run_pipeline`
    → test này ĐỎ (1 kết nối còn sống).
    """

    def test_tu_choi_chen_tham_van_dong_ket_noi(self, api_nhieu_buoi, monkeypatch):
        """Đếm bằng LỚP CON của `sqlite3.Connection`, không gán đè `conn.close`.

        `close` của đối tượng C là thuộc tính chỉ đọc — gán đè nó ném
        AttributeError, mà `run_pipeline` bắt mọi lỗi và trả `ok=False`, nên
        test vẫn "đỏ đúng chỗ" vì một lý do hoàn toàn khác. Lớp con thì
        `close()` thật sự đi qua.
        """
        import api as mod_api

        dang_mo = []

        class KetNoiDem(sqlite3.Connection):
            def close(self):
                if self in dang_mo:
                    dang_mo.remove(self)
                super().close()

        def connect_db_dem(duong):
            conn = sqlite3.connect(duong, timeout=30, factory=KetNoiDem)
            conn.execute("PRAGMA busy_timeout = 30000")
            conn.execute("PRAGMA synchronous = FULL")
            dang_mo.append(conn)
            return conn

        api_nhieu_buoi.run_pipeline(seed=42)
        conn = sqlite3.connect(api_nhieu_buoi.db_path)
        try:
            conn.execute(
                "INSERT INTO students (student_id, name, reserve_group) "
                "VALUES ('HS999', 'Em Mới', '')")
            conn.commit()
        finally:
            conn.close()

        monkeypatch.setattr(mod_api, "connect_db", connect_db_dem)
        kq = api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_5"])

        assert not kq["ok"]
        assert dang_mo == [], "%d ket noi con mo sau khi lan chay bi tu choi" % len(dang_mo)


class TestNhanBuoiBangSo:
    """Trường đánh số buổi "1".."5" thay vì đặt tên theo ngày.

    Bảng tra thứ nhận "2".."7" là thứ Ba..thứ Bảy nhưng KHÔNG nhận "1", "8",
    "9". Nên nhãn "1" rơi xuống nhóm không-nhận-ra và đứng cuối:

        sap_buoi(['1','2','3','4','5'])  ->  ['2','3','4','5','1']

    Cách sắp theo vần CŨ lại đúng ở đây — tức lần sửa thứ tự ngày đã làm hỏng
    một trường hợp nó vốn đang làm đúng. Chọn dải "từ 1 đến 3" cắt ra các buổi
    3, 4, 5, 1: đúng loại chọn nhầm âm thầm mà chính lần sửa đó sinh ra để
    ngăn.

    ĐỐI CHỨNG NGƯỢC đã chạy thật: bỏ tầng số trong `khoa_sap_buoi` (cho nhãn
    toàn chữ số rơi về tầng vần chữ cái) → hai test đầu ĐỎ.
    """

    def test_nhan_toan_so_sap_theo_gia_tri_so(self):
        assert loi.sap_buoi(["1", "2", "3", "4", "5"]) == ["1", "2", "3", "4", "5"]

    def test_so_hai_chu_so_khong_dung_truoc_so_mot_chu_so(self):
        """Sắp theo vần thì "10" đứng trước "2" — sai theo kiểu thứ hai."""
        assert loi.sap_buoi(["1", "2", "10"]) == ["1", "2", "10"]

    def test_nhan_toan_so_khong_bi_doc_thanh_thu_trong_tuan(self):
        assert loi.so_thu_trong_tuan("2") is None
        assert loi.so_thu_trong_tuan("7") is None
        # Có tiền tố thì vẫn là thứ — đây mới là cách trường viết ngày.
        assert loi.so_thu_trong_tuan("thu_2") == 2
        assert loi.so_thu_trong_tuan("t7") == 7

    def test_nhan_theo_ngay_khong_bi_anh_huong(self):
        """Sửa này không được đụng tới thứ tự của nhãn đặt theo ngày."""
        assert loi.sap_buoi(["thu_7", "thu_2", "thu_5"]) == [
            "thu_2", "thu_5", "thu_7"]
        assert loi.sap_buoi(["Thứ Tư", "Thứ Hai", "Thứ Năm"]) == [
            "Thứ Hai", "Thứ Tư", "Thứ Năm"]

    def test_ba_nhom_dung_dung_thu_tu(self):
        """Ngày trước, rồi số, rồi nhãn lạ theo vần."""
        assert loi.sap_buoi(
            ["ngoai_khoa", "thu_5", "3", "abc", "thu_2", "10"]
        ) == ["thu_2", "thu_5", "3", "10", "abc", "ngoai_khoa"]


class TestNhatKyNeuBuoiDaChay:
    """`buoi_da_chay` được ghi xuống thì phải đọc lên được.

    Cột này thêm vào từ lúc có tính năng chạy một phần, nhưng
    `get_run_history` không `SELECT` nó, nên bảng nhật ký hiện hai lần chạy
    CHỈ KHÁC NHAU Ở DẤU THỜI GIAN. Muốn biết lần nào đụng buổi nào phải mở
    `app.db` bằng tay — tức dấu vết kiểm toán tồn tại mà không dùng được.
    """

    def test_nhat_ky_tra_ve_buoi_da_chay(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_3", "thu_5"])

        ds = api_nhieu_buoi.get_run_history()["data"]
        assert len(ds) >= 2
        assert ds[0]["buoi_da_chay"] == "thu_3,thu_5"
        assert ds[1]["buoi_da_chay"] == "thu_2,thu_3,thu_4,thu_5,thu_6"

    def test_hai_lan_chay_khac_buoi_phan_biet_duoc(self, api_nhieu_buoi):
        """Nếu hai dòng chỉ khác dấu thời gian thì nhật ký không nói được gì."""
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_2"])
        api_nhieu_buoi.run_pipeline(seed=42, chi_buoi=["thu_4"])

        ds = api_nhieu_buoi.get_run_history()["data"]
        khong_ke_gio = [
            {k: v for k, v in r.items() if k not in ("run_at", "run_id")}
            for r in ds[:2]
        ]
        assert khong_ke_gio[0] != khong_ke_gio[1]

    def test_nhat_ky_kem_so_buoi_va_cach_boc_tham(self, api_nhieu_buoi):
        api_nhieu_buoi.run_pipeline(seed=42)
        r = api_nhieu_buoi.get_run_history()["data"][0]
        assert r["so_buoi"] == 5
        assert r["che_do_boc_tham"] == "stb_ngay"


# ---------------------------------------------------------------------------
# 13 — TRẦN TÍNH THEO TỪNG BUỔI
# ---------------------------------------------------------------------------

def _csv_nv_theo_buoi(sid, theo_buoi):
    """Dựng CSV nguyện vọng dạng cột-theo-buổi từ {buoi: [club_id]}."""
    buoi = sorted(theo_buoi)
    rong = max(len(v) for v in theo_buoi.values())
    cot = ["student_id", "name"]
    for b in buoi:
        cot += ["%s_pref_%d" % (b, i + 1) for i in range(rong)]
    o = [sid, "Em Thử"]
    for b in buoi:
        ds = theo_buoi[b]
        o += [ds[i] if i < len(ds) else "" for i in range(rong)]
    return ",".join(cot) + "\n" + ",".join(o) + "\n"


@pytest.fixture
def api_sau_buoi(api):
    """Sáu buổi, mỗi buổi 12 CLB — đủ rộng để thử trần 10 mỗi buổi."""
    for b in ("thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7"):
        for i in range(12):
            cid = "%s_c%02d" % (b, i)
            api.create_or_update_club(cid, "CLB %s" % cid, 30, 0, "", buoi=b)
    return api


class TestTranNguyenVongMoiBuoi:
    """Trần 10 nguyện vọng tính theo TỪNG BUỔI, không phải cả tuần.

    Trần cũ đếm cả tuần và BỎ TRỌN học sinh vượt trần. Nó viết cho trường
    MỘT buổi — con số 10 là giới hạn câu hỏi Ranking của Microsoft Forms, và
    `docs/KE_HOACH_NHIEU_BUOI.md` đã chốt mỗi buổi một câu Ranking riêng.

    Với sáu buổi, em nào chọn 2 CLB mỗi buổi đã là 12 nguyện vọng và rơi ra
    ngoài. Đo được trước khi sửa: **31 trên 180 em** của `bo_sau_buoi` và
    **4 trên 160** của `bo_nhieu_buoi` bị gạt lặng lẽ khỏi đợt xếp. Những em
    đó hiện ra trên màn hình Kết quả y như em trượt, mà thật ra chưa bao giờ
    vào cuộc.

    ĐỐI CHỨNG NGƯỢC đã chạy thật — xem docstring từng test.
    """

    def test_sau_muoi_nguyen_vong_qua_sau_buoi_nap_tron_ven(self, api_sau_buoi):
        """10 mỗi buổi × 6 buổi = 60 nguyện vọng, không em nào bị bỏ.

        ĐỐI CHỨNG NGƯỢC: đếm tổng cả tuần thay vì theo buổi → test này ĐỎ.
        """
        theo_buoi = {b: ["%s_c%02d" % (b, i) for i in range(10)]
                     for b in ("thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7")}
        kq = api_sau_buoi.import_preferences_csv(_csv_nv_theo_buoi("HS001", theo_buoi))

        assert kq["ok"], kq
        assert kq["data"]["n_students_skipped"] == 0
        assert kq["data"]["n_buoi_bo_qua"] == 0
        assert len(api_sau_buoi.get_student_entry_state("HS001")["data"]["ranked_clubs"]) == 60

    def test_vuot_tran_mot_buoi_chi_mat_buoi_do(self, api_sau_buoi):
        """Một lỗi ở thứ Ba không có lý do gì làm em mất cả tuần.

        ĐỐI CHỨNG NGƯỢC: bỏ trọn học sinh thay vì bỏ riêng buổi → test ĐỎ.
        """
        theo_buoi = {
            "thu_3": ["thu_3_c%02d" % i for i in range(11)],   # vượt trần
            "thu_2": ["thu_2_c%02d" % i for i in range(3)],
            "thu_5": ["thu_5_c%02d" % i for i in range(3)],
        }
        kq = api_sau_buoi.import_preferences_csv(_csv_nv_theo_buoi("HS002", theo_buoi))

        assert kq["ok"], kq
        assert kq["data"]["n_students_skipped"] == 0, "không được bỏ cả học sinh"
        assert kq["data"]["n_buoi_bo_qua"] == 1

        giu = api_sau_buoi.get_student_entry_state("HS002")["data"]["ranked_clubs"]
        assert len(giu) == 6, giu
        assert not any(c.startswith("thu_3_") for c in giu)

        canh = [w for w in kq["data"]["warnings"]
                if w["code"] == "csv_pref_bo_buoi_qua_tran"]
        assert len(canh) == 1
        assert canh[0]["params"]["buoi"] == "thu_3"
        assert canh[0]["params"]["count"] == 11

    def test_moi_buoi_deu_vuot_tran_thi_moi_mat_ca_em(self, api_sau_buoi):
        theo_buoi = {b: ["%s_c%02d" % (b, i) for i in range(11)]
                     for b in ("thu_2", "thu_3")}
        kq = api_sau_buoi.import_preferences_csv(_csv_nv_theo_buoi("HS003", theo_buoi))
        assert kq["data"]["n_students_skipped"] == 1
        assert kq["data"]["n_buoi_bo_qua"] == 2

    def test_ma_clb_lech_hoa_thuong_van_gom_dung_buoi(self, api_sau_buoi):
        """Trần phải kiểm SAU khi chuẩn hoá mã CLB.

        Tra buổi bằng mã thô người dùng gõ thì mã lệch hoa/thường tra không
        ra buổi, rơi vào buổi mặc định và gom nhầm nhóm: 11 nguyện vọng của
        thứ Ba viết HOA sẽ bị coi là 11 nguyện vọng của một buổi khác.

        ĐỐI CHỨNG NGƯỢC: chuyển phép kiểm lên TRƯỚC `khop_club` → test ĐỎ.
        """
        theo_buoi = {
            "thu_3": ["THU_3_C%02d" % i for i in range(11)],   # viết HOA
            "thu_2": ["thu_2_c%02d" % i for i in range(3)],
        }
        kq = api_sau_buoi.import_preferences_csv(_csv_nv_theo_buoi("HS004", theo_buoi))

        canh = [w for w in kq["data"]["warnings"]
                if w["code"] == "csv_pref_bo_buoi_qua_tran"]
        assert len(canh) == 1
        assert canh[0]["params"]["buoi"] == "thu_3", canh

    def test_truong_mot_buoi_khong_doi_gi(self, api):
        """Test quan trọng nhất của cả thay đổi.

        Trường một buổi: mọi CLB thuộc buổi mặc định, nên "10 mỗi buổi" thu
        về đúng "10 tổng" — hành vi Y HỆT bản cũ, kể cả CÂU thông báo (nhãn
        buổi mặc định là chuỗi nội bộ, nêu ra là bắt người dùng đọc một khái
        niệm trường họ không có).
        """
        for i in range(1, 13):
            api.create_or_update_club("clb_%02d" % i, "CLB %d" % i, 20, 0, "")

        cot = ",".join("pref_%d" % i for i in range(1, 12))
        val = ",".join("clb_%02d" % i for i in range(1, 12))
        kq = api.import_preferences_csv("student_id,name,%s\nHS910,T,%s\n" % (cot, val))
        assert kq["data"]["n_students_skipped"] == 1
        assert any(w["code"] == "csv_pref_too_many_skipped"
                   for w in kq["data"]["warnings"])
        assert not any(w["code"] == "csv_pref_bo_buoi_qua_tran"
                       for w in kq["data"]["warnings"])

        cot = ",".join("pref_%d" % i for i in range(1, 11))
        val = ",".join("clb_%02d" % i for i in range(1, 11))
        kq = api.import_preferences_csv("student_id,name,%s\nHS911,T,%s\n" % (cot, val))
        assert kq["data"]["n_students_skipped"] == 0
        assert len(api.get_student_entry_state("HS911")["data"]["ranked_clubs"]) == 10

    def test_submit_preferences_dem_theo_buoi(self, api_sau_buoi):
        """Đường giao diện: 10 ở thứ Hai cộng 10 ở thứ Ba phải được nhận."""
        api_sau_buoi.create_student_if_missing("HS005", "Em Thử")
        ds = (["thu_2_c%02d" % i for i in range(10)]
              + ["thu_3_c%02d" % i for i in range(10)])
        assert api_sau_buoi.submit_preferences("HS005", ds)["ok"]

        assert not api_sau_buoi.submit_preferences(
            "HS005", ["thu_2_c%02d" % i for i in range(11)])["ok"]


class TestTranClbThiMoiBuoi:
    """Trần 5 CLB thi mỗi buổi — luật HOÀN TOÀN MỚI, trước không có trần nào.

    Áp cho mọi trường, kể cả trường một buổi. Đã kiểm trước khi làm: không bộ
    dữ liệu nào trong kho vượt 5, và bộ `TEST_02` — dữ liệu nghiên cứu đã
    công bố — đứng ĐÚNG 5, không có suất dự phòng nào. Vì vậy điều kiện phải
    là `> 5` mới từ chối.

    ĐỐI CHỨNG NGƯỢC: viết `>= 5` thay vì `> 5` → `TEST_02` không nạp được.
    """

    def _csv_thi(self, sid, ds_clb, diem=None):
        cot = ["student_id", "name"]
        o = [sid, "Em Thử"]
        for i, c in enumerate(ds_clb, start=1):
            cot += ["test_club_%d" % i, "score_%d" % i]
            o += [c, str((diem or {}).get(c, 8.0))]
        return ",".join(cot) + "\n" + ",".join(o) + "\n"

    def test_nam_clb_mot_buoi_duoc_nhan(self, api_sau_buoi):
        ds = ["thu_2_c%02d" % i for i in range(5)]
        kq = api_sau_buoi.import_test_selection_csv(self._csv_thi("HS101", ds))
        assert kq["data"]["n_students_skipped"] == 0
        assert kq["data"]["n_buoi_bo_qua"] == 0
        assert kq["data"]["n_scores_written"] == 5

    def test_sau_clb_mot_buoi_bi_chan(self, api_sau_buoi):
        ds = (["thu_2_c%02d" % i for i in range(6)]
              + ["thu_3_c%02d" % i for i in range(2)])
        kq = api_sau_buoi.import_test_selection_csv(self._csv_thi("HS102", ds))

        assert kq["data"]["n_buoi_bo_qua"] == 1
        assert kq["data"]["n_students_skipped"] == 0
        canh = [w for w in kq["data"]["warnings"]
                if w["code"] == "csv_thi_bo_buoi_qua_tran"]
        assert len(canh) == 1 and canh[0]["params"]["buoi"] == "thu_2"

    def test_diem_cua_buoi_bi_bo_khong_de_them_canh_bao(self, api_sau_buoi):
        """Bỏ buổi phải kéo theo điểm của buổi đó, và CHỈ MỘT cảnh báo.

        Không bỏ điểm thì mỗi CLB bị bỏ để lại một dòng điểm mồ côi cho một
        CLB em không còn dự thi. Còn nếu bỏ mà vẫn kêu
        `csv_score_for_unselected_club` thì người đọc tưởng có hai lỗi khác
        nhau, trong khi chỉ có một.
        """
        ds = ["thu_2_c%02d" % i for i in range(6)]
        kq = api_sau_buoi.import_test_selection_csv(self._csv_thi("HS103", ds))

        assert kq["data"]["n_scores_written"] == 0
        assert not any(w["code"] == "csv_score_for_unselected_club"
                       for w in kq["data"]["warnings"])

    def test_bo_du_lieu_nghien_cuu_TEST_02_van_nap_duoc(self, tmp_path):
        """`TEST_02` đứng ĐÚNG 5 CLB thi — không có suất dự phòng nào.

        Đây là dữ liệu mà `docs/NGHIEN_CUU_TOI_UU.md` đang trích dẫn. Viết nhầm
        `>= 5` là làm hỏng nó.
        """
        students, clubs, scores, app, prefs, _ = _bo_mot_buoi(tmp_path, "TEST_0*")
        assert students, "bộ TEST_0* phải nạp được"
        # `app` khoá theo CLB; đếm theo HỌC SINH mới là con số trần nói tới.
        theo_em: dict = {}
        for cid, ds in app.items():
            for sid in ds:
                theo_em.setdefault(sid, []).append(cid)
        assert max(len(v) for v in theo_em.values()) >= 5, (
            "nếu bộ này không còn chạm trần thì test mất ý nghĩa canh"
        )

    def test_submit_test_selection_dem_theo_buoi(self, api_sau_buoi):
        api_sau_buoi.create_student_if_missing("HS104", "Em Thử")
        ds = (["thu_2_c%02d" % i for i in range(5)]
              + ["thu_3_c%02d" % i for i in range(5)])
        assert api_sau_buoi.submit_test_selection("HS104", ds)["ok"]

        assert not api_sau_buoi.submit_test_selection(
            "HS104", ["thu_2_c%02d" % i for i in range(6)])["ok"]
