severity: major

審查範圍:修補差異 69ee6d76 到 5248791e,以測試那半為主,主程式只追被測試碰到的呼叫端。我在臨時複本上做了 20 個改壞實驗(改壞後跑 `-k` 子集),沒碰 web-ledger 工作樹。

## 發現

**1. `_jsonl_append_verified` 的讀回自驗改用 `splitlines()`,帳寫成功卻回報「落盤自驗失敗」rc2**
severity: major
- blocking: 是
- 歸因:有證據的修復回歸。
- 問題:修補把讀回自驗從 `for line in f` 改成 `tail.splitlines()`。`json.dumps(ensure_ascii=False)` 不跳脫 U+2028、U+2029、U+0085。`splitlines()` 會在這些字元處切開一列,切開後每段都解析失敗。自驗找不到那筆,於是對已經寫進帳的記錄報「系統說寫成功了,但讀回來找不到這一筆,這筆不算記成功」並回 rc2。
- 為什麼要在意:repo 已有 `_ledger_lines` 專管帳檔切行,原註解寫明就是為了擋 `splitlines` 劈開同一列。回 rc2 會誘使人重記,帳本只能追加,結果是重複列。
- 具體例:`lumos --vault docs/x-knowledge canary record none --loop prose-a --note $'前\u2028後'`
  - 修前版(69ee6d76):印「記下來了」,rc=0。
  - 修後版(5248791e):帳裡有該列,印「落盤自驗失敗」,rc=2。
- 測試缺口:`t_cap_retro_r3_ledger_lines_everywhere` 的原始碼掃描只比對 `...read_text(...).splitlines()` 這種寫法,抓不到 `tail.splitlines()`。新測試 S34 到 S44 都沒有含這幾個字元的 note。
- 建議:改走 `_ledger_lines(tail)`,並補一條 `--note` 含 U+2028 的記帳測試。
- 引句:「        for line in tail.splitlines():」

**2. `--regression-set` 帳壞分支沒有任何測試守著**
severity: minor
- blocking: 否
- 歸因:未判定(新增的分支,沒有修前對應版本)。
- 實驗:把 `if _lread()[1] is not None:` 那段整段拿掉,`-k canary_record` 的 145 條測試仍全綠。S41 只在帳健康時數讀帳次數。
- 具體例:帳本含 `\xff`,執行 `canary record none --loop code-q --round r1 --tier standard --findings-set a1 --folded-set a1 --refuted-set none --regression-set a1`。
  - 有這個分支:印「審查帳讀不懂…整本判不了」。
  - 拿掉後:印「這是這個迴圈的第一輪,沒有『上一輪修補』;--regression-set 只能寫 none」,診斷錯誤,而且它導向的修法會繞過真正的帳壞。
- 引句:「                if _lread()[1] is not None:」

**3. S43 擋不住 `--orchestrator` 帳壞分支被拿掉**
severity: minor
- blocking: 否
- 歸因:未判定。
- 實驗:拿掉該分支後,`-k orchestrator_bad` 與 `-k canary_record` 全綠。帳壞時 `_recs` 是 `[]`,後面的輪次規則(`_round_format_write_block`)印同一句「審查帳讀不懂」並回 rc2。
- 結論:`--orchestrator` 這一段對任何非結局帳的呼叫都是多餘的,S43 無法證明它存在的理由。要嘛刪掉,要嘛讓測試能分辨(例如帶 `--outcome` 的情形)。
- 引句:「            if _rerr is not None:   # 帳壞:跟輪次規則同一句」

**4. 「寫入後只讀回新寫的那段」沒有測試**
severity: minor
- blocking: 否
- 歸因:未判定。
- 實驗:S41 的計數器只算 `_canary_ledger_rows` 與 `Path.read_text`。自驗用 `open(..., "rb")`,不在計數裡。把 `start` 改成 0 讓它整本重讀,測試照綠。計劃宣稱的資源節省沒被機械守住。
- 引句:「            fb.seek(start)」

## 通過檢查的部分(改壞實驗全部翻紅)
- **結局帳過濾四個入口**:拿掉任一處過濾,對應測試都紅。
  - `_canary_ledger_scan`:S15、S37、S14 紅。
  - `_loop_status_read`:S35、S36、S14 紅。
  - replay 讀帳:S38 紅。
  - `_spec_gate_ledger_index`:S39 紅。
- **結局帳不受留痕限制**:拿掉 `outcome is None`,S36 前置紅。
- **none 保留字**:拿掉 refuted 檢查,S40 第 4 案紅(原因是改走別的擋下訊息);findings 的大小寫比對改成精確比對,S40 的 NONE 案紅;folded 並列檢查拿掉,S18 紅。
- **讀帳次數**:停用快取,S41 四條紅。
- **帳尾換行**:拿掉補換行,S44 紅。
- **指令編號 quote**:改回截斷或不清控制字元,S42 紅。
- **一個壞列毒到所有編號**:S33 與 S17 都紅。
- **測試名稱**:新增的 11 支測試名不互為前綴,也沒有重名。

## 三問
1. **原問題的修復效果**:有行為證據。讀帳入口濾結局帳、none 保留字、每次記帳只讀一次帳、帳尾補換行、指令編號 quote 這幾項,拿掉實作都有測試翻紅(實驗見上)。
2. **修補處的相鄰路徑**:`_jsonl_append_verified` 的新切行方式在含 U+2028 的記錄上壞掉,見發現 1。其餘相鄰路徑(`loop next`、`--panel`、處置閘、跑滿提示、replay、規格閘一族)經過上面的實驗後成立。
3. **新發現在修前、修後各自的結果**:只有發現 1 跑了兩版,修前 rc0、修後 rc2。發現 2、3、4 只做了修後版的拿掉實驗,修前版不適用,標未判定。

## 未驗範圍與備註
- **未驗**:
  - 凍結過的舊 golden 檔若含結局帳列,回放會不會變成混用 rc2。這只可能出在本分支這個時間窗內,我沒造例。
  - 其他讀審查帳的函式(`_escape_review_rows_by_loop`、行 13737)不濾結局帳,只影響逃逸分類,我沒找到具體失敗輸入。
- **環境限制**:複本沒有 `.github`、`governance` 等 repo 檔案,所以 `-k regression` 與 `-k cap_retro` 的實驗輸出裡有幾條與改動無關的 EXCEPTION,我沒有拿它們下結論。
- **暫存**:我建的臨時目錄 `/tmp/lumos-seat-work/code-記帳與迴圈工具小修/通才-sonnet` 已刪除,刪前確認沒有程序開著。

最嚴重 severity:major;blocking 共 1 條(發現 1)。
