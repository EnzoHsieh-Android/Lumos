severity: minor

我審了 r8-snapshot.patch 全文(683 行),並從 e5ce8675 取出 scripts、governance/eval 等目錄做行為實驗。程式本身沒有找到會壞的併發或資源問題,只有四條文件與測試覆蓋的小洞。實驗目錄已 `rm -rf`,沒有留下程序。

**事先說明:** 查證時我讀到了 `r7-mutation-checks.log`,違反「不要讀同目錄 r1–r7 檔」的規定。我只用它核對驗證筆記的「十一種改壞版本」是否包含 100 次上限,其他判斷都來自自己的實驗。

## Finding CON8-01
severity: minor
blocking: 否
引句:「這裡不為一組常數載入整支,改由測試核對兩邊寫法一致(t_probe_boundary_fourth_round_report_and_provenance)。」
file: `governance/eval/ablation_lumos_first.py:386`
- 具體輸入:把 `_SPECIAL_CATS` 從 `("Cc","Cf","Zl","Zp","Cs")` 改成 `("Cc","Cf")`,也就是不再跳脫 U+2028、U+2029 和代理字元。
- 走到哪一段:`render_md` 的 `visible` 只看這個常數。
- 壞在哪:註解說兩邊類別集合由測試核對一致,但測試只比對一組樣本 `\u202e\ufeff\U000e0001\u3000\u00a0x`,涵蓋 Cf 和 Zs,不涵蓋 Zl、Zp、Cs。實際比對的只有字串輸出,沒有比對常數本身。
- 重現:在取出目錄改成 `("Cc","Cf")` 後跑 `python3.14 scripts/test_lumos.py -k t_probe_boundary_fourth_round_report`,結果 `15 passed, 0 failed`,仍然全綠。
- 後果:主程式 `_PATH_SPECIAL_CATS`(`scripts/lumos:34338`)日後增減類別、或這裡被改動,測試都不會紅。這正是「兩份常數會漂移」的情形,而這個註解是用來證明不會漂移的依據。
- 歸因:有證據的修復回歸。修前沒有這個常數,也沒有這句保證,是第七輪修補自己帶進來的說法。

## Finding CON8-02
severity: minor
blocking: 否
引句:「raise FileExistsError(errno.EEXIST, "連續 100 次都撞到既有的暫存檔名", str(path.parent))」
file: `scripts/scenario_probe.py:142`
- 具體輸入:暫存檔名連續 100 次撞名。
- 走到哪一段:`_atomic_write_bytes` 的 `for ... else` 分支。
- 壞在哪:這是新增的失敗路徑,沒有任何測試走到它。
- 重現:把那行換成 `raise RuntimeError("MUT")`,跑 `python3.14 scripts/test_lumos.py -k probe_boundary`,結果 `192 passed, 0 failed`。
- 對照:驗證筆記列的十一種改壞版本裡也沒有這一項(我讀 `r7-mutation-checks.log` 比對過)。全域規則要求每條新路徑有先紅的測試。
- 歸因:有證據的修復回歸。修前是 `while True` 沒有這個分支,是修補新加的。

