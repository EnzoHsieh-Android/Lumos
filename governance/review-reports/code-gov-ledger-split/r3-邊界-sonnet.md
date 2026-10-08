severity: major

## F1 本機帳是管線時,寫入器卡死(讀者補了、寫者沒補)
severity: major
blocking: 是
引句:「if local and path.is_symlink():   # 本機帳不跟捷徑寫到別處(代碼審 r1 資安席:被提交進來的捷徑可指向 repo 外)」
file: `scripts/lumos:1462`(_gate_event 寫入;只擋捷徑,管線照開)
file: `scripts/lumos:1539`(_append_governance_log,同樣只擋捷徑)
file: `scripts/lumos:16316`(_usage_log,r2 新加的守衛也只擋捷徑)
最小重現(已實跑,逾時 8 秒仍未返回,rc=124):
1. 建 docs/ 並 `mkfifo docs/.usage-local.jsonl`(或 `.governance-local.jsonl`,專案目錄先 git init)。
2. 載入 scripts/lumos 模組,對 `_usage_log`(env.vault.parent 指該 docs)呼叫一次;另一個實驗對 `_gate_event(root, "check-cascade", "warned", "x", hard=False)` 呼叫一次。
3. 兩個都停在 `open(path, "a")`:寫端開管線,沒有讀端就一直阻塞,不丟 OSError,所以外層的 `except OSError` / `except Exception` 接不到。
後果:r2 把「讀者」改成只讀一般檔案,理由是「管線讀不到底」;但同一個名字被做成管線時,寫者會永遠卡住。_usage_log 是 show/context 這種唯讀指令都會叫的,_gate_event 在 git hook 與 CI 裡跑,所以 hook 或唯讀查詢整個掛住。r2 的測試 t_gov_split_review_r2_fixes 只測了讀者碰到管線,沒測寫者。
修法方向:三處都改成「存在且不是一般檔案就不寫」(`p.exists() and not p.is_file()` 或 `os.open(..., O_NONBLOCK)` 後 fstat 判 S_ISREG),不只判 is_symlink。

## F2 度量暖機改取「第一筆」後,第一筆時間偏晚會讓護欄永久失效
severity: minor
blocking: 否
引句:「oldest = t if oldest is None else oldest」
file: `scripts/lumos:3953`
file: `scripts/lumos:3999`(`first > cutoff` 時整條 RULE 直接 continue)
失敗場景:
1. 本機帳(或版控帳)的第一行 ts 是一筆時鐘錯亂的未來時間(例如 2099 年,或剛 init 時系統時間比現在晚)。
2. `_gov_metric_events` 回 oldest = 2099;`first > cutoff` 恆真,這個閘+種類的所有度量式 [retire:度量] 永遠被略過、doctor 永遠不報「該撤」。
3. r2 的取捨只擋了「極早」一邊,對稱的「極晚」第一筆沒擋;因為只取第一筆,後面所有正常時間都救不了。要靠人去刪帳檔的第一行才解。
這是 r2 取捨的對稱缺口,影響範圍限 doctor 軟提醒,故 minor。

## F3 .gitignore 補行的鎖在「鎖資料夾建不起來」且 docs 不可寫時會卡 60 秒
severity: minor
blocking: 否
引句:「except (OSError, UnicodeDecodeError, RuntimeError):」
file: `scripts/lumos:17866`(`while not _excl_lock_try(...)`)與 `scripts/lumos:41929-41937`(`_excl_lock_try` 遇到 OSError 回 False)
失敗場景(⚠ 未能重現:本機用 root 跑,唯讀權限擋不住):
1. ~/.cache/lumos/vault-lock 不可信或建不起來,`_vault_lock_where` 退到 docs/.lumos-vault-<key>.lock。
2. docs/ 唯讀,`_excl_lock_try` 的 os.open 丟 PermissionError,被當成「沒搶到」回 False。
3. `_vault_write_lock` 每 0.05 秒重試到 60 秒才丟 RuntimeError,被 `_ensure_docs_gitignore` 吞掉回 []。lumos init 因而白等 60 秒,結果同樣是「不動」。唯讀 docs 本來就該立刻放棄。
註:新 .gitignore 的建立也被擠進同一把鎖,所以連「唯讀 docs 想建新檔」這條也要先過這 60 秒。

## 已走過沒問題的範圍
- .gitignore 空檔:raw 為空,chunk 不補前導換行,兩行直接寫入;只有 BOM:decode("utf-8") 得 U+FEFF 單行,補前導換行後追加,無例外。BOM 加整行相同的第一行會多補一份重複行,git 忽略規則重複無害。
- 混用換行:有任何 CRLF 就整段用 CRLF 追加,內容位元組不改,可接受。
- 唯讀 .gitignore:open("ab") 丟 PermissionError 被接住,沒有半寫(整段一次 write)。
- .gitignore 是壞捷徑(exists False、is_symlink True)、捷徑指向資料夾、資料夾、管線、硬連結(st_nlink>1):全部回 [] 不動;新建用 O_EXCL,競態輸家得 FileExistsError(OSError)被接住。
- docs/ 本身是捷徑到資料夾:is_dir 為真,照常追加到目標;docs 不存在:回 [] 不建。
- 讀者側:帳是壞捷徑、資料夾、管線、特殊裝置檔,`_gov_ledger_rows_by_time`、`cmd_gov.load`、`_gov_tail_bytes` 的 is_file 守衛都返回空;_local_ledger_doctor_msgs 同樣先 is_file;git 不在 PATH 時 subprocess 的 OSError 被接住,_append_governance_log 的外層 try 也接。
- 帳檔第一行壞行、無 ts、非字串 ts:_drift_jsonl_iter 只跳壞行,_gov_ts 回 None,排序排最前;ts 極早(0001 年帶 +05:00)的 timestamp() 在 aware 時間不溢位,naive 版本的 astimezone 溢位被 _gov_ts 內部擋掉。本機帳只有一筆:合讀與度量照常。
- 檔尾讀法被換成整份讀:超大本機帳會一次進記憶體,r2 已明講並在 doctor 5 MB 提醒,不另列。

總結:讀者端的特殊檔案守衛補齊了,但寫入端對管線仍會永久卡住,是這輪唯一需要擋下的洞。
