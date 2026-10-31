# Inventário anatômico dos músculos esqueléticos para treino e para o boneco musculado, e lacunas do nosso modelo 3D

Notas de pesquisa em português do Brasil. Legenda usada nas tabelas:

- **Camada:** S = superficial (molda a pele de uma figura magra); P = profundo (só dá para representar como a área por cima dele); S/P = parte aparece, parte fica coberta.
- **Visível:** F = frente, C = costas, L = lado, numa figura magra em pé. "Não" = nunca aparece na superfície.
- **Ação:** texto das ações tirado da [lista de músculos da Wikipedia][wp] (colunas "Action" e "Location"), traduzido e resumido. Quando a ação de uma cabeça ou parte não estava nessa fonte, está marcada com (†) e vale como anatomia de referência não reconferida nesta pesquisa.
- **Treino (academia):** exercícios que carregam o músculo. Esta coluna é **inferida** a partir da ação articular citada e, onde existe, das marcações do nosso catálogo de exercícios ([catalogue/exercises][cat], contagens de `target` e `secondaryMuscles` levantadas em 31/10/2026). Não achei uma fonte de exercícios acessível (ExRx e MuscleWiki devolveram 403).
- **Nosso modelo:** onde o músculo cai hoje entre as 31 regiões por lado do boneco 3D. "Inerte" = parte desenhada como silhueta (cabeça, pescoço, mãos, pés, joelhos, tornozelos).
- **Nomes PT-BR:** conferidos contra a [lista de músculos da Wikipedia em português][ptwp] e contra os rótulos das duas cartas anatômicas que o Lipe enviou (vista frontal). A Wikipedia PT ainda usa grafia anterior ao Acordo Ortográfico (deltóide, rombóide, supraespinhal); aqui uso a grafia atual do Brasil (deltoide, romboide) e registro a variante.

## 1. Inventário região por região: camada, visibilidade, ações e movimentos de academia

### Takeaway
O corpo tem cerca de 70 músculos ou partes que importam para treino ou para a silhueta de uma figura magra; cerca de 45 deles são superficiais e moldam a pele. Os profundos que mais importam para treino (manguito rotador anterior e superior, quadrado lombar, transverso e oblíquo interno, glúteo mínimo e rotadores laterais, iliopsoas, vasto intermédio, tibial posterior, sóleo em parte) só podem ser mostrados como a área por cima deles.

### Cited Findings

#### Cabeça e face (só uma linha, sem relevância de treino)
- **Frontal** (ventre frontal do occipitofrontal, *frontalis*): S, F; enruga a testa e eleva as sobrancelhas, segundo a [lista da Wikipedia][wp]. Aparece na carta frontal enviada pelo Lipe. Outros da face e mastigação (temporal, masseter, orbicular) ficam fora do escopo. Nosso modelo: cabeça inerte, correto para um boneco sem rosto.

#### Pescoço

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| esternocleidomastóideo | *sternocleidomastoideus* / sternocleidomastoid | S | F, L (o "V" do pescoço) | inclina a cabeça para o próprio lado, gira o rosto para o lado oposto, flete o pescoço; eleva o esterno na inspiração forçada ([WP][wp]) | flexão de pescoço com anilha ou faixa, máquina 4 direções; estabiliza em abdominais e na ponte; no catálogo aparece em 54 exercícios como secundário ([cat][cat]) | **ausente** (pescoço inerte); no código o nome cai em `null` e é descartado ([muscles.js][muscles]) |
| platisma | *platysma* | S (lâmina fina) | F | expressão facial, sem carga de treino (anatomia de referência †) | nenhum | ausente, correto |
| escalenos anterior, médio, posterior | *scalenus anterior, medius, posterior* | P (parte lateral aparece no triângulo posterior) | L, discreto | elevam a 1ª e 2ª costelas; com a costela fixa, fletem e inclinam o pescoço e giram para o lado oposto ([WP][wp]) | flexão lateral de pescoço; respiração | ausente |
| esplênio da cabeça e esplênio do pescoço (cervical) | *splenius capitis / cervicis* | P sob trapézio e ECM, aparece no triângulo posterior | C, L | estende, gira e inclina a cabeça ([WP][wp]) | extensão de pescoço com faixa ou máquina; isometria em levantamento terra e remadas | ausente |
| semiespinal da cabeça | *semispinalis capitis* | P | não (área: nuca, ao lado da linha média) | estende a cabeça ([WP][wp]) | extensão de pescoço | ausente |
| levantador da escápula | *levator scapulae* | P sob trapézio e ECM; faixa aparece de lado | L, C (discreto) | eleva a escápula e gira a cavidade glenoidal para baixo ([WP][wp]) | encolhimento de ombros (shrug), remadas altas; no catálogo é **alvo principal** de 65 exercícios ([cat][cat]) | **fundido** no trapézio superior (o código mapeia `levator scapulae` para `trapezius`, [muscles.js][muscles]) |
| suboccipitais, retos e oblíquos da cabeça | *suboccipitales* | P | não | movimentos finos da cabeça (†) | nenhum específico | ausente, correto |

