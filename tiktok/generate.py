#!/usr/bin/env python3
"""Génère une vidéo TikTok verticale (1080x1920) façon « dessin animé explicatif ».

Montage calqué sur les vidéos de référence : une illustration par bout de phrase
(coupe toutes les 2-3 s), zoom lent + « punch » à chaque coupe, accessoires qui
apparaissent en pop, Pépito qui cligne des yeux et remue la queue, sous-titres
2 mots en minuscules, bruitages et petite musique de fond.

Voix : ElevenLabs, en une seule prise pour tout le texte (intonation naturelle) ;
les timestamps caractère par caractère calent les coupes et les sous-titres.

Usage :
  export ELEVENLABS_API_KEY=...      # obligatoire pour la voix
  export ELEVENLABS_VOICE_ID=...     # optionnel ; sinon une voix espagnole du compte est cherchée
  python3 tiktok/generate.py tiktok/script_perros.json -o out/cara_de_culpable.mp4

  --preview      : rendu sans ElevenLabs (voix muette, timing estimé) pour vérifier le visuel.
  --music FICHIER: remplace la musique générée par la tienne.
"""
import argparse
import base64
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import tempfile
import wave
from bisect import bisect_right
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
SR = 44100
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"  # voix multilingue ElevenLabs, remplaçable
MODEL_ID = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
VOICE_SETTINGS = {"stability": 0.35, "similarity_boost": 0.8, "style": 0.5,
                  "use_speaker_boost": True, "speed": 1.06}
CAPTION_Y = 1490  # au-dessus de la zone couverte par l'interface TikTok

# Style « dessin plat » : aplats chauds, contours épais.
INK = (45, 30, 20)
OL = dict(outline=INK, width=8)
BROWN, DARK, BELLY = (176, 98, 40), (110, 55, 20), (214, 150, 90)

# Pépito est dessiné sur un calque de 1400 px puis réduit et posé dans le décor.
DOG_K, DOG_X, DOG_Y = 0.76, 8, 300
DOG_CX, DOG_CY = 760, 1180  # centre du corps, en coordonnées du calque


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def norm(word):
    return word.lower().strip("¿?¡!.,;:…\"'«»()")


# ---------------------------------------------------------------- voix

def pick_voice(api_key):
    """ELEVENLABS_VOICE_ID, sinon la voix du compte qui sonne le plus espagnole."""
    if os.environ.get("ELEVENLABS_VOICE_ID"):
        return os.environ["ELEVENLABS_VOICE_ID"], "ELEVENLABS_VOICE_ID"
    try:
        r = requests.get("https://api.elevenlabs.io/v1/voices",
                         headers={"xi-api-key": api_key}, timeout=30)
        r.raise_for_status()
        best, score = None, 0
        for v in r.json().get("voices", []):
            labels = " ".join(str(x) for x in (v.get("labels") or {}).values()).lower()
            s = 3 if any(k in labels for k in ("spanish", "español", "latin", "mexic",
                                              "castilian", "argentin", "colombia")) else 0
            for lang in v.get("verified_languages") or []:
                if lang.get("language") == "es" and (lang.get("accent") or lang.get("locale")):
                    s = max(s, 2)
            if s > score:
                best, score = v, s
        if best:
            return best["voice_id"], best.get("name", "?")
    except Exception as e:  # clé limitée au Text to Speech, réseau…
        print(f"(liste des voix indisponible : {e})")
    return DEFAULT_VOICE, "voix par défaut"


def tts(text, voice_id, api_key, cache_dir):
    """Une seule synthèse pour tout le texte ; mise en cache pour ne pas repayer."""
    key = hashlib.sha1(json.dumps([text, voice_id, MODEL_ID, VOICE_SETTINGS]).encode()).hexdigest()[:16]
    cache_dir.mkdir(parents=True, exist_ok=True)
    mp3, js = cache_dir / f"{key}.mp3", cache_dir / f"{key}.json"
    if not (mp3.exists() and js.exists()):
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={"text": text, "model_id": MODEL_ID, "voice_settings": VOICE_SETTINGS},
            timeout=300,
        )
        if r.status_code != 200:
            sys.exit(f"ElevenLabs a répondu {r.status_code} : {r.text[:400]}")
        data = r.json()
        mp3.write_bytes(base64.b64decode(data["audio_base64"]))
        js.write_text(json.dumps(data["alignment"]))
    al = json.loads(js.read_text())
    return str(mp3), al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]


