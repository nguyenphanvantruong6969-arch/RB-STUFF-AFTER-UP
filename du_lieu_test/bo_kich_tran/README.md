# Bộ kịch trần — ba buổi, 10 nguyện vọng và 5 CLB dự thi MỖI BUỔI

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
>
> 150 cái tên trong thư mục này do máy ghép từ bảng họ/đệm/tên (seed cố định
> `1010`). Bộ này còn được **cố ý dựng cho chật kịch** và cho **mọi em khai
> kín trần**, nên nó không mô phỏng một phân bố nguyện vọng tự nhiên. Trình
> bày các con số dưới đây như số liệu khảo sát thật là **bịa đặt dữ liệu**.

## Vì sao có thư mục này

Không bộ mẫu nào trước đó đứng sát trần của phần mềm:

| Bộ | Nguyện vọng /buổi | Dự thi /buổi | Buổi |
|---|---|---|---|
| `vi_du_huong_dan` | 2 | 2 | 1 |
| `vi_du_day_du` | 2 | 1 | 3 |
| `bo_nhieu_buoi` | 3 | 3 | 5 |
| `bo_sach` | 6 | 4 | 1 |
| `TEST_01..04` | 5 | **5** | 1 |
| **`bo_kich_tran`** | **10** | **5** | **3** |

Trần **10 nguyện vọng mỗi buổi** vì thế chỉ được khoá bằng test đơn vị, chưa
bao giờ được thả vào phần mềm thật qua đường người dùng. Thư mục này lấp đúng
chỗ đó, và lấp cả hai phía của ranh giới:

- `./` — **đứng đúng trần**, nhập vào **không một cảnh báo nào**;
- `vuot_tran/` — **quá trần một đơn vị**, để xem phần mềm bỏ đúng phần nào.

## Điều kiện bắt buộc: buổi phải có TRÊN 10 câu lạc bộ

Muốn xếp 10 nguyện vọng trong một buổi thì buổi đó phải có hơn 10 câu lạc bộ,
nếu không trần thật là **số câu lạc bộ của buổi**, không phải con số 10. Ở
`vi_du_day_du` mỗi buổi chỉ có 3 câu lạc bộ, nên 10 nguyện vọng là bất khả
thi về mặt vật lý — không liên quan gì tới trần.

Ở đây: **12 câu lạc bộ mỗi buổi**, nên xếp 10 vẫn là một lựa chọn thật — em
bỏ lại 2.

## Bộ chính — thả cả ba tệp cùng lúc

| Tệp | Nội dung |
|---|---|
| `KICHTRAN_01_danh_sach_CLB.csv` | 36 CLB · 3 buổi (`thu_2`, `thu_4`, `thu_6`) · 12 CLB mỗi buổi · 388 suất, 6 CLB có suất dự trữ |
| `KICHTRAN_02_chon_CLB_muon_thi.csv` | 150 em · **5 CLB dự thi mỗi buổi** · **2 189 ô điểm** điền sẵn |
| `KICHTRAN_03_xep_hang_nguyen_vong.csv` | Cùng 150 em · **10 nguyện vọng mỗi buổi** (30 cột `<buổi>_pref_<số>`) |

Nạp danh sách CLB trước — phần mềm tự sắp thứ tự nếu thả cả ba cùng lượt.

> **Nạp vào CSDL TRỐNG.** Nạp chồng lên dữ liệu cũ thì cảnh báo còn lại là của
> dữ liệu cũ, không phải của bộ này. Dọn ở tab **Quản lý** → **Vùng nguy hiểm**
> → *Xoá toàn bộ học sinh (giữ CLB)*.

### Sáu ca biên, cố định theo mã học sinh

| Mã | Ca |
|---|---|
| `HS141`–`HS146` | Bỏ trống **hẳn một buổi** — "ngày đó em bận". Dữ liệu **hợp lệ** |
| `HS147`–`HS150` | Khai **ngắn** ở một buổi (1, 3, 5, 6 nguyện vọng) — trần là trần **trên**, không phải chỉ tiêu |
| `HS131`–`HS135` | Khai đủ 10 nhưng **không dự thi CLB nào** ở một buổi — cả 10 nguyện vọng buổi đó chỉ được xét ở **Tier 2** |

`HS131` là ca đáng xem nhất: nó cho thấy khai đủ nguyện vọng mà không dự thi
thì vẫn có thể trắng tay buổi đó.

