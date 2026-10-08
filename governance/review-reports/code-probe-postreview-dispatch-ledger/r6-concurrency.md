severity: major

## Finding CON6-01
severity: major
blocking: 是
引句:「fd = os.open(path, os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0))」
file: `scripts/scenario_probe.py:64`
- 具體輸入:`--out` 指到一個 FIFO,而且沒有人在讀。`_output_target_problem` 對 FIFO 一律回 None(`scripts/scenario_probe.py:38`),所以開跑前檢查放行。
- 走到哪一段:整批模型跑完後 `_atomic_write_text` 走到 FIFO 分支。`os.open(..., O_WRONLY)` 沒加 O_NONBLOCK,沒有讀端就一直卡在 open。
- 壞在哪:數十分鐘的模型額度花完,結果卻永遠寫不出去,程序也不結束。history 沒寫、`skills_health` 事故資訊也沒寫。
- 時間窗:這不需要攻擊者。檢查後把目標換成 FIFO,或操作者本來就放了 FIFO,都會卡住。
- 重現:對同一支 `_atomic_write_text(fifo_path, "x")`:
  - 修前 4d765d5c:立刻結束,FIFO 被換成普通檔 `-rw-------`。
  - 修後 483df9fe:被卡住,我手動 kill 才停。目錄裡 `out.json` 還是 `prw-r--r--`(FIFO)。
- 歸因:有證據的修復回歸。修前會 `os.replace` 換掉 FIFO,修後新增這個「照舊直接寫」分支才會卡。
- 同分支的縫隙:lstat 到 open 之間,目標若被換成普通檔,`O_WRONLY` 沒有 O_TRUNC,會在原檔上覆蓋前幾個位元組並留下舊尾巴。這一點我只做了語意驗證,沒有重現成探針路徑,所以不單獨列 finding。

## Finding CON6-02
severity: minor
blocking: 否
引句:「if replace and not os.access(path.parent, os.W_OK | os.X_OK):」
file: `scripts/scenario_probe.py:44`
- 具體輸入:`--history ro/h.jsonl`,`ro` 是 0555 目錄,`h.jsonl` 還不存在。
- 走到哪一段:history 的 `replace=False`,所以父目錄可寫檢查被略過。
- 壞在哪:檢查回 None,整批跑完才在 `os.open(..., O_CREAT)` 噴 PermissionError(`scripts/scenario_probe.py:1365`)。新增這個檢查正是要避免這種結果。
- 重現:`_output_target_problem('ro/h.jsonl', replace=False)` 回 None。同一目錄用 `replace=True` 則回「ro 不可寫…」。
- 歸因:有證據的原有漏查。修前根本沒有這個檢查,修補補得不完整。

## 其他已驗與判定
- 暫存檔撞名、殘留:
  - `tempfile` 的隨機名保證不撞,`finally` 只刪自己的暫存檔,所以同目錄兩個探針或探針與消融同時寫不會清到對方的。
  - SIGKILL 後殘留的 `.probe-out-*.tmp` 不會被讀端收到:`ablation_lumos_first.py` 只 glob `*.json`、`*.pending`、`*.candidate`(約 137、146、169 行)。
- umask 與執行緒:`scenario_probe.py` 和 `ablation_lumos_first.py` 裡沒有 Thread、concurrent、multiprocessing(grep 為 0),`os.umask(0)` 再設回的窗口沒有同程序競爭者。
- `--history` 追加:`O_APPEND` 加一次 `write` 寫一行,記錄遠小於緩衝,多程序行不交錯。符號連結換入會在跑完後 ELOOP,與開跑前檢查一致,只是時機較晚,屬 CON6-02 同類,不另列。
- tty 測試子程序超時與 pty fd 洩漏:`test_lumos.py` 的 hunk 我沒逐行驗,見未驗範圍。
- lint:未對 diff 範圍執行 `ruff check`。
- 圖譜固定席:這份 diff 動到 `lumos-cli-lifecycle`、`bound-tests-gate`、`guard-kill` 等節點的牽連檔,但沒有改動它們宣稱的合約:
  - re-inject 的 sentinel 行為
  - bound-tests 閘
  - guard kill 的 rc 優先序
  - 授權檔白名單
  - search 的 superseded 排除
  - design-loop 處置閘
- `測試假綠形態` 的前置斷言合約:新增測試是否遵守,我沒查。

## 修補三問
1. 原問題的修復效果:新建檔照 umask、暫存檔名短,這兩點屬於邏輯推論,我只做了讀碼。FIFO 的「照舊直接寫」在有讀端時行為成立,沒讀端時卡死(CON6-01)。
2. 相鄰路徑:既有普通檔不可寫仍報 PermissionError(程式碼讀過),裝置檔如 `/dev/null` 走直接寫。FIFO 與開跑前檢查的組合是新增的不一致,見 CON6-01。
3. 同一案例前後結果:FIFO 目標修前立即完成,修後卡住;不可寫父目錄的 history 修前後都跑完才失敗。

## 未驗範圍
- 三支新測試的執行與其殺傷力,另有全套在背景跑,我沒跑。
- 圖譜筆記 hunk 的內文與 `lint`。
- tty 子程序的 60 秒超時與殘留、pty fd 洩漏。
- `render_md` 轉義改動。
- 實驗目錄的 FIFO 殘留與 `ro` 目錄我已清掉。

總結:最高嚴重度 major
