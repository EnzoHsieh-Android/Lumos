severity: major

先交代核對過、沒問題的部分:
- `manifest.json` 18 筆 sha256 我自己重算,全部對得上。目錄內沒有多出來的檔,也沒有缺的檔。
- 設計稿的快照與計劃檔逐位元相同,配套指紋表也等於 `scripts/test_quality.py` 現在的雜湊。
- S5 點名的七支測試、兩支守衛測試都存在,交叉引用的節點都存在。
- 計劃、驗證紀錄、標準、收證工具的家,對 Truth 兩型別、裝置兩型別、零選中誰擋、Semgrep 條件、原編號撤回原因的說法互相一致,也跟 `scripts/test_quality.py` 與 `scripts/test_quality_scan.py` 的行為相符。

**逐條 finding**

1. 回退步驟會銷毀唯一的完整卷證,而且跟「已排除:不可逆」矛盾
severity: major
   - blocking: 是,三個月後的人照回退步驟做,會不可逆地毀掉公開摘要明講「不能單獨重跑」的唯一重跑來源。
   - 計劃說完整卷證只在考場本機演練分支、不推。回退又寫「刪掉演練工作樹與分支即可」。
   - 我在考場工作樹查過:撤回的設計審證據目錄 `drill-evidence/design-review-r1-withdrawn/` 是未追蹤檔(git status 顯示 `??`)。連「只刪分支」都留不住它。
   - 計劃全文沒有「回退前先另存或打包卷證」的步驟,也沒有備份位置。
   - 實務隱患節卻把不可逆寫成已排除。
   - 引句:「mOrangePos:刪掉演練工作樹與分支即可,主目錄與 develop 沒有任何提交。」
   - 引句:「已排除:不可逆:演練分支不推不併;平板只裝演練變體的套件,可解除安裝。」

2. 「金流」「對外送出」的排除理由只講測試碼,沒講 App 啟動路徑 ⚠
severity: major
   - blocking: 是,這兩個「已排除」是裝到真平板跑之前的安全前提,理由卻沒涵蓋實際會執行的程式。
   - 儀器測試會在平板上啟動考場 App 的 Application 子類別。
   - file: `<考場演練工作樹>/<Application 子類別檔>:71` 附近會初始化付款 SDK(沙盒環境)。
   - file: `<考場演練工作樹>/<Application 子類別檔>:80-89` 附近會在背景掃待補送的當機檔,並 POST 到後端網址。
   - 這些都不受「測試用假資料來源」影響。
   - 失敗情境:某次演練中程序當機留下當機檔,下一次儀器測試啟動時就會對開發後端送出請求。
   - 我沒法確認演練期間真有網路活動,所以標 ⚠。至少排除理由要改成實際依據,或在驗證紀錄補一筆「啟動路徑的外送行為已查/未查」。
   - 引句:「已排除:金流:被測的是現金收支類別的管理,不碰付款與刷卡;測試全用假資料來源,不連後端。」
   - 引句:「已排除:對外送出:測試不連網、不連 POS 主機,只在平板本機執行。」

3. S4 的「演練後套件清單」沒有原始證據
severity: major
   - blocking: 是,S4 是驗收條款,要比對的兩份之一不存在。
   - 考場完整卷證的 `device/` 只有演練前清單 `packages-before.txt`(488 行)。整個 `drill-evidence`(排除撤回目錄)找不到演練後清單。
   - 「after 488、identical true」只出現在公開的 `controls.json` 第 77 到 81 行附近,是推導結果,不是原始證據。
   - 接手的人無法重驗 S4 的「平板只裝演練變體套件、前後一致」。
   - 補充:S4 說「演練指令沒有寫進主目錄」能證明,但沒有任何留存的物件支撐。我看了主目錄 32 個未提交檔的修改時間,全是 9 月,可以拿來當證據,但文件沒引用。
   - 引句:「manual:比對平板演練前後的套件清單、develop 的提交編號」

