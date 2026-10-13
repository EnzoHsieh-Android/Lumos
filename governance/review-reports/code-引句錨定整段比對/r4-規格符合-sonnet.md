severity: minor

我逐條對照了規格的〈做法〉、〈驗收條款 S1–S8〉、〈兩階段上線〉、〈量測與留痕〉和〈同步改的地方·第一階段〉。核心行為都照規格做到,只有三處字面落差,都不影響判定。

- **核對方式:**
  - 我把 `scripts/lumos` 載進同一個 Python 程序,用規格列的輸入(前綴照抄後補收尾引號、換行補收尾引號、另一型收尾引號、插入「引句:」字樣、前文有未閉合開引號、引句後接註記、5 個連續未閉合標籤)逐一跑過。
  - 判定都與規格一致:前五種是 `stray`,接註記的照常錨定,連續未閉合標籤每條 `unclosed`。
  - `python3.14 scripts/test_lumos.py -k quote_full_span` 全綠,90 passed、0 failed。
- **舊判準:**
  - `_quote_rows_legacy` 本體與 cb832b56 的 `_quote_rows` 逐字相同。
- **其餘規格項目:**
  - 常數 `_QUOTE_WRITE_RULE` 是 `legacy`,章與帳同一行寫入。
  - 讀章三種情況、處置閘接住判準例外並讓 MemoryError 往外丟、手動 `quote-check` 的 `--rule` 與 `--compare-rules`、比較模式輸出字串、`gov --stats` 四格、兩個測試替身改收 `**kw`,都照規格。
  - 第一階段沒有改任何講判準保證的文件。

1. 處置閘診斷指令那一行缺 `[disposal] ` 前綴
severity: minor
blocking: 否
引句:`_qdiag = _esc_clean(f"    診斷:lumos quote-check {_drift_sh(_prov_path(rp), node=True)}`
file: `scripts/lumos:26525`
- 規格〈判準版本蓋在帳上〉寫「這一行與『引句判準:』那行都帶處置閘各行共用的 `[disposal] ` 前綴(r3 規格符合席)」。
- 實作的「引句判準:」那行有前綴,診斷指令那行卻是四個空格開頭、沒有前綴。判失敗時,處置閘輸出裡只有這一行不帶 `[disposal]`。
- 測試只用 `"診斷:lumos quote-check " in stdout` 比對,擋不住這個差異。
- 這是 r3 規格符合席提過的點,規格已寫入,程式沒跟上。要嘛補前綴,要嘛改規格。

2. 擋下事件的 `quote=` 片段,「空白壓成單一空格」發生在濾 Cf/Co 之前
severity: minor
blocking: 否
引句:`snippet = ("".join(c for c in re.sub(r"\s+", " ", _esc_clean(first[:400], 400))`
file: `scripts/lumos:25846`
- 規格的順序是:截 400 字、`_esc_clean`、濾 Cf 與 Co、空白壓成單一空格、取前 60 字。
- 實作先壓空白再濾 Cf/Co。
- 我實測 `甲甲甲甲甲 \u200b 乙乙乙乙乙甲` 得到 `quote=甲甲甲甲甲  乙乙乙乙乙甲`,中間是兩個空格,與規格「單一空格」不符。
- 不影響安全,只影響 REVISIT 讀片段時的字面。

3. 程式做了規格沒寫的:`lumos-code-loop/SKILL.md` 步驟 5 新增「補防護工具先找既有」一條
severity: minor
blocking: 否
引句:`**補防護工具先找既有**:修補要寫安全讀檔、字元消毒`
file: `skills/lumos-code-loop/SKILL.md`
- 規格〈兩階段上線〉第一階段只列兩處手冊改動:design-loop `SKILL.md` 折入那步,以及 `templates.md` 回滾席那列。第二階段才動 code-loop `SKILL.md`,而且是步驟 2。
- 這一條不在規格任何地方,但已隨第一階段進了凍結 patch。
- 要嘛補進規格〈兩階段上線〉的清單,要嘛從第一階段拿掉。

總結:最高等級 minor,blocking 共 0 條

規格相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/docs/lumos-toolchain-knowledge/Projects/引句錨定整段比對_計劃.md`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-quote/scripts/lumos`

實驗目錄已清空刪除。
