"""Sinh tệp hướng dẫn dùng Google Forms: HUONG_DAN_GOOGLE_FORMS.docx.

    python mau_forms_thi_clb/tao_huong_dan_google.py

Viết bằng tiếng Việt đơn giản, không có gạch ngang dài. Dùng lại các hàm
định dạng của tao_word_6_phan.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx import Document  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Pt  # noqa: E402

import tao_word_6_phan as tw  # noqa: E402
from tao_word_6_phan import bang, doan, gach  # noqa: E402

RA = os.path.join(tw.THU_MUC, "HUONG_DAN_GOOGLE_FORMS.docx")


_DEM = [0]


def muc(doc, ten):
    """Tiêu đề mục. Đánh số bước lại từ 1 cho mỗi mục."""
    _DEM[0] = 0
    return doc.add_heading(ten, 1)


def buoc(doc, chu, dam=None):
    # Tự ghi số: kiểu List Number của Word đánh số nối tiếp qua các mục.
    _DEM[0] += 1
    p = doc.add_paragraph(style="List Paragraph")
    p.add_run("%d. " % _DEM[0]).bold = True
    if dam:
        p.add_run(dam).bold = True
    p.add_run(chu)
    return p


def viet():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = "Calibri", Pt(11)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    for ten in ("Title", "Heading 1", "Heading 2"):
        doc.styles[ten].font.color.rgb = tw.MAU
        doc.styles[ten].font.name = "Calibri"

    doc.add_heading("Hướng dẫn dùng Google Forms cho đăng ký CLB và thi tuyển", 0)
    doan(doc, "Tài liệu này hướng dẫn từng bước: tạo biểu mẫu, gửi cho học sinh, chấm điểm "
              "và lấy tệp Excel để nạp vào phần mềm xếp CLB.", nghieng=True)

    muc(doc, "Tổng quan")
    bang(doc, ["Việc", "Làm bằng", "Làm mấy lần"], [
        ["Tạo biểu mẫu", "Chạy hàm taoBieuMau", "Một lần"],
        ["Cài đặt thêm", "Bấm tay trong Google Forms", "Một lần"],
        ["Gửi học sinh", "Gửi đường dẫn", "Một lần"],
        ["Chấm điểm và xuất Excel", "Chạy hàm chamTheoCLB", "Mỗi khi cần kết quả mới"],
        ["Nạp vào phần mềm xếp CLB", "Nạp 3 tệp Excel", "Sau khi chấm"],
    ], dam_cot_dau=True)

    muc(doc, "A. Chuẩn bị")
    gach(doc, " Một tài khoản Google. Biểu mẫu và các tệp kết quả sẽ nằm trong Google Drive "
              "của tài khoản này.", dam="Tài khoản:")
    gach(doc, " Tệp TAO_GOOGLE_FORM.gs. Mở bằng Notepad hoặc bất kỳ trình soạn thảo chữ nào.",
         dam="Tệp mã:")

    muc(doc, "B. Tạo biểu mẫu (làm một lần)")
    buoc(doc, "Mở trình duyệt, vào script.google.com, đăng nhập tài khoản Google, bấm “Dự án "
              "mới” (New project). Cách khác: mở một biểu mẫu trống bất kỳ, bấm dấu ba chấm ở "
              "góc trên bên phải, chọn “Apps Script”. Hai cách như nhau.")
    buoc(doc, "Xoá hết chữ có sẵn trong khung soạn thảo (dòng function myFunction...).")
    buoc(doc, "Mở tệp TAO_GOOGLE_FORM.gs, chọn tất cả (Ctrl + A), sao chép (Ctrl + C), rồi dán "
              "vào khung soạn thảo (Ctrl + V).")
    buoc(doc, "Bấm biểu tượng đĩa mềm để lưu. Đặt tên dự án, ví dụ “Đăng ký CLB”.")
    buoc(doc, "Ở thanh trên cùng, chỗ chọn hàm, chọn taoBieuMau. Bấm “Chạy” (Run).")
    buoc(doc, "Google hỏi quyền truy cập. Bấm “Xem lại quyền” (Review permissions), chọn tài khoản.")
    buoc(doc, "Nếu hiện “Google chưa xác minh ứng dụng này”: bấm “Nâng cao” (Advanced), rồi "
              "“Đi tới Đăng ký CLB (không an toàn)”. Cảnh báo này hiện vì đoạn mã do chính em "
              "tạo, chưa qua Google duyệt. Mã chỉ làm việc trong Drive của em.")
    buoc(doc, "Bấm “Cho phép” (Allow). Đợi khoảng 1 tới 3 phút.")
    buoc(doc, "Khi chạy xong, phần “Nhật ký thực thi” (Execution log) ở dưới hiện hai đường dẫn: "
              "đường dẫn SỬA biểu mẫu và đường dẫn gửi HỌC SINH. Chép cả hai lại.")
    doan(doc, "Mỗi lần chạy taoBieuMau là tạo một biểu mẫu mới. Chỉ chạy một lần, trừ khi "
              "muốn làm lại từ đầu.", dam="Lưu ý: ")

    muc(doc, "C. Cài đặt thêm bằng tay (làm một lần)")
    doan(doc, "Mở đường dẫn SỬA biểu mẫu, bấm tab “Cài đặt” (Settings).")
    buoc(doc, " Mục “Công bố điểm” (Release grades) chọn “Sau khi xem xét thủ công” (Later, after "
              "manual review). Bỏ tick “Câu hỏi bị trả lời sai” và “Câu trả lời đúng”. Như vậy "
              "học sinh nộp xong không thấy đáp án để báo cho bạn làm sau.",
         dam="Bài kiểm tra (Quizzes).")
    buoc(doc, " Bật “Giới hạn 1 câu trả lời” (Limit to 1 response). Học sinh phải đăng nhập tài "
              "khoản Google và chỉ nộp được một lần.", dam="Câu trả lời (Responses).")
    buoc(doc, " Nếu nút “Xuất bản” ở góc trên còn màu tím, bấm vào để xuất bản. Chưa xuất bản "
              "thì học sinh không mở được biểu mẫu.", dam="Xuất bản.")
    buoc(doc, " Bấm biểu tượng con mắt (Xem trước) và làm thử: chọn Không ở một buổi; ở buổi "
              "khác chọn vài CLB ở Top 1, Top 2 (Top còn lại để “(Bỏ trống)”), tick 2 CLB, chọn làm CLB thứ nhất, rồi CLB thứ hai, "
              "rồi “Em không thi thêm CLB nào buổi này”. Kiểm tra chỉ đề của 2 CLB đó hiện ra.",
         dam="Làm thử.")

    muc(doc, "D. Gửi cho học sinh")
    gach(doc, "Gửi đường dẫn HỌC SINH qua nhóm lớp, email hoặc mã QR.")
    gach(doc, "Nhắc học sinh: buổi nào bận thì chọn “Không, em bận buổi này”. Bấm vào Top 1 và "
              "chọn CLB thích nhất trong danh sách, rồi Top 2...; Top không dùng thì để “(Bỏ trống)”; mỗi CLB chỉ chọn một lần. "
              "Tick trước các CLB muốn thi, tối đa 5. Sau đó chọn lần lượt CLB để làm bài, theo "
              "thứ tự trong danh sách; chỉ đề của CLB được chọn mới hiện ra. Chỉ bài của CLB đã "
              "tick và đã chọn ở một Top mới được tính điểm.")
    gach(doc, "Hết hạn nộp: trong tab “Câu trả lời”, tắt “Chấp nhận câu trả lời”.")

    muc(doc, "E. Chấm điểm và xuất Excel")
    buoc(doc, "Mở lại dự án trên script.google.com (dự án ở mục B).")
    buoc(doc, "Chọn hàm chamTheoCLB, bấm “Chạy”. Lần đầu Google hỏi thêm quyền dùng Drive và "
              "Sheets: bấm cho phép như ở mục B.")
    buoc(doc, "Đợi chạy xong. Nhật ký thực thi hiện đường dẫn “Thư mục kết quả”.")
    buoc(doc, "Mở đường dẫn đó. Trong thư mục có các tệp sau:")
    bang(doc, ["Tệp", "Dùng để"], [
        ["BANG_DIEM.xlsx", "Xem kết quả. Có 2 trang: Bảng điểm (điểm từng CLB, thang 10) và "
                           "Cảnh báo."],
        ["SO_NHAP_CLB.xlsx", "Sổ nhập CLB: tệp DUY NHẤT nạp vào phần mềm. Trang “1. CLB” phải "
                             "điền cột Chỉ tiêu trước. Trang “2. Học sinh”: nguyện vọng và điểm."],
        ["RAW_PHIEU.xlsx", "Dữ liệu raw: mọi câu trả lời của mọi phiếu, mỗi câu một dòng. Câu đề "
                           "thi đã chấm sẵn: đúng hay sai, điểm, có được tính không. Dùng để soát "
                           "lại hoặc xử lí tiếp. Định dạng xem tệp DINH_DANG_RAW.md."],
        ["DAP_AN.xlsx", "Đáp án của 100 câu đề thi, kèm 4 lựa chọn và điểm mỗi câu."],
        ["BANG_DIEM <ngày giờ>", "Bản Google Sheets của bảng điểm, để xem trên mạng."],
    ], dam_cot_dau=True)
    buoc(doc, "Tải về máy: bấm chuột phải vào tên thư mục, chọn “Tải xuống” (Download). Google "
              "nén cả thư mục thành một tệp .zip. Giải nén ra là có các tệp Excel.")
    doan(doc, "Có thêm phiếu nộp muộn thì chạy lại chamTheoCLB. Mỗi lần chạy tạo một thư mục "
              "mới, thư mục cũ vẫn giữ nguyên.", dam="Chạy lại: ")

    muc(doc, "F. Nạp vào phần mềm xếp CLB")
    buoc(doc, "Mở SO_NHAP_CLB.xlsx bằng Excel, trang “1. CLB”. Điền cột Chỉ tiêu: số học sinh "
              "tối đa của từng CLB (lớn hơn 0). Nếu có suất dành cho nhóm ưu tiên thì điền Suất "
              "ưu tiên và Nhóm ưu tiên. Lưu lại.")
    buoc(doc, "Trong phần mềm, thẻ “01 · Vận hành sắp xếp”: kéo sổ vào ô nạp, xem dòng tóm tắt, "
              "bấm “Nhập sổ”.")
    buoc(doc, "Sau khi nạp, đọc hết phần cảnh báo của phần mềm. Nạp được không có nghĩa là "
              "không có gì sai.")
    buoc(doc, "Đối chiếu với trang “Cảnh báo” trong BANG_DIEM.xlsx. Hai cảnh báo hay gặp: em làm "
              "bài một CLB mà không tick hoặc không chọn ở Top nào (bài không được tính), và em "
              "tick một CLB mà không làm bài.")

    muc(doc, "G. Lỗi thường gặp")
    bang(doc, ["Hiện tượng", "Cách xử lý"], [
        ["“Chưa biết chấm biểu mẫu nào”",
         "Biểu mẫu được tạo từ dự án khác hoặc bản mã cũ. Mở biểu mẫu, chép đường dẫn trên thanh "
         "địa chỉ (có /edit ở cuối), dán vào dòng const LINK_BIEU_MAU = '...' ở đầu tệp mã, lưu, "
         "chạy lại chamTheoCLB."],
        ["“Không xuất được ... (mã lỗi ...)”",
         "Mạng hoặc Google đang bận. Chạy lại chamTheoCLB."],
        ["Chạy taoBieuMau hai lần, có hai biểu mẫu",
         "Xoá biểu mẫu thừa trong Google Drive. Chỉ gửi học sinh đường dẫn của một biểu mẫu."],
        ["Học sinh báo không mở được",
         "Kiểm tra học sinh đã đăng nhập tài khoản Google, và biểu mẫu còn đang nhận câu trả lời."],
        ["Phần mềm báo thiếu chỉ tiêu CLB",
         "Chưa điền cột Chỉ tiêu ở trang “1. CLB” của SO_NHAP_CLB.xlsx."],
    ], dam_cot_dau=True)

    muc(doc, "H. Muốn đổi đề thi hoặc danh sách CLB")
    doan(doc, "Danh sách CLB và đề thi nằm trong tệp THIET_KE_6_PHAN.html. Sửa ở đó, rồi chạy "
              "python mau_forms_thi_clb/tao_google_forms.py để sinh lại TAO_GOOGLE_FORM.gs. Sau đó "
              "làm lại mục B để tạo biểu mẫu mới. Không sửa tay danh sách trong tệp .gs.")

    for z in doc.settings.element.findall(qn("w:zoom")):
        z.set(qn("w:percent"), "100")
    return doc


def main():
    doc = viet()
    tw.kiem_chu(doc)
    doc.save(RA)
    print("Đã ghi %s" % RA)


if __name__ == "__main__":
    sys.exit(main())
