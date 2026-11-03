severity: major

我讀的是 repo 現況(`/Users/enzo/harness/lumos-redbase-realrun`,修補已套上),再對照 r2-repair-review.patch。大部分搬動跟鄰居一致,但有一處自己切冒號,是「第二種做法」。

## 問 1 分層與依賴方向:大致對齊,有一處跨層以外的例外

- **對齊:`_gov_ledger_ignored` 的位置。** 它放在 `scripts/lumos:1775`,在 `_local_ledger_doctor_msgs`(`scripts/lumos:1752`)與 `_gov_routes_local` 之間。
  - 它呼叫的 `_lens_git_dl`(`scripts/lumos:64648`)是通用 git 包裝,不是比對工具的邏輯。
  - 鄰居 `_local_ledger_doctor_msgs` 同樣呼叫 lens 區的 `_lens_git`(`scripts/lumos:65105`),方向一致。
- **對齊:三個呼叫端。** 比對工具(`scripts/lumos:49815`)、規格閘(`scripts/lumos:14517`)、doctor(`scripts/lumos:2938`)都是「往帳檔區呼叫」。上一輪「doctor 去叫比對工具」的跨層直呼已消失。
- **對齊:舊名殘留。** `git grep` 查 `_tg_ledger_ignored` 與 `env_missing_re`,在 repo 內(排除卷證)零筆。
- **不對齊(分層以外):** 規格閘推送讀留痕的新分支(見下方第 1 條 finding)。

## 問 2 命名與錯誤處理:大致對齊,有兩處小差異

- **對齊:命名與例外接法。**
  - `_gov_ledger_ignored` 與同區 `_gov_ts`、`_gov_ledger_rows_by_time`、`_gov_routes_local` 同前綴。
  - doctor 新段改成 `except Exception` 加 `ok(f"…跳過(fail-open:{_e})")`(`scripts/lumos:2940` 一帶),與上方兩段(`scripts/lumos:2926`、`scripts/lumos:2937` 附近)逐字同形。
  - `except _TestRefPrefixError as e` 加 `e.prefix`(`scripts/lumos:16015`),與 `scripts/lumos:2441`、`scripts/lumos:69438` 同形。
- **對齊:輸出走哪條。** 規格閘那句提醒改走 `file=sys.stderr`(`scripts/lumos:14519`),與同函式 `scripts/lumos:14360`、`scripts/lumos:14382`、`scripts/lumos:14513` 一致。
- **不對齊(minor):** `.get("isig", …["sig"])` 的讀法,以及 `_ENV_MISSING_EVIDENCE` 的值形狀與讀法(見 finding 2、3)。

## 問 3 第二種做法:一處 major,兩處 minor

- **第 1 條 finding(major):手切冒號。** 新分支用 `t.split(":", 1)[1]` 自己切平台前綴。
  - `_split_test_ref_ex` 的 docstring 明寫「全庫切法只有這一支(呼叫端不再自己切冒號,代碼審 r2 架構席)」。
  - 計劃本身(patch 第 22 行)也寫「全庫唯一的切法 `_split_test_ref`」。
  - 新碼切出來的 `bare` 沒有走 `.strip()` 與 `_unwrap_backticks`,而 `_split_test_ref_ex` 兩者都做,兩種切法的結果已經不同。
  - 它也不限制前綴要「長得像平台名」(`_TEST_PLAT_LIKE_RE`),任何含冒號的名字都會被切一刀。目前靠後面的 `bare in methods_for(default)` 擋住,但切法本身是第二套。
- **第 2 條 finding(minor):`isig` 的讀法。** `_tg_fn_cands` 用 `.get("isig", …["sig"])` 做回退。
  - 所有函式字典都來自 `_tg_functions`(`scripts/lumos:49628`、`scripts/lumos:49629`、`scripts/lumos:50006`、`scripts/lumos:50060`、`scripts/lumos:50061`),字典一定有 `isig`。
  - 同一支函式裡 `prev["annot"]`、`f["annot"]` 都是直接取值。回退寫法在 `_tg_*` 這一帶是唯一一處。
  - `sig` / `isig` 的欄位命名本身,與 `annot` / `raw` / `mbody` 並列沒有不一致,不列。
- **第 3 條 finding(minor):`_ENV_MISSING_EVIDENCE` 的形狀與讀法。**
  - 同類表 `_RAN_EVIDENCE` 的值是具名欄位的字典(`re`、`measured`、`fix_hint`),旁邊的註解還強調「具名欄位,不用位置元組」。新表的值是光禿禿的樣式字串,說明文字另放在模組常數 `_ENV_MISSING_WHY`。
  - 讀法也不同:`_RAN_EVIDENCE` 的讀者是小函式(`_ran_count` 在 `scripts/lumos:68576`、`_ran_evidence_re` 在 `scripts/lumos:68597`、`_ran_evidence_check` 在 `scripts/lumos:68603`),`_ran_evidence_check` 會先 `_ANSI_RE.sub`。新表由 `_spec_gate_judge_items` 行內直接 `re.search`,沒有存取函式,也沒清色碼。
  - 表本身放在 `_RAN_EVIDENCE` 旁邊、以測試格式為鍵、不塞進 `_RAN_EVIDENCE`,這個結構選擇有理由(讀者都取 `re`),不列。
- **不計入的觀察(⚠ 交編排者):** doctor 新段自己算相對路徑 `(env.vault.parent / GOV_LOG_NAME).resolve().relative_to(…)`(`scripts/lumos:2937` 一帶),沒走同區的 `_docs_ledger_path`(`scripts/lumos:1652`)。這幾行是上一輪帶進來的,這輪只在同段改了函式名與 `except`。vault 在 `docs/<slug>-knowledge` 時 `vault.parent` 不一定是 repo 根,所以我判不準算不算第二種做法。
- **查過、不列的項目:**
  - `_rg_split_args` 的 `not angle` 條件(`scripts/lumos:48088`):行為有測試釘住,且不屬於上述兩類不一致。
  - 測試檔裡 `import random as _r` 與 `import json as _j` 寫在函式內:屬純風格。

不對齊共 3 條

第 1 條 finding:
severity: major
引句:「bare = t.split(":", 1)[1] if (not split and ":" in t) else None」
file: `scripts/lumos:16007`(對照 `scripts/lumos:6483`)

第 2 條 finding:
severity: minor
引句:「if prev is not None and prev.get("isig", prev["sig"]) == f.get("isig", f["sig"]) and prev["annot"] == f["annot"]:」
file: `scripts/lumos:49722`(對照同函式直接取值的 `prev["annot"]`)

第 3 條 finding:
severity: minor
引句:「_ENV_MISSING_EVIDENCE = {"kotlin-junit": _AGP_DEVICE_MISSING_RE, "java-junit": _AGP_DEVICE_MISSING_RE}」
file: `scripts/lumos:68527`(對照 `scripts/lumos:68530` 的 `_RAN_EVIDENCE` 與 `scripts/lumos:68603` 的 `_ran_evidence_check`,讀者在 `scripts/lumos:14967`)
