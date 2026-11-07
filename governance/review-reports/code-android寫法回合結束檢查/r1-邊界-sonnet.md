severity: major

我把 patch 讀完,另外 `git clone --shared` 到 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/邊界-sonnet/repo`,用假的 `lumos`(放在 `fk/`)和隔離的 HOME 實跑 `stop-lint-hook.py`。`impact-hook.py` 的改動(決策列挑選與標記)沒有實跑,只讀了 patch 與 `scripts/lumos` 裡對應的產生端。

**實跑結果,沒有問題的部分**
- 正常擋下:送出提示寫起點,收工擋下一次並寫出標記檔;同一批第二次不再擋。
- 批次上限:`b2`、`b3` 各再擋一次,`b4` 被三批上限擋住不再輸出。
- 非 UTF-8 的 stdin 回 rc0。
- `session_id` 是整數、`prompt_id` 是 dict 時不崩。
- 逾時:預算 30、4、1 秒時,耗時約 21、2.9、1.1 秒。
- 殺子程序:lint-new 忽略 SIGTERM 並另開工具群組時,逾時路徑與鉤子被 SIGTERM 兩條路,之後都沒有殘留的 `sleep` 或 `lumos` 程序。
- 搬家:`-k trusted_lumos`、`budget`、`stop_lint`、`hook_copy`、`handoff_hook_import`、`stop_block` 這幾組測試全綠;`_hookshared.py` 的原始碼與 `check-graph-sync.py` 刪掉的原文逐字相同。

F1 擋下訊息把放行指令截斷、也把告警清單截掉,放行指令不能直接貼
- 輸入:3 個以上的新增告警,檔案路徑是一般 Android 深度(約 70 字),`waive_cmd` 照 `_lint_waive_cmd` 的真實格式(`lumos lint-waive <16 碼指紋> --rule <規則> --file <路徑> --note "<為什麼放行>"`)。
- 實際:`_safe_path` 把每條放行指令截在 160 字。實測輸出的放行行結尾是 `--file …LoginViewModel0.kt --note `,必填的 `--note "<為什麼放行>"` 沒了(`scripts/lumos:76395` 標明 `--note` 必填);路徑更長時連 `--file` 的路徑也被截。檔名含空白時 `shlex.quote` 的引號會被截成不成對。
- 整段 `_reason` 再被截成 1490 字加「…」。實測 6 條告警只剩前 3 條多一點,第 4 條攔腰斷掉,「(另 N 條,跑 lumos lint-new --worktree --all 看全部)」那行整個不見。
- 預期:註解寫「最多 10 條」,放行指令要能照抄。
- 後果:AI 只看到前 3 條,修完後新批次才會出現後面的;三批上限用完後,剩下的告警不再擋。這是該擋沒擋的路徑。
引句:「lines.append(f"    放行:{sp(c.get('waive_cmd'))}")」
severity: major
blocking: 是

F2 逾時與失敗路徑沒有呼叫 `_hookevent.mark`,監控會顯示成功
- `_hookevent.guard` 的文件(`scripts/hooks/claude/_hookevent.py:160` 起)明說:內部吞掉逾時或失敗的鉤子必須自己 `mark("timeout"…)`,否則會被記成 `ok`,這正是 #19 r1 點名要防的假綠。
- 輸入:`lint-new` 跑超過內層時限(實跑預算 4 秒、lint-new sleep)。
- 實際:鉤子印「lint-new 超過時限,這次不檢查」後 `return 0`,`guard` 記一筆 `ok`。同一支鉤子的 rc2 和 rc3 也一樣。整支 patch 沒有任何 `mark(` 呼叫。
- 預期:逾時要記 `timeout`,否則 `lumos enforcement` 的 `stop-lint-hook` 一直是 active/ok,使用者以為每回合都檢查了,其實每次都逾時。
引句:「print("lumos 收工寫法檢查:lint-new 超過時限,這次不檢查(推送前閘照樣會判)", file=sys.stderr)」
severity: major
blocking: 是

F3 起點檔內容或 payload 型別不對時,鉤子拋 traceback 而不是放行
- 輸入一:`stop-turn/<會談>` 內容是 `{"prompt_id":"p5","t":"abc"}`(起點檔被改壞或舊版寫的)。實跑:`ValueError: could not convert string to float`,鉤子 rc1。
- 輸入二:Stop payload 的 `cwd` 是整數 5。實跑:`TypeError`(來自 `Path(start)`),rc1。
- 原因:`_hookevent.guard` 對這支沒開 `swallow`,例外直接往上丟。
- 預期:跟整支鉤子「寧可漏報」的政策一致,不擋也不丟 traceback。rc1 在 Claude Code 是非阻擋錯誤,但每回合都會跳出鉤子錯誤。
- 現實觸發條件偏弱,所以只列 minor。
引句:「cmd = [sys.executable, lumos, "lint-new", "--worktree", "--since", repr(float(rec.get("t") or 0)), "--json",」
severity: minor
blocking: 否

F4 Windows 上 `os.killpg` 不存在,逾時收尾會崩
- `merge-claude-settings.py` 有 win32 分支,代表這支鉤子可能被註冊到 Windows。
- `_kill_all` 的 `os.killpg(proc.pid, signal.SIGTERM)` 只捕 `OSError`,Windows 上 `os.killpg` 不存在,拋的是 `AttributeError`,逾時時鉤子崩潰。`_alive_group` 一樣只捕 `(OSError, ValueError)`。
- 預期:至少外層吞掉,或在 Windows 上不註冊。這條我沒在 Windows 上實跑。
引句:「os.killpg(proc.pid, signal.SIGTERM)」
severity: minor
blocking: 否

總結:最嚴重是 major(F1 放行指令與告警清單被截斷、F2 逾時被記成成功),會擋 2 條;另有 2 條 minor 不擋。

臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/邊界-sonnet/` 還在,有 `repo/`、`home/`、`fk/`、`hk/`、`w/` 和 `log`,收貨後請編排者刪。我沒有開著的程序在用它。
