severity: major

## F1 _ensure_docs_gitignore 新建分支的寫入沒包 try,寫失敗的 OSError 會逃出去,打斷 lumos update
severity: major
blocking: 是
引句:「                f.write(("# 本機流水帳(不進版控;lumos init 補的)\n" + lines).encode("utf-8"))」
file: `/home/user/Lumos/scripts/lumos:21053`(呼叫端 `_init_additive_setup`,上游 `/home/user/Lumos/scripts/lumos:20835`)
這段修補自己引入的洞:舊版整段包在 `except (OSError, UnicodeDecodeError, RuntimeError)` 裡;新版把 O_EXCL 開檔包了 try,但 `else:` 分支裡的 `fdopen` 加 `write` 沒包。追加分支(`_os.open(... O_APPEND ...)` 那段)有包,兩條路不對稱。
最小重現(已實跑,翻紅):
1. 建空資料夾 d,用 `signal.signal(SIGXFSZ, SIG_IGN)` 加 `resource.setrlimit(RLIMIT_FSIZE,(0,0))` 模擬寫入失敗(等同磁碟滿、配額滿、檔案大小上限)。
2. 載入 scripts/lumos,呼叫 `_ensure_docs_gitignore("d")`。
3. 實際輸出:`RAISED OSError [Errno 27] File too large`,而且 `d/.gitignore` 已被建成 0 位元組。
後果:
- `_ensure_docs_gitignore` 的約定是「回傳補上的行、失敗就回 []」,現在會丟例外。
- 呼叫鏈 `_init_additive_setup` 沒有 try;它在 `lumos update` 流程裡排在 `_scaffold_project` 之後、`_set_hooks_path` 與 `_init_config_skeleton` 之前,所以更新做到一半中止。
- 留下空的 .gitignore:下次跑走追加分支才補得回來。
修法方向:把新建分支的寫入一起放進 `except OSError` 回 `_manual(...)`。

## F2 暖機起點改取「第二早」後,帳裡只有一筆舊紀錄的專案永遠判不了「零筆撤除」
severity: minor
blocking: 否
引句:「    return evs, (two[1] if len(two) == 2 else None)」
file: `/home/user/Lumos/scripts/lumos:3994`(消費端 `first is None` 就 continue,在 `/home/user/Lumos/scripts/lumos:4006` 附近)
場景:
1. 版控帳(或本機帳)全帳只有一筆,時間是半年前,例如某專案只有一次 code-loop 通過紀錄。
2. 有效 RULE 寫 `[retire:度量 某閘.某種類 == 0 近4週]`,since 早於 4 週。
3. `_gov_metric_events` 回 `oldest=None`,`_doctor_metric_lines` 對這條一律不判。
4. 要等到帳出現第二筆才可能判;而「零筆」型條件正是在帳不再長的專案才該成立,所以永遠不會喊該撤。
佐證:修補自己得把舊測試改成「暖機要兩筆舊紀錄」才維持綠(delta 內 t_slots_doctor_reminders、t_slots_doctor_reminders_edges 的 old、bad 都多加一筆)。這是為擋單筆壞時間而付的代價,取捨可以接受,但沒寫進 doctor 的說明。若判不準是否算缺陷,⚠ 交作者裁。

## 已走過沒問題的範圍
- `_local_ledger_writable`:壞捷徑(`is_symlink` 先擋)、指向資料夾的捷徑、資料夾、管線(`exists` 為真但 `is_file` 為假)都回 False,三支寫入器不會卡在管線上開檔。本機帳所在的 docs/ 不存在或唯讀時,`open` 丟 OSError,各自吞掉。
- `_ensure_docs_gitignore`:
  - 空檔:`raw` 為空,不補換行,兩行照加。
  - 只有 BOM:不是 UTF-8-sig,BOM 自成一行,先補換行再加兩行,git 不受影響。
  - 混用換行:有任一 CRLF 就用 CRLF,不會壞。
  - 捷徑、壞捷徑、資料夾、管線、硬連結、唯讀(O_APPEND 開檔失敗)、UTF-16(PowerShell 重導向會產生)都走 `_manual`。
  - 沒有 O_NOFOLLOW(Windows)時 getattr 退成 0,不崩。
  - docs/ 不存在回 []。docs/ 唯讀且 .gitignore 不存在時,建檔的 OSError 被接住。
  - 兩個程序同時建檔時 FileExistsError 轉走已存在的路,只可能補出重複行,屬使用者已裁接受。
- `_local_ledger_doctor_msgs`:git 不在 PATH 時 `_lens_git` 回 None,不崩、不提醒。逾時也是同樣處理。`--` 分隔符讓怪檔名不被當旗標。
- `_gov_tail_bytes` 改丟 OSError:
  - doctor A2 在 broad except 內,會印「跳過」。
  - `_gov_metric_events` 的兩個呼叫端先判 `is_file()`,管線與資料夾不會走到它。
  - cmd_gov 與 `_gov_ledger_rows_by_time` 自帶 `is_file` 與 `except OSError`。
- `_gov_metric_events`:
  - 零筆、一筆回 None(見 F2)。
  - 兩筆同時刻時第二早等於第一早,不崩。
  - 極早(1970)與極晚(2099)的單筆壞時間不再讓護欄失效。
  - 全部時間經 `_gov_ts` 轉成帶時區,`nsmallest` 比較不會混用 naive 與 aware。
- `_gov_ledger_rows_by_time`:同時刻保持讀入順序,ts 解析不了排最前,壞行只跳那一行。

結論:新建 .gitignore 分支漏包例外讓寫入失敗時 update 中止(已實跑重現),另有一條暖機起點取第二早造成的單筆帳盲區,其餘極端輸入走查未發現問題。
