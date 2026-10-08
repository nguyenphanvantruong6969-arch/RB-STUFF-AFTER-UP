# Bộ câu hỏi Microsoft Forms — thu nguyện vọng cho thời khoá biểu tuần

Tài liệu này dành cho người **dựng biểu mẫu** và người **xử lý tệp xuất ra**.
Nó mô tả đúng một thứ: hình dạng dữ liệu phần mềm đọc được, và cách đi từ tệp
Forms xuất ra tới hình dạng đó.

Trường chỉ sinh hoạt **một buổi** thì bỏ qua tài liệu này — bộ câu hỏi cũ vẫn
đúng, và `mau_csv/HUONG_DAN_CSV.md` mục 3.1–3.5 đã đủ.

---

## 1. Ba thứ phải thu, hai biểu mẫu

| Thu gì | Câu hỏi trên Forms | Vào tệp nào |
|---|---|---|
| Mã học sinh, họ tên | 2 câu **Text** | cả hai tệp |
| CLB muốn **dự thi** mỗi buổi | 1 câu **Choice · chọn nhiều** cho mỗi buổi | tệp Bước 1 |
| **Xếp hạng** nguyện vọng mỗi buổi | 1 câu **Ranking** cho mỗi buổi | tệp Bước 2 |

Hai bước **độc lập** nhau và nên là **hai biểu mẫu riêng**. Gộp một biểu mẫu
vẫn chạy được, nhưng khi tách tệp xuất ra sẽ phải cắt cột bằng tay — thêm một
bước gõ tay là thêm một chỗ sai.

Danh sách CLB **không thu qua Forms**. Nhà trường tự lập
(`mau_csv/06_danh_sach_club_nhieu_buoi.csv`) và nạp **trước tiên**.

---

## 2. Trần số lượng — đúng bằng trần của phần mềm

| Câu hỏi | Tối đa | Vì sao đúng con số đó |
|---|---|---|
| Ranking mỗi buổi | **10 CLB** | Bằng trần nguyện vọng mỗi buổi của phần mềm |
| Choice mỗi buổi | **5 CLB** | Bằng trần dự thi mỗi buổi của phần mềm |

Hai con số này **phải khớp**. Để Forms cho chọn nhiều hơn trần phần mềm là dựng
sẵn một cái bẫy: học sinh khai hợp lệ theo biểu mẫu, rồi buổi đó **không được
nhập**, và em không hiểu vì sao.

Trường có trên 10 CLB trong **một** buổi thì phải chia bớt CLB sang buổi khác —
không có cách nào lách trần, vì 10 là giới hạn của chính câu hỏi Ranking.

---

## 3. Đặt tên câu hỏi

Forms lấy **nguyên văn câu hỏi** làm tên cột khi xuất. Nên đặt câu hỏi sao cho
đổi tên cột về sau là việc máy làm được, không phải việc đoán.

**Câu Ranking — mỗi buổi một câu:**

> `[thu_2] Thứ Hai (tiết 9) — em muốn vào câu lạc bộ nào? Kéo thả theo thứ tự
> em thích nhất trước.`

**Câu Choice chọn nhiều — mỗi buổi một câu:**

> `[thu_2] Thứ Hai (tiết 9) — em đăng ký dự thi câu lạc bộ nào? Chọn tối đa 5.`

Đặt **mã buổi trong ngoặc vuông ở đầu** câu hỏi. Mã đó phải **trùng từng ký
tự** với cột `buoi` trong danh sách CLB. Nhờ vậy người xử lý tệp chỉ cần đọc
phần trong ngoặc, không phải suy từ chữ "Thứ Hai".

Lựa chọn trong câu hỏi ghi **cả tên lẫn mã**:

> `CLB Cờ vua (clb_covua)`

Ghi mỗi tên thì người xử lý phải tra ngược ra mã — và tra sai thì sai lặng lẽ.

---

## 4. Một buổi em bận thì BỎ TRỐNG

