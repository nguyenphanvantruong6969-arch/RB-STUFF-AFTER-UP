# Bộ dữ liệu đầu vào mẫu — giải thích từng cột, từng dòng

Đây là **một trường hoàn chỉnh**, không phải ba mẩu rời. Ba tệp trong thư mục
này khớp nhau từng mã: mọi `club_id` trong tệp học sinh đều có thật trong danh
sách câu lạc bộ, mọi câu lạc bộ nằm đúng cột buổi của nó, mọi ô điểm đều ứng
với một câu lạc bộ mà em đó thật sự đăng ký thi.

Bản để thả vào phần mềm là **`SO_NHAP_CLB_vi_du.xlsx`** — cả ba tệp gộp trong
một Sổ nhập CLB (`mau_csv/HUONG_DAN_SO_NHAP.md`). Kéo sổ vào, bấm **Nhập sổ**,
rồi **Chạy phân bổ** là ra kết quả ngay. Phần dưới giải thích ba tệp CSV mà sổ
được sinh ra từ đó — cùng dữ liệu, cùng kết quả.

| | |
|---|---|
| Trường | 3 buổi (`thu_2`, `thu_4`, `thu_6`), 9 câu lạc bộ, 24 học sinh |
| Nhập vào | **0 cảnh báo** ở cả ba tệp, **0 cảnh báo** ở bảng sức khoẻ dữ liệu |
| Chạy thử | 23 / 24 em có ít nhất một câu lạc bộ; không câu lạc bộ nào vượt sức chứa |

> Toàn bộ tên học sinh là **tên bịa**. Không có dữ liệu học sinh thật nào trong
> kho mã nguồn này.

---

## Tệp 1 · `01_danh_sach_CLB.csv`

**Nhập tệp này TRƯỚC.** Hai tệp học sinh tham chiếu tới `club_id`, nên nhập
ngược thứ tự là cả tệp học sinh bị bỏ qua.

```csv
club_id,name,capacity,reserve_capacity,reserve_group,buoi
clb_bongro,CLB Bóng rổ,6,0,,thu_2
clb_vanhoc,CLB Văn học,5,2,chinh_sach,thu_2
clb_tinhoc,CLB Tin học,4,0,,thu_2
clb_mythuat,CLB Mỹ thuật,5,1,khoi_10,thu_4
clb_robotics,CLB Robotics,4,0,,thu_4
clb_nauan,CLB Nấu ăn,6,0,,thu_4
clb_tienganh,CLB Tiếng Anh,5,2,chinh_sach,thu_6
clb_lamvuon,CLB Làm vườn,6,0,,thu_6
clb_covua,CLB Cờ vua,4,0,,thu_6
```

| Cột | Bắt buộc | Trong bộ này |
|---|---|---|
| `club_id` | ✅ | Mã ngắn, không dấu, không khoảng trắng. **Phải khớp từng ký tự** với hai tệp kia |
| `name` | ✅ | Tên đầy đủ, có dấu — đây là chữ in ra bảng kết quả |
| `capacity` | ✅ | Tổng chỉ tiêu, phải **lớn hơn 0** |
| `reserve_capacity` | Không | Số suất dành riêng. `0` hoặc bỏ trống = không có |
| `reserve_group` | Không | Nhóm được ưu tiên. Bỏ trống = câu lạc bộ không có suất dự trữ |
| `buoi` | Không | Buổi sinh hoạt. **Trường một buổi thì bỏ hẳn cột này** |

### Ba điều bộ này cố ý cho thấy

**1. Suất dự trữ là một con số, không phải một cái nhãn.** `clb_vanhoc` có
`reserve_capacity=2` và `reserve_group=chinh_sach`: hai trong năm chỗ dành cho
diện chính sách. `clb_bongro` có `0` và để trống nhóm — không có dự trữ.
Điền nhóm mà để số bằng 0 thì cũng như không có, nên hai ô này luôn đi cùng nhau.

**2. Hai nhóm dự trữ khác nhau cùng tồn tại.** `chinh_sach` ở `clb_vanhoc` và
`clb_tienganh`, `khoi_10` ở `clb_mythuat`. Một em thuộc `khoi_10` **không** có
quyền gì ở suất dự trữ của `chinh_sach`, và ngược lại.

**3. Ba buổi, mỗi buổi ba câu lạc bộ.** Vì mỗi em tối đa một câu lạc bộ mỗi
buổi, tổng số chỗ mỗi buổi mới là thứ quyết định bao nhiêu em có chỗ ngày đó —
không phải tổng chỗ cả tuần.

