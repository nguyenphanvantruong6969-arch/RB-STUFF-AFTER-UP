# -*- coding: utf-8 -*-
"""Dựng báo cáo MẪU kết quả phân bổ, chạy trên bộ dữ liệu sạch `bo_sach/`.

    ./.venv/bin/python du_lieu_test/bao_cao_phan_bo.py

Đi ĐÚNG con đường người dùng thật đi: nạp CSV qua `import_csv_auto`, chạy
qua `run_pipeline`, đọc kết quả qua `match_results` — không gọi thẳng vào
trong thuật toán. Toàn bộ số liệu trong báo cáo ĐỌC THẲNG từ CSDL sau khi
chạy, không gõ tay con số nào. Dùng một CSDL tạm (`tempfile`), không đụng
tới `app.db` thật của người dùng.
"""

import collections
import io
import os
import sqlite3
import sys
import tempfile

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(THU_MUC)
sys.path.insert(0, GOC)

from api import PipelineAPI  # noqa: E402

BO_SACH = os.path.join(THU_MUC, "bo_sach")
TEN_FILE = [
    "SACH_01_danh_sach_CLB",
    "SACH_02_chon_CLB_muon_thi",
    "SACH_03_xep_hang_nguyen_vong",
]
RA = os.path.join(THU_MUC, "bao_cao_phan_bo.html")
SEED = 42
MAU = ["var(--cam)", "var(--reu)", "var(--vang)", "var(--gach)"]


# ------------------------------------------------------------------ #
# Chạy pipeline thật, thu số liệu
# ------------------------------------------------------------------ #
def chay_pipeline():
    with tempfile.TemporaryDirectory() as tmp:
        api = PipelineAPI(os.path.join(tmp, "app.db"))
        canh_bao_nhap = []
        for ten in TEN_FILE:
            p = os.path.join(BO_SACH, ten + ".csv")
            with io.open(p, encoding="utf-8-sig") as f:
                text = f.read()
            r = api.import_csv_auto(text)
            if not r["ok"]:
                raise RuntimeError("nạp %s thất bại: %r" % (ten, r))
            canh_bao_nhap += r["data"].get("warnings", [])

        suc_khoe = api.get_data_health_report()
        if not suc_khoe["ok"]:
            raise RuntimeError("get_data_health_report thất bại: %r" % suc_khoe)

        ket_qua = api.run_pipeline(seed=SEED)
        if not ket_qua["ok"]:
            raise RuntimeError("run_pipeline thất bại: %r" % ket_qua)

        conn = sqlite3.connect(api.db_path)
        conn.row_factory = sqlite3.Row
        clb = conn.execute(
            "SELECT club_id, name, capacity, reserve_capacity, reserve_group "
            "FROM clubs ORDER BY club_id"
        ).fetchall()
        ket = conn.execute(
            "SELECT student_id, club_id, matched_tier, rank_in_student_pref "
            "FROM match_results"
        ).fetchall()
        n_hoc_sinh = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        conn.close()

        return {
            "canh_bao_nhap": canh_bao_nhap,
            "n_canh_bao_suc_khoe": suc_khoe["data"]["n_warnings"],
            "ket_qua": ket_qua["data"],
            "n_hoc_sinh": n_hoc_sinh,
            "clb": clb,
            "ket": ket,
        }


