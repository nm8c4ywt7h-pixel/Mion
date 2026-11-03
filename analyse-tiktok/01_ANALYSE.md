# Analyse de 3 comptes TikTok (données du 03/11/2026)

> ⚠️ **Deux remarques avant tout**
> 1. Seuls **3 liens** ont été fournis (pas 4).
> 2. **Aucun des 3 comptes ne fait des énigmes.** Ce sont des comptes de faits et de « psychologie » animale (chats, chiens). J'ai donc analysé ce qu'ils font réellement, puis j'ai écrit les scripts allemands avec un **hook de type devinette** (« Rate mal… », une question posée avant la révélation), ce qui reste au plus près du format « énigme ».

Méthode : j'ai récupéré toutes les vidéos publiques (vues, likes, partages, enregistrements), téléchargé les 13 meilleures, transcrit la voix off (Whisper) et extrait des images pour analyser le montage.

---

## 1. Vue d'ensemble

| Compte | Langue | Abonnés | Vidéos | Vues médianes | Top vidéo |
|---|---|---|---|---|---|
| @instinctdeclic0 | FR | 48,6 k | 99 | ~101 k | 3,7 M |
| @lacienciadetras.ia | ES | 38,4 k | **19** (compte créé ~21/10/2026) | ~41 k | 2,6 M |
| @toutsavoiranimal | FR | 32,3 k | 158 | ~6 k | 664 k |

**Le plus impressionnant : @lacienciadetras.ia** a gagné 38 k abonnés en **2 semaines** avec 19 vidéos. Presque tout vient de la vidéo du pigeon (2,6 M vues), puis de l'enchaînement chat / chien.

---

## 2. Type de montage

### @instinctdeclic0, le plus fort en vues
Deux formats :
- **A. « Psychologie : ce que ressent ton chat… »** (vidéos à 3,7 M et 2,6 M)
  Dessin animé IA en **noir et blanc**, chat aux grands yeux inquiets, **cerveau qui brille** sur la tête, bulles de pensée (sablier, cœur brisé, famille). Un plan toutes les ~3 s (≈23 coupes en 77 s). Sous-titre blanc, un ou deux mots au centre. Voix off calme et grave, ton émotionnel et culpabilisant. Musique triste au piano.
- **B. « Si ton chat/chien fait X, ce n'est PAS pour Y »** (2,2 M, 1,5 M, 1,4 M, 1,2 M), son format actuel
  Illustration **vectorielle plate en couleurs** (style app éducative), un **personnage humain récurrent** (une fille) et une famille aux noms ridicules (« Kaka », « Mamichoufleur », « Harry Covert »). Sous-titres mot par mot, mot-clé en jaune. Structure **mini-histoire, fausse croyance, étude scientifique, chute vexante** (« tu es juste le seul idiot qui se lève pour lui »).
  Formule du hook : *« Tu savais que si ton [animal] fait [X], ce n'est pas du tout pour [Y évident], mais pour une raison bien plus troublante que tu ne l'imagines. »*

### @lacienciadetras.ia, la meilleure croissance d'abonnés
- Animation **3D/2D propre, cartoon réaliste** (pigeon sur une place pavée, ralenti, ligne verticale pour montrer que la tête reste fixe). 60 fps, **très peu de coupes** (≈4 en 80 s) : on reste sur la démonstration.
- Sous-titres blancs fins en haut de l'écran.
- Script **ultra-rythmé, phrases de 3 à 6 mots**, une vraie étude citée avec des chiffres précis (« 94 sur 100 », « 7 chiens sur 40 »), un retour vers le spectateur (« et toi aussi, tu fais pareil »), puis une chute en une phrase.
- **CTA identique à chaque vidéo** : *« Suis-moi pour ne pas rater le prochain fait, avec la science derrière »*. C'est une signature de marque qui pousse à l'abonnement.

