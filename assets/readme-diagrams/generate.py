#!/usr/bin/env python3
"""Rebuild the bilingual README illustrations. Python standard library only.

python3 assets/readme-diagrams/generate.py
python3 assets/readme-diagrams/generate.py --check
All scene text is real SVG text. Knowledge nodes reveal in story order;
other scene text stays visible while decorative paths animate.
"""
from pathlib import Path
from html import escape
import argparse
import xml.etree.ElementTree as ET

ASSETS = Path(__file__).resolve().parents[1]
C = dict(ink="#edf3ff", muted="#b5c4db", line="#526986", green="#75e5bd",
         blue="#8bbfff", purple="#c5adff", gold="#f3d18e", coral="#ffb4aa")
W = 760

def text(x, y, value, size=24, color="ink", anchor="start", weight=450):
    color = C.get(color, color)
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(value)}</text>'

def rect(x, y, w, h, fill="url(#panel)", stroke="#304461", r=18, sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def circle(x,y,r,fill,stroke="none",sw=1):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'

def path(d, color="line", width=2, dash="", animate=False):
    color=C.get(color,color)
    attr=f' stroke-dasharray="{dash}"' if dash else ""
    anim='<animate attributeName="stroke-dashoffset" values="0;-40" dur="2s" repeatCount="indefinite"/>' if animate else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{attr}>{anim}</path>'

def arrow(x,y,direction="right",color="line"):
    points={"right":f"{x-9},{y-6} {x},{y} {x-9},{y+6}",
            "left":f"{x+9},{y-6} {x},{y} {x+9},{y+6}",
            "down":f"{x-6},{y-9} {x},{y} {x+6},{y-9}",
            "up":f"{x-6},{y+9} {x},{y} {x+6},{y+9}"}[direction]
    return f'<polyline points="{points}" fill="none" stroke="{C.get(color,color)}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'

def badge(x,y,value,color="green",w=150):
    return rect(x,y,w,31,"#14243a",C[color],r=15,sw=.7)+circle(x+14,y+15,3,C[color])+text(x+26,y+21,value,14,color,weight=600)

def document(x,y,w,h,title,subtitle,color="blue"):
    return (rect(x+10,y-10,w,h,"#111e32","#263954",14)+
            rect(x+5,y-5,w,h,"#17253b","#344867",14)+
            rect(x,y,w,h)+
            rect(x+1,y+1,4,h-2,C[color],"none",2)+
            text(x+20,y+41,title,24,color,weight=600)+
            text(x+20,y+78,subtitle,21,"muted"))

def chip(x,y,value,color="blue",w=130):
    return rect(x,y,w,36,"#182a42","none",10)+text(x+w/2,y+25,value,20,color,"middle",550)

def header(kicker,title,en):
    return (text(34,34,kicker,13,"muted",weight=650)+
            text(34,76,title,30,weight=650)+
            path("M34 99H726","#283d58",1)+
            text(726,34,"LUMOS",13,"muted","end",650))

def scene(name,lang,title,kicker,h,body,desc):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(desc)}</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#122139"/><stop offset="1" stop-color="#090f1e"/></linearGradient>
  <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#1b2e48"/><stop offset="1" stop-color="#111d31"/></linearGradient>
  <radialGradient id="halo"><stop stop-color="#73b8d7" stop-opacity=".12"/><stop offset="1" stop-color="#73b8d7" stop-opacity="0"/></radialGradient>
  <pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".7" fill="#718da9" opacity=".15"/></pattern>
