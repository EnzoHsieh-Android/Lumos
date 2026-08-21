# doctor-run事件-std r2-s3 對抗審計 — LENS: consumers delta (CI/hooks/vendored consumers)

角色：獨立第三方審計，對抗但憑事實。對象=`/tmp/doctor-run事件-std-r2.md`（DELTA 輪，對照 r1-snapshot.md 找差異）。範圍=dr-common 指定 LENS：這一輪的 fold 有沒有新東西影響 consumers/CI/hooks，若有則確認不留 ≥major。

## r1→r2 實際差異（逐字比對 r1-snapshot.md 與 r2-snapshot.md）

只有三處變動，全部落在「設計」段與「審計修正紀錄」段：

1. 新增「已清的判讀方式」一段（nodes 恆空、由讀帳方以「run 邊界內無該節點 check-* 事件」推導已清；明講回應外家 r1 #1 的誤讀）。
2. 過濾段落重寫：從「在去噪摺疊之前、以 gate 名直接濾」改成「過濾只作用在**顯示迴圈的印出動作**（摺疊與逐行印兩處各自 `continue`），絕不改動 `ded` 列表本身」（修 std r1 s1 的 major）。
3. 測試 3 從「`gov --stats` 列出」加強為「`doctor-run` 列去重筆數 **== 2**」（斷數字，堵住「濾錯 `ded` 仍假綠」的洞）。
4. 「審計修正紀錄」段落新增 std r1 一行摘要（含 s3 消費者席發現的既有 `.gitignore` 放錯層問題，記為非本案引入）。

以上四點沒有一處觸及 CI workflow、pre-push hook、`_BOOKKEEPING_FILES`、vendor 範本（`_scaffold_project`/`_vendor_toolchain`）——即這輪 fold 完全是 `cmd_gov` 內部顯示邏輯與測試斷言的修正，**consumers/CI/hooks 面本輪沒有新的變更面。**

## 對照真代碼複核修正是否真的成立

- `scripts/lumos:3038-3078`（`cmd_gov`）：`ded` 在第 3033-3037 行 dedup 建好後，同時餵給 3140 行 `_render_gov_stats(_raw, ded, ...)` 與 3042 起的 `full`/else 印出分支——結構上「印出迴圈」與「傳給 stats 的 `ded`」確實是分岔點，r2 描述的落點（`continue` 只發生在兩個印出分支內部）是唯一能同時滿足「時間軸不印」與「stats 照列」的寫法，與 std r1 s1 的 major 診斷、r1-s2 的獨立複核（`scripts/lumos:3042-3078` if/else 結構比對）一致。**修正落地位置正確。**
- `scripts/lumos:2993`：mapper 讀 `d.get("note", "")`（非 `detail`），與「已清判讀」新增段落、light r1 M1 修正互相印證，未變。
- Test 3 的 `== 2` 斷言：若日後實作把過濾錯放到 `ded` 本身（filter 前置），`_render_gov_stats` 的 `ded` 桶會是 0（`agg[gate]["ded"] += 1` 對 `doctor-run` 永遠不執行），去重筆數斷言會直接失敗而非只憑「gate 名有沒有出現」矇混過關——堵洞邏輯成立。

## 消費者面既有事實複查（Q1-Q5，對照 r1-s3 已核對的結論，本輪未變）

- `pre-push:148` 仍是 `doctor --ci`（非純 `doctor`），`.github/workflows/ci.yml:25` 仍是 ephemeral runner 上的 `python scripts/lumos doctor --ci`——CI 不做 `git diff --exit-code`/porcelain 比對，不會因帳本恆變翻紅。
- `_BOOKKEEPING_FILES`（`scripts/lumos:10299-10300`）仍含 `docs/.governance-log.jsonl`，code-loop 簿記豁免通道不受影響。
- `_scaffold_project`（`scripts/lumos:8960-8971`）的 `.gitignore` 仍寫在 `kg/.gitignore`（vault 內），帳檔實際寫入點在 `vault.parent`（`docs/`）——放錯層、蓋不到，此既有落差原樣未動。此外，`governance/l4-audit/2026-08-21/reversibility-governance-ledger.verify.md` C11 已獨立核實同一事實（`git check-ignore` 對六本帳檔皆回 NOT ignored，`git ls-files` 確認已被追蹤）——與 r1-s3 的實測結論互相印證，**非本輪新發現，是既有、已有另一條審計線在追的事實**，`governance/golden/cochange-guard/spec.md:48` 的排除清單也顯示這幾個帳檔本就被系統當「治理帳」特殊處理（排除於 co-change 掃描外），不受本案影響。

## 判定

本輪（r1→r2）fold 只動了 `cmd_gov` 顯示邏輯的落點描述與一條測試斷言的精度，範圍完全在圖譜設計文件與既有 `cmd_gov`/`_render_gov_stats` 結構內部，**沒有任何新東西碰到 consumers/CI/hooks/vendoring 面**。r1-s3 原本點出的唯一相關項（帳本恆變在消費專案 fleet 上被放大、且既有 `.gitignore` 放錯層）維持 minor、非本案引入、範圍刀明確排除，且已有獨立審計線（l4-audit reversibility-governance-ledger）在追蹤同一事實，不因這輪 delta 而升級。

**沒有 ≥major 殘留。**

findings: blocker=0 major=0 minor=0（本輪范围内；既有 r1-s3 minor 1 項未變、未新增）
