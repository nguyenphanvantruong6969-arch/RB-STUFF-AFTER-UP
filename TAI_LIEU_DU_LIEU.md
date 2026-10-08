# Tài liệu dữ liệu — mọi thứ về dữ liệu đầu vào, bộ chạy thử và kỹ năng sinh dữ liệu

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
>
> Mọi cái tên, mã học sinh và điểm số nêu trong tài liệu này, cũng như trong
> mọi tệp nó nhắc tới, đều **do máy sinh** theo hạt giống cố định. Hơn nữa
> phần lớn các bộ được **cố ý dựng cho cạnh tranh cao** để cơ chế thuật toán
> lộ ra — chúng không mô phỏng một phân bố nguyện vọng tự nhiên.
>
> **Trình bày các con số này như số liệu khảo sát thật là bịa đặt dữ liệu.**

Tài liệu này gom về một chỗ tất cả những gì trước đây nằm rải ở 12 tệp tài
liệu và 9 thư mục: đặc tả từng cột, kiểm kê từng bộ dữ liệu, toàn văn kỹ năng
sinh dữ liệu, đường nhập trong mã nguồn, và test nào canh cái gì.

Mỗi phần ghi rõ **bản chính nằm ở đâu** (xem [Phần 11](#phần-11--bản-chính-ở-đâu)).
Tài liệu này là bản tổng hợp, không phải bản thay thế.

## Mục lục

| Phần | Nội dung |
|---|---|
| [1](#phần-1--bản-đồ-năm-tầng) | Bản đồ năm tầng — thư mục nào làm gì |
| [2](#phần-2--ba-tệp-đầu-vào--đặc-tả-cột-đầy-đủ) | Ba tệp đầu vào — đặc tả đủ 8 hình dáng CSV |
| [3](#phần-3--quy-tắc-và-trần--kèm-chỗ-mã-nguồn-áp) | Quy tắc và trần, kèm chỗ mã nguồn áp |
| [4](#phần-4--kỹ-năng-sinh-du-lieu-clb) | Kỹ năng `sinh-du-lieu-clb` — toàn văn và giải phẫu |
| [5](#phần-5--kiểm-kê-toàn-bộ-tài-sản-dữ-liệu) | Kiểm kê toàn bộ tài sản dữ liệu |
| [6](#phần-6--test_04_co_loi_co_yxlsx--sáu-lỗi-cài-sẵn) | `TEST_04` — sáu lỗi cài sẵn |
| [7](#phần-7--kết-quả-đúng-đã-kiểm-chứng) | Kết quả đúng đã kiểm chứng |
| [8](#phần-8--đường-nhập-dữ-liệu-trong-mã) | Đường nhập dữ liệu trong mã |
| [9](#phần-9--test-nào-canh-bộ-nào) | Test nào canh bộ nào |
| [10](#phần-10--sinh-lại-mọi-thứ) | Sinh lại mọi thứ — một khối lệnh |
| [11](#phần-11--bản-chính-ở-đâu) | Bản chính ở đâu |

### Cần gì đọc phần nào

| Tôi muốn… | Đọc |
|---|---|
| biết tệp CSV phải có cột gì | [Phần 2](#phần-2--ba-tệp-đầu-vào--đặc-tả-cột-đầy-đủ) |
| hiểu vì sao phần mềm báo cảnh báo khi tôi nhập | [Phần 3](#phần-3--quy-tắc-và-trần--kèm-chỗ-mã-nguồn-áp), rồi [Phần 8](#phần-8--đường-nhập-dữ-liệu-trong-mã) |
| dựng bộ dữ liệu cho một trường mới | [Phần 4](#phần-4--kỹ-năng-sinh-du-lieu-clb) |
| chạy thử phần mềm mà không thấy cảnh báo nào | `du_lieu_test/bo_sach/` — [Phần 5](#phần-5--kiểm-kê-toàn-bộ-tài-sản-dữ-liệu) |
| thử tính năng nhiều buổi trong tuần | `du_lieu_test/bo_nhieu_buoi/` hoặc `bo_sau_buoi/` |
| xem một trường hoàn chỉnh, nhỏ, giải thích từng dòng | `mau_csv/vi_du_day_du/` + `GIAI_THICH.md` |
| kiểm tra phần mềm **có** cảnh báo khi dữ liệu sai | [Phần 6](#phần-6--test_04_co_loi_co_yxlsx--sáu-lỗi-cài-sẵn) |
| biết kết quả chạy ra phải như thế nào | [Phần 7](#phần-7--kết-quả-đúng-đã-kiểm-chứng) |
| sinh lại một bộ đã có trong kho | [Phần 10](#phần-10--sinh-lại-mọi-thứ) |
| sửa một quy tắc mà không làm lệch tài liệu | [Phần 11](#phần-11--bản-chính-ở-đâu) |

---

## Phần 1 · Bản đồ năm tầng

Đây là chỗ hay lẫn nhất trong kho: `mau_csv/` và `du_lieu_test/` **không** cùng
một loại. Một thư mục dạy hình dáng cột, thư mục kia cho chạy thật.

| Tầng | Ở đâu | Là gì | **Không** phải gì |
|---|---|---|---|
| **Đặc tả** | `mau_csv/*.csv` (8 tệp) | 8 tệp mẫu chỉ để xem *hình dáng cột*, mỗi tệp 5–11 dòng | không phải bộ chạy được — quá nhỏ, không có kết quả gì đáng xem |
| **Ví dụ** | `mau_csv/vi_du_day_du/` | **một trường hoàn chỉnh** đã kiểm chứng: 3 buổi · 9 CLB · 24 em | không phải bộ đo hiệu năng |
| **Bộ chạy thử** | `du_lieu_test/bo_*/` (5 bộ) | 5 bộ chạy được, từ 10 đến 200 học sinh | không phải dữ liệu thật của trường nào |
| **Sinh mới** | `.claude/skills/sinh-du-lieu-clb/` | kỹ năng Claude + script dựng bộ mới cho trường khác | không phải nơi chứa bộ dữ liệu |
| **Canh** | `tests/` (~15 tệp liên quan) | khoá mọi lời hứa của bốn tầng trên | |

Thêm hai thư mục không thuộc luồng nhập:

| Ở đâu | Là gì |
|---|---|
| `du_lieu_test/thu_tai/` | bộ **đo tải** — sinh dữ liệu theo tham số để đo giới hạn phần mềm |
| `du_lieu_test/do_*.py` + `so_lieu_*.json` | 11 script **đo** trả lời từng câu hỏi về thuật toán, kèm kết quả đã chốt |

---

## Phần 2 · Ba tệp đầu vào — đặc tả cột đầy đủ

> **Người vận hành không dùng ba tệp này nữa.** Giao diện chỉ nhận Sổ nhập CLB
> (`mau_csv/HUONG_DAN_SO_NHAP.md`). Sổ được dịch thành đúng ba bảng dưới đây
> (`so_nhap.thanh_csv`) rồi nạp bằng các hàm nạp cũ, nên mọi quy tắc ở đây vẫn
> áp dụng. Phần này dành cho người phát triển và các bộ dữ liệu test.

Phần mềm nhận **ba loại tệp**. Mỗi loại có **dạng rộng** (một em một dòng, nhiều
cột) và **dạng dài** (một em nhiều dòng, ít cột) — chọn dạng nào cũng được.
Trường tổ chức nhiều buổi trong tuần thì thêm biến thể theo buổi.

Không phải chọn loại tệp khi nạp: phần mềm đọc dòng tiêu đề rồi tự nhận diện
(xem [Phần 8](#phần-8--đường-nhập-dữ-liệu-trong-mã)).

### Ba điều dễ sai nhất — đọc trước bảng cột

1. **`score_N` ghép với `test_club_N` theo con số trong tên cột, không theo vị
   trí.** Nên số cặp cột chỉ cần bằng số câu lạc bộ nhiều nhất *một* em dự thi,
   không phải 5 × số buổi.
2. **Câu lạc bộ không ai khai ở tệp 2 = câu lạc bộ không tổ chức thi.** Không có
   cột nào đánh dấu điều đó; phần mềm suy ra từ chính tệp ấy.
3. **Bỏ trống cả một buổi ở tệp 3 = em bận ngày đó.** Đó là dữ liệu **hợp lệ**,
   không phải thiếu sót, và phần mềm không cảnh báo.

### 2.1 · Chọn CLB muốn thi — dạng rộng

Tệp mẫu: `mau_csv/01_chon_club_thi_dang_rong.csv` · 395 B · 5 dòng dữ liệu

```csv
student_id,name,test_club_1,score_1,test_club_2,score_2,test_club_3,score_3,test_club_4,score_4
HS001,Nguyễn Văn An,clb_bongro,8.5,clb_tienganh,9,clb_amnhac,7.5,,
HS002,Trần Thị Bình,clb_tienganh,6.5,,,,,,
```

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `student_id` | ✅ | Khoá chính. **Phân biệt hoa thường** |
| `name` | | Chưa có em này thì lấy làm tên; thiếu thì lấy chính mã |
| `test_club_N` | | `club_id` phải **có trước** trong danh sách CLB |
| `score_N` | | Điểm của `test_club_N`. Ghép **theo con số N**, không theo vị trí |

Bỏ trống cặp cột cuối là bình thường — em thi ít câu lạc bộ hơn số cột.

### 2.2 · Chọn CLB muốn thi — dạng dài

Tệp mẫu: `mau_csv/02_chon_club_thi_dang_dai.csv` · 447 B · 11 dòng dữ liệu

```csv
student_id,name,club_id,score
HS001,Nguyễn Văn An,clb_bongro,8.5
HS001,Nguyễn Văn An,clb_tienganh,9
```

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `student_id` | ✅ | Lặp lại trên mỗi dòng của cùng một em |
| `name` | | |
| `club_id` | ✅ | Một câu lạc bộ mỗi dòng |
| `score` | | |

> ⚠️ Tệp này chỉ có `student_id` + `club_id` (không có `rank`, không có
> `capacity`) nên **phần mềm không tự đoán được** đây là tệp dự thi hay tệp
> nguyện vọng — nó sẽ hỏi lại. Xem `csv_kind_ambiguous` ở [Phần 8](#phần-8--đường-nhập-dữ-liệu-trong-mã).

### 2.3 · Xếp hạng nguyện vọng — dạng rộng

Tệp mẫu: `mau_csv/03_nguyen_vong_dang_rong.csv` · 276 B · 5 dòng dữ liệu

```csv
student_id,name,pref_1,pref_2,pref_3
HS001,Nguyễn Văn An,clb_bongro,clb_amnhac,clb_tienganh
HS002,Trần Thị Bình,clb_tienganh,,
```

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `student_id` | ✅ | |
| `name` | | |
| `pref_N` | | Thứ tự ưu tiên: `pref_1` là nguyện vọng 1. Tối đa **10** |

### 2.4 · Xếp hạng nguyện vọng — dạng dài

Tệp mẫu: `mau_csv/04_nguyen_vong_dang_dai.csv` · 397 B · 10 dòng dữ liệu

```csv
student_id,name,club_id,rank
HS001,Nguyễn Văn An,clb_bongro,1
HS001,Nguyễn Văn An,clb_amnhac,2
```

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `student_id` | ✅ | |
| `name` | | |
| `club_id` | ✅ | |
| `rank` | ✅ | Số thứ tự ưu tiên. Cột `rank` là dấu hiệu để phần mềm biết chắc đây là tệp nguyện vọng |

### 2.5 · Danh sách CLB — **nạp TRƯỚC hai tệp kia**

Tệp mẫu: `mau_csv/05_danh_sach_club.csv` · 239 B · 5 dòng dữ liệu

```csv
club_id,name,capacity,reserve_capacity,reserve_group
clb_bongro,CLB Bóng rổ,20,0,
clb_tienganh,CLB Tiếng Anh,25,5,chinh_sach
clb_robotics,CLB Robotics,15,0,
clb_amnhac,CLB Âm nhạc,20,0,
clb_mythuat,CLB Mỹ thuật,18,3,chinh_sach
```

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `club_id` | ✅ | Không dấu, không khoảng trắng. Khớp **từng ký tự** với hai tệp kia |
| `name` | ✅ | Tên hiển thị, có dấu |
| `capacity` | ✅ | **> 0** |
| `reserve_capacity` | | ≤ `capacity`. Lớn hơn 0 thì **bắt buộc** có `reserve_group` |
| `reserve_group` | | Nhãn nhóm ưu tiên |

### 2.6 · Danh sách CLB — trường nhiều buổi

Tệp mẫu: `mau_csv/06_danh_sach_club_nhieu_buoi.csv` · 309 B · 6 dòng dữ liệu

```csv
club_id,name,capacity,reserve_capacity,reserve_group,buoi
clb_covua,CLB Cờ vua,20,0,,thu_2
clb_nhiepanh,CLB Nhiếp ảnh,15,3,khoi_10,thu_2
clb_robotics,CLB Robotics,12,0,,thu_4
clb_khoahoc,CLB Khoa học,16,2,chinh_sach,thu_4
clb_bongro,CLB Bóng rổ,20,0,,thu_6
clb_lamvuon,CLB Làm vườn,18,0,,thu_6
```

Giống 2.5, thêm một cột:

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `buoi` | | Trường **một buổi thì bỏ hẳn cột này**. Khai thì phải khai cho **mọi** câu lạc bộ |

Nhãn buổi chuẩn nên dùng: `thu_2` `thu_3` `thu_4` `thu_5` `thu_6` `thu_7` `chu_nhat`.
Phần mềm còn nhận nhiều cách viết khác và tự quy về một nhãn (`chuan_hoa_buoi`).

### 2.7 · Chọn CLB muốn thi — trường nhiều buổi

Tệp mẫu: `mau_csv/07_chon_club_thi_nhieu_buoi.csv` · 351 B · 6 dòng dữ liệu

```csv
student_id,name,reserve_group,test_club_1,score_1,test_club_2,score_2
HS001,Nguyễn Văn An,,clb_nhiepanh,8.5,clb_robotics,9
HS002,Trần Thị Bình,khoi_10,clb_nhiepanh,7,,
```

**Cột dự thi không đổi gì** so với trường một buổi — phần mềm biết câu lạc bộ nào
thuộc buổi nào từ tệp danh sách, nên không cần nhắc lại ở đây. Chỉ thêm một cột
tuỳ chọn:

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `reserve_group` | | Gán nhóm dự trữ cho **học sinh**, ngay trong tệp. Có giá trị = ghi đè nhóm cũ; để trống = giữ nguyên; không có cột = giữ nguyên |

### 2.8 · Xếp hạng nguyện vọng — trường nhiều buổi

Tệp mẫu: `mau_csv/08_nguyen_vong_nhieu_buoi.csv` · 532 B · 6 dòng dữ liệu

```csv
student_id,name,reserve_group,thu_2_pref_1,thu_2_pref_2,thu_4_pref_1,thu_4_pref_2,thu_6_pref_1,thu_6_pref_2
HS001,Nguyễn Văn An,,clb_nhiepanh,clb_covua,clb_robotics,clb_khoahoc,clb_bongro,
HS002,Trần Thị Bình,khoi_10,clb_nhiepanh,,,,clb_lamvuon,clb_bongro
```

| Cột | Bắt buộc | Quy tắc |
|---|---|---|
| `student_id` | ✅ | |
| `name` | | |
| `reserve_group` | | như 2.7 |
| `<buổi>_pref_<số>` | | Tên buổi + `_pref_` + số. **Số đếm lại từ 1 ở mỗi buổi**. Tối đa 10 mỗi buổi |

Dòng `HS002` ở trên minh hoạ cả hai điều: em bỏ trống hẳn `thu_4` (bận ngày đó —
hợp lệ), và ở `thu_6` xếp hai nguyện vọng trong khi `thu_2` chỉ xếp một.

### 2.9 · Bảng tra nhanh — tệp mẫu nào ứng với hình dáng nào

| Hình dáng | Tệp mẫu | Dấu hiệu phần mềm nhận ra |
|---|---|---|
| Danh sách CLB | `05_danh_sach_club.csv` | có `capacity` **và** `club_id` |
| Danh sách CLB nhiều buổi | `06_danh_sach_club_nhieu_buoi.csv` | như trên, thêm cột `buoi` |
| Nguyện vọng dạng rộng | `03_nguyen_vong_dang_rong.csv` | có cột bắt đầu bằng `pref_` |
| Nguyện vọng theo buổi | `08_nguyen_vong_nhieu_buoi.csv` | khớp khuôn `<buổi>_pref_<số>` |
| Dự thi dạng rộng | `01_chon_club_thi_dang_rong.csv` | có cột bắt đầu bằng `test_club_` |
| Nguyện vọng dạng dài | `04_nguyen_vong_dang_dai.csv` | có `rank` + `club_id` + `student_id` |
| Dự thi dạng dài | `02_chon_club_thi_dang_dai.csv` | chỉ `student_id` + `club_id` → **phần mềm hỏi lại** |

---

## Phần 3 · Quy tắc và trần — kèm chỗ mã nguồn áp

Mỗi quy tắc ghi kèm **hàm áp nó**, để kiểm được ngay chứ không phải tin tài liệu.
Số dòng là chỉ dẫn tại thời điểm viết; **tên hàm mới là thứ đáng tin** — số dòng
đổi theo mỗi lần sửa mã.

### 3.1 · Hai trần cứng

| Trần | Giá trị | Khai ở | Áp ở |
|---|---|---|---|
| `TRAN_NGUYEN_VONG_MOI_BUOI` | **10** | `rbda_priority_pipeline.py:84` | `import_preferences_csv`, `validate_data_integrity`, `get_data_health_report` |
| `TRAN_CLB_THI_MOI_BUOI` | **5** | `rbda_priority_pipeline.py:89` | `import_test_selection_csv`, `get_data_health_report` |

**Trần 10 nguyện vọng mỗi buổi.** Tính **sau khi loại trùng**, và tính **cho từng
buổi một**, không phải cho cả tuần — trường sáu buổi thì một em xếp được tới 60
nguyện vọng, miễn mỗi buổi không quá 10.

Con số 10 không tuỳ tiện: đó là số mục tối đa của một câu hỏi Ranking trên
Microsoft Forms, mà **mỗi buổi là một câu Ranking riêng**.

Buổi nào quá 10 thì **riêng buổi đó không được nhập**, kèm cảnh báo nêu đích danh
em nào buổi nào. Các buổi khác của em vẫn nhập bình thường — các buổi độc lập với
nhau, nên một lỗi ở thứ Ba không có lý do gì làm em mất cả tuần. Chỉ khi **mọi**
buổi đều quá trần thì học sinh mới bị bỏ hẳn.

> Phần mềm **không tự cắt** còn 10, vì cắt bớt là âm thầm đổi nguyện vọng của
> học sinh.

Trường chỉ tổ chức **một buổi** thì mọi câu lạc bộ thuộc cùng một buổi, nên "10
mỗi buổi" thu về đúng "10 tổng".

**Trần 5 câu lạc bộ dự thi mỗi buổi.** Cùng một luật, áp cho tệp chọn CLB muốn
thi. Buổi nào quá 5 thì buổi đó không được nhập, **kể cả điểm của nó** — giữ lại
điểm của một câu lạc bộ em không còn dự thi chỉ tạo ra một dòng mồ côi mà không
màn hình nào đọc tới.

> ⚠️ `validate_data_integrity` **cố ý không** kiểm trần 5
> (`rbda_priority_pipeline.py:1013`). Lý do ghi ngay trong mã: `applicants`
> ở tầng đó **không** phải "những em đã đăng ký thi" — `load_from_sqlite` đã hợp
> nhất ô tick với **mọi** câu lạc bộ em có xếp nguyện vọng, vì em không thi vẫn
> được xét ở Tầng 2. Đến tầng này hai thứ đã nhập làm một và không tách ra được
> nữa, nên đếm ở đây là đếm nhầm sang nguyện vọng. Trần 5 vì thế áp **ở lúc
> nhập**, không phải lúc kiểm toàn vẹn.

### 3.2 · Thứ tự nạp

**Danh sách câu lạc bộ phải có trước hai tệp học sinh.** `club_id` trong tệp học
sinh phải đã tồn tại; nếu một học sinh có bất kỳ `club_id` nào chưa có thì **cả
học sinh đó bị bỏ qua** — phần mềm không nhập một nửa. Có cảnh báo ghi rõ mã nào sai.

Cách chắc chắn nhất: **thả cả ba tệp cùng lúc**. Phần mềm tự sắp thứ tự nạp, nên
không bao giờ rơi vào tình huống này.

### 3.3 · Mã học sinh

`student_id` là **khoá chính**, và phần mềm **phân biệt chữ hoa với chữ thường**:
`hs001` và `HS001` là **hai học sinh khác nhau**. Tệp tick chọn viết kiểu này, tệp
nguyện vọng viết kiểu kia, là thành hai hồ sơ rời rạc mỗi cái thiếu một nửa.

Phần mềm **cảnh báo** khi gặp hai mã chỉ khác hoa/thường, nhưng **không tự gộp** —
gộp nhầm hai em có thật thì hỏng nặng hơn nhiều. Người nhập tự quyết.

> Riêng **mã câu lạc bộ** thì được tha: `CLB_BongRo` khớp với `clb_bongro` như
> thường. Khác biệt là mã câu lạc bộ có danh sách gốc để đối chiếu, còn mã học
> sinh thì không.

### 3.4 · Excel và mã có số 0 đứng đầu

Mã như `0012345` mà để Excel tự nhận định dạng thì nó biến thành số `12345`, **mất
số 0**. Phần mềm nhận đúng những gì Excel lưu, nên không cứu được.

Cách tránh: bôi đen cột mã → định dạng ô → chọn **Text**, rồi mới nhập. Trong tệp
mẫu, cột `student_id` đã ở dạng text sẵn.

Phần mềm phát hiện giúp: nếu trong cùng một tệp có mã toàn chữ số ngắn hơn hẳn
những mã còn lại, sẽ thấy cảnh báo kiểu *"Mã `12348` chỉ dài 5 chữ số, trong khi
phần lớn mã trong tệp dài 7 — nhiều khả năng Excel đã cắt mất số 0 ở đầu."*

Đây chỉ là **cảnh báo, không chặn nhập** — phần mềm không biết mã gốc dài bao
nhiêu, tự thêm số 0 vào là bịa dữ liệu. Phải sửa ở tệp gốc rồi nhập lại.

### 3.5 · BOM và bảng mã

Mọi tệp CSV sinh bởi kho này ghi bằng `utf-8-sig` — tức **UTF-8 có BOM**. Không có
BOM thì Excel đọc tên tiếng Việt thành `Nguyá»…n VÄƒn An`.

Ở đường đọc, BOM được gỡ bằng `csv_text.lstrip("﻿")` trong `_parse_csv_rows`.
Ghi chú trong mã nói rõ hai điều:

- `.strip()` **không** gỡ được BOM;
- thiếu bước này thì phần mềm báo *"thiếu `student_id`"* trên một tệp hoàn toàn đúng —
  vì tên cột đầu tiên trở thành `﻿student_id`.

### 3.6 · Dấu phân cách và dấu thập phân

`_parse_csv_rows` đoán dấu phân cách trong `,` `;` và tab, nhưng **chỉ lấy dấu phân
cách, không lấy cả dialect**: `csv.Sniffer` đoán sai `doublequote=False` trên tên
câu lạc bộ tiếng Việt có dấu ngoặc.

Điểm đọc được cả hai kiểu (`_doc_diem`):

| Ghi trong tệp | Hiểu là |
|---|---|
| `9,5` | 9,5 — cách Excel bản tiếng Việt lưu |
| `9.5` | 9,5 |
| `9` | 9,0 |

### 3.7 · Nhập lại là ghi đè, không cộng dồn

Nhập lần hai **xoá sạch** nguyện vọng cũ của những học sinh **có trong tệp**, rồi
ghi lại từ đầu. Học sinh **không có** trong tệp thì không bị đụng tới. Nhờ vậy sửa
một lớp mà không ảnh hưởng lớp khác.

> ⚠️ Hệ quả quan trọng khi chạy thử: **học sinh cũ không bị xoá.** Nạp `TEST_04`
> hôm trước thì `HS204` mang nhãn sai `chinh_sac` vẫn nằm nguyên trong cơ sở dữ
> liệu và còn kêu mãi. Muốn nạp một bộ sạch thì phải dọn trước — xem
> [Phần 7](#phần-7--kết-quả-đúng-đã-kiểm-chứng).

### 3.8 · Nhóm dự trữ

Gán nhóm dự trữ cho học sinh **ngay trong tệp** bằng cột `reserve_group`:

| Ô | Kết quả |
|---|---|
| Có giá trị | **Ghi đè** nhóm hiện có |
| Để trống | **Giữ nguyên**, không xoá nhóm đã gán trước đó |
| Không có cột này | Cũng giữ nguyên — tệp thiếu cột không làm mất dữ liệu |

Phần mềm **tự quy mọi cách viết về một mã** (`chuan_hoa_nhom_du_tru`): bỏ dấu tiếng
Việt, chuyển chữ thường, thay khoảng trắng và dấu nối bằng gạch dưới.

| Gõ | Lưu |
|---|---|
| `chinh_sach` · `Chính sách` · `CHÍNH SÁCH` · `Chính-Sách` | `chinh_sach` |
| `Đội tuyển` | `doi_tuyen` |
| `Khối 10` | `khoi_10` |

Nên tệp CLB ghi `chinh_sach` còn tệp học sinh gõ `Chính sách` vẫn nhận nhau. Trước
khi có bước chuẩn hoá này, đó là hai nhóm khác nhau và học sinh diện chính sách
**mất suất dự trữ** mà không ai biết.

Chuẩn hoá chỉ gộp các cách viết **cùng một chữ**: `Khối 10` và `Khối 11` vẫn là hai
nhóm khác nhau, đúng như phải thế.

Gõ sai hẳn thì được báo **ngay khi vừa nạp tệp**, kèm gợi ý sửa — ví dụ nhãn
`chinh_sac` (thiếu chữ h) sinh cảnh báo *"không CLB nào nhận … Có phải bạn định ghi
`chinh_sach`?"*, không phải chờ mở mục Cảnh báo dữ liệu mới thấy.

> Nhóm dự trữ **chính là** cơ chế ưu tiên của RB-DA. Bỏ trống hết thì thuật toán
> vẫn chạy trơn tru và **không báo lỗi gì** — chỉ là không em nào vào được theo
> diện dự trữ.

### 3.9 · Những cái tự sửa được thì phần mềm tự sửa

| Tình huống | Xử lý |
|---|---|
| Cùng một câu lạc bộ xuất hiện nhiều lần cho một em | giữ **lần đầu**, kèm cảnh báo |
| Mã học sinh chưa tồn tại | **tạo mới**, lấy `name` làm tên (thiếu `name` thì lấy chính mã) |
| Một dòng câu lạc bộ sai định dạng | bỏ **riêng dòng đó**, cảnh báo nêu số dòng |
| Sức chứa Excel lưu thành `20.0` | `_o_excel_thanh_chu` quy về `20` — không có bước này thì `ValueError` và **âm thầm mất dòng câu lạc bộ đó** |

### 3.10 · Điều kiện về sức chứa và buổi

- `capacity > 0`
- `reserve_capacity ≤ capacity`
- `reserve_capacity > 0` thì **bắt buộc** có `reserve_group`
- khai cột `buoi` thì phải khai cho **mọi** câu lạc bộ, hoặc bỏ trống hết — khai
  nửa vời thì những câu lạc bộ bỏ trống bị gom chung một buổi, và học sinh chỉ vào
  được một trong số chúng

---

## Phần 4 · Kỹ năng `sinh-du-lieu-clb`

Kỹ năng này làm một việc: dựng Sổ nhập CLB (`SO_NHAP_CLB.xlsx`) sao cho nhập vào
phần mềm **không một cảnh báo nào**, hoặc soát một sổ (hay bộ ba CSV cũ) đã có để
tìm chỗ sai.

```
.claude/
└── skills/
    └── sinh-du-lieu-clb/
        ├── SKILL.md                 8 494 B · 156 dòng
        └── scripts/
            └── sinh_du_lieu.py     21 734 B · 496 dòng
```

Không có `.claude/settings.json`, không có hook, không có kỹ năng nào khác.

### 4.1 · Toàn văn `SKILL.md`

Dưới đây là **nguyên văn** `.claude/skills/sinh-du-lieu-clb/SKILL.md`, không cắt bớt:

~~~~markdown
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
~~~~

### 4.2 · Giải phẫu `scripts/sinh_du_lieu.py`

496 dòng, không phụ thuộc thư viện ngoài (chỉ `argparse` `csv` `io` `json` `os`
`random` `sys`). Nguyên tắc kiến trúc ghi ngay ở đầu tệp:

> Ba tệp luôn đi ra từ **MỘT** nguồn trong bộ nhớ, và mọi phép soát chạy **TRƯỚC**
> khi ghi. Sai một điều là không tệp nào được ghi — sinh ra một bộ dữ liệu hỏng còn
> tệ hơn không sinh gì, vì nó trông y như thật.
>
> Đoạn mã này **KHÔNG tự sửa** dữ liệu sai. Sửa giúp là giấu mất chỗ sai.

#### Hằng số

| Tên | Giá trị | Ghi chú |
|---|---|---|
| `TRAN_NGUYEN_VONG_MOI_BUOI` | `10` | **Phản chiếu** `rbda_priority_pipeline`, không tự nghĩ ra |
| `TRAN_CLB_THI_MOI_BUOI` | `5` | như trên |
| `TEN_TEP` | `{clb, thi, nv}` → `01_danh_sach_CLB.csv`, `02_chon_CLB_muon_thi.csv`, `03_xep_hang_nguyen_vong.csv` | tên tệp **cố định** |
| `BUOI_CHUAN` | `thu_2` … `chu_nhat` (7 nhãn) | cách viết chuẩn nên dùng khi sinh mới |

#### Hàm

| Hàm | Dòng | Việc |
|---|---|---|
| `soat(clb, hs)` | 49 | Trả **danh sách lỗi chặn**; rỗng = hợp lệ. Dùng chung cho cả sinh mới lẫn kiểm bộ đã có |
| `canh_bao_men(clb, hs)` | 138 | Cảnh báo mềm — **không chặn ghi** |
| `ghi_bo(thu_muc, clb, hs)` | 177 | Ghi ba tệp `utf-8-sig`. **Gọi sau khi `soat()` đã trả về rỗng** |
| `doc_bo(thu_muc)` | 256 | Đọc lại một bộ đã có, cho chế độ `soat` |
| `sinh_ngau_nhien(...)` | 325 | Một trường ngẫu nhiên nhưng luôn hợp lệ, tất định theo `seed` |
| `_in_ket_qua(clb, hs, loi, canh_bao)` | 433 | In kết quả, trả mã thoát |
| `main(argv=None)` | 447 | CLI ba lệnh con |

#### Bảng dữ liệu để bịa tên

| Bảng | Dòng | Số mục |
|---|---|---|
| `_HO` | 304 | 18 họ (`Nguyễn` `Trần` `Lê` …) |
| `_DEM` | 306 | 10 chữ đệm (`Văn` `Thị` `Minh` …) |
| `_TEN` | 307 | 24 tên (`An` `Bình` `Chi` …) |
| `_CHU_DE` | 311 | 20 cặp `(club_id, tên hiển thị)` |

Tên sinh ra là **ghép ngẫu nhiên** từ ba bảng đầu. `_CHU_DE` giới hạn số câu lạc bộ
sinh được: `clb_moi_buoi × số buổi` vượt 20 là lỗi dừng ngay, có thông báo rõ.

#### Chữ ký đầy đủ của bộ sinh

```python
sinh_ngau_nhien(n_hs, ds_buoi, clb_moi_buoi, seed,
                do_choi=1.15, ti_le_du_tru=0.35, ti_le_co_thi=0.34)
```

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `n_hs` | — | số học sinh |
| `ds_buoi` | — | danh sách nhãn buổi; `[""]` = trường một buổi |
| `clb_moi_buoi` | — | số câu lạc bộ mỗi buổi |
| `seed` | — | hạt giống — **cùng seed cho ra cùng bộ, từng byte** |
| `do_choi` | `1.15` | tổng chỗ so với số học sinh |
| `ti_le_du_tru` | `0.35` | xác suất một câu lạc bộ có suất dự trữ |
| `ti_le_co_thi` | `0.34` | xác suất một câu lạc bộ tổ chức thi |

Các xác suất cố định khác, đọc thẳng từ mã:

| Điều | Xác suất |
|---|---|
| một em bỏ trống hẳn một buổi (bận ngày đó) | `0.12` |
| một em được gán nhóm dự trữ | `0.22` |
| chấm điểm cho một câu lạc bộ em đã xếp và câu lạc bộ đó có thi | `0.8` |
| số nguyện vọng mỗi buổi | `randint(1, min(3, số CLB buổi đó))` |
| điểm | `uniform(4.0, 10.0)` làm tròn 1 chữ số, ghi bằng **dấu phẩy** thập phân |

#### Ba bất biến của bộ sinh — và lý do có thật ghi trong mã

**1 · Chỉ gán nhóm dự trữ mà có câu lạc bộ thật sự đặt suất cho.**
Gán bừa từ bảng `nhom_du_tru` thì gặp trường hợp không câu lạc bộ nào đặt suất cho
`khoi_10` — lúc đó những em mang nhãn đó có một cái nhãn **không đem lại gì ở bất kỳ
đâu**. Phần mềm gọi đó là "nhóm mồ côi" và cảnh báo mức **cao**, đúng.
*Đo được: trường 3 câu lạc bộ, 40 em → 9 em mang nhãn mồ côi và 2 cảnh báo khi nhập.*

**2 · Mỗi em phải khai ít nhất một nguyện vọng cả tuần.**
Bỏ trống **một** buổi là "ngày đó em bận" — hợp lệ. Bỏ trống **mọi** buổi là "em
không đăng ký gì cả", và phần mềm cảnh báo đúng: em đó chắc chắn trắng tay, không
phải vì thua ai mà vì chưa bao giờ vào cuộc. Ở trường một buổi, xác suất 12% ấy áp
lên cả "tuần", nên không chặn thì cứ 100 em lại có ~12 em như vậy.

**3 · Mỗi nhóm có câu lạc bộ đặt suất thì phải có người.**
Mặt gương của điều 1. Một câu lạc bộ giữ 1 chỗ cho `chinh_sach` mà cả trường không
em nào thuộc diện đó thì chỗ ấy không ai nhận được — phần mềm cảnh báo
`health_club_group_no_students`, đúng. Trường ít học sinh mới gặp: 20 em, mỗi em 22%
có nhóm, bốc ra toàn `khoi_10` là chuyện bình thường.
*Đo được: 1 trên 90 cấu hình đã thử.* Khi chữa, mã **ưu tiên em chưa có nhóm** để
không cướp nhãn của nhóm khác.

#### Cách `ghi_bo` quyết định số cột

| Tệp | Số cột quyết định thế nào |
|---|---|
| `01_danh_sach_CLB.csv` | 5 cột; thêm `buoi` **chỉ khi** có ít nhất một câu lạc bộ khai buổi |
| `02_chon_CLB_muon_thi.csv` | `max(số ô điểm của một em)` cặp cột — **không** phải `5 × số buổi`, vì phần mềm ghép `score_N` với `test_club_N` theo con số |
| `03_xep_hang_nguyen_vong.csv` | nhiều buổi: `<buổi>_pref_1..max` cho **mỗi** buổi; một buổi: `pref_1..max` |

Thứ tự buổi **giữ theo thứ tự xuất hiện** trong danh sách câu lạc bộ, không sắp lại.

### 4.3 · Chín điều phải đúng → chỗ kiểm trong mã

Ánh xạ từng điều trong `SKILL.md` sang chỗ kiểm cụ thể trong `soat()`, để sửa một
quy tắc thì biết sửa ở đâu:

| # | Điều | Dòng | Thông báo lỗi |
|---|---|---|---|
| 1 | mọi `club_id` trong tệp học sinh đều có trong danh sách | 109 | `mã '…' không có trong danh sách câu lạc bộ` |
| 2 | mỗi câu lạc bộ nằm đúng cột buổi của nó | 112 | `… nằm ở cột buổi X nhưng sinh hoạt Y` |
| 3 | không nguyện vọng nào trùng trong cùng một buổi | 103 | `nguyện vọng trùng nhau` |
| 4 | ≤ 10 nguyện vọng mỗi buổi | 105 | `… nguyện vọng, vượt trần 10 mỗi buổi` |
| 5 | ≤ 5 câu lạc bộ dự thi mỗi buổi | 129 | `dự thi … câu lạc bộ, vượt trần 5 mỗi buổi` |
| 6 | `capacity > 0`, `reserve_capacity ≤ capacity`, có dự trữ thì có nhóm | 72–82 | 5 thông báo riêng |
| 7 | chỉ chấm điểm cho câu lạc bộ có thật | 119 | `chấm điểm cho mã '…' không có thật` |
| 8 | chỉ chấm điểm cho câu lạc bộ em **có khai nguyện vọng** | 125 | `dự thi … nhưng không xếp nguyện vọng câu lạc bộ đó` |
| 9 | mã học sinh duy nhất | 93 | `có mã học sinh bị trùng` |

Ngoài chín điều trên, `soat()` còn kiểm hai điều về chính danh sách câu lạc bộ:

| Điều | Dòng |
|---|---|
| mã câu lạc bộ không trùng nhau | 59 |
| khai cột `buoi` thì phải khai cho **mọi** câu lạc bộ | 88 |

Và `canh_bao_men()` in ba loại cảnh báo mềm:

| Cảnh báo | Ngưỡng | Dòng |
|---|---|---|
| buổi chọi quá 3 lần | `số em / số chỗ > 3` | 160 |
| buổi thừa chỗ | `số em < số chỗ × 0.5` | 163 |
| số em không khai nguyện vọng nào cả tuần | > 0 | 167 |

> Trường một buổi mang nhãn rỗng. `canh_bao_men` quy nhãn rỗng về `__mac_dinh__`
> cho **cả hai phía** (câu lạc bộ và nguyện vọng). Ghi chú trong mã giải thích vì
> sao điều đó quan trọng: đổi một phía thôi thì hai bên không còn gặp nhau, và bảng
> cảnh báo nói *"0 em / 69 chỗ"* — một câu vô nghĩa, và **vô nghĩa theo kiểu nghe
> rất thật**.

### 4.4 · Ba lệnh của CLI

```bash
# 1 · Dựng từ bản khai báo JSON tường minh
python .claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py tao \
    --spec truong.json --ra ./bo_moi

# 2 · Dựng một trường ngẫu nhiên nhưng luôn hợp lệ
python .claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py ngau \
    --ra ./bo_moi --hoc-sinh 180 --buoi thu_2,thu_4,thu_6 \
    --clb-moi-buoi 3 --seed 42 --do-choi 1.15

# 3 · Soát một bộ đã có — không sửa gì
python .claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py soat ./bo_moi
```

| Lệnh | Cờ | Mặc định | Ghi chú |
|---|---|---|---|
| `tao` | `--spec` | *bắt buộc* | tệp JSON khai báo |
| | `--ra` | *bắt buộc* | thư mục ra |
| `ngau` | `--ra` | *bắt buộc* | |
| | `--hoc-sinh` | `120` | |
| | `--buoi` | `""` | vd `thu_2,thu_4,thu_6`. **Bỏ trống = trường một buổi** |
| | `--clb-moi-buoi` | `3` | |
| | `--seed` | `42` | |
| | `--do-choi` | `1.15` | |
| `soat` | `thu_muc` | *bắt buộc* | tham số vị trí |

**Mã thoát:** `0` = hợp lệ (đã ghi tệp, nếu là `tao`/`ngau`) · `1` = không hợp lệ,
**không tệp nào được ghi**.

`--do-choi` chỉnh độ chật — `1.15` là tổng chỗ nhiều hơn nhu cầu 15%:

| Giá trị | Hệ quả |
|---|---|
| < 1.0 | **chắc chắn** nhiều em trắng tay |
| ~1.15 | đủ chật để kết quả có nghĩa, đủ rộng để không quá nửa trường trắng tay |
| > 1.5 | gần như ai cũng có chỗ, và **kết quả không nói lên điều gì** |

Nhãn buổi lạ (không nằm trong `BUOI_CHUAN`) **không chặn** — chỉ in một dòng nhắc ra
`stderr` rồi chạy tiếp.

### 4.5 · Bản khai báo JSON cho lệnh `tao`

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

| Khoá | Kiểu | Ghi chú |
|---|---|---|
| `cau_lac_bo[]` | danh sách | đúng sáu khoá như bảng cột ở [Phần 2.6](#26--danh-sách-clb--trường-nhiều-buổi) |
| `hoc_sinh[].nguyen_vong` | `{buổi: [club_id]}` | thứ tự trong danh sách **là** thứ tự ưu tiên |
| `hoc_sinh[].diem` | `{club_id: điểm}` | **chỉ** cho câu lạc bộ em vừa khai nguyện vọng |

Trường một buổi: dùng `""` làm nhãn buổi ở cả hai phía.

### 4.6 · Giới hạn đã đo: `soat` không đọc được bộ MỘT BUỔI

Điều này **đã kiểm chứng bằng cách chạy thật**, và nó quan trọng vì nó làm sai kết
quả theo hướng nghe rất thuyết phục.

**Hiện tượng.** Chạy `soat` trên một bộ một buổi thì mọi ô điểm đều bị báo là lỗi
điều số 8:

```console
$ python .../sinh_du_lieu.py ngau --ra /tmp/mot --hoc-sinh 40 --seed 7
Hợp lệ: 3 câu lạc bộ · 1 buổi · 40 học sinh · 20 ô điểm
   → /tmp/mot/01_danh_sach_CLB.csv
   → /tmp/mot/02_chon_CLB_muon_thi.csv
   → /tmp/mot/03_xep_hang_nguyen_vong.csv

$ python .../sinh_du_lieu.py soat /tmp/mot
KHÔNG HỢP LỆ — 20 lỗi:
   ✗ HS001: dự thi clb_khoahoc nhưng không xếp nguyện vọng câu lạc bộ đó
   ✗ HS002: dự thi clb_khoahoc nhưng không xếp nguyện vọng câu lạc bộ đó
   …
```

Tức là **chính bộ mà kỹ năng vừa sinh ra, và vừa tuyên bố hợp lệ, lại bị bộ soát của
chính nó bác bỏ ngay sau đó.**

**Nguyên nhân.** `doc_bo` nhận cột nguyện vọng bằng phép thử ở dòng 283:

```python
if not k or not v or "_pref_" not in k:
    continue
```

Trường một buổi, `ghi_bo` đặt tên cột là `pref_1`, `pref_2`, … Chuỗi `pref_1`
**không chứa** `_pref_` (nó bắt đầu bằng `pref_`, không có gạch dưới đứng trước):

```python
>>> "_pref_" in "pref_1",  "_pref_" in "thu_2_pref_1"
(False, True)
```

Nên với bộ một buổi, `doc_bo` đọc ra **không nguyện vọng nào**. Sau đó mọi điểm đều
trở thành "điểm cho câu lạc bộ em không khai nguyện vọng" — điều số 8.

**Phạm vi ảnh hưởng.** Chỉ chế độ `soat`. Chế độ `ngau` và `tao` không đi qua
`doc_bo` nên không bị, và **tệp sinh ra hoàn toàn đúng** — đã kiểm bằng cách nạp
thật vào `PipelineAPI`. Đây là lỗi của bộ **đọc lại**, không phải bộ ghi.

Kết quả chạy `soat` trên cả năm bộ có sẵn trong kho (sau khi đổi tên tệp về đúng ba
tên `01_`/`02_`/`03_` mà `soat` yêu cầu):

| Bộ | Số buổi | Kết quả `soat` | Thực chất |
|---|---|---|---|
| `mau_csv/vi_du_day_du` | 3 | ✅ hợp lệ — 9 CLB · 24 em · 33 ô điểm | đúng |
| `du_lieu_test/bo_nhieu_buoi` | 5 | ✅ hợp lệ — 13 CLB · 160 em · 299 ô điểm | đúng |
| `du_lieu_test/bo_sau_buoi` | 6 | ✅ hợp lệ — 17 CLB · 180 em · 331 ô điểm | đúng |
| `du_lieu_test/bo_can_bang` | 6 | ✅ hợp lệ — 24 CLB · 200 em · 608 ô điểm | đúng |
| `du_lieu_test/bo_sach` | **1** | ❌ 560 lỗi | **báo động giả** — bộ này sạch, `tests/test_bo_sach.py` chứng minh |
| `du_lieu_test/vi_du_huong_dan` | **1** | ❌ 19 lỗi | **báo động giả** |

Đúng **560 lỗi** trên `bo_sach` bằng chính **560 ô điểm** của bộ đó, và **19 lỗi**
trên `vi_du_huong_dan` bằng chính **19 ô điểm** — một-đối-một, đúng như chẩn đoán.
`README.md` của `bo_sach` nói rõ bộ ấy dựng để "4 CLB thi luôn là **4 nguyện vọng
đầu**", nên điều số 8 không thể bị vi phạm dù chỉ một lần.

**Cách chữa** (một dòng, chưa áp dụng): ở dòng 283, nhận thêm cột `pref_<số>` trơn và
quy nó về nhãn buổi `""` — đúng nhãn mà `ghi_bo` dùng cho trường một buổi
(`next(iter(nv), "")`, dòng 243).

Đến khi chữa, **đừng tin `soat` trên bộ một buổi**. Phép kiểm đáng tin là nạp thật
vào phần mềm — xem [4.7](#47--luôn-kiểm-bằng-phần-mềm-thật).

### 4.7 · Luôn kiểm bằng phần mềm thật

Soát xong vẫn phải nhập thử. Đây là phép kiểm duy nhất đáng tin, và là phép kiểm mà
`SKILL.md` yêu cầu:

```python
import sys, io, os, tempfile
sys.path.insert(0, "<đường dẫn tới rbda-kiosk>")
from api import PipelineAPI

d = tempfile.mkdtemp()
api = PipelineAPI(os.path.join(d, "app.db"), thu_muc_xuat=d)
for t in ("01_danh_sach_CLB.csv", "02_chon_CLB_muon_thi.csv",
          "03_xep_hang_nguyen_vong.csv"):
    kq = api.import_csv_auto(io.open(os.path.join(BO, t), encoding="utf-8-sig").read())
    assert kq["ok"] and not (kq["data"].get("warnings") or []), (t, kq)
assert api.get_data_health_report()["data"]["n_warnings"] == 0
assert api.run_pipeline(seed=42)["ok"]
```

**Tiêu chuẩn: 0 cảnh báo khi nhập · 0 cảnh báo sức khoẻ dữ liệu · chạy được.**

> Một bộ mẫu mà phần mềm phải kêu là một bộ mẫu **đang dạy người ta làm sai**, và
> người đọc không có cách nào biết cảnh báo đó là cố ý hay là lỗi.

Ba điều cần nhớ khi chạy đoạn trên:

1. Đọc bằng `encoding="utf-8-sig"` — nếu không thì BOM biến `student_id` thành
   `﻿student_id`.
2. Nạp **đúng thứ tự** `01` → `02` → `03`, hoặc để `import_csv_auto` tự nhận diện
   rồi nạp cả ba trong một lần.
3. Dùng cơ sở dữ liệu **trống**. Nạp lên trên dữ liệu cũ thì cảnh báo còn lại là của
   dữ liệu cũ.

---

## Phần 5 · Kiểm kê toàn bộ tài sản dữ liệu

Mọi con số dưới đây **đo lại từ tệp thật** khi viết tài liệu, không chép từ README.
"Dòng" = số dòng dữ liệu, **không** tính dòng tiêu đề.

### 5.1 · `mau_csv/` — tám tệp mẫu định dạng

| Tệp | Kích thước | Dòng | Header |
|---|---|---|---|
| `01_chon_club_thi_dang_rong.csv` | 395 B | 5 | `student_id,name,test_club_1,score_1,…,test_club_4,score_4` |
| `02_chon_club_thi_dang_dai.csv` | 447 B | 11 | `student_id,name,club_id,score` |
| `03_nguyen_vong_dang_rong.csv` | 276 B | 5 | `student_id,name,pref_1,pref_2,pref_3` |
| `04_nguyen_vong_dang_dai.csv` | 397 B | 10 | `student_id,name,club_id,rank` |
| `05_danh_sach_club.csv` | 239 B | 5 | `club_id,name,capacity,reserve_capacity,reserve_group` |
| `06_danh_sach_club_nhieu_buoi.csv` | 309 B | 6 | `club_id,name,capacity,reserve_capacity,reserve_group,buoi` |
| `07_chon_club_thi_nhieu_buoi.csv` | 351 B | 6 | `student_id,name,reserve_group,test_club_1,score_1,test_club_2,score_2` |
| `08_nguyen_vong_nhieu_buoi.csv` | 532 B | 6 | `student_id,name,reserve_group,thu_2_pref_1,thu_2_pref_2,thu_4_pref_1,thu_4_pref_2,thu_6_pref_1,thu_6_pref_2` |

Giao diện **không** nhận các tệp trên nữa: nó chỉ nhận **Sổ nhập CLB**, một tệp
Excel hai trang (định nghĩa: `so_nhap.py`, hướng dẫn: `mau_csv/HUONG_DAN_SO_NHAP.md`).
Các sổ sinh bằng `mau_csv/tao_so_nhap.py`, phần lớn từ chính các bộ CSV:

| Sổ | Nội dung |
|---|---|
| `mau_csv/SO_NHAP_CLB.xlsx` | Sổ trống phát cho trường |
| `mau_csv/vi_du_day_du/SO_NHAP_CLB_vi_du.xlsx` | 3 buổi · 9 CLB · 24 học sinh |
| `mau_csv/vi_du_ca_tuan/SO_NHAP_CLB_vi_du.xlsx` | 6 buổi · 18 CLB · 60 học sinh |
| `du_lieu_test/vi_du_huong_dan/SO_NHAP_VIDU.xlsx` | 10 học sinh của sách hướng dẫn |
| `du_lieu_test/bo_sach/SO_NHAP_SACH.xlsx` | 140 học sinh, 0 cảnh báo |
| `du_lieu_test/SO_NHAP_TEST.xlsx` | 120 học sinh, cạnh tranh cao (bản sổ của `TEST_01–03`) |
| `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx` | Cố ý sai 5 chỗ, để xem bảng lỗi của màn hình nạp |

`tests/test_so_nhap.py` canh: nạp sổ và nạp bộ ba tệp cũ ra **cùng một CSDL**.

Tài liệu đi kèm: `mau_csv/HUONG_DAN_CSV.md` — **bản chính** của đặc tả ba bảng
nội bộ.

> ⚠️ Tám tệp `0*.csv` phẳng này **không có BOM**, khác với mọi CSV còn lại trong kho.
> Chúng là tệp mẫu tối giản để đọc bằng mắt, không phải tệp để mở bằng Excel.

### 5.2 · `mau_csv/vi_du_day_du/` — một trường hoàn chỉnh

Bộ để mở ra đầu tiên khi muốn biết tệp đầu vào trông thế nào. **3 buổi · 9 câu lạc
bộ · 45 chỗ · 24 học sinh · 33 ô điểm.** Suất dự trữ: 5 chỗ ở 3 câu lạc bộ. Nhóm:
`chinh_sach`, `khoi_10` — cả hai đều có câu lạc bộ nhận **và** có học sinh mang.

| Tệp | Kích thước | Dòng | Header |
|---|---|---|---|
| `01_danh_sach_CLB.csv` | 434 B | 9 | `club_id,name,capacity,reserve_capacity,reserve_group,buoi` |
| `02_chon_CLB_muon_thi.csv` | 1 439 B | 24 | `student_id,name,reserve_group,test_club_1,score_1,test_club_2,score_2,test_club_3,score_3` |
| `03_xep_hang_nguyen_vong.csv` | 2 050 B | 24 | `student_id,name,reserve_group,thu_2_pref_1,thu_2_pref_2,thu_4_pref_1,thu_4_pref_2,thu_6_pref_1,thu_6_pref_2` |

Buổi: `thu_2` `thu_4` `thu_6`. Điểm ghi bằng **dấu phẩy thập phân trong ngoặc kép**
(`"9,5"`) — đúng cách Excel bản tiếng Việt lưu.

Đi kèm: `GIAI_THICH.md` (11 070 B · 217 dòng) giải thích từng cột từng dòng, và
`tao_bo_mau.py` (9 673 B) đọc **một bảng khai báo duy nhất** rồi phát ra cả ba tệp,
nên ba tệp không thể lệch nhau. Bộ sinh này **tất định, không dùng `random`**.

### 5.3 · `du_lieu_test/` gốc — bộ cạnh tranh cao + bộ demo

| Tệp | Kích thước | Nội dung | Dùng để |
|---|---|---|---|
| `TEST_01_danh_sach_CLB.xlsx` | 6 610 B | 10 CLB, tổng 130 suất, 4 CLB có suất dự trữ | nạp **đầu tiên** |
| `TEST_02_chon_CLB_muon_thi.xlsx` | 14 111 B | 120 em, mỗi em thi 2–5 CLB, **kèm sẵn 396 ô điểm** | nạp thứ hai |
| `TEST_03_xep_hang_nguyen_vong.xlsx` | 11 355 B | cùng 120 em, mỗi em 2–5 nguyện vọng | nạp thứ ba |
| `TEST_04_CO_LOI_CO_Y.xlsx` | 7 168 B | 10 dòng, **cố ý sai 6 chỗ** | kiểm phần mềm **có** cảnh báo không — [Phần 6](#phần-6--test_04_co_loi_co_yxlsx--sáu-lỗi-cài-sẵn) |
| `app_DEMO_da_cham_diem.db` | 147 456 B | CSDL dựng sẵn tới ngay trước bước cuối: đã nạp, đã chấm điểm, **0 cảnh báo** | demo |

Mỗi tệp `.xlsx` có sheet **"Ghi chú"** giải thích nội dung ngay trong tệp.

Bộ này **cố ý thiết kế cho cạnh tranh cao** để cơ chế thuật toán lộ ra. Sinh lại
bằng `tao_du_lieu_test.py` (13 409 B), hạt giống `SEED = 2026`.

> `app_DEMO_da_cham_diem.db` **cố ý chưa chạy phân bổ sẵn.** Phần đáng xem nhất là
> lúc thuật toán chạy và kết quả hiện ra — dựng sẵn cả phần đó thì không còn gì để
> cho xem.
>
> Cách dùng hôm demo: đóng app → đổi tên `app.db` đang có thành `app_cua_toi.db`
> *(đừng xoá — đó là dữ liệu của bạn)* → chép tệp demo vào cạnh
> `PhanBoCauLacBo.exe`, đổi tên thành `app.db` → mở app → **Chạy phân bổ** →
> **Xuất kết quả**.

Đường thử thứ hai, không qua tệp: `NHAP_TAY.md` (5 993 B · 128 dòng) — kịch bản gõ
tay 8 học sinh, 3 câu lạc bộ, ~15 phút. Kiểm các màn hình *Quản lý club*, *Nhập dự
phòng tại kiosk*, *Chấm điểm* — những màn hình mà đường nạp tệp **không** đụng tới.
Bộ này nhỏ đủ để tự tính kết quả bằng tay rồi đối chiếu với máy.

### 5.4 · `du_lieu_test/bo_sach/` — bộ sạch, MỘT BUỔI

Bộ tồn tại vì đúng một lời hứa: **nạp vào không một cảnh báo nào**, để người chạy
thử biết mọi cảnh báo nhìn thấy đều là do dữ liệu của họ. Khác thư mục cha ở chỗ
**không chứa tệp lỗi nào**.

**12 câu lạc bộ · 150 chỗ cho 140 em · 140 học sinh · 560 ô điểm.** Suất dự trữ: 16
chỗ ở 4 câu lạc bộ. Hạt giống `SEED = 9090`.

| Tệp | Kích thước | Dòng | Header |
|---|---|---|---|
| `SACH_01_danh_sach_CLB.csv` | 501 B | 12 | `club_id,name,capacity,reserve_capacity,reserve_group` |
| `SACH_02_chon_CLB_muon_thi.csv` | 12 801 B | 140 | `student_id,name,reserve_group,test_club_1,score_1,…,test_club_4,score_4` |
| `SACH_03_xep_hang_nguyen_vong.csv` | 13 995 B | 140 | `student_id,name,reserve_group,pref_1,pref_2,pref_3,pref_4,pref_5,pref_6` |

**Không có cột `buoi`** — đây là bộ một buổi duy nhất trong nhóm `bo_*`. Mỗi em thi
**đúng 4** câu lạc bộ và xếp **6** nguyện vọng; 4 câu lạc bộ thi luôn là **4 nguyện
vọng đầu**.

Có cả bản `.xlsx`: `SACH_01` 6 732 B · `SACH_02` 14 690 B · `SACH_03` 12 846 B. Đã
đối chiếu: **hai đường vào cho ra kết quả xếp lớp giống hệt nhau.**

Phần *Cảnh báo dữ liệu* có 7 quy tắc rà soát; bộ này dựng để không vi phạm quy tắc nào:

| Quy tắc rà soát | Bộ này tránh bằng cách |
|---|---|
| CLB có người thi mà chưa chấm điểm | mọi lượt thi đều có điểm sẵn trong `SACH_02` |
| Thi CLB mà không xếp nguyện vọng CLB đó | 4 CLB thi luôn là 4 nguyện vọng đầu |
| Học sinh chưa xếp nguyện vọng nào | em nào cũng có đủ 6 |
| Nhãn dự trữ không CLB nào nhận | chỉ dùng `chinh_sach` và `khoi_10`, cả hai đều có CLB nhận |
| CLB có suất dự trữ mà quên đặt nhãn | 4 CLB có suất đều đã ghi nhãn |
| CLB dành suất cho nhãn chưa em nào mang | cả hai nhãn đều có học sinh mang |
| Tổng chỗ ít hơn số học sinh | 150 suất > 140 em |

> ⚠️ **Phải nạp vào CSDL trống.** Đã đo: nạp cả bộ `TEST_01..04` rồi chồng bộ sạch
> lên → CSDL có **148** em, còn **1 cảnh báo nghiêm trọng**, và chạy phân bổ ra
> **143/148** chứ không phải 140/140.
>
> Cách dọn trong chính phần mềm: tab **Quản lý** → cuối trang, khối **Vùng nguy
> hiểm** → **"Xoá toàn bộ học sinh (giữ CLB)"** → bấm lần nữa để xác nhận. Phần mềm
> **tự sao lưu `app.db`** trước khi xoá và báo tên tệp sao lưu, nên không mất gì;
> nhật ký `run_history` cũng được giữ.

### 5.5 · `du_lieu_test/bo_nhieu_buoi/` — 5 buổi

Bộ để thử tính năng thời khoá biểu tuần. **13 câu lạc bộ · 215 chỗ · 160 học sinh ·
299 ô điểm.** Suất dự trữ: 19 chỗ ở 6 câu lạc bộ. Hạt giống `HAT = 7788`.

| Tệp | Kích thước | Dòng | Header |
|---|---|---|---|
| `NHIEUBUOI_01_danh_sach_CLB.csv` | 639 B | 13 | `club_id,name,capacity,reserve_capacity,reserve_group,buoi` |
| `NHIEUBUOI_02_chon_CLB_muon_thi.csv` | 10 022 B | 160 | `student_id,name,reserve_group,test_club_1,score_1,…,test_club_4,score_4` |
| `NHIEUBUOI_03_xep_hang_nguyen_vong.csv` | 17 616 B | 160 | `…,thu_2_pref_1..3,thu_3_pref_1..3,thu_4_pref_1..2,thu_5_pref_1..2,thu_6_pref_1..3` |

Buổi: `thu_2` `thu_3` `thu_4` `thu_5` `thu_6`. Số cột nguyện vọng **khác nhau theo
buổi** (3/3/2/2/3) — minh hoạ đúng điều "số đếm lại từ 1 ở mỗi buổi".

Chọi cao ở giữa tuần — `soat` báo hai cảnh báo mềm: `thu_4` chọi **5,1 lần**
(132 em / 26 chỗ), `thu_5` chọi **3,9 lần** (121 em / 31 chỗ).

### 5.6 · `du_lieu_test/bo_sau_buoi/` — 6 buổi, tới Thứ Bảy

**17 câu lạc bộ · 279 chỗ · 180 học sinh · 331 ô điểm.** Suất dự trữ: 21 chỗ ở 7 câu
lạc bộ. Hạt giống `HAT = 20260912`.

| Tệp | Kích thước | Dòng |
|---|---|---|
| `SAUBUOI_01_danh_sach_CLB.csv` | 820 B | 17 |
| `SAUBUOI_02_chon_CLB_muon_thi.csv` | 11 310 B | 180 |
| `SAUBUOI_03_xep_hang_nguyen_vong.csv` | 24 731 B | 180 |

Buổi: `thu_2` … `thu_7`. Cột nguyện vọng: 3/3/3/3/3/2.
`soat` báo ba cảnh báo mềm: `thu_3` chọi 3,0 lần · `thu_4` chọi 3,8 lần · `thu_5`
chọi 3,2 lần.

### 5.7 · `du_lieu_test/bo_can_bang/` — 6 buổi theo hình dáng một trường có thật

Bộ lớn nhất. **24 câu lạc bộ · 574 chỗ · 200 học sinh · 608 ô điểm.** Suất dự trữ: 30
chỗ ở 7 câu lạc bộ. Hạt giống `HAT = 31415`.

| Tệp | Kích thước | Dòng |
|---|---|---|
| `CANBANG_01_danh_sach_CLB.csv` | 1 101 B | 24 |
| `CANBANG_02_chon_CLB_muon_thi.csv` | 16 529 B | 200 |
| `CANBANG_03_xep_hang_nguyen_vong.csv` | 34 711 B | 200 |

Buổi: `thu_2` … `thu_7`, **4 cột nguyện vọng cho mỗi buổi** (24 cột `*_pref_*`) và
**6 cặp cột dự thi** — bộ có bề ngang lớn nhất trong kho.

Khác ba bộ trên ở chỗ **cố ý cân bằng**: thay vì dồn chọi vào giữa tuần, nó rải đều
để giống một trường thật hơn. Đổi lại, `soat` báo một cảnh báo mềm khác:
**15 em không khai nguyện vọng nào cả tuần** — các em đó chắc chắn trắng tay. Đó là
dữ liệu cố ý, dùng để xem phần mềm có cảnh báo đúng không.

### 5.8 · `du_lieu_test/vi_du_huong_dan/` — bộ nhỏ in trong sách hướng dẫn

**4 câu lạc bộ · 10 chỗ · 10 học sinh · 19 ô điểm · một buổi.** Suất dự trữ: 1 chỗ ở
1 câu lạc bộ, nhóm `chinh_sach`. Bộ sinh `tao_vi_du.py` (7 432 B) **tất định, không
dùng `random`** — mọi giá trị viết thẳng trong hai bảng `CLB` và `HOC_SINH`.

| Tệp | Kích thước | Dòng | Header |
|---|---|---|---|
| `VIDU_01_danh_sach_CLB.csv` | 195 B | 4 | `club_id,name,capacity,reserve_capacity,reserve_group` |
| `VIDU_02_chon_CLB_muon_thi.csv` | 619 B | 10 | `student_id,name,reserve_group,test_club_1,score_1,test_club_2,score_2` |
| `VIDU_03_xep_hang_nguyen_vong.csv` | 516 B | 10 | `student_id,name,reserve_group,pref_1,pref_2` |

Có cả bản `.xlsx`: 6 396 B · 6 729 B · 6 486 B.

`HUONG_DAN_SU_DUNG.md` **in nguyên bảng kết quả của bộ này** rồi bảo người đọc "ra
khác bảng này là có gì đó đã đổi". Lời hứa đó do `tests/test_vi_du_huong_dan.py` canh.

### 5.9 · `du_lieu_test/thu_tai/` — bộ đo tải

Không phải bộ dữ liệu nạp được: đây là bộ **sinh dữ liệu theo tham số** để đo giới
hạn phần mềm.

| Tệp | Việc |
|---|---|
| `doi_chung.py` | **Chạy trước mọi thứ khác.** Bắt bộ đo đo lại bộ 120 em thật — thứ đã biết kết quả (108/120, 7 vòng). Lệch nghĩa là bộ đo hỏng, và mọi con số quy mô lớn sau đó đều vô nghĩa dù nhìn rất thuyết phục |
| `chay_thu_tai.py` | lưới quét, ~15 phút |
| `do_csdl.py` | tầng CSDL ở quy mô lớn — và chỉ mục giúp được bao nhiêu |
| `do_giao_dien.py` | tầng giao diện: bảng Kết quả vẽ bao lâu khi có nhiều học sinh |
| `kiem_on_dinh.py` | ở quy mô lớn, kết quả có còn **đúng** không — không chỉ nhanh |
| `thu_nghich_canh.py` | thử nghịch cảnh |
| `lam_bao_cao.py` | dựng `bao_cao_thu_tai.html` từ `ket_qua_thu_tai.csv` |

Lưới quét: học sinh 200 · 500 · 1 000 · 2 000 · 5 000 × câu lạc bộ 10 · 25 · 50 · 100
× nguyện vọng mỗi em 3 · 5 · 10 × tổng chỉ tiêu 100% và 108% × cách chia chỉ tiêu
`chia_deu` / `theo_nhu_cau`. **Số câu lạc bộ dự thi giữ cố định ở 4.**

Kết quả: `ket_qua_thu_tai.csv` · 17 332 B · **204 dòng** · 18 cột:

```csv
hoc_sinh,so_clb,nguyen_vong,ty_le_cho,cach_chia_chi_tieu,clb_du_thi,t_nap_giay,t_phan_bo_giay,t_xuat_giay,so_vong,xep_duoc,ty_le_xep,chua_xep,xep_nho_co_diem,xep_chi_nho_boc_tham,db_MB,dinh_bo_nho_MB,so_tep_xuat
```


| Cột | Ý nghĩa |
|---|---|
| `hoc_sinh` · `so_clb` · `nguyen_vong` · `ty_le_cho` | tham số đầu vào của ô lưới |
| `cach_chia_chi_tieu` | `chia_deu` (giống trường thật) hoặc `theo_nhu_cau` (dễ nhất) |
| `clb_du_thi` | luôn 4 |
| `t_nap_giay` · `t_phan_bo_giay` · `t_xuat_giay` | thời gian ba bước |
| `so_vong` | số vòng lặp thuật toán chạy |
| `xep_duoc` · `ty_le_xep` · `chua_xep` | kết quả xếp chỗ |
| `xep_nho_co_diem` | được xếp vào CLB mình **có dự thi** (Tầng 1) |
| `xep_chi_nho_boc_tham` | được xếp vào CLB mình **không dự thi** — chỉ nhờ bốc thăm (Tầng 2) |
| `db_MB` · `dinh_bo_nho_MB` | dung lượng CSDL và đỉnh bộ nhớ Python |
| `so_tep_xuat` | số tệp kết quả xuất ra |

Tệp này được **giữ lại có chủ ý**: `.gitignore` dòng 26 có `!du_lieu_test/thu_tai/ket_qua_thu_tai.csv`.

Nhu cầu sinh theo **trọng số Zipf**: câu lạc bộ thứ *i* hút khoảng `1/i` — đúng hình
dạng của bộ 120 em đã đo được.

### 5.10 · `du_lieu_test/do_*.py` — mười một script đo

Mỗi script trả lời một câu hỏi về thuật toán bằng **số**, không bằng lập luận.

| Script | Câu hỏi |
|---|---|
| `do_boc_tham.py` (42 378 B — lớn nhất) | bốc thăm ảnh hưởng kết quả ra sao |
| `do_cau_hoi_boc_tham.py` | ba câu hỏi hay bị hỏi nhất về bốc thăm |
| `do_anh_huong_seed.py` | đổi seed thì **thực tế** bao nhiêu em đổi chỗ |
| `do_ben_vung.py` | độ bền vững của kết quả |
| `do_danh_doi_on_dinh.py` | cái giá của tính ổn định |
| `do_toi_uu_on_dinh.py` | thuật toán có đưa ra cặp ghép tốt nhất không |
| `do_do_dai_nguyen_vong.py` | danh sách nguyện vọng ngắn thì thiệt tới đâu |
| `do_hai_canh_du_tru.py` | hai mặt của cơ chế dự trữ |
| `do_khong_du_tru.py` | bỏ hẳn cơ chế dự trữ thì sao |
| `do_khai_that.py` | khai thật có lợi hơn khai chiến thuật không |
| `co_che_doi_chung.py` | thí nghiệm đối chứng cho cơ chế |

Kết quả đã chốt nằm trong bốn tệp JSON: `so_lieu_boc_tham.json`,
`so_lieu_ben_vung.json`, `so_lieu_toi_uu.json`, `so_lieu_khai_that.json`. Các test
canh số đo đọc chính bốn tệp này và **tự bỏ qua** nếu phép đo chưa chạy.

Diễn giải đầy đủ: `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` (25 785 B · 492 dòng).

---

## Phần 6 · `TEST_04_CO_LOI_CO_Y.xlsx` — sáu lỗi cài sẵn

Tệp này **cố ý sai**. Nó tồn tại để trả lời một câu hỏi mà bộ dữ liệu sạch không trả
lời được: *phần mềm có thật sự kêu khi dữ liệu sai không?*

Cách chạy: nạp `TEST_01` trước, rồi nạp `TEST_04`. Phần mềm **phải** hiện đủ **6
cảnh báo**:

| # | Lỗi cài sẵn | Cảnh báo phải hiện |
|---|---|---|
| 1 | `HS202` xuất hiện hai dòng | mã xuất hiện 2 lần, chỉ giữ dòng cuối |
| 2 | `hs201` vs `HS201` | đang coi là hai học sinh khác nhau |
| 3 | nhóm dự trữ `chinh_sac` (thiếu chữ h) | không CLB nào nhận, gợi ý `chinh_sach` |
| 4 | nguyện vọng vào `clb_khong_co` | club không tồn tại, bỏ qua học sinh này |
| 5 | mã `12348` giữa các mã 7 chữ số | nghi Excel đã cắt mất số 0 đầu |
| 6 | cột `score_1` đặt trong tệp nguyện vọng | điểm ở đây **KHÔNG** được nạp |

> **Thiếu bất kỳ cảnh báo nào là lỗi của phần mềm** — chụp màn hình và báo lại.

Hai điều dễ hiểu lầm:

1. **Thả `TEST_04` cùng lúc với ba tệp kia là phần mềm kêu** — đúng như thiết kế,
   không phải phần mềm hỏng. Muốn chạy thử một đường sạch thì dùng
   `du_lieu_test/bo_sach/`, thư mục đó không có tệp lỗi nào.
2. **Phải đổi tên `app.db` cũ đi trước khi nạp bộ sạch.** Phần mềm *cộng thêm* học
   sinh chứ không xoá em cũ, nên `HS204` của `TEST_04` sẽ còn kêu mãi — xem
   [5.4](#54--du_lieu_testbo_sach--bộ-sạch-một-buổi) để biết cách dọn.

---

## Phần 7 · Kết quả đúng đã kiểm chứng

Ra khác các bảng dưới đây nghĩa là **có gì đó đã đổi** — đó là toàn bộ công dụng của
phần này.

### 7.1 · `TEST_01–03` — bộ cạnh tranh cao, `seed = 42`

Không cần chấm điểm: điểm nằm sẵn ở cột `score_*` trong `TEST_02`, nạp xong là bảng
*Cảnh báo dữ liệu* phải hiện **0 cảnh báo**.

| | |
|---|---|
| Được xếp | **108 / 120** — 12 em vào `_chua_duoc_xep.csv` |
| Nguyện vọng 1 | 64 em (59%) · NV2: 28 · NV3: 10 · NV4: 6 |
| Vào bằng **suất dự trữ** | **10 em** |
| CLB đầy chỗ | Bóng đá 20/20 · Tiếng Anh 16/16 · Mỹ thuật 12/12 · Tin học 12/12 |
| CLB thừa nhiều chỗ | Tình nguyện 5/12 · Khoa học 2/8 · Bóng rổ 13/18 |
| Tệp xuất ra | 120 dòng trong tệp tổng, 11 tệp theo CLB |

Ba điều bảng trên cho thấy:

- **41% số em được xếp KHÔNG vào nguyện vọng 1** — thuật toán thực sự phải đẩy người
  xuống nguyện vọng sau, không phải ai muốn gì được nấy.
- **10 em vào bằng suất dự trữ** — bỏ cơ chế dự trữ thì 10 em này mất chỗ vào tay các
  em điểm cao hơn.
- **Có CLB thừa 7 chỗ trong khi 12 em không có CLB nào** — thuật toán không nhét học
  sinh vào CLB họ không chọn.

### 7.2 · `bo_sach` — `seed = 42`, sinh bằng `SEED = 9090`

| | |
|---|---|
| Cảnh báo lúc nạp | **0** — với điều kiện nạp vào CSDL trống |
| Cảnh báo dữ liệu | **0** |
| Được xếp | **140 / 140** — không em nào vào `_chua_duoc_xep.csv` |
| Số vòng chạy | 11 |
| Nguyện vọng 1 | 54 em · NV2: 46 · NV3: 21 · NV4: 11 · NV5: 7 · NV6: 1 |
| Vào bằng **suất dự trữ** | **16 em** (Tier `reserve`); 124 em Tier `general` |
| CLB đầy chỗ | 9 / 12 |
| CLB còn chỗ | Khoa học 5/10 · Tình nguyện 7/10 · Robotics 8/10 |
| Cặp chặn (blocking pair) | **0** — kết quả ổn định |
| Tệp xuất ra | 140 dòng ở tệp tổng, 12 tệp theo CLB |

**Vì sao xếp được 100% mà vẫn không tầm thường.** Mỗi em xếp 6 nguyện vọng nhưng chỉ
thi 4 câu lạc bộ đầu. Hai nguyện vọng cuối rơi vào nhóm câu lạc bộ còn dư chỗ — đó là
**đường lui**, và là lý do không em nào trắng tay. Nhưng hai nguyện vọng cuối em
**không thi**, nên không có điểm; phần mềm vẫn xét, chỉ là ở **Tầng 2**: chọi nhau
bằng số bốc thăm STB chứ không bằng điểm. Nhờ vậy một bộ dữ liệu duy nhất cho thấy
**cả hai tầng ưu tiên** cùng lúc.

### 7.3 · `vi_du_day_du` — `seed = 42`

| Buổi | Câu lạc bộ | Đã xếp / sức chứa | Trong đó diện dự trữ |
|---|---|---|---|
| thu_2 | clb_bongro | 6 / 6 | — |
| thu_2 | clb_vanhoc | 5 / 5 | 2 |
| thu_2 | clb_tinhoc | 4 / 4 | — |
| thu_4 | clb_mythuat | 5 / 5 | 1 |
| thu_4 | clb_robotics | 4 / 4 | — |
| thu_4 | clb_nauan | 6 / 6 | — |
| thu_6 | clb_tienganh | 5 / 5 | 2 |
| thu_6 | clb_lamvuon | 6 / 6 | — |
| thu_6 | clb_covua | 4 / 4 | — |

Mọi câu lạc bộ lấp đầy đúng sức chứa, và **cả năm suất dự trữ đều có người dùng**.

**Độ phủ:** 1 em không có câu lạc bộ nào · 7 em có 1 · 10 em có 2 · 6 em có 3. Trung
bình **1,88** câu lạc bộ mỗi em.

**Một em vẫn trắng tay — và đó là điều nên đọc kỹ.** `HS013 · Đặng Gia Phúc`, diện
`chinh_sach`, khai đủ năm nguyện vọng và có dự thi, nhưng không vào được câu lạc bộ
nào. Lý do rõ nhất nằm ở `clb_tienganh`: **10 em dự thi, 5 chỗ**, và điểm của HS013 là
**6,0 — đứng thứ chín trên mười**. Ở bốn câu lạc bộ còn lại em ấy thua ở bốc thăm hoặc
thua những em có quyền ưu tiên mạnh hơn tại chính câu lạc bộ đó.

> **Bài học cho người vận hành:** thuộc diện dự trữ **không phải** một lời bảo đảm có
> chỗ. Suất dự trữ là một cái **sàn** — nó bảo đảm nhóm đó không bị ép xuống dưới một
> mức, chứ không bảo đảm từng cá nhân trong nhóm.

### 7.4 · Kịch bản nhập tay

8 học sinh · 3 câu lạc bộ · gõ trong ~15 phút. Kết quả **tính được bằng tay** rồi đối
chiếu với máy, nên không phụ thuộc may rủi. Chi tiết từng bước và bảng kết quả:
`du_lieu_test/NHAP_TAY.md`. Canh bởi `tests/test_kich_ban_nhap_tay.py`.

### 7.5 · Bộ đo — đọc ở đâu

`du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` chứa những phần không thuộc luồng nhập dữ
liệu nhưng cần khi phải trả lời câu hỏi về thuật toán:

| Mục | Nội dung |
|---|---|
| 1 | quy mô bài toán |
| 2 | kết quả phân bổ, lấp đầy từng CLB |
| 3 · 3b | tốc độ ở quy mô lớn, thử tải |
| 3c | ảnh hưởng của seed bốc thăm — seed có đổi được việc một em **có suất** hay không |
| 3d | cái giá của tính ổn định; quét 40 seed; thí nghiệm đối chứng |
| 3e | thuật toán có đưa ra cặp ghép **tốt nhất** không |
| 3f | ba thiết kế bốc thăm cho thời khoá biểu tuần |
| 4 | kịch bản nhỏ kiểm được bằng tay |
| 5 · 6 · 7 | kiểm thử phần mềm; lỗi tìm được khi phát triển; chạy trên Windows thật |

---

## Phần 8 · Đường nhập dữ liệu trong mã

### 8.1 · Dòng chảy, theo đúng thứ tự

| Bước | Ở đâu | Việc |
|---|---|---|
| 1 | `app.js` — ô kéo-thả | `.csv` đọc bằng `readAsText(file, "UTF-8")`; `.xlsx` đọc thành base64 |
| 2 | `xlsx_to_csv_text(file_base64, sheet_name="")` — `api.py:1277` | Excel → văn bản CSV; `_o_excel_thanh_chu` chuẩn hoá từng ô |
| 3 | `_parse_csv_rows(csv_text)` — `api.py:1196` | gỡ BOM, đoán dấu phân cách, hạ chữ thường tên cột |
| 4 | `detect_csv_kind(csv_text)` — `api.py:1336` | nhận diện loại tệp từ dòng tiêu đề |
| 5 | `import_csv_auto(csv_text, kind="", create_missing_students=True)` — `api.py:1382` | điều phối |
| 6 | `import_clubs_csv` `1419` · `import_preferences_csv` `1863` · `import_test_selection_csv` `2063` | nhập thật, áp hai trần |
| 7 | `validate_data_integrity(...)` — `rbda_priority_pipeline.py:966` | kiểm toàn vẹn |
| 8 | `get_data_health_report()` — `api.py:325` | 7 quy tắc rà soát trước khi chạy |
| 9 | `run_full_pipeline(db_path, seed, output_csv_path)` — `rbda_priority_pipeline.py:1522` | chạy phân bổ |
| 10 | `export_csv(output_path="")` — `api.py:3221` · `_xuat_match_results_csv` `648` | xuất kết quả |

Xem trước khi nhập thật: `preview_import_csv(csv_text, kind)` — `api.py:1520`.

### 8.2 · Thứ tự quyết định của `detect_csv_kind`

Trả về `{kind, format, confident, candidates, fieldnames}`. Thứ tự **có chủ ý**, và
ghi chú trong mã giải thích từng chỗ:

| # | Điều kiện | Kết luận |
|---|---|---|
| 1 | `capacity` **và** `club_id` có trong cột | `clubs` — `capacity` chỉ có nghĩa với tệp danh sách CLB |
| 2 | có cột nào bắt đầu bằng `pref_` | `preferences` / `wide` |
| 3 | khớp `_cot_nguyen_vong_theo_buoi(fieldnames)` | `preferences` / `wide_theo_buoi` |
| 4 | có cột nào bắt đầu bằng `test_club_` | `test_selection` / `wide` |
| 5 | `rank` **và** `club_id` **và** `student_id` | `preferences` / `long` — `rank` chỉ có nghĩa với nguyện vọng |
| 6 | `student_id` **và** `club_id`, không gì khác | **`confident: False`**, `candidates: ["test_selection", "preferences"]` |
| 7 | không khớp gì | `unknown`, `confident: False` |

Hai điều tinh tế trong thứ tự này, ghi rõ trong mã:

- Bước 3 phải xét **sau** bước 2, để một tệp có cả hai kiểu cột vẫn vào nhánh cũ.
- Bước 3 phải xét **trước** bước 4, vì một tên buổi có thể tình cờ bắt đầu bằng `test`.

**Khi không chắc thì phần mềm không đoán.** `import_csv_auto` trả lỗi
`csv_kind_ambiguous` kèm hai ứng viên, và giao diện hỏi lại người dùng. Ghi chú trong
mã nói thẳng lý do: *"Thà không nhập còn hơn nhập vào sai bảng."*

### 8.3 · Mã lỗi `validate_data_integrity` trả về

Hàm này **không raise exception** — nó trả về danh sách `{"code", "params"}` để
pipeline báo cáo **toàn bộ** lỗi một lần thay vì dừng ở lỗi đầu.

| Mã | Nghĩa |
|---|---|
| `pref_student_not_in_students` | có nguyện vọng của một mã học sinh không tồn tại |
| `pref_duplicate_club` | nguyện vọng trùng câu lạc bộ |
| `pref_too_many` | quá 10 nguyện vọng — **trường một buổi** |
| `pref_too_many_buoi` | quá 10 nguyện vọng ở một buổi — **trường nhiều buổi**, nêu tên buổi |
| `pref_unknown_club` | nguyện vọng vào câu lạc bộ không có thật |
| `club_capacity_not_positive` | `capacity ≤ 0` |
| `club_reserve_exceeds_capacity` | `reserve_capacity > capacity` |

> Vì sao **hai** mã cho cùng một trần: trường một buổi mang nhãn buổi
> `BUOI_MAC_DINH` — một chuỗi **nội bộ**, không phải thứ đọc lên được. Nêu nó ra là
> bắt người dùng đọc một khái niệm trường họ không có. Hai mã vì thế, và trường một
> buổi thấy đúng câu như bản cũ.
>
> Còn vì sao lỗi quá trần phải **nêu tên buổi**: câu *"em này quá nhiều nguyện vọng"*
> mà không nói buổi nào thì trường không biết sửa ở đâu.

### 8.4 · Mã cảnh báo sức khoẻ dữ liệu

Những khoảng trống **hợp lệ** — `validate_data_integrity` cho qua, pipeline chạy
được — nhưng âm thầm đổi việc ai vào câu lạc bộ nào. Định nghĩa trong `i18n_errors.py`:

| Mã | Nghĩa |
|---|---|
| `csv_reserve_group_unknown` | nhãn dự trữ không câu lạc bộ nào nhận — báo **ngay khi nạp**, kèm gợi ý sửa |
| `health_orphan_student_group` | học sinh mang nhãn mồ côi |
| `health_student_no_preferences` | học sinh chưa xếp nguyện vọng nào |
| `health_club_group_no_students` | câu lạc bộ dành suất cho nhãn chưa em nào mang |

`i18n_errors.py` giữ `err()` và `format_message()` cùng toàn bộ mã thông báo —
`api.py` và `rbda_priority_pipeline.py` chỉ phát ra mã, chuỗi văn bản dịch ở một chỗ.

### 8.5 · Các hàm chuẩn hoá

| Hàm | Ở đâu | Việc |
|---|---|---|
| `chuan_hoa_nhom_du_tru(raw)` | `api.py:1573` | `Chính sách` → `chinh_sach` |
| `_doc_diem(chuoi)` | `api.py:1602` | đọc `9,5` và `9.5` như nhau |
| `_buoi_qua_tran(cur, ds_clb, tran)` | `api.py:1791` | tìm buổi vượt trần |
| `_cot_nguyen_vong_theo_buoi(fieldnames)` | `api.py:1846` | nhận khuôn `<buổi>_pref_<số>` |
| `chuan_hoa_buoi(raw)` | `api.py:3577` | quy mọi cách viết nhãn buổi về một |
| `gom_theo_buoi(prefs, clubs)` | `rbda_priority_pipeline.py:92` | nhóm nguyện vọng theo buổi |
| `_o_excel_thanh_chu` | `api.py` ~1246 | `20.0` → `20`; không có bước này thì `ValueError` và **mất dòng câu lạc bộ đó** |

---

## Phần 9 · Test nào canh bộ nào

### 9.1 · Khung và cấu hình

**pytest.** `requirements-dev.txt` khai `pytest>=8.0`; `playwright>=1.40` (test giao
diện bằng Chromium thật) và `pillow>=10.0` (test biểu tượng) là **tuỳ chọn**, bọc bằng
`importorskip` nên máy thiếu chúng vẫn chạy được phần còn lại.

Không có `pytest.ini`, `pyproject.toml` hay `setup.cfg`. Toàn bộ cấu hình nằm ở
`tests/conftest.py`, gồm ba fixture:

| Fixture | Việc |
|---|---|
| `api` | một `PipelineAPI` trên `tmp_path/app.db` |
| `api_factory` | dựng **nhiều** `PipelineAPI` độc lập trong cùng một test — cần cho test quét nhiều seed: mỗi seed phải chạy trên CSDL sạch, nếu không dữ liệu lần trước làm lệch kết quả |
| `khong_ghi_vao_thu_muc_tai_ve_that` | **autouse.** Ghim `RBDA_THU_MUC_TAI_VE` vào thư mục tạm. Không có nó thì chạy pytest trên máy thật sẽ rải tệp kết quả vào Downloads của người đó — bộ test **không bao giờ được để lại rác** ngoài thư mục tạm của chính nó |

`conftest.py` cũng chèn gốc kho vào `sys.path`, nên `from api import PipelineAPI`
chạy được mà không cần cài gói.

CI: `python -m pytest tests/ -q`
(`.github/workflows/build-windows-exe.yml:51`). Workflow cũng chép cả `mau_csv` và
`du_lieu_test` vào bản đóng gói (dòng 148–149) — nên **các bộ dữ liệu là một phần của
sản phẩm giao**, không phải tài sản chỉ có trong kho mã.

### 9.2 · Bộ dữ liệu ↔ test canh nó

| Bộ / tệp | Test canh |
|---|---|
| `mau_csv/` (8 tệp mẫu + định dạng) | `tests/test_csv_mau.py` |
| `mau_csv/vi_du_day_du/` | `tests/test_vi_du_day_du.py` |
| `mau_csv/MAU_*.xlsx` | `tests/test_doc_file_excel.py` |
| `du_lieu_test/bo_sach/` | `tests/test_bo_sach.py` (11 test) |
| `du_lieu_test/vi_du_huong_dan/` | `tests/test_vi_du_huong_dan.py` |
| `du_lieu_test/bo_nhieu_buoi/` | `tests/test_nhieu_buoi.py` (94 KB — lớn nhất), `test_du_lieu_ket_qua.py`, `test_giao_dien_chon_buoi.py`, `test_giao_dien_danh_sach_clb.py`, `test_giao_dien_thu_gon_ket_qua.py` |
| `du_lieu_test/NHAP_TAY.md` | `tests/test_kich_ban_nhap_tay.py` |
| kỹ năng `sinh-du-lieu-clb` | `tests/test_skill_sinh_du_lieu.py` |
| nhận diện loại tệp, nạp CLB bằng CSV | `tests/test_upload_tu_nhan_dien.py`, `test_giao_dien_upload.py` |
| `so_lieu_*.json` (số đo) | `test_boc_tham.py`, `test_toi_uu_on_dinh.py`, `test_danh_doi_on_dinh.py`, `test_khong_du_tru.py`, `test_hai_canh_du_tru.py`, `test_anh_huong_seed.py`, `test_nghich_canh.py`, `test_diem_bat_thuong.py` — **tự bỏ qua** nếu phép đo chưa chạy |

Test đường dữ liệu không gắn với tệp cố định nào: `test_api.py`, `test_data_health.py`,
`test_data_durability.py`, `test_pipeline_core.py`, `test_reserve_group_csv.py`,
`test_chuan_hoa_nhom_du_tru.py`, `test_nap_diem_tu_file.py`, `test_nap_du_lieu_ca_kho.py`,
`test_nap_xuat_ca_hiem.py`, `test_export_ket_qua.py`, `test_xoa_du_lieu.py`,
`test_chen_stb_cong_bang.py`, `test_stb_khong_phu_thuoc_thu_tu.py`, `test_i18n_sync.py`,
`test_khoi_dong_backend.py`, `test_browser_host.py`, `test_chan_doan.py`, `test_do_api.py`,
`test_bieu_tuong.py`, và nhóm `test_giao_dien_*.py`.

### 9.3 · Mười bốn test canh chính kỹ năng

`tests/test_skill_sinh_du_lieu.py` nạp `sinh_du_lieu.py` bằng
`importlib.util.spec_from_file_location` (script không phải gói cài được), rồi sinh bộ
và **nhập vào `PipelineAPI` thật, đếm cảnh báo**.

| Test | Kiểm |
|---|---|
| `test_bo_ngau_nhien_nhap_sach` | bộ sinh ra nhập vào **0 cảnh báo** — tham số hoá theo số em / số buổi / seed |
| `test_truong_mot_buoi_cung_nhap_sach` | trường một buổi cũng nhập sạch |
| `test_cung_hat_giong_cho_ra_cung_bo` | cùng seed cho ra cùng bộ |
| `test_soat_bat_ma_clb_khong_co_that` | điều 1 |
| `test_soat_bat_clb_nam_sai_cot_buoi` | điều 2 |
| `test_soat_bat_hai_tran_moi_buoi` | điều 4 và 5 |
| `test_soat_bat_diem_cho_clb_em_khong_khai_nguyen_vong` | điều 8 |
| `test_soat_bat_du_tru_lon_hon_suc_chua_va_thieu_nhom` | điều 6 |
| `test_soat_bat_khai_buoi_nua_voi` | khai buổi nửa vời |
| `test_soat_bat_ma_hoc_sinh_trung` | điều 9 |
| `test_spec_sai_thi_khong_ghi_tep_nao` | **sai thì không tệp nào được ghi** |
| `test_soat_bo_mau_da_kiem_chung` | chạy bộ soát của kỹ năng trên `mau_csv/vi_du_day_du/` |
| `test_skill_md_neu_dung_hai_tran` | `SKILL.md` **phải nêu cả hai trần** |
| `test_tran_trong_skill_khop_voi_tran_cua_phan_mem` | trần trong kỹ năng **phải bằng** trần phần mềm |

Hai test cuối là thứ giữ tài liệu khỏi mục: đổi trần trong `rbda_priority_pipeline.py`
mà quên sửa `SKILL.md` là test kêu ngay.

> ⚠️ Không test nào **đọc lại** bộ một buổi bằng `doc_bo` rồi soát. Đó là lý do lỗi ở
> [4.6](#46--giới-hạn-đã-đo-soat-không-đọc-được-bộ-một-buổi) sống được tới giờ:
> `test_truong_mot_buoi_cung_nhap_sach` sinh bộ rồi nạp vào `PipelineAPI` — đúng
> đường mà lỗi không nằm trên.

---

## Phần 10 · Sinh lại mọi thứ

Mọi bộ trong kho sinh lại được từ mã, và **hạt giống cố định** nên chạy bao nhiêu lần
cũng ra đúng bộ đó. Đây là lý do có thể tin các bảng ở [Phần 7](#phần-7--kết-quả-đúng-đã-kiểm-chứng).

```bash
# ── Bộ cạnh tranh cao + CSDL demo ──────────────────────────────────
./.venv/bin/python du_lieu_test/tao_du_lieu_test.py     # TEST_01..04.xlsx   SEED = 2026
./.venv/bin/python du_lieu_test/tao_db_demo.py          # app_DEMO_da_cham_diem.db

# ── Năm bộ CSV chạy thử ────────────────────────────────────────────
./.venv/bin/python du_lieu_test/bo_sach/tao_bo_sach.py               # SEED = 9090
./.venv/bin/python du_lieu_test/bo_nhieu_buoi/tao_bo_nhieu_buoi.py   # HAT  = 7788
./.venv/bin/python du_lieu_test/bo_sau_buoi/tao_bo_sau_buoi.py       # HAT  = 20260912
./.venv/bin/python du_lieu_test/bo_can_bang/tao_bo_can_bang.py       # HAT  = 31415
./.venv/bin/python du_lieu_test/vi_du_huong_dan/tao_vi_du.py         # tất định, không random

# ── Tệp mẫu định dạng ──────────────────────────────────────────────
./.venv/bin/python mau_csv/vi_du_day_du/tao_bo_mau.py   # tất định, một bảng khai báo
./.venv/bin/python mau_csv/tao_so_nhap.py              # SO_NHAP_*.xlsx từ chính các CSV

# ── Bộ đo tải — chạy doi_chung.py TRƯỚC mọi thứ khác ───────────────
./.venv/bin/python du_lieu_test/thu_tai/doi_chung.py       # (1) kiểm bộ đo
./.venv/bin/python du_lieu_test/thu_tai/chay_thu_tai.py    # (2) lưới quét, ~15 phút
./.venv/bin/python du_lieu_test/thu_tai/do_csdl.py         # (3) tầng CSDL
xvfb-run -a ./.venv/bin/python du_lieu_test/thu_tai/do_giao_dien.py   # (4) tầng giao diện
./.venv/bin/python du_lieu_test/thu_tai/kiem_on_dinh.py    # (5) kết quả có còn ĐÚNG không
./.venv/bin/python du_lieu_test/thu_tai/lam_bao_cao.py     # (6) dựng trang báo cáo
```

Bảng hạt giống, gom lại một chỗ:

| Bộ | Biến | Giá trị |
|---|---|---|
| `TEST_01..04` + CSDL demo | `SEED` | `2026` |
| `bo_sach` | `SEED` | `9090` |
| `bo_nhieu_buoi` | `HAT` | `7788` |
| `bo_sau_buoi` | `HAT` | `20260912` |
| `bo_can_bang` | `HAT` | `31415` |
| `vi_du_huong_dan` · `vi_du_day_du` | — | tất định, không dùng `random` |
| chạy phân bổ khi kiểm kết quả | `seed` | `42` |

### Dựng một bộ hoàn toàn mới cho trường khác

```bash
S=.claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py

# Trường nhiều buổi
python $S ngau --ra ./bo_moi --hoc-sinh 180 \
    --buoi thu_2,thu_4,thu_6 --clb-moi-buoi 3 --seed 42

# Trường một buổi — bỏ hẳn --buoi
python $S ngau --ra ./bo_moi --hoc-sinh 120

# Từ bản khai báo JSON tường minh
python $S tao --spec truong.json --ra ./bo_moi

# Soát lại (⚠️ chưa dùng được với bộ MỘT BUỔI — xem 4.6)
python $S soat ./bo_moi
```

Rồi **luôn** kiểm bằng phần mềm thật theo đoạn ở [4.7](#47--luôn-kiểm-bằng-phần-mềm-thật).
Tiêu chuẩn: **0 cảnh báo khi nhập · 0 cảnh báo sức khoẻ · chạy được.**

### Soát một bộ đã có trong kho

`soat` đòi đúng ba tên tệp `01_danh_sach_CLB.csv`, `02_chon_CLB_muon_thi.csv`,
`03_xep_hang_nguyen_vong.csv`. Các bộ trong kho mang tiền tố (`SACH_`, `NHIEUBUOI_`,
`SAUBUOI_`, `CANBANG_`, `VIDU_`) nên phải chép sang tên chuẩn trước:

```bash
BO=du_lieu_test/bo_nhieu_buoi
T=$(mktemp -d)
cp $BO/*01_danh_sach_CLB.csv        $T/01_danh_sach_CLB.csv
cp $BO/*02_chon_CLB_muon_thi.csv    $T/02_chon_CLB_muon_thi.csv
cp $BO/*03_xep_hang_nguyen_vong.csv $T/03_xep_hang_nguyen_vong.csv
python .claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py soat $T
```

Kết quả mong đợi cho từng bộ: xem bảng ở [4.6](#46--giới-hạn-đã-đo-soat-không-đọc-được-bộ-một-buổi).

### Chạy test

```bash
./.venv/bin/python -m pytest tests/ -q                    # toàn bộ
./.venv/bin/python -m pytest tests/test_skill_sinh_du_lieu.py -q   # riêng kỹ năng
./.venv/bin/python -m pytest tests/test_bo_sach.py tests/test_csv_mau.py \
    tests/test_vi_du_day_du.py tests/test_vi_du_huong_dan.py -q   # riêng các bộ dữ liệu
```

---

## Phần 11 · Bản chính ở đâu

Tài liệu này là **bản tổng hợp**. Một tài liệu tổng hợp mà không nói rõ nó là bản chép
thì sớm muộn sẽ lệch với bản chính mà không ai biết. Sửa một điều thì sửa ở cột bên
phải, rồi cập nhật lại tài liệu này.

| Điều | Bản chính |
|---|---|
| Hai trần **10** / **5** | `rbda_priority_pipeline.py:84` và `:89` |
| Đặc tả cột, mọi biến thể định dạng | `mau_csv/HUONG_DAN_CSV.md` |
| Quy tắc sinh dữ liệu, chín điều phải đúng | `.claude/skills/sinh-du-lieu-clb/SKILL.md` |
| Hành vi bộ sinh và bộ soát | `.claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py` |
| Số đo đã kiểm chứng về thuật toán | `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` |
| Kết quả mong đợi của mỗi bộ | `README.md` của chính thư mục bộ đó |
| Giải thích từng cột của bộ mẫu | `mau_csv/vi_du_day_du/GIAI_THICH.md` |
| Kịch bản gõ tay | `du_lieu_test/NHAP_TAY.md` |
| Các cột của `ket_qua_thu_tai.csv` | `du_lieu_test/thu_tai/README.md` |
| Bộ câu hỏi Microsoft Forms sinh ra các cột này | `BO_CAU_HOI_FORMS.md` |
| Thuật toán xếp chỗ | `NGHIEN_CUU_TOI_UU.md`, `CO_CHE_THUAT_TOAN.md` |
| Kế hoạch nhiều buổi trong tuần | `KE_HOACH_NHIEU_BUOI.md` |
| Cơ chế bốc thăm | `GIAI_DAP_BOC_THAM.md` |
| Mã thông báo và bản dịch | `i18n_errors.py`, `i18n.js` |

`tests/test_tai_lieu_du_lieu.py` canh tài liệu này: mọi đường dẫn nêu ra phải tồn tại,
mọi header CSV trích ra phải khớp tệp thật, hai trần phải khớp phần mềm, và mọi tiêu đề
của `SKILL.md` phải có mặt ở [4.1](#41--toàn-văn-skillmd).
