# Sổ đăng ký 33 mục sửa mã nguồn

Nguồn duy nhất: `ke_hoach_thay_doi.json` (tệp này sinh từ đó). Số dòng lấy từ bản build — định vị theo **tên hàm**.
Ký hiệu áp dụng: **R** cần làm · **O** tuỳ chọn · **–** không cần. Quy mô: S/M/L/XL (xem CLAUDE.md).

## Bảng tóm tắt

| Mã | Việc | Mức · quy mô | Phụ thuộc | DT | KTX | SK | NT | YT | VL | KT | HP | TS | NS | LG | TC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | Tách thuật ngữ CLB / học sinh khỏi mã (gói từ vựng theo ngành) | Sửa mã · M (giao diện) – L (nếu đổi tên SQL) | Z6 | R | R | R | O | R | R | R | R | R | R | R | R |
| Z2 | Một nguồn cho giới hạn nhập (10 nguyện vọng, 5 CLB thi mỗi buổi) | Cấu hình → Sửa mã · S | Z6 | – | – | O | – | O | R | R | O | R | – | R | O |
| Z3 | Tách _run_pipeline_da_khoa (573 dòng) thành các bước có điểm móc | Sửa mã · L | Z6 | R | R | R | R | R | R | R | R | R | R | R | R |
| Z4 | Kiểm chứng ổn định nhanh (verify_stability) | Sửa mã · S | Z6 | O | O | O | O | O | R | O | O | R | O | R | O |
| Z5 | Trần vòng lặp và tài liệu về số vòng | Sửa mã · S | Z6 | O | O | O | O | O | R | O | O | R | O | R | O |
| Z6 | Bộ test và dữ liệu mô phỏng cho từng hàm mới | Viết mới · M mỗi ngành | — | R | R | R | R | R | R | R | R | R | R | R | R |
| Z7 | Cổng cắm cho hàm ưu tiên, hàm lựa chọn, luật đủ tư cách | Sửa mã · M | Z6, Z3 | R | R | R | R | R | R | R | R | R | R | R | R |
| A1 | Hàm ưu tiên theo ngành (thay compute_club_priority) | Sửa mã · M | Z7 | O | R | R | O | O | R | R | O | R | R | R | R |
| A2 | Luật hoà điểm: bốc thăm hay tiêu chí khác | Sửa mã · S–M | A1 | – | – | – | – | O | – | – | – | R | R | – | R |
| A3 | Hàm lựa chọn theo ngành (thay / bổ sung club_choice_function) | Viết mới · L (XL với ba lô) | Z7 | R | O | O | R | R | O | R | O | R | O | R | R |
| A4 | Dự trữ cứng / mềm và thứ tự xử lý dự trữ | Sửa mã · S–M | A3 | – | O | O | R | O | O | – | O | R | R | – | – |
| A5 | Điều kiện đủ tư cách đa thuộc tính và bộ lọc cứng | Sửa mã · M | Z7, B2 | O | R | O | O | R | O | R | R | R | R | O | O |
| A6 | Mức tối thiểu và vòng đóng–mở lại | Sửa mã · M | Z3, A3 | – | – | O | R | R | – | O | R | – | – | – | – |
| A7 | Sức chứa hai tầng và ghép nhiều–nhiều | Viết mới · L | A3 | R | – | R | – | O | O | R | – | O | – | O | O |
| A8 | Nhu cầu nhiều đơn vị và ràng buộc xuyên buổi | Viết mới · XL | A3, Z3 | – | – | O | O | O | – | – | R | – | O | – | – |
| A9 | Lịch tổng quát thay cho nhãn buổi | Sửa mã · M | B2 | – | – | R | R | O | – | O | R | – | O | R | – |
| A10 | Cặp cấm / xung đột lợi ích | Sửa mã · M | Z3, A5 | O | – | R | – | O | – | – | – | – | O | – | R |
| A11 | Đăng ký theo nhóm / cặp đôi | Viết mới · XL | A3 | – | O | – | O | R | – | – | – | – | – | – | – |
| A12 | Ổn định là chỉ số chất lượng, không phải điều kiện chặn | Sửa mã · M | Z3 | – | – | – | O | O | – | O | O | – | – | R | R |
| B1 | Điểm và thuộc tính theo cặp (đang là một số thực ≥ 0) | Sửa mã · M | Z6 | – | R | – | – | O | R | R | – | R | R | R | R |
| B2 | Bảng thực thể mới theo ngành | Viết mới · M mỗi ngành | Z6 | R | R | R | R | R | R | R | R | R | R | R | R |
| B3 | Sinh danh sách sở thích từ dữ liệu | Viết mới · L | B1, Z3 | – | O | – | – | – | R | R | – | – | O | R | R |
| C1 | Nhập dữ liệu: ánh xạ cột và kết nối hệ thống nguồn | Sửa mã · L | B2 | O | O | R | O | O | R | R | R | R | R | R | R |
| C2 | Xuất lịch và thông báo (.ics, thư) | Viết mới · S–M | A9 | – | – | R | O | – | – | O | R | O | – | O | – |
| C3 | Giải trình từng cá nhân (vì sao không trúng / không có chỗ) | Viết mới · M | Z7 | O | R | – | – | O | O | – | O | R | R | – | R |
| E1 | Máy chủ nhiều người dùng, phân quyền, mã hoá | Viết mới · XL | Z3 | – | O | O | – | O | R | O | O | R | R | R | R |
| E2 | Nhật ký kiểm toán và phê duyệt hai người | Sửa mã · M | Z3 | – | O | – | – | R | O | – | – | R | R | – | R |
| E3 | Dữ liệu cá nhân: đồng ý, thời hạn lưu, xoá | Sửa mã · M–L | B2 | O | R | O | R | R | R | O | O | R | R | R | R |
| G1 | Đến muộn / sức chứa giảm: tiếp tục DA từ trạng thái cũ (nâng cấp 1) | Sửa mã · M | Z3, Z4 | – | O | R | R | O | O | R | R | O | O | O | R |
| G2 | Huỷ / sức chứa tăng: rút lui (nâng cấp 2) | Sửa mã · M–L | G1 | – | R | O | R | R | O | O | R | R | R | O | R |
| G3 | Bảo vệ người đã công bố (nâng cấp 3) | Viết mới · L | G1, A3 | – | R | O | R | O | – | O | O | O | R | – | R |
| G4 | Gom lô nhỏ theo cửa sổ thời gian (nâng cấp 4) | Viết mới · M–L | G1, G3 | – | – | R | O | – | R | R | R | – | – | R | R |
| G5 | Đổi nguyện vọng và dòng liên tục (nâng cấp 5–6) | Viết mới · XL | — | – | – | – | – | – | O | – | – | – | – | R | – |

## Nhóm Z — Lõi chung — mọi ngành đều cần, làm trước

### Z1 — Tách thuật ngữ CLB / học sinh khỏi mã (gói từ vựng theo ngành)
- **Mức / quy mô:** Sửa mã / M (giao diện) – L (nếu đổi tên SQL)
- **Tệp:** i18n.js, i18n_errors.py → i18n_loi.js, index.html, api*.py, rbda_priority_pipeline.py
- **Dòng:** schema L1251–1290; giao diện: toàn bộ
- **Hàm:** UI_STRINGS, MESSAGES, DEFAULT_SCHEMA
- **Hiện trạng:** Thuật ngữ gắn cứng ở mọi tầng: 144/191 chuỗi SQL nhắc bảng clubs/students; 76/464 hàm có club/student/hoc_sinh trong tên; giao diện có 252 chữ 'CLB' và 231 chữ 'học sinh'; 84/340 thông báo lỗi nhắc CLB hoặc học sinh. Giao diện đã song ngữ vi/en qua một bảng (I18N.t) và thông báo lỗi chỉ có MỘT nguồn (i18n_errors.py → tao_i18n_js.py).
- **Thay đổi:** Lớp giao diện, thông báo, tệp xuất: thêm 'gói từ vựng' (tên đơn vị, tên ứng viên, tên buổi) nạp theo cấu hình — rẻ vì cơ chế I18N đã có. Lớp SQL và tên hàm: giữ club_id / student_id làm tên nội bộ; chỉ đổi khi bán ra ngoài và sau khi có bộ test hồi quy.
- **Rủi ro:** Thấp với giao diện. Đổi tên cột CSV (club_id, student_id) là đổi 'hợp đồng' mà người dùng đã quen.
- **Kiểm nhận:** Chạy lại bộ test hiện có; so từng tệp xuất trước/sau trên 3 bộ dữ liệu.
- **Phụ thuộc:** Z6
- **Ngành cần (R):** DT, KTX, SK, YT, VL, KT, HP, TS, NS, LG, TC · **tuỳ chọn (O):** NT
- **Khác nhau theo ngành:**
  - DT (Đề tài): Đơn vị = đề tài (+ giảng viên); ứng viên = sinh viên.
  - KTX (Ký túc xá): Đơn vị = phòng / toà; ứng viên = người ở.
  - SK (Sự kiện): Đơn vị = phiên / workshop.
  - NT (Ngoài trường): Gần như không đổi: 'khoá / đợt' ≈ 'CLB'.
  - YT (Y tế): Đơn vị = bệnh viện / khoa; ứng viên = bác sĩ / học viên.
  - VL (Việc làm tự do): Đơn vị = việc; ứng viên = người làm.
  - KT (Kỹ thuật): Đơn vị = dự án / máy; ứng viên = kỹ sư / tác vụ.
  - HP (Học phần): Đơn vị = học phần / lớp.
  - TS (Tuyển sinh): Đơn vị = ngành / trường; ứng viên = thí sinh.
  - NS (Nhân sự): Đơn vị = vị trí / phòng ban.
  - LG (Logistics): Đơn vị = xe / tuyến; ứng viên = đơn hàng.
  - TC (Tài chính): Đơn vị = chuyên viên; ứng viên = khách hàng / hồ sơ.

