/* js/03_ket_qua.js — Thẻ 02 — Kết quả: các bảng, thu gọn mục, xuất tệp.

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 4. TAB 2 — KẾT QUẢ
 * ------------------------------------------------------------------ */

function loadResultsTab() {
  loadTomTatKetQua();
  veXuatPanel();
  loadClubFillStats();
  loadMatchResults(el("resultsSearch") ? el("resultsSearch").value : "");
  loadDoPhu();
  loadThoiKhoaBieu(el("tkbSearch") ? el("tkbSearch").value : "");
  loadSoBocTham(el("thamSearch") ? el("thamSearch").value : "");
  loadPhanBoNguyenVong();
  loadEmChuaCoCho();
  loadSuatDuTru();
  /* Tieu de danh sach thanh vien la chu DONG (co ten cau lac bo), nen
     applyStaticText() khong dich duoc. Mo lai dung cai dang mo — giong
     het cach `openScoringClub` duoc goi lai o the 05. */
  if (clbDangMo) moDanhSachCLB(clbDangMo);
}

/* ---- Thu gọn / mở rộng từng mục ở thẻ Kết quả ----

   Thẻ này xếp năm mục chồng nhau, và mục dài nhất có một dòng cho mỗi em
   mỗi buổi — với 140 em × 3 buổi là hơn 400 dòng. Cuộn qua hết để tới
   mục cuối là việc thật, nên từng mục đóng lại được.

   HAI ĐIỀU DỄ LÀM SAI, đã tránh có chủ ý:

   1. `hidden` đặt trên `.panel-body`, KHÔNG BAO GIỜ trên `.panel`. Ba mục
      doPhu/tkb/tham đã dùng `hidden` trên chính `.panel` để nói "chưa có
      dữ liệu nên chưa hiện". Trộn hai nghĩa vào một thuộc tính thì
      "Mở rộng tất cả" sẽ lôi cả một mục rỗng ra giữa màn hình.

   2. Nhãn nút chung ĐỔI theo trạng thái nên nó là chữ ĐỘNG: nút không
      mang `data-i18n`, vì applyStaticText() sẽ đè chữ tĩnh lên đúng như
      LỖI 3 ở đầu tests/test_giao_dien_chon_buoi.py. Đổi ngôn ngữ thì vẽ
      lại trong reapplyDynamicTextForLangChange(). */

const MUC_KET_QUA = ["fillPanel", "clbPanel", "duTruPanel", "doPhuPanel",
                     "nvPanel", "chuaCoChoPanel", "tkbPanel", "thamPanel",
                     "dsXepPanel"];

/* Lần đầu mở: TẤT CẢ các mục đều đóng, chỉ hiện tiêu đề kèm con số.
   Bản trước để mở sẵn "Tỉ lệ lấp đầy theo CLB" và "Danh sách xếp CLB" —
   với 84 câu lạc bộ, vừa mở thẻ đã là một bức tường thanh ngang và dòng.
   Nhà trường chọn: màn hình gọn, cần mục nào thì bấm mở mục đó.
   Đổi mặc định = sửa đúng mảng này. */
const MAC_DINH_DONG = MUC_KET_QUA.slice();

/* `_v2`: máy nào đã bấm thu gọn/mở rộng dù một lần là đã LƯU trạng thái
   của cả chín mục — tức lưu luôn cái mặc định cũ "lấp đầy đang mở". Giữ
   khoá cũ thì mặc định mới không bao giờ tới được những máy đó. Lựa chọn
   lưu từ nay trở đi vẫn được nhớ như trước. */
const KHOA_THU_GON = "rbda_thu_gon_ket_qua_v2";

let mucDangDong = null;

function docTrangThaiThuGon() {
  /* Bản .exe chạy qua pywebview. Một lỗi kho lưu trữ được phép làm mất
     lựa chọn, KHÔNG được phép ném ra và làm hỏng cả thẻ.

     LƯU DẠNG BẢN ĐỒ {id: đang_mở}, KHÔNG phải mảng các mục đang đóng.
     Bản đầu lưu mảng, và mục nào không có trong mảng thì được hiểu là
     ĐANG MỞ — nên mỗi lần thêm mục mới, người đã dùng tính năng này sẽ
     thấy nó mở toang, đúng cái điều MAC_DINH_DONG sinh ra để tránh. Bản
     đồ phân biệt được "người này đã mở nó" với "chưa từng thấy mục này",
     và trường hợp thứ hai phải lấy mặc định. */
  const kq = new Set(MAC_DINH_DONG);
  try {
    const raw = window.localStorage &&
                window.localStorage.getItem(KHOA_THU_GON);
    if (!raw) return kq;
    const luu = JSON.parse(raw);
    if (!luu || typeof luu !== "object" || Array.isArray(luu)) return kq;
    MUC_KET_QUA.forEach((id) => {
      if (Object.prototype.hasOwnProperty.call(luu, id)) {
        if (luu[id]) kq.delete(id);
        else kq.add(id);
      }
    });
  } catch (e) { /* không đọc được thì dùng mặc định */ }
  return kq;
}

function luuTrangThaiThuGon() {
  try {
    if (window.localStorage) {
      const ban_do = {};
      MUC_KET_QUA.forEach((id) => { ban_do[id] = !mucDangDong.has(id); });
      window.localStorage.setItem(KHOA_THU_GON, JSON.stringify(ban_do));
    }
  } catch (e) { /* không ghi được thì thôi, giao diện vẫn chạy */ }
}

function datMuc(id, mo) {
  const than = el(id + "Body");
  const nut = document.querySelector("#" + id + " .panel-toggle");
  if (!than || !nut) return;
  than.hidden = !mo;
  nut.setAttribute("aria-expanded", mo ? "true" : "false");
  const dau = document.querySelector("#" + id + " .panel-head");
  if (dau) dau.classList.toggle("is-dong", !mo);
  if (mo) mucDangDong.delete(id);
  else mucDangDong.add(id);
}

function capNhatNutTatCa() {
  const nut = el("btnThuGonTatCa");
  if (!nut || !mucDangDong) return;
  const dongHet = MUC_KET_QUA.every((id) => mucDangDong.has(id));
  nut.textContent = t(dongHet ? "btn_mo_rong_tat_ca" : "btn_thu_gon_tat_ca");
  nut.dataset.mo = dongHet ? "1" : "0";
}

/* Một mục đang đóng vẫn phải nói nó chứa bao nhiêu — nếu không, đóng lại
   trông y hệt mất bảng. Giữ cả khoá lẫn con số trong dataset để vẽ lại
   được lúc đổi ngôn ngữ mà không phải hỏi lại phần mềm. */
function veDemMuc(id, khoa, n) {
  const o = el(id + "Dem");
  if (!o) return;
  if (!khoa || n === null || n === undefined) {
    o.textContent = "";
    delete o.dataset.khoa;
    return;
  }
  o.dataset.khoa = khoa;
  o.dataset.n = n;
  o.textContent = t(khoa, { n: n });
}

function veLaiCacDemMuc() {
  MUC_KET_QUA.forEach((id) => {
    const o = el(id + "Dem");
    if (o && o.dataset.khoa) {
      o.textContent = t(o.dataset.khoa, { n: o.dataset.n });
    }
  });
}

