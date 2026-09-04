#!/usr/bin/env python3
"""Nas sessões-maestro: de onde vêm os bytes de tool_result (por tool e por classe de comando Bash),
distribuição do contexto por turno e USD gasto em turnos acima de 150k tokens. Só leitura."""
import os, sys, json, glob, re, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from medir_canal import preco, ROOTS
res=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'medir_canal.json')))
maestros=[r for r in res if (r['recruit_cmds']>0 or r['canal_calls']>=3) and '.maestri/roles' not in r['cwd']]
paths={r['path'] for r in maestros}
por_tool={}; por_cmd={}; turnos=[]; usd_acima=usd_total=0; n_acima=n_total=0; ctx_max=0
def classe(cmd):
    c=cmd.strip()
    c=re.sub(r'^(cd\s+\S+\s*(&&|;)\s*)+','',c)
    tok=c.split()
    if not tok: return '?'
    if re.match(r'maestri\s+(check|ask|list|note)',c): return 'maestri check/ask/list/note'
    if c.startswith('maestri'): return 'maestri outros'
    if tok[0]=='git': return 'git '+(tok[1] if len(tok)>1 else '')
    if tok[0] in ('cat','sed','head','tail','less'): return 'cat/sed/head/tail'
    if tok[0] in ('python3','python','node','pnpm','npx','npm'): return tok[0]
    if tok[0] in ('ls','find','tree','wc','du'): return 'ls/find/wc'
    if tok[0] in ('grep','rg','ag'): return 'grep'
    if tok[0] in ('curl','ssh','scp','rsync'): return tok[0]
    if tok[0]=='docker': return 'docker'
    return tok[0][:12]
for p in paths:
    tool_of={}
    with open(p,'rb') as fh:
        for raw in fh:
            try: d=json.loads(raw)
            except Exception: continue
            t=d.get('type')
            if t not in ('user','assistant'): continue
            m=d.get('message') or {}; content=m.get('content')
            if t=='assistant':
                u=m.get('usage') or {}; model=m.get('model') or ''
                if u and model and model!='<synthetic>' and m.get('id'):
                    ctx=u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)
                    (pi,po,pw,pr),k=preco(model)
                    usd=(u.get('input_tokens',0)*pi+u.get('output_tokens',0)*po+u.get('cache_creation_input_tokens',0)*pw+u.get('cache_read_input_tokens',0)*pr)/1e6
                    turnos.append((ctx,usd,m.get('id')))
                if isinstance(content,list):
                    for b in content:
                        if isinstance(b,dict) and b.get('type')=='tool_use':
                            inp=b.get('input') or {}
                            tool_of[b.get('id')]=(b.get('name'),inp.get('command') or '',inp.get('file_path') or '')
            else:
                if isinstance(content,list):
                    for b in content:
                        if isinstance(b,dict) and b.get('type')=='tool_result':
                            c=b.get('content')
                            n=len(c.encode()) if isinstance(c,str) else sum(len((x.get('text') or '').encode()) for x in c if isinstance(x,dict)) if isinstance(c,list) else 0
                            name,cmd,fp=tool_of.get(b.get('tool_use_id'),('?','',''))
                            por_tool[name]=por_tool.get(name,0)+n
                            if name=='Bash':
                                k=classe(cmd); por_cmd[k]=por_cmd.get(k,0)+n
                            elif name=='Read':
                                k='Read '+('reporte/brief' if re.search(r'reporte|brief|estado-',fp) else 'outros')
                                por_cmd[k]=por_cmd.get(k,0)+n
# dedupe turnos por message.id
seen={}; 
for ctx,usd,mid in turnos: seen[mid]=(ctx,usd)
turnos=list(seen.values())
tot=sum(v for v in por_tool.values())
print(f'sessoes-maestro={len(paths)} tool_result_total={tot/1e6:.1f}MB')
print('Bytes de tool_result por tool (top):')
for k,v in sorted(por_tool.items(),key=lambda x:-x[1])[:10]: print(f'  {k:14s} {v/1e6:6.2f} MB {100*v/tot:5.1f}%')
print('Bytes por classe de comando Bash / Read (top 18):')
for k,v in sorted(por_cmd.items(),key=lambda x:-x[1])[:18]: print(f'  {k:28s} {v/1e6:6.2f} MB {100*v/tot:5.1f}%')
ctxs=[c for c,_ in turnos]; usds=[u for _,u in turnos]
print(f'turnos={len(turnos)} usd={sum(usds):.0f} ctx_mediana={statistics.median(ctxs)/1e3:.0f}k ctx_media={statistics.mean(ctxs)/1e3:.0f}k ctx_p90={sorted(ctxs)[int(0.9*len(ctxs))]/1e3:.0f}k ctx_max={max(ctxs)/1e3:.0f}k')
for lim in (100e3,150e3,200e3,300e3):
    a=[(c,u) for c,u in turnos if c>lim]
    print(f'  turnos com contexto > {lim/1e3:.0f}k: {len(a)} ({100*len(a)/len(turnos):.0f}% dos turnos) = {sum(u for _,u in a):.0f} USD ({100*sum(u for _,u in a)/sum(usds):.0f}% do gasto do maestro)')
print(f'custo médio por turno: {statistics.mean(usds):.3f} USD; por turno acima de 150k: {statistics.mean([u for c,u in turnos if c>150e3] or [0]):.3f} USD; abaixo de 100k: {statistics.mean([u for c,u in turnos if c<=100e3] or [0]):.3f} USD')
