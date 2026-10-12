severity: minor

乙區（計分器、自主迴圈測試、技能文件、知識筆記、評分員原始輸出遮蔽）沒有 blocker 或 major。撤出本身乾淨：程式裡已沒有〈待決問題〉解析的殘骸，也沒有斷掉的呼叫。我另外找到四條 minor，都是文件與測試碼上的殘留，沒有行為壞掉。

## 固定席逐條判定
- codex-harness：這個修補只動 qo_ablation.py 與 TestQoAblation，沒碰 scenario_probe.py，不影響。
- bound-tests-gate、design-loop、guard-kill、lumos-cli-lifecycle、lumos-cli-read、授權與歸屬、測試假綠形態（各自的 ★INVARIANT★）：這批合約綁的測試都不在被刪或改名之列，不影響。被刪的 `t_backend_qo_parser_robust`、`t_backend_qo_gate_fail_closed`、`t_backend_qo_unreadable_questions_fail_closed`、`t_backend_qo_blocking_question_holds_spec_gate`、`t_backend_qo_question_line_shape`、`t_backend_qo_stage_order_and_cap`，在 b187b5e9 的非卷證檔案裡搜不到殘留引用。
- design-loop 的「計劃有 [SN] 時條款要綁測試」：`python3.14 scripts/lumos spec-gate "Projects/後端工程提問與證據擴充_計劃" --no-run` 回「條款綁定: ✓ — 7 條全標」，S2 拿掉造成的編號空缺沒被擋。不影響。

## 三問
1. **原問題的修復證據。**
   - 計分器兩個洞（`--batch 0`/負數先刪光舊包、結果檔欄位型別錯就崩）：我把修後的 test_autonomous_loop.py 放進修前副本，`python3.14 -m unittest scripts.test_autonomous_loop.TestQoAblation` 兩條新測試都 ERROR（共 2 錯）；修後 29 個測試全過。修前跑修前自己的測試是 27 個全過，原因是那時還沒有這兩條測試。
   - 正文解析撤出：把修後的 test_lumos.py 放進修前副本，`-k section_not_parsed` 是 0 過 2 紅，`-k stage_facets_only` 是 5 過 2 紅；修後 `-k t_backend_qo` 是 9 過 0 紅。
2. **相鄰路徑。**
   - `pitfalls --stage` 的錯階段、與 `--diff` 並用、非 UTF-8 計劃回 2，以及不帶 `--stage` 時輸出一字不差，都在 `t_backend_qo_stage_facets_only` 的 ④⑤⑥⑦ 裡，修後全綠。
   - 評分員原始輸出的遮蔽：我把兩個檔裡的 `<會談暫存目錄>` 換回原前綴，逐字等於 46bc93c3 的版本（rating-mini 10 處、rating 14 處）。qo-ablation 目錄裡已沒有 `/Users/enzo`、`/private/tmp/` 或會談 id。遮蔽沒有改到原意。
3. **同一案例兩版結果。** 見上面第 1 點，兩版結果分開列出，無新增回歸。

## Findings

severity: minor
blocking: 否
歸因：有證據的修復回歸（這輪撤出時漏改的殘留）

〈後端工程提問與證據擴充_計劃〉裡，這輪沒改到的段落仍寫著已撤出的行為，與 S1 和 d10 互相矛盾：
- d7 的 `valid: true`，內容是「本計劃只新寫〈待決問題〉的文法與檢查」。
- 〈合約候選〉第一條寫「規格閘遇到需求或架構階段、標阻塞…的題就回 1(S1)」，與現在的 S1 正好相反。
- 以下各處同樣沒更新，還在講規格閘擋阻塞題、lint 規則、題目清單：
  - 關卡表的「需求就緒」列
  - 實務隱患的「守衛面」行
  - 第 3 階段的完成條件
  - 〈回退〉節
  - RETIRE-IF 的第①項

CLAUDE.md 規定決策紀錄能推翻程式，所以 d7 仍有效會誤導下一個 session，〈合約候選〉也可能被誤綁成 ★INVARIANT★。這輪只把 d1 標成已作廢，d7 沒有。

兩版查證：
- 修後：`python3.14 scripts/lumos decisions "Projects/後端工程提問與證據擴充_計劃"` 列出 d7 是 ✅。
- 修前：d7 同樣是 ✅，但那時解析還在，內容與程式相符。

引句:「Lumos 後端工程擴充採薄層方案(修訂):題目掛在計劃筆記的〈待決問題〉、答案掛既有決策紀錄、驗收證據掛既有測試綁定與破壞測試;本計劃只新寫〈待決問題〉的文法與檢查」
佐證 file: `docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md:87`

severity: minor
blocking: 否
歸因：有證據的修復回歸

這輪新寫的筆記承認了風險，卻沒附回頭看的條件，違反專案 CLAUDE.md 鐵則 4：
- 規格閘.md 的 WHY 寫「代價:擋阻塞題的功能暫時沒有，改存開頭欄位後再接回」。
- 情境出題.md 和 pitfalls-code-loop.md 有同類的「暫時沒有／後再接回」說法。
- 新的〈待決問題改存開頭欄位_計劃〉只有 RETIRE-IF，沒有 `REVISIT:`。

目前 `lumos lint` 對這幾篇都是 0 問題，所以這個缺口沒有機械守衛。

引句:「[代價:擋阻塞題的功能暫時沒有,改存開頭欄位後再接回]」
佐證 file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:86`

兩版查證：
- 修後：`git grep` 在這三篇和新計劃裡找不到對應的 REVISIT 行。
- 修前：這些句子不存在，是本輪新增的。

severity: minor
blocking: 否
歸因：有證據的修復回歸

測試檔留下沒人用的輔助常數 `_QO_DEC`，是撤出時沒清乾淨的殘骸。它只出現在自己的定義那一行，沒有其他引用。`_qo_plan` 的 `clauses`、`decisions` 參數也沒有任何呼叫者傳值。

引句:「_QO_DEC = "decisions:\n  - content: 採用甲方案\n    id: d1\n    decided: 2026-10-12\n    valid: true」
佐證 file: `scripts/test_lumos.py:56079`

兩版查證：`git grep -n -e "_QO_DEC" b187b5e9 -- scripts` 只有一筆（定義處）。修前這個常數有被用到，修後沒有。

severity: minor
blocking: 否
歸因：有證據的修復回歸

情境出題.md 寫遮蔽範圍是「六個檔，本機家目錄換成 `~`」。這輪另外對 `rating-mini/codex-rater-raw.txt` 和 `rating/codex-rater-raw.txt` 把路徑換成 `<會談暫存目錄>`，筆記沒提。事實與內容我都核對過沒問題，只是記錄不完整，下一個人可能以為這兩檔沒動過。

引句:「實驗目錄裡外部審查與原始輸出的六個檔,本機家目錄換成 `~`(逐檔驗過只換了這個字串)」
佐證 file: `docs/lumos-toolchain-knowledge/Systems/情境出題.md:33`

兩版查證：兩版筆記都沒提 `<會談暫存目錄>`；修前這兩個檔還帶著完整暫存路徑，修後是遮蔽版。

## 未驗範圍
- 沒跑全套 3700 多個案例，也沒跑 CI。
- 甲區（scripts/lumos 與 scripts/test_lumos.py 的程式本體）只看了與撤出有關的搜尋，沒逐 hunk 審。
- 沒對計分器做大型輸入的效能檢查。
- 下輪待驗：把〈合約候選〉第一條誤標成合約，推送前綁定測試閘是否會擋。

總結:最嚴重 minor;blocking 共 0 條。