---

## Tệp 2 · `02_chon_CLB_muon_thi.csv`

Tệp này nói **em nào muốn thi vào câu lạc bộ nào**, và kèm luôn **điểm thi** nếu
trường đã chấm xong trên giấy.

```csv
student_id,name,reserve_group,test_club_1,score_1,test_club_2,score_2,test_club_3,score_3
HS001,Nguyễn Văn An,,clb_tinhoc,"9,5",clb_robotics,"8,0",clb_tienganh,"7,5"
HS002,Trần Thị Bình,chinh_sach,clb_tinhoc,"6,0",clb_tienganh,"8,5",,
HS003,Lê Minh Cường,,,,,,,
```

| Cột | Bắt buộc | Ghi chú |
|---|---|---|
| `student_id` | ✅ | **Khoá chính.** Phân biệt hoa thường: `hs001` và `HS001` là hai em khác nhau |
| `name` | Không | Bỏ trống vẫn nhập được, nhưng bảng kết quả sẽ chỉ có mã |
| `reserve_group` | Không | Diện của em. Bỏ trống = không thuộc diện nào |
| `test_club_N` | Không | Mã câu lạc bộ em đăng ký thi |
| `score_N` | Không | Điểm của câu lạc bộ **cùng số N** |

### Bốn điều bộ này cố ý cho thấy

**1. Ghép theo SỐ trong tên cột, không theo vị trí.** `score_2` luôn đi với
`test_club_2`, dù hai cột đó nằm cách nhau bao xa trong tệp. Vì thế bộ này chỉ
cần **3 cặp cột**, không phải 15 — mỗi em ở đây thi nhiều nhất 3 câu lạc bộ.
Một bảng 33 cột gần như trống rỗng không dạy được ai điều gì.

**2. Dấu phẩy thập phân.** `"9,5"` — đúng cách Excel bản tiếng Việt lưu ra.
Phần mềm đọc được cả `9,5` lẫn `9.5`. Dấu nháy kép quanh ô là do chính Excel
thêm khi giá trị có dấu phẩy; không phải gõ tay.

**3. Em không thi câu lạc bộ nào cũng là một dòng hợp lệ.** `HS003` để trống
hết. Em ấy vẫn xếp nguyện vọng bình thường ở tệp 3, chỉ là em ấy sẽ đứng ở
**tầng hai** — tầng của những em không dự thi — tại mọi câu lạc bộ có tổ chức
thi, và thứ tự trong tầng đó do bốc thăm quyết định.

**4. Chỉ 3 trong 9 câu lạc bộ có thi.** `clb_tinhoc`, `clb_robotics`,
`clb_tienganh` — mỗi buổi một câu lạc bộ. Sáu câu lạc bộ còn lại không ai khai
ở tệp này, nghĩa là chúng **không tổ chức thi**, và mọi em cạnh tranh thuần
bằng bốc thăm. Không có cột nào đánh dấu "câu lạc bộ này có thi"; phần mềm suy
ra từ chính tệp này.

> ⚠️ Cột `score_*` **chỉ có tác dụng trong tệp này**. Đặt chúng vào tệp nguyện
> vọng thì điểm không được nạp, và phần mềm sẽ nói rõ điều đó thay vì im lặng.

---

## Tệp 3 · `03_xep_hang_nguyen_vong.csv`

Tệp này nói **em muốn vào câu lạc bộ nào, theo thứ tự ưu tiên nào**, cho từng
buổi.

```csv
student_id,name,reserve_group,thu_2_pref_1,thu_2_pref_2,thu_4_pref_1,thu_4_pref_2,thu_6_pref_1,thu_6_pref_2
HS001,Nguyễn Văn An,,clb_tinhoc,clb_bongro,clb_robotics,clb_nauan,clb_tienganh,clb_covua
HS002,Trần Thị Bình,chinh_sach,clb_vanhoc,clb_tinhoc,clb_mythuat,,clb_tienganh,
HS003,Lê Minh Cường,,clb_bongro,,clb_nauan,clb_mythuat,clb_lamvuon,
```

Tên cột là **`<buổi>_pref_<thứ tự>`**. Buổi trong tên cột phải trùng đúng nhãn
đã khai ở cột `buoi` của tệp 1.

### Bốn điều bộ này cố ý cho thấy

**1. Mỗi buổi một bộ cột riêng, và thứ tự đếm lại từ 1 ở mỗi buổi.**
`thu_2_pref_1` là nguyện vọng số một **của thứ Hai**, không phải của cả tuần.

