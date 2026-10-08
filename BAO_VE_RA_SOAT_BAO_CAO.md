# Rà soát báo cáo 15 trang trước buổi bảo vệ

> Đối tượng rà soát: `Xay_dung_phan_mem_sap_xep_hoc_sinh_15trang_3.docx`
>
> **Mọi con số "đúng" trong tệp này đều đã đối chiếu với nguồn gốc** —
> `du_lieu_test/thu_tai/ket_qua_thu_tai.csv` (204 cấu hình),
> `rbda_priority_pipeline.py`, `NGHIEN_CUU_TOI_UU.md`, `GIAI_DAP_BOC_THAM.md`.
> Không mục nào là suy đoán. Cách kiểm lại từng mục ghi ở cuối tệp.
>
> Tệp này **chỉ chỉ ra chỗ lệch giữa báo cáo và số gốc**. Việc diễn giải,
> viết lại câu, và quyết định giữ hay bỏ luận điểm nào — học sinh tự làm.

---

## Đọc bảng này thế nào

| Mức | Nghĩa | Ưu tiên |
|---|---|---|
| **A** | Số liệu sai hoặc gán nhầm nguồn. Giám khảo bắt được là **mất điểm trực tiếp** | Sửa trước tiên |
| **B** | Báo cáo **yếu hơn** phần mềm em đã làm. Không sai, nhưng **bỏ điểm sáng tạo** | Sửa nếu còn thời gian |
| **C** | Chính tả, câu tối nghĩa, rác định dạng | 15 phút cuối |

---

# MỨC A — sai số liệu

## A1. Con số 7,65 giây bị gán nhầm nguồn

**Báo cáo viết (mục Kết luận):**

> *"...mỗi học sinh có 10 nguyện vọng mất **7,65 giây từ lúc bấm nút bắt đầu
> đến lúc bảng kết quả hiện ra** (lần chạy lâu nhất trong 204 cấu hình)."*

**Vấn đề.** 7,6538 giây là giá trị cột `t_phan_bo_giay` — **chỉ bước phân bổ**.
Lưới quét đo **ba** bước riêng biệt, và hàng chậm nhất đó có:

| Bước | Cột | Giây |
|---|---|---|
| Nạp dữ liệu | `t_nap_giay` | 3,6685 |
| **Phân bổ** | `t_phan_bo_giay` | **7,6538** |
| Xuất kết quả | `t_xuat_giay` | 0,2006 |
| **Tổng ba bước** | | **11,5229** |

"Từ lúc bấm nút bắt đầu đến lúc bảng kết quả hiện ra" là mô tả của **tổng ba
bước**, không phải của bước phân bổ.

**Hai cách sửa, chọn một:**

- Giữ 7,65s, sửa mô tả thành *"**thời gian chạy phân bổ** — lần chạy lâu nhất
  trong 204 cấu hình"*.
- Giữ mô tả end-to-end, đổi số thành **11,52 giây**.

> **Cách sửa thứ nhất mạnh hơn** — vì phần em nghiên cứu là *thuật toán*, còn
> 3,67s nạp dữ liệu là chi phí đọc tệp, không phản ánh chất lượng thuật toán.

---

## A2. "Cấu hình cao nhất" — dùng sai từ

**Báo cáo viết (Kết luận và Hướng phát triển, 2 chỗ):**

> *"Thuật toán hiện tại có thể chạy với **cấu hình cao nhất gồm 5000 học sinh
> và 10 câu lạc bộ**..."*

**Vấn đề.** Lưới quét chạy số CLB ở **bốn** mức: **10 · 25 · 50 · 100**. Nên 10
CLB là mức **thấp nhất**, không phải cao nhất. Cấu hình 5000 em / 10 CLB là
cấu hình **chậm nhất**, và đó là chuyện khác hẳn.

Số đo thật, 5000 em / 10 nguyện vọng / chia đều chỉ tiêu:

