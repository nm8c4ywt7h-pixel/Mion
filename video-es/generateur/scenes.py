"""Les 29 plans du guion (voir ../GUION.md). Chaque plan : fond, dessin, voix off, mot à l'écran, son."""
from dessin import *


def s01(c):
    room(c, SAUGE, (190, 150, 110), 1350)
    c.rect(180, 1050, 900, 1250, (250, 250, 245), r=30)
    c.rect(150, 1230, 930, 1400, (150, 100, 70), r=20)
    c.rect(150, 900, 230, 1400, (150, 100, 70), r=20)
    dog(c, 560, 900, 1.1, face=1)
    for i in range(3):
        c.line([(200, 760 + i * 70), (290 - i * 20, 760 + i * 70)], (255, 255, 255), 10)


def s02(c):
    rays(c, MOUTARDE, (245, 205, 100))
    dog(c, 540, 1000, 1.0)
    big_x(c, 540, 860, 330)


def s03(c):
    c.img.paste((30, 34, 58), (0, 0, *c.img.size))
    halo(c, 540, 860, 470, (60, 66, 104))
    dog_face(c, 540, 860, 260, eyes="wide")
    waves(c, 260, 560, 160); waves(c, 830, 560, 160)


def living(c):
    room(c, (240, 200, 180), (200, 160, 120), 1350)
    window_day(c, 110, 300, 300, 380)
    c.rect(700, 330, 920, 520, (255, 245, 230), r=6)
    dog_face(c, 810, 425, 60)
    plant(c, 960, 1350)


def s04(c):
    living(c)
    person(c, "hugo", 280, 1450, 600)
    person(c, "sofia", 560, 1450, 680, arms="wave")
    dog(c, 820, 1420, 0.55)


def s05(c):
    living(c)
    person(c, "sofia", 340, 1450, 680, arms="point")
    c.ell(760, 1420, 170, 55, (200, 70, 70))
    c.ell(760, 1400, 140, 35, (240, 150, 140), outline=None)
    dog(c, 760, 1300, 0.45, face=-1)
    c.ell(540, 520, 200, 140, (255, 255, 255))
    c.poly([(470, 640), (430, 740), (530, 655)], (255, 255, 255), outline=None)
    heart(c, 540, 515, 70)


def s06(c):
    c.img.paste((120, 95, 80), (0, 0, *c.img.size))
    bed_top(c, dog_pos="bottom")


def s07(c):
    room(c, (210, 220, 200), (180, 140, 100), 1350)
    c.rect(80, 450, 330, 1350, CREME, r=0)
    dog(c, 220, 1290, 0.4)
    person(c, "hugo", 600, 1450, 700, arms="point")
    c.ell(880, 1380, 45, 45, (210, 230, 70))
    c.arc(880, 1380, 45, 45, 300, 60, (255, 255, 255), 6)


def s08(c):
    room(c, (210, 220, 200), (180, 140, 100), 1350)
    c.ell(300, 1380, 45, 45, (210, 230, 70))
    dog(c, 700, 1250, 0.8, face=1)
    for i in range(3):
        c.line([(330, 1150 + i * 60), (420, 1150 + i * 60)], (255, 255, 255), 10)


def s09(c):
    room(c, NUIT, (90, 80, 110), 1300)
    window_night(c, 120, 260, 340, 420)
    clock(c, 820, 420, 130, hour=3)
    person(c, "sofia", 540, 1400, 620, arms="down", eyes="open", mouth="sad")
    c.rect(220, 1180, 860, 1240, (150, 100, 70), r=10)
    c.rect(360, 1060, 720, 1180, (220, 225, 235), r=12)
    c.rect(385, 1080, 695, 1160, (130, 170, 230), r=6, w=4)


def s10(c):
    c.img.paste((30, 34, 58), (0, 0, *c.img.size))
    halo(c, 540, 880, 470, (60, 66, 104))
    p = PERSOS["sofia"]
    head(c, 540, 880, 300, p["skin"], p["hair"], "bob", True, "open", tears=True, mouth="sad")


def s11(c):
    c.img.paste((30, 34, 58), (0, 0, *c.img.size))
    halo(c, 540, 880, 470, (60, 66, 104))
    c.rect(150, 820, 930, 1200, (255, 255, 255), r=80)
    p = PERSOS["pablo"]
    head(c, 540, 880, 230, p["skin"], p["hair"], "short", False, "closed", mouth="snore")
    zzz(c, 760, 600, 110)


def s12(c):
    rays(c, (230, 120, 90), (245, 150, 110))
    dog_face(c, 540, 900, 280, eyes="wide")
    bolt(c, 190, 520, 140); bolt(c, 890, 520, 140)


