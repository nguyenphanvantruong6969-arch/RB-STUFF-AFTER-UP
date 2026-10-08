# Sổ nhập CLB — một tệp Excel, sáu bước

Phần mềm chỉ nhận **một tệp**: Sổ nhập CLB (`SO_NHAP_CLB.xlsx`). Một người
điền từ trên xuống dưới rồi kéo vào phần mềm là xong. Không còn ba tệp riêng,
không còn tên cột tiếng Anh, không phải nhớ thứ tự nạp.

> Mọi quy tắc trong tài liệu này được khoá bằng test tự động
> (`tests/test_so_nhap.py`). Định nghĩa của sổ nằm ở một chỗ duy nhất:
> `so_nhap.py`.

---

## Lấy sổ ở đâu

| Cách | Khi nào |
|---|---|
| Bấm **Tải sổ nhập mẫu** ở màn hình **01 · Vận hành** | Cách nên dùng. Phần mềm đã có CLB thì sổ **điền sẵn** danh sách CLB, chỉ còn điền học sinh |
| Mở `mau_csv/SO_NHAP_CLB.xlsx` | Sổ trống |
| Mở `mau_csv/vi_du_day_du/SO_NHAP_CLB_vi_du.xlsx` | Muốn xem một sổ đã điền đầy đủ (3 buổi, 9 CLB, 24 học sinh) |
| Chạy skill `xu-li-raw-forms` trên kết quả Google Forms | Học sinh đăng ký qua biểu mẫu: skill ra thẳng sổ này |

---

## Sáu bước

**Bước 1. Sheet `1. CLB`**: mỗi câu lạc bộ một dòng.

| Tên CLB | Buổi | Chỉ tiêu | Suất ưu tiên | Nhóm ưu tiên | Mã CLB |
|---|---|---|---|---|---|
| CLB Bóng rổ | Thứ 2 | 20 | | | |
| CLB Tiếng Anh | Thứ 4 | 25 | 5 | chinh_sach | |

| Cột | Bắt buộc | Ghi chú |
|---|---|---|
| **Tên CLB** | ✅ | Không được trùng. Đây là tên hiện trong danh sách thả xuống ở sheet 2 |
| **Buổi** | | Chọn Thứ 2 … Chủ nhật. Trường chỉ có **một** buổi thì để trống cả cột. Khai thì khai cho **mọi** CLB |
| **Chỉ tiêu** | ✅ | Tổng số chỗ, số nguyên lớn hơn 0 |
| **Suất ưu tiên** | | Số chỗ trong Chỉ tiêu dành riêng cho Nhóm ưu tiên. **Nằm trong** Chỉ tiêu, không cộng thêm |
| **Nhóm ưu tiên** | | Tên nhóm được giữ chỗ, ví dụ `chinh_sach` |
| **Mã CLB** | | Để trống: phần mềm tự tạo từ tên (`CLB Bóng đá (nữ)` → `clb_bong_da_nu`), hoặc dùng lại mã của CLB cùng tên đã có. **Đổi tên CLB thì giữ nguyên Mã CLB** |

**Bước 2. Sheet `2. Học sinh`**: mỗi học sinh một dòng. **Mã HS** bắt buộc và
không được trùng. **Nhóm ưu tiên** chỉ điền cho em thuộc nhóm đó.

**Bước 3. NV1, NV2, NV3…**: chọn tên CLB trong **danh sách thả xuống**, em
thích nhất đứng trước. Không cần điền kín.

> Trường nhiều buổi: cứ điền **chung một danh sách**. Phần mềm tự chia theo
> buổi của từng CLB. Em bận buổi nào thì đơn giản là không chọn CLB nào của
> buổi đó.

**Bước 4. Điểm 1, Điểm 2…**: điểm thi của CLB **ngay bên trái**.

| Ô Điểm | Nghĩa |
|---|---|
| Một số (`8,5` hoặc `8.5`) | Em đã thi CLB này, được chừng ấy điểm |
| Chữ `thi` | Em đã thi nhưng chưa có điểm, sẽ chấm sau ở màn hình **05 · Chấm điểm** |
| Trống | Em không thi CLB này |

CLB không em nào có điểm là CLB **không tổ chức thi**.

**Bước 5. Lưu tệp**, giữ định dạng `.xlsx`.

**Bước 6. Mở phần mềm → 01 · Vận hành → kéo sổ vào ô nạp.** Phần mềm đọc thử
(chưa ghi gì) và hiện tóm tắt:

> *Sẵn sàng nhập: 9 CLB · 3 buổi · 24 học sinh · 109 nguyện vọng · 33 lượt thi*

Đối chiếu con số rồi bấm **Nhập sổ**.

---

## Ví dụ một dòng học sinh

| Mã HS | Họ tên | Nhóm ưu tiên | NV1 | Điểm 1 | NV2 | Điểm 2 | NV3 | Điểm 3 |
|---|---|---|---|---|---|---|---|---|
| HS001 | Nguyễn Văn An | | CLB Tin học | 9,5 | CLB Bóng rổ | | CLB Robotics | thi |

An thích Tin học nhất và đã thi được 9,5. Nguyện vọng 2 là Bóng rổ, CLB không
thi tuyển. Nguyện vọng 3 là Robotics: An đã thi nhưng chưa có điểm.

---

## Sổ có lỗi thì sao

