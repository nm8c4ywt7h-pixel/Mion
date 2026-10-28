# Kit de production : vidéo TikTok en espagnol (format hook + structure rapide)

> Je n'ai pas pu voir la vidéo d'origine. Ce kit reprend donc le **format** des vidéos virales de ce type (hook choc, coupes rapides, sous-titres animés, CTA en boucle), avec un **script original en espagnol**.
> Remplace les `[CROCHETS]` par le sujet de ta vidéo (envoie-le-moi et je remplis tout).

---

## 1. Structure (30 s, environ 12 à 15 coupes)

| Temps | Bloc | Rôle | Durée des plans |
|---|---|---|---|
| 0,0–2,0 s | **HOOK** | Arrêter le scroll : phrase choc + visuel fort | 1 plan, zoom avant immédiat |
| 2,0–6,0 s | **TENSION** | Le problème que tout le monde a | 2 plans de 2 s |
| 6,0–20,0 s | **RÉVÉLATION** | 3 points / étapes, un par plan | 6 à 7 plans de 2 s |
| 20,0–26,0 s | **PREUVE** | Résultat, avant/après, chiffre | 2 à 3 plans |
| 26,0–30,0 s | **CTA + BOUCLE** | Appel à l'action + phrase qui renvoie au hook | 2 plans |

**Règle de rythme :** aucun plan ne dépasse 2,5 s, une coupe ou un zoom au moins toutes les 2 s, et l'alternance plan normal / plan zoomé (110 %) donne l'effet « jump cut ».

---

## 2. Script voix off en espagnol (à adapter)

**HOOK (0–2 s)**
> «Nadie te dice esto sobre [SUJET]… y por eso sigues fallando.»

*Variantes du hook à tester :*
- «Si haces [ACTION COURANTE], para ahora mismo.»
- «Esto es lo que [NOM] hace diferente… y nadie lo ve.»
- «Me costó [X] años entender esto. A ti te va a costar 30 segundos.»

**TENSION (2–6 s)**
> «Todo el mundo cree que [IDÉE REÇUE]. Pero la verdad es otra.»

**RÉVÉLATION (6–20 s)**
> «Primero: [POINT 1].»
> «Segundo: [POINT 2]. Y aquí es donde casi todos se equivocan.»
> «Tercero, y el más importante: [POINT 3].»

**PREUVE (20–26 s)**
> «Mira la diferencia.» (avant/après à l'écran)
> «[RÉSULTAT CHIFFRÉ] en solo [DURÉE].»

**CTA + BOUCLE (26–30 s)**
> «Guárdalo para no olvidarlo y sígueme para la parte 2…»
> «…porque lo que nadie te dice sobre [SUJET] es…» (on recoupe sur le hook pour créer la boucle)

**Règle des noms :** on garde toujours les mêmes noms. Si un nom a une forme espagnole, on utilise cette forme (ex. Pierre → Pedro, Jean → Juan, Marie → María, Louis → Luis). Sinon, on le garde tel quel. Même chose pour les mots-clés (ex. « caca » reste « caca » en espagnol, ou « popó » en Amérique latine).

**Conseils pour la voix :** espagnol neutre (ou castillan selon ta cible), débit rapide d'environ 170 mots/min, énergie forte sur le premier mot du hook, pas de silence de plus de 0,3 s (coupe les respirations au montage).

---

## 3. Tenue et décor (pour te démarquer)

Garde ce qui marche (cadrage serré, regard caméra, lumière de face) et change l'ambiance :

| Option | Tenue | Décor | Effet |
|---|---|---|---|
| **A : Urbain** | Hoodie oversize couleur unie (beige/olive), casquette | Rue / rooftop au golden hour | Authentique, « street » |
| **B : Clean premium** | Chemise lin blanche ou col roulé noir | Bureau minimaliste, plante, lampe chaude en fond | Expert, crédible |
| **C : En mouvement** | Veste technique / sportswear | Voiture (siège passager), marche en ville | Dynamique, rythme naturel |

**Une couleur signature** (même teinte dans la tenue et dans les sous-titres) aide à la reconnaissance d'une vidéo à l'autre.

---

## 4. Plan de tournage (shot list)

| # | Plan | Cadrage | Note |
|---|---|---|---|
| 01 | Hook face caméra | Gros plan visage | Commencer en parlant, pas de « hola » |
| 02 | Réaction / geste « non » | Plan poitrine | |
| 03 | B-roll problème | Détail (mains, écran, objet) | |
| 04 | Point 1 face caméra | Plan poitrine | |
| 05 | B-roll point 1 | Détail | |
| 06 | Point 2 face caméra | Gros plan | Se pencher vers la caméra |
| 07 | B-roll point 2 | Détail | |
| 08 | Point 3 face caméra | Gros plan | Le plus énergique |
| 09 | B-roll point 3 | Large | |
| 10 | Avant | Même cadre que 11 | |
| 11 | Après | Même cadre que 10 | |
| 12 | CTA face caméra | Gros plan | Pointer vers le bas/haut |

Filme en **vertical 1080×1920, 30 ou 60 i/s**, et prends 2 prises par plan.

---

## 5. Montage (même rythme, mêmes types d'effets)

**Effets à reproduire :**
- **Zoom punch-in** de 110 à 115 % sur un plan sur deux (jump cut). Le script `montage.sh` le fait automatiquement.
- **Sous-titres mot par mot** : gros, gras, centrés, contour noir, mot clé en couleur signature.
- **Whoosh** sur chaque transition de bloc (hook → tension → révélation…).
- **Pop / clic** sur chaque apparition de chiffre ou de mot clé.
- **Musique** tendance en fond, à environ -20 dB sous la voix (ducking automatique dans le script).
- **Freeze ou flash blanc** de 2 images sur la révélation du point 3.
- **Fin coupée net** au milieu de la phrase de boucle.

**Dans CapCut :** Auto-captions (langue : Español), puis style « Bold » avec contour, puis Animation « Pop ». Pour le zoom, utilise Keyframes (100 % au début du plan, 112 % à la 1re image du plan suivant). Le whoosh est dans Sons → « whoosh ».

**Avec le script fourni :** voir `montage.sh`.
