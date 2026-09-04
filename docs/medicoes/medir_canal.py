#!/usr/bin/env python3
"""Mede, nos transcripts locais do Claude Code (2 contas), o custo do canal Maestri no contexto do maestro
e o custo/hora de recrutas. Só leitura. Dedupe de usage por message.id (regra do Token Dash)."""
import os, sys, json, glob, re, statistics, datetime as dt
ROOTS=['/Users/gabriel/.claude/projects','/Users/gabriel/.claude-empresa/projects']
# USD por 1M tokens: (input, output, cache_write, cache_read) — fonte: skill claude-api (cache 2026-06-24)
PRECOS={
 'claude-fable-5-1':(10,50,12.5,0.25),'claude-fable-5':(10,50,12.5,1.0),'claude-mythos':(10,50,12.5,0.25),
 'claude-opus-5':(5,25,6.25,0.5),'claude-opus-4-8':(5,25,6.25,0.5),'claude-opus-4-7':(5,25,6.25,0.5),'claude-opus-4-6':(5,25,6.25,0.5),
 'claude-opus-4-5':(5,25,6.25,0.5),'claude-opus-4-1':(15,75,18.75,1.5),'claude-opus-4':(15,75,18.75,1.5),
 'claude-sonnet-5':(2,10,2.5,0.2),'claude-sonnet-4-6':(3,15,3.75,0.3),'claude-sonnet-4-5':(3,15,3.75,0.3),'claude-sonnet-4':(3,15,3.75,0.3),
 'claude-haiku-4-5':(1,5,1.25,0.1),'claude-haiku-4':(1,5,1.25,0.1),'claude-3-5-haiku':(0.8,4,1,0.08),
}
def preco(model):
    m=model.replace('[1m]','')
    for k in sorted(PRECOS,key=len,reverse=True):
        if m.startswith(k): return PRECOS[k],k
    return PRECOS['claude-opus-5'],'desconhecido:'+m
CANAL=re.compile(r'^\s*(maestri\s+(check|ask|list|note\s+read))\b')
def analisa(path):
    tool_cmd={}  # tool_use_id -> comando/nome
    canal_bytes=0; canal_calls=0; tr_bytes=0; tr_calls=0
    msgs={}; cwd=None; t0=None; t1=None; sidechain=False
    recruit_cmds=0; askback=0; estado_writes=0
    with open(path,'rb') as fh:
        for raw in fh:
            try: d=json.loads(raw)
            except Exception: continue
            t=d.get('type')
            if t not in ('user','assistant'): continue
            ts=d.get('timestamp')
            if ts:
                t0=t0 or ts; t1=ts
            cwd=cwd or d.get('cwd')
            sidechain=sidechain or bool(d.get('isSidechain'))
            m=d.get('message') or {}
            content=m.get('content')
            if t=='assistant':
                mid=m.get('id'); u=m.get('usage') or {}
                if mid and u and m.get('model') and m.get('model')!='<synthetic>':
                    msgs[mid]=(m.get('model'),u)  # último vence (mesmo usage)
                if isinstance(content,list):
                    for b in content:
                        if isinstance(b,dict) and b.get('type')=='tool_use':
                            inp=b.get('input') or {}
                            cmd=inp.get('command') if b.get('name')=='Bash' else None
                            tool_cmd[b.get('id')]=(b.get('name'),cmd or '',inp.get('file_path',''))
                            if cmd:
                                if 'maestri recruit' in cmd: recruit_cmds+=1
                                if re.search(r'maestri ask\s+"[^"]+"\s+"\[T-',cmd): askback+=1
                            if b.get('name') in ('Write','Edit') and 'estado-' in (inp.get('file_path') or ''): estado_writes+=1
            else:
                if isinstance(content,list):
                    for b in content:
                        if isinstance(b,dict) and b.get('type')=='tool_result':
                            c=b.get('content')
                            if isinstance(c,str): n=len(c.encode())
                            elif isinstance(c,list): n=sum(len((x.get('text') or '').encode()) for x in c if isinstance(x,dict))
                            else: n=0
                            tr_bytes+=n; tr_calls+=1
                            name,cmd,_=tool_cmd.get(b.get('tool_use_id'),('','',''))
                            if name=='Bash' and CANAL.search(cmd):
                                canal_bytes+=n; canal_calls+=1
    # custo
    usd=0; tok_in=tok_out=tok_cr=tok_cw=0; models={}
    for mid,(model,u) in msgs.items():
        (pi,po,pw,pr),k=preco(model)
        i=u.get('input_tokens',0); o=u.get('output_tokens',0); cw=u.get('cache_creation_input_tokens',0); cr=u.get('cache_read_input_tokens',0)
        usd+= (i*pi+o*po+cw*pw+cr*pr)/1e6
        tok_in+=i; tok_out+=o; tok_cr+=cr; tok_cw+=cw
        models[k]=models.get(k,0)+1
    dur_h=0
    if t0 and t1:
        try:
            a=dt.datetime.fromisoformat(t0.replace('Z','+00:00')); b=dt.datetime.fromisoformat(t1.replace('Z','+00:00')); dur_h=(b-a).total_seconds()/3600
        except Exception: pass
    return dict(path=path,cwd=cwd or '',sidechain=sidechain,t0=t0,t1=t1,dur_h=dur_h,n_msgs=len(msgs),usd=usd,
                tok_in=tok_in,tok_out=tok_out,tok_cr=tok_cr,tok_cw=tok_cw,models=models,
                canal_bytes=canal_bytes,canal_calls=canal_calls,tr_bytes=tr_bytes,tr_calls=tr_calls,
                recruit_cmds=recruit_cmds,askback=askback,estado_writes=estado_writes)
