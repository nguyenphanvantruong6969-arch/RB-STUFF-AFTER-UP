# Bảng tra poster — điền gì vào ô nào

Poster ba lá, mở phẳng **200 × 150 cm**, gập lại **rộng 100 · sâu 50 · cao 150 cm**.
Kiểu **quảng cáo**: ít chữ, hình lớn, một thông điệp chính.

> ## Ai làm phần nào
> | Phần | Ai làm | Trạng thái |
> |---|---|---|
> | Khung, màu, cỡ chữ, vị trí các ô | AI | ✅ xong — `poster_khung_200x150cm.pdf`, `poster_khung_1-2.pptx` |
> | Ảnh giao diện thật, sơ đồ (nhãn *"Sơ đồ do AI tạo ra"*), biểu đồ (nhãn *"Dữ liệu mô phỏng"*), 3 con số | AI | ✅ xong — đã đặt sẵn trong khung |
> | **Mọi ô chữ `[ … ]`** — H1–H3, T1–T3, G1–G2, S1–S3, P1–P6 | **Học sinh** | ⬜ chờ em viết |
>
> Phụ lục 1 cấm AI viết bản thảo poster (`BAN_GIAO.md` mục 6). Tệp này **không có câu
> viết sẵn** — chỉ có: câu hỏi gợi ý, độ dài tối đa, và **số liệu đã kiểm chứng kèm
> nguồn** để em tự viết câu của mình.

**Sửa được những gì trong `poster_khung_1-2.pptx`:** mọi ô chữ, 3 con số, ô QR, nền và
màu từng ô; **sơ đồ "Cách hoạt động"** là hình khối + chữ (nhóm "So do 5 lop" — bấm đúp để sửa từng
hộp); **hai biểu đồ** là biểu đồ gốc PowerPoint (chuột phải → *Edit Data* để đổi số, bấm
vào cột để đổi màu). Chỉ **2 ảnh chụp giao diện** là ảnh — vì đó là ảnh chụp thật.
Bản PDF/PNG vẫn dùng hình ảnh để in cho nét.

**Cách điền:** mở `poster_khung_1-2.pptx`, gõ đè lên từng ô `[ … ]`. Hoặc gửi chữ cho
AI, AI chỉ đặt vào đúng ô, sửa chính tả, cắt cho vừa — **không thêm ý**.

Mã ô ghi ngay trong khung và trong `poster_huong_dan.pdf`.

```
 LÁ TRÁI (50 cm)          LÁ GIỮA (100 cm)                          LÁ PHẢI (50 cm)
┌────────────────┐ ┌──────────────────────────────────────────┐ ┌────────────────┐
│ 01 Vấn đề   T1 │ │ H1 lĩnh vực                              │ │ 05 Lợi ích     │
│                │ │ H2 THÔNG ĐIỆP CHÍNH                      │ │   P1 P2 P3 P4  │
│                │ │ H3 tên đề tài                            │ │                │
├────────────────┤ ├─────────────────────────┬────────────────┤ ├────────────────┤
│ 02 Dùng thế nào│ │ [ảnh tab Kết quả]       │ S1  0          │ │ 06 Đã kiểm     │
│ [ảnh Vận hành] │ │                         │ S2  0,14 giây  │ │    chứng       │
│ T2             │ │ G1                      │ S3  816        │ │ [2 biểu đồ] P5 │
├────────────────┤ ├─────────────────────────┴────────────────┤ │                │
│ 03 Xem thử     │ │ 04 Cách hoạt động  [sơ đồ + bốc thăm]     │ ├────────────────┤
│ [QR]  T3       │ │ G2                                       │ │ Tuyên bố AI P6 │
└────────────────┘ └──────────────────────────────────────────┘ └────────────────┘
```

---

## 0. Ba điều sai là hỏng cả poster

