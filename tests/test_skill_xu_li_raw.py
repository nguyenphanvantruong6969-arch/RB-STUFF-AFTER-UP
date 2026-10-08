# -*- coding: utf-8 -*-
"""Skill `xu-li-raw-forms`: raw Google Forms -> Sổ nhập CLB của phần mềm.

Phép kiểm chính giống test_skill_sinh_du_lieu.py: KHÔNG phải "script chạy
không lỗi", mà là nạp kết quả vào phần mềm thật và đếm cảnh báo. Raw giả dựng
đúng định dạng mau_forms_thi_clb/DINH_DANG_RAW.md, có cài sẵn từng loại bất
thường để kiểm báo cáo bắt được.
"""

import base64
import importlib.util
import io
import os
import sys

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(GOC, ".claude", "skills", "xu-li-raw-forms", "scripts", "xu_li_raw.py")
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

from api import PipelineAPI  # noqa: E402


@pytest.fixture(scope="module")
def xr():
    spec = importlib.util.spec_from_file_location("xu_li_raw", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def de():
    import tao_google_forms as tg
    return tg.du_lieu_gs()


# ------------------------------------------------------------ dựng raw giả

class Raw:
    """Ghi raw đúng như ghiRaw_ trong TAO_GOOGLE_FORM.gs."""

    def __init__(self, xr, de):
        self.xr, self.de, self.rows, self.so = xr, de, [], 0
        self.clb = {c["id"]: (d, c) for d in de for c in d["clubs"]}

    def phieu(self, sid, ten, buoi=None, email="", sai_forms=()):
        """buoi: {ma_buoi: {"hang": [club_id theo hạng], "tick": [...], "lam": {club_id: số câu đúng}}}"""
        self.so += 1
        buoi = buoi or {}

        def dong(ma, loai, b="", club="", cau_so="", tl="", them=("",) * 7):
            self.rows.append([self.so, "2026-10-01 08:00:00", email, sid, "giu", ma, loai, b,
                              club, cau_so, "câu " + ma, tl] + list(them))
        dong("student_id", "thong_tin", tl=sid)
        dong("name", "thong_tin", tl=ten)
        for d in self.de:
            b = d["ma"]
            if b not in buoi:
                dong("di-" + b, "dang_ky_buoi", b, tl="Không, em bận buổi này")
                continue
            x = buoi[b]
            dong("di-" + b, "dang_ky_buoi", b, tl="Có")
            hang = x.get("hang", [c["id"] for c in d["clubs"]])
            for k, cid in enumerate(hang):
                dong(b, "xep_hang", b, cid, tl="Top %d" % (k + 1))
            for cid in x.get("tick", []):
                dong("chon-" + b, "chon_thi", b, cid, tl="%s (%s)" % (self.clb[cid][1]["name"], cid))
            truoc = None
            for cid, n_dung in x.get("lam", {}).items():
                ma = "thi-" + b if truoc is None else "thi-sau-" + truoc
                dong(ma, "cong_thi", b, cid, tl="%s (%s)" % (self.clb[cid][1]["name"], cid))
                truoc = cid
                for j, q in enumerate(self.clb[cid][1]["de"]):
                    dung = j < n_dung
                    tl = q["dung"] if dung else next(o for o in q["opts"] if o != q["dung"])
                    diem = 5 if dung else 0
                    forms = (5 - diem) if "%s-%d" % (cid, j + 1) in sai_forms else diem
                    dong("%s-%d" % (cid, j + 1), "de_thi", b, cid, j + 1, tl,
                         (q["dung"], int(dung), diem, 5, forms, 1, ""))

    def ghi(self, duong):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(self.xr.COT_RAW)
        for r in self.rows:
            ws.append([str(x) for x in r])
        wb.save(duong)


def ghi_dap_an(de, duong):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["buoi", "ten_buoi", "club_id", "ten_clb", "ma_cau", "cau_so", "cau_hoi",
               "lua_chon_a", "lua_chon_b", "lua_chon_c", "lua_chon_d", "dap_an_dung", "diem"])
    for d in de:
        for c in d["clubs"]:
            for j, q in enumerate(c["de"]):
                ws.append([d["ma"], d["ten"], c["id"], c["name"], "%s-%d" % (c["id"], j + 1),
                           str(j + 1), q["q"]] + q["opts"] + [q["dung"], "5"])
    wb.save(duong)


def ghi_clb(de, duong, bo=()):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["club_id", "name", "capacity", "reserve_capacity", "reserve_group", "buoi"])
    for d in de:
        for c in d["clubs"]:
            if c["id"] not in bo:
                ws.append([c["id"], c["name"], 10, 0, "", d["ma"]])
    wb.save(duong)


