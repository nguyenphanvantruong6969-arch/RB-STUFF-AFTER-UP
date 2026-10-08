# -*- coding: utf-8 -*-
"""Canh `TAI_LIEU_DU_LIEU.md` — tài liệu tổng hợp về dữ liệu đầu vào.

Tài liệu ấy dán nguyên văn header CSV, số liệu từng bộ và toàn văn
`SKILL.md`. Một tài liệu chép lại như thế mục rất nhanh: đổi một cột trong
tệp mẫu, thêm một mục vào `SKILL.md`, hay đổi trần trong pipeline là tài
liệu lệch mà không ai thấy — và lệch theo kiểu đọc lên vẫn rất thuyết phục.

Bốn test dưới đây khoá đúng những chỗ chép lại đó.

KHÔNG kiểm số dòng mã (`api.py:1196`): số dòng đổi theo mọi lần sửa mã, khoá
lại thì thành test giòn kêu oan. Tài liệu vì thế ghi tên hàm là chính, số
dòng chỉ là chỉ dẫn.
"""

import io
import os
import re

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAI_LIEU = os.path.join(GOC, "TAI_LIEU_DU_LIEU.md")
SKILL_MD = os.path.join(GOC, ".claude", "skills", "sinh-du-lieu-clb", "SKILL.md")

# Những đường dẫn tài liệu nhắc tới ĐỂ NÓI LÀ KHÔNG CÓ. Chúng phải vắng mặt,
# và `test_nhung_tep_tai_lieu_noi_khong_co_thi_van_khong_co` canh điều đó.
VANG_MAT_CO_Y = {".claude/settings.json"}


@pytest.fixture(scope="module")
def van_ban():
    with io.open(TAI_LIEU, encoding="utf-8") as f:
        return f.read()


def test_tai_lieu_ton_tai():
    assert os.path.exists(TAI_LIEU), (
        "Thiếu TAI_LIEU_DU_LIEU.md — Phần 11 của chính nó hứa tệp này tồn tại"
    )


def test_moi_duong_dan_trong_tai_lieu_deu_ton_tai(van_ban):
    """Mọi đường dẫn trong kho mà tài liệu nhắc tới đều phải có thật.

    Tài liệu trỏ người đọc tới hàng chục tệp. Một đường dẫn chết là người
    đọc đi vào ngõ cụt, và không có cách nào biết tệp bị xoá hay tài liệu gõ
    sai tên.
    """
    # Chỉ xét đường dẫn nằm trong `backtick` và bắt đầu bằng một thư mục
    # thật của kho — để không bắt oan tên tệp giả trong ví dụ (truong.json,
    # ./bo_moi, app.db…).
    mau = re.compile(
        r"`((?:mau_csv|du_lieu_test|tests|\.claude|\.github)/[^`\s]+)`"
    )
    thieu = []
    for duong_dan in sorted(set(mau.findall(van_ban))):
        # Bỏ những mục có ký tự đại diện hoặc dấu ba chấm — đó là mô tả
        # chung, không phải một tệp cụ thể.
        if any(k in duong_dan for k in ("*", "…", "<", ">")):
            continue
        # Tài liệu trích chỗ mã nguồn theo kiểu `tệp:dòng`. Bỏ phần số dòng.
        duong_dan = re.sub(r":\d+$", "", duong_dan)
        if duong_dan in VANG_MAT_CO_Y:
            continue
        if not os.path.exists(os.path.join(GOC, duong_dan)):
            thieu.append(duong_dan)
    assert not thieu, "Tài liệu trỏ tới đường dẫn không tồn tại: %s" % thieu


def test_nhung_tep_tai_lieu_noi_khong_co_thi_van_khong_co():
    """Mặt gương của test trên.

    Tài liệu khẳng định kho KHÔNG có `.claude/settings.json`, không hook và
    không kỹ năng nào khác. Ngày nào ai thêm tệp đó vào thì câu ấy thành sai
    — và sai theo kiểu không ai nghĩ tới việc kiểm lại. Test này bắt đúng
    lúc đó.
    """
    co_ma_khong_nen = [d for d in VANG_MAT_CO_Y
                       if os.path.exists(os.path.join(GOC, d))]
    assert not co_ma_khong_nen, (
        "Tài liệu nói những tệp này không tồn tại, nhưng giờ chúng có thật — "
        "sửa lại mục 4 của TAI_LIEU_DU_LIEU.md: %s" % co_ma_khong_nen
    )