Sổ có lỗi thì phần mềm **không nạp gì cả** và liệt kê từng lỗi kèm sheet, dòng.
Nạp một nửa sổ còn tệ hơn không nạp: người dùng tưởng đã xong. Sửa trong
Excel, lưu, kéo vào lần nữa.

| Lỗi phần mềm báo | Sửa thế nào |
|---|---|
| Không có CLB nào tên "…" | Ô NV gõ tay sai tên. Chọn lại trong danh sách thả xuống |
| "…" được chọn hai lần | Một CLB chỉ chọn một lần trên một dòng (Excel đã tô đỏ ô trùng) |
| "…" không phải điểm | Ghi một số, hoặc chữ `thi` |
| Có Điểm k nhưng NV k trống | Điểm phải nằm ngay cạnh CLB của nó |
| Mã HS … đã có ở dòng … | Mỗi học sinh một dòng. Gộp hai dòng làm một |
| Thiếu Mã HS | Dòng có dữ liệu mà không có mã |
| Tên CLB "…" đã có ở dòng … | Hai CLB trùng tên. Đặt tên khác nhau |
| Chỉ tiêu phải là số nguyên lớn hơn 0 | Sửa Chỉ tiêu, và Suất ưu tiên không được lớn hơn Chỉ tiêu |
| … nguyện vọng ở buổi …, tối đa 10 mỗi buổi | Một em xếp tối đa 10 CLB của **cùng một buổi**. Bớt nguyện vọng của buổi đó |
| Thi … CLB ở buổi …, tối đa 5 mỗi buổi | Một em thi tối đa 5 CLB của cùng một buổi. Xoá bớt ô Điểm |
| Mã tự tạo "…" trùng với CLB ở dòng … | Hai tên CLB ra cùng một mã. Điền Mã CLB cho một trong hai dòng |
| Thiếu cột "…" | Dòng tiêu đề bị xoá hoặc đổi tên. Tải lại sổ mẫu |
| Đây không phải Sổ nhập CLB | Tệp thiếu sheet `1. CLB` hoặc `2. Học sinh` |

Muốn thấy bảng lỗi này trên màn hình: kéo thử
`du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx` (cố ý sai 5 chỗ).

Sổ do phần mềm hay các công cụ đi kèm tạo ra luôn có tên CLB riêng: hai CLB
cùng tên ở hai buổi được thêm tên buổi, ví dụ "CLB Cờ vua (Thứ 5)".

Tên CLB chỉ cần khác nhau là đủ: "Bóng đá (nam)" và "Bóng đá (nữ)", "C++" và
"C#" là hai CLB. Gõ tay thiếu dấu ("clb tin hoc") vẫn được nhận nếu chỉ khớp
đúng một CLB; khớp nhiều CLB thì phần mềm báo lỗi chứ không đoán.

Sổ **sạch** vẫn có thể nhận vài **cảnh báo** sau khi nạp (ví dụ một buổi ít chỗ
hơn số em muốn vào). Cảnh báo không chặn việc nạp. Đọc chúng ở mục **Cảnh báo
dữ liệu** trước khi chạy.

---

## Nạp lại

Nạp lại sổ đã sửa là **cập nhật**, không tạo trùng: CLB khớp theo Mã CLB (Mã
CLB trống thì theo tên), học sinh khớp theo Mã HS.

Với mỗi em có trong sổ, **dòng của em là bản đầy đủ**:

- nguyện vọng và lựa chọn thi được **thay hẳn** bằng dòng mới;
- ô Điểm ghi `thi` nghĩa là **chưa có điểm**: điểm cũ của CLB đó bị xoá;
- ô Nhóm ưu tiên trống nghĩa là em **không thuộc nhóm nào**: nhóm cũ bị bỏ.
  Sổ sinh từ biểu mẫu Google/Microsoft Forms **không có cột** Nhóm ưu tiên:
  khi đó phần mềm giữ nguyên nhóm đã gán.

Trước khi nạp, phần mềm báo vàng những gì sẽ mất (bao nhiêu điểm bị xoá, bao
nhiêu em bị bỏ nhóm). Đã chấm điểm ở màn hình **05** mà muốn sửa sổ tiếp: xuất
**Dữ liệu đầu vào hiện tại** ra một sổ mới (có sẵn điểm vừa chấm) rồi sửa trên
sổ đó.

Học sinh và CLB **không có** trong sổ thì không bị xoá; CLB như vậy được báo
trước khi nạp (thường là CLB vừa đổi tên mà quên giữ Mã CLB). Muốn làm lại từ
đầu: màn hình **04 · Quản lý** → Xoá dữ liệu.

---

## Lấy lại sổ từ phần mềm

Màn hình **02 · Kết quả** → Xuất → **Dữ liệu đầu vào hiện tại** ghi ra một sổ
nhập đúng dữ liệu đang có, kể cả mọi chỗ sửa tay. Kéo sổ đó vào một máy khác là
dựng lại y nguyên.

---

## Cho người phát triển

Bên trong, phần mềm dịch sổ thành ba bảng (CLB, CLB dự thi kèm điểm, nguyện
vọng) rồi dùng đúng các hàm nạp cũ, nên mọi luật soát cũ vẫn áp dụng: tối đa
10 nguyện vọng và 5 CLB dự thi **mỗi buổi**, nhóm ưu tiên lạ, mã lệch
hoa/thường… Định dạng ba bảng nội bộ đó mô tả ở `mau_csv/HUONG_DAN_CSV.md` (tài liệu kỹ thuật).
