severity: major

## 發現

severity: major
blocking: 是 — 手冊明寫「內容從 base 讀、零自由文字」,新段卻從頂端讀推送者寫的自由文字,信任邊界的說法被默默改了,手冊沒跟上。
引句:「內容從頂端讀:新增的殘留只在這次的提交裡,主線版沒有。」
問題:這次修補在 `lumos dispatch-lens` 新增「這次新增的殘留」段。決策內容、`case`、`checker` 都是提交者能寫的字,而且從 head 提交讀。手冊另外兩處仍然寫著相反的話。
- `skills/lumos-design-loop/templates.md` §3 說「內容一律從 base 讀、零自由文字……唯一例外是帶 `[來源:外部]` 的外部事實行」。
- `skills/lumos-project-notes/commands/06-代碼審與推送.md` 的「固定席節點自動附進派工詞了嗎」那列說「內容從 base 讀;自由文字只有帶 `[來源:外部]` 的外部事實行,在框內」。
- 這次修補只在 SKILL.md、templates §3 的必答句和計劃筆記加了新段說明,上面兩處沒改。
- 下一個 session 的 AI 或審查者照手冊判斷「鏡頭裡哪些是可信的」,會判錯。新段是否算例外,手冊沒有答案。

具體失敗情境:審查者依 06 的說法,認定鏡頭除外部事實行外都來自主線、不會被分支作者影響。實際上殘留決策內容是分支作者寫的,一個提交就能改寫。段落有注入框和 300 字上限,但手冊把這個例外講成不存在。
佐證:
- ``skills/lumos-design-loop/templates.md:112-113``
- ``skills/lumos-project-notes/commands/06-代碼審與推送.md:31``
- ``scripts/lumos:48792-48800``(新段註解寫明「從頂端讀」)

severity: minor
blocking: 否 — 這是文件指向一個不存在的機制,不是程式壞掉,但它讓「審查席會被要求回答」的說法看起來有人把關。
引句:「沒答的席照漏答固定席處理」
問題:SKILL.md 說沒回答「這筆殘留的問答有沒有換編號或改字重問」的席,照漏答固定席處理。我 grep 了 `skills/`、`scripts/lumos` 和圖譜,「漏答」沒有任何對應的處理規則。`code-loop` 的折入和 `check` 都沒有去核對某席有沒有答固定席、更沒有核對殘留必答題。
具體失敗情境:五席都不答殘留那題,`code-loop pass` 照樣能留痕、推送照樣放行。實際上「把關」只剩 `pitfalls` 判 high 這一條,審查席的回答沒人驗。手冊讓人以為有人會抓漏答。
佐證:
- ``skills/lumos-code-loop/SKILL.md:32``
- ``skills/lumos-design-loop/templates.md:165``(只說「固定席必答」,沒有後續處理)

severity: minor
blocking: 否 — 「把關是新增殘留與新增問答要過高風險代碼審、審查席會看到」是兩件事,手冊把「審查席會看到」寫成了無條件。
引句:「這次推送新增了殘留,要過高風險代碼審(派工鏡頭把殘留決策與問答附給審查席逐條答)」
問題:這句寫成 `pitfalls` 判 high 就保證審查席看得到。實際上鏡頭段是否出現,取決於一串條件。
- 派工詞要有 `LUMOS-IMPACT` 標記。
- base 必須在主線歷史上,否則只附 `LUMOS-LENS:` 說明。
- hook 不能超時,超時只附一行說明,沒有殘留段。
- 殘留要已提交,因為鏡頭按 head 的 sha 讀,不像 `pitfalls` 在頂端是工作目錄時讀工作目錄那份。

另外,新增判 untestable 問答會升 high、鏡頭也會附段,但以下手冊都沒寫這一點,只寫「新增殘留」:
- `skills/lumos-project-notes/reference.md:558`
- `skills/lumos-project-notes/commands/06-代碼審與推送.md:19-20`
- `docs/methodology/圖譜即合約.md:95`

具體失敗情境:依手冊追加反例 c2,只做「問答 → 重審 → `--add`」,索引沒變,`pitfalls` 卻判 high。手冊找不到原因。標記寫錯的派工則靜默收不到殘留段,卻以為審查席已經看過。
佐證:
- ``scripts/lumos:49960-49975``(base 不在主線就擋下)
- ``scripts/hooks/claude/dispatch-lens-hook.py:~480-535``(超時只附說明)

severity: minor
blocking: 否 — 測試有守住主要條款,缺口在邊角,不是條款對不上。
引句:「G2 沒有新增殘留或問答 → 不出現那一小節與必答題」
問題:`t_dispatch_lens_residual_new_section` 只透過命令列 `dispatch-lens --no-cache` 跑。以下情況沒有覆蓋。
- 派工 hook 或 `--arm` 實際附上這段。
- 算不出來時固定印「⚠ 這次新增的殘留算不出來」加必答題。
- 超過 `_LENS_RESIDUAL_MAX` 條合約的「另有 N 條未列」。
- 帳列裡的 `case`、`checker`、`ts` 帶控制字元或偽造框線時的清洗。測試只偽造了決策內容的框線。

另一處:`t_guard_audit_residual_symlink_ledger` 只測符號連結,而 guard-kill 筆記寫「捷徑或有別的硬連結時不寫」,硬連結沒有測。

具體失敗情境:有人把 `_plain_label` 從 `case` 或 `checker` 欄位拿掉,所有測試照綠,偽造框線就能出現在審查席的派工詞裡。
佐證:
- ``scripts/test_lumos.py:5914``
- ``scripts/lumos:48851-48900``

## 已核對、沒問題的部分

- 計劃條款 S1、S5、S6、S9 列出的新測試名都存在於 patch 的測試檔裡。
- `governance/anchor-baseline.json` 的 `scripts/test_lumos.py` 雜湊,與 6b8d81bd 版的 `sha256` 一致。
- `schema` 版本改成 4 與測試期望一致。
- 手冊順序「問答 → `guard audit` → `decision-add` → `--add`」與程式的順序檢查相符。我看不出照做會被卡住的地方。

最高等級 major,blocking 1 條。
