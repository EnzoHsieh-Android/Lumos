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
    title="Understand the code. Keep the context." if en else "先理解程式，改完留下脈絡"
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
    b+=text(380,238,"Implement" if en else "完成改動",14,"blue","middle",550)
    b+=text(380,258,"+ context" if en else "連同脈絡送審",14,"blue","middle",550)
    b+=path("M563 311V366","purple",2,"12 8",True)+arrow(563,372,"down","purple")
    b+=text(575,346,"findings" if en else "各自的意見",15,"purple",weight=550)
    b+=path("M436 410H332","gold",2,"12 8",True)+arrow(324,410,"left","gold")
    b+=text(380,432,"outcomes" if en else "處理結果",15,"gold","middle",550)
    b+=path("M197 372V319","green",2,"12 8",True)+arrow(197,311,"up","green")
    b+=text(185,346,"next time" if en else "下次查得到",15,"green","end",550)
    nodes=[(70,231,"01","Read code" if en else "讀程式碼","Decisions + constraints" if en else "筆記補上決策與限制","green"),
           (436,231,"02","Dispatch" if en else "分派審查","Reviewers by risk" if en else "依風險派 AI 審查","blue"),
           (436,372,"03","Review & resolve" if en else "審查與處理","Every finding logged" if en else "每項意見留下處理結論","purple"),
           (70,372,"04","Write back" if en else "寫回筆記","Trade-offs + checks" if en else "留下取捨與驗證","gold")]
    for x,y,_n,t,s,c in nodes:
        b+=rect(x,y,254,80)+text(x+22,y+32,t,26,c,weight=600)+text(x+22,y+60,s,19)
    b+=text(380,589,"Git hooks run automated checks at commit and push." if en else "提交與推送時，Git hooks 核對可自動檢查的項目。",21,"muted","middle")
    return title,620,b,"Four steps around each change: read the code and add context from notes, dispatch reviewers by risk, review and record every finding, write back. Each hand-off is labelled. An outer loop records each round and checks the process itself. Decorative paths animate; all labels remain visible." if en else '每次改動依序理解程式並查閱脈絡、依風險分派審查、逐項處理意見、寫回筆記。箭頭標示各步驟交付的內容；外圈彙整每輪紀錄，定期檢查流程本身。裝飾線條會動，文字持續可見。'

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
    title="Connect plans, verification, and repairs." if en else "從計劃到驗證，把修復經驗接回來"
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
           (269,"02","Features" if en else "實作功能","blue"),
           (421,"03","Verification" if en else "記錄驗證","green"),
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
      ("verification-checkout",460,463,"Checkout E2E" if en else "結帳端對端測試","green",16,False),
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
    b+=text(79,718,"Gold ring: rules linked to verification" if en else "金環：記有重要規則，並連到驗證紀錄",20 if en else 22,"gold")
    b+=path("M45 743H68","coral",2.5)+arrow(69,743,"right","coral")
    b+=text(79,750,"Incident → repair plan → existing feature → recheck" if en else "事故 → 修復計劃 → 既有功能 → 回歸驗證",en and 20 or 22,"coral")
    return title,785,b,"Illustrative shop graph, assuming checkout owns points returns: plans precede features and verification. A points-not-returned incident is directly related to the checkout feature, creates a points-fix plan that modifies that existing flow, and is followed by a points regression test. Contract rings and stars appear after evidence. A 24-second cycle builds for 11.8 seconds, then holds the complete graph for 12.2 seconds; static fallback remains complete." if en else '假設退點由結帳系統負責的商店示意圖：計劃連到功能與驗證。取消訂單未退點的事故關聯到既有結帳功能，衍生退點修復計劃，修改既有流程後補上回歸測試。重要規則的金環與星號在驗證節點後出現。動畫每輪 24 秒，前 11.8 秒逐步展開，再保留完整圖 12.2 秒；不播放動畫時也顯示完整內容。'

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
    title="Review based on risk" if en else "依風險安排審查"
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
    b+=text(546,202,"1 to 2 reviewers" if en else "1 至 2 位審查員",17,"muted","end")
    b+=rect(222,240,344,188,"url(#panel)","#6a4c56")
    b+=text(242,272,"High risk" if en else "高風險",19,"coral",weight=600)
    b+=text(546,272,"7+ per round" if en else "每輪至少 7 位",17,"muted","end")
    cells=[("Correctness" if en else "正確性","ink"),("Concurrency" if en else "併發與資源","ink"),("Edges & input" if en else "邊界與輸入","ink"),
           ("Rules & notes" if en else "規則與筆記","ink"),("Architecture" if en else "架構一致","purple"),("Security" if en else "資安","gold"),
           ("Generalist" if en else "綜合檢查","ink")]
    for i,(label,c) in enumerate(cells):
        # 最後一排不滿三格時置中,不讓右邊空一塊
        last=(len(cells)-1)//3
        pad=(3-(len(cells)-last*3))*54 if i//3==last else 0
        x=236+(i%3)*108+pad
        y=288+(i//3)*40
        b+=rect(x,y,100,32,"#182a42","none" if c!="coral" else C["coral"],9,.8)
        b+=text(x+50,y+21,label,13 if en else 14,c,"middle",550)
    b+=text(242,418,"+ Spec reviewer when the design is finalized" if en else "＋定稿設計規格：另加 1 位對照規格",13,"muted")
    # Column C: every finding gets a disposition.
    b+=path("M566 196H578V297M566 330H578V297","line",2)+path("M578 297H584","line",2)+arrow(591,297)
    b+=badge(574,121,"OUTPUT" if en else "每條意見的去向","purple",150)
    b+=rect(592,166,132,262)
    for y,label,c in [(236,"Fixed" if en else "修掉","green"),(290,"Waived" if en else "說明不修理由","gold"),(344,"Disproved" if en else "證明不成立","muted")]:
        b+=circle(610,y-6,4,C[c])+text(622,y,label,16,c)
    # Bottom: the one mechanical rule plus the independence caveat.
    b+=rect(36,452,688,72,"#13243a","#334c68",14)
    b+=text(56,482,"High-risk push is blocked without a review outcome." if en else "高風險推送前必須留下審查結果：通過，或寫明理由的跳過。",18 if en else 19,weight=600)
    b+=text(56,508,"Finders don't see each other's reports; agreement isn't proof." if en else "審查員各自找問題，不互看報告，意見一致也不等於一定對。",16,"muted")
    return title,556,b,"A risk scan of new code sends ordinary changes to one or two reviewers and high-risk changes to at least seven per round: five problem-finders, architecture and security, plus a spec check when a finalized spec exists. Every finding must be fixed, waived with a reason, or disproved with evidence; a high-risk push needs a review outcome." if en else '先掃描新增程式的風險：一般改動由一至兩位審查員檢查，高風險每輪至少七位，包含五個找問題的席位、架構與資安席；有定稿設計時再加規格對照席。每條意見都要修正、附理由接受或以證據反駁；高風險推送必須有審查結果。'

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
    title = "The toolkit itself is checked every week" if en else "每週自動檢查這套工具本身"
    b = rect(36, 122, 688, 290)
    b += text(60, 160, "Scheduled mainly in Lumos's own repo" if en else "主要在 Lumos 自己的 repo 排程執行", 18, "muted")
    rows = [
        (180, "Review replay" if en else "審查回放", "Compare past verdicts and flag differences" if en else "比對歷史判定，找出差異", "purple"),
        (236, "Retrieval exam" if en else "查詢考卷", "Labelled questions: are the right notes found?" if en else "人工標好的題目：查得到該看的筆記嗎？", "blue"),
        (292, "Scenario probes" if en else "情境探針", "Plain requests: does the AI check notes itself?" if en else "用口語出題：AI 會不會自己去查筆記？", "green"),
        (348, "Missed notes" if en else "推播漏網", "Did notes shown before edits miss relevant ones?" if en else "改檔前送上的筆記，有沒有漏掉該看的？", "gold"),
    ]
    for y, label, desc, color in rows:
        b += chip(60, y, label, color, 160 if en else 130)
        b += text(236 if en else 206, y + 25, desc, 18 if en else 19)
    b += path("M380 414V446", "coral", 2) + arrow(380, 452, "down", "coral")
    boxes = [
        (36, "Record every week" if en else "每週留下紀錄"),
        (280, "Alert when triggered" if en else "符合條件時提醒"),
        (524, "Fix rules or add tests" if en else "修規則或補測試"),
    ]
    for x, label in boxes:
        b += rect(x, 460, 200, 64, "#322d3b", "#a67476", 14)
        b += text(x + 100, 499, label, 17 if en else 20, "coral", "middle", 600)
    for x in (236, 480):
        b += path(f"M{x} 492H{x + 36}", "coral", 2) + arrow(x + 43, 492, "right", "coral")
    b += path("M624 524V566H20V266H28", "coral", 2, "8 7") + arrow(34, 266, "right", "coral")
    b += rect(250, 550, 260, 32, "#101d30", "none", 8) + text(380, 572, "Measure again next week" if en else "下週再量一次", 18 if en else 20, "coral", "middle")
    b += text(36, 620, "Helps detect regressions in covered scenarios; improvement is not guaranteed." if en else "讓已涵蓋情境的退步更容易被發現，不保證每次改動都變好", 16, "muted")
    desc = (
        "Four checks run on a schedule, mainly in Lumos's own repo: review replay recomputes past verdicts, a retrieval exam checks whether labelled questions find the right notes, scenario probes check whether the AI looks up notes on its own, and a missed-note check looks for relevant notes that were not shown before edits. Results are recorded weekly; failed review replays or probe questions alert a person, the retrieval exam only alerts when too many candidate notes are unlabelled (score drops are just recorded), the missed-note check only keeps a list, and fixes become rules or tests that are measured again the next week. It helps detect regressions in covered scenarios but does not guarantee improvement."
        if en else
        "主要在 Lumos 自己的 repo 排程執行四種檢查：審查回放重算舊案結論、查詢考卷看標好的題目查不查得到該看的筆記、情境探針看 AI 會不會自己查筆記、推播漏網看改檔前送上的筆記有沒有漏。每週留下紀錄；審查回放或情境探針出問題就通知人，查詢考卷只在沒標過的候選筆記太多時通知（分數退步只記錄），推播漏網只留清單；修成規則或測試後下週再量。讓已涵蓋情境的退步更容易被發現，不保證每次改動都變好。"
    )
    return title, 650, b, desc

def swiss_cheese_scene(en):
    title="Multiple checks, complementary coverage." if en else "多層檢查，補足各自的盲點"
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
      (390,"04","Static checks" if en else "靜態檢查","gold",[(280,404,8),(390,430,12),(505,405,10),(590,415,10),(675,432,9)]),
      (470,"05","Tests + faults" if en else "測試與故障驗證","green",[(315,495,11),(445,480,8),(545,510,12),(590,495,10),(690,482,8)]),
    ]
    for i,(y,n,label,c,holes) in enumerate(rows):
        mask=f"cheese-{i}"
        b+=f'<g data-kind="defence-layer" data-layer="{n}">'
        b+=f'<defs><mask id="{mask}"><rect x="244" y="{y}" width="472" height="50" rx="14" fill="white"/>'
        for hx,hy,hr in holes:
            b+=f'<circle cx="{hx}" cy="{hy}" r="{hr}" fill="black"/>'
        b+='</mask></defs>'
        b+=text(40,y+20,n,13,c,weight=700)
        b+=text(76,y+34,label,18 if en else 20,c,weight=600)
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
    b+=text(58,583,"Track false alarms" if en else "追蹤誤報",18 if en else 20,"blue",weight=550)
    b+=text(58,613,"Track missed defects" if en else "追蹤漏判",18 if en else 20,"green",weight=550)
    b+=text(380,673,
            "Record escaped defects and use them to improve checks." if en else "記錄已發現的漏判，作為改進規則與測試的依據。",
            en and 19 or 21,"muted","middle")
    return title,700,b,"Five Swiss-cheese defence layers: risk tiering, multi-seat review, disposition gates, external rules, and tests proven to fail when behaviour is removed. A rare aligned escape enters an escape ledger, which feeds new mechanical rules or tests. Records of false alarms and missed defects inform improvements; the model does not claim zero defects." if en else '五層各有盲點的防線：風險分級、多席審查、處置閘、外部規則，以及確認改壞行為會失敗的測試。漏過防線的問題記入漏網帳，作為新增規則或測試的依據。誤報與漏判紀錄用來改進檢查，不代表零缺陷保證。'

