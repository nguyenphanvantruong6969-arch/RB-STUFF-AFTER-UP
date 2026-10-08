"""
co_che_doi_chung.py
===================
Thư viện CƠ CHẾ ĐỐI CHỨNG cho bộ đo tính tối ưu.

Tệp này KHÔNG đo gì cả — nó chỉ cài các cơ chế phân bổ khác để
`do_toi_uu_on_dinh.py`, `do_khai_that.py`, `do_ben_vung.py` có cái mà so.

VÌ SAO CẦN
----------
`verify_stability` đã canh được: RB-DA cho **0 cặp phá vỡ**. Nhưng "ổn định"
không có nghĩa là "tốt nhất". Muốn nói được câu nào về chữ *tốt nhất* thì
phải có cái để so — hoặc so với TOÀN BỘ các ma trận ổn định khác (vét cạn),
hoặc so với các cơ chế phân bổ khác.

RÀNG BUỘC TỰ ĐẶT — quan trọng, đừng gỡ
--------------------------------------
Mọi cơ chế ở đây **dùng lại** `club_choice_function` và
`compute_club_priority` của phần mềm thật. Không tệp nào trong thư mục này
được viết lại logic ưu tiên hay logic dự trữ. Lý do: nếu bộ đo tự cài lại
thứ tự ưu tiên thì nó đang so phần mềm với **bản sao của chính nó**, và mọi
kết luận rút ra đều vô nghĩa. Cả TTC lẫn Boston dưới đây đều gọi vào đúng
hàm lựa chọn mà `run_rbda` gọi.

NĂM CƠ CHẾ
----------
| Hàm | Cơ chế | Tính chất lý thuyết |
|---|---|---|
| `loi.run_rbda` | RB-DA (phần mềm đang chạy) | ổn định |
| `da_clb_de_xuat` | DA do CLB đề xuất | ổn định, **xấu nhất** cho học sinh |
| `co_che_boston` | Nhận ngay (Boston) | KHÔNG ổn định, thưởng khai gian |
| `co_che_thu_tu_boc_tham` | Xét lần lượt theo bốc thăm | Pareto tối ưu, **bỏ hết điểm thi** |
| `co_che_ttc` | Top Trading Cycles | Pareto tối ưu, KHÔNG ổn định |

Cộng thêm hai công cụ phân tích:

| Hàm | Việc |
|---|---|
| `liet_ke_ghep_on_dinh` | Vét cạn TOÀN BỘ ma trận ổn định (chỉ dùng được ở quy mô nhỏ) |
| `chu_trinh_pareto` | Tìm mọi chu trình đổi chỗ cùng có lợi, độ dài bất kỳ |

Mọi hàm cơ chế đều nhận cùng một chữ ký và trả về `dict[str, str | None]`
(student_id -> club_id hoặc None), để `do_*.py` gọi chúng qua một vòng lặp
duy nhất.
"""

import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbda_priority_pipeline as loi  # noqa: E402


# ---------------------------------------------------------------------------
# TIỆN ÍCH DÙNG CHUNG
# ---------------------------------------------------------------------------

def tinh_base_rank(clubs, tested_scores, applicants, stb_lottery):
    """{club_id: {student_id: thứ hạng}} — gọi thẳng hàm của phần mềm.

    Đây là thứ hạng ưu tiên NỀN hai tầng (điểm trước, bốc thăm sau). Mọi cơ
    chế dưới đây dùng chung bảng này, nên khác biệt giữa các cơ chế đến từ
    ĐÚNG cách chúng ghép, không phải từ cách chúng xếp hạng.
    """
    base_rank = {}
    for club_id in clubs:
        thu_tu = loi.compute_club_priority(
            club_id=club_id,
            applicants_for_club=applicants.get(club_id, []),
            tested_scores_for_club=tested_scores.get(club_id, {}),
            stb_lottery=stb_lottery,
        )
        base_rank[club_id] = {sid: i for i, sid in enumerate(thu_tu)}
    return base_rank


def bang_thu_hang_nguyen_vong(preferences):
    """{student_id: {club_id: thứ hạng nguyện vọng}} — số nhỏ = thích hơn."""
    return {sid: {cid: i for i, cid in enumerate(ps)} for sid, ps in preferences.items()}


