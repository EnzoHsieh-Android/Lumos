---
type: project
summary: |-
  FLAG:DECISION
  KEY:★Enzo 裁甲(2026-08-25,r1 攤牌後;decisions d1)★——多席 code-loop(含 high)收斂閘統一走處置閘(d5 型記帳),panel 轉純歷史回放;probe 抽查輪隨宿主退場(義務拔除、判定碼保留降觀測);防浮動條款具名處置:凍結句留(回放語意)、「20 筆抽查帳」通道正式作廢。程序=先裁後動(r1 五席 19 審項/blocking 15 攤牌在前)
  KEY:★d2(Enzo 第二裁)★:code-* 迴圈處置閘輪級加嚴——輪內任一席 severity ≥ major 則 accepted 必空(major 一律折),與 panel「max≤minor」同嚴度;散文維持 d5 現制。d4「防線不降級」由此成立
  KEY:r1 打穿 v1 前提——panel 非「僅舊帳回放」:多席現役唯一通閘(08-24 互斥案實據)且無 quote-check(收貨比處置閘薄),probe 為其唯一 PASS 後複核;教義互斥(08-08 被翻紀錄 vs SKILL 步驟7);本版=v2,範圍擴為路由統一+退場
  DEP:[[Issues/probe輪三參數只在散文]]｜[[Systems/convergence-evidence-gate]]
status: done
created: 2026-08-25
updated: 2026-08-25
tags:
  - type/project
  - status/done
decisions:
  - content: Enzo 裁甲(2026-08-25,r1 攤牌後):多席 code-loop(含 high)收斂閘統一走處置閘(d5 型記帳:各席留痕+一輪一筆彙總 carrier),panel 閘轉純歷史回放;probe 抽查輪隨宿主退場(義務拔除、判定碼保留降觀測)。此裁定同時具名處置防浮動條款:panel 判準凍結句保留(回放語意),「攢 20 筆抽查帳」翻案通道隨 panel 退役正式作廢——先例同 08-08 具名推翻與 canary 停用(皆業主先裁後動,本次亦然:r1 五席 19 審項/blocking 15 攤牌在前,實作在裁定之後)
    id: d1
    context: r1 揭露:panel 為多席現役唯一通閘且無 quote-check,probe 為其唯一 PASS 後複核;同時教義互斥(08-08 被翻紀錄寫 code-loop 改 disposal vs SKILL 步驟7 教多席 panel);今日三個多席 code-loop 已實跑 d5 型+處置閘單輪收斂
    why_chosen: 統一後多席收貨含 quote-check+留痕重驗(比 panel 厚);消除兩閘並存混淆面;probe 宿主退役後自然退場,零帳面遷移
    decided: 2026-08-25
    valid: false
    superseded_by: d3
    ended: 2026-08-25
  - content: Enzo 裁(2026-08-25,第二問):code-* 迴圈的處置閘輪級規則加嚴——輪內任一席 severity ≥ major 則 accepted 必須為空(major 一律折,不得附理由放行),與 panel 時代「存活 max≤minor」同等嚴度;散文設計審維持 d5 現制(僅 blocker 觸發輪級清空,non-blocking 可附理由接受)。由此 d4「防線不降級」成立:路由統一不放寬判準
    id: d2
    context: 外家 v2 否決席指出 panel 要求 max≤minor 而處置閘允許 major 附理由放行,路由統一未處理此差=實質放寬;攤牌後 Enzo 裁「code 迴圈加嚴,散文維持」
    why_chosen: code major=照字面會做出錯行為的實碼缺陷,必修不可談;散文 major 偶有正當接受場景且 d5 已裁,不回翻
    decided: 2026-08-25
    valid: true
  - content: Enzo 裁甲(2026-08-25,r1 攤牌後;本條=d1 佐證更正版,裁定本文逐字同 d1):多席 code-loop(含 high)收斂閘統一走處置閘(d5 型記帳),panel 閘轉純歷史回放;probe 抽查輪隨宿主退場(義務拔除、判定碼保留降觀測)。防浮動條款具名處置:凍結句保留(回放語意),「攢 20 筆抽查帳」通道正式作廢。程序=先裁後動(v2 r1 治理席以 git log 親驗:裁前零落地動作)
    id: d3
    context: 更正 d1 的佐證句:今日三個多席 code-loop 實為各兩輪(r1 折入+r2 delta)於上限內以處置閘收斂——d1 曾誤記「單輪收斂」,治理帳 governance-log 原文自證為兩輪,v2 r1 機械席逐帳抓回(「必逐檔數」又一犯);裁定實質不變
    why_chosen: 同 d1;佐證的正確版本:處置閘對多席 code-loop 三案皆在 cap 內收斂且引句紀律有效,非「單輪」
    decided: 2026-08-25
    valid: true
