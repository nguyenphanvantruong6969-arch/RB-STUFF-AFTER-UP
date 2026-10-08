# Thuật toán có đưa ra các cặp ghép TỐT NHẤT không?

> **Bản trình bày (trang web):** `NGHIEN_CUU_TOI_UU.html` — cùng nội dung, có
> biểu đồ, mở bằng trình duyệt bất kỳ. Bản trực tuyến:
> https://claude.ai/code/artifact/a4988038-e0e3-4a7d-b212-ef1459da09c9

> **Mọi con số trong tệp này đều do đo mà có.** Nguồn sự thật là bốn tệp
> `du_lieu_test/so_lieu_*.json`, sinh ra bởi bốn bộ đo dưới đây. Không con số
> nào trong tệp này được gõ tay.
>
> ```bash
> python3 du_lieu_test/do_toi_uu_on_dinh.py     # TN1, TN2, TN4, TN5
> python3 du_lieu_test/do_khai_that.py          # TN3
> python3 du_lieu_test/do_ben_vung.py           # TN6
> python3 du_lieu_test/do_boc_tham.py           # TN7
> python3 -m pytest tests/test_toi_uu_on_dinh.py tests/test_boc_tham.py -v
> ```

---

## Câu hỏi, và vì sao tài liệu cũ chưa trả lời được

`CO_CHE_THUAT_TOAN.md` đã ghi: `verify_stability` canh được **0 cặp phá vỡ**.
Đó là bằng chứng cho tính **ổn định**. Nhưng ổn định chỉ có nghĩa *không ai
phá được kết quả* — nó **không** có nghĩa *đây là kết quả tốt nhất*.

Chữ **"tốt nhất"** có bốn nghĩa khác nhau, và một cơ chế có thể đạt nghĩa này
mà hỏng nghĩa kia. Tệp này đo cả bốn:

| # | Nghĩa của "tốt nhất" | Câu hỏi |
|---|---|---|
| 1 | **Tốt nhất trong các cách ghép ổn định** | Có ma trận ổn định nào mà học sinh thích hơn không? |
| 2 | **Tối ưu Pareto** | Có cách nào làm nhiều em cùng lên nguyện vọng cao hơn mà không ai thiệt? |
| 3 | **Khai thật có lợi nhất** | Có em nào ghi sai thứ tự nguyện vọng rồi được CLB tốt hơn không? |
| 4 | **Bền** | Rung dữ liệu một chút thì kết quả có nhảy lung tung không? |

**Trả lời ngắn: nghĩa 1, 3, 4 — CÓ. Nghĩa 2 — KHÔNG, và đó là đánh đổi bắt
buộc, không phải lỗi.**

---

## Bảng tra nhanh

| Câu hỏi | Trả lời | Số đo |
|---|---|---|
| Có ma trận ổn định nào học sinh thích hơn không? | **Không** | **0** phản ví dụ trên **2 088** thể hiện vét cạn |
| Kể cả khi có suất dự trữ? | **Không** | **1 073/1 073** thể hiện có dự trữ |
| Có cách nào Pareto tốt hơn không? | **Có** | **16** chu trình · **32/140** em cùng lên hạng |
| Giá phải trả cho cách đó? | **Mất ổn định** | 0 → **92** cặp phá vỡ |
| Khai gian nguyện vọng có lợi không? | **Không** | **0/1 400** em, vét cạn mọi cách khai |
| Cơ chế Boston thì sao? | **Có lợi** | **258/1 400** em (18,4%) |
| Đổi bên đề xuất (CLB thay vì học sinh) có đổi kết quả không? | **Không** | **0/20** seed, cả ba bộ |
| Nhiễu dữ liệu có làm mất ổn định không? | **Không** | **0** cặp phá vỡ trên **392** phép thử |
| Em đang trượt có được cứu bởi cơ chế ổn định khác không? | **Không** | tập em có suất **bất biến** ở mọi ma trận ổn định |
| Bốc lại thăm mỗi buổi có làm ít em trắng tay hơn không? | **Có, nhưng rất ít** | **0,245** em trên **160** (0,15%) · KTC 95% [+0,020; +0,465] |
| Còn khi bốc thăm quyết định tất (không có điểm)? | **Có, rất nhiều** | cứu **1,2 → 79,0** em trên **200**, tuỳ tỉ lệ chọi |
| Vì sao hai con số trên cách xa nhau? | **Vì điểm** | lợi thế A2 đi từ **92%** xuống *không phân biệt được* khi tỉ lệ em có điểm chạy từ 0% lên 100% |
| Bốc thăm "có bù" có mở kênh khai gian không? | **Có** | **113/300** em giấu bớt buổi thì có lợi (A1 và A2: **0/300**) |

---

## TN1 — Có phải ma trận ổn định TỐT NHẤT cho học sinh không?

### Vì sao câu này không hiển nhiên

Định lý Gale–Shapley nói: DA do học sinh đề xuất cho ma trận ổn định tốt nhất
cho học sinh. Nhưng định lý đó giả định **mỗi CLB có một danh sách ưu tiên cố
định `Q_j`**. `do_hai_canh_du_tru.py` đã đo được rằng hàm lựa chọn thật của
phần mềm **không phải** một thứ tự tuyến tính — suất dự trữ làm nó phụ thuộc
vào *ai đang có mặt*:

| | Mô hình *một danh sách Q_j* | `club_choice_function` thật |
|---|---|---|
| Cảnh 1 — D có mặt | A, B, C | **D, A, B** |

Nên **không được trích định lý rồi coi là xong**. Câu trả lời phải đến từ phép
đo.

### Cách đo — vét cạn, không lấy mẫu

Với thể hiện đủ nhỏ (7 em / 4 CLB): liệt kê **mọi** phép gán khả dĩ, lọc lấy
tập ổn định bằng đúng `club_choice_function` của phần mềm, rồi so kết quả
RB-DA với **từng** phần tử của tập đó.

Định nghĩa "tốt nhất": **không một em nào thích một ma trận ổn định khác hơn
kết quả RB-DA.**

### Kết quả

| Cấu hình | Thể hiện | Có >1 ma trận ổn định | TB số ma trận | Nhiều nhất | **RB-DA tối ưu** |
|---|---|---|---|---|---|
| Không dự trữ | 1 015 | 120 (11,8%) | 1,13 | 4 | **1 015 / 1 015** |
| **Có dự trữ** | 1 073 | 120 (11,2%) | 1,12 | 4 | **1 073 / 1 073** |

**Chỉ tính trên nhóm KHÓ** — thể hiện có nhiều hơn một ma trận ổn định. Trên
nhóm chỉ có một ma trận, câu hỏi đúng một cách tầm thường (nó là ma trận duy
nhất) và không nói được gì:

| Cấu hình | Thể hiện khó | **RB-DA tối ưu** | Tập em có suất bất biến |
|---|---|---|---|
| Không dự trữ | 120 | **120 / 120** | 120 / 120 |
| **Có dự trữ** | 120 | **120 / 120** | 120 / 120 |

**Đọc ra ba điều:**

1. **Không tìm được phản ví dụ nào.** 2 088 thể hiện, 0 lần RB-DA thua một ma
   trận ổn định khác. Kết luận kinh điển **giữ nguyên** kể cả khi hàm lựa chọn
   không còn là thứ tự tuyến tính.
2. **Suất dự trữ không phá tính tối ưu.** Cột "có dự trữ" và "không dự trữ"
   giống nhau. Đây là chỗ đáng ngạc nhiên nhất của cả nghiên cứu — dự trữ phá
   được mô hình `Q_j` (đã đo), nhưng **không** phá được tính tối ưu.
3. **Định lý bệnh viện nông thôn giữ đúng.** Tập em CÓ SUẤT giống hệt nhau ở
   mọi ma trận ổn định, 240/240 thể hiện khó. Hệ quả thực tế:
   **đổi sang một cơ chế ổn định khác không cứu được em nào đang trượt** — nó
   chỉ đổi *ai vào CLB nào*.

### Trên bộ dữ liệu thật

Vét cạn `vi_du_huong_dan` (10 em / 4 CLB): **đúng 1** ma trận ổn định. RB-DA
nằm trong tập, và tối ưu.

---

## TN2 — Đổi bên đề xuất thì học sinh thiệt bao nhiêu?

Lý thuyết: đổi bên đề xuất cho ra **đầu kia** của dàn ổn định — bản do CLB đề
xuất là bản **xấu nhất** cho học sinh. Đã cài `da_clb_de_xuat` để đo hiệu số.

| Bộ dữ liệu | Seed cho kết quả KHÁC | Em khác nhiều nhất |
|---|---|---|
| `vi_du_huong_dan` (10 em) | **0 / 20** | 0 |
| `bo_sach` (140 em) | **0 / 20** | 0 |
| `TEST_0*` (120 em) | **0 / 20** | 0 |

**Đọc ra:** trên cả ba bộ, hai đầu của dàn ổn định **trùng nhau** — tức tập ổn
định chỉ có **đúng một** phần tử. Nghĩa là:

- Trên dữ liệu này, **mọi** cơ chế ổn định đều buộc phải cho ra đúng kết quả
  đang có. Tranh luận "học sinh đề xuất hay CLB đề xuất" là tranh luận rỗng.
- Bảo đảm "tốt nhất cho học sinh" **có thật** (TN1 chứng minh), nhưng trên ba
  bộ này nó **không phải thứ đang giữ kết quả lại** — ràng buộc nằm chỗ khác.

> **Đây là chỗ dễ đọc sai.** "Hai đầu trùng nhau" là tính chất của **dữ liệu**
> (điểm thi làm thứ tự ưu tiên rất phân tán), **không phải** của bộ đo. Bằng
> chứng: `tests/test_toi_uu_on_dinh.py::TestDaClbDeXuat` dựng một ví dụ hai em
> hai CLB có nguyện vọng ngược hẳn ưu tiên, và ở đó hai bản **cho kết quả khác
> nhau** — mỗi em được nguyện vọng 1 ở bản này, nguyện vọng 2 ở bản kia.

---

## TN3 — Khai thật có phải cách tốt nhất không?

