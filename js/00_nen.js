/* ==========================================================================
   Giao diện chính (js/00_nen.js … js/08_khoi_dong.js) — logic frontend cho kiosk Phân bổ Câu lạc bộ (RB-DA)
   ==========================================================================
   Toàn bộ giao tiếp với Python đi qua window.pywebview.api.<ten_ham>(...),
   mỗi hàm trả về Promise<{ok, data, errors}> (quy ước thống nhất ở api.py).
   Không dùng alert()/confirm() ở bất cứ đâu — thay bằng toast + xác nhận
   2 bước ngay tại chỗ (đổi label nút, yêu cầu bấm lần 2).

   Song ngữ (vi/en): mọi chuỗi hiển thị đi qua I18N.t(key, params) (xem
   i18n.js) — không hardcode chuỗi tiếng Việt/Anh trực tiếp trong file
   này. Lỗi/chi tiết bước từ backend là {code, params} (xem api.py +
   i18n_errors.py) và được dịch bằng I18N.translateError(s).
   ========================================================================== */

/* js/00_nen.js — Nền: t()/lỗi dùng chung, gọi API (mới nhất / dùng chung), thông báo,
   nút bận, trợ năng cho phần tử bấm được.

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

const t = window.I18N.t;
const trErr = window.I18N.translateError;
const trErrs = window.I18N.translateErrors;

/* ------------------------------------------------------------------ *
 * 0. TIỆN ÍCH DÙNG CHUNG
 * ------------------------------------------------------------------ */

const { apiSanSang, callApi, armTwoStepConfirm, nhaMoiNutXacNhan, choBackend } = window.RBDA;

/* Ma NOI BO cua "buoi mac dinh" (truong chi co mot buoi, hoac CLB chua
   khai buoi) — trung voi BUOI_MAC_DINH o rbda_priority_pipeline.py. Khong
   phai chu de doc: hien len man hinh thi luon qua nhanBuoi(). */
const BUOI_MAC_DINH = "__mac_dinh__";

/* Hai noi cung doc mot bao cao NGAY CUNG LUC (vd mo tab Quan ly: bang
   tai theo buoi va lich tuan deu can get_tai_theo_buoi) thi dung chung
   MOT yeu cau dang bay, khong gui hai lan. Chi dung cho ham DOC: xong la
   bo, lan goi sau van lay du lieu moi. */
const dangBayChung = {};
function callApiDocChung(name, ...args) {
  const khoa = name + JSON.stringify(args);
  if (!dangBayChung[khoa]) {
    dangBayChung[khoa] = callApi(name, ...args).finally(() => {
      delete dangBayChung[khoa];
    });
  }
  return dangBayChung[khoa];
}

/* Goi API ma CHI lan goi moi nhat tren cung `kenh` duoc tra ket qua.

   O tim kiem go tung chu, moi lan dung tay gui mot yeu cau. Tra ve
   KHONG theo thu tu gui: yeu cau cho "Ng" den SAU yeu cau cho "Nguyen"
   thi bang hien ket qua cua "Ng" duoi o dang ghi "Nguyen". Bam nhanh
   hai hoc sinh cung vay — nguoi dung dang nhin em thu hai ma man hinh
   lai do du lieu em thu nhat. Lan goi cu tra ve thi bi bo qua: Promise
   khong bao gio xong, nen doan `.then` phia sau khong chay. */
const luotGoiMoiNhat = {};
function callApiMoiNhat(kenh, name, ...args) {
  const luot = (luotGoiMoiNhat[kenh] = (luotGoiMoiNhat[kenh] || 0) + 1);
  return callApi(name, ...args).then((res) =>
    luot === luotGoiMoiNhat[kenh] ? res : new Promise(() => {}));
}

function el(id) {
  return document.getElementById(id);
}

/* Mot cau loi hien cho nguoi dung tu danh sach loi cua backend. Truoc day
   cung mot bieu thuc `t(khoa, { errors: trErrs(x).join("; ") })` duoc
   viet lai o 14 cho. */
