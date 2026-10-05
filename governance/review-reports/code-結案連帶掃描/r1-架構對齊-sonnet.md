severity: minor

## 問1 分層與依賴方向
大致對齊。偵測(_drift_c6)接在 _drift_state_findings 內、與 _drift_c2 同位置(lumos:32140-32151、32169);修法 _drift_fix_c6 登記進 _DRIFT_FIX_COMPUTE / _DRIFT_FIX_ALLOWED / _DRIFT_FIX_KIND_ARGS / _DRIFT_FIX_SELF_JUDGED 四張註冊表(lumos:35031),與 c1..c5、count 同做法;收尾列出 _drift_print_backrefs 由 main 與 cmd_drift_fix 呼叫,方向與 _drift_print_followups(lumos:32356)相同,沒有跨層直呼。唯一差別是落點:_decision_backrefs 與 _closing_revisits 放法見 F1、F2。
引句:「_DRIFT_FIX_ALLOWED = {"c1": {"date"}, "c2": {"close", "keep", "status", "reason", "decision", "keep_revisits"},」

## 問2 命名與錯誤處理
命名沿用 _drift_ 前綴、c6 / settled 與鄰居一致;錯誤訊息語氣(「擋下」「手動改」「不寫檔」)與 _drift_fix_c2/_drift_fix_count 一致。差別在例外處理:同一個列出函式,三個呼叫處的 fail-open 寫法不一致(見 F1)。
引句:「print(f"(列出連到這篇還寫待定的句子失敗,決策照樣記下了:{e})", file=sys.stderr)」

## 問3 第二種做法
沒有自創工具函式:_visible_lines、_drift_fm_end、_revisit_lines、_drift_one_line、_drift_placeholder_err、_drift_fix_by 都沿用。引入的第二種做法只有「已收尾」狀態集合多了一份(見 F3)與 gate 回傳形狀(見 F4),皆屬 minor。
引句:「_DRIFT_SETTLED = ("done", "resolved", "wontfix", "superseded")」

## F1 列出函式的 fail-open 只包在 decision 兩處
severity: minor
blocking: 否
引句:「_drift_print_backrefs(env.vault, rel)」
佐證:scripts/lumos:47035(set 路徑,裸呼叫,外層 try 只接 ValueError/RuntimeError 並印「擋下」回 2)、scripts/lumos:35199(cmd_drift_fix 裸呼叫)、scripts/lumos:32276-32282(_decision_backrefs 才包 try 並印 stderr);對照既有 cascade fail-open 寫法 scripts/lumos:47155。
說明:同一支只印不擋的列出,decision 路徑 fail-open(寫入已完成、rc 不變),set 與 drift fix 路徑沒包——Env(vault) 重建若丟 ValueError/RuntimeError,set 會在狀態已寫入後印「擋下」回 2,與「只列出、不擋、不改回傳碼」的自述不合。既有 _closing_revisits 也是把讀檔失敗靜默 return。建議把 try 收進 _drift_print_backrefs 本體,三處一致。另 cascade 既有寫法吞 Exception、這裡吞窄例外並換了訊息格式(無 CASCADE-ERROR 式前綴),語氣也不同。

## F2 _issue_close_revisits 改名成 _closing_revisits 並擴大職責
severity: minor
blocking: 否
引句:「def _closing_revisits(env, rel, new_status):」
佐證:scripts/lumos:32626(同層 _drift_print_followups 在 32356 是單一職責「列連帶待辦」;作廢標記與待定決策行也塞進同一支)
說明:同一函式現在處理 Issue 結案、任何筆記作廢、待定決策行三種列出,鄰居是一事一函式(followups / revisits 各自獨立)。結構仍在同層、方向未變,故只算 minor。

## F3 另開第三組「已收尾」狀態常數
severity: minor
blocking: 否
引句:「_DRIFT_SETTLED = ("done", "resolved", "wontfix", "superseded")」
佐證:scripts/lumos:32015 對照 scripts/lumos:32011(_DRIFT_CLOSED)、scripts/lumos:16805(_ISSUE_CLOSED_STATUSES)
說明:原本已有 _DRIFT_CLOSED(計劃)與 _ISSUE_CLOSED_STATUSES(Issue)兩組,這次新增不分類型的第三組,main 的 set 路徑(47033)與 c6 偵測用它、c2 仍用舊組。註解有交代理由,屬刻意,但漂移家族內「已收尾」現有三種定義,日後改狀態列舉要改三處。

## F4 _drift_close_gates 回三元組,鄰居回二元組
severity: minor
blocking: 否
引句:「def _drift_close_gates(cx):」
佐證:scripts/lumos:34700(回 (lines, live, err));對照 _drift_fix_c2/_c3/_c5/_count 的 (res, err) 形狀 scripts/lumos:34749、34800、34962、35031 附近
說明:各種類的計算函式與其輔助函式一律 (結果, 錯誤) 二元組;這支多帶一個 live,呼叫端 _drift_fix_c2 還要回頭用 _revisit_lines 再算一次(34746)。結構在同層,風格小異。

不對齊共 4 條,其中重大 0 條
