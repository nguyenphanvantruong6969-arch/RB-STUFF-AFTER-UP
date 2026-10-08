# Giải đáp về bốc thăm — ba câu hỏi hay gặp

> **Bản trình bày (trang web):** `GIAI_DAP_BOC_THAM.html` — cùng nội dung, có
> biểu đồ, mở bằng trình duyệt bất kỳ. Bản trực tuyến:
> https://claude.ai/code/artifact/449066d6-148b-4978-be60-cc422db69cdf

> **Mọi con số trong tệp này đều do đo mà có, không phải nói chay.** Cuối mỗi
> câu có lệnh chạy lại. Chạy lại lúc nào cũng ra đúng bằng đó — không có gì phụ
> thuộc đồng hồ hay máy tính đang dùng.
>
> Tái lập toàn bộ tệp này bằng một lệnh:
> ```
> python du_lieu_test/do_cau_hoi_boc_tham.py
> ```

## Trước hết: bốc thăm được dùng ở đâu

Mỗi câu lạc bộ xếp hạng học sinh nộp đơn theo **hai khoá, có thứ tự**
(`rbda_priority_pipeline.py`, hàm `club_priority_order`):

```python
key=lambda sid: (-tested_scores_for_club[sid], stb_lottery[sid])
#                 ^^^^^ ĐIỂM đứng trước         ^^^^^ bốc thăm chỉ đứng sau
```

Nghĩa là bốc thăm **chỉ** được dùng ở đúng hai chỗ:

1. Hai em **bằng điểm nhau** ở cùng một CLB.
2. Em dự tuyển một CLB mà **không thi** CLB đó (không có điểm để so).

Em có điểm cao hơn thì **luôn** đứng trên, mọi lúc, bất kể bốc thăm ra sao.
Đây là mệnh đề quan trọng nhất trong cả tệp này, và nó có test canh riêng —
xem cuối Câu 1.

---

## Câu 1 — Đổi seed có làm bốc thăm mất công bằng không?

**Không.** Đổi seed cho ra một bộ số bốc thăm khác, nhưng **không em nào được
lợi hay bị thiệt một cách có hệ thống**.

Đo trên **100 học sinh, 10 000 lần bốc thăm**:

| | Giá trị |
|---|---|
| Thứ hạng trung bình, **nếu công bằng tuyệt đối** | 49,50 |
| Thứ hạng trung bình **tốt nhất** trong 100 em | 48,88 |
| Thứ hạng trung bình **kém nhất** trong 100 em | 50,21 |
| Chênh lệch lớn nhất so với lý thuyết | **0,71 — tức 1,44%** |

| Tỉ lệ lọt vào nhóm 10% đầu bảng | Giá trị |
|---|---|
| Nếu công bằng tuyệt đối | 10,00% |
| Em ít lọt vào nhất trong 100 em | 9,38% |
| Em hay lọt vào nhất trong 100 em | 10,98% |

Không em nào lệch quá 1,5% so với lý thuyết sau 10 000 lần bốc.

### Mã học sinh có "kéo" thứ hạng không?

Câu hỏi này đáng hỏi, vì bộ số bốc thăm sinh ra từ **danh sách mã đã sắp xếp**
(lý do: xem Câu 2). Nếu mã nhỏ hay được số nhỏ thì bốc thăm thiên vị.

**Hệ số tương quan** là phép tính đo xem hai thứ có đi cùng nhau không. Bằng
**0** nghĩa là chẳng liên quan gì; bằng **+1** hoặc **−1** nghĩa là biết cái này
là đoán chắc được cái kia. Ở đây ta hỏi: *em có mã nhỏ hơn thì có hay được thứ
hạng tốt hơn không?*

Với 100 học sinh, ngay cả khi **hoàn toàn không có** liên hệ nào, con số đo được
vẫn tự dao động quanh 0 trong khoảng **±0,10**. Khoảng đó gọi là **ngưỡng
nhiễu**. Nên **một lần đo không kết luận được gì** — phải đo nhiều lần độc lập.

Đo **8 lần**, mỗi lần 10 000 lượt bốc thăm hoàn toàn riêng biệt, không lần nào
dùng lại seed của lần nào:

| Lần đo | Dùng seed số | Kết quả |
|---|---|---|
| Lần 1 | 1 – 10 000 | +0,1142 |
| Lần 2 | 10 001 – 20 000 | +0,0527 |
| Lần 3 | 20 001 – 30 000 | +0,1539 |
| Lần 4 | 30 001 – 40 000 | **−0,0155** |
| Lần 5 | 40 001 – 50 000 | +0,0827 |
| Lần 6 | 50 001 – 60 000 | **−0,0470** |
| Lần 7 | 60 001 – 70 000 | **−0,0250** |
| Lần 8 | 70 001 – 80 000 | +0,0909 |

