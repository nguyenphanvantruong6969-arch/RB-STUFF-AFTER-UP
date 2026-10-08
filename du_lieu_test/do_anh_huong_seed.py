"""Đổi seed thì THỰC TẾ bao nhiêu em đổi chỗ?

    ./.venv/bin/python du_lieu_test/do_anh_huong_seed.py
    ./.venv/bin/python du_lieu_test/do_anh_huong_seed.py --so-seed 500

CÂU HỎI ĐANG TRẢ LỜI
Seed là hạt giống bốc thăm. Đọc mã thì biết ngay nó chen vào được ở đâu —
khoá xếp hạng của mỗi CLB là `(-điểm, số_bốc_thăm)`
(`rbda_priority_pipeline.club_priority_order`), nên:

  * hai em ĐIỂM KHÁC NHAU  -> điểm quyết định, seed vô can
  * hai em ĐIỂM BẰNG NHAU  -> seed quyết định ai trước
  * em KHÔNG THI CLB đó    -> xếp thuần theo số bốc thăm (tier 2)

Nhưng đó là câu trả lời định tính. Tệp này ĐO: chạy lại pipeline trên cùng
một bộ dữ liệu với nhiều seed khác nhau, rồi đếm.

CÁCH ĐO
Nạp dữ liệu vào CSDL tạm MỘT lần, rồi với mỗi seed chỉ sinh lại bộ số bốc
thăm và chạy lại thuật toán. Không ghi gì vào CSDL giữa các seed — nên
không đụng `stb_lock`, và cũng không có nguy cơ seed sau nhìn thấy dấu vết
của seed trước.

KHÔNG đụng `app.db` thật: mọi thứ nằm trong thư mục tạm, xoá sau khi chạy.
"""

import argparse
import collections
import os
import shutil
import statistics
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rbda_priority_pipeline as loi  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.abspath(__file__))

SEED_MOC = 42          # seed mọi tài liệu khác đang dùng — lấy làm mốc để so
SO_SEED_MAC_DINH = 200

# Ba bộ dữ liệu, chọn vì chúng khác nhau ĐÚNG ở cái đang đo.
BO_DU_LIEU = [
    ("vi_du_huong_dan  (10 em / 4 CLB)", [
        "vi_du_huong_dan/VIDU_01_danh_sach_CLB.csv",
        "vi_du_huong_dan/VIDU_02_chon_CLB_muon_thi.csv",
        "vi_du_huong_dan/VIDU_03_xep_hang_nguyen_vong.csv",
    ]),
    ("bo_sach          (140 em / 12 CLB)", [
        "bo_sach/SACH_01_danh_sach_CLB.csv",
        "bo_sach/SACH_02_chon_CLB_muon_thi.csv",
        "bo_sach/SACH_03_xep_hang_nguyen_vong.csv",
    ]),
    # TEST_04 CỐ Ý sai — không nạp, vì ở đây đang đo ảnh hưởng của seed
    # trên dữ liệu sạch, không đo phần cảnh báo.
    ("TEST_0*          (120 em / 10 CLB)", [
        "TEST_01_danh_sach_CLB.xlsx",
        "TEST_02_chon_CLB_muon_thi.xlsx",
        "TEST_03_xep_hang_nguyen_vong.xlsx",
    ]),
]


def nap_bo(thu_muc_tam, duong_dan_tuong_doi):
    """Nạp các file CSV vào một CSDL tạm, trả về đường dẫn CSDL."""
    duong_db = os.path.join(thu_muc_tam, "app.db")
    api = PipelineAPI(duong_db)
    for rel in duong_dan_tuong_doi:
        duong = os.path.join(GOC, rel)
        if rel.endswith(".xlsx"):
            # Đi qua ĐÚNG đường mà giao diện đi (xlsx -> text CSV -> nạp),
            # chứ không đọc tắt bằng openpyxl — đo trên đường thật.
            import base64
            with open(duong, "rb") as f:
                kq = api.xlsx_to_csv_text(base64.b64encode(f.read()).decode())
            if not kq["ok"]:
                raise SystemExit("Doc %s that bai: %r" % (rel, kq["errors"]))
            text = kq["data"]["csv_text"]
        else:
            with open(duong, encoding="utf-8-sig") as f:
                text = f.read()
        kq = api.import_csv_auto(text)
        if not kq["ok"]:
            raise SystemExit("Nap %s that bai: %r" % (rel, kq["errors"]))
    return duong_db


