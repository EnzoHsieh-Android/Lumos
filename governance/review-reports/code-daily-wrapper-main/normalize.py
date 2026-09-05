"""收貨正規化(2026-08-26 SOP):quote: → 引句：「…」同行;file: 路徑:行 → 保留成 `路徑:行` 可被 refcheck 抓;確保首行 severity:。"""
import re,sys
src,dst=sys.argv[1],sys.argv[2]
lines=open(src,encoding="utf-8").read().splitlines()
out=[]
sev=next((l for l in lines if re.match(r"^\s*severity:\s*\w+",l)),None)
if sev: out.append(sev.strip())
else: out.append("severity: clean")
for l in lines:
    if re.match(r"^\s*severity:\s*\w+",l) and l.strip()==out[0]: continue
    m=re.match(r"^(\s*)quote:\s*(.*)$",l)
    if m:
        q=m.group(2).strip().strip('"').strip("'")
        q=q.replace("「","『").replace("」","』")
        out.append(f"{m.group(1)}引句：「{q}」"); continue
    m=re.match(r"^(\s*)file:\s*(\S+?):(\d+)\s*$",l)
    if m:
        out.append(f"{m.group(1)}位置:`{m.group(2)}:{m.group(3)}`"); continue
    out.append(l)
open(dst,"w",encoding="utf-8").write("\n".join(out)+"\n")
print("normalized",dst,"findings:",sum(1 for l in out if re.match(r"^\s*- \[",l)))