#### Cintura escapular e ombro

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| trapézio, parte descendente (superior) | *trapezius pars descendens* | S | C, L, F (borda acima da clavícula) | eleva e ajuda a girar a escápula para cima ([WP][wp], que divide o trapézio em parte descendente e partes transversa e ascendente) | encolhimento, remada alta, carregada do fazendeiro, desenvolvimento | trapézio superior, ok |
| trapézio, parte transversa (média) | *pars transversa* | S | C | retrai (aduz) a escápula ([WP][wp]) | remadas, face pull, crucifixo invertido | trapézio médio, ok |
| trapézio, parte ascendente (inferior) | *pars ascendens* | S | C | deprime a escápula e ajuda a rotação para cima ([WP][wp]) | Y deitado, face pull, puxada com escápula deprimida, desenvolvimento | trapézio inferior, ok |
| deltoide anterior (parte clavicular) | *deltoideus pars clavicularis* | S | F, L | o deltoide como um todo abduz, flete e estende o ombro ([WP][wp]); a parte anterior flete e roda medialmente † | desenvolvimento, elevação frontal, supino inclinado | deltoide anterior, ok |
| deltoide lateral (parte acromial) | *pars acromialis* | S | L, F, C | abdução do ombro † | elevação lateral, remada alta, desenvolvimento | deltoide lateral, ok |
| deltoide posterior (parte espinal) | *pars spinalis* | S | C, L | extensão e abdução horizontal do ombro, rotação lateral † | crucifixo invertido, face pull, remadas | deltoide posterior, ok |
| supraespinal (também grafado supraespinhal) | *supraspinatus* | P sob trapézio e deltoide | não (área: fossa acima da espinha da escápula, sob o trapézio superior e médio) | abduz e estabiliza o úmero; parte do manguito rotador ([WP][wp]) | elevação lateral, "full can", rotação de manguito | ausente como região própria |
| infraespinal (também infraespinhal) | *infraspinatus* | S/P (meio da escápula aparece entre trapézio, deltoide e redondos) | C | rotação lateral, adução e estabilização do úmero ([WP][wp]) | rotação externa com cabo ou elástico, face pull | "área do manguito rotador", ok |
| redondo menor | *teres minor* | S/P | C | rotação lateral e adução do úmero ([WP][wp]) | rotação externa | "área do manguito rotador", ok |
| redondo maior | *teres major* | S | C, L (volume na borda lateral baixa da escápula, acima do latíssimo) | rotação medial do úmero ([WP][wp]); acompanha o latíssimo na adução e extensão do ombro † | puxada, barra fixa, remadas, pullover | **fundido** com o manguito (infraespinal) na mesma área, embora gire o úmero no sentido oposto |
| subescapular | *subscapularis* | P (face anterior da escápula) | não | rotação medial e estabilização do ombro ([WP][wp]) | rotação interna com cabo; estabilizador em supino e puxadas | ausente (não dá para desenhar) |
| romboide maior e romboide menor | *rhomboideus major / minor* | P sob o trapézio médio (contorno pode aparecer em figura muito magra) | C | retraem a escápula, giram para baixo a cavidade glenoidal, fixam a escápula no tórax ([WP][wp]) | remadas, face pull, retração escapular; 375 exercícios do catálogo o citam como secundário ([cat][cat]) | romboides, ok |
| serrátil anterior | *serratus anterior* | S | L, F (os "dentes" sob a axila) | protrai e estabiliza a escápula, ajuda a rotação para cima ([WP][wp]) | flexão de braço com "plus", soco, desenvolvimento, pullover; alvo de 15 exercícios ([cat][cat]) | serrátil, ok |
| peitoral menor | *pectoralis minor* | P sob o peitoral maior | não | puxa a escápula para frente e para baixo contra o tórax ([WP][wp]) | paralelas, flexões, supino (estabilizador) | dentro da área do peito |
| subclávio | *subclavius* | P | não | deprime a clavícula ([WP][wp]) | nenhum específico | ausente, correto |

#### Peito

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| peitoral maior, parte clavicular | *pectoralis major pars clavicularis* | S | F, L | o peitoral aduz e roda medialmente o úmero; a parte clavicular **flete** o úmero ([WP][wp]) | supino inclinado, crucifixo inclinado, elevação frontal; "upper chest" é secundário em 279 exercícios ([cat][cat]) | peito superior, ok |
| peitoral maior, parte esternocostal | *pars sternocostalis* | S | F, L | aduz, roda medialmente e **estende** o úmero a partir da flexão ([WP][wp]) | supino reto, crucifixo, crossover, flexão de braço | peito médio, ok |
| peitoral maior, parte abdominal | *pars abdominalis* | S | F | adução e extensão a partir da flexão † | supino declinado, paralelas, crossover de cima para baixo | peito inferior, ok |
| coracobraquial | *coracobrachialis* | P (axila; aparece só com o braço elevado) | não, ou F com braço erguido | flete e aduz o ombro ([WP][wp]) | crucifixo, elevação frontal | ausente |

#### Costas superiores e médias

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| latíssimo do dorso (grande dorsal) | *latissimus dorsi* | S | C, L, F (bordas laterais abaixo da axila) | estende, roda medialmente e aduz o úmero ([WP][wp]); o [Kenhub][kenhub-dorso] o descreve como músculo superficial do dorso, com partes vertebral, ilíaca, costal, escapular e umeral, e registra o nome alternativo "grande dorsal" | barra fixa, puxada, remadas, pullover; estabiliza o terra | lats, ok |
| serrátil posterior superior e inferior | *serratus posterior* | P | não | respiração (†) | nenhum | ausente, correto |

O [artigo de costas do Hevy][hevy-back] lista como músculos principais das costas: latíssimo do dorso, trapézio superior, médio e inferior, redondo maior e menor, eretor da espinha e romboides.

#### Lombar e coluna

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| eretor da espinha: iliocostal, longuíssimo, espinal | *erector spinae* | camada intermediária dos músculos profundos do dorso ([Kenhub][kenhub-ee]), mas só coberto por fáscia na região lombar | C (as duas colunas ao lado da coluna lombar) | iliocostal e longuíssimo estendem ou inclinam a coluna; o longuíssimo da cabeça inclina cabeça e pescoço para o mesmo lado ([WP][wp]) | levantamento terra, extensão lombar, good morning, agachamento (isometria); "spine" é alvo de 168 exercícios e "lower back" secundário de 601 ([cat][cat]) | lombar, ok |
| multífidos e demais transversoespinais | *multifidus* | P | não | estabiliza as vértebras em movimentos locais da coluna ([WP][wp]) | bird dog, prancha, terra | dentro da lombar |
| quadrado lombar | *quadratus lumborum* | P (lateral e à frente do eretor) | não (área: flanco lombar entre a última costela e a crista ilíaca) | flete o tronco para o mesmo lado, fixa a 12ª costela, estende o tronco ([WP][wp]) | flexão lateral com halter, carregada unilateral (suitcase carry), prancha lateral | ausente (cai entre lombar e oblíquos) |

