# Hướng dẫn từng bước: biểu mẫu "Đăng ký CLB và thi tuyển"

Biểu mẫu này có **5 buổi, 50 CLB, 50 CLB tổ chức thi, 100 câu đề thi** (mỗi câu 5 điểm), tổng **212 câu hỏi**. Mỗi buổi học sinh thi tối đa **5 CLB**.

Các buổi: Thứ Hai (10 CLB); Thứ Ba (10 CLB); Thứ Tư (10 CLB); Thứ Năm (10 CLB); Thứ Sáu (10 CLB).

## Bước 1. Tạo biểu mẫu (làm một lần, khoảng 5 phút)

1. Mở **script.google.com** bằng tài khoản Google của trường, bấm **Dự án mới**.
   Cách khác: mở một biểu mẫu Google Forms trống, bấm dấu ba chấm góc trên bên phải, chọn **Apps Script**.
2. Xoá hết chữ có sẵn trong khung soạn thảo.
3. Mở tệp `TAO_GOOGLE_FORM.gs`, chọn tất cả (Ctrl + A), sao chép (Ctrl + C), dán vào khung soạn thảo (Ctrl + V).
4. Bấm biểu tượng đĩa mềm để lưu. Đổi tên dự án (bấm vào tên ở góc trên bên trái), ví dụ "Đăng ký CLB".
5. Ở thanh trên, chọn hàm **taoBieuMau**, bấm **Chạy**.
6. Google hỏi quyền: bấm **Xem lại quyền**, chọn tài khoản.
7. Nếu hiện **"Google chưa xác minh ứng dụng này"**: bấm **Nâng cao**, rồi **Đi tới ... (không an toàn)**. Cảnh báo này hiện vì đoạn mã do chính em tạo, chưa qua Google duyệt.
8. Trang chọn quyền: tick **Chọn tất cả** (Drive, Trang tính, Biểu mẫu, Kết nối dịch vụ bên ngoài), bấm **Tiếp tục**.
9. Đợi 1 tới 3 phút. Mở **Nhật ký thực thi** ở dưới, chép hai đường dẫn: đường dẫn **SỬA** biểu mẫu và đường dẫn gửi **HỌC SINH**.

Chạy taoBieuMau lần nữa là tạo thêm một biểu mẫu mới. Chỉ chạy một lần.

## Bước 2. Cài đặt và làm thử (làm một lần)

Mở đường dẫn SỬA biểu mẫu:

1. Nếu nút **Xuất bản** ở góc trên còn màu tím, bấm để xuất bản.
2. Tab **Cài đặt** → **Bài kiểm tra**: mục **Công bố điểm** chọn **Sau khi xem xét thủ công**. Bỏ tick "Câu hỏi bị trả lời sai" và "Câu trả lời đúng".
3. Tab **Cài đặt** → **Câu trả lời**: bật **Giới hạn 1 câu trả lời**.
4. Bấm biểu tượng con mắt (Xem trước) và làm thử: ở **Thứ Hai** chọn Có, chọn vài CLB ở Top 1, Top 2 (các Top còn lại để (Bỏ trống)), tick **CLB Cờ vua** và **CLB Văn học**, chọn làm CLB Cờ vua trước, rồi CLB Văn học, rồi "Em không thi thêm CLB nào buổi này". Kiểm tra chỉ hiện đề của đúng hai CLB đó. Các buổi khác chọn "Không, em bận buổi này".

## Bước 3. Gửi cho học sinh

1. Gửi đường dẫn HỌC SINH qua nhóm lớp, email hoặc mã QR.
2. Nhắc học sinh: buổi bận thì chọn "Không"; bấm vào Top 1 và chọn CLB thích nhất trong danh sách, rồi Top 2, ...; mỗi CLB chỉ chọn một lần, Top không dùng thì để (Bỏ trống); tick tối đa 5 CLB muốn thi; chọn làm bài lần lượt theo thứ tự trong danh sách. Chỉ bài của CLB đã tick và đã chọn ở một Top mới được tính điểm.
3. Hết hạn: tab **Câu trả lời**, tắt **Chấp nhận câu trả lời**.

## Bước 4. Chấm điểm và xuất Excel

1. Mở lại dự án Apps Script ở Bước 1. Chọn hàm **chamTheoCLB**, bấm **Chạy**.
2. Nhật ký thực thi hiện đường dẫn **Thư mục kết quả** trên Google Drive, gồm:
   - `BANG_DIEM.xlsx`: điểm từng CLB và trang cảnh báo.
   - `SO_NHAP_CLB.xlsx`: Sổ nhập CLB, tệp DUY NHẤT nạp vào phần mềm.
   - `RAW_PHIEU.xlsx`: mọi câu trả lời, đã chấm từng câu. `DAP_AN.xlsx`: đáp án.
3. Bấm chuột phải vào thư mục, chọn **Tải xuống**, giải nén.

## Bước 5. Nạp vào phần mềm xếp CLB

1. Mở `SO_NHAP_CLB.xlsx`, trang **1. CLB**: điền cột **Chỉ tiêu** (lớn hơn 0) cho mọi CLB. Lưu lại.
2. Cách nhanh: kéo sổ vào phần mềm, xem tóm tắt, bấm **Nhập sổ**. Đọc hết cảnh báo sau khi nạp.
3. Cách kỹ hơn: đưa thư mục kết quả và sổ đã điền chỉ tiêu cho Claude, nói **"xử lí raw"**. Skill `xu-li-raw-forms` chấm lại, soát bất thường, rồi ra một sổ nhập mới và một báo cáo.

## Lỗi thường gặp

| Hiện tượng | Cách xử lí |
|---|---|
| "Chưa biết chấm biểu mẫu nào" | Dán đường dẫn SỬA biểu mẫu vào dòng `const LINK_BIEU_MAU = '...'` ở đầu mã, lưu, chạy lại chamTheoCLB |
| "Không xuất được ... (mã lỗi ...)" | Mạng hoặc Google bận. Chạy lại chamTheoCLB |
| Chạy quá 6 phút, bị ngắt | Biểu mẫu quá dài. Xoá biểu mẫu dở dang, chia đề thành hai tệp Excel, tạo hai biểu mẫu |
| Có hai biểu mẫu giống nhau | Đã chạy taoBieuMau hai lần. Xoá một cái, chỉ gửi học sinh một đường dẫn |
| Học sinh không mở được | Biểu mẫu chưa xuất bản, hoặc đã tắt nhận câu trả lời, hoặc học sinh chưa đăng nhập Google |