| Số CLB | Thời gian phân bổ | Số vòng | Tỉ lệ được xếp |
|---|---|---|---|
| **10** | **7,65 s** | 31 | 100% |
| 25 | 5,91 s | 23 | 97,92% |
| 50 | 4,24 s | 22 | 95,80% |
| 100 | 3,58 s | 20 | 93,64% |

**Sửa thành:** *"Lưới quét chạy tới **5000 học sinh và 100 câu lạc bộ** (204 cấu
hình). Cấu hình **chậm nhất** là 5000 em / 10 CLB / 10 nguyện vọng: 7,65 giây
cho bước phân bổ."*

> ⚠️ **Cùng lúc đó, mục "Tính ổn định" của em lại viết đúng** — *"Với quy mô
> 5000 học sinh và **100** câu lạc bộ, không tìm được bất kì cặp phá vỡ nào."*
> Đó là phép đo khác (`kiem_on_dinh.py`, quy mô 500/25 · 2000/50 · 5000/100).
> Nên **hai con số 10 và 100 không mâu thuẫn nhau** — chúng thuộc hai thí
> nghiệm khác nhau. Nhưng đọc liền nhau thì trông như mâu thuẫn, và giám khảo
> sẽ hỏi. **Phải nói rõ đó là hai phép đo khác nhau.**

---

## A3. Câu về seed tự mâu thuẫn với chính đoạn sau nó

**Báo cáo viết (mục 4.2.2.3):**

> *"Số bốc thăm này dựa trên hàm random (seed), **các tác động của seed này đã
> được đo và không ảnh hưởng đến kết quả bốc thăm**."*

Rồi ba dòng sau, cùng mục:

> *"Nếu đổi mã số seed thì chỉ có **1% số học sinh bị đổi suất** và có kết quả
> khác."*

**Vấn đề.** Hai câu này phủ định nhau. Đổi seed **có** đổi kết quả — chính em
đã đo được là 1,1%. Điều đã đo được **không phải** "seed không ảnh hưởng", mà là:

> đổi seed **không làm em nào được lợi hay bị thiệt một cách hệ thống** —
> lệch tối đa **1,44%** so với kỳ vọng lý thuyết sau 10 000 lần bốc trên 100
> học sinh, và tương quan giữa mã học sinh với thứ hạng **đổi dấu** qua 8 khối
> seed, tức là nhiễu thống kê chứ không phải thiên lệch.

**Sửa:** bỏ hẳn cụm *"không ảnh hưởng đến kết quả bốc thăm"*, thay bằng câu
trên. Đây là lỗi **nguy hiểm nhất ở mức A**, vì nếu giám khảo bắt được câu đầu,
toàn bộ phần bốc thăm của em mất uy tín — dù số đo phía sau hoàn toàn đúng.

---

## A4. Trộn lẫn trần nguyện vọng (10) với trần thi (5)

**Báo cáo viết (mục Mô hình hóa bài toán):**

> *"Học sinh chỉ cần thực hiện n lần... và thực hiện **5n** tối đa bài thi để
> thi vào CLB đó và **5n** lần sắp xếp thứ tự nguyện vọng."*

**Vấn đề.** Hai trần trong mã nguồn là hai số khác nhau:

| Trần | Hằng số | Giá trị | Vị trí |
|---|---|---|---|
| Nguyện vọng / buổi | `TRAN_NGUYEN_VONG_MOI_BUOI` | **10** | `rbda_priority_pipeline.py:84` |
| CLB được thi / buổi | `TRAN_CLB_THI_MOI_BUOI` | **5** | `rbda_priority_pipeline.py:89` |