files=[]
for r in ROOTS: files+=glob.glob(os.path.join(r,'*','*.jsonl'))
res=[]
for f in files:
    try: res.append(analisa(f))
    except Exception as e: print('ERRO',f,e,file=sys.stderr)
maestros=[r for r in res if (r['recruit_cmds']>0 or r['canal_calls']>=3) and '.maestri/roles' not in r['cwd']]
recrutas=[r for r in res if '.maestri/roles' in r['cwd'] and r['n_msgs']>=5]
print(f'transcripts={len(res)} maestros={len(maestros)} recrutas={len(recrutas)}')
tot_canal=sum(r['canal_bytes'] for r in maestros); tot_tr=sum(r['tr_bytes'] for r in maestros); tot_calls=sum(r['canal_calls'] for r in maestros)
print(f'MAESTROS: canal_bytes={tot_canal} ({tot_canal/1e6:.1f} MB) canal_calls={tot_calls} tool_result_bytes={tot_tr} ({tot_tr/1e6:.1f} MB) canal%={100*tot_canal/max(tot_tr,1):.1f} bytes/call={tot_canal/max(tot_calls,1):.0f}')
print(f'MAESTROS: usd_total={sum(r["usd"] for r in maestros):.2f} estado_writes={sum(r["estado_writes"] for r in maestros)} recruit_cmds={sum(r["recruit_cmds"] for r in maestros)}')
print('Top 8 sessões-maestro por canal_bytes:')
for r in sorted(maestros,key=lambda r:-r['canal_bytes'])[:8]:
    print(f"  {r['t0'][:10] if r['t0'] else '?'} canal={r['canal_bytes']/1e3:.0f}KB calls={r['canal_calls']} tr={r['tr_bytes']/1e3:.0f}KB canal%={100*r['canal_bytes']/max(r['tr_bytes'],1):.0f} usd={r['usd']:.1f} dur={r['dur_h']:.1f}h models={r['models']} {os.path.basename(r['path'])[:8]} {r['cwd'][-40:]}")
print('RECRUTAS por modelo (USD/h nas sessões com >=5 msgs e >=0.25h):')
por={}
for r in recrutas:
    if r['dur_h']<0.25: continue
    k=max(r['models'],key=r['models'].get) if r['models'] else '?'
    por.setdefault(k,[]).append(r['usd']/r['dur_h'])
for k,v in sorted(por.items()):
    print(f'  {k}: n={len(v)} mediana={statistics.median(v):.2f} USD/h media={statistics.mean(v):.2f} max={max(v):.2f}')
print(f'RECRUTAS: usd_total={sum(r["usd"] for r in recrutas):.2f} horas={sum(r["dur_h"] for r in recrutas):.1f} sessoes={len(recrutas)}')
# custo total por conta e por mês (últimos 60 dias)
print('CUSTO por conta (todas as sessões, dedupe por message.id):')
for root in ROOTS:
    s=[r for r in res if r['path'].startswith(root)]
    print(f'  {root}: sessoes={len(s)} usd={sum(r["usd"] for r in s):.2f} out_tok={sum(r["tok_out"] for r in s)/1e6:.1f}M cache_read={sum(r["tok_cr"] for r in s)/1e9:.2f}G')
print('CUSTO 2026-09-04 (hoje) por conta:')
for root in ROOTS:
    s=[r for r in res if r['path'].startswith(root) and (r['t0'] or '').startswith('2026-09-04')]
    print(f'  {root}: sessoes={len(s)} usd={sum(r["usd"] for r in s):.2f}')
json.dump(res,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'medir_canal.json'),'w'),default=str)
