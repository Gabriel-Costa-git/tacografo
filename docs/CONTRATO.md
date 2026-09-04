# Tacógrafo — CONTRATO de implementação (F1) — 2026-09-04
Fonte de verdade do desenho: `docs/desenho.md` (v2, PASS do Auditor), `docs/organograma.json`, `docs/auditoria.md`. Contrato PROVADO dos hooks: `docs/sonda/` (hook.py, settings-sonda.json, runA/runB, eventos.jsonl). Este arquivo fixa o que cada implementador precisa para trabalhar em paralelo sem colidir. Em conflito entre este arquivo e o desenho, vale este arquivo (é o corte F1).

## Regras gerais
- python3 **stdlib somente** (alvo: 3.13 no Mac via `/opt/homebrew/bin/python3`; código compatível com 3.11+). Sem dependências, sem sqlite, **sem subprocess dentro dos hooks**.
- Cada módulo expõe `main(argv: list[str]) -> int` e é chamado por `bin/tg` (dispatcher). Módulos vivem em `bin/` e se importam pelo nome (`import tg_ledger`); `bin/tg` faz `sys.path.insert(0, dirname(__file__))` uma vez.
- Raiz do Tacógrafo: env `TG_HOME` ou `~/tacografo`. Nunca gravar fora dela.
- **Fail-open nos hooks**: qualquer exceção → nada no stdout, `exit 0`, traceback em `$TG_HOME/.log/erros.log` (cap 1 MB, trunca).
- Kill switch: arquivo `$TG_HOME/.off` ou env `TG_HOOKS=0` → hooks saem com exit 0 sem gravar.
- Testes: `python3 -m unittest discover -s tests -v` verde; testes usam `TG_HOME` apontando para um diretório temporário (nunca o real) e nunca chamam `maestri`/`claude` de verdade (mockar via `TG_MAESTRI_BIN` apontando para um script fake em tests/).
- Segredos: nunca gravar texto de prompt, `tool_input` completo, tokens ou chaves no ledger. Redação: regex `(gho_|ghp_|sk-|eyJ[A-Za-z0-9_-]{20,}\.eyJ|AKIA[0-9A-Z]{12}|sbp_)[A-Za-z0-9._-]*` → `<redigido>`.
- Mensagens e docstrings em pt-BR; nomes de função em pt-BR sem acento (ex.: `ler`, `gravar`, `identidade`).

## Layout
```
bin/tg                 dispatcher (argparse): tg <comando> [args]; comandos F1: hook recrutar status esperar gate freio doctor selftest
bin/tg_ledger.py       append/leitura/offsets/identidade/redação
bin/tg_hook.py         5 eventos: session_start prompt pre_bash stop session_end
bin/tg_freio.py        orçamento, custo.json (flock), FREIO, alerta/freio/duro, comando `tg freio`
bin/tg_status.py       `tg status`, `tg esperar`
bin/tg_gate.py         `tg gate`
bin/tg_recrutar.py     `tg recrutar` (driver do maestri CLI) e `tg doctor`
bin/tg_selftest.py     `tg selftest`
settings/recruta.json  deny (copiar de docs/recruit-settings.atual.json) + 5 hooks
frentes/<frente>/{orcamento.json,custo.json,FREIO,gates/,patches/}
ledger/eventos-AAAA-MM.jsonl · ledger/sessoes.jsonl · ledger/offsets/<sid>.json
tests/test_<modulo>.py · tests/fixtures/
```

## Identidade (env do processo do recruta) — fonte: docs/sonda e docs/dossie/dossie-maestri.md
`CLAUDE_CODE_SESSION_ID` (sid) · `CLAUDE_EFFORT` · `CLAUDE_CONFIG_DIR` (conta: contém `.claude-empresa` → `empresa`; ausente ou `~/.claude` → `pessoal`) · `MAESTRI_TERMINAL_ID` · `TG_FRENTE` · `TG_NOME` · `TG_MODELO` (as três últimas injetadas por `tg recrutar` no `--command` via `env`).

