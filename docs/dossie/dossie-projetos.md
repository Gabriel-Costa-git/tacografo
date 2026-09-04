# PROJETOS — repositórios locais do Gabriel

> Levantamento somente-leitura em 2026-09-04. Fontes: `~/kb/global/project_*.md`, `~/kb/projetos/*/MEMORY.md` (ls), e inspeção direta dos repos (`ls`, `package.json`, `pyproject.toml`, `.github/workflows`, `git log`/`git remote` com timeout, contagem de arquivos de teste). Nenhum valor de token/chave/senha foi copiado — onde um comando devolveu segredo (ex.: `git remote -v` com token embutido na URL), a URL foi redigida.

## Como foi selecionado
- Diretórios varridos: `~/dev`, `~/Developer`, `~/khal`, `~/Desktop` (todos acessíveis, sem EPERM nesta sessão).
- Critério do brief (package.json/composer.json/wp-content) mais duas exceções documentadas: `khal/autoseguro-agent` (Python — `pyproject.toml`/`uv.lock`, equivalente funcional) e `wordpress-cursos` (`.wp-env.json` + `themes/`, wp-content vive dentro do container Docker do wp-env, não no host).
- 11 repos perfilados (dentro do limite de 12), priorizando os projetos ativos listados em `~/kb/global/MEMORY.md`: 123Licitar, Somattos, SEB, AgendaSaaS, painel-medico, WordPress Cursos — mais 5 repos com evidência forte de atividade corrente (commits/memória de 2026-09) não citados no índice global mas com pasta própria em `~/kb/projetos/`: Unifacisa (homolog), sdr (api+painel), sdr-front, leiloes, khal/autoseguro-agent.
- Não perfilados / não localizados (ver `## Não lidos`).

---

## Matriz por projeto

### 1. 123Licitar
- **Caminho:** `/Users/gabriel/dev/123licitar` (⚠️ a memória `project_123licitar.md` registra `~/Desktop/123licitar` — esse caminho **não existe mais**; o repo real está em `~/dev`. Divergência a corrigir na memória.)
- **Stack:** Next.js 15.5.21, React 19.2.3, TypeScript 5, Vitest 4 (`package.json`)
- **Hospedagem/produção hoje:** Vercel (`vercel.json` presente), branch `main`; jobs pesados (`ingest`) via cron no servidor local, alertas leves no Trigger.dev Cloud (per memória `project_123licitar.md` — não re-verificado nesta task)
- **Banco:** Supabase (per memória; não inspecionado — fora de escopo tocar `.env*`)
- **Testes:** Vitest, 26 arquivos `*.test.*`/`*.spec.*` (find, node_modules podado); scripts `test`, `test:watch`, `test:coverage` no `package.json`
- **CI:** `.github/workflows/ci.yml` — `pnpm install --frozen-lockfile` → `pnpm exec tsc --noEmit` → `pnpm test` → `pnpm build` (build usa `secrets.*` do GitHub: Supabase, MercadoPago, Resend, base URL)
- **Hooks/gates do repo:** `.claude/settings.local.json` com `autoMemoryDirectory: ~/kb/projetos/123licitar` e allowlist de 3 comandos; sem `.claude/hooks/`
- **Git:** remote `git@github.com:Gabriel-Costa-git/plataforma.git`; 3 últimos commits são fixes de robustez de jobs (falha silenciosa, cache, detecção de falha lógica) — sessão de correção recente
- **O que é verificado à mão:** deploy (push para `main` dispara build Vercel, sem gate humano descrito na memória); painel MercadoPago (2FA manual); logs de ingest no servidor local