1. **Không có tên trường** — kể cả chữ viết tắt ("VAS") hay ảnh có logo, đồng phục,
   bảng tên. Các báo cáo cũ và `BAN_GIAO.md` có ghi tên trường: **chép đoạn nào sang
   là phải soát**. Cũng không có logo trường, mã dự án, tên giáo viên hướng dẫn, tên
   học sinh.
2. **QR không trỏ tới GitHub.** Địa chỉ repo chứa tên tài khoản → lộ tên học sinh.
   Chỉ dùng QR tới một video demo đăng ẩn danh (không tên kênh thật, không tên trong video).
3. **Mọi con số đều từ DỮ LIỆU MÔ PHỎNG** (khảo sát chưa thu). Viết như số khảo sát
   thật là **bịa đặt dữ liệu**. Hình và ô S1–S3 đã ghi sẵn "dữ liệu mô phỏng" — đừng xoá.

---

## 1. Lá giữa — thứ người qua đường thấy đầu tiên

### H1 · Lĩnh vực dự thi
| | |
|---|---|
| Nên có | Đúng tên lĩnh vực trong hồ sơ đăng ký |
| Độ dài | 1 dòng, ≤ 40 ký tự, viết hoa |
| Nguồn | Hồ sơ đăng ký của em (không có trong repo) |

### H2 · Thông điệp chính (chữ to nhất poster, 140 pt)
| | |
|---|---|
| Câu hỏi gợi ý | Đứng cách 3 m, người xem phải hiểu **một** điều gì? Lợi ích lớn nhất cho học sinh là gì — nói bằng lời của học sinh, không bằng thuật ngữ? |
| Độ dài | **≤ 60 ký tự, tối đa 2 dòng** (mỗi dòng ~ 30 ký tự ở cỡ 140 pt) |
| Tránh | Thuật ngữ ("Deferred Acceptance", "RB-DA", "ổn định") — để dành cho ô 04. Khẳng định không có số đỡ ("công bằng tuyệt đối", "tốt nhất"). |
| Số có thể dựa vào | Xem **Ngân hàng số liệu** mục 4 — chọn đúng một ý |

### H3 · Tên đề tài đầy đủ
| | |
|---|---|
| Nên có | Tên đề tài **y hệt** hồ sơ đăng ký |
| Độ dài | 1 dòng ở 48 pt ≈ ≤ 90 ký tự; dài hơn thì 2 dòng |

### Ảnh tab Kết quả (đã có) + G1 · chú thích ảnh
| | |
|---|---|
| Ảnh | `hinh/giao_dien_ket_qua.png` — giao diện **thật**, bộ 120 học sinh / 10 CLB, seed 42: biểu đồ lấp đầy 10 CLB, phần vàng là em vào bằng suất dự trữ |
| Câu hỏi gợi ý | Ảnh cho thấy người vận hành thấy được gì ngay sau khi bấm chạy? |
| Độ dài | ≤ 40 từ, 3–4 dòng |
| Sự thật trong ảnh | 108/120 em được xếp · 4 CLB đầy (Bóng đá 20/20, Tiếng Anh 16/16, Mỹ thuật 12/12, Tin học 12/12) · 10 trong 12 suất dự trữ dùng tới · 12 em chưa có chỗ — nguồn `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` §2 |

### S1 · S2 · S3 — ba con số (số và dòng nhỏ màu đen đã điền; em viết dòng nghiêng)
| Ô | Số (đã điền) | Nghĩa chính xác — đọc kỹ trước khi viết | Nguồn |
|---|---|---|---|
| S1 | **0** cặp phá vỡ | Không có cặp (một học sinh, một CLB) nào mà học sinh thích CLB đó hơn chỗ hiện tại **và** CLB cũng sẽ nhận em. Đúng ở **mọi seed, mọi bộ dữ liệu mô phỏng** đã chạy. | `CO_CHE_THUAT_TOAN.md` lớp 5; `NGHIEN_CUU_TOI_UU.md` |
| S2 | **0,14 giây** | Thời gian **chạy sắp xếp** cho 2 000 học sinh, 40 CLB (nạp dữ liệu thêm 0,10 s). 1 994/2 000 em được xếp. | `SO_LIEU_DA_KIEM_CHUNG.md` §3 |
| S3 | **816** | Số bài kiểm thử tự động (pytest), gồm 13 tệp chạy giao diện thật trên trình duyệt | `BAN_GIAO.md` §2–3 |