# ------------------------------------------------------------------ #
# Vẽ đồ thị cột bằng SVG viết tay — không kéo thư viện ngoài vào trang.
# ------------------------------------------------------------------ #
def do_thi_cot(nhan, gia_tri, mau_ct, don_vi=""):
    w, h, tren, phai, duoi, trai = 760, 260, 20, 24, 44, 46
    vw, vh = w - trai - phai, h - tren - duoi
    y_max = max(gia_tri) * 1.15 or 1
    n = len(gia_tri)
    rong_cot = vw / n * 0.55
    khoang = vw / n

    def X(i):
        return trai + khoang * i + (khoang - rong_cot) / 2

    def Y(v):
        return tren + vh * (1 - v / y_max)

    p = ['<svg viewBox="0 0 %d %d" class="do-thi" role="img">' % (w, h)]
    for i in range(5):
        v = y_max * i / 4
        y = Y(v)
        p.append('<line x1="%.0f" y1="%.1f" x2="%.0f" y2="%.1f" class="luoi"/>'
                  % (trai, y, trai + vw, y))
        p.append('<text x="%.0f" y="%.1f" class="nhan-truc nhan-y">%.0f%s</text>'
                  % (trai - 10, y + 4, v, don_vi))
    for i, (lb, v) in enumerate(zip(nhan, gia_tri)):
        x = X(i)
        y = Y(v)
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" rx="3"/>'
                  % (x, y, rong_cot, tren + vh - y, mau_ct[i % len(mau_ct)]))
        p.append('<text x="%.1f" y="%.1f" class="nhan-cot">%d</text>'
                  % (x + rong_cot / 2, y - 8, v))
        p.append('<text x="%.1f" y="%d" class="nhan-truc nhan-x">%s</text>'
                  % (x + rong_cot / 2, tren + vh + 22, lb))
    p.append("</svg>")
    return "\n".join(p)


def so(x, n=1):
    """Số kiểu Việt Nam: dấu PHẨY thập phân, dấu chấm phân nhóm nghìn."""
    t = ("{:,.%df}" % n).format(x)
    return t.replace(",", " ").replace(".", ",").replace(" ", ".")


