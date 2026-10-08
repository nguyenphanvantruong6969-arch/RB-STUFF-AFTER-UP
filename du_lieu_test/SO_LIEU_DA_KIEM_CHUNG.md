# Số liệu đã kiểm chứng

> ### ⚠️ TOÀN BỘ SỐ Ở ĐÂY ĐO TRÊN **DỮ LIỆU MÔ PHỎNG**
> 120 học sinh do máy sinh (`tao_du_lieu_test.py`, seed 2026), **không phải khảo
> sát học sinh có thật**. Hơn nữa bộ này được **cố ý thiết kế cho cạnh tranh cao**
> để cơ chế thuật toán lộ ra — nó **không** mô phỏng một phân bố nguyện vọng tự
> nhiên. Trình bày các con số này như số liệu khảo sát thật là **bịa đặt dữ liệu**.

Đây là **số đo thô**, kèm cách đo lại. Phần nhận xét, giải thích ý nghĩa và kết
luận — **học sinh tự viết**, AI không tham gia.

Tái lập mọi số dưới đây:

```bash
./.venv/bin/python du_lieu_test/tao_du_lieu_test.py   # sinh lại 4 tệp Excel
./.venv/bin/python du_lieu_test/tao_db_demo.py        # dựng lại CSDL demo
./.venv/bin/python -m pytest -q                       # chạy bộ kiểm thử
```

---

## 1. Quy mô bài toán

| Đại lượng | Giá trị |
|---|---|
| Học sinh | 120 |
| Câu lạc bộ | 10 |
| Tổng chỉ tiêu | 130 chỗ |
| Trong đó là suất dự trữ | 12 chỗ (ở 4 CLB, đều là CLB đông người đăng ký) |
| Lượt đăng ký thi | 396 |
| Ô điểm nạp thẳng từ tệp Excel | 396 |
| Học sinh thuộc diện dự trữ | 26 em — `chinh_sach` 19, `khoi_10` 7 |
| Học sinh không thuộc diện nào | 94 em |

## 2. Kết quả phân bổ

Chạy với `seed = 42`. Điểm nằm sẵn trong cột `score_*` của `TEST_02`, **không
chấm tay ô nào**.

| Đại lượng | Giá trị |
|---|---|
| Được xếp | **108 / 120** |
| Chưa được xếp | 12 |
| Số vòng lặp thuật toán | 7 |
| Thời gian chạy | **0,011 giây** (cả 5 bước, gồm sao lưu và xuất tệp) |
| Tổng chỗ được dùng | 108 / 130 |
| Cảnh báo dữ liệu trước khi chạy | **0** |

### Được xếp theo nguyện vọng thứ mấy

| Nguyện vọng | Số em | Tỉ lệ trên số em được xếp |
|---|---|---|
| Thứ 1 | **64** | 59% |
| Thứ 2 | 28 | 26% |
| Thứ 3 | 10 | 9% |
| Thứ 4 | 6 | 6% |

### Diện trúng tuyển

| Diện | Số em |
|---|---|
| Thường (`general`) | 98 |
| Dự trữ (`reserve`) | **10** |

*10 trong 12 suất dự trữ được dùng tới. 26 em thuộc diện dự trữ, 10 em trong số đó
vào được **qua suất dự trữ**; số còn lại vào bằng điểm thường hoặc không được xếp.*

### Lấp đầy từng CLB

| Mã CLB | Đã xếp / Chỉ tiêu | Suất dự trữ | Tình trạng |
|---|---|---|---|
| `clb_bongda` | 20 / 20 | 4 | Đầy |
| `clb_tienganh` | 16 / 16 | 2 | Đầy |
| `clb_mythuat` | 12 / 12 | 3 | Đầy |
| `clb_tinhoc` | 12 / 12 | 3 | Đầy |
| `clb_amnhac` | 13 / 14 | 0 | thừa 1 |
| `clb_bongro` | 13 / 18 | 0 | thừa 5 |
| `clb_robotics` | 7 / 8 | 0 | thừa 1 |
| `clb_vanhoc` | 8 / 10 | 0 | thừa 2 |
| `clb_khoahoc` | 2 / 8 | 0 | thừa 6 |
| `clb_tinhnguyen` | 5 / 12 | 0 | thừa 7 |