/* Nhan "Dien trung tuyen" — hai bang ket qua tung tu viet lai phep nay. */
function nhanDien(tier) {
  return tier === "reserve" ? t("tier_reserve") : tier === "general" ? t("tier_general") : "—";
}

/* Loi JS trong mot `.then` nao do truoc day chi nam trong console — ma
   ban dong goi khong co console. Nguoi dung thay nut khong phan ung va
   khong biet vi sao. Hien no ra thanh thong bao. */
window.addEventListener("unhandledrejection", (ev) => {
  console.error(ev.reason);
  showToast(t("loi_giao_dien_ngoai_du_kien"), "error",
    [{ code: "loi_giao_dien_ngoai_du_kien", params: { detail: String(ev.reason) } }]);
});

/* Khoa nut trong luc yeu cau dang chay, MO LAI du yeu cau thanh cong,
   that bai hay nem loi.

   Truoc day cac nut luu/xuat khong khoa: bam dup "Xuat" ra hai tep, bam
   dup "Luu diem" gui hai lan. Con nut nao tu khoa thi chi mo lai o
   nhanh thanh cong — mot loi JS giua chung la nut xam vinh vien, phai
   tat app mo lai. Nut dang khoa thi bo qua lan bam (tra Promise khong
   bao gio xong, doan `.then` phia sau khong chay). */
function khiBan(nut, taoPromise) {
  if (!nut || nut.disabled) return new Promise(() => {});
  nut.disabled = true;
  return Promise.resolve()
    .then(taoPromise)
    .finally(() => { nut.disabled = false; });
}

/* Bien mot <div> bam duoc thanh thu ban phim dung duoc: Tab toi duoc,
   Enter/Space kich hoat, va trinh doc man hinh biet no la gi. Truoc day
   ca tab Nhap tai cho chi dung duoc bang chuot. `laOTick`: o tick bat/tat
   (class is-checked) — dong bo aria-checked sau MOI lan bam. */
function choBamDuoc(elm, laOTick) {
  elm.tabIndex = 0;
  elm.setAttribute("role", laOTick ? "checkbox" : "button");
  const dongBo = () => {
    if (laOTick) elm.setAttribute("aria-checked", String(elm.classList.contains("is-checked")));
  };
  dongBo();
  elm.addEventListener("click", dongBo);
  elm.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" || ev.key === " ") {
      ev.preventDefault();
      elm.click();
    }
  });
}

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

/* Thoat ca dau nhay: truoc day chi an toan GIUA hai the. Chi can mot
   cho sau nay dung esc() trong thuoc tinh (title="${esc(ten)}") la mot
   ten co dau nhay kep pha thuoc tinh ra va chen duoc ma. */
function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/* Thong bao noi (toast).
   Truoc day MOI thong bao tu tat sau 3,6 giay, ke ca loi dai va duong
   dan tep vua xuat — doc chua het cau da mat. Nay:
     - thong bao thuong: tu tat, cau cang dai thi o cang lau (4–10 giay);
     - loi, canh bao, hoac `sticky: true`: GIU cho toi khi bam ×.
   Tra ve phan tu toast de ben goi co the tu go no (vd. het che do ve lai). */
const TOAST_TOI_DA = 4;