### Z2 — Một nguồn cho giới hạn nhập (10 nguyện vọng, 5 CLB thi mỗi buổi)
- **Mức / quy mô:** Cấu hình → Sửa mã / S
- **Tệp:** rbda_priority_pipeline.py; js/05_quan_ly.js; js/04_nhap_tai_cho.js; api_quan_ly.py
- **Dòng:** rbda L91, L96; 05_quan_ly.js L33–34; 04_nhap_tai_cho.js L397–445; api_quan_ly L430–476
- **Hàm:** TRAN_NGUYEN_VONG_MOI_BUOI, TRAN_CLB_THI_MOI_BUOI
- **Hiện trạng:** Hai hằng (10 và 5) được khai báo hai lần: một ở Python, một bản sao ở JS rồi dùng trong form nhập tại chỗ. Con số 10 đến từ giới hạn câu hỏi xếp hạng của Microsoft Forms (chú thích trong submit_preferences), không phải từ thuật toán.
- **Thay đổi:** Đưa vào một tệp cấu hình theo triển khai; backend gửi giá trị cho giao diện lúc khởi động để hai bên không lệch. Kiểm lại thời gian chạy với danh sách dài.
- **Rủi ro:** Thấp. Lý thuyết: DA chỉ chống khai gian trọn vẹn khi danh sách không bị cắt ngắn, nên nới trần là có lợi.
- **Kiểm nhận:** Test: đổi cấu hình thì Python và giao diện cùng đổi; chạy lại thử tải với danh sách dài.
- **Phụ thuộc:** Z6
- **Ngành cần (R):** VL, KT, TS, LG · **tuỳ chọn (O):** SK, YT, HP, TC
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Nhiều phiên → danh sách dài.
  - YT (Y tế): Xếp hạng đầy đủ các bệnh viện.
  - VL (Việc làm tự do): Như KT.
  - KT (Kỹ thuật): Sở thích sinh từ dữ liệu nên danh sách dài (hàng chục–trăm).
  - HP (Học phần): Số lựa chọn mỗi khung giờ.
  - TS (Tuyển sinh): Bỏ trần 10 thành tham số; quy mô 10⁴–10⁵ thí sinh.
  - LG (Logistics): Như KT.
  - TC (Tài chính): Danh sách ứng viên dài.

### Z3 — Tách _run_pipeline_da_khoa (573 dòng) thành các bước có điểm móc
- **Mức / quy mô:** Sửa mã / L
- **Tệp:** api.py
- **Dòng:** L744–1316
- **Hàm:** PipelineAPI._run_pipeline_da_khoa
- **Hiện trạng:** Một phương thức làm tất cả: sao lưu (L824) → kiểm dữ liệu (L840–847) → chọn buổi chạy (L858–871) → khoá seed và STB (L903–1027) → gọi run_rbda_nhieu_buoi (L1046) → sanity + verify_stability từng buổi, có vấn đề thì rollback (L1052–1071) → ảnh chụp ket_qua_truoc, match_results, run_history (L1086–1248) → xuất CSV (L1256–1263). Tất cả trong một giao dịch.
- **Thay đổi:** Tách thành danh sách bước (validate → prepare → solve → check → persist → export), mỗi bước nhận và trả một đối tượng ngữ cảnh; thêm điểm móc trước và sau 'solve' để từng ngành chèn bước riêng (loại cặp cấm, vòng mức tối thiểu, sinh sở thích, phê duyệt).
- **Rủi ro:** Đây là hàm quan trọng nhất của phần mềm (docstring _ket_noi_ghi dặn 'để nguyên'). Phải giữ thứ tự khoá và rollback.
- **Kiểm nhận:** Test trùng khít (3 bộ × 20 seed) và test rollback.
- **Phụ thuộc:** Z6
- **Ngành cần (R):** DT, KTX, SK, NT, YT, VL, KT, HP, TS, NS, LG, TC · **tuỳ chọn (O):** —
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Chèn bước loại cặp cấm.
  - NT (Ngoài trường): Chèn vòng đóng khoá dưới mức tối thiểu.
  - YT (Y tế): Chèn kiểm trần vùng / cặp đôi.
  - KT (Kỹ thuật): Chèn bước sinh sở thích từ dữ liệu.
  - HP (Học phần): Chèn bước kiểm không trùng lịch, đủ tín chỉ.
  - TS (Tuyển sinh): Chèn xét tuyển bổ sung.
  - LG (Logistics): Chèn bộ gom lô.
  - TC (Tài chính): Chèn bước chờ phê duyệt hai người.

### Z4 — Kiểm chứng ổn định nhanh (verify_stability)
- **Mức / quy mô:** Sửa mã / S
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L456–524 (gọi hàm lựa chọn ở L511)
- **Hàm:** verify_stability
- **Hiện trạng:** Với mỗi cặp (học sinh, CLB học sinh ưa hơn) gọi lại club_choice_function trên tập 'đang giữ + 1' (L511), tức sắp xếp lại cả tập mỗi lần. Đo trên mã thật (20 CLB, tỉ lệ chỗ 1,0): ở 10.000 học sinh run_rbda mất 1,08 s còn verify_stability mất 22–24 s (≈20 lần; hai lần đo).
- **Thay đổi:** Sắp sẵn danh sách thứ hạng của từng CLB một lần rồi tra vị trí bằng tìm kiếm nhị phân. Giữ bản gốc làm 'bản chậm' để đối chiếu (file kèm: de_xuat_verify_nhanh.py).
- **Rủi ro:** Bản nhanh gắn với đúng cấu trúc hai lượt (dự trữ rồi phổ thông). Hàm lựa chọn khác phải dùng bản chậm hoặc có bản nhanh riêng.
- **Kiểm nhận:** Đã thử (kiem_verify_nhanh.py): 7 cấu hình, danh sách cặp phá vỡ giống hệt bản gốc, gồm 3 kết quả thật (0 cặp) và 4 kết quả hoán đổi với 23.110 cặp nhân tạo; ở 10.000 học sinh 22,4 s → 0,09 s.
- **Phụ thuộc:** Z6
- **Ngành cần (R):** VL, TS, LG · **tuỳ chọn (O):** DT, KTX, SK, NT, YT, KT, HP, NS, TC
- **Khác nhau theo ngành:**
  - VL (Việc làm tự do): Quy mô nền tảng.
  - TS (Tuyển sinh): 10⁴–10⁵ thí sinh: bản chậm không dùng được.
  - LG (Logistics): Quy mô đơn hàng theo lô.

### Z5 — Trần vòng lặp và tài liệu về số vòng
- **Mức / quy mô:** Sửa mã / S
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L315 (max_rounds=1000), L372, L429–434
- **Hàm:** run_rbda
- **Hiện trạng:** Docstring nói số vòng 'đúng bằng độ dài danh sách nguyện vọng dài nhất' và trần 1000 gấp 100 lần mức cần. Bộ thử tải 204 lần chạy của chính dự án cho thấy khác: danh sách 3 mục → tối đa 37 vòng, 5 mục → 84, 10 mục → 227 (trung vị 9 / 14 / 18). Trần 1000 chỉ gấp ≈4,4 lần mức cao nhất đã thấy. Các lần chạy tự sinh của tôi (2.000–50.000 học sinh) chỉ 21–33 vòng nên chưa chạm trần; khi chạm, L429 ném RuntimeError và coi là 'dữ liệu hỏng'.
- **Thay đổi:** Đổi chốt chặn thành cận chứng minh được: số vòng ≤ tổng độ dài các danh sách nguyện vọng (mỗi vòng có ít nhất một đề nghị, mỗi em đề nghị tối đa len(prefs) lần). Sửa docstring.
- **Rủi ro:** Thấp.
- **Kiểm nhận:** Test với dữ liệu tạo chuỗi đẩy dài (cascade).
- **Phụ thuộc:** Z6
- **Ngành cần (R):** VL, TS, LG · **tuỳ chọn (O):** DT, KTX, SK, NT, YT, KT, HP, NS, TC
- **Khác nhau theo ngành:**
  - VL (Việc làm tự do): Quy mô nền tảng.
  - TS (Tuyển sinh): Quy mô lớn, danh sách dài.
  - LG (Logistics): Quy mô đơn hàng.

