"""Danh sách nguyện vọng ngắn thì thiệt tới đâu?

    ./.venv/bin/python du_lieu_test/do_do_dai_nguyen_vong.py

THÍ NGHIỆM CÓ ĐỐI CHỨNG: cùng một bộ dữ liệu, cùng điểm, cùng chỉ tiêu —
chỉ CẮT NGẮN danh sách nguyện vọng của mọi em xuống k, với k = 1..6.

CÂU HỎI
Sau khi đo ảnh hưởng của seed (`do_anh_huong_seed.py`), có 3 em mà chuyện có
suất hay không phụ thuộc bốc thăm, và một em trong đó chỉ đăng ký 2 nguyện
vọng. Từ đó nảy ra phỏng đoán "danh sách càng ngắn càng dễ bấp bênh". Ba ca
thì chưa kết luận được gì, nên đo hẳn.

CẦN PHÂN BIỆT HAI THỨ, VÌ CHÚNG KHÔNG ĐI CÙNG NHAU
  * CHƯA ĐƯỢC XẾP  — em không có suất nào
  * BẤP BÊNH       — em có suất hay không phụ thuộc vào seed

Số đo cho thấy danh sách dài hơn giảm rất mạnh cái thứ nhất, nhưng KHÔNG có
quy luật gì với cái thứ hai. Phỏng đoán ban đầu chỉ đúng một nửa.

MỘT GIỚI HẠN PHẢI NÓI RÕ
Thí nghiệm này CẮT BỚT nguyện vọng của những em vốn đã khai đủ — tức nó đo
"em mất gì khi KHÔNG khai hết những CLB mình vẫn chấp nhận". Nó KHÔNG chứng
minh rằng bắt em khai thêm CLB em KHÔNG muốn thì có lợi: khai thêm CLB không
muốn thì em có thể bị xếp đúng vào đó, và với em như thế còn tệ hơn không có
suất.
"""
import collections, os, shutil, sys, tempfile
sys.path.insert(0, "/home/user/truong/rbda-kiosk")
import rbda_priority_pipeline as loi
from api import PipelineAPI
GOC = "/home/user/truong/rbda-kiosk/du_lieu_test"
F = ["bo_sach/SACH_01_danh_sach_CLB.csv","bo_sach/SACH_02_chon_CLB_muon_thi.csv","bo_sach/SACH_03_xep_hang_nguyen_vong.csv"]
N_SEED = 50
tm = tempfile.mkdtemp()
try:
    db = os.path.join(tm,"app.db"); api = PipelineAPI(db)
    for rel in F: api.import_csv_auto(open(os.path.join(GOC,rel),encoding="utf-8-sig").read())
    students, clubs, diem, ung_vien_goc, nv_goc, _ = loi.load_from_sqlite(db)
    fn = loi.default_reserve_eligible_fn(students, clubs)
    print("Bộ sạch: %d em / %d CLB. Mỗi em có %d nguyện vọng."
          % (len(students), len(clubs), max(len(v) for v in nv_goc.values())))
    print()
    print("%-12s %14s %14s %16s" % ("Cắt còn", "chưa xếp (TB)", "chưa xếp (max)", "em bấp bênh"))
    print("-"*62)
    for k in range(1, 7):
        nv = {sid: v[:k] for sid, v in nv_goc.items()}
        # ung_vien phai dung lai: em thi CLB nao van la ung vien, cong em xep NV vao do
        uv = {cid: [] for cid in clubs}
        for cid, ds in ung_vien_goc.items():
            for sid in ds:
                if diem.get(cid,{}).get(sid) is not None: uv[cid].append(sid)
        for sid, ranked in nv.items():
            for cid in ranked:
                if cid in uv and sid not in uv[cid]: uv[cid].append(sid)
        chua = []; co_suat = collections.Counter()
        for s in range(1, N_SEED+1):
            stb = loi.generate_stb_lottery(sorted(students), s)
            kq = loi.run_rbda(students, clubs, diem, uv, nv, stb, fn)
            n = sum(1 for sid in students if not kq.assignment.get(sid))
            chua.append(n)
            for sid in students:
                if kq.assignment.get(sid): co_suat[sid] += 1
        bb = sum(1 for sid in students if 0 < co_suat[sid] < N_SEED)
        print("%-12s %14.1f %14d %11d (%.1f%%)"
              % ("%d nguyện vọng" % k, sum(chua)/len(chua), max(chua),
                 bb, 100*bb/len(students)))
finally:
    shutil.rmtree(tm, ignore_errors=True)
