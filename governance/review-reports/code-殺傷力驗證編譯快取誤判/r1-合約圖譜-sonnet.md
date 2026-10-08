severity: minor

## F1 Systems/guard-kill 對 weak 的定義沒跟著新增第四個成立條件
severity: minor
blocking: 否
引句:「res["weak"] = bool(mk["ws"] or mk["flaky"] or node_dirty or res.get("_mtime_unsure"))」
佐證行:file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:33`
1. 該行(WHY,2026-10-01)寫 weak 是「整套一起跑、flaky 平台、配方所在筆記有未提交改動任一成立」,diff 之後多了「寫檔後修改時間沒能錯開」第四個條件,筆記沒補。計劃〈要同步的文件〉明列要改 CLI 一節「與 rc/弱證據那條」;CLI 一節(第 72 行)已寫,但第 33 行的 weak 定義與第 74 行 rc/弱證據那條未動。
2. 影響有限:此行屬 WHY 線索,不是 ★INVARIANT★;weak 的讀者(guard kill 背書算法,scripts/lumos 約 39495、39533 行)只看 `verdict=="killed" and weak is not True`,語意方向一致(多一個弱的來源只會更保守),所以不會算錯。僅是下一個 session 讀第 33 行會漏掉這個成立條件。
3. 建議:第 33 行 weak 清單補一項「修改時間沒能跟上一次錯開」,並指向第 72 行。

## 核對結論(無問題項)
- rc 優先序:rc 只由 verdict 計算,weak 不參與;`_mtime_unsure` 只改 weak,不改 verdict,與 ★INVARIANT★ rc 優先序無衝突。實跑 `-k t_guard_kill_rc_precedence` 4 passed。
- --json 純度:警告走 `file=sys.stderr`,旁路欄 `_mtime_unsure` 加進 --json 濾除清單;實跑 `-k t_guard_kill_json_purity` 6 passed、`-k t_guard_kill_mtime_unsure` 3 passed。
- kill-log 欄位:寫入的欄位集合未變(仍是 covers/recipe_id/head_sha/weak 等),`_mtime_unsure` 不入帳,只透過 weak 反映;讀者(背書計算、`_kill_log_for_backing` 型別檢查 weak 必須是布林)仍收到 bool,因為 `bool(...)` 包住了。
- Issue「guard kill在Python專案會沿用編譯快取誤判殺得掉」已寫 2026-10-02 已修、status: done,與實作一致;計劃〈做法〉S1–S4 與 diff 逐項對得上(寫前等、寫後確認、收尾重算 weak、標準錯誤一行)。
- weak 其他 grep 命中(spec-gate、lint 新增告警、symbol_weak)是不同語意的同名欄位,不讀 kill-log,不受影響。

最高等級:minor
