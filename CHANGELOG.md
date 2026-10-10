# CHANGELOG

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng S (/code-review trên vòng R: 6 điểm, không lỗi đúng/sai — vòng sạch)

- Không sửa hành vi. Ba điểm "móc lỗi chặn cả `import json`" là đúng hành vi: tệp `json.py` cạnh mã vẫn che được
  `json`, và lần chạy thật (thư mục đứng đầu sys.path) cũng hỏng ở chính móc đó — sai là ở LỜI: dòng CHANGELOG
  vòng R và chú thích test ghi "thư viện chuẩn" thay vì "dựng sẵn / đóng băng". Đã sửa lời (đánh dấu tại chỗ),
  docstring `_tu_thu_muc` (dòng tóm tắt còn ghi "nghi ngờ thì coi là có"), và thêm ca `import json` bị từ chối
  vào test làm chốt (228 ca, 2 bỏ qua tuỳ môi trường).
- `_khong_the_bi_che` nhớ theo tên (`functools.cache`).
- Bác: tên đã có trong `sys.modules` của tiến trình đo — `sys.modules` của lần chạy thật là của tiến trình khác;
  chỉ đáng kể khi có móc đường dẫn hỏng, đã báo lỗi rõ.
- Vòng lặp 2 dừng tại đây theo tiêu chí "một vòng không còn lỗi đúng/sai được xác nhận".

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng R (/code-review trên vòng Q: 6 điểm, sửa 5, bác 1)

Không điểm nào làm phép đo chạy nhầm mã; đều là chẩn đoán, độ chặt của test và một ca từ chối thừa hiếm gặp.
- `_chung`: lỗi khi xét một tên (móc đường dẫn hỏng với thư mục, lỗi trong bộ tìm / PathFinder) -> SystemExit nêu
  đúng tên và lỗi gốc, thay vì báo nhầm thành "mô-đun anh em"; lỗi móc với thư mục chỉ nêu khi thật sự cần xét
  một tên (mã chỉ import mô-đun dựng sẵn / đóng băng không bị chặn; *sửa ở vòng S: bản đầu ghi nhầm
  "thư viện chuẩn"*).
- Luật "dựng sẵn / đóng băng không bị che" còn một chỗ, đứng trước phép xét thư mục trong `la_ten`.
- Test (227 ca, 2 bỏ qua tuỳ môi trường): bộ tìm cài thêm ghi mọi tên ngoài thư viện chuẩn (không chỉ hai tên);
  ca lỗi PathFinder kiểm cả lỗi gốc và đặt mục lỗi cuối sys.path; 1 ca mới. 3 ca thất bại với bản vòng Q.
- Bác: PathFinder chạy các móc đường dẫn trên sys.path khi xét phần namespace — đó chính là việc mọi import của
  mã được đo làm trong cùng tiến trình; docstring ghi rõ điều này.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng Q (/code-review trên vòng P: 7 điểm, sửa 5, bác 2)

- `_chung`: mô-đun dựng sẵn / đóng băng ngoài `sys.stdlib_module_names` (`__phello__`, `xxsubtype`) lại được nhận
  (hồi quy của vòng P: bỏ ngoại lệ của vòng O mà không thay bằng `_khong_the_bi_che`).
- Móc đường dẫn ném lỗi khác ImportError với thư mục đã chọn -> SystemExit rõ (PathFinder cũng chỉ bỏ qua
  ImportError); mọi lỗi khi tìm phần namespace (kể cả PathFinder trên sys.path) -> coi là có, từ chối rõ — không
  còn traceback. Không móc nào nhận thư mục -> trả ngay hàm luôn "không".
- Test (226 ca, 2 bỏ qua tuỳ môi trường): 3 ca mới, đều thất bại với bản vòng P (đã kiểm là lỗi thật, không phải
  lỗi cú pháp của mã test); bộ tìm cài thêm trong test chỉ ghi tên đang xét (không bắt nhầm import khác);
  `_chay_tien_trinh_moi` nối mã test sau một dòng mới (mã bắt đầu bằng `def` / `try` không còn thành lỗi cú pháp
  lặng lẽ).
- Bác:
  - Không dùng `sys.path_importer_cache[thu_muc]` của tiến trình đo: lần chạy thật là một tiến trình khác, bộ
    nhớ đệm trống, dựng bộ tìm từ `sys.path_hooks` — đúng như kịch bản làm.
  - Mô-đun đóng băng ở tiến trình đo nhưng không đóng băng ở lần chạy thật với cờ / bản Python khác: như vòng O —
    phép đo chạy trong chính trình thông dịch này, đối chiếu là nạp bình thường trong cùng trình thông dịch.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng P (/code-review trên vòng O: 7 điểm, sửa 7)

- `_chung`: **rút lại** việc hỏi các bộ tìm cài thêm trong `sys.meta_path` (vòng O). Đã tái hiện: hỏi
  `DistutilsMetaFinder` của setuptools về `distutils` / `pip` làm đổi trạng thái tiến trình đo; một bộ tìm chuyển
  tiếp cho PathFinder (kiểu móc của pytest / typeguard) làm tệp `pytest.py` cạnh mã lọt qua — lần chạy thật thư
  mục đứng đầu sys.path nên chính bộ tìm đó trả tệp cạnh mã (đo nhầm mã, lặng lẽ).
