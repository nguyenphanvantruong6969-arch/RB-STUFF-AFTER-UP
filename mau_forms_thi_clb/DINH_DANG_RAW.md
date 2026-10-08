# Định dạng dữ liệu raw của biểu mẫu Google Forms

Tài liệu này mô tả hai tệp mà hàm `chamTheoCLB` trong `TAO_GOOGLE_FORM.gs`
ghi vào thư mục "Kết quả CLB <ngày giờ>" trên Google Drive:

- `RAW_PHIEU.xlsx`: mọi câu trả lời của mọi phiếu, mỗi câu một dòng, câu đề
  thi đã được chấm.
- `DAP_AN.xlsx`: đáp án của toàn bộ đề thi.

Skill `xu-li-raw-forms` (`.claude/skills/xu-li-raw-forms/`) đọc theo đúng tài
liệu này để ra Sổ nhập CLB (`SO_NHAP_CLB.xlsx`) nạp vào phần mềm. Đổi cột trong `.gs` thì phải sửa tài liệu
này và skill cùng lúc; `tests/test_skill_xu_li_raw.py` báo lỗi nếu cột lệch.

Cả hai tệp chỉ có **một trang**, dòng 1 là tên cột. Mọi ô ghi dạng chữ (kể cả
số), để mã như `001` không bị đổi thành `1`. Đọc ra thì tự đổi sang số khi cần.

## 1. `RAW_PHIEU.xlsx`

Có **tất cả** các phiếu, kể cả phiếu bị bỏ. Phiếu bị bỏ vẫn được chấm từng câu
để xem lại, nhưng `duoc_tinh` luôn là `0`.

| Cột | Ý nghĩa |
|---|---|
| `phieu_so` | Số thứ tự phiếu theo thời gian nộp, bắt đầu từ 1 |
| `thoi_gian_nop` | `yyyy-MM-dd HH:mm:ss`, giờ Việt Nam |
| `email` | Email người nộp. Trống nếu biểu mẫu không thu email |
| `student_id` | Mã học sinh em tự gõ, đã bỏ khoảng trắng hai đầu |
| `trang_thai_phieu` | `giu`, `bo_nop_trung` hoặc `bo_khong_ma` (xem mục 3) |
| `ma_cau` | Mã trong ngoặc vuông ở đầu câu hỏi, ví dụ `clb_covua-1` |
| `loai_cau` | Loại câu (xem mục 2) |
| `buoi` | `thu_2` tới `thu_6`. Trống với câu thông tin |
| `club_id` | Mã CLB mà dòng này nói tới. Trống nếu câu không gắn với CLB |
| `cau_so` | `1` hoặc `2` với câu đề thi. Trống với loại câu khác |
| `cau_hoi` | Chữ câu hỏi, đã bỏ phần `[mã]` |
| `tra_loi` | Câu trả lời của em (xem cách ghi ở mục 2) |
| `dap_an_dung` | Chỉ có ở câu đề thi |
| `dung_sai` | `1` là đúng, `0` là sai. Chỉ có ở câu đề thi |
| `diem` | Điểm câu này theo đáp án gốc: `5` hoặc `0` |
| `diem_toi_da` | `5` |
| `diem_forms` | Điểm Google Forms tự chấm. Khác `diem` nghĩa là đáp án trên Forms bị sửa, lệch đáp án gốc |
| `duoc_tinh` | `1` nếu câu này được tính vào điểm CLB, `0` nếu không |
| `ghi_chu` | Lý do khi `duoc_tinh = 0` (xem mục 3) |

So khớp đáp án: bỏ khoảng trắng hai đầu, gộp khoảng trắng liên tiếp, không phân
biệt hoa thường.

## 2. Loại câu và cách ghi câu trả lời

| `loai_cau` | Câu hỏi | Số dòng mỗi phiếu | `tra_loi` |
|---|---|---|---|
| `thong_tin` | `[student_id]`, `[name]` | 1 dòng mỗi câu | Chữ em gõ |
| `dang_ky_buoi` | `[di-thu_2]` … | 1 dòng mỗi buổi | `Có` hoặc `Không, em bận buổi này` |
| `xep_hang` | `[thu_2-top-1]` … `[thu_2-top-10]` (mỗi Top một danh sách thả xuống; biểu mẫu cũ: bảng lưới `[thu_2]`) | 1 dòng cho mỗi Top em đã chọn; `club_id` là CLB ở Top đó | `Top n` |
| `chon_thi` | `[chon-thu_2]` … (ô tick, tối đa 5) | 1 dòng cho mỗi CLB đã tick | `Tên CLB (club_id)` |
| `cong_thi` | `[thi-thu_2]` (em thi CLB nào trước), `[thi-sau-clb_covua]` … (CLB nào tiếp theo) | 1 dòng mỗi trang chọn em đi qua; `club_id` là CLB em chọn, trống nếu em dừng | `Tên CLB (club_id)`, `Em không thi CLB nào buổi này` hoặc `Em không thi thêm CLB nào buổi này` |
| `de_thi` | `[clb_covua-1]` … | 1 dòng mỗi câu em làm | Chữ của lựa chọn em chọn |
| `khac` | Câu có `[mã]` lạ, không thuộc mẫu | 1 dòng | Chữ trả lời |

