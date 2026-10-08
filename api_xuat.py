"""Xuất kết quả: tệp tổng, tệp tổng hợp, tệp theo CLB/buổi và tệp Excel.

Một phần của PipelineAPI (xem api.py) — tách riêng cho dễ đọc; mọi hàm
public ở đây vẫn là hàm của PipelineAPI và giao diện gọi được như cũ.
"""

import datetime
import os
import sys

from api_chung import (
    _an_toan_cho_excel,
    _ghi_csv,
    _now,
    _phan_tram_vn,
    _so_vn,
    duong_dan_khong_de,
    thu_muc_tai_ve,
)
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import BUOI_MAC_DINH, dau_van_tay_du_lieu
import so_nhap


class XuatKetQuaMixin:
    # -----------------------------------------------------------------
    # XUẤT KẾT QUẢ
    #
    # File này là SẢN PHẨM CUỐI của cả quy trình — nhà trường dán bảng,
    # gửi phụ huynh, phát cho giáo viên phụ trách từng CLB. Bản cũ chỉ
    # xuất hai cột mã (student_id,club_id): nhìn vào không biết em nào
    # tên gì, đỗ CLB nào, đỗ nguyện vọng thứ mấy. Toàn bộ dữ liệu đó ĐÃ
    # có sẵn trong DB, chỉ là câu lệnh xuất không lấy.
    # -----------------------------------------------------------------

    # Ký tự KHÔNG được phép có trong tên file trên Windows, cộng thêm
    # dấu phân cách đường dẫn. club_id do trường tự đặt và
    # create_or_update_club KHÔNG giới hạn ký tự, nên một mã như
    # "../ngoai" hay "khoi 10/11" sẽ làm file rơi ra ngoài thư mục kết
    # quả (hoặc ghi đè file khác) nếu ghép thẳng vào tên file.
    _KY_TU_CAM_TRONG_TEN_FILE = '<>:"/\\|?*'

    @staticmethod
    def _ten_file_an_toan(raw: str, mac_dinh: str = "club") -> str:
        ten = "".join(
            "_" if (c in XuatKetQuaMixin._KY_TU_CAM_TRONG_TEN_FILE or ord(c) < 32) else c
            for c in (raw or "")
        ).strip(" .")
        # "..", "." và chuỗi rỗng đều không dùng làm tên file được
        if not ten or ten in (".", ".."):
            return mac_dinh
        # Windows không cho tạo tệp tên CON, NUL, COM1... (kể cả khi có
        # đuôi: "nul.csv" cũng hỏng). CLB mã "CON" từng làm lần xuất báo lỗi.
        if ten.split(".")[0].upper() in XuatKetQuaMixin._TEN_DANH_RIENG_WINDOWS:
            return "_" + ten
        return ten

    _TEN_DANH_RIENG_WINDOWS = frozenset(
        ["CON", "PRN", "AUX", "NUL"]
        + ["COM%d" % i for i in range(1, 10)]
        + ["LPT%d" % i for i in range(1, 10)])

    @staticmethod
    def _ten_chua_dung(ten: str, da_dung: set) -> str:
        """`ten`, hoặc `ten_2`, `ten_3`... — cái đầu tiên CHƯA dùng.

        So KHÔNG phân biệt hoa/thường: ổ NTFS trên Windows coi `clb_a.csv`
        và `CLB_A.csv` là một tệp, mà phần mềm lại cho phép hai mã CLB đó
        cùng tồn tại (_khop_club_id) — tệp sau từng ghi đè tệp trước, một
        giáo viên cầm nhầm danh sách. Thử đến khi trống thật, vì cách cũ
        (ghép số đếm) vẫn đụng một CLB tên sẵn là `a_2`.
        """
        ung_vien, n = ten, 1
        while ung_vien.casefold() in da_dung:
            n += 1
            ung_vien = f"{ten}_{n}"
        da_dung.add(ung_vien.casefold())
        return ung_vien

    # -----------------------------------------------------------------
    # SỔ EXCEL KẾT QUẢ
    #
    # Thứ tự trang = thứ tự người đọc cần: mở ra là trang hướng dẫn với
    # mấy con số chính và mục lục bấm được, rồi danh sách, rồi từng CLB để
    # phát cho giáo viên; phần kỹ thuật (hạt giống, số bốc thăm) để cuối.
    # -----------------------------------------------------------------
    TRANG_SO_EXCEL = ("Hướng dẫn", "Danh sách học sinh", "Theo CLB",
                      "Chưa có chỗ", "Thống kê", "Dấu vết (kỹ thuật)")

    def _ghi_so_excel(self, path: str, du: dict) -> list:
        """Ghi sổ kết quả sáu trang từ `_du_lieu_xuat`. Trả về tên các trang.

        Mọi trang đều có dòng tên trang và một câu nói trang dùng làm gì,
        in vừa khổ A4 theo chiều ngang, có số trang ở chân. Trang danh sách
        khoá dòng tiêu đề và bật bộ lọc. Các trang luôn có mặt, kể cả khi
        trống (kèm một dòng nói vì sao trống) — thứ tự trang cố định thì
        người dùng quen tay, không phải đi tìm.
        """
        from openpyxl import Workbook

        from so_excel import Trang

        wb = Workbook()
        wb.remove(wb.active)
        trang = {ten: Trang(wb.create_sheet(ten)) for ten in self.TRANG_SO_EXCEL}

        bao = self._bang_bao_cao(so=True)
        xuat_luc = _now()
        tt = self.get_trang_thai_ket_qua()
        co_ket_qua = bool(tt.get("ok") and tt["data"]["co_ket_qua"])
        ket_qua_cu = bool(co_ket_qua and tt["data"]["ket_qua_cu"])

        self._trang_huong_dan(trang["Hướng dẫn"], du, bao, xuat_luc,
                              co_ket_qua, ket_qua_cu)
        self._trang_danh_sach(trang["Danh sách học sinh"], du, co_ket_qua)
        self._trang_theo_clb(trang["Theo CLB"], du)
        self._trang_chua_co_cho(trang["Chưa có chỗ"], bao, co_ket_qua)
        self._trang_thong_ke(trang["Thống kê"], bao, du)
        self._trang_dau_vet(trang["Dấu vết (kỹ thuật)"], du, xuat_luc)

        wb.active = 0
        wb.save(path)
        return list(self.TRANG_SO_EXCEL)

    def _luu_so_excel(self, path: str, du: dict) -> list:
        """Ghi sổ vào tệp TẠM cạnh `path`, xong mới đổi tên đè lên `path`.

        Hỏng giữa chừng (đầy đĩa, dữ liệu lạ) thì chỉ xoá tệp tạm: tệp cũ ở
        `path` — có khi là tệp người dùng chỉ định — còn nguyên, và Tải
        xuống không bao giờ có một tệp .xlsx dở mở ra báo hỏng. Trước đây
        nhánh lỗi xoá thẳng `path`, tức xoá luôn tệp có sẵn của người dùng.
        """
        import uuid

        # Khong dung tempfile.mkstemp: tep do mang quyen 0600 va giu nguyen
        # quyen ay sau khi doi ten, khac voi moi tep xuat khac.
        tam = os.path.join(os.path.dirname(os.path.abspath(path)),
                           ".~%s.xlsx" % uuid.uuid4().hex)
        try:
            trang = self._ghi_so_excel(tam, du)
            os.replace(tam, path)
            return trang
        finally:
            if os.path.exists(tam):
                try:
                    os.remove(tam)
                except OSError:
                    pass

    def _trang_huong_dan(self, t, du, bao, xuat_luc, co_ket_qua, ket_qua_cu):
        from so_excel import CHU_CANH_BAO

        t.tieu_de("KẾT QUẢ PHÂN BỔ CÂU LẠC BỘ", "Xuất lúc %s." % xuat_luc)
        # Tep mang di hop phai tu noi duoc no con dung khong. Man hinh co dai
        # canh bao, nhung tep ra khoi phan mem thi chi con dong nay.
        if not co_ket_qua:
            t.ghi_chu("Chưa chạy sắp xếp lần nào — các trang danh sách đang "
                      "trống. Hãy chạy sắp xếp rồi xuất lại.", CHU_CANH_BAO)
        elif ket_qua_cu:
            t.ghi_chu("CHÚ Ý: dữ liệu đã sửa sau lần chạy này, kết quả có thể "
                      "đã cũ. Hãy chạy lại rồi xuất lại.", CHU_CANH_BAO)

        co_cho: dict = {}
        for r in du["rows"]:
            co_cho[r["student_id"]] = co_cho.get(r["student_id"], False) or bool(r["club_id"])
        so_co = sum(co_cho.values())

        t.muc("SỐ LIỆU CHÍNH")
        t.dong("Số học sinh", len(co_cho))
        t.dong("Số em đã có câu lạc bộ", so_co)
        t.dong("Số em chưa có chỗ", len(co_cho) - so_co)
        if du["nhieu_buoi"]:
            t.dong("Số buổi", len(du["ds_buoi"]))
        if "clb" in bao:
            dong_clb = bao["clb"][2]
            t.dong("Số câu lạc bộ", len(dong_clb))
            t.dong("Chỗ đã xếp", sum(d[6] or 0 for d in dong_clb))
            t.dong("Tổng sức chứa", sum(d[7] or 0 for d in dong_clb))
        if "nv" in bao and bao["nv"][2]:
            dau = bao["nv"][2][0]
            if dau[0] == "Nguyện vọng 1":
                t.dong("Tỉ lệ chỗ là nguyện vọng 1 (%)", dau[2])

        t.muc("CÁC TRANG TRONG TỆP NÀY — bấm tên trang để mở")
        mo_ta = {
            "Danh sách học sinh": (
                "Thời khoá biểu: mỗi em một dòng, mỗi buổi một cột."
                if du["nhieu_buoi"] else
                "Mỗi em một dòng, kèm câu lạc bộ của em. Lọc được theo câu lạc bộ."),
            "Theo CLB": "Danh sách từng câu lạc bộ để phát cho giáo viên phụ "
                        "trách. In ra mỗi câu lạc bộ một trang.",
            "Chưa có chỗ": "Những em chưa vào câu lạc bộ nào — nhà trường cần xử lý tiếp.",
            "Thống kê": "Số liệu để họp: câu lạc bộ nào đông, bao nhiêu em được "
                        "nguyện vọng 1, suất dự trữ dùng tới đâu.",
            "Dấu vết (kỹ thuật)": "Hạt giống và số bốc thăm để tính lại kết quả. "
                                  "Không cần đọc trang này để dùng kết quả.",
        }
        for ten in self.TRANG_SO_EXCEL[1:]:
            t.lien_ket(ten, mo_ta[ten])

        t.muc("LƯU Ý")
        t.ghi_chu("Tệp có điểm chấm và số bốc thăm — không gửi cho giáo viên chấm điểm.")
        t.ghi_chu("Đây là dữ liệu học sinh. Cân nhắc trước khi gửi qua email "
                  "hay chép lên máy dùng chung.")
        t.xong(ngang=False, rong_co_dinh={1: 34, 2: 90})

    def _trang_danh_sach(self, t, du, co_ket_qua):
        if du["nhieu_buoi"]:
            cot, dong = du["tkb"]
            t.tieu_de("THỜI KHOÁ BIỂU CÂU LẠC BỘ CẢ TUẦN",
                      "Mỗi em một dòng, mỗi buổi một cột. Bấm mũi tên ở dòng "
                      "tiêu đề để lọc. Dòng tô đỏ: em chưa có câu lạc bộ nào.")
            i_chua = len(cot) - 1          # cot "So CLB"
        else:
            cot, dong = du["cot_tong"], du["dong_tong"]
            t.tieu_de("DANH SÁCH HỌC SINH VÀ CÂU LẠC BỘ",
                      "Mỗi em một dòng. Bấm mũi tên ở dòng tiêu đề để lọc theo "
                      "câu lạc bộ. Dòng tô đỏ: em chưa được xếp.")
            i_chua = cot.index("Mã CLB")

        def chua_co_cho(d):
            return not d[i_chua]

        dau, _ = t.bang(cot, dong, to_do=chua_co_cho, khoa=True, loc=True,
                        rong="" if co_ket_qua else
                        "(chưa có kết quả — hãy chạy sắp xếp trước)")
        t.xong(lap_hang=dau)

    def _trang_theo_clb(self, t, du):
        t.tieu_de("DANH SÁCH TỪNG CÂU LẠC BỘ",
                  "Mỗi câu lạc bộ một khối. Khi in, mỗi câu lạc bộ sang một "
                  "trang riêng — phát thẳng cho giáo viên phụ trách.")
        cot = ["STT", "Mã học sinh", "Họ tên", "Nguyện vọng thứ",
               "Diện trúng tuyển", "Nhóm dự trữ"]

        lap = self.get_club_fill_stats()
        ds_clb = lap["data"] if lap.get("ok") else []
        thu_tu = {b: i for i, b in enumerate(du["ds_buoi"])}
        ds_clb = sorted(ds_clb, key=lambda c: (
            thu_tu.get(c.get("buoi"), len(thu_tu)),
            (c.get("name") or c["club_id"]).casefold()))

        theo_clb: dict = {}
        for r in du["rows"]:
            if r["club_id"]:
                theo_clb.setdefault(r["club_id"], []).append(r)

        if not ds_clb:
            t.ghi_chu("(chưa có câu lạc bộ nào)")
        for n, c in enumerate(ds_clb):
            if n:
                t.ngat_trang()
            ten = c.get("name") or c["club_id"]
            # Ten qua dai thi cat, de "Ma CLB" va "Da xep" con nam tren dong.
            if len(ten) > 120:
                ten = ten[:119] + "…"
            phan = [ten, "Mã CLB: %s" % c["club_id"]]
            if du["nhieu_buoi"]:
                phan.append("Buổi: %s" % c.get("buoi"))
            phan.append("Đã xếp %d/%d chỗ" % (c.get("matched") or 0,
                                              c.get("capacity") or 0))
            t.khoi(" · ".join(phan), len(cot))
            t.bang(cot, [
                [i, r["student_id"], r["ho_ten"] or "",
                 r["rank_in_student_pref"] or "",
                 self._nhan_dien(r["matched_tier"]), r["reserve_group"] or ""]
                for i, r in enumerate(theo_clb.get(c["club_id"], []), 1)
            ], rong="(chưa có em nào)")
            t.hang += 1
        t.xong(ngang=False)

    def _trang_chua_co_cho(self, t, bao, co_ket_qua):
        from openpyxl.styles import Alignment

        so_em, cot, dong = bao.get("tt") or (0, [
            "Mã học sinh", "Họ tên", "Số nguyện vọng đã khai",
            "Đã khai những câu lạc bộ (kèm tỉ lệ chọi)"], [])
        t.tieu_de("HỌC SINH CHƯA CÓ CÂU LẠC BỘ NÀO — %d em" % so_em,
                  "Nhà trường cần xếp tay hoặc liên hệ các em này. Cột cuối "
                  "cho biết em đã khai những câu lạc bộ nào và chúng chọi đến đâu.")
        dau, cuoi = t.bang(
            cot, dong, khoa=True, loc=True,
            rong="(không có em nào — mọi em đều có ít nhất một chỗ)"
            if co_ket_qua else "(chưa có kết quả — hãy chạy sắp xếp trước)")
        for h in range(dau + 1, cuoi + 1):
            t.ws.cell(row=h, column=len(cot)).alignment = Alignment(wrap_text=True)
        t.xong(lap_hang=dau, rong_co_dinh={len(cot): 70})

    def _trang_thong_ke(self, t, bao, du):
        t.tieu_de("THỐNG KÊ",
                  "Số liệu để họp: câu lạc bộ nào đông, buổi nào chật, bao "
                  "nhiêu em được nguyện vọng 1, suất dự trữ dùng tới đâu.")
        co_gi = False
        if "clb" in bao:
            _, cot, dong = bao["clb"]
            t.muc("TỪNG CÂU LẠC BỘ")
            # Cot "So em dang ky" KHONG cong don duoc — xem _bang_tong_hop.
            t.ghi_chu('Cột "Số em đăng ký" không cộng dồn được: một em khai ba '
                      'câu lạc bộ được đếm ở cả ba dòng.')
            t.bang(cot, dong)
            co_gi = True

        tai = self.get_tai_theo_buoi()
        if du["nhieu_buoi"] and tai.get("ok") and len(tai["data"]) > 1:
            t.muc("TẢI TỪNG BUỔI — buổi nào chật, buổi nào rộng")
            t.bang(["Buổi", "Số CLB", "Tổng chỗ", "Chỉ tiêu dự trữ",
                    "Số học sinh khai nguyện vọng", "Tỉ lệ chọi"],
                   [[x.get("buoi"), x.get("so_clb"), x.get("tong_cho"),
                     x.get("tong_du_tru"), x.get("so_hoc_sinh"), x.get("ti_le_choi")]
                    for x in tai["data"]])

        dp = self.get_do_phu()
        if dp.get("ok") and dp["data"]["tong_hoc_sinh"]:
            d = dp["data"]
            tong = d["tong_hoc_sinh"]
            t.muc("ĐỘ PHỦ — bao nhiêu em được mấy câu lạc bộ")
            t.bang(["Số câu lạc bộ", "Số em", "Tỉ lệ %"],
                   [[h["so_clb"], h["so_em"], round(100 * h["so_em"] / tong, 1)]
                    for h in d["phan_bo"]])

        if "nv" in bao:
            tong, cot, dong = bao["nv"]
            t.muc("NGUYỆN VỌNG THỨ MẤY THÌ ĐƯỢC — trên %d chỗ đã xếp" % tong)
            t.bang(cot, dong)
        if "dt" in bao:
            thua, cot, dong = bao["dt"]
            t.muc("SUẤT DỰ TRỮ DÙNG TỚI ĐÂU — còn thừa %d suất" % thua)
            t.bang(cot, dong)
        if not co_gi:
            t.ghi_chu("(chưa có câu lạc bộ nào)")
        t.xong(ngang=True)

    def _trang_dau_vet(self, t, du, xuat_luc):
        t.ws.sheet_properties.tabColor = "808080"
        t.tieu_de("DẤU VẾT LẦN CHẠY",
                  "Hạt giống + bộ số bốc thăm đã khoá + cách bốc thăm là đủ để "
                  "bất kỳ ai tính lại và ra đúng kết quả này. Không cần đọc "
                  "trang này để dùng kết quả.")
        t.bang(["Mục", "Giá trị"],
               self._dong_dau_vet() + [["Thời điểm xuất tệp này", xuat_luc]],
               bo_soc=True)
        if du["tham"]:
            # Phan mem xao lai thu tu o moi buoi; bang nay la ham TAT DINH cua
            # bo so da khoa va hat giong — ai cung tinh lai duoc.
            t.muc("SỐ BỐC THĂM TỪNG BUỔI — tính lại được từ bộ số đã khoá và hạt giống")
            t.bang(*du["tham"])
        t.xong()

    def _bang_bao_cao(self, so: bool) -> dict:
        """Bốn bảng báo cáo cả trường, dựng MỘT lần cho cả hai nơi dùng.

        Tệp tổng hợp (.csv, đọc bằng mắt) và các trang Excel (để tính tiếp)
        trước đây mỗi nơi tự dựng lại cùng bốn bảng — cùng cột, cùng phép
        tính, chỉ khác cách viết số. Sửa một nơi mà quên nơi kia là hai tệp
        của CÙNG một lần xuất nói hai điều khác nhau.

        `so=False`: số viết kiểu Việt để đọc ("84,5%", "(không có chỗ)").
        `so=True` : số thô để Excel tính được (84.5, ô trống).

        Trả về {tên: (số tóm tắt cho tiêu đề, [cột], [[ô]])}, chỉ gồm bảng
        đọc được dữ liệu.
        """
        def ti_le_choi(x):
            if x is None:
                return "" if so else "(không có chỗ)"
            return x if so else _so_vn(x)

        def phan_tram(a, b):
            if so:
                return round(100 * a / b, 1) if b else ""
            return _phan_tram_vn(a, b)

        def khai(e):
            return "; ".join(
                "%s (%s)" % (k["ten_clb"] or k["club_id"],
                             # Day la CHU (mot o ghep nhieu CLB), nen ke ca
                             # ban so=True cung viet so kieu Viet.
                             _so_vn(k["ti_le_choi"])
                             if k["ti_le_choi"] is not None else "không có chỗ")
                for k in e["da_khai"]) or "(chưa khai nguyện vọng nào)"

        ra = {}
        lap = self.get_club_fill_stats()
        if lap.get("ok"):
            ra["clb"] = (len(lap["data"]), [
                "Buổi", "Mã CLB", "Tên CLB", "Số em đăng ký",
                "Đặt nguyện vọng 1", "Tỉ lệ chọi", "Đã xếp", "Sức chứa",
                "Tỉ lệ lấp đầy" + (" %" if so else ""),
                "Trong đó diện dự trữ", "Chỉ tiêu dự trữ"],
                [[c.get("buoi"), c.get("club_id"), c.get("name"),
                  c.get("so_dang_ky"), c.get("so_dat_nv1"),
                  ti_le_choi(c.get("ti_le_choi")),
                  c.get("matched"), c.get("capacity") or 0,
                  phan_tram(c.get("matched") or 0, c.get("capacity") or 0),
                  c.get("matched_reserve"), c.get("reserve_capacity")]
                 for c in lap["data"]])

        nv = self.get_phan_bo_nguyen_vong()
        if nv.get("ok") and nv["data"]["tong_da_xep"]:
            n = nv["data"]
            tong = n["tong_da_xep"]
            dong = [[("Nguyện vọng %d trở lên" % h["hang"]) if h["gop"]
                     else ("Nguyện vọng %d" % h["hang"]),
                     h["so_em"], phan_tram(h["so_em"], tong)]
                    for h in n["phan_bo"]]
            if n["khong_ro"]:
                dong.append(["Không rõ thứ hạng", n["khong_ro"],
                             phan_tram(n["khong_ro"], tong)])
            ra["nv"] = (tong, ["Nguyện vọng", "Số chỗ",
                               "Tỉ lệ %" if so else "Tỉ lệ"], dong)

        dt = self.get_suat_du_tru()
        if dt.get("ok") and dt["data"]:
            ra["dt"] = (sum(c["con_thua"] for c in dt["data"]), [
                "Buổi", "Mã CLB", "Tên CLB", "Nhãn dự trữ",
                "Chỉ tiêu dự trữ", "Em thuộc nhóm có đăng ký",
                "Đã dùng", "Còn thừa"],
                [[c["buoi"], c["club_id"], c["name"], c["reserve_group"],
                  c["reserve_capacity"], c["nhom_dang_ky"], c["da_dung"],
                  c["con_thua"]] for c in dt["data"]])

        tt = self.get_em_chua_co_cho()
        if tt.get("ok"):
            d = tt["data"]
            ra["tt"] = (d["so_em"], [
                "Mã học sinh", "Họ tên", "Số nguyện vọng đã khai",
                "Đã khai những câu lạc bộ (kèm tỉ lệ chọi)"],
                [[e["student_id"], e["name"] or "", e["so_nguyen_vong"], khai(e)]
                 for e in d["danh_sach"]])
        return ra

    def _dong_dau_vet(self) -> list[list]:
        """[mục, giá trị] của lần chạy gần nhất — ba dòng đầu đủ để tính lại.

        Dùng chung cho tệp tổng hợp và trang "Dấu vết" của sổ Excel.
        """
        meta = self.get_last_run_info()
        m = meta.get("data") if meta.get("ok") else None
        if not m:
            return [["(chưa chạy lần nào)", ""]]
        khoa = self.get_stb_lock_status()
        k = khoa.get("data") if khoa.get("ok") else {}
        return [
            ["Hạt giống bốc thăm", m.get("seed")],
            ["Cách bốc thăm", m.get("che_do_boc_tham")],
            ["Bộ số bốc thăm khoá lúc", (k or {}).get("locked_at") or "(chưa khoá)"],
            ["Thời điểm chạy", m.get("run_at")],
            ["Số vòng xử lý", m.get("rounds_run")],
            ["Số buổi lần chạy này phủ", m.get("so_buoi")],
            ["Buổi đã chạy", (m.get("buoi_da_chay") or "").replace(",", ", ")],
        ]

    def _bang_tong_hop(self) -> list[list]:
        """Các dòng của tệp tổng hợp — dùng chung cho bản CSV và bản Excel.

        VÌ SAO TỆP NÀY PHẢI CÓ. Mọi tệp xuất ra trước đây đều nói *ai vào câu
        lạc bộ nào*, không tệp nào nói *kết quả này đến từ đâu*. Hai lần chạy
        khác hạt giống cho ra hai bộ tệp trông y hệt nhau: cùng tên cột, cùng
        số dòng, cùng hình dạng. Trường in ra dán bảng rồi sáu tháng sau bị
        hỏi "bảng này tính thế nào" thì không còn gì để trả lời.

        Mà cả thiết kế của phần mềm dựa trên một lời hứa: *ai cũng tính lại
        được*. Lời hứa ấy cần đúng ba thứ — bộ số bốc thăm đã khoá, hạt
        giống, và cách bốc thăm — và trước bản vá này **không thứ nào** đi
        theo tệp kết quả ra khỏi phần mềm.

        Bảng còn gộp mấy con số vốn chỉ xem được trên màn hình: độ phủ, tỉ lệ
        lấp đầy từng câu lạc bộ, tải từng buổi, và danh sách em chưa có chỗ
        nào. Đó đúng là những thứ nhà trường phải xử lý tiếp, nên chúng cần
        nằm trong tệp mang đi họp chứ không nằm trong một tab phải mở phần
        mềm mới thấy.
        """
        def phan(tieu_de):
            return [[], [tieu_de]]

        ra: list[list] = [["TỔNG HỢP KẾT QUẢ PHÂN BỔ CÂU LẠC BỘ (RB-DA)"]]

        # ---- 1. Dau vet lan chay ----
        ra += phan("DẤU VẾT LẦN CHẠY — ba dòng đầu là thứ cần để tính lại")
        ra.append(["Mục", "Giá trị"])
        ra += self._dong_dau_vet()
        ra.append(["Thời điểm xuất tệp này", _now()])
        # Tep mang di hop phai tu noi duoc no con dung khong. Man hinh co dai
        # canh bao, nhung tep ra khoi phan mem thi chi con dong nay.
        tt = self.get_trang_thai_ket_qua()
        if tt.get("ok") and tt["data"]["co_ket_qua"]:
            ra.append(["Kết quả còn khớp dữ liệu",
                       "CÓ" if not tt["data"]["ket_qua_cu"] else
                       "KHÔNG — dữ liệu đã sửa sau lần chạy này, kết quả có "
                       "thể đã cũ. Hãy chạy lại rồi xuất lại."])

        # ---- 2. Do phu ----
        dp = self.get_do_phu()
        if dp.get("ok"):
            d = dp["data"]
            tong = d["tong_hoc_sinh"] or 0
            ra += phan("ĐỘ PHỦ — bao nhiêu em được mấy câu lạc bộ")
            ra.append(["Số câu lạc bộ trong tuần", "Số em", "Tỉ lệ"])
            for h in d["phan_bo"]:
                ra.append([h["so_clb"], h["so_em"],
                           _phan_tram_vn(h["so_em"], tong)])
            ra.append(["Tổng số học sinh", tong, ""])
            ra.append(["Trung bình số câu lạc bộ mỗi em",
                       _so_vn(d["trung_binh_clb"]), ""])

        bang = self._bang_bao_cao(so=False)

        # ---- 3. Ti le lap day tung CLB ----
        # Cot "So em dang ky" KHONG cong don duoc: trong cung mot buoi, mot em
        # khai ba cau lac bo thi duoc dem o ca ba dong, ma em ay chi lay duoc
        # MOT cho. Cong cot nay roi chia cho tong chi tieu se ra mot ti le
        # choi phong len vo nghia — nen cau canh bao di ngay trong tieu de.
        if "clb" in bang:
            _, cot, dong = bang["clb"]
            ra += phan("TỪNG CÂU LẠC BỘ — \"số em đăng ký\" KHÔNG cộng dồn "
                       "được (một em khai ba câu lạc bộ được đếm ở cả ba dòng)")
            ra.append(cot)
            ra += dong

        # ---- 4. Tai tung buoi ----
        tai = self.get_tai_theo_buoi()
        if tai.get("ok") and len(tai["data"]) > 1:
            ra += phan("TẢI TỪNG BUỔI — đọc để biết buổi nào chật, buổi nào rộng")
            ra.append(["Buổi", "Số CLB", "Tổng chỗ", "Chỉ tiêu dự trữ",
                       "Số học sinh khai nguyện vọng", "Tỉ lệ chọi"])
            for t in tai["data"]:
                ra.append([
                    t.get("buoi"), t.get("so_clb"), t.get("tong_cho"),
                    t.get("tong_du_tru"), t.get("so_hoc_sinh"),
                    # None = khong co cho nao, khac han "thua cho" — xem
                    # chu thich trong get_tai_theo_buoi.
                    _so_vn(t.get("ti_le_choi")) if t.get("ti_le_choi") is not None
                    else "(không có chỗ)",
                ])

        # ---- 5. Nguyen vong thu may thi duoc ----
        # Do phu noi bao nhieu em co cho, khong noi cho ay co phai thu em
        # muon khong. Hai lan chay rat khac nhau van cho cung mot con so do
        # phu — day la con so phan biet duoc chung.
        if "nv" in bang:
            tong, cot, dong = bang["nv"]
            ra += phan("NGUYỆN VỌNG THỨ MẤY THÌ ĐƯỢC — trên %d chỗ đã xếp" % tong)
            ra.append(cot)
            ra += dong

        # ---- 6. Suat du tru dung toi dau ----
        # Mot suat khong ai dung KHONG bao loi va KHONG hien o dau — no lang
        # le thanh mot suat thuong, co che van chay dung, con y dinh uu tien
        # thi boc hoi. Cot cuoi la con so de quyet dinh noi nhan chinh sach
        # hay ha chi tieu du tru nam sau.
        if "dt" in bang:
            thua, cot, dong = bang["dt"]
            ra += phan("SUẤT DỰ TRỮ DÙNG TỚI ĐÂU — còn thừa %d suất" % thua)
            ra.append(cot)
            ra += dong

        # ---- 7. Em chua co CLB nao ----
        # Nhom nha truong phai xu ly tiep, nen no nam trong tep mang di hop.
        # Doc tu `get_em_chua_co_cho` chu khong tu `get_do_phu`: ban kia cat
        # danh sach con 200 em cho giao dien, va chi co TEN — ma cach xu ly
        # phu thuoc vao em da khai may nguyen vong, vao CLB chat den dau.
        if "tt" in bang:
            so_em, cot, dong = bang["tt"]
            ra += phan("HỌC SINH CHƯA CÓ CÂU LẠC BỘ NÀO — %d em" % so_em)
            if dong:
                ra.append(cot)
                ra += dong
            else:
                ra.append(["(không có em nào — mọi em đều có ít nhất một chỗ)", ""])

        return ra
    def _duong_xuat(self, output_path: str, ten_mac_dinh: str,
                    kem_duoi: tuple = ()) -> str:
        """Chỗ đặt một tệp (hoặc thư mục) xuất ra — MỘT luật cho mọi lần xuất.

        Rỗng hoặc TƯƠNG ĐỐI -> thư mục Tải xuống (lùi về cạnh app.db nếu
        không ghi được), và không ghi đè tệp đã có: `x.csv` thành
        `x (2).csv` như trình duyệt. Đường dẫn TUYỆT ĐỐI là ý muốn rõ ràng
        của bên gọi -> tôn trọng nguyên văn. Xem `export_csv`.
        """
        output_path = (output_path or "").strip() or ten_mac_dinh
        if os.path.isabs(output_path):
            return output_path
        thu_muc = self.thu_muc_xuat or thu_muc_tai_ve()
        if not (thu_muc and os.path.isdir(thu_muc)
                and os.access(thu_muc, os.W_OK)):
            thu_muc = os.path.dirname(os.path.abspath(self.db_path))
        # Chi tranh ghi de o duong CHUONG TRINH tu chon.
        # `kem_duoi`: tep di kem cung ten goc (so Excel + bo .csv) — ten goc
        # phai con trong cho moi duoi.
        return duong_dan_khong_de(
            os.path.join(thu_muc, os.path.basename(output_path)), kem_duoi)
    def _goc_xuat_hop_le(self) -> list:
        """Những thư mục GỐC mà tệp xuất có thể nằm trong — xem `_duong_xuat`."""
        goc = [self.thu_muc_xuat or thu_muc_tai_ve(),
               os.path.dirname(os.path.abspath(self.db_path))]
        return [os.path.realpath(g) for g in goc if g]
    @staticmethod
    def _nam_trong(thu_muc: str, goc: str) -> bool:
        """`thu_muc` là `goc` hoặc nằm bên trong nó.

        `commonpath` ném ValueError khi hai đường dẫn KHÁC Ổ ĐĨA (Windows:
        C:\\ và D:\\). Khác ổ thì chắc chắn không nằm trong nhau — trả False
        để phép so đi tiếp tới gốc hợp lệ kế tiếp, thay vì hỏng cả lần mở
        (tải xuống ở C: không ghi được, tệp rơi về cạnh app.db ở D:).
        """
        try:
            return os.path.commonpath([thu_muc, goc]) == goc
        except ValueError:
            return False
    def mo_thu_muc(self, path: str):
        """Mở thư mục chứa tệp vừa xuất trong trình quản lý tệp của máy.

        Chỉ hiện đường dẫn thì giáo viên phải tự lần tới thư mục Tải xuống
        — việc không phải ai cũng làm được. `path` là một TỆP (mở thư mục
        chứa nó) hoặc một THƯ MỤC (mở chính nó, vd thư mục dữ liệu đầu vào).

        AN TOÀN: hàm này gọi được từ JavaScript, nên CHỈ mở thư mục nằm
        trong chỗ phần mềm tự đặt tệp xuất (`_goc_xuat_hop_le`). So bằng
        `realpath` + `commonpath` để "..", liên kết tượng trưng hay đường
        dẫn lạ đều không lọt ra ngoài. Không bao giờ chạy qua shell.
        """
        try:
            p = os.path.realpath((path or "").strip() or ".")
            thu_muc = p if os.path.isdir(p) else os.path.dirname(p)
            if not os.path.isdir(thu_muc):
                return _fail(err("thu_muc_khong_hop_le", path=path))
            if not any(self._nam_trong(thu_muc, g) for g in self._goc_xuat_hop_le()):
                return _fail(err("thu_muc_khong_hop_le", path=path))
            if sys.platform == "win32":
                os.startfile(thu_muc)  # noqa: S606 — thu muc da duoc soat o tren
            else:
                import subprocess
                lenh = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([lenh, thu_muc], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            return _ok({"dir": thu_muc})
        except Exception as e:
            return _fail(err("thu_muc_khong_mo_duoc", detail=str(e)))

    # -----------------------------------------------------------------
    # KẾT QUẢ CÓ CÒN KHỚP DỮ LIỆU KHÔNG — và đã đổi gì so với lần trước
    # -----------------------------------------------------------------
    @staticmethod
    def _dau_van_tay_du_lieu(cur) -> str:
        """Xem `rbda_priority_pipeline.dau_van_tay_du_lieu` — MỘT định nghĩa
        "dữ liệu quyết định kết quả" cho cả lần chạy lẫn phép so sau đó."""
        return dau_van_tay_du_lieu(cur)
    def get_trang_thai_ket_qua(self):
        """Kết quả đang lưu có còn khớp dữ liệu hiện tại không.

        `ket_qua_cu` = đã có kết quả VÀ dữ liệu đã sửa sau lần chạy tạo ra
        nó (hoặc CSDL cũ chưa từng ghi dấu vân tay). Dùng cho dải cảnh báo ở
        thẻ Kết quả, cho mọi lần xuất tệp, và cho tệp tổng hợp.
        """
        try:
            with self._ket_noi_doc() as cur:
                co_ket_qua = cur.execute(
                    "SELECT COUNT(*) FROM match_results").fetchone()[0] > 0
                dvt = cur.execute(
                    "SELECT dau_van_tay, luc FROM dau_van_tay_chay WHERE id = 1"
                ).fetchone()
                meta = cur.execute(
                    "SELECT run_at FROM run_meta WHERE id = 1").fetchone()
                hien_tai = self._dau_van_tay_du_lieu(cur) if co_ket_qua else None
            ket_qua_cu = bool(co_ket_qua and (dvt is None or dvt[0] != hien_tai))
            return _ok({
                "co_ket_qua": co_ket_qua,
                "ket_qua_cu": ket_qua_cu,
                "luc_chay": meta[0] if meta else None,
            })
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
    # Thứ tự cố định để tệp và màn hình liệt kê giống nhau.
    _LOAI_THAY_DOI = ("moi_duoc_xep", "mat_cho", "doi_clb", "doi_dien",
                      "hoc_sinh_moi", "bi_bo")
    def get_thay_doi_ket_qua(self):
        """So bảng kết quả hiện tại với bản chụp NGAY TRƯỚC lần chạy gần nhất.

        So theo cặp (học sinh, buổi). Chỉ trả những cặp KHÁC nhau:
          * `moi_duoc_xep` — trước không có CLB, nay có
          * `mat_cho`      — trước có CLB, nay không
          * `doi_clb`      — CLB khác
          * `doi_dien`     — cùng CLB, đổi diện (dự trữ ↔ thường)
          * `hoc_sinh_moi` — trước chưa có dòng nào của cặp này
          * `bi_bo`        — nay không còn dòng nào của cặp này
        Lần chạy đầu tiên thì bản chụp rỗng -> `co_lan_truoc` = False.
        """
        try:
            with self._ket_noi_doc() as cur:
                meta = cur.execute(
                    "SELECT run_at FROM run_meta WHERE id = 1").fetchone()
                truoc = {
                    (r["student_id"], r["buoi"]): r for r in cur.execute(
                        "SELECT * FROM ket_qua_truoc")
                }
                nay = {
                    (r["student_id"], r["buoi"]): r for r in cur.execute(
                        "SELECT * FROM match_results")
                }
                ten_hs = dict(cur.execute(
                    "SELECT student_id, name FROM students").fetchall())
                ten_clb = dict(cur.execute(
                    "SELECT club_id, name FROM clubs").fetchall())
                run_at_truoc = next(
                    (r["run_at"] for r in truoc.values() if r["run_at"]), None)
                ds_buoi = self._ds_buoi(cur)

            dong = []
            for khoa in sorted(set(truoc) | set(nay)):
                a, b = truoc.get(khoa), nay.get(khoa)
                clb_a = a["club_id"] if a else None
                clb_b = b["club_id"] if b else None
                dien_a = a["matched_tier"] if a else None
                dien_b = b["matched_tier"] if b else None
                if a is None:
                    loai = "hoc_sinh_moi"
                elif b is None:
                    loai = "bi_bo"
                elif clb_a == clb_b:
                    if clb_a is None or dien_a == dien_b:
                        continue
                    loai = "doi_dien"
                elif clb_a is None:
                    loai = "moi_duoc_xep"
                elif clb_b is None:
                    loai = "mat_cho"
                else:
                    loai = "doi_clb"
                sid, buoi = khoa
                dong.append({
                    "student_id": sid, "name": ten_hs.get(sid) or "",
                    "buoi": buoi,
                    "club_cu": clb_a, "ten_club_cu": ten_clb.get(clb_a) if clb_a else None,
                    "dien_cu": dien_a,
                    "club_moi": clb_b, "ten_club_moi": ten_clb.get(clb_b) if clb_b else None,
                    "dien_moi": dien_b,
                    "loai": loai,
                })
            return _ok({
                "co_lan_truoc": bool(truoc),
                "run_at_truoc": run_at_truoc,
                "run_at_moi": meta[0] if meta else None,
                "nhieu_buoi": len(ds_buoi) > 1,
                "dong": dong,
                "dem": {k: sum(1 for d in dong if d["loai"] == k)
                        for k in self._LOAI_THAY_DOI},
            })
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
    _NHAN_LOAI_THAY_DOI = {
        "moi_duoc_xep": "Mới được xếp",
        "mat_cho": "Mất chỗ",
        "doi_clb": "Đổi CLB",
        "doi_dien": "Đổi diện",
        "hoc_sinh_moi": "Học sinh mới",
        "bi_bo": "Không còn trong kết quả",
    }
    @staticmethod
    def _nhan_dien(tier):
        # 'reserve'/'general' la ma noi bo — giao vien khong phai doan.
        return {"reserve": "Dự trữ", "general": "Thường"}.get(tier or "", "")
    def export_thay_doi_ket_qua(self, output_path: str = ""):
        """Tệp `thay_doi_ket_qua.csv`: những em có kết quả khác lần chạy trước."""
        try:
            kq = self.get_thay_doi_ket_qua()
            if not kq["ok"]:
                return kq
            d = kq["data"]
            if not d["co_lan_truoc"]:
                return _fail(err("chua_co_lan_chay_truoc"))
            path = self._duong_xuat(output_path, "thay_doi_ket_qua.csv")
            nb = d["nhieu_buoi"]
            header = (["Mã học sinh", "Họ tên"] + (["Buổi"] if nb else [])
                      + ["CLB cũ", "Diện cũ", "CLB mới", "Diện mới", "Loại thay đổi"])
            dong = [
                [x["student_id"], x["name"]] + ([x["buoi"]] if nb else [])
                + [x["ten_club_cu"] or x["club_cu"] or "(không có)",
                   self._nhan_dien(x["dien_cu"]),
                   x["ten_club_moi"] or x["club_moi"] or "(không có)",
                   self._nhan_dien(x["dien_moi"]),
                   self._NHAN_LOAI_THAY_DOI[x["loai"]]]
                for x in d["dong"]
            ]
            tt = self.get_trang_thai_ket_qua()
            ket_qua_cu = bool(tt["ok"] and tt["data"]["ket_qua_cu"])
            # Dong dau noi RO so voi lan nao — thieu no thi tep "thay doi"
            # khong noi duoc la thay doi tu dau.
            dau = [["So sánh kết quả lúc", d["run_at_truoc"] or "",
                    "với kết quả lúc", d["run_at_moi"] or ""]]
            if ket_qua_cu:
                dau.append(["CẢNH BÁO: dữ liệu đã sửa sau lần chạy gần nhất — "
                            "kết quả có thể đã cũ, hãy chạy lại."])
            _ghi_csv(path, [], dau + [[]] + [header] + dong)
            return _ok({"path": path, "n_thay_doi": len(dong),
                        "dem": d["dem"], "ket_qua_cu": ket_qua_cu})
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=str(e)))

    # -----------------------------------------------------------------
    # DỮ LIỆU ĐẦU VÀO HIỆN TẠI — một Sổ nhập CLB NẠP LẠI ĐƯỢC
    # -----------------------------------------------------------------
    def _du_lieu_so_nhap(self, cur):
        """(clubs, students, n_thi_ngoai_nv, n_ten_doi) đúng dạng `so_nhap.ghi_so_nhap`.

        Sổ đòi mỗi CLB một TÊN riêng (ô NV chọn theo tên), còn CSDL thì không
        (form CLB và CSV cũ cho phép "Toán" lẫn "toán"). Tên đụng nhau thì CLB
        sau được thêm buổi hoặc mã CLB (`so_nhap.ten_khong_trung`) — không
        thế thì sổ vừa xuất ra không nạp lại được. `n_ten_doi` đếm số tên đã thêm để giao diện nói ra.
        """
        clubs = [{
            "club_id": r[0], "name": (r[1] or "").strip() or r[0], "capacity": r[2],
            "reserve_capacity": r[3], "reserve_group": r[4],
            "buoi": "" if (r[5] or BUOI_MAC_DINH) == BUOI_MAC_DINH else r[5],
        } for r in cur.execute(
            "SELECT club_id, name, capacity, reserve_capacity, "
            "COALESCE(reserve_group, ''), buoi FROM clubs ORDER BY club_id")]
        n_ten_doi = so_nhap.ten_khong_trung(clubs)
        hs = {r[0]: {"student_id": r[0], "name": r[1] or "", "reserve_group": r[2],
                     "nv": []}
              for r in cur.execute(
                  "SELECT student_id, name, COALESCE(reserve_group, '') "
                  "FROM students ORDER BY student_id")}
        for sid, cid in cur.execute(
                "SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
            if sid in hs:
                hs[sid]["nv"].append({"club_id": cid, "thi": False, "diem": ""})
        n_ngoai = 0
        for sid, cid, diem in cur.execute("""
                SELECT t.student_id, t.club_id, sc.score
                FROM club_test_selection t
                LEFT JOIN club_scores sc
                       ON sc.student_id = t.student_id AND sc.club_id = t.club_id"""):
            o = next((x for x in hs.get(sid, {"nv": []})["nv"] if x["club_id"] == cid), None)
            if o is None:
                # Sổ chỉ ghi điểm CẠNH một nguyện vọng; thi CLB không xếp
                # nguyện vọng thì sổ không chứa được — đếm để nói ra.
                n_ngoai += 1
                continue
            o["thi"], o["diem"] = True, ("" if diem is None else diem)
        return clubs, list(hs.values()), n_ngoai, n_ten_doi

    def export_du_lieu_dau_vao(self, output_path: str = ""):
        """Xuất dữ liệu đầu vào ĐANG CÓ (kể cả sửa sau lần chạy) thành MỘT
        Sổ nhập CLB. Kéo sổ này vào ô nạp của một CSDL trống là dựng lại y
        nguyên — test `test_xuat_du_lieu.py` canh điều đó.

        Lượt thi một CLB mà em KHÔNG xếp nguyện vọng thì sổ không chứa được
        (điểm luôn nằm cạnh một NV) — đếm vào `n_thi_ngoai_nv` để giao diện
        nói ra. Thuật toán không bao giờ xếp em vào CLB em không chọn, nên
        lượt thi đó không đổi kết quả.
        """
        try:
            ten = "SO_NHAP_CLB_" + datetime.datetime.now().strftime("%Y%m%d_%H%M") + ".xlsx"
            path = self._duong_xuat(output_path, ten)
            with self._ket_noi_doc() as cur:
                clubs, students, n_ngoai, n_ten_doi = self._du_lieu_so_nhap(cur)
            so_nhap.ghi_so_nhap(path, clubs, students)
            return _ok({
                "path": path,
                "dir": os.path.dirname(path),
                "n_clubs": len(clubs),
                "n_hoc_sinh": len(students),
                "n_preferences": sum(len(s["nv"]) for s in students),
                "n_tick": sum(1 for s in students for x in s["nv"] if x["thi"]),
                "n_scores": sum(1 for s in students for x in s["nv"]
                                if x["diem"] not in ("", None)),
                "n_thi_ngoai_nv": n_ngoai,
                "n_ten_doi": n_ten_doi,
            })
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=str(e)))

    def tao_so_nhap_mau(self, output_path: str = ""):
        """Tạo Sổ nhập CLB để điền, đặt vào thư mục Tải xuống.

        Phần mềm đã có CLB thì sheet "1. CLB" điền sẵn chúng: người vận
        hành chỉ còn điền học sinh. Chưa có thì sổ trống.
        """
        try:
            path = self._duong_xuat(output_path, "SO_NHAP_CLB.xlsx")
            with self._ket_noi_doc() as cur:
                clubs, _, _, n_ten_doi = self._du_lieu_so_nhap(cur)
            so_nhap.ghi_so_nhap(path, clubs, [])
            return _ok({"path": path, "dir": os.path.dirname(path),
                        "n_clubs": len(clubs), "n_ten_doi": n_ten_doi})
        except Exception as e:
            return _fail(err("so_nhap_mau_loi", detail=str(e)))

    # -----------------------------------------------------------------
    # HỒ SƠ HỌC SINH — một em hoặc nhiều em được chọn
    # -----------------------------------------------------------------
    def export_hoc_sinh_csv(self, student_ids: list, output_path: str = ""):
        """Toàn bộ dữ liệu của các em được chọn, mỗi dòng một cặp (em, CLB).

        Một cặp có mặt khi em tick thi, xếp nguyện vọng, HOẶC được xếp vào
        CLB đó. Em chưa có gì vẫn có MỘT dòng — chọn em nào thì tệp phải có
        em đó, thiếu im lặng là người nhận tưởng em không tồn tại.

        Điểm: chỉ điểm còn tick, đúng tập lần chạy dùng. Số bốc thăm: trường
        nhiều buổi dùng số TỪNG BUỔI (cùng nguồn với bảng số bốc thăm), một
        buổi dùng số đã khoá. Nguyện vọng thứ: thứ hạng TRONG BUỔI, như cột
        cùng tên ở bảng kết quả.
        """
        try:
            if not isinstance(student_ids, list) or not student_ids:
                return _fail(err("chua_chon_hoc_sinh"))
            ids = list(dict.fromkeys(str(s) for s in student_ids))

            with self._ket_noi_doc() as cur:
                hs = {r["student_id"]: r for r in cur.execute(
                    "SELECT student_id, name, reserve_group, stb_number FROM students "
                    "WHERE student_id IN (%s)" % ",".join("?" * len(ids)), ids)}
                thieu = [s for s in ids if s not in hs]
                if thieu:
                    return _fail(err("student_not_found", student_id=", ".join(thieu)))
                clb = {r["club_id"]: r for r in cur.execute(
                    "SELECT club_id, name, COALESCE(NULLIF(buoi, ''), ?) AS buoi "
                    "FROM clubs", (BUOI_MAC_DINH,))}
                ds_buoi = self._ds_buoi(cur)
                dau = ",".join("?" * len(ids))
                tick = {(r[0], r[1]) for r in cur.execute(
                    "SELECT student_id, club_id FROM club_test_selection "
                    "WHERE student_id IN (%s)" % dau, ids)}
                diem = {(r[0], r[1]): r[2] for r in cur.execute(
                    "SELECT student_id, club_id, score FROM club_scores "
                    "WHERE student_id IN (%s)" % dau, ids)}
                nv: dict = {}
                for r in cur.execute(
                        "SELECT student_id, club_id FROM preferences "
                        "WHERE student_id IN (%s) ORDER BY student_id, rank" % dau, ids):
                    nv.setdefault(r[0], []).append(r[1])
                kq = {(r["student_id"], r["club_id"]): r for r in cur.execute(
                    "SELECT student_id, club_id, matched_tier FROM match_results "
                    "WHERE club_id IS NOT NULL AND student_id IN (%s)" % dau, ids)}

            nhieu_buoi = len(ds_buoi) > 1
            so_buoi: dict = {}
            if nhieu_buoi:
                tham = self.get_so_boc_tham_theo_buoi()
                if tham["ok"]:
                    so_buoi = {e["student_id"]: e["so"]
                               for e in tham["data"]["hoc_sinh"]}

            def buoi_cua(cid):
                return clb[cid]["buoi"] if cid in clb else BUOI_MAC_DINH

            header = (["Mã học sinh", "Họ tên", "Nhóm dự trữ"]
                      + (["Buổi"] if nhieu_buoi else [])
                      + ["Số bốc thăm", "Mã CLB", "Tên CLB", "Đăng ký thi",
                         "Điểm", "Nguyện vọng thứ", "Kết quả", "Diện"])
            dong = []
            for sid in ids:
                h = hs[sid]
                # Thu hang trong buoi: dem theo thu tu nguyen vong cua em.
                hang: dict = {}
                dem_buoi: dict = {}
                for cid in nv.get(sid, []):
                    b = buoi_cua(cid)
                    dem_buoi[b] = dem_buoi.get(b, 0) + 1
                    hang[cid] = dem_buoi[b]
                cac_clb = list(dict.fromkeys(
                    nv.get(sid, [])
                    + sorted(c for (s, c) in tick if s == sid)
                    + sorted(c for (s, c) in kq if s == sid)))
                # Sap theo buoi (thu tu ngay), roi theo thu tu tren.
                cac_clb.sort(key=lambda c: (ds_buoi.index(buoi_cua(c))
                                            if buoi_cua(c) in ds_buoi else 99))

                def so_tham(b, sid=sid, h=h):
                    if nhieu_buoi:
                        v = so_buoi.get(sid, {}).get(b)
                        return "" if v is None else v
                    return "" if h["stb_number"] is None else h["stb_number"]

                goc = [sid, h["name"] or "", h["reserve_group"] or ""]
                if not cac_clb:
                    dong.append(goc + ([""] if nhieu_buoi else [])
                                + [so_tham(None) if not nhieu_buoi else "",
                                   "", "(chưa nhập gì)", "", "", "", "", ""])
                    continue
                for cid in cac_clb:
                    b = buoi_cua(cid)
                    co_tick = (sid, cid) in tick
                    d = diem.get((sid, cid)) if co_tick else None
                    x = kq.get((sid, cid))
                    dong.append(
                        goc + ([b] if nhieu_buoi else [])
                        + [so_tham(b), cid,
                           clb[cid]["name"] if cid in clb else "",
                           "Có" if co_tick else "—",
                           "" if d is None else ("%g" % d),
                           hang.get(cid, ""),
                           "Được xếp" if x else "—",
                           self._nhan_dien(x["matched_tier"]) if x else ""])

            ten = ("hoc_sinh_%s.csv" % self._ten_file_an_toan(ids[0], "hoc_sinh")
                   if len(ids) == 1 else "hoc_sinh_da_chon_%d_em.csv" % len(ids))
            path = self._duong_xuat(output_path, ten)
            _ghi_csv(path, header, dong)
            tt = self.get_trang_thai_ket_qua()
            return _ok({
                "path": path,
                "n_hoc_sinh": len(ids),
                "n_dong": len(dong),
                "ket_qua_cu": bool(tt["ok"] and tt["data"]["ket_qua_cu"]),
            })
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=str(e)))

    def _khoa_xuat(self, ham, *args):
        """Giữ khoá ghi + bật bộ nhớ báo cáo suốt một lần xuất.

        Khoá ghi: không lời gọi ghi nào chen vào giữa, nên mọi tệp (và mọi
        trang) của một lần xuất cùng chụp MỘT trạng thái dữ liệu. Bộ nhớ:
        xem _nho_trong_luc_xuat.
        """
        with self._khoa_ghi:
            self._bo_nho_xuat = {}
            try:
                return ham(*args)
            finally:
                self._bo_nho_xuat = None

    def export_ket_qua(self, output_path: str = "", kem_csv: bool = False):
        """Xuất kết quả thành MỘT tệp Excel — đường xuất của nút trên giao diện.

        VÌ SAO. Ban giám khảo nhận xét phần xuất quá rối: một lần bấm từng
        đẻ ra tới sáu tệp rời và hai thư mục, tệp `.xlsx` có nhưng thông báo
        không nhắc tới, còn danh sách từng CLB lại không nằm trong sổ. Giờ
        mặc định chỉ ra một tệp `ket_qua_phan_bo.xlsx` sáu trang (xem
        `_ghi_so_excel`). Hỏng sổ Excel là hỏng cả lần xuất — sổ là sản phẩm
        chính, không được lặng lẽ biến mất như trước.

        `kem_csv=True`: ghi thêm bộ `.csv` rời cũ (xem `export_csv`) cạnh sổ,
        cùng tên gốc — cho ai cần đổ số liệu vào phần mềm khác.

        Chỗ đặt tệp theo đúng luật của `_duong_xuat`: rỗng/tương đối thì vào
        thư mục Tải xuống và không ghi đè tệp cũ.
        """
        return self._khoa_xuat(self._export_ket_qua_da_khoa, output_path, kem_csv)

    def _export_ket_qua_da_khoa(self, output_path: str, kem_csv: bool):
        path = None
        try:
            # Kem CSV thi ten goc phai con trong cho CA HAI duoi, khong thi tep
            # .csv di kem ghi de mot tep cu trung ten.
            path = self._duong_xuat(output_path, "ket_qua_phan_bo.xlsx",
                                    kem_duoi=(".csv",) if kem_csv else ())
            du = self._du_lieu_xuat()
            try:
                trang = self._luu_so_excel(path, du)
            except Exception as e:
                return _fail(err("error_exporting_excel", detail=str(e)))

            ra = {
                "path": path, "excel_path": path, "trang": trang,
                "n_rows": len(du["rows"]),
                "n_hoc_sinh": len({r["student_id"] for r in du["rows"]}),
                "nhieu_buoi": du["nhieu_buoi"],
                "ket_qua_cu": self._ket_qua_cu(),
                "csv_path": None, "per_club_dir": None, "n_club_files": 0,
                "tong_hop_path": None, "thoi_khoa_bieu_path": None,
                "so_boc_tham_path": None,
            }
            if kem_csv:
                # So Excel da ghi xong. CSV hong (vd tep CSV cu dang mo trong
                # Excel tren Windows) khong duoc xoa cong do: van tra ve duong
                # dan so, kem loi rieng cho phan CSV.
                try:
                    bo = self._ghi_bo_csv(os.path.splitext(path)[0] + ".csv", du)
                    bo["csv_path"] = bo.pop("path")
                    ra.update(bo)
                except Exception as e:
                    ra["loi_csv"] = err("error_exporting_csv", detail=str(e))
            return _ok(ra)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=str(e)))

    def export_csv(self, output_path: str = ""):
        """Bộ tệp `.csv` rời (kèm sổ Excel cùng tên) — đường xuất cho phần
        mềm khác và kịch bản đo đạc. Giao diện gọi `export_ket_qua`."""
        return self._khoa_xuat(self._export_csv_da_khoa, output_path)

    def _export_csv_da_khoa(self, output_path: str = ""):
        """
        Xuất kết quả phân bổ ra CSV:

          1. MỘT FILE TỔNG — mọi học sinh, đủ tên và diện trúng tuyển.
          2. MỘT THƯ MỤC theo CLB — mỗi CLB một file, kèm file
             `_chua_duoc_xep.csv` liệt kê các em chưa vào CLB nào.
          3. Tệp tổng hợp, và (nhiều buổi) thời khoá biểu, từng buổi, số
             bốc thăm.
          4. Sổ Excel cùng tên gốc. Hỏng sổ KHÔNG làm hỏng lần xuất này —
             các tệp `.csv` đã ghi xong và vẫn dùng được, `excel_path` None.

        output_path rỗng hoặc TƯƠNG ĐỐI -> tệp rơi vào **thư mục Tải
        xuống** của người dùng (lùi về cạnh app.db nếu không ghi được), và
        không ghi đè tệp cũ. Đường dẫn TUYỆT ĐỐI do bên gọi truyền vào thì
        tôn trọng nguyên văn, kể cả việc ghi đè. Luôn trả về đường dẫn ĐẦY
        ĐỦ để giao diện hiện đúng chỗ tệp nằm.
        """
        try:
            # So Excel cung ten goc di kem -> ten goc phai trong cho ca .xlsx,
            # khong thi ghi de so ma nut tren giao dien vua de o Tai xuong.
            output_path = self._duong_xuat(output_path, "ket_qua_phan_bo.csv",
                                           kem_duoi=(".xlsx",))
            du = self._du_lieu_xuat()
            ra = self._ghi_bo_csv(output_path, du)

            duong_excel = os.path.splitext(output_path)[0] + ".xlsx"
            try:
                self._luu_so_excel(duong_excel, du)
            except Exception:
                duong_excel = None
            ra["excel_path"] = duong_excel
            return _ok(ra)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=str(e)))

    def _ket_qua_cu(self) -> bool:
        tt = self.get_trang_thai_ket_qua()
        return bool(tt.get("ok") and tt["data"]["ket_qua_cu"])

    def _du_lieu_xuat(self) -> dict:
        """Mọi bảng của một lần xuất, đọc MỘT lần cho cả sổ Excel lẫn bộ CSV.

        Hai định dạng đi ra từ cùng một nguồn — không có hai đường tính song
        song để rồi trôi khỏi nhau.
        """
        with self._ket_noi_doc() as cur:
            rows = cur.execute("""
                SELECT m.student_id, s.name AS ho_ten, m.buoi, m.club_id,
                       c.name AS ten_club, m.rank_in_student_pref, m.matched_tier,
                       s.reserve_group
                FROM match_results m
                LEFT JOIN students s ON s.student_id = m.student_id
                LEFT JOIN clubs   c ON c.club_id   = m.club_id
                ORDER BY m.student_id, m.buoi COLLATE THU_TU_BUOI
            """).fetchall()
            ds_buoi = self._ds_buoi(cur)
        nhieu_buoi = len(ds_buoi) > 1
        dien = self._nhan_dien

        # Cot "Buoi" chi xuat hien khi truong THAT SU dung nhieu buoi.
        # Mot buoi ma van co cot day gia tri "__mac_dinh__" thi giao vien
        # phai doan xem no nghia la gi.
        cot_tong = (["Mã học sinh", "Họ tên"]
                    + (["Buổi"] if nhieu_buoi else [])
                    + ["Mã CLB", "Tên CLB", "Nguyện vọng thứ",
                       "Diện trúng tuyển", "Nhóm dự trữ"])
        dong_tong = [
            [r["student_id"], r["ho_ten"] or ""]
            + ([r["buoi"]] if nhieu_buoi else [])
            + [
                r["club_id"] or "",
                r["ten_club"] or ("" if r["club_id"] else "(chưa được xếp)"),
                r["rank_in_student_pref"] if r["rank_in_student_pref"] else "",
                dien(r["matched_tier"]), r["reserve_group"] or "",
            ]
            for r in rows
        ]

        # ---- Thoi khoa bieu tuan: SAN PHAM CHINH cua ban nhieu buoi ----
        # Moi em MOT dong, moi buoi MOT cot — dan bang duoc, phat cho hoc
        # sinh duoc.
        tkb = None
        tham = None
        if nhieu_buoi:
            theo_em: dict = {}
            for r in rows:
                em = theo_em.setdefault(
                    r["student_id"], {"ho_ten": r["ho_ten"] or "", "o": {}})
                em["o"][r["buoi"]] = (
                    r["ten_club"] or r["club_id"] or "") if r["club_id"] else ""
            tkb = (["Mã học sinh", "Họ tên"] + list(ds_buoi) + ["Số CLB"], [
                [sid, em["ho_ten"]]
                + [em["o"].get(b, "") for b in ds_buoi]
                + [sum(1 for b in ds_buoi if em["o"].get(b))]
                for sid, em in sorted(theo_em.items())
            ])

            # ---- So boc tham tung buoi ----
            # Phan mem xao lai thu tu o moi buoi, nen se co phu huynh hoi
            # "vi sao con toi thu Ba dung thu 30 ma thu Sau dung thu 120".
            # Truong van chi cong bo MOT thu: bo so da khoa cong hat giong.
            # Bang nay la ham TAT DINH cua hai thu do, ai cung tinh lai duoc.
            kq_tham = self.get_so_boc_tham_theo_buoi()
            if kq_tham["ok"] and kq_tham["data"]["da_chay"]:
                tham = (["Mã học sinh", "Họ tên"] + list(ds_buoi), [
                    [e["student_id"], e["name"] or ""]
                    + [e["so"].get(b, "") for b in ds_buoi]
                    for e in kq_tham["data"]["hoc_sinh"]
                ])

        return {"rows": rows, "ds_buoi": ds_buoi, "nhieu_buoi": nhieu_buoi,
                "cot_tong": cot_tong, "dong_tong": dong_tong,
                "tkb": tkb, "tham": tham}

    def _ghi_bo_csv(self, output_path: str, du: dict) -> dict:
        """Ghi bộ `.csv` rời từ `_du_lieu_xuat`. Trả về các đường dẫn đã ghi."""
        import csv

        ghi = _ghi_csv   # UTF-8 co BOM + chan cong thuc Excel
        rows = du["rows"]
        dien = self._nhan_dien
        ghi(output_path, du["cot_tong"], du["dong_tong"])

        goc, _ = os.path.splitext(output_path)
        per_club_dir = goc + "_theo_club"
        os.makedirs(per_club_dir, exist_ok=True)

        # Xoa tep .csv cua lan xuat TRUOC trong dung thu muc nay.
        # Khong xoa thi mot CLB da bi go khoi he thong van con nguyen
        # tep cua no, nam canh cac tep moi va trong y het nhu that.
        # Chi dung .csv, chi trong thu muc do phan mem tu tao ra.
        for cu_ten in os.listdir(per_club_dir):
            if cu_ten.lower().endswith(".csv"):
                try:
                    os.remove(os.path.join(per_club_dir, cu_ten))
                except OSError:
                    pass

        theo_club: dict = {}
        for r in rows:
            theo_club.setdefault(r["club_id"] or None, []).append(r)

        n_file = 0
        # Giu cho "_chua_duoc_xep" truoc, de mot CLB trung ten do khong
        # ghi de danh sach em chua co cho.
        ten_da_dung: set = {"_chua_duoc_xep"}
        for club_id, ds in theo_club.items():
            if club_id is None:
                ten = "_chua_duoc_xep"
            else:
                # Hai club_id khac nhau co the ra cung ten sau khi lam
                # sach ("a/b" va "a\b"), hoac chi khac hoa/thuong.
                ten = self._ten_chua_dung(
                    self._ten_file_an_toan(club_id), ten_da_dung)
            ghi(
                os.path.join(per_club_dir, ten + ".csv"),
                ["Mã học sinh", "Họ tên", "Nguyện vọng thứ",
                 "Diện trúng tuyển", "Nhóm dự trữ"],
                [[r["student_id"], r["ho_ten"] or "",
                  r["rank_in_student_pref"] if r["rank_in_student_pref"] else "",
                  dien(r["matched_tier"]), r["reserve_group"] or ""] for r in ds],
            )
            n_file += 1

        duong_tkb = None
        n_tkb = 0
        duong_tham = None
        n_tham = 0
        if du["tkb"]:
            duong_tkb = goc + "_thoi_khoa_bieu.csv"
            ghi(duong_tkb, *du["tkb"])
            n_tkb = len(du["tkb"][1])

            # ---- Mot tep moi buoi, cho giao vien truc ngay do ----
            per_buoi_dir = goc + "_theo_buoi"
            os.makedirs(per_buoi_dir, exist_ok=True)
            for cu_ten in os.listdir(per_buoi_dir):
                if cu_ten.lower().endswith(".csv"):
                    try:
                        os.remove(os.path.join(per_buoi_dir, cu_ten))
                    except OSError:
                        pass
            for b in du["ds_buoi"]:
                ghi(
                    os.path.join(per_buoi_dir, self._ten_file_an_toan(b, "buoi") + ".csv"),
                    ["Mã học sinh", "Họ tên", "Mã CLB", "Tên CLB",
                     "Nguyện vọng thứ", "Diện trúng tuyển"],
                    [
                        [r["student_id"], r["ho_ten"] or "", r["club_id"] or "",
                         r["ten_club"] or "",
                         r["rank_in_student_pref"] if r["rank_in_student_pref"] else "",
                         dien(r["matched_tier"])]
                        for r in rows
                        if r["buoi"] == b and r["club_id"]
                    ],
                )

        if du["tham"]:
            duong_tham = goc + "_so_boc_tham_theo_buoi.csv"
            ghi(duong_tham, *du["tham"])
            n_tham = len(du["tham"][1])

        # ---- Tep TONG HOP: ket qua nay den tu dau, va con gi phai lam ----
        duong_tong_hop = goc + "_tong_hop.csv"
        with open(duong_tong_hop, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerows([_an_toan_cho_excel(o) for o in d]
                        for d in self._bang_tong_hop())

        return {
            "path": output_path,
            "tong_hop_path": duong_tong_hop,
            "n_rows": len(rows),
            "per_club_dir": per_club_dir,
            "n_club_files": n_file,
            "nhieu_buoi": du["nhieu_buoi"],
            "thoi_khoa_bieu_path": duong_tkb,
            "n_thoi_khoa_bieu_rows": n_tkb,
            "so_boc_tham_path": duong_tham,
            "n_so_boc_tham_rows": n_tham,
        }
