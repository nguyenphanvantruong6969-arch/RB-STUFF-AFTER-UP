/* js/07_ngon_ngu.js — Đổi ngôn ngữ: vẽ lại mọi chữ do JavaScript ghi.

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 8. NGÔN NGỮ (vi/en)
 * ------------------------------------------------------------------ */

function initLangToggle() {
  const btn = el("btnLangToggle");
  if (!btn) return;
  btn.addEventListener("click", () => {
    window.I18N.setLang(window.I18N.getLang() === "vi" ? "en" : "vi");
  });
}

/* Hiệu ứng rê chuột: bật mặc định, tắt được để máy yếu chạy nhanh hơn.
   Lưu lựa chọn vào localStorage; kho lỗi thì vẫn chạy, chỉ mất lựa chọn. */
const KHOA_HIEU_UNG = "rbda_hieu_ung";

function hieuUngDangBat() {
  try {
    return !(window.localStorage &&
             window.localStorage.getItem(KHOA_HIEU_UNG) === "tat");
  } catch (e) { return true; }
}

function apDungHieuUng(bat) {
  document.documentElement.classList.toggle("tat-hieu-ung", !bat);
  const btn = el("btnMotionToggle");
  if (btn) {
    btn.textContent = t(bat ? "hieu_ung_bat" : "hieu_ung_tat");
    btn.setAttribute("aria-pressed", bat ? "true" : "false");
  }
}

function initMotionToggle() {
  // Giữ trạng thái trong biến, không đọc lại kho mỗi lần bấm: kho hỏng
  // thì nút vẫn đổi được trong phiên này.
  let bat = hieuUngDangBat();
  apDungHieuUng(bat);
  const btn = el("btnMotionToggle");
  if (!btn) return;
  btn.addEventListener("click", () => {
    bat = !bat;
    try {
      if (window.localStorage) {
        window.localStorage.setItem(KHOA_HIEU_UNG, bat ? "bat" : "tat");
      }
    } catch (e) { /* không ghi được thì thôi */ }
    apDungHieuUng(bat);
  });
  window.addEventListener("langchange", () => apDungHieuUng(bat));
}