def test_header_trich_trong_tai_lieu_khop_tep_that(van_ban):
    """Header CSV dán trong tài liệu phải khớp từng ký tự với tệp thật.

    Đây là chỗ dễ lệch nhất: thêm một cột vào tệp mẫu thì tài liệu vẫn in
    bản cũ, và người dùng dựng tệp theo tài liệu sẽ thiếu cột.
    """
    # Các tệp mà tài liệu dán ĐỦ header (không rút gọn bằng `…`).
    day_du = [
        "mau_csv/02_chon_club_thi_dang_dai.csv",
        "mau_csv/03_nguyen_vong_dang_rong.csv",
        "mau_csv/04_nguyen_vong_dang_dai.csv",
        "mau_csv/05_danh_sach_club.csv",
        "mau_csv/06_danh_sach_club_nhieu_buoi.csv",
        "mau_csv/07_chon_club_thi_nhieu_buoi.csv",
        "mau_csv/08_nguyen_vong_nhieu_buoi.csv",
        "mau_csv/vi_du_day_du/01_danh_sach_CLB.csv",
        "mau_csv/vi_du_day_du/02_chon_CLB_muon_thi.csv",
        "mau_csv/vi_du_day_du/03_xep_hang_nguyen_vong.csv",
        "du_lieu_test/bo_sach/SACH_01_danh_sach_CLB.csv",
        "du_lieu_test/bo_sach/SACH_03_xep_hang_nguyen_vong.csv",
        "du_lieu_test/vi_du_huong_dan/VIDU_01_danh_sach_CLB.csv",
        "du_lieu_test/vi_du_huong_dan/VIDU_02_chon_CLB_muon_thi.csv",
        "du_lieu_test/vi_du_huong_dan/VIDU_03_xep_hang_nguyen_vong.csv",
        "du_lieu_test/thu_tai/ket_qua_thu_tai.csv",
    ]
    lech = []
    for duong_dan in day_du:
        p = os.path.join(GOC, duong_dan)
        with io.open(p, encoding="utf-8-sig") as f:
            header = f.readline().strip()
        if header not in van_ban:
            lech.append((duong_dan, header))
    assert not lech, (
        "Header trong tài liệu không còn khớp tệp thật:\n"
        + "\n".join("  %s\n    tệp thật: %s" % (d, h) for d, h in lech)
    )


def test_hai_tran_trong_tai_lieu_khop_phan_mem(van_ban):
    """Hai trần trong tài liệu phải là hai trần phần mềm đang áp.

    Cùng khuôn với `test_tran_trong_skill_khop_voi_tran_cua_phan_mem` ở
    tests/test_skill_sinh_du_lieu.py: tài liệu nào nói về trần thì phải nói
    đúng con số phần mềm dùng, nếu không nó dạy người ta dựng tệp bị từ chối.
    """
    from rbda_priority_pipeline import (
        TRAN_CLB_THI_MOI_BUOI,
        TRAN_NGUYEN_VONG_MOI_BUOI,
    )

    assert "TRAN_NGUYEN_VONG_MOI_BUOI" in van_ban
    assert "TRAN_CLB_THI_MOI_BUOI" in van_ban
    assert "**%d**" % TRAN_NGUYEN_VONG_MOI_BUOI in van_ban, (
        "Tài liệu không nêu trần nguyện vọng %d" % TRAN_NGUYEN_VONG_MOI_BUOI
    )
    assert "**%d**" % TRAN_CLB_THI_MOI_BUOI in van_ban, (
        "Tài liệu không nêu trần câu lạc bộ dự thi %d" % TRAN_CLB_THI_MOI_BUOI
    )


def test_toan_van_skill_md_con_dung(van_ban):
    """Mục 4.1 dán nguyên văn SKILL.md — bản dán phải còn khớp bản chính.

    Kiểm theo tiêu đề: thêm, xoá hay đổi tên một mục trong SKILL.md mà quên
    cập nhật tài liệu là test kêu ngay.
    """
    with io.open(SKILL_MD, encoding="utf-8") as f:
        skill = f.read()

    tieu_de = [d for d in skill.splitlines() if d.startswith("## ")]
    assert tieu_de, "SKILL.md không còn tiêu đề `## ` nào — đọc sai tệp?"

    thieu = [d for d in tieu_de if d not in van_ban]
    assert not thieu, (
        "Tài liệu thiếu các mục của SKILL.md: %s" % thieu
    )

    # Ba nguyên tắc bất di bất dịch là phần quan trọng nhất của SKILL.md —
    # khoá riêng, vì mất chúng thì bản dán còn tiêu đề mà rỗng ruột.
    for cau in ("Sổ phải đi ra từ MỘT nguồn",
                "Sai thì không ghi tệp nào",
                "Không bịa dữ liệu học sinh thật"):
        assert cau in van_ban, "Tài liệu thiếu nguyên tắc: %s" % cau
