# BÀN GIAO NGỮ CẢNH — Dự án RB-DA

> **Đọc file này đầu tiên khi bắt đầu phiên làm việc mới.**
> Cập nhật lần cuối: 27/09/2026 · 831 test pass (kể cả test trình duyệt)

---

## 1. Dự án là gì

Phần mềm kiosk **phân bổ học sinh vào Câu lạc bộ** cho một trường THPT, dùng thuật toán
**Reserve-Based Deferred Acceptance (RB-DA)** — họ Gale–Shapley, có dự trữ mềm
(soft reserves, Kominers & Sönmez 2016) và Single Tie-Breaking (STB).

Đây là **đề tài dự thi nghiên cứu khoa học cấp Sở GD&ĐT**, không phải phần mềm thương mại.
Điều này quan trọng: xem mục 6 về quy định sử dụng AI.

**Kiến trúc:** ứng dụng desktop offline — pywebview (Python) + HTML/CSS/JS thuần, dữ liệu
trong SQLite một file (`app.db`). Không có server, không đăng nhập (chốt từ đầu: offline-first).

---

## 2. Trạng thái hiện tại

| | |
|---|---|
| Repo | `nguyenphanvantruong6969-arch/rbda-kiosk` — mã nằm ngay ở **gốc repo** |
| Nhánh | Nhánh chính `main`. Đợt gần nhất: `claude/program-design-review-oxjnp1` (PR #1) |
| Test | **1160 test, tất cả pass** (`xvfb-run -a ./.venv/bin/python -m pytest tests -q`) · ~3,5 phút |
| Bản `.exe` | Build qua GitHub Actions (workflow `build-windows-exe.yml`, chạy tay) |

**Chạy thử:**
```bash
python3 -m venv .venv                        # XEM LƯU Ý bên dưới
./.venv/bin/pip install -r requirements-dev.txt
./.venv/bin/python -m pytest -q              # chạy test
./.venv/bin/python main.py                   # chạy app
```

> **LƯU Ý cho phiên làm việc mới:** `.venv/` nằm trong `.gitignore` nên KHÔNG
> theo repo. Máy chạy phiên Claude là container mới, clone lại từ đầu mỗi lần
> — nên **luôn phải dựng lại `.venv` trước khi chạy test**. Đừng tưởng dự án
> hỏng khi thấy `./.venv/bin/python: No such file or directory`.

---

### Làm lại thẻ Kết quả cho người quản trị (27/09/2026)

Nhánh `claude/upbeat-gates-puuq1s`. Chỉ đụng giao diện (`index.html`, `app.js`,
`style.css`, `i18n.js`); không đổi API, không đổi ai vào CLB nào
(`test_ket_qua_khong_doi.py` vẫn xanh).

- **Dải "Tóm tắt lần xếp"** đầu thẻ: em đã có chỗ, % được nguyện vọng 1 (và
  trong 3 NV đầu), chỗ còn trống, em chưa có chỗ, suất dự trữ bỏ phí. Mỗi số
  lấy từ đúng hàm mà mục chi tiết dùng. Bấm ô là mở + cuộn tới mục đó.
  Chưa chạy lần nào thì dải ẩn (không nói "0 em · Ổn").
- **Biểu đồ lấp đầy**: tên CLB đủ rộng, hiện %, độ chọi; nhóm theo buổi kèm
  tổng từng buổi; ô **Sắp xếp** (theo buổi / đầy nhất / vắng nhất / chọi cao
  nhất, được nhớ); nhãn "⚠ Không ai" / "○ Còn nhiều chỗ" (ký hiệu + chữ, không
  chỉ màu). Cố ý KHÔNG có nhãn "quá tải" — trên bộ 5 buổi nó dán lên mọi dòng.
- **Chú thích nổi** (rê chuột hoặc Tab) trên biểu đồ lấp đầy, độ phủ, nguyện vọng.
- **Màu chuỗi số liệu mới** `--chart-general` #15714A / `--chart-reserve`
  #B7791A: cặp cũ (--moss/--gold) trượt phép kiểm bảng màu (xanh quá xám, vàng
  dưới 3:1). Cặp mới qua đủ sáu phép kiểm của validator trong skill `dataviz`.
- Test mới: `tests/test_giao_dien_tom_tat_ket_qua.py` (15 test, Playwright).
- **28/09 — đổi tên + vành khuyên:** mục "Nguyện vọng thứ mấy thì được" đổi
  thành **"Mức đáp ứng nguyện vọng"** (EN "How well choices were met"; id
  `nvPanel` giữ nguyên). Thêm biểu đồ vành khuyên (SVG tự vẽ, không thư viện)
  cạnh thanh ngang: % NV1 ở giữa, chú giải, chú thích nổi. Màu là dải TUẦN TỰ
  `--seq-1..4` (thứ hạng có thứ tự). Hình tròn chỉ dùng ở đây — suất dự
  trữ/chung chỉ 2 phần, còn trộn "em chưa có chỗ" vào thì sai mẫu số ở
  trường nhiều buổi. Yêu cầu của Truong: *"Suggest other name for “nguyen vong
  may thi duoc suat” and include any info that can be added and display using
  a pie chart"*.

Nhật ký AI: toàn bộ mã trên do AI (Claude) viết theo yêu cầu của Truong —
*"use this skill to redesign charts and information in the Result sector to be
more friendly and helpful for the adminstrator. Define done as Renovate and
help display data better"*. Mã học sinh viết bị sửa: `app.js`
(`loadClubFillStats` viết lại, `loadPhanBoNguyenVong`, `loadDoPhu`,
`loadResultsTab`, `initResultsHandlers`), `index.html` (thẻ Kết quả),
`style.css` (khối biểu đồ lấp đầy, độ phủ).

---

### Rà soát thiết kế 27/09/2026 — ĐỌC `KE_HOACH_SUA_THIET_KE.md`

Nhánh `claude/program-design-review-oxjnp1`. Đã làm xong và đã đẩy lên:

- **Hạt giống khoá cùng bộ số bốc thăm** — đổi hạt giống khi đã khoá bị chặn
  (`hat_giong_da_khoa`), ô hạt giống chỉ đọc; đổi qua nút Vẽ lại.
- **Cảnh báo thi quá 5 CLB/buổi** sau khi CLB đổi buổi (`health_thi_qua_tran_buoi`).
- **Ràng buộc CSDL** (FOREIGN KEY + CHECK) trên năm bảng; CSDL cũ chỉ được nâng
  lên khi sạch, có sao lưu trước; CSDL bẩn không bị đụng, bảng sức khoẻ chỉ ra.
- **Bảng thông báo lỗi một nguồn**: sửa `i18n_errors.py` rồi chạy
  `python tao_i18n_js.py` (sinh `i18n_loi.js`). KHÔNG sửa tay `i18n_loi.js`.
- **Test "kết quả từng em không đổi"** (`tests/test_ket_qua_khong_doi.py`).

Bộ test: **816 pass** (kể cả test trình duyệt). Nhật ký AI cho các việc này:
`KE_HOACH_SUA_THIET_KE.md` §11. Việc còn lại của kế hoạch: §10 của tệp đó.

### ĐÃ SỬA (28/09/2026) — điểm "ẩn" sau khi bỏ tick, và ô tìm không hiểu tiếng Việt

Nhánh `claude/section-3-search-score-data-3zc7l9`. **847 test pass** (kể cả test
trình duyệt, 0 bỏ qua).

**Lỗi điểm ẩn.** Bỏ tick một CLB đã chấm ở Bước 1 (hoặc *Sửa lại từ đầu*, hoặc nạp
lại tệp chọn CLB thi) chỉ xoá ô tick; điểm nằm lại trong `club_scores`. Điểm đó
biến khỏi thẻ 05, không xoá được (`score_not_applicant`), mà **vẫn được tính** nếu
em còn xếp CLB đó — lên Tầng 1 bằng bài thi đã rút. Đo được: CLB A một chỗ, HS1
thi 5, HS2 thi 9 rồi bỏ tick → HS2 vẫn lấy chỗ của HS1. Không có cảnh báo nào.

**Luật đã chốt (Truong chọn):** điểm chỉ tồn tại — và chỉ được tính — khi ô tick
còn. Bỏ tick = rút khỏi bài thi → xoá điểm, và **nói ra** số điểm đã xoá.

- `api.py` `_xoa_diem_khong_con_tick` — gọi trong CÙNG giao dịch ở cả ba cửa ghi
  ô tick: `submit_test_selection`, `reset_student_entry`,
  `import_test_selection_csv`. Cả ba trả `n_scores_removed`; nạp tệp thêm cảnh
  báo `csv_score_removed_unselected` cho từng em. **Cửa ghi ô tick mới nào cũng
  phải gọi hàm này.**
- `load_from_sqlite` chỉ đọc điểm có tick đi kèm (JOIN) — CSDL cũ còn sẵn điểm
  ẩn vẫn chạy đúng. Bảng sức khoẻ: cảnh báo mới `health_diem_khong_dang_ky_thi`;
  mục điểm lệch (8) cũng chỉ tính điểm có tick, khớp tập điểm lần chạy dùng.
- `app.js` — thông báo "đã xoá N điểm", và danh sách học sinh ở thẻ 03 làm mới
  thẻ "n CLB thi / n nguyện vọng" ngay sau khi lưu (trước đây đứng yên).

**Ô tìm.** `LIKE` của SQLite chỉ bỏ qua hoa/thường với chữ Latin trơn: "BÌNH"
không ra "Bình", "binh" không ra gì, `%`/`_` là ký tự đại diện. Giờ `connect_db`
đăng ký hàm SQL `khop_tim` (bỏ dấu, `đ→d`, casefold, so chuỗi con thật); cả năm
ô tìm (`list_students_admin`, `search_students`, `get_match_results`,
`get_thoi_khoa_bieu`, `get_so_boc_tham_theo_buoi`) dùng nó.

Test: `tests/test_diem_theo_o_tick.py`, `tests/test_tim_kiem_tieng_viet.py`,
`tests/test_giao_dien_nhap_tai_cho.py` (Chromium thật — 3 test đỏ với bản cũ).
**Kết quả các bộ dữ liệu mẫu không đổi** (`test_ket_qua_khong_doi.py` xanh): chúng
không có điểm nào thiếu tick.

### ĐÃ LÀM (28/09/2026, phiên sau) — xuất dữ liệu có tuỳ chọn, và hồ sơ học sinh

Cùng nhánh. **884 test pass**, 0 bỏ qua. Thẻ 02 có mục **Xuất dữ liệu** với ba ô
tuỳ chọn; thẻ 02 và thẻ 04 chọn được học sinh để xuất hồ sơ.

| Tính năng | API (`api.py`) | Ghi chú |
|---|---|---|
| Kết quả phân bổ | `export_csv` | Không đổi, trừ một dòng mới trong tệp tổng hợp: *"Kết quả còn khớp dữ liệu"* |
| Dữ liệu đầu vào hiện tại | `export_du_lieu_dau_vao` | 3 tệp **nạp lại được**. Tệp 02 ở **dạng rộng** (`test_club_N, score_N`) — dạng dài `club_id,score` cố ý bị cửa nạp coi là mơ hồ (`test_upload_tu_nhan_dien.py`), ĐỪNG đổi sang dạng dài |
| Thay đổi so với lần trước | `get_thay_doi_ket_qua`, `export_thay_doi_ket_qua` | Bảng mới `ket_qua_truoc`: `run_pipeline` chụp `match_results` trong CÙNG giao dịch, trước mọi lệnh xoá |
| Kết quả có thể đã cũ | `get_trang_thai_ket_qua`, `_dau_van_tay_du_lieu` | Bảng mới `dau_van_tay_chay` (SHA-256 dữ liệu quyết định kết quả, không gồm số bốc thăm và tên). Chạy một phần chỉ ghi dấu vân tay khi dữ liệu chưa đổi hoặc không còn buổi nào giữ kết quả cũ |
| Hồ sơ học sinh | `export_hoc_sinh_csv(ids)` | Mỗi dòng một cặp (em, CLB); em chưa nhập gì vẫn có một dòng; số bốc thăm từng buổi lấy từ `get_so_boc_tham_theo_buoi` |

Nối kết đã soát: `reset_data` và `delete_student` dọn hai bảng mới; `_parse_csv_rows`
gỡ đúng dấu nháy mà `_an_toan_cho_excel` thêm khi xuất (tên `=1+1` đi vòng tròn
nguyên vẹn). `_an_toan_cho_excel`, `_ghi_csv`, `_duong_xuat` giờ là hàm dùng chung
cho MỌI lần xuất — thêm kiểu xuất mới thì dùng ba hàm này.

**Sửa kèm (lỗi có từ trước):** bảng "Danh sách xếp CLB" ở trường một buổi ẩn tiêu
đề cột "Buổi" nhưng không ẩn ô dữ liệu, nên mọi cột lệch sang phải một ô. Giờ ẩn
theo từng dòng như `.cot-buoi-clb`; `test_giao_dien_xuat_du_lieu.py` canh.

Test: `test_xuat_du_lieu.py` (vòng tròn xuất → xoá → nạp lại → so 5 bảng → chạy lại
→ so kết quả), `test_thay_doi_ket_qua.py`, `test_xuat_hoc_sinh.py`,
`test_giao_dien_xuat_du_lieu.py` (Chromium).

### ĐÃ LÀM (28/09/2026, phiên sau nữa) — rà giao diện theo ý định người dùng

Cùng nhánh. **899 test pass**, 0 bỏ qua. Chạy app thật (Chromium, trường 2 buổi 12
em), đi từng ý định; bảy chỗ vướng đã sửa:

| # | Ý định | Đã sửa |
|---|---|---|
| 1 | Xuất em đang mở ở thẻ 03 | Nút **Xuất CSV em này**; còn thay đổi chưa lưu thì nhắc lưu trước |
| 2 | Chọn em không được xếp (trường nhiều buổi) | Ô **Hiện cả em chưa được xếp** thêm MỘT dòng *Cả tuần* mỗi em |
| 3 | Mục Xuất ở đầu thẻ 02 xa bảng chọn ~1.400 px | Ô thứ tư **Hồ sơ học sinh đã chọn** + nút **Chọn học sinh…** (mở mục nếu đang thu gọn, cuộn tới, đặt con trỏ vào ô tìm); chọn em đầu tiên thì ô tự bật |
| 4 | Thẻ 04: nút xuất nằm trong mục "Gán diện dự trữ" | Đổi tiêu đề mục, thêm bộ đếm "Đã đánh dấu N em" |
| 5 | Tìm tệp vừa xuất | Nút **Mở thư mục** — `api.mo_thu_muc` CHỈ mở thư mục nằm trong chỗ xuất (`realpath`+`commonpath`, không qua shell) |
| 6 | Dải "kết quả có thể đã cũ" | Nút **Đi tới Vận hành sắp xếp** |
| 7 | Thẻ 03: thay đổi chưa lưu mất im lặng khi sang em/thẻ khác (lỗi có từ trước) | Dấu **• Chưa lưu**; rời đi phải bấm lại **đúng chỗ đó** lần hai trong 4 giây (`roiDiNeuDuoc(hanhDong, khoa)` — khoá theo hành động, vì bấm em khác rồi bấm sang thẻ khác KHÔNG phải xác nhận đổi thẻ) |

**Sửa sau /code-review (3 lỗi, mỗi lỗi một test đỏ-trước-xanh-sau, `test_sua_theo_danh_gia.py`
+ `test_giao_dien_ux_xuat.py`):** (1) dấu vân tay giờ lấy CÙNG lần đọc với dữ liệu
(`load_from_sqlite_kem_dau_van_tay`, đọc trong giao dịch `BEGIN` — kiosk lưu giữa
chừng thì chờ rồi thành công, và kết quả bị báo "cũ" đúng); (2) `_nam_trong` bắt
`ValueError` khác ổ đĩa của `commonpath`; (3) xoá dữ liệu / xoá học sinh dọn tập em
đã chọn ở thẻ 02, và `boHsKhongConTonTai` bỏ em không còn tồn tại nếu backend báo.

Lưu ý CSS: `display:flex` thắng thuộc tính `hidden` — lớp nào đặt `display` mà có
lúc cần `hidden` thì phải thêm luật `[hidden] { display: none; }` (xem cuối
`style.css`). Test: `test_giao_dien_ux_xuat.py`, `test_mo_thu_muc.py`.

---

## 3. Bản đồ mã nguồn

### Học sinh tự viết (bản gốc upload 26/08/2026)
- `rbda_priority_pipeline.py` — **thuật toán lõi**. `DEFAULT_SCHEMA` trong file này là nguồn
  sự thật duy nhất cho schema DB (không có `02_schema.sql` riêng).
- `api.py` — lớp `PipelineAPI`, cầu nối JS ↔ Python. Mọi hàm trả `{ok, data, errors}`.
- `main.py`, `index.html`, `style.css`, `app.js`, `kiosk.spec`
- `ky_va_tin_cay.ps1` + `HUONG_DAN_CAI_DAT.md` — xử lý cảnh báo chữ ký Windows

### AI viết mới (đã trích dẫn đầy đủ trong nhật ký AI)
- `i18n_errors.py` — bảng thông báo lỗi song ngữ vi/en, **nguồn duy nhất**.
  `tao_i18n_js.py` sinh ra `i18n_loi.js` cho giao diện: sửa `i18n_errors.py`
  rồi chạy `python tao_i18n_js.py`. **Không sửa tay `i18n_loi.js`** —
  `tests/test_i18n_sync.py` đỏ ngay nếu nó cũ hơn nguồn.
