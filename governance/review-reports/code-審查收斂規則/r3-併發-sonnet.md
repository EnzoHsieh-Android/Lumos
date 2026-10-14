severity: minor

**測量結果(實跑)**
- 治理帳實際 122,102 列、20MB,對最老提交到 HEAD 的最大範圍跑 `_residual_tier_hits`,共 0.2 秒,記憶體峰值約 115MB。`git diff -U0` 這段單獨 0.06 秒,輸出 20MB。
- `_residual_ask_index` 讀整本帳是 0.13 秒、約 102MB。帳大本身不是問題。
- 我另造臨時倉庫測 `_residual_ask_rows_dropped`。刪一列 testable 回 1。整本帳改成 CRLF 時,剩下的 residual-ask 列全被算成刪除,0.21 秒。方向是多升 high,不會漏。實驗目錄已刪。

**finding**

severity: minor
blocking: 否 — 只在檔名清單的 git 呼叫失敗、且索引沒有任何殘留時才漏,機率低,而且同一時間 git 多半連帳的差異也讀不了。
引句:「if whole or bguard or hguard:」
問題:`git diff --name-only` 失敗或逾時(`names is None`)時,新加的 residual-ask 帳列檢查被早退跳過。早退只在索引有殘留時才記 `files_unknown`,否則直接 `return out`。`asks_dropped` 排在早退之後,所以這種情況下根本沒跑。
具體失敗情境:工作流程是先記 residual-ask(判 testable),此時合約行還沒掛 `[residual:]`,索引是空的。這時刪掉那列再推。若剛好遇到檔名清單 60 秒逾時,`whole`、`bguard`、`hguard` 全空,結果回 `{}`,不升 high。這正是這輪要堵的「刪 testable 問答重問」路徑。修法是把 `asks_dropped` 的判斷搬到早退之前,或檔名清單失敗時不論索引有沒有殘留都直接去查帳的差異。
佐證:file: `scripts/lumos:44532`(`_residual_tier_hits`,對應 patch 裡 `names is None` 那段)。

**已讀,無 finding**
- 逾時與失敗的方向:`git show` 與 `ls-tree` 逾時、版本不存在、物件遺失,都歸成 `unreadable`,再升 high(`base_bad` 或 `head_bad`)。空樹 `4b825dc` 的 `ls-tree` 回 0 且輸出為空,判為 `missing`,新分支首推不會誤報。`_residual_ask_rows_dropped` 逾時或 git 失敗回 None,再轉成 `asks_dropped=-1`,升 high。最壞時間約 200 秒(5 次 20 秒加 2 次 60 秒),全是 fail-closed。
- 帳差異的判讀:只看 `-` 行且含 `residual-ask`,再用 `gate` 欄精確比對。實際寫帳的 `_gate_event_build` 用的就是 `"gate"` 欄,比對得上。整本帳被刪或搬走時,每列都是刪除,會被算到。
- 索引比對再寫:`_residual_index_write` 在寫入鎖內重算、比對,相同才不碰檔。舊索引帶 `tests` 欄時,載入後不等於 `want`,所以會被重寫。符號連結或非一般檔走 `_write_refusal_reason`。`_write_lf` 是暫存檔加 `os.replace`,pitfalls 在 git 裡讀,不會讀到寫一半的檔。重算每次都走一遍測試檔,成本跟舊版相同,沒有新增。
- 所有 `_residual_index_write` 的呼叫端都已改成三元組,沒有漏改。
- 順帶看到,不屬於這輪修補:`scripts/hooks/pre-push:405` 的 `pf_json="$(... || true)"` 在 pitfalls 整支崩潰時 tier 會當成非 high。這是既有行為,patch 沒動它。

最高等級 minor,blocking 0 條。
