# 2026-11-01: o orquestrador do HexGym em cima do relentless

- **Data:** 2026-11-01 (America/Sao_Paulo)
- **Origem:** issue #15 (Tarefa 1 da fase 0, o orquestrador)
- **Quem decidiu:** o tech lead. São decisões técnicas (seção 9.1 da especificação); nada aqui muda
  produto ou visual.

## Contexto

A Tarefa 1 do plano da fase 0 criava um orquestrador próprio: dois agentes (`hexgym-implementador` e
`hexgym-revisor`), um quadro que movia os cartões do Project 6 e duas etiquetas de espera
(`decisão do founder` e `bloqueado`). Com o relentless 1.4.8 ativado neste projeto (nota
`2026-11-01-relentless-no-git-flow.md`), boa parte disso já existe: os papéis (implementador, QA,
revisor isolado, planner, documenter), as etiquetas `state:*` e `human:*`, o pedido de decisão com o
`/decide` e os portões do merge. Esta nota diz o que o HexGym usa do relentless, o que fica nosso e
por quê. O plano da fase 0 e a seção 9.1 da especificação mudam junto com ela.

## Decisão

### Papéis

- A sessão principal do Claude Code faz o papel do orquestrador do relentless, pela skill
  `hexgym-orquestrador`. A skill lê o `agents/orchestrator.md` do plugin (a pasta vem de
  `claude plugin list --json`, campo `installPath`) e diz onde o HexGym muda.
- Os agentes são os do relentless, chamados com o modelo escrito: `relentless:implementer`,
  `relentless:qa` e `relentless:reviewer`. O `relentless:documenter` escreve o resumo no fim de cada
  fase. Os planos continuam saindo do superpowers:writing-plans, aprovados pelo founder; o
  `relentless:planner` não escreve plano de fase.
- Os agentes `hexgym-implementador` e `hexgym-revisor` não são criados.
- Uma issue de cada vez.

### O estado e o quadro

- A verdade é a etiqueta `state:*` da issue, uma só, que só o orquestrador troca (`set-state.sh`).
- O `board.mjs sync` espelha as etiquetas no Project 6: `state:todo` pronta vai para "Pronto para
  começar", e as outras `state:todo` para "A fazer"; `state:in-progress`, "Em andamento";
  `state:review`, "Em revisão"; `state:done` ou fechada, "Feito"; `state:blocked` fica onde está.
  Ele também põe no Project a issue que falta e dá `state:todo` à issue aberta sem `state:*`.
- Pronta quer dizer: aberta, no milestone da fase atual, `state:todo`, sem `human:pending`, sem a
  etiqueta `epic` e com as dependências fechadas (linha `Depende de:` ou `Blocked by:`).
- O `board.mjs next` retoma primeiro a issue em `state:review`, depois a em `state:in-progress`, e só
  então pega a pronta de menor número. Nunca devolve um épico. O `move` e o `refresh` do plano antigo
  saem.
- Mover um cartão à mão não muda o estado: na próxima volta, o quadro volta a seguir a etiqueta.

### As esperas pelo founder

- Toda espera é um pedido de decisão do relentless. O `request-decision.sh` põe `human:pending` e
  `state:blocked` e atribui a issue ao Lipe. O texto vai em português, no formato de
  `core/templates/decision-request.md`: a pergunta, o contexto, as opções numeradas (prós, contras, o
  que muda, o que afeta, os riscos e o custo de voltar atrás) e a recomendação, com os marcadores
  `<!-- relentless:author=agent -->` e `<!-- relentless:decision-request -->`.
- O Lipe responde numa sessão do Claude Code neste projeto com `/decide <issue> <opção> [nota]`. O
  gancho do relentless grava a decisão, troca `human:pending` por `human:decided` e devolve a issue
  para `state:todo`. O gancho acha o repositório pelo `gh repo view`, que neste checkout resolve para
  `lipedesign/openGym` (`gh repo set-default`).
- Um passo do founder (um clique, uma instalação) também é um pedido, com a opção 1 "feito".
- Uma issue que volta de um `/decide` não começa de novo. Com código, ela é retomada pelo estado do
  PR. Sem código, pelo último passo comentado: numa Tarefa sem código, o orquestrador comenta cada
  passo feito na issue, com a prova, e o pedido de decisão conta como o passo em que sai. Os passos
  que uma Task com código dá ao orquestrador antes do merge (o envio ao TestFlight da Task 13, por
  exemplo) seguem a mesma regra.