- `i18n.js` — chữ giao diện song ngữ (`UI_STRINGS`) + hàm dịch; đọc bảng lỗi từ `i18n_loi.js`
- `recovery.py` / `recovery.html` / `recovery.js` — màn hình phục hồi khi `app.db` hỏng
- `browser_host.py` — chế độ chạy dự phòng bằng trình duyệt
- `tests/` — 53 file test, 816 test case (13 file chạy giao diện thật bằng Playwright + Chromium).
  Đáng biết nhất: `test_ket_qua_khong_doi.py` băm kết quả từng em trên sáu bộ mẫu —
  sửa cấu trúc mã mà nó đỏ là đã đổi ai vào CLB nào
- `KE_HOACH_SUA_THIET_KE.md` — kế hoạch sửa thiết kế sau rà soát 27/09: việc đã làm,
  việc còn lại, và dòng nhật ký AI (§11)
- `so_nhap.py` — định nghĩa **Sổ nhập CLB**: một tệp Excel duy nhất giao diện nhận
  (trang `1. CLB`, trang `2. Học sinh`). Thay cho ba tệp nạp cũ theo góp ý của ban
  giám khảo; `tests/test_so_nhap.py` canh sổ và ba tệp cũ ra cùng một kết quả
- `.claude/skills/sinh-du-lieu-clb/` — skill sinh và soát Sổ nhập CLB
- `mau_csv/` — `SO_NHAP_CLB.xlsx` (sổ trống) + `HUONG_DAN_SO_NHAP.md` (hướng dẫn
  người vận hành) + `tao_so_nhap.py` (sinh lại mọi sổ mẫu) + 8 file CSV định dạng
  nội bộ kèm `HUONG_DAN_CSV.md` + `vi_du_day_du/` (một trường hoàn chỉnh, 0 cảnh
  báo, có cả sổ lẫn ba CSV, kèm `GIAI_THICH.md`)
- `du_lieu_test/` — **các bộ dữ liệu MÔ PHỎNG**, mỗi bộ một mục đích khác nhau:
  - `TEST_01..04` (120 em, 10 CLB) + 1 tệp **cố ý sai 6 chỗ** — kiểm tra phần mềm
    có cảnh báo không. Sinh bằng `tao_du_lieu_test.py`, seed 2026
  - `bo_sach/` (140 em, 12 CLB) — chạy thử quy mô gần thật, **0 cảnh báo**,
    xếp 140/140. Seed 9090
  - `vi_du_huong_dan/` (10 em, 4 CLB) — bộ dạy học đi kèm `HUONG_DAN_SU_DUNG.md`,
    số liệu **viết tay** để in trọn vào hướng dẫn. Xem README của nó
  - `bo_nhieu_buoi/` (160 em, 13 CLB, 5 buổi), `bo_sau_buoi/` (180 em, 17 CLB) và
    `bo_can_bang/` (200 em, 24 CLB) — dữ liệu nhiều buổi; mỗi thư mục có script sinh lại
  - `thu_tai/` — đo phần mềm ở quy mô lớn (xem README của nó)
  - `app_DEMO_da_cham_diem.db` — CSDL demo đã nạp và chấm xong (lược đồ CŨ,
    tự được nâng cấp khi mở bằng bản hiện tại — có test canh)
  - `NHAP_TAY.md` — kịch bản gõ tay 8 em / 3 CLB cho các màn hình mà đường nạp
    tệp không chạm tới
- `HUONG_DAN_SU_DUNG.md` — hướng dẫn vận hành 14 mục, viết cho người **chưa từng
  mở phần mềm**. Có bản trang web để gửi cho giám khảo (xem nhật ký AI).
  Mọi con số trong đó lấy từ số đo thật của `vi_du_huong_dan/`, và
  `tests/test_vi_du_huong_dan.py` khoá lại — bộ mẫu lệch là hướng dẫn nói dối

---

### LỖI 13 — app chết sau một lúc mở (30/08) — ĐÃ SỬA

**Triệu chứng học sinh gặp:** mở app một lúc rồi quay lại, kéo file vào thì mọi
file đều báo `TypeError: Failed to fetch`. Giao diện vẫn hiện đầy đủ, số liệu vẫn
đó, nhưng không thao tác nào chạy.

**Nguyên nhân:** `browser_host.py` đếm ping do `setInterval` gửi, không có ping quá
120 giây thì tự tắt máy chủ. Giả định đằng sau con số 120 là "trình duyệt bóp ping
thưa xuống ~1 lần/phút" — **giả định đó SAI**. Chromium hiện **đóng băng hẳn** bộ
đếm giờ của trang bị che (intensive throttling), và Edge trên Windows bật thêm
**Efficiency mode** — nhìn thấy rõ ngay trong ảnh Task Manager học sinh gửi
trước đó: dòng *Tab: Phân bổ Câu lạc bộ* mang nhãn *Efficiency mode*.

Ping không thưa đi, nó **ngừng hẳn**. Máy chủ tự tắt trong khi cửa sổ vẫn mở.
Trình duyệt giữ lại hình đã vẽ nên nhìn như app còn sống.

**Cách sửa:** tín hiệu chính không còn là bộ đếm giờ mà là **một socket đang mở**.
Trang mở `EventSource("/__alive__")` và giữ nguyên. Trình duyệt **không** đóng băng
socket — nó chỉ đóng băng bộ đếm giờ. Cửa sổ còn mở thì kết nối còn đó; đóng cửa sổ
thì đứt ngay và máy chủ biết tức khắc. Ping cũ giữ lại làm lưới đỡ cho trường hợp
kết nối đó không thiết lập được lần nào (lúc đó vẫn dùng ngưỡng 120 giây cũ).

**Đã kiểm bằng Chromium THẬT** (Playwright + Xvfb): dừng hẳn mọi `setInterval` của
trang để giả lập đóng băng, hạ ngưỡng ping xuống 3 giây, chờ 9 giây — gọi backend
vẫn **thành công**. Với cách cũ thì đã chết từ giây thứ 3.

**Sửa kèm:** nhánh `open_browser=False` không gọi `server_close()`, nên sau khi
dừng, cổng vẫn mở: kết nối mới bắt tay được nhưng không ai trả lời, bên gọi **treo
vô hạn** thay vì nhận lỗi rõ ràng. Chính chỗ này làm bộ test treo lúc phát hiện.

### Soát lại vòng NẠP → XUẤT (30/08) — tìm thêm 2 lỗi im lặng

Chạy 7 ca hiểm của vòng nạp-xuất. 5 ca đạt ngay. Hai ca hỏng, cả hai đều im lặng:

**Lỗi 11 — `csv.Sniffer` làm vỡ ô có dấu nháy kép.** `sniff()` trả về
`doublequote=False`, tức bỏ quy ước `""` của CSV. Ô `"Trần ""Bo"" Văn A, Jr."` bị
cắt ngay dấu phẩy; phần đuôi `Jr."` trôi sang cột kế bên và bị hiểu là mã club. Cả
dòng bị bỏ, kèm cảnh báo *"club không tồn tại"* **chẳng liên quan gì tới nguyên
nhân thật** — người nhập sẽ đi tìm sai chỗ. Tên CLB tiếng Việt rất hay có dấu
nháy (`CLB "Vì Cộng Đồng"`). Đã sửa: chỉ lấy **dấu phân cách** từ Sniffer, phần
quy ước trích dẫn dùng `csv.excel` chuẩn. Có test canh `;` và Tab vẫn nhận đúng.

**Lỗi 12 — tệp của lần xuất trước còn sót lại.** Xuất lần hai mà một CLB không còn
ai vào thì tệp `.csv` của nó từ lần một **vẫn nằm nguyên**, trông y hệt tệp thật.
Giáo viên cầm nhầm đi tổ chức một CLB không còn học sinh nào. Đã sửa: dọn `.csv`
cũ trong đúng thư mục `_theo_club` trước khi ghi. Có test canh **không** đụng vào
tệp khác của người dùng để trong đó.

**Sửa thêm (không phải lỗi, là lỗ hổng):** ô bắt đầu bằng `= + - @` bị Excel TÍNH
như công thức — học sinh tên `=1+1` hiện ra là `2`. Nay thêm dấu nháy đơn ở đầu.

Ca thứ 7 tôi tưởng hỏng hoá ra **test viết sai**: `delete_club` từ chối xoá club
còn nguyện vọng/kết quả tham chiếu tới (`cannot_delete_club_referenced`) — phần
mềm đang bảo vệ dữ liệu đúng như phải thế.

Đã đối chứng A/B với bản trước khi sửa: bản cũ nạp tên có dấu nháy ra **0 học
sinh**, bản mới ra **1**; bản cũ để sót `clb_b.csv`, bản mới sạch.

### Biểu tượng ứng dụng (30/08)

Học sinh tự thiết kế, nộp dạng SVG. Nguồn gốc duy nhất là `logo.svg`;
`tao_logo.py` vẽ lại bằng Pillow ở độ phân giải gấp 8 rồi thu nhỏ, sinh ra
`logo.png` (512, nền trong suốt) và `logo.ico` (7 cỡ, 16→256). **Sửa hình thì sửa
`logo.svg` rồi chạy lại `tao_logo.py`, đừng sửa tay tệp .png/.ico.**

Gắn ở hai chỗ vì có hai đường hiển thị: `icon="logo.ico"` trong `kiosk.spec` cho
tệp `.exe`, và `<link rel="icon">` trong `index.html`/`recovery.html` cho cửa sổ
trình duyệt dự phòng. Ảnh chụp ngày 30/08 là lúc đường dự phòng đang chạy, nên quả
địa cầu học sinh nhìn thấy khi đó là biểu tượng mặc định của trang web, không phải
của `.exe`. Từ 31/08 đường chính chạy được, biểu tượng lấy từ `logo.ico`.

`tests/test_bieu_tuong.py` (8 test) canh cả hai, kèm một test soát mọi tệp khai
báo trong `datas` của `kiosk.spec` đều tồn tại thật.

### Vì sao ba phiên phải ĐOÁN lỗi pythonnet (30/08) — đã sửa gốc

`main.py` bắt được ngoại lệ khi pywebview hỏng rồi ghi vết lỗi ra
**`sys.stderr`** — mà bản đóng gói chạy `console=False` thì **không có stderr nào**.
Vết lỗi bị vứt đi đúng lúc nó xảy ra. Đó mới là lỗi gốc: không phải pywebview hỏng,
mà là hỏng **mà không ai biết vì sao**.

Nay có `chan_doan.py`:
- Ghi mọi thứ vào **`loi_khoi_dong.txt`** cạnh `app.db` — nối thêm, không ghi đè.
- Ghi cả khi THÀNH CÔNG, để biết lần nào chạy đường nào.
- Không bao giờ ném lỗi ra ngoài (hỏng phần ghi log mà làm chết app thì tệ hơn).

**Giả thuyết đang thử — chưa kiểm chứng được:** Windows gắn dấu "tải từ Internet"
(luồng NTFS `Zone.Identifier`) vào mọi tệp giải nén từ `.zip` tải về, và .NET
Framework **từ chối nạp assembly mang dấu đó**. Khớp đúng triệu chứng: thông báo
lỗi nêu rõ đường dẫn tới `Python.Runtime.dll`, tức tệp CÓ ở đó, .NET tìm thấy
nhưng không nạp.

Hai lớp cùng chữa nguyên nhân đó:
1. `chan_doan.go_dau_tai_ve()` xoá luồng `Zone.Identifier` khỏi mọi `.dll/.exe/.pyd`
   trong gói, chạy **trước** `import webview`. Không cần quyền Administrator.
2. `PhanBoCauLacBo.exe.config` với `loadFromRemoteSources enabled="true"` — bảo .NET
   bỏ qua dấu ngay từ đầu. **Phải nằm cạnh `.exe`**, không phải trong `_internal/`;
   quy trình build chép nó vào đúng chỗ, có test canh.

**Máy phát triển là Linux — không có .NET Framework lẫn luồng NTFS, nên hai lớp này
CHƯA CHẠY THẬT lần nào.** Đó chính là lý do phải có lớp ghi log: nếu giả thuyết sai
thì lần này biết sai ở đâu thay vì đoán lần thứ tư.

**Người dùng nay nhìn thấy đang chạy đường nào:** góc dưới thanh bên hiện
"Cửa sổ ứng dụng riêng" hoặc "Chế độ dự phòng (trình duyệt)" (màu vàng). Trước đây
phải mở Task Manager mới biết — và khi không ai biết thì không ai sửa.

### Cột điểm trong file nhập (30/08) — PHÁ LỆ ĐÓNG BĂNG CÓ CHỦ Ý

Học sinh yêu cầu "dữ liệu chạy ra kết quả có nghĩa". Đào ra thì gặp một chỗ chặn
thật: **không có điểm thì mọi em rơi xuống Tầng 2 và chỉ xếp bằng bốc thăm** —
vòng thi coi như không tồn tại. Mà phần mềm khi đó **không có đường nạp điểm từ
file**: 396 ô điểm phải gõ tay, khoảng 18 phút.

Đã thêm cột điểm vào **file chọn CLB muốn thi** (chỉ file đó):
- Dạng rộng: `score_N` ghép với `test_club_N` theo **hậu tố số**, không theo vị
  trí cột. Ghép theo vị trí thì bỏ trống `test_club_2` sẽ gán điểm nhầm club.
- Dạng dài: thêm cột `score`.
- Không bắt buộc. Thiếu cột thì hành vi y hệt trước.
- Ô điểm hỏng chỉ mất **riêng ô đó**, giữ nguyên lựa chọn thi.
- Điểm ghi bằng `club_id` ĐÃ KHỚP qua `_khop_club_id`, không phải chuỗi thô.
- File nguyện vọng có lẫn `score_*` → cảnh báo `csv_scores_ignored_here`.

Đây là **thêm tính năng trong thời gian đóng băng**, học sinh quyết định. Rủi ro
thấp: gói gọn trong một nhánh của `import_test_selection_csv`, 13 test riêng
(`tests/test_nap_diem_tu_file.py`), và ràng buộc "hai dạng cho kết quả giống hệt
nhau" vẫn được canh.

### Bố cục căn giữa (30/08)

`.main` có `max-width` nhưng thiếu `margin-inline: auto`, nên khối nội dung dính
sát mép trái cột `1fr` — màn hình 1900px thừa gần 700px bên phải. Nay căn giữa và
nới 980 → 1280px. Đo bằng Chromium thật ở ba bề rộng: 1900px cho lề 186px đều hai
bên, 1280px và 900px không tràn ngang.

### Bộ dữ liệu thiết kế lại cho cạnh tranh cao (30/08)

Bộ cũ cho 93/118 em được nguyện vọng 1 và chỉ **2 em** dùng tới suất dự trữ —
nhìn bảng kết quả như ai cũng được như ý, thuật toán không lộ ra là nó làm gì.

Ba thay đổi trong `tao_du_lieu_test.py` (giữ `SEED = 2026`):
1. Nguyện vọng bốc theo **độ hút**: 3 CLB "hot" trọng số 10, 3 CLB "nguội" 0.75.
2. Suất dự trữ chuyển sang **đúng các CLB chật**. Đặt ở CLB còn chỗ thì vô dụng.
3. Điểm nhóm dự trữ lệch thấp hơn (6.3/6.5 so với 7.6) — đây là cách dựng số liệu
   để suất dự trữ phải làm việc, **không** phải nhận định về học sinh diện chính sách.

Kết quả đo được: **108/120 được xếp**, nguyện vọng 1 **59%** (cũ 79%), **10 em**
vào bằng suất dự trữ (cũ 2), 12 em chưa được xếp, 4 CLB đầy và 6 CLB thừa chỗ,
**0 cảnh báo dữ liệu** sau khi nạp (vì điểm đã có sẵn trong file).

**Bộ này CỐ Ý thiết kế cho cạnh tranh cao, không mô phỏng phân bố tự nhiên.** Mọi
tài liệu phải ghi rõ điều đó — trình bày như phân bố nguyện vọng có thật là bịa
đặt dữ liệu.

## 4. Quyết định đã chốt — ĐỪNG tự ý đảo ngược

1. **Không bật WAL mode cho SQLite.** Đã thí nghiệm và xác nhận: WAL tạo file phụ `app.db-wal`,
   khiến quy trình sao lưu bằng USB (copy tay file `.db`) tạo ra bản sao **thiếu dữ liệu mới nhất
   mà không báo lỗi**. Giữ `journal_mode=DELETE`. Chỉ dùng `synchronous=FULL` + `busy_timeout=15000`.

2. **`run_pipeline()` là một giao dịch duy nhất, huỷ toàn bộ khi lỗi** (kể cả số STB vừa vẽ).
   Đã chốt phương án này thay vì "giữ lại số bốc thăm".

3. **pywebview là chính, trình duyệt là dự phòng.** Không bỏ pywebview.
   Lý do có chế độ dự phòng: xem mục 5.

4. **Số bốc thăm STB khoá sau lần chạy đầu.** Lời hứa của việc khoá là **thứ tự
   TƯƠNG ĐỐI giữa các em đã có không bao giờ đổi** — không phải "số tuyệt đối
   không đổi", vì số tuyệt đối không hiện ở đâu cho ai thấy. Học sinh thêm vào sau
   được **chèn ngẫu nhiên** vào dàn số (`chen_stb_cho_hoc_sinh_moi`). Vẽ lại toàn
   bộ cần xác nhận 2 bước trên giao diện. Xem khối "ĐÃ SỬA (05/09)" ở mục 5.

5. **Không thêm hệ thống đăng nhập.** Đúng thiết kế "offline-first" đã chốt.