#### Parede abdominal e core

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| reto do abdome (reto do abdômen, reto abdominal) | *rectus abdominis* | S | F | flete o tronco, comprime as vísceras, ajuda a expiração ([WP][wp]) | abdominal crunch, elevação de pernas, roda abdominal, prancha (anti-extensão); "lower abs" é secundário em 209 exercícios ([cat][cat]) | 3 fileiras do "tanquinho" + abdome inferior, ok |
| piramidal | *pyramidalis* | S (pequeno, base do reto) | não | tensiona a linha alba (†) | nenhum | dentro do abdome inferior |
| oblíquo externo do abdome | *obliquus externus abdominis* | S | L, F | flete o tronco para o mesmo lado, gira para o lado oposto, comprime as vísceras ([WP][wp]) | prancha lateral, lenhador (woodchop), Pallof, elevação de pernas oblíqua, carregadas | oblíquos, ok |
| oblíquo interno do abdome | *obliquus internus abdominis* | P sob o externo | não | flexão lateral e rotação do tronco, compressão ([WP][wp]; ver lacuna sobre o lado da rotação) | os mesmos do externo | dentro dos oblíquos |
| transverso do abdome | *transversus abdominis* | P | não | comprime as vísceras e ajuda a expiração ([WP][wp]) | vácuo abdominal, bracing, dead bug, prancha | dentro do abdome |
| diafragma, intercostais | *diaphragma, intercostales* | P (intercostais podem aparecer entre os dentes do serrátil) | não | respiração ([WP][wp]) | bracing na respiração | ausente, correto |

#### Braço

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| bíceps braquial, cabeça longa e cabeça curta | *biceps brachii caput longum / breve* | S | F, L | flete o cotovelo e supina o antebraço ([WP][wp]) | roscas, barra fixa supinada, remadas | bíceps (uma região) |
| braquial | *brachialis* | P sob o bíceps, mas aparece entre bíceps e tríceps na face lateral do braço | L, F (borda) | flete o cotovelo ([WP][wp]) | rosca martelo, rosca inversa, barra fixa; secundário em 156 exercícios ([cat][cat]) | **fundido** no bíceps (o código mapeia `brachialis` para `biceps`, [muscles.js][muscles]) |
| tríceps braquial: cabeça longa, lateral, medial | *triceps brachii* | S (medial mais coberta, aparece perto do cotovelo) | C, L | estende o cotovelo; a cabeça longa também aduz o ombro; a medial não atua no ombro ([WP][wp]) | tríceps pulley, tríceps francês e extensão acima da cabeça (cabeça longa alongada), supino fechado, paralelas, testa | tríceps (uma região) |
| ancôneo | *anconeus* | S (triângulo pequeno atrás do cotovelo) | C | estende o antebraço, estabiliza o cotovelo, abduz a ulna na pronação ([WP][wp]) | junto com o tríceps | dentro do tríceps ou antebraço |

#### Antebraço

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| braquiorradial | *brachioradialis* | S (massa lateral, "mobile wad") | F, L | flete o antebraço; prona a partir da supinação e supina a partir da pronação ([WP][wp]) | rosca martelo, rosca inversa, remadas com pegada neutra | **fundido** no antebraço |
| extensor radial longo e curto do carpo | *extensor carpi radialis longus / brevis* | S (mobile wad) | L, C | estendem o punho e abduzem a mão ([WP][wp]) | rosca de punho inversa, pegada em geral | fundido no antebraço |
| pronador redondo | *pronator teres* | S | F | prona o antebraço e flete o cotovelo ([WP][wp]) | rotação com halter ou clava, rosca | fundido no antebraço |
| flexor radial do carpo | *flexor carpi radialis* | S | F | flete e abduz o punho ([WP][wp]) | rosca de punho, pegada | fundido no antebraço |
| palmar longo | *palmaris longus* | S | F (tendão central no punho) | flete o punho ([WP][wp]) | rosca de punho | fundido no antebraço |
| flexor ulnar do carpo | *flexor carpi ulnaris* | S | F, C (borda ulnar) | flete e aduz o punho ([WP][wp]) | rosca de punho | fundido no antebraço |
| flexor superficial dos dedos | *flexor digitorum superficialis* | S (camada intermediária, aparece entre os outros) | F | flete os dedos, sobretudo nas interfalângicas proximais ([WP][wp]) | terra, carregada, suspensão na barra, hand grip; "grip muscles" é secundário em 222 exercícios ([cat][cat]) | fundido no antebraço |
| flexor profundo dos dedos, flexor longo do polegar, pronador quadrado | *flexor digitorum profundus, flexor pollicis longus, pronator quadratus* | P | não | flete punho e dedos; flete o polegar; prona fraco ([WP][wp]) | pegada | fundido no antebraço |
| extensor dos dedos, extensor do dedo mínimo, extensor ulnar do carpo | *extensor digitorum, extensor digiti minimi, extensor carpi ulnaris* | S | C | estendem mão e dedos; o ulnar estende e aduz o punho ([WP][wp]) | rosca de punho inversa, elástico de extensão de dedos | fundido no antebraço |
| supinador, abdutor longo do polegar, extensores curto e longo do polegar, extensor do indicador | *supinator, abductor pollicis longus, extensor pollicis brevis/longus, extensor indicis* | P (abdutor longo e extensor curto do polegar aparecem no dorso distal) | C, discreto | supina o antebraço; movimentos do polegar e do indicador ([WP][wp]) | rosca supinada, rotação com halter | fundido no antebraço |

No catálogo, "forearms" é alvo de 147 exercícios, "wrist flexors" secundário de 70 e "wrist extensors" de 51 ([cat][cat]); o código junta todos em `forearm` ([muscles.js][muscles]).

#### Mão (uma linha)
- **Lumbricais da mão**, interósseos palmares e dorsais, tenares (abdutor curto, flexor curto e oponente do polegar), adutor do polegar e hipotenares ([PT][ptwp]). Os lumbricais fletem as metacarpofalângicas e estendem as interfalângicas ([WP][wp]). Só a eminência tenar e o primeiro interósseo dorsal aparecem na pele. Treino: pegada em pinça. Nosso modelo: mãos inertes, adequado.