- Luật mới, bảo thủ (nghi ngờ thì từ chối rõ, không bao giờ đo nhầm): chỉ mô-đun dựng sẵn / đóng băng (hai bộ
  tìm của CPython, không tác dụng phụ) được coi là không thể bị che; bộ tìm của thư mục dựng từ `sys.path_hooks`
  như PathFinder làm (móc đường dẫn kiểu Hy thêm đuôi mới cũng được tính), lỗi khi tìm thì coi là có; phần
  namespace chỉ được nhận khi PathFinder trên sys.path tìm được mô-đun / gói thường. Tên do bộ tìm cài thêm cung
  cấp mà thư mục cũng có thì bị từ chối (ca `hookmod/` của vòng O đổi từ "nhận" sang "từ chối, không gọi bộ tìm").
- Một hàm phân loại duy nhất (`_tu_thu_muc`, nhớ theo tên); bỏ `_bo_tim_truoc_cung_cap` và lần gọi lặp trong
  `la_ten`.
- Test (223 ca, 2 bỏ qua tuỳ môi trường): ca bộ tìm cài thêm của vòng O thay bằng 2 ca bảo thủ (kèm kiểm bộ tìm
  không bị gọi lần nào) + 1 ca `sys.path_hooks`; cả 3 thất bại với bản vòng O.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng O (/code-review trên vòng N: 7 điểm, sửa 5, bác 2)

- `_chung`: sửa tận gốc luật mô-đun anh em — bỏ các luật tự bắt chước hệ thống import (`_anh_em`,
  `_nap_truoc_filefinder`, `_mo_dun_thuong_ngoai`; bốn vòng K–N mỗi vòng lại thấy một chỗ lệch) và hỏi chính các
  bộ tìm theo đúng thứ tự import: bộ tìm trong `sys.meta_path` đứng trước PathFinder (dựng sẵn, đóng băng, móc
  cài thêm) → FileFinder của thư mục đã chọn → PathFinder trên sys.path (gói thường thắng phần namespace).
  Không gọi PathFinder với thư mục đã chọn (giữ sys.path_importer_cache sạch); kết quả nhớ theo tên trong một lần nạp.
- Tên do bộ tìm đứng trước PathFinder cung cấp được nhận (vòng N từ chối nhầm khi có thư mục dữ liệu cùng tên).
- Docstring `_import_la` theo luật mới. Test dựng sẵn / đóng băng bỏ qua trên trình thông dịch không đóng băng `os`.
- Test (221 ca, 2 bỏ qua tuỳ môi trường): 1 ca mới thất bại với bản vòng N; mọi ca của vòng K–N vẫn qua với
  cách làm mới (lưới hồi quy cho lần viết lại).
- Bác:
  - Tệp cạnh mã trùng tên mô-đun đóng băng trên một trình thông dịch KHÁC (phiên bản cũ, `-X frozen_modules=off`):
    kịch bản đo chạy mã trong chính trình thông dịch đang chạy; đối chiếu là nạp bình thường trong cùng trình
    thông dịch đó, không phải một bản Python khác.
  - Thư mục hiện hành nằm trên sys.path của tiến trình kiểm (`python -m`, pytest) che phần namespace: cách chạy
    ghi trong CLAUDE.md (`python <kịch bản> <thư mục>`) không đưa thư mục hiện hành vào sys.path; tình huống cần
    hai bản kho mã lệch nhau ở đúng một tên — xa thực tế, không đáng thêm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng N (/code-review trên vòng M: 8 điểm, sửa 5, bác 3)

- `_chung` (luật mô-đun anh em): mô-đun dựng sẵn / đóng băng (`time`, `os`…) xét TRƯỚC — BuiltinImporter /
  FrozenImporter chạy trước FileFinder nên tệp cùng tên cạnh mã không che được (vòng M từ chối nhầm). Thư mục
  không `__init__` cạnh mã chỉ được nhận khi tên là mô-đun / gói THƯỜNG trên sys.path (PathFinder); gói
  namespace đã cài thì thư mục được gộp vào (`nsgoi.helper` chạy thật lấy từ thư mục) — từ chối (vòng M nhận nhầm).
- Docstring `_import_la` theo luật hiện hành; `importlib.machinery.all_suffixes()`; `with os.scandir(...)`.
- Test (220 ca, 1 bỏ qua khi chạy bằng root): 2 ca mới, đều thất bại với bản vòng M.
- Bác, kèm đường đã lần:
  - Thoát tiến trình qua bí danh (`_s.exit`, `from os import _exit`, `os.abort`) và nhánh except ghi bằng
    thuộc tính / biến bộ (`except errors.ImportError`, `except _LOI`): luật import tuỳ chọn chỉ còn áp cho tên
    KHÔNG có trong thư mục; với tên đó, chạy thật và chạy dưới kịch bản tìm trên cùng sys.path nên hành xử
    giống nhau — sai ở đây chỉ làm thông báo lỗi muộn hơn, không làm phép đo đo nhầm mã. Theo dõi bí danh tốn
    mã hơn lợi ích.
  - Thư mục dữ liệu namespace (vd `mau_csv/`) trong try/except ImportError vẫn bị từ chối: chạy thật gán một
    gói namespace rỗng, dưới kịch bản gán None — hai lần chạy đi hai nhánh khác nhau, từ chối là đúng.
  - Chi phí stat cho mỗi thư mục con: vài chục lần stat mỗi lần nạp, không đáng kể.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng M (/code-review trên vòng L: 10 điểm, sửa 9, bác 1)

