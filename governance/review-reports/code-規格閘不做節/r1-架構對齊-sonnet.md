severity: major

**架構對齊審查(規格閘不做節 r1)**

severity: major
blocking: 是 — 計劃自己寫明要借 `_h2_section_lines`、不另寫找節邏輯,實作卻另寫了一套認標題與找節範圍的迴圈,同一件事有了第二種做法。
引句:「if not (ln.startswith("#") and _NOGO_H2_RE.match(ln.strip())):」
對照:file: `scripts/lumos:7825`(`_h2_section_lines`,說明寫「找節邏輯不准長出第三套」,回退節 `scripts/lumos:7844` 與實務隱患節 `scripts/lumos:7953` 都走它)
判定理由:`_nogo_skip_lines` 自己用 `_visible_lines` 逐行掃,再用 `startswith("#")` 加標題正則認標題,又自己決定節從哪裡開始。這跟 `_h2_section_lines` 的標題判斷(`ln.startswith("#")` 加 `h2_re.match(ln.strip())`)是同一套邏輯。
- 該呼叫 `_h2_section_lines(text, _NOGO_H2_RE)`,從它回傳的行裡取開頭連續的清單段。
- 現在這份實作有三個行為跟既有找節函式不同:
  - 節的終點:既有函式讀到下一個 `## ` 或 `# ` 才停;新函式靠「行號不連續」或「非清單行」停。
  - 重複標題:既有函式把多個同名節合併;新函式每個標題各算一次。
  - 行號斷開:新函式用 `no2 != prev + 1` 偵測圍欄,是另一種做法。
- 計劃〈PRIOR-ART〉寫「借這兩樣,不另寫找節邏輯」,實作與此不符。
- 補充:`_NOGO_ITEM_RE` 是專案裡第四種清單項目判斷,但各處需求不同(例如 `scripts/lumos:37787`、`scripts/lumos:32655`、`scripts/lumos:7913`),這點只算 minor,不另列。

severity: minor
blocking: 否 — 沒有跨層直呼或雙重寫法,是第一次出現的新模式,而且有退回路徑。
引句:「nogo_src = inspect.getsource(_nogo_skip_lines)」
對照:file: `scripts/lumos:8045`(`_door_rule_fingerprint` 既有部分只收正則 `.pattern`、`PITFALL_CLASSES` 的 JSON 與中文名表),全檔沒有其他 `inspect.getsource` 或 `co_code` 的用法。
判定理由:
- 這是專案第一次把函式原始碼放進規則指紋,之前的做法都是把函式的輸入常數(正則、表)放進去。
- 如果 `_nogo_skip_lines` 照上一條改成呼叫 `_h2_section_lines`,「只收輸入常數」就夠用,可以不需要這個新機制。
- 退回路徑改用位元組碼,位元組碼會隨 Python 版本改變。同一份指紋在不同 Python 小版本上算出不同值,對照釘住的測試(`t_door_rule_version_pin`)可能出現假紅。這是風險,不是對不上現有寫法。

留痕新欄位(`nogo_skipped_n`、`nogo_skipped`、`inputs_sha`)的審查結果,已審,不列為問題:
- 這三個欄位只是加在既有 `rec` 字典上,沿用 `door_rule`、`clause_sha` 的做法。
- 讀端用 `.get` 或條件式讀取,舊留痕不受影響。

doctor 段落的審查結果,已審,不列為問題:
- 前 30 份改成先篩 `door_rule` 版本再排序,仍在原有的 `_two` 與 `_first30` 流程裡,沒有新增平行路徑。

不對齊 2 條,major 1 條(第一條,`_nogo_skip_lines` 另寫找節邏輯)。
