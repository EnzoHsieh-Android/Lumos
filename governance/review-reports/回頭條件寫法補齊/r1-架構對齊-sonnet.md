severity: major

總評:分層與依賴方向(第 1 問)大致對齊;問題集中在第 3 問(第三種「關掉提醒」機制)與幾處小的命名、呈現、落點不一致。對照基準:scripts/lumos 的 `_revisit_split`、`_revisit_lines`、`_probe_lines`、`_probe_parse`、`_ns_revisit_violations`、doctor E5、`_retire_lines`、`cmd_drift_ack`。

## 逐問回答

1. 分層與依賴方向:對齊。
   - 新判定 `_revisit_misplaced` 建在 `_revisit_split` 之上,由第一層(`_ns_revisit_violations`)與 doctor E5 共用,跟既有「判定只有一支、三處共用」同一個方向(scripts/lumos:31700、27915、2303;Systems/存量漂移守衛.md:97)。沒有看到跨層直呼。
   - 小偏差見 Z3、Z4。
2. 命名與錯誤處理:規則名「回頭條件寫在句中」「結案標記寫錯」跟鄰居「回頭條件格式不合」「條件寫錯」「條件寫在不評估的地方」同一種短語型;回傳形狀 `[(規則, 片段, 改法)]` 也同(scripts/lumos:27915-27950)。E5 治理帳 note 加 `misplaced=N` 跟 `due=N bad=M` 同型(scripts/lumos:2326)。小偏差見 Z3、Z4、Z5。
3. 第二種做法:有,見 Z1(major)與 Z2。
4. 落點:見 Z6。

## Findings

**Z1 `[closed:]` 是第三套「關掉提醒」機制,跟 `drift ack`、`[status:superseded]` 並存**
severity: major
⚠
blocking: 是 — 引入第二種做法(已有兩套「這條處理完了、不要再唸」的機制,本案加第三套);⚠ 因為計劃〈做法〉2-4、2-5 有寫為什麼不合併,是明知故犯而不是漏看,最終取捨要判定者裁。
引句:「不把兩者合併:合併等於讓表態檔變成第二個存放回頭條件狀態的地方,讀筆記的人看不到。」
對照 file:
- scripts/lumos:32715(`cmd_drift_ack` 的表態檔,對條件式回頭條件已能「照留」)
- scripts/lumos:31866-31880(`_retire_lines` 在抽取層就跳過 `[status:superseded]` 的行,正是「標了就不再評估、不再擋」的既有做法;`_ns_superseded` 在 scripts/lumos:28512)
- 計劃自己承認「條件式的兩種都能用」,等於同一件事(條件式不再需要)有兩個入口。
說明:`_retire_lines` 的做法(在抽取函式裡跳過已標記的行)跟本案「`_probe_lines` 不抽它」其實是同一個模式,這點是對齊的;不對齊的是標記本身又開了一種形狀。計劃的理由(REVISIT 不套格子、`superseded` 語意不夠)成立一半:日期式確實沒有既有出口,條件式則跟 `drift ack` 重疊。建議至少把條件式的範圍收窄(條件式已成立一律走 `drift ack`,`[closed:]` 只給日期式),或在計劃寫明兩者擇一的判準並讓 `drift ack` 對 `[closed:]` 行回報「已結案」,避免兩處各自靜音同一條。

**Z2 `[closed:]` 號稱「照 `[by:]` 的形狀」,位置規則卻不一樣**
severity: minor
blocking: 否 — 命名/錯誤處理不一致但結構對。
引句:「位置:日期式放在日期之後、條件式放在條件標記與 `[by:]` 之後,行內任一處都行(通常接在行尾)。」
對照 file: scripts/lumos:31694(`_PROBE_TOKEN_RE`)、scripts/lumos:31697(`_PROBE_LEAD_RE`)、scripts/lumos:31804-31840(`_probe_parse`)。
說明:`[by:]` 與 `[when-*]` 只在 REVISIT: 後面「從開頭連續吃」,中間穿插別的字就停;`[closed:]` 允許「任一處」,是另一種定位規則,需要另寫一支掃描。另外日期式的摘要是 `rest.partition(" ")` 之後的字(scripts/lumos:31735),`[closed:]` 留在摘要裡會被當成摘要印進 E5 的「到期」行;不過因為已結案的整行會被排除,實際無害。建議改成跟 `[by:]` 一樣「緊接在日期/條件標記之後的連續標記」,同一支 `_PROBE_TOKEN_RE` 擴一個鍵就行,不另寫掃描。

