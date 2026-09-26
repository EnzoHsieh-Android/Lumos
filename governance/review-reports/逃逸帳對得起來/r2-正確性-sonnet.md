severity: blocker

## F1 分母定義「kind=converged」對代碼審迴圈永遠是 0,而且治理帳裡沒有欄位可以認出是哪個迴圈
severity: blocker
blocking: 是——照這句字面實作,`escape-stats` 的「code」loop_kind 這整個分支(分子分母)永遠印「—」,設計的核心目的(把逃逸率拆成 design/code/plan 分開算)有三分之一從第一天就是死路,不是之後才退化。
引句:「分母:放行了的迴圈數。放行 = 治理帳有這個迴圈 `kind=converged` 的紀錄(處置閘過關時寫的;`cap-reached` 與 `rewrite` 都不算放行),而且審查帳裡有它的列(排除測試留下的假紀錄)。」
file: `docs/.governance-log.jsonl`——機械數過:`kind=converged` 的 258 筆全部 `"gate": "design-loop"`,一筆 `"gate": "code-loop"` 都沒有;代碼審過閘寫的是 `"gate": "code-loop", "kind": "passed"`(232 筆,例如 2026-09-26 提交 `74bd82c`:`{"ts": "2026-09-26T11:23:05+08:00", "commit": "74bd82c", "gate": "code-loop", "kind": "passed", "hard": false, "nodes": [], "detail": "驗收前提欄位可改:三輪代碼審,處置閘 PASS、判定已凍結", ...}`)。照 spec 字面判 `kind=="converged"`,這筆(以及全部 232 筆代碼審過閘紀錄)永遠不算放行。
file: `scripts/lumos:8656-8667`——程式碼自己的註解已經把這件事寫死:「★code-loop 那組的 nodes 欄永遠是空陣列★(148 筆全空)——因為那本帳認的是「分支 + 版本」不是迴圈編號,兩套識別體系從來沒建過對應關係」「code-loop 這組只能從自由文字的 detail 認編號(慣例上 detail 開頭就是編號)。★這是啟發式,不是保證★」,並留了 `REVISIT:2026-11-07 正解是讓 code-loop pass/skip 收一個 --loop 參數、把編號寫進 nodes...本批不做`。也就是說即使把判準從 `converged` 改成也認 `("code-loop","passed")`,治理帳裡也**沒有結構化欄位**能拿來對「這筆放行是哪個迴圈」——`nodes` 是 `[]`,迴圈名只在 `detail` 這種人寫的自由文字裡,現成的啟發式比對函式 `_loop_close_stamps`(scripts/lumos:8735-8778)本身也自稱「失效偏保守」。spec 全文(WHY 摘要、PRIOR-ART、一~四節、條款 S6/S12)都沒有提到 `gate` 欄位、`kind=passed` 這個值、或 `nodes` 對 code-loop 永遠是空陣列這件事,顯示這份分母定義是只驗過 design-loop 那一半資料寫出來的。
→ 要成立至少要:(a) 分母判準同時認 `("design-loop","converged")` 與 `("code-loop","passed")` 兩種 (gate,kind) 組合,且 (b) 對 code-loop 借用或重做 `_loop_close_stamps` 那套「已知編號→在 detail 裡找」啟發式(並承認它的保守失效面),而不是單看一個統一的 `kind=="converged"` 字串比對。

## F2 撤回紀錄本身(kind=withdraw)沒有被排除在統計之外,會被當成一筆「plan 類、無佐證」的逃逸列誤算進去
severity: major
blocking: 是——escape-stats 的「末尾印全體的無佐證...筆數」與 plan 類逃逸列數這兩個输出,只要有人用過一次 `--withdraw`,數字就會多算一筆跟真實逃逸完全無關的紀錄,而且會一直存在(帳本只進不出)。
引句:「統計類讀者(問閘尾漏斗、治理帳統計、escape-stats)用預設,**不算**被撤的列。」
引句:「撤回紀錄長這樣:`{"kind":"withdraw","target":"<被撤的 token>","reason":"…","by":"<git user.name>","ts":"…","token":"<新的 ESC- 編號>"}`——有自己的 token,不跟目標共用。」
file: `scripts/lumos:7397-7415`——現有 `_escape_rows_for` 就是把 `.escape-log.jsonl` 逐行 `json.loads` 後整包塞進 `out` 回傳,沒有任何 `kind` 過濾;spec 第三節只交代 `include_withdrawn` 這個參數要「不算**被撤的列**」(即:原逃逸列若已被某筆撤回紀錄的 `target` 指到,就濾掉那筆原逃逸列),但完全沒提撤回紀錄**自己**(`kind:"withdraw"` 那一筆,由「清單... 撤回紀錄本身也列出」可知它跟一般逃逸列存在同一份帳裡)要不要被計入 escape-stats 的迭代。撤回紀錄沒有 `loop`/`stage`/`sha`/`defect_ref`/`severity` 欄位:若原樣餵進 `loop_kind()`(`d.get("loop")` 拿到 `None`→不是 `code-` 開頭、也對不到審查帳→落在 `plan` 類)與「無佐證」判斷(沒有 `sha` 也沒有 `defect_ref`),它會被算成一筆額外的「plan 類無佐證逃逸」,汙染 REVISIT 要看的「撤回用過幾次」與「無佐證的新列有沒有再出現」這兩個數字——恰好是這份 spec 自己在摘要裡承諾要盯的指標。
→ 要成立需要在第三或第四節明寫:`escape-stats`(以及規則缺口統計、問閘尾漏斗)在套用 `loop_kind`/歸類邏輯之前,先按 `d.get("kind") == "withdraw"` 整筆排除撤回紀錄本身,不只是排除「被撤的原列」。