def thich_hon(bang, sid, cid_a, cid_b):
    """Em `sid` có thích `cid_a` hơn `cid_b` không? None = không có suất."""
    if cid_a is None:
        return False
    h = bang.get(sid, {})
    if cid_a not in h:
        return False                      # không khai CLB này -> không nhận
    if cid_b is None:
        return True                       # có suất luôn hơn không có suất
    if cid_b not in h:
        return True
    return h[cid_a] < h[cid_b]


def _ham_chon(clubs, base_rank, is_reserve_eligible_fn):
    """Trả về hàm chon(club_id, pool, cap=None, res=None) -> (nhận, tầng).

    Bọc `club_choice_function` lại cho gọn, và cho phép ghi đè sức chứa —
    Boston cần gọi với sức chứa CÒN LẠI chứ không phải sức chứa gốc.
    """
    def chon(club_id, pool, cap=None, res=None):
        info = clubs[club_id]
        return loi.club_choice_function(
            pool,
            info["capacity"] if cap is None else cap,
            info["reserve_capacity"] if res is None else res,
            lambda s, _c=club_id: is_reserve_eligible_fn(s, _c),
            base_rank[club_id],
        )
    return chon


# ---------------------------------------------------------------------------
# CƠ CHẾ 1 — DA DO CLB ĐỀ XUẤT (cận dưới của dàn ổn định)
# ---------------------------------------------------------------------------

def da_clb_de_xuat(
    students, clubs, tested_scores, applicants, preferences,
    stb_lottery, is_reserve_eligible_fn, max_rounds=10000,
):
    """Deferred Acceptance nhưng CLB là bên đề xuất.

    Lý thuyết ghép cặp: đổi bên đề xuất thì được đầu KIA của dàn ổn định.
    Bản do học sinh đề xuất (`run_rbda`) cho ma trận ổn định TỐT NHẤT cho
    học sinh; bản này cho ma trận ổn định XẤU NHẤT cho học sinh. Hiệu số
    giữa hai bản chính là "chọn ai đề xuất đáng giá bao nhiêu" — con số đó
    chưa từng được đo trong dự án.

    Cách chạy: mỗi CLB giữ tập `con_lai` = những em chưa từ chối nó. Mỗi
    vòng, CLB mời đúng tập `Ch_c(con_lai)`. Em giữ lời mời tốt nhất và từ
    chối phần còn lại; đã từ chối là vĩnh viễn (lời mời em đang giữ chỉ có
    thể tốt lên, không bao giờ xấu đi).
    """
    base_rank = tinh_base_rank(clubs, tested_scores, applicants, stb_lottery)
    bang = bang_thu_hang_nguyen_vong(preferences)
    chon = _ham_chon(clubs, base_rank, is_reserve_eligible_fn)

    # Chỉ những em CÓ khai CLB đó mới ghép được với nó.
    con_lai = {
        cid: [s for s in applicants.get(cid, []) if cid in bang.get(s, {})]
        for cid in clubs
    }
    dang_giu = {sid: None for sid in students}

    for _ in range(max_rounds):
        co_doi = False
        for cid in clubs:
            moi, _tang = chon(cid, con_lai[cid])
            for sid in moi:
                hien_tai = dang_giu[sid]
                if hien_tai == cid:
                    continue
                if thich_hon(bang, sid, cid, hien_tai):
                    if hien_tai is not None:
                        con_lai[hien_tai] = [s for s in con_lai[hien_tai] if s != sid]
                    dang_giu[sid] = cid
                    co_doi = True
                else:
                    con_lai[cid] = [s for s in con_lai[cid] if s != sid]
                    co_doi = True
        if not co_doi:
            break
    else:
        raise RuntimeError("da_clb_de_xuat khong hoi tu sau %d vong" % max_rounds)

    return dang_giu


# ---------------------------------------------------------------------------
# CƠ CHẾ 2 — BOSTON / NHẬN NGAY
# ---------------------------------------------------------------------------