#### Quadril e região glútea

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| glúteo máximo | *gluteus maximus* | S | C, L | estende e roda lateralmente o quadril, sustenta o joelho estendido pelo trato iliotibial, principal antigravitacional ao sentar ([WP][wp]) | hip thrust, agachamento, terra, stiff, avanço, step-up; "glutes" é alvo de 671 exercícios ([cat][cat]) | glúteo (junto com o médio) |
| glúteo médio | *gluteus medius* | S/P (parte superolateral não coberta pelo máximo, sob fáscia espessa) | L, C, F (na vista frontal aparece no alto do quadril, como na carta do Lipe) | abduz o quadril, impede a adução (estabilidade da pelve em apoio unipodal), roda medialmente a coxa ([WP][wp]); tem partes anterior, média e posterior, como um "deltoide do quadril" ([learnmuscles][learnmuscles]) | cadeira abdutora, elevação lateral de perna deitado, caminhada lateral com elástico, búlgaro e step-up (estabilizador); "abductors" é **alvo principal** de 90 exercícios ([cat][cat]) | **fundido** no glúteo (o código mapeia `abductors` para `gluteal`, [muscles.js][muscles]) |
| glúteo mínimo | *gluteus minimus* | P sob o médio | não | igual ao médio: abduz, impede a adução, roda medialmente ([WP][wp]) | os mesmos do médio | fundido no glúteo |
| tensor da fáscia lata | *tensor fasciae latae* | S | L, F (abaixo da espinha ilíaca anterossuperior) | flete e roda medialmente a coxa, estabiliza o tronco ([WP][wp]) | cadeira abdutora, flexão de quadril, corrida | **ausente** (fica entre glúteo, flexores do quadril e vasto lateral) |
| piriforme | *piriformis* | P sob o glúteo máximo | não | roda lateralmente a coxa ([WP][wp]) | concha (clamshell), rotação externa de quadril; estabilizador no agachamento | ausente (área: centro do glúteo) |
| gêmeos superior e inferior, obturadores interno e externo, quadrado femoral | *gemelli, obturatores, quadratus femoris* | P | não | rotadores laterais; o obturador externo também aduz, o interno estabiliza o quadril na marcha ([WP][wp]) | idem piriforme | ausente (área: glúteo inferior) |
| iliopsoas: psoas maior e ilíaco (psoas menor inconstante) | *iliopsoas: psoas major, iliacus* | P (só a porção distal aparece no triângulo femoral, abaixo do ligamento inguinal) | F, discreto | o psoas flete e roda lateralmente a coxa; o ilíaco flete o quadril ([WP][wp]) | elevação de pernas na barra, elevação de joelhos, abdominal completo, flexão de quadril no cabo, sprint; "hip flexors" é secundário em 782 exercícios ([cat][cat]) | flexores do quadril, ok |

#### Coxa anterior

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| sartório (costureiro) | *sartorius* | S (faixa diagonal da espinha ilíaca ao joelho medial) | F, L medial | flete, roda lateralmente e abduz a coxa; flete e roda medialmente a perna ([WP][wp]) | pouco isolável; trabalha na flexão de quadril | **ausente** (é a linha que separa quadríceps e adutores numa figura magra) |
| reto femoral | *rectus femoris* | S | F | estende o joelho e flete o quadril ([WP][wp]) | cadeira extensora, agachamento, sissy squat, elevação de pernas | reto femoral, ok |
| vasto lateral | *vastus lateralis* | S | F, L | estende o joelho ([WP][wp]) | agachamento, leg press, cadeira extensora | vasto lateral, ok |
| vasto medial (a "gota") | *vastus medialis* | S | F | estende o joelho ([WP][wp]) | agachamento profundo, leg press, cadeira extensora | vasto medial, ok |
| vasto intermédio | *vastus intermedius* | P sob o reto femoral | não | estende o joelho ([WP][wp]) | os mesmos | dentro do reto femoral |

#### Coxa medial (adutores)

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| pectíneo | *pectineus* | S/P (no triângulo femoral) | F (alto da coxa medial, como na carta do Lipe) | aduz e flete o quadril ([WP][wp]) | cadeira adutora, flexão de quadril | adutores ou flexores do quadril |
| adutor longo | *adductor longus* | S | F | aduz e roda medialmente o quadril ([WP][wp]) | cadeira adutora, prancha de Copenhague, agachamento sumô | adutores, ok |
| adutor curto | *adductor brevis* | P | não | aduz o quadril ([WP][wp]) | idem | dentro dos adutores |
| adutor magno (parte adutora e parte isquiocondilar, "do jarrete") | *adductor magnus* | S/P (aparece na face medial e na posterior medial da coxa) | F medial, C | as duas partes aduzem o quadril ([WP][wp]); a parte isquiocondilar costuma ser descrita também como extensora do quadril † | agachamento profundo, terra sumô, cadeira adutora | adutores (a parte de trás pode ter caído em isquiotibiais) |
| grácil | *gracilis* | S (faixa fina na borda medial) | F, C medial | aduz e flete o quadril, roda medialmente o joelho ([WP][wp]) | cadeira adutora, Copenhague | adutores, ok |

No catálogo, "adductors" é alvo de 68 exercícios e "groin" e "inner thighs" aparecem como secundários em 61 e 56 ([cat][cat]).

#### Coxa posterior (isquiotibiais)

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| bíceps femoral, cabeça longa e cabeça curta | *biceps femoris* | S (curta parcialmente coberta) | C, L | flete o joelho, roda lateralmente a perna com o joelho fletido, estende o quadril (só a cabeça longa) ([WP][wp]) | mesa flexora (as duas cabeças), stiff, good morning, nórdico, hip thrust | isquiotibiais (uma região) |
| semitendíneo | *semitendinosus* | S | C | flete o joelho, estende o quadril, roda medialmente a perna ([WP][wp]) | idem | isquiotibiais |
| semimembranáceo | *semimembranosus* | S/P (aparece dos dois lados do tendão do semitendíneo, perto do joelho) | C, medial | idem semitendíneo ([WP][wp]) | idem | isquiotibiais |

"Hamstrings" é alvo de 217 exercícios e secundário de 1.332 ([cat][cat]).

#### Perna