def estimate_alignment(text):
    """Mode aperçu : ~15 caractères/s, avec des pauses sur la ponctuation."""
    chars, starts, ends, t = [], [], [], 0.3
    for c in text:
        chars.append(c)
        starts.append(t)
        t += 1 / 15
        ends.append(t)
        if c in ",:;":
            t += 0.18
        elif c in ".?!…":
            t += 0.35
    return chars, starts, ends


def words_from_alignment(chars, starts, ends):
    words, cur, t0, t1 = [], "", None, None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                words.append([cur, t0, t1])
            cur, t0 = "", None
            continue
        if t0 is None:
            t0 = s
        cur += c
        t1 = e
    if cur:
        words.append([cur, t0, t1])
    return words


def split_words(words, beats):
    """Répartit les mots minutés entre les plans (même ordre que le texte)."""
    counts = [len(b["text"].split()) for b in beats]
    if len(words) != sum(counts):  # normalisation inattendue : répartition proportionnelle
        total = sum(counts)
        counts = [round(c * len(words) / total) for c in counts]
        counts[-1] = len(words) - sum(counts[:-1])
    out, i = [], 0
    for c in counts:
        out.append(words[i:i + c])
        i += c
    return out


# ---------------------------------------------------------------- dessins

def draw_pepito(d, pose):
    """Teckel cartoon (sans la queue, animée à part). pose : normal | guilty | sideeye | proud."""
    cx, cy = DOG_CX, DOG_CY
    for lx in (cx - 250, cx - 170, cx + 190, cx + 270):
        d.rounded_rectangle([lx - 26, cy + 40, lx + 26, cy + 170], 18, fill=DARK, **OL)
    d.rounded_rectangle([cx - 340, cy - 110, cx + 350, cy + 110], 110, fill=BROWN, **OL)
    d.ellipse([cx - 250, cy + 10, cx + 250, cy + 100], fill=BELLY)

    hx, hy = head_pos(pose)
    d.ellipse([hx - 150, hy - 140, hx + 150, hy + 140], fill=BROWN, **OL)
    d.rounded_rectangle([hx - 300, hy - 10, hx - 60, hy + 110], 55, fill=BELLY, **OL)
    d.ellipse([hx - 320, hy + 5, hx - 250, hy + 60], fill=(30, 15, 5))

    ear = [hx + 60, hy - 90, hx + 160, hy + 170] if pose == "guilty" \
        else [hx + 40, hy - 120, hx + 150, hy + 120]
    d.ellipse(ear, fill=DARK, **OL)

    for ex in (hx - 95, hx - 5):
        ey = hy - 40
        d.ellipse([ex - 38, ey - 42, ex + 38, ey + 42], fill="white", **OL)
        px = {"sideeye": 18, "guilty": -14}.get(pose, -8)
        py = {"guilty": 14}.get(pose, 0)
        d.ellipse([ex + px - 18, ey + py - 18, ex + px + 18, ey + py + 18], fill=(20, 10, 0))
        if pose in ("guilty", "sideeye"):  # paupières mi-closes
            d.chord([ex - 40, ey - 44, ex + 40, ey + 40], 180, 360, fill=BROWN)
            d.line([ex - 40, ey - 2, ex + 40, ey - 2], fill=INK, width=7)
        if pose == "guilty":  # sourcils inquiets
            d.line([ex - 35, ey - 70, ex + 30, ey - 85 if ex < hx - 50 else ey - 55],
                   fill=INK, width=9)

    mx, my = hx - 220, hy + 80
    if pose == "proud":
        d.arc([mx - 40, my - 20, mx + 60, my + 40], 10, 170, fill=INK, width=8)
    elif pose == "guilty":
        d.arc([mx - 30, my + 20, mx + 50, my + 60], 200, 340, fill=INK, width=8)
    else:
        d.line([mx - 20, my + 25, mx + 50, my + 25], fill=INK, width=8)

    if pose == "guilty":  # goutte de sueur
        d.polygon([(hx + 120, hy - 150), (hx + 95, hy - 90), (hx + 145, hy - 90)],
                  fill=(120, 200, 255))
        d.ellipse([hx + 95, hy - 115, hx + 145, hy - 65], fill=(120, 200, 255))

    # collier et médaille
    d.rounded_rectangle([hx + 20, hy + 105, hx + 130, hy + 135], 10, fill=(220, 30, 40))
    d.ellipse([hx + 55, hy + 125, hx + 95, hy + 165], fill=(255, 210, 0), **OL)


