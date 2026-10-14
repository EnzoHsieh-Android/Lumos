---
type: project
status: doing
created: 2026-10-14
updated: 2026-10-14
tags:
  - type/project
  - status/doing
  - scope/loop-engineering
related:
  - "[[Projects/世界解重新註解2026-10_總覽_調研]]"
  - "[[Projects/世界解重新註解2026-10_迴圈工程_調研]]"
lands_in:
  - Systems/pitfalls-code-loop
---
# 原生代碼審當通才席_計劃

> 白話:高風險代碼審裡「鏡頭5」那一席原本是自家派的同門通才。這篇把它換成 Claude Code 官方的 `/code-review`(在全新的無頭會談裡跑,官方怎麼審就怎麼審、跟著官方更新),再用一支轉換指令把它的結果變成 Lumos 收得下的席報告(每條有等級、逐字引句、佐證位置),照常進收貨、記帳與處置閘。

PRIOR-ART: 世界解總覽〈委派與照留地圖〉:代碼審「找問題」那段委派一部分給原生 `/code-review`、ultrareview 或 `codex review` 當額外一席,Lumos 留辯方、引句錨定、處置閘、凍結判定回放、擋推送([[Projects/世界解重新註解2026-10_總覽_調研]])。官方 `/code-review` 本機版的審法:八個角度(逐行、被刪行為、跨檔追呼叫者、重用、簡化、效率、整體、慣例)、最多 10 條、每條附檔案行號與失敗情境(2026-10-14 實驗讀到的派工詞)。外家席在本 repo 早有「`claude -p` 無頭跑一席」的先例(`skills/lumos-code-loop/SKILL.md` 第 2 步「外家席換 `claude -p`」);引句錨定、收貨三道、記帳格式沿用既有規則,不另立。

RETIRE-IF: 上線後累計 10 個高風險代碼審迴圈,原生審查席(帳上審查員名 `原生審查-sonnet`,對帳時家族算同門,比較靠審查員名)「存活且折入的 major」少於同期任何一個同門找問題席的一半,或它錨不到引句而被丟掉的發現超過三成,就換回同門通才席。

## 現況與實驗(2026-10-14)

- 高風險代碼審的編制(`scripts/lumos` 的 `_TIER_ROSTER` 裡 `("code", "high")`)有五個算人數的找問題席,第五席「鏡頭5」由同門通才補原外家 finder 的名額。
- 在暫存複本上對一個實際功能提交跑了五次 `claude -p "/code-review"`(sonnet,每次約 1.5–2 分鐘、0.2–0.4 美元,一般同門席約十幾萬 token):
  - 交回的形狀不固定:有時是編號清單(「`檔:行`:摘要」加「Failure scenario:」),有時是 JSON 陣列(`file`、`line`、`summary`、`failure_scenario`、`verdict`);語言有時中文有時英文。
  - 每條都沒有等級;用 `--append-system-prompt` 要它加等級欄位,兩次都沒照做;用 `--json-schema` 強制結構化時,斜線指令的結果不會交回(只回「Command completed」)。
  - 審的範圍是 `git diff @{upstream}...HEAD`,要先把被審分支的上游設成這輪的起點。
  - 第一次用全部放行的權限跑時出現一筆「推送」狀態事件(查證沒有東西被推上 GitHub),之後一律禁止 `git push`、`gh`、`git commit`。
  - 內容品質:五次都附實跑結果;其中「雙引號裡的反引號指令替換沒被判到」是剛合併的功能真的漏掉的洞。

## 範圍

- 這篇:①高風險代碼審的鏡頭5 改成原生審查席;②新增轉換指令 `lumos seat-import code-review`;③手冊寫明怎麼跑、怎麼補等級、怎麼轉換。
- 不做:設計審(`/code-review` 審的是程式改動,不審計劃);standard 單席與 light(它們只有一兩席,換掉就沒有自家視角);ultrareview(要使用者觸發而且另外計費,編排者不能自己啟動);把審法抄進 Lumos(會凍結住官方的更新)。

## 做法

- **跑原生審查**(編排者照手冊的固定指令跑,Lumos 不自己派模型):
  - 在 `/tmp/lumos-seat-work/<迴圈>/原生審查-sonnet/` 用 `git clone --shared` 建複本、切到這輪的頂端提交,另建一條指向這輪起點的分支設為上游,讓 `/code-review` 審的就是這輪的範圍。
  - 在複本裡跑 `claude -p "/code-review" --output-format json --model sonnet --permission-mode bypassPermissions --disallowedTools "Bash(git push:*)" "Bash(gh:*)" "Bash(git commit:*)"`,輸出存成 `raw.json`。全新的無頭會談不帶編排者的脈絡,席位獨立性跟派全新子代理一樣。
