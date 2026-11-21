severity: minor

第 3 輪修補沒有找到 blocker 或 major。我找到一條 minor 的行為回歸,另有一條文件措辭問題。

## 查證方式

- 在 `/tmp/lumos-seat-work/code-發現記出處席位/正確性-sonnet/` 用 `importlib` 載入 repo 的 `scripts/lumos`,直接呼叫 `_finding_seat_required_block`。事件寫入改成印出,沒有改 repo 任何檔。
- 修前版本用 `git show af2fb6f850feba8f2c0c145bb04544c78da3a239:scripts/lumos` 取出,與修後的 `_seat_noise_name` 並排比對。
- 跑了 `python3.14 scripts/test_lumos.py -k finding_seat`(65 passed、0 failed)和 `-k gov_stats_finding`(14 passed、0 failed)。

## 必填判斷順序(鏡頭 4)

以下每種組合都走過,結果都符合計劃〈做法〉必填條件與〈回退〉。

| 組合 | 結果 |
|---|---|
| 空帳、本筆晚於生效日 | rc 2,`finding-seat-missing` |
| 首筆早於生效日、本筆晚於生效日 | 放行 |
| 首筆晚於生效日 | rc 2 |
| 本筆晚於生效日、帳上有壞時間列(不論有無好的早列、全壞) | rc 2,`finding-seat-badts` |
| 本筆早於生效日、帳上有壞時間列 | 放行 |
| 生效日覆寫為 9999 | 放行;首筆不早於常數時留 `warned` 事件 `finding-seat-since-overridden` 並提醒 |
| 覆寫為 2999-01-01、本筆與首筆都早於常數 | 放行,不提醒 |
| 覆寫值壞掉 | 退回常數 |
| 覆寫為早於常數的日期 | 必填 |
| 本筆時間 UTC 2026-11-21T16:30(台北凌晨 00:30) | 算生效後,rc 2 |
| 本筆時間 UTC 2026-11-21T15:59(台北 23:59) | 算生效前,放行 |
| 本筆時間沒帶時區 | 判不了,從嚴 rc 2 |

擋下路徑只寫治理帳事件,不碰審查帳,沒有半寫帳。事件呼叫改成直接用 `_gate_event_or_warn` 加 `_esc_clean`,是既有做法,不引入新的清洗函式。

## finding 1

severity: minor
blocking: 否
file: `scripts/lumos:18071`(`_seat_noise_name`)
引句:「bare = role.rstrip("0123456789")」
失敗場景:席名角色尾巴是全形或其他 Unicode 數字,例如 `正確性２-sonnet` 或 `正確性٢-sonnet`。修前的 `\d+$` 會去掉輪次記號,併成 `正確性-sonnet`。修後只認 ASCII 數字,兩個都原樣保留,逐席沒用率會多出一列碎片。
歸因:有證據的修復回歸。修前 `af2fb6f8` 輸出 `正確性-sonnet`,修後 `aff4a913` 輸出 `正確性２-sonnet`。
查證命令:`/tmp/lumos-seat-work/code-發現記出處席位/正確性-sonnet/t2.py`,兩版並排結果如上。
影響:新席名照規定不帶輪次,只影響手打全形數字的舊帳,所以只列 minor。

## finding 2

severity: minor
blocking: 否
file: `docs/lumos-toolchain-knowledge/Systems/loop-convergence-recording.md`,「發現出自哪一席」節的「寫側兩段」那條
引句:「帳上有時間讀不動的列時判不了生效前後,不放行。」
失敗場景:同一條後半句說「本筆時間早於生效日就直接不必填,帳上有壞時間的列也不擋」,前後矛盾。計劃 `Projects/代碼審發現記出處席位_計劃.md` 第 52 行〈生效日〉也寫「帳上有一筆時間讀不動 … 擋下、不放行」,沒有加註本筆早於生效日的例外,〈預期值表〉也沒有對應列。讀文件的人會照字面以為回退到 9999 後壞時間列還會擋。程式本身是對的。
歸因:有證據的修復回歸(文件沒跟上)。修前程式本來就是壞列一律擋,此例外是這次修補新引入的。

## 圖譜鏡頭(固定席)

派工詞說這次沒附固定席節點,我只能判改到的兩篇筆記。

- 計劃筆記:審計修正紀錄新增 r2 一行,與程式一致,不影響其他節點。上面 finding 2 的措辭問題在此。
- `Systems/loop-convergence-recording.md`:改寫的段落與程式一致(直接呼叫 `_gate_event_or_warn`、`_esc_clean`、`warned` 事件)。除 finding 2 外不影響其他節點。
- `canary warned` 事件走治理帳,不進審查帳,不影響處置閘或 `gov --stats` 的審查帳讀取。

## 三問

1. 原問題的修復效果:
   - 壞時間列在本筆早於生效日時不再擋,有 `t_canary_record_finding_seat` 的案例鎖住。
   - 覆寫推遲生效日會留事件,測試檢查治理帳含 `finding-seat-since-overridden`。
   - 席名去尾數字改成線性,測試用十萬字元席名限 10 秒內跑完,整個測試 2.6 秒通過。
   - `正確性-2` 和 `外家codex-5` 不再被切成雙連字號,實測成立。
2. 相鄰呼叫路徑:
   - 席名比對路徑的 `finding-seat-unknown` 事件改直接呼叫,仍擋下且不寫帳。
   - `rows_err` 時 `rows` 為空,走「空帳看本筆」,從嚴擋下,方向保守。
3. 新發現的修前修後:
   - finding 1:修前併成 `正確性-sonnet`,修後保留 `正確性２-sonnet`。
   - finding 2:只在文件,不涉及程式前後差異。

最嚴重等級 minor