Tệp xuất ra: **120 dòng** trong tệp tổng, **11 tệp** theo CLB (10 CLB + 1 tệp
`_chua_duoc_xep.csv`).

## 3. Tốc độ ở quy mô lớn hơn

Dữ liệu sinh ngẫu nhiên, đo trên cùng một máy:

| Quy mô | Nạp dữ liệu | Chạy phân bổ | Kết quả | Số vòng |
|---|---|---|---|---|
| 120 học sinh / 10 CLB | — | 0,011 s | 108/120 | 7 |
| 500 học sinh / 20 CLB | 0,03 s | 0,03 s | 500/500 | 21 |
| 2 000 học sinh / 40 CLB | 0,10 s | 0,14 s | 1 994/2 000 | 33 |

## 3b. Thử tải ở quy mô lớn

Bảng ở mục 3 chỉ là ba điểm đo. Bộ thử tải đầy đủ — **204 lần chạy**, quét số học
sinh, số CLB, số nguyện vọng, tổng chỉ tiêu và cách chia chỉ tiêu — nằm ở
`du_lieu_test/thu_tai/`, số liệu thô trong `ket_qua_thu_tai.csv`.

**Cố ý không chép số sang đây.** Chép là tạo ra hai bản dễ lệch nhau; đọc thẳng
tệp CSV hoặc trang báo cáo.

## 3c. Ảnh hưởng của seed bốc thăm

Chạy lại toàn bộ quy trình với **200 seed** (1–200) trên cùng một bộ dữ liệu, lấy
seed 42 làm mốc rồi đếm số em xếp khác mốc.

| Bộ dữ liệu | Số em | **Không bao giờ đổi** | Đổi CLB: ít nhất / TB / nhiều nhất | Số em được xếp | Cặp phá vỡ |
|---|---|---|---|---|---|
| `vi_du_huong_dan/` | 10 | **10 (100%)** | 0 / 0,0 / 0 | 9 – 9 | 0 |
| `bo_sach/` | 140 | **127 (90,7%)** | 0 / 6,0 / 11 | 139 – 140 | 0 |
| `TEST_0*.xlsx` | 120 | **116 (96,7%)** | 0 / 1,9 / 4 | 107 – 109 | 0 |

Khoá xếp hạng của mỗi CLB là `(-điểm, số_bốc_thăm)`
(`rbda_priority_pipeline.club_priority_order`) — **điểm đứng trước**, nên seed chỉ
chen vào được đúng hai chỗ: em **hoà điểm**, và em dự tuyển CLB mình **không thi**
(tầng 2). Số đo khớp: trên cả ba bộ, **không một em nào** đổi chỗ mà lại nằm
ngoài hai nhóm đó.

`vi_du_huong_dan/` là ca đối chứng sạch nhất: bộ này **không có em hoà điểm và
không có em tầng 2**, và kết quả là **0 em đổi chỗ trên cả 200 seed**.

### Seed có đổi được việc một em CÓ SUẤT hay không?

Có — và đây là câu hỏi quan trọng hơn hẳn chuyện đổi CLB. Đổi CLB là đổi chỗ
ngồi; mất suất là ra khỏi cuộc chơi. Đã tách ra đếm riêng:

| Bộ dữ liệu | Luôn có suất | Luôn không có suất | **Bấp bênh — seed quyết định** |
|---|---|---|---|
| `vi_du_huong_dan/` (10 em) | 9 (90,0%) | 1 (10,0%) | **0 (0,0%)** |
| `bo_sach/` (140 em) | 139 (99,3%) | 0 | **1 (0,7%)** |
| `TEST_0*` (120 em) | 107 (89,2%) | 11 (9,2%) | **2 (1,7%)** |
| **Gộp ba bộ (270 em)** | | | **3 (1,1%)** |

Ba em đó, và chỉ ba em đó, là toàn bộ chỗ mà may rủi quyết định chuyện có suất
hay không. Phân bố số em được xếp trên 200 seed:

| Bộ | Phân bố |
|---|---|
| `vi_du_huong_dan/` | 9 em: **200/200 seed** — không dao động chút nào |
| `bo_sach/` | 139 em: 46 seed · 140 em: 154 seed |
| `TEST_0*` | 107 em: 49 · 108 em: 101 · 109 em: 50 |

### Trong trường hợp nào thì một em rơi vào nhóm bấp bênh

Theo dấu từng em qua 200 seed:

| Em | Nguyện vọng | Kết cục |
|---|---|---|
| `HS122` (bộ sạch) | 6 nguyện vọng | `clb_vanhoc` **154/200** (77%) · không suất **46/200** (23%) |
| `HS037` (TEST) | **chỉ 2 nguyện vọng** | `clb_bongda` **107/200** (54%) · không suất **93/200** (46%) |
| `HS045` (TEST) | 4 nguyện vọng | không suất **106/200** (53%) · `clb_mythuat` **94/200** (47%) |

Điểm chung: em đó bị từ chối hết các nguyện vọng trên, **rơi xuống nguyện vọng
cuối cùng còn với tới được**, và ở đúng đó lại đứng ngay ranh giới chỉ tiêu
trong một nhóm hoà nhau. Thua lượt bốc thăm ở chỗ đó thì **không còn nguyện
vọng nào phía dưới** để rơi tiếp — nên mất suất luôn.

`HS122` rơi tới nguyện vọng thứ **5** (`clb_vanhoc`, một CLB em không thi, tức
tầng 2 xếp thuần theo bốc thăm). `HS037` chỉ có **2** nguyện vọng nên không có
lưới nào đỡ.

**Một điều đã thử và KHÔNG kết luận được:** ranh giới này **không** đoán trước
được bằng cách so điểm thô. Ví dụ `HS122` ở `clb_tinhoc` có 34 em điểm cao hơn
trong khi chỉ tiêu là 14 — nhìn tĩnh thì em đứng ngoài rất xa, nhưng phần lớn
34 em kia lại đỗ nguyện vọng trên của họ, nên ranh giới thật tụt xuống tới em.
Ranh giới ở đây **sinh ra từ chuỗi dây chuyền** của thuật toán, không phải từ
bảng điểm. Bộ dò ranh giới tĩnh đã viết thử **không bắt được ca nào**.

### "Nguyện vọng càng ngắn càng dễ bấp bênh" — đã kiểm, và chỉ đúng một nửa

Cả ba em bấp bênh đều ở bộ có nguyện vọng ngắn hơn, và `HS037` chỉ có 2 nguyện
vọng. Ba ca thì chưa kết luận được, nên làm thí nghiệm đối chứng: **cùng bộ sạch,
cùng điểm, cùng chỉ tiêu — chỉ cắt danh sách nguyện vọng của mọi em xuống k**,
50 seed mỗi mức.

| Cắt còn | Em **chưa được xếp** (TB) | Nhiều nhất | Em **bấp bênh** |
|---|---|---|---|
| 1 nguyện vọng | **48,0** | 48 | 2 (1,4%) |
| 2 nguyện vọng | 26,2 | 27 | 7 (5,0%) |
| 3 nguyện vọng | 14,8 | 16 | 3 (2,1%) |
| 4 nguyện vọng | 7,5 | 8 | 3 (2,1%) |
| 5 nguyện vọng | 1,2 | 3 | 4 (2,9%) |
| 6 nguyện vọng | **0,3** | 1 | 1 (0,7%) |

**Hai cột cuối kể hai câu chuyện khác nhau, đừng gộp:**

- **Chưa được xếp**: hiệu ứng rất mạnh và rất đều — **48 → 0,3**.
- **Bấp bênh**: **không có quy luật nào** — 1,4 / 5,0 / 2,1 / 2,1 / 2,9 / 0,7,
  nhảy loạn. Danh sách dài hơn **không** làm em bớt bấp bênh.

Phỏng đoán ban đầu **đúng mạnh** cho vế thứ nhất, **sai** cho vế thứ hai.