function khoiTaoThuGon() {
  mucDangDong = docTrangThaiThuGon();
  MUC_KET_QUA.forEach((id) => {
    const dau = document.querySelector("#" + id + " .panel-head");
    if (!dau) return;
    datMuc(id, !mucDangDong.has(id));
    /* Cả vùng tiêu đề bấm được cho dễ trúng, TRỪ vùng bên phải: bấm vào
       ô tìm kiếm mà mục đóng sập lại là một cái bẫy. Nút <button> vẫn
       giữ nguyên để bàn phím tới được. */
    dau.addEventListener("click", (ev) => {
      if (ev.target.closest && ev.target.closest(".panel-actions")) return;
      datMuc(id, mucDangDong.has(id));
      luuTrangThaiThuGon();
      capNhatNutTatCa();
    });
  });
  const nutTatCa = el("btnThuGonTatCa");
  if (nutTatCa) {
    nutTatCa.addEventListener("click", () => {
      const mo = nutTatCa.dataset.mo === "1";
      MUC_KET_QUA.forEach((id) => datMuc(id, mo));
      luuTrangThaiThuGon();
      capNhatNutTatCa();
    });
  }
  capNhatNutTatCa();
}

/* ---- Chú thích nổi dùng chung cho mọi biểu đồ ở thẻ Kết quả ----

   MỘT phần tử `#bieuDoTooltip` cho cả thẻ, không phải một cái mỗi dòng:
   dòng thì vẽ lại mỗi lần đổi cách sắp xếp, còn chú thích thì không cần.
   Nội dung dựng từ HÀM chứ không từ chuỗi chụp sẵn, để đổi ngôn ngữ xong
   rê chuột vào là ra đúng tiếng mới.

   Bàn phím tới được: dòng mang tabindex=0, focus cũng hiện chú thích và
   đặt nó ngay dưới dòng — người không dùng chuột vẫn đọc được chi tiết. */

