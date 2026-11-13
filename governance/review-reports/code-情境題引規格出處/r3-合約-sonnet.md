severity: minor

## g1 實務隱患仍說「重跑會多寫一條重複條款」,與這輪的行為對不上
severity: minor
blocking: 否
歸因:有證據的原有漏查(修補把「已寫過」改成兩種救法,但同一份計劃的實務隱患那行沒跟著改)
引句:「指令回 1 並印補記方法,不叫人重跑(重跑會多寫一條重複條款)。」
file: `docs/lumos-toolchain-knowledge/Projects/情境題答案要引規格出處與回寫循環_計劃.md:95`
失敗場景:
1. 三個月後的接手者讀到實務隱患,以為重跑會寫出重複的 S 條款,所以只敢手補帳。
2. 實際上 `_situation_rule_already` 會擋掉重跑:帳已記就回 0,帳沒記就回 2 並叫人先刪掉那一行再重跑。補記要的殺傷力結果只有跑殺傷力那次拿得到,所以「不要重跑」的結論仍對,但理由與另一條出路都沒寫。
3. 範圍 4 的新文字與程式一致,只有這一行是舊說法。

## g2 Systems/棧別提問表態閘與 Systems/規格閘沒跟著這輪改的行為更新
severity: minor
blocking: 否
歸因:未判定(這輪新增的行為沒同步到這兩篇)
引句:「寫計劃到記完治理帳那段也接這三個訊號、只記下:寫計劃之前收到就 rc 2 不寫」
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:86`
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:159`
file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:65`
失敗場景:
1. 表態閘 86 行寫「計劃路徑解開後要在 Projects/ 底下、CRLF 計劃拒絕」「殺傷力期間 SIGTERM、SIGHUP 同 Ctrl-C 收尾」「已有同文同測試的條款就不插」。這些都沒錯,但漏了:BOM、單獨 CR、Projects/ 是連結、大小寫不符都會拒絕;第二個訊號只記下;寫計劃到記帳那段受保護;「已寫過」帳已記時回 0。
2. 159 行的指令說明沒講回 0 的「什麼都不用做」出口,也沒講 `--plan` 大小寫不符會被拒。接手者照它操作,遇到「跟實際檔名對不上」或「已寫過」時無處可查。
3. 規格閘 65 行沒提 origin 為 ai 的人裁條款會多印一行提醒(`_spec_gate_ruled_ai_lines`)。計劃天花板 7 有寫,圖譜的規格閘節點沒寫。
4. 這些行屬於線索層,程式優先,不會因此做錯操作,所以只給 minor。

## g3 範圍 4 的讀計劃拒絕條件只列 BOM 與 CRLF
severity: minor
blocking: 否
歸因:有證據的修復回歸(換用 `load_raw_for_edit` 之後,拒絕條件變多,文字沒列全)
引句:「讀計劃用 `load_raw_for_edit`(開頭帶 BOM、CRLF 換行就照它的訊息拒絕),另擋單獨的 CR」
file: `scripts/lumos:30532`(`load_raw_for_edit` 還拒:讀不到、非 UTF-8、開頭沒有 `---` 欄位區塊、欄位區塊沒收尾)
失敗場景:
1. 計劃檔沒有欄位區塊時,指令回 2,訊息是「計劃:這篇筆記開頭沒有欄位區塊(---)…」。
2. 照範圍 4 的清單看不出這條,接手者會以為只要沒有 BOM、沒有 CRLF 就能寫回。
3. 實際遇到的機率低(計劃都是圖譜節點,有欄位區塊),所以只給 minor。

## 附:三問、圖譜鏡頭
**①原問題的修復效果(行為證據)**
- 我跑了 `python3.14 scripts/test_lumos.py -k <關鍵字>`,每個關鍵字都全數通過,沒有失敗:

  | 關鍵字 | 結果 |
  |---|---|
  | `situation_rule_already` | 4 passed |
  | `situation_rule_same_exact` | 3 passed |
  | `situation_rule_readback` | 3 passed |
  | `situation_rule_read_line` | 3 passed |
  | `situation_rule_plan_symlink` | 3 passed |
  | `situation_rule_double` | 9 passed |
  | `situation_rule_signal_during` | 7 passed |
  | `isolated_worktree_keep` | 4 passed |
  | `ruled_clause` | 9 passed |

- `lint Systems/guard-kill`:0 問題。
- `lint` 計劃:0 問題。
- `spec-gate 情境題答案要引規格出處與回寫循環_計劃 --no-run`:條款綁定 19/19、預期值表 27 列通過。
- 新增 WHY 行的格式符合 CLAUDE.md〈寫筆記時〉那張表,有 `[出處:]`、`[因:]`、`[不選:]`、`[test:]`。三個 `[test:]` 測試名在 `scripts/test_lumos.py` 都各有一個定義:`t_situation_rule_double_signal`、`t_situation_rule_signal_during_write`、`t_isolated_worktree_keep_failed_build`。
- ⚠ 該 WHY 的 `[出處:…r2-intake.md …]` 指向的檔目前只在磁碟上(未追蹤),不在提交 f04090128 裡。`git cat-file -e` 回報該路徑 "exists on disk, but not in 'f04090128'"。依專案慣例,卷證要放進同一個提交;若沒放,這條出處就懸空。我沒讀 r1、r2 的檔,只確認存在性。

**②修補處的正常、錯誤與相鄰路徑**
- 正常路徑:寫計劃、記帳、印下一步,和 `cmd_situation_rule` 的 docstring 一致。
- 「已寫過」且帳已記:`_situation_rule_done` 回 0,在殺傷力之前。
- 「已寫過」且帳沒記:`_situation_rule_say` 回 2,訊息講兩種救法。
- 寫計劃之前收到訊號:回 2 不寫。
- 計劃寫了、記帳之前收到訊號:`_situation_rule_ledger_miss` 印補記事件,回 1。
- 記帳當中收到訊號:帳記完,仍回 0。
- 讀回不一致:`_situation_rule_write` 回 `(原因, True)`,呼叫端回 1。
- 相鄰路徑:規格閘的 AI 代跑提醒,高風險走 `_spec_gate_expected_part`、低風險走 `_spec_gate_twoway_gate`,兩條互斥,不會重複印。`_expected_requirement` 在推送前那一圈不傳 `ai_out`,所以提醒只在 spec-gate 指令印,與天花板 7 的說法一致。

**③新發現的同一案例,修前與修後**
- g1:修前(1d535b07b)就寫「重跑會多寫一條重複條款」,而「已寫過」那道擋(r1 c7)修前就有。所以那行在修前就已不準,修後仍未改。
- g2:修前的圖譜節點沒寫第二訊號、BOM、CR、大小寫、rc 0,因為這些行為是這輪才有的。
- g3:修前 `_situation_rule_read` 自己讀檔,只拒 CRLF 和非 UTF-8,對沒有欄位區塊的檔不拒。換用 `load_raw_for_edit` 之後才多出這條拒絕。

**圖譜鏡頭(固定席筆記)**
- hook 這次沒附固定席節點,鏡頭計算超時(`LUMOS-LENS`),我也沒自行補算。
- 我改看與本次改動直接相關的三篇:Systems/guard-kill(新增一行 WHY,與程式一致)、Systems/規格閘(65 行,見 g2)、Systems/棧別提問表態閘(86、159 行,見 g2)。
- skills/lumos-code-loop/SKILL.md 沒提 situation-rule,不受影響。
- 06-代碼審與推送.md 第 16 行寫的「同意後帶原話代跑、放背景跑、提交計劃與重跑留痕」仍成立,沒有舊說法,只是沒提新的 rc 0 出口與 `--plan` 新限制,不影響操作。

**乾淨項目的對照引句**
- 引句:「第一個訊號轉成中斷之後,收尾期間再來的訊號只記下、不再打斷收尾」(對照程式 `_on` 裡 `if not defer and len(got) == 1: raise KeyboardInterrupt`,一致)
- 引句:「樹沒建起來(ok 為假)時不寫保留標記、暫存資料夾照一般收掉」(對照 `if keep and wt.ok:`,一致)

最嚴重:minor;blocking 共 0 條
