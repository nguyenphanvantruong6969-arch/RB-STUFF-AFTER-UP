"""
thu_nghich_canh.py
==================
Thử tải kiểu NGHỊCH CẢNH — không phải to hơn, mà HIỂM hơn.

    ./.venv/bin/python du_lieu_test/thu_tai/thu_nghich_canh.py

VÌ SAO CẦN, KHI ĐÃ CÓ chay_thu_tai.py
--------------------------------------
`chay_thu_tai.py` đã quét 204 cấu hình tới 5000 em / 100 CLB. Nhưng nó
quét dữ liệu BÌNH THƯỜNG, chỉ đổi quy mô. Lỗi thật hiếm khi nấp ở chỗ
"nhiều quá" — nó nấp ở chỗ dữ liệu có HÌNH THÙ lạ mà lập trình viên
không nghĩ tới: mọi em cùng một nguyện vọng, mọi CLB một chỗ, cả trường
hoà điểm, CLB không ai đăng ký.

Mỗi kịch bản đi qua ĐÚNG đường người dùng đi (`PipelineAPI`), và phải
qua được ba chốt:

  * không ném lỗi, `run_pipeline` trả `ok = True`
  * **0 cặp phá vỡ** — `run_pipeline` tự rollback nếu có, nên `ok = True`
    đã hàm ý điều này, nhưng vẫn kiểm lại độc lập cho chắc
  * số vòng chạy dưới trần `max_rounds`

KHÔNG đụng `app.db` thật: mỗi kịch bản một thư mục tạm, xoá sau khi chạy.
"""

import os
import shutil
import sys
import tempfile
import time
import traceback

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, GOC)

import rbda_priority_pipeline as loi  # noqa: E402
from api import PipelineAPI  # noqa: E402

TRAN_VONG = 1000          # max_rounds mặc định của run_rbda


def _kiem_ket_qua(api, ten):
    """Đọc lại từ CSDL và kiểm độc lập, không tin lời run_pipeline."""
    students, clubs, diem, uv, nv, stb = loi.load_from_sqlite(api.db_path)
    fn = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda(students, clubs, diem, uv, nv, stb, fn)
    cap = loi.verify_stability(kq, clubs, nv, fn)
    if cap:
        raise AssertionError("%s: %d cặp phá vỡ" % (ten, len(cap)))
    if kq.rounds_run >= TRAN_VONG:
        raise AssertionError("%s: chạm trần %d vòng" % (ten, TRAN_VONG))
    return kq, len(students)


# --------------------------------------------------------------------------
# Các kịch bản. Mỗi hàm nhận api đã dựng sẵn, tự nạp dữ liệu của mình.
# --------------------------------------------------------------------------

def kb_mot_nguyen_vong_duy_nhat(api, n=800):
    """Mọi em chỉ xếp ĐÚNG MỘT nguyện vọng, vào cùng một CLB 20 chỗ.
    780 em chắc chắn trượt — chuỗi từ chối dài nhất có thể."""
    api.create_or_update_club("clb_hot", "CLB Hot", 20, 0, "")
    for i in range(n):
        sid = "HS%04d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_test_selection(sid, ["clb_hot"])
        api.submit_club_scores("clb_hot", [{"student_id": sid, "score": 5 + i % 5}])
        api.submit_preferences(sid, ["clb_hot"])
    return "800 em · 1 CLB 20 chỗ · mỗi em 1 nguyện vọng"


def kb_suc_chua_mot(api, n=300, n_clb=30):
    """Mọi CLB đúng MỘT chỗ. Đẩy dây chuyền tối đa."""
    for j in range(n_clb):
        api.create_or_update_club("c%02d" % j, "CLB %d" % j, 1, 0, "")
    for i in range(n):
        sid = "HS%04d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["c%02d" % ((i + k) % n_clb) for k in range(10)])
    return "300 em · 30 CLB SỨC CHỨA 1 · 10 nguyện vọng"


