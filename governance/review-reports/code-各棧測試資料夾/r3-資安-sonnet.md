severity: minor

已逐類檢視:1(注入類)/2(登入權限)/3(密鑰與個資)/4(加密與傳輸)/6(行動端執行期)已看,無新發現;新增依賴:無(純 stdlib)。5(執行邊界)為本輪主要發現,對應派工詞特別點名的「靠資料夾命名讓程式檔逃過要有家的要求」——這輪修正把 R1/R2 揪出的「零內容驗證」補成「要有同副檔名的旁證檔」,方向正確,但旁證檔的搜尋沒有限深、也沒有限定是不是真的屬於同一個測試目標,殘留可被利用的縫,見 F1、F2。

### F1 頂層測試資料夾的「旁邊有同副檔名檔」驗證不限深度,子樹裡任一支既存/同批新增的檔就能永久免家整個同名 Tests 資料夾
severity: minor
blocking: 否 — 只影響知識圖譜文件化/治理留痕義務(`_nodehome_is_test` 的棧測試資料夾判定只在 `_nodehome_required`[S1] 消費,不影響 pitfalls/contracts/程式執行),不觸發任意碼執行、外洩或繞過登入,屬縱深防禦類治理控制放寬
攻擊路徑:誰——有提交權限的內部人或被合併的惡意 PR;從哪裡——任一頂層資料夾 `tools/` 的整個子樹(`_nodehome_layout` 用 `side.all_paths` 掃全 repo、不分深淺);送什麼——同一個 commit 裡先放一支已登記家、無關痛癢的 `tools/anywhere/deep/util.cs`,同批再塞入任意數量的 `toolsTests/backdoor1.cs`…`toolsTests/backdoorN.cs`;拿到什麼——`top_exts["tools"]` 只要曾出現過 `.cs` 就永久成立,`toolsTests/` 底下不論放幾支 `.cs`、內容是否真對應 `tools/` 的程式目標,全部被判為測試檔,跳過「每支檔有家」提交前/推送前強制擋,且日後也不需要為 1:1 對應關係再舉證一次。
引句:「if len(parts) > 1 and parts[0] in tops:」
佐證 file: `scripts/lumos:17818`(收集旁證副檔名時不看深度);`scripts/lumos:17848`(消費端只問副檔名有沒有在集合裡,不問旁證檔跟被免家的檔是否同一個測試目標)

### F2 Gradle androidTest 分支同款問題:src/main 底下混進的非該棧語言檔,能讓 androidTest 放行任意語言的檔免家
severity: minor
blocking: 否 — 同 F1,限縮在 S1 每支檔有家的文件化義務範圍,不觸及執行/外洩/權限邊界
攻擊路徑:誰——同 F1;從哪裡——任一 Gradle 模組 `feature/x/src/main/` 子樹;送什麼——`src/main` 底下若曾混進一支非 Kotlin/Java 的檔(例如建置用 `src/main/scripts/gen.py`,現實 monorepo 常見),攻擊者再於同模組 `src/androidTest/` 底下放進任意數量的 `.py`/`.go`…等非 JVM 檔;拿到什麼——`main_exts` 只累計「該模組 src/main 出現過的任何副檔名」、不限制是不是 androidTest 這條規則原本鎖定的 Kotlin/Java,這些非 JVM 檔一樣被判為測試檔、跳過每支檔有家(r3 新增測試 ④f 只驗了 src/main 純淨、沒有混語言檔的情境,沒蓋到這個組合)。
引句:「if parts[k] == "src" and parts[k + 1] == "main":」
佐證 file: `scripts/lumos:17822`(累計副檔名不分語言);`scripts/lumos:17851`(消費端同樣不限定副檔名要屬於該測試地圖規則指定的棧)

總結:最高 severity minor,blocking 共 0 條
