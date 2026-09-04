# Auditoria da peça da stack — T-3

> **RASCUNHO / CHECKLIST (rodada 0)** — preparado em 2026-09-04 04:57 BRT, ANTES de o desenho existir.
> Nenhum veredito emitido: `/private/tmp/claude-501/-Users-gabriel/9ea7e425-c964-46fa-824f-267ff5661c8b/scratchpad/peca-stack/desenho.md` ainda não foi entregue.
> Aguardando o ask envelopado `[ARQ/peca-stack/T-2] desenho v1 …; auditar`.
> Insumos já lidos: briefs T-2 e T-3, os 3 dossiês (infra 137 linhas, maestri 173, memória 114), MAESTRI.md v3.1 inteiro (§0–§12 + Aprendizados 04/09).

---

## 0. Estado da rodada

| Rodada | Data-hora | Versão auditada | Veredito | Itens FAIL |
|---|---|---|---|---|
| 0 (checklist) | 2026-09-04 04:57 | — (desenho ausente) | — | — |
| 1 | 2026-09-04 05:5x | desenho v1 (Tacógrafo) | **FAIL** | 5 |
| 2 (delta) | 2026-09-04 07:3x | desenho v2 | **PASS** | 0 |
| 3 | | | | |

Máximo 3 rodadas (brief T-3). Após a 3ª sem PASS → reporte de FAIL ao brocador.

---

## 1. Tabela das 6 claims (a preencher na rodada 1)

O desenho deve trazer, na seção `## Claims falsificáveis`, **exatamente 6** afirmações factuais. Formato obrigatório do meu veredito por claim:

| # | Claim (texto literal do desenho) | Método de refutação aplicado | Evidência (comando/arquivo/linha) | Veredito |
|---|---|---|---|---|
| C1 | | | | SUSTENTADA / REFUTADA / SEM PROVA |
| C2 | | | | |
| C3 | | | | |
| C4 | | | | |
| C5 | | | | |
| C6 | | | | |

**Regras de veredito (autoimpostas, para não afrouxar):**
- SUSTENTADA exige fonte primária que eu mesmo executei/li nesta sessão, ou fato de dossiê com `confiança: verificado` **citado por linha**. Dossiê com `confiança: inferido` NÃO sustenta claim sozinho → vira SEM PROVA.
- "Parece razoável", "é padrão de mercado", "a documentação sugere" = SEM PROVA.
- REFUTADA exige: evidência + correção concreta + impacto no desenho (que seção cai).
- Claim não falsificável (sem número, sem comando, sem limite: "o sistema é robusto") = FAIL de forma, antes do mérito.

---

## 2. Munição pré-carregada (fatos dos dossiês para tentar derrubar o desenho)

Uso estes como armadilhas: se o desenho contrariar algum, é REFUTADA na hora.

### 2.1 Hardware / capacidade (dossie-infra)
- Servidor: 4 threads (nproc), 15Gi RAM com **13Gi disponíveis**, 163G livres de 220G, load 0.21–0.73 ocioso. — infra l.22–23. *Medição minha 04:55 BRT: `up 18:41`, load **3.55** 1-min / 1.08 5-min → a máquina NÃO está sempre ociosa; qualquer claim de "sobra de 4 threads" tem que contar com picos.*
- Mac: 16 GB, **12Gi livres de disco (94% cheio)**, 15 containers, VM do Docker reservando 1.292 MB. — infra l.7–9, l.67. → Peça que exija Docker novo **no Mac** é FAIL quase automático.
- Trigger.dev self-hosted foi descartado por exigir 3+4 vCPU em máquina de 4 threads. — infra l.52. → Qualquer componente com apetite semelhante herda o mesmo veto.
- Energia: sem no-break, sem "Restore on AC Power Loss", incidente 2026-08-08 com **3h25 de downtime** + troca de IP. — infra l.60.
- IP `dynamic` (sem reserva DHCP), já mudou .4 → .6. — infra l.25. Tailscale ativo (servidor 100.67.145.96, Mac 100.75.185.73) mitiga só acesso administrativo. — infra l.31.
- Sem ingress público: cloudflared **ausente** no servidor e nunca autenticado no Mac. — infra l.32. → Peça que dependa de webhook externo apontando para casa: FAIL sem fase explícita de cloudflared.
- Sem firewall de host; 8080/8081/19999 em 0.0.0.0 na LAN. — infra l.34–36.
- Backup **é zero**: `~/backups/123licitar` vazio, nenhum timer/cron de backup. — infra l.37–38.
- Segredos em .env texto puro replicados em ≥5 lugares. — infra l.41–42.
- Vercel Hobby estourado (Fluid CPU 6h46/4h, ISR 239K/200K) — dado de 2026-08-09, **não reconferido** (infra "Desconhecidos" l.120). → Se o desenho fizer conta com essa cota, a claim é no máximo SEM PROVA.
- Node em 3 majors (Mac 25, servidor 22, CI 20); pnpm 10.30.2 vs 9.15.4. — infra l.13.
- n8n não roda em lugar nenhum; `which n8n` = not found. — infra l.33.