6. **Chế độ dự phòng mở CỬA SỔ ỨNG DỤNG RIÊNG, không phải tab trình duyệt.**
   Dùng cờ `--app=<url>` của trình duyệt nhân Chromium (Edge có sẵn trên mọi
   máy Windows 10/11) → cửa sổ riêng, không thanh địa chỉ, không tab. Đã kiểm
   chứng chạy thật bằng Chromium + Xvfb trong sandbox. Không dùng Firefox vì
   nó không có cờ tương đương. Nếu máy không có trình duyệt Chromium nào mới
   quay về mở tab thường.

7. **KHÔNG bao giờ đoán loại file CSV khi dòng tiêu đề không đủ kết luận.**
   Giao diện cũ có hai ô nạp file và bắt người dùng tự chọn; chọn nhầm thì dữ
   liệu vào SAI BẢNG mà vẫn báo "thành công" (file nguyện vọng dạng dài khớp
   đủ cột của ô chọn-CLB-thi). Nay `detect_csv_kind()` tự nhận diện, và khi
   bộ cột là `student_id, club_id` không kèm `rank` — hợp với cả hai loại —
   thì DỪNG LẠI hỏi người dùng. Đoán bừa ở đây là dựng lại đúng cái bug đó.

8. **Thứ tự nhập bắt buộc: CLB trước, học sinh sau** (`THU_TU_NHAP` trong
   `app.js`). Học sinh tham chiếu `club_id`; nạp ngược thứ tự thì CẢ học sinh
   bị bỏ qua. Giao diện tự sắp xếp nên người dùng thả file thứ tự nào cũng
   được, nhưng đừng bỏ cơ chế sắp xếp này đi.

9. **File xuất kết quả đặt CẠNH `app.db`, không dùng đường dẫn tương đối.**
   Đường dẫn tương đối rơi vào thư mục làm việc của tiến trình — trên máy
   Windows chạy `.exe` qua shortcut, thư mục đó có thể là bất kỳ đâu và
   người dùng không tìm ra file. `export_csv` luôn trả về đường dẫn ĐẦY ĐỦ
   để giao diện hiện đúng chỗ. Cũng phải giữ `utf-8-sig` (BOM) khi ghi,
   nếu không Excel hỏng font tên tiếng Việt.

10. **`openpyxl` đọc thẳng .xlsx — KHÔNG bỏ đi.** Microsoft Forms xuất ra
   `.xlsx`; bắt người dùng tự Save As CSV là bước thừa và là chỗ hỏng dấu
   tiếng Việt nhiều nhất. Ba chỗ .xlsx khác CSV đã xử lý, đừng làm hỏng:
   số thực `20.0` phải đưa về `20` (không thì `int()` ném lỗi và **cả dòng
   CLB bị bỏ qua**), ô trống `None` phải về chuỗi rỗng, và lấy **sheet đầu
   tiên** chứ không phải sheet đang active. `openpyxl` là Python thuần,
   không dính .NET như pythonnet nên không thêm rủi ro đóng gói.

11. **`reserve_group` của học sinh: ô có giá trị GHI ĐÈ, ô trống GIỮ NGUYÊN.**
   Điền được thẳng trong cả hai file học sinh. Ô trống tuyệt đối không được
   xoá nhóm đã gán — file nhập lại mà thiếu giá trị sẽ làm mất dữ liệu.

12. **Mọi nhãn `reserve_group` phải đi qua `chuan_hoa_nhom_du_tru()` TRƯỚC
   khi ghi.** Nhãn gõ ở hai nơi (file CLB và file học sinh) và phải khớp thì
   dự trữ mới chạy; trước đây `chinh_sach` vs `Chính sách` là hai nhóm khác
   nhau và học sinh diện ưu tiên vào theo diện `general`, pipeline vẫn chạy
   hết không báo lỗi. Đã áp dụng ở 5 đường ghi: `create_or_update_club`,
   `import_clubs_csv`, `_ghi_nhom_du_tru` (2 đường CSV học sinh),
   `set_student_reserve_group`, `bulk_set_reserve_group`. Thêm đường ghi mới
   thì PHẢI gọi hàm này.

   Chuẩn hoá lúc GHI chứ không phải lúc SO SÁNH là chủ ý —
   `rbda_priority_pipeline.py` vẫn so khớp chuỗi chính xác, phần thuật toán
   không bị đụng tới.

   Dữ liệu nhập từ TRƯỚC bản này có thể còn nhãn chưa chuẩn; nhập lại file
   CLB và file học sinh là tự quy về mã chuẩn.

13. **`student_id` PHÂN BIỆT hoa/thường, `club_id` thì KHÔNG.** Có chủ ý:
   `club_id` có danh sách gốc trong bảng `clubs` để đối chiếu nên khớp
   hoa/thường an toàn (`_khop_club_id`, thử khớp chính xác TRƯỚC rồi mới bỏ
   qua hoa/thường — trường tạo cả `clb_a` lẫn `CLB_A` thì mã chính xác vẫn
   thắng). `student_id` không có gì để đối chiếu, nên chỉ CẢNH BÁO khi hai mã
   khác nhau mỗi hoa/thường, tuyệt đối KHÔNG tự gộp: gộp nhầm hai em có thật
   là hỏng nặng hơn nhiều so với để người nhập tự sửa.

14. **Ngưỡng tự tắt là 120 giây, KHÔNG được hạ xuống.** Trình duyệt bóp thắt
   `setInterval` của trang bị ẩn xuống ~1 lần/phút; ngưỡng 25 giây cũ khiến
   app tự tắt khi người vận hành chỉ thu nhỏ cửa sổ. Việc tắt nhanh khi đóng
   thật do `sendBeacon` trong `pagehide` lo (đo thực tế ~3 giây), không phải
   do ngưỡng này.

---

## 4b. ⚠️ BÁO CÁO VÀ PHẦN MỀM ĐANG LỆCH — việc học sinh phải tự làm trước 05/09

**Đọc mục này trước khi nộp.** Quét cả hai bản báo cáo `.docx`:

| Từ khoá | Số lần trong báo cáo |
|---|---|
| "dự trữ" | **0** |
| "bốc thăm" / "ngẫu nhiên" | **0** |
| "Reserve" / "RB-DA" | **0** |

Báo cáo mô tả **Gale–Shapley nhiều-một thuần tuý**: mỗi CLB có *"một danh sách
ưu tiên học sinh (Q_j)"* và một sức chứa. Phần mềm chạy **năm** lớp cơ chế, ba
lớp trong đó không có mặt trong báo cáo:

| Lớp | Hàm · dòng | Báo cáo |
|---|---|---|
| Deferred Acceptance, học sinh đề xuất | `run_rbda` · 207 | ✅ có |
| **Dự trữ mềm, xét hai lượt** | `club_choice_function` · 136 | ❌ **chưa có** |
| **Single Tie-Breaking** | `generate_stb_lottery` · 441 | ❌ **chưa có** |
| **Ưu tiên hai tầng thi / không thi** | `compute_club_priority` · 48 | ❌ **chưa có** |
| Kiểm chứng ổn định bằng hàm lựa chọn | `verify_stability` · 322 | ❌ **mâu thuẫn** |

**Hệ quả đi cả hai chiều:** không viết ra thì không được điểm cho phần khó nhất
của phần mềm, mà vẫn mang trọn rủi ro nếu giám khảo mở mã nguồn ra.

**Chỗ nặng nhất — mô hình toán trong báo cáo không mô tả được phần mềm.**
Đã chạy hàm thật để kiểm, không suy đoán
(`python du_lieu_test/do_hai_canh_du_tru.py`):

> CLB sức chứa 3, trong đó 1 suất dự trữ. Ưu tiên **A > B > C > D**.
> D thuộc diện dự trữ. Ưu tiên **giữ nguyên** ở cả hai cảnh.
>
> | | Mô hình một danh sách `Q_j` | `club_choice_function` thật | |
> |---|---|---|---|
> | **Cảnh 1** — D có mặt | A, B, C | **D, A, B** | **LỆCH** |
> | **Cảnh 2** — D vắng mặt | A, B, C | A, B, C | khớp |
>
> Cảnh 1: **C xếp trên D, CLB lấy 3 em — mà D đỗ còn C trượt.**
> So hai cảnh: **cùng em C, cùng thứ hạng, cùng CLB, cùng sức chứa** — lúc có
> suất lúc không. Kết cục phụ thuộc **ai khác đang nộp cùng lúc**, nên không
> viết ra được một `Q_j` cố định.

**Đây KHÔNG phải lỗi** — đó là điều suất dự trữ sinh ra, và là lý do
`verify_stability` phải kiểm cặp phá vỡ bằng chính hàm lựa chọn.
Có **11 test canh** (`tests/test_hai_canh_du_tru.py`); gỡ cơ chế dự trữ ra thì
**5 test đỏ** — đã thử.

**Tài liệu để học sinh viết theo:**

| Tệp | |
|---|---|
| `docs/CO_CHE_THUAT_TOAN.md` | Mô tả năm lớp, kèm số dòng và lý do dự án cần từng lớp |
| artifact `eced0ff9-08df-4922-a17e-5f85d99f79aa` | Bản trang web của tệp trên |
| `du_lieu_test/do_hai_canh_du_tru.py` | Bộ đo chạy lại được — gõ một lệnh là ra bảng hai cảnh |

> **AI KHÔNG viết phần cơ sở lý thuyết.** Hai tệp trên mô tả *phần mềm chạy cái
> gì*, không diễn giải ý nghĩa khoa học. Phần lý thuyết cho ba lớp còn thiếu là
> việc học sinh tự viết — Phụ lục 1.

**Về trích dẫn:** cả dự án chỉ có **đúng một** tên tài liệu — *Kominers & Sonmez
2016*, ở `rbda_priority_pipeline.py` dòng 6 và 145, **do chính học sinh viết**
trong commit đầu tiên `57f2e82` (26/08). AI **không** thêm tên nào, **không** lập
danh mục tài liệu tham khảo, **không** đánh giá tính mới — Phụ lục 1 cấm.

---

## 5. Vấn đề chưa giải quyết

### ⚠️ CÒN MỞ (02/09) — một test giao diện chập chờn

`tests/test_giao_dien_xoa_du_lieu.py::test_moi_o_so_tren_man_hinh_cap_nhat_ngay_sau_khi_xoa`
**đỏ 1 lần trên 2 lần chạy toàn bộ** ngày 02/09. Chạy lại toàn bộ: **404/404
xanh**. Chạy riêng mình nó: xanh, 2,4 giây.

**Không phải lỗi sản phẩm.** Hôm đó không đụng một dòng mã nguồn nào — chỉ sửa
tài liệu, `.gitignore` và thêm hai tệp Word. Nghi là chỗ **bấm hai bước** ở dòng
143–147: bấm lần một, chờ nút vào trạng thái `is-confirming`, rồi bấm lần hai.
Khi cả bộ 404 test cùng chạy thì Chromium chậm hơn, và các mốc `wait_for_function`
đặt hạn 10 giây có thể không đủ.

**Chưa sửa, và cố ý chưa sửa.** Nới hạn chờ là giấu triệu chứng chứ không phải
chữa nguyên nhân, mà đóng băng mã là 04/09. Ghi vào đây để nếu nó đỏ lần nữa thì
người đọc biết đây là chuyện đã thấy, không phải chuyện mới.

**Nếu giám khảo hỏi:** trả lời đúng như trên — một test giao diện chập chờn do
thời gian chờ, đã tái hiện được là chỉ xảy ra khi chạy cả bộ, và phần chức năng
mà nó canh thì vẫn đúng.

### ✅ ĐÃ ĐÓNG (02/09) — lỗi 25: `set_window()` làm TREO HẲN app

Lộ ra **nhờ** bản vá lỗi 24. Học sinh chạy bản mới trên Windows: cửa sổ mở,
tiêu đề ghi **"(Not Responding)"**, giao diện hiện đúng câu tiếng Việt của bản
vá lỗi 24 — *"Không kết nối được với phần lõi chương trình"*. Tiến trình treo
thật, không phải chậm.

**Đây là lần đầu tiên đường CỬA SỔ GỐC chạy được.** Suốt những ngày trước app
toàn rơi xuống chế độ trình duyệt. Bản vá gỡ dấu "tải từ Internet" đã có tác
dụng — và ngay đó đụng một cái bẫy chưa ai gặp.

> ### ✅ ĐÃ XÁC NHẬN CHẠY ỔN ĐỊNH (02/09/2026)
>
> **Học sinh chạy bản có bản vá lỗi 25 trên máy Windows và xác nhận phần mềm
> chạy ổn định.** Hết treo, cửa sổ gốc mở và dùng được bình thường.
>
> Nguồn của khẳng định này là **học sinh xác nhận**, không phải một tệp
> `loi_khoi_dong.txt` do AI đọc. Ghi rõ như vậy để nếu giám khảo hỏi *"em biết
> bằng cách nào"* thì câu trả lời đúng là *"em tự chạy trên máy của em"* — một
> câu trả lời hợp lệ, và là câu trả lời thật.

**Nguyên nhân nằm trong mã của mình, không phải pywebview.** `main.py` gọi
`api.set_window(window)`, nên `PipelineAPI.window` giữ đối tượng `Window` của
pywebview. Rồi pywebview dựng cầu nối bằng cách **dò chính đối tượng API**
(`webview/util.py`, `get_functions`):

```python
for name in dir(obj):
    if name.startswith('_'): continue      # <- lối thoát DUY NHẤT
    attr = getattr(obj, name)              # <- KÍCH HOẠT property
    ...
    elif not callable(attr) and hasattr(attr, '__module__'):
        get_functions(attr, ...)           # <- ĐỆ QUY vào attr
```

`Window` không callable và có `__module__` → pywebview **đệ quy vào chính cửa
sổ của nó**. Mà `dir()` cửa sổ đó có bốn property CHẶN (`webview/window.py`):

```python
@property
def width(self):
    self.events.shown.wait(15)              # chờ tới 15 giây
    width, _ = self.gui.get_size(self.uid)  # đọc Control.Size của WinForms
```

`width`, `height`, `x`, `y` — mỗi cái chờ tới 15 giây, và `get_size` đọc thuộc
tính của một control WinForms **từ luồng khác luồng giao diện**. Truy cập chéo
luồng đó chính là thứ làm cửa sổ ghi *"Not Responding"*. Luồng dò bị chặn →
`finish.js` không bao giờ chạy → `window.pywebview.api` mãi rỗng.

**Đo được, không phải suy luận** (`tests/test_do_api.py`, bản chưa vá):

| Đo | Kết quả |
|---|---|
| Thuộc tính công khai bị đệ quy vào | `['window']` |
| Property của cửa sổ bị chạm tới | `['height', 'width', 'x', 'y']` — **đủ cả bốn** |

**Sửa:** đổi `self.window` → `self._window`, `set_window` → `_set_window`.
`get_functions` bỏ qua tên bắt đầu bằng `_` **trước khi** gọi `getattr`, nên cửa
sổ không hề bị chạm. Một dấu gạch dưới, và nó là **bắt buộc chứ không phải quy
ước cho đẹp** — chú thích trong `api.py` nói rõ vì sao, vì sáu tháng sau sẽ có
người thấy nó thừa mà bỏ đi.

> Đáng chú ý: `self.window` được **gán hai lần và không đọc ở đâu cả**. Một
> thuộc tính không ai dùng, làm treo cả ứng dụng.

**Chữa luôn một lỗi chẩn đoán đi kèm.** `main.py` ghi nhật ký
`"cua so goc (pywebview) mo THANH CONG"` **trước** `webview.start()` — mà chính
`start()` mới là chỗ treo. Nghĩa là đúng lúc app treo, `loi_khoi_dong.txt` vẫn
ghi "THÀNH CÔNG": nói dối đúng lúc cần sự thật nhất, và `chan_doan.py` sinh ra
là để chống chuyện đó. Giờ ghi `"dang mo cua so goc..."` trước và
`"da dong binh thuong"` sau, có test canh.

**Bài học cho lần sau, đáng ghi vào báo cáo:** bản vá lỗi 24 không tự sửa lỗi
này — nó **làm lỗi này nhìn thấy được**. Trước đó triệu chứng là một câu tiếng
Anh khó hiểu; sau đó là một câu tiếng Việt nói đúng chuyện gì đang xảy ra, kèm
tên tệp nhật ký. Đó là toàn bộ giá trị của việc báo lỗi tử tế.


### ✅ ĐÃ ĐÓNG (01/09) — lỗi 24: cổng khởi động hỏi sai câu hỏi

Triệu chứng học sinh báo: *"mới cài, mở lần đầu thì thường bị lỗi backend không
kết nối được"*. Câu đó khớp đúng một chuỗi có thật trong mã (`app.js`,
`callApi`): `` `Backend not ready yet (${name})` `` — và chuỗi này **không đi qua
`I18N`**, nên nó hiện thẳng bằng tiếng Anh vào giao diện tiếng Việt.

**Nguyên nhân đọc được từ mã nguồn pywebview 6.2.1 trong `.venv`, không phải suy
đoán.** pywebview **không** dựng `window.pywebview` trong một nhịp:

| Tệp | Việc |
|---|---|
| `webview/js/api.js` | `window.pywebview = { …, api: {} }` — **api RỖNG** |
| `webview/js/finish.js` | `_createApi(…)` rồi mới `dispatch pywebviewready` |

`webview/util.py`, `generate_js_object()` chạy hai nhịp đó bằng **hai lệnh
`run_js` tách rời, trên một luồng riêng, có phản chiếu Python xen giữa**. Trong
khe hở đó `window.pywebview` **đã có thật** mà gọi hàm nào cũng trượt. Trên
Windows việc này còn chạy **sau khi trang đã tải xong**
(`webview/platforms/edgechromium.py`, trong `on_navigation_completed`).

