severity: minor

**hook 固定席段**:派工詞尾端有附上。我把 guard-kill、lumos-cli-read、bound-tests-gate、測試假綠形態、design-loop、lumos-cli-lifecycle 的合約行逐條對了這份修補差異。

## 固定席逐條判

- **guard-kill 的 rc 優先序**:不影響。差異只改 `_kill_merge_iter` 例外分支記的原因字串、斷路器常數和 run 事件的 merge_off 篩選。`cmd_guard_kill` 的 rc 計算沒動。
- **guard-kill 的 `--json` 純度**:不影響。新增和改動的輸出都走 `_kill_merge_off(quiet=True)`,這條路徑不印字,也沒新增 stdout。
- **lumos-cli-read、lifecycle、design-loop、測試假綠形態、bound-tests-gate**:不影響。差異沒碰 search 濾網、re-inject、處置閘、bound-tests 閘。
- **測試假綠形態**:補的 e1 測試有前置斷言。它檢查 `mg.interrupted is False`,也檢查 plats 確實是 `時限到`,不是只看有沒有印字。
- **表態記錄**:「同步命令列、無並行」這句我沒找到反證。

## 修補鏡頭三問

1. **原問題修好了嗎?** 修好了。原問題是量基準途中總時限用完時,不論原因一律記「中斷」。
   - claim:總時限到記 `時限到`,收到訊號記 `中斷`。
   - input:單支基準 2 秒、3 秒後 `should_stop` 轉真,沒有訊號。
   - expected:`mg.plats == {kotlin-junit: (False, 時限到)}`,`mg.interrupted` 為 False,不印「這次不合併」,run 的 `interrupted` 為假。
   - case_source:`t_choice_kill_merge_off_reasons` 新增的 e1 兩條斷言。
   - before:修前 `_kill_merge_iter` 在 `except _KillHalt` 裡無條件寫 `中斷`(`r3-repair.patch` 第 238 行),所以這個輸入記成「中斷」。
   - after:我在修後版本跑,17 條斷言全綠。
   - comparison:我把修後程式改回無條件 `"中斷"`,e1 那兩條立刻紅(`{'kotlin-junit': (False, '中斷')} False`),另 15 條仍綠。這個測試抓得到這個改壞。反向改壞(永遠記 `時限到`)會被既有的訊號案擋住(`scripts/test_lumos.py:146772` 斷言 `merge_off == {"kotlin-junit": "中斷"}`)。
   - 我只替換了條件式,沒有另外把整個 `except` 分支拿掉再跑。
   - 歸因:有證據的修復。

2. **兩種停法會不會都不成立或判反?**
   - 訊號到達時,`_on`(`scripts/lumos:77141`)先 `st.got.append`,再同步呼叫 `st.on_first`(`mg.on_signal`),把 `mg.interrupted` 設真。
   - Python 的訊號處理在主執行緒的 bytecode 邊界跑完整個處理函式才回主流程,所以 `stop()`(`scripts/lumos:79064`)不會看到「`st.got` 有值但 `mg.interrupted` 還是假」的中間狀態。
   - `_kill_merge_base` 裡的 `_KillHalt` 有兩個來源。一是 `hk.between()` 看 `should_stop`(訊號或時限)。二是 `mg.interrupted` 為真時主動丟(`scripts/lumos:29006`)。後者必記中斷,前者依 `mg.interrupted` 分流,沒有判反的輸入。
   - 訊號和時限同時成立時,`mg.interrupted` 為真,記「中斷」,合理。
   - 一個已知的小縫在下面的 finding。

3. **衍生資料:merge_off 排除斷路器用常數。**
   - `_CHOICE_MERGE_TRIPPED` 在寫入處(`scripts/lumos:29095`)和篩選處(`scripts/lumos:79113`)是同一個常數,兩處不會因字串改動而漂移。
   - 斷路器記的是 `(False, "斷路器")`,不會誤進 merge_off。
   - 時限到記的是 `(False, "時限到")`,會進 merge_off,符合計劃寫的 S10。

## Preserve 案例

- **claim**:斷路器和 merge_off 篩選的行為不變,只是字串抽成常數。
- **input**:沿用 S4 / S10 的既有案例。
- **expected**:跳開行印「最後一次」、merge_off 沒有斷路器那筆。
- **before / after**:修前是字面 `"斷路器"`,修後是同值常數。
- **comparison**:`t_choice_kill_merge_off_reasons` 17 條斷言全綠。S4 的 `t_choice_kill_merge_unclean_reasons` 我沒跑,所以這條 preserve 只驗到 S10 那半。
- 歸因:未判定(S4 那半沒跑)。

## Finding

引句:「st.on_first = self.merge.on_signal   # 第一個訊號當場收掉合併快篩與合併基準(〈做法〉4)」

file: `scripts/lumos:79080-79084`。`on_first` 是在 `_situation_rule_signals` 的 context 建好(訊號處理函式已安裝)之後才設。

- 失敗輸入:訊號剛好落在 handler 安裝完、`st.on_first = ...` 賦值之前。
- 走到的地方:這時 `st.got` 有值但 `mg.interrupted` 為 False。之後 `_kill_merge_base` 丟 `_KillHalt`,`except` 分支記成 `時限到`,而 run 的 `interrupted` 為真。
- 這個縫隙只有幾條 bytecode 寬,不影響判定結果,只影響 merge_off 的原因標籤。
- 我沒做出重現,只是讀碼推得,所以標 ⚠ 未能重現。
- 這一條不是修補引入的:修前是「一律記中斷」,這個縫隙在修前會剛好記對。所以嚴格說,它是修補把標籤改成依賴 `mg.interrupted` 之後才出現的邊角。
- 歸因:未判定。

severity: minor
blocking: 否。只影響診斷用的原因標籤,不影響判定、帳或 rc,也無法穩定重現。

## 已驗與未驗範圍

- **已驗**:新 e1 測試通過、改壞會紅。signal 與 deadline 兩條路的歸屬分流成立。常數兩處一致。`scripts/lumos` 與 `scripts/test_lumos.py` 在 `28543fb` 與目前 HEAD 之間沒有差異,所以我跑的就是被審版本。
- **未驗**:
  - 沒跑 S4 的 `t_choice_kill_merge_unclean_reasons`。
  - 沒實跑修前版本的 e1 輸入(修前行為是讀碼推得)。
  - e1 測試靠真實睡眠和 3 秒卡線,我只跑了一次,沒做壓力下的穩定性測試。邏輯上不管卡在哪一支都會停,所以穩定性風險看起來低。
  - 修補差異的文件 hunk(計劃與 guard-kill 筆記)只做了文字一致性檢查,沒逐條對程式。

總結:最高嚴重度 minor,blocking 0 條。
