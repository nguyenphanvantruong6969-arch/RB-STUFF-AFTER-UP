# Phần mềm này chạy cơ chế gì

> **Đây là bản mô tả PHẦN MỀM, không phải phần cơ sở lý thuyết của bài nghiên
> cứu.** Tệp này ghi *phần mềm làm gì* và *chỗ nào trong mã kiểm chứng được*.
> Phần diễn giải ý nghĩa khoa học, phần Kết luận, phần Tính mới — học sinh tự
> viết (Phụ lục 1).

Số dòng đối chiếu với `rbda_priority_pipeline.py` tại commit hiện tại. Kiểm lại
bằng:

```bash
grep -n "^def " rbda_priority_pipeline.py
```

---

## ⚠️ Báo cáo và phần mềm: còn đúng MỘT chỗ lệch

> **Cập nhật 21/09.** Bản trước của mục này ghi rằng báo cáo có **0** lần
> "dự trữ", **0** lần "bốc thăm", **0** lần "RB-DA". Điều đó **đã lạc hậu**.
> Bản báo cáo hiện tại (`...15trang_3.docx`) **đã mô tả cả ba lớp**: dự trữ mềm
> ở mục 4.2.2.2, bốc thăm STB ở 4.2.2.3, ưu tiên hai tầng ở 4.2.2.4, và tên
> RB-DA xuất hiện ở 4.2.2.1. Bảng đối chiếu ở cuối tệp đã được sửa theo.

Chỗ lệch **còn thật** là chỗ khó nhất, và nó vẫn chưa được viết ra:

**Báo cáo vẫn mô hình hóa mỗi CLB là "một danh sách thứ tự ưu tiên"** (mục
*Bài toán ghép cặp ổn định*). Với `reserve_capacity > 0` thì hàm lựa chọn thật
**không phải một thứ tự tuyến tính** — phản ví dụ chạy được ở mục
*"Chỗ mô hình trong báo cáo không mô tả được phần mềm"* phía dưới.

**Vì sao kết quả vẫn đúng:** định lý Gale–Shapley 1962 giả định đúng cái mô
hình một danh sách đó, nên dạng gốc không áp dụng nguyên văn. Nhưng hàm lựa chọn
có dự trữ vẫn có **tính thay thế** — em nào được chọn từ một nhóm lớn thì vẫn
được chọn khi nhóm nhỏ đi (kiểm bằng máy ngày 23/09 trên 221 220 cặp nhóm: 0 vi
phạm tính thay thế, 0 vi phạm luật cầu tổng). Lý thuyết ghép cặp tổng quát chỉ
cần các tính chất đó để bảo đảm ổn định, tối ưu cho học sinh và chống khai gian.
`NGHIEN_CUU_TOI_UU.md` TN1 (2 088 thể hiện vét cạn, 0 phản ví dụ, kể cả cấu hình
có dự trữ) **khớp đúng dự đoán đó**: phép đo xác nhận phần mềm cài đặt đúng, chứ
không phải một phát hiện lý thuyết mới.

Phần diễn giải và việc viết lại giả thuyết — **học sinh tự làm** (Phụ lục 1).
Bản rà soát báo cáo: `BAO_VE_RA_SOAT_BAO_CAO.md` mục B1–B2.

---

## Năm lớp cơ chế

| # | Lớp | Hàm · dòng |
|---|---|---|
| 1 | Deferred Acceptance, học sinh đề xuất | `run_rbda` · **275** |
| 2 | Dự trữ mềm + thứ tự xét | `club_choice_function` · **204** |
| 3 | Single Tie-Breaking (STB) | `generate_stb_lottery` · **1037** · `chen_stb_cho_hoc_sinh_moi` · **1061** |
| 4 | Ưu tiên hai tầng thi / không thi | `compute_club_priority` · **116** |
| 5 | Kiểm chứng ổn định bằng chính hàm lựa chọn | `verify_stability` · **410** |

Lớp 1 là phần báo cáo đã mô tả. Lớp 2, 3, 4 là phần chưa có. Lớp 5 là hệ quả
kỹ thuật bắt buộc của lớp 2.

