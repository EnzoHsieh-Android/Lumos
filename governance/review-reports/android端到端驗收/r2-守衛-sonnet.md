severity: major

## F1 「主線分岔點」與「既有推送範圍的算法」對不上,正常增量推送會漏要求
severity: major
blocking: 是 因為有一條不繞過檢查的路,沒驗收的 App 程式會被推上去而且沒有紀錄。

〈資料怎麼流〉第 4 步與〈不做〉互相矛盾。

引句:「主線分岔點用既有推送範圍的算法;算不出來(沒有主線、淺層 clone)時這道走 fail-open 並記一筆治理帳」

問題:spec 要比的是「主線分岔點」和「被推送提交」兩端的指紋,卻說這個分岔點用既有推送範圍的算法算。既有算法對一般增量推送不回主線分岔點,回的是遠端舊頂端。
- 情境一:分支先前推過帶未驗收 App 程式的提交 X。這可能發生在 `e2e` 段合進主線之前、用 tag 或其他非 heads 的 ref 推的、或用 `--no-verify`。後來該分支只多一個文件提交,再做增量推送。起點是舊頂端,兩端指紋相同,判成「不要求」,X 沒有紀錄也沒有擋。
- 情境二(⚠,spec 沒定義):直接推 `main`。既有算法會跳過「就是這次被推的那條」的主線候選,候選為空。「主線版有 `e2e` 段」要去讀哪個 ref 的設定,spec 沒寫。照〈資料怎麼流〉第 4 步「算不出主線就 fail-open」的字面實作,單人最常見的「直接推 main」整段繞過,只留一筆帳。
- 情境三:〈資料怎麼流〉第 4 步最後說:

引句:「CI:推到主線時分岔點就是頂端,這道不要求;第一版不另外接 CI(見 REVISIT)。」

  ci.yml 呼叫的是 `code-loop check --diff "$BEFORE..$SHA"`。若 `$BEFORE` 就是起點,CI 在 main 上會要求紀錄,跟「CI 不要求」相反。
- 修法:spec 要明寫分岔點與主線版設定各自從哪個 ref 取,不能指給既有算法。

佐證:
- file: `scripts/lumos:58701` 增量推送的起點是遠端舊值。
- file: `scripts/lumos:58661` 候選會跳過就是被推的那條。
- file: `scripts/lumos:58716` 頂端已在主線上時回 None。
- file: `scripts/hooks/pre-push:577` 傳給 check 的是 `--diff "$_brange"`。
- file: `.github/workflows/ci.yml:221` CI 傳的是 `--diff "$BEFORE..$SHA"`。

## F2 judge 與 gate 用哪一份設定算指紋沒定義,動到 `e2e` 段的提交永遠過不了
severity: major
blocking: 是 因為這是正常開發(新功能附新 flow、重構目錄)被誤擋,只能放行或略過檢查。

引句:「同一個提交裡刪掉或改弱這一段,要等合進主線才生效」

引句:「這一段設定本身,都算進指紋(見〈查證紀錄〉)」

問題:
- gate 用主線版設定算要涵蓋哪些檔,所以「重算值」是主線設定下的指紋(S9)。
- judge 的設定來源 spec 沒寫。judge 在被推送的分支工作目錄跑,實際讀到的是分支自己的 `e2e` 段。
- 指紋公式只用 `git ls-tree` 的物件編號。「這一段設定本身」是 `macrobench.json` 裡的一段,物件編號算不出來。要嘛整個檔算進去,要嘛設定根本沒進指紋。spec 沒選。

情境(兩個後果):
- 同一個提交加了新 Maestro flow(`.maestro/new.yaml`),並在 `flows` 加進它。judge 在分支設定下跑了新 flow 並算出 F_branch,紀錄存成 `<F_branch>.json`。gate 用主線設定重算得 F_main,而主線的檔案集合不含新 flow,於是 F_main 與 F_branch 不同,找不到紀錄,擋。要先把設定單獨合進主線,新功能與它的 flow 才能一起驗。
- 想關掉這道判定,正確的關法是刪 `e2e` 段。但那個提交本身也被判定:指紋有變、要求紀錄。judge 沒有 `e2e` 段就跑不了,只剩放行。「回退」那節的關閉路徑循環依賴這道閘。

佐證:
- file: `scripts/lumos:15996` 是 `_KNOWN_GATES`;spec 沒寫 judge 讀哪份設定,整份 spec 找不到對應文字,屬 spec 內部缺口。

## F3 只改設定旗標就能讓紀錄「過」,而 gate 不核對紀錄涵蓋的塊
severity: major
blocking: 是 因為 S9 與〈實驗室驗收〉宣稱「改弱 `e2e` 段要擋」,但設計不會擋。

