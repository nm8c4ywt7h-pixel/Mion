# Dossier TikTok « Acertijo animal » (espagnol) / « Tier-Rätsel » (allemand)

| Fichier | Contenu |
|---|---|
| **`videos/es/`** | **Les 20 vidéos finales en espagnol** (MP4 1080×1920 + `.srt` exact). `explicacion_XX` = explications, `acertijo_XX` = énigmes |
| `05_GUIONES_ES.md` | 10 scripts « explication » en espagnol (version utilisée pour les vidéos) |
| `06_ACERTIJOS_ES.md` | 10 énigmes en espagnol |
| `outils/render_videos.py` | Fabrique les vidéos : `python3 outils/render_videos.py` (espagnol) ou `--lang de` (allemand) |
| `01_ANALYSE.md` | Analyse des 3 comptes : montage, vidéos qui ont percé, estimation des abonnés |
| `02_SKRIPTE_DE.md` | (version allemande) 10 scripts « explication » (60–75 s), inspirés de leurs meilleures vidéos |
| `03_ECHTE_RAETSEL_DE.md` | (version allemande) 10 vraies énigmes animales (25–45 s) avec compte à rebours |
| `04_PROMPTS_IMAGES.md` | Style visuel, fiches personnages (Knödel, Bruno, Lena…), prompts par scène |
| `sous-titres/` | (version allemande, temps estimés) 20 fichiers `.srt` (`erklaer_XX` = explications, `raetsel_XX` = énigmes) |
| `outils/make_srt.py` | Régénère les `.srt` si tu modifies un script : `python3 outils/make_srt.py` |

## Montage dans CapCut (ordre conseillé)
1. **Voix off** : enregistre-toi, ou passe le texte (lignes `>` du script) dans une voix IA allemande (CapCut « Texte en parole », ElevenLabs…).
2. **Images** : génère-les avec `04_PROMPTS_IMAGES.md`, une image toutes les 2–3 s avec un zoom lent.
3. **Sous-titres** : *Texte → Importer des sous-titres* → choisis le `.srt`. Les temps sont **estimés** (~4,8 syllabes/s) : décale le bloc pour le caler sur ta voix, ou ajuste la vitesse de la voix IA. Autre option : « Sous-titres automatiques » de CapCut, puis corrige avec le texte du script.
4. Style des sous-titres : police grasse arrondie, blanc avec contour noir, **mot-clé en jaune**, au tiers inférieur.
5. Ajoute le tampon **AUFLÖSUNG** et le compte à rebours 5…1 avec un bruit de tic-tac.

## Rythme de publication
Alterne une explication et une énigme, 1 à 2 vidéos par jour. Les énigmes apportent des commentaires et des vues, les explications apportent des abonnés.

## Vidéos espagnoles générées
- Voix : `es-MX-JorgeNeural` (espagnol neutre d'Amérique latine). Pour l'Espagne, remplace par `es-ES-AlvaroNeural` dans `outils/render_videos.py`.
- Les MP4 ne sont pas dans git (trop lourds) : relance `python3 outils/render_videos.py` pour les recréer.
- Il n'y a pas de musique : ajoute un son tendance directement dans TikTok, à faible volume (10–15 %). Ça aide la portée.
- Visuels : émojis animés sur fond pastel. Pour une version plus haut de gamme, remplace-les par des images générées avec `04_PROMPTS_IMAGES.md`, en renommant Knödel en Churro et Lena en Lucía.