### Vì sao đây là thí nghiệm quan trọng nhất

Mọi con số kiểu *"59% số em được nguyện vọng 1"* chỉ có nghĩa **nếu** nguyện
vọng ghi trên tờ khai là nguyện vọng thật. Nếu khai gian có lợi thì:

- con số "được nguyện vọng 1" đo cái khác chứ không đo sự hài lòng;
- em nào biết mẹo thì lợi, em nào khai thật thì thiệt;
- dữ liệu nguyện vọng thu về không dùng để nghiên cứu gì được nữa.

### Cách đo

Với **mỗi** em: giữ nguyên khai báo của mọi em khác, thử **mọi hoán vị** và
**mọi cách cắt ngắn** danh sách nguyện vọng của riêng em đó, rồi chấm kết quả
bằng nguyện vọng **thật**. Điểm thi và việc tick chọn CLB muốn thi giữ nguyên —
trong phần mềm này đó là hai bước tách rời khỏi bước xếp hạng.

### Kết quả — vét cạn, 200 thể hiện, 1 400 lượt học sinh

| Cơ chế | Em đã thử | **Khai gian được** | Tỉ lệ | Lợi TB (bậc NV) |
|---|---|---|---|---|
| **RB-DA (phần mềm)** | 1 400 | **0** | **0,00%** | — |
| Boston / nhận ngay | 1 400 | **258** | **18,43%** | 2,51 |
| Xét theo bốc thăm | 1 400 | 0 | 0,00% | — |
| TTC | 1 400 | 0 | 0,00% | — |

### Đối chứng ngược — phần bắt buộc phải có

Một bộ dò khai gian lúc nào cũng báo "không tìm thấy" thì vô dụng: có thể nó
hỏng chứ không phải cơ chế tốt. Cột Boston chính là phép kiểm đó, và nó **khác
0**: 160/200 thể hiện có ít nhất một em khai gian được.

Một ví dụ cụ thể dưới Boston:

| | Khai | Kết quả |
|---|---|---|
| Khai thật | `C1 > C3 > C0` | **trượt** (nguyện vọng thứ 5 = không có suất) |
| Khai gian | chỉ ghi `C3` | **được nguyện vọng thứ 2** |

Em đó bỏ nguyện vọng 1 của mình đi thì được suất; ghi thật thì trượt. Đó đúng
là thứ RB-DA loại bỏ.

### Trên bộ dữ liệu thật (mẫu 40 em, tối đa 600 cách khai mỗi em)

| Bộ dữ liệu | RB-DA | Boston | Bốc thăm | TTC |
|---|---|---|---|---|
| `vi_du_huong_dan` | 0 / 10 | 0 / 10 | 0 / 10 | 0 / 10 |
| `bo_sach` | **0 / 40** | **8 / 40** | 0 / 40 | 0 / 40 |
| `TEST_0*` | **0 / 40** | **9 / 40** | 0 / 40 | 0 / 40 |

> **Phạm vi của bảng này:** ở đây không gian tìm kiếm bị **chặn** (danh sách 6
> nguyện vọng có 4 320 cách khai). *"Không tìm thấy"* yếu hơn *"không tồn
> tại"*. Phần kết luận mạnh nằm ở bảng vét cạn phía trên.

**Nối lại với mã nguồn:** `compute_club_priority` có ràng buộc ghi ở dòng 131–140
— hàm này không được nhận thứ hạng nguyện vọng. Bảng trên là **phép đo** cho
thấy ràng buộc đó làm đúng việc của nó, chứ không còn là một dòng ghi chú.

---

## TN4 — So với bốn cơ chế khác

Cùng dữ liệu, cùng bộ số bốc thăm (seed 42), cùng thứ hạng ưu tiên nền. Khác
biệt giữa các dòng đến từ **đúng cách chúng ghép**.

### `bo_sach` — 140 em / 12 CLB

| Cơ chế | NV1 | NV2 | NV3+ | Trượt | Hạng TB | **Cặp phá vỡ** | Khác RB-DA |
|---|---|---|---|---|---|---|---|
| **RB-DA (phần mềm)** | 54 | 46 | 40 | 0 | 2,100 | **0** | — |
| DA do CLB đề xuất | 54 | 46 | 40 | 0 | 2,100 | **0** | 0 |
| Boston / nhận ngay | **92** | 14 | 32 | 2 | **1,826** | 50 | 62 |
| Xét theo bốc thăm | 81 | 24 | 33 | 2 | 1,928 | 121 | 75 |
| TTC | 80 | 29 | 31 | 0 | 1,879 | 118 | 62 |

### `TEST_0*` — 120 em / 10 CLB

| Cơ chế | NV1 | NV2 | NV3+ | Trượt | Hạng TB | **Cặp phá vỡ** | Khác RB-DA |
|---|---|---|---|---|---|---|---|
| **RB-DA (phần mềm)** | 64 | 28 | 16 | 12 | 1,611 | **0** | — |
| DA do CLB đề xuất | 64 | 28 | 16 | 12 | 1,611 | **0** | 0 |
| Boston / nhận ngay | **81** | 10 | 15 | 14 | **1,462** | 25 | 29 |
| Xét theo bốc thăm | 72 | 19 | 16 | 13 | 1,570 | 84 | 49 |
| TTC | 77 | 16 | 12 | 15 | 1,419 | 68 | 28 |

