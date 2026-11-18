severity: minor

我讀了 `r1-docs.patch` 全 401 行。再把 `eebb84593` 檢出到 `/tmp/lumos-seat-work/code-選擇點第二批/合約-sonnet/repo`,逐項對照程式。文件與程式對得上的部分:
- `python3.14 configs/ast-grep/kotlin-android/check.py --catalog-only --sg /opt/homebrew/bin/ast-grep` 回「型錄問題 0 個」。選擇點表 37 列與〈統計〉寫的列數一致。
- `-k batch2`(35 案)與 `-k choice_by_row`(2 案)全綠。文件綁的九支測試名在 `scripts/test_lumos.py` 都存在。
- 「樣本標記指向不在表裡的列」那一條,我在副本樣本檔加一行 `// MISS C-99` 實測。有帶 `--sg` 與沒帶 `--sg` 都會報「表裡沒有這一列」,跟計劃寫的「不用 `--sg` 就查」相符。
- 「依列號」的口徑逐項對 `_gov_choice_counts`、`_gov_choice_by_row`、`_gov_choice_count_verdict`,都對得上:
  - 壞法鍵是 (檔, 行指紋, 列號)。
  - 終態是「曾殺掉 > 曾存活 > 跑不出結果」。
  - 原因冒號前等於「基準不綠沒跑」的不算。
  - 放行取 `ts` 最大那筆。
  - 沒有列號的放行另計。
- 驗證筆記的數字能自洽。甲 102→109 加乙 16→20 共多 11 個壞法,平均 0.55。比例 113/644=17.5%、20/193=10.4%,都在門檻內。「C-32 兩個、C-33 六個、C-37 兩個」合計 10,與甲各提交的增量吻合。
- 兩個真實專案的原始數字(甲、乙的行數、耗時、輸出位元組)我拿不到專案,無法重算,只驗了算術。

## k1 驗證筆記的 REVISIT 日期早於它要套用的 RETIRE-IF 兩個月窗
引句:「REVISIT:2027-01-15 讀 gov --stats 選擇點段「依列號」C-32 到 C-37 各列的殺掉、存活、跑不出結果與放行理由,照計劃 RETIRE-IF 判要不要撤列」
引句:「上線日 2026-11-17(RETIRE-IF 的兩個月從這天算)」
severity: minor
blocking: 否——只是回頭看的日期差兩天,照文件做不會出錯行為或讓推送被擋。
- 兩個月從 2026-11-17 算,到 2027-01-17 才滿。接手的人在 2027-01-15 被 doctor 點名後,照文件要判撤列,但 RETIRE-IF 的窗還沒滿。
- 計劃本身的 REVISIT 寫「最晚這天」讀數字,那句沒矛盾。矛盾只出在這篇驗證筆記把這個日期綁到「照 RETIRE-IF 判」。
- 佐證:`docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md` 的 RETIRE-IF 行寫「上線日(寫進第二批的 Verification)起滿兩個月」。
- 修法:驗證筆記的 REVISIT 改成 2027-01-17 之後,或改寫成「先讀數字,滿兩個月才判撤列」。

## k2 計劃範圍 6 要求 kotlin規則包 補一條「第二批來源與不收理由」的 WHY 行,實作沒有新增
引句:「補 WHY 行(第二批來源與不收理由)」
severity: minor
blocking: 否——內容有落在別處,只是計劃寫的落點跟實作不同。
- `Systems/kotlin規則包.md` 這次只改了既有的選擇點表那條 WHY(加進 NUL),另加 `about_code`、`verified_by` 與正文逐檔列規則的兩處。沒有新 WHY 行,也沒有不收清單(`runCatching`、頂層 `combine`、`remember`↔`rememberSaveable`、`==`→`===` 等)。
- 不收理由只在 `skills/kotlin-idioms/checks-catalog.md` 的〈選擇點表〉說明段與計劃本文。
- 修法:二選一。補那一行,或把計劃範圍 6 那句改成「不收理由放型錄說明段」。
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點表第二批常見誤用寫法_計劃.md:88`(範圍 6 的敘述,我看的是該檔的範圍 6 段落,行號是粗略位置)

## 圖譜鏡頭
- hook 沒附固定席節點(鏡頭計算超時),我沒有逐題的清單可判。能判的是這次動到的家:
  - `Systems/kotlin規則包` 與 `Systems/規格閘` 的改句,跟程式對得上(見上)。
  - `nul.yml` 與 `choice-batch2.kt` 已列入 `about_code`,每支新檔有家。
- 合約:三篇被改的筆記(兩個 Systems 節點、兩份計劃)裡,凡是 ★INVARIANT★、★IRREVERSIBLE★、★CHECKPOINT★ 都沒被碰。`Systems/規格閘.md` 的 `KEY:` 行(合約候選、門規則版本等)這次一行都沒動,所以沒有被破壞的合約或綁定測試。
- 新增的兩條 WHY(規格閘的「依列號」、kotlin規則包的 NUL)各帶 `[test:]`,對應測試存在且綠。
- 殘留風險:C-34、C-35、C-36 在兩個真實專案的 20 個提交裡一次都沒被挑到,編不過比例沒量到。驗證筆記已如實寫明,並綁了 2027-01-15 的回頭看,所以不算文件錯。

最嚴重:minor;blocking 共 0 條