### Z6 — Bộ test và dữ liệu mô phỏng cho từng hàm mới
- **Mức / quy mô:** Viết mới / M mỗi ngành
- **Tệp:** tests/ (không có trong gói zip); du_lieu_test/tao_*.py; du_lieu_test/thu_tai/
- **Dòng:** —
- **Hàm:** TestTrungKhit; chay_thu_tai.py
- **Hiện trạng:** Tài liệu ghi 37 tệp test, 483 ca, 25 lỗi đã tìm và sửa (10 lỗi im lặng). Có test canh 'trùng khít' khi thêm nhiều buổi và test đối chứng ngược cho bộ đếm cặp phá vỡ. Các bộ sinh dữ liệu chỉ sinh dữ liệu câu lạc bộ.
- **Thay đổi:** Mỗi hàm lựa chọn đăng ký mới phải qua: (1) thuộc tính thay thế được và luật tổng cầu bằng kiểm thử ngẫu nhiên trên tập nhỏ; (2) cấu hình mặc định cho kết quả trùng khít; (3) bộ sinh dữ liệu của ngành đó và chạy lại bộ thử tải.
- **Rủi ro:** Thiếu (1) thì DA có thể không cho kết quả ổn định, và người dùng chỉ thấy cặp phá vỡ ở bước verify làm hỏng cả lần chạy.
- **Kiểm nhận:** Chính là bộ test.
- **Phụ thuộc:** không
- **Ngành cần (R):** DT, KTX, SK, NT, YT, VL, KT, HP, TS, NS, LG, TC · **tuỳ chọn (O):** —
- **Khác nhau theo ngành:**
  - DT (Đề tài): Test cặp phá vỡ của SPA.
  - KT (Kỹ thuật): Test đủ vai trò.
  - HP (Học phần): Test không trùng lịch và đủ tín chỉ.
  - LG (Logistics): Như TC.
  - TC (Tài chính): Test cho hàm ba lô: kỳ vọng là KHÔNG ổn định, phải đo tỉ lệ cặp phá vỡ.

### Z7 — Cổng cắm cho hàm ưu tiên, hàm lựa chọn, luật đủ tư cách
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py; api.py
- **Dòng:** rbda L357, L404, L511; api.py L1041
- **Hàm:** run_rbda, verify_stability, default_reserve_eligible_fn
- **Hiện trạng:** run_rbda gọi compute_club_priority (L357) và club_choice_function (L404) theo tên; verify_stability gọi club_choice_function (L511) theo tên; api.py L1041 chọn luật đủ tư cách bằng cách gọi default_reserve_eligible_fn. Chưa có tham số nào để thay.
- **Thay đổi:** Thêm ba tham số (priority_fn, choice_fn, eligible_fn) có mặc định bằng hàm hiện tại; run_rbda_nhieu_buoi và run_full_pipeline chuyển tiếp; đăng ký theo tên trong cấu hình ngành.
- **Rủi ro:** Thấp nếu mặc định giữ nguyên (test trùng khít).
- **Kiểm nhận:** Test trùng khít mặc định.
- **Phụ thuộc:** Z6, Z3
- **Ngành cần (R):** DT, KTX, SK, NT, YT, VL, KT, HP, TS, NS, LG, TC · **tuỳ chọn (O):** —

## Nhóm A — Lõi thuật toán — phụ thuộc ngành

### A1 — Hàm ưu tiên theo ngành (thay compute_club_priority)
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L123–191 (+ L1723–1753 hop_ung_vien)
- **Hàm:** compute_club_priority
- **Hiện trạng:** Khoá cứng: Tầng 1 (có điểm) sắp theo −điểm rồi số bốc thăm; Tầng 2 (không điểm) sắp theo số bốc thăm; Tầng 1 luôn đứng trước. Mỗi cặp (CLB, ứng viên) chỉ có MỘT điểm. Hàm cố ý không nhận thứ hạng nguyện vọng (ràng buộc chống nội sinh ghi trong docstring).
- **Thay đổi:** Cho phép khoá ưu tiên là bộ tiêu chí có thứ tự (nhóm → điểm tổng hợp có trọng số → tiêu chí phụ → bốc thăm) cấu hình theo ngành. GIỮ nguyên ràng buộc: không đưa thứ hạng nguyện vọng hay kết cục buổi trước vào.
- **Rủi ro:** Nếu tiêu chí phụ đọc được thứ hạng nguyện vọng hoặc kết cục buổi trước thì mở kênh khai gian. Với trường hợp kết cục buổi trước, TN7d của dự án đã đo: 113/300 em tìm ra cách giấu bớt buổi có lợi.
- **Kiểm nhận:** Test chống nội sinh: đổi nguyện vọng của một em không được đổi khoá ưu tiên của CLB nào.
- **Phụ thuộc:** Z7
- **Ngành cần (R):** KTX, SK, VL, KT, TS, NS, LG, TC · **tuỳ chọn (O):** DT, NT, YT, HP
- **Khác nhau theo ngành:**
  - DT (Đề tài): Hai tầng hiện có khớp (đã phỏng vấn / chưa).
  - KTX (Ký túc xá): Khoảng cách (km) + điểm hoàn cảnh tính từ dữ liệu.
  - SK (Sự kiện): Tầng theo loại vé (VIP, diễn giả) rồi bốc thăm.
  - NT (Ngoài trường): Dùng điểm phỏng vấn hiện có.
  - YT (Y tế): Xếp hạng đầy đủ nên ít hoà điểm.
  - VL (Việc làm tự do): Điểm phù hợp tính từ hồ sơ.
  - KT (Kỹ thuật): Điểm tính từ chi phí, thời gian, năng lực máy.
  - HP (Học phần): Điều kiện tiên quyết là bộ lọc (A5), không phải ưu tiên.
  - TS (Tuyển sinh): Điểm tổ hợp + điểm cộng + khu vực cho từng (thí sinh, ngành); quy tắc ở ngưỡng.
  - NS (Nhân sự): Điểm đánh giá + thâm niên; quản lý xếp tay một phần (khớp Tầng 1/2).
  - LG (Logistics): Chi phí / khoảng cách.
  - TC (Tài chính): Tải hiện tại + chuyên môn; quản lý duyệt.

### A2 — Luật hoà điểm: bốc thăm hay tiêu chí khác
- **Mức / quy mô:** Sửa mã / S–M
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L123–191, L757–814, L1086–1109, L1112–1182
- **Hàm:** compute_club_priority, sinh_stb_theo_buoi, generate_stb_lottery, chen_stb_cho_hoc_sinh_moi
- **Hiện trạng:** Hoà điểm và Tầng 2 luôn do số bốc thăm (STB) quyết định. STB là một hoán vị dùng chung, khoá sau lần chạy đầu, hoán vị lại mỗi buổi (stb_ngay); học sinh đến muộn được chèn ngẫu nhiên đều. Không có lựa chọn khác.
- **Thay đổi:** Thêm chính sách hoà điểm: 'boc_tham' (hiện tại) | 'tieu_chi_phu' (xác định, ghi log) | 'nhan_het' (nhận mọi người bằng điểm ở ngưỡng, vượt chỉ tiêu). Giữ nguyên cơ chế khoá và seed cho nhánh bốc thăm.
- **Rủi ro:** 'nhan_het' làm số người vượt capacity nên phải sửa sanity_check_result (L2128 kiểm 'không CLB nào vượt capacity').
- **Kiểm nhận:** Test sanity có cờ vượt chỉ tiêu; báo cáo ghi rõ chính sách đã dùng.
- **Phụ thuộc:** A1
- **Ngành cần (R):** TS, NS, TC · **tuỳ chọn (O):** YT
- **Khác nhau theo ngành:**
  - YT (Y tế): Ít hoà điểm; giữ bốc thăm làm bước cuối.
  - TS (Tuyển sinh): Công lập thường không chấp nhận bốc thăm: cần 'nhận hết' hoặc tiêu chí phụ; tư thục có thể dùng bốc thăm.
  - NS (Nhân sự): Bốc thăm không được chấp nhận trong nhân sự: dùng thâm niên / khoảng cách, bốc thăm chỉ là bước cuối có log.
  - TC (Tài chính): Tiêu chí phụ xác định (tải hiện tại, thâm niên); vẫn ghi seed nếu có bốc thăm.

