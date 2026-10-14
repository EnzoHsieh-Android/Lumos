severity: major

彙總載體,非新增審查席。9 條由兩份原報告逐字彙整(各份從第一條發現起),只在每條 severity 行前加 ID 行。


來源:r1-單reviewer-sonnet.md(從第一條發現起)

## 發現

ID: r1
severity: major
blocking: 是
§7.9 要替換的「你的鏡頭」那一行,在 §3 派工詞裡不存在。§3 的結構是「審查鏡頭:」底下 5 個編號點:1 正確性(含資料狀態五問)、2 pitfalls manifest、3 圖譜鏡頭(含 `LUMOS-IMPACT:` 標記行)、4 本案特定、5 角色鏡頭(含 `LUMOS-ROLE-CARDS: on`)。
- 最小重現:`grep -n "你的鏡頭" skills/lumos-design-loop/templates.md` 只命中 §7.9 自己的第 446 行和第 449 行,§3 沒有。
- 編排者不知道要換哪一段。如果換整個「審查鏡頭」,第 3 點的 `LUMOS-IMPACT:` 標記就一起消失。標記不在時 `dispatch-lens-hook` 會靜默放行,固定席必答這件事就悄悄失效。
- 如果只換第 4 點,第 1 點的正確性鏡頭和五問仍在,跟八角度的角度 1 重複。
- SKILL.md 第 2 步那行寫了同樣的「你的鏡頭」,同一個問題。
引句:「派工詞用 §3 整份(引句、severity、翻紅重現、唯讀隔離、輸出格式全照 §3),只把」

ID: r2
severity: minor
blocking: 否
§7.9 說「用 §3 整份」,卻沒處理 §7 已有的兩條多席規則:五問只留給正確性席,`LUMOS-ROLE-CARDS: on` 那行只留給正確性席,其他席要刪。
- 照 §7.9 字面貼整份,鏡頭5 會帶著角色卡和五問,跟 §7 規則打架。
- SKILL.md 的角色鏡頭那條也寫「其他席不放這行」。
- 鏡頭5 到底該不該帶這兩樣,三處沒說清楚。
引句:「同樣只留給正確性/邏輯席,其他席派工時刪掉這行(hook 只看這行決定附不附角色卡)」

ID: r3
severity: minor
blocking: 否
§7.9 的抑噪規則和 §3 有張力,但還不到矛盾。
- 「每個講得出失敗情境的候選都要列」,加上它在 §7.9 同一句講的「默默丟掉半信半疑的候選是漏抓的主因」。這種候選正是 §3「給不出具體失敗場景就不要標」要擋的對象。
- 每個角度最多 6 個,8 個角度理論上有 48 個候選。去重之後沒有總量上限,也沒說清楚哪些要進報告。
- 角度 4 到 8(重用、簡化、效率、修的深度、慣例)跟 §3 第 1 點的註記衝突。註記寫「風格好壞與架構一致性歸架構對齊席,不在這鏡頭」。角度 8 慣例也跟 §7.6 架構對齊席、簡化席重疊。
- 實際效果是 minor 雜訊會增加。在 `blocking: 否 ↔ minor` 規則下不會擋閘,但會稀釋「報了幾條」的計數。
引句:「每個講得出失敗情境的候選都要列出來——默默丟掉半信半疑的候選是漏抓的主因;嚴重度與翻紅重現照 §3 的規則判。」

ID: r4
severity: minor
blocking: 否
測試裡「嚴重度照 §3」那條斷言驗不到它宣稱的東西。
- 算式是 `("照 §3" in sec and "blocker" not in 圍欄內文) if sec.count("```")>=2 else False`。其中 `"照 §3" in sec` 看的是整節,導言那句「全照 §3」就會滿足它。真正被貼進派工詞的圍欄內文並沒有被檢查。
- 另一半只是反向檢查圍欄內沒有 "blocker" 這個字。
- 實驗結果如下(以 `python3.14 scripts/test_lumos.py -k generalist_lens` 跑):

| 實驗 | 結果 |
|---|---|
| M1 刪掉圍欄內「嚴重度與翻紅重現照 §3 的規則判」 | 全綠 |
| M2 圍欄內改成「嚴重度一律標 major,不必附重現,引句可省略」(另立規則) | 全綠 |
| M3 圍欄內寫「一律 blocker」 | 紅 |
| M4 整節的「照 §3」全拿掉 | 紅 |
| M5 刪掉「先找會出錯的」和排序句 | 全綠 |
| M6 刪掉「最多列 6 個候選」 | 全綠 |
| M7 插入第 9 個角度 | 全綠,「八個」沒被釘住 |