### 2.2 Maestri / protocolo (dossie-maestri + MAESTRI.md)
- `maestri ask` tem **comportamento contraditório documentado**: o `--help` diz que bloqueia até idle; os Aprendizados 04/09 dizem que retorna em segundos (idle falso). — maestri l.88, MAESTRI.md Aprendizados. → Desenho que dependa do ask como transporte síncrono = REFUTADA.
- Envelope `[MAESTRO/...]` é **convenção textual, sem verificação mecânica**. — maestri l.25, l.145.
- `maestri notify` ≤ 500 caracteres; `notify/recruit/role/routine/workspace/floor` são **Maestro-only**. — maestri l.7, l.12. → Peça cujo componente precise chamar esses comandos de dentro de um recruta: FAIL.
- Sem status estruturado de terminal: "está trabalhando?" é `maestri check | grep 'esc to interrupt'`. — maestri l.144.
- Hook `Stop` via `--settings` funciona (T8/T8i) mas `/private/tmp/maestri-stops.log` **não existe hoje** — o mecanismo está ocioso. — memória l.59.
- `permissions.deny` vale sob bypassPermissions, mas **só foi testado em padrões `Bash(...)`** — MCP/Edit/Write/WebFetch sem prova. — maestri l.110, l.160.
- `--append-system-prompt-file` e `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` **não constam do `--help`**; `--disallowedTools Agent Workflow` vira no-op silencioso se os tools forem renomeados. — maestri l.111.
- Hook PreToolUse com decisão `ask` abre dialog **mesmo sob bypass e em comando read-only** → recruta trava. — maestri l.37.
- `dismiss` apaga `.maestri/roles/<uuid>`, compartilhado por terminais da mesma role. — maestri l.58, l.71.
- Editar `~/.maestri/preferences.json` fora do app é **trabalho descartável** (o app regrava ao fechar). — maestri l.62. → Peça que persista estado dentro do app: REFUTADA.
- 10 recrutas sumiram + `routines.json` zerado em 04/09; app **sem lock entre sessões-maestro**. — maestri l.86, l.112.
- Cap de **6 processos `claude` ociosos**; cada um 99–279 MB RSS; 10 somaram ≈1,6 GB. — maestri l.101.
- Incidente de custo: **130 USD em 45 min (123 USD/h)**, 10 terminais, effort xhigh herdado da conta. — maestri l.85.
- `/model` e `/effort` via ask **gravam default na conta**; `/effort` em voo invalida o cache. — maestri l.89.
- Gate verde **não prova fiação** (caso 19/08: função implementada e desligada, typecheck verde). — maestri l.75, l.149.
- Presets não-Claude (Codex, Antigravity, OpenCode, Shell) nascem **sem deny, sem guardrails, sem bloqueio de fan-out**. — maestri l.156.

### 2.3 Memória / custo / preferências (dossie-memoria)
- `ccusage` **não está no PATH** (`which ccusage` → not found); depende de `npx -y` a cada uso. — memória l.53.
- Token Dash **fora do ar** e no caminho errado (real: `~/Desktop/figma-tokens-plugin/token-dash`, sob iCloud/TCC, `ls` estourou 120s). — memória l.49–50.
- `ccusage` **superconta output em ~26%** por não deduplicar por `message.id`. — memória l.57. → Claim de economia medida por ccusage cru é SEM PROVA.
- Endpoint oficial de cota: `GET https://api.anthropic.com/api/oauth/usage` (Bearer + `anthropic-beta: oauth-2025-04-20`), tokens no Keychain (`Claude Code-credentials`, `…-38472cd9`). — memória l.52.
- `~/kb` é git **sem remote** — nenhum backup fora da máquina. — memória l.25.
- Recall nativo por relevância **não funciona** (flag `tengu_moth_copse`, zero ocorrências em 320 transcripts); `CLAUDE_MEMORY_STORES` decidido como "não usar". — memória l.26–27.
- Teto de índice: só **200 linhas / 25 KB** do MEMORY.md entram no contexto; lint avisa a partir de 180. — memória l.30.
- Conta **empresa** (padrão dos recrutas) **não tem `hooks` nem `permissions`** — o guard de conta só existe na pessoal. — memória l.40, l.100.
- Custo de contexto atual da memória: ~6,7 KB/sessão (CLAUDE.md + MEMORY.md), dobrado na home. — memória l.68.
- Preferência dura: "não devemos queimar tokens se não tiver explícito"; "acabou a ostentação de tokens". — memória l.14, l.16.
- Preferência dura: nada de menu AskUserQuestion; prosa curta com recomendação na frente. — memória l.10.
- Adendo do T-2 (04/09 04:58): a decisão de NÃO construir precisa vir de **teste ou número**, não de cautela.

---

## 3. Checklist de auditoria (escopo a–e do brief T-3)

### (a) As 6 claims — tentar refutar de verdade
- [ ] São **exatamente 6**? (≠6 → FAIL de forma)
- [ ] Cada uma é falsificável: tem número, comando, versão, porta ou limite que eu possa checar?
- [ ] Para cada claim, escolher e registrar o método:
  - **Hardware/capacidade** → SSH read-only: `nproc`, `free -h`, `df -h`, `docker ps`, `docker images`, `ss -tlnp`, `crontab -l`, `uptime`. Medir 2× se for claim de folga (o load de 04:55 já mostrou pico de 3.55).
  - **Existência de comando/flag do Maestri** → `maestri <cmd> --help` e `maestri --help` (leitura); confrontar com maestri l.6–21. Flag ausente do `--help` (ex.: `--append-system-prompt-file`) ≠ inexistente, mas vira SEM PROVA se o desenho depender dela sem teste.
  - **Versão/arquitetura/licença/requisito de software** → WebSearch/WebFetch na doc oficial. Exigir **amd64** (servidor é i5-5200U) e RAM declarada pelo fornecedor.
  - **Comportamento do Claude Code / transcripts** → ler arquivo em `~/.claude*/projects/…` (leitura pura).
  - **Custo de tokens** → ccusage não instalado + superconta 26% → qualquer número de economia sem metodologia declarada é SEM PROVA.
- [ ] Alguma claim é na verdade *desejo* ("a peça vai reduzir o gasto") em vez de fato verificável? → FAIL de forma.
- [ ] Alguma claim depende de item listado nos **Desconhecidos** dos dossiês (Vercel hoje, deny em MCP, `--disallowedTools` pós-upgrade, n8n do SEB, hiveos, BIOS, SMART)? → SEM PROVA obrigatório.

### (b) Contradições
- [ ] Contra fatos dos dossiês (citar arquivo + linha; a lista da §2 é o gabarito).
- [ ] Contra **MAESTRI.md §11** (decisões fechadas — reabrir sem fato novo é FAIL):
  - [ ] "agente-interface leve → terminal-cérebro" (rejeitada 07/07) — a peça reintroduz hop de interpretação sobre o `ask`?
  - [ ] bypassPermissions + deny (não allowlist/acceptEdits).
  - [ ] Brief/guardrails são o canal confiável; preset é conveniência.
  - [ ] Reporte durável em **arquivo**; nota é espelho.
  - [ ] Recrutas na conta empresa por padrão.
  - [ ] **Verificação mecânica é dos recrutas, não do maestro** (26/07, reafirmada 04/09) — peça que faça o maestro rodar varredura = FAIL.
  - [ ] Dismiss só com GO (exceto pessoal ao concluir).