### @toutsavoiranimal
- Image IA **photoréaliste chaude** (Maine Coon, lumière dorée, particules de phéromones) **ou** animation plate très colorée (format « Fais le test », barre de progression des « signes d'amour »).
- Narration **à la première personne, par le chat** (« Salut, moi c'est la chatte et je vais tout t'expliquer »).
- Sous-titres en majuscules, mot-clé en jaune. CTA agressif (« abonne-toi et partage un max pour nous aider, nous les chats »).
- Taux de **partage le plus élevé des trois** (3,7 % à 4,6 %), mais une base faible (vues médianes ~6 k).

---

## 3. Vidéos qui ont le plus percé et estimation des abonnés

TikTok ne publie pas les abonnés gagnés par vidéo. Je les estime avec trois indices : **partages + enregistrements** (signal le plus corrélé au follow), **contexte** (première vidéo virale d'un petit compte = gros pic d'abonnés) et **format série** (le spectateur s'abonne pour la suite).

| # | Vidéo | Vues | Partages | Pourquoi elle a rapporté des abonnés |
|---|---|---|---|---|
| 1 | instinctdeclic0, chat seul à la maison | 3,7 M | 74,8 k (2,0 %) | Le plus gros volume absolu ; a lancé la série « Psychologie : » |
| 2 | lacienciadetras.ia, tête du pigeon | 2,6 M | 38,1 k | **Première vidéo virale d'un compte neuf**, ≈ l'essentiel des 38 k abonnés |
| 3 | instinctdeclic0, chat seul pendant les vacances | 2,6 M | 35,5 k | Suite directe du n° 1 (effet série) |
| 4 | instinctdeclic0, ton chat te réveille la nuit | 2,2 M | 27,8 k | Lancement du format B (histoire + chute vexante) |
| 5 | instinctdeclic0, chien qui mendie à table | 1,5 M | 25,8 k | Conseil utile, donc gros taux d'enregistrement |
| 6 | instinctdeclic0, chat qui dort collé à toi | 1,4 M | 12,1 k | Format B |
| 7 | lacienciadetras.ia, ton chat connaît son nom | 815 k | 12,3 k | **18 % de likes/vue**, le record |
| 8 | toutsavoiranimal, coups de tête du chat | 664 k | 24,7 k (3,7 %) | Partagé à la personne qui reçoit les coups de tête |
| 9 | lacienciadetras.ia, ton chien penche la tête | 583 k | 6 k | Étude réelle et chiffrée |
| 10 | lacienciadetras.ia, ton chien te lèche quand tu pleures | 562 k | 7,3 k | Émotion + science |
| 11 | toutsavoiranimal, « Ton chat t'aime-t-il ? Fais le test » | 500 k | 6,7 k | **Format quiz**, le plus proche d'une énigme |
| 12 | lacienciadetras.ia, ton chien sent combien de temps tu es parti | 481 k | 8,6 k (1,8 %) | Fort taux de partage |

**Vidéos écartées volontairement :**
- « Ce que ton chat ressent dans ses derniers moments » (1,6 M) : la science est inventée (« son cerveau libère de l'ocytocine ») et le ton exploite le deuil.
- « Les chats savent quand vous avez des moments intimes » (400 k) : contenu faux (le chat « s'inquiète que vous n'ayez pas de bébé »). Le risque de signalement et de crédibilité est trop élevé.

---

## 4. Ce qui marche (les patterns communs)

1. **Hook = contradiction d'une croyance** : « Ce n'est PAS pour X ». Le spectateur reste pour connaître la vraie raison.
2. **« Ton chat / ton chien »** : on parle directement au propriétaire, dont c'est l'animal.
3. **Une étude réelle avec un chiffre**, qui rend le contenu crédible et partageable.
4. **Retour vers le spectateur** (« et toi aussi… », « tu n'es pas si spécial »).
5. **Chute courte et mémorable**, souvent drôle ou vexante.
6. **Durée 60–80 s**, voix off, sous-titres mot par mot.
7. **CTA fixe en signature**, qui transforme les vues en abonnés.

---

## 5. Comment se démarquer de leurs vidéos (pour l'allemand)

J'ai **réécrit tous les scripts avec mes propres mots**. Les faits scientifiques n'appartiennent à personne, mais le texte, les personnages, les dessins et la voix leur appartiennent. Voici ce qui a été changé et ce qu'il faut respecter au montage :

- **Nouveaux personnages et nouvelles histoires.** Une famille allemande récurrente (Lena, Opa Günther, Tante Brigitte, le chat « Knödel », le chien « Bruno »), à la place des familles d'instinctdeclic0.
- **Structure différente.** Chaque script commence par une **devinette** (« Rate mal… ») avec une pause de 1 s et un appel à commenter **avant** la réponse. Ce format n'existe chez aucun des trois.
- **Ne jamais réutiliser** leurs images, leur voix ou leur musique (TikTok détecte les doublons et réduit leur portée), **ni retourner ou recadrer** leurs vidéos.
- **Un style visuel propre et constant**, par exemple : animation flat **pastel** avec un **chat orange récurrent « Knödel » qui porte des lunettes de détective** (concept « Tier-Rätsel »), **un point d'interrogation géant** à l'écran pendant la devinette, puis un **« AUFLÖSUNG »** (solution) en tampon rouge.
- **Signature propre** au lieu de leur CTA : *« Folg mir für das nächste Tier-Rätsel. »*

Les 10 scripts sont dans [`02_SKRIPTE_DE.md`](02_SKRIPTE_DE.md).