function ganTooltip(nut, layNoiDung) {
  const hop = el("bieuDoTooltip");
  if (!hop || !nut) return;
  const hien = (x, y) => {
    const nd = layNoiDung();
    hop.innerHTML =
      `<div class="bd-tooltip-dau">${esc(nd.tieu_de)}</div>` +
      nd.dong.map(([k, v, lop]) =>
        `<div class="bd-tooltip-dong${lop ? " " + lop : ""}">` +
        `<span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("");
    hop.hidden = false;
    datViTri(x, y);
  };
  const datViTri = (x, y) => {
    /* Lệch 14px khỏi con trỏ; chạm mép phải/dưới thì lật sang bên kia
       thay vì bị cắt mất nửa. */
    const r = hop.getBoundingClientRect();
    let left = x + 14;
    let top = y + 14;
    if (left + r.width > window.innerWidth - 8) left = x - r.width - 14;
    if (top + r.height > window.innerHeight - 8) top = y - r.height - 14;
    hop.style.left = Math.max(8, left) + "px";
    hop.style.top = Math.max(8, top) + "px";
  };
  const an = () => { hop.hidden = true; };
  nut.addEventListener("mouseenter", (ev) => hien(ev.clientX, ev.clientY));
  nut.addEventListener("mousemove", (ev) => {
    if (!hop.hidden) datViTri(ev.clientX, ev.clientY);
  });
  nut.addEventListener("mouseleave", an);
  nut.addEventListener("focus", () => {
    const r = nut.getBoundingClientRect();
    hien(r.left + Math.min(r.width / 2, 240), r.bottom - 6);
  });
  nut.addEventListener("blur", an);
}

function phanTramTron(tu, mau) {
  /* Một chữ số thập phân, dấu phẩy kiểu Việt; mẫu 0 thì không chia. */
  if (!mau) return "0";
  return soThapPhan(Math.round((tu / mau) * 1000) / 10);
}

/* ---- Tóm tắt lần xếp (dải số lớn đầu thẻ) ----

   Năm câu người quản trị hỏi đầu tiên sau mỗi lần chạy. Trước đây câu
   trả lời nằm rải ở năm mục, phần lớn đóng sẵn, và phải tự cộng trừ.
   Mọi con số lấy từ ĐÚNG hàm mà mục chi tiết bên dưới dùng — ô tóm tắt
   và mục chi tiết không bao giờ được nói hai con số khác nhau.

   Màu trạng thái (đỏ/vàng/xanh) CHỈ dùng cho ô có nghĩa tốt-xấu, và luôn
   đi kèm ký hiệu + chữ, không bao giờ màu trơn. Bấm một ô là mở và cuộn
   tới mục giải thích con số đó. */

function moMucVaCuon(id) {
  const panel = el(id);
  if (!panel || panel.hidden || !mucDangDong) return;
  datMuc(id, true);
  luuTrangThaiThuGon();
  capNhatNutTatCa();
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function loadTomTatKetQua() {
  const dai = el("tomTatKetQua");
  if (!dai) return;
  Promise.all([
    callApi("get_em_chua_co_cho"),
    callApi("get_phan_bo_nguyen_vong"),
    callApi("get_club_fill_stats"),
    callApi("get_suat_du_tru"),
    callApi("get_last_run_info"),
  ]).then(([cho, nv, lap, duTru, lanChay]) => {
    const luoi = el("tomTatLuoi");
    clear(luoi);
    const tong = cho.ok ? cho.data.tong_hoc_sinh : 0;
    if (!tong) { dai.hidden = true; return; }
    dai.hidden = false;

    const trangTay = cho.data.so_em;
    const daXep = tong - trangTay;
    const o = [];

    o.push({
      muc: "dsXepPanel",
      nhan: t("kpi_da_xep"),
      so: `${daXep}/${tong}`,
      phu: t("kpi_da_xep_phu", { p: phanTramTron(daXep, tong) }),
    });

    if (nv.ok && nv.data.tong_da_xep) {
      const d = nv.data;
      const dem = (h) => (d.phan_bo.find((x) => x.hang === h && !x.gop) || {}).so_em || 0;
      const top3 = dem(1) + dem(2) + dem(3);
      o.push({
        muc: "nvPanel",
        nhan: t("kpi_nv1"),
        so: phanTramTron(dem(1), d.tong_da_xep) + "%",
        phu: t("kpi_nv1_phu", { p: phanTramTron(top3, d.tong_da_xep) }),
      });
    }

    if (lap.ok && lap.data.length) {
      let tongCho = 0;
      let trong = 0;
      lap.data.forEach((c) => {
        tongCho += c.capacity || 0;
        trong += Math.max(0, (c.capacity || 0) - (c.matched || 0));
      });
      o.push({
        muc: "fillPanel",
        nhan: t("kpi_cho_trong"),
        so: String(trong),
        phu: t("kpi_cho_trong_phu", { n: tongCho }),
        sapXep: "vang_nhat",
      });
    }

    o.push({
      muc: "chuaCoChoPanel",
      nhan: t("kpi_chua_co_cho"),
      so: String(trangTay),
      trangThai: trangTay > 0 ? "is-nguy" : "is-on",
      phu: trangTay > 0 ? t("kpi_can_xu_ly") : t("kpi_on"),
    });

    if (duTru.ok && duTru.data.length) {
      const thua = duTru.data.reduce((s, c) => s + (c.con_thua || 0), 0);
      const tongDt = duTru.data.reduce((s, c) => s + (c.reserve_capacity || 0), 0);
      o.push({
        muc: "duTruPanel",
        nhan: t("kpi_du_tru_thua"),
        so: `${thua}/${tongDt}`,
        trangThai: thua > 0 ? "is-canh" : "is-on",
        phu: thua > 0 ? t("kpi_du_tru_thua_phu") : t("kpi_on"),
      });
    }

    o.forEach((k) => {
      const nut = document.createElement("button");
      nut.type = "button";
      nut.className = "kpi-o" + (k.trangThai ? " " + k.trangThai : "");
      nut.dataset.muc = k.muc;
      const ky = k.trangThai === "is-nguy" ? "⚠ "
               : k.trangThai === "is-canh" ? "▲ "
               : k.trangThai === "is-on" ? "✓ " : "";
      nut.innerHTML =
        `<span class="kpi-nhan">${esc(k.nhan)}</span>` +
        `<span class="kpi-so">${esc(k.so)}</span>` +
        `<span class="kpi-phu">${esc(ky + k.phu)}</span>`;
      nut.title = t("kpi_bam_de_xem");
      nut.addEventListener("click", () => {
        if (k.sapXep) datCachSapXep(k.sapXep);
        moMucVaCuon(k.muc);
      });
      luoi.appendChild(nut);
    });

    const dong = el("tomTatLanChay");
    const r = lanChay.ok && lanChay.data;
    dong.textContent = r
      ? t("tom_tat_lan_chay", { luc: r.run_at || "—", seed: r.seed ?? "—" })
      : "";
  });
}

/* ---- Tỉ lệ lấp đầy theo CLB ---- */

const KHOA_SAP_XEP_LAP_DAY = "rbda_sap_xep_lap_day";
const CACH_SAP_XEP = ["buoi", "day_nhat", "vang_nhat", "choi_cao"];
let duLieuLapDay = [];

function docCachSapXep() {
  try {
    const v = window.localStorage &&
              window.localStorage.getItem(KHOA_SAP_XEP_LAP_DAY);
    if (CACH_SAP_XEP.indexOf(v) !== -1) return v;
  } catch (e) { /* không đọc được thì dùng mặc định */ }
  return "buoi";
}

function datCachSapXep(v) {
  if (CACH_SAP_XEP.indexOf(v) === -1) return;
  try {
    if (window.localStorage) window.localStorage.setItem(KHOA_SAP_XEP_LAP_DAY, v);
  } catch (e) { /* không ghi được thì thôi */ }
  const chon = el("fillSapXep");
  if (chon) chon.value = v;
  veBieuDoLapDay();
}

function loadClubFillStats() {
  callApiDocChung("get_club_fill_stats").then((res) => {
    if (!res.ok || !res.data.length) {
      duLieuLapDay = [];
      const box = el("clubFillList");
      clear(box);
      box.innerHTML = '<div class="empty-state"></div>';
      box.firstChild.textContent = t("admin_club_empty");
      veDemMuc("fillPanel", null, null);
      veBangNhuCauCLB([]);
      return;
    }
    duLieuLapDay = res.data;
    veBieuDoLapDay();
    veDemMuc("fillPanel", "dem_cau_lac_bo", res.data.length);
    veBangNhuCauCLB(res.data);
  });
}

function tiLeLap(c) {
  return c.capacity > 0 ? c.matched / c.capacity : 0;
}

/* Nhãn cần-để-ý của một CLB. Luôn là ký hiệu + chữ, không bao giờ chỉ
   là màu — người mù màu và bản in trắng đen vẫn đọc được. Chỉ gắn cho CLB
   cần người quản trị LÀM GÌ ĐÓ, mỗi CLB nhiều nhất một nhãn:
     - có chỗ mà không ai vào       -> Không ai
     - lấp chưa tới một nửa         -> Còn nhiều chỗ

   KHÔNG có nhãn "quá tải": đã thử, và trên bộ 160 em / 5 buổi CLB nào
   cũng chọi trên 4 lần, nên nhãn dán lên MỌI dòng — đánh dấu tất cả là
   không đánh dấu gì. Độ chọi đã in ở từng dòng, và "Chọi cao nhất" đưa
   các CLB đó lên đầu. */
function nhanCanDeY(c) {
  if (c.capacity > 0 && c.matched === 0) {
    return { lop: "is-nguy", chu: "⚠ " + t("fill_tag_khong_ai") };
  }
  if (c.capacity > 0 && tiLeLap(c) < 0.5) {
    return { lop: "is-thong-tin", chu: "○ " + t("fill_tag_con_nhieu") };
  }
  return null;
}

function veBieuDoLapDay() {
  const box = el("clubFillList");
  if (!box) return;
  clear(box);
  const ds = duLieuLapDay.slice();
  if (!ds.length) return;

  const cach = docCachSapXep();
  const chon = el("fillSapXep");
  if (chon) chon.value = cach;
  const nhieuBuoi = new Set(ds.map((c) => c.buoi)).size > 1;

  /* sort ổn định: hòa thì giữ thứ tự (buổi, mã) mà phần mềm trả về. */
  if (cach === "day_nhat") ds.sort((a, b) => tiLeLap(b) - tiLeLap(a));
  else if (cach === "vang_nhat") ds.sort((a, b) => tiLeLap(a) - tiLeLap(b));
  else if (cach === "choi_cao") {
    ds.sort((a, b) => (b.ti_le_choi ?? -1) - (a.ti_le_choi ?? -1));
  }

  const theoNhom = cach === "buoi" && nhieuBuoi;
  let buoiTruoc = null;
  ds.forEach((c) => {
    if (theoNhom && c.buoi !== buoiTruoc) {
      buoiTruoc = c.buoi;
      const cung = ds.filter((x) => x.buoi === c.buoi);
      const xep = cung.reduce((s, x) => s + (x.matched || 0), 0);
      const cho = cung.reduce((s, x) => s + (x.capacity || 0), 0);
      const dau = document.createElement("div");
      dau.className = "fill-nhom";
      dau.innerHTML =
        `<span class="fill-nhom-ten">${esc(nhanBuoi(c.buoi))}</span>` +
        `<span class="fill-nhom-so">${esc(t("fill_nhom_tong",
          { xep: xep, cho: cho, p: phanTramTron(xep, cho) }))}</span>`;
      box.appendChild(dau);
    }
    box.appendChild(veDongLapDay(c, nhieuBuoi && !theoNhom, nhieuBuoi));
  });
}

function veDongLapDay(c, hienChipBuoi, nhieuBuoi) {
  /* Hai đoạn LIỀN NHAU trong một máng flex, không chồng lên nhau: vàng
     = số em VÀO BẰNG SUẤT DỰ TRỮ, xanh = số em vào chỉ tiêu chung. Cộng
     lại đúng bằng tỉ lệ lấp đầy in bên phải, và khớp với cột "Diện
     trúng tuyển" trong tệp xuất ra. (Đoạn vàng vẽ theo SỐ EM ĐÃ VÀO,
     không phải chỉ tiêu dự trữ của CLB — xem tests/test_giao_dien_bieu_do.py.)

     Khe 2px giữa hai đoạn là bóng đổ lõm màu nền, KHÔNG phải margin:
     margin làm tổng bề rộng lệch khỏi tỉ lệ thật. */
  const suc = c.capacity > 0 ? c.capacity : 0;
  const duTru = Math.min(c.matched_reserve || 0, c.matched);
  const chung = Math.max(0, c.matched - duTru);
  /* Tính bề rộng từ SỐ GỐC. Làm tròn từng đoạn rồi cộng lại thì tổng có
     thể vượt 100%. */
  const phanTram = (n) => (suc > 0 ? Math.min(100, (n / suc) * 100) : 0);
  const ten = c.name || c.club_id;
  const nhan = nhanCanDeY(c);
  const coChoi = c.ti_le_choi !== null && c.ti_le_choi !== undefined;

  const row = document.createElement("div");
  row.className = "fill-row" + (nhan ? " " + nhan.lop : "");
  row.tabIndex = 0;
  row.dataset.clb = c.club_id;
  row.innerHTML =
    `<span class="fill-name" title="${esc(ten)}">${esc(ten)}</span>` +
    `<span class="fill-track">` +
    (duTru > 0
      ? `<span class="fill-bar is-reserve" style="width:${phanTram(duTru)}%"></span>`
      : "") +
    (chung > 0
      ? `<span class="fill-bar${duTru > 0 ? " is-sau" : ""}" style="width:${phanTram(chung)}%"></span>`
      : "") +
    `</span>` +
    `<span class="fill-so"><span class="fill-count">${c.matched}/${c.capacity}</span>` +
    `<span class="fill-pct">${esc(phanTramTron(c.matched, suc))}%</span></span>` +
    `<span class="fill-meta">` +
    (hienChipBuoi ? `<span class="fill-chip-buoi">${esc(nhanBuoi(c.buoi))}</span>` : "") +
    (coChoi ? `<span class="fill-choi">${esc(t("fill_choi", { x: soThapPhan(c.ti_le_choi) }))}</span>` : "") +
    (nhan ? `<span class="fill-tag ${nhan.lop}">${esc(nhan.chu)}</span>` : "") +
    `</span>`;

  ganTooltip(row, () => {
    const dong = [];
    if (nhieuBuoi) dong.push([t("th_buoi"), nhanBuoi(c.buoi)]);
    dong.push([t("tt_da_xep"), `${c.matched}/${c.capacity} · ${phanTramTron(c.matched, suc)}%`]);
    dong.push(["· " + t("legend_general"), String(chung)]);
    if (c.reserve_capacity > 0 || duTru > 0) {
      dong.push(["· " + t("legend_reserve"), `${duTru}/${c.reserve_capacity || 0}`]);
    }
    dong.push([t("legend_trong"), String(Math.max(0, suc - c.matched))]);
    dong.push([t("th_so_dang_ky"), String(c.so_dang_ky ?? "—")]);
    dong.push([t("th_dat_nv1"), String(c.so_dat_nv1 ?? "—")]);
    dong.push([t("th_ti_le_choi"), coChoi ? soThapPhan(c.ti_le_choi) + "×" : "—"]);
    if (nhan) dong.push([nhan.chu, "", "is-nhan " + nhan.lop]);
    return { tieu_de: ten, dong: dong };
  });
  return row;
}

/* ---- Theo từng câu lạc bộ: nhu cầu + danh sách thành viên ----

   Bảng này dùng CHÍNH kết quả của `get_club_fill_stats` mà mục tỉ lệ lấp
   đầy đang vẽ — một câu truy vấn, hai cách hiện. Hai đường tính song song
   cho cùng một con số là thứ sớm muộn cũng trôi khỏi nhau. */

let clbDangMo = null;      // mã câu lạc bộ đang mở danh sách, null = đóng

function soThapPhan(x) {
  /* Người Việt viết 4,35 chứ không phải 4.35. */
  return x === null || x === undefined ? "—" : String(x).replace(".", ",");
}

function veBangNhuCauCLB(ds) {
  const panel = el("clbPanel");
  if (!panel) return;
  const body = el("clbBody");
  const rong = el("clbEmpty");
  clear(body);
  panel.hidden = !ds.length;
  if (rong) rong.hidden = ds.length > 0;
  if (!ds.length) {
    veDemMuc("clbPanel", null, null);
    dongDanhSachCLB();
    return;
  }

  /* Lớp CSS RIÊNG (`.cot-buoi-clb`), không dùng chung `.cot-buoi` với
     bảng danh sách xếp CLB. `loadMatchResults` bật tắt `.cot-buoi` theo
     số buổi có trong KẾT QUẢ, còn bảng này đếm theo DANH SÁCH CÂU LẠC
     BỘ — hai quy tắc khác nhau trên cùng một lớp thì bên chạy sau thắng.
     Đã đo: trường hai buổi mà chỉ chạy một buổi thì cột Buổi ở đây biến
     mất, và bảng còn lại hai dòng không nói nổi dòng nào thuộc buổi nào. */
  const nhieuBuoi = new Set(ds.map((c) => c.buoi)).size > 1;

  ds.forEach((c) => {
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td class="cot-buoi-clb">${esc(nhanBuoi(c.buoi))}</td>` +
      `<td>${esc(c.club_id)}</td>` +
      `<td>${esc(c.name || c.club_id)}</td>` +
      `<td class="num">${esc(c.so_dang_ky)}</td>` +
      `<td class="num">${esc(c.so_dat_nv1)}</td>` +
      `<td class="num">${esc(c.capacity)}</td>` +
      `<td class="num">${esc(c.matched)}</td>` +
      `<td class="num">${esc(soThapPhan(c.ti_le_choi))}</td>` +
      `<td></td>`;
    tr.querySelector(".cot-buoi-clb").hidden = !nhieuBuoi;

    const nut = document.createElement("button");
    nut.className = "btn btn-ghost";
    nut.dataset.clb = c.club_id;
    nut.textContent = t(clbDangMo === c.club_id
                        ? "btn_dong_danh_sach" : "btn_xem_danh_sach");
    nut.addEventListener("click", () => {
      if (clbDangMo === c.club_id) dongDanhSachCLB();
      else moDanhSachCLB(c.club_id);
    });
    tr.lastElementChild.appendChild(nut);
    body.appendChild(tr);
  });
  document.querySelectorAll("#clbTable thead .cot-buoi-clb")
    .forEach((o) => { o.hidden = !nhieuBuoi; });
  veDemMuc("clbPanel", "dem_cau_lac_bo", ds.length);
}

