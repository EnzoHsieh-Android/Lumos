severity: major

我照〈回退〉節走了一遍,發現 4 條問題。實驗放在我自己的暫存目錄,現已刪除。

走法如下。我用現行(舊判準)程式跑 `quote-check`,模擬還原後的行為。我也讀了 `cmd_loop_replay` 的凍結與回放兩段、`_loop_status_disposal`,以及每週自動凍結與回放的 `replay_weekly.py`。

已讀,無 finding 的部分:
- 現存 305 份 `governance/replay/*/verdict.json` 的 `engine_rev` 全是 `d5-2026-08-25`,且全在切換日前凍結。上線前與還原後對它們都沒有影響。
- 我在 `scripts/lumos`、hooks、`scripts/*.sh` 裡找不到 pre-push 或 CI 去呼叫 replay 的地方。replay 只由每週自動腳本和人手動呼叫,所以「改切換日」和推送閘不會互卡。
- 代碼審留痕綁分支 sha,design-loop 處置閘是另一條路。不過改常數那個提交要不要出 `tier: high` 沒法預先判,⚠ 取決於 `lumos pitfalls` 實算。

1. 還原後,上線期間凍結的 golden 會變「邏輯漂移」紅燈,不是「制度演進」
severity: major
blocking: 是
引句:「遇到時那輪改用沒有這兩種寫法的席當載體重記,或照回放流程標記為制度演進。」
1. 流程:上線後每週自動腳本 `replay_weekly.py` 會對已收斂的迴圈自動 `--freeze`。golden 因此存下 `rows`(含載體 `ts`)和新判準算出的 `verdict`(例如 `fails: []`)。
2. 還原後舊程式不看 `ts`,對含巢狀引號的載體重算會得到 `fails: ["quote"]`。實測:巢狀引句 `「設定「甲「乙」丙」才能啟用」`,舊抽取只抽到 `「設定「甲「乙」`,判「<10 字下限」並回傳 rc1。
3. `cmd_loop_replay` 用 `g.get("engine_rev") != _REPLAY_ENGINE_REV` 判過期。spec 明說不推進 `_REPLAY_ENGINE_REV`,所以不會進「golden 過期(制度演進)」,而是走 `rc != want.get("rc")` 那條,回 rc1 的 `⛔ 邏輯漂移`。
4. 每週腳本把它記進 `red`,輸出「🔴 回放紅燈要人看」。
5. spec 說「照回放流程標記為制度演進」,唯一能做到的辦法是還原提交也推進 `_REPLAY_ENGINE_REV`。這會讓 305 份 golden 全部「跳過重算」,正是該節自己反對推進版本的理由。
6. 「單一提交還原」不包含這一步,spec 沒寫。
7. 另一條路是對每個受影響迴圈 `--freeze --note` 重凍。重凍時舊判準會把「判過」的輪次重算成 `fails: ["quote"]`,並把這個紅結果凍成新的標準答案,還會往治理帳寫一筆 `replay-refreeze`。

2. 「換載體重記」做不到,〈實務隱患〉的「不可逆:無」不成立
severity: major
blocking: 是
引句:「已排除:不可逆:只改判定,不改任何帳本或卷證;還原提交就回到舊判準」
file: `scripts/lumos:10950` 寫側註解寫明「帳本只進不出」,處置閘擋下時只能「換迴圈編號把整輪重記一次」。
1. 上線期間載體靠新判準過寫側檢查,例如含巢狀引號、或引句在反引號內。載體帳是 append-only,每輪只能有一筆(`len(carriers) > 1` 直接 rc2)。
2. 還原後處置閘對那筆帳改用舊判準,轉紅且撤不掉帳。唯一出路是換新迴圈編號,把整輪審查重做。
3. 〈回退〉寫的「那輪改用沒有這兩種寫法的席當載體重記」在同編號下不可行。
4. 所以「不改任何帳本」只對寫入動作成立。還原的實際後果是已通過的迴圈被迫整輪重審,加上重凍的治理帳條目,這些都不可逆。

3. 「把切換日改到未來」只關掉處置閘,寫側、手動 quote-check、seat-check 仍用新判準
severity: major
blocking: 是
引句:「只想暫時關掉不還原:把切換日改到未來,所有輪次都回到舊判準(要走代碼審)。」
1. 〈做法〉規定:記帳寫側、手動 `quote-check`、`seat-check`「一律用新判準」,只有處置閘看 `ts`。改常數只回退處置閘。
2. 停用期間兩邊判準分歧,而且兩個方向都會出問題:
   - 巢狀引號載體,寫側用新判準放行,處置閘用舊判準擋。帳已進本、撤不掉,又落入第 2 條的整輪重記。
   - 前綴對、後半編造的載體,寫側用新判準擋,處置閘本來會放。寫側變得比閘還嚴。
3. 程式註解(`scripts/lumos` 約 10950 行)寫側檢查的目的,就是讓寫側和處置閘用同一道檢查。這個停用路徑破壞了這個保證。
4. 「所有輪次都回到舊判準」的宣稱不實。

4. spec 的 `_QUOTE_STRICT_SINCE` 形狀與先寫好的測試互相矛盾,停用時改常數會出錯
severity: major
blocking: 是
引句:「新常數 `_QUOTE_STRICT_SINCE` 設成合入隔日 `T00:00:00+08:00`(實作時填實際日期,寫法同 `_SECURITY_SEAT_SINCE`)。」
file: `scripts/test_lumos.py` 的 `t_quote_full_span_forward_only` 組時間用 `f"{m._QUOTE_STRICT_SINCE}T00:00:00+08:00"`,把常數當純日期。
file: `scripts/lumos:8216` `_SECURITY_SEAT_SINCE` 是完整時間戳 `"2026-09-12T00:00:00+08:00"`。
1. 照 spec 實作,常數是完整時間戳。測試組出 `…+08:00T00:00:00+08:00`,`_loop_ts_key` 的 `fromisoformat` 丟 `ValueError`,回傳 `None`。
2. 這時「切換日當天」那列會落到舊判準,測試預期 rc1 實得 rc0,測試紅。
3. 實作者只能二選一:改測試,或把常數改成純日期,後者就偏離了「寫法同 `_SECURITY_SEAT_SINCE`」。
4. 停用或回退要動的正是這個常數,格式不定就沒有可照著做的步驟。
5. spec 對 `ts` 解析失敗(非缺 `ts`)也沒定義。`_loop_ts_key` 回 `None` 時,新舊哪一邊,spec 只寫了「缺 `ts` 用舊判準」。⚠

總結:最高等級 major,blocking 共 4 條
