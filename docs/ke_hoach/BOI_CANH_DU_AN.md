# Bối cảnh dự án — đọc toàn bộ trước khi sửa mã

Tài liệu này tóm tắt mọi điều đã biết về chương trình và các phân tích đã làm, để một phiên Claude Code mới hiểu đủ bối cảnh. Ngày lập: 07/10/2026. Số liệu lấy từ `ke_hoach_thay_doi.json` và các tài liệu của dự án.

## 1. Chương trình hiện có

**Bài toán.** Một trường phổ thông (~800 học sinh, ~20 CLB) cần phân học sinh vào CLB có giới hạn chỗ. Học sinh xếp hạng nguyện vọng (tối đa 10 mỗi buổi), tick tối đa 5 CLB muốn thi mỗi buổi; CLB chấm điểm các em thi (chấm mù: giám khảo không thấy số bốc thăm hay thứ hạng nguyện vọng).

**Cơ chế (RB-DA).**
- *Deferred Acceptance, học sinh đề nghị*: mỗi vòng, em chưa có chỗ nộp vào nguyện vọng kế tiếp; CLB giữ tạm tốt nhất theo hàm lựa chọn, từ chối phần còn lại. Kết quả ổn định: không có cặp (học sinh, CLB) cùng muốn đổi.
- *Ưu tiên hai tầng* (`compute_club_priority`): Tầng 1 = em có điểm ở CLB đó, sắp −điểm rồi STB; Tầng 2 = em không thi nhưng có xếp nguyện vọng, sắp theo STB. Tầng 1 luôn trên Tầng 2. **Cố ý không nhận thứ hạng nguyện vọng** (chống nội sinh / chống khai gian).
- *Dự trữ mềm hai lượt* (`club_choice_function`): lượt 1 lấy tối đa `reserve_capacity` em mang đúng `reserve_group` của CLB; lượt 2 lấy phần còn lại theo thứ hạng. Suất dự trữ không dùng hết thì thành chỗ thường. `reserve_capacity` nằm TRONG `capacity`.
- *Bốc thăm STB*: mỗi em một số duy nhất, dùng chung mọi CLB; sinh từ `seed` (tái lập bằng crc32, không dùng `hash()`); **khoá** sau lần chạy đầu cùng hạt giống; muốn bốc lại phải qua xác nhận hai bước và để lại dấu vết trong `run_history`. Em thêm vào sau khi khoá được **chèn ngẫu nhiên đều** (`chen_stb_cho_hoc_sinh_moi`), giữ nguyên thứ tự tương đối của em cũ.
- *Nhiều buổi* (`run_rbda_nhieu_buoi`): mỗi nhãn `buoi` chạy `run_rbda` độc lập; mỗi em tối đa một CLB mỗi buổi; ổn định cả tuần = ổn định từng buổi (không có ràng buộc nối hai buổi). Chế độ bốc thăm đang dùng: `stb_ngay` (hoán vị lại mỗi buổi). `stb_tuan` và `stb_co_bu` chỉ giữ để đo: `stb_co_bu` mở kênh khai gian (TN7d: 113/300 em tìm được cách).
- *Kiểm chứng* (`verify_stability`): với mỗi cặp (em, CLB em ưa hơn CLB hiện tại), thêm em vào tập đang giữ rồi chạy lại hàm lựa chọn động; được nhận = cặp phá vỡ. Pipeline (`api.py`) **rollback cả lần chạy** nếu có bất kỳ cặp phá vỡ hay vi phạm sanity nào.

**Pipeline** (`PipelineAPI._run_pipeline_da_khoa`, một giao dịch): sao lưu (SQLite Backup API) → kiểm dữ liệu → chọn buổi chạy (`chi_buoi`) → khoá seed/STB, bổ sung STB cho em mới → `run_rbda_nhieu_buoi` → sanity + verify từng buổi (lỗi thì rollback) → chụp `ket_qua_truoc`, ghi `match_results`, `run_meta`, `run_history` (không bao giờ ghi đè), dấu vân tay SHA-256 của dữ liệu đầu vào → xuất CSV.