Dòng em viết: ≤ 12 từ, 1 dòng. **Không** viết S1 thành "không ai bị xếp sai" hay
"ai cũng hài lòng" — 0 cặp phá vỡ **không** có nghĩa là thế (xem mục 5).

Muốn đổi số khác vào S1–S3: chọn trong **Ngân hàng số liệu** mục 4, báo AI để
thay (sửa `stats` trong `tao_poster.py`).

### Sơ đồ "Cách hoạt động" (đã có) + G2 · tóm tắt sơ đồ
| | |
|---|---|
| Hình | `hinh/so_do_5_lop.png` — **nhãn "Sơ đồ do AI tạo ra" nằm trong hình, bắt buộc giữ** |
| Câu hỏi gợi ý | Nếu phải giải thích cho một bạn lớp 10 trong 20 giây, em nói gì? Điều gì làm phần mềm khác cách xếp theo thứ tự đăng ký? |
| Độ dài | ≤ 40 từ, 1–2 câu |
| Trong sơ đồ (toàn tiếng Việt) | Hàng trên, theo thứ tự chạy: Đầu vào → ① Xếp ưu tiên ở mỗi CLB (tầng 1 đã thi / tầng 2 không thi) → ② Xét duyệt nhiều vòng (có suất dự trữ xét hai lượt) → ③ Kiểm tra (0 cặp phá vỡ) → Kết quả. Hàng dưới: **Bốc thăm hoạt động thế nào**, gồm 4 thẻ: một em · một số; chỉ dùng khi hoà; kiểm tra lại được; khoá sau khi bốc (số đã bốc giữ nguyên ở các lần chạy sau). Đối chiếu: `CO_CHE_THUAT_TOAN.md` lớp 1–5 |

---

## 2. Lá trái — câu chuyện

### T1 · Vấn đề
| | |
|---|---|
| Câu hỏi gợi ý | Hiện nay học sinh được xếp vào CLB bằng cách nào? Chuyện gì xảy ra với một em đăng ký muộn, hay một em giỏi nhưng xếp CLB đó ở nguyện vọng 2? Vì sao có CLB thi tuyển, có CLB không thi thì cách cũ khó xử lý? |
| Độ dài | ≤ 60 từ, 2–3 câu |
| ⚠️ | **Chưa có khảo sát → không có số hiện trạng.** Viết điều em tự quan sát, dạng định tính. Không viết "đa số", "…% học sinh". Không nhắc tên trường. |
| Bối cảnh có trong repo | Trường có cả CLB thi tuyển lẫn CLB không thi (lý do sinh ra lớp 4 — `CO_CHE_THUAT_TOAN.md`); cách xét thay thế là xét theo thứ tự đăng ký (lớp 1) |

### Ảnh tab Vận hành (đã có) + T2 · Dùng thế nào
| | |
|---|---|
| Ảnh | `hinh/giao_dien_van_hanh.png` — màn hình Vận hành thật |
| Câu hỏi gợi ý | Người vận hành làm những bước nào, theo thứ tự? Mỗi bước một dòng, bắt đầu bằng động từ. |
| Độ dài | 3–5 dòng, mỗi dòng ≤ 10 từ |
| Sự thật về các bước (từ giao diện) | Kéo thả tệp Excel/CSV — phần mềm tự nhận tệp nào là danh sách CLB, chọn CLB thi, nguyện vọng · **Cảnh báo dữ liệu** trước khi chạy (bộ mẫu: 0 cảnh báo) · Nhập điểm theo CLB · Bấm **Chạy sắp xếp** · Xem tab Kết quả · **Xuất CSV** tổng + từng CLB (bộ mẫu: 11 tệp) — `index.html`, `README.md`, `SO_LIEU_DA_KIEM_CHUNG.md` §2 |