### 2. Somattos (dashboard)
- **Caminho:** `/Users/gabriel/somattos`
- **Stack:** Next.js 16.1.6, React 19.2.3, TypeScript 5, pnpm workspace
- **Hospedagem:** Vercel, `https://somattos.vercel.app` (per memória)
- **Banco:** Supabase (per memória — pooler AWS us-west-2)
- **Testes:** 0 arquivos `*.test.*`/`*.spec.*` encontrados — **sem suíte de testes**
- **CI:** nenhum `.github/workflows`, `Dockerfile` ou `docker-compose*` encontrado — **sem CI**
- **Hooks/gates do repo:** `.claude/settings.local.json` presente; `.env.example` presente; sem hooks
- **Git:** remote `github.com/gabrielcosta-ai/somattos.git` (⚠️ URL capturada por `git remote -v` continha um GitHub token em texto plano na credencial embutida — **redigido**, não reproduzido aqui; recomendação: rotacionar esse token e trocar a URL do remote para SSH ou HTTPS sem credencial embutida). 3 últimos commits: ajustes de UI do dashboard
- **O que é verificado à mão:** tudo — sem lint/test/build gatilhados automaticamente antes do deploy

### 3. SEB — ETL Databricks → Supabase (`databricks-supabase-export`)
- **Caminho:** `/Users/gabriel/databricks-supabase-export`
- **Stack:** Node.js (scripts `.js`/`.py` soltos — `export*.js`, `investigate_*.py`), sem framework; `package.json` só com script `start`
- **Hospedagem/produção hoje:** não é app hospedado — é um conjunto de scripts ETL rodados manualmente; orquestração real é o workflow n8n `db-seb` (per `~/kb/global/project_seb.md`)
- **Banco:** Supabase (`dw_seb` schema) + Databricks (origem)
- **Testes:** 0 arquivos de teste; **não é um repo git** (`git log`/`git remote` retornaram "not a git repository") — sem versionamento
- **CI:** nenhum
- **O que é verificado à mão:** tudo — execução manual dos scripts, sem gate

### 4. AgendaSaaS (`saas-agendamentos`)
- **Caminho:** `/Users/gabriel/saas-agendamentos`
- **Stack:** PHP puro (sem Composer — `agendamentos.php`, `dashboard.php`, `api/`, `includes/`), MySQL
- **Hospedagem:** local, `php -S localhost:8080` (per `~/kb/global/project_agendasaas.md`); sem indício de deploy remoto
- **Banco:** MySQL local (`saas_agendamentos`)
- **Testes:** nenhum manifesto de teste (sem `phpunit.xml`, sem `composer.json`); 0 arquivos `*.test.*`/`*.spec.*`
- **CI:** nenhum; **não é repo git**
- **O que é verificado à mão:** tudo — projeto local sem nenhuma automação de verificação

### 5. painel-medico (AgendAI)
- **Caminho:** `/Users/gabriel/painel-medico`
- **Stack:** Next.js 16.2.1, React 19.2.4, TypeScript 5, Tailwind 4, shadcn/ui, pnpm
- **Hospedagem/produção hoje:** nenhuma — 2 commits locais (`fcb16a4`, `c33b386`), **sem remote configurado** (`git remote -v` vazio); todas as mudanças da sessão de migração ficaram *unstaged* (per memória)
- **Banco:** Supabase Cloud, schema `agent_dr` (⚠️ a memória `project_painel_medico.md` tem a **anon key e o management API token em texto plano** no arquivo — não reproduzidos aqui; recomendação: mover para `.env.local`/secret manager e considerar rotacionar, já que passaram por um arquivo de memória versionado em git)
- **Testes:** 0 arquivos de teste; sem `vitest`/`jest` nas deps
- **CI:** nenhum
- **O que é verificado à mão:** tudo — migração mock→Supabase feita e testada manualmente, sessão interrompida no meio (5 páginas ainda mockadas, per memória)