### A3 — Hàm lựa chọn theo ngành (thay / bổ sung club_choice_function)
- **Mức / quy mô:** Viết mới / L (XL với ba lô)
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L236–292; gọi ở L404 (run_rbda) và L511 (verify_stability)
- **Hàm:** club_choice_function
- **Hiện trạng:** Hai lượt: lượt dự trữ lấy tối đa reserve_capacity em đủ tư cách theo thứ hạng; lượt phổ thông lấy phần còn lại trong số chưa được chọn. Một hàm duy nhất cho mọi CLB; sức chứa là một con số.
- **Thay đổi:** Đăng ký thêm hàm lựa chọn theo ngành: hai tầng đề tài–giảng viên, theo ô vai trò, chỉ tiêu dọc/ngang chồng lấn, trần theo vùng, mức tối thiểu và trần cứng, ba lô theo khối lượng. Mỗi hàm kèm bản kiểm chứng tương ứng (Z4, Z6).
- **Rủi ro:** DA chỉ giữ bảo đảm ổn định khi hàm lựa chọn thay thế được và thoả luật tổng cầu. Ba lô (TC, LG) không thoả nên mất bảo đảm (xem A12).
- **Kiểm nhận:** Test thay thế được + tổng cầu (Z6).
- **Phụ thuộc:** Z7
- **Ngành cần (R):** DT, NT, YT, KT, TS, LG, TC · **tuỳ chọn (O):** KTX, SK, VL, HP, NS
- **Khác nhau theo ngành:**
  - DT (Đề tài): Hai tầng: đề tài trong giảng viên (SPA).
  - KTX (Ký túc xá): Dùng dự trữ mềm cho hoàn cảnh khó khăn.
  - SK (Sự kiện): Dùng dự trữ mềm hiện có cho VIP.
  - NT (Ngoài trường): Trần cứng cho trại ngủ đêm (nam/nữ); mức tối thiểu.
  - YT (Y tế): Trần theo vùng = dự trữ trên nhiều bệnh viện.
  - VL (Việc làm tự do): Dự trữ mềm cho người mới.
  - KT (Kỹ thuật): Mỗi ô vai trò có sức chứa và ưu tiên riêng; chứng chỉ là bộ lọc.
  - HP (Học phần): Dự trữ mềm theo ngành và năm học.
  - TS (Tuyển sinh): Chỉ tiêu dọc/ngang chồng lấn; chọn thứ tự xử lý dự trữ.
  - NS (Nhân sự): Dự trữ mềm cho ưu tiên nội bộ.
  - LG (Logistics): Tải trọng, thể tích nhiều chiều (ba lô): không thay thế được.
  - TC (Tài chính): Sức chứa theo khối lượng hồ sơ (ba lô): không thay thế được.

### A4 — Dự trữ cứng / mềm và thứ tự xử lý dự trữ
- **Mức / quy mô:** Sửa mã / S–M
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L236–292; schema clubs L1251
- **Hàm:** club_choice_function
- **Hiện trạng:** Dự trữ luôn mềm (suất thừa chuyển thành chỗ phổ thông) và luôn xét TRƯỚC lượt phổ thông. Không có lựa chọn.
- **Thay đổi:** Thêm tham số loai_du_tru ('mem' | 'cung') và thu_tu ('du_tru_truoc' | 'pho_thong_truoc'); ghi vào run_meta và tệp xuất để người đọc biết.
- **Rủi ro:** Thứ tự xử lý làm đổi kết quả, nên phải công bố.
- **Kiểm nhận:** Test hai thứ tự cho kết quả khác nhau trên ví dụ nhỏ; báo cáo ghi lựa chọn.
- **Phụ thuộc:** A3
- **Ngành cần (R):** NT, TS, NS · **tuỳ chọn (O):** KTX, SK, YT, VL, HP
- **Khác nhau theo ngành:**
  - NT (Ngoài trường): Trần cứng số chỗ nữ/nam.
  - TS (Tuyển sinh): Thứ tự xử lý dự trữ đổi kết quả; phải công bố.
  - NS (Nhân sự): Nhóm 'người đang giữ vị trí'.

### A5 — Điều kiện đủ tư cách đa thuộc tính và bộ lọc cứng
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py; api.py
- **Dòng:** rbda L1709–1720, L1723–1753; api.py L1041; schema L1251, L1290
- **Hàm:** default_reserve_eligible_fn, hop_ung_vien
- **Hiện trạng:** Đủ tư cách = so sánh chuỗi students.reserve_group == clubs.reserve_group; mỗi bên chỉ MỘT nhãn. Không có bước loại ứng viên không đủ điều kiện (tiên quyết, chứng chỉ, giới tính) trước khi chạy.
- **Thay đổi:** Bảng thuộc tính nhiều giá trị (ứng viên–nhãn, đơn vị–nhãn yêu cầu); tách hai loại điều kiện: (a) bộ lọc cứng loại khỏi danh sách trước DA, (b) nhãn dự trữ (ưu tiên).
- **Rủi ro:** Bộ lọc đổi danh sách nguyện vọng: cần cảnh báo ứng viên không còn lựa chọn nào.
- **Kiểm nhận:** Test: ứng viên bị lọc không bao giờ được ghép; cảnh báo ở báo cáo sức khoẻ dữ liệu.
- **Phụ thuộc:** Z7, B2
- **Ngành cần (R):** KTX, YT, KT, HP, TS, NS · **tuỳ chọn (O):** DT, SK, NT, VL, LG, TC
- **Khác nhau theo ngành:**
  - KTX (Ký túc xá): Giới tính, loại phòng, hoàn cảnh.
  - YT (Y tế): Chứng chỉ hành nghề.
  - KT (Kỹ thuật): Chứng chỉ an toàn = bộ lọc.
  - HP (Học phần): Môn tiên quyết = bộ lọc.
  - TS (Tuyển sinh): Nhiều diện ưu tiên trên một thí sinh.
  - NS (Nhân sự): 'Người đang giữ vị trí' + kỹ năng.

### A6 — Mức tối thiểu và vòng đóng–mở lại
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L218–233 (loi_suc_chua); L877–985, vòng ngoài quanh run_rbda ở L973; schema L1251
- **Hàm:** loi_suc_chua, run_rbda_nhieu_buoi
- **Hiện trạng:** Chỉ có trần (capacity), không có mức tối thiểu. loi_suc_chua là luật duy nhất cho sức chứa (ba nơi dùng chung). Schema ép capacity > 0.
- **Thay đổi:** Thêm min_capacity; vòng ngoài: chạy DA → đóng đơn vị dưới mức tối thiểu → trả người về → chạy lại, tới khi mọi đơn vị mở đều đạt mức hoặc hết đơn vị để đóng. Đây là xấp xỉ: bài toán chính xác khó.
- **Rủi ro:** Mất ổn định chặt chẽ; kết quả phụ thuộc thứ tự đóng.
- **Kiểm nhận:** Báo cáo đơn vị bị đóng; kiểm mọi đơn vị mở đều đạt mức tối thiểu.
- **Phụ thuộc:** Z3, A3
- **Ngành cần (R):** NT, YT, HP · **tuỳ chọn (O):** SK, KT
- **Khác nhau theo ngành:**
  - NT (Ngoài trường): Khoá / trại không đủ người thì đóng.
  - YT (Y tế): Bệnh viện tuyến dưới cần mức tối thiểu.
  - HP (Học phần): Lớp dưới sĩ số tối thiểu.

### A7 — Sức chứa hai tầng và ghép nhiều–nhiều
- **Mức / quy mô:** Viết mới / L
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L299–311 (MatchResult), L315–452 (run_rbda), L236–292
- **Hàm:** MatchResult, run_rbda
- **Hiện trạng:** Mỗi ứng viên nhận ĐÚNG một đơn vị mỗi buổi; mỗi đơn vị có một sức chứa. MatchResult.assignment là dict {ứng viên: đơn vị} nên không biểu diễn được một ứng viên – nhiều đơn vị hay hai tầng sức chứa.
- **Thay đổi:** Hai tầng (đề tài trong giảng viên) = thuật toán SPA: hàm lựa chọn hai tầng + kết quả {ứng viên: đơn vị}; nhiều–nhiều: mỗi bài cần k phản biện, mỗi phản biện nhận tối đa m bài.
- **Rủi ro:** Định nghĩa cặp phá vỡ khác: phải viết lại verify_stability.
- **Kiểm nhận:** Test cặp phá vỡ SPA.
- **Phụ thuộc:** A3
- **Ngành cần (R):** DT, SK, KT · **tuỳ chọn (O):** YT, VL, TS, LG, TC
- **Khác nhau theo ngành:**
  - DT (Đề tài): Đề tài + giảng viên (SPA).
  - SK (Sự kiện): Mỗi bài cần k phản biện, mỗi phản biện ≤ m bài.
  - KT (Kỹ thuật): Ô theo vai trò trong dự án.

