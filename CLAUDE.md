# CLAUDE.md — Chương trình phân bổ RB-DA (kiosk phân bổ câu lạc bộ)

> Tệp này nạp vào mọi phiên. Bối cảnh đầy đủ ở `docs/ke_hoach/` — **đọc trước khi sửa mã** (xem mục "Tài liệu cần đọc").
> Trả lời người dùng bằng **tiếng Việt**. Tên hàm, tên biến giữ nguyên như trong mã.

## Dự án là gì
- Phần mềm Windows (kiosk, chạy ngoại tuyến) phân bổ ~800 học sinh vào ~20 câu lạc bộ ở một trường phổ thông, là đề tài nghiên cứu khoa học kỹ thuật của một học sinh.
- Thuật toán: **RB-DA** = Deferred Acceptance (Gale–Shapley, học sinh đề nghị) + **dự trữ mềm** hai lượt (Kominers & Sönmez 2016) + **bốc thăm một lần dùng chung** (STB, single tie-breaking) + ưu tiên hai tầng (Tầng 1 có điểm thi: −điểm rồi STB; Tầng 2 không thi: STB).
- Ngăn xếp: Python 3.11 + SQLite (`app.db`), giao diện HTML/JS chạy trong pywebview (WebView2), có chế độ dự phòng mở bằng trình duyệt (`browser_host.py`). Đóng gói bằng PyInstaller qua GitHub Actions (workflow *Build Windows executable (rbda-kiosk)*; build tay: `build_windows.bat`).
- **Mục tiêu hiện tại của chủ dự án:** tổng quát hoá chương trình để bán cho các ngành khác ngoài CLB trường học (12 ngành đã đánh giá), và thêm khả năng xử lý thay đổi theo thời gian (em đến muộn, rút lui). Mô hình kinh doanh để sau.

## Bản đồ mã (định vị theo TÊN HÀM; số dòng đã đối chiếu với kho ngày 08/10/2026 — bảng đầy đủ ở `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`)
| Tệp | Vai trò | Hàm then chốt |
|---|---|---|
| `rbda_priority_pipeline.py` (~2.187 dòng) | Thuật toán, schema, I/O SQLite | `compute_club_priority` L123–191 · `club_choice_function` L236–292 · `run_rbda` L315–452 · `verify_stability` L456–524 · `run_rbda_nhieu_buoi` L877–985 · `generate_stb_lottery`, `chen_stb_cho_hoc_sinh_moi` L1086–1182 · `_BANG_RANG_BUOC` L1250, `DEFAULT_SCHEMA` L1290 · `di_tru_schema` L1568–1666 · `default_reserve_eligible_fn` L1709–1720 |
| `api.py` (~1.364 dòng) | `PipelineAPI`: pipeline 5 bước | `_run_pipeline_da_khoa` L784–1364 (rollback khi có cặp phá vỡ: L1107–1119) · `get_data_health_report` L236 |
| `api_nhap.py`, `api_xuat.py`, `api_quan_ly.py`, `api_bao_cao.py`, `api_cham_diem.py`, `api_chung.py` | Nhập/xuất CSV-Excel, quản lý, báo cáo, chấm điểm mù, tiện ích | số dòng trong sổ đã trôi (api_nhap +~230, api_xuat +~250): xem `docs/ke_hoach/DOI_CHIEU_KHO_MA.md` |
| `so_nhap.py`, `so_excel.py` | Sổ nhập CLB: MỘT tệp Excel thay ba tệp nạp; nguồn duy nhất của định dạng (skill trong `.claude/skills/` cũng dùng) | `import_so_nhap`, `xem_truoc_so_nhap` (api_nhap.py) |
| `i18n_errors.py` → `tao_i18n_js.py` → `i18n_loi.js` | Thông báo lỗi song ngữ, **một nguồn** | `err`, `phan_hoi_ok`, `phan_hoi_loi` |
| `browser_host.py`, `recovery.py`, `chan_doan.py`, `main.py` | Máy chủ dự phòng 127.0.0.1, phục hồi, log, điểm vào | |
| `index.html`, `js/00…08_*.js`, `i18n.js`, `style.css` | Giao diện; gọi backend qua `window.pywebview.api.*`, trả `{ok, data, errors}` | |
| `tests/` | 89 tệp `test_*.py`, 1.515 ca (`pytest --collect-only`, 10/10/2026) | `test_pipeline_core.py`, `test_nhieu_buoi.py::TestTrungKhit`, `test_toi_uu_on_dinh.py`, `test_boc_tham.py`, … |
| `du_lieu_test/`, `mau_csv/`, `docs/`, `BAN_GIAO.md` | Bộ dữ liệu mô phỏng, script đo, mẫu nhập, tài liệu cơ chế, nhật ký 25 lỗi đã sửa | |

