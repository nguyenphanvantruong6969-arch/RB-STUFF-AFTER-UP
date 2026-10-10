# -*- coding: utf-8 -*-
"""Phần dùng chung của các kịch bản tham khảo (kiem_verify_nhanh.py, exp_resume.py).

Một bản duy nhất cho bộ nạp mô-đun và bộ sinh dữ liệu, để hai kịch bản không lệch nhau.
Dữ liệu sinh ra là DỮ LIỆU MÔ PHỎNG, không phải dữ liệu thật.
"""
import ast
import functools
import importlib.machinery
import importlib.util
import marshal
import os
import random
import struct
import sys
import types
import zlib

_CAC_TRY = (ast.Try, ast.TryStar) if hasattr(ast, "TryStar") else (ast.Try,)
_COOKIE_PYINSTALLER = b'MEI\x0c\x0b\x0a\x0b\x0e'
_THU_MUC = os.path.dirname(os.path.abspath(__file__))


def nap_canh(ten, tien_to="tham_khao_"):
    """Nạp mô-đun `ten`.py cùng thư mục này theo đường dẫn, không sửa sys.path."""
    spec = importlib.util.spec_from_file_location(tien_to + ten, os.path.join(_THU_MUC, ten + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cung_tep(a, b):
    """So hai đường dẫn như hệ điều hành (liên kết, hoa/thường trên Windows)."""
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def _cung_nguon(tep, mong_doi):
    """`tep` (__file__ của mô-đun) đúng là tệp `mong_doi`? (không có __file__ thì không)."""
    return bool(tep) and _cung_tep(tep, mong_doi)


def _tep_nguon(thu_muc, ten):
    """Đường dẫn tệp nguồn <thu_muc>/<ten>.py; SystemExit rõ nếu thư mục không đọc được hoặc thiếu tệp.

    Kịch bản đo MÃ NGUỒN: nạp thẳng tệp .py này (không import theo tên), nên bản biên dịch cũ, gói cùng tên
    hay gói namespace nằm cạnh không thể chen vào. Thư mục chỉ có bản biên dịch (.pyc) thì không nhận.
    """
    try:
        os.scandir(thu_muc).close()
    except OSError as e:
        raise SystemExit("Không đọc được thư mục %s: %s" % (thu_muc, e))
    tep = os.path.join(thu_muc, ten + ".py")
    if not os.path.isfile(tep):
        raise SystemExit("%s không có %s.py (cần tệp nguồn; bản biên dịch không kèm nguồn không được nhận)."
                         % (thu_muc, ten))
    return tep


@functools.cache
def _goi_cai_dat():
    """Tên gói cấp cao nhất của các bản phân phối đã cài (site-packages), theo siêu dữ liệu cài đặt.
    Quét một lần mỗi tiến trình, và chỉ khi có tên chưa rõ."""
    try:
        from importlib.metadata import packages_distributions
        return frozenset(packages_distributions())
    except Exception:          # siêu dữ liệu hỏng / thiếu: coi như không có gói cài thêm (thận trọng)
        return frozenset()


def _khong_the_bi_che(ten):
    """Mô-đun dựng sẵn hay đóng băng: BuiltinImporter / FrozenImporter của CPython đứng trước mọi đường dẫn, tệp
    cạnh mã không che được. Chỉ hỏi hai bộ tìm này (không tác dụng phụ); bộ tìm cài thêm thì KHÔNG hỏi."""
    return ten in sys.builtin_module_names or importlib.machinery.FrozenImporter.find_spec(ten) is not None


def _tu_thu_muc(thu_muc):
    """Hàm `ten -> bool`: một lần chạy thật (thư mục đã chọn đứng đầu sys.path) có thể lấy `ten` — toàn bộ hay
    một phần gói namespace — từ thư mục đó không? Bảo thủ: nghi ngờ thì coi là có (từ chối rõ, không đo nhầm).

    1. dựng sẵn / đóng băng -> không (xem _khong_the_bi_che);
    2. bộ tìm của thư mục, dựng từ sys.path_hooks như PathFinder làm (không ghi vào sys.path_importer_cache):
       không thấy -> không; thấy mô-đun / gói thường -> có; lỗi -> có;
    3. thư mục chỉ có phần gói namespace -> có, trừ khi PathFinder trên sys.path tìm được mô-đun / gói thường.

    Bộ tìm cài thêm trong sys.meta_path KHÔNG được hỏi: gọi chúng có thể đổi trạng thái tiến trình (vd
    DistutilsMetaFinder của setuptools), và bộ tìm chuyển tiếp cho PathFinder sẽ thấy thư mục khi chạy thật. Tên
    do chúng cung cấp mà thư mục cũng có thì bị từ chối — báo lỗi thừa nhưng không bao giờ đo nhầm mã.
    """
    bo_tim = None
    for moc in sys.path_hooks:
        try:
            bo_tim = moc(thu_muc)
            break
        except ImportError:
            continue

    @functools.cache
    def co(ten):
        if _khong_the_bi_che(ten) or bo_tim is None:
            return False
        try:
            rieng = bo_tim.find_spec(ten)
        except Exception:
            return True
        if rieng is None:
            return False
        if rieng.loader is not None:
            return True
        ngoai = importlib.machinery.PathFinder.find_spec(ten)
        return ngoai is None or ngoai.origin in (None, "namespace")

    return co


_KET_THUC = {("sys", "exit"), ("os", "_exit"), (None, "exit"), (None, "quit")}


def _ket_thuc(cau):
    """Câu lệnh cuối nhánh except làm nhánh không phải đường lui: ném lại / ném lỗi khác / thoát tiến trình."""
    if isinstance(cau, ast.Raise):
        return True
    if isinstance(cau, ast.Expr) and isinstance(cau.value, ast.Call):
        ham = cau.value.func
        if isinstance(ham, ast.Name):
            return (None, ham.id) in _KET_THUC
        if isinstance(ham, ast.Attribute) and isinstance(ham.value, ast.Name):
            return (ham.value.id, ham.attr) in _KET_THUC
    return False


_BAT_DUOC_IMPORTERROR = ("ImportError", "ModuleNotFoundError", "Exception", "BaseException")


def _bat_importerror(nut_try):
    """Nhánh except ĐẦU TIÊN bắt được ImportError (theo thứ tự, như lúc chạy) là đường lui thật: không kết thúc
    bằng ném lại / thoát tiến trình? Điều kiện động (vd `if STRICT: raise`) không xét được tĩnh: coi là đường lui."""
    for h in nut_try.handlers:
        loai = [] if h.type is None else (h.type.elts if isinstance(h.type, ast.Tuple) else [h.type])
        if h.type is None or any(getattr(t, "id", None) in _BAT_DUOC_IMPORTERROR for t in loai):
            return not _ket_thuc(h.body[-1])
    return False


_PHAM_VI_MOI = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)   # thân lớp chạy ngay: không thuộc đây


def _cung_cap(nut):
    """`nut` và các nút chạy ngay cùng nó: không đi vào thân hàm / lambda (chạy lúc gọi, ngoài try)."""
    if isinstance(nut, _PHAM_VI_MOI):
        return
    yield nut
    for con in ast.iter_child_nodes(nut):
        yield from _cung_cap(con)


def _import_la(cay, cho_phep, tu_thu_muc=lambda ten: False):
    """Tên mô-đun mà cây ast `cay` import (đầu tệp LẪN trong hàm, cả import tương đối) không đo được:
    - mô-đun anh em: tên mà một lần chạy thật lấy (toàn bộ hay một phần) từ thư mục đã chọn (`tu_thu_muc`, xem
      _tu_thu_muc) và không thuộc `cho_phep` — luôn từ chối, kể cả trong try;
    - tên ngoài thư viện chuẩn, gói đã cài và `cho_phep`, trừ import tuỳ chọn: nằm trong khối try (kể cả thân
      lớp định nghĩa ở đó; thân hàm / lambda thì không — chạy lúc gọi) mà nhánh except ĐẦU TIÊN bắt được
      ImportError không kết thúc bằng ném lại / thoát tiến trình (xem _bat_importerror).

    Kịch bản đo mã nạp từ một thư mục KHÔNG nằm trên sys.path: mô-đun anh em sẽ hỏng hoặc lấy nhầm bản ở
    chỗ khác (vd thư mục hiện hành) — từ chối từ đầu. Tên KHÔNG có trong thư mục thì lúc chạy thật lẫn dưới
    kịch bản đều tìm trên cùng sys.path, nên luật import tuỳ chọn chỉ nhằm báo lỗi sớm và rõ, không quyết định
    đúng/sai của phép đo. Không bắt được import động bằng chuỗi; mã hiện tại không dùng.
    """
    cho_phep = set(cho_phep)
    tuy_chon = set()
    for nut in ast.walk(cay):
        if isinstance(nut, _CAC_TRY) and _bat_importerror(nut):
            for con in nut.body:
                tuy_chon.update(id(n) for n in _cung_cap(con))

    def la_ten(ten, nut):
        if ten in cho_phep:
            return False
        if tu_thu_muc(ten):
            return True
        if ten in sys.stdlib_module_names:
            return False
        return id(nut) not in tuy_chon and ten not in _goi_cai_dat()

    la = set()
    for nut in ast.walk(cay):
        if isinstance(nut, ast.Import):
            la.update(t for t in (a.name.split(".")[0] for a in nut.names) if la_ten(t, nut))
        elif isinstance(nut, ast.ImportFrom):
            if nut.level:                       # import tương đối: không có gói nào ở đây
                if nut.module:
                    la.add("." * nut.level + nut.module)
                else:
                    la.update("." * nut.level + a.name for a in nut.names)
            elif la_ten(nut.module.split(".")[0], nut):
                la.add(nut.module.split(".")[0])
    return sorted(la)


def _bien_dich_da_kiem(tep, cho_phep, tu_thu_muc=lambda ten: False):
    """Đọc tệp MỘT lần, kiểm import trên chính bản đã đọc rồi biên dịch đúng bản đó (không có khe giữa lúc
    kiểm và lúc chạy). SystemExit rõ cho lỗi đọc, lỗi cú pháp và import lạ."""
    try:
        with open(tep, "rb") as f:
            nguon = f.read()
        cay = ast.parse(nguon, filename=tep)
    except (OSError, SyntaxError, ValueError) as e:
        raise SystemExit("Không đọc / phân tích được %s: %s" % (tep, e))
    la = _import_la(cay, cho_phep, tu_thu_muc)
    if la:
        duoc = ", ".join(sorted(cho_phep)) or "không mô-đun nào của kho mã (nó được nạp trước)"
        raise SystemExit("%s import mô-đun anh em hoặc mô-đun ngoài thư viện chuẩn và gói đã cài: %s. Trong kho "
                         "mã, tệp này chỉ được import: %s. Mô-đun anh em sẽ không đến từ thư mục đã chọn (thư mục không nằm "
                         "trên sys.path; mô-đun nạp trước thì bản của thư mục này chưa có)."
                         % (tep, ", ".join(la), duoc))
    return compile(cay, tep, "exec", dont_inherit=True)


def _nguon_thuc(mod):
    """Mô tả nơi một mô-đun thật sự đến từ (gói namespace không có __file__ thì nêu __path__)."""
    if mod is None:
        return "một mục None không rõ nguồn trong sys.modules"
    tep = getattr(mod, "__file__", None)
    if tep:
        return tep
    duong = list(getattr(mod, "__path__", []) or [])
    return "gói namespace tại %s" % duong if duong else "một mô-đun không rõ nguồn (không có __file__)"


_TEN = ("i18n_errors", "rbda_priority_pipeline")   # i18n_errors trước: mô-đun chính import nó theo tên


def _nap_co_kiem(ao, nap, mo_ta, chuan_bi=None):
    """Một luật cho mọi nguồn: `ao` = {tên mô-đun: đường dẫn mong đợi}.

    Đã nạp đúng cả hai từ đó -> trả bản đã nạp. Đã nạp từ nơi khác -> SystemExit (mỗi tiến trình một bản).
    Chưa có -> gọi `chuan_bi(chua_co)` (nếu có) một lần cho mọi mô-đun còn thiếu, rồi `nap(ten)` theo thứ tự
    _TEN; hỏng giữa chừng thì gỡ mọi mô-đun vừa thêm.
    """
    da_nap = {ten: getattr(sys.modules.get(ten), "__file__", None) for ten in _TEN}
    if all(_cung_nguon(da_nap[ten], ao[ten]) for ten in _TEN):
        return sys.modules["rbda_priority_pipeline"]
    for ten in _TEN:
        if ten in sys.modules and not _cung_nguon(da_nap[ten], ao[ten]):
            raise SystemExit("Tiến trình này đã nạp %s từ %s; muốn đo %s hãy chạy một tiến trình riêng."
                             % (ten, _nguon_thuc(sys.modules[ten]), mo_ta))
    chua_co = [ten for ten in _TEN if ten not in sys.modules]
    try:
        if chuan_bi is not None:
            chuan_bi(chua_co)
        for ten in chua_co:
            nap(ten)
            # Kiểm SAU khi nạp (mô-đun có thể tự thay mình trong sys.modules khi chạy).
            tep = getattr(sys.modules.get(ten), "__file__", None)
            if not _cung_nguon(tep, ao[ten]):
                raise SystemExit("%s: mô-đun %s được nạp từ %s, không phải %s."
                                 % (mo_ta, ten, _nguon_thuc(sys.modules.get(ten)), ao[ten]))
    except BaseException:
        for ten in chua_co:   # nạp hỏng: không để mô-đun dở dang trong tiến trình
            sys.modules.pop(ten, None)
        raise
    return sys.modules["rbda_priority_pipeline"]


def nap_rb(duong_dan):
    """duong_dan = thư mục chứa rbda_priority_pipeline.py (kho mã) HOẶC tệp PhanBoCauLacBo.exe (bản build).

    Mỗi tiến trình chỉ nạp được MỘT bản rbda_priority_pipeline (mã của nó tự import i18n_errors
    theo tên). Nếu tiến trình đã có một bản từ nơi khác thì báo lỗi thay vì lặng lẽ trả bản cũ.
    """
    if os.path.isdir(duong_dan):
        # Thư mục NGƯỜI DÙNG đưa (không phải thư mục đích của liên kết): cả hai tệp lấy từ đây.
        thu_muc = os.path.abspath(duong_dan)
        # Nạp thẳng <thu_muc>/<tên>.py (không import theo tên qua sys.path, không đụng cache bộ tìm).
        # Kiểm mô-đun chính trước: thư mục sai thì báo thiếu rbda_priority_pipeline, đúng như cách dùng ghi.
        tep = {ten: _tep_nguon(thu_muc, ten) for ten in reversed(_TEN)}
        # Mô-đun được import mô-đun nào trong _TEN: chỉ mô-đun nạp TRƯỚC nó (i18n_errors nạp trước nên không
        # được import rbda_priority_pipeline — lúc đó bản này chưa có, import theo tên sẽ lấy nhầm bản khác).
        cho_phep = {ten: set(_TEN[:i]) for i, ten in enumerate(_TEN)}
        ma = {}

        def chuan_bi(chua_co):
            # Kiểm tĩnh và biên dịch MỌI tệp sắp nạp trước khi chạy tệp nào (hỏng ở mô-đun chính thì i18n_errors
            # cũng chưa chạy); tệp đã nạp đúng bản thì không đọc lại. Dựng đủ rồi mới gán (không nửa vời).
            tu_thu_muc = _tu_thu_muc(thu_muc)
            ma.update({t: _bien_dich_da_kiem(tep[t], cho_phep[t], tu_thu_muc) for t in chua_co})

        def nap(ten):
            # Như import: đặt vào sys.modules TRƯỚC khi chạy, để `from i18n_errors import err` bên trong
            # rbda_priority_pipeline lấy đúng bản vừa nạp từ thư mục này. Spec không có bộ nạp và không trỏ tới
            # .pyc: mã chỉ chạy qua đường đã kiểm (importlib.reload không thể đi vòng qua phép kiểm).
            spec = importlib.machinery.ModuleSpec(ten, None, origin=tep[ten])
            mod = importlib.util.module_from_spec(spec)
            mod.__file__ = tep[ten]
            mod.__cached__ = None
            sys.modules[ten] = mod
            exec(ma[ten], mod.__dict__)

        return _nap_co_kiem(tep, nap, "thư mục %s" % thu_muc, chuan_bi)
    if not os.path.isfile(duong_dan):
        raise SystemExit("%s không phải thư mục kho mã cũng không phải tệp PyInstaller (không tồn tại)."
                         % duong_dan)
    # Đường dẫn ảo bên trong tệp .exe: không bao giờ trùng một tệp .py thật của kho mã.
    ao = {ten: os.path.join(os.path.abspath(duong_dan), ten + ".py") for ten in _TEN}
    trang_thai = {}

    def nap(ten):
        if "pyz" not in trang_thai:
            trang_thai["pyz"], trang_thai["mods"] = _doc_pyz(duong_dan)
        pyz, mods = trang_thai["pyz"], trang_thai["mods"]
        if ten not in mods:
            raise SystemExit("Tệp %s không chứa mô-đun %s: không phải bản build rbda-kiosk?" % (duong_dan, ten))
        _ispkg, off, ln = mods[ten]
        co = marshal.loads(zlib.decompress(pyz[off:off + ln]))
        m = types.ModuleType(ten)
        m.__file__ = ao[ten]
        sys.modules[ten] = m
        exec(co, m.__dict__)

    return _nap_co_kiem(ao, nap, "bản build %s" % duong_dan)


def _doc_pyz(duong_dan):
    """Đọc PYZ trong tệp PyInstaller: trả (bytes PYZ, {tên mô-đun: (ispkg, vị trí, độ dài)})."""
    with open(duong_dan, 'rb') as f:
        data = f.read()
    pos = data.rfind(_COOKIE_PYINSTALLER)
    if pos < 0:
        raise SystemExit("%s không phải thư mục kho mã cũng không phải tệp PyInstaller "
                         "(không thấy cookie MEI)." % duong_dan)
    _magic, pkglen, tocpos, toclen, pyver, _pylib = struct.unpack('!8sIIII64s', data[pos:pos + 88])
    # Cookie ghi phiên bản Python lúc build (vd 311); bytecode chỉ nạp được bằng đúng phiên bản đó.
    dang_chay = sys.version_info.major * 100 + sys.version_info.minor
    if pyver >= 100:
        build = pyver
    else:  # PyInstaller rất cũ ghi dạng 27, 36...
        build = (pyver // 10) * 100 + pyver % 10
    if build != dang_chay:
        raise SystemExit("Bản build dùng Python %d.%d nhưng đang chạy Python %d.%d: hãy chạy bằng đúng "
                         "phiên bản đó." % (build // 100, build % 100, dang_chay // 100, dang_chay % 100))
    pkg_start = pos + 88 - pkglen
    toc = data[pkg_start + tocpos: pkg_start + tocpos + toclen]
    p = 0
    pyz = None
    while p < len(toc):
        esz, epos, dlen, _ulen, cflag, _typ = struct.unpack('!IIIIBc', toc[p:p + 18])
        n = toc[p + 18:p + esz].split(b'\x00')[0].decode()
        # PyInstaller 6 đặt tên "PYZ.pyz"; bản trước 6 đặt "PYZ-00.pyz".
        if n == "PYZ.pyz" or (n.startswith("PYZ-") and n.endswith(".pyz")):
            raw = data[pkg_start + epos: pkg_start + epos + dlen]
            pyz = zlib.decompress(raw) if cflag else raw
            break
        p += esz
    if pyz is None:
        raise SystemExit("Không thấy PYZ trong tệp PyInstaller %s." % duong_dan)
    tocoff = struct.unpack('!i', pyz[8:12])[0]
    toc_pyz = marshal.loads(pyz[tocoff:])
    # PyInstaller mới ghi danh sách (tên, mục); bản cũ ghi dict {tên: mục}.
    mods = dict(toc_pyz.items() if isinstance(toc_pyz, dict) else toc_pyz)
    return pyz, mods


def gen(S, K, ratio, npref=10, ntest=4, skew=1.0, seed=1, ngroup_frac=0.15):
    """Sinh (students, clubs, tested, apps, prefs): S học sinh, K CLB, tổng chỗ = S*ratio."""
    import numpy as np  # chỉ kịch bản tham khảo cần; không phải phụ thuộc sản phẩm
    rng = random.Random(seed)
    cids = [f"c{j:03d}" for j in range(K)]
    pop = np.array([1.0 / ((j + 1) ** skew) for j in range(K)])
    pop /= pop.sum()
    caps = np.maximum(1, np.round(int(S * ratio) * np.ones(K) / K)).astype(int)
    clubs = {c: {'capacity': int(caps[j]), 'reserve_capacity': int(caps[j] * 0.1),
                 'reserve_group': 'cs' if j % 3 == 0 else None} for j, c in enumerate(cids)}
    students = {}
    prefs = {}
    tested = {c: {} for c in cids}
    apps = {c: [] for c in cids}
    nrng = np.random.default_rng(seed)
    for i in range(S):
        sid = f"s{i:06d}"
        students[sid] = {'reserve_group': 'cs' if rng.random() < ngroup_frac else None}
        pl = list(nrng.choice(K, size=min(npref, K), replace=False, p=pop))
        prefs[sid] = [cids[j] for j in pl]
        for j in pl[:ntest]:
            tested[cids[j]][sid] = round(float(nrng.normal(6.5, 1.5)) * 2) / 2
        for j in pl:
            apps[cids[j]].append(sid)
    return students, clubs, tested, apps, prefs
