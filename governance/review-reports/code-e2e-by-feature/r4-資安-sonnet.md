severity: minor

## S1 本機檢測總表只擋最後一層捷徑,`.lumos/artifacts` 是捷徑時仍寫到專案外
severity: minor
blocking: 否

- 歸因:有證據的原有漏查。這不是修復造成的回歸,修前修後結果相同。第三輪只替查證紀錄補了捷徑檢查(`_e2e_record_update`),同一類的總表寫入沒一起掃。
- 攻擊路徑:
  - 誰:陌生專案的作者,在專案裡提交一個捷徑 `.lumos/artifacts`,指向使用者家目錄裡的某個目錄。
  - 從哪裡:使用者在這個專案跑 `lumos android-e2e judge --history`,或跑範本腳本。
  - 送什麼:捷徑本身。
  - 拿到什麼:在專案外的目錄建出 `android/history.jsonl`,或往已有的同名檔追加一行 JSON。
- 影響很窄:只能寫固定檔名,內容是檢測摘要,蓋不掉別的檔。範本腳本本來就會執行專案設定裡的 `build`,所以走腳本那條路沒有新增能力。真正多出來的是只跑 `judge` 的那條路。
- file: `scripts/lumos:41148`(`_e2e_history_append`)
- 引句:「ok = _local_ledger_append(p, ("\n" if _ledger_tail_needs_newline(p) else "") + text)」
- 修前修後證據(同一案例,兩版都用同一支程式載入 `scripts/lumos`,用 `SourceFileLoader` 確認載入路徑):
  - 案例:`.lumos/artifacts` 指向專案外的 outside 目錄,呼叫 `_e2e_history_append`。
  - 修前 4b056532:outside 底下出現 `android/history.jsonl`。
  - 修後 7988107c:同樣出現 `android/history.jsonl`。
  - 對照 C:`history.jsonl` 本身是捷徑時,兩版都沒寫進被指向的檔(victim 內容不變),這層擋得住。

## S2 run-id 擋 `history.jsonl` 是字串全等比對
severity: minor
blocking: 否

- 歸因:未判定。我沒有實際跑範本腳本,這條是從程式比對方式推出來的。
- 推論的攻擊路徑:macOS 預設檔案系統不分大小寫,`History.jsonl` 這種寫法過得了這道守衛。它和本機總表同名,結果是總表寫不進去,或 run 目錄建不起來。
- 攻擊路徑的「誰」和「送什麼」要使用者自己刻意打這個名字,不是順手操作會碰到的,所以只標推論。
- file: `scripts/templates/android-e2e-run.sh:preflight`
- 引句:「if run_id == "history.jsonl":   # 本機總表 .lumos/artifacts/android/history.jsonl 跟 run 目錄在同一層」

## 三類逐項結論

- **①提示注入**:已看,無。
  - 改動沒有把外來自由文字拼進給 AI 的派工詞或 hook 附加段。
  - 效能方法名和情境名都先過白名單,再進指令或路徑。我用十五種輸入跑過:`$`、`;`、空白、換行、`-` 開頭、全形數字都被擋;`#` 只收在中間。
- **②讀寫與執行越界**:已看,有 S1 和 S2。
  - 查證紀錄捷徑檢查:修前,`.lumos/e2e-records` 是捷徑時,紀錄檔寫進專案外的 outside 目錄(輸出裡看得到 `outside/aaaa….json`)。修後回「是捷徑,不跟過去寫」,outside 沒東西。**已修復**,同一案例兩版對比。
  - `macrobench_cmd`、`build` 和 `stability_scenarios.driver` 交給 `sh -c`:這是專案設定自己的指令,本來就由使用者跑腳本時執行。方法名已擋 shell 字元,沒有新增注入面。
  - `features.paths` 改共用 `_e2e_relpath_err`:`app//src`、`app/*.kt`、`a*` 修前通過、修後被擋;`app\src` 和 `..` 兩版都擋。
  - 新增的程式、範本、文件沒有密鑰、信箱、下載網址。
- **③非刻意、一步就繞過的守衛**:已看,無新增。
  - 殘留的 `LUMOS_E2E_COLLECT`:`collector_override` 搬到「真的要收記憶體時才標」之後,仍是失敗往安全那邊走,只是不寫查證紀錄,不會被記成驗過。
  - 殘留的 `LUMOS_STABILITY_SCENARIO`:整套跑時被拿掉,不會混進段本身的結果。
  - 逾時後的 `break`:沒跑到的記憶體情境,判定結果是 unjudged,兩版都一樣(我用缺步驟的 steps 驗過)。
  - 按功能跑寫進查證紀錄:開跑時和現在都要乾淨、HEAD 沒換,才會寫;替身收集腳本時不寫。沒驗完整的版本不會被記成驗過。

## 回答三問

1. **原問題的修復效果**:
   - 紀錄寫到專案外:修前寫出去,修後擋下(證據在上面)。
   - 路徑寫法:`app//src`、萬用字元修前收、修後擋。
   - 其餘修復項(寫不進去的處理、逾時後不再往下跑、按功能跑被擋時補寫總表)我只看了程式,沒跑出行為證據,標未判定。
2. **修補處的正常、錯誤與相鄰路徑**:
   - 正常路徑:`pkg.A#b`、`./a`、`app/` 修前修後都過。
   - 相鄰路徑:總表經 `.lumos/artifacts` 捷徑寫到專案外,修前修後都在(S1)。
3. **新發現同一案例的前後結果**:S1 兩版相同,所以不是回歸。S2 沒跑,未判定。

**沒驗到的範圍**:
- 沒接真機或 Maestro,範本腳本整體沒有端到端執行。
- 測試檔的紅綠沒重跑,只看了差異。
- `driver` 和 `build` 的內容視為專案自己的指令,沒有逐條審。

臨時目錄 `/tmp/lumos-seat-work/code-e2e-by-feature/資安-sonnet` 已刪。

這次修補沒有新增的可利用洞,只有一個同類的原有漏查(S1)和一個推論(S2)。
