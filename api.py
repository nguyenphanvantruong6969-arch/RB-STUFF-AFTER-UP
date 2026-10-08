"""
api.py
======
Lớp API expose cho pywebview — mọi hàm public ở đây có thể được gọi
từ JS qua window.pywebview.api.<ten_ham>(...) và luôn trả về dict
(pywebview tự serialize JSON hai chiều).

Quy ước trả về thống nhất cho mọi hàm:
    { "ok": bool, "data": ..., "errors": [...] }
Để JS chỉ cần check `.ok` là biết thành công hay không, không phải
try/catch riêng lẻ từng hàm.

Mỗi phần tử trong "errors" (và trong các danh sách "warnings" trả về
kèm data khi ok=True) là MỘT trong hai dạng:
  - chuỗi thô — hiển thị nguyên văn, không dịch. (Vết ngăn xếp KHÔNG đi lên
    giao diện; xem _loi_co_ghi_vet, ghi vào loi_ung_dung.txt cạnh app.db.)
  - {"code": "...", "params": {...}} — do err() ở i18n_errors.py tạo ra,
    frontend tự dịch sang ngôn ngữ đang chọn (bảng dịch ở i18n_loi.js,
    SINH TỪ MESSAGES trong i18n_errors.py bằng tao_i18n_js.py).
Điều này cho phép app hỗ trợ song ngữ (vi/en) mà không cần Python biết
người dùng đang chọn ngôn ngữ nào.
"""

import contextlib
import csv
import datetime
import os
import sqlite3
import statistics
import threading

from api_chung import (
    _fail_co_buoc,
    _now,
)
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import (
    BUOI_MAC_DINH,
    CHE_DO_BOC_THAM_MAC_DINH,
    cac_dong_match_results,
    cat_du_lieu_theo_buoi,
    chen_stb_cho_hoc_sinh_moi,
    connect_db,
    default_reserve_eligible_fn,
    generate_stb_lottery,
    init_db,
    load_from_sqlite,
    load_from_sqlite_kem_dau_van_tay,
    nhom_theo_buoi,
    run_rbda_nhieu_buoi,
    sanity_check_result,
    TRAN_CLB_THI_MOI_BUOI,
    sap_buoi,
    soat_vi_pham_rang_buoc,
    validate_data_integrity,
    verify_stability,
)

from api_bao_cao import BaoCaoMixin
from api_cham_diem import ChamDiemMixin
from api_nhap import NhapDuLieuMixin
from api_quan_ly import QuanLyMixin
from api_xuat import XuatKetQuaMixin


