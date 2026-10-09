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


def _chan_ban_khac(thu_muc):
    """SystemExit nếu tiến trình đã nạp rbda_priority_pipeline / i18n_errors từ nơi khác `thu_muc`."""
    for ten in ("rbda_priority_pipeline", "i18n_errors"):
        mod = sys.modules.get(ten)
        if mod is None:
            continue
        tep = os.path.realpath(getattr(mod, "__file__", "") or "")
        if tep != os.path.realpath(os.path.join(thu_muc, ten + ".py")):
            raise SystemExit("Tiến trình này đã nạp %s từ %s; muốn đo thư mục %s hãy chạy một tiến trình riêng."
                             % (ten, getattr(mod, "__file__", "?"), thu_muc))


def nap_rb(duong_dan):
    """duong_dan = thư mục chứa rbda_priority_pipeline.py (kho mã) HOẶC tệp PhanBoCauLacBo.exe (bản build).

    Mỗi tiến trình chỉ nạp được MỘT bản rbda_priority_pipeline (mã của nó tự import i18n_errors
    theo tên). Nếu tiến trình đã có một bản từ nơi khác thì báo lỗi thay vì lặng lẽ trả bản cũ.
    """
    if os.path.isdir(duong_dan):
        tep = os.path.realpath(os.path.join(duong_dan, "rbda_priority_pipeline.py"))
        if not os.path.isfile(tep):
            raise SystemExit("%s không có rbda_priority_pipeline.py." % duong_dan)
        thu_muc = os.path.dirname(tep)
        _chan_ban_khac(thu_muc)
        da_co = sys.modules.get("rbda_priority_pipeline")
        if da_co is not None:
            return da_co
        # Mô-đun import i18n_errors theo tên (cả bên trong hàm): nạp cả hai từ thư mục này rồi bỏ đường
        # dẫn khỏi sys.path để không che các mô-đun khác của tiến trình.
        sys.path.insert(0, thu_muc)
        try:
            import i18n_errors  # noqa: F401
            import rbda_priority_pipeline as rb_mod
        finally:
            sys.path.remove(thu_muc)
        return rb_mod
    for ten in ("rbda_priority_pipeline", "i18n_errors"):
        if ten in sys.modules:
            raise SystemExit("Tiến trình này đã nạp %s từ %s; muốn đo bản build hãy chạy một tiến trình riêng."
                             % (ten, getattr(sys.modules[ten], "__file__", "?")))
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

    def carch(name):
        toc = data[pkg_start + tocpos: pkg_start + tocpos + toclen]
        p = 0
        while p < len(toc):
            esz, epos, dlen, _ulen, cflag, _typ = struct.unpack('!IIIIBc', toc[p:p + 18])
            n = toc[p + 18:p + esz].split(b'\x00')[0].decode()
            if n == name:
                raw = data[pkg_start + epos: pkg_start + epos + dlen]
                return zlib.decompress(raw) if cflag else raw
            p += esz
        raise SystemExit("Không thấy %s trong tệp PyInstaller %s." % (name, duong_dan))

    pyz = carch('PYZ.pyz')
    tocoff = struct.unpack('!i', pyz[8:12])[0]
    toc_pyz = marshal.loads(pyz[tocoff:])
    # PyInstaller mới ghi danh sách (tên, mục); bản cũ ghi dict {tên: mục}.
    mods = dict(toc_pyz.items() if isinstance(toc_pyz, dict) else toc_pyz)

    def load_mod(name):
        _ispkg, off, ln = mods[name]
        co = marshal.loads(zlib.decompress(pyz[off:off + ln]))
        m = types.ModuleType(name)
        # Đường dẫn ảo bên trong tệp .exe: không bao giờ trùng một tệp .py thật của kho mã.
        m.__file__ = os.path.join(os.path.abspath(duong_dan), name + '.py')
        sys.modules[name] = m
        exec(co, m.__dict__)
        return m

    load_mod('i18n_errors')
    return load_mod('rbda_priority_pipeline')


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
