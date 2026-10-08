severity: major

審查立場:極端輸入代言人。對照碼:`scripts/lumos`(rw 副本)。實驗在 /tmp/revisitA-r1/x/t.py(載入 lumos 模組直接呼叫 `_revisit_split`、`_probe_parse`、`_revisit_lines`、`_notelines_regions`)。文件內部交叉引用(7 篇節點、`t_graph_discipline_negation_revisit`、`03-寫回圖譜.md`、`_excluded_line`、`_esc_clean`、`_issue_close_revisits`、`_probe_lines`)都核對存在。

## 〈依據〉〈範圍〉〈做法 1〉〈做法 2〉〈做法 3〉〈實務隱患〉〈驗收條款〉〈回退〉〈天花板〉逐節結果

**B1 結案標記「行內任一處都行」與程式的行首解析矛盾,放中間會讓條件式失去期限**
severity: major
blocking: 是 — 照字面實作,作者依規格寫的合法位置會被第一層誤擋或被 E5 靜默跳過
引句:「位置:日期式放在日期之後、條件式放在條件標記與 `[by:]` 之後,行內任一處都行(通常接在行尾)」
1. 位置:〈做法 2〉第 1 點。同一句前半說「放在條件標記與 `[by:]` 之後」、後半說「行內任一處都行」,自相矛盾。
2. 問題:`_probe_parse` 只從 `REVISIT:` 後面「連續」吃 `[when-…]`、`[by:…]`,遇到第一個不認得的方括號就停(`_PROBE_TOKEN_RE` 只認 when-* 與 by)。結案標記夾在條件與 `[by:]` 之間,後面的 `[by:]` 就讀不到。
3. 具體例子:
   - 輸入 `REVISIT:[when-file:a.py][closed:2026-10-03 已改用新閘][by:2026-12-31] t` → 實測 `_probe_parse` 回 `by: None`;第一層 `_ns_revisit_violations` 會補上「沒帶期限」報「條件寫錯」,E5 對 cond 且無日期的行直接 `continue`。作者寫了合規位置之一,卻被擋。
   - 輸入 `REVISIT:2026-10-05[closed:2026-10-03 已改用] x`(日期與標記黏著)→ `_revisit_split` 回 `bad`,因為取到空白為止的字串是 `2026-10-05[closed:2026-10-03`,fromisoformat 失敗。
   - 輸入 `REVISIT:[closed:2026-10-03 已改用][when-file:a.py][by:2026-12-31]` → 實測回 `bad`(開頭不是 `[when-`)。
4. 查證:file: `scripts/lumos:31694`(`_PROBE_TOKEN_RE`)、`scripts/lumos:31700`(`_revisit_split`)、`scripts/lumos:31804`(`_probe_parse`)。規格要嘛限定位置(只准行尾,並寫驗收條款),要嘛讓 `_probe_parse` 與日期解析跳過結案標記;現在兩者都沒寫,驗收 S6–S8 也沒涵蓋非行尾位置。

**B2 「結案日期在提交當天之後」用本機日期,CI 跑在 UTC,台北使用者每天約八小時會被 CI 擋掉合格的結案日**
severity: major
blocking: 是 — CI 擋下的出口只有改日期或改專案開關,`LUMOS_SKIP_NOTE_SHAPE` 在 CI 無效
引句:「時區差一天可能誤擋或誤放,寫法是結案日寫當天,影響極小。」
1. 位置:〈實務隱患〉跨環境、〈做法 2〉第 3 點。
2. 問題:規格自己說推送前與 CI 的 `note-shape --diff` 走同一支。CI 是 `ubuntu-latest`(UTC),本機在 UTC+8。
3. 具體例子:台北使用者 2026-10-03 07:00 提交,寫 `[closed:2026-10-03 已改用新閘道]`(照規格「寫當天」)。本機通過。CI 在 UTC 是 2026-10-02 23:00,檢查「日期在當天之後」→ 10-03 > 10-02 → CI 紅。這不是「差一天偶爾」,而是每天 00:00–08:00(台北)的固定窗口,且 CI 的規則是硬擋。規格把「影響極小」當結論,沒有給容忍(例如允許 +1 天)或改用提交時間戳。
4. 查證:file: `.github/workflows/ci.yml:11`(`runs-on: ubuntu-latest`)、`.github/workflows/ci.yml:141`(CI 跑 `note-shape --diff`);既有慣例 `date.today()` 見 `scripts/lumos:2292`。⚠ 我沒有實際在 UTC 機器跑,結論由時區算術得出。