def xep_theo_seed(du_lieu, seed):
    """Chạy lại RB-DA với một seed khác. Trả về (xếp chỗ, số cặp phá vỡ)."""
    students, clubs, diem, ung_vien, nguyen_vong, _stb_cu = du_lieu
    stb = loi.generate_stb_lottery(sorted(students), seed)
    du_tru_fn = loi.default_reserve_eligible_fn(students, clubs)
    kq = loi.run_rbda(students, clubs, diem, ung_vien, nguyen_vong, stb, du_tru_fn)
    cap = loi.verify_stability(kq, clubs, nguyen_vong, du_tru_fn)
    return dict(kq.assignment), cap


def em_hoa_diem(du_lieu):
    """Những em CÓ ÍT NHẤT MỘT lần hoà điểm với em khác ở một CLB mình dự
    tuyển. Đây đúng là nhóm mà seed có quyền động vào."""
    _students, _clubs, diem, ung_vien, _nv, _stb = du_lieu
    hoa = set()
    for club_id, ds in ung_vien.items():
        theo_diem = {}
        for sid in ds:
            d = diem.get(club_id, {}).get(sid)
            if d is None:
                continue                       # em không thi -> tier 2, tính riêng
            theo_diem.setdefault(d, []).append(sid)
        for cung_diem in theo_diem.values():
            if len(cung_diem) > 1:
                hoa.update(cung_diem)
    return hoa


def em_khong_thi(du_lieu):
    """Những em dự tuyển một CLB mà KHÔNG có điểm ở CLB đó (tier 2) — với
    họ, seed quyết định hoàn toàn."""
    _students, _clubs, diem, ung_vien, _nv, _stb = du_lieu
    return {
        sid
        for club_id, ds in ung_vien.items()
        for sid in ds
        if diem.get(club_id, {}).get(sid) is None
    }


