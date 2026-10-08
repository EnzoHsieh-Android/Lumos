# code-否決提案收齊查重 r1 收貨紀錄

- 凍結材料:r1-snapshot.patch(sha256 e1402634ed5004177baaf0318f6d9dc843719f4df539797ec75975183a7515ca),範圍 6467401a7012bb39acb3d5be064bb88758f45818..c728cf14a1fd5bb27f7dcba0793fd378b4360d89
- 席位:正確性-sonnet(找問題席,算人數)、架構對齊-sonnet(不算人數)。兩席收齊後才一次寫進卷證;收齊後 `git status` 只多卷證目錄,`git reflog -5` 最新仍是 c728cf14(席位的 git 實驗都在自己的 clone)。
- 正確性席第一次交的報告引句用反引號、總結行帶嚴重度字樣,quote-check 抽不到引句、report-normalize 標第 98 行;退回該席只改格式,內容不動,重交後兩道全過。
- 收貨三道:兩份報告 quote-check 全數錨定(正確性 6/6、架構對齊 5/5);refcheck 全 ok(5、9 條);seat-check 派工單沒列材料以外的要查項,vacuous。
- finding ID:正確性席 F1–F6 記為 c1–c6;架構對齊席 F1–F5 記為 a1–a5。
- 本輪有一條 major(c1),照代碼審規則整輪 accepted 必空,其餘 minor 全部折。

## 重現表

| id | 編排者重現 | 結果 | 採信 |
|---|---|---|---|
| c1 | `python3.14 scripts/test_lumos.py -k docs_command_count` 在 c728cf14:`2 passed, 2 failed`(ARCHITECTURE.md 與 reference.md claim 84、actual 85) | HIT | 採信,折 |
| c2 | 讀 `_rej_vault`:沒有 issue 節點、沒有 project 型作廢/否決節點、決策全是短句、唯一的不做類決策同時含「停案」「不做」;拿掉 `"issue"` 項或把視窗改成 `c[:5]`,佈景裡沒有能讓斷言變的資料 | HIT | 採信,折 |
| c3 | 本 repo `lumos rejections` 的「內文寫著不做」段列出 評測尺翻案_計劃#d1(推翻舊的刻意不做)、狀態標籤同步守衛_計劃#d1(「不做」在引號裡、內容是收窄舊結論) | HIT | 採信,折 |
| c4 | 臨時庫一篇摘要與正文各寫同一行 `WHY:同行 … [不選:甲方案]`:文字輸出「甲方案 ← 那行的決定:同行」印兩次,共 N 筆多一 | HIT | 採信,折 |
| c5 | 讀計劃:範圍第 2 點寫該測試不列條款,[S5] 是 manual 的模板化盤問那條;測試 docstring 自稱 S5 | HIT | 採信,折 |
| c6 | 同上臨時庫 `--json`:superseded-decision 的 context 是 `"→ ?"`;沒有 id 的不做決策文字輸出印成 `Projects/A_計劃#: …` | HIT | 採信,折 |
| a1 | 讀碼:摘要段的迴圈與 `_slot_summary_entries` 相同;正文段另訂 `_REJ_WHY_RE` 收全形冒號,而摘要段(`partition(":")`)與鄰居 `SYMBOL_RE` 只收半形 | HIT | 採信,折 |
| a2 | 讀碼:`_rejections_of_note` 自己 `read_text`,`env_text` 已是共用讀法(含記憶體 Env) | HIT | 採信,折 |
| a3 | 讀碼:其他輸出筆記的 JSON 用 `"node": rel`(帶 .md),新指令用 `"source"` 且去 .md | HIT | 採信,折 |
| a4 | 讀碼:規格閘其他印行抽成 `_spec_gate_print_*`,略過時印「—(原因;略過)」;新碼內嵌且 `except Exception: pass` 靜默 | HIT | 採信,折 |
| a5 | 臨時空庫 `lumos rejections`:印標題、「共 0 筆」與按概念比對那句;兄弟指令空結果只印一句「無…」 | HIT | 採信,折 |

## 根因分組與修前選例(共用範本 §3.1 第 0 步)

| 組 | 涵蓋 finding | 根因 | repair 案例 | preserve 案例 |
|---|---|---|---|---|
| g1 文件同步 | c1 | 新增頂層指令沒同步文件寫死的總數 | `t_docs_command_count` 修前紅、修後綠 | `t_docs_dont_hardcode_command_count` 修前綠、修後綠 |
| g2 測試佈景太鬆 | c2 | 佈景沒覆蓋每個關鍵字、視窗、issue 與 project 型節點 | 新斷言:各關鍵字單獨一筆、120 字內外各一筆、issue wontfix 與 project superseded/rejected 各一篇;對壞法(只剩「不做」、拿掉 issue、拿掉 project、拿掉視窗)要紅 | 原有 ①–⑦ 斷言的語意保留(筆數隨佈景重算) |
| g3 什麼算一條否決 | c3、c4、a1 | 收集口徑沒去重、決策關鍵字不分引述與翻案、正文與摘要認 WHY 的規則不同 | 摘要正文同一行只收一次;推翻/翻案類決策與只在引號裡出現關鍵字的決策不收 | 正文 `- WHY:` 列表行照收(真圖譜 5 行);圍欄裡的不收;被翻案又含不做只列一次 |
| g4 輸出形狀 | c6、a3、a5 | JSON 欄位沿用顯示字串、欄位名跟鄰居不同、空結果訊息跟兄弟不同 | JSON 用 `node`(帶 .md)、翻案的 context 是原值、缺值為 null;沒有 id 的決策不印 `#`;空圖譜印一句「無…(共 0 筆)」 | 文字輸出各段格式其餘不變;`decisions --superseded` 輸出一字不差 |
| g5 共用讀法與提醒寫法 | a2、a4 | 沒走共用讀檔函式;提醒行沒照鄰居抽函式、略過時不說原因 | 規格閘提醒抽成 `_spec_gate_print_rejections`,收集失敗印「—(原因;略過)」且沒有筆數;斷言 patch 的函式真的被呼叫 | 規格閘回傳碼與判定不變;正常時那行照印筆數 |
| g6 壞引用 | c5 | 測試 docstring 寫錯條款編號 | docstring 改成指到範圍第 2 點 | 無(純文字;不影響行為) |

- c4 附帶提到「4 格縮排的 WHY 行按 CommonMark 是縮排程式碼」:全專案唯一的程式碼區判定是 `_visible_lines`(只認圍欄),鄰居認前綴行也是先 strip 再比對;另立縮排規則等於引入第二種程式碼區判定,不做。c4 本體(重複計數)照折。
