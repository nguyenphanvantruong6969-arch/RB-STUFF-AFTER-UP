"""Sinh đoạn mã Google Apps Script dựng biểu mẫu 6 buổi trên Google Forms.

    python mau_forms_thi_clb/tao_google_forms.py

Ghi ra mau_forms_thi_clb/TAO_GOOGLE_FORM.gs. Dán tệp đó vào script.google.com
và chạy hàm taoBieuMau: biểu mẫu được dựng đủ câu hỏi, đáp án, điểm và rẽ
nhánh, không phải đặt tay chỗ nào.

Dữ liệu CLB và đề thi lấy từ THIET_KE_6_PHAN.html (qua tao_word_6_phan.py),
thứ tự lựa chọn xáo giống hệt tệp nhập Microsoft Forms và trang chạy thử.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

THU_MUC = os.path.dirname(os.path.abspath(__file__))
RA = os.path.join(THU_MUC, "TAO_GOOGLE_FORM.gs")

# Chữ các lựa chọn cố định. Trùng với tao_word_6_phan.py (test giữ hai bên
# khớp); khai lại ở đây để tệp này chạy được mà không cần python-docx.
DIEM_CAU, TRAN_THI = 5, 5
CO_BUOI, KHONG_BUOI = "Có", "Không, em bận buổi này"
CO, KHONG, DUNG = "Có, em thi CLB này", "Không", "Em không thi thêm CLB nào buổi này"
KHONG_THI = "Em không thi CLB nào buổi này"
BO_TRONG = "(Bỏ trống)"

MAU = r"""/**
 * Dựng biểu mẫu Google Forms "Đăng ký CLB và thi tuyển".
 *
 * TỆP NÀY DO tao_google_forms.py SINH RA. Sửa đề thì sửa THIET_KE_6_PHAN.html
 * rồi chạy lại tao_google_forms.py, không sửa tay danh sách BUOI bên dưới.
 *
 * Cách dùng:
 *   1. Mở script.google.com, bấm "Dự án mới".
 *   2. Xoá hết chữ có sẵn, dán toàn bộ tệp này vào, bấm Lưu.
 *   3. Chọn hàm taoBieuMau ở thanh trên, bấm Chạy, cho phép quyền truy cập.
 *   4. Mở "Nhật ký thực thi" để lấy đường dẫn sửa và đường dẫn gửi học sinh.
 *
 * Mỗi lần chạy tạo một biểu mẫu MỚI trong Google Drive, không sửa biểu mẫu cũ.
 *
 * Chấm điểm theo từng CLB (sau khi học sinh nộp):
 *   Chọn hàm chamTheoCLB, bấm Chạy. Hàm tạo trong Google Drive một thư mục
 *   "Kết quả CLB <ngày giờ>" chứa các tệp Excel: bảng điểm, 3 tệp nạp
 *   phần mềm xếp CLB, dữ liệu raw đã chấm từng câu, và đáp án. Đường dẫn thư mục nằm trong "Nhật ký thực thi".
 *   Nếu biểu mẫu được tạo bằng bản mã cũ (trước khi có hàm này), dán đường
 *   dẫn SỬA biểu mẫu vào LINK_BIEU_MAU bên dưới trước khi chạy.
 */

// Để trống nếu biểu mẫu được tạo bằng chính dự án này sau khi có hàm chamTheoCLB.
const LINK_BIEU_MAU = '';

const TIEU_DE = %(tieu_de)s;
const DIEM_CAU = %(diem)d;
const TRAN_THI = %(tran)d;
const CO_BUOI = %(co_buoi)s;
const KHONG_BUOI = %(khong_buoi)s;
const CO = %(co)s;
const KHONG = %(khong)s;
const DUNG = %(dung)s;
const KHONG_THI = %(khong_thi)s;
const BO_TRONG = %(bo_trong)s;

// [{ma, ten, clubs: [{id, name, de: [{q, opts, dung}]}]}]
const BUOI = %(buoi)s;