@pytest.fixture
def bo(tmp_path, xr, de):
    """Raw có đủ các loại bất thường."""
    r = Raw(xr, de)
    T2 = [c["id"] for c in de[0]["clubs"]]
    T4 = [c["id"] for c in de[2]["clubs"]]
    # HS001: bình thường, thi 2 CLB Thứ Hai, 1 CLB Thứ Tư
    r.phieu("HS001", "Học sinh Một", {
        "thu_2": {"tick": [T2[0], T2[2]], "lam": {T2[0]: 1, T2[2]: 2}},
        "thu_4": {"hang": list(reversed(T4)), "tick": [T4[5]], "lam": {T4[5]: 2}}},
        email="a@truong.vn")
    # HS002: làm bài CLB không tick; đáp án Forms lệch ở câu T2[0]-1
    r.phieu("HS002", "Học sinh Hai", {
        "thu_2": {"tick": [T2[0]], "lam": {T2[0]: 2, T2[1]: 2}}},
        sai_forms=("%s-1" % T2[0],))
    # HS003: tick mà không làm
    r.phieu("HS003", "Học sinh Ba", {"thu_2": {"tick": [T2[0], T2[3]], "lam": {T2[0]: 0}}})
    # Nộp trùng HS001, và cùng email với mã khác
    r.phieu("HS001", "Học sinh Một lần 2", {"thu_2": {"tick": [T2[1]], "lam": {T2[1]: 2}}})
    r.phieu("hs 04", "Mã gõ sai", {"thu_2": {"tick": [], "lam": {}}}, email="a@truong.vn")
    # Không có mã
    r.phieu("", "Không mã", {})
    r.ghi(str(tmp_path / "RAW_PHIEU.xlsx"))
    ghi_dap_an(de, str(tmp_path / "DAP_AN.xlsx"))
    ghi_clb(de, str(tmp_path / "01.xlsx"))
    return tmp_path, T2, T4


def _doc_so(xr, ra):
    """{student_id: em} theo dạng của skill: nguyen_vong {buoi: [...]}, diem {clb: điểm}."""
    _, hs = xr.sdl.doc_bo(str(ra))
    return {h["student_id"]: h for h in hs}


# ------------------------------------------------------------------ test

def test_nap_sach_vao_phan_mem_that(bo, xr):
    thu, T2, T4 = bo
    ra = thu / "ra"
    assert xr.main(["--raw", str(thu / "RAW_PHIEU.xlsx"), "--dap-an", str(thu / "DAP_AN.xlsx"),
                    "--clb", str(thu / "01.xlsx"), "--ra", str(ra)]) == 0
    assert sorted(os.listdir(str(ra))) == ["BAO_CAO_BAT_THUONG.md", "SO_NHAP_CLB.xlsx"]
    api = PipelineAPI(str(thu / "app.db"), thu_muc_xuat=str(thu))
    with open(str(ra / "SO_NHAP_CLB.xlsx"), "rb") as f:
        kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"] and not (kq["data"].get("warnings") or []), kq
    assert api.run_pipeline(seed=42)["ok"]


def test_cham_dung_va_bo_dung_cho(bo, xr):
    thu, T2, T4 = bo
    ra = thu / "ra"
    xr.chay(str(thu / "RAW_PHIEU.xlsx"), str(ra), str(thu / "DAP_AN.xlsx"), str(thu / "01.xlsx"))
    em = _doc_so(xr, ra)
    diem = {sid: h["diem"] for sid, h in em.items()}
    assert diem["HS001"] == {T2[0]: "5", T2[2]: "10", T4[5]: "10"}   # phiếu đầu, không phải lần 2
    assert diem["HS002"] == {T2[0]: "10"}                            # bài không tick bị bỏ
    assert diem["HS003"] == {T2[0]: "0"}
    assert set(em) == {"HS001", "HS002", "HS003", "hs 04"}
    assert em["HS001"]["nguyen_vong"]["thu_4"][0] == T4[-1]          # sắp theo hạng em chọn


def test_bao_cao_bat_du_bat_thuong(bo, xr):
    thu, T2, T4 = bo
    ra = thu / "ra"
    _, _, bc = xr.chay(str(thu / "RAW_PHIEU.xlsx"), str(ra), str(thu / "DAP_AN.xlsx"),
                       str(thu / "01.xlsx"))
    assert bc["phieu_trung"] and "giữ phiếu 1" in bc["phieu_trung"][0]
    assert bc["phieu_khong_ma"] == ["Phiếu 6"]
    assert any("hs 04" in x for x in bc["ma_sai_dang"])
    assert bc["email_hai_ma"] and "HS001" in bc["email_hai_ma"][0]
    assert bc["dap_an_forms_lech"] == ["%s-1: 1 bài Forms chấm khác đáp án gốc" % T2[0]]
    assert bc["lam_khong_tick"] == ["HS002: %s" % T2[1]]
    assert bc["tick_khong_lam"] == ["HS003: %s" % T2[3]]
    with io.open(str(ra / "BAO_CAO_BAT_THUONG.md"), encoding="utf-8") as f:
        bao_cao = f.read()
    assert "—" not in bao_cao and "–" not in bao_cao
    assert "HS002" in bao_cao