### A8 — Nhu cầu nhiều đơn vị và ràng buộc xuyên buổi
- **Mức / quy mô:** Viết mới / XL
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L877–985 (run_rbda_nhieu_buoi), L988–1009 (verify_stability_tuan), L703–737
- **Hàm:** run_rbda_nhieu_buoi, verify_stability_tuan
- **Hiện trạng:** Mỗi buổi chạy run_rbda ĐỘC LẬP (L973); mỗi em tối đa một CLB mỗi buổi; verify_stability_tuan dựa vào việc 'không ràng buộc nào nối hai buổi' (docstring L988). Đúng với lịch tách rời; sai nếu có trần tổng, điều kiện tiên quyết, môn đi kèm.
- **Thay đổi:** Giữ chạy độc lập cho trường hợp tách rời. Với ràng buộc xuyên buổi cần cơ chế đa đơn vị (vd chọn lần lượt có thứ tự ngẫu nhiên) và định nghĩa ổn định mới cho cả tuần.
- **Rủi ro:** Ổn định từng buổi không còn kéo theo ổn định cả tuần.
- **Kiểm nhận:** Test cho cả tuần; đo tỉ lệ vi phạm trên dữ liệu mô phỏng.
- **Phụ thuộc:** A3, Z3
- **Ngành cần (R):** HP · **tuỳ chọn (O):** SK, NT, YT, NS
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Phiên song song tách rời được: chỉ cấu hình.
  - NT (Ngoài trường): Chọn nhiều khoá vẫn tách rời được: chỉ cấu hình.
  - YT (Y tế): Luân khoa nhiều giai đoạn.
  - HP (Học phần): Tín chỉ tối thiểu/tối đa, môn tiên quyết, đủ k môn không trùng giờ: viết mới.
  - NS (Nhân sự): Luân chuyển nhiều vòng, không quay lại phòng ban đã qua.

### A9 — Lịch tổng quát thay cho nhãn buổi
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py; api_bao_cao.py
- **Dòng:** rbda L99–116, L575–700 (so_thu_trong_tuan L605, khoa_sap_buoi L649, nhom_theo_buoi L683); api_bao_cao L159–275
- **Hàm:** gom_theo_buoi, so_thu_trong_tuan, khoa_sap_buoi, nhom_theo_buoi
- **Hiện trạng:** 'Buổi' là nhãn chuỗi; hai CLB cùng nhãn = trùng giờ. Nhận ra thứ trong tuần (thu_2, t2, monday, thu_3_tiet_9) để sắp thứ tự ngày; nhãn lạ vẫn chạy nhưng xếp cuối theo vần chữ cái. Không có khoảng thời gian chồng lấn một phần.
- **Thay đổi:** Thêm khoảng thời gian (ngày, bắt đầu, kết thúc) cho mỗi đơn vị; xung đột = giao khoảng khác rỗng; thứ tự xét buổi theo ngày thật. Giữ nhãn cho trường học.
- **Rủi ro:** Thứ tự xét buổi ảnh hưởng kết quả ở một số chế độ bốc thăm; chế độ đang dùng (stb_ngay) đã khoá nên ít rủi ro.
- **Kiểm nhận:** Test trùng khít với nhãn cũ; test chồng lấn một phần.
- **Phụ thuộc:** B2
- **Ngành cần (R):** SK, NT, HP, LG · **tuỳ chọn (O):** YT, KT, NS
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Workshop chồng lấn một phần; xuất .ics.
  - NT (Ngoài trường): Đợt có ngày bắt đầu, kết thúc (thay 'buổi trong tuần').
  - YT (Y tế): Lịch luân khoa.
  - KT (Kỹ thuật): Ca / lịch rảnh.
  - HP (Học phần): Lịch học, phòng.
  - NS (Nhân sự): Ca trực.
  - LG (Logistics): Khung giờ giao.

### A10 — Cặp cấm / xung đột lợi ích
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L1723–1753 (hop_ung_vien), L456–524 (verify_stability), L1016–1083 (validate_data_integrity)
- **Hàm:** hop_ung_vien, verify_stability, validate_data_integrity
- **Hiện trạng:** Không có khái niệm cặp bị cấm: bất kỳ (ứng viên, đơn vị) trong danh sách nguyện vọng đều có thể được ghép.
- **Thay đổi:** Bảng cặp cấm (ứng viên, đơn vị); loại ở hop_ung_vien (trước DA); thêm kiểm 'không cặp cấm nào được ghép' ở verify và sanity; cảnh báo ở báo cáo sức khoẻ dữ liệu.
- **Rủi ro:** Loại cặp cấm tương đương rút khỏi danh sách nên kết quả vẫn ổn định theo danh sách đã lọc.
- **Kiểm nhận:** Test: không cặp cấm nào xuất hiện trong kết quả.
- **Phụ thuộc:** Z3, A5
- **Ngành cần (R):** SK, TC · **tuỳ chọn (O):** DT, YT, NS
- **Khác nhau theo ngành:**
  - DT (Đề tài): Quan hệ thân thuộc giảng viên – sinh viên.
  - SK (Sự kiện): Phản biện – tác giả.
  - YT (Y tế): Quan hệ thân thuộc.
  - NS (Nhân sự): Quan hệ nội bộ.
  - TC (Tài chính): Người có quan hệ với khách hàng không được thẩm định hồ sơ đó.

### A11 — Đăng ký theo nhóm / cặp đôi
- **Mức / quy mô:** Viết mới / XL
- **Tệp:** rbda_priority_pipeline.py
- **Dòng:** L315–452; schema preferences L1271
- **Hàm:** run_rbda
- **Hiện trạng:** Mỗi ứng viên xếp hạng độc lập (mỗi dòng preferences là một cặp ứng viên–đơn vị); không biểu diễn được 'hai người muốn cùng nơi'.
- **Thay đổi:** Nghiên cứu mở: ghép có cặp đôi có thể KHÔNG có kết quả ổn định. Đề xuất heuristic có báo cáo mức vi phạm, hoặc giới hạn nhóm ở mức đơn vị lớn (toà nhà, thành phố) thay vì ghép bạn cùng phòng.
- **Rủi ro:** Mất bảo đảm ổn định; phải công bố rõ.
- **Kiểm nhận:** Đo tỉ lệ nhóm bị tách trên dữ liệu mô phỏng.
- **Phụ thuộc:** A3
- **Ngành cần (R):** YT · **tuỳ chọn (O):** KTX, NT
- **Khác nhau theo ngành:**
  - KTX (Ký túc xá): Nhóm 2–4 người; không ghép bạn cùng phòng bằng DA.
  - NT (Ngoài trường): Nhóm bạn đi cùng.
  - YT (Y tế): Cặp đôi muốn cùng thành phố: bắt buộc.

### A12 — Ổn định là chỉ số chất lượng, không phải điều kiện chặn
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** api.py
- **Dòng:** L1052–1071 (sanity_problems, stability_problems → rollback)
- **Hàm:** _run_pipeline_da_khoa
- **Hiện trạng:** Nếu verify_stability tìm thấy BẤT KỲ cặp phá vỡ nào thì cả lần chạy bị rollback (L1062–1071). Hợp lý khi hàm lựa chọn thay thế được; sai khi hàm lựa chọn là ba lô.
- **Thay đổi:** Thêm chế độ 'bao_dam' (hiện tại) và 'do_luong': ghi số cặp phá vỡ vào báo cáo và run_history rồi vẫn lưu kết quả; ngưỡng cảnh báo cấu hình được.
- **Rủi ro:** Bỏ bảo đảm lý thuyết: phải ghi trong báo cáo và hợp đồng.
- **Kiểm nhận:** Test: ở chế độ đo lường, kết quả vẫn được lưu và số cặp phá vỡ được ghi.
- **Phụ thuộc:** Z3
- **Ngành cần (R):** LG, TC · **tuỳ chọn (O):** NT, YT, KT, HP
- **Khác nhau theo ngành:**
  - NT (Ngoài trường): Khi dùng mức tối thiểu xấp xỉ.
  - YT (Y tế): Khi có cặp đôi.
  - KT (Kỹ thuật): Khi có ô vai trò.
  - HP (Học phần): Khi có ràng buộc xuyên buổi.
  - LG (Logistics): Tải trọng / thể tích kiểu ba lô: đo cặp phá vỡ như chỉ số.
  - TC (Tài chính): Sức chứa theo khối lượng hồ sơ.

## Nhóm B — Mô hình dữ liệu và CSDL

### B1 — Điểm và thuộc tính theo cặp (đang là một số thực ≥ 0)
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py; api_cham_diem.py; api_nhap.py
- **Dòng:** schema L1265 (club_scores), L1260–1271; api_cham_diem L69–137; api_nhap L996–1194
- **Hàm:** club_scores.score
- **Hiện trạng:** Mỗi cặp (ứng viên, đơn vị) có đúng một điểm, kiểu REAL, NOT NULL, CHECK (score >= 0). Không có chỗ cho nhiều tiêu chí, điểm âm (điểm rủi ro, chi phí), ngày hay khoảng cách.
- **Thay đổi:** Bảng thuộc tính theo cặp dạng khoá–giá trị (hoặc cột JSON) rồi hàm ưu tiên đọc ra; bỏ CHECK ≥ 0 hoặc đổi theo kiểu thuộc tính; migrate bằng di_tru_schema (L1568) vì đã có sao lưu và dựng lại bảng.
- **Rủi ro:** Dữ liệu cũ phải còn chạy được (di_tru_schema idempotent).
- **Kiểm nhận:** Test migration trên app.db cũ; test trùng khít.
- **Phụ thuộc:** Z6
- **Ngành cần (R):** KTX, VL, KT, TS, NS, LG, TC · **tuỳ chọn (O):** YT
- **Khác nhau theo ngành:**
  - KTX (Ký túc xá): Km, điểm hoàn cảnh.
  - VL (Việc làm tự do): Điểm phù hợp.
  - KT (Kỹ thuật): Chi phí, thời gian: có thể âm.
  - TS (Tuyển sinh): Điểm tổ hợp, điểm cộng, nhiều thang.
  - NS (Nhân sự): Điểm năng lực.
  - LG (Logistics): Khoảng cách, chi phí.
  - TC (Tài chính): Tải, chuyên môn.