function taoBieuMau() {
  const form = FormApp.create(TIEU_DE);
  form.setIsQuiz(true)
      .setDescription('Mỗi buổi: xếp hạng CLB em muốn vào, tick các CLB muốn thi (tối đa ' + TRAN_THI + '), rồi chọn lần lượt CLB để làm bài. Buổi nào bận thì chọn "Không, em bận buổi này".')
      .setShuffleQuestions(false)
      .setProgressBar(true)
      .setShowLinkToRespondAgain(false)
      .setPublishingSummary(false)
      .setConfirmationMessage('Em đã nộp phiếu. Cảm ơn em.');

  form.addTextItem().setTitle('[student_id] Mã học sinh').setRequired(true);
  form.addTextItem().setTitle('[name] Họ và tên').setRequired(true);

  // Bước 1: tạo đủ các trang và câu hỏi theo đúng thứ tự. Mỗi buổi:
  //   trang buổi      [di-<buổi>]        có đăng ký buổi này không
  //   trang xếp hạng  [<buổi>]           lưới Top 1..Top 10, mỗi CLB dùng một lần
  //                   [chon-<buổi>]      tick CLB muốn thi, Google chặn quá 5
  //   trang chọn đầu  [thi-<buổi>]       "Em thi CLB nào trước?"
  //   đề CLB i, rồi   [thi-sau-<clb i>]  "Em thi CLB nào tiếp theo?" (chỉ CLB đứng sau i)
  // Học sinh chỉ thấy đề của CLB em chọn.
  const nhan = function (c) { return c.name + ' (' + c.id + ')'; };
  const days = BUOI.map(function (d) {
    const trangBuoi = form.addPageBreakItem().setTitle(d.ten);
    const cauBuoi = form.addMultipleChoiceItem()
        .setTitle('[di-' + d.ma + '] Em có đăng ký sinh hoạt ' + d.ten + ' không?')
        .setRequired(true);

    const trangXep = form.addPageBreakItem()
        .setTitle(d.ten + ': nguyện vọng và chọn CLB thi')
        .setHelpText('Top 1 là CLB em thích nhất. Bấm vào từng Top để chọn CLB trong danh sách. '
            + 'Mỗi CLB chỉ chọn một lần. Không muốn thêm thì để ' + BO_TRONG + '.');
    // Mỗi Top một danh sách thả xuống. Google không chặn được chọn trùng giữa
    // các danh sách: chamTheoCLB giữ Top cao hơn và ghi cảnh báo.
    d.clubs.forEach(function (_, k) {
      form.addListItem()
          .setTitle('[' + d.ma + '-top-' + (k + 1) + '] Top ' + (k + 1))
          .setChoiceValues([BO_TRONG].concat(d.clubs.map(nhan)));
    });

    // Chỉ CLB có đề thi mới có trong câu tick và các trang chọn làm bài.
    // Buổi không có CLB nào thi thì bỏ hẳn phần này.
    const coThi = d.clubs.filter(function (c) { return c.de.length; });
    if (!coThi.length) {
      return {trangBuoi: trangBuoi, cauBuoi: cauBuoi, trangXep: trangXep, chonDau: null, clubs: []};
    }

    // Google chặn cứng: không tick được quá TRAN_THI CLB. Chỉ bài thi của CLB
    // đã tick ở đây mới được tính điểm (xem chamTheoCLB).
    const chon = form.addCheckboxItem()
        .setTitle('[chon-' + d.ma + '] Chọn các CLB em muốn thi ' + d.ten + ' (tối đa ' + TRAN_THI + ')')
        .setHelpText('Không thi CLB nào thì bỏ trống. Chỉ bài thi của CLB em tick ở đây mới được tính điểm.')
        .setChoiceValues(coThi.map(nhan));
    chon.setValidation(FormApp.createCheckboxValidation()
        .setHelpText('Chỉ được chọn tối đa ' + TRAN_THI + ' CLB.')
        .requireSelectAtMost(TRAN_THI)
        .build());

    form.addPageBreakItem().setTitle(d.ten + ': làm bài thi');
    const chonDau = form.addMultipleChoiceItem()
        .setTitle('[thi-' + d.ma + '] Em thi CLB nào trước? Chọn một CLB em đã tick. Làm xong sẽ được chọn CLB tiếp theo.')
        .setRequired(true);

    const clubs = coThi.map(function (c, i) {
      const trangDe = form.addPageBreakItem().setTitle('Đề thi ' + c.name);
      c.de.forEach(function (q, j) {
        const it = form.addMultipleChoiceItem()
            .setTitle('[' + c.id + '-' + (j + 1) + '] ' + q.q)
            .setPoints(DIEM_CAU)
            .setRequired(true);
        it.setChoices(q.opts.map(function (o) { return it.createChoice(o, o === q.dung); }));
      });
      // Trang "tiếp theo" đứng ngay sau đề, nên làm xong đề là Google tự sang.
      // CLB thi cuối danh sách không có trang này: làm xong là sang buổi sau.
      let tiep = null;
      if (i + 1 < coThi.length) {
        form.addPageBreakItem().setTitle(d.ten + ': CLB tiếp theo');
        tiep = form.addMultipleChoiceItem()
            .setTitle('[thi-sau-' + c.id + '] Em thi CLB nào tiếp theo? Chỉ còn các CLB đứng sau ' + c.name + ' trong danh sách.')
            .setRequired(true);
      }
      return {c: c, trangDe: trangDe, tiep: tiep};
    });
    return {trangBuoi: trangBuoi, cauBuoi: cauBuoi, trangXep: trangXep, chonDau: chonDau, clubs: clubs};
  });

  // Bước 2: nối rẽ nhánh.
  days.forEach(function (d, k) {
    const sau = k + 1 < days.length ? days[k + 1].trangBuoi : FormApp.PageNavigationType.SUBMIT;
    d.cauBuoi.setChoices([
      d.cauBuoi.createChoice(CO_BUOI, d.trangXep),
      d.cauBuoi.createChoice(KHONG_BUOI, sau)
    ]);
    if (!d.chonDau) return;
    // Danh sách lựa chọn: các CLB thi từ vị trí `tu` trở đi, cộng lựa chọn dừng.
    const luaChon = function (item, tu, chuDung) {
      const ds = [];
      for (let j = tu; j < d.clubs.length; j++) ds.push(item.createChoice(nhan(d.clubs[j].c), d.clubs[j].trangDe));
      ds.push(item.createChoice(chuDung, sau));
      item.setChoices(ds);
    };
    luaChon(d.chonDau, 0, KHONG_THI);
    d.clubs.forEach(function (x, i) { if (x.tiep) luaChon(x.tiep, i + 1, DUNG); });
  });

  // Google Forms mới có nút "Xuất bản": chưa xuất bản thì học sinh không mở được.
  // Bản Apps Script cũ không có hàm này nên kiểm tra trước khi gọi.
  if (typeof form.setPublished === 'function') form.setPublished(true);
  PropertiesService.getScriptProperties().setProperty('FORM_ID', form.getId());
  Logger.log('Đường dẫn để SỬA biểu mẫu: ' + form.getEditUrl());
  Logger.log('Đường dẫn gửi HỌC SINH: ' + form.getPublishedUrl());
}

