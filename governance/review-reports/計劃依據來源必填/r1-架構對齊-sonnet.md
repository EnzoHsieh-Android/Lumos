severity: major

**第一問 模組邊界**

規格閘放新檢查、doctor 放提醒、check.py 放型錄計數,這三個落點都對。

引句:
「新開一支 `_spec_gate_sources_part(env, rel, text)`,在 `_spec_gate_front` 裡排在待決問題(`_spec_gate_pending`)之後、條款綁定(`_spec_gate_clause_part`)之前」

- 既有的 `_spec_gate_front` 就是照順序串各道:`_spec_gate_pending` 回 1 或 None,接著 `_spec_gate_clause_part`,再接 `_spec_gate_expected_part`。見 `scripts/lumos:15474`。
- 新道的形狀(擋回 1、沒事回 None)跟 `_spec_gate_pending`(`scripts/lumos:15393`)一致。
- 排在條款綁定前面的理由站得住。`_spec_gate_clause_part` 遇到零條款會提早回 0,所以預期值表那道不會跑。

引句:
「`lumos doctor` 數出狀態是 todo 或 doing、沒有〈依據來源〉節或節裡有缺出處列的計劃,列名字(最多 20 篇)」

- doctor 已有同形的提醒:`warn_soft` 加上限 20。見 `scripts/lumos:3862` 一帶的 P 段,以及 `scripts/lumos:4174` 的 `[:20]`。
- 這一條沒有問題。

引句:
「口徑跟 `catalog_problems` 同一套讀表(主表列用 `_MAIN_ROW_RE` 認、`_cells` 切欄、第 12 欄是來源)」

- 型錄計數放在 `configs/ast-grep/kotlin-android/check.py` 是對的。`catalog_problems` 讀表的 `_MAIN_ROW_RE`、`_cells` 和第 12 欄 `c[11]` 都在那裡。見 `configs/ast-grep/kotlin-android/check.py:147`。
- 但 `catalog_problems` 回傳的是「問題清單」,整份都是會擋的。計劃卻要它再多出一條只印數字、不擋、也不進清單的通道。
- 這條新通道要怎麼不影響退出碼,計劃沒寫接口。這是 F4 的內容。

**第二問 命名與錯誤處理**

引句:
「另立一個常數 `_PLAN_SOURCES_SINCE`(純日期,值取本案實作合併進主線的隔天,跟 `_HIGH_RISK_EVIDENCE_SINCE` 同一個取法)」

- 常數、環境變數 `LUMOS_PLAN_SOURCES_SINCE`、測試總檔預設 9999-12-31,都跟既有寫法對得上。
- 對照:`scripts/lumos:14221`(常數)、`scripts/lumos:14281`(讀法 `_expected_since`)、`scripts/test_lumos.py:159`(測試預設)。
- 計劃沒說要不要另寫一支 `_plan_sources_since()`。這是小缺口,放進 F3。

F3
severity: minor
blocking: 否
引句:
「欄五種都不是 → 印哪一列缺什麼並擋」
- 預期值表那一道的擋下訊息有固定三塊:
  - 標頭 `[spec-gate] 預期值表: ✗ — …N 處不合:`
  - 逐條 `    • 第 N 行:…`
  - 一行 `範例:…`(`_EXPECTED_EXAMPLE`)

  見 `scripts/lumos:15515`。
- 計劃只寫了「缺〈依據來源〉」這個詞,沒說採同樣的三塊。
- 計劃對舊計劃「印一行提醒」,而預期值表對不用查的計劃什麼都不印(`scripts/lumos:15511`)。這是新增的輸出形狀,沒有對照。
- 另外,計劃沒說要不要仿 `_spec_gate_expected_part` 在通過時印一行 ✓。
- 結構是對的,只有訊息沒對齊。

F4
severity: minor
blocking: 否
引句:
「印成一行數字與前 20 個編號;不擋。」
- `catalog_problems` 的回傳型別是 `[(編號, 訊息)]`,有一筆就算紅。見 `configs/ast-grep/kotlin-android/check.py:129`。
- 「不擋」的計數得放在另一支函式或另一個回傳值,計劃沒寫。
- 若硬塞進 `problems`,範圍 4 的「退出碼不因這個數字改變」就破功。
- 這是計劃缺細節,不是違反既有做法。

**第三問 第二種做法**

F1
severity: major
blocking: 是
引句:
「**出處**:下列之一,寫在「出處」欄:①網址(`http://` 或 `https://` 開頭);②repo 內存在的檔案路徑(反引號包住,refcheck 驗得到)」
- 專案裡已經有三套「這格有沒有出處」的判法,計劃另立了第四套五分類,沒說明跟前三套的關係:
  - 預期值表的來源格只看 `_real_chars(src) < 4`。見 `scripts/lumos:14380`。
  - 型錄來源欄用 `_WEAK_SRC`,加「網址或登記過的縮寫」的 regex。見 `configs/ast-grep/kotlin-android/check.py:169`。
  - 筆記的 `[出處:]` 欄位另有一套。
- 計劃自己承認「預期值表的來源欄講的是每條條款預期值的出處,本節講機制的出處」。兩個都是計劃筆記裡的出處欄,卻用兩種不同的合格標準。
- 同一份計劃裡,預期值表的來源寫「本計劃範圍 1 插入點」就過,〈依據來源〉的出處欄寫同樣的話會被擋。
- 路徑存在與節點存在,repo 已有共用函式 `_refcheck_scan` 和 `_SINGLE_WIKILINK_RE`。見 `scripts/lumos:509`、`scripts/lumos:20256`。
- 計劃只說「refcheck 驗得到」,沒指明直接呼叫它,有被另寫一套的風險。
- 型錄自己的判準(網址或縮寫)跟計劃新定的(網址或〔查證〕)也不同,這是第三種口徑。
- 這個判法要寫成一支共用函式,並在計劃裡說明跟預期值表來源格、型錄、`[出處:]` 的關係。規格閘與 doctor 兩處必須共用這支。

F2
severity: minor
blocking: 否
引句:
「計劃筆記裡標題剛好是 `## 依據來源` 的一節,內容是一張表(欄:機制|依據|出處)。」
- 既有找節的做法是 `_h2_section_lines(text, h2_re, heads=...)`(`scripts/lumos:13783`),搭配 `_EXPECTED_H2_RE`、`_expected_table_lines`、`_expected_split_cells`。
- 這套做法會處理節出現兩次、圍欄內的假表、分隔列、列數與格長上限。見 `scripts/lumos:14384`。
- 計劃沒點名要重用它們,只說「標題剛好是」。
- 這點目前還只是缺口。若實作者另寫節名比對與表解析,就會落入第二種做法。
- 計劃要明寫:節用 `_h2_section_lines`,表解析抽出與預期值表共用的一支。

不對齊共 4 條,其中會擋的 1 條。
