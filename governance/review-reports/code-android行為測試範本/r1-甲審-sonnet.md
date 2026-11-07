severity: minor

審查結論:型錄 68 列的改值正確,新增的三支測試也跑得過(`-k kotlin_test_templates`、`-k kotlin_catalog_c_rows` 皆綠)。我找到三條 minor。角色鏡頭的 `be-api-compat` 與 `be-authz` 都不適用,因為這批改動是離線自檢工具與文件,沒有對外 API 或端點。

我實際驗過的部分:
- 用 `check.py` 的 `_MAIN_ROW_RE` 與 `_cells` 讀表,共 473 列,欄數全是 12。
- 級含 C 的列有 68 列,「行為測試或正向約束=」的分布是:範本 T0=10、T1=8、T2=7、T3=2、T4=2、T5=3;未接(儀器批) 25、未接(架構測試後續計劃) 3、未接(Ktor 範本後續) 1、不接(代碼審或真機) 7。沒有「批五」,也沒有一列被改錯或漏改。
- 逐列比對 diff 前後:68 列只有通電批次那一格變動,其他欄位都沒動。
- `template_problems()` 對真檔回傳 `[]`。
- T1 對 T10 沒有問題,因為 `T\d+` 是貪婪比對。
- 驗證紀錄的格數對得上:43 個非全綠格加 14 個全綠格等於 57。

### F1 範本檔的 `## T<n> ` 標題比對不認程式圍欄,圍欄裡的假標題會讓缺節被放過
severity: minor
blocking: 否
引句:「have = set(re.findall(r"^## (T\d+) ", TEMPLATES.read_text(encoding="utf-8"), re.M))」

我在暫存複本重現:把真的 `## T3 ` 標題改名為 `## T3X`,再在〈怎麼用〉節加一段圍欄,內容是 `## T3 範例`。`template_problems()` 回 `[]`,引用 T3 的 STATE-6 和 STATE-26 沒被報出,但實際上已經沒有 T3 那一節。

反方向也要留意:標題寫成 `## T4：HTTP 邊界`(全形冒號),或寫成單獨一行 `## T4`,會被誤報為缺節。這個方向是安全失敗,只是訊息不好懂。

要修的話,先剝掉圍欄再比對,或者只認 `## T<n> ` 開頭的行,並要求它在圍欄外。`t_kotlin_test_templates_sections` 目前沒有圍欄案例。

### F2 範本檔編碼錯時 `template_problems` 直接丟例外,不報 (列編號, 原因)
severity: minor
blocking: 否
引句:「have = set(re.findall(r"^## (T\d+) ", TEMPLATES.read_text(encoding="utf-8"), re.M))」

我把範本檔寫成 `b'\xff\xfe## T0 x'` 後呼叫 `template_problems()`,得到 `UnicodeDecodeError`。`--catalog-only` 會印出堆疊,不會印「型錄問題 N 個」。

同函式裡,檔案不存在已經有 `("<templates>", "找不到範本檔")` 的處理,但編碼錯沒有對應的處理。型錄本身的 `read_text` 也有同樣問題,不過那是舊債。三支新測試都沒有編碼錯的案例。

### F3 測試品質標準新句子和同一清單裡既有的 Turbine 建議互相衝突,指路測試只比對檔名
severity: minor
blocking: 否
引句:「社群:用 Turbine 時,每個發出的值都要收掉,或用 `cancelAndIgnoreRemainingEvents()` 明講不管;錯誤用 `awaitError()` 收;不要用 `runCurrent()` 去推 Turbine。」

這是 `test-quality-standard.md` 的 Flow 小段裡既有的一行。同一段的結尾,diff 新增了這一行:
引句:「Turbine 自己的檢查(`awaitComplete()`、`awaitError()`、`expectNoEvents()`)失敗丟 `TurbineAssertionError`,收證工具不算斷言失敗;」

讀者會同時看到「錯誤用 `awaitError()` 收」和「`awaitError()` 失敗收證不算斷言」。前者應該補上「要當抓到錯的那一步時,改用 `awaitEvent()` 取事件再 `assertEquals`」,或指到新句。

測試面的缺口:`Systems/test-quality-cli` 新增的 WHY 行寫「並寫下範本實驗踩到的兩個坑」,綁的測試是 `t_kotlin_test_templates_linked`。但這支測試只檢查「協程」「Flow」兩小段含 `test-templates.md` 這串字。我的推演(未在複本實跑):把兩個坑的描述整句換成別的文字、只留檔名,測試仍然綠。SKILL.md 的連結目標也沒驗,例如 `(test-template.md)` 打錯字也會過。

總結:最嚴重是 minor(圍欄內假標題讓缺節被放過、編碼錯丟例外、新舊 Turbine 建議互相衝突且測試只比對檔名),會擋 0 條
