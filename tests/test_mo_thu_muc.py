# -*- coding: utf-8 -*-
"""Nút "Mở thư mục" sau khi xuất — mở được đúng chỗ, và KHÔNG mở chỗ khác.

`mo_thu_muc` gọi được từ JavaScript, nên nó là một cửa chạy chương trình
ngoài. Test canh hai chiều: thư mục xuất thì mở, mọi thứ khác thì từ chối
và KHÔNG gọi tới trình mở thư mục.
"""

import os
import sys

import pytest



@pytest.fixture
def ghi_lai(monkeypatch):
    goi = []
    if sys.platform == "win32":
        monkeypatch.setattr(os, "startfile", lambda p: goi.append(p), raising=False)
    else:
        import subprocess

        class Gia:
            def __init__(self, lenh, **kw):
                goi.append(lenh[-1])
        monkeypatch.setattr(subprocess, "Popen", Gia)
    return goi


def test_mo_thu_muc_chua_tep_vua_xuat(api, ghi_lai):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    api.create_student_if_missing("HS1", "An")
    p = api.export_hoc_sinh_csv(["HS1"])["data"]["path"]
    r = api.mo_thu_muc(p)
    assert r["ok"], r["errors"]
    assert ghi_lai == [os.path.realpath(os.path.dirname(p))]


def test_mo_thang_thu_muc_du_lieu_dau_vao(api, ghi_lai):
    api.create_or_update_club("A", "CLB A", 5, 0, "")
    d = api.export_du_lieu_dau_vao()["data"]["dir"]
    assert api.mo_thu_muc(d)["ok"]
    assert ghi_lai == [os.path.realpath(d)]


@pytest.mark.parametrize("duong", [
    "/", "/etc/passwd", os.path.expanduser("~"),
    "{xuat}/../../..", "", "/khong/co/thu/muc/nay",
])
def test_ngoai_cho_xuat_thi_tu_choi_va_khong_goi_gi(api, ghi_lai, duong):
    duong = duong.replace("{xuat}", os.environ["RBDA_THU_MUC_TAI_VE"])
    r = api.mo_thu_muc(duong)
    assert not r["ok"]
    assert r["errors"][0]["code"] == "thu_muc_khong_hop_le"
    assert ghi_lai == []


def test_lien_ket_tuong_trung_tro_ra_ngoai_bi_chan(api, ghi_lai):
    # Ngoai CA HAI goc hop le (Tai xuong va thu muc app.db — o day la tmp_path).
    import tempfile
    ngoai = tempfile.mkdtemp()
    lk = os.path.join(os.environ["RBDA_THU_MUC_TAI_VE"], "lk")
    try:
        os.symlink(str(ngoai), lk)
    except (OSError, NotImplementedError):
        pytest.skip("may khong tao duoc symlink")
    assert not api.mo_thu_muc(lk)["ok"]
    assert ghi_lai == []
