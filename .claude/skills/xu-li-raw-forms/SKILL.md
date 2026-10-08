---
name: xu-li-raw-forms
description: Xử lí dữ liệu raw xuất từ biểu mẫu Google Forms "Đăng ký CLB và thi tuyển" (tệp RAW_PHIEU.xlsx và DAP_AN.xlsx do hàm chamTheoCLB tạo) thành MỘT Sổ nhập CLB (SO_NHAP_CLB.xlsx) kéo thẳng vào phần mềm xếp CLB rbda-kiosk (sheet CLB có chỉ tiêu, sheet học sinh có nguyện vọng và điểm), chấm lại bài thi theo đáp án gốc, và soát dữ liệu bất thường (phiếu trùng, mã sai dạng, đáp án Forms lệch, làm bài không tick, tick không làm, thiếu xếp hạng). Dùng khi người dùng nói "xử lí raw", "xử lý dữ liệu raw", "RAW_PHIEU", "chuyển kết quả Google Forms sang phần mềm", "làm tệp nạp từ biểu mẫu", "soát phiếu", "process the raw export", hoặc đưa một thư mục "Kết quả CLB ...".
---

# Xử lí dữ liệu raw của Google Forms thành Sổ nhập CLB

> **Đường dẫn lệnh.** Trong kho mã rbda-kiosk, script nằm ở `.claude/skills/xu-li-raw-forms/scripts/xu_li_raw.py`. Ở bản đóng gói (.zip), dùng `scripts/xu_li_raw.py` trong thư mục của skill này; các tệp phụ thuộc đã có sẵn cạnh nó.

Biểu mẫu Google Forms được dựng bằng `mau_forms_thi_clb/TAO_GOOGLE_FORM.gs`.
Hàm `chamTheoCLB` trong đó xuất thư mục "Kết quả CLB <ngày giờ>" có
`RAW_PHIEU.xlsx` và `DAP_AN.xlsx`. Định dạng hai tệp này nằm trong
`mau_forms_thi_clb/DINH_DANG_RAW.md`: **đọc tài liệu đó trước** nếu cần hiểu
một cột.

Skill này biến raw thành đúng MỘT tệp phần mềm xếp CLB nạp được — Sổ nhập CLB
`SO_NHAP_CLB.xlsx` — và viết một báo cáo bất thường cho người vận hành đọc.

## Nguyên tắc

- **Không tin mù quáng các cột tính sẵn trong raw.** Script tự chấm lại theo
  `DAP_AN.xlsx`, tự chọn phiếu giữ (phiếu đầu của mỗi mã), tự quyết bài nào
  được tính (phải tick, phải được chọn ở một Top, tối đa 5 CLB mỗi buổi).
  Chỗ nào khác với raw thì ghi vào báo cáo.
- **Ô sai lẻ thì bỏ riêng ô đó và báo.** Một phiếu trùng, một bài không tick
  không làm hỏng cả bộ.
- **Đầu vào hỏng thì không ghi tệp nào**: thiếu cột, tệp chỉ tiêu thiếu CLB,
  buổi của CLB không khớp. Một bộ tệp hỏng trông y như thật còn tệ hơn không có.
- **Không bịa chỉ tiêu.** Chỉ tiêu CLB do nhà trường lập. Không có tệp chỉ
  tiêu thì cột Chỉ tiêu của sổ để trống, và phải nói rõ với người dùng.
- **Dữ liệu là của học sinh thật.** Không chép tên, mã học sinh vào kho mã
  nguồn, không đưa vào tệp mẫu hay test.

## Cách chạy

```bash
python .claude/skills/xu-li-raw-forms/scripts/xu_li_raw.py \
    --raw  "<thư mục kết quả>/RAW_PHIEU.xlsx" \
    --dap-an "<thư mục kết quả>/DAP_AN.xlsx" \
    --clb  "<SO_NHAP_CLB.xlsx đã điền chỉ tiêu>" \
    --ra   ./nap
```

- `--raw` bắt buộc. Nhận `.xlsx` hoặc `.csv`.
- `--dap-an` nên có. Thiếu thì dùng cột `diem` có sẵn trong raw, không chấm lại.
- `--clb` là danh sách CLB đã điền chỉ tiêu: một Sổ nhập CLB (đọc sheet
  `1. CLB`), hoặc tệp kiểu cũ có cột `club_id, name, capacity, reserve_capacity,
  reserve_group, buoi` (ví dụ `01_danh_sach_CLB.xlsx` trong thư mục kết quả).
  Thiếu thì cột Chỉ tiêu của sổ để trống.