Chính báo cáo đã viết đúng ở câu trước đó (*"trần cứng là 10 CLB"*, *"trần được
thi là 5 vốn khác với trần được sắp xếp thứ tự nguyện vọng là 10"*), rồi câu sau
lại dùng 5n cho cả hai.

**Sửa:** *"tối đa **5n** bài thi và **10n** lần sắp xếp thứ tự nguyện vọng"*.

> **Chuẩn bị sẵn câu trả lời cho câu hỏi kéo theo:** *vì sao 10 mà không phải
> số khác?* Câu trả lời có trong mã (`:82-83`): **10 là giới hạn của câu hỏi
> Ranking trong Microsoft Forms** — tức là **ràng buộc của công cụ, không phải
> của lý thuyết**. Còn 5 là **chính sách nhà trường** (`:86`), cũng không phải
> giới hạn kỹ thuật. Trả lời được hai nguồn gốc khác nhau này là được điểm.

---

## A5. Công thức chi phí thiếu biến quan trọng nhất

**Báo cáo viết (Hướng phát triển):**

> *"...cần giảm chi phí (Chi phí = số vòng lặp × số câu lạc bộ × cỡ danh sách
> nguyện vọng)"*

**Ba vấn đề:**

1. **Thiếu số học sinh `S`.** Mà chính báo cáo, mục "Thời gian chạy phân bổ",
   kết luận: *"Thời gian tăng dần tuyến tính theo **số học sinh**"*. Công thức
   bỏ mất đúng biến mà em vừa chứng minh là quan trọng nhất.
2. **Số CLB đi sai chiều.** Theo công thức, nhiều CLB hơn → chi phí cao hơn.
   Số đo (bảng ở A2) cho ngược lại: 10 CLB mất 7,65s, 100 CLB mất 3,58s —
   **nhiều CLB hơn lại nhanh hơn**.
3. **Repo không có phân tích độ phức tạp nào.** Anh đã tìm `O(n`, "độ phức
   tạp", "complexity" trong toàn bộ mã và tài liệu: **không có**. Nên công thức
   này không có gì chống lưng.

**Khuyến nghị:** **bỏ công thức**, thay bằng phát biểu dựa trên số đo —
*"thời gian phân bổ tăng gần tuyến tính theo số học sinh; số câu lạc bộ ảnh
hưởng ít hơn, và ở lưới quét này nhiều câu lạc bộ hơn lại cho thời gian thấp
hơn."*

Nếu em muốn **giữ** một công thức thì phải tự bảo vệ được nó, và phải giải thích
được nghịch lý ở điểm 2. **Lưu ý (sửa 23/09):** nguyên nhân KHÔNG phải số vòng
lặp — cấu hình chạy 227 vòng vẫn nhanh hơn cấu hình 31 vòng. Đo tách từng phần
cho thấy phần tốn nhất là kiểm ổn định, và nó đắt hơn khi mỗi CLB lớn hơn. Con
số 7,65s còn được đo khi đang bật theo dõi bộ nhớ (tracemalloc), làm chậm khoảng
gấp đôi. Chi tiết: Q31–Q32 và bài H12 trong `BAO_VE_NGAN_HANG_CAU_HOI.docx`.

---

## A6. Thiếu tài liệu tham khảo quan trọng nhất cho phần tính mới

**Danh mục hiện có [1]–[5]:** Gale & Shapley 1962 · Roth 1984 ·
Abdulkadiroğlu & Sönmez 2003 · Abdulkadiroğlu, Pathak, Roth & Sönmez 2005 ·
Ashlagi, Nikzad & Romm.

**Thiếu: Kominers & Sönmez (2016)** — và đây là tài liệu **duy nhất** được trích
trong mã nguồn:

```
rbda_priority_pipeline.py:6    (soft reserves, precedence ordering — Kominers & Sonmez 2016)
rbda_priority_pipeline.py:213  (đây chính là "reserve pass rồi general pass" — Kominers & Sonmez
```

**Vì sao nghiêm trọng.** Nó chống lưng cho **cơ chế dự trữ mềm** — phần tính mới
mạnh nhất của em. Hiện tại danh mục của em toàn tài liệu về DA *chuẩn*, không có
tài liệu nào về *dự trữ*. Giám khảo đọc danh mục sẽ thấy: em trích đủ tài liệu
cho phần em **không** tự làm, và không trích gì cho phần em **có** tự làm.

