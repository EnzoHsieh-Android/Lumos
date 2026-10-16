severity: minor

第 2 輪沒有發現第二種做法或跨層直呼。只有 1 條 minor,而且我判不準,標 ⚠ 交編排者。

## 1. 分層與依賴方向
**對齊。**
- 新增的詞表常數(`_PITFALL_SEND_WHEN`、`_PITFALL_PAYMENT_WHEN`)放在 `PITFALL_CLASSES` 正上方,由 `scripts/lumos:29931` 的 `_PITFALL_COMPILED` 統一編譯。這跟 `scripts/lumos:30026` 的 `_EXTCODE_WHEN` 一樣是「字串常數,另處編譯」。
- 前端面是 `scripts/lumos:29967` 往 `_REQUIREMENT_FACETS` 追加列,`--stage` 沿用 `scripts/lumos:47771` 既有的 `any(re.search(w, text) ...)` 過濾。沒有另開一套解析器。
- `_req_frontend_hit` 是三個入口(`--stage`、計劃模式、`--check`)共用的唯一判準。
- 框架名單與 `scripts/lumos:30253` 的 `_NODE_FRONTEND_MARKERS` 對齊,並有 `t_req_fe_when_covers_node_frontend_markers` 守兩處同步。
- `infra` 棧別:
  - 它經由 `_stack_key_for_file`(`scripts/lumos:30318`)這個唯一的鍵入口產生,依 `_STACK_PERF_QUESTIONS` 與 `_STACK_TRIGGERS` 的既有派生流程消費。
  - `_ARCH_IDIOM_SKILL`(`scripts/lumos:46220`)沒有 infra,`_idiom_skill_for` 回 None,是既有的「沒有慣例 skill」路徑。
  - 掛法是 `_STACK_QUESTION_SPECS["infra"] = [...]`(`scripts/lumos:30219`),與 `scripts/lumos:30242` 的 extcode 迴圈同樣是字典建好後再改。
- `_arch_alignment_hints` 新增 `skip=frozenset()`,預設值與 `_stack_changed_ok(cur_file, skip=frozenset())`(`scripts/lumos:46742`)一致,呼叫端傳的也是同一個 `vend_skip`(`scripts/lumos:47318`、`:47349`)。
- `_TEST_INFRA_PATH_RE` 只加在 `scripts/lumos:47359` 那一處,沒有動 `_stack_changed_ok`。

## 2. 命名與錯誤處理
**對齊。**
- `_WHEN` 後綴照 `_EXTCODE_WHEN`,r1 架1 已修。
- `_pitfalls_check_print`、`_pitfalls_frontend_json`、`_pitfalls_frontend_print` 的前綴跟 `scripts/lumos:47754` 的 `_pitfalls_stage` 同族。
- 訊息形狀沿用既有的:
  - `提醒:…` 對應 `scripts/lumos:46214` 的「提醒:」。
  - `✓ pitfalls --check` 與 `✗ pitfalls --check` 兩句原文保留,只在後面追加提醒行。
  - 回傳碼沒變,`t_pitfalls_check_frontend_hint_keeps_rc` 與 `t_pitfalls_check_fail_branch_frontend_hint` 守住。
- 測試的 helper(`_fe_pf`、`_fe_plan`、`_infra_repo`)是每個功能自帶一組,跟 `_rc_run`、`_disp_run`、`_codex_run` 同一個慣例。

## 3. 第二種做法
我搜過 `_stack_changed_ok`、`_vendored_skip`、`_PITFALL_DIFF_TEST_PAT`、`_testmap_is_test`、`_nodehome_is_test`、`_TESTMAP_DIR_RE`。結論是沒有重做既有的函式,但有 1 條判不準的。

⚠ 以下這條判不準,交編排者:測試或 e2e 路徑的判斷,專案裡本來已有 `scripts/lumos:30698` 的 `_PITFALL_DIFF_TEST_PAT`、`scripts/lumos:48029` 的 `_testmap_is_test`、`scripts/lumos:32817` 的 `_nodehome_is_test`。`scripts/lumos:5810` 的角色表也把 `e2e` 當資料夾名。新增的 `_TEST_INFRA_PATH_RE` 是第四種路徑樣式。註解(`scripts/lumos:30700` 起)說明它與 `_PITFALL_DIFF_TEST_PAT` 分工:那支整支排除,這支改歸 infra。我認為語意不同,不是重做。不過 `e2e/` 的認法現在散在四處,沒有共用一個「這是 e2e 路徑」的判斷。這算不算第二種做法,我判不準。

severity: minor
blocking: 否
引句:「_TEST_INFRA_PATH_RE = re.compile(r"^(?!(?:[^/]+/)*?(?:src|lib)/)」
審材外佐證:``file: `scripts/lumos:48029` ``

不對齊共 1 條,其中 major 0 條
