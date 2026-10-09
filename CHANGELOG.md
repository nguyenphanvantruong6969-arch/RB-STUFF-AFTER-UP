# CHANGELOG

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)

- `exp_resume.kiem_tien_de`: nhận số bốc thăm kiểu số bất kỳ (numpy.int64...), chỉ thiếu / None mới là lỗi; báo rõ CLB có sức chứa mới không hợp lệ (giảm dưới suất dự trữ) thay vì lỗi chung chung về sau.
- `_chung.nap_rb`: thư mục — luôn nạp cả `i18n_errors` từ cùng thư mục (kể cả khi mô-đun chính đã có sẵn); bản build — nạp lại cùng tệp .exe trả bản đã nạp thay vì từ chối; nạp hỏng thì gỡ mô-đun dở dang khỏi sys.modules.
- Test (154 ca): test khoá phá hoà nay phân biệt được bản đúng với bản cũ (thêm ca tách cặp trùng giữ thứ tự, bản chỉ so số bốc thăm từ chối nhầm; đã thử đột biến); bỏ test đo giây, thay bằng danh sách cấm tra `in` (bảo đảm không quét danh sách); dùng chung bộ nạp `_chung.nap_canh`.
- Bác: (1) `verify_stability_nhanh` import `i18n_errors` theo tên — giống hệt bản gốc `verify_stability`, và `nap_rb` bảo đảm cùng thư mục; (2) sửa cách phân xử em không có thứ hạng trong `club_choice_function` — mã sản phẩm, cần mục trong sổ (đã ghi ở DOI_CHIEU_KHO_MA.md).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)

- `exp_resume.kiem_tien_de`: so thứ tự bốc thăm bằng đúng khoá phá hoà của `compute_club_priority` (số bốc thăm, mã em) — số trùng trước đây lọt kiểm; thiếu hoặc rỗng số bốc thăm báo ValueError rõ thay vì KeyError/TypeError.
- `de_xuat_verify_nhanh.py`: luôn gọi hàm đủ tư cách cho ứng viên như bản gốc (trước đây bỏ qua khi CLB còn chỗ, nên lỗi của hàm đó không lộ ra giống bản gốc).
- `_chung.nap_rb`: từ chối cả `i18n_errors` nạp từ nơi khác; bỏ đường dẫn khỏi sys.path sau khi nạp; bản build từ chối khi tiến trình đã nạp mô-đun, và `__file__` của mô-đun nạp từ .exe là đường dẫn ảo trong tệp .exe (trước đây là đường dẫn tương đối, có thể trùng tệp của kho).
- Test: 150 ca; bỏ ngưỡng giây tuyệt đối (chập chờn trên CI), thay bằng tỉ lệ thời gian khi dữ liệu gấp 8 lần.
- Bác: gộp đoạn mồi nạp `_chung` (5 dòng) trong hai kịch bản — không gộp được mà không sửa sys.path (chính là lỗi đã sửa ở vòng trước).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)

