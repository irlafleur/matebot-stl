# MateBot – Guide d'assemblage de la main à tendons (v0)

> ⚠️ **Version v0, NON TESTÉE.** Aucune pièce de cette variante n'a encore été imprimée ni mesurée. Les forces sont des **estimations**. Ce guide sera corrigé après le banc d'essai à un doigt.
> Sources : `README.md` et `parts.py` (matebot-hand-tendon), guide officiel *AmazingHand_Assembly.pdf* (Pollen Robotics, CC BY 4.0).

## 0. Principe
- 4 doigts Amazing Hand, 2 DDL par doigt, donc 8 DDL.
- Les servos de la paume sont retirés. **8 × Feetech STS3215 12 V** sont logés dans l'avant-bras, un spool à double gorge (r = 8 mm) sur chacun.
- Chaque servo forme **une boucle antagoniste fermée** : une gorge tire le tendon fléchisseur, l'autre le tendon extenseur.
- Chaque doigt a **deux plaques à tendons** (côté +X et côté −X) sur la pièce `finger_link_tendon`, qui remplace le Link d'origine. Chaque servo a une boucle : fléchisseur sur une plaque, extenseur sur la plaque **opposée** (boucles croisées, sinon le doigt ne peut pas faire d'abduction). Servo A : fléchisseur côté +X, extenseur côté −X. Servo B : fléchisseur côté −X, extenseur côté +X.
- **A et B dans le même sens = flexion. En sens opposé = abduction.**
- Tendons : tresse PE (UHMWPE) classe ~100 lb, dans des gaines PTFE 2 × 4 mm (Bowden).

> 🔄 **Changement décidé le 2026-11-07 :** le bloc unique `servo_bay_8x_sts3215` est remplacé par **4 supports de paire** (une paire de servos par doigt), répartis sur la longueur de l'avant-bras. Ces supports sont **à concevoir**. Le fichier `servo_bay_8x_sts3215.stl` reste utilisable pour le banc d'essai.

