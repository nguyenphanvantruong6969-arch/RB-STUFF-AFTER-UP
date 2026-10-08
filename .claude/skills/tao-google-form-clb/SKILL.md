---
name: tao-google-form-clb
description: Tạo tệp Google Apps Script (.gs) dựng biểu mẫu Google Forms "Đăng ký CLB và thi tuyển" cho một trường, từ danh sách buổi, CLB và đề thi (tệp Excel mẫu), kèm hướng dẫn từng bước cụ thể để tạo biểu mẫu, gửi học sinh, chấm điểm và xuất Excel. Biểu mẫu tạo ra có Top 1 tới Top 10 dạng danh sách thả xuống, tick tối đa 5 CLB thi, chỉ hiện đề CLB được chọn, tự chấm, và xuất dữ liệu raw cho skill xu-li-raw-forms. Dùng khi người dùng nói "tạo Google Form", "làm biểu mẫu đăng ký CLB", "tạo file gs", "đổi đề thi trên form", "thêm CLB vào form", "làm form cho năm học mới", "hướng dẫn tạo form", "create the Google Form", hoặc đưa danh sách CLB / đề thi và muốn có biểu mẫu.
---

# Tạo tệp .gs dựng biểu mẫu Google Forms đăng ký CLB và thi tuyển

> **Đường dẫn lệnh.** Trong kho mã rbda-kiosk, script nằm ở `.claude/skills/tao-google-form-clb/scripts/tao_form.py`. Ở bản đóng gói (.zip), dùng `scripts/tao_form.py` trong thư mục của skill này; các tệp phụ thuộc đã có sẵn cạnh nó.

Tệp `.gs` tạo ra là một đoạn Google Apps Script. Người dùng dán vào
script.google.com, chạy một lần, là có đủ biểu mẫu: câu hỏi, đáp án, điểm, rẽ
nhánh. Khuôn mẫu mã nằm ở `mau_forms_thi_clb/tao_google_forms.py`; skill này chỉ
đổ dữ liệu của trường vào khuôn đó, nên mọi biểu mẫu tạo ra đều xuất dữ liệu raw
đúng `mau_forms_thi_clb/DINH_DANG_RAW.md` và skill `xu-li-raw-forms` xử lí được.

## Biểu mẫu tạo ra trông thế nào (để giải thích cho người dùng)

Phần 1 là mã học sinh và họ tên. Mỗi buổi sau đó:

1. "Em có đăng ký sinh hoạt <buổi> không?" Không thì sang buổi sau.
2. Top 1, Top 2, ...: mỗi Top là một danh sách thả xuống, chọn một CLB hoặc "(Bỏ trống)".
   Không bắt xếp đủ. Google không chặn được chọn cùng một CLB ở hai Top; khi chấm
   giữ Top cao hơn và ghi cảnh báo.
3. Tick các CLB muốn thi. Google chặn cứng ở số tối đa đã đặt (không quá 5).
4. "Em thi CLB nào trước?", làm đề CLB đó, rồi "CLB nào tiếp theo?" (chỉ các CLB
   đứng sau). Học sinh chỉ thấy đề của CLB mình chọn.

CLB không có câu nào trong đề là CLB không tổ chức thi: có trong danh sách Top, không
có trong câu tick và không có đề.

## Quy trình

### 1. Có dữ liệu chưa?

- **Chưa có**: tạo tệp mẫu rồi đưa người dùng điền.

  ```bash
  python .claude/skills/tao-google-form-clb/scripts/tao_form.py mau --ra MAU_DE_THI.xlsx
  ```

  Tệp mẫu có 4 trang: `Cai_dat` (tiêu đề, điểm mỗi câu, số CLB thi tối đa),
  `CLB` (buoi, ten_buoi, club_id, ten_clb), `De_thi` (club_id, cau_hoi,
  lua_chon_a tới d, dap_an là chữ a tới d), `Huong_dan`. Tệp đã điền sẵn bộ đề ví
  dụ 50 CLB để người dùng thấy cách điền: nhắc họ **thay bằng dữ liệu thật**.

