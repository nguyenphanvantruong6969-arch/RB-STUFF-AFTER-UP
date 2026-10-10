# Tiến độ

Claude Code cập nhật tệp này sau mỗi mục. Một dòng mỗi mục.

| Mã | Trạng thái (chưa / đang / xong / chặn) | Ngày | Tệp đã sửa | Test mới | Ghi chú |
|---|---|---|---|---|---|
| GĐ0 | xong | 2026-10-10 | CHANGELOG.md, docs/ke_hoach/DOI_CHIEU_KHO_MA.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/tham_khao/*, tests/test_tham_khao_verify_nhanh.py, CLAUDE.md, pyproject.toml | tests/test_tham_khao_verify_nhanh.py (218 ca) | Đọc và đo: 1.287 test đạt, phủ 91,06 %; verify nhanh khớp 7/7; 5.000 HS verify ~92 % thời gian (K=10); sổ 33 mục: 29 đúng, 3 khác, 1 sai. Việc tiếp, ngoài sổ (Truong yêu cầu qua /code-review), chuẩn bị Z4, G1, Z6: các lượt rà soát mã — xem CHANGELOG.md |
| Z6 | chưa | | | | Bộ test và dữ liệu mô phỏng cho từng hàm mới (Giai đoạn 1, thứ tự đầu tiên) |
| Z3 | chưa | | | | Tách _run_pipeline_da_khoa (581 dòng, không phải 573) |
| Z7 | chưa | | | | Cổng cắm; lõi không cần Z3, chỉ điểm gọi api.py cần (xem DOI_CHIEU Q6); không nhắm run_full_pipeline |
| Z4 | chưa | | | | Verify nhanh; cần chủ sở hữu cho điều hướng bản chậm (xem DOI_CHIEU Q6); số đo lại trên máy này |
| Z5 | chưa | | | | Sửa docstring số vòng (bị bác bỏ bởi ket_qua_thu_tai.csv); trần max_rounds theo cận chứng minh được |
| Z2 | chưa | | | | Một nguồn cho giới hạn 10 nguyện vọng / 5 CLB thi (hiện hai bản sao Python và JS) |
| Z1 | chưa | | | | Gói từ vựng giao diện; số đếm trong sổ phải ghi phương pháp |