def do_mot_bo(ten, files, so_seed):
    thu_muc = tempfile.mkdtemp()
    try:
        duong_db = nap_bo(thu_muc, files)
        du_lieu = loi.load_from_sqlite(duong_db)
        students = du_lieu[0]
        nguyen_vong = du_lieu[4]
        n_hs = len(students)

        moc, cap_moc = xep_theo_seed(du_lieu, SEED_MOC)
        if cap_moc:
            raise SystemExit("Bo %s: seed moc da co cap pha vo — loi nghiem trong." % ten)

        so_doi = []             # mỗi seed: bao nhiêu em khác chỗ so với mốc
        so_duoc_xep = []        # mỗi seed: bao nhiêu em có suất
        tung_doi = set()        # em nào TỪNG đổi chỗ ở ít nhất một seed
        cap_pha_vo_toi_da = 0
        # Đếm riêng chuyện CÓ SUẤT HAY KHÔNG — khác hẳn chuyện đổi CLB.
        # Đổi CLB là đổi chỗ ngồi; mất suất là ra khỏi cuộc chơi.
        so_lan_co_suat = collections.Counter()
        phan_bo_so_xep = collections.Counter()
        di_dau = collections.defaultdict(collections.Counter)

        seeds = [SEED_MOC] + [s for s in range(1, so_seed + 1) if s != SEED_MOC]
        for seed in seeds:
            xep, cap = xep_theo_seed(du_lieu, seed)
            cap_pha_vo_toi_da = max(cap_pha_vo_toi_da, len(cap))
            if seed != SEED_MOC:
                khac = {sid for sid in students if xep.get(sid) != moc.get(sid)}
                so_doi.append(len(khac))
                tung_doi |= khac
            n_xep = sum(1 for sid in students if xep.get(sid))
            so_duoc_xep.append(n_xep)
            phan_bo_so_xep[n_xep] += 1
            for sid in students:
                if xep.get(sid):
                    so_lan_co_suat[sid] += 1
                di_dau[sid][xep.get(sid) or "(không có suất)"] += 1

        n_seed = len(seeds)
        bap_benh = sorted(sid for sid in students
                          if 0 < so_lan_co_suat[sid] < n_seed)
        luon_co = sum(1 for sid in students if so_lan_co_suat[sid] == n_seed)
        luon_khong = sum(1 for sid in students if so_lan_co_suat[sid] == 0)

        khong_bao_gio_doi = n_hs - len(tung_doi)
        hoa = em_hoa_diem(du_lieu)
        tier2 = em_khong_thi(du_lieu)

        print()
        print("=" * 74)
        print(ten)
        print("=" * 74)
        print("  Số học sinh                          %8d" % n_hs)
        print("  Số seed đã chạy                      %8d  (1..%d, mốc là %d)"
              % (n_seed, so_seed, SEED_MOC))
        print()
        print("  Em đổi CLB so với seed mốc:")
        print("    ít nhất                            %8d em" % min(so_doi))
        print("    trung bình                         %8.1f em" % statistics.mean(so_doi))
        print("    nhiều nhất                         %8d em" % max(so_doi))
        print()
        print("  KHÔNG BAO GIỜ đổi, dù seed nào       %8d em  (%.1f%%)"
              % (khong_bao_gio_doi, 100.0 * khong_bao_gio_doi / n_hs))
        print("  Từng đổi ở ít nhất một seed          %8d em  (%.1f%%)"
              % (len(tung_doi), 100.0 * len(tung_doi) / n_hs))
        print()
        print("  Em có hoà điểm với bạn khác          %8d em" % len(hoa))
        print("  Em dự tuyển CLB mình KHÔNG thi       %8d em" % len(tier2))
        print("  Em từng đổi mà KHÔNG thuộc hai nhóm  %8d em"
              % len(tung_doi - hoa - tier2))
        print()
        print("  CÓ SUẤT HAY KHÔNG — khác với chuyện đổi CLB:")
        print("    luôn có suất, mọi seed              %8d em  (%.1f%%)"
              % (luon_co, 100.0 * luon_co / n_hs))
        print("    luôn KHÔNG có suất, mọi seed        %8d em  (%.1f%%)"
              % (luon_khong, 100.0 * luon_khong / n_hs))
        print("    BẤP BÊNH — seed quyết định          %8d em  (%.1f%%)"
              % (len(bap_benh), 100.0 * len(bap_benh) / n_hs))
        print("    phân bố số em được xếp: %s"
              % dict(sorted(phan_bo_so_xep.items())))
        for sid in bap_benh:
            print("      %s — nguyện vọng: %s"
                  % (sid, " > ".join(nguyen_vong.get(sid, []))))
            for cid, lan in di_dau[sid].most_common():
                print("          %-24s %4d/%d seed  (%.0f%%)"
                      % (cid, lan, n_seed, 100.0 * lan / n_seed))
        print()
        print("  Số em được xếp: ít nhất %d, nhiều nhất %d"
              % (min(so_duoc_xep), max(so_duoc_xep)))
        print("  Cặp phá vỡ nhiều nhất trên mọi seed  %8d %s"
              % (cap_pha_vo_toi_da, "✓" if cap_pha_vo_toi_da == 0 else "*** LỖI ***"))

        if cap_pha_vo_toi_da:
            raise SystemExit("Có seed cho kết quả KHÔNG ổn định — lỗi nghiêm trọng.")

        return {
            "ten": ten, "n_hs": n_hs, "so_seed": len(seeds) + 1,
            "doi_min": min(so_doi), "doi_tb": statistics.mean(so_doi),
            "doi_max": max(so_doi),
            "khong_doi": khong_bao_gio_doi, "tung_doi": len(tung_doi),
            "hoa": len(hoa), "tier2": len(tier2),
            "ngoai_hai_nhom": len(tung_doi - hoa - tier2),
            "xep_min": min(so_duoc_xep), "xep_max": max(so_duoc_xep),
            "bap_benh": len(bap_benh),
        }
    finally:
        shutil.rmtree(thu_muc, ignore_errors=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--so-seed", type=int, default=SO_SEED_MAC_DINH,
                   help="chạy seed 1..N (mặc định %d)" % SO_SEED_MAC_DINH)
    tham_so = p.parse_args()

    print()
    print("ĐO ẢNH HƯỞNG CỦA SEED — cùng dữ liệu, chỉ đổi hạt giống bốc thăm")
    print("Khoá xếp hạng của mỗi CLB là (-điểm, số bốc thăm): điểm đứng TRƯỚC,")
    print("nên seed chỉ chen vào được chỗ hoà điểm và chỗ em không thi CLB đó.")

    bang = [do_mot_bo(ten, files, tham_so.so_seed) for ten, files in BO_DU_LIEU]

    print()
    print("=" * 74)
    print("TÓM TẮT")
    print("=" * 74)
    print("%-36s %7s %14s %14s %8s"
          % ("Bộ dữ liệu", "số em", "không đổi CLB", "bấp bênh suất", "phá vỡ"))
    print("-" * 84)
    for d in bang:
        print("%-36s %7d %8d (%3.0f%%) %8d (%4.1f%%) %8s"
              % (d["ten"], d["n_hs"],
                 d["khong_doi"], 100.0 * d["khong_doi"] / d["n_hs"],
                 d["bap_benh"], 100.0 * d["bap_benh"] / d["n_hs"], "0  ✓"))
    tong_hs = sum(d["n_hs"] for d in bang)
    tong_bb = sum(d["bap_benh"] for d in bang)
    print("-" * 84)
    print("Gộp ba bộ: %d/%d em (%.1f%%) có suất hay không PHỤ THUỘC seed."
          % (tong_bb, tong_hs, 100.0 * tong_bb / tong_hs))
    print("Mọi seed đều cho kết quả ỔN ĐỊNH (không có cặp phá vỡ nào).")
    print()


if __name__ == "__main__":
    main()