**Dữ liệu.** `app.db`: `students(student_id, name, stb_number, reserve_group)`, `clubs(club_id, name, capacity>0, reserve_capacity 0..capacity, reserve_group, buoi)`, `club_test_selection`, `club_scores(score REAL ≥ 0)`, `preferences(rank ≥ 1)`, `match_results(PK student_id, buoi)`, `run_meta`, `run_history`, `stb_lock`, `ket_qua_truoc`, `dau_van_tay_chay`. Nhập CSV/Excel theo hợp đồng cột cố định (`club_id, name, capacity, reserve_capacity, reserve_group, buoi`; `student_id, test_club_k, score_k`; `pref_k` hoặc `<buoi>_pref_k`).

**Chất lượng đã có.** ~483 ca test, 25 lỗi đã tìm và sửa (10 lỗi "im lặng" — báo thành công trong khi dữ liệu sai), nhiều kiểm tra dữ liệu khi nhập (Excel cắt số 0 đầu, trùng hoa/thường, trùng dòng, điểm bất thường so với trung vị). Theo tài liệu dự án, đến 02/09 cửa sổ gốc pywebview chưa được xác nhận dùng được trên Windows thật; chế độ trình duyệt dự phòng đã chạy trọn luồng.

## 2. Mục tiêu của chủ dự án
1. Bán chương trình ra ngoài CLB trường học. Đã khảo sát tài chính, kỹ thuật và các lĩnh vực cần "hệ thống sắp xếp tốt". Mô hình kinh doanh để sau; trước hết muốn biết **điểm yếu** để cải thiện.
2. Cải tiến thuật toán để xử lý **thay đổi theo thời gian thực** (em đến muộn, huỷ, sức chứa đổi) nhằm mở thêm thị trường.
3. Biết **chính xác chỗ nào trong mã phải sửa, và sửa thế nào tuỳ từng ngành**.

## 3. Các phân tích đã làm (theo thứ tự)
1. **Bản đồ tài liệu**: 1.170 bài (2019–2026) về ghép cặp ổn định và ứng dụng. Không có bài nào nghiên cứu riêng phân bổ CLB trường học. Lưu ý: một số tên tác giả/tiêu đề trong danh sách sai; kiểm qua Crossref/arXiv trước khi trích dẫn.
2. **Đánh giá dùng lại**: chấm 7 tiêu chí phù hợp + mức thiếu hụt. Cao nhất: hoạt động ngoại khoá/trại/tình nguyện/thực tập, tuyển sinh cấp trường, phân đề tài; thấp nhất: ghép thận, điều xe thời gian thực, hẹn hò. Điểm là phán đoán, không phải số đo.
3. **Không nên bán vào**: tuyển sinh đại học toàn quốc (hệ thống "lọc ảo" của Bộ đã làm); giao dịch/phát hành/cho vay tài chính (phân bổ bằng giá và rủi ro); điều xe/giao hàng tức thời (cần họ thuật toán trực tuyến khác). Trong tài chính chỉ hợp phân bổ nội bộ.
4. **Báo cáo thay đổi theo ngành (bản 1)**: 12 ngành × 8 thành phần, thang 0–3, lập khi chưa thấy mã.
5. **Thiết kế thời gian thực** (chỉ báo cáo thiết kế): nâng cấp 0 chạy lại theo cửa sổ · 1 tăng dần (đến muộn, giảm sức chứa) · 2 huỷ, tăng sức chứa · 3 bảo vệ người đã công bố · 4 gom lô nhỏ · 5 đổi nguyện vọng · 6 dòng liên tục (họ khác).
6. **Đọc mã từ bản build** `PhanBoCauLacBo.exe` (gói `uu.zip` không có `.py`, `tests/`, `docs/`): đọc 12 mô-đun qua bytecode Python 3.11; số dòng từ bảng dòng bytecode; comment mất, docstring còn. Kết quả là **sổ đăng ký 33 mục** (`SO_DANG_KY_33_MUC.md`, `ke_hoach_thay_doi.json`) — bản này **thay thế** bản 1 ở mức mã.

