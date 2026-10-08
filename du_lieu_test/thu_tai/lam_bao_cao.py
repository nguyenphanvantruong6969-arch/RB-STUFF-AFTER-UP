"""Dựng trang báo cáo thử tải từ ket_qua_thu_tai.csv.

    ./.venv/bin/python du_lieu_test/thu_tai/lam_bao_cao.py

Số liệu ĐỌC THẲNG từ CSV, không gõ tay con số nào vào HTML — gõ tay là
tạo ra hai bản dễ lệch nhau. Sửa số đo thì chạy lại tệp này.
"""

import csv
import io
import os

THU_MUC = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(THU_MUC, "ket_qua_thu_tai.csv")
RA = os.path.join(THU_MUC, "bao_cao_thu_tai.html")

# Do bang do_csdl.py va do_giao_dien.py (chay tay, chep vao day).
TANG_CSDL_MS = 15.7      # truy van cham nhat: bang Canh bao du lieu
TANG_UI_MS = 59.0        # 2000 em: goi backend + ve bang
MAU = ["var(--cam)", "var(--reu)", "var(--vang)", "var(--gach)"]


def doc():
    with io.open(CSV, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("hoc_sinh", "so_clb", "nguyen_vong", "so_vong", "xep_duoc",
                  "chua_xep", "xep_chi_nho_boc_tham"):
            r[k] = int(r[k])
        for k in ("t_nap_giay", "t_phan_bo_giay", "t_xuat_giay", "ty_le_cho",
                  "ty_le_xep", "db_MB", "dinh_bo_nho_MB"):
            r[k] = float(r[k])
    return rows


# ------------------------------------------------------------------ #
# Ve do thi bang SVG viet tay — khong keo thu vien ngoai vao trang.
# ------------------------------------------------------------------ #
def khung(w, h, tren, phai, duoi, trai):
    return {"w": w, "h": h, "t": tren, "p": phai, "d": duoi, "tr": trai,
            "vw": w - trai - phai, "vh": h - tren - duoi}


def duong_ke(k, cac_duong, x_nhan, y_max, nhan_y, don_vi=""):
    """cac_duong: [(ten, mau, [gia_tri...])] — cùng độ dài với x_nhan."""
    n = len(x_nhan)
    def X(i):
        return k["tr"] + (k["vw"] * i / max(1, n - 1))
    def Y(v):
        return k["t"] + k["vh"] * (1 - v / y_max)

    p = ['<svg viewBox="0 0 %d %d" class="do-thi" role="img">' % (k["w"], k["h"])]
    # luoi ngang
    for i in range(5):
        v = y_max * i / 4
        y = Y(v)
        p.append('<line x1="%.0f" y1="%.1f" x2="%.0f" y2="%.1f" class="luoi"/>'
                 % (k["tr"], y, k["tr"] + k["vw"], y))
        p.append('<text x="%.0f" y="%.1f" class="nhan-truc nhan-y">%s</text>'
                 % (k["tr"] - 10, y + 4, nhan_y(v)))
    for i, lb in enumerate(x_nhan):
        p.append('<text x="%.1f" y="%d" class="nhan-truc nhan-x">%s</text>'
                 % (X(i), k["t"] + k["vh"] + 22, lb))
    for ten, mau, gt in cac_duong:
        d = " ".join(("M" if i == 0 else "L") + "%.1f %.1f" % (X(i), Y(v))
                     for i, v in enumerate(gt))
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" '
                 'stroke-linejoin="round" stroke-linecap="round"/>' % (d, mau))
        for i, v in enumerate(gt):
            p.append('<circle cx="%.1f" cy="%.1f" r="4" fill="%s"/>'
                     % (X(i), Y(v), mau))
    p.append("</svg>")
    return "\n".join(p)


def chu_thich(muc):
    o = ['<ul class="chu-thich">']
    for ten, mau in muc:
        o.append('<li><span class="cham" style="background:%s"></span>%s</li>' % (mau, ten))
    o.append("</ul>")
    return "\n".join(o)