**Việc cần làm:** em tự tra và bổ sung trích dẫn đầy đủ. Dòng trích dẫn trong mã
là **em tự viết**, có từ commit đầu `57f2e82` (26/08) — nên đây là tài liệu em
đã biết, chỉ là chưa đưa vào danh mục.

> Việc khảo sát và bổ sung tài liệu tham khảo là việc của em (Phụ lục 1). Anh
> chỉ chỉ ra chỗ **danh mục không khớp với mã nguồn của chính em**.

---

# MỨC B — báo cáo yếu hơn phần mềm

> Đây là nhóm **không sai một chữ nào**, nhưng đang làm em mất điểm ở hai tiêu
> chí nặng nhất: **Tính sáng tạo (20đ)** và **Trả lời phỏng vấn (25đ)**.

## B1. ⭐ Phát hiện mạnh nhất của cả dự án không có trong báo cáo

**Báo cáo mô hình hóa (mục Bài toán ghép cặp ổn định):**

> *"mỗi câu lạc bộ cần cung cấp số lượng học sinh giới hạn và **danh sách thứ tự
> ưu tiên** dựa trên bài kiểm tra"*

**Với `reserve_capacity > 0`, mô hình đó sai về mặt toán học** — và repo có phản
ví dụ **chạy được**. Anh vừa chạy `python3 du_lieu_test/do_hai_canh_du_tru.py`:

```
Câu lạc bộ:   sức chứa 3, trong đó 1 suất dự trữ
Ưu tiên nền:  A(1) > B(2) > C(3) > D(4)      ← giữ nguyên ở cả hai cảnh
Diện dự trữ:  D

Cảnh 1 — D có mặt:
  Mô hình 'một danh sách Q_j' ->  ['A', 'B', 'C']
  club_choice_function()      ->  ['D', 'A', 'B']      *** LỆCH ***

Cảnh 2 — D vắng mặt:
  Mô hình 'một danh sách Q_j' ->  ['A', 'B', 'C']
  club_choice_function()      ->  ['A', 'B', 'C']      KHỚP
```

Hai điều đọc ra:

1. **Cảnh 1: C xếp trên D (hạng 3 so với 4), CLB lấy đủ 3 em — mà D đỗ, C
   trượt.** Theo mô hình một danh sách thì chuyện đó không thể xảy ra.
2. **Cùng em C, cùng thứ hạng, cùng CLB, cùng sức chứa** — cảnh 1 trượt, cảnh 2
   đỗ. Cái đổi duy nhất là **D có mặt hay không**.

Nghĩa là: kết cục của C phụ thuộc **ai khác đang nộp cùng lúc**, không chỉ phụ
thuộc thứ hạng của C. **Không viết ra được một `Q_j` cố định.**

**Vì sao đây là điểm mạnh — và giới hạn của nó (sửa 23/09):**

Định lý Gale–Shapley 1962 **giả định mỗi CLB có một danh sách ưu tiên cố định**.
Phản ví dụ trên cho thấy phần mềm của em **không thỏa giả định đó**, nên định lý
dạng gốc không áp dụng nguyên văn.

> **Nhưng lý thuyết tổng quát vẫn áp dụng.** Hàm lựa chọn có dự trữ vẫn có
> **tính thay thế** (kiểm bằng máy trên 221 220 cặp nhóm: 0 vi phạm), và lý
> thuyết ghép cặp tổng quát chỉ cần tính chất đó để bảo đảm ổn định, tối ưu cho
> học sinh và chống khai gian. Phép đo TN1 (2 088 thể hiện vét cạn, 0 phản ví
> dụ) **khớp đúng dự đoán đó** — nó không phải phát hiện mới.