### Đã đo trên phần mềm thật (seed 42)

Nhập: **0 cảnh báo** · sức khoẻ dữ liệu: **0 cảnh báo** · chạy: **được**.

| Chỉ số | Giá trị |
|---|---|
| Khớp | **150/150** em có ít nhất một CLB trong tuần |
| Lấp chỗ | `thu_2` 128/128 · `thu_4` 130/130 · `thu_6` 130/130 — **kín 100%** |
| Trượt theo buổi | 20 / 18 / 18 em |
| Số CLB mỗi em trong tuần | 3 CLB: 94 em · 2 CLB: 50 em · 1 CLB: 6 em · 0 CLB: 0 em |
| Tầng | 372 suất thường · 16 suất dự trữ |

**Phân bố nguyện vọng nhận được** — đây là lý do bộ kịch trần đáng có:

| NV thứ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Số suất | 130 | 80 | 41 | 38 | 21 | 14 | 21 | 13 | 11 | **19** |

**64 suất rơi vào nguyện vọng 7–10**, trong đó 19 em nhận đúng nguyện vọng thứ
**10**. Không bộ mẫu nào khác chạm tới vùng đuôi này, nên phần đuôi của danh
sách xếp hạng chưa từng được chạy thật qua giao diện.

## Bộ `vuot_tran/` — CỐ Ý SAI

⚠️ **Đừng thả chung với bộ chính** rồi kết luận bộ chính bẩn. Cảnh báo sinh ra
là của bộ này.

6 học sinh, cùng 36 CLB. Đã đo — phần mềm phản ứng đúng như sau:

| Mã | Khai | Phần mềm làm gì |
|---|---|---|
| `HS001` | 11 NV ở `thu_2` | Bỏ **riêng nguyện vọng buổi `thu_2`**; `thu_4`, `thu_6` vào đủ; **5 CLB dự thi `thu_2` vẫn vào** (tệp dự thi không vi phạm) |
| `HS002` | 6 dự thi ở `thu_4` | Bỏ **dự thi `thu_4` kèm cả 5 ô điểm của buổi đó**; nguyện vọng cả ba buổi vào đủ |
| `HS003` | 12 NV **và** 7 dự thi ở `thu_6` | Bỏ **cả hai** ở `thu_6`; `thu_2`, `thu_4` nguyên vẹn |
| `HS004` | 11 NV ở **cả ba** buổi | Mất **toàn bộ** nguyện vọng — em này chắc chắn trắng tay |
| `HS005` | Đúng 10 / đúng 5 | **Vào trọn vẹn, không một cảnh báo** — đây là phép đối chứng |
| `HS006` | Khai vừa phải | Vào trọn vẹn |

Nguyên tắc đọc kết quả: phần mềm bỏ **đúng buổi sai của đúng em sai**, không
bỏ cả em, không bỏ cả tệp, và **không tự cắt** danh sách còn 10 — cắt bớt là
âm thầm đổi nguyện vọng của học sinh.

Mã cảnh báo tương ứng: `csv_pref_bo_buoi_qua_tran`, `csv_thi_bo_buoi_qua_tran`.

## Dựng lại

```bash
python du_lieu_test/bo_kich_tran/tao_bo_kich_tran.py    # bộ chính
python du_lieu_test/bo_kich_tran/tao_bo_vuot_tran.py    # bộ cố ý sai
```

Cả hai tệp sinh đều **soát trước, ghi sau**, dùng chung chín phép soát của
`.claude/skills/sinh-du-lieu-clb`. Sai một điều là không tệp nào được ghi.

Riêng bộ chính còn một phép soát nữa: nó phải **chạm đúng** trần 10/5, không
chỉ "không vượt trần". Tụt xuống 9 là bộ này mất lý do tồn tại, nên tệp sinh
từ chối ghi. Bộ `vuot_tran/` chạy **phép soát ngược**: nó phải sai, và sai
đúng những chỗ đã thiết kế.

Hai con số 10 và 5 lấy thẳng từ `rbda_priority_pipeline.TRAN_NGUYEN_VONG_MOI_BUOI`
và `TRAN_CLB_THI_MOI_BUOI`, không gõ lại — đổi trần trong phần mềm mà quên
dựng lại bộ này thì tệp sinh báo lỗi ngay.
