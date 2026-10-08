# -*- coding: utf-8 -*-
"""Sinh bộ dữ liệu đầu vào mẫu từ MỘT bảng khai báo duy nhất.

Ba tệp CSV đi ra từ cùng một nguồn nên KHÔNG THỂ lệch nhau — đó là cả lý do
tệp này tồn tại thay vì ba tệp gõ tay. Gõ tay thì sớm muộn cũng có một mã câu
lạc bộ trong tệp nguyện vọng không còn tồn tại trong danh sách, và không ai
thấy cho tới lúc nhập vào phần mềm.

Trước khi ghi, đoạn mã soát chín điều và DỪNG HẲN nếu có điều nào sai. Nó
không tự sửa: sửa giúp là giấu mất chỗ sai trong bảng khai báo.

Cách dùng: sửa hai bảng CLB và HS ở dưới, rồi chạy

    python tao_bo_mau.py
"""
import csv, io, os

THU_MUC = os.path.dirname(os.path.abspath(__file__))

# (club_id, ten, buoi, suc chua, chi tieu du tru, nhom du tru)
CLB = [
    ("clb_bongro",   "CLB Bóng rổ",        "thu_2", 6, 0, ""),
    ("clb_vanhoc",   "CLB Văn học",        "thu_2", 5, 2, "chinh_sach"),
    ("clb_tinhoc",   "CLB Tin học",        "thu_2", 4, 0, ""),
    ("clb_mythuat",  "CLB Mỹ thuật",       "thu_4", 5, 1, "khoi_10"),
    ("clb_robotics", "CLB Robotics",       "thu_4", 4, 0, ""),
    ("clb_nauan",    "CLB Nấu ăn",         "thu_4", 6, 0, ""),
    ("clb_tienganh", "CLB Tiếng Anh",      "thu_6", 5, 2, "chinh_sach"),
    ("clb_lamvuon",  "CLB Làm vườn",       "thu_6", 6, 0, ""),
    ("clb_covua",    "CLB Cờ vua",         "thu_6", 4, 0, ""),
]
BUOI = ["thu_2", "thu_4", "thu_6"]
# CLB co thi dau vao — dung mot CLB moi buoi cho de giai thich
CO_THI = {"clb_tinhoc", "clb_robotics", "clb_tienganh"}