Giá trị thật của phép đo: nó kiểm **phần mềm của em** có đúng không, và đã bắt
được lỗi thật. Đây là câu khó nhất em có thể bị hỏi — xem Q39 trong
`BAO_VE_NGAN_HANG_CAU_HOI.docx`.

**Và mặt ngược lại cũng đã đo** (`do_khong_du_tru.py`, `tests/test_khong_du_tru.py`
kiểm trên 200 pool ngẫu nhiên): đặt `reserve_capacity = 0` thì hàm lựa chọn
**thu về đúng** *"sắp theo thứ hạng, lấy K em đầu"* — tức mô hình `Q_j` trong
báo cáo trở thành **đúng**. Suất dự trữ là **nguyên nhân duy nhất** làm nó sai.

---

## B2. "Giả thuyết toán học" đang tự làm yếu chính nó

**Báo cáo viết:**

> *"Giả thuyết toán: Nếu áp dụng thuật toán Gale–Shapley vào bài toán sắp xếp
> học sinh–câu lạc bộ, với mỗi học sinh có một thứ tự nguyện vọng và mỗi câu lạc
> bộ có một thứ tự ưu tiên cùng sức chứa xác định, thì thuật toán sẽ tạo ra một
> phương án sắp xếp ổn định."*

**Câu hỏi giám khảo sẽ hỏi — gần như chắc chắn:**

> *"Gale và Shapley đã **chứng minh** điều này từ năm 1962. Em giả thuyết lại
> một định lý đã có để làm gì?"*

Với cách phát biểu hiện tại, câu này **không có đường trả lời**: em vừa mô tả
đúng tiền đề của định lý (*"mỗi câu lạc bộ có một thứ tự ưu tiên"*), nên giả
thuyết của em đúng một cách tầm thường — nó là định lý.

**Đường ra nằm ở B1.** Phần mềm của em **không** thỏa tiền đề đó. Nên giả thuyết
cần phát biểu lại để lộ đúng chỗ khó:

> *Khi CLB có suất dự trữ, hàm lựa chọn **không còn là một thứ tự ưu tiên tuyến
> tính**, nên định lý Gale–Shapley **không áp dụng trực tiếp**. Giả thuyết: biến
> thể có dự trữ vẫn cho kết quả ổn định, và vẫn là phương án tốt nhất cho học
> sinh trong các phương án ổn định.*

**Câu này em tự viết lại** — anh chỉ chỉ ra chỗ giả thuyết hiện tại đang tự vô
hiệu hóa. Nhưng lưu ý đây là **thay đổi lớn nhất** trong toàn bộ bản rà soát, và
là thay đổi duy nhất **tự nó nâng điểm Tính sáng tạo**.

---

## B3. Toàn bộ TN1–TN7 không có trong báo cáo

Em đã chọn bảo vệ cả phần nghiên cứu này. Nhưng **hội đồng chỉ đọc báo cáo** —
nên nếu em không chủ động đưa vào lời trình bày, phần này coi như không tồn tại
với người chấm.

| TN | Nội dung | Con số chính |
|---|---|---|
| TN1 | Có phải phương án ổn định **tốt nhất cho học sinh**? | **0** phản ví dụ / **2 088** thể hiện vét cạn |
| TN2 | Đổi bên đề xuất (CLB đề xuất) thì đổi gì? | **0/20** seed cho kết quả khác, cả 3 bộ |
| TN3 | **Khai gian nguyện vọng có lợi không?** | **0/1 400** em · Boston: **258/1 400** (18,4%) |
| TN4 | So với 4 cơ chế khác | Boston cho 92 em NV1 (em: 54) **nhưng 50 cặp phá vỡ** |
| TN5 | Có **tối ưu Pareto** không? | **KHÔNG** — 16 chu trình, 32/140 em |
| TN6 | **Độ bền** trước nhiễu dữ liệu | **392** phép thử, **0** cặp phá vỡ |
| TN7 | Ba thiết kế bốc thăm cho cả tuần | A3 tốt hơn nhưng **113/300 em khai gian được** |