def head_pos(pose):
    return DOG_CX - 330, DOG_CY - 170 + (50 if pose == "guilty" else 0)  # tête basse


def to_world(x, y, dy=0.0):
    return DOG_X + x * DOG_K, DOG_Y + y * DOG_K + dy


def draw_room(setting):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    if setting == "lab":
        d.rectangle([0, 0, W, 1150], fill=(205, 232, 240))
        d.rectangle([0, 1150, W, H], fill=(225, 230, 235))
        for x in range(0, W, 135):  # carrelage
            d.line([x, 1150, x, H], fill=(190, 198, 205), width=4)
        for y in range(1150, H, 135):
            d.line([0, y, W, y], fill=(190, 198, 205), width=4)
        d.rounded_rectangle([60, 230, 600, 700], 20, fill="white", **OL)  # tableau
        d.text((330, 400), "2009", font=font(120), fill=(40, 90, 200), anchor="mm")
        d.text((330, 560), "experimento", font=font(54), fill=INK, anchor="mm")
        d.rectangle([60, 700, 600, 730], fill=(150, 150, 160), **OL)
        d.rectangle([680, 760, 1040, 782], fill=(150, 150, 160), **OL)  # étagère et fioles
        for x, col in ((720, (120, 200, 120)), (840, (240, 120, 160)), (960, (120, 170, 240))):
            d.rectangle([x + 22, 640, x + 48, 690], fill=(235, 245, 250), **OL)
            d.polygon([(x + 22, 690), (x + 48, 690), (x + 75, 758), (x - 5, 758)], fill=col, outline=INK, width=6)
    else:  # salon
        d.rectangle([0, 0, W, 1150], fill=(240, 200, 140))
        for x in range(0, W, 90):  # papier peint rayé
            d.rectangle([x, 0, x + 40, 1150], fill=(235, 190, 128))
        d.rectangle([0, 1150, W, H], fill=(214, 150, 92))
        for y in range(1150, H, 110):  # parquet
            d.line([0, y, W, y], fill=(185, 120, 68), width=5)
            off = 0 if (y // 110) % 2 else 160
            for x in range(off, W, 320):
                d.line([x, y, x, y + 110], fill=(185, 120, 68), width=5)
        d.rounded_rectangle([90, 180, 470, 560], 16, fill=(170, 220, 250), **OL)  # fenêtre
        d.line([280, 180, 280, 560], fill=INK, width=8)
        d.line([90, 370, 470, 370], fill=INK, width=8)
        d.ellipse([340, 220, 440, 320], fill=(255, 215, 60))
        d.rounded_rectangle([560, 250, 760, 440], 10, fill=(255, 245, 225), outline=(150, 90, 40), width=14)
        for px, py, r in ((660, 365, 34), (615, 310, 14), (650, 295, 14), (690, 300, 14), (715, 330, 14)):
            d.ellipse([px - r, py - r, px + r, py + r], fill=(176, 98, 40))  # empreinte de patte
        d.line([0, 70, W, 110], fill=INK, width=5)  # guirlande de fanions
        cols = [(230, 80, 100), (90, 140, 200), (255, 200, 60), (110, 190, 130)]
        for k, x in enumerate(range(20, W, 110)):
            y = 70 + 40 * x / W
            d.polygon([(x, y), (x + 80, y + 3), (x + 40, y + 75)], fill=cols[k % 4], outline=INK, width=5)
        d.rounded_rectangle([560, 760, 1060, 1120], 50, fill=(90, 140, 200), **OL)  # canapé
        d.rounded_rectangle([600, 680, 1020, 900], 40, fill=(110, 160, 220), **OL)
    # tapis jaune à bord pointillé, sous les sous-titres
    d.rounded_rectangle([40, 1400, W - 40, 1600], 50, fill=(250, 225, 130), **OL)
    for x in range(100, W - 100, 50):
        d.line([x, 1430, x + 25, 1430], fill=INK, width=5)
        d.line([x, 1570, x + 25, 1570], fill=INK, width=5)
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse([120, 1290, 960, 1370], fill=80)
    img.paste((0, 0, 0), mask=shadow.filter(ImageFilter.GaussianBlur(20)))
    return img


_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT_BOLD, size)
    return _fonts[size]