- `_chung` (luật mô-đun anh em) bám đúng FileFinder: tính cả bản biên dịch không nguồn (`.pyc`); tên tệp là
  phần trước ĐÚNG đuôi (tệp `random.old.py` không phải `random`); thư mục không có `__init__` chỉ là phần gói
  namespace — không che thư viện chuẩn / gói đã cài, chỉ bị coi là anh em khi tên không có ở đâu khác (vòng L
  từ chối nhầm mã hợp lệ khi có thư mục dữ liệu tên `random/`, `csv/`...).
- Import tuỳ chọn: thân lớp chạy ngay nên được đường lui che (vòng L từ chối nhầm); xét nhánh except ĐẦU TIÊN
  bắt được ImportError theo thứ tự (kể cả `except Exception`), nhánh kết thúc bằng ném lại hay
  `sys.exit` / `os._exit` / `exit` / `quit` không phải đường lui. Điều kiện động (`if STRICT: raise`) không xét
  được tĩnh — coi là đường lui, ghi trong docstring.
- Chỉ kiểm / biên dịch các mô-đun CÒN THIẾU (i18n_errors đã nạp đúng bản thì không đọc lại), dựng đủ rồi mới
  gán. Spec không có bộ nạp và `cached = None` (vòng L chỉ đặt `__cached__`, `__spec__` vẫn trỏ .pyc và
  `importlib.reload` đi vòng qua phép kiểm). `functools.cache` thay danh sách tự chế.
- Test (218 ca, 1 bỏ qua khi chạy bằng root): 8 ca mới thất bại với bản vòng L (ca gói thường `random/__init__.py` đã đúng từ vòng L, giữ
  làm chốt chặn khi thu hẹp luật thư mục).
- Bác: nhãn "ngoài sổ" trái quy tắc 1 của CLAUDE.md — quy tắc cho phép khi đã hỏi; việc này do Truong (chủ dự
  án) yêu cầu trực tiếp, nhãn ghi đúng điều đó.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng L (/code-review trên vòng K: 9 điểm, sửa 8, sửa một phần 1)

- `_chung` (kiểm import): thêm luật **mô-đun anh em** — tên có mặt trong thư mục đã chọn (tệp .py, mô-đun mở
  rộng, thư mục) mà không được phép thì luôn bị từ chối, kể cả nằm trong `try/except ImportError` hay trùng tên
  gói đã cài (vòng K để lọt: `try: import rbda_priority_pipeline` trong i18n_errors; tệp `openpyxl.py` cạnh mã).
  Import tuỳ chọn chỉ được che khi nằm trực tiếp trong khối try (không vào thân hàm / lớp định nghĩa ở đó) và
  nhánh except không chỉ ném lại; nhận cả `except*`. Danh sách gói đã cài quét một lần, chỉ khi cần.
- Kiểm và biên dịch CẢ HAI tệp trước khi chạy tệp nào (vòng K chạy i18n_errors rồi mới đọc mô-đun chính).
  Thông báo nêu đúng tệp được import gì (i18n_errors: không mô-đun nào của kho mã, vì nó nạp trước).
- `__cached__ = None` (không trỏ tới .pyc không tồn tại); `compile(..., dont_inherit=True)`.
- Test (209 ca): khôi phục test "không thêm mục cache bộ tìm" (bỏ ở vòng K là sai: nó chặn hồi quy kiểu chèn
  tạm sys.path); 9 ca mới, đều thất bại với bản vòng K.
- Bác phần còn lại của điểm 6 (không dùng bộ nhớ đệm .pyc): cố ý từ vòng H–I (bản .pyc cũ từng bị dùng nhầm);
  phân tích + biên dịch mô-đun chính tốn ~46 ms mỗi tiến trình, không đáng kể so với phép đo.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng K (/code-review trên vòng J: 10 điểm, sửa 9, bác 1)

- `_chung` (kiểm import tĩnh của vòng J): nhận cả gói đã cài trong site-packages (theo `importlib.metadata.packages_distributions`) — vòng J đã thu hẹp quá mức mà CHANGELOG không ghi; bỏ qua import tuỳ chọn trong khối `try/except ImportError`; `i18n_errors` (nạp trước) không được import `rbda_priority_pipeline` (sẽ lấy nhầm bản khác); import tương đối báo đúng tên mô-đun (`.helpers`, không phải `.helpers.f`); bỏ điều kiện thừa `__future__`.
- Kiểm và biên dịch NGAY LÚC NẠP từ đúng bản đã đọc (`compile(cây ast)` rồi `exec`): không còn khe giữa lúc kiểm và lúc chạy; lỗi đọc / cú pháp / byte NUL thành SystemExit rõ; đã nạp đúng thư mục thì trả bản đã nạp mà không đọc lại tệp.
- Test (199 ca): bỏ test cache không thể thất bại (vòng J); 5 test mới, đều thất bại với bản vòng J.
- Bác: một tệp tên trùng thư viện chuẩn (vd `random.py`) chen trên sys.path — mối nguy chung của mọi chương trình Python, ngoài phạm vi kịch bản; phép kiểm theo đường dẫn của vòng I từng có báo nhầm nặng hơn.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng J (/code-review trên vòng I: 9 điểm, sửa 9)

