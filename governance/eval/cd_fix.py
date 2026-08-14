import json, collections
ORDER={"clean":0,"minor":1,"major":2,"blocker":3}
REPOS={"mOrangePos":"/Users/enzo/mOrangePos","Landmark":"/Users/enzo/backend/LandmarkMember","toolchain":"/Users/enzo/harness/lumos-toolchain"}
def cclist(cc):
    if isinstance(cc,list): return [int(c) for c in cc]
    return [int(c) for c in str(cc).strip("[] ").replace(" ","").split(",") if c]
def residual(l):
    f1=sum(1 for c in l if c==1); f2=sum(1 for c in l if c==2)
    return f1*(f1-1)/(2*(f2+1))
print("═══ C(修). 殘餘<1.0 之後,下一輪實際挖到什麼 ═══")
hits=clean=0
for name,repo in REPOS.items():
    rows=[json.loads(l) for l in open(repo+"/docs/.canary-log.jsonl") if l.strip()]
    loops=collections.OrderedDict()
    for r in rows:
        if r.get("loop"): loops.setdefault(r["loop"],[]).append(r)
    for lp,rs in loops.items():
        rounds=collections.OrderedDict()
        for i,r in enumerate(rs):
            rounds.setdefault(r.get("round") or f"_{i}",[]).append(r)
        rl=list(rounds.items())
        for i,(rid,g) in enumerate(rl[:-1]):
            cc=next((x.get("capture_counts") for x in g if x.get("capture_counts")),None)
            if cc is None: continue
            try: l=cclist(cc)
            except ValueError: continue
            if not l: continue
            est=residual(l)
            if est<1.0:
                nxt=rl[i+1][1]
                sevs=[x.get("severity") for x in nxt if x.get("severity")]
                mx=max(sevs,key=lambda s:ORDER.get(s,0)) if sevs else "-"
                fnd=sum(x.get("findings") or 0 for x in nxt)
                bad=ORDER.get(mx,0)>=2
                hits+=bad; clean+=(not bad)
                print(f"[{name}] {lp} {rid}: 殘餘 {round(est,2)} → 下一輪 max={mx} 折入{fnd} {'★仍出 major+★' if bad else ''}")
print(f"—— 帳面「快抓完」後下一輪仍出 major+ : {hits}/{hits+clean}")
print()
print("═══ D(修). 重疊分布 ═══")
for name,repo in REPOS.items():
    rows=[json.loads(l) for l in open(repo+"/docs/.canary-log.jsonl") if l.strip()]
    f1t=tot=ns=0
    for r in rows:
        cc=r.get("capture_counts")
        if cc is None: continue
        try: l=cclist(cc)
        except ValueError: continue
        if not l: continue
        f1t+=sum(1 for c in l if c==1); tot+=len(l); ns+=1
    if tot: print(f"[{name}] 有重疊數據 {ns} 筆 | 相異缺陷 {tot} | 只被一席抓到 {f1t}({round(100*f1t/tot)}%)")
