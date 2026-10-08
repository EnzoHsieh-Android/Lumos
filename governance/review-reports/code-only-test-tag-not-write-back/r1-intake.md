# code r1 收貨紀錄(code-only-test-tag-not-write-back)

八席齊了才動工作目錄。機械三道:report-normalize 後八份都合格(規格符合席由工具搬 2 處等級行;邊界、回歸、合約、通才、資安五席尾端總結行寫成「max severity: …」被判格式錯,退回各席自己改成「總結:全份最高等級 …」,其餘一字未動);quote-check 八份全錨;refcheck 全對得上;seat-check 只有觀測(多席沒寫出材料檔名,引句都錨進凍結 patch),不擋。
圖譜鏡頭:八席都回報派工詞尾端沒附固定席筆記。原因推論:本機 main 落後遠端很多,範圍起點 2aafdcb2 不在本機 main 的歷史上,dispatch-lens-hook 照設計靜默放行(手冊〈§3 須知〉①)。下一輪改用 `lumos impact --diff` 的結果手貼。

| id | 席 | 嚴重 | 重現/判讀 | 結論 |
|---|---|---|---|---|
| g1 | 通才 F1 | major | 席附臨時 repo 實跑三種英文寫法 rc0;編排者照抄情境寫成 t_nodehome_tag_exempt_hidden_sentence_caught_by_test_refs,修前版本(718d32bd)①放行 | HIT 採信,折:豁免只在 note_shape 總開關與 test_refs 推送時會擋才開,補 [S6] |
| c1 | 正確性 F1 | minor | 同 g1 | HIT 採信,折(同 g1) |
| b1 | 邊界 F1 | minor | 同 g1 | HIT 採信,折(同 g1) |
| s1 | 資安 F1 | minor | 同 g1 | HIT 採信,折(同 g1) |
| c2 | 正確性 F2 | minor | 新格 [S4] ⑪(空行夾住的單獨標記行整行刪掉)在 718d32bd 版本上 rc1 | HIT 採信,折:圍欄外空白壓平、連續空行收成一行 |
| b2 | 邊界 F2 | minor | 新格 [S4] ⑫(行首標記、全形空白前)在 718d32bd 版本上 rc1 | HIT 採信,折(同 c2) |
| a3 | 架構對齊 問3 | major | `scripts/lumos` 既有 `_NOTELINES_BARE_LIST_RE` 收 `-*+`、`1.`、`1)`(另收空核取方塊),跟新寫的正則重疊 | HIT 採信,折:改用既有正則,刪新常數 |
| a2 | 架構對齊 問1-2 | minor | 新常數擺在使用者之後;隨 a3 刪除 | HIT 採信,折 |
| a4 | 架構對齊 問3-2 | minor | 測試抄舊實作當對照組,本檔無先例(grep `_reference` 只有這支) | HIT 採信,折:docstring 寫明為什麼與何時刪 |
| a1 | 架構對齊 問1-1 | minor | 席說「_nodehome_ 區原本沒有呼叫別區私有函式的先例」;重現:awk 掃 `_nodehome_` 函式本體,`_nodehome_git`、`_nodehome_reader` 呼叫 `_lens_git`,`_nodehome_parse_note` 呼叫 `split_frontmatter`、`parse_frontmatter`——先例存在,前提不成立 | MISS 駁回 |
| k1 | 合約 F1 | minor | Projects/每支檔有家_計劃 [S12]「內容有變」定義沒提綁定標記例外 | HIT 採信,折:補括號 |
| k2 | 合約 F2 | minor | Systems/筆記內容閘 WHY 說其他字原樣,程式會連前面半形空白與 tab 拿掉 | HIT 採信,折 |
| k3 | 合約 F3 | minor | 「掃描規則只有一份」綁的測試只守 slot_parse | HIT 採信,折:[S5] 加比對 `_slot_strip_keys` 與 slot_parse 結果一致 |
| k4 | 合約 F4 | minor | 兩行現況說明只綁舊測試;TEST 支數 42 對機械數 61 | HIT 採信,折:補綁定、支數改機械數 |
| p1 | 規格符合 多做1 | minor | 清單符號多收 `1)` | HIT 採信,折:計劃〈範圍〉寫明 |
| p2 | 規格符合 多做2 | minor | `_slot_strip_keys` 回兩個值 | HIT 採信,折:計劃〈做法〉寫明 |

回歸席 clean(fuzz 30 萬筆、全 repo 6.8 萬行新舊 slot_parse 一致,新版不慢)。輪內有 major → 依代碼審規則 accepted 一條都不帶;a1 列 refuted。