def heart(d, x, y, r, fill=(240, 80, 120)):
    d.ellipse([x - r, y - r, x, y], fill=fill)
    d.ellipse([x, y - r, x + r, y], fill=fill)
    d.polygon([(x - r, y - r // 2), (x + r, y - r // 2), (x, y + r)], fill=fill)


def prop_cushion(d):
    d.rounded_rectangle([660, 740, 900, 880], 40, fill=(230, 80, 100), **OL)


def prop_feathers(d):
    rnd = random.Random(7)
    for _ in range(30):
        x, y = rnd.randint(40, W - 40), rnd.randint(1180, 1400)
        r = rnd.randint(16, 34)
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(252, 252, 248),
                  outline=(170, 170, 170), width=3)
    d.polygon([(760, 1300), (980, 1260), (1010, 1360), (800, 1390)],
              fill=(230, 80, 100), outline=INK, width=8)  # cojín roto


def prop_cookie(d):
    d.ellipse([90, 1250, 250, 1390], fill=(205, 145, 70), **OL)
    for cx, cy in ((140, 1300), (195, 1290), (170, 1345), (215, 1340)):
        d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(90, 50, 20))


def prop_question(d):
    for x, y in ((380, 760), (520, 700)):
        d.text((x, y), "?", font=font(150), fill="white", stroke_width=8, stroke_fill=INK)


def prop_hearts(d):
    for x, y, r in ((360, 760, 40), (470, 690, 30), (560, 780, 34)):
        heart(d, x, y, r)


def prop_clock(d):
    d.ellipse([800, 220, 1020, 440], fill="white", **OL)
    d.line([910, 330, 910, 245], fill=INK, width=10)
    d.line([910, 330, 985, 330], fill=INK, width=10)
    d.text((910, 500), "-3 h", font=font(70), fill="white", anchor="mm",
           stroke_width=6, stroke_fill=INK)


def prop_owner_angry(d):  # la dueña, enfadada, entra en el cuadro
    ox, oy = 650, 140
    d.ellipse([ox, oy, ox + 380, oy + 380], fill=(250, 205, 170), **OL)
    d.chord([ox - 15, oy - 30, ox + 395, oy + 250], 180, 360, fill=(120, 70, 40), **OL)
    for ex, tilt in ((ox + 120, 1), (ox + 260, -1)):
        d.ellipse([ex - 20, oy + 190, ex + 20, oy + 232], fill=INK)
        d.line([ex - 45, oy + 150 - 22 * tilt, ex + 45, oy + 150 + 22 * tilt],
               fill=INK, width=14)
    d.ellipse([ox + 50, oy + 250, ox + 105, oy + 285], fill=(240, 130, 130))
    d.ellipse([ox + 275, oy + 250, ox + 330, oy + 285], fill=(240, 130, 130))
    d.arc([ox + 130, oy + 280, ox + 250, oy + 360], 200, 340, fill=INK, width=10)
    d.text((ox - 60, oy - 20), "!", font=font(160), fill=(230, 50, 50),
           stroke_width=8, stroke_fill=INK)


def prop_no_sorry(d):  # bulle « lo siento » barrée : ce n'est pas de la culpabilité
    d.ellipse([110, 500, 640, 790], fill="white", **OL)
    d.ellipse([300, 820, 350, 860], fill="white", **OL)
    d.ellipse([330, 880, 360, 905], fill="white", **OL)
    d.text((375, 645), "lo siento", font=font(78), fill=INK, anchor="mm")
    for a, b in (((190, 560), (560, 730)), ((190, 730), (560, 560))):
        d.line([a, b], fill=INK, width=32)
        d.line([a, b], fill=(225, 40, 40), width=20)


def prop_name_tag(d):
    d.rounded_rectangle([170, 560, 910, 690], 30, fill=(220, 40, 60), **OL)
    d.text((540, 625), "Pépito Saucisse", font=font(70), fill="white", anchor="mm",
           stroke_width=4, stroke_fill=INK)


def prop_lightbulb(d):
    x, y = 850, 360
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([x + 120 * math.cos(r), y + 120 * math.sin(r),
                x + 165 * math.cos(r), y + 165 * math.sin(r)], fill=(255, 190, 0), width=12)
    d.ellipse([x - 85, y - 95, x + 85, y + 75], fill=(255, 225, 70), **OL)
    d.rounded_rectangle([x - 45, y + 65, x + 45, y + 130], 12, fill=(150, 150, 160), **OL)


def prop_magnifier(d):  # posée sur le tableau, comme pour l'examiner
    x, y = 560, 500
    d.line([x + 80, y + 80, x + 180, y + 190], fill=INK, width=44)
    d.line([x + 80, y + 80, x + 180, y + 190], fill=(150, 90, 40), width=30)
    d.ellipse([x - 120, y - 120, x + 120, y + 120], fill=(200, 235, 255), outline=INK, width=26)
    d.arc([x - 80, y - 85, x + 40, y + 20], 190, 260, fill="white", width=12)


def prop_white_flag(d):  # señal de calma
    d.line([600, 1110, 600, 700], fill=INK, width=14)
    d.polygon([(606, 705), (700, 690), (780, 725), (700, 760), (606, 790)],
              fill="white", outline=INK, width=7)


def prop_comment(d):
    d.rounded_rectangle([620, 240, 1030, 500], 60, fill="white", **OL)
    d.polygon([(700, 495), (680, 590), (780, 498)], fill="white", outline=INK, width=8)
    d.line([710, 498, 770, 498], fill="white", width=10)
    for k in range(3):
        d.ellipse([700 + k * 85, 345, 750 + k * 85, 395], fill=INK)
    heart(d, 990, 250, 45)


PROPS = {n[5:]: f for n, f in list(globals().items()) if n.startswith("prop_")}


def sprite(draw_fn, size=(W, H)):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    box = layer.getbbox()
    return layer.crop(box), box[0], box[1]


def dog_sprite(pose):
    img, x, y = sprite(lambda d: draw_pepito(d, pose), (1400, H))
    img = img.resize((round(img.width * DOG_K), round(img.height * DOG_K)), Image.LANCZOS)
    return img, round(DOG_X + x * DOG_K), round(DOG_Y + y * DOG_K)


# ---------------------------------------------------------------- animation

def ease_out_back(x):
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


TOP_PROPS = {"owner_angry", "clock", "lightbulb", "comment", "name_tag", "no_sorry"}

CAMERAS = {  # (centre x, centre y, zoom) en coordonnées du décor
    "wide": (540, 960, 1.0),
    "dog": (400, 1040, 1.7),
    "medium": (480, 980, 1.3),
    "owner": (600, 700, 1.25),
    "board": (420, 760, 1.45),
}


def draw_tail(d, pose, t, dy):
    up = pose in ("proud", "normal")
    bx, by = (DOG_CX + 330, DOG_CY - 30) if up else (DOG_CX + 330, DOG_CY + 10)
    vx, vy = (90, -140) if up else (110, 50)
    amp, freq = {"proud": (0.45, 2.6), "normal": (0.3, 2.0),
                 "sideeye": (0.15, 1.2), "guilty": (0.12, 1.5)}[pose]  # la colita, despacito
    a = amp * math.sin(2 * math.pi * freq * t)
    ex, ey = bx + vx * math.cos(a) - vy * math.sin(a), by + vx * math.sin(a) + vy * math.cos(a)
    p0, p1 = to_world(bx, by, dy), to_world(ex, ey, dy)
    d.line([p0, p1], fill=INK, width=28)
    d.line([p0, p1], fill=DARK, width=20)
    d.ellipse([p1[0] - 13, p1[1] - 13, p1[0] + 13, p1[1] + 13], fill=DARK, outline=INK, width=4)


def draw_blink(d, pose, dy):
    hx, hy = head_pos(pose)
    for ex in (hx - 95, hx - 5):
        x, y = to_world(ex, hy - 40, dy)
        d.ellipse([x - 30, y - 33, x + 30, y + 32], fill=BROWN, outline=INK, width=6)
        d.line([x - 30, y, x + 30, y], fill=INK, width=6)


class Timeline:
    """Plans minutés + accessoires programmés + rendu image par image."""

    def __init__(self, beats, beat_words, total):
        self.beats = beats
        self.total = total
        self.rooms = {s: draw_room(s) for s in {b.get("setting", "salon") for b in beats}}
        self.dogs = {p: dog_sprite(p) for p in {b.get("pose", "normal") for b in beats}}
        self.props = {}
        self.sfx = []  # (temps, type)
        starts = []
        for i, ws in enumerate(beat_words):
            if i == 0:
                starts.append(0.0)
            else:  # la coupe tombe juste avant le premier mot du plan
                starts.append(max(starts[-1] + 0.4, ws[0][1] - 0.06 if ws else 0.0))
        for i, b in enumerate(beats):
            b["t0"] = starts[i]
            b["t1"] = starts[i + 1] if i + 1 < len(beats) else total
            b["words"] = beat_words[i]
            self._schedule(i, b)
        self.shots = [s for i, b in enumerate(beats) for s in self._shots(i, b)]
        self.shot_starts = [s[0] for s in self.shots]

    def _schedule(self, i, b):
        prev = self.beats[i - 1] if i else None
        same_room = prev is not None and prev.get("setting", "salon") == b.get("setting", "salon")
        prev_names = {p["name"] for p in prev["_props"]} if same_room else set()
        if prev is not None and not same_room:
            self.sfx.append((b["t0"], "whoosh"))
        b["_props"], b["shake"] = [], None
        for k, spec in enumerate(b.get("props", [])):
            name, at = (spec, None) if isinstance(spec, str) else (spec["name"], spec.get("at"))
            if name not in self.props:
                self.props[name] = sprite(PROPS[name])
            if name in prev_names and at is None:  # déjà à l'écran : pas de nouveau pop
                b["_props"].append({"name": name, "t": b["t0"], "pop": False})
                continue
            t = b["t0"] + 0.12 + 0.1 * k
            if at:
                t = next((w[1] for w in b["words"] if norm(w[0]).startswith(norm(at))), t)
            b["_props"].append({"name": name, "t": t, "pop": True})
            self.sfx.append((t, "ding" if name == "lightbulb" else "pop"))
            if name == "owner_angry":
                b["shake"] = t
        b["hop"] = prev is None or prev.get("pose") != b.get("pose")

    def _shots(self, i, b):
        """Un plan de plus de 3,6 s est recoupé en deux, comme dans la référence :
        sur le mot qui fait apparaître un accessoire (même cadrage, effet « punch »),
        sinon au mot le plus proche du milieu, avec un autre cadrage."""
        cam, t0, t1 = b.get("camera", "wide"), b["t0"], b["t1"]
        if t1 - t0 <= 3.6:
            return [(t0, t1, i, cam)]
        ok = lambda t: t0 + 1.2 <= t <= t1 - 1.2
        cuts = [p["t"] - 0.04 for p in b["_props"] if p["pop"] and p["t"] > t0 + 0.5 and ok(p["t"] - 0.04)]
        if cuts:
            cut, cam2 = cuts[0], cam
        else:
            mid = (t0 + t1) / 2
            cands = [w[1] - 0.06 for w in b["words"][1:] if ok(w[1] - 0.06)]
            if not cands:
                return [(t0, t1, i, cam)]
            cut = min(cands, key=lambda t: abs(t - mid))
            cam2 = {"wide": "medium", "medium": "wide", "dog": "medium",
                    "owner": "wide", "board": "wide"}[cam]
            if cam == "wide" and any(p["name"] in TOP_PROPS for p in b["_props"]):
                cam2 = cam  # un recadrage couperait l'accessoire du haut : simple « punch »
        return [(t0, cut, i, cam), (cut, t1, i, cam2)]

    def frame(self, t):
        k = max(0, bisect_right(self.shot_starts, t) - 1)
        s0, s1, i, camera = self.shots[k]
        b = self.beats[i]
        tl, dur = t - s0, max(0.1, s1 - s0)
        pose = b.get("pose", "normal")
        world = self.rooms[b.get("setting", "salon")].copy()
        d = ImageDraw.Draw(world)

        dy = 3 * math.sin(2 * math.pi * 0.6 * t)  # respiration
        if b["hop"] and t - b["t0"] < 0.3:
            dy -= 26 * math.sin(math.pi * (t - b["t0"]) / 0.3)
        draw_tail(d, pose, t, dy)
        img, x, y = self.dogs[pose]
        world.paste(img, (x, round(y + dy)), img)
        if pose in ("normal", "proud") and (t + 0.7 * i) % 3.1 < 0.13:
            draw_blink(d, pose, dy)

        for p in b["_props"]:
            if t < p["t"]:
                continue
            img, x, y = self.props[p["name"]]
            u = (t - p["t"]) / 0.3
            if p["pop"] and u < 1:
                s = max(0.05, ease_out_back(u))
                sw, sh = max(1, round(img.width * s)), max(1, round(img.height * s))
                small = img.resize((sw, sh), Image.BILINEAR)
                world.paste(small, (round(x + (img.width - sw) / 2), round(y + (img.height - sh) / 2)), small)
            else:
                world.paste(img, (x, y), img)

        cx, cy, z = CAMERAS[camera]
        u = tl / dur
        z *= (1 + 0.045 * u) if k % 2 == 0 else (1.045 - 0.045 * u)  # zoom lent, alterné
        z *= 1 + 0.08 * (1 - ease_out_cubic(min(1.0, tl / 0.25)))  # « punch » à la coupe
        z = max(z, 1.02)
        if b["shake"] is not None and 0 <= t - b["shake"] < 0.4:
            st = t - b["shake"]
            amp = 10 * math.exp(-st * 9)
            cx += amp * math.sin(70 * st)
            cy += amp * math.cos(55 * st)
        w, h = W / z, H / z
        cx = min(max(cx, w / 2), W - w / 2)
        cy = min(max(cy, h / 2), H - h / 2)
        return world.resize((W, H), Image.BILINEAR, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))


