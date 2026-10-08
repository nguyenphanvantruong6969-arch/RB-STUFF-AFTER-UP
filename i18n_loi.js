/* ==========================================================================
   i18n_loi.js — TỆP SINH TỰ ĐỘNG, KHÔNG SỬA TAY.
   ==========================================================================
   Nguồn: MESSAGES trong i18n_errors.py. Sửa ở đó rồi chạy:
       python tao_i18n_js.py
   tests/test_i18n_sync.py đỏ ngay nếu tệp này lệch khỏi nguồn.
   ========================================================================== */
window.I18N_ERROR_MESSAGES = {
  "error_reading_last_run": {
    "vi": "Không đọc được thông tin lần sắp xếp gần nhất. Hãy thử lại.",
    "en": "Couldn't load the latest allocation. Try again."
  },
  "error_reading_dashboard": {
    "vi": "Không tải được trang tổng quan. Hãy thử lại.",
    "en": "Couldn't load the overview. Try again."
  },
  "error_checking_integrity": {
    "vi": "Không kiểm tra được dữ liệu. Hãy thử lại.",
    "en": "Couldn't check the data. Try again."
  },
  "error_checking_run_warning": {
    "vi": "Không kiểm tra được dữ liệu trước khi sắp xếp. Hãy thử lại.",
    "en": "Couldn't check the data before allocating. Try again."
  },
  "error_reading_stb_lock": {
    "vi": "Không kiểm tra được số bốc thăm. Hãy thử lại.",
    "en": "Couldn't check the lottery numbers. Try again."
  },
  "error_reading_run_history": {
    "vi": "Không mở được nhật ký các lần sắp xếp. Hãy thử lại.",
    "en": "Couldn't open the allocation history. Try again."
  },
  "error_running_pipeline": {
    "vi": "Sắp xếp bị dừng giữa chừng do một lỗi ngoài dự kiến. Dữ liệu chưa bị thay đổi. Hãy thử lại.",
    "en": "The allocation stopped because of an unexpected problem. No data was changed. Try again."
  },
  "xem_nhat_ky": {
    "vi": "Chi tiết kỹ thuật đã được ghi vào tệp {file}, nằm cùng thư mục với tệp dữ liệu. Nếu lỗi còn lặp lại, gửi tệp đó cho người phụ trách kỹ thuật.",
    "en": "Technical details were saved to {file}, in the same folder as the data file. If the error keeps happening, send that file to the technical contact."
  },
  "loi_ngoai_du_kien": {
    "vi": "Có lỗi ngoài dự kiến khi thực hiện thao tác ({ten}). Hãy thử lại.",
    "en": "Something unexpected went wrong during an operation ({ten}). Try again."
  },
  "error_reading_csv_preview": {
    "vi": "Không xem trước được tệp này. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't preview this file. Check the file and try again."
  },
  "error_importing_preferences_csv": {
    "vi": "Không nạp được tệp nguyện vọng. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the preferences file. Check the file and try again."
  },
  "error_importing_test_selection_csv": {
    "vi": "Không nạp được tệp chọn CLB dự thi. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the test club file. Check the file and try again."
  },
  "error_reading_scoring_overview": {
    "vi": "Không tải được tình hình chấm điểm. Hãy thử lại.",
    "en": "Couldn't load the scoring overview. Try again."
  },
  "error_reading_scoring_list": {
    "vi": "Không tải được danh sách chấm điểm. Hãy thử lại.",
    "en": "Couldn't load the scoring list. Try again."
  },
  "error_saving_scores": {
    "vi": "Không lưu được điểm. Hãy thử lại.",
    "en": "Couldn't save the scores. Try again."
  },
  "error_reading_club_roster": {
    "vi": "Không tải được danh sách thành viên của câu lạc bộ. Hãy thử lại.",
    "en": "Couldn't load the club's member list. Try again."
  },
  "error_reading_pref_distribution": {
    "vi": "Không tải được thống kê nguyện vọng. Hãy thử lại.",
    "en": "Couldn't load the preference summary. Try again."
  },
  "error_reading_unplaced": {
    "vi": "Không tải được danh sách học sinh chưa có chỗ. Hãy thử lại.",
    "en": "Couldn't load the list of unplaced students. Try again."
  },
  "error_reading_reserve_usage": {
    "vi": "Không tải được thống kê suất dự trữ. Hãy thử lại.",
    "en": "Couldn't load the reserve seat summary. Try again."
  },
  "error_reading_results": {
    "vi": "Không tải được kết quả. Hãy thử lại.",
    "en": "Couldn't load the results. Try again."
  },
  "error_detecting_csv_kind": {
    "vi": "Không nhận ra được đây là tệp gì. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't tell what kind of file this is. Check the file and try again."
  },
  "error_importing_csv_auto": {
    "vi": "Không nạp được tệp này. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import this file. Check the file and try again."
  },
  "error_importing_clubs_csv": {
    "vi": "Không nạp được tệp danh sách CLB. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the club list file. Check the file and try again."
  },
  "csv_kind_ambiguous": {
    "vi": "Chưa rõ đây là tệp chọn CLB dự thi hay tệp xếp hạng nguyện vọng (các cột: {fieldnames}). Hãy chọn loại tệp, hoặc thêm cột rank nếu đây là tệp nguyện vọng.",
    "en": "Couldn't tell whether this is a test club file or a preferences file (columns: {fieldnames}). Choose the file type, or add a rank column if it holds preferences."
  },
  "csv_kind_unknown": {
    "vi": "Không nhận ra định dạng của tệp này. Xem các cột được hỗ trợ trong mau_csv/HUONG_DAN_CSV.md.",
    "en": "This file format isn't recognised. See the supported columns in mau_csv/HUONG_DAN_CSV.md."
  },
  "csv_club_row_invalid": {
    "vi": "Dòng {line} bị bỏ qua vì {reason} không hợp lệ. Tổng chỗ phải lớn hơn 0 và suất dự trữ không được nhiều hơn tổng chỗ.",
    "en": "Line {line} was skipped because {reason} isn't valid. Total seats must be above 0, and reserve seats can't be more than total seats."
  },
  "xlsx_read_failed": {
    "vi": "Không mở được tệp Excel này. Kiểm tra tệp có đúng định dạng .xlsx không, hoặc lưu lại tệp rồi thử lần nữa.",
    "en": "Couldn't open this Excel file. Check that it's an .xlsx file, or save it again and retry."
  },
  "file_too_large": {
    "vi": "Tệp quá lớn ({size_mb} MB, tối đa {max_mb} MB). Tệp danh sách của một trường không lớn cỡ này. Hãy kiểm tra xem có chọn nhầm tệp không.",
    "en": "The file is too large ({size_mb} MB, maximum {max_mb} MB). A school's list is never this big. Check that the right file was chosen."
  },
  "xlsx_empty": {
    "vi": "Tệp Excel này không có dữ liệu.",
    "en": "This Excel file has no data."
  },
  "xlsx_support_missing": {
    "vi": "Bản cài này không mở được tệp Excel. Hãy lưu tệp ở dạng CSV UTF-8 rồi nạp lại.",
    "en": "This version can't open Excel files. Save the file as CSV UTF-8 and import it again."
  },
  "csv_reserve_group_unknown": {
    "vi": "Nhãn dự trữ {reserve_group} không khớp với câu lạc bộ nào, nên {n} học sinh mang nhãn này sẽ không được xét suất dự trữ. Có thể nhãn đúng là {goi_y}.",
    "en": "The reserve label {reserve_group} doesn't match any club, so {n} student(s) with this label won't be considered for reserve seats. The intended label may be {goi_y}."
  },
  "csv_duplicate_student_rows": {
    "vi": "Mã {student_id} có ở {n} dòng trong tệp. Chỉ dòng cuối cùng được giữ.",
    "en": "Student {student_id} appears on {n} rows. Only the last row was kept."
  },
  "csv_score_not_a_number": {
    "vi": "Điểm “{score}” của học sinh {student_id} ở CLB {club_id} không phải là số nên chưa được lưu. Các lựa chọn dự thi vẫn được giữ. Sửa điểm rồi nạp lại tệp.",
    "en": "The score “{score}” for student {student_id} in club {club_id} isn't a number, so it wasn't saved. The test club choices were kept. Fix the score and import the file again."
  },
  "csv_score_negative": {
    "vi": "Điểm “{score}” của học sinh {student_id} ở CLB {club_id} là số âm, có thể do gõ thừa dấu trừ. Điểm này chưa được lưu.",
    "en": "The score “{score}” for student {student_id} in club {club_id} is negative, probably an extra minus sign. This score wasn't saved."
  },
  "csv_score_for_unselected_club": {
    "vi": "Học sinh {student_id} có điểm ở CLB {club_id} nhưng không đăng ký dự thi CLB này, nên điểm chưa được lưu. Kiểm tra xem mã CLB có bị gõ nhầm không.",
    "en": "Student {student_id} has a score for club {club_id} but didn't sign up to test for it, so the score wasn't saved. Check the club code for typos."
  },
  "thu_muc_khong_hop_le": {
    "vi": "Không mở được thư mục \"{path}\". Chỉ mở được thư mục chứa tệp phần mềm vừa xuất.",
    "en": "Cannot open the folder \"{path}\". Only folders holding files this app exported can be opened."
  },
  "thu_muc_khong_mo_duoc": {
    "vi": "Máy không mở được thư mục. Hãy mở thủ công theo đường dẫn hiện trên màn hình.",
    "en": "The computer could not open the folder. Open it by hand using the path shown on screen."
  },
  "chua_chon_hoc_sinh": {
    "vi": "Chưa chọn học sinh nào để xuất. Hãy đánh dấu ít nhất một học sinh.",
    "en": "No students selected to export. Tick at least one student."
  },
  "chua_co_lan_chay_truoc": {
    "vi": "Chưa có lần chạy trước để so sánh. Cần chạy sắp xếp ít nhất hai lần.",
    "en": "There is no previous run to compare with. Run the allocation at least twice."
  },
  "csv_score_removed_unselected": {
    "vi": "Học sinh {student_id}: tệp mới không còn {n} CLB đã có điểm chấm. Học sinh được coi như rút khỏi bài thi đó, nên {n} điểm cũ đã bị xoá theo.",
    "en": "Student {student_id}: the new file no longer lists {n} club(s) that already had a score. The student is treated as withdrawn from that test, so the {n} old score(s) were deleted."
  },
  "csv_score_without_club": {
    "vi": "Học sinh {student_id} có điểm ở ô điểm số {cot} nhưng ô mã CLB bên cạnh để trống, có thể do lệch cột. Điểm này chưa được lưu.",
    "en": "Student {student_id} has a score in score column {cot} but the club column next to it is empty, probably a shifted column. This score wasn't saved."
  },
  "csv_scores_ignored_here": {
    "vi": "Tệp xếp hạng nguyện vọng không dùng để nạp điểm, nên các cột điểm trong tệp này được bỏ qua. Hãy đưa điểm vào tệp chọn CLB dự thi.",
    "en": "Scores can't be imported from a preferences file, so the score columns here were ignored. Put the scores in the test club file instead."
  },
  "csv_student_id_case_conflict": {
    "vi": "Mã {student_id} và mã {da_co} chỉ khác nhau ở chữ hoa, chữ thường nên đang được tính là hai học sinh. Nếu là cùng một học sinh, hãy viết mã giống nhau ở cả hai tệp.",
    "en": "The codes {student_id} and {da_co} differ only in upper and lower case, so they count as two students. If both codes belong to one student, write the code the same way in both files."
  },
  "csv_student_id_maybe_truncated": {
    "vi": "Mã {student_id} có {do_dai} chữ số, trong khi phần lớn mã khác có {do_dai_pho_bien}. Có thể Excel đã bỏ số 0 ở đầu. Mở tệp gốc, đặt cột mã ở dạng Text rồi nạp lại.",
    "en": "The code {student_id} has {do_dai} digits while most codes have {do_dai_pho_bien}. Excel may have removed a leading zero. Open the original file, set the code column to Text, and import again."
  },
  "error_reading_club_stats": {
    "vi": "Không tải được thống kê câu lạc bộ. Hãy thử lại.",
    "en": "Couldn't load the club summary. Try again."
  },
  "error_exporting_csv": {
    "vi": "Không xuất được tệp kết quả. Kiểm tra thư mục lưu còn chỗ trống và tệp cũ không đang mở, rồi thử lại.",
    "en": "Couldn't export the results. Check that the folder has free space and the old file isn't open, then try again."
  },
  "error_exporting_excel": {
    "vi": "Không ghi được tệp Excel kết quả. Đóng tệp cũ nếu đang mở trong Excel, kiểm tra thư mục lưu còn chỗ trống, rồi thử lại.",
    "en": "Couldn't write the results Excel file. Close the old file if it's open in Excel, check that the folder has free space, then try again."
  },
  "error_saving_club": {
    "vi": "Không lưu được câu lạc bộ. Hãy thử lại.",
    "en": "Couldn't save the club. Try again."
  },
  "error_deleting_club": {
    "vi": "Không xoá được câu lạc bộ. Hãy thử lại.",
    "en": "Couldn't delete the club. Try again."
  },
  "error_reading_reserve_groups": {
    "vi": "Không tải được danh sách nhãn dự trữ. Hãy thử lại.",
    "en": "Couldn't load the reserve labels. Try again."
  },
  "error_assigning_reserve_group": {
    "vi": "Không gán được nhãn dự trữ. Hãy thử lại.",
    "en": "Couldn't assign the reserve label. Try again."
  },
  "error_bulk_assigning": {
    "vi": "Không gán được nhãn cho các học sinh đã chọn. Hãy thử lại.",
    "en": "Couldn't assign the label to the selected students. Try again."
  },
  "error_reading_student_list": {
    "vi": "Không tải được danh sách học sinh. Hãy thử lại.",
    "en": "Couldn't load the student list. Try again."
  },
  "error_reading_club_list": {
    "vi": "Không tải được danh sách câu lạc bộ. Hãy thử lại.",
    "en": "Couldn't load the club list. Try again."
  },
  "error_searching_students": {
    "vi": "Không tìm được học sinh lúc này. Hãy thử lại.",
    "en": "Couldn't search for students right now. Try again."
  },
  "error_reading_student_state": {
    "vi": "Không tải được thông tin của học sinh này. Hãy thử lại.",
    "en": "Couldn't load this student's details. Try again."
  },
  "error_saving_test_selection": {
    "vi": "Không lưu được lựa chọn CLB dự thi. Hãy thử lại.",
    "en": "Couldn't save the test club choices. Try again."
  },
  "error_saving_preferences": {
    "vi": "Không lưu được nguyện vọng. Hãy thử lại.",
    "en": "Couldn't save the preferences. Try again."
  },
  "error_creating_student": {
    "vi": "Không tạo được học sinh mới. Hãy thử lại.",
    "en": "Couldn't add the new student. Try again."
  },
  "error_resetting_student_entry": {
    "vi": "Không xoá được lựa chọn của học sinh này. Hãy thử lại.",
    "en": "Couldn't clear this student's choices. Try again."
  },
  "error_deleting_student": {
    "vi": "Không xoá được học sinh. Hãy thử lại.",
    "en": "Couldn't delete the student. Try again."
  },
  "reset_confirmation_mismatch": {
    "vi": "Chưa xoá dữ liệu nào vì thiếu bước xác nhận. Hãy bấm nút xoá thêm một lần để xác nhận.",
    "en": "Nothing was deleted because the confirmation step was missing. Click the delete button once more to confirm."
  },
  "reset_scope_unknown": {
    "vi": "Chưa xoá dữ liệu nào vì yêu cầu xoá không hợp lệ. Hãy dùng các nút xoá trong ứng dụng.",
    "en": "Nothing was deleted because the request wasn't valid. Use the delete buttons in the app."
  },
  "error_resetting_data": {
    "vi": "Không xoá được dữ liệu. Nếu bản sao lưu đã được tạo, bản đó vẫn nằm trong thư mục dữ liệu.",
    "en": "Couldn't delete the data. If a backup was made, it's still in the data folder."
  },
  "csv_empty": {
    "vi": "Tệp này trống hoặc không có dòng nào đọc được.",
    "en": "This file is empty, or none of its rows could be read."
  },
  "csv_missing_columns": {
    "vi": "Tệp dạng dọc cần có cột mã học sinh và cột mã CLB (tên cột \"student_id\" và \"club_id\"). Các cột đang có: {fieldnames}",
    "en": "A long-format file needs a student code column and a club code column (named \"student_id\" and \"club_id\"). Columns found: {fieldnames}"
  },
  "capacity_must_be_positive": {
    "vi": "Tổng chỗ phải lớn hơn 0.",
    "en": "Total seats must be more than 0."
  },
  "no_data_to_run": {
    "vi": "Chưa có dữ liệu để sắp xếp. Cần ít nhất một câu lạc bộ và một học sinh.",
    "en": "There's no data to allocate yet. Add at least one club and one student."
  },
  "clb_thieu_buoi": {
    "vi": "Có {n} câu lạc bộ chưa có buổi sinh hoạt: {club_ids}. Các câu lạc bộ này sẽ bị tính chung một buổi, nên mỗi học sinh chỉ vào được một trong số đó. Hãy điền buổi cho tất cả câu lạc bộ, hoặc để trống cột buổi ở tất cả.",
    "en": "{n} club(s) have no session: {club_ids}. These clubs will be treated as one session, so a student can join only one of them. Fill in a session for every club, or leave the session column empty for all of them."
  },
  "buoi_khong_ton_tai": {
    "vi": "Không có buổi sinh hoạt nào tên “{buoi}”. Các buổi hiện có: {dang_co}.",
    "en": "There's no session called “{buoi}”. Current sessions: {dang_co}."
  },
  "chua_chon_buoi_nao": {
    "vi": "Chưa chọn buổi nào để sắp xếp. Hãy chọn ít nhất một buổi.",
    "en": "No session is selected. Choose at least one session."
  },
  "khong_ve_lai_tham_khi_chay_mot_phan": {
    "vi": "Không thể bốc thăm lại khi chỉ sắp xếp một số buổi, vì bốc thăm lại sẽ đổi thứ tự của cả những buổi đang giữ kết quả cũ. Muốn bốc thăm lại, hãy chọn tất cả các buổi.",
    "en": "The lottery can't be redrawn when only some sessions are allocated, because a redraw also changes the order of the sessions that keep their results. To redraw, select every session."
  },
  "khong_chen_tham_khi_chay_mot_phan": {
    "vi": "Có {n} học sinh chưa có số bốc thăm. Cấp số mới sẽ đổi thứ tự của mọi buổi, kể cả những buổi đang giữ kết quả cũ. Hãy chọn tất cả các buổi rồi sắp xếp một lần cho cả tuần.",
    "en": "{n} student(s) don't have a lottery number yet. Adding them changes the order of every session, including those keeping their results. Select every session and allocate the whole week at once."
  },
  "khong_doi_hat_giong_khi_chay_mot_phan": {
    "vi": "Lần sắp xếp trước dùng số khởi tạo bốc thăm {cu}, lần này là {moi}. Đổi số này sẽ đổi thứ tự của mọi buổi, kể cả những buổi đang giữ kết quả cũ. Hãy đặt lại số {cu}, hoặc chọn tất cả các buổi và sắp xếp một lần cho cả tuần.",
    "en": "The last allocation used lottery starting number {cu}; this one uses {moi}. Changing it changes the order of every session, including those keeping their results. Set it back to {cu}, or select every session and allocate the whole week at once."
  },
  "hat_giong_da_khoa": {
    "vi": "Số khởi tạo bốc thăm đã khoá ở {cu} cùng bộ số bốc thăm, nhưng lần này lại là {moi}. Đổi số khởi tạo là đổi thứ tự ưu tiên của từng buổi, tức là đổi kết quả đã công bố, giống như bốc thăm lại. Hãy đặt lại số khởi tạo là {cu}. Muốn dùng số mới thì bấm \"Bốc thăm lại…\" rồi chạy lại.",
    "en": "The lottery starting number is locked at {cu} together with the lottery numbers, but this run uses {moi}. Changing it changes each session's priority order and so the published results, just like redrawing the lottery. Set it back to {cu}. To use a new number, click \"Redraw lottery…\" and run again."
  },
  "nguyen_vong_lech_buoi": {
    "vi": "Dòng {line}: học sinh {student_id} xếp CLB {club_id} vào cột buổi {buoi_cot}, nhưng CLB này sinh hoạt buổi {buoi_that}. Nguyện vọng này được bỏ qua.",
    "en": "Row {line}: student {student_id} put club {club_id} under {buoi_cot}, but the club meets on {buoi_that}. This preference was skipped."
  },
  "reserve_capacity_negative": {
    "vi": "Suất dự trữ không được là số âm",
    "en": "Reserve capacity cannot be negative"
  },
  "reserve_capacity_exceeds_capacity": {
    "vi": "Suất dự trữ không được nhiều hơn tổng chỗ.",
    "en": "Reserve seats can't be more than total seats."
  },
  "club_id_required": {
    "vi": "Hãy nhập mã CLB.",
    "en": "Enter a club code."
  },
  "cannot_delete_club_referenced": {
    "vi": "Không xoá được CLB {club_id} vì CLB này đang có trong {n_prefs} nguyện vọng và {n_matches} kết quả. Hãy xử lý các dữ liệu đó trước.",
    "en": "Club {club_id} can't be deleted because it's still in {n_prefs} preference(s) and {n_matches} result(s). Deal with that data first."
  },
  "student_not_found": {
    "vi": "Không tìm thấy học sinh {student_id}.",
    "en": "Student {student_id} wasn't found."
  },
  "club_not_found": {
    "vi": "Không tìm thấy CLB {club_id}.",
    "en": "Club {club_id} wasn't found."
  },
  "unknown_clubs": {
    "vi": "Không tìm thấy các CLB: {club_ids}.",
    "en": "These clubs weren't found: {club_ids}."
  },
  "scores_must_be_nonempty_list": {
    "vi": "Chưa có điểm nào để lưu.",
    "en": "There are no scores to save."
  },
  "student_ids_must_be_nonempty_list": {
    "vi": "Chưa chọn học sinh nào.",
    "en": "No students are selected."
  },
  "club_ids_must_be_list": {
    "vi": "Danh sách CLB không hợp lệ. Hãy thử lại.",
    "en": "The club list isn't valid. Try again."
  },
  "ordered_club_ids_must_be_list": {
    "vi": "Danh sách nguyện vọng không hợp lệ. Hãy thử lại.",
    "en": "The preference list isn't valid. Try again."
  },
  "must_rank_at_least_one": {
    "vi": "Hãy chọn ít nhất một nguyện vọng.",
    "en": "Choose at least one preference."
  },
  "max_pref_moi_buoi": {
    "vi": "Buổi {buoi} đã đủ {tran} nguyện vọng. Muốn thêm, hãy bỏ bớt một CLB của buổi này.",
    "en": "{buoi} already has {tran} preferences, the most allowed. To add another, remove one from this session."
  },
  "max_thi_moi_buoi": {
    "vi": "Buổi {buoi} đã đủ {tran} CLB dự thi. Muốn thêm, hãy bỏ bớt một CLB của buổi này.",
    "en": "{buoi} already has {tran} test clubs, the most allowed. To add another, remove one from this session."
  },
  "duplicate_preference_in_list": {
    "vi": "CLB này đã có trong danh sách nguyện vọng.",
    "en": "This club is already in the preference list."
  },
  "cannot_delete_student_matched": {
    "vi": "Không xoá được học sinh {student_id} vì học sinh này có trong kết quả sắp xếp gần nhất. Hãy xử lý xong rồi sắp xếp lại.",
    "en": "Student {student_id} can't be deleted because the student is in the latest results. Sort that out, then run the allocation again."
  },
  "stb_redrawn_and_locked": {
    "vi": "Đã bốc thăm cho {n} học sinh và khoá kết quả bốc thăm.",
    "en": "Drew lottery numbers for {n} student(s) and locked them."
  },
  "stb_supplemented": {
    "vi": "Số bốc thăm đã khoá. Thứ tự cũ được giữ nguyên, {n} học sinh mới được xếp ngẫu nhiên vào.",
    "en": "Lottery numbers were already locked. The existing order was kept and {n} new student(s) were added at random."
  },
  "stb_reused": {
    "vi": "Số bốc thăm đã khoá nên được dùng lại, không bốc thăm mới.",
    "en": "Lottery numbers were already locked, so they were reused."
  },
  "rbda_done": {
    "vi": "Hoàn tất sau {rounds} vòng, không có lỗi.",
    "en": "Finished in {rounds} round(s) with no errors."
  },
  "db_backed_up": {
    "vi": "Đã sao lưu dữ liệu trước khi sắp xếp: {backup_name}",
    "en": "Backed up the data before allocating: {backup_name}"
  },
  "db_backup_failed": {
    "vi": "Không sao lưu được dữ liệu. Việc sắp xếp vẫn tiếp tục.",
    "en": "Couldn't back up the data. The allocation continued anyway."
  },
  "pipeline_rolled_back": {
    "vi": "Sắp xếp bị dừng giữa chừng nên mọi thay đổi của lần này đã được huỷ, kể cả số bốc thăm mới. Dữ liệu giữ nguyên như trước khi bấm chạy.",
    "en": "The allocation stopped partway, so every change from this run was undone, including new lottery numbers. The data is the same as before the run."
  },
  "pref_student_not_in_students": {
    "vi": "Mã {student_id} có nguyện vọng nhưng không có trong danh sách học sinh.",
    "en": "Code {student_id} has preferences but isn't in the student list."
  },
  "pref_duplicate_club": {
    "vi": "Học sinh {student_id} có một CLB bị lặp trong danh sách nguyện vọng.",
    "en": "Student {student_id} has the same club twice in the preference list."
  },
  "pref_too_many": {
    "vi": "Học sinh {student_id} có {count} nguyện vọng, nhiều hơn mức tối đa 10.",
    "en": "Student {student_id} has {count} preferences. The most allowed is 10."
  },
  "pref_too_many_buoi": {
    "vi": "Học sinh {student_id} có {count} nguyện vọng ở buổi {buoi}, nhiều hơn mức tối đa 10 mỗi buổi.",
    "en": "Student {student_id} has {count} preferences in {buoi}. The most allowed is 10 per session."
  },
  "thi_too_many": {
    "vi": "Học sinh {student_id} đăng ký dự thi {count} CLB, nhiều hơn mức tối đa 5.",
    "en": "Student {student_id} signed up to test for {count} clubs. The most allowed is 5."
  },
  "thi_too_many_buoi": {
    "vi": "Học sinh {student_id} đăng ký dự thi {count} CLB ở buổi {buoi}, nhiều hơn mức tối đa 5 mỗi buổi.",
    "en": "Student {student_id} signed up to test for {count} clubs in {buoi}. The most allowed is 5 per session."
  },
  "pref_unknown_club": {
    "vi": "Học sinh {student_id} có nguyện vọng vào CLB {club_id}, nhưng không tìm thấy CLB này.",
    "en": "Student {student_id} chose club {club_id}, but that club wasn't found."
  },
  "club_capacity_not_positive": {
    "vi": "CLB {club_id} có tổng chỗ bằng 0. Tổng chỗ phải lớn hơn 0.",
    "en": "Club {club_id} has 0 seats. Total seats must be more than 0."
  },
  "club_reserve_negative": {
    "vi": "CLB {club_id} có số suất dự trữ âm. Số này phải từ 0 trở lên.",
    "en": "Club {club_id} has a negative number of reserved seats. It must be 0 or more."
  },
  "club_reserve_exceeds_capacity": {
    "vi": "CLB {club_id} có suất dự trữ nhiều hơn tổng chỗ.",
    "en": "Club {club_id} has more reserve seats than total seats."
  },
  "applicants_unknown_club": {
    "vi": "Danh sách dự thi có CLB {club_id}, nhưng không tìm thấy CLB này.",
    "en": "The test list includes club {club_id}, but that club wasn't found."
  },
  "applicants_unknown_student": {
    "vi": "Danh sách dự thi có mã {student_id}, nhưng không tìm thấy học sinh này.",
    "en": "The test list includes student {student_id}, but that student wasn't found."
  },
  "assignment_not_in_preferences": {
    "vi": "Học sinh {student_id} được xếp vào CLB {club_id} dù CLB này không có trong nguyện vọng.",
    "en": "Student {student_id} was placed in club {club_id}, which isn't among the student's preferences."
  },
  "club_over_capacity": {
    "vi": "CLB {club_id} có {count} học sinh nhưng chỉ có {capacity} chỗ.",
    "en": "Club {club_id} has {count} student(s) but only {capacity} seat(s)."
  },
  "club_over_reserve_capacity": {
    "vi": "CLB {club_id} có {count} học sinh dùng suất dự trữ nhưng chỉ có {reserve_capacity} suất.",
    "en": "Club {club_id} has {count} student(s) in reserve seats but only {reserve_capacity} reserve seat(s)."
  },
  "blocking_pair": {
    "vi": "Có thể chưa công bằng: học sinh {student_id} thích CLB {club_id} hơn CLB đang được xếp ({current_club}) và đủ điều kiện vào {club_id}. CLB {club_id} hiện đã nhận {n_holders}/{capacity} chỗ.",
    "en": "Possible unfair result: student {student_id} prefers club {club_id} to the assigned club ({current_club}) and qualifies for {club_id}. Club {club_id} has filled {n_holders}/{capacity} seats."
  },
  "csv_pref_duplicate_deduped": {
    "vi": "{student_id}: có CLB bị lặp trong nguyện vọng, phần lặp đã được bỏ.",
    "en": "{student_id}: a club was listed twice in the preferences. The repeat was removed."
  },
  "csv_thi_bo_buoi_qua_tran": {
    "vi": "{student_id}: buổi {buoi} có {count} CLB dự thi, nhiều hơn mức tối đa {tran}. Buổi này chưa được nạp, kể cả điểm. Các buổi khác vẫn được nạp.",
    "en": "{student_id}: {buoi} has {count} test clubs, more than the limit of {tran}. This session wasn't imported, scores included. The other sessions were."
  },
  "csv_pref_bo_buoi_qua_tran": {
    "vi": "{student_id}: buổi {buoi} có {count} nguyện vọng, nhiều hơn mức tối đa {tran}. Buổi này chưa được nạp. Các buổi khác vẫn được nạp. Sửa buổi này rồi nạp lại nếu cần.",
    "en": "{student_id}: {buoi} has {count} preferences, more than the limit of {tran}. This session wasn't imported. The other sessions were. Fix it and import again if needed."
  },
  "csv_pref_too_many_skipped": {
    "vi": "{student_id}: có {count} nguyện vọng, nhiều hơn mức tối đa {tran}, nên học sinh này chưa được nạp.",
    "en": "{student_id}: has {count} preferences, more than the limit of {tran}, so this student wasn't imported."
  },
  "csv_thi_too_many_skipped": {
    "vi": "{student_id}: đăng ký dự thi {count} CLB, nhiều hơn mức tối đa {tran}, nên học sinh này chưa được nạp.",
    "en": "{student_id}: signed up to test for {count} clubs, more than the limit of {tran}, so this student wasn't imported."
  },
  "csv_unknown_clubs_skipped": {
    "vi": "{student_id}: không tìm thấy các CLB {club_ids}, nên học sinh này chưa được nạp.",
    "en": "{student_id}: clubs {club_ids} weren't found, so this student wasn't imported."
  },
  "csv_student_missing_skipped": {
    "vi": "{student_id}: chưa có trong danh sách học sinh nên được bỏ qua. Bật tuỳ chọn tự tạo học sinh mới để nạp cả mã này.",
    "en": "{student_id}: not in the student list, so it was skipped. Turn on adding new students automatically to include it."
  },
  "score_not_applicant": {
    "vi": "{student_id}: không có trong danh sách dự thi của CLB này.",
    "en": "{student_id}: isn't on this club's test list."
  },
  "score_not_a_number": {
    "vi": "{student_id}: điểm “{score}” không phải là số nên chưa được lưu.",
    "en": "{student_id}: the score “{score}” isn't a number, so it wasn't saved."
  },
  "score_negative": {
    "vi": "{student_id}: điểm “{score}” là số âm, có thể do gõ thừa dấu trừ. Điểm này chưa được lưu.",
    "en": "{student_id}: the score “{score}” is negative, probably an extra minus sign. It wasn't saved."
  },
  "health_scoring_none": {
    "vi": "CLB {club_id}: có {n_applicants} học sinh dự thi nhưng chưa ai được chấm điểm. Nếu sắp xếp lúc này, các học sinh đó chỉ được xét theo số bốc thăm.",
    "en": "Club {club_id}: {n_applicants} student(s) took the test but none have a score yet. If the allocation runs now, those students will be ranked by lottery number only."
  },
  "health_scoring_partial": {
    "vi": "CLB {club_id}: mới chấm {n_scored}/{n_applicants} học sinh. {n_missing} học sinh chưa có điểm sẽ xếp sau tất cả học sinh đã có điểm.",
    "en": "Club {club_id}: {n_scored} of {n_applicants} students are scored. The {n_missing} without a score will rank below every scored student."
  },
  "health_tested_not_ranked": {
    "vi": "{n} lượt dự thi sẽ không có tác dụng vì học sinh dự thi một CLB nhưng không chọn CLB đó làm nguyện vọng. Ví dụ: {sample}",
    "en": "{n} test sign-up(s) won't count because the student tested for a club but didn't list it as a preference. For example: {sample}"
  },
  "health_diem_khong_dang_ky_thi": {
    "vi": "{n} điểm chấm không còn ô đăng ký thi đi kèm (học sinh đã bỏ đăng ký sau khi được chấm). Lần chạy sắp xếp bỏ qua các điểm này, và màn hình Nhập điểm không hiện chúng. Để dọn: mở học sinh đó ở thẻ \"Nhập tại chỗ\" và bấm \"Lưu CLB dự thi\". Ví dụ: {sample}",
    "en": "{n} score(s) no longer have a matching test registration (the student withdrew after being scored). Allocation runs ignore these scores, and the Score entry screen does not show them. To clean up: open that student in the \"Kiosk entry\" tab and press \"Save test clubs\". For example: {sample}"
  },
  "health_thi_qua_tran_buoi": {
    "vi": "{n} học sinh đăng ký thi quá {tran} câu lạc bộ trong buổi {buoi}, thường do một câu lạc bộ vừa được chuyển sang buổi này ở màn Quản lý CLB & dự trữ. Thi thêm câu lạc bộ là được xét ưu tiên ở thêm chỗ, không công bằng với học sinh khác. Sửa ở màn Nhập tại chỗ: mở học sinh đó, bỏ bớt CLB dự thi của buổi này rồi lưu. Ví dụ (số câu lạc bộ đang thi): {sample}",
    "en": "{n} student(s) are signed up to test for more than {tran} clubs on {buoi}, usually because a club was just moved to this session in Clubs & reserves. Testing for extra clubs gives them priority in more places, which is unfair to others. Fix it in the Kiosk entry tab: open the student, untick some of this session's test clubs and save. For example (clubs being tested for): {sample}"
  },
  "health_thi_qua_tran": {
    "vi": "{n} học sinh đăng ký thi quá {tran} câu lạc bộ, thường do danh sách câu lạc bộ vừa được sửa ở màn Quản lý CLB & dự trữ. Thi thêm câu lạc bộ là được xét ưu tiên ở thêm chỗ, không công bằng với học sinh khác. Sửa ở màn Nhập tại chỗ: mở học sinh đó, bỏ bớt CLB dự thi rồi lưu. Ví dụ (số câu lạc bộ đang thi): {sample}",
    "en": "{n} student(s) are signed up to test for more than {tran} clubs, usually because the club list was just edited in Clubs & reserves. Testing for extra clubs gives them priority in more places, which is unfair to others. Fix it in the Kiosk entry tab: open the student, untick some test clubs and save. For example (clubs being tested for): {sample}"
  },
  "health_vi_pham_clb_suc_chua_sai": {
    "vi": "{n} câu lạc bộ có sức chứa không hợp lệ (sức chứa phải lớn hơn 0, suất dự trữ từ 0 tới sức chứa). Sửa ở màn Quản lý CLB & dự trữ. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "{n} club(s) have invalid capacity (capacity must be above 0, reserve seats between 0 and capacity). Fix them in Clubs & reserves. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_nguyen_vong_hang_sai": {
    "vi": "{n} nguyện vọng có thứ hạng nhỏ hơn 1. Nhập lại nguyện vọng của những học sinh này. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "{n} preference(s) have a rank below 1. Re-enter these students' preferences. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_diem_am": {
    "vi": "{n} điểm chấm là số âm. Sửa ở màn Nhập điểm. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "{n} score(s) are negative. Fix them in the Score entry tab. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_mo_coi_hoc_sinh": {
    "vi": "Bảng {bang} có dữ liệu của {n} mã học sinh không còn tồn tại. Tạo lại học sinh có mã đó, hoặc bấm \"Xoá toàn bộ học sinh (giữ CLB)\" ở màn Quản lý CLB & dự trữ. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "Table {bang} holds data for {n} student ID(s) that no longer exist. Recreate a student with that ID, or click \"Delete all students (keep clubs)\" in Clubs & reserves. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_vi_pham_mo_coi_clb": {
    "vi": "Bảng {bang} có dữ liệu của {n} mã câu lạc bộ không còn tồn tại. Tạo lại câu lạc bộ có mã đó ở màn Quản lý CLB & dự trữ. Ví dụ: {sample}. Phần mềm chưa bật được lớp chặn dữ liệu hỏng cho tệp dữ liệu này; sửa xong thì đóng và mở lại phần mềm để bật.",
    "en": "Table {bang} holds data for {n} club ID(s) that no longer exist. Recreate a club with that ID in Clubs & reserves. For example: {sample}. The software cannot switch on its bad-data protection for this database until this is fixed; after fixing, close and reopen the software to switch it on."
  },
  "health_student_no_preferences": {
    "vi": "{n} học sinh chưa có nguyện vọng nào nên sẽ không được xếp vào CLB nào. Ví dụ: {sample}",
    "en": "{n} student(s) have no preferences, so none of them will be placed in a club. For example: {sample}"
  },
  "health_orphan_student_group": {
    "vi": "Nhãn dự trữ \"{reserve_group}\" đang gán cho {n} học sinh nhưng không CLB nào dùng nhãn này, có thể do gõ sai (ví dụ: {sample}). Các học sinh này sẽ không được ưu tiên ở đâu. Sửa ở thẻ Quản lý: tìm học sinh, đánh dấu, để trống ô nhãn rồi bấm \"Gán cho học sinh đã đánh dấu\".",
    "en": "The reserve label \"{reserve_group}\" is given to {n} student(s) but no club uses it, which may be a typo (for example: {sample}). These students won't get priority anywhere. To fix it on the Admin tab: find the students, tick them, leave the label box empty, and click \"Assign to ticked students\"."
  },
  "health_club_reserve_no_group": {
    "vi": "CLB {club_id} có {reserve_capacity} suất dự trữ nhưng chưa có nhãn dự trữ, nên các suất này sẽ thành suất thường.",
    "en": "Club {club_id} has {reserve_capacity} reserve seat(s) but no reserve label, so those seats will become regular seats."
  },
  "health_club_group_no_students": {
    "vi": "CLB {club_id} để {reserve_capacity} suất cho nhãn \"{reserve_group}\", nhưng chưa học sinh nào có nhãn này. Các suất đó sẽ bỏ trống.",
    "en": "Club {club_id} keeps {reserve_capacity} seat(s) for the label \"{reserve_group}\", but no student has that label. Those seats will go unused."
  },
  "health_score_outlier": {
    "vi": "CLB {club_id}: có {n} điểm khác hẳn các điểm còn lại (điểm giữa của CLB là {trung_vi}). Ví dụ: {sample}. Có thể điểm bị gõ nhầm, như 70 thay cho 7,0. Kiểm tra lại ở thẻ Chấm điểm.",
    "en": "Club {club_id}: {n} score(s) are far from the rest (the club's middle score is {trung_vi}). For example: {sample}. A score may be mistyped, such as 70 instead of 7.0. Check them on the Scoring tab."
  },
  "health_oversubscribed": {
    "vi": "Tổng số chỗ là {n_seats} nhưng có {n_students} học sinh đã nộp nguyện vọng. Ít nhất {n_short} học sinh sẽ không có chỗ.",
    "en": "There are {n_seats} seats in total but {n_students} students submitted preferences. At least {n_short} student(s) won't get a seat."
  },
  "health_oversubscribed_chua_khai_buoi": {
    "vi": "Các câu lạc bộ chưa khai buổi có tổng {n_seats} chỗ, trong khi {n_students} học sinh xếp nguyện vọng vào các câu lạc bộ này. Ít nhất {n_short} học sinh chắc chắn không có chỗ ở nhóm này. Các câu lạc bộ chưa khai buổi được xếp chung như một buổi riêng. Hãy khai buổi cho chúng ở màn Quản lý CLB & dự trữ, tăng sức chứa, hoặc chấp nhận.",
    "en": "Clubs with no session set have {n_seats} seats in total, but {n_students} student(s) ranked these clubs. At least {n_short} student(s) will certainly get no seat among them. Clubs with no session set are matched together as one separate session. Set their session in Clubs & reserves, raise capacity, or accept it."
  },
  "health_oversubscribed_buoi": {
    "vi": "Buổi {buoi} có tổng {n_seats} chỗ, trong khi {n_students} học sinh xếp nguyện vọng ở buổi này. Ít nhất {n_short} học sinh chắc chắn không có câu lạc bộ nào trong buổi {buoi}. Chỗ trống ở buổi khác không bù được. Hãy tăng sức chứa, thêm câu lạc bộ cho buổi này, hoặc chấp nhận.",
    "en": "Session {buoi} has {n_seats} seats in total, but {n_students} student(s) ranked clubs in this session. At least {n_short} student(s) will certainly get no club on {buoi}. Free seats in other sessions cannot make up for it. Raise capacity, add a club to this session, or accept it."
  },
  "recovery_db_is_healthy": {
    "vi": "Tệp dữ liệu hiện tại vẫn đọc được bình thường, nên phần mềm không đổi tên hay thay thế nó. Lỗi lúc khởi động có lẽ không phải do dữ liệu hỏng, mà thường do thư mục không có quyền ghi hoặc tệp đang được mở ở chương trình khác. Đóng các chương trình khác, chuyển thư mục phần mềm ra chỗ có quyền ghi (ví dụ Desktop), rồi mở lại.",
    "en": "The current data file still reads normally, so it was not renamed or replaced. The startup error is probably not corrupt data. Usually the folder is not writable, or the file is open in another program. Close other programs, move the app folder somewhere writable (for example the Desktop), and open it again."
  },
  "recovery_no_backups": {
    "vi": "Không tìm thấy bản sao lưu nào. Có thể máy này chưa sắp xếp lần nào, hoặc thư mục sao lưu đã bị xoá.",
    "en": "No backups were found. This computer may not have run an allocation yet, or the backup folder was deleted."
  },
  "recovery_all_backups_corrupt": {
    "vi": "Đã thử {n_tried} bản sao lưu nhưng không bản nào mở được.",
    "en": "Tried {n_tried} backup(s), but none could be opened."
  },
  "recovery_restore_failed": {
    "vi": "Không khôi phục được dữ liệu. Hãy thử lại.",
    "en": "Couldn't restore the data. Try again."
  },
  "recovery_restored_from": {
    "vi": "Đã khôi phục từ bản sao lưu {backup_name}. Bỏ qua {n_skipped} bản mới hơn vì không mở được.",
    "en": "Restored from backup {backup_name}. Skipped {n_skipped} newer backup(s) that couldn't be opened."
  },
  "recovery_fresh_created": {
    "vi": "Đã tạo một tệp dữ liệu mới, trống. Tệp cũ được đổi tên và vẫn nằm trong cùng thư mục.",
    "en": "Created a new, empty data file. The old file was renamed and is still in the same folder."
  },
  "so_nhap_khong_phai_so": {
    "vi": "Đây không phải Sổ nhập CLB (cần có hai sheet \"1. CLB\" và \"2. Học sinh\"). Hãy bấm \"Tải sổ nhập mẫu\", điền vào sổ đó rồi nạp lại.",
    "en": "This isn't a Club Input Workbook (it needs the sheets \"1. CLB\" and \"2. Học sinh\"). Click \"Download the input workbook\", fill it in and import it again."
  },
  "so_nhap_chi_nhan_xlsx": {
    "vi": "Phần mềm chỉ nhận Sổ nhập CLB (tệp .xlsx). Hãy bấm \"Tải sổ nhập mẫu\", điền vào sổ đó rồi nạp lại.",
    "en": "Only the Club Input Workbook (.xlsx) can be imported. Click \"Download the input workbook\", fill it in and import it again."
  },
  "so_nhap_thieu_sheet": {
    "vi": "Sổ nhập thiếu sheet \"{sheet}\".",
    "en": "The workbook is missing the sheet \"{sheet}\"."
  },
  "so_nhap_thieu_cot": {
    "vi": "Sheet \"{sheet}\" thiếu cột \"{cot}\". Đừng xoá hay đổi tên dòng tiêu đề của sổ.",
    "en": "Sheet \"{sheet}\" is missing the column \"{cot}\". Don't delete or rename the workbook's header row."
  },
  "so_nhap_khong_co_clb": {
    "vi": "Sheet \"{sheet}\" chưa có câu lạc bộ nào.",
    "en": "Sheet \"{sheet}\" has no clubs yet."
  },
  "so_nhap_clb_thieu_ten": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: thiếu Tên CLB.",
    "en": "Sheet \"{sheet}\", row {dong}: the club name is missing."
  },
  "so_nhap_clb_trung_ten": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: tên CLB \"{ten}\" đã có ở dòng {dong_truoc}. Mỗi CLB một tên riêng.",
    "en": "Sheet \"{sheet}\", row {dong}: the club name \"{ten}\" is already used on row {dong_truoc}. Each club needs its own name."
  },
  "so_nhap_clb_trung_ma": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: Mã CLB \"{ma}\" đã có ở dòng {dong_truoc}.",
    "en": "Sheet \"{sheet}\", row {dong}: the club code \"{ma}\" is already used on row {dong_truoc}."
  },
  "so_nhap_chi_tieu_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): Chỉ tiêu phải là số nguyên lớn hơn 0, Suất ưu tiên không được lớn hơn Chỉ tiêu (đang ghi: {chi_tieu} / {uu_tien}).",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): seats must be a whole number above 0, and priority seats can't exceed seats (found: {chi_tieu} / {uu_tien})."
  },
  "so_nhap_thieu_ma_hs": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: thiếu Mã HS.",
    "en": "Sheet \"{sheet}\", row {dong}: the student ID is missing."
  },
  "so_nhap_hs_trung": {
    "vi": "Sheet \"{sheet}\", dòng {dong}: Mã HS {student_id} đã có ở dòng {dong_truoc}. Mỗi học sinh một dòng.",
    "en": "Sheet \"{sheet}\", row {dong}: student ID {student_id} is already on row {dong_truoc}. One row per student."
  },
  "so_nhap_clb_khong_co": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}), NV{k}: không có CLB nào tên \"{gia_tri}\" ở sheet \"1. CLB\". Hãy chọn tên trong danh sách thả xuống.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}), NV{k}: there is no club called \"{gia_tri}\" on sheet \"1. CLB\". Pick a name from the drop-down list."
  },
  "so_nhap_nv_trung": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): \"{gia_tri}\" được chọn hai lần (NV{k_truoc} và NV{k}).",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): \"{gia_tri}\" is chosen twice (NV{k_truoc} and NV{k})."
  },
  "so_nhap_diem_sai": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}), Điểm {k}: \"{gia_tri}\" không phải điểm. Ghi một số (vd 8,5), hoặc chữ thi nếu chưa có điểm.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}), Điểm {k}: \"{gia_tri}\" isn't a score. Enter a number (e.g. 8.5), or the word thi if the score isn't known yet."
  },
  "so_nhap_diem_khong_nv": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): có Điểm {k} nhưng NV{k} trống. Điểm phải nằm ngay cạnh CLB của nó.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): Điểm {k} is filled but NV{k} is empty. A score must sit right next to its club."
  },
  "loi_nap_so_nhap": {
    "vi": "Không nạp được sổ nhập. Kiểm tra lại tệp rồi thử lần nữa.",
    "en": "Couldn't import the workbook. Check the file and try again."
  },
  "so_nhap_mau_loi": {
    "vi": "Không tạo được sổ nhập mẫu. Hãy thử lại.",
    "en": "Couldn't create the input workbook. Try again."
  },
  "so_nhap_qua_tran_nv": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): {n} nguyện vọng ở buổi {buoi}, tối đa {tran} mỗi buổi. Bớt nguyện vọng của buổi này.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): {n} preferences in session {buoi}, at most {tran} per session. Remove some for this session."
  },
  "so_nhap_qua_tran_thi": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({student_id}): thi {n} CLB ở buổi {buoi}, tối đa {tran} mỗi buổi. Xoá bớt ô Điểm của buổi này.",
    "en": "Sheet \"{sheet}\", row {dong} ({student_id}): {n} tested clubs in session {buoi}, at most {tran} per session. Clear some Điểm cells for this session."
  },
  "so_nhap_ma_tu_sinh_trung": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): mã tự tạo \"{ma}\" trùng với CLB ở dòng {dong_truoc}. Điền Mã CLB cho một trong hai dòng.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): the generated code \"{ma}\" clashes with the club on row {dong_truoc}. Fill in Mã CLB on one of the two rows."
  },
  "so_nhap_canh_bao_xoa_diem": {
    "vi": "{n} điểm đã chấm trong phần mềm sẽ bị xoá, vì sổ ghi \"thi\" (chưa có điểm) ở các ô đó. Muốn giữ điểm thì xuất lại dữ liệu đầu vào thành sổ mới rồi sửa trên sổ đó.",
    "en": "{n} score(s) already entered in the app will be removed, because the workbook says \"thi\" (no score yet) in those cells. To keep them, export the current input data to a new workbook and edit that one."
  },
  "so_nhap_canh_bao_bo_nhom": {
    "vi": "{n} học sinh đang có Nhóm ưu tiên sẽ bị bỏ nhóm, vì ô Nhóm ưu tiên của những học sinh đó trong sổ để trống.",
    "en": "{n} student(s) who currently have a priority group will lose it, because their Nhóm ưu tiên cell in the workbook is empty."
  },
  "so_nhap_canh_bao_clb_ngoai_so": {
    "vi": "{n} CLB có trong phần mềm nhưng không có trong sổ ({ten}). Chúng vẫn được giữ. Nếu đó là CLB vừa đổi tên thì giữ nguyên Mã CLB khi đổi tên, rồi xoá CLB thừa ở thẻ 04.",
    "en": "{n} club(s) are in the app but not in the workbook ({ten}). They are kept. If one was just renamed, keep its Mã CLB when renaming, then delete the leftover club on tab 04."
  },
  "so_nhap_ma_tu_sinh_trung_clb_da_co": {
    "vi": "Sheet \"{sheet}\", dòng {dong} ({ten}): mã tự tạo \"{ma}\" trùng mã của CLB \"{ten_cu}\" đã có trong phần mềm. Nếu đây chính là CLB đó (đổi tên), điền Mã CLB là {ma_cu}; nếu là CLB khác, điền một Mã CLB mới.",
    "en": "Sheet \"{sheet}\", row {dong} ({ten}): the generated code \"{ma}\" is already used by the club \"{ten_cu}\" in the app. If this is that club (renamed), fill in Mã CLB as {ma_cu}; if it is a different club, fill in a new Mã CLB."
  }
};