function moBieuMau_() {
  if (LINK_BIEU_MAU) return FormApp.openByUrl(LINK_BIEU_MAU);
  const id = PropertiesService.getScriptProperties().getProperty('FORM_ID');
  if (id) return FormApp.openById(id);
  throw new Error('Chưa biết chấm biểu mẫu nào. Dán đường dẫn SỬA biểu mẫu vào LINK_BIEU_MAU ở đầu tệp rồi chạy lại.');
}

/**
 * Đọc bảng lưới xếp hạng (biểu mẫu cũ) thành [{id, top}] sắp theo top. Nhận hai kiểu lưới:
 *   bản mới: dòng thứ k là "Top k", ô chọn là "Tên CLB (mã)";
 *   bản cũ:  dòng thứ k là CLB thứ k trong danh sách, ô chọn là "Hạng n".
 */
function docTop_(d, mang) {
  const ds = [];
  [].concat(mang || []).forEach(function (v, k) {
    const id = maClb_(v);
    if (id) { ds.push({id: id, top: k + 1}); return; }
    const n = parseInt(String(v == null ? '' : v).replace(/\D/g, ''), 10);
    if (!isNaN(n) && d.clubs[k]) ds.push({id: d.clubs[k].id, top: n});
  });
  return ds.sort(function (a, b) { return a.top - b.top; });
}

/**
 * Xếp hạng của một phiếu trong một buổi, [{id, top}] sắp theo top.
 * Biểu mẫu mới: mỗi Top một câu thả xuống [<buổi>-top-k]. Biểu mẫu cũ: một
 * bảng lưới [<buổi>] (docTop_ đọc được cả hai kiểu lưới).
 */
function docTopPhieu_(d, tl) {
  const ds = [];
  let coThaXuong = false;
  d.clubs.forEach(function (_, k) {
    const ma = d.ma + '-top-' + (k + 1);
    if (!(ma in tl)) return;
    coThaXuong = true;
    const id = maClb_(tl[ma]);
    if (id) ds.push({id: id, top: k + 1});
  });
  return coThaXuong ? ds : docTop_(d, tl[d.ma]);
}

