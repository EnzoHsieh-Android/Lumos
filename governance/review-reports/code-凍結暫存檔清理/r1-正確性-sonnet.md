severity: minor

審查範圍是整份 diff。我跑了 `python3.14 scripts/test_lumos.py -k loop_replay`,25 個測試全過。diff 裡沒有 blocker 或 major。我也試著在 `scripts/lumos` 和 `scripts/test_lumos.py` 找更重的洞,沒找到。

### F1 測試準備抽走後,舊測試留下兩個沒用到的匯入,ruff 會報 F401
severity: minor
blocking: 是 — 推送前閘跑程式規則檢查,這兩條是這份 diff 新造成的,不是舊帳。
引句:「def _replay_fx():」
失敗場景:準備步驟搬進 `_replay_fx` 之後,`t_loop_replay_freeze_and_golden` 還留著 `import hashlib as _h` 和 `import tempfile as _tf`,但函式本體已不再用到 `_h.`、`_tf.`(grep 計數 0)。`ruff check scripts/test_lumos.py --select F401` 在 `scripts/test_lumos.py:38097` 和 `scripts/test_lumos.py:38099` 報這兩條。manifest 裡同一位置也有對應的兩條 F401。修法是刪掉這兩行匯入。
佐證行:`scripts/test_lumos.py:38097`、`scripts/test_lumos.py:38099`

### F2 並行重凍時,先跑完的那邊的 finally 可能刪掉另一邊剛寫好的暫存檔
severity: minor
blocking: 否 — 要兩個 `--freeze` 同時撞同一個編號才會發生,改前沒有這個問題,但後果是 rc2 加一句可重跑的提示,不會壞資料。
引句:「_tmp.unlink(missing_ok=True)」
失敗場景:
1. A 做完 `os.replace`,尚未進 finally。
2. B 進來,`tmp.write_text` 寫好 `.verdict.tmp`,`target` 此刻已存在,B 把 A 的 `verdict.json` 歸檔成 `verdict-<時間>.json`。
3. A 的 finally 執行 `unlink`,把 B 的暫存檔刪了。
4. B 的 `os.replace(tmp, target)` 丟 FileNotFoundError,印出「新 verdict 換上位失敗」,這個編號暫時沒有現行 verdict。

改前沒有呼叫端 finally,B 的暫存檔不會被誰刪,B 會成功。使用者照訊息重跑 `--freeze` 即可,因為 `target` 不存在時不需要 `--note`。要完全避免,暫存檔名可以加 pid 或隨機尾碼。這個範圍我不要求修。
佐證行:`scripts/lumos:1160`、`scripts/lumos:986`

### F3 測試 ④ 用替身整個換掉 `_replay_write_verdict`,換上位失敗的真實路徑沒被測到
severity: minor
blocking: 否 — 呼叫端 finally 確實被測到,真實函式內部的「歸檔後 replace 失敗」那段只是沒有對應紅綠釘。
引句:「def _fail_after_tmp(tmp, target, vdir_, verdict):」
失敗場景:替身寫完暫存檔就回 2,所以只證明呼叫端的 finally 會清暫存檔。真實的 `target.rename(arch)` 成功、`os.replace` 失敗這條路徑從沒被執行。我手讀的結果是:暫存檔被刪,舊檔留在 `verdict-<時間>.json`,`verdict.json` 不存在;訊息教的「重跑 --freeze」仍成立。改前暫存檔還留著,可以手動搬上位,改後不行。這是可接受的取捨,不算回歸。
佐證行:`scripts/test_lumos.py:38242`

### 逐項確認過、沒有問題的地方
- 時間字串:`now().astimezone().strftime("%Y-%m-%d-%H%M%S")` 和原本 `now().strftime(...)` 取的是同一個本地牆鐘時間,字串一樣,DST 和台北凌晨都一樣。
- 模組可用性:`json` 和 `sys` 是模組層匯入(`import json` 在檔尾,函式呼叫時已存在),`datetime` 和 `os` 在函式內匯入。
- finally 裡的 unlink:`OSError` 被吞掉,其他例外照原樣往外傳,不會蓋掉回傳值。
- `--note` 檢查前移:被擋時暫存檔根本沒寫。測試 ② 驗證現行 verdict 位元組沒變,我看得過去。
- 舊測試 `t_loop_replay_freeze_and_golden`:準備步驟逐行搬進 `_replay_fx`,舊測試用到的變數都有回傳,沒有未定義的名稱,測試通過。
- 刪掉的兩個 `.verdict.tmp`:全 repo grep 只有 `scripts/lumos`、`scripts/test_lumos.py`、筆記和舊審查卷證在提這個檔名,沒有程式或測試讀那兩份檔。
- `.gitignore`:規則 `governance/replay/*/.verdict.tmp` 只比對這個檔名,不會蓋到 `verdict.json` 或 `verdict-*.json`。

### manifest(pitfalls)
落在新增行上的只有 F1 的兩條 F401(真隱患)和 E702 之類的舊風格雜訊。`cmd_loop_replay` 的 C901 是舊帳,這份 diff 讓它變輕,不是新增。

總結:共 3 條,最高 minor