- **Người dùng đưa danh sách CLB và đề thi dạng khác** (văn bản, Word, bảng
  tính khác): tự chép vào tệp mẫu bằng openpyxl, **đúng nguyên văn**. Không bịa
  câu hỏi, không tự chọn đáp án. Thiếu đáp án thì hỏi lại. Chưa có mã CLB thì tự
  đặt từ tên (không dấu, gạch dưới, ví dụ `clb_co_vua`) và cho người dùng xem.

### 2. Tạo tệp .gs

```bash
python .claude/skills/tao-google-form-clb/scripts/tao_form.py tao \
    --vao MAU_DE_THI.xlsx --ra ./form_moi
```

Ra `TAO_GOOGLE_FORM.gs` và `HUONG_DAN_TUNG_BUOC.md`. Mã thoát 1 và dòng "KHÔNG
GHI TỆP NÀO" nghĩa là tệp Excel có chỗ sai: đọc danh sách lỗi (có số dòng), sửa
cùng người dùng, chạy lại. Không tự đoán để sửa đáp án.

Script soát: mã buổi hợp lệ, `club_id` đúng dạng và không trùng, tối đa 10 CLB
mỗi buổi, đề thi thuộc CLB có thật, ít nhất 2 lựa chọn, không có hai lựa chọn
giống nhau, đáp án nằm trong các lựa chọn, số CLB thi tối đa từ 1 tới 5. Các trần
này lấy từ phần mềm xếp CLB (skill `sinh-du-lieu-clb`), không tự đặt.

"Lưu ý" in ra (CLB không có đề, buổi không có CLB thi, biểu mẫu quá dài) không
chặn, nhưng phải nói lại với người dùng.

### 3. Giao cho người dùng

1. Gửi hai tệp (`TAO_GOOGLE_FORM.gs`, `HUONG_DAN_TUNG_BUOC.md`).
2. Tóm tắt các bước trong `HUONG_DAN_TUNG_BUOC.md` ngay trong câu trả lời, bằng
   tiếng Việt đơn giản: tạo biểu mẫu (dán mã, chạy `taoBieuMau`, cho phép quyền),
   cài đặt và làm thử, gửi học sinh, chấm bằng `chamTheoCLB`, nạp phần mềm hoặc
   dùng skill `xu-li-raw-forms`.
3. Nói trước hai chỗ người dùng hay hỏi:
   - Cảnh báo **"Google chưa xác minh ứng dụng này"** là bình thường vì mã do
     chính họ tạo: bấm Nâng cao, rồi Đi tới ... (không an toàn).
   - Trang chọn quyền: tick **Chọn tất cả** (4 quyền đều cần).
4. Đã có biểu mẫu cũ thì nhắc: tạo lại bằng `taoBieuMau` là ra biểu mẫu **mới**;
   xoá biểu mẫu cũ để không gửi nhầm đường dẫn.

## Giới hạn của Google Forms (nói thật với người dùng khi được hỏi)

- Câu tick không điều khiển được việc hiện câu hỏi. Vì thế học sinh tick trước
  (để bị chặn ở mức tối đa), rồi chọn lần lượt CLB để làm bài.
- Chọn làm bài phải theo thứ tự trong danh sách: Google không nhớ em đã làm CLB
  nào, nên mỗi trang "tiếp theo" chỉ liệt kê CLB đứng sau.
- Google chỉ cho một tổng điểm. Điểm từng CLB do hàm `chamTheoCLB` tách ra.
- Apps Script chạy tối đa 6 phút mỗi lần. Trên khoảng 400 câu hỏi thì nên chia
  thành hai biểu mẫu.

## Kiểm tra

- Không thể chạy Apps Script thật ở đây. Để kiểm đoạn mã sinh ra, bộ test
  `tests/test_skill_tao_google_form.py` chạy nó trên một bản giả lập FormApp bằng
  Node (tự bỏ qua nếu máy không có Node): đếm câu, kiểm rẽ nhánh, kiểm CLB không
  thi không xuất hiện ở câu tick.
- Với bộ đề ví dụ, `mau` rồi `tao` phải ra tệp giống hệt
  `mau_forms_thi_clb/TAO_GOOGLE_FORM.gs`.
