severity: major

整份 spec 已逐節讀完並對照 `scripts/lumos` 查證。有 3 條 major、6 條 minor。

## 逐節結論

- 白話、WHY、PRIOR-ART、RETIRE-IF:已讀,只有 RETIRE-IF 的計數口徑一條 minor(見 finding 7)。
- 舊否決比對:已讀,無 finding。
- 範圍:finding 1、4。
- 做法:finding 1、2、3、4、5、8、9。
- 驗收條款與預期值表:finding 2、6;S1 到 S10 彼此沒有矛盾。
- 回退:已讀,無 finding。
- 實務隱患:見文末。

## Findings

severity: major
blocking: 是(照字面實作,沒有圖譜資料夾的專案在 pass 當場崩潰)
spec 段落:〈做法〉圖譜物件。
問題:spec 只寫了「建一次 `Env(_vault_in(repo_root))`」,沒處理 `_vault_in` 回 None 的情況。`code-loop pass` 明確支援沒有圖譜資料夾的專案。
佐證:
- `_vault_in` 找不到圖譜資料夾時回 None:file: `scripts/lumos:36664`。
- `Env.__init__` 直接呼叫 `load_vault(vault)`,裡面是 `vault.rglob(...)`:file: `scripts/lumos:969`、`scripts/lumos:624`。對 None 會丟 AttributeError。
- pass 現有的 vault-free 相容邊界在 `_codeloop_pass_verify`:file: `scripts/lumos:73346`。
- 另一支用同樣方式建 Env 的程式,前面有擋 None,註解寫「前面已擋過 None」:file: `scripts/lumos:73506`。
- 缺 vault 的 Kotlin 專案只要生效日已過又改到 `.kt`,pass 就會崩潰。spec 沒有對應的條款或測試,也沒說 fail-open 要不要記帳。
引句:「生效日(`_choice_since()`)已過、而且範圍內有 `.kt` 改動時才建 `Env(_vault_in(repo_root))`」

severity: major
blocking: 是(照 spec 實作,對話裡跑 pass 會被工具逾時砍掉,而且 S10 沒要求手冊寫背景跑)
spec 段落:〈做法〉自動跑、〈實務隱患〉耗時、S10。
問題:pass 內含最長約 600 秒的 `choice-kill`,spec 沒處理對話環境的逾時,S10 也沒要求手冊寫「放背景跑」。實際耗時比 600 秒更長,冷編譯還沒量。
佐證:
- `choice-kill` 的總時限從 t0 起算,t0 在 Env 建立、兩次掃描和守的測試雜湊之後:file: `scripts/lumos:78516`、`scripts/lumos:78548`。
- 基準測試另算,每條測試指令最長 `max(600, floor)` 秒:file: `scripts/lumos:78558`。
- 實際最壞耗時是 4.7 秒 + 掃描 + 基準約 600 秒 + 配方約 600 秒 + 第二次判定,可達 20 分鐘以上。
- 手冊 SKILL 第 16 行已明寫 choice-kill「放背景跑」。同檔另一段寫明對話裡跑指令預設 2 分鐘上限,會砍掉它。
- 被外層逾時殺掉時,Gradle 子程序群組和隔離工作樹可能留下殘骸。`_ChoiceKillRun.run` 的兩段式訊號只對 Ctrl-C 或 SIGTERM 有效,對 SIGKILL 無效:file: `scripts/lumos:78492`。
- 冷編譯一次跑不完時,每次重跑都在 2 分鐘內被砍,可能永遠記不到第一筆。
引句:「冷編譯耗時還沒量。」
引句:「lumos-code-loop 手冊與命令速查 應 寫到 pass 會自動跑 choice-kill、存活要在 pass 之前處置、通過後帳要一起提交」
建議:S10 加上「pass 放背景跑、標明預計耗時」,並明寫冷編譯超時的出路。