## 1. Pièces imprimées (PETG noir sauf mention)
| Pièce | Fichier | Qté (1 main) | Note |
|---|---|---|---|
| Spool double gorge r8 | `spool_r8.stl` | 8 (+2 de rechange) | 100 % de remplissage ou 6 parois |
| Bloc d'ancrage des gaines | `ptfe_anchor_8x.stl` | 4 (2 côté servos, 2 côté paume) | 8 logements par bloc pour 16 gaines. Le README ne parle que d'un bloc par extrémité, à confirmer |
| Support des servos | `servo_bay_8x_sts3215.stl` (v0), puis 4 supports de paire **à concevoir** | 1, puis 4 | ≈120 × 103 × 18 mm |
| Link à tendons (remplace le Link) | `finger_link_tendon.stl` | 4 (+2 de rechange) | v0 non testé. Imprime-en 1 d'abord. Supports nécessaires. Voir le README de `matebot/` |
| Doigt : Finger_Frame-1, Finger_Frame-2, Proximal, Distal, Gimbal, Proximal_Shell, Distal_Shell (pas de Link, voir ci-dessus) | `Amazing Hand Parts - <nom>.stl` | 4 de chaque | Shells en TPU (le README garde les coques/coussinets TPU d'origine) |
| Spacer | `BallJoint_Rod - Spacer.stl` | 0 | **Inutile** avec les tendons (il ne sert qu'aux bielles à rotule d'origine) |
| Paume, plaque, coque supérieure, interface poignet | `R-Palm_Shell`, `R-Hand_Plate`, `R-Top_Shell`, `R-Wrist_Interface` | 1 de chaque (main droite) | Paume à modifier : poches de servos retirées, plaque d'ancrage PTFE ajoutée |

## 2. Quincaillerie et matériel
- 8 × STS3215 12 V, 1 adaptateur Waveshare Bus Servo Adapter (A) dédié à la main, une alimentation 12 V 10 A.
- Tresse PE ~100 lb, ~7 m de tube PTFE 2 × 4 mm, sertissages ~1 mm (pas encore achetés ni chiffrés).
- Vis M2.5 (spool sur palonnier, 4 par spool, soit 32), vis M3 (4 pour le support, 2 par bloc d'ancrage).
- Doigts (guide officiel, par doigt) : 2 bagues Ø int. 6, 1 grande rondelle M2.5, 2 axes D2×10, 2 axes D2×16, 4 vis thermoplastique 2.5×6, 1 vis 2.5×8.
- Outils (guide officiel) : forets Ø1.5 et Ø2, taraud M2, tournevis PH0, pince plate, scalpel, Dremel, perceuse.

## 3. Préparer et tester les servos (avant tout montage)
1. **Mesure un STS3215 et son palonnier au pied à coulisse.** Le corps nominal est de 45,2 × 24,7 × 35 mm, et le cercle de vis du palonnier est **supposé** de 14 mm. Corrige `parts.py` (`S_L, S_W, S_H`, jeu `CL = 0.4`, perçages du spool) avant d'imprimer.
2. Branche **un seul servo à la fois** sur l'adaptateur Waveshare, 12 V. Dans le logiciel FD de Feetech, choisis le port COM, règle le débit à **1 000 000**, puis Open et Search.
3. **Change l'ID** de chaque servo. Le README prévoit les **ID 21 à 28** pour la main ; le guide officiel utilise 1 à 8 (index 1-2, majeur 3-4, annulaire 5-6, pouce 7-8). Choisis un des deux schémas et note-le sur chaque servo.
4. **Centrage :** mets chaque servo en position milieu (511 en brut dans la méthode Arduino du guide officiel ; 1 pas ≈ 0,293°). Note la valeur.
5. Vérifie que chaque servo tourne sans bruit et que l'ID répond seul sur le bus.

## 4. Monter les supports de servos
- **v0 :** 2 rangées de 4, sorties vers le haut, dans `servo_bay_8x_sts3215`, fixé par 4 × M3. Les câbles en guirlande passent dessous par les découpes.
- **Version retenue :** 4 supports de paire (à concevoir), un par doigt. Garde les deux servos de la paire côte à côte (A à gauche, B à droite) pour que les deux boucles sortent ensemble.

## 5. Spools et enroulement des tendons
1. Fixe le spool sur le palonnier rond d'origine avec 4 × M2.5. Le trou central de 6,5 mm laisse passer la vis centrale du palonnier.
2. Servo au **centre**, passe le tendon fléchisseur dans le trou transversal d'une gorge, et l'extenseur dans l'autre.
3. **Enroule au moins 1,5 tour** dans chaque gorge avant l'ancrage, en sens opposés : quand le spool tourne, il tire l'un et relâche l'autre de la même longueur.
4. Repère (estimation CAO) : flexion complète (environ 70° de rotation du Link) ≈ 10 mm de tendon, abduction ±20° ≈ ±4,5 mm, jusqu'à 15 mm au total ≈ 105° de rotation du spool.

## 6. Gaines PTFE
- 16 gaines (8 boucles × 2), environ 30 à 40 cm chacune.
- Fixe **les deux extrémités** : côté servos dans un `ptfe_anchor_8x` (logement de 8 mm de profondeur), côté paume dans la plaque d'ancrage.
- **Rayon de courbure d'au moins 30 mm** partout. Fais passer le faisceau **par le centre du poignet**.
- Repère chaque gaine (doigt, A ou B, fléchisseur ou extenseur) avec du ruban de couleur.

## 7. Assemblage des doigts (d'après le guide officiel)
1. **Reprise des trous Ø2 :** sur Proximal, Distal, Gimbal et `finger_link_tendon` (à la place du Link), les trous de pivot doivent être en partie **glissants** (plusieurs allers-retours de foret) et en partie **serrés** (un seul aller-retour). Nettoie les surfaces imprimées avec support.
2. **Mécanisme :** enfonce les axes D2×10 dans le Distal avec le `finger_link_tendon` entre les oreilles (plaques vers l'extérieur), puis fais de même avec le Gimbal. Enfonce ensuite les axes D2×16 dans le Proximal pour tenir le sous-ensemble. **Vérifie que la flexion et l'extension sont fluides sur toute la course.**
3. **Coques :** Proximal_Shell puis Distal_Shell, avec des vis 2.5×6. **Ne serre pas trop**, sinon la vis traverse la coque mince.
4. **Bagues :** enfonce les 2 bagues Ø int. 6 de chaque côté du Finger_Frame-1. C'est le pivot d'abduction.
5. **Montage final :** insère le doigt dans les bagues, puis serre la vis 2.5×8 avec sa grande rondelle dans le Gimbal **sans bloquer l'abduction**.
6. **Différence avec la version à tendons :** utilise `finger_link_tendon` à la place du Link (mêmes trous de pivot) et saute les bielles à rotule, les palonniers et les Spacers. Chaque plaque a une gorge sur son bord et deux poches pour le nœud ou le sertissage (Ø3,2 × 2 mm, canal de 1,2 mm). **Poche du bas = fléchisseur** (côté paume), **poche du haut = extenseur** (dos du doigt). Passe le tendon dans le canal, fais un nœud (ou sertis) dans la poche, puis remets-le au fond. Croise les boucles : fléchisseur du servo A sur la plaque +X et son extenseur sur la plaque −X, l'inverse pour le servo B.
7. Vérifie que les plaques (jusqu'à X = ±14,4 mm) ne touchent ni le doigt voisin ni la fenêtre de la paume sur toute la course. Les extrémités de gaines dans la paume restent **à concevoir** (à 30 mm ou plus derrière la base du doigt).
8. **Premiers essais avec la limite de couple des servos à 10 %** (environ 35 N dans le tendon) : le Link à tendons est la pièce la plus faible du doigt. Tout ce qui précède est une estimation CAO, non testée.

## 8. Réglage de la tension
1. Mets les deux servos du doigt au **centre**.
2. Tends chaque boucle à la main, doigt droit, puis fais le nœud ou le sertissage.
3. Pas de mou, mais ne force pas : la tension se règle avec le servo, pas en sur-serrant.
4. Après 30 min de cycles, vérifie le fluage de la tresse et retends si besoin.

## 9. Premier test (un doigt, deux servos, gaines de 40 cm)
1. **Limite de couple à 10 %** dans l'EEPROM avant le premier mouvement (30 % au maximum plus tard).
2. Petits mouvements autour du centre :
   - **A+B (même sens) : flexion et extension**
   - **A−B (sens opposés) : abduction**
3. Note la course, le jeu, la friction (lecture de charge du servo) et la température.
4. Ensuite : test au peson (force au bout du doigt), 4 doigts, test de préhension avec une bouteille d'eau, endurance de 30 min. Mets ce guide à jour avec les valeurs mesurées.

## 10. Sécurité
- **Arrêt d'urgence sur la ligne 12 V**, à portée de main.
- Limite de couple basse au départ (10 % pour les essais du doigt) et surveillance de la température. Ne maintiens jamais le servo au couple de blocage.
- Garde les doigts et les cheveux loin des spools pendant les tests. Porte des lunettes, car un tendon peut casser sous tension.
- Un adaptateur de bus séparé pour la main au début, pour faciliter le débogage.

---
*Basé sur l'Amazing Hand de Pollen Robotics (CC BY 4.0). Modifications MateBot : servos sortis de la main, doigts entraînés par tendons Bowden depuis l'avant-bras.*