- `_chung`: đính chính vòng I — phép kiểm "mô-đun anh em" chạy SAU khi nạp nên bỏ lọt import bên trong hàm (đúng kiểu import của mã này; đã tái hiện), từ chối nhầm mô-đun C của thư viện chuẩn trên Windows (`<base>\DLLs`), không dùng tham số `thu_muc`, và để lại mô-đun lạ trong sys.modules. Thay bằng kiểm TĨNH trước khi chạy gì: đọc cả hai tệp nguồn bằng `ast`, lấy mọi import (đầu tệp lẫn trong hàm, kể cả import tương đối) và từ chối tên không thuộc `sys.stdlib_module_names` hay `i18n_errors` / `rbda_priority_pipeline`. Bỏ `_thu_muc_chuan`, `_phu_thuoc_la` (không còn đoán theo đường dẫn, không còn sysconfig). Hai tệp thật của kho qua kiểm (không import lạ).
- Test (195 ca): 4 ca import lạ (đầu tệp, trong hàm, anh em ngay thư mục chọn, import tương đối — đều thất bại với bản vòng I) và kiểm không mô-đun nào bị nạp; 1 ca nhận mô-đun C của thư viện chuẩn; 1 ca thư mục chưa có mục cache vẫn không có sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng I (/code-review trên vòng H: 9 điểm, sửa 8, bác 1)

- `_chung.nap_rb` (thư mục), sửa tận gốc theo điểm "sai tầng": bỏ hẳn cơ chế đoán tệp Python sẽ nạp (`sys.path_hooks`, bộ tìm riêng, các ca .so / gói / namespace — thêm dần từ vòng C tới H). Nay nạp THẲNG `<thư mục>/<tên>.py` bằng `spec_from_file_location`: bản biên dịch cũ, gói cùng tên, gói namespace nằm cạnh không thể chen vào; không đụng sys.path hay cache bộ tìm; không còn đường lỗi traceback từ bộ tìm hay loader cũ. Đổi hành vi có chủ đích: thư mục chỉ có bản biên dịch không kèm nguồn (.pyc) nay bị TỪ CHỐI (kịch bản đo mã nguồn) — đảo lại phần nhận .pyc của vòng C–D.
- Mới: nếu mã được nạp import thêm mô-đun ngoài thư viện chuẩn / site-packages (vd một phiên bản khác import mô-đun anh em, lấy nhầm từ thư mục khác trên sys.path), từ chối thay vì đo lẫn mã. Mã hiện tại chỉ import thư viện chuẩn và `i18n_errors` (đã kiểm).
- Test (190 ca): viết lại nhóm test bộ nạp thư mục theo thiết kế mới (8 test thất bại với bản vòng H vì hành vi đổi có chủ đích hoặc vì mô-đun anh em trước đây lọt).
- Bác: khoá import và "đọc lại sys.modules sau exec" của bộ import — kịch bản chạy một luồng, và `_nap_co_kiem` đã kiểm nguồn của mục sys.modules sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng H (/code-review trên vòng G: 6 điểm, sửa 6)

- `_chung.nap_rb` (thư mục), sửa tận gốc: không còn import theo tên qua sys.path nữa. Hỏi bộ tìm mà CHÍNH Python dùng (gọi `sys.path_hooks` như PathFinder, kể cả hook tuỳ biến, nhưng tạo mới và không ghi cache) lấy spec cho từng mô-đun, rồi nạp ĐÚNG spec đó (`module_from_spec` + `exec_module`, đặt vào sys.modules trước như import). Hệ quả: dự đoán và lần nạp thật không thể lệch; bỏ toàn bộ phần sửa / khôi phục sys.path và `sys.path_importer_cache` (vòng G bỏ sót bước xoá mục cũ trước khi import nên có thể đi qua bộ tìm cũ hoặc mục None — đã tái hiện bằng test); thư mục mất quyền giữa chừng vẫn báo lỗi đọc.
- Test (193 ca): test cache tự gieo mục sẵn có (không còn đúng vô nghĩa khi cache trống); test thư mục đã ở trên sys.path với mục cache cũ None (thất bại với bản vòng G).

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng G (/code-review trên vòng F: 8 điểm, sửa 7, bác 1)

- `_chung`: đính chính vòng F — `nap_rb` vẫn để lại bộ tìm tệp của thư mục trong `sys.path_importer_cache` (vòng F chỉ dọn ở `_tep_se_nap`; đã tái hiện). Nay `_tep_se_nap` dùng một `FileFinder` RIÊNG (cùng thứ tự loại tệp như mặc định) nên không đụng cache toàn cục, và bước import của `nap_rb` trả mục cache về như cũ (không để lại cho thư mục tạm, không thay bộ tìm sẵn có). Kiểm đọc được thư mục bằng `os.scandir` (rẻ); lỗi OSError khi tìm thành SystemExit; docstring nói rõ thư mục không có `<tên>.py` thì nhận đúng thứ Python nạp.
- Test (192 ca): test chmod 000 thật (bỏ qua khi chạy root hay Windows; CI Linux chạy được); `.pyc` trong `__pycache__` bỏ qua khi `cache_tag` là None; 2 test cache bộ tìm (thất bại với bản vòng F); test giả lập lỗi quyền đổi sang `os.scandir` (thất bại với bản vòng F chỉ vì vòng F dùng `os.listdir`).
- Bác: thư mục chỉ có gói `rbda_priority_pipeline/__init__.py` (không có `.py`) được nhận — đúng ý: đó là mã Python sẽ chạy khi import từ thư mục đó; docstring đã ghi rõ.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng F (/code-review trên vòng E: 7 điểm, sửa 6, bác 1)

