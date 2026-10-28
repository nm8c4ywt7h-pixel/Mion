#!/usr/bin/env python3
"""Génère une vidéo TikTok verticale (1080x1920) à partir d'un script JSON.

Voix : ElevenLabs (text-to-speech avec timestamps -> sous-titres mot à mot).
Visuels : Pépito Saucisse, teckel dessiné avec Pillow, + titres animés.

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

def gradient(c1, c2):
    a = Image.new("RGB", (W, H), c1)
    b = Image.new("RGB", (W, H), c2)
    mask = Image.linear_gradient("L").resize((W, H))
    return Image.composite(b, a, mask)


def draw_pepito(img, pose, props):
    """Teckel cartoon. pose : normal | guilty | sideeye | proud."""
    d = ImageDraw.Draw(img)
    W = img.width  # calque plus large que l'écran, réduit ensuite
    brown, dark, belly = (176, 98, 40), (110, 55, 20), (214, 150, 90)
    cx, cy = W // 2 + 60, 1180
    ol = dict(outline=(40, 20, 5), width=8)

    if props == "feathers":
        rnd = random.Random(7)
        for _ in range(28):
            x, y = rnd.randint(60, W - 60), rnd.randint(1330, 1560)
            r = rnd.randint(18, 40)
            d.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(250, 250, 245),
                      outline=(200, 200, 200), width=3)
        d.rounded_rectangle([700, 1330, 960, 1450], 30, fill=(230, 70, 90), **ol)
        d.line([720, 1350, 940, 1440], fill=(150, 30, 50), width=10)

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


def fit_font(text, max_w, size):
    while size > 30:
        f = ImageFont.truetype(FONT_BOLD, size)
        if f.getbbox(text)[2] <= max_w:
            return f
        size -= 4
    return ImageFont.truetype(FONT_BOLD, size)


def render_scene(scene, idx, total, out_png):
    img = gradient(*scene["bg"])
    # ombre au sol
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).ellipse([120, 1250, 960, 1330], fill=90)
    img.paste((0, 0, 0), mask=shadow.filter(ImageFilter.GaussianBlur(25)))
    layer = Image.new("RGBA", (1400, H), (0, 0, 0, 0))
    draw_pepito(layer, scene.get("pose", "normal"), scene.get("props"))
    k = 0.76
    layer = layer.resize((int(1400 * k), int(H * k)), Image.LANCZOS)
    img.paste(layer, ((W - layer.width) // 2, int(1250 * (1 - k))), layer)

    d = ImageDraw.Draw(img)
    f = fit_font(scene["headline"], W - 120, 120)
    tw = f.getbbox(scene["headline"])[2]
    d.text(((W - tw) // 2, 330), scene["headline"], font=f, fill="white",
           stroke_width=10, stroke_fill="black")
    small = ImageFont.truetype(FONT_BOLD, 44)
    d.text((60, 200), "@pepito.saucisse", font=small, fill="white",
           stroke_width=4, stroke_fill="black")
    # barre de progression
    d.rounded_rectangle([60, 140, W - 60, 156], 8, fill=(255, 255, 255, 90))
    d.rounded_rectangle([60, 140, 60 + (W - 120) * (idx + 1) // total, 156], 8, fill="white")
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
Style: Cap,DejaVu Sans,86,&H00FFFFFF,&H0000E5FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,3,2,70,70,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    # blocs de 3 mots (jamais à cheval sur deux scènes), mot courant en jaune
    for scene_words in words:
        for i in range(0, len(scene_words), 3):
            chunk = scene_words[i:i + 3]
            end_chunk = (scene_words[i + 3][1] if i + 3 < len(scene_words)
                         else chunk[-1][2] + 0.2)
            for j, (w, s, e) in enumerate(chunk):
                e2 = chunk[j + 1][1] if j + 1 < len(chunk) else end_chunk
                txt = " ".join(
                    ("{\\c&H00E5FF&\\fscx110\\fscy110}" + ww.upper() + "{\\r}") if k == j else ww.upper()
                    for k, (ww, _, _) in enumerate(chunk))
                lines.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e2)},Cap,,0,0,0,,{txt}")
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
        print(f"[{i + 1}/{len(scenes)}] {sc['headline']}")
        audio = str(tmp / f"a{i}.mp3")
        words = (silent_preview(sc["text"], audio) if args.preview
                 else tts_elevenlabs(sc["text"], audio, api_key, voice))
        dur = duration(audio) + pad
        all_words.append([(w, s + offset, e + offset) for w, s, e in words])
        png = str(tmp / f"s{i}.png")
        render_scene(sc, i, len(scenes), png)
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
