# code-codex-s2 r1 單 reviewer 審查報告

審查對象:`governance/review-reports/code-codex-s2/r1-snapshot.patch`(逐 hunk 全讀,1233 行)。
方法:除了讀 diff,逐條可疑處都在 repo 裡直接跑最小重現——用 `git stash` 把 `scripts/lumos`/`scripts/test_lumos.py`
還原到這份 patch 對應的 HEAD 狀態(blob `ce5c4fa` 與 patch 的 after-index 完全一致,確認測的是這份 diff 本身,不是後續已改動的工作樹),
跑完再 `stash pop` 復原。file:line 一律以這個 HEAD 狀態為準。

---

## Finding 1 ★核心★

severity: major
blocking: 是
file: `scripts/lumos:6216`(`cmd_loop_next` 一致性檢查)、`scripts/lumos:4143-4152`(`cmd_canary` 對應檢查)、`scripts/lumos:5814-5817`(`_loop_orchestrator`)

引句:「if orchestrator and orch_anchor and orchestrator != orch_anchor:」

**問題**:「帳面已定錨就不能中途換」這條保護,只在 `orch_anchor`(帳面已有的編排者值)為真時才生效。但 `_loop_orchestrator` 對「完全沒有 `orchestrator` 欄的舊帳」回傳 `None`——這正是本設計自己承認會存在的常態(舊帳、或任何一次 `canary record` 忘記/選擇不帶 `--orchestrator`,因為 record 本來就「不擋且不寫欄」)。於是「舊帳 + 第一次帶 `--orchestrator`」這個轉角完全繞過了保護:不管帳上已經有多少輪、那些輪的審查員原本是在什麼假設下審的,只要現在第一次有人(不管是不是筆誤)喊出 `--orchestrator codex`,工具就直接接受,並且**回溯**把整本帳都當成 codex 編排——`_roster_observe` 是拿同一個 `orch` 去對**所有**輪(不分新舊),不是只對新輪生效。

**最小重現**(實測,rc 與輸出逐字貼):
1. 手寫一筆舊帳:`{"loop":"oldacct-test2","round":"r1","tier":"standard","auditor":"sonnet-r1",...}`(沒有 `orchestrator` 欄,代表這個編號本來就沒宣告過編排者——所有既有 S1 時期或忘記帶旗標的迴圈都長這樣)。
2. 之後隨口記一筆 r2:`canary record none --loop oldacct-test2 --round r2 --auditor codex-r2 ... --orchestrator codex` → **rc0,無警告**。
3. 這時候 `loop status oldacct-test2 --roster` 印出:
   ```
   [roster] oldacct-test2:類型 design(從名稱前綴推的),分級 standard,編排者 codex
   [roster] r1: 實派 1 席(同門[codex] 0/外家 1/unknown 0);應派 required 同門 4+外家 0
   [roster] r1:seat_shortfall——同門(codex)審查員缺不夠(實際 0 席,應有 4 席)
   ```
   **round r1 的審查員「sonnet-r1」被回溯改判成「外家」,還被打成 seat_shortfall**——但這輪本來根本不是在 codex 編排下審的,r1 記錄時這個功能甚至還不存在。全程沒有任何一行警告說「這個編號正在從無主變成 codex 主」。

這正是這個功能自己要防的事(程式碼注釋自己講:「工具不預設 claude——Codex 編排時漏了會靜默套錯家族」),只是換了一個觸發路徑(「舊帳 + 首次帶旗標」而非「新帳 + 忘記帶旗標」)。`--tier` 沒有這個問題是因為 tier 的「無定錨」分支有明確的 legacy fallback 語意,不會被拿來回溯重新分類任何東西;`--orchestrator` 借用了同一套「`anchor = next(...)` 找不到就是 None」的模式,但沒有意識到自己的下游(`_roster_observe`)是全帳適用,語意不對稱。

---

## Finding 2

severity: major
blocking: 是
file: `scripts/lumos:6353`(`emit()` 文字模式家族重標)、`scripts/lumos:6254`(`out["roster"] = _roster`,未重標直接塞進 JSON)

引句:「_fam = ("同門[" + out.get("orchestrator", "claude") + "]") if s['family'] == "claude" else ("外家(不是 " + out.get("orchestrator", "claude") + " 那一家)" if s['family'] == "external" else s['family'])」

