severity: minor

整體結構對得上既有做法:沒有第二套表態比對、沒有第二套記帳、沒有跨層直呼。有兩處和 m1 記帳的細節不一致,都是 minor。

## ① 分層與依賴方向
- `_drift_ack_text` 放在 `cmd_drift_ack` 正上方,呼叫的 `_ns_summary_logical` 和 `_retire_lines` 用的是同一支。寫入端(ack)和判定端(`_retire_lines`)取原文走同一個來源,依賴方向沒變。對照 `scripts/lumos:30341`,比對鍵仍是 `_drift_ack_key(path, text, kind)`,沒有為 retire 另開比對函式。
- 非 retire 的種類仍記 `lines[line - 1].strip()`,所以 c1 到 c5 和 m1 的鍵不受影響。
- `_drift_retire_ledger` 只包 `_gate_event_or_warn`,沒有直接寫檔,層級和 `_drift_m1_ledger`(`scripts/lumos:32405`)一致。
- 測試端 `_rt_ack` 用 subprocess 跑 GRAPHCTL,和原本 `t_slots_retire_followups` 的寫法一樣。`_rt_events` 建在既有的 `_ns_gov`(`scripts/test_lumos.py:49790`)上,沒有另讀檔。
- 這一問沒有不對齊。

## ② 命名與錯誤處理
- 欄位詞 `handle`、`listed`、`check: "retire"`、`base_sha` 非字串記空字串,都照 m1(`scripts/lumos:32405`)。
- 「放行不寫帳」對得上 `_drift_report_must`(`scripts/lumos:31527`)只在有事時才記的規矩,也已寫進 Issue 筆記。
- 有兩處和 m1 不一致:

**R3A1**
severity: minor
blocking: 否 — 只影響寫帳失敗時的事後追查,不改判定
引句:「_gate_event_or_warn(root, "drift-check", kind, note, hard=hard, head_sha=tip, nodes=nodes,」
- m1 記帳寫不進去時會呼叫 `_drift_m1_ledger_miss` 留痕(`scripts/lumos:32428`),節點清單也先過 `_drift_m1_fit` 壓進 4 KB。
- retire 的 `_drift_retire_ledger` 兩樣都沒有,節點上限也從 50 改成 20。
- 兩者都走同一支通用寫入器,所以不算第二種記帳。這是「同一層的帳,有的有兜底、有的沒有」。
- 佐證:`scripts/lumos:32405`、`scripts/lumos:32428`。
- ⚠ 筆記說 retire 一次推送最多一筆、節點上限 20,可能是刻意取捨。但 Issue 裡只提 m1 的 `ledger-miss`,沒說 retire 為何不留痕。

**R3A2**
severity: minor
blocking: 否 — 只是欄位值語意不同,讀帳時要分兩套口徑
引句:「{"handle": 0, "listed": 0, "error": type(ex).__name__})」
- 例外兜底這筆帳把「沒判完」記成 `handle: 0`、`listed: 0`。
- m1 在判不了的狀態下,`handle` 和 `listed` 記 `None`(`judged` 為假時),用來和「判完、零筆」區分(`scripts/lumos:32415`、`scripts/lumos:32423`)。
- 讀帳的人看到 `0` 會把它當成判完且沒事。
- 佐證:`scripts/lumos:32423`。

## ③ 第二種做法
- 表態原文:只有一套。retire 改記接回續行的整條,判定端(`_retire_lines`)和寫入端(`_drift_ack_text`)共用 `_ns_summary_logical`,比對仍走 `_drift_split_acked`。
- 記帳:retire 沿用 `_gate_event_or_warn`,並用 `check` 欄區分,和 m1 同一套,沒有新的寫入器。
- 測試工具:`_rt_ack`、`_rt_line`、`_rt_events`、`_rt_inproc` 是這組測試專用的小工具,沒有和既有 `_dr_repo`、`_dr` 重複。
- `_rt_inproc` 把「暫換模組常數再跑 `cmd_drift_check`」收成一支。同檔的 `t_slots_retire_when_push` 仍手寫同樣的樣板(`scripts/test_lumos.py:31035` 附近)。這不算第二種做法,只是新舊並存。
- `_rt_events` 沒照 `_m1_events`(`scripts/test_lumos.py:58409`)自己讀帳,而是用 `_ns_gov`,這點反而更接近通用做法。
- 這一問沒有不對齊。

不對齊共 2 條,其中 major 0 條
