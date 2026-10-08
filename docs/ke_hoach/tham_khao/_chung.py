# -*- coding: utf-8 -*-
"""Phần dùng chung của các kịch bản tham khảo (kiem_verify_nhanh.py, exp_resume.py).

Một bản duy nhất cho bộ nạp mô-đun và bộ sinh dữ liệu, để hai kịch bản không lệch nhau.
Dữ liệu sinh ra là DỮ LIỆU MÔ PHỎNG, không phải dữ liệu thật.
"""
import marshal
import os
import random
import struct
import sys
import types
import zlib

_COOKIE_PYINSTALLER = b'MEI\x0c\x0b\x0a\x0b\x0e'


def nap_rb(duong_dan):
    """duong_dan = thư mục chứa rbda_priority_pipeline.py (kho mã) HOẶC tệp PhanBoCauLacBo.exe (bản build)."""
    if os.path.isdir(duong_dan):
        sys.path.insert(0, os.path.abspath(duong_dan))
        import rbda_priority_pipeline as rb_mod
        return rb_mod
    with open(duong_dan, 'rb') as f:
        data = f.read()
    pos = data.rfind(_COOKIE_PYINSTALLER)
    if pos < 0:
        raise SystemExit("%s không phải thư mục kho mã cũng không phải tệp PyInstaller "
                         "(không thấy cookie MEI)." % duong_dan)
    _magic, pkglen, tocpos, toclen, _pyver, _pylib = struct.unpack('!8sIIII64s', data[pos:pos + 88])
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
    mods = {n: v for n, v in marshal.loads(pyz[tocoff:])}

    def load_mod(name):
        _ispkg, off, ln = mods[name]
        co = marshal.loads(zlib.decompress(pyz[off:off + ln]))
        m = types.ModuleType(name)
        m.__file__ = name + '.py'
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
