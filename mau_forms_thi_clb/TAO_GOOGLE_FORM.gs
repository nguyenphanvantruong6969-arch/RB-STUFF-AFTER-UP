/**
 * Dựng biểu mẫu Google Forms "Đăng ký CLB và thi tuyển".
 *
 * TỆP NÀY DO tao_google_forms.py SINH RA. Sửa đề thì sửa THIET_KE_6_PHAN.html
 * rồi chạy lại tao_google_forms.py, không sửa tay danh sách BUOI bên dưới.
 *
 * Cách dùng:
 *   1. Mở script.google.com, bấm "Dự án mới".
 *   2. Xoá hết chữ có sẵn, dán toàn bộ tệp này vào, bấm Lưu.
 *   3. Chọn hàm taoBieuMau ở thanh trên, bấm Chạy, cho phép quyền truy cập.
 *   4. Mở "Nhật ký thực thi" để lấy đường dẫn sửa và đường dẫn gửi học sinh.
 *
 * Mỗi lần chạy tạo một biểu mẫu MỚI trong Google Drive, không sửa biểu mẫu cũ.
 *
 * Chấm điểm theo từng CLB (sau khi học sinh nộp):
 *   Chọn hàm chamTheoCLB, bấm Chạy. Hàm tạo trong Google Drive một thư mục
 *   "Kết quả CLB <ngày giờ>" chứa các tệp Excel: bảng điểm, 3 tệp nạp
 *   phần mềm xếp CLB, dữ liệu raw đã chấm từng câu, và đáp án. Đường dẫn thư mục nằm trong "Nhật ký thực thi".
 *   Nếu biểu mẫu được tạo bằng bản mã cũ (trước khi có hàm này), dán đường
 *   dẫn SỬA biểu mẫu vào LINK_BIEU_MAU bên dưới trước khi chạy.
 */

// Để trống nếu biểu mẫu được tạo bằng chính dự án này sau khi có hàm chamTheoCLB.
const LINK_BIEU_MAU = '';

const TIEU_DE = "Đăng ký CLB và thi tuyển";
const DIEM_CAU = 5;
const TRAN_THI = 5;
const CO_BUOI = "Có";
const KHONG_BUOI = "Không, em bận buổi này";
const CO = "Có, em thi CLB này";
const KHONG = "Không";
const DUNG = "Em không thi thêm CLB nào buổi này";
const KHONG_THI = "Em không thi CLB nào buổi này";
const BO_TRONG = "(Bỏ trống)";