def test_khong_co_chi_tieu_thi_cot_chi_tieu_de_trong(bo, xr):
    thu, _, _ = bo
    ra = thu / "ra"
    assert xr.main(["--raw", str(thu / "RAW_PHIEU.xlsx"), "--dap-an", str(thu / "DAP_AN.xlsx"),
                    "--ra", str(ra)]) == 0
    ws = openpyxl.load_workbook(str(ra / "SO_NHAP_CLB.xlsx"))["1. CLB"]
    dong = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0]]
    assert len(dong) == 50 and all(r[2] in (None, "") for r in dong)
    with io.open(str(ra / "BAO_CAO_BAT_THUONG.md"), encoding="utf-8") as f:
        assert "Chưa có chỉ tiêu CLB" in f.read()


def test_clb_lay_tu_so_nhap_da_dien_chi_tieu(bo, xr):
    """Vòng làm việc thật: chạy lần 1 không có chỉ tiêu, nhà trường điền cột
    Chỉ tiêu ngay trong sổ, chạy lại với --clb là chính sổ đó."""
    thu, _, _ = bo
    lan1 = thu / "lan1"
    assert xr.main(["--raw", str(thu / "RAW_PHIEU.xlsx"), "--dap-an", str(thu / "DAP_AN.xlsx"),
                    "--ra", str(lan1)]) == 0
    wb = openpyxl.load_workbook(str(lan1 / "SO_NHAP_CLB.xlsx"))
    ws = wb["1. CLB"]
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 1).value:
            ws.cell(r, 3).value = 7
    wb.save(str(thu / "so_da_dien.xlsx"))

    lan2 = thu / "lan2"
    assert xr.main(["--raw", str(thu / "RAW_PHIEU.xlsx"), "--dap-an", str(thu / "DAP_AN.xlsx"),
                    "--clb", str(thu / "so_da_dien.xlsx"), "--ra", str(lan2)]) == 0
    clb, _ = xr.sdl.doc_bo(str(lan2))
    assert len(clb) == 50 and {c["capacity"] for c in clb} == {7}


def test_dau_vao_hong_thi_khong_ghi_gi(bo, xr, de, tmp_path):
    thu, T2, _ = bo
    # Tệp chỉ tiêu thiếu một CLB có trong raw.
    ghi_clb(de, str(thu / "01_thieu.xlsx"), bo=(T2[0],))
    ra = tmp_path / "ra_hong"
    assert xr.main(["--raw", str(thu / "RAW_PHIEU.xlsx"), "--dap-an", str(thu / "DAP_AN.xlsx"),
                    "--clb", str(thu / "01_thieu.xlsx"), "--ra", str(ra)]) == 1
    assert not ra.exists()
    # Raw thiếu cột.
    wb = openpyxl.Workbook()
    wb.active.append(["phieu_so", "student_id"])
    wb.save(str(thu / "hong.xlsx"))
    assert xr.main(["--raw", str(thu / "hong.xlsx"), "--ra", str(ra)]) == 1
    assert not ra.exists()


def test_cot_raw_khop_ma_google(xr):
    """Skill và TAO_GOOGLE_FORM.gs phải cùng một danh sách cột."""
    import re
    import tao_google_forms as tg
    gs = tg.noi_dung()
    cot = re.findall(r"'([a-z_]+)'", re.search(r"const COT_RAW = \[(.*?)\];", gs, re.S).group(1))
    assert cot == xr.COT_RAW


def test_clb_chon_o_nhieu_top_khong_chan_ca_bo(tmp_path, xr, de):
    """Danh sách thả xuống không chặn chọn trùng: skill giữ Top cao nhất, không để soat() chặn."""
    T2 = [c["id"] for c in de[0]["clubs"]]
    r = Raw(xr, de)
    r.phieu("HS001", "Một", {"thu_2": {"hang": [T2[2], T2[0], T2[2]], "tick": [T2[0]], "lam": {T2[0]: 2}}})
    r.ghi(str(tmp_path / "RAW_PHIEU.xlsx"))
    ghi_dap_an(de, str(tmp_path / "DAP_AN.xlsx"))
    ghi_clb(de, str(tmp_path / "01.xlsx"))
    _, hs, bc = xr.chay(str(tmp_path / "RAW_PHIEU.xlsx"), str(tmp_path / "ra"),
                        str(tmp_path / "DAP_AN.xlsx"), str(tmp_path / "01.xlsx"))
    assert hs[0]["nguyen_vong"]["thu_2"] == [T2[2], T2[0]]
    assert bc["clb_nhieu_top"] == ["HS001 · thu_2: %s ở Top 1 và Top 3, giữ Top 1" % T2[2]]
