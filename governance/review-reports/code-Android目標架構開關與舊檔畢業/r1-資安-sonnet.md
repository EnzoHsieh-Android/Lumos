severity: clean

已看,無可利用的洞。逐類結果如下:

**① 提示注入:已看,無。**
- 清單內容只用在集合比對(`nfc(f) not in legacy`)。
- 進到 doctor 和 code-loop check 的文字只有計數(`len(legacy)`、`gone`、`stray`、`len(gone)`)和固定句子。
- 清單內的路徑字串沒有被回顯進派工詞或 hook 附加段。

**② 讀寫與執行越界:已看,無。**
- 新程式只讀:`_arch_legacy_at` 走 `_lumos_config_at_ref`,路徑是常數 `.lumos/arch-legacy.json`,透過 `git show ref:路徑` 或 `cat-file` 讀 git 物件。
- 清單裡的路徑沒有拿去開檔或寫檔,只拿去比對。
- 檔案內容是符號連結時,git 回傳的是連結文字本身,不會跟過去。
- 沒有新增 shell 插值、hook 執行、下載來源,也沒有密鑰或信箱。我只掃了測試檔 patch 裡有沒有 subprocess、shell、environ、token、secret 這幾個關鍵字,沒看到命中。

**③ 非刻意、一步就能繞過的守衛:已看,無。**
- 審查端讀的是可信版本(`_trusted_decl_ref`)的清單。被審分支自己在 HEAD 改清單,只能讓畢業的檔照目標審,審得更嚴,不會放寬。
- 畢業要同時滿足三件事:HEAD 的宣告與可信版逐字相同、沒有警告、HEAD 版清單讀得懂。任何一件不成立就維持照鄰居審,不會因為清單壞掉而意外放行。
- 可信版的清單不存在或讀不懂時,整份清單失效,檔案照目標審,方向是審得更多。
- 設計審那條路(`head=None`)只扣不放,不開畢業口。
- 我找不到誰、從哪、送什麼、拿到哪道守衛被意外走過的路徑。
- 要讓放寬生效,得先把清單合併進主線,這屬刻意偽造或需要人裁的範圍,不報。

最嚴重 severity: clean;blocking 條數: 0。
