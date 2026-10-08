"""Sinh tệp biểu tượng cho ứng dụng từ hình vẽ gốc trong `logo.svg`.

    ./.venv/bin/python tao_logo.py

Vẽ lại đúng các hình trong `logo.svg` bằng Pillow ở độ phân giải gấp 8
lần rồi thu nhỏ — cách này cho đường cong mịn mà không cần thêm thư viện
đọc SVG nào vào bản đóng gói.

Sinh ra:
  logo.png  512x512, nền trong suốt ngoài hình tròn — dùng làm biểu
            tượng trên thanh tiêu đề và thanh tác vụ.
  logo.ico  gồm 6 cỡ (16 → 256) — PyInstaller gắn vào tệp .exe.
"""

from PIL import Image, ImageDraw

CAM = (204, 120, 92, 255)      # #CC785C
SANG = (244, 239, 232, 255)    # #F4EFE8
CO = 512
BIEN = 56                      # hình tròn 400 trong khung 512
PHONG = 8                      # vẽ to gấp 8 lần rồi thu nhỏ cho mịn

# (x, y, bán kính) của 10 đầu mút — toạ độ trong khung 400 của logo.svg
DAU_MUT = [
    (95, 120, 9), (20, 200, 12), (88, 270, 9), (115, 368, 12),
    (285, 368, 9), (312, 270, 12), (380, 200, 9), (305, 120, 12),
    (150, 30, 9), (245, 55, 12),
]
GACH_GIUA = [(182, 192, 218, 192), (182, 202, 218, 202), (182, 212, 204, 212)]


def ve():
    n = CO * PHONG
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def q(v):
        """Toạ độ trong khung 400 -> điểm ảnh trong ảnh đang vẽ."""
        return (BIEN + v) * PHONG

    def net(x1, y1, x2, y2, mau, day):
        r = day * PHONG / 2
        d.line([q(x1), q(y1), q(x2), q(y2)], fill=mau, width=int(day * PHONG))
        for x, y in ((x1, y1), (x2, y2)):     # đầu tròn
            d.ellipse([q(x) - r, q(y) - r, q(x) + r, q(y) + r], fill=mau)

    def cham(x, y, r, mau):
        d.ellipse([q(x - r), q(y - r), q(x + r), q(y + r)], fill=mau)

    cham(200, 200, 200, CAM)                                   # nền tròn
    for x, y, _ in DAU_MUT:
        net(200, 200, x, y, SANG, 6)                           # nan hoa
    for x, y, r in DAU_MUT:
        cham(x, y, r, SANG)                                    # đầu mút

    d.rounded_rectangle([q(158), q(158), q(242), q(242)],      # khối giữa
                        radius=8 * PHONG, fill=SANG)
    d.rounded_rectangle([q(167), q(167), q(233), q(233)],
                        radius=4 * PHONG, outline=CAM, width=3 * PHONG)
    for x in (167, 233):
        for y in (167, 233):
            cham(x, y, 3.5, CAM)
    for x1, y1, x2, y2 in GACH_GIUA:
        net(x1, y1, x2, y2, CAM, 3)

    return im.resize((CO, CO), Image.LANCZOS)


if __name__ == "__main__":
    anh = ve()
    anh.save("logo.png")
    anh.save("logo.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
    print("da tao logo.png (512x512) va logo.ico (7 co)")