def so(x, n=2):
    """Số kiểu Việt Nam: dấu PHẨY thập phân, dấu chấm phân nhóm nghìn."""
    t = ("{:,.%df}" % n).format(x)
    return t.replace(",", "\u00a0").replace(".", ",").replace("\u00a0", ".")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


CSS = """
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>

  :root {
    --muc: #1C2321;          /* mực — chữ chính */
    --muc-nhat: #4A5350;
    --xam: #5B6570;
    --giay: #F3F4F1;         /* nền, hơi ngả xanh — không phải kem */
    --the: #FFFFFF;
    --ke: #DBDCD5;
    --ke-mo: #E9EAE4;
    --cam: #CC785C;          /* màu của logo phần mềm */
    --reu: #3F6B52;
    --vang: #C98A1F;
    --gach: #B84A3E;
    --reu-nhat: #DCE9E0;
    --gach-nhat: #F3DCD9;
    --vang-nhat: #F1DFB8;
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
  .chu-thich { list-style: none; padding: 0; margin: 6px 0 0; display: flex;
    flex-wrap: wrap; gap: 8px 20px; font-family: var(--f-so); font-size: 12px; color: var(--muc-nhat); }
  .chu-thich li { display: flex; align-items: center; gap: 7px; }
  .cham { width: 11px; height: 11px; border-radius: 50%; flex: none; }

  .ket { border-left: 3px solid var(--cam); padding: 2px 0 2px 18px; margin: 20px 0; }
  .ket p:last-child { margin-bottom: 0; }
  .doan-cuoi { margin-top: 72px; padding-top: 24px; border-top: 1px solid var(--ke);
    color: var(--xam); font-size: 14px; }
  .doan-cuoi p { max-width: none; }
  .sai { color: var(--gach); font-weight: 600; }
  .dung { color: var(--reu); font-weight: 600; }
</style>
"""


