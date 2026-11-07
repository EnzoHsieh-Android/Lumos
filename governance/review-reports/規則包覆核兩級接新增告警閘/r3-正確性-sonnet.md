severity: major

我做完了逐節審查。現況假設逐項用 `git -C … show Lumos/main:` 與 grep 查過(主線提交 `4785338d1`)。本機沒有 ast-grep,所以做 3 的 SARIF 實跑沒驗,只驗了靜態部分。審查時沒有改 repo,也沒有跑任何測試。

## F1 S3 條款「大小寫變體應照舊執行」跟既有測試和 Linux CI 矛盾
severity: major
blocking: 是——照字面實作會讓新測試在 Linux CI 或舊測試紅,屬於做出錯行為。
- spec 段落:驗收條款 S3、預期值表 S3 三列、做 5。
- 問題:
  - **目錄大小寫變體**:`$HOME/Harness/...` 這種寫法,既有行為是不通過。`_lint_wt_allow` 在「真實路徑不在工具鏈底下」那支會走大小寫救濟分支,回「大小寫跟工具鏈實際目錄不同」。`t_lint_new_worktree_allowlist` 還有一條「S3 宣告路徑大小寫跟工具鏈實際目錄不同 → 不通過」。S3 說大小寫變體「照舊執行」,跟這條互相打架。
  - **檔名大小寫變體**:`SGCONFIG.YML` 只有在不分大小寫的檔案系統(macOS)上才跟 `sgconfig.yml` 是同一支檔。在 Linux CI 上它是不存在的檔,`os.path.samefile` 會丟 OSError,只能走「不是同一支」而被拒。同一條測試在 macOS 與 Linux 會得到相反結果。
  - spec 沒說 OSError 怎麼處理,也沒說測試要不要依平台分支。
- 佐證:
  - file: `scripts/lumos:41184` 起的 `_lint_wt_allow`,末段 `if not inside:` 的 `samefile` 祖先迴圈與原因句。
  - file: `scripts/test_lumos.py:132186-132190`,既有的大小寫不通過斷言。
- 建議:S3 改成「同一支檔(`os.path.samefile`)才通過,samefile 丟 OSError 一律拒絕」。大小寫那條只在 `(home / "Harness").exists()` 時斷言,延用既有寫法。

引句:「指向 `sgconfig.yml`(含 `$HOME/` 寫法與大小寫變體) 應照舊執行」

## F2 做 5 沒說比對的是哪個根底下的 `sgconfig.yml`
severity: minor
blocking: 否——實作時第一次跑測試就會紅,修法單純。
- spec 段落:範圍做 5。
- 問題:`_lint_wt_allow(cmd, root=None)` 的 `root` 參數被既有測試傳入假工具鏈根。這些測試的假根底下有 `configs/ast-grep/kotlin-android/sgconfig.yml`,見 `scripts/test_lumos.py:132137-132140`。spec 只寫「工具鏈 `configs/ast-grep/kotlin-android/sgconfig.yml`」。若實作者用 `_kt_toolchain_root()`,而不是函式內已算好的 `root`,`t_lint_new_worktree_allowlist` 的 4 條通過案例(範本命令、`${HOME}`+CSV、`-c`+`--filter`)會全紅。
- 其餘既有測試不受影響:
  - 其餘用 `_lint_wt_allow` 的測試(`t_lwt_r1_shellfree_argv`、`t_lwt_*` 系列)都用 `_lwt_pack_cfg()`,也就是真的 `sgconfig.yml`。
  - `evil/sgconfig.yml`(符號連結指到外面)與 `../` 案例原本就在前一關被擋。
- 主線上沒有別的合法用途會被誤殺:`configs/ast-grep/` 底下只有 `kotlin-android` 一個包,沒有別的棧或假規則包。
- 建議:寫明「比對對象由函式內的 `root` 算出,不用全域工具鏈根」。

引句:「真實路徑要跟 `configs/ast-grep/kotlin-android/sgconfig.yml` 是同一支檔」

## F3 做 3 的「跑不起來」會被 `t_kotlin_rulepack_samples` 的濾詞濾掉
severity: minor
blocking: 否——只影響換版本偵測的完整度,不會做出錯行為。
- spec 段落:範圍做 3、驗收條款 S2。
- 問題:
  - spec 規定「讀不懂輸出照『跑不起來』報」,但同時規定那個測試只留含「壞例、好例、樣本、載入、祖先」的問題。
  - 既有的「掃 samples/bad 跑不起來」訊息本來就不含這五詞。所以新的 SARIF 掃描若因 ast-grep 換版而輸出讀不懂,測試會把這筆濾掉而不紅。
  - 只有「沒有目標規則的結果」那條(含「樣本」)會紅。這跟做 3 自述的「讓工具鏈換版本時有東西會紅」只對一半。
- 佐證:file: `scripts/test_lumos.py:126367`,`sample_probs` 的篩選詞。
- 建議:SARIF 讀不懂的原因句也帶「樣本」二字,例如「SARIF 掃壞例樣本跑不起來」。
- 做 3 指定的兩條規則(查證結果):
  - `kt-livedata-setvalue-background` 在 `rules-review/state.yml`,嚴重度 info,訊息開頭 `[STATE-16]`。
  - `kt-value-assign-background` 在 `rules-hints/state.yml`,嚴重度 hint,訊息開頭 `[STATE-16]`。
  - 兩條各有 `samples/bad/<id>/src/main/kotlin/<id>.kt` 與好例樣本。value-assign 的壞例有 2 個 `// case:`,滿足既有「壞例至少命中 2 處」。
  - 兩條都不是出處不全的 8 條,不會被搬走。

引句:「掃描共用既有的逾時旗標」

