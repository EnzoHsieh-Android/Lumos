severity: blocker

# 規格落成可驗收條件_計劃 r2 審查報告

## 逐節閱讀記錄

- 檔頭 summary/decisions:已讀。d9 的 34/29/5/0/0 已用獨立腳本重算,與正文一致(見 finding 佐證),無 finding。
- 為什麼(數字表):已讀,無 finding。
- 兩層要分開:已讀,無 finding。
- 一、門怎麼判:有 finding(見 F1)。硬單向門訊號 2(合約行掃描走 `cmd_contracts`)與訊號 3(`door: one-way`)本身邏輯自洽,無 finding。
- 二、條款句式:有 finding(見 F2)。
- 三、綁定規則:有 finding(見 F3)。
- 四、新閘 `lumos spec-gate`:已讀,`{method}` 鎖單支、零條款擋、測試名互異三條邏輯自洽,無新 finding。
- 五、逃逸自動記:有 finding(見 F4,對應已落地程式碼)。
- 六、退場條件:已讀,絕對門檻邏輯本身自洽;但其可靠性依賴 F4 修正,見 F4。
- 進度:已讀,與程式碼現況核對一致(見下方程式碼佐證),無 finding。
- 要動什麼:已讀,交叉引用全部存在,無 finding。
- 實務隱患:F1 的佐證就取自此節。
- 驗收條款 S1–S21:已讀,S4/S6/S8/S9/S13/S17 等逐條用新文法手動重放,皆能正確解析,無新增自我矛盾;S6/S7 與 F3 相關。
- 回退:已讀,`pre-spec-gate` tag 尚未打(預期中,落地前才打),無 finding。
- 誠實界線:已讀,無 finding。
- 審計修正紀錄:已讀,見「r1 折入後的殘餘」段落。

## r1 折入後的殘餘(每個「死結」的補丁都留了一個新洞)

r1 KEY 行宣稱三個死結「全部折入」,但重放後三個補丁各自留了一個新洞,型態相同:**補丁把觸發條件堵住了,但沒有堵住覆蓋範圍**。

## Findings

**F1**:規格閘規則 1 的「跳過已排除:開頭的行」是**整份計劃全文範圍的字首比對**,不限定在四類正式排除宣告內——spec 自己的「實務隱患」節就示範了這個漏洞:「已排除:效能」「已排除:多人並行」兩行根本不在四類清單(金流/對外送出/不可逆/守衛面)裡,照樣會被整行跳過。這代表任何人只要在計劃裡寫一行以「已排除:」開頭的句子(無論後面接什麼、是否屬於四類、是否滿足≥4字含實字),就能讓該行內容完全逃出硬單向門的關鍵字掃描,而這與「雙向門的條件」段落嚴格要求的四類正式格式是兩套不同的判準,前者鬆後者嚴。
severity: blocker
blocking: 是——判準:此漏洞讓規則 1 標榜的「光是討論這些詞仍會命中」防線可被一個字首繞過,而 spec 自身文字已經證明此漏洞存在,屬於設計層而非實作細節,應在放行前修正掃描範圍(限定在「實務隱患」節的四類正式宣告行)。
引句:「光是討論這些詞仍會命中,誤判代價只是多一次審查,接受。」
引句:「閘只讀計劃與跑測試,不寫共用狀態;留痕走既有審查帳的寫入原語。」

**F2**:一條文法把「無條件型」定義為「句首不是 當/在/若」,但中文沒有詞界,「當然」「在此」「若干」這類常見詞彙的**第一個字元**恰好等於觸發關鍵字,而這三個詞後面通常沒有逗號可配對成 `觸發子句`——結果是這種合法的無條件句既配不出 `觸發子句`,又因為句首字元命中 當/在/若 而被「無條件型」排除規則擋下,兩條路都走不通,規格閘會把一條寫得好好的條款判成「格式看不懂」。spec 對這個字元級/詞級的邊界完全沒有交代,留給實作者猜。
severity: major
blocking: 是——判準:這是會真的把合法條款誤判為「格式看不懂」的可重現場景(當然/在此/若干開頭),文法規則本身要先補一條消歧規則(例如要求關鍵字後緊接特定分隔符或建停用詞表)才能開始實作,否則不同實作者會做出不同行為。
引句:「無條件型 = 沒有觸發子句,而且句首不是 當/在/若」

