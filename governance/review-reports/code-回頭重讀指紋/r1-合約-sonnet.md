severity: minor

計劃〈要一起改的說法〉列的每一處都有改到,而且改對了。我逐項對過:

- **程式說法**:回頭重讀擋下時印的那句已改成新說法,`_note_reread_contrast_fp` 的 docstring 已標 v1 並說明何時用。
- **手冊**:`skills/lumos-project-notes/commands/06-代碼審與推送.md` 的「程式改了就要重判」與消費專案 CI 兩段都改了。
- **圖譜筆記**:`Systems/筆記內容審`、`Systems/pitfalls-code-loop`、`Projects/守檔筆記對照改動_計劃`、`Projects/舊句兩道轉擋_計劃` 都就地改成新事實,並留帶日期的舊理由。
- **測試**:`t_note_audit_reread_check_reminds` 的翻紅釘已拆成 v1(⑩)與 v2(⑧)兩條。`t_reread_block_layer1` 的字串也跟著改。
- **殘留**:我用 grep 找舊說法(整個 repo,排除 review-reports),沒有漏掉的。
- **S1–S19 測試**:十九支測試都存在。S4 寫死十六進位字面值。
- **本機實跑**:`-k reread_check_reminds` 12 條全綠,但我沒有親手做翻紅變異。
- **合約**:沒有破壞 ★INVARIANT★ 行。固定席上被牽連的合約,這次改動都沒碰。

沒有 blocking 的問題,只有下面三條 minor。

severity: minor
blocking: 否 — 只是計劃筆記的敘述互相矛盾,程式與測試沒受影響
引句:「CHANGELOG 那筆放在 v1.3 底下、標日期(檔頭說沒發版的不進,但計劃要加一筆、版號不升)」
問題:同一篇計劃〈要一起改的說法〉改成「CHANGELOG 不加」,並註明 2026-10-14 實作時更正。但同一篇〈實作紀錄〉「跟計劃字面不同的小決定」這一行還寫「CHANGELOG 那筆放在 v1.3 底下」。這次的差異裡沒有動 `CHANGELOG.md`,所以這句是錯的。
失敗情境:下一個 session 讀到〈實作紀錄〉,會以為 CHANGELOG 已有這一筆。要嘛去 `CHANGELOG.md` 找不到而懷疑有人漏提交,要嘛照字面補一筆,違反 `CHANGELOG.md` 檔頭「沒發版的不進」。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/回頭重讀指紋不因主線前進失效_計劃.md:121` ``(〈實作紀錄〉那一行)與同檔「CHANGELOG 不加」那一行互相矛盾。

severity: minor
blocking: 否 — 手冊少講一個例外,不會讓閘判錯
引句:「主線往前、rebase 上去而你的改動沒變,不用重判」
問題:手冊這句是無條件的。守檔筆記計劃已明寫 v2 的指紋含作者改動前後三行,主線若改到那三行之內,指紋就會變。手冊面向消費專案的作者,卻沒講這個邊界。
失敗情境:作者以為只要自己的改動沒變就不會被重列。主線改了緊鄰那一段的幾行,他 rebase 後被重列,會當成工具誤報。
佐證:``file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:75` ``;對照 ``file: `docs/lumos-toolchain-knowledge/Projects/守檔筆記對照改動_計劃.md:162` `` 的「含前後三行」。

severity: minor
blocking: 否 — 只是測試名稱過時,斷言本身對得上
引句:「def t_reread_fp_ff_main_uses_v1_field」
問題:r3 已把「紀錄另記舊指紋的欄位」拿掉,這支測試現在斷言的是 `covered_by` 為 `{"v1": 0, "v2": 1}`,也就是靠 v2 紀錄判已對照。名稱卻還寫 `uses_v1_field`。計劃條款 S19 也用同一個舊名。
失敗情境:之後有人看到名稱,以為還有 v1 欄位的行為要維護,或者照名稱去找已刪掉的欄位。
佐證:``file: `scripts/test_lumos.py:` ``裡的 `def t_reread_fp_ff_main_uses_v1_field`;計劃檔 S19 那一行。

最高等級 minor,blocking 0 條。
