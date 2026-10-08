"""Canh chuyện pywebview DÒ đối tượng API — lỗi từng làm treo hẳn app.

TRIỆU CHỨNG ĐÃ GẶP
Cửa sổ ứng dụng mở ra, tiêu đề ghi **"(Not Responding)"**, giao diện báo
"Không kết nối được với phần lõi chương trình". Tiến trình treo thật, không
phải chậm.

NGUYÊN NHÂN
pywebview dựng `window.pywebview.api` bằng cách DÒ đối tượng API. Luật của
nó, nguyên văn trong `webview/util.py` (hàm `get_functions` bên trong
`inject_pywebview`):

    for name in dir(obj):
        if name.startswith('_'):
            continue                              # <- lối thoát DUY NHẤT
        attr = getattr(obj, name)                 # <- KÍCH HOẠT property
        ...
        elif inspect.isclass(attr) or (
                isinstance(attr, object) and not callable(attr)
                and hasattr(attr, '__module__')):
            get_functions(attr, ...)              # <- ĐỆ QUY vào attr

Cửa sổ pywebview không callable và có `__module__`. Nên khi `main.py` gọi
`set_window(window)` và API cất nó ở một thuộc tính **công khai**, pywebview
đệ quy vào chính cửa sổ của nó. Mà `dir()` cửa sổ đó có bốn property CHẶN
(`webview/window.py`):

    @property
    def width(self):
        self.events.shown.wait(15)               # chờ tới 15 giây
        width, _ = self.gui.get_size(self.uid)   # đọc Control.Size (WinForms)

`width`, `height`, `x`, `y` — mỗi cái chờ tới 15 giây, và `get_size` đọc
thuộc tính của một control WinForms **từ luồng khác luồng giao diện**. Luồng
dò bị chặn, `finish.js` không bao giờ chạy, `window.pywebview.api` mãi rỗng.

VÌ SAO LÂU MỚI LỘ
App chạy nhiều ngày ở **chế độ trình duyệt dự phòng**, nơi không có cửa sổ
pywebview nào để đệ quy vào. Bản vá gỡ dấu "tải từ Internet" làm đường cửa sổ
gốc chạy được lần đầu — và đụng ngay cái bẫy này.

File test này KHÔNG cần pywebview, không cần Windows. Nó áp đúng luật trên
lên đối tượng API của mình.
"""

import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import PipelineAPI  # noqa: E402
from recovery import RecoveryAPI  # noqa: E402


def pywebview_se_de_quy_vao(attr) -> bool:
    """Chép nguyên điều kiện đệ quy của `get_functions` trong webview/util.py."""
    return inspect.isclass(attr) or (
        isinstance(attr, object)
        and not callable(attr)
        and hasattr(attr, "__module__")
    )


def thuoc_tinh_pywebview_se_do(obj):
    """Những tên mà pywebview sẽ `getattr` khi dò `obj`."""
    return [ten for ten in dir(obj) if not ten.startswith("_")]


class CuaSoGia:
    """Giả làm cửa sổ pywebview: KHÔNG callable, CÓ `__module__`, và mọi
    property đều ghi lại khi bị đọc — đúng chỗ cửa sổ thật sẽ chặn 15 giây
    rồi đọc control WinForms chéo luồng."""

    def __init__(self):
        self.da_bi_doc = []

    def _ghi(self, ten):
        self.da_bi_doc.append(ten)
        return 0

    @property
    def width(self):
        return self._ghi("width")

    @property
    def height(self):
        return self._ghi("height")

    @property
    def x(self):
        return self._ghi("x")

    @property
    def y(self):
        return self._ghi("y")


def do_nhu_pywebview(obj, da_qua=None, ket=None):
    """Dò `obj` ĐÚNG như `get_functions` của pywebview, **kể cả phần đệ quy**.

    Phải đệ quy thật thì mới đo được cái cần đo: bản thân việc chạm tới
    thuộc tính của cửa sổ mới là chỗ chặn 15 giây. Dừng ở một tầng thì test
    xanh mà chẳng chứng minh được gì.

    `da_qua` chép lại `exposed_objects` của pywebview — chặn đệ quy vô hạn.
    Trả về danh sách đường dẫn tới những thuộc tính bị đệ quy vào.
    """
    da_qua = [] if da_qua is None else da_qua
    ket = [] if ket is None else ket
    if id(obj) in da_qua:
        return ket
    da_qua.append(id(obj))

    for ten in thuoc_tinh_pywebview_se_do(obj):
        attr = getattr(obj, ten)          # <- chỗ property bị KÍCH HOẠT
        if pywebview_se_de_quy_vao(attr):
            ket.append(ten)
            do_nhu_pywebview(attr, da_qua, ket)
    return ket