## F4 做 2 的細節:嚴重度、好例排除、讀表函式都對得上,但有兩個要寫明的點
severity: minor
blocking: 否——都是實作時會自己撞到的小處。
- spec 段落:範圍做 1、做 2。
- 逐項結果:
  - **`_DIR_SEVERITY`**:`message_problems` 目前用 `_DIR_SEVERITY.get(dir, ())`,不認得的目錄一律報錯。`rules-unwired` 必須加成「全部嚴重度」,也就是 `SEVERITIES` 全集。「不限」不能做成跳過檢查,否則前一道「severity 只能是 error/warning/info/hint」會被連帶繞過。
  - **`r.get("dir")`**:`catalog_problems` 目前沒讀 `dir`,spec 的改法可行。S1 預期值表第 4 列(假規則沒有 dir 鍵)在這個設計下成立。
  - **好例排除**:`review_ids` 擴到 `rules-unwired`,是對的。
  - **`good_cases`**:`good_cases` 本身只看檔名前綴,不受影響。
  - **第四組載入條數**:`want` 對 `rules-unwired` 也要算,所以搬走 8 條後 hints 的載入條數會從 50 變 42,`sgconfig-hints.yml` 不用改。
  - **檔數對得上**:
    - 8 列各掛一條,逐列在 `rules-hints/` 各 1 條,共 7 支檔,每支同檔剩 4 到 6 條,都和 spec 說的一致。
    - 型錄 8 列中 `STATE-9` 的「現成規則」格寫了兩個名字,其中 `kt-statein-lazily-or-no-timeout` 在主線規則目錄裡不存在,只有 `kt-whilesubscribed-no-timeout`。這是型錄的舊名漂移,數量照樣是 8。順手修掉最好。
- 真實規則包搬完後預期 0 個問題:成立。前提是做 6 同時把 8 列的型錄格改成「不接」,出處不全判定的 `weak_ids` 只看名稱欄,不看格子文字。

引句:「這 8 列各掛一條,分散在 `rules-hints/` 的 7 支檔裡」

## F5 做 6 的「批一」前綴跟型錄自己對「批一」的定義衝突
severity: minor
blocking: 否——型錄自檢不認這個前綴,只是文字語意自相矛盾。
- spec 段落:範圍做 6。
- 問題:
  - 型錄第 11 行定義「批一=會擋的規則已上線」。
  - spec 要求 8 列出處不全的格子改成「不接(rules-unwired)」,又要求新文字保留「告警帶寫法=批一」前綴。這樣一格同時說「批一(會擋)」與「不接」。
  - 覆核級的 7+3 格也是:規則不在預設 `sgconfig.yml`、要消費專案自己宣告才擋,掛「批一」也不準。
- 自檢怎麼看(查證結果):
  - `check.py` 對通電批次格只判「批四」。形狀類另檢接電方式欄(第 9 欄)含「告警帶寫法」。沒有程式檢查「批一」前綴。
  - 唯一用到「告警帶寫法=批一」的是 `scripts/test_lumos.py:126658` 的改壞六,它只要求「有一列是批一而且沒有行為測試段」。型錄裡還有大量真正的批一列,所以前綴留不留都不影響測試。
  - 括號內不放分號的顧慮屬實:`behavior_value` 只看「行為測試或正向約束=」到分號那一段,TEST-5 的格子是 `告警帶寫法=批一;行為測試或正向約束=範本 T0` 這種形狀。
  - 統計數字也對:現有「接上前不擋」7 格(API-17、STATE-1、STATE-7、STATE-16、CO-44、DATA-10、DATA-36)、「批一」卻有覆核級規則 3 格(API-11、STATE-4、TEST-5)、「只有提示級規則,預設不接」共 40 格(8 列出處不全,32 格不動),都跟 spec 一致。
- 建議:前綴只留給真的在 `sgconfig.yml` 擋的列;覆核級改用「批一(覆核級:…)」之外的獨立值,並在第 11 行定義。

引句:「其餘提示級的 32 格不動(提示級照舊不接)」

## 固定席:對圖譜節點的逐條判
- `Systems/kotlin規則包`(計劃連結):不影響。計劃只是改 WHY 的字面、補第四個目錄與 `[test:]` 掛鉤,不動既有欄位齊全的 RULE 的原意。計劃自己也寫了提示級照舊不接。唯一要注意的是「誤報超過一成」RULE 要重新 `[confirmed:]`,spec 已寫。
- `Systems/linter精選目錄`(計劃連結):不影響。範本從一條變兩條、釘版本,屬文字改動。我沒有打開節點全文逐行對,這條只依計劃描述判。

## 風險類逐類答
- **既有 `_lint_wt_allow` 其他合法用途會被誤殺?** 主線上沒有。見 F2:`configs/ast-grep/` 只有一個包,既有測試都用真或假的 `kotlin-android/sgconfig.yml`。前提是 F2 的 `root` 問題處理好。
- **既有測試哪些會紅?**
  - 做 5 本身:只有 F1(大小寫條款)與 F2(根的取法)兩處會紅。
  - 做 1、2:`t_kotlin_rulepack_messages_cite_catalog` 的改壞「非 hint 規則引用出處不全」仍成立(假規則沒有 `dir` 鍵,依 spec 缺鍵算「不在 unwired」,會報)。
  - `t_kotlin_rulepack_samples` 的「規則目錄全空」迴圈要加第四目錄,spec 已列。
- **`_DIR_SEVERITY`、`good_cases`、好例排除:** 見 F4。
- **做 3 兩條規則:** 存在、所在目錄與樣本都對,見 F3。
- **做 6 的前綴與自檢:** 見 F5。

總結:最高等級為 major,blocking 共 1 條
