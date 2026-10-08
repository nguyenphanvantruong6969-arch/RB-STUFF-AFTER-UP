/* js/08_khoi_dong.js — Khởi động: init() và cổng chờ backend (choBackend ở chung.js).

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 9. KHỞI ĐỘNG
 * ------------------------------------------------------------------ */

function init() {
  window.I18N.applyStaticText();
  initLangToggle();
  initMotionToggle();
  window.addEventListener("langchange", reapplyDynamicTextForLangChange);
  initTabs();
  initPipelineHandlers();
  initResultsHandlers();
  initFallbackHandlers();
  initAdminHandlers();
  initScoringHandlers();
  loadPipelineTab(); // tab mặc định đang mở khi khởi động
}

function baoVaoOSucKhoe(cau) {
  const o = el("healthSummary");
  if (o) {
    o.className = "health-summary is-warn";
    o.textContent = cau;
  }
}

/* Cong khoi dong dung chung voi man hinh phuc hoi — xem choBackend trong
   chung.js. `get_last_run_info` chac chan co trong PipelineAPI va init()
   goi ngay, nen dung no lam phep thu "backend da goi duoc chua". */
choBackend("get_last_run_info", init, baoVaoOSucKhoe, (cau) => {
  baoVaoOSucKhoe(cau);
  const oDb = el("dbStatusLine");
  if (oDb) oDb.textContent = t("backend_khong_ket_noi");
});