Không thêm câu hỏi *"em bận buổi nào"*. Buổi nào em không muốn sinh hoạt thì
**không chọn gì** ở câu của buổi đó — danh sách rỗng đã nói đúng điều ấy.

Vì vậy **mọi câu Ranking và Choice đều phải để là KHÔNG bắt buộc**. Đặt bắt
buộc là ép em khai một buổi em không rảnh, và phần mềm sẽ xếp em vào đó.

---

## 5. Từ tệp Forms xuất ra tới tệp nạp được

Forms xuất ra một tệp Excel có sẵn các cột `ID`, `Start time`, `Completion
time`, `Email`, `Name`… rồi mới tới các câu hỏi. Việc cần làm:

1. **Xoá** các cột Forms tự thêm. Phần mềm bỏ qua cột lạ, nhưng giữ lại thì
   khó soát bằng mắt.
2. **Đổi tên cột** theo bảng dưới.
3. Lưu lại dạng **CSV UTF-8** (hoặc thả thẳng tệp `.xlsx`, phần mềm đọc được).

| Cột gốc | Đổi thành |
|---|---|
| Câu hỏi mã học sinh | `student_id` |
| Câu hỏi họ tên | `name` |
| `[thu_2] … Ranking …` | `thu_2_pref_1`, `thu_2_pref_2`, … |
| `[thu_2] … Choice …` | `test_club_1`, `test_club_2`, … |

Câu Ranking cho **một ô mỗi vị trí**: CLB em xếp nhất vào `thu_2_pref_1`, xếp
nhì vào `thu_2_pref_2`.

Câu Choice cho **một ô mỗi lựa chọn đã tick**, và ở tệp Bước 1 thì **các buổi
nối liền nhau vào cùng một dãy** `test_club_1`, `test_club_2`, … — không có
tiền tố buổi, vì phần mềm suy buổi từ chính mã CLB.

> **Đủ bao nhiêu cột?** Trần 5 là **mỗi buổi**, không phải cả tuần. Trường ba
> buổi cần tới `test_club_15`, trường sáu buổi cần tới `test_club_30`. Thiếu
> cột thì mất lựa chọn của em một cách lặng lẽ, nên cứ lấy **5 × số buổi**.

Cột điểm (`score_1`, `score_2`, …) **không thu qua Forms** — giáo viên chấm
xong mới điền, hoặc nhập thẳng ở màn hình chấm điểm của phần mềm.

**Ô chỉ được chứa mã CLB**, không chứa tên. Forms ghi cả `CLB Cờ vua
(clb_covua)` thì phải cắt còn `clb_covua` — dùng Tìm và thay thế của Excel,
không sửa từng ô.

Xem tệp mẫu đã có sẵn hình dạng cuối cùng:
`mau_csv/08_nguyen_vong_nhieu_buoi.csv` và
`mau_csv/07_chon_club_thi_nhieu_buoi.csv`.

---

## 6. Ba lỗi hay gặp, và cách phần mềm báo

| Lỗi | Phần mềm làm gì |
|---|---|
| CLB của buổi này lọt vào cột buổi khác | **Bỏ riêng ô đó**, báo *nguyện vọng lệch buổi*, nêu đích danh dòng và em |
| Một buổi khai quá 10 nguyện vọng | **Bỏ riêng buổi đó**, các buổi khác của em vẫn nhập |
| Một buổi đăng ký thi quá 5 CLB | **Bỏ riêng buổi đó**, kể cả điểm của nó |

Cả ba đều **có cảnh báo nêu tên buổi**. Sau mỗi lần nạp phải đọc hết phần cảnh
báo — nạp xong không có nghĩa là nạp đúng.

---

## 7. Soát thử trước khi gửi cho học sinh

Dựng xong biểu mẫu thì **tự điền một phiếu**, xuất tệp, đổi tên cột, rồi nạp
vào phần mềm trên một cơ sở dữ liệu trống. Nạp sạch, không cảnh báo nào, thì
mới gửi cho học sinh.

Phát hiện sai cột sau khi 200 em đã nộp thì phải sửa 200 dòng bằng tay.
