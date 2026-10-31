#!/usr/bin/env python3
"""Gera exercise_regions.json: para cada exercício do catálogo do openGym, as regiões do
manequim 3D do HexGym (regiões do MuscleMap, 31 por lado) que acendem como primárias
(violeta forte) e secundárias (violeta claro).

    python3 build_exercise_regions.py            escreve exercise_regions.json ao lado deste script
    python3 build_exercise_regions.py --report   também imprime as contagens usadas nas notas
    python3 build_exercise_regions.py --v2       modelo v2 (36 regiões pintadas por lado): escreve
                                                 exercise_regions_v2.json e regions_v2.json

Só lê texto (catalogue/exercises/*.json, frontend/src/lib/exercises.js e
scripts/catalogue/validate.mjs). Nunca abre nada de catalogue/media/: as imagens e animações
são licenciadas da Gym visual e não podem ser lidas nem passadas a ferramentas de IA. O nome do
arquivo de mídia é o id do exercício (media/still/<id>.webp, media/clip/<id>.mp4), então a
junção mídia -> músculos é pela chave do JSON, sem abrir mídia nenhuma.

Precedência, igual à do app (frontend/src/lib/muscles.js, weightsOf):
  1. "muscleMap": o muscleMap curado do catálogo. Com "weights", eles mandam (1 = primário,
     0 < w < 1 = secundário, 0 = associação explícita sem crédito, não acende). Sem weights,
     valem as listas primaries/secondaries. O muscleMap só fala em grupos (vocabulário do mapa
     2D); um grupo é estreitado para as sub-regiões que o texto livre do mesmo exercício nomeia,
     quando o texto só nomeia sub-partes daquele grupo (ex.: alvo "lats" -> só upperBack).
  2. "curated": texto livre mais o SECONDARY_ADDITIONS de exercises.js (sem muscleMap).
  3. "freetext": target -> primário; secondaryMuscles -> secundário.
  4. "bodypart": nada desenhável no texto; usa BY_BODYPART de muscles.js (maior peso ->
     primário, demais -> secundário). O app nunca chega aqui para exercícios do catálogo,
     porque conta "cardiovascular system" como pseudo-músculo; o modelo 3D não desenha isso.

Campos extras opcionais:
  "emphasis": sub-regiões que o texto livre nomeia dentro de um grupo que já está inteiro no
              primário (ex.: alvo "pectorals" + secundário "upper chest" -> ["upperChest"]).
              É uma dica de ênfase, não muda primary/secondary.
  "variantOf": o id é um desenho (figura feminina) de outro exercício; regiões copiadas dele.
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CATALOGUE = ROOT / 'catalogue' / 'exercises'
EXERCISES_JS = ROOT / 'frontend' / 'src' / 'lib' / 'exercises.js'
VALIDATE_MJS = ROOT / 'scripts' / 'catalogue' / 'validate.mjs'
OUT = HERE / 'exercise_regions.json'

# Os 18 grupos do app (ordem cabeça-pés de MUSCLES em muscles.js) e as regiões do MuscleMap.
# Atenção: "chest", "deltoids", "quadriceps" e "trapezius" são ao mesmo tempo nome de grupo
# (no app) e de UMA região (no modelo). Aqui uma região "chest" sozinha é só o peitoral médio.
GROUP_REGIONS = {
    'trapezius': ['upperTrapezius', 'trapezius', 'lowerTrapezius'],
    'deltoids': ['frontDeltoid', 'deltoids', 'rearDeltoid'],
    'chest': ['upperChest', 'chest', 'lowerChest'],
    'upper-back': ['upperBack', 'rhomboids', 'rotatorCuff'],
    'serratus': ['serratus'],
    'biceps': ['biceps'],
    'triceps': ['triceps'],
    'forearm': ['forearm'],
    'abs': ['upperAbs', 'lowerAbs'],
    'obliques': ['obliques'],
    'lower-back': ['lowerBack'],
    'gluteal': ['gluteal'],
    'quadriceps': ['quadriceps', 'innerQuad', 'outerQuad'],
    'hamstring': ['hamstring'],
    'adductors': ['adductors'],
    'hip-flexors': ['hipFlexors'],
    'calves': ['calves'],
    'tibialis': ['tibialis'],
}
V1_GROUP_REGIONS = GROUP_REGIONS
REGION_ORDER = [r for regions in GROUP_REGIONS.values() for r in regions]
GROUP_OF = {r: g for g, regions in GROUP_REGIONS.items() for r in regions}

G = GROUP_REGIONS
# Todo termo que o catálogo usa em "target" e "secondaryMuscles" -> regiões. [] = não desenhável.
TERM_REGIONS = {
    # alvos (target)
    'abs': G['abs'],
    'pectorals': G['chest'],
    'biceps': G['biceps'],
    'glutes': G['gluteal'],
    'delts': G['deltoids'],
    'triceps': G['triceps'],
    'upper back': G['upper-back'],
    'lats': ['upperBack'],
    'calves': G['calves'],
    'quads': G['quadriceps'],
    'forearms': G['forearm'],
    'hamstrings': G['hamstring'],
    'spine': G['lower-back'],
    'traps': G['trapezius'],
    'adductors': G['adductors'],
    'serratus anterior': G['serratus'],
    'abductors': G['gluteal'],             # glúteo médio/mínimo: o modelo só tem "gluteal"
    'levator scapulae': ['upperTrapezius'],  # fica sob o trapézio superior; pescoço é pele
    'cardiovascular system': [],
    # secundários (secondaryMuscles)
    'shoulders': G['deltoids'],
    'deltoids': G['deltoids'],
    'rear deltoids': ['rearDeltoid'],
    'rotator cuff': ['rotatorCuff'],
    'chest': G['chest'],
    'upper chest': ['upperChest'],
    'brachialis': G['biceps'],             # sem região própria; o app também manda para bíceps
    'wrists': G['forearm'],
    'wrist flexors': G['forearm'],
    'wrist extensors': G['forearm'],
    'grip muscles': G['forearm'],
    'back': G['upper-back'],               # genérico; o app manda para upper-back
    'latissimus dorsi': ['upperBack'],
    'rhomboids': ['rhomboids'],
    'trapezius': G['trapezius'],
    'lower back': G['lower-back'],
    'core': G['abs'],                      # o app manda "core" só para abs (sem oblíquos)
    'abdominals': G['abs'],
    'obliques': G['obliques'],
    'lower abs': ['lowerAbs'],
    'hip flexors': G['hip-flexors'],
    'quadriceps': G['quadriceps'],
    'inner thighs': G['adductors'],
    'groin': G['adductors'],
    'soleus': G['calves'],                 # sem região própria (gastrocnêmio e sóleo juntos)
    'shins': G['tibialis'],
    'ankles': [], 'ankle stabilizers': [], 'feet': [], 'hands': [],
    'sternocleidomastoid': [],             # pescoço é pele no modelo
}


def is_subpart(term):
    """True quando o termo acende só parte de um grupo (ex.: "upper chest", "lats")."""
    regions = TERM_REGIONS[term]
    return bool(regions) and set(regions) < set(G[GROUP_OF[regions[0]]])


# ---------------------------------------------------------------- modelo v2

# v2: sete regiões novas por lado. O manguito passa a contar no ombro (como no app) e o redondo
# maior, separado, nas costas. "neck" é grupo só do boneco: no Watch e no widget fica inerte.
V2_GROUP_REGIONS = {
    'trapezius': ['upperTrapezius', 'trapezius', 'lowerTrapezius'],
    'deltoids': ['frontDeltoid', 'deltoids', 'rearDeltoid', 'rotatorCuff'],
    'chest': ['upperChest', 'chest', 'lowerChest'],
    'upper-back': ['upperBack', 'teresMajor', 'rhomboids'],
    'serratus': ['serratus'],
    'biceps': ['biceps', 'brachialis'],
    'triceps': ['tricepsLongHead', 'triceps'],
    'forearm': ['forearm'],
    'abs': ['upperAbs', 'lowerAbs'],
    'obliques': ['obliques'],
    'lower-back': ['lowerBack'],
    'gluteal': ['gluteal', 'gluteusMedius'],
    'quadriceps': ['quadriceps', 'innerQuad', 'outerQuad'],
    'hamstring': ['hamstring'],
    'adductors': ['adductors'],
    'hip-flexors': ['hipFlexors'],
    'calves': ['calves', 'soleus'],
    'tibialis': ['tibialis'],
    'neck': ['sternocleidomastoid', 'neckBack'],
}
V2_NEW = ['gluteusMedius', 'soleus', 'brachialis', 'teresMajor', 'sternocleidomastoid', 'neckBack', 'tricepsLongHead']
# Quando o muscleMap nomeia o grupo e o texto não estreita, estas regiões NÃO acendem sozinhas:
# só por nome (manguito, braquial, glúteo médio). O resto do grupo acende inteiro.
V2_BY_NAME_ONLY = {'rotatorCuff', 'brachialis', 'gluteusMedius'}
V2_HEADS = ['frontDeltoid', 'deltoids', 'rearDeltoid']
V2_TERM_CHANGES = {
    'delts': V2_HEADS, 'shoulders': V2_HEADS, 'deltoids': V2_HEADS,
    'biceps': ['biceps'],
    'brachialis': ['brachialis'],
    'glutes': ['gluteal'],
    'abductors': ['gluteusMedius'],
    'soleus': ['soleus'],
    'lats': ['upperBack', 'teresMajor'],
    'latissimus dorsi': ['upperBack', 'teresMajor'],
    'sternocleidomastoid': ['sternocleidomastoid'],
    'levator scapulae': ['neckBack'],
}
# Nome no app (os 18 grupos do Watch e do widget) e nome em português de cada região pintada.
V2_REGION_PT = {
    'upperTrapezius': 'Trapézio superior', 'trapezius': 'Trapézio médio', 'lowerTrapezius': 'Trapézio inferior',
    'frontDeltoid': 'Deltoide frontal', 'deltoids': 'Deltoide lateral', 'rearDeltoid': 'Deltoide posterior',
    'rotatorCuff': 'Manguito rotador', 'upperChest': 'Peito alto', 'chest': 'Peito médio', 'lowerChest': 'Peito baixo',
    'upperBack': 'Dorsal', 'teresMajor': 'Redondo maior', 'rhomboids': 'Romboides', 'serratus': 'Serrátil anterior',
    'biceps': 'Bíceps', 'brachialis': 'Braquial', 'tricepsLongHead': 'Tríceps, cabeça longa',
    'triceps': 'Tríceps, cabeças lateral e medial', 'forearm': 'Antebraço', 'upperAbs': 'Reto abdominal',
    'lowerAbs': 'Abdômen baixo', 'obliques': 'Oblíquo externo', 'lowerBack': 'Lombar',
    'gluteal': 'Glúteo máximo', 'gluteusMedius': 'Glúteo médio', 'quadriceps': 'Reto femoral',
    'innerQuad': 'Vasto medial', 'outerQuad': 'Vasto lateral', 'hamstring': 'Posterior de coxa',
    'adductors': 'Adutores', 'hipFlexors': 'Flexores do quadril', 'calves': 'Gastrocnêmio', 'soleus': 'Sóleo',
    'tibialis': 'Tibial anterior', 'sternocleidomastoid': 'Esternocleidomastóideo',
    'neckBack': 'Nuca (esplênios e levantador da escápula)',
}
V2_DEFAULT = {}   # grupo -> regiões quando o muscleMap nomeia o grupo sem estreitar (preenchido em use_v2)


def use_v2():
    """Troca as tabelas do módulo pelas da v2 (as funções leem os globais na hora da chamada)."""
    global GROUP_REGIONS, REGION_ORDER, GROUP_OF, G, TERM_REGIONS, OUT
    GROUP_REGIONS = V2_GROUP_REGIONS
    REGION_ORDER = [r for regions in GROUP_REGIONS.values() for r in regions]
    GROUP_OF = {r: g for g, regions in GROUP_REGIONS.items() for r in regions}
    G = GROUP_REGIONS
    old = TERM_REGIONS
    TERM_REGIONS = {}
    for t, regs in old.items():   # termo que apontava para um grupo inteiro aponta para o grupo v2
        whole = next((g for g, rr in V1_GROUP_REGIONS.items() if regs and set(regs) == set(rr)), None)
        TERM_REGIONS[t] = list(G[whole]) if whole else list(regs)
    TERM_REGIONS['rotator cuff'] = ['rotatorCuff']
    TERM_REGIONS.update(V2_TERM_CHANGES)
    V2_DEFAULT.update({g: [r for r in rr if r not in V2_BY_NAME_ONLY] for g, rr in G.items()})
    OUT = HERE / 'exercise_regions_v2.json'


NECK_SIDE = re.compile(r'side|lateral|inclination')
def v2_name_rules(e, p, s):
    """Regras por nome da v2 (relatório, seção de regras). Mudam primário e secundário."""
    n = e['name'].lower()
    stretch = 'stretch' in n or e.get('category') == 'stretching'
    if re.search(r'abduct', n) and 'gluteusMedius' in p and 'gluteal' in p:
        p.discard('gluteal'); s.add('gluteal')                         # abdução: médio, não máximo
    if re.search(r'seated.*calf|calf.*seated', n) and not stretch and 'calves' in p:
        p.discard('calves'); p.add('soleus'); s.add('calves')          # joelho dobrado: sóleo
    if e['target'] == 'triceps' and re.search(r'overhead|french|behind (the )?head|above head', n) and not stretch:
        if 'triceps' in p:
            p.discard('triceps'); p.add('tricepsLongHead'); s.add('triceps')
    if re.search(r'\bcurl', n) and not re.search(r'wrist|leg|hamstring|calf|nordic|toe', n):
        if 'hammer' in n:
            p |= {'brachialis', 'forearm'}
        elif re.search(r'reverse', n):
            if 'biceps' in p:
                p.discard('biceps'); s.add('biceps')
            p |= {'brachialis', 'forearm'}
    if e['bodyPart'] == 'neck' and not stretch:
        flex, ext = 'flexion' in n, 'extension' in n or 'bridge' in n
        if NECK_SIDE.search(n) and (flex or re.search(r'raise|lifting|bend', n)):
            p.clear(); p |= {'sternocleidomastoid', 'neckBack'}
        elif flex and ext:
            p.clear(); p |= {'sternocleidomastoid', 'neckBack'}
        elif flex:
            p.clear(); p.add('sternocleidomastoid'); s.clear()
        elif ext:
            p.clear(); p.add('neckBack'); s.clear(); s.add('upperTrapezius')
    s -= p
    return p, s


def write_regions_v2():
    """regions_v2.json: cada região pintada, seu grupo no boneco e o grupo que o Watch mostra."""
    rows = [{'region': r, 'name': V2_REGION_PT[r], 'group': g, 'watchGroup': None if g == 'neck' else g,
             'new': r in V2_NEW} for g, rr in V2_GROUP_REGIONS.items() for r in rr]
    path = HERE / 'regions_v2.json'
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    return rows


# BY_BODYPART de muscles.js (fallback do app), com os mesmos pesos.
BY_BODYPART = {
    'chest': {'chest': 1},
    'back': {'upper-back': 0.75, 'lower-back': 0.25},
    'shoulders': {'deltoids': 1},
    'upper arms': {'biceps': 0.5, 'triceps': 0.5},
    'lower arms': {'forearm': 1},
    'waist': {'abs': 0.7, 'obliques': 0.3},
    'upper legs': {'quadriceps': 0.4, 'hamstring': 0.35, 'gluteal': 0.25},
    'lower legs': {'calves': 0.8, 'tibialis': 0.2},
    'neck': {'trapezius': 1},
    'full body': {'chest': 0.2, 'upper-back': 0.2, 'gluteal': 0.2, 'quadriceps': 0.2, 'hamstring': 0.1, 'abs': 0.1},
    'cardio': {},
}


def ordered(regions):
    s = set(regions)
    return [r for r in REGION_ORDER if r in s]


def read_vocabulary():
    """TARGETS e SECONDARY de validate.mjs: falha se surgir um termo que este script não conhece."""
    src = VALIDATE_MJS.read_text(encoding='utf-8')
    out = {}
    for name in ('TARGETS', 'SECONDARY'):
        m = re.search(r"export const %s = list\('([^']*)'\)" % name, src)
        if not m:
            sys.exit(f'não achei {name} em {VALIDATE_MJS}')
        out[name] = [t.strip() for t in m.group(1).split(',') if t.strip()]
    return out


def read_secondary_additions():
    """O SECONDARY_ADDITIONS de exercises.js (secundários extras que o app aplica por cima)."""
    src = EXERCISES_JS.read_text(encoding='utf-8')
    m = re.search(r'const SECONDARY_ADDITIONS = \{(.*?)\n\}', src, re.S)
    if not m:
        return {}
    out = {}
    for id_, items in re.findall(r"'(\d+)':\s*\[([^\]]*)\]", m.group(1)):
        out[id_] = re.findall(r"'([^']+)'", items)
    return out


def load_catalogue():
    exercises, variants = {}, {}
    for path in sorted(CATALOGUE.glob('*.json')):
        e = json.loads(path.read_text(encoding='utf-8'))
        (variants if e.get('variantOf') else exercises)[e['id']] = e
    return exercises, variants


def regions_of_terms(terms):
    out = set()
    for t in terms:
        out |= set(TERM_REGIONS[t])
    return out


def emphasis_of(primary, sub_terms):
    """Sub-regiões nomeadas dentro de grupos que estão inteiros no primário."""
    out = set()
    for t in sub_terms:
        regs = set(TERM_REGIONS[t])
        group = set(G[GROUP_OF[next(iter(regs))]])
        if group <= primary:
            out |= regs
    return out


def from_freetext(e, extra):
    sec_terms = list(dict.fromkeys(e['secondaryMuscles'] + extra))
    primary = set(TERM_REGIONS[e['target']])
    secondary = regions_of_terms(sec_terms) - primary
    emph = emphasis_of(primary, [t for t in sec_terms if is_subpart(t)])
    return primary, secondary, emph


def refine_group(group, text_terms):
    """Regiões de um grupo do muscleMap, estreitadas pelo texto livre quando ele só nomeia sub-partes."""
    full = set(V2_DEFAULT.get(group) or G[group])
    named = [t for t in text_terms if TERM_REGIONS[t] and GROUP_OF[TERM_REGIONS[t][0]] == group]
    if not named or any(not is_subpart(t) for t in named):
        return full
    return regions_of_terms(named)


def from_musclemap(e, extra):
    m = e['muscleMap']
    weights = m.get('weights')
    if weights:
        pg = [g for g, w in weights.items() if w >= 1]
        sg = [g for g, w in weights.items() if 0 < w < 1]
    else:
        pg = list(m.get('primaries') or [])
        sg = [g for g in (m.get('secondaries') or []) if g not in pg]
    text_terms = list(dict.fromkeys([e['target']] + e['secondaryMuscles'] + extra))
    primary, secondary = set(), set()
    for g in pg:
        primary |= refine_group(g, text_terms)
    for g in sg:
        secondary |= refine_group(g, text_terms)
    secondary -= primary
    emph = emphasis_of(primary, [t for t in text_terms if is_subpart(t)])
    return primary, secondary, emph


def from_bodypart(e):
    bp = (e.get('muscleMap') or {}).get('bodyPart') or e['bodyPart']
    weights = BY_BODYPART.get(bp) or {}
    if not weights:
        return set(), set()
    top = max(weights.values())
    primary = {r for g, w in weights.items() if w == top for r in G[g]}
    secondary = {r for g, w in weights.items() if w < top for r in G[g]}
    return primary, secondary


def build():
    vocab = read_vocabulary()
    unknown = [t for t in vocab['TARGETS'] + vocab['SECONDARY'] if t not in TERM_REGIONS]
    if unknown:
        sys.exit('termos novos no catálogo sem mapeamento em TERM_REGIONS: ' + ', '.join(unknown))
    additions = read_secondary_additions()
    exercises, variants = load_catalogue()

    out = {}
    for id_, e in exercises.items():
        extra = [t for t in additions.get(id_, []) if t not in e['secondaryMuscles']]
        if e.get('muscleMap'):
            p, s, emph = from_musclemap(e, extra)
            source = 'muscleMap'
        else:
            p, s, emph = from_freetext(e, extra)
            source = 'curated' if extra else 'freetext'
        if not p and not s:
            p, s = from_bodypart(e)
            emph = set()
            source = 'bodypart'
        if V2_DEFAULT:
            p, s = v2_name_rules(e, set(p), set(s))
        row = {'name': e['name'], 'primary': ordered(p), 'secondary': ordered(s), 'source': source}
        if emph:
            row['emphasis'] = ordered(emph)
        out[id_] = row
    for id_, v in variants.items():
        base = out[v['variantOf']]
        out[id_] = {**base, 'variantOf': v['variantOf']}
    return dict(sorted(out.items(), key=lambda kv: (int(kv[0]), kv[0]))), exercises, additions


def write(rows):
    lines = [f'  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}' for k, v in rows.items()]
    OUT.write_text('{\n' + ',\n'.join(lines) + '\n}\n', encoding='utf-8')


# ---------------------------------------------------------------- relatório (--report)

LEG = r'leg curl|hamstring|nordic|leg extension'
FAMILIES = [  # (rótulo, regex no nome em minúsculas, regex de exclusão, categoria)
    ('supino / chest press (bench|chest|floor press)', r'bench press|chest press|floor press', None, None),
    ('inclinado (incline)', r'\bincline\b', None, None),
    ('declinado (decline)', r'\bdecline\b', None, None),
    ('crucifixo / fly (fly|flye|crossover|pec deck)', r'\bfly\b|\bflye|crossover|pec deck', r'rear|reverse', None),
    ('flexão de braço (push-up)', r'push[- ]?up', None, None),
    ('mergulho (dip)', r'\bdips?\b', None, None),
    ('desenvolvimento (shoulder/overhead/military/arnold/push press)', r'shoulder press|overhead press|military press|arnold press|push press', None, None),
    ('elevação lateral (lateral raise)', r'lateral raise', r'rear', None),
    ('remada alta (upright row)', r'upright row', None, None),
    ('elevação frontal (front raise)', r'front raise', None, None),
    ('deltoide posterior (rear delt|reverse/rear fly|face pull|pull apart)', r'rear delt|reverse fly|rear fly|face pull|pull apart|rear lateral', None, None),
    ('rotação de ombro (external/internal rotation)', r'external rotation|internal rotation|shoulder rotation', r'stretch', None),
    ('remada (row, sem upright)', r'\brows?\b', r'upright', None),
    ('puxada / barra (pulldown|pull-up|chin-up)', r'pulldown|pull[- ]?down|pull[- ]?up|chin[- ]?up', None, None),
    ('pullover', r'pullover', None, None),
    ('encolhimento (shrug)', r'\bshrug', None, None),
    ('rosca (curl, sem leg curl)', r'\bcurl', LEG, None),
    ('tríceps (triceps|pushdown|kickback|skull crusher)', r'triceps|pushdown|push-down|kickback|skull', LEG, None),
    ('agachamento (squat)', r'\bsquat', None, None),
    ('afundo (lunge|split squat|step-up)', r'\blunge|split squat|step[- ]?up', None, None),
    ('terra / stiff (deadlift|rdl|romanian|good morning)', r'deadlift|\brdl\b|romanian|good morning', None, None),
    ('elevação de quadril (hip thrust|bridge)', r'hip thrust|glute bridge|\bbridge\b', None, None),
    ('leg press', r'leg press', None, None),
    ('cadeira extensora (leg extension)', r'leg extension', None, None),
    ('mesa flexora (leg curl|nordic)', r'leg curl|hamstring curl|nordic', None, None),
    ('abdução de quadril (abduction)', r'abduct', None, None),
    ('adução de quadril (adduction)', r'adduct', None, None),
    ('panturrilha (calf raise|calf press)', r'\bcalf\b', r'stretch', None),
    ('abdominal (crunch|sit-up)', r'crunch|sit[- ]?up', None, None),
    ('elevação de pernas (leg raise|knee raise|leg lift)', r'leg raise|knee raise|leg lift', None, None),
    ('prancha (plank)', r'\bplank', None, None),
    ('rotação de tronco (twist|russian|woodchop|side bend)', r'twist|russian|wood ?chop|side bend', None, None),
    ('extensão lombar (back extension|hyperextension|superman)', r'back extension|hyperextension|superman', None, None),
    ('pescoço (bodyPart neck)', None, None, 'bp:neck'),
    ('alongamento (category stretching)', None, None, 'stretching'),
    ('cardio (category cardio)', None, None, 'cardio'),
    ('olímpicos (category olympic)', None, None, 'olympic'),
]


def family_members(exercises, rx, exclude, cat):
    out = []
    for e in exercises.values():
        n = e['name'].lower()
        if cat and cat.startswith('bp:'):
            if e['bodyPart'] != cat[3:]:
                continue
        elif cat:
            if e['category'] != cat:
                continue
        if rx and not re.search(rx, n):
            continue
        if exclude and re.search(exclude, n):
            continue
        out.append(e)
    return out


def report(rows, exercises, additions):
    ex_rows = {k: v for k, v in rows.items() if 'variantOf' not in v}
    n = len(ex_rows)
    print(f'# exercícios: {n}; desenhos variantes: {len(rows) - n}; total de chaves: {len(rows)}')
    print('fontes:', dict(collections.Counter(v['source'] for v in ex_rows.values())))
    print('com >=1 região primária:', sum(1 for v in ex_rows.values() if v['primary']))
    print('sem primária mas com secundária:', sum(1 for v in ex_rows.values() if not v['primary'] and v['secondary']))
    print('sem nenhuma região:', sum(1 for v in ex_rows.values() if not v['primary'] and not v['secondary']))

    def partial(regs):
        by = collections.defaultdict(set)
        for r in regs:
            by[GROUP_OF[r]].add(r)
        return {g for g, rs in by.items() if rs < set(G[g])}
    sub_any = sub_p = 0
    for v in ex_rows.values():
        pp = partial(v['primary'])
        ss = partial([r for r in v['secondary']])
        if pp or ss:
            sub_any += 1
        if pp:
            sub_p += 1
    print('acendem sub-parte (algum grupo parcial em primary ou secondary):', sub_any, '| no primário:', sub_p)
    print('com emphasis:', sum(1 for v in ex_rows.values() if v.get('emphasis')))

    # termos: quantos exercícios cada termo acende, por papel
    tc, sc = collections.Counter(), collections.Counter()
    for id_, e in exercises.items():
        tc[e['target']] += 1
        for t in set(e['secondaryMuscles'] + additions.get(id_, [])):
            sc[t] += 1
    print('\n## termos (exercícios como alvo / como secundário) -> regiões')
    for t in sorted(TERM_REGIONS, key=lambda t: -(tc[t] + sc[t])):
        mark = ' [sub-parte]' if is_subpart(t) else ''
        print(f'  {t}: alvo={tc[t]} sec={sc[t]} -> {TERM_REGIONS[t]}{mark}')

    print('\n## regiões (exercícios que acendem como primária / secundária)')
    rp = collections.Counter(r for v in ex_rows.values() for r in v['primary'])
    rs = collections.Counter(r for v in ex_rows.values() for r in v['secondary'])
    for r in REGION_ORDER:
        print(f'  {r}: primária={rp[r]} secundária={rs[r]}')

    print('\n## famílias (regiões primárias >= 30%, secundárias >= 25% dos membros)')
    for label, rx, exclude, cat in FAMILIES:
        mem = family_members(exercises, rx, exclude, cat)
        if not mem:
            continue
        k = len(mem)
        pc = collections.Counter(r for e in mem for r in rows[e['id']]['primary'])
        sc2 = collections.Counter(r for e in mem for r in rows[e['id']]['secondary'])
        ec = collections.Counter(r for e in mem for r in rows[e['id']].get('emphasis', []))
        tg = collections.Counter(e['target'] for e in mem)
        src = collections.Counter(rows[e['id']]['source'] for e in mem)
        fmt = lambda c, lim: ', '.join(f'{r} {round(100 * x / k)}%' for r, x in c.most_common() if x / k >= lim)
        print(f'- {label}: n={k}; alvos={dict(tg.most_common(4))}; fontes={dict(src)}')
        print(f'    primárias: {fmt(pc, 0.30)}')
        print(f'    secundárias: {fmt(sc2, 0.25)}')
        if ec:
            print(f'    ênfase: {fmt(ec, 0.05)}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--v2', action='store_true', help='modelo v2: regiões novas e regras por nome')
    args = ap.parse_args()
    if args.v2:
        use_v2()
        print(f'regions_v2.json: {len(write_regions_v2())} regiões pintadas por lado', file=sys.stderr)
    rows, exercises, additions = build()
    write(rows)
    print(f'{OUT.name}: {len(rows)} chaves escritas', file=sys.stderr)
    if args.report:
        report(rows, exercises, additions)


if __name__ == '__main__':
    main()
