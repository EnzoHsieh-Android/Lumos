severity: major

第 4 輪文件與測試修補把「只准問一次是方便、真把關是新增殘留的推送過高風險代碼審」寫進了多處文件,說法大致一致,但有一處空洞,和幾處殘留的舊說法。我只讀文件、程式與測試修補,沒有執行測試。

我照手冊順序走了一遍:問答、`guard audit`、`decision-add`、`guard residual --add`、推送。這條路走得通,沒有被新規則卡住。`--add` 現在比對治理帳裡兩筆事件的時間戳記,不再比戳記日期;一般用法下 `guard audit` 一定會記帳。失敗路徑(帳寫不進去)會明確提示「重審」,不會卡死。

severity: major
blocking: 是 — 文件宣稱的「真正把關」沒有任何手冊步驟或機制讓審查席真的去查,把關可能退化成「隨便跑一次代碼審就過」。
引句:「真正的把關是新增殘留的推送要過高風險代碼審」
問題:各處文件都說「審查席看殘留決策與問答」(`reference.md`、計劃、`pitfalls-code-loop.md`、`guard-kill.md`、`lumos` 提示文字)。但 `skills/lumos-code-loop/` 底下完全沒提殘留,派工範本也沒要審查席檢查「新增殘留是否換編號重問」。現有機制只有兩樣:`pitfalls` 因「新增了殘留」升 high,以及派工鏡頭的殘留徽章。升 high 只要求有一次代碼審留痕,不要求任何席去看那筆殘留決策或 `residual-ask` 的帳列。
具體失敗情境:編排者換編號 c2 重問,拿到 untestable 後記殘留。推送升 high,走一輪不含「殘留」關鍵字的普通代碼審,審查席報告沒提殘留,`code-loop pass` 照樣放行。
佐證:``skills/lumos-code-loop/reference.md` 全文沒有與殘留審查相關的指示(grep 只命中第 494 行的歷史註記)``。把關的真實強度是「要跑一輪審」,不是「審查席會看」,文件應照實寫,或在派工單加一條必查項並綁測試。

severity: minor
blocking: 否 — 只是文字殘留,不改變行為。
引句:「它的模型與日期寫進殘留決策並由寫入指令檢查」
問題:計劃「守衛面」那行(`Projects/審查收斂規則_計劃.md`)同一句裡還留著「它說測得到就照它補測試,不准換人重問」。修補在這一行補了「方便,不是保證」,但沒把「不准換人重問」刪掉,同一行前後自相矛盾,前半句仍像機械保證。
失敗情境:下一個 session 讀到「不准換人重問」,會誤以為換編號、換代理重問會被擋。
佐證:``docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:79``

severity: minor
blocking: 否 — 提示文字誤導,不影響判定。
引句:「不能換代理重問到聽見想要的答案{tail}」
問題:`residual-ask` 被擋時印的錯誤訊息,與 `--help` 的說明「同一個反例已經記過就回 2(不能換代理重問)」,仍是「擋得住重問」的口氣。修補只動了 `{tail}`,沒把這句改成「這個編號已問過;換編號仍問得到,把關在推送」。
失敗情境:使用者看到擋下訊息,誤以為換代理重問被機械禁止,而不知道換編號就繞得過去。
佐證:``scripts/lumos:18999``、``scripts/lumos:53761``、``scripts/lumos:53145``

severity: minor
blocking: 否 — 測試強度不足,但條款方向沒錯。
引句:「寫明只准問一次是方便、把關在新增殘留的推送過高風險代碼審」
問題:`r3 G1` 文件檢查只在四個檔各自「全文任一處」找符合 `只准問一次[^。\n]{0,20}方便` 的字串,加上 `新增殘留的推送要過高風險代碼審`。`reference.md` 第 558 行的「只准問一次」距離「方便」超過 20 字,是靠第 591 行的另一句才過關。檢查完全沒涵蓋 `design-loop.md`、`guard-kill.md`、`pitfalls-code-loop.md` 和 `scripts/lumos` 的提示文字,上面兩條殘留因此測不到。
失敗情境:有人把某處改回「只准問一次=保證」,只要同檔另一處仍有那句話,測試照綠。
佐證:``scripts/test_lumos.py`(patch 內 `t_reference_audit_q3_rules` 新增段)``

severity: minor
blocking: 否 — 條款與測試的對應有缺口。
引句:「應在那條合約行尾加 `[residual:Projects/a_計劃#d12]`」
問題:條款 S8(審計五問段應寫的內容)沒有要求「只准問一次是方便、把關在新增殘留的推送」,但綁定的 `t_reference_audit_q3_rules` 已在檢查這件事。S9 也沒寫「改字換指紋重問後記殘留,該推送升 high」,但 `t_residual_testable_sticks_to_case` 與 `t_pitfalls_residual_added_needs_review` 已在測。測試比條款多守,條款寫的和測的並非一一對上。
佐證:``docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:74``、``docs/lumos-toolchain-knowledge/Projects/審查收斂規則_計劃.md:75``

最高等級 major,blocking 1 條。
