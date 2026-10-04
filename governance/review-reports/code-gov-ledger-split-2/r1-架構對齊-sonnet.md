severity: minor

## 問1 分層與依賴方向
大致對齊。新帳檔常數(GOV_LOG_NAME、GOV_LOCAL_LOG_NAME、USAGE_LOCAL_LOG_NAME)放在檔案前段 `scripts/lumos:1316`,鄰居 CI_LOG_NAME 在 `scripts/lumos:38645` 跟自己的 cmd 區塊放一起,位置不同但常數歸屬各自領域,不算跨層。讀者(`_gov_ledger_rows_by_time` 重用 `_drift_jsonl_iter` `scripts/lumos:33768`)、doctor 提醒走 `_lens_git` `scripts/lumos:40988`、`_ensure_docs_gitignore` 由 `_init_additive_setup` `scripts/lumos:21029` 呼叫,方向都同鄰居,沒有跨層直呼。僅 F1 的路徑組法與鄰居有小差異。

## 問2 命名與錯誤處理
大致對齊。`_usage_log` 維持「best-effort 靜默」`except Exception: pass`(`scripts/lumos:16322` 一帶),doctor 新段維持 `ok(f"…觀測跳過(fail-open:{_e})")`(`scripts/lumos:2424`,同 `scripts/lumos:2414`),`_ensure_docs_gitignore` 內 `import os as _os` 同 `_write_lf` 的區域別名寫法(`scripts/lumos:17756`)。訊息語氣(「⚠ …沒有自動補…」「✓ 本機帳的忽略設定…」)同 `_init_additive_setup` 的 `✓ 本機留痕的忽略設定`(`scripts/lumos:21052`)。只有 F2 的追加方式不一致。

## 問3 第二種做法
- 帳檔路徑:新增 `_docs_ledger_path(docs_dir, name)`,鄰居是 `_ci_log_path(env)`(F1)。
- 追加寫法:新帳寫入器用 `open(path,"a")`,同鄰居(`scripts/lumos:43466`)一致;`_ensure_docs_gitignore` 用 O_NOFOLLOW|O_APPEND,同 `scripts/lumos:18657` 的一種既有做法。同一個 diff 內兩種並存,見 F2。
- 沒自創輪子:時間解析抽成 `_gov_ts` 是把度量段與合讀兩份收成一份(淨減少一種做法);不走 `_write_lf` 的理由已寫在 docstring,且 `_write_lf` 為整檔替換原語,追加用 O_APPEND 屬另一語意,不算第二種做法。

## F1 帳檔路徑:新增 `_docs_ledger_path`,版控帳仍混用字面值
severity: minor
blocking: 否
引句:「+    load(".governance-log.jsonl", _gov_row)」
file: `scripts/lumos:8318`
鄰居 `.ci-log` 用 `CI_LOG_NAME` 加 `_ci_log_path(env)`(`scripts/lumos:38738`、`scripts/lumos:8352`),帳名常數與路徑函式成對。本 diff 新增 `GOV_LOG_NAME` 常數,卻在 cmd_gov 的 load 緊鄰一行用字面值 `".governance-log.jsonl"`、下一行用 `GOV_LOCAL_LOG_NAME`,同一函式內同一族帳兩種寫法;`_gov_ledger_rows_by_time`、度量段用常數,`scripts/lumos:2357`、`scripts/lumos:10334`、`scripts/lumos:11282` 等仍是字面值。路徑函式也另立 `_docs_ledger_path(docs_dir, name)`(引句同 diff 的 `def _docs_ledger_path(docs_dir, name):`,`scripts/lumos:1334`,簽名吃目錄不吃 env),跟 `_ci_log_path(env)` 並存兩套形狀。結構(常數加路徑函式)方向對,只是沒收齊。說明已寫「舊碼字面值照留」,所以只列 minor;但被本 diff 改到的那一行 `load(...)` 沒換成常數,是漏網處。

## F2 追加寫入:帳檔寫入器不帶 O_NOFOLLOW,同 diff 的忽略檔追加帶
severity: minor
blocking: 否
引句:「+        with open(path, "a", encoding="utf-8") as f:」
file: `scripts/lumos:43466`
同一個 diff 內有兩種追加做法:`_gate_event`、`_append_governance_log`、`_usage_log` 先 `_local_ledger_writable`(`is_symlink` 判斷)再 `open(path,"a")`,檢查與開檔之間可被換成捷徑;`_ensure_docs_gitignore` 用 `os.open(..., O_APPEND | O_NOFOLLOW)`(引句同 diff 的 `fd = _os.open(str(gi), _os.O_WRONLY | _os.O_APPEND | nofollow)`,`scripts/lumos:21090` 一帶)。專案內已有 O_NOFOLLOW 追加先例(`scripts/lumos:18657`、`scripts/lumos:35900`),也有 plain open 先例(`scripts/lumos:43466`),所以兩邊各自都有鄰居對得上,不是新手法;不一致只在本 diff 自己前後。⚠ 判不準是否值得統一:本機帳不進版控、威脅面比忽略檔小。

不對齊共 2 條,其中重大 0 條