### QR + T3 · Xem thử
| | |
|---|---|
| Việc em làm | Quay video demo ngắn (≤ 2 phút) **không lộ tên, không lộ trường**; đăng ẩn danh; tạo QR; báo AI để chèn ảnh QR vào ô |
| Câu hỏi gợi ý | Người xem được làm gì tại gian — xem video, thử bấm trên máy? |
| Độ dài | 1 câu, ≤ 20 từ |
| Gợi ý thêm | Mang máy chạy sẵn `du_lieu_test/app_DEMO_da_cham_diem.db` — đã nạp và chấm điểm, **cố ý dừng trước bước chạy** để người xem tự bấm (`du_lieu_test/tao_db_demo.py`) |

---

## 3. Lá phải — vì sao nên tin

### P1–P4 · Bốn lợi ích
Mỗi ô **một** lợi ích, **≤ 20 từ, tối đa 2 dòng**. Em chọn 4 trong các sự thật dưới
đây và tự viết thành lợi ích **cho người dùng** (học sinh, CLB, người vận hành):

| Sự thật đã kiểm chứng | Số đỡ | Nguồn |
|---|---|---|
| Khai thật nguyện vọng là cách có lợi nhất | 0/1 400 lượt vét cạn khai gian được lợi (Boston: 258) | `NGHIEN_CUU_TOI_UU.md` TN3 |
| Kết quả ổn định | 0 cặp phá vỡ, mọi seed, mọi bộ | `CO_CHE_THUAT_TOAN.md` lớp 5 |
| Bốc thăm chỉ phá hoà, không phụ thuộc thứ tự nhập | Đổi seed: 90,7–100% số em giữ nguyên chỗ | `SO_LIEU_DA_KIEM_CHUNG.md` §3c |
| Em nhập muộn không bị xếp cuối mọi CLB | Em mới được chèn ngẫu nhiên vào dàn số: TB 3,5 suất (cách cũ: 0) | `CO_CHE_THUAT_TOAN.md` lớp 3 |
| Suất dự trữ không bị bỏ trống | Suất dự trữ thừa tự chuyển sang lượt chung | `CO_CHE_THUAT_TOAN.md` lớp 2 |
| Chấm điểm mù | Tab Nhập điểm chỉ hiện mã và tên — không hiện số bốc thăm hay thứ hạng nguyện vọng | giao diện tab 05, `hinh/giao_dien_cham_diem.png` |
| Nhanh | 2 000 học sinh / 40 CLB: 0,14 s | `SO_LIEU_DA_KIEM_CHUNG.md` §3 |
| Không cần mạng, dữ liệu an toàn | Tự sao lưu trước mỗi lần chạy; màn hình phục hồi khi CSDL hỏng | `README.md` mục bền vững dữ liệu |
| Song ngữ | Việt / Anh, đổi bằng một nút | `README.md` |

### Hai biểu đồ (đã có) + P5
| | |
|---|---|
| Biểu đồ 1 | `hinh/bieu_do_khai_gian.png` — khai sai nguyện vọng mà được lợi: RB-DA **0/1 400**, Boston **258/1 400 (18,43%)**; vét cạn, 200 thể hiện |
| Biểu đồ 2 | `hinh/bieu_do_nguyen_vong.png` — 108 em được xếp: NV1 **64 (59%)**, NV2 28 (26%), NV3 10 (9%), NV4 6 (6%) |
| Câu hỏi gợi ý | Với một học sinh, hai biểu đồ này có nghĩa gì khi em điền nguyện vọng? |
| Độ dài | ≤ 40 từ |
| ⚠️ | Biểu đồ 1 là **"không tìm thấy trong phép vét cạn"**, không phải chứng minh cho mọi quy mô. Biểu đồ 2 là một bộ dữ liệu được **cố ý dựng chật** — không phải tỉ lệ sẽ xảy ra ở trường. |

