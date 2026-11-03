"""Génère un fichier .srt par vidéo à partir des scripts Markdown.

Usage : python3 make_srt.py
Lit 02_SKRIPTE_DE.md et 03_ECHTE_RAETSEL_DE.md (lignes de voix off commençant par "> ")
et écrit les sous-titres dans ../sous-titres/.
Les temps sont estimés (vitesse de parole ~4,8 syllabes/s) : dans CapCut, importe le .srt,
puis cale le début sur ta voix off ou utilise « Sous-titres automatiques » et colle le texte.
"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "sous-titres"
SOURCES = [("02_SKRIPTE_DE.md", "erklaer"), ("03_ECHTE_RAETSEL_DE.md", "raetsel")]
SYL_PER_SEC = 4.8
WORDS_PER_CUE = 3
EMOJI = re.compile(r"[\U0001F000-\U0001FFFF☀-➿←-⇿⬀-⯿️]")


def syllables(word):
    return max(1, len(re.findall(r"[aeiouäöüy]+", word.lower())))


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def slug(title):
    t = title.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        t = t.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:50]


def sections(text):
    cur = None
    for line in text.splitlines():
        h = re.match(r"^## (Skript|Rätsel) (\d+): (.+)", line)
        if h:
            if cur:
                yield cur
            cur = {"n": int(h.group(2)), "title": h.group(3), "paras": []}
        elif cur and line.startswith(">"):
            p = EMOJI.sub("", line[1:]).strip()
            if p:
                cur["paras"].append(p)
    if cur:
        yield cur


def cues(paras):
    t, out = 0.2, []
    for para in paras:
        if para.lower().startswith("fünf."):  # compte à rebours : un chiffre par seconde
            for w in para.split():
                out.append((t, t + 1.0, w))
                t += 1.0
            t += 0.4
            continue
        # découpe en phrases, puis chaque phrase en morceaux équilibrés de <= 3 mots
        for sent in re.findall(r"[^.!?…:]+[.!?…:]*", para):
            words = sent.split()
            if not words:
                continue
            n = -(-len(words) // WORDS_PER_CUE)
            bounds = [round(k * len(words) / n) for k in range(n + 1)]
            for a, b in zip(bounds, bounds[1:]):
                chunk = words[a:b]
                dur = max(sum(syllables(w) for w in chunk) / SYL_PER_SEC, 0.45)
                out.append((t, t + dur, " ".join(chunk)))
                t += dur
            t += 0.25
        t += 0.4
    return out


def main():
    OUT.mkdir(exist_ok=True)
    for fname, prefix in SOURCES:
        for s in sections((BASE / fname).read_text(encoding="utf-8")):
            cs = cues(s["paras"])
            path = OUT / f"{prefix}_{s['n']:02}_{slug(s['title'])}.srt"
            with path.open("w", encoding="utf-8") as f:
                for k, (a, b, txt) in enumerate(cs, 1):
                    f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
            print(f"{path.name}: {len(cs)} sous-titres, ~{cs[-1][1]:.0f} s")


if __name__ == "__main__":
    main()
