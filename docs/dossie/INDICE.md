# ÍNDICE — lacunas consolidadas dos 4 dossiês

> Base: as seções "## Lacunas" de `dossie-maestri.md` (18 itens), `dossie-infra.md` (25 itens), `dossie-memoria.md` (16 itens) e `dossie-projetos.md` (`## Lacunas comuns`, 6 itens agrupados) — 65 lacunas ao todo, reclassificadas por tema abaixo. A contagem por tema é a soma de itens de lacuna originais que caem nesse tema; a fonte de cada uma é o dossiê onde o item apareceu (não há duplicação entre dossiês — cada lacuna foi contada uma vez, no tema mais específico).

| Tema | Contagem | Fontes (dossiê → nº de itens) |
|---|---|---|
| Infra/resiliência | 15 | dossie-maestri.md (6) · dossie-infra.md (8) · dossie-projetos.md (1) |
| Verificação/CI | 12 | dossie-maestri.md (6) · dossie-infra.md (2) · dossie-memoria.md (2) · dossie-projetos.md (2) |
| Memória/contexto | 12 | dossie-maestri.md (2) · dossie-infra.md (1) · dossie-memoria.md (9) |
| Segredos/backup | 11 | dossie-maestri.md (2) · dossie-infra.md (5) · dossie-memoria.md (3) · dossie-projetos.md (1) |
| Entrega/hosting | 8 | dossie-maestri.md (1) · dossie-infra.md (6) · dossie-projetos.md (1) |
| Observabilidade/custo | 7 | dossie-maestri.md (1) · dossie-infra.md (3) · dossie-memoria.md (2) · dossie-projetos.md (1) |

Total: 65 (12+15+12+11+8+7 = 65).

---

## Infra/resiliência — 15
**Fontes:** dossie-maestri.md (6), dossie-infra.md (8), dossie-projetos.md (1)
- Ambiente de build frágil como causa-raiz recorrente (iCloud pendura tsc/vitest/git; TCC revoga Desktop/Documents/Downloads em sessão; zsh não faz word-split) — dossie-maestri.md
- Effort herdado da conta / `/model`+`/effort` via ask gravam default fora da sessão — dossie-maestri.md (2 itens)
- Sem coordenação entre sessões-maestro no mesmo app (routines.json zerado, edição concorrente) — dossie-maestri.md
- Flush de texto preso é artesanal e arriscado — dossie-maestri.md
- Descoberta de ferramentas: outros presets (Codex/Antigravity/OpenCode) sem guardrails nem deny — dossie-maestri.md
- Servidor local sem alta disponibilidade (sem no-break, sem "Restore on AC Power Loss", sem WoL de S5) e IP ainda dinâmico — dossie-infra.md (2 itens)
- Sem ingress público (cloudflared não instalado) — dossie-infra.md
- Documentação do servidor não versionada (`~/dev/servidor-casa` não é repo git) — dossie-infra.md
- Disco do Mac em 94% (12Gi livres) com 21,5GB de imagens Docker recuperáveis — dossie-infra.md
- Stack Supabase `arcio` sobe 11 containers sem otimização (pressão de RAM no Mac 16GB) — dossie-infra.md
- Material do projeto Oracle sumiu (retomar exige refazer rede e chaves) — dossie-infra.md
- Rate limit do PNCP sem tratamento (429/timeout sistemático no ingest 123Licitar) — dossie-infra.md
- Ambientes de projeto sem `Dockerfile`/`.env.example` na maioria dos 12 repos perfilados — dossie-projetos.md

## Verificação/CI — 12
**Fontes:** dossie-maestri.md (6), dossie-infra.md (2), dossie-memoria.md (2), dossie-projetos.md (2)
- Verificação pós-recrutamento é toda manual (ler tela, trust dialog, checar conta, achar session-id) — dossie-maestri.md
- Sem status estruturado de terminal (parsing de tela para saber se está trabalhando) — dossie-maestri.md
- Reporte e brief são convenção de arquivo, nada valida que foram lidos/escritos — dossie-maestri.md
- Gate verde não prova fiação (função implementada e desligada passou com typecheck+teste verdes) — dossie-maestri.md
- Gate de invariância é script ad hoc reconstruído por frente — dossie-maestri.md
- Manutenção do protocolo Maestri sem teste automatizado (checklist manual T1–T15) — dossie-maestri.md
- CI cobre só 2 de ~15 repos (123licitar e leiloes); os demais sem typecheck/teste/build automatizado — dossie-infra.md
- Drift de runtime em 3 majors (Node 25 Mac / 22 servidor / 20 CI) — dossie-infra.md
- Evidência de verificação é prosa no reporte, não artefato durável — dossie-memoria.md
- Hook `Stop` (único mecanismo de evento por sessão) está ocioso, arquivo não existe — dossie-memoria.md
- 10 dos 12 repos perfilados têm zero arquivos de teste no padrão `*.test.*`/`*.spec.*`, sem CI — dossie-projetos.md
- CI herdado sem revisão quebra por depender de secrets de outro projeto (incidente documentado no `ci.yml` do leiloes) — dossie-projetos.md