> **⚠️ Đừng đọc bảng này thành "bắt học sinh điền tối đa số CLB".** Thí nghiệm
> **CẮT BỚT** nguyện vọng của em vốn đã khai đủ, tức nó đo *"em mất gì khi không
> khai hết những CLB mình VẪN CHẤP NHẬN"*. Nó **không** đo chuyện thêm CLB em
> **không** muốn — mà thêm CLB không muốn thì em có thể bị xếp đúng vào đó, và
> với em như thế còn tệ hơn không có suất. Xem `BAN_GIAO.md` mục 5, khối "CẢNH
> BÁO DIỄN GIẢI".

```
python du_lieu_test/do_do_dai_nguyen_vong.py
```

Còn một điều nữa:

- **Mọi seed đều cho 0 cặp phá vỡ.** Đổi seed đổi *ai* được suất trong nhóm hoà
  nhau, chứ không bao giờ làm kết quả mất tính ổn định.

Trên `bo_sach/` thì 138/140 em có hoà điểm ở đâu đó và cả 140 em đều có ít nhất
một CLB mình không thi, nên câu "không em nào đổi ngoài hai nhóm" ở bộ này gần
như hiển nhiên. Bằng chứng mạnh nằm ở `vi_du_huong_dan/` và ở test dựng riêng
(`tests/test_anh_huong_seed.py`), nơi ba em ba điểm khác nhau tranh hai suất và
**100 seed đều cho cùng một kết quả**.

```
python du_lieu_test/do_anh_huong_seed.py --so-seed 200
```

Chạy hai lần ra **đúng cùng một bảng** — đã kiểm.

> Ba câu hỏi hay gặp về **bản thân phép bốc thăm** (đổi seed có còn công
> bằng không, thứ tự nhập có ảnh hưởng không, những gì ảnh hưởng tới bộ
> số) được trả lời riêng, kèm số đo, ở **`docs/GIAI_DAP_BOC_THAM.md`**.

## 3d. Cái giá của tính ổn định — cặp đôi cùng có lợi

Mục 3c hỏi *"seed đổi thì ai đổi chỗ"*. Mục này hỏi câu khác và khó hơn: **kết
quả ổn định rồi, nhưng có tốt nhất cho học sinh không?**

> **Cặp đôi cùng có lợi** — em `s1` xếp CLB `c1`, em `s2` xếp CLB `c2`, mà `s1`
> thích `c2` hơn **và** `s2` thích `c1` hơn. Đổi chỗ thì **cả hai cùng lên**.
>
> **Không phải cặp phá vỡ.** Cặp phá vỡ gồm 1 học sinh + 1 **câu lạc bộ**, và có
> nghĩa là kết quả **sai**. Cặp đôi cùng có lợi gồm 2 **học sinh**, và có nghĩa
> là kết quả **không tối ưu Pareto** — đánh đổi đã biết của cả họ thuật toán ghép
> cặp ổn định.

### Seed mốc 42

| Bộ | Cặp phá vỡ | Cặp đôi cùng có lợi | Số em dính | Bốc thăm CÓ phần | Bốc thăm VÔ CAN |
|---|---|---|---|---|---|
| `vi_du_huong_dan/` (10 em) | 0 | **0** | 0 | — | — |
| `bo_sach/` (140 em) | 0 | **85** | 34 (24,3%) | 18 (21%) | **67 (79%)** |
| `TEST_0*` (120 em) | 0 | **19** | 16 (13,3%) | 2 (11%) | **17 (89%)** |

### Quét 40 seed

| Bộ | Cặp phá vỡ | Ít nhất · TB · Nhiều nhất | Số seed cho 0 cặp |
|---|---|---|---|
| `vi_du_huong_dan/` | 0 ở mọi seed | 0 · 0,0 · 0 | 40 / 40 |
| `bo_sach/` | 0 ở mọi seed | 82 · **91,0** · 103 | **0 / 40** |
| `TEST_0*` | 0 ở mọi seed | 19 · **21,5** · 24 | **0 / 40** |

### Thí nghiệm đối chứng — bỏ điểm để đẩy học sinh xuống Tầng 2

