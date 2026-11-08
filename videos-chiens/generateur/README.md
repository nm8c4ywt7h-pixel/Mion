# Générateur de vidéo « Patapouf-Ville »

Ce dossier fabrique automatiquement la vidéo :
- une scène 3D low-poly (three.js), rendue image par image dans Chromium (Playwright) ;
- une voix off IA (edge-tts) ;
- une musique et des effets sonores synthétisés ;
- le tout assemblé avec ffmpeg.

## Installation (une fois)
```
npm install three@0.170.0 @fontsource/baloo-2 @fontsource/montserrat
npm install playwright    # (ou utiliser une installation globale)
pip install edge-tts numpy
```

## Générer une langue (ex. `fr`)
1. Modifier `script_fr.json` : la voix, les phrases, les titres, les sous-titres (`*mot*` = mot en jaune),
   les étiquettes des maisons et les noms des bâtiments du vote.
2. Lancer les commandes suivantes :
```
python3 make_audio.py fr                    # voix off + timeline_fr.json
python3 -m http.server 8765 &               # sert scene.html
node render.js fr 30                        # images -> frames_fr/
python3 mix.py fr                           # mixage voix + musique + effets -> mix_fr.wav
ffmpeg -framerate 30 -i frames_fr/%04d.jpg -i mix_fr.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest video_fr.mp4
```
Pour une autre langue, copier `script_fr.json` en `script_es.json`, puis traduire le texte et changer la voix
(ex. `es-ES-AlvaroNeural`).

`tts.py` force le certificat du proxy de l'environnement cloud. En local, supprimer la ligne `certifi.where = …`.

## Version complète « Villa Patitas » (Día 1, espagnol, ≈ 47 s)
Elle utilise la scène `scene2.html` : 14 plans calqués sur le Tag 1 du FC Asche.
```
python3 make_audio.py es
SCENE=scene2.html node render.js es 30
python3 mix.py es
ffmpeg -framerate 30 -i frames_es/%04d.jpg -i mix_es.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest villa_patitas_es.mp4
```
Pour la décliner en français ou dans une autre langue : copier `script_es.json` (phrases, sous-titres et textes
de l'interface dans `ui`), changer la voix, puis relancer les mêmes commandes.

## Version 2 « Pipo, el único perro del pueblo » (espagnol, ≈ 30 s)
Scène `scene3.html`, script `script_es2.json` :
```
python3 make_audio.py es2 && SCENE=scene3.html node render.js es2 30 && python3 mix.py es2
ffmpeg -framerate 30 -i frames_es2/%04d.jpg -i mix_es2.wav -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest pipo_es.mp4
```
