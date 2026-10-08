#!/usr/bin/env python3
"""
tao_bao_cao_docx.py
===================
Sinh BAO_CAO_CACH_CHAY.docx TỪ BAO_CAO_CACH_CHAY.html.

VÌ SAO SINH RA CHỨ KHÔNG GÕ TAY. Hai bản báo cáo — bản web tương tác và bản
Word để nộp — phải nói y hệt nhau. Gõ tay bản thứ hai là tạo ra một nguồn sự
thật thứ hai, và hai nguồn sự thật luôn trôi khỏi nhau. Ở đây bản HTML là
nguồn DUY NHẤT; tệp .docx là sản phẩm dẫn xuất, sinh lại được bất cứ lúc nào.

Sơ đồ và các bước mô phỏng KHÔNG được vẽ lại bằng thư viện khác — chúng được
CHỤP MÀN HÌNH từ chính trang HTML bằng Chromium. Vẽ lại là mở đúng cái khe
cho hai bản lệch nhau.

Chạy:
    python3 tao_bao_cao_docx.py

Cần: pip install python-docx playwright
"""

import os
import pathlib
import re
import sys
from html.parser import HTMLParser

GOC = pathlib.Path(__file__).resolve().parent
NGUON = GOC / "BAO_CAO_CACH_CHAY.html"
DICH = GOC / "BAO_CAO_CACH_CHAY.docx"
THU_MUC_ANH = GOC / "bao_cao_hinh"

# Mô phỏng nào có bao nhiêu bước — phải khớp mảng S1/S2 trong trang HTML.
# Sai số ở đây chỉ làm thiếu/thừa ảnh, không làm sai nội dung: kịch bản click
# dừng lại khi nút "Bước tiếp" bị vô hiệu hoá.
MO_PHONG = [("sim1", "s1", 5), ("sim2", "s2", 8)]


# ---------------------------------------------------------------------------
# 1. CHỤP ẢNH SƠ ĐỒ VÀ MÔ PHỎNG TỪ CHÍNH TRANG HTML
# ---------------------------------------------------------------------------

def chup_anh() -> dict:
    """Chụp 5 sơ đồ + mọi bước của 2 mô phỏng. Trả về {khoá: đường dẫn ảnh}."""
    from playwright.sync_api import sync_playwright

    THU_MUC_ANH.mkdir(exist_ok=True)
    ra = {}
    trinh_duyet = os.environ.get("RBDA_CHROMIUM", "/opt/pw-browsers/chromium")

    with sync_playwright() as pw:
        tuy_chon = {"executable_path": trinh_duyet} if os.path.exists(trinh_duyet) else {}
        b = pw.chromium.launch(**tuy_chon)
        # scale 2 để hình còn nét khi in ra giấy
        pg = b.new_page(viewport={"width": 1320, "height": 1100},
                        device_scale_factor=2)
        pg.goto(NGUON.as_uri())
        pg.wait_for_timeout(1500)

        so_do = pg.locator(".diagram")
        for i in range(so_do.count()):
            d = so_do.nth(i)
            d.scroll_into_view_if_needed()
            pg.wait_for_timeout(200)
            p = THU_MUC_ANH / f"so_do_{i + 1}.png"
            d.screenshot(path=str(p))
            ra[f"diagram:{i}"] = p

        for ten_sim, tien_to, _so_buoc in MO_PHONG:
            khung = pg.locator("#" + ten_sim)
            khung.scroll_into_view_if_needed()
            pg.click(f"#{tien_to}-reset")
            pg.wait_for_timeout(250)
            buoc = 0
            while True:
                p = THU_MUC_ANH / f"{ten_sim}_buoc_{buoc + 1}.png"
                khung.screenshot(path=str(p))
                ra[f"{ten_sim}:{buoc}"] = p
                buoc += 1
                if pg.locator(f"#{tien_to}-next").is_disabled():
                    break
                pg.click(f"#{tien_to}-next")
                pg.wait_for_timeout(250)
        b.close()
    return ra