function showToast(message, type, opts) {
  /* Tham so thu ba: mang loi (tu showErrorToast) hoac tuy chon
     {sticky, ghim, khiDong, errors}. */
  let errors = null;
  if (Array.isArray(opts)) {
    errors = opts;
    opts = {};
  } else if (opts && opts.errors) {
    errors = opts.errors;
  }
  const stack = el("toastStack");
  const toastEl = document.createElement("div");
  toastEl.className = "toast" + (type === "error" ? " is-error"
    : type === "warn" ? " is-warn"
    : type === "success" ? " is-success" : "");
  if (type === "error") toastEl.setAttribute("role", "alert");

  const noiDung = document.createElement("div");
  noiDung.className = "toast-noi-dung";
  const msg = document.createElement("span");
  msg.className = "toast-msg";
  msg.textContent = message;
  noiDung.appendChild(msg);
  /* Chi tiet ky thuat (vd. loi goc) nam rieng, dong san, mo ra khi can. */
  const coChiTiet = errors ? ganChiTietKyThuat(noiDung, errors) : false;
  toastEl.appendChild(noiDung);

  function go() {
    if (!toastEl.isConnected || toastEl.classList.contains("is-leaving")) return;
    toastEl.classList.add("is-leaving");
    setTimeout(() => toastEl.remove(), 200);
    if (opts && opts.khiDong) opts.khiDong();
  }
  toastEl.goBo = go;
  /* Bam vao thong bao cung dong duoc no, nhu truoc. */
  msg.addEventListener("click", go);

  const giu = type === "error" || type === "warn" || coChiTiet || !!(opts && opts.sticky);
  if (giu) {
    const nutDong = document.createElement("button");
    nutDong.type = "button";
    nutDong.className = "toast-close";
    nutDong.textContent = "×";
    nutDong.setAttribute("aria-label", t("btn_dong"));
    nutDong.addEventListener("click", go);
    toastEl.appendChild(nutDong);
  } else {
    const thoiGian = Math.min(10000, 4000 + 40 * String(message).length);
    setTimeout(go, thoiGian);
  }

  // `ghim`: thong bao gan voi mot trang thai dang bat (vd. che do ve lai)
  // — gioi han so thong bao KHONG duoc tu dong go no.
  if (opts && opts.ghim) toastEl.classList.add("is-ghim");
  stack.appendChild(toastEl);
  // Khong de chong thong bao che het man hinh: bo cai cu nhat.
  const dangHien = Array.from(stack.querySelectorAll(".toast:not(.is-leaving):not(.is-ghim)"));
  dangHien.slice(0, Math.max(0, dangHien.length - TOAST_TOI_DA)).forEach((x) => x.goBo());
  return toastEl;
}

function feedback(node, message, isError) {
  node.textContent = message;
  node.className = "save-feedback " + (isError ? "is-error" : "is-success");
  const lanNay = (node.dataset.lan = String(Number(node.dataset.lan || 0) + 1));
  if (message) {
    /* Loi kem chi tiet ky thuat thi de lau hon cho kip mo ra doc. */
    setTimeout(() => {
      if (node.dataset.lan === lanNay) node.textContent = "";
    }, isError ? 12000 : 5000);
  }
}

/* Chi tiet ky thuat cua loi (thong bao goc cua may, vd "database is
   locked") KHONG nam trong cau hien ra. Cau noi bang loi thuong; chi
   tiet nam trong mot muc "Chi tiet ky thuat" dong san, de nguoi sua
   loi van doc duoc ma nguoi dung khong phai doc. */
function ganChiTietKyThuat(node, errors) {
  const ds = window.I18N.errorDetails(errors);
  if (!ds.length) return false;
  const hop = document.createElement("details");
  hop.className = "chi-tiet-ky-thuat";
  const tom = document.createElement("summary");
  tom.textContent = t("chi_tiet_ky_thuat");
  const noi = document.createElement("div");
  noi.className = "chi-tiet-ky-thuat-noi";
  noi.textContent = ds.join("\n");
  hop.appendChild(tom);
  hop.appendChild(noi);
  node.appendChild(hop);
  return true;
}

/* Bao loi tu mot phan hoi API. `khoaMau` (tuy chon) boc cau loi vao mot
   cau mau co {errors}, vd "Khong xuat duoc ket qua. {errors}". */
function showErrorToast(errors, khoaMau) {
  const cau = trErrs(errors).join(" ");
  showToast(khoaMau ? t(khoaMau, { errors: cau }) : cau, "error", errors);
}

function feedbackErrors(node, errors) {
  feedback(node, trErrs(errors).join(" "), true);
  ganChiTietKyThuat(node, errors);
}

function debounce(fn, ms) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