Câu nào em không đi qua (vì rẽ nhánh) hoặc bỏ trống thì **không có dòng**.

Biểu mẫu tạo bằng bản mã cũ (bảng lưới mỗi dòng một CLB, chọn "Hạng n"; mỗi CLB
một câu `[thi-<club_id>]` trả lời `Có, em thi CLB này`) vẫn cho ra raw đúng định
dạng này: `xep_hang` được đổi sang `Top n`, và câu `[thi-<club_id>]` là
`cong_thi` với `club_id` của CLB đó khi em chọn Có.

## 3. Mã trạng thái

`trang_thai_phieu`:

| Mã | Nghĩa |
|---|---|
| `giu` | Phiếu hợp lệ, được dùng |
| `bo_nop_trung` | Mã học sinh đã nộp trước đó. Chỉ giữ phiếu đầu tiên |
| `bo_khong_ma` | Không có mã học sinh |

`ghi_chu` ở câu đề thi khi `duoc_tinh = 0`:

| Mã | Nghĩa |
|---|---|
| `khong_tick` | Em làm bài CLB này nhưng không tick CLB đó ở câu `chon_thi` |
| `qua_tran` | Đã đủ 5 CLB trong buổi, bài này bị bỏ (chỉ xảy ra nếu biểu mẫu bị sửa tay) |
| `bo_nop_trung`, `bo_khong_ma` | Phiếu bị bỏ, lấy theo `trang_thai_phieu` |
| `khong_xep_hang` | Em làm bài CLB này nhưng không chọn CLB đó ở Top nào |
| `khong_lam_bai` | Có câu đề thi nhưng không trang chọn nào chọn CLB đó (hiếm, chỉ khi biểu mẫu bị sửa) |

## 4. `DAP_AN.xlsx`

Mỗi câu đề thi một dòng, 100 dòng.

| Cột | Ý nghĩa |
|---|---|
| `buoi`, `ten_buoi` | Ví dụ `thu_2`, `Thứ Hai` |
| `club_id`, `ten_clb` | Ví dụ `clb_covua`, `CLB Cờ vua` |
| `ma_cau` | Khớp với cột `ma_cau` của `RAW_PHIEU.xlsx` |
| `cau_so` | `1` hoặc `2` |
| `cau_hoi` | Chữ câu hỏi |
| `lua_chon_a` … `lua_chon_d` | 4 lựa chọn, theo thứ tự hiện trên biểu mẫu |
| `dap_an_dung` | Chữ của lựa chọn đúng |
| `diem` | Điểm mỗi câu: `5` |

## 5. Từ raw ra tệp nạp phần mềm xếp CLB

Chỉ dùng các dòng có `trang_thai_phieu = giu`.

- **Điểm một CLB của một em** = tổng `diem` các dòng `de_thi` có cùng
  `student_id`, `club_id` và `duoc_tinh = 1`. Thang 10.
- **Tệp 02** (`student_id, name, reserve_group, test_club_1, score_1, …`): mỗi
  em một dòng. Các cặp `test_club_n, score_n` là các CLB có điểm ở trên.
  `name` lấy từ dòng `thong_tin` có `ma_cau = name`.
- **Tệp 03** (`student_id, name, reserve_group, thu_2_pref_1, …`): với mỗi buổi
  em đăng ký (`dang_ky_buoi` là `Có`), sắp các dòng `xep_hang` theo số trong
  `Top n`, rồi điền `club_id` vào `<buoi>_pref_1`, `<buoi>_pref_2`, … (bỏ
  trống một Top ở giữa thì dồn lên). Một CLB chọn ở nhiều Top thì giữ Top cao nhất. Bài thi của CLB không có trong danh sách Top
  thì không tính.
- **Tệp 01** (danh sách CLB) không có trong raw: chỉ tiêu do nhà trường lập.

Skill ghép tệp 02 và 03 thành trang `2. Học sinh` của Sổ nhập CLB (điểm đặt
cạnh nguyện vọng của CLB đó) và tệp 01 thành trang `1. CLB`. Bố cục sổ:
`mau_csv/HUONG_DAN_SO_NHAP.md`, `so_nhap.py`; ba bảng nội bộ:
`mau_csv/HUONG_DAN_CSV.md`.

## 6. Những điểm bất thường nên soát

- Hai phiếu cùng `student_id` (đã được đánh dấu `bo_nop_trung`).
- `student_id` sai dạng so với mã của trường, hoặc cùng một email mà hai mã khác nhau.
- `diem_forms` khác `diem`: đáp án trên Google Forms lệch với `DAP_AN.xlsx`.
- `ghi_chu = khong_tick`: em làm bài mà quên tick.
- Có dòng `chon_thi` cho một CLB nhưng không có dòng `de_thi` nào của CLB đó: em tick mà không làm bài.
- Buổi `dang_ky_buoi = Có` nhưng thiếu dòng `xep_hang`, hoặc bỏ trống một Top ở giữa.
- Câu `loai_cau = khac`: biểu mẫu có câu lạ, có thể đã bị sửa tay.
