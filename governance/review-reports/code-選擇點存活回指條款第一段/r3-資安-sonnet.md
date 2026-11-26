severity: clean

這輪(r3 修補差異加上 r3 完整快照裡的 `scripts/lumos` 相關段落)沒有找到能被利用的洞。攻擊路徑我逐條推演過,下面的檔案行號都是我在 repo 根實際讀到的。表態記錄裡「沒有外呼、沒有不可逆操作」的說法,我只就這輪新增的路徑核對過,沒有反證。

**① 提示注入:已看,無。**
這輪新增的字串來源只有三類:Groovy 腳本裡的常數、快取檔名(雜湊值)、測試名稱。測試名稱進輸出前走 `_kill_esc`,沒有新增任何把筆記、分支名或帳本欄位帶進派工詞或 hook 附加段的路徑。`gov` 帳本多帶的 `cov_judged` 欄位只是把帳本現有的值讀出來統計,不會變成給 AI 的指令。

**② 讀寫與執行越界:已看,無。**
- **快取寫入。** `store` 改走 `_write_bytes_atomic`(`scripts/lumos:32277`)。目標檔名由 `_cache_path`(`scripts/lumos:29103`)用 `_choice_sha(...)` 算出,是 24 碼的雜湊值加 `.exec`,檔名裡沒有外來字串。暫存檔用 `O_EXCL` 建立,最後 `os.replace`。就算有人事先在目標位置放了符號連結,`os.replace` 換掉的是連結本身,不會跟到 repo 外去寫。
- **資料夾來源。** 快取資料夾由 `_choice_cov_dir`(`scripts/lumos:79819`)取得。它要求 `at_sha` 通過 `[0-9a-fA-F]{7,64}` 的完整比對,並走 `_note_audit_safe_dir`,符號連結一律拒用。
- **清檔。** `_choice_cov_prune` 先過 `_repo_path_unsafe`,再用名稱比對(`x.name != cur`)排除這次的 `at_sha`,只列 `choice-cov/` 底下的直接子資料夾、並排除符號連結。`shutil.rmtree` 對符號連結的頂層會拒絕,內部的連結也不會跟過去。刪除範圍不會超出自己的快取子目錄。`at_sha` 在這支函式裡只拿來字串比對,不參與路徑組合。比對與刪除之間的競態屬於併發類,範圍外。
- **測試執行外部程式。** 新測試用 `java -cp <jar> groovy.ui.GroovyMain <tmp 檔>`。
  - `java` 來自 `which`。
  - jar 來自 `GRADLE_USER_HOME` 或 `pwd` 取得的真家目錄底下的 `wrapper/dists/gradle-*/.../groovy-[0-9]*.jar`。
  - 執行的腳本是測試自己寫進 `mkdtemp` 目錄的 Groovy,內容由程式裡的常數拼成,沒有外來輸入。
  - `subprocess.run` 用的是 list 形式,沒有 shell 插值。
  - 唯一可被外部影響的是 `GRADLE_USER_HOME`。那是使用者自己設的環境變數,而且只在測試時用。要借它放惡意 jar,需要使用者本人刻意設定,屬範圍外。
- **Groovy 腳本。** 這輪只改了 `dependsOn` 的比對寫法(先 `toString` 再比對),沒有新增檔案讀寫或外呼。
- **密鑰與信箱。** diff 內沒有新寫入的密鑰或信箱。

**③ 非刻意、一步就能繞過的守衛:已看,無。**
- 覆蓋資料被判成 Robolectric 專案類別紀錄數為 0 時,現在存到 scratch、不進快取。這是變嚴,不會讓壞資料被帶回下一次。
- `_choice_cov_parse` 要求 `nolines` 與 `noclasses` 欄位齊全且型別正確,缺了就判分析失敗。這是從「缺就當沒經過」改成「缺就失敗」,也是變嚴。
- `after` 固定回 6 項,被截斷的那支不寫進基準,不會有「被截斷卻被記成綠」的繞過。
- `_choice_cov_prune` 的保留數改成 `subs[_CHOICE_COV_KEEP - 1:]`,代表這次的 `at_sha` 一定保留,不會被自己清掉。

總結:最高等級是 clean