## 4. Phát hiện chính khi đọc mã
- Lõi DA (`run_rbda`, `club_choice_function`) dùng lại được cho mọi ngành; thứ phải đổi là xung quanh: hàm ưu tiên, luật hoà điểm, luật đủ tư cách, schema, nhập/xuất, cách xử lý khi mất ổn định.
- "Bốc thăm giữ nguyên" chỉ đúng với ngành chấp nhận bốc thăm: STB nằm ngay trong khoá ưu tiên, nên tuyển sinh công lập, nhân sự, tài chính cần đổi luật hoà điểm (A2).
- `verify_stability` đã dùng hàm lựa chọn động nên tổng quát được; chỉ cần cho phép cắm hàm (Z7), không phải viết lại.
- Sức chứa kiểu ba lô (khối lượng hồ sơ, tải trọng/thể tích) làm hàm lựa chọn không còn thay thế được → DA mất bảo đảm ổn định; mà pipeline lại rollback khi có cặp phá vỡ (A12).
- Hằng 10 nguyện vọng / 5 CLB thi khai báo hai lần (Python L91, L96 và `js/05_quan_ly.js` L33–34); con số 10 đến từ giới hạn câu xếp hạng của Microsoft Forms, không phải từ thuật toán.
- Thuật ngữ gắn cứng: 144/191 chuỗi SQL nhắc `clubs`/`students`; giao diện có 252 chữ "CLB", 231 chữ "học sinh".

## 5. Số đo (hàm thật nạp từ .exe, dữ liệu TỰ SINH, 20 CLB)
**Kiểm chứng ổn định chiếm phần lớn thời gian** (mục Z4):

| Số học sinh | run_rbda (s) | verify_stability gốc (s) | verify đề xuất (s) |
|---|---|---|---|
| 2000 | 0,16 | 0,26 | 0,007 |
| 5000 | 0,46 | 3,21 | 0,072 |
| 10000 | 1,08 | 22,38 | 0,091 |
| 20000 | 3,06 | — | 0,292 |

Ở 2.000–5.000 học sinh hai lần đo cùng cấu hình chênh tới 3 lần (máy bận); đọc tỉ lệ ở 10.000 (≈20×). Bản đề xuất (`tham_khao/de_xuat_verify_nhanh.py`, tra bisect trên thứ hạng sắp sẵn) cho **cùng danh sách cặp phá vỡ** với bản gốc trên 7 cấu hình (3 kết quả thật: 0 cặp; 4 kết quả hoán đổi, CLB đều đầy, có dự trữ: 23.110 cặp). Chỉ đúng với cấu trúc hai lượt hiện tại. Con số 7,65 s ở 5.000 học sinh trong báo cáo gốc có lẽ phần lớn là verify — **chưa xác nhận** trên dữ liệu thật.

**Số vòng** (mục Z5; từ 204 lần thử tải của dự án, `ket_qua_thu_tai.csv`): docstring nói số vòng = độ dài danh sách dài nhất; thực tế:

| Danh sách | Trung vị | Lớn nhất |
|---|---|---|
| 3 mục | 9 | 37 |
| 5 mục | 14 | 84 |
| 10 mục | 18 | 227 |

Trần `max_rounds = 1000` chỉ gấp ≈4,4 lần mức cao nhất đã thấy; chạm trần thì L429 ném `RuntimeError`. Cận chứng minh được: tổng độ dài các danh sách nguyện vọng.

**Em đến muộn làm đổi kết quả em cũ** (mục G1–G3; 2.000 học sinh):

| Tỉ lệ chỗ | Em đến muộn | Em cũ bị đổi (TB) | …mất hẳn chỗ | …tốt lên |
|---|---|---|---|---|
| 1 | 1 | 1,72 | 0,62 | 0 |
| 1 | 5 | 9,03 | 2,07 | 0 |
| 1 | 20 | 40,7 | 9,55 | 0 |
| 0,8 | 1 | 1,7 | 0,8 | 0 |
| 0,8 | 5 | 8,17 | 4 | 0 |
| 0,8 | 20 | 32,4 | 16,25 | 0 |

**Tiếp tục DA từ trạng thái cũ** (trạng thái khôi phục từ `MatchResult.assignment` + `rank_in_student_pref`; chỉ tính lại thứ hạng của CLB em mới đăng ký):

| Cấu hình (HS/CLB/tỉ lệ chỗ/em mới) | Giống hệt chạy lại | Chạy lại (ms) | Tiếp tục (ms) |
|---|---|---|---|
| 2000/20/1.0/1 em | 15/15 | 43,9 | 11,18 |
| 2000/20/0.8/5 em | 10/10 | 110,6 | 52,61 |
| 5000/20/1.0/1 em | 8/8 | 933 | 243,43 |
| 5000/20/0.9/20 em | 5/5 | 778,1 | 425,6 |

