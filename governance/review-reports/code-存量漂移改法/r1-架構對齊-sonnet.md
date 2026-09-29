severity: minor

# 架構對齊-sonnet 席(代碼審 r1,patch a = scripts/lumos)

## 問 1 分層與依賴方向:對齊
- drift fix 新碼放在 drift 區段 `cmd_drift_ack` 之後、`# ── 推送閘` 之前(patch a:1430 `cmd_drift_fix`),c1 呼叫 guard 區段的 `_guard_pass_rewrite`(patch a:1103-1112,docstring 明寫「往下呼叫」);guard 區段新函式(`_guard_pass_commit_date` 等,patch a:264-380)不回頭呼叫 drift、不碰 drift 內部狀態,沒有 guard→drift 反向依賴。
- `cmd_drift_fix --keep` 走既有 `cmd_drift_ack`(patch a:1440 附近),drift→drift 同層;`_issue_close_revisits` 放 issue 區段,由 drift fix 與 `lumos set` 兩處呼叫(patch a:1460、1766),與鄰居「共用函式放被共用最多的那一層」一致。
- 對照:base 的 `cmd_drift_ack` 在 scripts/lumos:27101,`_vault_write_lock` 在 scripts/lumos:14997(patch 與 base 行號不同,以函式名為準)。

## 問 2 命名與錯誤處理:對齊
- 命名 `_drift_fix_*` / `_drift_c4_*` / `_guard_*`,與鄰居 `_drift_ack_*`、`_guard_settle_*` 前綴風格一致。
- 錯誤處理一律 `print("擋下:…", file=sys.stderr)` + rc 2(patch a:1456 `cmd_drift_fix`),與 `cmd_drift_ack` 原有寫法相同;帳檔追加仍走 `_jsonl_append_verified`(scripts/lumos:8499),治理事件走 `_gate_event_or_warn`(與 base `cmd_drift_ack` 同款);鎖用 `_vault_write_lock`(scripts/lumos:14997);frontmatter 讀寫用 `load_raw_for_edit`(scripts/lumos:14876)+`atomic_write_verify`(scripts/lumos:14927)。
- git 呼叫走 `_lens_git`(patch a:1058)/`_nodehome_git`(patch a:266),與鄰居同一條包裝鏈(`_nodehome_git`→`_lens_git`,scripts/lumos:23351)。`_plan_first_commit` 加 `timeout` 參數沿用它原本的直呼 `subprocess.run`,是既有寫法的延伸,不是新包裝。

## 問 3 第二種做法:大致沒有,一處讀檔重複
- 鎖、原子寫入、frontmatter、git 包裝、JSONL 追加都重用既有函式。`_drift_ledger_append`(patch a:903-928)是包在 `_jsonl_append_verified` 外的一層,加了路徑符號連結檢查與補檔尾換行,寫入本體沒有另起一套;路徑檢查 docstring 自述照 `_mkdir_trusted_under_home`(scripts/lumos:33435)的逐層查法。這層檢查只有兩本 drift 帳用、其他帳沒有,⚠ 鄰居沒有對照可判(base 各帳都是裸 `_jsonl_append_verified`),不列 finding。
- 環境變數故障注入 `LUMOS_DRIFT_FIX_FAULT`(patch a:1403、1417)⚠:專案有 `LUMOS_DELGUARD_RAISE`(scripts/lumos:28391)這類測試接縫先例,但沒有統一寫法可對,不硬判。

## F1 帳檔讀取另寫一支,與既有表態檔讀取函式重複
severity: minor
blocking: 否
引句:「def _drift_jsonl_rows(fp):」
file: `scripts/lumos:27051`(base 的 `_drift_load_acks`:同樣 `fp.read_bytes() if fp.is_file() and not fp.is_symlink()`、`decode(errors="replace").splitlines()`、逐行 json.loads、只收 dict)
1. 新增 `_drift_jsonl_rows`(patch a:859-873)讀 `governance/drift-acks.jsonl` 與 `drift-fixes.jsonl`,`_drift_next_seq`(patch a:877)用它算序號;同一份表態檔在同一區段本來就有 `_drift_load_acks` 讀取,兩支讀檔骨架幾乎相同、過濾條件不同(後者要求 path 與 kind 合法)。
2. 兩支的例外集合已經分歧:新的接 `(ValueError, RecursionError)`,舊的只接 `ValueError`(`_jsonl_append_verified` 已補 RecursionError,scripts/lumos:8499 附近),同一份帳檔用兩種讀法容忍度不一樣。
3. 未附最小重現(這是結構重複,沒有壞掉的輸入可造),依規則列 minor;修法是讓 `_drift_load_acks` 底下改吃 `_drift_jsonl_rows` 再加自己的過濾。

不對齊共 1 條,其中 major 0 條
最高等級:minor