**Ba con số nên đưa vào lời trình bày** (chọn ít, nói sâu — đừng đọc cả bảng):

1. **0/1 400 em khai gian được, trong khi Boston là 258/1 400.** Đây là con số
   mạnh nhất, vì nó có **đối chứng ngược** — một bộ dò lúc nào cũng báo "không
   tìm thấy" thì vô dụng; cột Boston khác 0 chứng minh bộ dò hoạt động.
2. **2 088 thể hiện vét cạn, 0 phản ví dụ** — nối thẳng vào B1/B2.
3. **Không tối ưu Pareto** — nêu chủ động, xem B5.

---

## B4. Không có bảng so sánh với cơ chế khác, dù TN4 đã đo đủ

Tiêu chí **Tính sáng tạo (20đ)** hỏi đúng câu *"khác gì so với nghiên cứu đã
có"*. Báo cáo hiện chỉ so với **"phương pháp thủ công / thứ tự đăng ký"** — tức
so với cái không ai bảo vệ. TN4 đã so với **bốn cơ chế học thuật thật**
(Boston, TTC, xét theo bốc thăm, DA do CLB đề xuất) trên cùng dữ liệu, cùng seed.

Bảng `bo_sach` (140 em / 12 CLB) — nên đưa vào báo cáo:

| Cơ chế | NV1 | Trượt | Hạng TB | **Cặp phá vỡ** | Khai gian được |
|---|---|---|---|---|---|
| **Của em** | 54 | 0 | 2,100 | **0** | **0%** |
| Boston | **92** | 2 | **1,826** | **50** | **18,4%** |
| Xét theo bốc thăm | 81 | 2 | 1,928 | 121 | 0% |
| TTC | 80 | 0 | 1,879 | 118 | 0% |

**Đây đồng thời là câu hỏi bẫy nặng nhất** — xem T3 trong bộ câu hỏi: *"Boston
cho 92 em nguyện vọng 1, em chỉ cho 54. Sao em không dùng Boston?"*

---

## B5. Báo cáo không có mục "Giới hạn nghiên cứu"

Báo cáo có "Hướng phát triển" nhưng **không nêu hạn chế nào**. Khung trình bày
VISEF yêu cầu chủ động nêu giới hạn **trước khi bị hỏi** — nêu trước là được
điểm tư duy phản biện, bị hỏi mới nói là mất.

**Hai hạn chế thật, mạnh nhất, đã có sẵn số liệu trong repo:**

1. **Vét cạn chỉ chạy được ở quy mô nhỏ — 7 em / 4 CLB.** Nên kết luận TN1 là
   *"không tìm được phản ví dụ trong 2 088 thể hiện nhỏ"*, **không phải một
   chứng minh toán học cho mọi quy mô**. (`NGHIEN_CUU_TOI_UU.md:537-539`)
2. **Kết quả không tối ưu Pareto.** 16 chu trình đổi chỗ, 32/140 em (22,9%) có
   thể **cùng** lên nguyện vọng cao hơn. Và đó là **đánh đổi bắt buộc**: đổi chỗ
   theo cả 16 chu trình thì hạng trung bình từ 2,100 xuống 1,771, nhưng sinh ra
   **92 cặp phá vỡ**. Đây là đặc điểm của **mọi** cơ chế giữ tính ổn định, không
   phải lỗi cài đặt của em.

**Hạn chế thứ ba nên nói nếu bị hỏi về dữ liệu** (xem T2): cả ba bộ dữ liệu đều
là **mô phỏng do máy sinh**, không phải học sinh thật. `bo_sach` còn được **cố ý
dựng cho chật**. `NGHIEN_CUU_TOI_UU.md:543-545` gọi việc trình bày các số này
như số liệu khảo sát thật là **"bịa đặt dữ liệu"** — nên tuyệt đối không nói
chúng là số liệu khảo sát ở trường.