---

# probe輪退場_計劃

> 白話(v2,裁甲重寫):v1 以為抽查機制掛在一道已退役的閘上,審查證明那道閘還是多席審查唯一走得通的路——所以先攤給 Enzo 裁。裁定:多席審查統一改走處置閘(今天三案已實跑、各兩輪於上限內收斂、收貨更厚),舊閘轉純歷史回放,抽查輪隨之退場。本版把路由統一和退場一起落地。

PRIOR-ART:借用=①d5(散文審回歸處置閘,2026-08-25)之延伸——同一記帳型態(各席留痕+一輪一筆 carrier)今日已在三個多席 code-loop 實跑並於 cap 內收斂(各兩輪);②canary 停用模式(義務退場+判定碼保留+頁頂告示+專屬測試釘,2026-08-14)——v1 只借到前兩件,r1 arch 席指出缺後兩件,本版補齊;③08-08 具名翻案程序(先裁後動)。[[Issues/只退場不痛的機制]] 誠實標註:該篇立場是「退零成本機制不算本事」——本案退場的正當性不靠「零成本」,靠「宿主由裁定轉回放+接手路徑收貨更厚」(r1 s1 席對 v1 引用方向的糾正)。

## 症狀與裁定前現況(r1 修正版)

①教義互斥:[[Projects/panel收斂判準改革_計劃]] 被翻紀錄(2026-08-08,Enzo 具名)寫「code-loop 收斂改走 --disposal」;但 code-loop SKILL 步驟 7 現文教「多席 panel → --gate --panel」,且 2026-08-24 互斥案實據=多席各自記帳的迴圈**只能**問 panel(CLI 撞牆指路,scripts/lumos:10074 段)。②panel 收貨無 quote-check:`_panel_extra_checks`(scripts/lumos:3810 段)僅 min-seats+G3;quote-check 只在處置閘(10161 段)——高風險路徑反而最薄。③probe 抽查=panel PASS 唯一複核層,印行在 scripts/lumos:4019、4122 兩處;canary-log `"round": "probe-` 0 筆(機制落地三週、11 個 high panel 迴圈跑過,義務被印出過卻零執行)。④三配套參數(席可縮/不計 cap/限 1 次)程式碼零實作([[Issues/probe輪三參數只在散文]] 實證)。⑤今日對照組:三個多席 code-loop 以 d5 型記帳走處置閘,各兩輪(r1 折入+r2 delta)於 cap 內收斂、引句紀律有效——v2 曾誤記「皆單輪收斂」進裁定佐證,governance-log 原文自證兩輪,d1→d3 更正(「必逐檔數」又一犯);另註:08-08 被翻紀錄字面未限單席,實作只落到單席——多席真正可走處置閘始於今日 d1/d3,非 08-08。

## 核心裁定(本節 c 編號=正文局部;正式裁定=frontmatter decisions,現行有效 d2/d3——r2 席抓的撞號消歧義)

- **c1 路由統一(=decisions d3 前半)**:多席 code-loop(含 high)一律 d5 型記帳(各席一筆留痕無 set+一輪一筆彙總 carrier)問 `--disposal`;panel 閘(--gate --panel)轉**純歷史回放**(判定碼、K=2、兩條合取原樣保留供舊帳重放)。高風險 high 分級的「多席不同鏡頭」編制不變——變的只是記帳型態與問閘指令。
- **c2 probe 退場(=decisions d3 後半)**:義務拔除(skill 不再要求 PASS 後加開 probe-* 輪);判定碼保留降觀測——**「應抽」分支整句改寫**(非追加,r1 三席同抓自我矛盾風險):「本輪落在應抽樣(觀測;2026-08-25 起 panel 僅回放、不再加開 probe 輪,詳 Issues/probe輪三參數只在散文)」;「免抽」分支同步加(觀測)註記。歷史回放時 probe-* 輪 major 使 K=2 窗 FAIL 的機械語意不動(不依賴三參數,r1 s2 席行為級驗證)。
- **c3 防浮動條款(具名處置,見 decisions d3 原文)**:「判準凍結」句保留(語意=回放判準不漂);「唯一翻案通道=攢滿 20 筆抽查帳」正式作廢——由 Enzo 本裁定具名處置,非本案自行剪線;因果誠實版:feeder 實質停擺始於多席實務轉處置閘,本裁定將其正式化(r1 arch 席時點修正)。
- **c4 防線不降級(v3,以 decisions d2 為地基)**:嚴重度門檻——處置閘原制允許 major 附理由放行(panel 要求存活 max≤minor),路由統一若不處理=實質放寬(ext 席否決點)→**d2 已裁:code-* 迴圈輪內任一席 ≥ major 則 accepted 必空**,與 panel 同嚴度,「不降級」由裁定兌現而非論證話術。收貨密度——處置閘逐輪全查(quote-check+留痕 sha 重驗+refcheck+intake 機械重現),panel 連 quote-check 都沒有;不宣稱兩者為等價 oracle。**誠實承認一項真實變化(r1 s1 席 D)**:panel 的 K=2「連續兩輪乾淨」完整性要求對多席一併消失,處置閘一輪清空即過——部分補償=d2 使 major 必折+r2 delta 回歸實務慣行(今日三案皆自發跑了第二輪);回頭條件:下一個真實 high 迴圈若單輪收斂、事後(CI/生產/後續審)抓到該輪漏網 ≥major→開 Issue 重估「多席最低輪數」。

