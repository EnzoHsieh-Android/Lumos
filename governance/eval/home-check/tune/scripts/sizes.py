import sys
sys.path.insert(0, __file__.rsplit("/",1)[0])
from common import *
cases = [("A1","b2fc512","Systems/分析行程流程與檢查點.md"),("A2","c177791","Systems/一鍵展示.md"),("A3","d98b4ca","Systems/任務流程領域模型.md"),("C","b2fc512","Systems/展示頁面.md"),("D1","b2fc512","Systems/評估與Jev決策點.md"),("D2","5ec931e","Systems/模型用戶端.md"),("D3","b2fc512","Systems/一鍵展示.md")]
for cid,c,n in cases:
    t = note_at(c,n); ac = about_code(t)
    code=[f for f in changed_files(c) if is_code(f) and f in ac]
    d = git("show","--format=","-U3",c,"--",*code)
    print(cid, "note chars",len(t),"lines",t.count("\n"),"| diff chars",len(d),"lines",d.count("\n"), "files",len(code))
