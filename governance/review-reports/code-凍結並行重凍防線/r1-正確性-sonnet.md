severity: minor

整體判斷:修補本身正確。我另外挑了一個剩餘的窗口,列在 F1。

**已驗主張與證據**
- 我在 `/tmp/lumos-seat-work/code-凍結並行重凍防線/正確性-sonnet/c` 的 clone 跑了 `-k loop_replay`,31 個測試全過。這個 clone 在 HEAD 50574f11,已含這份 diff 的內容。
- 我把寫入端的判斷刪掉(只刪 `_replay_write_verdict` 裡 `if not note or not note.strip():` 那 3 行),清掉 `__pycache__` 後跑 `-k loop_replay_freeze_race`,結果是 0 passed、3 failed,也就是三個檢查全紅。所以測試真的鎖住了修補。
- 測試替身 `_race` 換掉 `m._replay_git_blob`。這個函式在 `cmd_loop_replay` 的卷證迴圈(`scripts/lumos:1151`)被呼叫,時機在開頭檢查(`scripts/lumos:1103`)之後、`_replay_write_verdict`(`scripts/lumos:1179`)之前。替身只在判定檔還不存在時才寫入對方的檔,所以模擬走得到修補那一行,修補拿掉後也不會假綠。
- 被擋下時暫存檔的處理:`_replay_write_verdict` 在 `tmp.write_text` 之後才判 note,擋下時回 `(2, None)`。呼叫端的 `try/finally`(`scripts/lumos:1178-1184`)照樣 `os.unlink(_tmp)`,暫存檔會清掉。擋下分支沒有任何 rename 或 replace,對方的 `verdict.json` 不會被動到。測試的第二個檢查驗證了這點。
- `vdir/target` 提前到開頭組:`root` 在原本的 `_cur_v` 就已使用,值不變。`vdir.mkdir` 仍在原位(`scripts/lumos:1172`),在帳本空、處置閘 rc2、無輪次這幾個提早 return 之後。所以那幾條路徑不會多建目錄,行為不變。
- 帶 `--note` 的重凍:寫入端判斷為真,照舊歸檔,然後走 `_refroze`、`note.strip()`。這時 note 必有值。
- 第一次凍結:`target.exists()` 為假,不進判斷。
- 回放模式(`--golden`):在 `if freeze:` 區塊之外,完全沒動。
- `_replay_refreeze_blocked` 讀現行判定檔時,壞 JSON 會丟 ValueError(含 UnicodeDecodeError),目錄會丟 IsADirectoryError(OSError),頂層是 list 會丟 AttributeError。三者都被 except 接住,`cur` 變成 `?`,不會崩。對方寫到一半時走壞 JSON 這條,結果同上。
- 其他 `note.strip()` 呼叫點:`scripts/lumos:1188` 只在 `_refroze` 為真時執行。寫入端現在保證有歸檔就有 note,所以 `note=None` 不會再走到這裡。`_replay_write_verdict` 的 `note=None` 預設值只讓舊替身相容,不會繞過檢查。
- 表態記錄(`py-eventloop na`)與這份 diff 無關:改動範圍內沒有 async。
- pitfalls manifest:所有 claims 都落在原本就有的行(例如 1050 的 C901、1167/1219 的 E741、1209 的 F541)。diff 新增的行是 996-1015、1100-1104、1179,沒有 claim 落在上面。
- 圖譜鏡頭:diff 動到的家筆記是 `loop-convergence-recording.md`。PITFALL 行補了 test 與說明,REVISIT 加了 `[closed:...]`,內容與程式一致。這份筆記沒有被牽連的 INVARIANT 受影響。
- 未驗範圍:沒有真的開兩個行程做並行競賽,也沒有跑全套測試。

### F1 寫入端的檢查和 os.replace 之間仍有窗口
severity: minor
blocking: 否 — 這是原本就有的 TOCTOU,diff 目標(沒帶 --note 的重凍不得歸檔別人的檔、不得崩潰)已達成,剩下的是另一種結果。
引句:「            _replay_refreeze_blocked(target)」
失敗場景:兩個第一次凍結 A、B 同時跑。
1. A 在寫入端執行 `target.exists()`,得到 False,所以不進判斷。
2. B 在此刻用 `os.replace` 寫好 `verdict.json`。
3. A 接著執行 `os.replace(tmp, target)`,無聲覆蓋 B 的判定檔,沒有歸檔、沒有留痕。

無論 A 有沒有帶 `--note` 都會發生。這個窗口比前一版小很多,但不是零。要完全消除,得改成不覆蓋的原子建立(例如 `os.link(tmp, target)` 遇到 FileExistsError 就走重凍路徑)。因為目標檔本來就是歸檔不覆寫歷史,這裡只提醒,不要求這輪修。
佐證行:`scripts/lumos:1008-1009` 的 `if target.exists():` 在 `scripts/lumos:1025` 的 `os.replace(tmp, target)` 之前,兩者之間沒有鎖。

總結:共 1 條,最高 minor