Chỉ nhanh hơn 1,8–3,9× vì vẫn sắp lại cả danh sách của CLB; muốn mức mili-giây phải giữ danh sách xếp hạng có chỉ mục và chèn bằng bisect.

**Từ tài liệu kiểm chứng của dự án** (`SO_LIEU_DA_KIEM_CHUNG.md`, cũng là dữ liệu mô phỏng): RB-DA tối ưu trong các kết quả ổn định (0 phản ví dụ / 2.088 thể hiện vét cạn) và chống khai gian (0/1.400), nhưng **không tối ưu Pareto** (bộ `bo_sach` 140 em: 85 cặp đổi chỗ cùng có lợi, 34 em = 24,3%). Tập em có suất **bất biến** giữa mọi kết quả ổn định (240/240), nên đổi cơ chế ổn định không cứu thêm ai. Boston cho nhiều NV1 hơn (92 so với 54) nhưng 50 cặp phá vỡ và 18,43% em khai gian được; TTC 118 cặp phá vỡ.

## 6. Lý thuyết phải giữ khi mở rộng
- DA giữ ổn định và chống khai gian khi hàm lựa chọn **thay thế được** (substitutable) và thoả **luật tổng cầu** (law of aggregate demand). Dự trữ mềm hai lượt với cùng một thứ hạng nền thoả điều này; mọi hàm mới phải kiểm bằng test.
- Sức chứa có trọng số (ba lô), nhu cầu nhiều môn trùng giờ, cặp đôi, mức tối thiểu: có thể **không có** kết quả ổn định hoặc bài toán khó tính → phải báo rõ, đo cặp phá vỡ như chỉ số.
- Giới hạn độ dài danh sách (10) làm DA không còn chống khai gian trọn vẹn (Dur & Morrill 2020) → nới trần là có lợi.
- Thêm một người đề nghị chỉ có thể làm các người đề nghị khác **xấu đi hoặc giữ nguyên** → chạy lại sau khi có em đến muộn có thể hạ chỗ người đã công bố; cần mục G3 (bảo vệ người đã công bố bằng dự trữ mềm + ngân sách cặp phá vỡ), chú ý rủi ro giữ chỗ ảo; giữ nguyên số bốc thăm khi nộp lại để không "bốc lại" được.
- Sự kiện thêm ràng buộc (đến muộn, giảm sức chứa) tiếp tục DA được từ trạng thái lưu; sự kiện bớt ràng buộc (huỷ, tăng sức chứa) cần phát lại từ điểm lưu trước sự kiện hoặc chuỗi chỗ trống (chưa chứng minh tương đương).

## 7. Pháp lý và bối cảnh Việt Nam (để nhắc, không phải tư vấn pháp lý)
- Luật Bảo vệ dữ liệu cá nhân **91/2025/QH15** hiệu lực từ 01/01/2026, hướng dẫn bởi Nghị định 356/2025/NĐ-CP. Liên quan: đồng ý của cha mẹ khi người đăng ký là trẻ em, thời hạn lưu, xoá khi nghỉ việc, dữ liệu nhạy cảm (sức khoẻ, hoàn cảnh, tài chính). Cần chuyên gia pháp lý kiểm điều khoản cụ thể.
- Tuyển sinh đại học toàn quốc đã có hệ thống lọc ảo của Bộ (không phải thị trường).

## 8. 12 ngành và điều khác biệt
### DT — Phân bổ đề tài, đồ án, người hướng dẫn
- 3 mục R riêng · điểm công sức 10 (kể cả tiền đề: 10) · kế hoạch 7 mục
- Ít việc riêng nhất: ưu tiên hai tầng hiện có (đã phỏng vấn / chưa) khớp sẵn. Việc chính là SPA, tức hàm lựa chọn hai tầng đề tài–giảng viên (A3, A7) và bảng giảng viên (B2). Không cần thời gian thực.

### KTX — Ký túc xá, nhà ở sinh viên, nhà ở xã hội
- 8 mục R riêng · điểm công sức 20 (kể cả tiền đề: 26) · kế hoạch 15 mục · tiền đề ngoài R: Z4, A3, G1
- Dự trữ mềm dùng được cho chỗ hoàn cảnh khó khăn. Việc riêng: ưu tiên theo khoảng cách và điểm hoàn cảnh (A1, B1), bộ lọc giới tính / loại phòng (A5), bảo vệ người đang ở (G3, kéo theo G1 và A3), giải trình (C3), dữ liệu nhạy cảm (E3). Không ghép bạn cùng phòng bằng DA.