### 6. WordPress Cursos (LP nova)
- **Caminho:** `/Users/gabriel/wordpress-cursos`
- **Stack:** WordPress local via `@wordpress/env` (Docker), tema custom em `themes/`; `.wp-env.json` mapeia porta 8889
- **Hospedagem/produção hoje:** repo git próprio; deploy real não confirmado nesta varredura (memória cita `wordpress-deploy.zip` e `wp-config-deploy.php` no repo — sugere deploy manual por upload, não automatizado)
- **Banco:** MySQL dentro do container wp-env; há `db-backups/`, `db-deploy.sql`, `db-mock.sql` no repo
- **Testes:** nenhum `phpunit.xml`; 0 arquivos de teste
- **CI:** nenhum `.github/workflows`
- **Git:** remote `github.com/gabrielcosta-ai/wordpress-cursos.git` (⚠️ mesma situação do Somattos — token embutido na URL do `git remote -v`, **redigido**; mesma recomendação de rotação); 2 commits (`d5506fa`, `d5ed868`)
- **O que é verificado à mão:** tudo — sem gate automatizado; ajuste visual pixel-perfect confirmado olho-a-olho contra Figma (per memória)

### 7. Unifacisa (ambiente homolog local)
- **Caminho:** `/Users/gabriel/dev/unifacisa-homolog`
- **Stack:** WordPress + Docker Compose (`docker-compose.yml`), `wp-content/` no host (tema/plugins editáveis diretamente)
- **Hospedagem/produção hoje:** **não é repo git** (`git log`/`git remote` falharam — "not a git repository"); produção real fica fora deste diretório — a memória de projeto (`~/kb/projetos/unifacisa/`) cita deploy via FTPS/lftp para Hostinger (arquivos `deploy-hostinger-*.md`), ou seja, entrega por upload direto, não por push/CI
- **Segredos:** `.env` e `.deploy-credentials.txt` presentes no diretório — **não lidos** (fora de escopo, e o nome do arquivo já indica credencial de deploy em texto plano no disco, risco a registrar na seção de lacunas)
- **Testes:** nenhum `phpunit.xml`/framework de teste
- **CI:** nenhum
- **Hooks/gates:** `.claude/settings.local.json` presente
- **O que é verificado à mão:** tudo — ambiente local espelha produção "a olho" (per memórias `espelho_homolog_local.md`, `drift_local_homolog_2026-06-23.md` no acervo do projeto, não abertas nesta task por não fazerem parte do escopo de MEMORY.md global)

### 8. sdr — api
- **Caminho:** `/Users/gabriel/Developer/sdr/api` (monorepo `sdr`, subpacote)
- **Stack:** Node/TypeScript 5.6.3, `@sdr/api`
- **Hospedagem:** Vercel (`vercel.json`)
- **Testes:** 5 arquivos `*.test.*`/`*.spec.*`
- **Scripts:** `dev`, `dev:trigger`, `typecheck` — **sem script `test` nem `build` no `package.json`** apesar de haver arquivos de teste (rodam por outro caminho, ex. `vitest`/`node --test` direto — não confirmado)
- **CI:** nenhum `.github/workflows` no repo raiz do monorepo
- **Git:** remote `github.com/gabrielcosta-ai/sdr.git` (sem token embutido desta vez); 3 últimos commits são fixes de lógica de agente (WhatsApp, transcrição, PIX)
- **O que é verificado à mão:** typecheck manual (`pnpm typecheck`?), sem gate de CI

### 9. sdr — painel
- **Caminho:** `/Users/gabriel/Developer/sdr/painel` (mesmo repo git do item 8)
- **Stack:** Next.js 16.2.9, React 19.2.4, TypeScript 5
- **Hospedagem:** Vercel (`vercel.json`)
- **Testes:** 0 arquivos de teste
- **Scripts:** `dev`, `build`, `start`, `lint` — sem `test`
- **CI:** nenhum
- **O que é verificado à mão:** tudo (lint manual, sem test)

### 10. sdr-front
- **Caminho:** `/Users/gabriel/Developer/sdr-front` (repo git separado do monorepo `sdr`)
- **Stack:** Next.js 16.2.9, React 19.2.4, TypeScript 5
- **Hospedagem:** Vercel (`vercel.json`)
- **Testes:** 0 arquivos de teste
- **CI:** nenhum
- **Git:** remote `github.com/gabrielcosta-ai/sdr-front.git`; commits recentes de features de integração CRM/HubSpot
- **O que é verificado à mão:** tudo

