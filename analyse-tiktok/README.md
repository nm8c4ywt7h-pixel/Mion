# Dossier TikTok « Tier-Rätsel » (allemand)

| Fichier | Contenu |
|---|---|
| `01_ANALYSE.md` | Analyse des 3 comptes : montage, vidéos qui ont percé, estimation des abonnés |
| `02_SKRIPTE_DE.md` | 10 scripts « explication » (60–75 s), inspirés de leurs meilleures vidéos |
| `03_ECHTE_RAETSEL_DE.md` | 10 vraies énigmes animales (25–45 s) avec compte à rebours |
| `04_PROMPTS_IMAGES.md` | Style visuel, fiches personnages (Knödel, Bruno, Lena…), prompts par scène |
| `sous-titres/` | 20 fichiers `.srt` prêts pour CapCut (`erklaer_XX` = explications, `raetsel_XX` = énigmes) |
| `outils/make_srt.py` | Régénère les `.srt` si tu modifies un script : `python3 outils/make_srt.py` |

## Montage dans CapCut (ordre conseillé)
1. **Voix off** : enregistre-toi, ou passe le texte (lignes `>` du script) dans une voix IA allemande (CapCut « Texte en parole », ElevenLabs…).
2. **Images** : génère-les avec `04_PROMPTS_IMAGES.md`, une image toutes les 2–3 s avec un zoom lent.
3. **Sous-titres** : *Texte → Importer des sous-titres* → choisis le `.srt`. Les temps sont **estimés** (~4,8 syllabes/s) : décale le bloc pour le caler sur ta voix, ou ajuste la vitesse de la voix IA. Autre option : « Sous-titres automatiques » de CapCut, puis corrige avec le texte du script.
4. Style des sous-titres : police grasse arrondie, blanc avec contour noir, **mot-clé en jaune**, au tiers inférieur.
5. Ajoute le tampon **AUFLÖSUNG** et le compte à rebours 5…1 avec un bruit de tic-tac.

## Rythme de publication
Alterne une explication et une énigme, 1 à 2 vidéos par jour. Les énigmes apportent des commentaires et des vues, les explications apportent des abonnés.
