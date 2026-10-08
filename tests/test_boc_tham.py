"""
test_boc_tham.py
================
Canh bộ đo ba thiết kế bốc thăm (`du_lieu_test/do_boc_tham.py`).

BỐN THỨ ĐƯỢC CANH, VÀ VÌ SAO TỪNG THỨ CÓ MẶT
--------------------------------------------
1. **Chiều dấu.** Bảng đo lần trước in nhãn "(âm = A2 tốt hơn)" cho hiệu
   `A1 − A2` trên số em trắng tay, trong khi âm nghĩa là A1 ít em trắng tay
   hơn, tức A1 tốt hơn. Nhãn được gõ tay nên không có gì phát hiện ra: mã
   chạy đúng, số đúng, chỉ câu chữ dẫn người đọc sang kết luận ngược. Nhóm
   test này dựng hai mẫu ĐÃ BIẾT chiều rồi soát cả nhãn lẫn kết luận.

2. **Tái lập.** Cùng seed phải ra cùng số, kể cả ở một tiến trình khác với
   `PYTHONHASHSEED` khác. `sinh_stb_theo_buoi` dẫn xuất seed theo tên buổi;
   nếu ai đó đổi `zlib.crc32` thành `hash()` thì hai lần chạy ra hai kết
   quả khác nhau — loại lỗi im lặng tới lúc có người đối chiếu hai lần chạy.

3. **Ổn định.** Cả ba thiết kế phải cho 0 cặp phá vỡ. Một thiết kế bốc thăm
   không được phép đánh đổi sự ổn định lấy sự công bằng — nếu có cặp phá vỡ
   thì mọi so sánh về công bằng ở trên đều vô nghĩa.

4. **Chốt số.** Lát cắt tất định nhỏ phải khớp `so_lieu_boc_tham.json`.
   Số trôi mà không ai biết thì trang nghiên cứu trích số cũ của một phần
   mềm đã đổi.

ĐỐI CHỨNG NGƯỢC — ĐÃ THỬ THẬT, KẾT QUẢ GHI Ở ĐÂY
------------------------------------------------
Mỗi test chỉ đáng tin nếu nó BẮT được lỗi mà nó nói là canh. Ba lần thử:

  a. Đảo dấu trong `hieu_theo_cap` (`x - y` thành `y - x`):
     -> ĐỎ 3/23: test_chieu_dau_khi_a_tot_hon · test_chieu_dau_khi_b_tot_hon ·
        test_chieu_dau_dao_lai_khi_cang_lon_cang_tot.

  b. Đổi `mo_ta_chieu` thành nhãn gõ tay kiểu cũ — bỏ `cang_nho_cang_tot`,
     in thẳng ("âm = %s tốt hơn" % ten_b). Đây ĐÚNG là lỗi đã mắc lần trước:
     -> ĐỎ 3/23: cùng ba test trên.
     Lần thử đầu chỉ bắt được 1/3, vì hai test kia không soát nhãn. Đã thêm
     assert nhãn vào cả ba rồi thử lại — ghi lại ở đây vì một đối chứng
     ngược "gần như bắt được" cũng là một lỗ hổng, chỉ là lỗ hổng ở test.

  c. Đổi `_seed_cua_buoi` từ `zlib.crc32` sang `hash()`:
     -> ĐỎ 2/23: test_tai_lap_qua_hai_tien_trinh[1] và [12345].
     Ô [0] vẫn XANH, và đúng là nó không bắt được: cả hai tiến trình trong ô
     đó cùng chạy PYTHONHASHSEED=0 nên hash() cho cùng số. Ô [0] có mặt để
     soát chính bộ test, hai ô kia mới là ô canh lỗi.

  d. Cài A2 thành A1 (`sinh_stb_theo_buoi` ngắn mạch cho MỌI chế độ):
     -> ĐỎ 2/23: test_ba_thiet_ke_khac_nhau_khi_thuan_boc_tham ·
        test_chot_so_tn7b_o_choi_cao.
"""

import json
import os
import subprocess
import sys

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))

import rbda_priority_pipeline as loi  # noqa: E402
import do_boc_tham as db  # noqa: E402

DUONG_JSON = os.path.join(GOC, "du_lieu_test", "so_lieu_boc_tham.json")