## Lệnh
- Chạy test: `python -m pytest -q` trong venv của dự án (tài liệu ghi `./.venv/bin/python -m pytest -q`; trên Windows: `.venv\Scripts\python -m pytest -q`). Toàn bộ ~22 phút trên máy 4 nhân kèm test giao diện Chromium (BAN_GIAO.md ghi ~3,5 phút; chưa giải thích được, xem `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`). Lint: `ruff check .`; CI đòi phủ ≥ 85 %.
- Sinh lại thông báo lỗi JS sau khi sửa `i18n_errors.py`: `python tao_i18n_js.py`.
- Kiểm verify nhanh (tham khảo): `pip install numpy` (chỉ cho kịch bản tham khảo, KHÔNG thêm vào requirements) rồi `python docs/ke_hoach/tham_khao/kiem_verify_nhanh.py <thư mục chứa rbda_priority_pipeline.py>`. Test `tests/test_tham_khao_verify_nhanh.py` (không cần numpy) canh `verify_stability_nhanh`, `exp_resume.resume_da` / `kiem_tien_de`, `_chung.nap_rb` (thư mục: nạp thẳng tệp .py, cùng bản, bản khác, tiến trình mới, mô-đun anh em lạ; tệp không phải PyInstaller); `_chung.gen` chỉ được kiểm khi có numpy; đường nạp `.exe` được kiểm bằng một tệp PyInstaller tối thiểu dựng trong test (không có bản build thật trong kho).

## Bất biến — KHÔNG được phá
1. Cấu hình mặc định phải cho kết quả TRÙNG KHÍT với trước khi sửa (cùng dữ liệu, cùng seed): so từng dòng match_results trên 3 bộ dữ liệu × 20 seed.
2. compute_club_priority KHÔNG được nhận thứ hạng nguyện vọng hay kết cục buổi trước (ràng buộc chống nội sinh); thêm tiêu chí mới cũng không được đọc chúng.
3. Cơ chế số bốc thăm (STB): khoá sau lần chạy đầu, seed khoá cùng bộ số, sinh bằng crc32 (không dùng hash()), em đến muộn chèn ngẫu nhiên đều nhưng giữ thứ tự tương đối của em cũ.
4. run_history không bao giờ bị ghi đè hay xoá; mọi lần chạy ghi thêm một dòng.
5. Pipeline giữ nguyên thứ tự: sao lưu → kiểm dữ liệu → khoá seed/STB → giải → sanity/verify → ghi trong MỘT giao dịch → xuất; lỗi thì rollback.
6. Hợp đồng giữa giao diện và backend là {ok, data, errors} với errors = [{code, params}]; thông báo lỗi chỉ có một nguồn (i18n_errors.py → tao_i18n_js.py).
7. Hợp đồng cột CSV (club_id, student_id, test_club_k, score_k, pref_k, <buoi>_pref_k) chỉ đổi khi mục tương ứng ghi rõ; di_tru_schema phải chạy lặp an toàn và có sao lưu.
8. Mọi hàm lựa chọn mới phải qua test thay thế được (substitutability) và luật tổng cầu trước khi đăng ký; nếu không thoả, phải báo rõ 'không bảo đảm ổn định'.

## Quy tắc làm việc
1. Mỗi thay đổi gắn với **một mã mục** trong sổ đăng ký (Z1…G5). Không làm việc ngoài sổ khi chưa hỏi.
2. **Test trước**: viết test thất bại theo trường `kiem_nhan`, rồi sửa tối thiểu, rồi chạy toàn bộ test.
3. Tham số mới phải có **mặc định = hành vi cũ**; cấu hình mặc định phải cho kết quả **trùng khít** (so từng dòng `match_results`, 3 bộ dữ liệu × 20 seed).
4. Không xoá các chế độ đối chứng (`stb_tuan`, `stb_co_bu`, A1/A3 trong TN7): script đo trong `du_lieu_test/` cần chúng để tái lập số liệu.
5. Hàm lựa chọn mới phải qua test **thay thế được** và **luật tổng cầu**; không qua thì ghi rõ "không bảo đảm ổn định" và dùng chế độ đo lường (mục A12).
6. Sau mỗi mục: cập nhật `CHANGELOG.md` (mã mục, tệp, test mới) và đánh dấu tiến độ trong `docs/ke_hoach/TIEN_DO.md`.
7. Dừng và hỏi khi: một bất biến xung đột với mục; số dòng/hiện trạng trong sổ lệch hẳn so với kho; cần thêm thư viện; cần đổi hợp đồng cột CSV hay schema ngoài phạm vi mục.

