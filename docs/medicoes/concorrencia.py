import os, json, time, sys
PATH=os.path.join(os.path.dirname(os.path.abspath(__file__)),'concorrencia.jsonl')
if os.path.exists(PATH): os.remove(PATH)
N_PROC=10; N_LINES=2000
t0=time.time()
pids=[]
for i in range(N_PROC):
    pid=os.fork()
    if pid==0:
        fd=os.open(PATH, os.O_WRONLY|os.O_APPEND|os.O_CREAT, 0o644)
        for n in range(N_LINES):
            rec={'w':i,'n':n,'ts':time.time(),'pad':'x'*(300+(n*7)%1200)}
            os.write(fd,(json.dumps(rec)+'\n').encode())
        os.close(fd); os._exit(0)
    pids.append(pid)
for p in pids: os.waitpid(p,0)
dt=time.time()-t0
ok=bad=0; seen=set()
with open(PATH,'rb') as fh:
    for line in fh:
        try:
            d=json.loads(line); seen.add((d['w'],d['n'])); ok+=1
        except Exception: bad+=1
print(f'procs={N_PROC} linhas_validas={ok} corrompidas={bad} unicas={len(seen)} esperadas={N_PROC*N_LINES} tempo={dt:.2f}s tamanho={os.path.getsize(PATH)} bytes fs={os.statvfs(PATH).f_frsize}')
