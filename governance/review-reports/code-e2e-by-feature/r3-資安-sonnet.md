severity: minor

## S1 查證紀錄目錄是捷徑時,紀錄檔會寫到 repo 外
severity: minor
blocking: 否
- 歸因:有證據的原有漏查。同一支 `_e2e_record_update` 在修前版本(787dd51b)就有,兩版結果一樣。
- 攻擊路徑:
  - 誰:打開陌生 repo 的使用者,攻擊者是那個 repo 的作者。
  - 從哪裡:repo 裡提交一個捷徑 `.lumos/e2e-records`,指向 repo 外的目錄。使用者照常跑 `android-e2e judge` 寫紀錄,或按功能跑寫 `feature_runs`。
  - 送什麼:只有那個捷徑,沒有別的輸入。
  - 拿到什麼:`<64 位十六進位>.json` 這種固定檔名的 JSON 檔,被寫進捷徑指向的目錄。檔名不可控,內容是紀錄結構,所以只能算縱深防禦。
  - 前提:要走到寫紀錄這一步,就得先跑過這個 repo 自己的 `build` 與 `macrobench_cmd`。這些指令本來就是專案自己的設定,打開陌生專案時已經是外來輸入。所以這條幾乎沒有額外的攻擊面,也寫不出更大的後果。
- 查證命令:
  - 臨時 repo 裡做 `.lumos/e2e-records -> ../../out`,用 `git show <提交碼>:scripts/lumos` 取出的兩版分別載入,呼叫 `_e2e_record_update(repo, "f"*64, mut)`。
  - 載入版本:兩版都由 `importlib` 從 `git show` 輸出的檔案載入,載入後印出 `__file__` 確認。
  - 修前(787dd51b):`out/ffff…ffff.json` 被建出來。
  - 修後(4b056532):同樣被建出來。
- file: `scripts/lumos:40827`(修後版本的 `_write_lf(p, json.dumps(rec, …))`)
引句:「p.parent.mkdir(parents=True, exist_ok=True)」

## 三類各一段
- 提示注入:已看,無。這次新增的自由文字(功能名、情境名、效能方法名)進的是判定器、`sh -c` 與終端訊息,沒有進給 AI 的派工詞或 hook 附加段。
- 讀寫與執行越界:已看,除 S1 外無。
  - 效能方法名換進 `sh -c`:
    - 修前規則 `[A-Za-z0-9_.$][A-Za-z0-9_.$#]*` 收 `$`,所以 `$HOME`、`Outer$Inner#test` 通過設定檢查。
    - 修後規則 `[A-Za-z0-9_.][A-Za-z0-9_.#]*` 把這兩個都擋掉。
    - 我另外逐項驗過:`$(…)`、反引號、`;`、`|`、`&`、空白、換行、`-` 開頭、`#` 開頭、`-` 都不收。`fullmatch` 不會被結尾換行放過。
    - `.`、`..`、`A.b#c` 放進 `printf`、帶前綴字、帶雙引號三種寫法,`sh` 都當一般字,不會變成註解、展開或萬用字元。
    - `lumos` 與範本腳本 `run.sh` 兩邊的規則一致。修前 `run.sh` 也收 `$`,修後同步拿掉。
    - 我沒有真的跑完整的 `run.sh` 流程(沒有裝置),所以「`run.sh` 遇到 `$` 名會 die」只是讀程式的結論,沒有實跑證據。
  - 記憶體情境名:
    - `lumos` 只收 `[A-Za-z0-9_-]+`,run-id 另有一條 `[A-Za-z0-9._-]+` 檢查,產物路徑 `<run-id>.<情境>` 不會出現路徑分隔字元。
    - `LUMOS_STABILITY_SCENARIO` 在收集腳本裡只用來查 `stability_scenarios` 的鍵,不進路徑,也不進 shell。
    - `run.sh` 在整套跑時會先拿掉環境裡殘留的這個變數,本席已讀到這段程式。
    - 收集腳本在這次修補前後沒有改動(`diff` 為空)。
  - `stability_scenarios.driver` 與 `macrobench_cmd`、`build` 都是設定檔給的指令,由 `sh -c` 在主機上跑。這是設計上就有的行為,執行前使用者要主動啟動 `run.sh`,不是一步就意外走過。
  - `features.paths`:只做字串比對,不讀檔,絕對路徑與 `..` 本來就擋。修補多擋了 `//`、`/./`、`.`,這是正確性問題。
  - `--changed` 用到的 `git diff --name-only HEAD`、`ls-files`,走的是原本就有的 `_lens_git`,沒有新增 hook 或外部程式的執行路徑。
  - 測試檔與 patch 裡沒找到新寫進的密鑰或信箱。
- 非刻意繞過守衛:已看,無。
  - 殘留的 `LUMOS_E2E_COLLECT`(換成替身收集腳本):`run.sh` 會把它記進 `steps.json` 的 `collector_override`。這個欄位在修前版本的 `lumos` 裡沒有,是本輪範圍內新增的。修補在 `_e2e_feature_record` 補了檢查,按功能跑時就不寫查證紀錄。
  - 按功能跑寫的 `feature_runs` 只寫進 `feature_runs`,`runs` 仍是 `null`。本席沒有找到會讀 `feature_runs` 並放行的閘,所以沒有「沒驗完整的版本被記成驗過」的路徑。
  - `_e2e_keep_old` 的八個組合我實跑過,修後版本都符合註解的規則,修前版本沒有這個函式:
    - 這次沒過一律蓋掉。
    - 既有那筆完整且判完,而這次沒判完或不完整的通過,則留舊的。
    - 既有那筆完整的失敗,不會被不完整的通過蓋掉。
    - 一個疑點:規則裡拿掉了修前版本的 `old.commit == head` 條件。紀錄本來就綁指紋,所以這是設計取捨,我沒有找到可利用的路徑。

## 三問
1. 原問題的修復效果:
   - 方法名含 `$` 的情況,修前 `E2E_BENCH_NAME_RE.fullmatch("$HOME")` 為 True、`_e2e_case_bench_err` 對 `Outer$Inner#test` 回 None。
   - 修後這兩個都被擋,且訊息說明原因。
   - `feature_runs` 的覆蓋規則,修後才有明確的函式(修前版本沒有 `_e2e_keep_old`)。
   - 載入版本確認方式:兩版都從 `git show` 取出後用 `importlib` 載入,並印出 `__file__`。
   - 未驗:`run.sh` 的整體流程沒實跑。
2. 修補處的正常、錯誤與相鄰呼叫路徑:
   - 正常方法名(`ok.Class#m`、`A.b#c`)修前修後都通過,`#` 在字中間時 `sh` 不當註解。
   - `lumos` 與 `run.sh` 兩邊規則一致,相鄰的記憶體情境名與 run-id 檢查沒有變動。
   - `_e2e_changed_files` 現在 git 讀不到就回錯誤。我只讀了程式,沒有實跑。
3. 新發現的同一案例,修前修後:S1 修前與修後結果相同,歸因是原有漏查。

## 未驗範圍
- `run.sh` 的完整實跑(需要裝置與 Maestro)。
- 讀 `_e2e_changed_files` 的 git 失敗分支,沒有實際製造失敗。
- `history` 指令會印帳本裡的字串(終端控制字元),我判斷攻擊面不在三類範圍內,沒有展開。

臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/資安-sonnet` 已刪除。

這輪修補確實擋住了 `$` 進 `sh -c` 的洞,我只找到一條與修補無關、原本就有的縱深防禦類發現。