/* Nhãn nút phải theo trạng thái thật. Bản đầu chỉ ẩn vùng danh sách đi
   mà không đụng tới nút, nên đóng xong nút vẫn ghi "Đóng danh sách" —
   một nút nói dối về việc bấm nó sẽ làm gì. */
function capNhatNhanNutDanhSach() {
  document.querySelectorAll("#clbBody tr").forEach((tr) => {
    const nut = tr.querySelector("button");
    if (nut) {
      nut.textContent = t(nut.dataset.clb === clbDangMo
                          ? "btn_dong_danh_sach" : "btn_xem_danh_sach");
    }
  });
}

function dongDanhSachCLB() {
  clbDangMo = null;
  const vung = el("clbDsArea");
  if (vung) vung.hidden = true;
  capNhatNhanNutDanhSach();
}

function moDanhSachCLB(club_id) {
  callApi("get_danh_sach_clb", club_id).then((res) => {
    if (!res.ok) {
      /* Câu lạc bộ đã bị xoá ở thẻ Quản lý trong lúc danh sách của nó
         đang mở: đóng lại là đúng, còn ném một hộp lỗi đỏ lên màn hình
         thì đang báo động về một việc người dùng vừa CỐ Ý làm. Lỗi khác
         (đọc cơ sở dữ liệu hỏng) thì vẫn phải nói. */
      const ma_loi = (res.errors && res.errors[0] && res.errors[0].code) || "";
      if (ma_loi === "club_not_found") dongDanhSachCLB();
      else showErrorToast(res.errors);
      return;
    }
    clbDangMo = club_id;
    const d = res.data;
    const vung = el("clbDsArea");
    el("clbDsTieuDe").textContent =
      t("clb_ds_tieu_de", { ten: d.club_name || d.club_id });

    const body = el("clbDsBody");
    clear(body);
    d.thanh_vien.forEach((em) => {
      const dien = nhanDien(em.matched_tier);
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(em.student_id)}</td>` +
        `<td>${esc(em.name || "")}</td>` +
        `<td class="num">${esc(em.rank_in_student_pref ?? "—")}</td>` +
        `<td>${esc(dien)}</td>` +
        `<td>${esc(em.reserve_group || "")}</td>`;
      body.appendChild(tr);
    });
    if (vung) vung.hidden = false;
    capNhatNhanNutDanhSach();
  });
}

/* ---- Mức đáp ứng nguyện vọng ---- */

function loadPhanBoNguyenVong() {
  const panel = el("nvPanel");
  if (!panel) return;
  callApi("get_phan_bo_nguyen_vong").then((res) => {
    if (!res.ok || !res.data.tong_da_xep) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const d = res.data;
    const box = el("nvCot");
    clear(box);

    const hang = d.phan_bo.slice();
    if (d.khong_ro) hang.push({ hang: null, gop: false, so_em: d.khong_ro });
    const lonNhat = Math.max(1, ...hang.map((h) => h.so_em));

    /* Câu tiêu điểm: con số nhà trường bị hỏi đầu tiên khi công bố. */
    const dem = (n) => (d.phan_bo.find((x) => x.hang === n && !x.gop) || {}).so_em || 0;
    const tieuDiem = el("nvTieuDiem");
    if (tieuDiem) {
      tieuDiem.textContent = t("nv_tieu_diem", {
        p1: phanTramTron(dem(1), d.tong_da_xep),
        p3: phanTramTron(dem(1) + dem(2) + dem(3), d.tong_da_xep),
      });
    }

    /* MỘT mảng cho cả thanh ngang lẫn vành khuyên — hai hình của cùng một
       phép đếm không được phép tính riêng rồi trôi khỏi nhau. */
    let luyKe = 0;
    const muc = hang.map((h) => {
      if (h.hang !== null) luyKe += h.so_em;
      return {
        hang: h.hang,
        nhan: h.hang === null ? t("nv_khong_ro")
            : h.gop ? t("nv_hang_gop", { n: h.hang })
            : t("nv_hang", { n: h.hang }),
        so_em: h.so_em,
        ti_le: d.tong_da_xep
          ? Math.round((h.so_em / d.tong_da_xep) * 1000) / 10 : 0,
        luy_ke: h.hang === null ? null : luyKe,
      };
    });
    const noiDungTooltip = (m) => () => {
      const ds = [[t("tt_so_cho"), String(m.so_em)],
                  [t("tt_ti_le"), soThapPhan(m.ti_le) + "%"]];
      if (m.luy_ke !== null) {
        ds.push([t("tt_luy_ke"), phanTramTron(m.luy_ke, d.tong_da_xep) + "%"]);
      }
      return { tieu_de: m.nhan, dong: ds };
    };

    muc.forEach((m) => {
      const dong = document.createElement("div");
      /* Cùng lớp màu với cung tương ứng trên vành khuyên: thanh và cung
         của một thứ hạng phải trông là một thứ. */
      dong.className = "do-phu-dong nv-dong " +
        (m.hang === null ? "is-khong-ro" : "is-h" + m.hang) +
        (m.hang === 1 ? " is-nv1" : "");
      dong.tabIndex = 0;
      dong.innerHTML =
        `<span class="do-phu-nhan">${esc(m.nhan)}</span>` +
        `<span class="do-phu-track"><span class="do-phu-bar" ` +
        `style="width:${(m.so_em / lonNhat) * 100}%"></span></span>` +
        `<span class="do-phu-so-em">${esc(m.so_em)}` +
        `<span class="nv-ti-le"> · ${esc(soThapPhan(m.ti_le))}%</span></span>`;
      ganTooltip(dong, noiDungTooltip(m));
      box.appendChild(dong);
    });
    veDonutNguyenVong(muc, d.tong_da_xep, noiDungTooltip,
                      tieuDiem ? tieuDiem.textContent : "");
    veDemMuc("nvPanel", "dem_cho", d.tong_da_xep);
  });
}

/* Vành khuyên: phần của từng thứ hạng nguyện vọng trên TỔNG số chỗ đã xếp.

   Vì sao được dùng hình tròn ở đây mà không ở chỗ khác: đây là phần-trên-
   tổng thật (các phần cộng đúng bằng tong_da_xep), chỉ 4–5 phần. Suất dự
   trữ/chung chỉ có 2 phần — hình tròn 2 miếng là một ô số đội lốt biểu đồ;
   còn trộn "em chưa có chỗ" vào đây là sai mẫu số ở trường nhiều buổi (thứ
   hạng đếm theo CHỖ, trắng tay đếm theo EM).

   Màu là dải TUẦN TỰ một sắc xanh, đậm nhất = nguyện vọng 1: thứ hạng có
   thứ tự, nên không dùng màu phân loại. Hai bậc nhạt dưới 3:1 trên nền
   trắng, nên chú giải kèm số là bắt buộc, không phải trang trí.

   Vẽ bằng stroke-dasharray trên <circle>: không cần thư viện (ứng dụng
   chạy offline), và độ dài cung đọc thẳng được từ thuộc tính — test đo
   trên đó. Khe 2px màu nền giữa các cung trừ vào chính cung, nên tổng
   cung + khe đúng bằng chu vi. */
function veDonutNguyenVong(muc, tong, noiDungTooltip, moTa) {
  const hop = el("nvDonut");
  const chuGiai = el("nvDonutChuGiai");
  if (!hop || !chuGiai) return;
  clear(hop);
  clear(chuGiai);
  if (!tong) return;

  const R = 70;
  const DAY = 22;
  const CHU_VI = 2 * Math.PI * R;
  const coSo = muc.filter((m) => m.so_em > 0);
  const KHE = coSo.length > 1 ? 2 : 0;
  const lopMau = (m) => (m.hang === null ? "is-khong-ro" : "is-h" + m.hang);

  const NS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", "0 0 180 180");
  svg.setAttribute("class", "nv-donut-svg");
  svg.setAttribute("role", "img");
  svg.setAttribute("aria-labelledby", "nvDonutTieuDe");
  const tieuDe = document.createElementNS(NS, "title");
  tieuDe.id = "nvDonutTieuDe";
  tieuDe.textContent = moTa || t("nv_title");
  svg.appendChild(tieuDe);

  /* Máng nền: một vòng mảnh để vành khuyên vẫn có hình khi một cung nhạt
     nằm sát nền trắng. */
  const mang = document.createElementNS(NS, "circle");
  mang.setAttribute("cx", "90");
  mang.setAttribute("cy", "90");
  mang.setAttribute("r", String(R));
  mang.setAttribute("class", "nv-donut-mang");
  svg.appendChild(mang);

  let batDau = 0;
  coSo.forEach((m) => {
    const dai = (m.so_em / tong) * CHU_VI;
    const cung = document.createElementNS(NS, "circle");
    cung.setAttribute("cx", "90");
    cung.setAttribute("cy", "90");
    cung.setAttribute("r", String(R));
    cung.setAttribute("class", "nv-cung " + lopMau(m));
    cung.setAttribute("stroke-width", String(DAY));
    cung.setAttribute("stroke-dasharray",
      `${Math.max(0, dai - KHE)} ${CHU_VI - Math.max(0, dai - KHE)}`);
    cung.setAttribute("stroke-dashoffset", String(-batDau));
    // Vòng tròn SVG bắt đầu ở 3 giờ; xoay để cung đầu (NV1) mở từ 12 giờ.
    cung.setAttribute("transform", "rotate(-90 90 90)");
    cung.setAttribute("tabindex", "0");
    cung.dataset.soEm = m.so_em;
    batDau += dai;

    const bat = () => {
      svg.classList.add("is-dang-chi");
      cung.classList.add("is-dang-chi");
    };
    const tat = () => {
      svg.classList.remove("is-dang-chi");
      cung.classList.remove("is-dang-chi");
    };
    cung.addEventListener("mouseenter", bat);
    cung.addEventListener("focus", bat);
    cung.addEventListener("mouseleave", tat);
    cung.addEventListener("blur", tat);
    ganTooltip(cung, noiDungTooltip(m));
    svg.appendChild(cung);
  });

  /* Giữa vành: % nguyện vọng 1 — con số mở đầu của cả mục, khớp ô tóm tắt. */
  const nv1 = muc.find((m) => m.hang === 1);
  const giua = document.createElementNS(NS, "text");
  giua.setAttribute("x", "90");
  giua.setAttribute("y", "90");
  giua.setAttribute("class", "nv-donut-so");
  giua.textContent = phanTramTron(nv1 ? nv1.so_em : 0, tong) + "%";
  svg.appendChild(giua);
  const duoi = document.createElementNS(NS, "text");
  duoi.setAttribute("x", "90");
  duoi.setAttribute("y", "112");
  duoi.setAttribute("class", "nv-donut-nhan");
  duoi.textContent = t("nv_donut_tam");
  svg.appendChild(duoi);
  hop.appendChild(svg);

  /* Chú giải chỉ mang màu + tên + phần trăm. Số chỗ đã in ở thanh ngang
     ngay bên cạnh; nhắc lại lần hai chỉ thêm việc đọc. */
  muc.forEach((m) => {
    const li = document.createElement("li");
    li.innerHTML =
      `<span class="nv-o-mau ${lopMau(m)}"></span>` +
      `<span class="nv-cg-nhan">${esc(m.nhan)}</span>` +
      `<span class="nv-cg-so">${esc(soThapPhan(m.ti_le))}%</span>`;
    chuGiai.appendChild(li);
  });
}

/* ---- Em chưa có chỗ nào ---- */

function loadEmChuaCoCho() {
  const panel = el("chuaCoChoPanel");
  if (!panel) return;
  callApi("get_em_chua_co_cho").then((res) => {
    if (!res.ok) { panel.hidden = true; return; }
    const d = res.data;
    const body = el("chuaCoChoBody");
    const rong = el("chuaCoChoEmpty");
    clear(body);

    /* Chua chay lan nao thi KHONG hien mot bang trong reo "moi em deu co
       cau lac bo" — cau do se sai va sai theo huong yen long nhat. */
    panel.hidden = !d.tong_hoc_sinh;
    if (rong) rong.hidden = d.so_em > 0;

    d.danh_sach.forEach((em) => {
      const khai = em.da_khai.length
        ? em.da_khai.map((k) =>
            `<span class="club-tag">${esc(k.ten_clb || k.club_id)}` +
            (k.ti_le_choi === null || k.ti_le_choi === undefined ? ""
             : ` <span class="nv-ti-le">${esc(soThapPhan(k.ti_le_choi))}</span>`) +
            `</span>`).join(" ")
        : `<span class="tkb-trong">${esc(t("chua_khai_gi"))}</span>`;
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(em.student_id)}</td>` +
        `<td>${esc(em.name || "")}</td>` +
        `<td class="num">${esc(em.so_nguyen_vong)}</td>` +
        `<td>${khai}</td>`;
      body.appendChild(tr);
    });
    veDemMuc("chuaCoChoPanel", "dem_hoc_sinh", d.so_em);
  });
}

