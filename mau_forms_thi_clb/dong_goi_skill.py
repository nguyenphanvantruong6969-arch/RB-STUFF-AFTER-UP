"""Đóng gói hai Claude skill thành tệp .zip tự chạy được, để tải lên nơi khác.

    python mau_forms_thi_clb/dong_goi_skill.py --ra ./skill_zip

Ghi ra:

    tao-google-form-clb.zip   Excel đề thi -> TAO_GOOGLE_FORM.gs + hướng dẫn
    xu-li-raw-forms.zip       RAW_PHIEU.xlsx -> Sổ nhập CLB (SO_NHAP_CLB.xlsx) + báo cáo

Trong kho mã, hai skill dùng chung vài tệp (khuôn mẫu .gs, bộ soát của
sinh-du-lieu-clb). Tải riêng một skill ra ngoài thì thiếu các tệp đó, nên mỗi
.zip mang theo bản sao của chúng ngay cạnh script. Script ưu tiên tệp nằm cạnh
nó, nên bản đóng gói chạy được ở bất kỳ thư mục nào.
"""

import argparse
import os
import sys
import zipfile

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(GOC, ".claude", "skills")
MFT = os.path.join(GOC, "mau_forms_thi_clb")
SDL = os.path.join(SKILLS, "sinh-du-lieu-clb", "scripts", "sinh_du_lieu.py")
# sinh_du_lieu.py ghi Sổ nhập CLB bằng so_nhap.py (gốc kho), so_nhap.py báo
# lỗi bằng i18n_errors.py — hai tệp này phải đi kèm mọi bản có sinh_du_lieu.
SO_NHAP = [(os.path.join(GOC, "so_nhap.py"), "scripts/so_nhap.py"),
           (os.path.join(GOC, "i18n_errors.py"), "scripts/i18n_errors.py")]

# skill -> [(đường dẫn nguồn, đường dẫn trong .zip)]
GOI = {
    "tao-google-form-clb": [
        (os.path.join(SKILLS, "tao-google-form-clb", "SKILL.md"), "SKILL.md"),
        (os.path.join(SKILLS, "tao-google-form-clb", "scripts", "tao_form.py"), "scripts/tao_form.py"),
        (os.path.join(MFT, "tao_google_forms.py"), "scripts/tao_google_forms.py"),
        (os.path.join(MFT, "THIET_KE_6_PHAN.html"), "scripts/THIET_KE_6_PHAN.html"),
        (SDL, "scripts/sinh_du_lieu.py"),
        *SO_NHAP,
        (os.path.join(MFT, "MAU_DE_THI.xlsx"), "assets/MAU_DE_THI.xlsx"),
        (os.path.join(MFT, "DINH_DANG_RAW.md"), "references/DINH_DANG_RAW.md"),
    ],
    "xu-li-raw-forms": [
        (os.path.join(SKILLS, "xu-li-raw-forms", "SKILL.md"), "SKILL.md"),
        (os.path.join(SKILLS, "xu-li-raw-forms", "scripts", "xu_li_raw.py"), "scripts/xu_li_raw.py"),
        (SDL, "scripts/sinh_du_lieu.py"),
        *SO_NHAP,
        (os.path.join(MFT, "DINH_DANG_RAW.md"), "references/DINH_DANG_RAW.md"),
    ],
}


def dong_goi(thu_muc_ra):
    os.makedirs(thu_muc_ra, exist_ok=True)
    ra = []
    for ten, tep in GOI.items():
        duong = os.path.join(thu_muc_ra, ten + ".zip")
        with zipfile.ZipFile(duong, "w", zipfile.ZIP_DEFLATED) as z:
            for nguon, dich in tep:
                # Thư mục gốc trong .zip là tên skill, đúng dạng claude.ai nhận.
                z.write(nguon, ten + "/" + dich)
        ra.append(duong)
    return ra


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--ra", required=True)
    a = p.parse_args(argv)
    for d in dong_goi(a.ra):
        print("Đã ghi %s" % d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
