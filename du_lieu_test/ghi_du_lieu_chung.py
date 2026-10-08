"""Hai hàm dùng chung cho các bộ sinh dữ liệu trong du_lieu_test/.

Trước đây `tao_bo_can_bang.py`, `tao_bo_nhieu_buoi.py` và
`tao_bo_sau_buoi.py` mỗi tệp chép y hệt hai hàm này. Danh sách họ/tên đệm/
tên thì CỐ Ý để riêng ở từng bộ (mỗi bộ một kiểu tên), nên truyền vào.

Mọi thay đổi ở đây phải giữ nguyên TỪNG BYTE tệp đã commit — xem
tests/test_bo_sinh_du_lieu_tai_lap.py.
"""

import csv
import os


def ten_ngau_nhien(rng, ho, dem, ten):
    return "%s %s %s" % (rng.choice(ho), rng.choice(dem), rng.choice(ten))


def ghi_csv(thu_muc, ten_tep, header, rows):
    duong = os.path.join(thu_muc, ten_tep)
    # utf-8-sig: Excel không có BOM thì đọc tên tiếng Việt thành ký tự lạ.
    with open(duong, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    return duong