# --------------------------------------------------------------------------
# Test chính: sau khi gắn cửa sổ, KHÔNG thuộc tính công khai nào được là một
# đối tượng mà pywebview sẽ đệ quy vào.
# --------------------------------------------------------------------------

def test_api_khong_de_lo_doi_tuong_nao_cho_pywebview_de_quy_vao(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"))
    api._set_window(CuaSoGia())

    lo = do_nhu_pywebview(api)
    assert lo == [], (
        "Thuộc tính công khai %s là đối tượng — pywebview sẽ ĐỆ QUY vào đó "
        "khi dựng cầu nối. Nếu đó là cửa sổ pywebview thì app TREO HẲN. "
        "Đổi tên thành _%s để `get_functions` bỏ qua trước khi getattr."
        % (lo, lo[0] if lo else "")
    )


def test_cua_so_khong_he_bi_cham_toi_khi_pywebview_do_api(tmp_path):
    """Test mạnh hơn: không chỉ 'không đệ quy', mà cửa sổ KHÔNG BỊ ĐỌC lần
    nào. Trên cửa sổ thật, mỗi lần đọc là một lần chờ 15 giây cộng một lần
    chạm control WinForms chéo luồng."""
    cua_so = CuaSoGia()
    api = PipelineAPI(str(tmp_path / "app.db"))
    api._set_window(cua_so)

    do_nhu_pywebview(api)
    assert cua_so.da_bi_doc == [], (
        "pywebview chạm vào %s của cửa sổ. Trên Windows, mỗi cái là "
        "events.shown.wait(15) + đọc Control.Size từ luồng khác luồng giao "
        "diện — đúng thứ làm cửa sổ ghi 'Not Responding'." % cua_so.da_bi_doc
    )


def test_man_hinh_phuc_hoi_cung_sach(tmp_path):
    """RecoveryAPI là màn hình hiện ra KHI CSDL ĐÃ HỎNG. Treo nốt ở đó thì
    không còn đường nào."""
    api = RecoveryAPI(str(tmp_path / "app.db"), "loi gia de dung test")
    assert do_nhu_pywebview(api) == []


# --------------------------------------------------------------------------
# Canh phía main.py: nó phải gọi đúng tên có gạch dưới. Đổi một bên mà quên
# bên kia thì `hasattr` lặng lẽ trả False, cửa sổ không bao giờ được gắn, và
# không ai biết — lỗi im lặng, đúng loại khó tìm nhất.
# --------------------------------------------------------------------------

def test_main_goi_dung_ten_co_gach_duoi():
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = open(os.path.join(goc, "main.py"), encoding="utf-8").read()
    assert '_set_window' in src
    assert 'hasattr(js_api, "set_window")' not in src, (
        "main.py còn dò tên công khai — sẽ luôn trả False sau khi đổi tên.")
    assert hasattr(PipelineAPI, "_set_window")
    assert not hasattr(PipelineAPI, "set_window"), (
        "Còn tên công khai thì pywebview vẫn phơi nó ra JS, và một trang bất "
        "kỳ có thể gọi thẳng hàm đó để nhét gì đó vào.")


# --------------------------------------------------------------------------
# Canh chẩn đoán: nhật ký không được ghi "THÀNH CÔNG" trước khi thật sự xong.
# Đúng lúc app treo trong webview.start(), nhật ký cũ vẫn ghi "mo THANH CONG"
# — nói dối đúng lúc cần sự thật nhất.
# --------------------------------------------------------------------------

def test_nhat_ky_khong_bao_thanh_cong_truoc_khi_mo_xong():
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = open(os.path.join(goc, "main.py"), encoding="utf-8").read()
    truoc = src.index("webview.start()")
    assert "mo THANH CONG" not in src[:truoc], (
        "main.py ghi 'THANH CONG' TRƯỚC webview.start(), mà chính chỗ đó đã "
        "từng treo.")