Bỏ điểm của `p%` số cặp (em, CLB) thì các em đó tụt xuống **Tầng 2**, nơi bốc
thăm quyết định **hoàn toàn**. Nếu bốc thăm sinh ra tổn thất thì số cặp phải
**tăng**. 10 seed mỗi mức.

| Bỏ điểm | `bo_sach` cặp đôi (TB) | bốc thăm có phần | `TEST_0*` cặp đôi (TB) | bốc thăm có phần |
|---|---|---|---|---|
| 0% | **90,2** | 18,4 (20%) | **21,1** | 2,0 (9%) |
| 25% | 65,3 | 7,9 (12%) | 20,0 | 4,0 (20%) |
| 50% | 58,5 | 29,4 (50%) | 41,5 | 33,9 (82%) |
| 75% | 45,2 | 41,2 (91%) | 29,5 | 29,3 (99%) |
| **100%** | **4,1** | 4,1 (100%) | **2,2** | 2,2 (100%) |

Ở mức bỏ hết điểm, bốc thăm quyết định 100% — mà số cặp lại **ít nhất**, và
`TEST_0*` còn có **3/10 seed cho 0 cặp** (tối ưu Pareto). Khi điểm còn nguyên thì
**không seed nào** trong 40 làm được điều đó.

**Hai giới hạn của phép đo này, ghi để không ai trích thiếu:**

- Các mức **ở giữa không đi một chiều** — chỉ hai đầu bảng mới đọc ra được.
- Trên ba bộ này **Tầng 2 rất hiếm khi giữ suất**: `bo_sach/` có **8** em giữ
  suất ở CLB mình không thi, `TEST_0*` có **0**. Nên cả 18 và 2 cặp *"bốc thăm có
  phần"* đều đến từ **hoà điểm**. Thí nghiệm ở trên tồn tại chính vì lý do đó.

```
python du_lieu_test/do_danh_doi_on_dinh.py
```

Có **24 test canh** con số này: `tests/test_danh_doi_on_dinh.py`. Diễn giải đầy
đủ ở `docs/CO_CHE_THUAT_TOAN.md` và `BAN_GIAO.md` mục 5.

## 3e. Thuật toán có đưa ra cặp ghép TỐT NHẤT không?

Mục 3d ở trên đếm **cặp đôi cùng có lợi** — triệu chứng của việc không tối ưu
Pareto. Nhưng nó chưa trả lời được câu gốc: *kết quả này có phải cách ghép tốt
nhất không?* Sáu thí nghiệm mới trả lời câu đó, đầy đủ ở
**`docs/NGHIEN_CUU_TOI_UU.md`** (bản có biểu đồ: `docs/NGHIEN_CUU_TOI_UU.html`).

Chữ "tốt nhất" có bốn nghĩa, và một cơ chế có thể đạt nghĩa này mà hỏng nghĩa
kia:

| Nghĩa | Đạt? | Số đo |
|---|---|---|
| Tốt nhất trong các cách ghép **ổn định** | ✅ **Có** | 0 phản ví dụ / **2 088** thể hiện vét cạn |
| **Tối ưu Pareto** | ❌ **Không** | 16 chu trình · 32/140 em cùng lên hạng được |
| **Khai thật có lợi nhất** | ✅ **Có** | 0 / **1 400** em khai gian được (Boston: 258) |
| **Bền** trước nhiễu | ✅ **Có** | 0 cặp phá vỡ / **392** phép thử nhiễu |

Bốn con số đáng chú ý nhất:

1. **Suất dự trữ KHÔNG phá tính tối ưu.** Vét cạn toàn bộ tập ổn định trên
   1 073 thể hiện *có* dự trữ: RB-DA tối ưu ở **1 073/1 073**. Đáng ngạc nhiên,
   vì dự trữ *có* phá được mô hình một-danh-sách `Q_j` (mục "hai cảnh dự trữ"
   trong `docs/CO_CHE_THUAT_TOAN.md`).
2. **Tập em CÓ SUẤT là bất biến** ở mọi ma trận ổn định (240/240 thể hiện khó).
   Hệ quả: **đổi sang cơ chế ổn định khác không cứu được em nào đang trượt** —
   nó chỉ đổi *ai vào CLB nào*.