# ---------------------------------------------------------------------------
# 2. ĐỌC TRANG HTML THÀNH DANH SÁCH KHỐI
# ---------------------------------------------------------------------------
#
# Không dùng thư viện phân tích HTML ngoài: markup của trang do chính dự án
# viết, tập thẻ dùng tới rất hẹp và cố định, nên một bộ đọc nhỏ ở đây đủ dùng
# mà không thêm phụ thuộc cho người chạy lại.

KHOI_VAN_BAN = {"h2", "h3", "h4", "p", "li", "td", "th", "blockquote"}


class DocReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.khoi = []            # danh sách khối đã đọc xong
        self.ngan = []            # ngăn xếp (tag, lớp css)
        self.dam = 0              # đang trong <strong>/<b>?
        self.mono = 0             # đang trong <code>/<span class=cite>?
        self.dem_sim = 0
        self.dem_so_do = 0
        self.runs = None          # các đoạn chữ của khối đang mở
        self.loai = None          # loại khối đang mở
        self.bang = None          # bảng đang dựng
        self.hang = None
        self.trong_script = False
        self.trong_style = False
        self.muc_ds = 0           # độ sâu danh sách
        self.kieu_ds = []

    # -- tiện ích --------------------------------------------------------
    def _lop(self, attrs):
        return dict(attrs).get("class", "")

    def _dong_khoi(self):
        if self.loai and self.runs is not None:
            chu = "".join(r[0] for r in self.runs).strip()
            if chu:
                self.khoi.append((self.loai, self.runs))
        self.loai, self.runs = None, None

    # -- xử lý thẻ -------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        lop = self._lop(attrs)
        if tag == "script":
            self.trong_script = True
            return
        if tag == "style":
            self.trong_style = True
            return
        if self.trong_script or self.trong_style:
            return

        if tag == "div" and "diagram" in lop.split():
            self.dem_so_do += 1
            self.khoi.append(("anh", f"diagram:{self.dem_so_do - 1}"))
            self.ngan.append(("SKIP_DIAGRAM", lop))
            return
        if tag == "div" and "sim" in lop.split():
            self.dem_sim += 1
            self.khoi.append(("mo_phong", self.dem_sim - 1))
            self.ngan.append(("SKIP_SIM", lop))
            return
        if any(t[0].startswith("SKIP") for t in self.ngan):
            self.ngan.append((tag, lop))
            return

        if tag in ("strong", "b"):
            self.dam += 1
        elif tag in ("code", "tt"):
            self.mono += 1
        elif tag == "span" and "cite" in lop.split():
            self.mono += 1
            self.ngan.append(("CITE", lop))
            return
        elif tag == "table":
            self._dong_khoi()
            self.bang = []
        elif tag == "tr":
            self.hang = []
        elif tag in ("td", "th"):
            self.runs, self.loai = [], "o"
        elif tag in ("ul", "ol"):
            self._dong_khoi()
            self.muc_ds += 1
            self.kieu_ds.append(tag)
        elif tag == "li":
            self._dong_khoi()
            self.runs, self.loai = [], ("li_o" if self.kieu_ds and self.kieu_ds[-1] == "ol" else "li_c")
        elif tag in ("h2", "h3", "h4", "blockquote"):
            self._dong_khoi()
            self.runs, self.loai = [], tag
        elif tag == "p":
            self._dong_khoi()
            if "box-title" in lop.split():
                self.runs, self.loai = [], "box_title"
            elif "deck" in lop.split():
                self.runs, self.loai = [], "deck"
            else:
                self.runs, self.loai = [], "p"
        elif tag == "pre":
            self._dong_khoi()
            self.runs, self.loai = [], "pre"
        elif tag == "figcaption":
            self._dong_khoi()
            self.runs, self.loai = [], "caption"
        elif tag == "span" and "chapnum" in lop.split():
            self._dong_khoi()
            self.runs, self.loai = [], "chapnum"
        elif tag == "div" and "box" in lop.split():
            kind = ("canh_bao" if "warn" in lop.split()
                    else "bang_chung" if "proof" in lop.split()
                    else "giam_khao" if "judge" in lop.split() else "thuong")
            self.khoi.append(("box_mo", kind))
        elif tag == "br" and self.runs is not None:
            self.runs.append(("\n", self.dam > 0, self.mono > 0))

        self.ngan.append((tag, lop))

    def handle_endtag(self, tag):
        if tag == "script":
            self.trong_script = False
            return
        if tag == "style":
            self.trong_style = False
            return
        if self.trong_script or self.trong_style:
            return

        while self.ngan:
            t, lop = self.ngan.pop()
            if t == "CITE":
                # </span> NAY khop voi muc CITE — dung lai. Truoc day `continue`
                # lam vong lap pop tiep ca the <p> bao ngoai, don sach ngan xep,
                # va doan van bi cat cut ngay tu cho co trich dan dau tien.
                self.mono = max(0, self.mono - 1)
                break
            if t in ("SKIP_DIAGRAM", "SKIP_SIM"):
                break
            if t == tag:
                break

        if tag in ("strong", "b"):
            self.dam = max(0, self.dam - 1)
        elif tag in ("code", "tt"):
            self.mono = max(0, self.mono - 1)
        elif tag in ("td", "th"):
            if self.hang is not None:
                self.hang.append(self.runs or [])
            self.runs, self.loai = None, None
        elif tag == "tr":
            if self.bang is not None and self.hang:
                self.bang.append(self.hang)
            self.hang = None
        elif tag == "table":
            if self.bang:
                self.khoi.append(("bang", self.bang))
            self.bang = None
        elif tag in ("ul", "ol"):
            self._dong_khoi()
            self.muc_ds = max(0, self.muc_ds - 1)
            if self.kieu_ds:
                self.kieu_ds.pop()
        elif tag in ("li", "h2", "h3", "h4", "p", "pre", "blockquote",
                     "figcaption"):
            self._dong_khoi()
        elif tag == "span":
            # CHI dong khoi khi chinh <span> nay MO ra khoi do (span.chapnum).
            # Dong vo dieu kien la cat mat phan chu sau moi <span> long trong
            # mot doan hay mot o bang.
            if self.loai == "chapnum":
                self._dong_khoi()
        elif tag == "div":
            self._dong_khoi()
            if any(k[0] == "box_mo" for k in self.khoi[-40:]):
                pass

    def handle_data(self, data):
        if self.trong_script or self.trong_style:
            return
        if any(t[0].startswith("SKIP") for t in self.ngan):
            return
        if self.runs is None:
            return
        if self.loai == "pre":
            self.runs.append((data, False, True))
        else:
            chu = re.sub(r"\s+", " ", data)
            if chu:
                self.runs.append((chu, self.dam > 0, self.mono > 0))