Không điểm nào làm phép đo sai; đều là thông báo lỗi và độ vững của test.
- `_chung._tep_se_nap`: thư mục không đọc được báo đúng "Không đọc được thư mục" (FileFinder nuốt lỗi quyền rồi trả None nên trước đây báo nhầm "không có mô-đun"); tạo bộ tìm tệp mới mỗi lần và không để lại trong `sys.path_importer_cache`; thông báo nêu cả khả năng "gói cùng tên nằm cạnh". `nap_rb` kiểm mô-đun chính trước, nên thư mục sai báo thiếu `rbda_priority_pipeline`.
- Test (190 ca): test `__pycache__` ghi .pyc vào đúng chỗ và kiểm là có (không thành vô nghĩa khi đặt PYTHONPYCACHEPREFIX); 4 test mới, đều thất bại với bản vòng E.
- Bác: gọi `nap_rb` lần hai trên cùng thư mục sau khi tệp trong đó đổi giữa chừng thì bị từ chối — chỉ là từ chối (đòi tiến trình mới), không bao giờ đo nhầm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng E (/code-review trên vòng D: 8 điểm, sửa 7, bác 1)

- `_chung.nap_rb`, sửa tận gốc: bỏ các luật đoán theo tên tệp (`_co_mo_dun`, phần tiền tố của `_cung_nguon`); hỏi chính bộ import của Python (`importlib.machinery.PathFinder.find_spec`) tệp nào sẽ được nạp từ thư mục, rồi đòi đúng tệp đó sau khi nạp. Hệ quả: .pyc có thẻ trong `__pycache__` (Python không nạp) và hậu tố mở rộng của hệ khác không còn bị nhận nhầm; thư mục chỉ có `__pycache__` báo SystemExit rõ thay vì traceback; bản mở rộng cũ chen trước tệp nguồn vẫn bị từ chối; gói namespace bị chặn ngay ở bước kiểm trước (không phụ thuộc sys.path của máy); thông báo nêu đúng tệp mong đợi; lỗi đọc thư mục thành SystemExit; thông báo "đã nạp nơi khác" nêu nguồn thật (gói namespace, mục None).
- Test (186 ca): 2 test cho hàm mới `_tep_se_nap` (thất bại với bản vòng D chỉ vì hàm chưa có) và 1 test hành vi qua `nap_rb` (thất bại thật với bản vòng D).
- Bác: điểm cũ float và điểm mới Decimal cùng giá trị bị coi là "đổi" — giữ, vì đổi kiểu có thể đổi thứ hạng thật: `Decimal('7.1') > 7.1` (float 7.1 là 7,0999…), nên từ chối là đúng.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng D (/code-review trên vòng C: 6 điểm, sửa 6)

- `_chung.nap_rb`: sửa lỗi do vòng C đưa vào — khi thư mục CÓ `<tên>.py`, chỉ nhận đúng tệp đó; một bản biên dịch cũ (.so/.pyd) nằm cạnh mà Python ưu tiên nạp trước bị từ chối (trước đây vòng C nhận nó và đo nhầm mã cũ). Bản biên dịch không kèm nguồn chỉ được nhận khi KHÔNG có .py, nay cho cả mô-đun chính; gói namespace chen vào được nêu đúng nơi (thay vì "None").
- `exp_resume.kiem_tien_de`: nhận điểm Decimal (không là numbers.Real); chỉ kiểm điểm của dữ liệu mới (điểm em cũ đã phải bằng hệt dữ liệu cũ).
- Test (184 ca): bỏ test tiền đề không có khẳng định (luôn xanh), giữ lý do thành chú thích; 4 test mới, đều thất bại với bản vòng C.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng C (/code-review trên vòng B: 8 điểm, sửa 7, bác 1)

- `exp_resume.kiem_tien_de`: một luật `_so_hop_le` cho mọi số mà `compute_club_priority` sắp (số bốc thăm và điểm): điểm là chuỗi CSV, None, bool, pd.NA hay NaN đều bị từ chối bằng ValueError rõ (trước đây chuỗi / None lọt kiểm rồi gây TypeError giữa `resume_da` — đã tái hiện).
- `_chung.nap_rb`: nhận bản biên dịch không kèm nguồn (`i18n_errors.pyc` trong đúng thư mục) thay vì báo "nạp nhầm"; thông báo lỗi sau khi nạp nêu đúng nguồn thực và nguồn mong đợi.
- Test (181 ca): test tiền đề về NaN chuyển thành tự bỏ qua nếu sau này mã sản phẩm xử lý NaN xác định (không chặn bản sửa đúng); thêm 8 ca điểm không hợp lệ (2 ca NaN thất bại với bản vòng B chỉ vì đổi thông báo lỗi; 6 ca chuỗi / None / bool là lỗi thật) và 1 ca `.pyc`.
- Hồ sơ: đính chính câu "6 test mới đều thất bại" của vòng B; cập nhật ngày ở TIEN_DO.md.
- Bác: từ chối NaN cả ở điểm không ảnh hưởng thứ hạng (em không có trong apps, điểm nhập trước của em mới) — giữ, vì thận trọng: chỉ tốn một lần chạy lại toàn bộ, không bao giờ cho kết quả sai.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng B (/code-review trên vòng A: 7 điểm, sửa 5, bác 2)

