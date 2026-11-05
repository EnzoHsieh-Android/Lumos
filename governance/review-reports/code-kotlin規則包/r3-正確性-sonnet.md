severity: minor

我在臨時目錄的複本上,對這輪 check.py 的每道新檢查各改壞一次,再跑相關三組測試:`kotlin_rulepack_samples`、`kotlin_catalog_rows_wired`、`kotlin_rulepack_messages`。沒有會做出錯行為的問題,也沒有 r2 修補本身的洞。改壞後測試照綠的有兩個:「(無)」那組是死碼加空洞測試,files 區塊新讀法完全沒測試。實驗完臨時目錄已刪,repo 工作樹沒動。

### 改壞實驗結果

| 改壞 | 結果 |
|---|---|
| 去掉 `rule_id in review_ids`(review-fp 豁免不限覆核級) | 紅 |
| `good_cases` 不再跳過 review-fp 檔 | 紅 |
| `scan` 不守逾時旗標 | 紅(用了 10.5 秒) |
| files 區塊讀法還原成舊式 `(?=^\S)` | 照綠 |
| 去掉 `owner == rule_id` | 照綠 |
| `loaded_count` 不守逾時旗標 | 照綠 |
| `scan` 逾時時不設旗標 | 照綠 |
| `check()` 開頭不重設旗標 | 照綠 |
| 缺〈來源縮寫〉不早退 | 照綠 |
| 半形「(無)」不認 | 照綠 |
| 全形「(無)」不認 | 照綠 |

照綠的各條分述如下。

severity: minor
blocking: 否

**「(無)」那段判斷是死碼,新增的「不報」測試翻不紅(正3 的修補沒有實際效果)**
引句:「        if c[4].strip() in ("(無)", "\uff08無\uff09"):」
`catalog_problems` 裡,「(無)」被當一般觸發字解析,`trig` 本來就非空。它既不會觸發「不准空」,也不在停用字表,所以設成 `[]` 與否輸出完全相同。我把半形、全形各拿掉一邊都全綠。「觸發字寫「(無)」是刻意不設,不報」這條斷言在沒有這個分支時也過。`scripts/lumos` 目前沒有任何地方讀決策表觸發字,所以分支沒有可觀察的後果。「觸發字空白要報」那條倒是有效。建議等第二、三批真的消費觸發字時,再讓測試斷言解析結果是空清單。在那之前,要嘛承認這是預留位置,要嘛讓 `catalog_problems` 對「(無)」產生可驗的輸出。

severity: minor
blocking: 否

**files 區塊新讀法沒有任何測試,還有個小退步**
引句:「+    m = re.search(r"^files:(.*?)(?=^[A-Za-z_\"'][^\n]*:)", doc + "\nzz:", re.M | re.S)」
- **沒測試**:改回舊式後全綠。現有 207 條規則兩種讀法的 test_only 分類完全一致,所以修補是對的,只是沒被鎖住。
- **正向修好**:頂格 `- '**/src/test/**'` 清單,舊式判成 False,新式判成 True。
- **小退步**:頂格註解現在算進區塊。下面這個最小重現,舊式判 True,新式判 False,祖先目錄檢查就悄悄略過這條規則:
  ```
  id: x
  files:
    - '**/src/test/**'
  # 不掃 src/main
  rule:
    pattern: a
  ```
- 建議:判斷前先去掉 `#` 開頭的行,並補兩條改壞測試,一條頂格清單、一條頂格註解帶 `src/main`。

severity: minor
blocking: 否

**缺〈來源縮寫〉節的早退沒有測試**
引句:「+        return [("<catalog>", "找不到〈來源縮寫〉節(來源欄的縮寫要對照它)")]」
拿掉這個早退整組測試全綠。補法:`t_kotlin_catalog_rows_wired` 的型錄複本裡刪掉該節,斷言有這句訊息。注意早退會只回這一條,把其他型錄問題都蓋住,建議在訊息或測試裡註明這是刻意的。

severity: minor
blocking: 否

**逾時測試只鎖到「`loaded_count` 先逾時」這一條路,門檻也太鬆**
引句:「+    check("逾時一次之後不再逐次等滿(整次在 4 秒內)", took < 4, f"{took:.1f}s")」
- 測試用的假 `sg` 一律睡 5 秒,所以第一個逾時的永遠是 `loaded_count`。`scan` 自己設旗標那行(照綠)與 `loaded_count` 的守衛(照綠)都沒被獨立驗到。
- `SCAN_TIMEOUT=1` 時,守衛正確約 1 秒;少了 `loaded_count` 守衛約 3 秒,仍小於 4 秒。
- 建議:再補一個假 `sg`,遇到 `--inspect` 立刻成功、遇到 `--json=stream` 才睡。同時把門檻收緊到約 2.5 秒。

severity: minor
blocking: 否

**`owner == rule_id` 是多餘條件,r2 想鎖的跨規則好例命中其實沒人看**
引句:「+                if kind == "good" and owner == rule_id and Path(f).name.startswith(REVIEW_FP_PREFIX) and rule_id in review_ids:」
- 後面只讀 `hits[("good", rid, rid)]`。`owner != rule_id` 的命中本來就不會被報,所以拿掉這個條件行為完全一樣(照綠)。
- 順帶一個舊有的洞:放在 `good/A/` 的檔案若觸發別條會擋的規則 B,沒有任何檢查會報,因為只讀自己目錄的命中。
- 建議:要嘛刪掉這個條件,要嘛新增「好例目錄裡的命中屬於別條規則」的檢查,再補測試。

severity: minor
blocking: 否

**註解錯位,留在 `SCAN_TIMEOUT` 那行**
引句:「SCAN_TIMEOUT = 120     # 一次掃描的上限(秒);正常不到一秒,卡住時不要拖到外層測試逾時          # 新增告警閘解析 SARIF 時把訊息截在 120 字」
那段 SARIF 註解是 `MSG_MAX = 120` 的,現在 `MSG_MAX` 沒有註解。這行是 diff 的上下文,不是這輪新改的。

其餘 hunk 逐項走過,行為都正確:
- `.lumos/config.json` 的 `node_home.ignore` 收窄到 `*.kt` 與 `*.kts`:`samples/` 全是 `.kt`,深層路徑也命中,「每支檔有家略過規則包樣本」測試綠。
- `_ktpack_sg` 本機沒有 `ast-grep` 時改回 None:兩個呼叫端都處理了,先跑靜態那半再印沒驗到。
- `shlex.quote` 在包裝腳本與 `cmd` 都用對。

這輪沒有發現會做出錯行為的問題,只有測試防線的缺口和一個小退步,都不擋推送。
