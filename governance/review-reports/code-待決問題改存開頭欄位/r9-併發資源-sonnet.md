severity: major

這輪沒看到平方級或記憶體問題,但簽核被 Ctrl-C 中斷時,帳會留下一行簽核紀錄,而筆記已被還原。

1. Ctrl-C 落在 `_signoff_append` 裡面時,簽核帳不會截回,帳上留著一行已完成的簽核。
severity: major
   blocking: 是
   - `_signoff_append` 只接 `(OSError, UnicodeError, WriteBlocked)`,KeyboardInterrupt 直接穿過去,只有 `finally` 關描述子,不做 `ftruncate`,新建的帳也不刪。
   - `_signoff_write_locked` 的 `except BaseException` 只還原筆記。
   - 結果是筆記回到沒有 signed_off,簽核帳卻多一行帶 `ref` 的紀錄。
   - `_guard_signoff_refs` 讀這本帳,`guard abandon` 靠它判斷「有人簽核過」。所以這一行會讓一次被中斷、使用者沒完成的簽核,變成放棄合約的授權。
   - 最小重現(把 `os.fsync` 換成丟 KeyboardInterrupt,走真的 `lumos signoff Systems/S --ref Systems/S --note n`):
     - 修後:KeyboardInterrupt 往外丟,筆記已還原,`.signoff-log.jsonl` 存在且含該行,`_guard_signoff_refs` 回 `{'Systems/S'}`。
     - 修前:筆記沒還原,帳同樣留著那一行。
     - 單獨呼叫 `_signoff_append` 也一樣:舊帳會變成「舊行加新行」,新建的帳不會被刪。
   - 腳本在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-併發資源-sonnet/e2e_ki.py`(`python3.14 e2e_ki.py lumos_after.py` 或 `lumos_before.py`)和 `ki.py`。
   - 測試 ③e 把整支 `_signoff_append` 換成直接丟 KeyboardInterrupt,所以帳的狀態根本沒被檢查。
   - 圖譜 `Systems/lumos-cli-write.md` 第 118 行和計劃第 91 行都寫「Ctrl-C 也還原」,只講筆記,沒提帳上會殘留一行。
   - 歸因:有證據的原有漏查。修前同樣會留帳,這輪補了筆記還原,但帳那一半沒補。
   - 引句:「Ctrl-C 這類程序內中斷落在筆記已寫、帳還沒寫完之間:先還原筆記再往外丟」
   - file: `scripts/lumos:9193`、`scripts/lumos:9225`、`scripts/lumos:16744`

2. 測試 ⑤ 驗不出「拿鎖後才讀原稿」這條修補。
severity: minor
   blocking: 否
   - 助手程序在寫完 done 之後才寫 `ready`,signoff 是在 `ready` 之後才啟動,所以不論原稿在鎖前還是鎖後讀,讀到的都是 done。
   - 變異驗證:在 75620ccf 的獨立 worktree 把 `original = _signoff_read_original(path)` 搬到 `with _vault_write_lock` 之前,`-k qfm_r8_signoff_and_write_refusal` 仍是 13 passed, 0 failed。
   - 對照組:把 `os.ftruncate(fd, pos)` 拿掉會讓 ③ 變紅,所以這個 worktree 的測試確實有套到變異。
   - 這個測試也靠固定的 5 秒等待和 0.4 秒持鎖,負載重時時序不穩。我沒實測到失敗。
   - 歸因:未判定。這是這輪新增的測試,修前版本沒有它。
   - 引句:「check("⑤ 另一程序持鎖寫成 done 後，signoff 才進鎖；帳捷徑失敗時保留那個改動且目標帳不變"」
   - file: `scripts/test_lumos.py:57566`、`scripts/lumos:9262`

3. `_write_refusal_reason` 檢查後到 `os.open` 之間,帳可以被換成硬連結。
severity: minor
   blocking: 否
   - `O_NOFOLLOW` 擋住了符號連結,但硬連結只在 `os.open` 之前用 lstat 查一次,開檔後沒用 `fstat` 再查 `st_nlink`。
   - 重現(`tocttou.py`):在檢查通過後立刻 `os.link(victim, log)`,簽核行會被追加進 victim 檔。失敗時的 `ftruncate` 也會截到那個檔。
   - 需要同使用者的外部程序競爭,所以我只當小問題。
   - 修前用 `open(log,"ab")` 連符號連結都會跟,所以只是部分改善。
   - 歸因:有證據的原有漏查。
   - 引句:「★不帶緩衝、不跟符號連結★(代碼審 r8 正確性、併發、邊界席」
   - file: `scripts/lumos:9176`、`scripts/lumos:9183`

4. ⚠ Ctrl-C 的窗口還有兩處沒蓋住,我沒做完整重現。
severity: minor
   blocking: 否
   - 第一處:`_cmd_set_locked` 在 `try` 之外。筆記換入之後、`try` 開始之前被中斷,筆記會留著 signed_off 而帳沒有紀錄。
   - 第二處:`BaseException` 路徑裡 `_signoff_restore_note` 的回傳字串被丟掉。還原失敗時使用者只看到 KeyboardInterrupt,不知道筆記仍帶 signed_off。
   - 歸因:未判定。
   - 引句:「被強制殺掉或斷電仍不是跨檔交易,見圖譜的回頭條件」
   - file: `scripts/lumos:9215`、`scripts/lumos:9225`

三問:
- ①原問題的修復效果:
  - 資源面:所有最壞輸入都是線性,沒有平方級。
    - 輸入包含連串 `- `、連串 `&a`、4 萬字單行 flow、巢狀括號、很長的引號鍵、4 萬個 emoji、重複的 ZWJ 和 FE0F、2 到 4 萬行的各種頂格鍵和決策。
    - 最慢的是 4 萬題,耗時 1.4 秒、記憶體峰值約 18MB。
    - 這些情形的耗時和記憶體都跟輸入大小成正比,沒有平方級。
  - 併發面:6 個 signoff 加 6 個 set 同時跑同一篇,6 行帳、筆記完整、沒有殘留暫存檔。
  - 磁碟滿、帳是目錄、檢查失敗的截回和還原,有測試和程式碼佐證。
  - 缺口:Ctrl-C 這一格,帳沒截回(見 1)。
- ②正常、錯誤、相鄰路徑:
  - 正常的 signoff、set,以及 guard、decision 各分派的擋下訊息仍成立,`_cli()` 兜底也成立。
  - 相鄰路徑 `guard abandon` 會被 1 的殘留帳誤放行。
- ③同一案例修前、修後:案例 1 修前筆記和帳都不還原,修後只有筆記還原。案例 3 修前、修後都會寫穿到被換進來的硬連結。

總結:簽核被 Ctrl-C 中斷時帳殘留、可被 `guard abandon` 當授權,是會擋合併的問題;其餘是測試漏洞和小窗口。

(收尾:實驗放在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-併發資源-sonnet/`。我建的 `wt` worktree 已移除,現場留給編排者刪。)