- `_chung.nap_rb`: kiểm SAU khi nạp rằng mỗi mô-đun đến đúng từ thư mục / bản build đã chọn — thư mục thiếu `i18n_errors.py` trước đây lặng lẽ lấy tệp cùng tên ở chỗ khác trên sys.path (đã tái hiện), nay từ chối và gỡ mô-đun; mục sys.modules không rõ nguồn (None, mô-đun giả) báo rõ; tệp build không chứa mô-đun cần thiết báo SystemExit thay vì KeyError.
- `exp_resume.kiem_tien_de`: TỪ CHỐI điểm NaN (cả em cũ lẫn em mới) — `compute_club_priority` cho thứ tự phụ thuộc thứ tự đầu vào khi có NaN (đã tái hiện), nên vòng A coi NaN == NaN là sai; chưa nạp mô-đun rbda là RuntimeError (lỗi cài đặt, để người gọi bắt ValueError rồi chạy lại toàn bộ không nuốt mất).
- Test (174 ca): 7 test mới — 6 thất bại với bản vòng A; 1 là test tiền đề chỉ chạy mã sản phẩm (`compute_club_priority` với NaN) nên không phân biệt hai bản (đính chính ở vòng C).
- Bác: (1) em mới đã có trong apps/điểm của dữ liệu cũ làm `resume_da` lệch — thử 5.000 thể hiện ngẫu nhiên có trường hợp này: 0 lệch; (2) bản nhanh gọi `club_choice_function` một lần mỗi CLB làm chậm — đo 10.000 HS: 0,037 s so với 0,034 s, không đáng kể so với giá trị (khớp mọi kiểm tra đầu vào của bản gốc).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng A (2 lần /code-review trên 2386dd7: 20 điểm ~15 khác nhau)

Quyết định của Truong: KHÔNG sửa mã sản phẩm (phân xử em không có thứ hạng trong `club_choice_function` vẫn hoãn); lặp tới khi một vòng không còn lỗi đúng đắn.
- `exp_resume.kiem_tien_de`: mọi vi phạm là ValueError (kể cả chưa nạp rbda); bỏ em mới ở CẢ dữ liệu cũ khi so điểm / apps (điểm nhập trước cho em đến muộn không còn báo nhầm "em cũ đổi"); nhóm dự trữ '' và None coi như một (như `default_reserve_eligible_fn`); điểm NaN không đổi không bị báo đổi; kiểm thứ tự bốc thăm sắp một lần; `resume_test` dùng bản rbda đã nạp.
- `de_xuat_verify_nhanh.py`: lần đầu xét mỗi CLB, gọi đúng lời gọi `club_choice_function` của bản gốc (đang giữ + ứng viên, hàm đủ tư cách và thứ hạng thật) — mọi kiểm tra đầu vào, hiện tại và sau này, chạy y hệt.
- `_chung.py`: một hàm `_nap_co_kiem` cho cả thư mục lẫn bản build (kiểm "đã nạp nơi khác", trả bản đã nạp, gỡ mô-đun dở dang); thư mục lấy theo đường dẫn người dùng đưa (không theo đích liên kết); đường dẫn không tồn tại báo rõ; đọc được tệp PyInstaller < 6 (mục `PYZ-00.pyz`, mục lục dict).
- Test (169 ca): 7 test mới, đều thất bại với bản trước; chuỗi so lỗi chính xác ("thứ tự bốc thăm"); đường dẫn Windows dự phòng thật sự viết khác.
- Bác: gộp đoạn mồi 4 dòng (lý do như trước); thay `compute_club_priority` bằng chèn bisect trong `resume_da` (ghi ở DOI_CHIEU, để khi làm G1); sửa phân xử trong `club_choice_function` (chủ dự án hoãn).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 4 (/code-review trên vòng 3: 9 điểm, sửa 8, bác một phần 1)

- `exp_resume.kiem_tien_de`: số bốc thăm phải là số thực (không chuỗi CSV, không bool, không NaN) — báo ValueError rõ; kiểm sức chứa dùng bản rbda đã nạp kể cả khi `exp_resume.rb` chưa gán (trước đây lặng lẽ bỏ qua).
- `_chung.nap_rb`: so đường dẫn như hệ điều hành (liên kết, hoa/thường Windows) khi nạp lại cùng .exe; nhánh thư mục nạp hỏng cũng gỡ mô-đun dở dang như nhánh bản build.
- Test (162 ca): lần đầu có test cho đường nạp `.exe` (tệp PyInstaller tối thiểu dựng trong test): nạp, nạp lại qua đường dẫn khác, nạp hỏng không để mô-đun dở dang, lệch phiên bản Python; danh sách cấm cả `.index`/`.count`; dùng đúng một bản `_chung` trong tiến trình; sửa chú thích sai (v + 20).
- Bác một phần: kiểm sức chứa trong `kiem_tien_de` lặp lại luật của `club_choice_function` — giữ, vì cần nêu tên CLB trước khi làm việc và chỉ tốn một lần gọi mỗi CLB.

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)

