/* ==========================================================================
   recovery.js — logic cho recovery.html, màn hình CHỈ hiện khi PipelineAPI
   không khởi tạo được (app.db hỏng/mất, xem main.py + recovery.py).
   Cùng quy ước với js/*.js: mọi hàm backend trả Promise<{ok, data, errors}>,
   mọi chuỗi hiển thị qua I18N, không dùng alert()/confirm() native.
   ========================================================================== */

(function () {
  "use strict";

  const t = window.I18N.t;
  const trErr = window.I18N.translateError;

  /* callApi, nut xac nhan hai buoc va cong khoi dong: xem chung.js. */
  const { callApi, armTwoStepConfirm, choBackend } = window.RBDA;

  function el(id) {
    return document.getElementById(id);
  }

  function fmtBytes(n) {
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
    return `${(n / (1024 * 1024)).toFixed(1)} MB`;
  }

  function renderBackups(backups) {
    const tbody = el("backupsTableBody");
    const table = el("backupsTable");
    const noMsg = el("noBackupsMsg");
    tbody.innerHTML = "";
    if (!backups || backups.length === 0) {
      table.hidden = true;
      noMsg.hidden = false;
      noMsg.textContent = trErr({ code: "recovery_no_backups" });
      return;
    }
    table.hidden = false;
    noMsg.hidden = true;
    for (const b of backups) {
      const tr = document.createElement("tr");
      const tdName = document.createElement("td");
      tdName.textContent = b.name;
      const tdTime = document.createElement("td");
      tdTime.textContent = b.modified_at;
      const tdSize = document.createElement("td");
      tdSize.textContent = fmtBytes(b.size_bytes);
      tr.appendChild(tdName);
      tr.appendChild(tdTime);
      tr.appendChild(tdSize);
      tbody.appendChild(tr);
    }
  }

  /* Chi tiet ky thuat cua loi nam rieng, dong san — cau loi chi noi bang
     loi thuong. Cung cach voi app.js. */
  function ganChiTiet(errors) {
    const ds = window.I18N.errorDetails(errors);
    if (!ds.length) return;
    const hop = document.createElement("details");
    hop.className = "recovery-error-detail";
    const tom = document.createElement("summary");
    tom.textContent = t("chi_tiet_ky_thuat");
    const pre = document.createElement("pre");
    pre.textContent = ds.join("\n");
    hop.appendChild(tom);
    hop.appendChild(pre);
    el("recoveryStatus").appendChild(hop);
  }

  function showStatus(kind, text) {
    const box = el("recoveryStatus");
    box.className = `recovery-status is-${kind}`;
    box.textContent = text;
    box.hidden = false;
  }

  function clearStatus() {
    const box = el("recoveryStatus");
    box.hidden = true;
    box.textContent = "";
  }

  function setButtonsDisabled(disabled) {
    el("btnRestoreBackup").disabled = disabled;
    el("btnStartFresh").disabled = disabled;
  }

  /* Khong ghi duoc vao thu muc -> doi HAN noi dung man hinh: tieu de va
     loi dan noi dung nguyen nhan, an phan sao luu/khoi phuc (khong nut nao
     trong do giup duoc). Doi khoa data-i18n chu khong ghi thang chu, de
     bam doi ngon ngu van dich dung. */
  function veKhongGhiDuoc(khongGhi, thuMuc) {
    el("khongGhiDuoc").hidden = !khongGhi;
    el("phanKhoiPhuc").hidden = khongGhi;
    el("recoveryHeading").setAttribute("data-i18n", khongGhi ? "recovery_kg_heading" : "recovery_heading");
    el("recoveryIntro").setAttribute("data-i18n", khongGhi ? "recovery_kg_intro" : "recovery_intro");
    el("khongGhiDuocThuMuc").textContent = thuMuc || "";
    window.I18N.applyStaticText();
    document.title = t("recovery_title");
  }

  function refreshStatus() {
    return callApi("get_status").then((res) => {
      if (!res.ok) return;
      el("initErrorDetail").textContent = res.data.init_error || "";
      renderBackups(res.data.backups);
      veKhongGhiDuoc(res.data.ghi_duoc === false, res.data.thu_muc);
      return res.data;
    });
  }

  function init() {
    window.I18N.applyStaticText();
    document.title = t("recovery_title");
    window.addEventListener("langchange", () => {
      document.title = t("recovery_title");
    });

    el("btnLangToggle").addEventListener("click", () => {
      window.I18N.setLang(window.I18N.getLang() === "vi" ? "en" : "vi");
    });

    refreshStatus();

    el("btnKiemLaiThuMuc").addEventListener("click", () => {
      clearStatus();
      /* Da ghi duoc thi VAN giu man hinh nay: CSDL chua duoc mo, chuong
         trinh phai khoi dong lai moi vao duoc man hinh chinh. */
      callApi("get_status").then((res) => {
        if (!res.ok) return;
        if (res.data.ghi_duoc) {
          showStatus("success", t("recovery_kg_da_duoc"));
        } else {
          showStatus("error", t("recovery_kg_van_chua"));
        }
      });
    });

    el("btnRestoreBackup").addEventListener("click", () => {
      clearStatus();
      setButtonsDisabled(true);
      showStatus("pending", t("recovery_working"));
      callApi("restore_from_backup").then((res) => {
        setButtonsDisabled(false);
        if (res.ok) {
          showStatus("success", `${trErr(res.data.detail)} ${t("recovery_please_restart")}`);
        } else {
          showStatus("error", trErr(res.errors[0]));
          ganChiTiet(res.errors);
          refreshStatus();
        }
      });
    });

    armTwoStepConfirm(el("btnStartFresh"), () => t("confirm_start_fresh"), () => {
      clearStatus();
      setButtonsDisabled(true);
      showStatus("pending", t("recovery_working"));
      callApi("start_fresh").then((res) => {
        setButtonsDisabled(false);
        if (res.ok) {
          showStatus("success", `${trErr(res.data.detail)} ${t("recovery_please_restart")}`);
        } else {
          showStatus("error", trErr(res.errors[0]));
          ganChiTiet(res.errors);
          refreshStatus();
        }
      });
    });
  }

  /* Man hinh nay hien ra KHI CSDL DA HONG — cong khoi dong o day hong not
     thi khong con duong nao, nen no dung CHUNG mot cong voi js/*.js
     (choBackend trong chung.js). Khoi dong hai lan o day con lam nut "Bat
     dau lai voi CSDL trong" (start_fresh) chay HAI LUOT cho mot chuoi bam
     hai buoc. */
  choBackend("get_status", init,
    (cau) => showStatus("pending", cau),
    (cau) => showStatus("error", cau));
})();