| PT-BR | Latim / inglês | Camada | Visível | Ação (fonte) | Treino (inferido) | Nosso modelo |
|---|---|---|---|---|---|---|
| gastrocnêmio, cabeças medial e lateral | *gastrocnemius caput mediale / laterale* | S | C, L, F (bordas) | flexão plantar do tornozelo; flexão do joelho (menor) ([WP][wp]) | panturrilha em pé, no leg press, saltos, sprint | panturrilha (junto com o sóleo) |
| sóleo | *soleus* | S/P (sob o gastrocnêmio, mas sobra dos dois lados da metade baixa da perna) | C, L, F (aparece na carta frontal do Lipe, medial à tíbia) | só flexão plantar do tornozelo, não cruza o joelho ([WP][wp]) | panturrilha **sentado** (joelho fletido); secundário em 105 exercícios ([cat][cat]) | **fundido** na panturrilha (o código mapeia `soleus` para `calves`, [muscles.js][muscles]) |
| plantar | *plantaris* | P | não | flexão plantar e flexão do joelho ([WP][wp]) | panturrilha | ausente, correto |
| poplíteo | *popliteus* | P (atrás do joelho) | não | roda medialmente e flete o joelho ([WP][wp]) | nenhum específico | joelho inerte, correto |
| tibial anterior | *tibialis anterior* | S | F, L | dorsiflexão e inversão do pé ([WP][wp]) | tibial raise, elevação de ponta de pé, "shins" secundário em 72 exercícios ([cat][cat]) | tibial anterior, ok |
| extensor longo dos dedos | *extensor digitorum longus* | S | F, L | estende os dedos e o tornozelo ([WP][wp]) | idem tibial | provavelmente dentro do tibial |
| extensor longo do hálux | *extensor hallucis longus* | P (tendão aparece no dorso do pé) | F, discreto | estende o hálux, ajuda a dorsiflexão, inverte fraco ([WP][wp]) | idem | dentro do tibial |
| fibular terceiro | *fibularis tertius* | P | não | dorsiflexão e eversão ([WP][wp]) | idem | ausente |
| fibular longo e fibular curto | *fibularis (peroneus) longus / brevis* | S | L, F (o longo aparece na carta frontal do Lipe) | flexão plantar e eversão ([WP][wp]) | panturrilha (secundário), equilíbrio unipodal, eversão com elástico | **ausente** (faixa entre tibial e panturrilha) |
| tibial posterior, flexor longo dos dedos, flexor longo do hálux | *tibialis posterior, flexor digitorum longus, flexor hallucis longus* | P | não | inverte e faz flexão plantar; fletem dedos e hálux ([WP][wp]) | panturrilha (secundário), sustentação do arco | ausente (área: panturrilha) |

#### Pé (uma linha cada)
- **Extensor curto dos dedos** e **extensor curto do hálux** (dorso do pé, S, aparece como um volume lateral no dorso): estendem os dedos 2 a 4 e o hálux ([WP][wp]); estão na carta frontal do Lipe. **Abdutor do hálux** (borda medial, aparece) abduz o hálux ([WP][wp]). Flexor curto dos dedos, quadrado plantar, lumbricais e interósseos do pé ficam na planta, invisíveis ([PT][ptwp]). Treino: "short foot", flexão de dedos. Nosso modelo: pés inertes, adequado.

### Inferences
- **A coluna "Treino" é inferida da ação articular** (ex.: quem estende o cotovelo trabalha em tríceps pulley) e das marcações do catálogo. É coerente com a prática de academia, mas não foi conferida linha a linha numa fonte de exercícios.
- **Camada e visibilidade** foram avaliadas pela estratificação anatômica padrão e pelos rótulos das cartas frontais do Lipe; as fontes citadas confirmam a região e o compartimento (ex.: "Forearm, Anterior compartment, Superficial" na [WP][wp]), não a visibilidade em si.
- **Os músculos superficiais que moldam a figura magra** e que um mapa deve ter: ECM; trapézio (3 partes); deltoide (3); infraespinal, redondo menor e redondo maior; latíssimo; serrátil anterior; peitoral maior (2 ou 3); bíceps, braquial (lateral), tríceps; braquiorradial, flexores e extensores do antebraço; reto do abdome, oblíquo externo; eretores lombares; glúteo máximo e médio, tensor da fáscia lata; sartório, reto femoral, vastos lateral e medial, adutores (pectíneo, adutor longo, grácil, adutor magno); bíceps femoral, semitendíneo, semimembranáceo; gastrocnêmio, sóleo, tibial anterior, fibulares.
- **Profundos que só cabem como "área por cima":** supraespinal (sob o trapézio superior e médio), subescapular (impossível), romboides (sob o trapézio médio, mas já é região nossa), quadrado lombar (flanco lombar), multífidos, oblíquo interno e transverso (sob oblíquo externo e reto), glúteo mínimo e piriforme com os rotadores laterais (sob o glúteo), iliopsoas (virilha), vasto intermédio (sob o reto femoral), tibial posterior e flexores longos (sob a panturrilha), peitoral menor e coracobraquial (sob o peitoral e na axila).

### Gaps
- Não consegui acessar uma fonte de exercícios por músculo (ExRx.net e MuscleWiki devolveram HTTP 403); a coluna de treino ficou inferida.
- Ações das partes do deltoide, da parte abdominal do peitoral, do redondo maior além da rotação medial, e a função extensora do adutor magno não vieram da lista da Wikipedia; estão marcadas com (†).
- **Oblíquo interno:** o resumo da lista da Wikipedia deu "gira para o lado oposto" para os dois oblíquos. A descrição anatômica usual é que o interno gira o tronco para o **mesmo** lado, em par com o externo do lado oposto. Não reconferi na fonte original; tratar como conflito em aberto.
- Variações que mudam o que se vê ficaram sem fonte nesta pesquisa: número de interseções tendíneas do reto do abdome (o "tanquinho" de 4, 6 ou 8 gomos), ausência do palmar longo, do plantar e do psoas menor em parte da população, e a cabeça medial do gastrocnêmio descer mais que a lateral.
- Não achei a Terminologia Anatômica da SBA online para fixar a grafia oficial de supraespinal x supraespinhal e das partes do deltoide (clavicular, acromial, espinal); a [Wikipedia PT][ptwp] usa "supraespinhal" e "infraespinhal".
- Um resultado de busca (cartões de estudo) dizia que o sóleo nasce nos epicôndilos do fêmur; descartei por contrariar a [WP][wp], onde o sóleo só faz flexão plantar e não cruza o joelho.

## 2. Músculos e cabeças que o meio fitness costuma separar, e por quê

### Takeaway
A separação que importa para o treino é a de partes com **ações diferentes ou que cruzam articulações diferentes**: aí a escolha do exercício (ângulo do ombro, joelho dobrado ou esticado, rotação) muda qual parte trabalha. Peitoral clavicular x esternocostal, as três partes do deltoide e do trapézio, gastrocnêmio x sóleo, reto femoral x vastos, cabeça longa do tríceps, braquial x bíceps, glúteo médio x máximo e redondo maior x infraespinal são os pares com respaldo direto nas ações citadas.