## Liêm chính học thuật (đây là đề tài của học sinh)
- **Mọi số liệu kiểm chứng là dữ liệu MÔ PHỎNG.** Không bao giờ viết như thể là khảo sát thật.
- Các phần **nhận xét, diễn giải, kết luận** trong báo cáo đề tài do **học sinh tự viết** — không soạn hộ những phần đó. Tài liệu vận hành, mã, test thì được.
- Trợ giúp của AI được ghi trong nhật ký AI của dự án; ghi thêm khi làm việc lớn.
- Tên đúng là **Gale–Shapley** (báo cáo gốc có chỗ viết "Sharpley").

## 12 ngành đích (mã dùng trong mọi tệp)
| Mã | Ngành | Mục R riêng | Điểm công sức | Số mục trong kế hoạch |
|---|---|---|---|---|
| `DT` | Phân bổ đề tài, đồ án, người hướng dẫn | 3 | 10 | 7 |
| `KTX` | Ký túc xá, nhà ở sinh viên, nhà ở xã hội | 8 | 20 | 15 |
| `SK` | Sự kiện, hội nghị (workshop, phản biện, gặp doanh nghiệp) | 9 | 22,5 | 17 |
| `NT` | Hoạt động ngoài trường, trại hè, khoá ngắn, tình nguyện | 9 | 23,5 | 13 |
| `YT` | Y tế (học viên thực hành, luân khoa, nội trú) | 8 | 26 | 14 |
| `VL` | Nền tảng việc làm tự do, crowdsourcing | 8 | 28 | 18 |
| `KT` | Kỹ thuật – sản xuất (kỹ sư vào dự án, tác vụ vào máy) | 10 | 29 | 17 |
| `HP` | Phân bổ học phần, môn tự chọn | 10 | 29,5 | 17 |
| `TS` | Tuyển sinh cấp trường (lớp 6, lớp 10, trường tư, chọn ngành) | 13 | 37 | 21 |
| `NS` | Nhân sự nội bộ (tân tuyển, thực tập, luân chuyển, giáo viên) | 13 | 37 | 20 |
| `LG` | Logistics – vận tải (đơn hàng cho xe, tài xế cho tuyến) | 12 | 44 | 21 |
| `TC` | Tài chính – ngân hàng (chia khách hàng, hồ sơ thẩm định) | 17 | 50,5 | 23 |

Thứ tự làm chung khi chuẩn bị nhiều ngành: `Z6 → Z3 → Z7 → Z4 → Z5 → Z2 → Z1 → B1 → B2 → A1 → A2 → A3 → A4 → A5 → A6 → A7 → A8 → A9 → A10 → A11 → A12 → B3 → C1 → C2 → C3 → E1 → E2 → E3 → G1 → G2 → G3 → G4 → G5`

## Tài liệu cần đọc (theo thứ tự)
1. `docs/ke_hoach/BOI_CANH_DU_AN.md` — toàn bộ bối cảnh: lịch sử phân tích, phát hiện, số đo, lý thuyết, câu hỏi mở.
2. `docs/ke_hoach/SO_DANG_KY_33_MUC.md` — 33 mục sửa: hiện trạng, thay đổi, rủi ro, kiểm nhận, áp dụng cho ngành nào.
3. `docs/ke_hoach/ke_hoach_thay_doi.json` — cùng dữ liệu, dạng máy đọc; `nganh[].ke_hoach` là thứ tự làm đã tính phụ thuộc — **làm theo, không tự sắp lại**.
4. Trong kho: `BAN_GIAO.md`, `docs/CO_CHE_THUAT_TOAN.md`, `docs/NGHIEN_CUU_TOI_UU.md`, `docs/GIAI_DAP_BOC_THAM.md`, `docs/KE_HOACH_NHIEU_BUOI.md`, `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md`.
5. Tham khảo: `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản thay `verify_stability`, mục Z4), `kiem_verify_nhanh.py`, `exp_resume.py` (tiếp tục DA từ trạng thái cũ, mục G1).
