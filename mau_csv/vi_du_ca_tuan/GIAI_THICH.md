# Bộ dữ liệu mẫu — một trường sinh hoạt **cả tuần**

Thư mục này là phiên bản "cả tuần" của `vi_du_day_du/`: cùng ba tệp, cùng
nguyên tắc, nhưng trải trên **sáu buổi từ thứ Hai đến thứ Bảy** thay vì ba
buổi. Dùng nó khi trường sinh hoạt câu lạc bộ nhiều ngày trong tuần và cần
thấy trước cột nào đẻ ra cột nào khi số buổi tăng lên.

Thả cả ba tệp vào phần mềm theo đúng thứ tự đánh số rồi bấm **Chạy phân bổ**.

| | |
|---|---|
| Trường | 6 buổi (`thu_2` → `thu_7`), 18 câu lạc bộ (3 buổi/ngày), 60 học sinh |
| Sức chứa | 48 chỗ mỗi buổi (15 hoặc 18 chỗ mỗi câu lạc bộ), 288 chỗ cả tuần |
| Nhập vào | **0 cảnh báo** ở cả ba tệp, **0 cảnh báo** ở bảng sức khoẻ dữ liệu |
| Chạy thử | 60/60 em có ít nhất một câu lạc bộ; 287 suất được xếp; không câu lạc bộ nào vượt chỉ tiêu |

> Mọi tên học sinh trong bộ này là **tên bịa**, ghép máy từ bảng họ/đệm/tên.
> Không có dữ liệu học sinh thật nào trong kho mã nguồn.

---

## Ba tệp, và cái gì đổi khi có nhiều buổi

| Tệp | Nhiều buổi làm đổi gì |
|---|---|
| `01_danh_sach_CLB.csv` | Thêm **cột `buoi`**, khai cho **mọi** câu lạc bộ |
| `02_chon_CLB_muon_thi.csv` | **Không đổi gì cả** — vẫn `test_club_N` / `score_N` |
| `03_xep_hang_nguyen_vong.csv` | Tên cột thành **`<buổi>_pref_<số>`**, đếm lại từ 1 ở mỗi buổi |

Đây là chỗ hay nhầm nhất: nhiều buổi **không** nhân đôi tệp dự thi. Một em thi
`clb_tinhoc` là thi một lần, dù `clb_tinhoc` sinh hoạt ngày nào.

---

## Tệp 1 · `01_danh_sach_CLB.csv` — nhập TRƯỚC hai tệp kia

```csv
club_id,name,capacity,reserve_capacity,reserve_group,buoi
clb_robotics,CLB Robotics,15,3,chinh_sach,thu_2
clb_covua,CLB Cờ vua,18,0,,thu_2
clb_bongro,CLB Bóng rổ,15,0,,thu_2
clb_bongda,CLB Bóng đá,15,0,,thu_3
...
clb_dangian,CLB Trò chơi dân gian,18,0,,thu_7
```

- **Một câu lạc bộ thuộc đúng một buổi.** Muốn Tin học sinh hoạt cả thứ Ba lẫn
  thứ Năm thì phải là **hai dòng, hai `club_id` khác nhau** (`clb_tinhoc_t3`,
  `clb_tinhoc_t5`) — mỗi dòng một chỉ tiêu riêng. Lặp lại cùng một `club_id` ở
  hai buổi là dữ liệu hỏng.
- **Cột `buoi` đã khai thì phải khai hết.** Bỏ trống một dòng là phần mềm không
  biết xếp câu lạc bộ đó vào ngày nào.
- **Giá trị buổi tự do**, miễn nhất quán giữa tệp 1 và tệp 3. Bộ này dùng
  `thu_2`…`thu_7`; `sang_2`, `chieu_5`, `t2_ca1` đều chấp nhận được.
- `reserve_capacity` > 0 thì **bắt buộc** có `reserve_group`. Bộ này có hai
  nhóm cùng tồn tại: `chinh_sach` (Robotics, Làm vườn) và `khoi_10` (Tin học,
  Khoa học, Nấu ăn, Nhiếp ảnh, Thư viện). Một em thuộc `khoi_10` **không** có
  quyền gì ở suất dự trữ của `chinh_sach`.

### Chia chỉ tiêu theo buổi, không theo tuần

Mỗi em nhận **tối đa một câu lạc bộ mỗi buổi**. Nên con số quyết định là **tổng
chỗ của riêng ngày đó**, không phải tổng cả tuần. Bộ này để 48 chỗ/buổi trong
khi mỗi buổi có 52–55 em đăng ký — chật vừa đủ để thấy thuật toán làm việc,
nhưng không đến mức ai cũng trượt.

---

## Tệp 2 · `02_chon_CLB_muon_thi.csv` — ai thi gì, điểm bao nhiêu

```csv
student_id,name,reserve_group,test_club_1,score_1,test_club_2,score_2,...
HS001,Trần Thanh Linh,khoi_10,clb_khieuvu,"9,8",clb_coking,"9,3",,,,,,
HS002,Trịnh Thanh Sương,,clb_khieuvu,"9,5",clb_coking,"6,5",clb_dangian,"4,1",,,,
```

- `score_N` ghép với `test_club_N` **theo con số trong tên cột**, không theo vị
  trí cột. Dời cột trong Excel không làm lệch điểm; sửa số trong tên cột thì có.
- **Số cặp cột = số câu lạc bộ nhiều nhất mà _một_ em dự thi**, không phải 5 ×
  số buổi. Bộ này 6 buổi nhưng chỉ cần 5 cặp.
- Dấu phẩy thập phân (`9,8`) và dấu chấm (`9.8`) đều đọc được. Ô có dấu phẩy
  phải nằm trong ngoặc kép — Excel tự làm việc này.
