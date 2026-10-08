severity: minor

# r2 正確性-opus(否定現況句配回頭條件,第 1 輪修正)

實跑環境:`git clone --shared` 到自己的臨時目錄(HEAD a17be371,修正提交 0984c966),Python 3.14.6。每次改壞前先清 `__pycache__`,跑完用 `git -C <臨時複製> checkout` 還原。

## 逐項驗證(都成立,不列為 finding)

- **基線全綠**:`-k negation_hint_consumer_sim` 4 過 0 紅(約 27 秒);`-k graph_discipline_negation` 7 過(來源專用那支的 ①②③ 在來源 repo 真的有跑,沒被跳過);`-k note_shape_negation` 65 過。
- **模擬消費專案的測試真的會紅**:把 `t_graph_discipline_negation_revisit_source` 的 `_need_src(...)` 那兩行拿掉 → 模擬環境內層那支丟 FileNotFoundError,外層 ②(`-k graph_discipline_negation`)和 ③(要看到 skip 那一行)都紅,rc≠0。在模擬環境裡,原本的來源專用那支確實記成 `skip`(基線的 ③ 過,就是在確認這件事)。
- **拿到的檔案集合**:真正的安裝端(`_vendor_toolchain`)照 `_VENDORED_TOOLKIT + _VENDORED_TREE_FILES` 一支一支複製;模擬環境對兩個資料夾用 `copytree` 整夾複製,比真的多(會多帶未受版控的檔)。另有一支既有測試把 `_VENDORED_TREE_FILES` 跟受版控的檔逐一比對,所以差別只在沒提交的暫存檔,找不到會造成錯判的具體情境,不列。
- **五句新例句**:在自己的複製裡各改一處判定分支,只跑 `-k lexicon_pinned`,每次都只有 ③ 紅,而且只紅對應的那一句:
  - 修飾語視窗 9→8 → 紅在「功能還沒做完整支援新版本的」
  - 規則字眼改成只看否定字眼前面 → 紅在「還沒審不准推」
  - 拿掉「還沒」接「有」那條 → 紅在「還沒有對應的節點管這支檔」
  - 拿掉遇到停止字元就停(整段拿掉,或只從集合裡拿掉空白)→ 紅在「功能還沒做 的部分另談」(只拿掉空白那種還會讓 ② 常數比對一起紅)
  - 拿掉「的時候」→ 紅在「目前沒有的時候先跳過」
- **⑬**:`_ns_negation_collected` 改成不看 `seen`、每次都印 → ⑬ 的「只改程式檔」「只改開頭欄位其他欄」兩項紅。另一種改法:`seen` 改成把所有列都算進去(不只正文與摘要)→「只改開頭欄位其他欄」紅,表示第二種情境真的只動到開頭欄位的列,不是剛好沒改到東西。
- **⓪**:把 doctor 那行改回 `[w for w in r["warns"] if "看不懂" in w]` → ⓪ 紅(回 `[]`)。
- **`_note_shape_negation_parse` 跟原本的介面行為一樣**:把 1ca70d4f 版跟現版的 `_note_shape_negation_config`、`_ns_negation_doctor_lines` 載進來,餵 27 種輸入逐一比對,差異 0 筆。輸入包括 None、空位元組、壞 JSON、帶 BOM、`\xff\xfe`、bytearray、頂層是陣列/null/數字/字串、note_shape 是 null/陣列/字串/空物件、negation 是 null/warn/off/"OFF"/false/0/"block"/陣列/物件/"看不懂"/前面帶空白/帶零寬字元。提交前那條路(`_ns_negation_prepare`)還是呼叫 `_note_shape_negation_config`,所以 ⑩ 的替身仍然打得到。
- `lumos lint` 對兩篇筆記都是 0 問題;`note-shape --diff 1ca70d4f..0984c966` 沒擋任何東西;`pitfalls` 在新函式上沒有新的 lint 告警。

## F1 模擬消費專案那支測試的說明,寫錯哪一項會紅、為什麼紅
severity: minor
blocking: 否
引句:「翻紅釘:skill 斷言沒掛 _need_src(拆回同一支)→ ①② 紅(FileNotFoundError)。」
file: `scripts/test_lumos.py:58057`(t_negation_hint_consumer_sim)
file: `scripts/test_lumos.py:58065`(①前置那一項)

1. 實跑結果:把 `_need_src` 拿掉以後,紅的是 **②和③**,①照樣綠。① 只檢查模擬環境怎麼搭(有工具與範本、沒有 skill 和量測程式),跟 `_need_src` 有沒有掛無關,這個改法怎樣都不會讓它紅。如果照說明寫的「拆回同一支」,來源專用那支就不存在了,③ 會因為找不到 `skip t_graph_discipline_negation_revisit_source` 而紅。兩種改法都是 ②③ 紅、① 綠。
2. 「FileNotFoundError」也不是讀 skill 時丟的:實際輸出是 `No such file or directory: '…/gctl-neg-consumer-…/CLAUDE.md'`。原因是模擬環境裡沒有 `CLAUDE.md`/`AGENTS.md`,而那支測試先讀注入區塊。真正的消費專案有自己的 `CLAUDE.md`(注入的是自己的 slug),所以那裡的第一個紅會是「①CLAUDE.md 注入區塊跟範本一致」這項斷言不成立,接著讀 skill 時才丟 FileNotFoundError。結論一樣是紅,所以守衛本身有效;但說明把紅的位置和原因寫錯了。專案規則把內部不一致列為一律要報的例外;下一個照這句去做改壞驗證的人,會因為 ① 沒紅以為守衛沒接上。
3. 修法:說明改成「→ ②③ 紅(模擬環境沒有 CLAUDE.md,讀注入區塊就丟 FileNotFoundError;真的消費專案是注入區塊不一致,接著讀 skill 時丟例外)」。

最高等級:minor