- **補等級**(原生審查不給等級):先用 `lumos seat-import code-review --raw raw.json --list-only` 只解析、印出清單(JSON),再把清單交給另一次無頭呼叫(`claude -p --model haiku --json-schema`,結構化輸出對一般提示有效),依固定規則逐條判:會做錯行為、破壞合約、資料損壞或可被利用的是 major,會造成無法還原的損害的是 blocker,命名、風格、效率、文件精度是 minor;取輸出的 `structured_output`(形狀 `{"severities": [...]}`,長度與順序同清單)存成 `severity.json`。補等級的是另一個沒有編排者脈絡的模型,算審查員層宣告;編排者不改它,要放行照處置閘的既有規則附理由(兩層不互改)。
- **轉換指令 `lumos seat-import code-review --raw raw.json --severity severity.json --snapshot <凍結 patch> --repo <複本> --out <席報告>`**:
  - 解析:認 JSON 陣列(在 result 文字裡的 ```json 區塊或整段)與編號清單(每條頂格「編號. `檔:行`:摘要」,檔名行號可包粗體;失敗情境多行保留換行)兩種形狀。編號清單裡有頂格的編號行認不得 → 整份 rc2(不默默丟掉一條、也不讓它的內容併進上一條)。官方明說沒有發現(整段或整個 JSON 區塊是 `[]`,或寫明 no findings/沒有發現)→ 產出 clean 報告。其他抽不出 → rc2,原文另存成 `<報告>.unparsed.txt`,不產生席報告。
  - 等級:`severity.json` 的條數要等於解析出的條數(含之後錨不到的那些)、每條只能是 blocker/major/minor;不符 → rc2。
  - 引句:照每條的檔案與行號,在複本裡讀那一行;那一行去掉首尾空白後至少 10 字、跟凍結 patch 裡某一行(去掉開頭的 `+`/`-`/空白與首尾空白)完全相同、而且不含「」(引句格式用的括號),就當引句;否則依上 1、下 1、上 2、下 2、上 3、下 3 行的順序找第一行符合的;都找不到就列進報告末尾的「錨不到」段(不寫 severity 行,照規則不採信)。
  - 產出的席報告照既有格式:第一行檔級 `severity:`(取有引句的發現裡最高的,一條都沒有就 clean)、每條可採信的發現恰一行 `severity:`、一行 `blocking:`(minor↔否、major/blocker↔是)、一行 `引句:「…」`、一行佐證位置 ``file: `路徑:行號` ``、摘要與失敗情境原文照抄(不翻譯、不改寫),原生判定有就附上(CONFIRMED=官方審查自己實跑證實,PLAUSIBLE=推論)。報告開頭註明來源、跑的完整指令、等級由誰補。
- **編制**:`_TIER_ROSTER` 的 `("code", "high")` 鏡頭5 備註改成「原生審查席(Claude Code /code-review,轉換後收貨)」;席名 `原生審查-sonnet`。
- **手冊**:`skills/lumos-code-loop/SKILL.md` 第 2 步與 `skills/lumos-design-loop/templates.md` 新增一節〈原生審查席〉寫上面三段指令;收貨、記帳照既有規則。

## 驗收條款

- [S1] 當原生審查輸出是 JSON 陣列或編號清單(檔名行號可包粗體)時,`lumos seat-import code-review` 應 解析出每一條的檔案、行號、摘要、失敗情境(多行保留換行)與原生判定,原文不改,`--list-only` 應 只印清單;編號清單有認不得的頂格編號行、或形狀都不認得時 應 rc2、不產生席報告並另存原文;官方說沒有發現時 應 產出 clean 報告 [test:t_seat_import_code_review]
- [S2] 當 `severity.json` 條數不等於解析出的條數、或含 blocker/major/minor 以外的值時,轉換 應 rc2;條數相符時每條 應 帶對應等級,blocking 應 跟等級一致 [test:t_seat_import_code_review]
- [S3] 當發現的那一行(或上下 3 行內依序最先符合的一行)去掉首尾空白後至少 10 字、跟凍結 patch 的某一行完全相同、不含「」時,應 用它當引句;都找不到時 應 列進「錨不到」段、不寫 severity 行,全部錨不到時報告 應 是 clean;有可採信發現的席報告 應 通過 `lumos report-normalize` 與 `lumos quote-check` [test:t_seat_import_code_review]
- [S4] 當讀高風險代碼審編制時,鏡頭5 應 標成原生審查席 [test:t_seat_import_roster_slot]
- [S5] 當編排者照手冊跑原生審查席時,應 禁止 `git push`、`gh`、`git commit` 並在獨立複本裡跑 [manual:讀 lumos-code-loop 與 templates 的〈原生審查席〉,確認三段指令與禁止清單齊全]

## 回退

- 編制改回同門通才:把 `_TIER_ROSTER` 鏡頭5 的備註還原,手冊那一節刪掉;轉換指令留著不影響其他流程。

## 實務隱患

- 已排除:金流:只產生審查報告,不碰付款或計費。
- 已排除:對外送出:原生審查禁止推送與 `gh`,只在暫存複本裡讀碼;無頭呼叫打的是本來就在用的模型 API。
- 已排除:不可逆:轉換只寫一份席報告到卷證目錄,可刪可重產。
- 已排除:守衛面:處置閘、引句錨定、收貨三道全照舊;換掉的是一席找問題的人,不放寬任何判定。
- 原生審查的輸出形狀可能隨官方更新改變:轉換指令認不得就 rc2 擋下,不會產生殘缺的報告;編排者這輪改派同門通才補位。
- 補等級的模型可能判錯:等級是審查員層宣告,編排者不改它;判讀時認為誤判,照處置閘既有規則附理由放行(minor 才能放行,major 一律折),理由寫進收貨紀錄。轉換只負責搬運、不改原文。

REVISIT:2026-11-30 回看這段期間高風險代碼審裡原生審查席的存活 major 數、錨不到比例與成本,對照 RETIRE-IF 決定留或換回

## 審計修正紀錄