- [ ] Contra o princípio §0: "instrução em prompt é empurrão; o que barra erro é gate mecânico" — a peça entrega gate **mecânico** ou só mais texto de protocolo?
- [ ] Contra o já descartado no T-2: Coolify/Dokploy, "mais um dashboard", Trigger.dev self-hosted, Oracle Cloud.
- [ ] Contra o adendo 04/09: a recusa de construir algo veio de teste/número ou de cautela?

### (c) Completude (cada item ausente = FAIL numerado)
- [ ] **Backup** da própria peça e dos dados que ela gera (dossiê: backup é zero hoje; `~/kb` sem remote).
- [ ] **Segredos**: onde vivem, modo do arquivo, quem lê, rotação. Nada de sexta cópia de `.env`.
- [ ] **Autenticação / exposição de rede**: porta nova em 0.0.0.0 sem firewall = FAIL; Tailscale-only ou 127.0.0.1 é o mínimo.
- [ ] **Queda de energia**: o que acontece com a peça em 3h25 de downtime; ela religa sozinha (`restart: unless-stopped` / systemd) sem BIOS?
- [ ] **IP DHCP**: a peça usa `192.168.24.6` hardcoded? (já mudou uma vez) — exigir nome/Tailscale/descoberta.
- [ ] **Custo de tokens**: a peça **baixa** o gasto do maestro? Com que número e medido como? Componente que consome tokens (agente extra rodando sozinho) precisa de teto declarado.
- [ ] **Quem mantém**: dev solo; manutenção recorrente declarada em minutos/mês; o que quebra a cada upgrade do Maestri/Claude Code (§10 já exige re-teste manual).
- [ ] **Como testar o próprio sistema**: existe suíte/gate que prova que a peça funciona, e regenerável do zero?
- [ ] **RAM/threads reais**: soma de RAM dos componentes novos + 6 recrutas ociosos (≈0,6–1,7 GB) cabe nos 13Gi do servidor? No Mac (12Gi de disco livre, VM Docker já em 1,3 GB) cabe?
- [ ] Regenerável do zero e **falha aberto** (adendo 04/09): se a peça morrer, o Maestri continua funcionando?
- [ ] Testado nas **2 contas** (pessoal e empresa; empresa não tem hooks/permissions).

### (d) "Por que NÃO de outra forma"
- [ ] A tabela existe com **≥3 alternativas óbvias** e motivo concreto (número, limite ou incidente datado) em cada linha?
- [ ] As alternativas óbvias que EU esperaria — se faltar alguma sem justificativa, é FAIL:
  1. Não construir nada / continuar manual (baseline).
  2. Comprar/assinar SaaS pronto (bloqueado por "sem gasto novo de nuvem além de free tier").
  3. Fazer no Vercel/nuvem (Hobby estourado; Oracle morta).
  4. n8n (nunca saiu do papel — é alternativa e é risco).
  5. Hook nativo do Claude Code (Stop/PostToolUse) em vez de componente novo — o mais barato; **se o desenho não explicar por que o hook não basta, é FAIL**.
  6. Rotina do próprio Maestri (`routine --every … --pre-run`), citada nos dossiês como "a validar".
- [ ] Cada "por que não" é motivo concreto, não preferência estética?

### (e) Especificidade (generalidade = FAIL)
- [ ] Portas explícitas e **livres**: conferir contra `ss -tlnp` (ocupadas: 22, 8080, 8081, 19999, 5355, 127.0.0.1:25/8125/4317/53).
- [ ] Caminhos absolutos de diretório e arquivo.
- [ ] Comandos copiáveis (e compatíveis com zsh — sem `cmd $VAR` com lista, que não faz word-split).
- [ ] Formatos de arquivo definidos (JSON/JSONL/md com campos nomeados).
- [ ] Limites numéricos: RAM por componente, threads, timeout, tamanho de arquivo, retenção, frequência.
- [ ] Versões pinadas (nada de tag `latest` — a Evolution API já roda `latest` contra a doc, infra l.28).

### Forma do desenho (gate do T-2 que eu confiro de graça)
- [ ] 14 seções com os títulos exatos, **na ordem**.
- [ ] `organograma.json` válido (`python3 -c "import json;json.load(open('…/organograma.json'))"`) e com **10–16 nós**, cada um com id/pai/nome/funcao/tecnologia/roda_em/porque.
- [ ] Organograma do .md e o JSON **batem** (mesmo conteúdo).
- [ ] `## Como escolhi`: 3 candidatos (risco/evidência, entrega/ambientes, operação/custo), tabela de notas 0–10 nos 6 critérios **somada corretamente** (vou recalcular a soma), escolha justificada em 5 linhas, enxertos listados.
- [ ] `## Fluxos`: 3–5 sequências passo a passo concretas.
- [ ] `## Roadmap`: 3–4 fases, cada uma com entregável verificável + **comando** de gate.
- [ ] `## Evidências citadas`: fato → fonte, e as fontes existem de verdade (vou amostrar 3 e conferir).

### (f) Coexistência com os hooks do acervo kb — item extra do maestro (2026-09-04 05:2x)

> **Fato posterior aos dossiês.** Os dossiês descrevem uma máquina com **1 hook** (`confirm-account-before-commit.sh`, só na conta pessoal — memória l.38, l.100). Isso mudou hoje ~05:00. Verifiquei lendo os dois `settings.json` às 05:2x com `python3 -c "json.load(...)"` (só o bloco `hooks` + a lista de chaves; não li valores de `permissions`).

**O que está instalado agora — confere com a descrição do maestro, sem divergência:**

| Evento | `~/.claude` (pessoal) | `~/.claude-empresa` (padrão dos recrutas) |
|---|---|---|
| `UserPromptSubmit` | `kb.py hook-prompt` (timeout 5) | idem |
| `PostToolUse` matcher `Bash` | `kb.py hook-erro` (5) | idem |
| `PostToolUse` matcher `Write\|Edit\|MultiEdit` | `kb.py hook-track` (3) | idem |
| `PostToolUseFailure` | `kb.py hook-erro` (5) | idem |
| `Stop` | `afplay` (10, async) + `kb.py hook-stop` (5) + `kb.py hook-index` (30, async) | `hook-stop` (5) + `hook-index` (30, async) |
| `PreToolUse` matcher `Bash` | `confirm-account-before-commit.sh` | **ausente** |
| `Notification` | `afplay` (10, async) | ausente |

