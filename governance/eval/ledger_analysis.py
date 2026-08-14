import json, collections, statistics
def _cclist(cc):
    # 2026-08-14 code-loop r1 s5 nit 修:帳上 capture_counts 是 list,str().split 解析必炸→C/D 段死碼
    if isinstance(cc, list):
        return [int(c) for c in cc]
    return [int(c) for c in str(cc).strip("[] ").replace(" ", "").split(",") if c]

ORDER={"clean":0,"minor":1,"major":2,"blocker":3}
REPOS={"mOrangePos":"/Users/enzo/mOrangePos","Landmark":"/Users/enzo/backend/LandmarkMember","toolchain":"/Users/enzo/harness/lumos-toolchain","KDS":"/Users/enzo/Citrus_KDS"}
def residual(cc):
    f1=sum(1 for c in cc if c==1); f2=sum(1 for c in cc if c==2)
    return f1*(f1-1)/(2*(f2+1))
allrows={}
for name,repo in REPOS.items():
    try: rows=[json.loads(l) for l in open(repo+"/docs/.canary-log.jsonl") if l.strip()]
    except FileNotFoundError: continue
    allrows[name]=rows

print("═══ A. 逐 loop 輪序剖面(輪=round id 或逐筆;嚴重度序列看長尾) ═══")
for name,rows in allrows.items():
    loops=collections.OrderedDict()
    for r in rows:
        lp=r.get("loop")
        if lp: loops.setdefault(lp,[]).append(r)
    for lp,rs in loops.items():
        if len(rs)<4: continue
        # group by round preserving append order
        rounds=collections.OrderedDict()
        for i,r in enumerate(rs):
            rid=r.get("round") or f"_{i}"
            rounds.setdefault(rid,[]).append(r)
        seq=[]
        for rid,g in rounds.items():
            sevs=[x.get("severity") for x in g if x.get("severity")]
            mx=max(sevs,key=lambda s:ORDER.get(s,0)) if sevs else "-"
            miss=sum(1 for x in g if x.get("kind")=="missed")
            seq.append(f"{mx}{'(m'+str(miss)+')' if miss else ''}")
        # 長尾:首個 major+ 之後又出現 major+ 的次數
        idx=[i for i,s in enumerate(seq) if s.startswith(("major","blocker"))]
        tail=len(idx)-1 if len(idx)>1 else 0
        print(f"[{name}] {lp}: {len(rounds)}輪 {len(rs)}筆 | 序列 {'→'.join(seq)} | major+輪距首次後再現 {tail} 次")

print()
print("═══ B. 規模 vs 收穫(scope_lines 有值的記錄;世界:diff 越大越抓不到) ═══")
for name,rows in allrows.items():
    pts=[(r["scope_lines"], r.get("findings")) for r in rows if r.get("scope_lines") is not None and r.get("findings") is not None]
    if len(pts)<8: print(f"[{name}] 樣本 {len(pts)} 筆,太少跳過"); continue
    big=[f for s,f in pts if s>=900]; small=[f for s,f in pts if s<900]
    def m(x): return round(statistics.mean(x),2) if x else "-"
    # 粗相關
    try:
        xs=[s for s,_ in pts]; ys=[f for _,f in pts]
        mx,my=statistics.mean(xs),statistics.mean(ys)
        cov=sum((a-mx)*(b-my) for a,b in pts)
        corr=cov/((sum((a-mx)**2 for a in xs)**.5)*(sum((b-my)**2 for b in ys)**.5)+1e-9)
    except Exception: corr=float('nan')
    print(f"[{name}] n={len(pts)} | <900行 平均存活 findings {m(small)}(n={len(small)}) vs ≥900行 {m(big)}(n={len(big)}) | pearson r={round(corr,2)}")

print()
print("═══ C. capture-recapture 假安心檢驗:殘餘<1.0(帳面「快抓完」)的輪,下一輪實際還挖到什麼 ═══")
hits=miss=0
for name,rows in allrows.items():
    loops=collections.OrderedDict()
    for r in rows:
        lp=r.get("loop")
        if lp: loops.setdefault(lp,[]).append(r)
    for lp,rs in loops.items():
        rounds=collections.OrderedDict()
        for i,r in enumerate(rs):
            rid=r.get("round") or f"_{i}"
            rounds.setdefault(rid,[]).append(r)
        rl=list(rounds.items())
        for i,(rid,g) in enumerate(rl[:-1]):
            cc=next((x.get("capture_counts") for x in g if x.get("capture_counts")),None)
            if not cc: continue
            try: ccl=_cclist(cc)
            except ValueError: continue
            est=residual(ccl)
            if est<1.0:
                nxt=rl[i+1][1]
                sevs=[x.get("severity") for x in nxt if x.get("severity")]
                mx=max(sevs,key=lambda s:ORDER.get(s,0)) if sevs else "-"
                fnd=sum(x.get("findings") or 0 for x in nxt)
                tag="★下一輪仍挖到 major+★" if ORDER.get(mx,0)>=2 else ("下一輪乾淨" if ORDER.get(mx,0)<=1 else "")
                if ORDER.get(mx,0)>=2: hits+=1
                else: miss+=1
                print(f"[{name}] {lp} {rid}: 殘餘估計 {round(est,2)} → 下一輪 max={mx} findings={fnd} {tag}")
print(f"—— 殘餘<1 之後仍出 major+ 的比例: {hits}/{hits+miss}")

print()
print("═══ D. 重疊分布(f1 占比高=席間幾乎不重疊=獨立性存疑或各抓皮毛) ═══")
for name,rows in allrows.items():
    f1t=tot=0; ns=0
    for r in rows:
        cc=r.get("capture_counts")
        if not cc: continue
        try: l=_cclist(cc)
        except ValueError: continue
        f1t+=sum(1 for c in l if c==1); tot+=len(l); ns+=1
    if tot: print(f"[{name}] 有重疊數據輪 {ns} | 缺陷總數 {tot} | 只被一席抓到 {f1t}({round(100*f1t/tot)}%)")

print()
print("═══ E. 漏抓率×模型檔位(舊制帳;停用後轉歷史) ═══")
for name,rows in allrows.items():
    by=collections.Counter()
    tot=collections.Counter()
    for r in rows:
        k=r.get("kind"); a=(r.get("auditor") or "?").split("-")[0].split("/")[0]
        if k in ("caught","missed"):
            tot[a]+=1
            if k=="missed": by[a]+=1
    line=" | ".join(f"{a}:{by[a]}/{tot[a]}" for a in tot if tot[a]>=5)
    print(f"[{name}] missed/總 {line}")
