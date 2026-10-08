# CHANGELOG

## 2026-10-08 — Sửa theo rà soát mã (/code-review, 10 điểm)

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
