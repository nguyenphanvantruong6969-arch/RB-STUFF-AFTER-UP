# Định dạng CSV nội bộ (tài liệu kỹ thuật)

> ### Người dùng: đọc [`HUONG_DAN_SO_NHAP.md`](HUONG_DAN_SO_NHAP.md)
>
> Giao diện phần mềm chỉ nhận **Sổ nhập CLB** — một tệp Excel duy nhất
> (`SO_NHAP_CLB.xlsx`). Tài liệu này **không** dành cho người vận hành.

Tài liệu này mô tả **chính xác** ba bảng CSV mà các hàm nạp bên trong phần mềm
đọc (`import_clubs_csv`, `import_test_selection_csv`, `import_preferences_csv`).
Sổ nhập được dịch thành đúng ba bảng này (`so_nhap.thanh_csv`) rồi nạp bằng
chính các hàm đó, nên mọi quy tắc dưới đây vẫn áp dụng cho sổ. Tài liệu dành
cho người phát triển, người viết bộ chuyển đổi, và các bộ dữ liệu test trong
`du_lieu_test/`.

> Mọi quy tắc trong tài liệu này đều được **khoá bằng test tự động**
> (`tests/test_csv_mau.py`). Nếu code đổi mà tài liệu không đổi, test đỏ.

---

## 1. Có ba loại file nhập được

Phần mềm chia quy trình đăng ký làm hai bước tách biệt, mỗi bước một file:

| Thứ tự | Loại file | Nội dung |
|---|---|---|
| **Trước tiên** | Danh sách CLB | Mã CLB, tên, chỉ tiêu, chỉ tiêu dự trữ |
| **Bước 1** | Chọn club muốn thi/xét | Học sinh **tick** những club muốn dự tuyển (không xếp thứ tự) |
| **Bước 2** | Xếp hạng nguyện vọng | Học sinh **xếp thứ tự** club theo mức độ mong muốn |

Hai file học sinh độc lập nhau, nhập file nào trước cũng được — nhưng **danh
sách CLB phải có trước cả hai**.

Trường sinh hoạt **nhiều buổi trong tuần** thì vẫn đúng ba loại file đó, chỉ
thêm một cột và đổi cách đặt tên cột nguyện vọng — xem **mục 3.7**.

> 📁 **Muốn xem một trường hoàn chỉnh thay vì từng mẩu rời?** Mở thư mục
> **`vi_du_day_du/`**. Trong đó là một trường 3 buổi · 9 câu lạc bộ · 24 học
> sinh, ba tệp khớp nhau từng mã, nhập vào **không một cảnh báo nào**, chạy
> phân bổ ra kết quả thật. Tệp `GIAI_THICH.md` đi kèm giảng từng cột, từng
> trường hợp biên, và giải thích cả vì sao có đúng một em không vào được câu
> lạc bộ nào.
>
> Thư mục đó còn có `tao_bo_mau.py` — sửa bảng khai báo ở đầu tệp rồi chạy là
> có bộ dữ liệu cho trường mình, với chín phép soát chạy trước khi ghi.

> 📅 **Trường sinh hoạt cả tuần?** Mở **`vi_du_ca_tuan/`** — cùng ba tệp đó
> nhưng trải trên 6 buổi (`thu_2`→`thu_7`), 18 câu lạc bộ, 60 học sinh, cũng
> **0 cảnh báo** khi nhập. `GIAI_THICH.md` của nó nói rõ cái gì đổi khi số buổi
> tăng, cái gì không đổi, và chia chỉ tiêu theo buổi thế nào cho khỏi chật.

---

## 2. Mỗi loại file có hai dạng — chọn dạng nào cũng được

Phần mềm **tự nhận diện** dạng file, bạn không phải chọn gì. Cùng một dữ
liệu, hai dạng cho ra **kết quả giống hệt nhau**.

- **Dạng rộng** — mỗi học sinh **một dòng**. Dễ nhìn, dễ sửa bằng Excel.
- **Dạng dài** — mỗi lựa chọn **một dòng**. Đây là dạng
  `06_ms_forms_transform.py` xuất ra.

Phần mềm nhận ra dạng rộng khi thấy cột tên bắt đầu bằng `pref_` hoặc
`test_club_`. Không thấy thì hiểu là dạng dài.

---

## 3. Bảng cột chi tiết

