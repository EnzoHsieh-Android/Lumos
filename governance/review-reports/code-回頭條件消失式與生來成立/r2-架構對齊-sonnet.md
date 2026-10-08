severity: minor

# 架構對齊審查 第 2 輪(回頭條件 when-gone 修正段)

## 三問

1. 分層與依賴方向:沒有跨層直呼。`_DriftProbeTree._read_raw` 改走 `_nodehome_cat_blobs_capped`(同層批次讀取層,鄰居 `scripts/lumos:23838`、`scripts/lumos:42666` 也是這樣用),`is_dir` 放在樹物件上、`_drift_probe_row_problems` 與 `present` 共用,方向正確。`_drift_probe_judge` 仍不認得 `gone`。
2. 命名與錯誤處理:兩處不一致(Z1、Z2),結構都對。
3. 第二種做法:`_read_raw` 把 `_drift_cat` 的「內容編號優先、退回版本:路徑」邏輯在行內又寫了一份(Z3),是唯一的第二份寫法,但範圍只有一行表達式,判 minor。

## 發現

**Z1 `_probe_gone_backtick_err` 一支函式吃兩種形狀的輸入,靠 startswith 分流**
severity: minor
blocking: 否 — 兩個呼叫端都對得上,但分流條件是隱含約定,結構沒錯
引句:「if s.startswith("when-gone:"):          # 撤除條件的值(格子解析出來的,不帶方括號)」

1. 輸入:`_slot_retire_err` 傳的是已去掉 `retire:` 的值(`scripts/lumos:3885`,以 `when-gone:` 開頭、不帶方括號);`_ns_revisit_cond_viol` 傳的是整行原文(`scripts/lumos:27988`)。
2. 走到:同一支函式內用 `startswith("when-gone:")` 決定走哪個分支,原文那條用 `\[(?:retire:)?when-gone:` 找標記。
3. 壞在:鄰居(`_probe_value_err`、`_probe_named_err`)都是「一支函式一種輸入」。這裡原文那條分支的 `(?:retire:)?` 在 REVISIT 行路徑上其實不會用到(RULE 撤除條件走另一個呼叫端),屬於為了合併而留的死分支。與既有慣例不一致,但沒有已知失敗輸入,所以只是 minor。⚠ 若日後有人在 REVISIT 行最前面直接寫 when-gone: 開頭的文字(目前行首必為 REVISIT:/RULE:,走不到),分流會誤判。

**Z2 帶字串 when-gone 讀不出的原因訊息,git 模式與工作目錄模式用語不同,且與計劃寫的原因清單不符**
severity: minor
blocking: 否 — 只影響點名文字,判定結果一致
引句:「return None, f"讀不出或超過 {_DRIFT_GONE_MAX_BYTES // 1048576} MB"」

1. 輸入:git 模式下帶字串的 when-gone 指到超過 2 MB 的檔。
2. 走到:`_nodehome_cat_blobs_capped` 對超過上限的檔回 None(與「讀不出」無法區分),`_drift_gone_text(None)` 於是印「讀不出或超過 2 MB」;工作目錄模式因為保留了 `_DRIFT_RAW_TOO_BIG`,印的是「超過 2 MB」。
3. 壞在:同一個條件在兩個模式講的原因不同;計劃〈做法〉3「判不了要講對原因」明列「超過上限、讀不出」是兩個不同原因,這次修正把 git 模式併成一個。`_DRIFT_RAW_TOO_BIG` 的哨兵現在只剩工作目錄模式在用,是半截的設計。測試⑤、③各自只斷言了 "讀不出"/"MB" 子字串,蓋不到這個差異。file: `scripts/lumos:32486`(`_DRIFT_GONE_MAX_BYTES` 區塊與哨兵定義)。

**Z3 `_read_raw` 內聯了一份 `_drift_cat` 的編號查找邏輯,沒有給 `_drift_cat` 加上限參數**
severity: minor
blocking: 否 — 重複的只有一行表達式,行為與 `_drift_cat` 一致,但那段的理由寫在 `_drift_cat` 的 docstring 裡,現在有兩處要同步
引句:「blobs = _nodehome_cat_blobs_capped(self.root, [oids.get(p) or f"{self.where}:{p}" for p in todo],」

1. 輸入:任何 git 模式下帶字串的 when-gone 讀檔。
2. 走到:`_read_raw` 自己呼叫 `_drift_oids` 再組 `oids.get(p) or f"{where}:{p}"`,與 `_drift_cat` 完全同一句,只差把 `_nodehome_cat_blobs` 換成 `_nodehome_cat_blobs_capped`。file: `scripts/lumos:32235`(`_drift_cat` 本體與 docstring 說明為何必須用編號:NFC/NFD、相容表意字、路徑含換行)。
3. 壞在:NFD 檔名那類修正以後若改 `_drift_cat`,`_read_raw` 這份不會跟著改。照既有做法(上限放在批次讀取層、不另起查法)應讓 `_drift_cat` 多一個可選的 `max_bytes` 參數,或抽一支共用的「組讀取規格」函式。未達 major 是因為兩份目前逐字相同、且測試③守了大檔行為。

## 沒問題的項目

- `_drift_cond_split(v, k)` 鍵參數改必填:全部 9 個呼叫點(`scripts/lumos:31942`、`31952`、`31982`、`32349`、`32351`、`32395`、`32433`、`32434`、`32472`、`32581`、`32583`、`32648`)都帶鍵,沒有遺漏的舊式單參數呼叫。
- `is_dir` 共用:`present` 與 when-file 資料夾提示都走它;尾斜線差異不會出事,因為 `_probe_check_value("gone","src/")` 已正規化成 `src`(實跑回 `('src', None)`),`_drift_probe_cond_candidate` 的前綴比對不受影響。
- `_probe_gone_err` 的方括號檢查放在 `_probe_check_value` 內部步驟,REVISIT 與 RULE 撤除條件兩條路共用同一支,符合計劃「兩條路要求一致」。
- 工作目錄模式 `_read_raw` 每支檔看預算,與 `_read`(`scripts/lumos:32323` 附近)的寫法一致。
- 推送判定的候選篩選與點名提示的分層未變(判定函式不認得 gone)。

## 固定席節點

- bound-tests-gate、guard-kill 等節點的合約綁定測試與本次改動無直接衝突;本輪未動 `_reinject_all` 與紀律範本邏輯,diff 內只有計劃筆記文字更新。

最高 severity:minor
