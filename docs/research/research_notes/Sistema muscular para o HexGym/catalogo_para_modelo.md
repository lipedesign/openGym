# Catálogo do openGym para o manequim muscular 3D do HexGym

Notas de leitura do repositório (só texto: JSON, JS e Markdown). Objetivo: saber, para cada
exercício do catálogo, quais regiões do nosso manequim (regiões do MuscleMap, 18 grupos, 31
regiões por lado) acendem como primárias (violeta forte) e secundárias (violeta claro).

Arquivos produzidos nesta pasta:

- `exercise_regions.json`: o resultado, uma linha por id.
- `build_exercise_regions.py`: o gerador. `python3 build_exercise_regions.py` regrava o JSON;
  `--report` imprime todas as contagens usadas abaixo. Só usa a biblioteca padrão do Python e
  falha se o catálogo ganhar um termo de músculo que o script ainda não conhece.

Nenhuma mídia foi aberta. Em `catalogue/media/` só os nomes de arquivo foram listados.

## Resumo em números

| Item | Valor |
|---|---|
| Arquivos em `catalogue/exercises/` | 6.554 |
| Exercícios de verdade (sem `variantOf`) | 5.632 |
| Desenhos de figura feminina (`{id, variantOf}` só) | 922 |
| Exercícios com `muscleMap` curado | 246 (todos de origem ExerciseDB) |
| Exercícios com ao menos uma região primária | 5.460 (96,9%) |
| Sem primária, só secundárias (alvo "cardiovascular system") | 172 |
| Sem nenhuma região | 0 |
| Que precisariam do fallback por parte do corpo | 0 |
| Com algum termo de sub-parte no texto | 1.471 |
| Que acendem sub-parte (grupo parcial em primary ou secondary) | 887 (382 no primário) |
| Com dica de ênfase (`emphasis`) | 615 |
| Que usam alguma informação de sub-parte (parcial ou ênfase) | 1.366 |
| Que só acendem grupos inteiros | 4.266 |
| Média de regiões por exercício | 1,90 primárias, 3,89 secundárias |

Validação: projetando as regiões de volta para os 18 grupos, o resultado bate com o
`musclesOf()` do app em 5.546 dos 5.632 exercícios. Os 86 que diferem são todos o mesmo caso
proposital: "rotator cuff", que o app joga em deltoides e o MuscleMap desenha nas costas (ver
seção 3).

## 1. De onde vêm os dados

- `catalogue/exercises/<id>.json`: um exercício por arquivo, em inglês. Campos: `id`, `name`,
  `bodyPart`, `equipment`, `target` (um termo), `secondaryMuscles` (lista), `category`,
  `description`, `instructions`, `textSource`, e opcionais `hold` (135), `needs` (110),
  `muscleMap` (246), `femaleVariant` (935), `maleVariant` (13), `variantOf` (922).
- Os 922 arquivos com `variantOf` têm só `{id, variantOf}`: são a mesma coisa desenhada numa
  figura feminina e não têm músculos próprios.
- `textSource`: 1.324 `exercisedb` (texto de origem ExerciseDB v1, MIT, via
  hasaneyldrm/exercises-dataset) e 4.308 `opengym` (escritos para o openGym, AGPL). O
  `muscleMap` e todas as descrições são do openGym (AGPL). O aviso está em `NOTICE.md` na raiz
  (não existe `catalogue/NOTICE.md`; o aviso da mídia é `catalogue/media/NOTICE.md`).
- O vocabulário é fechado: `scripts/catalogue/validate.mjs` lista os 19 termos aceitos em
  `target`, os 41 em `secondaryMuscles` e os 18 nomes do mapa (`MUSCLES`) aceitos dentro de
  `muscleMap`. Todos os 60 termos aparecem no catálogo.
- `scripts/catalogue/build.mjs` gera `frontend/src/lib/exercises-data.js` (EXDB: `tg` = target,
  `sm` = secondaryMuscles, `mg` = primeiro secundário, `img` = `<id>.webp`, `gif` = `<id>.mp4`,
  `fv`/`mv` = desenho feminino/masculino) e `frontend/src/lib/exercise-muscle-map.json` (o
  `muscleMap` de cada exercício, renomeando `bodyPart` para `bp` e `weights` para
  `muscleWeights`). Verifiquei: o JSON gerado bate 100% com os 246 `muscleMap` do catálogo.

Distribuições úteis (5.632 exercícios):

- category: strength 2.895, calisthenics 1.012, stretching 466, mobility 372, plyometrics 240,
  isometric 183, cardio 145, yoga 109, olympic 74, pilates 62, rehab 38, combat 36.
- bodyPart: upper legs 1.605, waist 863, back 720, shoulders 618, upper arms 561, chest 477,
  full body 251, lower legs 239, lower arms 139, cardio 93, neck 66.
- equipment (principais): body weight 2.246, dumbbell 757, cable 446, barbell 389, leverage
  machine 279, band 261, kettlebell 187, resistance band 149, weighted 148, suspension trainer
  133, smith machine 94.
- Quantidade de secundários por exercício: 0 (1), 1 (416), 2 (1.816), 3 (2.122), 4 (1.090),
  5 (185), 6 (2). São 15.711 menções de secundários no total.

## 2. Como o app transforma texto em músculos (`frontend/src/lib/muscles.js`)

Precedência em `weightsOf(ex)` para um exercício do catálogo:

1. `muscleWeights` (vem de `muscleMap.weights`): se existir, é a resposta inteira. Só conta
   músculo de `MUSCLES` com peso entre 0 e 1. Peso 0 é "associação explícita sem crédito": fica
   nos metadados, mas `musclesOf()` só devolve pesos > 0, então não pinta.
2. `primaries` / `secondaries` (de `muscleMap`): primário vale 1, secundário vale 0,4.
3. Campos de exercício próprio (`muscleGroups`, `muscles`, `targetMuscles`): não ocorrem no
   catálogo.
