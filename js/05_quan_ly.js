/* js/05_quan_ly.js — Thẻ 04 — Quản lý CLB & dự trữ, cùng phần nhiều buổi dùng chung (chọn buổi,
   lịch tuần, bảng tải, thời khoá biểu, độ phủ).

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 6. TAB 4 — QUẢN LÝ CLUB & DỰ TRỮ
 * ------------------------------------------------------------------ */

let adminStudentPage = 1;
const ADMIN_PAGE_SIZE = 50;

/* Da co ket qua chay chua — quyet dinh nhan xac nhan cua hai nut xoa
   noi ro "mat ca ket qua da chay" hay khong. Doc mot lan luc mo tab
   vi armTwoStepConfirm goi nhan dong bo, khong cho duoc promise. */
let adminCoKetQua = false;

/* ------------------------------------------------------------------ *
 * 8b. NHIỀU BUỔI SINH HOẠT TRONG TUẦN
 * ------------------------------------------------------------------ *
 * Toàn bộ phần này TỰ ẨN khi trường chưa khai buổi nào. Một trường chỉ
 * tổ chức một buổi phải thấy đúng màn hình như trước — không ai bị bắt
 * học một khái niệm mình chưa dùng tới.
 * ------------------------------------------------------------------ */

/* Giu dung con so phia Python (rbda_priority_pipeline.py). Hai noi cung
   mot tran, va test canh chung khop nhau. */
const TRAN_NGUYEN_VONG_MOI_BUOI = 10;
const TRAN_CLB_THI_MOI_BUOI = 5;

/* Buoi cua mot CLB, tra tu danh sach da nap san — khong goi them API. */
/* Tra bang, khong quet mang: ham nay chay cho MOI o da tick o moi cu
   bam, nen `find` tren ca danh sach CLB thanh binh phuong. */
function clubBuoi(clubId) {
  return clubId in buoiCuaClb ? buoiCuaClb[clubId] : null;
}

function nhanBuoi(buoi) {
  if (!buoi || buoi === BUOI_MAC_DINH) return t("buoi_chua_chia");
  return buoi;
}

/* Ba mức tải, cùng ngưỡng dùng cho cả bảng lẫn lịch tuần.
   Mốc nằm ở 1,0 vì tỉ lệ chọi là SỐ EM trên SỐ CHỖ: trên 1 là chắc chắn
   có em trượt, dưới 1 là chắc chắn có chỗ bỏ không. Dải 0,95–1,05 gọi là
   "vừa đủ" để một buổi cân bằng không bị tô cảnh báo chỉ vì lệch vài em.

   Ngưỡng đầu tiên viết là 0,8 — sai: một buổi 0,88× (12% số chỗ bỏ
   trống) bị gán nhãn "Vừa đủ", đúng lúc nó là buổi nên dời CLB sang. */
function mucTai(tiLe) {
  if (tiLe === null || tiLe === undefined) return null;
  if (tiLe > 1.05) return { lop: "is-qua-tai", nhan: t("tai_buoi_qua_tai") };
  if (tiLe >= 0.95) return { lop: "is-vua-du", nhan: t("tai_buoi_vua_du") };
  return { lop: "is-con-trong", nhan: t("tai_buoi_con_trong") };
}

function loadBuoiOptions() {
  callApiDocChung("get_danh_sach_buoi").then((res) => {
    const list = el("buoiOptions");
    if (!list) return;
    clear(list);
    if (!res.ok) return;
    res.data.ds_buoi
      .filter((b) => b !== res.data.buoi_mac_dinh)
      .forEach((b) => {
        const opt = document.createElement("option");
        opt.value = b;
        list.appendChild(opt);
      });
  });
}

