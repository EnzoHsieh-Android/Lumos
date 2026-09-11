severity: major

## 問題一:分層與依賴方向

對齊。新函式 `_search_counts`(`governance/eval/lens-utilization/recount.py:926`)是純文字解析函式,跟既有的 `_search_verdict`(`governance/eval/lens-utilization/recount.py:898`)放在同一段、同一層,只被 `_search_events`(`governance/eval/lens-utilization/recount.py:931`)呼叫,沒有再往下叫別的層。`_search_events` 取代舊的 `_search_event`,呼叫端還是原本那兩個入口——`search_events_claude`(`governance/eval/lens-utilization/recount.py:969`)與 `analyze_codex`(`governance/eval/lens-utilization/recount.py:1020`),兩條路徑一樣共用同一個事件產生函式,沒有新增跨層直呼、也沒有繞過既有入口。

不對齊:無。

## 問題二:命名與錯誤處理

對齊。事件 dict 仍是 `ts`/`query`/`verdict` 三欄(`governance/eval/lens-utilization/recount.py:939`);摘要欄位 `search_zero_unattributed` 沿用既有 `search_zero`/`search_undetermined` 的 `search_` 前綴(`governance/eval/lens-utilization/recount.py:1116-1118`);週檔 local 檔的欄位 `zero_unattributed` 去掉前綴,跟同一段既有的 `undetermined`(也是去掉 `search_` 前綴)寫法一致(`governance/eval/lens-utilization/recount.py:1142-1144`)。`lens_weekly.py` 新插的 LOG 分句用既有的「(另有 …)」插入語氣接進原本那句(`governance/autonomous_loop/lens_weekly.py:49-51`)。回傳形狀從單一 `dict | None` 改成 `list[dict]`,呼叫端同步從「有才 append」改成 `+=` 收集,跟檔案裡其他多值收集(如 `reads.append`)同款。

⚠ 有一點判不準,列出來給編排者看,不硬判:新欄位 `zero_unattributed` 是「有才寫」(`z` 為真才塞進 `evs[0]`),下游都要用 `.get(..., 0)`;同檔案裡 `zero_push`/`cooldown_inherited` 這類欄位是「永遠有、給預設值」(`governance/eval/lens-utilization/recount.py:679`)。但同一份檔案 Codex 段落的 `row["ambiguous"]` 本身也是「條件式才塞」(`governance/eval/lens-utilization/recount.py:332`),Claude 段落同名欄位卻是「永遠有」(`governance/eval/lens-utilization/recount.py:403`)——鄰居檔自己兩種寫法都在用,判不出這次改動該對齊哪一種。

不對齊:無(判不準的一點已標⚠,不計入 Bx)。

## 問題三:第二種做法

不對齊,一條:

B1
severity: major
blocking: 是
引句:「SEARCH_COUNT_ANY = re.compile(r'(?m)^\((?:共 (\d+) 篇候選|候選 (\d+);)|^(\d+) 處 / (\d+) 篇|"candidates":\s*(\d+)')」
file: `governance/eval/lens-utilization/recount.py:868`
這行把既有 `SEARCH_RANKED`(`governance/eval/lens-utilization/recount.py:860`)與 `SEARCH_LEGACY`(`governance/eval/lens-utilization/recount.py:862`)的字面樣式原封抄成一份新常數,還另外用字串正規式 `"candidates":\s*(\d+)` 抓 JSON 欄位;同一件事(從輸出判斷 candidates 計數)本來 `_search_verdict`(`governance/eval/lens-utilization/recount.py:898`)是用 `json.loads` 真的解 JSON。現在單一搜尋走 `_search_verdict`(JSON 解析+既有兩個正規式+結果行 fallback),多重搜尋走新的 `_search_counts`(`governance/eval/lens-utilization/recount.py:926`)配 `SEARCH_COUNT_ANY`(正規式硬配、沒有結果行 fallback),同一件事兩套判法,不是共用或改寫既有正規式與既有 JSON 解析。

不對齊共 1 條,其中 major 1 條,全份最高嚴重度是 major。