### 11. leiloes (123arrematar)
- **Caminho:** `/Users/gabriel/Developer/leiloes`
- **Stack:** Next.js 15.5.21, React 19.2.3, TypeScript 5, Vitest 4
- **Hospedagem:** Vercel (`vercel.json`)
- **Testes:** Vitest, 29 arquivos `*.test.*`/`*.spec.*`; scripts `test`, `test:watch`, `test:coverage`
- **CI:** `.github/workflows/ci.yml` — `tsc --noEmit` → `pnpm test` → `pnpm build`, **deliberadamente sem `secrets.*` do GitHub** (comentário no próprio workflow explica: build só precisa de envs com formato válido, nenhum serviço externo é contatado de verdade; decisão tomada após um workflow herdado quebrar por depender de secrets de outro projeto)
- **Git:** remote `git@github.com:Gabriel-Costa-git/123arrematar.git`; commits recentes de features de busca/filtro
- **O que é verificado à mão:** deploy (push→build Vercel sem gate humano descrito)

### 12. khal — autoseguro-agent
- **Caminho:** `/Users/gabriel/khal/autoseguro-agent`
- **Stack:** Python ≥3.12, `pyproject.toml` (uv) — deps: `agno`, `fastapi`, `google-genai`, `sqlalchemy`, `uvicorn`; dev: `pytest`, `pytest-asyncio`, `respx`, `ruff`
- **Hospedagem:** não determinado nesta varredura (agente de desafio FDE Namastex, per `pyproject.toml`); `.venv` local presente
- **Testes:** framework `pytest` configurado (`pyproject.toml`), mas 0 arquivos `*.test.*`/`*.spec.*` encontrados pelo padrão de busca do brief — **suíte real provavelmente usa convenção `test_*.py`/`tests/` (padrão pytest), não capturada pelo filtro `*.test.*`/`*.spec.*` do gate**; há diretório `tests/` no repo (não contado)
- **CI:** nenhum `.github/workflows`
- **Git:** remote `github.com/Gabriel-Costa-git/autoseguro-agent.git`; commits recentes sobre exportador de logs de IA (assinaturas/denylist)
- **O que é verificado à mão:** tudo — `.pytest_cache`/`.ruff_cache` presentes indicam que lint/test rodam localmente, mas não há gate automatizado

---

## Não lidos (repos/caminhos citados na memória, não localizados ou fora de escopo)
- **`~/Desktop/token-dash`** (Token Dash) — diretório **não existe** neste `ls`. A memória do projeto e o journal MAESTRI (dossiê memória, área "Desconhecidos") já registram essa mesma incerteza — pode ter sido movido/renomeado ou a memória sempre teve o caminho errado (aparenta estar em `~/Desktop/figma-tokens-plugin/` junto com dezenas de outros projetos, não confirmado).
- **`~/wordpress-unifacisa`** (site original Unifacisa, porta 8081) — citado em `project_wordpress_cursos.md`, **não encontrado** em nenhum `find` sob `~/`. Pode ter sido consolidado no diretório `~/dev/unifacisa-homolog` atual (item 7) — não confirmado, precisa perguntar ao Gabriel.
- **`~/tw-br-commander`** — existe conforme memória, mas **sem `.git`, sem `package.json`/`composer.json`** (confirmado: userscript único `.user.js`, "sem git, sem CLAUDE.md" já documentado na própria memória do projeto). Fora do critério de perfilamento do brief; não hospeda nada, roda como userscript no navegador — não há "entrega" nem "teste" a levantar.
- **`~/dev/carreira`, `~/dev/arcio`, `~/dev/all`, `~/Developer/marido de aluguel udia`, `~/Desktop/agent-gabriel`, `~/Desktop/arcio`, `~/Desktop/btc`, `~/Desktop/dev-urba`, `~/Desktop/figma-tokens-plugin/*`, `~/Desktop/unifacisa_frontend`** — listados pelo `ls`, não perfilados (excederiam o limite de 12; sem menção nos `MEMORY.md` ativos consultados). `figma-tokens-plugin/` sozinho contém dezenas de subpastas de projeto (`123licitar`, `arcio`, `buscarzap`, `caller*`, `cms-unifacisa`, backups de Supabase) — parece ser uma área de rascunho/backup, não o repo de trabalho.
- **`~/Developer/sdr-wt`, `~/Developer/leiloes-brief`** — existem mas vazios/só documentação (`sdr-wt` é worktree placeholder vazio; `leiloes-brief` é pasta de briefs/arquitetura, não o app).
- **Nenhum acesso negado (EPERM) nesta sessão** — todos os diretórios listados no brief (`~/dev`, `~/Developer`, `~/khal`, `~/Desktop`) responderam normalmente.