### B2 — Bảng thực thể mới theo ngành
- **Mức / quy mô:** Viết mới / M mỗi ngành
- **Tệp:** rbda_priority_pipeline.py; api_quan_ly.py
- **Dòng:** schema L1240–1300; di_tru_schema L1568–1666
- **Hàm:** DEFAULT_SCHEMA, di_tru_schema
- **Hiện trạng:** Schema nghiệp vụ chỉ có 6 bảng: students, clubs, club_test_selection, club_scores, preferences, match_results (cộng bảng kiểm toán). di_tru_schema nâng cấp idempotent, có sao lưu.
- **Thay đổi:** Mỗi ngành thêm bảng riêng và màn hình quản lý, dùng đúng cơ chế di_tru_schema.
- **Rủi ro:** Thấp nếu tuân theo di_tru_schema.
- **Kiểm nhận:** Test migration + test nhập/xuất bảng mới.
- **Phụ thuộc:** Z6
- **Ngành cần (R):** DT, KTX, SK, NT, YT, VL, KT, HP, TS, NS, LG, TC · **tuỳ chọn (O):** —
- **Khác nhau theo ngành:**
  - DT (Đề tài): Giảng viên; quan hệ đề tài–giảng viên.
  - KTX (Ký túc xá): Phòng/giường, hợp đồng, người đang ở.
  - SK (Sự kiện): Vé, phiên, diễn giả.
  - NT (Ngoài trường): Đợt, lệ phí, trạng thái thanh toán.
  - YT (Y tế): Lịch luân khoa nhiều giai đoạn, chứng chỉ hành nghề.
  - VL (Việc làm tự do): Hồ sơ, ngân sách, thanh toán.
  - KT (Kỹ thuật): Kỹ năng, chứng chỉ, lịch rảnh, vai trò.
  - HP (Học phần): Lịch học, phòng, tín chỉ, môn tiên quyết.
  - TS (Tuyển sinh): Tổ hợp xét tuyển, đối tượng ưu tiên, điểm cộng.
  - NS (Nhân sự): Kỹ năng, chứng chỉ, địa điểm, định biên.
  - LG (Logistics): Bản đồ/GPS, khung giờ, tải trọng.
  - TC (Tài chính): Khách hàng, chuyên viên, khối lượng hồ sơ.

### B3 — Sinh danh sách sở thích từ dữ liệu
- **Mức / quy mô:** Viết mới / L
- **Tệp:** mô-đun mới (thay nguồn của api_nhap.import_preferences_csv)
- **Dòng:** api_nhap L814–994
- **Hàm:** import_preferences_csv
- **Hiện trạng:** Nguồn nguyện vọng duy nhất là người dùng tự xếp (Forms, CSV, kiosk). Không có bên nào sinh thứ hạng từ dữ liệu.
- **Thay đổi:** Mô-đun sinh thứ hạng từ chi phí, thời gian, khoảng cách, năng lực; ghi lại cách tính để kiểm toán.
- **Rủi ro:** Chất lượng kết quả phụ thuộc hàm sở thích; kênh khai gian chuyển sang dữ liệu đầu vào.
- **Kiểm nhận:** So sánh với xếp hạng thủ công trên mẫu nhỏ.
- **Phụ thuộc:** B1, Z3
- **Ngành cần (R):** VL, KT, LG, TC · **tuỳ chọn (O):** KTX, NS
- **Khác nhau theo ngành:**
  - VL (Việc làm tự do): Gợi ý danh sách ngắn.
  - KT (Kỹ thuật): Máy / tác vụ không có người xếp hạng.
  - LG (Logistics): Đơn hàng – xe theo khoảng cách, chi phí.
  - TC (Tài chính): Khách hàng không xếp hạng chuyên viên.

## Nhóm C — Nhập, xuất, giải trình

### C1 — Nhập dữ liệu: ánh xạ cột và kết nối hệ thống nguồn
- **Mức / quy mô:** Sửa mã / L
- **Tệp:** api_nhap.py
- **Dòng:** L240–320 (detect_csv_kind, import_csv_auto), L339–425, L814–994, L996–1194
- **Hàm:** import_csv_auto, import_clubs_csv, import_preferences_csv, import_test_selection_csv
- **Hiện trạng:** Nhập CSV/Excel theo hợp đồng cột cố định (club_id, name, capacity, reserve_*; student_id, test_club_k, score_k, pref_k hoặc <buoi>_pref_k); nhận loại tệp theo tiêu đề; đã có kiểm Excel cắt số 0 đầu, trùng hoa/thường, trùng dòng. Chưa có kết nối API.
- **Thay đổi:** Tầng ánh xạ cột (tệp cấu hình theo nguồn) và bộ kết nối (REST hoặc CSV định kỳ) đặt trước import_csv_auto; giữ nguyên các kiểm tra dữ liệu.
- **Rủi ro:** Mỗi nguồn có lỗi dữ liệu riêng; phải giữ các kiểm tra 'im lặng' đã có.
- **Kiểm nhận:** Test với tệp mẫu của từng nguồn.
- **Phụ thuộc:** B2
- **Ngành cần (R):** SK, VL, KT, HP, TS, NS, LG, TC · **tuỳ chọn (O):** DT, KTX, NT, YT
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Hệ thống bán vé.
  - VL (Việc làm tự do): API thời gian thực + thanh toán.
  - KT (Kỹ thuật): ERP / quản lý dự án.
  - HP (Học phần): Phần mềm quản lý đào tạo.
  - TS (Tuyển sinh): Điểm từ Sở hoặc nhà trường.
  - NS (Nhân sự): Phần mềm nhân sự.
  - LG (Logistics): TMS, GPS.
  - TC (Tài chính): Triển khai tại chỗ, dữ liệu không ra khỏi ngân hàng.

### C2 — Xuất lịch và thông báo (.ics, thư)
- **Mức / quy mô:** Viết mới / S–M
- **Tệp:** api_xuat.py; api_bao_cao.py
- **Dòng:** api_xuat L825–1080, L81–148; api_bao_cao L226–275
- **Hàm:** _export_csv_da_khoa, _xuat_excel, get_thoi_khoa_bieu
- **Hiện trạng:** Xuất CSV (UTF-8 BOM, số kiểu Việt Nam) và Excel nhiều trang; thời khoá biểu tuần là bảng chứ không phải lịch cá nhân.
- **Thay đổi:** Thêm xuất .ics cho từng người và mẫu thông báo.
- **Rủi ro:** Thấp.
- **Kiểm nhận:** Mở thử .ics trong Outlook/Google Calendar.
- **Phụ thuộc:** A9
- **Ngành cần (R):** SK, HP · **tuỳ chọn (O):** NT, KT, TS, LG
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Lịch cá nhân .ics là bắt buộc.
  - HP (Học phần): Thời khoá biểu cá nhân.

### C3 — Giải trình từng cá nhân (vì sao không trúng / không có chỗ)
- **Mức / quy mô:** Viết mới / M
- **Tệp:** api_bao_cao.py; api_xuat.py
- **Dòng:** api_bao_cao L368–479; api_xuat L468–541
- **Hàm:** get_phan_bo_nguyen_vong, get_em_chua_co_cho, get_thay_doi_ket_qua
- **Hiện trạng:** Có thống kê phân bố nguyện vọng, danh sách em chưa có chỗ kèm nguyện vọng đã khai, và so sánh với lần chạy trước. Chưa có bản giải trình từng người: 'ở nguyện vọng k đơn vị đã đầy tới thứ hạng nào, em đứng thứ mấy'.
- **Thay đổi:** Sinh từ MatchResult.rejection_log và base_rank (đã có sẵn trong kết quả): với mỗi nguyện vọng bị từ chối, vòng nào, thứ hạng của em và thứ hạng cuối được nhận.
- **Rủi ro:** Lộ thông tin xếp hạng của người khác: chỉ hiện ngưỡng, không hiện tên.
- **Kiểm nhận:** Test: bản giải trình khớp kết quả và không chứa mã người khác.
- **Phụ thuộc:** Z7
- **Ngành cần (R):** KTX, TS, NS, TC · **tuỳ chọn (O):** DT, YT, VL, HP
- **Khác nhau theo ngành:**
  - KTX (Ký túc xá): Giải thích phân phòng.
  - TS (Tuyển sinh): Phúc khảo: điểm chuẩn từng nguyện vọng.
  - NS (Nhân sự): Giải thích quyết định nhân sự.
  - TC (Tài chính): Kiểm toán: lý do mỗi phân công.

