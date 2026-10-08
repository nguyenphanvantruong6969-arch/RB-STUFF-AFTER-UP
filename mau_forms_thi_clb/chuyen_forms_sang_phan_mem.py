"""Chuyển tệp Excel Microsoft Forms xuất ra thành Sổ nhập CLB + bảng điểm.

    python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py KET_QUA_FORMS.xlsx --ra ./nap

Ghi ra thư mục --ra:

    SO_NHAP_CLB.xlsx    MỘT tệp kéo thẳng vào phần mềm: sheet "1. CLB" dựng từ
                        de_thi.json, sheet "2. Học sinh" có nguyện vọng các buổi
                        và điểm đã chấm ngay cạnh CLB em thi
    BANG_DIEM.xlsx      bảng điểm, chi tiết đúng/sai, thống kê đề, cảnh báo

Điểm được CHẤM LẠI từ đáp án trong de_thi.json, không lấy cột "Points" của
Forms. Có cột Points thì đem ra đối chiếu: lệch nhau nghĩa là đáp án trên
Forms và trong de_thi.json không còn khớp, và phải biết điều đó TRƯỚC khi
dùng điểm để xét tuyển.

Tệp xuất thiếu hẳn một câu của mẫu thì dừng, không ghi tệp nào. Một ô sai
lẻ (mã CLB lạ, thi CLB chưa xếp nguyện vọng…) thì bỏ riêng ô đó và báo
đích danh dòng — đúng cách phần mềm xử lý khi nạp.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bieu_mau as bm  # noqa: E402
import so_nhap  # noqa: E402

TIEN_TO_DIEM = "Points - "
TIEN_TO_NHAN_XET = "Feedback - "


class LoiTepXuat(ValueError):
    """Tệp xuất không dùng được — không ghi tệp nào."""


def _o(gia_tri):
    if gia_tri is None:
        return ""
    if isinstance(gia_tri, float) and gia_tri.is_integer():
        return str(int(gia_tri))
    return str(gia_tri).strip()


def doc_tep_xuat(duong_dan):
    """Trả về (tiêu đề, các dòng) của sheet đầu — Forms chỉ xuất một sheet."""
    import openpyxl

    wb = openpyxl.load_workbook(duong_dan, read_only=True, data_only=True)
    ws = wb[wb.sheetnames[0]]
    dong = [[_o(x) for x in r] for r in ws.iter_rows(values_only=True)]
    wb.close()
    if not dong:
        raise LoiTepXuat("tệp trống")
    return dong[0], dong[1:]


def _ban_do_cot(de, tieu_de):
    """{mã câu: [chỉ số cột]} và {mã câu: chỉ số cột Points}."""
    cot, cot_diem, la = {}, {}, []
    for i, h in enumerate(tieu_de):
        if h.startswith(TIEN_TO_NHAN_XET):
            continue
        if h.startswith(TIEN_TO_DIEM):
            ma = bm.ma_cua_cau(h[len(TIEN_TO_DIEM):])
            if ma:
                cot_diem[ma] = i
            continue
        ma = bm.ma_cua_cau(h)
        if ma:
            # Nhiều cột cùng mã (Ranking tách mỗi vị trí một cột) thì nối lại
            # theo thứ tự cột.
            cot.setdefault(ma, []).append(i)

    can = ["student_id", "name"] + [b["ma"] for b in de["buoi"]]
    for clb in bm.clb_co_thi(de):
        can.append("thi-" + clb["club_id"])
        can += ["%s-%d" % (clb["club_id"], i) for i in range(1, len(clb["de_thi"]) + 1)]
    thieu = [m for m in can if m not in cot]
    if thieu:
        raise LoiTepXuat(
            "tệp xuất thiếu %d câu của mẫu (mã: %s). Câu hỏi trên Forms phải "
            "giữ nguyên phần [mã] ở đầu." % (len(thieu), ", ".join(thieu)))
    la = sorted(set(cot) - set(can))
    return cot, cot_diem, la


def _gia_tri(dong, cac_cot):
    return ";".join(dong[i] for i in cac_cot if i < len(dong) and dong[i])


def phan_tich(de, tieu_de, cac_dong):
    """Đọc toàn bộ phản hồi. Không ghi gì — chỉ trả kết quả và cảnh báo."""
    cot, cot_diem, la = _ban_do_cot(de, tieu_de)
    canh_bao = []
    if la:
        canh_bao.append(("", "", "bỏ qua %d câu không thuộc mẫu: %s"
                         % (len(la), ", ".join(la))))

    theo_ma = {c["club_id"]: c for c in de["cau_lac_bo"]}
    theo_ten = {bm._chuan(c["name"]): c for c in de["cau_lac_bo"]}
    hoc_sinh = {}  # student_id -> bản ghi của phiếu ĐẦU TIÊN

    for so_dong, dong in enumerate(cac_dong, 2):
        if not any(dong):
            continue
        sid = _gia_tri(dong, cot["student_id"])
        if not sid:
            canh_bao.append((so_dong, "", "phiếu không có mã học sinh — bỏ cả phiếu"))
            continue

        def bao(noi_dung, so_dong=so_dong, sid=sid):
            canh_bao.append((so_dong, sid, noi_dung))

        nguyen_vong = {}
        for b in de["buoi"]:
            ds = []
            for muc in _gia_tri(dong, cot[b["ma"]]).split(";"):
                muc = muc.strip()
                if not muc:
                    continue
                clb = theo_ma.get(bm.ma_trong_lua_chon(muc)) or theo_ten.get(bm._chuan(muc))
                if clb is None:
                    bao("%s: lựa chọn %r không phải CLB nào trong de_thi.json — bỏ ô này"
                        % (b["ma"], muc))
                elif clb["buoi"] != b["ma"]:
                    bao("%s: %s sinh hoạt %s, không thuộc buổi này — bỏ ô này"
                        % (b["ma"], clb["club_id"], clb["buoi"]))
                elif clb["club_id"] not in ds:
                    ds.append(clb["club_id"])
            if len(ds) > bm.TRAN_CLB_MOI_BUOI:
                bao("%s: %d nguyện vọng, chỉ giữ %d đầu"
                    % (b["ma"], len(ds), bm.TRAN_CLB_MOI_BUOI))
                ds = ds[:bm.TRAN_CLB_MOI_BUOI]
            if ds:
                nguyen_vong[b["ma"]] = ds

        bai_thi = []
        for clb in bm.clb_co_thi(de):
            ma = clb["club_id"]
            if not bm._chuan(_gia_tri(dong, cot["thi-" + ma])).startswith("có"):
                continue
            tra_loi = {i: _gia_tri(dong, cot["%s-%d" % (ma, i)])
                       for i in range(1, len(clb["de_thi"]) + 1)}
            diem, dung = bm.cham_bai(de, clb, tra_loi)
            cot_p = [cot_diem.get("%s-%d" % (ma, i)) for i in tra_loi]
            if all(c is not None for c in cot_p):
                try:
                    diem_forms = sum(float(dong[c] or 0) for c in cot_p)
                except ValueError:
                    diem_forms = None
                if diem_forms is not None and abs(diem_forms - diem) > 1e-9:
                    bao("%s: Forms chấm %s, đáp án de_thi.json chấm %s — đáp án "
                        "trên Forms đã lệch, soát lại trước khi dùng điểm"
                        % (ma, bm.ghi_so(diem_forms), bm.ghi_so(diem)))
            da_xep = ma in nguyen_vong.get(clb["buoi"], [])
            if not da_xep:
                # Điểm cho CLB em không xếp là điểm không dùng tới — phần mềm
                # cũng sẽ bỏ. Giữ trong bảng điểm để giáo viên vẫn thấy bài.
                bao("%s: em làm bài thi nhưng KHÔNG xếp CLB này ở nguyện vọng %s "
                    "— điểm có trong BANG_DIEM.xlsx nhưng không nạp vào phần mềm"
                    % (ma, clb["buoi"]))
            bai_thi.append({"club_id": ma, "diem": diem, "dung": dung,
                            "tra_loi": tra_loi, "nap": da_xep})

        for b in de["buoi"]:
            # Sổ nhập CHẶN cả sổ khi một em thi quá trần trong một buổi
            # (so_nhap_qua_tran_thi), nên ở đây chỉ nạp bài của các CLB em xếp
            # cao nhất, tới đúng trần; bài còn lại vẫn có trong BANG_DIEM.xlsx.
            xep = nguyen_vong.get(b["ma"], [])
            thi = sorted((t for t in bai_thi
                          if t["nap"] and theo_ma[t["club_id"]]["buoi"] == b["ma"]),
                         key=lambda t: xep.index(t["club_id"]))
            if len(thi) > bm.TRAN_THI_MOI_BUOI:
                bo = thi[bm.TRAN_THI_MOI_BUOI:]
                for t in bo:
                    t["nap"] = False
                bao("%s: dự thi %d CLB, vượt trần %d. Chỉ nạp bài của %d CLB xếp "
                    "cao nhất; không nạp: %s"
                    % (b["ma"], len(thi), bm.TRAN_THI_MOI_BUOI, bm.TRAN_THI_MOI_BUOI,
                       ", ".join(t["club_id"] for t in bo)))

        if sid in hoc_sinh:
            # Giữ phiếu ĐẦU: đây là bài thi, cho nộp lại là cho làm lại tới
            # khi được điểm cao. Muốn đổi nguyện vọng thì giáo viên sửa tay.
            bao("nộp lần nữa — BỎ phiếu này, giữ phiếu đầu ở dòng %d"
                % hoc_sinh[sid]["dong"])
            continue
        hoc_sinh[sid] = {"dong": so_dong, "student_id": sid,
                         "name": _gia_tri(dong, cot["name"]),
                         "nguyen_vong": nguyen_vong, "bai_thi": bai_thi}
        if not nguyen_vong:
            bao("không xếp nguyện vọng buổi nào")

    return list(hoc_sinh.values()), canh_bao


# ---------------------------------------------------------------- ghi tệp

TEN_SO = "SO_NHAP_CLB.xlsx"


def ghi_tep_phan_mem(de, hoc_sinh, thu_muc):
    """Ghi Sổ nhập CLB. Trả đường dẫn.

    Nguyện vọng các buổi nối thành một danh sách theo thứ tự buổi trong
    de_thi.json; điểm (chỉ bài được nạp) đặt ngay cạnh CLB đó.
    """
    clubs = [{"club_id": c["club_id"], "name": c["name"], "capacity": c["capacity"],
              "reserve_capacity": c["reserve_capacity"],
              "reserve_group": c["reserve_group"], "buoi": c["buoi"]}
             for c in de["cau_lac_bo"]]
    students = []
    for h in hoc_sinh:
        diem = {t["club_id"]: bm.ghi_so(t["diem"]) for t in h["bai_thi"] if t["nap"]}
        thu_tu = [ma for b in de["buoi"] for ma in h["nguyen_vong"].get(b["ma"], [])]
        # Không có nhóm: sổ ghi KHÔNG có cột Nhóm ưu tiên (co_nhom=False bên dưới).
        students.append({
            "student_id": h["student_id"], "name": h["name"], "reserve_group": "",
            "nv": [{"club_id": ma, "thi": ma in diem, "diem": diem.get(ma, "")}
                   for ma in thu_tu],
        })
    duong = os.path.join(thu_muc, TEN_SO)
    # co_nhom=False: Forms không hỏi nhóm ưu tiên. Không có cột thì phần mềm
    # GIỮ nhóm đã gán; có cột mà trống thì phần mềm sẽ BỎ nhóm của em.
    so_nhap.ghi_so_nhap(duong, clubs, students, co_nhom=False)
    return duong


def ghi_bang_diem(de, hoc_sinh, canh_bao, duong):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    dam = Font(bold=True, color="FFFFFF")
    nen = PatternFill("solid", fgColor="1F3A5F")
    co_thi = bm.clb_co_thi(de)

    def dau_bang(ws, tieu_de, rong):
        ws.append(tieu_de)
        for i, w in enumerate(rong, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
            ws.cell(1, i).font, ws.cell(1, i).fill = dam, nen
            ws.cell(1, i).alignment = Alignment(wrap_text=True, vertical="center")
        ws.freeze_panes = "C2"

    wb = Workbook()
    ws = wb.active
    ws.title = "Bảng điểm"
    dau_bang(ws, ["Mã HS", "Họ tên"]
             + ["%s (%s)\n/%s" % (c["name"], c["club_id"], bm.ghi_so(bm.diem_toi_da(de, c)))
                for c in co_thi] + ["Số CLB đã thi"],
             [10, 24] + [14] * len(co_thi) + [10])
    ws.row_dimensions[1].height = 45
    for h in hoc_sinh:
        diem = {t["club_id"]: t["diem"] for t in h["bai_thi"]}
        ws.append([h["student_id"], h["name"]]
                  + [diem.get(c["club_id"]) for c in co_thi] + [len(diem)])

    ws = wb.create_sheet("Chi tiết")
    n_cau = max(len(c["de_thi"]) for c in co_thi)
    dau_bang(ws, ["Mã HS", "Họ tên", "CLB", "Buổi"]
             + ["Câu %d" % i for i in range(1, n_cau + 1)]
             + ["Điểm", "Nạp vào phần mềm"],
             [10, 24, 14, 8] + [7] * n_cau + [7, 16])
    for h in hoc_sinh:
        for t in h["bai_thi"]:
            buoi = next(c["buoi"] for c in co_thi if c["club_id"] == t["club_id"])
            ws.append([h["student_id"], h["name"], t["club_id"], buoi]
                      + ["Đ" if x else "S" for x in t["dung"]]
                      + [""] * (n_cau - len(t["dung"]))
                      + [t["diem"], "Có" if t["nap"] else "Không — chưa xếp nguyện vọng"])

    ws = wb.create_sheet("Thống kê đề")
    dau_bang(ws, ["CLB", "Câu", "Nội dung", "Đáp án", "Số bài", "Số đúng", "Tỉ lệ đúng"],
             [14, 6, 50, 26, 8, 8, 10])
    for c in co_thi:
        bai = [t for h in hoc_sinh for t in h["bai_thi"] if t["club_id"] == c["club_id"]]
        for i, cau in enumerate(c["de_thi"]):
            dung = sum(t["dung"][i] for t in bai)
            ws.append([c["club_id"], i + 1, cau["cau"], cau["lua_chon"][cau["dap_an"]],
                       len(bai), dung, (dung / len(bai)) if bai else None])
            ws.cell(ws.max_row, 7).number_format = "0%"

    ws = wb.create_sheet("Cảnh báo")
    dau_bang(ws, ["Dòng Excel", "Mã HS", "Nội dung"], [10, 10, 100])
    for x in canh_bao:
        ws.append(list(x))
    if not canh_bao:
        ws.append(["", "", "Không có cảnh báo nào."])
    wb.save(duong)


def chuyen(duong_xlsx, thu_muc_ra, de=None):
    de = de or bm.doc_de_thi()
    tieu_de, cac_dong = doc_tep_xuat(duong_xlsx)
    hoc_sinh, canh_bao = phan_tich(de, tieu_de, cac_dong)
    if not hoc_sinh:
        raise LoiTepXuat("tệp không có phiếu nào có mã học sinh")
    os.makedirs(thu_muc_ra, exist_ok=True)
    ghi_tep_phan_mem(de, hoc_sinh, thu_muc_ra)
    ghi_bang_diem(de, hoc_sinh, canh_bao, os.path.join(thu_muc_ra, "BANG_DIEM.xlsx"))
    return {"n_hoc_sinh": len(hoc_sinh),
            "n_bai_thi": sum(len(h["bai_thi"]) for h in hoc_sinh),
            "canh_bao": canh_bao}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("tep_xuat", help="tệp .xlsx tải từ Forms (Responses → Open in Excel)")
    ap.add_argument("--ra", required=True, help="thư mục ghi kết quả")
    ap.add_argument("--de", default=bm.DE_THI_MAC_DINH, help="de_thi.json")
    a = ap.parse_args(argv)
    try:
        kq = chuyen(a.tep_xuat, a.ra, bm.doc_de_thi(a.de))
    except (bm.LoiDeThi, LoiTepXuat) as e:
        print("KHÔNG GHI TỆP NÀO — %s" % e, file=sys.stderr)
        return 1
    print("Đã chuyển %d học sinh, chấm %d bài thi -> %s"
          % (kq["n_hoc_sinh"], kq["n_bai_thi"], a.ra))
    if kq["canh_bao"]:
        print("\n%d cảnh báo (cũng có trong sheet 'Cảnh báo' của BANG_DIEM.xlsx):"
              % len(kq["canh_bao"]))
        for dong, sid, nd in kq["canh_bao"]:
            print("  dòng %s %s: %s" % (dong, sid, nd))
    print("\nKéo %s vào ô nạp ở màn hình Vận hành của phần mềm." % TEN_SO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
