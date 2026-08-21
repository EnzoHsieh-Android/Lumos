# doctor-run事件-std r2 — s2 delta review（LENS: ledger semantics）

角色：外部第三方對抗審計。標的：`/tmp/doctor-run事件-std-r2.md`（尚未實作 — `scripts/lumos` 全檔搜尋 `doctor-run` 零命中，本輪純審 spec 對現有 code 的描述是否準）。

## 逐點核對

### 1.「過濾只作用在顯示迴圈的印出動作（摺疊與逐行印兩處各自 continue）」

實地讀 `cmd_gov` 的非 `--full` 分支（`scripts/lumos`）:

- 3040-3041 `_is_advisory`：`kind == "warned"` 才算 advisory。doctor-run 事件 `kind="ran"`，恆為 `False`。
- 3048-3057：**聚合迴圈**（loop1）——只在 `_is_advisory(r)` 為真時才標 `_agg`/`_drop`，本身不印任何東西。
- 3058-3077：**顯示迴圈**（loop2，spec 講的「顯示迴圈」）——內部恰有兩個印出點：
  - 3062-3076「摺疊」印出（`if r.get("_agg")` 分支，大群組摘要 3072 / 小群組逐節點 3075，統一以 3076 的 `continue` 收尾）
  - 3077「逐行印」（未進 `_agg` 的行的兜底印出，doctor-run 唯一會落地之處）

spec 說「過濾只作用在顯示迴圈」——這句本身**準確**，正確排除了 loop1（loop1 沒有任何 print，掛在那裡的 continue 不會影響輸出，也不會誤傷 `--stats`）。這正是 LENS 提出的疑慮（loop1 vs loop2 是否會混淆）的答案：spec 用「印出動作」四字已經把 loop1 排除掉，不是含混語。

但「摺疊與逐行印兩處各自 continue」這句**略為過度規定**：由於 doctor-run 的 `kind="ran"` 恆不滿足 `_is_advisory`，它**永遠不會**被標 `_agg`，因此永遠走不到 3062-3076 的「摺疊」印出點——只會落在 3077 的兜底印出。也就是說，兩處各設一道 `continue` 裡，摺疊分支那道是死碼（該分支對 doctor-run 永遠不可達）。真正扛住過濾責任的只有 3077 前面那道。單一 `continue` 放在 3059 `if r.get("_drop"): continue` 之後即可覆蓋兩個印出點（因為擋在 loop 開頭，兩個下游印出點都進不去）。

依 HARD RULES 的 major 定義（字面實作誤動作或弄壞消費者）——**這條不到 major**：照 spec 字面「兩處各自加 continue」實作出來的程式，行為仍然正確（多一道摸不到的死碼分支，無害）。只是「兩處」比實際需要的更囉唆，屬 minor 精確度瑕疵，不影響任何消費者。

引句：「過濾只作用在顯示迴圈的印出動作」

**severity: minor** — 描述本身方向正確且已排除掉 loop1/loop2 混淆的疑慮；「兩處各自 continue」對「摺疊」分支而言是不可達的死碼保險，非必要但無害，不構成字面實作誤動作。

### 2.「`gov --stats` 的 `doctor-run` 列去重筆數 == 2」測試可行性

dedup 鍵（`scripts/lumos:3030`）：`(r["commit"], frozenset(r["nodes"]), r["gate"], r["kind"], r.get("token", ""))`。doctor-run 事件恆 `nodes=[]`、`gate="doctor-run"`、`kind="ran"`、無 `token`——五元鍵裡只剩 `commit` 會變動。若測試跑兩次 `doctor --ci` 但中間沒有真的換 commit，兩筆事件鍵完全相同 → `ded` 只留 1 筆，`--stats` 斷言 `count == 2` 會**假紅**（不是假綠，是測試寫錯會導致測試本身跑不過，逼人發現）。

Spec 文字已自帶但書「跑兩次 `doctor --ci`（不同 commit）」——與上述 dedup 鍵分析一致，spec 本身沒有掉這個坑。

測試可行性：`scripts/test_lumos.py` 沒有一個叫 `_git_two_commits` 之類的專用 fixture，但「同一個臨時 repo 內連續兩次真實 commit」的樣式在既有測試裡重複出現超過 10 處（如 5408/5410、8441/8450、8462/8466、9472/9480 行，皆為「改檔→`git add -A`→`git commit -qm`」重複兩次），是抄得到的現成套路，不是要新造 fixture 能力。`t_governance_log_write`（scripts/test_lumos.py:2914-2933）也示範了「真 git repo + `run(vault, "doctor", "--ci")`」的最小骨架，只需在中間插入第二次「改檔+commit」再跑第二次 `--ci`。

引句：「跑兩次 `doctor --ci`（不同 commit）」

**判定：測試可達成，非阻塞。** 需注意實作測試時必須是「兩個不同 commit」而非「同 commit 跑兩次 --ci」，spec 文字已明講，且原始碼的 dedup 鍵分析也印證這個要求是必要而非多餘。

## 其餘核對（均與 code 相符，未發現新增問題）

- `_append_governance_log` 空事件 early-return（`scripts/lumos:421-424`）未被要求更動，spec 範圍刀一致；因 doctor-run 恆無條件塞入，`--ci` 路徑此後事件永不為空，early-return 對 `--ci` 呼叫點形同不可達，但這是 spec 明確意圖非疏漏。
- `note` 鍵讀取：`.governance-log.jsonl` mapper 的 `detail: d.get("note", "")` 已是現況（cmd_gov 內），與 spec 修正後的鍵名一致。
- `_KNOWN_GATES` 漂移測試（`t_gov_stats_gate_drift`，scripts/test_lumos.py:3047-3062）掃字面值 `"gate": "..."`，新增 `"gate": "doctor-run"` 字面值會被抓進 `lits`、逼人補進 `_KNOWN_GATES`；且此寫法不會撞到「動態閘名寫點恰為 1 處」的第二道釘（`r'"gate": [^"]'` 只認非字串字面值），與 spec 第 4 條測試描述相符。
- node 縮限模式：`scripts/lumos:3035-3037` 的節點過濾對「nodes 恆空」的 gate 天然排除，不需特判，與 spec 相符。
- `_render_gov_stats` 的 nodes 欄：doctor-run 的 `nodes` 集合恆空 → 印 `n/a`（`scripts/lumos` `_render_gov_stats` 內 `nd = "n/a" if not a["nodes"] else ...`），`_STATS_NODE_SEMANTICS` 確實不必加項，與 spec 相符。
- `issues=<n>` 可行性：`issues` 計數器（`scripts/lumos:452` 起）在 `--ci` 落帳點（1327-1328）之前已無任何後續遞增（僅 468/509 兩處直接寫，其餘經 `nonlocal issues` 的 `warn()` 閉包在 Check A-N 段落內完成，皆早於落帳點），數值到落帳當下已定型，可安全取用。

## 結論

本輪 delta 未發現 blocker/major。唯一值得記錄的是「摺疊與逐行印兩處各自 continue」的措辭略為過度規定（其中一道 continue 對 doctor-run 是不可達死碼），屬 minor，不影響功能正確性，可留給實作者自行判斷是否簡化為單一 continue。

count: 1
