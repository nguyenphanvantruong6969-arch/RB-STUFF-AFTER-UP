# Kế hoạch mở rộng: phân bổ CLB cho NHIỀU BUỔI trong tuần

> **Giai đoạn 1–3 ĐÃ LÀM XONG.** Tài liệu này giữ nguyên như lúc thiết kế, để
> đối chiếu được cái đã hình dung với cái đã dựng. Phần đã làm, phần còn lại,
> và những chỗ thiết kế phải sửa khi chạm vào mã thật — xem mục 12 ở cuối.
>
> Bản trình bày có sơ đồ: `KE_HOACH_NHIEU_BUOI.html`. Bản trực tuyến:
> https://claude.ai/code/artifact/64494a54-773d-4a8d-ad4a-1e19d15c036a

---

## 1. Bài toán đang mở rộng

Phần mềm hiện tại giải: **mỗi học sinh ↔ đúng một CLB**.

Thực tế ở trường: một tuần có nhiều CLB sinh hoạt vào nhiều ngày khác nhau, và
một em có thể tham gia nhiều CLB miễn không trùng buổi. Cần xếp ra một **thời
khoá biểu tuần** cho mỗi em.

Yêu cầu ràng buộc: **giữ nguyên thuật toán đã có** (`run_rbda`), không viết
lại, và không được làm mất bốn tính chất đã đo ở `NGHIEN_CUU_TOI_UU.md`.

### Bốn điều kiện đã chốt

| Câu hỏi | Chốt |
|---|---|
| Một CLB sinh hoạt mấy buổi/tuần? | **Đúng một buổi** |
| Trần số CLB mỗi tuần? | **Không có trần** — chỉ ràng buộc ≤ 1 CLB mỗi ngày |
| Trùng giờ trong ngày? | **Không** — trường chỉ tổ chức vào **tiết 9** |
| Học sinh khai nguyện vọng? | **Mỗi ngày một danh sách xếp hạng riêng** |
| Bốc thăm qua các ngày? | **Làm cả ba thiết kế, đo rồi quyết** |

---

## 2. Vì sao bốn điều kiện trên là trường hợp ĐẸP NHẤT

Vì mỗi CLB thuộc **đúng một** buổi, học sinh lấy tối đa một CLB mỗi buổi, và
**không có trần tuần**, nên tập CLB khả thi của một em là: *chọn tuỳ ý, độc
lập, tối đa một CLB trong mỗi buổi*.

Đây là ràng buộc **phân hoạch** thuần tuý — các buổi **không ràng buộc lẫn
nhau**. Hệ quả:

> ### Bài toán tuần = số buổi × bài toán ngày, HOÀN TOÀN ĐỘC LẬP.
>
> Chạy đúng `run_rbda` hiện tại, mỗi buổi một lần. Không sửa một dòng thuật
> toán nào.

Và vì các thị trường độc lập, mọi tính chất chứng minh cho một ngày **tự động**
đúng cho cả tuần:

| Tính chất | Một buổi (đã đo) | Cả tuần | Vì sao |
|---|---|---|---|
| Ổn định (0 cặp phá vỡ) | ✅ | ✅ | không cặp nào bắc cầu được giữa hai buổi |
| Tối ưu cho học sinh | ✅ | ✅ | tối ưu trong từng thị trường độc lập |
| **Khai thật có lợi nhất** | ✅ | ✅ | **khai ở buổi *d* chỉ ảnh hưởng buổi *d*** — không có kênh nào để hi sinh ngày này lấy ngày kia |
| Bền trước nhiễu | ✅ | ✅ | nhiễu buổi *d* không lan sang buổi khác |

**Ba điều kiện phải nói rõ trong báo cáo, vì bỏ bất kỳ điều nào là mất bảng
trên:** một CLB một buổi · không có trần tuần · ưu tiên buổi này không phụ
thuộc kết cục buổi khác.

