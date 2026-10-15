severity: minor

LUMOS-SEAT: audit-規格閘第十一輪修補/r1/正確性-sonnet

所有實驗都在主線 9d9eb5dc(lens-followups,只讀)上做,沒有寫帳或改檔。實驗用到的臨時目錄已刪。

## Finding 1

severity: minor
blocking: 否 — 要刻意在同一個詞裡混用兩種分隔才繞得過,屬刻意夾帶。計劃〈實務隱患〉對這類「要刻意才寫得出來」的寫法一貫放行。但這是同一族第七次,應該照實記下。
引句:「含這幾個字的行另比一份刪掉的寫法」
問題:修補只比「全換成空格」與「全刪掉」兩種寫法。一個多字危險詞若同時有一處是詞間分隔、另一處是詞內夾字,兩種寫法都湊不出原詞。
具體失敗情境:
- 輸入 `DROP\x0bTA\x0bBLE`。換空格得到 `DROP TA BLE`,刪掉得到 `DROPTABLE`,都不命中,`_door_keyword_hits` 回空清單。
- 輸入 `pre-pu\x1fsh\x0bhook` 同樣回空。
- 對照:`DROP\x0bTABLE`、`DROP TA\x0bBLE`、`pay\x0bment`、`退\x0b款` 都正確命中。
- 結果:這行危險內容判成風險低,不需要設計審。
- 補法:把「是否算分隔」交給詞表自己決定,例如多字詞的空白位置改成「空格或這 9 個字元都可有可無」。

佐證:`scripts/lumos:8256`(`scans = (...)` 只有兩份),`scripts/lumos:8234`(`_DOOR_SPACE_LIKE`)。

## Finding 2

severity: minor
blocking: 否 — 只影響 `pre-push hook` 這一個帶連字號的詞,而且要刻意換字元。
引句:「連字號變體 → -:U+2010–U+2015、減號 U+2212、小型破折號 U+FE58」
問題:連字號變體用手列碼位,沒有按 Unicode 類別 Pd 判。專案前幾輪(r8 到 r10 的隱形字元)已經在同一種做法上吃過虧。
具體失敗情境:
- 輸入 `pre\u058apush hook`(亞美尼亞連字號),回空清單。
- `pre\u05bepush hook`(希伯來 maqaf)、`pre\u1806push`、`pre\u30a0push`(片假名雙連字號)、`pre\u2043push`(U+2043 的類別是 Po,不是 Pd)也都回空。
- 對照:`pre\u2010push hook` 與 `pre\u2212push hook` 命中。
- 我掃了全碼位。NFKC 的輸出裡沒有手列表以外的 Pd 字元,所以只有「原本就是這些碼位」的路徑漏,範圍有限。
- 補法:Pd 全類加 U+2043、U+2212 換成 `-`,並像 `t_door_scan_space_like_as_space` 那樣用全碼位窮舉驗表。

佐證:`scripts/lumos:8237`(`_DOOR_DASH_FOLD`)。`t_door_scan_dash_variants` 的碼位也是手列(`‐‑‒–—―−﹘﹣－`),所以測試抓不到漏的碼位。

## Finding 3

severity: minor
blocking: 否 — 在本 repo 沒有實際影響,但計劃與 Systems 筆記的說法與行為對不上。
引句:「改這張表要升 _DOOR_RULE_VERSION」
問題:`PITFALL_CLASSES` 是兩條路共用的表:門的關鍵字掃描,以及 `lumos pitfalls <計劃> [--check]`(`_pitfall_scan_classes`,`scripts/lumos:47142`)。改了詞界之後,`pitfalls` 那條路也跟著放寬。計劃〈做法〉寫的是「本計劃不動它」,修補的文件沒更正。
具體失敗情境:
- 消費專案的計劃散文(剝掉行內程式碼後)寫了 `send_email`、`prod_db` 或 `部署到prod環境`。
- 修補前 `pitfalls --check` 不命中、不要求「## 實務隱患」節,修補後命中、無節就回 1。
- 實測本 repo 292 份 `Projects/*_計劃.md`,命中類別改變 0 份。

## 已讀,無 finding

**單字詞夾分隔字元與多字詞**
- 單字詞夾分隔字元:`pay\x0bment`、`pay\x1fment`、`退\x0b款` 都命中(分別靠刪掉那份與漢字間空白拿掉)。
- 多字詞:`DROP\x0bTABLE`、`DROP\x0b\x0bTABLE`、`DELETE\u2028FROM`、`anchor\x0bverify`、`LINE\x0b推送` 都命中。
- 全形加分隔字元的 `ｐａｙ\x0bｍｅｎｔ` 也命中。

**兩份比對**
- 每行每類只回一筆,沒有重複算。
- `next(...)` 的順序固定(先看詞表、再看兩份比對),所以記進指紋的命中詞是確定的。
- `any(c in _DOOR_SPACE_LIKE ...)` 檢查的是原文。
- 我對全碼位掃了 NFKC:沒有任何字會生出那 9 個字元,所以「先換再 NFKC」成立。

**切行、行號與條款指紋**
- `_ledger_lines` 就是 `_LEDGER_LINE_RE.split`,沒有自己丟尾段。
- `_note_lines` 只多丟一次尾端空段,行為與修補前相同。
- `"a\n\n"` 仍得到 `["a", ""]`。

**英文詞界放寬的誤判量**
- 我拿修補前的詞表與主線的 `_door_scan_text` 比 953 份 `docs/**/*.md`:新增命中只有 8 份、8 行(send 5、prod 2、`LINE推送` 1),沒有任何一行從有命中變成沒命中。
- 這與計劃寫的「944 篇、9 篇有變」同量級。
- 對照詞 `sendgrid`、`prod2`、`sending`、`email`、`products`、`gmail` 不命中。
- 非 ASCII 字母緊貼(例如 `émail`)會命中,這是多判高的方向,可接受。

**效能與記憶體**
- 約 3.5MB 單行純文字掃描 3.4 秒(其中 `any(...)` 只佔 0.13 秒),峰值約 217MB。
- 480 萬字且全是分隔字元的單行,兩份比對共 1.4 秒。
- 20 萬行 2.6 秒;100 萬個空白 0.03 秒。
- 都是線性,沒有爆炸。

**治理帳惰性讀**(資料狀態五問)
- 帳不存在、空檔、尾端截斷或含亂碼:回 `([], None)` 或可用的事件,不崩。
- 帳是資料夾或符號連結:回 `([], 原因)`,fail-closed 的資訊照樣傳給 `_disposal_judge`。
- 兩次呼叫回同一個物件(`ctx["gov"]`),多份計劃只讀一次。
- 讀失敗的結果也會被快取,每份計劃看到同一個原因。
- 讀帳失敗(`err`)路徑的 ctx 沒有 `"gov"` 鍵,但那條路在走到 (b) 之前就已擋下。
- 併發這一項在單人依序操作的威脅模型下不適用。

**`_plan_quote`**
- 先過 `_esc_clean`,再換掉「」與全形、半形括號。
- 風險低那一行與落點那一步兩個呼叫點都已換用。
- `lands_in` 的成功行有 `_LANDS_IN_ITEM_RE` 把關。

**`_CJK_HAN_RANGE`**
- 兩個正則都由它組出,等價於修補前的字面範圍。

最高等級 minor,blocking 0 條。