function maClb_(v) {
  const m = String(v == null ? '' : v).match(/\(([A-Za-z0-9_]+)\)\s*$/);
  return m ? m[1] : '';
}

function chuanHoa_(s) {
  return String(s == null ? '' : s).trim().replace(/\s+/g, ' ').toLowerCase();
}

/**
 * Chấm lại mọi phiếu theo đáp án trong BUOI, tách điểm từng CLB (thang 10),
 * và ghi vào một thư mục "Kết quả CLB <ngày giờ>":
 *   SO_NHAP_CLB.xlsx    Sổ nhập CLB: tệp DUY NHẤT kéo vào phần mềm. Trang
 *                       "1. CLB" (điền cột Chỉ tiêu trước khi nạp) và trang
 *                       "2. Học sinh" (nguyện vọng, điểm cạnh CLB đã thi)
 *   BANG_DIEM.xlsx      trang Bảng điểm (mỗi em một dòng, mỗi CLB có thi một
 *                       cột) và trang Cảnh báo (phiếu bị bỏ và lý do)
 *   RAW_PHIEU.xlsx      mọi câu trả lời, đã chấm từng câu
 *   DAP_AN.xlsx         đáp án. Định dạng hai tệp này: DINH_DANG_RAW.md.
 */
function chamTheoCLB() {
  const form = moBieuMau_();
  const phieu = form.getResponses();
  const daCo = {};
  const hocSinh = [];
  const canhBao = [];

  const META = moTaCau_();
  const raw = [COT_RAW];

  phieu.forEach(function (r, i) {
    const tl = {};
    const cacCau = [];
    r.getItemResponses().forEach(function (ir) {
      const m = String(ir.getItem().getTitle()).match(/^\s*\[([^\]]+)\]\s*(.*)$/);
      if (!m) return;
      let diemForms = '';
      try { const s = ir.getScore(); if (s !== null && s !== undefined) diemForms = s; } catch (e) {}
      tl[m[1]] = ir.getResponse();
      cacCau.push({ma: m[1], cau: m[2], tl: ir.getResponse(), diemForms: diemForms});
    });
    const sid = String(tl.student_id || '').trim();
    const dong = 'Phiếu thứ ' + (i + 1);
    // Cách xử lí từng CLB trong phiếu: {club_id: [được tính 1/0, ghi chú]}.
    const xuLi = {};
    let trangThai = 'giu';

    if (!sid) {
      trangThai = 'bo_khong_ma';
      canhBao.push([dong, '', 'Không có mã học sinh, bỏ cả phiếu']);
    } else if (daCo[sid]) {
      trangThai = 'bo_nop_trung';
      canhBao.push([dong, sid, 'Nộp lần nữa. Bỏ phiếu này, giữ phiếu đầu (' + daCo[sid] + ')']);
    } else {
      daCo[sid] = dong;
      const hs = {sid: sid, ten: String(tl.name || '').trim(), nv: {}, diem: {}, thi: []};
      BUOI.forEach(function (d) {
        if (tl['di-' + d.ma] !== CO_BUOI) return;
        // Bảng lưới: dòng Top k nhận "Tên (mã)" của CLB em chọn. Bỏ trống một
        // Top ở giữa thì dồn lên và báo.
        const top = docTopPhieu_(d, tl);
        let truoc = 0;
        const topCua = {};
        const nv = [];
        top.forEach(function (x) {
          if (x.top !== truoc + 1) {
            canhBao.push([dong, sid, d.ten + ': bỏ trống Top ' + (truoc + 1) + ' nhưng có chọn Top ' + x.top + ', đã dồn lên.']);
          }
          truoc = x.top;
          if (topCua[x.id]) {
            canhBao.push([dong, sid, d.ten + ': chọn ' + x.id + ' ở cả Top ' + topCua[x.id] + ' và Top ' + x.top + ', giữ Top ' + topCua[x.id] + '.']);
            return;
          }
          topCua[x.id] = x.top;
          nv.push(x.id);
        });
        if (!nv.length) canhBao.push([dong, sid, d.ten + ': đăng ký buổi nhưng không xếp CLB nào.']);
        hs.nv[d.ma] = nv;

        // CLB em đã tick ở câu [chon-...]: Google trả về mảng chữ "Tên (mã)".
        const daTick = {};
        [].concat(tl['chon-' + d.ma] || []).forEach(function (v) {
          const m = String(v).match(/\(([A-Za-z0-9_]+)\)\s*$/);
          if (m) daTick[m[1]] = true;
        });

        // CLB em đã chọn làm bài: ở trang "thi CLB nào trước" và các trang "tiếp theo".
        const daLam = {};
        [tl['thi-' + d.ma]].concat(d.clubs.map(function (c) { return tl['thi-sau-' + c.id]; }))
            .forEach(function (v) { const id = maClb_(v); if (id) daLam[id] = true; });
        // Biểu mẫu bản cũ: mỗi CLB một câu [thi-<mã CLB>] trả lời "Có, em thi CLB này".
        d.clubs.forEach(function (c) { if (tl['thi-' + c.id] === CO) daLam[c.id] = true; });

        let soThi = 0;
        d.clubs.forEach(function (c) {
          const lam = !!daLam[c.id];
          if (!lam) {
            if (daTick[c.id]) canhBao.push([dong, sid, d.ten + ': tick ' + c.name + ' nhưng không làm bài.']);
            return;
          }
          if (!daTick[c.id]) {
            xuLi[c.id] = [0, 'khong_tick'];
            canhBao.push([dong, sid, d.ten + ': làm bài ' + c.name + ' nhưng không tick ở câu chọn CLB thi, không tính điểm.']);
            return;
          }
          if (nv.indexOf(c.id) < 0) {
            xuLi[c.id] = [0, 'khong_xep_hang'];
            canhBao.push([dong, sid, d.ten + ': làm bài ' + c.name + ' nhưng không chọn CLB này ở Top nào, không tính điểm.']);
            return;
          }
          // Phòng hờ: Google đã chặn tick quá TRAN_THI, nhưng biểu mẫu có thể bị sửa tay.
          if (soThi >= TRAN_THI) {
            xuLi[c.id] = [0, 'qua_tran'];
            canhBao.push([dong, sid, d.ten + ': quá ' + TRAN_THI + ' CLB, bỏ bài ' + c.name + '.']);
            return;
          }
          soThi++;
          xuLi[c.id] = [1, ''];
          let dung = 0;
          c.de.forEach(function (q, j) {
            if (chuanHoa_(tl[c.id + '-' + (j + 1)]) === chuanHoa_(q.dung)) dung++;
          });
          hs.diem[c.id] = dung * DIEM_CAU;
          hs.thi.push(c.id);
        });
      });
      hocSinh.push(hs);
    }

    ghiRaw_(raw, META, i + 1, r, sid, trangThai, xuLi, cacCau);
  });

  const luc = Utilities.formatDate(new Date(), 'Asia/Ho_Chi_Minh', 'yyyy-MM-dd HH-mm');
  const thuMuc = DriveApp.createFolder('Kết quả CLB ' + luc);
  const ss = SpreadsheetApp.create('BANG_DIEM ' + luc);
  DriveApp.getFileById(ss.getId()).moveTo(thuMuc);

  // Bảng điểm
  const coThi = [];
  BUOI.forEach(function (d) { d.clubs.forEach(function (c) { if (c.de.length) coThi.push(c); }); });
  const bang = [['Mã HS', 'Họ tên'].concat(coThi.map(function (c) { return c.name; })).concat(['Số CLB đã thi'])];
  hocSinh.forEach(function (h) {
    bang.push([h.sid, h.ten].concat(coThi.map(function (c) {
      return h.diem.hasOwnProperty(c.id) ? h.diem[c.id] : '';
    })).concat([h.thi.length]));
  });
  ghiTrang_(ss.getSheets()[0].setName('Bảng điểm'), bang, false);

  // Sổ nhập CLB: MỘT tệp phần mềm nhận (bố cục như so_nhap.py của phần mềm).
  // Trang "2. Học sinh": mỗi em một dòng NV1, Điểm 1, NV2, Điểm 2…; nguyện
  // vọng các buổi nối nhau, điểm đặt ngay cạnh CLB em đã thi.
  // Sổ chọn CLB theo TÊN nên tên phải riêng: CLB cùng tên ở buổi khác
  // (vd "CLB Cờ vua" Thứ Hai và Thứ Năm) thêm tên buổi vào sau.
  const tenClb = {}, daDung = {};
  BUOI.forEach(function (d) {
    d.clubs.forEach(function (c) {
      let ten = c.name;
      if (daDung[ten.toLowerCase()]) ten = c.name + ' (' + d.ten + ')';
      if (daDung[ten.toLowerCase()]) ten = c.name + ' (' + c.id + ')';
      daDung[ten.toLowerCase()] = true;
      tenClb[c.id] = ten;
    });
  });
  const soNv = Math.max.apply(null, [1].concat(hocSinh.map(function (h) {
    return BUOI.reduce(function (n, d) { return n + (h.nv[d.ma] || []).length; }, 0);
  })));
  // Không có cột Nhóm ưu tiên: biểu mẫu không hỏi nhóm, và cột vắng mặt
  // nghĩa là phần mềm GIỮ nhóm đã gán (cột có mà ô trống thì là bỏ nhóm).
  const tHs = ['Mã HS', 'Họ tên'];
  for (let i = 1; i <= soNv; i++) tHs.push('NV' + i, 'Điểm ' + i);
  const soHs = [tHs].concat(hocSinh.map(function (h) {
    const row = [h.sid, h.ten];
    BUOI.forEach(function (d) {
      (h.nv[d.ma] || []).forEach(function (id) {
        row.push(tenClb[id] || id, h.diem.hasOwnProperty(id) ? h.diem[id] : '');
      });
    });
    while (row.length < tHs.length) row.push('');
    return row;
  }));

  ghiTrang_(ss.insertSheet('Cảnh báo'),
      [['Phiếu', 'Mã HS', 'Nội dung']].concat(canhBao.length ? canhBao : [['', '', 'Không có cảnh báo nào.']]), false);

  // Trang "1. CLB". Cột Chỉ tiêu để trống: nhà trường tự điền ngay trong sổ.
  const soClb = [['Tên CLB', 'Buổi', 'Chỉ tiêu', 'Suất ưu tiên', 'Nhóm ưu tiên', 'Mã CLB']];
  BUOI.forEach(function (d) { d.clubs.forEach(function (c) { soClb.push([tenClb[c.id], d.ma, '', '', '', c.id]); }); });

  SpreadsheetApp.flush();
  xuatExcel_(ss.getId(), thuMuc, 'BANG_DIEM.xlsx');
  taoSoNhap_(thuMuc, soClb, soHs);

  taoTepNap_(thuMuc, 'RAW_PHIEU', raw);
  taoTepNap_(thuMuc, 'DAP_AN', bangDapAn_());

  Logger.log('Đã chấm ' + hocSinh.length + ' học sinh.');
  Logger.log('Thư mục kết quả: ' + thuMuc.getUrl());
  if (canhBao.length) Logger.log('Có ' + canhBao.length + ' cảnh báo, xem trang "Cảnh báo" trong BANG_DIEM.xlsx.');
  Logger.log('Nhớ điền cột Chỉ tiêu ở trang "1. CLB" của SO_NHAP_CLB.xlsx rồi kéo sổ vào phần mềm.');
}