# ---------------------------------------------------------------- son

def write_wav(path, mono):
    pcm = (np.clip(mono, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(np.repeat(pcm, 2).tobytes())


def pluck(freq, dur=0.7, seed=0):
    """Corde pincée (Karplus-Strong), façon ukulélé."""
    rng = np.random.default_rng(seed)
    n, p = int(dur * SR), int(SR / freq)
    buf = list(rng.uniform(-1, 1, p))
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = 0.996 * 0.5 * (buf[j] + buf[(j + 1) % p])
    return out * np.linspace(1, 0, n) ** 0.5


def make_music(total):
    """Petite boucle légère (Do-Sol-Lam-Fa, 100 bpm) pour le fond."""
    out = np.zeros(int((total + 1) * SR))
    eighth = 60 / 100 / 2
    chords = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]
    order = (0, 1, 2, 1, 2, 1, 0, 1)
    cache = {}
    t, i = 0.0, 0
    while t < total:
        chord = chords[(i // 8) % 4]
        note = chord[order[i % 8]] + 12
        if note not in cache:
            cache[note] = pluck(440 * 2 ** ((note - 69) / 12), seed=note)
        s = int(t * SR)
        seg = cache[note][: len(out) - s]
        out[s:s + len(seg)] += 0.3 * seg
        if i % 4 == 0:  # basse douce
            bt = np.arange(int(0.5 * SR)) / SR
            f = 440 * 2 ** ((chord[0] - 24 - 69) / 12)
            bass = 0.35 * np.sin(2 * np.pi * f * bt) * np.exp(-bt * 5)
            bass = bass[: len(out) - s]
            out[s:s + len(bass)] += bass
        t += eighth
        i += 1
    out = out[: int(total * SR)]
    fade = np.ones_like(out)
    fi, fo = int(0.5 * SR), int(1.5 * SR)
    fade[:fi] = np.linspace(0, 1, fi)
    fade[-fo:] = np.linspace(1, 0, fo)
    out *= fade
    return 0.9 * out / (np.abs(out).max() + 1e-9)


def sfx_sound(kind, rng):
    if kind == "pop":
        t = np.arange(int(0.09 * SR)) / SR
        f = 300 + 700 * np.exp(-t * 40)
        return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)
    if kind == "ding":
        t = np.arange(int(1.2 * SR)) / SR
        return 0.35 * (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 4)
    n = int(0.5 * SR)  # whoosh : bruit filtré qui monte puis redescend
    noise, y, prev = rng.normal(0, 1, n), np.empty(n), 0.0
    for i in range(n):
        fc = 400 + 3500 * math.sin(math.pi * i / n)
        prev += (1 - math.exp(-2 * math.pi * fc / SR)) * (noise[i] - prev)
        y[i] = prev
    y *= np.sin(np.pi * np.arange(n) / n) ** 2
    return 0.5 * y / (np.abs(y).max() + 1e-9)


def make_sfx(events, total):
    out = np.zeros(int(total * SR))
    rng = np.random.default_rng(1)
    sounds = {}
    for t, kind in events:
        if kind not in sounds:
            sounds[kind] = sfx_sound(kind, rng)
        s = int(t * SR)
        seg = sounds[kind][: max(0, len(out) - s)]
        out[s:s + len(seg)] += seg
    return out


# ---------------------------------------------------------------- sous-titres

def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_ass(beats, emph, path):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,92,&H00FFFFFF,&H00FFFFFF,&H00141E28,&H78000000,-1,0,0,0,100,100,0,0,1,9,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    emph = {norm(w) for w in emph}
    chunks = []  # comme les vidéos de référence : 2 mots à la fois, en minuscules
    for b in beats:
        ws = b["words"]
        for i in range(0, len(ws), 2):
            chunks.append(ws[i:i + 2])
    lines = []
    for k, chunk in enumerate(chunks):
        start = chunk[0][1]
        end = chunk[-1][2] + 0.5
        if k + 1 < len(chunks):
            end = min(end, chunks[k + 1][0][1])
        words = [("{\\c&H00E1FF&}%s{\\c&HFFFFFF&}" % w.lower()) if norm(w) in emph else w.lower()
                 for w, _, _ in chunk]
        size = len(" ".join(w for w, _, _ in chunk))
        fs = "\\fs%d" % max(58, 92 * 15 // size) if size > 15 else ""
        pop = "\\fscx75\\fscy75\\t(0,90,\\fscx108\\fscy108)\\t(90,170,\\fscx100\\fscy100)"
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,"
                     f"{{\\pos({W // 2},{CAPTION_Y}){fs}{pop}}}{' '.join(words)}")
    Path(path).write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- montage

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("-o", "--out", default="out/tiktok.mp4")
    ap.add_argument("--preview", action="store_true",
                    help="sans ElevenLabs : voix muette, timing estimé")
    ap.add_argument("--music", help="fichier audio à utiliser comme musique de fond")
    ap.add_argument("--music-volume", type=float, default=0.10)
    args = ap.parse_args()

    data = json.loads(Path(args.script).read_text(encoding="utf-8"))
    beats = data["beats"]
    text = " ".join(b["text"] for b in beats)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="tiktok_"))

    if args.preview:
        chars, starts, ends = estimate_alignment(text)
        voice = None
    else:
        api_key = os.environ.get("ELEVENLABS_API_KEY")
        if not api_key:
            sys.exit("ELEVENLABS_API_KEY manquante (ou utilise --preview).")
        voice_id, voice_name = pick_voice(api_key)
        print(f"Voix ElevenLabs : {voice_name} ({voice_id}), modèle {MODEL_ID}")
        voice, chars, starts, ends = tts(text, voice_id, api_key, out.parent / ".tts_cache")

    words = words_from_alignment(chars, starts, ends)
    total = words[-1][2] + 1.0
    tl = Timeline(beats, split_words(words, beats), total)
    print(f"{len(tl.shots)} plans, {total:.1f} s")

    if voice is None:
        voice = str(tmp / "voice.wav")
        write_wav(voice, np.zeros(int(total * SR)))
    music = args.music
    if not music:
        music = str(tmp / "music.wav")
        write_wav(music, make_music(total))
    sfx = str(tmp / "sfx.wav")
    write_wav(sfx, make_sfx(tl.sfx, total))
    ass = tmp / "subs.ass"
    write_ass(beats, data.get("emph", []), ass)

    log = open(tmp / "ffmpeg.log", "wb")
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", voice, "-stream_loop", "-1", "-i", music, "-i", sfx,
         "-filter_complex",
         f"[0:v]ass={ass}[v];"
         f"[1:a]aresample={SR},apad[a1];[2:a]aresample={SR},volume={args.music_volume}[a2];"
         f"[3:a]aresample={SR},volume=0.6[a3];"
         "[a1][a2][a3]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]",
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)],
        stdin=subprocess.PIPE, stderr=log)
    n = math.ceil(total * FPS)
    for f in range(n):
        enc.stdin.write(tl.frame(f / FPS).tobytes())
        if f % (FPS * 10) == 0:
            print(f"  rendu {f / FPS:5.1f} / {total:.1f} s", flush=True)
    enc.stdin.close()
    if enc.wait() != 0:
        sys.exit("ffmpeg a échoué :\n" + (tmp / "ffmpeg.log").read_text(errors="replace"))
    print(f"OK -> {out} ({total:.1f} s)")


if __name__ == "__main__":
    main()