4. 公開檔仍有考場真實識別字(方法名與屬性名那一類) ⚠
severity: major
   - blocking: 是,這類問題正是撤回原編號的原因,公開 README 還宣稱已換代稱。
   - 公開卷證 `README.md` 第 3 行說類別名、套件名、欄位名都換成代稱。
   - 但 ViewModel 的公開方法與屬性名沒換:載入、新增、作廢三個方法,三條一次性通知流,loading 狀態與清單狀態屬性。
   - 共用的結果包裝型別名也沒換,連同它所在的子套件路徑(`model` 底下的 `api` 子路徑)。
   - 出現位置:
     - `requirements.md` 第 8、12-13、19-25、32-34、40-44、51 行
     - `bad-tests.kt.txt` 第 4、41、43、74、80、84、101、109、112 行
     - `fault-checks/` 的 M6 檔、`bad-test-checks/` 的 b9 檔與 `summary.json` 內的測試 id
     - `device/instrumented-summary.json`
   - 判斷依據:我拿考場該 ViewModel 的 develop 原始碼逐一核對,這些名稱都是原樣。
   - 仍判 ⚠,因為 Enzo 的裁定只列「類別名、套件名、欄位名」,方法與屬性名算不算在內需要他裁。
   - 引句:「公開的工具鏈只放去識別化摘要(類別名、套件名、欄位名換代稱」

5. 台帳暫存區還留著撤回輪次的行,直接提交會公開,跟「公開 repo 不留」矛盾
severity: major
   - blocking: 是,不加 `-a` 的 `git commit` 就會把本該移走的帳公開。
   - `git status` 顯示 `docs/.canary-log.jsonl` 是 `MM`。
   - 暫存版(index)仍含撤回輪次 r1 的四行 CANARY(正確性、邊界、架構對齊、整合席)。只有工作樹版把它們刪了。
   - `docs/.governance-log.jsonl` 暫存版另有一行 design-loop 的 converged(disposal gate PASS),節點寫的是撤回的舊編號。
   - 兩個後果:
     - 四行帳會被公開,指向已不在 repo 的卷證檔(`report_path`、`snapshot_path`)。
     - 舊編號的「通過」留在公開帳,新編號 `-std` 這輪卻還沒有對應行。
   - 驗證紀錄又說「帳只能追加」,而這裡實際是刪除。兩處說法自己衝突。
   - 引句:「原編號的證據、凍結判定與四行審查帳移到考場本機卷證」

6. 公開摘要與完整卷證之間的追溯鏈不完整
severity: minor
   - blocking: 否,不影響結論,但三個月後的人要多繞路。
   - 驗證紀錄的 `valid_under` 與第 22 行寫提交 8a774ca,又說既有本機測試全綠的數字見完整卷證 `logs/`。
   - 但 `logs/full-unit-suite-summary.json` 與 `logs/full-unit-suite.log` 是 ed44d42 才加的。照驗證紀錄 checkout 8a774ca 的人看不到。只有公開 `README.md` 寫了 ed44d42。
   - 考場完整卷證的 `README.md` 第 18 行說 `logs/` 放零選中與編譯錯。實際上 `logs/` 只有預設零選中、依賴解析、返回預設值那幾個輸出。
   - 「關掉保護的零選中」與「編譯錯」的證據在 `receipts-bad/b5` 與 `receipts-bad/compile-error`。
   - 公開檔到完整卷證檔沒有對照表,也沒有原檔雜湊。
   - 公開 `device/instrumented-summary.json` 第 16 行的失敗文字是代稱後重寫的,不是原樣。去識別化有沒有失真無法稽核,而 README 仍稱「不可變證據」。

7. 重跑所需的工具鏈版本沒記
severity: minor
   - blocking: 否,計劃已說明收據換版會被拒,只是沒說該用哪一版。
   - 收據不記工具版本(`scripts/test_quality.py` 的 `load_receipt_data`),計劃第 75 行自己承認。
   - 完整卷證的重跑腳本指向「當時的工具鏈工作樹」。這批改動現在未提交,公開摘要與驗證紀錄都沒寫是哪一版工具產生的收據。
   - 三個月後重跑會遇到「記錄的結果跟原始報告不同」的拒收,看起來像偽造,而實際只是版本不對。
   - 建議在提交後的驗證紀錄補工具鏈提交編號與 `scripts/test_quality.py` 的雜湊。

8. S5 與做法第 7 步的判定句比程式寬鬆
severity: minor
   - blocking: 否,程式與測試是對的,只是驗收條款的字面讀法會放行。
   - file: `scripts/test_quality.py:133-134` 只在 Caused by 之前找 JUnit Assert 堆疊。
   - file: `scripts/test_test_quality_cli.py:290` 有反例:第一行是帶訊息的 `AssertionError`,Assert 堆疊只出現在 Caused by 之後,必須判不是斷言失敗。
   - 計劃第 74 行與 S5 只寫「要有 JUnit Assert 的堆疊」,沒寫「Caused by 之前」。按字面讀,這個反例應該被認定。
   - 標準、收證工具的家、驗證紀錄都寫了「Caused by 之前」,只有計劃沒有。
   - 引句:「第一行剛好是這兩個型別之一(可接冒號加訊息),而且要有 JUnit `Assert` 的堆疊」

9. 安全證據閘的 JUnit 宣告那條路,新行為沒有任何測試釘住
severity: minor
   - blocking: 否,放行面那條有守衛,這條只是「變成失敗:斷言失敗」的說法沒守衛。
   - 計劃、驗證紀錄、收證工具的家都寫了這條路的新判定。
   - S5 只綁了 `t_secev_fault_truth_assertion_counts_like_assertion`,它只測 fault_sensitivity 那條。
   - `scripts/test_lumos.py` 裡 `failure_truth` 與 Truth 型別只出現在那一支守衛。
   - file: `scripts/lumos:8846` 起的 `_secev_junit_declared` 這條路,把 Truth 型別拿掉或歸因改回去時,沒有測試會紅。
   - 引句:「同一個判定函式也被安全證據閘的兩條路用」

10. `Expect` 規則「會包住非斷言例外」的說法,演練裡沒有觀察到
severity: minor
⚠
    - blocking: 否,選擇的是保守的「不認」,錯了只會多拒收,不會多放行。
    - 考場完整卷證全部收據與報告 grep 不到 `SimpleAssertionError`。考場測試也沒用 `Expect`。
    - 唯一樣本是人造的:`scripts/test_test_quality_cli.py:244-246`。
    - 計劃把它放在「演練中發現」,標準也當事實寫,但依據應該是讀原始碼或文件,不是實跑。
    - 建議標準與計劃註明來源,或補一次實跑。
    - 引句:「Truth 的 `Expect` 規則丟的 `Truth$SimpleAssertionError` 也會包住不是斷言的例外,不加」

11. 承認的缺口沒附回頭條件,而且「兩條舊回頭條件」數錯
severity: minor
    - blocking: 否。
    - 專案鐵則 4 要求把「沒跑、沒重跑」搬成 `REVISIT:` 行。
    - 計劃與驗證紀錄全文沒有 `REVISIT`,而 Semgrep「沒跑」(第 77 行)、C# 與 iOS 原生 runner「沒重跑」(第 79 行)都是會過期的承認。
    - 計劃說碰到「兩條」`when-file:scripts/test_quality.py` 的舊回頭條件。實際有三條:
      - `Systems/test-quality-cli.md:36`
      - `Verification/測試品質工具接線_CSharpAndroidiOS原生消費驗證.md:33`
      - `Verification/測試品質工具接線_Node與Laravel原生消費驗證.md:35`
    - 第三條要求「擴充 reporter 或框架前先驗真實身份與 assertion 歸因」,計劃沒交代怎麼處置。這批改動推送時會被點名。
    - 引句:「改到 `test_quality.py` 會碰到兩條掛在它身上的舊回頭條件」

12. 零選中的控制組只有本機路,裝置路沒有 ⚠
severity: minor
    - blocking: 否。
    - `controls.json` 第 2 到 11 行附近的 `zero_selection` 與 `compile_error` 只對應本機 Gradle 單元測試。
    - 標準新增的建議是「裝置收證用類別篩選」,但演練沒示範類別名打錯時裝置路的行為(是失敗、空報告、還是整份拒收)。
    - 接手的人照標準用類別篩選時,碰到打錯字不知道由誰擋。我沒查證裝置路實際行為,所以標 ⚠。
    - 引句:「篩選選不到測試卻回報成功(Gradle 預設零選中會失敗,所以要先示範預設被擋」

13. 開發用尾碼與變體名的去識別化口徑前後不一
severity: minor
⚠
    - blocking: 否,是否算識別字要 Enzo 裁。
    - 計劃前掃 P7 把「演練變體的名稱與套件尾碼」當識別字,改成描述。
    - 但同一批公開檔仍有原樣的變體名與尾碼:
      - 驗證紀錄第 5 行與第 46 行
      - 公開 `device/instrumented-summary.json` 第 16 行與第 180 行
    - 另外 `governance/review-reports/code-收證認得Truth與裝置字串比較/r1-snapshot-A.patch` 第 61、88、95、103、241 行也有。
    - 要嘛全部抽象化,要嘛承認它不算識別字、回頭改 P7。現在是兩套標準。

**固定席節點(`Systems/test-quality-cli`)逐條判**
- 落點正確:`lands_in` 指向的節點已存在,有負責範圍,不需另開。
- 「管 3 支檔」不含 `scripts/test_lumos.py` 與標準文件:不影響,這兩者的家另有節點,且文件不算程式檔。
- 「0 條合約」:不影響這份設計稿。但安全證據閘的新放行面目前只靠一支測試,合約化是否合適可由 Enzo 另議,見 finding 9。

**實務隱患鏡頭逐類**
- 效能:無。三次實跑加上測試套件約一兩分鐘,計劃已寫,數字合理。
- 金流、對外送出:見 finding 2。
- 不可逆:見 finding 1、5。
- 資安(公開洩漏):見 finding 4、13。
- 併發:無。被測的是單人本機演練,卷證寫入沒有多寫者。
- 資料遷移:無。沒有動資料庫或 schema。考場 App 啟動有一次性的偏好設定遷移,但只落在新裝的演練變體上。
- 相容性:收據換版被拒已寫(計劃第 75 行),見 finding 7。

**各節狀況**
- 前言、問題與最小解、名詞:已讀,無 finding。
- 做法第 1-5 步:已讀,第 5 步見 finding 12。
- 做法第 6-7 步:見 finding 8、10、11,以及公開洩漏相關的 4、5。
- S1、S2、S3、S6:已讀,數字與公開矩陣、`fault-checks/`、`bad-test-checks/` 核對一致,無 finding。
- S4:見 finding 3。
- S5:見 finding 8、9。
- 回退:見 finding 1。
- 實務隱患:見 finding 2。
- 審計修正紀錄:見 finding 5。

總結:最嚴重等級 major,blocking 5 條