---

### Lớp 1 — Deferred Acceptance, học sinh đề xuất

`run_rbda` · dòng **275**

Học sinh lần lượt đề xuất vào CLB theo thứ tự nguyện vọng. CLB **giữ tạm** những
em tốt nhất trong số đang có mặt và từ chối phần còn lại. Em bị từ chối đề xuất
tiếp nguyện vọng sau. Hết đề xuất thì dừng.

Chữ *"trì hoãn"* nằm ở chỗ **giữ tạm**: CLB không chốt ai cho tới vòng cuối, nên
một em giỏi xuất hiện muộn vẫn đẩy được em kém hơn ra.

**Vì sao dự án cần:** đây là lớp thay thế cách xét theo thứ tự đăng ký.

---

### Lớp 2 — Dự trữ mềm, xét hai lượt

`club_choice_function` · dòng **204**

Mỗi CLB có thể để riêng một số suất (`reserve_capacity`) cho một nhóm học sinh
(`reserve_group`). Khi xét, CLB chạy **hai lượt**:

1. **Lượt dự trữ** — chỉ xét em thuộc diện, lấy tối đa bằng số suất dự trữ.
2. **Lượt chung** — xét toàn bộ số còn lại (kể cả em thuộc diện chưa được suất
   dự trữ), lấp nốt sức chứa.

**"Mềm" nghĩa là gì:** suất dự trữ **không khoá cứng**. Không đủ em thuộc diện
thì phần thừa **tự chuyển sang lượt chung** — CLB vẫn tuyển đủ. Có test canh
điều này (`test_suat_du_tru_thua_tu_chuyen_sang_luot_chung`).

**Một chi tiết quan trọng trong mã** (ghi chú dòng **188–202**): việc phân nhóm
dự trữ/chung phải **tính lại ở mỗi vòng**, theo đúng tập em đang có mặt lúc đó.
Bản đầu tiên gộp thành một thứ tự tổng thể tính một lần — **sai**, và đã sửa sau
khi đối chiếu với bản tham chiếu.

**Vì sao dự án cần:** để CLB giữ được chỗ cho nhóm mình hướng tới, mà không phải
loại bỏ cơ chế xét chung.

---

### Lớp 3 — Single Tie-Breaking (STB)

`generate_stb_lottery` · dòng **1037**

Mỗi học sinh nhận **một** số bốc thăm, **dùng chung cho mọi CLB**. Đó là nghĩa
của *"single"* — trái với việc mỗi CLB bốc một bộ số riêng.

**Ba tính chất đã đo, không phải khẳng định suông:**

- Cùng dữ liệu, cùng seed → cùng kết quả, **kể cả khi đổi thứ tự nhập liệu**
  (`sorted()` trước khi xáo — dòng 1056).
- Mã học sinh **không** kéo thứ hạng: tương quan giữa mã và số bốc thăm **đổi
  dấu** qua 8 khối seed → là nhiễu. Xem `GIAI_DAP_BOC_THAM`.
- Đổi seed thì **1,1%** số em đổi kết cục có suất / không suất, và **0 cặp phá
  vỡ ở mọi seed** trong 600 lần chạy.

> **KHÔNG viết:** *"số bốc thăm dựa trên mã học sinh"* — sai, và nghe như em tên
> A có lợi hơn em tên Z. Viết đúng: *"bốc thăm không phụ thuộc thứ tự nhập liệu"*.

**Học sinh thêm vào SAU khi bộ số đã khoá** (`chen_stb_cho_hoc_sinh_moi` ·
dòng **1061**): em mới **bốc một vị trí ngẫu nhiên** trong dàn số, thứ tự tương
đối giữa các em đã có **giữ nguyên tuyệt đối**.

Bản đầu cấp cho em mới số `MAX(stb)+1` — ghi chú trong mã nói mục đích là *"tránh
trùng số"*. Vì số nhỏ = ưu tiên cao, cách đó đặt em mới **sau mọi em cũ, ở mọi
CLB, vĩnh viễn**. Đo được (20 em cũ + 10 em mới tranh 10 suất, đều Tầng 2):

