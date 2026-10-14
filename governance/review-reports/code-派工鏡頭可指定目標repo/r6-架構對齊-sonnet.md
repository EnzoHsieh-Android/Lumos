severity: minor

已讀五個點名項,對照 patch(`/tmp/code-派工鏡頭可指定目標repo-r6-repair-code.patch`)與 `lens-repo` 原始碼。結論:①④⑤與專案既有做法一致,②有一處分歧,③有一處形狀差異。

## Finding 1:同一個 `arch_text` 欄位,設計審有框、代碼審沒框

severity: minor
blocking: 否 — 兩條路的內容來源信任度不同(代碼審讀分叉點版本,設計審讀 HEAD),沒有跨層直呼,也沒有引入第二套框;只是同一欄位的框法不一致。
引句:「return _frame_injected(_arch_target_text(root, "HEAD", vault_rel, _arch_target_split(cands, rules), warns, show=show))」
對照:代碼審的 `_dispatch_lens_arch_text` 回傳 `_arch_target_text(root, ref, ..., targets, warns)`,沒有 `_frame_injected`,失敗時回 `_arch_target_fail_text(e)` 也沒框。對照 `scripts/lumos:50218` 與 `scripts/lumos:50221`。設計審的 `_dispatch_lens_spec_arch_text` 在 `scripts/lumos:51156` 與 `scripts/lumos:51159` 已經包框。
判定理由:
- 框用的是同一支 `_frame_injected`,沒有另組,這部分合格。
- 但 `_arch_target_text` 現在有兩種呼叫形狀。設計審傳 `show` 並在外層包框,代碼審不傳也不包。
- 代碼審那條路的規則原文與檔名仍是被審分支可影響的檔名,只經 `_kill_esc`,而且在框外。
- 這和 patch 自己講的「R5 起作者可控文字一律在框內」不完全同調。
- 建議之後統一在 `_arch_target_text` 內部加框,或在註解寫明代碼審不框的理由。這次不列為 major。
- 佐證:``scripts/lumos: `scripts/lumos:50218` ``、``scripts/lumos: `scripts/lumos:51156` ``

## Finding 2:端到端哨兵測試與既有測試形狀大致同形,但不是同一支輔助

severity: minor
blocking: 否 — 沿用同一組夾具函式(`_nh_*`、`_lr_*`、`_load_hook_mod`),沒有引入第二套測試框架。
引句:「def _lr5_sentinel_problems(t, tokens, m):」
對照:既有注入框測試 `t_dispatch_lens_hook_claim_timeout_framed`(`scripts/test_lumos.py:45610`)和 `t_dispatch_lens_spec_commit_frame_without_nodes`(`scripts/test_lumos.py:46926`)都是直接斷言框頭框尾存在。
判定理由:
- 新測試另寫了 `_lr5_frames`、`_lr5_sentinel_problems`,多驗一層「整個哨兵落在同一對單角引號之間」,這是新要求,不算風格偏好。
- 它們只在新測試裡用,沒有人去複用既有框偵測。
- 舊的 AST 結構守衛(`t_dispatch_lens_spec_author_names_single_exit`)已經被拿掉,改成行為守衛。這是有說明的換形狀(R5 邊界席證明 AST 守衛漏 join、extend、覆寫變數),不是同一件事的兩種做法並存。
- 搜尋 `single_exit` 在 `scripts/test_lumos.py` 已無殘留。
- 佐證:``scripts/test_lumos.py: `scripts/test_lumos.py:47946` ``、``scripts/test_lumos.py: `scripts/test_lumos.py:47976` ``

## 逐項回答

- **①`_kill_esc` 加參數 vs 其他消毒:已讀,無 finding。**
  - `_esc_clean`(`scripts/lumos:12382`)是有損的換空格,註解明說不併用。
  - `_plain_label`(`scripts/lumos:49463`)是單行化,供注入框內的標籤用。
  - `_lens_visible` 是出口最後一道,逐行呼叫 `_kill_esc`。
  - 「無損、看得見的 `\uXXXX` 跳脫」本來就是 `_kill_esc` 的職責,新參數預設空集合,既有呼叫端行為不變。
  - `_lens_author_name_show` 在上面加標記、截斷與空名字處理,分工清楚。
  - `_lens_visible` 會再過一次 `_kill_esc`,但已跳脫的內容是純 ASCII,不會重複跳脫。
- **②注入框組法:** 全部走 `_frame_injected`,沒有另組。
  - 掛鉤端的四種說明行與逾時、鎖狀態未知那條都包 `_frame_injected`,和掛鉤自己已有的 `CLAIM_TIMEOUT_NOTE` 做法(`dispatch-lens-hook.py:450`)一致。
  - 落點、掛鉤說明行改成「有輸出就加框」(`if lines:`),和影響鏡頭一致。
  - 代碼審那條不框,見 Finding 1。
- **④`_lens_spec_nfc_groups`:已讀,無 finding。**
  - 做法同 `_nodehome_landing_missing`(`scripts/lumos:50874`):先 `unicodedata.normalize("NFC", …)` 再比。
  - 它還是 `_lens_spec_code_cands`、提交候選和 `_dispatch_lens_spec_arch_text` 三處共用的單一入口,原本兩處各寫一份的 NFC 去重收斂成一支。
- **⑤掛鉤抄最小實作加兩邊比對:已讀,無 finding。**
  - 專案的做法是掛鉤不 import lumos,各 hook 各自抄 `_frame_injected`、`_plain_label`(`ci-status-hook.py:98`、`lumos-entry-hook.py:78`、`memory-sweep.py:75`、`impact-hook.py:498`)。
  - 這次改成「對同一批樣本比輸出」(`t_dispatch_lens_hook_name_show_matches_lumos`),比原本只比常數更強,方向一致。
  - 掛鉤的類別集合是七個字面類別,lumos 是 `_PATH_SPECIAL_CATS`(Cc、Cf、Zl、Zp、Cs)加上 Co、Cn,兩邊等價,有樣本測試守著。

最高等級 minor,blocking 0 條。
