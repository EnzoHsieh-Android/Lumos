# 架構對齊審查報告——code-loop-friction r1

материалы: `governance/review-reports/code-loop-friction/r1-docs.patch`(345行)、`r1-code.patch`(176行);比對基準 `docs/lumos-toolchain-knowledge/Projects/迴圈摩擦三修_計劃.md`(v2,d1/d2/d3/d4 + [S1]-[S4] + 例1-5)。

## 判準1:templates.md/SKILL.md 落地 vs spec [S1][S2]/d1/d2 條款

**1a. d1 引句限凍結審材——對齊。**
引句:`格式行**限逐字出自凍結審材**`(r1-docs.patch:41,templates.md 審查員輸出格式段)。對 spec 原句「引句:」格式行限逐字出自凍結審材,一字不差落地。

**1b. d1 佐證通道格式含反引號——對齊。**
引句:`格式固定「file: \`路徑:行號\`」＋敘述`(r1-docs.patch:42)。與 spec d1「格式固定『file: \`路徑:行號\`』——反引號必加」一致;`refcheck 只抽反引號inline-code,漏了連存在性都驗不到`(r1-docs.patch:42-43)的機械理由經查證屬實——file: `scripts/lumos:68`(`INLINE_CODE_RE = re.compile(r"\`[^\`\n]*\`")`)+`scripts/lumos:10846`(`_refcheck_scan` 只用此正則抽 span),確認 refcheck 的抽取管道確實只認反引號包住的 inline code,d1 的技術理由非空話。

**1c. carrier 選席 SOP(templates+SKILL 雙落地)——對齊。**
引句(templates.md,r1-docs.patch:312):`carrier=記帳載體、非證據總集（機制兜底=d5 記帳型態:各席一筆帶 report+sha,僅 carrier 帶三個 set）`。
引句(SKILL.md,r1-code.patch 無涉、見 r1-docs.patch:260):`carrier=記帳載體非證據總集,全輪證據=各席報告 sha 留痕+rN-intake.md`。
兩處措辭一致、與 spec d1「carrier=記帳載體、非證據總集」同義,SKILL 版本略精簡符合「摘要」定位。

**1d. rN-intake.md 收貨留痕慣例+「非全機械」澄清——對齊。**
引句(templates.md,r1-docs.patch:313):`此步為編排者人工判讀+機械留痕,非全機械`。
引句(SKILL.md 步驟4,r1-docs.patch:256):`此步是人工判讀+機械留痕,不是全機械`。
兩處都遵守 spec d1「收貨段行文要明寫,別掛進『全機械』三道裡」的要求,且都放在「三道之外(非取代)」的獨立位置,沒有被誤掛進 quote-check/refcheck/seat-check 三道機械清單裡——比對 SKILL.md 步驟4 原文「收貨三道(全機械,錨不到的不採信)」的既有標題(context line,未被patch觸碰),新增的 rN-intake 條目確實掛在標題之外的第四個 bullet。

**1e. 正本歸屬(templates 權威、SKILL 摘要,不另立)——對齊。**
SKILL.md 步驟4新增句明寫「判準與 MISS 處置見 templates.md〈編排者判讀規則〉」(r1-docs.patch:256),把 HIT/MISS 判準與 MISS 處置細節的權威留在 templates.md、自己只放摘要,沒有重複展開。既有聲明句「派工的完整 prompt 在同目錄 \`templates.md\`(派工以它為準)」(SKILL.md 頭部,context line,未被本次 diff 觸碰)維持原樣,沒有另立新聲明。

**1f. d2 前掃第四類+分流+升級規則——對齊。**
引句(SKILL.md 步驟2,r1-docs.patch:250):`語意類命中=修真檔+逐條(含修改前→後對照)寫進 rN-intake.md 留痕;動到「核心裁定」節的=升級為正式 finding 交席位審,前掃不得自行改裁定`。
逐條核對 spec d2:分流規則(存在類直接修/語意類留痕)、before-after 對照要求、動核心裁定節升級規則——三項全部逐字或近逐字落地,無遺漏、無走樣。

**1g(minor 觀察,blocking:否). 落地額外觸及 spec [S3] 未列舉的兩處(Systems/design-loop.md 新 KEY、`Verification/2026-08-25_設計審收斂重定義落地.md`〈誠實邊界〉bullet 改寫)。**
spec [S3] 明列三個寫回目標(設計審收斂重定義落地 KEY、連鎖佇列計劃句、decision-add),但 r1-docs.patch 另外改了 `Systems/design-loop.md`(新增 verified_by 連結+一行 KEY,r1-docs.patch:150-153)與該 Verification 檔的〈誠實邊界〉bullet(把「d3 血緣帳...寫入端未建」改成「✅...gov --stats 重寫桶=1」,r1-docs.patch:198-199)。
判準:這兩處不是「引入第二種做法」,是既有 verified_by 反向連結慣例(該 Systems 頁面既有 KEY 清單每筆都對應一篇 Verification,新增一筆同形狀)+糾正一句會變成過期矛盾的舊宣稱(若不改,該 bullet 會與同一天已落地的 rewrite 端點事實衝突,違反 CLAUDE.md「行為事實和圖譜衝突查清哪邊錯」的鐵則)。內容本身經實跑查證屬實(見判準3)。severity 定為 minor、非 blocking。

## 判準2:行為斷言例1-4 實跑驗收

**例1(templates.md)——對齊。**
`grep -n "限逐字出自凍結審材" skills/lumos-design-loop/templates.md` → 命中 line 41;`grep -n 'file: \`' skills/lumos-design-loop/templates.md` → 命中 line 42。落地前版本(`git show ee53d68:skills/lumos-design-loop/templates.md`)兩字串 grep -c 皆為 0,與 spec「兩字串現檔皆 0 命中,落地後 >0」的鑑別力斷言相符。

**例2(SKILL.md 驗語意/不只驗存在)——對齊。**
現檔命中 `skills/lumos-design-loop/SKILL.md:19`;落地前版本 grep -c 兩字串皆 0。

**例4(SKILL.md rN-intake)——對齊。**
現檔命中兩處:`skills/lumos-design-loop/SKILL.md:19,25`;落地前版本 grep -c 為 0。

**例3(SKILL.md 重寫出口段一字不動)——對齊,以 git diff 驗證。**
file: `skills/lumos-design-loop/SKILL.md:44` 現仍為 `**重寫出口(人裁選項,非自動)**:單輪 blocking 密度極高(暫用門檻 >1 條 blocking/300 字,本專案自定 heuristic、未實測校準,校準前只當攤人建議訊號)...`——「300 字」「暫用」均在。
機械驗證:r1-docs.patch 對 SKILL.md 只有**一個** hunk,標頭 `@@ -9,29 +9,30 @@`,涵蓋舊檔第 9-37 行 / 新檔第 9-38 行;而重寫出口段位於新檔第 44 行,落在該 hunk 範圍**之外**——不是靠肉眼比對文字沒變,是 hunk 的行號區間本身就沒觸及第 44 行,機械上不可能改到它。與 spec d3「本案不動現行重寫出口」的回縮裁定完全一致。

## 判準3:寫回五處一致性 + 可實跑宣稱

**gov --stats 重寫桶=1——對齊,實跑確認。**
執行 `./scripts/lumos gov --stats`,輸出行:「審查迴圈結案方式(只算有記帳的 16 個編號):閘過了 12 個、跑滿上限沒過關(人裁放行) 3 個、**人裁判整份重寫收尾 1 個**——人裁放行率 19%」。與 `Verification/2026-08-25_迴圈摩擦兩修落地.md`(r1-docs.patch:218)「gov --stats 重寫桶=1」逐字對得上。

**兩守衛紅轉綠——對齊,實跑確認。**
`python3 scripts/test_lumos.py -k t_command_index_complete` → 14 passed, 0 failed;`-k t_every_subcommand_has_when` → 1 passed, 0 failed;兩者當前皆綠,且斷言內容(「每個頂層子指令都在索引裡有『什麼時候用』」「每個子指令 --help 都有『什麼時候用』」)正是 spec d4 提到「子命令未進指令索引與『什麼時候用』字典」兩支守衛。順帶跑 `-k t_loop_rewrite_mark` → 4 checks 全綠,confirm code patch 的 rewrite 端點測試現實有效。

**五處內容互相一致——對齊。**
`設計審收斂重定義_計劃.md` decisions d3(r1-docs.patch:16-21)、`連鎖佇列軟提醒_計劃.md` 下一步句(r1-docs.patch:134)、`Verification/2026-08-25_設計審收斂重定義落地.md` 校準 KEY(r1-docs.patch:179)、`Systems/design-loop.md` 新 KEY(r1-docs.patch:152)、新檔 `Verification/2026-08-25_迴圈摩擦兩修落地.md`(r1-docs.patch:213-233)——五處講的都是同一件事(雙訊號嘗試已試並撤回、密度門檻與 2 條/300 字校準結論維持),用詞和事實互不矛盾,查詢通道(`lumos decisions`)可查得到該 decision,沒有發現任一處寫錯目標檔或內容漂移(spec r1 折入時明確訂正過「[S3] 目標句寫錯檔」這個舊問題,本輪未見重犯)。

**code patch 與 docs 的一致性——對齊。**
r1-code.patch 的 HELP_WHEN 條目(引句,r1-code.patch:72)「後收尾:記 rewrite 事件+血緣(prev/successor)進治理帳;連續第二次判重寫會警告強制攤人」與 r1-docs.patch 的 commands/05 索引行(引句,r1-docs.patch:339)「記 rewrite 事件+血緣進治理帳;連續第二次判重寫會印強制攤人警告」描述一致,且都對應 file: `scripts/lumos`(現檔內 `cmd_loop_rewrite` 函式,經比對與 patch 內容逐字相同)。`lumos loop rewrite` 端點屬 spec d4「不佔本案條款」的既有交付物,本輪只補了索引/HELP_WHEN,未變更端點行為本身,與 d3「不動重寫出口 heuristic」不衝突(兩者是不同層——一個是人裁後的記帳指令,一個是 SKILL.md 裡的門檻文字)。

## 總結

25 項核對(1a-1g + 例1-4 + gov/守衛/五處一致/code-docs 一致)中,**24 項對齊,1 項 minor 觀察(blocking:否)**。最嚴重 severity = minor;blocking 共 **0 條**。未發現條款漏落地、落地走樣、引入第二種做法、或寫回內容與 code 實跑現實矛盾的情形。