- `exp_resume.kiem_tien_de`: nhận số bốc thăm kiểu số bất kỳ (numpy.int64...), chỉ thiếu / None mới là lỗi; báo rõ CLB có sức chứa mới không hợp lệ (giảm dưới suất dự trữ) thay vì lỗi chung chung về sau.
- `_chung.nap_rb`: thư mục — luôn nạp cả `i18n_errors` từ cùng thư mục (kể cả khi mô-đun chính đã có sẵn); bản build — nạp lại cùng tệp .exe trả bản đã nạp thay vì từ chối; nạp hỏng thì gỡ mô-đun dở dang khỏi sys.modules.
- Test (154 ca): test khoá phá hoà nay phân biệt được bản đúng với bản cũ (thêm ca tách cặp trùng giữ thứ tự, bản chỉ so số bốc thăm từ chối nhầm; đã thử đột biến); bỏ test đo giây, thay bằng danh sách cấm tra `in` (bảo đảm không quét danh sách); dùng chung bộ nạp `_chung.nap_canh`.
- Bác: (1) `verify_stability_nhanh` import `i18n_errors` theo tên — giống hệt bản gốc `verify_stability`, và `nap_rb` bảo đảm cùng thư mục; (2) sửa cách phân xử em không có thứ hạng trong `club_choice_function` — mã sản phẩm, cần mục trong sổ (đã ghi ở DOI_CHIEU_KHO_MA.md).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)

- `exp_resume.kiem_tien_de`: so thứ tự bốc thăm bằng đúng khoá phá hoà của `compute_club_priority` (số bốc thăm, mã em) — số trùng trước đây lọt kiểm; thiếu hoặc rỗng số bốc thăm báo ValueError rõ thay vì KeyError/TypeError.
- `de_xuat_verify_nhanh.py`: luôn gọi hàm đủ tư cách cho ứng viên như bản gốc (trước đây bỏ qua khi CLB còn chỗ, nên lỗi của hàm đó không lộ ra giống bản gốc).
- `_chung.nap_rb`: từ chối cả `i18n_errors` nạp từ nơi khác; bỏ đường dẫn khỏi sys.path sau khi nạp; bản build từ chối khi tiến trình đã nạp mô-đun, và `__file__` của mô-đun nạp từ .exe là đường dẫn ảo trong tệp .exe (trước đây là đường dẫn tương đối, có thể trùng tệp của kho).
- Test: 150 ca; bỏ ngưỡng giây tuyệt đối (chập chờn trên CI), thay bằng tỉ lệ thời gian khi dữ liệu gấp 8 lần.
- Bác: gộp đoạn mồi nạp `_chung` (5 dòng) trong hai kịch bản — không gộp được mà không sửa sys.path (chính là lỗi đã sửa ở vòng trước).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)

- `exp_resume.py` (G1), sửa tận gốc: `resume_da(res0, cu, moi, new_ids)` nhận cả dữ liệu cũ lẫn mới; `kiem_tien_de` (O(dữ liệu), dùng tập hợp) kiểm và TỪ CHỐI với thông báo rõ mọi thay đổi không phải "thêm ràng buộc": em nộp lại / mã trùng, đóng CLB, tăng sức chứa, đổi dự trữ, đổi nguyện vọng / điểm / nhóm / thứ tự bốc thăm của em cũ, em cũ xếp CLB mới mở, apps thiếu nguyện vọng (kể cả res0 lập từ apps thiếu). Hỗ trợ thêm GIẢM sức chứa (chọn lại trên tập đang giữ). Em mới không có dòng nguyện vọng không còn KeyError. `resume_test` đo riêng thời gian kiểm tiền đề.
- `de_xuat_verify_nhanh.py` (Z4): chữ ký trùng `verify_stability` (bỏ tham số `err`, dùng `err` của i18n_errors); chuẩn bị từng CLB một cách lười (chỉ CLB thật sự được xét, như bản gốc); kiểm sức chứa bằng `club_choice_function` của mô-đun đã nạp với ứng viên thật.
- `_chung.py`: `nap_canh` là bản duy nhất của bộ nạp theo đường dẫn; `nap_rb(thu_muc)` báo lỗi khi tiến trình đã nạp bản từ nơi khác (trước đây lặng lẽ trả bản cũ); bản build: báo rõ khi lệch phiên bản Python, đọc được mục lục PYZ dạng dict của PyInstaller cũ.
- `kiem_verify_nhanh.py`: `is not None` khi chọn em để hoán đổi.
- Test: 145 ca (vi sai tiếp tục/chạy lại có giảm sức chứa, CLB mới, em không nguyện vọng; một ca từ chối cho mỗi vi phạm; kiểm tiền đề tuyến tính; bản nhanh không đọc CLB không ai xét; `nap_rb` cùng thư mục / khác thư mục / tiến trình mới).
- Kiểm vi sai ngoài bộ test: `resume_da` = `run_rbda` trên 20.000 thể hiện ngẫu nhiên (có giảm sức chứa, CLB mới); bản nhanh = bản gốc trên 60.000 thể hiện (gồm 3.195 ca sức chứa sai, cùng thông báo lỗi).
- Chưa sửa (mã sản phẩm, cần mục trong sổ): `club_choice_function` xếp em không có thứ hạng bằng `len(rank)` rồi theo thứ tự pool — ghi trong DOI_CHIEU_KHO_MA.md.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)