**2. Câu lạc bộ phải nằm đúng cột buổi của nó.** `clb_nauan` sinh hoạt thứ Tư
nên chỉ được xuất hiện ở cột `thu_4_*`. Đặt nhầm sang `thu_2_*` thì nguyện vọng
đó bị bỏ qua kèm cảnh báo nêu đích danh số dòng — bộ này không có dòng nào như
thế.

**3. Bỏ trống cả một buổi là cách em nói "ngày đó em bận".** `HS021` để trống
toàn bộ cột `thu_2_*`. Đó là dữ liệu hợp lệ, **không phải thiếu sót**: em ấy
chỉ đơn giản không sinh hoạt thứ Hai. Phần mềm không xếp em vào đâu ngày đó và
cũng không cảnh báo gì.

**4. Số nguyện vọng mỗi buổi không cần bằng nhau.** `HS002` khai hai câu lạc bộ
thứ Hai nhưng chỉ một câu lạc bộ thứ Tư. Ô thừa để trống.

> **Trần: tối đa 10 nguyện vọng MỖI BUỔI** (đúng giới hạn câu hỏi Ranking của
> Microsoft Forms) và **tối đa 5 câu lạc bộ dự thi MỖI BUỔI**. Vượt trần ở một
> buổi thì **chỉ mất buổi đó**, các buổi khác của em vẫn được nhập bình thường.
> Bộ này dùng nhiều nhất 2 nguyện vọng và 1 câu lạc bộ dự thi mỗi buổi, nên còn
> rất xa trần.

---

## Chạy thử bộ này ra gì

Hạt giống `42`, chạy cả tuần:

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

Mọi câu lạc bộ lấp đầy đúng sức chứa, và cả năm suất dự trữ đều có người dùng.

**Độ phủ:** 1 em không có câu lạc bộ nào · 7 em có 1 · 10 em có 2 · 6 em có 3.
Trung bình 1,88 câu lạc bộ mỗi em.

### Một em vẫn trắng tay — và đó là điều nên đọc kỹ

`HS013 · Đặng Gia Phúc`, diện `chinh_sach`, khai đủ năm nguyện vọng và có dự
thi. Em ấy không vào được câu lạc bộ nào.

Lý do kiểm chứng được rõ nhất nằm ở `clb_tienganh`: **10 em dự thi, 5 chỗ**, và
điểm của HS013 là **6,0 — đứng thứ chín trên mười**.

| Hạng | Em | Điểm | Diện |
|---|---|---|---|
| 1 | HS010 | 9,0 | khoi_10 |
| 2 | HS002 | 8,5 | chinh_sach |
| 3 | HS017 | 8,0 | khoi_10 |
| … | | | |
| **9** | **HS013** | **6,0** | **chinh_sach** |
| 10 | HS015 | 5,5 | — |

Ở bốn câu lạc bộ còn lại em ấy thua ở bốc thăm hoặc thua những em có quyền ưu
tiên mạnh hơn tại chính câu lạc bộ đó.

**Bài học cho người vận hành:** thuộc diện dự trữ **không phải** một lời bảo
đảm có chỗ. Suất dự trữ là một cái **sàn** — nó bảo đảm nhóm đó không bị ép
xuống dưới một mức, chứ không bảo đảm từng cá nhân trong nhóm. Muốn hiểu cơ chế
xếp chỗ ở mức chi tiết hơn, đọc `docs/NGHIEN_CUU_TOI_UU.md`.

---

## Tự dựng một bộ như thế này cho trường mình

Thư mục này kèm `tao_bo_mau.py` — chính đoạn mã đã sinh ra ba tệp trên. Nó đọc
**một bảng khai báo duy nhất** rồi phát ra cả ba tệp, nên ba tệp không thể lệch
nhau. Trước khi ghi, nó soát chín điều và **dừng hẳn** nếu có điều nào sai:

1. mọi `club_id` trong nguyện vọng đều có thật;
2. mọi câu lạc bộ nằm đúng cột buổi của nó;
3. không nguyện vọng nào trùng trong cùng một buổi;
4. không buổi nào vượt trần 10 nguyện vọng;
5. không buổi nào vượt trần 5 câu lạc bộ dự thi;
6. mọi `club_id` được chấm điểm đều có thật;
7. chỉ chấm điểm cho câu lạc bộ có tổ chức thi;
8. chỉ chấm điểm cho em có khai nguyện vọng câu lạc bộ đó;
9. mọi mã học sinh là duy nhất.

Sửa bảng khai báo ở đầu tệp rồi chạy `python tao_bo_mau.py` là có bộ mới.
