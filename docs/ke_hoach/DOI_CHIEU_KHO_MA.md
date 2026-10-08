# Đối chiếu sổ đăng ký 33 mục với kho mã

- **Ngày:** 2026-10-08 (Giai đoạn 0: chỉ đọc và đo, không sửa mã sản phẩm)
- **Kho:** rbda-kiosk, nhánh `main` @ `52981bb` (snapshot nhập vào nhánh `claude/upbeat-ride-vsdibu`).
- **Sổ đối chiếu:** `docs/ke_hoach/SO_DANG_KY_33_MUC.md`, lập từ bản build `.exe`, nên số dòng lệch so với kho là điều dự kiến.
- **Dữ liệu:** mọi số đo trong tài liệu này là **dữ liệu MÔ PHỎNG** do máy sinh theo tham số, không phải khảo sát học sinh thật.
- **Môi trường đo:** máy 4 nhân, Python 3.11.17 (venv `.venv`), pytest 9.1.1, pytest-cov 7.1.0, ruff 0.16.10, numpy 2.4.6 (chỉ cho tệp tham khảo, không phải phụ thuộc sản phẩm), Chromium có sẵn qua `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.

---

## Kết quả đo giai đoạn 0

### Bước 3: bộ test và lint

| Chỉ số | Kết quả |
|---|---|
| Lệnh | `xvfb-run -a .venv/bin/python -m pytest -q -rs --cov --cov-report=term` |
| Đạt / hỏng / bỏ qua / lỗi | **1.287 đạt** / 0 hỏng / 0 bỏ qua / 0 lỗi |
| Phủ mã sản phẩm | **91,06 %** (5.046 lệnh, 451 chưa chạy); ngưỡng 85 % đạt |
| Thời gian (dòng cuối của pytest) | **1.352,45 s (22 phút 32 giây)** |
| Ruff `ruff check .` | **All checks passed** (exit 0) |

- Không có test nào bị bỏ qua, nên không có lý do bỏ qua để liệt kê. Không có test nào hỏng.
- So với các con số có sẵn: gói kế hoạch ghi ~483 ca và ~95 giây; `BAN_GIAO.md` (dòng 28) ghi 1.160 ca và ~3,5 phút; `grep -c "def test_"` cho 1.078 định nghĩa trong 91 tệp. Pytest thu thập 1.287 ca vì nhiều test được tham số hoá.
- Thời gian thực tế dài gấp khoảng 14 lần con số của gói. Chưa tách thời gian theo tệp; phần lớn có thể là các test giao diện Playwright (Chromium headless).
- Đầu ra đầy đủ: `scratchpad/stage0/pytest.txt`.
- **Lưu ý:** 22 phút 32 giây chưa giải thích được (chưa chạy `--durations`); có thể do máy 4 nhân và các test giao diện Chromium. Đo lại bằng `pytest --durations=15` làm mốc cho Giai đoạn 1 trước khi kết luận là chậm đi.

### Bước 4: kiểm tương đương verify nhanh

`kiem_verify_nhanh.py` chạy với `-I` không lỗi, nên không phải chạy lại không có `-I`.

| Cấu hình | Số cặp phá vỡ (gốc / nhanh) | Giống hệt | t gốc (s) | t nhanh (s) |
|---|---|---|---|---|
| Kết quả thật, 2.000 HS, 20 CLB, tỉ lệ chỗ 1,0 | 0 / 0 | có | 0,20 | 0,006 |
| Kết quả thật, 5.000 HS | 0 / 0 | có | 1,42 | 0,038 |
| Kết quả thật, 10.000 HS | 0 / 0 | có | 6,53 | 0,042 |
| Hoán đổi, 1.500 HS, 10 CLB, chỗ 0,6, 200 lần hoán đổi | 8.128 / 8.128 | có | – | – |
| Hoán đổi, 1.500 HS, 15 CLB, chỗ 0,5, 50 lần | 7.278 / 7.278 | có | – | – |
| Hoán đổi, 800 HS, 8 CLB, chỗ 0,7, 300 lần | 3.422 / 3.422 | có | – | – |
| Hoán đổi, 1.200 HS, 12 CLB, chỗ 0,8, 150 lần | 4.282 / 4.282 | có | – | – |

- **`TAT_CA_GIONG_NHAU True`** cho cả 7 cấu hình. Tổng cặp phá vỡ trong 4 kết quả hoán đổi là 23.110, khớp gói.
- Thời gian 10.000 HS: gốc 6,53 s, nhanh 0,042 s. Gói ghi 22,4 s và 0,09 s. Máy khác, nên lệch là chấp nhận được, nhưng tỉ lệ nhanh hơn của bản đề xuất vẫn lớn (≈155 lần trên máy này so với ≈250 lần của gói).
- Đầu ra: `scratchpad/stage0/verify.txt`.

### Bước 5: tách thời gian một lần chạy 5.000 học sinh

Dữ liệu sinh bằng `sinh_csv()` của `du_lieu_test/thu_tai/chay_thu_tai.py` (import, không sửa), nạp qua `PipelineAPI.import_csv_auto`, chạy `run_pipeline` một lần để khoá STB, rồi đọc lại bằng `load_from_sqlite`. Tham số: 5.000 HS, 10 nguyện vọng, tỉ lệ chỗ 1,00, chia chỉ tiêu đều (`chia_deu`). Các cột là **trung vị của 3 lần lặp**, đơn vị giây.

| Số CLB (K) | `run_rbda` | `sanity_check_result` | `verify_stability` | `verify_stability_nhanh` | `run_pipeline` (cả đường) | Số vòng | Em được xếp | Cặp phá vỡ |
|---|---|---|---|---|---|---|---|---|
| 10 | 0,184 | 0,004 | 2,090 | 0,019 | 3,138 | 31 | 5.000 | 0 |
| 20 | 0,178 | 0,005 | 1,543 | 0,026 | 2,091 | 30 | 4.926 | 0 |
| 100 | 0,168 | 0,004 | 0,468 | 0,028 | 1,355 | 20 | 4.682 | 0 |

- Nạp CSV (ba tệp): 0,85 s (K=10), 0,90 s (K=20), 1,17 s (K=100).
- `sanity_check_result` trả 0 vấn đề ở cả ba cấu hình. Kết quả của `verify_stability` và của bản nhanh giống nhau ở mọi lần lặp.
- Tỉ lệ `verify_stability` / `run_rbda`: 11,4 lần (K=10), 8,7 lần (K=20), 2,8 lần (K=100).
- Đầu ra: `scratchpad/stage0/do_5000.txt`; mã: `scratchpad/stage0/do_5000.py`.
- **Lưu ý:** script gọi `run_rbda` trực tiếp trên `stb_number` đã lưu. Đây là phép **đo thời gian**, không đối chiếu kết quả phân bổ với pipeline (pipeline dùng số bốc thăm theo buổi `stb_ngay`).

### Bước 6: thí nghiệm tiếp tục DA từ trạng thái cũ (G1)

| Cấu hình (HS / CLB / tỉ lệ chỗ / em mới) | Giống hệt chạy lại | Chạy lại (ms, TB) | Tiếp tục (ms, TB) | Tỉ lệ nhanh |
|---|---|---|---|---|
| 2.000 / 20 / 1,0 / 1 | **15/15** | 40,5 | 11,28 | 3,6 |
| 2.000 / 20 / 0,8 / 5 | **10/10** | 55,1 | 18,38 | 3,0 |
| 5.000 / 20 / 1,0 / 1 | **8/8** | 165,6 | 41,34 | 4,0 |
| 5.000 / 20 / 0,9 / 20 | **5/5** | 165,5 | 69,7 | 2,4 |

- Tổng: **38/38** lần khớp với chạy lại toàn bộ. Gói ghi 15/15, 10/10, 8/8, 5/5 và "nhanh 1,8–3,9 lần"; đo ở đây cho 2,4–4,0 lần.
- Thí nghiệm này chỉ kiểm tra tiếp tục DA cho ra cùng kết quả với chạy lại toàn bộ. Nó **không** đo việc em cũ bị đổi chỗ (xem Q3).
- Đầu ra: `scratchpad/stage0/resume.txt`.

---

## Bảng đối chiếu

**Quy ước.** Cột "Hiện trạng" đánh giá các khẳng định về hành vi, tên hàm và số liệu trong mục "Hiện trạng" của sổ:
- **đúng**: khẳng định còn đúng. Lệch dòng nhỏ được ghi ở "Ghi chú" và không làm đổi nhãn.
- **khác**: ý chính đúng nhưng số đo, tên hoặc chi tiết lệch.
- **sai**: một khẳng định không còn đúng hoặc không đúng với kho.

Dòng theo sổ là số trong `SO_DANG_KY_33_MUC.md`. Dòng thực tế là vị trí tìm thấy trong kho (`grep -n`). Mọi hàm đều được định vị theo tên.

| Mã mục | Hàm | Dòng theo sổ | Dòng thực tế | Hiện trạng (đúng/sai/khác) | Ghi chú |
|---|---|---|---|---|---|
| Z1 | UI_STRINGS, MESSAGES, DEFAULT_SCHEMA | schema L1251–1290; giao diện: toàn bộ | DEFAULT_SCHEMA L1290; `_BANG_RANG_BUOC` L1250; MESSAGES `i18n_errors.py` L20; `UI_STRINGS` có trong `i18n.js` L21 (bảng chữ giao diện vi/en, hàm `t` L859) | khác | Các số đếm không tái lập được: chữ 'CLB' 202 và 'học sinh' 138 trong index.html + i18n.js + js/*.js (sổ: 252 / 231; đếm không phân biệt hoa thường: 305 / 156 gồm cả tên biến); MESSAGES 174 mã, 99 nhắc CLB/học sinh (sổ: 84 / 340); 23 trên 436 hàm có club/student/hoc_sinh trong tên (sổ: 76 / 464). Sổ cần ghi phương pháp đếm. Số dòng SQL nhắc club/student: 166 / 239 dòng (sổ: 144 / 191 chuỗi, đơn vị khác). |
| Z2 | TRAN_NGUYEN_VONG_MOI_BUOI, TRAN_CLB_THI_MOI_BUOI | rbda L91, L96; 05_quan_ly.js L33–34; 04_nhap_tai_cho.js L397/441; api_quan_ly L430–476 | rbda L91, L96; 05_quan_ly.js L33–34; 04_nhap_tai_cho.js L397, L401, L441, L445; api_quan_ly `submit_preferences` L435 (import L19–20) | đúng | Hai bản sao (Python và JS) vẫn tồn tại. Chú thích 'Microsoft Forms' ở `submit_preferences` xác nhận nguồn con số 10. |
| Z3 | PipelineAPI._run_pipeline_da_khoa | api.py L744–1316 (573 dòng) | api.py **L784–1364 (581 dòng, là hàm cuối của tệp)**; sao lưu L864; kiểm dữ liệu L885; chọn buổi L899–919; khoá STB L989–1075; `run_rbda_nhieu_buoi` L1094; sanity/verify/rollback L1103–1119; ghi kết quả L1126–1238; run_history L1283; xuất CSV L1304–1313 | đúng | Các bước và thứ tự khoá/rollback đúng như mô tả. Dòng và độ dài trong sổ đã trôi (573 → 581). Docstring `_ket_noi_ghi` (L681) có 'để nguyên' đúng như sổ. |
| Z4 | verify_stability | rbda L456–524 (gọi club_choice_function L511) | def L456; gọi `club_choice_function` L511 ✓; thân kết thúc ~L524 | khác | Số đo không tái lập đúng trên máy này: 10.000 HS verify 6,53 s (sổ: 22–24 s; chưa đo `run_rbda` ở 10.000). Ở 5.000 HS, tỉ lệ verify / run_rbda là 11,4× (K=10), 8,7× (K=20), 2,8× (K=100), không phải "≈20×". Bản nhanh khớp hoàn toàn ở 7/7 cấu hình (bước 4). |
| Z5 | run_rbda (max_rounds) | rbda L315, L372, L429–434 | def L315; tham số `max_rounds` L323; vòng lặp L372; `raise` L428–434 | đúng | Docstring (L334–342) nói số vòng 'đúng bằng độ dài danh sách nguyện vọng dài nhất' và **bị bác bỏ bởi dữ liệu của chính dự án**: với 3 / 5 / 10 nguyện vọng, số vòng lớn nhất là 37 / 84 / 227 (204 lần, `du_lieu_test/thu_tai/ket_qua_thu_tai.csv`; trung vị 9 / 14 / 18). Sổ đúng; lỗi nằm ở docstring trong mã. |
| Z6 | TestTrungKhit; chay_thu_tai.py | tests/ (không có trong gói); du_lieu_test/; du_lieu_test/thu_tai/ | `tests/test_nhieu_buoi.py` L156 `class TestTrungKhit` (có); 91 tệp test; 1.078 `def test_`; 1.287 ca chạy | khác | Sổ ghi '37 tệp, 483 ca' (theo CLAUDE.md của gói): lỗi thời. Khẳng định 'các bộ sinh dữ liệu chỉ sinh dữ liệu câu lạc bộ' vẫn **đúng** theo nghĩa của sổ: chỉ có dữ liệu miền CLB trường học (học sinh, CLB, nguyện vọng, điểm), chưa có bộ sinh cho ngành nào khác. |
| Z7 | run_rbda, verify_stability, default_reserve_eligible_fn | rbda L357, L404, L511; api.py L1041 | L357, L404, L511 đúng; api.py gọi `default_reserve_eligible_fn` **L1089** (sổ L1041); def L1709 | đúng | Chưa có tham số thay thế (đã kiểm chữ ký). Lệch dòng api.py (+48). Không nên nhắm `run_full_pipeline` (L1961, chỉ dùng để thử nghiệm). |
| A1 | compute_club_priority; hop_ung_vien | rbda L123–191; L1723–1753 | def L123, thân kết thúc L191 ✓; hop_ung_vien L1723–1753 ✓ | đúng | Hai tầng, tầng 1 luôn đứng trước, mỗi cặp một điểm. Chữ ký chỉ có 4 tham số, không nhận thứ hạng nguyện vọng (ràng buộc chống nội sinh còn nguyên). |
| A2 | compute_club_priority; sinh_stb_theo_buoi; generate_stb_lottery; chen_stb_cho_hoc_sinh_moi | rbda L123–191; L757–814; L1086–1109; L1112–1182 | def L123, L757, L1086, L1112 ✓ | đúng | Không có chính sách hoà điểm khác ('tieu_chi_phu', 'nhan_het' đều không có). `CHE_DO_BOC_THAM_MAC_DINH = "stb_ngay"`. Ghi chú cho 'nhan_het': cũng chạm `loi_suc_chua` (L271) và `sanity_check_result` (L2128). |
| A3 | club_choice_function | rbda L236–292; gọi L404, L511 | def L236 ✓; thân kết thúc L298; gọi L404 ✓, L511 ✓ | đúng | Hai lượt (dự trữ rồi phổ thông), một hàm cho mọi CLB. Lệch dòng nhỏ (kết thúc L298). |
| A4 | club_choice_function; schema clubs | rbda L236–292; schema L1251 | L236–298; `clubs` trong `_BANG_RANG_BUOC` L1250 | đúng | Dự trữ mềm và xét trước: đúng (`reserve_held` trước `general_capacity`). Không có tham số `loai_du_tru`, `thu_tu`. |
| A5 | default_reserve_eligible_fn; hop_ung_vien | rbda L1709–1720, L1723–1753; api.py L1041; schema L1251, L1290 | L1709–1720 ✓; L1723–1753 ✓; api.py L1089 | đúng | Đủ tư cách = so chuỗi `reserve_group` (một nhãn mỗi bên). `hop_ung_vien` chỉ hợp tập ứng viên, không lọc ai. |
| A6 | loi_suc_chua; run_rbda_nhieu_buoi | rbda L218–233; L877–985 (vòng gọi L973) | def L218 ✓; def L877 ✓; gọi run_rbda L973–975 ✓ | đúng | Không có `min_capacity` (grep). `loi_suc_chua` được gọi ở rbda L271 và L1058, api_nhap L612, api_quan_ly L79. Schema: `CHECK (capacity > 0)` tại L1254. |
| A7 | MatchResult; run_rbda | rbda L299–311; L315–452 | MatchResult L300–313; run_rbda L315 ✓ | đúng | `assignment` là dict sinh viên → CLB, một CLB mỗi em mỗi buổi. |
| A8 | run_rbda_nhieu_buoi; verify_stability_tuan; cat_du_lieu_theo_buoi | rbda L877–985; L988–1009; L703–737 | L877 ✓; L988 ✓; L703 ✓ | đúng | Docstring L988–996 đúng: không ràng buộc nào nối hai buổi. |
| A9 | gom_theo_buoi; so_thu_trong_tuan; khoa_sap_buoi; nhom_theo_buoi | rbda L99–116, L575–700 (L605, L649, L683); api_bao_cao L159–275 | gom_theo_buoi L99 ✓; so_thu_trong_tuan L605 ✓; khoa_sap_buoi L649 ✓; nhom_theo_buoi L683 ✓; get_tai_theo_buoi L160 | đúng | Nhãn lạ đứng sau theo vần chữ cái (`khoa_sap_buoi` trả `(3, 0, buoi)`). Không có khoảng thời gian chồng lấn. |
| A10 | hop_ung_vien; verify_stability; validate_data_integrity | rbda L1723–1753; L456–524; L1016–1083 | L1723 ✓; L456 ✓; L1016 ✓ | đúng | Không có khái niệm cặp cấm trong mã. |
| A11 | run_rbda; schema preferences | rbda L315–452; schema L1271 | L315 ✓; `preferences` L1271 ✓ | đúng | Mỗi ứng viên xếp hạng độc lập; không có nhóm cặp đôi. |
| A12 | _run_pipeline_da_khoa (rollback) | api.py L1052–1071 | rollback L1110–1119 (`sanity_problems + stability_problems`) | đúng | Không có chế độ 'bao_dam' / 'do_luong' (grep). Lệch dòng. |
| B1 | club_scores.score | schema L1265; api_cham_diem L69–137; api_nhap L996–1194 | `club_scores` L1265 ✓; `score REAL NOT NULL CHECK (score >= 0)` L1268; `submit_club_scores` L69 ✓; api_nhap L996–1194 không còn khớp (`import_test_selection_csv` L1226, `import_preferences_csv` L1041) | đúng | Chỉ một điểm REAL cho mỗi cặp. |
| B2 | DEFAULT_SCHEMA; di_tru_schema | schema L1240–1300; L1568–1666 | DEFAULT_SCHEMA L1290 ✓; di_tru_schema L1568 ✓ | đúng | 6 bảng nghiệp vụ (students, clubs, club_test_selection, club_scores, preferences, match_results) và 5 bảng phụ trợ (run_history, run_meta, stb_lock, ket_qua_truoc, dau_van_tay_chay). |
| B3 | import_preferences_csv | api_nhap L814–994 | def L1041 (sổ ghi L814) | đúng | Không có mô-đun sinh thứ hạng (grep). Lệch dòng. |
| C1 | import_csv_auto; import_clubs_csv; import_preferences_csv; import_test_selection_csv | api_nhap L240–320; L339–425; L814–994; L996–1194 | detect_csv_kind L437; import_csv_auto L483; import_clubs_csv L565; import_preferences_csv L1041; import_test_selection_csv L1226; **mới:** xem_truoc_so_nhap L347, import_so_nhap L364 (dùng so_nhap.py) | sai | Hiện trạng lỗi thời: Sổ nhập một tệp Excel (`so_nhap.py`, hai sheet) đã là đường nhập có giao diện (js/02_van_hanh.js L564–832). Phần 'chưa có kết nối API' vẫn đúng. C1 phải bắt đầu từ `so_nhap.py`. |
| C2 | _export_csv_da_khoa; _xuat_excel; get_thoi_khoa_bieu | api_xuat L825–1080, L81–148; api_bao_cao L226–275 | `_export_csv_da_khoa` L1087 ✓; **`_xuat_excel` không tồn tại** (có `_ghi_so_excel` L92, `_luu_so_excel` L127); get_thoi_khoa_bieu L226 ✓ | đúng | UTF-8 BOM (api_xuat L1292), số kiểu Việt Nam (`_so_vn`), thời khoá biểu dạng bảng đều đúng. Sửa tên hàm trong sổ. |
| C3 | get_phan_bo_nguyen_vong; get_em_chua_co_cho; get_thay_doi_ket_qua | api_bao_cao L368–479; api_xuat L468–541 | get_phan_bo_nguyen_vong L369 ✓; get_em_chua_co_cho L416 ✓; get_thay_doi_ket_qua L679 (sổ ghi L468) | đúng | `rejection_log` và `base_rank` chỉ được dùng trong rbda; chưa có giải trình từng người (grep). |
| E1 | _Handler._authorized; _host_hop_le; serve; connect_db | browser_host L186–208, L535–634; rbda L1416–1441; api.py L78–103 | `_authorized` L186 ✓; `_host_hop_le` L197 ✓; `serve` L535 ✓; `connect_db` L1416 ✓; `PipelineAPI.__init__` L78 ✓ | đúng | Một token, kiểm Host (DNS rebinding). Journal mode DELETE, không WAL (rbda L1385–1386). Ghi chú: browser_host L80–90 đã có danh sách trắng theo đuôi tệp, nên `app.db` không còn được phục vụ; sổ nên ghi điều này. |
| E2 | get_run_history; dau_van_tay_du_lieu | api.py L565–584; rbda L1756–1793 | get_run_history L567 (±2); dau_van_tay_du_lieu L1756 ✓ | đúng | Không có danh tính người chạy hoặc người duyệt (grep). |
| E3 | reset_data; delete_student; export_du_lieu_dau_vao | api_quan_ly L569–638, L519–546; api_xuat L594–809; rbda L1756–1793 | reset_data L574 (sao lưu trước, `_backup_db`); delete_student L524; export_du_lieu_dau_vao L845 | đúng | Không có ghi nhận đồng ý, thời hạn lưu, hay xoá theo hạn (grep). Dòng rbda L1756–1793 trong sổ là dấu vân tay (thuộc E2), không thuộc E3. |
| G1 | run_rbda; MatchResult; chen_stb_cho_hoc_sinh_moi; chi_buoi | rbda L315–452, L299–311, L1112–1182; api.py L858–871, L1013–1027 | run_rbda L315 ✓; MatchResult L300 ✓; chen L1112 ✓; `chi_buoi` là **tham số** của run_rbda_nhieu_buoi (L888) và biến trong api.py (L899–919), **không phải hàm**; khoá STB L989–1075 | đúng | Tiếp tục DA từ trạng thái cũ cho kết quả khớp chạy lại 38/38 (bước 6). Sửa mục 'Hàm: chi_buoi'. |
| G2 | reset_student_entry; delete_student | rbda L315–452; api_quan_ly L495–546 | reset_student_entry L500; delete_student L524 (chặn khi có match_results, L524–545) | đúng | Đúng như mô tả: chỉ chạy lại toàn bộ, chưa có đường rút lui sau khi chạy. |
| G3 | club_choice_function; ket_qua_truoc; get_thay_doi_ket_qua | rbda L236–292, L456–524; api.py L1086–1104; api_xuat L468–541 | ket_qua_truoc ghi tại api.py L1127–1140; get_thay_doi_ket_qua L679 | đúng | Phân loại `moi_duoc_xep` / `mat_cho` / `doi_clb` ✓. Không có cờ 'đã công bố' (grep). |
| G4 | _run_pipeline_da_khoa | api.py L744–1316 | L784–1364 | đúng | Chạy thủ công; xác nhận hai bước (js/02_van_hanh.js L416, L438–443). Không có bộ lập lịch. |
| G5 | — | — | — | đúng | Không có mã (đúng như sổ: ngoài phạm vi sửa mã). |

**Tổng hợp:** 33 mục → **29 đúng**, **3 khác** (Z1, Z4, Z6), **1 sai** (C1). Mọi mục đều có dòng trôi; dòng trôi nặng nhất ở api_nhap.py, api_xuat.py và api.py (xem Q1).

---

## Trả lời câu hỏi mở (mục 9 BOI_CANH_DU_AN.md)

**Q1. Số dòng và hiện trạng trong sổ còn đúng với kho không?**
- rbda_priority_pipeline.py: 2.187 dòng; cả 24 dòng định nghĩa hàm trong gói khớp đúng, và các điểm gọi L357, L404, L511 cũng khớp.
- Các tệp khác đã trôi: api.py 1.364 dòng (`_run_pipeline_da_khoa` L784–1364, +40 đến +48 dòng); api_nhap.py 1.424 dòng (+~230); api_xuat.py (+210 đến +260); api_quan_ly.py (+5).
- Hiện trạng: 29 đúng, 3 khác, 1 sai (bảng trên). Lệch nhẹ (khác): Z1 (số đếm không tái lập được), Z4 (số đo tốc độ trên máy này), Z6 (số test lỗi thời). Sai: C1 (thiếu Sổ nhập `so_nhap.py`).

**Q2. Con số 7,65 s ở 5.000 HS chia cho từng bước bao nhiêu?**
- Không tái lập được 7,65 s. Trên máy này, 5.000 HS × 10 CLB (chia đều, 10 nguyện vọng) cho `run_rbda` 0,184 s, `sanity_check_result` 0,004 s, `verify_stability` 2,090 s; cả đường `run_pipeline` 3,138 s.
- Tỉ trọng: `verify_stability` chiếm ~92 % trong tổng `run_rbda + sanity + verify` ở K=10, ~89 % ở K=20 và ~73 % ở K=100. Vì vậy phần lớn thời gian thực sự là kiểm chứng ổn định, đúng với hướng của gói.
- Con số 7,65 s có thể đến từ cấu hình hoặc máy khác (chưa rõ). Cần ghi đủ cấu hình (K, số nguyện vọng, tỉ lệ chỗ, cách chia, máy) trong báo cáo.

**Q3. Em cũ có "tuyệt đối không đổi" khi chèn em muộn không?**
- **Đúng về thứ tự bốc thăm:** `chen_stb_cho_hoc_sinh_moi` (rbda L1112) chèn em mới ngẫu nhiên đều nhưng giữ thứ tự tương đối của em cũ (bất biến 3 trong CLAUDE.md). Stage 0 không đo lại riêng phần này.
- **Sai về kết quả phân bổ:** em cũ có thể đổi chỗ. Số của gói (2.000 HS, dữ liệu tự sinh, chưa đo lại ở Stage 0): trung bình 1,72 em cũ bị đổi khi có 1 em muộn; 40,7 em đổi và 9,55 em mất hẳn chỗ khi có 20 em muộn; không có em nào tốt lên.
- Bước 6 của Stage 0 không đo điều này. Nó chỉ cho thấy tiếp tục DA cho cùng kết quả với chạy lại toàn bộ (38/38), tức là sai khác từ việc chèn em mới, không phải lỗi của cơ chế tiếp tục.

**Q4. 7,65 s ở 5.000 × 10 CLB và 0 cặp phá vỡ ở 5.000 × 100 CLB cần thống nhất thế nào?**
- Đo ở Stage 0 (cùng dữ liệu sinh, chia đều): 0 cặp phá vỡ ở cả K=10, K=20 và K=100. `verify_stability` mất 2,09 s (K=10) và 0,47 s (K=100); không có cấu hình nào đạt 7,65 s trên máy này.
- Kết luận đề nghị: báo cáo phải ghi cùng cấu hình và máy cho mọi con số thời gian. Không dùng một con số 7,65 s không kèm cấu hình để so với K=100.

**Q5. Đối chiếu `verify_stability` với thư viện `matching`.**
- Đã thử `pip install matching`: cài được (phiên bản 1.4.3) vào `.venv`, không thêm vào requirements.
- Trạng thái: **có thể cài; so sánh để giai đoạn sau.** Chưa làm so sánh trong Stage 0.

**Q6. Phụ thuộc giữa các mục (`phu_thuoc`) có cần sửa không?** Có. Đề xuất sửa:
1. **Z7 → Z3:** chỉ điểm gọi trong api.py (L1089–1094) phụ thuộc Z3. Z7 phần lõi (`run_rbda`, `verify_stability`) có thể làm trước Z3; giữ thứ tự chung nhưng ghi chú.
2. **Điều hướng bản nhanh (dispatch) chưa có chủ:** Z4 chỉ đúng cho `club_choice_function` mặc định. Không mục nào sở hữu việc chuyển sang bản chậm khi `choice_fn` khác. Đề xuất gắn vào **Z4** (cần tham số của Z7; có thể kiểm bằng so sánh `choice_fn is club_choice_function` trước khi Z7 xong).
3. **G1 → Z4:** Z4 chỉ cần cho tốc độ, không cho tính đúng. Nên ghi là phụ thuộc mềm.
4. **C1 → so_nhap.py:** C1 phải bắt đầu từ `so_nhap.py` (đã có giao diện), không chỉ từ CSV. Thêm phụ thuộc vào `so_nhap.py`.
5. **Z1 và C1 → `.claude/skills/`:** hai script (`sinh-du-lieu-clb/scripts/sinh_du_lieu.py`, `xu-li-raw-forms/scripts/xu_li_raw.py`) import `so_nhap`. Mọi thay đổi Z1, C1, B1 phải giữ tương thích; thêm vào phần kiểm nhận.
6. **A2 'nhan_het' → loi_suc_chua (L271) và sanity (L2128):** không chỉ sanity như sổ ghi.
7. **`run_full_pipeline` không phải mục tiêu của Z7:** docstring ghi đây là đường thử nghiệm, từ chối chạy trên CSDL thật, không có verify, rollback hay run_history (L1953).

**Q7. Ngành nào làm trước?** Quyết định của chủ dự án.

---

## Chỗ sai hoặc thiếu trong sổ đăng ký

- **Số test lỗi thời:** gói ghi ~483 ca và ~95 giây; BAN_GIAO.md ghi 1.160 ca và ~3,5 phút; đo được 1.287 ca đạt trong 22 phút 32 giây trên máy 4 nhân (xem bước 3). Z6 ghi '37 tệp, 483 ca': đo được 91 tệp.
- **Chưa có CHANGELOG.md:** gói yêu cầu cập nhật sau mỗi mục nhưng không có tệp nào. Giai đoạn 0 tạo `CHANGELOG.md`.
- **Dòng trôi trong các tệp api:** api.py (+40 đến +48), api_nhap.py (+~230), api_xuat.py (+210 đến +260), api_quan_ly.py (+5); bảng dòng cụ thể nằm ở bảng đối chiếu.
- **`_run_pipeline_da_khoa` có 581 dòng, không phải 573** (L784–1364, hàm cuối của api.py).
- **Tên hàm không tồn tại hoặc sai loại:** `_xuat_excel` (C2) không có (đúng là `_ghi_so_excel`, `_luu_so_excel`); `chi_buoi` (G1) là tham số, không phải hàm.
- **Hiện trạng C1 lỗi thời:** Sổ nhập Excel một tệp (`so_nhap.py`, `import_so_nhap`, `xem_truoc_so_nhap`) là đường nhập có giao diện, và là nguồn duy nhất cho định dạng workbook. C1 phải bắt đầu từ đây.
- **Dict schema không được nêu tên:** các bảng ràng buộc nằm trong `_BANG_RANG_BUOC` (L1250), không chỉ `DEFAULT_SCHEMA`. B1, B2, Z1, A4, A5, A11 cần nêu.
- **Docstring của `run_rbda` (L334–342) sai:** nói số vòng 'đúng bằng độ dài danh sách nguyện vọng dài nhất'; dữ liệu thử tải của dự án cho tới 227 vòng với 10 nguyện vọng. Việc sửa docstring nên thuộc Z5.
- **Số đo của Z4 không khớp trên máy này:** 22–24 s và ≈20× không tái lập; sổ phải ghi máy và cấu hình.
- **Số đếm của Z1 không tái lập** (xem bảng). Sổ phải ghi phương pháp đếm để tái lập được.
- **E3 dẫn rbda L1756–1793:** đây là dấu vân tay dữ liệu (`dau_van_tay_du_lieu`), thuộc E2 nhiều hơn; E3 chỉ dùng gián tiếp qua `export_du_lieu_dau_vao`.
- **E1 thiếu một hiện trạng đã thay đổi:** browser_host đã có danh sách trắng theo đuôi tệp (L80–90), nên `app.db` không còn được phục vụ qua HTTP.
- **`run_full_pipeline` không nên là mục tiêu của Z7** (đường thử nghiệm).
- **Phụ thuộc:** xem Q6 (Z7→Z3 chỉ ở api.py, Z4 dispatch chưa có chủ, G1→Z4 là phụ thuộc mềm, C1→so_nhap.py, skill phụ thuộc so_nhap, A2 chạm loi_suc_chua).
- **Tệp tham khảo:** `kiem_verify_nhanh.py`, `exp_resume.py` (và `_chung.gen`) cần numpy, không có trong requirements và đúng là không phải phụ thuộc sản phẩm. Lúc nhập gói, ruff (bộ luật của `pyproject.toml`) báo **19 lỗi** trên thư mục này và thư mục từng bị loại khỏi ruff; **hiện nay** lỗi đã được sửa, loại trừ đã bỏ, `docs/ke_hoach/tham_khao` được ruff kiểm như mã khác. `docs/*` vẫn loại khỏi đo phủ (không phải mã sản phẩm); phủ đo ở giai đoạn 0 là 91,06 %.
- **Tiến độ đo tốc độ tiếp tục DA (G1):** sổ ghi nhanh hơn 1,8–3,9 lần; đo ở Stage 0 là 2,4–4,0 lần (khác máy).
- **Ghi chú môi trường:** CLAUDE.md của gói ghi '~95 giây', '~37 tệp, ~483 ca' và số dòng api.py cũ; đã sửa trong CLAUDE.md sau giai đoạn 0 (xem CHANGELOG.md).
