severity: major

我是三個月後接手的人,所以只查能不能照做、對不對得上。除第 3 條外,其餘的查證都實跑或實讀過。我沒有建任何實驗目錄,沒有東西要清。

已對上現況的部分:
- `templates.md` 第 63 行原句與 spec 逐字相同。
- `skills/lumos-code-loop/SKILL.md` 第 34 行的摘述存在,`t_no_adhoc_normalizer_in_review_reports` 釘的是 `"巢狀" in sk`。
- `05-設計審查迴圈.md` 第 14 行有 `quote-check` 那一列。
- `Systems/design-loop` 的收貨三道 KEY 在第 62 行;`loop-convergence-recording` 第 139 行有〈載體席的引句要全錨〉。
- `_quote_rows` 的呼叫點是 `scripts/lumos` 的 10965、26373、26529、26787,剛好四個。
- `loop replay <編號> --golden governance/replay/<編號>/verdict.json` 我實跑了一個,0.96 秒、回放一致。`governance/replay` 底下 305 個目錄、305 個 `verdict.json`,所以「約 5 分鐘」成立。
- `gov --since 60 --stats` 的旗標存在。
- 新測試用設定檔明寫 `write_rule`,所以第一階段預設 `legacy` 不會讓它們誤紅。

1. 第二階段沒有人、沒有日期、沒有接電
severity: major
blocking: 是
引句:「另一個提交把程式預設改成 `full-span-v1`(本 repo 不必寫設定)」
1. 〈兩階段上線〉只寫了條件(第一階段已在主線、已跑 `--compare-rules`),沒寫誰做、什麼時候做、怎麼確認條件成立。
2. 全篇沒有任何一行 `REVISIT:` 在盯第二階段。唯一的 REVISIT 是 2026-12-15,但它預設第二階段早已上線。
3. 「別的工作樹同步到第一階段」這個條件沒有機制可查。spec 只說窗口「壓小」,沒說怎麼知道窗口已經關了。
4. 我三個月後接手,看不出第二階段該不該做、什麼時候做。第一階段預設 `legacy` 等於沒改,最可能的結局是永遠停在第一階段,新判準從不生效。
5. 第二階段是另一個提交,但改的是這道守衛的預設值。spec 沒說它要不要再過一次代碼審。
6. 建議的接法:`REVISIT:[when-test:scripts/test_lumos.py::t_quote_full_span_rule_stamped_on_ledger][by:日期]`,或在第一階段提交寫死一個日期式 REVISIT。

2. REVISIT 與 RETIRE-IF 的度量靠第二階段,卻沒綁在一起
severity: major
blocking: 是
引句:「REVISIT:2026-12-15 跑 `lumos gov --stats --since 60` 看」
1. RETIRE-IF 寫「第二階段上線後 8 週內」,REVISIT 卻是固定日期 2026-12-15。第二階段若晚於 2026-10-20,這一天剛好不足 8 週。
2. 第一階段 `write_rule=legacy` 時,擋下的是舊判準。`kind` 由另一版判準重算,所以只會是 `both` 或 `legacy-only`,不會有 `new-only`。
3. 第二階段沒上線時,REVISIT 看到「`new-only` 零筆」,接手的人會誤讀成沒有誤傷。
4. 指令 `lumos gov --since 60 --stats` 本身能跑,我實跑確認了。
5. 但 spec 對「引句判準」那一格只說「多一格」和「計數」,沒說會拆出 `new-only` 筆數,測試也只釘 `"引句判準 2"`。照抄指令看不到 REVISIT 要的數字(見第 3 條)。

3. 擋下事件的 note 缺報告路徑,REVISIT 說的「逐筆讀擋下的報告」做不到
severity: major
blocking: 是
引句:「寫側擋下載體時(不論哪一版判準擋的)」
1. note 形狀只有 `write_rule`、`kind`、`cats`、`loop`、`auditor`、`id`,沒有 `report_path`。
2. 被擋的那筆「不寫帳」(S5),帳本裡沒有該報告的路徑。
3. 席位重記時,同一個報告檔大概率會被覆寫,「逐條看後誤傷多於真抓」缺原始證據。
4. 這是 RETIRE-IF 的判準來源,所以是 blocking。建議 note 補報告 sha 或路徑,或擋下當下把原文存進卷證。
5. 這條是推論,沒有實際重現。

