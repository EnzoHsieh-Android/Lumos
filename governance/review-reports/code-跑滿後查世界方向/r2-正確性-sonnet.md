severity: minor

本輪修補的三個目標都成立:記完人裁後讀回帳上那筆、各呼叫端補給情況值、新鮮度守衛改 -G 並嚴格早於。我找不到會做出錯誤行為或損壞資料的輸入,只有兩條覆蓋與文字不一致的 minor。

### F1 `--template --write` 兩處新帶入的情況值沒有任何測試守著
severity: minor
blocking: 否 — 只是覆蓋面不足(minor 對應否):提示句少接一句不會做錯事,也不破壞合約。
引句:「print(f"擋下:回顧檔已經存在({qrel}),不覆寫。{_cap_retro_fix_cmd(root, loop_id, 'none', _cap_world_case(dec))}", file=sys.stderr)」
file: `scripts/lumos:23040`(同類的另一處在 `scripts/lumos:23034`)
失敗場景:最新人裁是生效後的 extra-round,回顧檔已存在,使用者再跑 `lumos loop retro <編號> --template --write`。程式走到 `FileExistsError` 那支,訊息應多接 `把查方向的結論寫進回顧的 world_check`。把這兩處改回不帶情況值,訊息就少了這句。修補宣稱 `--template --write` 也帶入,但測試抓不到:
- `t_cap_retro_fix_cmd_world_fill_everywhere` 只驗 doctor 與 retro-stats。
- `t_cap_hint_world_check_first` 只驗 cap-decision、canary record、處置閘。
- 修補配對的 `r1-fix.json` 沒有列對應 `--template --write` 的案例。
重現(我在臨時 clone 做的):
1. clone 到 `531463257`,把 `scripts/lumos` 裡這兩處的 `, _cap_world_case(dec))` 拿掉(替換命中 2 處)。
2. 清掉 `__pycache__`。
3. 跑 `python3.14 scripts/test_lumos.py -k world` 得 `116 passed, 0 failed`。
4. 跑 `python3.14 scripts/test_lumos.py -k retro` 得 `428 passed, 0 failed`。

對照組:同樣方式把 doctor 那處拿掉,`t_cap_retro_fix_cmd_world_fill_everywhere` 的 doctor 斷言翻紅。把 retro-stats 那處拿掉,retro-stats 斷言翻紅。把 cap-decision 改回讀時鐘,`t_cap_decision_world_fill_reads_ledger` 翻紅。這三處有守住,只有 `--template --write` 這兩處沒有。
歸因:未判定。這兩處是修補才新增的(修前 `87211d82e` 沒帶情況值,修後有),所以是修補自己的覆蓋缺口,不是修前行為的回歸。修前沒有這個行為可比,所以沒有修前對照。修後兩處同時拿掉全部測試仍綠,以此為證。

### F2 新鮮度守衛改成嚴格早於後,常數旁的註解、測試 docstring 和計劃做法 7 仍寫「不早於/不晚於」
severity: minor
blocking: 否 — 只是文字與實際判法不一致,不改變行為,守衛本身正確。
引句:「最後一次改到常數那一行的提交日期不晚於常數日期」
file: `scripts/test_lumos.py:t_cap_world_since_parseable_and_fresh` 的 docstring;`scripts/lumos:22127` 的常數註解(寫「不早於最後一次改它的提交日」);計劃〈做法〉7(寫「不晚於常數日期」)
失敗場景:讀註解的人把常數設成「提交當天零點」,例如提交日 `2026-11-05`、常數 `2026-11-05T00:00:00+08:00`。依註解「不早於/不晚於」這該過。實際判法是 `day < since[:10]`,同日會紅(測試 `F2 守衛的比法` 也釘「同日不算」)。條件寫成含等號,實作是不含等號。
重現:`python3.14 scripts/lumos` 同目錄臨時 repo 下,用 `_cap_since_fresh("2026-11-05","2026-11-05T00:00:00+08:00")` 得 False。
歸因:有證據的修復回歸。比對式在修補才由 `<=` 改成 `<`,文字沒跟著改;`87211d82e` 的 docstring 與 `<=` 當時一致。

## 圖譜鏡頭
- **Systems/loop-retro**:宣稱「五處共用同一支判定」。修補只新增呼叫端傳入情況值,判定仍只有 `_cap_world_case` 一支;`_cap_retro_status` 的狀態、回傳欄位、`_RETRO_STATE_LABEL` 沒動,只在 dict 開頭多一個 `world_case: None`。不破壞它。
- **Systems/loop-convergence-recording**:修補在 WHY 補了「doctor、retro-stats 都經過它;記完人裁讀回帳上那筆」,與程式一致,並多綁 `t_cap_decision_world_fill_reads_ledger`。不破壞它。
- **Systems/每輪修補差異派工**:修補沒碰派工與〈先查世界〉相關檔,不影響。

## 三問
1. **原問題的修復效果有何行為證據?**
   - c1/a4(記完人裁判情況):把 `cmd_loop_cap_decision` 改回讀時鐘,`t_cap_decision_world_fill_reads_ledger` 的 3 條「判情況用的是帳上那筆」斷言翻紅,修後綠。
   - 要補一句:這個測試是用 spy 看傳進 `_cap_world_case` 的引數形狀。時鐘與帳上 ts 只有跨過生效常數那一刻才會不同,實際行為斷言(輸出含不含 fill)在舊寫法下也綠。所以它靠 spy 才分得出新舊,對「引數必須是帶 `gate`/`kind` 的帳上事件」有耦合。
   - a1–a3(doctor、retro-stats 帶情況值):各自拿掉對應呼叫端,`t_cap_retro_fix_cmd_world_fill_everywhere` 對應斷言翻紅。
   - c2(新鮮度守衛):`t_cap_since_last_change_sees_value_edit` 造「先加常數、後只改值」兩個提交,期望 `2026-11-10`。`-G` 看得到,`-S` 看不到。同日不算新鮮也有直接斷言。
2. **修補處正常、錯誤、相鄰路徑是否仍成立?**
   - 同一迴圈多筆人裁時取檔內最後一筆,與 `_cap_retro_status` 取 D 的規則一致。
   - 讀回帳失敗時 `dec=None`、判成 ignored,只會少印提示,不影響 `--check` 的強制判定;剛寫成功後讀不動不是實際路徑。
   - `_cap_world_case` 對 ts 為 `None`、空字串、整數、清單、`Z`、無時區、孤立代理字元、年份極端值、全形數字都不丟例外,結果與計劃 S5 一致。
   - `_retro_world_check` 與 `_retro_world_empty` 對 17 種值的四欄組合(約 8 萬組)不丟例外。
   - 所有 `_cap_retro_fix_cmd(` 呼叫端我逐個核對:知道最新人裁的都帶情況值,治理帳壞的兩處(`None,'gov-bad'`、`'gov-bad'`)照舊不帶,符合文件說法。
3. **新發現的同一案例修前、修後各是什麼結果?**
   - F1:修前 `87211d82e` 沒有帶入,修後有,修後拿掉全綠,所以屬覆蓋缺口。
   - F2:修前 `<=` 與文字一致,修後 `<` 文字未跟上。

兩條 minor:`--template --write` 兩處情況值沒有測試守著,以及新鮮度守衛改嚴格早於後,註解、docstring 和計劃做法 7 的文字沒跟著改。