function loadTaiTheoBuoi() {
  const panel = el("taiBuoiPanel");
  if (!panel) return;
  callApiDocChung("get_tai_theo_buoi").then((res) => {
    const body = el("taiBuoiBody");
    clear(body);
    /* Một buổi thì bảng này không nói được gì: cả trường chỉ có một
       dòng, và "dời CLB sang buổi vắng" không còn là lời khuyên nào. */
    if (!res.ok || res.data.length < 2) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    res.data.forEach((r) => {
      const muc = mucTai(r.ti_le_choi);
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(nhanBuoi(r.buoi))}</td>` +
        `<td class="num">${esc(r.so_clb)}</td>` +
        `<td class="num">${esc(r.tong_cho)}</td>` +
        `<td class="num">${esc(r.so_hoc_sinh)}</td>` +
        `<td class="num">${r.ti_le_choi === null ? "—" : esc(r.ti_le_choi) + "×"}</td>` +
        `<td>${muc ? `<span class="chip-tai ${muc.lop}">${esc(muc.nhan)}</span>` : ""}</td>`;
      body.appendChild(tr);
    });
  });
}

function loadLichTuan() {
  const panel = el("lichTuanPanel");
  if (!panel) return;
  Promise.all([
    callApiDocChung("get_tai_theo_buoi"),
    callApiDocChung("get_club_fill_stats"),
  ]).then(([tai, fill]) => {
    const box = el("lichTuan");
    clear(box);
    if (!tai.ok || tai.data.length < 2 || !fill.ok) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;

    const theoBuoi = {};
    fill.data.forEach((c) => {
      (theoBuoi[c.buoi] = theoBuoi[c.buoi] || []).push(c);
    });

    tai.data.forEach((b) => {
      const muc = mucTai(b.ti_le_choi);
      const cot = document.createElement("div");
      cot.className = "lich-cot";
      cot.innerHTML =
        `<div class="lich-dau ${muc && muc.lop === "is-qua-tai" ? "is-qua-tai" : ""}">` +
        `<span class="lich-buoi">${esc(nhanBuoi(b.buoi))}</span>` +
        `<span class="lich-phu">${esc(b.tong_cho)} · ${b.ti_le_choi === null ? "—" : esc(b.ti_le_choi) + "×"}</span>` +
        `</div>`;
      (theoBuoi[b.buoi] || []).forEach((c) => {
        const phanTram = c.capacity > 0
          ? Math.min(100, (c.matched / c.capacity) * 100)
          : 0;
        const o = document.createElement("div");
        o.className = "lich-o";
        o.innerHTML =
          `<span class="lich-ten">${esc(c.name || c.club_id)}</span>` +
          `<span class="lich-thanh"><span style="width:${phanTram}%"></span></span>`;
        o.title = `${c.matched}/${c.capacity}`;
        cot.appendChild(o);
      });
      box.appendChild(cot);
    });
  });
}

/* ---- Chọn buổi sẽ xếp (thẻ Vận hành) ----

   Hai cách chọn cho hai thói quen khác nhau, cùng sửa một tập:
     · bấm từng chip  -> chọn đúng một buổi, hoặc một tập rời rạc
     · Từ ... đến ... -> chọn một dải liên tiếp trong tuần

   Buổi không chọn GIỮ NGUYÊN kết quả lần xếp trước — đó là lý do tính
   năng này tồn tại, nên dòng nhắc phải nằm ngay đây chứ không nằm trong
   tài liệu. */

let dsBuoiCoThe = [];
let buoiDangChon = new Set();

/* `datLai: true` = chon lai TAT CA buoi (dung sau khi nhap tep). Mac
   dinh thi GIU lua chon cu neu danh sach buoi khong doi: truoc day moi
   lan quay lai the nay (vd. xem the Ket qua roi quay ve) lua chon bi dat
   lai thanh ca tuan, va bam Chay luc do se ghi de ca nhung buoi nguoi
   dung da co y giu nguyen. */
function loadChonBuoi({ datLai = false } = {}) {
  const box = el("chonBuoiBox");
  if (!box) return;
  callApiDocChung("get_danh_sach_buoi").then((res) => {
    /* Một buổi thì không có gì để chọn — bộ chọn chỉ làm rối một màn
       hình vốn đã chạy đúng. */
    if (!res.ok || !res.data.nhieu_buoi) {
      box.hidden = true;
      dsBuoiCoThe = [];
      buoiDangChon = new Set();
      return;
    }
    box.hidden = false;
    const dsMoi = res.data.ds_buoi;
    const giuLuaChon = !datLai
      && dsMoi.length === dsBuoiCoThe.length
      && dsMoi.every((b, i) => b === dsBuoiCoThe[i])
      && buoiDangChon.size > 0;
    dsBuoiCoThe = dsMoi;
    if (giuLuaChon) {
      // Danh sach khong doi: ve lai nhung giu nguyen lua chon va hai o dai.
      veLaiDaiGiuGiaTri();
      veChonBuoi();
      return;
    }
    /* Mặc định chọn HẾT: bấm Chạy mà không để ý bộ chọn thì phải ra
       đúng hành vi cũ. Mặc định chọn một buổi là lặng lẽ đổi nghĩa của
       nút Chạy. Danh sách buổi vừa đổi thì đây cũng là hướng an toàn. */
    buoiDangChon = new Set(dsBuoiCoThe);
    veChonBuoiDai();
    /* Hai o "Tu/Den" vua duoc dung lai nen deu dang o buoi DAU TIEN, trong
       khi moi the deu bat. Bo chon noi hai dieu khac nhau ve cung mot thu,
       va o dieu sai lai hep hon dieu dung. */
    dongBoDaiVoiChip();
    veChonBuoi();
  });
}

/* Dung lai hai o "Tu/Den" ma KHONG doi gia tri dang chon: veChonBuoiDai()
   goi clear() nen phai chup truoc va tra lai sau. */
function veLaiDaiGiuGiaTri() {
  const oTu = el("chonBuoiTu");
  const oDen = el("chonBuoiDen");
  const giuTu = oTu && oTu.value;
  const giuDen = oDen && oDen.value;
  veChonBuoiDai();
  if (oTu && giuTu) oTu.value = giuTu;
  if (oDen && giuDen) oDen.value = giuDen;
}

function veChonBuoiDai() {
  ["chonBuoiTu", "chonBuoiDen"].forEach((id) => {
    const sel = el(id);
    if (!sel) return;
    clear(sel);
    dsBuoiCoThe.forEach((b) => {
      const o = document.createElement("option");
      o.value = b;
      o.textContent = nhanBuoi(b);
      sel.appendChild(o);
    });
  });
}

/* Doi lua chon buoi khi thanh xac nhan dang treo thi cau hua tren thanh
   do khong con dung nua. Go no di, buoc nguoi dung bam Chay lai va doc
   lai cau hua moi — re hon nhieu so voi de ho xac nhan mot pham vi khac
   voi pham vi se chay. */
function goThanhXacNhanNeuCo() {
  const thanh = el("runConfirmBar");
  if (thanh) {
    thanh.remove();
    datVeLai(false);
    capNhatKhoaVanHanh(); // thanh xac nhan dong -> nut Chay mo lai
  }
}

function veChonBuoi() {
  const box = el("chonBuoiChip");
  if (!box) return;
  clear(box);
  dsBuoiCoThe.forEach((b) => {
    const nut = document.createElement("button");
    nut.type = "button";
    nut.className = "buoi-chip" + (buoiDangChon.has(b) ? " is-chon" : "");
    nut.textContent = nhanBuoi(b);
    nut.setAttribute("aria-pressed", buoiDangChon.has(b) ? "true" : "false");
    nut.addEventListener("click", () => {
      if (buoiDangChon.has(b)) buoiDangChon.delete(b);
      else buoiDangChon.add(b);
      goThanhXacNhanNeuCo();
      dongBoDaiVoiChip();
      veChonBuoi();
    });
    box.appendChild(nut);
  });
  capNhatKhoaVanHanh(); // the vua dung lai: ap dung trang thai khoa

  /* Nhắc đúng tình huống đang xảy ra, không nhắc chung chung. Chọn hết
     thì không có buổi nào bị giữ lại, nói câu đó là thừa và gây phân vân. */
  const nhac = el("chonBuoiNhac");
  if (nhac) {
    const duoc = dsBuoiCoThe.filter((b) => !buoiDangChon.has(b));
    nhac.textContent = duoc.length
      ? t("chon_buoi_nhac_giu").replace("{buoi}", duoc.map(nhanBuoi).join(", "))
      : t("chon_buoi_nhac_het");
  }
}

function dongBoDaiVoiChip() {
  /* Dải chỉ có nghĩa khi tập đang chọn là một đoạn LIỀN NHAU. Rời rạc
     thì để nguyên hai ô, đừng ép nó nói một điều không đúng. */
  const chon = dsBuoiCoThe.filter((b) => buoiDangChon.has(b));
  if (!chon.length) return;
  const dau = dsBuoiCoThe.indexOf(chon[0]);
  const cuoi = dsBuoiCoThe.indexOf(chon[chon.length - 1]);
  if (cuoi - dau + 1 !== chon.length) return;
  if (el("chonBuoiTu")) el("chonBuoiTu").value = chon[0];
  if (el("chonBuoiDen")) el("chonBuoiDen").value = chon[chon.length - 1];
}

function apDungDaiBuoi() {
  const tu = dsBuoiCoThe.indexOf(el("chonBuoiTu").value);
  const den = dsBuoiCoThe.indexOf(el("chonBuoiDen").value);
  if (tu < 0 || den < 0) return;
  const [a, b] = tu <= den ? [tu, den] : [den, tu];
  buoiDangChon = new Set(dsBuoiCoThe.slice(a, b + 1));
  goThanhXacNhanNeuCo();
  veChonBuoi();
}

/* Trả về null khi chọn HẾT: null là "chạy cả tuần" ở phía API, và đó
   đúng là điều người dùng đang nói. */
function buoiGuiDi() {
  if (!dsBuoiCoThe.length) return null;
  if (buoiDangChon.size === dsBuoiCoThe.length) return null;
  return dsBuoiCoThe.filter((b) => buoiDangChon.has(b));
}

/* ---- Số bốc thăm theo buổi (thẻ Kết quả) ----

   Phần mềm xáo lại thứ tự ở MỖI buổi, nên sẽ có phụ huynh hỏi đúng câu
   "vì sao con tôi thứ Ba đứng thứ 30 mà thứ Sáu đứng thứ 120". Bảng này
   là câu trả lời — và nó không phá tính minh bạch: trường vẫn chỉ công bố
   MỘT bộ số đã khoá cộng hạt giống, thứ tự từng buổi suy ra tất định từ
   hai thứ đó nên ai cũng tính lại được. */

function loadSoBocTham(search) {
  const panel = el("thamPanel");
  if (!panel) return;
  callApiMoiNhat("so_tham", "get_so_boc_tham_theo_buoi", search || "").then((res) => {
    /* Một buổi thì bảng này không nói thêm gì so với bộ số đã khoá; chưa
       chạy lần nào thì chưa có hạt giống nào để suy ra thứ tự. */
    if (!res.ok || !res.data.nhieu_buoi || !res.data.da_chay) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const d = res.data;

    const canhBao = el("thamCachCu");
    if (canhBao) canhBao.hidden = !d.cach_cu;

    const head = el("thamHead");
    clear(head);
    head.innerHTML =
      `<th>${esc(t("th_student_id"))}</th><th>${esc(t("th_name"))}</th>` +
      d.ds_buoi.map((b) => `<th class="num">${esc(nhanBuoi(b))}</th>`).join("");

    const body = el("thamBody");
    clear(body);
    /* Dung ca bang trong mot DocumentFragment roi gan MOT lan: gan tung
       dong vao bang dang hien la trinh duyet tinh lai bo cuc moi dong —
       voi 400-800 dong va moi lan go phim tim kiem, do la cai giat. */
    const manh = document.createDocumentFragment();
    d.hoc_sinh.forEach((em) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(em.student_id)}</td><td>${esc(em.name || "")}</td>` +
        d.ds_buoi
          .map((b) => `<td class="num">${esc(em.so[b])}</td>`)
          .join("");
      manh.appendChild(tr);
    });
    body.appendChild(manh);
    veDemMuc("thamPanel", "dem_hoc_sinh", d.hoc_sinh.length);
  });
}

