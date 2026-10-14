severity: minor

這份 diff 在你點名的幾處都跟既有寫法一致:沒有第二種做法,也沒有跨層直呼。新加的 git 呼叫都走 `_lens_git`,經 `_lens_git_dl` 包一層截止時間。只有兩條小處的重複。

- `_lens_default_base` 搬到推送起點那一區,舊的 `_lens_default_base` 呼叫端(手動 code-loop check 的起點函式)改成一行薄包裝,行為不變。
- 事件寫帳走既有 `_gate_event_fit` 加 `_gate_event_or_warn`,跟 `note-shape` 放寬帳的寫法同形,新欄位只是往 `extra` 加。
- `_note_reread_hits` 包住 `_note_reread_covered`(先 v1、再 v2),是分層,不是兩條平行路徑。`prepare` 與 `check` 都改呼叫 `_note_reread_hits`,沒有一邊漏改。
- `_patch_file_changes` 新增兩個參數,預設值維持資安席原行為。

severity: minor
blocking: 否 — 只是同一件事多寫一份,不引入新做法,行為也一致
引句:「min(cap, deadline - _t.monotonic())」
對照:既有寫法 file: `scripts/lumos:31359`(`_nodehome_cat_blobs_capped`,內聯寫 `timeout if deadline is None else min(timeout, deadline - _t.monotonic())`)
判定理由:新加的 `_git_timeout` 與 `_lens_git_dl` 是「單次 git 逾時夾進剩餘時間」的通用 helper,但 `_nodehome_cat_blobs_capped` 的內聯寫法沒有改用它。專案現在同時有「通用 helper」和「各處內聯」兩種寫法。這兩處語意相同,後續可以讓舊處改用新 helper,現在不構成跨層或分歧。

severity: minor
blocking: 否 — 設定值重複,目前兩處同值,不影響行為
引句:「"-c", "core.precomposeunicode=false", "diff", "--no-ext-diff",」
對照:同一份 patch 新增的 `_NOTE_REREAD_FP_GIT`(`scripts/lumos` 新增常數,同樣含 `-c core.precomposeunicode=false`)
判定理由:`_note_reread_diff` 把 `core.precomposeunicode=false` 直接寫死在 `_ns_git` 呼叫裡。v2 指紋那邊則是集中放在 `_NOTE_REREAD_FP_GIT` 常數。同一個 git 設定有兩處各寫一份,日後改一邊容易漏另一邊。`_note_reread_diff` 仍走既有的 `_ns_git`,而新增的指紋呼叫走 `_lens_git_dl`,兩者原本就是不同的既有 git 封裝,不算跨層。

不對齊 2 條(都是 minor),major 0 條。
