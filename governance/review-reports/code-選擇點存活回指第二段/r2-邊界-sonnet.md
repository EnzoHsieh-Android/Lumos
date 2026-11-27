severity: minor

審完 `r2-repair.patch`。上一輪修補大致都修到了。這輪探針只有一個、整批紅、沒驗、exhausted、抽查 no_result 等極端輸入都沒找到會做出錯行為的洞。找到兩個小問題,都不阻擋。

**修到沒:**
- **探針:** 整批紅時只有一個探針就不記補償,多個才逐個單獨編,能編的那個才記。
- **沒驗:** 修改時間沒錯開或有還原沒錯開的檔,現在回 `_CHOICE_COMPILE_UNVERIFIED`,不記無效也不記補償。
- **抽查 no_result:** 不記 cov-audit。若抽到的是 none 行,`audit_unsure` 讓其餘 none 行改照跑全部守的測試。只有一行 none 時,它自己 `p["done"]` 已為真,不會卡住。
- **exhausted:** 兩處 `KeyError` 的路徑都改成 `.get` 加預設文字。
- **`.git` 檢查:** 用路徑各段比對,所以 `.github` 不會被誤擋。

**同類位置:** 全庫其他 `.git` 判斷(`scripts/lumos:14917`、`scripts/lumos:74324`)都先 `.lower()`,只有新加的這處沒有。

severity: minor
blocking: 否
`scripts/lumos:29410` 新的 `.git` 檢查沒有轉小寫,`.GIT`、`.Git` 這類大小寫變體會通過。macOS 預設不分大小寫,這種路徑會寫進真正的 `.git`。實際上 git 本身拒絕追蹤這種路徑,壞法的檔又來自改到的檔,所以很難觸發。檢查本身是漏的。最小重現:`units()` 吃一筆 `file` 為 `.GIT/config` 的配方,在不分大小寫的檔案系統上不會被略過(未能重現完整寫入,只就程式推論)。
引句:「if not target.startswith(self.c.wt_real + os.sep) or ".git" in Path(os.path.relpath(target, self.c.wt_real)).parts:」

severity: minor
blocking: 否
`scripts/lumos:80424` 壞法行讀檔頭改成只讀 `_CHOICE_COV_SRC_HEAD` 位元組後,檔頭剛好在 package 宣告中間切斷時,不會回 `""`,而是回被切半的套件名,而且沒有任何提示。重現:`"\n"*(32768-12)+"package com.example.foo.bar"` 切到 32768 位元組,`_choice_cov_pkg_of` 回 `'com/'`,整份檔則回 `'com/example/foo/bar'`。套件對不上 jacoco 的類別,這一行的覆蓋分類會偏。需要超過 32K 的檔頭才會觸發,所以只算小。另外 `scripts/lumos:80231` 的 docstring 還寫「壞法行的套件(讀整份檔)」,已過時。
引句:「head = text.encode("utf-8")[:_CHOICE_COV_SRC_HEAD].decode("utf-8", "replace")」

總結:最高等級是 minor
