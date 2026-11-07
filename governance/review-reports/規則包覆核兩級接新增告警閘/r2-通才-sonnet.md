severity: major

## F1 做 6 讓分支自己放行就能把代碼審分級壓低,AI 放行等於整個逃掉審查
severity: major
blocking: 是(放行只要 10 個字的理由、AI 也能放,而讀的又是被審分支自己提交的放行檔,等於被審者自己決定要不要被審)
- spec 段落:範圍 做 6、實務隱患「作者隨手放行」、守衛面。
- 問題:`pitfalls --diff` 的 high 分級原本不看放行,所以「放行過、但仍要代碼審」是 AI 自放行的後盾。做 6 改成放行過的命中不算分級,而且「對所有 lint 宣告都成立,不只覆核兩級」。放行檔 `.lumos/lint-waivers.json` 是工作樹上被審分支自己會改的檔。
- spec 只說「放行後少審(只對作者已寫理由放行的那幾筆)」,沒處理作者就是 AI 這件事。AI 放行只進待看清單、doctor 只印軟提醒,不擋。
- 佐證:`file: scripts/lumos`(`Lumos/main`)的 `cmd_lint_waive` 只要求理由去掉空白後 10 字以上,AI 無互動終端時 `origin` 記為 `ai` 照樣寫入。`_lint_waivers_load(repo_root)` 讀工作目錄那份。同檔 pitfalls 的架構對齊段註解明寫「被審的分支不能自己改宣告決定自己怎麼被審」,所以那段讀的是 `_trusted_decl_ref` 起點版本。做 6 沒套這個原則,也沒說放行檔要讀哪一版。
- 修法方向:放行檔只讀範圍起點(受信版本)那份,或只認已被人 `--ack` 過的放行。
引句:「指紋(用新增告警閘同一支 `_lint_new_key` 算)在放行檔裡的不算進分級」

## F2 天花板 3 的「換版本靠自檢在 CI 上紅」邏輯上做不到
severity: major
blocking: 是(這是 spec 宣稱的唯一換版偵測,實際偵測不到消費專案的版本漂移,而漂移後的失效是靜默放行)
- spec 段落:天花板 3、範圍 做 3、做 4 的安裝句。
- 問題:自檢跑在工具鏈 CI,而 CI 釘死 0.51.1,消費專案用 `brew install ast-grep` 的版本更新時,CI 的 ast-grep 還是 0.51.1,不會紅。做 3 的檢查也只問「SARIF 至少一筆」,不問版本。
- 後果:消費專案升版後若 SARIF 形狀變了,`_lint_run_and_parse` 回 `([], True)` 當乾淨,覆核兩級整批靜默失效。
- 範本現行的安裝句是「要 0.51.1 以上」,不是釘版本。做 4 只在文字補一句「只在 0.51.1 驗過」,沒有機械保護。
- 佐證:`file: scripts/test_lumos.py`(`Lumos/main`)的 `_ktpack_sg` 註解「CI 裝釘版本 0.51.1」。`file: scripts/lumos` 的 `_lint_run_and_parse` 解析 SARIF 時不讀 level,結果為空就當乾淨。`file: docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md` 的安裝句寫「要 0.51.1 以上」。
引句:「消費專案用 brew 裝的版本可能更新,換版本靠做 3 的自檢在工具鏈 CI 上紅」

## F3 d1 把「有出處」當成能擋人的唯一門檻,把已知誤報多、先前因誤報降級的規則一起接上閘
severity: major
blocking: 是(同時推翻節點上有人裁依據的 RULE,而且沒有先量誤報)
- spec 段落:decisions d1、依據來源「依據不足的規則不准擋人」、範圍 做 7 對 RULE 的改寫。
- 問題:搬出去的只有「出處不全」8 條。其餘 42 條提示級規則全部接閘,其中有型錄自己標「誤報多」的規則,也有 2026-11-05 真專案實測因誤報才降成提示級的規則。
- 佐證一:`file: skills/kotlin-idioms/checks-catalog.md` 的 CO-17 列(規則 `kt-cancel-then-proceed`,有出處)寫「形狀:.cancel() 下一句不是 join(誤報多)」,在被接上的 42 條裡。
- 佐證二:`file: docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md` 的 `sgconfig-hints.yml` 條寫「誤報可能較高或依據的型錄列出處不全」,「2026 實測」節寫「降提示級 3 條」。
- 佐證三:同檔 RULE「規則在真專案誤報超過命中的一成就降提示級或改形狀」五欄俱全、`confirmed:2026-11-05`、`retire:人裁`,按專案 CLAUDE.md 有挑戰程式碼的效力。做 7 把它改成「降到 rules-unwired/」,卻把原本「降提示級」的那批規則接上閘,實際等於推翻這條 RULE,沒有人裁。
- 誤擋量要上線前才量(見 F11),所以「接閘的規則誤報是否過一成」目前沒有證據。
引句:「覆核級 12 條與有出處的提示級規則,直接用既有新增告警閘的宣告接上」