| Nếu vi phạm | Hỏng cái gì |
|---|---|
| CLB sinh hoạt 2 buổi, vào là phải đi cả hai | Sinh **tính bổ trợ** giữa các ngày → ma trận ổn định **có thể không tồn tại** |
| Có trần K CLB/tuần | Vẫn tồn tại và vẫn tối ưu cho học sinh (ràng buộc là một **matroid cắt ngọn**), nhưng **khai thật có lợi nhất không còn được bảo đảm** |
| CLB có nhiều lớp khác ngày, em chỉ vào một lớp | "≤1 mỗi buổi" giao "≤1 mỗi CLB" là **giao hai matroid — không còn là matroid** → mất bảo đảm |

---

## 3. Một hệ quả không hiển nhiên, phải nêu TRƯỚC khi đo

Vì các buổi độc lập, **STB tuần** (một số bốc thăm dùng chung cả tuần) và **STB
ngày** (mỗi buổi bốc lại) cho **cùng một phân phối kết quả ở mỗi buổi**. Chúng
chỉ khác nhau ở chỗ *may rủi có tương quan giữa các ngày hay không*:

- **STB tuần**: em số xấu đứng cuối Tầng 2 ở **mọi** buổi → may rủi **cộng
  dồn** → có em trắng tay cả tuần.
- **STB ngày**: may rủi **san đều** → xác suất trắng tay cả tuần giảm theo
  luỹ thừa số ngày.

> ### Dự đoán phải kiểm
>
> Số CLB **trung bình** mỗi em ở STB tuần và STB ngày **bằng nhau**; chỉ
> **phương sai** và **số em trắng tay** khác nhau, và STB ngày thấp hơn hẳn.

Nêu dự đoán trước để phép đo có thể **bác bỏ** nó. Nếu đo ra STB ngày làm giảm
cả số trung bình thì hoặc mô hình độc lập sai, hoặc bộ đo sai — cả hai đều phải
truy ra chứ không được bỏ qua.

---

## 4. Dữ liệu vào

### 4.1. Nguyên tắc: thêm buổi mà KHÔNG phá bộ dữ liệu cũ

`buoi` là **cột tuỳ chọn**. Không có cột đó ⇒ mọi CLB thuộc một buổi ngầm định
`__mac_dinh__` ⇒ **chạy y hệt phần mềm hiện tại**. Đây là ràng buộc cứng, có
test canh.

### 4.2. Tệp 01 — danh sách CLB: thêm một cột

```csv
club_id,name,capacity,reserve_capacity,reserve_group,buoi
clb_bongda,CLB Bóng đá,22,5,chinh_sach,thu_3
clb_tinhoc,CLB Tin học,14,4,chinh_sach,thu_5
```

`buoi` là **nhãn tự do**, không phải danh sách cố định thứ-2…thứ-7. Quy tắc duy
nhất: **hai CLB cùng giá trị `buoi` là trùng giờ.** Trường hiện chỉ dùng tiết 9
nên nhãn bằng ngày là đủ; nếu sau này có thêm tiết thì `thu_3_tiet_9` và
`thu_3_tiet_10` chạy được ngay, **không đổi một dòng thuật toán nào**.

**Cảnh báo bắt buộc:** một số CLB có `buoi` còn số khác trống → gom nhóm trống
vào `__chua_xep_buoi__` và kêu **cảnh báo nghiêm trọng**, không im lặng.

### 4.3. Tệp 03 — nguyện vọng: mỗi buổi một danh sách

Microsoft Forms: **một câu Ranking cho mỗi buổi** — *"Thứ 3 (tiết 9) em muốn
CLB nào?"*

Trần của phần mềm nay khớp đúng công cụ thu phiếu: **10 nguyện vọng mỗi buổi**,
bằng số mục tối đa của một câu Ranking. Trước đây trần đếm cho cả tuần, tức
một con số của Forms bị đem áp cho sáu câu hỏi Forms gộp lại.

```csv
student_id,name,reserve_group,thu_3_pref_1,thu_3_pref_2,thu_5_pref_1,thu_5_pref_2
HS001,Nguyễn Văn A,,clb_bongda,clb_covua,clb_tinhoc,
```

Em không muốn sinh hoạt buổi nào thì **để trống** cột buổi đó. Đó cũng là cách
khai *"thứ 5 em bận"* — **không cần thêm cột `ngay_ban`**: danh sách rỗng đã
nói đúng điều đó. Không thêm trường nào mà nguyện vọng đã diễn đạt được.