def co_che_boston(
    students, clubs, tested_scores, applicants, preferences,
    stb_lottery, is_reserve_eligible_fn, **_,
):
    """Nhận ngay: vòng k, CLB xét những em ghi nó là nguyện vọng thứ k và
    nhận LUÔN, KHÔNG giữ tạm.

    Đây là cơ chế trực giác nhất và là cơ chế nhiều nơi dùng thật. Chỗ chết
    người: em bị trượt nguyện vọng 1 xuống vòng 2 thì chỗ tốt đã hết, nên
    KHAI THẬT LÀ DẠI — phải đoán xem mình có đỗ nguyện vọng 1 không rồi mới
    dám xếp. `do_khai_that.py` đo đúng chỗ đó.

    Cài đặt: dùng lại `club_choice_function` với sức chứa CÒN LẠI mỗi vòng
    (và suất dự trữ còn lại), nên phần dự trữ vẫn chạy đúng như phần mềm.
    """
    base_rank = tinh_base_rank(clubs, tested_scores, applicants, stb_lottery)
    chon = _ham_chon(clubs, base_rank, is_reserve_eligible_fn)

    xep = {sid: None for sid in students}
    da_nhan = {cid: [] for cid in clubs}
    du_tru_da_dung = {cid: 0 for cid in clubs}
    dai_nhat = max((len(p) for p in preferences.values()), default=0)

    for vong in range(dai_nhat):
        nop = {cid: [] for cid in clubs}
        for sid in students:
            if xep[sid] is not None:
                continue
            ps = preferences.get(sid, [])
            if vong < len(ps) and ps[vong] in clubs:
                nop[ps[vong]].append(sid)

        for cid, ung_vien in nop.items():
            con = clubs[cid]["capacity"] - len(da_nhan[cid])
            if con <= 0 or not ung_vien:
                continue
            con_du_tru = max(0, clubs[cid]["reserve_capacity"] - du_tru_da_dung[cid])
            nhan, tang = chon(cid, ung_vien, cap=con, res=min(con, con_du_tru))
            for sid in nhan:
                xep[sid] = cid
                da_nhan[cid].append(sid)
                if tang.get(sid) == "reserve":
                    du_tru_da_dung[cid] += 1

    return xep


# ---------------------------------------------------------------------------
# CƠ CHẾ 3 — XÉT LẦN LƯỢT THEO BỐC THĂM (serial dictatorship)
# ---------------------------------------------------------------------------

def co_che_thu_tu_boc_tham(
    students, clubs, tested_scores, applicants, preferences,
    stb_lottery, is_reserve_eligible_fn, **_,
):
    """Gọi tên từng em theo thứ tự bốc thăm; em được chọn CLB còn chỗ mà
    mình thích nhất.

    Đây là bản tái lập được của cách phân bổ "ai đăng ký trước được trước" —
    cách nhiều trường đang làm. Nó **Pareto tối ưu** cho học sinh (không có
    cách đổi chỗ nào làm ai đó tốt hơn mà không ai xấu đi), nhưng nó **vứt
    bỏ hoàn toàn điểm thi**: em điểm 10 gọi sau em điểm 2 thì thua.

    Có mặt trong bảng so sánh chính vì lý do đó — nó cho thấy "được nguyện
    vọng 1 nhiều" một mình KHÔNG phải thước đo tốt.
    """
    xep = {sid: None for sid in students}
    con_cho = {cid: clubs[cid]["capacity"] for cid in clubs}
    for sid in sorted(students, key=lambda s: stb_lottery.get(s, len(stb_lottery))):
        for cid in preferences.get(sid, []):
            if cid in clubs and con_cho[cid] > 0:
                xep[sid] = cid
                con_cho[cid] -= 1
                break
    return xep


# ---------------------------------------------------------------------------
# CƠ CHẾ 4 — TOP TRADING CYCLES
# ---------------------------------------------------------------------------

