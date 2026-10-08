import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from api import PipelineAPI


@pytest.fixture
def api(tmp_path):
    return PipelineAPI(str(tmp_path / "app.db"))

@pytest.fixture
def api_factory(tmp_path):
    """Dựng NHIỀU PipelineAPI độc lập trong cùng một test.

    Cần cho các test quét nhiều seed: mỗi seed phải chạy trên một CSDL
    sạch, nếu không dữ liệu của lần trước còn nguyên và làm lệch kết quả.
    """
    dem = {"n": 0}

    def tao():
        dem["n"] += 1
        thu_muc = tmp_path / ("db%d" % dem["n"])
        thu_muc.mkdir()
        return PipelineAPI(str(thu_muc / "app.db"))

    return tao

@pytest.fixture(autouse=True)
def khong_ghi_vao_thu_muc_tai_ve_that(tmp_path, monkeypatch):
    """Chốt chặn cho TOÀN BỘ bộ test.

    `export_csv("")` giờ đặt tệp vào thư mục Tải xuống của người dùng.
    Không có fixture này thì chạy pytest trên máy thật sẽ rải tệp kết
    quả vào Downloads của người đó — bộ test không bao giờ được để lại
    rác ngoài thư mục tạm của chính nó.
    """
    cho_tam = tmp_path / "TaiXuong_gia"
    cho_tam.mkdir(exist_ok=True)
    monkeypatch.setenv("RBDA_THU_MUC_TAI_VE", str(cho_tam))
