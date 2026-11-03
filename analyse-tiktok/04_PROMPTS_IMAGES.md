# Prompts d'images : style constant pour Knödel et Bruno

Les prompts sont **en anglais** (Midjourney, DALL·E, Leonardo, Ideogram et Kling répondent mieux).
**Méthode pour garder les mêmes personnages :**
1. Génère d'abord les **fiches personnages** (section 2) et garde la meilleure image de chacun.
2. Pour chaque scène, ajoute cette image comme **référence de personnage** (Midjourney : `--cref <url> --cw 100` ; Leonardo : « Character Reference » ; DALL·E : joins l'image et écris « same character as in the image »).
3. Ajoute **toujours** le bloc STYLE ci-dessous à la fin du prompt.
4. Format **9:16** (`--ar 9:16`), en laissant de la place en bas pour les sous-titres.

---

## 1. Bloc STYLE (à coller à la fin de chaque prompt)

```
flat 2D vector illustration, soft pastel color palette (mint, peach, lavender, butter yellow), thick rounded dark outlines, simple shapes, subtle grain texture, soft shadows, clean minimal background, cozy German home details, children's educational app style, vertical 9:16, empty space at the bottom third for subtitles, no text
```

Ce style est volontairement **différent des trois comptes** : pas de noir et blanc (instinctdeclic0), pas de 3D réaliste (lacienciadetras.ia), pas de photoréalisme doré (toutsavoiranimal).

---

## 2. Fiches personnages (à générer en premier)

**Knödel (le chat détective)**
```
character sheet of a chubby orange tabby cat named Knödel, round face, big amber eyes, small round brown detective glasses, tiny green scarf, front view, side view, back view, happy, surprised and thinking expressions, white background
```

**Bruno (le chien)**
```
character sheet of a friendly beagle dog named Bruno, floppy brown ears, white muzzle, red collar with a round golden tag, front view, side view, sitting, begging, head tilted, white background
```

**Lena (l'héroïne humaine)**
```
character sheet of a 22-year-old woman named Lena, messy brown bun, oversized mustard sweater, freckles, round face, front view, side view, smiling, sleepy, proud expressions, white background
```

**Famille (Opa Günther, Tante Brigitte, Paul)**
```
character lineup: grumpy grandpa with white mustache and knitted vest (Opa Günther), cheerful aunt with red curly hair and floral dress (Tante Brigitte), 10-year-old boy with a blue cap (Paul), standing side by side, white background
```

**Éléments récurrents (stempel et countdown)**
```
red rubber stamp graphic with blank center, slightly rotated, ink texture, isolated on transparent background
```
```
giant cute question mark mascot with small eyes, pastel yellow, isolated
```
→ Ajoute ensuite le texte « AUFLÖSUNG » et les chiffres du countdown dans CapCut, pas dans le générateur (le texte généré par IA est souvent déformé).

---

## 3. Scènes clés : explications (`02_SKRIPTE_DE.md`)

| Script | Prompts (+ bloc STYLE + référence personnage) |
|---|---|
| 1. Katze allein | `Knödel sitting alone facing a closed front door, hallway, worried big eyes` · `Knödel curled up sleeping on a mustard sweater left on a chair` · `thought bubble with an hourglass above Knödel's head` · `Lena opening the door, Knödel calmly looking away, relieved` |
| 2. Weckt nur dich | `top view of a hallway with four bedroom doors at dawn, Knödel running past three doors` · `Knödel standing on sleeping Lena's belly, tail in her face, 5 AM clock` · `family breakfast table, Opa Günther grumpy dipping a bread roll in coffee, Lena proud` · `sepia flashback: Lena half-asleep filling a cat food bowl at night` |
| 3. Kuscheln | `expensive heated cat bed, empty, with a big red cross` · `Knödel sleeping pressed against Lena in bed, summer heat, fan, thermometer showing 30` · `top view of a group of cats lying in pairs, small hearts between pairs` · `Knödel licking Lena's forehead, gentle` |
| 4. Hund bettelt | `Bruno with his head on a lap under a Sunday dinner table, eyes following a fork` · `Tante Brigitte secretly passing bread under the tablecloth to Bruno` · `cute slot machine icon with a dog bone inside, pastel` · `Bruno lying relaxed in his dog bed while the family eats` |
| 5. Taube | `pigeon walking on a German train platform, motion lines, vertical guide line through its eye` · `close-up of a pigeon's side-facing eye` · `pigeon walking on a small treadmill in a lab` · `view through a train window, trees passing` |
| 6. Name | `Knödel with ears drooping, floating speech bubbles: table, chair, cup, key icons` · `Knödel ears suddenly perked up, surprised` · `cat food bowl, hand petting, vet bag icons in a row` |
| 7. Kopf schief | `Bruno tilting his head, cute, thought bubble with a duck toy, ball and bone` · `pile of dog toys, Bruno choosing one` · `loading bar icon above Bruno's head` |
| 8. Weinen | `Lena crying on the sofa, Bruno coming close, soft scent clouds around her` · `Bruno yawning, contagious yawn icon` · `beagle puppy licking its mother's mouth, warm` · `Bruno resting his head on Lena's knee, comforting` |
| 9. Kopfstoß | `Knödel with a magnifying glass, detective pose` · `Knödel bumping his forehead against Lena's forehead, tiny golden particles` · `Knödel pushing his head against a smartphone in Lena's hand` |
| 10. Test | `Knödel slow-blinking, eyes half closed, soft smile` · `Knödel lying on his back showing belly` · `Knödel sitting outside a bathroom door` · `Knödel kneading a blanket with his paws` · `Knödel sleeping on Lena's clothes` |

---

## 4. Scènes clés : énigmes (`03_ECHTE_RAETSEL_DE.md`)

| Énigme | Prompts (+ bloc STYLE) |
|---|---|
| 1. Drei Herzen | `three cute pulsing hearts floating` · `friendly octopus glowing soft blue, three small hearts visible inside` · `octopus crawling on the sea floor instead of swimming` |
| 2. Wolf, Ziege, Kohl | `top view of a river with a small wooden boat, farmer, wolf, goat and cabbage on the left bank` · `farmer rowing with the goat in the boat` |
| 3. Ei auf dem Dach | `rooster sitting on the very top of a house roof, sky background` · `rooster shrugging, confused` |
| 4. Arche | `cute wooden ark with animal pairs lining up` · `old man with white beard holding a staff, ambiguous` |
| 5. Springen | `three silhouettes: kangaroo, cat, elephant, side by side` · `kangaroo and cat jumping, elephant standing still, smiling` |
| 6. Knödels Mama | `mother cat with three kittens, the third kitten shown as a silhouette with a question mark` · `third kitten revealed as baby Knödel with tiny glasses` |
| 7. Schnecke | `cross-section of a stone well with a meter scale 0 to 10, snail at the bottom` · `snail at the top edge of the well, sunrise` |
| 8. Fingerabdrücke | `fingerprint under a magnifying glass` · `koala holding a eucalyptus branch, close-up on its fingers` |
| 9. Leine | `Bruno wearing a leash, food bowl far away, measuring tapes showing 3 m and 5 m` · `the loose end of the leash dragging on the floor, nothing attached` |
| 10. Delfin | `sleeping dolphin near the surface, one eye open` · `dolphin brain icon, one half grey with zzz, the other half glowing` |

---

## 5. Animer les images (facultatif)

Dans Kling, Runway ou Hailuo, mets l'image en entrée puis un prompt court de mouvement :
```
subtle idle animation, gentle breathing, slow blink, slight camera push-in, 3 seconds, no morphing
```
Sans IA vidéo, ça marche aussi : dans CapCut, applique un zoom lent (Ken Burns) sur chaque image et coupe toutes les 2 à 3 secondes.
