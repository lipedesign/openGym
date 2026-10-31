# Estudo de cor primária (accent) do fork

Data: 31/10/2026. Objetivo: escolher a cor principal do app nativo iOS, sem assumir o verde do openGym.

**Método.** O Mobbin exige plano pago, então não foi usado. Os screenshots atuais da App Store foram baixados pela API iTunes Lookup (versões publicadas entre setembro e outubro de 2026), e as cores chapadas saturadas foram medidas pixel a pixel e conferidas visualmente. Também foram lidos o CSS e a meta `theme-color` dos sites oficiais, o guia de marca da WHOOP e o Apple HIG.

**Legenda da fonte do hex:**
- **O**: documento oficial.
- **S**: CSS ou meta do site oficial.
- **A**: aproximado, medido em screenshot.
- **3**: site de terceiros, não confirmado.

---

## 1. Mercado

| App | Accent (hex) | Fonte | Fundo | Sensação |
|---|---|---|---|---|
| Strong | azul ~#34A6FF; verde ~#2DCD70 para concluir; roxo ~#A55BFD nos gráficos | A | claro (tem escuro) | utilitário, confiável, neutro |
| Hevy | azul ~#1C82E9 (no site, #008CFF) | A/S | claro (tem escuro) | social, amigável, limpo |
| Fitbod | vermelho-rosado #F2305A (dentro do app, ~#D52751) | S/A | escuro | intenso, esportivo, coach |
| Boostcamp | amarelo #FCC100 | S/A | escuro | técnico, powerlifting |
| JEFIT | azul-ciano ~#23A3E2 a #3294C4 (no site, #3179FF) | A/S | claro | genérico, academia comercial |
| Alpha Progression | azul ~#018CF5 (no site, #0080FF) | A/S | escuro | científico, preciso, sério |
| StrongLifts 5x5 | vermelho ~#F40519 (no site, #D22E2E) | A/S | claro | simples, direto, old-school |
| Liftin' | rosa-choque ~#FD0164 | A | escuro | pop, jovem, ousado |
| Apple Fitness / Fitness+ | volt #A6FF00 (a cor do anel Exercise). Anéis: Move #FA114F, Exercise #A6FF00, Stand #00FFF6 | O | preto | nativo, energético, icônico |
| Nike Training Club | monocromático, sem accent | A | escuro, com foto | editorial, premium, atlético |
| WHOOP | CTA teal #00F19F; Strain #0093E7; Recovery #16EC06 / #FFDE00 / #FF0026 | O | escuro (gradiente #283339 → #101518) | dados, performance, elite |
| Oura | sem accent saturado; azul-petróleo ~#2B7393 nos gradientes | A | escuro | calmo, joia, wellness premium |
| Strava | laranja #FC4C02 (uma fonte cita #FC5200) | 3 | escuro e claro | social, competitivo, outdoor |
| Peloton | interface em violeta ~#6C52F3; vermelho de marca #DF1C2F (não confirmado); Strength+ monocromático | A/3 | escuro | instrutor, aula, premium |
| Ladder | neon amarelo-lima #E6FF00 | S/A | escuro #0E0E0E | hype, coach, boutique |
| Future | monocromático; verde #65D92B só no site | A/S | escuro | concierge, discreto, premium |
| MacroFactor Workouts | azul ~#0171FB | A | preto | científico, denso, sóbrio |
| Gentler Streak | laranja-coral ~#F67D48, mais verde ~#28C886 | A | claro (tem escuro) | gentil, ilustrado, acolhedor |
| Bevel | sem accent único; uma cor por métrica | A/S | claro (tem escuro) | wellness, IA, limpo |
| Athlytic | botões azul ~#0291FC; recovery verde ~#00E866 | A | escuro | dados, técnico |
| Gymshark Training | pulado: a página do app dá 404 na App Store dos EUA, Reino Unido e Brasil |  |  |  |
| openGym (hoje) | systemGreen #30D158; marca lima #A3E635 |  | #0C0E12 / #000 |  |

## 2. O que está saturado