// [{ma, ten, clubs: [{id, name, de: [{q, opts, dung}]}]}]
const BUOI = [
 {
  "ma": "thu_2",
  "ten": "Thứ Hai",
  "clubs": [
   {
    "id": "clb_covua",
    "name": "CLB Cờ vua",
    "de": [
     {
      "q": "Quân nào đi theo hình chữ L?",
      "opts": [
       "Xe",
       "Hậu",
       "Tượng",
       "Mã"
      ],
      "dung": "Mã"
     },
     {
      "q": "Muốn nhập thành thì cần điều kiện nào?",
      "opts": [
       "Xe đã di chuyển trước đó",
       "Vua đang bị chiếu",
       "Vua chưa từng di chuyển",
       "Có quân đứng giữa Vua và Xe"
      ],
      "dung": "Vua chưa từng di chuyển"
     }
    ]
   },
   {
    "id": "clb_vanhoc",
    "name": "CLB Văn học",
    "de": [
     {
      "q": "Truyện Kiều là tác phẩm của ai?",
      "opts": [
       "Nguyễn Du",
       "Nguyễn Trãi",
       "Nguyễn Đình Chiểu",
       "Hồ Xuân Hương"
      ],
      "dung": "Nguyễn Du"
     },
     {
      "q": "Câu “Mặt trời xuống biển như hòn lửa” dùng biện pháp tu từ nào?",
      "opts": [
       "Ẩn dụ",
       "Nói quá",
       "Hoán dụ",
       "So sánh"
      ],
      "dung": "So sánh"
     }
    ]
   },
   {
    "id": "clb_nhiepanh",
    "name": "CLB Nhiếp ảnh",
    "de": [
     {
      "q": "Số khẩu độ nhỏ (ví dụ f/1.8) nghĩa là gì?",
      "opts": [
       "Máy chụp liên tục",
       "Lỗ mở nhỏ, ít ánh sáng vào",
       "Lỗ mở lớn, nhiều ánh sáng vào",
       "Ảnh sẽ thành đen trắng"
      ],
      "dung": "Lỗ mở lớn, nhiều ánh sáng vào"
     },
     {
      "q": "Quy tắc một phần ba giúp bức ảnh thế nào?",
      "opts": [
       "Ảnh có dung lượng nhỏ hơn",
       "Pin dùng lâu hơn",
       "Ảnh sáng hơn",
       "Bố cục cân đối và dễ nhìn"
      ],
      "dung": "Bố cục cân đối và dễ nhìn"
     }
    ]
   },
   {
    "id": "clb_caulong",
    "name": "CLB Cầu lông",
    "de": [
     {
      "q": "Một ván cầu lông thường chơi tới bao nhiêu điểm?",
      "opts": [
       "11",
       "15",
       "25",
       "21"
      ],
      "dung": "21"
     },
     {
      "q": "Quả cầu lông thi đấu thường làm từ lông gì?",
      "opts": [
       "Lông cừu",
       "Lông gà",
       "Lông ngỗng hoặc lông vịt",
       "Lông công"
      ],
      "dung": "Lông ngỗng hoặc lông vịt"
     }
    ]
   },
   {
    "id": "clb_hungbien",
    "name": "CLB Hùng biện",
    "de": [
     {
      "q": "Mở đầu bài nói nên làm gì?",
      "opts": [
       "Đọc nguyên văn tờ giấy",
       "Xin lỗi vì mình nói kém",
       "Nói thật nhanh cho xong",
       "Gây chú ý và nêu chủ đề"
      ],
      "dung": "Gây chú ý và nêu chủ đề"
     },
     {
      "q": "Khi nói trước đông người nên nhìn vào đâu?",
      "opts": [
       "Nhìn người nghe",
       "Nhắm mắt lại",
       "Nhìn lên trần nhà",
       "Nhìn xuống sàn"
      ],
      "dung": "Nhìn người nghe"
     }
    ]
   },
   {
    "id": "clb_sinhhoc",
    "name": "CLB Sinh học",
    "de": [
     {
      "q": "Bộ phận nào của tế bào chứa vật chất di truyền?",
      "opts": [
       "Màng tế bào",
       "Thành tế bào",
       "Nhân tế bào",
       "Không bào"
      ],
      "dung": "Nhân tế bào"
     },
     {
      "q": "Hồng cầu có nhiệm vụ chính là gì?",
      "opts": [
       "Vận chuyển oxy",
       "Làm đông máu",
       "Tiêu hoá thức ăn",
       "Chống vi khuẩn"
      ],
      "dung": "Vận chuyển oxy"
     }
    ]
   },
   {
    "id": "clb_guitar",
    "name": "CLB Guitar",
    "de": [
     {
      "q": "Đàn guitar thông thường có mấy dây?",
      "opts": [
       "4",
       "12",
       "6",
       "7"
      ],
      "dung": "6"
     },
     {
      "q": "Hợp âm Đô trưởng được ký hiệu là gì?",
      "opts": [
       "G",
       "A",
       "D",
       "C"
      ],
      "dung": "C"
     }
    ]
   },
   {
    "id": "clb_baochi",
    "name": "CLB Báo chí",
    "de": [
     {
      "q": "Trước khi đăng một tin, việc cần làm đầu tiên là gì?",
      "opts": [
       "Kiểm tra lại nguồn tin",
       "Xoá tên nguồn tin",
       "Thêm chi tiết cho hấp dẫn",
       "Đăng ngay cho nhanh"
      ],
      "dung": "Kiểm tra lại nguồn tin"
     },
     {
      "q": "Một bản tin tốt phải trả lời được những câu nào?",
      "opts": [
       "Ai, cái gì, ở đâu, khi nào, vì sao, như thế nào",
       "Chỉ cần trả lời ai",
       "Chỉ cần trả lời khi nào",
       "Không cần trả lời câu nào"
      ],
      "dung": "Ai, cái gì, ở đâu, khi nào, vì sao, như thế nào"
     }
    ]
   },
   {
    "id": "clb_truyentranh",
    "name": "CLB Vẽ truyện tranh",
    "de": [
     {
      "q": "Ô chứa lời nói của nhân vật trong truyện tranh gọi là gì?",
      "opts": [
       "Mục lục",
       "Khung tranh",
       "Trang bìa",
       "Bóng thoại"
      ],
      "dung": "Bóng thoại"
     },
     {
      "q": "Truyện tranh Nhật Bản thường được gọi là gì?",
      "opts": [
       "Ngụ ngôn",
       "Comic",
       "Manhwa",
       "Manga"
      ],
      "dung": "Manga"
     }
    ]
   },
   {
    "id": "clb_boiloi",
    "name": "CLB Bơi lội",
    "de": [
     {
      "q": "Kiểu bơi nào nằm ngửa trên mặt nước?",
      "opts": [
       "Bơi bướm",
       "Bơi ếch",
       "Bơi ngửa",
       "Bơi sải"
      ],
      "dung": "Bơi ngửa"
     },
     {
      "q": "Trước khi xuống nước nên làm gì?",
      "opts": [
       "Chạy quanh hồ bơi",
       "Ăn thật no",
       "Nhảy xuống ngay",
       "Khởi động kỹ"
      ],
      "dung": "Khởi động kỹ"
     }
    ]
   }
  ]
 },
 {
  "ma": "thu_3",
  "ten": "Thứ Ba",
  "clubs": [
   {
    "id": "clb_tienganh",
    "name": "CLB Tiếng Anh",
    "de": [
     {
      "q": "She ___ to school every day.",
      "opts": [
       "goes",
       "going",
       "go",
       "gone"
      ],
      "dung": "goes"
     },
     {
      "q": "Từ trái nghĩa với “ancient” là gì?",
      "opts": [
       "old",
       "modern",
       "huge",
       "quiet"
      ],
      "dung": "modern"
     }
    ]
   },
   {
    "id": "clb_mythuat",
    "name": "CLB Mỹ thuật",
    "de": [
     {
      "q": "Ba màu cơ bản trong hội hoạ truyền thống là gì?",
      "opts": [
       "Đỏ, vàng, lam",
       "Đen, trắng, xám",
       "Cam, tím, lục",
       "Đỏ, lục, lam"
      ],
      "dung": "Đỏ, vàng, lam"
     },
     {
      "q": "Màu bổ túc của màu đỏ là màu nào?",
      "opts": [
       "Lục",
       "Vàng",
       "Cam",
       "Tím"
      ],
      "dung": "Lục"
     }
    ]
   },
   {
    "id": "clb_bongda",
    "name": "CLB Bóng đá",
    "de": [
     {
      "q": "Mỗi đội bóng đá có bao nhiêu cầu thủ trên sân?",
      "opts": [
       "9",
       "10",
       "11",
       "12"
      ],
      "dung": "11"
     },
     {
      "q": "Cầu thủ nhận thẻ đỏ thì sao?",
      "opts": [
       "Chỉ bị nhắc nhở",
       "Được đá phạt",
       "Phải rời sân, không được thi đấu tiếp",
       "Được nghỉ giữa hiệp"
      ],
      "dung": "Phải rời sân, không được thi đấu tiếp"
     }
    ]
   },
   {
    "id": "clb_tiengnhat",
    "name": "CLB Tiếng Nhật",
    "de": [
     {
      "q": "Bảng chữ Hiragana dùng cho tiếng nước nào?",
      "opts": [
       "Tiếng Nhật",
       "Tiếng Hàn",
       "Tiếng Trung",
       "Tiếng Thái"
      ],
      "dung": "Tiếng Nhật"
     },
     {
      "q": "“Arigatou” nghĩa là gì?",
      "opts": [
       "Cảm ơn",
       "Xin chào",
       "Tạm biệt",
       "Xin lỗi"
      ],
      "dung": "Cảm ơn"
     }
    ]
   },
   {
    "id": "clb_kich",
    "name": "CLB Kịch",
    "de": [
     {
      "q": "Nhân vật nói một mình để bộc lộ suy nghĩ gọi là gì?",
      "opts": [
       "Độc thoại",
       "Phụ đề",
       "Đối thoại",
       "Lời dẫn chuyện"
      ],
      "dung": "Độc thoại"
     },
     {
      "q": "Ai là người chỉ đạo diễn viên trong một vở kịch?",
      "opts": [
       "Khán giả",
       "Đạo diễn",
       "Nhạc công",
       "Người soát vé"
      ],
      "dung": "Đạo diễn"
     }
    ]
   },
   {
    "id": "clb_hoahoc",
    "name": "CLB Hoá học",
    "de": [
     {
      "q": "Công thức hoá học của nước là gì?",
      "opts": [
       "CO2",
       "NaCl",
       "H2O",
       "O2"
      ],
      "dung": "H2O"
     },
     {
      "q": "Dung dịch có độ pH nhỏ hơn 7 là loại gì?",
      "opts": [
       "Nước cất",
       "Axit",
       "Bazơ",
       "Trung tính"
      ],
      "dung": "Axit"
     }
    ]
   },
   {
    "id": "clb_nauan",
    "name": "CLB Nấu ăn",
    "de": [
     {
      "q": "Vì sao phải rửa tay trước khi nấu ăn?",
      "opts": [
       "Không cần rửa tay",
       "Để giữ vệ sinh, an toàn thực phẩm",
       "Để tay đẹp hơn",
       "Để nấu nhanh hơn"
      ],
      "dung": "Để giữ vệ sinh, an toàn thực phẩm"
     },
     {
      "q": "Thịt sống và đồ ăn chín nên để thế nào?",
      "opts": [
       "Để riêng, dùng thớt riêng",
       "Rửa chung một chậu",
       "Để chung một thớt",
       "Trộn lẫn với nhau"
      ],
      "dung": "Để riêng, dùng thớt riêng"
     }
    ]
   },
   {
    "id": "clb_thietke",
    "name": "CLB Thiết kế đồ hoạ",
    "de": [
     {
      "q": "Hệ màu dùng cho màn hình máy tính là gì?",
      "opts": [
       "CMYK",
       "Pantone",
       "Đen trắng",
       "RGB"
      ],
      "dung": "RGB"
     },
     {
      "q": "Ảnh vector khác ảnh thường ở điểm nào?",
      "opts": [
       "Không in ra được",
       "Luôn có nhiều màu hơn",
       "Chỉ có hai màu",
       "Phóng to không bị vỡ hình"
      ],
      "dung": "Phóng to không bị vỡ hình"
     }
    ]
   },
   {
    "id": "clb_cotuong",
    "name": "CLB Cờ tướng",
    "de": [
     {
      "q": "Quân Tượng trong cờ tướng có được qua sông không?",
      "opts": [
       "Có",
       "Chỉ khi ăn quân",
       "Không",
       "Chỉ ở nước đi đầu"
      ],
      "dung": "Không"
     },
     {
      "q": "Quân Mã bị cản khi nào?",
      "opts": [
       "Khi gặp quân Tướng",
       "Khi đi qua sông",
       "Có quân đứng sát ngay hướng đi",
       "Có quân ở cuối đường đi"
      ],
      "dung": "Có quân đứng sát ngay hướng đi"
     }
    ]
   },
   {
    "id": "clb_mua",
    "name": "CLB Múa",
    "de": [
     {
      "q": "Múa sạp là điệu múa nổi tiếng của dân tộc nào?",
      "opts": [
       "Dân tộc Khmer",
       "Dân tộc Thái",
       "Dân tộc Hoa",
       "Dân tộc Chăm"
      ],
      "dung": "Dân tộc Thái"
     },
     {
      "q": "Khởi động trước khi tập múa giúp gì?",
      "opts": [
       "Tránh chấn thương",
       "Mệt nhanh hơn",
       "Dễ quên động tác",
       "Không có tác dụng"
      ],
      "dung": "Tránh chấn thương"
     }
    ]
   }
  ]
 },
 {
  "ma": "thu_4",
  "ten": "Thứ Tư",
  "clubs": [
   {
    "id": "clb_robotics",
    "name": "CLB Robotics",
    "de": [
     {
      "q": "Cảm biến siêu âm trên robot dùng để làm gì?",
      "opts": [
       "Đo độ ẩm",
       "Đo nhiệt độ",
       "Đo khoảng cách",
       "Nhận biết màu"
      ],
      "dung": "Đo khoảng cách"
     },
     {
      "q": "Vòng lặp trong lập trình dùng để làm gì?",
      "opts": [
       "Nối dây điện",
       "Dừng chương trình",
       "Xoá biến",
       "Lặp lại một nhóm lệnh"
      ],
      "dung": "Lặp lại một nhóm lệnh"
     }
    ]
   },
   {
    "id": "clb_khoahoc",
    "name": "CLB Khoa học",
    "de": [
     {
      "q": "Ở áp suất tiêu chuẩn, nước sôi ở bao nhiêu độ C?",
      "opts": [
       "100",
       "50",
       "90",
       "0"
      ],
      "dung": "100"
     },
     {
      "q": "Cây xanh tạo chất hữu cơ nhờ ánh sáng qua quá trình nào?",
      "opts": [
       "Hô hấp",
       "Quang hợp",
       "Thoát hơi nước",
       "Lên men"
      ],
      "dung": "Quang hợp"
     }
    ]
   },
   {
    "id": "clb_kynang",
    "name": "CLB Kỹ năng sống",
    "de": [
     {
      "q": "Số điện thoại gọi cứu hoả ở Việt Nam là số nào?",
      "opts": [
       "113",
       "114",
       "115",
       "111"
      ],
      "dung": "114"
     },
     {
      "q": "Bị lạc ở nơi đông người, em nên làm gì?",
      "opts": [
       "Đi theo người lạ",
       "Đứng yên ở chỗ dễ thấy và nhờ người có trách nhiệm",
       "Chạy khắp nơi để tìm",
       "Ngồi khóc và chờ"
      ],
      "dung": "Đứng yên ở chỗ dễ thấy và nhờ người có trách nhiệm"
     }
    ]
   },
   {
    "id": "clb_thienvan",
    "name": "CLB Thiên văn",
    "de": [
     {
      "q": "Hành tinh nào gần Mặt Trời nhất?",
      "opts": [
       "Sao Thuỷ",
       "Trái Đất",
       "Sao Kim",
       "Sao Hoả"
      ],
      "dung": "Sao Thuỷ"
     },
     {
      "q": "Trái Đất quay một vòng quanh Mặt Trời mất khoảng bao lâu?",
      "opts": [
       "Một năm",
       "Mười năm",
       "Một tháng",
       "Một ngày"
      ],
      "dung": "Một năm"
     }
    ]
   },
   {
    "id": "clb_dialy",
    "name": "CLB Địa lý",
    "de": [
     {
      "q": "Đỉnh núi cao nhất Việt Nam là đỉnh nào?",
      "opts": [
       "Bà Đen",
       "Lang Biang",
       "Fansipan",
       "Tây Côn Lĩnh"
      ],
      "dung": "Fansipan"
     },
     {
      "q": "Đường xích đạo chia Trái Đất thành hai phần nào?",
      "opts": [
       "Lục địa và đại dương",
       "Ngày và đêm",
       "Bán cầu Bắc và bán cầu Nam",
       "Bán cầu Đông và bán cầu Tây"
      ],
      "dung": "Bán cầu Bắc và bán cầu Nam"
     }
    ]
   },
   {
    "id": "clb_bongchuyen",
    "name": "CLB Bóng chuyền",
    "de": [
     {
      "q": "Mỗi đội bóng chuyền có mấy người trên sân?",
      "opts": [
       "6",
       "5",
       "7",
       "11"
      ],
      "dung": "6"
     },
     {
      "q": "Một đội được chạm bóng tối đa mấy lần trước khi đưa bóng qua lưới?",
      "opts": [
       "2",
       "3",
       "5",
       "4"
      ],
      "dung": "3"
     }
    ]
   },
   {
    "id": "clb_lamphim",
    "name": "CLB Làm phim",
    "de": [
     {
      "q": "Kịch bản phân cảnh (vẽ trước từng cảnh) dùng để làm gì?",
      "opts": [
       "Chọn nhạc nền",
       "Tính tiền vé",
       "Viết phụ đề",
       "Lên kế hoạch cho từng cảnh quay"
      ],
      "dung": "Lên kế hoạch cho từng cảnh quay"
     },
     {
      "q": "Cảnh quay sát khuôn mặt nhân vật gọi là gì?",
      "opts": [
       "Cận cảnh",
       "Toàn cảnh",
       "Trung cảnh",
       "Viễn cảnh"
      ],
      "dung": "Cận cảnh"
     }
    ]
   },
   {
    "id": "clb_moitruong",
    "name": "CLB Môi trường",
    "de": [
     {
      "q": "Loại rác nào sau đây tái chế được?",
      "opts": [
       "Thức ăn thừa",
       "Chai nhựa đã rửa sạch",
       "Vỏ chuối",
       "Khăn giấy đã dùng"
      ],
      "dung": "Chai nhựa đã rửa sạch"
     },
     {
      "q": "Ngày Môi trường Thế giới là ngày nào?",
      "opts": [
       "22 tháng 4",
       "8 tháng 3",
       "1 tháng 6",
       "5 tháng 6"
      ],
      "dung": "5 tháng 6"
     }
    ]
   },
   {
    "id": "clb_tienghan",
    "name": "CLB Tiếng Hàn",
    "de": [
     {
      "q": "Bảng chữ cái tiếng Hàn gọi là gì?",
      "opts": [
       "Kanji",
       "Hangul",
       "Pinyin",
       "Katakana"
      ],
      "dung": "Hangul"
     },
     {
      "q": "“Annyeonghaseyo” nghĩa là gì?",
      "opts": [
       "Chúc ngủ ngon",
       "Xin chào",
       "Tạm biệt",
       "Cảm ơn"
      ],
      "dung": "Xin chào"
     }
    ]
   },
   {
    "id": "clb_khoinghiep",
    "name": "CLB Khởi nghiệp",
    "de": [
     {
      "q": "Lợi nhuận được tính thế nào?",
      "opts": [
       "Chỉ tính chi phí",
       "Doanh thu cộng chi phí",
       "Doanh thu trừ chi phí",
       "Chỉ tính doanh thu"
      ],
      "dung": "Doanh thu trừ chi phí"
     },
     {
      "q": "Khách hàng mục tiêu là ai?",
      "opts": [
       "Nhà cung cấp",
       "Đối thủ cạnh tranh",
       "Mọi người trên thế giới",
       "Nhóm người mà sản phẩm hướng tới"
      ],
      "dung": "Nhóm người mà sản phẩm hướng tới"
     }
    ]
   }
  ]
 },
 {
  "ma": "thu_5",
  "ten": "Thứ Năm",
  "clubs": [
   {
    "id": "clb_tinhoc",
    "name": "CLB Tin học",
    "de": [
     {
      "q": "1 byte bằng bao nhiêu bit?",
      "opts": [
       "10",
       "16",
       "8",
       "2"
      ],
      "dung": "8"
     },
     {
      "q": "Hệ nhị phân dùng những chữ số nào?",
      "opts": [
       "A đến F",
       "0 và 1",
       "1 và 2",
       "0 đến 9"
      ],
      "dung": "0 và 1"
     }
    ]
   },
   {
    "id": "clb_amnhac",
    "name": "CLB Âm nhạc",
    "de": [
     {
      "q": "Có bao nhiêu tên nốt nhạc cơ bản?",
      "opts": [
       "7",
       "12",
       "5",
       "8"
      ],
      "dung": "7"
     },
     {
      "q": "Một nốt tròn dài bằng mấy nốt đen?",
      "opts": [
       "4",
       "8",
       "1",
       "2"
      ],
      "dung": "4"
     }
    ]
   },
   {
    "id": "clb_tinhnguyen",
    "name": "CLB Tình nguyện",
    "de": [
     {
      "q": "Hoạt động tình nguyện là gì?",
      "opts": [
       "Bài tập bắt buộc có điểm",
       "Hoạt động quảng cáo",
       "Tự nguyện giúp cộng đồng, không nhận tiền công",
       "Làm thêm có lương"
      ],
      "dung": "Tự nguyện giúp cộng đồng, không nhận tiền công"
     },
     {
      "q": "Quyên góp quần áo cũ thì nên làm gì?",
      "opts": [
       "Góp cả đồ đã rách nát",
       "Nhét chung vào một túi",
       "Để nguyên đồ bẩn",
       "Giặt sạch và phân loại trước"
      ],
      "dung": "Giặt sạch và phân loại trước"
     }
    ]
   },
   {
    "id": "clb_vatly",
    "name": "CLB Vật lý",
    "de": [
     {
      "q": "Đơn vị đo điện trở là gì?",
      "opts": [
       "Oát",
       "Vôn",
       "Ôm",
       "Ampe"
      ],
      "dung": "Ôm"
     },
     {
      "q": "Ánh sáng đi nhanh nhất trong môi trường nào?",
      "opts": [
       "Chân không",
       "Kim loại",
       "Nước",
       "Thuỷ tinh"
      ],
      "dung": "Chân không"
     }
    ]
   },
   {
    "id": "clb_hopxuong",
    "name": "CLB Hợp xướng",
    "de": [
     {
      "q": "Giọng nữ cao nhất trong hợp xướng gọi là gì?",
      "opts": [
       "Soprano",
       "Alto",
       "Tenor",
       "Bass"
      ],
      "dung": "Soprano"
     },
     {
      "q": "Giọng nam trầm nhất gọi là gì?",
      "opts": [
       "Tenor",
       "Bass",
       "Alto",
       "Soprano"
      ],
      "dung": "Bass"
     }
    ]
   },
   {
    "id": "clb_tranhbien",
    "name": "CLB Tranh biện",
    "de": [
     {
      "q": "Một lập luận tốt cần có những gì?",
      "opts": [
       "Chỉ cần cảm xúc",
       "Nói thật to",
       "Chê bai người khác",
       "Luận điểm, dẫn chứng và giải thích"
      ],
      "dung": "Luận điểm, dẫn chứng và giải thích"
     },
     {
      "q": "Khi phản bác, em nên nhắm vào đâu?",
      "opts": [
       "Trường của đối phương",
       "Lập luận của đối phương",
       "Ngoại hình đối phương",
       "Giọng nói đối phương"
      ],
      "dung": "Lập luận của đối phương"
     }
    ]
   },
   {
    "id": "clb_vothuat",
    "name": "CLB Võ thuật",
    "de": [
     {
      "q": "Vovinam là võ thuật của nước nào?",
      "opts": [
       "Hàn Quốc",
       "Nhật Bản",
       "Thái Lan",
       "Việt Nam"
      ],
      "dung": "Việt Nam"
     },
     {
      "q": "Karate bắt nguồn từ nước nào?",
      "opts": [
       "Hàn Quốc",
       "Trung Quốc",
       "Brazil",
       "Nhật Bản"
      ],
      "dung": "Nhật Bản"
     }
    ]
   },
   {
    "id": "clb_game",
    "name": "CLB Lập trình game",
    "de": [
     {
      "q": "Scratch là gì?",
      "opts": [
       "Một hệ điều hành",
       "Một trình duyệt web",
       "Công cụ lập trình bằng cách kéo thả khối lệnh",
       "Một máy chơi game"
      ],
      "dung": "Công cụ lập trình bằng cách kéo thả khối lệnh"
     },
     {
      "q": "Biến trong lập trình dùng để làm gì?",
      "opts": [
       "Nối mạng",
       "Lưu một giá trị để dùng lại",
       "Vẽ hình tròn",
       "Tắt máy tính"
      ],
      "dung": "Lưu một giá trị để dùng lại"
     }
    ]
   },
   {
    "id": "clb_sach",
    "name": "CLB Đọc sách",
    "de": [
     {
      "q": "Truyện ngắn “Lão Hạc” là của ai?",
      "opts": [
       "Tô Hoài",
       "Nam Cao",
       "Thạch Lam",
       "Kim Lân"
      ],
      "dung": "Nam Cao"
     },
     {
      "q": "“Dế Mèn phiêu lưu ký” là của ai?",
      "opts": [
       "Xuân Diệu",
       "Tô Hoài",
       "Nam Cao",
       "Nguyễn Nhật Ánh"
      ],
      "dung": "Tô Hoài"
     }
    ]
   },
   {
    "id": "clb_thucong",
    "name": "CLB Thủ công",
    "de": [
     {
      "q": "Nghệ thuật gấp giấy của Nhật Bản gọi là gì?",
      "opts": [
       "Bonsai",
       "Sushi",
       "Ikebana",
       "Origami"
      ],
      "dung": "Origami"
     },
     {
      "q": "Keo nến thường dùng với dụng cụ nào?",
      "opts": [
       "Máy khâu",
       "Thước kẻ",
       "Kéo",
       "Súng bắn keo"
      ],
      "dung": "Súng bắn keo"
     }
    ]
   }
  ]
 },
 {
  "ma": "thu_6",
  "ten": "Thứ Sáu",
  "clubs": [
   {
    "id": "clb_toan",
    "name": "CLB Toán tư duy",
    "de": [
     {
      "q": "Số tiếp theo của dãy 2, 4, 8, 16 là gì?",
      "opts": [
       "18",
       "32",
       "24",
       "20"
      ],
      "dung": "32"
     },
     {
      "q": "Lớp có 30 học sinh, 40% là nữ. Lớp có bao nhiêu bạn nữ?",
      "opts": [
       "18",
       "14",
       "10",
       "12"
      ],
      "dung": "12"
     }
    ]
   },
   {
    "id": "clb_lichsu",
    "name": "CLB Lịch sử",
    "de": [
     {
      "q": "Chiến thắng Điện Biên Phủ diễn ra năm nào?",
      "opts": [
       "1954",
       "1975",
       "1945",
       "1968"
      ],
      "dung": "1954"
     },
     {
      "q": "Ngô Quyền đánh thắng quân Nam Hán trên sông nào?",
      "opts": [
       "Sông Hương",
       "Sông Như Nguyệt",
       "Sông Hồng",
       "Sông Bạch Đằng"
      ],
      "dung": "Sông Bạch Đằng"
     }
    ]
   },
   {
    "id": "clb_bongro",
    "name": "CLB Bóng rổ",
    "de": [
     {
      "q": "Một cú ném từ ngoài vạch ba điểm được mấy điểm?",
      "opts": [
       "3",
       "4",
       "2",
       "1"
      ],
      "dung": "3"
     },
     {
      "q": "Mỗi đội bóng rổ có mấy người trên sân?",
      "opts": [
       "5",
       "11",
       "7",
       "6"
      ],
      "dung": "5"
     }
    ]
   },
   {
    "id": "clb_tiengtrung",
    "name": "CLB Tiếng Trung",
    "de": [
     {
      "q": "Cách ghi âm tiếng Trung bằng chữ cái Latinh gọi là gì?",
      "opts": [
       "Kanji",
       "Romaji",
       "Pinyin",
       "Hangul"
      ],
      "dung": "Pinyin"
     },
     {
      "q": "“Nǐ hǎo” nghĩa là gì?",
      "opts": [
       "Xin chào",
       "Cảm ơn",
       "Tạm biệt",
       "Xin lỗi"
      ],
      "dung": "Xin chào"
     }
    ]
   },
   {
    "id": "clb_socuu",
    "name": "CLB Sơ cứu",
    "de": [
     {
      "q": "Số điện thoại cấp cứu y tế ở Việt Nam là số nào?",
      "opts": [
       "114",
       "115",
       "116",
       "113"
      ],
      "dung": "115"
     },
     {
      "q": "Bị bỏng nhẹ thì nên làm gì trước tiên?",
      "opts": [
       "Bôi kem đánh răng",
       "Chườm đá thật lâu",
       "Chọc vỡ chỗ phồng",
       "Xả nước mát lên chỗ bỏng"
      ],
      "dung": "Xả nước mát lên chỗ bỏng"
     }
    ]
   },
   {
    "id": "clb_kinhte",
    "name": "CLB Kinh tế",
    "de": [
     {
      "q": "Lạm phát là gì?",
      "opts": [
       "Giá cả nói chung tăng lên theo thời gian",
       "Giá cả nói chung giảm xuống",
       "Lương tăng gấp đôi",
       "Ngân hàng đóng cửa"
      ],
      "dung": "Giá cả nói chung tăng lên theo thời gian"
     },
     {
      "q": "Tiết kiệm là gì?",
      "opts": [
       "Để dành một phần tiền kiếm được",
       "Đi vay tiền",
       "Mua thật nhiều đồ",
       "Tiêu hết số tiền có"
      ],
      "dung": "Để dành một phần tiền kiếm được"
     }
    ]
   },
   {
    "id": "clb_dienkinh",
    "name": "CLB Điền kinh",
    "de": [
     {
      "q": "Cự ly chạy ngắn phổ biến nhất là bao nhiêu?",
      "opts": [
       "42 km",
       "10 km",
       "100 m",
       "5 km"
      ],
      "dung": "100 m"
     },
     {
      "q": "Chạy marathon dài khoảng bao nhiêu?",
      "opts": [
       "42 km",
       "10 km",
       "21 km",
       "100 km"
      ],
      "dung": "42 km"
     }
    ]
   },
   {
    "id": "clb_bongban",
    "name": "CLB Bóng bàn",
    "de": [
     {
      "q": "Một ván bóng bàn chơi tới mấy điểm?",
      "opts": [
       "11",
       "15",
       "21",
       "25"
      ],
      "dung": "11"
     },
     {
      "q": "Bóng bàn còn được gọi là gì?",
      "opts": [
       "Bóng ném",
       "Cầu mây",
       "Ping pong",
       "Quần vợt"
      ],
      "dung": "Ping pong"
     }
    ]
   },
   {
    "id": "clb_dangian",
    "name": "CLB Văn hoá dân gian",
    "de": [
     {
      "q": "Tết Trung thu vào ngày nào âm lịch?",
      "opts": [
       "Mùng 5 tháng Năm",
       "Rằm tháng Giêng",
       "Rằm tháng Tám",
       "Mùng 1 tháng Giêng"
      ],
      "dung": "Rằm tháng Tám"
     },
     {
      "q": "Bánh chưng gắn với dịp nào?",
      "opts": [
       "Rằm tháng Bảy",
       "Tết Trung thu",
       "Tết Đoan ngọ",
       "Tết Nguyên đán"
      ],
      "dung": "Tết Nguyên đán"
     }
    ]
   },
   {
    "id": "clb_truyenthong",
    "name": "CLB Truyền thông",
    "de": [
     {
      "q": "Muốn dùng ảnh của người khác thì cần làm gì?",
      "opts": [
       "Đổi màu ảnh là được",
       "Xin phép và ghi nguồn",
       "Cứ dùng, không cần hỏi",
       "Cắt bỏ tên tác giả"
      ],
      "dung": "Xin phép và ghi nguồn"
     },
     {
      "q": "Bài đăng cho trang của trường nên thế nào?",
      "opts": [
       "Đăng tin chưa kiểm tra",
       "Rõ ràng, đúng thông tin, lời lẽ lịch sự",
       "Càng nhiều chữ viết tắt càng tốt",
       "Dùng ảnh mờ cho nhanh"
      ],
      "dung": "Rõ ràng, đúng thông tin, lời lẽ lịch sự"
     }
    ]
   }
  ]
 }
];