Interpretador: `/opt/homebrew/bin/python3` (caminho absoluto, não depende de PATH).

**Achados verificados (uso como munição):**
1. **A assimetria entre contas NÃO foi fechada.** A empresa continua com 8 chaves e **sem bloco `permissions`** (conferido na lista de chaves): ganhou os 5 hooks do kb, mas segue sem `deny` e sem o guard de conta. A lacuna de memória l.40/l.100 continua de pé — desenho que se apoie em `deny`/hook de conta na conta empresa é REFUTADO.
2. **Arrays somam, e há prova empírica de que `--settings` não apaga os hooks da conta.** O `Stop` da pessoal tem **3 entradas independentes** (afplay, hook-stop, hook-index). E o meu próprio processo (`pid 98767`: `claude --model opus --effort high --permission-mode bypassPermissions --add-dir <frente> --disallowedTools Agent Workflow --strict-mcp-config --settings …/recruit-settings.json --append-system-prompt-file …/guardrails-recruta.md`) roda com um `--settings` **sem bloco `hooks`** e mesmo assim os hooks da conta dispararam nesta sessão (as linhas `KB —` que apareceram depois dos meus Bash). → `--settings` sem `hooks` **não suprime** os hooks da conta.
3. **MAS o caso que interessa continua SEM PROVA:** `recruit-settings-stophook.json` **declara** um `Stop`. Ninguém testou se um `--settings` **com** `hooks` **soma** ao array da conta ou **substitui**. Se o desenho precisar de hook próprio no recruta, tem que dizer qual dos dois é e como testou — senão é SEM PROVA, e vira FAIL se a peça depender disso para funcionar.
4. **Falha aberta: confirmado.** Todos os 5 handlers abrem com `if kbcore.hooks_off(): return` (kb.py l.384/455/487/507/525) e o decorator `kbcore.fail_open` (kbcore.py l.355–362) captura qualquer exceção, grava traceback em `~/kb/.log/erros.log` e faz `sys.exit(0)`. `erros.log` **não existe** → nenhum hook falhou desde a instalação.
5. **Kill switch: confirmado, com uma pegadinha.** `kbcore.hooks_off()` (kbcore.py l.365–366) = `KB_HOOKS=0` **ou** a sentinela `~/kb/.off` (não existe agora → hooks ativos). A env var só vale no processo que a tem: para desligar num recruta seria preciso entrar no `env …` do `--command` do `maestri recruit`. **A sentinela `.off` é a única que desliga tudo de uma vez, inclusive recrutas já vivos.** Desenho que ofereça kill switch só por env var é pior que o que já existe.
6. **Latência.** Medido agora: `python3 -c pass` = 0,03 s; `kb.py hook-prompt` com stdin vazio = 0,07 / 0,07 / 0,10 s → **~40–70 ms de partida por evento**. Bate com a memória `gotcha_hook_latencia_subprocess` (python3 ~70 ms; +sqlite3/unicodedata ~135 ms). Tetos **síncronos** declarados: 5 s (prompt) + 5 s (Bash) + 3 s (edit) + 5 s (failure) + 5 s (stop); só `hook-index` (30 s) é `async`. Pior caso teórico de um turno de recruta com 30 Bash: **5 + 30×5 + 5 = 160 s**. → O desenho precisa de **orçamento de latência por evento** e dizer o que acontece no estouro de timeout.
7. **Custo de TOKENS, não só de tempo.** `hook-prompt` e `hook-erro` **injetam texto no contexto** (`KB — …`). Nesta sessão: 2 linhas injetadas depois de um Bash comum e 3 depois de um Bash com falha. Isso é gasto por evento, em todo recruta, e a régua do T-2 é justamente *baixar* tokens. Desenho que adicione hook injetor **sem teto de linhas e sem dedupe** = FAIL. (O kb já tem dedupe por sessão: `state_save` em `~/kb/.log/state/<session_id>.json`, janela `dedupe_min` do `config.json`.)
8. **Concorrência.** O estado dos hooks é `~/kb/.cache/kb.sqlite` (1,1 MB, com `db.lock` e locks por índice) + `~/kb/.log/state/*.json` (23 arquivos) + `hits.log` (29 KB, **sem rotação**). N recrutas paralelos escrevem no MESMO sqlite. Desenho com fan-out escrevendo no acervo tem que dizer como serializa (o kb usa `fcntl.flock` com `LOCK_NB` e **desiste em silêncio** se não pegar o lock — kb.py l.814–818).
9. **O roteamento por cwd quebra fora de `~` — e esta frente está fora.** `kbcore.layer_for_cwd` (l.471–488) sobe do cwd até `~` procurando `.claude/settings.local.json`; se o cwd não começa com `/Users/gabriel`, o `while` nem executa e a função devolve `None`. O cwd desta frente é `/private/tmp/claude-501/…` → **os hooks não classificam camada para recruta que trabalha fora da home**, que é exatamente o contorno oficial do iCloud (rsync para `/private/tmp`, memória `troubleshoot_icloud_desktop_toolchain`). Peça que more em `/private/tmp` ou dependa de roteamento por cwd = FAIL.
10. **O hook já é ciente do envelope.** `_prompt_util` (kb.py) remove o prefixo `[MAESTRO/…]` antes de buscar e **descarta** prompt que comece com `/` ou tenha menos de 20 caracteres → um ask-back curto (`[T-3] pronto: …`) cai abaixo do corte. Desenho que conte com o hook vendo toda mensagem do canal está errado.
11. **`gerar_indices` reescreve o `MEMORY.md`.** `hook-index` (Stop, async) detecta `.md` mais novo que o sqlite e chama `gerar_indices()`, que **regenera MEMORY.md (curto) + CATALOGO.md** (`cmd_index`, kb.py l.196–203). O cabeçalho atual já é gerado ("índice curto (30 de 39 fatos)"). → **A regra 10 do `guardrails-recruta.md` ("adicione a linha dele no MEMORY.md") virou trabalho descartável hoje** — mesma classe de erro da saga do `preferences.json` (maestri l.62). Se o desenho tocar em memória/índice sem tratar isso, é FAIL; se tratar, é enxerto valioso.
12. **O ambiente está mudando debaixo da auditoria:** `kb.py` passou de 25.224 bytes/576 linhas (05:10) para 38.942 bytes/854 linhas (05:24) e o `MEMORY.md` global saltou de 32 para 39 fatos no mesmo intervalo — outra sessão está construindo o kb agora. Qualquer claim do desenho sobre o acervo tem que ser **datada e re-verificada na hora da auditoria**, não herdada dos dossiês.

