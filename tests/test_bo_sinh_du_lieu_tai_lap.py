"""Ba bộ sinh dữ liệu phải tái lập ĐÚNG TỪNG BYTE các tệp CSV đã commit.

Các tệp này được trích dẫn trong tài liệu nghiên cứu (số em trắng tay, tỉ lệ
nguyện vọng 1...). Sửa bộ sinh mà tệp ra khác đi là các con số đó không còn
tính lại được — và trước đây không có gì bắt được điều đó.
"""

import filecmp
import importlib.util
import os

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize("thu_muc, tep", [
    ("bo_can_bang", "tao_bo_can_bang.py"),
    ("bo_nhieu_buoi", "tao_bo_nhieu_buoi.py"),
    ("bo_sau_buoi", "tao_bo_sau_buoi.py"),
])
def test_bo_sinh_tai_lap_dung_tep_da_commit(tmp_path, monkeypatch, thu_muc, tep):
    duong = os.path.join(GOC, "du_lieu_test", thu_muc, tep)
    spec = importlib.util.spec_from_file_location("bo_sinh_" + thu_muc, duong)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "GOC", str(tmp_path))
    mod.sinh()

    that = os.path.join(GOC, "du_lieu_test", thu_muc)
    ra = sorted(f for f in os.listdir(tmp_path) if f.endswith(".csv"))
    assert ra, "bo sinh khong ghi tep nao"
    for f in ra:
        assert filecmp.cmp(os.path.join(tmp_path, f), os.path.join(that, f), shallow=False), f