/* ---- Thời khoá biểu + độ phủ (thẻ Kết quả) ---- */

function loadThoiKhoaBieu(search) {
  const panel = el("tkbPanel");
  if (!panel) return;
  callApiMoiNhat("tkb", "get_thoi_khoa_bieu", search || "").then((res) => {
    if (!res.ok || res.data.ds_buoi.length < 2 || !res.data.hoc_sinh.length) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const dsBuoi = res.data.ds_buoi;

    const head = el("tkbHead");
    clear(head);
    head.innerHTML =
      `<th>${esc(t("th_student_id"))}</th><th>${esc(t("th_name"))}</th>` +
      dsBuoi.map((b) => `<th>${esc(nhanBuoi(b))}</th>`).join("") +
      `<th class="num">${esc(t("tkb_so_clb"))}</th>`;

    const body = el("tkbBody");
    clear(body);
    /* Dung ca bang trong mot DocumentFragment roi gan MOT lan: gan tung
       dong vao bang dang hien la trinh duyet tinh lai bo cuc moi dong —
       voi 400-800 dong va moi lan go phim tim kiem, do la cai giat. */
    const manh = document.createDocumentFragment();
    res.data.hoc_sinh.forEach((em) => {
      const o = dsBuoi.map((b) => {
        const c = em.theo_buoi[b];
        if (!c || !c.club_id) {
          return `<td><span class="tkb-trong">—</span></td>`;
        }
        const lop = c.matched_tier === "reserve" ? " is-du-tru" : "";
        return `<td><span class="tkb-o${lop}">${esc(c.club_name || c.club_id)}</span></td>`;
      }).join("");
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(em.student_id)}</td><td>${esc(em.name)}</td>` + o +
        `<td class="num">${esc(em.so_clb)}</td>`;
      manh.appendChild(tr);
    });
    body.appendChild(manh);
    veDemMuc("tkbPanel", "dem_hoc_sinh", res.data.hoc_sinh.length);
  });
}

function loadDoPhu() {
  const panel = el("doPhuPanel");
  if (!panel) return;
  callApiDocChung("get_do_phu").then((res) => {
    if (!res.ok || res.data.ds_buoi.length < 2 || !res.data.tong_hoc_sinh) {
      panel.hidden = true;
      return;
    }
    panel.hidden = false;
    const d = res.data;
    el("doPhuTb").textContent = soThapPhan(d.trung_binh_clb);
    el("doPhuTrangTay").textContent = d.so_em_trang_tay;
    veDemMuc("doPhuPanel", "dem_hoc_sinh", d.tong_hoc_sinh);

    const box = el("doPhuCot");
    clear(box);
    const lonNhat = Math.max(1, ...d.phan_bo.map((p) => p.so_em));
    d.phan_bo.forEach((p) => {
      const nhan =
        p.so_clb === 0 ? t("do_phu_0_clb")
        : p.so_clb === 1 ? t("do_phu_1_clb")
        : t("do_phu_x_clb", { n: p.so_clb });
      const ti_le = phanTramTron(p.so_em, d.tong_hoc_sinh);
      const dong = document.createElement("div");
      dong.className = "do-phu-dong" + (p.so_clb === 0 ? " is-trang-tay" : "");
      dong.tabIndex = 0;
      /* Hàng "không CLB nào" mang màu trạng thái đỏ, nên PHẢI kèm ký hiệu:
         màu một mình không đủ cho người mù màu hay bản in trắng đen. */
      dong.innerHTML =
        `<span class="do-phu-nhan">${p.so_clb === 0 && p.so_em > 0
          ? '<span class="ky-hieu-nguy" aria-hidden="true">⚠</span> ' : ""}${esc(nhan)}</span>` +
        `<span class="do-phu-track"><span class="do-phu-bar" ` +
        `style="width:${(p.so_em / lonNhat) * 100}%"></span></span>` +
        `<span class="do-phu-so-em">${esc(p.so_em)}` +
        `<span class="nv-ti-le"> · ${esc(ti_le)}%</span></span>`;
      ganTooltip(dong, () => ({
        tieu_de: nhan,
        dong: [[t("tt_so_em"), String(p.so_em)],
               [t("tt_ti_le"), ti_le + "%"]],
      }));
      box.appendChild(dong);
    });
  });
}

/* ---- Chỉ báo phủ buổi ở màn nhập tại chỗ ---- */

let buoiTaiCho = null;

function veChiBaoPhuBuoi(dsClbDaXep) {
  const box = el("fallbackPhuBuoi");
  const hint = el("fallbackBuoiHint");
  if (!box) return;
  /* Ham nay chay o MOI cu bam xep hang. Danh sach buoi khong doi trong
     luc xep cho mot em, nen hoi backend mot lan roi dung lai; chon em
     khac thi hoi lai (selectFallbackStudent xoa bo nho nay). */
  if (!buoiTaiCho) {
    buoiTaiCho = callApiDocChung("get_danh_sach_buoi").then((res) => {
      if (!res.ok) buoiTaiCho = null;
      return res;
    });
  }
  buoiTaiCho.then((res) => {
    if (!res.ok || !res.data.nhieu_buoi) {
      box.hidden = true;
      if (hint) hint.hidden = true;
      return;
    }
    box.hidden = false;
    if (hint) hint.hidden = false;

    const dsBuoi = res.data.ds_buoi;
    const daCo = new Set(
      (dsClbDaXep || [])
        .map((cid) => buoiCuaClb[cid])
        .filter((b) => b !== undefined)
    );
    clear(box);
    dsBuoi.forEach((b) => {
      const chip = document.createElement("span");
      chip.className = "phu-buoi-chip" + (daCo.has(b) ? " is-co" : "");
      chip.textContent = nhanBuoi(b);
      box.appendChild(chip);
    });
    const tom = document.createElement("span");
    tom.className = "phu-buoi-tom";
    tom.textContent = t("fallback_phu_buoi", { n: daCo.size, tong: dsBuoi.length });
    box.appendChild(tom);
  });
}


/* `giuTrang`: doi ngon ngu thi ve lai NHUNG giu trang dang xem — nguoi
   dung dang o trang 4 danh sach hoc sinh khong duoc bi day ve trang 1.
   Tra ve Promise cua danh sach hoc sinh de ben goi tick lai o da chon. */
function loadAdminTab(giuTrang) {
  loadAdminClubs();
  loadReserveGroupOptions();
  loadBuoiOptions();
  loadTaiTheoBuoi();
  loadLichTuan();
  if (!giuTrang) adminStudentPage = 1;
  callApi("get_last_run_info").then((res) => {
    adminCoKetQua = !!(res.ok && res.data);
  });
  return loadAdminStudents();
}

function loadAdminClubs() {
  callApi("list_clubs_admin").then((res) => {
    const body = el("adminClubTableBody");
    const emptyState = el("adminClubEmptyState");
    clear(body);
    if (!res.ok || !res.data.length) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    const nhieuBuoi = new Set(res.data.map((c) => c.buoi || BUOI_MAC_DINH)).size > 1;
    document.querySelectorAll("#view-admin .cot-buoi").forEach((o) => {
      o.hidden = !nhieuBuoi;
    });
    res.data.forEach((c) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${esc(c.club_id)}</td><td>${esc(c.name)}</td><td>${esc(c.capacity)}</td>` +
        `<td>${esc(c.reserve_capacity)}</td><td>${esc(c.reserve_group || "—")}</td>` +
        `<td class="cot-buoi">${esc(nhanBuoi(c.buoi))}</td><td></td>`;
      const delBtn = document.createElement("button");
      delBtn.className = "btn-icon-danger";
      delBtn.dataset.originalLabel = t("btn_delete");
      delBtn.textContent = delBtn.dataset.originalLabel;
      armTwoStepConfirm(delBtn, () => t("confirm_delete_generic"), () => {
        callApi("delete_club", c.club_id).then((delRes) => {
          if (delRes.ok) {
            showToast(t("toast_club_deleted", { club_id: c.club_id }), "success");
            loadAdminClubs();
            loadReserveGroupOptions();
          } else {
            showErrorToast(delRes.errors);
          }
        });
      });
      tr.lastElementChild.appendChild(delBtn);
      body.appendChild(tr);
    });
  });
}

