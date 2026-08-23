---
type: system
status: done
created: 2026-07-10
updated: 2026-07-24
self_audit: sonnet/2026-07-24
about_code_stamp: batch-2026-08-23/2026-08-23/2faf3eec082c
tags:
  - type/system
  - status/done
  - risk/守衛面
summary: |-
  KEY:★INVARIANT★ guard kill rc 優先序:survived→rc1、drifted/abort/error→rc2、弱證據(unattributed/timeout)不放行執行錯誤 [test:t_guard_kill_rc_precedence] [audit:sonnet/2026-07-29]
  KEY:★INVARIANT★ guard kill --json 模式**成功跑完時(rc 0/1)** stdout 恰一行合法 JSON(所有診斷走 stderr;rc2 早退路徑不印 JSON=範圍外,明文收窄) [test:t_guard_kill_json_purity] [audit:sonnet/2026-07-29]
  FLOW:kill-add(配方進kill_recipes+KEY行[kill:recipes],同檔原子寫)→kill(依platform分組→worktree於系統temp→baseline綠→套壞法(圍欄+唯一命中)→綁定測試必翻紅→七態verdict→docs/.kill-log.jsonl留痕)
  KEY:宣告式壞法(人寫,從業務行為推導非實作反轉;繞開等價變異不可判定)｜run_cmd由config宣告(platforms.X.run_cmd/legacy test.run_cmd,{method}佔位+shlex.quote+killpg)｜**七態**(2026-07-29 oracle品質包升級,取代舊六態):killed(強證據,歸因到綁定測試)/killed_unattributed(紅了但歸不到該測試)/timed_out_weak(**不再計為 killed**,舊版歸 killed 是假強殺)/survived(稻草人rc1)/drifted/abort/error
  KEY:baseline前置(cargo-mutants)防假殺;timeout=baseline×5下限20s(LUMOS_KILL_TIMEOUT_FLOOR可覆寫);worktree只隔離原始碼不隔離DB(hermetic警語);HEAD基準(dirty大聲警告)
  KEY:★DEBT★ hydration(未提交帶入)與lockfile v1砍(否決位裁);E2E maestro {method}不適用;冷build成本;submodule不init
  KEY:★誠實界線[2026-07-23 日報吸收]★——殺傷率有天花板:「殺得掉」≠「殺得準」。研究(arXiv 2606.10417)實測突變殺傷率 7-9 成的測試仍漏一大片未真正驗到的行為,且很多「殺掉」是程式碰巧崩(rc≠0)、非斷言真的檢查了被改壞的行為。**對 lumos 兩重意義**:①guard-kill 的 survived(rc1)只證「綁定測試對這個壞法翻紅」,不證斷言指到被改的業務欄位——高風險合約可加一句「準殺」檢查(失敗測試斷言須提及被弄壞的欄位/行為,非只看 rc)②**打臉 2026-07-22 日報 inspiration「把 Check K 健康指標從『數測試』換成『殺傷率』」**(該 inspiration 未落地)——別把可鑽的『數量』換成另一個可鑽的『殺傷率』;真要換,健康指標得是『準殺』(斷言驗到規則),不是裸殺傷率。載重合約留「這條到底驗了哪些行為」比留一個殺傷率數字誠實
  DEP:[[Systems/check-t-sentinel]][[Systems/test-profile-multiplatform]]
  TEST:t_guard_kill(七態+M1/M2殺手測試)+t_guard_kill_attribution+t_guard_kill_rc_precedence+t_guard_kill_json_purity+全套923綠 | VERIFY:[[Verification/2026-07-10_guard殺傷力驗證]]
related:
  - "[[Projects/guard殺傷力驗證_計劃]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Verification/2026-07-10_guard殺傷力驗證]]"
aliases:
  - 殺傷力驗證
decisions:
  - content: 拿掉 2026-07-10 那份已 stale 的驗證背書(態數升級後前提不成立,E1 連喊 24 天 207 次沒人理——機制空轉週報首批)。目前 guard kill 沒有有效驗證紀錄;重驗要在有 kill 配方的消費端專案跑一輪,排進下一批。
    id: d1
    decided: 2026-08-22
    valid: true
  - content: 歸因需要測試輸出把「失敗標記」和「測試名」放同一行或 5 行內:test_lumos.py 的 runner 在每支失敗測試後印「✗ FAILED <名>(N 條斷言)」。2026-08-22 第一次真跑 kill(canary-audit 落盤自驗配方)判 killed_unattributed 就是因為這個。
    id: d2
    decided: 2026-08-22
    valid: true
verified_by:
  - "[[Verification/2026-08-22_guard-kill首次真跑]]"
about_code:
  - scripts/lumos
---
# guard-kill（殺傷力驗證）

## 概述

合約鏈最後一哩：`★INVARIANT★→[test:]` 只證「保鑣存在」，`guard kill` 真的打一拳——隔離 worktree 裡故意弄壞被守護的行為，綁定測試必須翻紅；全綠＝稻草人證據（rc 1）。設計三輪 panel 收斂見 [[Projects/guard殺傷力驗證_計劃]]，golden 凍結 `governance/golden/guard-kill/`。

## CLI

- `lumos guard kill-add <node> "<KEY子字串>" --file F --old X --new Y [--test 名] [--platform P] [--note]`
- `lumos guard kill <node> ["<KEY子字串>"] [--platform P] [--json] [--keep-worktree]`
- rc（2026-07-29 七態後的優先序，`[test:t_guard_kill_rc_precedence]`）：任一 survived=1；drifted/abort/error 存在且無 survived=2；**全部只有弱證據（`killed_unattributed`／`timed_out_weak`）=1**（不放行——弱證據不算接住）；有強證據 killed 且無錯誤=0。舊版「全 killed（含 timed_out）=0」已作廢：把逾時當殺掉是假強殺。
- `lumos gov` 第 5 支 load 撈 kill 留痕；guard list 顯示 `[kill✓]`。

## 實作位置

`scripts/lumos`：`_kill_read_recipes`/`cmd_guard_kill_add`/`_kill_run`/`cmd_guard_kill` + INV_TAG_RE 擴 kill + KILL_REF_RE + gov/gitignore/cochange 三處同步。測試 `t_guard_kill`。

## 相關模組

- [[Projects/guard殺傷力驗證_計劃]]
- [[Systems/check-t-sentinel]]
- [[Systems/test-profile-multiplatform]]