### SK — Sự kiện, hội nghị (workshop, phản biện, gặp doanh nghiệp)
- 9 mục R riêng · điểm công sức 22,5 (kể cả tiền đề: 32,5) · kế hoạch 17 mục · tiền đề ngoài R: Z4, A3, A5, G3
- Workshop theo khung giờ chạy được như 'buổi'. Việc riêng: ghép phản biện nhiều–nhiều (A7), cặp cấm phản biện–tác giả (A10), lịch chồng lấn và xuất .ics (A9, C2), nhập từ hệ thống bán vé (C1).

### NT — Hoạt động ngoài trường, trại hè, khoá ngắn, tình nguyện
- 9 mục R riêng · điểm công sức 23,5 (kể cả tiền đề: 23,5) · kế hoạch 13 mục · tiền đề ngoài R: Z4
- Gần chương trình hiện tại nhất (khoá, đợt ≈ CLB). Việc riêng chủ yếu: mức tối thiểu và trần cứng (A6, A4), đợt có ngày (A9), thay đổi theo thời gian (G1–G3), dữ liệu trẻ em cần đồng ý của cha mẹ (E3).

### YT — Y tế (học viên thực hành, luân khoa, nội trú)
- 8 mục R riêng · điểm công sức 26 (kể cả tiền đề: 28) · kế hoạch 14 mục · tiền đề ngoài R: Z4, G1
- Khó nhất là cặp đôi (A11, XL): có thể không tồn tại kết quả ổn định. Ngoài ra: mức tối thiểu cho tuyến dưới (A6), trần vùng qua hàm lựa chọn (A3), chứng chỉ hành nghề (A5), nhật ký kiểm toán (E2). Chỉ dữ liệu nhân sự, không đưa dữ liệu bệnh nhân vào.

### VL — Nền tảng việc làm tự do, crowdsourcing
- 8 mục R riêng · điểm công sức 28 (kể cả tiền đề: 38) · kế hoạch 18 mục · tiền đề ngoài R: A3, G1, G3
- Quy mô nền tảng (Z4, Z5, E1); không có người xếp hạng (A1, B3); nhập qua API (C1); gom lô liên tục (G4). Nặng nhất là máy chủ nhiều người dùng (E1, XL).

### KT — Kỹ thuật – sản xuất (kỹ sư vào dự án, tác vụ vào máy)
- 10 mục R riêng · điểm công sức 29 (kể cả tiền đề: 33) · kế hoạch 17 mục · tiền đề ngoài R: Z4, G3
- Máy và tác vụ không có người xếp hạng: cần sinh sở thích từ dữ liệu (B3), điểm có thể âm (B1); dự án chia ô theo vai trò (A3, A7); chứng chỉ là bộ lọc (A5).

### HP — Phân bổ học phần, môn tự chọn
- 10 mục R riêng · điểm công sức 29,5 (kể cả tiền đề: 37,5) · kế hoạch 17 mục · tiền đề ngoài R: Z4, A3, G3
- Cách dễ (chạy riêng từng khung giờ như 'buổi') dùng được ngay; cách đúng (tín chỉ tối thiểu/tối đa, môn tiên quyết, k môn không trùng giờ) là A8 — mục XL — cộng lịch học, phòng (A9, B2) và nhập từ phần mềm đào tạo (C1).

### TS — Tuyển sinh cấp trường (lớp 6, lớp 10, trường tư, chọn ngành)
- 13 mục R riêng · điểm công sức 37 (kể cả tiền đề: 39) · kế hoạch 21 mục · tiền đề ngoài R: G1
- Nhiều việc vì ba lý do: luật ưu tiên và hoà điểm (A1, A2, A4: điểm tổ hợp, nhận hết ở ngưỡng, thứ tự dự trữ); quy mô 10⁴–10⁵ thí sinh nên Z4, Z5 bắt buộc và phải bỏ trần 10 (Z2); giải trình, kiểm toán, phúc khảo (C3, E2). Tuyển sinh đại học toàn quốc nằm ngoài phạm vi.

