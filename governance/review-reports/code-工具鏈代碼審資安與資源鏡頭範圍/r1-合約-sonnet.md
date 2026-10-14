severity: minor

整體:計劃〈做法〉1–10 與 S1–S12 逐條對過,沒有做少或做多。我把凍結提交 477816362158 解開放在 `/tmp/lumos-seat-work/code-工具鏈代碼審資安與資源鏡頭範圍/合約-sonnet/w` 實跑:

- 8 支新測試全綠。
- 5 支既有守衛測試(`t_templates_security_seat_section`、`t_seat_templates_carry_marker`、`t_data_state_lens_in_code_template`、`t_disposal_security_seat_required`、`t_roster_code_high_has_security_seat`)照樣綠,`-k templates_` 的 108 支全綠。
- 7 篇動到的筆記 `lumos lint` 都是 0 問題。
- `scripts/test_lumos.py` 的雜湊跟 `governance/anchor-baseline.json` 吻合。
- 歷史段落沒被動:`reference.md` 的三處改動都在「## 歷史與停用」之前,設計審的 §1、§7 panel 原文也沒改。
- 固定席 ★INVARIANT★ 沒被破壞;改動只加了 design-loop 的一條 WHY,處置閘第五步那條沒動。

以下是我找到的問題,都不影響合併。

severity: minor
blocking: 否 — 只會讓正確性、邊界席在工具鏈本 repo 多報一些該被判為範圍外的併發誤報,折掉即可,不會漏洞或誤擋
引句:「pitfalls manifest 附的併發類檢核題(鎖、交易包裹)在這個 repo 判「範圍外、不審」,標誤報即可。」
問題:這句豁免寫在〈工具鏈三類〉裡,但那一節是只貼給資安席的。pitfalls manifest 只出現在 §3 reviewer 派工詞(`templates.md:171`),資安席的 §7.8 圍欄沒有 manifest。真正會看到併發題的正確性、邊界席,既拿不到這句,§3 編排者須知(`templates.md:142`)又只換掉「冪等與併發」那一項,沒提 manifest。計劃新規則 3 與 S4 的字面是這樣寫,這裡照做了,但達不到 RULE 2「不審多人或多會談同時寫入的競態」的目的。
失敗情境:工具鏈本 repo 的高風險代碼審,manifest 命中「鎖/交易」題。正確性席照 §3 第 2 點逐條判真隱患或誤報,沒有任何指示說這在本 repo 是範圍外,就可能照舊報成 major,要多折一輪。
佐證:``file: `skills/lumos-design-loop/templates.md:476` ``、``file: `skills/lumos-design-loop/templates.md:171` ``、``file: `skills/lumos-design-loop/templates.md:142` ``

severity: minor
blocking: 否 — 只是範本裡一句指示不精確,記帳時被擋會立刻看到錯誤訊息
引句:「記帳時這類發現帶 `--finding-kind <id>=process`(流程自己要求的文件,不寫修正紀錄、不補測試)。」
問題:有兩處跟程式不符。
- 程式要求整輪每一條發現都各標一個種類(`set(kinds) != F` 就擋下 rc2,`scripts/lumos:11509-11516`)。範本、Issue、SKILL 的寫法讀起來像只標範圍外那幾條。
- `process` 在程式裡的定義是「流程要求產出的規格文件、留痕格式、範本」,而且是「流程自產工作量」統計的唯一量法(`scripts/lumos:10137-10146`)。把刻意偽造類發現標成 `process`,會灌高那個佔比。
- 我只在 `_fix_needed`(`scripts/lumos:14646`)看到 `process` 豁免「修正紀錄」,沒找到「不補測試」的機制。
失敗情境:編排者只給範圍外那一條帶 `--finding-kind f3=process`,記帳被擋;或標了之後「流程自產工作量」統計被範圍外手法污染。
佐證:``file: `skills/lumos-design-loop/templates.md:489` ``、``file: `scripts/lumos:11502` ``

severity: minor
blocking: 否 — 條款裡幾個詞沒有測試守住,但目前文字是對的
引句:「卷證與派工單裡的本機絕對路徑(`file:` 佐證、`repo 在…`)是既有慣例,不報。」
問題:`t_templates_toolchain_lens_scope` 沒綁住 S4 的幾個詞。我在複本上做了變異,測試仍然全綠:
- 把「是既有慣例,不報」改成「要報」。
- 把「接受不看」裡的「加密與傳輸(安裝腳本下載來源那部分已併進②)」整段拿掉。
- 拿掉「(非刻意殘留的環境屬③)」。
此外,「散文才拿掉保護說法」只驗到有「散文」這個詞,沒驗它的條件。d1「設計審照舊」的 WHY 綁的是 `t_templates_toolchain_resource_lens`,它只驗那一列有「設計審照舊」字串,看不出 §1 審計員第 5 點、§7 設計審 panel 有沒有被改。
失敗情境:之後有人把「不報」誤改成「要報」,測試不會紅,資安席就開始報卷證路徑。
佐證:``file: `scripts/test_lumos.py` 的 t_templates_toolchain_lens_scope(⑥⑦兩組關鍵字清單)``

