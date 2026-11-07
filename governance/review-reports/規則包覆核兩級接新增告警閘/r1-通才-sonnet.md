severity: major

先講我沒能做到的:這台機器沒有裝 ast-grep,所以 SARIF 實測與 `check.py` 完整模式我都沒跑,相關判斷都靠讀主線程式碼(`Lumos/main`)。

## F1 提示級是否進得了閘沒有驗證,退路也和自檢互相打架
severity: major
blocking: 是(進閘與否是整份設計成敗的前提,退路改動會讓自檢本身出錯)
- 位置:範圍做 3、驗收條款 S2 與 S3、天花板 3。
- 問題一:做 3 說「提示級在 SARIF 對應 `note`」,依據是 `print/cloud_print.rs`。這個檔案名稱和描述都指向 GitHub 註解格式的輸出器,不是 SARIF 輸出器。所以「提示級會出現在 SARIF 裡」目前沒有證據,只有「GitHub 輸出會略過」。⚠ 我無法離線核對 0.42.0 原始碼。
- 問題二:S2 只驗「`check.py` 自己用 `--format sarif` 掃壞例有結果」,而且標成 `[manual:...]`,沒有機械測試。S3 的實際走閘驗證只用「覆核級」規則造命中。42 條提示級實際走過「新增告警閘 + lint-waive」從頭到尾沒有任何一條驗收。
- 問題三:做 3 的退路是「把 `rules-hints/` 嚴重度提到 info,`_DIR_SEVERITY` 跟著改」,但這會讓兩個地方出錯。
  - 一是 `rules-review/` 和 `rules-hints/` 都變成 info,目錄與嚴重度不再一一對應。
  - 二是主線 `check.py` 的 `catalog_problems` 目前用 `r["severity"] != "hint"` 判斷出處不全(`check.py` 約第 393 行)。spec 沒說這條要改,也沒說 `rules-hints-unsourced/` 要不要繼續保持 hint 來和 `rules-hints/` 區分。
- 佐證:`scripts/lumos` 主線的 SARIF 解析(約 42340–42375 行)不看 `level`,所以閘本身不會因為 note 而丟掉結果。這代表風險只在 ast-grep 是否輸出,正好是上面三點沒驗的部分。
引句:「ast-grep 的提示級在 SARIF 裡對應 `note`、在 GitHub 註解輸出被略過(ast-grep 0.42.0 原始碼 `print/cloud_print.rs`),0.51.1 沒人驗過。」

## F2 指紋含整段命中範圍,多行命中被編輯就重擋,隱患節沒提
severity: minor
blocking: 否(上線前的誤擋量測量能暴露,會造成噪音但不破壞設計)
- 位置:實務隱患「改名、重新縮排讓命中換指紋」與 PRIOR-ART 說「指紋綁規則加檔名加命中行」。
- 問題:實際指紋是 `規則 + 檔名 + 命中起訖行的正規化片段`,不是單行。
  - `_lint_new_key` 會取 `lines[line-1:end]` 作為片段。覆核級與提示級很多規則是區塊形狀,例如「HttpClient 設定區塊缺 `install(HttpTimeout)`」「`@Preview` 函式本體」「mutex 兩層」。
  - 這類命中範圍內改任何一行,指紋就變,原放行失效並重擋。
  - 反過來,語意規則「分不出對錯」,但放行綁的是文字片段:同檔同片段一次放行,日後相同片段的新命中也繼承這個放行。理由只對第一處當時的語境成立。
- 佐證:file: `scripts/lumos`(主線)`_lint_new_key` 約 42830 行,以及 `_lint_new_norm_snippet` 約 42812 行,保留縮排、去行尾空白。spec 的隱患只提「改名、重新縮排」,沒有「區塊內任何編輯」與「相同片段繼承放行」。
引句:「改名、重新縮排讓命中換指紋**:同一般新增告警,改了就重新擋一次。」