def drift_scene(en):
    title = "Keep notes useful for the next change" if en else "讓筆記跟得上每次改動"
    b = path("M57 147V487", "blue", 2)
    stages = [
        (122, "Writing notes" if en else "寫入時", "green",
         "Record decisions and constraints" if en else "保存決策與限制",
         "Keep context the code cannot explain." if en else "留下程式碼看不出的理由與限制。",
         "Set revisit conditions for temporary arrangements." if en else "暫時安排要寫明何時回頭確認。"),
        (292, "At commit" if en else "提交時", "blue",
         "Check that notes were maintained" if en else "檢查筆記是否同步維護",
         "Check note updates alongside code changes." if en else "檢查程式改動是否伴隨筆記更新。",
         "New source files need an assigned note." if en else "新增程式檔要指定負責的筆記。"),
        (462, "Before push" if en else "推送前", "purple",
         "Find stale references and pending checks" if en else "找出過期引用與待確認內容",
         "Check old references and revisit conditions." if en else "檢查舊名稱、連結與已成立的回頭條件。",
         "Reread notes updated with the code they describe." if en else "程式與負責的筆記一起改時，安排整篇重讀。"),
    ]
    for number, (y, label, color, purpose, line1, line2) in enumerate(stages, 1):
        b += circle(57, y + 25, 20, "#14243a", C[color])
        b += text(57, y + 32, str(number), 20, color, "middle", 600)
        b += rect(94, y, 630, 150)
        b += text(114, y + 32, label, 23, color, weight=600)
        b += text(114, y + 67, purpose, 23 if not en else 22, weight=550)
        b += text(114, y + 101, line1, 18, "muted")
        b += text(114, y + 128, line2, 18, "muted")
    for y in (282, 452):
        b += arrow(57, y, "down", "blue")
    b += text(94, 651, "Scopes and block/warn conditions are detailed below the diagram." if en else "各項檢查的範圍與擋下／提醒條件，見圖下方細節。", 17, "muted")
    b += text(94, 678, "Content accuracy still needs review and human judgment." if en else "筆記內容是否正確，仍需審查與人的判斷。", 17, "muted")
    desc = (
        "Three stages: record decisions and constraints, check note maintenance at commit, and find stale references and pending checks before push. This overview does not list every block or warning; the README details their scopes and exceptions."
        if en else
        "三階段維護筆記：寫入時保存決策與限制，提交時檢查筆記是否同步維護，推送前找出過期引用與待確認內容。這是摘要圖；各項擋下或提醒條件、範圍與例外見 README 細節。"
    )
    return title, 710, b, desc