- A resposta do founder entra no critério de aceite: o `context.mjs` põe na brief e no pacote de
  revisão os pedidos e as respostas da issue (os comentários com `relentless:decision-request` e com
  `relentless:decision option=`).
- As etiquetas `decisão do founder` e `bloqueado` saem. A visão "Pede você" passa a filtrar
  `label:"human:pending","state:blocked" is:open`.
- O orquestrador para na lista fechada do relentless (ADR; segredos e credenciais; proteção de
  branch; publicação num registro; `state:blocked`; apagar branch ou reescrever histórico) e nas
  paradas da seção 9.1: decisão de visual ou de produto; dinheiro, contas, loja ou falar com o Duarte;
  o fim de cada fase e tudo que entra em `main`; o primeiro envio ao TestFlight; o texto público do
  projeto (README e afins); e quando trava de verdade.
- Apagar branch é parada, com duas exceções: a branch local de um PR que já entrou (a remota o
  GitHub apaga no merge) e a branch de teste que o próprio orquestrador criou na mesma Task, sem
  trabalho de ninguém (o PR de teste da Task 2 e o da Task 11).

### Base `develop` e squash

- O orquestrador cria a worktree antes de chamar o implementador, porque o `relentless:implementer`
  diz `origin/main` e `--type feat`:
  `worktree-create.sh --repo lipedesign/openGym --workdir <checkout> --issue <n> --slug <nome> --type feature --base develop --path <checkout>/.claude/worktrees/<n>-<nome>`.
- O merge segue a nota anterior: `merge-if-ready.sh --dry-run` saindo com 0 (uma linha `ADRs:`,
  `review:approved` e o veredito no commit atual), os checks obrigatórios verdes depois da #3, e o
  squash à mão com `gh pr merge --squash --match-head-commit`. O `merge.default` continua `human`:
  quem faz o merge é o tech lead, como diz a seção 9.1.
- Até a #3, o `wait-ci.sh` sai sempre com 3, porque nenhum check roda nos PRs. O implementador não
  fica esperando: roda as checagens locais e reporta.
- Os commits usam a mensagem que a Task pede, sem o prefixo de conventional commits. O
  `check-commit-msg.sh` não vale aqui: o squash leva só o título do PR.
- O repositório apaga a branch do PR no merge. O `worktree-cleanup.sh` tira a worktree e deixa a
  branch local, que o orquestrador apaga depois do merge.

### A Task do plano é o critério de aceite

- O `build-review-bundle.sh` usa o corpo da issue como critério de aceite e manda o diff inteiro. No
  HexGym, o requisito é a Task do plano, e o diff do motor traz um script gerado de uns 2 MB.
- O `scripts/hexgym/context.mjs` monta os dois textos. O `brief` junta as Restrições globais, o Foco
  da revisão e a Task. O `review` monta o pacote do relentless, com os mesmos títulos, mais a Task
  lida de `origin/develop`, sem os lockfiles e sem os arquivos gerados de `reviewExclude`, e diz o que
  ficou de fora.
- Issue sem linha `Plano:` (um achado de revisão, por exemplo) usa o próprio corpo como requisito,
  com as Restrições globais e o Foco da revisão do plano da fase.
- A revisão: o `relentless:reviewer` recebe só o caminho do pacote; a resposta inteira vai para
  `.relentless/review/<pr>/agent-out.md`; e o `run-isolated-review.sh --from-output` lê a última
  linha (`Verdict: approved` ou `Verdict: changes_requested`), comenta os achados no PR e troca as
  etiquetas. O arquivo não pode ser o `reviewer-out.md` da mesma pasta: o script copia a saída para
  lá, e o `cp` de um arquivo nele mesmo falha.
- Antes de aplicar o veredito, o commit do PR tem que ser o mesmo do pacote. Se mudou, o pacote e a
  revisão são refeitos.

### QA

- O `relentless:qa` roda `node scripts/hexgym/check.mjs <partes>` na worktree e usa o app de verdade
  quando a Task tem tela (simulador, com os prints e vídeos das Restrições globais).
