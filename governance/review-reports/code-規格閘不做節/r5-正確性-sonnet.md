severity: major

**Finding 1**

severity: major
blocking: 是 — 不改計劃、只重跑一次規格閘,就能洗掉輕量審抓到的 major,導致沒有真的輕量審卻推得上去。
引句:「每遇到一筆規格閘留痕就重開窗口:舊的審查、舊的 major、舊的帶輪次紀錄都不再算」
問題:`_nogo_light_window` 遇到任何一筆 `kind=spec-gate` 的帳列,就把窗口清空。`_light_gate_fails` 的 ratchet 和 `any("round" ...)` 都只看窗口。`_spec_gate_record` 每次 PASS 都無條件追加一筆留痕,沒有比對 `clause_sha` 或被略過的那幾行有沒有變。計劃的 `trade_offs` 與訊息文字寫的是「改了計劃重跑規格閘才會重開」,程式實際上不要求改過計劃。
具體失敗情境:
1. 計劃的不做清單夾帶了要做的事,規格閘判風險低,略過了危險詞。
2. 輕量審席報 major,依規矩應寫 `plan_risk: high` 改走完整設計審。
3. 作者不改計劃,再敲一次 `lumos spec-gate 計劃`。計劃沒變,所以照樣 PASS 並追加新留痕,窗口清空,major 不再算。
4. 再記一筆乾淨的席,`--spec`、`--snapshot`、`--reviewed` 都沿用同一份快照。快照裡被略過的那幾行跟現在的一樣,`_nogo_review_unbound` 放行。
5. 結果是推送前通過。含 major 的那份快照,同一份被略過的行,輕量審卻判通過。
- 這代表 r3 的永久 ratchet 被繞掉了,而且不需要改任何內容。
- 建議:窗口重開只在 `clause_sha` 或 `nogo_skipped` 跟上一筆留痕不同時才發生。或者讓 ratchet 也計入較早窗口裡、快照被略過行與現在相同的 major。
- 佐證:``file: `scripts/lumos:9188-9200` ``(窗口函式)、``file: `scripts/lumos:8232-8252` ``(留痕無條件追加)、``file: `scripts/lumos:8890-8894` ``(PASS 後即記)。

**Finding 2**

severity: minor
blocking: 否 — 只是多擋、可以補審解開,不是漏審。
引句:「推送範圍改到的計劃(touched_plans)不論狀態、不論有沒有留痕,不走全套的也要重判一次不做清單」
問題:範圍內任何被碰到的 Projects 筆記都會重判,包括 done 或 superseded 的舊計劃。這類檔走 `_spec_gate_push_nogo_only`,而且不經過 `_spec_gate_push_stale`。舊計劃的不做節本來就有「退款」之類的詞,被新的略過邏輯判成低風險且略過了危險詞時,只要被碰到就被擋。
具體失敗情境:一次全庫的改欄位或改連結,順手動了 N 份舊計劃。其中符合上述條件的,每份都要補一次 `spec-gate` 加輕量審。
- 此處我沒有量到實際數量:目前圖譜 342 份 Projects 筆記裡,新邏輯下被略過行數為 0。
- 屬於設計取捨,不是漏洞。
- 佐證:``file: `scripts/lumos:9324-9350` ``(`_spec_gate_push_scan` 的 touched_plans 分支)。

**已讀,無 finding 的部分**
- 快照路徑解析:相對路徑以 repo 根為準,搬 worktree 不受影響;repo 外的絕對路徑照樣能讀。`_at` 兩邊都 resolve 並 NFC,比對沒問題。範本把快照放進 `governance/review-reports/<編號>/`,並提醒別放會被清的暫存目錄。
- 被略過行的比較:我用合成計劃實測,LF、CRLF、BOM、CR 行尾算出的行集合一致。快照與現況走同一支 `_nogo_skipped_rows`,排序後的 list 型別相同。
- 推送範圍的檔名清單:刪檔時 `is_file()` 為假,直接略過。改名時 git 對新路徑有輸出,迴圈編號改變,要重跑規格閘並重審。新增檔案同樣被重判。測試索引讀不動時,`idx=False` 的分支仍會重判輕量審。
- 席別要求、`_light_gate_fails` 新增的型別檢查、治理事件寫入失敗的處理:沒問題。
- 範本流程:`loop next` 的 `record_cmd` 在 light 下不帶 `--round`,端到端測試「照範本走完 → 推送前 rc0」涵蓋了合法流程。
- 重判成本:我以空樹範圍整庫跑推送前檢查,耗時 28 秒,多半是既有的測試真跑,看不出新增的重判有額外問題。
- 資料狀態五問:
  - 缺欄位(舊帳沒有快照)會擋,屬正確的升級成本。
  - 型別錯誤會走 `bad` 分支。
  - 超深巢狀行只跳過那一行。
  - 空窗口與窗口前有紀錄各自有訊息。
  - 帳檔讀不到會擋。

最高等級 major,blocking 1 條。
