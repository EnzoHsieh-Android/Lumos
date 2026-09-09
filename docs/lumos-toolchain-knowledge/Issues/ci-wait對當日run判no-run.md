---
type: issue
status: open
created: 2026-09-09
updated: 2026-09-09
aliases: []
about_code: []
tags:
  - type/issue
  - status/open
summary: |-
  FLAG:
  DECISION:
  KEY:
related:
  - "[[Systems/pitfalls-code-loop]]"
---
# ci-wait對當日run判no-run

> 白話：推完之後用工具問「CI 綠了沒」，它回「沒有 run」或「等到超時」；但同一時間直接問 GitHub，那幾個 commit 的 run 都已經跑完而且是綠的。工具看不到，人就得繞去用它叫我們別用的指令。

## 現象（2026-09-09 16:5x，本機實測）

- `lumos ci-wait --sha f233c79 --timeout 240 --json` → `{"verdict": "no-run", "runs": []}`；改帶全長 sha → `timeout`、`runs: []`；`--branch main` → 同樣 `timeout`。
- 同一分鐘 `gh run list --limit 6`（只讀查證，不進帳）：f233c79、d6f1ce0、c526824 三個 run 都 `completed success`，7b44871 `in_progress`。
- `lumos ci-status` 印的是 13:29 那次查到的舊結果（eb58cab），之後幾次推送都沒更新。

## 影響

- 推送後的 CI 結論進不了治理帳（code-loop skill 步驟 8 要求用 ci-wait，rc0≠綠那條也就無從判）；人只能繞去 gh，正是 CLAUDE.md 叫別用的路。

## 沒查的

- 是查詢條件（workflow 名、event 過濾、sha 比對長度）還是 API 分頁；沒開碼看。今天的 run 都是 push 事件、名稱是 commit 標題，跟 13:29 能查到的那次（eb58cab）有什麼不同也沒比。

## 回頭條件

REVISIT:2026-09-16 開 `cmd_ci_wait` 對 2026-09-09 16:55 前後那四個 run 重現一次，找出過濾條件哪裡對不上；修好後把當日四個 run 的結論補進治理帳。