Cổng cũ chỉ hỏi `if (window.pywebview)` rồi hẹn giờ **một phát 300 ms**. Gọi T1 =
lúc nhịp 1 xong, T3 = lúc sự kiện bắn:

| | Điều kiện | Chuyện xảy ra |
|---|---|---|
| A | 300 ms < T1 | đúng — nhưng chỉ xảy ra khi máy **chậm** |
| **B** | T1 < 300 ms < T3 | `init()` chạy với **api rỗng** → `"Backend not ready yet"` |
| **C** | T3 < 300 ms | `init()` chạy **hai lần** — cờ `appInit` chỉ được đặt ở nhánh hẹn giờ, nên đường sự kiện không đánh dấu gì |

**Đo được cả bốn hậu quả** (`tests/test_khoi_dong_backend.py`, bản chưa vá):

| Đo | Kết quả |
|---|---|
| Ca B | `Không đọc được trạng thái tổng quan: Backend not ready yet (get_dashboard_status)` |
| Ca C | `init()` chạy **2 lần** |
| Nút đổi ngôn ngữ | bấm **một** cái, ngôn ngữ **không đổi** |
| Nút xoá hai bước | `reset_data` chạy **2 lần** |

Hai dòng cuối là vì cả **40** chỗ gắn sự kiện trong `app.js` đều dùng
`addEventListener`, **không chỗ nào** dùng `.onclick` (đã đếm) — khởi động hai
lần là **gắn đôi toàn bộ nút**. Nút đổi ngôn ngữ gọi `setLang` hai lượt
(vi→en→vi) nên **trông như chết**; `armTwoStepConfirm` sinh hai bao đóng, mỗi cái
một biến `armed` riêng, nên bấm lần hai là `onConfirmed()` chạy hai lượt.

> **Lỗi này giải thích luôn báo cáo "đổi ngôn ngữ bị giật" của phiên trước.** Lần
> đó đã sửa một nguyên nhân có thật (cất câu đã dịch), nhưng đây là nguyên nhân
> **thứ hai, độc lập** — và nó mới giải thích được phần "lúc được lúc không".

**Sửa:** tách `apiSanSang(name)` để cổng khởi động hỏi **chính** điều kiện mà
`callApi` đòi hỏi (hàm gọi được, không phải đối tượng tồn tại); thay hẹn giờ
một-phát bằng **hỏi vòng 50 ms, hạn 20 giây**; đặt cờ **ngay trong**
`khoiDongMotLan()` nên mọi đường vào đều qua nó; quá hạn thì báo bằng tiếng Việt
và **chỉ tên tệp `loi_khoi_dong.txt`** để lần sau không phải đoán. `recovery.js`
là **bản sao nguyên văn** của cùng cổng đó nên vá y hệt — riêng ở đó, gắn đôi làm
`start_fresh` (nút xoá sạch để bắt đầu lại) chạy hai lượt, **đã đo, đã đóng**.

Cố tình **không** nghe `pywebviewready` song song với hỏi vòng: điều kiện hỏi
vòng mạnh hơn sự kiện, và hai đường vào cho cùng một việc chính là cách lỗi này
sinh ra lần đầu.

**Vì sao 381 test không bắt được — quan trọng, đừng để người sau vấp lại:** mọi
test giao diện đều đi qua `browser_host.serve(...)`, mà `browser_host` chèn cầu
nối giả lập **trước `</head>`**, đồng bộ, `api` là Proxy luôn sẵn sàng. Nghĩa là
**không test nào từng chạy qua con đường người dùng Windows thật đi**. Có test
giao diện **không** đồng nghĩa với đã phủ đường khởi động. File test mới phục vụ
trang bằng `http.server` tĩnh rồi **mô phỏng đúng hai nhịp của pywebview** bằng
`add_init_script`, có kiểm soát thời điểm.

**Tác động lên kết quả đã công bố: không có.** Lỗi thuần tầng khởi động giao diện,
không đụng thuật toán.


### ✅ ĐÃ ĐÓNG (01/09) — lỗi 23: ô điểm nuốt mất dấu phẩy, `8,5` thành `85`

Tìm ra khi dò lại sau khi đã sửa lỗi 21–22. **Nặng hơn cả hai lỗi đó.**

Đo trong Chromium thật, cả locale `en-US` lẫn `vi-VN`:

```
Gõ "8,5" vào ô điểm  ->  .value === "85"
                         validity.valid === true
```

Ô điểm là `<input type="number">`. Trình duyệt **nuốt dấu phẩy** rồi **báo là hợp
lệ** — không gạch đỏ, không thông báo. Điểm bị nhân lên **10 lần**, im lặng.

Khác mọi lỗi điểm khác ở một chỗ quyết định: **không cần ai gõ nhầm.** `8,5` là
cách viết thập phân bình thường của tiếng Việt. Gõ đúng thói quen, máy hiểu sai.

**Nghịch lý ngay trong dự án:** nạp tệp Excel thì `8,5` lưu đúng thành 8.5, vì
`_doc_diem()` xử lý dấu phẩy và chú thích ghi rõ *"Excel bản tiếng Việt lưu 8,5"*.
Nhưng `submit_club_scores` gọi `float()` thẳng, không dùng hàm đó. Lại là
**"hai cửa, hai luật"** — cùng loại với lỗi 21.

**Sửa hai nửa:**

1. `app.js` — `type="number"` → `type="text"` + `inputMode="decimal"`. Trình duyệt
   hết cơ hội đụng vào dấu phẩy; máy cảm ứng vẫn hiện bàn phím số. Mất mấy nút
   mũi tên tăng/giảm, với kiosk thì không tiếc. `.score-input` không có luật CSS
   nào phụ thuộc `type=number` (đã soát).
2. `api.py` — `submit_club_scores` dùng `_doc_diem()` thay `float()`. Sau đó hai
   cửa cùng một luật: `8,5` và `8.5` đều đúng, `abc` sai ở cả hai. `_doc_diem`
   còn chặt hơn `float()` ở chỗ loại `inf`/`nan`.

**Vì sao 363 test không bắt được:** tầng Python **mù hoàn toàn** — API chưa bao
giờ nhìn thấy dấu phẩy, vì trình duyệt đã xoá trước khi gửi. API nhận `"85"` và
lưu đúng `85`. Chỉ Chromium thật mới thấy. Đây là file test giao diện thứ **năm**
của dự án, và là lần thứ ba trong ngày một lỗi chỉ lộ ra ở trình duyệt.

`tests/test_giao_dien_cham_diem.py` kiểm **giá trị trong CSDL**, không kiểm
`.value` của ô — chính `.value` là chỗ lỗi ẩn nấp. Chạy với bản chưa vá: 3 test
đỏ, và một test cho thấy gõ `7,5` lưu ra **75,0**.

**Tác động lên kết quả đã công bố: không có.** Mọi bộ dữ liệu nạp qua tệp, không
qua màn hình chấm điểm.


### ✅ ĐÃ ĐÓNG (01/09) — lỗi 21 và 22: điểm không có chốt chặn nào

Lỗi duy nhất còn lại có thể làm **sai người trúng tuyển**. Đo trên bộ ví dụ 10 em,
gõ `70` thay vì `7.0` cho HS10:

| Em | Trước | Sau |
|---|---|---|
| HS10 | *(chưa xếp)* | **CLB Bóng rổ** |
| HS02 | CLB Bóng rổ | **CLB Mỹ thuật** |
| HS08 | CLB Mỹ thuật | **CLB Nấu ăn** |

**Một lỗi gõ, ba em đổi chỗ** — em bị đẩy ra lại đi đẩy em khác. Và 0 cảnh báo.

**Lỗi 21 — hai cửa, hai luật.** Cùng giá trị `-9`: đường nạp tệp từ chối
(`csv_score_negative`), màn hình Chấm điểm **nhận**. Bắt được hay không tuỳ giáo
viên đi cửa nào. Nay `submit_club_scores` từ chối điểm âm, mã lỗi `score_negative`,
và **điểm cũ không bị ghi đè** — có test canh riêng chỗ đó.

**Lỗi 22 — không có quy tắc nào soát điểm bất thường.** Nay có quy tắc rà soát
thứ 8: so mỗi điểm với **trung vị của chính CLB đó**.

> **KHÔNG đặt trần cứng ở 10.** Trường có thể chấm thang 100, chặn cứng là chặn
> nhầm. So với trung vị thì thang nào cũng đúng, và bắt được cả hai phía.

**Ngưỡng 3,0 chọn bằng số đo, không phải cảm tính:**

| | |
|---|---|
| Tỉ lệ (điểm cao nhất / trung vị) trong một CLB — cao nhất trên **579 ô điểm thật** | **1,42** |
| Tỉ lệ khi gõ lệch dấu chấm | **≈ 10** |
| Quét thử hệ số 1,5 | **11 cảnh báo giả** |
| Quét thử hệ số 2,0 · 2,5 · 3,0 | **0 cảnh báo giả** |

Lấy 3,0 để cách ca thật tệ nhất 2,1 lần mà vẫn thừa sức bắt lỗi gõ. Bắt được
`70`, `85` và `0.85`; không báo với `6.0` (điểm thấp thật) và không báo với
trường chấm thang 100. CLB dưới 3 điểm thì bỏ qua — chưa có phân bố nào để so.

**Tác động lên kết quả đã công bố: không có.** Lỗi 21 chỉ từ chối thứ chắc chắn
sai (không bộ dữ liệu nào có điểm âm); lỗi 22 chỉ **thêm cảnh báo**, không chặn
ai chạy. Cả hai bộ dữ liệu vẫn **0 cảnh báo**, kết quả không đổi một dòng.

**Còn lại không sửa được:** một điểm sai *vừa phải* — 9 thay vì 8 — thì không
cách nào phát hiện. Đã ghi vào mục *Giới hạn đã biết* của hướng dẫn.


### ✅ ĐÃ ĐÓNG (01/09) — lỗi 19: bốc thăm phụ thuộc THỨ TỰ NHẬP học sinh

Học sinh hỏi *"chạy trên máy khác có ra cùng kết quả không?"* — hỏi đúng chỗ hiểm.

`load_from_sqlite` đọc `SELECT student_id, stb_number, reserve_group FROM students`
**không có `ORDER BY`**. Truy vấn cần cột ngoài chỉ mục nên SQLite quét bảng, trả
về theo **thứ tự chèn**. `generate_stb_lottery` rồi `shuffle` đúng danh sách đó,
mà `shuffle` phụ thuộc thứ tự đầu vào.

| Thử nghiệm (10 em điểm bằng nhau, `seed=42`) | Kết quả |
|---|---|
| Chèn HS01→HS10 vs HS10→HS01, **trước bản vá** | **6/10 em khác CLB** |
| Cùng thử nghiệm, **sau bản vá** | **0 em khác** |

Chữa bằng **một dòng**: `sorted(student_ids)` trước khi xáo, đặt **trong hàm**
`generate_stb_lottery` chứ không ở chỗ gọi — chính hàm đó hứa *"seed cố định để
tái lập kết quả khi kiểm tra/audit"*, nên nó phải tự giữ lời hứa, và hàm có hai
chỗ gọi.

**Không đổi bản chất thuật toán.** RB-DA không sửa dòng nào. Xáo trên danh sách
đã sắp vẫn cho hoán vị ngẫu nhiên đều — đo được: `HS01` nhận số 9/12, số 0 rơi
vào `HS08`. Đã đo trên hai bộ dữ liệu đã công bố: **0 em đổi CLB**, bảng trong
hướng dẫn khớp từng dòng.

> **Câu chữ cho báo cáo — chỗ này rất dễ nói sai:**
> **KHÔNG viết** "số bốc thăm dựa trên mã học sinh" — nghe như em tên A có lợi
> hơn em tên Z, và không đúng.
> **Viết đúng:** *bốc thăm không phụ thuộc thứ tự nhập liệu*. Mã học sinh chỉ
> dùng để danh sách đầu vào luôn ở một trật tự cố định; xáo xong thì mã không
> còn vai trò gì.

### ✅ ĐÃ ĐÓNG (01/09) — lỗi 20: biểu đồ lấp đầy chưa bao giờ vẽ được thanh chính

Học sinh gửi ảnh: CLB đầy **14/14** mà máng trắng trơn, còn đúng 4 CLB có suất
dự trữ thì hiện một đoạn vàng ngắn.

`.fill-bar` là `<span>` mà CSS chỉ đặt `height` và `background`, **không đặt
`display`**. `width`/`height` **không áp dụng cho phần tử inline** → thanh không
có kích thước. Đoạn dự trữ vẽ được **chỉ vì** JS gắn `position:absolute` nội
tuyến, mà absolute thì bị ép thành block.

Đo trong Chromium thật, trước bản vá:

| CLB | Số | Thanh chính |
|---|---|---|
| Âm nhạc | 14/14 | `display:inline`, css `100%` → **vẽ ra 0 px** |
| Khoa học | 5/10 | `display:inline`, css `50%` → **vẽ ra 0 px** |

Ba việc đi cùng nhau:

1. **Máng thành `display:flex`** — con của flex tự động thành block, nên không
   đoạn nào có thể rơi lại vào inline. Chọn flex thay vì thêm `display:block` là
   có chủ ý: triệt **cả lớp lỗi**, không chỉ ca đang gặp.
2. **`get_club_fill_stats` trả thêm `matched_reserve`** — số em **thực sự** vào
   bằng suất dự trữ. Bản cũ vẽ theo `reserve_capacity`, tức chỉ tiêu của CLB,
   một thuộc tính của CLB chứ không phải điều đã xảy ra.
3. **Vẽ hai đoạn liền nhau**, không chồng mờ: vàng = vào bằng dự trữ, xanh = vào
   ở chỉ tiêu chung, cộng lại đúng bằng tỉ lệ lấp đầy in bên phải.

Chú giải cũng sai theo nên sửa: *"Có suất dự trữ"* → *"Vào bằng suất dự trữ"*.

Đo lại trên bộ 140 em: mọi thanh khớp con số của nó, và bốn đoạn vàng cộng lại
đúng **16 em** — bằng số em vào bằng dự trữ đã ghi trong tài liệu.

**Vì sao sống sót lâu vậy:** `test_api.py` và `test_kich_ban_nhap_tay.py` có gọi
`get_club_fill_stats`, và **API luôn trả về đúng số**. Sai nằm ở tầng CSS, nơi
tầng Python mù hoàn toàn — y hệt lỗi i18n cùng ngày. Nay có
`tests/test_giao_dien_bieu_do.py` đo **bề rộng vẽ ra thật**
(`getBoundingClientRect`), không đo thuộc tính CSS: chính `width:100%` mà vẽ ra
0 px là cái bẫy đã giấu lỗi này từ đầu.


### ✅ ĐÃ ĐÓNG (01/09) — lỗi đổi ngôn ngữ ở ô nạp tệp

Học sinh báo "chuyển tiếng Việt/tiếng Anh bị lỗi". Dò bằng Chromium thật, quét cả
5 tab và đối chiếu 145 cặp chuỗi vi/en: **đổi tab bình thường không sót chuỗi
nào**. Lỗi chỉ hiện ở những trạng thái **đang dang dở**, và đúng ở khu vực người
dùng chạm vào đầu tiên.

| # | Tái hiện | Hiện tượng |
|---|---|---|
| 16 | Thả tệp → đổi ngôn ngữ | Hàng chờ vẫn ghi *"Nhận diện: Danh sách CLB"* |
| 17 | Nhập xong → đổi ngôn ngữ | Tóm tắt vẫn ghi *"Xong: 5 CLB mới…"* |
| 18 | Nút xoá đang chờ xác nhận → đổi ngôn ngữ | Nút vẫn ghi *"Bấm lần nữa để xoá…"* |

**Nguyên nhân chung, và đây là phần đáng viết vào báo cáo:** mã **dịch một lần
rồi cất câu đã dịch**. Vẽ lại bao nhiêu lần cũng ra nguyên tiếng cũ. Chữa bằng
cách cất **khoá + tham số**, gọi `t()` lúc vẽ — đúng khuôn mẫu `lastRenderedSteps`
đã dùng cho stepper từ trước, không nghĩ cách mới.

Lỗi 18 vốn **do thiết kế**: `applyStaticText()` cố ý bỏ qua phần tử
`.is-confirming` để nhãn không lệch khỏi trạng thái bên trong. Lý do đúng, cách
xử lý sai — nay **nhả hẳn nút** ra khi đổi ngôn ngữ.

`tests/test_giao_dien_doi_ngon_ngu.py` (4 test, Chromium thật). **Đã chạy thử với
bản chưa vá: 3 test đỏ.** Bản test đầu tiên của tôi xanh giả vì hạn chờ 8 giây
rộng hơn bộ đếm tự nhả 4 giây của chính nút — siết xuống 1,5 giây mới bắt được.
Test thứ tư là lưới an toàn cho tương lai, xanh cả hai bên là đúng.


### ✅ ĐÃ ĐÓNG (01/09) — hai lỗi lộ ra khi học sinh chạy thử bộ sạch

Học sinh nạp bộ `bo_sach/` (bộ được thiết kế để **không** sinh cảnh báo nào) rồi
vẫn thấy **1 cảnh báo nghiêm trọng**. Truy ra hai lỗi khác nhau.

**Tái hiện được, và đây là số đo:** nạp `TEST_01..04` (có file lỗi cố ý) rồi
chồng bộ sạch lên, không xoá gì → CSDL có **148** học sinh thay vì 140, còn đúng
**1 cảnh báo**, và chạy phân bổ ra **143/148** chứ không phải 140/140.