---

## B6. Mục "Nên cho học sinh xếp bao nhiêu nguyện vọng?" không trả lời câu hỏi

Tiêu đề mục là một câu hỏi. Phần thân mô tả hai biểu đồ (chỉ tiêu chia đều vs
chỉ tiêu theo độ hút), rồi kết luận:

> *"Cách nhà trường chia chỉ tiêu gây ảnh hưởng đến tỉ lệ học sinh không được
> chia vào câu lạc bộ nào."*

**Đó là kết luận về cách chia chỉ tiêu, không phải về số nguyện vọng.** Tiêu đề
hứa một con số và phần thân không đưa con số nào.

Giám khảo sẽ hỏi thẳng: ***"Vậy theo em nên cho xếp mấy nguyện vọng?"*** — và em
phải có một con số kèm lý do, hoặc phải đổi tiêu đề mục cho khớp nội dung.

> Repo có `du_lieu_test/do_do_dai_nguyen_vong.py` — bộ đo đúng cho câu hỏi này.
> Chạy nó rồi lấy số, hoặc đổi tiêu đề mục thành *"Cách chia chỉ tiêu ảnh hưởng
> thế nào đến tỉ lệ học sinh không được xếp?"*.

---

## B7. Con số "600 lần chạy" không có nguồn

**Báo cáo viết (mục 4.2.2.3):**

> *"...với **0 cặp phá vỡ ở mọi seed trong 600 lần chạy** và thử khác nhau."*

**Anh đã tìm toàn bộ repo — không có script nào sinh ra con số 600.** Nó chỉ
xuất hiện ở **một chỗ duy nhất**: `CO_CHE_THUAT_TOAN.md:105`, tức là được chép
sang báo cáo từ đó. Các phép đo thật có nguồn là:

| Con số có nguồn | Phép đo | Script |
|---|---|---|
| **40 seed**, 0 cặp phá vỡ | quét seed cho cặp đôi cùng có lợi | `do_danh_doi_on_dinh.py` |
| **392 phép thử**, 0 cặp phá vỡ | độ bền trước nhiễu (TN6) | `do_ben_vung.py` |
| **300 lần chạy**, 0 cặp phá vỡ | ba thiết kế bốc thăm (TN7b) | `do_boc_tham.py` |
| **20 seed** × 3 bộ | đổi bên đề xuất (TN2) | `do_toi_uu_on_dinh.py` |

**Việc cần làm:** thay 600 bằng một trong các con số **có script chống lưng** ở
trên, hoặc tìm lại nguồn gốc của 600. Giám khảo hỏi *"600 lần chạy nào, em chạy
bằng gì?"* mà em không chỉ ra được thì **mất uy tín cả bảng số** — dù mọi con số
khác đều đúng.

> Đây là lỗi nhỏ về lượng nhưng lớn về hậu quả: một con số không truy được nguồn
> làm giám khảo nghi ngờ **tất cả** những con số còn lại.

---

# MỨC C — chính tả, câu tối nghĩa, rác định dạng

| Chỗ | Đang là | Sửa thành |
|---|---|---|
| **Tiêu đề mục** (!) | *"Thuật toán chấp nhận trì **hoàn**"* | trì **hoãn** |
| Tóm tắt dự án | *"tuyển sinh vào trường hợp vi mô"* | câu tối nghĩa — **viết lại cả câu** |
| Nguyên nhân vấn đề | *"phương pháp xử lý **hiên** tại"* | hiện tại |
| 4.2.2.2 | *"số lượng **xuất** dự trữ"* | **suất** dự trữ |
| 4.2.2.2 | *"**Xét cá** học sinh thuộc diện dự trữ"* | Xét **các** học sinh |
| 4.2.2.2 | *"**Lượt chung: Lượt chung:** xét toàn bộ..."* | lặp nhãn — bỏ một cái |
| 4.2.2.3 | *"Số bốc thăm **nay** dựa trên..."* | **này** |
| 4.2.2.4 | *"thứ hạng nguyện **vòng** của học sinh"* | nguyện **vọng** |
| 4.2.2.5 | *"s thích c hơn chỗ **hiệu** tại"* | **hiện** tại |
| Mục "Nên cho xếp mấy NV" | *"Khi **câu lạc động người thích** có chỉ tiêu cao hơn"* | *"Khi **câu lạc bộ nhiều người thích** có chỉ tiêu cao hơn"* |
| **Mục 4.2.2.6** | rác textbox: `left00` và `279404769485039900` | **xóa** — đây là lỗi dán hình trong Word, sẽ in ra giấy |