ANDROID_TITLES={"en":"Android: check first, then dig one layer at a time.","zh":"Android：先判有沒有問題，再一層一層往下查"}   # validate 也用它認圖,改標題只改這裡

def android_scene(en):
    title=ANDROID_TITLES["en" if en else "zh"]
    b=text(38,128,"From a single run or the full check before push; dig only on a problem." if en else "可以單獨跑，也可以來自推送前整套驗收；上一層有異常才往下。",
           17 if en else 20,"muted")
    b+='<g data-kind="android-inputs">'
    b+=rect(38,150,330,70)+rect(39,151,4,68,C["blue"],"none",2)
    b+=text(58,180,"Macrobenchmark",21,"blue",weight=600)
    b+=text(58,207,"Startup and scroll numbers + traces" if en else "啟動、滑動的每輪數字與 Trace",16 if en else 17,"muted")
    b+=rect(392,150,330,70)+rect(393,151,4,68,C["purple"],"none",2)
    b+=text(412,180,"Memory & stability run" if en else "記憶體與穩定性收集",21,"purple",weight=600)
    b+=text(412,207,"Collects with dumpsys · Perfetto · logcat" if en else "dumpsys、Perfetto、logcat 收資料",16 if en else 17,"muted")+'</g>'
    b+=path("M203 220V246","line",2)+arrow(203,250,"down")+path("M557 220V246","line",2)+arrow(557,250,"down")
    layers=[
      (254,"L0","Slower? Below the agreed bar?" if en else "有沒有變慢、達不達標","lumos macrobench: vs. baseline and agreed standards" if en else "lumos macrobench：跟基準比、對照人訂的標準","Lumos","green"),
      (346,"L1","Where is it stuck: busy or waiting?" if en else "卡在哪：忙著算，還是在等","Perfetto + trace_processor, read via Google's skill" if en else "Perfetto 錄、trace_processor 查，照 Google 官方 skill","Google skill" if en else "Google 官方","blue"),
      (438,"L2","Which function, which line?" if en else "哪個函式、哪一行","simpleperf (Android NDK) points to file and line" if en else "simpleperf（NDK 附）抽樣，指到檔案與行號","Android tool" if en else "Android 工具","gold"),
      (530,"L3","What holds memory, and why?" if en else "誰在佔記憶體、為什麼不釋放","heap_profile, java_heap_dump; test data OK'd first" if en else "heap_profile、java_heap_dump；要先同意只用測試資料","Needs a human" if en else "要人裁","coral"),
    ]
    for i,(y,n,label,sub,tag,c) in enumerate(layers):
        b+=f'<g data-kind="android-layer" data-layer="{n}">'
        b+=rect(38,y,684,70)+rect(39,y+1,4,68,C[c],"none",2)
        b+=text(58,y+31,n,15,c,weight=700)
        b+=text(98,y+31,label,20 if en else 21,"ink",weight=600)
        b+=text(98,y+57,sub,15 if en else 16,"muted")
        b+=badge(562,y+20,tag,c,146)+'</g>'
        if i<len(layers)-1:
            b+=path(f"M380 {y+70}V{y+88}","line",2,"6 6",True)+arrow(380,y+92,"down")
    # 記憶體類 check 沒過時從 L0 直達 L3(L1、L2 看 CPU 時間,記憶體問題看不到)
    b+='<g data-kind="memory-shortcut">'+path("M722 289H738Q746 289 746 297V557Q746 565 738 565H726","coral",2,"6 6",True)+arrow(724,565,"left","coral")+'</g>'
    b+=text(380,626,"No anomaly at a layer → record it and stop there" if en else "哪一層沒有異常，就在查證紀錄記下並停在那一層",15 if en else 16,"muted","middle")
    b+='<g data-kind="android-record">'+rect(38,642,684,82,"#14243a","#344967",14)
    b+=text(58,674,"Evidence record" if en else "查證紀錄",22,"green",weight=650)
    b+=text(58,705,"rerun.sh reruns it all; an AI with no background re-judges → notes" if en else "rerun.sh 一鍵重跑；不知前因的 AI 再判一次 → 寫回筆記",15 if en else 17,"muted")+'</g>'
    desc=("Android verification flow. Two inputs: Macrobenchmark results with a recording of each run, and a memory and stability run that opens and closes a screen many times. "
          "L0 uses lumos macrobench to compare with the saved baseline and the standards people agreed on. Only when it finds a problem does L1 read a Perfetto recording with trace_processor, following Google's official android-profiler skill, to find where the app is stuck; "
          "L2 uses simpleperf from the Android NDK to point at the function and line; L3 uses Perfetto's heap_profile and java_heap_dump, only after a person agrees to run on test data only. The memory and stability run gathers data with dumpsys, Perfetto, and logcat. "
          "Both inputs can come from a single run or from the full check before push. A dashed shortcut takes failed memory checks from L0 straight to L3. Any layer with nothing wrong is recorded and the check stops there; everything goes into an evidence record that can be rerun and is re-judged by an AI with no background.") if en else (
          "Android 驗證流程。兩種輸入：Macrobenchmark 的結果（含每次的執行紀錄），以及反覆開關畫面的記憶體與穩定性收集。"
          "L0 由 lumos macrobench 跟存好的基準比、對照人訂的標準；有問題才到 L1，用 trace_processor 讀 Perfetto 錄下的紀錄，照 Google 官方 android-profiler skill 找出卡在哪；"
          "L2 用 Android NDK 附的 simpleperf 指到函式與行號；L3 用 Perfetto 附的 heap_profile 與 java_heap_dump 查記憶體，要先有人同意只用測試資料。記憶體與穩定性收集用 dumpsys、Perfetto、logcat 收資料。"
          "兩種輸入可以單獨跑，也可以來自推送前整套驗收。記憶體類的檢查沒過時，虛線從 L0 直接跳到 L3。哪一層沒問題就記下並停在那一層；全部寫進可重跑、並由不知前因的 AI 再判一次的查證紀錄。")
    return title,746,b,desc

