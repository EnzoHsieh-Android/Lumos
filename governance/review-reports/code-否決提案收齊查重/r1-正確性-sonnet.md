severity: major

## F1 新增頂層指令讓 `t_docs_command_count` 變紅(文件寫 84、實際 85)
severity: major
blocking: 是
引句:「p = sub.add_parser("rejections", help="舊否決清單:收齊圖譜裡寫下的否決,設計前按概念比對")」
佐證:file: `ARCHITECTURE.md:108`
佐證:file: `skills/lumos-project-notes/reference.md:117`
佐證:file: `scripts/test_lumos.py:27131`
失敗場景:
1. 這份 diff 多了一個頂層指令 `rejections`,`lumos --help` 的 choices 從 84 變 85。
2. diff 沒有改 `ARCHITECTURE.md` 的「84 個頂層命令」(第 108、112 行),也沒有改 `reference.md` 的「84 個頂層命令」(第 117 行)。
3. `t_docs_command_count` 在 argparse 實數和文件宣稱不一致時就紅。
4. 重現:在 c728cf14 的乾淨 clone 跑 `python3.14 scripts/test_lumos.py -k docs_command_count`,輸出如下。
   - `✗ ARCHITECTURE.md 命令數與 argparse 同步  claim={'84'} actual=85`
   - `✗ skills/lumos-project-notes/reference.md 命令數與 argparse 同步  claim={'84'} actual=85`
   - `2 passed, 2 failed`
5. 對照:`git checkout 6467401a` 後同一指令是 `4 passed, 0 failed`,所以是這條分支造成的。
6. `--suite docs` 整套也是 `711 passed, 2 failed`,失敗的就是這兩條。
7. 推送前的閘會跑到這支測試(docs 子集和全套都含它),推不過。計劃筆記的實作紀錄只提到跑過三支新測試和一次 high→standard 重分級,沒提這支。

## F2 [S1] 的測試太鬆:四種來源裡有三處壞了照綠
severity: minor
blocking: 否
引句:「_REJ_RETIRED = {"project": ("superseded", "rejected"), "system": ("superseded", "rejected"), "issue": ("wontfix",)}」
佐證:file: `scripts/test_lumos.py:76412`(`_rej_vault` 佈景)
失敗場景:我在 clone 裡逐個改壞,每次都跑 `-k rejections`,結果都是 `24 passed, 0 failed`。
1. 把 `_REJ_NOGO_RE` 改成只剩 `r"不做"`。佈景裡「停案不做己方案」本身就含「不做」,所以 `停案`、`否決`、`不採` 三個關鍵字都沒有被單獨驗到。
2. 把 `c[:120]` 改成 `c[:5]`,或整個拿掉視窗。佈景裡的決策全是短句,120 字視窗沒被驗到。
3. 拿掉 `"issue": ("wontfix",)`。佈景沒有任何 issue 節點。
4. 拿掉 `"project"` 這一項。佈景的作廢和否決節點都是 `type: system`,所以 project 的 superseded/rejected 沒被驗到。
5. 計劃 [S1] 寫的是「作廢或否決的節點」「內文寫不做的有效決策」。上面任一種實作錯誤,[S1] 的測試都不會變紅。
6. 計劃實作紀錄說「七種壞法各自紅」,但沒有列出上述四種。

## F3 「不做」關鍵字會把「推翻不做」的有效決策列成否決(設計取捨,但真圖譜已有誤導例)
severity: minor
blocking: 否
引句:「if str(d.get("valid", "true")).lower() != "false" and _REJ_NOGO_RE.search(c[:120]):」
失敗場景:
1. 在真圖譜(171 筆)跑 `lumos rejections`,「內文寫著不做的有效決策」那段有兩筆其實是在推翻或收窄舊的不做。
2. `Projects/評測尺翻案_計劃#d1` 內容是「推翻 2026-08-17 …的刻意不做,真的修尺」。結論是「做」,卻列在「不做」底下。
3. `Projects/狀態標籤同步守衛_計劃#d1` 內容是「收窄舊結論…『不做』不再是通則」。同樣是反向意思。
4. 另有 `Systems/cross-family-audit#d2` 的「disputed=否決不放行」,這是狀態值,不是被否決的提案。
5. 120 字視窗本身影響很小:真圖譜只有 2 筆有效決策是關鍵字在 120 字之後才出現而被漏掉,所以視窗不是問題。
6. 計劃已寫「會有誤收」,節標題也標了「可能誤收」,所以只算 minor。但拿清單做決定的代理會被這兩筆誤導。

## F4 摘要和正文有同一行 WHY 時同一條否決收兩次,筆數被灌水
severity: minor
blocking: 否
引句:「out += _rejections_why_alts(rel, ln[m.end():])」
失敗場景:
1. 一篇筆記的 summary 有 `WHY:同行 [出處:x] [因:y] [不選:甲方案]`,正文也有同一行。
2. `_rejections_of_note` 先從 `_note_summary_entries` 收一次,再從 `_visible_lines` 的正文收一次,兩邊沒有去重。
3. 我實跑:輸出兩行 `Projects/A_計劃: 甲方案  ← 那行的決定:同行`,「共 N 筆」多算一筆。
4. 規格閘那行和 `lumos rejections` 用同一個函式,口徑一致,但兩邊都會灌水。
5. 目前真圖譜 171 筆裡沒有重複,所以只是潛在問題。計劃只說「摘要與正文都收」,沒有去重規則。
6. 同類小問題:正文用 4 格縮排寫的 `    WHY:… [不選:戊縮排]` 也會被收進來,但它按 CommonMark 是縮排程式碼區塊,不是 WHY 行。`_REJ_WHY_RE` 的 `^\s*` 沒有排除。