- `exp_resume.py` (G1), sửa tận gốc: `resume_da(res0, cu, moi, new_ids)` nhận cả dữ liệu cũ lẫn mới; `kiem_tien_de` (O(dữ liệu), dùng tập hợp) kiểm và TỪ CHỐI với thông báo rõ mọi thay đổi không phải "thêm ràng buộc": em nộp lại / mã trùng, đóng CLB, tăng sức chứa, đổi dự trữ, đổi nguyện vọng / điểm / nhóm / thứ tự bốc thăm của em cũ, em cũ xếp CLB mới mở, apps thiếu nguyện vọng (kể cả res0 lập từ apps thiếu). Hỗ trợ thêm GIẢM sức chứa (chọn lại trên tập đang giữ). Em mới không có dòng nguyện vọng không còn KeyError. `resume_test` đo riêng thời gian kiểm tiền đề.
- `de_xuat_verify_nhanh.py` (Z4): chữ ký trùng `verify_stability` (bỏ tham số `err`, dùng `err` của i18n_errors); chuẩn bị từng CLB một cách lười (chỉ CLB thật sự được xét, như bản gốc); kiểm sức chứa bằng `club_choice_function` của mô-đun đã nạp với ứng viên thật.
- `_chung.py`: `nap_canh` là bản duy nhất của bộ nạp theo đường dẫn; `nap_rb(thu_muc)` báo lỗi khi tiến trình đã nạp bản từ nơi khác (trước đây lặng lẽ trả bản cũ); bản build: báo rõ khi lệch phiên bản Python, đọc được mục lục PYZ dạng dict của PyInstaller cũ.
- `kiem_verify_nhanh.py`: `is not None` khi chọn em để hoán đổi.
- Test: 145 ca (vi sai tiếp tục/chạy lại có giảm sức chứa, CLB mới, em không nguyện vọng; một ca từ chối cho mỗi vi phạm; kiểm tiền đề tuyến tính; bản nhanh không đọc CLB không ai xét; `nap_rb` cùng thư mục / khác thư mục / tiến trình mới).
- Kiểm vi sai ngoài bộ test: `resume_da` = `run_rbda` trên 20.000 thể hiện ngẫu nhiên (có giảm sức chứa, CLB mới); bản nhanh = bản gốc trên 60.000 thể hiện (gồm 3.195 ca sức chứa sai, cùng thông báo lỗi).
- Chưa sửa (mã sản phẩm, cần mục trong sổ): `club_choice_function` xếp em không có thứ hạng bằng `len(rank)` rồi theo thứ tự pool — ghi trong DOI_CHIEU_KHO_MA.md.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)

- `de_xuat_verify_nhanh.py` (Z4): không còn nhập `loi_suc_chua` theo tên và không chép thông báo lỗi; kiểm sức chứa bằng chính `club_choice_function` của mô-đun đã nạp (kho mã hay bản build cũ), nên cùng luật, cùng thông báo.
- `exp_resume.py` (G1): `is not None` ở mọi chỗ (trước đây `held` và `nxt` lệch nhau với CLB có mã rỗng); bỏ ID CLB không tồn tại khỏi tập tính lại thứ hạng; CLB mới sau lần chạy cũ không còn KeyError; em không có dòng nguyện vọng dùng `prefs.get(s, [])` như `run_rbda`.
- `kiem_verify_nhanh.py`, `exp_resume.py`: nạp `_chung` và bản nhanh theo đường dẫn (không sửa sys.path); phần chạy của `kiem_verify_nhanh.py` đặt trong `main()`.
- `tests/test_tham_khao_verify_nhanh.py`: 85 ca (86 sau rà soát bổ sung). Thêm biến đổi kết quả làm CLB thừa/thiếu người, bỏ chỗ; ca thật "em trong nguyện vọng nhưng không trong apps"; dự trữ 0 / một phần / bằng sức chứa; so thông báo lỗi; em mới có diện dự trữ và điểm thi, CLB mới, nguyện vọng trỏ CLB không có, em không có nguyện vọng; kiểm `nap_rb` và `gen`; kiểm phép so sánh không rỗng. Nạp kịch bản theo đường dẫn. 16 ca thất bại với bản `exp_resume.py` trước sửa.
- Rà soát bổ sung (Sonnet, kiểm vi sai ngẫu nhiên): bản nhanh khớp bản gốc trên 600.000 thể hiện (kể cả thứ hạng trùng, sức chứa sai); `resume_da` lệch chạy lại khi em có trong nguyện vọng nhưng không trong apps (em không thứ hạng trùng nhau, phân xử theo thứ tự pool). Đường thật không có ca này (`hop_ung_vien`); `resume_da` nay ghi rõ tiền đề và từ chối dữ liệu như vậy; thêm test phản ví dụ (86 ca).
- Tài liệu: mã tiến độ `RS` (không có trong sổ) đổi thành `GĐ0`; số test trong CLAUDE.md đếm lại; sửa hai dòng mâu thuẫn / lỗi thời trong `DOI_CHIEU_KHO_MA.md`.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)