// ------------------------------------------------------------------------
// Dữ liệu raw và đáp án. Định dạng mô tả trong DINH_DANG_RAW.md: đổi cột ở
// đây thì phải sửa cả tài liệu đó, vì skill xử lí sau đọc theo tài liệu.

const COT_RAW = ['phieu_so', 'thoi_gian_nop', 'email', 'student_id', 'trang_thai_phieu',
  'ma_cau', 'loai_cau', 'buoi', 'club_id', 'cau_so', 'cau_hoi', 'tra_loi',
  'dap_an_dung', 'dung_sai', 'diem', 'diem_toi_da', 'diem_forms', 'duoc_tinh', 'ghi_chu'];

function moTaCau_() {
  const M = {student_id: {loai: 'thong_tin'}, name: {loai: 'thong_tin'}};
  BUOI.forEach(function (d) {
    M['di-' + d.ma] = {loai: 'dang_ky_buoi', buoi: d.ma};
    M[d.ma] = {loai: 'xep_hang', buoi: d.ma, d: d};  // bảng lưới của biểu mẫu cũ
    d.clubs.forEach(function (_, k) {
      M[d.ma + '-top-' + (k + 1)] = {loai: 'xep_hang', buoi: d.ma, top: k + 1};
    });
    M['chon-' + d.ma] = {loai: 'chon_thi', buoi: d.ma};
    M['thi-' + d.ma] = {loai: 'cong_thi', buoi: d.ma};
    d.clubs.forEach(function (c) {
      M['thi-sau-' + c.id] = {loai: 'cong_thi', buoi: d.ma};
      M['thi-' + c.id] = {loai: 'cong_thi', buoi: d.ma, club: c.id};  // biểu mẫu bản cũ
      c.de.forEach(function (q, j) {
        M[c.id + '-' + (j + 1)] = {loai: 'de_thi', buoi: d.ma, club: c.id, so: j + 1, dung: q.dung};
      });
    });
  });
  return M;
}

