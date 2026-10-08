"""Các bảng của thẻ Kết quả: lấp đầy, tải theo buổi, thời khoá biểu,
độ phủ, nguyện vọng, dự trữ, số bốc thăm.

Một phần của PipelineAPI (xem api.py) — tách riêng cho dễ đọc; mọi hàm
public ở đây vẫn là hàm của PipelineAPI và giao diện gọi được như cũ.
"""

from api_chung import (
    _nho_trong_luc_xuat,
)
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import (
    BUOI_MAC_DINH,
    CHE_DO_BOC_THAM_MAC_DINH,
    sap_buoi,
    sinh_stb_theo_buoi,
    so_thu_trong_tuan,
)


class BaoCaoMixin:
    # -----------------------------------------------------------------
    # TAB "KẾT QUẢ"
    # -----------------------------------------------------------------

    def get_match_results(self, search: str = ""):
        """Bảng kết quả, lọc theo student_id/name nếu search có giá trị."""
        try:
            with self._ket_noi_doc() as cur:
                query = """
                    SELECT m.student_id, s.name, m.buoi, m.club_id,
                           c.name as club_name, m.matched_tier,
                           m.rank_in_student_pref
                    FROM match_results m
                    JOIN students s ON s.student_id = m.student_id
                    LEFT JOIN clubs c ON c.club_id = m.club_id
                """
                params = ()
                if search:
                    query += " WHERE khop_tim(m.student_id, ?) OR khop_tim(s.name, ?)"
                    params = (search, search)
                query += " ORDER BY m.student_id, m.buoi COLLATE THU_TU_BUOI"
                rows = cur.execute(query, params).fetchall()
            return _ok([dict(r) for r in rows])
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))

    @_nho_trong_luc_xuat
    def get_club_fill_stats(self):
        """Tỉ lệ lấp đầy mỗi club — dùng vẽ thanh progress bar."""
        try:
            with self._ket_noi_doc() as cur:
                # matched_reserve: SỐ EM THỰC SỰ VÀO BẰNG SUẤT DỰ TRỮ — khác
                # với reserve_capacity là chỉ tiêu dự trữ của CLB. Biểu đồ
                # trước đây vẽ theo chỉ tiêu, tức là vẽ một thuộc tính của
                # CLB chứ không phải điều đã xảy ra. Dữ liệu vốn có sẵn ở
                # match_results.matched_tier, chỉ là câu lệnh chưa lấy.
                # PHIA CAU, khong chi phia cung. Thanh lap day noi "16/16"
                # giong het nhau cho mot CLB 18 em dang ky va mot CLB 90 em
                # dang ky — hai bai toan khac han voi nha truong.
                #
                # `hang_trong_buoi` PHAI tinh lai bang ham cua so. Cot
                # preferences.rank la so 1..n CHAY SUOT qua cac buoi noi
                # lien nhau (xem chu thich o import_preferences_csv), nen
                # `WHERE rank = 1` chi bat duoc nguyen vong dau tien cua ca
                # tuan. Da do tren bo 160 em / 5 buoi: cach do bao thu Nam
                # va thu Sau co 0 em dat nguyen vong 1, trong khi that ra la
                # 121 va 57. Mot con so sai am tham, khong gi tren man hinh
                # cho thay no sai.
                rows = cur.execute("""
                    WITH hang AS (
                        SELECT p.club_id,
                               ROW_NUMBER() OVER (
                                   PARTITION BY p.student_id, COALESCE(c.buoi, ?)
                                   ORDER BY p.rank
                               ) AS hang_trong_buoi
                        FROM preferences p
                        JOIN clubs c ON c.club_id = p.club_id
                    ),
                    nhu_cau AS (
                        SELECT club_id,
                               COUNT(*) AS so_dang_ky,
                               SUM(CASE WHEN hang_trong_buoi = 1 THEN 1 ELSE 0 END)
                                   AS so_dat_nv1
                        FROM hang GROUP BY club_id
                    )
                    SELECT c.club_id, c.name, c.capacity, c.reserve_capacity,
                           COALESCE(c.buoi, ?) AS buoi,
                           COUNT(m.student_id) as matched,
                           SUM(CASE WHEN m.matched_tier = 'reserve' THEN 1 ELSE 0 END)
                               AS matched_reserve,
                           COALESCE(n.so_dang_ky, 0) AS so_dang_ky,
                           COALESCE(n.so_dat_nv1, 0) AS so_dat_nv1
                    FROM clubs c
                    LEFT JOIN match_results m ON m.club_id = c.club_id
                    LEFT JOIN nhu_cau n ON n.club_id = c.club_id
                    GROUP BY c.club_id
                    ORDER BY buoi COLLATE THU_TU_BUOI, c.club_id
                """, (BUOI_MAC_DINH, BUOI_MAC_DINH)).fetchall()

            ra = []
            for r in rows:
                d = dict(r)
                suc = d.get("capacity") or 0
                # Khong co chi tieu thi de None chu khong phai 0 — "khong co
                # cho" khac han "thua cho", va 0 o cot nay doc ra nghia
                # nguoc hang.
                d["ti_le_choi"] = (
                    round(d["so_dang_ky"] / suc, 2) if suc else None)
                ra.append(d)
            return _ok(ra)
        except Exception as e:
            return _fail(err("error_reading_club_stats", detail=str(e)))

    # -----------------------------------------------------------------
    # NHIỀU BUỔI SINH HOẠT
    # -----------------------------------------------------------------

    def _ds_buoi(self, cur) -> list[str]:
        """Danh sách buổi đang có CLB, sắp theo THỨ TỰ NGÀY. Rỗng CLB -> rỗng.

        Sắp trong Python chứ không bằng `ORDER BY` của SQL: thứ tự ngày
        trong tuần không phải thứ tự vần chữ cái, mà SQLite thì không biết
        "Thứ Hai" đứng trước "Thứ Ba". Sắp theo vần ở đây từng cho ra Ba,
        Bảy, Hai, Năm, Sáu, Tư — vô nghĩa trên màn hình, và sai hẳn với
        tính năng chọn KHOẢNG buổi.
        """
        return sap_buoi(
            r[0] for r in cur.execute(
                "SELECT DISTINCT COALESCE(buoi, ?) AS b FROM clubs",
                (BUOI_MAC_DINH,),
            )
        )

    def get_danh_sach_buoi(self):
        """Các buổi sinh hoạt đang dùng, kèm cờ cho biết trường có dùng nhiều buổi không.

        Giao diện đọc `nhieu_buoi` để quyết định hiện hay ẩn toàn bộ phần
        nhiều buổi. Trường chưa khai buổi nào thì màn hình phải trông y
        hệt bản cũ — không ai bị bắt học một khái niệm mình chưa dùng.
        """
        try:
            with self._ket_noi_doc() as cur:
                ds = self._ds_buoi(cur)
            return _ok({
                "ds_buoi": ds,
                "nhieu_buoi": len(ds) > 1,
                "buoi_mac_dinh": BUOI_MAC_DINH,
                # Thứ mấy trong tuần, hoặc null nếu nhãn không nhận ra
                # được. Giao diện dùng để nhóm và để bộ chọn khoảng biết
                # đâu là "liền kề".
                "thu_trong_tuan": {b: so_thu_trong_tuan(b) for b in ds},
            })
        except Exception as e:
            return _fail(err("error_reading_club_list", detail=str(e)))

    @_nho_trong_luc_xuat
    def get_tai_theo_buoi(self):
        """Mỗi buổi có bao nhiêu chỗ, bao nhiêu lượt nguyện vọng, tỉ lệ chọi.

        Đọc TRƯỚC khi chạy phân bổ. Đây là bảng sửa được vấn đề thay vì
        phải giải thích nó: thấy thứ 3 chọi 3,1 lần trong khi thứ 6 mới
        0,4 lần thì dời một câu lạc bộ đông sang thứ 6, chứ không phải
        chạy xong rồi mới đi trả lời vì sao nhiều em trượt.
        """
        try:
            with self._ket_noi_doc() as cur:
                rows = cur.execute("""
                    SELECT COALESCE(c.buoi, ?) AS buoi,
                           COUNT(DISTINCT c.club_id) AS so_clb,
                           COALESCE(SUM(c.capacity), 0) AS tong_cho,
                           COALESCE(SUM(c.reserve_capacity), 0) AS tong_du_tru
                    FROM clubs c
                    GROUP BY buoi
                    ORDER BY buoi COLLATE THU_TU_BUOI
                """, (BUOI_MAC_DINH,)).fetchall()

                nv = dict(cur.execute("""
                    SELECT COALESCE(c.buoi, ?) AS buoi, COUNT(*) AS n
                    FROM preferences p
                    JOIN clubs c ON c.club_id = p.club_id
                    GROUP BY buoi
                """, (BUOI_MAC_DINH,)).fetchall())

                em = dict(cur.execute("""
                    SELECT COALESCE(c.buoi, ?) AS buoi,
                           COUNT(DISTINCT p.student_id) AS n
                    FROM preferences p
                    JOIN clubs c ON c.club_id = p.club_id
                    GROUP BY buoi
                """, (BUOI_MAC_DINH,)).fetchall())

            ra = []
            for r in rows:
                tong_cho = r["tong_cho"] or 0
                so_nv = nv.get(r["buoi"], 0)
                ra.append({
                    "buoi": r["buoi"],
                    "so_clb": r["so_clb"],
                    "tong_cho": tong_cho,
                    "tong_du_tru": r["tong_du_tru"] or 0,
                    "so_nguyen_vong": so_nv,
                    "so_hoc_sinh": em.get(r["buoi"], 0),
                    # Tỉ lệ chọi = SỐ HỌC SINH muốn buổi này / số chỗ.
                    #
                    # Mẫu số là số HỌC SINH chứ không phải số lượt nguyện
                    # vọng, vì mỗi em chỉ lấy được MỘT chỗ trong một buổi.
                    # Đếm theo lượt thì một em khai cả ba câu lạc bộ của
                    # buổi đó bị tính thành ba người đi tranh — con số phồng
                    # lên và mọi buổi trông như nhau, đúng lúc cần nó phân
                    # biệt buổi chật với buổi rộng.
                    #
                    # Không chỗ nào thì để None chứ không phải 0 — "không có
                    # chỗ" khác hẳn "thừa chỗ", và 0 ở cột này đọc ra nghĩa
                    # ngược hẳn.
                    "ti_le_choi": (
                        round(em.get(r["buoi"], 0) / tong_cho, 2) if tong_cho else None
                    ),
                })
            return _ok(ra)
        except Exception as e:
            return _fail(err("error_reading_club_stats", detail=str(e)))

    def get_thoi_khoa_bieu(self, search: str = ""):
        """Thời khoá biểu tuần: mỗi em một dòng, mỗi buổi một ô.

        Đây là sản phẩm chính của bản nhiều buổi — thứ nhà trường in ra
        dán bảng và phát cho học sinh.
        """
        try:
            with self._ket_noi_doc() as cur:
                ds_buoi = self._ds_buoi(cur)
                query = """
                    SELECT m.student_id, s.name, m.buoi, m.club_id,
                           c.name AS club_name, m.matched_tier,
                           m.rank_in_student_pref
                    FROM match_results m
                    JOIN students s ON s.student_id = m.student_id
                    LEFT JOIN clubs c ON c.club_id = m.club_id
                """
                params = ()
                if search:
                    query += " WHERE khop_tim(m.student_id, ?) OR khop_tim(s.name, ?)"
                    params = (search, search)
                rows = cur.execute(query + " ORDER BY m.student_id, m.buoi COLLATE THU_TU_BUOI",
                                   params).fetchall()

            theo_em: dict = {}
            for r in rows:
                em = theo_em.setdefault(r["student_id"], {
                    "student_id": r["student_id"],
                    "name": r["name"],
                    "theo_buoi": {},
                    "so_clb": 0,
                    "so_nv1": 0,
                })
                em["theo_buoi"][r["buoi"]] = {
                    "club_id": r["club_id"],
                    "club_name": r["club_name"],
                    "matched_tier": r["matched_tier"],
                    "rank_in_student_pref": r["rank_in_student_pref"],
                }
                if r["club_id"]:
                    em["so_clb"] += 1
                    if r["rank_in_student_pref"] == 1:
                        em["so_nv1"] += 1

            return _ok({
                "ds_buoi": ds_buoi,
                "hoc_sinh": [theo_em[k] for k in sorted(theo_em)],
            })
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))

    @_nho_trong_luc_xuat
    def get_do_phu(self):
        """Độ phủ: bao nhiêu em được mấy CLB, và em nào trắng tay cả tuần.

        Con số đáng nhìn nhất ở đây là SỐ EM KHÔNG CÓ CLB NÀO CẢ TUẦN.
        Với một buổi thì nó trùng với "số em chưa được xếp" quen thuộc;
        với nhiều buổi nó là thứ khác hẳn, và là thứ dễ bị bỏ sót nhất khi
        chỉ nhìn tỉ lệ lấp đầy từng câu lạc bộ.
        """
        try:
            with self._ket_noi_doc() as cur:
                ds_buoi = self._ds_buoi(cur)
                rows = cur.execute("""
                    SELECT m.student_id, s.name,
                           SUM(CASE WHEN m.club_id IS NOT NULL THEN 1 ELSE 0 END) AS so_clb
                    FROM match_results m
                    JOIN students s ON s.student_id = m.student_id
                    GROUP BY m.student_id
                    ORDER BY so_clb, m.student_id
                """).fetchall()

            phan_bo: dict[int, int] = {}
            trang_tay = []
            for r in rows:
                n = int(r["so_clb"] or 0)
                phan_bo[n] = phan_bo.get(n, 0) + 1
                if n == 0:
                    trang_tay.append({"student_id": r["student_id"], "name": r["name"]})

            tong = len(rows)
            return _ok({
                "ds_buoi": ds_buoi,
                "tong_hoc_sinh": tong,
                "phan_bo": [
                    {"so_clb": n, "so_em": phan_bo.get(n, 0)}
                    for n in range(0, len(ds_buoi) + 1)
                ],
                "so_em_trang_tay": len(trang_tay),
                "em_trang_tay": trang_tay[:200],
                "trung_binh_clb": (
                    round(sum(int(r["so_clb"] or 0) for r in rows) / tong, 2)
                    if tong else 0
                ),
            })
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))

    def get_danh_sach_clb(self, club_id: str):
        """Danh sách thành viên của MỘT câu lạc bộ.

        VÌ SAO HÀM NÀY PHẢI CÓ. Cả phần mềm chỉ trả lời được một chiều —
        *em này vào câu lạc bộ nào*. Chiều ngược lại, *câu lạc bộ này có
        những em nào*, đã được xuất ra tệp từ lâu (`export_csv` dựng thư
        mục `..._theo_club/`) nhưng không có đường nào lên màn hình, nên
        cách duy nhất để xem là bấm Xuất rồi mở từng tệp một. Mà đây đúng
        là tờ giấy nhà trường dùng nhiều nhất sau khi chạy: mỗi thầy cô
        phụ trách một bản.

        KHÔNG dùng `get_club_applicants_for_scoring` cho việc này —
        hàm đó cố ý giấu thứ hạng nguyện vọng để chấm mù, và thẻ 05 phải
        giữ nguyên là chấm mù.
        """
        try:
            with self._ket_noi_doc() as cur:
                clb = cur.execute(
                    "SELECT club_id, name, capacity, reserve_capacity, "
                    "       COALESCE(buoi, ?) AS buoi "
                    "FROM clubs WHERE club_id = ?",
                    (BUOI_MAC_DINH, club_id),
                ).fetchone()
                if not clb:
                    return _fail(err("club_not_found", club_id=club_id))
                rows = cur.execute("""
                    SELECT m.student_id, s.name, m.buoi,
                           m.rank_in_student_pref, m.matched_tier,
                           s.reserve_group
                    FROM match_results m
                    LEFT JOIN students s ON s.student_id = m.student_id
                    WHERE m.club_id = ?
                    ORDER BY s.name, m.student_id
                """, (club_id,)).fetchall()
            return _ok({
                "club_id": clb["club_id"],
                "club_name": clb["name"],
                "buoi": clb["buoi"],
                "capacity": clb["capacity"],
                "thanh_vien": [dict(r) for r in rows],
            })
        except Exception as e:
            return _fail(err("error_reading_club_roster", detail=str(e)))

    @_nho_trong_luc_xuat
    def get_phan_bo_nguyen_vong(self):
        """Bao nhiêu em được nguyện vọng 1, 2, 3, 4 trở lên.

        VÌ SAO CON SỐ NÀY PHẢI CÓ. Độ phủ nói *bao nhiêu em có chỗ*, không
        nói *chỗ ấy có phải thứ em muốn không*. Một lần chạy 90% em được
        nguyện vọng 1 và một lần phần lớn em được nguyện vọng 4 cho ra
        cùng một con số độ phủ, cùng một tỉ lệ lấp đầy, cùng một bảng kết
        quả về hình dạng. Đây là thước đo phân biệt được hai lần chạy ấy,
        và là con số nhà trường bị hỏi đầu tiên khi công bố.

        `khong_ro` đếm những chỗ đã xếp mà không có thứ hạng — đúng ra
        không bao giờ xảy ra, nhưng để riêng thì tổng luôn cộng khớp với
        số chỗ đã xếp, thay vì âm thầm hụt đi vài dòng.
        """
        try:
            with self._ket_noi_doc() as cur:
                rows = cur.execute("""
                    SELECT rank_in_student_pref AS hang, COUNT(*) AS so_em
                    FROM match_results
                    WHERE club_id IS NOT NULL
                    GROUP BY rank_in_student_pref
                    ORDER BY hang
                """).fetchall()

            dem = {r["hang"]: r["so_em"] for r in rows}
            khong_ro = dem.pop(None, 0)
            tong = sum(dem.values()) + khong_ro

            phan_bo = []
            for h in (1, 2, 3):
                phan_bo.append({"hang": h, "gop": False, "so_em": dem.get(h, 0)})
            # Gop tu 4 tro len bang TONG cac hang >= 4, khong phai dem.get(4):
            # truong cho khai toi 10 nguyen vong moi buoi, nen hang 5..10 co
            # that va lay dung hang 4 thi bang nay hut mat nguoi.
            phan_bo.append({
                "hang": 4, "gop": True,
                "so_em": sum(v for k, v in dem.items() if k and k >= 4),
            })
            return _ok({
                "phan_bo": phan_bo,
                "khong_ro": khong_ro,
                "tong_da_xep": tong,
            })
        except Exception as e:
            return _fail(err("error_reading_pref_distribution", detail=str(e)))

    @_nho_trong_luc_xuat
    def get_em_chua_co_cho(self):
        """Em không có câu lạc bộ nào cả tuần — KÈM em ấy đã khai những gì.

        VÌ SAO PHẢI KÈM. `get_do_phu` đã đưa ra danh sách tên, rồi im
        lặng. Nhưng đây là việc nhà trường phải xử lý tiếp, và cách xử lý
        phụ thuộc hẳn vào chỗ danh sách kia không nói: một em khai MỘT
        nguyện vọng vào câu lạc bộ chọi 4,35 lần là một chuyện; một em
        khai TÁM nguyện vọng mà vẫn trắng tay là chuyện khác hẳn.

        Tỉ lệ chọi lấy thẳng từ `get_club_fill_stats` chứ không tính lại —
        hai đường tính song song cho cùng một con số là thứ sớm muộn cũng
        trôi khỏi nhau.
        """
        try:
            lap = self.get_club_fill_stats()
            choi = {c["club_id"]: c for c in (lap.get("data") or [])}

            with self._ket_noi_doc() as cur:
                # Cung mot co so voi get_do_phu (dem tu match_results JOIN
                # students), neu khong hai man hinh canh nhau se noi hai con
                # so khac nhau cho cung mot cau hoi.
                tong = cur.execute(
                    "SELECT COUNT(DISTINCT student_id) FROM match_results"
                ).fetchone()[0]
                trang_tay = cur.execute("""
                    SELECT m.student_id, s.name
                    FROM match_results m
                    JOIN students s ON s.student_id = m.student_id
                    GROUP BY m.student_id
                    HAVING SUM(CASE WHEN m.club_id IS NOT NULL THEN 1 ELSE 0 END) = 0
                    ORDER BY m.student_id
                """).fetchall()
                nv = {}
                for r in cur.execute("""
                    SELECT p.student_id, p.club_id, c.name AS ten_clb,
                           COALESCE(c.buoi, ?) AS buoi
                    FROM preferences p
                    JOIN clubs c ON c.club_id = p.club_id
                    ORDER BY p.student_id, p.rank
                """, (BUOI_MAC_DINH,)):
                    nv.setdefault(r["student_id"], []).append({
                        "club_id": r["club_id"],
                        "ten_clb": r["ten_clb"],
                        "buoi": r["buoi"],
                        "ti_le_choi": (choi.get(r["club_id"]) or {}).get("ti_le_choi"),
                    })

            ds = []
            for r in trang_tay:
                da_khai = nv.get(r["student_id"], [])
                ds.append({
                    "student_id": r["student_id"],
                    "name": r["name"],
                    "so_nguyen_vong": len(da_khai),
                    "da_khai": da_khai,
                })
            # `tong_hoc_sinh` la cach giao dien phan biet "chua chay lan
            # nao" voi "moi em deu co cho" — hai trang thai cung cho
            # so_em = 0, ma cau thu hai neu noi sai thi sai theo huong yen
            # long nhat.
            return _ok({"so_em": len(ds), "tong_hoc_sinh": tong,
                        "danh_sach": ds})
        except Exception as e:
            return _fail(err("error_reading_unplaced", detail=str(e)))

    @_nho_trong_luc_xuat
    def get_suat_du_tru(self):
        """Suất dự trữ của từng câu lạc bộ dùng tới đâu, thừa bao nhiêu.

        VÌ SAO PHẢI ĐO. Suất dự trữ là phần lõi khoa học của cả RB-DA. Một
        suất không ai dùng KHÔNG báo lỗi và KHÔNG hiện ở đâu — nó lặng lẽ
        trở thành một suất thường, cơ chế vẫn chạy đúng, còn ý định chính
        sách thì bốc hơi. Thanh vàng ở mục tỉ lệ lấp đầy cho thấy bao
        nhiêu em VÀO BẰNG suất dự trữ; nó không bao giờ cho thấy bao nhiêu
        suất BỊ BỎ PHÍ, mà đó mới là con số để quyết định nới nhãn chính
        sách hay hạ chỉ tiêu dự trữ năm sau.
        """
        try:
            with self._ket_noi_doc() as cur:
                rows = cur.execute("""
                    SELECT c.club_id, c.name, COALESCE(c.buoi, ?) AS buoi,
                           c.capacity, c.reserve_capacity, c.reserve_group,
                           (SELECT COUNT(*)
                              FROM preferences p
                              JOIN students s ON s.student_id = p.student_id
                             WHERE p.club_id = c.club_id
                               AND s.reserve_group IS NOT NULL
                               AND s.reserve_group = c.reserve_group
                           ) AS nhom_dang_ky,
                           (SELECT COUNT(*)
                              FROM match_results m
                             WHERE m.club_id = c.club_id
                               AND m.matched_tier = 'reserve'
                           ) AS da_dung
                    FROM clubs c
                    WHERE c.reserve_capacity > 0
                    ORDER BY buoi COLLATE THU_TU_BUOI, c.club_id
                """, (BUOI_MAC_DINH,)).fetchall()

            ra = []
            for r in rows:
                d = dict(r)
                # Khong the am: neu co bao gio da_dung > chi tieu thi do la
                # loi o cho khac, va ep ve 0 o day se giau no di.
                d["con_thua"] = max(0, (d["reserve_capacity"] or 0) - (d["da_dung"] or 0))
                ra.append(d)
            return _ok(ra)
        except Exception as e:
            return _fail(err("error_reading_reserve_usage", detail=str(e)))

    def get_so_boc_tham_theo_buoi(self, search: str = ""):
        """Thứ tự bốc thăm của từng em ở TỪNG BUỔI.

        VÌ SAO BẢNG NÀY PHẢI CÓ. Phần mềm xáo lại thứ tự ở mỗi buổi. Một
        phụ huynh nhìn kết quả sẽ hỏi đúng câu: *"vì sao con tôi thứ Ba
        đứng thứ 30 mà thứ Sáu đứng thứ 120?"*. Không trả lời được câu đó
        thì cách bốc thăm này không dùng được ở trường, dù nó công bằng
        hơn theo phép đo.

        VÀ NÓ KHÔNG PHÁ TÍNH MINH BẠCH. Trường vẫn chỉ công bố MỘT thứ: bộ
        số đã khoá, cộng với hạt giống. Thứ tự từng buổi là hàm TẤT ĐỊNH
        của hai thứ đó (`sinh_stb_theo_buoi`, dẫn xuất bằng `zlib.crc32`
        chứ không bằng `hash()`), nên ai cũng tính lại được và phải ra
        đúng bảng này. Có test canh việc hai tiến trình khác nhau ra cùng
        kết quả.

        TÍNH LẠI, KHÔNG LƯU THÊM. Không có bảng mới trong cơ sở dữ liệu,
        không phải di trú gì. Hàm dẫn xuất là tất định nên tính lại cho
        đúng bộ số mà lần chạy đã dùng — lưu thêm một bản sao chỉ tạo ra
        cơ hội cho hai bản trôi khỏi nhau.

        DÙNG CHẾ ĐỘ ĐÃ GHI TRONG NHẬT KÝ, KHÔNG DÙNG CHẾ ĐỘ HIỆN TẠI. Một
        cơ sở dữ liệu đã chạy bằng bản trước (ghi 'stb_tuan') mà hiển thị
        theo cách mới thì bảng này khoe một thứ tự CHƯA TỪNG được dùng để
        xếp ai vào đâu — sai, và sai theo kiểu không ai nhận ra. Đọc chế
        độ từ `run_meta` thì bảng luôn trung thực với lần chạy có thật, và
        khi lần chạy đó dùng một bộ số cho cả tuần thì các cột trùng nhau,
        tự nó nói lên điều đó. Cờ `cach_cu` bật để giao diện nói rõ.
        """
        try:
            with self._ket_noi_doc() as cur:
                ds_buoi = self._ds_buoi(cur)
                meta = cur.execute(
                    "SELECT seed, che_do_boc_tham FROM run_meta WHERE id=1"
                ).fetchone()

                query = ("SELECT student_id, name, stb_number FROM students "
                         "WHERE stb_number IS NOT NULL")
                params = ()
                if search:
                    query += " AND (khop_tim(student_id, ?) OR khop_tim(name, ?))"
                    params = (search, search)
                rows = cur.execute(
                    query + " ORDER BY student_id", params).fetchall()

                # Bo so PHAI lay TOAN BO hoc sinh, khong loc theo o tim kiem:
                # thu tu trong mot buoi la thu hang trong CA DAN. Loc trong
                # roi moi xao thi con so hien ra la thu hang trong nhom da
                # loc — mot con so khong co that, va trong y het that.
                tat_ca = dict(cur.execute(
                    "SELECT student_id, stb_number FROM students "
                    "WHERE stb_number IS NOT NULL").fetchall())

            if meta is None or not tat_ca:
                return _ok({"ds_buoi": ds_buoi, "hoc_sinh": [], "seed": None,
                            "nhieu_buoi": len(ds_buoi) > 1, "da_chay": False,
                            "cach_cu": False, "che_do": None})

            seed = meta["seed"]
            che_do = meta["che_do_boc_tham"] or CHE_DO_BOC_THAM_MAC_DINH
            theo_buoi = sinh_stb_theo_buoi(tat_ca, ds_buoi, seed, che_do)

            hoc_sinh = [
                {
                    "student_id": r["student_id"],
                    "name": r["name"],
                    "so": {b: theo_buoi[b].get(r["student_id"]) for b in ds_buoi},
                }
                for r in rows
            ]
            return _ok({
                "ds_buoi": ds_buoi,
                "hoc_sinh": hoc_sinh,
                "tong_hoc_sinh": len(tat_ca),
                "seed": seed,
                "che_do": che_do,
                "cach_cu": che_do != CHE_DO_BOC_THAM_MAC_DINH,
                "nhieu_buoi": len(ds_buoi) > 1,
                "da_chay": True,
            })
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
