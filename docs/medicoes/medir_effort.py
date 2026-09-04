#!/usr/bin/env python3
"""Recrutas: USD/h por modelo×effort; maestros: quais arquivos o Read mais trouxe. Só leitura."""
import os, sys, json, re, statistics, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from medir_canal import preco
res=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'medir_canal.json')))
recrutas=[r for r in res if '.maestri/roles' in r['cwd'] and r['n_msgs']>=5]
maestros=[r for r in res if (r['recruit_cmds']>0 or r['canal_calls']>=3) and '.maestri/roles' not in r['cwd']]
por={}  # (modelo,effort) -> [usd/h por sessão]
ctx_rec=[]
for r in recrutas:
    seen={}; efforts={}
    with open(r['path'],'rb') as fh:
        for raw in fh:
            try: d=json.loads(raw)
            except Exception: continue
            if d.get('type')!='assistant': continue
            m=d.get('message') or {}; u=m.get('usage') or {}; mid=m.get('id')
            if not (mid and u and m.get('model') and m.get('model')!='<synthetic>'): continue
            (pi,po,pw,pr),k=preco(m['model'])
            usd=(u.get('input_tokens',0)*pi+u.get('output_tokens',0)*po+u.get('cache_creation_input_tokens',0)*pw+u.get('cache_read_input_tokens',0)*pr)/1e6
            ctx=u.get('input_tokens',0)+u.get('cache_read_input_tokens',0)+u.get('cache_creation_input_tokens',0)
            seen[mid]=(k,d.get('effort') or '?',usd,ctx)
    if r['dur_h']<0.25 or not seen: continue
    for k,e,usd,ctx in seen.values():
        efforts[(k,e)]=efforts.get((k,e),0)+usd; ctx_rec.append(ctx)
    tot=sum(efforts.values())
    if tot<=0: continue
    (k,e)=max(efforts,key=efforts.get)
    por.setdefault((k,e),[]).append(tot/r['dur_h'])
print('RECRUTAS USD/h por modelo×effort (sessões >=0.25h, effort dominante):')
for (k,e),v in sorted(por.items()):
    print(f'  {k:18s} {e:7s} n={len(v):3d} mediana={statistics.median(v):6.2f} media={statistics.mean(v):6.2f} max={max(v):6.2f}')
print(f'contexto por turno dos recrutas: mediana={statistics.median(ctx_rec)/1e3:.0f}k p90={sorted(ctx_rec)[int(0.9*len(ctx_rec))]/1e3:.0f}k max={max(ctx_rec)/1e3:.0f}k turnos={len(ctx_rec)}')
# arquivos mais lidos pelo maestro (Read)
by=({},{})
for r in maestros:
    tool_of={}
    with open(r['path'],'rb') as fh:
        for raw in fh:
            try: d=json.loads(raw)
            except Exception: continue
            t=d.get('type'); m=d.get('message') or {}; c=m.get('content')
            if t=='assistant' and isinstance(c,list):
                for b in c:
                    if isinstance(b,dict) and b.get('type')=='tool_use' and b.get('name')=='Read':
                        tool_of[b['id']]=(b.get('input') or {}).get('file_path','')
            elif t=='user' and isinstance(c,list):
                for b in c:
                    if isinstance(b,dict) and b.get('type')=='tool_result' and b.get('tool_use_id') in tool_of:
                        cc=b.get('content'); n=len(cc.encode()) if isinstance(cc,str) else sum(len((x.get('text') or '').encode()) for x in cc if isinstance(x,dict)) if isinstance(cc,list) else 0
                        fp=tool_of[b['tool_use_id']]
                        ext=os.path.splitext(fp)[1] or '(sem ext)'
                        cat=('scratchpad' if '/scratchpad' in fp or 'claude-501' in fp else 'kb/memoria' if '/kb/' in fp or '/memory/' in fp else '.claude' if '/.claude' in fp else 'repo')
                        by[0][cat]=by[0].get(cat,0)+n; by[1][ext]=by[1].get(ext,0)+n
tot=sum(by[0].values())
print(f'MAESTRO Read total={tot/1e6:.2f}MB por origem:')
for k,v in sorted(by[0].items(),key=lambda x:-x[1]): print(f'  {k:12s} {v/1e6:5.2f} MB {100*v/tot:4.0f}%')
print('  por extensão (top 8):', ', '.join(f'{k}={v/1e6:.2f}MB' for k,v in sorted(by[1].items(),key=lambda x:-x[1])[:8]))
