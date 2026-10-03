severity: minor

審查範圍:/tmp/code-revA-r3.patch(r2 修正:半形引號整類不認、只認全形)。實驗在 /tmp/codeRevA/exp3/cp(對 repo 的 --shared clone,f7ed1497),repo 本身沒動。`python3.14 scripts/test_lumos.py -k revisit` 在該 clone 80 passed、0 failed。

**C1 落單的全形開引號後面另有一對全形引號時,句中 REVISIT 仍被藏起來(半形那類「整類拿掉」沒有拿到全形)**
severity: minor
blocking: 否 — 只會讓一條寫錯位置的回頭條件漏擋,而且要先有落單的 `「`,實務很少見;出口是 doctor 之外沒人列它,不會誤擋也不會損資料
引句:「        out.append(any(v and last[_REVISIT_QUOTES[o]] > i for o, v in open_.items()))」

1. 輸入:`「沒收的引號 REVISIT:2026-10-05 x 他說「好」然後`(落單的 `「`,後面另有一對 `「好」`)。
2. 走法:掃到位置 i 時 `open_['「']` 為 True(落單的開引號);`last['」']` 是後面那個 `」` 的位置,大於 i,所以判成「在引號裡」,回傳 `[]`,第一層不擋、doctor Z 段不列。
3. 重現(clone 內):`m._revisit_misplaced("「沒收的引號 REVISIT:2026-10-05 x 他說「好」然後")` 輸出 `[]`;同樣的 `“未收 REVISIT:2026-10-05 x 再 “好” 結尾` 也輸出 `[]`。
4. 壞在哪:這跟 r1、r2 兩輪對半形 `"` 抓到的是同一個形狀(落單開引號 + 後面另一對),作者的結論「分不出開與收所以整類拿掉」只對半形成立;全形的「開」本身分得出來,但「落單的開引號」仍分不出,「後面真的有收」這個判準擋不住後面剛好另有一對的情況。測試 `t_revisit_misplaced_review_r1` ② 只測了「落單開引號後面完全沒有收」,沒測這個組合。
5. 計劃宣稱:〈做法〉1.1 與審計修正紀錄寫「同類第二輪,換形狀:半形引號整類不認」,讀的人會以為引號這類已收斂;實際全形還剩一個組合。落單的全形開引號本來就少見,所以只算 minor。

**C2 同種全形引號巢狀時,內層一收就把外層當成已收,外層引號裡的句中 REVISIT 被報**
severity: minor
blocking: 否 — 只是把本該放過的範例句誤報(要求作者改用行內程式碼),有明確改法,不漏擋
引句:「                open_[closer[ch]] = False」

1. 輸入:`範例「他說「好」然後 REVISIT:2026-10-05 x 結束」`(外層 `「…」` 裡又有一對 `「好」`)。
2. 走法:每種引號只用一個布林;內層 `」` 把 `open_['「']` 設成 False,後面的 REVISIT 位置因此不被當成在引號裡,回傳 `[11]`,第一層會擋。
3. 重現(clone 內):上面那行輸出 `[11]`;同一句內層改成 `『好』` 則輸出 `[]`。
4. 壞在哪:旗標不是計數,同種巢狀會讓外層提早「收」。範例句裡再引一句話是自然的寫法(正是這個規則要放過的對象)。出口是改用行內程式碼,跟改法字串一致,所以不是 blocking。

沒問題的項目

- 半形 `"` 整類拿掉後的程式與測試:`_revisit_quote_states` 不再讀 `"`,`'他寫 "REVISIT:2027-01-01 x" 這樣'` 現在回 `[4]`(算句中)、`'我們用 5" 管。REVISIT:2026-10-05 x'` 回 `[9]`;測試 ③b 兩個斷言都直接釘這兩個形狀,把修法改回去會紅(舊碼會回 `[]`)。
- 已有的前置斷言:`t_revisit_misplaced_ignores_mentions` ② 先證明同一句拿掉引號就算句中,所以「引號內不報」那條不是空轉;測試把半形範例換成 `“…”`,與新規則一致。
- 線性效能:`last` 改為只算三個收引號的 `rfind`,掃描仍整行一遍,`t_revisit_misplaced_linear` 沒受影響(80 支全綠含該支)。
- 說明同步:`_REVISIT_MISPLACED_FIX` 字串、`skills/lumos-project-notes/commands/03-寫回圖譜.md`、計劃〈做法〉1.1、1.2、S3、天花板 1 都已改成「全形引號」;我用 grep 搜整個 repo 找「用行內程式碼或引號」,留著舊字樣的只剩 `governance/review-reports/` 下的歷史卷證快照,不是現行說明。
- 存量影響:對 clone 內所有 `docs/*-knowledge` 跑 `_revisit_misplaced_lines`,有「半形引號包住 REVISIT」形狀的只有 1 行(`Codex完全支援_計劃.md` 169 行),doctor Z 段多列一行,不影響其他計數。
- 與審計修正紀錄:r2 紀錄寫「2 條(同一件)/全 minor」與我看到的這輪 diff 內容相符;沒有發現計劃宣稱跟程式不一致的驗收條款(S3 已改全形、天花板 1 已改全形)。

固定席節點(lens.txt)

- bound-tests-gate、guard-kill、授權與歸屬、測試假綠形態、lumos-cli-read、design-loop、lumos-cli-lifecycle 這七篇的合約都針對別的機制(固定席閘、guard kill 的 rc 與 JSON、授權檔白名單、翻紅釘前置斷言、search 排除 superseded、處置閘第五步、re-inject sentinel)。這份 diff 只動 `_revisit_quote_states`、`_revisit_misplaced` 的說明字、一個提示字串、一支測試與計劃/skill 文字,不碰那些路徑,判不影響。
- 測試假綠形態「還原翻紅釘要配前置斷言」:本輪新增的 ③b 是還原會翻紅的釘,現場(`_revisit_misplaced` 對半形引號行真的被呼叫)由同一支測試前面的 ③ 與 ignores_mentions 的 ② 前提撐住,符合。
- 授權與歸屬:`scripts/lumos` 檔頭 SPDX 與 MIT 全文沒被這份 diff 動到(hunk 都在 31723 行之後)。
- pitfalls-code-loop 與其餘只列名的節點:這份 diff 沒有碰留痕、簿記或分級邏輯,判不影響。

最高 severity:minor