def kb_ca_truong_hoa_diem(api, n=500, n_clb=10):
    """Mọi em CÙNG MỘT điểm ở mọi CLB — bốc thăm gánh toàn bộ việc phá hoà."""
    for j in range(n_clb):
        api.create_or_update_club("c%02d" % j, "CLB %d" % j, 20, 0, "")
    for i in range(n):
        sid = "HS%04d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        ds = ["c%02d" % ((i + k) % n_clb) for k in range(5)]
        api.submit_test_selection(sid, ds)
        for c in ds:
            api.submit_club_scores(c, [{"student_id": sid, "score": 8.0}])
        api.submit_preferences(sid, ds)
    return "500 em · CÙNG điểm 8.0 ở mọi CLB"


def kb_toan_bo_tang_2(api, n=400, n_clb=10):
    """KHÔNG em nào được chấm điểm — toàn Tầng 2, nhánh ít chạy nhất."""
    for j in range(n_clb):
        api.create_or_update_club("c%02d" % j, "CLB %d" % j, 15, 0, "")
    for i in range(n):
        sid = "HS%04d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["c%02d" % ((i + k) % n_clb) for k in range(4)])
    return "400 em · KHÔNG ai được chấm điểm (toàn Tầng 2)"


def kb_rong_va_le_loi(api):
    """CLB không ai đăng ký, em không nguyện vọng nào, CLB 1 chỗ 1 người.
    Toàn những chỗ dễ chia cho 0 hoặc lấy phần tử của danh sách rỗng."""
    api.create_or_update_club("clb_vang", "CLB không ai vào", 10, 0, "")
    api.create_or_update_club("clb_vua", "CLB vừa khít", 1, 0, "")
    api.create_student_if_missing("HS_khong_nv", "Em không nguyện vọng")
    api.create_student_if_missing("HS_co_nv", "Em có nguyện vọng")
    api.submit_preferences("HS_co_nv", ["clb_vua"])
    return "CLB không ai đăng ký · em không nguyện vọng · CLB vừa khít"


def kb_du_tru_bang_suc_chua(api, n=200, n_clb=8):
    """`reserve_capacity == capacity` — lượt chung không còn chỗ nào."""
    for j in range(n_clb):
        api.create_or_update_club("c%02d" % j, "CLB %d" % j, 10, 10, "uu_tien")
    for i in range(n):
        sid = "HS%04d" % i
        api.create_student_if_missing(sid, "Em %d" % i)
        api.submit_preferences(sid, ["c%02d" % ((i + k) % n_clb) for k in range(4)])
        if i % 3 == 0:
            api.set_student_reserve_group(sid, "uu_tien")
    return "200 em · suất dự trữ = TOÀN BỘ sức chứa"


def kb_nap_theo_dot(api, dot=5, moi_dot=400, n_clb=20):
    """Nạp → chạy → nạp thêm → chạy lại, NĂM đợt.

    Đây là kịch bản quan trọng nhất tệp này: đường chèn ngẫu nhiên cho
    học sinh vào sau (`chen_stb_cho_hoc_sinh_moi`) mới viết, và mới chỉ
    chạy ở quy mô 30 em. Ở đây nó chạy tới 2000 em qua 5 lần khoá.

    Kiểm sau mỗi đợt: thứ tự TƯƠNG ĐỐI của các em cũ giữ nguyên tuyệt đối.
    """
    import sqlite3
    for j in range(n_clb):
        api.create_or_update_club("c%02d" % j, "CLB %d" % j, 25, 0, "")

    def bo_so():
        conn = sqlite3.connect(api.db_path)
        try:
            return dict(conn.execute(
                "SELECT student_id, stb_number FROM students "
                "WHERE stb_number IS NOT NULL"))
        finally:
            conn.close()

    truoc = {}
    for d in range(dot):
        for i in range(d * moi_dot, (d + 1) * moi_dot):
            sid = "HS%05d" % i
            api.create_student_if_missing(sid, "Em %d" % i)
            api.submit_preferences(sid, ["c%02d" % ((i + k) % n_clb) for k in range(6)])
        kq = api.run_pipeline(seed=42)
        if not kq["ok"]:
            raise AssertionError("đợt %d: run_pipeline thất bại %r" % (d + 1, kq["errors"]))
        sau = bo_so()
        if truoc:
            cu = sorted(truoc)
            if sorted(cu, key=lambda s: truoc[s]) != sorted(cu, key=lambda s: sau[s]):
                raise AssertionError("đợt %d ĐẢO thứ tự tương đối của em cũ" % (d + 1))
        truoc = sau
    return "%d đợt × %d em = %d em, kiểm thứ tự em cũ sau mỗi đợt" % (
        dot, moi_dot, dot * moi_dot)


