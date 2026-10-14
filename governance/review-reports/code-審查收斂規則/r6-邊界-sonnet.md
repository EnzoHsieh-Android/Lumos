severity: minor

在範圍內(`notes` 欄壞形狀、圖譜檔判定、測試殺傷力)我只找到測試覆蓋不足和一個索引壞形狀的靜默放行,沒有 major。破壞測試只跑完 M1、M2 兩個,M3 到 M6 因機器負載(其他會談也在跑測試)超過單一實驗 2 分鐘,中止了,沒結論。

severity: minor
blocking: 否 — 起點索引的 notes 寫錯時分級漏判,但漏判發生前已有 doctor 的 notes 比對與 `notes_moved` 把關,不是單次推送就能繞過。
引句:「nm = e.get("notes") if isinstance(e.get("notes"), dict) else {}」
問題:`_residual_index_notes` 只判斷 notes 是不是字串,不驗證路徑指到的是不是真正存著該決策的筆記。`_residual_note_hits` 也只拿路徑跟改動檔名比對。
具體失敗情境:我造了起點索引的 notes 值,再只改 `a_計劃.md`(決策本文)。四種壞形狀裡,值是 `../x.md`、值指到不存在的檔、大小寫不同(`A_計劃.md`,macOS 大小寫不分),三種得到 `light`(理由「改動裡沒有程式檔」),沒有任何提示;另一種是值為整數或空字串,走 `notes_unknown`,有升 high。字串型 notes、空字串、`./` 前綴、反斜線、NFD 路徑都有正確處理。
這種索引靠手改或搬家後忘了重建就會出現。起點索引壞掉的那次推送若不是剛好改了 notes,doctor 不會擋,分級就靜默放行。
佐證:``scripts/lumos: `_residual_index_notes`、`_residual_note_hits` ``(取代碼審 r5 G1 新增段)。

severity: minor
blocking: 否 — 只是測試沒守住判斷分支,實作行為目前是對的。
引句:「return rel.lower().endswith(".md") and any(f in segs for f in folders)」
問題:`_residual_graph_file` 的「路徑含殘留指標頂層資料夾的 .md」分支,我在工作樹副本把它改成 `return False`,清掉 `__pycache__` 後跑 `-k residual_decision_note`、`records_decision_note`、`lens_residual`,結果 10、6、42 全過,沒有紅。
具體失敗情境:測試的保險庫都命名成 `rc-knowledge`,第一個條件就成立了。圖譜放在別處(例如 `docs/notes/Projects/`)的專案,舊索引加改決策筆記這條路徑,沒有任何測試守著。這個分支壞了也不會紅。
佐證:``scripts/test_lumos.py:6194``(`t_pitfalls_residual_decision_note_touched` 只用 `vault="rc-knowledge"`)。

severity: minor
blocking: 否 — 同上,只是測試沒釘住 NFC 正規化。
引句:「if nfc(p) in changed:」
問題:我把它改成 `if p in changed:`,同一組測試也全過。`changed` 本身已先 NFC,但測試的索引路徑與 diff 檔名都是 NFC,NFD 不一致的情況沒有被測。
具體失敗情境:索引 notes 寫成 NFD 路徑時,現行程式碼正確,但這個行為沒有被任何測試釘住。以後有人把 `nfc(p)` 簡化掉也不會紅。
佐證:``scripts/test_lumos.py:6194``。

已讀,無 finding:
- `notes` 欄是整張字典、字串、整數值、空字串的情況,`isinstance` 都有處理(走 `notes_unknown`)。
- 含 `..` 的路徑在 `_lens_residual_decision` 被擋,只會退回 `vault_rel + 節點`。
- 筆記改名在 `--no-renames` 下舊路徑列為改動,會升 high。
- `_gov_ts` 對極端 ts 的處理與 `newest_first` 排序一致,讀不出的排最後。
- `_residual_graph_file` 的 `.lower()` 對大寫 `.MD` 有效。

未驗證:M3(`moved` 分支)、M4(排序)、M5(`.lower()`)、M6(`notes_unknown` 分支)的破壞測試沒跑完,這四條不能算測試有守住。符號連結形式的決策筆記、`#dN` 簡寫指標在非標準保險庫的情況也沒有跑到,實驗目錄已刪。

最高等級 minor,blocking 0 條。
