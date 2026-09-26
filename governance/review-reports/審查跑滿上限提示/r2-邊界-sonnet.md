severity: major

## F1 「各席報的都是 0 條 → 算折 0」用錯欄位,會把合法通過的空輪誤判成「沒記處置」
severity: major
blocking: 是 — 判準:照 spec 字面實作,「有沒有彙總帳/算不算空輪」這一步會用 `_review_yield_round` 的 N(彙總 `reported` 欄)當「這輪找到幾條」的依據;但處置閘自己判定「空輪」用的是另一個欄位 `findings`,兩者語意不同、可以互相背離,實作者照字面做會產出跟處置閘實際判定相反的訊息。
引句:「各席報的都是 0 條 → 算折 0(處置閘本來就把它當合法的空輪)」
file: `scripts/lumos:7374-7377` — `_review_yield_round` 的 N 是加總每筆 `r["reported"]`(`reported` 是從 `--report` 檔案文字機器算出的「草稿裡列了幾條」,寫在 `scripts/lumos:7886` `rec["reported"] = _report_reported_count(_rtext)`)。
file: `scripts/lumos:18352-18376` — 處置閘判「空輪(vacuous)」用的是 `_findings_zero(r)`,讀的是 `findings` 欄(辯方裁決後存活的真數;`scripts/lumos:30712-30713` `--findings` 沒有預設值,不填就是 `None`);`_findings_zero` 明寫「沒填 ≠ 明說 0」,`None` 一律當非空輪處理。`carrier is None` 分支只有 `all(_fz)`(每筆都明確 `--findings 0`)才判 vacuous、印「✓ 這輪 0 條發現」;否則印「✗ 判定輪有發現但無處置帳」、`fails.append("無處置帳")`。
重現場景:一輪三席各自的 `--report` 草稿都列了發現(`reported`=2、3、1,N=6>0),但辯方對質後全部折損/駁回,三席都明確帶 `--findings 0` 收尾、沒有人提交 `--findings-set` 彙總帳。這一輪處置閘的實際結果是 **PASS**(vacuous 空輪,`carrier is None` 且 `all(_fz)` 為真)。照 spec 這一段字面實作,cap 報告只看 N(=6,非 0),就會落到「有人報了條數卻沒有彙總帳 → 印『這輪沒記處置』」這一支——對一輪已經合法過關的輪次印出「沒記處置」的錯誤診斷,而且會連帶讓 S5/S12 的「折入數走勢」比較拿到錯的分子(用 N 而非處置閘認定的折 0)。
反過來也成立:三席報告草稿都空手(`reported`=0)但沒有人明確帶 `--findings 0`(疏漏),N=0 照 spec 判「折 0」,但處置閘實際上會判「✗ 無處置帳」FAIL——cap 報告會把一輪真正 FAIL 的輪次講成「合法空輪」。
要修:S7 的空輪判準必須跟處置閘同源,即檢查「該輪逐筆 `findings` 是否都明確為 0」,不能拿 `_review_yield_round` 的 N(reported 欄加總)當代理。

## F2 提早熔斷只綁在「處置閘輸出」,主要驅動介面 `loop next` 在跑滿之前永遠看不到
severity: major
blocking: 是 — 判準:RETIRE-IF/PRIOR-ART 講的「連續被擋或累計量過大就退回給人」的重點是「早」;但照 spec 字面分工,實作者會把熔斷字串寫進 `--disposal` 專屬路徑,而 `loop next` 只在真正跑滿(phase==cap-reached)那一輪才組 cap_report——熔斷這個「不等跑滿」的機制,在日常真正驅動迴圈前進的工具上完全不會出現,直到跑滿為止都是靜默的,等於熔斷形同虛設,是會讓實作者做出「設計了但派不上用場」的系統。
引句:「欄累計超過 20 → 在處置閘輸出印」
引句:「`loop next` 回跑滿上限時:文字輸出與 `--json` 都要有」
file: `scripts/lumos:10336-10345,10663-10680` — `cmd_loop_next` 目前的委派段(未來改問處置閘後同理)把 `cmd_loop_status(...)` 的 stdout/stderr 整段 `redirect` 進 `buf`;只有 `rc==2` 才把 `buf` 內容吐到 stderr(`sys.stderr.write(buf.getvalue())`);`rc==1`(閘沒過但輪數未達上限,即熔斷已觸發但還沒跑滿的最常見狀況)那條路直接落進「④ plant-canary」,`buf` 內容(含熔斷那行)整個被丟棄、不印。
影響:這份計劃的一句話目標是「讓多席迴圈真的會說出『跑滿上限』」,操作者實際上是靠 `lumos loop next` 逐輪往前推(skill 文件寫「用 lumos loop next 派席」);要看到熔斷提示得另外手動多敲一次 `lumos loop status <id> --disposal`,但 spec 全文沒有任何一句要求或提醒操作者在跑滿之前主動去敲這第二個指令——正常流程裡沒有人會在輪數還沒到上限時想到要去查熔斷。S8 的測試只綁在 `--disposal` 這一側,`loop next` 側完全沒有對應條款/測試,這個落差在條款清單裡是隱形的。