**問題**:d4 的賣點是「family 欄相對化」——但這個相對化**只做在文字模式的 print 裡**,`out["roster"]["seats"]` 這個字典本身(也就是 `--json` 吐出來的東西)從頭到尾維持 `_TIER_ROSTER` 表裡寫死的絕對字面值 `"claude"`/`"external"`,從未被改寫。`--json` 是官方支援、文件明講存在的機讀輸出模式(`cmd_loop_next` 簽章就有 `as_json`),任何照著 JSON 走的下游(例如未來的自動化派工,或任何不完全複製這段 print 邏輯的消費端)只要照字面讀 `family`,在 codex 編排下就會把「同門」席誤讀成「必須是 Claude 模型」,方向恰好相反。

**最小重現**(實測):
```
lumos loop next code-jsontest2 --tier high --orchestrator codex --json
```
輸出:
```json
{"orchestrator": "codex", "roster": {"seats": [
  {"slot": "鏡頭1", "family": "claude", "occupies_w": true, "requirement": "required"},
  ...
  {"slot": "外家finder", "family": "external", "occupies_w": true, "requirement": "required-fail-closed"}
]}}
```
`orchestrator` 講的是 codex,但 4 個「required」佔權重席的 `family` 仍字面寫 `"claude"`——JSON 消費端若不知道要拿 `orchestrator` 欄再自己重算一次相對關係(而這段重算邏輯目前**只存在於文字 print 分支裡**,沒有抽成共用函式、也沒有寫進任何欄位),就會照字面把這些席派給 Claude 模型,重演這個功能想避免的「靜默套錯家族」。`t_codex_s2_orchestrator` 的斷言 2 只驗了 `d.get("orchestrator") == "codex"`,從未檢查過 `d["roster"]["seats"]` 的 family 值,所以這個落差完全沒被測試釘住。

---

## Finding 3 ★本案特定鏡頭★

severity: major
blocking: 是
file: `scripts/test_lumos.py:17008`(`t_m1_loop_next` 第一條斷言)

引句:「r = run(v, "loop", "next", f"nx-{_M1U}")」

**問題**:這是「27 個舊呼叫機械補旗標」裡**沒有補到**的一個,而它沒被補到本身造成了語意漂移。這一行緊接著的斷言是 `check("零記錄無 tier rc2", r.returncode == 2)`——這條測試在這次 diff 之前,測的是「零記錄、沒給 `--tier` → rc2」這件事。但這次 diff 在 `cmd_loop_next` 裡新插了一段「零記錄且沒給 `--orchestrator` → rc2」的檢查,而且**它排在 tier 檢查前面**(`scripts/lumos:6183` 附近的 `orch_anchor`/`orchestrator` 判斷段落先於 `if eff_tier is None:` 段落)。這一行呼叫**兩個旗標都沒給**,所以現在 rc2 是因為缺 `--orchestrator`,不是因為缺 `--tier`。斷言只檢查 `r.returncode == 2`(沒檢查訊息內容),所以測試依然綠燈,但它已經不是在測自己名字寫的那件事了。

**實測驗證**(對照組,同一個 HEAD 狀態下跑):
```
$ lumos loop next nx-test123          # 兩個旗標都不給
擋下:...第一次呼叫要帶 --orchestrator claude|codex...     # rc2,原因是 orchestrator
$ lumos loop next nx-test456 --orchestrator claude   # 只補 orchestrator,不給 tier
擋下:...工具不會幫你猜分級...第一次呼叫請加 --tier 指定分級   # rc2,這才是原本要測的訊息
```
第二個組合(「給了 `--orchestrator` 但沒給 `--tier`」)才是真正還在測「缺 tier」這個行為的輸入,但**整份 diff 裡沒有任何一個測試呼叫用這個組合**——搜過全部 54 個 `run(v, "loop", "next", ...)` 呼叫點與全部 4 個行程內 `cmd_loop_next(...)` 呼叫,沒有一個是「帶 orchestrator、不帶 tier、零記錄」。也就是說,`cmd_loop_next` 裡「零記錄缺 --tier → rc2」這條分支(`scripts/lumos:6228` 附近)目前實質上沒有任何測試守住,只是恰好被另一條新守衛擋在前面,表面上綠燈。

---

## Finding 4

