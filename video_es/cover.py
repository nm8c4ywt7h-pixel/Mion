"""TikTok cover image (1080x1920)."""
from PIL import ImageDraw, ImageFont
from scenes import bg, W
from sprites import dog, fork, qmark, FONT, INK

im = bg("burst", ((250, 150, 60, 255), (255, 175, 90, 255))).copy()
d = dog("head", "beg", "tongue", 0, False, 2.3)
im.alpha_composite(fork(1.1).rotate(20, expand=True), (110, 1050))
im.alpha_composite(d, ((W - d.width) // 2, 1880 - d.height))
q = qmark(1.1)
im.alpha_composite(q, (840, 1000))
dr = ImageDraw.Draw(im)
for y, txt, size, col in ((330, "¿TU PERRO", 150, (255, 255, 255, 255)), (500, "TE SUPLICA", 150, (255, 222, 40, 255)),
                          (670, "EN LA MESA?", 150, (255, 255, 255, 255)), (860, "No es hambre…", 90, (255, 255, 255, 255))):
    f = ImageFont.truetype(FONT, size)
    dr.text((W // 2, y), txt, font=f, fill=col, anchor="mm", stroke_width=16 if size > 100 else 10, stroke_fill=INK)
im.convert("RGB").save("portada_tiktok.jpg", quality=92)
