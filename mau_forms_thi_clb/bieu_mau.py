"""Phần dùng chung của mẫu Microsoft Forms "Đăng ký CLB và thi tuyển".

Một nguồn duy nhất — `de_thi.json` — sinh ra mọi thứ: tệp Quick Import,
bảng cài đặt Forms, tệp xuất mẫu, và là đáp án để chấm lại bài. Tên câu
hỏi cũng chỉ được dựng ở ĐÂY: biểu mẫu và bộ chuyển đổi cùng gọi một hàm,
nên không thể lệch nhau.

Mỗi câu hỏi mở đầu bằng một MÃ trong ngoặc vuông. Forms lấy nguyên văn câu
hỏi làm tên cột khi xuất Excel, nên bộ chuyển đổi chỉ cần đọc phần trong
ngoặc — sửa lời câu hỏi trên Forms không làm hỏng việc đọc tệp.

    [student_id]      mã học sinh
    [name]            họ tên
    [thu_2]           câu Ranking nguyện vọng của buổi thu_2
    [thi-clb_covua]   câu cổng "Em có dự thi CLB Cờ vua không?"
    [clb_covua-3]     câu 3 trong đề thi của CLB Cờ vua
"""

import json
import os
import re

THU_MUC = os.path.dirname(os.path.abspath(__file__))
DE_THI_MAC_DINH = os.path.join(THU_MUC, "de_thi.json")

# Trần của phần mềm (xem BO_CAU_HOI_FORMS.md mục 2). Để biểu mẫu vượt trần
# là dựng sẵn cái bẫy: học sinh điền hợp lệ theo Forms mà phần mềm không nhập.
TRAN_CLB_MOI_BUOI = 10
TRAN_THI_MOI_BUOI = 5

CO = "Có, em làm bài thi ngay bây giờ"
KHONG = "Không"

_MA_CLB = re.compile(r"^[A-Za-z0-9_]+$")
# Forms đôi khi giữ số thứ tự "3." của Quick Import trong tên câu hỏi.
_MA_CAU = re.compile(r"^\s*(?:\d+[.)]\s*)?\[([^\]]+)\]")
_MA_TRONG_LUA_CHON = re.compile(r"\(([A-Za-z0-9_]+)\)\s*$")


class LoiDeThi(ValueError):
    """de_thi.json sai — không sinh gì cả."""


def doc_de_thi(duong_dan=DE_THI_MAC_DINH):
    with open(duong_dan, encoding="utf-8") as f:
        de = json.load(f)
    soat_de_thi(de)
    return de


def soat_de_thi(de):
    """Ném LoiDeThi liệt kê MỌI chỗ sai, không dừng ở chỗ đầu tiên."""
    loi = []
    ma_buoi = [b["ma"] for b in de.get("buoi", [])]
    if not ma_buoi:
        loi.append("chưa khai buổi nào")
    if len(set(ma_buoi)) != len(ma_buoi):
        loi.append("mã buổi bị trùng")
    diem = de.get("diem_moi_cau")
    if not isinstance(diem, (int, float)) or diem <= 0:
        loi.append("diem_moi_cau phải là số dương")

    thay = set()
    for clb in de.get("cau_lac_bo", []):
        ma = clb.get("club_id", "")
        if not _MA_CLB.match(ma):
            loi.append("club_id %r chỉ được có chữ không dấu, số, gạch dưới" % ma)
        if ma in thay:
            loi.append("club_id %r bị trùng" % ma)
        thay.add(ma)
        if clb.get("buoi") not in ma_buoi:
            loi.append("%s: buổi %r không có trong danh sách buổi" % (ma, clb.get("buoi")))
        if ";" in clb.get("name", ""):
            # Forms nối các lựa chọn Ranking bằng dấu chấm phẩy khi xuất.
            loi.append("%s: tên CLB không được chứa dấu ;" % ma)
        cap, du_tru = clb.get("capacity", 0), clb.get("reserve_capacity", 0)
        if not isinstance(cap, int) or cap <= 0:
            loi.append("%s: capacity phải là số nguyên > 0" % ma)
        elif du_tru > cap:
            loi.append("%s: reserve_capacity lớn hơn capacity" % ma)
        if du_tru and not clb.get("reserve_group"):
            loi.append("%s: có suất dự trữ thì phải có reserve_group" % ma)
        for i, cau in enumerate(clb.get("de_thi", []), 1):
            lc = cau.get("lua_chon", [])
            if len(lc) < 2:
                loi.append("%s câu %d: cần ít nhất 2 lựa chọn" % (ma, i))
            if len(set(_chuan(x) for x in lc)) != len(lc):
                # Chấm theo NỘI DUNG lựa chọn — hai lựa chọn giống nhau thì
                # không phân biệt được em chọn cái nào.
                loi.append("%s câu %d: có lựa chọn trùng nhau" % (ma, i))
            if not isinstance(cau.get("dap_an"), int) or not 0 <= cau["dap_an"] < len(lc):
                loi.append("%s câu %d: dap_an phải là số thứ tự lựa chọn, đếm từ 0" % (ma, i))

    for b in ma_buoi:
        o_buoi = [c for c in de.get("cau_lac_bo", []) if c.get("buoi") == b]
        if len(o_buoi) > TRAN_CLB_MOI_BUOI:
            loi.append("buổi %s có %d CLB, vượt trần %d của câu Ranking"
                       % (b, len(o_buoi), TRAN_CLB_MOI_BUOI))
        co_thi = [c for c in o_buoi if c.get("de_thi")]
        if len(co_thi) > TRAN_THI_MOI_BUOI:
            loi.append("buổi %s có %d CLB tổ chức thi, vượt trần %d"
                       % (b, len(co_thi), TRAN_THI_MOI_BUOI))
    if loi:
        raise LoiDeThi("de_thi.json sai:\n  - " + "\n  - ".join(loi))