### Cited Findings
- **Peitoral, clavicular x esternocostal:** a parte clavicular flete o úmero e a esternocostal o estende ([WP][wp]). Ações opostas no plano sagital justificam o "peito superior" como região à parte; o catálogo já marca "upper chest" em 279 exercícios ([cat][cat]).
- **Deltoide anterior, lateral, posterior:** o deltoide abduz, flete e estende o ombro ([WP][wp]); o catálogo marca "rear deltoids" como secundário em 328 exercícios ([cat][cat]). A biblioteca MuscleMap separa front e rear deltoid como sub-grupos ([MuscleMap][mm]).
- **Trapézio em três partes:** a [WP][wp] separa a parte descendente das partes transversa e ascendente, com elevação, adução e depressão da escápula. O [Hevy][hevy-back] lista trapézio superior, médio e inferior como músculos distintos das costas; o MuscleMap separa upper e lower trapezius ([MuscleMap][mm]).
- **Tríceps:** a cabeça longa aduz o ombro e a medial não atua no ombro ([WP][wp]); por isso exercícios acima da cabeça (ombro fletido) mudam a carga sobre a cabeça longa.
- **Bíceps x braquial x braquiorradial:** o bíceps flete o cotovelo e supina; o braquial só flete o cotovelo; o braquiorradial flete o antebraço e leva o antebraço à posição neutra ([WP][wp]). O catálogo marca "brachialis" em 156 exercícios ([cat][cat]).
- **Gastrocnêmio x sóleo:** o gastrocnêmio faz flexão plantar e flete o joelho; o sóleo só faz flexão plantar ([WP][wp]). É a base da panturrilha sentado x em pé; o catálogo marca "soleus" em 105 exercícios ([cat][cat]).
- **Reto femoral x vastos:** o reto femoral estende o joelho e flete o quadril; os vastos só estendem o joelho ([WP][wp]). O MuscleMap tem sub-grupos "innerQuad", "outerQuad" e "hipFlexors" dentro do quadríceps ([MuscleMap][mm]).
- **Bíceps femoral, cabeça longa x curta, e isquiotibiais mediais:** só a cabeça longa estende o quadril; bíceps femoral roda a perna para fora e semitendíneo e semimembranáceo para dentro ([WP][wp]).
- **Glúteo máximo x médio:** o máximo estende e roda lateralmente; o médio abduz, impede a adução e roda medialmente ([WP][wp]); o glúteo médio tem partes anterior, média e posterior, como o deltoide ([learnmuscles][learnmuscles]). O catálogo tem 90 exercícios com "abductors" como alvo principal ([cat][cat]).
- **Tensor da fáscia lata, sartório, grácil:** TFL flete e roda medialmente; sartório flete, abduz e roda lateralmente o quadril e flete o joelho; grácil aduz, flete e roda medialmente o joelho ([WP][wp]).
- **Redondo maior x infraespinal e redondo menor:** o redondo maior roda medialmente o úmero, enquanto infraespinal e redondo menor rodam lateralmente ([WP][wp]). O Hevy lista "teres major and minor" entre os músculos de costas ([Hevy][hevy-back]); o MuscleMap tem "rotatorCuff" e "rhomboids" como regiões só da vista de costas ([MuscleMap][mm]).
- **Levantador da escápula e ECM:** o levantador eleva a escápula; o ECM flete, inclina e gira a cabeça ([WP][wp]). O catálogo tem 65 exercícios com "levator scapulae" como alvo e 54 com "sternocleidomastoid" como secundário ([cat][cat]). O Hevy criou um grupo muscular "neck" na versão 1.30.7 ([changelog Hevy][hevy-neck]).
- **Extensores do pescoço** (esplênios, semiespinal) estendem a cabeça ([WP][wp]); nenhuma fonte de app consultada os separa do grupo "pescoço".

### Inferences
- Regra prática para decidir uma divisão: **separar quando a parte cruza uma articulação a mais ou faz ação oposta** (gastrocnêmio/sóleo, reto femoral/vastos, cabeça longa do tríceps, cabeça longa do bíceps femoral, redondo maior/infraespinal, peitoral clavicular/esternocostal). Nesses casos o usuário pode de fato mudar o estímulo trocando o exercício, e o mapa consegue dar um retorno que muda decisão.
- Divisões que o fitness faz por estética mas com pouco respaldo de ação diferente (cabeça longa x curta do bíceps, "vasto medial oblíquo", "abdome inferior") valem como desenho, não como dado; sem dado por exercício, pintar a sub-região separada sugere uma precisão que não existe, o mesmo argumento que já está no comentário de [body-paths.js][bodypaths].

### Gaps
- Não achei, nas fontes acessíveis, evidência de hipertrofia regional (ex.: inclinado x reto para o peitoral clavicular, extensão acima da cabeça para a cabeça longa do tríceps). Fica como lacuna para outro pesquisador.
- As "bias" populares (rosca inclinada para a cabeça longa do bíceps, rosca Scott para a curta) não foram verificadas.

## 3. Análise de lacunas do nosso modelo (31 regiões por lado) e proposta de v2

### Takeaway
O boneco cobre bem peito, ombro, trapézio, abdome e coxa anterior, mas **funde quatro pares que dão retorno errado de treino** (glúteo médio no glúteo, redondo maior no manguito, sóleo na panturrilha, braquial no bíceps) e **não desenha o pescoço**, embora o catálogo já tenha 65 exercícios com alvo no levantador da escápula, 54 com ECM e 90 com alvo em abdutores. A v2 deve primeiro criar essas regiões (todas já têm dado no catálogo) e só depois as que são mais estéticas (fibulares, sartório, divisão de antebraço, isquiotibiais e tríceps).