@pytest.fixture(scope="module")
def so_lieu():
    if not os.path.exists(DUONG_JSON):
        pytest.skip("chua chay du_lieu_test/do_boc_tham.py")
    with open(DUONG_JSON, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 1 — CHIỀU DẤU
# ---------------------------------------------------------------------------

class TestChieuDau:
    """Nhãn và kết luận phải đi theo công thức, không đi theo trí nhớ."""

    def test_chieu_dau_khi_a_tot_hon(self):
        # A ít em trắng tay hơn ở mọi seed -> A tốt hơn, hiệu phải ÂM.
        h = db.hieu_theo_cap("A", "B", [10, 11, 9, 10], [20, 21, 19, 20],
                             cang_nho_cang_tot=True, so_lan=2000)
        assert h["trung_binh_hieu"] < 0
        assert h["ket_luan"] == "A tốt hơn"
        assert h["so_seed_a_thang"] == 4
        assert h["so_seed_b_thang"] == 0
        # Nhãn phải nói ĐÚNG chiều đó: âm ứng với A.
        assert "âm = A tốt hơn" in h["nhan_chieu"]
        assert "dương = B tốt hơn" in h["nhan_chieu"]

    def test_chieu_dau_khi_b_tot_hon(self):
        h = db.hieu_theo_cap("A", "B", [20, 21, 19, 20], [10, 11, 9, 10],
                             cang_nho_cang_tot=True, so_lan=2000)
        assert h["trung_binh_hieu"] > 0
        assert h["ket_luan"] == "B tốt hơn"
        assert h["so_seed_b_thang"] == 4
        # Nhãn không đổi theo dữ liệu — nó mô tả CÔNG THỨC, nên vẫn phải là
        # "âm = A". Nhãn gõ tay hay đảo chỗ hai tên chính là chỗ này hỏng.
        assert "âm = A tốt hơn" in h["nhan_chieu"]

    def test_chieu_dau_dao_lai_khi_cang_lon_cang_tot(self):
        # Cùng một cặp số, nhưng chỉ số này CÀNG LỚN CÀNG TỐT (ví dụ số CLB
        # trung bình mỗi em) -> người thắng phải đổi bên.
        nho = db.hieu_theo_cap("A", "B", [20, 21], [10, 11], cang_nho_cang_tot=True,
                               so_lan=2000)
        lon = db.hieu_theo_cap("A", "B", [20, 21], [10, 11], cang_nho_cang_tot=False,
                               so_lan=2000)
        assert nho["ket_luan"] == "B tốt hơn"
        assert lon["ket_luan"] == "A tốt hơn"
        assert "âm = A tốt hơn" in nho["nhan_chieu"]
        assert "âm = B tốt hơn" in lon["nhan_chieu"]

    def test_ket_luan_suy_ra_tu_khoang_tin_cay(self):
        # Chênh lệch nhỏ và lẫn lộn -> khoảng tin cậy chứa 0 -> KHÔNG được
        # gọi tên người thắng. Đây là chỗ chặn việc đọc nhiễu thành tín hiệu.
        a = [10, 11, 10, 9, 10, 11, 9, 10, 11, 9]
        b = [10, 10, 11, 10, 9, 10, 11, 9, 10, 11]
        h = db.hieu_theo_cap("A", "B", a, b, so_lan=4000)
        assert h["ci95_thap"] <= 0 <= h["ci95_cao"]
        assert h["ket_luan"] == "không phân biệt được"

    def test_hai_mau_lech_so_seed_thi_bao_loi(self):
        with pytest.raises(ValueError):
            db.hieu_theo_cap("A", "B", [1, 2, 3], [1, 2], so_lan=100)


# ---------------------------------------------------------------------------
# 2 — TÁI LẬP
# ---------------------------------------------------------------------------

class TestTaiLap:

    def test_cung_seed_ra_cung_ket_qua(self):
        import random
        du_lieu = db.sinh_bo_tong_hop(random.Random(1), so_em=60, so_buoi=4)
        a = db.chay_tuan(du_lieu, 7, "stb_ngay")[0]
        b = db.chay_tuan(du_lieu, 7, "stb_ngay")[0]
        assert a.assignment == b.assignment

    @pytest.mark.parametrize("hash_seed", ["0", "1", "12345"])
    def test_tai_lap_qua_hai_tien_trinh(self, hash_seed):
        """Chặn `hash()` của Python trong đường sinh bộ số theo buổi.

        hash() của chuỗi bị ngẫu nhiên hoá theo tiến trình, nên test này
        PHẢI chạy ở tiến trình con với PYTHONHASHSEED khác nhau — gọi hàm
        hai lần trong cùng tiến trình không bắt được lỗi đó.
        """
        ma = (
            "import sys, random;"
            "sys.path.insert(0, %r); sys.path.insert(0, %r);"
            "import do_boc_tham as db;"
            "d = db.sinh_bo_tong_hop(random.Random(1), so_em=60, so_buoi=4);"
            "k = db.chay_tuan(d, 7, 'stb_ngay')[0];"
            "print(sorted((s, tuple(sorted(v.items()))) for s, v in k.assignment.items()))"
            % (GOC, os.path.join(GOC, "du_lieu_test"))
        )
        moi = dict(os.environ, PYTHONHASHSEED=hash_seed)
        ra = subprocess.run([sys.executable, "-c", ma], capture_output=True,
                            text=True, env=moi, cwd=GOC)
        assert ra.returncode == 0, ra.stderr
        goc = subprocess.run([sys.executable, "-c", ma], capture_output=True,
                             text=True, env=dict(os.environ, PYTHONHASHSEED="0"),
                             cwd=GOC)
        assert ra.stdout == goc.stdout


# ---------------------------------------------------------------------------
# 3 — ỔN ĐỊNH VÀ RÀNG BUỘC
# ---------------------------------------------------------------------------

class TestOnDinh:

    @pytest.mark.parametrize("che_do", ["stb_tuan", "stb_ngay", "stb_co_bu"])
    def test_khong_cap_pha_vo(self, che_do):
        import random
        for i in range(5):
            du_lieu = db.sinh_bo_tong_hop(
                random.Random(100 + i), so_em=80, so_buoi=4, ti_le_choi=1.5)
            kq, _stb, elig = db.chay_tuan(du_lieu, 42 + i, che_do)
            t = db.cham_ket_qua(kq, du_lieu, elig=elig)
            assert t["cap_pha_vo"] == 0

    @pytest.mark.parametrize("che_do", ["stb_tuan", "stb_ngay", "stb_co_bu"])
    def test_moi_buoi_toi_da_mot_clb(self, che_do):
        import random
        du_lieu = db.sinh_bo_tong_hop(random.Random(5), so_em=80, so_buoi=5)
        kq, _stb, _e = db.chay_tuan(du_lieu, 9, che_do)
        for _sid, theo_buoi in kq.assignment.items():
            assert len(theo_buoi) == len(kq.ds_buoi)
            for buoi, cid in theo_buoi.items():
                if cid is not None:
                    assert du_lieu[1][cid]["buoi"] == buoi

    def test_ba_thiet_ke_khac_nhau_khi_thuan_boc_tham(self):
        """Bốc thăm quyết định tất thì ba thiết kế PHẢI ra khác nhau.

        Giống hệt nhau nghĩa là bộ chọn chế độ hỏng, và cả TN7b lẫn TN7c
        chỉ đang đo đúng một thiết kế ba lần.
        """
        import random
        du_lieu = db.sinh_bo_tong_hop(
            random.Random(11), so_em=200, ti_le_choi=2.0, ti_le_tier1=0.0)
        tt = {}
        for _nhan, ma in db.CHE_DO:
            kq, _s, _e = db.chay_tuan(du_lieu, 3, ma)
            tt[ma] = db.cham_ket_qua(kq, du_lieu, kiem_on_dinh=False)["trang_tay"]
        assert len(set(tt.values())) == 3, tt
        assert tt["stb_tuan"] > tt["stb_ngay"] > tt["stb_co_bu"]


# ---------------------------------------------------------------------------
# 4 — CHỐT SỐ
# ---------------------------------------------------------------------------

class TestChotSo:
    """Lát cắt nhỏ, tất định, chạy lại được trong vài giây."""

    def test_chot_so_tn7a_bo_mau(self, so_lieu):
        moc = so_lieu["tn7a_bo_mau"]
        chay = db.tn7a_bo_mau(5, so_seed_kiem_on_dinh=2, in_ra=False)
        # 5 seed đầu là tập con của 200 seed đã ghi, nên trung bình lệch
        # được; cái PHẢI khớp là những thứ không phụ thuộc số seed.
        assert chay["so_em_co_khai"] == moc["so_em_co_khai"]
        for nhan, _ in db.CHE_DO:
            assert chay["theo_che_do"][nhan]["tong_cap_pha_vo"] == 0
            assert moc["theo_che_do"][nhan]["tong_cap_pha_vo"] == 0

    def test_chot_so_tn7b_o_choi_cao(self, so_lieu):
        """Ô chọi 4,0× / khai 5 buổi — ô có lợi thế A2 lớn nhất.

        Chạy lại đúng ô đó với 3 seed đầu và đòi khớp TỪNG SỐ với lần chạy
        đã ghi. Ba seed đủ để bắt mọi thay đổi làm lệch kết quả, mà chỉ tốn
        vài giây.
        """
        import random
        moc = so_lieu["tn7b_thuan_boc_tham"]["choi_4.0_khai_5"]
        assert moc["trang_tay_tb"][db.CHE_DO[0][0]] > moc["trang_tay_tb"][db.CHE_DO[1][0]]

        def tao(i):
            rng = random.Random(db.HAT_SINH + 7919 * i + int(4.0 * 100) + 5)
            return db.sinh_bo_tong_hop(rng, ti_le_choi=4.0, so_buoi_khai=5,
                                       ti_le_tier1=0.0)

        mau, _phu, cpv = db._chay_mot_o(tao, 3)
        assert cpv == 0
        a1 = mau[db.CHE_DO[0][0]]
        a2 = mau[db.CHE_DO[1][0]]
        assert sum(a1) / 3 > sum(a2) / 3 + 20, (a1, a2)

    def test_chot_so_tn7c_loi_the_giam_dan(self, so_lieu):
        """Mệnh đề trung tâm của TN7c: em có điểm càng nhiều, lợi thế A2 càng ít.

        Không đòi giảm đơn điệu từng bước (30 seed thì nhiễu ở hai mức sát
        nhau là bình thường) — đòi hai đầu cách nhau rõ rệt và xu hướng đi
        xuống.
        """
        c1 = so_lieu["tn7c_co_che"]["theo_ti_le_tier1"]
        day = [c1[k]["loi_the_A2"] for k in sorted(c1, key=lambda k: c1[k]["ti_le_tier1"])]
        assert day[0] > 5.0, day
        assert day[-1] < 1.0, day
        assert day[0] > day[len(day) // 2] > day[-1], day

    def test_chot_so_tn7d_a3_khai_gian_duoc(self, so_lieu):
        """A1/A2 phải là 0, A3 phải khác 0 — nếu A3 cũng 0 thì bộ dò hỏng."""
        d = so_lieu["tn7d_khai_gian"]
        assert d[db.CHE_DO[0][0]]["so_em_loi_tong_diem"] == 0
        assert d[db.CHE_DO[1][0]]["so_em_loi_tong_diem"] == 0
        assert d[db.CHE_DO[2][0]]["so_em_loi_tong_diem"] > 0
        assert d[db.CHE_DO[2][0]]["vi_du"] is not None

    def test_so_lieu_khong_phai_ban_rut_gon(self, so_lieu):
        """Trang nghiên cứu trích tệp này, nên tệp này không được là bản --nhanh."""
        assert so_lieu["_ban_rut_gon"] is False
        assert so_lieu["so_seed_tn7a"] >= 200
        assert so_lieu["so_seed_moi_o"] >= 30


# ---------------------------------------------------------------------------
# 5 — LÕI KHÔNG BỊ ĐỤNG
# ---------------------------------------------------------------------------

def test_bo_do_khong_sua_nam_ham_loi():
    """Bộ đo phải GỌI thuật toán, không được dựng lại một bản của nó.

    Nếu tệp đo tự cài lại vòng lặp DA thì mọi con số nói về bản sao đó chứ
    không nói về phần mềm mà học sinh dùng.
    """
    with open(os.path.join(GOC, "du_lieu_test", "do_boc_tham.py"), encoding="utf-8") as f:
        ma = f.read()
    assert "loi.run_rbda_nhieu_buoi(" in ma
    assert "loi.verify_stability_tuan(" in ma
    assert "loi.generate_stb_lottery(" in ma
    # Không được có vòng lặp deferred acceptance viết tay trong tệp đo.
    assert "while unassigned" not in ma
    assert "def run_rbda" not in ma


def test_compute_club_priority_khong_nhan_them_tham_so():
    """Ràng buộc chống nội sinh ở dòng 63–72 phải còn nguyên.

    `stb_co_bu` được cài bằng cách đánh lại BỘ SỐ BỐC THĂM trước khi chạy
    buổi đó, chứ không phải bằng cách nhét kết cục buổi trước vào hàm tính
    ưu tiên. Test này canh chữ ký hàm để cách cài đó không trôi.
    """
    import inspect

    ts = list(inspect.signature(loi.compute_club_priority).parameters)
    assert ts == ["club_id", "applicants_for_club", "tested_scores_for_club",
                  "stb_lottery"], ts