## F3 範圍漏了必須同步改的既有測試,自檢改動會讓它們紅
severity: minor
blocking: 否(實作階段會當場紅,但範圍清單不完整)
- 位置:範圍做 2、驗收條款 S1(只列一支新測試)。
- 問題:主線 `scripts/test_lumos.py` 有既有測試和 spec 的改法衝突,spec 沒列要同步更新。
  - `t_kotlin_rulepack_messages_cite_catalog` 用沒有 `dir` 鍵的假規則字典呼叫 `catalog_problems`,斷言「非 hint 規則引用出處不全的列要被抓到」。spec 把檢查改成「看所在目錄」,這個字典會缺鍵或判定改變。
  - 「規則目錄全空不准判通過」那段只清 `("rules","rules-review","rules-hints")` 三個目錄。新增第四個目錄後,規則並沒有全空,「一條規則都沒讀到」不會觸發,該測試會變紅。
  - 同一支測試檔裡還有 `rules-hints/` 放 info 的假資料,語意要重核。
- 佐證:file: `scripts/test_lumos.py`(主線)約 126457 行、126486 行與 `t_kotlin_rulepack_messages_cite_catalog` 後段。修改測試檔還要依專案規矩另行簽名,spec 沒提這一步。
引句:「「引用出處不全的列只准 hint 級」那條檢查改成「只准放在 `rules-hints-unsourced/`」」

## F4 數字與現況描述對不上
severity: minor
blocking: 否(文字不一致,不影響機制)
- 位置:實務隱患「誤擋量」與依據來源表「兩級 62 條一起處理」,以及範圍做 4 與做 5。
- 問題一:8 條搬走後,接閘的只剩 12 加 42 共 54 條,但隱患節仍寫「62 條」量測。
- 問題二:範圍做 4 說「加 `sgconfig-review.yml` 與 `sgconfig-hints.yml`」。這兩個檔在主線已經存在,要改的只有範本文字。
- 問題三:`Systems/kotlin規則包` 第 62 行寫「接上前不擋」、第 63 行寫「範本預設不接」。做 5 只說「補 WHY」,沒說要改這兩句現況描述,上線後它們就是過期的。`Systems/linter精選目錄` 第 198 行有明確改寫,所以那篇沒問題。
- 佐證:我用主線 `check.py` 的 `load_rules` 與型錄讀表函式數過,`rules` 145、`rules-review` 12、`rules-hints` 50,引用出處不全列的提示級規則恰為 8 條(`API-36`、`ARCH-3`、`UI-103`、`CO-37`、`FLOW-14`、`STATE-9`、`TEST-16`、`TEST-33`),與 spec 一致。
引句:「**誤擋量**:62 條在真專案的命中量沒量過(2026-11-05 只跑了會擋的那份)。」

## F5 守衛面只寫「不排除」沒分析,量測門檻與預算耗盡行為沒定義
severity: minor
blocking: 否(影響上線風險的完整性,不影響設計成立)
- 位置:實務隱患「守衛面」「誤擋量」。
- 問題一:實務隱患逐類答覆中,金流、對外送出、不可逆都有理由,「守衛面」寫「不排除」卻沒說明風險是什麼、如何控制。
- 問題二:「量出來太多就先只接覆核級」沒有數字門檻,上線前的判斷無從執行。
- 問題三:範本變三條宣告後,新增告警閘每側要跑 3 次 ast-grep(基準版與現在版共 6 次),預設總預算 300 秒、單條保底 30 秒。spec 只說「逾時與工具沒裝的處置照舊」,沒說第三條(提示級)因預算耗盡被略過時,是整體放行還是只略過那條。
- 佐證:file: `scripts/lumos`(主線)`_LINT_NEW_DEFAULTS` 約 42400 行 `budget_sec: 300`、`per_cmd_floor_sec: 30`。
- 實務隱患逐類:金流、對外送出、不可逆,同意 spec 排除(只讀本機、純文字與規則檔搬移)。守衛面見上。
引句:「守衛面:不排除——範本讓消費專案多兩份會擋的規則設定,動的是守衛面」

## 固定席逐條判
- `Systems/kotlin規則包`:不影響其合約。該節點掛 0 條合約、0 行 KEY,spec 只搬規則檔並改自檢,規則 id、樣本目錄、型錄對應都不變。唯一的連動是 F4 所述兩句描述變過期。
- `Systems/linter精選目錄`:不影響其 12 行 KEY。spec 明確改寫第 198 行「提示級預設不接」,屬於它自己宣告要改的範圍。主線 KEY 沒有任何一行寫死「覆核兩級不接閘」以外的行為。

總結:最高等級為 major,blocking 共 1 條。