## Evento do ledger (1 linha JSON, < 4 KB, UTF-8, sem `\n` interno)
Campos comuns (sempre presentes; desconhecido = `null`): `ts` (ISO-8601 local com offset), `ev`, `frente`, `nome`, `sid`, `conta`, `modelo`, `effort`, `terminal`, `cwd`.
Tipos e campos específicos:
- `recruit`: `role`, `comando_len` (gravado por `tg recrutar`)
- `session_start`: `transcript`
- `prompt`: `task` ("T-7"|null), `envelope` ("inicio"|"colado"|"ausente"), `tamanho` (chars), `slash` (bool) — **NUNCA o texto do prompt**
- `stop`: `ctx_tokens`, `tokens_in`, `tokens_out`, `cache_read`, `cache_write`, `usd_turno` (null em F1), `usd_sessao` (null em F1), `dur_s`, `transcript_offset`
- `gate`: `task`, `cmd`, `exit`, `dur_s`, `log`, `stat`, `patch`, `commit`, `dirty`, `fora_escopo` ([] em F1)
- `askback`: `task`, `resultado` ("pronto"|"falhou"), `resumo` (≤ 200 chars, redigido)
- `pre_bash_deny`: `motivo`, `task`
- `alerta`: `pct`, `usd`, `teto` · `freio`: `motivo`, `usd`, `teto` · `liberar`/`go`: `texto`, `teto_novo`
- `largada`/`encerrar`: `maestro` · `session_end`: `reason`

## API de `bin/tg_ledger.py` (FIXA — os outros módulos dependem dela)
- `home() -> pathlib.Path` — `TG_HOME` ou `~/tacografo`
- `identidade(env=os.environ) -> dict` — os 8 campos comuns exceto `ts`/`ev`
- `append(ev: dict) -> None` — preenche `ts` (se ausente) e os campos comuns ausentes via `identidade()`; strings > 500 chars truncadas com `…`; `json.dumps(ensure_ascii=False, separators=(",",":"))`; escreve com `os.open(O_WRONLY|O_APPEND|O_CREAT, 0o644)` + **um único** `os.write` em `ledger/eventos-AAAA-MM.jsonl` (cria diretórios)
- `ler(mes: str|None = None, **filtros) -> Iterator[dict]` — `mes` "AAAA-MM" (default mês atual); filtros por igualdade (`ev="stop", frente="x"`); linhas inválidas ignoradas
- `ultimo(**filtros) -> dict|None`
- `caminho_mes(mes=None) -> pathlib.Path`
- `offset_ler(sid) -> {"offset": int, "ids": list[str]}` · `offset_gravar(sid, offset, ids)` (≤ 50 ids)
- `redigir(texto: str) -> str`
- `agora() -> str` (ISO-8601 local com offset)

