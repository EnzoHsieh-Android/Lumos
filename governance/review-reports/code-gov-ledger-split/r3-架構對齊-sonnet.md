severity: minor

## 問1 分層與依賴方向
結構上跟鄰居一致。新的帳路徑、判定、讀取函式都放在治理帳寫入器那一帶(`scripts/lumos:1333` 起,緊鄰 _gate_event_build 與 _gate_event),被 _gate_event、_append_governance_log、cmd_gov、度量段、doctor 呼叫,方向是由下往上,沒有跨層直呼。
把 docs 資料夾當 vault 傳給 _vault_write_lock(`scripts/lumos:21064`)合既有用法:這支鎖只拿參數算 realpath 雜湊當鎖鍵(`scripts/lumos:17790` 起 _vault_lock_where),鄰居也傳檔案路徑(`scripts/lumos:25500` 的 _lint_waivers_add 傳 `p`)。副作用是這把鎖跟筆記庫的 set/append 鎖不同鍵,不互斥,但兩邊寫的是不同檔,沒有衝突。
讀取判定類讀者只讀版控帳、統計類兩本合讀,這條分界在 `scripts/lumos:1361` 與 `scripts/lumos:8309` 兩處都落實,沒有判定類讀者誤走合讀。

## 問2 命名與錯誤處理
- 常數命名:GOV_LOCAL_LOG_NAME、USAGE_LOCAL_LOG_NAME 對得上 `scripts/lumos:38613` 的 CI_LOG_NAME。
- doctor 段的 `except Exception ... ok(f"本機帳觀測跳過(fail-open:{_e})")`(`scripts/lumos:2418`)與 `scripts/lumos:2409`、`scripts/lumos:2853` 同一句型,一致。
- 讀側「跟捷徑、但只讀一般檔案」:cmd_gov 的 load(`scripts/lumos:8260` 起)註解寫明跟捷徑,_gov_tail_bytes(`scripts/lumos:3813`)、_gov_ledger_rows_by_time 同判法,三處一致、有理由(帳在版控內的捷徑本來就有人用)。這跟 _doctor_cfg_bytes(`scripts/lumos:3828`)不跟捷徑是不同的對象(設定檔是信任輸入、帳是統計輸入),不算不一致。
- 寫側「本機帳不跟捷徑、版控帳照舊跟」:有註解理由(資安席),但同一個判法被抄在三處,見 F2。
- 壞行處理:合讀走既有 _drift_jsonl_iter(`scripts/lumos:33736`),沒自創切行。

## 問3 第二種做法
- 沒有自創鎖,用既有 _vault_write_lock 與 _excl_lock_try 那一套。
- 有三處輕微的「鄰居已有工具、新碼另走一條」:路徑組法(F1)、檔案寫入原語(F3)、git 呼叫(F4)。結構都對,沒到引入第二種機制的程度,故為輕微。

## F1 新增 _docs_ledger_path 與既有內聯組路徑並存,版控帳檔名沒有常數
severity: minor
blocking: 否
引句:「+    return Path(docs_dir) / name」
佐證:file: `scripts/lumos:1333`;同層既有做法 file: `scripts/lumos:38706`(_ci_log_path 加 CI_LOG_NAME 常數)、file: `scripts/lumos:3981`(同一支 _metric_rows 裡版控帳仍是 `env.vault.parent / ".governance-log.jsonl"` 內聯,下一行本機帳卻走 helper)、file: `scripts/lumos:8309`(cmd_gov 仍用 `docs / name`)
說明:同一個檔案裡現在有兩種組帳檔路徑的寫法,且 helper 只是 Path 相加,沒承擔任何額外規則;`".governance-log.jsonl"` 字串在新碼裡重複出現(`scripts/lumos:1361`、`scripts/lumos:1461`、`scripts/lumos:1537`),不像 CI 帳有 CI_LOG_NAME。結構對、只是慣例不齊。

## F2 本機帳不跟捷徑寫的判法抄三份,且與版控帳寫側不對稱
severity: minor
blocking: 否
引句:「+    if local and path.is_symlink():   # 本機帳不跟捷徑寫到別處(代碼審 r1 資安席:被提交進來的捷徑可指向 repo 外)」
佐證:file: `scripts/lumos:1462`(_gate_event)、file: `scripts/lumos:1538`(_append_governance_log,`batch is local and path.is_symlink()`)、file: `scripts/lumos:16316`(_usage_log);對照 _gov_routes_local 為避免兩支寫入器各抄一份而抽出,file: `scripts/lumos:1368` 附近
說明:同一個 patch 內為「路由判定」抽了共用函式,「本機帳不寫捷徑」卻散成三份各自內聯,後續改判法(例如改成 resolve 後比對)要改三處。版控帳那一側的寫入(`scripts/lumos:1465`、`scripts/lumos:1543`)仍跟捷徑寫,兩本帳在寫側的捷徑政策不同,理由只寫在註解、沒有統一入口。

## F3 _ensure_docs_gitignore 手刻獨佔建檔與追加,沒走 _write_lf
severity: minor
blocking: 否
引句:「+                fd = _os.open(str(gi), _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL, 0o666)」
佐證:file: `scripts/lumos:21072` 附近(新建分支);對照 file: `scripts/lumos:17736`(_write_lf,自述「vault 唯一寫入原語」)、file: `scripts/lumos:21010`(同檔 _scaffold_project 寫 .gitignore 用 _write_lf)、file: `scripts/lumos:30840`
說明:新建 .gitignore 的分支是 _write_lf 已有能力(UTF-8、LF、權限依 umask),另寫一份 O_EXCL;追加分支不走 _write_lf 有說明理由(替換會拆捷徑與硬連結),這一半成立。新建分支沒有同等理由,但在 _vault_write_lock 內,功能上沒差,只是第二種寫法。

## F4 doctor 本機帳提醒直接 subprocess 呼叫 git,沒用既有 git 包裝
severity: minor
blocking: 否
引句:「+            tracked = _sp.run(["git", "-C", str(docs_dir), "ls-files", "--error-unmatch", name],」
佐證:file: `scripts/lumos:1390`、file: `scripts/lumos:1392`;對照既有包裝 file: `scripts/lumos:1512`(_sp_run_text)、file: `scripts/lumos:13903`(_nodehome_git)、file: `scripts/lumos:38400`(_testmap_git)
說明:鄰居呼叫 git 多半經過包裝(統一逾時、錯誤吞法);這裡自己 import subprocess、自己寫逾時與例外清單。需要回傳碼而不是文字是理由之一,⚠ 判不準既有包裝是否能取得回傳碼,故只標輕微。

不對齊共 4 條,其中重大 0 條