def _chuan(s):
    return " ".join(str(s or "").split()).casefold()


def ten_buoi(de, ma):
    return next(b["ten"] for b in de["buoi"] if b["ma"] == ma)


def clb_cua_buoi(de, ma_buoi):
    return [c for c in de["cau_lac_bo"] if c["buoi"] == ma_buoi]


def clb_co_thi(de):
    return [c for c in de["cau_lac_bo"] if c["de_thi"]]


def lua_chon_clb(clb):
    """Ghi cả tên lẫn mã — người xử lý không phải tra ngược tên ra mã."""
    return "%s (%s)" % (clb["name"], clb["club_id"])


# ---- Tên câu hỏi: nguồn duy nhất cho cả biểu mẫu lẫn bộ chuyển đổi ----

def cau_ma_hoc_sinh():
    return "[student_id] Mã học sinh của em (ghi đúng như trên thẻ học sinh)"


def cau_ho_ten():
    return "[name] Họ và tên của em"


def cau_xep_hang(de, ma_buoi):
    return ("[%s] %s — em muốn vào câu lạc bộ nào? Kéo thả, câu lạc bộ em "
            "thích nhất lên đầu. Bận buổi này thì bỏ qua câu này."
            % (ma_buoi, ten_buoi(de, ma_buoi)))


def cau_cong_thi(de, clb):
    return ("[thi-%s] %s · Em có dự thi %s không? Chỉ chọn Có nếu em đã xếp "
            "câu lạc bộ này ở câu nguyện vọng %s."
            % (clb["club_id"], ten_buoi(de, clb["buoi"]), clb["name"],
               ten_buoi(de, clb["buoi"])))


def cau_de_thi(clb, so_thu_tu):
    cau = clb["de_thi"][so_thu_tu - 1]["cau"]
    return "[%s-%d] %s" % (clb["club_id"], so_thu_tu, cau)


def ma_cua_cau(tieu_de):
    """'[thu_2] Thứ Hai — …' -> 'thu_2'. Không phải câu của mẫu -> None."""
    m = _MA_CAU.match(str(tieu_de or ""))
    return m.group(1).strip() if m else None


def ma_trong_lua_chon(chu):
    """'CLB Cờ vua (clb_covua)' -> 'clb_covua'."""
    m = _MA_TRONG_LUA_CHON.search(str(chu or "").strip())
    return m.group(1) if m else None


def cac_phan(de):
    """Bố cục biểu mẫu: [(tên phần, [(tiêu đề câu, loại, lựa chọn, bắt buộc)])].

    Loại: 'text', 'ranking', 'choice'. Thứ tự phần CHÍNH LÀ luồng mặc định
    của Forms: làm xong đề thi CLB X thì tự sang câu cổng của CLB kế tiếp,
    nên chỉ đáp án "Không" của câu cổng là cần rẽ nhánh.
    """
    phan = [("Thông tin học sinh", [
        (cau_ma_hoc_sinh(), "text", [], True),
        (cau_ho_ten(), "text", [], True),
    ])]
    for b in de["buoi"]:
        o_buoi = clb_cua_buoi(de, b["ma"])
        # Ranking KHÔNG bắt buộc: bỏ trống = em bận buổi đó. Đặt bắt buộc
        # là ép em khai một buổi em không rảnh (BO_CAU_HOI_FORMS.md mục 4).
        phan.append(("%s · Nguyện vọng" % b["ten"], [
            (cau_xep_hang(de, b["ma"]), "ranking",
             [lua_chon_clb(c) for c in o_buoi], False),
        ]))
        for clb in o_buoi:
            if not clb["de_thi"]:
                continue
            phan.append(("%s · Dự thi %s" % (b["ten"], clb["name"]), [
                (cau_cong_thi(de, clb), "choice", [CO, KHONG], True),
            ]))
            phan.append(("%s · Đề thi %s" % (b["ten"], clb["name"]), [
                (cau_de_thi(clb, i), "choice", cau["lua_chon"], True)
                for i, cau in enumerate(clb["de_thi"], 1)
            ]))
    return phan


def re_nhanh(de):
    """[(câu cổng, đáp án 'Không' đi tới đâu)] — đúng những gì phải cài tay."""
    ten_phan = [p[0] for p in cac_phan(de)]
    kq = []
    for clb in clb_co_thi(de):
        de_phan = "%s · Đề thi %s" % (ten_buoi(de, clb["buoi"]), clb["name"])
        i = ten_phan.index(de_phan)
        toi = ten_phan[i + 1] if i + 1 < len(ten_phan) else "End of the form"
        kq.append((clb, toi))
    return kq


def cham_bai(de, clb, tra_loi):
    """tra_loi: {số thứ tự câu: nội dung em chọn}. Trả (điểm, [đúng/sai])."""
    diem_cau = de["diem_moi_cau"]
    dung = []
    for i, cau in enumerate(clb["de_thi"], 1):
        dap_an = cau["lua_chon"][cau["dap_an"]]
        dung.append(_chuan(tra_loi.get(i)) == _chuan(dap_an))
    return diem_cau * sum(dung), dung


def diem_toi_da(de, clb):
    return de["diem_moi_cau"] * len(clb["de_thi"])


def ghi_so(x):
    """8.0 -> '8', 9.5 -> '9.5' — đúng dạng phần mềm đọc."""
    x = float(x)
    return str(int(x)) if x.is_integer() else ("%g" % x)