/* ---- Suất dự trữ dùng tới đâu ---- */

function loadSuatDuTru() {
  const panel = el("duTruPanel");
  if (!panel) return;
  callApi("get_suat_du_tru").then((res) => {
    if (!res.ok || !res.data.length) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const ds = res.data;
    const nhieuBuoi = new Set(ds.map((c) => c.buoi)).size > 1;
    const body = el("duTruBody");
    clear(body);
    let tong_thua = 0;
    ds.forEach((c) => {
      tong_thua += c.con_thua || 0;
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td class="cot-buoi-clb">${esc(nhanBuoi(c.buoi))}</td>` +
        `<td>${esc(c.name || c.club_id)}</td>` +
        `<td>${esc(c.reserve_group || "")}</td>` +
        `<td class="num">${esc(c.reserve_capacity)}</td>` +
        `<td class="num">${esc(c.nhom_dang_ky)}</td>` +
        `<td class="num">${esc(c.da_dung)}</td>` +
        `<td class="num${c.con_thua > 0 ? " is-canh-bao-o" : ""}">` +
        `${esc(c.con_thua)}</td>`;
      tr.querySelector(".cot-buoi-clb").hidden = !nhieuBuoi;
      body.appendChild(tr);
    });
    document.querySelectorAll("#duTruTable thead .cot-buoi-clb")
      .forEach((o) => { o.hidden = !nhieuBuoi; });
    const rong = el("duTruEmpty");
    if (rong) rong.hidden = true;
    // Con so dang nhin la SUAT BI BO PHI, khong phai so cau lac bo.
    veDemMuc("duTruPanel", "dem_suat", tong_thua);
  });
}

function loadMatchResults(search) {
  callApiMoiNhat("ket_qua", "get_match_results", search || "").then((res) => {
    const body = el("resultsTableBody");
    const empty = el("resultsEmptyState");
    const badge = el("unmatchedBadge");
    clear(body);
    /* Dung ca bang trong mot DocumentFragment roi gan MOT lan: gan tung
       dong vao bang dang hien la trinh duyet tinh lai bo cuc moi dong —
       voi 400-800 dong va moi lan go phim tim kiem, do la cai giat. */
    const manh = document.createDocumentFragment();

    if (!res.ok || !res.data.length) {
      empty.hidden = false;
      badge.hidden = true;
      veDemMuc("dsXepPanel", null, null);
      capNhatChonHs();
      return;
    }
    empty.hidden = true;

    /* NHIỀU BUỔI: một em có MỘT dòng cho MỖI buổi, kể cả buổi em không
       có suất. Giữ nguyên cách hiện thì bảng này phồng lên gấp số buổi
       (160 em × 5 buổi = 800 dòng, phần lớn là ô trống) và huy hiệu
       "chưa được xếp" đếm số Ô TRỐNG chứ không phải số EM trắng tay —
       593 thay vì 38, một con số vừa sai vừa đáng sợ.

       Nên ở chế độ nhiều buổi, bảng này chỉ liệt kê chỗ đã xếp THẬT, còn
       "em nào chưa có gì" đọc ở bảng Độ phủ ngay phía trên — chỗ con số
       đó có đúng nghĩa. */
    const dsBuoi = new Set(res.data.map((r) => r.buoi));
    const nhieuBuoi = dsBuoi.size > 1;
    let dong = nhieuBuoi ? res.data.filter((r) => r.club_id) : res.data;
    /* Truong nhieu buoi chi liet ke cho DA XEP, nen em khong duoc xep o
       buoi nao thi khong co dong nao de danh dau. "Hien ca em chua duoc
       xep" them MOT dong trong cho moi em nhu vay (khong lap theo buoi). */
    el("hienCaEmChuaXepHang").hidden = !nhieuBuoi;
    if (nhieuBuoi && el("hienCaEmChuaXep").checked) {
      const coCho = new Set(dong.map((r) => r.student_id));
      const daThem = new Set();
      res.data.forEach((r) => {
        if (!coCho.has(r.student_id) && !daThem.has(r.student_id)) {
          daThem.add(r.student_id);
          /* Dong dai dien cho CA TUAN — o buoi ghi "Ca tuan", khong ghi
             buoi cua dong goc (de doc thanh "chi truot thu Hai"). */
          dong.push(Object.assign({}, r, { caTuan: true }));
        }
      });
      dong.sort((a, b) => (a.student_id < b.student_id ? -1 : a.student_id > b.student_id ? 1 : 0));
    }

    /* Cột "Buổi" chỉ có nghĩa khi trường dùng nhiều buổi. Một buổi mà
       vẫn hiện một cột toàn "Chưa chia buổi" là thêm việc đọc cho người
       dùng mà không thêm thông tin nào. */
    document.querySelectorAll("#view-results .cot-buoi").forEach((o) => {
      o.hidden = !nhieuBuoi;
    });

    veDemMuc("dsXepPanel", "dem_dong", dong.length);

    let nUnmatched = 0;
    dong.forEach((r) => {
      const tr = document.createElement("tr");
      const clubCell = r.club_id
        ? `<span class="club-tag">${esc(r.club_name || r.club_id)}</span>`
        : `<span class="club-tag is-empty">${esc(t("not_matched_label"))}</span>`;
      if (!r.club_id) nUnmatched++;
      const tierLabel = nhanDien(r.matched_tier);
      tr.innerHTML =
        `<td class="cot-chon"><input type="checkbox" class="chon-hs" data-student-id="${esc(r.student_id)}"` +
        `${hsDaChon.has(r.student_id) ? " checked" : ""} aria-label="${esc(r.student_id)}"></td>` +
        `<td>${esc(r.student_id)}</td><td>${esc(r.name)}</td>` +
        `<td class="cot-buoi">${esc(r.caTuan ? t("ca_tuan") : nhanBuoi(r.buoi))}</td><td>${clubCell}</td>` +
        `<td>${esc(tierLabel)}</td><td>${esc(r.rank_in_student_pref ?? "—")}</td>`;
      /* An o buoi NGAY TREN dong vua ve. Vong an `.cot-buoi` o tren chay
         TRUOC khi cac dong nay ton tai, nen truoc day o tieu de "Buoi" an
         ma o du lieu van hien — truong mot buoi thay moi cot lech sang
         phai mot o. Cung cach `.cot-buoi-clb` o hai bang ben tren. */
      tr.querySelector(".cot-buoi").hidden = !nhieuBuoi;
      manh.appendChild(tr);
    });
    body.appendChild(manh);
    capNhatChonHs(); // o "chon tat ca" phai khop voi cac dong vua ve

    if (nhieuBuoi) {
      /* Huy hiệu phải nói SỐ EM không có CLB nào cả tuần. Lấy từ đúng
         nguồn đã tính điều đó thay vì suy ra từ bảng này. */
      callApiDocChung("get_do_phu").then((dp) => {
        const n = dp.ok ? dp.data.so_em_trang_tay : 0;
        badge.hidden = n <= 0;
        if (n > 0) badge.textContent = t("unmatched_badge", { n: n });
      });
    } else if (nUnmatched > 0) {
      badge.hidden = false;
      badge.textContent = t("unmatched_badge", { n: nUnmatched });
    } else {
      badge.hidden = true;
    }
  });
}

function initResultsHandlers() {
  khoiTaoThuGon();
  if (el("fillSapXep")) {
    el("fillSapXep").addEventListener("change", (ev) => datCachSapXep(ev.target.value));
  }
  el("resultsSearch").addEventListener(
    "input",
    debounce((ev) => loadMatchResults(ev.target.value), 250)
  );
  if (el("tkbSearch")) {
    el("tkbSearch").addEventListener(
      "input",
      debounce((ev) => loadThoiKhoaBieu(ev.target.value), 250)
    );
  }
  if (el("btnChonTatCaBuoi")) {
    el("btnChonTatCaBuoi").addEventListener("click", () => {
      buoiDangChon = new Set(dsBuoiCoThe);
      goThanhXacNhanNeuCo();
      dongBoDaiVoiChip();
      veChonBuoi();
    });
  }
  ["chonBuoiTu", "chonBuoiDen"].forEach((id) => {
    if (el(id)) el(id).addEventListener("change", apDungDaiBuoi);
  });
  if (el("thamSearch")) {
    el("thamSearch").addEventListener(
      "input",
      debounce((ev) => loadSoBocTham(ev.target.value), 250)
    );
  }
  /* ---- Xuat du lieu: cac muc tuy chon ---- *
     Khong truyen ten file -> backend tu dat vao THU MUC TAI XUONG cua
     nguoi dung va tra ve duong dan DAY DU, de nguoi dung biet file nam o
     dau. Da co file cung ten thi them "(2)" nhu trinh duyet, khong ghi de.
     Chay LAN LUOT tung muc (khong song song): moi muc la mot lan ghi dia,
     va bao ket qua theo dung thu tu nguoi dung thay tren man hinh. */
  el("btnXuatTuyChon").addEventListener("click", () => {
    const muc = [];
    /* Mac dinh MOT tep Excel (export_ket_qua). Bo .csv roi chi ra khi
       danh dau "Kem cac tep CSV roi". */
    if (el("xuatKetQua").checked) {
      muc.push(["xuat_muc_ket_qua", "export_ket_qua", ["", el("xuatKemCsv").checked],
        (d) => t("toast_export_success", {
          n_hoc_sinh: d.n_hoc_sinh, path: d.path,
          n_trang: d.trang.length, trang: d.trang.join(", "),
        }) + (d.csv_path
          ? "\n" + t("xuat_kq_kem_csv", { path: d.csv_path, n_club_files: d.n_club_files })
          : "") + (d.loi_csv
          ? "\n" + t("xuat_kq_csv_loi", { errors: trErrs([d.loi_csv]).join("; ") })
          : "")]);
    }
    if (el("xuatDauVao").checked) {
      muc.push(["xuat_muc_dau_vao", "export_du_lieu_dau_vao", [""],
        (d) => t("xuat_kq_dau_vao", { path: d.path }) +
          (d.n_thi_ngoai_nv ? "\n" + t("xuat_kq_dau_vao_thieu", { n: d.n_thi_ngoai_nv }) : "") +
          (d.n_ten_doi ? "\n" + t("xuat_kq_ten_doi", { n: d.n_ten_doi }) : "")]);
    }
    if (el("xuatThayDoi").checked && !el("xuatThayDoi").disabled) {
      muc.push(["xuat_muc_thay_doi", "export_thay_doi_ket_qua", [""],
        (d) => t("xuat_kq_thay_doi", { n: d.n_thay_doi, path: d.path })]);
    }
    if (el("xuatHocSinh").checked && hsDaChon.size) {
      muc.push(["xuat_muc_hoc_sinh", "export_hoc_sinh_csv", [Array.from(hsDaChon).sort(), ""],
        (d) => t("xuat_kq_hoc_sinh", { n: d.n_hoc_sinh, n_dong: d.n_dong, path: d.path }),
        boHsKhongConTonTai]);
    }
    if (!muc.length) {
      showToast(t("toast_xuat_chua_chon_muc"), "error");
      return;
    }
    chayXuat(muc);
  });

  /* "Kem CSV" chi co nghia khi dang xuat ket qua. */
  el("xuatKetQua").addEventListener("change", () => {
    el("xuatKemCsv").disabled = !el("xuatKetQua").checked;
    if (!el("xuatKetQua").checked) el("xuatKemCsv").checked = false;
  });

  el("btnXuatHsDaChon").addEventListener("click", () => {
    if (!hsDaChon.size) return;
    chayXuat([["xuat_muc_hoc_sinh", "export_hoc_sinh_csv", [Array.from(hsDaChon).sort(), ""],
      (d) => t("xuat_kq_hoc_sinh", { n: d.n_hoc_sinh, n_dong: d.n_dong, path: d.path }),
      boHsKhongConTonTai]]);
  });

  el("btnBoChonHs").addEventListener("click", () => {
    hsDaChon.clear();
    document.querySelectorAll("#resultsTableBody .chon-hs").forEach((cb) => { cb.checked = false; });
    capNhatChonHs();
  });

  /* Mot o tick cho MOT EM, khong phai mot dong: truong nhieu buoi thi mot
     em co nhieu dong, bam o nao cung la chon/bo em do o moi dong. */
  el("resultsTableBody").addEventListener("change", (ev) => {
    const cb = ev.target;
    if (!cb.classList || !cb.classList.contains("chon-hs")) return;
    const sid = cb.dataset.studentId;
    if (cb.checked) hsDaChon.add(sid);
    else hsDaChon.delete(sid);
    document.querySelectorAll("#resultsTableBody .chon-hs").forEach((o) => {
      if (o.dataset.studentId === sid) o.checked = cb.checked;
    });
    capNhatChonHs();
  });

  /* "Chon tat ca" = cac em DANG HIEN (sau khi loc tim kiem), khong phai
     ca truong — dung thu nguoi dung dang nhin thay. */
  el("chonTatCaKetQua").addEventListener("change", (ev) => {
    const bat = ev.target.checked;
    document.querySelectorAll("#resultsTableBody .chon-hs").forEach((o) => {
      o.checked = bat;
      if (bat) hsDaChon.add(o.dataset.studentId);
      else hsDaChon.delete(o.dataset.studentId);
    });
    capNhatChonHs();
  });

  /* "Chon hoc sinh…" o muc Xuat: danh sach chon nam xa ben duoi, sau
     tam muc khac — dua nguoi dung toi tan noi, mo muc neu dang thu gon. */
  el("btnChonHocSinh").addEventListener("click", () => {
    const nutMo = document.querySelector('#dsXepPanel .panel-toggle');
    if (nutMo && nutMo.getAttribute("aria-expanded") === "false") nutMo.click();
    el("dsXepPanel").scrollIntoView({ behavior: "smooth", block: "start" });
    el("resultsSearch").focus({ preventScroll: true });
  });

  el("hienCaEmChuaXep").addEventListener("change", () => {
    loadMatchResults(el("resultsSearch").value);
  });

  el("btnDiToiChay").addEventListener("click", () => switchTab("pipeline"));
}

/* Tap hoc sinh da chon o the Ket qua. SONG QUA o tim kiem va qua lan ve
   lai bang: tim "An" chon 2 em, tim "Binh" chon them 1 -> xuat ca 3. */
const hsDaChon = new Set();

function capNhatChonHs() {
  const n = hsDaChon.size;
  el("hsDaChonDem").textContent = n ? t("hs_da_chon_dem", { n }) : t("hs_chua_chon");
  el("btnXuatHsDaChon").disabled = n === 0;
  el("btnBoChonHs").disabled = n === 0;
  /* O thu tu cua muc Xuat: tu danh dau khi vua chon em DAU TIEN — nguoi
     dung vua chon hoc sinh la de xuat — va khoa lai khi khong con em nao. */
  const oHs = el("xuatHocSinh");
  if (n === 0) oHs.checked = false;
  else if (oHs.disabled) oHs.checked = true;
  oHs.disabled = n === 0;
  el("xuatHocSinhDem").textContent = n ? t("xuat_hoc_sinh_dem", { n }) : t("xuat_hoc_sinh_chua_chon");
  const cac = Array.from(document.querySelectorAll("#resultsTableBody .chon-hs"));
  const dau = el("chonTatCaKetQua");
  dau.checked = cac.length > 0 && cac.every((o) => o.checked);
  dau.indeterminate = !dau.checked && cac.some((o) => o.checked);
}

/* Chay lan luot cac lan xuat; ghi ket qua vao o phan hoi (KHONG tu tat —
   duong dan tep phai doc duoc) va mot toast tom tat. Dung chung cho the
   Ket qua va the 04. */
function chayXuat(dsMuc, oPhanHoi) {
  /* Bam dup se ghi them mot bo tep "(2)": khoa moi nut xuat trong luc xuat. */
  if (khoa.dangXuat) return;
  datKhoa("dangXuat", true);
  const o = oPhanHoi || el("xuatFeedback");
  o.textContent = "";
  o.className = "save-feedback xuat-ket-qua";
  const dong = [];
  let coLoi = false;
  let cu = false;
  let duongMo = null; // tep/thu muc DAU TIEN xuat duoc -> nut "Mo thu muc"
  dsMuc
    .reduce(
      (chuoi, [khoaMuc, ham, doiSo, noi, khiLoi]) =>
        chuoi.then(() =>
          callApi(ham, ...doiSo).then((res) => {
            if (res.ok) {
              dong.push(noi(res.data));
              if (res.data.ket_qua_cu) cu = true;
              if (res.data.loi_csv) coLoi = true; // so Excel co, CSV hong: van hien duong dan
              if (!duongMo) duongMo = res.data.dir || res.data.path || null;
            } else {
              coLoi = true;
              dong.push(t("xuat_kq_loi", { muc: t(khoaMuc), errors: trErrs(res.errors).join("; ") }));
              if (khiLoi) {
                const them = khiLoi(res.errors || []);
                if (them) dong.push(them);
              }
            }
          })
        ),
      Promise.resolve()
    )
    /* Mot lan goi hong bat ngo van phai mo khoa — khong thi nut xuat bi
       khoa toi khi mo lai chuong trinh. */
    .catch((e) => { console.error(e); coLoi = true; })
    .then(() => {
      datKhoa("dangXuat", false);
      if (cu) dong.push(t("xuat_kq_cu"));
      veKetQuaXuat(o, dong, coLoi, duongMo);
      showToast(dong[0] || "", coLoi ? "error" : "success");
      if (currentTabName() === "results") veXuatPanel();
    });
}

/* Luoi an toan cho tap em da chon: em nao backend bao khong con ton tai
   thi bo khoi tap (va noi ra), de lan bam Xuat ke tiep chay duoc cho cac
   em con lai — thay vi hong mai mai cho toi khi nguoi dung tu bo chon. */
function boHsKhongConTonTai(errors) {
  const mat = [];
  errors.forEach((e) => {
    if (e && e.code === "student_not_found") {
      String((e.params && e.params.student_id) || "").split(",").forEach((x) => {
        const sid = x.trim();
        if (sid && hsDaChon.delete(sid)) mat.push(sid);
      });
    }
  });
  if (!mat.length) return "";
  document.querySelectorAll("#resultsTableBody .chon-hs").forEach((cb) => {
    cb.checked = hsDaChon.has(cb.dataset.studentId);
  });
  capNhatChonHs();
  return t("xuat_bo_hs_khong_con", { ds: mat.join(", ") });
}

/* Ghi ket qua xuat vao `o` (KHONG tu tat — duong dan phai doc duoc) kem
   nut "Mo thu muc". Dung chung cho the 02, 03, 04. */
function veKetQuaXuat(o, dong, coLoi, duongMo) {
  o.textContent = dong.join("\n");
  o.className = "save-feedback xuat-ket-qua " + (coLoi ? "is-error" : "is-success");
  if (!duongMo) return;
  const nut = document.createElement("button");
  nut.type = "button";
  nut.className = "btn btn-ghost nut-mo-thu-muc";
  nut.textContent = t("btn_mo_thu_muc");
  nut.addEventListener("click", () => {
    callApi("mo_thu_muc", duongMo).then((res) => {
      if (!res.ok) showToast(trErrs(res.errors).join("; "), "error");
    });
  });
  o.appendChild(document.createElement("br"));
  o.appendChild(nut);
}

/* Dai "ket qua co the da cu" + so dong thay doi canh o tick tuong ung. */
function veXuatPanel() {
  callApi("get_trang_thai_ket_qua").then((res) => {
    el("ketQuaCuBanner").hidden = !(res.ok && res.data.ket_qua_cu);
  });
  callApi("get_thay_doi_ket_qua").then((res) => {
    const oTick = el("xuatThayDoi");
    const dem = el("xuatThayDoiDem");
    const co = res.ok && res.data.co_lan_truoc;
    oTick.disabled = !co;
    if (!co) oTick.checked = false;
    dem.textContent = co
      ? t("xuat_thay_doi_dem", { n: res.data.dong.length })
      : t("xuat_thay_doi_chua_co");
  });
  capNhatChonHs();
}