### Cited Findings
- **Contagem atual:** peito 3, deltoide 3, bíceps 1, tríceps 1, antebraço 1, abdome 4 (3 fileiras + inferior), oblíquo 1, serrátil 1, trapézio 3, costas superiores 3 (latíssimo, romboides, área do manguito), lombar 1, glúteo 1, flexores do quadril 1, quadríceps 3, adutores 1, isquiotibiais 1, panturrilha 1, tibial 1 = 31 (descrição do modelo no pedido).
- **O dado do app é mais grosso que o desenho:** a lista `MUSCLES` do app web tem 18 músculos (trapézio, deltoides, peito, costas superiores, serrátil, bíceps, tríceps, antebraço, abdome, oblíquos, lombar, glúteo, quadríceps, isquiotibiais, adutores, flexores do quadril, panturrilha, tibial), e o arquivo de geometria descarta os sub-grupos do MuscleMap porque "o conjunto de exercícios resolve para músculos inteiros" ([muscles.js][muscles], [body-paths.js][bodypaths]). O campo curado `muscleMap` do catálogo também usa só esses nomes inteiros ([cat][cat]).
- **Aliases que hoje fundem ou descartam informação** ([muscles.js][muscles]): `abductors → gluteal` (90 alvos), `levator scapulae → trapezius` (65 alvos), `rotator cuff → deltoids` (185 secundários; note que o boneco 3D põe o manguito nas costas, não no deltoide), `rhomboids → upper-back` (375), `brachialis → biceps` (156), `soleus → calves` (105), `wrist flexors / wrist extensors / grip muscles → forearm` (70 / 51 / 222), `shins → tibialis` (72), `sternocleidomastoid → null` (54, descartado), `ankles`, `feet`, `hands`, `ankle stabilizers → null` ([cat][cat]).
- **Itens das cartas do Lipe sem região própria:** esternocleidomastóideo (pescoço inerte), palmar longo, flexor radial do carpo, braquiorradial e flexor superficial dos dedos (todos dentro de "antebraço"), lumbricais e extensores curtos do pé (mãos e pés inertes, aceitável), glúteo médio (dentro de "glúteo"), tensor da fáscia lata (ausente), pectíneo, adutor longo e grácil (dentro de "adutores"), sartório (ausente), sóleo (dentro de "panturrilha"), fibular longo (ausente). Frontal (cabeça) fica de fora por ser boneco sem rosto (cartas de referência do Lipe, vista frontal).
- **Equivalentes de costas:** infraespinal + redondo menor + redondo maior fundidos numa área; levantador da escápula e esplênios ausentes; quadrado lombar ausente (profundo); glúteo máximo + médio fundidos; mínimo e piriforme profundos; bíceps femoral, semitendíneo e semimembranáceo fundidos; cabeças do gastrocnêmio e sóleo fundidos; três cabeças do tríceps fundidas; braquial no bíceps; braquiorradial e extensores no antebraço; ancôneo sem lugar definido.
- O MuscleMap original tem 22 músculos base mais 14 sub-grupos (36), em 4 vistas (masculino e feminino, frente e costas), incluindo "neck" como sub-grupo sempre visível de "head" e "rotatorCuff", "rhomboids" e "rearDeltoid" só na vista de costas ([MuscleMap][mm]).

### Inferences
**Fusões que importam para o retorno de treino, em ordem de prioridade:**

1. **Glúteo médio (com mínimo e, opcionalmente, TFL) separado do glúteo máximo.** Ações diferentes (abdução e estabilidade pélvica x extensão), visível de lado e de frente, e o catálogo já tem 90 exercícios com "abductors" como alvo. Hoje uma cadeira abdutora pinta o glúteo inteiro, o que diz ao usuário que treinou o hip thrust.
2. **Pescoço deixa de ser inerte:** duas regiões, "esternocleidomastóideo" (frente e lado) e "pescoço posterior" (esplênios, semiespinal e a faixa do levantador da escápula no lado do pescoço). Dá casa aos 54 secundários de ECM hoje descartados e aos 65 alvos de levantador que hoje vão para o trapézio; o Hevy já tem um grupo "neck".
3. **Redondo maior sai da área do manguito.** Ele trabalha com o latíssimo nas puxadas, enquanto infraespinal e redondo menor fazem rotação externa. Proposta: "redondo maior" como região própria (ou colado ao latíssimo) e "manguito rotador" fica só com infraespinal e redondo menor. Corrigir junto o alias `rotator cuff → deltoids` para apontar para essa região.
4. **Sóleo separado do gastrocnêmio.** Visível dos dois lados da perna, inclusive na vista frontal; 105 secundários no catálogo; muda a leitura entre panturrilha sentado e em pé.
5. **Braquial separado do bíceps** (faixa na face lateral do braço, entre bíceps e tríceps). 156 secundários no catálogo; rosca martelo e inversa passam a ter retorno próprio.
6. **Antebraço em dois ou três:** "braquiorradial" (com extensores radiais, massa lateral alta), "flexores" (face anterior e medial) e "extensores" (face posterior). Há dado: 70 flexores, 51 extensores, 222 pegada.

**Divisões mais estéticas ou com pouco dado (v2.1):**

7. **Fibulares** (faixa lateral da perna): visível de frente e de lado e está na carta do Lipe; quase sem dado no catálogo (só "ankle stabilizers" em 4 e "ankles" em 216, hoje descartados).
8. **Isquiotibiais lateral (bíceps femoral) x medial (semitendíneo e semimembranáceo):** os dois lados são visíveis e rodam a perna em sentidos opostos, mas o catálogo não distingue.
9. **Tríceps: cabeça longa x lateral (com a medial):** forma a "ferradura" e responde diferente a exercícios acima da cabeça; sem dado no catálogo.
10. **Sartório e tensor da fáscia lata:** importantes para o desenho da coxa e do quadril de uma figura magra; pouco dado. O sartório pode ser só uma faixa de divisa (pintada com a cor dos flexores do quadril ou inerte); o TFL pode entrar na região do glúteo médio como "abdutores".

**O que manter fundido (ou até simplificar):**
- Profundos sem superfície ficam como área: supraespinal no trapézio superior e médio, subescapular nenhum, quadrado lombar e multífidos na lombar, oblíquo interno e transverso nos oblíquos e no abdome, glúteo mínimo, piriforme e rotadores no glúteo, vasto intermédio no reto femoral, tibial posterior e flexores longos na panturrilha, peitoral menor no peito.
- **As 4 regiões do abdome e as 3 do peito não têm dado para pintar separado** (o catálogo só distingue "upper chest" e "lower abs"). Manter o recorte no desenho, mas sombrear como 2 regiões de dado em cada (peito superior x resto; abdome superior x inferior), herdando a cor do pai quando não há dado específico. O mesmo vale para as 3 partes do quadríceps.

**Proposta de lista v2 (por lado):**

| Etapa | Mudança | Regiões depois |
|---|---|---|
| v2.0 | + glúteo médio (com mínimo e TFL); + esternocleidomastóideo; + pescoço posterior (esplênios e levantador); redondo maior sai do manguito como região própria; + sóleo; + braquial | 31 + 6 = **37** |
| v2.1 | antebraço vira braquiorradial, flexores, extensores (+2); + fibulares (+1); isquiotibiais lateral e medial (+1); tríceps longa e lateral (+1); + sartório como faixa (+1) | **43** |