**Perguntas que o desenho tem de responder (ausência de qualquer uma = item de FAIL numerado):**
- [ ] Cita os 5 hooks kb existentes e declara que **coexiste** com eles (não assume máquina limpa)?
- [ ] Se instala hook próprio: em qual evento, com que `timeout`, `async` ou não, e **soma ou substitui** — com teste que prove?
- [ ] Orçamento de latência por evento e por turno, e comportamento no estouro do timeout?
- [ ] **Falha aberta** (padrão `fail_open` + `exit 0`) e kill switch pelo menos tão bom quanto `~/kb/.off` (que alcança recruta já vivo)?
- [ ] Teto e dedupe do texto injetado em contexto — quantas linhas/tokens por evento, no pior caso?
- [ ] Concorrência: N recrutas escrevendo no mesmo estado; qual o lock e o que acontece quando não pega?
- [ ] Funciona com cwd fora de `~` (o caso desta frente e o do contorno do iCloud)?
- [ ] Vale nas **duas** contas, sabendo que a empresa não tem `permissions` nem `PreToolUse`?

**Regra de FAIL deste item:** se o `desenho.md` **não mencionar** os hooks do acervo kb, entra como item de FAIL numerado ("assume ambiente anterior a 04/09 05:00"), independentemente do mérito da peça.

---

---

# RODADA 1 — desenho v1 "Tacógrafo" · 2026-09-04 05:5x BRT · **FAIL (5 itens)**

Auditado: `desenho.md` (180 linhas, 14 seções), `organograma.json` (16 nós) e os 4 scripts de medição.
Método: reproduzi as medições em cópia própria (`…/507d1926…/scratchpad/verif/`) para não sobrescrever o `medir_canal.json` do Arquiteto; conferi o binário 2.1.260, o `env` do meu próprio processo de recruta, o servidor por SSH somente-leitura e a documentação oficial de hooks.

**Veredito: FAIL.** Não por arquitetura — a peça é sólida, a forma está completa e quase tudo reproduz. Os 5 itens abaixo são de **calibração e prova**, todos corrigíveis em texto.

## Forma (gate do T-2) — tudo verde
- 14 seções, títulos exatos, na ordem ✓ · `organograma.json` carrega em `json.load` ✓ · 16 nós (limite 10–16) ✓ · ids únicos, 1 nó com `pai:"raiz"`, nenhum pai órfão, nenhum nó sem os 7 campos ✓ · os 16 nomes do `.md` e do `.json` são **idênticos** ✓
- Tabela de notas: 40 / 29 / 54 — somas conferidas uma a uma ✓; "14 pontos sobre (a)" ✓
- Amostrei 3 fontes citadas: `dossie/INDICE.md` diz mesmo **65 lacunas** ✓; `dossie-projetos.md` e `INDICE.md` existem (nasceram 04:57–04:58) ✓; `git -C ~/kb remote -v` vazio ✓

## Tabela das 6 claims

| # | Claim (resumo) | Evidência que produzi | Veredito |
|---|---|---|---|
| C1 | 5 hooks via `--settings` disparam sob bypass; `decision:block` no UserPromptSubmit e `permissionDecision:deny` no PreToolUse bloqueiam | Nomes no binário 2.1.260 reproduzem **exatamente** (SessionStart 61, SessionEnd 29, UserPromptSubmit 42, PreToolUse 88, Stop 446); a frase do contrato (`decision`:"block" válido em UserPromptSubmit, *deprecated* em PreToolUse → `hookSpecificOutput.permissionDecision`) confere; docs oficiais confirmam bloqueio em PreToolUse/UserPromptSubmit/Stop; hooks de conta rodam num recruta sob `--settings` (observei ao vivo na minha sessão). **Mas**: só `Stop` via `--settings` tem teste (T8); SessionStart/SessionEnd/UserPromptSubmit/PreToolUse **declarados no arquivo do `--settings`** nunca foram exercitados | **SEM PROVA** (parcial) → item 3 |
| C2 | `CLAUDE_CODE_SESSION_ID`, `CLAUDE_EFFORT`, `CLAUDE_CONFIG_DIR`, `MAESTRI_TERMINAL_ID` chegam ao recruta; extras via `env X=… claude` também | `env` do meu processo (pid 98767, recruta desta frente): as 4 presentes, mais `CLAUDE_PID`, `CLAUDE_CODE_CHILD_SESSION=1`. A prova do "extra" é o próprio `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`, injetado pelo `env …` do `--command` e visível no ambiente | **SUSTENTADA** |
| C3 | Campos do transcript + dedupe por `message.id` reproduzem o custo sem ccusage; 342 transcripts em < 10 s | Rodei `medir_canal.py`: **344 transcripts em 5,1 s**, 43 maestros, 158 recrutas, 3.327 USD (desenho: 3.319). Campos presentes e coerentes | **SUSTENTADA** (com defeito de método → item 5) |
| C4 | `O_APPEND`, 1 `write` por linha, 10 processos: 20.000 linhas, 0 corrompidas | Rodei `concorrencia.py` em cópia própria: `linhas_validas=20000 corrompidas=0 unicas=20000 tempo=0.26s` | **SUSTENTADA** (ressalva: linhas de 300–1.500 B, não os 4 KB do cap → medir no limite declarado) |
| C5 | Servidor tem git 2.47.3, python3 3.13.5, 163 GB, aceita `git push` a bare repo por SSH sem instalar nada | `ssh servidor`: git **2.47.3** ✓, Python **3.13.5** ✓, 163G ✓, `~/git` inexistente ✓, `PasswordAuthentication no` ✓, `git-receive-pack` em `/usr/bin` ✓; alias `servidor` no `~/.ssh/config` com `Match … nc -z 192.168.24.6` → LAN e fallback `100.67.145.96` + SOCKS ✓ | **SUSTENTADA** (o `push` em si não é testável sem mudar estado; todos os pré-requisitos verificados) |
| C6 | Gasto do maestro concentrado em contexto: 84% dos turnos e 92% dos 3.319 USD acima de 150k; 0,176 vs 0,393 USD/turno; canal = 2,8% dos bytes | `medir_contexto.py` reproduz: 43 sessões, **9.315 turnos**, **3.327 USD**, mediana **312k**, p90 568k, máx 899k, **>150k = 84% / 92%**, **0,176 vs 0,391** USD/turno. Canal: **2,5%** (0,348 MB, 654 chamadas, 532 B/chamada) | **SUSTENTADA nos números medidos**; a extrapolação de 40–50% **não** é medida → item 4 |