### NS — Nhân sự nội bộ (tân tuyển, thực tập, luân chuyển, giáo viên)
- 13 mục R riêng · điểm công sức 37 (kể cả tiền đề: 43) · kế hoạch 20 mục · tiền đề ngoài R: Z4, A3, G1
- Bốc thăm thường không được chấp nhận (A2); ưu tiên theo đánh giá và thâm niên (A1); quyền người đang giữ vị trí (A4, A5, G3); phê duyệt, nhật ký, phân quyền (E1, E2); xoá dữ liệu khi nghỉ việc (E3).

### LG — Logistics – vận tải (đơn hàng cho xe, tài xế cho tuyến)
- 12 mục R riêng · điểm công sức 44 (kể cả tiền đề: 50) · kế hoạch 21 mục · tiền đề ngoài R: G1, G3
- Hàm lựa chọn kiểu ba lô (tải trọng, thể tích) làm mất bảo đảm ổn định (A3, A12); sở thích từ khoảng cách và chi phí (A1, B3); khung giờ giao (A9); lô ngắn (G4). Điều phối tức thời (G5) nằm ngoài phạm vi.

### TC — Tài chính – ngân hàng (chia khách hàng, hồ sơ thẩm định)
- 17 mục R riêng · điểm công sức 50,5 (kể cả tiền đề: 52,5) · kế hoạch 23 mục · tiền đề ngoài R: Z4, A5
- Nhiều việc nhất, phần lớn không thuộc thuật toán: sức chứa theo khối lượng hồ sơ kiểu ba lô (A3, A12); cặp cấm xung đột lợi ích (A10); hoà điểm xác định (A2); triển khai tại chỗ, phân quyền, mã hoá (E1); phê duyệt hai người (E2); dữ liệu tài chính (E3). Chỉ nhắm phân bổ nội bộ, không phải giao dịch.

## 9. Câu hỏi còn mở — kiểm khi có kho mã
1. Số dòng và hiện trạng trong sổ đăng ký có còn đúng với nhánh hiện tại không? (sổ lập từ bản build)
2. Con số 7,65 s ở 5.000 học sinh chia cho từng bước bao nhiêu? (đo thời gian riêng `run_rbda`, sanity, verify)
3. Báo cáo gốc nói kết quả của em cũ "tuyệt đối không đổi" khi chèn em muộn — chỉ đúng với số bốc thăm; kết quả phân bổ có đổi (mục 5).
4. Báo cáo gốc ghi 7,65 s ở 5.000 HS × 10 CLB nhưng test 0 cặp phá vỡ ở 5.000 × 100 CLB — cần thống nhất.
5. Đối chiếu `verify_stability` với thư viện Python `matching` (Wilde và cộng sự, 2020) — dự định trước đây, chưa làm.
6. Quan hệ phụ thuộc giữa các mục (`phu_thuoc`) là phán đoán kỹ thuật; sửa nếu đọc kho thấy khác.
7. Ngành nào làm trước là quyết định của chủ dự án (đề xuất kỹ thuật: thử kiến trúc bằng một trong các ngành nhẹ — đề tài, ngoài trường, ký túc xá, sự kiện).

## 10. Thuật ngữ
| Từ | Nghĩa |
|---|---|
| DA / RB-DA | Deferred Acceptance / Reserve-Based DA (DA có dự trữ) |
| STB | single tie-breaking: một số bốc thăm mỗi em, dùng chung mọi CLB |
| buổi | nhãn khung sinh hoạt; hai CLB cùng `buoi` = trùng giờ |
| Tầng 1 / Tầng 2 | em có điểm thi ở CLB đó / em không thi nhưng xếp nguyện vọng |
| dự trữ mềm | suất ưu tiên cho một nhóm, thừa thì thành chỗ thường |
| cặp phá vỡ (blocking pair) | (em, CLB) mà em thích CLB hơn chỗ hiện tại và CLB sẵn sàng nhận em |
| trùng khít | cùng dữ liệu, cùng seed → `match_results` giống từng dòng |
| R / O / – | cần làm / tuỳ chọn / không cần (cho một ngành) |
| tiền đề | mục ngành không đánh dấu R nhưng một mục R của ngành phụ thuộc vào |
| S / M / L / XL | một hàm / vài hàm một tệp / nhiều tệp, nhiều lớp / thuật toán mới hoặc bài toán mở |
