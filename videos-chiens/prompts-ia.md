# Prompts IA pour générer les vidéos

Outils conseillés : **Kling AI**, **Google Veo**, **Sora**, **Runway**, **Hailuo / MiniMax**, **Pika** (vidéo) ·
**Midjourney**, **Flux**, **Ideogram** (images fixes à animer ensuite en « image → vidéo »).
Voix off : **ElevenLabs** ou la voix IA de **CapCut**. Montage : **CapCut**.

> Astuce cohérence : génère d'abord **une image de référence** du personnage (ex. Biscuit),
> puis utilise-la en « image → vidéo » ou « character reference » pour tous les plans.
> Garde toujours la même description du chien, mot pour mot.

## Bloc de style à coller à la fin de chaque prompt

```
vertical 9:16, cinematic, shallow depth of field, soft natural light, photorealistic,
highly detailed fur, emotional, 4k, film grain, gentle slow camera push-in
```

## Fiche personnage (à réutiliser)

```
Biscuit, a fluffy 10-week-old golden retriever puppy, light cream fur, big dark shiny eyes,
small pink nose, one ear slightly folded, wearing a small red collar
```

## Prompts par format

### Histoire émouvante
```
A tiny wet beagle puppy sitting alone on an empty train platform at night, rain falling,
neon reflections on the ground, the puppy looks up at the camera with sad hopeful eyes,
[bloc de style]
```
```
An elderly train station worker kneeling down and gently offering half of his sandwich to a
small beagle puppy, warm station lights, rain in the background, [bloc de style]
```
```
A shivering husky puppy in deep snow at dusk, a little girl in a red coat watching from a warm
lit window in the background, snowflakes falling, [bloc de style]
```

### Chien qui parle (plan fixe, regard caméra)
```
Close-up of a corgi sitting on a kitchen floor staring intensely at the camera with huge eyes,
head slightly tilted, funny serious expression, warm kitchen light, [bloc de style]
```
> Ajoute ensuite le lip-sync (Kling « Lip Sync », Hedra ou CapCut) avec la voix off.

### Avant / Après
```
A tiny great dane puppy sleeping in the palm of a human hand, cozy living room, [bloc de style]
```
```
The same great dane, now huge, awkwardly lying on the same small sofa, legs hanging off,
same cozy living room, funny, [bloc de style]
```

### IA surréaliste
```
A golden retriever puppy dressed as a firefighter with a tiny helmet, sitting proudly on a red
fire truck, [bloc de style]
```
```
A giant 30-meter golden retriever gently walking through the streets of Paris near the Eiffel
Tower, happy people petting its paws, wide shot, [bloc de style]
```
```
A tiny puppy sitting inside a cappuccino cup on a café table, latte art around it, morning light,
[bloc de style]
```

### Héros
```
A Newfoundland dog swimming in a river carrying a small soaked kitten on its back,
dramatic lighting, splashing water, [bloc de style]
```
```
A Saint Bernard dog digging in deep snow on a mountain, rescue team running in the background,
blizzard, dramatic, [bloc de style]
```

## Prompts de mouvement (pour image → vidéo)

- `slow push-in, the puppy blinks and tilts its head`
- `the dog wags its tail and runs toward the camera`
- `snow falling, the puppy shakes its fur`
- `camera orbits slowly around the dog, wind moves the fur`

## Prompt négatif (si l'outil le permet)

```
extra legs, deformed paws, extra tail, blurry, distorted face, text, watermark, cartoon
```
