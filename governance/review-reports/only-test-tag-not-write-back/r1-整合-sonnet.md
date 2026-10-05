severity: minor

# r1 外部審稿:只換測試綁定不算寫說明_計劃

核心結論:rtb 的實際情境(`Systems/共用行程基礎.md` 第 17、18、25、27、28、35 行,值全是 ASCII 測試名,rtb 副本 `/Users/enzo/rtb-lumos-update` 掃過無不合白名單的標記、無奇數反引號行)用這份 spec 解得掉。判定面查證:`_nodehome_parse_note` 的 sig 只有三處讀取(`scripts/lumos:27239`、`scripts/lumos:27335`、`scripts/lumos:26861` 定義),一處改兩條路都生效的說法成立;S3 的走法也對(content_changed 空 → wb_notes 空 → 落到 legacy-homeless 提醒)。以下是投稿者沒看到的洞,皆不擋實作。

## 逐節
- 標頭/summary/白話/依據/PRIOR-ART/RETIRE-IF:已讀,無 finding。
- 範圍:見 F2。
- 做法:見 F2、F3。
- 實務隱患:已讀,無 finding(「提醒多唸」「誤判沒變」與 `scripts/lumos:27412` 附近 nudge 邏輯對得上)。
- 驗收條款:見 F4。
- 回退、天花板:已讀,無 finding。

## Findings

### F1 寫進圖譜的說明只補一行 WHY,同一篇裡兩條現行 KEY 會變成假話
severity: minor
blocking: 否 + 只是筆記精度,程式行為不受影響
引句:「寫進 [[Systems/每支檔有家]]:摘要一行 WHY 說明「內容有變」不含綁定標記與值的字元限制。」
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:34` 寫「沒有單條逃生口,越界的唯一合法寫法是把檔加進那篇的 about_code」;放行後多了「只換綁定」這個合法寫法,「唯一」就錯了。
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:28` 寫「內容(摘要、決策、正文)是在這個提交改的才算寫回」,沒提綁定標記被扣掉。
三個月後的人讀 34 行會照舊叫 rtb 去加 about_code(正是 rtb 試過且失敗的路)。spec 步驟 3 沒要求改這兩行(KEY 是未分類的線索,但這兩條是下一個 session 最先讀到的)。

### F2 「行內程式碼整段保留」逐字描述是跨行掃,跟它宣稱一致的 `slot_parse` 是逐行
severity: minor
blocking: 否 + 錯誤方向是多擋(保守),且需要奇數反引號行才觸發
引句:「跟行內標記解析 `slot_parse` 的既有判法一致(行內程式碼裡的方括號不算欄位)。」
引句:「由左往右掃,碰到行內程式碼(反引號到下一個反引號)整段照留」
file: `scripts/lumos:4145-4160` `slot_parse` 一次只吃一行(`rest`),不成對的反引號只影響到行尾;而 sig 的摘要、正文是多行字串,若實作照字面對整段字串掃,上一行的單個落單反引號會配到下一個反引號(或吞到全文結尾),使後面真正的 `[test:舊]` 沒被拿掉(換名仍擋)、或使真行內程式碼的範例被拿掉。S1 沒有「奇數反引號行後面接綁定換名」的案例,實作者兩種寫法都會過驗收。要寫明「逐行掃」並補一個案例。

### F3 單獨成行的綁定標記:加或刪那一行仍算內容有變,與 S1 的「多加一個綁定、刪掉一個綁定」字面不符
severity: minor
blocking: 否 + 只影響標記單獨占一行(例如條列符號後只有標記)的寫法,現存節點未見
引句:「只換、加、刪測試綁定標記的改動不算寫說明。」
file: `scripts/lumos:26861-26862` sig 是 `"\n".join(l.rstrip() for l in ...)`;標記拿掉後該行變成空行或只剩 `-`,新增整行綁定會多出一行,逐行 join 的結果就不同,等於仍判有變。spec 的做法 1 只說拿掉標記與前面的空白,沒說拿掉後空行是否一併收掉。⚠ 現存節點未見這種寫法,只是字面與實作對不上。

### F4 放行 home check 不等於整個提交過得了關;步驟 4「可以重做改名」未驗其他閘
severity: minor
blocking: 否 + rtb 實際那幾行(RULE/PITFALL,有 since/retire 或防回歸)與本案無衝突,風險只落在沒帶來源的 FACT/FLOW/DEP 行
引句:「上線後告訴 rtb:可以重做 2026-10-03 放棄的那次測試改名,並關掉交棒單那條回頭條件。」
file: `scripts/lumos:28167-28175` `_ns_is_tail_append` 是筆記形狀擋唯一的舊行豁免,只認行尾補括號;行中間把 `[test:舊]` 換成新名的行,對筆記形狀擋是新寫的行。
file: `docs/lumos-toolchain-knowledge/Systems/reversibility-governance-ledger.md:42` 是一行沒帶 `[來源:…]` 的 DEP 行,行中帶真綁定 `[test:t_marker_doc_sync]`;換名會被「沒帶來源的 FACT/FLOW/DEP 行」那道擋下,而本案放行後 home check 回 0。⚠ 我沒在臨時 repo 實跑筆記形狀擋,依 `scripts/lumos:3728` 與 `_ns_is_tail_append` 判斷。spec 〈範圍〉「不做」與〈天花板〉都沒講這條互動,對 rtb 的告知也應附「其他行必須自己合格」。

### F5 收窄條件只涵蓋中文,Kotlin/Jest 外其他棧常見的測試名字元會落到天花板而 spec 沒列
severity: minor
blocking: 否 + 只是未列入天花板的已知缺口,走拆提交的既有出口
引句:「值裡有中文或其他字(含方括號)的標記不拿掉,照舊算內容。」
白名單(英數底線點冒號斜線井號@逗號連字號空白圓括號單引號)不含 `[ ] > $ + = * !`:pytest 參數化名稱 `test_x[case-1]`、Jest/Dart 巢狀名稱用 `>` 的標記換名一樣擋。〈天花板〉3 只講了「帶中文說明」。rtb 現存標記全部在白名單內(我掃過 rtb 副本與本 repo `Systems/*.md`,不合的只有 6 個且都是中文或省略號),所以不影響本次解 rtb 的問題;三個月後有人用參數化測試名會再撞一次,且 spec 沒寫這個預期。

整份:最嚴重 minor,blocking 共 0 條。
