---
type: verification
status: pass
feature: "Task 2: canary record --findings + loop status --gate 三檢(K-streak∧G1 refcheck∧G2 發現枯竭)"
commit: 4ce445bbbc70be1be60fe5122cf53674f4452992
date: 2026-07-03
valid_under:
  - "Python 3.7+"
  - "_refcheck_scan(text, repo_root) 已完成(Task 1)"
  - "_anchor_repo_root(repo) 既有"
revalidate_when:
  - "cmd_canary 或 cmd_loop_status 簽名改動"
  - "refcheck 核對邏輯變更"
  - "發現枯竭(G2)演算法需調整"
plan_refs:
  - "[[多平台合約測試綁定_計劃]]"
---

# Verification: Task 2 canary record --findings + loop status --gate

## 變更範圍

### cmd_canary (findings 參數)
- 簽名新增 `findings=None` 參數
- rec 紀錄時: `if findings is not None: rec["findings"] = findings`
- argparse: `cr.add_argument("--findings", type=int, ...)`
- dispatch: 傳遞 `findings=args.findings`

### cmd_loop_status (gate 三檢)
- 簽名新增 `gate=False, spec=None, repo=None`
- argparse: 新增 `--gate`, `--spec`, `--repo`
- dispatch: 傳遞三個參數
- 核心邏輯:
  1. **K-streak**: 連 K 輪 caught+乾淨(既有)
  2. **G1 refcheck**: 呼叫 `_refcheck_scan(text, repo_root)` 核對引用座標
  3. **G2 發現枯竭**: findings 單調遞減、末輪≤1 且(=0 或<前輪)

## 測試項目

### t_canary_findings (3 checks)
| 場景 | 預期 | 結果 |
|------|------|------|
| --findings 3 | 寫入 rec | ✅ |
| 不給 findings | 無該鍵 | ✅ |
| 非整數值 | rc!=0 | ✅ |

### t_loop_gate (16 checks)
| 案例 | 描述 | 預期 | 結果 |
|------|------|------|------|
| g3 | [2,0] 全過 | rc=0 PASS | ✅ |
| g4 | [2,1] 殘餘正向 | rc=0 PASS | ✅ |
| g5 | [2,3] 非枯竭 | rc=1 G2 | ✅ |
| g6 | 末輪 2>1 | rc=1 G2 | ✅ |
| g7 | [1,1] 恆定涓流 | rc=1 G2 | ✅ |
| g8 | K=3 [2,1,1] | rc=1 G2 | ✅ |
| g9a | K=1 [1] | rc=1 | ✅ |
| g9b | K=1 [0] | rc=0 無 IndexError | ✅ |
| g10a | clean 卻 findings=1 | rc=1 互證 | ✅ |
| g10b | minor 卻 findings=0 | rc=1 互證 | ✅ |
| g11 | 壞引用 | rc=1 G1 含 ghost 檔 | ✅ |
| g12 | 缺 severity 輪 | rc=1 K-streak | ✅ |
| g2f | 缺 findings 欄位 | rc=1 fail-closed + --findings 提示 | ✅ |
| 案13a | 不帶 --gate CONVERGED | rc=0(舊判準) | ✅ |
| 案13b | g5 無 gate 仍 CONVERGED | rc=0 | ✅ |
| 案14 | --gate 缺 --spec | rc=2 | ✅ |

### 回歸測試
| 項目 | 預期 | 結果 |
|------|------|------|
| 總測試數 | 352 (333+19) | ✅ 352 passed, 0 failed |
| t_canary_findings | 3 checks | ✅ 全綠 |
| t_loop_gate | 16 checks | ✅ 全綠 |
| 非 gate 路徑輸出 | 原樣無異動 | ✅ 確認 |
| per-round 行無 findings | 無 gate 時不加欄 | ✅ 確認 |

## 測試方式

```bash
# 確認 test count 與新 checks
python3 scripts/test_lumos.py 2>&1 | tail -1
# 預期: 352 passed, 0 failed

# 確認新測試全綠
python3 scripts/test_lumos.py 2>&1 | grep -E "t_canary_findings|t_loop_gate" | grep "✓"
# 預期: 19 條 check 全 ✓

# 驗證非 gate 舊路徑一致性
python3 scripts/test_lumos.py 2>&1 | grep "案13"
# 預期: 案13a/b 都 ✓(舊判準不看 findings)
```

## 相關模組
- [[Systems/loop-convergence-recording]] - 核心設計
- [[Systems/judge-severity-gate]] - G1/G2 判決邏輯

## 核心實現細節

### Gate 三檢流程
```python
# K-streak(必要條件)
if converged:  # 既有邏輯
    print(f"[gate] K-streak: ✓")
else:
    fails.append("K-streak")

# G1: refcheck 引用座標
claims, n_missing, n_oor, _n_ok = _refcheck_scan(text, repo_root)
bad = [c for c in claims if c["status"] in ("missing", "line_out_of_range")]
if bad:
    fails.append("G1")
    # 列 ghost 檔

# G2: 發現枯竭
fs = [r.get("findings") for r in tail]  # tail = rounds[-need:]
# ① 完備性: len(tail) >= need && all fs not None
# ② 互證: (clean→findings==0) ∧ (minor→findings≥1)
# ③ 單調+末端: mono ∧ fs[-1]<=1 ∧ (fs[-1]==0 ∨ fs[-1]<fs[-2])
```

### 向後相容保證
1. 無 `--findings` → 無 findings 鍵(done ✅)
2. 無 `--gate` → 輸出與 rc 分毫不變(done ✅)
3. 非 gate 路徑的 per-round 輸出無 findings 欄(done ✅)

## 簽名變更

**cmd_canary**
```python
# before
def cmd_canary(env, kind, auditor=None, token=None, note=None, loop=None, severity=None):

# after
def cmd_canary(env, kind, auditor=None, token=None, note=None, loop=None, severity=None, findings=None):
```

**cmd_loop_status**
```python
# before
def cmd_loop_status(env, loop_id, need=2):

# after
def cmd_loop_status(env, loop_id, need=2, gate=False, spec=None, repo=None):
```

## 已知限制 & 天花板

1. **findings 數字正確性**: findings 源自 LLM 裁決,gate 機械化的是算術不是數字本身的正確性
2. **G1 refcheck 局限**: 只核對存在性/行號,不檢查內容語義
3. **G2 枯竭判定**: 基於 findings 單調性,若 LLM 判決不合理該機制仍會放過
4. **fail-closed**: 缺 findings 欄位直接 rc=1(寧嚴毋寬)

## 提案/決策

無重大提案,係 Task 2 brief 逐字實作(見 brief Step 1-6 100% compliance)

