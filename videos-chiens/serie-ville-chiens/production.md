# Production — Patapouf-Ville

## La méthode
La ville doit rester **exactement la même** d'un épisode à l'autre ; seuls les nouveaux bâtiments apparaissent.
- **Option A (pour démarrer vite)** : générer une image de référence de la ville vue du dessus, puis, à chaque épisode,
  **éditer cette même image** (« ajoute une niche en forme d'os sur le terrain vide en bas à gauche ») avec un outil
  d'édition d'image IA (ChatGPT Images, Gemini, Flux Kontext…). Ensuite, animation légère avec Kling, Hailuo ou Runway,
  ou simple zoom dans CapCut.
- **Option B (le plus proche de la référence)** : une ville low-poly dans **Blender**, avec des modèles 3D gratuits
  (packs CC0 de Kenney « City Kit » et Quaternius pour les animaux). On ajoute les maisons au fur et à mesure et on
  anime l'apparition (échelle 0 → 110 % → 100 %).
- Voix off, sous-titres et montage : comme dans [`../serie-refuge/production.md`](../serie-refuge/production.md),
  mais avec **la palette de couleurs ci-dessous**.

**Style (à coller à la fin de chaque prompt) :**
```
bright low-poly 3D render, simple toy-like shapes, sunny day, clear blue sky, vivid green grass,
dark grey roads in a grid, small rounded pine trees, soft shadows, cheerful and cute, vertical 9:16,
no text
```

## Prompts
**La ville vide (vue du dessus) :**
```
top-down isometric view of a small empty town: a grid of dark roads, empty green and sand-colored
plots, small pine trees, rows of small empty dog kennels, no people, no animals, [style]
```
**Le maire, triste :**
```
a cute low-poly cartoon mayor with a big round head, rosy cheeks, a yellow hard hat with a small dog
bone on top, black suit, red tie, green mayor sash, holding an empty dog leash, sad face, standing on
an empty road, [style]
```
**Le maire, heureux, qui pointe la caméra :**
```
the same mayor smiling widely and pointing his finger directly at the camera, close-up, [style]
```
**La meute de chiots qui arrive :**
```
a crowd of tiny cute low-poly puppies of many breeds running happily down the main street of a small
town, top-down angle, [style]
```
**Les silhouettes mystère** : à faire dans CapCut ou Canva. Une forme noire (chien géant, tour) avec un contour
blanc en pointillés.
**Une maison personnalisée :**
```
a small low-poly dog house shaped like a giant [bone / tennis ball / pink castle with glitter / rocket],
on a green plot next to a road, a [golden retriever] puppy peeking out of the door, [style]
```
**Les bâtiments à voter :**
```
a low-poly dog park with a slide, tunnels and a fountain shaped like a bone, top-down view, [style]
```
```
a small low-poly veterinary clinic with a paw-print cross sign on the roof, [style]
```
```
a small low-poly bakery with a giant dog biscuit on the roof, [style]
```

## Les textes (même logique que la référence, avec nos couleurs)
- **Titre en haut** : une petite ligne blanche, puis une **grande ligne en majuscules jaune (#FFC928)** avec un contour noir.
  Police très grasse et arrondie (Montserrat Black, Poppins ExtraBold ou Luckiest Guy).
- **Sous-titre en bas** : 2–3 mots en blanc avec un contour noir, **mots-clés en jaune**.
- **Étiquette de maison** : pastille blanche arrondie, texte noir « 🐶 Biscuit · @pseudo ».
- **Lettres de vote** : grosses lettres A / B / C blanches avec un contour noir, posées sur les bâtiments.
- **Barre « RÉSULTAT DANS 2 JOURS »** : barre jaune qui se remplit.
- **Bouton final** : pastille rouge « S'ABONNER », qui devient grise « ABONNÉ ✓ », puis confettis.

## Son
Voix off joyeuse et énergique (ElevenLabs, ou la voix IA de CapCut), une phrase toutes les 1,5–2 s.
Petits « pop » à chaque apparition, « tadaa » sur les révélations, aboiements de chiots en fond, musique légère et joyeuse.

## Tableau de suivi

| Épisode | Date | Abonnés totaux | Nouveaux (= chiots en ville) | Vote gagnant | Maisons construites (nom · race · @pseudo · envie) | Prochain palier |
|---|---|---|---|---|---|---|
| 1 | | (référence) | 0 | — | — | +1 000 |
