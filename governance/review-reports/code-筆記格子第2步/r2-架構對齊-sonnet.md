severity: minor

整體判斷:這份修正差異沒有引入第二套預算、第二套開關讀法或跨層直呼,結構對齊舊句檢查 m1 那一支。我只找到 3 條小處不一致。

## ① 分層與依賴方向

對齊,沒有 major。

- **預算**:`_drift_retire_guarded` 自己一個截止時間,寫法同 m1,只差常數(20 秒對 30 秒)。
  - 對照:`scripts/lumos:32413`、`scripts/lumos:31538`、`scripts/lumos:31430`。
  - 常數也跟 m1 一樣放在自己那一段旁邊。
- **開關讀取**:`cmd_drift_check` 改成直接用 `_drift_config_text_parts` 解析一次,各開關從同一份結果拿。這和 doctor 讀 `parts` 是同一條路,沒有新建讀法。
  - 對照:`scripts/lumos:31299`、`scripts/lumos:32598`。
  - `_drift_config` 保留四元組,測試呼叫它的地方不受影響(`scripts/test_lumos.py:52124`、`scripts/test_lumos.py:53514`)。
- **治理帳**:走 `_gate_event_or_warn`,參數 `head_sha` 和 `extra` 的用法同 m1 的 `_drift_m1_ledger`(`scripts/lumos:32383`,同一檔 `scripts/lumos:32405` 以下)。
- **doctor**:`_drift_retire_doctor_lines(parts)` 的位置與簽章同 `_drift_old_sentence_doctor_lines(parts)`(`scripts/lumos:32613` 附近)。

**R2A1**
severity: minor
blocking: 否 — 帳照記、判定不受影響,只是少了 m1 帳那層保護
引句:「extra={"check": "retire", "must": len(must), "unknown": len(unknown), "base_sha": base})」
- 治理帳少了 m1 兩層做法:
  - m1 在落帳前先用 `_drift_m1_fit` 把節點、欄位裁到帳放得下。
  - m1 在 `_gate_event_or_warn` 回 `False` 時另走 `_drift_m1_ledger_miss`。
  - 撤除條件這支兩層都沒有,只做 `sorted(...)[:50]` 截斷。
- 欄位名也不同:m1 記 `handle` 和 `listed`,這裡記 `must` 和 `unknown`。語意相近,但同一個閘的兩支記帳,欄位詞是兩套。
- 對照 `scripts/lumos:32383`、`scripts/lumos:32405`、`scripts/lumos:32352`。

## ② 命名與錯誤處理

**R2A2**
severity: minor
blocking: 否 — 屬刻意取捨(判不了只列出不擋),但和 m1 兜底的做法分叉
引句:「print(f"存量漂移檢查:RULE 撤除條件這次沒跑完({type(ex).__name__}),不擋", file=sys.stderr)」
- m1 的例外兜底有兩步:先把例外轉成 `error` 狀態,走 `_drift_m1_report` 照常記帳;block 模式再照判不了的規矩擋(回 1)。
- 撤除條件這支只印一行,回 0,也不記帳。
- 提醒字樣也不同:m1 是「舊句檢查:工具內部出錯(…),這次沒判,帳也沒記」,這裡是「這次沒跑完…不擋」。
- 帳少一筆的缺口沒有被標出來。⚠ 若計劃已明講要這樣,可降為 clean。
- 對照 `scripts/lumos:32409` 到 `scripts/lumos:32421`。

壞值提醒、總開關與子開關的讀法已對齊,不必處理。
- 三句提醒的結構都同 `_drift_old_sentence_config`:設定檔讀不成 JSON、`drift_check` 不是物件、值看不懂各講一句。
- 對照 `scripts/lumos:31334` 到 `scripts/lumos:31348`。
- 預設改成「照總開關」,這是刻意的不同,不算不一致。
- doctor 字樣「沒讀懂(…)」同舊句檢查「設定沒讀懂(…)」。
- 「不改就留著並表態」固定段同 `_drift_report_must`(`scripts/lumos:31505` 以下)。這裡只有單一種類,所以直接寫死 `--kind retire`,和那邊的做法等價。

## ③ 第二種做法

沒有 major。

- **預算配法**:只有一套,「自己的截止時間」,舊的「吃核心剩下的」已拿掉。
- **開關讀法**:只有一套,`parts`。
- **印法**:仍走 `_drift_print_findings` 和 `_drift_print_hints`。

**R2A3**
severity: minor
blocking: 否 — 只是測試寫法,不影響行為
引句:「rt = [e for e in evs if e.get("check") == "retire"]」
- 新測試⑤自己內聯解析治理帳 JSONL。既有的 `_m1_events` 把檢查名寫死成 `old-sentence`,所以沒法直接重用,但這等於複製了一份讀帳邏輯。
- 測試①表態是用 `subprocess` 加 `cwd` 直接呼叫,沒有走 `_dr` 加 `--repo` 的慣用法。⚠ 我沒有全檔確認其他 ack 測試怎麼寫,這點判不準。
- 對照 `scripts/test_lumos.py:58373`、`scripts/test_lumos.py:51815`。

不對齊共 3 條,其中 major 0 條