### 3.1. Chọn club muốn thi — dạng rộng
**File mẫu: `01_chon_club_thi_dang_rong.csv`**

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `student_id` | ✅ | Mã học sinh. Là **khoá chính** — phải duy nhất, không đổi giữa hai file. |
| `name` | Không | Họ tên. Chỉ dùng khi **tạo mới** học sinh; học sinh đã có tên thì không bị ghi đè. |
| `reserve_group` | Không | **Nhóm dự trữ của học sinh** (vd `chinh_sach`). Xem mục 4. |
| `test_club_1`, `test_club_2`, … | ✅ ít nhất một | `club_id` của club muốn dự tuyển. **Ô trống được bỏ qua**, không cần điền kín. |
| `score_1`, `score_2`, … | Không | **Điểm chấm** cho club cùng **số thứ tự**. Xem mục 3.6. |

```csv
student_id,name,test_club_1,score_1,test_club_2,score_2
HS001,Nguyen Van An,clb_bongro,8.5,clb_tienganh,9
HS002,Tran Thi Binh,clb_tienganh,6.5,,
```

Số cột `test_club_*` tuỳ bạn — thêm bao nhiêu cũng được.

### 3.2. Chọn club muốn thi — dạng dài
**File mẫu: `02_chon_club_thi_dang_dai.csv`**

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `student_id` | ✅ | Mã học sinh, **lặp lại** ở mỗi dòng của cùng học sinh. |
| `name` | Không | Họ tên. |
| `club_id` | ✅ | Một club mỗi dòng. |
| `score` | Không | **Điểm chấm** cho club ở dòng đó. Xem mục 3.6. |

```csv
student_id,name,club_id,score
HS001,Nguyen Van An,clb_bongro,8.5
HS001,Nguyen Van An,clb_tienganh,9
HS002,Tran Thi Binh,clb_tienganh,6.5
```

### 3.3. Xếp hạng nguyện vọng — dạng rộng
**File mẫu: `03_nguyen_vong_dang_rong.csv`**

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `student_id` | ✅ | Mã học sinh. |
| `name` | Không | Họ tên. |
| `reserve_group` | Không | **Nhóm dự trữ của học sinh** (vd `chinh_sach`). Xem mục 4. |
| `pref_1`, `pref_2`, … `pref_10` | ✅ ít nhất một | **Thứ tự cột chính là thứ tự nguyện vọng.** `pref_1` = nguyện vọng 1. |

```csv
student_id,name,pref_1,pref_2,pref_3
HS001,Nguyen Van An,clb_bongro,clb_amnhac,clb_tienganh
HS002,Tran Thi Binh,clb_tienganh,,
```

### 3.4. Xếp hạng nguyện vọng — dạng dài
**File mẫu: `04_nguyen_vong_dang_dai.csv`**

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `student_id` | ✅ | Mã học sinh, lặp lại mỗi dòng. |
| `name` | Không | Họ tên. |
| `club_id` | ✅ | Một club mỗi dòng. |
| `rank` | Nên có | Thứ hạng nguyện vọng (1 = cao nhất). **Cột này quyết định thứ tự, không phải thứ tự dòng trong file.** Thiếu cột `rank` thì phần mềm mới dùng thứ tự dòng. |

```csv
student_id,name,club_id,rank
HS001,Nguyen Van An,clb_bongro,1
HS001,Nguyen Van An,clb_amnhac,2
```

---

### 3.5. Danh sách CLB
**File mẫu: `05_danh_sach_club.csv`**

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `club_id` | ✅ | Mã CLB. Chính là mã dùng trong hai file học sinh — phải khớp từng ký tự. |
| `name` | ✅ | Tên đầy đủ để hiển thị và in ra file kết quả. |
| `capacity` | ✅ | Tổng chỉ tiêu. Phải **lớn hơn 0**. |
| `reserve_capacity` | Không | Số suất dành cho nhóm dự trữ. Bỏ trống = 0. Không được lớn hơn `capacity`. |
| `reserve_group` | Không | Tên nhóm được ưu tiên (vd `chinh_sach`). Bỏ trống = CLB không có dự trữ. |

```csv
club_id,name,capacity,reserve_capacity,reserve_group
clb_bongro,CLB Bóng rổ,20,0,
clb_tienganh,CLB Tiếng Anh,25,5,chinh_sach
```

Nhập lại file này là **cập nhật** CLB đã có (theo `club_id`), không tạo trùng.
Dòng nào có chỉ tiêu sai (bằng 0, hoặc dự trữ lớn hơn tổng chỉ tiêu) thì
**bỏ qua riêng dòng đó** kèm cảnh báo ghi rõ số dòng — các dòng còn lại vẫn
nhập bình thường.

