severity: minor

審查方式:完整讀 r3-snapshot.patch、r1/r2 intake 與 r2 併發席報告。實驗全在我自己的臨時目錄(scratchpad/r3 的空 git repo、假 git、直接載入 scripts/lumos 的腳本),沒改 repo,沒跑任何會改設定的 claude plugin 子指令。

### F1 prune 在「還沒開始刪」就失敗時,訊息卻說「已刪了一部分」
severity: minor
blocking: 否 — 只是回報文字不實,不多刪也不少刪任何資料;資料面是安全的。

hunk:`_events_prune` 的 except 區塊與 `cmd_events` 印失敗的迴圈。
引句:「(已刪了一部分,剩下的檔案還在)」
問題:partial 旗標是用「例外之後資料夾還在、而且裡面還有東西」推出來的。但 stat 掃描階段(算 newest)與 rmtree 共用同一個 try。只要掃描時任一塊檔剛好被寫入端改名或刪除,就會在 rmtree 之前丟 OSError,走進同一條回報,資料夾原封不動卻被標成「已刪了一部分」。
具體時序→結果:
1. 會談 A 閒置超過 N 天,有 1.jsonl、2.jsonl。
2. prune 掃 newest,stat 2.jsonl 時它剛被改名,丟 FileNotFoundError。
3. except 判斷 d.exists() 為真且 iterdir 有內容,回 (A, True)。
4. 使用者看到「已刪了一部分」,以為歷史已缺損,實際一個檔都沒動。
重現(臨時目錄 p.py,用 mock 讓 stat 在 2.jsonl 丟 FileNotFoundError):
```
([], [('A', True)])
['1.jsonl', '2.jsonl']
```
佐證:r2 intake 把 r2 併發 F1 標為折入,修法是加這段回報;修法的判準沒有區分「掃描失敗」與「rmtree 失敗」。
引句:「寫入端同時在寫:檔案可能剛出現或剛被改名」

### F2 同時安裝的等待窗是固定的 3 秒左右,沒有總預算
severity: minor
blocking: 否 — 只影響 install 的訊息與耗時(回傳碼不看這一步),最終狀態由先到的那支完成;不在開場 hook 路徑上。
⚠ 真 claude 的並行行為我沒驗證(派工詞禁止會改設定的子指令),此條由程式結構推出,故維持 minor。

hunk:`_ledger_wait` 與 `_sync_claude_plugin` 的 add、install 兩處重試。
引句:「同時跑的另一支 install 可能還在寫:最多再查 tries 次、每次隔 pause 秒。」
問題:
- 窗口是 3 次 × (1 秒睡眠 + 一次 claude list 的耗時)。慢機器上對方的 add 超過這個窗口,後到的一支仍印「沒裝好」,而對方稍後把狀態做對,使用者被誤導去重跑。
- 錯誤出在 TimeoutExpired 時完全不進等待(它不是 RuntimeError):add 逾時 30 秒被殺,但實際可能已寫入,直接判 failed。
- 最壞耗時沒有總預算:add 失敗後每次 check 的 list 若各卡 30 秒,add 段約 3×31+30 秒,install 段同型,整體約數分鐘。這條路徑只在 install、update、init(已確認 `_sync_global_hooks` 有 `_refuse_if_probe`,hook 檔裡沒有任何入口呼叫它),不吃開場 hook 預算。
時序→結果:A、B 同時 install;B 的 add 回錯;B 的 3 次重查都落在 A 完成之前;B 印失敗,A 之後完成。
佐證:測試 t_ledger_plugin_teardown_scope_and_messages 的假 claude 延遲恰為 1 秒,只能證明窗口內的情形。

### F3 teardown 外掛移除失敗但市集移除成功時,留下指向已不存在市集的外掛
severity: minor
blocking: 否 — 失敗時已印兩條手動指令,結果可由使用者補齊。
⚠ 真 claude 移除市集時是否連帶處理其外掛我沒驗證。

hunk:`_teardown_claude_plugin`。
引句:「外掛那步失敗也照樣處理市集(各步獨立)」
問題:r2 要求各步獨立,這點做到了。代價是外掛 uninstall 失敗(例如被鎖)後市集仍被移除,剩下一個來源已被登記簿抹掉的外掛。
時序→結果:uninstall 回非 0 → 記入 errors → 市集 remove 成功 → 輸出「移除沒做完」與兩條手動指令;其中第二條 `claude plugin marketplace remove` 此時會因市集已不在而失敗,使用者照抄會看到新的錯。
佐證:輸出 `_LEDGER_MANUAL` 兩條是固定文字,不依實際剩下什麼調整。

### 前輪修復驗收
- r2 併發席 F2(enforcement 的 git 沒逾時):已修好,且實測有效。`_events_root` 改成 timeout=3。我用假 git(遇到 git-common-dir 就 sleep 15)在空 repo 跑整支 `lumos enforcement --json`:總共 4.4 秒,24 列都在;再加一個背景 sleep 孫行程握住管線,總共 3.9 秒,沒有被孫行程拖住(CPython 在 POSIX 上逾時只 kill 加 wait)。基線無 hang 為 0.9 秒,3 秒上限加基線仍低於開場內層預算 7 秒。
- r2 併發席 F3(兩支 install 只重查一次):已改成 `_ledger_wait` 最多再查三次、每次隔一秒,add 與 install 兩處都接上,終態判斷用 `ours()` 與 `_ledger_user_plugin`。方向正確,殘留限制見 F2。
- r2 併發席 F1(prune 刪到一半):已加 failed 清單與「已刪了一部分」提示;rmtree 失敗確實改成不崩、繼續處理其他會談。殘留問題是 F1(旗標在掃描階段失敗時誤報),另外「newest 檢查後、rmtree 掃描前才寫入的新塊檔會被靜默刪掉」仍存在,但只在閒置超過 N 天的會談恰好被續用的那一瞬間發生,維持 r2 的 minor 判斷,本輪不重列。
- 掃描成本新驗:在空 repo 造 20000 個會談資料夾,enforcement 總共 1.0 秒、列出 active 正常;`lumos events --json` 0.56 秒。沒有放大問題。
- 逾時與例外:`_claude_json` 與 `_claude_do` 的 RuntimeError、ValueError、OSError、TimeoutExpired 全被兩個進入點攔下;RecursionError 是 RuntimeError 子類,深巢狀輸出也被接住。`_events_main_trusted` 與 `_events_path_safe` 兩道在 prune 之前,rmtree 對被換成連結的目錄會拒絕,TOCTOU 沒找到洞。
- 測試執行器隔離:`LUMOS_SKIP_CLAUDE_PLUGIN=1` 與清 `CLAUDE_CONFIG_DIR` 在 `_isolate_environment` 內,沒找到繞過口。

### 圖譜鏡頭(固定席)
- 這次沒附固定席節點(派工詞已說明鏡頭計算超時),我沒有補算也沒有逐條判。唯一可補的觀察:`cmd_uninstall` 現在多了外掛移除、`cmd_events` 是新指令,講 uninstall 只拆 symlink 與 skills 的 Systems 節點(例如 slim-uninstall-一行卸載、lumos-deinit)可能落後一步,我沒打開驗證(⚠)。

總結:最嚴重 minor,blocking 0 條
