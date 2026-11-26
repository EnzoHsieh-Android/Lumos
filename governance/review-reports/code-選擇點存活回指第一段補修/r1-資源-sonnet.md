severity: minor

我只讀了 diff 和 `scripts/lumos` 的相關行,沒有實際執行。續跑快取的清理沒有問題:`.base.json` 與 `.exec` 放在同一個 `choice-cov/<at_sha>/` 資料夾,整個資料夾由 `_choice_cov_prune` 依 at_sha 整份刪除(`scripts/lumos:79935`),不會累積成孤兒。`.base.json` 單檔大小也有界(輸出尾巴 4000 字,讀回時上限 64KB)。

severity: minor
blocking: 否
`scripts/lumos:79836`(新增的 `_choice_cov_src_pkgs`)走訪量的上限沒有涵蓋非原始碼檔案。
引句:「    for d, subs, files in os.walk(str(root)):」
場景:`_CHOICE_COV_SRC_MAX` 只計 `.kt` 與 `.java` 檔,其他檔案與目錄沒有上限。平台根底下若有大型非原始碼目錄,例如 `Pods`、`.dart_tool`、`vendor`、`.venv`,這些都不在 `_CHOICE_COV_SRC_SKIP` 裡,會被整個走訪。這段走訪不受 `self.remaining()` 約束,每個平台組的 `_measure` 也會重走一次(`scripts/lumos:29144`)。後果只是慢,不會判錯。
建議:結果快取到 `_KillPrep` 上、一個平台只算一次,並加走訪目錄數或秒數的上限。
未能重現(沒有大型測試樹可跑)。

severity: minor
blocking: 否
`scripts/lumos:79848`。超過 20000 檔時只印出已收的套件、沒有任何訊息,而且走訪順序是任意的。
引句:「            if seen > _CHOICE_COV_SRC_MAX:」
場景:大型 monorepo 的平台根底下主程式超過 20000 個 `.kt` 與 `.java` 檔時,後面模組的套件不會進集合。Robolectric 測試只碰這些模組時,專案類別有紀錄數會是 0,被判成「覆蓋接不起來」。`settle` 的「沒有一支記到專案類別」判斷在整批都落在漏掉的套件時也會誤斷路,整批退回跑全部守的測試。結果是正確但比不開覆蓋更慢。
建議:截斷時印一行警告,或直接視為算不出來,不要默默用殘缺集合。
未能重現。

severity: minor
blocking: 否
`scripts/lumos:79848`。`open(..., "rb")` 之前沒有檢查檔案類型。
引句:「                with open(os.path.join(d, f), "rb") as fh:」
場景:根底下若有名為 `x.kt` 或 `x.java` 的具名管道,`open` 會一直卡住,而且不在任何逾時之內。這情況很罕見。
建議:先 `os.path.isfile` 再開。
未能重現。

總結:最高等級是 minor
