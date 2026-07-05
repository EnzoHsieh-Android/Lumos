---
type: issue
status: open
created: 2026-07-05
updated: 2026-07-05
tags:
  - type/issue
  - status/open
related:
  - "[[pitfalls網搜補漏_計劃]]"
summary: |-
  FLAG:TECHNICAL
  KEY:lumos-toolchain(python3 stdlib)的 linter 未收錄實務隱患台帳——lumos-pitfalls-gapfill skill 網搜補漏的落點;兩段〈已採納〉(放行的坑,可被 pitfalls 進場餵)〈已評估駁回〉(駁回的坑+反證,供 skill 去重跳過)
  KEY:〈已採納〉目前空(2026-07-05 首次 dogfood 唯一候選被反證預篩駁倒)
  DECISION:isinstance(True,int) bool 穿 int 守衛=真通則隱患但 lumos 已全修(唯二 config int 守衛皆加 not isinstance bool)→ 駁回(無未修實例),記此避免重找
---
# linter-gap 實務隱患(lumos-toolchain / python3 stdlib)

`lumos-pitfalls-gapfill` skill 的落點:linter(ruff/pylint 等)未收錄、經網搜+反證預篩+人放行的殘餘新坑。skill 進場先讀本節點兩段去重。

## 〈已採納〉(放行的坑 — 可被 pitfalls 進場當隱患鏡頭餵)
*(目前空 — 2026-07-05 首次 dogfood 的唯一候選被反證預篩駁倒,見下)*

| 坑 | 觸發條件 | 來源 |
|----|----------|------|
| — | — | — |

## 〈已評估駁回〉(駁回的坑 + 反證 — skill 去重跳過,別重找)

- **`isinstance(x, int)` 誤收 bool**(python `bool` 是 `int` 子類,`isinstance(True,int)==True`;config 讀 JSON 整數欄位用 `isinstance(v,int)` 守衛時 `{"depth":true}` 會穿透)。**真通則隱患、ruff/pylint 一般不 flag**,但**對 lumos 駁回=無未修實例**:反證者 grep 全 codebase,唯二讀 JSON config 整數守衛的地方(`_impact_load_config` `scripts/lumos:5573-5576`、`impact-hook.py:335`)**皆已加 `not isinstance(v,bool)`**,其餘 json.load 讀 str/dict/list 無整數守衛場景。來源:[Real Python isinstance](https://realpython.com/ref/builtin-functions/isinstance/)、[TIL bool subtype of int](https://www.linkedin.com/pulse/til-python-bool-subtype-int-wouter-donders)。(2026-07-05 dogfood)