- `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản đề xuất cho Z4): khớp `club_choice_function` ở mọi ca biên — em đang giữ chỗ không có trong `base_rank` xếp cuối (`rank.get(s, len(rank))`) thay vì ném KeyError; thứ hạng trùng dùng `bisect_right` (khớp sắp xếp ổn định; test mới tìm ra lệch khi dùng `bisect_left`); kiểm `loi_suc_chua` và ném cùng ValueError; `is not None` khi gom em đang giữ; gọi hàm đủ tư cách một lần cho mỗi em.
- `exp_resume.py` (nguyên mẫu G1): bỏ qua nguyện vọng trỏ tới CLB không tồn tại như `run_rbda`; nhập được từ test (phần chạy đặt trong `__main__`, numpy chỉ nạp khi đo).
- Mới `docs/ke_hoach/tham_khao/_chung.py`: một bản duy nhất của bộ nạp `nap_rb` (báo lỗi rõ khi tệp không phải PyInstaller) và bộ sinh `gen`; bỏ bản sao và import thừa trong hai kịch bản.
- `pyproject.toml`: bỏ loại trừ ruff cho `docs/ke_hoach/tham_khao` (đã sửa lỗi lint); giữ loại `docs/*` khỏi đo phủ.
- Test mới `tests/test_tham_khao_verify_nhanh.py` (43 ca, không cần numpy).
- `CLAUDE.md`: cập nhật bản đồ mã theo kho (api.py L784–1364, rollback L1107–1119, `_BANG_RANG_BUOC`, Sổ nhập), số test, thời gian chạy, lệnh verify cần numpy, `CHANGELOG.md`.
- Chạy lại: `kiem_verify_nhanh.py` → `TAT_CA_GIONG_NHAU True` (7/7); `exp_resume.py` → 38/38 khớp chạy lại.

## 2026-10-08 — Giai đoạn 0 (chỉ đọc và đo)

- Môi trường: `.venv` (Python 3.11.17) cài `requirements-dev.txt` và `numpy`; `matching` 1.4.3 cài thêm chỉ để so sánh sau này (Q5), không thêm vào requirements.
- Gói kế hoạch đã có trước đó (commit 7c4f423): `CLAUDE.md`, `docs/ke_hoach/*`, và các loại trừ trong `pyproject.toml` (ruff: `docs/ke_hoach/tham_khao`; phủ: `docs/*`). Giai đoạn 0 không sửa các tệp này.
- Thêm `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`: đối chiếu 33 mục của sổ với kho, kết quả đo và trả lời câu hỏi mở mục 9 của `BOI_CANH_DU_AN.md`.
- Cập nhật `docs/ke_hoach/TIEN_DO.md`: GĐ0 xong; Z1–Z7 đánh dấu chưa.
- Không sửa mã sản phẩm (`.py`, `.js`, `.html`, `.css`).

Số đo chính (dữ liệu mô phỏng):
- Bộ test: 1.287 ca đạt, 0 hỏng, 0 bỏ qua, 0 lỗi; phủ 91,06 %; thời gian 1.352 s. Ruff: sạch.
- Verify nhanh: khớp hoàn toàn ở 7/7 cấu hình (`TAT_CA_GIONG_NHAU True`); 10.000 HS: 6,53 s so với 0,042 s.
- 5.000 HS, 10 CLB: `run_rbda` 0,18 s; `verify_stability` 2,09 s (≈92 % thời gian kiểm tra); 0 cặp phá vỡ.
- Tiếp tục DA từ trạng thái cũ: khớp chạy lại 38/38 lần.
- Sổ 33 mục: 29 đúng, 3 khác (Z1, Z4, Z6), 1 sai (C1).
