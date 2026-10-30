severity: clean

delta(130 行)對齊兩份兄弟範本,沒有帶進新的不一致。整份也沒發現「第二種做法」或跨層直呼。

**1. 分層與依賴方向:對齊。**
- delta 新增的 `_android_template_block()` 位置、參數和回傳都與 `_ddd_template_block()` 一致。對照 `scripts/test_lumos.py:15449-15457`(無參數、自帶 `_need_src`、「## 範本」切節、markdown 圍欄、`check("前置…")` 後回傳 body)與 `scripts/test_lumos.py:109195`。
- 測試只讀範本檔,沒有跨到產品碼,呼叫方向與兄弟一樣。
- `t_arch_target_android_template_valid` 的結構(`mkvault`、`run lint`、`_arch_target_note_rules`、換佔位前後各一次)與 `scripts/test_lumos.py:109160-109176` 的前端版同形。
- `t_arch_target_android_template_konsist_names_match` 沒有用輔助函式,直接內嵌 `_need_src` 加 `read_text` 加 `split`。兄弟測試裡找不到「讀非範本小節」的共用輔助函式。`_ddd_template_block` 的註解自己說這是「同其他讀說明檔的測試」的寫法。所以這是既有的做法,不算第二種。

**2. 命名與錯誤處理:對齊。**
- 輔助函式命名 `_android_template_block` 對應 `_ddd_template_block`。
- 測試名 `t_arch_target_android_template_*` 沿用 `t_arch_target_ddd_template_*` 的前綴與後綴。
- 失敗走 `check(...)`,與兄弟相同。
- `[test:<測試名>]` 的寫法已改回與兩份兄弟範本一致,見 ddd-template 的 `:63` 行與 frontend-template 的 `:58` 行。
- 範本 `:224` 另外補了「測試不在預設平台目錄底下時,先宣告平台再寫 `[test:<平台>:<測試名>]`」。這是附加說明,沒有改掉主寫法。

**3. 第二種做法:無。**
- r1 的兩條 minor(自創的小節切割工具、`[test:<平台>:…]` 寫法)都已收回。
- Konsist 骨架是這份範本新增的內容類型,兩份兄弟範本沒有對照。⚠ 交編排者:r1 報告已記載編排者判它是計劃要的新能力,我沿用這個判斷,不列發現。

不對齊共 0 條,其中 major 0 條