## Nhóm E — Vận hành, bảo mật, tuân thủ

### E1 — Máy chủ nhiều người dùng, phân quyền, mã hoá
- **Mức / quy mô:** Viết mới / XL
- **Tệp:** browser_host.py; rbda_priority_pipeline.py; api.py
- **Dòng:** browser_host L186–208, L535–634; rbda L1416–1441; api.py L78–103
- **Hàm:** _Handler._authorized, _host_hop_le, serve, connect_db
- **Hiện trạng:** Chạy trên MỘT máy Windows: pywebview hoặc máy chủ cục bộ 127.0.0.1 với MỘT token và chặn DNS rebinding; dữ liệu là MỘT tệp app.db (SQLite, không WAL, khoá ghi trong tiến trình). Không có tài khoản, vai trò, mã hoá dữ liệu lúc nghỉ.
- **Thay đổi:** Chế độ máy chủ: tài khoản và vai trò (nhập, chấm, chạy, duyệt, xem), mã hoá tệp CSDL hoặc chuyển sang CSDL máy chủ. browser_host.py là điểm xuất phát vì đã có kiểm tra Host, token.
- **Rủi ro:** Bề mặt tấn công lớn hơn nhiều khi rời khỏi 127.0.0.1.
- **Kiểm nhận:** Kiểm thử phân quyền; rà soát bảo mật độc lập.
- **Phụ thuộc:** Z3
- **Ngành cần (R):** VL, TS, NS, LG, TC · **tuỳ chọn (O):** KTX, SK, YT, KT, HP
- **Khác nhau theo ngành:**
  - VL (Việc làm tự do): Nền tảng web nhiều người dùng.
  - TS (Tuyển sinh): Cấp tỉnh, nhiều đơn vị.
  - NS (Nhân sự): Vai trò HR / quản lý.
  - LG (Logistics): Nhiều điều phối viên.
  - TC (Tài chính): Triển khai tại chỗ, phân quyền theo vai trò, mã hoá.

### E2 — Nhật ký kiểm toán và phê duyệt hai người
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** api.py; rbda_priority_pipeline.py
- **Dòng:** api.py L565–584; schema run_history/run_meta/stb_lock; dau_van_tay_du_lieu L1756–1793
- **Hàm:** get_run_history, dau_van_tay_du_lieu
- **Hiện trạng:** Đã có: run_history không bao giờ ghi đè (seed, thời điểm, STB có vẽ lại không, buổi đã chạy), khoá STB cùng hạt giống, dấu vân tay SHA-256 của dữ liệu đầu vào, ảnh chụp ket_qua_truoc. Chưa có: danh tính người chạy / người duyệt; nhật ký chống sửa (ai ghi được app.db thì sửa được run_history).
- **Thay đổi:** Thêm cột người chạy, người duyệt; bước 'chờ duyệt' trước khi ghi match_results; chuỗi băm nối các dòng nhật ký.
- **Rủi ro:** Thấp.
- **Kiểm nhận:** Test: không chạy được nếu thiếu người duyệt khi bật chế độ này.
- **Phụ thuộc:** Z3
- **Ngành cần (R):** YT, TS, NS, TC · **tuỳ chọn (O):** KTX, VL
- **Khác nhau theo ngành:**
  - YT (Y tế): Quyết định có hệ quả nghề nghiệp.
  - TS (Tuyển sinh): Công bố kết quả có ký.
  - NS (Nhân sự): Duyệt quyết định.
  - TC (Tài chính): Phê duyệt hai người; ghi đầu vào nào, ai chạy.

### E3 — Dữ liệu cá nhân: đồng ý, thời hạn lưu, xoá
- **Mức / quy mô:** Sửa mã / M–L
- **Tệp:** api_quan_ly.py; api_xuat.py; rbda_priority_pipeline.py
- **Dòng:** api_quan_ly L569–638, L519–546; api_xuat L594–809; rbda L1756–1793
- **Hàm:** reset_data, delete_student, export_du_lieu_dau_vao
- **Hiện trạng:** Có xoá toàn bộ / xoá học sinh (luôn sao lưu trước; run_history giữ lại). Chưa có: ghi nhận đồng ý (cha mẹ nếu là trẻ em), thời hạn lưu theo loại dữ liệu, xoá theo hạn, nhật ký truy cập. Các bản sao lưu app.db.bak-* cũng chứa dữ liệu nên phải nằm trong chính sách xoá.
- **Thay đổi:** Bảng đồng ý và thời hạn lưu; tác vụ xoá / ẩn danh theo hạn, kể cả bản sao lưu; xuất dữ liệu tối thiểu. Pháp lý: Luật 91/2025/QH15 hiệu lực 01/01/2026 (nên nhờ chuyên gia pháp lý kiểm tra điều khoản cụ thể).
- **Rủi ro:** Rủi ro pháp lý nếu bán cho tổ chức xử lý dữ liệu nhạy cảm.
- **Kiểm nhận:** Test: xoá theo hạn xoá cả bản sao lưu.
- **Phụ thuộc:** B2
- **Ngành cần (R):** KTX, NT, YT, VL, TS, NS, LG, TC · **tuỳ chọn (O):** DT, SK, KT, HP
- **Khác nhau theo ngành:**
  - KTX (Ký túc xá): Hoàn cảnh gia đình nhạy cảm.
  - NT (Ngoài trường): Trẻ em: đồng ý của cha mẹ.
  - YT (Y tế): Chỉ dữ liệu nhân sự, không đưa dữ liệu bệnh nhân vào.
  - VL (Việc làm tự do): Thanh toán.
  - TS (Tuyển sinh): Dữ liệu thí sinh, giấy tờ tuỳ thân.
  - NS (Nhân sự): Xoá khi nghỉ việc.
  - LG (Logistics): Vị trí cá nhân.
  - TC (Tài chính): Dữ liệu tài chính khách hàng + quy định ngân hàng.

## Nhóm G — Thời gian thực

### G1 — Đến muộn / sức chứa giảm: tiếp tục DA từ trạng thái cũ (nâng cấp 1)
- **Mức / quy mô:** Sửa mã / M
- **Tệp:** rbda_priority_pipeline.py; api.py
- **Dòng:** rbda L315–452, L299–311, L1112–1182; api.py L858–871, L1013–1027
- **Hàm:** run_rbda, MatchResult, chen_stb_cho_hoc_sinh_moi, chi_buoi
- **Hiện trạng:** Mọi lần chạy đọc toàn bộ app.db rồi chạy lại từ đầu. Đã có: chạy riêng một buổi (chi_buoi), chèn STB cho em đến muộn mà giữ thứ tự tương đối của em cũ, ảnh chụp và so sánh kết quả. MatchResult lưu assignment, rank_in_student_pref, base_rank, rejection_log nên trạng thái cuối của DA khôi phục được.
- **Thay đổi:** run_rbda nhận trạng thái ban đầu (held, next_choice_idx) khôi phục từ MatchResult; base_rank giữ dạng có chỉ mục để chèn ứng viên mới thay vì sắp lại; cửa sổ chạy lại theo chu kỳ.
- **Rủi ro:** Kết quả đã công bố vẫn có thể bị hạ chỗ (đã đo, xem mục 3.3): cần G3.
- **Kiểm nhận:** Đã thử: tiếp tục từ trạng thái cũ cho đúng kết quả của chạy lại toàn bộ (38/38 lần, 4 cấu hình).
- **Phụ thuộc:** Z3, Z4
- **Ngành cần (R):** SK, NT, KT, HP, TC · **tuỳ chọn (O):** KTX, YT, VL, TS, NS, LG
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Khách đến tại chỗ.
  - NT (Ngoài trường): Đăng ký muộn.
  - KT (Kỹ thuật): Máy hỏng = giảm sức chứa.
  - HP (Học phần): Tuần thêm–bớt môn.
  - TC (Tài chính): Khách hàng mới.

### G2 — Huỷ / sức chứa tăng: rút lui (nâng cấp 2)
- **Mức / quy mô:** Sửa mã / M–L
- **Tệp:** rbda_priority_pipeline.py; api_quan_ly.py
- **Dòng:** rbda L315–452; api_quan_ly L495–546
- **Hàm:** reset_student_entry, delete_student
- **Hiện trạng:** delete_student CHẶN nếu em đã có trong match_results (L519–546): hiện chưa có đường rút lui sau khi đã chạy, chỉ chạy lại toàn bộ.
- **Thay đổi:** Rút lui = bỏ em khỏi trạng thái, giải phóng chỗ, cho người xếp sau lên theo chuỗi chỗ trống (hoặc chạy lại có kiểm soát).
- **Rủi ro:** Có biến thể chưa có chứng minh; phương án 'ít chuyển chỗ' đổi phúc lợi lấy ít xáo trộn.
- **Kiểm nhận:** Test: kết quả sau rút lui ổn định theo verify.
- **Phụ thuộc:** G1
- **Ngành cần (R):** KTX, NT, YT, HP, TS, NS, TC · **tuỳ chọn (O):** SK, VL, KT, LG
- **Khác nhau theo ngành:**
  - KTX (Ký túc xá): Trả phòng giữa kỳ.
  - NT (Ngoài trường): Huỷ vì chưa đóng phí.
  - YT (Y tế): Rút lui.
  - HP (Học phần): Rút môn.
  - TS (Tuyển sinh): Xét tuyển bổ sung sau khi có người không nhập học.
  - NS (Nhân sự): Nghỉ việc.
  - TC (Tài chính): Chuyên viên nghỉ việc, chia lại danh mục.