**B3 開頭欄位的 YAML 清單項寫 `- REVISIT:日期`,E5 當有效、第一層規則卻說「其他欄都不會被讀到」**
severity: minor
blocking: 否 — 只影響警告用語與 S2 的邊界,不影響已有行為
引句:「寫在句中、表格或開頭欄位其他欄都不會被讀到。」
1. 位置:〈做法 1〉第 2、3 點與 S2。
2. 問題:`_revisit_lines` 不看區塊,只剝圍欄與行內程式碼,所以開頭欄位裡 `  - REVISIT:2026-01-01 x` 這種清單項,`_revisit_split` 回 `date`,E5 照常算到期。規格卻把「開頭欄位其他欄」整類宣告為死的。
3. 具體例子:
   - 實測 `---\nrelated:\n  - REVISIT:2026-01-01 x\n---` 的 `_revisit_lines` 回 `[(4,'date','2026-01-01','x',…)]`,`_notelines_regions` 該行為 `other`。
   - 輸入 `other: 見 REVISIT:2026-10-05` → 第一層報「寫在句中」。
   - 輸入 `  - REVISIT:2026-10-05` 同區塊 → 若第 1 點的「`_revisit_split` 判不是」為前提則不報(split 回 date),若 S2 的「開頭欄位其他欄」是直接用正則則報,但它同時被 E5 計為有效回頭條件。規格沒說用哪一個。
   - 縮排四格以上(`    REVISIT:2026-10-05 x`)同樣被當有效,而 CommonMark 視為程式碼區塊。這是既有行為,但本案新規則的「死」「活」界線因此與使用者直覺不符。
4. 查證:file: `scripts/lumos:31721`(`_revisit_lines`)、`scripts/lumos:27214`(`_notelines_regions`)。

**B4 E5 要找句中行,但 `_revisit_lines` 只回 REVISIT 行且不帶區塊,規格沒說掃描怎麼走;「多一個正則」低估成本**
severity: minor
blocking: 否 — 可實作,但規格留白,實作者會各自發明第二份逐行掃描
引句:「E5 掃每篇的可見行時多數一種「寫在句中、不會到期」的行(正文、摘要、開頭欄位其他欄都算)」
1. 位置:〈做法 1〉第 3 點、〈實務隱患〉效能。
2. 問題:E5 現在只呼叫 `_revisit_lines(_txt5)`,它對非 REVISIT 行直接 `continue`,沒有區塊資訊。要分「正文/摘要/表格/開頭欄位其他欄」就得另呼叫 `_notelines_regions`(再跑 `split_frontmatter`)與第二輪 `_visible_lines` + `_strip_inline_markup`,630 多篇都要。規格只寫「多一個正則」,也沒說新函式簽名(`_revisit_misplaced(probe)` 只收一行文字,看不到是否表格或哪個區塊)。
3. 具體例子:實作者若讓 `_revisit_lines` 回傳所有可見行以配合,會破壞「兩個既有呼叫端」的簽名;若另寫一支,就是違反檔內「全檔唯一」註解警告的第二份可見行判定。
4. 查證:file: `scripts/lumos:31721-31736`、`scripts/lumos:2303`。