**F3**:「每條新行為各自紅」的機制完全依賴作者誠實地只在「既有行為」條款上標 `[keeps]`,但規格文本沒有任何機制驗證 `[keeps]` 標記的真實性(例如驗證該測試方法在這輪迴圈之前就已存在於 git 歷史)。這代表作者只要把**全部**條款(包含真正的新行為)都標成 `[keeps]`,S6/S7 的「沒標 keeps 的每一條測試都是紅的」檢查就變成空集合上的真命題,整份雙向門計劃可以在零支紅測試的情況下直接放行,而這個漏洞比 spec 自己承認的「樁測試」殘餘更嚴重——樁測試只是繞過「至少一支紅」,全標 keeps 是繞過「所有新行為都要紅」。
severity: blocker
blocking: 是——判準:此漏洞讓第四節「至少一條紅」這個被 r1 三席認定為核心防線的機制形同虛設,且 spec 明文承認的殘餘段落沒有涵蓋這個更大的洞,應在放行前補一條機械檢查(至少要求存在一條未標 keeps 的條款,理想情況再加對 keeps 測試的既存性驗證)。
引句:「沒有標記的條款一律視為新行為,其測試在規格閘時必須是紅的」

**F4**(對應已落地程式碼,非本輪新寫但屬 r1 折入後的接縫新洞):CI 逃逸來源篩法的判準是字串子字串比對 `"test" in failed_step.lower()`,這會誤判任何名稱含 "test" 子字串但與測試無關的 CI 步驟,例如 "latest"(含 test)、"attestation"(含 test)、"contest" 等常見英文詞——這些步驟失敗時會被錯誤記成逃逸,污染第六節「雙向門計劃的逃逸率」這個唯一的主要指標,可能造成 RETIRE-IF ①②誤觸發或誤不觸發。
severity: major
blocking: 是——判準:這條記帳邏輯是整套「靠量測補洞」設計(誠實界線段落明講)的度量基礎,子字串誤判會讓退場判準失真,且是可重現的具體輸入(步驟名含"latest"等),應在放行前修正為更精確的比對(如步驟名以 test 開頭、或用既有 workflow 步驟分類欄位)。
file: `scripts/lumos:22328` ——`if concl in _CI_RED and "test" in str(r.get("failed_step", "")).lower():`

**F5**:針對「push-gate:unreviewed 依賴的雙向門留痕由尚未實作的 spec-gate 寫入,這條路徑現在是死路還是空轉」——實地追蹤 `_door_for_loop`(`scripts/lumos:7479`)發現它讀 `.canary-log.jsonl` 尋找 `kind=="spec-gate"` 的記錄,目前沒有任何指令會寫這種記錄,所以 `door` 永遠是 `"unknown"`,`_auto_escape`(`scripts/lumos:7534`)裡 `if stage == "push-gate:unreviewed" and door != "two-way":` 這條判斷永遠為真,因此該階段目前**空轉、不會寫入任何逃逸紀錄**,而不是拋錯或死路。這個行為是安全的(保守不誤記),但 spec 沒有明文交代「上線前這條路徑恆為零筆」這件事,不理解程式碼的人看逃逸帳可能誤以為機制壞了。
severity: minor
blocking: 否——判準:程式行為正確且保守(fail-safe 不誤記),只是文件沒交代這個過渡期現象,不影響是否可放行進實作。
file: `scripts/lumos:7479` ——`_door_for_loop` 找不到 `kind: spec-gate` 記錄時回傳 `"unknown"`
file: `scripts/lumos:7534` ——`if stage == "push-gate:unreviewed" and door != "two-way":`(door 恆為 unknown,恆不記)

