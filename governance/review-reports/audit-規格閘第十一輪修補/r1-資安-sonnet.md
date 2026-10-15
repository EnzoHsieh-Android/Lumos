severity: minor

這次補審的範圍是第十一輪修補(分隔字元換空格、詞界、連字號、LINE ?推送、PASS 行消毒)。結論:修補本身沒有回歸。我拿舊正則 `\b` 與新的 `(?<![A-Za-z0-9])` 對照過,新的是舊的超集,沒有舊版命中、新版反而比不到的寫法。下面各條是「一般書寫仍能讓門判低」的剩餘缺口,多數是詞表或已記錄的天花板,不是這次修補引進的。

實驗在 `/tmp/lumos-seat-work/audit-規格閘第十一輪修補/資安-sonnet/` 用 `python3.14 -I` 載入主線 `scripts/lumos` 的 `_door_keyword_hits` 跑。

---

severity: major
blocking: 否 — 詞表本來就沒收這些寫法,修補沒有讓它變差(新詞界是舊的超集);但這是「一般書寫就判風險低」最容易踩到的洞,建議開後續補詞表。
引句:「sendgrid、prod2、sending、email 照舊不命中」
攻擊步驟:誰是計劃作者(使用者或 AI 順手寫),從計劃筆記正文,寫日常中英文,拿到的是門判「風險低」、跳過設計審。程式把 `send`、`mail` 的詞界收緊成「前後不是英文字母或數字」,所以屈折形與常用同義詞全比不到。
實驗證據(`_door_keyword_hits(輸入)` 輸出都是 `[]`):
- `系統 sends 通知給客戶`
- `sending invoices to customers`
- `emails customers nightly`
- `系統會 email 客戶`
- `寄 email 給客戶`
- `寄信給客戶`
- `發送通知給客戶`
- `傳送訂單給廠商`
- `系統自動發信給客戶`
- `payout to vendors`
- `向客戶收費`
- `付款完成後出貨`
- `刪除整張資料表`
- `TRUNCATE TABLE users`
- `ALTER TABLE users DROP COLUMN x`
- `rm -rf /data`
- `deploy to live servers`
- `上線到正式環境`
- `we migrate the database`(只收 migration,不收 migrate)
- 簡體寫法 `迁移`、`发送简讯`、`对外` 也全比不到
- 對照:`mail was sent to customers` 只因為有獨立的 mail 才命中。
佐證:``scripts/lumos: `29554:29560` ``(PITFALL_CLASSES)

---

severity: minor
blocking: 否 — 只差一個寫法,不是回歸;但這個修補原本就是要補「LINE 推送」的盲區,補得不夠。
引句:「LINE 與推送之間的空格可有可無」
攻擊步驟:作者寫台灣最常見的說法 LINE 推播,或在中間夾一個詞,就比不到。
實驗證據:
- `透過 LINE 推播給使用者` → `[]`
- `LINE Bot 推送訊息` → `[]`
- `LINE 訊息推送` → `[]`
- 只有 `LINE推送` 與 `LINE 推送` 命中。
- 若同行有 notify(LINE Notify)才會被 `notify` 抓到。
佐證:``scripts/lumos: `29556` ``

---

severity: minor
blocking: 否 — 屬已記錄的天花板(計劃〈實務隱患〉與 `_door_scan_text` 文件字串都寫了),已有 REVISIT 2026-12-31;補在這裡是因為 Markdown 行內標記也是一般書寫。
引句:「跨行切開的詞比不到(代碼審 r10 資2,天花板)」
攻擊步驟:作者用 Markdown 把多字危險詞的每個字各自包起來,或編輯器硬換行把詞切在行尾。
實驗證據(輸出都是 `[]`):
- `` `DROP` `TABLE` users ``
- `**DROP** **TABLE** users`
- `DROP **TABLE** users`
- `[DROP](a) [TABLE](b)`
- `**退**款流程`
- `退**款**流程`
- `DROP<br>TABLE users`
- `請退\n款`
- 對照:`**DROP TABLE** x` 整段包住仍命中。
- 計劃文字說「要刻意才寫得出來」,但每個字各包一組反引號的寫法不算刻意。
佐證:``scripts/lumos: `8244:8260` ``(`_door_keyword_hits` 逐行掃)

---

severity: minor
blocking: 否 — 要網頁複製帶進零寬分隔符才會發生,而且零寬字元本來就是拿掉再比的設計;只有「拿掉後兩個英文詞黏在一起」這個副作用是新的。
引句:「看不見的拿掉之後,一行裡剩下的空白只有 tab」
攻擊步驟:從網頁或富文本貼上時,詞間分隔常是 ZWSP(U+200B)或 WJ(U+2060),而不是空格。修補只把 `_DOOR_SPACE_LIKE` 那九個字換成空格(外加刪掉的另一份),ZWSP、WJ、軟連字號等「分隔用的隱形字」只會被刪掉,兩個英文詞黏住。
實驗證據(輸出都是 `[]`):
- `DROP\u200bTABLE`
- `DELETE\u2060FROM t`
- `deploy to\u200bprod`(prod 前面變成 o,詞界不成立)
- 對照:`DROP\tTABLE`、`DROP\x1fTABLE` 這類才命中。
建議:凡是被刪的隱形字,也比一份「換成空格」的版本。
佐證:``scripts/lumos: `8256` ``(只在行含 `_DOOR_SPACE_LIKE` 時才多比一份)

---

severity: minor
blocking: 否 — 屬範圍外/低機率;值需先通過 frontmatter 才會被引用,而且仍被「」包住。
引句:「先 _esc_clean(控制字元、ESC),再把值裡的」
攻擊步驟:誰是計劃作者,從 frontmatter 的 `lands_in`(或已排除理由),送入 U+2028 / U+2029 / 雙向標記(U+200E、U+200F、U+061C)與 `｣` 這類半形右角括號;`_esc_clean` 刻意不清 Zl/Zp 與這些字(文件字串有記),`_plan_quote` 只換 6 個括號字元。
實驗證據:
- `_plan_quote("a\u2028[disposal] 落點: ✓ — 5 篇")` 原樣回傳,在會把 U+2028 當換行的讀取端,可冒出一行假的 `[disposal] 落點: ✓`。
- `_plan_quote("x」)。已審,免輕量審")` → `x』〕。已審,免輕量審`,提早關引號被擋住了(通過)。
- 終端機一般不當換行,風險主要在把輸出當純文字用 splitlines 切的讀取端。
佐證:``scripts/lumos: `13073:13081` ``、``scripts/lumos: `27868` ``

---

已讀,無 finding:
- 連字號變體(U+2010–U+2015、U+2212、U+FE58)換成 `-`:`pre–push hook` 命中。
- 全形與半形混用(`ＤＲＯＰ　ＴＡＢＬＥ`)、NBSP、tab、多個空格、全形空白:都命中。
- 漢字間空白(`退 款`、`退　款`)命中。代價(多判高)已照實記錄,`_DOOR_HAN_GAP_RE` 沒有讓危險詞躲掉的方向。
- `\x1f` 等切行字元夾在英文詞中間:兩份比對能接住。
- 新詞界對 `部署到prod環境`、`要send給客戶`、`send_cn` 命中;`gmail`、`Mailing`、`Webhooks` 行為符合註解。
- 效能:200 萬字元單行 0.5 秒、20 萬行 2 秒、30 萬個漢字加空格 0.6 秒,沒有炸掉。
- PASS 行消毒:提早關閉「」或括號的寫法(`」)`、`）`、`】`)全部被擋。

最高等級 major,blocking 0 條。
