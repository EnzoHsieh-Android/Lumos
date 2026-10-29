severity: minor

**1. 分層與依賴方向:跟鄰居一樣嗎?**
一樣。新增的跳過條件加在同一條 `caller_step` 子查詢裡,和 `f.so != 'libart.so'` 並排,沒有新增 CTE,也沒有新層或新的呼叫方向。名字比對用 `coalesce(f.fname, '') != 'art_jni_trampoline'`,對照同檔 `fr2` 裡配置器名單的 `fname in (...)` 與 `coalesce(fname, '') != ''`,都是在 SQL 內用精確名字比對。修補差異沒有動 SQL,只改測試、PITFALL 行和計劃的 REVISIT 行,沒帶進新的分層差異。測試的路徑常數 `_MS_BOOT`、`_MS_BOOT_FW`、`_MS_VDEX` 放在原有 `_MS_*` 區塊,這是把原本函式內的區域變數提升出來,寫法和同區塊一致。對照:file: `scripts/templates/android-stability-native.sql:46-52`、file: `scripts/test_lumos.py:18475-18480`

**2. 命名與錯誤處理:跟鄰居一樣嗎?**
基本一樣,只有一處不對齊(finding 1)。
- 測試函式名 `t_android_native_query_caller_jni_trampoline` 沿用 `t_android_native_query_*`。
- 結果彙整用 `by = {s[0]: s ...}`,和 `t_android_native_query_caller` 的寫法相同。
- `_ms_native` 假表工具沒有改動,只是多餵了幾條呼叫鏈。
- 驗證紀錄有 `system_refs`(Verification 目錄約 320 篇裡有 42 篇用)和「沒驗到的」小節(其他驗證紀錄也有這個標題),都不是新做法。
- 逃逸帳新條目的欄位和既有的 `"stage": "實作"` 手動條目一致,共 8 筆。
- 計劃新增的 REVISIT 行是「日期 + 要看什麼 + 有就怎麼做」,和相鄰行同形。

**3. 第二種做法:有沒有引入專案裡原本沒有的做法?**
沒有。上一輪判過的「按 .oat 整個跳過」這條路,這次被改成只比對精確名字,和同檔配置器判斷「.so 加名字並用」是同一種做法。測試新增了 `art_named`(App 自己的套件名以 art 開頭)和 `no_symbol` 這兩條反例,也沿用 `_ms_native` 的鏈條格式。

**finding 1. PITFALL 根因行寫了一個沒查的未知,卻沒有搬成獨立的回頭條件行**
severity: minor
blocking: 否
引句:「同一台裝置鎖定畫面那次的呼叫鏈沒有這一框(什麼情況下才出現沒查)」
file: `docs/lumos-toolchain-knowledge/Projects/原生記憶體增長提示_計劃.md:86-89`(既有 REVISIT 行都是獨立一行、帶日期;這次新增的那條只管「其他 ART 過渡框架」,沒有管「跳板什麼時候才出現」)
專案 CLAUDE.md 鐵則 4 要求把「沒查」這類會過期的話搬成獨立的 `REVISIT:` 行,沒有搬就沒人會回頭。⚠ 這個未知也許不需要追,但那樣就該刪掉這句,而不是留在根因裡。

不對齊共 1 條,其中會擋推送的 0 條