## Itens FAIL (numerados)

**1. As medianas de USD/h são por hora de parede (com ocioso) e a Primeira sessão orça com elas — o desenho contradiz o próprio incidente.**
Evidência: `medir_canal.py` divide `usd` por `dur_h = t1 − t0` do transcript. As sessões-maestro têm `dur=34,0 / 43,9 / 95,7 / 98,6 / 100,8 h`; os 158 recrutas somam 1.702 h para 158 sessões (**10,8 h médias**). É tempo de vida da sessão, não de trabalho. Consequência aritmética: pelas medianas do próprio desenho, os 10 terminais de 04/09 (5 Opus xhigh + 4 Sonnet + 1 Haiku) dariam `(5×10,76 + 4×2,06 + 1×0,08)/10 ≈ 6,2 USD/h` por terminal — mas o incidente foi **130 USD / 45 min = 17,3 USD/h por terminal**, ~**2,8× mais**. O desenho usa as duas réguas na mesma seção sem dizer que divergem: "40 USD ≈ 19 h de Sonnet high" e "≈ 19 USD" para 3 recrutas × 3 h (§Primeira sessão) convivem com "a 123 USD/h do incidente, para em 20 min" (§Justificativa).
O que precisa mudar: rotular a métrica ("USD por hora de sessão viva, inclui ocioso"), orçar a Primeira sessão pela taxa ativa (ou em turnos, que é o que o `stop` mede), e recalibrar o `teto_usd` padrão dizendo a qual das duas taxas ele corresponde. Sem isso o freio — o coração da peça — está calibrado numa unidade que não é a do incidente que ele existe para evitar.

**2. O multiplicador que justifica `effort_max: high` não reproduz.**
Evidência: desenho diz "Opus 5 xhigh 17,85 (n=4)" e "o xhigh custa ~2,2× o high no Opus". `medir_effort.py` agora: `opus-5 high n=30 mediana 7,67` · `opus-5 xhigh n=5 mediana 10,76` → **1,40×**. E "Fable 5.1 xhigh 24,45 (n=1)" virou **8,74** (n=1). Os valores mudaram em ~30 minutos porque n≤5 e a duração de parede da mesma sessão cresceu.
O que precisa mudar: derrubar o multiplicador ou recalculá-lo **por turno** (comparando turnos de contexto semelhante), não por sessão. O default `effort_max: high` continua defensável — mas pelo incidente documentado (10 recrutas herdando xhigh), não por uma razão de amostra n=4.

**3. A parte decisiva da C1 não tem prova, e o desenho a testa depois de construir.**
Evidência: dos 5 eventos, só `Stop` via `--settings` foi exercitado (T8/T8i). O `recruit-settings-stophook.json` é o único precedente e ninguém testou um `--settings` **com** `hooks` convivendo com os 5 hooks de conta do `kb.py`. A doc oficial diz que hooks "merge across settings levels rather than replacing each other" e que "all matching hooks run in parallel" — o que **sustenta** a tese do desenho, mas é documentação, não teste nesta máquina, e o `--settings` de CLI não é nomeado na frase.
Por que é bloqueante: se `UserPromptSubmit` declarado no `--settings` não disparar, não existe freio; se **substituir** em vez de somar, o tg cala os 5 hooks do kb (e, na conta pessoal, o `confirm-account-before-commit.sh`) em silêncio.
O que precisa mudar: promover isso a **sonda de 15 minutos ANTES da F1** — um `--settings` com um `Stop` que grava num arquivo próprio + um ask trivial; dois rastros (o do arquivo e o do kb em `~/kb/.log/state/<sid>.json`) = soma; um só = substitui. Só depois escrever `bin/tg`. E citar a doc de hooks na §Justificativa (hoje "comportamento documentado" aparece sem fonte).

**4. A economia de 40–50% é inferência apresentada ao lado de números medidos.**
Evidência: reproduzi que turnos **>100k já são 93% dos turnos e 97% do gasto** — ou seja, passar de 100k é o estado normal de qualquer sessão longa, não um desvio. Manter tudo ≤150k exige compactar muitas vezes, e cada `/compact` paga `cache_creation` a 1,25× o input e acrescenta turnos; o desenho não desconta nada disso. O hedge ("é potencial, não garantia") está lá, mas o número 40–50% aparece na §Justificativa técnica com o mesmo peso visual dos medidos.
O que precisa mudar: ou sai o percentual, ou entra a conta do re-priming (quantos `/compact`, a que custo de cache write) — a régua do Gabriel é número, e este é o único da seção que não é medido.

**5. O dedupe por `message.id` é por arquivo, não global, e os subagentes ficam fora da varredura.**
Evidência: em `medir_canal.py`, `msgs` é um dict **por transcript**; o dossiê de memória (l.57) registra que o ground truth exige **dedupe global** porque streaming e fork/resume repetem `message.id` entre arquivos. Além disso o glob é `<root>/*/*.jsonl`, que não alcança `<projeto>/<sessionId>/subagents/agent-*.jsonl` — e as sessões-maestro usam Agent (0,24 MB de `tool_result` de Agent nelas). Logo 6.810 / 3.327 USD são estimativas com dupla contagem possível para cima e omissão de subagentes para baixo.
O que precisa mudar: `set` global de `message.id` (3 linhas) e incluir `subagents/*.jsonl` no glob — ou declarar as duas omissões junto dos números. Isso importa além do desenho: é o mesmo parser que a F2 usa para o custo do freio, e o gate da F2 exige "divergir < 1%" contra `medir_canal.py`, o que hoje seria comparar um parser com ele mesmo.

