/* js/01_khung.js — Khung: điều hướng thẻ và thanh bên (trạng thái CSDL, lần chạy cuối).

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 1. ĐIỀU HƯỚNG TAB
 * ------------------------------------------------------------------ */

/* Goi TRE (qua ham mui ten), khong tham chieu thang: cac ham nap nam o
   tep js/ nap SAU tep nay, nen luc dong nay chay chung chua ton tai. */
const TAB_LOADERS = {
  pipeline: () => loadPipelineTab(),
  results: () => loadResultsTab(),
  fallback: () => loadFallbackTab(),
  admin: () => loadAdminTab(),
  scoring: () => loadScoringTab(),
};

function initTabs() {
  const navItems = document.querySelectorAll(".nav-item");
  navItems.forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });
}

function currentTabName() {
  const active = document.querySelector(".nav-item.is-active");
  return active ? active.dataset.tab : "pipeline";
}

function switchTab(tabName) {
  /* Roi the 03 khi con thay doi chua luu: phai bam hai lan (xem
     roiDiNeuDuoc). Cac the khac khong giu gi chua luu. */
  if (currentTabName() === "fallback" && tabName !== "fallback" &&
      typeof roiDiNeuDuoc === "function") {
    roiDiNeuDuoc(() => doiThe(tabName), "the:" + tabName);
    return;
  }
  doiThe(tabName);
}

function doiThe(tabName) {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    const dangMo = btn.dataset.tab === tabName;
    btn.classList.toggle("is-active", dangMo);
    /* Trinh doc man hinh khong thay mau nen: noi thang the nao dang mo. */
    if (dangMo) btn.setAttribute("aria-current", "page");
    else btn.removeAttribute("aria-current");
  });
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("is-active", view.id === "view-" + tabName);
  });
  const loader = TAB_LOADERS[tabName];
  if (loader) loader();
}

/* ------------------------------------------------------------------ *
 * 2. SIDEBAR: TRẠNG THÁI DB / LẦN CHẠY GẦN NHẤT
 * ------------------------------------------------------------------ */

function refreshSidebarStatus() {
  callApi("get_last_run_info").then((res) => {
    const line = el("lastRunLine");
    if (res.ok && res.data) {
      line.textContent = t("last_run_line", {
        run_at: res.data.run_at,
        seed: res.data.seed,
        n_matched: res.data.n_matched,
        n_total: res.data.n_total,
      });
      napHatGiongLanTruoc(res.data);
    } else {
      line.textContent = t("never_run");
    }
  });
  el("dbStatusLine").textContent = t("db_connected");
  /* Noi thang app dang ve cua so bang duong nao. Khong co dong nay thi
     phai mo Task Manager moi biet — va khi khong biet thi khong ai sua. */
  const oCheDo = el("cheDoHienThi");
  if (oCheDo) {
    const duPhong = window.__CHE_DO_HIEN_THI === "trinh_duyet";
    oCheDo.textContent = t(duPhong ? "display_browser" : "display_native");
    oCheDo.classList.toggle("is-fallback", duPhong);
  }
}
