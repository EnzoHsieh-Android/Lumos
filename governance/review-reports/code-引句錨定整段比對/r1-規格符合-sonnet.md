severity: minor

我逐條對照了規格的〈做法〉〈驗收條款 S1–S8〉〈兩階段上線〉〈量測與留痕〉〈同步改的地方·第一階段〉和程式、測試。核心行為都照規格字面做到,沒找到 major 以上的偏差。下面只列「沒做到」和「做得不一樣」的地方。

**做到的項目(主要的)**
- **抽取規則**:規格第 1 到 6 步都對得上。
  - 標籤規則與舊判準同一條,配對、尾段各自計數、`unclosed` 和 `stray` 兩種 `kind`、200 字截斷加「…(截斷)」都對。
  - 我另外手跑了 5000 個標籤、20 萬個引號的輸入,都在 0.06 秒內完成。
- **判準版本**:`_QUOTE_WRITE_RULE="legacy"`,`rule` 是必填關鍵字參數,別的值丟 `ValueError`。四個呼叫點都明確傳 `rule`。
- **讀章與處置閘**:讀章邏輯和「引句判準欄不認得」訊息逐字符合。處置閘印「引句判準:<版本>」和「(帳上無章)」,判準丟例外時印型別、不 traceback,章取自載體列(`carrier`),都對。
- **手動 `quote-check`**:預設用寫側常數,第一行印判準,`--rule` 覆蓋,`--json` 多 `rule` 欄。缺報告或缺 `--spec` 擋下 rc2。
- **`--compare-rules`**:五行輸出、略過行、逐條清單都符合規格字面,參數互斥(帶報告、`--spec` 或 `--rule` 就擋下)和帳本不存在的處理也都對。
- **寫側擋下事件**:note 欄位順序與規格一致。`kind` 另用另一版判準算,出錯記 `kind=unknown cats=err`。
- **`gov --stats`**:四格互斥,輸出字面一致。
- **測試**:八支 `t_quote_full_span_*` 對應 S1–S8,兩個替身已改成收 `**kw`。

**1. 第一階段「文件一句都不改」沒有照做**

severity: minor
blocking: 否
引句:「折入要**新增機制**(新設定鍵、新帳欄、新指令或旗標)時,先在審計修正紀錄寫一行」
file: `skills/lumos-design-loop/SKILL.md`(patch 第 1305 行起)
- 規格〈兩階段上線〉寫「文件一句都不改」,〈同步改的地方〉也把所有文件放在第二階段。
- patch 在第一階段改了 `skills/lumos-design-loop/SKILL.md`(加一行折入紀律)和 `skills/lumos-design-loop/templates.md`(回滾席列加句),又在 `Systems/loop-convergence-recording.md` 新增整節。
- 另外還新增一篇規格沒預列的 Issue(`消費專案接入靜默失效回放漂移`)。
- 這些句子都沒有宣稱「整段保證」,所以不是規格擔心的說謊風險。但字面上是做得不一樣,卷證應該明講這是有意放行。

**2. 舊判準函式的 docstring 第一行被改了**

severity: minor
blocking: 否
引句:「舊判準(★原樣保留,一字不改★;quote-check 核心原文):」
file: `scripts/lumos:25791`(`_quote_rows_legacy` 的 docstring)
- 我拿改前提交 `cb832b56` 的 `_quote_rows` 整段和新的 `_quote_rows_legacy` 逐行 diff,只差函式名和 docstring 第一行,可執行程式碼一字不差。
- 規格與共用說明都寫「一字不改」,docstring 第一行字面上被動了。行為不受影響。

**3. 處置閘的診斷指令只在部分判失敗時印**

severity: minor
blocking: 否
引句:「診斷:lumos quote-check {rp} --spec {sp} --rule {_qrule}」
file: `scripts/lumos:26506`
- 規格寫「判失敗時另印一行診斷指令」,並只排除章不認得的列。
- 實作只在兩種情況印:判準丟例外,以及有引句錨不到。
- 報告零引句(`rows is None`)和讀檔失敗(`OSError`、`UnicodeDecodeError`)兩種判失敗不印。
- ⚠ 規格的「判失敗」是否包含這兩種,規格沒講清楚。

**4. 量測段要求的「補一行實測結果」沒有落到卷證;回放全跑也沒全綠**

severity: minor
blocking: 否
引句:「305 個回放一致;1 個不一致」
file: `docs/lumos-toolchain-knowledge/Verification/2026-10-13_引句判準第一階段推送前驗證.md`
- 〈量測〉第三點寫「第一階段實作後用 `lumos quote-check --compare-rules` 依同一口徑重算……並在本節補一行實測結果」。patch 裡的計劃〈量測〉沒有這一行,驗證紀錄也沒提到跑過比較指令。只有 REVISIT 2026-10-20 排了這件事。
- 〈推送前驗證〉寫「全部『回放一致』才推」。驗證紀錄是 305 個一致、1 個不一致。
  - 驗證紀錄說用改前程式回放同一個迴圈結果相同,並立了 Issue,處理合理。
  - 但這是對規格門檻的書面偏離,規格本身沒寫例外條件。

**5. 比較模式「略過」計數的非零分支沒有測試**

severity: minor
blocking: 否
引句:「略過:讀不到 0 組、非 UTF-8 0 組、壞行 2 列」
file: `scripts/test_lumos.py`(`t_quote_full_span_compare_and_event`)
- S6 要求照字面印「略過:讀不到 a 組、非 UTF-8 b 組、壞行 c 列」。
- 測試只釘了「讀不到」和「非 UTF-8」都是 0 的情況。快照讀不到時整組一起算進 `unread`、`nonutf`,這兩條路徑沒有任何測試走到。

**6. 程式做了規格沒寫的事**

severity: minor
blocking: 否
引句:「(f"(其中 {n_bad} 條格式不合)" if n_bad else "")」
file: `scripts/lumos:26531`
- 處置閘的 `quote-check: ✗` 那行,在規格沒寫的地方多接了「(其中 N 條格式不合)」。
- `--rule` 用 argparse `choices=_QUOTE_RULES`,輸入錯值時走 argparse 的 usage 錯誤,不是規格風格的「擋下:」訊息(結果同樣是 rc2)。
- 這兩處都是行為補強,不影響判定。

總結:最高等級 minor,blocking 共 0 條