### Chỗ quan trọng nhất trong cả tệp này

**Boston cho 92 em nguyện vọng 1, RB-DA chỉ cho 54.** Nhìn cột đó thì Boston
thắng đậm. Nhưng cùng bảng đó nói:

- Boston tạo **50 cặp phá vỡ** — có 50 lần một em và một CLB cùng muốn nhận
  nhau mà kết quả không cho.
- **18,4%** số em khai gian được dưới Boston (TN3). Nên con số 92 **không phải**
  92 em thật sự được nguyện vọng thật của mình — nó là 92 em được cái họ **dám
  ghi**.

> **Suy ra một điều phải nói thẳng: "tỉ lệ được nguyện vọng 1" MỘT MÌNH không
> phải thước đo chất lượng.** Cơ chế nào cũng đẩy được con số đó lên bằng cách
> khiến học sinh chỉ dám ghi CLB mình chắc đỗ. Đọc cột đó mà không đọc cột
> "cặp phá vỡ" và cột "khai gian" là đọc sai.

---

## TN5 — Còn cách nào Pareto tốt hơn không, và giá bao nhiêu?

### Mở rộng phép đo cũ

`do_danh_doi_on_dinh.py` đếm **cặp đôi cùng có lợi** — chu trình đổi chỗ độ dài
2. Nhưng một chu trình ba em (A muốn chỗ B, B muốn chỗ C, C muốn chỗ A) làm
**cả ba** cùng lên hạng, mà bộ đếm cặp đôi **không nhìn thấy**. Bộ đo mới tìm
chu trình **mọi độ dài**.

### Kết quả — seed mốc 42

| Bộ dữ liệu | Chu trình | Độ dài | Em cùng lên hạng | Cặp phá vỡ | Hạng TB |
|---|---|---|---|---|---|
| `vi_du_huong_dan` | **0** | — | 0 | 0 → 0 | 1,222 → 1,222 |
| `bo_sach` | **16** | **2, 3, 4** | **32** (22,9%) | 0 → **92** | 2,100 → 1,771 |
| `TEST_0*` | **5** | 2 | 10 (8,3%) | 0 → **49** | 1,611 → 1,509 |

**7 trong 16** chu trình của `bo_sach` dài hơn 2 — tức bộ đếm cặp đôi cũ bỏ sót
gần một nửa số cơ hội cải thiện.

### Quét 20 seed

| Bộ dữ liệu | Chu trình ít nhất / TB / nhiều nhất | Seed cho 0 chu trình | Seed có chu trình dài >2 |
|---|---|---|---|
| `vi_du_huong_dan` | 0 / 0,0 / 0 | **20 / 20** | 0 |
| `bo_sach` | 14 / **14,95** / 16 | **0 / 20** | **20 / 20** |
| `TEST_0*` | 5 / **5,4** / 6 | **0 / 20** | 0 |

**Đọc ra:**

1. **Kết quả KHÔNG tối ưu Pareto**, và điều đó ổn định qua mọi seed — không
   phải chuyện xui một lần.
2. **Cái giá đo được rõ ràng.** Đổi chỗ theo cả 16 chu trình thì 32 em lên
   hạng, hạng trung bình từ 2,100 xuống 1,771 — nhưng sinh ra **92 cặp phá
   vỡ**. Không có cách nào lấy phần lợi mà không trả phần giá đó.
3. `vi_du_huong_dan` **đạt tối ưu Pareto** (0 chu trình ở mọi seed). Nên đây
   không phải khuyết tật cố hữu của thuật toán — nó phụ thuộc dữ liệu.

> **Đừng lẫn hai khái niệm** — đây là chỗ giám khảo bắt lỗi được ngay:
>
> | | Gồm những ai | Nghĩa là gì |
> |---|---|---|
> | **Cặp phá vỡ** | 1 học sinh + 1 **CLB** | Kết quả **không ổn định** → **LỖI** |
> | **Chu trình cùng có lợi** | 2+ **học sinh** | Không tối ưu Pareto → **đánh đổi đã biết** |

---

## TN6 — "Ổn định" theo nghĩa BỀN

Chữ *ổn định* trong dự án có hai nghĩa không liên quan nhau: **stable** (không
có cặp phá vỡ — đúng/sai) và **bền** (rung dữ liệu thì kết quả đổi bao nhiêu —
định lượng). Nghĩa thứ hai chưa từng được đo ngoài phần đổi seed.

### `bo_sach` — 140 em

| Nhiễu | Phép thử | Em đổi CLB (ít / TB / nhiều) | % đổi TB | Phép thử không đổi gì | **Cặp phá vỡ** |
|---|---|---|---|---|---|
| Chỉ tiêu ±1 (mỗi CLB) | 24 | 0 / 1,17 / 3 | **0,83%** | 7 | **0** |
| Thêm 1 học sinh | 30 | 0 / 0,70 / 3 | **0,50%** | 18 | **0** |
| Bớt 1 học sinh | 30 | 0 / 1,77 / 5 | **1,27%** | 3 | **0** |
| Nhiễu điểm ±0,1 | 20 | 0 / 6,65 / 12 | 4,75% | 1 | **0** |
| Đổi seed bốc thăm | 20 | 2 / 6,10 / 11 | 4,36% | 0 | **0** |
| Nhiễu điểm ±0,5 | 20 | 15 / 21,20 / 29 | **15,14%** | 0 | **0** |