## 落地件

1. [S1] code-loop SKILL.md:步驟 2「只在 high 的 panel」改「只在 high 的多席編制(記帳與問閘見步驟 6-7)」——消歧義(三席同抓:panel 一詞從指令語意切到編制語意會打架);步驟 7 改寫——多席行改「多席同輪照步驟 6 的 d5 型記帳(彙總掛一席)→ 同問 `--disposal`;`--gate --panel` 僅供 2026-08-25 前已定錨 panel 帳的舊迴圈回放」;刪「PASS 訊息若印『應抽查』,要再開一輪 probe-* 抽查(材料全量、不計上限、抽出 major 自動撤銷收斂)才算做完」義務句(原句在步驟 7,grep「再開一輪 probe」現檔 1 命中);護欄「舊制 panel…K=2」句補「(含 high;2026-08-25 甲裁後多席亦處置閘)」。
2. [S2] scripts/lumos 三件:①4019/4122 兩處印行整句改寫(c2 措辭;「要——加開一輪…」句刪除);②**panel 閘新迴圈 cutoff 拒判**(首筆 ts ≥ 2026-08-26 的迴圈問 --gate --panel 一律拒+白話指路 d5 型記帳問 --disposal;env 覆寫供測試——照 K=2 cutoff 既有模式;10074 段擋下訊息同步改寫:對新迴圈不再給可複製的 panel 指令,s2 席抓的「補句不改指令=路由虛設」);③**code-* 嚴格輪級規則(d2)**:處置閘輪內任一席 severity ≥ major → accepted 必空(以 loop 編號 code- 前綴判;散文迴圈維持 blocker 門檻)。**行為級三釘 t_panel_probe_retired**:(a)新迴圈問 panel 被拒且訊息含指路 (b)code-* 迴圈 major 席+非空 accepted → disposal FAIL;散文迴圈同況 PASS (c)舊迴圈(cutoff 前)panel 印行含新觀測句、不含「才算做完」。t_loop_status_disposal_panel_routing 期待值同步(其現斷言=指回 panel,與新路由反向);t_panel_k2_and_probe 兩處「抽查」斷言同步(anchor approve 留痕)。**已知限制誠實列**:閘機械上無法對帳「carrier 是否收齊各席 findings」(帳面無逐席 finding 清單)——證據=各席報告 sha+rN-intake,不假裝有機械擋;**回頭條件(r2 席補,鐵則 4)**:每個 code-loop 收尾時編排者在 rN-intake 記一行「各席 findings 數 vs carrier 收錄數」對帳;連兩案出現漏收→立 Issue 議 record 端加逐席 finding 清單欄。
3. [S3] **skills/lumos-code-loop/reference.md 全面同步(v2 最大漏列,三席+外家同抓)**:§4(307-402:328 問收斂指令/347-365 端到端範例/371 K=2+抽查義務/383/399)整節照 2026-08-25 既有活範本(design-loop reference:252 路由句式)改「僅供已定錨舊迴圈回放」+範例改 d5 型記帳問 --disposal;design-loop reference.md:180、:332 與 :374 三處現行章節敘述同步(r1 s2 席逐行定位;v1 誤指「舊制章節」);convergence-evidence-gate KEY 補裁定事實句+頁頂 ⛔ 告示(**照 canary 四段結構**:標題帶裁定日期與決策 id/理由/落地實證/重啟-回放條件,arch 席補齊要求);[[Projects/panel收斂判準改革_計劃]] 補**第二段**被翻紀錄(明寫與 08-08 段是兩件事:那次=閘切換,本次=多席路由統一+probe 退場+通道作廢);Issue 結案橫幅;code-loop 指令檔(06)同步問閘行。
4. [S4] 本案兼 [[Projects/迴圈摩擦三修_計劃]] S4 實測載體,兩輪數據(r1 攤牌輪+v2 輪)一併回寫該案驗證。