def s13(c):
    room(c, (230, 190, 170), (180, 140, 100), 1350)
    window_night(c, 620, 260, 320, 380)
    c.rect(120, 1000, 960, 1300, (120, 170, 140), r=60)
    c.rect(120, 900, 960, 1080, (110, 160, 130), r=60)
    person(c, "sofia", 400, 1260, 600, eyes="open", tears=True, mouth="sad")
    dog(c, 720, 1050, 0.65, face=-1, eyes="closed")
    heart(c, 640, 760, 60)


def lab(c):
    room(c, (235, 240, 245), (200, 205, 215), 1350)
    for i in range(6):
        for j in range(10):
            c.rect(i * 190 - 10, j * 130, i * 190 + 180, j * 130 + 120, None, outline=(215, 222, 232), w=3)


def s14(c):
    lab(c)
    c.rect(640, 330, 940, 530, (255, 255, 255), r=6)
    c.ell(790, 430, 55, 55, (220, 40, 50), outline=None)
    person(c, "sabia", 420, 1450, 720, arms="point")


def s15(c):
    c.img.paste((235, 228, 215), (0, 0, *c.img.size))
    cols = [DOG, (230, 200, 150), (120, 100, 90), (200, 200, 200), (60, 55, 60)]
    for i in range(4):
        for j in range(6):
            dog_face(c, 160 + i * 253, 220 + j * 270, 85, eyes="closed" if (i + j) % 3 == 0 else "open",
                     tears=(i + j) % 2 == 0, color=cols[(i * 6 + j) % 5])


def s16(c):
    room(c, (250, 225, 190), (210, 170, 120), 1350)
    person(c, "pablo", 330, 1450, 680, arms="up")
    dog(c, 720, 1300, 0.7, face=-1, tears=True)
    heart(c, 520, 600, 60); heart(c, 760, 760, 45); heart(c, 290, 480, 40)


def s17(c):
    c.img.paste(NUIT, (0, 0, *c.img.size))
    c.rect(60, 560, 500, 1200, (210, 225, 210), r=30)
    c.rect(580, 560, 1020, 1200, (210, 225, 210), r=30)
    p = PERSOS["sofia"]
    head(c, 280, 880, 150, p["skin"], p["hair"], "bob", True, "open", tears=True)
    dog_face(c, 800, 880, 150, tears=True)
    c.text(540, 880, "=", 160, fill=MOUTARDE)
    heart(c, 420, 620, 45); heart(c, 940, 620, 45)


def s18(c):
    c.img.paste((214, 120, 90), (0, 0, *c.img.size))
    c.ell(540, 1050, 640, 560, DOG)
    c.ell(540, 820, 330, 230, (60, 45, 45))
    c.ell(420, 860, 70, 95, (25, 20, 25), outline=None)
    c.ell(660, 860, 70, 95, (25, 20, 25), outline=None)
    waves(c, 420, 480, 150, (255, 255, 255)); waves(c, 660, 480, 150, (255, 255, 255))


def s19(c):
    lab(c)
    for x in (300, 780):
        c.rect(x - 15, 400, x + 15, 1350, (240, 200, 60), r=6)
    c.rect(270, 400, 810, 440, (240, 200, 60), r=6)
    person(c, "sabio", 380, 1450, 660, arms="point")
    person(c, "sabia", 720, 1450, 640)
    check(c, 540, 260, 140)


def s20(c):
    c.img.paste((225, 235, 240), (0, 0, *c.img.size))
    cols = [MOUTARDE, (90, 170, 120), (235, 100, 100), (90, 120, 190), (180, 120, 200), (240, 150, 70)]
    for i in range(6):
        for j in range(8):
            x, y = 140 + i * 160, 300 + j * 165
            col = cols[(i + 2 * j) % 6]
            c.rect(x - 45, y + 20, x + 45, y + 75, col, r=22, w=5)
            c.ell(x, y, 38, 38, SKIN[(i + j) % 3], w=5)


