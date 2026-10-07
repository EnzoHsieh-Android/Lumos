severity: minor

我有在派工詞尾端看到「lumos 自動附加」段:固定席列了 23 篇(前 8 篇貼內容,其餘 15 篇只列名)。角色鏡頭有附卡但本次略過,沒有 finding 對應 be-api-compat 或 be-authz。

## F1 指令速查手冊仍寫「base 不在主線→靜默放行」,與本次改動矛盾
severity: minor
blocking: 否
引句:「base 不在主線→靜默放行 | 鏡頭不是閘,不擋」
佐證:file: `skills/lumos-project-notes/commands/06-代碼審與推送.md`(同一格前半句已改寫成「算不出來會附一行 LUMOS-LENS: 說明」,後半格的舊句沒改)
失敗場景:讀手冊的人或 AI 以為 base 不在主線時掛鉤不會講話。實際上 base_not_mainline 現在會印 `{"lens_fail":"base_not_mainline"}`,掛鉤附說明行。同一格自相矛盾。
歸因:有證據的原有漏查(舊句在修前版與修後版都各出現 1 次,修補只改了同格的前半句)。
查證命令:
- `git show 6c6eeb78:skills/lumos-project-notes/commands/06-代碼審與推送.md | grep -c 'base 不在主線→靜默放行'`,結果 1。
- 同一命令用 `a8b38648`,結果 1。

其餘我走過的路徑都成立:
- 六種代碼的 JSON 與回傳碼:跑了 `lumos dispatch-lens <sha>..HEAD --repo . --json --no-cache --role-cards`。`HEAD~1..HEAD` 回 rc0 並有 text。`<sha>..HEAD` 與 `main..main` 回 `{"lens_fail": "empty_range"}`、rc2。
- 武裝路徑:`--arm X..X` 現在回 rc2。原本會武裝一段全零備援段,這是有意的行為改變,沒有測試或其他呼叫者靠它。`cmd_dispatch_lens_arm` 只在 rc 非零時回傳 rc,JSON 被它自己的緩衝吞掉,不外洩。
- 空輸出判斷:掛鉤「舊版 lumos 不認 --role-cards 才重叫」的條件是 rc2 且 stdout 空。新碼 empty_range 的 stdout 非空,不會被誤判成舊版 lumos。
- `_SAFE_RANGE_RE`:`origin/main..feature/x`、`HEAD~3..HEAD`、完整 sha 範圍都符合。`HEAD@{1}..HEAD` 這種不符合的會被換成 `<範圍>`,只是說明裡少了原文,無害。標記用 `\S+` 擷取、行已 strip,所以 `$` 容許結尾換行這個洞走不到。
- 新舊版本錯開:新掛鉤配舊 lumos 沒有 lens_fail,原樣放行,有測試。舊掛鉤配新 lumos 讀不到 role_text,原樣放行。角色卡開啟、圖譜失敗時 JSON 同時帶 lens_fail 與 role_text,說明在前、角色卡在後。
- 測試:在 `/tmp/lumos-seat-work/code-派工鏡頭跨repo不再靜默/正確性r2-sonnet/c` 跑 `python3.14 scripts/test_lumos.py -k dispatch_lens`,105 通過、0 失敗。

三問:
1. 原問題的修復效果有行為證據:`<sha>..HEAD` 在 HEAD 等於 base 時,修前照算出全零備援段,修後回 `{"lens_fail":"empty_range"}`、rc2。掛鉤對六種代碼都附說明,並有 t_dispatch_lens_hook_fail_reason_notice 驗證。引句:「if bad:」(掛鉤與 lumos 兩端都已實跑確認)。
2. 修補處的正常、錯誤與相鄰路徑仍成立:正常範圍照算,格式不合法與不帶 --json 仍不印,逾時、鎖、spawn 失敗分支未受影響。
3. 新發現的同一案例:F1 修前與修後結果相同,屬原有漏查。

總結:最高等級 輕微(只有手冊一句過期,無程式缺陷)