| | |
|---|---|
| Trung bình của 8 lần đo | +0,0509 |
| Mức chênh lệch **giữa các lần đo** | 0,0727 |
| Ngưỡng nhiễu — mức dao động tự nhiên | 0,1005 |

**Đọc bảng này thế nào.** Kết quả **đổi cả dấu** — ba lần đo ra giá trị **âm**. Mức
chênh lệch giữa các lần đo (0,073) còn **lớn hơn** chính giá trị trung bình (0,051), và
khối lệch nhiều nhất cũng chỉ bằng **1,53 lần** ngưỡng nhiễu.

Một thiên vị **thật** thì phải giữ nguyên dấu qua mọi lần đo — mã nhỏ đã được
ưu ái thì lần nào cũng phải được ưu ái. Cái này đổi
dấu, nên đó là **nhiễu thống kê, không phải thiên vị**.

> Đo một lần rồi kết luận là sai phương pháp. Lần đầu cho +0,1142, nhìn qua thì
> tưởng có xu hướng thật, và suýt nữa đã ghi vào tài liệu như vậy.

### Còn mệnh đề quan trọng nhất

Bốc thăm **không đụng được** vào chỗ điểm đã quyết định. Test dựng riêng
(`tests/test_anh_huong_seed.py`): ba em, ba điểm khác nhau, tranh hai suất.

| Số seed đã thử | Số lần kết quả khác đi |
|---|---|
| 100 | **0** |

Em điểm cao nhất luôn vào, em điểm thấp nhất luôn trượt. Đã kiểm chứng test này
bắt được lỗi thật: đảo hai khoá xếp hạng thì test **đỏ ngay ở seed đầu tiên**.

```
python du_lieu_test/do_cau_hoi_boc_tham.py
python -m pytest tests/test_anh_huong_seed.py -v
```

---

## Câu 2 — Đổi thứ tự nhập dữ liệu có ảnh hưởng không?

**Không.** Và đây là chỗ **đã từng có lỗi thật, đã sửa, và có test canh.**

Đo: 20 học sinh, **cố ý cho tất cả hoà điểm** — tức đặt đúng vào chỗ duy nhất mà
bốc thăm có quyền can thiệp. Nhập lại **20 lần theo 20 thứ tự xáo ngẫu nhiên**
khác nhau:

| | Kết quả |
|---|---|
| Số lần bộ **số bốc thăm** khác bản gốc | **0 / 20** |
| Số lần **kết quả xếp CLB** khác bản gốc | **0 / 20** |

Đối chứng ngược lại — đổi seed thì **phải** khác, nếu không thì phép đo trên vô
nghĩa:

| | Kết quả |
|---|---|
| 50 seed, số seed cho bộ số khác seed 42 | **49 / 49** |

### Vì sao chỗ này từng sai

Đây là **lỗi 19** của dự án (xem `BAN_GIAO.md` mục 5). `random.shuffle` xáo
**đúng danh sách được đưa vào**, mà `load_from_sqlite` đọc bảng `students` không
có `ORDER BY` nên SQLite trả về **theo thứ tự chèn**. Hệ quả: cùng một trường,
cùng seed, nhập theo thứ tự khác là ra kết quả khác.

Đo lúc đó — 10 em **bằng điểm nhau**, cùng `seed = 42`, chỉ đổi thứ tự chèn:

| Thử nghiệm | Kết quả |
|---|---|
| Nhập xuôi so với nhập ngược, **trước khi sửa** | **6 / 10 em vào CLB khác** |
| Cùng thử nghiệm, **sau khi sửa** | **0 em khác** |

Sửa bằng **một dòng** — sắp xếp trước khi xáo (`generate_stb_lottery`):

```python
shuffled = sorted(student_ids)   # <- dòng này
rng.shuffle(shuffled)
```

Có `tests/test_stb_khong_phu_thuoc_thu_tu.py` canh riêng chỗ này.

> **Cách nói đúng về việc này:** *"bốc thăm không phụ thuộc thứ tự nhập liệu"*.
> **Không** được nói *"số bốc thăm dựa trên mã học sinh"* — mã học sinh chỉ dùng
> để **sắp xếp danh sách trước khi xáo**, chứ không quyết định số. Bằng chứng
> chính là bảng tương quan ở Câu 1.

```
python -m pytest tests/test_stb_khong_phu_thuoc_thu_tu.py -v
```