3. **Bốc thăm KHÔNG phải thứ kéo mạnh.** Nhiễu điểm ±0,5 xáo **15,14%** số em;
   đổi seed bốc thăm chỉ xáo **4,36%**. Xác nhận mệnh đề trung tâm của
   `GIAI_DAP_BOC_THAM`: bốc thăm chỉ đứng sau điểm.
4. **Boston cho 92 em nguyện vọng 1 còn RB-DA chỉ cho 54** — nhưng Boston tạo
   50 cặp phá vỡ và **18,43%** số em khai gian được dưới nó. Nên *"tỉ lệ được
   nguyện vọng 1"* một mình **không phải** thước đo chất lượng.

Bảng năm cơ chế trên `bo_sach` (140 em, seed 42):

| Cơ chế | NV1 | NV2 | NV3+ | Trượt | Hạng TB | Cặp phá vỡ |
|---|---|---|---|---|---|---|
| **RB-DA (phần mềm)** | 54 | 46 | 40 | 0 | 2,100 | **0** |
| DA do CLB đề xuất | 54 | 46 | 40 | 0 | 2,100 | **0** |
| Boston / nhận ngay | 92 | 14 | 32 | 2 | 1,826 | 50 |
| Xét theo bốc thăm | 81 | 24 | 33 | 2 | 1,928 | 121 |
| TTC | 80 | 29 | 31 | 0 | 1,879 | 118 |

Trên cả ba bộ, **DA do học sinh đề xuất và DA do CLB đề xuất cho kết quả giống
hệt nhau ở 20/20 seed** — tức tập ổn định chỉ có đúng một phần tử. Đó là tính
chất của dữ liệu (điểm thi làm ưu tiên rất phân tán), không phải của bộ đo:
test canh dựng một ví dụ nơi hai bản **khác nhau**.

```
python3 du_lieu_test/do_toi_uu_on_dinh.py
python3 du_lieu_test/do_khai_that.py
python3 du_lieu_test/do_ben_vung.py
python3 du_lieu_test/do_boc_tham.py
```

Số liệu thô: `du_lieu_test/so_lieu_toi_uu.json`, `so_lieu_khai_that.json`,
`so_lieu_ben_vung.json`, `so_lieu_boc_tham.json` — bốn tệp này là **nguồn sự
thật duy nhất**, mọi bảng đọc từ đó. Có **52 test canh**:
`tests/test_toi_uu_on_dinh.py` và `tests/test_boc_tham.py`, trong đó một nhóm
**đối chứng ngược** đỏ ngay nếu bộ đếm cặp phá vỡ hoặc bộ dò khai gian hỏng
thành "lúc nào cũng báo 0".

## 3f. Ba thiết kế bốc thăm cho thời khoá biểu tuần

Khi phần mềm xếp CLB cho cả tuần, bộ số bốc thăm dùng cho các buổi có ba cách
dựng: **A1** bốc một lần cho cả tuần · **A2** bốc lại mỗi buổi · **A3** bốc
thăm có bù (em đang ít CLB được lên trước). Đầy đủ ở **TN7** trong
`docs/NGHIEN_CUU_TOI_UU.md`.

**Trên bộ dữ liệu 5 buổi (160 em có khai, 200 seed, ghép cặp theo seed):**

| Thiết kế | Em trắng tay cả tuần | CLB TB mỗi em | Cặp phá vỡ |
|---|---|---|---|
| A1 một lần cả tuần | **36,50** | 1,320 | **0** |
| A2 bốc lại mỗi buổi | **36,26** | 1,319 | **0** |
| A3 có bù | **35,69** | 1,316 | **0** |

Hiệu A1 − A2 = **+0,245 em**, khoảng tin cậy 95% **[+0,020 ; +0,465]**. Không chứa
0 nên chênh lệch là thật, nhưng **0,245 trên 160 em là 0,15%** — phân biệt được
về thống kê, gần như không phân biệt được trên thực tế.

