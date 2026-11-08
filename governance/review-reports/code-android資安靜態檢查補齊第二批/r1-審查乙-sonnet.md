severity: minor

我只審了乙包。逐 hunk 讀完後,型錄、統計、待查證刪列、來源網址和內建檢查版本都對得上,沒有 blocker 或 major。三條 minor 都是覆蓋或文字精度問題。

## 查證結果

- **〈統計〉重數**:我用 `main_rows` 與 `load_rules` 另寫程式重數,下列數字都與 diff 一致。
  - 總列數 532,各主題 API 51、FLOW 32、STATE 28、CO 44、UI 111、ARCH 91、DATA 98、TEST 38、PERF 39。
  - 各級、級的組合、形狀 426、語意 106、人裁 4、出處不全 35、逐列查證 519、沒查證的 13 列。
  - 規則包 227 條(error 46、warning 119、info 12、hint 50),其中不接閘 29 條。
  - 被會擋的規則守到的列數 128。
  - 待查證 51 列(規則代號待查 48、來源待核對 3)。
- **〈待查證〉刪掉的 84 列**:我從 diff 的刪除行抽出 84 個編號,逐列對主表,現成規則欄都不含「待查」,來源欄都不含「未開頁核對」「搜尋摘要」「無網址」。反向也查了:主表仍含這些字樣、卻不在〈待查證〉的列是 0 列,所以沒有刪錯或漏刪。
- **型錄列與實驗數字**:API-48 到 API-51、ARCH-89 到 ARCH-91、DATA-88 到 DATA-98 的名稱、編號、現成規則欄、通電批次,都與計劃範圍 3 和〈實驗〉表一致。樣本內外的命中、抽判、誤報數,我用 `judge-insample.tsv` 與 `judge-oos.tsv` 重數,全部相符。
- **規則放置與通電批次**:所有規則訊息的 `[編號]` 都對得到型錄列。放 `rules/` 的列都標批一,放 `rules-unwired/` 的列都標未接。
- **來源網址**:我 curl 了 15 個網址(Android 風險指南 9 頁、MASTG 3 頁、CWE-78、Semgrep 規則檔、WebSettings),全部 200,內容也支持主張。
- **內建檢查的 Since 與預設**(官方檢查頁):
  - SdCardPath 為 Initial,SetWorldWritable 為 1.5.0,UnsafeDynamicallyLoadedCode 為 2.0.0。
  - UnsanitizedFilenameFromContentProvider 為 8.8.0(2025 年 1 月),SecretInSource 為 8.3.0,AuthLeak 為 2.2.0。
  - 四條漏登的內建檢查都是 Android Open Source Project 提供、Warning。
  - 「預設開」那一半,我只看到嚴重度,沒在頁面找到預設開關欄位,沒有獨立驗到。
- **三列錯登縮範圍**:我讀了 Google `BadCryptographyUsageDetector.kt` 原始碼,與 AOSP `CipherGetInstanceDetector.kt` 對照。
  - `VulnerableCryptoAlgorithm` 只看 Cipher,以前綴比對,所以 DESede 也會報。
  - `UnsafeCryptoAlgorithmUsage` 只在 `algorithm/mode/padding` 三段齊全時判斷,`RSA/ECB/NoPadding` 的 `ECB`、`NoPadding` 都沒有對應的報告分支,不報。
  - AOSP `GetInstance` 的 ECB 分支明寫 `!transformation.startsWith("RSA/")`,把 RSA 排除。
  - 所以 DATA-82、DATA-83、DATA-79 的縮範圍與 DATA-98 新列的說法都成立。
- **新舊互讀**:`check.py --catalog-only` 回報 0 個問題、還沒逐列查證 0 列。DATA-27 寫成「批一、批四(CI 範本:Android Lint)」時,`batch4_expected_tags` 對 `內建:SdCardPath` 回傳 `[CI 範本:Android Lint]`,自檢的比對條件是「該標籤字串出現在通電批次內」,並存寫法不會被誤報。
- **測試實跑**:`-k kt_catalog`、`-k kotlin_rulepack`、`-k kotlin_catalog` 分別 54、186、59 個測試全過。
- **S1 與 `_KTSEC_CASES`**:預期值表 S1 共 24 列,`C48` 到 `C71` 共 24 筆,一一對應。`C68`、`C69` 多加的 `BiometricPrompt` 宣告行,測試註解已寫明。

## 圖譜鏡頭

這次沒附固定席節點,我只看了 diff 牽連到的筆記。