### G3 — Bảo vệ người đã công bố (nâng cấp 3)
- **Mức / quy mô:** Viết mới / L
- **Tệp:** rbda_priority_pipeline.py; api.py; api_xuat.py
- **Dòng:** rbda L236–292, L456–524; api.py L1086–1104; api_xuat L468–541
- **Hàm:** club_choice_function, ket_qua_truoc, get_thay_doi_ket_qua
- **Hiện trạng:** ket_qua_truoc là bản chụp ngay trước lần chạy; get_thay_doi_ket_qua phân loại mới được xếp / mất chỗ / đổi CLB. Nhưng không có cờ 'đã công bố' để chặn việc hạ chỗ.
- **Thay đổi:** Cờ đã_công_bố trên match_results; hàm lựa chọn có 'tập được bảo vệ' (dự trữ mềm cho nhóm đã công bố) cộng ngân sách cặp phá vỡ chấp nhận được.
- **Rủi ro:** Tăng cặp phá vỡ; có thể bị giữ chỗ ảo.
- **Kiểm nhận:** Đo số em bị hạ chỗ trước và sau khi bật bảo vệ.
- **Phụ thuộc:** G1, A3
- **Ngành cần (R):** KTX, NT, NS, TC · **tuỳ chọn (O):** SK, YT, KT, HP, TS
- **Khác nhau theo ngành:**
  - KTX (Ký túc xá): Quyền giữ chỗ của người đang ở.
  - NT (Ngoài trường): Giữ chỗ người đã xác nhận.
  - NS (Nhân sự): Không ai bị chuyển sang nơi kém hơn hiện tại.
  - TC (Tài chính): Danh mục đã giao cho chuyên viên.

### G4 — Gom lô nhỏ theo cửa sổ thời gian (nâng cấp 4)
- **Mức / quy mô:** Viết mới / M–L
- **Tệp:** api.py (bộ lập lịch mới bọc quanh pipeline)
- **Dòng:** api.py L744–1316
- **Hàm:** _run_pipeline_da_khoa
- **Hiện trạng:** Chạy hoàn toàn thủ công: nút 'Chạy pipeline' với xác nhận hai bước.
- **Thay đổi:** Bộ lập lịch cửa sổ Δ (chạy mỗi Δ phút hoặc khi đủ N yêu cầu) cộng hàng đợi yêu cầu; đi kèm G1–G3.
- **Rủi ro:** Tái nhập ưu thế thứ tự đến nếu quy tắc kém: phải gom lô rồi xếp theo ưu tiên, không theo thời điểm đến.
- **Kiểm nhận:** Test: đổi thứ tự đến trong cùng một lô không đổi kết quả.
- **Phụ thuộc:** G1, G3
- **Ngành cần (R):** SK, VL, KT, HP, LG, TC · **tuỳ chọn (O):** NT
- **Khác nhau theo ngành:**
  - SK (Sự kiện): Đổi phiên trong ngày.
  - VL (Việc làm tự do): Việc mới liên tục.
  - KT (Kỹ thuật): Đơn hàng mới theo lô.
  - HP (Học phần): Tuần thêm–bớt môn.
  - LG (Logistics): Lô ngắn cho ngày hôm sau.
  - TC (Tài chính): Khách hàng mới theo lô.

### G5 — Đổi nguyện vọng và dòng liên tục (nâng cấp 5–6)
- **Mức / quy mô:** Viết mới / XL
- **Tệp:** mô-đun mới (họ thuật toán trực tuyến)
- **Dòng:** —
- **Hàm:** —
- **Hiện trạng:** Không có: lõi là DA theo lô tĩnh.
- **Thay đổi:** Họ thuật toán khác; nằm ngoài phạm vi sửa mã.
- **Rủi ro:** Không còn ổn định như lô tĩnh; chống khai gian không mặc nhiên.
- **Kiểm nhận:** Cần nghiên cứu riêng.
- **Phụ thuộc:** không
- **Ngành cần (R):** LG · **tuỳ chọn (O):** VL
- **Khác nhau theo ngành:**
  - VL (Việc làm tự do): Nếu việc phải giao ngay.
  - LG (Logistics): Điều phối tức thời (taxi, giao hàng): đã đánh giá là không nên bán bằng chương trình này.

## Kế hoạch theo ngành (đúng thứ tự làm, đã gồm tiền đề)

- **DT** (Phân bổ đề tài, đồ án, người hướng dẫn): Z6, Z3, Z7, Z1, B2, A3, A7  · tuỳ chọn: Z4, Z5, A1, A5, A10, C1, C3, E3
- **KTX** (Ký túc xá, nhà ở sinh viên, nhà ở xã hội): Z6, Z3, Z7, Z4*, Z1, B1, B2, A1, A3*, A5, C3, E3, G1*, G2, G3  · tuỳ chọn: Z5, A4, A11, B3, C1, E1, E2
- **SK** (Sự kiện, hội nghị (workshop, phản biện, gặp doanh nghiệp)): Z6, Z3, Z7, Z4*, Z1, B2, A1, A3*, A5*, A7, A9, A10, C1, C2, G1, G3*, G4  · tuỳ chọn: Z5, Z2, A4, A6, A8, E1, E3, G2
- **NT** (Hoạt động ngoài trường, trại hè, khoá ngắn, tình nguyện): Z6, Z3, Z7, Z4*, B2, A3, A4, A6, A9, E3, G1, G2, G3  · tuỳ chọn: Z5, Z1, A1, A5, A8, A11, A12, C1, C2, G4
- **YT** (Y tế (học viên thực hành, luân khoa, nội trú)): Z6, Z3, Z7, Z4*, Z1, B2, A3, A5, A6, A11, E2, E3, G1*, G2  · tuỳ chọn: Z5, Z2, B1, A1, A2, A4, A7, A8, A9, A10, A12, C1, C3, E1, G3
- **VL** (Nền tảng việc làm tự do, crowdsourcing): Z6, Z3, Z7, Z4, Z5, Z2, Z1, B1, B2, A1, A3*, B3, C1, E1, E3, G1*, G3*, G4  · tuỳ chọn: A4, A5, A7, C3, E2, G2, G5
- **KT** (Kỹ thuật – sản xuất (kỹ sư vào dự án, tác vụ vào máy)): Z6, Z3, Z7, Z4*, Z2, Z1, B1, B2, A1, A3, A5, A7, B3, C1, G1, G3*, G4  · tuỳ chọn: Z5, A6, A9, A12, C2, E1, E3, G2
- **HP** (Phân bổ học phần, môn tự chọn): Z6, Z3, Z7, Z4*, Z1, B2, A3*, A5, A6, A8, A9, C1, C2, G1, G2, G3*, G4  · tuỳ chọn: Z5, Z2, A1, A4, A12, C3, E1, E3
- **TS** (Tuyển sinh cấp trường (lớp 6, lớp 10, trường tư, chọn ngành)): Z6, Z3, Z7, Z4, Z5, Z2, Z1, B1, B2, A1, A2, A3, A4, A5, C1, C3, E1, E2, E3, G1*, G2  · tuỳ chọn: A7, A9, C2, G3
- **NS** (Nhân sự nội bộ (tân tuyển, thực tập, luân chuyển, giáo viên)): Z6, Z3, Z7, Z4*, Z1, B1, B2, A1, A2, A3*, A4, A5, C1, C3, E1, E2, E3, G1*, G2, G3  · tuỳ chọn: Z5, A8, A9, A10, B3
- **LG** (Logistics – vận tải (đơn hàng cho xe, tài xế cho tuyến)): Z6, Z3, Z7, Z4, Z5, Z2, Z1, B1, B2, A1, A3, A9, A12, B3, C1, E1, E3, G1*, G3*, G4, G5  · tuỳ chọn: A5, A7, C2, G2
- **TC** (Tài chính – ngân hàng (chia khách hàng, hồ sơ thẩm định)): Z6, Z3, Z7, Z4*, Z1, B1, B2, A1, A2, A3, A5*, A10, A12, B3, C1, C3, E1, E2, E3, G1, G2, G3, G4  · tuỳ chọn: Z5, Z2, A7

`*` = mục tiền đề (ngành không đánh dấu R nhưng mục khác cần).