---

### 3.7. Trường tổ chức NHIỀU BUỔI trong tuần

Trường chỉ sinh hoạt **một buổi** thì bỏ qua cả mục này — ba file ở trên là đủ,
và không có gì đổi.

Trường xếp cả tuần thì thêm **một cột** vào danh sách CLB, và nguyện vọng dùng
**một bộ cột cho mỗi buổi**.

**File mẫu: `06_danh_sach_club_nhieu_buoi.csv` · `07_chon_club_thi_nhieu_buoi.csv`
· `08_nguyen_vong_nhieu_buoi.csv`**

#### Danh sách CLB: thêm cột `buoi`

| Cột | Bắt buộc | Ý nghĩa |
|---|---|---|
| `buoi` | Không | Buổi CLB sinh hoạt. Bỏ trống = buổi mặc định. |

```csv
club_id,name,capacity,reserve_capacity,reserve_group,buoi
clb_covua,CLB Cờ vua,20,0,,thu_2
clb_robotics,CLB Robotics,12,0,,thu_4
clb_bongro,CLB Bóng rổ,20,0,,thu_6
```

`buoi` là **nhãn tự do**, phần mềm không diễn giải nội dung — nó chỉ hỏi *"hai
nhãn này có bằng nhau không"*. `thu_2` hay `Thứ Hai` hay `thu_3_tiet_9` đều
chạy được, miễn **viết thống nhất một kiểu** trong cả file.

Chỉ có một chỗ phần mềm đọc hiểu nhãn: **xếp thứ tự hiển thị**. Nó nhận ra
`thu_2`…`thu_7`, `Thứ Hai`, `t6`, `cn`, `monday` và xếp theo đúng thứ tự ngày;
nhãn toàn chữ số (`1`, `2`, `10`) xếp theo giá trị số; nhãn lạ xếp cuối theo
vần. Sắp sai thứ tự chỉ làm khó đọc, **không** làm sai kết quả xếp lớp.

> **Một CLB sinh hoạt đúng MỘT buổi.** Hai CLB cùng `buoi` là trùng giờ, nên
> một em chỉ vào được một trong hai. Đó cũng là toàn bộ ý nghĩa của cột này.

#### Nguyện vọng: mỗi buổi một bộ cột

Đặt tên cột là `<buoi>_pref_<số>` — phần trước `_pref_` chính là nhãn buổi:

```csv
student_id,name,thu_2_pref_1,thu_2_pref_2,thu_4_pref_1,thu_6_pref_1
HS001,Nguyễn Văn An,clb_nhiepanh,clb_covua,clb_robotics,clb_bongro
HS002,Trần Thị Bình,clb_nhiepanh,,,clb_lamvuon
```

Đây đúng là hình dạng Microsoft Forms xuất ra khi mỗi buổi là **một câu hỏi
Ranking riêng** — và cũng là lý do trần nguyện vọng tính theo từng buổi.

**Bỏ trống một buổi nghĩa là *"em bận buổi đó"*.** Không cần thêm cột nào để
nói điều ấy: danh sách rỗng đã nói đúng rồi. Ở ví dụ trên, HS002 không sinh
hoạt thứ Tư.

> **CLB ghi ở cột nào phải thuộc đúng buổi đó.** Viết `clb_robotics` (buổi
> `thu_4`) vào cột `thu_2_pref_1` thì phần mềm **bỏ riêng ô đó** và báo
> `nguyện vọng lệch buổi`, nêu đích danh dòng nào em nào. Đây là lỗi gõ tay dễ
> xảy ra nhất khi ghép file bằng tay, và im lặng bỏ qua nó là im lặng đổi
> nguyện vọng của học sinh.

#### File chọn CLB muốn thi: **không đổi gì**

Vẫn đúng bộ cột cũ (`test_club_1`, `score_1`, …). Buổi suy ra từ chính CLB em
chọn, nên không cần nhắc lại ở đây.

---

### 3.6. Cột điểm — nạp điểm chấm thẳng từ file

**Không bắt buộc.** Bỏ trống thì chấm điểm trong phần mềm như trước.

Nhưng nếu có sẵn điểm (chấm trên giấy rồi nhập Excel), điền vào đây tiết kiệm rất
nhiều: bộ 120 học sinh cần **396 ô điểm**, gõ tay trong phần mềm mất khoảng 18
phút.

**Dạng rộng — ghép theo SỐ THỨ TỰ trong tên cột, không theo vị trí:**

