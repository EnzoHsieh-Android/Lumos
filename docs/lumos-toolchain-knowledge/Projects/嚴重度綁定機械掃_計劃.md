---
type: project
summary: |-
  FLAG:TECHNICAL
  KEY:地基盤點第 3 批案 D——新收斂制地基假設「席報告的 severity 標籤↔帳面 --severity 忠實轉錄」至今零機械守衛(僅人工核過 0/18);★r1 外家否決成立(2026-08-26),層次反轉重寫:寫側為第一層★:[S1] record 寫側強制(生效日後帶 --report 的新帳列:報告 parse 不到合法 severity 宣告或帳面≠報告最高=拒絕入帳 rc2;嚴格整行 regex 天生排掉引句/blockquote 逃逸)[S2] severity-check 掃描器降第二層(歷史帳 advisory+新帳縱深重驗,抓到=寫側 bug 開 Issue)[S3] 併入 --disposal 尾端(轉述帶「觀測不進合取」字樣;留痕併入 roster-alerts.log 不開孤兒檔)[S4] 歷史首驗(08-25 起全量)
  DEP:[[Systems/loop-convergence-recording]]｜[[Projects/地基盤點2026-08-26_調研]]
status: doing
created: 2026-08-26
updated: 2026-08-26
tags:
  - type/project
  - status/doing
---

# 嚴重度綁定機械掃_計劃

> 白話:整套新收斂制信一件事——記帳的人把審查員講的最嚴重等級照實抄。這件事現在靠自律。r1 外家把原案(只做事後掃描)否決掉了:掃描器抓到的時候閘已經放行,而且「報告乾脆不寫等級」就掃不到。反轉後的做法:**入帳那一刻就擋**——新帳列的報告裡沒有機器讀得懂的等級宣告、或帳面跟報告對不上,直接拒絕記帳;掃描器降級為歷史帳的補掃跟縱深保險。

PRIOR-ART: borrow——同 repo 的 quote-check/refcheck/seat-check 收貨三道就是「報告↔帳」機械對帳的現成模式,本案第一層是寫側前置驗證(比照 record 既有 --severity choices 白名單的「入口擋」哲學,往內容層延伸一步),第二層才是收貨型掃描(severity 維度的第四道);報告檔已凍結入帳(path+sha256),parse 基礎全在。

## 現況事實

- 帳列有 severity(寫側白名單擋值域)、report{path,sha256}。席報告格式★不★一致:2026-08-26 普查 59 份,41 份用「severity: <值>」獨立行,但外家席(codex)報告慣用「### id / 等級 / 標題」表頭、全篇零獨立行——恰好是掛否決權重、最需要機械驗的席(r1 兩席獨立實測證偽了「全部報告皆此格式」的原始前提)。收貨轉錄時要把表頭型正規化成獨立行(與引句正規化同一步驟)。
- 綁定驗證現況=編排者自律;人工核僅一次(0/18);disposal 閘不驗此維度——低報 severity 可讓 major 變 minor 逃過「code-* major 必折」鐵則。

## 條款

- **[S1] record 寫側強制(第一層,硬擋)**:`canary record` 凡帶 --report 的新帳列(生效日=本案實作合入日,程式內常數;ts 在生效日前的舊帳不溯及)入帳前驗:讀報告檔(此時本來就要算 sha),parse 全部嚴格整行 `^severity:\s*(clean|minor|major|blocker)\s*$`(大小寫、全形冒號、行首多餘字元一律不認,fixture 釘變體),取最高;帳面 --severity 必須==報告最高,且至少 parse 到一行——parse 不到或不等=**拒絕入帳 rc2**,訊息指路「先把報告 severity 行補齊/對正再記」。嚴格整行錨定天生排掉兩型逃逸(r1 兩席各抓一型):引句行(以「引句」標籤起頭,整行不可能匹配)與 blockquote(以 > 起頭,同理)——不需要任何「排除引句行」啟發式;fixture 各釘一個逃逸樣本。值序抽模組常數 `_SEV_ORDER`(既有三處字面複製回填,不開第四份)。
- **[S2] severity-check 掃描器(第二層,advisory)**:`lumos severity-check --loop <id> --round <rN> --auditor <席>`——吃帳列座標不吃檔案路徑(對帳對象是帳列;resolver 複用 loop status 既有 loop/round 篩選,單一實作——這是四道收貨裡第一個吃座標的介面,理由在此交代)。生效日前的歷史帳=純 advisory(格式掃不出=提醒,相容);生效日後的新帳=縱深重驗,抓到低報=**寫側有 bug**(第一層本應拒帳),紅字轉述+開 Issue 攤人;converged 不自動撤(撤=改閘語意,另案過審)。standalone 模式自驗報告 sha 與帳面一致;被 disposal 尾端呼叫時信合取③已驗過(旗標跳過,不對同一檔重算兩遍雜湊)。
- **[S3] 併入 --disposal 尾端(異常才發聲)**:問閘收尾對判定輪逐席跑 [S2],比照 roster 尾端(try/except 降級、__seqN 合成鍵跳過、advisory 恆不動 rc);轉述行必帶「(觀測,不進合取)」免責字樣(canary 觀測段已有先例,roster 尾端漏了——本案順手補上同款,一行);留痕★不開新檔★——寫進既有 `roster-alerts.log` 同一寫入路徑,kind=`severity_underreport`(第二個沒人讀的孤兒檔比一個更容易被忘;檔名沿用,定位升為「問閘尾端異常留痕簿」,Systems 筆記記一句)。
- **[S4] 歷史首驗**:對 2026-08-25 起全部 d5 迴圈帳列跑 [S2] 歷史掃,結果入本案驗證紀錄(0/18 的人工核升級成 n/全量的機械帳)。
- 邊界:寫側新增「入帳前置驗證」(★推翻原「不動記帳寫側」邊界——r1 外家否決層次倒置成立★),但不動 severity 值域白名單、不動閘判定布林;生效日前舊帳一律豁免(機械時間邊界,不靠人判「新舊」);報告格式正規化發生在收貨轉錄(既有步驟),不是掃描器去適配百家格式。

