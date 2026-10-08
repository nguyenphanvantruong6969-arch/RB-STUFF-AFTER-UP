# Cài đặt Microsoft Forms cho mẫu "Đăng ký câu lạc bộ và thi tuyển — mẫu"

> **Tệp này do `tao_mau_forms.py` sinh từ `de_thi.json`.** Đừng sửa tay —
> sửa `de_thi.json` rồi chạy lại. Hướng dẫn đầy đủ: `README.md` cùng thư mục.

Biểu mẫu có **26 phần, 67 câu hỏi**: 5 buổi, 15 CLB, trong đó **10 CLB tổ chức thi** (mỗi đề 5 câu × 2 điểm = 10 điểm).

## 1. Bố cục — thứ tự phần CHÍNH LÀ luồng đi của học sinh

| Phần | Tên phần | Câu hỏi | Loại | Bắt buộc |
|---|---|---|---|---|
| 1 | Thông tin học sinh | 1 · `[student_id]` | Text | ✅ |
|  |  | 2 · `[name]` | Text | ✅ |
| 2 | Thứ Hai · Nguyện vọng | 3 · `[thu_2]` | **Ranking** | — |
| 3 | Thứ Hai · Dự thi CLB Cờ vua | 4 · `[thi-clb_covua]` | Choice | ✅ |
| 4 | Thứ Hai · Đề thi CLB Cờ vua | 5 · `[clb_covua-1]` | Choice | ✅ |
|  |  | 6 · `[clb_covua-2]` | Choice | ✅ |
|  |  | 7 · `[clb_covua-3]` | Choice | ✅ |
|  |  | 8 · `[clb_covua-4]` | Choice | ✅ |
|  |  | 9 · `[clb_covua-5]` | Choice | ✅ |
| 5 | Thứ Hai · Dự thi CLB Văn học | 10 · `[thi-clb_vanhoc]` | Choice | ✅ |
| 6 | Thứ Hai · Đề thi CLB Văn học | 11 · `[clb_vanhoc-1]` | Choice | ✅ |
|  |  | 12 · `[clb_vanhoc-2]` | Choice | ✅ |
|  |  | 13 · `[clb_vanhoc-3]` | Choice | ✅ |
|  |  | 14 · `[clb_vanhoc-4]` | Choice | ✅ |
|  |  | 15 · `[clb_vanhoc-5]` | Choice | ✅ |
| 7 | Thứ Ba · Nguyện vọng | 16 · `[thu_3]` | **Ranking** | — |
| 8 | Thứ Ba · Dự thi CLB Tiếng Anh | 17 · `[thi-clb_tienganh]` | Choice | ✅ |
| 9 | Thứ Ba · Đề thi CLB Tiếng Anh | 18 · `[clb_tienganh-1]` | Choice | ✅ |
|  |  | 19 · `[clb_tienganh-2]` | Choice | ✅ |
|  |  | 20 · `[clb_tienganh-3]` | Choice | ✅ |
|  |  | 21 · `[clb_tienganh-4]` | Choice | ✅ |
|  |  | 22 · `[clb_tienganh-5]` | Choice | ✅ |
| 10 | Thứ Ba · Dự thi CLB Mỹ thuật | 23 · `[thi-clb_mythuat]` | Choice | ✅ |
| 11 | Thứ Ba · Đề thi CLB Mỹ thuật | 24 · `[clb_mythuat-1]` | Choice | ✅ |
|  |  | 25 · `[clb_mythuat-2]` | Choice | ✅ |
|  |  | 26 · `[clb_mythuat-3]` | Choice | ✅ |
|  |  | 27 · `[clb_mythuat-4]` | Choice | ✅ |
|  |  | 28 · `[clb_mythuat-5]` | Choice | ✅ |
| 12 | Thứ Tư · Nguyện vọng | 29 · `[thu_4]` | **Ranking** | — |
| 13 | Thứ Tư · Dự thi CLB Robotics | 30 · `[thi-clb_robotics]` | Choice | ✅ |
| 14 | Thứ Tư · Đề thi CLB Robotics | 31 · `[clb_robotics-1]` | Choice | ✅ |
|  |  | 32 · `[clb_robotics-2]` | Choice | ✅ |
|  |  | 33 · `[clb_robotics-3]` | Choice | ✅ |
|  |  | 34 · `[clb_robotics-4]` | Choice | ✅ |
|  |  | 35 · `[clb_robotics-5]` | Choice | ✅ |
| 15 | Thứ Tư · Dự thi CLB Khoa học | 36 · `[thi-clb_khoahoc]` | Choice | ✅ |
| 16 | Thứ Tư · Đề thi CLB Khoa học | 37 · `[clb_khoahoc-1]` | Choice | ✅ |
|  |  | 38 · `[clb_khoahoc-2]` | Choice | ✅ |
|  |  | 39 · `[clb_khoahoc-3]` | Choice | ✅ |
|  |  | 40 · `[clb_khoahoc-4]` | Choice | ✅ |
|  |  | 41 · `[clb_khoahoc-5]` | Choice | ✅ |
| 17 | Thứ Năm · Nguyện vọng | 42 · `[thu_5]` | **Ranking** | — |
| 18 | Thứ Năm · Dự thi CLB Tin học | 43 · `[thi-clb_tinhoc]` | Choice | ✅ |
| 19 | Thứ Năm · Đề thi CLB Tin học | 44 · `[clb_tinhoc-1]` | Choice | ✅ |
|  |  | 45 · `[clb_tinhoc-2]` | Choice | ✅ |
|  |  | 46 · `[clb_tinhoc-3]` | Choice | ✅ |
|  |  | 47 · `[clb_tinhoc-4]` | Choice | ✅ |
|  |  | 48 · `[clb_tinhoc-5]` | Choice | ✅ |
| 20 | Thứ Năm · Dự thi CLB Âm nhạc | 49 · `[thi-clb_amnhac]` | Choice | ✅ |
| 21 | Thứ Năm · Đề thi CLB Âm nhạc | 50 · `[clb_amnhac-1]` | Choice | ✅ |
|  |  | 51 · `[clb_amnhac-2]` | Choice | ✅ |
|  |  | 52 · `[clb_amnhac-3]` | Choice | ✅ |
|  |  | 53 · `[clb_amnhac-4]` | Choice | ✅ |
|  |  | 54 · `[clb_amnhac-5]` | Choice | ✅ |
| 22 | Thứ Sáu · Nguyện vọng | 55 · `[thu_6]` | **Ranking** | — |
| 23 | Thứ Sáu · Dự thi CLB Toán tư duy | 56 · `[thi-clb_toan]` | Choice | ✅ |
| 24 | Thứ Sáu · Đề thi CLB Toán tư duy | 57 · `[clb_toan-1]` | Choice | ✅ |
|  |  | 58 · `[clb_toan-2]` | Choice | ✅ |
|  |  | 59 · `[clb_toan-3]` | Choice | ✅ |
|  |  | 60 · `[clb_toan-4]` | Choice | ✅ |
|  |  | 61 · `[clb_toan-5]` | Choice | ✅ |
| 25 | Thứ Sáu · Dự thi CLB Lịch sử | 62 · `[thi-clb_lichsu]` | Choice | ✅ |
| 26 | Thứ Sáu · Đề thi CLB Lịch sử | 63 · `[clb_lichsu-1]` | Choice | ✅ |
|  |  | 64 · `[clb_lichsu-2]` | Choice | ✅ |
|  |  | 65 · `[clb_lichsu-3]` | Choice | ✅ |
|  |  | 66 · `[clb_lichsu-4]` | Choice | ✅ |
|  |  | 67 · `[clb_lichsu-5]` | Choice | ✅ |

