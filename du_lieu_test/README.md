# Bộ dữ liệu chạy thử

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
>
> Toàn bộ tên và mã trong thư mục này do máy sinh ngẫu nhiên (seed cố định).
> Hơn nữa bộ này được **cố ý thiết kế cho cạnh tranh cao** để cơ chế thuật toán
> lộ ra — nó không mô phỏng một phân bố nguyện vọng tự nhiên. Trình bày các con
> số này như số liệu khảo sát thật là **bịa đặt dữ liệu**.

## Thả vào phần mềm: Sổ nhập CLB

Giao diện chỉ nhận **Sổ nhập CLB** (một tệp Excel). Mỗi bộ dưới đây có sẵn bản sổ:

| Sổ | Bộ | Dùng để |
|---|---|---|
| `SO_NHAP_TEST.xlsx` | `TEST_01–03`: 120 em, 10 CLB, cạnh tranh cao | Chạy thử, kết quả đúng ở mục dưới |
| `SO_NHAP_CO_LOI_CO_Y.xlsx` | 10 em, **cố ý sai 5 chỗ** | Xem bảng lỗi: phần mềm phải liệt kê đủ 5 lỗi kèm dòng và **không nạp gì** |
| `bo_sach/SO_NHAP_SACH.xlsx` | 140 em, 12 CLB | Chạy thử, 0 cảnh báo |
| `vi_du_huong_dan/SO_NHAP_VIDU.xlsx` | 10 em, 4 CLB | Đi kèm `HUONG_DAN_SU_DUNG.md` |

Năm lỗi cài sẵn trong `SO_NHAP_CO_LOI_CO_Y.xlsx`: NV ghi tên một CLB không có
(`CLB Bóng chuyền`), một ô điểm ghi chữ (`tám`), một mã HS lặp hai dòng, một CLB
chọn hai lần trên cùng dòng, một CLB có Chỉ tiêu bằng 0.

Các sổ sinh bằng `mau_csv/tao_so_nhap.py` từ đúng các tệp dưới đây.

## Bốn file gốc (định dạng nội bộ)

`TEST_01–04` là định dạng ba tệp cũ: phần mềm còn đọc được qua các hàm nạp bên
trong (bộ test dùng), nhưng **giao diện không nhận** — dùng `SO_NHAP_TEST.xlsx`.

| File | Nội dung | Dùng để |
|---|---|---|
| `TEST_01_danh_sach_CLB.xlsx` | 10 CLB, tổng 130 suất, 4 CLB có suất dự trữ | Nạp **đầu tiên** |
| `TEST_02_chon_CLB_muon_thi.xlsx` | 120 học sinh, mỗi em thi 2–5 CLB, **kèm sẵn 396 ô điểm** | Nạp thứ hai |
| `TEST_03_xep_hang_nguyen_vong.xlsx` | Cùng 120 em, mỗi em 2–5 nguyện vọng | Nạp thứ ba |
| `TEST_04_CO_LOI_CO_Y.xlsx` | 10 dòng, cố ý sai 6 chỗ | Kiểm tra phần mềm **có cảnh báo không** |

Mỗi file có sheet **“Ghi chú”** giải thích nội dung ngay trong file.

> ### Chỉ muốn thử đường nạp → chạy → xuất, không muốn thấy cảnh báo nào?
>
> Dùng thư mục **[`bo_sach/`](bo_sach/README.md)** — 3 file, 140 học sinh,
> 12 CLB, **không có file lỗi nào lẫn vào**. Thả cả thư mục cũng ra **0 cảnh
> báo** và xếp được **140/140** em.
>
> `TEST_04` dưới đây **cố ý sai**. Thả nó cùng lúc với ba file kia là phần mềm
> kêu — đúng như thiết kế, không phải phần mềm hỏng.
>
> Và nhớ **đổi tên `app.db` cũ đi trước khi nạp bộ sạch**: phần mềm cộng thêm
> học sinh chứ không xoá em cũ, nên `HS204` của `TEST_04` sẽ còn kêu mãi.

## Hai đường thử khác nhau

- **Nạp tệp** — bốn tệp `.xlsx` ở trên, dùng ô kéo-thả. Đường mà nhà trường
  thật sự sẽ dùng khi có sẵn dữ liệu từ Microsoft Forms.
- **Gõ tay** — xem `NHAP_TAY.md`: 8 học sinh, 3 CLB, gõ trong ~15 phút. Kiểm tra
  các màn hình *Quản lý club*, *Nhập dự phòng tại kiosk*, *Chấm điểm* — những
  màn hình mà đường nạp tệp **không** đụng tới. Bộ này nhỏ đủ để tự tính kết quả
  bằng tay rồi đối chiếu với máy.