| # | Lỗi | Chữa thế nào |
|---|---|---|
| 14 | Cảnh báo "nhãn dự trữ không club nào dùng" nói có gõ sai chính tả nhưng **không nói em nào**. Hai cảnh báo ngay trên nó đều kèm mã học sinh; mục này bị bỏ sót | Thêm `sample` (tối đa 5 mã, đã sắp xếp) vào `get_data_health_report()` mục 4, và bổ sung câu chỉ đường tới chỗ chữa |
| 15 | **Không có đường nào trong app đưa dữ liệu về trống.** Nạp file cộng thêm học sinh, không bao giờ xoá — đúng như phải thế, nhưng khi đó cách duy nhất làm lại từ đầu là đóng app rồi đổi tên `app.db` ngoài File Explorer, việc không ai tìm ra | `reset_data(pham_vi, xac_nhan)` + khối **Vùng nguy hiểm** cuối tab Quản lý |

Lỗi 15 nguy hiểm ở chỗ **im lặng**: học sinh của lần chạy trước vẫn chiếm suất và
làm lệch kết quả mà không có dấu hiệu nào.

**Ba điều `reset_data()` bắt buộc làm, và lý do:**

1. **Kiểm tra xác nhận TRƯỚC, sao lưu SAU.** Đảo lại thì mỗi lần gọi nhầm vẫn đẻ
   ra một tệp `.bak` rác. Có test canh riêng cho thứ tự này.
2. **Tự sao lưu** bằng `_backup_db()` đã có sẵn (SQLite Backup API, không copy
   tệp thô). Test mở bản sao lưu ra đếm lại, chứ không chỉ kiểm tra tệp tồn tại.
3. **Mở khoá STB.** Bỏ qua thì lần chạy sau ghi nhật ký là "tái sử dụng STB" cho
   một bộ số bốc thăm không còn tồn tại — sai cho phần kiểm toán.

**Không xoá `run_history`** ở bất kỳ phạm vi nào: lược đồ ghi rõ bảng đó "không
bao giờ xoá/ghi đè". Xoá dữ liệu không được phép xoá dấu vết.

Sau bản vá, đúng tình huống trên: xoá → nạp lại → **0 cảnh báo, 140/140**.
`tests/test_bo_sach.py` khoá cả hai vế (khẳng định lỗi có thật, rồi khẳng định
bản vá chữa được), và `tests/test_giao_dien_xoa_du_lieu.py` mở Chromium thật để
bắt lỗi đặt nhầm bảng i18n — loại lỗi chỉ lộ ra ở trình duyệt.

### ✅ ĐÃ ĐÓNG (31/08) — lỗi `.exe` Windows, lỗi cũ nhất của dự án

Mở từ 27/08, đóng ngày 31/08. **Nguyên nhân gốc không nằm trong mã nguồn.**

```
RuntimeError: Failed to resolve Python.Runtime.Loader.Initialize
from ...\_internal\pythonnet\runtime\Python.Runtime.dll
```

**Nguyên nhân thật:** Windows gắn dấu "tải từ Internet" (luồng NTFS
`Zone.Identifier`) vào **mọi tệp** giải nén từ `.zip` tải về, và .NET Framework
**từ chối nạp assembly mang dấu đó**. Vì thế thông báo lỗi nêu rõ đường dẫn — tệp
CÓ ở đó, .NET tìm thấy, chỉ là không chịu nạp.

**Bằng chứng từ máy học sinh** (`loi_khoi_dong.txt`):

```
[2026-08-31 15:34:42] go dau tai-ve trong ...\_internal:
                      {'da_go': 173, 'bo_qua': 0, 'loi': 0}
[2026-08-31 15:34:42] cua so goc (pywebview) mo THANH CONG
```

Đọc kỹ ba con số đó:
- `da_go: 173` — 173 tệp mang dấu, mã tự gỡ hết
- **`bo_qua: 0`** — không một tệp nào sạch sẵn, tức học sinh **KHÔNG** unblock tay;
  chính mã làm. Nghĩa là nó tự chạy trên **máy bất kỳ**, kể cả máy giám khảo.
- Dòng thứ ba **KHÔNG** chứng minh pywebview mở thành công — xem ngay dưới.

> **SỬA LẠI (02/09) — dòng `mo THANH CONG` đã bị đọc quá tay.**
> `main.py` ghi dòng đó **trước** khi gọi `webview.start()`, mà `start()` mới là
> chỗ thật sự mở cửa sổ. Nên nó chỉ chứng minh *mã chạy tới được lời gọi đó*,
> chứ không chứng minh cửa sổ mở được. Bằng chứng: ngày 02/09, đúng bản build
> ghi "THANH CONG" lại treo với tiêu đề **"(Not Responding)"** (lỗi 25, mục 5).
> `main.py` giờ ghi `"dang mo cua so goc..."` trước và
> `"da dong binh thuong"` sau, có test canh (`tests/test_do_api.py`).
>
> **Điều bản vá gỡ dấu THẬT SỰ chứng minh:** phần gỡ `Zone.Identifier` chạy
> đúng (173 tệp, tự động, không cần thao tác tay) — và nhờ đó pywebview mới đi
> được xa tới mức tạo được cửa sổ, thay vì chết ngay lúc `import webview` như
> trước. Đó là tiến bộ có thật, chỉ là chưa phải "chạy được".
>
> **Chốt lại (02/09, sau bản vá lỗi 25):** giờ thì *đã* chạy được — học sinh
> xác nhận app chạy ổn định trên Windows. Nhưng bài học về dòng log vẫn giữ
> nguyên giá trị: **một dòng log ghi trước lời gọi không chứng minh lời gọi đó
> thành công.** Đừng lặp lại lỗi đọc quá tay này ở chỗ khác.

Task Manager xác nhận: `PhanBoCauLacBo.exe` là tiến trình riêng; nhóm
`msedgewebview2.exe` (WebView2 Runtime) vẽ nội dung **bên trong** cửa sổ của nó.

**Câu chữ đúng cho báo cáo tính đến 02/09:** cả **hai** đường hiển thị đều đã
chạy được trên Windows. Chế độ dự phòng bằng trình duyệt xác nhận 30/08; **cửa
sổ gốc** — đường ưu tiên trong mã — xác nhận **02/09** sau bản vá lỗi 25, học
sinh chạy trên máy mình và báo lại là **chạy ổn định**.

Viết được: *phần mềm chạy ổn định trong cửa sổ ứng dụng của riêng nó trên
Windows*. Vẫn **không** được viết *"không dùng gì của Microsoft"* — xem khối câu
chữ nguyên văn ở cuối mục này.

**Cách chữa — hai lớp, xem `chan_doan.py`:**
1. `go_dau_tai_ve()` xoá luồng `Zone.Identifier` khỏi mọi `.dll/.exe/.pyd` trong
   gói, chạy **TRƯỚC** `import webview`. Không cần quyền Administrator.
   **Đảo thứ tự là mất tác dụng hoàn toàn** — có test canh (`test_chan_doan.py`).
2. `PhanBoCauLacBo.exe.config` với `loadFromRemoteSources enabled="true"` — bảo
   .NET bỏ qua dấu ngay từ đầu. Phải nằm **cạnh** `.exe`, không phải trong
   `_internal/`.

### Vì sao ba phiên trước không tìm ra — phần đáng viết vào báo cáo

Lỗi thật không phải pywebview hỏng, mà là **hỏng mà không ai biết vì sao**:
`main.py` ghi vết lỗi ra `sys.stderr`, còn bản `console=False` **không có stderr**.
Bằng chứng bị vứt đi đúng lúc nó xảy ra. Ba phiên phải ĐOÁN, và đoán sai hai lần:

- **Lần 1 — đổ cho UPX.** Sai: máy build GitHub chưa bao giờ cài UPX.
- **Lần 2 — đổ cho thiếu tệp pythonnet.** Sai: hook chính thức đã chạy sẵn ở bản
  lỗi; log build run `33124799256` cho thấy build THÀNH CÔNG, `pythonnet 3.1.0`,
  `clr_loader 0.3.1`, `pywebview 6.2.1` đều có mặt.
- **Truy được chỗ ném lỗi:** `clr_loader/netfx.py` dòng 46–49, khi
  `pyclr_get_function` trả NULL. Đúng chỗ, nhưng vẫn không biết TẠI SAO.

Chỉ khi **ghi vết lỗi ra tệp** thay vì stderr thì mới kiểm chứng được giả thuyết
thay vì đoán tiếp. Bài học đáng viết: *thứ hỏng trước tiên không phải tính năng, mà
là khả năng biết được tính năng đã hỏng thế nào.*

### Câu chữ ĐÚNG cho báo cáo — dùng nguyên văn

> **Được viết:** phần mềm chạy trong cửa sổ ứng dụng của riêng nó; nội dung được vẽ
> bằng WebView2 Runtime — một thành phần có sẵn của Windows 10/11.
>
> **Được viết (mới 02/09):** phần mềm **chạy ổn định** trên máy Windows ở chế độ
> cửa sổ gốc. Nguồn: học sinh tự chạy và xác nhận.
>
> **Được viết:** lỗi đóng gói đã tìm ra nguyên nhân gốc và đã chữa.
>
> **KHÔNG được viết:** *"không dùng gì của Microsoft"* — WebView2 là của Microsoft.
> Nói đúng là **dùng thành phần hệ điều hành**, không phải **chạy trong trình duyệt**.

### ĐÃ ĐO, KHÔNG PHẢI LỖI — vài em có suất hay không phụ thuộc bốc thăm (02/09)

**Đọc mục này trước khi định "sửa" nó.** Ghi vào đây vì nó *trông* như lỗi, và
người đọc sau — hoặc chính học sinh khi bị giám khảo hỏi — rất dễ tưởng là lỗi.

**Số đo** (`du_lieu_test/do_anh_huong_seed.py`, 200 seed, ba bộ dữ liệu):

| Bộ | Luôn có suất | Luôn không | **Phụ thuộc bốc thăm** |
|---|---|---|---|
| `vi_du_huong_dan/` (10 em) | 9 | 1 | **0 (0,0%)** |
| `bo_sach/` (140 em) | 139 | 0 | **1 (0,7%)** |
| `TEST_0*` (120 em) | 107 | 11 | **2 (1,7%)** |
| **Gộp (270 em)** | | | **3 (1,1%)** |

**Vì sao đây KHÔNG phải lỗi.** Khi hai em bằng điểm nhau tranh một chỗ, phải có
gì đó phân định. Mọi phương án khác đều **thiên vị có hệ thống**: thứ tự nhập thì
ai nộp sớm luôn thắng; mã học sinh thì em mã nhỏ luôn thắng — **cùng một người
được lợi ở mọi CLB, năm này qua năm khác**. Bốc thăm không thiên vị ai. Đây là
lựa chọn thiết kế của cả họ thuật toán Gale–Shapley, không phải thiếu sót của
bản cài đặt này.

**Ba điều SẼ đáng lo — đã đo, đều không xảy ra:**

| Nếu | Đo được |
|---|---|
| Seed lật kết quả của em **điểm khác nhau** | **Không.** 3 em 3 điểm khác nhau, 100 seed, cùng kết quả (`tests/test_anh_huong_seed.py`) |
| Seed phá tính ổn định | **Không.** 0 cặp phá vỡ / 200 seed / 3 bộ |
| Bốc thăm thiên vị một em | **Không.** Hai em hoà điểm tranh một suất: cả hai đều từng thắng |

**Rủi ro THẬT, và nó đã được chặn sẵn — đừng gỡ:** vì seed *có* đổi số phận vài
em, việc bốc lại nhiều lần rồi chọn kết quả vừa ý là rủi ro liêm chính thật sự.
Ba lớp đang giữ:

1. `stb_lock` khoá bộ số sau lần chạy đầu (`api.py`, `run_pipeline`).
2. Bốc lại phải bật cờ `force_redraw_stb` — hành động cố ý, không lỡ tay được.
3. **`run_history` ghi thêm một dòng mỗi lần chạy**, kèm `seed` và cờ
   `stb_redrawn`. Bảng này **không bao giờ ghi đè**, và `reset_data` **không
   đụng tới** (đã kiểm). Ai dò seed đẹp để lại dấu vết không xoá được.

> Ba lớp này là lý do 1,1% ở trên chấp nhận được. **Gỡ bất kỳ lớp nào là biến
> một tính chất thành một lỗ hổng.**

**Điều đáng làm nhất lại là chuyện vận hành, không phải mã:** trong ba em phụ
thuộc bốc thăm, một em (`HS037`) chỉ đăng ký **2 nguyện vọng** và có **46%** khả
năng không có suất nào. Đã ghi vào `HUONG_DAN_SU_DUNG.md` mục 13.

> ### ⚠️ CẢNH BÁO DIỄN GIẢI — dễ sai, và sai thì hỏng cả lập luận
>
> Từ số đo trên rất dễ nhảy sang kết luận **"vậy bắt học sinh điền tối đa số
> CLB"**. Đó là kết luận **SAI**, và nó phá đúng tính chất làm nên giá trị của
> thuật toán này.
>
> DA phía học sinh đề nghị là **strategy-proof**: khai đúng nguyện vọng thật là
> chiến lược tối ưu, không ai lợi được nhờ khai gian. Tính chất đó chỉ đúng khi
> danh sách là nguyện vọng **THẬT**. Bắt một em khai thêm CLB em không muốn thì:
>
> 1. Em có thể **bị xếp đúng vào CLB đó** — với em, tệ hơn không có suất.
> 2. Trường **mất dữ liệu nguyện vọng thật**, nên không còn biết học sinh thật
>    sự muốn gì.
> 3. Bản thân số đo cũng không đỡ được kết luận đó: thí nghiệm ở trên **CẮT BỚT**
>    nguyện vọng của em vốn đã khai đủ, tức nó đo *"em mất gì khi không khai hết
>    những CLB mình VẪN CHẤP NHẬN"*. Nó **không** đo chuyện thêm CLB em không
>    muốn.
>
> **Câu đúng:** khuyến khích học sinh khai hết những CLB em **thật sự chấp nhận**
> — an toàn chính vì thuật toán strategy-proof. **Câu sai:** bắt điền cho đủ số ô.
>
> Và "không có suất" **không phải lúc nào cũng là thất bại**: em chỉ muốn 2 CLB,
> cả hai hết chỗ, thì không có suất là câu trả lời trung thực.
>
> *(Tính chất strategy-proof của DA là định lý đã có trong tài liệu chuyên ngành.
> Tìm và trích dẫn nguồn là việc của học sinh — AI không tìm trích dẫn hộ, theo
> quy định ở mục 6.)*

**Hai điều CỐ Ý không kết luận:**
- Ranh giới này **không đoán trước được bằng bảng điểm**. `HS122` ở `clb_tinhoc`
  có 34 em điểm cao hơn tranh 14 chỗ — nhìn tĩnh thì đứng ngoài rất xa, nhưng
  phần lớn 34 em đó đỗ nguyện vọng trên của họ nên ranh giới thật tụt xuống tới
  em. Ranh giới sinh ra từ **chuỗi dây chuyền**, không từ bảng điểm. Đã viết một
  bộ dò ranh giới tĩnh để thử: **không bắt được ca nào**.
- ~~"Nguyện vọng càng ngắn càng dễ bấp bênh"~~ — **ĐÃ ĐO (02/09), và phỏng đoán
  này SAI một nửa.** Thí nghiệm đối chứng (`du_lieu_test/do_do_dai_nguyen_vong.py`):
  cùng bộ sạch, cắt danh sách nguyện vọng của mọi em xuống k = 1..6, 50 seed mỗi mức.

  | Cắt còn | Em **chưa được xếp** (TB) | Em **bấp bênh** |
  |---|---|---|
  | 1 nguyện vọng | **48,0** | 2 (1,4%) |
  | 2 nguyện vọng | 26,2 | 7 (5,0%) |
  | 3 nguyện vọng | 14,8 | 3 (2,1%) |
  | 4 nguyện vọng | 7,5 | 3 (2,1%) |
  | 5 nguyện vọng | 1,2 | 4 (2,9%) |
  | 6 nguyện vọng | **0,3** | 1 (0,7%) |

  Danh sách dài hơn giảm **rất mạnh và rất đều** nguy cơ **không có suất**
  (48 → 0,3). Nhưng với **bấp bênh** thì **không có quy luật nào** — 1,4 / 5,0 /
  2,1 / 2,1 / 2,9 / 0,7, nhảy loạn. Đây là hai hiện tượng khác nhau, đừng gộp.

Số liệu đầy đủ: `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` mục 3c.


### ĐÃ ĐO, KHÔNG PHẢI LỖI — kết quả ổn định nhưng không tối ưu Pareto (03/09)

**Đọc mục này trước khi định "sửa" nó.** Học sinh hỏi thẳng câu này (dán vào một
đoạn giải thích về *tie-breaking* trong DA, nói rằng phá hoà bằng bốc thăm làm
mất tối ưu Pareto). Câu trả lời dưới đây là **đo được**, không phải trả lời bằng
trí nhớ — và **kết quả đo bác một nửa đoạn văn đó**.

**Hiện tượng có thật:**

> **Cặp đôi cùng có lợi** — em `s1` xếp CLB `c1`, em `s2` xếp CLB `c2`, mà `s1`
> thích `c2` hơn **và** `s2` thích `c1` hơn. Đổi chỗ thì **cả hai cùng lên**
> nguyện vọng cao hơn. Thuật toán không cho, vì đổi như vậy phá tính ổn định.