## F5 測試 docstring 的條款編號和計劃筆記對不上
severity: minor
blocking: 否
引句:「"""[否決提案收齊查重 S5] lumos decisions --superseded 改用共用收集函式後,輸出一字不差(格式釘死在測試裡)。"""」
佐證:file: `docs/lumos-toolchain-knowledge/Projects/否決提案收齊查重_計劃.md`(範圍第 2 點、驗收條款 [S5])
失敗場景:
1. 計劃的 [S5] 是「2026-06-12 模板化盤問的否決要出現在清單裡」,綁的是 `[manual:]`。
2. 計劃範圍第 2 點明寫 `t_decisions_superseded_output_unchanged`「不列條款」。
3. 但這支測試的 docstring 自稱 `S5`,是壞引用。用條款編號回頭查綁定測試或做追溯的工具,會把這支測試誤認成 [S5] 的證據。

## F6 `--json` 的 `context` 欄位混了顯示格式,缺值時是字面的 `→ ?`
severity: minor
blocking: 否
引句:「"context": "→ " + str(d.get("superseded_by", "?"))})」
失敗場景:
1. `--json` 的 `superseded-decision` 項,`context` 是 `"→ d9"`,沒有 `superseded_by` 時是 `"→ ?"`。
2. 想從 JSON 找推翻它的那筆決策的程式,得自己剝掉箭頭,還要把 `?` 當成缺值。
3. 同一個欄位在 `rejected-alt` 裡是截到 40 字的核心句,在 `retired-node` 裡是 status,在 `no-go-decision` 裡是 id,四種語意不同。
4. 沒有 id 的 no-go 決策,文字輸出會變成 `Projects/X#: …`(實測 `#` 後面是空的)。
5. 計劃只規定 `source`、`kind`、`content`、`total` 四欄,目前沒有程式在讀 `context`,所以只標 minor。

## 其他逐項走過、沒問題的
- **重構等價**:`_superseded_decisions` 排序、`n.stem`、`→ ?` 預設值、空結果訊息都和原本的 inline 版一樣,`t_decisions_superseded_output_unchanged` 和 `-k decisions`(21 支)都綠。
- **例外處理**:規格閘那行的 try/except 範圍剛好,`print` 也在裡面。收集出錯時照樣略過、不改 rc,我拿掉 try 再跑,測試會紅。
- **舊格式讀取**:`valid: False`、`valid: "false"` 都照翻案處理。`valid: no` 一律當有效,這和原本 `decisions --superseded` 一致。
- **邊界輸入**:空圖譜、沒有 `[不選:]` 的 WHY、巢狀方括號、全形冒號 `[不選：…]`、同行多個 `[不選:]`、`- WHY:` 列表、圍欄未閉合都符合預期。2 萬個 `[不選:` 和 2 萬行 WHY 的壓力輸入各跑約 0.5 到 0.8 秒,rc 0,沒有二次方變慢。
- **效能**:真圖譜 768 篇,我這台收集一次約 0.34 到 0.5 秒,低於計劃設的 1 秒門檻。
- **相關測試**:`-k spec_gate` 103 支全綠,`-k help` 8 支全綠。兩篇改過的圖譜筆記 `lumos lint` 都是 0 問題。
- **全套測試**:我另外跑了全套,但在輸出到一半時整個程序消失,沒有最終統計,所以不能當證據。

## 圖譜固定席逐條判定
- `lumos-cli-read` ★INVARIANT★(search 預設排除 superseded、不排除 stale):不影響。`rejections` 是獨立的新指令,有意收作廢節點,沒有碰 search 的濾網和 `--include-superseded`。
- `bound-tests-gate` ★INVARIANT★(綁定測試逐支真跑):不影響。新測試沒有綁進別人的合約,新增測試也不會讓現有綁定懸空。
- `guard-kill` ★INVARIANT★(rc 優先序、`--json` 純度):不影響。diff 沒碰 guard kill。
- `授權與歸屬` ★INVARIANT★:不影響。`scripts/lumos` 檔頭和授權白名單都沒動。
- `測試假綠形態` ★INVARIANT★(還原翻紅釘要配前置斷言):大致符合,有一個缺口。`t_spec_gate_rejections_hint` 先用 ① 證明未 patch 時那行會印(現場成立),② 才 patch。但 ② 沒有斷言 patch 的函式真的被呼叫過。要是 `cmd_spec_gate` 提早返回,「舊否決 not in 輸出」會空綠。實際上 rc 比較和拿掉 try 後會紅這兩點讓它還算站得住,所以不算破壞合約。
- `design-loop` ★INVARIANT★(處置閘第五步、條款要有 `[綁定測試:有]`):不影響。`SKILL.md` 只多一句手冊文字;計劃的 [S1]、[S2]、[S4] 綁了測試,[S3]、[S5] 用 `[manual:]`。
- `reversibility-governance-ledger`、`loop-convergence-recording` ★RISK★:不影響。新指令只讀,規格閘只多印一行,不改判定和回傳碼。

共 6 條 finding,最高一條是 F1
