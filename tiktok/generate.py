#!/usr/bin/env python3
"""Génère une vidéo TikTok verticale (1080x1920) à partir d'un script JSON.

Voix : ElevenLabs (text-to-speech avec timestamps -> sous-titres mot à mot).
Visuels : Pépito Saucisse, teckel en dessin plat (Pillow), décors salon / labo.

Usage :
  export ELEVENLABS_API_KEY=...            # obligatoire pour la voix
  export ELEVENLABS_VOICE_ID=...           # optionnel (voix espagnole de ton choix)
  python3 tiktok/generate.py tiktok/script_perros.json -o out/cara_de_culpable.mp4

  --preview : rendu sans ElevenLabs (audio muet, timing estimé) pour vérifier le visuel.
"""
import argparse
import base64
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEFAULT_VOICE = "JBFqnCBsd6RMkjVDRZzb"  # voix multilingue ElevenLabs, remplaçable
MODEL_ID = "eleven_multilingual_v2"


# ---------------------------------------------------------------- voix

def tts_elevenlabs(text, out_mp3, api_key, voice_id):
    """Synthèse ElevenLabs ; renvoie la liste des mots [(mot, début, fin)]."""
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": MODEL_ID,
            "voice_settings": {"stability": 0.4, "similarity_boost": 0.8,
                               "style": 0.45, "use_speaker_boost": True},
        },
        timeout=120,
    )
    if r.status_code != 200:
        sys.exit(f"ElevenLabs a répondu {r.status_code} : {r.text[:300]}")
    data = r.json()
    Path(out_mp3).write_bytes(base64.b64decode(data["audio_base64"]))
    al = data["alignment"]
    return chars_to_words(al["characters"], al["character_start_times_seconds"],
                          al["character_end_times_seconds"])


def chars_to_words(chars, starts, ends):
    words, cur, t0, t1 = [], "", None, None
    for c, s, e in zip(chars, starts, ends):
        if c.isspace():
            if cur:
                words.append((cur, t0, t1))
            cur, t0 = "", None
            continue
        if t0 is None:
            t0 = s
        cur += c
        t1 = e
    if cur:
        words.append((cur, t0, t1))
    return words


def silent_preview(text, out_audio):
    """Mode aperçu : audio muet et timing estimé (~2,7 mots/s)."""
    tokens = text.split()
    step = 1 / 2.7
    words = [(w, i * step, (i + 1) * step) for i, w in enumerate(tokens)]
    dur = len(tokens) * step + 0.3
    run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", f"{dur:.2f}", "-q:a", "9", out_audio])
    return words


def duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path])
    return float(out)


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


# ---------------------------------------------------------------- visuels

def draw_pepito(img, pose):
    """Teckel cartoon. pose : normal | guilty | sideeye | proud."""
    d = ImageDraw.Draw(img)
    W = img.width  # calque plus large que l'écran, réduit ensuite
    brown, dark, belly = (176, 98, 40), (110, 55, 20), (214, 150, 90)
    cx, cy = W // 2 + 60, 1180
    ol = dict(outline=(40, 20, 5), width=8)

    tail_up = pose in ("proud", "normal")
    tx = cx + 330
    if tail_up:
        d.line([tx, cy - 30, tx + 90, cy - 170], fill=dark, width=26)
    else:
        d.line([tx, cy + 10, tx + 110, cy + 60], fill=dark, width=26)
    for lx in (cx - 250, cx - 170, cx + 190, cx + 270):
        d.rounded_rectangle([lx - 26, cy + 40, lx + 26, cy + 170], 18, fill=dark, **ol)
    d.rounded_rectangle([cx - 340, cy - 110, cx + 350, cy + 110], 110, fill=brown, **ol)
    d.ellipse([cx - 250, cy + 10, cx + 250, cy + 100], fill=belly)

    hx, hy = cx - 330, cy - 170
    if pose == "guilty":
        hy += 50  # tête basse
    d.ellipse([hx - 150, hy - 140, hx + 150, hy + 140], fill=brown, **ol)
    d.rounded_rectangle([hx - 300, hy - 10, hx - 60, hy + 110], 55, fill=belly, **ol)
    d.ellipse([hx - 320, hy + 5, hx - 250, hy + 60], fill=(30, 15, 5))

    ear = [hx + 60, hy - 90, hx + 160, hy + 170] if pose == "guilty" \
        else [hx + 40, hy - 120, hx + 150, hy + 120]
    d.ellipse(ear, fill=dark, **ol)

    for ex in (hx - 95, hx - 5):
        ey = hy - 40
        d.ellipse([ex - 38, ey - 42, ex + 38, ey + 42], fill="white", **ol)
        px = {"sideeye": 18, "guilty": -14}.get(pose, -8)
        py = {"guilty": 14}.get(pose, 0)
        d.ellipse([ex + px - 18, ey + py - 18, ex + px + 18, ey + py + 18], fill=(20, 10, 0))
        if pose == "guilty":
            d.chord([ex - 40, ey - 44, ex + 40, ey + 40], 180, 360, fill=brown)
            d.line([ex - 40, ey - 2, ex + 40, ey - 2], fill=(40, 20, 5), width=7)
            d.line([ex - 35, ey - 70, ex + 30, ey - 85 if ex < hx - 50 else ey - 55],
                   fill=(40, 20, 5), width=9)
        elif pose == "sideeye":
            d.chord([ex - 40, ey - 44, ex + 40, ey + 40], 180, 360, fill=brown)
            d.line([ex - 40, ey - 2, ex + 40, ey - 2], fill=(40, 20, 5), width=7)

    mx, my = hx - 220, hy + 80
    if pose == "proud":
        d.arc([mx - 40, my - 20, mx + 60, my + 40], 10, 170, fill=(40, 20, 5), width=8)
    elif pose == "guilty":
        d.arc([mx - 30, my + 20, mx + 50, my + 60], 200, 340, fill=(40, 20, 5), width=8)
    else:
        d.line([mx - 20, my + 25, mx + 50, my + 25], fill=(40, 20, 5), width=8)

    if pose == "guilty":  # goutte de sueur
        d.polygon([(hx + 120, hy - 150), (hx + 95, hy - 90), (hx + 145, hy - 90)],
                  fill=(120, 200, 255))
        d.ellipse([hx + 95, hy - 115, hx + 145, hy - 65], fill=(120, 200, 255))

    # étiquette du collier
    d.rounded_rectangle([hx + 20, hy + 105, hx + 130, hy + 135], 10, fill=(220, 30, 40))
    d.ellipse([hx + 55, hy + 125, hx + 95, hy + 165], fill=(255, 210, 0), **ol)