</defs>
<rect x=".5" y=".5" width="759" height="{h-1}" rx="20" fill="url(#bg)" stroke="#35465e"/>
<rect x="1" y="1" width="758" height="{h-2}" rx="20" fill="url(#grid)"/>
<ellipse cx="420" cy="190" rx="335" ry="185" fill="url(#halo)"/>
<g font-family="Inter, 'PingFang TC', 'Noto Sans TC', 'Microsoft JhengHei', system-ui, sans-serif">
{header(kicker,title,lang=="en")}
{body}
</g>
</svg>
'''

def map_scene(en):
    title="Read the code first. Write back after." if en else "先讀程式碼，改完寫回"
    b=path("M74 156H674Q720 156 720 205V491Q720 544 669 544H89Q40 544 40 495V217Q40 156 74 156","coral",2.5,"12 8",True)
    b+=rect(170,129,420,50,"#111f34","#6a4c56",16)
    b+=text(380,162,"Outer loop: checking the process" if en else "外圈：定期檢查這套流程",22,"coral","middle",600)
    b+=path("M40 205H199V229","coral",2)+arrow(199,230,"down","coral")
    b+=rect(58,185,275 if en else 168,29,"#122038","none",6)+text(68,207,"Adjust rules on drift" if en else "有走樣就調整規則",21,"coral")
    b+=path("M572 452V535","coral",2)+arrow(572,543,"down","coral")
    # Label sits left of the downward connector so the line never crosses the text.
    b+=rect(*((276,481,284,33) if en else (404,481,156,33)),"#101c30","none",6)+text(552,505,"Records go to the outer loop" if en else "每輪紀錄送進外圈",19 if en else 21,"coral","end")
    # Clockwise station loop. Each hand-off is labelled with what travels along it.
    b+=path("M324 271H428","blue",2,"12 8",True)+arrow(437,271,"right","blue")
    b+=text(380,258,"notes + diff" if en else "筆記＋改動",15,"blue","middle",550)
    b+=path("M563 311V366","purple",2,"12 8",True)+arrow(563,372,"down","purple")
    b+=text(575,346,"findings" if en else "各自的意見",15,"purple",weight=550)
    b+=path("M436 410H332","gold",2,"12 8",True)+arrow(324,410,"left","gold")
    b+=text(380,432,"outcomes" if en else "處理結果",15,"gold","middle",550)
    b+=path("M197 372V319","green",2,"12 8",True)+arrow(197,311,"up","green")
    b+=text(185,346,"next time" if en else "下次查得到",15,"green","end",550)
    nodes=[(70,231,"01","Read code" if en else "讀程式碼","Notes add the why" if en else "筆記補上理由","green"),
           (436,231,"02","Dispatch" if en else "分派審查","Reviewers by risk" if en else "依風險派 AI 審查","blue"),
           (436,372,"03","Review & resolve" if en else "審查與處理","Every finding logged" if en else "每條意見記下怎麼處理","purple"),
           (70,372,"04","Write back" if en else "寫回筆記","Trade-offs + checks" if en else "留下取捨與驗證","gold")]
    for x,y,_n,t,s,c in nodes:
        b+=rect(x,y,254,80)+text(x+22,y+32,t,26,c,weight=600)+text(x+22,y+60,s,19)
    b+=text(380,589,"Git hooks check the parts that can be checked mechanically." if en else "提交與推送時，Git hooks 檢查能機械判斷的部分。",21,"muted","middle")
    return title,620,b,"Four steps around each change: read the code and add context from notes, dispatch reviewers by risk, review and record every finding, write back. Each hand-off is labelled. An outer loop records each round and checks the process itself. Decorative paths animate; all labels remain visible."

def case_scene(en):
    title = "How review changed the fix" if en else "審查如何改變修法"
    b = text(36, 136, "Installed tool files caused a false high-risk rating." if en else "工具掃到自己安裝的檔案、讓小專案首次推送被誤判高風險", 18, "muted")
    widths = (210, 214, 216) if en else (202, 202, 236)
    headings = ("Skip the directory", "Match filenames", "Compare content") if en else ("整個目錄免查", "只認檔名", "比對內容")
    labels = ("Round 1 / 4 reviewers", "Round 3 / reviewers", "Result / fingerprints") if en else ("第 1 輪 / 4 位各自抓到", "第 3 輪 / 審查員抓到", "結果 / 內容指紋")
    lines = (
        ("User code in the same", "directory is skipped too."),
        ("Same-named user files", "and modified tool files", "still escape checks."),
        ("Record hashes at install.", "Skip only listed filenames", "with matching content.", "Changed files get checked."),
    ) if en else (
        ("同目錄的使用者程式", "也跟著逃過檢查"),
        ("使用者自己的同名檔", "或改過的工具檔", "仍然會漏查"),
        ("安裝時記下雜湊值", "檔名在清單上且內容相同", "才免查、改過就照掃"),
    )
    x = 36
    for i, (width, heading, label, rows, color) in enumerate(zip(widths, headings, labels, lines, ("coral", "purple", "green"))):
        b += rect(x, 164, width, 280)
        b += text(x + 16, 193, f"0{i + 1}", 14, color, weight=650)
        b += text(x + 16, 228, heading, 20 if en else 24, color, weight=600)
        b += text(x + 16, 262, label, 14, color, weight=600)
        for j, row in enumerate(rows):
            b += text(x + 16, 299 + j * 25, row, 15 if en else 17, "muted")
        if i == 2:
            b += text(x + 16, 414, "Accidents, not abuse." if en else "防不小心、不防刻意繞過", 15 if en else 16, "green", weight=600)
        if i < 2:
            b += path(f"M{x + width + 3} 237H{x + width + 20}", color, 2)
            b += arrow(x + width + 21, 237, "right", color)
        x += width + 24
    footer = (
        "The list lives in the project. Editing it too can bypass the check.",
        "At the three-round limit, a human approved round 4. Its fixes were not reviewed again.",
        "All 46 findings were handled before committing; many concerned other issues,",
        "including list-field writes and concurrency.",
    ) if en else (
        "指紋清單也放在專案裡、連清單一起改就能繞過。",
        "跑滿 3 輪上限後、由人決定加開第 4 輪。第 4 輪的修正未再受審。",
        "四輪 46 條意見全部處理後才提交、其中不少與此事無關、",
        "例如清單欄位寫入與併發問題。",
    )
    for i, row in enumerate(footer):
        b += text(36, 478 + i * 26, row, 15 if en else 17, "muted")
    desc = (
        "Three fixes linked by review findings. Round 1: four reviewers independently found that skipping the tool directory also skipped user code. Round 3: exact filenames still missed same-named user files and modified tool files. The final fix records hashes at installation and skips only listed filenames with identical content. The project-local list can itself be changed, so this prevents accidents, not deliberate bypass. A human approved round 4 after the three-round limit; its fixes were not reviewed again. All 46 findings, many unrelated, were handled before committing."
        if en else
        "三格因果圖。第 1 輪有 4 位審查員各自抓到整個目錄免查會漏掉使用者程式。第 3 輪抓到只認精確檔名仍漏掉使用者同名檔與改過的工具檔。最後在安裝時記下雜湊值、僅檔名在清單上且內容相同才免查。專案內的清單也能被改、防不小心、不防刻意繞過。跑滿 3 輪由人加開第 4 輪、其修正未再受審。四輪 46 條包含不少無關問題、全部處理後才提交。"
    )
    return title, 588, b, desc

def first_scene(en):
    title="A conversation becomes a change." if en else "從一句需求，到有依據的改動"
    b=badge(36,121,"YOU" if en else "你提出需求","green",150)
    b+=rect(36,172,293,199)
    # A filled, attached speech tail. The former two-stroke green tail looked
    # like an unexplained check mark at README scale.
    b+='<path d="M67 370V391L96 370Z" fill="#17253b" stroke="#304461" stroke-width="1.5" stroke-linejoin="round"/>'
    b+='<path d="M68 370H95" stroke="#17253b" stroke-width="3"/>'
    b+=text(58,266,"“Add refunds.”" if en else "「幫我加退款功能」",26,weight=600)
    b+=text(58,307,"Clarify goals and trade-offs" if en else "釐清需求、限制與取捨",20,"muted")
    b+=path("M329 258H375","blue",2)+arrow(383,258,"right","blue")
    b+=badge(399,121,"AI WORKFLOW" if en else "AI 承接流程","blue",210)
    b+=path("M419 207V338","#3e5775",2)
    stages=[(201,"search","Read context" if en else "查脈絡","green"),
            (267,"code","Build & test" if en else "實作與測試","blue"),
            (333,"note","Commit & record" if en else "提交與寫回","gold")]
    for n,(y,i,t,c) in enumerate(stages,1):
        b+=circle(419,y,23,"#15253b",C[c])+text(419,y+7,str(n),20,c,"middle",550)+text(460,y+8,t,25,weight=550)
    b+=rect(36,416,688,64,"#13243a","#334c68",14)
    b+=text(58,443,"Checks return feedback; the AI fixes or asks." if en else "檢查回傳原因，AI 補正或回報你決定。",en and 21 or 23)
    b+=text(58,467,"Git actions stay within your authorization." if en else "Git 操作仍在你的授權範圍內。",18,"muted")
    return title,510,b,"Illustrative workflow, not a recorded run: a request, context retrieval, implementation and testing, authorized Git operations and write-back."

def graph_scene(en):
    title="Plans, features, evidence — then repair." if en else "計劃形成實作，事故推動修正"
    b='<g id="knowledge-flow">'
    # A complete static fallback; a 24-second story holds its final state
    # for 12.2 seconds after the repair verification appears.
    times={"plan-checkout":.3,"plan-payment":1.0,
           "feature-checkout":2.0,"feature-payment":3.0,
           "verification-checkout":5.0,"verification-payment":6.0,
           "incident":7.5,"plan-points-fix":9.0,"verification-points":11.5}
    def reveal(at):
        return (f'<animate attributeName="opacity" dur="24s" repeatCount="indefinite" '
                f'values="0;0;1;1" keyTimes="0;{at/24:.4f};{(at+.3)/24:.4f};1"/>')
    bands=[(132,"01","Plans" if en else "先寫計劃","purple"),
           (269,"02","Features" if en else "形成功能","blue"),
           (421,"03","Verification" if en else "留下驗證","green"),
           (558,"04","Incidents" if en else "事故回饋","coral")]
    for y,n,t,c in bands:
        b+=rect(30,y,700,111,"#142238","#2b3c55",15)
        b+=text(48,y+28,n,14,"muted",weight=650)
        b+=text(48,y+63,t,en and 21 or 24,c,weight=600)
    # A small narrative rail makes the animation's current story beat legible
    # without turning the diagram into a UI mockup or adding decorative icons.
    b+=text(48,117,"STORY BEATS" if en else "流程節點",13,"muted",weight=650)
    beats=[(360,.3,"01", "Context" if en else "既有流程","purple"),
           (472,7.5,"02", "Incident" if en else "事故","coral"),
           (584,9.0,"03", "Repair" if en else "修正","coral"),
           (696,11.5,"04", "Recheck" if en else "回歸","green")]
    b+=path("M360 119H696","#2b3c55",2)
    previous=360
    for x,at,n,label,c in beats:
        if x!=previous:
            b+=f'<g data-kind="story-progress" data-reveal="{at}" opacity="1">{reveal(at)}'
            b+=path(f"M{previous+7} 119H{x-7}",c,2.5)+"</g>"
        b+=f'<g data-kind="story-beat" data-reveal="{at}" opacity="1">{reveal(at)}'
        b+=circle(x,119,7,"#17263c",C[c],2)+circle(x,119,3,C[c])
        b+=text(x,110,n+"  "+label,13,c,"middle",650)+"</g>"
        previous=x
    # The repair plan targets an existing feature, not an unrelated new module.
    edges=[
      ("plan-checkout","feature-checkout","M460 229V287","purple","down",460,287,2.1),
      ("plan-payment","feature-payment","M642 229V287","purple","down",642,287,3.1),
      ("feature-checkout","feature-payment","M495 322H607","blue","right",607,322,3.2),
      ("feature-checkout","verification-checkout","M460 386V435","green","down",460,435,5.1),
      ("feature-payment","verification-payment","M642 386V435","green","down",642,435,6.1),
      ("incident","plan-points-fix","M263 585C168 451 172 179 261 179","coral","right",261,179,8.5),
      ("plan-points-fix","feature-checkout","M309 179H350Q370 179 370 202V298Q370 322 425 322","coral","right",425,322,9.8),
      ("feature-checkout","verification-points","M436 386C412 413 353 463 313 463","green","left",313,463,11.0),
    ]
    for source,target,d,c,orientation,x,y,at in edges:
        b+=f'<g data-from="{source}" data-to="{target}" data-reveal="{at}" opacity="1">{reveal(at)}'
        b+=path(d,c,2.5,"8 7" if c=="coral" else "")
        b+=arrow(x,y,orientation,c)
        if source=="plan-points-fix":
            b+=rect(316,254,108,35,"#142238","none",7)
            b+=text(370,278,"Fix points" if en else "修正退點",en and 18 or 20,"coral","middle",550)
        b+='</g>'
    # Ownership/impact is distinct from chronology: the incident belongs to
    # checkout even before it creates a repair plan. A fine dotted relation
    # keeps that fact visible without competing with the repair arrows.
    at=7.9
    b+=f'<g data-from="incident" data-to="feature-checkout" data-relation="affected-feature" data-reveal="{at}" opacity="1">{reveal(at)}'
    b+=path("M299 586C340 554 352 519 374 477C397 433 416 382 440 345","coral",1.8,"3 7")
    b+=circle(440,345,3,C["coral"])+"</g>"
    nodes=[
      ("plan-points-fix",285,179,"Points-fix plan" if en else "退點修復計劃","purple",16,False),
      ("plan-checkout",460,179,"Checkout plan" if en else "結帳流程計劃","purple",16,False),
      ("plan-payment",642,179,"Payment plan" if en else "付款串接計劃","purple",16,False),
      ("feature-checkout",460,322,"Checkout" if en else "結帳流程","blue",23,True),
      ("feature-payment",642,322,"Payments" if en else "付款串接","blue",23,True),
      ("incident",285,600,"Points not returned" if en else "取消訂單未退點","coral",16,False),
      ("verification-points",285,463,"Points regression" if en else "退點回歸測試","green",16,False),
      ("verification-checkout",460,463,"Checkout E2E" if en else "結帳端對端","green",16,False),
      ("verification-payment",642,463,"Duplicate charge" if en else "重複付款壓測","green",16,False),
    ]
    for node,x,y,label,c,r,contract in nodes:
        b+=f'<g id="{node}" data-reveal="{times[node]}" opacity="1">{reveal(times[node])}'
        b+=circle(x,y,r+8,"#192c45")+circle(x,y,r,C[c])
        if contract:
            evidence="verification-checkout" if node=="feature-checkout" else "verification-payment"
            at=times[evidence]+.6
            b+=f'<circle data-kind="contract" data-evidence="{evidence}" data-reveal="{at}" opacity="1" cx="{x}" cy="{y}" r="29" fill="none" stroke="{C["gold"]}" stroke-width="2.5">{reveal(at)}</circle>'
            b+=f'<g data-kind="contract-star" data-reveal="{at}" opacity="1">{reveal(at)}'
            b+=text(x,y+7,"★",20,"#172237","middle",650)+'</g>'
        b+=text(x,y+(49 if contract else 41),label,en and 18 or 21,"ink","middle",550)
        b+='</g>'
    b+=text(415,600,"Affects the checkout flow." if en else "影響既有結帳流程",en and 21 or 24,"muted")
    b+=text(415,633,"Then verify the fix." if en else "修正後，補上回歸驗證",en and 21 or 22,"muted")
    b+='</g>'
    b+=rect(30,688,700,74,"#14243a","#344967",14)
    b+=circle(56,711,7,C["blue"])+circle(56,711,11,"none",C["gold"],2)
    b+=text(79,718,"Gold ring: contract linked to verification" if en else "金環：帶合約，並連到驗證紀錄",en and 20 or 22,"gold")
    b+=path("M45 743H68","coral",2.5)+arrow(69,743,"right","coral")
    b+=text(79,750,"Incident → repair plan → existing feature → recheck" if en else "事故 → 修復計劃 → 既有功能 → 回歸驗證",en and 20 or 22,"coral")
    return title,785,b,"Illustrative shop graph, assuming checkout owns points returns: plans precede features and verification. A points-not-returned incident is directly related to the checkout feature, creates a points-fix plan that modifies that existing flow, and is followed by a points regression test. Contract rings and stars appear after evidence. A 24-second cycle builds for 11.8 seconds, then holds the complete graph for 12.2 seconds; static fallback remains complete."

def dispatch_scene(en):
    title="One brief. Several independent lenses." if en else "材料相同，判斷保持獨立"
    b=badge(37,124,"INPUT" if en else "共用材料","green",125)
    b+=document(37,191,190,198,"Brief" if en else "派工材料","Change + context" if en else "改動與脈絡","green")
    b+=chip(56,293,"Rules" if en else "重要規則","gold",150)+chip(56,338,"Evidence" if en else "驗證依據","blue",150)
    b+=path("M227 289H260V192H290M260 289H290M260 289V386H290","blue",2.5)
    b+=path("M484 192H512V289H543M484 289H512M484 386H512V289","purple",2.5)+arrow(544,289,"right","purple")
    rows=[(159,"Correctness" if en else "正確性","code","green"),
          (256,"Boundaries" if en else "邊界與風險","search","blue"),
          (353,"Architecture" if en else "架構一致性","layers","purple")]
    for y,t,i,c in rows:
        b+=rect(291,y,193,66,"#16263c","#3d526f",33)
        b+=text(388,y+41,t,en and 21 or 23,c,"middle",550)
    b+=badge(550,124,"OUTPUT" if en else "逐條處置","purple",170)
    b+=rect(545,191,178,198)
    b+=text(564,234,"Findings" if en else "意見",22,"purple",weight=600)
    for y,t,c in [(290,"Adopt" if en else "採納","green"),(332,"Reject" if en else "駁回","muted"),(374,"Follow up" if en else "待處理","gold")]:
        b+=circle(567,y-6,4,C[c])+text(582,y,t,23,c)
    b+=text(380,473,"Finders don't see one another's reports; agreement isn't proof." if en else "找問題的審查看不到彼此的報告；意見一致也不等於一定對。",22,"muted","middle")
    return title,505,b,"The same change, context, rules and evidence fan out to independent review perspectives, then findings are accounted for as adopted, rejected or needing follow-up. Seats are illustrative."

def risk_review_scene(en):
    title="Review weight follows risk" if en else "依風險決定審多重"
    # Column A: what goes in and how risk is judged.
    b=badge(36,121,"INPUT" if en else "輸入","green",110)
    b+=rect(36,166,150,262)
    b+=rect(37,167,4,260,C["green"],"none",2)
    b+=text(56,204,"New code" if en else "新增的程式碼",20 if en else 21,"green",weight=600)
    b+=text(56,240,"Scanned with" if en else "用固定規則",17,"muted")
    b+=text(56,264,"fixed rules" if en else "掃高風險寫法",17,"muted")
    b+=text(56,318,"e.g." if en else "例如：",15,"muted")
    b+=text(56,342,"write w/o txn" if en else "寫入沒包交易",15)
    b+=text(56,366,"HTTP, no timeout" if en else "HTTP 沒設逾時",15)
    # Column B: two branches.
    b+=path("M186 196H214","line",2)+arrow(221,196)
    b+=path("M186 330H214","coral",2)+arrow(221,330,color="coral")
    b+=rect(222,166,344,58)
    b+=text(242,202,"Ordinary change" if en else "一般改動",19,"blue",weight=600)
    b+=text(546,202,"1 to 2 reviewers" if en else "派 1 到 2 位審查",17,"muted","end")
    b+=rect(222,240,344,188,"url(#panel)","#6a4c56")
    b+=text(242,272,"High risk" if en else "高風險",19,"coral",weight=600)
    b+=text(546,272,"7+ per round" if en else "每輪至少 7 位",17,"muted","end")
    cells=[("Correctness" if en else "正確性","ink"),("Concurrency" if en else "併發與資源","ink"),("Edges & input" if en else "邊界與輸入","ink"),
           ("Rules & notes" if en else "規則與筆記","ink"),("Architecture" if en else "架構一致","purple"),("Security" if en else "資安","gold"),
           ("Generalist" if en else "通才找問題","ink"),("Spec, if any" if en else "對照規格","muted")]
    for i,(label,c) in enumerate(cells):
        # 最後一排不滿三格時置中,不讓右邊空一塊
        last=(len(cells)-1)//3
        pad=(3-(len(cells)-last*3))*54 if i//3==last else 0
        x=236+(i%3)*108+pad
        y=288+(i//3)*40
        b+=rect(x,y,100,32,"#182a42","none" if c!="coral" else C["coral"],9,.8)
        b+=text(x+50,y+21,label,13 if en else 14,c,"middle",550)
    b+=text(242,418,"Spec = only with a finalized design spec" if en else "對照規格 = 有定稿的設計規格才派",13,"muted")
    # Column C: every finding gets a disposition.
    b+=path("M566 196H578V297M566 330H578V297","line",2)+path("M578 297H584","line",2)+arrow(591,297)
    b+=badge(574,121,"OUTPUT" if en else "每條意見的去向","purple",150)
    b+=rect(592,166,132,262)
    for y,label,c in [(236,"Fixed" if en else "修掉","green"),(290,"Waived" if en else "附理由不修","gold"),(344,"Disproved" if en else "證明不成立","muted")]:
        b+=circle(610,y-6,4,C[c])+text(622,y,label,18,c)
    # Bottom: the one mechanical rule plus the independence caveat.
    b+=rect(36,452,688,72,"#13243a","#334c68",14)
    b+=text(56,482,"High-risk push is blocked without a review outcome." if en else "高風險推送前必須留下審查結果：通過，或寫明理由的跳過。",18 if en else 19,weight=600)
    b+=text(56,508,"Finders don't see each other's reports; agreement isn't proof." if en else "找問題的審查彼此看不到報告，意見一致也不等於一定對。",16,"muted")
    return title,556,b,"A risk scan of new code sends ordinary changes to one or two reviewers and high-risk changes to at least seven per round: five problem-finders, architecture and security, plus a spec check when a finalized spec exists. Every finding must be fixed, waived with a reason, or disproved with evidence; a high-risk push needs a review outcome."

def review_scene(en):
    title="Different checks. Shared evidence." if en else "從規則、判斷到行為，交叉看同一個改動"
    b=rect(36,123,688,75,"#222a44","#655781",16)
    b+=text(58,155,"Architecture consistency" if en else "架構一致性",25,"purple",weight=600)
    b+=text(58,182,"Compare with this project’s established patterns." if en else "先對照專案既有做法與分層。",20,"muted")
    cols=[(36,"01","Linters" if en else "Linter","Encoded rules" if en else "已編碼規則","code","green"),
          (275,"02","Review" if en else "檢核與審查","Context + reasoning" if en else "脈絡與推論","search","blue"),
          (514,"03","Tests" if en else "測試","Covered behaviour" if en else "覆蓋情境的行為","check","gold")]
    for x,n,t,sub,i,c in cols:
        b+=rect(x,225,210,193)
        b+=text(x+105,305,n,40,c,"middle",550)
        b+=text(x+105,355,t,25,c,"middle",600)+text(x+105,386,sub,en and 18 or 21,"muted","middle")
    b+=path("M141 418V439H619V418M380 418V449","purple",2)+arrow(380,456,"down","purple")
    b+=text(380,484,"Complementary evidence, not a safety guarantee." if en else "互補的證據，不是安全保證。",22,"muted","middle")
    return title,518,b,"Architecture review compares the project’s existing patterns. Linters, context-dependent review questions and tests supply complementary evidence with different blind spots, not a strict sequence or guarantee."

def writeback_scene(en):
    title="Make the next session less blind." if en else "讓這次的理由，成為下次的起點"
    b=badge(39,122,"THIS CHANGE" if en else "這次留下什麼","gold",194)
    b+=rect(39,175,231,199)
    for y,t,i,c in [(204,"Decisions" if en else "設計取捨","chat","purple"),(271,"Dispositions" if en else "審查處置","check","blue"),(338,"Verification" if en else "驗證結果","shield","green")]:
        b+=text(60,y+5,t,en and 23 or 25,c,weight=550)
        if y!=338:b+=path(f"M58 {y+32}H250","#2d425e",1)
    b+=path("M270 276H349","gold",2.5)+arrow(354,276,"right","gold")
    b+=text(313,253,"Write" if en else "寫回",20,"gold","middle")
    b+=document(357,174,354,205,"Project notes" if en else "相關專案筆記","Context that can be retrieved" if en else "可查詢、可追溯的脈絡","gold")
    b+=chip(378,277,"Reasons" if en else "理由","purple",144)+chip(536,277,"Evidence" if en else "證據","green",151)
    b+=text(379,348,"Update · recheck · mark stale" if en else "更新、重驗，或標示過時",21,"muted")
    b+=path("M534 379V406","green",2.5)+arrow(534,413,"down","green")
    b+=rect(357,414,354,64,"#132d30","#3b7068",14)+text(379,453,"Next session retrieves it" if en else "下一個 session 查回使用",en and 21 or 23,"green",weight=550)
    b+=path("M357 446H81Q59 446 59 423V388","green",2,"8 7")+arrow(59,379,"up","green")
    return title,513,b,"A change’s design decisions, review dispositions and verification results are written to relevant notes. A later session retrieves them; records are updated, rechecked or marked stale as needed."

def evals_scene(en):
    title="Evaluate the process, not just the patch." if en else "評測工作台：流程本身也要被檢查"
    b=badge(36,122,"REVIEW REPLAY" if en else "審查回放","purple",en and 205 or 175)
    b+=badge(36,314,"RETRIEVAL EVAL" if en else "查詢評測","blue",en and 205 or 175)
    for y,t,s,c in [(174,"Review records" if en else "審查紀錄","Findings + dispositions" if en else "發現與處置","purple"),
                    (366,"Labelled set" if en else "標註題目","Retrieval reference" if en else "查詢參照","blue")]:
        b+=document(36,y,248,104,t,s,c)
    b+=path("M284 225H319","purple",2)+arrow(326,225,"right","purple")
    b+=path("M284 417H319","blue",2)+arrow(326,417,"right","blue")
    b+=rect(329,174,241,296)
    b+=text(350,211,"Compare" if en else "回放與比較",en and 25 or 24,weight=600)
    b+=path("M349 235H550","#344b69",1)
    b+=text(449,272,"Verdicts" if en else "判定有沒有改變？",en and 24 or 22,"purple","middle")
    b+=rect(351,291,92,41,"#252b47","none",10)+rect(456,291,92,41,"#252b47","none",10)
    b+=text(397,319,"Prior" if en else "舊案",20,"muted","middle")+text(502,319,"Replay" if en else "回放",20,"purple","middle")
    b+=path("M349 350H550","#344b69",1)
    b+=text(449,389,"Retrieval results" if en else "查詢結果怎麼變？",en and 22 or 22,"blue","middle")
    b+=path("M355 419H414M355 432H393M463 419H541M463 432H523","blue",4)
    b+=path("M570 322H603","coral",2.5)+arrow(611,322,"right","coral")
    b+=rect(609,287,115,74,"#322d3b","#a67476",14)
    b+=text(666,332,"Calibrate" if en else "校準",en and 22 or 27,"coral","middle",600)
    b+=path("M669 361V410","coral",2)
    b+=path("M669 410V498H160V484","coral",2,"8 7")+arrow(160,479,"up","coral")
    b+=rect(270,484,331,34,"#101d30","none",8)+text(435,508,"Feed subsequent rounds" if en else "帶回後續流程，再留下新紀錄",en and 22 or 20,"coral","middle")
    return title,548,b,"Two evaluation streams: replay review records to compare verdicts, and use human-labelled retrieval questions to compare results. Comparisons inform calibration. This conceptual workbench shows no measured scores or guaranteed improvement."

def swiss_cheese_scene(en):
    title="Five imperfect layers. Fewer escapes." if en else "五層都有洞，但問題更難一路穿過"
    b=text(38,126,
           "Different blind spots reduce the chance of one shared miss." if en else "不同防線有不同盲點；疊起來，漏洞較不容易全部對齊。",
           en and 19 or 21,"muted")
    # The coral path sits behind every slice. Masks cut real holes in each
    # slice, so the path is visible only where one rare route lines up.
    b+='<g data-kind="aligned-escape">'+path("M590 132V540","coral",3,"9 8",True)+'</g>'
    rows=[
      (150,"01","Risk tiering" if en else "風險分級","purple",[(318,164,12),(448,188,9),(590,175,10),(676,161,8)]),
      (230,"02","AI reviewers" if en else "多個 AI 審查","blue",[(287,246,9),(405,265,13),(522,240,8),(590,255,10),(680,270,11)]),
      (310,"03","Disposition gate" if en else "放行規則","coral",[(305,340,12),(468,324,9),(590,335,10),(690,348,8)]),
      (390,"04","External rules" if en else "外部規則","gold",[(280,404,8),(390,430,12),(505,405,10),(590,415,10),(675,432,9)]),
      (470,"05","Tests proven red" if en else "測試翻紅","green",[(315,495,11),(445,480,8),(545,510,12),(590,495,10),(690,482,8)]),
    ]
    for i,(y,n,label,c,holes) in enumerate(rows):
        mask=f"cheese-{i}"
        b+=f'<g data-kind="defence-layer" data-layer="{n}">'
        b+=f'<defs><mask id="{mask}"><rect x="244" y="{y}" width="472" height="50" rx="14" fill="white"/>'
        for hx,hy,hr in holes:
            b+=f'<circle cx="{hx}" cy="{hy}" r="{hr}" fill="black"/>'
        b+='</mask></defs>'
        b+=text(40,y+20,n,13,c,weight=700)
        b+=text(76,y+34,label,en and 18 or 21,c,weight=600)
        b+=f'<rect x="244" y="{y}" width="472" height="50" rx="14" fill="#3a3225" stroke="{C[c]}" stroke-width="1.2" mask="url(#{mask})"/>'
        for hx,hy,hr in holes:
            b+=circle(hx,hy,hr,"none","#886f4d",1)
        b+='</g>'
    b+=arrow(590,546,"down","coral")
    b+='<g data-kind="escape-ledger">'+rect(403,554,313,77,"#2c2630","#925e67",14)
    b+=text(424,585,"Escape ledger" if en else "漏網帳",22,"coral",weight=650)
    b+=text(424,614,"Miss → new rule or test" if en else "漏掉的問題 → 新規則或測試",en and 18 or 20,"muted")+'</g>'
    b+=path("M403 594H369Q344 594 344 569V435Q344 415 365 415","green",2.5,"8 7")
    b+=arrow(373,415,"right","green")
    b+=rect(38,554,305,77,"#14243a","#344967",14)
    b+=text(58,583,"Intercept ledger → precision" if en else "攔截帳 → 精準度",en and 18 or 20,"blue",weight=550)
    b+=text(58,613,"Escape ledger → recall" if en else "漏網帳 → 召回率",en and 18 or 20,"green",weight=550)
    b+=text(380,673,
            "Not zero risk—visible leakage that becomes harder to repeat." if en else "不是零風險；而是讓漏多少看得見，並讓同類問題更難再漏。",
            en and 19 or 21,"muted","middle")
    return title,700,b,"Five Swiss-cheese defence layers: risk tiering, multi-seat review, disposition gates, external rules, and tests proven to fail when behaviour is removed. A rare aligned escape enters an escape ledger, which feeds new mechanical rules or tests. Intercept and escape ledgers make precision and recall observable; the model does not claim zero defects."

def drift_scene(en):
    title = "From writing notes to pushing code" if en else "從寫下筆記到推送程式碼"
    b = path("M57 147V538", "blue", 2)
    stages = [
        (122, 162, "Writing notes" if en else "寫入時", "green"),
        (304, 132, "At commit" if en else "提交時", "blue"),
        (456, 164, "Before push" if en else "推送前", "purple"),
    ]
    for number, (y, height, label, color) in enumerate(stages, 1):
        b += circle(57, y + 25, 20, "#14243a", C[color])
        b += text(57, y + 32, str(number), 20, color, "middle", 600)
        b += rect(94, y, 630, height)
        b += text(114, y + 32, label, 23, color, weight=600)
    for y in (293, 445):
        b += arrow(57, y, "down", "blue")

    b += text(114, 185, "Keep reasons the code can't explain." if en else "只記程式碼看不出來的理由", 17)
    b += text(114, 211, "Don't copy fields, defaults or flows." if en else "欄位、預設值、流程不抄進筆記", 17, "muted")
    b += text(114, 241, "New code line refs / unsourced state descriptions" if en else "新增程式行號 / 沒註明來源的現況描述", 16)
    b += badge(542 if en else 584, 219, "Block at commit" if en else "提交時擋下", "coral", 162 if en else 120)
    b += text(114, 272, "Other content needs rules and review." if en else "其餘內容靠守則和審查", 16, "muted")

    rows = [
        (365, "Code changed, no notes touched" if en else "改了程式、一篇筆記都沒動", "Always block" if en else "一定擋下", "coral"),
        (404, "New source file, no assigned note" if en else "新增程式檔、沒指定負責的筆記", "Block" if en else "擋下", "coral"),
        (517, "Note still cites a removed name or path" if en else "名稱或路徑消失、筆記還在提", "Warn only" if en else "只提醒", "gold"),
        (556, "Test exists, note says 'test to be added'" if en else "測試已上線、筆記還說之後補測試", "Block" if en else "擋下", "coral"),
        (595, "Linked note was deleted" if en else "連到的另一篇筆記已被刪除", "Always block" if en else "一定擋下", "coral"),
    ]
    for y, label, status, color in rows:
        b += text(114, y, label, 16)
        b += badge(566 if en else 584, y - 22, status, color, 138 if en else 120)

    b += text(94, 652, "Other blocks can be set to warn by the project." if en else "除了兩項一定擋下的檢查、其餘可由專案改成提醒", 16, "muted")
    b += text(94, 679, "Content accuracy still needs review and people." if en else "筆記內容對不對、最後仍靠審查和人", 16, "muted")
    desc = (
        "Three checkpoints from writing to push. Writing rules block new code line references and unsourced state descriptions at commit. Commit checks block code changes without note updates and new source files without an assigned note. Before push, removed names or paths still in notes only warn, while outdated promises to add existing tests and deleted note links block. Missing note updates and broken links always block. Other blocks can be set to warn. Content accuracy needs review and people."
        if en else
        "從寫入到推送的三道關卡。新增程式行號及沒註明來源的現況描述在提交時擋下。提交時也擋下改程式沒動筆記、新增程式檔沒指定負責筆記。推送前、消失的名稱或路徑只提醒、測試已上線卻仍寫之後補測試及筆記連結斷掉則擋下。改程式沒動筆記和連結斷掉一定擋、其餘可改成提醒。內容正確性仍靠審查和人。"
    )
    return title, 710, b, desc


SCENES={"map":("00 / THE SYSTEM",map_scene),
        "drift-guard":("NOTES / DRIFT CHECKS",drift_scene),
        "first-change":("START / NATURAL LANGUAGE",first_scene),
        "graph-demo":("01 / KNOWLEDGE",graph_scene),
        "case-review":("CASE / REAL REVIEW",case_scene),
        "dispatch-overview":("02 / DISPATCH",dispatch_scene),
        "risk-review":("02-03 / REVIEW BY RISK",risk_review_scene),
        "review-overview":("03 / REVIEW",review_scene),
        "swiss-cheese":("QUALITY / FIVE LAYERS",swiss_cheese_scene),
        "writeback-overview":("04 / WRITE-BACK",writeback_scene),
        "evals-overview":("EVALS / FEEDBACK",evals_scene)}

def validate(svg):
    root=ET.fromstring(svg)
    ns={"s":"http://www.w3.org/2000/svg"}
    parents={c:p for p in root.iter() for c in p}
    graph=root.find(".//*[@id='knowledge-flow']")
    for el in root.findall(".//s:animate",ns):
        parent=parents[el]
        if el.get("attributeName")=="opacity":
            assert graph is not None and parent in set(graph.iter())
            assert parent.get("data-reveal") is not None
            assert parent.get("opacity")=="1", "Static fallback must be complete"
            assert el.get("values")=="0;0;1;1"
            assert el.get("dur")=="24s"
            keys=list(map(float,el.get("keyTimes").split(";")))
            assert all(a<b for a,b in zip(keys,keys[1:]))
            assert keys[0]==0 and keys[-1]==1
            at=float(parent.get("data-reveal"))
            assert abs(keys[1]-at/24)<.0001 and abs(keys[2]-(at+.3)/24)<.0001
        else:
            assert el.get("attributeName") in {"stroke-width","stroke-dashoffset"}
            assert parent.tag.rsplit("}",1)[-1] in {"path","rect","circle"}
    assert root.find("s:title",ns).text
    assert root.find("s:desc",ns).text
    if root.find("s:title",ns).text in {"Five imperfect layers. Fewer escapes.","五層都有洞，但問題更難一路穿過"}:
        assert len(root.findall(".//*[@data-kind='defence-layer']"))==5
        assert len(root.findall(".//*[@data-kind='aligned-escape']"))==1
        assert len(root.findall(".//*[@data-kind='escape-ledger']"))==1
    if graph is not None:
        # Preserve the node process, not merely the same palette.
        expected={
            ("plan-checkout","feature-checkout"),
            ("plan-payment","feature-payment"),
            ("feature-checkout","feature-payment"),
            ("feature-checkout","verification-checkout"),
            ("feature-payment","verification-payment"),
            ("incident","feature-checkout"),
            ("incident","plan-points-fix"),
            ("plan-points-fix","feature-checkout"),
            ("feature-checkout","verification-points"),
        }
        relations={(el.get("data-from"),el.get("data-to"))
                   for el in graph.iter() if el.get("data-from")}
        assert relations==expected, "Knowledge-flow relations changed"
        node_ids={el.get("id") for el in graph.iter() if el.get("id")}
        assert all(a in node_ids and b in node_ids for a,b in relations)
        assert len(graph.findall(".//*[@data-kind='contract']"))==2
        assert len(graph.findall(".//*[@data-kind='contract-star']"))==2
        by_id={el.get("id"):el for el in graph.iter() if el.get("id")}
        for suffix in ("checkout","payment"):
            plan=float(by_id[f"plan-{suffix}"].get("data-reveal"))
            feature=float(by_id[f"feature-{suffix}"].get("data-reveal"))
            verification=float(by_id[f"verification-{suffix}"].get("data-reveal"))
            assert plan+.3<feature and feature+.3<verification
        for ring in graph.findall(".//*[@data-kind='contract']"):
            assert float(ring.get("data-reveal"))>float(by_id[ring.get("data-evidence")].get("data-reveal"))+.4
        incident=float(by_id["incident"].get("data-reveal"))
        repair=float(by_id["plan-points-fix"].get("data-reveal"))
        recheck=float(by_id["verification-points"].get("data-reveal"))
        repair_edge=next(el for el in graph.iter() if el.get("data-from")=="plan-points-fix")
        affected=next(el for el in graph.iter() if el.get("data-relation")=="affected-feature")
        assert affected.get("data-from")=="incident" and affected.get("data-to")=="feature-checkout"
        assert incident+.3<float(affected.get("data-reveal"))<repair-.3
        assert incident+.3<repair
        assert repair+.3<float(repair_edge.get("data-reveal"))<recheck-.3
        assert max(float(el.get("data-reveal"))+.3 for el in graph.iter() if el.get("data-reveal"))<=14
    for el in root.findall(".//s:text",ns):
        assert float(el.get("font-size"))>=13
        p=el
        while p in parents:
            assert p.get("opacity","1")=="1", "Text must stay fully opaque"
            p=parents[p]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true",help="Validate and compare generated files without writing.")
    args=parser.parse_args()
    count=0
    for name,(kicker,fn) in SCENES.items():
        for lang in ("zh","en"):
            title,h,body,desc=fn(lang=="en")
            svg=scene(name,lang,title,kicker,h,body,desc)
            validate(svg)
            p=ASSETS/f"{name}-{lang}.svg"
            if args.check:
                assert p.read_text(encoding="utf-8")==svg, f"Regenerate {p.name}"
            else:
                p.write_text(svg,encoding="utf-8")
            count+=1
    print(f"{count} bilingual SVGs: {'validated, reproducible, static fallback and reveal order checked' if args.check else 'generated'}")

if __name__=="__main__":
    main()