---

## Câu 3 — Những gì ảnh hưởng tới bộ số bốc thăm?

**Đúng hai thứ: SỐ SEED và TẬP MÃ HỌC SINH.** Không có thứ ba.

Thử đổi từng thứ một, giữ nguyên mọi thứ còn lại:

| Đổi thứ này | Bộ số bốc thăm |
|---|---|
| **Số seed** (42 → 43) | **ĐỔI** |
| **Thêm 1 học sinh** vào danh sách | **ĐỔI** — chỉ 6/100 em giữ nguyên số |
| **Bớt 1 học sinh** khỏi danh sách | **ĐỔI** — chỉ 5/99 em giữ nguyên số |
| Thứ tự danh sách (đảo ngược) | không đổi |
| Thứ tự danh sách (100 lần xáo ngẫu nhiên) | không đổi, cả **100/100** |
| Chạy lại y nguyên | không đổi |

**Không** ảnh hưởng: thứ tự nhập, họ tên học sinh, điểm số, giờ chạy, máy tính
đang dùng, hệ điều hành.

### Hai điều rút ra từ bảng trên

**Thêm hoặc bớt một học sinh làm đổi số của gần như tất cả mọi người.** Chỉ 6
trên 100 em giữ nguyên số. Đây là tính chất của phép xáo, không phải lỗi — nhưng
nó có hệ quả thực tế quan trọng, dẫn sang điều thứ hai.

**Vì thế bốc thăm bị KHOÁ sau lần chạy đầu.** Nếu không khoá, chỉ cần thêm một
em vào danh sách là toàn bộ bộ số đổi, và kết quả đã công bố có thể lật ngược.
Cơ chế đang chạy (`api.py`, `run_pipeline`):

- Chạy lần đầu → vẽ toàn bộ số bốc thăm rồi **khoá** (`stb_lock`).
- Đã khoá, có học sinh mới → **chỉ cấp số bổ sung** cho em mới, đánh số tiếp nối
  sau số lớn nhất hiện có. **Không vẽ lại** số của ai đã có.
- Muốn vẽ lại toàn bộ → phải bật cờ `force_redraw_stb`, là hành động cố ý.

### Chống việc bốc đi bốc lại để chọn kết quả vừa ý

Vì seed *có* đổi số phận của một số em, việc bốc lại nhiều lần rồi chọn kết quả
mình thích là rủi ro thật. Ba lớp đang chặn:

| Lớp | Cơ chế |
|---|---|
| 1 | `stb_lock` khoá bộ số sau lần chạy đầu |
| 2 | Vẽ lại phải bật cờ `force_redraw_stb` — không lỡ tay được |
| 3 | **`run_history` ghi thêm một dòng mỗi lần chạy**, kèm `seed` và cờ `stb_redrawn`, kèm giờ |

Lớp thứ ba là lớp quan trọng nhất: bảng `run_history` **không bao giờ bị ghi
đè**, và chức năng xoá dữ liệu (`reset_data`) **không đụng tới nó**. Ai bốc lại
để dò seed đẹp đều để lại dấu vết **không xoá được** — đủ cả seed đã thử lẫn mốc
thời gian. Xem được ngay trong phần mềm, mục **Lịch sử chạy pipeline**.

```
python du_lieu_test/do_cau_hoi_boc_tham.py
```

---

## Câu 4 — Nhiều buổi thì sao? Có phải bốc mấy lần không?

Trường tổ chức nhiều buổi trong tuần thì phần mềm **xáo lại thứ tự ở mỗi
buổi**. Nghe qua thì như bốc thăm nhiều lần, và câu hỏi đi kèm là câu đáng
hỏi: *vậy có phải công bố năm bảng số thăm không, và ai kiểm được?*

**Không. Vẫn chỉ bốc MỘT lần, và vẫn chỉ công bố MỘT thứ.**

### Vì sao phải xáo lại

Dùng chung một bộ số cho cả tuần thì em rút phải số xấu đứng cuối Tầng 2 ở
**mọi** buổi. May rủi không tản ra mà **cộng dồn** lên đúng một em: rủi ở thứ
Hai thì cũng rủi ở thứ Sáu, vì vẫn là con số ấy.

Đo được (TN7, `NGHIEN_CUU_TOI_UU.md`): trên dữ liệu mà bốc thăm quyết định,
xáo lại mỗi buổi cứu được **1,2 tới 79,0 em trên 200** khỏi cảnh trắng tay cả
tuần, tuỳ mức chật. Nó **không tạo thêm chỗ** — số câu lạc bộ trung bình mỗi em
gần như không đổi — nó chỉ đổi **ai** được chỗ: bớt cảnh vài em ôm nhiều câu
lạc bộ còn nhiều em không có gì.