## Memória/contexto — 12
**Fontes:** dossie-maestri.md (2), dossie-infra.md (1), dossie-memoria.md (9)
- Estado da orquestração vive num `.md` escrito à mão, não derivado de `maestri list`/`ps`/transcripts — dossie-maestri.md
- Memória de aprendizados mesclada à mão pelo maestro (protocolo não sobrevive sem essa triagem humana) — dossie-maestri.md
- Documentação da infra defasada em pontos que induzem a erro (Tailscale, repos movidos, CLI logado errado) — dossie-infra.md
- Recuperação por relevância não existe no acervo `~/kb` (sem recall nativo, sem busca semântica, sem hook de consulta) — dossie-memoria.md
- Preferências fortes presas em camadas de projeto (31 de 36) — sessão em outro projeto não as vê — dossie-memoria.md
- Higiene do acervo com dívida estável de 138 avisos — dossie-memoria.md
- Cobertura incompleta: hiveos, caller, alliage, carreira, harven, servidor-casa ainda não migrados — dossie-memoria.md
- Teto de índice se aproximando em unifacisa (123 de 200 linhas), sem rotação — dossie-memoria.md
- Memória com fato errado em produção (caminho do Token Dash não existe mais) — dossie-memoria.md
- Sem registro do que cada sessão fez (history.jsonl só guarda o prompt) — dossie-memoria.md
- Reportes de recruta vivem em scratchpad efêmero, nada agrega por frente — dossie-memoria.md
- Sem métrica de uso do próprio acervo (não dá para saber o que virou peso morto) — dossie-memoria.md

## Segredos/backup — 11
**Fontes:** dossie-maestri.md (2), dossie-infra.md (5), dossie-memoria.md (3), dossie-projetos.md (1)
- Canal recruta↔maestro sem autenticação (envelope é convenção textual, injeção de ordem falsa já ocorreu) — dossie-maestri.md
- Higiene de configuração: 44 entradas com segredo removidas do allowlist, mas credenciais ainda NÃO rotacionadas — dossie-maestri.md
- Backup é zero (Postgres Evolution, MySQL WordPress, 100 volumes Docker sem dump nem cron) — dossie-infra.md
- Backup do acervo pessoal pendente (SSD 480GB desconectado, nunca copiado) — dossie-infra.md
- Gestão de segredos artesanal (mesmos valores replicados em 6+ lugares, sem rotação nem auditoria) — dossie-infra.md
- Sem firewall de host (Evolution/WordPress/Netdata expostos a toda a subnet) — dossie-infra.md
- Contas fragmentadas entre serviços (Vercel/GitHub/Trigger.dev em contas diferentes) — dossie-infra.md
- Acervo `~/kb` é git local sem remote — perda de disco leva 235 fatos junto — dossie-memoria.md
- Assimetria de guarda entre contas pessoal/empresa (só a pessoal tem hooks/permissions) — dossie-memoria.md
- Allowlist pessoal com 184 entradas sem deny; credenciais do servidor e do Supabase pendentes de rotação — dossie-memoria.md
- 2 tokens de GitHub embutidos em URL de `git remote -v` (Somattos, WordPress Cursos) + `.deploy-credentials.txt` em texto plano (Unifacisa homolog) + anon/management key do Supabase em texto plano num arquivo de memória (painel-medico) — dossie-projetos.md

## Entrega/hosting — 8
**Fontes:** dossie-maestri.md (1), dossie-infra.md (6), dossie-projetos.md (1)
- Revisão/commit/integração é gargalo de um só nó (só o maestro commita) — dossie-maestri.md
- Sem staging/preview web para o 123Licitar (Hobby estourado, previews sob risco) — dossie-infra.md
- Deploy no servidor é manual e sem procedência (rsync sem pipeline, sem tag de versão) — dossie-infra.md
- Trabalho pronto parado fora de main (5 commits de robustez em branch `audit/2026-08-09`) — dossie-infra.md
- Imagem `latest` da Evolution API em produção, sem caminho de rollback — dossie-infra.md
- Conta `gh` ativa sem escopo `workflow` — dossie-infra.md
- n8n nunca saiu do papel (pendente no servidor, morto na Oracle) — dossie-infra.md
- 6 de 12 repos perfilados fazem deploy Vercel sem gate humano descrito entre push e produção; 2 sites WordPress sem pipeline (upload manual/FTPS) — dossie-projetos.md

## Observabilidade/custo — 7
**Fontes:** dossie-maestri.md (1), dossie-infra.md (3), dossie-memoria.md (2), dossie-projetos.md (1)
- Custo sem freio mecânico (incidente de 130 USD em 45 min só parou porque o Gabriel viu) — dossie-maestri.md
- Alerta de queda de energia não funciona para o cenário mais provável (vigia roda na própria máquina que cai) — dossie-infra.md
- Observabilidade de aplicação inexistente (só Netdata de host; sem APM, sem uptime check) — dossie-infra.md
- Dependência de provedor único para notificação (RESEND_API_KEY sem fallback) — dossie-infra.md
- Nenhum medidor de custo instalado (ccusage fora do PATH, Token Dash fora do ar) — dossie-memoria.md
- Sem custo por frente/sessão/recruta (stats-cache.json congelado, sem USD) — dossie-memoria.md
- Nenhum dos 12 repos perfilados tem indício de monitoramento de erro em produção (Sentry/logging estruturado) — dossie-projetos.md

---

## Leitura rápida
- **Maior tema:** infra/resiliência (15) e verificação/CI e memória/contexto empatados em 12 — a stack tem tanta dívida em "o ambiente aguenta" quanto em "o código está certo" e em "o que já se sabe fica achável".
- **Tema mais concentrado num único dossiê:** memória/contexto (9 de 12 itens vêm só de dossie-memoria.md) e entrega/hosting (6 de 8 vêm só de dossie-infra.md) — sinal de que esses dois temas foram bem cobertos por uma área específica do journal, e o dossiê de projetos (levantado agora, só leitura) contribui pouco a esses dois porque não tem escopo de infra de servidor nem de arquitetura de memória.
- **Segredos/backup (11)** é o único tema com contribuição de todos os 4 dossiês — reforça que é transversal: acervo de memória, protocolo Maestri, servidor e repos de projeto compartilham o mesmo padrão de segredo espalhado sem rotação.
