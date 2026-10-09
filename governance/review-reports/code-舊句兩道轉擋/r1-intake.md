# r1 收貨、重現與處置

## 開輪依據與材料

- `lumos pitfalls --diff f605fecb..f80352f6` 判 tier standard(有程式檔改動、沒命中風險型樣);沒有觸發任何棧別效能題,不用表態。照工具分級開 standard,不自行升級,所以不派資安席。
- 凍結審材 `r1-snapshot.patch` 8134 行,其中約 4300 行是設計審卷證與簿記帳,不審。程式與文件拆成三段,各 ≤1800 行,各派一席:`r1-part-lumos.patch`(主程式 1644 行)、`r1-part-tests.patch`(測試總檔、推送前掛鉤、README 圖產生器 1250 行)、`r1-part-docs.patch`(CHANGELOG、README、手冊、筆記 936 行)。另派架構對齊一席,讀前兩段。四席皆 Claude Sonnet,同門;沒派外家席。
- `seat-check` 對每席都報「沒提到 r1-part-docs.patch」:材料本來就依席分段,派工單的 `materials` 是三段聯集,每席的 `seats[].materials` 才是它該讀的那段。這項只觀測不擋。

## 收貨

- **磁碟滿事故**:四席跑到一半本機磁碟寫滿(ENOSPC),席位的 Bash 全部失效。
  - 主程式席、文件席、架構對齊席改用 Read 讀真碼完成,結論不靠跑指令,照收。
  - 測試掛鉤第一席(`正確性測試掛鉤1-sonnet`)的主鏡頭是改壞實驗,一次都沒做成。編排者清出空間後,同材料同鏡頭重派 `正確性測試掛鉤1b-sonnet`,兩份都留卷證、都記帳。
- **報告來源**:
  - 1b 席從子代理逐字稿抽最後一則正式報告存檔。
  - 另外四席交回時磁碟正滿,逐字稿沒寫進最後那則訊息,只能照完成通知原文逐字存檔。已核對這四份報告不含會被通知轉跳脫的角括號。
- **退回一次**:主程式席的總結句寫「沒有 blocker 或 major」,`report-normalize` 判總結句等級高於檔級宣告。退回該席,只改這一行;它交回的替代句照原文換上,其餘一字未動。
- 五份都過 `report-normalize`、`quote-check`(全數錨定)、`refcheck`(missing 0、out_of_range 0)。

## 重現(編排者機械重現)

| finding | 重現 | 說明 |
|---|---|---|
| TSB1 / TST1 | HIT | 重現副本把 `_note_audit_resolve` 的淺層偵測改成 `if False:`,`-k t_reread_block_undecidable` 仍 29 passed, 0 failed |
| TSB2 / TST3 | HIT | `LUMOS_SKIP_REREAD_CHECK=1 python3.14 scripts/test_lumos.py -k t_reread_block_undecidable` → 22 passed, 7 failed;未設變數 29 passed |
| TSB3 | HIT | `_NOTE_REREAD_MATCH_MIN = 6` 改成 1,`-k t_reread_block_layer2` 仍 17 passed, 0 failed |
| TSB4–TSB7 | 採信 | 席位改壞實驗總表逐列附改法與結果;都是測試補強,折入時以新測試先紅驗證 |
| TST2 | MISS | 重現副本把 `_DRIFT_SCAN_KINDS` 改成含 reread,`-k t_drift_ack_reread_kind` 的 ⑥ 變紅(6 passed, 1 failed),所以 ⑥ 有殺傷力,不是假綠;1b 席同一實驗也紅 |
| COR1 | 重現(讀碼) | `reread-record` 把 `r["text"]` 設成整條實體行、不截;讀端單份上限 256 KB 讀不了就判不了,block 下擋。寫端製造讀端拒收的檔 |
| COR2 | 重現(讀碼) | `_note_reread_uncommitted` 只比檔名、不看 `provenance_ok`;`reread-prepare` 用它排除 todo,所以來源核對沒過、還沒提交的紀錄會讓 prepare 不產項目檔,跟 record 印的「請重派判定者」相反 |
| DOC1 | HIT | `Projects/守檔筆記對照改動_計劃.md` 第 89 行仍寫「沒寫、寫 null 照 warn;這一版寫 block 也照 warn 並印一句「轉擋還沒做」」 |
| DOC2 | HIT | 同篇第 82 行仍寫「這一版不需要表態」 |
| DOC3 | HIT | `Projects/舊句檢查_計劃.md` 第 115、182、194、211 行仍是舊說法(沒寫照 warn、跟 gate 無關、預設只提醒) |
| DOC4 | HIT | `Projects/舊句兩道轉擋_計劃.md` 第 151 行〈回退〉寫「設定讀到之前的失敗改讀工作目錄設定」,第 65 行〈設計〉寫「不另設工作目錄設定的退路」,真碼照第 65 行 |
| DOC5–DOC8 | 採信 | CHANGELOG、README、手冊措辭;折入時逐句對真碼 |
| ARC1–ARC5 | 採信 | 架構對齊席附了對照的既有寫法 file:line |

## 處置

finding 編號:主程式席 COR1–2;測試掛鉤第一席 TST1–3;重派席 TSB1–7;文件席 DOC1–8;架構對齊席 ARC1–5。

- **折入**:COR1、COR2、TST1、TST3、TSB1–TSB7、DOC1–DOC8、ARC2–ARC5。
  - TST1 與 TSB1 同一件事(淺層案例用空範圍);TST3 與 TSB2 同一件事(行程內呼叫沒清單次略過變數)。
  - 重大問題 TSB1、TSB2、TSB3、DOC1、DOC3、DOC4 全折。
- **附理由放行**:ARC1。新增四支共用函式沒用 `_note_reread_` 前綴;其中 `_reread_summary_entries`、`_reread_rule_entry` 是設計規格逐字指定的名稱,條款與實作紀錄都用這兩個名字。另外兩支是同一組的,改名會讓同一組裡兩種前綴並存。這幾支也被漂移的照留表態共用,不只屬於回頭重讀。
- **駁回**:TST2。編排者把 `_DRIFT_SCAN_KINDS` 改壞後 ⑥ 翻紅,重派席同一實驗也紅,該斷言有殺傷力。

## 編排者另加的修正(不是席位發現)

- 修補代理回報 `Issues/舊句檢查超長行判準偏寬與留痕殘行` 第一條的放行理由「預設是 warn」已不成立:名稱消失檢查沒寫開關改成照總開關、預設 block 之後,超長行把「名稱只是較長識別字的一段」也算判不了,會誤擋沒設定的專案。這是本分支自己放大的風險,編排者併進本輪修補:超長行改用整字先篩(`_drift_m1_line_names`),測試 `t_drift_m1_long_line_whole_word` 修前紅(①)、修後綠,既有三支超長行測試照綠。Issue 第一條標已修、綁定改成真測試;第二、三條照原 REVISIT。

## 修補提交

- 202da1a4:G1–G6(修補代理,先紅後綠,每條新斷言附改壞→紅)。
- 5ce8115d:上面那條 Issue 第一條。

## 記帳註記

- 四筆單席帳的 `--scope-lines` 誤填成三段加總的 3830,帳上因此標了 scope_oversize。各席實際只審自己那段:主程式席 1644 行、兩個測試掛鉤席各 1250 行、架構對齊席讀前兩段共 2894 行(只判一致性、不逐行找 bug)。帳本只能追加,照留;彙總那筆照文件席實際的 936 行記。