# Style « dessin plat » : aplats chauds, contours épais, décor de pièce.
INK = (45, 30, 20)
OL = dict(outline=INK, width=8)


def draw_room(d, setting):
    if setting == "lab":
        d.rectangle([0, 0, W, 1150], fill=(205, 232, 240))
        d.rectangle([0, 1150, W, H], fill=(225, 230, 235))
        for x in range(0, W, 135):  # carrelage
            d.line([x, 1150, x, H], fill=(190, 198, 205), width=4)
        for y in range(1150, H, 135):
            d.line([0, y, W, y], fill=(190, 198, 205), width=4)
        d.rounded_rectangle([60, 230, 600, 700], 20, fill="white", **OL)
        f = ImageFont.truetype(FONT_BOLD, 120)
        d.text((330, 400), "2009", font=f, fill=(40, 90, 200), anchor="mm")
        f2 = ImageFont.truetype(FONT_BOLD, 54)
        d.text((330, 560), "experimento", font=f2, fill=INK, anchor="mm")
        d.rectangle([60, 700, 600, 730], fill=(150, 150, 160), **OL)
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
        d.rounded_rectangle([560, 760, 1060, 1120], 50, fill=(90, 140, 200), **OL)  # canapé
        d.rounded_rectangle([600, 680, 1020, 900], 40, fill=(110, 160, 220), **OL)
    # tapis jaune à bord pointillé (zone des sous-titres)
    d.rounded_rectangle([40, 1420, W - 40, 1800], 50, fill=(250, 225, 130), **OL)
    for x in range(100, W - 100, 50):
        d.line([x, 1460, x + 25, 1460], fill=INK, width=5)
        d.line([x, 1760, x + 25, 1760], fill=INK, width=5)


