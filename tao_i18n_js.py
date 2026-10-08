"""
tao_i18n_js.py
==============
Sinh `i18n_loi.js` từ `MESSAGES` trong `i18n_errors.py`.

`i18n_errors.py` là NGUỒN DUY NHẤT của bảng thông báo lỗi song ngữ. Trước
đây bảng này có hai bản chép tay — một ở Python, một ở `i18n.js` — và một
test bắt chúng lệch nhau. Test đó bắt được lệch, nhưng mỗi lần thêm một
thông báo vẫn phải gõ hai lần, và trên máy không có Node.js thì test tự bỏ
qua, tức là lệch vẫn lọt.

Giờ chỉ sửa `i18n_errors.py`, rồi chạy:

    python tao_i18n_js.py

`tests/test_i18n_sync.py` kiểm tệp sinh ra khớp từng byte với đầu ra của
tệp này, bằng Python thuần — không cần Node.js, chạy được cả trên Windows.

Vì sao sinh ra một tệp .js chứ không để trang đọc thẳng một tệp .json: trang
chạy trong pywebview và cả khi mở thẳng từ đĩa, nơi `fetch()` tệp cục bộ bị
trình duyệt chặn. Một thẻ `<script>` thì luôn nạp được.
"""

import io
import json
import os

GOC = os.path.dirname(os.path.abspath(__file__))
TEP_RA = os.path.join(GOC, "i18n_loi.js")

_DAU_TEP = """\
/* ==========================================================================
   i18n_loi.js — TỆP SINH TỰ ĐỘNG, KHÔNG SỬA TAY.
   ==========================================================================
   Nguồn: MESSAGES trong i18n_errors.py. Sửa ở đó rồi chạy:
       python tao_i18n_js.py
   tests/test_i18n_sync.py đỏ ngay nếu tệp này lệch khỏi nguồn.
   ========================================================================== */
"""


def noi_dung() -> str:
    """Nội dung đúng của `i18n_loi.js` — tất định, cùng nguồn ra cùng byte."""
    from i18n_errors import MESSAGES

    bang = json.dumps(MESSAGES, ensure_ascii=False, indent=2)
    return _DAU_TEP + "window.I18N_ERROR_MESSAGES = " + bang + ";\n"


def main() -> None:
    with io.open(TEP_RA, "w", encoding="utf-8", newline="\n") as f:
        f.write(noi_dung())
    print("Da ghi", TEP_RA)


if __name__ == "__main__":
    main()
