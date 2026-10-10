# -*- coding: utf-8 -*-
"""Phần dùng chung của các kịch bản tham khảo (kiem_verify_nhanh.py, exp_resume.py).

Một bản duy nhất cho bộ nạp mô-đun và bộ sinh dữ liệu, để hai kịch bản không lệch nhau.
Dữ liệu sinh ra là DỮ LIỆU MÔ PHỎNG, không phải dữ liệu thật.
"""
import importlib.util
import marshal
import os
import random
import struct
import sys
import types
import zlib

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


def _thu_muc_chuan():
    """Các thư mục thư viện của trình thông dịch (thư viện chuẩn, site-packages)."""
    import sysconfig
    duong = sysconfig.get_paths()
    return [os.path.normcase(os.path.realpath(duong[k])) for k in ("stdlib", "platstdlib", "purelib", "platlib")
            if duong.get(k)]


def _phu_thuoc_la(truoc, thu_muc):
    """Mô-đun mới xuất hiện trong sys.modules (ngoài _TEN) có tệp nằm NGOÀI thư viện chuẩn / site-packages:
    mã đo đã import một mô-đun anh em và nó đến từ chỗ khác thư mục đã chọn (vd thư mục hiện hành)."""
    chuan = _thu_muc_chuan()
    la = []
    for ten in set(sys.modules) - truoc - set(_TEN):
        tep = getattr(sys.modules.get(ten), "__file__", None)
        if not tep:
            continue           # mô-đun dựng sẵn
        tep = os.path.normcase(os.path.realpath(tep))
        if not any(tep.startswith(g + os.sep) for g in chuan):
            la.append((ten, tep))
    return sorted(la)


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


def _nap_co_kiem(ao, nap, mo_ta):
    """Một luật cho mọi nguồn: `ao` = {tên mô-đun: đường dẫn mong đợi}.

    Đã nạp đúng cả hai từ đó -> trả bản đã nạp. Đã nạp từ nơi khác -> SystemExit (mỗi tiến trình một bản).
    Chưa có -> gọi `nap(ten)` theo thứ tự _TEN; hỏng giữa chừng thì gỡ mọi mô-đun vừa thêm.
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

        def nap(ten):
            # Như import: đặt vào sys.modules TRƯỚC khi chạy, để `from i18n_errors import err` bên trong
            # rbda_priority_pipeline lấy đúng bản vừa nạp từ thư mục này. Mã hiện tại chỉ import thư viện
            # chuẩn và i18n_errors; nếu một phiên bản khác import mô-đun anh em thì nó sẽ không đến từ thư mục
            # này — phát hiện và từ chối thay vì đo lẫn mã.
            truoc = set(sys.modules)
            spec = importlib.util.spec_from_file_location(ten, tep[ten])
            mod = importlib.util.module_from_spec(spec)
            sys.modules[ten] = mod
            spec.loader.exec_module(mod)
            la = _phu_thuoc_la(truoc, thu_muc)
            if la:
                raise SystemExit("%s.py import thêm mô-đun ngoài thư viện chuẩn, nạp từ chỗ khác thư mục đã chọn: "
                                 "%s. Kịch bản chỉ đo được mã import thư viện chuẩn và i18n_errors." % (ten, la))

        return _nap_co_kiem(tep, nap, "thư mục %s" % thu_muc)
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