**B5 E5 對 68 行存量永遠印出,且仍寫治理帳事件,與同檔 Z 段「存量不寫帳以免被 nags 升級成噪音」的原則相反;「前 5 個位置」又被軟段上限 3 截斷**
severity: minor
blocking: 否 — 屬噪音與用語不實
引句:「並列前 5 個位置(`節點:行號`,過 `_esc_clean`)」
1. 位置:〈做法 1〉第 3 點、S5、S10。
2. 問題:
   - 我用粗略規則數 toolchain 圖譜,句中 REVISIT 行 68 條(與規格自述相符)。上線當天起,每次 `doctor` 都印 E5,且 `gov_events` 每次追加 `check-revisit warned`(`hard: False`),規格要求在 note 加 `misplaced=N`。Z 段的註解明寫「不寫治理帳——這些是存量,每天唸同一批會被 nags 升級成噪音」。E5 的 `nodes` 只填到期 stem,句中行 stem 沒進 `nodes`,nags 以 gate+node 升級的機制抓不到,但事件本身每天一筆。
   - `warn_soft` 預設每段只顯示 3 行(`_SOFT_CAP`),其餘收成「另 N 條」。「前 5 個位置」若放在行裡,實際只看到 3 個;若放進 head,又與既有 head 的「N 件到期…」「壞損」兩句拼接,長度未定。
3. 具體例子:到期 0、壞損 0、句中 68 → 段落印出,行數 5 但畫面 3 行加「另 2 條」。
4. 查證:file: `scripts/lumos:1383-1397`(`warn_soft`)、`scripts/lumos:2338-2342`(gov 事件)、`scripts/lumos:2345`(Z 段註解)。

**B6 `[closed:` 出現在「不是 REVISIT 的行」就硬擋,會誤傷一般散文,且舊行重編輯也被擋**
severity: minor
blocking: 否 — 有跳過出口,但消費專案會被外溢
引句:「寫在不是 REVISIT 的行(那行不會被任何工具讀,寫了等於沒寫)」
1. 位置:〈做法 2〉第 3 點、S8。
2. 問題:規則把任何含 `[closed:` 的可見行都當「結案標記寫錯」,不看是不是結案語意。消費專案的筆記常見 changelog/追蹤式寫法 `[closed: #123]`、`[closed: duplicate]`,第一層規則是整行層級、`_ns_append_subtract` 只扣 `_NS_FRAG_KEY_RULES`,所以舊行補括號也被擋。本 repo 目前 `[closed:` 零出現(grep docs/scripts/skills 僅本計劃),所以量測看不出外溢。
3. 具體例子:消費專案某行 `- 修好登入 [closed: 2026-09-01 已合併]` 在正文 → 報「結案標記寫錯」並要求搬成 REVISIT 行,但這行根本不是回頭條件。
4. 查證:file: `scripts/lumos:27694-27730`(`_ns_append_subtract` 預設不扣)。

**B7 不合格的結案標記在 E5、`_probe_lines`、Issue 列出的處置沒定義**
severity: minor
blocking: 否 — 只在 `--no-verify`/跳過後才出現
引句:「這幾處共用一支 `_revisit_closed(probe)` → (結案標記的原文, 錯誤說明清單)」
1. 位置:〈做法 2〉第 2 點與 S6、S7、S9。
2. 問題:`_revisit_closed` 回「原文 + 錯誤清單」,但驗收只寫「合格的」才靜音。標記有錯(日期在未來、理由 3 字、兩個標記)時,E5、`_probe_lines`、`_issue_close_revisits` 是視為已結案、視為未結案,還是回報壞行,沒說。另外 `bad` 種類加 closed(例如日期壞了又寫結案)也沒說。
3. 具體例子:被 `LUMOS_SKIP_NOTE_SHAPE` 放行的 `REVISIT:2026-09-01 x [closed:2026-12-31 好]`(未來日期、1 字理由):E5 若照「有標記就靜音」會被一行垃圾關掉提醒;若照「不合格就不算」則 E5 照唸,但作者看不到為什麼,除非 E5 另報。規格要寫死一邊,並補一條驗收。
4. 查證:file: `scripts/lumos:2303-2316`(E5 迴圈)。

