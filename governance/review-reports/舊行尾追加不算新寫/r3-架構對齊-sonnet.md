severity: major

先講結論:上一輪那條「配對起點另寫一套分岔點算法」已確實撤掉,本版沒有新增跨層直呼。但「用到才算」又做了一套新的取得函式,跟既有的 `_NotelinesNet` 並存,這條是 major。另有三條 minor。

**1. 分層與依賴方向:無跨層直呼,上一輪的 major 已收回**
- 起點全部沿用各道檢查自己的範圍起點,材料沒有再新算一個:
  - 推送前與 CI 走 `_lens_push_base` 再接 `_nodehome_clamp_base`:`scripts/lumos:28600`、`scripts/lumos:28606`。
  - 第二層走 `_note_audit_resolve`:`scripts/lumos:29125`,說明在 `scripts/lumos:29072-29074`。
  - 這跟材料宣稱的一致,也沒有新增第三套找主線的演算法(`_push_range_start` 在 `scripts/lumos:38627`)。
- 新函式 `_notelines_append_pairs` 放在 notelines 共用層,由第一層 `_note_shape_eval` 和第二層 `_note_audit_items`(`scripts/lumos:28942`)往下呼叫。這個方向跟現況相同:`_note_audit_items` 本來就呼叫 `_notelines_new`(`scripts/lumos:28946`)。
- 它用 `_ns_diff`(`scripts/lumos:27207`)取改動區塊。`_NotelinesNet` 也這樣用(`scripts/lumos:27411`),所以不算新的跨層。
- `_notelines_parse_added` 改成包新的 `_notelines_parse_hunks`,是把現有四處呼叫端收斂成一支(`scripts/lumos:27307`、`27332`、`27358`、`27414`),沒有多養一套。

**2. 命名與錯誤處理:大方向一致,兩處有出入**

**Z2 `_gate_event_fit` 的簽名裝不下現行 `_drift_m1_fit`**
severity: minor
blocking: 否 — 結構沒錯,是共用函式的介面跟鄰居對不上。
引句:「把 `_drift_m1_fit` 拆成共用的 `_gate_event_fit(repo_root, gate, kind, note, extra, list_key)`」
- 現行 `_drift_m1_fit(root, kind, note, hard, tip, nodes, extra)` 另外收 `hard`、`tip`、`nodes`,並回傳截短後的 `nodes`(`scripts/lumos:33635-33650`)。
- 材料的簽名沒有 `hard`、`nodes`、`tip`。`_gate_event_build` 會用 `head_sha` 參數填 `commit` 欄,`nodes` 是獨立參數(`scripts/lumos:1147-1177`)。
- `then(extra)` 這個回呼只拿得到 `extra`,截不到 `nodes`,而現行流程要靠它「把 `nodes` 截到 20」。
- 兩種補法:簽名補齊並維持回傳 `nodes`,或讓 `then` 能改 `nodes`。
- 另外,整個專案沒有其他「可選 `then` 回呼」的寫法。改成明確參數(例如 `nodes=None`)會比較貼近鄰居,不然就是第二種做法。⚠ 交編排者判斷要不要接受回呼。

**Z3 失敗帳的 `state` 值域跟舊句檢查帳不同**
severity: minor
blocking: 否 — 記帳結構沒問題,值域用詞不一致。
引句:「`state: "failed"` 加 `error`(例外類別名或 `git`)——照舊句檢查帳用同一個種類加狀態欄的做法」
- 舊句檢查帳的 `state` 是 `done`、`timeout`、`git-failed`、`unreadable`、`error`(`_DRIFT_M1_UNKNOWN`,`scripts/lumos:32870`)。
- 材料用 `ok` 與 `failed`,而且 `kind` 固定為 `relaxed`;舊句檢查帳的 `kind` 會隨結果變成 `passed`、`warned`、`blocked` 或 `range-unavailable`(`scripts/lumos:33684-33692`)。
- 建議失敗值沿用既有詞 `git-failed` 與 `error`,成功值沿用 `done`。REVISIT 與 RETIRE-IF 說的「`state` 是 ok 與 failed 分開數」要一併改。
- 失敗回傳 `(配對表, 失敗原因)` 的元組沒有對齊問題:`_ns_negation_prepare` 回傳的元組最後一格也是例外類別名或 None(`scripts/lumos:28644-28650`)。