severity: minor
blocking: 否(建議與 Finding 1 一起修,但單獨看不影響任何測試或現有流程)
file: `scripts/lumos:6281`(`record_cmd` 範本,已補旗標)vs `scripts/lumos:6288-6295`(`disposal_cmd` 範本,未補)

引句:「f" --spec <計劃節點.md> --reviewed <sha256>{_tier_flag}")」

**問題**:`loop next` 同時吐兩個複製貼上範本——`record_cmd`(給一般席位用,這次 diff 有幫它補上 `{_orch_flag}`,見 patch 300-301 行的 `-`/`+` 對)與 `disposal_cmd`(T5 處置閘的「彙總 carrier」範本,skill 文件寫的 SOP 是「各席一筆留痕(用 record_cmd 樣式)+ 同輪僅一筆彙總 carrier(用 disposal_cmd 樣式)」)。這次 diff 只改了前者,`disposal_cmd` 那段的 f-string 结尾維持 `{_tier_flag}")`,完全沒有 `{_orch_flag}`——同一個函式裡兩個並列的範本,一個補了一個沒補。

實務影響有限(因為 disposal_cmd 只在「非 light 且非 legacy」時才吐,而同輪通常還有其他用 `record_cmd` 樣式記帳的席位,那些席位的記錄會把 orchestrator 錨上),但如果編排者照抄 `disposal_cmd` 的完整範本、且那一筆恰好是這個迴圈編號的第一筆落帳,這筆記錄本身就不會帶 `--orchestrator`,不利於「每筆記錄的來源可追」這件事,也是不對稱維護(下次有人改 `_tier_flag` 相關邏輯,大概率只會想到改 `record_cmd` 那一處)。

---

## Finding 5

severity: minor
blocking: 否
file: `scripts/lumos:4143-4152`(`cmd_canary` 的 orchestrator 區塊)

引句:「rec["orchestrator"] = orchestrator」

**問題**(對應審查鏡頭第 1 點指定要查的「`--orchestrator` 給了但 `--loop` 沒給」):這一行在 `if loop:` 分支**外面**(見同區塊「若 loop 有給才做定錨衝突檢查,`rec["orchestrator"] = orchestrator` 則是無條件執行」的縮排結構),所以 `--orchestrator codex` 不搭 `--loop` 一樣會 rc0、欄位照寫。但 `orchestrator` 欄位存在的唯一意義是「錨定某個 loop 編號的編排者」——沒有 `--loop` 的記錄本來就不會被任何 `_loop_orchestrator(_loop_records(env, loop_id))` 查詢撈到(因為查詢是照 `loop_id` 過濾的),這個欄位寫上去純粹是孤兒資料,使用者以為自己標記成功,實際上這筆記錄的 orchestrator 資訊不會被任何下游邏輯讀取或使用。不是資料損毀,但是一個容易誤導使用者「已標記」的靜默行為落差。

---

## Finding 6

severity: minor
blocking: 否
file: `scripts/lumos:5931-5933`(`_roster_observe` 席名尾碼提示)

引句:「for a in auditors:   # 席名慣例 <鏡頭>-<模型>(收斂閘殘餘估計降級_計劃):沒帶模型尾碼的外家席只提示不改帳(調研候選 ⑥)」

**問題**(對應審查鏡頭第 1 點「席名提示對每輪每席都印,會不會在多輪帳面洗版」):這段迴圈巢狀在外層 `for rid in rids:`(`rids` 在沒給 `only_rid` 時是**整個編號的全部歷史輪**)裡面,而且用的是 `_quiet()`(在 `lumos loop status <id> --roster` 的完整多輪視角下**會印**;只有單輪問閘尾端 `anomalies_only=True` 才被壓下)。所以同一個外家席名字如果每輪都沒改(常見情況——同一個人被連續派了好幾輪),同一句提示會逐輪重複。

**最小重現**(實測):同一個 loop 記 3 輪,每輪外家席都叫 `codex`(沒有 `-模型` 尾碼),`lumos loop status <id> --roster` 印出:
```
[roster] r1:席名 codex 沒帶模型尾碼,建議照慣例寫成 <鏡頭>-<模型>(如 外家否決-codex),家族辨識才穩
[roster] r2:席名 codex 沒帶模型尾碼,建議照慣例寫成 <鏡頭>-<模型>(如 外家否決-codex),家族辨識才穩
[roster] r3:席名 codex 沒帶模型尾碼,建議照慣例寫成 <鏡頭>-<模型>(如 外家否決-codex),家族辨識才穩
```
三行一字不差,單純因為輪數而線性重複——是純觀察建議(不進 rc),但長期迴圈(design-loop 上限到 3、code high 到 3、light 到 2,已經不算太誇張;但歷史上確實有迴圈跑到 6 輪以上的 legacy 帳)看下來會洗版。