function ghiRaw_(raw, META, so, r, sid, trangThai, xuLi, cacCau) {
  let luc = '', email = '';
  try { luc = Utilities.formatDate(r.getTimestamp(), 'Asia/Ho_Chi_Minh', 'yyyy-MM-dd HH:mm:ss'); } catch (e) {}
  try { email = r.getRespondentEmail() || ''; } catch (e) {}
  const dau = [so, luc, email, sid, trangThai];

  cacCau.forEach(function (c) {
    const m = META[c.ma] || {loai: 'khac'};
    const dong = function (club, cauSo, traLoi, them) {
      raw.push(dau.concat([c.ma, m.loai, m.buoi || '', club || '', cauSo || '', c.cau, traLoi])
          .concat(them || ['', '', '', '', '', '', '']));
    };
    if (m.loai === 'xep_hang') {
      // Một dòng cho mỗi Top em đã chọn: club_id là CLB, trả lời là "Top k".
      if (m.top) {
        // Câu thả xuống của một Top: một dòng nếu em chọn một CLB.
        if (maClb_(c.tl)) dong(maClb_(c.tl), '', 'Top ' + m.top);
      } else {
        docTop_(m.d, c.tl).forEach(function (x) { dong(x.id, '', 'Top ' + x.top); });
      }
    } else if (m.loai === 'chon_thi') {
      // Một dòng cho mỗi CLB đã tick.
      [].concat(c.tl || []).forEach(function (v) { dong(maClb_(v), '', v); });
    } else if (m.loai === 'cong_thi') {
      // Trang chọn CLB làm bài: club_id là CLB em chọn, trống nếu em dừng.
      dong(maClb_(c.tl) || (c.tl === CO ? m.club : ''), '', c.tl);
    } else if (m.loai === 'de_thi') {
      const dung = chuanHoa_(c.tl) === chuanHoa_(m.dung) ? 1 : 0;
      const xl = trangThai !== 'giu' ? [0, trangThai] : (xuLi[m.club] || [0, 'khong_lam_bai']);
      dong(m.club, m.so, c.tl, [m.dung, dung, dung * DIEM_CAU, DIEM_CAU, c.diemForms, xl[0], xl[1]]);
    } else {
      dong(m.club, '', Array.isArray(c.tl) ? c.tl.join(' ; ') : c.tl);
    }
  });
}