function taoBieuMau() {
  const form = FormApp.create(TIEU_DE);
  form.setIsQuiz(true)
      .setDescription('Mỗi buổi: xếp hạng CLB em muốn vào, tick các CLB muốn thi (tối đa ' + TRAN_THI + '), rồi chọn lần lượt CLB để làm bài. Buổi nào bận thì chọn "Không, em bận buổi này".')
      .setShuffleQuestions(false)
      .setProgressBar(true)
      .setShowLinkToRespondAgain(false)
      .setPublishingSummary(false)
      .setConfirmationMessage('Em đã nộp phiếu. Cảm ơn em.');

  form.addTextItem().setTitle('[student_id] Mã học sinh').setRequired(true);
  form.addTextItem().setTitle('[name] Họ và tên').setRequired(true);

  // Bước 1: tạo đủ các trang và câu hỏi theo đúng thứ tự. Mỗi buổi:
  //   trang buổi      [di-<buổi>]        có đăng ký buổi này không
  //   trang xếp hạng  [<buổi>]           lưới Top 1..Top 10, mỗi CLB dùng một lần
  //                   [chon-<buổi>]      tick CLB muốn thi, Google chặn quá 5
  //   trang chọn đầu  [thi-<buổi>]       "Em thi CLB nào trước?"
  //   đề CLB i, rồi   [thi-sau-<clb i>]  "Em thi CLB nào tiếp theo?" (chỉ CLB đứng sau i)
  // Học sinh chỉ thấy đề của CLB em chọn.
  const nhan = function (c) { return c.name + ' (' + c.id + ')'; };
  const days = BUOI.map(function (d) {
    const trangBuoi = form.addPageBreakItem().setTitle(d.ten);
    const cauBuoi = form.addMultipleChoiceItem()
        .setTitle('[di-' + d.ma + '] Em có đăng ký sinh hoạt ' + d.ten + ' không?')
        .setRequired(true);

    const trangXep = form.addPageBreakItem()
        .setTitle(d.ten + ': nguyện vọng và chọn CLB thi')
        .setHelpText('Top 1 là CLB em thích nhất. Bấm vào từng Top để chọn CLB trong danh sách. '
            + 'Mỗi CLB chỉ chọn một lần. Không muốn thêm thì để ' + BO_TRONG + '.');
    // Mỗi Top một danh sách thả xuống. Google không chặn được chọn trùng giữa
    // các danh sách: chamTheoCLB giữ Top cao hơn và ghi cảnh báo.
    d.clubs.forEach(function (_, k) {
      form.addListItem()
          .setTitle('[' + d.ma + '-top-' + (k + 1) + '] Top ' + (k + 1))
          .setChoiceValues([BO_TRONG].concat(d.clubs.map(nhan)));
    });

    // Chỉ CLB có đề thi mới có trong câu tick và các trang chọn làm bài.
    // Buổi không có CLB nào thi thì bỏ hẳn phần này.
    const coThi = d.clubs.filter(function (c) { return c.de.length; });
    if (!coThi.length) {
      return {trangBuoi: trangBuoi, cauBuoi: cauBuoi, trangXep: trangXep, chonDau: null, clubs: []};
    }

    // Google chặn cứng: không tick được quá TRAN_THI CLB. Chỉ bài thi của CLB
    // đã tick ở đây mới được tính điểm (xem chamTheoCLB).
    const chon = form.addCheckboxItem()
        .setTitle('[chon-' + d.ma + '] Chọn các CLB em muốn thi ' + d.ten + ' (tối đa ' + TRAN_THI + ')')
        .setHelpText('Không thi CLB nào thì bỏ trống. Chỉ bài thi của CLB em tick ở đây mới được tính điểm.')
        .setChoiceValues(coThi.map(nhan));
    chon.setValidation(FormApp.createCheckboxValidation()
        .setHelpText('Chỉ được chọn tối đa ' + TRAN_THI + ' CLB.')
        .requireSelectAtMost(TRAN_THI)
        .build());

    form.addPageBreakItem().setTitle(d.ten + ': làm bài thi');
    const chonDau = form.addMultipleChoiceItem()
        .setTitle('[thi-' + d.ma + '] Em thi CLB nào trước? Chọn một CLB em đã tick. Làm xong sẽ được chọn CLB tiếp theo.')
        .setRequired(true);

    const clubs = coThi.map(function (c, i) {
      const trangDe = form.addPageBreakItem().setTitle('Đề thi ' + c.name);
      c.de.forEach(function (q, j) {
        const it = form.addMultipleChoiceItem()
            .setTitle('[' + c.id + '-' + (j + 1) + '] ' + q.q)
            .setPoints(DIEM_CAU)
            .setRequired(true);
        it.setChoices(q.opts.map(function (o) { return it.createChoice(o, o === q.dung); }));
      });
      // Trang "tiếp theo" đứng ngay sau đề, nên làm xong đề là Google tự sang.
      // CLB thi cuối danh sách không có trang này: làm xong là sang buổi sau.
      let tiep = null;
      if (i + 1 < coThi.length) {
        form.addPageBreakItem().setTitle(d.ten + ': CLB tiếp theo');
        tiep = form.addMultipleChoiceItem()
            .setTitle('[thi-sau-' + c.id + '] Em thi CLB nào tiếp theo? Chỉ còn các CLB đứng sau ' + c.name + ' trong danh sách.')
            .setRequired(true);
      }
      return {c: c, trangDe: trangDe, tiep: tiep};
    });
    return {trangBuoi: trangBuoi, cauBuoi: cauBuoi, trangXep: trangXep, chonDau: chonDau, clubs: clubs};
  });

  // Bước 2: nối rẽ nhánh.
  days.forEach(function (d, k) {
    const sau = k + 1 < days.length ? days[k + 1].trangBuoi : FormApp.PageNavigationType.SUBMIT;
    d.cauBuoi.setChoices([
      d.cauBuoi.createChoice(CO_BUOI, d.trangXep),
      d.cauBuoi.createChoice(KHONG_BUOI, sau)
    ]);
    if (!d.chonDau) return;
    // Danh sách lựa chọn: các CLB thi từ vị trí `tu` trở đi, cộng lựa chọn dừng.
    const luaChon = function (item, tu, chuDung) {
      const ds = [];
      for (let j = tu; j < d.clubs.length; j++) ds.push(item.createChoice(nhan(d.clubs[j].c), d.clubs[j].trangDe));
      ds.push(item.createChoice(chuDung, sau));
      item.setChoices(ds);
    };
    luaChon(d.chonDau, 0, KHONG_THI);
    d.clubs.forEach(function (x, i) { if (x.tiep) luaChon(x.tiep, i + 1, DUNG); });
  });

  // Google Forms mới có nút "Xuất bản": chưa xuất bản thì học sinh không mở được.
  // Bản Apps Script cũ không có hàm này nên kiểm tra trước khi gọi.
  if (typeof form.setPublished === 'function') form.setPublished(true);
  PropertiesService.getScriptProperties().setProperty('FORM_ID', form.getId());
  Logger.log('Đường dẫn để SỬA biểu mẫu: ' + form.getEditUrl());
  Logger.log('Đường dẫn gửi HỌC SINH: ' + form.getPublishedUrl());
}

