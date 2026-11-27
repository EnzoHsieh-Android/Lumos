severity: major

**圖譜鏡頭**:`lens-r1.txt` 沒附、固定席節點未知,我沒讀圖譜節點。這一項不判定,也不影響下面的程式面結論。

白話:這批改動的主幹(合批編譯、換候選、還原、抽查)大致站得住。但有兩處壞掉:一處新行狀態會讓指令崩潰,一處補償機制在常見情況下形同虛設。

### Finding 1:`exhausted` 行讓 `situation-rule --point` 丟 KeyError

severity: major
blocking: 是

`scripts/lumos:81637`(`_situation_rule_point_target`)。這份 diff 新增了行狀態 `exhausted`,`_choice_line_pick` 在候選全在跳過集合時設它。`_choice_kill_scan(..., skip=None)` 會自己讀帳算出跳過集合,所以這條路會產生 `exhausted` 行。

但 `x["status"] != "mutant"` 之後那個查表只認 `None`、`arid`、`none`、`not_unique`,沒有 `exhausted`。對 `exhausted` 的行跑 `lumos situation-rule --point <檔>:<行>`,會丟 `KeyError: 'exhausted'` 並印 traceback。正確行為是印「沒有可用壞法」並 rc 2。

最小重現:把 `_choice_kill_scan` 換成回傳一行 `{"file":"a.kt","line":3,"status":"exhausted","mutant":None}`,再呼叫 `m._situation_rule_point_target(None,"a.kt:3",None,None)`。實跑結果是 `KeyError 'exhausted'`。

對比 `_choice_waive_target`(`:81585`)雖然沒崩,但把 `exhausted` 講成「沒有壞法」,不夠精確。

引句:「    x = next((y for y in res["lines"] if (y["file"], y["line"]) == loc), None)」

這句在 `_situation_rule_point_target`,原檔 `:81634`,屬於 diff 外。diff 內的對應引句是 `_CHOICE_STATUS_TEXT` 新增的 `"exhausted"`。

引句:「+_CHOICE_STATUS_TEXT = {"none": "沒有壞法", "arid": "乾節點", "not_unique": "不唯一", "unrun": "沒跑", "exhausted": "沒有可用壞法"}」

diff 只更新了這張表,漏了同族的第二張表 `:81637`。測試 `t_choice_compile_batch` 只驗了 `choice-points` 與推送閘,沒驗 `--point` 對 `exhausted` 行的行為,所以抓不到。

### Finding 2:探針整批全綠才補償,一個永久編不過的探針會讓同批所有補償失效

severity: major
blocking: 是

`_KillCompile.probe`,patch 約 `:765`~`:778`。這是實作者的偏離「探針整批全綠才補償」。

規格〈用詞〉跳過集合(`選擇點存活回指條款_計劃.md:81`)要求「能編了就記補償」,是逐候選的語意。實作把每行第一個舊候選全套進同一批,只要整批 rc 非 0,一個都不記。

一條真的永久編不過的舊候選會留在 `live` 裡。條件是 blob 不變且每次 `at_sha` 不同,所以它每次 run 都被放進探針批,批次必紅。別條行的候選即使已經能編了,也永遠補償不到,一直被跳過。

重現(實跑):用兩行 stub 呼叫 `_KillCompile.probe`。A 行舊候選真的編不過,B 行舊候選現在能編。結果 `on_invalid` 呼叫清單是 `[]`,B 沒被補償。

測試 `t_choice_compile_probe` 只有單一行,抓不到這個。

引句:「+        if got is None or got[0] != 0 or got[2]:」

建議做法是比照 `one_batch`:整批紅時退回逐個單獨編,或二分。

### Finding 3:`--reach-only` 也會跑合批編譯並寫 `invalid` 事件、換候選

severity: minor
blocking: 否

`_choice_reach_only` 把 `run_opts` 原樣傳下去,只覆寫 `audit=0`,`compile` 沒清掉。`_choice_prep_attach` 因此在 `--reach-only` 下也建出帶 `compile` 的準備物件,`_KillPrep.run` 先做 `_KillCompile`。

規格與 docstring 說 `--reach-only` 只量覆蓋、不動壞法。實際會多編幾次,並寫 `invalid` 事件、改動 `plan_of`(候選用完的行被拿掉,於是補不到 reach)。覆蓋分類不依賴壞法內容,所以這些編譯是白花時間,還寫了不該寫的帳。

引句:「+    _choice_prep_attach(kr, rr, at_sha, cov_plats, cov_sha_of, blobs, max_seconds, t0, dict(opts or {}, audit=0))   # 不跑壞法,不抽查」

### Finding 4:多平台時,換候選會清掉前一個平台組已跑出的列

severity: minor
blocking: 否

`_ChoiceKillRun.on_swap` 裡的 `p["x"], p["rows"], p["plats"] = nx, {}, set()`。

平台 A 組先跑完(列已入 `p["rows"]`),平台 B 組的合批編譯才發現同一行候選編不過而換候選。此時 A 的舊列被清空,A 對新候選的配方也不會再跑,因為 A 的組已結束。`p["order"]` 仍含 A 的測試,這行永遠湊不齊列,最後落成「缺結果」。

這是理論上的多平台邊界。預設只有 Android 平台開 `compile_check`,觸發機率低。

引句:「+        p["x"], p["rows"], p["plats"] = nx, {}, set()」

### 已逐項檢查、判定沒問題的項目

- **寫一半中斷**:`apply_compile` 的 `finally` 與 `restore` 涵蓋「寫到第二支檔失敗」,`wrote` 在寫前就登記。內容比對在文字模式下兩邊都做通用換行轉換,CRLF 不會誤判。
- **預算**:`cap()` 與 `csecs` 沒有重複計時。
- **舊帳**:缺 `invalid`/`cov-audit` 的舊帳,`_choice_skip_read` 提早回空,`_choice_ledger_aux` 的新欄位不影響既有的 `.get("reach")`。
- **既有帳欄位型別**:新增的 `_GOV_FIELD_TYPES` 鍵(`killed`、`wrong`、`blob`、`at_sha`、`compile` 等)我對 repo 內現存各本帳掃過,沒有型別撞名。
- **配方編號**:`_kill_recipe_id` 由節點、invariant、file、old 組成,換候選的 `#<new_sha 前 8 碼>` 後綴能避免撞號。
- **`exhausted` 在推送閘**:`n_need` 只算 `mutant`/`not_unique`,不會擋。
- **截斷標記**:`...[truncated ` 與 `_kill_cap` 的實際輸出一致。
- **實作者 11 項偏離**:除了 Finding 2 的「探針整批全綠」會做錯事,其餘我沒找到會出錯的輸入。
  - 「cov-audit 判錯也計入 clause 抽查」讓 `_choice_cov_wrong` 比規格字面更廣(規格只講 none 行被殺掉)。這是更保守的方向,可接受。
  - 「只抽單一平台的行」與「換到的下一個候選不唯一就這次不跑」都是 fail-open,可接受。

### 測試獨立判準

`t_choice_compile_batch` 等測試的預期值(`_ckcc_sha`、編譯順序)是獨立於實作算的,符合〈實作測試品質〉。缺口是前面兩處:`exhausted` 在 `--point` 路徑,以及多行探針。

總結:最高等級是 major(2 條 major、2 條 minor)。