**Soát chéo bắt buộc:** CLB ghi ở cột `thu_3_pref_*` mà lại có `buoi = thu_5`
→ cảnh báo, nêu đích danh dòng. Đây là lỗi gõ tay dễ xảy ra nhất, và im lặng
thì hỏng kết quả.

### 4.4. Tệp 02 — chọn CLB muốn thi: **không đổi**

Điểm là của cặp (học sinh, CLB), không phụ thuộc buổi. Giữ nguyên hoàn toàn,
kể cả quy trình chấm mù.

### 4.5. Bảng `preferences`: `rank` đổi nghĩa

`rank` giờ là thứ hạng **trong buổi đó** (mỗi buổi đánh lại từ 1). Không đổi
schema. Với dữ liệu một buổi, *"trong buổi"* ≡ *"toàn cục"* → **tương thích
ngược tuyệt đối**. Luật soát trùng rank đổi từ *"trùng trong một học sinh"*
thành *"trùng trong một (học sinh, buổi)"*.

---

## 5. Thuật toán

### 5.1. Lõi: KHÔNG sửa gì

`compute_club_priority`, `club_choice_function`, `run_rbda`,
`verify_stability`, `generate_stb_lottery` — **giữ nguyên từng dòng**. 29 test
ở `tests/test_toi_uu_on_dinh.py` và toàn bộ `NGHIEN_CUU_TOI_UU.md` vẫn nói về
đúng đoạn mã đang chạy.

### 5.2. Thêm một hàm điều phối

```python
def run_rbda_nhieu_buoi(students, clubs, tested_scores, applicants,
                        preferences, stb_theo_buoi, is_reserve_eligible_fn):
    """Cắt dữ liệu theo buổi, gọi run_rbda cho TỪNG buổi, ghép kết quả.

    stb_theo_buoi: {buoi: {student_id: so_boc_tham}} — cho phép ba thiết kế
    bốc thăm ở mục 5.3 mà KHÔNG đụng chữ ký compute_club_priority.
    """
```

Trả về `assignment: {student_id: {buoi: club_id | None}}`, cộng
`per_buoi: {buoi: MatchResult}` để mọi số liệu cũ vẫn tra được. Khoảng
**60–80 dòng**, thuần cắt–gọi–ghép, không có logic ưu tiên mới.

### 5.3. Ba thiết kế bốc thăm — đều chỉ là cách sinh `stb_theo_buoi`

| Mã | Tên | Cách sinh | Giữ được tính độc lập? |
|---|---|---|---|
| **A1** | STB tuần | `generate_stb_lottery(sorted(hs), seed)` một lần, dùng cho mọi buổi | ✅ |
| **A2** | STB ngày | mỗi buổi gọi lại với `seed + hash(buoi)` | ✅ |
| **A3** | **STB có bù** | xử lý buổi theo thứ tự; buổi sau xếp lại theo `(số CLB đã có, STB)` — em chưa có gì lên đầu | ❌ **PHÁ** |

**Ràng buộc cài đặt tuyệt đối:** A3 được cài bằng cách **đánh lại bộ số STB
trước khi chạy buổi đó** — tuyệt đối **không** thêm tham số nào vào
`compute_club_priority`. Ràng buộc chống nội sinh ghi ở dòng 63–72 của hàm đó
phải còn nguyên chữ.

> **A3 là cái bẫy, và phải ghi rõ là bẫy.** Nó làm ưu tiên buổi sau phụ thuộc
> **kết cục** buổi trước, mà kết cục lại phụ thuộc nguyện vọng đã khai. Một em
> có thể **cố tình bỏ trống Thứ 3** để giữ ưu tiên cao cho Thứ 5 — đúng kiểu
> khai gian mà cả dự án được dựng lên để loại bỏ. A3 có mặt ở đây để **bị đo**,
> không phải để được khuyến nghị trước khi đo.

### 5.4. Ổn định cho cả tuần

Kết quả tuần **ổn định** ⟺ kết quả **mỗi buổi** ổn định. Không cần định nghĩa
mới: gọi `verify_stability` từng buổi rồi cộng lại. Không có cặp phá vỡ nào bắc
cầu được giữa hai buổi, vì không ràng buộc nào nối hai buổi.