def co_che_ttc(
    students, clubs, tested_scores, applicants, preferences,
    stb_lottery, is_reserve_eligible_fn, **_,
):
    """Top Trading Cycles — cơ chế Pareto tối ưu kinh điển.

    Học sinh trỏ vào CLB mình thích nhất còn chỗ; CLB trỏ vào em nó ưu tiên
    nhất còn lại. Mọi chu trình trong đồ thị đó được chốt ngay rồi gỡ khỏi
    bài toán. Lặp tới khi hết.

    TTC cho kết quả **Pareto tối ưu** — không tồn tại cách đổi chỗ nào làm
    một em tốt hơn mà không có em nào xấu đi. Đổi lại, nó **không ổn định**:
    có cặp phá vỡ. Đặt cạnh RB-DA, nó cho thấy đúng cái giá của ổn định.

    Chỗ CLB trỏ vào ai: gọi `club_choice_function` với sức chứa 1 chứ không
    tự đọc `base_rank`, để suất dự trữ vẫn được tôn trọng đúng thứ tự xét
    của phần mềm.
    """
    base_rank = tinh_base_rank(clubs, tested_scores, applicants, stb_lottery)
    chon = _ham_chon(clubs, base_rank, is_reserve_eligible_fn)

    xep = {sid: None for sid in students}
    con_cho = {cid: clubs[cid]["capacity"] for cid in clubs}
    con_du_tru = {cid: clubs[cid]["reserve_capacity"] for cid in clubs}
    con_em = set(students)
    ung_vien_con = {cid: [s for s in applicants.get(cid, [])] for cid in clubs}

    while con_em:
        # Em trỏ vào đâu: CLB thích nhất còn chỗ.
        tro_toi = {}
        for sid in list(con_em):
            dich = None
            for cid in preferences.get(sid, []):
                if cid in clubs and con_cho[cid] > 0:
                    dich = cid
                    break
            if dich is None:
                xep[sid] = None
                con_em.discard(sid)
            else:
                tro_toi[sid] = dich
        if not tro_toi:
            break

        # CLB trỏ vào ai: em đứng đầu hàm lựa chọn của chính nó.
        clb_tro = {}
        for cid in clubs:
            if con_cho[cid] <= 0:
                continue
            pool = [s for s in ung_vien_con[cid] if s in con_em]
            if not pool:
                continue
            dau, _tang = chon(cid, pool, cap=1, res=1 if con_du_tru[cid] > 0 else 0)
            if dau:
                clb_tro[cid] = dau[0]

        # Đi theo đồ thị tìm chu trình.
        da_xu_ly = set()
        tim_thay = False
        for goc in list(tro_toi):
            if goc in da_xu_ly:
                continue
            duong = []
            vi_tri = {}
            nut = goc
            while True:
                if nut not in tro_toi:
                    break
                if nut in vi_tri:
                    chu_trinh = duong[vi_tri[nut]:]
                    for sid in chu_trinh:
                        cid = tro_toi[sid]
                        _nhan, tang = chon(cid, [sid], cap=1,
                                           res=1 if con_du_tru[cid] > 0 else 0)
                        xep[sid] = cid
                        con_cho[cid] -= 1
                        if tang.get(sid) == "reserve" and con_du_tru[cid] > 0:
                            con_du_tru[cid] -= 1
                        con_em.discard(sid)
                    tim_thay = True
                    break
                vi_tri[nut] = len(duong)
                duong.append(nut)
                cid = tro_toi[nut]
                ke = clb_tro.get(cid)
                if ke is None or ke not in tro_toi:
                    break
                nut = ke
            da_xu_ly.update(duong)
            if tim_thay:
                break

        if not tim_thay:
            # Không còn chu trình nào -> phần còn lại không ghép được nữa.
            for sid in list(con_em):
                xep[sid] = None
                con_em.discard(sid)

    return xep


# ---------------------------------------------------------------------------
# CÔNG CỤ 1 — VÉT CẠN TOÀN BỘ MA TRẬN ỔN ĐỊNH
# ---------------------------------------------------------------------------

def la_ghep_on_dinh(xep, clubs, preferences, base_rank, chon, bang=None):
    """Ma trận `xep` có ổn định không? Hai điều kiện, cả hai đều bắt buộc.

    (a) CLB không muốn bỏ ai đang giữ:  Ch_c(mu(c)) == mu(c)
    (b) Không có cặp phá vỡ: với mọi (s, c) mà s thích c hơn chỗ hiện tại,
        s KHÔNG nằm trong Ch_c(mu(c) + s)

    Dùng ĐÚNG `club_choice_function` của phần mềm cho cả hai — giống hệt
    cách `verify_stability` làm, chỉ khác là hàm này chạy được trên MỘT ma
    trận bất kỳ chứ không riêng đầu ra của `run_rbda`.
    """
    if bang is None:
        bang = bang_thu_hang_nguyen_vong(preferences)

    giu = {cid: [] for cid in clubs}
    for sid, cid in xep.items():
        if cid is not None:
            giu[cid].append(sid)

    # Kiểm sức chứa TRƯỚC — đây là phép loại rẻ nhất, và ở chế độ vét cạn nó
    # loại phần lớn tổ hợp trước khi phải gọi hàm lựa chọn lần nào.
    for cid, ds in giu.items():
        if len(ds) > clubs[cid]["capacity"]:
            return False
    for cid, ds in giu.items():
        nhan, _ = chon(cid, ds)
        if set(nhan) != set(ds):
            return False                     # (a) CLB muốn bỏ bớt

    for sid, ps in preferences.items():
        hien_tai = xep.get(sid)
        gioi_han = bang[sid].get(hien_tai, len(ps)) if hien_tai else len(ps)
        for cid in ps[:gioi_han]:
            if cid not in clubs or sid not in base_rank.get(cid, {}):
                continue
            nhan, _ = chon(cid, giu[cid] + [sid])
            if sid in nhan:
                return False                 # (b) cặp phá vỡ
    return True


