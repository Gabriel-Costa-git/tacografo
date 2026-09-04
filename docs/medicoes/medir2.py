#!/usr/bin/env python3
"""v2 (auditoria rodada 1): glob recursivo (inclui subagents/**), dedupe GLOBAL por message.id e por tool_use_id,
hora ATIVA (gaps entre turnos capados em 300 s), USD/turno por modelo×effort, composição do gasto do maestro
e simulação de compactação com re-priming. Só leitura."""
import os, sys, json, glob, re, statistics, datetime as dt
ROOTS=['/Users/gabriel/.claude/projects','/Users/gabriel/.claude-empresa/projects']
PRECOS={
 'claude-fable-5-1':(10,50,12.5,0.25),'claude-fable-5':(10,50,12.5,1.0),'claude-mythos':(10,50,12.5,0.25),
 'claude-opus-5':(5,25,6.25,0.5),'claude-opus-4-8':(5,25,6.25,0.5),'claude-opus-4-7':(5,25,6.25,0.5),'claude-opus-4-6':(5,25,6.25,0.5),
 'claude-opus-4-5':(5,25,6.25,0.5),'claude-opus-4-1':(15,75,18.75,1.5),'claude-opus-4':(15,75,18.75,1.5),
 'claude-sonnet-5':(2,10,2.5,0.2),'claude-sonnet-4-6':(3,15,3.75,0.3),'claude-sonnet-4-5':(3,15,3.75,0.3),'claude-sonnet-4':(3,15,3.75,0.3),
 'claude-haiku-4-5':(1,5,1.25,0.1),'claude-haiku-4':(1,5,1.25,0.1),'claude-3-5-haiku':(0.8,4,1,0.08),
}
def preco(model):
    m=(model or '').replace('[1m]','')
    for k in sorted(PRECOS,key=len,reverse=True):
        if m.startswith(k): return PRECOS[k],k
    return PRECOS['claude-opus-5'],'desconhecido:'+m
CANAL=re.compile(r'^\s*(cd\s+\S+\s*(&&|;)\s*)*maestri\s+(check|ask|list|note)\b')
def ts(s):
    try: return dt.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
    except Exception: return None
files=[]
for r in ROOTS: files+=glob.glob(os.path.join(r,'**','*.jsonl'),recursive=True)
msgs={}      # message.id -> dict(sid, model, effort, usage, t, root)
tool_use={}  # tool_use_id -> (sid, name, cmd, fp)
tool_res={}  # tool_use_id -> bytes (dedupe global)
sess={}      # sid -> dict(cwd, root, files, recruit_cmds, estado_writes, sidechain)
for f in files:
    root=ROOTS[0] if f.startswith(ROOTS[0]) else ROOTS[1]
    with open(f,'rb') as fh:
        for raw in fh:
            try: d=json.loads(raw)
            except Exception: continue
            t=d.get('type')
            if t not in ('user','assistant'): continue
            sid=d.get('sessionId') or os.path.basename(f).split('.')[0]
            s=sess.setdefault(sid,dict(cwd=None,root=root,files=set(),recruit_cmds=0,estado_writes=0,sidechain=False))
            s['files'].add(f); s['cwd']=s['cwd'] or d.get('cwd'); s['sidechain']=s['sidechain'] or bool(d.get('isSidechain'))
            m=d.get('message') or {}; c=m.get('content')
            if t=='assistant':
                mid=m.get('id'); u=m.get('usage') or {}
                if mid and u and m.get('model') and m.get('model')!='<synthetic>' and mid not in msgs:
                    msgs[mid]=dict(sid=sid,model=m['model'],effort=d.get('effort') or '?',u=u,t=ts(d.get('timestamp') or ''),root=root)
                if isinstance(c,list):
                    for b in c:
                        if isinstance(b,dict) and b.get('type')=='tool_use' and b.get('id') not in tool_use:
                            inp=b.get('input') or {}; cmd=inp.get('command') if b.get('name')=='Bash' else ''
                            tool_use[b['id']]=(sid,b.get('name'),cmd or '',inp.get('file_path') or '')
                            if cmd and 'maestri recruit' in cmd: s['recruit_cmds']+=1
                            if b.get('name') in ('Write','Edit') and 'estado-' in (inp.get('file_path') or ''): s['estado_writes']+=1
            else:
                if isinstance(c,list):
                    for b in c:
                        if isinstance(b,dict) and b.get('type')=='tool_result' and b.get('tool_use_id') not in tool_res:
                            cc=b.get('content')
                            n=len(cc.encode()) if isinstance(cc,str) else sum(len((x.get('text') or '').encode()) for x in cc if isinstance(x,dict)) if isinstance(cc,list) else 0
                            tool_res[b['tool_use_id']]=n