---

## 6. Dữ liệu ra

| Tệp | Nội dung |
|---|---|
| **`ket_qua_thoi_khoa_bieu.csv`** | **Sản phẩm chính** — mỗi em một dòng: `student_id, name, thu_2, …, thu_7, so_clb, so_nv1` |
| `ket_qua_phan_bo_theo_club/<clb>.csv` | giữ nguyên, **thêm cột `buoi`** |
| `ket_qua_theo_buoi/<buoi>.csv` | danh sách theo từng buổi, cho giáo viên trực ngày đó |
| `ket_qua_do_phu.csv` | em trắng tay cả tuần · em trống buổi nào · số CLB mỗi em |
| `ket_qua_danh_sach_cho/<buoi>_<clb>.csv` | hàng chờ theo thứ tự ưu tiên, lấy từ `rejection_log` — dùng khi có em rút |

> ### Lỗ rò dữ liệu phải bịt TRƯỚC khi có tệp đầu tiên
>
> `.gitignore` hiện chặn `ket_qua*.csv` và `ket_qua*_theo_club/`. Tệp
> `ket_qua_theo_buoi/thu_2.csv` có **basename là `thu_2.csv`** nên **không khớp
> luật nào** — nó sẽ lọt vào git. Phải thêm `ket_qua_theo_buoi/` và
> `ket_qua_danh_sach_cho/` vào `.gitignore` ngay ở **giai đoạn 1**.

`run_history` ghi thêm `che_do_boc_tham` và `so_buoi` — không có hai cột này thì
không truy được kết quả cũ chạy bằng thiết kế nào.

---

## 7. Giao diện

Một thành phần mới, dùng lại ở ba chỗ: **lưới tuần** (cột = buổi, ô = CLB kèm
thanh lấp đầy).

| Tab | Thêm gì |
|---|---|
| **04 Quản lý CLB** | Trường `Buổi` trong form · **lưới tuần** toàn trường · **Bảng tải theo buổi**: mỗi buổi bao nhiêu chỗ, bao nhiêu lượt nguyện vọng, tỉ lệ chọi |
| **01 Vận hành** | Chọn thiết kế bốc thăm (A1/A2/A3, A3 kèm cảnh báo đỏ) · kết quả tách **theo từng buổi**: số vòng, số em xếp được, cặp phá vỡ |
| **02 Kết quả** | **Thời khoá biểu**: tra một em → hiện cả tuần · **Theo buổi**: chọn buổi → CLB + danh sách · **Độ phủ**: biểu đồ số em có 0/1/2/…/5 CLB, nêu đích danh em trắng tay |
| **03 Nhập tại chỗ** | Nhập nguyện vọng theo từng buổi, kèm chỉ báo sống *"em mới khai 2 buổi → tối đa 2 CLB"* |
| **05 Nhập điểm** | Nhóm CLB theo buổi cho dễ tìm. Việc chấm **không đổi** — điểm vẫn mù và không phụ thuộc buổi |

**Ưu tiên cao nhất trong nhóm này là Bảng tải theo buổi.** Nó rẻ để làm, và nó
sửa được vấn đề *trước* khi chạy (dời một CLB sang buổi vắng) thay vì phải giải
thích *sau* khi chạy.

---

## 8. Thí nghiệm mới — dùng lại nguyên bộ đo đã có

Thêm `du_lieu_test/do_boc_tham_nhieu_buoi.py`, dùng lại `co_che_doi_chung.py`
và `do_khai_that.py`.

**TN7 — Ba thiết kế bốc thăm** (đóng góp nghiên cứu chính). Mỗi arm đo: phân bố
số CLB/em · **số em trắng tay cả tuần** · Gini · thứ hạng NV trung bình · cặp
phá vỡ từng buổi · **số em khai gian được**.

Dự đoán: A1 và A2 **bằng nhau về trung bình**, A2 thấp hơn hẳn về phương sai và
số em trắng tay; A1 và A2 cho **0 em khai gian**, **A3 khác 0**.

**TN8 — Phân rã có đúng không** (bắt buộc, không phải nghiên cứu):
một buổi ⇒ kết quả **trùng khít** phần mềm cũ, 3 bộ dữ liệu × 20 seed · không
em nào có 2 CLB cùng buổi · cặp phá vỡ mỗi buổi = 0.