def kb_chuoi_hiem(api):
    """Tên có dấu, ký tự điều khiển, chuỗi rất dài, chuỗi trông như công thức."""
    api.create_or_update_club("clb_a", "CLB Nguyễn Ðừc — “trích dẫn”", 5, 0, "")
    ten_hiem = [
        "Nguyễn Văn Ðạt",
        "=1+1",                       # Excel hiểu thành công thức
        "@SUM(A1:A9)",
        "Trần Thị " + "A" * 300,      # rất dài
        "Lê\tMinh\nCường",            # tab + xuống dòng
        "☃ ⚡ 学生",                    # ngoài BMP thông dụng
    ]
    for i, ten in enumerate(ten_hiem):
        sid = "HS%02d" % i
        api.create_student_if_missing(sid, ten)
        api.submit_preferences(sid, ["clb_a"])
    return "6 tên hiểm: công thức Excel, tab/xuống dòng, 300 ký tự, emoji"


KICH_BAN = [
    ("Một nguyện vọng duy nhất", kb_mot_nguyen_vong_duy_nhat),
    ("Sức chứa 1 ở mọi CLB", kb_suc_chua_mot),
    ("Cả trường hoà điểm", kb_ca_truong_hoa_diem),
    ("Toàn bộ Tầng 2", kb_toan_bo_tang_2),
    ("Rỗng và lẻ loi", kb_rong_va_le_loi),
    ("Dự trữ = toàn bộ sức chứa", kb_du_tru_bang_suc_chua),
    ("Nạp theo 5 đợt", kb_nap_theo_dot),
    ("Chuỗi hiểm", kb_chuoi_hiem),
]


def main() -> None:
    print("THỬ TẢI NGHỊCH CẢNH — dữ liệu có hình thù lạ, không phải to hơn")
    print("=" * 78)
    print("%-28s %8s %7s %6s %9s  %s" % (
        "kịch bản", "giây", "học sinh", "vòng", "xếp được", "kết quả"))
    print("-" * 78)

    hong = []
    for ten, ham in KICH_BAN:
        d = tempfile.mkdtemp()
        t0 = time.time()
        try:
            api = PipelineAPI(os.path.join(d, "app.db"))
            mo_ta = ham(api)
            if ten != "Nạp theo 5 đợt":       # kịch bản đó tự chạy pipeline rồi
                kq = api.run_pipeline(seed=42)
                if not kq["ok"]:
                    raise AssertionError("run_pipeline thất bại: %r" % (kq["errors"],))
            res, n_hs = _kiem_ket_qua(api, ten)
            n_xep = sum(1 for v in res.assignment.values() if v)
            print("%-28s %8.2f %7d %6d %9d  ĐẠT" % (
                ten, time.time() - t0, n_hs, res.rounds_run, n_xep))
            print("%-28s   %s" % ("", mo_ta))
        except Exception as e:
            hong.append((ten, e))
            print("%-28s %8.2f %7s %6s %9s  *** HỎNG ***" % (
                ten, time.time() - t0, "—", "—", "—"))
            print("      " + "\n      ".join(traceback.format_exc().splitlines()[-3:]))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    print("=" * 78)
    if hong:
        print("CÓ %d/%d KỊCH BẢN HỎNG:" % (len(hong), len(KICH_BAN)))
        for ten, e in hong:
            print("   %s: %s" % (ten, e))
        raise SystemExit(1)
    print("Cả %d kịch bản ĐẠT: không ném lỗi, 0 cặp phá vỡ, số vòng dưới trần %d."
          % (len(KICH_BAN), TRAN_VONG))
    print("Mọi dữ liệu là MÔ PHỎNG, dựng trong thư mục tạm và đã xoá.")


if __name__ == "__main__":
    main()