## 行為斷言(每條配例;r1 修正 grep 基準)

- 例1:`grep -c "再開一輪 probe" skills/lumos-code-loop/SKILL.md` 現檔 1→落地後 0;`grep -c "僅供.*舊迴圈回放" skills/lumos-code-loop/SKILL.md` 現檔 0→落地後 ≥1。
- 例2:`grep -c "不再加開 probe 輪" scripts/lumos` 現檔 0→落地後 2;「要——加開一輪」字樣落地後 0(整句改寫非追加)。
- 例3:t_panel_probe_retired 行為級三釘各自可翻紅:(a)新迴圈問 panel 拒判 (b)code-* major+accepted→FAIL 且同構散文案 PASS (c)舊迴圈印行新句;另 disposal PASS 輸出不含「抽查」。
- 例4:reference.md:180 與 :374 區域落地後含「回放」語意字樣;`grep -c "判準凍結" Systems/convergence-evidence-gate 對應檔` ≥1 且原句逐字仍在(落地後實測=2:⛔ 告示自引該詞屬預期——cpr r1 arch 席訂正斷言目標)。
- 例5:canary-log `"round": "probe-` 維持 0(零帳面遷移)。

## 實務隱患

- **high 多席改 d5 型記帳的實務未跑**:今日三案多席=1 主審+1 arch(2-3 席),high 的 4-5 席 carrier 彙總未實測——回頭條件:下一個真實 high 迴圈([S4] 之後首個)驗 carrier 彙總在 5 席規模下的可操作性;跑出問題升 Issue。
- **panel 回放路徑長期無人踩**:判定碼保留但未來零使用=死碼累積——與 canary 同款處置(封存不拆);若兩季後回放零次,另案議拆——回頭條件掛本案落地 Verification 的 revalidate_when(stale 掃描只認 Verification/ 路徑,s3 席讀碼實證;canary 先例其實是 KEY 散文句非此欄位,「同款」只借形不借掛法)。
- REVISIT:2027-02-25 panel 回放兩季使用檢視(零次→另案議拆;上行條款)
- **印行改寫觸及 t_panel_k2_and_probe**:該測試只斷言「抽查」子字串與冪等(r1 s2 席實測)——新句保留「抽樣」字樣但「抽查」二字被改掉會紅!落地時先跑該測試,紅則同步其斷言字串(anchor approve 留痕)——明列,不是靜默改測試。
- **金流/對外/不可逆**:不涉及;全部可 revert(兩處印行+散文+一支新測試)。

## 審計修正紀錄

- r1(2026-08-25,5 席:s1 通才/s2 機械/s3 治理/arch/ext=Codex):19 審項/blocking 15(blocker 3)/一句結論:v1 前提「panel 僅回放」被三份 08-24 文件+實碼打穿(panel=多席現役唯一通閘且無 quote-check)、程序搶跑違反兩先例(皆先裁後動)、落地件三處定位錯——**不折不閘,攤人**;Enzo 裁甲(路由統一+退場+條款具名處置),密度+前提級觸發整份重寫(本版=v2),原編號 rewrite 收尾入治理帳(第二筆真實血緣事件)。
- 詳帳:`governance/review-reports/probe-retire/r1-*.md`+r1-intake.md(收貨:s1/s2 全錨、s3/arch 註記格式由編排者逐主張核原文、ext 一句快照巢狀截斷機械重現)。

- r1@v2(2026-08-25,5 席:s1 通才/s2 機械/s3 治理/arch/ext=Codex):18 審項/blocking 11/一句結論:v1 十五條核銷(九組乾淨一組半);新洞=判準放寬(d2 裁定補正)、code-loop 自家 reference §4 整段漏列、「皆單輪收斂」進裁定佐證被治理帳自證為兩輪(d1→d3 更正)、10074 指路虛設(改 cutoff 拒判)、K=2 第二輪消失(d4 誠實承認+回頭條件)——**全數折入零放行**(blocker 席在輪,accepted 必空);「先裁後動」治理席 git log 親驗成立。
- 詳帳:`governance/review-reports/probe-retire-v2/r1-*.md`+r1-intake.md。★r1 記帳自首:編排者曾在未跑 quote-check 時於 intake 寫「全數錨定」——處置閘 quote 關抓包(carrier 實際 0 句可抽);intake 誠實重寫,r2 delta 輪修復閘判。收貨檔慣例無機械守衛的首個反面教材,回寫迴圈摩擦案 [S4]★

## 下一步

probe-retire-v2 r1 審本版→過閘→[S1]-[S3] 實作→code-loop→推送;[S4] 兩輪數據回寫迴圈摩擦案並判其結案。