---

## Lacunas comuns

- **Verificação:** só 2 dos 12 projetos perfilados têm suíte de testes com massa relevante (123Licitar: 26 arquivos; leiloes: 29 arquivos) e CI que roda `tsc`+`test`+`build` (`.github/workflows/ci.yml` nos dois). Os outros 10 têm zero arquivos de teste no padrão `*.test.*`/`*.spec.*` (khal/autoseguro-agent tem `pytest` configurado mas usa convenção `tests/test_*.py`, não capturada pelo filtro) e nenhum CI. Evidência: contagem `find` + presença/ausência de `.github/workflows` por repo, itens 1–12 acima.
- **Entrega/hosting:** 6 repos em Vercel sem gate humano descrito entre push e deploy em produção (123Licitar, Somattos, sdr-api, sdr-painel, sdr-front, leiloes); 2 sites WordPress sem pipeline — deploy manual por upload/FTPS (WordPress Cursos: `wordpress-deploy.zip` no repo; Unifacisa homolog: nem é repo git, produção via Hostinger/FTPS per memória de projeto); SEB e AgendaSaaS não têm hospedagem alguma, rodam manualmente.
- **Segredos:** 2 ocorrências de token do GitHub embutido em URL de remote (`git remote -v`) capturadas nesta varredura — Somattos e WordPress Cursos, ambas redigidas neste dossiê, recomendação de rotação. `unifacisa-homolog` tem arquivo `.deploy-credentials.txt` no disco (não lido, nome sugere segredo em texto plano). `painel-medico` tem anon key + management API token do Supabase em texto plano dentro de um arquivo de memória versionado em git (`~/kb/global/project_painel_medico.md`) — mesmo não sendo um repo de código, é um vazamento de segredo dentro do próprio acervo de memória.
- **Ambientes:** nenhum dos 12 repos tem `Dockerfile` (só `docker-compose.yml` em Unifacisa homolog, para ambiente local); `.env.example` presente em só 4 dos 12 (123Licitar tem `.env*` mas não `.env.example` no root listado — na verdade tem `.audit`/`.docs` etc., não confirmei `.env.example` isolado; Somattos, sdr-api, leiloes, khal/autoseguro-agent têm `.env.example` confirmado) — a maioria dos projetos não documenta variáveis de ambiente necessárias para outra pessoa (ou outro agente) rodar do zero.
- **Observabilidade/custo:** nenhum dos 12 repos tem indício de monitoramento de erro em produção (Sentry, logging estruturado) nos arquivos de configuração inspecionados; a única observabilidade real identificada em toda a stack é o Netdata do servidor local (fora do escopo desta parte, ver dossiê infra).
- **CI/gates herdados sem cuidado:** o comentário no `ci.yml` do `leiloes` documenta um incidente real — um workflow de CI copiado de outro projeto ("do produto de origem") quebrou por depender de secrets que não existiam no repo novo. Sinal de que copiar configuração entre projetos sem revisar é uma fonte de fricção recorrente nesta stack.