ANDROID_ACCEPTANCE_TITLES={"en":"Android: a full device check before push.","zh":"Android：推之前在實機上整套驗收一次"}   # validate 也用它認圖,改標題只改這裡

def android_acceptance_scene(en):
    title=ANDROID_ACCEPTANCE_TITLES["en" if en else "zh"]
    b=text(38,128,"Commit first; the record is tied to this version of the app." if en else "先提交再跑；查證紀錄綁在這一版 App 程式與驗收素材上。",
           17 if en else 20,"muted")
    b+='<g data-kind="android-e2e-preflight">'+rect(38,150,684,58,"#14243a","#344967",14)
    b+=text(58,177,"Preflight" if en else "開跑前檢查",20,"green",weight=650)
    b+=text(58,199,"Device, tools, clean working tree; fails → exit 2, app untouched" if en else "裝置、工具、工作目錄乾淨；不過就回 2，不碰 App",15 if en else 16,"muted")+'</g>'
    b+=path("M380 208V222","line",2)+arrow(380,226,"down")
    steps=[
      ("Build and install" if en else "建置並安裝","Build the APK, install it, record its fingerprint" if en else "建 APK、裝上平板、記下檔案指紋","Must pass" if en else "必須過","blue"),
      ("UI flows" if en else "UI 流程","Maestro taps through each flow file; one retry" if en else "Maestro 照流程檔點一遍；沒過自動重跑一次","Must pass" if en else "必須過","green"),
      ("Screenshots" if en else "截圖比對","Compare with baselines a person approved (99.5%)" if en else "跟人看過的基準圖比，門檻 99.5%","Must pass" if en else "必須過","green"),
      ("Memory & stability" if en else "記憶體與穩定性","Open and close a screen: leaks, crashes, StrictMode" if en else "反覆開關畫面：漏記憶體、閃退、主執行緒違規","Must pass" if en else "必須過","purple"),
      ("Speed" if en else "效能","Macrobenchmark against the saved baseline" if en else "Macrobenchmark 跟存好的基準比","Warns only" if en else "只提醒","gold"),
    ]
    for i,(label,sub,tag,c) in enumerate(steps):
        y=230+i*74
        b+=f'<g data-kind="android-e2e-step" data-step="{i+1}">'
        b+=rect(38,y,684,58)+rect(39,y+1,4,56,C[c],"none",2)
        b+=text(58,y+25,str(i+1),15,c,weight=700)
        b+=text(86,y+25,label,19 if en else 20,"ink",weight=600)
        b+=text(86,y+48,sub,14 if en else 15,"muted")
        b+=badge(588,y+14,tag,c,120)+'</g>'
        b+=path(f"M380 {y+58}V{y+70}","line",2,"6 6",True)+arrow(380,y+74,"down")
    b+='<g data-kind="android-e2e-judge">'+rect(38,600,684,58,"#14243a","#344967",14)
    b+=text(58,627,"lumos android-e2e judge",20,"green",weight=650)
    b+=text(58,649,"Reads every step's output and decides pass or fail" if en else "讀每一步的結果，判過不過",15 if en else 16,"muted")+'</g>'
    b+=path("M380 658V672","line",2)+arrow(380,676,"down")
    b+='<g data-kind="android-e2e-record">'+rect(38,680,684,96,"#14243a","#344967",14)
    b+=text(58,710,"Verification record" if en else "查證紀錄",22,"green",weight=650)
    b+=text(58,734,"Change the app code, a flow, a baseline or a threshold → run again" if en else "改了 App 程式、流程檔、基準圖或門檻 → 紀錄失效、要重跑",14 if en else 15,"muted")
    for j,(lab,c) in enumerate((("0 passed" if en else "0 通過","green"),("1 failed / not judged" if en else "1 沒過或沒判完","coral"),("2 no record" if en else "2 沒寫紀錄","gold"))):
        b+=badge(58+j*214,742,lab,c,200)
    b+='</g>'
    b+=text(380,806,"Failed or slower → dig in layer by layer with the diagram above" if en else "沒過或變慢 → 照上一張圖一層一層往下查",15 if en else 16,"muted","middle")
    b+=text(380,832,"It does not block pushing yet; the push check is the next batch." if en else "目前還不會擋推送；推送前檢查是下一批。",15 if en else 16,"muted","middle")
    desc=("Android full check before push. A preflight checks the device, tools, and that the working tree is clean; if it fails the script exits with 2 and never touches the app. "
          "Five steps then run in order: build and install the app and record its fingerprint; tap through Maestro flow files, retrying once; compare screenshots with baselines a person approved at a 99.5 percent threshold; open and close a screen repeatedly to check leaks, crashes and StrictMode; and run Macrobenchmark against the saved baseline, which only warns. "
          "lumos android-e2e judge reads every step and writes a verification record tied to this version of the app code and test materials: exit 0 means passed, 1 means a part failed or could not be judged, 2 means no record was written. "
          "A failure or slowdown is investigated layer by layer with the evidence diagram. It does not block pushing yet.") if en else (
          "Android 推送前整套驗收。先做開跑前檢查：裝置、工具、工作目錄是否乾淨；不過就回 2，完全不碰 App。"
          "接著依序五步：建置並安裝 App、記下檔案指紋；Maestro 照流程檔點一遍，沒過重跑一次；拍畫面跟人看過的基準圖比，門檻 99.5%；反覆開關畫面查漏記憶體、閃退與主執行緒違規；Macrobenchmark 跟存好的基準比，只提醒。"
          "lumos android-e2e judge 讀每一步的結果，寫一份綁在這一版 App 程式與驗收素材上的查證紀錄：回 0 通過、1 有一塊沒過或沒判完、2 沒寫紀錄。"
          "沒過或變慢就照分層查證的圖一層一層往下查。目前還不會擋推送。")
    return title,856,b,desc

