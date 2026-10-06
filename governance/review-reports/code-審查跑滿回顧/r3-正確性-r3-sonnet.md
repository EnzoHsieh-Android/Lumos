severity: minor

席名:正確性-r3-sonnet。鏡頭:正確性/邏輯,另含資料狀態五問(新舊互讀、寫一半、衍生資料、時間、不可逆)。
查過沒壞的(不另列 finding):`_ledger_tail_needs_newline` 改走 `_regular_own_fd(require_owner=False)` 後,三個呼叫者(`_gate_event`、`_append_governance_log`、`_drift_ledger_append`)對一般檔行為不變;`_regular_own_fd` 預設仍要求自己的檔,其他呼叫者(`_local_ledger_append`、.gitignore 兩處)沒被改壞;`_esc_clean` 全域改動的其餘呼叫者都是顯示用,沒有拿結果比對或雜湊的;`_ledger_lines` 與 `read_text` 的通用換行不衝突;`--template --write` 的捷徑與 repo 外檢查、無法編碼字元(argv、帳上欄位 → context null、`--write` 不留殘檔)我實跑都對;`python3 scripts/test_lumos.py -k t_cap_retro` 17 支全綠。

### F1 卷證資料夾本身是捷徑時,下一步提示叫人跑的指令正是被拒絕的那一條 (修補引起)
severity: minor
blocking: 否 — 提示死路,但同一段輸出另附 `--skip` 出口,迴圈不會卡死。
- 輸入:有人裁紀錄的迴圈,`governance/review-reports/<編號>` 是指向 repo 內另一個資料夾的符號連結(帳上席報告仍在,所以仍「要回顧」)。
- 走到哪:處置閘第八步(同樣的還有 canary 擋下、loop next、doctor、retro-stats)呼叫 `_cap_retro_fix_cmd`;它只 `os.lstat` 回顧檔本身,經過資料夾捷徑 lstat 到的是不存在的檔,`st is None`,落到最後一句印 `--template --write`。
- 壞在哪:照貼 `--template --write`,第二輪新加的落點檢查直接回 2「卷證資料夾 … 是捷徑、或解析後不在 repo 根底下」。提示與拒絕互相矛盾,跟 `_cap_retro_fix_cmd` 文件自己宣稱的「兩條提示不會互相叫對方先做」不一致。
- 引句:「        return f"回顧檔位置 {q} 是資料夾、捷徑或其他特殊檔,移除該路徑後再 {_retro_cmd(loop_id, '--template --write')}"」(此分支只在回顧檔本身是特殊檔時才走到;資料夾是捷徑時走不到)
- 佐證行:file: `scripts/lumos:13355`(`_cap_retro_fix_cmd` 現檔,僅 lstat 回顧檔);file: `scripts/lumos:13644` 附近 `--template --write` 的 `inside` 檢查
- 重現(已跑):`_cr_repo`+`_cr_loop`+`_cr_decide` 造三輪迴圈與 extra-round 人裁,把 `governance/review-reports/crx` 搬到 `altdir` 後 `os.symlink(altdir, crx)`。`loop status crx --disposal` 印 `lumos loop retro crx --template --write`;照跑 `loop retro crx --template --write` → rc=2,stderr「擋下:卷證資料夾 governance/review-reports/crx 是捷徑、或解析後不在 repo 根底下——不在那裡建回顧檔」。

### F2 回顧檔存在但判不了(超過 256KB、或過期且檔已不在)時,提示是死路或指向不存在的檔 (修補引起)
severity: minor
blocking: 否 — 提示不準,`--skip` 與人工刪檔重建仍可走通。
- 輸入 A:回顧檔是一般檔、超過 256KB(`_retro_read_bytes` 回「超過 256KB」)。
- 走到哪 A:`--check` 的讀檔失敗分支呼叫 `_cap_retro_fix_cmd(root, loop_id, 'none')`,檔是一般檔 → 回「回顧檔已在、還沒記:--check 過了再 --record」。
- 壞在哪 A:正在跑的就是 `--check`,它剛說超過 256KB,提示又叫人跑 `--check`,沒人說要縮小檔案。實跑輸出:`✗ 回顧檔超過 256KB(至少 300000 位元組):… → 回顧檔已在、還沒記:lumos loop retro crx --check 過了再 lumos loop retro crx --record`。
- 輸入 B:`--record` 之後回顧檔被刪掉,狀態判「過期」(`cur is None`)。
- 壞在哪 B:`_cap_retro_fix_cmd` 的 stale 分支不看檔在不在,印「改好現有回顧檔 <路徑>(或刪掉後 … --template --write 重建)」。檔已不在,「改好現有」的對象不存在、「刪掉後」是多餘一步。實跑處置閘與 canary 擋下都印這句。
- 根因:`_cap_retro_fix_cmd` 只用 lstat 的類型分四句,沒用「為什麼判不了」(太大、不存在、過期)。
- 引句:「        return f"回顧檔已在、還沒記:{_retro_cmd(loop_id, '--check')} 過了再 {_retro_cmd(loop_id, '--record')}"」
- 佐證行:file: `scripts/lumos:13355`;file: `scripts/lumos:13130`(`_retro_read_bytes` 超過 256KB 回錯誤字串,與提示脫鉤)
- 重現(已跑):造同上迴圈、`--record` 合格後 `p.write_bytes(b"x"*300000)`,`loop retro crx --check` → rc=1 且輸出含上面那句;`os.unlink(p)` 後 `loop status crx --disposal` 的第八步印「改好現有回顧檔 governance/review-reports/crx/cap-retro.json(或刪掉後 … 重建)」。

### F3 `_append_governance_log` 遇到不能編碼的字串仍丟 UnicodeEncodeError,跟同族寫入器的修法不一致 (修補不完整)
severity: minor
blocking: 否 — 只有帶孤立代理字元的事件(例如 delguard/doctor 帶到非 UTF-8 檔名的節點)才觸發,現有流程未見傳入。
- 輸入:`_append_governance_log(vault, [事件])`,事件的 `nodes` 含 `"a\udcff"`(os.listdir 取到非 UTF-8 檔名時 surrogateescape 的結果)。
- 走到哪:追加治理帳的第三支寫入器,只接 `except OSError: pass`;r2 把 `_gate_event` 與 `_local_ledger_append` 改成接 `UnicodeEncodeError`,這支漏了。
- 壞在哪:`f.write(text)` 丟 `UnicodeEncodeError`(ValueError 子類,不是 OSError),直接冒成堆疊,doctor --ci、anchor approve、delguard 等呼叫者隨之中斷;專案筆記 loop-retro 寫「治理帳寫入器遇到編碼錯誤回『寫不進去』不丟堆疊」,只對 `_gate_event` 成立。
- 引句:「+    except (OSError, UnicodeEncodeError):   # 帶不能編碼的字串(孤立代理字元)也算寫不進去,不丟堆疊(r2 併發、邊界席)」
- 佐證行:file: `scripts/lumos:1601-1605`(`_append_governance_log` 的 `except OSError: pass`)
- 重現(已跑):臨時 git repo(docs/kg)內 `m._gate_event(root,"loop-retro","skipped","\ud800xx"*5)` → False(正確);`m._append_governance_log(vault,[{"gate":"delguard","kind":"x","hard":False,"nodes":["a\udcff"]}])` → `UnicodeEncodeError: 'utf-8' codec can't encode character '\udcff' in position 117`(scripts/lumos:1602)。

總結:最嚴重 minor,blocking 0 條
