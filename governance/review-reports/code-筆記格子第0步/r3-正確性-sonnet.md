severity: minor

我逐 hunk 讀完 diff,也在 repo 內跑了相關測試子集。這批修正本身沒有走錯,第 2 輪的四項修正都修對了。新發現兩條 minor,都不 blocking。

測試結果:`t_slots_see`、`t_doctor_lists_stale`、`gov_stats_gate`、`doctor_s7` 子集都綠。

圖譜鏡頭:`lumos-cli-read` 的 WHY 摘要行已補上「共用 `_rule_stale_keys`、治理帳一篇一筆」。這個改動沒有新增合約,也沒有改動既有的 `[test:]`。我判不影響其他節點。

**R3C1**
severity: minor
blocking: 否 — 只是治理帳的測試沒釘住,不會做出錯行為。
引句:「                if n.stem not in _nodes16:     # 一篇一筆事件,同篇多條 RULE 不重複記」
- 這條去重是本輪的修正重點,但沒有任何測試咬住它。
- `t_doctor_lists_stale_rules` 的 fixture 在同一篇 `Systems/R.md` 放了三條過期 RULE,正好能測去重。但測試只斷言 `"gate": "check-s16"` 字面值在原始碼裡,沒有跑出治理帳數筆數。
- 變異驗證:拿掉 `if n.stem not in _nodes16` 這層判斷,該測試仍然全綠。
- 建議在 fixture 上斷言只落一筆事件。
- 順帶一點:去重的鍵是 `n.stem`,同 stem 不同資料夾的兩篇會被併成一筆。但事件的 `nodes` 欄本來就只寫 stem,所以只是名義上的漏記,影響很小。若要貼合「一篇一筆」,可改用 `rel` 去重。

**R3C2**
severity: minor
blocking: 否 — 提示文字的前綴沒有測試保護,不影響擋或放行。
引句:「        return ([f"筆記格子『RULE:』{w}" for w in slot_check("RULE", rest, commit_time=True)]   # 字樣同 lint 那條路」
- 本輪第 4 項(提交時的格子提醒補前綴)沒有對應測試。
- 變異驗證:把前綴拿掉,既有測試仍然全綠。
- 提交時的提示因此可能悄悄退回無前綴的版本。
- 另外,lint 那條路會在警告後面附 `:{rest[:40]}`,提交時這條路沒有。這是格式差異,不算錯。

**已查項目(無問題)**
- **SEE 判斷:** 新條件 `"[[" not in body or not _NS_POINTER_ONLY_RE.match(body)` 與 `slot_check` 的 SEE 分支(`scripts/lumos:3589`)逐字一致。
  - `SEE:[[Systems/甲]]、[[Systems/乙]]` 放行。
  - 空的 `SEE:` 骨架因 `body` 為空而放行。
  - `SEE:見`、`SEE:、` 沒有 `[[`,會擋。
  - `SEE:Redis 連線上限是 200` 會擋。
  - 變異驗證:把條件還原成舊版,`見` 會被正則放行,新測試因此翻紅,所以這條測試有咬住。
- **`_KNOWN_GATES` 加註解行:**
  - 搜尋 `_KNOWN_GATES = (` 的有兩處,都是取第一個 `)` 當結尾:`scripts/test_lumos.py:2624` 和新測試 ⑤。
  - 新增的註解沒有 `)`,`check-s16` 仍在第一個 `)` 之前。
  - 第一個 `)` 落在後面註解的「(code-loop 已在上面)」。這很脆弱,但目前成立。若有人把含 `)` 的註解插到 `check-s16` 之前,⑤ 會假紅。
  - `t_gov_stats_gate_drift` 的剝註解掃描,以及 `lumos:3555`、`lumos:1220` 的成員檢查,都不受註解影響。
  - 變異驗證:刪掉 `"check-s16"` 字面值,⑤ 會翻紅。
- **測試 ⑥:** `_rule_stale_keys` 的期待值 `["until","confirmed"]` 正確,`[confirmed:2026-09-30]` 回 `[]` 也正確。

最高嚴重度 minor,blocking 0 條