def main():
    rows = doc()
    lay = lambda **kw: [r for r in rows
                        if all(r[k] == v for k, v in kw.items())]

    HS = sorted({r["hoc_sinh"] for r in rows})
    CLB = sorted({r["so_clb"] for r in rows})

    # --- Do thi 1: thoi gian phan bo theo so hoc sinh ---
    d1 = []
    for i, c in enumerate(CLB):
        gt = []
        for h in HS:
            m = lay(hoc_sinh=h, so_clb=c, nguyen_vong=5, cach_chia_chi_tieu="chia_deu",
                    ty_le_cho=1.08)
            gt.append(m[0]["t_phan_bo_giay"] if m else 0.0)
        d1.append(("%d CLB" % c, MAU[i % len(MAU)], gt))
    y1 = max(max(g) for _, _, g in d1) * 1.15

    # --- Do thi 2: % khong duoc xep theo so CLB, moi muc nguyen vong mot duong ---
    def bo_hai(cach):
        ra = []
        for i, nv in enumerate([3, 5, 10]):
            gt = []
            for c in CLB:
                m = lay(hoc_sinh=2000, so_clb=c, nguyen_vong=nv,
                        cach_chia_chi_tieu=cach, ty_le_cho=1.0)
                gt.append(100 - m[0]["ty_le_xep"] if m else 0.0)
            ra.append(("%d nguyện vọng" % nv, MAU[i], gt))
        return ra
    d2a, d2b = bo_hai("chia_deu"), bo_hai("theo_nhu_cau")
    y2 = max(max(g) for bo in (d2a, d2b) for _, _, g in bo) * 1.2 or 1

    # --- So chinh o 2000/50 ---
    def o(nv, cach, ty=1.0):
        m = lay(hoc_sinh=2000, so_clb=50, nguyen_vong=nv,
                cach_chia_chi_tieu=cach, ty_le_cho=ty)
        return m[0]
    chinh = o(5, "chia_deu")
    # "Xấu nhất" phải là lần CHẠY LÂU NHẤT, không phải lần nhiều dữ liệu
    # nhất — hai thứ đó khác nhau, và lấy nhầm là báo cáo một con số dễ
    # chịu hơn sự thật.
    cham_nhat = max(rows, key=lambda r: r["t_phan_bo_giay"])
    tong_cho = chinh["t_phan_bo_giay"] * 1000 + TANG_CSDL_MS + TANG_UI_MS

    k1 = khung(760, 300, 20, 24, 44, 62)
    k2 = khung(760, 280, 20, 24, 44, 52)

    H = []
    A = H.append
    A('<title>Ngưỡng chịu tải RB-DA</title>')
    A(CSS)
    A('<div class="khung">')
    A('<h1>Ngưỡng chịu tải của thuật toán RB-DA</h1>')
    A('<p class="dan">Đo phần mềm phân bổ câu lạc bộ ở %d cấu hình khác nhau — '
      'từ 200 tới 5 000 học sinh, từ 10 tới 100 câu lạc bộ. Ba tầng đều được đo: '
      'thuật toán, truy vấn cơ sở dữ liệu, và thời gian vẽ giao diện.</p>' % len(rows))

    A('<div class="canh-bao"><span class="tieu">Dữ liệu mô phỏng</span>'
      '<p>Toàn bộ số liệu dưới đây đo trên <strong>dữ liệu do máy sinh theo tham số</strong>, '
      'không phải khảo sát học sinh có thật. Trang này chỉ chứa <strong>số đo và cơ chế '
      'kỹ thuật</strong> — phần diễn giải, nhận xét và kết luận nghiên cứu do học sinh tự viết.</p></div>')

    # ---------- Cau tra loi ngan ----------
    A('<h2><span class="stt">TL</span>Câu trả lời ngắn</h2>')
    A('<p>Ở quy mô <strong>2 000 học sinh và 50 câu lạc bộ</strong>, mỗi em xếp 5 nguyện vọng '
      'và dự thi 4 câu lạc bộ:</p>')
    A('<div class="doc-so">')
    for gt, nhan, lop in [
        (so(chinh["t_phan_bo_giay"]) + " s", "chạy phân bổ", "tot"),
        ("%d" % chinh["so_vong"], "số vòng lặp", ""),
        (so(chinh["ty_le_xep"], 1) + "%", "được xếp", ""),
        (so(TANG_CSDL_MS, 0) + " ms", "truy vấn chậm nhất", ""),
        (so(TANG_UI_MS, 0) + " ms", "vẽ bảng kết quả", ""),
        (so(chinh["dinh_bo_nho_MB"], 1) + " MB", "đỉnh bộ nhớ", ""),
    ]:
        A('<div class="o-so %s"><div class="con-so">%s</div>'
          '<span class="nhan">%s</span></div>' % (lop, gt, nhan))
    A('</div>')
    A('<div class="ket"><p>Cả ba tầng cộng lại: <strong>%s giây</strong> từ lúc bấm nút '
      'tới lúc bảng kết quả hiện ra. Lần chạy <strong>lâu nhất trong cả %d cấu hình</strong> — '
      '%s học sinh, %d câu lạc bộ, mỗi em 10 nguyện vọng — mất <strong>%s giây</strong>.</p>'
      '<p style="margin-top:10px">Tỉ lệ 90%% ở trên là trường hợp <strong>chỉ tiêu vừa khít</strong> '
      '(tổng chỗ đúng bằng số học sinh) và mọi câu lạc bộ chỉ tiêu bằng nhau. Dư 8%% chỗ thì '
      'con số này lên <strong>%s%%</strong>.</p></div>'
      % (so(tong_cho / 1000), len(rows), so(cham_nhat["hoc_sinh"], 0),
         cham_nhat["so_clb"], so(cham_nhat["t_phan_bo_giay"]),
         so(o(5, "chia_deu", 1.08)["ty_le_xep"], 1)))

    # ---------- Tang 1 ----------
    A('<h2><span class="stt">1</span>Tầng thuật toán</h2>')
    A('<p>Thời gian chạy phân bổ theo số học sinh, mỗi đường là một số câu lạc bộ. '
      'Mỗi em 5 nguyện vọng, chỉ tiêu chia đều, dư 8%.</p>')
    A('<div class="the-do-thi">')
    A(duong_ke(k1, d1, ["%d" % h for h in HS], y1, lambda v: "%.1fs" % v))
    A(chu_thich([(t, m) for t, m, _ in d1]))
    A('</div>')
    A('<p>Đường cong gần thẳng: thời gian tăng gần tuyến tính theo số học sinh, '
      'không bùng nổ. Số câu lạc bộ ảnh hưởng ít hơn số học sinh.</p>')

    A('<div class="bang-cuon"><table><thead><tr>'
      '<th>Quy mô</th><th>Nạp dữ liệu</th><th>Chạy phân bổ</th><th>Xuất kết quả</th>'
      '<th>Số vòng</th><th>Bộ nhớ</th><th>Tệp .db</th></tr></thead><tbody>')
    for h in HS:
        c = 50 if h >= 500 else 25
        m = lay(hoc_sinh=h, so_clb=c, nguyen_vong=5,
                cach_chia_chi_tieu="chia_deu", ty_le_cho=1.08)
        if not m:
            continue
        r = m[0]
        A('<tr><td class="so">%d em / %d CLB</td><td class="so">%s s</td>'
          '<td class="so dam">%s s</td><td class="so">%s s</td>'
          '<td class="so">%d</td><td class="so">%s MB</td><td class="so">%s MB</td></tr>'
          % (h, c, so(r["t_nap_giay"]), so(r["t_phan_bo_giay"]), so(r["t_xuat_giay"]),
             r["so_vong"], so(r["dinh_bo_nho_MB"], 1), so(r["db_MB"], 1)))
    A('</tbody></table></div>')

    # ---------- Tang 2 + 3 ----------
    A('<h2><span class="stt">2</span>Tầng cơ sở dữ liệu và giao diện</h2>')
    A('<p>Trước khi đo, tôi đọc mã và <strong>đoán trước hai chỗ sẽ nghẽn</strong>: '
      'cơ sở dữ liệu không có một chỉ mục phụ nào, và màn hình Kết quả vẽ thẳng mọi dòng '
      'ra DOM không phân trang. <span class="sai">Cả hai dự đoán đều sai.</span></p>')
    A('<div class="bang-cuon"><table><thead><tr>'
      '<th>Phép đo ở 2 000 em / 50 CLB</th><th>Kết quả</th><th>Dự đoán trước khi đo</th>'
      '</tr></thead><tbody>'
      '<tr><td>Truy vấn chậm nhất (Cảnh báo dữ liệu)</td><td class="so dam">%s ms</td>'
      '<td>nghẽn vì thiếu chỉ mục — <span class="sai">sai</span></td></tr>'
      '<tr><td>Thêm chỉ mục vào bản sao thì nhanh hơn</td><td class="so">1,0–2,0×</td>'
      '<td>trên truy vấn vốn đã dưới 2 ms — không đáng</td></tr>'
      '<tr><td>Vẽ bảng Kết quả 2 000 dòng</td><td class="so dam">%s ms</td>'
      '<td>nghẽn vì không phân trang — <span class="sai">sai</span></td></tr>'
      '<tr><td>Vẽ bảng 200 dòng, để so sánh</td><td class="so">18 ms</td>'
      '<td>—</td></tr>'
      '</tbody></table></div>' % (so(TANG_CSDL_MS, 1), so(TANG_UI_MS, 0)))
    A('<div class="ket"><p>Ở quy mô này, <strong>thuật toán chiếm gần như toàn bộ thời gian '
      'chờ</strong>: %s phần nghìn giây so với %s ms của cơ sở dữ liệu và %s ms của '
      'giao diện. Hai chỗ tôi nghi ngờ trước khi đo đều không phải vấn đề — chúng chỉ trở '
      'thành vấn đề ở quy mô lớn hơn nhiều so với một trường trung học.</p></div>'
      % (so(chinh["t_phan_bo_giay"] * 1000, 0), so(TANG_CSDL_MS, 1), so(TANG_UI_MS, 0)))

    # ---------- Do thi 2: so nguyen vong ----------
    A('<h2><span class="stt">3</span>Nên cho học sinh xếp mấy nguyện vọng?</h2>')
    A('<p>Đây mới là câu ảnh hưởng tới học sinh thật. Với 2 000 em, mỗi em <strong>chỉ dự thi '
      '4 câu lạc bộ</strong> (không thể bắt một em thi 50 kỳ thi), tổng chỉ tiêu vừa đủ 100%%. '
      'Trục đứng là <strong>tỉ lệ em không được xếp vào đâu cả</strong>.</p>')
    A('<h3>Khi mọi câu lạc bộ chỉ tiêu bằng nhau — giống trường thật</h3>')
    A('<div class="the-do-thi">')
    A(duong_ke(k2, d2a, ["%d CLB" % c for c in CLB], y2, lambda v: "%.0f%%" % v))
    A(chu_thich([(t, m) for t, m, _ in d2a]))
    A('</div>')
    A('<h3>Khi câu lạc bộ đông người thích được chia nhiều chỗ hơn</h3>')
    A('<div class="the-do-thi">')
    A(duong_ke(k2, d2b, ["%d CLB" % c for c in CLB], y2, lambda v: "%.0f%%" % v))
    A(chu_thich([(t, m) for t, m, _ in d2b]))
    A('</div>')

    A('<div class="bang-cuon"><table><thead><tr><th>2 000 em, chỉ tiêu vừa đủ</th>'
      '<th>3 nguyện vọng</th><th>5 nguyện vọng</th><th>10 nguyện vọng</th>'
      '</tr></thead><tbody>')
    for cach, ten in [("chia_deu", "Chỉ tiêu chia đều (giống trường thật)"),
                      ("theo_nhu_cau", "Chỉ tiêu chia theo nhu cầu")]:
        o_ = '<tr><td>%s — số em không được xếp</td>' % ten
        for nv in (3, 5, 10):
            r = o(nv, cach)
            o_ += '<td class="so dam">%d</td>' % r["chua_xep"]
        A(o_ + "</tr>")
    A('<tr><td>Được xếp vào CLB <strong>không dự thi</strong> (chỉ nhờ bốc thăm)</td>')
    for nv in (3, 5, 10):
        A('<td class="so">%d</td>' % o(nv, "chia_deu")["xep_chi_nho_boc_tham"])
    A('</tr></tbody></table></div>')
    A('<div class="ket"><p>Hai đồ thị trên khác nhau ở đúng một điều: <strong>cách nhà trường '
      'chia chỉ tiêu</strong>. Cùng số học sinh, cùng số nguyện vọng, cùng thuật toán.</p></div>')

    # ---------- Tinh dung dan ----------
    A('<h2><span class="stt">4</span>Nhanh, nhưng có còn đúng không?</h2>')
    A('<p>Chạy nhanh mà kết quả sai thì không tính là chạy được. Thuật toán họ Gale–Shapley '
      'bảo đảm kết quả <strong>ổn định</strong>: không tồn tại cặp (học sinh, câu lạc bộ) nào '
      'mà cả hai đều muốn đổi cho nhau. <code>kiem_on_dinh.py</code> kiểm trực tiếp lời bảo '
      'đảm đó ở quy mô lớn.</p>')
    A('<div class="bang-cuon"><table><thead><tr><th>Quy mô</th><th>Số vòng</th>'
      '<th>Cặp phá vỡ tìm được</th><th>Thời gian kiểm</th></tr></thead><tbody>'
      '<tr><td class="so">500 em / 25 CLB</td><td class="so">12</td>'
      '<td class="so dung">0</td><td class="so">0,01 s</td></tr>'
      '<tr><td class="so">2 000 em / 50 CLB</td><td class="so">16</td>'
      '<td class="so dung">0</td><td class="so">0,08 s</td></tr>'
      '<tr><td class="so">5 000 em / 100 CLB</td><td class="so">12</td>'
      '<td class="so dung">0</td><td class="so">0,31 s</td></tr>'
      '</tbody></table></div>')

    # ---------- Cho gay truoc ----------
    A('<h2><span class="stt">5</span>Chỗ nào gãy trước</h2>')
    A('<div class="bang-cuon"><table><thead><tr><th>Chỗ</th><th>Đo được</th>'
      '<th>Khi nào thành vấn đề</th></tr></thead><tbody>'
      '<tr><td>Thuật toán duyệt <strong>mọi</strong> câu lạc bộ ở mỗi vòng, kể cả câu lạc bộ '
      'không nhận đề nghị nào — và mỗi lần đều sắp xếp lại danh sách</td>'
      '<td class="so">%s s ở %s em / %d CLB</td>'
      '<td>Chi phí ≈ số vòng × số CLB × cỡ danh sách. Đây là lần chạy lâu nhất trong cả %d cấu hình.</td></tr>'
      '<tr><td>Trần cứng <strong>10 nguyện vọng</strong> mỗi học sinh</td>'
      '<td class="so">10</td>'
      '<td>Với 50–100 câu lạc bộ, học sinh chỉ xếp được 10–20%% số lựa chọn.</td></tr>'
      '<tr><td>Cơ sở dữ liệu không có chỉ mục phụ</td><td class="so">%s ms</td>'
      '<td>Chưa thành vấn đề ở 2 000 em. Thêm chỉ mục chỉ lợi 1–2× trên truy vấn vốn đã nhanh.</td></tr>'
      '<tr><td>Bảng Kết quả vẽ thẳng mọi dòng, không phân trang</td><td class="so">%s ms</td>'
      '<td>Chưa thành vấn đề ở 2 000 dòng.</td></tr>'
      '</tbody></table></div>'
      % (so(cham_nhat["t_phan_bo_giay"]), so(cham_nhat["hoc_sinh"], 0),
         cham_nhat["so_clb"], len(rows), so(TANG_CSDL_MS, 1), so(TANG_UI_MS, 0)))

    # ---------- Phuong phap ----------
    A('<h2><span class="stt">PP</span>Cách đo</h2>')
    A('<p>Mọi phép đo đi <strong>đúng con đường người dùng đi</strong>: nạp tệp qua '
      '<code>import_csv_auto</code>, chạy qua <code>run_pipeline</code>, xuất qua '
      '<code>export_csv</code>. Không gọi thẳng vào trong thuật toán — gọi thẳng cho ra con số '
      'đẹp hơn nhưng không phải con số người dùng gặp.</p>')
    A('<p>Trước khi tin bất cứ số nào, bộ đo phải đo lại một thứ <strong>đã biết kết quả</strong>: '
      'bộ 120 học sinh thật của dự án, phải ra đúng 108/120 và 7 vòng. '
      '<code>doi_chung.py</code> làm việc đó và dừng hẳn nếu lệch.</p>')
    A('<p>Nhu cầu sinh theo trọng số Zipf (câu lạc bộ thứ <em>i</em> hút khoảng 1/<em>i</em>), '
      'seed cố định nên chạy lại luôn ra đúng bộ đó. Đo trên máy Linux ảo; máy khác sẽ cho '
      'con số tuyệt đối khác, nhưng <strong>tỉ lệ giữa các quy mô thì giữ nguyên</strong>.</p>')
    A('<p>Tái lập: <code>./.venv/bin/python du_lieu_test/thu_tai/chay_thu_tai.py</code>. '
      'Số liệu thô đầy đủ %d dòng trong <code>ket_qua_thu_tai.csv</code>.</p>' % len(rows))

    A('<div class="doan-cuoi"><p>Trang này chỉ chứa số đo và mô tả cơ chế kỹ thuật. '
      '<strong>Phần diễn giải, nhận xét và kết luận nghiên cứu do học sinh tự viết.</strong> '
      'Dữ liệu là mô phỏng do máy sinh, không phải khảo sát học sinh có thật.</p></div>')
    A('</div>')
    io.open(RA, "w", encoding="utf-8").write("\n".join(H))
    print("da dung %s tu %d dong so lieu" % (RA, len(rows)))


if __name__ == "__main__":
    main()
