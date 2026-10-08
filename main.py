"""
main.py
=======
Điểm khởi động ứng dụng kiosk. Tạo cửa sổ pywebview, gắn PipelineAPI
làm js_api để index.html và js/*.js gọi qua window.pywebview.api.*

Cách chạy:
    python3 main.py                    # dùng app.db cùng thư mục main.py
    python3 main.py /duong/dan/khac.db # chỉ định DB khác
"""

import os
import sys
import traceback

import browser_host
import chan_doan
from api import PipelineAPI
from recovery import RecoveryAPI

APP_TITLE = "Sắp xếp Câu lạc bộ — RB-DA"

# QUAN TRỌNG khi đóng gói bằng PyInstaller: __file__ của main.py KHÔNG
# trỏ tới thư mục chứa file .exe thật — nó trỏ vào thư mục tài nguyên
# tạm (_internal/ ở chế độ onedir, hoặc thư mục giải nén tạm ở chế độ
# onefile). Nếu dùng __file__ để tính đường dẫn app.db, DB sẽ bị ghi
# nhầm vào bên trong _internal/ (đã tự phát hiện bug này bằng cách
# build thật và chạy thử).
#
#   BASE_DIR      -> nơi ĐẶT app.db (phải là thư mục chứa .exe thật,
#                     để dữ liệu không bị mất khi build lại/cập nhật app)
#   RESOURCE_DIR  -> nơi ĐỌC tài nguyên đã đóng gói (index.html,
#                     style.css, js/*.js, assets/fonts/) — ở chế độ đóng
#                     gói, đây là _internal/ (hoặc thư mục tạm), khác
#                     với BASE_DIR; ở chế độ chạy thường (python3
#                     main.py), cả hai trùng nhau.
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = getattr(sys, "_MEIPASS", BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = BASE_DIR


def resolve_db_path() -> str:
    if len(sys.argv) > 1:
        return os.path.abspath(sys.argv[1])
    return os.path.join(BASE_DIR, "app.db")


def _show_ui(title: str, page: str, js_api, width: int, height: int,
             min_size: tuple) -> None:
    """
    Hiện giao diện `page` với backend `js_api`, THỬ HAI CÁCH theo thứ tự:

      1. Cửa sổ pywebview (ưu tiên — cửa sổ gốc của hệ điều hành).
      2. NẾU pywebview hỏng: máy chủ cục bộ + một CỬA SỔ RIÊNG của trình
         duyệt nhân Chromium (Edge/Chrome), mở bằng cờ `--app=` nên KHÔNG
         có thanh địa chỉ, KHÔNG có tab — nhìn và dùng như ứng dụng
         desktop. Chỉ khi máy không có trình duyệt Chromium nào thì mới
         đành mở tab thường (xem browser_host.py).

    VÌ SAO CẦN CÁCH 2: trên Windows, pywebview bắt buộc đi qua
    pythonnet -> .NET Framework, và mắt xích này đã hỏng thật trên máy
    người dùng sau khi đóng gói bằng PyInstaller:

        RuntimeError: Failed to resolve Python.Runtime.Loader.Initialize
        from ...\\_internal\\pythonnet\\runtime\\Python.Runtime.dll

    Trước đây lỗi đó làm cả tiến trình chết kèm hộp thoại khó hiểu, app
    hoàn toàn không dùng được. Giờ nó chỉ khiến app đổi cách vẽ cửa sổ —
    TOÀN BỘ tính năng giữ nguyên, vì js/*.js/recovery.js vẫn gọi backend
    qua đúng `window.pywebview.api.*` như cũ (browser_host dựng sẵn cầu
    nối giả lập). Với cờ `--app=`, người dùng vẫn thấy MỘT CỬA SỔ ỨNG
    DỤNG RIÊNG, không phải một tab lẫn trong trình duyệt.
    """
    # Gỡ dấu "tải từ Internet" TRƯỚC khi nạp webview. Windows gắn dấu đó
    # vào mọi tệp giải nén từ .zip tải về, và .NET Framework từ chối nạp
    # assembly mang dấu — khớp đúng triệu chứng: lỗi nêu rõ đường dẫn tới
    # Python.Runtime.dll, tức tệp CÓ đó, .NET tìm thấy nhưng không nạp.
    if getattr(sys, "frozen", False):
        ket = chan_doan.go_dau_tai_ve(RESOURCE_DIR)
        chan_doan.ghi(BASE_DIR, "go dau tai-ve trong %s: %r" % (RESOURCE_DIR, ket))

    try:
        import webview

        window = webview.create_window(
            title, os.path.join(RESOURCE_DIR, page), js_api=js_api,
            width=width, height=height, min_size=min_size,
        )
        if hasattr(js_api, "_set_window"):
            # Cho phép các tính năng dùng hộp thoại gốc của hệ điều hành
            # sau này (hiện chưa tính năng nào bắt buộc phải có window ref).
            #
            # TEN PHAI CO DAU GACH DUOI. Doc chu thich trong
            # PipelineAPI._set_window — de ten cong khai thi pywebview de quy
            # vao chinh cua so cua no va TREO HAN app.
            js_api._set_window(window)
        # KHONG duoc ghi "THANH CONG" o day. webview.start() ben duoi moi la
        # cho that su mo cua so, va no da tung TREO ngay tai do — luc ay nhat
        # ky van ghi "THANH CONG", tuc noi doi dung luc can su that nhat.
        chan_doan.ghi(BASE_DIR, "dang mo cua so goc (pywebview)...")
        webview.start()
        chan_doan.ghi(BASE_DIR, "cua so goc (pywebview) da dong binh thuong")
        return
    except (KeyboardInterrupt, SystemExit):
        # Nguoi dung CHU DONG dung (Ctrl+C, dong tien trinh) — khong phai
        # pywebview hong. Truoc day nhanh duoi nuot ca hai va mo luon che do
        # trinh duyet: bam Ctrl+C de tat thi app lai bat len cua so khac.
        raise
    except BaseException:
        # Nuot MOI loai loi con lai (ke ca khong phai Exception) roi thu
        # cach 2 — con mot duong chay duoc van hon la chet kem stack trace.
        #
        # NHUNG PHAI GHI LAI VET LOI VAO TEP. Truoc day cho ra sys.stderr,
        # ma ban build console=False khong co stderr nao — vet loi bi vut
        # di dung luc no xay ra, va ba phien lam viec phai DOAN nguyen
        # nhan. Ghi ra tep canh app.db thi lan sau doc duoc nguyen van.
        chan_doan.ghi_ngoai_le(
            BASE_DIR, "cua so goc (pywebview) HONG, chuyen sang trinh duyet:")
        # Ban dong goi console=False: PyInstaller dat sys.stderr = None. Goi
        # .write() tren None se nem AttributeError NGAY TRONG khoi except nay
        # va chan luon duong du phong ben duoi — dung luc can no nhat.
        if sys.stderr is not None:
            sys.stderr.write(
                "pywebview khong khoi dong duoc, chuyen sang che do trinh duyet:\n"
                + traceback.format_exc()
            )

    chan_doan.ghi(BASE_DIR, "dang chay bang CHE DO TRINH DUYET (du phong)")
    browser_host.serve(js_api, RESOURCE_DIR, page, width=width, height=height)


def main() -> None:
    db_path = resolve_db_path()

    # KHÔNG BAO GIỜ được chết ngầm: nếu app.db hỏng/mất, PipelineAPI(...)
    # (gọi init_db bên trong) ném exception NGAY TẠI ĐÂY — TRƯỚC khi có
    # bất kỳ cửa sổ nào được tạo. Không bọc try/except thì tiến trình
    # thoát với exit code 1 và KHÔNG cửa sổ nào hiện ra — đặc biệt
    # nghiêm trọng trên bản build Windows console=False (kiosk), nơi
    # không có terminal nào để người vận hành thấy lỗi (xem
    # kế hoạch kiểm thử mất dữ liệu — artifact, xem BAN_GIAO.md mục 8, nhóm B). Thay vào đó: mở màn hình PHỤC HỒI
    # (recovery.html/recovery.py) cho phép khôi phục từ bản sao lưu tự
    # động (xem PipelineAPI._backup_db trong api.py) hoặc bắt đầu lại
    # với DB trống.
    try:
        api = PipelineAPI(db_path)
    except Exception as e:
        _show_ui(
            APP_TITLE + " — Phục hồi dữ liệu",
            "recovery.html",
            RecoveryAPI(db_path, f"{e}\n\n{traceback.format_exc()}"),
            width=900, height=700, min_size=(700, 560),
        )
        return

    _show_ui(
        APP_TITLE, "index.html", api,
        width=1280, height=800, min_size=(1024, 640),
    )


if __name__ == "__main__":
    main()