// Nội dung tĩnh (data-i18n) tự cập nhật qua applyStaticText(). Nội dung
// ĐỘNG (đã render dựa trên ngôn ngữ cũ) cần được yêu cầu vẽ lại — dùng
// lại loader của tab đang mở (đọc từ SQLite, rẻ) thay vì lưu cache toàn
// bộ dữ liệu. stepper/log không gắn với tab nào nên xử lý riêng.
function reapplyDynamicTextForLangChange() {
  // The run-confirmation bar (runPipelineFlow) is a safety-critical
  // dialog for an irreversible action (overwrite results / redraw STB)
  // built once from plain textContent, not data-i18n — leaving it up
  // would show a stale-language confirmation next to a freshly
  // retranslated page. Dismiss it (same as Cancel) rather than risk a
  // mismatched-language safety prompt; the user just re-clicks "Run".
  goThanhXacNhanNeuCo();
  /* Nhan nut Chay ("Dang chay…") do capNhatKhoaVanHanh() ghi, ma
     applyStaticText() vua ghi de bang nhan tinh. Ve lai tu trang thai. */
  capNhatKhoaVanHanh();
  // Che do ve lai con bat thi hien lai loi nhac bang ngon ngu moi.
  if (forceRedrawArmed) datVeLai(true);

  /* Nut dang cho xac nhan ket lai o tieng cu: applyStaticText() co y bo
     qua phan tu .is-confirming de nhan hien thi khong lech khoi trang
     thai ben trong. Ly do dung, nhung cach xu ly la NHA nut ra — giong
     het cach runConfirmBar bi go o tren. */
  nhaMoiNutXacNhan();

  /* Hang cho nap tep khong thuoc tab nao nen vong lap theo tab ben duoi
     khong cham toi. Day chinh la cho nguoi dung cham vao dau tien. */
  veHangDoi();
  veCanhBaoNhap();
  const oTomTat = el("feedbackImportAll");
  if (oTomTat) oTomTat.textContent = "";

  /* Dai the chon buoi va dong nhac di kem deu do JavaScript ghi, nen
     applyStaticText() khong dich duoc chung. Khong ve lai thi sau khi
     doi ngon ngu, dong neu dich danh buoi nao duoc giu nguyen bien mat
     hoac ket lai o tieng cu. */
  if (dsBuoiCoThe.length) {
    /* Hai o "Tu/Den" cung phai dung lai. Nhan buoi thuong la chu THO do
       truong dat nen khong doi theo ngon ngu — tru mot truong hop:
       `nhanBuoi(BUOI_MAC_DINH)` tra ve `t("buoi_chua_chia")`, co dich.
       Truong khai buoi cho mot so cau lac bo va bo trong o so khac (phan
       mem chi CANH BAO chu khong chan) thi nhan do co mat trong bo chon,
       va doi ngon ngu xong dai the noi "No session set" trong khi hai o
       van noi "Chua chia buoi". Da do that: the doi, option khong.

       `veChonBuoiDai()` goi `clear()` nen XOA luon gia tri dang chon —
       phai chup truoc va tra lai sau. KHONG dung `dongBoDaiVoiChip()` o
       day: ham do thoat som khi tap dang chon khong lien nhau, nen se bo
       hai o lai o lua chon dau tien, tuc doi ngon ngu lai lam mat trang
       thai nguoi dung vua dat. */
    veLaiDaiGiuGiaTri();
    veChonBuoi();
  }

  /* Nut "Thu gon tat ca" va cac con so o tieu de muc deu do JavaScript
     ghi, nen applyStaticText() khong cham toi. Khong ve lai thi doi ngon
     ngu xong chung ket lai o tieng cu ngay canh mot trang da dich xong. */
  capNhatNutTatCa();
  veLaiCacDemMuc();

  refreshSidebarStatus();
  if (lastRenderedSteps) renderSteps(lastRenderedSteps);
  if (lastRenderedTopErrors) showLog(lastRenderedTopErrors);

  const tab = currentTabName();
  if (tab === "pipeline") {
    refreshDashboardStats();
    refreshStbLockLine();
    loadHealthReport();
    if (!el("historyTable").hidden) loadRunHistory();
  } else if (tab === "results") {
    loadResultsTab();
  } else if (tab === "admin") {
    /* Ve lai tu CSDL xoa sach o da tick — nguoi dung dang chon 30 em de
       gan nhom du tru, doi ngon ngu la mat het. Chup lai roi tick lai. */
    const daTick = new Set(Array.from(
      document.querySelectorAll(".admin-row-checkbox:checked")
    ).map((cb) => cb.dataset.studentId));
    loadAdminTab(true).then(() => {
      document.querySelectorAll(".admin-row-checkbox").forEach((cb) => {
        if (daTick.has(cb.dataset.studentId)) cb.checked = true;
      });
    });
  } else if (tab === "scoring") {
    loadScoringOverview();
    if (currentScoringClub) {
      /* Diem da go nhung CHUA LUU nam trong o nhap, khong nam trong
         CSDL. Nap lai tu CSDL la xoa mat cong giao vien vua go. */
      const daGo = {};
      document.querySelectorAll("#scoringTableBody .score-input").forEach((o) => {
        daGo[o.dataset.studentId] = o.value;
      });
      openScoringClub(currentScoringClub).then(() => {
        document.querySelectorAll("#scoringTableBody .score-input").forEach((o) => {
          if (o.dataset.studentId in daGo) o.value = daGo[o.dataset.studentId];
        });
      });
    }
  } else if (tab === "fallback") {
    /* Truoc day bo qua tab nay vi cho rang chi co ten CLB (du lieu). Sai:
       nut "Bo", nhan phan trang, nhan buoi va the "da thi/da xep" deu la
       chu giao dien, va ket lai o ngon ngu cu. Ve lai tu TRANG THAI DANG
       CO tren man hinh (o da tick, thu tu dang xep), khong nap lai CSDL,
       de khong mat thao tac chua luu. */
    loadFallbackStudentList();
    if (currentFallbackStudent) {
      const daTick = Array.from(
        document.querySelectorAll("#testSelectionGrid .option-row.is-checked")
      ).map((r) => r.dataset.clubId);
      renderTestSelectionGrid(daTick);
      renderRankingSourceGrid();
      renderRankingList();
    }
  }
}
