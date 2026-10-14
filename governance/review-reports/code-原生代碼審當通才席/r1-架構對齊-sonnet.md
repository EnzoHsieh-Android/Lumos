severity: minor

**一、分層與依賴方向**

沒有 major。新席沒有跨層直呼,依賴方向跟 §7.8 資安席一樣。`_TIER_ROSTER` 只多一段備註,席名、occupies_w、family 都沒動,SKILL.md 步驟 2 和 §7.9 都只往 §3 引用。
- file: `scripts/lumos:13309`(patch 的鏡頭5 備註,對照同表資安席備註「派工 templates.md §7.8」)
- file: `skills/lumos-design-loop/templates.md:406`(§7.8 同樣是範本章節加席位備註指過去)

有一處不對齊,見下面 finding 1。

**二、命名與錯誤處理**

先是章節和備註的寫法,這部分大致一致:
- §7.9 的標題是「通才鏡頭」,同時帶了日期、裁決人和 `單源=[[…計劃]]`,跟 §7.6、§7.8 的標題格式一樣。
- 目錄列、§0 之外的位置(排在 §7.8 後、§7 前)也沿用既有排法。
- file: `skills/lumos-design-loop/templates.md:334`、`skills/lumos-design-loop/templates.md:406`

不一致處有三個:
1. 測試沒做來源專屬防護。既有讀 `skills/` 的測試(`t_templates_security_seat_section`、`t_skill_code_loop_mentions_security_seat`)都先 `if not p.exists(): raise _SrcOnly(...)`,新測試直接 `read_text`,消費端沒有 `skills/` 會崩。
2. 新測試的位置和命名。它被插在分片測試之間,不在其他範本章節測試(`t_templates_security_seat_section`)附近。命名也不照 `t_templates_*_section` 的慣例,而且路徑是 `Path(GRAPHCTL).resolve().parent.parent`,資安席同類測試用 `pathlib.Path(__file__).resolve().parent.parent`。這個路徑寫法本檔也有其他測試在用,所以是弱不一致。
3. 新測試漏了其他席都會做的兩項檢查:§7.7 立場表有沒有通才一列,以及 §0 的 LUMOS-SEAT 清單有沒有通才。

**三、第二種做法(§7.9 有沒有另立一套規則)**

沒有。§7.9 明講引句、severity、翻紅重現、唯讀隔離、輸出格式全照 §3,八角度之後只說嚴重度與翻紅重現照 §3 的規則判,沒有自己定嚴重度或格式。測試也有檢查 §7.9 的圍欄裡不含 blocker。

另有一個 ⚠ 判不準的細節:§7.9 說要換掉 §3 的「你的鏡頭」那段,但 §3 派工詞裡只有「審查鏡頭：」,沒有「你的鏡頭」這個標籤。§3 的第 4 點是「本案特定鏡頭」。SKILL.md 步驟 2 和 §7.9 都用「你的鏡頭」指稱,跟既有範本的用語對不上,換哪一段並不明確。

## findings

**Finding 1:新測試沒用 `_SrcOnly` 防護**
severity: minor
blocking: 否
引句:「tpl = (Path(GRAPHCTL).resolve().parent.parent / "skills" / "lumos-design-loop" / "templates.md").read_text(encoding="utf-8")」
- file: `scripts/test_lumos.py:54076`(`t_templates_security_seat_section` 的 `_SrcOnly` 寫法)
- file: `scripts/test_lumos.py:54090`(`t_skill_code_loop_mentions_security_seat` 同樣有防護)

**Finding 2:測試放的位置、取名和路徑寫法跟同類的範本章節測試不同**
severity: minor
blocking: 否
引句:「def t_generalist_lens_native_review_method():」
- file: `scripts/test_lumos.py:54075`(同類測試取名 `t_templates_*_section`,放在範本相關測試群裡)
- file: `scripts/test_lumos.py:21805`(新測試被插在分片測試之間)

**Finding 3:⚠ §7.9 要替換的「你的鏡頭」在 §3 範本裡沒有這個標籤**
severity: minor
blocking: 否
引句:「派工詞用 §3 整份(引句、severity、翻紅重現、唯讀隔離、輸出格式全照 §3),只把」
- file: `skills/lumos-design-loop/templates.md:45`(§3 實際用的標籤是「審查鏡頭：」)
- file: `skills/lumos-design-loop/templates.md:77`(第 4 點「本案特定鏡頭」才是可替換的槽)

**Finding 4:新測試漏驗兩個其他席都有的對齊項(§7.7 立場表一列、§0 清單)**
severity: minor
blocking: 否
引句:「check("範本目錄列了 §7.9", "§7.9 通才鏡頭" in tpl.split("---", 1)[0], "")」
- file: `skills/lumos-design-loop/templates.md:393`(§7.7 立場表資安一列)
- file: `scripts/test_lumos.py:54082`(`t_templates_security_seat_section` 會驗立場表)

不對齊共 4 條,其中 major 0 條
