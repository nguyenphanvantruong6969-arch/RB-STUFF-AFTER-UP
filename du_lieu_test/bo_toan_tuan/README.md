# Bộ toàn tuần — cả 7 buổi, kín trần 10/5 ở MỌI buổi

> ### ⚠️ DỮ LIỆU MÔ PHỎNG — KHÔNG PHẢI HỌC SINH CÓ THẬT
>
> 200 cái tên do máy ghép từ bảng họ/đệm/tên (seed cố định `7070`). Bộ này
> được dựng cho **mọi em kín trần ở mọi buổi**, một điều không trường nào có
> thật. Trình bày các con số dưới đây như số liệu khảo sát là **bịa đặt dữ
> liệu**.

## Bộ này đo cái gì

Đúng một thứ: **trần tuyệt đối của phần mềm khi không chỗ nào dôi ra**.

Phần mềm nhận bảy nhãn buổi (`thu_2`…`thu_7`, `chu_nhat`), trần là trần **mỗi
buổi**, nên không cấu hình hợp lệ nào vượt được:

| | Mỗi buổi | × 7 buổi |
|---|---|---|
| Nguyện vọng xếp hạng | 10 | **70** |
| Câu lạc bộ dự thi (kèm điểm) | 5 | **35** |

Mọi em trong bộ này khai đúng cả 70 và 35 — **không một ca lệch nào**.

### Khác `bo_kich_tran` ở đâu

| | `bo_kich_tran` | `bo_toan_tuan` |
|---|---|---|
| Buổi | 3 | **7 — mọi buổi phần mềm nhận ra** |
| Kín trần | Đa số em | **Mọi em, mọi buổi** |
| Ca biên | Có (em bận, khai ngắn, không dự thi) | **Không một ca nào** |
| Dùng để | Xem phần mềm xử đúng các trường hợp lệch | Xem phần mềm chịu được mức trần tuyệt đối |

Hai bộ bổ nhau, không thay nhau. Bộ có ca biên mới bắt được lỗi xử lý lệch;
bộ kín trần mới bắt được lỗi ở mức tải và ở vùng đuôi danh sách.

## Ba tệp

| Tệp | Nội dung |
|---|---|
| `TOANTUAN_01_danh_sach_CLB.csv` | **84 CLB** · 7 buổi · 12 CLB mỗi buổi · **1 218 suất** · 14 CLB có suất dự trữ |
| `TOANTUAN_02_chon_CLB_muon_thi.csv` | 200 em · **35 lượt dự thi mỗi em** · **7 000 ô điểm** (70 cột `test_club_*`/`score_*`) |
| `TOANTUAN_03_xep_hang_nguyen_vong.csv` | Cùng 200 em · **70 nguyện vọng mỗi em** · **14 000** nguyện vọng (70 cột `<buổi>_pref_<số>`) |

Mỗi buổi phải có **trên 10** CLB, nếu không trần thật là số CLB của buổi chứ
không phải con số 10. Ở đây 12 CLB mỗi buổi — xếp 10 vẫn là lựa chọn thật, em
bỏ lại 2.

> **Nạp vào CSDL TRỐNG**, và phải xoá **cả câu lạc bộ** (bộ này có danh sách
> CLB riêng): tab **Quản lý** → **Vùng nguy hiểm** → *Xoá toàn bộ dữ liệu*.

### Sức chứa ngược với độ hút

Cả bảy buổi dùng chung một hồ sơ: CLB **hút nhất lại chật nhất**
(8 chỗ) và CLB ít ai chọn thì rộng nhất (22 chỗ). Trải đều thì ai cũng vừa ý
ngay vòng đầu và thuật toán không phải đẩy dây chuyền lần nào — bộ mẫu như vậy
không chứng minh được gì.

## Đã đo trên phần mềm thật (seed 42)

Nhập: **0 cảnh báo** · sức khoẻ dữ liệu: **0 cảnh báo** · chạy: **được**,
40 vòng.

| Chỉ số | Giá trị |
|---|---|
| Khớp | **200/200** em có ít nhất một CLB |
| Lấp chỗ | **174/174 mỗi buổi, cả bảy buổi — kín 100%** |
| Trượt | 26 em mỗi buổi |
| Tầng | 1 183 suất thường · 35 suất dự trữ |
| Thời gian | nhập ~0,1 giây · chạy ~0,1 giây |

**Số CLB mỗi em trong tuần** — 89 em kín cả bảy ngày:

| CLB/tuần | 7 | 6 | 5 | 4 | 3 | 2 | 0 |
|---|---|---|---|---|---|---|---|
| Số em | **89** | 72 | 20 | 8 | 9 | 2 | **0** |

**Nguyện vọng nhận được** — đuôi danh sách làm việc thật:

| NV thứ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Suất | 341 | 225 | 152 | 114 | 94 | 72 | 64 | 52 | 57 | **47** |

**292 suất** rơi vào nguyện vọng 7–10, trong đó **47 em** nhận đúng nguyện
vọng thứ 10.

## Thứ tự buổi trên màn hình Kết quả

Bảy nhãn đều nằm trong bảng `_SO_CUA_THU` của `rbda_priority_pipeline`, nên
phần mềm sắp chúng theo **thứ trong tuần**, không theo vần chữ cái —
`chu_nhat` mang số 8 nên đứng cuối, không nhảy lên đầu vì chữ "c".

## Dựng lại

```bash
python du_lieu_test/bo_toan_tuan/tao_bo_toan_tuan.py
```

Soát trước, ghi sau, dùng chín phép soát của `.claude/skills/sinh-du-lieu-clb`;
sai một điều là không tệp nào được ghi. Thêm một phép soát riêng: **mọi em,
mọi buổi phải đúng 10 và đúng 5** — chùng một ô là tệp sinh từ chối ghi, vì
chùng thì không cảnh báo nào của phần mềm kêu (nó chỉ hỏi "có quá không",
không hỏi "đã đủ chưa").

Hai con số lấy thẳng từ `TRAN_NGUYEN_VONG_MOI_BUOI` và `TRAN_CLB_THI_MOI_BUOI`,
không gõ lại.