## F4 d1 決策紀錄還留著舊目錄名 rules-hints-unsourced/
severity: minor
blocking: 否(改一個名字就能修,不影響機制)
- spec 段落:frontmatter decisions d1 的 content,對照範圍 做 1 與 S1。
- 問題:修訂時新目錄改名為 `rules-unwired/`,正文、做 1、S1、回退都已改,d1 沒改。
- 專案 CLAUDE.md 把 `decisions:` 欄位視為有結構、可挑戰程式碼的紀錄,實作者照 d1 會建一個不存在的目錄。
- 範圍上 d1 也只說「出處不全」搬走,沒提 (b)「還沒量過的新規則」也進 unwired,語意比正文窄。
引句:「出處不全列上的 8 條提示級規則搬到不接閘的 rules-hints-unsourced/」

## F5 about_code 不能用 lumos append 寫目錄
severity: minor
blocking: 否(改成逐檔列或不列就能修)
- spec 段落:範圍 做 7 的 `Systems/kotlin規則包` 項。
- 問題:`about_code` 只收檔案。
- 佐證:`file: scripts/lumos`(`Lumos/main`)約第 31096 行,對目錄回「它是目錄;about_code 要寫到檔案」。現有 `rules/`、`rules-hints/` 的 yml 也沒進 about_code。`.yml` 不在 `_NODEHOME_CODE_EXTS`,本來就不需要「家」。
- 按 spec 照做,`lumos append about_code rules-unwired/` 會被擋。
引句:「`about_code` 補 `sgconfig-unwired.yml` 與 `rules-unwired/`(用 `lumos append`)」