**TN9 — Quy mô**: 5 buổi × 12 CLB × 500 em — thời gian chạy, số vòng mỗi buổi.

**TN10 (tuỳ chọn)** — A3 có phụ thuộc **thứ tự xét buổi** không (Thứ 2 trước vs
Thứ 6 trước)? Nếu có, đó là một điểm trừ nữa của A3.

---

## 9. Lộ trình — năm giai đoạn, mỗi giai đoạn dùng được ngay

| GĐ | Việc | Xong là có gì |
|---|---|---|
| **1** | `clubs.buoi` + migration · nhập CSV có `buoi` · Admin UI + lưới tuần + bảng tải · **vá `.gitignore`** | Khai báo được buổi; chạy vẫn y hệt cũ |
| **2** | `run_rbda_nhieu_buoi` · `match_results` khoá chính `(student_id, buoi)` · ba thiết kế bốc thăm · xuất thời khoá biểu | Xếp được cả tuần |
| **3** | Tab Kết quả: thời khoá biểu, theo buổi, độ phủ · Nhập tại chỗ theo buổi | Dùng được thật ở trường |
| **4** | TN7–TN9, mở rộng trang nghiên cứu, **chốt thiết kế bốc thăm bằng số đo** | Trả lời được "dùng cách bốc thăm nào" |
| **5** | Bộ câu hỏi Forms mới · mẫu CSV · `HUONG_DAN_SU_DUNG` | Bàn giao được |

### Hai tệp đụng nhiều nhất

- `rbda_priority_pipeline.py` — **chỉ thêm**, không sửa 5 hàm lõi.
- `api.py` — `run_pipeline`, `import_clubs_csv`, `import_preferences_csv`,
  `export_csv`, `get_match_results`, `get_club_fill_stats` đều đọc
  `match_results` nên phải cập nhật theo khoá chính mới.

### Chỗ rủi ro nhất: migration `match_results`

Khoá chính đổi từ `student_id` sang `(student_id, buoi)` — khoá này **tự nó
canh ràng buộc "≤1 CLB mỗi buổi" ở tầng cơ sở dữ liệu**, không chỉ ở tầng mã.

Quy trình: sao lưu bằng `_backup_db()` có sẵn → tạo bảng mới → chép dòng cũ với
`buoi = '__mac_dinh__'` → đổi tên. **`run_history` không được đụng tới** — đó
là dấu vết kiểm toán, `reset_data` cũng không xoá nó.

---

## 10. Những bẫy đã biết — ghi ra để không vấp

| Bẫy | Xử lý ở v1 |
|---|---|
| **CLB có hai lớp khác ngày, em chỉ vào một** | v1 **cấm**. Nếu cần thì tách thành hai CLB riêng và chấp nhận em có thể trúng cả hai |
| **Sàn sĩ số** (CLB dưới N em thì không mở) | Ràng buộc sàn **phá tính ổn định**. v1 **chỉ báo cáo** *"3 CLB dưới sàn"*; người phụ trách quyết định huỷ rồi chạy lại — và phải ghi rõ chạy lại **không** còn là kết quả ổn định của bài toán gốc |
| **Số phòng mỗi buổi có hạn** | v1 chỉ hiện trong Bảng tải theo buổi, không đưa vào ràng buộc |
| **Em khai lệch buổi** | Soát khi nhập, nêu đích danh dòng |
| **Danh sách 10 NV chia cho 5 buổi** | Không còn là vấn đề: mỗi buổi có danh sách riêng, mỗi buổi tới 10 lựa chọn |

Tuỳ chọn để sau, không thuộc v1: xuất lịch `.ics`; công cụ *"nếu dời CLB X sang
buổi khác thì sao"*.

---

## 11. Kiểm chứng