| | Em mới giành được suất |
|---|---|
| Cách cũ | **0** ở mọi seed |
| Công bằng thì kỳ vọng | ~3,3 |
| Sau khi sửa, 20 seed | ít nhất 2 · **TB 3,5** · nhiều nhất 5 |

Đây là quy tắc ở **tầng quản lý dữ liệu** (`api.py`), không phải trong thuật toán
— năm hàm ở trên không đổi một dòng nào, và **không con số nào trong báo cáo phải
đo lại**. Có 13 test canh: `tests/test_chen_stb_cong_bang.py`.

**Vì sao dự án cần:** ở tầng không thi tuyển, nhiều em ngang nhau hoàn toàn. Phải
có cách phá hoà, và cách đó phải tái lập được để kiểm toán.

---

### Lớp 4 — Ưu tiên hai tầng: đã thi / không thi

`compute_club_priority` · dòng **116**

| Tầng | Gồm ai | Xếp theo |
|---|---|---|
| **Tầng 1** | Em **đã được chấm điểm** cho CLB đó | Điểm giảm dần; **hoà điểm mới tới** số bốc thăm |
| **Tầng 2** | Em có đăng ký nhưng **không thi** CLB đó | **Thuần** số bốc thăm |

**Tầng 1 luôn đứng trọn trước Tầng 2** — không xen kẽ.

**Một ràng buộc cứng ghi ngay trong mã** (dòng 131–140): hàm này **không được**
nhận bất kỳ tham số nào liên quan tới **thứ hạng nguyện vọng** của học sinh. Nếu
CLB biết em xếp mình là nguyện vọng mấy rồi ưu tiên theo đó, tính *khai thật có
lợi nhất* của thuật toán bị phá.

**Vì sao dự án cần — đây là lớp sinh ra từ hoàn cảnh trường:** có CLB tổ chức
thi tuyển, có CLB không. Một bài toán ghép cặp chuẩn không có chỗ cho tình huống
hai loại CLB cùng tồn tại trong một đợt phân bổ.

---

### Lớp 5 — Kiểm chứng ổn định bằng chính hàm lựa chọn

`verify_stability` · dòng **410**

Cách thường: so kết quả với một bảng ưu tiên tĩnh. **Không dùng được ở đây** —
xem phần dưới.

Cách phần mềm làm: với mỗi cặp (học sinh `s`, câu lạc bộ `c`) mà `s` thích `c`
hơn chỗ hiện tại — **thêm `s` vào tập `c` đang giữ, rồi chạy lại hàm lựa chọn
của `c`**. Nếu `s` nằm trong tập được chọn thì đó là một **cặp phá vỡ**.

**Vì sao dự án cần:** đây là định nghĩa tổng quát, đúng cả khi hàm lựa chọn
không phải một thứ tự tuyến tính. Cách cũ dùng bảng tĩnh **đã bị phát hiện sai**
khi đối chiếu với bản tham chiếu.

---

## Chỗ mô hình trong báo cáo không mô tả được phần mềm

Báo cáo viết mỗi CLB có **một danh sách ưu tiên `Q_j`**. Hàm lựa chọn thật
**không phải** một thứ tự tuyến tính. Chạy lại để tự xem:

```bash
python du_lieu_test/do_hai_canh_du_tru.py
```

> CLB sức chứa **3**, trong đó **1 suất dự trữ**.
> Ưu tiên: **A > B > C > D**. D thuộc diện dự trữ.
> Ưu tiên **giữ nguyên** ở cả hai cảnh; chỉ đổi *ai đang có mặt*.

| | Mô hình *một danh sách Q_j* | `club_choice_function` thật | |
|---|---|---|---|
| **Cảnh 1** — D có mặt | A, B, C | **D, A, B** | **LỆCH** |
| **Cảnh 2** — D vắng mặt | A, B, C | A, B, C | khớp |

**Đọc ra hai điều:**