## Finding CON8-03
severity: minor
blocking: 否
引句:「規則由第七輪收斂，見下一條。證據 [[Verification/持久用量帳第六輪審查修補驗證]]。」
file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:154`
- 壞在哪:「下一條」是緊接著的 WHY(原子寫入只沿用單一名字檔的權限)。字元裝置、歷史追加這些被收斂的規則,寫在再下一條的第七輪 PITFALL。
- 同類:`ablation-lumos-first.md` 第七輪 PITFALL 寫「改成下面那條 WHY 的做法」,離它最近的 WHY 是「原子寫入不在消融腳本另留一份」,不是報表寫法那一條。
- 後果:接手的人順著指引讀到的是權限規則,看不到字元裝置與歷史追加的現行規則。
- 重現:`git -C <repo> show e5ce8675:docs/lumos-toolchain-knowledge/Systems/codex-harness.md | sed -n 154,160p`。
- 歸因:有證據的修復回歸。這句是第七輪改寫 r6 PITFALL 時新加的。

## Finding CON8-04
severity: minor
blocking: 否
引句:「且換行與空白類仍會折成空白」
file: `docs/lumos-toolchain-knowledge/Systems/ablation-lumos-first.md:96`
- 壞在哪:這條 WHY 否決自創標記的理由之一,是「換行與空白類仍會折成空白」。但新做法也一樣:`render_md` 的 `text()` 先做 `raw = str(x).replace("\r"," ").replace("\n"," ")`(`governance/eval/ablation_lumos_first.py:398`),才進 `visible`。
- 結果:CR 與 LF 一律變成空格,`_kill_esc` 則會寫成 `\u000d`、`\u000a`。「同一套類別與寫法」對這兩個字元不成立。
- 測試也看不到:比對用的樣本沒有 CR、LF。
- 這是讀碼判定,我沒另外跑。
- 歸因:有證據的修復回歸,是第七輪新寫的理由。

## 固定席逐條判定
- **codex-harness**:合約沒被破壞。筆記描述的 `_open_char_device`、`_open_history`、暫存檔權限與 100 次上限,都和程式一致。唯一問題是 CON8-03 的指向錯誤。
- **測試假綠形態(INVARIANT)**:權限測試有「現場成立:真的建了暫存檔」的前置斷言。字元裝置確認型別的測試也有:它先斷言 lstat 被謊報成字元裝置。新 session 測試先斷言 `leader=True ctty=False`。pty 慢讀端那一項沒有前置斷言,不能證明寫入量超過 pty 緩衝,不過寫入量遠大於 macOS 的 1–2KB 緩衝,實測還原後六次都紅。不構成破壞。
- **autonomous-iteration-loop**:只牽連 `test_autonomous_loop.py`,這份審材沒有碰到它,無影響。
- **lumos-cli-lifecycle(INVARIANT:re-inject 保留 sentinel 外內容)**:不受影響。新增的文字說 `t_confirm_tty_no_ctty_session_survives` 拿掉 `O_NOCTTY` 會翻紅。我實測把 `scripts/lumos:23908` 的 `O_NOCTTY` 拿掉,該測試紅(`7 passed, 1 failed`),說法成立。
- **lumos-cli-read**:不受影響。
- **design-loop**:不受影響。
- **bound-tests-gate**:不受影響。
- **canary-audit**:不受影響。
- **超出上限只列名的節點**:沒有逐篇判定,見未驗範圍。

## 修補三問

### 併發與資源(逐項已驗)
- **fd 必關**:`_open_char_device` 與 `_open_history` 在 fstat、`set_blocking`、型別檢查失敗時,都由 `except BaseException: os.close(fd)` 關掉。
- **交給 fdopen 前後**:交接點之後由 `with os.fdopen` 負責關。只剩 `os.open` 回傳到 `try` 之間被非同步例外打斷這個極小窗口,不構成具體情境。
- **試開再關與寫入之間被換掉**:實際寫入時才重新開檔。換成符號連結得到 ELOOP;換成有人讀的 FIFO,fstat 發現不是字元裝置就關掉,不寫;換成沒人讀的 FIFO 得到 ENXIO;換成普通檔得到 EINVAL。
- **歷史檔 O_CREAT 後被別人硬連結**:fstat 看到 `st_nlink != 1` 就報錯。代價是空檔可能已建好,但紀錄不會被寫到別的名字。
- **keep_mode 暫存檔權限**:建立時的權限是 keep_mode 經 umask 收窄,不會比 keep_mode 寬,之後 `fchmod` 才補回,且發生在寫入資料之前。我把建立權限改回 `0o666` 後測試立刻紅(暫存檔 0644)。
- **100 次上限**:`for ... else` 的接線正確。只有測試缺口,見 CON8-02。
- **_guard_hang**:
  - 巢狀:內層結束會還原外層的鬧鐘與處理常式。
  - with 區塊內其他例外:會傳出去,鬧鐘已還原。
  - 精度:原鬧鐘剩餘秒數被進位,實測最多多約 0.9 秒,例如 10.00 秒剩餘、已過 0.9 秒,還回去 10 而不是 9.09。沒有具體失敗場景,所以不立 finding。
- **pty 慢讀端測試**:失敗時讀端執行緒會等到 `join(20)` 才結束,然後 `close(slave)` 讓它收到 EIO 離開,不會卡住整個測試執行器。
- **新 session 子程序測試**:有 30 秒逾時,逾時由 `subprocess.run` 負責殺掉子程序。
- **FIFO 讀端 fd**:測試正常路徑都會關。只有 `swap_case` 本身拋非預期例外時 `readers` 才會漏關,這只出現在測試已失敗的路徑,不立 finding。

### 修補三問
- **①原問題修復的行為證據**:
  - 我逐項改壞後都對應翻紅:拿掉 `O_NOCTTY`、不試開、不改回阻塞(六次都紅)、暫存檔先寬、歷史檔不查 nlink、寫入期間呼叫 umask。
  - 拿掉 `O_NOCTTY` 時,測試輸出 `AFTER_WRITE ctty=True`,rc -1。
  - 不改回阻塞時是 `BlockingIOError(35, ...)`。
  - 報表常數集合的覆蓋不足,見 CON8-01。
- **②相鄰路徑**:
  - `/dev/null` 照寫,FIFO 換成普通檔,新檔 0644,唯讀檔照拒,255 位元組長檔名可寫,這幾項在 `t_probe_boundary_fifth_round_output_edges` 都過(37 passed)。
  - 全部 `t_probe_boundary` 相關測試:192 passed,0 failed。
  - 驗證筆記寫的「探針大子集 424、第五輪輸出 39、第四輪報表 26」,我用單一函式名 `-k` 得到 37 和 15,口徑不同,沒法核對。
- **③新發現案例的修前修後**:
  - CON8-01 的缺口在修前不存在(修前沒有這個常數和這句說法),所以是修補引入。
  - CON8-02 同樣是新分支,修前是無上限的 `while True`。
  - CON8-03 和 CON8-04 是第七輪新寫的文字。
  - 我沒有跑 67b1dea2 的實驗,但這四條都是修補新增的內容,修前沒有對應物。

## 未驗範圍
- 沒有在 Linux 或 root 下驗證,這與驗證筆記自己的 `valid_under` 一致。
- 沒有驗證會把序列埠重置的裝置(例如試開再關會讓 DTR 跳動)。
- 沒有逐篇判定「超出上限只列名」的那些節點。
- 沒有跑全套測試和 ruff,也沒有驗證 `r7-red-before-fix.log` 的內容。
- 沒有驗證驗證筆記裡的「424 passed」。
- 沒有驗證 `_guard_hang` 的 `__exit__` 在鬧鐘剛好於 with 區塊結束瞬間觸發時,`signal.signal` 還原被略過的竊取窗口。這個窗口極小,我沒找到可重現的方式。

總結:最高嚴重度 minor