CSS = """
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>

  :root {
    --muc: #1C2321; --muc-nhat: #4A5350; --xam: #5B6570;
    --giay: #F3F4F1; --the: #FFFFFF; --ke: #DBDCD5; --ke-mo: #E9EAE4;
    --cam: #CC785C; --reu: #3F6B52; --vang: #C98A1F; --gach: #B84A3E;
    --reu-nhat: #DCE9E0; --gach-nhat: #F3DCD9; --vang-nhat: #F1DFB8;
    --f-hien: "Be Vietnam Pro", "Segoe UI", sans-serif;
    --f-than: "IBM Plex Sans", "Segoe UI", sans-serif;
    --f-so: "IBM Plex Mono", ui-monospace, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --muc: #E8EAE6; --muc-nhat: #B4BAB6; --xam: #929A9E;
      --giay: #161A19; --the: #1F2422; --ke: #333A37; --ke-mo: #262C2A;
      --cam: #E39A80; --reu: #7FB393; --vang: #E0AF52; --gach: #E08074;
      --reu-nhat: #23342A; --gach-nhat: #382422; --vang-nhat: #33291A;
    }
  }
  :root[data-theme="dark"] {
    --muc: #E8EAE6; --muc-nhat: #B4BAB6; --xam: #929A9E;
    --giay: #161A19; --the: #1F2422; --ke: #333A37; --ke-mo: #262C2A;
    --cam: #E39A80; --reu: #7FB393; --vang: #E0AF52; --gach: #E08074;
    --reu-nhat: #23342A; --gach-nhat: #382422; --vang-nhat: #33291A;
  }

  * { box-sizing: border-box; }
  body {
    background: var(--giay); color: var(--muc);
    font-family: var(--f-than); font-size: 16px; line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }
  .khung { max-width: 1000px; margin: 0 auto; padding: 56px 24px 96px; }

  h1 { font-family: var(--f-hien); font-weight: 700; font-size: clamp(30px, 5vw, 44px);
       line-height: 1.12; letter-spacing: -0.02em; margin: 0 0 14px; text-wrap: balance; }
  h2 { font-family: var(--f-hien); font-weight: 600; font-size: 24px; letter-spacing: -0.01em;
       margin: 64px 0 6px; display: flex; align-items: baseline; gap: 14px; text-wrap: balance; }
  h2 .stt { font-family: var(--f-so); font-size: 13px; color: var(--cam);
            border: 1px solid var(--cam); border-radius: 4px; padding: 1px 7px; flex: none; }
  h3 { font-family: var(--f-hien); font-weight: 600; font-size: 17px; margin: 34px 0 8px; }
  p { margin: 0 0 14px; max-width: 68ch; }
  .dan { color: var(--xam); font-size: 15px; margin-bottom: 30px; max-width: 68ch; }
  code { font-family: var(--f-so); font-size: 0.9em; background: var(--ke-mo);
         padding: 1px 5px; border-radius: 3px; }
  strong { font-weight: 600; }

  .canh-bao { border: 1px solid var(--gach); background: var(--gach-nhat);
    border-radius: 8px; padding: 16px 20px; margin: 0 0 34px; }
  .canh-bao p { margin: 0; font-size: 14.5px; color: var(--muc); }
  .canh-bao .tieu { font-family: var(--f-so); font-size: 11px; letter-spacing: .1em;
    text-transform: uppercase; color: var(--gach); display: block; margin-bottom: 6px; }

  .doc-so { display: grid; gap: 14px; margin: 26px 0 8px;
    grid-template-columns: repeat(auto-fit, minmax(168px, 1fr)); }
  .o-so { background: var(--the); border: 1px solid var(--ke); border-radius: 10px; padding: 16px 18px; }
  .o-so .con-so { font-family: var(--f-so); font-weight: 500; font-size: 30px;
    line-height: 1.1; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
  .o-so .nhan { font-family: var(--f-so); font-size: 10.5px; letter-spacing: .09em;
    text-transform: uppercase; color: var(--xam); margin-top: 7px; display: block; }
  .o-so.tot .con-so { color: var(--reu); }
  .o-so.canh .con-so { color: var(--gach); }

  .bang-cuon { overflow-x: auto; margin: 22px 0; border: 1px solid var(--ke); border-radius: 10px; }
  table { border-collapse: collapse; width: 100%; font-size: 14.5px; background: var(--the); }
  th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--ke-mo); }
  th { font-family: var(--f-so); font-size: 10.5px; letter-spacing: .08em;
       text-transform: uppercase; color: var(--xam); font-weight: 500;
       background: var(--ke-mo); white-space: nowrap; }
  td.so { font-family: var(--f-so); font-variant-numeric: tabular-nums; white-space: nowrap; }
  tbody tr:last-child td { border-bottom: none; }
  .dam { font-weight: 600; }

  .the-do-thi { background: var(--the); border: 1px solid var(--ke); border-radius: 10px;
    padding: 22px 20px 14px; margin: 22px 0; overflow-x: auto; }
  .do-thi { width: 100%; height: auto; min-width: 480px; display: block; }
  .luoi { stroke: var(--ke); stroke-width: 1; }
  .nhan-truc { font-family: var(--f-so); font-size: 11px; fill: var(--xam); }
  .nhan-y { text-anchor: end; }
  .nhan-x { text-anchor: middle; }
  .nhan-cot { font-family: var(--f-so); font-size: 12px; font-weight: 500;
    fill: var(--muc); text-anchor: middle; }
  .chu-thich { list-style: none; padding: 0; margin: 6px 0 0; display: flex;
    flex-wrap: wrap; gap: 8px 20px; font-family: var(--f-so); font-size: 12px; color: var(--muc-nhat); }
  .chu-thich li { display: flex; align-items: center; gap: 7px; }
  .cham { width: 11px; height: 11px; border-radius: 50%; flex: none; }

  .ket { border-left: 3px solid var(--cam); padding: 2px 0 2px 18px; margin: 20px 0; }
  .ket p:last-child { margin-bottom: 0; }
  .doan-cuoi { margin-top: 72px; padding-top: 24px; border-top: 1px solid var(--ke);
    color: var(--xam); font-size: 14px; }
  .doan-cuoi p { max-width: none; }
</style>
"""


