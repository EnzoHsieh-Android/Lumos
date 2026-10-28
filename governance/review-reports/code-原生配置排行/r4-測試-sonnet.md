severity: minor

先交代前置。派工詞指的鎖檔 `.warming` 不存在,所以沒有鎖要處理。固定席筆記沒有附上:機器附加段寫明這次沒附固定席節點,所以圖譜鏡頭沒有逐條可答的項目。基準全跑 `python3.14 scripts/test_lumos.py -k android_native` 是 217 條全綠。

**1. NATIVE_TAIL 改成從 STOP_WAIT 組出來,STOP_WAIT 設成 nan 會讓「時間不夠」的守衛整個失效**
severity: minor
blocking: 否。只有測試縮短用的環境變數 `LUMOS_STABILITY_STOP_TIMEOUT` 被設成 nan 才會觸發,一般使用不會碰到,所以是 minor。
引句:「NATIVE_TAIL = STOP_WAIT + T_SHORT + NATIVE_QUERY_S」
file: `scripts/templates/android-stability-collect.sh:28`、`:36`、`:585`、`:673-679`
歸因:有證據的修復回歸。
- 兩版查證:在副本把 `t_android_native_collect_budget` 的 121 秒那組環境加上 `LUMOS_STABILITY_STOP_TIMEOUT=nan`,修前和修後各跑一次。
  - 修前(223de76d):5 passed,守衛照擋。
  - 修後(f58ae189):該組斷言紅,第二段照跑,結果是 `status: ok`,「時間不夠」沒出現。
- 失敗場景:
  - STOP_WAIT 是 nan 時 NATIVE_TAIL 也是 nan。
  - `2*elapsed + NATIVE_TAIL > remaining` 因此永遠是 False,預估的守衛就當沒有。
  - `left()` 裡 `min(T_LONG, nan)` 回 T_LONG,驅動不再被步驟上限限制。
  - 同一個檔的 `LUMOS_STABILITY_STEP_BUDGET_S` 已經用 `math.isfinite` 擋 nan,STOP_WAIT 沒擋,修補新增了這個耦合。
- STOP_WAIT 是 inf 時預估永遠不夠,第二段永遠不跑,這是另一個方向的同類問題。
- 測試沒有蓋到這個:測試只驗 `NATIVE_TAIL == STOP_WAIT + T_SHORT + NATIVE_QUERY_S` 這條等式,拿實作公式驗實作公式。
- 單人、測試縮短用的旋鈕,不給修法。

**2. 測試說明文字還寫著舊的「120 秒」**
severity: minor
blocking: 否。只有說明文字與實作不一致,沒有行為錯。
引句:「S23:有設 LUMOS_STABILITY_STEP_BUDGET_S、開跑到現在的秒數加第二段預估(第一段的兩倍加 120 秒)超過它」
file: `scripts/test_lumos.py:18860`(`t_android_native_collect_budget` 的 docstring)、`scripts/test_lumos.py:18970` 附近(`t_android_native_budget_rule` 的 docstring,寫「NATIVE_TAIL(120 秒)」)
歸因:有證據的修復回歸。原本 120 是對的,這次修補把 NATIVE_TAIL 改成預設 180 秒,卻沒改這兩段說明。
失敗場景:讀測試的人照 docstring 算預估會算成 2×第一段+120,與實作的 2×第一段+180 差 60 秒。

**3. 中斷訊息新增的 `perfetto-configs/` 與「只刪 lumos-stability- 與 lumos-native- 開頭的」沒有任何斷言**
severity: minor
blocking: 否。只是訊息文字沒被守住,規格 S1–S29 裡沒有哪條要求這段字。
引句:「只刪 lumos-stability- 與 lumos-native- 開頭的)")   # 照實寫(代碼審 r4 資安席)」
file: `scripts/templates/android-stability-collect.sh:696-699`
歸因:有證據的修復回歸。這是這次新增的字。
- 改壞:把整段提示換回只有 `/data/misc/perfetto-traces/ 看過再刪` 的舊字,`-k android_native` 217 passed, 0 failed,照綠。
- 唯一碰到「裝置沒回應」訊息的測試只斷言 `"可能還在" in err` 與 `"暫存已刪" not in err`。
- 失敗場景:有人改回舊字,使用者照訊息只列 traces 目錄,漏掉 configs 目錄裡的 `lumos-native-*.pbtxt`。

**4. native_skip 的「時間不夠」原因多出來的「第二段預估要 X 秒」沒被斷言**
severity: minor
blocking: 否。內容是診斷用字,測試已守住小數一位與不印負數。
引句:「時間不夠,不跑第二段(第一段 {elapsed:.1f} 秒,這一步只剩 {max(remaining, 0):.1f} 秒,第二段預估要 {2 * elapsed + NATIVE_TAIL:.1f} 秒)」
file: `scripts/templates/android-stability-collect.sh:586`
歸因:有證據的修復回歸。這是新增的字。
- 改壞:拿掉 `,第二段預估要 … 秒` 這段,`-k android_native_budget_rule` 12 passed, 0 failed。
- 失敗場景:預估值被寫成別的算式(例如漏掉 `2 *`),使用者看到的預估與實際用來判斷的不一致,測試不會紅。

**三問**
- 原問題修復效果的行為證據:
  - 改壞 `NATIVE_QUERY_S = 0` 後,`t_android_native_collect_budget` 紅(175 秒那組預估放行,第二段 ok,斷言要的是驅動被砍)。
  - 邊界「剛好等於預估照跑」與「少 0.1 秒不跑」有被 `t_android_native_budget_rule` 守住。
  - 負數被 `max(remaining, 0)` 擋掉。
  - `_macrobench_native_retained` 的六鍵重組,有「多塞鍵」與函式名、.so 名、呼叫者的控制字元兩條斷言守。
- 正常、錯誤與相鄰路徑:
  - 新整段測試 `t_android_native_stop_interrupted` 守住 `del state["rec"]` 的位置:把 `stop_record` 之前先 `state.pop("rec")` 就紅(`cleanup 再停一次第二段的錄製` 實得 2,要 3 以上)。
  - 時序判讀:假 adb 的 `kill -TERM` 每次卡 3 秒。前置斷言要 `kill -TERM 4321` 恰好 2 次,且 log 含 `lumos-native-run1`,證明中斷落在第二段停錄。
  - 這個測試變不穩只會變紅、不會誤綠:極慢的機器若在 3 秒窗口外才送 SIGTERM,是紅。
  - 測試沒有改全域狀態:環境變數只放在傳給子程序的 dict,暫存都在 `tempfile` 裡。
  - 它沒有像其他整段測試那樣呼叫 `_ms_orphans` 做孤兒檢查,但此時驅動已結束,找不到具體失敗場景,不標。
- 新發現同一案例的修前、修後結果:見 finding 1,修前守衛成立,修後 nan 失效。

最嚴重等級見檔首,會擋推送的共 0 條。

實驗副本與工具腳本已用字面絕對路徑刪除。
