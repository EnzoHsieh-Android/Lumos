severity: minor

## 問1 分層與依賴方向
新純函式 `_drift_ack_live` 放在 `_drift_split_acked` 旁、`status_of` 以回呼傳入,跟鄰居「純函式 + 呼叫端給資料」同形;推送路徑惰性建圖譜物件,對照 `scripts/lumos:35661` 的 retire 路徑本來就在 `_drift_retire_guarded` 內自己建 `_drift_tree_env`,同形,沒有跨層直呼。
引句:「`status_of` 用呼叫端手上的圖譜物件:`env.notes` 取 NFC 路徑(去掉圖譜資料夾前綴)的筆記」
唯一差異見 F1(today 參數語意)。

## 問2 命名與錯誤處理
`_DRIFT_EXPIRING_KINDS` 照 `_DRIFT_BOUND_KINDS`(`scripts/lumos:32259`)命名;「壞欄位當失效、不丟例外」對照 `_drift_related_ok`(`scripts/lumos:34445` 一帶)與 `_drift_seq_ok` 同做法。有兩處命名/形狀小差異,見 F1、F2。
引句:「命名照 `_DRIFT_BOUND_KINDS`」

## 問3 第二種做法
狀態集合:用 `_DRIFT_OPEN_ISSUE`(`scripts/lumos:32231`)與 `_STATUS_ENUM["project"]`(`scripts/lumos:16850`)扣 `_DRIFT_CLOSED`,沒另造。讀筆記狀態:用 `_drift_str`(`scripts/lumos:32269`)與 tenv,沒另讀檔。取日期:表態檔寫入沿用 `datetime.date.today().isoformat()`(`scripts/lumos:34554` 一帶 cmd_drift_ack),scan 傳 today,沒另造來源。印舊表態:沿用 `_drift_prev_ack_line`(`scripts/lumos:34451`)並以 `dead` 分支擴充。沒有 major。只有 F1、F2 兩個 minor。
引句:「「開著」不另寫狀態表:Issue 用 `_DRIFT_OPEN_ISSUE`,計劃用 `_STATUS_ENUM["project"] - set(_DRIFT_CLOSED)`。」

## 問4 落點
lands_in 寫 Systems/存量漂移守衛,與所有 `_drift_*` 函式同一個家,正確;skill 兩處同步也列了。
引句:「寫回 [[Systems/存量漂移守衛]]:照留失效規則、兩個新欄位、推送不看日期的理由。」

## F1 today=None 在本函式當成「推送模式開關」,跟鄰居「None 就取今天」相反
severity: minor
blocking: 否
引句:「不傳 `today`(推送檢查):kind 在 `_DRIFT_EXPIRING_KINDS` 的照留不看期限」
對照 `scripts/lumos:4104`:`today = today or _dt.date.today()`,慣例是不傳就取今天。本案同一個參數名反過來:不傳=不看日期。結構可行,但同名參數語意跟專案慣例相反,日後有人照慣例補 `today or` 會悄悄把推送檢查變成看日期。建議改成明確旗標(例如 `expire=False`)或把 today 設必傳、推送傳 None 並在文件寫明。另:參數名 `status_of` 蓋住全域 `status_of(env, rel)`(`scripts/lumos:769`),建議改名 `note_state`。

## F2 prev_ack 的選「最後一筆」另寫規則,沒沿用 `_drift_bound_latest`
severity: minor
blocking: 否
引句:「(取 seq 或檔內順序最後一筆)」
對照 `scripts/lumos:34437` `_drift_bound_latest` 以 seq 最大、同號全算選最新;本案 probe/retire 沒有 seq(沒有 `_drift_seq_ok` 把關),因此另訂「seq 或檔內順序」。結構對、規則是小分叉;建議明寫:probe/retire 不記 seq 一律取檔內順序最後一筆,不要「或」,免得同鍵有 seq 與無 seq 混在一起時選法不定。

不對齊共 2 條,其中 major 0 條