### P6 · Tuyên bố sử dụng AI
| | |
|---|---|
| Nên nêu | (1) Phần mã AI viết — danh sách `BAN_GIAO.md` §3 "AI viết mới" (giao diện song ngữ, màn hình phục hồi, chế độ trình duyệt dự phòng, bộ kiểm thử, bộ dữ liệu mô phỏng…); thuật toán lõi `rbda_priority_pipeline.py` là **học sinh viết**. (2) Có nhật ký câu lệnh AI. (3) Khung poster, sơ đồ, biểu đồ và ảnh chụp giao diện do AI dựng; **chữ trên poster do học sinh viết**. |
| Độ dài | ≤ 40 từ, cỡ 24 pt |
| ⚠️ | Ghi đúng phạm vi, không nới không thu. Ghi thêm việc dựng poster vào nhật ký AI. |

---

## 4. Ngân hàng số liệu — mọi số dùng được, kèm cách trích đúng

Tất cả: **dữ liệu mô phỏng**. Chạy lại được bằng lệnh ở cột cuối.

| Số | Trích đúng | Nguồn · lệnh chạy lại |
|---|---|---|
| 108/120 em được xếp | "bộ mô phỏng 120 học sinh, 10 CLB, 130 chỗ" | `SO_LIEU_DA_KIEM_CHUNG.md` §2 |
| 59% vào NV1 (64/108) | tính trên số em **được xếp**, không phải trên 120 | như trên |
| 7 vòng · 0,011 s | cả 5 bước, gồm sao lưu và xuất tệp | như trên |
| 0 cảnh báo dữ liệu | bộ mẫu TEST_01–03 | như trên |
| 500 em: 0,03 s · 2 000 em: 0,14 s | thời gian **chạy phân bổ**; 204 lần thử tải ở `du_lieu_test/thu_tai/` | §3, `thu_tai/README.md` |
| 0 cặp phá vỡ | mọi seed, mọi bộ | `verify_stability` |
| 0 phản ví dụ / 2 088 thể hiện | "không tìm được phản ví dụ trong 2 088 thể hiện **nhỏ** (7 em / 4 CLB)" — **không** phải chứng minh | `NGHIEN_CUU_TOI_UU.md` TN1 · `python3 du_lieu_test/do_toi_uu_on_dinh.py` |
| 0/1 400 vs 258/1 400 | vét cạn 200 thể hiện | TN3 · `python3 du_lieu_test/do_khai_that.py` |
| 392 phép thử nhiễu, 0 cặp phá vỡ | "bền trước nhiễu" | TN6 · `python3 du_lieu_test/do_ben_vung.py` |
| Nhiễu điểm ±0,5 xáo 15,14% · đổi seed xáo 4,36% | điểm quyết định nhiều hơn bốc thăm | TN6 |
| 90,7% / 96,7% / 100% em không bao giờ đổi chỗ khi đổi seed | 3 bộ: 140 / 120 / 10 em, quét 200 seed | §3c · `du_lieu_test/do_anh_huong_seed.py` |
| Em thêm muộn: TB 3,5 suất (cách cũ 0) | 20 em cũ + 10 em mới tranh 10 suất, 20 seed | `CO_CHE_THUAT_TOAN.md` lớp 3 |
| 10/12 suất dự trữ được dùng | bộ 120 em | §2 |
| 816 test | `python -m pytest -q` | `BAN_GIAO.md` |

---

## 5. Những câu KHÔNG được viết (giám khảo bắt lỗi được ngay)