function bangDapAn_() {
  const rows = [['buoi', 'ten_buoi', 'club_id', 'ten_clb', 'ma_cau', 'cau_so', 'cau_hoi',
    'lua_chon_a', 'lua_chon_b', 'lua_chon_c', 'lua_chon_d', 'dap_an_dung', 'diem']];
  BUOI.forEach(function (d) {
    d.clubs.forEach(function (c) {
      c.de.forEach(function (q, j) {
        const lc = q.opts.slice(0, 4);
        while (lc.length < 4) lc.push('');
        rows.push([d.ma, d.ten, c.id, c.name, c.id + '-' + (j + 1), j + 1, q.q]
            .concat(lc).concat([q.dung, DIEM_CAU]));
      });
    });
  });
  return rows;
}

function ghiTrang_(sh, rows, laChu) {
  const vung = sh.getRange(1, 1, rows.length, rows[0].length);
  // Tệp nạp ghi dạng chữ để mã như 001 không bị Sheets đổi thành số 1.
  if (laChu) vung.setNumberFormat('@');
  vung.setValues(rows);
  sh.setFrozenRows(1);
  sh.getRange(1, 1, 1, rows[0].length).setFontWeight('bold');
}

function taoTepNap_(thuMuc, ten, rows) {
  const tam = SpreadsheetApp.create(ten);
  ghiTrang_(tam.getSheets()[0].setName(ten), rows, true);
  SpreadsheetApp.flush();
  xuatExcel_(tam.getId(), thuMuc, ten + '.xlsx');
  DriveApp.getFileById(tam.getId()).setTrashed(true);
}