引句:「最近一次結果是 pass、或有任何一筆放行 → 過」

問題:gate 只看紀錄的 `result` 與有沒有放行。紀錄裡的塊明細沒對照主線設定要求哪幾塊。judge 用的是分支設定。
情境:同一個提交把 `stability: true` 改 `false`(或縮小 `stability_checks`,或把 `macrobench` 關掉),只跑 UI 流程,`result` 是 pass。這種旗標改動不改變任何檔案的物件集合,所以主線設定算出的指紋與紀錄一致,gate 放行。〈實驗室驗收〉只列「同一個提交裡刪掉 e2e 段」,刪段 judge 跑不了,沒有覆蓋「改弱」。
修法:紀錄記實際跑了哪幾塊、各用什麼設定,gate 對照主線設定要求的塊。

佐證:
- file: `.github/workflows/ci.yml:221` CI 只重跑同一道 check,沒有額外核對。

## F4 「乾淨的工作目錄」只檢查 `app_dirs` 與驗收素材,APK 卻吃整個工作目錄
severity: major
blocking: 是 因為驗收的 APK 與被推送的提交可以不同,又不留任何紀錄。

引句:「範本腳本在乾淨的工作目錄上照它建」

引句:「驗收素材在工作目錄沒有未提交的改動(有就停,因為紀錄要綁提交)」

問題:開跑前只擋 `app_dirs` 與驗收素材的未提交改動。`build` 指令看的是整個工作目錄,包括根目錄 `build.gradle.kts`、`gradle.properties`、`buildSrc`、模組外的 gradle 檔。
情境:開發者為了讓驗收通過,暫時改了 `gradle.properties`(例如關掉 minify),沒有提交。範本腳本照過、judge 寫 pass、指紋只綁已提交的 `app_dirs`。推上去的是沒改過的設定,驗收測的是另一個 APK。紀錄裡記了 APK 的 sha256,但 gate 沒有拿它跟任何東西比。
- 〈實務隱患〉只承認「`app_dirs` 漏列」,沒提這條。

佐證:
- file: `scripts/lumos:20941` 既有的 `_dirty_non_bookkeeping` 檢查整個工作目錄(除簿記檔),可以直接沿用,不必自訂更窄的範圍。

## F5 `.e2e-lock` 只防同一個工作目錄,殘鎖沒有清除規則
severity: minor
blocking: 否 因為擋的是開跑前的人工步驟,有手動出口,不是漏擋。

引句:「開跑前檢查沒過(工作目錄有未提交改動、裝置沒連上或鎖屏、另一次驗收在跑)時不開跑並說原因」

問題:
- `.lumos/artifacts/android/.e2e-lock` 在專案工作目錄內,鎖的範圍是工作目錄,不是裝置。全域規則要求每個任務開獨立 worktree,兩個 worktree 可以同時對同一台 SM-X710 跑,互相干擾。toolkit 的 `.maestro/.lock-<裝置>` 也在各自 worktree 內,同樣擋不住。
- 範本腳本只處理 INT/TERM。終端機被關(SIGHUP)或 SIGKILL 後,`.e2e-lock` 會留下。spec 只寫了清 `.maestro/.lock-<序號>` 的規則,沒寫 `.e2e-lock` 的過期判斷。下一次開跑被「另一次驗收在跑」擋住,只能手刪。

## F6 〈回退〉引用不存在的設定檔
severity: minor
blocking: 否 因為不影響判定本身,只讓文件裡的關閉辦法失效。

引句:「專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑」

〈回退〉第一條寫刪掉那個檔就不跑這道判定。整份 spec 的設定都在 `.lumos/macrobench.json` 的 `e2e` 段,沒有 `.lumos/android-e2e.json`。照回退節操作,刪的是不存在的檔,判定照擋。要改成「合進主線的刪 `e2e` 段」,並處理 F2 說的循環依賴。

## 已讀無 finding 的部分
- 〈一次驗收跑什麼〉的 toolkit 介面:`visual-check.sh` 的回傳碼 0、1、2 與 `THRESHOLD` 底線 99.5 跟 spec 一致。diff 圖與鎖已被 toolkit 的 `install.sh` 寫進 `.gitignore`,所以不會讓工作目錄變髒。
- `maestro test --udid`、`--format`、`--output` 在 Maestro 2.10.0 上存在。
- 〈實務隱患〉的金流、對外送出、不可逆:已讀,無 finding,理由 spec 已列(只讀驗收輸出、不送外部、放行只增不刪)。
- 已列在〈不做〉與 REVISIT 的範圍(tag 推送、CI、AI 冒充人答終端確認、略過推送前檢查)沒有重報。

最嚴重 severity: major;blocking 共 4 條(F1、F2、F3、F4)。
