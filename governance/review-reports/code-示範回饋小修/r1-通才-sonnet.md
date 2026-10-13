severity: major

審查範圍:全部 hunk 都讀過。名稱邊界與風險面觸發我在臨時 repo `/tmp/lumos-seat-work/code-示範回饋小修/通才-sonnet/` 用 `scripts/lumos` 實跑。兩支新測試(`t_new_project_appends_plan_suffix`、`t_stage_facets_scale_and_sync`)在目前的實作上都綠。

**1.**
引句:「    if ntype == "project" and not name.endswith(("_計劃", "_調研")):」
file: `scripts/lumos:22686`(`cmd_new` 的補後綴判斷)。後綴判斷只認兩個字串,既有的合法命名會被改壞,重現如下:
- `lumos new project 規劃_草案` 建成 `規劃_草案_計劃.md`。
- `Projects/` 下有 20 篇「_草案」結尾的現成檔,另有「_實作計畫」(「計畫」,不是「計劃」)的檔。
- `lumos new project foo_計畫` 建成 `foo_計畫_計劃.md`,多出一個後綴。
- 名稱為空字串時建成 `_計劃.md`。修之前是 `.md`,現在不擋也不報錯。
- 名稱為 `foo_計劃 `(尾端帶空白)時建成 `foo_計劃 _計劃.md`。
severity: major
blocking: 是 — 會用違反既有命名的檔名建檔且不報錯,而且建出來的檔要手動刪掉重建;這正是此修法要消除的問題。
最小重現:`python3.14 scripts/lumos new project 規劃_草案`,再看 `Projects/` 下的檔名。

**2.**
引句:「[需求風險面的觸發 regex] "when": [r"大量|高併發|同時|搶|秒殺|活動|尖峰|流量"]」
file: `scripts/lumos:27870` 起的 `_REQUIREMENT_FACETS`。上面的引句是 req-scale 那列 `when` 的內容;arch-sync 那列用同一串詞再加「排隊|非同步」。
- 「同時」「活動」是一般詞。我跑了只寫「使用者修改密碼時,同時更新暱稱與信箱,並在活動紀錄顯示」的設定頁計劃。
- `pitfalls --stage 需求` 多列出 req-scale(量級),`--stage 架構` 多列出 arch-sync(要不要上佇列)。
- 這兩列是專門為搶購那類計劃加的。
- `t_stage_facets_scale_and_sync` 的 calm 樣本刻意避開了這些詞,所以測不到這個誤觸。
- 「同時」誤觸在既有的 impl-concurrency 就有,但新列把它擴到需求與架構兩個階段。
severity: minor
blocking: 否 — 只是多出提示題,不影響規格閘判定(計劃第 47 行也這樣宣稱)。
最小重現:`printf "# 設定頁\n\n修改密碼時同時更新暱稱,並在活動紀錄顯示。\n" > a.md; python3.14 scripts/lumos pitfalls a.md --repo . --stage 架構`,輸出含 `[arch-sync]`。

**3.**
引句:「check("⑤ 補完後撞到既有的同名計劃:照樣擋下、不重建", r5.returncode == 2 and "已經有了" in r5.stderr, r5.stdout + r5.stderr)」
- 這一格沒有鑑別力。第二次呼叫 `new project 訂單下單` 時,修之前會去建 `訂單下單.md`,而它在 ① 就已存在,所以同樣回 2 並印「已經有了」。
- ③ 的「_調研 原樣」、② 的「已是 _計劃 原樣」、④ 的「system 不補」也一樣,把補後綴邏輯整個拿掉照綠。只有 ① 和「輸出提到補了」這一格會翻紅。
- 真正需要釘的「補完後撞名」是另一條路徑:已有舊的 `X.md`(無後綴)時,`new project X` 現在會靜默另建 `X_計劃.md`,近名提醒雖會出現,但不擋。測試沒涵蓋。
- 這幾格也不符合〈實作測試品質〉要求的「現場成立 + 抓得到實際錯誤」。
severity: minor
blocking: 否 — ① 已能對補後綴本身翻紅,多餘的格子只是假安全感。
最小重現:把 `cmd_new` 的補後綴三行註解掉,② ③ ④ ⑤ 四格仍綠,只有 ① 翻紅。

