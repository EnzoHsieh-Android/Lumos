C1 ✅ lint 掃 summary 中以 `KEY:` 起頭的行,三訊號(_U_DIST/_U_ENT/_U_MOD)同現、無 `[test:`、非 `★DEBT★` 才 warn,訊息明確提示「若真是通則,寫成一支列舉所有實例的測試(適應度函數)並 [test:] 綁上」 | 證據: scripts/lumos:2763-2776(迴圈 `for _ln in summ.splitlines()` → `if not _s.startswith("KEY:")` 2765 → `if "[test:" in _s or "★DEBT★" in _s: continue` 2767 → 三訊號 `and` 判定 2769-2770 → warn 訊息 2772-2776)

C2 ✅ 分配式量詞詞表逐字相符 | 證據: scripts/lumos:2759 `_U_DIST = r'(所有|每個|每支|每一|各個|凡是|凡|一律)'`

C3 ✅ 程式實體詞表逐字相符 | 證據: scripts/lumos:2760 `_U_ENT = r'(Service|Repository|Controller|Job|服務|排程|查詢|端點|入口|呼叫點|實作|模組|節點|欄位)'`

C4 ✅ 義務語氣詞表逐字相符 | 證據: scripts/lumos:2761 `_U_MOD = r'(必須|都要|都必須|皆須|應該|一律要|要寫|要帶|不可|禁止)'`

C5 ✅ 三條消音路徑皆在程式碼中可對應:`[test:` 與 `★DEBT★` 為程式碼直接 continue 跳過,warn 訊息明文提「改寫語氣消音」 | 證據: scripts/lumos:2767(`if "[test:" in _s or "★DEBT★" in _s: continue`)、2775(訊息「★請改寫成限定範圍★」)、2776(「誤報可加 [test:] 或改寫語氣消音」)

C6 ❓ 「單看量詞」命中率 17% 有程式碼註解佐證,但「45 行」這個絕對數字在可讀範圍(scripts/、test_lumos.py)找不到逐字出處;261×17%≈44.4,無法對出恰好 45 這個整數,且該精確計數應只存在於被禁讀的知識圖譜 fixture/Verification 節點內 | 證據: scripts/lumos:2754-2755(「LandmarkMember 30 篇 Systems / 261 條 KEY 行…單看量詞…→ 命中 17%」,無附「45 行」字樣);scripts/test_lumos.py:5335,5371(同樣只寫 17%,無絕對行數)

C7 ✅ 三訊號同現後命中率降到 1%(5 行),其中 3 條真陽性,逐字相符 | 證據: scripts/lumos:2756「收緊成「分配式量詞 + 程式實體 + 義務語氣」三者同現 → 命中 1%(5 行),其中 3 條真陽性」

C8 ✅ Check U 對應 6 條 `check()` 斷言(跨 5 個測試函式:t_checku_fires_on_universal_claim_without_test/t_checku_silent_when_bound_to_test/t_checku_silent_on_debt/t_checku_needs_all_three_signals[內含 2 條]/t_checku_ignores_non_key_lines),且明確含「只有量詞不吵」與「缺義務語氣不吵」兩條防噪音斷言 | 證據: scripts/test_lumos.py:5346-5388(6 個 `check("Check U: …")` 呼叫,行 5350,5358,5366,5374,5377,5388);5374「只有量詞(用詞規範)不吵」、5377「缺義務語氣(純描述)不吵」

C9 ✅ Check U 一律 `warns.append`(非 `errs.append`),而 `cmd_lint` 回傳值只受 `errs` 影響(`return 1 if errs else 0`),warn 不擋 | 證據: scripts/lumos:2771-2776(warns.append)、2786(`return 1 if errs else 0`)、2785(「warning 不阻擋,但建議補」)

C10 ✅ 兩個 Verification 節點檔案皆存在(僅核對檔名存在性,未讀取內容) | 證據: docs/lumos-toolchain-knowledge/Verification/2026-08-12_CheckU_過度概化守衛.md、docs/lumos-toolchain-knowledge/Verification/2026-08-12_通用性修正_profile化與歷史重放.md(find 命中,檔案存在)

C11 ✅ 結構上相符:Check U 的三訊號判定邏輯內嵌於 `cmd_lint`(scripts/lumos:2595 起),即 `lumos lint` 子命令本體——寫入層(write path)驗證函式;`Systems/lumos-cli-write.md` 節點檔案存在但內容屬禁讀範圍,DEP 邊本身未逐字核對 | 證據: scripts/lumos:2595(`def cmd_lint(env, node):`)包住 2746-2777 的 Check U 區塊;docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md(檔案存在,未讀內容)

C12 ❓ check-t-sentinel 對應機制(★INVARIANT★ 缺 [test:] 即報)確有程式碼佐證,但「Check U 是它的前一哩」這個定位敘述在可讀範圍(scripts/、skills/)找不到逐字或等義表述,只能靠程式碼結構(Check U 掃所有 KEY: 全稱宣稱、Check T 只管已標 ★INVARIANT★ 者缺 [test:])推論兩者互補,無法核實「前一哩」這個關係定性本身 | 證據: scripts/lumos:705(「Check T: ★INVARIANT★ 合約測試綁定」)、2725(「裸 ★INVARIANT★(沒綁 [test:],Check T 會擋)」);grep 全庫(排除知識圖譜)無「前一哩」或「check-t-sentinel」字樣

C13 ✅ 對照表三項機制描述皆與程式碼相符:Check N 靠使用者自訂語法 `<!--lumos:count=N re=... in=...-->`(非詞表,language-agnostic);Check Y 靠 `load_symbol_profile` 的 shape_re + neg_lexicon,依 repo `.lumos/config.json` 之 `symbol_profile`(csharp/python 等)profile 化;Check U 三詞表為程式碼內寫死常數、無任何 `load_*_profile` 呼叫 | 證據: scripts/lumos:1150-1152(Check N 語法);1936-1954(`load_symbol_profile` 讀 `.lumos/config.json` 的 `symbol_profile`/`neg_lexicon`,csharp/python 等 profile);2759-2761(Check U 三詞表為模組層級常數,區塊內無 profile 載入呼叫)

C14 ✅(部分逐字) CustTransfer/滿額贈「折疊守衛(通則)」實例及日期(2026-06-02 漏補、07-21 使用者回報)、自稱通則、零 [test:] 皆與程式碼註解相符;但 C14 引句「凡顯示/計數該表的查詢都必須折疊」與程式碼裡實際引用/測試 fixture 的字句「凡顯示該表的查詢都必須按事件鍵折疊」不完全逐字一致(可能是圖譜原文的另一種轉述,圖譜原文本身禁讀無法逐字核對) | 證據: scripts/lumos:2756-2758(「含 CustTransfer/滿額贈 的「折疊守衛(通則)」(自稱通則、零 [test:],且節點自己記載 2026-06-02 漏補一路到 07-21 才被使用者回報)」);scripts/test_lumos.py:5347-5348(測試 fixture 引句「凡顯示該表的查詢都必須按事件鍵折疊,否則一事件顯示 N 列」)

C15 ✅ 5 命中中 3 真陽性,故 2 誤報,與 C7 同一程式碼註解可交叉算出(5-3=2) | 證據: scripts/lumos:2756(「命中 1%(5 行),其中 3 條真陽性」)

✅9 ❌0 ❓3 ⏭0