- **Câu lạc bộ không ai khai ở tệp này = câu lạc bộ không tổ chức thi.** Không
  có cột nào đánh dấu điều đó; phần mềm suy ra từ chính tệp này. Bộ này có 5
  trên 18 câu lạc bộ tổ chức thi, đúng như một trường thật: phần lớn câu lạc bộ
  nhận theo nguyện vọng, chỉ vài câu lạc bộ có vòng tuyển.
- Chỉ chấm điểm cho câu lạc bộ mà em đó **có khai nguyện vọng** ở tệp 3. Điểm
  cho câu lạc bộ em không xếp là điểm không dùng tới, và gần như luôn là gõ
  lệch cột.

---

## Tệp 3 · `03_xep_hang_nguyen_vong.csv` — muốn vào đâu, ngày nào

```csv
student_id,name,reserve_group,thu_2_pref_1,thu_2_pref_2,thu_2_pref_3,thu_3_pref_1,...,thu_7_pref_3
HS001,Trần Thanh Linh,khoi_10,clb_robotics,clb_bongro,,clb_tinhoc,...
HS004,Dương Thanh Phúc,,clb_covua,,,,,,,,,clb_nauan,,,clb_tranhbien,,,clb_thuvien,clb_dangian,clb_coking
```

- Tên cột là **`<buổi>_pref_<số>`**, thứ tự **đếm lại từ 1 ở mỗi buổi**. Không
  có `thu_3_pref_4` khi thứ Ba chỉ có 3 nguyện vọng.
- Chuỗi buổi trong tên cột phải **khớp từng ký tự** với cột `buoi` của tệp 1.
  `thu2_pref_1` (thiếu gạch dưới) là một buổi khác, và phần mềm sẽ báo.
- **Bỏ trống cả một buổi = em bận ngày đó.** Đó là dữ liệu hợp lệ, không phải
  thiếu sót. Xem `HS004`: chỉ khai thứ Hai, thứ Năm, thứ Sáu, thứ Bảy.
- Không nguyện vọng nào được trùng **trong cùng một buổi**. Trùng **giữa hai
  buổi khác nhau** cũng không được, vì mỗi câu lạc bộ chỉ thuộc một buổi.
- Trần cứng: **10 nguyện vọng mỗi buổi** — đúng giới hạn câu hỏi Ranking của
  Microsoft Forms. Bộ này dùng 3, quá đủ cho 3 câu lạc bộ mỗi ngày.

### Một dòng dài bao nhiêu

6 buổi × 3 nguyện vọng = 18 cột nguyện vọng, cộng 3 cột đầu là **21 cột**. Đây
là cái giá của tệp dạng rộng khi số buổi tăng. Nếu thấy khó nhìn trong Excel,
dùng **dạng dài** (mỗi lựa chọn một dòng) — xem `HUONG_DAN_CSV.md` mục 2; phần
mềm tự nhận dạng, kết quả giống hệt.

---

## Kết quả chạy thử (seed 42)

| Buổi | Số em khai | Chỗ | Số em có chỗ |
|---|---|---|---|
| `thu_2` | 52 | 48 | 48 |
| `thu_3` | 54 | 48 | 48 |
| `thu_4` | 52 | 48 | 48 |
| `thu_5` | 52 | 48 | 47 |
| `thu_6` | 55 | 48 | 48 |
| `thu_7` | 55 | 48 | 48 |

- **287 suất** được xếp trên 360 ô (60 em × 6 buổi). Phần còn lại là em bận
  ngày đó hoặc trượt cả ba nguyện vọng của ngày đó — cả hai đều là kết quả
  bình thường, không phải lỗi.
- **268 / 287 suất là nguyện vọng 1.** Chật ở mức này mà vẫn ra được con số đó
  là nhờ ba nguyện vọng mỗi buổi trải đều trên ba câu lạc bộ.
- `thu_5` có 47 chứ không 48: một chỗ trống ở câu lạc bộ mà những em còn lại
  của ngày đó không ai xếp. Thuật toán **không** nhét em vào câu lạc bộ em
  không đăng ký.
- Không em nào trắng tay cả tuần — 18 em đủ 6 buổi, 22 em được 5 buổi.

---

## Sinh lại bộ này, hoặc bộ cho trường mình

Ba tệp trên ra từ **một lệnh duy nhất**, nên chúng không thể lệch mã nhau:

```bash
python .claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py ngau \
    --ra mau_csv/vi_du_ca_tuan \
    --hoc-sinh 60 --buoi thu_2,thu_3,thu_4,thu_5,thu_6,thu_7 \
    --clb-moi-buoi 3 --seed 2026 --do-choi 4.8
```

**`--do-choi` tính theo cả bộ, không theo buổi.** Công cụ chia tổng chỗ đều cho
các buổi, nên trường nhiều buổi mà mỗi em sinh hoạt gần như ngày nào cũng có
thì phải nhân lên: muốn mỗi buổi dư 15% chỗ so với số em, đặt
`--do-choi ≈ 1.15 × số buổi`. Để nguyên `1.15` cho 6 buổi thì mỗi buổi chỉ có
1/6 số chỗ cần, và công cụ sẽ cảnh báo chọi hơn 4 lần.

Soát lại một bộ bất kỳ mà **không sửa gì**:

```bash
python .claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py soat mau_csv/vi_du_ca_tuan
```

Chỉ tiêu trong `01_danh_sach_CLB.csv` của bộ này được chỉnh tay cho lệch nhau
(15 và 18) sau khi sinh, để thấy các câu lạc bộ cùng buổi không bắt buộc bằng
chỉ tiêu. Sửa tay xong thì chạy lại lệnh `soat` ở trên — đó là lý do nó tồn tại.