def main():
    d = chay_pipeline()
    kq = d["ket_qua"]
    n_total, n_matched, rounds = kq["n_total"], kq["n_matched"], kq["rounds_run"]

    dem_hang = collections.Counter(
        r["rank_in_student_pref"] for r in d["ket"] if r["rank_in_student_pref"]
    )
    dem_tang = collections.Counter(r["matched_tier"] for r in d["ket"] if r["matched_tier"])
    chua_xep = n_total - n_matched

    hang_toi_da = max(dem_hang) if dem_hang else 0
    nhan_hang = [str(i) for i in range(1, hang_toi_da + 1)]
    gt_hang = [dem_hang.get(i, 0) for i in range(1, hang_toi_da + 1)]

    dem_theo_clb = collections.Counter(r["club_id"] for r in d["ket"] if r["club_id"])
    dem_dt_theo_clb = collections.Counter(
        r["club_id"] for r in d["ket"] if r["club_id"] and r["matched_tier"] == "reserve"
    )

    H = []
    A = H.append
    A('<title>Báo cáo mẫu — Kết quả phân bổ RB-DA</title>')
    A(CSS)
    A('<div class="khung">')
    A('<h1>Báo cáo mẫu: Kết quả phân bổ câu lạc bộ</h1>')
    A('<p class="dan">Chạy thật thuật toán RB-DA (Reserve-Based Deferred Acceptance) trên '
      'bộ dữ liệu mẫu <code>du_lieu_test/bo_sach/</code> — %d học sinh, %d câu lạc bộ, '
      'seed cố định = %d. Đi đúng đường người dùng thật đi: nạp CSV qua '
      '<code>import_csv_auto</code>, chạy qua <code>run_pipeline</code>, đọc kết quả từ '
      'bảng <code>match_results</code>.</p>' % (d["n_hoc_sinh"], len(d["clb"]), SEED))

    A('<div class="canh-bao"><span class="tieu">Dữ liệu mô phỏng</span>'
      '<p><code>bo_sach/</code> là bộ dữ liệu do máy sinh (không phải học sinh có thật), '
      'thiết kế để nạp vào <strong>không phát sinh cảnh báo nào</strong> — đo được '
      '<strong>%d cảnh báo lúc nạp</strong> và <strong>%d cảnh báo sức khoẻ dữ liệu</strong> '
      'ở lần chạy này. Đây là báo cáo <strong>mẫu</strong> minh hoạ định dạng đầu ra, '
      'không phải kết quả tuyển sinh thật.</p></div>'
      % (len(d["canh_bao_nhap"]), d["n_canh_bao_suc_khoe"]))

    # ---------- Tom tat ----------
    A('<h2><span class="stt">TL</span>Tóm tắt</h2>')
    A('<div class="doc-so">')
    for gt, nhan, lop in [
        ("%d / %d" % (n_matched, n_total), "học sinh được xếp", "tot" if chua_xep == 0 else ""),
        (so(100 * n_matched / n_total, 1) + "%", "tỉ lệ xếp được", ""),
        ("%d" % rounds, "số vòng lặp thuật toán", ""),
        ("%d" % dem_tang.get("reserve", 0), "vào bằng suất dự trữ", ""),
        ("%d" % dem_hang.get(1, 0), "được đúng nguyện vọng 1", ""),
        ("%d" % chua_xep, "chưa được xếp", "canh" if chua_xep else "tot"),
    ]:
        A('<div class="o-so %s"><div class="con-so">%s</div>'
          '<span class="nhan">%s</span></div>' % (lop, gt, nhan))
    A('</div>')

    A('<div class="ket"><p>%d trong tổng số %d học sinh (%s%%) được xếp vào một câu lạc bộ. '
      '%s trong số đó vào bằng <strong>suất dự trữ</strong> (ưu tiên theo nhóm khai báo, '
      'không theo điểm/bốc thăm) — cơ chế dự trữ thật sự có tác dụng trên bộ dữ liệu này, '
      'không chỉ tồn tại trên lý thuyết.</p></div>'
      % (n_matched, n_total, so(100 * n_matched / n_total, 1), dem_tang.get("reserve", 0)))

    # ---------- Phan bo nguyen vong ----------
    A('<h2><span class="stt">1</span>Được xếp vào nguyện vọng thứ mấy</h2>')
    A('<p>Không phải ai cũng vào nguyện vọng 1 — đây chính là bằng chứng thuật toán '
      '<strong>thực sự phải cạnh tranh</strong>, không phải ai muốn gì được nấy.</p>')
    A('<div class="the-do-thi">')
    A(do_thi_cot(nhan_hang, gt_hang, MAU))
    A('</div>')
    A('<div class="bang-cuon"><table><thead><tr><th>Nguyện vọng</th><th>Số học sinh</th>'
      '<th>Tỉ lệ trong nhóm được xếp</th></tr></thead><tbody>')
    for i in range(1, hang_toi_da + 1):
        n = dem_hang.get(i, 0)
        A('<tr><td>Nguyện vọng %d</td><td class="so dam">%d</td>'
          '<td class="so">%s%%</td></tr>' % (i, n, so(100 * n / n_matched, 1)))
    A('</tbody></table></div>')

    # ---------- Dien thuong / du tru ----------
    A('<h2><span class="stt">2</span>Diện thường và diện dự trữ</h2>')
    A('<div class="bang-cuon"><table><thead><tr><th>Diện trúng tuyển</th>'
      '<th>Số học sinh</th><th>Tỉ lệ</th></tr></thead><tbody>'
      '<tr><td>Thường</td><td class="so dam">%d</td><td class="so">%s%%</td></tr>'
      '<tr><td>Dự trữ</td><td class="so dam">%d</td><td class="so">%s%%</td></tr>'
      '</tbody></table></div>'
      % (dem_tang.get("general", 0), so(100 * dem_tang.get("general", 0) / n_matched, 1),
         dem_tang.get("reserve", 0), so(100 * dem_tang.get("reserve", 0) / n_matched, 1)))

    # ---------- Theo CLB ----------
    A('<h2><span class="stt">3</span>Tình hình từng câu lạc bộ</h2>')
    A('<p>Chỗ đã lấp so với chỉ tiêu, tách riêng phần lấp bằng suất dự trữ.</p>')
    A('<div class="bang-cuon"><table><thead><tr><th>Câu lạc bộ</th><th>Chỉ tiêu</th>'
      '<th>Đã lấp</th><th>Trong đó dự trữ</th><th>Lấp đầy</th></tr></thead><tbody>')
    for c in d["clb"]:
        da_lap = dem_theo_clb.get(c["club_id"], 0)
        dt = dem_dt_theo_clb.get(c["club_id"], 0)
        ty_le = 100 * da_lap / c["capacity"] if c["capacity"] else 0
        A('<tr><td>%s</td><td class="so">%d</td><td class="so dam">%d</td>'
          '<td class="so">%s</td><td class="so">%s%%</td></tr>'
          % (c["name"] or c["club_id"], c["capacity"], da_lap,
             str(dt) if c["reserve_capacity"] else "—", so(ty_le, 0)))
    A('</tbody></table></div>')

    # ---------- Phuong phap ----------
    A('<h2><span class="stt">PP</span>Cách tạo báo cáo này</h2>')
    A('<p>Sinh bằng <code>du_lieu_test/bao_cao_phan_bo.py</code>: dựng một CSDL tạm, nạp '
      'ba tệp CSV trong <code>bo_sach/</code> qua đúng API nạp liệu của ứng dụng '
      '(<code>PipelineAPI.import_csv_auto</code>), chạy '
      '<code>PipelineAPI.run_pipeline(seed=%d)</code>, rồi đọc thẳng bảng '
      '<code>match_results</code>/<code>clubs</code> để tính mọi con số ở trên — không có '
      'con số nào gõ tay. CSDL tạm bị xoá ngay sau khi chạy xong, không đụng tới '
      '<code>app.db</code> thật.</p>' % SEED)
    A('<p>Tái tạo: <code>./.venv/bin/python du_lieu_test/bao_cao_phan_bo.py</code>. '
      'Cùng seed và cùng bộ dữ liệu luôn cho ra đúng các con số này — xem '
      '<code>tests/test_bo_sach.py</code> để biết những gì được canh cố định.</p>')

    A('<div class="doan-cuoi"><p>Đây là báo cáo <strong>mẫu</strong> để minh hoạ định dạng '
      'đầu ra của hệ thống. Dữ liệu là mô phỏng do máy sinh (seed cố định), không phải học '
      'sinh có thật; báo cáo cho một đợt tuyển sinh thật sẽ dùng đúng script này trên '
      '<code>app.db</code> thật thay vì bộ mẫu.</p></div>')
    A('</div>')
    io.open(RA, "w", encoding="utf-8").write("\n".join(H))
    print("đã dựng %s (%d/%d học sinh, %d vòng lặp)" % (RA, n_matched, n_total, rounds))


if __name__ == "__main__":
    main()