`Systems/kotlin規則包` 那行 WHY 改寫後,測試綁定 `t_kotlin_rulepack_security_rules` 仍成立。WHY 裡的數字與〈實驗〉一致,包括混合內容 244 處抽判 120 處誤報 2、生物辨識 5%、外部網址 14 處誤報 1。本包沒有破壞該節點宣稱的行為或合約。

## Findings

### 1.
file: `skills/kotlin-idioms/checks-catalog.md`(〈統計〉節開頭、〈待查證〉節開頭)
severity: minor
blocking: 否

這次把〈輸入與口徑〉改成「〈待查證〉一節是手寫的,改主表時一起改」,但同檔另外兩句沒改。照做的人看到「由程式撈出」,會去找一支不存在的產生器,而且 `t_kt_catalog_stats_consistent` 的判準來源註解正是引用〈統計〉那句自稱。

引句:「由程式從各表撈出:「現成規則」欄含「待查」的規則代號,以及「來源」欄標(搜尋摘要)或(未開頁核對)的出處。」
引句:「用程式讀本檔各主題表格列數得出(不是手算;規則包數字讀 `configs/ast-grep/kotlin-android/rules*/*.yml`)。」

佐證:file: `skills/kotlin-idioms/checks-catalog.md`,在 9e277bf24 的版本上,搜尋「由程式從各表撈出」與「用程式讀本檔各主題表格列數得出」仍在。

### 2.
file: `scripts/test_lumos.py`,`_kt_stats_problems` 與 `t_kt_catalog_stats_consistent`
severity: minor
blocking: 否

計劃範圍 6 說〈統計〉要重數的項目包括各級、情境、待查證、守到的列數、逐列查證列數。測試只讀了總列數、各主題、規則包條數、不接閘條數四個數字(`num()` 與 `got` 只取這四處)。

具體改壞而測試照綠:
- 把 `待查證:51 列` 改成 `待查證:99 列`。
- 把 `A 242` 改成 `A 999`。
- 把 `error 46` 改成 `error 40`。

依程式讀碼這些都不會被抓到,我沒有實際對測試跑這些改壞。

現有一個實例:`情境決策表列數:56(證據樣式:主寫 (無) 的 8 列、例外寫 (無) 的 31 列、兩段都 (無) 的 5 列)`。我用 `_dt_header` 與 `_cells` 重數,主寫 (無) 為 14、例外 (無) 為 33、兩段都 (無) 為 10,與 8、31、5 不符。這是我自己的解析,口徑可能與作者不同,但若屬實,守這節的新測試抓不到這個舊誤差。計劃已用 `REVISIT:2026-11-22` 承認並附日期,所以只列 minor。

引句:「- 待查證:51 列(規則代號待查 48 列、來源待核對 3 列,兩者可重疊;2026-11-08 刪掉主表」
引句:「- 情境決策表列數:56(證據樣式:主寫 `(無)` 的 8 列、例外寫 `(無)` 的 31 列、兩段都 `(無)` 的 5 列)」

佐證:file: `scripts/test_lumos.py`,`_kt_stats_problems` 內 `num(...)` 呼叫只出現四處。

### 3.
file: `scripts/test_lumos.py`,`_kt_batch2_row_problems`、`_kt_batch2_misreg_problems`;`configs/ast-grep/kotlin-android/check.py:359`
severity: minor
blocking: 否

新測試只檢查 DATA-27 等列的現成規則欄,不檢查通電批次。型錄自檢那邊只判「已含批四的列,標籤要對」,不判「口徑認定該有批四的列,一定要寫批四」。

具體改壞而測試照綠:把 DATA-27 的 `批一、批四(CI 範本:Android Lint)` 改成 `批一`。我用 `check.py` 的 `catalog_problems` 在複本上實跑,回報 0 個問題。ARCH-89、DATA-95 把批四改成 `未接` 也是同樣路徑。

引句:「告警帶寫法=批一、批四(CI 範本:Android Lint)」
引句:「# 計劃範圍 2 的四條漏登內建檢查 → 該登在哪一列(DATA-27、DATA-85 是併進既有列,另兩條是新列)」

佐證:file: `configs/ast-grep/kotlin-android/check.py:359`,`want = batch4_expected_tags(c[5]) if "批四" in batch else []`。

最高等級 minor,blocking 共 0 條。

臨時目錄 `/tmp/lumos-seat-work/code-android資安靜態檢查補齊第二批/審查乙-sonnet/` 留著,待編排者收貨後處理。