1. Cảnh 1: **C xếp trên D, CLB lấy 3 em — mà D đỗ còn C trượt.** Theo mô hình
   một danh sách thì chuyện đó không xảy ra được.
2. So hai cảnh: **cùng em C, cùng thứ hạng, cùng CLB, cùng sức chứa** — lúc có
   suất lúc không. Cái đổi duy nhất là D có mặt hay không.

Nghĩa là: kết cục của C **không chỉ** phụ thuộc thứ hạng của C, mà còn phụ thuộc
**ai khác đang nộp cùng lúc**. Không viết ra được một `Q_j` cố định rồi đọc ra
kết quả.

**Đây không phải lỗi.** Đó là điều suất dự trữ sinh ra, và là lý do Lớp 5 phải
kiểm cặp phá vỡ bằng chính hàm lựa chọn.

Bảng này có test canh: `tests/test_hai_canh_du_tru.py` (11 test). Gỡ cơ chế dự
trữ ra thì **5 test đỏ** — đã thử.

---

## Nếu trường KHÔNG dùng suất dự trữ

Suất dự trữ sinh ra từ hoàn cảnh trường công. Một trường quốc tế có thể không cần
cơ chế đó — mọi CLB đặt `reserve_capacity = 0`. Câu hỏi: phần mềm còn chạy đúng
không, và chỗ lệch ở mục trên có còn không?

```bash
python du_lieu_test/do_khong_du_tru.py
```

### Chỗ lệch BIẾN MẤT — và đó là điều đáng nói nhất

`reserve_capacity = 0` làm `reserve_held = candidates[:0] = []`, nên
`general_capacity = capacity` và lượt chung xét **toàn bộ** pool. Hàm lựa chọn
thu về đúng *"sắp theo thứ hạng, lấy K em đầu"*.

Cùng một pool `A, B, C, D, E` (ưu tiên A > B > C > D > E, sức chứa 3, D và E
thuộc diện dự trữ), chỉ đổi số suất dự trữ:

| Suất dự trữ | `club_choice_function` | Mô hình `Q_j` | |
|---|---|---|---|
| 2 | `D, E, A` | `A, B, C` | **LỆCH** |
| 1 | `D, A, B` | `A, B, C` | **LỆCH** |
| **0** | `A, B, C` | `A, B, C` | **khớp** |

**Đọc ra:** suất dự trữ **là nguyên nhân duy nhất** làm hàm lựa chọn không phải
một thứ tự tuyến tính. Bỏ nó đi thì RB-DA **thu về Deferred Acceptance thuần
tuý**, và **mô hình `Q_j` trong báo cáo trở thành ĐÚNG**.

Nói cách khác: chỗ lệch báo cáo ↔ phần mềm ở mục trên tồn tại **chỉ vì** dự trữ.

### Kết quả phân bổ đổi bao nhiêu

Bỏ hết suất dự trữ, so với giữ nguyên — quét 20 seed:

| Bộ dữ liệu | Em đổi CLB | Em mất suất | Em được thêm suất | Cặp phá vỡ |
|---|---|---|---|---|
| `bo_sach` (140 em · 16 suất dự trữ) | TB **32,3** (23,1%) | 0,1 | 0,1 | **0** ở cả hai cấu hình |
| `TEST_0*` (120 em · 12 suất dự trữ) | TB **22,6** (18,8%) | 5,7 | 4,2 | **0** ở cả hai cấu hình |

Ba điều đọc được:

1. **Phần mềm chạy đúng không cần sửa gì.** 0 cặp phá vỡ ở mọi seed, cả hai cấu
   hình. Trường không dùng dự trữ chỉ cần để cột `reserve_capacity` bằng 0.
2. **Nhưng kết quả không giống nhau** — khoảng **một phần năm** số em đổi CLB.
   16 suất dự trữ trên 150 chỗ làm 32 em đổi chỗ: dự trữ đẩy dây chuyền sang cả
   những em không thuộc diện nào.