| Cột club | Cột điểm đi kèm |
|---|---|
| `test_club_1` | `score_1` |
| `test_club_2` | `score_2` |
| `test_club_7` | `score_7` |

Bỏ trống `test_club_2` mà vẫn điền `test_club_3` cũng không sao — phần mềm ghép
theo con số, không đếm cột.

**Dạng dài:** một cột `score` duy nhất, ứng với `club_id` trên cùng dòng.

**Chấp nhận cả dấu phẩy thập phân.** Excel bản tiếng Việt lưu `8,5` chứ không phải
`8.5`; cả hai đều đọc được.

**Ô điểm hỏng chỉ mất ô đó, không mất cả học sinh:**

| Tình huống | Phần mềm làm gì |
|---|---|
| Điểm ghi chữ (`tám phẩy năm`) | Bỏ riêng ô điểm, **giữ nguyên** lựa chọn thi, có cảnh báo |
| Điểm âm (`-8`) | Bỏ riêng ô điểm, có cảnh báo — gần như chắc là thừa dấu trừ |
| Có điểm mà ô club cùng số để trống | Bỏ riêng ô điểm, có cảnh báo gõ lệch cột |
| Điểm cho club em đó không đăng ký thi | Bỏ riêng ô điểm, có cảnh báo |

> ⚠️ **Cột điểm chỉ thuộc file CHỌN CLB MUỐN THI.** Đặt `score_*` vào file xếp
> hạng nguyện vọng thì điểm **không** được nạp — phần mềm sẽ báo rõ điều đó thay
> vì im lặng bỏ qua.

**Nạp file có điểm xong là chạy phân bổ được ngay** — bảng *Cảnh báo dữ liệu* sẽ
không còn mục "chưa chấm điểm" nào.

## 4. Quy tắc phải biết trước khi nhập

### Mã học sinh: viết thống nhất một kiểu

`student_id` là **khoá chính**, và phần mềm phân biệt chữ hoa với chữ thường:
`hs001` và `HS001` là **hai học sinh khác nhau**. File tick chọn viết kiểu
này, file nguyện vọng viết kiểu kia, là thành hai hồ sơ rời rạc mỗi cái thiếu
một nửa.

Phần mềm **cảnh báo** khi gặp hai mã chỉ khác hoa/thường, nhưng **không tự
gộp** — gộp nhầm hai em có thật thì hỏng nặng hơn nhiều. Người nhập tự quyết.

> Riêng **mã CLB** thì được tha: `CLB_BongRo` khớp với `clb_bongro` như
> thường. Khác biệt là mã CLB có danh sách gốc để đối chiếu, còn mã học sinh
> thì không.

### ⚠️ Excel và mã có số 0 đứng đầu

Mã như `0012345` mà để Excel tự nhận định dạng thì nó biến thành số `12345`,
**mất số 0**. Phần mềm nhận đúng những gì Excel lưu, nên không cứu được.

Cách tránh: bôi đen cột mã → định dạng ô → chọn **Text**, rồi mới nhập. Trong
file mẫu, cột `student_id` đã ở dạng text sẵn.

**Phần mềm phát hiện giúp bạn.** Nếu trong cùng một file có mã toàn chữ số ngắn
hơn hẳn những mã còn lại, bạn sẽ thấy cảnh báo:

> Mã `12348` chỉ dài 5 chữ số, trong khi phần lớn mã trong file dài 7 — nhiều
> khả năng Excel đã cắt mất số 0 ở đầu.

Đây chỉ là **cảnh báo, không chặn nhập** — phần mềm không biết mã gốc dài bao
nhiêu, tự thêm số 0 vào là bịa dữ liệu. Bạn phải sửa ở file gốc rồi nhập lại.

### ⚠️ CLB phải có TRƯỚC file học sinh
`club_id` trong file học sinh **phải đã tồn tại**. Nếu một học sinh có bất kỳ
`club_id` nào chưa có, **cả học sinh đó bị bỏ qua** — phần mềm không nhập một
nửa. Có cảnh báo ghi rõ mã nào sai.

Sổ nhập CLB không bao giờ rơi vào tình huống này: `import_so_nhap` luôn nạp
bảng CLB trước rồi mới tới hai bảng học sinh.

### Nhập lại là GHI ĐÈ, không cộng dồn
Nhập lần hai **xoá sạch** nguyện vọng cũ của những học sinh có trong file,
rồi ghi lại từ đầu. Học sinh **không có** trong file thì không bị đụng tới.
Nhờ vậy bạn sửa một lớp mà không ảnh hưởng lớp khác.