SCENES={"map":("00 / THE SYSTEM",map_scene),
        "drift-guard":("NOTES / DRIFT CHECKS",drift_scene),
        "first-change":("START / NATURAL LANGUAGE",first_scene),
        "graph-demo":("01 / KNOWLEDGE",graph_scene),
        "case-review":("CASE / REAL REVIEW",case_scene),
        "dispatch-overview":("02 / DISPATCH",dispatch_scene),
        "risk-review":("02-03 / REVIEW BY RISK",risk_review_scene),
        "review-overview":("03 / REVIEW",review_scene),
        "swiss-cheese":("QUALITY / FIVE LAYERS",swiss_cheese_scene),
        "android-e2e":("ANDROID / EVIDENCE BY LAYER",android_scene),
        "android-acceptance":("ANDROID / FULL CHECK BEFORE PUSH",android_acceptance_scene),
        "writeback-overview":("04 / WRITE-BACK",writeback_scene),
        "evals-overview":("EVALS / FEEDBACK",evals_scene)}

def validate_android(root,ns):
    """android-e2e 圖:四層依序是 L0 到 L3,輸入、記憶體捷徑、查證紀錄各一個。"""
    if root.find("s:title",ns).text not in set(ANDROID_TITLES.values()):
        return
    assert [el.get("data-layer") for el in root.findall(".//*[@data-kind='android-layer']")]==["L0","L1","L2","L3"]
    for kind in ("android-inputs","memory-shortcut","android-record"):
        assert len(root.findall(f".//*[@data-kind='{kind}']"))==1, kind

def validate_android_acceptance(root,ns):
    """android-acceptance 圖:開跑前檢查、五步依序、判定、查證紀錄各一個。"""
    if root.find("s:title",ns).text not in set(ANDROID_ACCEPTANCE_TITLES.values()):
        return
    assert [el.get("data-step") for el in root.findall(".//*[@data-kind='android-e2e-step']")]==["1","2","3","4","5"]
    for kind in ("android-e2e-preflight","android-e2e-judge","android-e2e-record"):
        assert len(root.findall(f".//*[@data-kind='{kind}']"))==1, kind

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
    if root.find("s:title",ns).text in {"Multiple checks, complementary coverage.","多層檢查，補足各自的盲點"}:
        assert len(root.findall(".//*[@data-kind='defence-layer']"))==5
        assert len(root.findall(".//*[@data-kind='aligned-escape']"))==1
        assert len(root.findall(".//*[@data-kind='escape-ledger']"))==1
    validate_android(root,ns)
    validate_android_acceptance(root,ns)
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