- **Azul é o padrão do nicho.** Dos 10 apps de registro de força com accent definido, 5 usam azul (Strong, Hevy, JEFIT, Alpha Progression, MacroFactor). Azul também é o tint padrão do iOS, então não diferencia.
- **Vermelho e rosa:** Fitbod, StrongLifts, Liftin'.
- **Lima e neon virou clichê:** Ladder, Apple Fitness+, o próprio openGym, a WHOOP. A lima do openGym fica quase idêntica ao anel Exercise (ΔE 7).
- **Amarelo:** Boostcamp é dono.
- **Premium monocromático:** NTC, Oura, Future, Peloton Strength+.
- **Fundo:** entre os apps de força, a maioria é escura.

## 3. Lacunas

- **Violeta / ultravioleta:** nenhum app de registro de força usa como primária.
- **Cobre / bronze:** ninguém usa como primária.
- **Ciano-gelo:** nenhum app usa como primária.
- **Monocromático com uma cor de conquista:** nenhum app de registro faz isso.

## 4. Psicologia da cor no treino

A evidência é mista e os efeitos são pequenos. A cor da interface não muda o desempenho; o que pesa é diferenciação, significado e legibilidade.

- **Vermelho:** estudos se contradizem (Elliot & Aarts 2011: mais força de preensão; Payen et al. 2011: menos taxa de força; Akers et al. 2012: mais raiva). Melhor reservar para erro e perigo.
- **Azul:** confiança e precisão, mas banalizado.
- **Laranja e âmbar:** energia sem soar como perigo, mas são as cores do meio da escala de esforço.
- **Violeta:** associação cultural com premium, maestria e tecnologia. Sobre fundo quase preto, lê como "neon elétrico" sem parecer agressivo.
- **Monocromático:** foco e linguagem editorial; deixa as cores dos dados falarem sozinhas.

## 5. Restrições práticas

**Distância de cor contra as cores com significado** (ΔE OKLab ×100; abaixo de ~10 dá para confundir num relance, acima de ~20 é claramente distinto):

| Cor | Conflitos medidos |
|---|---|
| #30D158 (atual) | É o systemGreen, a cor de "sucesso". Em deuteranopia fica a ΔE 5 do laranja do RPE e a 8 do vermelho de erro |
| #A3E635 (lima) | ΔE 7 do anel Exercise; 1 a 5 do ouro de PR para daltônicos |
| Vermelhos e rosas | ΔE 2 a 5 do anel Move, do rosa de frequência cardíaca e do erro |
| Âmbar | ΔE 8 a 9 do ouro de PR e do laranja do RPE |
| Cobre | ΔE 5 do laranja do RPE; ΔE ~1 do verde de sucesso em deuteranopia |
| **Violeta** | ≥ 24 contra todas as cores quentes, verdes e dos anéis, inclusive com daltonismo |
| Ciano | ΔE ~11 do anel Stand |
| Giz (off-white) | Sem conflito relevante |