# custo por mensagem
def custo(m):
    (pi,po,pw,pr),k=preco(m['model']); u=m['u']
    i=u.get('input_tokens',0); o=u.get('output_tokens',0); cw=u.get('cache_creation_input_tokens',0); cr=u.get('cache_read_input_tokens',0)
    return dict(usd=(i*pi+o*po+cw*pw+cr*pr)/1e6, usd_in=i*pi/1e6, usd_out=o*po/1e6, usd_cw=cw*pw/1e6, usd_cr=cr*pr/1e6, ctx=i+cw+cr, out=o, cw=cw, cr=cr, i=i, k=k)
por_sess={}
for mid,m in msgs.items():
    c=custo(m); r=por_sess.setdefault(m['sid'],dict(turnos=[],usd=0))
    r['usd']+=c['usd']; r['turnos'].append((m['t'] or 0, c, m['model'], m['effort']))
for sid,r in por_sess.items():
    r['turnos'].sort(key=lambda x:x[0])
    tt=[x[0] for x in r['turnos'] if x[0]]
    r['t0']=tt[0] if tt else None; r['t1']=tt[-1] if tt else None
    r['parede_h']=((tt[-1]-tt[0])/3600) if len(tt)>1 else 0
    r['ativa_h']=sum(min(b-a,300) for a,b in zip(tt,tt[1:]))/3600 if len(tt)>1 else 0
    mods={}
    for _,c,model,eff in r['turnos']: mods[(c['k'],eff)]=mods.get((c['k'],eff),0)+c['usd']
    r['dominante']=max(mods,key=mods.get) if mods else ('?','?')
# canal e classificação
canal_b={}; canal_n={}; tr_b={}
for tid,n in tool_res.items():
    if tid not in tool_use: continue
    sid,name,cmd,fp=tool_use[tid]
    tr_b[sid]=tr_b.get(sid,0)+n
    if name=='Bash' and CANAL.search(cmd): canal_b[sid]=canal_b.get(sid,0)+n; canal_n[sid]=canal_n.get(sid,0)+1
maestros=[sid for sid,s in sess.items() if sid in por_sess and (s['recruit_cmds']>0 or canal_n.get(sid,0)>=3) and '.maestri/roles' not in (s['cwd'] or '')]
recrutas=[sid for sid,s in sess.items() if sid in por_sess and '.maestri/roles' in (s['cwd'] or '') and len(por_sess[sid]['turnos'])>=5]
print(f'arquivos={len(files)} sessoes={len(por_sess)} mensagens_unicas={len(msgs)} maestros={len(maestros)} recrutas={len(recrutas)}')
tot=sum(r['usd'] for r in por_sess.values())
for root in ROOTS:
    s=[sid for sid in por_sess if sess[sid]['root']==root]
    print(f'  conta {root.split("/")[-2]}: sessoes={len(s)} usd={sum(por_sess[x]["usd"] for x in s):.0f}')
print(f'TOTAL usd={tot:.0f}')
M=[por_sess[s] for s in maestros]
usd_m=sum(r['usd'] for r in M); turnos_m=[c for r in M for _,c,_,_ in r['turnos']]
print(f'MAESTROS usd={usd_m:.0f} turnos={len(turnos_m)} parede_h={sum(r["parede_h"] for r in M):.0f} ativa_h={sum(r["ativa_h"] for r in M):.0f} usd/h_ativa={usd_m/max(sum(r["ativa_h"] for r in M),1e-9):.2f}')
comp={k:sum(c[k] for c in turnos_m) for k in ('usd_in','usd_out','usd_cw','usd_cr')}
print('  composição do gasto do maestro: '+', '.join(f'{k}={v:.0f} ({100*v/usd_m:.0f}%)' for k,v in comp.items()))
ctxs=sorted(c['ctx'] for c in turnos_m)
print(f'  ctx mediana={statistics.median(ctxs)/1e3:.0f}k p90={ctxs[int(0.9*len(ctxs))]/1e3:.0f}k max={max(ctxs)/1e3:.0f}k')
for lim in (100e3,150e3,200e3,300e3):
    a=[c for c in turnos_m if c['ctx']>lim]; print(f'  >{lim/1e3:.0f}k: {len(a)} turnos ({100*len(a)/len(turnos_m):.0f}%) = {sum(c["usd"] for c in a):.0f} USD ({100*sum(c["usd"] for c in a)/usd_m:.0f}%)')