```bash
# 1. Không hồi quy — điều kiện tiên quyết của cả kế hoạch
python3 -m pytest tests/ -q                 # 482 test phải xanh như trước

# 2. Test TRÙNG KHÍT: một buổi ⇒ y hệt phần mềm cũ (test quan trọng nhất)
python3 -m pytest tests/test_nhieu_buoi.py -q

# 3. Bộ đo cũ không đổi số — chứng tỏ thuật toán lõi không bị đụng
python3 du_lieu_test/do_toi_uu_on_dinh.py
python3 du_lieu_test/do_khai_that.py

# 4. Thí nghiệm mới
python3 du_lieu_test/do_boc_tham_nhieu_buoi.py

# 5. Đối chứng ngược — bộ đo mới phải BẮT được lỗi thật
#    bỏ lọc theo buổi -> test "≤1 CLB mỗi buổi" phải đỏ
#    cài A3 thành A1   -> TN7 phải mất hết chênh lệch giữa các arm
```

**Định nghĩa "xong" của giai đoạn 2:** test trùng khít xanh trên cả ba bộ dữ
liệu × 20 seed. Chừng nào nó chưa xanh thì mọi số trong `NGHIEN_CUU_TOI_UU.md`
chưa chắc còn nói về đoạn mã đang chạy.

---

*Tài liệu này mô tả **thiết kế và hệ quả kỹ thuật**. Phần nhận định về việc
trường nên chọn thiết kế bốc thăm nào, cái giá nào chấp nhận được, và ý nghĩa
khoa học của kết quả — người thực hiện đề tài tự viết (Phụ lục 1).*


---

## 12. Đã làm tới đâu

**Cả năm giai đoạn xong.** Phần mềm khai báo được buổi, xếp được cả tuần, có
đủ ba màn hình mới, ba thiết kế bốc thăm đã được đo chính thức (TN7, mục
`NGHIEN_CUU_TOI_UU.md`), và bộ câu hỏi Forms kèm mẫu CSV nhiều buổi đã có
(`BO_CAU_HOI_FORMS.md`, `mau_csv/` tệp `06_`–`08_`). Ba bộ đo cũ ra đúng số cũ,
và năm hàm lõi không sửa một dòng.

Hai việc làm THÊM sau khi lộ trình năm giai đoạn đã chốt, vì dùng thật mới lộ
ra: **chọn buổi để xếp** (xếp lại một ngày mà không đụng ngày đã công bố) và
**trần nguyện vọng tính theo từng buổi** (trần cũ đếm cả tuần, âm thầm gạt
31/180 em của một bộ dữ liệu thử ra khỏi đợt xếp).

| Giai đoạn | Trạng thái |
|---|---|
| 1 — Buổi vào dữ liệu, di trú, `.gitignore` | ✅ xong |
| 2 — `run_rbda_nhieu_buoi`, ba cách bốc thăm, xuất thời khoá biểu | ✅ xong |
| 3 — Lịch tuần, bảng tải, thời khoá biểu, độ phủ, song ngữ | ✅ xong |
| 4 — Đo lường TN7 và mở rộng trang nghiên cứu | ✅ xong |
| 5 — Bộ câu hỏi Microsoft Forms mới | ✅ xong |

### Bốn chỗ thiết kế phải sửa khi chạm vào mã thật

1. **Một buổi thì ba cách bốc thăm phải cho CÙNG kết quả.** Bản đầu để
   `stb_ngay` xáo lại cả khi chỉ có một buổi — nghĩa là một trường chỉ tổ chức
   một buổi mà lỡ chọn cách đó sẽ nhận kết quả khác bản cũ, không vì lý do gì.
   Đã chặn ở `sinh_stb_theo_buoi`, có test canh.

2. **Ba cách bốc thăm đều phải dẫn xuất từ bộ số ĐÃ KHOÁ.** Thiết kế ban đầu
   để `stb_ngay` tự bốc bộ số mới mỗi buổi — làm thế thì cơ chế `stb_lock` mất
   nghĩa ở đúng cách bốc thăm cần nó nhất. Bản cài đặt hoán vị VỊ TRÍ trong
   dàn số đã khoá, nên tính "không phụ thuộc thứ tự nhập liệu" được thừa kế
   nguyên vẹn.

3. **Tỉ lệ chọi phải đếm theo SỐ HỌC SINH, không phải số lượt nguyện vọng.**
   Mỗi em chỉ lấy được một chỗ trong một buổi, nên đếm theo lượt làm mọi buổi
   trông như nhau (đo được: 4,1× tới 6,5× ở mọi buổi) đúng lúc cần nó phân
   biệt buổi chật với buổi rộng (đếm đúng: 0,88× tới 4,92×).