## F3 手動記帳的 `--sha` 目前不會寫進帳列,S2 的「有 sha 就放行」等於摸不到
severity: major
blocking: 是——若只照 S2 字面加「沒有 sha/defect_ref/--no-defect-ref 就擋」這道驗證,卻沒同時修 `rec` 組裝那段,使用者傳了 `--sha` 卻過了驗證關卡,寫進帳的那一列卻仍然沒有 `sha` 欄位,escape-stats 之後把它算成「無佐證」——驗證端與統計端對「有沒有證據」判斷會對不上同一筆真實資料。
引句:「新寫的列至少要有 `sha` 或 `defect_ref` 其中之一。手動記帳兩個都沒有時,要另給 `--no-defect-ref "<為什麼沒有>"`」
file: `scripts/lumos:9509-9519`——手動記帳分支(非 `--auto`、非 `--list`)組 `rec` 只塞了 `loop/stage/severity/desc/ts/token`,`defect_ref`/`rule` 有給才加,**完全沒有 `rec["sha"] = sha` 這一行**;而 `--sha` 這個 CLI 旗標(`scripts/lumos:30823`,`le.add_argument("--sha", dest="esc_sha", help="--auto 用:去重鍵的 sha(不給就取 HEAD)")`)在 dispatch(`scripts/lumos:31664-31668`)時**無條件**把 `args.esc_sha` 傳給 `cmd_loop_escape` 的 `sha` 形參——也就是說手動模式今天已經可以吃到 `--sha`,只是這個值在寫帳那段被靜默丟掉。spec 的判法只講「要有 sha 或 defect_ref」,沒交代這是檢查「使用者有沒有給」還是「這一列最後寫進帳的內容有沒有帶」——兩者在現況程式碼下是兩回事。
→ 要成立需要:S2 的驗證要嘛明確改成只認 `defect_ref`/`--no-defect-ref`(手動模式的 `--sha` 停用或標成「暫不落帳」),要嘛在驗證通過後同時把 `rec["sha"] = sha` 補進手動分支的組裝邏輯,讓帳列真的帶得到 sha。目前 spec 兩邊都沒說,實作者按字面走大概率漏掉後者。

已看,無:一~二節的 `loop_kind` 三分類規則(`code-` 前綴/審查帳存在/都不是→plan)本身在真實 25 筆逃逸帳上是自洽的——例如 `code-每支檔有家` 前綴命中→code;`逃逸自動記`(無前綴、`attribution:"plan-file"`,審查帳裡查無此名)→plan;`雙向門放行`(無前綴、審查帳裡有,`canary-log.jsonl` 有一筆 `kind:"spec-gate"` 的列)→design,三種真實情況都能落到對的分類,沒找到算錯的列。第四節「下一站接住」白名單把「消費專案真推送(pos-ios)」明文歸進「其他站名…算漏網」而非「下一站接住」,對照真實那筆 `ESC-75f0bfd0`(desc 寫「推送被擋」)語意上是合理的——那是下游消費專案自己的推送閘擋下,比擋在本 repo 的 push-gate 更晚一站,算漏網是對的,不是遺漏。第四節「歸因不明」規則對照真實資料(sha `9bfa759f1f...` 同時出現在 `規格落成可驗收條件`/`逃逸自動記`/`雙向門放行` 三個迴圈列)能正確被抓出來,不誤判。`_loop_anchor_tier`(S9 引用)現有實作(`scripts/lumos:17905-17908`,「帳上第一筆帶 tier 的值」)與 spec 描述逐字相符,是既有函式直接重用,沒有落差。S10 `_plan_for_loop` 要加的「去 `code-` 前綴 + NFC」是這次要新增的行為(現況 `scripts/lumos:9293-9298` 確實兩者都沒做),不是 spec 對現況的錯誤宣稱,是要做的工作項本身,不算 bug。「lands_in: Systems/loop-convergence-recording」節點的既有內容(`canary record` 的欄位語意、K-streak 收斂算法、`_auto_escape` 三來源掛勾)這份 spec 全是加法(新增 `loop_kind`/撤回/`escape-stats`),不改動任何既有讀寫路徑,不會破壞該節點宣稱的行為。

實務隱患:spec 自己列的併發/效能/守衛面/已排除三類都合理(唯讀新指令不進閘、撤回共用既有寫入鎖、撤回會讓數字變好看但留痕可查),沒有另外要補的類別——本次審查在我的鏡頭(正確性/統計邏輯)下沒找到需要新增的隱患類。

總結:severity 最高 blocker,blocking 共 3 條(F1/F2/F3 皆是)。