**Trên cả ba bộ dữ liệu: 392 phép thử, 0 cặp phá vỡ.**

**Đọc ra ba điều:**

1. **Nhiễu hành chính rất rẻ.** Thêm/bớt một em, xin thêm một suất — dưới
   **1,3%** số em bị ảnh hưởng. Kết quả đã công bố không bị lật.
2. **Điểm là thứ kéo mạnh nhất, đúng như thiết kế.** Nhiễu điểm ±0,5 xáo
   **15,1%** số em — gấp 3,5 lần đổi seed bốc thăm. Điều này **xác nhận** mệnh
   đề trung tâm của `GIAI_DAP_BOC_THAM`: bốc thăm chỉ đứng sau điểm.
   *Hệ quả cho người dùng: chấm điểm cẩn thận quan trọng hơn nhiều so với chọn
   seed nào.*
3. **Không nhiễu nào phá được tính ổn định.** Đây là ràng buộc cứng — nhiễu
   được phép đổi *ai vào đâu*, không được phép làm kết quả mất ổn định.

> Dòng "thêm 1 học sinh" ở đây **vẽ lại toàn bộ bộ số bốc thăm**, là kịch bản
> xấu nhất. Phần mềm thật không làm thế — nó khoá bộ số rồi chèn riêng cho em
> mới (`chen_stb_cho_hoc_sinh_moi`). Nên 0,50% là **cận trên**, không phải mức
> xáo trộn thật.

---

---

## TN7 — Trong ba thiết kế bốc thăm cho cả tuần, thiết kế nào tốt nhất?

Sáu thí nghiệm trên đều nói về việc xếp CLB cho **một** buổi. Khi phần mềm xếp
cho cả **tuần**, mỗi buổi vẫn là một lần chạy RB-DA độc lập, nhưng bộ số bốc
thăm dùng cho các buổi thì có ba cách dựng:

| Mã | Thiết kế | Cách dựng |
|---|---|---|
| **A1** `stb_tuan` | Bốc một lần cho cả tuần | Dùng thẳng bộ số đã khoá cho mọi buổi. Em bốc phải số xấu thì xấu ở **mọi** buổi — may rủi **cộng dồn**. |
| **A2** `stb_ngay` | Bốc lại mỗi buổi | Mỗi buổi một hoán vị dẫn xuất từ (seed, tên buổi). May rủi **độc lập** giữa các buổi. |
| **A3** `stb_co_bu` | Bốc thăm có bù | Trước mỗi buổi đánh lại số theo `(số CLB đã có, số gốc)` — em đang ít CLB được lên trước. |

Cả ba đều là **hàm của bộ số đã khoá**, nên cơ chế khoá bốc thăm còn nguyên ý
nghĩa ở cả ba. Dữ liệu chỉ có một buổi thì cả ba cho **cùng một kết quả**.

> **Phần mềm nay chỉ chạy A2, và bảng đo dưới đây là căn cứ.** Bộ chọn ba thiết
> kế đã bỏ; `api.run_pipeline` không còn nhận tham số chế độ. A1 và A3 vẫn nằm
> trong `rbda_priority_pipeline.py` để `do_boc_tham.py` đối chứng được — không
> có chúng thì mọi con số ở mục này mất khả năng tái lập. Vì một buổi thì cả ba
> trùng nhau, việc chốt A2 **không làm sai một con số nào ở TN1–TN6**.

### TN7a — Trên bộ dữ liệu 5 buổi, 200 seed, ghép cặp

Mỗi seed: bốc **một** bộ số, chạy cả ba thiết kế trên đúng bộ số đó. Nên chênh
lệch giữa ba dòng là chênh lệch của **thiết kế**, không phải của dữ liệu hay
của may rủi.

| Thiết kế | Em trắng tay cả tuần (TB) | ít nhất | nhiều nhất | CLB TB mỗi em | Độ lệch chuẩn | **Cặp phá vỡ** |
|---|---|---|---|---|---|---|
| A1 một lần cả tuần | **36,50** | 33 | 39 | 1,320 | 0,943 | **0** |
| A2 bốc lại mỗi buổi | **36,26** | 34 | 39 | 1,319 | 0,939 | **0** |
| A3 có bù | **35,69** | 33 | 38 | 1,316 | 0,928 | **0** |

*Mẫu số là **160 em có khai ít nhất một nguyện vọng**.*