> **Số này đã đo lại.** Bản trước ghi mẫu **156 em**. Bốn em còn lại CÓ khai
> nguyện vọng, nhưng bước nạp khi ấy đếm nguyện vọng cho *cả tuần* với trần 10
> và bỏ qua trọn học sinh vượt trần, nên bốn em bị gạt khỏi đợt xếp mà con số
> 156 không cho thấy. Trần nay tính theo *từng buổi*; TN7a đo lại trên đúng 200
> hạt giống cũ, và kết luận không đổi — khoảng tin cậy vẫn không chứa 0. TN7b,
> TN7c, TN7d không dùng bộ dữ liệu này nên giữ nguyên từng ký tự.

**Bốn con số đáng chú ý:**

1. **Không thiết kế nào tạo thêm chỗ.** Tổng số suất: 211,13 · 211,03 · 210,50.
   Chúng chỉ đổi *ai* được chỗ, không đổi *bao nhiêu* chỗ.
2. **Khi bỏ hẳn điểm thì chênh lệch rất lớn.** 200 em / 5 buổi / mọi em Tầng 2:
   A2 cứu được từ **1,2** tới **79,0** em, tuỳ tỉ lệ chọi. Ở chọi 0,5× thì cả ba
   ra 0 — thừa chỗ thì bốc thăm không có việc gì để làm.
3. **Nguyên nhân của khoảng cách đó là ĐIỂM, không phải thiếu ghế.** Vặn tỉ lệ
   em có điểm từ 0% lên 100%, lợi thế của A2 đi từ **92%** số em mà A1 bỏ lại
   xuống tới *không phân biệt được*. Vặn độ mịn thang điểm cho kết quả y hệt:
   **91%** ở thang 1 mức (hoà hết) xuống **0%** ở thang 61 mức. Thiếu ghế thì
   không xoá được lợi thế của A2 — ở chọi 4,0× nó vẫn cứu 79 em.
4. **A3 mở kênh khai gian.** Giấu bớt buổi có lợi cho **113/300** em dưới A3,
   và **0/300** dưới A1 lẫn A2. Kênh đó là kênh *đánh đổi* (phải bỏ một suất
   buổi trước để lên trước ở buổi sau), nhưng vẫn đủ để dữ liệu nguyện vọng
   thu về không còn là nguyện vọng thật.

**Đã chốt theo bảng đo này: phần mềm chạy duy nhất A2.** Không còn bộ chọn,
không còn bảng đối chiếu trên giao diện, và `api.run_pipeline` không còn nhận
tham số chế độ — có test canh chữ ký hàm đó. Một buổi thì A2 cho kết quả y hệt
A1, nên không con số nào ở các mục trên phải đo lại.

A1 và A3 vẫn còn trong `rbda_priority_pipeline.py` **để TN7 đối chứng được** —
xoá chúng đi thì `do_boc_tham.py` không chạy lại được và mọi số ở mục này mất
khả năng tái lập.

Thứ tự bốc thăm của từng buổi đọc ở thẻ **02 Kết quả**, bảng *Số bốc thăm theo
buổi*, và ở tệp `..._so_boc_tham_theo_buoi.csv`. Trường vẫn chỉ công bố hai
thứ như trước — bộ số đã khoá và `seed` — vì thứ tự từng buổi là hàm tất định
của hai thứ đó.

## 4. Kịch bản nhỏ kiểm được bằng tay

Xem `NHAP_TAY.md` — 8 học sinh, 3 CLB.

| Đại lượng | Giá trị |
|---|---|
| Được xếp | 6 / 8 |
| Em vào bằng suất dự trữ | 1 (điểm 6,0) |
| Em điểm cao hơn nhưng không vào CLB đó | 2 (điểm 8,5 và 8,0) |
| Số hạt giống đã thử | 5 (1, 7, 42, 999, 12345) |
| Số lần cho kết quả khác nhau | **0** |

Không có hai em bằng điểm trong cùng một CLB nên bước bốc thăm không được dùng
tới — kết quả tính được bằng tay.

## 5. Kiểm thử phần mềm

| Đại lượng | Giá trị |
|---|---|
| Tệp kiểm thử | 37 |
| Trường hợp kiểm thử | **483** |
| Số trường hợp không đạt | 0 |
| Thời gian chạy toàn bộ | ~95 giây |

