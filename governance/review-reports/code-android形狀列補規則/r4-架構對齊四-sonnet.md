severity: minor

我沒有在 `/tmp/lumos-seat-work/code-android形狀列補規則/架構對齊四-sonnet/` 建任何路徑,也沒改 repo。整份判讀靠讀 patch 和對照既有檔,沒跑測試,也沒跑 ast-grep。

## 問 1:分層與依賴方向
結論:對齊。我找不到跨層直呼。

- 新的註冊判斷放在 `utils/`,格式與掛法跟 `debug-only.yml` 一樣。
  - 對照:`file: `configs/ast-grep/kotlin-android/utils/debug-only.yml:5``。
  - `sgconfig.yml` 本來就掛 `utilDirs: utils`,所以消費專案只宣告 `rules/` 也讀得到:`file: `configs/ast-grep/kotlin-android/sgconfig.yml:1``。
  - 引用方向跟 `in-debug-only-branch` 相同:規則用 `matches:` 引用 util,util 不反過來引用規則。
- `check.py` 的 `scan` 改回三元組,`check.py` 內兩個呼叫端和 `scripts/test_lumos.py` 的唯一呼叫端 `m.scan(sg, cfg, root)` 都跟著改。
  - 對照:`file: `configs/ast-grep/kotlin-android/check.py:914``、`file: `scripts/test_lumos.py:127262``。
  - 測試只經 `m.scan` 和 `m.main_rows` 讀規則包,沒有另抄讀法。
- 規則檔放哪個目錄,跟既有批次同一套:升級的進 `rules/api.yml`、`rules/architecture.yml`,沒升的留 `rules-unwired/`。對照:`file: `configs/ast-grep/kotlin-android/rules-unwired/architecture.yml:14``。

## 問 2:命名與錯誤處理
結論:規則 id、訊息句式、樣本、統計數字都跟鄰居一致。「warning 也擋、建議語氣放 `rules-hints/`」有兩處不一致,另有一處測試擺放不同。

- 規則 id 都是 `kt-…`,訊息都是 `[型錄編號]錯在哪;改用/改成 …`。
- 註解開頭 `# [[Projects/…_計劃]] 範圍 N:不接閘/會擋(樣本外…)` 跟既有規則一樣。
- 樣本都有 `// BAD` 與「容易誤報:」註解。對照:`file: `configs/ast-grep/kotlin-android/samples/good/kt-jackson-default-typing/src/main/kotlin/kt-jackson-default-typing.kt``。
- 型錄通電批次那句「未接(規則在 rules-unwired/:樣本外誤報超過一成或量不夠)」已有 21 筆先例,`file: `scripts/test_lumos.py:129658`` 也是同一句。
- 統計新數 228 / 49 / 118 / 49 / 27 我重算過:API-2 加 error,ARCH-59 加 warning,另兩條是 hint,數字對得上。

severity: minor
blocking: 否

「warning 也擋」在四處說法是一致的。規格(用詞節、範圍 4)、型錄 ARCH-59 列、規則包節點的檔案行和 WHY 行,都寫 `rules/` 的 warning 會擋、看目錄不看等級。規則檔註解沒寫放置判準,但沒有講反。

不一致的是「建議語氣的規則過了只放 `rules-hints/`」。這條判準只出現在計劃範圍 4 和規則包節點的 WHY 行。規則包節點「檔案」段對 `sgconfig-hints.yml` 的定義沒改,仍寫「誤報可能較高」。對照:`file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:80``。

這樣 `rules-hints/` 同時有兩個進入條件:既有的「誤報可能較高」,和新的「出處只有建議語氣」。節點「怎麼改」第 1 點也只講 `rules-review/`、`rules-unwired/` 到 `rules/` 的升級路徑,沒有通往 `rules-hints/` 的路。型錄通電批次也沒有對應寫法,這種規則只能沿用既有的「批一(只有提示級規則,預設不接)」。

規格的歷史列也沒標記作廢:r1 那行還留著「UI-33 最多升 warning」,同節 r3 和實作那兩行才更正。

引句:「過了也只搬提示目錄 `rules-hints/`(hint,範本預設不接,推送前不擋),不放 `rules/`」
引句:「提示級規則(`rules-hints/`),誤報可能較高,範本預設不接。」
引句:「API-2 升級時拿掉 review-fp 樣本、UI-33 最多升 warning。」

severity: minor
blocking: 否

計劃範圍 4 寫「過升級條件的規則搬到 `rules/`、等級改 error」,量測結果表卻讓 ARCH-59 以 warning 進 `rules/`。
- 先例:`kt-compose-password-keyboard` 升級後是 error,測試還釘著它。對照:`file: `scripts/test_lumos.py:127243``,以及該測試 docstring 的「等級改 warning → S2 紅」。
- 另一側:`rules/` 本來就有大量 warning 規則,所以 warning 進 `rules/` 本身不算新做法,不一致只在規格通則與結果表之間。
- 我判不準這算「例外已在結果表明寫」還是「通則沒改」,標 ⚠ 交編排者。

引句:「過升級條件的規則搬到 `rules/`、等級改 error,型錄通電批次改」
引句:「搬 `rules/`、warning(會擋;原文寫明會注入錯的實例)」

severity: minor
blocking: 否

型錄現成規則欄的檢查寫在 `t_kotlin_rulepack_security_rules` 裡,做法是一個新的 `_KTSHAPE_CATALOG_IDS` 元組加一個迴圈,只驗「自寫 ast-grep <id>」。

鄰居的做法是每批一個專屬 `t_kt_catalog_security_lint_batchN`,用寫死的列表驗名稱、現成規則欄和通電批次三樣。對照:`file: `scripts/test_lumos.py:129676``(`c[9] != batch`)。新做法沒釘通電批次,這次真正改的是通電批次(API-2、ARCH-59 改為批一)。讀表用的 `main_rows` 與鄰居相同,所以只是擺放與覆蓋範圍不同,不是第二種讀法。

引句:「cat_rows = {r: c[5] for r, c in m.main_rows().items()}」

## 問 3:第二種做法
結論:沒有引入第二種做法。

- 第 4 條指的是逐例表第五欄(預期行號)、型錄實測欄寫理由、表內分段註解,這三項 r2 已放行,理由成立,我不重報。
- 「`rules-hints/` 依出處語氣分流」是這份 diff 新帶進來的分類軸。我已併入問 2 第一條,不另算。

不對齊共 3 條,其中 major 0 條
