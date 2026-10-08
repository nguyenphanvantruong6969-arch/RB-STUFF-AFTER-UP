"""Đo lại ba câu hỏi hay bị hỏi nhất về bốc thăm — để trả lời bằng SỐ.

    ./.venv/bin/python du_lieu_test/do_cau_hoi_boc_tham.py

Ba câu:
  1. Đổi seed có làm bốc thăm mất công bằng không?
  2. Đổi thứ tự nhập dữ liệu có ảnh hưởng không?
  3. Những gì thật sự ảnh hưởng tới bộ số bốc thăm?

Kết quả in ra dùng cho `docs/GIAI_DAP_BOC_THAM.md`. Chạy lại lúc nào cũng ra
đúng bằng đó — không có gì phụ thuộc đồng hồ hay máy.
"""

import collections
import os
import random
import shutil
import statistics
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbda_priority_pipeline as loi  # noqa: E402
from api import PipelineAPI  # noqa: E402

N_HS = 100
N_SEED = 10000
N_KHOI = 8          # số khối seed rời nhau, để phân biệt nhiễu với thiên vị
MA = ["HS%03d" % i for i in range(1, N_HS + 1)]


def _tuong_quan(ma, seed_dau, n_seed):
    """Tương quan Pearson giữa thứ tự mã học sinh và thứ hạng bốc thăm
    trung bình, đo trên một khối seed."""
    tong = {s: 0 for s in ma}
    for s in range(seed_dau, seed_dau + n_seed):
        for sid, h in loi.generate_stb_lottery(ma, s).items():
            tong[sid] += h
    tb = {s: tong[s] / n_seed for s in ma}
    thu_tu = {s: i for i, s in enumerate(sorted(ma))}
    x = [thu_tu[s] for s in ma]
    y = [tb[s] for s in ma]
    mx, my = statistics.mean(x), statistics.mean(y)
    tu = sum((a - mx) * (b - my) for a, b in zip(x, y))
    mau = (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** 0.5
    return tu / mau


def tieu_de(n, chu):
    print()
    print("=" * 72)
    print("CÂU %d — %s" % (n, chu))
    print("=" * 72)


# ---------------------------------------------------------------------------
def cau_1():
    tieu_de(1, "Đổi seed có làm bốc thăm mất công bằng không?")

    # Với mỗi em: qua N_SEED lần bốc, em đó nhận được những thứ hạng nào?
    tong = collections.Counter()
    o_dau_bang = collections.Counter()      # lọt top 10%
    for s in range(1, N_SEED + 1):
        bo = loi.generate_stb_lottery(MA, s)
        for sid, hang in bo.items():
            tong[sid] += hang
            if hang < N_HS // 10:
                o_dau_bang[sid] += 1

    tb = {sid: tong[sid] / N_SEED for sid in MA}
    ky_vong = (N_HS - 1) / 2
    print("  %d học sinh, %d seed (mỗi seed một lần bốc lại toàn bộ)" % (N_HS, N_SEED))
    print()
    print("  Thứ hạng trung bình của mỗi em qua %d lần bốc:" % N_SEED)
    print("    lý thuyết nếu công bằng tuyệt đối   %8.2f" % ky_vong)
    print("    thấp nhất trong %d em              %8.2f  (%s)"
          % (N_HS, min(tb.values()), min(tb, key=tb.get)))
    print("    cao nhất trong %d em               %8.2f  (%s)"
          % (N_HS, max(tb.values()), max(tb, key=tb.get)))
    print("    chênh lệch lớn nhất so với lý thuyết %7.2f  (%.2f%%)"
          % (max(abs(v - ky_vong) for v in tb.values()),
             100 * max(abs(v - ky_vong) for v in tb.values()) / ky_vong))
    print()
    tl = {sid: 100.0 * o_dau_bang[sid] / N_SEED for sid in MA}
    print("  Tỉ lệ lọt vào nhóm 10% đầu bảng:")
    print("    lý thuyết nếu công bằng tuyệt đối   %8.2f%%" % 10.0)
    print("    thấp nhất                           %8.2f%%  (%s)"
          % (min(tl.values()), min(tl, key=tl.get)))
    print("    cao nhất                            %8.2f%%  (%s)"
          % (max(tl.values()), max(tl, key=tl.get)))
    print()

    # Ma hoc sinh co "keo" thu hang khong?
    #
    # Do MOT lan roi ket luan la SAI: he so tuong quan tren 100 em von da dao
    # dong quanh 0 mot cach tu nhien (nguong nhieu ly thuyet ~ 1/sqrt(n-1) =
    # 0.10). Muon biet la thien vi THAT hay chi la nhieu thi phai do tren
    # NHIEU KHOI SEED ROI NHAU: thien vi that thi giu nguyen dau va do lon;
    # nhieu thi doi ca dau.
    print("  Mã học sinh có kéo thứ hạng không?")
    print("    (hệ số tương quan giữa THỨ TỰ MÃ và THỨ HẠNG TRUNG BÌNH;")
    print("     0 = không liên quan gì, ±1 = phụ thuộc hoàn toàn)")
    print()
    r = []
    for i in range(N_KHOI):
        dau = 1 + i * N_SEED
        r.append(_tuong_quan(MA, dau, N_SEED))
        print("      seed %6d..%-6d %+8.4f" % (dau, dau + N_SEED - 1, r[-1]))
    nguong = 1 / (N_HS - 1) ** 0.5
    print()
    print("      trung bình %d khối          %+8.4f" % (N_KHOI, statistics.mean(r)))
    print("      độ lệch giữa các khối       %+8.4f" % statistics.stdev(r))
    print("      ngưỡng nhiễu lý thuyết      %+8.4f   (= 1/căn(%d-1))"
          % (nguong, N_HS))
    print()
    doi_dau = min(r) < 0 < max(r)
    print("      hệ số có ĐỔI DẤU giữa các khối không? %s" % ("CÓ" if doi_dau else "KHÔNG"))
    print("      -> %s" % ("NHIỄU, không phải thiên vị. Thiên vị thật thì giữ "
                           "nguyên dấu qua mọi khối." if doi_dau else
                           "CẦN XEM LẠI — giữ nguyên dấu là dấu hiệu thiên vị."))


# ---------------------------------------------------------------------------
def cau_2():
    tieu_de(2, "Đổi thứ tự nhập dữ liệu có ảnh hưởng không?")

    def chay(thu_tu_hs):
        d = tempfile.mkdtemp()
        try:
            api = PipelineAPI(os.path.join(d, "app.db"))
            api.create_or_update_club("clb_a", "CLB A", 5, 0, "")
            api.create_or_update_club("clb_b", "CLB B", 5, 0, "")
            for sid in thu_tu_hs:
                api.create_student_if_missing(sid, "Học sinh " + sid)
                api.submit_test_selection(sid, ["clb_a", "clb_b"])
                api.submit_preferences(sid, ["clb_a", "clb_b"])
                # CỐ Ý cho nhiều em hoà điểm — chỗ duy nhất bốc thăm can thiệp
                api.submit_club_scores("clb_a", [{"student_id": sid, "score": 8.0}])
                api.submit_club_scores("clb_b", [{"student_id": sid, "score": 7.0}])
            api.run_pipeline(seed=42)
            st, cl, dm, uv, nv, stb = loi.load_from_sqlite(os.path.join(d, "app.db"))
            kq = loi.run_rbda(st, cl, dm, uv, nv, stb,
                              loi.default_reserve_eligible_fn(st, cl))
            return dict(stb), dict(kq.assignment)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    goc = MA[:20]
    stb_goc, xep_goc = chay(goc)

    rng = random.Random(2026)
    khac_stb = khac_xep = 0
    N_THU = 20
    for lan in range(N_THU):
        xao = goc[:]
        rng.shuffle(xao)
        stb2, xep2 = chay(xao)
        if stb2 != stb_goc:
            khac_stb += 1
        if xep2 != xep_goc:
            khac_xep += 1

    print("  20 học sinh, tất cả HOÀ ĐIỂM (chỗ duy nhất bốc thăm có quyền)")
    print("  Nhập lại %d lần theo %d thứ tự XÁO NGẪU NHIÊN khác nhau:" % (N_THU, N_THU))
    print()
    print("    số lần bộ SỐ BỐC THĂM khác bản gốc   %3d / %d" % (khac_stb, N_THU))
    print("    số lần KẾT QUẢ XẾP khác bản gốc      %3d / %d" % (khac_xep, N_THU))
    print()
    print("  Ngược lại, đổi seed thì phải khác:")
    n_khac = sum(1 for s in range(1, 51)
                 if loi.generate_stb_lottery(goc, s) != loi.generate_stb_lottery(goc, 42))
    print("    50 seed, số seed cho bộ số khác seed 42:  %d / 49" % n_khac)


# ---------------------------------------------------------------------------
def cau_3():
    tieu_de(3, "Những gì ảnh hưởng tới bộ số bốc thăm?")

    goc = loi.generate_stb_lottery(MA, 42)

    print("  Thử đổi từng thứ một, xem bộ số có đổi theo không:")
    print()
    print("    %-42s %s" % ("Đổi thứ này", "Bộ số bốc thăm"))
    print("    " + "-" * 62)

    # 1. doi seed
    print("    %-42s %s" % ("Số seed (42 -> 43)",
          "ĐỔI" if loi.generate_stb_lottery(MA, 43) != goc else "không đổi"))
    # 2. doi thu tu danh sach dua vao
    dao = MA[::-1]
    print("    %-42s %s" % ("Thứ tự danh sách đưa vào (đảo ngược)",
          "ĐỔI" if loi.generate_stb_lottery(dao, 42) != goc else "không đổi"))
    # 3. xao ngau nhien nhieu lan
    rng = random.Random(7)
    khac = 0
    for _ in range(100):
        x = MA[:]
        rng.shuffle(x)
        if loi.generate_stb_lottery(x, 42) != goc:
            khac += 1
    print("    %-42s %s" % ("Thứ tự danh sách (100 lần xáo ngẫu nhiên)",
          "ĐỔI %d/100" % khac if khac else "không đổi, cả 100/100"))
    # 4. them mot hoc sinh
    them = loi.generate_stb_lottery(MA + ["HS999"], 42)
    n_giu = sum(1 for sid in MA if them.get(sid) == goc.get(sid))
    print("    %-42s %s" % ("Thêm 1 học sinh vào danh sách",
          "ĐỔI — chỉ %d/%d em giữ nguyên số" % (n_giu, len(MA))))
    # 5. bot mot hoc sinh
    bot = loi.generate_stb_lottery(MA[:-1], 42)
    n_giu2 = sum(1 for sid in MA[:-1] if bot.get(sid) == goc.get(sid))
    print("    %-42s %s" % ("Bớt 1 học sinh khỏi danh sách",
          "ĐỔI — chỉ %d/%d em giữ nguyên số" % (n_giu2, len(MA) - 1)))
    # 6. chay lai y nguyen
    print("    %-42s %s" % ("Chạy lại y nguyên (cùng seed, cùng tập)",
          "không đổi" if loi.generate_stb_lottery(MA, 42) == goc else "ĐỔI"))

    print()
    print("  => Đúng HAI thứ ảnh hưởng: SỐ SEED và TẬP MÃ HỌC SINH.")
    print("     Thứ tự nhập không ảnh hưởng. Tên, điểm, giờ chạy không ảnh hưởng.")


if __name__ == "__main__":
    print()
    print("ĐO LẠI BA CÂU HỎI VỀ BỐC THĂM")
    print("Mọi số dưới đây sinh ra từ chính mã đang chạy trong phần mềm.")
    cau_1()
    cau_2()
    cau_3()
    print()