## Observações não bloqueantes
- **Eventos que o desenho não usa e resolveriam o que ele critica.** A doc oficial lista `PermissionRequest` (com objeto `decision`), `PreModelSwitch`/`PostModelSwitch`, `SubagentStop`, `TaskCreated`/`TaskCompleted`, `MessageDisplay`. Hoje `tg status --telas` continua fazendo *parsing de tela* do `maestri check` — exatamente a prática que o desenho ataca. `PermissionRequest` transformaria "dialog pendente" em evento do ledger, e `PreModelSwitch`/`PostModelSwitch` dispensariam inferir o modelo pelo turno. Vale 1 parágrafo dizendo por que 5 eventos e não 8.
- **`tg autoteste` no maestro contradiz o §11.** §Primeira sessão põe o brocador rodando `tg autoteste --conta empresa` (pty + `claude` real + comparação de latências) — é o trabalho mecânico mais pesado do desenho no contexto mais caro. §11: "verificação mecânica é execução: dos recrutas por padrão, não do maestro". Passe para um recruta; o maestro recebe PASS/FAIL.
- **Inconsistência interna de número:** §Por que essa forma diz canal = "0,38 MB em 649 chamadas"; §Evidências diz "649 chamadas = 0,35 MB". Reproduzi 0,348 MB / 654 chamadas / 532 B — alinhe os dois e carimbe a hora.
- **C4 no limite declarado:** o teste usou linhas de 300–1.500 B; o cap do desenho é 4 KB. Repita com linhas de 4 KB antes de fixar o cap.
- **Resumo para o chat vende F2 como presente:** "aviso quando o próprio contexto passa de 150k" e "custo da frente a cada turno" são F2 (e o de 150k depende de GO do Gabriel para tocar o `settings.json` da conta). O Gabriel lê só esse bloco — marque a fase.
- **Manutenção não tem número.** O item (c) do meu checklist pede "quem mantém, em minutos/mês". O desenho tem `tg autoteste` a cada upgrade, mas não estima o custo recorrente.
- **A favor do desenho, contra o dossiê:** `claude --help` de hoje mostra `--append-system-prompt[-file]`, `--settings`, `--disallowedTools`, `--effort`, `--strict-mcp-config`. A afirmação do dossiê e do §3 ("não constam do `--help`") está desatualizada — o desenho está certo.
- **Coexistência com o kb (meu item 3(f)): atendida.** O desenho cita os 5 hooks do `kb.py` nas duas contas, com timeouts, kill switch e latências, e decide por dois runners com switches separados. Não entra como FAIL.

---

# RODADA 2 (DELTA, time-boxed) — desenho v2 · 2026-09-04 07:3x BRT · **PASS**

Escopo por ordem do maestro: só (a) os 5 itens de FAIL da rodada 1 e (b) a sonda de coexistência. Não re-auditei forma, claims sustentadas nem números já reproduzidos; nenhuma reprodução de dataset nesta rodada.

| # | Item da rodada 1 | O que a v2 fez | Verifiquei | Estado |
|---|---|---|---|---|
| 1 | USD/h de parede usado para orçar | Métrica renomeada para **hora ATIVA** (soma dos intervalos entre turnos, cada um capado em 300 s) e quantificada: maestros 1.444 h de parede / **143 h ativas** (25,2 USD/h ativa); recrutas 1.699 h / 101 h (23,3). Teto da 1ª sessão 40 → **90 USD**, com regra de bolso (recrutas × horas ativas × USD/h ativa × 1,3) | Li §Justificativa e §Primeira sessão. Fizeram mais do que pedi: um **teste de consistência contra o incidente** — a tabela ativa prevê (5×28,1 + 4×14,1 + 2,6)/10 = **19,9 USD/h por terminal** contra os **17,3** reais de 04/09, e registra que a régua de parede daria 6,2 (o erro de 2,8× que apontei) | **RESOLVIDO** |
| 2 | Multiplicador xhigh/high 2,2× não reproduzia | Multiplicador **derrubado**. Entrou tabela **USD/turno** por modelo×effort e a leitura honesta: nesta amostra o effort não é multiplicador de custo por turno (Opus xhigh 0,124 vs high 0,155, porque rodou com contexto menor); o que xhigh muda é saída por turno (630 vs 399, 1,6×). `effort_max: high` fica como **política** (regra de 04/09 + rastro do `--go`), não como número | §Justificativa, linha da tabela e o parágrafo "Leitura honesta" | **RESOLVIDO** |
| 3 | Só `Stop` via `--settings` tinha teste | **Sonda real às 07:14** (`scratchpad/sonda/`, 0,031 USD) + doc oficial citada com URL | Verifiquei os artefatos, não o relato — ver bloco abaixo | **RESOLVIDO** |
| 4 | 40–50% de economia era inferência | Substituído por **simulação sobre os turnos reais**: −40%, sensibilidade 32–44% | Li `simula(T,P,S)` em `medir2_fio.py`: a cada compactação cobra `S*preço_saída` (resumo) **+** `P*preço_cache_write` (re-priming) e reduz o `cache_read` seguinte pelo offset; varre 5 pares (T,P). É simulação com o custo de re-priming pago, como pedi | **RESOLVIDO** |
| 5 | Dedupe por arquivo; subagentes fora do glob | Parser v2 (`medir2.py`, `medir2_fio.py`) | Conferi no código: `glob(…,'**','*.jsonl',recursive=True)` alcança `subagents/` ✓; `msgs` e `tool_res` são dicts de **módulo** → dedupe global por `message.id` e por `tool_use_id` ✓; separa fio principal × sidechains (44 maestros: 3.339 USD em 9.432 turnos no fio, 280 USD em 3.900 turnos de sidechain) | **RESOLVIDO** |

## (b) Sonda de coexistência `--settings` + hooks da conta — verificada nos artefatos

Não aceitei o relato: li `settings-sonda.json`, `hook.py`, `eventos.jsonl`, `runA.json` e `runB.json`.

