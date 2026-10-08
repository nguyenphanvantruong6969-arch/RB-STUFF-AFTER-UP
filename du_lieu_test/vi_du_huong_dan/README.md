# Bộ ví dụ dùng trong hướng dẫn sử dụng

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
>
> Mười cái tên trong thư mục này là tên bịa, viết tay trong `tao_vi_du.py`.
> Trình bày như số liệu khảo sát thật là **bịa đặt dữ liệu**.

## Bộ này để làm gì

`HUONG_DAN_SU_DUNG.md` giải thích từng bước dựa trên đúng bộ này. Nó **nhỏ** —
10 học sinh, 4 CLB — để in trọn vào hướng dẫn, và để người đọc **tự tính lại
bằng tay** rồi đối chiếu với máy.

| Bộ | Quy mô | Dùng khi nào |
|---|---|---|
| `vi_du_huong_dan/` | 10 em, 4 CLB | Học cách dùng, đi kèm hướng dẫn |
| `bo_sach/` | 140 em, 12 CLB | Chạy thử ở quy mô gần thật |
| `TEST_01..04` | 120 em + 1 tệp cố ý sai | Kiểm tra phần mềm có cảnh báo không |

## Sổ nhập — tệp để thả vào phần mềm

**`SO_NHAP_VIDU.xlsx`**: cả bộ trong một Sổ nhập CLB. Kéo sổ này vào ô nạp ở thẻ
**01 · Vận hành sắp xếp**, bấm **Nhập sổ**. Sổ sinh từ ba tệp dưới đây bằng
`mau_csv/tao_so_nhap.py`.

## Ba tệp gốc (định dạng nội bộ, dùng cho test)

| Tệp | Nội dung |
|---|---|
| `VIDU_01_danh_sach_CLB` | 4 CLB, tổng **10 suất** cho 10 em; Bóng rổ có 1 suất dự trữ |
| `VIDU_02_chon_CLB_muon_thi` | 10 em, mỗi em thi 1–2 CLB, **điểm có sẵn** |
| `VIDU_03_xep_hang_nguyen_vong` | 10 em, mỗi em 1–2 nguyện vọng |

Mỗi tệp có cả `.xlsx` và `.csv`.

## Kết quả đúng — đối chiếu với màn hình

Nạp vào CSDL trống, chạy với `seed = 42`:

| Mã | Họ tên | CLB được xếp | Nguyện vọng | Diện |
|---|---|---|---|---|
| HS01 | Nguyễn Văn An | CLB Bóng rổ | 1 | Thường |
| HS02 | Trần Thị Bình | CLB Bóng rổ | 1 | Thường |
| HS03 | Lê Minh Cường | CLB Nấu ăn | **2** | Thường |
| HS04 | Phạm Thu Dung | CLB Bóng rổ | 1 | **Dự trữ** |
| HS05 | Hoàng Văn Đức | CLB Tin học | **2** | Thường |
| HS06 | Vũ Ngọc Giang | CLB Tin học | 1 | Thường |
| HS07 | Đỗ Thị Hạnh | CLB Mỹ thuật | 1 | Thường |
| HS08 | Bùi Quang Khánh | CLB Mỹ thuật | 1 | Thường |
| HS09 | Ngô Phương Linh | CLB Nấu ăn | 1 | Thường |
| **HS10** | Dương Bá Minh | **chưa được xếp** | — | — |

Sức chứa: Bóng rổ 3/3 · Mỹ thuật 2/2 · Tin học 2/2 · **Nấu ăn 2/3**

Đo thêm: **0 cảnh báo** lúc nhập, **0 cảnh báo** dữ liệu, **0 cặp chặn**
(kết quả ổn định), chạy xong sau **2 vòng**.

## Bốn điều bộ này cho thấy

**1. Không phải ai cũng được nguyện vọng 1.** Sáu em xếp Bóng rổ làm nguyện
vọng 1 nhưng chỉ có 3 chỗ. HS03 và HS05 tụt xuống nguyện vọng 2.

**2. Suất dự trữ thực sự quyết định.** Đo bằng cách chạy hai lần, một lần có
suất dự trữ và một lần bỏ đi — **đúng một chỗ đổi chủ**:

| | Có suất dự trữ | Bỏ suất dự trữ |
|---|---|---|
| HS04 *(điểm 6,0 · diện chinh_sach)* | **CLB Bóng rổ** | **chưa được xếp** |
| HS03 *(điểm 8,0)* | CLB Nấu ăn | CLB Bóng rổ |

**3. Có em chưa được xếp dù CLB còn chỗ.** HS10 chỉ xếp **một** nguyện vọng,
vào đúng CLB đông nhất. Nấu ăn còn trống 1 chỗ, nhưng thuật toán **không nhét
học sinh vào CLB các em không chọn**. Em này nằm trong tệp `_chua_duoc_xep.csv`.

**4. Không cảnh báo nào.** Mọi cảnh báo người dùng nhìn thấy khi chạy bộ này
đều là do dữ liệu của họ, không phải do bộ mẫu.

## Sinh lại

```bash
./.venv/bin/python du_lieu_test/vi_du_huong_dan/tao_vi_du.py
```

`tests/test_vi_du_huong_dan.py` khoá toàn bộ bảng kết quả trên. Bộ mẫu lệch khỏi
hướng dẫn thì hướng dẫn thành nói dối, nên phải có test canh.

---

*Phần nhận xét và diễn giải về kết quả, học sinh tự viết.*