## Chạy thử bộ cạnh tranh (TEST_01–03)

1. Kéo `SO_NHAP_TEST.xlsx` vào ô thả file, bấm **Nhập sổ**.
2. **Không cần chấm điểm.** Điểm nằm sẵn trong sổ (cạnh từng nguyện vọng); nạp
   xong là bảng *Cảnh báo dữ liệu* phải hiện **0 cảnh báo**.
3. Bấm **Chạy phân bổ**.
4. Bấm **Xuất kết quả**.

**Kết quả đúng phải ra như sau** (đã kiểm chứng với `seed=42`):

| | |
|---|---|
| Được xếp | **108 / 120** — 12 em vào `_chua_duoc_xep.csv` |
| Nguyện vọng 1 | 64 em (59%) · NV2: 28 · NV3: 10 · NV4: 6 |
| Vào bằng **suất dự trữ** | **10 em** |
| CLB đầy chỗ | Bóng đá 20/20 · Tiếng Anh 16/16 · Mỹ thuật 12/12 · Tin học 12/12 |
| CLB thừa nhiều chỗ | Tình nguyện 5/12 · Khoa học 2/8 · Bóng rổ 13/18 |
| File xuất ra | 120 dòng trong file tổng, 11 file theo CLB |

Ba điều bảng trên cho thấy, và **học sinh tự viết phần nhận xét**:

- **41% số em được xếp KHÔNG vào nguyện vọng 1** — thuật toán thực sự phải đẩy
  người xuống nguyện vọng sau, không phải ai muốn gì được nấy.
- **10 em vào bằng suất dự trữ** — nếu bỏ cơ chế dự trữ thì 10 em này mất chỗ vào
  tay các em điểm cao hơn.
- **Có CLB thừa 7 chỗ trong khi 12 em không có CLB nào** — thuật toán không nhét
  học sinh vào CLB họ không chọn.

## Chạy thử bộ có lỗi

Nạp `TEST_01` trước, rồi nạp `TEST_04`. Phần mềm **phải** hiện đủ **6 cảnh báo**:

| # | Lỗi cài sẵn | Cảnh báo phải hiện |
|---|---|---|
| 1 | `HS202` xuất hiện hai dòng | mã xuất hiện 2 lần, chỉ giữ dòng cuối |
| 2 | `hs201` vs `HS201` | đang coi là hai học sinh khác nhau |
| 3 | nhóm dự trữ `chinh_sac` (thiếu chữ h) | không CLB nào nhận, gợi ý `chinh_sach` |
| 4 | nguyện vọng vào `clb_khong_co` | club không tồn tại, bỏ qua học sinh này |
| 5 | mã `12348` giữa các mã 7 chữ số | nghi Excel đã cắt mất số 0 đầu |
| 6 | cột `score_1` đặt trong file nguyện vọng | điểm ở đây KHÔNG được nạp |

**Thiếu bất kỳ cảnh báo nào là lỗi của phần mềm** — chụp màn hình và báo lại.

## Bộ demo — `app_DEMO_da_cham_diem.db`

Dựng sẵn tới ngay trước bước cuối: dữ liệu đã nạp, điểm đã có đủ, **0 cảnh báo**.

**Cách dùng, hôm demo:**

1. Đóng app
2. Đổi tên `app.db` đang có thành `app_cua_toi.db` *(đừng xoá — đó là dữ liệu của bạn)*
3. Chép `app_DEMO_da_cham_diem.db` vào cạnh `PhanBoCauLacBo.exe`, đổi tên thành `app.db`
4. Mở app → bấm **Chạy phân bổ** → **Xuất kết quả**

> Cố ý **chưa chạy phân bổ sẵn**. Phần đáng xem nhất là lúc thuật toán chạy và kết
> quả hiện ra — dựng sẵn cả phần đó thì không còn gì để cho xem.

## Sinh lại

```bash
./.venv/bin/python du_lieu_test/tao_du_lieu_test.py   # 4 tệp Excel
./.venv/bin/python du_lieu_test/tao_db_demo.py        # CSDL demo
./.venv/bin/python du_lieu_test/bo_sach/tao_bo_sach.py  # bộ sạch (seed 9090)
```

Seed cố định (`SEED = 2026`) nên chạy bao nhiêu lần cũng ra đúng bộ này.

*Phần nhận xét về kết quả chạy thử, học sinh tự viết.*
