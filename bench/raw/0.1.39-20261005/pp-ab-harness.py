#!/usr/bin/env python3
import importlib.util, concurrent.futures, json, statistics, threading, time, argparse
from pathlib import Path
H=Path('/home/gonus/tmp/strata-paper-024-20260930/bench_client.py')
sp=importlib.util.spec_from_file_location('b',H); b=importlib.util.module_from_spec(sp); sp.loader.exec_module(b)

ap=argparse.ArgumentParser()
ap.add_argument('--mode',choices=['lanes','layer'],required=True)
ap.add_argument('--target',type=int,required=True)
ap.add_argument('--reps',type=int,default=5)
a=ap.parse_args()
ports=[19087,19088,19089] if a.mode=='lanes' else [19090,19090,19090]
kind='long_review' if a.target>=100000 else 'reasoning'

def make(rep,i):
    content,built,ph=b.workload_prompt(kind,a.target,nonce=f'pp-ab-{a.mode}-{a.target}-r{rep}-q{i}')
    body=b.request_body(content,1,seed=1234+rep*10+i)
    return body,built,ph

def parse(api,client_s,built,ph):
    u=api.get('usage') or {}
    t=api.get('timings') or {}
    pn=int(t.get('prompt_n') or 0)
    pm=float(t.get('prompt_ms') or 0.0)
    cn=int(t.get('cache_n') or 0)
    return {'built':built,'hash':ph,'api_prompt_tokens':u.get('prompt_tokens'),
            'cache_n':cn,'prompt_n':pn,'prompt_ms':pm,
            'engine_pp_tok_s':pn/(pm/1000.0) if pn and pm>0 else None,
            'client_s':client_s,'completion_tokens':u.get('completion_tokens')}

vals=[]
for rep in range(1,a.reps+1):
    specs=[make(rep,i) for i in range(3)]
    barrier=threading.Barrier(4)
    def worker(i):
        body,built,ph=specs[i]
        barrier.wait()
        api,client=b.post(ports[i],body,timeout=900)
        return i,parse(api,client,built,ph)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
        fut=[ex.submit(worker,i) for i in range(3)]
        barrier.wait(); t0=time.perf_counter()
        got=[f.result() for f in fut]
        wall=time.perf_counter()-t0
    got.sort(); rows=[x[1] for x in got]
    processed=sum(x['prompt_n'] for x in rows)
    api_total=sum(int(x['api_prompt_tokens'] or 0) for x in rows)
    rec={'kind':'rep','mode':a.mode,'target':a.target,'rep':rep,'wall_s':wall,'rows':rows,
         'processed_prompt_tokens':processed,'api_prompt_tokens_total':api_total,
         'common_wall_pp_tok_s':processed/wall if wall else None,
         'max_client_s':max(x['client_s'] for x in rows)}
    vals.append(rec['common_wall_pp_tok_s'])
    print(json.dumps(rec),flush=True)
print(json.dumps({'kind':'summary','mode':a.mode,'target':a.target,'n':len(vals),
                  'mean':statistics.fmean(vals),'sd':statistics.stdev(vals) if len(vals)>1 else 0.0,
                  'min':min(vals),'max':max(vals)}),flush=True)