3. **Số em mất hẳn suất ít hơn nhiều số em đổi chỗ.** Bỏ dự trữ chủ yếu xáo lại
   *ai vào đâu*, không phải *ai có suất*.

Có **7 test canh** (`tests/test_khong_du_tru.py`), trong đó một test kiểm trên
**200 pool ngẫu nhiên** rằng suất dự trữ 0 cho đúng mô hình `Q_j`.

> **Phần này chỉ ĐẾM hệ quả.** Trường nên hay không nên dùng suất dự trữ —
> **học sinh tự viết** (Phụ lục 1).

---

## Cái giá của tính ổn định — đã đo, không phải suy luận

`verify_stability` canh được **0 cặp phá vỡ**. Nhưng *"ổn định"* và *"tốt nhất
cho học sinh"* là hai chuyện khác nhau, và chỗ khác nhau đó đo được:

> **CẶP ĐÔI CÙNG CÓ LỢI** — em `s1` được xếp CLB `c1`, em `s2` được xếp CLB `c2`,
> mà `s1` thích `c2` hơn và `s2` thích `c1` hơn. Hai em đổi chỗ cho nhau thì
> **cả hai cùng lên** nguyện vọng cao hơn — thuật toán không cho, vì đổi như vậy
> phá mất tính ổn định.

**Đừng lẫn hai khái niệm** — đây là chỗ giám khảo bắt lỗi được ngay:

| | Gồm những ai | Có nghĩa là gì |
|---|---|---|
| **Cặp phá vỡ** (blocking pair) | 1 học sinh + 1 **câu lạc bộ** | Kết quả **không ổn định** → **LỖI** |
| **Cặp đôi cùng có lợi** | 2 **học sinh** | Kết quả không tối ưu Pareto → **đánh đổi đã biết**, không phải lỗi |

Chạy lại:

```bash
python du_lieu_test/do_danh_doi_on_dinh.py
```

### Đo được gì (seed mốc 42)

| Bộ dữ liệu | Cặp phá vỡ | **Cặp đôi cùng có lợi** | Số em dính | Bốc thăm CÓ phần | Bốc thăm VÔ CAN |
|---|---|---|---|---|---|
| `vi_du_huong_dan` (10 em) | 0 | **0** | 0 | — | — |
| `bo_sach` (140 em) | 0 | **85** | 34 (24,3%) | 18 (21%) | **67 (79%)** |
| `TEST_0*` (120 em) | 0 | **19** | 16 (13,3%) | 2 (11%) | **17 (89%)** |

Quét **40 seed**, mỗi bộ:

| Bộ dữ liệu | Cặp phá vỡ | Ít nhất · TB · Nhiều nhất | **Số seed cho 0 cặp** |
|---|---|---|---|
| `vi_du_huong_dan` | 0 ở mọi seed | 0 · 0,0 · 0 | 40 / 40 |
| `bo_sach` | 0 ở mọi seed | 82 · **91,0** · 103 | **0 / 40** |
| `TEST_0*` | 0 ở mọi seed | 19 · **21,5** · 24 | **0 / 40** |

### Không quy được cho bốc thăm — và đây là thí nghiệm chứng minh

Cách đọc tự nhiên là đổ cho **bốc thăm phá hoà**. Ba phép đo đều **không** ủng hộ
cách đọc đó:

1. **Đổi bốc thăm không làm hiện tượng biến mất.** 0/40 seed cho 0 cặp trên cả
   hai bộ có hiện tượng, biên độ dao động nhỏ.
2. **Phần lớn số cặp là em thua vì ĐIỂM**, không phải vì hoà rồi thua bốc thăm —
   79% và 89%.
3. **Thí nghiệm can thiệp thẳng.** Bỏ điểm của `p%` số cặp (em, CLB) để đẩy các
   em đó xuống **Tầng 2** — nơi bốc thăm quyết định **hoàn toàn**. Nếu bốc thăm
   sinh ra tổn thất thì càng nhiều Tầng 2, số cặp phải càng **tăng**.

`bo_sach`, 10 seed mỗi mức:

| Bỏ điểm | Cặp đôi (TB) | Bốc thăm có phần | Thua vì điểm | Seed cho 0 cặp |
|---|---|---|---|---|
| 0% | **90,2** | 18,4 (20%) | 71,8 | 0/10 |
| 25% | 65,3 | 7,9 (12%) | 57,4 | 0/10 |
| 50% | 58,5 | 29,4 (50%) | 29,1 | 0/10 |
| 75% | 45,2 | 41,2 (91%) | 4,0 | 0/10 |
| **100%** | **4,1** | 4,1 (100%) | 0,0 | 0/10 |

`TEST_0*`, cùng cách:

| Bỏ điểm | Cặp đôi (TB) | Bốc thăm có phần | Thua vì điểm | Seed cho 0 cặp |
|---|---|---|---|---|
| 0% | **21,1** | 2,0 (9%) | 19,1 | 0/10 |
| 25% | 20,0 | 4,0 (20%) | 16,0 | 0/10 |
| 50% | 41,5 | 33,9 (82%) | 7,6 | 0/10 |
| 75% | 29,5 | 29,3 (99%) | 0,2 | 0/10 |
| **100%** | **2,2** | 2,2 (100%) | 0,0 | **3/10** |

**Đọc ra:** ở mức bỏ hết điểm, bốc thăm quyết định 100% — mà số cặp lại **ít
nhất** (90,2 → 4,1 và 21,1 → 2,2), thậm chí `TEST_0*` có **3/10 seed cho 0 cặp**,
tức có lần đạt **tối ưu Pareto**. Chuyện đó **không xảy ra lần nào** khi điểm còn
nguyên. Hướng đi ngược hẳn với cách đọc *"tại bốc thăm"*.

> **Hai chỗ phải nói thẳng, đừng cắt đi khi trích:**
>
> - **Các mức ở giữa không đi một chiều** (65,3 · 58,5 · 45,2 — và `TEST_0*` còn
>   vọt lên 41,5 ở mức 50%). Chỉ **hai đầu** của bảng mới là điều đọc ra được.
>   Không viết thành *"càng nhiều Tầng 2 càng ít cặp"*.
> - **Trên ba bộ này, Tầng 2 rất hiếm khi giữ suất**: `bo_sach` chỉ có **8** em
>   giữ suất ở CLB mình không thi, `TEST_0*` có **0**. Nên toàn bộ 18 và 2 cặp
>   *"bốc thăm có phần"* đều đến từ **hoà điểm**, không từ Tầng 2. Thí nghiệm ở
>   trên tồn tại chính vì lý do đó — nó tạo ra Tầng 2 mà dữ liệu gốc không có.

### Nghĩa là gì cho phần mềm

Tổn thất đến từ chỗ **CLB có ưu tiên thật** (điểm thi) và ưu tiên đó **không
trùng** với nguyện vọng học sinh. Đó là đặc điểm của **mọi** thuật toán ghép cặp
giữ tính ổn định, không phải khuyết điểm của bản cài đặt này. Bỏ bốc thăm đi
cũng không gỡ được — số đo ở trên cho thấy bốc thăm gần như vô can.

Bảng số này có test canh: `tests/test_danh_doi_on_dinh.py` (24 test). Sửa hàm
tìm cặp cho lỏng ra thì **3 test đỏ**; sửa hàm quy nguyên nhân thì thêm test đỏ
nữa — đã thử.

> **Phần này chỉ ĐẾM cái giá.** Cái giá đó có chấp nhận được không, có nên đổi cơ
> chế không, nên nói gì với học sinh về nó — **học sinh tự viết** (Phụ lục 1).

---

## Còn câu "có phải cặp ghép TỐT NHẤT không"

Mục trên đo **cái giá** của tính ổn định. Câu hỏi gốc — *kết quả này có phải
cách ghép tốt nhất không* — được trả lời riêng ở **`NGHIEN_CUU_TOI_UU.md`**
(bản có biểu đồ: `NGHIEN_CUU_TOI_UU.html`), bằng sáu thí nghiệm.