function moBieuMau_() {
  if (LINK_BIEU_MAU) return FormApp.openByUrl(LINK_BIEU_MAU);
  const id = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  if (id) return FormApp.openById(id);
  throw new Error('Chưa biết chấm biểu mẫu nào. Dán đường dẫn SỬA biểu mẫu vào LINK_BIEU_MAU ở đầu tệp rồi chạy lại.');
}

/**
 * Đọc bảng lưới xếp hạng (biểu mẫu cũ) thành [{id, top}] sắp theo top. Nhận hai kiểu lưới:
 *   bản mới: dòng thứ k là "Top k", ô chọn là "Tên CLB (mã)";
 *   bản cũ:  dòng thứ k là CLB thứ k trong danh sách, ô chọn là "Hạng n".
 */
function docTop_(d, mang) {
  const ds = [];
  [].concat(mang || []).forEach(function (v, k) {
    const id = maClb_(v);
    if (id) { ds.push({id: id, top: k + 1}); return; }
    const n = parseInt(String(v == null ? '' : v).replace(/\D/g, ''), 10);
    if (!isNaN(n) && d.clubs[k]) ds.push({id: d.clubs[k].id, top: n});
  });
  return ds.sort(function (a, b) { return a.top - b.top; });
}

/**
 * Xếp hạng của một phiếu trong một buổi, [{id, top}] sắp theo top.
 * Biểu mẫu mới: mỗi Top một câu thả xuống [<buổi>-top-k]. Biểu mẫu cũ: một
 * bảng lưới [<buổi>] (docTop_ đọc được cả hai kiểu lưới).
 */
