severity: minor

我開了 `scripts/lumos` 和 `configs/ast-grep/kotlin-android/check.py` 對照。r1 的六條這版都改對了:覆核宣告改成獨立檔、擋停放在 `_codeloop_lint_new_step` 這一層、算命中收成一支共用函式、`--unsure` 做成同一組互斥模式、型錄載入沿用同一支、判定真相只留治理帳一處。這版沒有跨層直呼,也沒有第二份真相來源。下面 7 條都是 minor,沒有 major。

severity: minor
blocking: 否
- spec 段落:〈範圍〉做 3,「分支、版本、合併提交那一側照表態那一道 `_disp_bj_source` 的讀法」。
- 引句:「分支、版本、合併提交那一側照表態那一道 `_disp_bj_source` 的讀法」
- 既有做法:
  - `_disp_bj_source(rec, marker_branch, merge_ledger)` 要吃一筆表態紀錄 `rec`,靠 `rec["_merge_side"]` 判斷哪一側。file: `scripts/lumos:74237`
  - `_codeloop_lint_new_step(repo_root, diff_range, tier)` 沒有 `marker_branch`、`rec`、`merge_ledger`。file: `scripts/lumos:74556`
  - 兩處呼叫點(`scripts/lumos:74711`、`scripts/lumos:74777`)也沒傳這些。
- 差在介面:覆核這一層拿不到「合併提交哪一側」的資訊。
- 建議對齊:spec 明寫要擴 `_codeloop_lint_new_step` 的簽名,從 `_codeloop_guard_verdict` 傳進 `marker_branch` 和合併側資訊。S12 的測試要涵蓋這條新路徑。

severity: minor
blocking: 否
- spec 段落:〈範圍〉做 7,「寫一筆 `code-loop` 閘 fail-open 事件(scope `rule-review`)」,並說跟新增告警閘自動放行同樣被 `gov --stats` 數。
- 引句:「寫一筆 `code-loop` 閘 fail-open 事件(scope `rule-review`)」
- 既有做法:
  - `_gate_failopen(repo_root, gate, why)` 只有三個參數,沒有 scope。file: `scripts/lumos:72878`
  - 新增告警閘的自動放行事件記在閘名 `lint-new` 底下,不是 `code-loop`。file: `scripts/lumos:74556`
- 差在命名和資料形狀:spec 的事件閘名和多出來的 scope 欄位,跟它說要照做的那一筆對不上。
- 建議對齊:在「事件落在哪個閘名、怎麼區分覆核」二選一寫定。
  - 沿用 `_gate_failopen(repo_root, "lint-new", "覆核沒跑:<原因>")`,把原因放在文字裡。
  - 或另立閘名,並寫明 `gov --stats` 要改哪裡才數得到。

severity: minor
blocking: 否
- spec 段落:〈範圍〉做 7,「工具不可用、時間預算用完、參數太長、例外;任一種都…不擋」。
- 引句:「任一種都印一行「覆核沒跑:<原因>」並寫一筆 `code-loop` 閘 fail-open 事件」
- 既有做法:
  - 同一條管線(`_lint_new_run_cmds`)對「預算不夠」和「參數太長」記成 `undone`,判成擋,明寫不歸自動放行。file: `scripts/lumos:42656`、`scripts/lumos:42664`
  - 只有 `env` 類走自動放行。
- 這是政策分岔:同一種沒跑,覆核全部放行、一般段是擋。出處不全的 7 條原本就只提醒,放行有它的道理,但 spec 沒講為什麼覆核要放寬。
- 建議對齊:在〈範圍〉或〈天花板〉補一句「為何覆核的預算與參數太長不擋」。依據是覆核命中本來就要等盲判,沒跑時不能拿來當擋的理由。要不要順便對齊一般段,交編排者。

severity: minor
blocking: 否
- spec 段落:〈範圍〉做 2 的 `_rule_review_hits`,「內部照新增告警閘的做法抽兩份快照、跑命令、比對新增」。
- 引句:「內部照新增告警閘的做法抽兩份快照、跑命令、比對新增」
- 既有做法:
  - 這幾步已經拆成可重用的函式:`_lint_new_extract`、`_lint_new_support`、`_lint_new_run_cmds`、`_lint_new_diff_claims`。file: `scripts/lumos:42592`(`_lint_new_tools`)
  - 這條管線有 `waivers` 參數,放行過的命中在 `kept = [c for c in new if c.get("key") not in waivers]` 先濾掉。
- 兩個疑點:
  - spec 沒說 `_rule_review_hits` 是複用上面那些函式,還是另寫一份。另寫就是第二份快照加比對管線。
  - spec 沒說已放行(`lint-waive`)的命中要不要先濾掉。不濾的話,S3「判 real、`lint-waive` 之後放行」就得靠步驟層另外濾,`--template` 與 `rule_hits` 的 seg 驗證也會把已放行的命中算進去。