## 實務隱患鏡頭逐類作答

- **併發**:F1/F3 之外,已落地的逃逸自動記寫側有 `_vault_write_lock`(`scripts/lumos:7520`)包住讀-判-寫整段,`t_escape_auto_lock` 已翻紅釘驗證,無新併發風險。
- **效能**:規格閘只跑綁定的那幾支測試,spec 已排除全套效能疑慮(第 219 行),合理。
- **資源**:規格閘只讀計劃、跑既有 `run_cmd`,不新開長生命週期資源(連線/檔案),無。
- **回滾**:回退步驟①②③④齊全且有 `pre-spec-gate` tag 錨點規劃,tag 目前確實還沒打(`git tag -l pre-spec-gate` 空),但這是「落地前才打」的正常順序,不算缺陷。
- **遷移**:`.escape-log.jsonl`/`.canary-log.jsonl` 都是 append-only 新增欄位,不改既有記錄格式,`_round_valid_m2`(`scripts/lumos:6337`)的 kind 白名單目前不含 `spec-gate`,但 spec 已自陳這點待補,無新增遷移風險。

## 固定席節點逐條判斷(會不會破壞其宣稱的行為/合約)

- `Systems/design-loop`(★INVARIANT★ 處置閘第五步):**會影響**,但 spec 已明文承認是「改不可變合約行」的單向門改動,並規劃綁測試+審計更新合約行——這是被審計劃內建的改動,不算意外破壞。
- `Issues/code-loop守衛main-direct盲區`:**不影響**——spec 沒有改動 pre-push 對 main 直推的判斷邏輯,只在 code-loop 擋下的分支上新增逃逸記帳呼叫,原有盲區判斷路徑未觸碰。
- `Systems/anchor-integrity`:**會觸發但不破壞**——`scripts/hooks/pre-push` 與 `scripts/test_lumos.py` 是錨點檔,spec 進度段已正確指出要 `lumos anchor approve`,合約行為(baseline hash 比對)本身沒被改動,只是這次改動會讓下次 `anchor verify` 依約翻紅,是預期內行為。
- `Systems/每支檔有家`:**不影響**——本次要動的 `scripts/lumos`/`scripts/hooks/pre-push`/`scripts/test_lumos.py` 皆已有家(design-loop/其自身),新開 `Systems/規格閘` 也已在 `lands_in` 寫明。
- `Systems/lumos-cli-lifecycle`(re-inject sentinel 不變量):**不影響**——本案不碰 CLAUDE.md 的 re-inject 邏輯。
- `Systems/bound-tests-gate`(★INVARIANT★ 合約測試逐支真跑):**不影響其現有合約**,且被 spec 第四節明文重用(`run_cmd {method}` 鎖單支、弱證據不收的邏輯直接借用同一套判準),屬於延伸使用而非改動。
- `Systems/測試假綠形態`(★INVARIANT★ 翻紅釘要有前置斷言):**不影響其合約本身**,但 F4 指出的 CI 子字串誤判是本輪發現的「假綠/假紅來源」新案例,可視為對此節點知識庫的補充候選,非破壞。
- `Systems/lumos-cli-read`(★INVARIANT★ search 預設排除 superseded 不排除 stale):**不影響**——spec-gate/逃逸帳與 search 排除邏輯無交集。

## 結論

severity: blocker
blocking 4 條(F1/F2/F3/F4),non-blocking 1 條(F5)。r1 折入的三個「死結」修正在重放後各自留了一個新洞(F1/F2/F3),另有已落地程式碼的一個接縫 bug(F4)污染退場判準所依賴的度量;放行前應優先修 F1 與 F3(兩者是靜默繞過,危害性高於 F2 的誤拒與 F4 的誤記)。