severity: major
blocking: 是(pass 與推送前判的不是同一個範圍,spec 的防線理由不成立)
spec 段落:〈做法〉範圍,對照〈實務隱患〉守衛面。
問題:spec 說判定「推送前本來就會擋同一批」,但 pass 的範圍是 `_codeloop_default_range`,和推送前的範圍來源不同。
佐證:
- pass 用 `_lens_default_base`:分岔點 = 與主線候選(多加本機 main/master)的 merge-base。這就是整條分支從分岔點到 HEAD:file: `scripts/lumos:79505`。
- 推送前走 `_choice_push_range` 加 `push=(遠端, ref)`,再呼叫 `_push_range_start`。起點在增量推送時是「遠端舊值」,也就是只看這次新推的提交:file: `scripts/lumos:78632`。
- 結果一:第二次以後的增量推送,pass 會要求把前幾次已推過、推送前不再看的舊提交也補齊記錄,包括生效日前就推過的行和測試已變的「過期」行。這代表 pass 會多擋、多跑。
- 結果二:`include_local=True` 會把尚未推送的本機 main 算進候選,pass 的範圍可能比推送範圍小。於是會 pass 通過、推送被擋缺紀錄,正是這份計劃要消滅的情形。
- S7 只比「同一 HEAD 的帳」,沒有任何條款比兩邊的範圍。
引句:「推送前本來就會擋同一批」
建議:要嘛 pass 帶 `push=` 走推送起點的單一來源,要嘛把「兩邊範圍可能不同」寫成已知差異並補條款。

severity: minor
blocking: 否(只是白做工,不會做出錯的結果)
spec 段落:〈做法〉圖譜物件。
問題:前置判斷不含「專案有 kotlin-junit 平台」,「生效日已過」也沒講當天算不算。
佐證:
- 工具鏈本 repo 有 497 支 `.kt` 規則包樣本,但 `.lumos/config.json` 沒有 kotlin-junit 平台。
- 照 spec,工具鏈自己的分支只要改到樣本就會付 4.7 秒 Env 才發現「不要求」:file: `scripts/lumos:78567`。
- 生效日當天:`_choice_push_round` 判的是 `since > today` 才不跑,當天要跑:file: `scripts/lumos:78846`。spec 寫的「已過」有歧義,和 S4 的邊界也沒對齊。
- 這兩種情況沒有對應條款。
引句:「改動時才建 `Env(_vault_in(repo_root))`(建一次約 4.7 秒),否則這一道直接放行」

severity: minor
blocking: 否(語意取捨,spec 已寫明)
spec 段落:〈做法〉中斷。
問題:使用者按 Ctrl-C 的本意是停,但 pass 照常做第二次判定,仍可能寫入通過留痕。
佐證:`_ChoiceKillRun.run` 把第一個訊號當「停在配方之間」並正常返回:file: `scripts/lumos:78492`。之後 `cmd_code_loop` 會照常 `_codeloop_write`:file: `scripts/lumos:80366`。建議中斷後直接回 2,或至少先問一句再往下。
引句:「pass 接著做第二次判定(全部壞法都已判完時可能照樣放行)」

severity: minor
blocking: 否(對照推送前也是缺紀錄就擋,只是 spec 的描述不完整)
spec 段落:〈實務隱患〉守衛面、驗收條款。
問題:spec 只把 ast-grep 不在列為「只提醒」,測試環境沒裝(Gradle、JDK)沒有條款。
佐證:
- 基準不綠時所有行判成 no_result,pass 被擋「跑不出結果」,而且 no_result 的列會寫進治理帳。
- 出路只有逐行 `lint-waive … 不適用`。
- `_choice_kill_report` 照 rc 2 處理:file: `scripts/lumos:78695`。
- 「工具沒裝只提醒」這句話過度概括。
引句:「工具沒裝或算不出來只提醒」

severity: minor
blocking: 否(統計與排序問題)
spec 段落:RETIRE-IF、〈範圍〉① 的接點順序。
問題一:每次重跑 pass 被擋都記一筆 `code-loop-pass`。超過 30 行要分多輪跑完,中間每一輪都會被擋「沒跑完」,過半會是「沒跑完」,RETIRE-IF 因此會被正常重跑灌水。計數口徑應該是「每次通過前的第一筆」或「每個 loop 取最後一筆」。
問題二:選擇點排在 `_codeloop_pass_verify` 之前,昂貴的最多 10 分鐘以上的 choice-kill 先跑,最便宜的「凍結判定不存在或過期」最後才檢查。使用者等了 10 分鐘才被告知沒凍結。因為「記錄不丟、重跑接著做」,不會重複付費,但體驗差。
引句:「上線兩個月後,`code-loop pass` 因選擇點擋下的紀錄裡,過半是」
引句:「`_codeloop_pass_mech` 回 True 之後、`_codeloop_pass_verify` 之前」

