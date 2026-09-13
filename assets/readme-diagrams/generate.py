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
    title="Context, action, feedback." if en else "讓每次改動，都接得上下一次"
    b=path("M74 156H674Q720 156 720 205V491Q720 544 669 544H89Q40 544 40 495V217Q40 156 74 156","coral",2.5,"12 8",True)
    b+=rect(203,129,354,50,"#111f34","#6a4c56",16)
    b+=text(380,162,"evals · Evaluate & calibrate" if en else "evals · 評測與校準",23,"coral","middle",600)
    b+=path("M40 205H199V229","coral",2)+arrow(199,230,"down","coral")
    b+=rect(58,185,275,29,"#122038","none",6)+text(68,207,"Calibration feeds back" if en else "校準後回到開發",21,"coral")
    b+=path("M572 452V535","coral",2)+arrow(572,543,"down","coral")
    b+=rect(421,481,286,33,"#101c30","none",6)+text(565,505,"Each round leaves records" if en else "每輪留下紀錄",21,"coral","middle")
    # Clear clockwise station loop; text never fades.
    b+=path("M324 271H428","blue",2,"12 8",True)+arrow(437,271,"right","blue")
    b+=path("M563 309V366","purple",2,"12 8",True)+arrow(563,372,"down","purple")
    b+=path("M436 410H332","gold",2,"12 8",True)+arrow(324,410,"left","gold")
    b+=path("M197 372V319","green",2,"12 8",True)+arrow(197,309,"up","green")
    nodes=[(70,231,"01", "Notes" if en else "圖譜","Retrieve context" if en else "查回相關脈絡","green","search"),
           (436,231,"02","Dispatch" if en else "派工","Independent views" if en else "不同角度獨立看","blue","fork"),
           (436,372,"03","Review" if en else "審查","Challenge evidence" if en else "檢查改動與依據","purple","shield"),
           (70,372,"04","Write-back" if en else "寫回","Keep the reasoning" if en else "留下決策與驗證","gold","note")]
    for x,y,n,t,s,c,i in nodes:
        b+=rect(x,y,254,80)+text(x+22,y+32,t,26,c,weight=600)+text(x+22,y+60,s,19)
    b+=text(380,346,"LUMOS",14,"muted","middle",650)
    b+=text(380,589,"Development inside. Evaluation around it." if en else "內圈做開發，外圈評估並校準。",22,"muted","middle")
    return title,620,b,"Four stations form a development loop. Records flow to evals; calibration returns to development. Decorative paths animate; all labels remain visible."

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
    b+=text(380,473,"Reviewers do not see one another’s reports." if en else "各席彼此看不到報告；一致不等於一定正確。",22,"muted","middle")
    return title,505,b,"The same change, context, rules and evidence fan out to independent review perspectives, then findings are accounted for as adopted, rejected or needing follow-up. Seats are illustrative."

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
      (230,"02","Multi-seat review" if en else "多席審查","blue",[(287,246,9),(405,265,13),(522,240,8),(590,255,10),(680,270,11)]),
      (310,"03","Disposition gate" if en else "放行規則","coral",[(305,340,12),(468,324,9),(590,335,10),(690,348,8)]),
      (390,"04","External rules" if en else "外部規則","gold",[(280,404,8),(390,430,12),(505,405,10),(590,415,10),(675,432,9)]),
      (470,"05","Failure-proven tests" if en else "測試翻紅","green",[(315,495,11),(445,480,8),(545,510,12),(590,495,10),(690,482,8)]),
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

SCENES={"map":("00 / THE SYSTEM",map_scene),
        "first-change":("START / NATURAL LANGUAGE",first_scene),
        "graph-demo":("01 / KNOWLEDGE",graph_scene),
        "dispatch-overview":("02 / DISPATCH",dispatch_scene),
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