function loadReserveGroupOptions() {
  callApi("list_reserve_groups_in_use").then((res) => {
    const list = el("reserveGroupOptions");
    clear(list);
    if (res.ok) {
      res.data.forEach((g) => {
        const opt = document.createElement("option");
        opt.value = g;
        list.appendChild(opt);
      });
    }
  });
}

function loadAdminStudents() {
  const search = el("adminStudentSearch").value.trim();
  return callApiMoiNhat("ds_hs_quan_ly", "list_students_admin", search, adminStudentPage, ADMIN_PAGE_SIZE).then((res) => {
    const body = el("adminStudentTableBody");
    const emptyState = el("adminStudentEmptyState");
    const pagination = el("adminStudentPagination");
    clear(body);
    el("adminChonTatCa").checked = false; // trang moi -> chua em nao duoc tick
    el("adminDemDanhDau").textContent = "";

    if (!res.ok || !res.data.rows.length) {
      emptyState.hidden = false;
      pagination.hidden = true;
      return;
    }
    emptyState.hidden = true;
    pagination.hidden = false;

    res.data.rows.forEach((s) => {
      const tr = document.createElement("tr");
      const tdCheck = document.createElement("td");
      const cb = document.createElement("input");
      cb.type = "checkbox";
      cb.className = "admin-row-checkbox";
      cb.dataset.studentId = s.student_id;
      tdCheck.appendChild(cb);
      tr.appendChild(tdCheck);
      /* insertAdjacentHTML, khong `innerHTML +=`: cach sau phan tich lai
         ca dong va thay o tick vua tao bang mot ban sao. */
      tr.insertAdjacentHTML("beforeend",
        `<td>${esc(s.student_id)}</td><td>${esc(s.name)}</td><td>${esc(s.reserve_group || "—")}</td>`);
      body.appendChild(tr);
    });

    el("adminPaginationLabel").textContent = t("pagination_label", {
      page: res.data.page,
      total_pages: res.data.total_pages,
      total: res.data.total,
    });
    el("btnAdminPrevPage").disabled = res.data.page <= 1;
    el("btnAdminNextPage").disabled = res.data.page >= res.data.total_pages;
  });
}