> **Số đo này đã đổi so với bản công bố trước, và đây là lý do.** Bản trước ghi
> mẫu 156 em. Bốn em còn lại không phải "không khai gì" — các em CÓ khai, nhưng
> bước nạp khi ấy đếm nguyện vọng cho **cả tuần** với trần 10 và **bỏ qua trọn**
> học sinh vượt trần, nên bốn em bị gạt khỏi đợt xếp mà con số 156 không cho
> thấy. Trần nay tính theo **từng buổi**, bốn em vào được cuộc, và toàn bộ TN7a
> đã đo lại trên đúng 200 hạt giống cũ. TN7b, TN7c, TN7d không đổi — chúng
> không dùng bộ dữ liệu này.

| Cặp so | Hiệu TB | Khoảng tin cậy 95% | Số seed thắng–thua–hoà | Kết luận |
|---|---|---|---|---|
| A1 − A2 | **+0,245 em** | [+0,020 ; +0,465] | 63 – 90 – 47 | A2 tốt hơn |
| A1 − A3 | **+0,815 em** | [+0,730 ; +0,900] | 0 – 141 – 59 | A3 tốt hơn |

> **Đọc cho đúng chiều.** Hiệu được tính `A1 − A2` trên **số em trắng tay**, mà
> ít em trắng tay là tốt — nên **dương** nghĩa là A1 nhiều em trắng tay hơn, tức
> **A2 tốt hơn**. Nhãn này do `mo_ta_chieu()` sinh ra từ chính các biến đã dùng
> để tính hiệu, không gõ tay; `tests/test_boc_tham.py` có bốn test canh chiều dấu.

Hai điều đọc được từ bảng:

1. **Khoảng tin cậy không chứa 0**, nên chênh lệch là thật. Nhưng độ lớn là
   **0,245 em trên 160**, tức **0,15%**. Phân biệt được về thống kê, gần như
   không phân biệt được trên thực tế.
2. **Tổng số suất gần như không đổi**: 211,13 · 211,03 · 210,50. Không thiết kế
   nào **tạo thêm chỗ** — chúng chỉ đổi **ai** được chỗ.

### TN7b — Bỏ hẳn điểm: bốc thăm quyết định tất

200 em · 5 buổi · mọi em Tầng 2 · không CLB nào có suất dự trữ · 30 seed mỗi ô.
Số chỗ mỗi buổi tính ngược từ số em đã khai, nên tỉ lệ chọi ra **đúng** bằng
cột đầu.

| Tỉ lệ chọi | Em khai mấy buổi | A1 | A2 | A3 | **A2 cứu được** | KTC 95% của hiệu |
|---|---|---|---|---|---|---|
| 0,5× | 5 | 0,00 | 0,00 | 0,00 | 0,00 | [0,00 ; 0,00] |
| 0,5× | 3 | 0,00 | 0,00 | 0,00 | 0,00 | [0,00 ; 0,00] |
| 1,0× | 5 | 1,20 | 0,00 | 0,00 | **+1,20** | [+0,80 ; +1,63] |
| 1,0× | 3 | 5,37 | 0,70 | 0,00 | **+4,67** | [+3,83 ; +5,53] |
| 1,5× | 5 | 14,17 | 0,80 | 0,00 | **+13,37** | [+12,40 ; +14,27] |
| 1,5× | 3 | 27,77 | 6,93 | 0,00 | **+20,83** | [+19,50 ; +22,23] |
| 2,0× | 5 | 54,73 | 5,73 | 0,00 | **+49,00** | [+46,57 ; +51,40] |
| 2,0× | 3 | 66,93 | 24,57 | 1,17 | **+42,37** | [+40,50 ; +44,23] |
| 4,0× | 5 | 126,70 | 47,67 | 0,00 | **+79,03** | [+77,03 ; +81,20] |
| 4,0× | 3 | 132,20 | 85,50 | 50,03 | **+46,70** | [+44,67 ; +48,73] |

**300 lần chạy, 0 cặp phá vỡ ở cả ba thiết kế.**

Hai ô **0,5×** ra 0 ở cả ba cột: thừa chỗ thì không em nào trắng tay, bốc thăm
thế nào cũng vậy. Hai ô đó là chốt soát chính bộ đo — một bộ đo bịa ra chênh
lệch thì đã không cho 0 ở đây.

Từ **1,0×** trở lên, A2 hơn A1 ở **mọi** ô, và khoảng tin cậy không ô nào chứa
0. Số CLB trung bình mỗi em thì **trùng nhau tới chữ số thứ ba** ở cả ba cột
(ví dụ ô 1,5×/5 buổi: 3,294 · 3,297 · 3,296).

### TN7c — Vì sao bộ dữ liệu của trường lại gần như không phân biệt được?

TN7a và TN7b lệch nhau quá xa để bỏ qua: cùng một thiết kế, cùng một phần mềm,
mà chênh lệch là 0,30 em ở bảng trước và 79 em ở bảng sau. Khác biệt giữa hai
bộ dữ liệu là **điểm**: bộ mẫu của trường có điểm, dữ liệu TN7b thì không.

TN7c vặn đúng núm đó. Chọi giữ cố định 1,5×, 5 buổi, 30 seed mỗi ô.

**c1 — Vặn tỉ lệ em CÓ ĐIỂM:**

