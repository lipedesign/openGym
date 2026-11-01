# Fase 0 do HexGym (Fundação): plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> No HexGym, quem executa é o orquestrador (Task 1, skill `hexgym-orquestrador`). Cada Task é uma issue do milestone "Fase 0: Fundação" e um PR para `develop`: uma worktree e uma branch por Task, a revisão da Task é a revisão do PR, e o merge em `develop` faz o papel do superpowers:finishing-a-development-branch. Os títulos ficam "Task N" porque os scripts do superpowers procuram esse nome.

**Objetivo:** deixar o fork pronto para o trabalho feito por agentes e o HexGym abrindo no simulador e no iPhone do founder, ainda sem telas, com o motor do openGym rodando no JavaScriptCore, o documento de dados no App Group e um build interno no TestFlight.

**Arquitetura:** o motor é o código de `frontend/src/lib`, juntado num script só (`HexEngine`) pelo Vite que o frontend já tem e rodado num único `JSContext` dentro de um `actor` Swift (pacote `HexEngine`). O documento de dados é o mesmo `gym_state_v1` do openGym, guardado como JSON no App Group por outro `actor` (pacote `HexStore`, que não está na lista da seção 8.7: decisão do tech lead, para a gravação ter testes próprios, sem o motor). O app SwiftUI liga os dois e mostra o estado numa tela provisória. O orquestrador é uma skill do Claude Code com dois scripts Node sem dependências, um para o quadro e outro para as checagens; a CI chama as mesmas checagens.

**Tecnologias:** Node 22, com o Vite e o Vitest do frontend; Swift (`swift-tools-version: 6.2`), SwiftUI, JavaScriptCore e Swift Testing; Xcode 27; `gh` e GitHub Actions.

**Especificação:** `docs/superpowers/specs/2026-10-31-hexgym-native-app-design.md`, seções 5, 8.2, 8.3, 8.7, 8.10, 8.13, 9, 9.1, 10 e 11.

## Restrições globais (Global Constraints)

Valem para toda Task. Os valores vêm da especificação e do levantamento de 31/10/2026.

- **Plataforma:** iOS 26 e watchOS 26 como mínimo (`IPHONEOS_DEPLOYMENT_TARGET = 26.0`, `WATCHOS_DEPLOYMENT_TARGET = 26.0`). Xcode 27 via `DEVELOPER_DIR`, porque o `xcode-select` desta máquina aponta para as Command Line Tools: `/Applications/Xcode.app` (o 27.2 estável, quando o founder instalar na Task 12) ou, até lá, `/Applications/Xcode-beta.app` (27.0 beta 6). Da Task 7 em diante, todo `swift`, `xcodebuild`, `xcrun` e `codesign` roda com `DEVELOPER_DIR=$(node scripts/hexgym/xcode.mjs)`.
- **Formato do projeto:** `objectVersion = 77` e `preferredProjectObjectVersion = 77` (o formato "Xcode 16.0", que o Xcode 26 e o 27 abrem), sempre `project.pbxproj`, nunca o `.xcproj` em JSON do Xcode 27.2. Pacotes com `swift-tools-version: 6.2`. Nenhuma API só do iOS 27 ou do watchOS 27.
- **O Watch não roda JavaScript:** nada de JavaScriptCore nos alvos do Watch.
- **Poucas dependências:** nenhum pacote Swift de terceiros e nenhuma dependência npm nova; o script do motor usa o Vite que o frontend já tem.
- **Compatibilidade com o openGym:** o mesmo documento de dados (as chaves de `gym_state_v1`), sem perder chave nenhuma ao ler e gravar.
- **Privacidade:** sem telemetria, sem conta de terceiros, e nenhuma chamada de rede no app nesta fase.
- **Texto para o usuário:** simples e humano, sem travessão; português do Brasil e inglês.
- **Mídias de exercício:** nenhuma entra no app nesta fase. Nunca abrir, converter ou passar por ferramenta de IA as fotos e animações da Gym visual, e nada novo em `catalogue/media/`.
- **Prints e vídeo dos PRs:** ficam em `docs/hexgym/prints/<issue>/`, no commit do próprio PR, e o corpo do PR os mostra por `https://github.com/lipedesign/openGym/blob/<sha>/docs/hexgym/prints/<issue>/<arquivo>?raw=true`. O vídeo é do simulador (`xcrun simctl io <udid> recordVideo --codec h264`), com até 15 s e menos de 5 MB. Nenhum print ou vídeo mostra as imagens ou animações da Gym visual.
- **Repositório:** nunca mexer no upstream (`DuarteSantos8/openGym`) nem no espelho do GitLab, e nenhum `gh` aponta para ele: para ler o upstream, o `git` com o remoto `upstream`, que não tem push. Todo `gh` mira o fork: `-R lipedesign/openGym`, `repos/lipedesign/openGym/` no `gh api`, `--owner lipedesign` no Project, ou `--project-id PVT_kwHOAYVuVc4Bpo0b` no `gh project item-edit`, que não aceita dono. Nada em `data/`.
- **IDs:** `app.hexgym`, `app.hexgym.widgets`, `app.hexgym.watchkitapp`, `app.hexgym.watchkitapp.widgets`; App Group `group.app.hexgym`; esquema de URL `hexgym://`; time `MPAGLMK4Q2`.
- **Alvos:** `HexGym`, `HexGymWidgets`, `HexGymWatch` e `HexGymWatchWidgets`, com pastas sincronizadas e sem gerador de projeto.
- **Motor:** um `JSContext` só, dentro de um `actor`, nunca na thread principal; o script gerado é versionado, e o `--check` falha quando ele está velho.
- **Mudanças no código do openGym:** pequenas, com teste, cada uma num commit que possa ser proposto ao openGym; `cd frontend && npm test` e as checagens de locale (`node scripts/check-locales.mjs && node scripts/check-source-strings.mjs --strict`, em `frontend/`) continuam verdes.
- **Git Flow:** `feature/<número>-<nome>` a partir de `develop`; PR para `develop` com `Closes #<número>`; squash nas features; merge normal em release, sync e hotfix.
- **Arquivos em `.claude/`:** o `.gitignore` do openGym ignora a pasta inteira; arquivo novo ali entra com `git add -f`.
- **Commits:** terminam com a linha `Co-Authored-By:` do agente que escreveu.

## Foco da revisão (Review Focus)

O que a especificação implica, nenhuma Task testaria sozinha e mais pode morder quem usa o app. Cada linha ganhou um teste na Task dona do código.

1. **Documento truncado, corrompido ou que não abre naquela hora** (o app morreu no meio da gravação, disco cheio, permissão, o aparelho ainda bloqueado depois de ligar): com o documento ruim, o app abre a cópia anterior, guarda o arquivo ruim de lado e avisa no log; com as duas cópias ruins, ou com um arquivo que existe e não abre, mostra o erro e não grava nada. Nunca começa do zero em silêncio. Testes nas Tasks 8 e 10.
2. **Documento com chaves que o HexGym não conhece** (de um openGym mais novo ou de outra versão do HexGym), **ou com um texto que só o JavaScript lê** (um emoji cortado ao meio, que o `JSON.stringify` grava como `\ud83d`): restaurar e gravar de volta preserva todas as chaves, os valores e os bytes. Testes nas Tasks 7 e 8.
3. **Erro dentro do motor** (exceção no JS, JSON inválido, função que não existe): vira um erro Swift com a mensagem do JS, e a chamada seguinte funciona no mesmo contexto. Teste na Task 7.
4. **Histórico grande** (anos de treino): carregar o motor e marcar uma série ficam dentro das metas da seção 8.13, medidos sem JIT. Teste na Task 6.
5. **Fuso horário do aparelho** diferente do da máquina que gravou os casos, com e sem horário de verão: o JavaScriptCore dá o mesmo resultado que o Node no mesmo fuso, inclusive num treino que cruza a meia-noite. Teste na Task 7.

## Mapa dos arquivos

```
scripts/hexgym/                  ferramentas do HexGym (Node 22, sem dependências)
  project.json                   IDs do repositório, do Project e das colunas
  board.mjs                      o quadro: fase atual, próxima issue, mover cartão
  check.mjs                      as checagens por parte; a CI chama o mesmo script
  xcode.mjs                      qual Xcode usar e qual simulador
  engine-load.mjs                teste de carga do motor no jsc, sem JIT
  engine-tests.mjs               quais testes do lib rodam contra o script
  engine-cases.mjs               os casos de contrato do motor
  record-engine-cases.mjs        grava os casos no Node, um arquivo por fuso (--check)
  testflight.mjs                 arquivo, exportação e envio ao TestFlight
scripts/build-hexgym-engine.mjs  junta o motor num script só (--check)
frontend/src/lib/                as mudanças pequenas no openGym (Task 4)
frontend/vitest.hexengine.config.js   roda os testes do lib contra o script gerado
apple/
  .gitignore
  .gitattributes                 marca o script e os casos como gerados
  HexGym.xcodeproj/              os quatro alvos e os testes, formato 77
  HexGym/ HexGymWidgets/ HexGymWatch/ HexGymWatchWidgets/ HexGymTests/ Shared/
  Config/                        Info.plist parciais e entitlements, fora das pastas sincronizadas
  ExportOptions.plist
  Packages/HexEngine/            o motor no JavaScriptCore
    JS/                          o que o script leva além do lib, com os testes em Node
    Sources/HexEngine/           o ator e, em Resources/, o script gerado e o host.js
    Tests/HexEngineTests/        os testes Swift e, em Cases/, os casos gravados
  Packages/HexStore/             o documento de dados no App Group
.claude/skills/hexgym-orquestrador/SKILL.md
.claude/agents/hexgym-implementador.md, hexgym-revisor.md
.github/workflows/hexgym.yml
.github/README.md, .github/CONTRIBUTING.md, .github/SECURITY.md
docs/hexgym/prints/              os prints e os vídeos dos PRs, uma pasta por issue
docs/superpowers/.gitignore      deixa o git ver os planos (o openGym ignora docs/superpowers/plans/); entra com este plano
```

## Ordem e dependências

| Task | Issue | O que entrega | Depende de | Quem faz |
|---|---|---|---|---|
| 1 | #15 | O agente orquestrador | | tech lead |
| 2 | #3 | Workflows herdados desligados e `tests-ok` obrigatório | | tech lead, depois do clique do founder na aba Actions |
| 3 | #11 | Branches e etiquetas herdadas | 1 | orquestrador |
| 4 | #16 | O motor sem React | 1 | orquestrador |
| 5 | #17 | O script do motor | 4 | orquestrador |
| 6 | #18 | Os testes do lib contra o script e a carga no jsc | 5 | orquestrador |
| 7 | #19 | O pacote HexEngine | 5 | orquestrador |
| 8 | #20 | O pacote HexStore | 7 | orquestrador |
| 9 | #21 | O projeto Xcode com os quatro alvos | 7, 8 | orquestrador |
| 10 | #22 | O app abre com o motor e os dados | 9 | orquestrador |
| 11 | #9 | A CI do HexGym | 2, 6, 10 | orquestrador |
| 12 | #23 | Xcode 27.2, os IDs e o app no App Store Connect | 9 | founder |
| 13 | #24 | TestFlight a partir desta máquina | 10, 12 | orquestrador, com o ok do founder no primeiro envio |
| 14 | #8 | README, CONTRIBUTING e SECURITY do fork | 10 | orquestrador, com o texto aprovado pelo founder |
| 15 | #10 | Cópia dos arquivos do corpo e procedência da referência | 1 | orquestrador, depois das respostas do founder |
| 16 | #25 | Versão 0.1.0 | todas as outras, menos a 15 | orquestrador, com a aprovação do founder |

Cada issue leva duas linhas que o orquestrador lê: `Depende de: #a, #b` (ou `nenhuma`) e `Plano: docs/superpowers/plans/2026-10-31-fase-0-fundacao.md, Task N`. O tech lead criou as issues novas junto com o PR deste plano, já com as duas linhas, e acrescentou as duas no fim das Notas da #3, da #8, da #9, da #10 e da #11. A #14 é este plano e fecha com o PR dele; a #3 fecha no mesmo dia, com a Task 2.

Ficam fora desta fase, de propósito: o WatchCore em `apple/` (fase 4), o pacote `HexDesign` (fase 1), o `session-controller.js` (fase 3), as traduções do openGym em JSON (fase 2), o HealthKit, a sincronização com servidor e a medição num iPhone real com histórico grande (seção 8.13), que espera as telas que fazem esses cálculos (fases 3 e 5); nesta fase, a medida é a do `jsc` sem JIT, na Task 6.