def draw_props(d, props):
    rnd = random.Random(7)
    if "cushion" in props:
        d.rounded_rectangle([660, 740, 900, 880], 40, fill=(230, 80, 100), **OL)
    if "feathers" in props:
        for _ in range(30):
            x, y = rnd.randint(40, W - 40), rnd.randint(1180, 1400)
            r = rnd.randint(16, 34)
            d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(252, 252, 248),
                      outline=(170, 170, 170), width=3)
        d.polygon([(760, 1300), (980, 1260), (1010, 1360), (800, 1390)],
                  fill=(230, 80, 100), outline=INK, width=8)  # cojín roto
    if "cookie" in props:
        d.ellipse([90, 1250, 250, 1390], fill=(205, 145, 70), **OL)
        for cx, cy in ((140, 1300), (195, 1290), (170, 1345), (215, 1340)):
            d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=(90, 50, 20))
    if "question" in props:
        f = ImageFont.truetype(FONT_BOLD, 150)
        for x, y in ((380, 780), (520, 720)):
            d.text((x, y), "?", font=f, fill="white", stroke_width=8, stroke_fill=INK)
    if "hearts" in props:
        for x, y, r in ((360, 760, 40), (470, 690, 30), (560, 780, 34)):
            d.ellipse([x - r, y - r, x, y], fill=(240, 80, 120))
            d.ellipse([x, y - r, x + r, y], fill=(240, 80, 120))
            d.polygon([(x - r, y - r // 2), (x + r, y - r // 2), (x, y + r)],
                      fill=(240, 80, 120))
    if "clock" in props:
        d.ellipse([720, 230, 960, 470], fill="white", **OL)
        d.line([840, 350, 840, 260], fill=INK, width=10)
        d.line([840, 350, 920, 350], fill=INK, width=10)
        f = ImageFont.truetype(FONT_BOLD, 70)
        d.text((840, 530), "-3 h", font=f, fill="white", anchor="mm",
               stroke_width=6, stroke_fill=INK)
    if "owner_angry" in props:  # la dueña, enfadada, que entra en el cuadro
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
        f = ImageFont.truetype(FONT_BOLD, 160)
        d.text((ox - 60, oy - 20), "!", font=f, fill=(230, 50, 50), stroke_width=8, stroke_fill=INK)


def render_scene(scene, out_png):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    draw_room(d, scene.get("setting", "salon"))
    props = scene.get("props", [])
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse([120, 1290, 960, 1370], fill=80)
    img.paste((0, 0, 0), mask=shadow.filter(ImageFilter.GaussianBlur(20)))
    layer = Image.new("RGBA", (1400, H), (0, 0, 0, 0))
    draw_pepito(layer, scene.get("pose", "normal"))
    k = 0.76
    layer = layer.resize((int(1400 * k), int(H * k)), Image.LANCZOS)
    img.paste(layer, ((W - layer.width) // 2, 300), layer)
    draw_props(ImageDraw.Draw(img), props)
    img.save(out_png)


# ---------------------------------------------------------------- sous-titres

def ass_time(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_ass(words, path):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,96,&H00FFFFFF,&H00FFFFFF,&H00281E14,&H64000000,-1,0,0,0,100,100,0,0,1,9,0,2,70,70,255,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    # comme les vidéos de référence : 2 mots à la fois, en minuscules
    for scene_words in words:
        for i in range(0, len(scene_words), 2):
            chunk = scene_words[i:i + 2]
            end = (scene_words[i + 2][1] if i + 2 < len(scene_words)
                   else chunk[-1][2] + 0.2)
            txt = " ".join(w for w, _, _ in chunk).lower()
            if len(txt) > 16:  # mots longs : on réduit plutôt que de couper la ligne
                txt = "{\\fs%d}" % max(60, 96 * 16 // len(txt)) + txt
            lines.append(f"Dialogue: 0,{ass_time(chunk[0][1])},{ass_time(end)},Cap,,0,0,0,,{txt}")
    Path(path).write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- montage

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("-o", "--out", default="out/tiktok.mp4")
    ap.add_argument("--preview", action="store_true",
                    help="sans ElevenLabs : audio muet, timing estimé")
    args = ap.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key and not args.preview:
        sys.exit("ELEVENLABS_API_KEY manquante (ou utilise --preview).")
    voice = os.environ.get("ELEVENLABS_VOICE_ID", DEFAULT_VOICE)

    scenes = json.loads(Path(args.script).read_text(encoding="utf-8"))["scenes"]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="tiktok_"))

    all_words, clips, offset = [], [], 0.0
    pad = 0.25  # respiration entre les scènes
    for i, sc in enumerate(scenes):
        print(f"[{i + 1}/{len(scenes)}] {sc['text'][:50]}…")
        audio = str(tmp / f"a{i}.mp3")
        words = (silent_preview(sc["text"], audio) if args.preview
                 else tts_elevenlabs(sc["text"], audio, api_key, voice))
        dur = duration(audio) + pad
        all_words.append([(w, s + offset, e + offset) for w, s, e in words])
        png = str(tmp / f"s{i}.png")
        render_scene(sc, png)
        clip = str(tmp / f"c{i}.mp4")
        frames = math.ceil(dur * FPS)
        zoom = f"zoompan=z='1+0.06*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}"
        run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", audio,
             "-filter_complex", f"[0:v]scale=1188:2112,{zoom},format=yuv420p[v];[1:a]apad,aresample=44100[a]",
             "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "192k", "-ac", "2", clip])
        clips.append(clip)
        offset += dur

    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    joined = str(tmp / "joined.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", joined])

    ass = tmp / "subs.ass"
    write_ass(all_words, ass)
    run(["ffmpeg", "-y", "-i", joined, "-vf", f"ass={ass}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", str(out)])
    print(f"OK -> {out} ({offset:.1f} s)")


if __name__ == "__main__":
    main()
