severity: minor

我只讀了乙區的程式與測試部分(`qo_ablation.py`、`test_autonomous_loop.py`、兩份評分員原始輸出的路徑遮蔽)。技能文件和知識筆記的 hunk 沒逐條審,不列入結論。

**Finding 1:同一族的欄位型別洞只補了一半。`calls` 的元素形狀不對,`score` 照樣崩潰,而且該場被判為有效。**

severity: minor
blocking: 否
歸因:有證據的原有漏查(修前修後行為相同,不是這次修補引入的)
引句:「型別錯照列成無效場,計分不崩(代碼審 r3)」

- 這行註解宣稱型別錯的檔案一律列成無效場、計分不崩。實際上只有 `answer` 和 `answer_len` 做了型別防護。
- `_valid` 只檢查 `calls` 是清單,不檢查每個元素。`_load_runs` 的 `tuple(c) for c in calls` 對任何 list 都放行。
- `code_start` 的 `for name, summ in calls` 遇到長度不是 2 的元素,或 `summ` 不是字串,就會崩。
- 重現:臨時目錄,結果檔為 `{"results":[{"answer":"x","answer_len":1,"calls":X}]}`,執行 `python3 qo_ablation.py score --out-dir w/out --gold w/gold.json --dest w/s.json`。

| `calls` 內容 | 修前(46bc93c3) | 修後(b187b5e9) |
|---|---|---|
| `[["Bash"]]` | rc=1,ValueError: not enough values to unpack | rc=1,同上 |
| `[["Bash",5]]` | rc=1,TypeError | rc=1,同上 |
| `[["Bash",["x"]]]` | rc=1,TypeError | rc=1,同上 |
| `[["Write",null]]` | rc=0 | rc=0 |

- 這幾個檔案的 `valid` 都是 true,所以不是「列成無效場」,而是整批 `score` 算不出來。
- 對一份已跑完、只用來重算的實驗,實際影響很小。
- 建議在 `_load_runs` 過濾 `calls`:只收長度為 2、`str` 加 `str` 或 `None` 的元素;或在 `_valid` 一併檢查。

**三問的回答**

1. 原問題的修復效果:已修復,有行為證據。同一份輸入在修前、修後各跑一次(`python3 <qo_ablation.py> ...`,臨時目錄):

| 輸入 | 修前 | 修後 |
|---|---|---|
| `answer:null` | `score` rc=1 | rc=0 |
| `answer_len:"3"`(answer 為 "abc") | rc=1 | rc=0 |
| `answer:5` | rc=1 | rc=0 |
| `packets --batch 0` | rc=1,舊的 `packet-01.json` 被刪光 | rc=2,舊包保留 |

   測試 `test_score_survives_wrong_field_types` 和 `test_packets_bad_batch_keeps_old_packets` 用的正是這幾筆輸入。因為這些輸入在修前就讓 `score`/`packets` 崩潰或清掉舊包,拿掉實作會翻紅,測試有抓錯力。
   這兩個測試我沒有直接跑,只是照同一份輸入手動比對兩版得到上面的結果。
2. 修補處的正常與相鄰路徑:成立。
   - 正常場(`answer` 為字串、`answer_len` 等於長度)的 `valid` 仍為 true,`score` rc=0。
   - `--batch` 為正整數時,舊包只清 `packet-*.json`,沿用既有測試 `只清自己產的包`(我沒另外執行)。
   - 負數 `--batch` 的行為我沒單獨實跑,只確認程式碼用同一個 `a.batch < 1` 判斷會擋下。
3. 同一案例在兩版:見 Finding 1 的表,兩版相同,屬原有漏查,不是修補造成的回歸。

**路徑遮蔽(評分員原始輸出)**:在修後版本用 `git grep` 搜 `claude-501` 和 `/Users/enzo`,在 `governance/eval/qo-ablation-2026-10` 底下沒有命中,遮蔽沒有殘留。

**固定席節點**:這次改動沒有碰 `scripts/lumos` 的任何行為,也沒有碰 `bound-tests-gate`、`guard-kill`、`lumos-cli-*`、授權、`design-loop` 這些合約節點宣稱的行為。乙區只動計分器、一個測試檔、文件與卷證,所以這些節點判為不影響。

**未驗範圍**:`gold` 缺少場景鍵時 `_regex_row` 會 KeyError,`must_surface` 為空時會除以零。這兩項由預先登記的 gold 檔控制,不在本席範圍,沒有深究。`cmd_packets` 寫包與寫對照表不是原子操作,寫到一半崩潰會留下有包無對照表的狀態,我沒有構造出具體觸發輸入,所以不標 finding。

總結:最嚴重 minor;blocking 共 0 條。