**KHÔNG được gọi đây là "cặp phá vỡ".** Cặp phá vỡ gồm 1 học sinh + 1 **câu lạc
bộ** và nghĩa là kết quả **sai**; phần mềm đo được **0 cặp phá vỡ ở mọi seed**.
Cặp đôi cùng có lợi gồm 2 **học sinh** và nghĩa là kết quả **không tối ưu
Pareto** — đánh đổi đã biết của cả họ thuật toán ghép cặp ổn định. Lẫn hai chỗ
này là mất điểm ngay.

**Số đo** (`du_lieu_test/do_danh_doi_on_dinh.py`, seed mốc 42):

| Bộ | Cặp phá vỡ | Cặp đôi cùng có lợi | Số em dính | Bốc thăm CÓ phần | Bốc thăm VÔ CAN |
|---|---|---|---|---|---|
| `vi_du_huong_dan/` (10 em) | 0 | **0** | 0 | — | — |
| `bo_sach/` (140 em) | 0 | **85** | 34 (24,3%) | 18 (21%) | **67 (79%)** |
| `TEST_0*` (120 em) | 0 | **19** | 16 (13,3%) | 2 (11%) | **17 (89%)** |

Quét 40 seed: `bo_sach/` 82 · TB 91,0 · 103, **0/40 seed cho 0 cặp**; `TEST_0*`
19 · TB 21,5 · 24, **0/40**.

**Vì sao KHÔNG quy được cho bốc thăm — thí nghiệm đối chứng.** Bỏ điểm của `p%`
số cặp (em, CLB) để đẩy các em đó xuống **Tầng 2**, nơi bốc thăm quyết định
**hoàn toàn**. Nếu bốc thăm sinh ra tổn thất thì số cặp phải **tăng**:

| Bỏ điểm | `bo_sach` (TB) | `TEST_0*` (TB) |
|---|---|---|
| 0% (giữ nguyên) | **90,2** | **21,1** |
| 100% (bốc thăm quyết định tất cả) | **4,1** | **2,2** |

Ngược hẳn. Và ở mức bỏ hết điểm, `TEST_0*` có **3/10 seed cho 0 cặp** — tức có
lần đạt tối ưu Pareto, chuyện **không xảy ra lần nào** khi điểm còn nguyên.

> ### ⚠️ CẢNH BÁO DIỄN GIẢI — hai kết luận sai dễ nhảy sang
>
> **SAI 1 — "vậy phải bỏ bốc thăm đi".** Số đo **không** đỡ kết luận đó. Bốc thăm
> vô can trong **79–89%** số cặp, và khi cho bốc thăm toàn quyền thì số cặp
> **giảm** chứ không tăng. Bỏ bốc thăm cũng không có gì thay thế: hai em hoà điểm
> vẫn phải có cách phân định, và mọi cách khác đều thiên vị có hệ thống (xem khối
> "ĐÃ ĐO, KHÔNG PHẢI LỖI" ở trên).
>
> **SAI 2 — "vậy phần mềm sai".** Không. `verify_stability` canh đúng cái phải
> canh (0 cặp phá vỡ). Việc còn cặp đôi cùng có lợi là **hệ quả của việc giữ tính
> ổn định**, không phải lỗi cài đặt.
>
> **Câu đúng, ngắn gọn:** tổn thất đến từ chỗ **CLB có ưu tiên thật (điểm thi)
> không trùng với nguyện vọng học sinh** — không phải từ việc phá hoà.

**Hai giới hạn của phép đo, ghi để không trích thiếu:**

- Các mức **ở giữa** của thí nghiệm (25/50/75%) **không đi một chiều** — chỉ hai
  đầu bảng mới đọc ra được. Đừng viết *"càng nhiều Tầng 2 càng ít cặp"*.
- Trên ba bộ này **Tầng 2 rất hiếm khi giữ suất**: `bo_sach/` chỉ có **8** em giữ
  suất ở CLB mình không thi, `TEST_0*` có **0**. Nên cả 18 và 2 cặp *"bốc thăm có
  phần"* đều đến từ **hoà điểm**, không từ Tầng 2. Thí nghiệm đối chứng tồn tại
  chính vì lý do đó — nó tạo ra Tầng 2 mà dữ liệu gốc không có.

Có **24 test canh** (`tests/test_danh_doi_on_dinh.py`). Nới hàm tìm cặp cho lỏng
ra thì **3 test đỏ**; phá hàm quy nguyên nhân thì thêm test đỏ nữa — đã thử.

> **AI không kết luận hộ.** Bộ đo **ĐẾM** cái giá. Cái giá đó có chấp nhận được
> không, có nên đổi cơ chế không, nên nói gì với học sinh về nó — **học sinh tự
> viết** (Phụ lục 1, mục 6).

Số liệu đầy đủ: `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` mục 3d và
`docs/CO_CHE_THUAT_TOAN.md`.


### ĐÃ SỬA (05/09) — em vào sau luôn xếp CUỐI, và tài liệu đang hứa ngược lại

**Phát hiện thế nào.** Học sinh hỏi *"bốc thăm có vấn đề gì không"*. Đọc lại mã
thì thấy nhánh vẽ bổ sung cấp cho em mới số bắt đầu từ `MAX(stb_number)+1`. Ghi
chú trong mã nói mục đích là *"tránh trùng số"* — **không nhắc gì tới hệ quả**.

