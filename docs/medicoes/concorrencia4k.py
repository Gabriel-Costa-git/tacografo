import os, json, time
def teste(tam_alvo, n_proc=10, n_lines=2000):
    PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),f'conc-{tam_alvo}.jsonl')
    if os.path.exists(PATH): os.remove(PATH)
    t0=time.time(); pids=[]
    for i in range(n_proc):
        pid=os.fork()
        if pid==0:
            fd=os.open(PATH, os.O_WRONLY|os.O_APPEND|os.O_CREAT, 0o644)
            for n in range(n_lines):
                base=json.dumps({'w':i,'n':n,'pad':''})
                pad='x'*(tam_alvo-len(base)-1-((n*7)%50))   # linhas entre alvo-50 e alvo bytes, sem truncar
                os.write(fd,(json.dumps({'w':i,'n':n,'pad':pad})+'\n').encode())
            os.close(fd); os._exit(0)
        pids.append(pid)
    for p in pids: os.waitpid(p,0)
    dt=time.time()-t0; ok=bad=0; seen=set(); mx=0
    with open(PATH,'rb') as fh:
        for line in fh:
            mx=max(mx,len(line))
            try: d=json.loads(line); seen.add((d['w'],d['n'])); ok+=1
            except Exception: bad+=1
    print(f'linhas ate {tam_alvo} B (max real {mx}): procs={n_proc} validas={ok} corrompidas={bad} unicas={len(seen)} esperadas={n_proc*n_lines} tempo={dt:.2f}s')
    os.remove(PATH)
for t in (4096, 8192, 16384, 65536): teste(t)