- Vòng làm việc gọn nhất: chạy lần đầu không có `--clb`, nhà trường điền cột
  **Chỉ tiêu** ngay trong `SO_NHAP_CLB.xlsx` rồi kéo sổ đó vào phần mềm — không
  phải chạy lại. Chạy lại với `--clb <sổ đã điền>` chỉ khi raw có phiếu mới.
- Mã thoát `1` và dòng "KHÔNG GHI TỆP NÀO" nghĩa là đầu vào hỏng: đọc lý do,
  báo người dùng, không tự sửa dữ liệu.

Người dùng đưa thư mục đã giải nén từ Drive thì tìm ba tệp trong đó. Có nhiều
thư mục "Kết quả CLB ..." thì dùng thư mục mới nhất theo tên, và nói rõ đã dùng
thư mục nào.

## Đầu ra (trong `--ra`)

| Tệp | Nội dung |
|---|---|
| `SO_NHAP_CLB.xlsx` | Sheet `1. CLB`: CLB, buổi, chỉ tiêu (trống nếu chưa có `--clb`). Sheet `2. Học sinh`: mỗi em một dòng, NV1, NV2… theo hạng em chọn (buổi này nối buổi kia), điểm thang 10 ngay cạnh CLB em đã thi |
| `BAO_CAO_BAT_THUONG.md` | Mọi điều bất thường, kèm mã học sinh |

Sổ được soát bằng `soat()` của skill `sinh-du-lieu-clb` (9 điều bắt buộc của
phần mềm) rồi ghi bằng `so_nhap.py` của chính phần mềm, nên bố cục giống hệt sổ
mẫu trong kho.

## Đọc báo cáo và nói với người dùng

Tóm tắt cho người dùng theo thứ tự ưu tiên:

1. **Đáp án Forms lệch đáp án gốc**: gom theo câu. Nhiều bài lệch ở cùng một
   câu gần như chắc chắn là đáp án trên Google Forms bị tick sai. Điểm trong
   sổ đã theo đáp án gốc, nhưng nên sửa đáp án trên Forms.
2. **Làm bài mà không tick**: bài không được tính. Hỏi người dùng có muốn
   liên hệ học sinh không; **không tự tính điểm** cho những bài này.
3. **Phiếu trùng, phiếu không mã, mã sai dạng, một email nhiều mã**: có thể
   là gõ nhầm mã. Liệt kê để người dùng kiểm với danh sách lớp.
4. **Bỏ trống một Top ở giữa, chọn một CLB ở nhiều Top**: đã dồn lên và giữ Top cao nhất, chỉ cần báo.
5. **Thiếu xếp hạng, trùng hạng, câu lạ**: dấu hiệu biểu mẫu bị sửa tay.
6. Chưa có chỉ tiêu: nhắc điền cột **Chỉ tiêu** ở sheet `1. CLB` trước khi nạp.

Nói bằng tiếng Việt đơn giản, nêu con số cụ thể.

## Luôn kiểm bằng phần mềm thật

Có chỉ tiêu thì nạp thử trước khi giao:

```python
import base64, os, sys, tempfile
sys.path.insert(0, "<đường dẫn tới rbda-kiosk>")
from api import PipelineAPI

d = tempfile.mkdtemp()
api = PipelineAPI(os.path.join(d, "app.db"), thu_muc_xuat=d)
with open(os.path.join(RA, "SO_NHAP_CLB.xlsx"), "rb") as f:
    kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
print(kq["ok"], kq["errors"] or kq["data"]["warnings"])
print(api.get_data_health_report()["data"]["n_warnings"])
print(api.run_pipeline(seed=42)["ok"])
```

Tiêu chuẩn: nạp được sổ, 0 cảnh báo khi nạp, chạy xếp CLB được. Cảnh
báo sức khoẻ dữ liệu (ví dụ "điểm lạ" khi một bài 0 điểm) có thể là thật: đối
chiếu với báo cáo rồi nói với người dùng, đừng tự sửa điểm.

## Kiểm bộ test

`tests/test_skill_xu_li_raw.py` dựng raw giả với đủ các loại bất thường, chạy
script, rồi nạp kết quả vào phần mềm thật và đếm cảnh báo.