- O orquestrador publica com o `fill-qa-section.sh`, que comenta no PR e troca a seção
  `## QA / dogfood result` do corpo até o próximo título `## `. Por isso o modelo de PR passa a usar
  `##` em todos os títulos.

### O registro

- O `docs/decisions/log.jsonl` segue a doutrina do relentless: uma linha por decisão do founder
  (`human_decide`) e por decisão do orquestrador (`merge`, `changes_requested`, `state_change`), com
  os campos do `orchestrator.md`.
- As linhas esperam em `.claude/hexgym/log-pendente.jsonl`, fora do git, e entram no primeiro commit
  da branch da próxima issue com código. Nunca entram num PR em revisão.

### Etiquetas, modelos e milestones

- A Tarefa 1 troca as esperas da #3 e da #10 por pedidos de decisão e apaga `decisão do founder` e
  `bloqueado`. A #23 ganha o pedido dela quando ficar pronta, depois da Task 9: a lista do founder
  abre o projeto Xcode, que só existe a partir dali.
- A Task 3 (#11) passa `feature` para `enhancement` e `docs` para `documentation`, apaga `feature` e
  `docs` e troca `accessibility` por `acessibilidade`. `chore` e `upstream` ficam como tipos só do
  HexGym. As seis etiquetas padrão do GitHub ficam, porque o bootstrap do relentless as recria.
  Apagar as branches herdadas passa por um pedido de decisão.
- Os formulários Tarefa e Bug ganham `state:todo`. Os três do relentless ficam.
- O milestone de cada fase ganha a seção `## Outcome`, e a fase ganha um épico com todas as issues
  dela como sub-issues. A fase 0 recebe os dois na Tarefa 1; as outras, quando o plano delas for
  escrito.
- No `.relentless/config.json`, `checks.test` passa a ser `node scripts/hexgym/check.mjs` e
  `checks.install`, `npm ci && npm ci --prefix frontend`.

## Doutrina para quem escreve

- Para trocar o estado, `set-state.sh`; nunca `gh issue edit` com `state:*`.
- `human:pending` só entra pelo `request-decision.sh` e só sai pelo `/decide` do Lipe. Agente não
  roda `/decide` nem `decide.sh`.
- Achado de revisão, de QA ou de CI que fica para depois vira uma issue no milestone da fase,
  sub-issue do épico, com a linha `Origem: achado durante <revisão|QA|CI> da PR #<n>`.
- Os nomes e as opções desta nota são os do relentless 1.4.8. Depois de atualizar o plugin, reler o
  `agents/orchestrator.md` e os scripts que a skill chama.

## Evidência

- `run-isolated-review.sh`, linhas 90 a 98: com `--from-output`, copia o arquivo para
  `.relentless/review/<pr>/reviewer-out.md` e aplica o veredito, sem chamar outro `claude`.
- `apply-review-verdict.sh`: o comentário do veredito leva os achados e o commit; as etiquetas só
  mudam depois dele.
- `fill-qa-section.sh`: troca do título `## QA / dogfood result` até o próximo `## `.
- `merge-if-ready.sh`, linhas 634 a 638: no modo `auto`, `gh pr merge --merge`.
- `worktree-cleanup.sh`: remove a worktree e não apaga a branch.
- `pretool-protect-worktree-write.sh`: só barra escrita fora da worktree quando o checkout tem
  `.relentless/worktree.json` ou o ambiente diz `RELENTLESS_ROLE=implementer`.
- Neste checkout, `gh repo set-default --view` imprime `lipedesign/openGym`, e o repositório tem
  `delete_branch_on_merge` ligado.
- `updateProjectV2View` com `filter` testado sem mudar nada na visão "Pede você", em 01/11/2026.
- `lib/human-decision.sh` (usado pelo `decide.sh` e pelo gancho do `/decide`): o comentário da
  resposta leva `<!-- relentless:decision option="<K>" -->` e a nota; a issue troca `human:pending`
  por `human:decided` e volta para `state:todo`.
- `check-milestone-outcomes.sh` só lê os milestones abertos (`milestones?state=open`): no fim da
  fase, ele roda antes de o milestone fechar.
