# Kịch bản nhập tay — 8 học sinh, 3 CLB

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
> Tên và mã đều do máy sinh. Dùng để chạy thử phần mềm, không phải khảo sát.

Bộ Excel trong thư mục này kiểm tra **đường nạp tệp**. Kịch bản này kiểm tra
**đường gõ tay** — tức là các màn hình mà giáo viên và học sinh thật sự bấm vào:
tab *Quản lý club*, tab *Nhập dự phòng tại kiosk*, tab *Chấm điểm*.

Nhỏ đủ để gõ trong khoảng 15 phút, và — điểm quan trọng nhất — **nhỏ đủ để bạn
tự tính ra kết quả bằng tay rồi đối chiếu**.

---

## Bước 1 — Tạo 3 CLB

Tab **Quản lý club & diện dự trữ** → form *Thêm / sửa club*:

| Mã club | Tên club | Tổng chỗ | Suất dự trữ | Nhãn dự trữ |
|---|---|---|---|---|
| `clb_nhiepanh` | CLB Nhiếp ảnh | 3 | 1 | `chinh_sach` |
| `clb_covua` | CLB Cờ vua | 2 | 0 | *(bỏ trống)* |
| `clb_nauan` | CLB Nấu ăn | 2 | 0 | *(bỏ trống)* |

Tổng **7 chỗ cho 8 học sinh** — cố ý thiếu, để thấy phần mềm xử lý người không
được xếp thế nào.

## Bước 2 — Tạo 8 học sinh và nhập lựa chọn

Tab **Nhập dự phòng tại kiosk**. Với mỗi em: gõ mã + họ tên vào ô *Tạo học sinh
mới*, rồi tick CLB ở Bước 1 và xếp nguyện vọng ở Bước 2.

| Mã | Họ tên | Tick thi những CLB | Nguyện vọng (đúng thứ tự) |
|---|---|---|---|
| `HS01` | Ngô Văn An | Nhiếp ảnh, Cờ vua | 1. Nhiếp ảnh → 2. Cờ vua |
| `HS02` | Lê Thị Bình | Nhiếp ảnh, Nấu ăn | 1. Nhiếp ảnh → 2. Nấu ăn |
| `HS03` | Trần Ngọc Chi | Nhiếp ảnh, Cờ vua | 1. Nhiếp ảnh → 2. Cờ vua |
| `HS04` | Phạm Văn Dũng | Nhiếp ảnh | 1. Nhiếp ảnh |
| `HS05` | Vũ Thị Hà | Nhiếp ảnh, Nấu ăn | 1. Nhiếp ảnh → 2. Nấu ăn |
| `HS06` | Đỗ Minh Khoa | Cờ vua, Nấu ăn | 1. Cờ vua → 2. Nấu ăn |
| `HS07` | Bùi Thị Lan | Nấu ăn | 1. Nấu ăn |
| `HS08` | Hoàng Văn Minh | Cờ vua | 1. Cờ vua |

## Bước 3 — Gán diện dự trữ cho HS05

Vẫn ở tab **Quản lý club**, phần *Gán diện dự trữ cho học sinh*: tìm `HS05`,
tick vào em đó, gõ nhãn `chinh_sach`, bấm **Gán cho học sinh đã tick**.

**Chỉ một em duy nhất thuộc diện dự trữ.** Cả kịch bản xoay quanh em này.

## Bước 4 — Chấm điểm

Tab **Chấm điểm (mù)**. Điểm phải gõ **đúng như bảng** — kết quả ở dưới chỉ đúng
với đúng bộ điểm này:

| | Nhiếp ảnh | Cờ vua | Nấu ăn |
|---|---|---|---|
| HS01 | **9.5** | 8.0 | |
| HS02 | **9.0** | | 7.5 |
| HS03 | **8.5** | 9.0 | |
| HS04 | **8.0** | | |
| HS05 | **6.0** | | 6.5 |
| HS06 | | 7.0 | 9.0 |
| HS07 | | | 8.5 |
| HS08 | | 6.5 | |

## Bước 5 — Chạy phân bổ

Tab **Vận hành pipeline** → **Chạy phân bổ**. Rồi sang tab **Kết quả**.

---

## Kết quả đúng phải ra như sau

**Xếp được 6 trên 8 em.**

| Mã | Vào CLB | Nguyện vọng thứ | Diện |
|---|---|---|---|
| HS01 | Nhiếp ảnh | 1 | Thường |
| HS02 | Nhiếp ảnh | 1 | Thường |
| HS03 | **Cờ vua** | **2** | Thường |
| HS04 | *(chưa được xếp)* | — | — |
| HS05 | Nhiếp ảnh | 1 | **Dự trữ** |
| HS06 | Cờ vua | 1 | Thường |
| HS07 | Nấu ăn | 1 | Thường |
| HS08 | *(chưa được xếp)* | — | — |

Tỉ lệ lấp đầy: Nhiếp ảnh **3/3**, Cờ vua **2/2**, Nấu ăn **1/2**.

> **Ra khác bảng này là phần mềm sai** — chụp màn hình và báo lại. Kịch bản này
> đã được chạy trong bộ kiểm thử tự động (`tests/test_kich_ban_nhap_tay.py`).

---

## Bốn điều kịch bản này chứng minh

**1. Suất dự trữ thật sự hoạt động.** HS05 chỉ 6.0 điểm mà vào được Nhiếp ảnh,
trong khi HS03 (8.5) và HS04 (8.0) **trượt** — vì một trong ba chỗ của Nhiếp ảnh
là suất dự trữ, chỉ em thuộc `chinh_sach` mới tranh được. Đây chính là cơ chế
trung tâm của thuật toán, và ở đây nó hiện ra chỉ trong năm dòng số.

**2. Trượt nguyện vọng 1 không có nghĩa là mất chỗ.** HS03 bị đẩy khỏi Nhiếp ảnh
nhưng rơi xuống nguyện vọng 2 là Cờ vua, và vào được với 9.0 điểm. Đó là phần
"deferred" trong *deferred acceptance*: chỗ chỉ được chốt sau khi mọi em đã hết
đường tranh.

**3. Xếp ít nguyện vọng là tự làm hại mình.** HS04 và HS08 mỗi em chỉ ghi **một**
nguyện vọng, trượt là hết. HS03 điểm gần bằng HS04 nhưng ghi hai nguyện vọng nên
vẫn có chỗ. Đây là điều nhà trường cần dặn học sinh trước khi phát phiếu.

**4. Còn chỗ trống không có nghĩa là xếp sai.** Nấu ăn còn 1 chỗ trống trong khi
hai em chưa được xếp — vì **không em nào trong hai em đó ghi Nấu ăn vào nguyện
vọng**. Thuật toán không nhét học sinh vào CLB họ không chọn. Muốn lấp nốt thì
đó là quyết định của nhà trường, không phải việc của phần mềm.

---

## Vì sao kết quả này không phụ thuộc may rủi

Thuật toán có một bước bốc thăm (Single Tie-Breaking) để xử lý **hai em bằng
điểm nhau**. Bộ điểm trên **cố ý không có cặp nào bằng nhau trong cùng một CLB**,
nên bước bốc thăm không bao giờ được dùng tới.

Đã chạy thử với 5 hạt giống ngẫu nhiên khác nhau (1, 7, 42, 999, 12345) — **kết
quả giống hệt nhau cả 5 lần**. Nghĩa là bạn có thể tự kiểm bằng bút chì trên
giấy, và máy phải ra đúng như vậy.

*Phần nhận xét về ý nghĩa của kết quả này, học sinh tự viết.*