function docTopPhieu_(d, tl) {
  const ds = [];
  let coThaXuong = false;
  d.clubs.forEach(function (_, k) {
    const ma = d.ma + '-top-' + (k + 1);
    if (!(ma in tl)) return;
    coThaXuong = true;
    const id = maClb_(tl[ma]);
    if (id) ds.push({id: id, top: k + 1});
  });
  return coThaXuong ? ds : docTop_(d, tl[d.ma]);
}

function maClb_(v) {
  const m = String(v == null ? '' : v).match(/\(([A-Za-z0-9_]+)\)\s*$/);
  return m ? m[1] : '';
}

function chuanHoa_(s) {
  return String(s == null ? '' : s).trim().replace(/\s+/g, ' ').toLowerCase();
}

/**
 * Chấm lại mọi phiếu theo đáp án trong BUOI, tách điểm từng CLB (thang 10),
 * và ghi vào một thư mục "Kết quả CLB <ngày giờ>":
 *   SO_NHAP_CLB.xlsx    Sổ nhập CLB: tệp DUY NHẤT kéo vào phần mềm. Trang
 *                       "1. CLB" (điền cột Chỉ tiêu trước khi nạp) và trang
 *                       "2. Học sinh" (nguyện vọng, điểm cạnh CLB đã thi)
 *   BANG_DIEM.xlsx      trang Bảng điểm (mỗi em một dòng, mỗi CLB có thi một
 *                       cột) và trang Cảnh báo (phiếu bị bỏ và lý do)
 *   RAW_PHIEU.xlsx      mọi câu trả lời, đã chấm từng câu
 *   DAP_AN.xlsx         đáp án. Định dạng hai tệp này: DINH_DANG_RAW.md.
 */
