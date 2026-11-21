severity: minor

審查範圍:修補差異全文(`r3-repair.patch`),另跑兩版行為對照與 `python3.14 scripts/test_lumos.py -k finding_seat`(65 passed, 0 failed)。實測時我自己取的函式區段是用 `exec` 載入 `scripts/lumos`,沒改任何 repo 檔。

## 發現

severity: minor
blocking: 否
file: `scripts/lumos:19620`(同型在 19615、19624、19655)
引句:「_gate_event_or_warn(root, "canary", "blocked", f"finding-seat-badts loop={_esc_clean(loop)} auditor={_esc_clean(auditor)} id={uuid.uuid4().hex[:8]}", hard=True)」
失敗場景:`canary record` 的 `--auditor` 不是必填(`scripts/lumos:81689`,預設 None)。載體不帶 `--auditor` 卻帶 `--finding-seat` 而被擋時,四種事件的 note 會寫成 `auditor=None`。被刪的 `_finding_seat_event._one` 用 `str(x or "")`,會寫成 `auditor=`。鄰居 `refuted-set-missing`(`scripts/lumos:19855`)用 `auditor or ''`,所以這次也跟鄰居的寫法不一致。影響只是治理帳 note 的字面值,擋下行為與 rc 不變。
重現(兩版同一輸入):`_esc_clean(None)` 回 `'None'`;修前的包裝函式會產生 `''`。
歸因:有證據的修復回歸。刪包裝函式時沒把 `or ''` 補回呼叫處。
修法:四處改成 `_esc_clean(auditor or '')`。

## 逐項核對(判不影響或判通過)

- **G1 事件寫法**:三種擋下事件與推遲提醒的呼叫位置與參數,對照修補差異逐行核過,rc 都是 2、帳不變。`warned` 事件走 `_gate_event_or_warn`,`canary` 在 `_KNOWN_GATES` 內,寫入器沒有 kind 白名單。canary 的 token 去重只針對 `blocked`,`warned` 不受影響。
- **G2 效能**:十萬字元的席名(`a*100000`、中文加十萬個 1、十萬個連字號)三種輸入合計 0.004 秒,是線性。
- **G3 席名併列**:
  - 原樣分列:`正確性-2-sonnet`、`外家codex-5-mini`、`外家codex-6-mini`、`gemini-2`、`edge-3`。
  - 併成同一列:` 空白席-sonnet ` 併成 `空白席-sonnet`;`架構對齊r2-sonnet` 變 `架構對齊-sonnet`;`通才2-sonnet` 變 `通才-sonnet`。
  - `正確性-2-sonnet` 的修前結果是 `正確性--sonnet`(舊正則把 `正確性-2` 的 2 去掉,留下孤立連字號),修後已修好。
  - `外家finder2-codex` 變成 `外家finder-codex`:2 被去掉,跟修前相同,不是新回歸。
- **G4 必填判斷**:
  - 邏輯:`good` 空、`keys` 空、`first` 為 None 等邊角各走一遍,沒有走不到或誤放行的分支。
  - 本筆早於生效日時,帳上有壞時間列也不擋,覆寫為 9999 放行,符合計劃〈回退〉。
  - 本筆不早於生效日且帳上有壞列時,仍擋 `badts` 並回 2。
  - 生效日起,時間在生效前的舊迴圈只要帳上混有一筆壞時間列就會被擋,要補帶 `--finding-seat` 才能記。這是保留的原行為,脫困訊息已寫明。
- **G5 文件**:`--help` 已寫明要跟 `--loop`、`--round`、`--findings-set` 一起給。手冊日期的對照測試 `t_finding_seat_docs_match_since` 通過。reference.md 範本改成行尾 `\` 續行。
- **系統筆記內部不一致(措辭類)**:`loop-convergence-recording.md` 的新段同時有「帳上有時間讀不動的列時判不了生效前後,不放行」和「本筆早於生效日時帳上壞時間列也不擋」兩句。讀者可能誤解前一句是無條件的。不影響程式行為,不另列 finding,可順手補一句「本筆不早於生效日時」。
- **固定席筆記**:這輪派工沒有附固定席節點(鏡頭計算超時),所以沒有逐條固定席判定可寫。我沒自己補算。

## 三問

1. **原問題的修復效果有何行為證據?** 十萬字元席名線性、0.004 秒;`正確性-2`、`外家codex-5` 不再被切壞;四種事件改在原處直接呼叫 `_gate_event_or_warn`。65 個 finding_seat 相關測試全綠。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 成立。設計審、已帶 `finding_seats`、首筆早於生效日、空帳這幾條路徑沒變。唯一偏差是上面那條 minor。
3. **新發現的同一案例修前、修後各是什麼結果?** 載體不帶 `--auditor` 被擋時,修前事件 note 是 `auditor=`,修後是 `auditor=None`。

最嚴重等級 minor
