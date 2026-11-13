severity: minor

## z1 SIGTERM 的保護只到殺傷力結束,寫計劃到記帳之間仍是預設處理
severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後兩版都只有殺傷力那一段裝處理器,這個窗口兩版一樣;修補沒擴大也沒縮小它)

引句:「處理器只裝在殺傷力那一段、離開還原,進來前是忽略的照留」
file: `scripts/lumos:75789`(修後版 `cmd_situation_rule` 的 `_vault_write_lock` 區塊到 `_gate_event` 之間)

失敗場景:
1. 殺傷力跑完、使用者在終端答 y 之後,`_situation_rule_write` 已把條款寫進計劃,還沒走到 `_gate_event`。此時送 SIGTERM,程序用預設處理直接結束。
2. 結果是計劃有 S<n>,治理帳沒有 situation-rule。「計劃已寫入,治理帳沒記到」那段補記說明沒機會印出來。
3. 重跑會被修補新加的「計劃已寫過 S<n>」去重拒絕,補記事件也沒人印給使用者。規格閘會把那條當新行為。
4. 實際影響窗口是毫秒級,所以只評 minor。
5. 沒有實跑這個窗口,只是讀碼。兩版查證:`git show 6ccb7a46:scripts/lumos` 與 `git show 1d535b07:scripts/lumos` 都只有 `_situation_rule_kill` 一處呼叫處理器,寫入段沒有。

## z2 `--keep-worktree` 在 worktree 建不起來時留下永遠清不掉的空資料夾
severity: minor
blocking: 否
歸因:有證據的修復回歸。標記是這次修補新加的,修前沒有標記,同一個殘骸過一天就會被清掉。

引句:「_ISOLATED_WT_KEEP_MARK = ".lumos-keep"          # keep=True 保留的現場在暫存資料夾裡寫這個檔,清殘骸跳過」
file: `scripts/lumos:27547`(`_isolated_worktree` 的 keep 分支),`scripts/lumos:27578`(sweep 的跳過條件)

重現:
1. 把 `_isolated_worktree` 指向一個不是 git repo 的目錄,帶 `keep=True`。
2. 結果是 `wt.ok=False`("not a git repository"),但 finally 照樣寫入 `.lumos-keep`。
3. 把該資料夾的 mtime 調到超過 `_ISOLATED_WT_STALE_SEC`,跑 `_isolated_worktree_sweep`,資料夾還在(`after sweep exists: True`)。
4. 資料夾裡只有標記檔,沒有任何現場可看,但永遠不會被回收。
5. 修前版沒有標記,同一個殘骸超過一天就會被 sweep 清掉。
6. 修法:`wt.ok` 為 False 時不寫標記(或直接刪 parent)。
7. 影響很小(一個空資料夾,而且要 `--keep-worktree` 加建樹失敗才會碰到),所以是 minor。

## 附:三問、圖譜鏡頭

**①子程序與訊號**
- 驗證方式:載入修後版 `scripts/lumos`,在小 git repo 裡跑 `_situation_rule_signals()` + `_isolated_worktree` + `_kill_run`。測試指令是 `sleep 300 & wait`,等 pid 檔出現後才送訊號。
- 單一 SIGTERM:收到 KeyboardInterrupt,`sleep` 子程序已不存在,暫存工作樹資料夾已刪,repo 的 `git worktree list` 乾淨。
- SIGTERM 加 SIGHUP 雙重訊號:間隔 0.5ms、3ms、10ms、30ms、80ms 各跑一次,結果都一樣,沒有殘留程序或資料夾。
- 離開後:`getsignal(SIGTERM)` 還原為 0(SIG_DFL),同一程序後續再跑別的指令不受影響。
- 沒驗到:第二個訊號剛好落在 `_kill_run` 的 `except KeyboardInterrupt` 裡、`killpg` 之前。這個窗口沒打到,標 ⚠ 未判定。
- 訊號落在 `Popen` 回傳到指派給 `proc` 的幾個位元組碼之間,同樣是理論窗口,未驗。
- 殺傷力開始前的 SIGTERM:`cmd_guard_kill` 在建工作樹之前沒有開子程序或改檔,只靠讀碼判斷,沒實測。
- 寫計劃當下的 SIGTERM:見 z1。

**②時間預算與記憶體**
- `_expected_gov` 把治理帳讀一次存進 `ctx["exp_gov"]`。人裁集合在門判 high 與生效日之後才算,風險低或生效日前的計劃不讀帳。
- 推送前一圈最多讀一次帳,這點只靠讀碼判斷。我沒有造 12 萬行的帳實測,所以讀帳的記憶體量也未驗。
- 已知:`_gov_vc_gate_events` 以 `limit=None` 把整本帳讀進記憶體,再用位元組先篩,這是修前就有的做法,修補沒有加重。
- `_kill_run` 的逾時預算沒動。
- `_situation_rule_insert` 的去重是線性掃描,沒有二次方工作。
- `_kt_sit_read_many` 取代了不帶逾時的 `git show`,是改善。

**③標記檔寫失敗時**
- `_isolated_worktree` 寫標記失敗時 `except OSError: pass`,現場留著但沒標記。下一次 sweep 可能在超過一天後把使用者刻意保留的現場刪掉。這是低機率情況,沒有實測。

**④互相蓋掉**
- `_lint_wt_begin` 只在 lint-new 的工作樹模式裝 SIGTERM,是另一個指令的程序。
- `cmd_situation_rule` 與它沒有同程序共用的路徑,我沒找到呼叫端。
- `_situation_rule_signals` 只在 `_situation_rule_kill` 的 `with` 裡存在,進入時記下原處理器、離開時還原。進來前是 SIG_IGN 的訊號不替換,所以 nohup 情形不被蓋掉。
- 測試覆蓋:`t_situation_rule_term_signal` 實際收到 SIGTERM 與 SIGHUP,驗程序群組收掉和處理器還原。子程序測試把 SIGHUP 設為 SIG_DFL,沒覆蓋 SIG_IGN 保留這條。把 `cur == signal.SIG_IGN` 那段拿掉,測試抓不到。這只是覆蓋面不足,沒有具體失敗場景,所以不算 finding。
- 其他呼叫端(合約測試閘、guard kill 本身)沒有裝這個處理器,行為未變。

**圖譜鏡頭**
- 固定席筆記因鏡頭計算超時沒有附上,依派工詞不自行補算。
- 修補差異裡跟資源相關的筆記文字(`Systems/guard-kill.md`、棧別提問表態閘、規格閘,以及計劃的〈中斷〉與天花板 8)已核對,與修後程式一致。
- 天花板 8 講的「孫程序另開 session 逃出群組」與「SIGKILL 工作樹留給下次清」都照實,沒有看到跟程式矛盾的說法。
- 其餘筆記牽連:未判定。

**清理**
- 實驗只用自己建的暫存目錄與子程序,全部已刪。`ps` 與暫存區都查過,沒有殘留。

最嚴重 severity:minor;blocking 共 0 條。