**B8 第 1 點判定與工具既有解析在空白、巢狀記號上不一致,改法提示會誤導**
severity: minor
blocking: 否 — 屬判定邊界與提示用語
引句:「搬成獨立一行(行首寫 `REVISIT:`,前面可以有列表記號)」
1. 位置:〈做法 1〉第 1、2 點。
2. 問題與實測(`_revisit_split`):
   - `- [ ] REVISIT:2026-10-05 x` → None(核取方塊清單常見)。改法說「前面可以有列表記號」,作者留著 `- ` 只去掉其他字照舊被擋或被當句中,提示沒說核取方塊不行。
   - `> - REVISIT:2026-10-05 x`(引用裡的清單)→ None,同樣被報句中,而規格的〈依據〉第 33 點說「去一層列表或引用記號」,作者自然以為合法。
   - `**REVISIT:2026-10-05** x` → None。
   - 中間句 `… REVISIT: 2026-10-05 …`(冒號後有空白)依規格第 1 點「可隔空白」算命中,但同樣內容放行首,`_revisit_split` 判 `bad`(空白算壞損),兩邊對「冒號後空白」的態度相反;作者依改法搬到行首後又換成「格式不合」的新報錯。
3. 查證:file: `scripts/lumos:31693`(`_REVISIT_MARK_RE`)、`scripts/lumos:31700`。

**B9 結案標記語法細節沒定:理由含 `]`、未閉合反引號、CRLF**
severity: minor
blocking: 否 — ⚠ 規格沒給正則,以下是對照既有 `_PROBE_TOKEN_RE` 慣例(`[^\]\n]*`)的推論
引句:「理由要寫為什麼不用再回頭(附提交或測試更好),至少 4 個實字」
1. 位置:〈做法 2〉第 1、3 點。
2. 問題:
   - 理由含圖譜最常見的 `[[節點]]` 連結時,照既有 `[^\]]*` 風格會在第一個 `]` 截斷,理由變成 `見 [[Systems/x`,字數照過、內容殘缺;規格沒說允許與否。
   - 未閉合的反引號之後,`_strip_inline_markup` 整段截掉(實測 `REVISIT:2026-10-05 x \`unclosed [closed:2026-10-03 ok ok]` 回 `REVISIT:2026-10-05 x `),結案標記在可見文字裡消失,既不生效也不報錯。
   - 「4 個實字」照 `_excluded_line` 用 `[^\W_]`,純數字或重複字母也過(`2026`、`abcd`),規格已自承只看寫法(天花板 3),此點只提示不另算缺陷。
   - CRLF:`line.strip()` 會吃掉結尾 `\r`,實測日期式、條件式行都正常;全形 `【closed：】` 不認,屬天花板 1 同類,不報。
3. 查證:file: `scripts/lumos:368-381`(`_strip_inline_markup`)、`scripts/lumos:6396-6405`(`_excluded_line`)。

## 實務隱患鏡頭(逐類)

- 併發:無 — 只讀筆記文字,不寫檔;治理帳走既有寫入器(同規格)。
- 效能:見 B4。第一層每行多一次 `_revisit_split` 與一個正則,線性、無回溯;超長行不放大。E5 要多算區塊與第二輪可見行,630 篇量級可接受,但規格的「多一個正則」說法不準。
- 回滾:無新問題 — 還原提交即可;已寫的 `[closed:]` 變成普通文字,但回到第一層後它在非 REVISIT 行不再擋(因規則消失)。
- 誤擋與繞過:見 B1(合法位置被擋)、B2(CI 時區)、B6(散文誤傷)、B8(提示誤導)。繞過路徑規格已自承(全形冒號、斜線日期)。
- 守衛面:`drift ack` 把表態綁在「行原文」,在存量條件式行補 `[closed:]` 會改變原文,既有表態失聯,規格未提;因 closed 之後該行不再被評估,影響有限,故併入 B7 的未定義處置不另立條。

最嚴重 severity 是 major,blocking 共 2 條(B1、B2)。