function chamTheoCLB() {
  const form = moBieuMau_();
  const phieu = form.getResponses();
  const daCo = {};
  const hocSinh = [];
  const canhBao = [];

  const META = moTaCau_();
  const raw = [COT_RAW];

  phieu.forEach(function (r, i) {
    const tl = {};
    const cacCau = [];
    r.getItemResponses().forEach(function (ir) {
      const m = String(ir.getItem().getTitle()).match(/^\s*\[([^\]]+)\]\s*(.*)$/);
      if (!m) return;
      let diemForms = '';
      try { const s = ir.getScore(); if (s !== null && s !== undefined) diemForms = s; } catch (e) {}
      tl[m[1]] = ir.getResponse();
      cacCau.push({ma: m[1], cau: m[2], tl: ir.getResponse(), diemForms: diemForms});
    });
    const sid = String(tl.student_id || '').trim();
    const dong = 'Phiếu thứ ' + (i + 1);
    // Cách xử lí từng CLB trong phiếu: {club_id: [được tính 1/0, ghi chú]}.
    const xuLi = {};
    let trangThai = 'giu';

    if (!sid) {
      trangThai = 'bo_khong_ma';
      canhBao.push([dong, '', 'Không có mã học sinh, bỏ cả phiếu']);
    } else if (daCo[sid]) {
      trangThai = 'bo_nop_trung';
      canhBao.push([dong, sid, 'Nộp lần nữa. Bỏ phiếu này, giữ phiếu đầu (' + daCo[sid] + ')']);
    } else {
      daCo[sid] = dong;
      const hs = {sid: sid, ten: String(tl.name || '').trim(), nv: {}, diem: {}, thi: []};
      BUOI.forEach(function (d) {
        if (tl['di-' + d.ma] !== CO_BUOI) return;
        // Bảng lưới: dòng Top k nhận "Tên (mã)" của CLB em chọn. Bỏ trống một
        // Top ở giữa thì dồn lên và báo.
        const top = docTopPhieu_(d, tl);
        let truoc = 0;
        const topCua = {};
        const nv = [];
        top.forEach(function (x) {
          if (x.top !== truoc + 1) {
            canhBao.push([dong, sid, d.ten + ': bỏ trống Top ' + (truoc + 1) + ' nhưng có chọn Top ' + x.top + ', đã dồn lên.']);
          }
          truoc = x.top;
          if (topCua[x.id]) {
            canhBao.push([dong, sid, d.ten + ': chọn ' + x.id + ' ở cả Top ' + topCua[x.id] + ' và Top ' + x.top + ', giữ Top ' + topCua[x.id] + '.']);
            return;
          }
          topCua[x.id] = x.top;
          nv.push(x.id);
        });
        if (!nv.length) canhBao.push([dong, sid, d.ten + ': đăng ký buổi nhưng không xếp CLB nào.']);
        hs.nv[d.ma] = nv;

        // CLB em đã tick ở câu [chon-...]: Google trả về mảng chữ "Tên (mã)".
        const daTick = {};
        [].concat(tl['chon-' + d.ma] || []).forEach(function (v) {
          const m = String(v).match(/\(([A-Za-z0-9_]+)\)\s*$/);
          if (m) daTick[m[1]] = true;
        });

        // CLB em đã chọn làm bài: ở trang "thi CLB nào trước" và các trang "tiếp theo".
        const daLam = {};
        [tl['thi-' + d.ma]].concat(d.clubs.map(function (c) { return tl['thi-sau-' + c.id]; }))
            .forEach(function (v) { const id = maClb_(v); if (id) daLam[id] = true; });
        // Biểu mẫu bản cũ: mỗi CLB một câu [thi-<mã CLB>] trả lời "Có, em thi CLB này".
        d.clubs.forEach(function (c) { if (tl['thi-' + c.id] === CO) daLam[c.id] = true; });

        let soThi = 0;
        d.clubs.forEach(function (c) {
          const lam = !!daLam[c.id];
          if (!lam) {
            if (daTick[c.id]) canhBao.push([dong, sid, d.ten + ': tick ' + c.name + ' nhưng không làm bài.']);
            return;
          }
          if (!daTick[c.id]) {
            xuLi[c.id] = [0, 'khong_tick'];
            canhBao.push([dong, sid, d.ten + ': làm bài ' + c.name + ' nhưng không tick ở câu chọn CLB thi, không tính điểm.']);
            return;
          }
          if (nv.indexOf(c.id) < 0) {
            xuLi[c.id] = [0, 'khong_xep_hang'];
            canhBao.push([dong, sid, d.ten + ': làm bài ' + c.name + ' nhưng không chọn CLB này ở Top nào, không tính điểm.']);
            return;
          }
          // Phòng hờ: Google đã chặn tick quá TRAN_THI, nhưng biểu mẫu có thể bị sửa tay.
          if (soThi >= TRAN_THI) {
            xuLi[c.id] = [0, 'qua_tran'];
            canhBao.push([dong, sid, d.ten + ': quá ' + TRAN_THI + ' CLB, bỏ bài ' + c.name + '.']);
            return;
          }
          soThi++;
          xuLi[c.id] = [1, ''];
          let dung = 0;
          c.de.forEach(function (q, j) {
            if (chuanHoa_(tl[c.id + '-' + (j + 1)]) === chuanHoa_(q.dung)) dung++;
          });
          hs.diem[c.id] = dung * DIEM_CAU;
          hs.thi.push(c.id);
        });
      });
      hocSinh.push(hs);
    }

    ghiRaw_(raw, META, i + 1, r, sid, trangThai, xuLi, cacCau);
  });

  const luc = Utilities.formatDate(new Date(), 'Asia/Ho_Chi_Minh', 'yyyy-MM-dd HH-mm');
  const thuMuc = DriveApp.createFolder('Kết quả CLB ' + luc);
  const ss = SpreadsheetApp.create('BANG_DIEM ' + luc);
  DriveApp.getFileById(ss.getId()).moveTo(thuMuc);

  // Bảng điểm
  const coThi = [];
  BUOI.forEach(function (d) { d.clubs.forEach(function (c) { if (c.de.length) coThi.push(c); }); });
  const bang = [['Mã HS', 'Họ tên'].concat(coThi.map(function (c) { return c.name; })).concat(['Số CLB đã thi'])];
  hocSinh.forEach(function (h) {
    bang.push([h.sid, h.ten].concat(coThi.map(function (c) {
      return h.diem.hasOwnProperty(c.id) ? h.diem[c.id] : '';
    })).concat([h.thi.length]));
  });
  ghiTrang_(ss.getSheets()[0].setName('Bảng điểm'), bang, false);

  // Sổ nhập CLB: MỘT tệp phần mềm nhận (bố cục như so_nhap.py của phần mềm).
  // Trang "2. Học sinh": mỗi em một dòng NV1, Điểm 1, NV2, Điểm 2…; nguyện
  // vọng các buổi nối nhau, điểm đặt ngay cạnh CLB em đã thi.
  // Sổ chọn CLB theo TÊN nên tên phải riêng: CLB cùng tên ở buổi khác
  // (vd "CLB Cờ vua" Thứ Hai và Thứ Năm) thêm tên buổi vào sau.
  const tenClb = {}, daDung = {};
  BUOI.forEach(function (d) {
    d.clubs.forEach(function (c) {
      let ten = c.name;
      if (daDung[ten.toLowerCase()]) ten = c.name + ' (' + d.ten + ')';
      if (daDung[ten.toLowerCase()]) ten = c.name + ' (' + c.id + ')';
      daDung[ten.toLowerCase()] = true;
      tenClb[c.id] = ten;
    });
  });
  const soNv = Math.max.apply(null, [1].concat(hocSinh.map(function (h) {
    return BUOI.reduce(function (n, d) { return n + (h.nv[d.ma] || []).length; }, 0);
  })));
  // Không có cột Nhóm ưu tiên: biểu mẫu không hỏi nhóm, và cột vắng mặt
  // nghĩa là phần mềm GIỮ nhóm đã gán (cột có mà ô trống thì là bỏ nhóm).
  const tHs = ['Mã HS', 'Họ tên'];
  for (let i = 1; i <= soNv; i++) tHs.push('NV' + i, 'Điểm ' + i);
  const soHs = [tHs].concat(hocSinh.map(function (h) {
    const row = [h.sid, h.ten];
    BUOI.forEach(function (d) {
      (h.nv[d.ma] || []).forEach(function (id) {
        row.push(tenClb[id] || id, h.diem.hasOwnProperty(id) ? h.diem[id] : '');
      });
    });
    while (row.length < tHs.length) row.push('');
    return row;
  }));

  ghiTrang_(ss.insertSheet('Cảnh báo'),
      [['Phiếu', 'Mã HS', 'Nội dung']].concat(canhBao.length ? canhBao : [['', '', 'Không có cảnh báo nào.']]), false);

  // Trang "1. CLB". Cột Chỉ tiêu để trống: nhà trường tự điền ngay trong sổ.
  const soClb = [['Tên CLB', 'Buổi', 'Chỉ tiêu', 'Suất ưu tiên', 'Nhóm ưu tiên', 'Mã CLB']];
  BUOI.forEach(function (d) { d.clubs.forEach(function (c) { soClb.push([tenClb[c.id], d.ma, '', '', '', c.id]); }); });

  SpreadsheetApp.flush();
  xuatExcel_(ss.getId(), thuMuc, 'BANG_DIEM.xlsx');
  taoSoNhap_(thuMuc, soClb, soHs);

  taoTepNap_(thuMuc, 'RAW_PHIEU', raw);
  taoTepNap_(thuMuc, 'DAP_AN', bangDapAn_());

  Logger.log('Đã chấm ' + hocSinh.length + ' học sinh.');
  Logger.log('Thư mục kết quả: ' + thuMuc.getUrl());
  if (canhBao.length) Logger.log('Có ' + canhBao.length + ' cảnh báo, xem trang "Cảnh báo" trong BANG_DIEM.xlsx.');
  Logger.log('Nhớ điền cột Chỉ tiêu ở trang "1. CLB" của SO_NHAP_CLB.xlsx rồi kéo sổ vào phần mềm.');
}