| Đừng viết | Vì sao | Viết đúng hướng |
|---|---|---|
| "Kết quả tối ưu / tốt nhất cho mọi học sinh" | **Không** tối ưu Pareto: 16 chu trình, 32/140 em có thể cùng lên hạng — nhưng đổi thì 0 → 92 cặp phá vỡ | "tốt nhất **trong các cách xếp ổn định**" |
| "0 cặp phá vỡ nghĩa là không ai muốn đổi" | Cặp phá vỡ = 1 học sinh + 1 CLB. Hai **học sinh** muốn đổi chỗ cho nhau vẫn có thể có | tách rõ hai khái niệm |
| "Bốc thăm dựa trên mã học sinh" | Sai — bốc thăm không phụ thuộc thứ tự nhập | "không phụ thuộc thứ tự nhập liệu" |
| "Khảo sát cho thấy…" | Chưa thu khảo sát | bỏ, hoặc chờ số thật |
| "Đã chứng minh…" | Vét cạn ở quy mô nhỏ ≠ chứng minh | "không tìm thấy phản ví dụ trong …" |
| "AI thiết kế khảo sát / AI làm poster" | Sai phạm vi Phụ lục 1 | theo đúng câu ở P6 |

---

## 6. Soát trước khi in

- [ ] Không còn ô `[ … ]` nào — mọi ô đã có chữ **em viết**
- [ ] Soát chữ "VAS", tên trường, logo, đồng phục, tên người, mã dự án — trên chữ **và trong ảnh**
- [ ] QR mở đúng video, video không lộ tên / trường, **không** dẫn tới GitHub
- [ ] Nhãn "Sơ đồ do AI tạo ra" và "Dữ liệu mô phỏng" còn nguyên
- [ ] Không chữ nào nằm trong vùng gạch chéo của `poster_huong_dan.pdf` (lề 3 cm, 2,5 cm mỗi bên nếp gấp)
- [ ] Chữ nội dung ≥ 28 pt ở tỉ lệ 1:1 (≥ 14 pt trên tệp pptx 1:2)
- [ ] Mỗi con số khớp bảng mục 4
- [ ] Ghi việc dựng poster vào nhật ký AI
- [ ] Tiệm in: **200 × 150 cm**, in từ PDF; nếu in từ pptx 1:2 thì **phóng 200%**; nếp gấp ở 50 cm và 150 cm tính từ mép trái

---

## 7. Hướng nhấn mạnh — chọn một, rồi TỰ viết câu

> Mỗi hướng chỉ là **từ khoá + sự thật làm nền**, không phải câu dùng ngay. Em chọn
> hướng, rồi viết câu bằng lời của em. Cách AI hỗ trợ ở mục này **sát ranh giới
> Phụ lục 1** — nên hỏi giáo viên hướng dẫn trước khi dùng, và ghi vào nhật ký AI:
> *"AI gợi ý hướng nhấn mạnh dạng từ khoá kèm số liệu; học sinh chọn hướng và tự viết câu."*

Cột **Người đọc**: HS = học sinh · CLB = ban chủ nhiệm CLB · VH = người vận hành · GK = giám khảo.

### H2 · Thông điệp chính (chọn đúng **một**)
| Hướng (từ khoá) | Sự thật làm nền | Người đọc | Rủi ro khi viết |
|---|---|---|---|
| **khai thật · không thiệt** | 0/1 400 lượt khai gian được lợi (Boston 258) | HS | không nói "tuyệt đối", "chứng minh" |
| **không ai "chen" được** | 0 cặp phá vỡ, mọi seed | HS, CLB | không nói "ai cũng hài lòng" |
| **nhanh · công bằng · minh bạch** | 0,14 s / 2 000 em; bốc thăm tái lập theo seed | VH | "công bằng" cần một con số đi kèm ở S1–S3 |