def liet_ke_ghep_on_dinh(
    students, clubs, tested_scores, applicants, preferences,
    stb_lottery, is_reserve_eligible_fn, tran=400000,
):
    """Liệt kê TOÀN BỘ ma trận ổn định của một thể hiện nhỏ.

    Vét cạn: mỗi em nhận một trong các CLB mình khai, hoặc không có suất.
    Số tổ hợp là tích của (số nguyện vọng + 1), nên chỉ chạy được ở quy mô
    nhỏ — `tran` chặn lại nếu vượt.

    Đây là công cụ trả lời câu hỏi chính: RB-DA có phải ma trận ổn định TỐT
    NHẤT cho học sinh trong TOÀN BỘ tập đó không, hay chỉ là một trong số
    chúng.
    """
    base_rank = tinh_base_rank(clubs, tested_scores, applicants, stb_lottery)
    chon = _ham_chon(clubs, base_rank, is_reserve_eligible_fn)

    ds_em = sorted(students)
    lua_chon = [[c for c in preferences.get(s, []) if c in clubs] + [None] for s in ds_em]

    tong = 1
    for lc in lua_chon:
        tong *= len(lc)
        if tong > tran:
            raise ValueError(
                "The hien qua lon de vet can: >%d to hop (tran=%d)" % (tong, tran))

    # Tính bảng thứ hạng nguyện vọng MỘT lần rồi truyền vào. Bản đầu dựng lại
    # nó bên trong la_ghep_on_dinh, tức là dựng lại vài chục nghìn lần cho mỗi
    # thể hiện — đó là phần lớn thời gian chạy.
    bang = bang_thu_hang_nguyen_vong(preferences)

    ket_qua = []
    for to_hop in itertools.product(*lua_chon):
        xep = dict(zip(ds_em, to_hop))
        if la_ghep_on_dinh(xep, clubs, preferences, base_rank, chon, bang):
            ket_qua.append(xep)
    return ket_qua


def yeu_thich_hon_moi_em(xep_a, xep_b, preferences):
    """`xep_a` có được MỌI em yếu-thích hơn hoặc bằng `xep_b` không?

    Đây đúng là định nghĩa "tối ưu cho học sinh" (student-optimal): không
    một em nào thích `xep_b` hơn `xep_a`.
    """
    bang = bang_thu_hang_nguyen_vong(preferences)
    for sid in preferences:
        if thich_hon(bang, sid, xep_b.get(sid), xep_a.get(sid)):
            return False
    return True


# ---------------------------------------------------------------------------
# CÔNG CỤ 2 — CHU TRÌNH ĐỔI CHỖ CÙNG CÓ LỢI (Pareto, mọi độ dài)
# ---------------------------------------------------------------------------

