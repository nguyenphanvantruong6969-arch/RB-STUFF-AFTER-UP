"""Tìm Chromium cho các test giao diện (Playwright).

Trước đây mười một tệp test tự ghi cứng một đường dẫn chỉ có trên máy phát
triển (`/opt/pw-browsers/chromium-1194/...`). Máy khác — kể cả máy CI — không
có đúng đường dẫn đó, nên TOÀN BỘ test giao diện lặng lẽ bị bỏ qua mà bộ test
vẫn báo xanh. Giờ tìm theo thứ tự:

  1. biến môi trường RBDA_TEST_CHROMIUM (chỉ định thẳng);
  2. bất kỳ bản Chromium nào trong /opt/pw-browsers (máy phát triển);
  3. trình duyệt Playwright tự tải (`playwright install chromium`, như CI).

Không tìm thấy thì CHROMIUM là None và test giao diện tự bỏ qua.
"""

import glob
import os


def _tim() -> "str | None":
    tu_chon = os.environ.get("RBDA_TEST_CHROMIUM", "")
    if tu_chon and os.path.exists(tu_chon):
        return tu_chon
    for duong in sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"),
                        reverse=True):
        if os.path.exists(duong):
            return duong
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            duong = pw.chromium.executable_path
        return duong if duong and os.path.exists(duong) else None
    except Exception:
        return None


CHROMIUM = _tim()