| Tỉ lệ em Tầng 1 | A1 | A2 | A3 | Lợi thế A2 | = mấy phần số em A1 bỏ lại |
|---|---|---|---|---|---|
| 0% | 13,77 | 1,03 | 0,00 | **+12,73** | **92%** |
| 10% | 12,90 | 1,17 | 0,00 | +11,73 | 91% |
| 25% | 12,97 | 3,23 | 0,00 | +9,73 | 75% |
| 50% | 13,60 | 8,13 | 1,37 | +5,47 | 40% |
| 75% | 10,33 | 8,37 | 6,13 | +1,97 | 19% |
| 90% | 5,57 | 5,37 | 3,97 | +0,20 | 4% · *không phân biệt được* |
| 100% | 0,87 | 0,70 | 0,03 | +0,17 | *không phân biệt được* |

*Cột cuối ở mốc 100% đọc ra 19% nếu tính máy móc, nhưng ở mốc đó A1 chỉ còn bỏ
lại **0,87** em — tỉ lệ bị chia cho một mẫu số quá nhỏ nên không có nghĩa. Lợi
thế tuyệt đối ở đó là **+0,17** em và khoảng tin cậy chứa 0.*

**c2 — Vặn độ mịn của thang điểm** (mọi em đều có điểm):

| Thang điểm | A1 | A2 | A3 | Lợi thế A2 | = mấy phần số em A1 bỏ lại |
|---|---|---|---|---|---|
| 1 mức (hoà hết) | 13,10 | 1,17 | 0,00 | **+11,93** | **91%** |
| 2 mức | 1,97 | 0,87 | 0,20 | +1,10 | 56% |
| 4 mức | 1,23 | 0,87 | 0,33 | +0,37 | 30% |
| 11 mức | 0,70 | 0,53 | 0,40 | +0,17 | *không phân biệt được* |
| 61 mức | 1,03 | 1,03 | 1,00 | **0,00** | *không phân biệt được* |

Cột cuối là cột phải đọc. Cột tuyệt đối có một chỗ dễ đọc nhầm: khi tỉ lệ Tầng 1
tăng thì số em trắng tay của **cả hai** thiết kế cùng giảm, nên lợi thế tuyệt
đối giảm theo mà chưa chắc vì bốc thăm hết việc. Cột tỉ lệ hỏi đúng câu cần
hỏi: **trong số em mà A1 bỏ lại, A2 cứu được bao nhiêu phần?** — và nó đi từ
92% xuống tới không phân biệt được, trên cả hai núm.

### TN7d — A3 có mở kênh khai gian không?

`stb_co_bu` làm ưu tiên buổi sau phụ thuộc **kết cục** buổi trước, mà kết cục
lại phụ thuộc nguyện vọng đã khai. Bảng này dò xem điều đó có thành một cách
khai gian dùng được không: với mỗi em, thử **giấu bớt** — giấu hẳn một tập con
các buổi, hoặc cắt ngắn danh sách trong một buổi — rồi chấm lại bằng nguyện
vọng **thật**.

60 em · 4 buổi · mọi em Tầng 2 · 12 thể hiện × 25 em = **300 lượt**.

| Thiết kế | Em đã thử | **Em giấu bớt có lợi** | Tỉ lệ |
|---|---|---|---|
| A1 một lần cả tuần | 300 | **0** | 0% |
| A2 bốc lại mỗi buổi | 300 | **0** | 0% |
| A3 có bù | 300 | **113** | **37,7%** |

**Đối chứng ngược nằm ở chính cột đó:** A3 phải khác 0. Nếu A3 cũng ra 0 thì bộ
dò hỏng, và hai số 0 của A1/A2 không nói lên điều gì.

Một ví dụ tìm được (em `E0001`, dưới A3):

```
khai thật   buổi 1: [clb2, clb1]   buổi 2: [clb3]   buổi 3: [clb1, clb2, clb3]   buổi 4: [clb2]
            -> điểm từng buổi  0 · 1 · 2 · 0   = 3
giấu buổi 2 buổi 1: [clb2, clb1]                    buổi 3: [clb1, clb2, clb3]   buổi 4: [clb2]
            -> điểm từng buổi  0 · 0 · 3 · 1   = 4
```

Em bỏ suất ở buổi 2, đổi lấy nguyện vọng 1 ở buổi 3 (thay vì nguyện vọng 2) và
một suất ở buổi 4 (thay vì trắng).

> **Phạm vi của bảng này.** Kênh được dò là kênh *giấu bớt*; hoán vị thứ tự
> nguyện vọng **trong** một buổi không thử ở đây vì TN3 đã vét cạn nó (0/1 400).
> Với A3, tìm **thấy** một cách là đủ kết luận, nên việc giới hạn không gian
> không làm yếu kết luận về A3.
>
> Kênh của A3 là kênh **đánh đổi**, không phải kênh lợi không mất gì: muốn giữ
> "số CLB đã có" bằng 0 để lên trước ở buổi sau thì phải **bỏ** một suất ở buổi
> trước. Phép dò không tìm được cách nào không kém ở buổi nào mà hơn ở ít nhất
> một buổi — và con số 0 đó **không** phải bằng chứng A3 an toàn, nó là hệ quả
> của chính cách khai gian.

---

## Tổng hợp: bốn nghĩa của "tốt nhất"

