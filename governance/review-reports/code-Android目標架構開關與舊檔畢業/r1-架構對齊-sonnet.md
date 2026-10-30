severity: minor

**一、分層與依賴方向:對齊**

- 新碼全放在 `scripts/lumos` 裡目標架構那一帶,跟鄰居同一層。`_arch_legacy_apply` 夾在宣告切檔(`_arch_target_split`、`_arch_target_lens_split`)和輸出(`_arch_alignment_hints`、`_arch_target_text`)之間,三個呼叫點都是同一個接法:
  - 推送前分級:`_pitfall_diff_collect`。
  - 代碼審派工鏡頭:`_dispatch_lens_arch_text`。
  - 設計審派工鏡頭:`_dispatch_lens_spec_arch_text`。
- 讀設定走既有的 `_lumos_config_at_ref(..., strict=True, rel=...)`,沒有繞過去直接呼叫 git 讀檔。
  - 先例是 `_e2e_config_at` 用同一個函式讀 `.lumos/macrobench.json`。
  - file: `scripts/lumos:57345`、`scripts/lumos:40730`
- 讀版本的規則也跟鄰居一樣:ref 用 `_trusted_decl_ref` 算出來的可信版本,設計審讀 "HEAD"。沒有跨層直呼。
- 測試用既有夾具 `_arch_target_repo`、`_arch_pitfalls`、`_arch_lens`、`_arch_cfg`,檔名與 `t_arch_target_*` 一致。
  - file: `scripts/test_lumos.py:15411`

**二、命名與錯誤處理:大致對齊,一條 minor 不對齊**

對齊的部分:
- 讀不懂回 `(set(), "unreadable")`,不丟例外,跟 `_lumos_config_at_ref` 的四種狀態一致。
- doctor 那段包 try/except,出錯時印「…出錯(類名),這次略過」,跟目標架構宣告那段同一個寫法。
  - file: `scripts/lumos:2282`
- 提醒走 `warn_soft`,摘要走 `ok`。

不對齊的一條(合併三個小處):
- 前綴:鄰居的函式與常數全是 `_arch_target_*` 和 `_ARCH_TARGET_*`,新的是 `_arch_legacy_*` 和 `_ARCH_LEGACY_REL`。
- 回傳形狀:鄰居 `_arch_target_doctor_lines` 回 `(清單行 list, 提醒行 list)`,新的 `_arch_legacy_doctor_line` 回 `(str 或 None, str 或 None)`。
- 呼叫端因此不能照鄰居的 `if _atl` / `warn_soft(_atp, f"…{len(_atp)} 處…")` 寫,多了一個寫死「1 處」的 `warn_soft([_alp], "舊檔清單有 1 處要看(不擋):")`。
- 小重複:`_arch_legacy_doctor_line` 為了算「已不存在、沒被判給目標節點」,又寫了一次 `ls-files -z` 加 `_arch_target_rule_index` 的迴圈,又讀了一次 `_arch_targets_at(root, "HEAD")`。鄰居 `_arch_target_doctor_lines` 已經做過這兩件事,而且 run_doctor 在同一處先呼叫它。
- 對照:`scripts/lumos:57562`(鄰居)、`scripts/lumos:2282`(run_doctor 鄰居段)

severity: minor
blocking: 否
引句:「def _arch_legacy_doctor_line(env):」
引句:「r = _lens_git(root, "ls-files", "-z")」
引句:「warn_soft([_alp], "舊檔清單有 1 處要看(不擋):")」

**三、第二種做法:沒有 major,一條 minor 的雙軌**

沒有引入第二種讀設定檔的方式,也沒有另一套改動檔清單:
- 讀設定走同一支 `_lumos_config_at_ref`。
- 改動檔都走 `_arch_target_changed_files` 再 `_arch_target_split`。
- 宣告比對沿用 `_arch_targets_at` 回 `(rules, warns)` 的相等比較。

不對齊的一條:「哪些檔畢業」這件事有兩套各自推導的算法。
- `_arch_legacy_apply` 的條件是:head 版宣告和 ref 版相同、`not h_warns`、head 版清單狀態在 ok 或 missing。它回傳的 `grad` 就是畢業的檔。
- 三個呼叫端都把 `grad` 丟掉了(`_at_grad`、`_grad` 都沒人用)。
- `_arch_legacy_check_lines` 為了印「其中 N 支這次有改動、已照目標審」,另外用自己的條件重算一遍:`at_base == at_head and not at_base[1]`,再自己呼叫 `_arch_target_split(_arch_target_changed_files(...))`。
- 兩邊條件已經不完全相同。apply 檢查 head 版的警告,check 檢查 base 版的警告。之後只改一邊,「check 印出畢業幾支」就會跟「審查實際畢業幾支」對不上。
- 為什麼只標 minor:這是同一功能內部的雙軌,不是專案層級的第二種做法,結構上還是共用同一組底層函式。我判不準要不要升 major,⚠ 交編排者。
- 對照:`scripts/lumos:57439`(apply)、`scripts/lumos:57710`(check 鄰居函式)

severity: minor
blocking: 否
引句:「targets = _arch_target_split(_arch_target_changed_files(root, base, head), at_base[0])」
引句:「if gone and at_base == at_head and not at_base[1]:」
引句:「_at_targets, _at_grad = _arch_legacy_apply(repo_root, _at_ref, _at_head,」

不對齊共 2 條,其中 major 0 條

表態記錄裡我沒去反駁的是 `py-eventloop`、`py-parallel`、`py-memory`、`py-hotpath` 這幾題。diff 沒有 async,也沒有會成長的模組狀態,這部分跟我審的範圍無關。