## Hooks (Claude Code 2.1.260; contrato provado em `docs/sonda`)
Chamada: `/opt/homebrew/bin/python3 /Users/gabriel/tacografo/bin/tg hook <evento>` com JSON no stdin: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `prompt` (UserPromptSubmit), `tool_name` + `tool_input.command` (PreToolUse Bash), `stop_hook_active` (Stop), `reason` (SessionEnd).
Mapeamento `settings/recruta.json`: SessionStart→`session_start` · UserPromptSubmit→`prompt` · PreToolUse (matcher `Bash`)→`pre_bash` · Stop→`stop` · SessionEnd→`session_end`; timeout 5 (Stop 10). Formato do bloco `hooks` = igual ao de `docs/sonda/settings-sonda.json`.
Saídas:
- `prompt`: extrai task do envelope `[MAESTRO/<frente>/T-n]` (regex `\[MAESTRO/([^/\]]+)/(T-\d+[a-z]?)\]`); `envelope`: "inicio" (posição 0), "colado" (existe mas não na posição 0), "ausente"; `slash` = prompt começa com "/". Se `frentes/<frente>/FREIO` existe **e** `slash` é falso → stdout `{"decision":"block","reason":"FREIO <frente>: <motivo> — aguarde o maestro (tg freio <frente> --liberar --go \"<texto>\")"}` e exit 0 (grava evento `prompt` com `bloqueado: true`). Sem FREIO → grava e sem stdout.
- `pre_bash`: se `tool_input.command` casa `maestri ask` com `[T-n] pronto|falhou` e NÃO existe evento `gate` com `exit == 0` para essa task+frente → stdout `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"tg: T-n sem gate verde — rode tg gate T-n -- <cmd>"}}` exit 0 e grava `pre_bash_deny`. Se `custo.json` ≥ `freio_duro_pct` do teto → deny de todo Bash com motivo. Caso contrário sem stdout; se o ask de `pronto|falhou` passa, grava `askback`.
- `stop`: lê `transcript_path` a partir do offset salvo; para cada linha `type == "assistant"` com `message.id` novo (dedupe pelos últimos 50 ids): soma `message.usage.input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`; `ctx_tokens` = input + cache_read + cache_creation da ÚLTIMA mensagem assistant; `dur_s` = diferença entre o primeiro e o último `timestamp` novos; grava `stop` e `offset_gravar`; atualiza `frentes/<frente>/custo.json` com `fcntl.flock` (F1: tokens; `usd` null); se `orcamento.json` tem `teto_tokens` não nulo: ≥ `alerta_pct`% → evento `alerta`; ≥ 100% → cria `FREIO` + evento `freio`. Estrutura das linhas do transcript: ver `docs/transcript-amostra-estrutura.jsonl`.
- `session_start`/`session_end`: gravam e saem.
Latência alvo ≤ 60 ms por evento (`time echo '{}' | python3 bin/tg hook session_end`).

## `orcamento.json` (frentes/<f>/) — default criado por `tg recrutar`/`tg freio`
`{"teto_usd":40,"alerta_pct":70,"teto_recrutas":4,"effort_max":"high","cota_5h_freio_pct":90,"freio_duro_pct":120,"teto_tokens":null}`
`custo.json`: `{"usd":null,"tokens":int,"por_sessao":{sid:{"tokens":int,"turnos":int,"ultimo":ts}},"atualizado":ts}`. `FREIO`: texto `"<motivo> | <ts>"`.
`tg freio <f> [--liberar] [--teto N] [--go "texto"] [--motivo "texto"]`: sem flags cria FREIO (motivo obrigatório) + evento `freio`; `--liberar` remove FREIO + evento `liberar`; `--teto N` altera `teto_usd` (+ evento `go` se `--go`). Ordem de effort: low < medium < high < xhigh < max.

## `tg recrutar` (driver) — F1
`tg recrutar <Nome> --role "<Role>" --modelo <m> --effort <e> --frente <f> [--repo <dir>] [--go "<texto>"] [--mcp] [--dry-run]`
1. Carrega `orcamento.json` da frente (cria default). Recrutas vivos da frente = eventos `session_start` sem `session_end` correspondente (por sid); vivos ≥ `teto_recrutas` ou effort > `effort_max` → recusa (exit 4) sem `--go`.
2. Monta: `maestri recruit "<Nome>" --preset "Claude Code" --role "<Role>" --dir <repo|$TG_HOME/frentes/<f>> --command "env CLAUDE_CONFIG_DIR=/Users/gabriel/.claude-empresa CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 TG_FRENTE=<f> TG_NOME=<Nome> TG_MODELO=<m> claude --model <m> --effort <e> --permission-mode bypassPermissions --add-dir <repo> --disallowedTools Agent Workflow --strict-mcp-config --settings /Users/gabriel/tacografo/settings/recruta.json --append-system-prompt-file /Users/gabriel/.claude/maestri/templates/guardrails-recruta.md"` (`--mcp` omite `--strict-mcp-config`; `--dry-run` imprime o comando e sai 0). Binário do maestri: env `TG_MAESTRI_BIN` ou `maestri` no PATH.
3. Executa (subprocess); espera 5 s; `maestri check <Nome>`; se a tela contém `Yes, I trust` → `maestri ask <Nome> --raw "\e[B"` e depois `--raw "\n"`.
4. Espera evento `session_start` com `nome == <Nome>` (≤ 30 s, poll 1 s no ledger); grava evento `recruit`; imprime 1 linha `<Nome> <m>/<e> <conta> sid=<sid> cwd=<cwd>`; exit 0. Timeout → imprime o que tem e exit 2.
`tg doctor`: TG_HOME, versão do python, `settings/recruta.json` válido com 5 hooks, ledger gravável, últimos 5 eventos, `.off`, disco livre; exit 0/1.