severity: minor
blocking: 否 — 兩句話之間的語意落差,不影響閘
引句:「要先能控制推送行程的環境變數才做得到,屬刻意設定環境的手法,在工具鏈的資安範圍外(工具鏈本身的資安只看提示注入、讀寫越界、非刻意的一步繞過;見 Systems/pitfalls-code-loop 工具鏈資安範圍 RULE)」
問題:bound-tests-gate 的這條 WHY 把「PYTHONPATH 帶 sitecustomize」判成範圍外,並改指向 RULE 當依據。可是 RULE ③ 正好把「別的程序帶進來的 `PYTHONPATH` 這類非刻意的環境」列為範圍內。WHY 的括號也把「讀寫與執行越界」縮成「讀寫越界」,跟 RULE 字面不一致。讀者拿 RULE 去驗證這條 WHY,會得到「非刻意殘留的 PYTHONPATH 是範圍內」。
失敗情境:下一次資安席依 RULE ③ 重新報這條 sitecustomize 繞過,編排者翻 WHY 發現「依據」其實並沒有排除這種非刻意的情況。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:142` ``、``file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:58` ``

severity: minor
blocking: 否 — 只漏兩份少用的子代理派工詞,規則本身已盡力
引句:「下面每一份第一行是 `LUMOS-SEAT:` 的派工詞,加上 §5 實作與 §6 任務審查兩份派工詞」
問題:刪檔紀律只補進這 8 份。templates.md 裡還有兩份給子代理的派工詞沒帶:§3.1 修補鏡頭(`templates.md:241`)和 §9 跑滿回顧起草者(`templates.md:540`)。全域規則寫的是「派子代理時這條要原文寫進派工詞」。`t_templates_rm_literal_absolute_path` 又把數量釘死在 6 份加 §5、§6,這兩份就沒有任何測試或規則會提醒。計劃的〈不做〉只排除了 lumos 程式自己產生的派工詞,沒有討論這兩份。
失敗情境:跑滿回顧起草者要清暫存時,沒被告知字面絕對路徑,會觸發刪除保險絲而卡住。
佐證:``file: `skills/lumos-design-loop/templates.md:241` ``、``file: `skills/lumos-design-loop/templates.md:540` ``

severity: minor
blocking: 否 — 筆記整潔度問題
引句:「這三份說明的家是 [[Systems/每輪修補差異派工]],說明寫進那篇。」
問題:
- 該節點的 `about_code` 只列了 `SKILL.md`、`templates.md`、06 子檔三支,沒有 `skills/lumos-code-loop/reference.md`,所以「三份說明的家」其中一份其實沒有家。
- 計劃的 `lands_in` 沒列新開的 `Issues/工具鏈範圍外手法紀錄`,CLAUDE.md 鐵則 5 要求寫「現況落在哪幾篇或新開哪一篇」。
- pitfalls-code-loop 與資安席計劃兩條 KEY 句尾寫「見 Systems/pitfalls-code-loop 新決策與 RULE」,沒寫 d8。前一條 KEY 就在 pitfalls-code-loop 本篇裡,「新」字會隨時間失去指向。
佐證:``file: `docs/lumos-toolchain-knowledge/Systems/每輪修補差異派工.md:9` ``、``file: `docs/lumos-toolchain-knowledge/Projects/工具鏈代碼審資安與資源鏡頭範圍_計劃.md:10` ``

以下已讀,無 finding:
- `loop next` 的實作:
  - 位置在席位之後、「在審材料」之前。
  - 條件是 `code-` 前綴,fail-open 包在 try 裡,`--repo` 有生效。
  - 固定字串逐字等於計劃。
- 兩條 RULE 欄位齊全:`依據`、`since`、`retire:人裁`、`until`、`confirmed` 都有。
- d8 的 `alternatives` 與 `trade_offs` 寫進 `why_chosen` 後半,是計劃給的退路;d6 沒被取代。
- Issue 四段與表格,及其 `--finding-kind` 值本身合法。
- 三份說明檔與 06 子檔的句子,逐字等於測試常數。
- 〈消費專案六類〉跟改動前圍欄原文逐字相同。
- §7.7、§7 鏡頭列的句子。

我的實驗目錄 `/tmp/lumos-seat-work/code-工具鏈代碼審資安與資源鏡頭範圍/合約-sonnet/` 留給編排者收貨後刪。

最高等級 minor,blocking 0 條。