4. Texto livre: `tg` (target) vale 1; `mg` e cada item de `smOf(ex)` (secundários mais o
   `SECONDARY_ADDITIONS` de `exercises.js`) valem 0,4. Quando dois termos caem no mesmo grupo,
   fica o maior peso.
5. Se nada foi reconhecido: `BY_BODYPART[bp]` (pesos que somam 1, por exemplo upper legs =
   quadríceps 0,4, posteriores 0,35, glúteo 0,25).

Detalhes que importam:

- `SECONDARY = 0.4` é a única nuance de peso no texto livre: primário 1, secundário 0,4. Os
  pesos do `muscleMap` usam só 1, 0,4 e 0 (108, 230 e 104 ocorrências).
- O "load" multiplica o peso por séries feitas ("séries efetivas"); `levelsOf` reduz a 5 tons
  relativos ao músculo mais treinado.
- "cardiovascular system" vira um pseudo-músculo com peso 1 que não está em `MUSCLES` (não é
  desenhado). Por isso nenhum exercício do catálogo cai no fallback por parte do corpo no app:
  todo `target` é reconhecido. No nosso modelo esse termo não acende nada.
- `ALIAS` colapsa os 60 termos em 18 grupos e joga fora as sub-partes: "upper chest" vira
  chest, "rear deltoids" e "rotator cuff" viram deltoids, "rhomboids", "lats" e "back" viram
  upper-back, "lower abs" vira abs, "levator scapulae" vira trapezius, "abductors" vira gluteal,
  "brachialis" vira biceps, "soleus" vira calves. Mapeiam para `null` (somem): ankles, feet,
  hands, ankle stabilizers, sternocleidomastoid.
- O mapa 2D (`body-paths.js`, convertido do MuscleMap) descartou de propósito os sub-grupos do
  MuscleMap. O comentário do arquivo diz que pintar sub-região "implicaria uma precisão que os
  dados não têm". As chaves desenhadas são exatamente os 18 grupos de `MUSCLES` mais as partes
  inertes (head, hair, neck, hands, feet, knees, ankles). `BodyMap.jsx` pinta cada grupo com
  `l0..l4`; `MiniBodyMap.jsx` e `Heatmap.jsx` reutilizam a mesma escala; `MuscleExplorer.jsx`
  conta exercícios por grupo com `musclesOf`.
- `SECONDARY_ADDITIONS` (em `exercises.js`): 6 exercícios ganham um secundário a mais.
  "rear deltoids" em 0027, 0293, 0499, 0861 (remadas) e "lower back" em 4133 e 10189. Os
  quatro primeiros têm `muscleMap`, então no app a adição é ignorada (o `muscleMap` vence);
  no nosso script ela serve para estreitar o deltoide para `rearDeltoid` (seção 6).

## 3. Vocabulário do catálogo e mapeamento proposto para o modelo

Convenção de regiões (slug entre colchetes). Cuidado: "chest", "deltoids", "quadriceps" e
"trapezius" são nome de grupo no app e nome de UMA região no MuscleMap. No JSON, uma região
`chest` sozinha significa só o peitoral médio; o grupo inteiro aparece sempre expandido.

| Grupo (app) | Regiões do modelo |
|---|---|
| chest | upperChest, chest, lowerChest |
| deltoids | frontDeltoid, deltoids (lateral), rearDeltoid |
| upper-back | upperBack (latíssimo), rhomboids, rotatorCuff |
| trapezius | upperTrapezius, trapezius (médio), lowerTrapezius |
| abs | upperAbs (3 fileiras), lowerAbs |
| quadriceps | quadriceps (reto femoral), innerQuad (vasto medial), outerQuad (vasto lateral) |
| demais 12 | uma região cada: biceps, triceps, forearm, obliques, serratus, lowerBack, gluteal, hipFlexors, adductors, hamstring, calves, tibialis |

### 3.1 Termos de `target` (19, contagem = exercícios)

| Termo | Exercícios | ALIAS do app | Regiões no modelo | Observação |
|---|---:|---|---|---|
| abs | 848 | abs | upperAbs, lowerAbs | |
| glutes | 671 | gluteal | gluteal | |
| quads | 654 | quadriceps | quadriceps, innerQuad, outerQuad | nenhum termo separa as cabeças |
| delts | 619 | deltoids | frontDeltoid, deltoids, rearDeltoid | nenhum termo separa frontal e lateral |
| pectorals | 473 | chest | upperChest, chest, lowerChest | |
| lats | 317 | upper-back | **upperBack** | sub-parte |
| biceps | 284 | biceps | biceps | |
| triceps | 283 | triceps | triceps | |
| calves | 242 | calves | calves | |
| upper back | 239 | upper-back | upperBack, rhomboids, rotatorCuff | genérico; ver nota abaixo |
| hamstrings | 217 | hamstring | hamstring | |
| cardiovascular system | 172 | pseudo-músculo | nenhuma | não é músculo |
| spine | 168 | lower-back | lowerBack | eretores da espinha |
| forearms | 147 | forearm | forearm | |
| abductors | 90 | gluteal | gluteal | detalhe perdido: glúteo médio/mínimo, TFL |
| adductors | 68 | adductors | adductors | |
| levator scapulae | 65 | trapezius | **upperTrapezius** | sub-parte (fica sob o trapézio superior) |
| traps | 60 | trapezius | upperTrapezius, trapezius, lowerTrapezius | nenhum termo separa as porções |
| serratus anterior | 15 | serratus | serratus | |

Nota sobre "upper back" e "lats": o catálogo usa os dois como alvos diferentes (puxadas e
barras quase sempre "lats"; remadas e crucifixo invertido quase sempre "upper back"). Mapeei
"lats" para só o latíssimo e "upper back" para o grupo inteiro, porque o termo é genérico e as
remadas também trabalham o latíssimo. Alternativa a avaliar: "upper back" como rhomboids +
trapézio médio, deixando o latíssimo só para "lats".

