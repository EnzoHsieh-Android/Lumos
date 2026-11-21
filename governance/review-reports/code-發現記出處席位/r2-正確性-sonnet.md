severity: minor

整體判斷:修補處的正常、錯誤與相鄰路徑都走得通,我沒找到 major 以上的洞。有 54 個 `-k finding_seat` 案例通過;`-k loop_next` 在背景跑,我交稿時還沒收到結果,所以這一組未判定。以下兩條 finding 都是 minor。

## Findings

severity: minor
blocking: 否
file: `scripts/test_lumos.py`(`t_canary_record_finding_seat`,新增的「覆寫寫純日期也生效」那段,約 12255 行)
引句:「blocked("覆寫寫純日期也生效", carrier("code-fs-date", "c1"), n0, "--finding-seat")」
失敗場景:這條測試用 `_fs_since("2000-01-01")` 驗純日期覆寫(G4 repair)。修前的 `_finding_seat_since_key` 讀不動純日期,會退回常數 `2026-11-22T00:00:00+08:00`。
- 今天(2026-11-21),載體時間是現在,小於常數,修前版會放行,測試翻紅,鎖得住。
- 2026-11-22 之後,載體時間大於等於常數,修前版也擋,「純日期覆寫生效」這條在修前碼上照綠,變成假綠。
- 我用 `datetime.fromisoformat("2000-01-01").tzinfo is None` 確認純日期會讓 `_loop_ts_key` 回 None,所以才退回常數。
- 我沒有真的把系統時鐘撥到 11-22 去跑測試,這個失效日是推算的。
- 建議改成覆寫 `2999-01-01`,預期同一份載體不被擋,這樣修前修後都能分辨。
歸因:有證據的修復回歸。新測試是這次修補才加的,它的鑑別力會在生效日當天消失。證據是上面的 `fromisoformat` 結果加時間推算,不是整合重跑,所以這條證據偏弱。

severity: minor
blocking: 否
file: `scripts/lumos:18067-18078`(`_seat_noise_name`)
引句:「bare = re.sub(r"(?:(?<=[^\x00-\x7f])r)?\d+$", "", role)」
失敗場景:我拿 `docs/.canary-log.jsonl` 的 794 個真實 auditor 逐一跑這支函式。
- 對照的席名都正確:`正確性2-sonnet`、`資安-r2-sonnet`、`外家finder2-codex`、`架構對齊r2-sonnet` 照預期併回;`外家-gemini-2-flash` 與 `外家-gemini-3-flash` 不併;`外家codex-gpt-5.6-terra` 不動。
- 唯一的副作用:舊帳裡 `鏡頭1-codex`、`鏡頭2-codex`、`修補差異1-codex`、`修補差異2-codex` 的數字是鏡頭編號,不是輪次,會併成 `鏡頭-codex`、`修補差異-codex`。
- 另有三類名字不會被併:`正確性-codex-gpt-5.6-sol-r2` 這種尾端 r2、`slot1-sonnet` 這種英文開頭席名、`r2-seatA-sonnet` 這種輪次在最前面的席名。
- 這些都是已入帳的舊名字,新席名依規定不帶輪次,所以只影響舊帳讀出的數字,而且只在鏡頭編號被誤認為輪次時才併錯;歷史上一個迴圈同時用 `鏡頭1`、`鏡頭2` 兩個鏡頭,它們各報的條數會被加在一列。
- 重現:對 `鏡頭1-codex`、`鏡頭2-codex` 呼叫 `_seat_noise_name`,兩個都回 `鏡頭-codex`。
歸因:有證據的原有漏查。修前的 `_SEAT_ROUND_MARK_RE` 對這些名字也會去掉數字,所以不是修補造成;我沒有逐一對兩版跑完整個 auditor 集合。

## 修補逐項核對(原問題效果、修補處與相鄰路徑)

| 組 | repair | preserve |
|---|---|---|
| G1 席名併列 | `外家-gemini-2/3-flash` 分列、`外家codex-gpt-5.6-terra` 原樣、`外家finder2-codex` 併成 `外家finder-codex`。查證方式:從 `lumos_after.py` 抽出函式直接跑真實 auditor 集合。 | `架構對齊r2-sonnet`、`架構對齊-r2-sonnet`、`架構對齊2-sonnet` 都併成 `架構對齊-sonnet`。 |
| G2 首筆取最早 | 新增混合迴圈測試(首筆 2020、第二筆現在)。程式本身沒改,仍是 `min(keys)`,若改成 `max` 這條測試會紅,鎖得住。 | 空帳和首筆早於生效日不擋,首筆不早於生效日擋。 |
| G3 無 `--loop` | 帶 `--finding-seat` 卻沒 `--loop` 時,在 `if finding_seats:` 內 rc2,不寫帳。 | 沒帶 `--loop` 的載體走不到 `_finding_seat_write_block`(呼叫端有 `if (loop and ...)`),照舊能記。 |
| G4 覆寫生效日 | 純日期當台北 00:00。覆寫把照常數該填的推遲時,stderr 有提醒,條件是 `first >= const`。 | 帶時區的覆寫和沒設覆寫時用常數,都照舊。 |
| G5 badts | 事件 `finding-seat-badts` 有留,訊息含「補帶 --finding-seat」。救法可行:同輪席名通常已入帳,補帶就能過。 | `finding-seat-missing`、`finding-seat-unknown` 事件照舊。 |
| G6 hints | standard 代碼審的 hints 多一條「載體最後記」。 | high 代碼審照舊印資安包與 `--finding-source` 兩條。 |
| G7 `_fs_blocked_n` | 改成只讀 `docs/.governance-log.jsonl`。 | 兩種事件計數照舊成立。 |

另外確認:真實 `docs/.canary-log.jsonl` 沒有時間讀不動或不帶時區的列,所以 badts 的擋下不會誤傷現有迴圈。

## 固定席逐條判定

這次沒附固定席節點,無從逐條判。就我讀到的 `loop-convergence-recording.md` 該節,修補後的敘述與程式一致:三種擋下事件、席名 repr、覆寫提醒、`_seat_noise_name` 規則、56 天窗口。

## 計劃〈驗收條款〉與〈預期值表〉

- 修補後的程式與測試兌現了 S1、S3、S6、S8、S9、S11。
- 回退節新增「手冊與命令速查寫的『目前 2026-11-22』跟著改」。我確認 `reference.md` 與 `06-代碼審與推送.md` 確實各有一處「目前 2026-11-22」。

## 三問

1. 原問題的修復效果有何行為證據?有:54 個案例通過,另有抽出函式的直接重現(G1)。G2、G3、G5、G6 的新測試能鎖住行為,G4 純日期那條的鑑別力有上面那條失效日問題。
2. 修補處的正常、錯誤與相鄰路徑是否仍成立?成立。上表每組都對得上,我沒找到被修補弄壞的相鄰路徑。
3. 新發現的同一案例在修前、修後各是什麼結果?
   - 純日期測試:修前碼今天翻紅、11-22 起翻綠(推算,沒撥時鐘重跑)。
   - 鏡頭編號併列:修前修後都併,屬原有行為。

最嚴重等級 minor