### G1 · Chú thích ảnh tab Kết quả
| Hướng | Sự thật | Người đọc |
|---|---|---|
| **nhìn một lần · biết CLB nào đầy** | biểu đồ lấp đầy 10 CLB, 4 CLB đầy | VH |
| **suất dự trữ · thấy rõ** | phần vàng = em vào bằng dự trữ; 10/12 suất dùng tới | CLB |
| **em chưa có chỗ · không bị bỏ sót** | mục "Em chưa có chỗ nào": 12 em, hiện riêng | VH |

### S1 · S2 · S3 · Dòng giải nghĩa
| Ô | Hướng | Rủi ro |
|---|---|---|
| S1 (0) | **không cặp nào muốn phá kết quả** — dịch "cặp phá vỡ" sang lời thường | không nói "không ai muốn đổi" |
| S2 (0,14 s) | **quy mô cả khối / cả trường · không phải chờ** | ghi rõ là "chạy sắp xếp", không gồm nhập liệu |
| S3 (816) | **kiểm tra tự động · mỗi lần sửa** | không nói "không có lỗi" |

### G2 · Tóm tắt sơ đồ
| Hướng | Sự thật | Người đọc |
|---|---|---|
| **nguyện vọng trước · điểm sau · bốc thăm chỉ phá hoà** | thứ tự khoá xếp hạng: điểm → số bốc thăm (lớp 3, 4) | HS |
| **giữ tạm · không chốt sớm** | CLB giữ tạm, em giỏi đến muộn vẫn vào được (lớp 1) | HS, GK |
| **CLB thi và CLB không thi · chung một lần xếp** | hai tầng ưu tiên (lớp 4) — sinh ra từ hoàn cảnh trường | GK |

### T2 · Dùng thế nào (mỗi dòng một bước)
Các bước có thật trên giao diện, theo thứ tự: **kéo thả tệp → xem cảnh báo → nhập
điểm → chạy sắp xếp → xem kết quả → xuất tệp**. Em chọn 3–5 bước, tự đặt động từ.

### T3 · Xem thử
| Hướng | Nền |
|---|---|
| **tự tay bấm · 1 phút** | máy demo đã nạp sẵn, dừng trước bước chạy |
| **xem video** | QR tới video ẩn danh |

### P1–P4 · Lợi ích (chọn 4, mỗi người đọc ít nhất một ô)
| Hướng (từ khoá) | Sự thật | Người đọc |
|---|---|---|
| **khai thật là chiến lược tốt nhất** | 0/1 400 vs 258/1 400 | HS |
| **đến muộn không bị xếp cuối** | em thêm sau: TB 3,5 suất, cách cũ 0 | HS |
| **người chấm không biết thứ hạng** | tab Nhập điểm chỉ hiện mã, tên | HS, CLB |
| **giữ chỗ cho nhóm ưu tiên · không bỏ trống** | dự trữ mềm, suất thừa chuyển sang lượt chung | CLB |
| **một cú bấm · có sao lưu** | sao lưu trước mỗi lần chạy; màn hình phục hồi | VH |
| **không cần mạng · song ngữ** | chạy offline; Việt/Anh | VH |
| **kiểm tra lại được** | cùng dữ liệu + cùng seed → cùng kết quả | GK |

### P5 · Hai biểu đồ nói gì
| Hướng | Nền | Rủi ro |
|---|---|---|
| **so với cách xét "ai chọn trước được trước"** | Boston: 18,43% khai gian được lợi | gọi đúng tên "cơ chế Boston" |
| **đa số vào nguyện vọng 1** | 59% số em được xếp | bộ dữ liệu cố ý dựng chật — ghi "mô phỏng" |

### Không có hướng gợi ý
- **T1 · Vấn đề** — hiện trạng ở trường là điều em quan sát; chưa có khảo sát nên AI không có gì để dựa vào. Dùng câu hỏi gợi ý ở mục 2.
- **P6 · Tuyên bố AI** — theo đúng Phụ lục 1, mục 3.
- **H1, H3** — lấy từ hồ sơ đăng ký.