// ------------------------------------------------------------------------
// Dữ liệu raw và đáp án. Định dạng mô tả trong DINH_DANG_RAW.md: đổi cột ở
// đây thì phải sửa cả tài liệu đó, vì skill xử lí sau đọc theo tài liệu.

const COT_RAW = ['phieu_so', 'thoi_gian_nop', 'email', 'student_id', 'trang_thai_phieu',
  'ma_cau', 'loai_cau', 'buoi', 'club_id', 'cau_so', 'cau_hoi', 'tra_loi',
  'dap_an_dung', 'dung_sai', 'diem', 'diem_toi_da', 'diem_forms', 'duoc_tinh', 'ghi_chu'];

function moTaCau_() {
  const M = {student_id: {loai: 'thong_tin'}, name: {loai: 'thong_tin'}};
  BUOI.forEach(function (d) {
    M['di-' + d.ma] = {loai: 'dang_ky_buoi', buoi: d.ma};
    M[d.ma] = {loai: 'xep_hang', buoi: d.ma, d: d};  // bảng lưới của biểu mẫu cũ
    d.clubs.forEach(function (_, k) {
      M[d.ma + '-top-' + (k + 1)] = {loai: 'xep_hang', buoi: d.ma, top: k + 1};
    });
    M['chon-' + d.ma] = {loai: 'chon_thi', buoi: d.ma};
    M['thi-' + d.ma] = {loai: 'cong_thi', buoi: d.ma};
    d.clubs.forEach(function (c) {
      M['thi-sau-' + c.id] = {loai: 'cong_thi', buoi: d.ma};
      M['thi-' + c.id] = {loai: 'cong_thi', buoi: d.ma, club: c.id};  // biểu mẫu bản cũ
      c.de.forEach(function (q, j) {
        M[c.id + '-' + (j + 1)] = {loai: 'de_thi', buoi: d.ma, club: c.id, so: j + 1, dung: q.dung};
      });
    });
  });
  return M;
}

