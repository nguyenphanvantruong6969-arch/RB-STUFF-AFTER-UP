---
name: sinh-du-lieu-clb
description: Sinh, soát và sửa dữ liệu đầu vào cho phần mềm phân bổ câu lạc bộ RB-DA (rbda-kiosk) — một Sổ nhập CLB (SO_NHAP_CLB.xlsx) gồm danh sách câu lạc bộ và mỗi học sinh một dòng nguyện vọng kèm điểm thi. Dùng khi cần tạo dữ liệu thử, dựng sổ nhập cho một trường mới, kiểm một sổ nhập (hoặc bộ ba CSV cũ) xem có nhập được không, hoặc tìm lý do phần mềm báo cảnh báo khi nhập. Cũng dùng khi người dùng nói "tạo dữ liệu mẫu", "sinh dữ liệu test", "làm file đầu vào", "kiểm tra file CSV", "generate input data", "sample data for the kiosk".
---

# Sinh dữ liệu đầu vào cho phần mềm phân bổ câu lạc bộ

Phần mềm `rbda-kiosk` chỉ nhận **một tệp**: Sổ nhập CLB `SO_NHAP_CLB.xlsx`
(định nghĩa trong `so_nhap.py` ở gốc kho mã). Kỹ năng này dựng sổ sao cho nhập
vào **không một cảnh báo nào**, và soát một sổ đã có để tìm chỗ sai.

## Nguyên tắc bất di bất dịch

**Sổ phải đi ra từ MỘT nguồn.** Luôn dùng `scripts/sinh_du_lieu.py` — nó soát
dữ liệu trong bộ nhớ rồi mới ghi sổ bằng chính `so_nhap.py` của phần mềm.

**Sai thì không ghi tệp nào.** Một bộ dữ liệu hỏng còn tệ hơn không có, vì nó
trông y như thật. Đoạn mã soát trước, ghi sau, và **không tự sửa** — sửa giúp
là giấu mất chỗ sai.

**Không bịa dữ liệu học sinh thật.** Mọi tên do kỹ năng này sinh ra là tên bịa
ghép từ bảng họ/đệm/tên. Không bao giờ chép tên học sinh có thật vào kho mã
nguồn hay vào tệp mẫu.

## Cách dùng

```bash
# Một trường ngẫu nhiên nhưng luôn hợp lệ — tất định theo --seed
python scripts/sinh_du_lieu.py ngau --ra ./bo_moi \
    --hoc-sinh 180 --buoi thu_2,thu_4,thu_6 --clb-moi-buoi 3 --seed 42

# Trường một buổi: bỏ hẳn --buoi
python scripts/sinh_du_lieu.py ngau --ra ./bo_moi --hoc-sinh 120

# Dựng từ bản khai báo JSON tường minh
python scripts/sinh_du_lieu.py tao --spec truong.json --ra ./bo_moi

# Soát một sổ đã có (hoặc thư mục chứa nó, hoặc bộ ba CSV cũ) — không sửa gì
python scripts/sinh_du_lieu.py soat ./bo_moi/SO_NHAP_CLB.xlsx
```

`--do-choi` chỉnh độ chật: `1.15` là tổng chỗ nhiều hơn nhu cầu 15%. Dưới `1.0`
thì chắc chắn nhiều em trắng tay; trên `1.5` thì gần như ai cũng có chỗ và kết
quả không nói lên điều gì.

## Sổ nhập trông thế nào

Một tệp Excel, hai sheet dữ liệu và một sheet `Hướng dẫn`.

### Sheet `1. CLB` — mỗi câu lạc bộ một dòng

| Tên CLB | Buổi | Chỉ tiêu | Suất ưu tiên | Nhóm ưu tiên | Mã CLB |
|---|---|---|---|---|---|
| CLB Bóng rổ | Thứ 2 | 6 | | | clb_bongro |
| CLB Văn học | Thứ 2 | 5 | 2 | chinh_sach | clb_vanhoc |

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| Tên CLB | ✅ | Tên hiển thị, có dấu, **không trùng** — ô NV ở sheet 2 chọn theo tên này |
| Buổi | | Thứ 2 … Chủ nhật. Trường một buổi thì **để trống cả cột**. Khai thì phải khai cho **mọi** câu lạc bộ |
| Chỉ tiêu | ✅ | Số nguyên **> 0** |
| Suất ưu tiên | | ≤ Chỉ tiêu. Lớn hơn 0 thì **bắt buộc** có Nhóm ưu tiên |
| Nhóm ưu tiên | | Nhãn nhóm, ví dụ `chinh_sach` |
| Mã CLB | | Kỹ năng luôn ghi mã; người dùng tự điền thì để trống cũng được (phần mềm tự tạo) |

### Sheet `2. Học sinh` — mỗi học sinh một dòng

| Mã HS | Họ tên | Nhóm ưu tiên | NV1 | Điểm 1 | NV2 | Điểm 2 | … |
|---|---|---|---|---|---|---|---|
| HS001 | Nguyễn Văn An | | CLB Tin học | 9,5 | CLB Bóng rổ | | |

- **NV1, NV2, …**: tên câu lạc bộ theo thứ tự ưu tiên. **Một danh sách chung
  cho mọi buổi** — phần mềm tự chia theo buổi của từng câu lạc bộ. Kỹ năng ghi
  lần lượt nguyện vọng buổi 1, rồi buổi 2, …
