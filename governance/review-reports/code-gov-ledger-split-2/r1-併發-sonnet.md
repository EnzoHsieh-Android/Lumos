severity: minor

## F1 補忽略行:讀與追加之間檔被改,追加的字會黏在使用者最後一行上
severity: minor
blocking: 否
引句:「    chunk = (b"" if not raw or raw.endswith(b"\n") else nl) + b"".join(n.encode("utf-8") + nl for n in missing)」
file: `scripts/lumos:21057`(_ensure_docs_gitignore;chunk 依「讀到的舊內容」算要不要先補換行,追加卻開「現在的檔」)
注意:這條不是「重複行」那個已裁取捨,後果是改壞使用者既有的一行,且本機帳沒被忽略。
失敗場景:
1. 程序 A 進 `_ensure_docs_gitignore`,`gi.read_bytes()` 讀到 "a\n"(結尾有換行),算出 chunk 不帶前導換行。
2. 此刻使用者(或另一支工具)存檔,檔變成 "build/*.log"(結尾沒換行)。
3. A 用 O_APPEND 開檔追加 chunk,檔變成 `build/*.log.governance-local.jsonl` 加一行 `.usage-local.jsonl`。
4. 使用者原本的忽略規則被改成另一個樣式;`.governance-local.jsonl` 沒被忽略,每次例行寫入都弄髒工作目錄;函式還印「補上 2 行」,doctor 的 `git check-ignore` 才可能事後察覺。
重現:/tmp/gls2/w/t.py 在 read_bytes 後注入存檔,實跑輸出 `'build/*.log.governance-local.jsonl\n.usage-local.jsonl\n'`。窗口只在讀與開檔之間(微秒級),所以只給 minor。
修向:追加前用同一個 fd 讀(開 O_RDWR|O_APPEND、讀尾巴一個位元組判斷換行),或一律以 nl 開頭(多一個空行無害)。

## F2 本機帳檢查與開檔之間被換成管線,寫入端卡死(git hook 掛住)
severity: minor
blocking: 否
引句:「    return not p.is_symlink() and (not p.exists() or p.is_file())」
file: `scripts/lumos:1339`(_local_ledger_writable 只是先檢查;三個呼叫點 `scripts/lumos:1467`、`scripts/lumos:1544`、`scripts/lumos:16325` 之後都用 open(path,"a"),沒有 O_NOFOLLOW、沒有 O_NONBLOCK)
失敗場景:
1. `_usage_log`(show/context 每次都跑)呼叫 `_local_ledger_writable`,檔不存在,回 True。
2. 其他程序或使用者在此刻 `mkfifo docs/.usage-local.jsonl`(或換成捷徑)。
3. `open(p,"a")` 對沒有讀者的管線會永遠阻塞;`_gate_event`、`_append_governance_log` 同理,都在 pre-commit/pre-push hook 內,等於 hook 掛住。
重現:/tmp/gls2/w/t2.py 在檢查後 mkfifo,`_usage_log` 執行緒 5 秒後仍卡住(輸出 hung)。
備註:需要有人在極窄窗口內換檔,實務機率低;同一個缺口也在 `_ensure_docs_gitignore` 的 `is_file()` 與 `os.open(...O_WRONLY|O_APPEND|nofollow)` 之間(那裡有 O_NOFOLLOW 擋捷徑,但擋不了管線,且 `gi.read_bytes()` 也會讀管線卡住)。修向:寫入一律用 os.open 加 O_NOFOLLOW|O_NONBLOCK 再 fstat 確認是一般檔。

## F3 建新 .gitignore 時寫入失敗(磁碟滿、配額)讓 init/update 整個中止
severity: minor
blocking: 否
引句:「                f.write(("# 本機流水帳(不進版控;lumos init 補的)\n" + lines).encode("utf-8"))」
file: `scripts/lumos:21057`(該函式);呼叫端 `scripts/lumos:21053` 沒有包 try,後面的 `_init_config_skeleton(root)` 因此不會跑。
失敗場景:
1. docs/.gitignore 不存在,O_EXCL 建檔成功。
2. `f.write` 因 ENOSPC 或 EDQUOT 丟 OSError。這段在 try 之外(舊版整段包在 `except OSError`)。
3. 例外一路冒出 `_init_additive_setup`,init/update 帶堆疊失敗,留下空的 .gitignore;重跑時走「已存在、空檔」那條路會補上,所以能自癒,但那一次失敗是這版新增的行為退步,與函式文件寫的「best-effort、印出手動兩行」不一致。
未能重現(沒有構造磁碟滿的環境),自降為 minor。

## 圖譜鏡頭
派工尾端沒有附固定席筆記(未見 LUMOS-IMPACT 內容),無逐條可答。順帶:計劃筆記若仍寫「_ensure_docs_gitignore 讀與追加同一把鎖」應以現況(不拿鎖、O_NOFOLLOW)為準;本審未查圖譜節點。

## 已走過沒問題的範圍
- 讀者端:cmd_gov 之外的 `_gov_ledger_rows_by_time` 用 is_file 後 read_bytes,管線不讀;`_gov_tail_bytes` 改丟 OSError,三個呼叫點(doctor 成長段在 broad except 內、度量段先 is_file、`_gov_metric_events` 由 `_doctor_metric_lines` 先判 is_file)都不會因此崩。
- O_EXCL 建檔與另一程序同時追加:A 的 fd 不是 O_APPEND、從偏移 0 寫,會蓋掉 B 較短的內容,結果仍是完整的一份,不黏行、不丟使用者內容。
- 記憶體:`_gov_ledger_rows_by_time` 整份讀兩本且無上限,只有 doctor 提醒 5 MB;唯一呼叫點(`scripts/lumos:2999`)在完整 doctor 內,屬已知取捨,未給出具體失敗場景故不報。
- 兩個 hook 同時寫本機帳:`open("a")` 即 O_APPEND,單行(未超過 8 KB 緩衝)一次 write,不會交錯;超大單批在分流前就已存在於版控帳寫法,非本次新增。
- `_gate_event`/`_append_governance_log`/`_usage_log` 在 `_local_ledger_writable` 回 False 時安靜略過,無重試迴圈、無卡住路徑(除 F2 的換檔窗口)。

總結:併發與資源面三條都是極窄時序或環境失敗下的退步(黏行改壞使用者規則、被換成管線卡 hook、建檔寫失敗中止 init),沒有需要擋下合併的問題。