### Tối đa 10 nguyện vọng MỖI BUỔI
Giới hạn tính **sau khi loại trùng**, và tính **cho từng buổi một**, không
phải cho cả tuần. Trường sáu buổi thì một em xếp được tới 60 nguyện vọng,
miễn là mỗi buổi không quá 10.

Con số 10 không tuỳ tiện: đó là số mục tối đa của một câu hỏi Ranking trên
Microsoft Forms, mà mỗi buổi là **một câu Ranking riêng**.

Buổi nào quá 10 thì **riêng buổi đó không được nhập**, kèm cảnh báo nêu đích
danh em nào buổi nào. Các buổi khác của em vẫn nhập bình thường — các buổi
độc lập với nhau, nên một lỗi ở thứ Ba không có lý do gì làm em mất cả tuần.
Chỉ khi **mọi** buổi đều quá trần thì học sinh mới bị bỏ hẳn.

Phần mềm **không tự cắt** còn 10, vì cắt bớt là âm thầm đổi nguyện vọng của
học sinh.

Trường chỉ tổ chức **một buổi** thì mọi câu lạc bộ thuộc cùng một buổi, nên
"10 mỗi buổi" thu về đúng "10 tổng" — y hệt cách phần mềm vẫn làm từ trước.

### Tối đa 5 câu lạc bộ dự thi MỖI BUỔI
Cùng một luật, áp cho tệp **chọn CLB muốn thi**. Thi quá năm câu lạc bộ trong
một buổi thì không trường nào chấm xuể; còn cả tuần sáu buổi, năm câu lạc bộ
mỗi buổi là bình thường.

Buổi nào quá 5 thì buổi đó không được nhập, **kể cả điểm của nó** — giữ lại
điểm của một câu lạc bộ em không còn dự thi chỉ tạo ra một dòng mồ côi mà
không màn hình nào đọc tới.

### Club trùng nhau được tự loại
Cùng một club xuất hiện nhiều lần thì chỉ giữ **lần đầu tiên**, kèm cảnh báo.

### Học sinh chưa có sẽ được tạo tự động
Mã học sinh chưa tồn tại thì phần mềm tạo mới, lấy `name` làm tên (không
có `name` thì lấy chính mã học sinh).

### Nhóm dự trữ điền thẳng trong file
Thêm cột `reserve_group` vào file học sinh là xong — không phải vào màn hình
04 gán tay từng em nữa.

| Ô | Kết quả |
|---|---|
| Có giá trị | **Ghi đè** nhóm hiện có (người nhập chủ động đưa vào) |
| Để trống | **Giữ nguyên**, không xoá nhóm đã gán trước đó |
| Không có cột này | Cũng giữ nguyên — file thiếu cột không làm mất dữ liệu |

### Không phải lo gõ khác kiểu

Phần mềm **tự quy mọi cách viết về một mã**: bỏ dấu tiếng Việt, chuyển chữ
thường, thay khoảng trắng và dấu nối bằng gạch dưới.

| Bạn gõ | Phần mềm lưu |
|---|---|
| `chinh_sach` | `chinh_sach` |
| `Chính sách` | `chinh_sach` |
| `CHÍNH SÁCH` | `chinh_sach` |
| `Chính-Sách` | `chinh_sach` |
| `Đội tuyển` | `doi_tuyen` |
| `Khối 10` | `khoi_10` |

Nên file CLB ghi `chinh_sach` còn file học sinh gõ `Chính sách` vẫn nhận
nhau. Trước đây đó là hai nhóm khác nhau và học sinh diện chính sách **mất
suất dự trữ** mà không ai biết.

Chuẩn hoá chỉ gộp các cách viết **cùng một chữ**. `Khối 10` và `Khối 11` vẫn
là hai nhóm khác nhau, đúng như phải thế.

### Gõ sai hẳn thì được báo ngay

Nếu nhãn không CLB nào nhận — ví dụ gõ thiếu chữ thành `chinh_sac` — phần mềm
báo **ngay khi vừa nạp file**, kèm gợi ý:

> Nhãn dự trữ `chinh_sac` (1 học sinh) không CLB nào nhận — các em này sẽ
> KHÔNG được xét diện dự trữ. Có phải bạn định ghi `chinh_sach`?

Không phải chờ mở mục *Cảnh báo dữ liệu* mới thấy.

