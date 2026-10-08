# Thử tải — đo phần mềm ở quy mô lớn

> ### ⚠️ DỮ LIỆU MÔ PHỎNG
> Toàn bộ dữ liệu ở đây do máy sinh theo tham số, **không phải học sinh có thật**.
> Dùng để đo giới hạn của phần mềm, không phải kết quả khảo sát.

## Bốn tệp chạy được

```bash
./.venv/bin/python du_lieu_test/thu_tai/doi_chung.py       # (1) kiểm bộ đo trước
./.venv/bin/python du_lieu_test/thu_tai/chay_thu_tai.py    # (2) lưới quét, ~15 phút
./.venv/bin/python du_lieu_test/thu_tai/do_csdl.py         # (3) tầng CSDL
xvfb-run -a ./.venv/bin/python du_lieu_test/thu_tai/do_giao_dien.py   # (4) tầng giao diện
./.venv/bin/python du_lieu_test/thu_tai/kiem_on_dinh.py    # (5) kết quả có còn ĐÚNG không
```

**Chạy `doi_chung.py` trước mọi thứ khác.** Nó bắt bộ đo đo lại bộ 120 học sinh
thật — thứ đã biết kết quả (108/120, 7 vòng). Lệch nghĩa là bộ đo hỏng, và mọi
con số quy mô lớn sau đó đều vô nghĩa dù nhìn rất thuyết phục.

## Thử sức tệp Excel kết quả

```bash
./.venv/bin/python du_lieu_test/thu_tai/stress_xuat_excel.py           # ~8 phút
./.venv/bin/python du_lieu_test/thu_tai/stress_xuat_excel.py --nhanh   # ~1 phút
```

173 kịch bản trong sáu nhóm: quy mô (tới 5.000 em × 5 buổi), giới hạn cứng của
Excel, dữ liệu lạ và độc, trạng thái lạ, hệ thống tệp, và 90 bộ dữ liệu ngẫu
nhiên đối chiếu từng trang với CSDL. Tệp đáng ngờ được mở lại bằng LibreOffice.
Kết quả ghi vào `ket_qua_stress_xuat.csv`.

Lần chạy 03/10/2026 bắt được ba lỗi (đã sửa, có test trong
`tests/test_so_excel_de_dung.py`): ký tự điều khiển trong tên làm hỏng cả lần
xuất; quá 1.026 CLB vượt giới hạn ngắt trang của Excel; tên CLB quá dài đẩy
"Mã CLB" ra khỏi dòng đầu khối. Sau khi sửa: 173/173 đạt; 5.000 em × 5 buổi
xuất trong ~5 giây, đỉnh bộ nhớ ~87 MB, tệp ~1,1 MB.

## Lưới quét

| Chiều | Các mức |
|---|---|
| Học sinh | 200 · 500 · 1 000 · 2 000 · 5 000 |
| Câu lạc bộ | 10 · 25 · 50 · 100 |
| Nguyện vọng mỗi em | 3 · 5 · 10 *(10 là trần cứng của phần mềm)* |
| Tổng chỉ tiêu | 100% và 108% số học sinh |
| **Cách chia chỉ tiêu** | `chia_deu` · `theo_nhu_cau` |
| CLB mỗi em **dự thi** | **4, cố định** |

Bỏ các ô mà mỗi CLB chưa nổi 8 chỗ. Kết quả ra `ket_qua_thu_tai.csv`.

### Hai điều cố ý trong thiết kế

**Số CLB dự thi giữ cố định ở 4.** Bắt một em dự 50 kỳ thi là vô nghĩa, nên khi số
CLB tăng thì số kỳ thi **không** tăng theo. Hệ quả: em xếp 10 nguyện vọng mà chỉ
thi 4 CLB thì 6 nguyện vọng còn lại **rơi xuống Tầng 2**, chỉ xét bằng số bốc
thăm. Cột `xep_chi_nho_boc_tham` đếm đúng số em rơi vào tình huống đó.

**Cách chia chỉ tiêu là một biến, không phải hằng số.** Đây là chỗ tôi làm sai ở
lần chạy đầu: ban đầu tôi chia chỉ tiêu **theo đúng độ hút** của mỗi CLB, tức là
cung khớp cầu sẵn — và tất nhiên gần như em nào cũng có chỗ, ở mọi quy mô. Con số
đẹp nhưng vô nghĩa.

Trường thật không mở CLB to gấp mười lần chỉ vì nhiều em thích nó. Nên lưới quét
chạy **cả hai**:

| Cách chia | Nghĩa là gì |
|---|---|
| `chia_deu` | Mọi CLB chỉ tiêu bằng nhau, nhu cầu vẫn rất lệch. **Giống trường thật.** |
| `theo_nhu_cau` | CLB càng đông người thích càng nhiều chỗ. Trường hợp dễ nhất. |

Chênh lệch giữa hai cột đó chính là **cái giá của việc chia chỉ tiêu không theo
nhu cầu** — và đó là con số nhà trường dùng được.

## Các cột trong `ket_qua_thu_tai.csv`

| Cột | Ý nghĩa |
|---|---|
| `t_nap_giay` / `t_phan_bo_giay` / `t_xuat_giay` | Thời gian ba bước |
| `so_vong` | Số vòng lặp thuật toán chạy |
| `ty_le_xep` | % học sinh được xếp vào một CLB |
| `xep_nho_co_diem` | Được xếp vào CLB mình **có dự thi** (Tầng 1) |
| `xep_chi_nho_boc_tham` | Được xếp vào CLB mình **không dự thi** — chỉ nhờ bốc thăm |
| `dinh_bo_nho_MB` | Đỉnh bộ nhớ Python trong cả lần chạy |

## Nhu cầu sinh ra thế nào

Trọng số Zipf: CLB thứ *i* hút khoảng `1/i`. CLB đầu bảng đông gấp nhiều lần chỉ
tiêu, CLB cuối bảng gần như không ai chọn — đúng hình dạng của bộ dữ liệu 120 em
đã đo được. Seed cố định nên chạy lại luôn ra đúng bộ đó.

*Phần diễn giải và đánh giá ý nghĩa các con số, học sinh tự viết.*