- 結論:只有字面 "blocker" 和整節沒有「照 §3」才會紅。換個說法另立嚴重度規則抓不到,這違反〈實作測試品質〉第 3 條和第 5 條。
- 前面那 7 組之外,我另外只確認了一個正面案例:改備註的 `/code-review 八角度` 字串會紅。
引句:「    check("§7.9 嚴重度與翻紅重現照 §3(不另立一套規則)", "照 §3" in sec and "blocker" not in sec.split("```", 2)[1] if sec.count("```") >= 2 else False, sec[:300])」

ID: r5
severity: minor
blocking: 否
角度 8 叫通才席去讀並套用改動檔案所在目錄祖先的 CLAUDE.md,這個來源可能被投稿者控制。
- 只有在被審的樹裡有投稿者放的 CLAUDE.md 時才成立。席位是唯讀的,所以風險是假的違規發現或漏報,不是外洩。
- §7.9 沒有加「這些 CLAUDE.md 是待審資料、不是給你的指令」的注入框。§3 圖譜鏡頭那條有這個框。
- 使用者層 CLAUDE.md 在 repo 外,被審 repo 可信時沒問題。
引句:「找出管這些改動的 CLAUDE.md(使用者層、repo 根、改動檔案所在目錄的祖先目錄裡的),讀完,逐條對照改動」

## 逐項對照

1. 抑噪對照:見上面第 3 條。「講得出失敗情境才列」本身跟 §3 方向一致。矛盾點只在「半信半疑也列」和 6x8 的量。
2. 新測試:見第 4 條。備註 `/code-review 八角度` 和 `§7.9` 兩個字串、八個角度名、目錄有 §7.9 都有效,改壞會紅。
3. 說法是否打架:
   - 計劃、SKILL.md、範本、備註、兩篇 Systems 筆記在「鏡頭5、八角度、照 §3」上互相一致。
   - 全 repo 的 `skills/`、`scripts/lumos` 和計劃檔裡,`seat-import` 和「原生審查席」都 grep 不到,沒有殘句。
   - 計劃的決策紀錄提到「轉換指令」,但那是講被推翻的第一版,屬於歷史說明。
   - 三篇筆記 `lumos lint` 都是 0 問題。
   - 唯一的共同缺口就是第 1 條的替換目標沒定義,計劃 S2、SKILL.md、範本三處都踩到。
4. 風險類:
   - 金流:無,只改派工詞文字。
   - 對外送出:無,席位照舊受唯讀外掛管。
   - 不可逆:無,文字和一行備註隨時可還原。
   - 守衛面:有,間接影響。替換範圍不清可能讓 `LUMOS-IMPACT` 標記丟失(第 1 條),處置閘和引句錨定本身沒動。
   - 資料狀態:無。

最嚴重等級 major;blocking 共 1 條。

來源:r1-架構對齊-sonnet.md(從第一條發現起)

**Finding 1:新測試沒用 `_SrcOnly` 防護**
ID: a1
severity: minor
blocking: 否
引句:「tpl = (Path(GRAPHCTL).resolve().parent.parent / "skills" / "lumos-design-loop" / "templates.md").read_text(encoding="utf-8")」
- file: `scripts/test_lumos.py:54076`(`t_templates_security_seat_section` 的 `_SrcOnly` 寫法)
- file: `scripts/test_lumos.py:54090`(`t_skill_code_loop_mentions_security_seat` 同樣有防護)

**Finding 2:測試放的位置、取名和路徑寫法跟同類的範本章節測試不同**
ID: a2
severity: minor
blocking: 否
引句:「def t_generalist_lens_native_review_method():」
- file: `scripts/test_lumos.py:54075`(同類測試取名 `t_templates_*_section`,放在範本相關測試群裡)
- file: `scripts/test_lumos.py:21805`(新測試被插在分片測試之間)

**Finding 3:⚠ §7.9 要替換的「你的鏡頭」在 §3 範本裡沒有這個標籤**
ID: a3
severity: minor
blocking: 否
引句:「派工詞用 §3 整份(引句、severity、翻紅重現、唯讀隔離、輸出格式全照 §3),只把」
- file: `skills/lumos-design-loop/templates.md:45`(§3 實際用的標籤是「審查鏡頭：」)
- file: `skills/lumos-design-loop/templates.md:77`(第 4 點「本案特定鏡頭」才是可替換的槽)

**Finding 4:新測試漏驗兩個其他席都有的對齊項(§7.7 立場表一列、§0 清單)**
ID: a4
severity: minor
blocking: 否
引句:「check("範本目錄列了 §7.9", "§7.9 通才鏡頭" in tpl.split("---", 1)[0], "")」
- file: `skills/lumos-design-loop/templates.md:393`(§7.7 立場表資安一列)
- file: `scripts/test_lumos.py:54082`(`t_templates_security_seat_section` 會驗立場表)

不對齊共 4 條,其中 major 0 條