## 2. Đổi 5 câu nguyện vọng sang Ranking

Quick Import không biết loại **Ranking** — các câu `[thu_…]` về tới Forms
sẽ là câu Choice. Với từng câu: bấm **+ Add new → ⌄ → Ranking** ngay dưới
nó, **dán nguyên văn** tiêu đề và các lựa chọn (giữ cả phần `[mã]` và phần
`(club_id)`), để **không bắt buộc**, rồi xoá câu Choice cũ.

## 3. Rẽ nhánh — chỉ 10 chỗ

Chọn câu cổng → **…** → **Add branching**. Đáp án **"Có, em làm bài thi ngay bây giờ"** để nguyên (đi tiếp sang phần đề thi ngay sau). Đáp án **"Không"** đặt **Go to**:

| Câu cổng | "Không" → Go to |
|---|---|
| `[thi-clb_covua]` CLB Cờ vua | **Thứ Hai · Dự thi CLB Văn học** |
| `[thi-clb_vanhoc]` CLB Văn học | **Thứ Ba · Nguyện vọng** |
| `[thi-clb_tienganh]` CLB Tiếng Anh | **Thứ Ba · Dự thi CLB Mỹ thuật** |
| `[thi-clb_mythuat]` CLB Mỹ thuật | **Thứ Tư · Nguyện vọng** |
| `[thi-clb_robotics]` CLB Robotics | **Thứ Tư · Dự thi CLB Khoa học** |
| `[thi-clb_khoahoc]` CLB Khoa học | **Thứ Năm · Nguyện vọng** |
| `[thi-clb_tinhoc]` CLB Tin học | **Thứ Năm · Dự thi CLB Âm nhạc** |
| `[thi-clb_amnhac]` CLB Âm nhạc | **Thứ Sáu · Nguyện vọng** |
| `[thi-clb_toan]` CLB Toán tư duy | **Thứ Sáu · Dự thi CLB Lịch sử** |
| `[thi-clb_lichsu]` CLB Lịch sử | **End of the form** |