## F3 处置閘既有的 `readonly` 判斷是逐段包,不是整支函式包一層——新印段落要自己記得包,插入點(FAIL 分支)目前沒被既有的 `if not readonly` 蓋到
severity: minor
blocking: 否 — 判準:S9 文字本身已經寫明「回放與凍結不印」,只要實作者照著做這句話仍能做對;沒做對也只是漏了一個訊息、不會讓閘的判定或退出碼變化(S9 綁的是「不改判定與退出碼」),頂多是回放輸出多印一段不該印的建議文字,不會讓人依它做錯決定的等級不到 major。
file: `scripts/lumos:18265` — `_loop_status_disposal(..., readonly=False, ...)`。
file: `scripts/lumos:18534-18552,18583-18584` — 目前 `readonly` 是逐段各自包(`_roster_tail`/`_severity_tail` 一段、intake+審查有沒有用一段、尾端 `_loop_gov_mark` 一段各自寫 `if not readonly:`),不是整支函式外層一層 `if not readonly:` 包住全部輸出。
file: `scripts/lumos:18574-18576` — cap 報告最自然的插入點(FAIL 分支 `if fails: print(FAIL banner); return 1`)目前完全不在任何 `readonly` 判斷之內,PASS 分支(18577-18585)同理——插入這兩處的新印段落不會「自動」被既有守衛蓋到,得各自補一個新的 `if not readonly:`。
spec 只講了「要不印」這個結果要求,沒有指出既有 `readonly` 是逐段而非整函式包裹這件事,實作時若順著「reuse 既有慣例」的直覺以為包一層就好,容易漏掉 FAIL/PASS 這兩個新插入點各自需要新守衛。

## 已看,無:
- `_panel_retired_for` 的日期邊界(`scripts/lumos:8197-8208`)是 `ts[:10] >= cutoff`,含 2026-08-26 當天,跟 spec「舊閘退役那天起」「判法直接呼叫 `_panel_retired_for`,不在文字裡另寫日期」一致,「帳首日期剛好在退役日」這個邊界沒問題。
- light(`scripts/lumos:10402-10403`)與 code 循序單審 `seq`(`scripts/lumos:10404-10406`,`eff_tier=="standard" and _roster_kind==「code」and not panel_fmt`)都是既有變數,且寫側已經擋死:非 code 的 standard/high 分級若 round-less 會在 `scripts/lumos:10412-10415` 直接擋下(rc2)——也就是說範圍外唯一合法的 round-less 情形只有 light 跟 code-seq 兩種,S10「三種路徑不變」在資料形狀上是自洽的,不存在第四種漏網的 round-less 多席迴圈。
- `_loop_status_disposal` 已有 `result_out` 參數(`scripts/lumos:18265`,`scripts/lumos:18571-18573` `result_out["rid"]`/`result_out["fails"]`),`loop replay --freeze` 已經在用它取回 `rid`/`fails`(`scripts/lumos:635,649` 一帶呼叫處)——spec 說 cap 報告要「照抄處置閘列出的失敗步驟」技術上有現成的機器可讀管道,不必靠 parse stdout banner 文字,這條路可行。
- 「一輪有兩筆彙總帳」:處置閘只驗「latest」(當前最後一輪)的 carrier 數量(`scripts/lumos:18340-18350`,`len(carriers)>1` 直接擋下 rc2),因此在任何一輪還是 latest 的當下,重複彙總帳就會被擋、無法再往下一輪推進——換句話說,一個 loop 帳本裡「已成為過去輪」的那些輪,在它們還是 latest 的那一刻必定已經被這道守衛驗過只有 0 或 1 筆 carrier,不會有歷史輪帶著兩筆彙總帳留在帳上侵入 cap 報告的統計。這個邊界對這份計劃沒有新風險,`_review_yield_round`(`scripts/lumos:7378` `next(...)` 只取第一筆)沿用既有函式不算新洞。
- 「輪次編號跳號」:`rounds_count`(`scripts/lumos:10416`)是 distinct round-id 字串的數量而非數值序,跳號(如只有 r1、r3 沒有 r2)不影響跑滿判斷或 cap 報告的輪數統計,只是顯示上的字串,不是計算上的隱患。
- 「處置閘同時有多個失敗步驟」:`fails` 是字串 list(可同時含 `"G3"`/`"無處置帳"`或`"處置集合"`/`"留痕缺席"`/`"留痕"`/`"quote"`/`"條款綁定"`/`"資安席"`/`"落點"`,見 `scripts/lumos:18333,18376,18395,18406,18412,18416,18430,18434,18441,18559,18564,18570`),S4 的「只要有處置以外的就先修」邏輯只需要判斷 `fails` 是否為 `{"無處置帳","處置集合"}` 的子集,能用既有結構實作,不受多重失敗步驟同時出現影響;只是 spec 例舉的「留痕、條款綁定、落點、資安席、材料被改過」清單沒把 `quote`(引句錨定)這個獨立失敗步驟名字算進去,但因為判準是「處置以外」的全稱,不是白名單比對,不影響行為正確性,已併入 F4 等級以下、不另開條目。
- 「輪次編號已收斂之後又記一輪」「重寫收尾的迴圈」:S8 熔斷是按「同一個審查編號」累計,本身無跨編號洩漏風險;此計劃的慣例(含它自己取代 `代碼審跑滿上限的判斷依據_計劃` 的方式)是重寫後開新編號而非沿用舊 id,審計修正紀錄與 WHY 段落也是這樣操作的,沒看到程式或帳本層面允許同一 id 在 converged/rewrite 之後又被接續记帳而不受任何守衛質疑的路徑,判不出這裡有新風險,先不標。
- 實務隱患五類:金流/對外送出/守衛面(不改判定與退出碼)三項跟 spec 自報一致,程式面沒看到反例;併發/效能兩項 spec 自報「不另開讀帳路徑」也跟現有 `_loop_status_disposal`/`_review_yield_round` 都是純讀函式一致;唯一要補的是 F1/F2 兩個行為缺口不是「風險類」漏答,而是這功能本身「印出的內容跟閘的真實判定對不上」「該早出現的時候沒出現」這兩件事,不屬於五類清單但更貼近這份計劃的核心承諾(「讓迴圈真的會說出跑滿上限」「先修出口再印算得準的數字」)。

最嚴重 severity: major;blocking 共 2 條(F1、F2)。
