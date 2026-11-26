severity: minor

上輪的七處修補我都看過,沒找到會做出錯行為的洞,只有兩個 minor。這輪沒有實際跑測試,結論都來自讀 patch 與 `scripts/lumos` 原始碼。

**已逐項確認沒問題**
- **單支上限比對**:`self.full` 與 `_kill_measure_singles` 的 `full` 都是 `max(600.0, c.floor)`,口徑一致。「剩下時限剛好等於單支上限」時 `cap == full`,不算截斷,正確。
- **分析輸出格式**:真正的分析腳本一定寫 `noclasses: files.isEmpty()`(布林)和 `nolines`,見 `scripts/lumos:79657`。所以 `type(...) is not bool` 不會誤殺真輸出;字串 `"false"`、數字 0、缺鍵、`nolines` 不是清單,都判成分析失敗。
- **清快取**:`subs[_CHOICE_COV_KEEP - 1:]` 在 0 / 1 / 2 / 3 個舊資料夾、這次的 at_sha 已存在或尚未建立時,都剛好剩 2 個。符號連結不跟、不刪。
- **Robolectric 零紀錄**:`cached()` 讀回壞資料時會刪除重量。快取檔為空時 `_choice_cov_exec_classes` 回 None,先短路,不會走到 `robo_zero`。
- **原子寫入**:`_write_bytes_atomic` 的暫存檔名帶 pid 與 uuid,不會撞名;`OSError` 被 `store` 接住,回 None 後記「覆蓋資料沒產出」。
- **Groovy 任務名**:變體名由 `test<變體>UnitTest` 取出,多段 flavor 如 `FreeDebug` 首字母已大寫,`*.toString()` 後比對正常。

severity: minor
blocking: 否
`scripts/lumos:29299`:`red_rerun` 在「掛覆蓋跑滿單支上限」時,先斷路再跑不掛覆蓋的重跑。如果那支測試連不掛覆蓋也本來就掛住或超過 600 秒(`plain[3]` 為真),整批覆蓋照樣已被停掉,其餘壞法全部退回跑全部測試。上輪的「連續 3 支」門檻是為了擋這種單支誤觸發,這次把它拿掉了。後果是變慢而不是判錯,且斷路原因有印。建議把斷路移到重跑之後,只在「不掛綠」時才觸發。
引句:「if res[3] and not self.tripped:   # 掛覆蓋跑滿單支上限:比掛覆蓋紅更強的訊號,當場斷路,不等連續 3 支(代碼審 r2 資源 s2)」

severity: minor
blocking: 否
`scripts/test_lumos.py` 的 `t_choice_cov_groovy_dep`:本機沒有 Gradle 附的 Groovy 或 java 時,只印一行說明就 `return`,測試仍然綠,等於只剩靜態正則。正則只擋「`in [ …${… ]`」這一種字面寫法,把 GString 放進變數再 `in` 比對就抓不到。這個測試在 CI 上到底有沒有真跑 Groovy,從 patch 看不出來。這屬於覆蓋面可以更完整,不是保護必要行為的缺口。
引句:「print("    (本機沒有 Gradle 附的 Groovy 或 java,r2 c1 只做靜態檢查)")」

總結:最高等級是 minor