- `de_xuat_verify_nhanh.py` (Z4): không còn nhập `loi_suc_chua` theo tên và không chép thông báo lỗi; kiểm sức chứa bằng chính `club_choice_function` của mô-đun đã nạp (kho mã hay bản build cũ), nên cùng luật, cùng thông báo.
- `exp_resume.py` (G1): `is not None` ở mọi chỗ (trước đây `held` và `nxt` lệch nhau với CLB có mã rỗng); bỏ ID CLB không tồn tại khỏi tập tính lại thứ hạng; CLB mới sau lần chạy cũ không còn KeyError; em không có dòng nguyện vọng dùng `prefs.get(s, [])` như `run_rbda`.
- `kiem_verify_nhanh.py`, `exp_resume.py`: nạp `_chung` và bản nhanh theo đường dẫn (không sửa sys.path); phần chạy của `kiem_verify_nhanh.py` đặt trong `main()`.
- `tests/test_tham_khao_verify_nhanh.py`: 85 ca (86 sau rà soát bổ sung). Thêm biến đổi kết quả làm CLB thừa/thiếu người, bỏ chỗ; ca thật "em trong nguyện vọng nhưng không trong apps"; dự trữ 0 / một phần / bằng sức chứa; so thông báo lỗi; em mới có diện dự trữ và điểm thi, CLB mới, nguyện vọng trỏ CLB không có, em không có nguyện vọng; kiểm `nap_rb` và `gen`; kiểm phép so sánh không rỗng. Nạp kịch bản theo đường dẫn. 16 ca thất bại với bản `exp_resume.py` trước sửa.
- Rà soát bổ sung (Sonnet, kiểm vi sai ngẫu nhiên): bản nhanh khớp bản gốc trên 600.000 thể hiện (kể cả thứ hạng trùng, sức chứa sai); `resume_da` lệch chạy lại khi em có trong nguyện vọng nhưng không trong apps (em không thứ hạng trùng nhau, phân xử theo thứ tự pool). Đường thật không có ca này (`hop_ung_vien`); `resume_da` nay ghi rõ tiền đề và từ chối dữ liệu như vậy; thêm test phản ví dụ (86 ca).
- Tài liệu: mã tiến độ `RS` (không có trong sổ) đổi thành `GĐ0`; số test trong CLAUDE.md đếm lại; sửa hai dòng mâu thuẫn / lỗi thời trong `DOI_CHIEU_KHO_MA.md`.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)

- `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản đề xuất cho Z4): khớp `club_choice_function` ở mọi ca biên — em đang giữ chỗ không có trong `base_rank` xếp cuối (`rank.get(s, len(rank))`) thay vì ném KeyError; thứ hạng trùng dùng `bisect_right` (khớp sắp xếp ổn định; test mới tìm ra lệch khi dùng `bisect_left`); kiểm `loi_suc_chua` và ném cùng ValueError; `is not None` khi gom em đang giữ; gọi hàm đủ tư cách một lần cho mỗi em.
- `exp_resume.py` (nguyên mẫu G1): bỏ qua nguyện vọng trỏ tới CLB không tồn tại như `run_rbda`; nhập được từ test (phần chạy đặt trong `__main__`, numpy chỉ nạp khi đo).
- Mới `docs/ke_hoach/tham_khao/_chung.py`: một bản duy nhất của bộ nạp `nap_rb` (báo lỗi rõ khi tệp không phải PyInstaller) và bộ sinh `gen`; bỏ bản sao và import thừa trong hai kịch bản.
- `pyproject.toml`: bỏ loại trừ ruff cho `docs/ke_hoach/tham_khao` (đã sửa lỗi lint); giữ loại `docs/*` khỏi đo phủ.
- Test mới `tests/test_tham_khao_verify_nhanh.py` (43 ca, không cần numpy).
- `CLAUDE.md`: cập nhật bản đồ mã theo kho (api.py L784–1364, rollback L1107–1119, `_BANG_RANG_BUOC`, Sổ nhập), số test, thời gian chạy, lệnh verify cần numpy, `CHANGELOG.md`.
- Chạy lại: `kiem_verify_nhanh.py` → `TAT_CA_GIONG_NHAU True` (7/7); `exp_resume.py` → 38/38 khớp chạy lại.

## 2026-10-08 — Giai đoạn 0 (chỉ đọc và đo)

- Môi trường: `.venv` (Python 3.11.17) cài `requirements-dev.txt` và `numpy`; `matching` 1.4.3 cài thêm chỉ để so sánh sau này (Q5), không thêm vào requirements.
- Gói kế hoạch đã có trước đó (commit 7c4f423): `CLAUDE.md`, `docs/ke_hoach/*`, và các loại trừ trong `pyproject.toml` (ruff: `docs/ke_hoach/tham_khao`; phủ: `docs/*`). Giai đoạn 0 không sửa các tệp này.
- Thêm `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`: đối chiếu 33 mục của sổ với kho, kết quả đo và trả lời câu hỏi mở mục 9 của `BOI_CANH_DU_AN.md`.
- Cập nhật `docs/ke_hoach/TIEN_DO.md`: GĐ0 xong; Z1–Z7 đánh dấu chưa.
- Không sửa mã sản phẩm (`.py`, `.js`, `.html`, `.css`).

Số đo chính (dữ liệu mô phỏng):
- Bộ test: 1.287 ca đạt, 0 hỏng, 0 bỏ qua, 0 lỗi; phủ 91,06 %; thời gian 1.352 s. Ruff: sạch.
- Verify nhanh: khớp hoàn toàn ở 7/7 cấu hình (`TAT_CA_GIONG_NHAU True`); 10.000 HS: 6,53 s so với 0,042 s.
- 5.000 HS, 10 CLB: `run_rbda` 0,18 s; `verify_stability` 2,09 s (≈92 % thời gian kiểm tra); 0 cặp phá vỡ.
- Tiếp tục DA từ trạng thái cũ: khớp chạy lại 38/38 lần.
- Sổ 33 mục: 29 đúng, 3 khác (Z1, Z4, Z6), 1 sai (C1).