## 行為斷言

fixture:【寫側】新帳列報告 blocker+帳 minor→拒帳 rc2 指名差異;報告無 severity 行→拒帳 rc2;報告 minor+帳 major(高報)→拒帳 rc2(不等就擋,方向不豁免);生效日前舊帳→不驗照收;引句行/blockquote 內含 severity 字樣→不計入 parse(逃逸樣本各一);全形冒號/大小寫變體→不認。【掃描器】歷史帳低報→紅字轉述+rc 不變;新帳低報→轉述行標「寫側 bug」;sha 不符→拒掃指路 quote-check;尾端轉述行帶「(觀測,不進合取)」且 rc 不變(打樁);歷史掃跑完出統計行;留痕落 roster-alerts.log 且 kind=severity_underreport。

## 實務隱患

- 守衛面:第一層(寫側)天生是硬擋(拒帳 rc2),不存在「等掃描器抓到才升級」的循環空窗(r1 外家 ext-f4 指的循環盲點因此不成立於新案);第二層 advisory 恆不動 rc。已排除:金流/對外/不可逆。
- 誠實邊界(r1 外家 ext-f2 折入):報告與帳同出一個編排者之手——寫側強制擋的是**疏忽轉錄錯**(這是 0/18 人工核想防的那類),不擋有意共謀(同時改報告文字與帳面值做平);對抗性造假歸既有 [audit:] 獨立審計層,本案不宣稱防對抗。
- 回頭條件(機械):2026-11-26(與 roster 覆核同日)數 `roster-alerts.log` 的 `severity_underreport` 條目——任一條=寫側有 bug,當場開 Issue 攤人;零條=第二層掃描器+尾端一併重審是否退場(寫側 fixture 常駐測試網,不在重審範圍)。

## 審計修正紀錄

- r1(2026-08-26,五席+外家,外家否決成立;16 條全折零放行(2+2+4+4+4 逐席機械數),整案層次反轉重寫):
  - ext-f1+ext-f3(2 blocker:「parse 不到=不紅」是明文設計的逃逸門+層次倒置,寫側才是該擋的入口)→ 整案反轉:[S1] 改為 record 寫側硬擋(拒帳 rc2),掃描器降第二層;原「不動記帳寫側」邊界推翻。
  - s1-f1+s2-f1(2 blocker,兩席獨立實測:ext 席報告零 severity 獨立行,「全部報告皆此格式」前提已被本日真實資料證偽)→ 現況事實改寫;收貨轉錄正規化表頭型;寫側強制讓新報告缺行=拒帳而非靜默提醒。
  - s1-f2+s2-f2(2 major:blockquote 引句格式錨不到排除規則/引句行尾可藏真宣告)→ 廢除「排除引句行」啟發式,改嚴格整行 regex(兩型逃逸天生排除),fixture 各釘樣本。
  - s3-f1(blocker:偵測時機在 PASS 定案後,converged 已被 loop next 消費,無事後程序)→ 寫側前置讓低報進不了帳;第二層抓到=寫側 bug 開 Issue 攤人,converged 不自動撤(明文)。
  - ext-f4(major:升級條件循環盲點)→ 寫側即硬擋,循環空窗不存在(明文記於守衛面)。
  - ext-f2(major:自我對帳威脅模型)→ 誠實邊界明文:擋疏忽不擋共謀,對抗歸 [audit:]。
  - s3-f2(major:回頭條件散文)→ 改機械條款:2026-11-26 數 severity_underreport 條目,判準明列。
  - s3-f3+arch-f3(major+minor:第二個孤兒留痕檔)→ 不開新檔,併入 roster-alerts.log 加 kind。
  - s3-f4(major:尾端輸出與合取難分辨)→ 轉述行帶「(觀測,不進合取)」,並順手補 roster 尾端同款。
  - arch-f1(minor:座標介面背離「傳路徑」先例)→ S2 明文交代理由(對帳對象是帳列)與 resolver 複用。
  - arch-f2(minor:值序第四份複製)→ 抽 _SEV_ORDER 常數,三處回填。
  - arch-f4(minor:sha 重複驗)→ 尾端呼叫時信③已驗,旗標跳過。