- **Điểm k** nằm ngay cạnh **NV k**: có điểm = em đã thi câu lạc bộ đó; trống =
  không thi; chữ `thi` = đã thi, chấm sau trong phần mềm.
- Câu lạc bộ **không em nào có điểm** = câu lạc bộ **không tổ chức thi**.
- Em không xếp câu lạc bộ nào của một buổi = **em bận ngày đó**. Hợp lệ.
- Điểm cho câu lạc bộ em không xếp nguyện vọng thì sổ **không chứa được** (điểm
  luôn nằm cạnh một NV) — điều 8 dưới đây chặn nó từ trước.

## Chín điều phải đúng, nếu không thì không ghi

1. mọi `club_id` trong tệp học sinh đều có trong danh sách câu lạc bộ;
2. trong bản khai báo JSON, mỗi câu lạc bộ nằm đúng buổi của nó;
3. không nguyện vọng nào trùng trong cùng một buổi;
4. ≤ **10 nguyện vọng mỗi buổi** (đúng giới hạn câu hỏi Ranking của Microsoft Forms);
5. ≤ **5 câu lạc bộ dự thi mỗi buổi**;
6. `capacity > 0`, `reserve_capacity ≤ capacity`, có dự trữ thì có nhóm;
7. chỉ chấm điểm cho câu lạc bộ có thật;
8. chỉ chấm điểm cho câu lạc bộ em **có khai nguyện vọng** — điểm cho câu lạc
   bộ em không xếp là điểm không dùng tới, và gần như chắc chắn là gõ lệch cột;
9. mã học sinh duy nhất (phần mềm **phân biệt hoa thường**: `hs001` và `HS001`
   là hai em khác nhau).

Ngoài ra kỹ năng in **cảnh báo mềm** — không chặn, nhưng nên đọc: buổi chọi quá
3 lần, buổi thừa chỗ, số em không khai nguyện vọng nào.

## Luôn kiểm bằng phần mềm thật, đừng tin mình

Soát xong vẫn phải nhập thử. Đây là phép kiểm duy nhất đáng tin:

```python
import base64, os, sys, tempfile
sys.path.insert(0, "<đường dẫn tới rbda-kiosk>")
from api import PipelineAPI

d = tempfile.mkdtemp()
api = PipelineAPI(os.path.join(d, "app.db"), thu_muc_xuat=d)
with open(os.path.join(BO, "SO_NHAP_CLB.xlsx"), "rb") as f:
    kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
assert kq["ok"] and not (kq["data"].get("warnings") or []), kq
canh_bao = api.get_data_health_report()["data"]["warnings"]
assert [w for w in canh_bao
        if w["code"] != "health_oversubscribed_buoi"] == [], canh_bao
assert api.run_pipeline(seed=42)["ok"]
```

**Tiêu chuẩn: 0 cảnh báo khi nhập, 0 cảnh báo sức khoẻ dữ liệu (trừ đúng một
mã, xem dưới), chạy được.** Một bộ mẫu mà phần mềm phải kêu là một bộ mẫu đang dạy
người ta làm sai, và người đọc không có cách nào biết cảnh báo đó là cố ý hay
là lỗi.

Chỉ được phép đúng một mã: `health_oversubscribed_buoi` — một buổi có ít chỗ
hơn số em xếp nguyện vọng buổi đó. Đó là sự thật về độ chọi, không phải lỗi dữ
liệu: bộ sinh ra cố ý để chật chỗ cho kết quả có ý nghĩa. Đọc nó để biết buổi
nào sẽ có em trắng tay. Mọi mã khác, kể cả mức "info", vẫn phải bằng 0.

## Bản khai báo JSON

```json
{
  "cau_lac_bo": [
    {"club_id": "clb_covua", "name": "CLB Cờ vua", "capacity": 4,
     "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"}
  ],
  "hoc_sinh": [
    {"student_id": "HS001", "name": "Nguyễn Văn An", "reserve_group": "",
     "nguyen_vong": {"thu_2": ["clb_covua"]},
     "diem": {}}
  ]
}
```

`nguyen_vong` là `{buổi: [club_id theo thứ tự ưu tiên]}`.
`diem` là `{club_id: điểm}` — chỉ cho câu lạc bộ em vừa khai nguyện vọng.

## Đọc thêm khi cần chi tiết

| Cần gì | Đọc đâu |
|---|---|
| Một trường hoàn chỉnh đã kiểm chứng | `mau_csv/vi_du_day_du/` và `GIAI_THICH.md` của nó |
| Một trường sinh hoạt cả tuần (6 buổi) | `mau_csv/vi_du_ca_tuan/` và `GIAI_THICH.md` của nó |
| Sổ nhập: từng cột, từng lỗi phần mềm báo | `mau_csv/HUONG_DAN_SO_NHAP.md`, `so_nhap.py` |
| Cách dựng biểu mẫu Microsoft Forms khớp các trần này | `docs/BO_CAU_HOI_FORMS.md` |
| Thuật toán xếp chỗ hoạt động ra sao | `docs/NGHIEN_CUU_TOI_UU.md`, `docs/CO_CHE_THUAT_TOAN.md` |