# student_id, ho ten, nhom du tru, {buoi: [nguyen vong theo thu tu]},
# {club_id: diem thi}
HS = [
    ("HS001", "Nguyễn Văn An",    "",            {"thu_2": ["clb_tinhoc", "clb_bongro"], "thu_4": ["clb_robotics", "clb_nauan"], "thu_6": ["clb_tienganh", "clb_covua"]}, {"clb_tinhoc": "9,5", "clb_robotics": "8,0", "clb_tienganh": "7,5"}),
    ("HS002", "Trần Thị Bình",    "chinh_sach",  {"thu_2": ["clb_vanhoc", "clb_tinhoc"], "thu_4": ["clb_mythuat"], "thu_6": ["clb_tienganh"]}, {"clb_tinhoc": "6,0", "clb_tienganh": "8,5"}),
    ("HS003", "Lê Minh Cường",    "",            {"thu_2": ["clb_bongro"], "thu_4": ["clb_nauan", "clb_mythuat"], "thu_6": ["clb_lamvuon"]}, {}),
    ("HS004", "Phạm Thu Dung",    "khoi_10",     {"thu_2": ["clb_vanhoc", "clb_bongro"], "thu_4": ["clb_mythuat", "clb_robotics"], "thu_6": ["clb_covua"]}, {"clb_robotics": "7,0"}),
    ("HS005", "Hoàng Gia Em",     "",            {"thu_2": ["clb_tinhoc"], "thu_4": [], "thu_6": ["clb_lamvuon", "clb_covua"]}, {"clb_tinhoc": "8,0"}),
    ("HS006", "Vũ Ngọc Giang",    "",            {"thu_2": ["clb_bongro", "clb_vanhoc"], "thu_4": ["clb_robotics"], "thu_6": ["clb_tienganh", "clb_lamvuon"]}, {"clb_robotics": "9,0", "clb_tienganh": "6,5"}),
    ("HS007", "Đỗ Khánh Hà",      "chinh_sach",  {"thu_2": ["clb_vanhoc"], "thu_4": ["clb_nauan"], "thu_6": ["clb_tienganh", "clb_covua"]}, {"clb_tienganh": "7,0"}),
    ("HS008", "Bùi Quang Huy",    "",            {"thu_2": ["clb_tinhoc", "clb_bongro"], "thu_4": ["clb_robotics", "clb_mythuat"], "thu_6": ["clb_covua"]}, {"clb_tinhoc": "7,5", "clb_robotics": "6,0"}),
    ("HS009", "Ngô Bảo Khanh",    "",            {"thu_2": ["clb_bongro"], "thu_4": ["clb_nauan", "clb_robotics"], "thu_6": ["clb_lamvuon"]}, {"clb_robotics": "5,5"}),
    ("HS010", "Dương Thị Lan",    "khoi_10",     {"thu_2": ["clb_vanhoc", "clb_tinhoc"], "thu_4": ["clb_mythuat"], "thu_6": ["clb_tienganh"]}, {"clb_tinhoc": "8,5", "clb_tienganh": "9,0"}),
    ("HS011", "Lý Hoàng Minh",    "",            {"thu_2": ["clb_tinhoc", "clb_vanhoc"], "thu_4": ["clb_robotics"], "thu_6": ["clb_covua", "clb_lamvuon"]}, {"clb_tinhoc": "6,5", "clb_robotics": "8,5"}),
    ("HS012", "Hồ Thanh Nga",     "",            {"thu_2": ["clb_bongro", "clb_tinhoc"], "thu_4": ["clb_nauan"], "thu_6": ["clb_lamvuon"]}, {"clb_tinhoc": "5,0"}),
    ("HS013", "Đặng Gia Phúc",    "chinh_sach",  {"thu_2": ["clb_vanhoc", "clb_bongro"], "thu_4": ["clb_mythuat", "clb_nauan"], "thu_6": ["clb_tienganh"]}, {"clb_tienganh": "6,0"}),
    ("HS014", "Phan Minh Quân",   "",            {"thu_2": ["clb_bongro"], "thu_4": ["clb_robotics", "clb_nauan"], "thu_6": ["clb_covua"]}, {"clb_robotics": "7,5"}),
    ("HS015", "Trịnh Thu Sương",  "",            {"thu_2": ["clb_tinhoc"], "thu_4": ["clb_mythuat", "clb_nauan"], "thu_6": ["clb_lamvuon", "clb_tienganh"]}, {"clb_tinhoc": "9,0", "clb_tienganh": "5,5"}),
    ("HS016", "Mai Anh Tuấn",     "",            {"thu_2": ["clb_bongro", "clb_vanhoc"], "thu_4": ["clb_nauan"], "thu_6": ["clb_covua", "clb_lamvuon"]}, {}),
    ("HS017", "Chu Diệu Uyên",    "khoi_10",     {"thu_2": ["clb_vanhoc"], "thu_4": ["clb_mythuat", "clb_robotics"], "thu_6": ["clb_tienganh", "clb_lamvuon"]}, {"clb_robotics": "6,5", "clb_tienganh": "8,0"}),
    ("HS018", "Tạ Quốc Việt",     "",            {"thu_2": ["clb_tinhoc", "clb_bongro"], "thu_4": ["clb_robotics"], "thu_6": ["clb_covua"]}, {"clb_tinhoc": "4,5", "clb_robotics": "9,5"}),
    ("HS019", "Cao Thị Xuân",     "",            {"thu_2": ["clb_vanhoc", "clb_tinhoc"], "thu_4": ["clb_nauan", "clb_mythuat"], "thu_6": ["clb_lamvuon"]}, {"clb_tinhoc": "7,0"}),
    ("HS020", "Lâm Hoài Yến",     "chinh_sach",  {"thu_2": ["clb_vanhoc"], "thu_4": ["clb_mythuat"], "thu_6": ["clb_tienganh", "clb_covua"]}, {"clb_tienganh": "7,5"}),
    ("HS021", "Đinh Bá Long",     "",            {"thu_2": [], "thu_4": ["clb_robotics", "clb_nauan"], "thu_6": ["clb_lamvuon", "clb_covua"]}, {"clb_robotics": "5,0"}),
    ("HS022", "Võ Kim Ngân",      "",            {"thu_2": ["clb_bongro", "clb_tinhoc"], "thu_4": ["clb_nauan"], "thu_6": ["clb_covua"]}, {"clb_tinhoc": "8,5"}),
    ("HS023", "Hà Đức Thắng",     "khoi_10",     {"thu_2": ["clb_tinhoc", "clb_vanhoc"], "thu_4": ["clb_mythuat", "clb_robotics"], "thu_6": ["clb_lamvuon"]}, {"clb_tinhoc": "6,0", "clb_robotics": "7,0"}),
    ("HS024", "Nguyễn Thảo Vy",   "",            {"thu_2": ["clb_bongro", "clb_vanhoc"], "thu_4": ["clb_nauan", "clb_mythuat"], "thu_6": ["clb_tienganh", "clb_covua"]}, {"clb_tienganh": "6,5"}),
]