## `tg status` / `tg esperar`
`tg status <frente> [--nota] [--historico HH:MM-HH:MM]` → texto ≤ 1,2 KB: 1 linha por recruta (`nome modelo/effort conta · ocupado|ocioso desde HH:MM · task atual · gate T-n exit=0 · askback T-n pronto · tokens`) + linha de totais (`tokens/usd vs teto · FREIO? · vivos/teto_recrutas`). Ocupado = último evento da sessão é `prompt` sem `stop` posterior. `--nota` também grava `maestri note write status-<frente> "<texto>"` (subprocess permitido: não é hook).
`tg esperar <frente> [--nome N] [--evento askback|stop|gate|freio|alerta] [--timeout 1800]` → `os.stat` do arquivo do mês a cada 2 s; ao chegar evento novo que casa, imprime a linha compacta (`HH:MM ev nome task resultado`) e sai 0; timeout → exit 3.

## `tg gate`
`tg gate <T-n> -- <comando...>` ou `tg gate <T-n> --manual "<motivo>"` → roda o comando (subprocess; `shell=True` só se houver 1 argumento), captura stdout+stderr em `frentes/<f>/gates/<T-n>-<HHMM>.log` (cap 200 KB, redigido), mede duração; `git diff --stat` e patch em `frentes/<f>/patches/<T-n>-<HHMM>.patch` (cap 1 MB, excluindo `.env*`), `git rev-parse --short HEAD`, `dirty` = `git status --porcelain` não vazio (se não for repo git: campos null). Grava evento `gate`. Exit = exit do comando (`--manual` = 0). Imprime 1 linha.

## `tg selftest`
1) parser de transcript com `tests/fixtures/transcript-amostra.jsonl` (3 turnos, 1 id repetido → dedupe; totais esperados fixados no teste); 2) concorrência: 10 processos × 2000 linhas (300–4000 B) via `multiprocessing` → 20000 linhas válidas, 0 corrompidas; 3) block: FREIO presente + stdin sintético de `prompt` → saída de block; 4) deny: `pre_bash` com `maestri ask "brocador" "[T-9] pronto"` sem gate → deny; com evento gate exit 0 → sem saída; 5) latência de `hook session_end` ≤ 100 ms (mediana de 3). Exit 0 se tudo verde; imprime 1 linha por item.

## Divisão de trabalho (ramos git; cada um só toca os próprios arquivos)
- `f1/core`: `bin/tg_ledger.py`, `bin/tg_hook.py`, `settings/recruta.json`, `tests/test_ledger.py`, `tests/test_hook.py`, `tests/fixtures/transcript-amostra.jsonl`
- `f1/freio-status`: `bin/tg_freio.py`, `bin/tg_status.py`, `tests/test_freio.py`, `tests/test_status.py`
- `f1/gate-recrutar`: `bin/tg`, `bin/tg_gate.py`, `bin/tg_recrutar.py`, `bin/tg_selftest.py`, `tests/test_gate.py`, `tests/test_recrutar.py`, `tests/fake_maestri.py`
Quem precisa de módulo de outro ramo ainda inexistente escreve um stub mínimo **em tests/** (nunca em `bin/`), seguindo a API deste contrato.
