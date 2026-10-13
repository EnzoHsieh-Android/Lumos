# r2 收貨紀錄(一般分級:單審+架構對齊,全新席,同門 sonnet;外家未派)

架構對齊席引句全數錨定,選為載體;單審席 #1 的引句 `這輪要 {width} 人審,最多跑 {cap} 輪` 在 `scripts/lumos` 的 `cmd_loop_next`,但不在這輪凍結 patch 的改動範圍內,所以錨不到——現象已機械重現(下表 V1)。

## 機械重現表

| finding | 重現命令/查證 | 結果 |
|---|---|---|
| V1 | 讀 `cmd_loop_next`:代問的閘依 `_panel_retired_for` 分流,新迴圈走處置閘(不收 min_seats)、舊 panel 迴圈走 panel 閘;夾具帳日期 2026-08-18 → 舊迴圈,改前印 1、閘要 3。改成舊 panel 迴圈維持 `_TIER_PARAMS`、新迴圈照名冊後,`t_loop_next_width_matches_roster` 釘舊迴圈 3/3、新迴圈 1/1 | HIT(修補造成的回歸:r1 修 U1 時只改顯示值) |
| V2 | 上游設成本機分支 `feature/base` 時 `@{upstream}` 切斜線得到不存在的遠端 `feature`;改讀 `branch.<名>.remote` 並確認在 `git remote` 清單內,`t_codeloop_default_base_prefers_newest_mainline` 補「上游是本機分支」「上游在 fork」「唯一遠端不叫 origin」三案 | HIT |
| V3 | 原測試從沒設上游;同上補三案 | HIT |
| W1 | `_push_mainlines`、`_mainline_ref` 說明沒提新入口;補一句 | HIT |
| W2 | 取上游遠端就地寫(⚠);V2 改法已改讀 git 設定,現在只有這一處需要「遠端名」,不抽共用 | HIT(折入:V2 已改讀 `branch.<名>.remote`,取上游遠端的寫法跟 repo 其他讀 git 設定處同形;只有一個呼叫點,不抽共用) |
| W3 | `_codeloop_guard_verdict` 表態範圍仍用 `_mainline_ref`(⚠);本次未改,在 `Systems/pitfalls-code-loop` 加 REVISIT:2026-11-13 量一次 | HIT(折入:在 `Systems/pitfalls-code-loop` 加 REVISIT:2026-11-13) |

## 處置

- 折入全部 6 條(本輪單審席報 major,代碼審同輪有 major 時不放行任何一條)。refuted:無。
- 回歸:V1 是上一輪修補 U1 造成的。