def s21(c):
    lab(c)
    c.rect(170, 280, 910, 820, (40, 80, 70), r=12)
    for k, ch in enumerate("+×÷−×+"):
        c.text(300 + (k % 3) * 240, 420 + (k // 3) * 230, ch, 130, fill=(255, 255, 255), stroke=(40, 80, 70), sw=0)
    person(c, "pablo", 540, 1450, 640, eyes="wide", mouth="o")
    bolt(c, 260, 950, 110); bolt(c, 830, 950, 110)


def s22(c):
    lab(c)
    c.rect(120, 1080, 960, 1120, (150, 155, 165), r=6)
    for x, col in ((330, (130, 190, 240)), (750, (190, 140, 230))):
        c.rect(x - 90, 800, x + 90, 1080, (235, 245, 250), r=20)
        c.rect(x - 70, 920, x + 70, 1060, col, r=14, outline=None)
        c.rect(x - 100, 770, x + 100, 820, (180, 185, 195), r=8)
    waves(c, 750, 640, 140)
    dog(c, 560, 1300, 0.75, face=1)


def s23(c):
    rays(c, (90, 170, 120), (110, 190, 140))
    c.text(540, 860, "+90%", 260, fill=MOUTARDE, sw=16)


def s24(c):
    c.img.paste((120, 95, 80), (0, 0, *c.img.size))
    bed_top(c, dog_pos="middle")


def s25(c):
    c.img.paste(NUIT, (0, 0, *c.img.size))
    person(c, "sofia", 540, 1500, 900, eyes="closed")
    heart(c, 540, 1000, 70)
    pts = [(120, 1000), (330, 1000), (370, 920), (410, 1080), (450, 1000)]
    c.line(pts, (235, 80, 100), 10)
    c.line([(630, 1000), (670, 920), (710, 1080), (750, 1000), (960, 1000)], (235, 80, 100), 10)


def s26(c):
    c.img.paste((120, 95, 80), (0, 0, *c.img.size))
    bed_top(c, dog_pos="middle", blanket=(120, 130, 180))
    for x, y in ((330, 700), (750, 700), (330, 1150), (750, 1150)):
        waves(c, x, y, 130)


def s27(c):
    c.img.paste((120, 95, 80), (0, 0, *c.img.size))
    bed_top(c, dog_pos="middle")
    big_x(c, 760, 560, 110)
    heart(c, 540, 1150, 70)
    check(c, 540, 1380, 90)


def s28(c):
    room(c, NUIT, (70, 60, 90), 1350)
    c.ell(820, 330, 110, 110, (250, 240, 190), outline=None)
    c.ell(870, 300, 100, 100, NUIT, outline=None)
    c.rect(140, 900, 940, 1500, (150, 100, 70), r=30)
    c.rect(180, 940, 900, 1460, (250, 250, 245), r=24)
    c.rect(330, 970, 750, 1160, (255, 255, 255), r=40)
    dog_face(c, 540, 1060, 120, eyes="closed")
    c.rect(180, 1200, 900, 1460, (205, 120, 95), r=24)
    zzz(c, 700, 860, 90)


def s29(c):
    c.img.paste((25, 25, 35), (0, 0, *c.img.size))
    dog_face(c, 540, 760, 200)
    c.text(540, 1180, "SÍGUEME", 120, fill=MOUTARDE)
    c.text(540, 1330, "@ton_compte", 70, fill=(255, 255, 255), sw=6)


# (dessin, voix off, mot à l'écran, son au début du plan)
PLANS = [
    (s01, "Si tu perro duerme contigo,", "CONTIGO", "whoosh"),
    (s02, "no es por comodidad.", "NO ES", "pop"),
    (s03, "La razón real es inquietante.", "INQUIETANTE", "boom"),
    (s04, "Mira a Sofía y a su hijo Hugo.", "SOFÍA", "whoosh"),
    (s05, "Cada noche, Sofía le dice a Salchicha: ¡a tu cama!", "A TU CAMA", "pop"),
    (s06, "Y cada noche, Salchicha acaba aquí.", "AQUÍ", None),
    (s07, "Hugo intenta distraerlo con su pelota.", "HUGO", None),
    (s08, "Nada. Ni la mira.", "NADA", "whoosh"),
    (s09, "Una noche, Sofía no puede dormir.", "3:00", None),
    (s10, "Está agotada, y llora en silencio.", "LLORA", None),
    (s11, "Nadie se da cuenta.", "NADIE", None),
    (s12, "Nadie, excepto él.", "EXCEPTO ÉL", "boom"),
    (s13, "Salchicha se sube al sofá y se pega a ella.", "SE PEGA", "pop"),
    (s14, "Y la ciencia tiene una explicación.", "CIENCIA", "whoosh"),
    (s15, "En Japón, midieron las lágrimas de muchos perros,", "LÁGRIMAS", None),
    (s16, "y al reencontrarse con su dueño, producían más.", "MÁS", "pop"),
    (s17, "Tu perro se emociona contigo.", "CONTIGO", None),
    (s18, "Pero hay más: su nariz.", "NARIZ", "boom"),
    (s19, "En Irlanda del Norte lo comprobaron,", "COMPROBADO", "pop"),
    (s20, "con muestras de aliento y sudor de personas,", "PERSONAS", None),
    (s21, "antes y después de un ejercicio estresante.", "ESTRÉS", None),
    (s22, "Los perros reconocieron el olor del estrés,", "OLOR", None),
    (s23, "en más del noventa por ciento de los casos.", "+90%", "pop"),
    (s24, "Así que, cuando duerme contigo,", "CONTIGO", "whoosh"),
    (s25, "está vigilando tu cuerpo.", "TU CUERPO", None),
    (s26, "Siente tus nervios, tus miedos, todo.", "TODO", None),
    (s27, "Y muchas personas dicen dormir mejor con su perro que con su pareja.", "MEJOR", "pop"),
    (s28, "No es tu cama lo que quiere. Eres tú.", "TÚ", "boom"),
    (s29, "Sígueme para más.", "", "whoosh"),
]