**Z4 `_note_audit_fold` 的鍵形狀改了,六個呼叫端都要跟著動**
severity: minor
blocking: 否 — 沒有第二種做法,只是回傳形狀變動的波及範圍沒盤點完。
引句:「`_note_audit_fold` 照(編號, `tail` 或沒有)分開取最重。」
- 現行回傳 `{id: class}`,有六處呼叫:`scripts/lumos:29428`、`29561`、`29601`、`29606`、`29644`、`34449`。
- 材料只列出「五個呼叫端」,而且 `29606` 是第二次呼叫 `wfold`。
- 實作時要先確認 `_note_audit_covered`(`scripts/lumos:29067`)與所有 `fold.get(it["id"])` 的取法一併改。
- 判定檔多一個可省略欄位這件事本身是對的:`_note_audit_parse_verdict` 只驗 `id` 與 `class`,多餘欄位照收(`scripts/lumos:29003-29005`)。這跟現有判定檔的擴充方式一致,沒有引入第二種擴充法。

**3. 第二種做法**

**Z1 「用到才算」另做一個取得函式,跟 `_NotelinesNet` 並存**
severity: major
blocking: 是 — 引入第二種「用到才算」的做法。
引句:「配對表用一個取得函式包起來(第一次呼叫才跑配對,整個範圍一次、之後重用)」
- 專案裡「用到才算」的既有做法是 `_NotelinesNet`:一個帶 `failed` 旗標的類別,第一次呼叫 `lines()` 才跑 diff(`scripts/lumos:27400-27415`)。
- 它的 docstring 專門寫了「為什麼用旗標不回 None」,並且是以無參數函式的形式傳進 `_notelines_rows`(`scripts/lumos:27397`)。
- 材料不重用它,理由是「它只在 `keep_other` 時建」。但「第一次呼叫才算,失敗另外回報」的形狀完全相同,只是改成閉包加元組回傳。
- 這樣就同時有「旗標類別」和「閉包加 `(表, 原因)`」兩套。後者還要另外把失敗原因傳到記帳那一端。
- 建議二選一:
  - 做成跟 `_NotelinesNet` 同形的小類別(內含 `failed` 與 `error` 欄位),`_ns_negation_collect` 與 `_ns_negation_hints` 轉傳它的方法。
  - 或在材料裡明寫為什麼這裡不能用旗標類別,並補上設計取捨。
- ⚠ 材料已經寫了不共用的理由,但沒回答「為什麼不照同樣形狀另做一個類別」,請編排者裁定是否接受。

其餘第二種做法都對得上既有慣例:
- 判定檔加可省略欄位,對得上 `scripts/lumos:29003`。
- 統一 diff 區塊解析,是收斂而不是新增。
- `_ns_diff` 加旗標,對得上現有的 `-U0 -M --no-ext-diff` 釘法(`scripts/lumos:27207`)。

**4. 落點**
- `lands_in` 的三篇大致合理:
  - 第一層與解析器歸「筆記內容閘」。
  - 送審標記與 `tail` 欄歸「筆記內容審」。
  - 共用的 4 KB 裁法拆自 `_drift_m1_fit`,歸「存量漂移守衛」。
- 小提醒:`_gate_event_fit` 拆出後是跨閘共用的記帳工具,更貼近 `_gate_event_build` 所在的治理帳那篇。`_gate_event_build` 在 `scripts/lumos:1147`,材料〈做法〉8 已把 `Systems/reversibility-governance-ledger` 列入同步。這不算不對齊。建議把 `_gate_event_fit` 的歸屬明寫在那篇,並考慮把它放進 `lands_in`。

不對齊共 4 條,其中 major 1 條