---

## 逐項正確性鏡頭覆核(未獨立列 finding 的部份,附結論)

- **`_roster_family` dual-hit / 大小寫 / 判序**:`orchestrator="codex"` 時,`own` 取 `_ROSTER_CODEX_KEYS=("codex","gpt")`,`other` 取 `_ROSTER_CLAUDE_KEYS ∪ (_ROSTER_EXTERNAL_KEYS − CODEX_KEYS)` = `{"sonnet","opus","haiku","claude","gemini","qwen"}`,`other` 優先判(「外家先比、先命中先贏」對 codex 編排一樣成立,只是「外家」的字典換了)。實測 `codex-sonnet`(同時含兩家關鍵字)在 `orchestrator="codex"` 下判成 `("external", True)`——同時符合「先命中先贏」的文件承諾與既有 dual-hit 測試precedent,不是 bug。大小寫用 `.lower()` 處理,`"CODEX-caps"` 正確判成同門。舊呼叫點(`t_roster_family_classify` 用預設參數呼叫)因為 `orchestrator="claude"` 是預設值,行為與改動前逐位元組相同,已跑過該測試確認綠燈。
- **定錨:帳面兩筆不同 orchestrator(人手直接改檔)**:`_loop_orchestrator` 取檔案順序中第一筆合法值,這點與既有 `tier` 定錨的「先到先贏」慣例一致,不是這次新增的獨有問題;真正的洞是 Finding 1 描述的「從 None 到有值」這個轉角完全沒被這條保護網接住,不需要人手改檔就能觸發。
- **`cmd_canary` 對「loop 給了但 orchestrator 沒給」**:確認 `record` 不擋、不寫欄(`if orchestrator is not None:` 整段直接跳過),符合設計「首輪必帶是 `loop next` 的責任,`record` 只是選配」。
- **`eff_orch` 的 UnboundLocal 風險**:`eff_orch = orch_anchor or orchestrator or "claude"`(`scripts/lumos:6223`)定義在所有 phase 分支(escalate/gate-pending/converged/cap-reached/plant-canary)之前、只算一次,`emit()` 閉包直接讀外層變數,實測 escalate/gate-pending/cap-reached/converged/plant-canary 五條路徑均可正常吐值,無 UnboundLocalError。
- **`out["orchestrator"]` 是否 JSON 與人讀兩條路都出**:JSON 恆出(`out` 字典頂層鍵);人讀模式僅在有 roster 可印時才會透過 `_fam` 間接帶出(見 Finding 2),`roster_note`(查表 miss/indeterminate)分支下人讀模式看不到 orchestrator 是誰——影響有限(這類 loop 本來就沒有 roster 語意),未獨立列 finding。
- **`record_cmd` 對 light 分級也帶旗標**:確認會(`_orch_flag` 定義在 `if phase == "plant-canary":` 區塊內、`light` 只影響 `rmode`/`canary_type`,不影響 `_orch_flag` 是否附加)。
- **零記錄但 rounds 非空(壞行)邊界**:壞行(JSON parse 失敗)在讀取階段就被 `except ValueError: continue` 濾掉,不會進 `rounds`,不影響 orchestrator 判斷;這段行為與既有 tier 邏輯共用同一段讀取迴圈,非本次改動風險點。
- **`_roster_observe` 的 `rounds` 在 `only_rid` 模式是全帳還是單輪**:追過三個呼叫點(`cmd_loop_status` 的 `--roster` 全模式、`_loop_status_disposal` 的單輪問閘尾端、`cmd_loop_replay`),`rounds`/`parsed` 參數在全部路徑都是「整個 loop_id 的完整歷史記錄」,`only_rid` 只影響**要對哪一輪的 dispatch 快照跑席位比對**,不影響 `_loop_orchestrator(rounds)` 讀到的樣本——即使判定輪自己沒帶 orchestrator 欄,只要帳上任一輪帶了就抓得到,不會誤判成舊帳。這點設計正確,行為與 `tier` 的 `only_rid` fallback 限制刻意不同(有文件解釋:orchestrator 是全帳唯一值,tier 理論上曾允許跨輪不一致)。

