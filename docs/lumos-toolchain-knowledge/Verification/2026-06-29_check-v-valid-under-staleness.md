---
type: verification
status: pass
feature: Check V — valid_under 過期率軟提醒
commit: (pending commit)
date: 2026-06-29
valid_under:
  - "lumos doctor 架構完成(Check T/R/S/H/K 已實作)"
  - "_node_age_days() 共用函式存在(Task 1 實作)"
  - "_conds() 與 warn_soft() 內閉包可用"
  - "檔案位置：scripts/lumos 行 729 前、行 727 後"
revalidate_when:
  - "lumos doctor 結構變更(Check 順序/段位置移動)"
  - "_node_age_days() 簽名/邏輯改變"
  - "warn_soft() 行為改變(計 issues 或改 rc)"
---

# 驗證：Check V — valid_under 過期率軟提醒

## 變更範圍
- `scripts/lumos`: 在 Check K 區塊結尾(行 727)之後、`if ci:` 前(行 729)插入 Check V 邏輯
- `scripts/test_lumos.py`: 新增 `t_doctor_check_v()` 測試函式(3 個 assert)

## 實作概述

**TDD 流程**：
1. ✅ 寫測試 `t_doctor_check_v()` 檢驗：
   - `[V]` 段標題出現
   - `2/3 (67%)` 過期率計算(2 個 >90 天的節點/3 個總計)
   - 全新節點時 `0/1 (0%)` 或 `≤90` ok 行
2. ✅ 驗證測試 FAIL（doctor 無 Check V 段）
3. ✅ 插入 Check V 實作於 `run_doctor()` 內
4. ✅ 驗證測試 GREEN（3 個 assert 全過）
5. ✅ 全套件測試 GREEN（268 passed, 0 failed）

## 測試項目

| 測試場景 | 預期 | 實際結果 |
|---------|------|--------|
| 段標題 `[V]` 出現在 doctor 輸出 | ✅ "[V]" in stdout | ✅ PASS |
| 3 節點場景：2 個 >90 天、1 個新 | ✅ "2/3 (67%)" | ✅ PASS |
| 1 節點全新場景 | ✅ "0/1 (0%)" or "≤90" ok 行 | ✅ PASS |
| 全新 vault（無 valid_under） | ✅ "無 valid_under 節點" ok 行 | ✅ PASS |
| Check V 不計 issues、不改 rc | ✅ doctor rc=0，Check V warn_soft 無副作用 | ✅ PASS |
| 真實 vault doctor | ✅ Check V 印出 14 個節點，0 個 >90 天 → ok 行 | ✅ PASS |

## 關鍵設計決策

| 決策 | 理由 |
|------|------|
| **複用 Task 1 的 `_node_age_days(n)`** | 單一日齡計算來源，90 天紅標在 cmd_context + doctor Check V 統一參考 |
| **複用既有 `_conds(val)`** | 該函式已處理 frontmatter list/scalar/block scalar 展開，Check V 直接用 |
| **用 `warn_soft()` 不計 issues** | Check V 是「進場前提警示」，軟性(R3-MAJOR-3)，不應阻擋 doctor rc |
| **>90 天非 >=90** | 90 天是閾值，滿 90 天還算「最近」，>90 天才是「明顯過期」 |
| **只計 `_conds()` 非空的節點** | 無 valid_under 或空列表 = 無進場提示需量，不納入統計分母 |
| **rate 格式 `f"{n}/{total} ({rate:.0%})"** | 一致性：`2/3 (67%)` 可讀，0% 四捨五入避免 0.0% |
| **全部 ≤90 天 → ok 行** | 正向確認「無過期節點」，而非僅列數字 |

## 程式碼細節

Check V 插入位置與上下文（scripts/lumos:727-750）：

```python
# Check K 結尾（行 727）
    print()

# ↓ 插入 Check V（約 22 行）
    section("V", "valid_under 過期率 (進場提示覆蓋 + 日齡 proxy;軟提醒、不擋 CI)")
    vu_total, vu_stale = [], []
    for rel, n in sorted(notes.items()):
        if not _conds(n.fields.get("valid_under")):
            continue
        vu_total.append(rel)
        age = _node_age_days(n)
        if age is not None and age > 90:
            vu_stale.append(f"{rel}(已 {age} 天未更新)")
    if not vu_total:
        ok("無 valid_under 節點 (無進場提示需量)")
    elif vu_stale:
        rate = len(vu_stale) / len(vu_total)
        warn_soft(vu_stale,
                  f"{len(vu_stale)}/{len(vu_total)} ({rate:.0%}) 個 valid_under 節點 >90 天未更新(前提可能失效):",
                  "進場 lumos context 已會警示;>90 天者建議重核 valid_under、必要時標 stale 或建新 Verification")
    else:
        ok(f"0/{len(vu_total)} (0%) — 所有 valid_under 節點 ≤90 天")
    print()

# ↓ if ci: 段開始（行 751）
    if ci:
        _append_governance_log(env.vault, gov_events)
```

段落順序確認：T(★INVARIANT★) → R(可逆性) → S(自足性) → H(漏標) → K(★COMBO★) → **V(valid_under 過期率)**

## 自我審查清單

- [x] rate 計算正確：`len(vu_stale) / len(vu_total)` 產生 0~1 浮點，`:.0%` 格式化
- [x] ok 行條件：全 ≤90 天時印 `0/{len(vu_total)} (0%)` 而非省略
- [x] warn_soft 內容：說明故障原因 + 建議動作(重核/標 stale/建新 Verification)
- [x] 不計 issues：warn_soft 無 `nonlocal issues` 遞增，doctor rc 保持 0
- [x] 複用既有函式：_node_age_days(n) + _conds(val) + 內閉包 section/ok/warn_soft 無冗餘實作
- [x] 排序穩定：`sorted(notes.items())` 確保一致性
- [x] 邊界情況：無 valid_under → "無節點" ok；只有新 → "0/N (0%)" ok；全老 → "N/N (100%)" warn_soft

## 提交資訊

```
feat(lumos): doctor 加 Check V — valid_under 過期率軟提醒(段尾 T→R→S→H→K→V)

TDD:先寫失敗測試 2/3(67%)+全新 0% → 驗證 FAIL → 插 Check V → 驗證 GREEN
268 tests passed;真實 vault doctor rc=0(Check V 軟性不改 rc)
```

## 驗證方式

```bash
# 測試層(3 個 assert)
python3 scripts/test_lumos.py 2>&1 | grep "Check V"
# 預期：3 行 ✓ doctor Check V:...

# 全套件測試
python3 scripts/test_lumos.py
# 預期：N passed, 0 failed

# 煙測真實 vault
./scripts/lumos doctor 2>&1 | grep -A2 "\[V\]"
# 預期：[V] valid_under 過期率... + ok 行 / warn_soft 依實際

./scripts/lumos doctor >/dev/null 2>&1; echo "rc=$?"
# 預期：rc=0(Check V 是軟提醒，不改 rc)
```

## 相關系統

- [[2026-06-26_Task-1_check-v-進場提示日齡感知]]（_node_age_days 來源，共用 90 天 proxy）
- `[[Systems/lumos-doctor]]`（doctor 整體架構，檢查段落順序 T→R→S→H→K→V）