4. **Bảng kết quả và huy hiệu "chưa được xếp" phải đổi nghĩa.** Một em giờ có
   một dòng cho mỗi buổi, nên bảng phồng lên gấp số buổi (160 em × 5 buổi =
   800 dòng) và huy hiệu đếm số Ô TRỐNG chứ không phải số EM trắng tay — 593
   thay vì 38. Ở chế độ nhiều buổi, bảng chỉ liệt kê chỗ đã xếp thật, còn con
   số "em trắng tay" lấy từ bảng Độ phủ.

### Dự đoán về bốc thăm: bị bác bỏ ở đâu, được xác nhận ở đâu

Mục 5.3 ghi một dự đoán trước khi đo: **`stb_ngay` (A2) sẽ giảm hẳn số em trắng
tay**. Giai đoạn 4 đã đo (TN7 trong `NGHIEN_CUU_TOI_UU.md`,
`du_lieu_test/do_boc_tham.py`, 23 test canh). Kết quả chia làm ba câu:

1. **Trên dữ liệu của trường, dự đoán gần như không đúng.** Bộ mẫu 5 buổi, 160
   em có khai, **200 seed** ghép cặp: A1 để lại **36,50** em trắng tay, A2
   **36,26**. Hiệu **+0,245 em**, khoảng tin cậy 95% **[+0,020 ; +0,465]** — thật
   nhưng bằng **0,15%** số em. Không phải mức "giảm hẳn" mà dự đoán nói tới.

2. **Trên dữ liệu thuần bốc thăm, dự đoán đúng và đúng rất mạnh.** 200 em /
   5 buổi / mọi em Tầng 2: A2 cứu được **1,2 → 79,0** em, thắng ở **mọi** mức
   tỉ lệ chọi, không khoảng tin cậy nào chứa 0. Nên cài đặt đúng, cơ chế đúng;
   chỉ là điều kiện áp dụng hẹp hơn lúc nêu dự đoán.

3. **Nguyên nhân là ĐIỂM, không phải thiếu ghế.** Giả thuyết ghi ở bản trước —
   *"em trắng tay trượt vì thiếu chỗ chứ không vì thua bốc thăm"* — đã bị bác
   bỏ hai lần: 33/38 em trắng tay có khai từ hai buổi trở lên, và ở chọi
   **4,0×** (thiếu ghế trầm trọng) A2 vẫn cứu **79** em. Thí nghiệm can thiệp
   TN7c chỉ ra nguyên nhân thật: vặn tỉ lệ em **có điểm** từ 0% lên 100% thì
   lợi thế của A2 đi từ **92%** số em A1 bỏ lại xuống tới *không phân biệt
   được*; vặn độ mịn thang điểm cho y hệt (**91%** ở thang 1 mức → **0%** ở
   thang 61 mức). Tầng 1 luôn đứng trên Tầng 2, nên em không có điểm là Tầng 2
   ở **mọi** buổi — rủi ro đã tương quan sẵn qua điểm chứ không qua bộ số thăm,
   và bốc lại thăm mỗi buổi không gỡ được mối tương quan đó.

**A3 thì đã có bằng chứng, không còn là suy luận.** TN7d dò kênh *giấu bớt
buổi*: **113/300** em có cách khai gian có lợi dưới A3, **0/300** dưới A1 và
A2. Kênh đó là kênh đánh đổi (phải bỏ một suất buổi trước để lên trước ở buổi
sau), nhưng thế vẫn đủ hỏng: em nào biết mẹo thì đổi được, em nào khai thật thì
không.

### Hai lỗi của chính bộ đo, ghi lại vì chúng là lý do các test canh tồn tại

1. **Kết luận trên một seed.** Bảng trong bản trước của mục này (38 / 38 / 37)
   là **một** lần chạy ở seed 42. Một seed không đủ để so ba thiết kế bốc thăm,
   vì chính cái đang đo là tác động của may rủi: dao động theo seed trên bộ đó
   là **6 em**, gấp tám lần khoảng cách giữa ba thiết kế. Mọi số của TN7 giờ
   đều là trung bình nhiều seed, ghép cặp theo seed, kèm khoảng tin cậy.

