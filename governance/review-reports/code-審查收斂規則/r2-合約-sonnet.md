severity: minor

我逐字照手冊的順序,用 `_rc_repo` 的暫存庫從頭到尾真跑了一次,工具每一步都沒擋。順序是 `guard residual-ask` 判 untestable、`guard audit` 蓋 `[audit:]`、`decision-add` 記殘留決策(得 `Projects/a_計劃#d16`)、`guard residual --add`,最後 `doctor` 回 0 問題。`python3.14 scripts/test_lumos.py -k residual` 跑出 138 passed、0 failed。`governance/anchor-baseline.json` 裡 `test_lumos.py` 的雜湊與檔案實際的 sha256 相同。`lumos lint` 審查收斂規則_計劃 回 0 問題。跑完的暫存庫我已刪掉。

目前沒有 blocking 的缺口,只有下面三條 minor。

severity: minor
blocking: 否 — 屬驗收條款與測試對不齊,不影響現行行為
引句:「推送範圍改到殘留索引(起點或頂端版本)裡列的檔時」
問題:S6 條款沒有跟著 r1 的修正更新。r1 後綁定測試所在的檔,要 diff 碰到綁定測試名才升 high,只有 about_code 整檔算。條款仍寫成列的檔一律判 high。
失敗情境:
- 綁定的 `t_pitfalls_tier_high_on_residual_index` 用的索引條目沒有 `tests` 欄,走的是舊索引整檔命中的退路。
- 因此 r1 新增的行為(測試名比對、起點有頂端沒有、頂端索引壞掉)只由 `t_pitfalls_tier_high_on_residual_removed` 和 `t_pitfalls_residual_test_file_needs_bound_test` 守。這兩支沒有被任何 `[test:]` 條款綁定。
- 把測試名比對整段拿掉,S6 綁的測試照綠。
- 同樣沒綁的還有 `t_residual_identity_normalized`、`t_guard_residual_index_write_failure` 等,它們只列在 guard-kill 的 TEST 行。
- 第 3 問順序的測試 `_order_ok` 只檢查手冊的審計段、`圖譜即合約.md` 與計劃。`06-代碼審與推送.md` 的順序行、`design-loop.md` 的 KEY 行沒人守,抽換順序不會紅。
佐證:``file: `scripts/test_lumos.py:4742` ``、``file: `docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:37` ``

severity: minor
blocking: 否 — 屬回頭條件格式與涵蓋範圍,不影響功能
引句:「也沒有核對 kill 帳上那條配方真的是」
問題:「殘餘風險」那條承認了四個風險,卻只替其中兩個寫了回頭條件。
- 已寫回頭條件的:換編號重問、改字重問。
- 沒有回頭條件的:`--checker` 只靠自報字串、努力補過測試仍殺不掉卻沒核對 kill 帳。
- 規則 4 要求把承認風險那一句搬成獨立一行回頭條件、原行刪掉那一句。這條沒搬,原行還留著「機械驗不到」「只靠自報」。
- 收尾那句「靠留痕事後量」對後兩個風險是空頭承諾,REVISIT 的數法量不到它們。
- REVISIT 行緊接在 `- ` 項目後面,沒有列表前綴,markdown 會把它當成上一條的續行。doctor 與 lint 倒是認得。
失敗情境:2027-01-15 到期時,REVISIT 只會去數編號與改字,自報偽造與 kill 帳沒核對這兩項永遠沒人回頭看。
佐證:``file: `docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:79` ``、``file: `docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:80` ``

severity: minor
blocking: 否 — 屬手冊說法比工具實際把關寬,工具不會擋下合法流程
引句:「第 ④ 步寫入當下驗前三步都做了」
問題:`--add` 只確認三件事:問答存在且判 untestable、決策還在、合約行有任一 `[audit:]`。它不比較先後,也不檢查 `[audit:]` 是不是在問答之後才蓋的。
失敗情境:合約在上一輪已經有舊的 `[audit:]`,審計員在同一輪新判了「要記殘留」。編排者跳過步驟 2 重新蓋章,照樣 `--add` 成功,但手冊說「驗前三步都做了」。實際上驗的是存在,不是順序。
佐證:``file: `scripts/lumos:18980` ``(`_residual_check` 內只呼叫 `invariant_audit_refs(body)` 看有沒有)

總結:最高等級 minor,blocking 0 條(共 3 條 minor)。
