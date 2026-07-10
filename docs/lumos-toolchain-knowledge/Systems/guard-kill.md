---
type: system
status: done
created: 2026-07-10
updated: 2026-07-10
tags:
  - type/system
  - status/done
summary: |-
  FLOW:kill-add(配方進kill_recipes+KEY行[kill:recipes],同檔原子寫)→kill(依platform分組→worktree於系統temp→baseline綠→套壞法(圍欄+唯一命中)→綁定測試必翻紅→六態verdict→docs/.kill-log.jsonl留痕)
  KEY:宣告式壞法(人寫,從業務行為推導非實作反轉;繞開等價變異不可判定)｜run_cmd由config宣告(platforms.X.run_cmd/legacy test.run_cmd,{method}佔位+shlex.quote+killpg)｜六態:killed/timed_out(歸killed,PIT語意)/survived(稻草人rc1)/drifted/abort/error
  KEY:baseline前置(cargo-mutants)防假殺;timeout=baseline×5下限20s(LUMOS_KILL_TIMEOUT_FLOOR可覆寫);worktree只隔離原始碼不隔離DB(hermetic警語);HEAD基準(dirty大聲警告)
  KEY:★DEBT★ hydration(未提交帶入)與lockfile v1砍(否決位裁);E2E maestro {method}不適用;冷build成本;submodule不init
  DEP:[[Systems/check-t-sentinel]][[Systems/test-profile-multiplatform]]
  TEST:21/21(t_guard_kill 六態全走)+全套923綠 | VERIFY:[[Verification/2026-07-10_guard殺傷力驗證]]
related:
  - "[[Projects/guard殺傷力驗證_計劃]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/test-profile-multiplatform]]"
verified_by:
  - "[[Verification/2026-07-10_guard殺傷力驗證]]"
---
# guard-kill（殺傷力驗證）

## 概述

合約鏈最後一哩：`★INVARIANT★→[test:]` 只證「保鑣存在」，`guard kill` 真的打一拳——隔離 worktree 裡故意弄壞被守護的行為，綁定測試必須翻紅；全綠＝稻草人證據（rc 1）。設計三輪 panel 收斂見 [[Projects/guard殺傷力驗證_計劃]]，golden 凍結 `governance/golden/guard-kill/`。

## CLI

- `lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y [--test 名] [--platform P] [--note]`
- `lumos guard kill <node> ["<KEY子字串>"] [--platform P] [--json] [--keep-worktree]`
- rc：全 killed（含 timed_out）=0；任一 survived=1；drifted/abort/error 存在無 survived=2。
- `lumos gov` 第 5 支 load 撈 kill 留痕；guard list 顯示 `[kill✓]`。

## 實作位置

`scripts/lumos`：`_kill_read_recipes`/`cmd_guard_kill_add`/`_kill_run`/`cmd_guard_kill` + INV_TAG_RE 擴 kill + KILL_REF_RE + gov/gitignore/cochange 三處同步。測試 `t_guard_kill`。

## 相關模組

- [[Projects/guard殺傷力驗證_計劃]]
- [[Systems/check-t-sentinel]]
- [[Systems/test-profile-multiplatform]]