**Z3 句中 REVISIT 的存量放 E5,而「寫了卻不被讀」的既有同類發現放 doctor Z**
severity: minor
blocking: 否 — 呈現位置不一致,結構沒壞。
引句:「E5 掃每篇的可見行時多數一種「寫在句中、不會到期」的行(正文、摘要、開頭欄位其他欄都算),在 E5 的開頭行加一句「另有 N 行 REVISIT 寫在句中、表格或開頭欄位其他欄,永遠不會到期——搬成獨立一行」,並列前 5 個位置」
對照 file:
- scripts/lumos:34806-34815(`_drift_doctor_lines` 用 `_probe_lines` 的 `dead` 回傳,把「條件寫在不評估的地方」放 Z 段,同一類「寫了不會被讀」)
- scripts/lumos:2303-2315(E5 迴圈用 `_revisit_lines`,只回 REVISIT 行,不含摘要以外的開頭欄位,也沒有區段資訊;`_notelines_regions` 才有,在 `_probe_lines` 用,scripts/lumos:31850 附近)
- scripts/lumos:1383-1397 與 2326 附近注解 H-2(計數進 head、不進 lines,因為 `warn_soft` 每段最多 3 條 `_SOFT_CAP`)
說明:三點不對齊。①既有「寫在不評估的地方」由 `_probe_lines` 回傳 `dead` 再由 Z 段呈現,本案另在 E5 呈現同類;至少要說明為什麼不跟 `dead` 同處。②E5 目前拿不到區段與開頭欄位,要看「開頭欄位其他欄」就得另跑一個帶區段的掃描,等於在 E5 迴圈外再寫一支類似 `_probe_lines` 的逐行迴圈,應改成擴充 `_probe_lines`(或與它共用抽取)。③計劃要「列前 5 個位置」,但 E5 既有慣例是把數量放 head、清單受 `_SOFT_CAP`=3 限制,列 5 個會被截成 3 加「另 N 條」,且 E5 開段條件 `if _rv_due or _rv_bad` 也得加上 misplaced,否則「全靜默」的描述對不上現有程式。

**Z4 `_revisit_lines` 加一個「兩個既有呼叫端都排除」的參數,是死參數**
severity: minor
blocking: 否 — 錯誤處理/介面慣例,結構沒壞。
引句:「E5 與 Issue 結案列出走 `_revisit_lines`,讓它多一個參數決定要不要排除已結案的(預設排除;兩個既有呼叫端都排除)。」
對照 file: scripts/lumos:31721-31736(`_revisit_lines`)、scripts/lumos:2303、scripts/lumos:31749;既有教訓見 scripts/lumos:34830 附近「抄了參數不用是死參數」(代碼審 r3 架構對齊席)。
說明:兩個呼叫端都用預設,新參數沒有任何使用者;若要保留「未結案也看得到」的路徑應指出誰要用(例如一個尚未列在計劃裡的稽核),否則直接在 `_revisit_lines` 內排除即可。另外 `_revisit_closed(probe)` 回 `(原文, 錯誤說明清單)` 的二元組,跟 `_probe_parse` 回 dict(conds/by/errs/bad)的形狀不同,建議沿用 dict 的 `errs` 欄命名,讓第一層的錯誤拼接(scripts/lumos:27927-27935)寫法一致。

**Z5 理由「至少 4 個實字」說照 `_excluded_line` 的算法,但那個算法沒有獨立函式可呼叫**
severity: minor
blocking: 否 — 重複實作風險,尚未發生。
引句:「至少 4 個實字(字母、數字或漢字,標點與空白不算;照「已排除」行理由的既有算法 `_excluded_line`,不照 `drift ack`」
對照 file: scripts/lumos:6396-6408(算法是 `_excluded_line` 內嵌的 `len(re.findall(r"[^\W_]", reason)) >= 4`,沒有拆出);`drift ack` 的檢查在 `_drift_ack_args_err`(scripts/lumos:32718 呼叫處)。
說明:計劃沒說是抽出共用小函式還是複製一份。複製就是專案裡第三份「實字計數」,建議明寫抽出共用並讓 `_excluded_line` 與 `_revisit_closed` 都呼叫。

**Z6 落點:lands_in 列了兩篇,但〈說明與同步〉只寫其中一篇;WHY 該放的位置與既有鄰居不同**
severity: minor
blocking: 否 — 落點建議,不影響程式結構。
引句:「[[Systems/存量漂移守衛]] 補一行 WHY(為什麼擋句中、為什麼結案寫在行內不放表態檔);[[Systems/筆記內容閘]] 的規則清單由程式答得了,不寫。」
對照 file:
- docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md:29(既有 REVISIT 第一層新規則的 WHY 在這一篇:「新寫的 REVISIT 行也在這一層擋…」)
- docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:38、:97(條件式必帶期限的 WHY 與「這行是不是 REVISIT 只有一支判定」在這一篇)
- 計劃 frontmatter `lands_in` 兩篇都列。
說明:①「為什麼提交時擋句中」是第一層新規則的 WHY,鄰居(S10 的 WHY)已經在筆記內容閘,新的也應寫在那裡,而不是放存量漂移守衛;②「結案寫行內不放表態檔」「E5 列出句中」屬存量漂移守衛。所以應該是兩篇各補一行 WHY(既有那兩篇,不另開),且 `lands_in` 與正文要一致:要嘛筆記內容閘也寫,要嘛從 lands_in 拿掉。另外兩篇的 responsibility 都沒提 E5,建議計劃一併決定 E5 的家是存量漂移守衛(它已在 :97 講 E5 判定),並在 responsibility 補一句。

不對齊共 6 條,其中 major 1 條
