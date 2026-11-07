severity: major

**① 分層與依賴方向**

沒有跨層直呼。`catalog_problems` 把自己讀好的列交給 `template_problems(rows)`,依賴方向是由上往下。這一點確實收掉了上一輪「主表讀兩次」中重讀型錄檔案的部分。

F1
severity: minor
blocking: 否
引句:「+def main_rows(text=None):」
主表的解析仍有三份,其中兩份沒有必要。
- 第一份是 `catalog_problems` 的迴圈(`configs/ast-grep/kotlin-android/check.py:149-168`)。它自己切 `\n## 情境決策表`、比對 `_MAIN_ROW_RE`、檢查欄數。
- 第二份是 patch 新增的 `main_rows`(`check.py:227`),邏輯是同一套,只是用 `rows.setdefault` 吃重複編號。
- 第三份是測試端的 `_kt_main_rows`(`scripts/test_lumos.py:125728`)。patch 沒有改它,它仍是 `t[:t.find("\n## 情境決策表")]` 加 `_MAIN_ROW_RE` 加 `_cells`。
- 既有的 `catalog_ids`(`check.py:83-88`)也是第四處切主表的地方,但那是舊債,不算這次新增。

`main_rows` 在正式路徑上只剩「單獨呼叫 `template_problems()`」會用到。那個情境只有測試會碰。為了測試,為同一張表多養了一份解析,而且 `catalog_problems` 並沒有改用它。更乾淨的做法是讓 `catalog_problems` 用 `main_rows` 產出 `rows`,或讓 `template_problems` 只收 `rows`。測試端直接呼叫 `m.main_rows()`,不要再抄一份。

**② 命名與錯誤處理**

編碼錯的回報形狀對得上既有慣例,新增的測試名也沒有偏離。
- 編碼錯回 `("<templates>", f"範本檔不是 UTF-8:第 {e.start} 個位元組讀不了({e.reason})")`。它跟既有的 `("<templates>", "找不到範本檔")`、`<catalog>` 同樣是角括號 id 加中文短句,回傳型別也是 `(id, 原因)`。
- `behavior_value` 沒有底線前綴,`_outside_fences` 有。同檔已有公開的 `catalog_ids`、`message_problems`,所以這不算不一致。
- 沒有新增 `t_kotlin_*` 測試函式。改壞四到改壞六以及架構 F1 的檢查,都併進既有的 `t_kotlin_test_templates_sections`,測試名沿用 `t_kotlin_*` 前綴。

這一問我沒有找到不對齊的地方。

**③ 第二種做法**

F2
severity: major
blocking: 是
引句:「+_FENCE_RE = re.compile(r"^\s*(```|~~~)")」
⚠ 這裡引入了第二份剝圍欄的實作,請編排者裁定要不要擋。
- `scripts/lumos` 的 `_visible_lines`(`scripts/lumos:5326`)與 `_fence_regions`(`scripts/lumos:5369-5395`)被標成「全檔唯一的 fence 判定」。
- 該段(約 `scripts/lumos:4025-4028`)和 `_search_visible_lines`(約 `scripts/lumos:5398-5412`)的註解都寫了:曾經有人另寫一份,結果兩份在邊界案例上分岔,後來被明令不准再加。
- 現在 `_outside_fences` 又自己寫一份逐行 toggle(`check.py` 新增的 `_FENCE_RE` 與 `_outside_fences`)。口徑已經分岔:
  - lumos 限縮進縮排 ≤3、不接受 tab。
  - lumos 要求收尾圍欄的長度不小於開頭圍欄。
  - lumos 的 strict 模式要求收尾行除了圍欄字元外不能有別的字。
  - check.py 全部不管這些。縮排 4 格的 ``` 是程式區塊,不是圍欄,但這裡會當成圍欄。
- 可能的辯護是 `check.py` 的檔頭寫「零依賴(只用標準庫)」,而且是獨立執行的自檢程式,不能 import `scripts/lumos`(那個檔沒有 `.py` 副檔名)。這個理由成立,但 patch 沒有在程式或筆記裡寫明「這是刻意的第二份、為什麼不借用」。依專案「借用既有設計」的原則,至少要補上這一句,或改成 `check.py` 載入 `scripts/lumos` 的函式。
- 同一個語言的第三種寫法在守衛測試裡:`_re.findall(r"^```kotlin\n(.*?)^```", body, _re.M | _re.S)`(`scripts/test_lumos.py` 的 `t_kotlin_test_templates_content_guards`)。那是成對非貪婪的正則,恰好是 `scripts/lumos:5283` 與 `scripts/lumos:4026` 點名「看不見未閉合圍欄」的那種寫法。它的用途是取出 kotlin 程式塊,不是剝圍欄,所以我只標記為同族,不另外計為不對齊。

F3
severity: minor
blocking: 否
引句:「+    mm = _re.search(r"行為測試或正向約束=([^;]*)", batch_cell)」
上一輪「通電批次兩套解析口徑」,口徑確實一致了,但現在是同一條正則抄在兩處。
- `check.py` 有 `_BEHAVIOR_RE` 和 `behavior_value`。
- 測試端 `_kt_behavior_value`(`scripts/test_lumos.py:125735`)又寫一份一模一樣的。
- 測試已經在載入 `m`,直接呼叫 `m.behavior_value` 就能共用。現在是兩份抄本,以後只改一邊就會再分岔。

F4
severity: minor
blocking: 否
引句:「+    have = set(re.findall(r"^## (T\d+)(?:[ \t]|$)", _outside_fences(text), re.M))」
標題的認法在 `check.py` 和測試之間又不同口徑。
- `check.py` 現在認 `## T3` 整行、`## T3 ` 後接空白或 tab,並且先剝圍欄。
- 測試端的 `_kt_template_sections`(`scripts/test_lumos.py:125839`)仍是 `^## (T\d+) .*$`,不認整行 `## T3`,也不剝圍欄。
- 結果是 `check.py` 判某節存在,測試端切段卻找不到它,守衛測試靜默少掃一組。這是 F3 同類的口徑漂移,但影響的是守衛測試的範圍,所以列 minor。

不對齊共 4 條,其中會擋的 1 條。
