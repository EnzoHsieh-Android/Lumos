---
type: verification
status: pass
date: 2026-07-05
plan_refs:
  - "[[design-loop折入守衛_計劃]]"
valid_under: "_fold_reverse_omission 介面不變;split_frontmatter/審計段切法不變;token pattern 定義不變"
revalidate_when: "token pattern 改 / 審計段排除邏輯改 / split_frontmatter 介面改"
tags:
  - type/verification
  - status/pass
related:
  - "[[design-loop折入守衛_計劃]]"
summary: |-
  TEST:t_fold_reverse_omission pass;full suite 508 passed 0 failed(無回歸)
  VERIFY:TDD flow:失敗測試→FAIL→實作→PASS;placeholder 排除/審計段排除/CamelCase/--flag/★MARKER★/點檔名 全驗
---
# 2026-07-05_fold-check-reverse-omission

Task 3 `_fold_reverse_omission(text) -> list[dict]` 實作驗證。

## 測試覆蓋
- `t_fold_reverse_omission`:body 有 `--bar` summary 無 → flag;`--foo` 兩邊都有 → 不 flag;`<path>` placeholder → 排除(r2-F5)。
- 額外直接驗證:CamelCase(`MultiEdit`)、`★MARKER★`、審計段排除、`\w+\.\w+` 檔名。

## 實作要點
- 審計段排除:複用 `_FOLD_AUDIT_RECORD_RE` / `_FOLD_NEXT_H2_RE`(與 T2 同一切段方法)。
- Summary 抽取:掃 frontmatter `summary: |-` 縮排區塊。
- Token patterns:`--flag`、`★\w+★`、`\w+\.\w+`、CamelCase、backtick 內容。
- Placeholder 排除:`<[^>]+>` 先替換再抽。
- 回傳:`[{token, present_in:"body", missing_in:"summary"}]` 已排序。

## 已知限制
- body↔body 跨段 omission 不偵測(主軸為 body vs summary);全文域 drift 靠 value-drift。
- `\w+\.\w+` 含數字點如版本號(`1.0`),可能假陽;保守設計。
</content>
</invoke>