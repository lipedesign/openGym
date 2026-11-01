# 2026-11-01: o relentless no Git Flow do HexGym

- **Data:** 2026-11-01 (America/Sao_Paulo)
- **Origem:** issue #15 (Tarefa 1 da fase 0, o orquestrador)

## Contexto

O HexGym passa a usar o relentless (1.4.8) como base do trabalho feito por agentes. O plugin fica
ativado só neste projeto, em `.claude/settings.json`, que o git não vê.

O relentless supõe um repositório com `main` como base:

- o `worktree-segura` e os agentes dizem `origin/main`;
- o `worktree-create.sh` usa `--base main` quando não recebe outra;
- o `merge-if-ready.sh` faz o merge com `gh pr merge --merge`;
- o bootstrap grava o `relentless-ci.yml`, que falha de propósito quando não acha comando de teste;
- o `wait-ci.sh` olha só a última execução de workflow do branch.

O fork segue o Git Flow da seção 9.1 de `docs/superpowers/specs/2026-10-31-hexgym-native-app-design.md`:
`develop` é a branch padrão e integra o trabalho, e `main` só recebe versões.

## Decisão

- **Base `develop`.** Onde o relentless diz `origin/main`, leia `origin/develop`. A worktree sai assim,
  com `<checkout>` sendo o checkout principal (nesta máquina, `/Users/lipe/Developer/MyGym`):
  `worktree-create.sh --repo lipedesign/openGym --issue <n> --slug <nome> --type feature --base develop --path <checkout>/.claude/worktrees/<n>-<nome>`.
  O branch fica `feature/<n>-<nome>`, e o PR vai para `develop` com `Closes #<n>`.
- **Squash nas features.** Com `merge.default` em `human`, o `merge-if-ready.sh` confere os gates e
  comenta que o PR está pronto. O merge é `gh pr merge <PR> -R lipedesign/openGym --squash`, feito pelo
  tech lead ou pelo Lipe. O `merge:auto` só entra depois que a CI rodar (issue #3) e o relentless
  souber fazer squash.
- **Merge normal, nunca squash:** `release/*` e `hotfix/*` em `main`, o PR de `main` para `develop` e
  o sync `sync/opengym-<data>` (seção 8.11).
- **CI:** o `test.yml` (job `tests-ok`) e, a partir da #9, o `hexgym.yml` (job `hexgym-ok`). O
  `relentless-ci.yml` não fica no repositório. Os `checks` de `.relentless/config.json` mudam junto
  com a #9.
- **Etiquetas e modelos de issue:** valem as etiquetas da seção 9.1, e as do relentless convivem com
  elas. A revisão da #15 casa as de tipo (`enhancement` e `documentation` com `feature`, `docs`,
  `chore` e `upstream`), as de espera (`human:pending` com `decisão do founder`, `state:blocked` com
  `bloqueado`) e os modelos de issue do relentless com os nossos.
- **Nenhuma onda do relentless antes da revisão da #15.** Os milestones ainda não têm a seção Outcome
  nem os épicos, e o quadro do Project 6 não acompanha as etiquetas `state:*`.
- **Título do PR** em português, simples, dizendo o que muda, porque vira o commit do squash. O
  prefixo de conventional commits não é exigido.
- **Linha `ADRs:`** no corpo do PR, uma vez só. O modelo de PR já traz.
- **Proteção das branches** não vem do bootstrap: fica com a #3.

## Doutrina para quem escreve

- Leia `docs/decisions/` antes de planejar ou implementar.
- O bootstrap, rodado de novo, regrava `.github/ISSUE_TEMPLATE/config.yml`, a descrição da etiqueta
  `bug` e o `relentless-ci.yml`. Depois dele, volte o `config.yml` (o link do documento de design) e a
  descrição "Tipo: algo não funciona como deveria", e apague o `relentless-ci.yml`.
- No sync com o openGym, um conflito no fim do `CLAUDE.md` fica com as duas partes: o texto do
  openGym e o bloco do relentless.
- O `.worktreeinclude` leva o `.claude/settings.json` para cada worktree nova, para o relentless
  continuar ativado nela.
- O relentless 1.4.8 não roda no bash 3.2 do macOS sem a correção guardada em
  `.claude/relentless-compat/`, nesta máquina e fora do git. Depois de atualizar o plugin, siga o
  README de lá.

## Evidência

- `bootstrap.sh --apply` em 01/11/2026: 19 etiquetas novas (de 21 para 40), `.relentless/config.json`
  com `merge.default` em `human` e o decisor Lipe (`lipedesign`), e `core.hooksPath` em
  `.relentless/githooks`.
- Com a correção, as suítes do próprio relentless passam no bash 3.2: 176 de 176 testes.