> Nhóm dự trữ chính là cơ chế ưu tiên của RB-DA. Bỏ trống hết thì thuật toán
> vẫn chạy trơn tru và **không báo lỗi gì** — chỉ là không em nào vào được
> theo diện dự trữ. Kiểm tra lại ở màn hình *04 Quản lý club & dự trữ*.

---

## 5. Về file Excel

### Lưu file đúng cách
Trong Excel: **File → Save As → chọn `CSV UTF-8 (Comma delimited) (*.csv)`**.

Phải chọn đúng **UTF-8**, nếu không tên tiếng Việt có dấu sẽ thành ký tự
lạ trong phần mềm.

### Dấu phân cách
Phần mềm tự nhận cả **dấu phẩy `,`**, **dấu chấm phẩy `;`** và **Tab**.
Excel bản tiếng Việt hay lưu bằng dấu chấm phẩy — vẫn nhập được bình thường.

### Ký tự BOM
Excel thêm một ký tự vô hình (BOM) vào đầu file khi lưu CSV UTF-8.
Phần mềm **đã xử lý**, bạn không cần làm gì. (Trước phiên bản này, chính
ký tự đó khiến file đúng vẫn báo "thiếu cột `student_id`".)

---

## 6. Bảng lỗi thường gặp

| Hiện tượng | Nguyên nhân | Cách xử lý |
|---|---|---|
| Báo thiếu cột `student_id` | Sai tên cột, hoặc file có dòng tiêu đề phụ ở trên | Dòng đầu tiên phải là dòng tên cột |
| Nhiều học sinh "bị bỏ qua" | `club_id` chưa được tạo trong phần mềm | Kiểm tra lại danh sách club ở màn hình 04 |
| Tên tiếng Việt thành ký tự lạ | Lưu sai bảng mã | Lưu lại bằng **CSV UTF-8** |
| Nguyện vọng sai thứ tự | Dạng dài thiếu cột `rank` | Bổ sung cột `rank`, hoặc sắp đúng thứ tự dòng |
| Nhập xong nhưng dự trữ không chạy | Chưa điền `reserve_group`, hoặc gõ sai hẳn tên nhóm | Đọc cảnh báo hiện ngay sau khi nhập — nó gợi ý đúng nhóm bạn định ghi |
| Nhãn hiện ra khác lúc gõ (`Chính sách` thành `chinh_sach`) | Đúng thiết kế — phần mềm quy về một mã để hai file luôn khớp | Không phải sửa gì |
| Chỉ tiêu CLB từ Excel bị bỏ qua | (đã xử lý) Excel lưu số dạng `20.0`; phần mềm tự đưa về `20` |
| Phần mềm hỏi "chưa chắc đây là file gì" | Bộ cột hợp với cả hai loại | Chọn loại ở ô bên phải, hoặc thêm cột `rank` nếu là nguyện vọng |
| Học sinh bị bỏ qua hàng loạt ngay lần nhập đầu | Chưa nhập danh sách CLB | Thả cả file CLB vào cùng lúc, phần mềm tự xếp thứ tự |
| Báo "mã X xuất hiện N lần" | Một học sinh có nhiều dòng trong file dạng rộng | Chỉ dòng **cuối** được giữ. Xoá dòng thừa nếu đó là nhầm lẫn |
| Báo "chỉ khác chữ hoa/thường" | Hai file viết mã học sinh khác kiểu (`hs001` vs `HS001`) | Sửa cho hai file cùng kiểu — phần mềm **không tự gộp**, vì gộp nhầm hai em có thật thì hỏng nặng hơn |
| Mã CLB viết hoa/thường khác file CLB | Không sao — phần mềm tự khớp | Không phải sửa |

---

## 7. Bộ club dùng trong file mẫu

Không phải tạo tay nữa — **thả `05_danh_sach_club.csv` vào cùng lúc** là xong.
Nội dung file đó đúng bằng bảng dưới:

| club_id | Tên | Chỉ tiêu | Chỉ tiêu dự trữ | Nhóm dự trữ |
|---|---|---|---|---|
| `clb_bongro` | CLB Bóng rổ | 20 | 0 | |
| `clb_tienganh` | CLB Tiếng Anh | 25 | 5 | `chinh_sach` |
| `clb_robotics` | CLB Robotics | 15 | 0 | |
| `clb_amnhac` | CLB Âm nhạc | 20 | 0 | |
| `clb_mythuat` | CLB Mỹ thuật | 18 | 3 | `chinh_sach` |

Dữ liệu trong file mẫu là **dữ liệu bịa để minh hoạ định dạng** — không
phải học sinh thật, không dùng làm số liệu nghiên cứu.