| Nghĩa | Đạt? | Bằng chứng |
|---|---|---|
| Tốt nhất trong các cách ghép **ổn định** | ✅ **Có** | 2 088 thể hiện vét cạn, 0 phản ví dụ |
| **Tối ưu Pareto** | ❌ **Không** | 16 chu trình, 32/140 em có thể cùng lên hạng |
| **Khai thật có lợi nhất** | ✅ **Có** | 0/1 400 em khai gian được (Boston: 258) |
| **Bền** trước nhiễu | ✅ **Có** | 392 phép thử, 0 cặp phá vỡ; nhiễu hành chính < 1,3% |

**Hai nghĩa đầu không thể cùng đạt.** Đó không phải khuyết điểm của bản cài
đặt này mà là đặc điểm của **mọi** thuật toán ghép cặp giữ tính ổn định: khi
CLB có ưu tiên thật (điểm thi) và ưu tiên đó không trùng nguyện vọng học sinh,
giữ ổn định buộc phải từ chối một số cơ hội đổi chỗ cùng có lợi.

Bảng TN4 cho thấy chỗ đánh đổi đó nằm ở đâu: **cơ chế nào cũng thắng ở vài
cột và thua ở vài cột khác.** Không có dòng nào tốt nhất mọi cột.

---

## Giới hạn của nghiên cứu này — đọc trước khi trích

1. **Vét cạn chỉ chạy được ở quy mô nhỏ** (7 em / 4 CLB). Kết luận TN1 là
   *"không tìm được phản ví dụ trong 2 088 thể hiện nhỏ"*, **không phải** một
   chứng minh toán học cho mọi quy mô.
2. **TN3 trên bộ dữ liệu lớn có chặn không gian tìm kiếm.** Chỉ TN3a là vét
   cạn.
3. **Ba bộ dữ liệu đều là mô phỏng do máy sinh.** `bo_sach` còn được **cố ý
   dựng cho chật** để thuật toán phải làm việc — nó không mô phỏng một phân bố
   nguyện vọng tự nhiên. Trình bày các con số này như số liệu khảo sát thật là
   **bịa đặt dữ liệu**.
4. **Tất cả đo ở một cấu hình dự trữ.** Đổi `reserve_group` hay chính sách xét
   dự trữ thì phải đo lại.
5. **TN7b, TN7c, TN7d chạy trên dữ liệu do máy dựng theo tham số**, không phải
   trên một trường có thật. Ba bảng đó trả lời câu *"cơ chế hành xử thế nào khi
   vặn núm này"*, **không** trả lời câu *"trường X nên chọn thiết kế nào"* — câu
   sau phải đo trên dữ liệu của chính trường X, và phần mềm có sẵn bảng đối
   chiếu ba thiết kế cho việc đó (`so_sanh_boc_tham`, tab **01 Vận hành**).
6. **TN7d chỉ dò một kênh khai gian** (giấu bớt buổi). "Không tìm thấy" ở A1 và
   A2 vì thế yếu hơn "không tồn tại"; kết luận về A3 thì không bị ảnh hưởng, vì
   tìm thấy được một cách là đủ.

---

## Tệp liên quan

| Tệp | Nội dung |
|---|---|
| `du_lieu_test/co_che_doi_chung.py` | Thư viện 4 cơ chế đối chứng + vét cạn tập ổn định |
| `du_lieu_test/do_toi_uu_on_dinh.py` | TN1, TN2, TN4, TN5 |
| `du_lieu_test/do_khai_that.py` | TN3 |
| `du_lieu_test/do_ben_vung.py` | TN6 |
| `du_lieu_test/do_boc_tham.py` | TN7 |
| `du_lieu_test/so_lieu_*.json` | Số liệu thô — nguồn sự thật duy nhất |
| `tests/test_toi_uu_on_dinh.py` | 29 test canh, gồm nhóm đối chứng ngược |
| `tests/test_boc_tham.py` | 23 test canh cho TN7, gồm nhóm canh **chiều dấu** |
| `KE_HOACH_NHIEU_BUOI.md` | Thiết kế phần nhiều buổi và ba thiết kế bốc thăm |
| `CO_CHE_THUAT_TOAN.md` | Năm lớp cơ chế của phần mềm |
| `GIAI_DAP_BOC_THAM.md` | Bốc thăm STB — công bằng và tái lập |
| `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` mục 3d | Cặp đôi cùng có lợi (bản đếm cũ, độ dài 2) |

---

**Về dữ liệu dùng để đo.** Toàn bộ học sinh trong các phép đo trên là **dữ liệu
mô phỏng do máy sinh ra**, không phải học sinh có thật. Các mã như *HS001,
E00…* chỉ là mã đánh số tự động.

*Tệp này chỉ trình bày **số đo và cơ chế**. Phần nhận định, diễn giải ý nghĩa
khoa học, phần Kết luận và phần Tính mới — người thực hiện đề tài tự viết
(Phụ lục 1). Cái giá đo được ở TN5 có chấp nhận được không, trường nên chọn cơ
chế nào — đó là câu hỏi của người viết báo cáo, không phải của bộ đo.*
