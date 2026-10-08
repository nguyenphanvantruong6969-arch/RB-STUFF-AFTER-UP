# Bộ sạch — chạy thử không một cảnh báo

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
>
> 140 cái tên trong thư mục này do máy sinh ngẫu nhiên (seed cố định `9090`).
> Bộ này còn được **cố ý dựng** cho đủ chật để thuật toán phải làm việc — nó
> không mô phỏng một phân bố nguyện vọng tự nhiên. Trình bày các con số này
> như số liệu khảo sát thật là **bịa đặt dữ liệu**.

## Thư mục này khác gì thư mục cha

Thư mục cha (`du_lieu_test/`) có `TEST_04_CO_LOI_CO_Y.xlsx` — một file **cố ý
sai**, dựng riêng để xem phần mềm có kêu không. Thả cả bốn file cùng lúc thì
phần mềm kêu đúng như thiết kế, nhưng người chạy thử lại tưởng phần mềm hỏng.

**Thư mục này không chứa file lỗi nào.** Thả cả thư mục vào ô kéo-thả cũng
không sinh ra một cảnh báo nào. Đó là toàn bộ lý do nó tồn tại.

## Trước hết: phải nạp vào CSDL TRỐNG

**Nạp bộ này lên trên dữ liệu cũ thì vẫn còn cảnh báo** — và cảnh báo đó là của
dữ liệu cũ, không phải của bộ này. Phần mềm *cộng thêm* học sinh chứ không xoá
những em đã có; nạp `TEST_04` hôm trước thì `HS204` mang nhãn sai `chinh_sac`
vẫn nằm nguyên trong CSDL.

Đã đo: nạp cả bộ `TEST_01..04` rồi chồng bộ sạch lên → CSDL có **148** em,
còn **1 cảnh báo nghiêm trọng**, và chạy phân bổ ra **143/148** chứ không phải
140/140.

**Cách dọn — trong chính phần mềm:**

Tab **Quản lý** → cuối trang, khối **Vùng nguy hiểm** → bấm
**“Xoá toàn bộ học sinh (giữ CLB)”** → bấm lần nữa để xác nhận.

Phần mềm **tự sao lưu `app.db`** trước khi xoá và báo tên tệp sao lưu trong thông
báo, nên không mất gì. Nhật ký các lần chạy (`run_history`) cũng được giữ nguyên.

Muốn xoá cả danh sách CLB thì dùng nút thứ hai, **“Xoá toàn bộ dữ liệu”**.

*Phương án hai, nếu vì lý do gì đó không vào được phần mềm:* đóng app, đổi tên
`app.db` nằm cạnh `PhanBoCauLacBo.exe` thành `app_cu.db`, mở lại — app tự tạo
tệp mới, trống.

## Ba file — thả cả ba cùng lúc cũng được

| File | Nội dung |
|---|---|
| `SACH_01_danh_sach_CLB` | 12 CLB, tổng **150 suất** cho 140 em; 4 CLB có suất dự trữ |
| `SACH_02_chon_CLB_muon_thi` | 140 em, mỗi em thi **đúng 4 CLB**, kèm sẵn **560 ô điểm** |
| `SACH_03_xep_hang_nguyen_vong` | Cùng 140 em, mỗi em **6 nguyện vọng** |

Mỗi file có cả bản `.xlsx` lẫn `.csv` (utf-8-sig, Excel mở không vỡ dấu). Máy
nào thiếu thư viện đọc Excel thì dùng bản `.csv` — đã đối chiếu: **hai đường
vào cho ra kết quả xếp lớp giống hệt nhau**.

Phần mềm tự sắp thứ tự nạp, không cần kéo đúng thứ tự.

## Vì sao bộ này im lặng hoàn toàn

Phần *Cảnh báo dữ liệu* có 7 quy tắc rà soát. Bộ này được dựng để không vi
phạm quy tắc nào:

| Quy tắc rà soát | Bộ này tránh bằng cách |
|---|---|
| CLB có người thi mà chưa chấm điểm | mọi lượt thi đều có điểm sẵn trong `SACH_02` |
| Thi CLB mà không xếp nguyện vọng CLB đó | 4 CLB thi luôn là **4 nguyện vọng đầu** |
| Học sinh chưa xếp nguyện vọng nào | em nào cũng có đủ 6 |
| Nhãn dự trữ không CLB nào nhận | chỉ dùng `chinh_sach` và `khoi_10`, cả hai đều có CLB nhận |
| CLB có suất dự trữ mà quên đặt nhãn | 4 CLB có suất đều đã ghi nhãn |
| CLB dành suất cho nhãn chưa em nào mang | cả hai nhãn đều có học sinh mang |
| Tổng chỗ ít hơn số học sinh | 150 suất > 140 em |

## Kết quả đúng phải ra như sau

Đã đo với `seed = 42`. Ra khác bảng này nghĩa là có gì đó đã đổi.

| | |
|---|---|
| Cảnh báo lúc nạp | **0** — với điều kiện nạp vào CSDL trống |
| Cảnh báo dữ liệu | **0** |
| Được xếp | **140 / 140** — không em nào vào `_chua_duoc_xep.csv` |
| Số vòng chạy | 11 |
| Nguyện vọng 1 | 54 em · NV2: 46 · NV3: 21 · NV4: 11 · NV5: 7 · NV6: 1 |
| Vào bằng **suất dự trữ** | **16 em** (Tier `reserve`); 124 em Tier `general` |
| CLB đầy chỗ | 9 / 12 CLB |
| CLB còn chỗ | Khoa học 5/10 · Tình nguyện 7/10 · Robotics 8/10 |
| Cặp chặn (blocking pair) | **0** — kết quả ổn định |
| File xuất ra | 140 dòng ở file tổng, 12 file theo CLB |

## Vì sao xếp được 100% mà vẫn không tầm thường

Mỗi em xếp 6 nguyện vọng nhưng chỉ thi 4 CLB đầu. Hai nguyện vọng cuối rơi vào
nhóm CLB còn dư chỗ — đó là **đường lui**, và là lý do không em nào trắng tay.

Nhưng hai nguyện vọng cuối em **không thi**, nên không có điểm. Phần mềm vẫn xét,
chỉ là ở **Tier 2**: chọi nhau bằng số bốc thăm STB chứ không bằng điểm. Nhờ vậy
một bộ dữ liệu duy nhất cho thấy **cả hai tầng ưu tiên** cùng lúc, thay vì chỉ
tầng điểm.

## Sinh lại

```bash
./.venv/bin/python du_lieu_test/bo_sach/tao_bo_sach.py
```

Seed cố định nên chạy bao nhiêu lần cũng ra đúng bộ này.

`tests/test_bo_sach.py` (11 test) canh bộ này luôn sạch: nạp không cảnh báo,
xếp đủ 140 em, dùng cả hai tier, hai đường `.xlsx`/`.csv` khớp nhau, và thư mục
không được lẫn file lạ.

---

*Phần nhận xét, diễn giải và kết luận về kết quả chạy thử, học sinh tự viết.*