### 3.2 Termos de `secondaryMuscles` (41, contagem = exercícios)

| Termo | Exercícios | ALIAS do app | Regiões no modelo | Observação |
|---|---:|---|---|---|
| core | 1.885 | abs | upperAbs, lowerAbs | o app não inclui oblíquos em "core" |
| shoulders | 1.482 | deltoids | frontDeltoid, deltoids, rearDeltoid | |
| glutes | 1.334 | gluteal | gluteal | |
| hamstrings | 1.332 | hamstring | hamstring | |
| triceps | 791 | triceps | triceps | |
| hip flexors | 782 | hip-flexors | hipFlexors | nunca é alvo |
| obliques | 651 | obliques | obliques | nunca é alvo |
| quadriceps | 637 | quadriceps | quadriceps, innerQuad, outerQuad | |
| forearms | 634 | forearm | forearm | |
| upper back | 622 | upper-back | upperBack, rhomboids, rotatorCuff | |
| lower back | 601 (+2 por SECONDARY_ADDITIONS) | lower-back | lowerBack | |
| calves | 592 | calves | calves | |
| biceps | 561 | biceps | biceps | |
| rhomboids | 375 | upper-back | **rhomboids** | sub-parte |
| trapezius | 359 | trapezius | upperTrapezius, trapezius, lowerTrapezius | |
| rear deltoids | 328 (+4 por SECONDARY_ADDITIONS) | deltoids | **rearDeltoid** | sub-parte |
| upper chest | 279 | chest | **upperChest** | sub-parte |
| chest | 275 | chest | upperChest, chest, lowerChest | |
| adductors | 273 | adductors | adductors | |
| lats | 224 | upper-back | **upperBack** | sub-parte |
| grip muscles | 222 | forearm | forearm | detalhe perdido (flexores dos dedos) |
| ankles | 216 | null | nenhuma | pele no modelo |
| lower abs | 209 | abs | **lowerAbs** | sub-parte |
| rotator cuff | 185 | deltoids | **rotatorCuff** | sub-parte; muda de grupo (ver abaixo) |
| brachialis | 156 | biceps | biceps | detalhe perdido: sem região própria |
| feet | 114 | null | nenhuma | pele |
| soleus | 105 | calves | calves | detalhe perdido: sem região própria |
| shins | 72 | tibialis | tibialis | nunca é alvo |
| wrist flexors | 70 | forearm | forearm | detalhe perdido |
| groin | 61 | adductors | adductors | |
| inner thighs | 56 | adductors | adductors | |
| sternocleidomastoid | 54 | null | nenhuma | pescoço é pele no modelo |
| wrist extensors | 51 | forearm | forearm | detalhe perdido |
| hands | 37 | null | nenhuma | pele |
| traps | 33 | trapezius | upperTrapezius, trapezius, lowerTrapezius | |
| deltoids | 28 | deltoids | frontDeltoid, deltoids, rearDeltoid | |
| back | 11 | upper-back | upperBack, rhomboids, rotatorCuff | genérico; poderia incluir lowerBack |
| latissimus dorsi | 5 | upper-back | **upperBack** | sub-parte |
| ankle stabilizers | 4 | null | nenhuma | pele |
| wrists | 3 | forearm | forearm | |
| abdominals | 2 | abs | upperAbs, lowerAbs | |

"rotator cuff" é o único termo que muda de grupo: o app o soma ao deltoide, e o MuscleMap tem
uma região própria nas costas (rotatorCuff, dentro de upper-back). Em 86 exercícios isso faz
upper-back aparecer como secundário onde o app só mostra deltoide. É a única divergência do
nosso JSON em relação ao app no nível de grupo.

### 3.3 Termos com sub-parte que o app joga fora e o modelo pode mostrar

"Exercícios" conta onde o termo aparece (qualquer papel). "Parcial" conta onde, no JSON final,
a sub-região acende sem o resto do grupo no mesmo nível (é o que o modelo mostra de novo).
"Ênfase" conta onde o grupo inteiro já estava no primário e a sub-parte ficou registrada só no
campo `emphasis`.

| Termo | Região | Exercícios | Parcial (prim / sec) | Ênfase | Engolido pelo grupo |
|---|---|---:|---:|---:|---:|
| lats | upperBack | 541 | 429 (317 / 112) | 87 | 25 |
| rhomboids | rhomboids | 375 | 180 (11 / 169) | 121 | 74 |
| rear deltoids | rearDeltoid | 332 | 183 (0 / 183) | 136 | 13 |
| upper chest | upperChest | 279 | 129 (0 / 129) | 141 | 9 |
| lower abs | lowerAbs | 209 | 2 (0 / 2) | 200 | 7 |
| rotator cuff | rotatorCuff | 185 | 95 (0 / 95) | 10 | 80 |
| levator scapulae | upperTrapezius | 65 | 65 (65 / 0) | 0 | 0 |
| latissimus dorsi | upperBack | 5 | 5 (0 / 5) | 0 | 0 |

