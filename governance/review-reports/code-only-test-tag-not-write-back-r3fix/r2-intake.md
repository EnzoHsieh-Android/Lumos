# code-only-test-tag-not-write-back-r3fix r2 收貨紀錄

八席齊了才動工作目錄。report-normalize:資安席檔首寫 clean、內文有一條 minor,退回該席自己把檔首改成 minor,其餘七份合格。quote-check 六份全錨;判定路徑2 #1 引的是 `scripts/lumos` 的註解(`grep -cF` 得 1,HIT);合約2 #1 #2 #4 引的是計劃筆記,那篇不在 r2-snapshot.patch,而且收貨後才改過——拿席位讀的版本重現:`git show febaa2d3:docs/lumos-toolchain-knowledge/Projects/只換測試綁定不算寫說明_計劃.md | grep -cF` 三句各 1,HIT。
判定路徑2、規格符合2 clean(判定路徑席實跑 20 多種變形,拿掉的文字跟核對的名稱出自同一份值)。輪內沒有 major 以上 → minor 可附理由放行。

| id | 席 | 嚴重 | 重現/判讀 | 結論 |
|---|---|---|---|---|
| g1 | 通才2 | minor | 席實跑:同一段推送改 `.lumos/config.json` 新增句子名的平台,`[test:那句話:test_alive]` 兩道 rc0 | HIT 採信,折:天花板 11 |
| k1 | 合約2 1 | minor | 計劃「只認測試刪了」比程式核對的強 | HIT 採信,折:改寫成「用意是…程式只核對上一版綁過」 |
| k2 | 合約2 2 | minor | 實作紀錄的測試條數與「五條驗收測試」是舊的 | HIT 採信,折:標明是當時、以後各輪為準 |
| k3 | 合約2 3 | minor | [[Projects/每支檔有家_計劃]] [S12] 補句沒寫名稱形狀與 test-gone 條件 | HIT 採信,折 |
| k4 | 合約2 4 | minor | 效能那句比程式保守(還要有新出現的單一識別字名稱才建索引) | HIT 採信,折 |
| c1 | 正確性2 1 | minor | 標記緊貼 emoji、底線、組合字元時,原句本來有空白會被判寫了說明 | HIT 採信,放行:多擋方向,只差一格空白,走拆提交的既有出口 |
| c2 | 正確性2 2 | minor | 上一版 `python:test_x`、新版 `test-gone:test_x` 不算只換綁定 | HIT 採信,放行:刻意取捨(前綴不核對就能夾帶說明,見 r1 g1),多擋方向 |
| e1 | 邊界2 | minor | 標記後緊接符號(底線、反引號、連字號)會吞前面一格空白,`a_b` 改 `a [test:t]_b` 判只換綁定 | HIT 採信,放行:只差一格空白、藏不進字;收緊會誤擋「a [k:v]。」這類常見寫法 |
| a1 | 架構對齊2 | minor | `isalnum()` 對照既有 `[^\W_]`/`\w` 寫法 | HIT 採信,放行:`[^\W_]` 跟 `isalnum()` 判法相同(底線都不算字),只差寫法;下次動到這段再改成正則 |
| s1 | 資安 | minor | 上一版已有的句子型 `[test:一句話]` 改標成 `[test-gone:同一句]` 會過(推論) | HIT 採信,放行:那段文字上一版就在,沒有新增說明 |