- **Merge provado, e é a prova que faltava.** Em `runA.json` (sessão `d555067d`, 3 turnos, 0,031 USD) o modelo devolveu, no MESMO `UserPromptSubmit`, o marcador `SONDA-TG-CTX-7731` (hook declarado no arquivo do `--settings`) **e** duas linhas `KB —` (hooks da conta, `~/.claude-empresa/settings.json`). Hooks de arquivos diferentes **somam**; não substituem. Era o meu item 3 e a suposição mais arriscada da peça.
- **`PreToolUse` deny funciona a partir do `--settings`:** `permission_denials` de `runA.json` traz `{"tool_name":"Bash","tool_input":{"command":"echo SONDA_DENY"}}`, e o modelo reportou `SONDA-TG-DENY-7731`. Um Bash que não casa o padrão (`SONDA_OK`) passou — o hook é seletivo.
- **`UserPromptSubmit` block funciona:** `runB.json` → `"result":"UserPromptSubmit operation blocked by hook:\nSONDA-TG-BLOCK-7731"`, `num_turns: 0`, `total_cost_usd: 0`. É o freio, provado a custo zero de turno.
- **Eventos gravados:** `eventos.jsonl` traz `session_start`, `prompt` e `session_end` da sessão `44ff7b99` (a do block), com `stdin_keys` mostrando `cwd`, `hook_event_name`, `session_id`, `transcript_path`, `source`/`reason`, e o `env` com `CLAUDE_CODE_SESSION_ID`.
- **Ressalva registrada (não bloqueante):** o `stop` **não** aparece nos artefatos — em `runB` o prompt foi bloqueado (não houve turno) e os eventos de `runA` não estão no arquivo. `Stop` via `--settings` segue apoiado no T8/T8i, não nesta sonda. Somando os dois, os 5 eventos estão cobertos, mas o `Stop` é o único que não foi re-provado hoje. A sonda também rodou em `claude -p` (headless), não num terminal recrutado pelo Maestri — o `tg autoteste` da F1 é que fecha o caso interativo.

## Não bloqueantes da rodada 1 — conferidos
- `tg autoteste` saiu do maestro: §Primeira sessão agora dá `selftest` e `autoteste --conta empresa` ao **Executor B**, citando §2/§11 explicitamente. ✓ (Sobrou uma inconsistência: §Integração, "Quem dispara", ainda lista `tg autoteste` entre os comandos do maestro — 1 palavra a corrigir quando alguém encostar no arquivo.)
- C4 refeito no tamanho do cap e além: 4 KB (0,33 s), 8 KB (0,52 s), 16 KB (1,07 s), 64 KB (1,92 s), sempre 20.000 linhas / 0 corrompidas (`concorrencia4k.py`). ✓
- Canal unificado em **0,35 MB / 654 chamadas** nas três ocorrências. ✓
- Resumo para o chat agora marca `(F1)` e `(F2–F3)`. ✓
- Eventos que eu sugeri entraram como opcionais da F2: `PostModelSwitch`, `PreCompact`/`PostCompact`, `PermissionRequest`. ✓
- Doc oficial de hooks citada com URL na §Por que essa forma. ✓

## Forma (re-conferida só porque o arquivo mudou no disco)
`organograma.json` (mtime 07:23) continua válido: 16 nós, ids únicos, raiz `tacografo`, nenhum nó sem os 7 campos, nenhum pai órfão. `desenho.md` mantém as 14 seções.

## Observações que ficam para o dono da peça (não bloqueiam)
1. A simulação do item 4 cobra resumo + re-priming, mas **não** cobra os turnos extras de re-trabalho que uma compactação no meio de uma task costuma gerar. A banda 32–44% é de (T,P), não desse efeito. Vale uma linha.
2. `Stop` não foi re-provado hoje (acima).
3. §Integração ainda lista `tg autoteste` como comando do maestro.
4. O `teto_usd: 40` continua no `orcamento.json` padrão; agora está explicado como "1–2 recrutas", mas quem copiar o JSON sem ler o parágrafo herda o número antigo. Um comentário no arquivo de exemplo resolveria.

**Veredito da rodada 2: PASS.** Os 5 itens de FAIL foram resolvidos com evidência, e a sonda entregou a prova empírica que faltava para o mecanismo central da peça.

## 4. Itens FAIL (numerados) — rodada N
*(rodada 1 acima; rodada 2 fechou todos)*

## 5. Observações não bloqueantes
- Medição própria 2026-09-04 04:55 BRT: servidor online, `up 18:41`, load 1-min **3.55** (4 threads) com 13Gi RAM disponíveis. O load contraria a leitura de "máquina praticamente ociosa" do dossiê (infra l.21, load 0.21/0.32/0.73) — vou remedir antes de aceitar qualquer claim de folga de CPU.
- `maestri list` confirma a topologia da frente: eu (Auditor, role "Auditor de Frente") conectado a **brocador** e **Arquiteto** — o canal auditor↔executor previsto no brief está fiado.
- `dossie/dossie-projetos.md` citado no brief T-2 **ainda não existe** (só infra, maestri e memória). Se o desenho v1 chegar antes dele, claims sobre projetos ficam sem lastro documental.
- **Os dossiês já estão parcialmente vencidos** na parte de hooks/memória: foram extraídos do journal de uma máquina com 1 hook; às 05:24 as duas contas têm 5 hooks do acervo kb e o `kb.py` cresceu 54% em 14 minutos (ver §3(f), item 12). Vou re-verificar na hora qualquer claim sobre `~/kb`, hooks ou índice em vez de citar o dossiê.
- Consequência de protocolo, não de desenho: a **regra 10 do `guardrails-recruta.md`** manda o recruta acrescentar a linha no `MEMORY.md`, mas o `hook-index` regenera esse arquivo no `Stop` (§3(f), item 11). Reporto ao maestro no fim; não é FAIL do Arquiteto.

## 6. Protocolo desta auditoria
- Ao receber `[ARQ/peca-stack/T-2] desenho v1 …`: ack imediato ao Arquiteto ("recebido, auditando"), auditoria assíncrona, retorno por ask. Nunca segurar o ask dele esperando trabalho longo.
- FAIL → `maestri ask "Arquiteto" "[AUD/peca-stack/T-3] FAIL rodada <n>: <k> itens em …/auditoria.md"`.
- PASS → `maestri ask "Arquiteto" "[AUD/peca-stack/T-3] PASS"` e depois `maestri ask "brocador" "[T-3] PASS: <1 linha>"`.
- Só leitura: nada de editar `desenho.md`/`organograma.json`, nada de mudar estado local ou remoto (SSH só com comandos de leitura, sem sudo).
