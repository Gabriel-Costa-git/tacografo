#!/usr/bin/env python3
"""Complemento ao medir2.py: separa fio principal (isSidechain=false) de sidechains nas sessões-maestro
e roda a simulação de compactação só no fio principal. Só leitura. Uso: python3 medir2_fio.py"""
import os, json, glob, statistics, re
src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'medir2.py')).read().split("# custo por mensagem")[0]
exec(src.replace("msgs[mid]=dict(","msgs[mid]=dict(side=bool(d.get('isSidechain')),"))
def custo(m):
    (pi,po,pw,pr),k=preco(m['model']); u=m['u']
    i=u.get('input_tokens',0); o=u.get('output_tokens',0); cw=u.get('cache_creation_input_tokens',0); cr=u.get('cache_read_input_tokens',0)
    return dict(usd=(i*pi+o*po+cw*pw+cr*pr)/1e6, ctx=i+cw+cr, out=o, cw=cw, cr=cr, i=i, k=k, side=m['side'], model=m['model'], t=m['t'] or 0)
por_sess={}
for mid,m in msgs.items(): por_sess.setdefault(m['sid'],[]).append(custo(m))
canal_n={}
for tid,n in tool_res.items():
    if tid in tool_use:
        sid,name,cmd,fp=tool_use[tid]
        if name=='Bash' and CANAL.search(cmd): canal_n[sid]=canal_n.get(sid,0)+1
maestros=[sid for sid,s in sess.items() if sid in por_sess and (s['recruit_cmds']>0 or canal_n.get(sid,0)>=3) and '.maestri/roles' not in (s['cwd'] or '')]
main=[c for s in maestros for c in por_sess[s] if not c['side']]; side=[c for s in maestros for c in por_sess[s] if c['side']]
um=sum(c['usd'] for c in main); us=sum(c['usd'] for c in side)
print(f'MAESTROS fio principal: turnos={len(main)} usd={um:.0f} | sidechains: turnos={len(side)} usd={us:.0f} ({100*us/(um+us):.0f}%)')
ctxs=sorted(c['ctx'] for c in main)
print(f'  ctx mediana={statistics.median(ctxs)/1e3:.0f}k p90={ctxs[int(0.9*len(ctxs))]/1e3:.0f}k max={max(ctxs)/1e3:.0f}k')
for lim in (100e3,150e3,200e3,300e3):
    a=[c for c in main if c['ctx']>lim]; print(f'  >{lim/1e3:.0f}k: {len(a)} ({100*len(a)/len(main):.0f}%) = {sum(c["usd"] for c in a):.0f} USD ({100*sum(c["usd"] for c in a)/um:.0f}%)')
print(f'  usd/turno: <=100k {statistics.mean([c["usd"] for c in main if c["ctx"]<=100e3]):.3f} | >150k {statistics.mean([c["usd"] for c in main if c["ctx"]>150e3]):.3f} | geral {statistics.mean([c["usd"] for c in main]):.3f}')
def simula(T,P,S=4000):
    real=sim=0; comps=0
    for s in maestros:
        off=0
        for c in sorted([c for c in por_sess[s] if not c['side']],key=lambda c:c['t']):
            (pi,po,pw,pr),k=preco(c['model']); real+=c['usd']
            cr=max(0,c['cr']-off); ctx=c['i']+c['cw']+cr
            sim+=(c['i']*pi+c['out']*po+c['cw']*pw+cr*pr)/1e6
            if ctx>T:
                comps+=1; sim+=(S*po+P*pw)/1e6; off=max(0,c['cr']+c['cw']+c['i']-P)
    return real,sim,comps
for T,P in ((150e3,40e3),(150e3,60e3),(150e3,80e3),(200e3,60e3),(300e3,60e3)):
    real,sim,comps=simula(T,P); print(f'  simulação T={T/1e3:.0f}k P={P/1e3:.0f}k: real={real:.0f} sim={sim:.0f} economia={100*(1-sim/real):.0f}% compactacoes={comps} (1 a cada {len(main)/max(comps,1):.0f} turnos)')