def chu_trinh_pareto(xep, preferences):
    """Tìm mọi chu trình đổi chỗ mà MỌI em trên chu trình đều lên nguyện
    vọng cao hơn.

    `do_danh_doi_on_dinh.py` mới đếm chu trình ĐỘ DÀI 2 (cặp đôi cùng có
    lợi). Hàm này tổng quát hoá: dựng đồ thị "em s thích chỗ của em t hơn
    chỗ của mình", tìm MỘT chu trình bất kỳ, thực hiện đổi chỗ trên chu
    trình đó, rồi lặp lại trên kết quả mới cho tới khi đồ thị không còn
    chu trình nào.

    Vì sao phải làm: một chu trình ba em (A muốn chỗ B, B muốn chỗ C, C
    muốn chỗ A) làm CẢ BA cùng lên, mà bộ đếm cặp đôi KHÔNG nhìn thấy.
    Không đo thì không biết con số "không tối ưu Pareto" thật sự lớn cỡ nào.

    HAI CHỖ DỄ CÀI SAI, đã vấp và đã sửa:

      1. Bản đầu cho mỗi em chỉ trỏ vào MỘT em — em giữ chỗ mà mình thích
         nhất — rồi đi tìm chu trình. Sai: em A có thể trỏ sang C trong khi
         chu trình thật là A <-> B, và đường đi kết thúc ở một em không trỏ
         đi đâu. Bản đầu báo **0 chu trình** trên cả `bo_sach` lẫn `TEST_0*`,
         trong khi `do_danh_doi_on_dinh.py` đếm được 85 và 19 cặp đôi trên
         đúng hai bộ đó. Hai con số không thể cùng đúng — và bản đầu là bản
         sai. Giờ dựng ĐỦ mọi cung rồi mới dò chu trình.

      2. Chu trình phải đi qua các em ĐANG CÓ SUẤT. Em chưa có suất không
         có gì để đổi, nên không nằm trên chu trình nào.

    Vòng lặp dừng chắc chắn: mỗi lần đổi, tổng thứ hạng nguyện vọng của cả
    trường GIẢM THẬT SỰ (mọi em trên chu trình đều lên hạng), mà tổng đó là
    số nguyên không âm.

    Returns:
        (danh_sách_chu_trình, xếp_sau_khi_đổi)
    """
    bang = bang_thu_hang_nguyen_vong(preferences)
    hien_tai = dict(xep)
    tat_ca = []

    while True:
        co_suat = [s for s, c in hien_tai.items() if c is not None]
        cung = {
            s: [t for t in co_suat
                if t != s and thich_hon(bang, s, hien_tai[t], hien_tai[s])]
            for s in co_suat
        }

        # Dò chu trình bằng DFS ba màu (0 chưa thăm, 1 đang trên ngăn xếp,
        # 2 đã xong). Gặp lại nút đang trên ngăn xếp = tìm thấy chu trình.
        mau = {s: 0 for s in co_suat}
        ngan_xep = []
        chu_trinh = None

        def dfs(u):
            nonlocal chu_trinh
            mau[u] = 1
            ngan_xep.append(u)
            for v in cung[u]:
                if chu_trinh is not None:
                    return
                if mau[v] == 1:
                    chu_trinh = ngan_xep[ngan_xep.index(v):]
                    return
                if mau[v] == 0:
                    dfs(v)
            ngan_xep.pop()
            mau[u] = 2

        gioi_han_cu = sys.getrecursionlimit()
        sys.setrecursionlimit(max(gioi_han_cu, len(co_suat) * 4 + 1000))
        try:
            for s in co_suat:
                if mau[s] == 0 and chu_trinh is None:
                    dfs(s)
                if chu_trinh is not None:
                    break
        finally:
            sys.setrecursionlimit(gioi_han_cu)

        if chu_trinh is None:
            break

        cho_cu = {s: hien_tai[s] for s in chu_trinh}
        for i, sid in enumerate(chu_trinh):
            hien_tai[sid] = cho_cu[chu_trinh[(i + 1) % len(chu_trinh)]]
        tat_ca.append(list(chu_trinh))

    return tat_ca, hien_tai


# ---------------------------------------------------------------------------
# THỐNG KÊ CHUNG CHO MỘT MA TRẬN GHÉP
# ---------------------------------------------------------------------------

def thong_ke(xep, clubs, preferences, base_rank, chon):
    """Bộ số dùng chung để so mọi cơ chế trên cùng một thước."""
    bang = bang_thu_hang_nguyen_vong(preferences)
    tong = len(preferences)
    co_suat = [s for s, c in xep.items() if c is not None]
    thu_hang = [bang[s][xep[s]] + 1 for s in co_suat if xep[s] in bang.get(s, {})]

    pha_vo = 0
    giu = {cid: [] for cid in clubs}
    for sid, cid in xep.items():
        if cid is not None:
            giu[cid].append(sid)
    for sid, ps in preferences.items():
        hien_tai = xep.get(sid)
        gioi_han = bang[sid].get(hien_tai, len(ps)) if hien_tai else len(ps)
        for cid in ps[:gioi_han]:
            if cid not in clubs or sid not in base_rank.get(cid, {}):
                continue
            nhan, _ = chon(cid, giu[cid] + [sid])
            if sid in nhan:
                pha_vo += 1

    ct, _sau = chu_trinh_pareto(xep, preferences)
    return {
        "tong_hoc_sinh": tong,
        "co_suat": len(co_suat),
        "khong_suat": tong - len(co_suat),
        "nv1": sum(1 for h in thu_hang if h == 1),
        "nv2": sum(1 for h in thu_hang if h == 2),
        "nv3_tro_len": sum(1 for h in thu_hang if h >= 3),
        "thu_hang_tb": round(sum(thu_hang) / len(thu_hang), 3) if thu_hang else None,
        "cap_pha_vo": pha_vo,
        "chu_trinh_pareto": len(ct),
        "em_trong_chu_trinh": sum(len(c) for c in ct),
    }