**4.**
引句:「PRIOR-ART: ①沿用既有慣例(圖譜紀律「計劃一律寫成 Projects/<主題>_計劃」,現有 339 篇有 328 篇這樣結尾、33 篇用「_調研」)」
- file: `docs/lumos-toolchain-knowledge/Projects/`。我數了 `ls | grep` 的結果:共 340 篇,「_計劃」結尾只有 280 篇,「_調研」結尾 33 篇,兩者都不是的有 27 篇(其中 20 篇「_草案」)。
- 計劃的 PRIOR-ART 數字(328)與實際差 48 篇,而這份落差正是 finding 1 的來源。
- 這是筆記裡的事實錯誤,應修正並改立 Issue。
severity: minor
blocking: 否 — 只是計劃筆記的描述錯誤,不改程式行為。

**5.**
引句:「        print(f"名稱補成 {name}_計劃(計劃筆記的慣例;要建調研筆記就用 {name}_調研)")」
- file: `scripts/lumos:22686`。這行在 `--plan/--systems` 檢查、`about_code` 檢查、同名檔存在檢查之前就印到 stdout。
- 之後被擋(例如補完後撞到 `A_計劃.md` 已存在)時,使用者會先看到「名稱補成 A_計劃」,再看到「擋下」。
- 訊息本身沒有錯,但印在 `擋下:` 之前,容易讓人以為已經建了。
- 其餘用到 `name` 的地方(`path`、`self_rel`、近名比對、`# {name}` 標題、`lumos lint {name}` 提示)都在改名之後才執行,用的是補過的名字,這部分沒問題。
severity: minor
blocking: 否 — 只是訊息順序問題,檔案與帳都是對的。

**固定席逐條判定**(均不影響,各附理由):
- `Systems/lumos-cli-read.md` 的 INVARIANT(search 預設排除 superseded):不影響。diff 沒碰 `search` 的濾網或分岔邏輯,只改 `cmd_new` 與 `_REQUIREMENT_FACETS`。
- `Systems/pitfalls-code-loop.md`:不影響合約。`--stage` 讀 facets 的寫法(`scripts/lumos:44302` 的列表推導)沒改,只多兩個條目。測試 `t_backend_qo_stage_facets_only`(9 項)與 `t_qfm_*` 相關(11 項)我跑過,全綠。
- `Systems/測試假綠形態.md` 的 INVARIANT(還原翻紅釘必配前置斷言):新測試違反這條精神,見 finding 3。② ③ ④ ⑤ 把修法還原仍綠,只有 ① 會紅;沒破壞既有綁定測試。
- `Systems/guard-kill.md`、`Systems/design-loop.md`、`Systems/bound-tests-gate.md`:不影響。沒動 guard kill 的 rc 優先序,也沒動處置閘、綁定測試閘。`design-loop.md` 的處置閘那條 INVARIANT 沒被手冊新增那句改到。
- `Systems/arch-alignment-lens.md`、`Systems/loop-convergence-recording.md`:不影響。手冊新增的 `--findings` 規則與 code-loop 步驟 6 寫的「`--findings` 不得多於它的報告」一致,沒有互相矛盾。
- 超出上限只列名的那批:沒看到 diff 與它們的合約有交集。
- 家(home)的問題:計劃的 `lands_in` 只列 `Systems/情境出題` 與 `Systems/lumos-cli-write`,兩份手冊(`skills/lumos-design-loop/SKILL.md`、`skills/lumos-code-loop/SKILL.md`)的改動沒落在這兩篇。計劃第 34 行也沒提 code-loop 手冊會被改。這是範圍描述不一致,不是行為破壞,所以沒另列成 finding。

總結:最嚴重 severity 為 major,blocking 1 條(finding 1)。
