severity: major

**第 1 問:分層與依賴方向。對齊。**
- 新碼放在 `check.py` 的「`situation_sample_problems` 之後、`_BEHAVIOR_RE` 之前」,位置跟鄰居一樣。
- 呼叫 `scripts/lumos` 的私有函式,是既有做法:`configs/ast-grep/kotlin-android/check.py:699` 的 `lm._kt_sit_row_check`、`:740` 的 `lumos._kt_sit_text_segments`,都是同一種跨檔借用。新增的 `_kt_trigger_re`、`_kt_sit_text_segments` 跟它們同形。
- 路徑篩選抽成 `_kt_sit_path_ok`(`scripts/lumos`),推送端兩處與型錄反查共用同一支,沒有跨層直呼,也沒另組條件。這點比鄰居更整齊。
- 呼叫端的接法跟 `situation_sample_problems` 一致:`check()` 與 `main --catalog-only` 都顯式載入 lumos 後傳進去。載入失敗時回 `("<api>", …)` 這類問題項,不丟例外。
- `scan_ranges` 是 `scan` 的超集,`scan` 退成薄包裝,原本的三元組呼叫端不動。這是延伸,不算第二套掃描。

**第 2 問:命名與錯誤處理。大致對齊,有兩個小處不齊。**
- 錯誤回傳都是 `[(鍵, 原因)]`,鍵用 `<api>`、`<reach>`,跟既有的 `<pack>`、`<situation>`、`<templates>` 同形。
- 節標題用 `_API_TITLE`、`_UNREACH_TITLE` 常數,跟 `_WIRING_TITLE` 同風格。
- 函式簽名 `(text, rows, …)` 跟 `wiring_problems`、`pending_problems` 一致。
- 讀表函式取名與回傳是 `_api_table`、`_unreach_table`,跟 `wiring_table`、`_pending_table` 同型,回傳形狀各表本來就不同。
- 不齊處見 finding 2、3、4。

**第 3 問:第二種做法。不對齊,有 1 條 major、3 條 minor。**

**Finding 1 — `_fence_body` 另寫了一份圍欄內文取法**

severity: major
blocking: 是
引句:「regions, unterminated = _fence_regions(lines, True)」
- 新的 `_fence_body` 自己呼叫 `_fence_regions`,自己做「先嚴格、沒關再退寬鬆」,自己組出圍欄內的行號集合,自己用 `startswith("#")` 找小節標題。
- 既有的圍欄判定是 `_visible_lines`(`configs/ast-grep/kotlin-android/check.py` 內,`template_sections` 就是用它)。
- lumos 端的 `_visible_lines` 本來就有 `keep_fenced` 參數可保留圍欄內文,見 `scripts/lumos:5375`。check.py 這份是它的刻意複本,只缺 `keep_fenced`。
- 一致的做法是給 check.py 的 `_visible_lines` 補 `keep_fenced`,再由它取圍欄內文。現在這樣把「退回寬鬆」的取捨抄成第三份。
- `t_kotlin_template_fence_parity`(`scripts/test_lumos.py:127627`)只比對 `_visible_lines`,不涵蓋 `_fence_body`,所以這份複本沒有口徑守衛。
- 範本小節的切法在測試端已有 `_kt_template_sections`(`scripts/test_lumos.py`,用 `template_sections` 加圍欄外的 `### ` 標題)。`_fence_body` 又寫了一套找 `### 壞寫法:` 小節的邏輯。
- ⚠ `_fence_body` 有用 `_fence_regions`,所以區段判定本身沒分叉。分叉的是「退寬鬆」與「圍欄內行集合」兩段,我判為 major 但幅度偏邊緣。

**Finding 2 — `_norm_colon` 跟既有的 `_norm` 重疊**

severity: minor
blocking: 否
引句:「return s.replace("：", ":")」
- `_norm`(`configs/ast-grep/kotlin-android/check.py:187`)已經是「全形括號與冒號換半形」的標準函式,`dt_evidence_parse` 等處都用它。
- 新增的 `_norm_colon` 只做其中的冒號,是它的子集。
- 該表的歸屬欄和理由欄也有全形括號的可能,走 `_norm` 比較一致。

**Finding 3 — 反引號片段的取法在新碼裡重複**

severity: minor
blocking: 否
引句:「return [s.replace("\\|", "|") for s in re.findall(r"`([^`]+)`", cell)]」
- `dt_evidence_parse`(`configs/ast-grep/kotlin-android/check.py:204`)已有同一個 idiom:`re.findall(r"`([^`]+)`", part)` 加 `\\|` 還原。
- `_snippets` 是新 helper,但沒回頭讓既有處共用。`_unreach_table` 又手寫了一次 `\\|` 還原。
- 同一個 idiom 現在有三處獨立實作。

**Finding 4 — `scan_index` 的路徑正規化寫在 `check()` 內聯**

severity: minor
blocking: 否
引句:「scan_index.setdefault((rule_id, str(Path(f) if Path(f).is_absolute() else (HERE / f).resolve())), []).append((a, b))」
- 既有的 `_sample_owner`(`configs/ast-grep/kotlin-android/check.py:1471`)已經是「ast-grep 回報的檔路徑 → 相對 HERE」的轉換點。
- 新碼在 `check()` 內聯另一套絕對化規則,而且寫在 `for` 迴圈裡,跟 `_bad_lines` 的 `str(f.resolve())` 互相對得上也是巧合。
- 這是命名與位置的不一致,結構本身沒錯。

不對齊共 4 條,其中 major 1 條