### Vì sao vẫn kiểm được

Thứ tự của từng buổi **không phải bốc mới**. Nó là hàm của đúng hai thứ:

```
thứ tự buổi d  =  f( bộ số ĐÃ KHOÁ ,  seed ,  tên buổi d )
```

Quy tắc `f` cố định, không có nguồn ngẫu nhiên nào khác chen vào, và nó dùng
`zlib.crc32` chứ không dùng `hash()` của Python — `hash()` của chuỗi bị ngẫu
nhiên hoá theo từng tiến trình, nên cùng dữ liệu cùng seed vẫn ra hai kết quả
khác nhau ở hai lần mở máy. Đó đúng là loại lỗi không ai phát hiện ra cho tới
khi có người đối chiếu hai lần chạy. Có test canh riêng chỗ này, và nó chạy
phép so giữa **hai tiến trình** khác nhau.

Hệ quả cho nhà trường:

| | |
|---|---|
| Công bố mấy thứ? | **Hai**: bộ số đã khoá, và con số gieo (`seed`) |
| Ai kiểm lại được? | Bất kỳ ai có hai thứ đó — thứ tự từng buổi phải ra đúng bảng của trường |
| Bốc mấy lần? | **Một**. `stb_lock` vẫn khoá đúng một bộ số như trước |
| Xem thứ tự từng buổi ở đâu? | Thẻ **Kết quả** → bảng **Số bốc thăm theo buổi**, và tệp `..._so_boc_tham_theo_buoi.csv` |

### Còn cách "em chưa có câu lạc bộ nào thì được ưu tiên buổi sau"?

Nghe công bằng, và **đã bị loại sau khi đo**. Nó làm ưu tiên buổi sau phụ thuộc
**kết cục** buổi trước, mà kết cục lại phụ thuộc nguyện vọng đã khai — tức là
mở đúng cái kênh khai gian mà cả phần mềm được dựng lên để bịt.

Đo được: **113/300** em tìm được cách giấu bớt một buổi để có lợi dưới cách đó,
trong khi hai cách kia đều **0/300**. Phần mềm không chạy nó.

---

## Bảng tra nhanh

| Câu hỏi | Trả lời | Số đo |
|---|---|---|
| Đổi seed, bốc thăm còn công bằng không? | Còn | Lệch tối đa **1,44%** / 10 000 lần bốc |
| Nhiều buổi thì bốc mấy lần? | **Một** | Thứ tự từng buổi suy ra tất định từ bộ số đã khoá + seed |
| Xáo lại mỗi buổi có đáng không? | Có | Cứu **1,2 → 79,0** em trên 200, tuỳ mức chật |
| Cách "có bù" thì sao? | **Đã loại** | **113/300** em khai gian được; hai cách kia **0/300** |
| Mã học sinh có kéo thứ hạng không? | Không | Tương quan **đổi dấu** qua 8 khối seed |
| Bốc thăm có lật được kết quả của em điểm cao hơn không? | Không | **0/100** seed |
| Đổi thứ tự nhập có ảnh hưởng không? | Không | **0/20** lần xáo |
| Đổi seed thì bộ số có thật sự đổi không? | Có | **49/49** seed |
| Có bao nhiêu thứ ảnh hưởng tới bốc thăm? | **Hai** | Seed và tập mã học sinh |
| Bốc lại có bị phát hiện không? | Có | `run_history`, không ghi đè, không xoá được |

---

## Tài liệu liên quan

| Tệp | Nội dung |
|---|---|
| `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` mục 3c | Ảnh hưởng của seed lên **kết quả phân bổ** (không phải lên bộ số) |
| `HUONG_DAN_SU_DUNG.md` mục 12 | Thuật toán hoạt động thế nào |
| `BAN_GIAO.md` mục 5 | Lỗi 19 (thứ tự nhập) và mục "ĐÃ ĐO, KHÔNG PHẢI LỖI" |

---

**Về dữ liệu dùng để đo.** Toàn bộ học sinh trong các phép đo trên là **dữ liệu
mô phỏng do máy sinh ra**, không phải học sinh có thật. Các mã như *HS001,
HS002…* chỉ là mã đánh số tự động để phân biệt, không tương ứng với người nào.

*Tệp này chỉ trình bày **số đo và cơ chế**. Phần nhận xét, diễn giải ý nghĩa và
kết luận về kết quả phân bổ do người thực hiện đề tài tự viết.*