Mà **số nhỏ = ưu tiên cao** (`compute_club_priority`: *"bằng điểm → STB tăng
dần"*, Tầng 2 *"thuần STB tăng dần"*). Nên cách đó đặt em mới **sau MỌI em cũ, ở
MỌI câu lạc bộ, vĩnh viễn**.

**Đo được, không phải suy luận.** 20 em cũ + 10 em mới tranh 10 suất, tất cả đều
Tầng 2 nên thứ tự hoàn toàn do bốc thăm:

| | Em mới giành được suất |
|---|---|
| Cách cũ (`MAX+1`) | **0** — ở mọi seed |
| Công bằng thì kỳ vọng | ~3,3 |
| Sau khi sửa (20 seed) | ít nhất 2 · **TB 3,5** · nhiều nhất 5 |

Không phải "hơi thiệt". Với nhóm đó **bốc thăm không còn tồn tại**.

**Vì sao bắt buộc phải sửa, chứ không phải chỉ ghi chú lại.**
`HUONG_DAN_SU_DUNG.md` bước 4 đang hứa nguyên văn: *"Em `HS01` không hề có lợi
thế nào so với em cuối danh sách."* Câu đó **sai** với mọi em thêm vào sau — tài
liệu đang nói một điều phần mềm không làm. Ba đường thêm học sinh đều dẫn vào đây
(`api.py` dòng 1393, 1533, 2317 — tất cả ghi `stb_number = NULL`), và mục 8 của
hướng dẫn tồn tại **đúng để phục vụ em nộp muộn**.

**Đã làm gì.** Thêm `chen_stb_cho_hoc_sinh_moi` cạnh `generate_stb_lottery`
(`rbda_priority_pipeline.py`): chọn ngẫu nhiên `k` vị trí trong `n+k` chỗ cho em
mới, phần còn lại giữ nguyên thứ tự cũ. `sorted()` trước khi xáo — **cùng hạng
lỗi với lỗi 19**, không sắp thì thứ tự nhập liệu lại lén quyết định.

> **KHÔNG phải thay đổi thuật toán.** Không sửa một dòng nào trong năm hàm
> (`compute_club_priority`, `club_choice_function`, `run_rbda`,
> `verify_stability`, `generate_stb_lottery`) — chỉ **thêm** một hàm cạnh chúng.
> Nhánh vẽ bổ sung vốn nằm ở `api.py`, tầng quản lý dữ liệu.
>
> **Không con số nào trong báo cáo phải đo lại.** Đã kiểm cả 6 bộ đo: tất cả nạp
> trọn danh sách rồi chạy **một lần**, không bộ nào chạm nhánh vẽ bổ sung.

**Cái giá, nói thẳng:** em cũ **có thể** mất suất vào tay em mới qua bốc thăm.
Không tránh được — cho em mới một cơ hội thật thì cơ hội đó phải lấy từ đâu đó.
Và chuyện này vốn đã đúng với **điểm thi**: một em mới điểm cao luôn đánh bật
được em cũ điểm thấp hơn, vì Tầng 1 đứng trọn trước Tầng 2. Bản vá chỉ làm bốc
thăm hành xử nhất quán với điểm.

Có **13 test canh** (`tests/test_chen_stb_cong_bang.py`). Chạy đột biến: trả lại
cách dồn xuống cuối làm **4 test đỏ**, bỏ `sorted()` làm **1 test đỏ**.


### ĐÃ SỬA (05/09) — tệp kết quả rơi vào thư mục cài đặt

`export_csv` đặt tệp **cạnh `app.db`**, tức bên trong thư mục cài đặt, lẫn với
`.exe` và dữ liệu. Tìm được, nhưng không phải chỗ để tệp cho người ta mang đi.

Nay tệp vào **thư mục Tải xuống** của người dùng (`thu_muc_tai_ve()` trong
`api.py`). Trên Windows hỏi thẳng hệ điều hành bằng `SHGetKnownFolderPath` với
`FOLDERID_Downloads` — **không** ghép `%USERPROFILE%\Downloads` làm cách chính,
vì người dùng dời được thư mục đó và OneDrive thường chuyển hướng nó.

- Xuất nhiều lần **không ghi đè**: `ket_qua_phan_bo (2).csv`, `(3)`… như trình duyệt.
  Thư mục Tải xuống là thư mục của **người dùng** — ghi đè im lặng ở đó là xoá mất
  tệp họ có thể đang cần.
- Không tìm được thư mục Tải xuống → **lùi về cạnh `app.db`** như cũ. Việc xuất
  không bao giờ thất bại chỉ vì chuyện chỗ để tệp.
- Đường dẫn **tuyệt đối** do bên gọi truyền vào vẫn được tôn trọng nguyên văn.
- `tests/conftest.py` có fixture `autouse` đặt `RBDA_THU_MUC_TAI_VE` vào thư mục
  tạm — **không test nào được rải tệp vào Downloads thật của người chạy**.


### ĐÃ SỬA (05/09) — giao diện tiếng Việt còn lẫn tiếng Anh

Đếm được trong chuỗi hiển thị: `pipeline` 15 · `club` 60 · `file` 11 · `STB` 10 ·
`tab`, `tick`, `kiosk`, `hardcode`… Và giao diện **mâu thuẫn với chính hướng
dẫn**: nút ghi *"Chạy pipeline"*, hướng dẫn bước 4 ghi *"Bấm **Chạy phân bổ**"*.

Đã Việt hoá `i18n.js`, `i18n_errors.py` và chữ mặc định trong `index.html`.
Bảng từ: pipeline → *phân bổ* · club → *CLB* · file → *tệp* · tab → *thẻ* ·
tick → *đánh dấu* · kiosk → *tại chỗ* · hardcode → *cài cứng*.

**Giữ nguyên tiếng Anh có chủ ý — đừng "sửa nốt":**

- `(STB)` và `(seed)` trong ngoặc đơn, ở lần xuất hiện đầu mỗi màn hình — để
  người đọc báo cáo hoặc mã nguồn nối được với nút trên màn hình. Học sinh chọn.
- `capacity`, `reserve_capacity`, `reserve_group`, `club_id` — **tên cột thật
  trong tệp CSV người dùng tự gõ**. Dịch chúng là chỉ sai chỗ cần sửa.
- `tab General` / `Unblock` trong `HUONG_DAN_CAI_DAT` — đúng chữ trên hộp thoại
  Windows.

Có lưới chắn: `tests/test_giao_dien_tieng_viet_sach.py` quét cả ba nơi và đỏ nếu
chuỗi mới lẫn tiếng Anh. Bản thân lưới chắn cũng có test canh (nếu bộ lọc quá
rộng thì nó xanh một cách vô nghĩa).


### ⚠️ PHẢI LÀM TRƯỚC KHI NỘP — build lại `.exe` và thử trên Windows

Ba thay đổi ngày 05/09 đụng **cả Python lẫn JS/HTML**, nên bản `.exe` hiện có đã
lạc hậu. Phải build lại qua GitHub Actions (`build-windows-exe.yml`) rồi tải về
máy Windows thật thử.

**Một thứ KHÔNG thử được trong môi trường phát triển:** đường dẫn thư mục Tải
xuống trên Windows (`SHGetKnownFolderPath`). Trên Linux nhánh đó không chạy lần
nào. Khi thử trên Windows, kiểm đúng ba điều:

1. Bấm **Xuất kết quả** → tệp có nằm trong `Downloads` thật không (kể cả khi
   OneDrive đã chuyển hướng thư mục đó).
2. Bấm **hai lần** → có ra `ket_qua_phan_bo (2).csv` không, hay ghi đè.
3. Thông báo hiện ra có đúng đường dẫn đầy đủ không.


### ĐÃ SỬA (05/09, phiên 2) — đường dòng lệnh vượt qua cả ba lớp bảo vệ

**Tìm được khi rà nối backend, không phải khi đi tìm lỗi.**
`rbda_priority_pipeline.py` có `run_full_pipeline()` — chạy được bằng
`python rbda_priority_pipeline.py app.db 42 out.csv`. Nó **thiếu bốn lớp** mà
`api.run_pipeline()` có:

| Thiếu gì | Hậu quả nếu chạy nhầm lên `app.db` thật |
|---|---|
| Không tôn trọng `stb_lock` | Vẽ lại **toàn bộ** số bốc thăm, lật kết quả đã công bố |
| Không chèn ngẫu nhiên cho em vào sau | (không đặt ra, vì nó vẽ lại tất) |
| Không `verify_stability` / `sanity_check_result`, không rollback | Kết quả sai vẫn ghi thẳng vào CSDL |
| **Không ghi `run_history`** | **Không để lại dấu vết nào** — lớp quan trọng nhất trong ba lớp chống dò seed biến mất |

**Đã làm gì.** Thêm `_chan_neu_la_du_lieu_that()`: hàm **từ chối chạy** khi CSDL
đã khoá số bốc thăm hoặc đã có dòng nào trong `run_history`. Trên CSDL sạch (ví
dụ do `seed_sample_data` dựng) nó chạy như cũ, nên vẫn dùng để gỡ lỗi được.

> **Vì sao KHÔNG cho nó uỷ quyền về `api.run_pipeline`** — đó là phương án nghe
> hợp lý nhất và nó **sai**: `api.py` đã `import` từ `rbda_priority_pipeline.py`,
> nên chiều ngược lại tạo **vòng lặp import** ngay trong mô-đun mà mọi thứ khác
> phụ thuộc. Thêm chốt chặn rẻ hơn và không đụng gì tới đường chạy thật.

Test canh: `tests/test_pipeline_core.py` — chạy trên CSDL đã dùng thật phải
`raise` **và không kịp đổi số bốc thăm nào**; trên CSDL sạch vẫn chạy.


### ĐÃ ĐO (05/09, phiên 2) — thử tải NGHỊCH CẢNH, không tìm ra lỗi nào

`du_lieu_test/thu_tai/` cũ quét 204 cấu hình tới 5000 em, nhưng chỉ đổi **quy
mô** — dữ liệu vẫn bình thường. Bộ mới
`du_lieu_test/thu_tai/thu_nghich_canh.py` đổi **hình thù**:

| Kịch bản | Số vòng | Kết quả |
|---|---|---|
| 800 em · 1 CLB 20 chỗ · mỗi em 1 nguyện vọng | 1 | đạt |
| 300 em · 30 CLB **sức chứa 1** | 18 | đạt |
| 500 em · **cả trường cùng điểm 8.0** | 13 | đạt |
| 400 em · **không ai được chấm điểm** (toàn Tầng 2) | 8 | đạt |
| CLB không ai đăng ký · em không nguyện vọng nào | 1 | đạt |
| **Suất dự trữ = toàn bộ sức chứa** | 11 | đạt |
| **Nạp → chạy → nạp thêm → chạy lại, 5 đợt, 2000 em** | 23 | đạt |
| Tên là công thức Excel, có tab/xuống dòng, 300 ký tự, emoji | 1 | đạt |

**Cả 8 kịch bản đạt**: không ném lỗi, **0 cặp phá vỡ**, số vòng cao nhất **23**
so với trần 1000. Bản nhanh nằm trong bộ test thường (`tests/test_nghich_canh.py`,
13 test, chạy dưới 2 giây).

Kịch bản áp chót là đáng giá nhất: nó chạy đường chèn ngẫu nhiên viết hôm qua ở
quy mô **2000 em qua 5 lần khoá**, gấp 66 lần quy mô nó được viết ra — và thứ tự
tương đối của các em cũ giữ nguyên sau **mọi** đợt.


### ĐÃ ĐO (05/09, phiên 2) — cấu hình KHÔNG có suất dự trữ

Câu hỏi: trường quốc tế không cần chính sách dự trữ thì phần mềm chạy sao?

**Phần mềm chạy đúng, không phải sửa gì** — chỉ cần để cột `reserve_capacity`
bằng 0. 0 cặp phá vỡ ở mọi seed.

**Nhưng có một điều đáng đưa vào báo cáo:** `reserve_capacity = 0` làm hàm lựa
chọn thu về đúng *"sắp theo thứ hạng, lấy K em đầu"* — tức **mô hình `Q_j` trong
báo cáo TRỞ THÀNH ĐÚNG**. Chỗ lệch báo cáo ↔ phần mềm ở mục 4b tồn tại **chỉ vì**
có suất dự trữ.

| Bỏ hết dự trữ, 20 seed | Em đổi CLB | Mất suất | Được thêm suất |
|---|---|---|---|
| `bo_sach` (140 em · 16 suất) | TB **32,3** (23,1%) | 0,1 | 0,1 |
| `TEST_0*` (120 em · 12 suất) | TB **22,6** (18,8%) | 5,7 | 4,2 |

16 suất dự trữ trên 150 chỗ làm **32 em** đổi chỗ — dự trữ đẩy dây chuyền sang cả
những em không thuộc diện nào. Nhưng số em **mất hẳn suất** thì ít hơn nhiều: bỏ
dự trữ chủ yếu xáo lại *ai vào đâu*, không phải *ai có suất*.

Bộ đo `du_lieu_test/do_khong_du_tru.py`, 7 test canh
(`tests/test_khong_du_tru.py`). Diễn giải đầy đủ ở `docs/CO_CHE_THUAT_TOAN.md`.

> **AI không kết luận hộ.** Trường nên hay không nên dùng suất dự trữ — học sinh
> tự viết.


### ĐÃ RÀ, KHÔNG PHẢI LỖI (05/09, phiên 2) — ba nghi ngờ đã bác bỏ bằng số đo

**Đọc mục này trước khi định "sửa" ba chỗ đó.** Cả ba trông như lỗi khi đọc mã.

| Nghi ngờ | Đo được |
|---|---|
| 33/34 hàm mở kết nối SQLite không có `finally` → **rò kết nối** | **Không rò.** Gọi 600 lần vào các nhánh lỗi: số kết nối còn sống vẫn **0**. CPython thu hồi bằng đếm tham chiếu. Vấn đề *phong cách*, không phải lỗi |
| `max_rounds = 1000` bị chạm → **cắt cụt âm thầm** | **Không chạm được** — nhưng lập luận cũ ở đây SAI, và sai từ đầu. Cận trên KHÔNG phải độ dài danh sách nguyện vọng: một em bị đẩy ra khỏi CLB này lại đi nộp CLB khác, đẩy em kế tiếp, nên sóng từ chối chạy dài hơn danh sách của bất kỳ ai. Đo lại trên ba bộ dữ liệu × 10 hạt giống: nguyện vọng dài nhất trong một buổi là **4**, mà số vòng lên tới **12**. Cận trên thật là tổng số lượt nộp trong MỘT buổi (đo được cao nhất: **412**), và vòng lặp chạy theo từng buổi nên con số đó không cộng dồn qua các buổi. Cách 1000 rất xa |
| Không có khoá chống gọi chồng | `connect_db` đã đặt `busy_timeout` dài + `synchronous=FULL`, và giao diện tự khoá nút lúc chạy. Kiosk một người dùng — đủ |

Dù `max_rounds` không chạm được, `run_rbda` nay **ném lỗi tường minh** nếu chạm,
thay vì lặng lẽ trả kết quả dở dang. Trước đây `verify_stability` sẽ bắt được
nhưng báo **sai nguyên nhân** ("có cặp phá vỡ" thay vì "hết vòng").

**Một thứ KHÔNG kiểm được và đừng tin kết quả cũ:** tôi có chạy `pyflakes` để dò
import thừa — **máy không cài `pyflakes`**, nên kết quả rỗng lúc đó là *vô nghĩa
chứ không phải sạch*. Muốn kiểm thật thì phải cài trước.


### QUY ƯỚC (06/09) — mở kết nối CSDL bằng `with`, đừng viết tay nữa

`api.py` từng lặp đúng một mẫu **33 lần**:

```python
conn = connect_db(self.db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
... câu SQL ...
conn.close()
```

Ba dòng đầu và dòng cuối không nói gì về việc hàm đang làm — chúng chỉ che mất
câu SQL, thứ duy nhất đáng đọc. Nay có hai trình quản lý ngữ cảnh:

| Dùng khi | Gọi thế nào | Nó lo giúp |
|---|---|---|
| Chỉ đọc | `with self._ket_noi_doc() as cur:` | `row_factory`, con trỏ, và **luôn đóng** kể cả khi ném lỗi |
| Có ghi, một giao dịch | `with self._ket_noi_ghi() as cur:` | như trên, cộng **commit** khi trọn vẹn và **rollback** khi lỗi |

**Đã chuyển 25/33 hàm.** Tám hàm còn lại **cố ý để nguyên**:

- **`run_pipeline`** — học sinh dặn *"đừng động vào"*. Nó điều phối rollback và
  ghi nhật ký nhiều bước; đó là hàm quan trọng nhất của phần mềm.
- **Bảy hàm ghi có đường `return` sớm** (`delete_club`, `set_student_reserve_group`,
  `submit_club_scores`, `submit_test_selection`, `submit_preferences`,
  `reset_student_entry`, `delete_student`). Chuyển máy móc sang "tự commit khi
  thoát khối `with`" là **đổi ngữ nghĩa**: một `return` giữa chừng sau khi đã ghi,
  hiện đang KHÔNG commit, sẽ thành CÓ commit. Muốn chuyển thì phải soi từng hàm,
  không chạy script hàng loạt.

> `rollback()` trong `_ket_noi_ghi` **không đổi hành vi** — đóng kết nối SQLite khi
> chưa commit thì giao dịch tự huỷ. Viết ra thành chữ để đọc mã không phải nhớ
> luật đó mới biết dữ liệu có an toàn không.

**Đã chứng minh không đổi hành vi**, không chỉ dựa vào test: diff bỏ qua thụt lề
chỉ còn **78 thêm / 97 xoá**, và mọi dòng xoá đều là mẫu lặp; vân tay kết quả xếp
lớp của cả ba bộ dữ liệu trùng khớp từng ký tự với bản trước khi sửa; và commit
lẫn rollback được kiểm bằng cách đọc thẳng tệp `.db` từ một tiến trình khác.


### Còn lại chưa giải quyết

- **`ky_va_tin_cay.ps1` chưa chạy ở đâu bao giờ.** Nếu demo trên máy không có quyền
  Administrator thì nó vô dụng — cân nhắc bỏ hẳn cho gọn.
- **Trần 10 nguyện vọng — nay tính theo TỪNG BUỔI.** Trước đây đếm cho cả tuần và
  bỏ qua trọn học sinh vượt trần; trần đó viết cho trường một buổi. Với sáu buổi thì
  em nào chọn 2 CLB mỗi buổi đã là 12 nguyện vọng và rơi ra ngoài — đo được **31 trên
  180 em** của `bo_sau_buoi` và **4 trên 160** của `bo_nhieu_buoi` bị gạt lặng lẽ khỏi
  đợt xếp. Nay vượt trần thì chỉ **riêng buổi đó** không được nhập. Kèm theo một trần
  mới: **5 câu lạc bộ dự thi mỗi buổi**.

**Việc tiện lợi CÒN LẠI đã khảo sát nhưng chưa làm** (xem lại nếu học sinh hỏi):
- ~~Club phải tạo tay từng cái~~ — ĐÃ XONG: `import_clubs_csv` +
  `mau_csv/05_danh_sach_club.csv`.
- ~~`reserve_group` của HỌC SINH~~ — ĐÃ XONG: cột `reserve_group` trong cả
  hai file học sinh (xem mục 4.11).
- ~~Phải tự chuyển Excel sang CSV~~ — ĐÃ XONG: `xlsx_to_csv_text` đọc thẳng
  `.xlsx`, kèm 3 file Excel mẫu có sheet hướng dẫn.
- ~~Lệch tên nhóm dự trữ~~ — ĐÃ XONG: chuẩn hoá nhãn (mục 4.12) + cảnh báo
  `csv_reserve_group_unknown` hiện NGAY lúc nhập, kèm gợi ý nhóm gần giống
  nhất (`difflib.get_close_matches`). Mục Cảnh báo dữ liệu vốn ĐÃ bắt được
  ca này từ trước (mục 4 và 6 của `get_data_health_report`), nhưng nằm ở
  panel khác nên rất dễ lướt qua.
- **Chưa có nút "Sao lưu ngay" / "Khôi phục"** trong app thường; hiện chỉ
  tự sao lưu trước mỗi lần chạy pipeline, còn khôi phục thì chỉ xuất hiện
  ở màn hình recovery — tức là SAU KHI DB đã hỏng. Quy trình sao lưu đã
  chốt là copy tay file `.db` qua USB (mục 4.1), nên một nút "Xuất bản sao
  lưu ra USB" sẽ khớp đúng quy trình đó.

**Đã soát thủ công luồng nạp (29/08), các ca CÒN LẠI chưa xử lý:**
- ~~Excel làm mất số 0 đứng đầu mã học sinh~~ — ĐÃ CÓ CẢNH BÁO
  (`_soat_ma_nghi_bi_cat`): mã toàn chữ số ngắn hơn độ dài phổ biến trong cùng
  file thì báo `csv_student_id_maybe_truncated`. Ba điều kiện chống nhiễu: chỉ
  xét mã toàn số, cần ≥3 mã như vậy, và mã ngắn phải là thiểu số. KHÔNG tự thêm
  số 0 — phần mềm không biết mã gốc dài bao nhiêu, đoán thêm là bịa dữ liệu.
- **File .xlsx chứa CÔNG THỨC chưa được Excel tính sẵn** đọc ra ô rỗng
  (`data_only=True` lấy giá trị đã lưu, file do openpyxl tạo thì không có).
  File Excel thật do Excel lưu luôn có giá trị nên thực tế hiếm gặp; dòng
  hỏng vẫn bị bỏ qua kèm cảnh báo `csv_club_row_invalid`.

**Cảnh báo chữ ký số của Windows (30/08):** bản `.exe` không có chữ ký thương mại
nên Windows SmartScreen cảnh báo "nhà phát hành không xác định". Đây KHÔNG phải lỗi
phần mềm — mọi ứng dụng không mua chứng chỉ đều bị. Chứng chỉ OV giá 200–400 USD/năm
mà SmartScreen VẪN cảnh báo tới khi đủ lượt tải; chỉ EV (400–1000 USD/năm, kèm USB
token) mới hết ngay → ngoài tầm với đề tài học sinh.

Đã làm hai đường đi được, ghi trong `HUONG_DAN_CAI_DAT.md`:
- **Bấm qua cảnh báo** (More info → Run anyway) — mặc định, không cần quyền gì, và
  Windows nhớ lựa chọn nên chỉ hiện lần đầu trên mỗi máy.
- **`ky_va_tin_cay.ps1`** — tạo chứng chỉ tự ký, cài vào kho tin cậy, ký `.exe`.
  Hết cảnh báo hoàn toàn NHƯNG chỉ trên máy đã chạy script (cần Administrator).

### Bộ dữ liệu chạy thử (`du_lieu_test/`)

Đã chạy trọn quy trình với bộ này trong sandbox: nạp 3 file Excel → chấm điểm 356
lượt → `run_pipeline(seed=42)` → xuất kết quả. Ra **118/120 em được xếp**, 2 em vào
`_chua_duoc_xep.csv`, 11 file theo CLB. File `TEST_04_CO_LOI_CO_Y.xlsx` cho ra đủ
**5 cảnh báo** đã hứa trong sheet Ghi chú.

`NHAP_TAY.md` hứa một bảng kết quả cụ thể và bảo người dùng "ra khác là phần mềm
sai". Lời hứa đó được canh bằng `tests/test_kich_ban_nhap_tay.py` (8 test) — không
có test canh thì một thay đổi thuật toán sẽ âm thầm làm tài liệu nói dối. Kịch bản
cố ý không có hai em bằng điểm trong cùng CLB, nên STB không được dùng tới: đã chạy
với 5 seed khác nhau, kết quả giống hệt nhau.

Chính bộ này lộ ra lỗi thứ mười: `_soat_ma_trung_hoa_thuong` chỉ đối chiếu mã trong
file với mã **đã có trong CSDL**, nên hai cách viết `HS201`/`hs201` nằm trong **cùng
một file** (cả hai đều mới) thì lọt hoàn toàn. Đã sửa và có test riêng.

### ✅ TRỌN LUỒNG NẠP → CHẠY → XUẤT ĐÃ CHẠY TRÊN WINDOWS (01/09)

Bước cuối cùng của dự án chưa ai kiểm chứng — *"mở tệp xuất ra trên máy thật"* —
nay đã đóng. Học sinh chạy bộ `bo_sach/` trên máy Windows rồi gửi lại tệp kết
quả; đối chiếu với lần chạy trên Linux ở đây.

| Đối chiếu | Kết quả |
|---|---|
| Số dòng | 140 — khớp |
| **Số dòng KHÁC nhau giữa hai máy** | **0** |
| Phân bố nguyện vọng | 54 · 46 · 21 · 11 · 7 · 1 — khớp |
| Diện thường / dự trữ | 124 / 16 — khớp |
| Sức chứa 12 CLB | khớp từng CLB |
| Dấu BOM `utf-8-sig` | có |
| Xuống dòng | CRLF (chuẩn Windows) |
| Tiếng Việt | không dòng nào vỡ dấu; chuẩn hoá **NFC** |

**Điều đáng viết vào báo cáo:** cùng một bộ dữ liệu và cùng `seed = 42` thì
Windows và Linux cho ra **kết quả phân bổ giống hệt nhau tới từng dòng**. Thuật
toán tất định, không phụ thuộc hệ điều hành — nghĩa là kết quả **tái lập được**,
ai cầm dữ liệu cũng dựng lại được đúng bảng đó để kiểm chứng.

*Lưu ý khi đọc bảng kết quả:* dữ liệu mô phỏng có vài em **trùng họ tên**
(vd `HS009` và `HS021` cùng tên "Phan Đức Phúc"). Đây là ngẫu nhiên khi sinh tên,
không phải lỗi — hệ thống định danh bằng **mã học sinh**, không bằng tên.

Tệp kết quả **không đưa vào git**: đó là dữ liệu học sinh, dù ở đây là dữ liệu
mô phỏng thì vẫn giữ đúng quy tắc (mục 4).

### ✅ ĐÃ CHẠY ĐƯỢC TRÊN MÁY WINDOWS THẬT (30/08) — học sinh xác nhận

Ba câu hỏi chặn cả tuần đã có câu trả lời, học sinh tự quan sát và báo lại:

| Câu hỏi | Kết quả |
|---|---|
| Cửa sổ riêng hay tab trình duyệt? | **Cửa sổ ứng dụng riêng** |
| Có mục riêng trên thanh tác vụ? | **Có** |
| Thu nhỏ 3–5 phút rồi mở lại còn sống? | **Còn sống** |

Học sinh cũng đã nạp thành công cả 4 tệp Excel trong `du_lieu_test/` và gửi ảnh
màn hình. **Mười con số ứng viên mỗi CLB (31 · 35 · 37 · 36 · 43 · 38 · 28 · 34 ·
31 · 43) khớp từng cái với kết quả đo trong sandbox** — đường đọc Excel → nhận
diện → ghi CSDL cho kết quả giống nhau trên hai máy khác nhau.

Học sinh báo **không gặp lỗi nào**. 11 cảnh báo trên màn hình là phần mềm chạy
ĐÚNG: 10 cảnh báo "chưa chấm điểm" (đo được: chấm xong thì 11 → 1) và 1 cảnh báo
nhãn `chinh_sac` — chính là lỗi cố ý trong `TEST_04`, bị bắt lần thứ hai bởi một
cơ chế khác với lúc nhập tệp.

**Diễn biến hai ngày, ghi lại đầy đủ vì đây là phần đáng viết vào báo cáo:**

- **30/08** — ảnh Task Manager cho thấy nhóm *Microsoft Edge (8)*, mọi tiến trình
  con là `msedge.exe`. Kết luận lúc đó: đang chạy bằng **chế độ dự phòng**, lỗi
  pythonnet vẫn còn.
- **31/08** — sau khi thêm phần ghi log và tự gỡ dấu tệp: nhóm đổi thành
  *WebView2 Manager*, tiến trình `msedgewebview2.exe`, và Task Manager có
  `PhanBoCauLacBo.exe` **là tiến trình riêng**. Log ghi `da_go: 173, bo_qua: 0` rồi
  *"cua so goc (pywebview) mo THANH CONG"*.

**Lỗi đã đóng.** Xem mục 5 để biết nguyên nhân gốc và bằng chứng đầy đủ.

Phân biệt hai tên tiến trình — chỗ này dễ nhầm và quan trọng cho báo cáo:

| Tiến trình | Là gì | Nghĩa là |
|---|---|---|
| `msedge.exe` | **Trình duyệt Edge** | App đang mượn trình duyệt để vẽ (đường dự phòng) |
| `msedgewebview2.exe` | **WebView2 Runtime** — thành phần hệ điều hành | App vẽ trong cửa sổ của chính nó (đường chính) |

Đường dự phòng **vẫn giữ nguyên trong mã**, làm lưới an toàn cho máy thiếu WebView2
Runtime. Địa vị của nó đổi từ *"đường đang chạy"* thành *"đường lẽ ra không bao giờ
chạy"* — góc dưới thanh bên nói rõ đang chạy đường nào.

**Điều kiện dùng thật, học sinh xác nhận 30/08:** dùng **chuột**, không phải màn
hình cảm ứng → mọi lo ngại về kích thước nút cho ngón tay là **không còn liên quan**.
Máy demo có thể là máy giám khảo, và có mạng ở phòng thi.

Hai hệ quả đã xử lý:
- Bản build nay được đưa lên mục **Releases** (tải bằng đường dẫn thường, không cần
  đăng nhập GitHub — tệp trong mục Actions thì BẮT BUỘC đăng nhập, trên máy người
  khác là rào cản thật).
- Bộ 120 học sinh cần **356 ô điểm** và phần mềm **không có đường nhập điểm từ tệp**
  — gõ tay hết mất ~18 phút, dài hơn thời gian demo. Đã dựng sẵn
  `du_lieu_test/app_DEMO_da_cham_diem.db` (nạp xong, chấm xong, 0 cảnh báo, cố ý
  chưa chạy phân bổ). Đây là **lỗ hổng tiện dụng còn lại đã biết**, không sửa vì
  đang đóng băng tính năng.

**Chưa kiểm chứng trên máy thật:** các bước SAU khi nạp dữ liệu (chấm điểm, chạy
phân bổ, xuất kết quả), và
máy kiosk thật, và **toàn bộ `ky_va_tin_cay.ps1`** — sandbox là Linux, không có
`signtool`, không có kho chứng chỉ Windows. Đã kiểm được cú pháp PowerShell (parse
sạch, 988 token) và logic tìm file, nhưng các lệnh `New-SelfSignedCertificate`,
`Import-Certificate`, `signtool sign` thì CHƯA CHẠY THẬT lần nào.

---

## 6. Quy định sử dụng AI của Sở GD&ĐT — BẮT BUỘC ĐỌC

Đề tài này chịu ràng buộc của **Phụ lục 1 (Bảng Quy Định Sử Dụng AI)** và
**Phụ lục 2 (Sổ Nhật Ký Nghiên Cứu)**.

**Được phép kèm điều kiện:** AI viết mã nguồn — nhưng **phải trích dẫn rõ code nào do AI tạo
+ lưu nhật ký câu lệnh**. Đã có: `Nhat_Ky_AI_RB-DA.pdf` (artifact
`https://claude.ai/code/artifact/1369e5c3-3d9f-4d8f-8c00-0328bc1b5131`).

**KHÔNG bao giờ được phép** — AI tuyệt đối không làm:
- Viết bản thảo kế hoạch nghiên cứu, tóm tắt (abstract), bài báo, poster
- Viết bất kỳ phần nào của bài nghiên cứu để nộp dưới tên học sinh
- **Viết phần Kết luận hoặc Hướng phát triển tương lai của bài nghiên cứu**
- Bổ sung luận điểm mới vào bài đã viết
- Thu thập dữ liệu nghiên cứu, tìm trích dẫn chứng minh, tạo danh mục tài liệu tham khảo

**Điều kiện phải nhắc học sinh mỗi khi liên quan:**
- Sơ đồ AI vẽ → phải ghi nhãn *"Sơ đồ do AI tạo ra"*
- **Bộ dữ liệu 120 học sinh là DỮ LIỆU MÔ PHỎNG** (`seed_sample_data(seed=42)`, và bộ
  Excel trong `du_lieu_test/` với `seed=2026`), không phải khảo sát thật. Trình bày như
  số liệu thật là **bịa đặt dữ liệu**.
- Diễn giải, nhận xét kết quả kiểm thử → học sinh tự viết

### Khảo sát hiện trạng (02/09) — ranh giới đã vạch ở đâu

Học sinh nhờ soạn bộ câu hỏi cho form *"KHẢO SÁT: Quy trình & Mức độ hài lòng
với việc phân bổ CLB"*. Đây là chỗ **sát ranh giới**, nên ghi rõ đã chia thế nào:

| Việc | Ai làm |
|---|---|
| **Hỗ trợ và tư vấn chọn lựa câu hỏi** nhằm tối đa hóa thông tin trên mỗi câu hỏi, giúp thời gian thực hiện biểu mẫu ở mức hợp lí | AI |
| **Xem xét, chọn lọc, sửa và đưa ra quyết định cuối cùng** | **Học sinh** |
| Tạo biểu mẫu, phát khảo sát | **Học sinh** |
| **Thu phản hồi** | **Học sinh** — quy định cấm AI thu thập dữ liệu |
| Phân tích, nhận xét, diễn giải, kết luận từ số liệu | **Học sinh** |
| Dựng biểu đồ từ **số đã tổng hợp** (nếu học sinh đưa) | AI |

> ### Câu chữ phải dùng — không nới rộng, không thu hẹp
> Đây là câu chữ **do chính học sinh chọn**, ghi ở nhật ký AI câu lệnh #92:
>
> *"AI hỗ trợ và tư vấn chọn lựa câu hỏi nhằm tối đa hóa thông tin trên mỗi câu
> hỏi nhằm giúp thời gian thực hiện biểu mẫu ở mức hợp lí. Học sinh xem xét, chọn
> lọc, sửa và đưa ra quyết định cuối cùng. Học sinh tự tạo biểu mẫu, tự phát, tự
> thu phản hồi và tự phân tích."*
>
> **KHÔNG** viết *"AI soạn bộ câu hỏi khảo sát"*, *"AI thiết kế khảo sát"* hay
> *"AI thực hiện khảo sát"* — cả ba đều sai phạm vi và đều chạm vào ô *cấm thu
> thập dữ liệu nghiên cứu* của Phụ lục 1.

Thiết kế công cụ khảo sát **là một phần của phương pháp nghiên cứu**, nên bản
nháp chỉ là điểm khởi đầu — học sinh phải đọc và sửa, không được dán nguyên.

**Vì sao cần khảo sát:** hai bản báo cáo đang *khẳng định* **bảy** điều về hiện
trạng ở VAS mà chưa có số liệu nào đỡ. Khi bảo vệ, giám khảo chỉ cần hỏi *"em
biết điều đó từ đâu?"*.

**Nền tảng: MICROSOFT FORMS** (chốt 02/09, bỏ Google Form). Bốn tệp:

| Tệp | Dùng để làm gì |
|---|---|
| `docs/KHAO_SAT_NHAP_FORMS.docx` | **Đem nhập** bằng Quick Import |
| `docs/KHAO_SAT_HUONG_DAN_FORMS.docx` | **Đọc, KHÔNG nhập** — cài đặt, rẽ nhánh, danh sách soát |
| `docs/KHAO_SAT_CAU_HOI.md` | Bộ câu hỏi kèm lý do thiết kế từng câu |
| artifact `803629b4-b0af-4a89-8715-38b54ccc1ee1` | Bản trang web của tệp trên |

**Quick Import KHÔNG mang theo ba thứ** — rẽ nhánh, dấu bắt buộc, thang Likert.
Cả ba làm tay sau khi nhập. Và Microsoft ghi rõ **bản tiếng Anh chuyển đổi chính
xác hơn các ngôn ngữ khác**, nên bộ câu hỏi tiếng Việt **phải soát lại từng câu**
sau khi nhập.

> ### ⚠️ "GHI LẠI TÊN" TRONG MICROSOFT FORMS MẶC ĐỊNH LÀ **BẬT**
> Với tài khoản trường học, mục *Record name* **bật sẵn** — mỗi phản hồi kèm tên
> và email người trả lời. **Nguy hiểm hơn hẳn Google Forms**, nơi mục tương đương
> mặc định đã TẮT. Người trả lời phần lớn là **trẻ vị thành niên**.
> Phải **TẮT** trước khi phát, và kiểm lại một lần nữa ngay trước khi gửi đường dẫn.

**Bản hiện tại: 16 câu.** Ngày 02/09 học sinh yêu cầu thêm câu và
yêu cầu câu **có ý nghĩa hơn**; đối chiếu lại với hai bản báo cáo thì thấy ba
khẳng định trước đó **không có câu nào chạm tới** — hệ quả sau khi bị xếp sai,
phía câu lạc bộ, và chuyện học sinh tự bỏ nguyện vọng thật của mình. Thêm 6 câu,
bỏ 1 câu trùng.

> ### ⚠️ CÂU 12 KHÔNG PHẢI LÀ "ĐẾM CẶP PHÁ VỠ" — đừng viết nhầm vào báo cáo
> Câu 12 hỏi: *hai em cùng muốn đổi CLB cho nhau*. Đó là **trao đổi cùng có lợi**
> giữa **hai học sinh**. **Cặp phá vỡ** (blocking pair) là chuyện khác hẳn: một
> **học sinh** và một **câu lạc bộ**.
>
> Một phương án ghép cặp **ổn định vẫn có thể để lại** những cặp đổi như vậy — đó
> là chỗ **đánh đổi giữa tính ổn định và tính tối ưu**, không phải lỗi thuật toán
> và không phải điều thuật toán hứa sẽ xoá bỏ.
>
> | Viết được | KHÔNG viết |
> |---|---|
> | "X% học sinh gặp trường hợp muốn đổi CLB cho nhau" | ~~"khảo sát đếm được X cặp phá vỡ"~~ |
> | "cách làm hiện tại để lại những trao đổi cùng có lợi không thực hiện được" | ~~"thuật toán xoá bỏ được X cặp này"~~ |
>
> Câu 12 đáng hỏi vì nó đo **chi phí thật của cách làm hiện tại**, không phải vì
> nó chứng minh thuật toán đúng.

> ### ⚠️ PHẢN HỒI KHẢO SÁT LÀ DỮ LIỆU HỌC SINH CÓ THẬT
> Khác **hoàn toàn** với mọi bộ trong `du_lieu_test/` (đều là máy sinh). Đây là
> câu trả lời của học sinh thật, phần lớn là trẻ vị thành niên.
>
> - Bảng tính kết quả **không bao giờ được vào git**.
> - Trong Forms phải **TẮT "Ghi lại tên"** — xem khối cảnh báo ở trên.
> - Báo cáo chỉ đưa **số đã tổng hợp**, không đưa bảng thô.
>
> #### Lỗ hổng `.gitignore` phát hiện được nhờ chuyển nền tảng (02/09)
>
> Microsoft Forms xuất phản hồi ra tên dạng **`<tên biểu mẫu>(1-53).xlsx`**. Luật
> chặn cũ viết cho Google Forms **không bắt được kiểu tên đó** — `KHAO_SAT*` không
> khớp `KHẢO SÁT` (khác dấu, khác khoảng trắng). Đã thử bằng `git check-ignore`
> trước khi vá, cả bốn đều **LỌT**:
>
> ```
> KHẢO SÁT Quy trình & Mức độ hài lòng với việc phân bổ CLB(1-53).xlsx
> KHẢO SÁT(1-12).xlsx
> Form1(1-53).xlsx
> Khảo sát CLB.xlsx
> ```
>
> Đã vá và kiểm **hai chiều**: 8/8 kiểu tên nay bị chặn, và **25/25** tệp `.csv`
> / `.xlsx` đang được theo dõi **không** bị chặn nhầm. Thêm lưới chắn cuối
> `/*.xlsx` và `/*.csv` — chặn mọi bảng tính ở thư mục gốc dự án, vì tên tệp Forms
> xuất ra không đoán trước được. Bộ mẫu và bộ dữ liệu test nằm trong thư mục con
> nên không bị ảnh hưởng; `docs/KHAO_SAT_CAU_HOI.md/.html/.docx` vẫn vào git bình thường.

**Nếu phiên mới có nhật ký AI cần cập nhật:** ghi thêm câu lệnh mới vào cuối Mục 3 của
artifact, cập nhật số liệu ở Mục 4.

**Trạng thái nhật ký AI (28/09/2026):** đã cập nhật tới **mục #145**. Từ #119 tới #144
câu lệnh **không chép được nguyên văn** — dựng lại từ lịch sử Git, tên phiên và dòng trạng thái
hệ thống ghi. Mục 5 có khối cảnh báo đầu ngày 16/09 – 28/09 nói rõ điều đó. Năm phiên **chạm
ranh giới** (#121 dàn ý + biểu đồ cho Phần 4 báo cáo, #123 AI đề nghị viết lại mục 4.2.2.3,
#124 bàn về nguồn tài liệu, #129 “kết quả chính” cho một biểu mẫu, #130 rà báo cáo) — học sinh
phải tự khai (Mục 7, ý 26–28). **Mọi nhánh đã được gộp vào main** qua nhánh tích hợp `claude/loving-cerf-i3beul` (30/09), kể
cả bản vá lỗ rò `GET /app.db` (`claude/gifted-faraday-yt1zqp`) và lỗi điểm của bài thi đã rút
(`claude/section-3-search-score-data-3zc7l9`). Hai nhánh không gộp vì đã có trên main:
`claude/admiring-bell-hjc6fc` và `claude/confident-edison-mdh71z` (đổi "phân bổ" thành "sắp xếp").

**Trạng thái 15/09/2026:** đã cập nhật tới **câu lệnh #117**, phủ hết
tới ngày 15/09 — **117 câu lệnh · 95 mã commit · 131 tệp do AI viết mới · 757 test**.
Phần thêm từ #99 gồm: bảy thí nghiệm tối ưu/ổn định (TN1–TN7), phần nhiều buổi, ba
thiết kế bốc thăm và việc chốt một thiết kế, chọn buổi để chạy, trần theo buổi, dựng
bản cài trên máy Windows, bốn mục dữ liệu mới ở thẻ Kết quả, bộ ví dụ đầu vào có
giảng giải, và kỹ năng sinh dữ liệu.

> **Hai chỗ trong nhật ký cần biết khi đối chiếu:**
>
> - **Kho mã chuyển chỗ ngày 12/09.** Commit tới `c5ed5bd` tra ở kho cũ; từ `504bd15`
>   trở đi tra ở kho `rbda-kiosk`. Lịch sử được giữ nguyên khi tách, không chép tay.
> - **Câu lệnh ba ngày 06–08/09 không chép lại được nguyên văn** — bản ghi hội thoại
>   của những phiên ấy không còn. Mục **#99** ghi thẳng điều đó và liệt kê sáu mã
>   commit thay thế, thay vì dựng lại câu lệnh theo trí nhớ. Đây là chỗ nhật ký yếu
>   nhất về bằng chứng câu lệnh, và nó được nói ra chứ không che đi.

**Trạng thái trước đó (05/09/2026):** đã cập nhật tới **câu lệnh #97**, phủ hết
ngày 02–05/09 — lỗi 24, lỗi 25, ba bộ đo bốc thăm, trang `GIAI_DAP_BOC_THAM`, bộ
câu hỏi khảo sát 16 câu, việc chuyển sang Microsoft Forms, trang
`CO_CHE_THUAT_TOAN`, bộ đo cái giá của tính ổn định, và ba việc ngày 05/09.

> **Phần khảo sát trong nhật ký ghi đúng phạm vi — đừng nới rộng khi viết báo cáo.**
> Câu chữ do **học sinh chọn**, ghi ở câu lệnh #92:
> *"AI hỗ trợ và tư vấn chọn lựa câu hỏi nhằm tối đa hóa thông tin trên mỗi câu hỏi
> nhằm giúp thời gian thực hiện biểu mẫu ở mức hợp lí. Học sinh xem xét, chọn lọc,
> sửa và đưa ra quyết định cuối cùng. Học sinh tự tạo biểu mẫu, tự phát, tự thu phản
> hồi và tự phân tích."*
> **KHÔNG** viết "AI soạn bộ câu hỏi khảo sát", "AI thiết kế khảo sát" hay "AI thực
> hiện khảo sát" — cả ba đều sai phạm vi và đều chạm vào ô *cấm thu thập dữ liệu
> nghiên cứu* của Phụ lục 1.

Hai mốc dùng được khi giám khảo hỏi về ranh giới sử dụng AI:

- Câu lệnh **#89** — **AI từ chối viết phần Kết luận** (02/09).
- Câu lệnh **#95** — **AI từ chối tìm tài liệu tham khảo**, hỏi bốn lần từ chối cả
  bốn (02/09). Là mục duy nhất trong nhật ký mang nhãn **"Không được phép"**.

---

## 7. Cách làm việc học sinh mong đợi

- **Trả lời bằng tiếng Việt.**
- **Kiểm chứng bằng thực nghiệm, đừng đoán.** Bài học đắt giá: hai lần đoán nguyên nhân lỗi
  `.exe` đều sai, chỉ khi đọc log build mới tìm ra sự thật. Học sinh đã phải tải về thử vô ích 2 lần.
- **Nói thẳng khi không chắc**, và nói rõ phần nào chưa kiểm chứng được.
- Chạy `pytest` trước khi commit. Giữ `i18n.js` ↔ `i18n_errors.py` đồng bộ.

---

## 8. Tài liệu tham chiếu

| Tài liệu | Nơi lưu |
|---|---|
| Giải thích thuật toán RB-DA (tiếng Việt, có sơ đồ) | artifact `ef3cc025-51d6-4bb8-a8ee-92ac23c945c8` |
| Kế hoạch kiểm thử mất dữ liệu | artifact `c0aa29df-b2b2-4e40-8e72-4adb63627a26` |
| Nhật ký AI (PDF in được) | artifact `1369e5c3-3d9f-4d8f-8c00-0328bc1b5131` |
| Phần mềm chạy cơ chế gì (5 lớp + cái giá của ổn định) | artifact `eced0ff9-08df-4922-a17e-5f85d99f79aa` · `docs/CO_CHE_THUAT_TOAN.md` |
| Tài liệu thuật toán + dữ liệu test | `TAI_LIEU_RBDA.zip` (đã gửi cho học sinh) |
| README chi tiết | `rbda-kiosk/README.md` |

**Lưu ý:** các file sau được nhắc trong chú thích code nhưng **chưa bao giờ được upload**:
`02_schema.sql`, `03_reference_rbda.py`, `06_ms_forms_transform.py`, `PACKAGING_HUONGDAN.md`,
`compare_with_reference.py`, `expected_match_results.csv`. Chú thích trong code giờ trỏ về
mục này. `ke-hoach-mat-du-lieu.html` chính là artifact "Kế hoạch kiểm thử mất dữ liệu" ở
bảng trên.
