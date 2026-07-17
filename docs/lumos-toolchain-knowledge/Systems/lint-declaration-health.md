---
type: system
status: done
created: 2026-07-17
updated: 2026-07-17
tags:
  - type/system
  - status/done
related:
  - "[[Systems/pitfalls-lint-adapter]]"
  - "[[Systems/lint-version-watch]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Issues/lint-watch空轉假綠]]"
summary: |-
  KEY:lint-check 收「宣告了跑不動的東西」破口——同 lint-watch 空轉([[Issues/lint-watch空轉假綠]])同病根:宣告與現實脫鉤、無機制對帳。lumos lint-check <repo> 兩層:靜態格式校驗(恆跑)+ --smoke 真跑冒煙
  FLOW:讀 .lumos/lint.json → _lintcheck_validate 靜態校驗(非dict/value非list/命令空/缺{LINT_SARIF_OUT}佔位符)→ [--smoke:格式過才對每條命令 _lint_run_and_parse、無可解析SARIF產出=跑不動]→ rc 0健康(含無宣告)/1有問題/2非JSON
  KEY:兩層各抓一類——靜態層抓「格式錯」(便宜、純靜態);smoke層抓「格式對但跑不動」(工具/task/檔案缺;唯一能抓 gradle task 或外部 jar 存不存在的方法,靜態永遠抓不到)
  KEY:真實案例(2026-07-17 KDS)——Citrus_KDS 的 lint.json 格式完全正確(`{"kt":["java -jar /tmp/detekt-dist/...detekt-cli.jar --report sarif:{LINT_SARIF_OUT}..."]}`),但 detekt jar 放在 /tmp 被系統清掉→靜態層正確放行、--smoke 正確抓「跑不出 SARIF」rc1。靜態抓不到、smoke 抓得到,正是兩層必要性的鐵證
  KEY:誠實天花板——靜態層驗格式不驗命令跑不跑得動;smoke真跑=慢(每linter一次完整run)、且對「輸出SARIF到stdout而非佔位符檔」的宣告會報錯(那也是宣告錯,smoke正確抓出,非誤報);外部工具放 /tmp 這類易失位置=宣告脆弱,smoke 是唯一守衛
  KEY:設計哲學=宣告即契約需對帳——lint.json/lint-watch.json/test-layers.json 三個宣告檔都吃「宣告了不存在/跑不動的東西沒人知道」風險;lint-check 是 lint.json 這條的對帳器,同族收口
  DEP:scripts/lumos cmd_lint_check + _lintcheck_validate｜復用 _lint_run_and_parse(smoke)
  TEST:t_lintcheck_validate(格式校驗含 value 非 list 誤植案例)+t_lintcheck_cli(無檔rc0/空殼rc1/格式對rc0/smoke抓跑不動rc1/smoke真產SARIF rc0/非JSON rc2);全套 1236 passed
---
# lint-declaration-health——lint 宣告健康檢查(收「宣告了跑不動的東西」破口)

> **緣起**:2026-07-17 收窄 lint-watch 後盤點消費專案,使用者指出「宣告了跑不動的東西,也要是被檢測出來的一環」——這正是 lint-watch 空轉([[Issues/lint-watch空轉假綠]])的同病根:**宣告與現實脫鉤,沒有機制逼對帳**。

PRIOR-ART: ① 最小解層級——復用既有 `_lint_run_and_parse`(smoke)+ 新增純函數校驗,無新機制。② 世界解過——CI 界 config-lint/schema-validation(actionlint 驗 workflow、renovate-config-validator);本質是「宣告檔的宣告器」。③ 裁定=borrow-design。

## 兩層設計(各抓一類壞)
| 層 | 抓什麼 | 成本 |
|---|---|---|
| **靜態格式校驗**(恆跑) | 格式明顯錯:非 dict / value 非 list / 命令空 / 缺 `{LINT_SARIF_OUT}` 佔位符 | 便宜(純靜態) |
| **`--smoke` 冒煙**(可選) | 格式對但**跑不動**:task 不存在、plugin/jar/工具缺、SARIF 無產出 | 貴(每 linter 真跑一次) |

**為什麼要兩層**:靜態永遠抓不到「gradle task 存不存在」「外部 jar 還在不在」(那要真跑才知道);smoke 是唯一能抓的方法。但 smoke 慢,故分開——日常/巡檢跑靜態,定期/setup 後跑 smoke。

## 真實案例:KDS 的脆弱宣告(2026-07-17)
Citrus_KDS 的 `.lumos/lint.json` **格式完全正確**:
```json
{"kt": ["…/java -jar /tmp/detekt-dist/detekt-cli-1.23.7-all.jar --input …/MainActivity.kt --report sarif:{LINT_SARIF_OUT} --build-upon-default-config"]}
```
用獨立 detekt CLI jar(非 gradle plugin)跑。但 jar 放在 `/tmp/detekt-dist/…`——`/tmp` 被系統清掉後 jar 沒了。
- **靜態層**:格式合法(kt→list、有佔位符)→ 正確放行 ✓
- **`--smoke`**:真跑 → jar 不存在 → 跑不出 SARIF → 正確抓 rc1 ✓

兩層必要性的鐵證:靜態抓不到(宣告本身沒錯)、smoke 抓得到(現實跑不動)。教訓:**外部工具放 `/tmp` 這類易失位置=脆弱宣告**,靜態校驗無能為力,smoke 是唯一守衛;根治是把工具放持久位置或走 gradle plugin。

## rc 語意
`0`=健康(含無 lint.json=無宣告,不報) / `1`=有問題(格式或 smoke) / `2`=lint.json 非合法 JSON。

## 誠實天花板
- 靜態層只驗格式,不驗命令跑不跑得動——smoke 的責任田。
- smoke 對「輸出 SARIF 到 stdout 而非 `{LINT_SARIF_OUT}` 檔」的宣告會報錯——不是誤報:那確實是宣告錯(缺重導向),宣告端須把 SARIF 導向 `{LINT_SARIF_OUT}`。
- smoke 真跑消費專案自己宣告的 shell 命令(非外部輸入),風險等同該專案 CI 跑自己的 lint;且慢,不進 doctor --ci。

## 同族收口(宣告即契約需對帳)
lumos 三個宣告檔都吃「宣告了不存在/跑不動的東西沒人知道」風險:
- `.lumos/lint.json`(該跑什麼 linter)→ **本節點 lint-check 對帳**
- `.lumos/lint-watch.json`(該盯什麼 linter 新版)→ 心跳行 + 收窄([[Issues/lint-watch空轉假綠]])
- `.lumos/test-layers.json`(該跑什麼測試層)→ 恆 fail-open advisory(尚無對帳器,見待辦)

## 待辦
- [ ] 接巡檢:`lint-check` 靜態層併入 `doctor --ci`(消費專案 push 前掃自己 lint.json 格式);smoke 太慢不進 doctor,留 CI/setup 手動或 daily-governance
- [ ] test-layers.json 也給對帳器(同族第三個宣告檔,目前無檢查)
- [ ] KDS:detekt jar 從 /tmp 移到持久位置(或改 gradle plugin),再 `lint-check --smoke` 驗過——目前宣告格式對但跑不動(jar 被清)