**Nas superfícies do sistema:**
- **Liquid Glass:** o HIG pede cor com parcimônia e variantes para claro, escuro e Increased Contrast. Cores de luminância média e croma alto (violeta, cobre) aparecem como vidro colorido; cores muito claras (giz, lima, ciano) desbotam no vidro.
- **Widgets:** os modos tinted e clear dessaturam, a Lock Screen é monocromática e o StandBy noturno fica vermelho. A identidade precisa vir também de forma, tipografia e motion.
- **Dynamic Island e Live Activity:** fundo sempre preto; o accent precisa ser luminoso (violeta #9D8CFF dá 7.6:1 no preto).
- **Apple Watch:** os anéis de atividade têm cores fixas, e o HIG manda diferenciar outros anéis deles. Um anel de descanso verde, lima ou rosa se confunde; violeta, não.

## 6. Paletas candidatas

### A) Ultravioleta (recomendação do estudo)
- **Escuro:** texto e ícones #8B7BFF (5.9:1); preenchimento de botão #6F5CFF com rótulo branco (4.5:1); Watch e Dynamic Island #9D8CFF (7.6:1).
- **Claro:** #5B45E6 (6.1:1 no branco).
- **Apoio:** ouro de PR, #FFC94D no escuro e #8A6100 no claro, só em recordes e celebrações.
- **Por quê:** nenhum app de força usa; fica longe de todas as cores com significado, inclusive para daltônicos; funciona como vidro tingido; o ouro, complementar, faz do recorde o momento "wow".
- **Riscos:** a interface do Peloton usa um violeta parecido; violeta pode lembrar calma (compensar com motion e tipografia pesada); vizinho do systemIndigo.

### B) Giz & Ferro (monocromático com ouro)
- **Escuro:** #F2EFE9 com rótulo preto. **Claro:** #1D1D1F.
- **Apoio:** o mesmo ouro de PR, como única cor de marca.
- **Por quê:** "o app é preto e branco até você conquistar cor". Conflito de significado zero.
- **Riscos:** pouca lembrança de marca com a tela parada; depende de motion, ícone e tipografia; fica igual ao sistema na Dynamic Island e nos widgets.

### C) Ciano Glacial
- **Escuro:** #4FD8FF com rótulo preto. **Claro:** #00739E.
- **Apoio:** índigo #5E6BFF para gradientes.
- **Por quê:** precisão, cara de laboratório, a melhor legibilidade no preto.
- **Riscos:** perto do anel Stand; vizinho do "mar de azul"; soa frio, mais "recuperação" do que "força"; desbota no vidro claro.

### D) Cobre Forjado
- **Escuro:** #F2895A com rótulo preto. **Claro:** #B0521F com rótulo branco.
- **Apoio:** aço #8EA4BF.
- **Por quê:** único tom quente sem dono no nicho; lembra anilha, barra e ferro.
- **Riscos:** o maior conflito de significado: perto do laranja do RPE e do vermelho de erro, quase igual ao verde para daltônicos. Exigiria refazer a escala de esforço. Vizinho do Strava.

### Descartadas
Verde e lima (clichê, colidem com o anel Exercise), azul (o mais saturado do nicho e padrão do iOS), vermelho e rosa (colidem com erro, frequência cardíaca e anel Move), âmbar (colide com o ouro de PR e o meio da escala de esforço).

### Regras para qualquer escolha
- Erro sempre em systemRed.
- Recorde (PR) sempre em ouro.
- Escala de esforço sempre com número ou rótulo além da cor.
- Variantes Increased Contrast definidas.
- Cores definidas em Display P3.

---

## Fontes

- Guia de marca WHOOP: https://developer.whoop.com/assets/files/WHOOP%20-%20Brand%20&%20Design%20Guidelines-bdea3554e94b4ea09e68695b1e8dc8e7.pdf
- Apple HIG: [Color](https://developer.apple.com/design/human-interface-guidelines/color), [Activity rings](https://developer.apple.com/design/human-interface-guidelines/activity-rings), [Materials](https://developer.apple.com/design/human-interface-guidelines/materials), [Widgets](https://developer.apple.com/design/human-interface-guidelines/widgets), [Live Activities](https://developer.apple.com/design/human-interface-guidelines/live-activities), [App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- Screenshots da App Store via `https://itunes.apple.com/lookup?id=<id>&country=us`. IDs: Strong 464254577, Hevy 1458862350, Fitbod 1041517543, Boostcamp 1529354455, JEFIT 449810000, Alpha Progression 1462277793, StrongLifts 488580022, Liftin' 1445041669, NTC 301521403, WHOOP 933944389, Oura 1043837948, Strava 426826309, Peloton 792750948, Peloton Strength+ 6476712925, Ladder 1502936453, Future 1288178982, MacroFactor 1553503471, MacroFactor Workouts 6737156524, Gentler Streak 1576857102, Bevel 6456176249, Athlytic 1543571755, Apple Fitness 1208224953.
- Sites oficiais (CSS e theme-color): hevy.com, fitbod.me, boostcamp.app, jefit.com, alphaprogression.com, stronglifts.com, joinladder.com, future.co, athlyticapp.com, bevel.health, gentler.app, liftinapp.co
- Strava (terceiros): designpieces.com, brandpalettes.com. Peloton (terceiros): shadcn.io/design/peloton
- Tendências: https://www.lazyweb.com/research/what-theme-do-health-fitness-apps-use
- Pesquisas: Elliot & Aarts 2011 (pubmed 21500913), Payen et al. 2011 (hal-01469884), Hong et al. 2022 (Frontiers in Psychology, fpsyg.2021.744913), Mehta & Zhu 2009 (pubmed 19197022), Akers et al. 2012 (repository.essex.ac.uk/5060)
