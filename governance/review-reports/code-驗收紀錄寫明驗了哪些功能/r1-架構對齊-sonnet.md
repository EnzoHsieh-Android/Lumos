severity: minor

## 問 1:分層與依賴方向

結構對。新 helper(`_verification_status`、`_typed_link_target`、`_system_ref_item`、`_verification_system_targets`)放在 `status_of` 與 `TYPED_EDGE_FIELDS` 之間的模組層,依賴方向是 doctor / sync-verified-by / `_suggest_systems_for_orphan` 往下呼叫 helper,沒有反向、沒有跨層直呼。`build_typed_index` 改呼 `_typed_link_target` 是把同一套規則抽出來共用,不是新增第二套。對照:`status_of` `scripts/lumos:732`、`_suggest_systems_for_orphan` `scripts/lumos:875`、`_is_forgotten` `scripts/lumos:4277`(模組層小判斷函式的先例)。
唯一的分層小問題:狀態正規化在 repo 裡已有第三種寫法(見 F1)。

## 問 2:命名與錯誤處理

- 命名:`_` 前綴私有、常數全大寫(`_VERIF_INACTIVE`),跟鄰居一致(`_SET_COND_SLOTS`、`_esc_clean`)。run_doctor 內的局部變數 `_vt/_dec/_got/_bad` 帶底線前綴,鄰居有 `_shown`、`_soft`、`_verbose`(`scripts/lumos:1460` 一帶),可接受。
- 錯誤處理:`_typed_link_target` 回 `(種類, 附帶)` 元組、不丟例外,跟 `build_typed_index` 原本把壞項分進 ghosts/ambiguous/scalars 的「不丟例外、分流記帳」一致。壞項報法跟 4/4 對 plan_refs 斷鏈「自己報在該段」同一路數。
- 不一致處:見 F1、F2。

## 問 3:第二種做法

- doctor 段裡直接調 `issues` 計數:鄰居有先例(1/4 孤兒段 `issues += len(orphans)`,`scripts/lumos:1508`),所以「直接動 issues」本身不算新寫法。但本批在 `warn(...)` 之後再 `issues += len(sr_bad) - len(_shown)` 去補差額,是「先手動截斷、再補計數」的新手法(見 F2)。
- 狀態讀法:見 F1。
- 函式放的位置:合理。`_suggest_systems_for_orphan` 在 1/4 段又呼叫一次 `_verification_system_targets`(`scripts/lumos:1498` 起)做「全寫壞」判斷,判斷散在 helper 與 doctor 段兩處,見 F3。

## F1 新增 `_verification_status` 成為第三種「讀 status 並正規化」的寫法
severity: minor
blocking: 否
引句:「return status_of(env, rel).strip().lower()」
佐證行 file: `scripts/lumos:4277`(`_is_forgotten` 自己用 `str(n.fields.get("status") or "").strip().lower()`)、`scripts/lumos:732`(`status_of` 不 strip/lower)、`scripts/lumos:16506`(同一批 Verification 的 stale 判斷仍用 `status_of(...) == "stale"` 原樣比)。
1. 既有做法:`status_of` 原樣取值;要不分大小寫的地方各自內聯 `.strip().lower()`。本批新增專屬 helper,只服務 doctor 1/4、3/4、E1、sync 四處;同樣處理 Verification stale 的 `scripts/lumos:16506`、`:1872`、`:1928` 等仍走原樣比較,同一份驗收紀錄的「失效」判定在 repo 裡出現兩套口徑(patch 註解也承認「其他讀 status 的地方照舊分大小寫」)。
2. 結構對,屬於局部不一致,不影響本批功能;要收斂可讓 `_VERIF_INACTIVE` 的其他使用點一併改用,或留註明範圍(已留)。

## F2 `warn` 之後手動封頂並補 `issues` 差額,是鄰居沒有的做法
severity: minor
blocking: 否
引句:「issues += len(sr_bad) - len(_shown)」
佐證行 file: `scripts/lumos:1435`(`warn` 內 `issues += len(lines)`)、`scripts/lumos:1457`(封頂是 `warn_soft` 的內建 `_SOFT_CAP`,本批沒用它而是呼叫端自己切 20 項)。
1. 既有做法:要封頂的軟提醒走 `warn_soft`(內建 `_SOFT_CAP` + 「另 N 條」);要計數的硬提醒走 `warn`,不截斷(4/4 `chain`、G 段 `collisions` 都全列)。本批在呼叫端自己切片、補一句「…另 N 項」,再從 `issues` 外補差額,等於繞過 `warn` 的計數合約。
2. 若要保留硬計數又要封頂,較對齊的做法是讓 `warn` 接可選封頂參數,而不是在呼叫端 `issues` 偷補;目前只有這一處,故列 minor。

## F3 「全寫壞」判斷散在 doctor 1/4 段、跟 `_suggest_systems_for_orphan` 的回傳語意拆成兩處
severity: minor
blocking: 否
引句:「print("          ↳ (system_refs 全寫壞,先照 doctor 3/4 修)")」
佐證行 file: `scripts/lumos:875`(`_suggest_systems_for_orphan` 本來把所有推薦理由與「無線索」都收在函式內回 list,doctor 段只負責印)。
1. 既有做法:doctor 1/4 段只迭代 `sug` 並印;「沒有線索」的訊息由 `if not sug` 一處處理。本批在同一迴圈內為同一份 `o` 再呼叫 `_verification_system_targets` 一次、另開一個 `continue` 分支,於是「沒推薦」有兩個出口(全寫壞 / 無線索),且同一筆記被解析兩次。
2. 結構仍是 helper 呼叫、沒跨層,屬 minor;要對齊可讓 `_suggest_systems_for_orphan` 回一個可辨識的「全寫壞」旗標(或回空 list 配合同一個 `if not sug` 分流)。

⚠
`_verification_system_targets` 回傳三元組 `(宣告了沒, set, list)` 並以 `None` 表「已失效」;鄰居函式多回 dict/list/單一值,這種「None 或元組」的多義回傳在 `scripts/lumos` 內是否有先例,我沒逐一查完,判不準是否算新寫法,故不列為 finding。

不對齊共 3 條,其中 major 0 條
