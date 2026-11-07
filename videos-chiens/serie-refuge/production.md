# Production — fabriquer les épisodes

## Le secret de la série : un décor et des personnages qui ne changent JAMAIS
La série de référence fonctionne parce que tout reste parfaitement identique d'un épisode à l'autre.
On a 2 façons d'y arriver :

### Option A (recommandée pour démarrer) : images IA cohérentes + animation légère
1. **Créer la « bible visuelle » une seule fois** : 1 image du décor, 1 image de chaque personnage
   (avec les prompts ci-dessous). Garde les meilleures : ce sont tes **images de référence**.
2. **Chaque plan** : on génère une nouvelle image *à partir des références*. Utilise un outil qui accepte des images
   de référence ou l'édition d'image (ChatGPT Images, Gemini, Midjourney avec référence de personnage,
   Flux Kontext, Ideogram…). Ensuite, « ajoute 30 bénévoles en gilet jaune dans la cour », etc.
3. **Animer** chaque image en clip de 3–5 s avec **Kling, Hailuo, Veo ou Runway** (image → vidéo),
   avec un mouvement simple : `slow camera push-in, light rain falling, the dog blinks`.
   Pour les plans « fiche personnage » ou « compteur », une image fixe avec un zoom dans CapCut suffit.

### Option B (le plus proche de l'original, le plus solide sur la durée) : une scène 3D
- Construire le refuge **une seule fois** dans **Blender** (gratuit), avec des modèles 3D gratuits en style low-poly
  (packs CC0 de Kenney ou Quaternius : chiens, clôtures, maisons, arbres, pluie).
- Les bénévoles = **un seul personnage dupliqué** N fois (Blender le fait automatiquement), donc le compteur
  peut correspondre visuellement au vrai chiffre.
- Chaque épisode : on modifie la scène (nouveau bâtiment, plus de monde), on fait 10–20 rendus de caméra, et on monte.
- Plus long à mettre en place (quelques jours), mais ensuite chaque épisode va plus vite et le décor ne bouge plus jamais.

> Conseil : commence avec l'option A pour les jours 1 à 3. Si la série prend (comme pour la référence),
> passe à l'option B ou fais-toi aider par un graphiste 3D.

## Prompts de la bible visuelle

**Style (à coller à la fin de chaque prompt) :**
```
stylized 3D cartoon render, toy-like low-poly look, soft rounded shapes, characters with big round
white eyes and tiny pupils, rainy evening, muted blue-grey and green palette with warm yellow and
orange accents, soft volumetric light, vertical 9:16, clean composition, no text
```

**Le décor (refuge, jour 1) :**
```
an old run-down countryside dog shelter: muddy dirt courtyard with puddles, one small crooked wooden
dog kennel, bent wire fence, an old white caravan used as an office with a hand-painted wooden sign,
a few pine trees, light rain, empty and a bit sad but cute, wide shot, [style]
```

**Le fondateur :**
```
a friendly cartoon man in a bright yellow raincoat, rubber boots, thick knitted scarf, a whistle around
his neck, holding a clipboard, standing in a muddy courtyard, full body, [style]
```

**Papi Gaston :**
```
a very old sleepy basset hound with a white muzzle and extremely long ears touching the ground,
eyes half closed, sitting in front of a wooden kennel, [style]
```

**Brioche :**
```
a very round chubby pug with a guilty face, crumbs around its mouth, next to a caravan with its door
missing, [style]
```

**Choupette :**
```
a tiny chihuahua wearing a pink knitted sweater, growling bravely with a fierce face, [style]
```

**Le chiot n° 7 :**
```
a small scruffy mixed-breed puppy, one ear up and one ear down, wearing a mismatched striped sock as a
collar, head tilted, huge curious eyes, [style]
```

**Les bénévoles (la foule qui grandit) :**
```
the same muddy dog shelter courtyard, now filled with [30 / hundreds of / thousands of] tiny cartoon
volunteers wearing yellow high-visibility vests, cheering, some holding dog toys, [style]
```

**La Gamelle (la caisse) :**
```
a giant shiny metal dog bowl on a wooden bench, overflowing with gold coins and banknotes, rain,
[style]
```

**La rivale :**
```
an elegant snobbish lady with a tall hairdo surrounded by perfectly groomed white poodles with pom-pom
haircuts, in front of a luxurious pink kennel club, [style]
```

## La voix off
- **ElevenLabs** (ou la voix IA de CapCut), en français : une voix masculine ou féminine **calme, posée,
  pince-sans-rire**. Toujours la même voix : elle fait partie de l'identité de la série.
- **Une phrase = 2 secondes environ.** Phrases courtes, pas de « euh ». Pas de silence de plus de 0,3 s.
- Ton : sérieux, comme un documentaire, même quand c'est absurde. C'est ce décalage qui fait rire.

## Les sous-titres (CapCut)
- Sous-titres automatiques, puis découpage en **2–3 mots maximum** par ligne.
- **MAJUSCULES**, police très grasse (Montserrat Black, Anton ou une police « bold » de CapCut),
  blanc avec un **contour noir épais**, placés aux ~75 % de la hauteur de l'écran.
- **Mots-clés colorés** : vert (#3DDC4A) pour le positif (BÉNÉVOLE, COUR, GAMELLE, TOOOR/VICTOIRE),
  rouge (#E8322E) pour le négatif (ZÉRO, VIDE, PERDU).
- Animation : apparition « pop » mot par mot.

## Les éléments graphiques à créer une fois (Canva ou CapCut)
- Badge **« JOUR X »** : rectangle vert arrondi, contour blanc, texte blanc gras, légère ombre
- Étiquette **« 1 ABONNÉ = 1 BÉNÉVOLE »**
- **Fiche personnage** : carte blanche avec numéro, nom, rôle et défaut
- **Compteur** « BÉNÉVOLES » + gros chiffre (vert ou rouge)
- Compteur **« GAMELLE »** en €
- **Cartes de vote** A / B / C (la dernière, verte : « ? AUTRE CHOSE »)
- Badge **« DÉCISION N° X »**
- Carte **« BÉNÉVOLE OG · Carte n° 001 »**
- **Captures réelles** : ton profil TikTok (abonnés entourés) et les commentaires sélectionnés

## Montage (CapCut), étape par étape
1. Importer la voix off, la placer sur la piste principale.
2. Poser un plan (image ou clip) **tous les 1,5 à 2,5 s**, calé sur chaque phrase.
3. Zoom lent (100 % → 108 %) sur toutes les images fixes.
4. Ajouter les badges et les étiquettes au moment où le mot est prononcé.
5. Sous-titres (réglages ci-dessus).
6. Son : bruit de pluie léger en fond, petits « pop » sur l'apparition des badges, « ka-ching » sur la Gamelle.
   Musique très discrète ou aucune.
7. Exporter en 1080×1920, 30 ips.
8. Vérifier : **quelque chose change à l'écran au moins toutes les 2 secondes** ?

## Le suivi des chiffres (tableau à tenir)

| Jour | Date / heure | Abonnés totaux | Nouveaux bénévoles (= total − référence) | Gamelle avant | Dépense (vote) | Gamelle après | Top commentaire | Pseudos utilisés |
|---|---|---|---|---|---|---|---|---|
| 1 | | (référence) | 0 | 500 € | — | 500 € | | |
| 2 | | | | | | | | |
