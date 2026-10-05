#!/usr/bin/env python3
import importlib.util, concurrent.futures, json, statistics, threading, time
from pathlib import Path
H=Path('/home/gonus/tmp/strata-paper-024-20260930/bench_client.py')
sp=importlib.util.spec_from_file_location('b',H); b=importlib.util.module_from_spec(sp); sp.loader.exec_module(b)
P=19090
content,n,ph=b.workload_prompt('reasoning',1500)
print(json.dumps({'kind':'metadata','prompt_tokens_built':n,'prompt_hash':ph,'requests':2,'reps':5,'max_tokens':512}),flush=True)
def pair(max_tokens,rep):
    barrier=threading.Barrier(3)
    def w(i):
        body=b.request_body(content,max_tokens,seed=1234)
        barrier.wait(); t=time.perf_counter(); api,_=b.post(P,body,timeout=300)
        return i,time.perf_counter()-t,api
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        fs=[ex.submit(w,i) for i in range(2)]
        barrier.wait(); t0=time.perf_counter(); vals=[f.result() for f in fs]; wall=time.perf_counter()-t0
    vals.sort(); rows=[]
    for i,e2e,api in vals:
        u=api.get('usage') or {}; tm=api.get('timings') or {}
        rows.append({'i':i,'e2e_s':e2e,'completion_tokens':u.get('completion_tokens'),'prompt_tokens':u.get('prompt_tokens'),'timings':tm})
    total=sum(int(x['completion_tokens'] or 0) for x in rows)
    return {'kind':'warmup' if rep==0 else 'rep','rep':rep,'wall_s':wall,'aggregate_tg_tok_s':total/wall,'rows':rows}
print(json.dumps(pair(128,0)),flush=True)
vals=[]; e=[[],[]]
for rep in range(1,6):
    r=pair(512,rep); vals.append(r['aggregate_tg_tok_s'])
    for i,row in enumerate(r['rows']): e[i].append(row['e2e_s'])
    print(json.dumps(r),flush=True)
print(json.dumps({'kind':'summary','aggregate_mean':statistics.fmean(vals),'aggregate_sd':statistics.stdev(vals),'min':min(vals),'max':max(vals),'per_pos_e2e_mean':[statistics.fmean(x) for x in e]}),flush=True)