Làm xong đề thi CLB này thì Forms **tự** sang phần kế tiếp — đúng là câu
cổng của CLB sau, hoặc nguyện vọng của buổi sau. Không cần đặt thêm nhánh.

## 4. Đáp án và điểm (chế độ Quiz)

Chỉ cần nếu tạo dạng **Quiz**. Mỗi câu đề thi: bấm vào đáp án đúng →
dấu ✔ **Correct answer**, ô **Points** = **2**. Câu cổng, câu nguyện vọng,
mã và tên học sinh: **không** cho điểm.

Bộ chuyển đổi **chấm lại** theo chính bảng này, và báo nếu điểm Forms
chấm lệch — tức là có câu tick nhầm đáp án trên Forms.

**CLB Cờ vua** (`clb_covua`, Thứ Hai)

| Câu | Đáp án đúng |
|---|---|
| `[clb_covua-1]` Quân nào đi theo hình chữ L? | c. Mã |
| `[clb_covua-2]` Muốn nhập thành thì cần điều kiện nào? | a. Vua chưa từng di chuyển |
| `[clb_covua-3]` Tốt đi tới hàng cuối cùng của bàn cờ thì sao? | b. Được phong thành quân khác (trừ Vua) |
| `[clb_covua-4]` Trường hợp nào ván cờ là HOÀ? | b. Bên tới lượt không còn nước đi hợp lệ và không bị chiếu |
| `[clb_covua-5]` Ký hiệu O-O nghĩa là gì? | a. Nhập thành cánh Vua |

**CLB Văn học** (`clb_vanhoc`, Thứ Hai)

| Câu | Đáp án đúng |
|---|---|
| `[clb_vanhoc-1]` Truyện Kiều là tác phẩm của ai? | a. Nguyễn Du |
| `[clb_vanhoc-2]` Câu “Mặt trời xuống biển như hòn lửa” dùng biện pháp tu từ nào? | a. So sánh |
| `[clb_vanhoc-3]` Mỗi cặp câu thơ lục bát gồm những câu nào? | a. Một câu 6 chữ và một câu 8 chữ |
| `[clb_vanhoc-4]` Tiểu thuyết Tắt đèn là của ai? | b. Ngô Tất Tố |
| `[clb_vanhoc-5]` Kể theo ngôi thứ nhất thì người kể xưng là gì? | a. Tôi |

**CLB Tiếng Anh** (`clb_tienganh`, Thứ Ba)

| Câu | Đáp án đúng |
|---|---|
| `[clb_tienganh-1]` She ___ to school every day. | b. goes |
| `[clb_tienganh-2]` Từ trái nghĩa với “ancient” là gì? | a. modern |
| `[clb_tienganh-3]` I have lived here ___ 2020. | a. since |
| `[clb_tienganh-4]` If it rains tomorrow, we ___ at home. | a. will stay |
| `[clb_tienganh-5]` Câu nào đúng ngữ pháp? | b. He doesn't like tea. |

**CLB Mỹ thuật** (`clb_mythuat`, Thứ Ba)

| Câu | Đáp án đúng |
|---|---|
| `[clb_mythuat-1]` Ba màu cơ bản trong hội hoạ truyền thống là gì? | a. Đỏ, vàng, lam |
| `[clb_mythuat-2]` Màu bổ túc của màu đỏ là màu nào? | b. Lục |
| `[clb_mythuat-3]` Luật xa gần giúp bức tranh có điều gì? | c. Cảm giác chiều sâu |
| `[clb_mythuat-4]` Tranh dân gian Đông Hồ thường in trên loại giấy nào? | a. Giấy điệp |
| `[clb_mythuat-5]` Pha màu lam với màu vàng thì được màu gì? | d. Lục |

**CLB Robotics** (`clb_robotics`, Thứ Tư)

| Câu | Đáp án đúng |
|---|---|
| `[clb_robotics-1]` Cảm biến siêu âm trên robot dùng để làm gì? | b. Đo khoảng cách |
| `[clb_robotics-2]` Vòng lặp trong lập trình dùng để làm gì? | a. Lặp lại một nhóm lệnh |
| `[clb_robotics-3]` Động cơ servo khác động cơ DC thường ở điểm nào? | c. Điều khiển được góc quay chính xác |
| `[clb_robotics-4]` Robot tránh vật cản đo được khoảng cách dưới 10 cm thì nên làm gì? | c. Dừng lại hoặc rẽ hướng khác |
| `[clb_robotics-5]` Arduino là gì? | a. Bo mạch vi điều khiển |