## F6 既有測試的「規則目錄全空」案例會在加第四個目錄後翻紅,spec 沒列要改
severity: minor
blocking: 否(實作時一定會撞到,但驗收範圍與測試清單沒寫)
- spec 段落:範圍 做 2、S2 綁 `t_kotlin_rulepack_samples`。
- 問題:`file: scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples` 有一段 `for d in ("rules", "rules-review", "rules-hints")` 把 yml 刪光,再斷言「一條規則都沒讀到」要被報。
- 加了 `rules-unwired/` 之後,複本裡 8 條規則還在,`load_rules()` 不為空,這個斷言必紅。做 2 只提到 check.py 的訊息,沒提這個測試。
- 同一測試的 `_ktpack` 複本與 `t_kotlin_rulepack_messages_cite_catalog` 的假規則也沒列入調整。
引句:「另外兩句寫死三個目錄的訊息(嚴重度與目錄不符那句、」

## F7 做 5 用點名兩個檔案的黑名單,沒處理白名單「任何設定都收」這個根因
severity: minor
blocking: 否(目前只有一份 pack,實害有限)
- spec 段落:範圍 做 5、S3。
- 問題:r1 指出的根因是 `_lint_wt_allow` 接受 `configs/ast-grep/` 底下任何設定。做 5 的寫法是對 `sgconfig-review.yml`、`sgconfig-hints.yml` 兩個檔名回拒絕。
- 新增的 `sgconfig-unwired.yml` 或日後任何新設定,只要消費專案宣告就會每回合在收工檢查自動執行,而 unwired 的規則正是「依據不夠、不准擋人」的那批。
- 同一個函式的後半段已經把真實路徑算出來了,改成只放行 `sgconfig.yml` 的白名單,不需要多一個判斷。spec 的 S3 預期值也只驗了 hints 與 sgconfig 兩例。
- 佐證:`file: scripts/lumos` 的 `_lint_wt_allow` 後半段用 `realpath` 與 `commonpath` 判斷「在 configs/ast-grep/ 底下」,沒有檔名限制。
引句:「對 `--config` 值是規則包 `sgconfig-review.yml` 或 `sgconfig-hints.yml` 的命令回」

## F8 做 3 的 SARIF 自檢只問「有沒有任何結果」,不驗是目標規則、也不驗格式
severity: minor
blocking: 否(自檢偏弱,不影響正確性)
- spec 段落:範圍 做 3、S2。
- 問題:「各一條規則的壞例樣本掃出至少一筆」就過。但設定檔載入的是整個目錄的規則,別條規則命中也算通過。
- 閘靠 SARIF 的 ruleId 與訊息(型錄編號開頭)產生放行指紋與擋下訊息,檢查沒驗這兩個欄位。
- spec 也沒指定用哪兩條規則,測試換規則時結果可能變。
- 建議至少要求結果裡有目標規則的 `ruleId`。
引句:「拿 `rules-review/` 與 `rules-hints/` 各一條規則的壞例樣本用 `--format sarif` 掃,結果要至少一筆」

## F9 做 6 沒講清楚指紋雜湊,而且只修了放行過的命中,沒修「基準版就有」的命中
severity: minor
blocking: 否(實作細節缺口,測試 S4 會抓到前者;後者是既有行為的延伸)
- spec 段落:範圍 做 6、S4。
- 問題一:`_lint_new_key` 回的是未雜湊的 `(原始鍵, 是否弱比對)`。放行檔存的是 `sha256(原始鍵)[:16]`,雜湊在 `_lint_new_diff_claims` 裡做。spec 只說「用 `_lint_new_key` 算」,照字面比對永遠對不上。
- 問題二:`pitfalls --diff` 的 lint 命中是「落在新增行上」,不是閘的「基準版對現在版差集」。縮排或搬動造成的重新新增行,閘判不新增、也沒有放行指紋可放,分級仍被推成 high。接了 54 條規則後這類情況變多。
- 問題三:弱比對的指紋是規則加檔名加訊息,放行一筆就會把同檔同規則的所有命中從分級拿掉。
- 佐證:`file: scripts/lumos` 的 `_lint_new_key` 與 `_lint_new_diff_claims`(約第 42830 與 42856 行),以及 pitfalls 收 lint 命中那段的 `c["line"] in added.get(c["file"], set())`。
引句:「這條對所有 lint 宣告都成立,不只覆核兩級。」

## F10 「預算不夠時先跑會擋的那份」擋不住預算用完的後果
severity: minor
blocking: 否(上線前量測會暴露,風險是誤擋)
- spec 段落:範圍 做 4。
- 問題:閘的預算預設 300 秒、單條保底 30 秒。預算不夠沒跑到的命令被記成 `undone kind=budget`,判定是擋,不是自動放行。
- 排序只決定誰先跑,不改變後兩條沒跑到時整次被擋。大型推送在改前後各跑三份設定共六次掃描,更容易撞到。spec 把「排第一」當成緩解,但結果還是擋。
- 佐證:`file: scripts/lumos` 的 `_lint_new_run_cmds`(剩餘預算小於 `per_cmd_floor_sec` 就記 `undone`)與 `_lint_new_tools`。
引句:「`sgconfig.yml` 那條排第一,預算不夠時先跑會擋的那份」

## F11 誤擋量的「超過 20 筆就延後提示級」只是散文,沒有驗收、沒有順序,也沒說怎麼量
severity: minor
blocking: 否(違反的是專案「承認風險要附回頭看的條件」,不是機制錯誤)
- spec 段落:實務隱患「誤擋量」、做 4、S5。
- 問題:做 4 把範本改成三條宣告,和這份計劃同一個變更落地。「上線前量、超過 20 筆就只接覆核級」要靠事後退回範本才做得到。
- S1 到 S5 沒有一條驗這個門檻,S5 只造一筆命中。
- nowinandroid 沒有推送,「單次推送新增命中」怎麼算沒定義(整份掃等於全新增)。
- 專案規則 4 要求這類條件寫成 `REVISIT:` 或帶事件的回頭條件,而不是散文。
引句:「任一專案單次推送新增命中超過 20 筆,先只接覆核級、提示級那條宣告延後」

## 固定席逐條判
- `Systems/kotlin規則包`:該節點沒有 KEY、沒有合約。
  - 「查不到的列標(出處不全),引用它的規則只准提示級」那條 WHY 綁的是 `t_kotlin_catalog_rows_wired`,這個測試並不驗「只准 hint 級」。真正驗它的是 `t_kotlin_rulepack_messages_cite_catalog` 與新增的 S1。做 7 說「綁的測試照舊」,改寫後的新句子會沒有測試綁。這是 minor。
  - 那條 RULE 的衝突見 F3。
- `Systems/linter精選目錄`:12 行 KEY 都是各語言工具選單與事實。
  - 範圍 做 4 只改 Kotlin 範本與一句「提示級預設不接」,不影響這些 KEY。
  - 判不影響。
  - 該節點「管 1 支檔、沒寫負責範圍」,本計劃落點沒要求補,不阻擋。

總結:最高等級為 major,blocking 共 3 條