print(f'  usd/turno: <=100k {statistics.mean([c["usd"] for c in turnos_m if c["ctx"]<=100e3] or [0]):.3f} | >150k {statistics.mean([c["usd"] for c in turnos_m if c["ctx"]>150e3] or [0]):.3f} | geral {statistics.mean([c["usd"] for c in turnos_m]):.3f}')
print(f'  canal maestri: {sum(canal_b.get(s,0) for s in maestros)/1e6:.3f} MB em {sum(canal_n.get(s,0) for s in maestros)} chamadas; tool_result total {sum(tr_b.get(s,0) for s in maestros)/1e6:.2f} MB; estado_writes={sum(sess[s]["estado_writes"] for s in maestros)}; recruit_cmds={sum(sess[s]["recruit_cmds"] for s in maestros)}')
# recrutas: por modelo×effort — USD/h ativa, USD/turno, ctx mediana
R=[por_sess[s] for s in recrutas]
print(f'RECRUTAS usd={sum(r["usd"] for r in R):.0f} sessoes={len(R)} parede_h={sum(r["parede_h"] for r in R):.0f} ativa_h={sum(r["ativa_h"] for r in R):.0f} usd/h_ativa={sum(r["usd"] for r in R)/max(sum(r["ativa_h"] for r in R),1e-9):.2f}')
por={}
for r in R:
    for t,c,model,eff in r['turnos']:
        por.setdefault((c['k'],eff),[]).append(c)
por_h={}
for r in R:
    if r['ativa_h']>=0.1: por_h.setdefault(r['dominante'],[]).append((r['usd']/r['ativa_h'], r['usd']/max(r['parede_h'],1e-9)))
print('  modelo×effort: n_turnos | USD/turno mediana | out tok/turno mediana | ctx mediana | USD/h ATIVA mediana (n sessões) | USD/h parede mediana')
for k in sorted(por, key=lambda k:-len(por[k])):
    v=por[k]
    if len(v)<20: continue
    h=por_h.get(k,[])
    print(f'  {k[0]:18s} {k[1]:7s} n={len(v):5d} | {statistics.median([c["usd"] for c in v]):.3f} | {statistics.median([c["out"] for c in v]):.0f} | {statistics.median([c["ctx"] for c in v])/1e3:.0f}k | {statistics.median([a for a,_ in h]) if h else float("nan"):.2f} (n={len(h)}) | {statistics.median([b for _,b in h]) if h else float("nan"):.2f}')
# incidente 04/09 (LeilõesBR): sessões de recruta iniciadas em 2026-09-04 entre 00:00 e 04:00 UTC-3? -> usar todas de hoje com cwd leiloes
# simulação de compactação nos maestros
def simula(T,P,S=4000):
    real=0; sim=0; comps=0
    for r in M:
        off=0
        for _,c,model,eff in r['turnos']:
            (pi,po,pw,pr),k=preco(model)
            real+=c['usd']
            cr=max(0,c['cr']-off); ctx=c['i']+c['cw']+cr
            sim+=(c['i']*pi+c['out']*po+c['cw']*pw+cr*pr)/1e6
            if ctx>T:
                comps+=1; sim+=(S*po+P*pw)/1e6; off=c['cr']+c['cw']+c['i']-P
                if off<0: off=0
    return real,sim,comps
print('SIMULAÇÃO de compactação nos maestros (mesmos turnos; a cada turno acima de T, compacta para P pagando resumo de 4k tokens de saída + re-priming de P a preço de cache write):')
for T in (150e3,200e3,300e3):
    for P in (40e3,60e3,80e3):
        real,sim,comps=simula(T,P)
        print(f'  T={T/1e3:.0f}k P={P/1e3:.0f}k: real={real:.0f} sim={sim:.0f} economia={100*(1-sim/real):.0f}% compactacoes={comps} (1 a cada {len(turnos_m)/max(comps,1):.0f} turnos)')
json.dump({'maestros':maestros,'recrutas':recrutas,'por_sess':{s:{k:v for k,v in r.items() if k!='turnos'} for s,r in por_sess.items()}},open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'medir2.json'),'w'),default=str)