**CLB Khoa học** (`clb_khoahoc`, Thứ Tư)

| Câu | Đáp án đúng |
|---|---|
| `[clb_khoahoc-1]` Ở áp suất tiêu chuẩn, nước sôi ở bao nhiêu độ C? | b. 100 |
| `[clb_khoahoc-2]` Cây xanh tạo chất hữu cơ nhờ ánh sáng qua quá trình nào? | c. Quang hợp |
| `[clb_khoahoc-3]` Đơn vị đo lực là gì? | a. Niutơn (N) |
| `[clb_khoahoc-4]` Khí nào chiếm tỉ lệ lớn nhất trong không khí? | d. Nitơ |
| `[clb_khoahoc-5]` Trong thí nghiệm, “biến kiểm soát” là gì? | a. Yếu tố giữ nguyên để so sánh công bằng |

**CLB Tin học** (`clb_tinhoc`, Thứ Năm)

| Câu | Đáp án đúng |
|---|---|
| `[clb_tinhoc-1]` 1 byte bằng bao nhiêu bit? | b. 8 |
| `[clb_tinhoc-2]` Hệ nhị phân dùng những chữ số nào? | a. 0 và 1 |
| `[clb_tinhoc-3]` Số nhị phân 101 bằng bao nhiêu trong hệ thập phân? | b. 5 |
| `[clb_tinhoc-4]` Thuật toán là gì? | c. Dãy hữu hạn các bước để giải một bài toán |
| `[clb_tinhoc-5]` Mật khẩu nào mạnh nhất? | d. T0i#Hoc!2026 |

**CLB Âm nhạc** (`clb_amnhac`, Thứ Năm)

| Câu | Đáp án đúng |
|---|---|
| `[clb_amnhac-1]` Có bao nhiêu tên nốt nhạc cơ bản? | b. 7 |
| `[clb_amnhac-2]` Một nốt tròn dài bằng mấy nốt đen? | c. 4 |
| `[clb_amnhac-3]` Ký hiệu # trong bản nhạc gọi là gì? | a. Dấu thăng |
| `[clb_amnhac-4]` Nhịp 3/4 có ý nghĩa gì? | a. Mỗi ô nhịp 3 phách, mỗi phách là một nốt đen |
| `[clb_amnhac-5]` Bài Tiến quân ca do ai sáng tác? | b. Văn Cao |

**CLB Toán tư duy** (`clb_toan`, Thứ Sáu)

| Câu | Đáp án đúng |
|---|---|
| `[clb_toan-1]` Số tiếp theo của dãy 2, 4, 8, 16 là gì? | d. 32 |
| `[clb_toan-2]` Lớp có 30 học sinh, 40% là nữ. Lớp có bao nhiêu bạn nữ? | b. 12 |
| `[clb_toan-3]` Tổng ba góc trong một tam giác bằng bao nhiêu? | b. 180° |
| `[clb_toan-4]` Ba bạn bắt tay nhau, mỗi cặp bắt đúng một lần. Có bao nhiêu cái bắt tay? | b. 3 |
| `[clb_toan-5]` Số nguyên tố nhỏ nhất là số nào? | c. 2 |

**CLB Lịch sử** (`clb_lichsu`, Thứ Sáu)

| Câu | Đáp án đúng |
|---|---|
| `[clb_lichsu-1]` Chiến thắng Điện Biên Phủ diễn ra năm nào? | b. 1954 |
| `[clb_lichsu-2]` Ngô Quyền đánh thắng quân Nam Hán trên sông nào? | c. Sông Bạch Đằng |
| `[clb_lichsu-3]` Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập vào ngày nào? | b. 2/9/1945 |
| `[clb_lichsu-4]` Vua Quang Trung đại phá quân Thanh vào năm nào? | b. 1789 |
| `[clb_lichsu-5]` Bình Ngô đại cáo do ai viết? | c. Nguyễn Trãi |

## 5. Settings

| Cài đặt | Giá trị | Vì sao |
|---|---|---|
| Who can fill out this form | **Only people in my organization** | Học sinh đăng nhập tài khoản trường |
| **One response per person** | **BẬT** | Đây là bài thi: nộp lại là làm lại tới khi được điểm cao. Bộ chuyển đổi cũng chỉ giữ phiếu **đầu** của mỗi mã học sinh |
| Shuffle questions | **TẮT** | Xáo câu là hỏng rẽ nhánh |
| Shuffle options (từng câu đề thi) | Bật được | Chấm theo nội dung lựa chọn, không theo vị trí |
| Show results automatically (Quiz) | **TẮT** | Bật là em làm trước biết đáp án, chuyền cho em làm sau |
| Start date / End date | Đặt đủ cả hai | Hết giờ tự khoá, không phải canh |