function ghiRaw_(raw, META, so, r, sid, trangThai, xuLi, cacCau) {
  let luc = '', email = '';
  try { luc = Utilities.formatDate(r.getTimestamp(), 'Asia/Ho_Chi_Minh', 'yyyy-MM-dd HH:mm:ss'); } catch (e) {}
  try { email = r.getRespondentEmail() || ''; } catch (e) {}
  const dau = [so, luc, email, sid, trangThai];

  cacCau.forEach(function (c) {
    const m = META[c.ma] || {loai: 'khac'};
    const dong = function (club, cauSo, traLoi, them) {
      raw.push(dau.concat([c.ma, m.loai, m.buoi || '', club || '', cauSo || '', c.cau, traLoi])
          .concat(them || ['', '', '', '', '', '', '']));
    };
    if (m.loai === 'xep_hang') {
      // Một dòng cho mỗi Top em đã chọn: club_id là CLB, trả lời là "Top k".
      if (m.top) {
        // Câu thả xuống của một Top: một dòng nếu em chọn một CLB.
        if (maClb_(c.tl)) dong(maClb_(c.tl), '', 'Top ' + m.top);
      } else {
        docTop_(m.d, c.tl).forEach(function (x) { dong(x.id, '', 'Top ' + x.top); });
      }
    } else if (m.loai === 'chon_thi') {
      // Một dòng cho mỗi CLB đã tick.
      [].concat(c.tl || []).forEach(function (v) { dong(maClb_(v), '', v); });
    } else if (m.loai === 'cong_thi') {
      // Trang chọn CLB làm bài: club_id là CLB em chọn, trống nếu em dừng.
      dong(maClb_(c.tl) || (c.tl === CO ? m.club : ''), '', c.tl);
    } else if (m.loai === 'de_thi') {
      const dung = chuanHoa_(c.tl) === chuanHoa_(m.dung) ? 1 : 0;
      const xl = trangThai !== 'giu' ? [0, trangThai] : (xuLi[m.club] || [0, 'khong_lam_bai']);
      dong(m.club, m.so, c.tl, [m.dung, dung, dung * DIEM_CAU, DIEM_CAU, c.diemForms, xl[0], xl[1]]);
    } else {
      dong(m.club, '', Array.isArray(c.tl) ? c.tl.join(' ; ') : c.tl);
    }
  });
}

function bangDapAn_() {
  const rows = [['buoi', 'ten_buoi', 'club_id', 'ten_clb', 'ma_cau', 'cau_so', 'cau_hoi',
    'lua_chon_a', 'lua_chon_b', 'lua_chon_c', 'lua_chon_d', 'dap_an_dung', 'diem']];
  BUOI.forEach(function (d) {
    d.clubs.forEach(function (c) {
      c.de.forEach(function (q, j) {
        const lc = q.opts.slice(0, 4);
        while (lc.length < 4) lc.push('');
        rows.push([d.ma, d.ten, c.id, c.name, c.id + '-' + (j + 1), j + 1, q.q]
            .concat(lc).concat([q.dung, DIEM_CAU]));
      });
    });
  });
  return rows;
}

function ghiTrang_(sh, rows, laChu) {
  const vung = sh.getRange(1, 1, rows.length, rows[0].length);
  // Tệp nạp ghi dạng chữ để mã như 001 không bị Sheets đổi thành số 1.
  if (laChu) vung.setNumberFormat('@');
  vung.setValues(rows);
  sh.setFrozenRows(1);
  sh.getRange(1, 1, 1, rows[0].length).setFontWeight('bold');
}

function taoTepNap_(thuMuc, ten, rows) {
  const tam = SpreadsheetApp.create(ten);
  ghiTrang_(tam.getSheets()[0].setName(ten), rows, true);
  SpreadsheetApp.flush();
  xuatExcel_(tam.getId(), thuMuc, ten + '.xlsx');
  DriveApp.getFileById(tam.getId()).setTrashed(true);
}

// Sổ nhập CLB: một tệp Excel hai trang "1. CLB" và "2. Học sinh".
function taoSoNhap_(thuMuc, soClb, soHs) {
  const tam = SpreadsheetApp.create('SO_NHAP_CLB');
  ghiTrang_(tam.getSheets()[0].setName('1. CLB'), soClb, true);
  ghiTrang_(tam.insertSheet('2. Học sinh'), soHs, true);
  SpreadsheetApp.flush();
  xuatExcel_(tam.getId(), thuMuc, 'SO_NHAP_CLB.xlsx');
  DriveApp.getFileById(tam.getId()).setTrashed(true);
}

function xuatExcel_(id, thuMuc, ten) {
  const url = 'https://docs.google.com/spreadsheets/d/' + id + '/export?format=xlsx';
  const res = UrlFetchApp.fetch(url, {
    headers: {Authorization: 'Bearer ' + ScriptApp.getOAuthToken()},
    muteHttpExceptions: true
  });
  if (res.getResponseCode() !== 200) {
    throw new Error('Không xuất được ' + ten + ' (mã lỗi ' + res.getResponseCode() + '). Chạy lại chamTheoCLB.');
  }
  thuMuc.createFile(res.getBlob().setName(ten));
}