/* So em dang danh dau o the 04 — dung chung cho nut Gan va nut Xuat. */
function demDanhDauAdmin() {
  const n = document.querySelectorAll(".admin-row-checkbox:checked").length;
  el("adminDemDanhDau").textContent = n ? t("admin_dem_danh_dau", { n }) : "";
}

function initAdminHandlers() {
  el("btnSaveClub").addEventListener("click", () => {
    const id = el("clubFormId").value.trim();
    const name = el("clubFormName").value.trim();
    const capacity = el("clubFormCapacity").value;
    const reserveCapacity = el("clubFormReserveCapacity").value || 0;
    const reserveGroup = el("clubFormReserveGroup").value.trim();
    const buoi = el("clubFormBuoi") ? el("clubFormBuoi").value.trim() : "";
    if (!id || !name || !capacity) {
      feedback(el("clubFormFeedback"), t("feedback_club_form_required"), true);
      return;
    }
    khiBan(el("btnSaveClub"), () => callApi("create_or_update_club", id, name, capacity, reserveCapacity, reserveGroup, buoi)).then((res) => {
      if (res.ok) {
        feedback(el("clubFormFeedback"), t("feedback_club_saved", { club_id: id }), false);
        el("clubFormId").value = "";
        if (el("clubFormBuoi")) el("clubFormBuoi").value = "";
        el("clubFormName").value = "";
        el("clubFormCapacity").value = "";
        el("clubFormReserveCapacity").value = "0";
        el("clubFormReserveGroup").value = "";
        loadAdminClubs();
        loadReserveGroupOptions();
      } else {
        feedbackErrors(el("clubFormFeedback"), res.errors);
      }
    });
  });

  el("adminStudentSearch").addEventListener(
    "input",
    debounce(() => {
      adminStudentPage = 1;
      loadAdminStudents();
    }, 250)
  );

  el("btnAdminPrevPage").addEventListener("click", () => {
    if (adminStudentPage > 1) {
      adminStudentPage -= 1;
      loadAdminStudents();
    }
  });
  el("btnAdminNextPage").addEventListener("click", () => {
    adminStudentPage += 1;
    loadAdminStudents();
  });

  /* Cung tap o tick voi nut "Gan" ben canh — mot cach chon, hai viec. */
  el("btnAdminXuatHs").addEventListener("click", () => {
    const ids = Array.from(document.querySelectorAll(".admin-row-checkbox:checked")).map(
      (cb) => cb.dataset.studentId
    );
    if (!ids.length) {
      showToast(t("toast_no_students_ticked"), "error");
      return;
    }
    chayXuat([["xuat_muc_hoc_sinh", "export_hoc_sinh_csv", [ids, ""],
      (d) => t("xuat_kq_hoc_sinh", { n: d.n_hoc_sinh, n_dong: d.n_dong, path: d.path })]],
      el("adminXuatFeedback"));
  });

  el("adminChonTatCa").addEventListener("change", (ev) => {
    document.querySelectorAll(".admin-row-checkbox").forEach((cb) => { cb.checked = ev.target.checked; });
    demDanhDauAdmin();
  });
  el("adminStudentTableBody").addEventListener("change", (ev) => {
    if (ev.target.classList && ev.target.classList.contains("admin-row-checkbox")) demDanhDauAdmin();
  });

  el("btnBulkAssign").addEventListener("click", () => {
    const ids = Array.from(document.querySelectorAll(".admin-row-checkbox:checked")).map(
      (cb) => cb.dataset.studentId
    );
    const group = el("bulkReserveGroupInput").value.trim();
    if (!ids.length) {
      showToast(t("toast_no_students_ticked"), "error");
      return;
    }
    khiBan(el("btnBulkAssign"), () => callApi("bulk_set_reserve_group", ids, group)).then((res) => {
      if (res.ok) {
        showToast(t("toast_bulk_assign_success", { n: res.data.n_updated }), "success");
        loadAdminStudents();
        loadReserveGroupOptions();
      } else {
        showErrorToast(res.errors);
      }
    });
  });

  /* --- Vung nguy hiem: xoa du lieu de lam lai tu dau --------------- *
     Chuoi "XOA" la xac nhan bat buoc o phia Python. No KHONG phai thu
     nguoi dung go — nut da co xac nhan hai buoc roi. No de mot lenh
     goi API nham (vd tu console) khong xoa duoc gi. */
  /* Du lieu da xoa thi moi thu dang TRO toi du lieu cu cung phai di:
     o tim kiem con chu, em dang mo o the Nhap tai cho, danh sach CLB
     dang mo, CLB dang cham. Bo sot thi quay sang the kia van thay dung
     em vua tim — mot em khong con ton tai. */
  function donSachSauKhiXoaDuLieu() {
    ["studentSearchInput", "newStudentId", "newStudentName", "adminStudentSearch",
     "resultsSearch", "tkbSearch", "thamSearch"].forEach((id) => {
      if (el(id)) el(id).value = "";
    });
    boChonHocSinhDuPhong();
    currentClubs = [];
    fallbackStudentPage = 1;
    adminStudentPage = 1;
    clear(el("studentSearchResults"));
    el("fallbackStudentPagination").hidden = true;
    dongDanhSachCLB();
    currentScoringClub = null;
    if (el("scoringWorkArea")) el("scoringWorkArea").hidden = true;
  }

  function noiNutXoa(idNut, phamVi, khoaNhanThuong, khoaNhanCoKetQua, khoaToast) {
    armTwoStepConfirm(
      el(idNut),
      () => t(adminCoKetQua ? khoaNhanCoKetQua : khoaNhanThuong),
      () => {
        /* Dang nhap tep hay dang chay thi chuoi do van ghi tiep sau khi xoa:
           cac tep con lai nap vao CSDL vua xoa, roi ghi "Da nhap xong" de
           len the Van hanh vua don sach. Nut "Bo danh sach" bi khoa luc nay
           cung vi ly do do. */
        if (khoa.dangNhap || khoa.dangChay) {
          showToast(t("toast_reset_blocked_busy"), "error");
          return;
        }
        callApi("reset_data", phamVi, "XOA").then((res) => {
          if (!res.ok) {
            showErrorToast(res.errors);
            return;
          }
          showToast(
            t(khoaToast, {
              n_students: res.data.n_students,
              n_clubs: res.data.n_clubs,
              n_clubs_left: res.data.n_clubs_con_lai,
              backup_name: res.data.backup_name,
            }),
            "success"
          );
          /* Phai lam moi CA nhung thu KHONG nam tren tab nay. Thanh ben
             luon hien, va sau khi xoa no van noi "Chay gan nhat: 6/6 xep
             duoc" cho mot lan chay ma du lieu da khong con — man hinh noi
             mot dieu khong dung, ngay sau thao tac nguy hiem nhat. */
          /* Hoc sinh da bi xoa -> tap em da chon o the 02 khong con nghia.
             Giu lai thi lan xuat ho so sau hong ca lo (student_not_found). */
          hsDaChon.clear();
          donSachSauKhiXoaDuLieu();
          donSachTheVanHanh();
          loadAdminTab();
          loadHealthReport();
          refreshDashboardStats();
          refreshSidebarStatus();
        });
      }
    );
  }

  noiNutXoa("btnResetStudents", "hoc_sinh",
            "confirm_reset_students", "confirm_reset_students_has_results",
            "toast_reset_students_done");
  noiNutXoa("btnResetAll", "tat_ca",
            "confirm_reset_all", "confirm_reset_all_has_results",
            "toast_reset_all_done");
}