// Sổ nhập CLB: một tệp Excel hai trang "1. CLB" và "2. Học sinh".
function taoSoNhap_(thuMuc, soClb, soHs) {
  const tam = SpreadsheetApp.create('SO_NHAP_CLB');
  ghiTrang_(tam.getSheets()[0].setName('1. CLB'), soClb, true);
  ghiTrang_(tam.insertSheet('2. Học sinh'), soHs, true);
  SpreadsheetApp.flush();
  xuatExcel_(tam.getId(), thuMuc, 'SO_NHAP_CLB.xlsx');
  DriveApp.getFileById(tam.getId()).setTrashed(true);
}

function xuatExcel_(id, thuMuc, ten) {
  const url = 'https://docs.google.com/spreadsheets/d/' + id + '/export?format=xlsx';
  const res = UrlFetchApp.fetch(url, {
    headers: {Authorization: 'Bearer ' + ScriptApp.getOAuthToken()},
    muteHttpExceptions: true
  });
  if (res.getResponseCode() !== 200) {
    throw new Error('Không xuất được ' + ten + ' (mã lỗi ' + res.getResponseCode() + '). Chạy lại chamTheoCLB.');
  }
  thuMuc.createFile(res.getBlob().setName(ten));
}
"""


HTML = os.path.join(THU_MUC, "THIET_KE_6_PHAN.html")
M32 = 0xFFFFFFFF


def doc_du_lieu():
    """Bộ đề mẫu đã duyệt, đọc từ THIET_KE_6_PHAN.html.

    [(mã buổi, tên buổi, [(club_id, tên, [(câu, đáp án đúng, [lựa chọn])])])],
    đáp án đúng là lựa chọn đầu tiên trong dữ liệu gốc.
    """
    import re
    with open(HTML, encoding="utf-8") as f:
        html = f.read()
    m = re.search(r"const BUOI = (\[.*?\n\]);", html, re.S)
    if not m:
        raise SystemExit("Không tìm thấy dữ liệu BUOI trong THIET_KE_6_PHAN.html")
    return [(ma, ten, [(cid, name, [(q, ops[0], ops) for q, ops in de])
                       for cid, name, de in ds])
            for ma, ten, ds in json.loads(m.group(1))]


def xao(ds, hat_giong):
    """Bản Python của shuffled() trong THIET_KE_6_PHAN.html, cho ra cùng thứ tự."""
    h = 2166136261
    for c in hat_giong:
        h = ((h ^ ord(c)) * 16777619) & M32
    x = h or 1
    a = list(ds)
    for i in range(len(a) - 1, 0, -1):
        x ^= (x << 13) & M32
        x ^= x >> 17
        x ^= (x << 5) & M32
        j = x % (i + 1)
        a[i], a[j] = a[j], a[i]
    return a


def du_lieu_gs():
    """Bộ đề mẫu theo dạng BUOI của tệp .gs."""
    return [{"ma": ma, "ten": ten, "clubs": [
        {"id": cid, "name": name, "de": [
            {"q": q, "opts": xao(ops, cid + str(j)), "dung": dung}
            for j, (q, dung, ops) in enumerate(de)]}
        for cid, name, de in ds]}
        for ma, ten, ds in doc_du_lieu()]


TIEU_DE_MAC_DINH = "Đăng ký CLB và thi tuyển"


def noi_dung(du_lieu=None, tieu_de=TIEU_DE_MAC_DINH, diem=None, tran=None):
    """Nội dung tệp .gs. du_lieu theo dạng du_lieu_gs(); bỏ trống là bộ đề mẫu.

    Skill tao-google-form-clb gọi hàm này với dữ liệu nhà trường điền.
    """
    j = lambda x: json.dumps(x, ensure_ascii=False)  # noqa: E731
    return MAU % {
        "tieu_de": j(tieu_de),
        "diem": DIEM_CAU if diem is None else diem,
        "tran": TRAN_THI if tran is None else tran,
        "co_buoi": j(CO_BUOI), "khong_buoi": j(KHONG_BUOI),
        "co": j(CO), "khong": j(KHONG), "dung": j(DUNG),
        "khong_thi": j(KHONG_THI), "bo_trong": j(BO_TRONG),
        "buoi": json.dumps(du_lieu_gs() if du_lieu is None else du_lieu,
                           ensure_ascii=False, indent=1),
    }


def main():
    with open(RA, "w", encoding="utf-8") as f:
        f.write(noi_dung())
    print("Đã ghi %s" % RA)


if __name__ == "__main__":
    sys.exit(main())