Para leitura em tamanho pequeno (widget, Apple Watch, miniaturas de exercício), usar **nível de detalhe**: agregar de volta aos 18 grupos que o app já usa (ou a algo próximo de 20), e só mostrar as 37 a 43 regiões na tela de detalhe com zoom. Isso mantém o mapa legível e evita que regiões menores que a ponta do dedo virem ruído.

### Gaps
- Não medi a área em pixels das regiões novas (sóleo, braquial, ECM) no tamanho do Watch; a afirmação de legibilidade é estimativa.
- A distribuição do catálogo mistura 922 exercícios sem `target` definido ([cat][cat]); as contagens acima valem para os que têm.
- Não verifiquei se o boneco 3D já tem geometria separável para TFL, sartório e fibulares, ou se exigem remodelagem.

## 4. Como apps e referências populares desenham o mapa do corpo (granularidade)

### Takeaway
Os mapas de recuperação dos apps comerciais ficam na faixa de 14 a 21 grupos, e bibliotecas de desenho mais finas chegam a 36 (MuscleMap). Nosso boneco com 31 já está acima dos apps de recuperação; uma v2 entre 37 e 43 fica no nível de detalhe do MuscleMap, desde que o tamanho pequeno use agregação.

### Cited Findings
- **MuscleMap (Melih Colpan, MIT, a base do nosso desenho):** 22 músculos base (abs, biceps, calves, chest, deltoids, feet, forearm, gluteal, hamstring, hands, head, knees, lowerBack, obliques, quadriceps, rhomboids, rotatorCuff, serratus, tibialis, trapezius, triceps, upperBack) e 14 sub-grupos (upperChest, lowerChest, upperAbs, lowerAbs, innerQuad, outerQuad, hipFlexors, frontDeltoid, rearDeltoid, upperTrapezius, lowerTrapezius, e os sempre visíveis ankles, adductors e neck), num total de 36, em 4 vistas ([MuscleMap][mm]). Não tem deltoide lateral, glúteo médio, sóleo, braquial nem ECM.
- **Nosso app web:** reduz tudo a 18 músculos e descarta os sub-grupos do MuscleMap ([muscles.js][muscles], [body-paths.js][bodypaths]).
- **Fitbod:** a aba Body mostra um mapa de músculos colorido com quanto cada grupo está recuperado, de 0 a 100%, e o usuário pode editar manualmente os grupos "frescos"; a orientação geral é 48 a 72 horas entre treinos do mesmo grupo ([Fitbod, central de ajuda][fitbod-help]; [Fitbod blog][fitbod-blog]; informação vinda de trechos de busca, a página de ajuda devolveu 403). Não achei a lista oficial de grupos.
- **Hevy:** o gráfico de corpo dos últimos 7 dias destaca em azul as partes treinadas, e as estatísticas deixam selecionar músculos de uma lista ([Hevy][hevy-sets]); adicionou o grupo "neck" na versão 1.30.7 ([changelog][hevy-neck]) e anunciou melhoria da precisão dos grupos musculares na 2.3.3 ([changelog][hevy-233]). O artigo de costas cita latíssimo, trapézio superior, médio e inferior, redondo maior e menor, eretor da espinha e romboides ([Hevy][hevy-back]). Não achei a lista completa de grupos do app.
- **Outros apps de mapa na App Store:** um anuncia estado de recuperação de 21 áreas musculares no mapa do corpo e outro de 14 grupos principais ([App Store id6758854092][app1]; [App Store id6782176731][app2]); o resumo da busca não deixou claro qual número pertence a qual app.
- **MuscleWiki:** biblioteca gratuita com mapa interativo em que se toca no músculo para ver exercícios, com mais de 2.000 vídeos, sem cadastro ([MuscleWiki][musclewiki], via trechos de busca; o site devolveu 403).

### Inferences
- A faixa de 14 a 21 grupos dos mapas de recuperação coincide com o que o nosso app já usa (18). É o nível certo para tamanho pequeno e para "o que estou negligenciando".
- O detalhe a mais que vale a pena (pescoço, glúteo médio, sóleo, braquial, redondo maior) é justamente o que o MuscleMap não tem e o nosso catálogo tem dado para alimentar; isso diferencia o HexGym sem pular para um atlas.
- Passar de uns 45 por lado transforma o mapa em atlas anatômico; não achei app de treino comercial que faça isso no mapa principal.

### Gaps
- MuscleWiki, ExRx e a central de ajuda do Fitbod devolveram HTTP 403; não verifiquei se o MuscleWiki tem um modo "avançado" com cabeças separadas, nem a estrutura do diretório de músculos do ExRx.
- Não achei documentação de granularidade do Strong (não houve resultado útil).
- A lista exata de grupos do Hevy e do Fitbod precisa ser lida dentro dos apps.

[wp]: https://en.wikipedia.org/wiki/List_of_skeletal_muscles_of_the_human_body
[ptwp]: https://pt.wikipedia.org/wiki/Lista_de_m%C3%BAsculos_do_corpo_humano
[kenhub-ee]: https://www.kenhub.com/pt/library/anatomia/musculos-eretores-da-espinha
[kenhub-dorso]: https://www.kenhub.com/pt/library/anatomia/anatomia-do-dorso-visao-geral
[learnmuscles]: https://learnmuscles.com/?p=173344
[mm]: https://github.com/melihcolpan/MuscleMap
[hevy-back]: https://www.hevyapp.com/back-and-bicep-workout/
[hevy-sets]: https://www.hevyapp.com/features/sets-per-muscle-group-per-week/
[hevy-neck]: https://www.apkmirror.com/apk/hevy-gym-workout-tracker/hevy-gym-log-workout-tracker/hevy-gym-log-workout-tracker-1-30-7-release/
[hevy-233]: https://www.apkmirror.com/?p=9828809
[fitbod-help]: https://help.fitbod.me/hc/en-us/articles/360006269014-Muscle-Recovery
[fitbod-blog]: https://fitbod.me/blog/muscle-recovery/
[app1]: https://apps.apple.com/app/id6758854092
[app2]: https://apps.apple.com/app/id6782176731
[musclewiki]: https://musclewiki.com/
[cat]: /Users/lipe/Developer/MyGym/catalogue/exercises
[muscles]: /Users/lipe/Developer/MyGym/frontend/src/lib/muscles.js
[bodypaths]: /Users/lipe/Developer/MyGym/frontend/src/lib/body-paths.js
