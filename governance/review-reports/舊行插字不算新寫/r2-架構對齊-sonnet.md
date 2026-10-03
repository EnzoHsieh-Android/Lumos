severity: minor

## 三問

**① 分層與依賴方向:對齊。**
- 新函式 `_ns_old_line_match` 放在 `_note_shape_eval` 內部、每篇算一次配對表。表交給違規迴圈和否定提醒收集器,方向是由上往下,沒有跨層直呼。
- 收集器多收一個參數,沿用 `_ns_negation_collect(hints, p, text, rows)` 的收集器形狀(`scripts/lumos:27858`)。前綴提醒收集器 `_ns_tag_hints_collect`(`scripts/lumos:27921`)不動,與〈做法〉5 一致。
- 起點版本的批次讀走 `_nodehome_cat_blobs`(`scripts/lumos:26440`),不另開 git 行程。新寫的 `_note_shape_eval` 後半的喚醒路徑本來就這樣讀(`scripts/lumos:28440`)。
- 判定同一把尺用 `_ns_check_line` 與 `_ns_revisit_violations`(`scripts/lumos:28422-28427`),沒有複製規則。
- 有兩處小落差,見 R2A1、R2A3。

**② 命名與錯誤處理:大致對齊。**
- 函式名 `_ns_old_line_match` 對得上 `_ns_old_keys`、`_ns_is_old` 的 `_ns_` 家族(`scripts/lumos:28193`、`scripts/lumos:28208`)。
- 失敗時「不配對、照整行查」是放寬類功能的偏嚴做法,方向合理。它跟 `_ns_slots_old_lines` 讀不到時回 None、呼叫端 fail-open(`scripts/lumos:28271-28276`)不同,但格子是新增檢查、這裡是放寬判定,兩者理由不同,不算不一致。⚠ 計劃只說「照既有命名」,沒寫出上限常數名(每次最多比 2000 對、單行 2000 字)。實作時要對齊 `_NS_DOCTOR_SCAN_CAP` 那種 `_NS_` 大寫常數(`scripts/lumos:27109`)。
- 提醒類丟例外不能讓閘失敗,既有做法是收集器 try/except 後清空 items、記例外類別名(`scripts/lumos:27863-27867`)。計劃沒寫新配對表出錯時怎麼退。⚠ 若表算失敗,應退成整行查,並比照收集器的樣子隔離。

**③ 第二種做法:收斂大致成立,格子與 `old_by` 不併的理由站得住。有三處不夠乾淨(R2A1 到 R2A3)。**
- 格子的舊行判定(`_ns_slot_key`、`_ns_is_old`)比的是「核心一句文字鍵加連結只增不減」,只套摘要前綴(`scripts/lumos:28175-28215`)。`old_by` 是上線前寫的行的集合(`scripts/lumos:27279-27299`、`scripts/lumos:28453`)。這兩個問的是不同的事,不併成立。
- `hinted` 帳沒有另起一套。既有兩筆就是同一個寫入器 `_gate_event_or_warn`(`scripts/lumos:1234`),閘 `note-shape`、種類 `hinted`,再用 `extra.check` 區分:`negation`(`scripts/lumos:28680`)和 `tag-hints`(`scripts/lumos:27972`)。新增 `insert-only` 是同一個形狀。治理帳去重鍵也含 `check`(`scripts/lumos:7991`),所以不會被吃掉。
- 這版的新舊行判定共四套:格子、`old_by`、`ln.strip() in old`、新增的 difflib 配對。計劃只把後兩者收成一支。

## 不對齊條目

**R2A1**
severity: minor
blocking: 否 — 結構對,但「收成一支」只在名義上成立,可以在計劃裡講清楚再實作
引句:「`_note_shape_eval` 前半(新增行)與後半(新程式檔喚醒舊引用,原本的 `ln.strip() in old` 整行相等)都改呼叫它」
- 喚醒路徑今天比的是上線點版本 `gl` 的整行集合,外加 `old_by`(`scripts/lumos:28450-28453`),不是 `base_where`。〈做法〉2 把「起點版本」定義成 `base_where`。
- 喚醒路徑也沒有「O 被用掉、一對一」的概念。舊行沒改它仍在,不能被消耗。
- 所以「喚醒那一路只認整行相等」其實是呼叫端留在原地,新函式沒有真的被共用。S11 的「跟今天一樣」也只能靠這個來保證。
- 建議二選一:要嘛明寫喚醒路徑繼續用現行的集合判定、不呼叫新函式,收斂宣稱縮成「新增行一路」;要嘛新函式把「整行相等」拆成不需要消耗的獨立分支,並寫明喚醒路徑傳的是 `gl` 版本,不是 `base_where`。
- 佐證:`scripts/lumos:28450-28453`

**R2A2**
severity: minor
blocking: 否 — 記帳形狀對齊,但下游消費者可能把新一筆算進去
引句:「記一筆治理帳(閘 `note-shape`,種類 `hinted`」
- `hinted` 帳是既有慣例,多一種 `check` 值不算另起一套。
- ⚠ 筆記格子的「度量」語法接受 `<閘>.hinted` 這類條件(`_SLOT_METRIC_KINDS`、`_SLOT_METRIC_RE`)。我沒追到實際計數端是否按 `check` 過濾,所以不確定。
- 如果計數端不按 `check` 過濾,新增的 `insert-only` 會被算進任何對 `note-shape.hinted` 下的度量。
- 計劃〈做法〉7 只列了兩篇計劃的量測口徑同步,沒查這條。
- 建議實作前先確認計數端有沒有按 `check` 過濾,再把結果寫進計劃。
- 另外,既有兩筆 `extra` 只帶整數或規則名清單,新一筆多帶「各規則名條數」。形狀不同但沒有破壞性。
- 佐證:`scripts/lumos:3759`、`scripts/lumos:28680`

**R2A3**
severity: minor
blocking: 否 — 取「O 被用掉」的做法與格子取舊行的做法並存,屬可接受的重疊
引句:「O 這段文字在終點版本整篇出現的次數比起點版本少(原行真的被改掉了)」
- 格子那一路取「被改掉的舊行」,用 `git diff -U0` 的刪除行(`_ns_deleted_summary_lines`)加起點版本摘要行(`_ns_base_summary_lines`)。新設計改成整篇文字數出現次數。
- 取法不同有它的理由:刪除行那支只收像摘要前綴的行,正文行拿不到,所以不是第二套重複實作。
- 但同一次 `_note_shape_eval` 可能對同一批起點版本的筆記批次讀兩次,一次給格子、一次給配對。
- 建議實作時讓配對表和格子共用同一次讀取結果(照 `slots` 容器那樣掛在同一個 sink 上),不要各讀各的。
- 佐證:`scripts/lumos:28240`、`scripts/lumos:28292`

不對齊共 3 條,其中 major 0 條