# ---------------- SOAT TRUOC KHI GHI ----------------
ma_clb = {c[0] for c in CLB}
buoi_cua = {c[0]: c[2] for c in CLB}
loi = []
for sid, ten, nhom, nv, diem in HS:
    for b, ds in nv.items():
        if len(ds) != len(set(ds)):
            loi.append("%s: %s co nguyen vong trung" % (sid, b))
        for cid in ds:
            if cid not in ma_clb:
                loi.append("%s: ma CLB la '%s'" % (sid, cid))
            elif buoi_cua[cid] != b:
                loi.append("%s: %s nam o cot %s nhung sinh hoat %s"
                           % (sid, cid, b, buoi_cua[cid]))
        if len(ds) > 10:
            loi.append("%s: %s vuot tran 10 nguyen vong" % (sid, b))
    theo_buoi_thi = {}
    for cid in diem:
        if cid not in ma_clb:
            loi.append("%s: diem cho ma la '%s'" % (sid, cid))
            continue
        if cid not in CO_THI:
            loi.append("%s: cham diem cho %s ma CLB do khong thi" % (sid, cid))
        theo_buoi_thi.setdefault(buoi_cua[cid], []).append(cid)
        # Diem chi co nghia neu em CO khai nguyen vong CLB do
        if cid not in nv.get(buoi_cua[cid], []):
            loi.append("%s: thi %s nhung khong khai nguyen vong CLB do" % (sid, cid))
    for b, ds in theo_buoi_thi.items():
        if len(ds) > 5:
            loi.append("%s: %s vuot tran 5 CLB du thi" % (sid, b))
# Ma hoc sinh phai duy nhat — day la khoa chinh
ma_hs = [h[0] for h in HS]
if len(ma_hs) != len(set(ma_hs)):
    loi.append("co ma hoc sinh bi trung")

if loi:
    raise SystemExit(
        "BẢNG KHAI BÁO SAI — không ghi tệp nào:\n  " + "\n  ".join(loi))

# ---------------- GHI BA TEP ----------------
def ghi(ten, header, dong):
    p = os.path.join(THU_MUC, ten)
    with io.open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(dong)
    return p

ghi("01_danh_sach_CLB.csv",
    ["club_id", "name", "capacity", "reserve_capacity", "reserve_group", "buoi"],
    [[c[0], c[1], c[3], c[4], c[5], c[2]] for c in CLB])

# File 02: dang RONG. Phan mem ghep `test_club_N` voi `score_N` theo CON SO
# trong ten cot, KHONG theo vi tri — nen chi can dung so cot bang so CLB
# nhieu nhat MOT em du thi, khong phai 5 x so buoi. Mot bang 33 cot gan nhu
# trong rong khong day duoc ai dieu gi.
N_THI = max(len(d) for *_, d in HS)
head2 = ["student_id", "name", "reserve_group"]
for i in range(1, N_THI + 1):
    head2 += ["test_club_%d" % i, "score_%d" % i]
dong2 = []
for sid, ten, nhom, nv, diem in HS:
    o = [sid, ten, nhom]
    ds = sorted(diem, key=lambda c: (BUOI.index(buoi_cua[c]), c))
    for i in range(N_THI):
        o += [ds[i], diem[ds[i]]] if i < len(ds) else ["", ""]
    dong2.append(o)
ghi("02_chon_CLB_muon_thi.csv", head2, dong2)

# File 03: moi buoi mot bo cot <buoi>_pref_N
MAX_NV = max(len(ds) for _, _, _, nv, _ in HS for ds in nv.values())
head3 = ["student_id", "name", "reserve_group"]
for b in BUOI:
    head3 += ["%s_pref_%d" % (b, i) for i in range(1, MAX_NV + 1)]
dong3 = []
for sid, ten, nhom, nv, diem in HS:
    o = [sid, ten, nhom]
    for b in BUOI:
        ds = nv.get(b, [])
        o += [ds[i] if i < len(ds) else "" for i in range(MAX_NV)]
    dong3.append(o)
ghi("03_xep_hang_nguyen_vong.csv", head3, dong3)

print("OK — %d CLB / %d buoi / %d hoc sinh / toi da %d nguyen vong moi buoi"
      % (len(CLB), len(BUOI), len(HS), MAX_NV))
print("So o diem da dien:", sum(len(d) for *_, d in HS))