> Mục 4.2.2.6 là mục *"Sơ đồ và các chuỗi hình ảnh"* — kiểm lại xem sơ đồ có
> thật sự hiện ra không, hay chỉ còn hai dòng rác đó. Một mục có tiêu đề mà
> không có nội dung là chỗ giám khảo hỏi ngay.

---

# Thứ tự làm việc đề xuất

| Ưu tiên | Việc | Thời gian |
|---|---|---|
| **1** | A3 (câu về seed tự mâu thuẫn) — nguy hiểm nhất ở mức A | 5 phút |
| **2** | A1, A2, A4 (ba con số sai/gán nhầm) | 15 phút |
| **3** | B5 (thêm mục Giới hạn, 2 hạn chế) — được điểm ngay | 30 phút |
| **4** | B2 + B1 (phát biểu lại giả thuyết) — **nâng điểm sáng tạo nhiều nhất** | 1 giờ |
| **5** | A5, A6, B7 (bỏ công thức, thêm trích dẫn, sửa con số 600) | 30 phút |
| **6** | B4 (thêm bảng so sánh TN4) | 30 phút |
| **7** | Mức C toàn bộ + kiểm mục 4.2.2.6 | 15 phút |
| 8 | B6, B3 (nếu còn thời gian) | — |

---

# Cách kiểm lại từng con số trong tệp này

```bash
# A1, A2 — thời gian và lưới quét
python3 -c "
import csv
r=list(csv.DictReader(open('du_lieu_test/thu_tai/ket_qua_thu_tai.csv')))
print('So cau hinh:', len(r))
h=[k for k in r[0] if 'hoc_sinh' in k][0]
m=max(r,key=lambda x: float(x['t_phan_bo_giay']))
print('Cham nhat:', m[h],'em /',m['so_clb'],'CLB /',m['nguyen_vong'],'NV')
print('  nap=%s  phan_bo=%s  xuat=%s'%(m['t_nap_giay'],m['t_phan_bo_giay'],m['t_xuat_giay']))
print('  TONG = %.4f'%(float(m['t_nap_giay'])+float(m['t_phan_bo_giay'])+float(m['t_xuat_giay'])))
print('Cac muc so CLB:', sorted({int(x['so_clb']) for x in r}))
"

# A4 — hai tran
grep -n "TRAN_NGUYEN_VONG_MOI_BUOI = \|TRAN_CLB_THI_MOI_BUOI = " rbda_priority_pipeline.py

# A6 — trich dan trong ma nguon
grep -n "Kominers" rbda_priority_pipeline.py

# B1 — phan vi du Q_j  (bang chung manh nhat, in ra mang vao phong)
python3 du_lieu_test/do_hai_canh_du_tru.py

# B1 mat nguoc — bo du tru thi mo hinh Q_j dung tro lai
python3 du_lieu_test/do_khong_du_tru.py

# B7 — tim nguon con so 600
grep -rn "600 lần chạy" --include=*.md .
```

---

*Tệp này do AI lập, chỉ đối chiếu báo cáo với số liệu gốc và mã nguồn. Phần
diễn giải, viết lại câu, và quyết định giữ hay bỏ luận điểm nào — học sinh tự
làm (Phụ lục 1).*