Por região, acesas sem o resto do grupo: upperBack 317 primário / 117 secundário; rhomboids
11 / 249; rotatorCuff 0 / 256; rearDeltoid 0 / 183; upperChest 0 / 129; upperTrapezius 65 / 0;
lowerAbs 0 / 2; trapezius médio e lowerTrapezius 0 / 52 (efeito colateral: alvo "levator
scapulae" + secundário "trapezius" deixa o superior no primário e o resto no secundário).

Termos que carregam detalhe anatômico mas não têm região própria no modelo (vão para o grupo
inteiro, sem ganho): brachialis (156), soleus (105), abductors (90 alvos), grip muscles (222),
wrist flexors (70), wrist extensors (51), groin (61), inner thighs (56), sternocleidomastoid
(54, não desenhável).

## 4. Mídia: como cada arquivo se liga a um exercício

Só listei nomes. `catalogue/media/still/` tem 6.554 arquivos `<id>.webp` e
`catalogue/media/clip/` tem 6.554 arquivos `<id>.mp4` (não há GIF; "gif" é o nome histórico do
campo). O conjunto de nomes (sem extensão) é idêntico ao conjunto de ids de
`catalogue/exercises/`. Ou seja:

- arquivo de mídia `<id>.*` = exercício `<id>`, quando o id é um exercício (5.632);
- `<id>.*` = desenho feminino de `variantOf` (922). No app, `ex.fv` aponta para esse desenho e
  `imgSrc`/`gifSrc` montam `exercise-media/still/<fv>.webp` e `exercise-media/clip/<fv>.mp4`.
  Dos 935 `femaleVariant`, 922 apontam para esses desenhos e 13 apontam para outro exercício de
  verdade (pares com `maleVariant`).

O `exercise_regions.json` tem as 6.554 chaves: os 922 desenhos repetem as regiões do exercício
base e carregam `"variantOf"`. Então "mídia ↔ exercício ↔ músculos" é uma junção direta pelo
nome do arquivo, sem abrir mídia nenhuma.

## 5. Os mapas curados

### 5.1 O que existe

| Arquivo | Entradas | Papel hoje |
|---|---:|---|
| `catalogue/exercises/<id>.json` campo `muscleMap` | 246 | **fonte da verdade** |
| `frontend/src/lib/exercise-muscle-map.json` | 246 | gerado pelo build a partir do catálogo; é o que o app lê em tempo de execução (`exercises.js`) |
| `exercise-muscle-batch-1.json` | 104 | legado: "compound lifts", ExRx-informed |
| `exercise-muscle-batch-2.json` | 119 | legado: máquinas, cabo, sled e Smith |
| `exercise-muscle-olympic.json` | 16 | legado: levantamentos olímpicos |
| `exercise-muscle-batch-1.js` `USER_EXERCISE_MUSCLE_OVERRIDES` | 72 | legado: pesos aprovados pelo dono, com zeros explícitos |
| `exercise-muscle-batch-2.js` | 0 | só reexporta o JSON |

Os três JSON legados não se sobrepõem (0 ids em comum). A função
`exerciseMuscleMetadataFor(id)` mescla, nesta ordem, batch-1, batch-2, olympic e overrides (o
último vence). Esse resultado foi gravado uma vez no catálogo por
`scripts/catalogue/import-legacy.mjs` (script de uso único da v1.4.0). Hoje os arquivos legados
só são lidos pelos próprios testes e por esse script; o app não os importa.

Conferi: a união dos legados (104 + 119 + 16 + 7 overrides sem lote = 246) é exatamente o
conjunto do `muscleMap`, e as listas primaries/secondaries batem em 100%. A única diferença é
que 15 remadas (0167, 0193, 0208, 0236, 0239, 0571, 0588, 1313, 1318, 1320, 1321, 1323, 1324,
1350, 3200) ganharam `weights` direto no catálogo depois (commit fe84f240f, "Fix: back
exercises should not commit to chest and triceps"); os legados não foram atualizados. Por isso há 87 entradas
com pesos no catálogo e 72 nos overrides.

### 5.2 Formato

```json
"muscleMap": {
  "bodyPart": "full body",                         // opcional, 26 casos (troca a parte do corpo)
  "primaries": ["quadriceps", "gluteal", "adductors"],
  "secondaries": ["hamstring", "calves", "lower-back", "abs", "obliques"],
  "weights": { "upper-back": 1, "biceps": 0.4, "triceps": 0 }   // opcional, 87 casos
}
```

Só nomes de grupo do mapa 2D (os 18 de `MUSCLES`); não há sub-parte. Combinações: 134 só
listas, 80 listas + pesos, 25 listas + bodyPart, 1 tudo, 7 só pesos (prensas de panturrilha
1391, 1392, 2289, 2334, 2335, 0738 e abdução 3006). Tamanho do primário: 1 grupo em 166, 2 em
13, 3 em 43, 4 em 11, 5 em 4, 6 em 2. Trocas de bodyPart: 25 para "full body" (agachamentos,
terras, olímpicos), 1 de back para upper legs.

Cobertura por tipo: 216 strength, 18 olympic, 12 calisthenics; equipamentos leverage machine
60, cable 55, barbell 42, smith 21, dumbbell 19, sled 15, kettlebell 12, body weight 11. Os 246
são todos de `textSource: exercisedb`; nenhum dos 4.308 exercícios novos tem `muscleMap`.

### 5.3 Como sobrescrevem o texto livre

No app, quando há `muscleMap`, o texto livre é ignorado por completo (inclusive o
`SECONDARY_ADDITIONS`). Comparando os 246 com o texto do mesmo exercício:

- O grupo do `target` não está no primário curado em 5 casos, todos correções de ruído do
  ExerciseDB: 1010 band straight leg deadlift (alvo spine), 0518 kettlebell alternating hang
  clean (alvo forearms), 0525 e 0526 (alvo biceps em cleans), 0552 kettlebell two arm clean
  (alvo delts).
- Secundários do texto promovidos a primário: quadríceps 33, posteriores 22, glúteo 14, lombar
  7, trapézio 5, tríceps 4, deltoide 1.
- Secundários do texto descartados pelo curado: posteriores 20, upper-back 16, glúteo 11,
  deltoide 10, tríceps 9, panturrilha 9, quadríceps 3, bíceps 3, lombar 1, trapézio 1.
- Grupos que o curado acrescenta: trapézio 77, adutores 55, deltoide 55, oblíquos 44, lombar 37,
  panturrilha 32, antebraço 29, abdômen 28, quadríceps 21, serrátil 20, peitoral 15, upper-back
  11, posteriores 11, glúteo 10, tríceps 5, bíceps 3, flexores do quadril 1.

### 5.4 Pesos

Pesos curados mandam sobre as listas: 1 = primário, 0,4 = secundário, 0 = "este músculo foi
considerado e não recebe crédito". Os zeros: tríceps 43 (puxadas e remadas), bíceps 25 (supinos
e crucifixos), peitoral 17 (remadas), panturrilha 10 (leg press), posteriores 8 (prensas de
panturrilha, abdução), deltoide 1 (0607 lever triceps extension). No nosso JSON, zero não acende.

### 5.5 Problemas de qualidade

1. **Listas e pesos discordam.** Em 70 entradas, um músculo com peso 0 continua em
   `secondaries` (ex.: 0025 barbell bench press lista biceps; as remadas de fe84f240f listam
   chest e triceps). O desenho usa os pesos (não pinta), mas `muscleGroupsOf`,
   `exerciseMuscleSnapshot` e o editor de exercício próprio (`sheets.jsx`, que semeia os chips
   de secundário a partir dessas listas) ainda veem o bíceps como músculo do supino. Em outras
   10 entradas o zero não está na lista (barras: tríceps 0 fora da lista). O script usa só os
   pesos quando existem.
2. **Legados desatualizados.** Os 15 pesos de remada não estão em batch-2 nem nos overrides.
   Quem regenerar o catálogo a partir dos legados perde essa correção.
3. **O mesmo movimento com mapas diferentes.** 41 famílias de nome (ignorando parênteses e
   "v. N") misturam um membro curado com irmãos em texto livre. Exemplo forte: 0032 barbell
   deadlift (curado: primário lombar, glúteo, posteriores) contra 0966 "(back view)", 0967
   "(front pov)" e 6692 "(side pov)", que são o mesmo levantamento visto de outro ângulo e só
   acendem glúteo no primário. Dos 13 nomes com "(... pov)" ou "(back view)", 4 divergem do
   exercício base. Outros: 0043 barbell full squat (curado: quadríceps, glúteo, adutores) contra
   0878 "(with rack)" (só quadríceps); 2805 contra 2806 (single leg deadlift: curado glúteo +
   posteriores, irmão só posteriores). No total, 362 famílias de nome com 844 membros; 196 têm
   mapas de região diferentes entre os membros e 47 diferem já no primário.
4. **Pares masculino/feminino que são exercícios separados.** 13 exercícios têm `maleVariant`;
   em 9 desses pares as regiões diferem (ex.: 2797 e 2798 barbell squat jump step rear lunge,
   um com abdômen no secundário e o outro sem).
5. **Nomes duplicados.** 6 nomes exatos repetidos; só um par diverge: 0088 e 1371 "barbell
   seated calf raise" (o primeiro tem quadríceps como secundário).
6. **"upper back" contra "lats" nas remadas.** Das 293 remadas (sem upright row), 164 têm alvo
   "upper back" e 85 "lats": 1350 lever seated row (curado), 2265 "v. 2" (upper back) e 2664
   "(plate loaded)" (lats) são a mesma máquina.
7. **"upper chest" não indica supino inclinado.** Aparece em 74 supinos/flexões, dos quais 52
   são retos (ex.: 3185 barbell bench press with hanging band, 7620 barbell banded bench press),
   e só em 22 dos 58 inclinados com alvo pectorals. Por isso o script não promove "upper chest"
   a primário; registra como ênfase.
8. **"rear deltoids" em elevação lateral.** 14 das 63 elevações laterais listam "rear deltoids";
   o músculo principal delas é o lateral, que nenhum termo nomeia.
9. **"levator scapulae" como alvo de pescoço.** 63 dos 66 exercícios de bodyPart neck usam esse
   alvo, inclusive flexões de pescoço que trabalham o esternocleidomastoideo (50 deles também
   listam sternocleidomastoid).
10. O comentário de `muscles.js` fala em "nineteen primary and forty secondary spellings"; o
    vocabulário real tem 19 e 41.

## 6. Como o script decide (resumo do que está em `build_exercise_regions.py`)

1. **muscleMap (246)**: pesos (`>= 1` primário, `0 < w < 1` secundário, 0 descartado) ou
   listas. Cada grupo curado vira as regiões do grupo, e é **estreitado** quando o texto livre
   do mesmo exercício nomeia só sub-partes daquele grupo. Casos: puxadas com alvo "lats" ficam
   só com upperBack no primário (21 exercícios); remadas e puxadas com "rear deltoids" ficam com
   rearDeltoid no secundário (15, incluindo 0027, 0293, 0499, 0861 via SECONDARY_ADDITIONS);
   "lats" + "rhomboids" deixam upperBack + rhomboids (11); crucifixos invertidos e remadas de
   deltoide posterior ficam com rhomboids no secundário (6); 0587 lever military press fica com
   upperChest no secundário (1).
2. **curated (2)**: texto livre mais `SECONDARY_ADDITIONS`, para os 2 exercícios com adição e
   sem `muscleMap` (4133, 10189).
3. **freetext (5.384)**: `target` vira primário; `secondaryMuscles` vira secundário, menos o que
   já é primário.
4. **bodypart (0)**: só se nada acender; usa `BY_BODYPART` do app (maior peso primário, o resto
   secundário). Nenhum exercício chega aqui hoje.
5. **emphasis**: sub-partes nomeadas no texto dentro de um grupo que já está inteiro no
   primário. Ex.: 2127 weighted captain's chair leg raise = primário abdômen inteiro, ênfase
   lowerAbs. Distribuição: lowerAbs 200, upperChest 141, rearDeltoid 136, rhomboids 121,
   upperBack 87, rotatorCuff 10.

Exemplos de linhas:

```json
"0025": {"name": "barbell bench press", "primary": ["upperChest", "chest", "lowerChest"], "secondary": ["frontDeltoid", "deltoids", "rearDeltoid", "triceps"], "source": "muscleMap"},
"0652": {"name": "pull-up", "primary": ["upperBack"], "secondary": ["frontDeltoid", "deltoids", "rearDeltoid", "biceps", "forearm"], "source": "muscleMap"},
"0861": {"name": "cable seated row", "primary": ["upperBack", "rhomboids", "rotatorCuff"], "secondary": ["rearDeltoid", "biceps", "forearm"], "source": "muscleMap"},
"7252": {"name": "dumbbell incline powell raise", "primary": ["frontDeltoid", "deltoids", "rearDeltoid"], "secondary": ["upperBack", "rhomboids", "rotatorCuff"], "source": "freetext", "emphasis": ["rearDeltoid"]},
"0004": {"name": "air twisting crunch", "primary": ["upperAbs", "lowerAbs"], "secondary": ["obliques", "hipFlexors"], "source": "freetext", "variantOf": "5266"}
```

As regiões saem sempre na ordem cabeça-pés do app (trapézio, deltoide, peitoral, upper-back,
serrátil, bíceps, tríceps, antebraço, abdômen, oblíquos, lombar, glúteo, quadríceps,
posteriores, adutores, flexores do quadril, panturrilha, tibial).

## 7. Cobertura

- Fontes: freetext 5.384 (95,6%), muscleMap 246 (4,4%), curated 2, bodypart 0.
- Com ao menos uma primária: 5.460. Sem primária: 172, todos com alvo "cardiovascular system"
  (cardio 118, plyometrics 47, calisthenics 3, strength 2, combat 1, rehab 1); todos têm
  secundários, então acendem algo em violeta claro. Sugestão: no HexGym, promover os
  secundários a primários nesses 172 ou mostrá-los com um selo de "cardio".
- Só fallback por parte do corpo: 0 (no app também 0, porque o pseudo-músculo cardio conta como
  reconhecido). Só 1 exercício não tem secundário nenhum (5889 corpse pose savasana, alvo spine).
- Acendem sub-parte: 887 (382 no primário: 317 por "lats" e 65 por "levator scapulae"); com
  ênfase: 615; usam alguma informação de sub-parte: 1.366 de 1.471 que têm termo de sub-parte.
- Contagem por região (exercícios que acendem como primária / secundária):

| Região | Prim. | Sec. | Região | Prim. | Sec. |
|---|---:|---:|---|---:|---:|
| upperTrapezius | 139 | 386 | upperAbs | 849 | 1.623 |
| trapezius (médio) | 74 | 438 | lowerAbs | 849 | 1.625 |
| lowerTrapezius | 74 | 438 | obliques | 0 | 695 |
| frontDeltoid | 621 | 1.544 | lowerBack | 174 | 605 |
| deltoids (lateral) | 621 | 1.544 | gluteal | 785 | 1.220 |
| rearDeltoid | 621 | 1.727 | quadriceps | 697 | 604 |
| upperChest | 473 | 417 | innerQuad | 697 | 604 |
| chest (médio) | 473 | 288 | outerQuad | 697 | 604 |
| lowerChest | 473 | 288 | hamstring | 247 | 1.293 |
| upperBack | 556 | 584 | adductors | 105 | 305 |
| rhomboids | 250 | 716 | hipFlexors | 0 | 783 |
| rotatorCuff | 239 | 723 | calves | 242 | 615 |
| serratus | 15 | 20 | tibialis | 0 | 72 |
| biceps | 282 | 562 | | | |
| triceps | 287 | 783 | | | |
| forearm | 146 | 777 | | | |

## 8. Padrões de ativação por família de exercício

Famílias por palavra-chave no nome (regex no script, uma família pode sobrepor outra).
Percentuais = parcela dos membros em que a região acende. "Grupo inteiro" quer dizer que as
regiões do grupo acendem juntas porque o termo do catálogo é genérico. Primário com >= 30% e
secundário com >= 25% dos membros.

| Família | n | Alvos dominantes | Primário típico | Secundário típico | Sub-parte que os dados dão |
|---|---:|---|---|---|---|
| Supino / chest press | 145 | pectorals 126, triceps 17 | peitoral inteiro 87% | deltoide inteiro 98%, tríceps 87% | ênfase upperChest 39% (inclusive supinos retos) |
| Inclinado (qualquer exercício) | 156 | pectorals 58, delts 25, triceps 20, biceps 19 | peitoral inteiro 37% | deltoide 58 a 62%, tríceps 36% | ênfase upperChest 14% |
| Declinado | 65 | pectorals 28, abs 18 | peitoral inteiro 43% | deltoide 62%, tríceps 45%, flexores do quadril 28% | nenhum termo para peitoral inferior |
| Crucifixo (sem rear/reverse) | 84 | pectorals 75 | peitoral inteiro 89% | deltoide 82%, bíceps 30% | ênfase upperChest 42% |
| Flexão de braço | 170 | pectorals 119, triceps 20 | peitoral inteiro 70% | deltoide 91%, tríceps 84%, abdômen 75% | nenhuma |
| Mergulho (dip) | 58 | triceps 41, pectorals 11 | tríceps 71% | deltoide 93%, peitoral 71% | nenhuma |
| Desenvolvimento (shoulder/overhead/military/arnold/push press) | 110 | delts 92 | deltoide inteiro 84% | tríceps 99%, upperChest 63%, abdômen 51%, trapézio 35% | upperChest no secundário |
| Elevação lateral | 52 | delts 50 | deltoide inteiro 96% | trapézio 87%, rotatorCuff 77%, rhomboids 40%, upperBack 38% | ênfase rearDeltoid 17% (o certo seria o lateral) |
| Remada alta (upright row) | 19 | delts 18 | deltoide inteiro 95% | trapézio 100%, bíceps 95%, upper-back 47% | nenhuma |
| Elevação frontal | 50 | delts 46 | deltoide inteiro 92% | upperChest 70%, trapézio 52%, abdômen 40% | upperChest no secundário |
| Deltoide posterior (rear delt, reverse fly, face pull, pull apart) | 97 | delts 91 | deltoide inteiro 94% | rhomboids 94%, rotatorCuff 63%, upperBack 61%, trapézio 53% | ênfase rearDeltoid 64%, rhomboids parcial |
| Rotação de ombro (external/internal) | 65 | delts 48, glutes 10 | deltoide inteiro 74% | rotatorCuff 75% | ênfase rearDeltoid 38%, rotatorCuff parcial |
| Remada (sem upright) | 293 | upper back 164, lats 85, delts 21 | upperBack 85%, rhomboids e rotatorCuff 56% | bíceps 89%, rearDeltoid 54%, rhomboids 43%, rotatorCuff 36%, antebraço 29% | rearDeltoid parcial; ênfase upperBack e rhomboids 26% |
| Puxada / barra (pulldown, pull-up, chin-up) | 156 | lats 142 | upperBack (só latíssimo) 92% | bíceps 87%, antebraço 72%, rhomboids 56%, rotatorCuff 47%, rearDeltoid 34% | latíssimo isolado no primário |
| Pullover | 41 | lats 22, pectorals 16 | upperBack 54%, peitoral 39% | tríceps 93%, abdômen 56%, peitoral 51% | nenhuma |
| Encolhimento (shrug) | 38 | traps 35 | trapézio inteiro 92% | rhomboids 61%, antebraço 53%, upper-back 50 a 53%, deltoide 42 a 45% | nenhuma (o real é o trapézio superior) |
| Rosca (curl, sem leg curl) | 341 | biceps 262, forearms 63 | bíceps 77% (antebraço nas roscas de punho) | antebraço 76% | brachialis em 156, sem região |
| Tríceps (extension, pushdown, kickback, skull crusher) | 181 | triceps 156, glutes 21 | tríceps 86% | deltoide 78 a 80%, abdômen 34%, antebraço 29% | nenhuma |
| Agachamento | 433 | quads 296, glutes 97 | quadríceps inteiro 73% | posteriores 79%, glúteo 72%, abdômen 56%, panturrilha 34%, adutores 30% | nenhuma cabeça do quadríceps |
| Afundo (lunge, split squat, step-up) | 270 | quads 174, glutes 70 | quadríceps inteiro 65% | posteriores 87%, glúteo 71%, abdômen 52%, quadríceps 33%, panturrilha 31%, adutores 30% | nenhuma |
| Terra / stiff (deadlift, RDL, good morning) | 163 | glutes 81, hamstrings 77 | posteriores 58%, glúteo 51% | lombar 93%, antebraço 47%, abdômen 39%, quadríceps 37% | nenhuma |
| Elevação de quadril (hip thrust, bridge) | 134 | glutes 101, abs 18 | glúteo 78% | posteriores 79%, abdômen 74%, lombar 28% | nenhuma |
| Leg press | 30 | quads 19, glutes 8, calves 3 | quadríceps 83%, glúteo 30% | posteriores 90%, glúteo 63%, panturrilha 50%, adutores 33% | nenhuma |
| Cadeira extensora | 18 | quads 14 | quadríceps inteiro 78% | flexores do quadril 83% | nenhuma |
| Mesa flexora (leg curl, nordic) | 47 | hamstrings 46 | posteriores 98% | panturrilha 94%, glúteo 83%, abdômen 36% | nenhuma |
| Abdução de quadril | 57 | abductors 47 | glúteo 86% | abdômen 40% | glúteo médio vira glúteo inteiro |
| Adução de quadril | 45 | adductors 29 | adutores 64% | glúteo 31% | nenhuma |
| Panturrilha (calf raise, calf press) | 103 | calves 101 | panturrilha 98% | nenhum >= 25% (sóleo, tornozelo e pés no resto) | soleus sem região |
| Abdominal (crunch, sit-up) | 224 | abs 223 | abdômen inteiro 100% | flexores do quadril 79%, oblíquos 63% | ênfase lowerAbs 27% |
| Elevação de pernas (leg/knee raise, leg lift) | 108 | abs 78 | abdômen inteiro 72% | flexores do quadril 79% | ênfase lowerAbs 43% |
| Prancha | 115 | abs 96 | abdômen inteiro 83% | deltoide 92%, glúteo 55%, oblíquos 53% | nenhuma |
| Rotação de tronco (twist, russian, woodchop, side bend) | 206 | abs 149 | abdômen inteiro 72% | oblíquos 90% | oblíquos nunca primários |
| Extensão lombar (back extension, hyperextension, superman) | 73 | spine 48, glutes 19 | lombar 66% | posteriores 85%, glúteo 68% | nenhuma |
| Pescoço (bodyPart neck) | 66 | levator scapulae 63 | upperTrapezius 100% | trapézio médio e inferior 76%, upper-back 48% | sternocleidomastoid não desenhável |
| Alongamento (category) | 466 | calves 63, glutes 49, hamstrings 39, quads 38 | sem padrão (o alvo é o músculo alongado) | sem padrão | |
| Cardio (category) | 145 | cardiovascular system 118 | nenhum | quadríceps 72%, panturrilha 59%, glúteo 48%, abdômen 41%, deltoide 38%, posteriores 34% | |
| Olímpicos (category) | 74 | glutes 34, delts 16, quads 11, traps 8 | glúteo 68%, quadríceps 34% | abdômen 72%, deltoide 66%, posteriores 65%, quadríceps 53%, antebraço 35%, trapézio 34% | 18 dos 74 são curados |

Leitura rápida: o catálogo é bom em "qual grupo" e fraco em "qual parte do grupo". Os únicos
sinais de sub-parte confiáveis são "lats" (puxadas), "rear deltoids" (famílias de deltoide
posterior e remadas), "rhomboids" (remadas, crucifixo invertido), "rotator cuff" (rotações e
elevações) e "lower abs" (elevações de perna, abdominais invertidos). "upper chest" é ruidoso.

## 9. Lacunas

### 9.1 O que o catálogo nomeia e o modelo não desenha

| Termo | Exercícios | Motivo | O que fazemos |
|---|---:|---|---|
| cardiovascular system | 172 (alvo) | não é músculo | primário vazio, secundários mantidos |
| ankles | 216 | tornozelo é pele no modelo | descartado |
| feet | 114 | pele | descartado |
| hands | 37 | pele | descartado |
| ankle stabilizers | 4 | pele (fibulares não existem no modelo) | descartado |
| sternocleidomastoid | 54 | pescoço é pele | descartado; flexões de pescoço ficam só com upperTrapezius |
| levator scapulae | 65 (alvo) | músculo profundo do pescoço | aproximado por upperTrapezius |
| brachialis | 156 | sem região própria | vira biceps |
| soleus | 105 | sem região própria (só calves) | vira calves |
| abductors | 90 (alvo) | glúteo médio/mínimo e TFL sem região própria | vira gluteal |
| grip muscles, wrist flexors, wrist extensors, wrists | 346 no total | antebraço é uma região só | vira forearm |
| groin, inner thighs | 117 | adutores é uma região só | vira adductors |
| spine, lower back | 168 + 601 | eretores; a coluna inteira não é desenhada | vira lowerBack |
| core | 1.885 | conceito, não músculo | vira abdômen (como no app); poderia incluir oblíquos |

### 9.2 O que o modelo desenha e o catálogo nunca separa

- **frontDeltoid e deltoids (lateral)**: o catálogo só tem "delts", "shoulders" e "deltoids"
  (os três juntos) e "rear deltoids". Toda elevação lateral, desenvolvimento e supino acende o
  deltoide inteiro.
- **chest (médio) e lowerChest**: só existe "upper chest". Nenhum exercício isola o peitoral
  inferior nem o médio.
- **upperAbs** sozinho: só existe "lower abs".
- **trapezius (médio) e lowerTrapezius** sozinhos: "traps" e "trapezius" são o músculo todo;
  só "levator scapulae" isola (por aproximação) o superior.
- **quadriceps (reto femoral), innerQuad, outerQuad**: só "quads"/"quadriceps", sempre os três.
- **obliques, hipFlexors, tibialis**: nunca são alvo (0 primários); aparecem só como
  secundários (695, 783 e 72 exercícios).
- **serratus**: alvo em só 15 exercícios e nunca secundário no texto (os 20 secundários vêm do
  `muscleMap`).

### 9.3 Regras por nome que poderiam preencher as lacunas (propostas, não aplicadas no JSON)

O JSON reflete só o que os dados dizem. Estas regras usam o nome do exercício e mudariam a cor
de sub-partes. Contagem = exercícios afetados hoje.

| Regra proposta | Efeito | Exercícios |
|---|---|---:|
| Nome com "incline" e peitoral inteiro no primário | upperChest primário, médio e inferior secundários | 58 (22 já têm ênfase) |
| Nome com "decline" e peitoral inteiro no primário | lowerChest primário | 28 |
| Empurrar (supino, chest press, flexão, mergulho, desenvolvimento, front raise) com deltoide inteiro aceso | estreitar para frontDeltoid | 516 (138 com deltoide no primário) |
| "lateral raise", "upright row", "side raise" (sem "rear") com deltoide primário | deltoids (lateral) primário | 69 |
| "rear delt", "reverse fly", "face pull", "pull apart" com deltoide primário | rearDeltoid primário | 91 |
| "external/internal/shoulder rotation" (sem stretch) com deltoide primário | rotatorCuff primário | 48 |
| "shrug" com trapézio inteiro primário | upperTrapezius primário | 35 |
| Remadas (sem upright) com trapézio inteiro no secundário | trapézio médio | 34 (outras 259 remadas não citam trapézio) |
| "y raise", "prone y" | lowerTrapezius | 15 |
| "crunch", "sit-up" sem ênfase | ênfase upperAbs | 163 |
| "leg raise", "knee raise", "reverse crunch", "leg lift" sem ênfase lowerAbs | ênfase lowerAbs | 39 (além dos 200 que os dados já dão) |
| "twist", "russian", "woodchop", "side bend", "oblique" | obliques promovidos a primário | 201 |
| "sumo", "wide stance", "plie" sem adutores no primário | adutores primário | 42 |

## 10. Como regenerar e conferir

```sh
cd "docs/research/research_notes/Sistema muscular para o HexGym"
python3 build_exercise_regions.py            # regrava exercise_regions.json (6.554 chaves)
python3 build_exercise_regions.py --report   # imprime contagens, termos, regiões e famílias
```

O script lê `catalogue/exercises/*.json`, o `SECONDARY_ADDITIONS` de
`frontend/src/lib/exercises.js` e as listas `TARGETS`/`SECONDARY` de
`scripts/catalogue/validate.mjs`. Não altera nenhum arquivo do repositório fora desta pasta.
Se o catálogo ganhar um termo novo, ele para com a lista dos termos sem mapeamento.

Licença do resultado: o JSON é derivado do texto do catálogo (MIT para os 1.324 de origem
ExerciseDB, AGPL para o resto e para o `muscleMap`). Como o HexGym é fork AGPL do openGym, pode
usar com a atribuição do `NOTICE.md`. Nada disso envolve a mídia da Gym visual.