def doc_html():
    r = DocReader()
    r.feed(NGUON.read_text(encoding="utf-8"))
    r._dong_khoi()
    return r.khoi


# ---------------------------------------------------------------------------
# 3. DỰNG TỆP .DOCX
# ---------------------------------------------------------------------------

def dat_nen(o, ma_mau):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tc = OxmlElement("w:shd")
    tc.set(qn("w:val"), "clear")
    tc.set(qn("w:fill"), ma_mau)
    o.get_or_add_tcPr().append(tc) if hasattr(o, "get_or_add_tcPr") else None


def viet_runs(doan, runs, mono_mac_dinh=False):
    from docx.shared import Pt
    for chu, dam, mono in runs:
        r = doan.add_run(chu)
        r.bold = bool(dam)
        if mono or mono_mac_dinh:
            r.font.name = "Consolas"
            r.font.size = Pt(9)


def dung_docx(khoi, anh):
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, Inches, RGBColor

    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)

    # --- trang bìa ---
    tieu = d.add_heading("Phần mềm xếp câu lạc bộ chạy thế nào", level=0)
    tieu.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = d.add_paragraph(
        "Báo cáo kỹ thuật · dự án rbda-kiosk\n"
        "Toàn bộ đường đi của chương trình, kèm sơ đồ, mô phỏng và trích dẫn "
        "tới từng dòng mã nguồn.")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = d.add_paragraph(
        "Tệp này được SINH RA từ BAO_CAO_CACH_CHAY.html bằng "
        "tao_bao_cao_docx.py — không gõ tay. Bản web có hai mô phỏng bấm được; "
        "ở đây chúng được chụp lại thành từng bước.")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.italic = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x5B, 0x65, 0x70)
    d.add_page_break()

    i = 0
    while i < len(khoi):
        loai, ndung = khoi[i]
        i += 1

        if loai == "chapnum":
            p = d.add_paragraph()
            viet_runs(p, ndung)
            for r in p.runs:
                r.font.size = Pt(9)
                r.font.color.rgb = RGBColor(0x7A, 0x53, 0x10)
                r.bold = True
        elif loai == "h2":
            d.add_page_break()
            h = d.add_heading(level=1)
            viet_runs(h, ndung)
        elif loai == "h3":
            viet_runs(d.add_heading(level=2), ndung)
        elif loai == "h4":
            viet_runs(d.add_heading(level=3), ndung)
        elif loai == "deck":
            p = d.add_paragraph()
            viet_runs(p, ndung)
            for r in p.runs:
                r.italic = True
                r.font.color.rgb = RGBColor(0x5B, 0x65, 0x70)
        elif loai == "p":
            viet_runs(d.add_paragraph(), ndung)
        elif loai == "box_title":
            p = d.add_paragraph()
            viet_runs(p, ndung)
            for r in p.runs:
                r.bold = True
                r.font.color.rgb = RGBColor(0x7A, 0x53, 0x10)
        elif loai == "blockquote":
            p = d.add_paragraph(style="Intense Quote")
            viet_runs(p, ndung)
        elif loai in ("li_c", "li_o"):
            p = d.add_paragraph(
                style="List Bullet" if loai == "li_c" else "List Number")
            viet_runs(p, ndung)
        elif loai == "caption":
            p = d.add_paragraph()
            viet_runs(p, ndung)
            for r in p.runs:
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(0x5B, 0x65, 0x70)
        elif loai == "pre":
            chu = "".join(r[0] for r in ndung).strip("\n")
            p = d.add_paragraph()
            r = p.add_run(chu)
            r.font.name = "Consolas"
            r.font.size = Pt(8.5)
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(10)
        elif loai == "bang":
            hang = ndung
            so_cot = max(len(h) for h in hang)
            t = d.add_table(rows=0, cols=so_cot)
            t.style = "Light Grid Accent 1"
            for k, h in enumerate(hang):
                o = t.add_row().cells
                for j in range(so_cot):
                    o[j].text = ""
                    if j < len(h):
                        pr = o[j].paragraphs[0]
                        viet_runs(pr, h[j])
                        if k == 0:
                            for rr in pr.runs:
                                rr.bold = True
                        for rr in pr.runs:
                            rr.font.size = Pt(9)
            d.add_paragraph()
        elif loai == "anh":
            p = anh.get(ndung)
            if p and p.exists():
                d.add_picture(str(p), width=Inches(6.3))
                d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif loai == "mo_phong":
            ten_sim = MO_PHONG[ndung][0] if ndung < len(MO_PHONG) else None
            if ten_sim:
                p = d.add_paragraph()
                r = p.add_run(
                    "Mô phỏng tương tác — bản web cho phép bấm từng bước. "
                    "Dưới đây là toàn bộ các bước, chụp từ chính trang đó:")
                r.italic = True
                r.font.size = Pt(9.5)
                b = 0
                while True:
                    pa = anh.get(f"{ten_sim}:{b}")
                    if not pa or not pa.exists():
                        break
                    d.add_picture(str(pa), width=Inches(6.0))
                    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    b += 1
        elif loai == "box_mo":
            pass

    d.save(str(DICH))
    return DICH


def main():
    if not NGUON.exists():
        sys.exit("Khong tim thay %s" % NGUON)
    print("1/3 · chup so do va mo phong tu trang HTML...")
    try:
        anh = chup_anh()
    except Exception as e:
        print("   KHONG chup duoc anh (%s)." % e)
        print("   Van sinh .docx nhung SE THIEU HINH. Cai playwright roi chay lai.")
        anh = {}
    print("      %d anh" % len(anh))
    print("2/3 · doc BAO_CAO_CACH_CHAY.html...")
    khoi = doc_html()
    print("      %d khoi noi dung" % len(khoi))
    print("3/3 · dung .docx...")
    p = dung_docx(khoi, anh)
    print("Xong: %s (%.1f KB)" % (p, p.stat().st_size / 1024))


if __name__ == "__main__":
    main()