# PipelineAPI GHÉP từ các phần theo việc. Tách tệp chứ KHÔNG tách lớp:
# pywebview đưa MỌI hàm public của đối tượng js_api lên window.pywebview.api,
# nên giao diện vẫn thấy đúng một đối tượng với đủ các hàm như trước.
#
# Phần ở lại tệp này là LÕI: khởi tạo, kết nối CSDL, sao lưu, sức khoẻ dữ
# liệu và run_pipeline. Chúng ở lại đây có chủ ý — test thay
# `api.connect_db`, `api.run_rbda_nhieu_buoi`... để giả lập sự cố, và phép
# thay đó chỉ có tác dụng với mã nằm trong CHÍNH tệp này.
class PipelineAPI(NhapDuLieuMixin, ChamDiemMixin, BaoCaoMixin,
                  XuatKetQuaMixin, QuanLyMixin):
    def __init__(self, db_path: str, thu_muc_xuat: str = ""):
        self.db_path = db_path
        # MỘT khoá cho mọi thao tác GHI trong tiến trình này.
        #
        # pywebview chạy mỗi lời gọi từ giao diện trên một luồng riêng, và
        # chế độ trình duyệt dùng ThreadingHTTPServer — tức các lời gọi
        # THẬT SỰ chạy song song. run_pipeline đọc dữ liệu ở một kết nối
        # rồi mới ghi ở kết nối khác: bấm "Chạy" hai lần, hoặc kiosk lưu
        # nguyện vọng đúng lúc đang chạy, thì hai lần chạy cùng vẽ lại số
        # bốc thăm, hoặc nguyện vọng vừa lưu bị kết quả cũ đè lên mà không
        # ai hay. Khoá này xếp chúng thành hàng: lời gọi sau CHỜ lời gọi
        # trước xong, thay vì chạy chồng lên nhau hay chờ 15 giây rồi báo
        # "database is locked". RLock vì run_pipeline có thể gọi lại chính
        # các hàm ghi khác trong cùng luồng.
        self._khoa_ghi = threading.RLock()
        # Giao dịch chung đang mở trong luồng này (xem _mot_giao_dich).
        self._giao_dich = threading.local()
        self._bo_nho_xuat = None
        # Nơi đặt tệp kết quả khi người dùng không tự chọn đường dẫn.
        # Thứ tự: tham số -> biến môi trường (để test không ghi vào thư
        # mục Tải xuống thật của máy) -> thư mục Tải xuống của hệ điều
        # hành. Rỗng hết thì export_csv lùi về cạnh app.db.
        self.thu_muc_xuat = (
            thu_muc_xuat or os.environ.get("RBDA_THU_MUC_TAI_VE", "") or "")
        # DẤU GẠCH DƯỚI LÀ BẮT BUỘC, không phải quy ước cho đẹp. Xem
        # _set_window() ngay dưới đây.
        self._window = None
        init_db(self.db_path)

    def _set_window(self, window) -> None:
        """
        Gọi từ main.py sau webview.create_window(...):
            api = PipelineAPI(db_path)
            window = webview.create_window("...", "index.html", js_api=api)
            api._set_window(window)
        Không bắt buộc — nếu không gọi, mọi tính năng vẫn hoạt động,
        chỉ riêng import CSV sẽ nhận nội dung file qua FileReader ở JS
        (đã dùng theo mặc định) thay vì hộp thoại chọn file gốc của hệ điều hành.

        VÌ SAO TÊN PHẢI BẮT ĐẦU BẰNG DẤU GẠCH DƯỚI — đây từng là lỗi làm
        TREO HẲN app trên Windows (cửa sổ ghi "Not Responding"):

        pywebview dựng cầu nối bằng cách DÒ chính đối tượng API này
        (webview/util.py, get_functions). Luật của nó là:

            for name in dir(obj):
                if name.startswith('_'): continue      # <- lối thoát duy nhất
                attr = getattr(obj, name)              # <- KÍCH HOẠT property
                ...
                elif not callable(attr) and hasattr(attr, '__module__'):
                    get_functions(attr, ...)           # <- ĐỆ QUY vào attr

        Cửa sổ pywebview không callable và có `__module__`, nên khi nó nằm ở
        một thuộc tính CÔNG KHAI, pywebview đệ quy vào chính cửa sổ của nó —
        và `dir()` cửa sổ đó có bốn property CHẶN (webview/window.py):

            @property
            def width(self):
                self.events.shown.wait(15)              # chờ tới 15 giây
                width, _ = self.gui.get_size(self.uid)  # đọc Control.Size

        `width`, `height`, `x`, `y`: mỗi cái chờ tới 15 giây, và `get_size`
        đọc thuộc tính của một control WinForms TỪ LUỒNG KHÁC luồng giao
        diện. Luồng dò bị chặn -> finish.js không bao giờ chạy ->
        `window.pywebview.api` mãi rỗng -> giao diện báo không kết nối được,
        còn cửa sổ thì treo.

        Dấu gạch dưới cắt đứt chuỗi đó ngay bước đầu: `get_functions` bỏ qua
        tên bắt đầu bằng `_` TRƯỚC khi gọi `getattr`, nên cửa sổ không hề bị
        chạm tới. Có test canh (tests/test_do_api.py).
        """
        self._window = window

    # -----------------------------------------------------------------
    # TAB "VẬN HÀNH PIPELINE"
    # -----------------------------------------------------------------

    def get_last_run_info(self):
        """Thông tin lần chạy pipeline gần nhất — để hiện ở sidebar/dashboard."""
        try:
            with self._ket_noi_doc() as cur:
                row = cur.execute("SELECT * FROM run_meta WHERE id = 1").fetchone()
            return _ok(dict(row) if row else None)
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def get_dashboard_status(self):
        """Số liệu tổng quan để hiển thị ngay khi mở tab Pipeline."""
        try:
            with self._ket_noi_doc() as cur:
                n_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
                n_clubs = cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0]
                n_prefs = cur.execute(
                    "SELECT COUNT(DISTINCT student_id) FROM preferences"
                ).fetchone()[0]
                n_matched = cur.execute(
                    "SELECT COUNT(DISTINCT student_id) FROM match_results "
                    "WHERE club_id IS NOT NULL"
                ).fetchone()[0]
                has_results = cur.execute(
                    "SELECT COUNT(DISTINCT student_id) FROM match_results"
                ).fetchone()[0] > 0
            return _ok({
                "n_students": n_students,
                "n_clubs": n_clubs,
                "n_students_with_preferences": n_prefs,
                "n_matched": n_matched,
                "has_results": has_results,
            })
        except Exception as e:
            return _fail(err("error_reading_dashboard", detail=str(e)))

    def check_data_integrity(self):
        """Nút 'Kiểm tra dữ liệu' — chỉ validate, KHÔNG chạy pipeline."""
        try:
            students, clubs, tested_scores, applicants, preferences, _ = (
                load_from_sqlite(self.db_path)
            )
            errors = validate_data_integrity(students, clubs, preferences, applicants)
            if errors:
                return _fail(errors)
            return _ok({
                "message": "Du lieu hop le.",
                "n_students": len(students),
                "n_clubs": len(clubs),
            })
        except Exception as e:
            return _fail(self._loi_co_ghi_vet(err("error_checking_integrity", detail=str(e))))

    # -----------------------------------------------------------------
    # KIỂM TRA SỨC KHOẺ DỮ LIỆU (pre-flight)
    #
    # validate_data_integrity() chỉ bắt dữ liệu KHÔNG HỢP LỆ (club không
    # tồn tại, capacity <= 0, nguyện vọng trùng…). Nhưng có cả một nhóm
    # tình huống mà dữ liệu VẪN HỢP LỆ, pipeline VẪN CHẠY, kết quả VẪN
    # trông bình thường — trong khi ai được vào club đã bị thay đổi bởi
    # một thiếu sót mà người vận hành không hề thấy. Ví dụ nguy hiểm nhất:
    # giáo viên mới chấm được một nửa danh sách, nửa còn lại lập tức bị
    # xếp dưới TOÀN BỘ các em đã có điểm — kể cả em thấp điểm nhất.
    #
    # Hàm này liệt kê đúng nhóm đó dưới dạng CẢNH BÁO (không phải lỗi):
    # không chặn chạy pipeline, nhưng bắt buộc phải hiện ra trước mắt
    # người vận hành để họ tự quyết định.
    # -----------------------------------------------------------------

    _HEALTH_SAMPLE_LIMIT = 5

    # Nguong bao "diem la": gap bao nhieu lan TRUNG VI cua chinh CLB do.
    #
    # Chon 3.0 bang so do, khong phai cam tinh. Do tren 579 o diem that
    # cua hai bo du lieu: ti le (diem cao nhat / trung vi) trong mot CLB
    # cao nhat la 1.42. Loi go lech dau cham thi lech gap ~10 lan. Giua
    # 1.42 va 10 la mot khoang trong gan mot bac do lon.
    #
    # Quet thu: he so 1.5 -> 11 canh bao GIA; tu 2.0 tro len -> 0. Lay
    # 3.0 de cach xa ca that te nhat 2.1 lan ma van thua suc bat loi go.
    _NGUONG_DIEM_LA = 3.0

    def get_data_health_report(self):
        """
        Rà soát các thiếu sót dữ liệu ÂM THẦM LÀM ĐỔI KẾT QUẢ.
        Trả về {"warnings": [...], "n_warnings": int, "n_high": int} —
        mỗi cảnh báo là {code, params, severity} với severity là
        "high" (gần như chắc chắn làm sai kết quả) hoặc "medium"/"info".
        """
        try:
            with self._ket_noi_doc() as cur:
                warnings = []

                def warn(severity, code, **params):
                    entry = err(code, **params)
                    entry["severity"] = severity
                    warnings.append(entry)

                # --- 1. Chấm điểm thiếu / chưa chấm ---------------------------
                for row in cur.execute("""
                    SELECT c.club_id,
                           COUNT(DISTINCT t.student_id) AS n_applicants,
                           COUNT(DISTINCT sc.student_id) AS n_scored
                    FROM clubs c
                    JOIN club_test_selection t ON t.club_id = c.club_id
                    LEFT JOIN club_scores sc
                           ON sc.club_id = c.club_id AND sc.student_id = t.student_id
                    GROUP BY c.club_id
                    ORDER BY c.club_id
                """).fetchall():
                    n_app, n_scored = row["n_applicants"], row["n_scored"]
                    if n_app == 0:
                        continue
                    if n_scored == 0:
                        warn("high", "health_scoring_none",
                             club_id=row["club_id"], n_applicants=n_app)
                    elif n_scored < n_app:
                        warn("high", "health_scoring_partial",
                             club_id=row["club_id"], n_applicants=n_app,
                             n_scored=n_scored, n_missing=n_app - n_scored)

                # --- 2. Đăng ký thi nhưng không xếp nguyện vọng club đó -------
                wasted = cur.execute("""
                    SELECT t.student_id, t.club_id
                    FROM club_test_selection t
                    LEFT JOIN preferences p
                           ON p.student_id = t.student_id AND p.club_id = t.club_id
                    WHERE p.student_id IS NULL
                    ORDER BY t.student_id, t.club_id
                """).fetchall()
                if wasted:
                    sample = ", ".join(
                        f"{r['student_id']}→{r['club_id']}"
                        for r in wasted[:self._HEALTH_SAMPLE_LIMIT]
                    )
                    warn("high", "health_tested_not_ranked",
                         n=len(wasted), sample=sample)

                # --- 2b. Có điểm nhưng không còn ô tick thi -------------------
                # Điểm của bài thi em đã rút. Các cửa ghi giờ tự dọn
                # (`_xoa_diem_khong_con_tick`), nên chỉ CSDL dựng bằng bản cũ
                # còn dòng này. Chạy sắp xếp đã bỏ qua chúng (`load_from_sqlite`)
                # — nhưng người dùng phải được biết, vì màn hình chấm điểm
                # không hiện những điểm này.
                mo_coi = cur.execute("""
                    SELECT sc.student_id, sc.club_id
                    FROM club_scores sc
                    LEFT JOIN club_test_selection t
                           ON t.student_id = sc.student_id AND t.club_id = sc.club_id
                    WHERE t.student_id IS NULL
                    ORDER BY sc.student_id, sc.club_id
                """).fetchall()
                if mo_coi:
                    warn("high", "health_diem_khong_dang_ky_thi",
                         n=len(mo_coi),
                         sample=", ".join(
                             f"{r['student_id']}→{r['club_id']}"
                             for r in mo_coi[:self._HEALTH_SAMPLE_LIMIT]))

                # --- 3. Học sinh chưa xếp nguyện vọng nào ---------------------
                no_pref = cur.execute("""
                    SELECT s.student_id FROM students s
                    LEFT JOIN preferences p ON p.student_id = s.student_id
                    WHERE p.student_id IS NULL
                    ORDER BY s.student_id
                """).fetchall()
                if no_pref:
                    warn("medium", "health_student_no_preferences",
                         n=len(no_pref),
                         sample=", ".join(r["student_id"] for r in no_pref[:self._HEALTH_SAMPLE_LIMIT]))

                # --- 4. Nhãn dự trữ của học sinh mà không club nào dùng -------
                # Kèm MÃ HỌC SINH như hai mục trên. Không có mã thì cảnh báo
                # bảo "kiểm tra xem có gõ sai chính tả không" mà người dùng
                # phải tự dò tay qua cả danh sách mới biết dò em nào.
                for row in cur.execute("""
                    SELECT s.reserve_group AS g, COUNT(*) AS n,
                           GROUP_CONCAT(s.student_id) AS ids
                    FROM students s
                    WHERE s.reserve_group IS NOT NULL AND TRIM(s.reserve_group) <> ''
                      AND s.reserve_group NOT IN (
                          SELECT reserve_group FROM clubs
                          WHERE reserve_group IS NOT NULL AND TRIM(reserve_group) <> ''
                      )
                    GROUP BY s.reserve_group ORDER BY s.reserve_group
                """).fetchall():
                    # GROUP_CONCAT không hứa thứ tự — phải sắp TRƯỚC khi cắt,
                    # nếu không mỗi lần bấm "Kiểm tra lại" lại ra một mẫu khác
                    # và người dùng tưởng dữ liệu vừa đổi.
                    ids = sorted((row["ids"] or "").split(","))
                    warn("high", "health_orphan_student_group",
                         reserve_group=row["g"], n=row["n"],
                         sample=", ".join(ids[:self._HEALTH_SAMPLE_LIMIT]))

                # --- 5. Club có suất dự trữ nhưng chưa đặt nhãn ---------------
                for row in cur.execute("""
                    SELECT club_id, reserve_capacity FROM clubs
                    WHERE reserve_capacity > 0
                      AND (reserve_group IS NULL OR TRIM(reserve_group) = '')
                    ORDER BY club_id
                """).fetchall():
                    warn("high", "health_club_reserve_no_group",
                         club_id=row["club_id"], reserve_capacity=row["reserve_capacity"])

                # --- 6. Club dành suất cho nhãn chưa học sinh nào mang --------
                for row in cur.execute("""
                    SELECT club_id, reserve_group, reserve_capacity FROM clubs
                    WHERE reserve_capacity > 0
                      AND reserve_group IS NOT NULL AND TRIM(reserve_group) <> ''
                      AND reserve_group NOT IN (
                          SELECT reserve_group FROM students
                          WHERE reserve_group IS NOT NULL AND TRIM(reserve_group) <> ''
                      )
                    ORDER BY club_id
                """).fetchall():
                    warn("medium", "health_club_group_no_students",
                         club_id=row["club_id"], reserve_group=row["reserve_group"],
                         reserve_capacity=row["reserve_capacity"])

                # --- 6b. Đăng ký thi vượt trần mỗi buổi -----------------------
                # Trần được kiểm ở cửa nhập, nhưng đổi buổi của CLB về sau
                # (màn Quản lý) có thể dồn nhiều ô tick hợp lệ vào cùng một
                # buổi. Thi thêm CLB là thêm chỗ được xét ở Tầng 1, nên đây là
                # chuyện công bằng — nhưng thuật toán vẫn đúng, nên chỉ cảnh báo.
                qua_tran: dict = {}
                for row in cur.execute("""
                    SELECT t.student_id AS sid,
                           COALESCE(NULLIF(c.buoi, ''), ?) AS buoi,
                           COUNT(*) AS n
                    FROM club_test_selection t
                    JOIN clubs c ON c.club_id = t.club_id
                    GROUP BY t.student_id, COALESCE(NULLIF(c.buoi, ''), ?)
                    HAVING COUNT(*) > ?
                    ORDER BY t.student_id
                """, (BUOI_MAC_DINH, BUOI_MAC_DINH, TRAN_CLB_THI_MOI_BUOI)).fetchall():
                    qua_tran.setdefault(row["buoi"], []).append(
                        (row["sid"], row["n"]))
                for buoi in sap_buoi(qua_tran):
                    ds = qua_tran[buoi]
                    sample = ", ".join(
                        "%s (%d)" % (sid, n)
                        for sid, n in ds[:self._HEALTH_SAMPLE_LIMIT])
                    if buoi == BUOI_MAC_DINH:
                        warn("high", "health_thi_qua_tran", n=len(ds),
                             tran=TRAN_CLB_THI_MOI_BUOI, sample=sample)
                    else:
                        warn("high", "health_thi_qua_tran_buoi", n=len(ds),
                             buoi=buoi, tran=TRAN_CLB_THI_MOI_BUOI,
                             sample=sample)

                # --- 6c. Dữ liệu vi phạm ràng buộc của CSDL ------------------
                # Chỉ có ở CSDL dựng bằng bản cũ mà dữ liệu không sạch: di trú
                # cố ý KHÔNG dựng lại bảng cho CSDL đó (xem
                # `_dung_lai_bang_co_rang_buoc`), nên CSDL chưa tự chặn được
                # dữ liệu hỏng. Chỉ ra dòng nào hỏng để nhà trường sửa; sửa
                # xong, mở lại phần mềm là ràng buộc được bật.
                for vp in soat_vi_pham_rang_buoc(cur):
                    warn("high", "health_vi_pham_" + vp["loai"],
                         bang=vp["bang"], n=vp["n"], sample=", ".join(vp["mau"]))

                # --- 7. Tổng chỗ ít hơn số học sinh đã nộp nguyện vọng --------
                # Đếm THEO BUỔI, vì mỗi buổi xếp riêng: chỗ trống của buổi
                # này không cứu được em nào ở buổi kia. Bản cũ cộng chỗ cả
                # tuần nên bỏ sót đúng ca nguy hiểm nhất — buổi ít CLB. Đo
                # được: Thứ Hai 3 CLB (30 chỗ), Thứ Năm 12 CLB (120 chỗ), 50
                # em xếp cả hai buổi -> tổng 150 chỗ, không cảnh báo, trong
                # khi 20 em chắc chắn trắng tay ở Thứ Hai.
                #
                # Học sinh được đếm ở buổi nào em có ÍT NHẤT MỘT nguyện vọng
                # ở buổi đó — em không xếp buổi nào thì không tranh chỗ ở đó.
                cho_theo_buoi = {
                    row["buoi"]: row["n"] for row in cur.execute("""
                        SELECT COALESCE(NULLIF(buoi, ''), ?) AS buoi,
                               COALESCE(SUM(capacity), 0) AS n
                        FROM clubs
                        GROUP BY COALESCE(NULLIF(buoi, ''), ?)
                    """, (BUOI_MAC_DINH, BUOI_MAC_DINH)).fetchall()
                }
                em_theo_buoi = {
                    row["buoi"]: row["n"] for row in cur.execute("""
                        SELECT COALESCE(NULLIF(c.buoi, ''), ?) AS buoi,
                               COUNT(DISTINCT p.student_id) AS n
                        FROM preferences p
                        JOIN clubs c ON c.club_id = p.club_id
                        GROUP BY COALESCE(NULLIF(c.buoi, ''), ?)
                    """, (BUOI_MAC_DINH, BUOI_MAC_DINH)).fetchall()
                }
                for buoi in sap_buoi(em_theo_buoi):
                    n_seats = cho_theo_buoi.get(buoi, 0)
                    n_with_prefs = em_theo_buoi[buoi]
                    if n_with_prefs <= n_seats:
                        continue
                    # Nhãn BUOI_MAC_DINH là chuỗi nội bộ, không phải thứ
                    # người dùng đọc được, nên không bao giờ nêu nó ra. Hai ca:
                    #   * trường MỘT buổi — nhóm mặc định là cả trường, giữ
                    #     đúng câu cũ "tổng chỗ toàn hệ thống";
                    #   * trường TRỘN (vài CLB chưa khai buổi, số còn lại đã
                    #     khai) — nhóm mặc định chỉ là các CLB chưa khai buổi.
                    #     Nói "toàn hệ thống" ở đây là sai số liệu, nên dùng
                    #     câu riêng gọi đúng tên nhóm đó.
                    if buoi == BUOI_MAC_DINH and len(cho_theo_buoi) > 1:
                        warn("info", "health_oversubscribed_chua_khai_buoi",
                             n_seats=n_seats, n_students=n_with_prefs,
                             n_short=n_with_prefs - n_seats)
                    elif buoi == BUOI_MAC_DINH:
                        warn("info", "health_oversubscribed",
                             n_seats=n_seats, n_students=n_with_prefs,
                             n_short=n_with_prefs - n_seats)
                    else:
                        warn("info", "health_oversubscribed_buoi",
                             buoi=buoi, n_seats=n_seats,
                             n_students=n_with_prefs,
                             n_short=n_with_prefs - n_seats)

                # --- 8. Điểm lệch hẳn khỏi phân bố của chính CLB đó ----------
                # Gõ 70 thay vì 7.0 thì phần mềm vẫn nhận, và em đó nhảy lên
                # đầu bảng. Đo trên bộ ví dụ: MỘT lỗi gõ làm BA em đổi chỗ,
                # vì em bị đẩy ra lại đi đẩy em khác.
                #
                # KHÔNG đặt trần cứng ở 10 — trường có thể chấm thang 100, và
                # chặn cứng là chặn nhầm. So với TRUNG VỊ CỦA CHÍNH CLB đó thì
                # thang nào cũng đúng, và bắt được cả hai phía: 70 (thừa) lẫn
                # 0.85 (thiếu).
                diem_theo_clb: dict = {}
                # Chỉ điểm còn ô tick — đúng tập điểm mà lần chạy sắp xếp
                # dùng (`load_from_sqlite`). Điểm không tick đã có cảnh báo
                # riêng ở mục 2b; tính nó vào trung vị ở đây là so với một
                # phân bố khác với thứ thật sự quyết định chỗ.
                for row in cur.execute("""
                    SELECT sc.club_id, sc.student_id, sc.score FROM club_scores sc
                    JOIN club_test_selection t
                      ON t.student_id = sc.student_id AND t.club_id = sc.club_id
                    ORDER BY sc.club_id, sc.student_id
                """).fetchall():
                    diem_theo_clb.setdefault(row["club_id"], []).append(
                        (row["student_id"], row["score"])
                    )
                for club_id in sorted(diem_theo_clb):
                    cap = diem_theo_clb[club_id]
                    # Dưới 3 điểm thì không có phân bố nào để mà so.
                    if len(cap) < 3:
                        continue
                    giua = statistics.median([s for _, s in cap])
                    if giua <= 0:
                        continue
                    la = [(sid, s) for sid, s in cap
                          if s > self._NGUONG_DIEM_LA * giua
                          or s * self._NGUONG_DIEM_LA < giua]
                    if la:
                        warn("high", "health_score_outlier",
                             club_id=club_id, n=len(la),
                             trung_vi=("%g" % giua),
                             sample=", ".join(
                                 "%s (%g)" % (sid, s)
                                 for sid, s in la[:self._HEALTH_SAMPLE_LIMIT]))

            return _ok({
                "warnings": warnings,
                "n_warnings": len(warnings),
                "n_high": sum(1 for w in warnings if w["severity"] == "high"),
            })
        except Exception as e:
            return _fail(err("error_checking_integrity", detail=str(e)))

    def get_pipeline_run_warning(self):
        """
        Gọi TRƯỚC khi hiện hộp xác nhận 'Chạy pipeline' (bước 1 trong xác
        nhận 2 bước). Cho UI biết: (a) đã có kết quả cũ sẽ bị ghi đè chưa,
        (b) STB đã bị khoá chưa (nếu khoá, chạy bình thường sẽ TÁI SỬ DỤNG
        STB cũ chứ không vẽ lại — chỉ vẽ lại nếu force_redraw_stb=True).
        """
        try:
            with self._ket_noi_doc() as cur:
                has_results = cur.execute(
                    "SELECT COUNT(DISTINCT student_id) FROM match_results"
                ).fetchone()[0] > 0
                lock_row = cur.execute(
                    "SELECT is_locked, locked_at, seed FROM stb_lock WHERE id = 1"
                ).fetchone()
                last_run = cur.execute(
                    "SELECT run_at, seed FROM run_meta WHERE id = 1"
                ).fetchone()
            return _ok({
                "has_existing_results": has_results,
                "stb_locked": bool(lock_row[0]) if lock_row else False,
                "stb_locked_at": lock_row[1] if lock_row else None,
                "stb_locked_seed": lock_row[2] if lock_row and lock_row[0] else None,
                "last_run_at": last_run[0] if last_run else None,
                "last_run_seed": last_run[1] if last_run else None,
            })
        except Exception as e:
            return _fail(err("error_checking_run_warning", detail=str(e)))

    def get_stb_lock_status(self):
        try:
            with self._ket_noi_doc() as cur:
                row = cur.execute(
                    "SELECT is_locked, locked_at, unlocked_at, seed FROM stb_lock WHERE id = 1"
                ).fetchone()
            if not row:
                return _ok({"is_locked": False, "locked_at": None,
                            "unlocked_at": None, "seed": None})
            return _ok({
                "is_locked": bool(row[0]),
                "locked_at": row[1],
                "unlocked_at": row[2],
                # Chỉ có nghĩa khi đang khoá: mở khoá (xoá dữ liệu) thì hạt
                # giống cũ không còn ràng buộc gì.
                "seed": row[3] if row[0] else None,
            })
        except Exception as e:
            return _fail(err("error_reading_stb_lock", detail=str(e)))

    def get_run_history(self, limit: int = 20):
        """Nhật ký toàn bộ các lần chạy pipeline, mới nhất trước — phục vụ kiểm toán.

        `buoi_da_chay` được ghi xuống từ lúc có tính năng chạy một phần, nhưng
        hàm này từng không đọc nó, nên bảng nhật ký hiện hai lần chạy chỉ khác
        nhau ở dấu thời gian — muốn biết lần nào đụng buổi nào phải mở app.db
        bằng tay. Một dấu vết kiểm toán không đọc được thì không phải dấu vết.
        """
        try:
            limit = max(1, min(int(limit), 200))
            with self._ket_noi_doc() as cur:
                rows = cur.execute(
                    "SELECT run_id, seed, run_at, rounds_run, n_matched, n_total, "
                    "       stb_redrawn, so_buoi, buoi_da_chay, che_do_boc_tham "
                    "FROM run_history ORDER BY run_id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            return _ok([dict(r) for r in rows])
        except Exception as e:
            return _fail(err("error_reading_run_history", detail=str(e)))

    _MAX_BACKUPS = 10

    def _loi_co_ghi_vet(self, loi):
        """Ghi vết ngăn xếp của ngoại lệ ĐANG xử lý vào `loi_ung_dung.txt`
        cạnh app.db, rồi trả `[loi, xem_nhat_ky]` để đưa lên giao diện: câu
        lỗi đã dịch, kèm một dòng nói chi tiết nằm ở tệp nào để gửi cho
        người phụ trách kỹ thuật.

        Trước đây vết ngăn xếp đi thẳng lên giao diện: lộ đường dẫn máy và
        cấu trúc mã cho bất kỳ ai đứng trước kiosk, mà người vận hành cũng
        không đọc được. Giờ giao diện chỉ hiện thông điệp đã dịch; người
        bảo trì mở tệp log khi cần. Chỉ gọi trong khối `except`.
        """
        import chan_doan

        chan_doan.ghi_ngoai_le_canh_db(
            self.db_path,
            "Loi: %s" % (loi.get("code") if isinstance(loi, dict) else loi))
        return [loi, err("xem_nhat_ky", file=chan_doan.TEN_LOG_UNG_DUNG)]

    @contextlib.contextmanager
    def _ket_noi_doc(self):
        """Kết nối CHỈ ĐỌC, trả về sẵn con trỏ.

        Gom lại một mẫu lặp 33 lần trong tệp này:

            conn = connect_db(self.db_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            ... truy vấn ...
            conn.close()

        Ba dòng đầu và dòng cuối chẳng nói gì về việc hàm đang làm; chúng
        chỉ che mất câu SQL — thứ duy nhất đáng đọc. Gom vào đây thì mỗi
        hàm còn đúng phần việc của nó.

        Và `close()` nay nằm trong `finally`: trước đây nó là dòng cuối
        của khối `try`, nên bất kỳ lỗi nào ở giữa cũng bỏ qua nó. Đã đo:
        trên CPython đếm tham chiếu thu hồi kịp nên KHÔNG rò thật (600
        lần gọi lỗi, 0 kết nối còn sống) — nhưng dựa vào chi tiết cài đặt
        của trình thông dịch để đóng tệp thì không phải cách viết đúng.
        """
        chung = getattr(self._giao_dich, "conn", None)
        if chung is not None:
            # Trong giao dịch chung: đọc trên CÙNG kết nối để thấy cả những
            # gì bước trước vừa ghi mà chưa commit.
            cur = chung.cursor()
            cur.row_factory = sqlite3.Row
            yield cur
            return
        conn = connect_db(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn.cursor()
        finally:
            conn.close()

    @contextlib.contextmanager
    def _mot_giao_dich(self):
        """Gộp nhiều lần ghi thành MỘT giao dịch: trọn vẹn, hoặc không gì cả.

        Trong khối này, mọi `_ket_noi_ghi` / `_ket_noi_doc` của CÙNG luồng
        dùng chung một kết nối và không tự commit. Khối chạy trọn thì commit
        một lần; ném lỗi thì rollback tất cả. Dùng cho Sổ nhập CLB: nạp CLB
        xong mà bước học sinh hỏng thì CLB cũng không được ở lại — nạp nửa
        sổ còn tệ hơn không nạp.
        """
        if getattr(self._giao_dich, "conn", None) is not None:
            yield                      # đã ở trong giao dịch chung
            return
        with self._khoa_ghi:
            conn = connect_db(self.db_path)
            self._giao_dich.conn = conn
            try:
                yield
                conn.commit()
            except BaseException:
                conn.rollback()
                raise
            finally:
                self._giao_dich.conn = None
                conn.close()

    @contextlib.contextmanager
    def _ket_noi_ghi(self):
        """Kết nối CÓ GHI: commit khi chạy trọn, rollback khi ném lỗi, luôn đóng.

        `rollback()` ở đây KHÔNG đổi hành vi — đóng một kết nối SQLite khi
        chưa commit thì giao dịch đang mở tự bị huỷ. Viết ra thành chữ vì
        đọc mã không nên phải nhớ luật đó mới biết dữ liệu có an toàn không.

        Đây là mẫu cho các thao tác ghi ĐƠN GIẢN, một giao dịch. `run_pipeline`
        KHÔNG dùng cái này: nó điều phối rollback và ghi nhật ký nhiều bước,
        và đó là hàm quan trọng nhất của phần mềm — để nguyên.
        """
        chung = getattr(self._giao_dich, "conn", None)
        if chung is not None:
            yield chung.cursor()       # commit/rollback do _mot_giao_dich lo
            return
        with self._khoa_ghi:
            conn = connect_db(self.db_path)
            try:
                yield conn.cursor()
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def _backup_db(self) -> str:
        """
        Sao lưu app.db bằng SQLite Backup API (connection.backup(), KHÔNG
        phải copy file thô) ngay TRƯỚC khi pipeline bắt đầu ghi gì —
        an toàn kể cả khi có tiến trình khác đang mở file cùng lúc, khác
        với copy file trực tiếp vốn có thể chụp phải trạng thái nửa-ghi
        (xem kế hoạch kiểm thử mất dữ liệu — artifact, xem BAN_GIAO.md mục 8). Giữ lại tối đa _MAX_BACKUPS bản
        gần nhất, tự xoá bản cũ hơn. Trả về đường dẫn bản sao lưu.
        """
        backup_dir = os.path.dirname(self.db_path) or "."
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{os.path.basename(self.db_path)}.bak-{ts}"
        backup_path = os.path.join(backup_dir, backup_name)

        src = connect_db(self.db_path)
        try:
            dst = sqlite3.connect(backup_path)
            try:
                src.backup(dst)
            finally:
                dst.close()
        except BaseException:
            # Bản sao DỞ DANG (đĩa đầy, bị ngắt) không được ở lại: nó mang
            # đúng tên của một bản sao lưu, nên vòng xoay bên dưới lần sau
            # sẽ tính nó là một trong 10 bản và đẩy một bản TỐT ra ngoài.
            try:
                os.remove(backup_path)
            except OSError:
                pass
            raise
        finally:
            src.close()

        prefix = f"{os.path.basename(self.db_path)}.bak-"
        existing = sorted(f for f in os.listdir(backup_dir) if f.startswith(prefix))
        for stale in existing[: -self._MAX_BACKUPS] if len(existing) > self._MAX_BACKUPS else []:
            try:
                os.remove(os.path.join(backup_dir, stale))
            except OSError:
                pass
        return backup_path

    def _xuat_match_results_csv(self, output_path: str) -> None:
        """Ghi `match_results.csv` từ CƠ SỞ DỮ LIỆU, không từ kết quả trong bộ nhớ.

        VÌ SAO KHÔNG DÙNG `result`. `export_match_results(result, ...)` đi qua
        `cac_dong_match_results(result)` — đúng cái generator dựng câu `INSERT`
        CÓ PHẠM VI ở bước 5. Chạy riêng thứ Năm thì nó chỉ sinh dòng thứ Năm,
        nên tệp bị ghi đè còn đúng một buổi trong khi nhật ký bước 6 vẫn báo
        `done` kèm đường dẫn. Cơ sở dữ liệu vẫn đủ; chỉ tệp mất các ngày
        trường đã in ra dán bảng — im lặng, và chỉ lấy lại được bằng cách
        chạy lại cả tuần.

        Cùng 5 cột, cùng quy ước "rỗng thay cho NULL" như
        `export_match_results` (rbda_priority_pipeline.py). Thứ tự cũng trùng:
        hàm kia sắp theo `(student_id, thứ tự NGÀY của buổi)`, mà một em chỉ
        có MỘT câu lạc bộ mỗi buổi nên `ORDER BY student_id, buoi COLLATE
        THU_TU_BUOI` cho đúng dãy đó — chạy cả tuần ra tệp y hệt bản trước,
        có test canh. (COLLATE: xem connect_db — Chủ nhật sau thứ Bảy.)
        """
        with self._ket_noi_doc() as cur:
            rows = cur.execute(
                "SELECT student_id, buoi, club_id, matched_tier, "
                "       rank_in_student_pref "
                "FROM match_results ORDER BY student_id, buoi COLLATE THU_TU_BUOI"
            ).fetchall()
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["student_id", "buoi", "club_id", "matched_tier",
                             "rank_in_student_pref"])
            for r in rows:
                writer.writerow([
                    r["student_id"], r["buoi"], r["club_id"] or "",
                    r["matched_tier"] or "", r["rank_in_student_pref"] or "",
                ])

    def run_pipeline(self, seed: int = 42, force_redraw_stb: bool = False,
                     chi_buoi=None):
        """Giữ khoá ghi suốt cả lần chạy — xem `_khoa_ghi` trong __init__.

        Đọc dữ liệu, vẽ số bốc thăm và ghi kết quả phải thấy CÙNG một bản
        dữ liệu; không lời gọi ghi nào khác được chen vào giữa.
        """
        with self._khoa_ghi:
            return self._run_pipeline_da_khoa(seed, force_redraw_stb, chi_buoi)

    def _run_pipeline_da_khoa(self, seed: int = 42, force_redraw_stb: bool = False,
                              chi_buoi=None):
        """
        Nút 'Chạy pipeline' — chạy trọn 5 bước, trả về log từng bước
        để UI hiển thị lên stepper. Log trả về MỘT LẦN khi chạy xong (lời
        gọi pywebview chỉ có một giá trị trả về), không phải từng bước
        theo thời gian thực.

        Quy tắc khoá STB (giải quyết #3 ghi đè âm thầm + #4 khoá STB):
          - Nếu STB CHƯA khoá (lần chạy đầu tiên, hoặc sau khi người
            dùng chủ động mở khoá): vẽ STB cho MỌI học sinh, rồi tự
            động khoá lại ngay sau khi vẽ xong.
          - Nếu STB ĐÃ khoá và force_redraw_stb=False (mặc định): KHÔNG
            vẽ lại — chỉ vẽ bổ sung cho học sinh MỚI (stb_number NULL,
            vd học sinh vừa được thêm qua kiosk sau khi đã khoá), số đã
            có giữ nguyên. Đây là hành vi mặc định khi bấm 'Chạy lại'.
          - Nếu STB đã khoá và force_redraw_stb=True (người dùng xác
            nhận 2 bước trên UI để "vẽ lại"): vẽ lại TOÀN BỘ, ghi log
            unlocked_at của lần khoá cũ rồi khoá lại với thời điểm mới.
          - Mọi lần chạy (kể cả tái sử dụng STB) đều được append vào
            run_history — không bao giờ mất dấu vết lần chạy nào.

        Tính nguyên tử (giải quyết #1 trong kế hoạch kiểm thử mất dữ liệu — artifact, xem BAN_GIAO.md mục 8):
          - Vẽ/khoá STB, ghi match_results, ghi run_meta/run_history đều
            diễn ra trong MỘT connection/transaction duy nhất. Nếu bất kỳ
            bước nào ở giữa ném lỗi (kể cả crash tiến trình được bắt
            bằng try/except ở đây), TOÀN BỘ transaction rollback — kể cả
            số STB vừa vẽ ("full rollback", phương án đã chốt: mọi lần
            gọi lại run_pipeline() sau một crash bắt đầu từ trạng thái
            sạch, không có "khoá STB mồ côi" không đi kèm kết quả nào).
          - Xuất CSV chỉ thực hiện SAU KHI transaction đã commit thành
            công — CSV là sản phẩm phụ, lỗi ghi file không được phép
            khiến DB rơi vào trạng thái dở dang.

        CÁCH BỐC THĂM KHÔNG PHẢI LỰA CHỌN, VÀ HÀM NÀY KHÔNG NHẬN NÓ.
        Phần mềm chạy duy nhất `stb_ngay` — bốc lại thứ tự ở mỗi buổi, dẫn
        xuất tất định từ bộ số ĐÃ KHOÁ cộng với `seed`. Căn cứ là TN7
        (`du_lieu_test/do_boc_tham.py`, 200 seed, ghép cặp, khoảng tin cậy
        bootstrap); hai thiết kế còn lại trong
        `rbda_priority_pipeline.CHE_DO_BOC_THAM` là dụng cụ đo, không có
        đường nào từ đây gọi tới chúng.

        Thêm lại một tham số chế độ vào chữ ký hàm này là mở lại đúng cái
        lựa chọn phép đo đã đóng — có test canh chữ ký
        (tests/test_nhieu_buoi.py::TestMotThietKeDuyNhat).

        Trường chỉ có MỘT buổi thì không đổi gì: `sinh_stb_theo_buoi` ngắn
        mạch về đúng bộ số đã khoá, nên kết quả y hệt bản trước khi có tính
        năng nhiều buổi.

        CHẠY RIÊNG MỘT SỐ BUỔI — `chi_buoi`
        -----------------------------------
        `chi_buoi=None` (mặc định) chạy hết mọi buổi, y như trước.

        Truyền danh sách buổi thì chỉ những buổi đó được tính lại, và
        **kết quả các buổi khác GIỮ NGUYÊN**. Đây là tình huống có thật:
        một câu lạc bộ thứ Năm đổi sức chứa hoặc bị huỷ, cần xếp lại riêng
        thứ Năm mà không đụng tới các ngày đã công bố.

        Ba điều phải giữ, và cả ba đều có test canh:

        1. **Xoá có phạm vi.** Chỉ `DELETE` những dòng `match_results` của
           buổi được chọn. Câu `DELETE FROM match_results` không điều kiện
           của bản trước sẽ xoá sạch kết quả các ngày đã công bố — mất dữ
           liệu, im lặng, và không lấy lại được ngoài bản sao lưu.
        2. **Không vẽ lại số bốc thăm khi chạy một phần.** Vẽ lại là đổi
           thứ tự ưu tiên của MỌI buổi, kể cả những buổi đang giữ kết quả
           cũ — kết quả cũ ấy lập tức không còn giải thích được bằng bộ số
           mới. Bị chặn bằng lỗi, không phải bằng cảnh báo.
        3. **Ghi lại lần chạy này phủ buổi nào** vào `run_meta` và
           `run_history`. Kết quả trong cơ sở dữ liệu giờ có thể là hợp của
           nhiều lần chạy, nên thiếu cột đó là mất khả năng truy nguồn.
        """
        steps_log = []
        conn = None
        try:
            # ---------------- Bước 1/6 · SAO LƯU ----------------
            # Sao lưu hỏng KHÔNG chặn việc chạy — mất bản sao còn hơn
            # mất luôn khả năng phân bổ. Chỉ ghi cảnh báo vào nhật ký.
            try:
                backup_path = self._backup_db()
                steps_log.append({
                    "step": "backup", "status": "done",
                    "detail": err("db_backed_up", backup_name=os.path.basename(backup_path)),
                })
            except Exception as e:
                # Sao luu la luoi an toan, KHONG phai dieu kien tien quyet —
                # loi sao luu khong duoc chan pipeline chay.
                steps_log.append({
                    "step": "backup", "status": "error",
                    "detail": err("db_backup_failed", detail=str(e)),
                })

            # ---------------- Bước 2/6 · KIỂM TRA DỮ LIỆU ----------------
            # Sai ở đây thì dừng hẳn, không vẽ số bốc thăm. Vẽ rồi mới
            # phát hiện dữ liệu hỏng là đã tiêu mất một bộ số.
            steps_log.append({"step": "validate", "status": "running"})
            # Dữ liệu VÀ dấu vân tay của nó lấy trong CÙNG một lần đọc — dấu
            # vân tay ghi lên kết quả ở bước 5 phải là của đúng dữ liệu này.
            (students, clubs, tested_scores, applicants, preferences, _), \
                dau_van_tay = load_from_sqlite_kem_dau_van_tay(self.db_path)
            errors = validate_data_integrity(students, clubs, preferences, applicants)
            if errors:
                steps_log.append({"step": "validate", "status": "error", "detail": errors})
                return _fail_co_buoc(steps_log, errors)
            # Soat danh sach buoi TRUOC khi ve so boc tham. Ve roi moi phat
            # hien tham so sai la da tieu mat mot bo so — cung ly do vi sao
            # buoc kiem tra du lieu nam truoc buoc boc tham.
            # `sap_buoi` chu khong `sorted`: chuoi nay di thang vao cau bao
            # loi `buoi_khong_ton_tai` duoi dang "cac buoi dang co", ma sap
            # theo van cho ra "Ba, Bay, Hai, Nam, Sau, Tu" — dung thu vo
            # nghia ma `_ds_buoi` da bo.
            ds_buoi_tat_ca = sap_buoi(
                {(c.get("buoi") or BUOI_MAC_DINH) for c in clubs.values()})
            if chi_buoi is None:
                chi_buoi_chuan = None
            else:
                # Nhãn đúng như trong CSDL thì giữ nguyên; không thì chuẩn
                # hoá, rồi quy về nhãn CŨ cùng buổi nếu có (CSDL tạo trước
                # khi chuẩn hoá thứ còn nhãn `thứ_3`, xem _khop_buoi_da_co).
                def _chuan(b):
                    if b in ds_buoi_tat_ca:
                        return b
                    ma = self.chuan_hoa_buoi(b) or BUOI_MAC_DINH
                    return next((x for x in ds_buoi_tat_ca
                                 if x == ma or self.chuan_hoa_buoi(x) == ma), ma)
                chi_buoi_chuan = [_chuan(b) for b in chi_buoi]
                la = sorted(set(chi_buoi_chuan) - set(ds_buoi_tat_ca))
                if la:
                    return _fail(err("buoi_khong_ton_tai",
                                     buoi=", ".join(la),
                                     dang_co=", ".join(ds_buoi_tat_ca)))
                if not chi_buoi_chuan:
                    return _fail(err("chua_chon_buoi_nao"))
                if set(chi_buoi_chuan) == set(ds_buoi_tat_ca):
                    chi_buoi_chuan = None        # chon het = chay ca tuan

            # Ve lai so boc tham la doi thu tu uu tien cua MOI buoi, ke ca
            # nhung buoi dang giu ket qua cu. Ket qua cu ay lap tuc khong
            # con giai thich duoc bang bo so moi — hai thu trong cung mot
            # co so du lieu noi hai dieu khac nhau. Chan bang LOI chu khong
            # phai canh bao: day la thu khong sua lai duoc sau khi da chay.
            if chi_buoi_chuan is not None and force_redraw_stb:
                return _fail(err("khong_ve_lai_tham_khi_chay_mot_phan"))

            # DOI HAT GIONG CUNG LA DOI THU TU UU TIEN CUA MOI BUOI.
            #
            # O `seed` tren man hinh sua tu do, va `seed` chinh la thu dan
            # xuat hoan vi rieng cho tung buoi (`sinh_stb_theo_buoi` voi
            # 'stb_ngay'). Chay rieng thu Nam bang mot hat giong khac thi cac
            # buoi VUA DUOC HUA GIU NGUYEN van giu dong ket qua cu, trong khi
            # `run_meta.seed` da bi ghi de — ma `get_so_boc_tham_theo_buoi`
            # dung lai thu tu tung buoi TU CHINH COT DO. Bang so boc tham se
            # khoe mot thu tu chua bao gio xep ai vao dau, va khong ai nhan ra.
            #
            # Dieu kien la CO BUOI DANG DUOC GIU, khong phai "da tung chay":
            # vua xoa sach ket qua thi khong dong nao bi bo lai, chan o do la
            # cam mot viec khong hong gi.
            if chi_buoi_chuan is not None:
                with self._ket_noi_doc() as _cur_doc:
                    dau_hoi = ",".join("?" * len(chi_buoi_chuan))
                    con_giu = _cur_doc.execute(
                        "SELECT COUNT(*) FROM match_results "
                        "WHERE buoi NOT IN (%s)" % dau_hoi,
                        tuple(chi_buoi_chuan),
                    ).fetchone()[0]
                    _meta = _cur_doc.execute(
                        "SELECT seed FROM run_meta WHERE id = 1").fetchone()
                seed_cu = _meta["seed"] if _meta else None
                if con_giu and seed_cu is not None and seed_cu != seed:
                    return _fail(err("khong_doi_hat_giong_khi_chay_mot_phan",
                                     cu=seed_cu, moi=seed))

            # HAT GIONG KHOA CUNG BO SO BOC THAM.
            #
            # Khoa chi giu `stb_number` thi chua du: o truong nhieu buoi, thu
            # tu uu tien cua TUNG buoi la ham cua bo so da khoa VA hat giong
            # (`sinh_stb_theo_buoi`). Do duoc tren `bo_nhieu_buoi`: chay ca
            # tuan bang 42, khoa, roi chay lai bang 43 -> 22/800 dong doi chu,
            # trong khi man hinh van bao "da khoa". Ve lai bo so phai xac nhan
            # hai buoc, con doi hat giong — cung tac dung — thi khong.
            #
            # Mot luat cho moi truong, ke ca truong mot buoi (o do hat giong
            # chi con quyet dinh cho chen em moi): khong bat nguoi van hanh
            # nho truong minh thuoc loai nao moi biet o hat giong co tac dung.
            #
            # Muon doi hat giong thi di duong "ve lai" (`force_redraw_stb`).
            # Khoa ma chua ghi hat giong (NULL: CSDL cu khong co lan chay nao
            # de lay) thi nhan hat giong duoc go — ghi vao khoa o buoc 3.
            if not force_redraw_stb:
                with self._ket_noi_doc() as _cur_doc:
                    _khoa = _cur_doc.execute(
                        "SELECT is_locked, seed FROM stb_lock WHERE id = 1"
                    ).fetchone()
                if (_khoa and _khoa["is_locked"] and _khoa["seed"] is not None
                        and _khoa["seed"] != seed):
                    return _fail(err("hat_giong_da_khoa",
                                     cu=_khoa["seed"], moi=seed))

            steps_log.append({"step": "validate", "status": "done"})

            # ---------------- Bước 3/6 · SỐ BỐC THĂM ----------------
            # Ba nhánh: chưa khoá -> vẽ toàn bộ rồi khoá; đã khoá + có em
            # mới -> chèn ngẫu nhiên (giữ thứ tự tương đối em cũ); đã
            # khoá + không em mới -> dùng lại nguyên bộ số.
            steps_log.append({"step": "stb_lottery", "status": "running"})
            conn = connect_db(self.db_path)
            cur = conn.cursor()
            lock_row = cur.execute(
                "SELECT is_locked FROM stb_lock WHERE id = 1"
            ).fetchone()
            already_locked = bool(lock_row[0]) if lock_row else False
            stb_redrawn = False

            if not already_locked or force_redraw_stb:
                # Ve lai TOAN BO
                stb_lottery_new = generate_stb_lottery(list(students.keys()), seed=seed)
                conn.executemany(
                    "UPDATE students SET stb_number = ? WHERE student_id = ?",
                    [(v, k) for k, v in stb_lottery_new.items()],
                )
                if already_locked and force_redraw_stb:
                    cur.execute(
                        "UPDATE stb_lock SET unlocked_at = ? WHERE id = 1", (_now(),)
                    )
                cur.execute(
                    "UPDATE stb_lock SET is_locked = 1, locked_at = ?, seed = ? "
                    "WHERE id = 1",
                    (_now(), seed),
                )
                stb_redrawn = True
                stb_step_detail = err("stb_redrawn_and_locked", n=len(stb_lottery_new))
                for sid, v in stb_lottery_new.items():
                    students[sid]["stb"] = v
            else:
                # Khoa tu CSDL cu ma chua co hat giong nao de doi chieu: hat
                # giong cua lan nay tro thanh hat giong cua khoa. Chung mot
                # giao dich, nen lan chay nay hong thi ghi nay cung bi huy.
                cur.execute(
                    "UPDATE stb_lock SET seed = ? WHERE id = 1 AND seed IS NULL",
                    (seed,),
                )
                # Da khoa: chi ve bo sung cho hoc sinh moi (stb_number con NULL)
                missing = [
                    sid for sid, info in students.items() if info.get("stb") is None
                ]
                if missing and chi_buoi_chuan is not None:
                    # CHEN SO CHO EM MOI CUNG DOI THU TU CUA MOI BUOI.
                    #
                    # Chu thich ben duoi noi chi so tuyet doi "khong ai nhin
                    # thay" — dung voi man hinh, SAI voi thuat toan: chinh
                    # chi so do la dau vao cua `sinh_stb_theo_buoi`, ham sinh
                    # hoan vi rieng cho tung buoi. Danh lai so la doi thu tu
                    # cua MOI buoi, ke ca buoi vua hua giu nguyen.
                    #
                    # Do duoc tren bo 6 buoi: them mot em roi chay rieng thu
                    # Nam -> 17/180 so doi, va 27 tren 900 o giu lai KHONG
                    # con tai lap duoc tu bo so da khoa cong hat giong. Loi
                    # hua "ai cung tinh lai duoc" gay o dung do.
                    #
                    # Chan y nhu `force_redraw_stb` ngay phia tren, va vi
                    # dung mot ly do.
                    return _fail(err("khong_chen_tham_khi_chay_mot_phan",
                                     n=len(missing)))
                if missing:
                    # CHEN NGAU NHIEN, khong noi duoi. Ban dau cho em moi
                    # so MAX(stb)+1 "de tranh trung" — ma so nho = uu tien
                    # cao, nen cach do dat em moi sau MOI em cu, o MOI CLB,
                    # vinh vien. Do duoc: 20 em cu + 10 em moi tranh 10 suat
                    # -> em moi duoc 0 suat. Xem chen_stb_cho_hoc_sinh_moi.
                    #
                    # Thu tu TUONG DOI cua em cu van giu nguyen tuyet doi;
                    # chi so tuyet doi bi danh lai, ma so do khong ai nhin
                    # thay (khong hien tren giao dien, khong nam trong tep
                    # xuat, man cham diem co y giau).
                    thu_tu_cu = [
                        r[0] for r in cur.execute(
                            "SELECT student_id FROM students "
                            "WHERE stb_number IS NOT NULL ORDER BY stb_number"
                        ).fetchall()
                    ]
                    bo_so_moi = chen_stb_cho_hoc_sinh_moi(thu_tu_cu, missing, seed=seed)
                    conn.executemany(
                        "UPDATE students SET stb_number = ? WHERE student_id = ?",
                        [(v, k) for k, v in bo_so_moi.items()],
                    )
                    stb_step_detail = err("stb_supplemented", n=len(missing))
                    for sid, v in bo_so_moi.items():
                        students[sid]["stb"] = v
                else:
                    stb_step_detail = err("stb_reused")
            steps_log.append({"step": "stb_lottery", "status": "done", "detail": stb_step_detail})

            # Khong mo connection moi de doc lai stb_number: cac thay doi
            # o tren CHUA commit, mot connection khac se khong thay duoc
            # (va se pha vo tinh nguyen tu). Cap nhat truc tiep vao dict
            # students trong bo nho (da lam o hai nhanh phia tren) roi
            # dung lai cho RB-DA — tuong duong voi doc lai tu DB nhung
            # van nam trong CUNG MOT transaction.
            stb_lottery = {sid: info["stb"] for sid, info in students.items()}

            # ---------------- Bước 4/6 · CHẠY THUẬT TOÁN ----------------
            # Chạy xong PHẢI qua hai chốt (sanity + ổn định) rồi mới được
            # ghi. Hỏng một trong hai là rollback toàn bộ giao dịch.
            steps_log.append({"step": "rbda_cascade", "status": "running"})
            reserve_fn = default_reserve_eligible_fn(students, clubs)
            # Mot buoi hay nhieu buoi deu di qua DUNG mot duong nay: voi du
            # lieu mot buoi, run_rbda_nhieu_buoi goi run_rbda dung mot lan
            # voi dung du lieu do. Co test canh su trung khit ay tren ba bo
            # du lieu x 20 seed (tests/test_nhieu_buoi.py).
            result = run_rbda_nhieu_buoi(
                students, clubs, tested_scores, applicants, preferences,
                stb_lottery, is_reserve_eligible_fn=reserve_fn,
                che_do_boc_tham=CHE_DO_BOC_THAM_MAC_DINH, seed=seed,
                chi_buoi=chi_buoi_chuan,
            )
            sanity_problems = []
            stability_problems = []
            _nhom = nhom_theo_buoi(clubs)   # một lần, không phải mỗi buổi
            for _buoi, _kq in result.per_buoi.items():
                _clubs_b, _, _, _prefs_b = cat_du_lieu_theo_buoi(
                    _buoi, _nhom[_buoi], clubs,
                    tested_scores, applicants, preferences)
                sanity_problems += sanity_check_result(_kq, _clubs_b, _prefs_b)
                stability_problems += verify_stability(
                    _kq, _clubs_b, _prefs_b, reserve_fn)
            if sanity_problems or stability_problems:
                steps_log.append({
                    "step": "rbda_cascade", "status": "error",
                    "detail": sanity_problems + stability_problems,
                })
                conn.rollback()
                conn.close()
                conn = None
                steps_log.append({"step": "rollback", "status": "done", "detail": err("pipeline_rolled_back")})
                return _fail_co_buoc(steps_log, sanity_problems + stability_problems)
            steps_log.append({
                "step": "rbda_cascade", "status": "done",
                "detail": err("rbda_done", rounds=result.rounds_run),
            })

            # ---------------- Bước 5/6 · GHI KẾT QUẢ ----------------
            steps_log.append({"step": "write_results", "status": "running"})
            # CHUP KET QUA CU truoc moi lenh xoa ben duoi — nguon cua tep "thay
            # doi so voi lan chay truoc" (`get_thay_doi_ket_qua`). Cung giao
            # dich: chay hong thi rollback ca ban chup, ban chup cu con nguyen.
            # Chup ca bang (ke ca khi chay mot phan): so sanh la giua HAI
            # trang thai cua bang ket qua, khong phai giua hai lan tinh.
            _meta_cu = cur.execute(
                "SELECT run_at FROM run_meta WHERE id = 1").fetchone()
            cur.execute("DELETE FROM ket_qua_truoc")
            cur.execute(
                "INSERT INTO ket_qua_truoc (student_id, buoi, club_id, round_num, "
                " matched_tier, rank_in_student_pref, run_at) "
                "SELECT student_id, buoi, club_id, round_num, matched_tier, "
                " rank_in_student_pref, ? FROM match_results",
                (_meta_cu[0] if _meta_cu else None,),
            )
            # DAU VAN TAY du lieu ma lan chay nay dung — `dau_van_tay` lay o
            # buoc 2, CUNG lan doc voi du lieu. KHONG tinh lai o day: mot lan
            # luu tu kiosk giua buoc 2 va buoc nay se lot vao dau van tay ma
            # khong vao ket qua (loi do /code-review tim ra).
            # Chay CA TUAN: ket qua moi buoi vua tinh tu du lieu nay -> ghi.
            # Chay MOT PHAN: cac buoi khong chay van la ket qua cu; chi ghi khi
            # du lieu CHUA doi tu lan ghi truoc (tuc ket qua cu cung da tinh tu
            # chinh du lieu nay), neu khong canh bao "ket qua co the da cu"
            # phai con.
            _dvt_cu = cur.execute(
                "SELECT dau_van_tay FROM dau_van_tay_chay WHERE id = 1").fetchone()
            if chi_buoi_chuan is None:
                _ghi_dvt = True
            else:
                # Khong con dong nao cua buoi KHONG chay -> ca bang ket qua
                # deu sap tinh tu du lieu nay, cung sach nhu chay ca tuan.
                _con_giu = cur.execute(
                    "SELECT COUNT(*) FROM match_results WHERE buoi NOT IN (%s)"
                    % ",".join("?" * len(chi_buoi_chuan)),
                    tuple(chi_buoi_chuan)).fetchone()[0]
                _ghi_dvt = (not _con_giu) or bool(
                    _dvt_cu and _dvt_cu[0] == dau_van_tay)
            if _ghi_dvt:
                cur.execute(
                    "INSERT INTO dau_van_tay_chay (id, dau_van_tay, luc) VALUES (1, ?, ?) "
                    "ON CONFLICT(id) DO UPDATE SET dau_van_tay = excluded.dau_van_tay, "
                    "luc = excluded.luc",
                    (dau_van_tay, _now()),
                )
            # QUET DONG MO COI TRUOC. Mot buoi ma KHONG CLB NAO con sinh
            # hoat thi khong ket qua nao duoc phep ton tai o do.
            #
            # Truong doi lich — chuyen moi CLB thu Sau sang thu Nam — thi
            # `result.ds_buoi` khong con ten "thu_6", nen lenh xoa co pham
            # vi ben duoi khong cham toi dong nao cua buoi do. Do duoc: 180
            # dong thu_6 song sot qua mot lan chay LAI CA TUAN, va vi
            # `get_club_fill_stats` noi theo club_id khong kem dieu kien
            # buoi, bang lap day bao clb_bongro 40/20 cho, clb_lamvuon
            # 36/18. Ban cu xoa vo dieu kien KHONG the gay ra chuyen nay.
            #
            # Quet o MOI lan chay, ke ca chay mot phan: mot buoi da bien mat
            # khong phai "buoi khong chon" — no khong con ton tai, nen loi
            # hua giu nguyen khong ap cho no.
            cur.execute(
                "DELETE FROM match_results WHERE buoi NOT IN "
                "(SELECT DISTINCT COALESCE(NULLIF(buoi, ''), ?) FROM clubs)",
                (BUOI_MAC_DINH,),
            )
            # QUET THEO CAP (CLB, BUOI). Cau quet ben tren bat theo TEN
            # BUOI, nen no chi don duoc khi mot buoi bien mat HAN. Truong
            # doi lich cho DUNG MOT cau lac bo — chuyen no tu thu Sau sang
            # thu Ba trong khi cac CLB khac van o thu Sau — thi ten "thu_6"
            # con nguyen, va dong cu cua CLB vua doi khong ai cham toi.
            #
            # Chay CA TUAN thi lenh xoa co pham vi ben duoi don duoc, vi
            # "thu_6" nam trong `result.ds_buoi`. Chay MOT PHAN khong gom
            # thu Sau thi khong. Do duoc tren bo 6 buoi: doi clb_tinhnguyen
            # sang thu Ba roi chay rieng thu Ba -> 22 dong thu_6 song sot,
            # CLB do co 44 dong cho 22 cho, va bang lap day bao 44/22 vi
            # `get_club_fill_stats` noi theo club_id khong kem dieu kien buoi.
            #
            # Ly le y het cau quet ben tren, chi hep hon mot bac: mot buoi
            # da bien mat khong phai "buoi khong chon", va mot cau lac bo da
            # doi buoi thi dong cu KHONG CON la ket qua cua ngay ay nua. No
            # mo ta mot viec khong the xay ra.
            #
            # Chi cham dong CO cau lac bo. Dong `club_id IS NULL` la "em nay
            # khong duoc suat nao buoi do" — mot CLB doi di noi khac khong
            # lam cau do sai, nen de nguyen.
            #
            # Sau khi quet, em do khong con dong nao cho thu Sau, tuc hien ra
            # la chua duoc xep ngay do cho toi khi thu Sau duoc chay lai. Do
            # la trang thai DUNG SU THAT, va la lua chon duy nhat trung thuc:
            # dung mot dong trong thay the la bia ra mot ket qua chua he tinh.
            cur.execute(
                "DELETE FROM match_results WHERE club_id IS NOT NULL "
                "AND NOT EXISTS ("
                "  SELECT 1 FROM clubs c "
                "  WHERE c.club_id = match_results.club_id "
                "    AND COALESCE(NULLIF(c.buoi, ''), ?) = match_results.buoi)",
                (BUOI_MAC_DINH,),
            )
            # XOA CO PHAM VI. `DELETE FROM match_results` khong dieu kien se
            # xoa sach ket qua cac buoi KHONG chay trong lan nay — cac buoi
            # ma truong co the da in ra dan bang. Mat du lieu, im lang, va
            # chi lay lai duoc tu ban sao luu.
            cur.executemany(
                "DELETE FROM match_results WHERE buoi = ?",
                [(b,) for b in result.ds_buoi],
            )
            cur.executemany(
                "INSERT INTO match_results "
                "(student_id, buoi, club_id, round_num, matched_tier, rank_in_student_pref) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                cac_dong_match_results(result),
            )
            steps_log.append({"step": "write_results", "status": "done"})

            # "Da duoc xep" = co it nhat MOT CLB trong tuan. Mot em co CLB
            # thu 3 nhung trong thu 5 van la da duoc xep — cho trong buoi
            # nao thi doc o bang do phu, khong doc o con so nay.
            #
            # Dem lai tu CO SO DU LIEU chu khong tu `result`. Chay mot phan
            # thi `result` chi chua nhung buoi vua chay, nen dem theo no se
            # bao it hon su that: mot em da co CLB thu Hai tu lan chay truoc
            # van dang duoc xep, du lan nay chi chay thu Nam. Con so tren
            # bang dieu khien phai noi ve CO SO DU LIEU, khong phai ve lan
            # chay vua roi.
            n_matched = cur.execute(
                "SELECT COUNT(DISTINCT student_id) FROM match_results "
                "WHERE club_id IS NOT NULL"
            ).fetchone()[0]
            so_clb = result.so_clb_moi_em()
            run_at = _now()
            buoi_da_chay = ",".join(result.ds_buoi)

            cur.execute(
                "INSERT INTO run_meta "
                "(id, seed, run_at, rounds_run, n_matched, n_total, che_do_boc_tham, "
                " so_buoi, buoi_da_chay) "
                "VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET seed=excluded.seed, run_at=excluded.run_at, "
                "rounds_run=excluded.rounds_run, n_matched=excluded.n_matched, "
                "n_total=excluded.n_total, che_do_boc_tham=excluded.che_do_boc_tham, "
                "so_buoi=excluded.so_buoi, buoi_da_chay=excluded.buoi_da_chay",
                (seed, run_at, result.rounds_run, n_matched, len(so_clb),
                 result.che_do_boc_tham, len(result.ds_buoi), buoi_da_chay),
            )
            # Ghi che_do_boc_tham lay tu chinh KET QUA chu khong tu hang so:
            # cot nay la DAU VET KIEM TOAN, no phai noi dung cach ma lan chay
            # nay da dung. Lay tu hang so thi hai thu troi khoi nhau ma khong
            # co gi bao — va `get_so_boc_tham_theo_buoi` doc lai chinh cot nay
            # de dung lai thu tu tung buoi, nen mot gia tri sai o day lam bang
            # so boc tham hien ra mot thu tu chua bao gio duoc dung.
            #
            # Dong cu ghi 'stb_tuan' (chay bang ban truoc khi chot mot thiet ke)
            # KHONG BAO GIO duoc sua lai.
            #
            # run_history: KHONG BAO GIO ghi de — moi lan chay them 1 dong moi,
            # de nguoi dung luon xem lai duoc lich su chay pipeline (giai quyet #3).
            cur.execute(
                "INSERT INTO run_history "
                "(seed, run_at, rounds_run, n_matched, n_total, stb_redrawn, "
                " che_do_boc_tham, so_buoi, buoi_da_chay) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (seed, run_at, result.rounds_run, n_matched, len(so_clb),
                 1 if stb_redrawn else 0, result.che_do_boc_tham,
                 len(result.ds_buoi), buoi_da_chay),
            )

            # Diem commit DUY NHAT cua toan bo pipeline: neu bat ky dong
            # nao o tren (ve STB, ghi ket qua, ghi run_meta/run_history)
            # nem exception, khoi except ben duoi se rollback() thay vi
            # chay den day — STB vua ve cung bi huy theo (full rollback).
            conn.commit()
            conn.close()
            conn = None

            # Xuat CSV CHI xay ra SAU KHI DB da commit thanh cong.
            # ---------------- Bước 6/6 · XUẤT TỆP ----------------
            # Xuất hỏng KHÔNG được huỷ kết quả đã ghi — người dùng xuất
            # lại được bằng nút riêng.
            steps_log.append({"step": "export", "status": "running"})
            export_path = os.path.join(os.path.dirname(self.db_path), "match_results.csv")
            try:
                # Doc tu CSDL chu khong tu `result` — xem
                # `_xuat_match_results_csv`. Chay mot phan ma xuat tu `result`
                # la ghi de tep bang dung nhung buoi vua chay.
                self._xuat_match_results_csv(export_path)
                steps_log.append({"step": "export", "status": "done", "detail": export_path})
            except Exception as e:
                steps_log.append({
                    "step": "export", "status": "error",
                    "detail": err("error_exporting_csv", detail=str(e)),
                })
                export_path = None

            return _ok({
                "steps": steps_log,
                "n_matched": n_matched,
                "n_total": len(result.assignment),
                "rounds_run": result.rounds_run,
                "export_path": export_path,
                "stb_redrawn": stb_redrawn,
            })
        except BaseException as e:
            # BaseException (khong chi Exception): KeyboardInterrupt/
            # SystemExit KHONG ke thua tu Exception, nhung mot "crash
            # giua chung" phai duoc rollback du no la loai nao — full
            # rollback (Option A) khong duoc phep chi ap dung cho mot
            # so loai loi. Sau khi don dep xong, neu day la tin hieu
            # dieu khien tien trinh (Ctrl+C, thoat) thi PHAI nem lai
            # (raise) thay vi nuot thanh {ok: False} nhu mot loi
            # nghiep vu binh thuong.
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
                conn.close()
                conn = None
                steps_log.append({"step": "rollback", "status": "done", "detail": err("pipeline_rolled_back")})
            if not isinstance(e, Exception):
                raise
            error_entry = err("error_running_pipeline", detail=str(e))
            steps_log.append({"step": "unknown", "status": "error", "detail": error_entry})
            return _fail_co_buoc(steps_log, self._loi_co_ghi_vet(error_entry))
        finally:
            # Hai khoi tren KHONG du. `except` chi chay khi co exception, ma
            # ham nay con `return _fail(...)` o giua — vd khi tu choi chen so
            # boc tham luc chay mot phan — va nhung duong do roi ra ngoai voi
            # ket noi CON MO. Tren Windows do la mot the giu `app.db`, du
            # khong dong nao bi ghi.
            #
            # Duong thanh cong da gan `conn = None` truoc khi `return`, va
            # khoi `except` cung vua gan, nen `finally` chi cham vao nhung
            # duong thoat con bo lai ket noi that.
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
                conn.close()