Ba kết quả liên quan thẳng tới năm lớp cơ chế mô tả ở trên:

| Phát hiện | Nối vào lớp nào |
|---|---|
| RB-DA là ma trận ổn định **tốt nhất cho học sinh** — 0 phản ví dụ trên **2 088** thể hiện vét cạn, kể cả cấu hình **có dự trữ** | Lớp 1 + Lớp 2 |
| **Không em nào khai gian nguyện vọng mà có lợi** — 0/1 400 lượt vét cạn; cùng phép dò cho ra 258/1 400 dưới cơ chế Boston | Lớp 4 (ràng buộc chống nội sinh, dòng 131–140) |
| **Nhiễu điểm ±0,5 xáo 15,14% số em, đổi seed chỉ xáo 4,36%** | Lớp 3 (bốc thăm chỉ đứng sau điểm) |

Kết quả thứ nhất đáng chú ý vì mục ngay trên đã chứng minh **dự trữ phá được mô
hình một danh sách `Q_j`**. Nó phá mô hình, nhưng **không** phá tính tối ưu —
hai chuyện khác nhau, và cả hai đều đã đo.

Ngược lại, kết quả **không tối ưu Pareto** ở mục trên được đo lại rộng hơn: bộ
đếm cũ chỉ thấy chu trình độ dài 2, bộ đo mới tìm mọi độ dài và thấy **16 chu
trình** trên `bo_sach`, trong đó **7 chu trình dài hơn 2** — tức bộ đếm cũ bỏ
sót gần một nửa.

---

## Bảng đối chiếu báo cáo ↔ phần mềm

Đối chiếu với bản báo cáo hiện tại (`...15trang_3.docx`, quét 21/09):

| Phần mềm chạy | Báo cáo đã mô tả? |
|---|---|
| Deferred Acceptance học sinh đề xuất | ✅ có |
| Ghép cặp nhiều-một, có sức chứa | ✅ có |
| Kiểm tra cặp phá vỡ | ✅ có — và mục 4.2.2.5 đã mô tả **đúng** cách kiểm bằng chính hàm lựa chọn |
| Dự trữ mềm, xét hai lượt | ✅ có — mục 4.2.2.2, nêu cả `reserve_capacity` và `reserve_group` |
| Bốc thăm STB dùng chung mọi CLB | ✅ có — mục 4.2.2.3 |
| Ưu tiên hai tầng thi / không thi | ✅ có — mục 4.2.2.4, kèm cả ràng buộc chống nội sinh |
| Tên RB-DA | ✅ có — mục 4.2.2.1 |
| **Hàm lựa chọn không phải thứ tự tuyến tính** | ❌ **mâu thuẫn** — báo cáo vẫn viết mỗi CLB có *"một danh sách thứ tự ưu tiên"* |
| **Giả thuyết phát biểu đúng chỗ khó** | ❌ **chưa** — giả thuyết hiện tại dùng đúng tiền đề của định lý 1962, nên đúng một cách tầm thường |

Hai dòng ❌ cuối là **cùng một chỗ lệch**, nhìn từ hai phía. Xem
`BAO_VE_RA_SOAT_BAO_CAO.md` mục B1–B2.

---

## Một lưu ý về trích dẫn

Cả dự án chỉ có **đúng một** tên tài liệu được nêu: **Kominers & Sonmez 2016**,
ở `rbda_priority_pipeline.py` dòng 6 và 213 — cho phần dự trữ mềm.

Dòng đó **do chính học sinh viết**, có trong commit đầu tiên `57f2e82` (26/08),
trước khi AI chỉnh sửa tệp.

AI **không** tìm thêm trích dẫn, **không** lập danh mục tài liệu tham khảo và
**không** đánh giá tính mới — Phụ lục 1 cấm. Việc khảo sát tài liệu là của học
sinh.

---

*Tệp này do AI viết, mô tả phần mềm do AI tham gia lập trình. Nó không chứa
nhận định về ý nghĩa khoa học của kết quả — phần đó học sinh tự viết.*