severity: minor
blocking: 否(訊息不準,可由使用者判斷)
spec 段落:〈做法〉判一次。
問題:要穿過的函式清單不完整,工作目錄模式下有幾句訊息會誤導。
佐證:
- 讀帳實際在 `_choice_push_ledger(rr, at_sha)`,裡面 `_gov_rows_at(rr, at_sha, …)`:file: `scripts/lumos:78659`。清單只列了 `_choice_push_read`,沒列 `_choice_push_ledger`。
- 「被推版本 {sha} 的治理帳不存在…修好再推」(`_choice_push_read`)在 pass 情境下措辭不對:file: `scripts/lumos:78885`。
- `_CHOICE_PUSH_FIX["缺紀錄"]` 叫使用者「跑 lumos choice-kill 記帳後提交」,但 pass 剛自動跑過:file: `scripts/lumos:78611`。
- spec 說「印同一段處置指示」,但沒要求兩次判定的重複提醒(語法樹算不出的檔、守的測試變了)只印一次。
引句:「前綴與範圍說明要穿過 `_choice_push_round`、`_choice_push_scan`、`_choice_push_unverified`、`_choice_push_part_unverified`、`_choice_push_read`、`_choice_push_verdict` 這幾支。」

severity: minor
blocking: 否(出路清楚)
spec 段落:〈做法〉自動跑、〈範圍〉③。
問題:放行檔與計劃是從 HEAD 讀,處置後要先提交才認,但 pass 前置檢查看到未提交的非簿記檔時,訊息和擋下原因會自相矛盾。
佐證:
- `.lumos/lint-waivers.json` 不在 `_BOOKKEEPING_FILES`,放行檔或計劃有未提交改動就算髒:file: `scripts/lumos:40896`。
- 髒的時候 `_choice_kill_base` 印「工作目錄有未提交改動…先提交再跑」後回 2:file: `scripts/lumos:78292`。
- 使用者看到的是「存活 → 請 lint-waive」(他剛做完)加「先提交」兩條訊息,需要自己推理。
- 處置的修補提交(補測試、改計劃)進的是審查完之後的版本,pass 通過時那份差異沒有被審過。spec 沒提這個後果。
引句:「它自己的前置檢查(工作目錄除簿記檔外乾淨、範圍右端是 HEAD、有計劃與可守的測試)不過就印原因回 2;它的 rc 不用,改看第二次判定。」

## 實務隱患鏡頭

- 守衛面:有。見 finding 3、6、8。「擋錯的代價小」成立,因為有 `code-loop skip`,但 finding 3 的範圍不同會讓 pass 通過後推送才被擋,正是這份計劃要消滅的情形。
- 耗時與中斷:有。見 finding 2、5。
- 資料與帳:有。見 finding 7(重複擋下事件計數)和 finding 8(只讀工作目錄帳與推送前不同,S7 已涵蓋)。治理帳是 append-only,重跑冪等,沒有發現會損壞帳的路徑。
- 空與邊界:新分支首次 pass(沒有主線)走 `_codeloop_default_range` 回 None 後 fail-open 並記帳,合理。範圍等於 HEAD 靜默放行,正確。單一壞法、空計劃、只改測試檔走 `_choice_requirement` 回不要求,正確。超大(30 個以上壞法)見 finding 2、7:spec 已寫「重跑會接著跑」。
- 金流、對外送出、不可逆:無。spec 已寫排除理由。Gradle 冷編譯會下載套件,是既有行為,且 `choice-kill` 只寫治理帳。
- 併發:依題意不考慮。

最嚴重等級 major,blocking 共 3 條