Ficam também para a fase 5, cada um com uma issue no milestone "Fase 5: O resto do openGym" (#26 e #27), o que o JavaScriptCore não tem e só a importação e a exportação usam: `URL` (sem ele, o `cleanUrl` de `media-refs.js` devolve `null` e o plano compartilhado perde os links dos exercícios personalizados), `fetch` (a importação do Hevy), `TextEncoder`, `TextDecoder` e `Blob` (o zip e o FIT), e a leitura das datas do Apple Health (o JavaScriptCore não entende `new Date('2024-01-15 07:30:00 +0100')`, usado em `import-csv.js:866`). Nenhuma tela da fase 0 chega nesses caminhos, e o teste `webGlobalsTheEngineDoesNotHaveYet` da Task 7 prende o que falta: quem trouxer um deles muda o teste junto.

E duas coisas que a revisão do plano achou e ficam para depois, de propósito. A nota do dia é cortada por unidade de UTF-16 (`day-notes.js:33`), o que parte um emoji que cai na posição 500: o HexStore aceita esse texto (Task 8), e cortar por caractere é uma proposta ao openGym, para quando o founder falar com o Duarte. E o `save` do HexStore lê o `state.json` inteiro a cada gravação para decidir a cópia anterior: na fase 0 isso acontece uma vez por início, e a fase 3, que grava a cada série, mede antes de mudar.

---

### Task 1: O agente orquestrador

**Issue:** #15. **Quem faz:** o tech lead, à mão. É a única Task que não passa pelo orquestrador, porque é ela que cria o orquestrador.

**Files:**
- Create: `scripts/hexgym/project.json`
- Create: `scripts/hexgym/board.mjs`, `scripts/hexgym/board.test.mjs`
- Create: `scripts/hexgym/check.mjs`, `scripts/hexgym/check.test.mjs`
- Create: `scripts/hexgym/README.md`
- Create: `.claude/skills/hexgym-orquestrador/SKILL.md`
- Create: `.claude/agents/hexgym-implementador.md`, `.claude/agents/hexgym-revisor.md`

**Interfaces:**
- Produces:
  - `node scripts/hexgym/board.mjs phase` imprime `{"number":1,"title":"Fase 0: Fundação"}`: o primeiro milestone aberto na ordem de `project.json`.
  - `node scripts/hexgym/board.mjs refresh` só mexe nas issues abertas da fase que estão em "A fazer", em "Pronto para começar" ou fora do Project: põe em "Pronto para começar" a que não tem etiqueta de espera e tem as dependências fechadas, devolve para "A fazer" a que deixou de estar pronta, e adiciona ao Project a que falta lá. As que estão em andamento, em revisão ou feitas ficam como estão.
  - `node scripts/hexgym/board.mjs next` imprime `{"number","title","url","status","resume","plan","task"}` e sai com 0. A ordem: a de menor número em "Em revisão", depois a de menor número em "Em andamento" (as duas com `resume: true`), depois a pronta de menor número. Sem nada, imprime `null`, lista no stderr cada issue que espera e o motivo, e sai com 3.
  - `node scripts/hexgym/board.mjs move <número> <todo|ready|doing|review|done>`.
  - `node scripts/hexgym/board.mjs board` imprime a fase atual por coluna e a lista "Pede você".
  - `check.mjs` exporta `PARTS` (objeto `parte → [{ name, cmd, args, cwd?, env? }]`, na ordem em que rodam), `planChecks(parts: string[]) → check[]` e `runChecks(checks, run) → { ok: boolean, failed?: string }`. CLI: `node scripts/hexgym/check.mjs [parte ...] [--list]`, e sem parte roda todas. As Tasks seguintes acrescentam partes ao `PARTS`.
  - Os agentes `hexgym-implementador` e `hexgym-revisor`, e a skill `hexgym-orquestrador`.

`scripts/hexgym/project.json`, com os valores reais do Project 6:

```json
{
  "repo": "lipedesign/openGym",
  "owner": "lipedesign",
  "projectNumber": 6,
  "projectId": "PVT_kwHOAYVuVc4Bpo0b",
  "statusFieldId": "PVTSSF_lAHOAYVuVc4Bpo0bzhoDhPg",
  "status": {
    "todo": { "name": "A fazer", "id": "f75ad846" },
    "ready": { "name": "Pronto para começar", "id": "813d5271" },
    "doing": { "name": "Em andamento", "id": "47fc9ee4" },
    "review": { "name": "Em revisão", "id": "2256ca28" },
    "done": { "name": "Feito", "id": "98236657" }
  },
  "phases": [1, 2, 3, 4, 5, 6, 7, 8],
  "waitLabels": ["bloqueado", "decisão do founder"]
}
```

- [ ] **Step 1: Write the failing tests for `board.mjs`**

Em `scripts/hexgym/board.test.mjs`, com `node:test` e `node:assert/strict`. Um `fakeGh(fixtures)` responde a `issue list`, `project item-list`, `api .../milestones`, `project item-add` e `project item-edit` a partir dos fixtures e guarda cada chamada em `calls`; `run(argv, gh)` chama `main(argv, { gh, out, err })` e devolve `{ code, stdout, stderr, json }`. Os fixtures: `open(n, status, { labels = [], body = '', milestone = 1 } = {})` é uma issue aberta, com `status` `null` quando ela não está no Project; `closed(n)`, uma fechada; `ms(n, state)`, um milestone. O fake dá a cada issue do Project o item `PVTI_<n>`, e o `item-add` devolve `addItemId` ou, sem ele, `PVTI_<n>`. `statusEdits(calls)` junta as chamadas de `item-edit` num objeto `número → opção`, com o número lido do `--id`.

```js
test('parseMeta reads the dependencies and the plan task', () => {
  assert.deepEqual(
    parseMeta('Depende de: #15, #16\nPlano: docs/superpowers/plans/2026-10-31-fase-0-fundacao.md, Task 5'),
    { deps: [15, 16], plan: 'docs/superpowers/plans/2026-10-31-fase-0-fundacao.md', task: 5 })
  assert.deepEqual(parseMeta('Depende de: nenhuma'), { deps: [], plan: null, task: null })
  assert.deepEqual(parseMeta(''), { deps: [], plan: null, task: null })
})

test('phase is the first open milestone in config order', async () => {
  const r = await run(['phase'], fakeGh({ milestones: [ms(1, 'closed'), ms(2, 'open'), ms(3, 'open')] }))
  assert.equal(r.json.number, 2)
})

test('next resumes review before doing, then takes the lowest ready number', async () => {
  const r = await run(['next'], fakeGh({ issues: [open(16, 'Pronto para começar'), open(20, 'Em andamento'), open(23, 'Em revisão'), open(21, 'Em revisão')] }))
  assert.equal(r.json.number, 21); assert.equal(r.json.resume, true)
  const r2 = await run(['next'], fakeGh({ issues: [open(16, 'Pronto para começar'), open(15, 'A fazer')] }))
  assert.equal(r2.json.number, 15); assert.equal(r2.json.resume, false)
})

test('next skips waiting issues and says why', async () => {
  const r = await run(['next'], fakeGh({ issues: [
    open(15, 'A fazer', { labels: ['bloqueado'] }),
    open(16, 'A fazer', { labels: ['decisão do founder'] }),
    open(17, 'A fazer', { body: 'Depende de: #99' }), open(99, 'A fazer', { milestone: 2 })] }))
  assert.equal(r.code, 3); assert.equal(r.stdout.trim(), 'null')
  assert.match(r.stderr, /#15.*bloqueado/); assert.match(r.stderr, /#16.*decisão do founder/); assert.match(r.stderr, /#17.*espera #99/)
})

test('next ignores closed issues and other milestones', async () => {
  const r = await run(['next'], fakeGh({ issues: [closed(14), open(30, 'Pronto para começar', { milestone: 2 })] }))
  assert.equal(r.code, 3)
})

test('refresh moves ready issues forward and unready ones back, and leaves the rest alone', async () => {
  const gh = fakeGh({ issues: [open(15, 'A fazer'), open(16, 'Pronto para começar', { body: 'Depende de: #17' }), open(17, 'A fazer'), open(18, null),
    open(19, 'Em andamento'), open(20, 'Em revisão', { body: 'Depende de: #17' })] })
  await run(['refresh'], gh)
  assert.deepEqual(statusEdits(gh.calls), { 15: '813d5271', 16: 'f75ad846', 17: '813d5271', 18: '813d5271' })
})

test('move adds the item and sets the status option', async () => {
  const gh = fakeGh({ addItemId: 'PVTI_x' })
  await run(['move', '15', 'doing'], gh)
  assert.deepEqual(gh.calls.at(-2), ['project', 'item-add', '6', '--owner', 'lipedesign', '--url', 'https://github.com/lipedesign/openGym/issues/15', '--format', 'json'])
  assert.deepEqual(gh.calls.at(-1), ['project', 'item-edit', '--id', 'PVTI_x', '--project-id', 'PVT_kwHOAYVuVc4Bpo0b', '--field-id', 'PVTSSF_lAHOAYVuVc4Bpo0bzhoDhPg', '--single-select-option-id', '47fc9ee4'])
})

test('move rejects an unknown status', async () => {
  const r = await run(['move', '15', 'later'], fakeGh({}))
  assert.equal(r.code, 2); assert.match(r.stderr, /todo, ready, doing, review, done/)
})

test('no gh call names another repository', async () => {
  const gh = fakeGh({ milestones: [ms(1, 'open')], issues: [open(15, 'A fazer')], addItemId: 'PVTI_x' })
  for (const argv of [['phase'], ['next'], ['refresh'], ['move', '15', 'doing'], ['board']]) await run(argv, gh)
  assert.ok(gh.calls.length >= 5)
  for (const call of gh.calls) {
    const line = call.join(' ')
    assert.ok(call.includes('lipedesign/openGym') || line.includes('--owner lipedesign') || line.includes('--project-id PVT_kwHOAYVuVc4Bpo0b')
      || call.some(a => a.startsWith('repos/lipedesign/openGym/')), line)
    assert.ok(!line.includes('DuarteSantos8'), line)
  }
})
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `node --test scripts/hexgym/board.test.mjs`
Expected: FAIL, `Cannot find module` para `./board.mjs`.

- [ ] **Step 3: Implement `scripts/hexgym/board.mjs`**

Exporta `parseMeta(body: string)`, `currentPhase(milestones, config)`, `pickNext({ issues, items, config, phase })`, `refreshMoves({ issues, items, config, phase })` e `main(argv, { gh, out, err }) → Promise<number>`. Os dados vêm de três chamadas: `gh issue list -R lipedesign/openGym --state all --limit 500 --json number,title,state,labels,milestone,body,url`, `gh project item-list 6 --owner lipedesign --limit 500 --format json` (o número em `.items[].content.number`, a coluna em `.items[].status`) e `gh api 'repos/lipedesign/openGym/milestones?state=all&per_page=100'`. Um `gh(args) → string` padrão usa `execFileSync('gh', args, { encoding: 'utf8' })`. A issue que não está no Project conta como "A fazer". Uma dependência conta como fechada se a issue estiver fechada, de qualquer milestone. Saídas: 0 ok, 2 uso errado, 3 nada pronto.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `node --test scripts/hexgym/board.test.mjs`
Expected: PASS, 9 testes.

- [ ] **Step 5: Write the failing tests for `check.mjs`**

```js
test('the scripts part runs the node tests of scripts/hexgym', () => {
  assert.deepEqual(planChecks(['scripts']).map(c => [c.cmd, ...c.args]), [['node', '--test', 'scripts/hexgym/*.test.mjs']])
})
test('no part means every part, in PARTS order', () => {
  assert.deepEqual(planChecks([]), Object.values(PARTS).flat())
})
test('an unknown part fails with the list of parts', () => {
  assert.throws(() => planChecks(['x']), /parte desconhecida: x \(partes: scripts\)/)
})
test('runChecks stops at the first failure', async () => {
  const ran = []
  const r = await runChecks([{ name: 'a' }, { name: 'b' }, { name: 'c' }], async c => { ran.push(c.name); return c.name === 'b' ? 1 : 0 })
  assert.deepEqual(r, { ok: false, failed: 'b' }); assert.deepEqual(ran, ['a', 'b'])
})
```

O teste "unknown part" lista as partes que existirem no `PARTS`; as Tasks que acrescentam partes atualizam a mensagem esperada.

- [ ] **Step 6: Run the tests to verify they fail**

Run: `node --test scripts/hexgym/check.test.mjs`
Expected: FAIL, `Cannot find module` para `./check.mjs`.

- [ ] **Step 7: Implement `scripts/hexgym/check.mjs`**

`PARTS = { scripts: [{ name: 'testes dos scripts', cmd: 'node', args: ['--test', 'scripts/hexgym/*.test.mjs'] }] }`. O `PARTS` fica escrito sempre nesta ordem, e cada Task põe a sua parte no lugar dela: `scripts`, `engine`, `load`, `packages`, `app`. O `run` padrão usa `spawn` com `stdio: 'inherit'`, `cwd` relativo à raiz do repositório e `env` somado ao `process.env`. O `args` e o `env` podem ser um valor ou uma função que devolve o valor; a função só é chamada quando aquela checagem vai rodar, e o `--list` mostra `(calculado ao rodar)` no lugar, para uma parte que precisa do Xcode não quebrar as outras nem o `--list` numa máquina sem ele. A CLI imprime `▶ <nome>` antes de cada checagem e, no fim, `ok` ou `falhou: <nome>`, saindo com 1 na falha. `--list` imprime os comandos e não roda nada.

- [ ] **Step 8: Run the tests to verify they pass**

Run: `node scripts/hexgym/check.mjs scripts`
Expected: PASS nos dois arquivos de teste e `ok` no fim.

- [ ] **Step 9: Write `.claude/agents/hexgym-implementador.md`**

Frontmatter: `name: hexgym-implementador`, `description: Implementa uma Task do plano do HexGym numa worktree do fork lipedesign/openGym, com testes, e reporta no contrato do superpowers.`, `tools: Bash, Read, Edit, Write, Grep, Glob`. O corpo, em português, diz: trabalha só na worktree que recebe; a brief é o requisito e já traz as Restrições globais e o Foco da revisão do plano, que valem para tudo; TDD, um commit por passo de commit da brief; antes de reportar, roda `node scripts/hexgym/check.mjs` nas partes que tocou; nunca faz push, nunca abre PR, nunca faz merge e nunca chama outro agente; nunca mexe no upstream; nunca abre as mídias da Gym visual; arquivo novo em `.claude/` entra com `git add -f`; reporta como manda o `implementer-prompt.md` do superpowers:subagent-driven-development (DONE, DONE_WITH_CONCERNS, NEEDS_CONTEXT ou BLOCKED, com o relatório completo no arquivo que recebeu).

- [ ] **Step 10: Write `.claude/agents/hexgym-revisor.md`**

Frontmatter: `name: hexgym-revisor`, `description: Revisa um PR do HexGym no fork lipedesign/openGym contra a Task do plano e deixa a revisão como comentário no PR.`, `tools: Bash, Read, Grep, Glob`. Recebe o número do PR, a brief (com as Restrições globais e o Foco da revisão do plano), o relatório do implementador e, numa nova rodada, a lista do que ficou aberto. Lê `gh pr view <n> -R lipedesign/openGym --json number,title,body,headRefOid,files` e o diff, confere a brief, as Restrições globais e o checklist do PR. Os arquivos gerados (`apple/Packages/HexEngine/Sources/HexEngine/Resources/hexengine.js` e `apple/Packages/HexEngine/Tests/HexEngineTests/Cases/`) não entram na leitura, porque o script tem uns 2 MB: o diff sai de `git diff origin/develop...<sha> -- . ':(exclude)apple/Packages/HexEngine/Sources/HexEngine/Resources/hexengine.js' ':(exclude)apple/Packages/HexEngine/Tests/HexEngineTests/Cases'`, e para eles basta o `--check` da parte `engine` passar. Enquanto o `hexgym-ok` não for obrigatório (até a Task 11), roda `node scripts/hexgym/check.mjs` nas partes que o PR toca, numa worktree do commit do PR. Classifica em Crítico (quebra, perde dados, fere a licença ou a regra das mídias, segurança), Importante (falta um requisito da brief, teste que não prova o que diz, risco real) e Menor. Publica com `gh pr comment <n> -R lipedesign/openGym --body-file <arquivo>`, neste formato:

```markdown
## Revisão do segundo agente
Commit revisado: `<sha>`

### Crítico
- `arquivo:linha`: o problema e por que importa

### Importante

### Menor

**Pronto para merge:** sim | não
```

Nunca edita arquivo, faz push, merge ou aprova.

- [ ] **Step 11: Write `.claude/skills/hexgym-orquestrador/SKILL.md`**

Frontmatter:

```yaml
---
name: hexgym-orquestrador
description: Use para tocar o trabalho do HexGym no fork lipedesign/openGym, como "segue a fase", "pega a próxima issue" ou "roda o orquestrador". Leva a próxima issue pronta do milestone atual até o merge em develop, com a revisão de um segundo agente, e para nas decisões do founder.
---
```

O corpo tem estas seções, nesta ordem:

1. **Antes de tudo:** rodar da raiz do checkout; `gh auth status`; `git fetch origin`; ler as Restrições globais do plano da fase atual; nunca mexer no upstream nem no GitLab; todo `gh` com `-R lipedesign/openGym`.
2. **O laço:**
   1. `node scripts/hexgym/board.mjs refresh`, depois `node scripts/hexgym/board.mjs next`. Saída 3: avisar o founder do que espera e parar.
   2. Com `resume: true`, achar a branch `feature/<n>-*` e o PR, e seguir de onde parou. Sem branch nem PR, é uma Task feita à mão: não mexer nela, avisar o founder e parar.
   3. `board.mjs move <n> doing`, `git worktree add .claude/worktrees/<n> -b feature/<n>-<nome-curto> origin/develop` e, na worktree nova, `npm ci` em `frontend/` (as partes `engine` e `load` e os testes do lib precisam dele).
   4. A brief, num arquivo: as seções "Restrições globais" e "Foco da revisão" do plano (`sed -n '/^## Restrições globais/,/^## Mapa dos arquivos/p' <plano> | sed '$d'`), seguidas da saída de `bash <skill subagent-driven-development>/scripts/task-brief <plano> <task>`, com o plano e a Task da linha `Plano:` da issue. Issue sem Task no plano: as duas seções do plano da fase atual e o corpo da issue.
   5. Implementar com o agente `hexgym-implementador` (modelo pela seção 8), passando a brief, o arquivo de relatório, a worktree e as interfaces das Tasks anteriores.
   6. Na worktree, `node scripts/hexgym/check.mjs`. Vermelho volta para o implementador.
   7. Push da branch e `gh pr create -R lipedesign/openGym --base develop` com o título da issue e o corpo no modelo de PR, com `Closes #<n>`. Depois, `board.mjs move <n> review`.
   8. Revisão com o agente `hexgym-revisor`, com o número do PR, a mesma brief e o relatório do implementador; ele comenta no PR.
   9. Correções como no superpowers:subagent-driven-development: rodadas 1 a 3 com o mesmo implementador, 4 e 5 com um novo num modelo mais forte, cada rodada com uma nova revisão só do que mudou; depois da quinta, o orquestrador decide cada ponto aberto e escreve a decisão no PR.
   10. Merge quando os checks obrigatórios estão verdes (`gh pr checks <pr> -R lipedesign/openGym --required`) e a última revisão diz "Pronto para merge: sim" para o commit atual: `gh pr merge <pr> -R lipedesign/openGym --squash --match-head-commit <sha> --subject "<título do PR> (#<pr>)" --body-file <arquivo>`, com o corpo dizendo o que entrou, a revisão e `Closes #<n>`. Depois, na raiz do checkout, os passos da Task cujo título começa com "After the merge" (como nas Tasks 11 e 14), e então `board.mjs move <n> done`.
   11. `git worktree remove .claude/worktrees/<n>`, apagar a branch local e voltar ao passo 1.
3. **Tarefa sem código:** fazer os passos, conferir cada um, comentar na issue o que foi feito com a prova (a saída dos comandos), e `board.mjs move <n> done`. Numa Task do founder (como a 12), quando ele tira a etiqueta de espera, o orquestrador só roda os passos de conferência: o que a issue diz que é do founder, ele nunca faz.
4. **Quando parar e chamar o founder**, como na seção 9.1: decisão de visual ou de produto (etiqueta `decisão do founder`, comentário na issue, e segue em outra issue); tudo que envolva dinheiro, contas, loja ou falar com o Duarte; o fim de cada fase; quando trava de verdade, depois de tentar os caminhos que tem. O chamado vai na conversa e como comentário na issue ou no PR.
5. **Fim de fase:** a última Task do plano da fase. Nada entra em `main` sem a aprovação do founder na conversa.
6. **Regras do repositório:** as Restrições globais do plano; o PR de sync, as releases e os hotfixes entram com merge normal, nunca squash; nada em `data/` nem em `catalogue/media/`.
7. **Quando a sessão perde o fio:** o quadro, o git e os comentários dos PRs são o registro. `next` retoma o que estava em revisão ou em andamento, e o ledger do superpowers fica em `.superpowers/sdd/<plano>/progress.md`.
8. **Modelos:** implementador `sonnet`, ou `opus` quando a Task pede desenho (projeto Xcode, o script do motor, o pacote HexEngine); revisor `opus` em código, `sonnet` em documentação; sempre passar o modelo de forma explícita.

- [ ] **Step 12: Write `scripts/hexgym/README.md`**

Uma tabela de duas colunas, no formato do `scripts/README.md` do openGym, com cada script de `scripts/hexgym/` e o que ele faz, mais uma linha dizendo que a skill `hexgym-orquestrador` é quem usa os dois primeiros.

- [ ] **Step 13: Check against the real board**

Run: `node scripts/hexgym/board.mjs phase && node scripts/hexgym/board.mjs refresh && node scripts/hexgym/board.mjs next`
Expected: `{"number":1,"title":"Fase 0: Fundação"}`, e o `next` devolve a issue desta Task com `"resume":true`: ela é a única em andamento, porque a #3 e a #14 fecharam com o PR do plano.

- [ ] **Step 14: Commit**

```bash
git add scripts/hexgym
git add -f .claude/skills/hexgym-orquestrador/SKILL.md .claude/agents/hexgym-implementador.md .claude/agents/hexgym-revisor.md
git commit -m "Orquestrador do HexGym: o quadro, as checagens e os agentes"
```

---

### Task 2: Os workflows herdados e o check obrigatório

**Issue:** #3. **Quem faz:** o tech lead, depois do clique do founder (passo 1). Sem código.

- [ ] **Step 1: Confirm the fork's Actions run on events**

O `"enabled":true` de `gh api repos/lipedesign/openGym/actions/permissions` e os workflows como `active` não provam que eles rodam. Os nove apareceram às 23:48:32Z de 31/10, dois segundos depois do merge do #7 em `develop`: foi o merge que registrou os arquivos. Em 01/11/2026, a abertura do PR #28, um commit novo nele e um push numa branch `ci-*` não dispararam nada, e o `workflow_dispatch` do `test.yml` rodou e passou. Num fork, o GitHub só roda por evento depois que o dono clica em "I understand my workflows, go ahead and enable them", na aba Actions. O clique é do founder, e a #3 fica com a etiqueta `bloqueado` até ele.

Run: depois do clique, um commit num PR aberto e `gh run list -R lipedesign/openGym --event pull_request --limit 1`; e `gh api repos/lipedesign/openGym/actions/workflows --jq '.workflows[] | "\(.state) \(.path)"'`
Expected: uma execução do `Tests` com evento `pull_request`, e os sete do passo 2 ainda `disabled_manually`.

- [x] **Step 2: Disable the seven inherited workflows**

`gh workflow disable <id> -R lipedesign/openGym` para `audit.yml` (403149169), `cla-issue.yml` (403149170), `cla.yml` (403149171), `docker-publish.yml` (403149172), `mirror.yml` (403149174), `pages.yml` (403149175) e `release-check.yml` (403149176). Os sete ficaram `disabled_manually`; `test.yml` (403149177) e `ios.yml` (403149173) seguem ativos. Feito em 31/10/2026.

- [ ] **Step 3: See `tests-ok` pass on a pull request**

Run: `gh pr checks <pr> -R lipedesign/openGym`, no PR do passo 1, com a execução vinda do `pull_request` (a do `workflow_dispatch` não prova que o check chega sozinho).
Expected: `tests-ok` com `pass`.

- [ ] **Step 4: Require `tests-ok` on both branches**

Hoje `required_status_checks` é nulo nas duas, então vai um `PUT` da proteção inteira, com os valores atuais mais o check. Salvar antes a saída de `gh api repos/lipedesign/openGym/branches/<branch>/protection`. Depois, `gh api -X PUT repos/lipedesign/openGym/branches/develop/protection --input <arquivo>`, com:

```json
{
  "required_status_checks": { "strict": false, "checks": [{ "context": "tests-ok", "app_id": 15368 }] },
  "enforce_admins": true,
  "required_pull_request_reviews": { "required_approving_review_count": 0 },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

E o mesmo em `main`, com `"strict": true`.

- [ ] **Step 5: Verify the protection**

Run: `gh api repos/lipedesign/openGym/branches/develop/protection --jq '.required_status_checks.checks'` e o mesmo para `main`
Expected: `[{"context":"tests-ok","app_id":15368}]` nas duas, `strict` falso em `develop` e verdadeiro em `main`, e o resto igual ao que foi salvo no passo 4.

- [ ] **Step 6: Close the issue**

Comentar na #3 o que foi feito, com a saída dos passos 3 e 5, e `node scripts/hexgym/board.mjs move 3 done` (ou o `gh project item-edit` com a opção `98236657`, se a Task 1 ainda não entrou).

---

### Task 3: As branches e as etiquetas herdadas

**Issue:** #11. **Sem código.**

- [ ] **Step 1: Save the current lists**

O ledger é `.superpowers/sdd/2026-10-31-fase-0-fundacao/`, fora do git (`.gitignore:20`).

Run: `mkdir -p .superpowers/sdd/2026-10-31-fase-0-fundacao`, `git ls-remote --heads origin > .superpowers/sdd/2026-10-31-fase-0-fundacao/heads-antes.txt` e `gh label list -R lipedesign/openGym --limit 100 --json name,description,color > .superpowers/sdd/2026-10-31-fase-0-fundacao/etiquetas-antes.json`

- [ ] **Step 2: List the branches to keep**

`main`, `develop` e as branches dos PRs abertos: `gh pr list -R lipedesign/openGym --state open --json headRefName --jq '.[].headRefName'`.

- [ ] **Step 3: Delete each inherited branch that is identical in the openGym**

Os SHAs vêm do `git`, que lê o upstream sem `gh`: `git ls-remote --heads origin` e `git ls-remote --heads upstream` (o remoto `upstream` não tem push). Para cada outra branch `b`, com o SHA igual nos dois: `gh api -X DELETE repos/lipedesign/openGym/git/refs/heads/$b`. Diferente, ou ausente no upstream: fica, e entra na lista do comentário com o motivo.

- [ ] **Step 4: Clean the labels**

`gh label delete <nome> -R lipedesign/openGym --yes` para `duplicate`, `good first issue`, `help wanted`, `invalid`, `question` e `wontfix`. A `accessibility` vira etiqueta de área (decisão do tech lead, registrada na seção 9.1 da especificação): `gh label edit accessibility -R lipedesign/openGym --name acessibilidade --description "Área: VoiceOver, Dynamic Type, contraste e movimento reduzido"`.

- [ ] **Step 5: Verify**

Run: `git ls-remote --heads origin` e `gh label list -R lipedesign/openGym --limit 100 --json name --jq '[.[].name] | sort'`
Expected: só `main`, `develop`, as branches de PR aberto e as que ficaram com motivo; e exatamente `acessibilidade`, `bloqueado`, `bug`, `build`, `chore`, `dados`, `decisão do founder`, `design-system`, `docs`, `feature`, `motor`, `sync`, `upstream`, `watch`, `widgets`.

- [ ] **Step 6: Close the issue**

Comentar na #11 o que saiu, o que ficou e por quê, e `node scripts/hexgym/board.mjs move 11 done`.

---

### Task 4: O motor sem React

**Issue:** #16. São as três mudanças pequenas no código do openGym da seção 8.2. Cada uma vai num commit com mensagem em inglês, no estilo do openGym (`Área: o que mudou`), para poder ser proposta ao openGym. Propor fica com o founder (seção 9.1: falar com o Duarte).

**Files:**
- Create: `frontend/src/lib/state-core.js`, `frontend/src/lib/state-core.test.js`
- Create: `frontend/src/store/useStore.state-core.test.jsx`
- Modify: `frontend/src/store/useStore.js` (de `DEF`, na linha 90, até `restoredStateFor`, na 356, e `loadState`)
- Modify: `frontend/src/lib/coach.js:21`, `frontend/src/lib/duration.js:5`
- Create: `frontend/src/lib/plan-print.js`
- Modify: `frontend/src/lib/plan-share.js` (o import da linha 27 e a seção "printable PDF", da linha 366 ao fim)
- Modify: `frontend/src/sheets.jsx:39`, `frontend/src/views/RoutineEdit.jsx:20`, `frontend/src/lib/report-print.js:12`, `frontend/src/lib/plan-print.test.js:3`, `frontend/src/lib/speed.test.js:6`, `frontend/src/lib/failure-sets.test.js:10`, `frontend/src/views/RoutineEdit.print.test.jsx:14,23`, `frontend/scripts/pdf/render-samples.mjs:44` (o `npm run pdf:check`, que a CI não roda)
- Modify: o comentário de `frontend/src/lib/mobile.js:318`, que cita o caminho

**Interfaces:**
- Produces, em `frontend/src/lib/state-core.js`:
  - `DEF`, `clone(o)`, `draftOf(prev) → { S, done() }`, `restartedState(cur)`, `hasData(st) → boolean` e `restoredStateFor(local, remote, dirty = false)`, como estão hoje;
  - `detectedLang(tag = globalThis.navigator?.language) → string` e `freshState(tag?) → object`: a língua do aparelho pode vir de fora, e o padrão continua o `navigator`;
  - `stateFromSaved(saved, tag?) → object`, novo: o ramo de `loadState` que lê uma cópia salva (`sanitizeAccent(Object.assign(clone(DEF), saved))`, com `detectedLang(tag)` quando a cópia não tem `lang`). O `loadState` passa a usar.
  - `useStore.js` reexporta `DEF`, `draftOf`, `freshState`, `restartedState`, `restoredStateFor` e `hasData`, e nenhum import do app muda.
- Produces, em `frontend/src/lib/plan-print.js`: `printedName(ex, fallback)`, `planPrintHTML(S, owner, { routineId, probe } = {})` e `printPlan(S, owner, opts)`, saídos de `plan-share.js` sem mudar nada. O `plan-share.js` fica com `buildPlanBundle`, `parsePlan` e `mergePlan`, e não importa mais o `print-doc.js` (que importa o `mobile.js`).
- `coach.js` e `duration.js` importam `t` e `tn` de `i18n-core.js`, as mesmas funções que o `i18n.js` reexporta.

- [ ] **Step 1: Install and take the baseline**

Run: `cd frontend && npm ci && npm test`
Expected: tudo verde. O relatório anota quantos arquivos e testes passaram, para os passos 5 e 9.

- [ ] **Step 2: Write the failing tests for `state-core.js`**

```js
import { test, expect, vi } from 'vitest'
import { DEF, freshState, stateFromSaved, detectedLang } from './state-core.js'

test('a fresh state is what the web app starts with', () => {
  const s = freshState('pt-BR')
  expect([s.lang, s.langAuto, s.weighIn, s.gifSize]).toEqual(['en', true, false, 'mini'])
  expect(freshState('ar-EG').lang).toBe('ar')
})
test('without a navigator the language is English', () => {
  vi.stubGlobal('navigator', undefined)                  // o Node 22 tem navigator.language, da máquina
  try { expect(detectedLang()).toBe('en') } finally { vi.unstubAllGlobals() }
})
test('a saved copy keeps the keys this version does not know', () => {
  const s = stateFromSaved({ chaveDoFuturo: { x: [1, 2] }, unit: 'lb' })
  expect(s.chaveDoFuturo).toEqual({ x: [1, 2] }); expect(s.unit).toBe('lb'); expect(s.routines).toEqual(DEF.routines)
})
test('a saved copy without a language gets the detected one', () => {
  expect(stateFromSaved({}, 'ar-EG').lang).toBe('ar'); expect(stateFromSaved({ lang: 'de' }, 'ar-EG').lang).toBe('de')
})
```

O `state-core.test.js` só importa o `state-core.js`, para rodar também contra o script (Task 6). A reexportação fica num arquivo à parte, `frontend/src/store/useStore.state-core.test.jsx`, com o mesmo cabeçalho `// @vitest-environment happy-dom` e os mesmos dois `vi.mock` de `useStore.default-lang.test.jsx`:

```js
test('useStore re-exports the same objects', () => {
  expect(store.DEF).toBe(DEF); expect(store.freshState).toBe(freshState); expect(store.restartedState).toBe(restartedState)
})
```

- [ ] **Step 3: Run them to verify they fail**

Run: `cd frontend && npx vitest run src/lib/state-core.test.js src/store/useStore.state-core.test.jsx`
Expected: FAIL nos dois, porque `state-core.js` não existe.

- [ ] **Step 4: Move the definitions**

Vão para `state-core.js` como estão, com os comentários; mudam só as duas assinaturas, e entra o `stateFromSaved`. Em `useStore.js` saem os imports que só essas definições usavam, o `loadState` chama `stateFromSaved(JSON.parse(raw))`, o `clone` vem de `state-core.js` e entram as reexportações (o `hasData` continua no `export` do fim do arquivo).

- [ ] **Step 5: Run the whole suite**

Run: `cd frontend && npm test`
Expected: PASS, com os números do passo 1 mais os 5 testes novos.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/lib/state-core.js frontend/src/lib/state-core.test.js frontend/src/store/useStore.state-core.test.jsx frontend/src/store/useStore.js
git commit -m "Engine: DEF and the state helpers in lib/state-core.js, so a host without React can start and read a profile"
```

- [ ] **Step 7: Point `coach.js` and `duration.js` at the i18n core, and commit**

Trocar `from './i18n.js'` por `from './i18n-core.js'` nas duas linhas.

Run: `grep -n "i18n.js'" frontend/src/lib/coach.js frontend/src/lib/duration.js; cd frontend && npx vitest run src/lib/coach src/lib/duration`
Expected: o `grep` não acha nada, e os testes passam.

```bash
git add frontend/src/lib/coach.js frontend/src/lib/duration.js
git commit -m "Engine: coach.js and duration.js read t and tn from i18n-core.js, which does not pull React"
```

- [ ] **Step 8: Move the printable plan to `plan-print.js`**

A seção "printable PDF" de `plan-share.js` vai inteira para `plan-print.js`. O que ela usa do resto de `plan-share.js` (como o `cleanIntensifier`) passa a ser exportado e importado de lá. Os oito importadores da lista de arquivos trocam o caminho: o `vi.mock` de `RoutineEdit.print.test.jsx` passa a mirar `../lib/plan-print.js`, e o `render-samples.mjs` carrega `/src/lib/plan-print.js` para o `planPrintHTML`. O comentário de `mobile.js:318` passa a citar `lib/plan-print.js`.

Run: `grep -n "print-doc" frontend/src/lib/plan-share.js` e `grep -rn "plan-share" frontend/scripts`
Expected: nada, nos dois.

- [ ] **Step 9: Run the whole suite and the locale checks**

Run: `cd frontend && npm test && node scripts/check-locales.mjs && node scripts/check-source-strings.mjs --strict`
Expected: verde, com os mesmos números do passo 5.

- [ ] **Step 10: Commit**

```bash
git add frontend/src/lib/plan-share.js frontend/src/lib/plan-print.js frontend/src/sheets.jsx frontend/src/views/RoutineEdit.jsx frontend/src/lib/report-print.js frontend/src/lib/plan-print.test.js frontend/src/lib/speed.test.js frontend/src/lib/failure-sets.test.js frontend/src/views/RoutineEdit.print.test.jsx frontend/scripts/pdf/render-samples.mjs frontend/src/lib/mobile.js
git commit -m "Plans: the printable plan in lib/plan-print.js, so plan-share.js no longer reaches the print and mobile code"
```

---

### Task 5: O script do motor

**Issue:** #17.

**Files:**
- Create: `apple/Packages/HexEngine/JS/values.js`, `polyfills.js`, `runtime.js`
- Create: `apple/Packages/HexEngine/JS/values.test.mjs`, `polyfills.test.mjs`, `runtime.test.mjs`, `build.test.mjs`
- Create: `apple/Packages/HexEngine/JS/test-fixtures/imports-react.js` (uma linha: `import 'react'`), `dynamic-import.js` (`export const load = name => import(name)`) e `import-meta.js` (`export const here = import.meta.url`)
- Create: `scripts/build-hexgym-engine.mjs`
- Create (gerado): `apple/Packages/HexEngine/Sources/HexEngine/Resources/hexengine.js`
- Create: `apple/.gitattributes`
- Modify: `scripts/hexgym/check.mjs`, `scripts/hexgym/check.test.mjs` (parte `engine`)

**Interfaces:**
- Consumes: `state-core.js` e os módulos liberados na Task 4.
- Produces:
  - `values.js`: `encodeValue(v)` e `decodeValue(v)`. JSON comum, mais `{"$date": ms}`, `{"$undefined": true}` e `{"$number": "NaN" | "Infinity" | "-Infinity"}`. Map, Set, função ou símbolo lançam `Error('valor que o motor não sabe passar: <tipo>')`.
  - `polyfills.js`: exporta `cloneStructured(v)` e o instala como `structuredClone` só quando o global não existe. Copia objetos, arrays, `Date`, `Map`, `Set`, valores `undefined` e referências circulares; função ou símbolo lança um erro com `name` `DataCloneError`. Os outros complementos da seção 8.2 (`console` e os timers) vêm do Swift, na Task 7.
  - `runtime.js`, o que o Swift chama, sempre com texto JSON:
    - `info() → string`: `{"exercises": CATALOGUE.length, "openGymVersion": __APP_VERSION__}`, com `"dev"` quando o global não existe (nos testes sem build);
    - `setDeviceLanguage(tag)`;
    - `freshDocument() → string`: o documento passa a ser `freshState(tag)`;
    - `restore(json)`: o documento passa a ser `stateFromSaved(JSON.parse(json), tag)`; o que não for objeto lança `TypeError('HexEngine: o documento não é um objeto JSON')`;
    - `document() → string`: o `stateJson` do documento; antes do primeiro, `Error('HexEngine: nenhum documento aberto')`;
    - `makeCall(modules) → call(name, argsJson) → string`: `name` é `"<caminho do módulo>#<export>"`, como `"frontend/src/lib/onerm.js#estimate1RM"`; os argumentos são `decodeValue(JSON.parse(argsJson))` e a resposta é `JSON.stringify(encodeValue({ returned, args }))`, com os argumentos depois da chamada, para mostrar o que a função mudou; nome que não existe lança um erro que diz o nome.

    Cada troca de documento cura e registra os exercícios personalizados e os apelidos, como o boot do app web (`useStore.js:1352-1354`): `healCustomEx`, `registerCustom` e `registerExerciseAliases`.
  - `scripts/build-hexgym-engine.mjs`: `engineGraph(repo) → Promise<{ [módulo]: string[] }>`, `cleanModules(graph) → string[]` (os `frontend/src/lib/*.js` limpos, em ordem alfabética), `buildEngine(repo, { extra = [] } = {}) → Promise<{ code, modules }>` e `main(argv, io) → Promise<number>`, com `io = { build, readFile, writeFile, out, err }` e os reais como padrão. CLI: `node scripts/build-hexgym-engine.mjs [--check]`.
  - O `hexengine.js`: um script clássico que cria o global `HexEngine` com o que `runtime.js` exporta, `call = makeCall(__modules)` e `__modules`, com cada módulo do motor pelo caminho a partir da raiz do repositório.
  - A parte `engine` do `check.mjs`.

**O que é o motor:** todo módulo de `frontend/src/lib` (sem os testes e sem `fixtures/`) que não alcança, por nenhum caminho de imports estáticos ou dinâmicos, um pacote, um módulo do Node ou um arquivo fora de `frontend/src/lib` e `api/coach/core`, mais os JSON e os módulos de `api/coach/core` que ele importa. Assim, módulo novo do openGym que não puxa o navegador entra sozinho, e o `--check` mostra a mudança.

**As decisões do build:**
- O Vite vem de `frontend/node_modules`, porque a raiz não tem: `createRequire(<frontend/package.json>).resolve('vite')` (no Vite 8, o `exports["."]` é o texto `./dist/node/index.js`), importado por `pathToFileURL`. Sempre com `configFile: false` e `root: repo`, para nada do `vite.config.js` do app entrar.
- `engineGraph` faz um build de sondagem, em formato ES e sem gravar, com uma entrada que importa todo módulo de `frontend/src/lib`. Um plugin anota cada import em `resolveId`, estático e dinâmico, e marca como externo tudo fora das duas pastas. Os caminhos ficam relativos à raiz, os pacotes ficam com o nome (`react`, `@capacitor/core`) e os módulos do Node com `node:`.
- `buildEngine` faz o build de verdade:
  - `build.lib` em `iife` com `name: 'HexEngine'`, `write: false`, `minify: false` (o erro do JS chega ao Swift com uma linha que dá para ler) e `target: 'es2022'`;
  - uma entrada virtual que importa `polyfills.js` primeiro, depois `runtime.js` e um `import * as` para cada módulo limpo, juntos em `__modules`;
  - `define: { __APP_VERSION__: JSON.stringify(<versão de frontend/package.json>) }`;
  - um plugin `enforce: 'pre'` que troca cada `import.meta.env` por `({})`: é o "`import.meta.env` vazio" da seção 8.2, e por isso nenhuma variável `VITE_` da máquina entra no script. Depois da troca, o `transform` dele lê cada `.js` com `this.parse` e, se ainda sobrar um `MetaProperty` com `meta.name === 'import'`, falha com `o motor não pode usar import.meta (em <módulo>)`;
  - um `resolveId` que falha com `o motor não pode importar <x> (em <módulo>)` para qualquer coisa fora das duas pastas e de `apple/Packages/HexEngine/JS`;
  - um `generateBundle` que lê a saída com `this.parse` e falha com `o script do motor ficou com import dinâmico` se achar um `ImportExpression`. As duas conferências vão pela árvore do código, nunca por expressão regular, porque há comentários que falam de `import.meta.glob` e de `import()`;
  - o `banner` `// Gerado por scripts/build-hexgym-engine.mjs a partir do openGym <versão>, com <n> módulos. Não edite à mão.`
- A CLI grava `apple/Packages/HexEngine/Sources/HexEngine/Resources/hexengine.js`. Com `--check`, só compara (arquivo que falta conta como velho) e sai com 1 e `apple/Packages/HexEngine/Sources/HexEngine/Resources/hexengine.js está desatualizado. Rode: node scripts/build-hexgym-engine.mjs`, como os outros `--check` do repositório.
- `apple/.gitattributes` marca `Packages/HexEngine/Sources/HexEngine/Resources/hexengine.js` e `Packages/HexEngine/Tests/HexEngineTests/Cases/*.json` (Task 7) com `linguist-generated=true`, para o GitHub dobrar esses diffs.

- [ ] **Step 1: Write the failing tests for `values.js`, `polyfills.js` and `runtime.js`**

```js
// values.test.mjs
test('dates, undefined and the numbers JSON cannot hold go and come back', () => {
  const v = { d: new Date(0), u: undefined, n: NaN, i: -Infinity, list: [1, { x: undefined }] }
  assert.deepStrictEqual(decodeValue(JSON.parse(JSON.stringify(encodeValue(v)))), v)
})
test('a Map, a Set or a function is refused', () => {
  for (const v of [new Map(), new Set(), () => 1]) assert.throws(() => encodeValue(v), /valor que o motor não sabe passar/)
})

// polyfills.test.mjs
test('the copy matches the native structuredClone', () => {
  const a = { n: 1, u: undefined, d: new Date(5), m: new Map([[1, { y: 2 }]]), s: new Set([1, 2]), list: [1, [2]] }
  a.self = a
  const c = cloneStructured(a)
  assert.deepStrictEqual(c, structuredClone(a)); assert.notEqual(c.list, a.list); assert.equal(c.self, c)
})
test('a function cannot be copied', () => assert.throws(() => cloneStructured({ f() {} }), e => e.name === 'DataCloneError'))
test('the native one stays when it exists', () => assert.notEqual(globalThis.structuredClone, cloneStructured))

// runtime.test.mjs: R é `import * as R from './runtime.js'`; exerciseOf, estimate1RM e isoOf vêm direto de frontend/src/lib
test('a fresh document is the web app first run in the device language', () => {
  R.setDeviceLanguage('ar-EG'); assert.equal(JSON.parse(R.freshDocument()).lang, 'ar')
  R.setDeviceLanguage('pt-BR'); const d = JSON.parse(R.freshDocument())
  assert.deepEqual([d.lang, d.langAuto, d.weighIn, d.gifSize], ['en', true, false, 'mini'])
})
test('restore keeps the keys it does not know', () => {
  R.restore('{"chaveDoFuturo":{"x":[1,2]}}'); assert.deepEqual(JSON.parse(R.document()).chaveDoFuturo, { x: [1, 2] })
})
test('restore refuses what is not a JSON object', () => {
  assert.throws(() => R.restore('[1]'), /o documento não é um objeto JSON/); assert.throws(() => R.restore('{'), SyntaxError)
})
test('each document brings its own custom exercises', () => {
  R.restore('{"customEx":[{"id":"c1","n":"Remada do HexGym","bp":"back"}]}'); assert.equal(exerciseOf('c1')?.n, 'Remada do HexGym')
  R.restore('{}'); assert.equal(exerciseOf('c1'), undefined)
})
test('call runs a function and shows the arguments after the call', () => {
  const call = R.makeCall({ 'frontend/src/lib/onerm.js': { estimate1RM } })
  assert.deepEqual(JSON.parse(call('frontend/src/lib/onerm.js#estimate1RM', '[100,5]')), { returned: estimate1RM(100, 5), args: [100, 5] })
  assert.throws(() => call('frontend/src/lib/nope.js#x', '[]'), /frontend\/src\/lib\/nope\.js#x/)
})
test('call decodes the arguments it receives', () => {
  const call = R.makeCall({ 'frontend/src/lib/format.js': { isoOf } }), noon = Date.UTC(2026, 9, 25, 12)
  assert.equal(JSON.parse(call('frontend/src/lib/format.js#isoOf', JSON.stringify([{ $date: noon }]))).returned, isoOf(new Date(noon)))
})
test('document before any document fails', async () => {
  const fresh = await import('./runtime.js?antes'); assert.throws(() => fresh.document(), /nenhum documento aberto/)
})
```

- [ ] **Step 2: Run them to verify they fail**

Run: `node --test 'apple/Packages/HexEngine/JS/*.test.mjs'`
Expected: FAIL, `Cannot find module` para os três módulos.

- [ ] **Step 3: Implement `values.js`, `polyfills.js` and `runtime.js`**

- [ ] **Step 4: Run them to verify they pass**

Run: o comando do passo 2
Expected: PASS, 12 testes.

- [ ] **Step 5: Write the failing tests for the build**

Em `build.test.mjs`, `repo` é a raiz do repositório e `engine()` guarda o resultado do primeiro `buildEngine(repo)` do arquivo. `fakeIo({ built, current })` devolve um `io` cujo `build` resolve `{ code: built, modules: [] }` e cujo `readFile` devolve `current`, e que guarda cada gravação em `writes` e o que foi para `err` em `stderr`:

```js
const L = 'frontend/src/lib/'
test('a module is clean only when nothing it reaches leaves the engine folders', () => {
  const graph = {
    [L + 'a.js']: [L + 'b.js'], [L + 'b.js']: ['react'], [L + 'c.js']: [L + 'a.js'],
    [L + 'd.js']: [L + 'data.json', 'api/coach/core/x.js'], [L + 'data.json']: [], 'api/coach/core/x.js': [],
    [L + 'e.js']: ['frontend/src/store/useStore.js'], [L + 'f.js']: ['node:fs'],
    [L + 'g.js']: [L + 'h.js'], [L + 'h.js']: [L + 'g.js'], [L + 'i.js']: [L + 'j.js'], [L + 'j.js']: [L + 'i.js', '@capacitor/core'],
  }
  assert.deepEqual(cleanModules(graph), [L + 'd.js', L + 'g.js', L + 'h.js'])
})
test('the engine has what the app needs and none of the browser side', async () => {
  const { modules } = await engine()
  for (const m of ['progression', 'sync-merge', 'state-core', 'coach', 'duration', 'plan-share', 'exercises']) assert.ok(modules.includes(`${L}${m}.js`), m)
  for (const m of ['i18n', 'mobile', 'api', 'print-doc', 'plan-print']) assert.ok(!modules.includes(`${L}${m}.js`), m)
})
test('the script is the same on every run, whatever VITE_ variables the machine has', async () => {
  const { code } = await engine(); process.env.VITE_IMG_BASE = 'https://example.com/'
  try { assert.equal((await buildEngine(repo)).code, code) } finally { delete process.env.VITE_IMG_BASE }
})
test('the script has no path of this machine', async () => assert.ok(!(await engine()).code.includes(repo)))
test('a module forced in with a computed import fails the build', async () => {
  await assert.rejects(buildEngine(repo, { extra: ['apple/Packages/HexEngine/JS/test-fixtures/dynamic-import.js'] }), /o script do motor ficou com import dinâmico/)
})
test('a module forced in with import.meta fails with its name', async () => {
  await assert.rejects(buildEngine(repo, { extra: ['apple/Packages/HexEngine/JS/test-fixtures/import-meta.js'] }),
    /o motor não pode usar import\.meta \(em apple\/Packages\/HexEngine\/JS\/test-fixtures\/import-meta\.js\)/)
})
test('the script loads and answers', async () => {
  const E = new Function((await engine()).code + '\nreturn HexEngine')()
  assert.ok(JSON.parse(E.info()).exercises > 5000); E.setDeviceLanguage('pt-BR'); assert.equal(JSON.parse(E.freshDocument()).langAuto, true)
})
test('a module forced in that imports a package fails with its name', async () => {
  await assert.rejects(buildEngine(repo, { extra: ['apple/Packages/HexEngine/JS/test-fixtures/imports-react.js'] }),
    /o motor não pode importar react \(em apple\/Packages\/HexEngine\/JS\/test-fixtures\/imports-react\.js\)/)
})
test('--check reports a stale script and writes nothing', async () => {
  const io = fakeIo({ built: 'novo', current: 'velho' })
  assert.equal(await main(['--check'], io), 1); assert.match(io.stderr, /hexengine\.js está desatualizado/); assert.equal(io.writes.length, 0)
  assert.equal(await main(['--check'], fakeIo({ built: 'novo', current: 'novo' })), 0)
})
```

- [ ] **Step 6: Run them to verify they fail**

Run: `node --test apple/Packages/HexEngine/JS/build.test.mjs`
Expected: FAIL, `Cannot find module` para `scripts/build-hexgym-engine.mjs`.

- [ ] **Step 7: Implement `scripts/build-hexgym-engine.mjs`**

Seguindo as decisões acima.

- [ ] **Step 8: Generate the script and run every test**

Run: `node scripts/build-hexgym-engine.mjs && node --test 'apple/Packages/HexEngine/JS/*.test.mjs'`
Expected: o build imprime o número de módulos e o tamanho do script, e os testes dão PASS, 21 no total.

- [ ] **Step 9: Add the `engine` part to `check.mjs`**

`PARTS.engine`: `node scripts/build-hexgym-engine.mjs --check` e `node --test 'apple/Packages/HexEngine/JS/*.test.mjs'`. Atualizar a mensagem esperada do teste "unknown part".

Run: `node scripts/hexgym/check.mjs scripts engine`
Expected: `ok`.

- [ ] **Step 10: Commit**

```bash
git add scripts/build-hexgym-engine.mjs apple/.gitattributes apple/Packages/HexEngine/JS apple/Packages/HexEngine/Sources/HexEngine/Resources/hexengine.js scripts/hexgym/check.mjs scripts/hexgym/check.test.mjs
git commit -m "Script do motor: os módulos limpos do lib num HexEngine só, com --check"
```

---

### Task 6: Os testes do lib contra o script e a carga no jsc

**Issue:** #18.

**Files:**
- Create: `frontend/vitest.hexengine.config.js`
- Create: `scripts/hexgym/engine-tests.mjs`, `scripts/hexgym/engine-tests.test.mjs`
- Create: `scripts/hexgym/engine-load.mjs`, `scripts/hexgym/engine-load.test.mjs`
- Modify: `scripts/hexgym/check.mjs`, `scripts/hexgym/check.test.mjs` (a parte `engine` ganha o Vitest, e entra a parte `load`)

**Interfaces:**
- Consumes: o script, com `__modules` (Task 5); `buildDemoState()` de `frontend/src/lib/demoSeed.js`; `draftOf` e `stateFromSaved` (Task 4); `buildCombinedEntries` de `frontend/src/lib/session-merge.js`.
- Produces:
  - `scripts/hexgym/engine-tests.mjs`: `pickEngineTests(files, engineModules) → { picked: string[], skipped: [{ path, reason }] }`, com `files` como `[{ path, text }]`, `engineModules` como um `Set` e os caminhos sempre a partir da raiz do repositório;
  - `cd frontend && npx vitest run --config vitest.hexengine.config.js`;
  - `node scripts/hexgym/engine-load.mjs [--workouts N]`, que exporta `padHistory(S, total) → S` e `overBudget(results, slack = 1) → string[]`;
  - a parte `load`.

**O config do Vitest:**
- Roda o script uma vez, com `new Function(code + '\nreturn HexEngine')`, para saber os módulos de `__modules` e o que cada um exporta.
- Escolhe os testes com `pickEngineTests`, sobre os `*.test.js` e `*.test.jsx` de `src/lib`. Entra o teste em que cada import (`import … from`, `import '…'`, `export … from` e `import('…')` com texto fixo) é um módulo do script, `vitest`, `fast-check`, um módulo `node:` ou um `.json`, com pelo menos um módulo do script, e que não chama `vi.mock`, `vi.doMock`, `vi.stubEnv` nem `vi.resetModules`: um mock não alcança o código que já está dentro do script, e o ambiente ficou fixo no build. O que fica de fora leva o motivo, nesta ordem: o primeiro import fora da lista (`importa <x>`, com o nome do pacote ou o caminho a partir da raiz), a primeira das quatro chamadas (`chama vi.mock`), ou `não importa nenhum módulo do motor`.
- Tira os de `EXCLUDED`, um objeto `arquivo → motivo` no próprio config, só para teste que falha por causa do redirecionamento. O primeiro candidato é `state-json.test.js`, cuja checagem só existe com `MODE === 'test'`. Cada entrada passa pela revisão.
- Lança erro se a escolha tiver menos de 117 arquivos (o número da seção 8.2) ou se faltar um destes: `progression`, `sync-merge`, `onerm`, `finish-workout`, `recovery`, `workout-model`, `log-workout`, `history`, `supersetFlow`, `routines`, `units`, `measurements`, `plan-share`, `exercises` e `state-core`. Imprime `HexEngine: <n> arquivos de teste contra o script, <m> de fora` e, com `HEXENGINE_SKIPPED=1`, uma linha `fora: <arquivo> (<motivo>)` para cada um dos de fora.
- `test.setupFiles: ['./src/test-setup.js']`, o mesmo do `vite.config.js`, e nada mais dele.
- Um plugin `enforce: 'pre'`: quando um teste escolhido importa um módulo do script, o `resolveId` devolve `\0hexengine:<caminho>`, e o `load` devolve um módulo que pega o script de `\0hexengine-script` (`export default new Function(<texto do script> + '\nreturn HexEngine')()`, avaliado uma vez por arquivo de teste) e reexporta cada nome com `export const <nome> = m.<nome>`, mais o `default`. Nenhum módulo do `lib` exporta `let` ou `var`, então copiar o valor não perde nada.

**O teste de carga** (`engine-load.mjs`):
- Usa o `jsc` de `/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc`. Sem ele, sai com 1 e `o teste de carga precisa do jsc do macOS`.
- Monta no Node o histórico grande com `padHistory(buildDemoState(), total)`: os treinos do demo copiados para trás, uma semana por vez, com `id` novo, até `total` (padrão 1.040, cinco anos de quatro treinos por semana).
- Roda `jsc --useJIT=false` (o iPhone roda o JavaScriptCore sem JIT) num script de medição que carrega o `hexengine.js` com `load()`, mede com `preciseTime()` e imprime um JSON com:
  - `evaluate`: avaliar o script;
  - `restore`: o `HexEngine.restore` do documento;
  - `tick`: a mediana de 20 séries marcadas, cada uma como o `update()` do app web faz: `draftOf(S)`, uma série a mais feita em `active`, `done()`, `stampChange(prev, next, now)` e `stateJson(next)`. A sessão começa como o `beginWorkout` (`sheets.jsx:3120-3135`): as `entries` de `buildCombinedEntries(S, [rotina.id])` (`session-merge.js:22`) e os mesmos campos de `active`;
  - `fatigue`: o `fatigueOf(S.workouts, now)`, só para registro;
  - `structuredClone`: se a cópia de um objeto com `Date`, `Map`, `Set` e referência circular é igual ao original e não é o mesmo objeto.
- O `jsc` roda cinco vezes, um processo novo de cada vez. A tabela usa a mediana das cinco em cada tempo, e o `structuredClone` precisa dar certo nas cinco.
- Imprime uma tabela e sai com 1 quando `overBudget` acha algo: `evaluate + restore` acima de 300 ms, `tick` acima de 30 ms, ou `structuredClone` falso. As metas são do tech lead, a partir da seção 8.13 (o app abre em menos de 1 s e a série aparece em menos de 100 ms), com folga de três vezes para um iPhone mais lento que este Mac. O `slack` multiplica as duas metas: o script lê `HEXGYM_LOAD_SLACK` (padrão 1), e a CI usa 2, porque o runner é mais lento e mais instável que este Mac.

- [ ] **Step 1: Write the failing tests for `pickEngineTests`**

```js
const L = 'frontend/src/lib/', engine = new Set([L + 'onerm.js', L + 'history.js'])
test('a test that only reads engine modules is picked', () => {
  const text = "import { test } from 'vitest'\nimport fc from 'fast-check'\nimport { estimate1RM } from './onerm.js'\n" +
    "import rows from './fixtures/rows.json' with { type: 'json' }\nimport { readFileSync } from 'node:fs'"
  assert.deepEqual(pickEngineTests([{ path: L + 'onerm.test.js', text }], engine).picked, [L + 'onerm.test.js'])
})
test('every other test is left out with its reason', () => {
  const { picked, skipped } = pickEngineTests([
    { path: L + 'a.test.js', text: "import { x } from './onerm.js'\nimport React from 'react'" },
    { path: L + 'b.test.js', text: "import { vi } from 'vitest'\nimport { x } from './onerm.js'\nvi.mock('./history.js')" },
    { path: L + 'c.test.js', text: "export { t } from './i18n.js'\nimport { x } from './onerm.js'" },
    { path: L + 'd.test.js', text: "import { test } from 'vitest'" },
    { path: L + 'e.test.js', text: "import { x } from './history.js'\nconst m = await import('../store/useStore.js')" },
  ], engine)
  assert.deepEqual(picked, [])
  assert.deepEqual(skipped.map(s => [s.path.slice(L.length), s.reason]), [
    ['a.test.js', 'importa react'], ['b.test.js', 'chama vi.mock'], ['c.test.js', 'importa frontend/src/lib/i18n.js'],
    ['d.test.js', 'não importa nenhum módulo do motor'], ['e.test.js', 'importa frontend/src/store/useStore.js']])
})
```

- [ ] **Step 2: Run them to verify they fail**

Run: `node --test scripts/hexgym/engine-tests.test.mjs`
Expected: FAIL, `Cannot find module` para `./engine-tests.mjs`.

- [ ] **Step 3: Implement `engine-tests.mjs` and write the config**

Run: o comando do passo 2
Expected: PASS, 2 testes.

- [ ] **Step 4: Run the lib tests against the script**

Run: `cd frontend && HEXENGINE_SKIPPED=1 npx vitest run --config vitest.hexengine.config.js`
Expected: `HexEngine: <n> arquivos de teste contra o script, <m> de fora`, com n de 117 para cima, a lista dos de fora com o motivo (ela vai no PR) e PASS. Teste que falha só pelo redirecionamento entra em `EXCLUDED`, com o motivo. Teste que falha por outro motivo é uma diferença real entre o script e o código: a Task para com BLOCKED e os detalhes, sem excluir nada.

- [ ] **Step 5: Prove the tests read the script**

Trocar à mão, no script gerado, o `return` de `estimate1RM` por `return 0` e rodar o comando do passo 4.
Expected: FAIL em `onerm.test.js`. Depois, `node scripts/build-hexgym-engine.mjs` e o passo 4 de novo, com PASS.

- [ ] **Step 6: Write the failing tests for the load test**

```js
test('padHistory reaches the total with a new id for each copy', () => {
  const S = padHistory(buildDemoState(), 1040)
  assert.equal(S.workouts.length, 1040); assert.equal(new Set(S.workouts.map(w => w.id)).size, 1040)
})
test('overBudget names each limit that was passed', () => {
  assert.deepEqual(overBudget({ evaluate: 100, restore: 150, tick: 10, structuredClone: true }), [])
  assert.deepEqual(overBudget({ evaluate: 200, restore: 150, tick: 31, structuredClone: false }),
    ['evaluate + restore: 350 ms (meta 300)', 'tick: 31 ms (meta 30)', 'structuredClone diferente no JavaScriptCore'])
  assert.deepEqual(overBudget({ evaluate: 200, restore: 150, tick: 31, structuredClone: true }, 2), [])
})
```

- [ ] **Step 7: Run them to verify they fail**

Run: `node --test scripts/hexgym/engine-load.test.mjs`
Expected: FAIL, `Cannot find module` para `./engine-load.mjs`.

- [ ] **Step 8: Implement `engine-load.mjs`**

Importar o arquivo não roda nada; a medição só roda quando ele é o script principal.

- [ ] **Step 9: Run the load test**

Run: `node --test scripts/hexgym/engine-load.test.mjs && node scripts/hexgym/engine-load.mjs`
Expected: PASS nos dois testes e a tabela dentro das metas. A tabela vai no PR, em "Para o founder ver".

- [ ] **Step 10: Add the checks**

Em `PARTS.engine`, depois dos testes do script: `{ name: 'testes do lib contra o script', cmd: 'npx', args: ['vitest', 'run', '--config', 'vitest.hexengine.config.js'], cwd: 'frontend' }`. Parte nova `load`: `node scripts/hexgym/engine-load.mjs`. Atualizar a mensagem do teste "unknown part".

Run: `node scripts/hexgym/check.mjs scripts engine load`
Expected: `ok`.

- [ ] **Step 11: Commit**

```bash
git add frontend/vitest.hexengine.config.js scripts/hexgym/engine-tests.mjs scripts/hexgym/engine-tests.test.mjs scripts/hexgym/engine-load.mjs scripts/hexgym/engine-load.test.mjs scripts/hexgym/check.mjs scripts/hexgym/check.test.mjs
git commit -m "Os testes do lib contra o script do motor e o teste de carga no jsc sem JIT"
```

---

### Task 7: O pacote HexEngine

**Issue:** #19.

**Files:**
- Create: `apple/.gitignore`
- Create: `apple/Packages/HexEngine/Package.swift`
- Create: `apple/Packages/HexEngine/Sources/HexEngine/HexEngine.swift`, `apple/Packages/HexEngine/Sources/HexEngine/Resources/host.js`
- Create: `apple/Packages/HexEngine/Tests/HexEngineTests/HexEngineTests.swift`, `RecordedCasesTests.swift`
- Create (gerados): `apple/Packages/HexEngine/Tests/HexEngineTests/Cases/America_Sao_Paulo.json`, `Europe_Zurich.json`, `Pacific_Auckland.json`
- Create: `scripts/hexgym/xcode.mjs`, `scripts/hexgym/xcode.test.mjs`
- Create: `scripts/hexgym/engine-cases.mjs`, `scripts/hexgym/record-engine-cases.mjs`, `scripts/hexgym/record-engine-cases.test.mjs`
- Modify: `scripts/hexgym/check.mjs`, `scripts/hexgym/check.test.mjs` (a parte `engine` ganha o `--check` dos casos, e entra a parte `packages`)

**Interfaces:**
- Consumes: o script e `values.js` (Task 5).
- Produces:

```swift
public actor HexEngine {
  public init(language: String = Locale.preferredLanguages.first ?? "en")
  public func load() throws -> EngineInfo        // avalia o script na primeira vez; depois devolve o mesmo
  public func freshDocument() throws -> Data     // cria o documento dentro do motor e devolve para gravar
  public func restore(_ document: Data) throws   // troca o documento dentro do motor
  public func document() throws -> Data          // o documento de agora, para gravar
}
public struct EngineInfo: Equatable, Sendable { public let exercises: Int; public let openGymVersion: String }
public enum EngineError: Error, Equatable, Sendable { case scriptMissing, notLoaded, javaScript(String) }
```

  - Internos, para os testes com `@testable import`: `call(_ name: String, json arguments: Data) throws -> Data` e `evaluate(_ script: String) throws -> String`.
  - `scripts/hexgym/xcode.mjs`: `developerDir({ env = process.env, exists = fs.existsSync, selected = () => execFileSync('xcode-select', ['-p'], { encoding: 'utf8' }) } = {}) → string`. A ordem: `DEVELOPER_DIR`, depois `/Applications/Xcode.app`, depois `/Applications/Xcode-beta.app`, depois o que o `xcode-select -p` aponta quando não é a Command Line Tools (o runner `xcode-27` tem nomes com número, como `/Applications/Xcode_27.2.app`). Rodado sozinho, imprime o resultado: `DEVELOPER_DIR=$(node scripts/hexgym/xcode.mjs)` é como os comandos desta fase escolhem o Xcode.
  - `scripts/hexgym/engine-cases.mjs`: `TIME_ZONES = ['America/Sao_Paulo', 'Europe/Zurich', 'Pacific/Auckland']` e `buildCases(load) → Promise<[{ name, fn, args, ignore? }]>`, em que `load(caminho)` importa um módulo de `frontend/src/lib`.
  - `scripts/hexgym/record-engine-cases.mjs`: `recordZone(zone) → Promise<string>` (o texto do arquivo daquele fuso) e a CLI `[--check]`.
  - A parte `packages` do `check.mjs`, começada aqui; a Task 8 põe o HexStore depois.

**Como o pacote funciona:**
- `load()` cria o `JSContext`, avalia o `host.js` e depois o `hexengine.js` (os dois do `Bundle.module`, com `withSourceURL`), chama `setDeviceLanguage(language)` e lê o `info()`. Sem o script, `.scriptMissing`. Antes do `load()`, toda chamada lança `.notLoaded`.
- O `host.js` traz os complementos do Swift (seção 8.2): `console`, com cada método indo para o `Logger(subsystem: "app.hexgym", category: "motor")` no nível certo, e `setTimeout`/`clearTimeout`, com cada timer guardado num `Map` do JS e disparado por um `Task.sleep` do Swift que volta ao ator. Os blocos Swift que o `host.js` chama capturam o ator com `[weak self]`, para o contexto não prender o motor.
- Swift e JS trocam texto JSON, nunca `JSValue` de objeto. Depois de cada chamada, se `context.exception` não for nulo, ele vira `.javaScript("<mensagem>\n<stack>")` e é limpo, e o contexto segue usável. Exceção dentro de um timer vai para o log como erro.
- `Package.swift`: `swift-tools-version: 6.2`; `platforms: [.iOS(.v26), .macOS(.v26)]`, sem watchOS, porque o Watch não roda JavaScript; produto `HexEngine`; recursos `.copy("Resources/hexengine.js")` e `.copy("Resources/host.js")`; alvo de teste `HexEngineTests` com `.copy("Cases")`. A pasta `JS/` da Task 5 fica fora dos alvos.
- `apple/.gitignore`: `xcuserdata/`, `DerivedData/`, `build/`, `.build/` e `.swiftpm/`.

**Os casos gravados.** O Node grava o que o código do openGym responde, num arquivo por fuso, e o Swift confere que o JavaScriptCore, rodando o script, responde o mesmo (seção 8.2 e Foco da revisão 5).
- `record-engine-cases.mjs` roda um processo filho por fuso de `TIME_ZONES`, com `TZ`. O filho chama `buildCases`, roda cada caso nos módulos de `frontend/src/lib` (como o servidor MCP faz) e devolve `{ name, fn, args, result }`: `args` com `encodeValue` antes da chamada e `result` com `encodeValue({ returned, args })` depois, sem os caminhos de `ignore`. O pai grava `apple/Packages/HexEngine/Tests/HexEngineTests/Cases/<fuso, com _ no lugar de />.json`, com `{ "zone": …, "cases": […] }` e dois espaços de recuo. Com `--check`, compara e sai com 1 e `<arquivo> está desatualizado. Rode: node scripts/hexgym/record-engine-cases.mjs`.
- Só entra caso cuja resposta depende apenas dos argumentos e do fuso. Função que gera `id` entra com o `id` em `ignore`.
- As sessões de treino, no relógio de cada fuso: (1) de 24/10/2026 23:30 a 25/10/2026 00:40, cruzando a meia-noite; (2) 25/10/2026 das 01:30 às 03:30, a volta do horário de verão em Zurique; (3) 29/03/2026 das 01:30 às 03:30, a ida em Zurique; (4) 05/04/2026 das 01:30 às 03:30, a volta em Auckland; (5) 27/09/2026 das 01:30 às 03:30, a ida em Auckland. São Paulo não tem horário de verão. Cada `active` sai de uma rotina com dois exercícios do catálogo, montado como o `beginWorkout` monta (`sheets.jsx:3120-3135`): as `entries` de `buildCombinedEntries(S, [rotina.id])` (`session-merge.js:22`) e os campos das linhas 3125 a 3134, com as séries feitas.
- Os casos:

| Caso | Função | O que prende |
|---|---|---|
| documento novo | `state-core.js#freshState`, com `'pt-BR'` e com `'ar-EG'` | o primeiro uso igual ao do app web |
| cópia salva | `state-core.js#stateFromSaved`, com uma chave desconhecida e sem `lang` | o que a restauração guarda |
| dia | `format.js#isoOf` no começo e no fim de cada sessão | o dia de cada instante no fuso |
| semana | `format.js#weekKey` do dia de cada começo, com `0` e com `1` | a semana que começa no domingo e na segunda |
| tempo atrás | `format.js#fmtAgo(começo, fim)` de cada sessão | o texto relativo, em inglês |
| treino terminado | `finish-workout.js#buildCompletedWorkout(active, { end })` de cada sessão, com `returned.id` em `ignore` | as séries e os recordes, iguais no V8 e no JavaScriptCore |
| dia do treino | `history.js#workoutDay` de cada sessão sem `d`, só com `start` | o dia local de um começo perto da meia-noite ou da troca de horário |
| meio-dia do treino | `history.js#workoutAt` de um treino só com `d`, em cada data das sessões | o meio-dia local, que muda com o fuso e com o horário de verão |
| fadiga | `recovery.js#fatigueOf(treinos, agora)`, com os cinco treinos só com `d` (sem `start`) e `agora` 36 h depois do último | o decaimento contado do meio-dia local, através da troca de horário |
| carimbo | `sync-merge.js#stampChange(prev, next, wall)`, com uma série mudada | o horário de cada campo |
| mesclagem | `sync-merge.js#mergeStates(a, b)`, com duas cópias que mudaram campos diferentes | a junção das duas |
| 1RM | `onerm.js#estimate1RM`, com `[100, 5]`, `[60, 12]` e `[140, 1]`, e `[80, 8]` em cada fórmula de `FORMULAS` | as contas puras |

**O `RecordedCasesTests.swift`:**
- É um `@Suite struct RecordedCasesTests`, o nome que o `--filter` usa.
- Roda só com `HEXGYM_CASES` no ambiente (o `check.mjs` põe junto com o `TZ`), para um `swift test` comum não depender do fuso da máquina: `@Test(.enabled(if: ProcessInfo.processInfo.environment["HEXGYM_CASES"] != nil))`.
- Primeiro, confere que `evaluate("Intl.DateTimeFormat().resolvedOptions().timeZone")` é o fuso de `HEXGYM_CASES`: a prova de que o `TZ` chegou ao JavaScriptCore.
- Depois, para cada caso do arquivo daquele fuso, `call(fn, json: args)`, tira os caminhos de `ignore` e compara com `result`: a mesma estrutura, os mesmos textos e booleanos, e números iguais, com tolerância relativa de `1e-9` para os que não são inteiros (o `Math.exp` e o `Math.pow` podem diferir no último bit entre o V8 e o JavaScriptCore). A falha diz o nome do caso.

- [ ] **Step 1: Write the failing tests for `developerDir`**

```js
test('DEVELOPER_DIR wins', () => assert.equal(developerDir({ env: { DEVELOPER_DIR: '/x' }, exists: () => true }), '/x'))
test('Xcode.app comes before the beta', () =>
  assert.equal(developerDir({ env: {}, exists: () => true }), '/Applications/Xcode.app/Contents/Developer'))
test('the beta when it is the only one', () =>
  assert.equal(developerDir({ env: {}, exists: p => p.includes('Xcode-beta') }), '/Applications/Xcode-beta.app/Contents/Developer'))
test('xcode-select when it points to a full Xcode', () => assert.equal(
  developerDir({ env: {}, exists: () => false, selected: () => '/Applications/Xcode_27.2.app/Contents/Developer\n' }), '/Applications/Xcode_27.2.app/Contents/Developer'))
test('no Xcode says what to do', () => assert.throws(
  () => developerDir({ env: {}, exists: () => false, selected: () => '/Library/Developer/CommandLineTools\n' }), /nenhum Xcode encontrado: instale o Xcode 27\.2 ou defina DEVELOPER_DIR/))
```

- [ ] **Step 2: Run them to verify they fail**

Run: `node --test scripts/hexgym/xcode.test.mjs`
Expected: FAIL, `Cannot find module` para `./xcode.mjs`.

- [ ] **Step 3: Implement `xcode.mjs` and run the tests**

Run: o comando do passo 2
Expected: PASS, 5 testes.

- [ ] **Step 4: Write `Package.swift` and the failing Swift tests**

Em `HexEngineTests.swift`, `object(_:)` lê um `Data` como `[String: Any]`, `loaded(_ language: String = "en")` devolve um `HexEngine(language:)` já carregado, e `openGymVersion()` lê a versão de `frontend/package.json` a partir do `#filePath`:

```swift
@Test func loadsTheCatalogueAndTheOpenGymVersion() async throws {
  let info = try await HexEngine().load()
  #expect(info.exercises > 5000); #expect(info.openGymVersion == openGymVersion())
}
@Test func callsBeforeLoadFail() async {
  await #expect(throws: EngineError.notLoaded) { try await HexEngine().document() }
}
@Test func loadingTwiceKeepsTheSameContext() async throws {
  let e = try await loaded(); _ = try await e.evaluate("globalThis.marca = 7"); _ = try await e.load()
  #expect(try await e.evaluate("String(globalThis.marca)") == "7")
}
@Test func freshDocumentIsTheWebAppFirstRun() async throws {
  let d = try object(await loaded("pt-BR").freshDocument())
  #expect(d["lang"] as? String == "en"); #expect(d["langAuto"] as? Bool == true); #expect(d["gifSize"] as? String == "mini")
  #expect(try object(await loaded("ar-EG").freshDocument())["lang"] as? String == "ar")
}
@Test func restoreKeepsKeysTheAppDoesNotKnow() async throws {                      // Foco da revisão 2
  let e = try await loaded()
  try await e.restore(Data(#"{"chaveDoFuturo":{"x":[1,2]},"unit":"lb"}"#.utf8))
  let d = try object(await e.document())
  #expect(d["chaveDoFuturo"] as? NSDictionary == ["x": [1, 2]] as NSDictionary); #expect(d["unit"] as? String == "lb")
}
@Test func aHalfEmojiSurvivesTheEngine() async throws {                           // Foco da revisão 2
  let e = try await loaded()
  try await e.restore(Data(#"{"dayNotes":{"2026-10-31":{"text":"\ud83d"}}}"#.utf8))
  #expect(String(decoding: try await e.document(), as: UTF8.self).contains(#""text":"\ud83d""#))
}
@Test func eachDocumentBringsItsOwnCustomExercises() async throws {
  let e = try await loaded(), find = Data(#"["c1"]"#.utf8)
  func found() async throws -> [String: Any]? { try object(await e.call("frontend/src/lib/exercises.js#exerciseOf", json: find))["returned"] as? [String: Any] }
  try await e.restore(Data(#"{"customEx":[{"id":"c1","n":"Remada do HexGym","bp":"back"}]}"#.utf8))
  #expect(try await found()?["n"] as? String == "Remada do HexGym")
  try await e.restore(Data("{}".utf8))
  #expect(try await found()?["$undefined"] as? Bool == true)
}
@Test func anErrorInTheEngineIsThrownAndTheEngineKeepsWorking() async throws {     // Foco da revisão 3
  let e = try await loaded()
  for bad in ["[1]", "{", ""] {
    let error = await #expect(throws: EngineError.self) { try await e.restore(Data(bad.utf8)) }
    #expect(error.map { if case .javaScript(let m) = $0 { !m.isEmpty } else { false } } == true)
  }
  let missing = await #expect(throws: EngineError.self) { _ = try await e.call("frontend/src/lib/nope.js#x", json: Data("[]".utf8)) }
  #expect("\(String(describing: missing))".contains("nope.js#x"))
  try await e.restore(Data("{}".utf8)); #expect(try object(await e.document())["workouts"] != nil)
}
@Test func timersFireOnceAndCanBeCancelled() async throws {
  let e = try await loaded()
  _ = try await e.evaluate("globalThis.hits = 0; setTimeout(() => hits++, 20); clearTimeout(setTimeout(() => hits += 10, 20)); setTimeout(() => { throw new Error('timer') }, 5); 0")
  try await Task.sleep(for: .milliseconds(300))
  #expect(try await e.evaluate("String(hits)") == "1")
}
@Test func consoleAndStructuredCloneWork() async throws {
  #expect(try await loaded().evaluate("console.log('oi'); console.error(new Error('x')); JSON.stringify(structuredClone({ a: [1, { b: 2 }], d: new Date(0) }))")
          == #"{"a":[1,{"b":2}],"d":"1970-01-01T00:00:00.000Z"}"#)
}
@Test func webGlobalsTheEngineDoesNotHaveYet() async throws {
  // URL: cleanUrl, em media-refs.js. fetch: import-hevy.js. TextEncoder, TextDecoder e Blob: zip.js. Cada um tem issue na fase 5.
  #expect(try await loaded().evaluate("[typeof URL, typeof fetch, typeof TextEncoder, typeof TextDecoder, typeof Blob].join()")
          == "undefined,undefined,undefined,undefined,undefined")
}
```

- [ ] **Step 5: Run them to verify they fail**

Run: `DEVELOPER_DIR=$(node scripts/hexgym/xcode.mjs) swift test --package-path apple/Packages/HexEngine`
Expected: FAIL, o alvo `HexEngine` não compila porque ainda não tem código.

- [ ] **Step 6: Implement `HexEngine.swift` and `host.js`**

- [ ] **Step 7: Run them to verify they pass**

Run: o comando do passo 5
Expected: PASS, 11 testes.

- [ ] **Step 8: Write the failing tests for the recorder**

```js
test('the same zone recorded twice gives the same text', async () => {
  assert.equal(await recordZone('Europe/Zurich'), await recordZone('Europe/Zurich'))
})
test('each zone records its own instants', async () => {
  const start = async zone => JSON.parse(await recordZone(zone)).cases.find(c => c.fn === 'frontend/src/lib/format.js#isoOf').args[0].$date
  assert.notEqual(await start('Pacific/Auckland'), await start('Europe/Zurich'))
})
```

- [ ] **Step 9: Run them to verify they fail**

Run: `node --test scripts/hexgym/record-engine-cases.test.mjs`
Expected: FAIL, `Cannot find module` para `./record-engine-cases.mjs`.

- [ ] **Step 10: Implement the cases and the recorder, and record**

Run: `node --test scripts/hexgym/record-engine-cases.test.mjs && node scripts/hexgym/record-engine-cases.mjs`
Expected: PASS, 2 testes, e os três arquivos em `Cases/`.

- [ ] **Step 11: Write `RecordedCasesTests.swift`**

- [ ] **Step 12: Replay the cases in each zone**

Run: `for z in America/Sao_Paulo Europe/Zurich Pacific/Auckland; do TZ=$z HEXGYM_CASES=$z DEVELOPER_DIR=$(node scripts/hexgym/xcode.mjs) swift test --package-path apple/Packages/HexEngine --filter RecordedCasesTests || exit 1; done`
Expected: PASS nos três. Um caso diferente é uma diferença real entre o JavaScriptCore e o V8: a Task para com BLOCKED e o caso, sem tirar o caso.

- [ ] **Step 13: Prove the zone check works**

Run: `TZ=America/Sao_Paulo HEXGYM_CASES=Europe/Zurich DEVELOPER_DIR=$(node scripts/hexgym/xcode.mjs) swift test --package-path apple/Packages/HexEngine --filter RecordedCasesTests`
Expected: FAIL na conferência do fuso.

- [ ] **Step 14: Add the checks**

Em `PARTS.engine`: `{ name: 'casos gravados em dia', cmd: 'node', args: ['scripts/hexgym/record-engine-cases.mjs', '--check'] }`. `PARTS.packages`: `swift test --package-path apple/Packages/HexEngine` com `TZ` e `HEXGYM_CASES` no primeiro fuso de `TIME_ZONES`, e uma rodada com `--filter RecordedCasesTests` para cada outro fuso. O `env` de cada uma é uma função que devolve `{ DEVELOPER_DIR: developerDir(), TZ, HEXGYM_CASES }`. Atualizar a mensagem do teste "unknown part".

Run: `node scripts/hexgym/check.mjs scripts engine packages`
Expected: `ok`.

- [ ] **Step 15: Commit**

```bash
git add apple/.gitignore apple/Packages/HexEngine/Package.swift apple/Packages/HexEngine/Sources apple/Packages/HexEngine/Tests scripts/hexgym
git commit -m "HexEngine: o motor num JSContext dentro de um ator, com os casos gravados no Node"
```

---

### Task 8: O pacote HexStore

**Issue:** #20.

**Files:**
- Create: `apple/Packages/HexStore/Package.swift`
- Create: `apple/Packages/HexStore/Sources/HexStore/DocumentStore.swift`
- Create: `apple/Packages/HexStore/Tests/HexStoreTests/DocumentStoreTests.swift`
- Modify: `scripts/hexgym/check.mjs` (a parte `packages` ganha o HexStore)

**Interfaces:**
- Consumes: `developerDir()` de `scripts/hexgym/xcode.mjs` (Task 7) na checagem.
- Produces:

```swift
public actor DocumentStore {
  public init(directory: URL)
  public static func appGroupDirectory(_ identifier: String = "group.app.hexgym",
                                       lookup: (String) -> URL? = { FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: $0) }) throws -> URL
  public func load() throws -> StoredDocument
  public func save(_ document: Data) throws
  public func syncBase() throws -> SyncBase?
  public func saveSyncBase(_ base: SyncBase) throws
}
public enum StoredDocument: Equatable, Sendable { case empty, current(Data), recovered(Data) }
public struct SyncBase: Codable, Equatable, Sendable { public var rev: Int; public var ts: Int?; public var wid: String? }
public enum DocumentStoreError: Error, Equatable { case appGroupUnavailable(String), unreadable, notAnObject }
```

Os arquivos, todos no `directory`: `state.json` (o documento), `state.previous.json` (a cópia anterior), `state.unreadable.json` (o último arquivo ruim, guardado para alguém olhar) e `sync-base.json`. `Package.swift`: `swift-tools-version: 6.2`, `platforms: [.iOS(.v26), .macOS(.v26), .watchOS(.v26)]`, produto `HexStore`, alvo de teste `HexStoreTests`.

- [ ] **Step 1: Write the failing tests**

Swift Testing, cada teste num diretório temporário novo:

```swift
@Test func emptyDirectoryHasNoDocument() async throws { #expect(try await store.load() == .empty) }
@Test func saveThenLoadGivesTheSameBytes() async throws { try await store.save(a); #expect(try await store.load() == .current(a)) }
@Test func secondSaveKeepsThePreviousCopy() async throws {
  try await store.save(a); try await store.save(b)
  #expect(read("state.json") == b); #expect(read("state.previous.json") == a)
}
@Test func truncatedDocumentRecoversFromThePreviousCopy() async throws {   // Foco da revisão 1
  try await store.save(a); try await store.save(b); write("state.json", b.prefix(10))
  #expect(try await store.load() == .recovered(a))
  #expect(read("state.unreadable.json") == b.prefix(10))
}
@Test func bothCopiesBrokenThrowsAndTouchesNothing() async throws {      // Foco da revisão 1
  write("state.json", Data("{".utf8)); write("state.previous.json", Data("x".utf8))
  await #expect(throws: DocumentStoreError.unreadable) { try await store.load() }
  #expect(read("state.json") == Data("{".utf8)); #expect(read("state.previous.json") == Data("x".utf8))
}
@Test func brokenDocumentWithoutAPreviousCopyThrows() async throws {     // Foco da revisão 1
  write("state.json", Data("{".utf8))
  await #expect(throws: DocumentStoreError.unreadable) { try await store.load() }
  #expect(read("state.json") == Data("{".utf8))
}
@Test func missingDocumentWithAPreviousCopyRecovers() async throws {     // Foco da revisão 1
  write("state.previous.json", a)
  #expect(try await store.load() == .recovered(a))
}
@Test func savingOverABrokenDocumentKeepsTheGoodPreviousCopy() async throws {   // Foco da revisão 1
  try await store.save(a); try await store.save(b); write("state.json", Data("{".utf8))
  try await store.save(c)
  #expect(read("state.json") == c); #expect(read("state.previous.json") == a)
}
@Test func onlyJSONObjectsAreSaved() async throws {
  await #expect(throws: DocumentStoreError.notAnObject) { try await store.save(Data("[1]".utf8)) }
  #expect(try await store.load() == .empty)
}
@Test func unknownKeysSurvive() async throws {                            // Foco da revisão 2
  let doc = Data(#"{"settings":{},"chaveDoFuturo":{"x":[1,2]}}"#.utf8)
  try await store.save(doc); #expect(try await store.load() == .current(doc))
}
@Test func aHalfEmojiIsSavedAndReadAsIs() async throws {                    // Foco da revisão 2
  let doc = Data(#"{"dayNotes":{"2026-10-31":{"text":"\ud83d"}},"x":"\ude00"}"#.utf8)
  try await store.save(doc); #expect(read("state.json") == doc); #expect(try await store.load() == .current(doc))
}
@Test func aDocumentThatCannotBeReadNowThrowsAndTouchesNothing() async throws {   // Foco da revisão 1
  try await store.save(a); try await store.save(b); lock("state.json")
  await #expect(throws: DocumentStoreError.unreadable) { try await store.load() }
  await #expect(throws: DocumentStoreError.unreadable) { try await store.save(c) }
  unlock("state.json"); #expect(read("state.json") == b); #expect(read("state.previous.json") == a)
  #expect(!exists("state.unreadable.json"))
}
@Test func syncBaseRoundTrips() async throws {
  try await store.saveSyncBase(SyncBase(rev: 7, ts: 1_730_000_000_000, wid: "w1"))
  #expect(try await store.syncBase() == SyncBase(rev: 7, ts: 1_730_000_000_000, wid: "w1"))
}
@Test func missingAppGroupThrows() {
  #expect(throws: DocumentStoreError.appGroupUnavailable("group.app.hexgym")) {
    try DocumentStore.appGroupDirectory(lookup: { _ in nil })
  }
}
```

`a`, `b` e `c` são três documentos JSON pequenos e diferentes; `read` e `write` leem e gravam direto no diretório temporário, `lock` e `unlock` põem as permissões do arquivo em `0o000` e em `0o644`, e `exists` diz se o arquivo está lá.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `DEVELOPER_DIR=$(node scripts/hexgym/xcode.mjs) swift test --package-path apple/Packages/HexStore`
Expected: FAIL, `cannot find 'DocumentStore' in scope`.

- [ ] **Step 3: Implement `DocumentStore`**

O documento é opaco: o pacote só confere que é um objeto JSON e guarda os bytes como vieram.
- "Válido" quer dizer que o `JSON.parse` leria o arquivo como um objeto: o `JSONSerialization` aceita o arquivo, ou aceita uma cópia em que cada escape de surrogate sem par (um `\ud800` a `\udbff` sem um `\udc00` a `\udfff` logo depois, ou um destes sem aquele antes) virou `�`. O `JSONSerialization` recusa os dois tipos de surrogate sozinho, e o `JSON.stringify` grava os dois (conferido nesta máquina em 31/10/2026). A troca serve só para conferir: os bytes gravados e devolvidos são sempre os originais.
- "Falta" quer dizer só o erro `NSFileReadNoSuchFileError`. Qualquer outro erro de leitura (permissão, disco, um aparelho que ligou e ainda não foi desbloqueado) lança `.unreadable` sem mexer em nada, no `load` e no `save`.
- `save` confere o documento novo (um inválido lança `.notAnObject`), depois copia o `state.json` atual para `state.previous.json`, e só se ele for válido, e por fim grava o novo `state.json`. As duas gravações usam `Data.write(to:options: .atomic)`.

`load`, nesta ordem:

| `state.json` | `state.previous.json` | O que faz |
|---|---|---|
| válido | não é lido | `.current(state.json)` |
| falta, ou existe e é ruim | válido | move o `state.json` ruim, se existir, para `state.unreadable.json` e devolve `.recovered(previous)` |
| falta | falta | `.empty` |
| os outros casos, inclusive um erro de leitura em qualquer dos dois | | lança `.unreadable` sem mexer em nada |

A recuperação e o erro vão para o `Logger(subsystem: "app.hexgym", category: "dados")`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: o comando do passo 2
Expected: PASS, 14 testes.

- [ ] **Step 5: Add HexStore to the `packages` check**

Em `PARTS.packages`, depois do HexEngine: `{ name: 'HexStore', cmd: 'swift', args: ['test', '--package-path', 'apple/Packages/HexStore'], env: () => ({ DEVELOPER_DIR: developerDir() }) }`.

Run: `node scripts/hexgym/check.mjs packages`
Expected: `ok`.

- [ ] **Step 6: Commit**

```bash
git add apple/Packages/HexStore scripts/hexgym/check.mjs
git commit -m "HexStore: o documento de dados no App Group, com cópia anterior"
```

---

### Task 9: O projeto Xcode com os quatro alvos

**Issue:** #21.

**Files:**
- Create: `apple/HexGym.xcodeproj/project.pbxproj`
- Create: `apple/HexGym.xcodeproj/xcshareddata/xcschemes/HexGym.xcscheme`, `HexGymWatch.xcscheme`
- Create: `apple/Shared/Wordmark.swift`
- Create: `apple/HexGym/HexGymApp.swift`, `apple/HexGym/ContentView.swift`, `apple/HexGym/Assets.xcassets`
- Create: `apple/HexGymWidgets/HexGymWidgets.swift`
- Create: `apple/HexGymWatch/HexGymWatchApp.swift`, `apple/HexGymWatch/Assets.xcassets`
- Create: `apple/HexGymWatchWidgets/HexGymWatchWidgets.swift`
- Create: `apple/HexGymTests/SmokeTests.swift`
- Create: `apple/Config/HexGym-Info.plist`, `HexGymWidgets-Info.plist`, `HexGymWatchWidgets-Info.plist`
- Create: `apple/Config/HexGym.entitlements`, `HexGymWidgets.entitlements`, `HexGymWatch.entitlements`, `HexGymWatchWidgets.entitlements`
- Create: `scripts/hexgym/placeholder-icon.swift`
- Create: `scripts/hexgym/project-format.test.mjs`
- Create: `docs/hexgym/prints/<issue>/` (os prints do PR)
- Modify: `scripts/hexgym/check.mjs`, `scripts/hexgym/check.test.mjs` (parte `app`)

**Interfaces:**
- Consumes: os produtos `HexEngine` (Task 7) e `HexStore` (Task 8), ligados só ao alvo `HexGym`. O `HexGymTests`, hospedado no app, importa os dois pelo app: duas cópias estáticas no mesmo processo fariam dois tipos `HexEngine`.
- Produces: os esquemas `HexGym` (compila o app com o Watch e os widgets embutidos e roda o `HexGymTests`) e `HexGymWatch`; a view `Wordmark()`; a parte `app` do `check.mjs`.

As decisões do projeto, que o arquivo precisa seguir:

- **Formato:** `objectVersion = 77`, `preferredProjectObjectVersion = 77`, `LastUpgradeCheck = 2700`, `developmentRegion = en`, `knownRegions = (en, Base, "pt-BR")`.
- **Pastas sincronizadas** (`PBXFileSystemSynchronizedRootGroup`): `HexGym`, `HexGymWidgets`, `HexGymWatch`, `HexGymWatchWidgets` e `HexGymTests`, cada uma no seu alvo; `Shared` entra nos quatro alvos do app. `Config/` não é sincronizada: os Info.plist e os entitlements são citados só pelos ajustes `INFOPLIST_FILE` e `CODE_SIGN_ENTITLEMENTS`.
- **Pacotes:** `XCLocalSwiftPackageReference` com `relativePath = Packages/HexEngine` e `Packages/HexStore`.
- **Alvos:**

| Alvo | Tipo | Bundle ID | Plataforma | Embutido em |
|---|---|---|---|---|
| `HexGym` | `com.apple.product-type.application` | `app.hexgym` | iphoneos | |
| `HexGymWidgets` | `com.apple.product-type.app-extension` | `app.hexgym.widgets` | iphoneos | `HexGym`, fase "Embed Foundation Extensions" (`dstSubfolderSpec = 13`) |
| `HexGymWatch` | `com.apple.product-type.application` | `app.hexgym.watchkitapp` | watchos, `TARGETED_DEVICE_FAMILY = 4` | `HexGym`, fase "Embed Watch Content" (`dstSubfolderSpec = 16`, `dstPath = "$(CONTENTS_FOLDER_PATH)/Watch"`) |
| `HexGymWatchWidgets` | `com.apple.product-type.app-extension` | `app.hexgym.watchkitapp.widgets` | watchos | `HexGymWatch`, "Embed Foundation Extensions" (`13`) |
| `HexGymTests` | `com.apple.product-type.bundle.unit-test` | `app.hexgym.tests` | iphoneos | hospedado no `HexGym` (`TEST_HOST`, `BUNDLE_LOADER`) |

- **Ajustes comuns:** `DEVELOPMENT_TEAM = MPAGLMK4Q2`, `CODE_SIGN_STYLE = Automatic`, `SWIFT_VERSION = 6.0`, `MARKETING_VERSION = 0.1.0`, `CURRENT_PROJECT_VERSION = 1`, `GENERATE_INFOPLIST_FILE = YES`, `LOCALIZATION_PREFERS_STRING_CATALOGS = YES`. Nos embutidos, `SKIP_INSTALL = YES`. No app e no Watch, `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` e `ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon` (sem ele, o ícone fica fora do pacote e do Info.plist, e o App Store Connect recusa o envio). Nos alvos do iPhone, `IPHONEOS_DEPLOYMENT_TARGET = 26.0` e `TARGETED_DEVICE_FAMILY = 1`; nos do Watch, `WATCHOS_DEPLOYMENT_TARGET = 26.0` e `TARGETED_DEVICE_FAMILY = 4`.
- **Info do app:** `INFOPLIST_KEY_CFBundleDisplayName = HexGym`, `INFOPLIST_KEY_ITSAppUsesNonExemptEncryption = NO`, `INFOPLIST_KEY_UIUserInterfaceStyle = Dark` (só escuro no primeiro TestFlight, seção 11), `INFOPLIST_KEY_UILaunchScreen_Generation = YES`. `Config/HexGym-Info.plist` só traz o `CFBundleURLTypes` com o esquema `hexgym`.
- **Info do Watch:** `INFOPLIST_KEY_WKCompanionAppBundleIdentifier = app.hexgym`, `INFOPLIST_KEY_WKRunsIndependentlyOfCompanionApp = NO` (a fase 4 revê). O `WKApplication` o Xcode põe sozinho.
- **Info dos widgets:** os dois Info.plist de `Config/` só trazem `NSExtension` → `NSExtensionPointIdentifier = com.apple.widgetkit-extension`.
- **Entitlements:** os quatro só com `com.apple.security.application-groups = [group.app.hexgym]`.
- **Ícone provisório:** `scripts/hexgym/placeholder-icon.swift` desenha, com `ImageRenderer` do SwiftUI, um PNG de 1024 × 1024 sem canal alfa (o App Store Connect recusa ícone com transparência): a imagem do `ImageRenderer` é redesenhada num `CGContext` sem alfa (`CGImageAlphaInfo.noneSkipLast`) antes de virar PNG. Fundo preto e `HEX` branco, peso heavy, largura condensada, centralizado. Vai como ícone de tamanho único no `AppIcon` do app e do Watch. O ícone de verdade é decisão do founder, na fase 1.
- **As telas provisórias:** `Wordmark()` é `HEX` em peso heavy e largura condensada seguido de `gym` em peso thin, branco, com `accessibilityLabel("HexGym")`. O app e o Watch mostram o `Wordmark` centralizado em fundo preto. Cada pacote de widgets tem um widget, `kind` `HexGymWordmark`: no iPhone, `.systemSmall`; no Watch, `.accessoryRectangular`; os dois com `containerBackground(.black, for: .widget)`.

- [ ] **Step 1: Write the failing format test**

Em `scripts/hexgym/project-format.test.mjs`, lendo `apple/HexGym.xcodeproj/project.pbxproj` e os quatro entitlements:

```js
test('the project stays in the Xcode 16.0 format', () => {
  assert.match(pbx, /objectVersion = 77;/); assert.match(pbx, /preferredProjectObjectVersion = 77;/)
})
test('the four bundle IDs and the team are set', () => {
  for (const id of ['app.hexgym', 'app.hexgym.widgets', 'app.hexgym.watchkitapp', 'app.hexgym.watchkitapp.widgets'])
    assert.match(pbx, new RegExp(`PRODUCT_BUNDLE_IDENTIFIER = ${id.replaceAll('.', '\\.')};`))
  assert.match(pbx, /DEVELOPMENT_TEAM = MPAGLMK4Q2;/); assert.doesNotMatch(pbx, /DEVELOPMENT_TEAM = (?!MPAGLMK4Q2;)/)
})
test('the deployment targets are 26.0', () => {
  assert.match(pbx, /IPHONEOS_DEPLOYMENT_TARGET = 26\.0;/); assert.match(pbx, /WATCHOS_DEPLOYMENT_TARGET = 26\.0;/)
  assert.doesNotMatch(pbx, /(IPHONEOS|WATCHOS)_DEPLOYMENT_TARGET = (?!26\.0;)/)
})
test('the app icon and the device families are set', () => {
  assert.ok(pbx.match(/ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;/g)?.length >= 4)   // Debug e Release do app e do Watch
  assert.match(pbx, /TARGETED_DEVICE_FAMILY = 1;/); assert.match(pbx, /TARGETED_DEVICE_FAMILY = 4;/)
})
test('every target has the app group', () => {
  for (const f of entitlements) assert.match(f, /<string>group\.app\.hexgym<\/string>/)
})
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node --test scripts/hexgym/project-format.test.mjs`
Expected: FAIL, `ENOENT` no `project.pbxproj`.

- [ ] **Step 3: Write the project, the sources and the icon**

Seguindo as decisões acima. Os identificadores do pbxproj são 24 dígitos hexadecimais, únicos no arquivo. Rodar `swift scripts/hexgym/placeholder-icon.swift apple/HexGym/Assets.xcassets/AppIcon.appiconset/AppIcon.png` e copiar o PNG para o `AppIcon` do Watch.

Run: `sips -g hasAlpha apple/HexGym/Assets.xcassets/AppIcon.appiconset/AppIcon.png`
Expected: `hasAlpha: no`.

- [ ] **Step 4: Add the `app` part to `check.mjs`**

`PARTS.app`, com `env: () => ({ DEVELOPER_DIR: developerDir() })`:
1. `xcodebuild -project apple/HexGym.xcodeproj -scheme HexGym -destination "generic/platform=iOS Simulator" -derivedDataPath apple/DerivedData CODE_SIGNING_ALLOWED=NO build`
2. `xcodebuild -project apple/HexGym.xcodeproj -scheme HexGymWatch -destination "generic/platform=watchOS Simulator" -derivedDataPath apple/DerivedData CODE_SIGNING_ALLOWED=NO build`

Atualizar a mensagem esperada do teste "unknown part" com as partes que existem.

- [ ] **Step 5: Run the checks**

Run: `node scripts/hexgym/check.mjs scripts app`
Expected: os testes de formato passam e os dois builds terminam com `** BUILD SUCCEEDED **`.

- [ ] **Step 6: Verify the embedding and the Info.plist**

Run: `find apple/DerivedData/Build/Products/Debug-iphonesimulator/HexGym.app -maxdepth 3 \( -name '*.appex' -o -name '*.app' \)` e `plutil -extract WKCompanionAppBundleIdentifier raw apple/DerivedData/Build/Products/Debug-iphonesimulator/HexGym.app/Watch/HexGymWatch.app/Info.plist`
Expected: `PlugIns/HexGymWidgets.appex`, `Watch/HexGymWatch.app` e, dentro dele, `PlugIns/HexGymWatchWidgets.appex`; e `app.hexgym`.

- [ ] **Step 7: See it run**

O build da checagem é sem assinatura (`CODE_SIGNING_ALLOWED=NO`), e um app sem assinatura não leva os entitlements: para ver rodando, compilar assinado, para um simulador de iPhone com o sistema 26 ou mais novo (`xcrun simctl list devices available`), com a assinatura local que o Xcode faz para simulador: `xcodebuild -project apple/HexGym.xcodeproj -scheme HexGym -destination id=<udid> -derivedDataPath apple/DerivedData build`, e o mesmo com `-scheme HexGymWatch` para um simulador de Apple Watch. Instalar os dois com `xcrun simctl install`.

Run: `xcrun simctl get_app_container <udid> app.hexgym group.app.hexgym`
Expected: a pasta do App Group no simulador, a prova de que o entitlement chegou.

Depois, `xcrun simctl launch` nos dois e print das duas telas com `xcrun simctl io <udid> screenshot`. Os prints vão no PR, em "Para o founder ver", como dizem as Restrições globais.

- [ ] **Step 8: Commit**

```bash
git add apple/HexGym.xcodeproj apple/Shared apple/HexGym apple/HexGymWidgets apple/HexGymWatch apple/HexGymWatchWidgets apple/HexGymTests apple/Config scripts/hexgym docs/hexgym/prints
git commit -m "Projeto Xcode do HexGym com os quatro alvos e o ícone provisório"
```

---

### Task 10: O app abre com o motor e os dados

**Issue:** #22.

**Files:**
- Create: `apple/HexGym/AppModel.swift`
- Modify: `apple/HexGym/HexGymApp.swift`, `apple/HexGym/ContentView.swift`
- Create: `apple/HexGym/Localizable.xcstrings`
- Create: `apple/HexGymTests/AppModelTests.swift` (e remove o `SmokeTests.swift`)
- Create: `docs/hexgym/prints/<issue>/` (os prints do PR)
- Modify: `scripts/hexgym/xcode.mjs`, `scripts/hexgym/xcode.test.mjs`, `scripts/hexgym/check.mjs`

**Interfaces:**
- Consumes: `HexEngine` (Task 7): `init(language:)`, `load() -> EngineInfo`, `freshDocument() -> Data` e `restore(_:)`; `DocumentStore` (Task 8): `appGroupDirectory()`, `load() -> StoredDocument` e `save(_:)`.
- Produces:

```swift
@Observable @MainActor final class AppModel {
  enum State: Equatable { case starting, ready(Status), failed(String) }   // em failed, o detalhe, para o log e os testes
  struct Status: Equatable { var exercises: Int; var origin: Origin }
  enum Origin: Equatable { case created, opened, recovered }
  private(set) var state: State
  init(engine: HexEngine, store: DocumentStore?)   // nil: o App Group não abriu
  func start() async
  static func live() -> AppModel
}
```

- `scripts/hexgym/xcode.mjs` ganha `pickSimulator(simctlJSON, family = 'iPhone') → udid`: o primeiro aparelho disponível com o nome começando por `family`, no iOS mais novo que for 26 ou acima.

`start()`: sem `store`, vira `.failed` na hora, sem carregar o motor nem gravar nada. Com `store`: `engine.load()`; depois `store.load()`. Com `.empty`, `freshDocument()` e `save` do que ele devolveu, origem `.created`. Com `.current`, `restore`, origem `.opened`, e nada é gravado. Com `.recovered`, `restore` e depois `save` dos mesmos bytes recuperados, para o próximo início abrir normal, origem `.recovered`. O documento novo não leva horário: um carimbo de agora ganharia, numa sincronização futura, de um documento de verdade do servidor. Qualquer erro vira `.failed(<descrição do erro>)` e vai para o `Logger(subsystem: "app.hexgym", category: "app")`, e depois de um erro nada é gravado. `live()` tenta `DocumentStore(directory: DocumentStore.appGroupDirectory())` e, se falhar, passa `nil`: nunca inventa outra pasta, porque o documento iria para um lugar que o Watch e os widgets não veem, ou que o sistema limpa.

A tela mostra o `Wordmark` e, embaixo, uma linha por estado:

| Estado | pt-BR | en |
|---|---|---|
| `.starting` | Abrindo… | Opening… |
| `.ready`, sempre | Motor carregado · %lld exercícios | Engine loaded · %lld exercises |
| `.created` | Documento criado | Document created |
| `.opened` | Documento aberto | Document opened |
| `.recovered` | Documento recuperado da cópia anterior | Document restored from the previous copy |
| `.failed` | Não deu para abrir os seus dados. | Couldn't open your data. |

O detalhe do erro vai para o log, nunca para a tela.

- [ ] **Step 1: Write the failing tests**

Em `apple/HexGymTests/AppModelTests.swift`, dentro de `@Suite @MainActor struct AppModelTests` (o alvo de teste não tem o ator principal como padrão, e o `AppModel` é `@MainActor`), cada teste com um `DocumentStore` num diretório temporário, e `read` e `write` como na Task 8:

```swift
@Test func firstRunCreatesAndSavesADocument() async throws {
  let model = AppModel(engine: HexEngine(), store: store); await model.start()
  guard case .ready(let s) = model.state else { Issue.record("\(model.state)"); return }
  #expect(s.origin == .created); #expect(s.exercises > 5000)
  #expect(try JSONSerialization.jsonObject(with: read("state.json")) is [String: Any])
}
@Test func secondRunOpensWithoutWriting() async throws {
  await AppModel(engine: HexEngine(), store: store).start(); let before = read("state.json")
  let model = AppModel(engine: HexEngine(), store: store); await model.start()
  #expect(model.state.origin == .opened); #expect(read("state.json") == before)
}
@Test func bothCopiesBrokenFailsWithoutWriting() async throws {          // Foco da revisão 1
  write("state.json", Data("{".utf8)); write("state.previous.json", Data("x".utf8))
  let model = AppModel(engine: HexEngine(), store: store); await model.start()
  guard case .failed = model.state else { Issue.record("\(model.state)"); return }
  #expect(read("state.json") == Data("{".utf8))
}
@Test func recoveredDocumentIsRestoredAndSaved() async throws {          // Foco da revisão 1
  await AppModel(engine: HexEngine(), store: store).start(); let good = read("state.json")
  try await store.save(good)                                   // deixa a cópia anterior
  write("state.json", Data("{".utf8))
  let model = AppModel(engine: HexEngine(), store: store); await model.start()
  #expect(model.state.origin == .recovered); #expect(read("state.json") == good)
  #expect(read("state.unreadable.json") == Data("{".utf8))
}
@Test func missingAppGroupFailsWithoutWriting() async {
  let model = AppModel(engine: HexEngine(), store: nil); await model.start()
  guard case .failed = model.state else { Issue.record("\(model.state)"); return }
}
```

(`state.origin` é um atalho de teste, numa extensão dentro do `AppModelTests.swift`.)

- [ ] **Step 2: Write the failing test for `pickSimulator`**

Em `scripts/hexgym/xcode.test.mjs`, com um JSON no formato de `xcrun simctl list devices available --json` que tem um iPhone 17 no iOS 26.4, um iPhone 17 Pro no iOS 27.0 e um iPad no iOS 27.0: `pickSimulator(json)` devolve o udid do iPhone 17 Pro; sem nenhum iPhone 26 ou acima, lança `Error` com `nenhum simulador de iPhone com iOS 26 ou mais novo`.

- [ ] **Step 3: Run them to verify they fail**

Run: `node --test scripts/hexgym/xcode.test.mjs` e `DEVELOPER_DIR=$(node scripts/hexgym/xcode.mjs) xcodebuild -project apple/HexGym.xcodeproj -scheme HexGym -destination id=<udid> -derivedDataPath apple/DerivedData test`
Expected: FAIL, `pickSimulator is not a function` e `cannot find 'AppModel' in scope`.

- [ ] **Step 4: Implement `AppModel`, the screen, the strings and `pickSimulator`**

`HexGymApp` cria o `AppModel.live()` e chama `start()` num `.task` da janela. As chamadas ao motor e ao armazenamento ficam nos atores, fora da thread principal.

- [ ] **Step 5: Add the test run to the `app` part**

Terceira checagem de `PARTS.app`: `xcodebuild -project apple/HexGym.xcodeproj -scheme HexGym -destination id=<udid> -derivedDataPath apple/DerivedData test`, com `args` como função que acha o `udid` com `pickSimulator` na hora de rodar, sobre a saída de `xcrun simctl list devices available --json` no mesmo `DEVELOPER_DIR`.

- [ ] **Step 6: Run the checks**

Run: `node scripts/hexgym/check.mjs scripts app`
Expected: `ok`, com os cinco testes do `AppModelTests` passando.

- [ ] **Step 7: See it run**

Compilar assinado e instalar no simulador do iPhone, como no passo 7 da Task 9. Os testes hospedados já abriram o app, então antes do primeiro print apagar os `state*.json` da pasta que `xcrun simctl get_app_container <udid> app.hexgym group.app.hexgym` devolve. Abrir o app e tirar print com "Documento criado"; fechar, abrir de novo e tirar print com "Documento aberto". Os dois prints vão no PR, como dizem as Restrições globais.

- [ ] **Step 8: Commit**

```bash
git add apple/HexGym apple/HexGymTests scripts/hexgym docs/hexgym/prints
git commit -m "O app abre com o motor e o documento de dados"
```

---

### Task 11: A CI do HexGym

**Issue:** #9.

**Files:**
- Create: `.github/workflows/hexgym.yml`
- Modify: `.claude/agents/hexgym-revisor.md` (fica em `.claude/`, que o `.gitignore:18` ignora: `git add -f`)

**Interfaces:**
- Consumes: as partes `scripts`, `engine`, `load`, `packages` e `app` do `check.mjs` (Tasks 1, 5 a 10).
- Produces: o check `hexgym-ok`, que vira obrigatório em `main` e `develop` depois do merge.

O workflow, com os mesmos pins de ação do `test.yml` e do `ios.yml`:

- `name: HexGym`; `on`: `pull_request`, `push` em `[main, develop]` e `workflow_dispatch`; `permissions: contents: read`; `concurrency` com `group: hexgym-${{ github.ref }}` e `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`.
- Todo `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1` leva `persist-credentials: false`: nenhum job usa o token depois do checkout.
- `changes` (`ubuntu-latest`, com `permissions` `contents: read` e `pull-requests: read`, que o filtro usa para listar os arquivos do PR): checkout e `dorny/paths-filter@ceb8a2b8f2d89434be7ff52d3de7ec3738c5cc9d # v4.0.3` com `id: f`, `base: ${{ github.event_name == 'push' && github.ref_name || '' }}` e três filtros. Cada saída do job é `${{ steps.f.outputs.<filtro> == 'true' || github.event_name == 'workflow_dispatch' }}`, para o disparo à mão rodar tudo:
  - `scripts`: `scripts/hexgym/**`, `apple/HexGym.xcodeproj/**`, `apple/Config/**`, `frontend/src/lib/**`, `.github/workflows/hexgym.yml` (os testes dos scripts também leem o projeto, os entitlements e o `lib`)
  - `engine`: `frontend/src/lib/**`, `api/coach/core/**`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/vitest.hexengine.config.js`, `scripts/build-hexgym-engine.mjs`, `scripts/hexgym/**`, `apple/Packages/HexEngine/**`, `.github/workflows/hexgym.yml`
  - `apple`: `apple/**`, `scripts/hexgym/**`, `.github/workflows/hexgym.yml`
- `scripts` (`ubuntu-latest`, se `scripts`): checkout, `actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0` com Node 22, `node scripts/hexgym/check.mjs scripts`.
- `engine` (`ubuntu-latest`, se `engine`): checkout, setup-node com cache de npm em `frontend/package-lock.json`, `npm ci` em `frontend/`, `node scripts/hexgym/check.mjs engine`.
- `packages` (`runs-on: xcode-27`, se `engine` ou `apple`): checkout, setup-node, `node scripts/hexgym/check.mjs load packages`, com `HEXGYM_LOAD_SLACK: 2` no `env` (Task 6).
- `app` (`runs-on: xcode-27`, se `apple`): checkout, setup-node, `xcodebuild -showsdks | grep -q watchsimulator || xcodebuild -downloadPlatform watchOS`, `node scripts/hexgym/check.mjs app`.
- `hexgym-ok` (`ubuntu-latest`, `needs: [changes, scripts, engine, packages, app]`, `if: always()`): o mesmo passo do `tests-ok` do `test.yml`, que passa quando cada job deu `success` ou `skipped`.
- `timeout-minutes`: 5 no `changes`, `scripts` e `hexgym-ok`; 15 no `engine`; 30 no `packages`; 45 no `app`.

- [ ] **Step 1: Write the workflow**

Seguindo a lista acima.

- [ ] **Step 2: Stop the reviewer from running the checks by hand**

Tirar de `.claude/agents/hexgym-revisor.md` a frase "Enquanto o `hexgym-ok` não for obrigatório (até a Task 11), roda `node scripts/hexgym/check.mjs` nas partes que o PR toca, numa worktree do commit do PR.": daqui em diante, quem roda é a CI. A checagem local do orquestrador, no passo 2.6 da skill, continua.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/hexgym.yml
git add -f .claude/agents/hexgym-revisor.md
git commit -m "CI do HexGym num workflow próprio, com o resumo hexgym-ok"
```

- [ ] **Step 4: See it pass on this pull request**

O orquestrador faz este passo depois do push.

Run: `gh pr checks <pr> -R lipedesign/openGym`
Expected: `changes`, `scripts`, `engine`, `packages`, `app` e `hexgym-ok` com `pass` (o PR mexe em `.github/workflows/hexgym.yml`, então os filtros ligam tudo).

- [ ] **Step 5: After the merge, require `hexgym-ok`**

`gh api -X PATCH repos/lipedesign/openGym/branches/develop/protection/required_status_checks --input <arquivo>` com `{"strict": false, "checks": [{"context": "tests-ok", "app_id": 15368}, {"context": "hexgym-ok", "app_id": 15368}]}`, e o mesmo em `main` com `"strict": true`.

Run: `gh api repos/lipedesign/openGym/branches/develop/protection --jq '.required_status_checks.checks'` e o mesmo em `main`
Expected: os dois checks, nas duas branches.

- [ ] **Step 6: After the merge, see it block a broken test**

Numa branch `teste/hexgym-ok-vermelho`, a partir de `develop`, trocar uma asserção de `scripts/hexgym/check.test.mjs` para falhar e abrir um PR para `develop`, fora do rascunho.

Run: `gh pr checks <pr> -R lipedesign/openGym --required` e `gh pr view <pr> -R lipedesign/openGym --json mergeStateStatus`
Expected: `hexgym-ok` com `fail` e `BLOCKED`. Fechar o PR sem merge e apagar a branch.

---

### Task 12: Xcode 27.2, os IDs e o app no App Store Connect

**Issue:** #23, com a etiqueta `decisão do founder` e atribuída a `lipedesign`. **Quem faz:** o founder. O orquestrador só confere, sem ler segredo nenhum.

O que o founder faz, como lista na issue:

1. Instalar o Xcode 27.2 pela App Store do Mac (fica em `/Applications/Xcode.app`) e abrir uma vez, para ele instalar os componentes. O Xcode-beta pode ficar até o orquestrador confirmar.
2. Abrir `apple/HexGym.xcodeproj` no Xcode 27.2. Se ele oferecer "Update to recommended settings" ou converter o projeto, recusar: o formato fica o das Restrições globais. Em cada um dos quatro alvos, na aba Signing & Capabilities, com o time dele, deixar o Xcode registrar o App ID e o App Group `group.app.hexgym` (aparece um botão quando falta registrar). Ou dizer ao orquestrador "pode registrar", e ele tenta pelo `xcodebuild -allowProvisioningUpdates` com a conta do Xcode; se o App Group não ficar associado, volta para ele.
3. No App Store Connect, em Apps, o botão "+" e Novo app: iOS, nome "HexGym", idioma principal Português (Brasil), bundle ID `app.hexgym`, SKU `hexgym`. Se o nome não estiver livre, a escolha é dele.
4. Recomendado: uma chave da API do App Store Connect (Usuários e acesso, Integrações, Chaves da equipe), com a função Admin, que os certificados de distribuição na nuvem pedem. O arquivo `AuthKey_<KEY ID>.p8` vai para `~/.appstoreconnect/private_keys/`, e ele manda ao tech lead só o Key ID e o Issuer ID. Sem a chave, os envios usam a conta do Xcode.
5. No TestFlight, em Testes internos, criar o grupo "Founder" e se pôr nele.
6. Ao terminar, tirar a etiqueta `decisão do founder` da issue, ou avisar o orquestrador na conversa.

- [ ] **Step 1: Verify Xcode 27.2**

Run: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild -version`
Expected: `Xcode 27.2`.

- [ ] **Step 2: Verify the project survived Xcode 27.2**

Run: `node --test scripts/hexgym/project-format.test.mjs && git status --porcelain apple/`
Expected: PASS e nenhuma mudança no projeto.

- [ ] **Step 3: Verify signing for a device**

Run: `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild -project apple/HexGym.xcodeproj -scheme HexGym -destination generic/platform=iOS -derivedDataPath apple/DerivedData -allowProvisioningUpdates build`
Expected: `** BUILD SUCCEEDED **`, com os perfis de desenvolvimento dos quatro alvos.

- [ ] **Step 4: Verify the key, when there is one**

Run: `test -f ~/.appstoreconnect/private_keys/AuthKey_<KEY ID>.p8 && echo existe`
Expected: `existe`. Só a existência: o conteúdo nunca é lido nem impresso.

- [ ] **Step 5: Close the issue**

Comentar na issue o que foi conferido e `node scripts/hexgym/board.mjs move <n> done`.

---

### Task 13: TestFlight a partir desta máquina

**Issue:** #24.

**Files:**
- Create: `scripts/hexgym/testflight.mjs`, `scripts/hexgym/testflight.test.mjs`
- Create: `apple/ExportOptions.plist`

**Interfaces:**
- Consumes: `developerDir()` de `scripts/hexgym/xcode.mjs` (Task 7).
- Produces: `node scripts/hexgym/testflight.mjs [--dry-run]`; exporta `readAuth(env, exists) → { keyPath, keyId, issuerId } | null`, `buildNumber(now = new Date()) → string` e `uploadCommands({ developerDir, buildNumber, auth }) → [{ cmd, args, env }]`.

`apple/ExportOptions.plist`: `method = app-store-connect`, `destination = upload`, `teamID = MPAGLMK4Q2`, `signingStyle = automatic`, `uploadSymbols = true` e `manageAppVersionAndBuildNumber = false` (o número do build é o do script, não o do Xcode).

Os dois comandos:
1. `xcodebuild archive -project apple/HexGym.xcodeproj -scheme HexGym -configuration Release -destination generic/platform=iOS -archivePath apple/build/HexGym.xcarchive -allowProvisioningUpdates CURRENT_PROJECT_VERSION=<n>`
2. `xcodebuild -exportArchive -archivePath apple/build/HexGym.xcarchive -exportOptionsPlist apple/ExportOptions.plist -exportPath apple/build/export -allowProvisioningUpdates`

Com chave (variáveis `HEXGYM_ASC_KEY_ID` e `HEXGYM_ASC_ISSUER_ID`, e o arquivo `~/.appstoreconnect/private_keys/AuthKey_<id>.p8` existindo), os dois ganham `-authenticationKeyPath <arquivo> -authenticationKeyID <id> -authenticationKeyIssuerID <issuer>`; sem chave, usam a conta do Xcode. O número do build é a data e a hora em UTC, `AAAAMMDD.HHMM` (como `20261031.1507`), e só cresce: o `git rev-list --count` repetiria o número na Task 16, porque a branch de release sai de `develop` sem commit novo. Com a árvore suja, o script para, e um arquivo fora do git conta como mudança: numa pasta sincronizada, um arquivo novo entra no build.

- [ ] **Step 1: Write the failing tests**

```js
test('buildNumber is the UTC date and time, and only grows', () => {
  assert.equal(buildNumber(new Date(Date.UTC(2026, 9, 31, 15, 7))), '20261031.1507')
  assert.equal(buildNumber(new Date(Date.UTC(2026, 10, 1, 0, 5))), '20261101.0005')
})
test('commands without a key use the Xcode account', () => {
  const [archive, exp] = uploadCommands({ developerDir: '/Applications/Xcode.app/Contents/Developer', buildNumber: '20261031.1507', auth: null })
  assert.deepEqual(archive.args, ['archive', '-project', 'apple/HexGym.xcodeproj', '-scheme', 'HexGym', '-configuration', 'Release', '-destination', 'generic/platform=iOS', '-archivePath', 'apple/build/HexGym.xcarchive', '-allowProvisioningUpdates', 'CURRENT_PROJECT_VERSION=20261031.1507'])
  assert.ok(!exp.args.some(a => a.startsWith('-authentication')))
  assert.equal(archive.env.DEVELOPER_DIR, '/Applications/Xcode.app/Contents/Developer')
})
test('commands with a key pass the three flags to both steps', () => {
  const auth = { keyPath: '/k/AuthKey_ABC.p8', keyId: 'ABC', issuerId: 'iss' }
  for (const c of uploadCommands({ developerDir: '/x', buildNumber: '20261031.1507', auth }))
    assert.deepEqual(c.args.slice(-6), ['-authenticationKeyPath', '/k/AuthKey_ABC.p8', '-authenticationKeyID', 'ABC', '-authenticationKeyIssuerID', 'iss'])
})
test('readAuth only checks that the key exists', () => {
  const seen = []
  assert.equal(readAuth({}, p => { seen.push(p); return true }), null)
  const a = readAuth({ HEXGYM_ASC_KEY_ID: 'ABC', HEXGYM_ASC_ISSUER_ID: 'iss', HOME: '/h' }, p => { seen.push(p); return true })
  assert.deepEqual(a, { keyPath: '/h/.appstoreconnect/private_keys/AuthKey_ABC.p8', keyId: 'ABC', issuerId: 'iss' })
  assert.equal(readAuth({ HEXGYM_ASC_KEY_ID: 'ABC', HEXGYM_ASC_ISSUER_ID: 'iss', HOME: '/h' }, () => false), null)
})
test('a dirty tree stops the script, untracked files too', async () => {
  for (const status of [' M x\n', '?? apple/HexGym/Novo.swift\n']) {
    const r = await run(['--dry-run'], { git: args => args[0] === 'status' ? status : '' })
    assert.equal(r.code, 2); assert.match(r.stderr, /a árvore tem mudanças/)
  }
})
```

`readAuth` recebe só uma função `exists`: o script nunca lê o arquivo da chave.

- [ ] **Step 2: Run them to verify they fail**

Run: `node --test scripts/hexgym/testflight.test.mjs`
Expected: FAIL, `Cannot find module`.

- [ ] **Step 3: Implement `testflight.mjs` and `ExportOptions.plist`**

`--dry-run` imprime os dois comandos e não roda nada. `apple/build/` já está no `apple/.gitignore` (Task 7).

- [ ] **Step 4: Run them to verify they pass**

Run: `node scripts/hexgym/check.mjs scripts`
Expected: `ok`.

- [ ] **Step 5: Commit**

```bash
git add scripts/hexgym/testflight.mjs scripts/hexgym/testflight.test.mjs apple/ExportOptions.plist
git commit -m "TestFlight a partir desta máquina, com a chave da API ou a conta do Xcode"
```

Os passos 6 a 8 são do orquestrador, na worktree da Task, depois deste commit: o script só roda com a árvore limpa.

- [ ] **Step 6: Ask the founder before the first upload**

Parada da seção 9.1 (loja): o orquestrador mostra a saída do `node scripts/hexgym/testflight.mjs --dry-run` ao founder e espera o "pode mandar" na conversa.

- [ ] **Step 7: Upload**

Run: `node scripts/hexgym/testflight.mjs`
Expected: o export termina com `** EXPORT SUCCEEDED **` e o build aparece no TestFlight do app em alguns minutos.

- [ ] **Step 8: The founder opens it on his iPhone**

O founder instala pelo app TestFlight, do grupo "Founder", e confirma que o HexGym abre com a linha "Documento criado". É o "o app abre no iPhone dele" da seção 9.

---

### Task 14: O README, o CONTRIBUTING e o SECURITY do fork

**Issue:** #8.

**Files:**
- Create: `.github/README.md`, `.github/CONTRIBUTING.md`, `.github/SECURITY.md`

Em português, simples, sem travessão:

- **README:** o que é o HexGym (o app nativo de academia para iPhone e Apple Watch); que é um fork do openGym, com link para `https://github.com/DuarteSantos8/openGym`, o mesmo motor e os mesmos dados; a licença AGPL-3.0 e o `NOTICE.md`, com a exceção das lojas de apps; a regra das mídias de exercício da seção 5, em poucas linhas; o estado (fase 0); como compilar (Xcode 27.2, `node scripts/hexgym/check.mjs`); links para o documento de design e para o quadro, avisando que o quadro é privado. Não chama "HexGym" de marca registrada: a pesquisa no INPI e no USPTO está pendente (seção 11).
- **CONTRIBUTING:** o caminho de uma issue até o merge (seção 9.1), o Git Flow, o checklist do PR e o orquestrador.
- **SECURITY:** como avisar de uma falha sem abrir issue pública, pelo "Report a vulnerability" da aba Security. Ligar esse relato privado é uma configuração do repositório: o orquestrador pede o ok do founder junto com o texto, e liga com `gh api -X PUT repos/lipedesign/openGym/private-vulnerability-reporting`.

- [ ] **Step 1: Write the three files**

- [ ] **Step 2: Founder review**

Parada da seção 9.1: o texto é a página de entrada do projeto. A issue ganha `decisão do founder` até ele aprovar, e o orquestrador segue em outra issue enquanto isso.

- [ ] **Step 3: Verify that no root file changed**

Run: `git diff --stat origin/develop...HEAD -- README.md CONTRIBUTING.md SECURITY.md`
Expected: vazio.

- [ ] **Step 4: Commit**

```bash
git add .github/README.md .github/CONTRIBUTING.md .github/SECURITY.md
git commit -m "README, CONTRIBUTING e SECURITY do HexGym em .github/"
```

- [ ] **Step 5: After the merge, verify what GitHub shows**

Run: `gh api repos/lipedesign/openGym/community/profile --jq '.files.readme.html_url, .files.contributing.html_url'` e abrir `https://github.com/lipedesign/openGym/security/policy`
Expected: as duas URLs em `.github/`, e a política do HexGym na aba Security. Se o GitHub mostrar o `SECURITY.md` da raiz, registrar na issue e decidir com o founder se o da raiz muda.

---

### Task 15: A cópia dos arquivos do corpo e a procedência da referência

**Issue:** #10. Espera duas respostas do founder: onde guardar, e como a imagem `ref/referencia-corpo.jpg` foi feita (desenho, IA ou foto, e de quem). A recomendação do tech lead é um repositório privado na conta lipedesign, fora da rede de forks do openGym.

**Files:**
- Modify: `scripts/hexbody/README.md`

- [ ] **Step 1: Get the two answers**

A issue já tem `decisão do founder`. Sem as respostas, o orquestrador segue em outras issues.

- [ ] **Step 2: Make the copy**

No repositório privado: `gh repo create lipedesign/hexgym-corpo --private --description "Arquivos de origem do corpo do HexGym"` (criar repositório na conta dele é a resposta do passo 1 que autoriza). Se algum arquivo de `scripts/hexbody/work/` passar de 100 MB, o limite do GitHub, esses vão por Git LFS. Num iCloud Drive ou Google Drive, quem copia é o founder, ou o orquestrador numa pasta que ele indicar.

- [ ] **Step 3: Write it down**

No `scripts/hexbody/README.md`: onde a cópia fica, como trazer de volta para `scripts/hexbody/work/` e como a imagem de referência foi feita.

- [ ] **Step 4: Verify the restore**

Trazer a cópia para uma pasta limpa e rodar os passos 5 a 7 do README do hexbody.
Expected: as mesmas saídas (mesmo hash) que as de `scripts/hexbody/work/`.

- [ ] **Step 5: Commit**

```bash
git add scripts/hexbody/README.md
git commit -m "Onde ficam os arquivos de origem do corpo e de onde vem a referência"
```

---

### Task 16: A versão 0.1.0

**Issue:** #25. Depende de todas as outras, menos a 15: o passo 1 decide a #10.

- [ ] **Step 1: Check that the phase is done**

Run: `gh issue list -R lipedesign/openGym --milestone "Fase 0: Fundação" --state open`
Expected: só esta issue. Se a #10 ainda esperar apenas as respostas do founder, ela passa para o milestone "Fase 1: Design system", com um comentário dizendo por quê.

- [ ] **Step 2: Cut the release branch**

`git worktree add .claude/worktrees/release-0.1.0 -b release/0.1.0 origin/develop` e conferir que `MARKETING_VERSION = 0.1.0`.

- [ ] **Step 3: Take the prints and a short video**

No simulador do iPhone e no do Watch, compilados assinados como no passo 7 da Task 9: o print de cada tela e um vídeo do app abrindo, com até 15 s e menos de 5 MB (`xcrun simctl io <udid> recordVideo --codec h264 <arquivo>.mp4`). Os arquivos vão para `docs/hexgym/prints/<issue>/`, num commit na branch da release.

- [ ] **Step 4: Build for TestFlight**

Na worktree da release, depois do commit: `node scripts/hexgym/testflight.mjs`.

- [ ] **Step 5: Open the release pull request**

`gh pr create -R lipedesign/openGym --base main --head release/0.1.0 --title "Versão 0.1.0: a fundação"`, com o que entrou na fase, os prints do iPhone e do Watch, o link do vídeo e o número do build no TestFlight, como dizem as Restrições globais.

- [ ] **Step 6: Call the founder**

Parada da seção 9.1, fim de fase: comentário no PR e mensagem na conversa, com os prints e o vídeo. Nada segue sem a aprovação dele.

- [ ] **Step 7: Merge, tag and bring it back**

Depois da aprovação: `gh pr merge <pr> -R lipedesign/openGym --merge --match-head-commit <sha>`; `gh release create v0.1.0 -R lipedesign/openGym --target main --title "HexGym 0.1.0" --notes-file <notas>`; e um PR de `main` para `develop`, que entra com merge normal.

- [ ] **Step 8: Close the phase**

`gh api -X PATCH repos/lipedesign/openGym/milestones/1 -f state=closed`. Depois, `node scripts/hexgym/board.mjs phase` imprime a Fase 1. O filtro da visão "Fase atual" só muda pela página do Project: o founder troca, ou o orquestrador pelo Claude in Chrome com o ok dele. A página do design ganha o resultado da fase.