## 6. Lỗi tìm được trong quá trình phát triển

| Đại lượng | Giá trị |
|---|---|
| Tổng số lỗi đã tìm và sửa | **25** |
| Trong đó là lỗi **im lặng** | **10** |

*Lỗi im lặng = phần mềm báo thành công trong khi dữ liệu đã sai.* Danh sách từng
lỗi và cách phát hiện nằm trong lịch sử Git và `BAN_GIAO.md` mục 5.

## 7. Chạy trên máy Windows thật

| Kiểm tra | Kết quả | Ngày |
|---|---|---|
| Mở được bản `.exe` | Có | 30/08 |
| Cửa sổ ứng dụng riêng, không thanh địa chỉ | Có | 30/08 |
| Mục riêng trên thanh tác vụ | Có | 30/08 |
| Còn sống sau 3–5 phút thu nhỏ | Có | 30/08 |
| Nạp 4 tệp Excel | Thành công | 30/08 |
| Số ứng viên mỗi CLB khớp với số đo trên máy phát triển | Khớp cả 10 | 30/08 |
| `PhanBoCauLacBo.exe` là tiến trình riêng trong Task Manager | Có | 31/08 |
| Cửa sổ gốc (pywebview) **được tạo** | Có | 31/08 |
| Cửa sổ gốc **dùng được** | **Chưa** — treo, xem dưới | 02/09 |

**Đã sửa lại một khẳng định sai ở mục này (02/09).** Bản trước ghi *"Cửa sổ gốc
(pywebview) mở được: Có"* và dẫn chứng bằng dòng nhật ký:

```
[2026-08-31 15:34:42] go dau tai-ve trong ...\_internal:
                      {'da_go': 173, 'bo_qua': 0, 'loi': 0}
[2026-08-31 15:34:42] cua so goc (pywebview) mo THANH CONG
```

**Dòng "mo THANH CONG" đó không chứng minh được điều nó có vẻ chứng minh.**
`main.py` ghi nó **trước** khi gọi `webview.start()` — mà `start()` mới là chỗ
thật sự mở cửa sổ, và cũng chính là chỗ đã treo. Nói cách khác, nhật ký ghi
"THÀNH CÔNG" ngay cả trong lần chạy mà app đứng hình. Chi tiết: `BAN_GIAO.md`
mục 5, lỗi 25.

Ngày 02/09 học sinh chạy thử: cửa sổ gốc **có** mở, nhưng tiêu đề ghi
**"(Not Responding)"** và giao diện không kết nối được với phần lõi. Nguyên nhân
đã tìm ra và đã sửa (`api.set_window` khiến pywebview đệ quy vào chính cửa sổ của
nó, chạm bốn property chặn 15 giây và đọc control WinForms chéo luồng).

**Trạng thái đúng tính đến 02/09:** bản vá đã có, đã đóng gói, **nhưng CHƯA được
xác nhận trên máy Windows.** Máy phát triển chạy Linux, không có .NET Framework
lẫn WinForms — cơ chế đo được bằng cách chạy lại đúng luật dò của pywebview
(`tests/test_do_api.py`), còn xác nhận cuối cùng phải do máy thật cho.

**Đường hiển thị được xác nhận là dùng được: chế độ dự phòng bằng trình duyệt**
(đã chạy trọn luồng nạp → chạy → xuất trên Windows ngày 30/08). Cửa sổ gốc là
đường ưu tiên trong mã, nhưng **báo cáo không được viết là nó đã chạy được** cho
tới khi có một lần chạy thành công trên máy Windows.

`da_go: 173` vẫn là số liệu đúng: đó là số tệp mang dấu "tải từ Internet" mà phần
mềm tự gỡ lúc khởi động. `bo_qua: 0` nghĩa là **không tệp nào sạch sẵn** — tức
việc gỡ dấu do **mã tự làm**, không phải người dùng thao tác tay.

---

*Phần diễn giải, nhận xét và đánh giá ý nghĩa của các con số trên, học sinh tự viết.*