4. 現有 seat-check 注入測試會被「函式一開頭就讀設定」弄紅
severity: major
blocking: 否
引句:「`seat-check` 用 `write_rule`(它只拿抽出的引句文字比材料範圍」
file: `scripts/test_lumos.py:37043` 這個測試把 `cmd_seat_check` 用 `exec` 丟進只有 `Path, sys, os, _quote_norm, _quote_rows` 的環境,且 `_quote_rows` 是 `lambda *_: []`。
1. 若實作在 `cmd_seat_check` 開頭就呼叫 `_quote_rule_for_write` 之類的新全域函式,這個測試走到 `materials[1]` 錯形態的 rc2 之前就拋 `NameError`,而 `except` 只接 TypeError、AttributeError、UnicodeEncodeError,測試就紅。
2. `lambda *_` 也不收 `rule=` 關鍵字。
3. 同步清單與驗收條款都沒提這條現有測試,照改會踩到。
4. 實作要把讀 `write_rule` 放到材料驗證之後,或同步改這個 stub。

5. 比較指令輸出字面,spec 與測試對不上
severity: minor
blocking: 否
引句:「輸出:兩版都錨定、兩版都不過、舊過新不過、舊不過新過、零引句、略過」
1. 測試 S6 檢查的是 `"舊判不過新判過 1"` 與 `"壞行 1"`,spec 寫的是「舊不過新過」。
2. S5 要求輸出含 `"隔離"` 二字,spec 只寫「印警告」。
3. 照 spec 字面實作會讓這兩個測試翻紅,要把字面寫進 spec。

6. 決策記錄的指令與實際 CLI 對不上
severity: minor
blocking: 否
引句:「用 `lumos decision-add` 在本計劃記一條決策(決定:不推進」
1. `decision-add` 的參數是 `note content --decided [--context] [--why]`,沒有「不選」「代價」旗標。
2. spec 沒說四欄怎麼塞進 `content`、`--context`、`--why`。
3. Issue 結案只寫「在正文補一節」,沒寫 `lumos set` 狀態怎麼改,也沒寫計劃自己的 `status: doing` 何時轉 done。
4. 接手的人得自己翻 `03-寫回圖譜.md` 才知道怎麼做。

7. 立案清單第 18 項的結案條件與 spec 的做法不一致
severity: major
blocking: 否
引句:「立案清單第 18 項標結案指向本篇」
file: `docs/lumos-toolchain-knowledge/Projects/逾期回頭條件立案清單2026-10_計劃.md:164`
1. 第 18 項的「怎麼算做完」是「所有講收貨三道的地方都有那句明文」,spec 只改 `templates.md` 這個單一來源就結案。
2. 講收貨三道的地方還有 `skills/lumos-design-loop/SKILL.md:27`、`skills/lumos-design-loop/reference.md:94` 與 `:514`、`skills/lumos-code-loop/reference.md:91`,同步清單一個都沒列。
3. 要嘛同步這幾處,要嘛在清單第 18 項明寫「以單源為準,不逐處」。

8. 新範本與 code-loop 摘述、測試訊息語意矛盾
severity: minor
blocking: 否
引句:「保留「巢狀」二字(測試 `t_no_adhoc_normalizer_in_review_reports` 釘著它)」
file: `scripts/test_lumos.py:45578` 測試訊息寫「引句內不要再包同型括號(巢狀會被收貨截斷)」。
1. 新範本改成「巢狀可以,但要成對」,SKILL.md 若只保留「巢狀」二字,可能留下「不要巢狀」的舊意思,測試照綠。
2. 要連測試訊息一起改,並把釘住的字串改成能區分新舊語意的片段。

9. 〈推送前驗證〉三步:指令能跑,但時間和結果存哪沒說完
severity: minor
blocking: 否
引句:「先用未改的提交對全帳每組(報告, 快照)跑一次現行 `_quote_rows`」
1. 第二步(回放全跑)我實跑驗證可行,約 1 秒一個,但 spec 只寫逐一跑,沒給迴圈指令。
2. 第一步要寫一支一次性腳本,沒說放哪、誰負責、基線檔名。
3. 〈推送前驗證〉寫「比對結果寫進驗證紀錄」,但沒指到 `lumos new verification` 的指令。
4. 第三步的 `-k` 子集 spec 與專案 `CLAUDE.md` 一致。

10. `_QUOTE_RULE_STAMP_SINCE` 的值在提交時不可能等於合入日
severity: minor
blocking: 否
引句:「第一階段合入日存成常數 `_QUOTE_RULE_STAMP_SINCE`(帶時區完整時間」
1. 常數要在合入前寫死。實際合入時間晚於它,中間舊版程式寫的無章帳會多出誤警告。
2. 只警告不擋,影響小,但 spec 沒說合入後要不要回頭校正這個常數。

11. S7 的測試無法區分「章被刪」與「帳被動」
severity: minor
blocking: 否
引句:「把帳上的章刪掉後回放 應 報帳被動」
1. 測試只改一列後斷言 `rc != 0` 且輸出含「帳」。任何帳列被動都會達成,不證明讀章邏輯正確。
2. 建議補一個只改 `quote_rule` 值(`legacy` 與 `full-span-v1` 互換)的案例。

實務隱患逐類:
- 回頭條件接電:有缺,見第 1、2 條。
- 擋下事件可稽核:有缺,見第 3 條。
- 現有測試相容:有缺,見第 4、5、8 條。
- 手改帳本、別的工作樹跑舊版程式、效能、不可逆:spec 已自述,我沒有新發現。
- 金流、對外送出:無,如 spec 所述,只讀本機檔案。

總結:最高等級 major,blocking 共 3 條。
