/* ==========================================================================
   chung.js — phần DÙNG CHUNG của js/*.js và recovery.js.

   Trước đây recovery.js là BẢN SAO NGUYÊN VĂN của cổng khởi động, callApi
   và nút xác nhận hai bước trong js/*.js ("sửa bên này nhớ sửa bên kia").
   Màn hình phục hồi lại là màn hình hiện ra KHI CSDL ĐÃ HỎNG — bản sao bị
   bỏ quên ở đúng chỗ đó thì không còn đường nào. Giờ chỉ còn một bản.

   Nạp SAU i18n.js và TRƯỚC js/*.js / recovery.js. Xuất ra window.RBDA.
   ========================================================================== */

(function (global) {
  "use strict";

  /* Backend goi duoc CHUA? Tach rieng de cong khoi dong (choBackend) hoi CHINH
     dieu kien nay, chu khong viet mot luat thu hai.

     KHONG duoc chi hoi `window.pywebview`. pywebview dung doi tuong do
     TRUOC voi `api: {}` RONG (webview/js/api.js), roi mot lenh run_js THU
     HAI moi do ham vao va ban su kien (webview/js/finish.js) — hai lenh
     tach roi, tren mot luong rieng, co phan chieu Python xen giua
     (webview/util.py, generate_js_object). Trong khe ho do
     `window.pywebview` da that ma goi ham nao cung truot. Tren Windows
     viec nay con chay SAU khi trang da tai xong
     (webview/platforms/edgechromium.py, on_navigation_completed). */
  function apiSanSang(name) {
    return !!(global.pywebview && global.pywebview.api
              && typeof global.pywebview.api[name] === "function");
  }

  function callApi(name, ...args) {
    if (!apiSanSang(name)) {
      return Promise.resolve({
        ok: false,
        data: null,
        errors: [global.I18N.t("backend_dang_ket_noi") + " (" + name + ")"],
      });
    }
    /* "TypeError: Failed to fetch" nguyen van khong noi voi nhan vien
       nha truong phai lam gi: ghi loi goc ra console, hien cau da dich. */
    return global.pywebview.api[name](...args).catch((e) => {
      console.error("callApi", name, e);
      return { ok: false, data: null, errors: [global.I18N.t("api_mat_ket_noi")] };
    });
  }

  // Nút xác nhận 2 bước (thay confirm() native) — bấm lần 1 đổi label +
  // class .is-confirming, bấm lần 2 trong vòng `windowMs` mới thật sự chạy.
  // `getConfirmLabel` là hàm (không phải chuỗi cố định) và nhãn gốc được
  // đọc LẠI mỗi lần reset (qua data-i18n hoặc dataset.originalLabel) thay
  // vì chụp 1 lần lúc gắn sự kiện — để đổi ngôn ngữ giữa chừng không làm
  // nút "hồi" lại nhãn cũ khi bấm lần kế tiếp.
  /* Danh sach ham "nha" cua MOI nut xac nhan 2 buoc dang song. Trang thai
     armed nam trong closure nen ben ngoai khong voi toi duoc — doi ngon
     ngu giua chung thi nut dang cho xac nhan ket lai o tieng cu. Dang ky
     ham nha vao day de nhaMoiNutXacNhan() goi duoc. */
  const nutXacNhanDangSong = [];

  function armTwoStepConfirm(button, getConfirmLabel, onConfirmed, windowMs) {
    let armed = false;
    let timer = null;

    function currentOriginalLabel() {
      const key = button.getAttribute("data-i18n");
      if (key) return global.I18N.t(key);
      return button.dataset.originalLabel || button.textContent;
    }

    /* Nha nhan VA nha trang thai. Nha moi nhan ma quen armed la bien nut
       hai buoc thanh nut MOT buoc — bam mot phat la xoa that. */
    function nha() {
      clearTimeout(timer);
      armed = false;
      button.textContent = currentOriginalLabel();
      button.classList.remove("is-confirming");
    }

    /* Don nut da roi khoi DOM ngay khi dang ky nut moi. Bang CLB ve lai la
       tao lai mot nut "Xoa" moi dong, nen truoc day mang nay chi phinh ra
       cho toi khi doi ngon ngu. */
    for (let i = nutXacNhanDangSong.length - 1; i >= 0; i--) {
      if (!nutXacNhanDangSong[i].button.isConnected) nutXacNhanDangSong.splice(i, 1);
    }
    nutXacNhanDangSong.push({ button, nha });

    button.addEventListener("click", () => {
      if (!armed) {
        armed = true;
        button.textContent = typeof getConfirmLabel === "function" ? getConfirmLabel() : getConfirmLabel;
        button.classList.add("is-confirming");
        timer = setTimeout(nha, windowMs || 4000);
      } else {
        nha();
        onConfirmed();
      }
    });
  }

  function nhaMoiNutXacNhan() {
    /* Nut trong bang duoc tao lai moi lan ve — cai cu roi khoi DOM nhung
       van con trong mang. Bo chung di, dung goi nha() tren xac cu. */
    for (let i = nutXacNhanDangSong.length - 1; i >= 0; i--) {
      const muc = nutXacNhanDangSong[i];
      if (!muc.button.isConnected) {
        nutXacNhanDangSong.splice(i, 1);
        continue;
      }
      muc.nha();
    }
  }

  /* CONG KHOI DONG — goi `khiSan()` DUNG MOT LAN khi backend goi duoc.

     CHI HOI VONG, KHONG NGHE `pywebviewready`. Dieu kien hoi vong
     (apiSanSang) MANH HON su kien: su kien chi bao "_createApi da chay",
     con cai ta thuc su can la "ham goi duoc". Mot duong vao thi kiem chung
     duoc; hai duong vao cho cung mot viec chinh la cach loi nay sinh ra
     lan dau. Cham nhat la tre NHIP_MS, khong ai thay.

     DUNG MOT LAN: khoi dong hai lan la GAN DOI TOAN BO nut — mot cu bam
     doi ngon ngu goi setLang hai luot (nut trong nhu chet), mot chuoi bam
     hai buoc goi reset_data (hay start_fresh o man hinh phuc hoi) hai lan.
     Ca hai deu da do duoc. Co `data-app-init` dat NGAY trong day nen moi
     duong vao deu di qua no.

     `hamThu`   : ham chac chan co trong API cua trang, dung lam phep thu.
     `baoDangCho(cau)` / `baoQuaHan(cau)`: noi hien trang thai cho nguoi dung.
     Test rut ngan han cho qua window.__HAN_BACKEND_MS (tests/
     test_khoi_dong_backend.py); ban chay that khong bao gio dat bien nay. */
  function choBackend(hamThu, khiSan, baoDangCho, baoQuaHan) {
    const NHIP_MS = 50;
    const HIEN_DANG_CHO_SAU_MS = 400;   // duoi nguong nay khong ai kip thay
    const HAN_MS = Number(global.__HAN_BACKEND_MS) || 20000;
    let daKhoiDong = false;
    let daNoiDangCho = false;
    const batDau = Date.now();

    function khoiDongMotLan() {
      if (daKhoiDong) return;
      daKhoiDong = true;
      document.body.dataset.appInit = "1";
      khiSan();
    }

    (function cho() {
      if (apiSanSang(hamThu)) {
        khoiDongMotLan();
        return;
      }
      if (Date.now() - batDau > HAN_MS) {
        baoQuaHan(global.I18N.t("backend_qua_han"));
        return;
      }
      if (!daNoiDangCho && Date.now() - batDau > HIEN_DANG_CHO_SAU_MS) {
        daNoiDangCho = true;
        baoDangCho(global.I18N.t("backend_dang_ket_noi"));
      }
      setTimeout(cho, NHIP_MS);
    })();
  }

  global.RBDA = { apiSanSang, callApi, armTwoStepConfirm, nhaMoiNutXacNhan, choBackend };
})(window);
