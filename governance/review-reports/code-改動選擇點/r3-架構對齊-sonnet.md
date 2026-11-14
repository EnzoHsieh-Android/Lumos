severity: major

## a1 測試所在檔的查找另寫了一套,沒用專案既有的 `類別.方法` 取最後一段慣例
severity: major
blocking: 是(判準:第二種做法;有最小重現)

**位置與做法**:`_choice_test_blobs` 這輪改寫成一次 `git grep -z -o -w -F -I` 帶全部測試名,自己組平台根前綴(`_choice_plat_prefix`)與副檔名樣式。專案裡已有同一件事的共用做法:`_test_in_tree`(`scripts/lumos:75001`)在被推版本的平台根底下整字找測試名,表態閘(`:74993`)與 note-shape(`:52225`)都用它。
- 專案認 `Class.Method` 是合法的綁定寫法,查找時取最後一段:`scripts/lumos:73222`、`:12402`、`:4015`。
- `_choice_guard` 收進來的 `t["name"]` 可能是 `FooTest.bar`,新函式卻拿整串去 `-w -F` 字面比對,在原始碼裡永遠對不到。

**預期 vs 實際**:預期這種名稱跟 `bar` 一樣查得到所在檔;實際查不到,記成 `?`。`_choice_kill_pick` 對帶 `?` 的雜湊一律重跑存活的行,`_choice_push_stale_tests` 也不比對。

**兩版證據**:在臨時 repo 放 `app/src/test/java/FooTest.kt`(內含 `fun bar()`),分別載入修前與修後的 `scripts/lumos`,對同一個提交呼叫:

| 版本 | 測試名 | 回傳 | 雜湊 |
|---|---|---|---|
| 修前 `f1be3141…` | `bar` | blob `5cf8df6e…` | `51d80e7a8204c81c` |
| 修前 | `FooTest.bar` | blob 空字串,只算名字 | `ae2ce85a3ff13d46`(穩定,存活的行會被帶過去不重跑) |
| 修後 `8e521300…` | `bar` | `['android','bar','5cf8df6e…']` | `51d80e7a8204c81c` |
| 修後 | `FooTest.bar` | `['android','FooTest.bar','?']` | `61071b2279dbe29a?`(帶不明標記,存活的行每次重跑) |

`does x`(反引號名)兩版都找得到。我也跑了 `python3.14 scripts/test_lumos.py -k t_choice_kill_test_files_in_test_paths`,19 個通過。這條測試沒有點號名稱的案例,所以抓不到這個差異。

引句:「一次 `git grep -z -o -w -F -e <名>…` 帶全部測試名,」

file: `scripts/lumos:77947`、`scripts/lumos:75001`、`scripts/lumos:73222`

歸因:有證據的修復回歸。修前點號名稱只是找不到所在檔、雜湊穩定;修後多了 `?` 的語意,同一個輸入從「帶過去」變成「每次重跑」。找不到所在檔本身是原有漏查:修前也是字面 `-F` 找整串。

## 三問回答

1. **分層與依賴方向**:大致跟鄰居一致。
   - 新碼用 `_drift_list`/`_drift_oids`、`_nodehome_list`、`_lens_git_dl`、`_git_timeout`、`_choice_is_test`(建在 `_nodehome_is_test` 上),沒有直呼底層。
   - `_lint_waivers_ai_pending(..., choice=True)`、`lv["ai_pending_choice"]`、`_cl_say_lint_waive_notes` 多一行,都沿用 `situation` 那一路的寫法。
   - 例外只有 a1:找測試檔這件事沒走 `_test_in_tree` 的取名慣例。
2. **命名與錯誤處理**:沒有發現不一致。
   - `_choice_scan_batch` 與 `_choice_scan_one` 同樣用 `_LINT_SARIF_MAX_BYTES`,同樣讓 `_ChoiceNoTool` 往外丟。
   - `⚠` 警告訊息前綴、rc 2(算不出選擇點)都跟 `choice-kill` 原有寫法一致。
   - 新增的 PITFALL/WHY 行欄位齊全,五個引用的測試名在 `scripts/test_lumos.py` 都存在。
3. **第二種做法**:除 a1 外沒有。
   - 掃描先整批、失敗才逐檔,是在 `_choice_scan` 內部分岔,沒有另起一套掃描。
   - 新增 `_CHOICE_PICK_BUDGET`、`_CHOICE_GUARD_FLOOR`,跟既有的 `_CHOICE_GOV_BUDGET`、`_ROLE_BUDGET_FLOOR` 同型。
   - AI 放行計數是擴充同一支函式的旗標,不是另一套計數。
   - 判測試路徑沿用 `_choice_is_test`。

## 圖譜鏡頭
這次沒附固定席節點,無從逐條判。

## 未驗範圍
- 只量了 `_choice_test_blobs` 的輸出,沒有真的跑 `choice-kill` 去看每次重跑的行數。
- 沒有核對 `r3-repair-tests.patch`。
- `_gate_event_fit` 縮 `tests` 清單時,新三欄元素會不會被縮壞,沒有驗。

不對齊共 1 條,其中 major 1 條
最嚴重:major;blocking 共 1 條