---

## pitfalls manifest

0 條,如題目所述。本次審查未依賴 manifest,全部命中靠逐 hunk 手讀 + 實跑重現。

---

## 圖譜鏡頭(固定席逐條判)

- **Issues/hook卸載殘留註冊.md**(牽連 `scripts/merge-claude-settings.py`):**不影響**——本次 diff 完全沒有觸碰 `merge-claude-settings.py`。
- **Systems/slim-install-安裝器.md**(★INVARIANT★ ×7,牽連 check-graph-sync.py/impact-hook.py/scripts/lumos/merge-claude-settings.py/test_lumos.py):**不影響**——這次改動集中在 `cmd_canary`/`cmd_loop_next`/`_roster_family` 等 loop/canary 家族判斷函式,跟 7 條 INVARIANT 描述的 CLAUDE.md 注入位置、冪等性、FULL-BACKUP 編碼、manifest 寫入、目標守衛、Windows shim 直譯器偵測、碰撞偵測完全是不同函式、不同程式路徑,沒有共用任何狀態或呼叫關係。
- **Systems/loop-convergence-recording.md**(★RISK★,牽連 scripts/lumos):**直接相關,是本次改動的宿主子系統**——但 `lumos context` 查到的 KEY 摘要講的是 canary-stats 讀取面與 settle 模式,兩者都沒被這次 diff 碰;既有的 escalate/gate-pending/converged/cap-reached 判定邏輯順序與內容未變(已用 `t_m1_loop_next` 等測試在乾淨 HEAD 狀態下逐條驗證)。這次改動新引入的風險是 Finding 1/2 描述的「編排者定錨」本身的縫隙,屬於這個系統新增的攻擊面,非既有合約被破壞。
- **Systems/slim-uninstall-一行卸載.md**(★INVARIANT★ ×6):**不影響**,理由同 slim-install-安裝器。
- **Systems/lumos-cli-lifecycle.md**(★INVARIANT★:re-inject 保留 sentinel 外內容):**不影響**——這次 diff 沒有碰 CLAUDE.md 注入/re-inject 邏輯。
- **Systems/design-loop.md**(★RISK★,牽連 scripts/lumos/test_lumos.py):**直接相關**(design-loop 的一頁手冊本身也在這次 diff 裡被改,新增「--orchestrator 首輪必帶」的進場要求)。核心收斂判準(散文審處置閘四條合取)未被觸碰,風險同 loop-convergence-recording 條目——新增的編排者定錨層有 Finding 1/2 兩個縫隙,但不影響既有的收斂判定機制本身。
- **Systems/bound-tests-gate.md**(★INVARIANT★):**不影響**——這次 diff 沒有碰 `code-loop check` 真跑合約綁定測試的邏輯(`cmd_code_loop` 系列函式未被觸及)。
- **Systems/canary-audit.md**(★INVARIANT★ ×2:readback 驗證、second 純 telemetry):**不影響**——`cmd_canary` 新增的 orchestrator 驗證/寫入區塊(`scripts/lumos:4143-4152`)在既有的「先驗證全部欄位、最後才 append + readback」流程**之前**,寫檔本身的時機與內容格式(仍是一行合法 JSON)未變,readback 驗證機制沒被動到;`cmd_canary_second` 完全沒被這次 diff 觸碰,second 仍是純 telemetry,不影響 gate rc。

---

## 總結

max severity: **major**
blocking 條數: **3**(Finding 1、Finding 2、Finding 3)
非 blocking:3(Finding 4、5、6,均為 minor)

三條 major 的共同性質:這次 diff 的核心賣點是「編排者定錨,不讓 Codex 編排時靜默套錯家族」,但定錨保護本身留了一個「舊帳從未定錨 → 首次帶旗標即靜默生效並回溯」的縫隙(F1),機讀輸出(`--json`)沒有跟著相對化這個新語意(F2),而測試補丁的機械式操作意外讓一條既有守衛失去測試覆蓋而未被察覺(F3)。三者互相獨立、不互為因果,但都指向同一件事:「防止靜默套錯家族」這個目標在這份 diff 裡只做到了「新迴圈 + 忘記帶旗標」這一種觸發路徑,還有其他路徑沒堵到。
