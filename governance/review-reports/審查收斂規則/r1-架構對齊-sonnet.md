severity: major

## 發現

severity: major
blocking: 是 — 殘留戳記把子欄位塞進 `[audit:]` 的值裡,是行內標記的第二種寫法,而且這支檔以前因為同類問題被改過
引句:「寫成 `[audit:模型/日期 殘留:<節點>#<決策 id>]`」
對照:`/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos: 3911-3912`(「一欄位一個正則…(2026-09-21 架構對齊席:原本寫成一條合併正則+dict,是這支檔裡的第二種做法)」)。同見 `5485`(`AUDIT_REF_RE`)、`5496`(`KILL_REF_RE`)、`5948-5949`(`ROLLBACK_REF_RE` / `GUARD_REF_RE`)。
判定理由:
- 既有慣例是一個方括號只放一個欄位,例如 `[test:]`、`[audit:]`、`[kill:recipes]`、`[rollback:]`、`[guard:]`,以及 `[since:]` 這一族,每個欄位各自一個正則。
- 材料把 `殘留:` 當成 `[audit:]` 值裡的次欄位,以空白分隔。這要求所有 `[audit:]` 讀者自己再切一次字串,現在沒有這種做法。
- 受影響的讀者有四處:
  - `invariant_audit_refs`(`5936`)。
  - `_cmd_guard_audit_locked` 的寫後自驗:`stamp in invariant_audit_refs(...)`(`18760`),帶殘留的整串戳記會讓比對對不上。
  - `guard list` 的 `[audit:…]` 顯示(`15828`)。
  - 重審時 `AUDIT_REF_RE.search` 整串覆蓋(`18746-18750`)。
- 材料自己的回退段也承認舊工具重審會整串覆蓋、殘留標示跟著消失,這就是塞進同一個值的代價。
- 對齊的做法是獨立標記,例如 `[residual:節點#d12]`,各用一個正則。`[audit:模型/日期]` 的解析因此不動,S4 的相容性自然成立,舊工具重審也不會抹掉殘留標記。

severity: minor
blocking: 否 — 只是漏寫放哪裡,不是第二種做法
引句:「doctor 檢查戳記裡的節點存在、那筆決策存在、沒有被標成 `valid: false`」
對照:`/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos: 2088`(Check T)、`6722`(單檔 lint 版同一條判斷)、`2838-2850`(Check E3,`節點#dN` 的決策指標檢查)。
判定理由:
- 材料沒說這個檢查放在哪一段。
- `[audit:]` 的檢查已經分在 doctor Check T 和單檔 lint 兩處。
- 「節點#dN 指向的決策是否存在、`valid:false`」這套邏輯 Check E3 已經有(含 dangling 與「缺 `valid` 視為有效」的讀法)。
- 應該寫明:放進 Check T,並抽共用函式給單檔 lint 版;決策指標的解析與判斷重用 E3 的讀法,不另寫一套。
- 材料用的 `Projects/a_計劃#d12` 格式與既有 `decision_refs` 的 `<節點rel>#dN` 一致,這點是對齊的。

severity: minor
blocking: 否 — 屬子命令家族的輸出慣例,沒有跨層
引句:「`lumos loop sec-delta <迴圈編號> --spec <這一輪的凍結 patch>`」
對照:`/Users/enzo/orca/workspaces/lumos-toolchain/review-converge/scripts/lumos: 52646-52653`(`fix-check` 有 `--repo`、`--json`;`next` 有 `--json`、`--repo`)、`53801-53806`(分派寫法)、`26018`(`_disposal_security_step` 只回 `fail` / `ok` / `skip`,自己印輸出)。
判定理由:
- 方向對:唯讀、不改處置閘、比對函式共用,這與 `loop next` 的「唯讀指針」同類。
- 但有三處沒對齊,材料也沒交代:
  - 沒有 `--json`,同家族的 `fix-check` 與 `next` 都有。
  - 沒有 `--repo`。`next` 與 `fix-check` 都有,`prov_path` 的解析也要它。
  - 位置參數的 `dest` 前綴(`fc_`、`next_` 一類)沒提。
- 抽出共用函式也沒說清楚。`_disposal_security_step` 目前是「讀帳、算 seen / unseen / changed、直接印出」一氣呵成。
- 要抽的是中間「算 unseen / changed」那段,回傳資料(unseen 和 changed 兩個清單),印字留給呼叫端。這樣 `sec-delta` 和處置閘才是同一支比對。
- 另外,有多個 required-gated 席(slots)時,清單怎麼算也沒定。

## 總結
不對齊共 3 條,其中 major 1 條(殘留戳記語法);另兩條是 doctor 檢查放哪段沒寫明、`loop sec-delta` 少了家族慣用的 `--json` 與 `--repo`。

<br>

以下是 `guard audit --residual` 的旗標補充,沒有獨立成條。`--residual` 本身與 `guard audit` 的 `--model`、`--date` 同風格,沒有跨層問題。問題只在上面第一條的寫入形狀,不在旗標本身。