2. **In sai chiều hiệu số.** Một bản đo trung gian in nhãn *"(âm = A2 tốt hơn)"*
   cho hiệu `A1 − A2` trên số em trắng tay, trong khi âm nghĩa là A1 **ít** em
   trắng tay hơn, tức A1 tốt hơn. Nhãn được gõ tay nên không đi theo công thức,
   và không có gì phát hiện ra: mã chạy đúng, số đúng, chỉ câu chữ dẫn người
   đọc sang kết luận ngược. Nay nhãn do `mo_ta_chieu()` sinh ra từ chính các
   biến đã dùng để tính hiệu, và `tests/test_boc_tham.py` có bốn test canh
   chiều dấu — đảo dấu trong `hieu_theo_cap` làm đỏ ba trong số đó.

### Đã chốt: phần mềm chỉ chạy A2, bỏ hẳn hai thiết kế kia

Bản trước để mặc định **A1** kèm một bộ chọn ba thiết kế và một bảng đối chiếu,
với lý do "đây là câu hỏi của trường, phép đo không quyết thay được". Đã chốt
theo hướng khác: **phần mềm chạy duy nhất A2 `stb_ngay`**, không còn bộ chọn,
không còn bảng đối chiếu, `api.run_pipeline` không còn nhận tham số chế độ.

**Vì sao chốt được:**

1. **A2 không thua ở ô nào đã đo**, và hơn hẳn ở mọi vùng bốc thăm quyết định
   (cứu 1,2 → 79,0 em trên 200). Trên dữ liệu có điểm của trường nó chênh 0,15%
   — tức gần như miễn phí, không phải một cái giá.
2. **Một buổi thì A2 ≡ A1** nhờ nhánh ngắn mạch trong `sinh_stb_theo_buoi`, nên
   không con số nào trong `NGHIEN_CUU_TOI_UU.md` phải đo lại. Có test canh trên
   ba bộ dữ liệu × 20 seed, và một test nữa canh qua đúng đường `api.run_pipeline`.
3. **A3 có bằng chứng để loại**, không còn là lo ngại lý thuyết: 113/300 em
   giấu bớt buổi thì có lợi, A1 và A2 đều 0/300 (TN7d).
4. **Cái giá minh bạch em nêu ở bản trước là sai.** Ghi rằng A2 buộc trường
   "công bố năm bảng số thăm thay vì một" — không đúng. Thứ tự từng buổi là hàm
   TẤT ĐỊNH của bộ số đã khoá và `seed`, nên trường vẫn chỉ công bố **hai** thứ
   như cũ và ai cũng tính lại được. Cái thiếu thật sự là phần mềm chưa **hiện**
   thứ tự ấy ra — `stb_theo_buoi` được tính rồi vứt đi. Đã thêm bảng **Số bốc
   thăm theo buổi** ở thẻ Kết quả và tệp `..._so_boc_tham_theo_buoi.csv`.

**Hai thiết kế kia vẫn còn trong `rbda_priority_pipeline.py`, và đó là cố ý.**
Chúng là đối chứng của TN7: xoá đi thì `do_boc_tham.py` không chạy được nữa và
mọi con số TN7 mất khả năng tái lập. Chúng đổi vai trò từ *lựa chọn sản phẩm*
thành *dụng cụ đo*. `TestMotThietKeDuyNhat` canh cả hai chiều: không có đường
nào từ `api.py` gọi tới chúng, và chúng không bị xoá khỏi thuật toán.

**Việc phải làm khi nâng cấp một trường đang chạy:** trường đã chạy nhiều buổi
bằng bản cũ thì lần chạy tới ra kết quả khác (bộ số đã khoá không đổi, thứ tự
trong từng buổi thì đổi). Trường một buổi không đổi gì. Dòng nhật ký cũ ghi
`stb_tuan` **không bị sửa lại**, và `get_so_boc_tham_theo_buoi` đọc chính cột
đó để dựng lại đúng thứ tự mà lần chạy ấy đã dùng — bảng luôn trung thực với
lần chạy có thật, kể cả lần chạy bằng bản cũ.