- 建議對齊:寫明複用 `_lint_new_extract`、`_lint_new_support`、`_lint_new_run_cmds`、`_lint_new_diff_claims`。同時規定 `_rule_review_hits` 吃 `waivers`,在函式裡濾掉已放行的,三處呼叫端因此算出同一組。

severity: minor
blocking: 否
- spec 段落:〈範圍〉做 1 的覆核宣告驗證,「讀法照 `_lint_deps_load` 那套」,以及〈用詞〉說格式跟 `.lumos/lint.json` 一樣是「副檔名 → 命令清單」。
- 引句:「驗證要求每條命令帶 `{LINT_FILES}` 或 `{LINT_FILES_CSV}`」
- 既有做法:
  - `_lint_deps_load` 的形狀是 `{"cmds": [...]}`,回 `([命令], 錯誤訊息)`,不是副檔名對應表。file: `scripts/lumos:41928`
  - 「副檔名 → 命令」的結構驗證已經在 `_lintcheck_validate`(非 dict、非 list、空清單、命令為空)。file: `scripts/lumos:39607`
  - 副檔名分流用 `_lint_stacks_for_diff` / `_lint_file_ext`。
  - 這條管線取結果靠 SARIF,現行驗證要求 `{LINT_SARIF_OUT}`。
- 差在:spec 的形狀是副檔名對應表,卻說照 `_lint_deps_load`(形狀不同),「另一份驗證」也重複了結構檢查。spec 只要求檔案佔位符,沒提 `{LINT_SARIF_OUT}`,但覆核命令若要走 `_lint_new_run_one`(吃 SARIF 取結果),缺了它輸出沒處去。
- 建議對齊:
  - 讀檔照 `_lint_deps_load` 的「另開檔、回 `(結果, 錯誤)`」風格即可。
  - 結構驗證抽共用,只換「必備佔位符」這一條規則,不另寫一整份。
  - 驗證補上 `{LINT_SARIF_OUT}`,或明寫覆核命令不走 SARIF 的取結果方式。

severity: minor
blocking: 否
- spec 段落:〈範圍〉做 4,「`_load_hook_file`,`required` 從 `("dt_table",)` 擴成 `("dt_table", "main_rows")`」。
- 既有做法:`_kt_pack_check` 載入點寫死 `("dt_table",)`,情境側的 `_KT_DT_ERR` 也走這支。file: `scripts/lumos:38350`
- 影響:`required` 一擴,情境題那條路也被連帶要求 `main_rows`。check.py 版本不一致時,情境題盲判會跟著被擋。這跟 spec 說的「`--rule-hits` 這條路不需要情境側算得出來」方向相反:現在是規則側的需求把情境側拖下水。
- 建議對齊:`main_rows` 缺失只讓規則命中那條路走「型錄讀不到」,不要動情境側的 `required`。或在 spec 寫明兩側同進退,並補一條情境側的測試。

severity: minor
blocking: 否
- spec 段落:〈範圍〉做 5 的帳欄 `token`、做 6 的 `--batch <token>`,以及做 6 `rule-review <指紋> agree|overturn`,說值的用詞照 `canary second`。
- 既有做法:
  - `token` 已在 `_GOV_FIELD_TYPES` 的字串欄,不是新欄。file: `scripts/lumos:17499`
  - `blind-judge` 在 `_gov_row` 本來就拿 `written_at`(微秒,每筆唯一)當鑑別子。file: `scripts/lumos:17585`
  - `canary second` 的介面是 `--id`、`--verdict agree|overturn`、`--auditor`(必填,且要和原判不同人),寫的是 `.canary-log.jsonl`。file: `scripts/lumos:19290`
- 兩個重疊:
  - 一次記帳的識別碼其實已經有 `written_at`,再加 `token` 是兩個身分。
  - 人複查的介面(位置參數 vs `--id`/`--verdict`)和 `canary second` 不一致。spec 只說「用詞照」,沒說介面照不照。
- 建議對齊:
  - `--batch` 的 token 直接用 `written_at`,或明寫為何另立。
  - `rule-review` 的旗標命名向 `canary second` 看齊,或寫明故意不同的理由。分權(`--auditor` 不同人)在單人使用下可省,但要寫明。

⚠ 交編排者:上面第 4 條(`_rule_review_hits` 是複用還是另寫一份管線、有沒有濾已放行)如果 spec 的意思是「另寫一份」,就是第二種做法,該升 major。我讀起來比較像複用,所以給 minor。

總結:r1 的 6 條都改對了;這版全部是小問題,沒有跨層、沒有雙重真相;剩 7 條小問題都是介面或命名要補寫或對齊
