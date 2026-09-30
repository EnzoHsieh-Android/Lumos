severity: major

架構對齊鏡頭:對照筆記內容審(note-audit)、存量漂移檢查(drift check)、每支檔有家(nodehome)。整體沿用既有骨架(`_note_audit_resolve`、`_nodehome_*`、`_write_lf`、工作目錄、逐件紀錄檔、簿記豁免),下列是仍出現「第二種做法」或接法不一致的地方。

## F1 prepare 與 check 用兩種起點判法,同一次推送的項目指紋對不上
severity: major
blocking: 是
引句:「手動跑不帶那兩個參數時照 `_lens_push_base`。」
file: `scripts/lumos:26147`
1. 指紋含「給的 diff 全文雜湊」,diff 由範圍起點決定。spec 讓 reread-check(掛鉤與 CI)走 `_push_range_start`(帶 --push-remote/--pushed-ref),而 reread-prepare 手動跑時走 `_lens_push_base`(`_note_audit_start` 的兩條分支,26147)。兩者在合過主線、新分支、遠端舊值比主線分岔點舊時起點不同,diff 不同,指紋不同。
2. 結果:作者照 check 印的指令 prepare、record、commit 之後再推,check 用自己的起點重算指紋,對不上、一樣列「沒對照」。提醒永遠消不掉。
3. 既有做法是 note-audit 的 prepare、record、check 三者都吃同一個 `_lens_push_base`,所以彼此對得上;drift 只有 check 一支所以沒這問題。本案是第一個「產出物綁範圍、而產出者與檢查者起點判法不同」的家族成員。
4. spec 沒寫 reread-prepare 是否接受 --push-remote/--pushed-ref、check 印的 prepare 指令是否帶它們。要嘛 prepare 也收這兩個參數且 check 印的指令原樣帶上;要嘛指紋不含 diff 全文(改用 about_code 內被改檔的 blob 雜湊)。

## F2 掛鉤「回傳值不看」跟既有掛鉤接法不同,會吞掉 Ctrl-C
severity: major
blocking: 是
引句:「之後加一段,參數照它;回傳值不看。」
file: `scripts/hooks/pre-push:477`
1. pre-push 裡每一道檢查(包含存量漂移那段)都用 `pp_stop_if_signaled "$rc" "<名>"`:rc>=128(被訊號殺、多半是 Ctrl-C)整支掛鉤停下,不往下跑全套也不推(pre-push:50、478)。
2. spec 明寫回傳值不看,這是掛鉤裡第二種接法。使用者對 reread-check(最壞會跑 git 一陣子)按 Ctrl-C,掛鉤會繼續跑全套測試並放行推送,跟其餘每一道閘的行為相反。
3. reread-check 自己恆回 0 不代表被殺時也是 0;「恆回 0」該由 lumos 內部保證,掛鉤仍應保留 `pp_stop_if_signaled`,其餘非零可靜默(或印一句「這次沒提醒」)。
4. 同理,現有那段還有「上線標記」註解行(`# lumos drift check`,pre-push:468)明寫別改寫別刪;spec 只靠呼叫行本身含 `note-audit reread-check` 當上線點,沒有說明要不要同樣獨立標記行。建議照做並在註解寫「上線標記」。

## F3 治理帳閘名沿用 note-audit,與 drift 家族「各檢查自己一個閘名」不一致,且一次跳過會雙記
severity: minor
blocking: 否
引句:「閘名沿用 `note-audit`(已在 `_KNOWN_GATES`,事件種類不用登記)」
file: `scripts/lumos:26099`
1. `_note_audit_resolve` 預設 `gate="note-audit"`,起點算不出、淺層 clone 時在裡面自己記一筆 `note-audit`/`skipped`(26099 之後)。spec 沒說 reread 呼叫時要傳 `gate=`,所以一次跳過會記兩筆:resolve 的 `skipped` 與 spec 的 `reread-skipped`。
2. `note-audit`/`skipped` 已被 `note-audit skip` 子指令用來表示「略過了 N 行」(26585);reread 的跳過混進同一個閘同一個事件種類,筆記內容審自己 REVISIT(2026-10-12)量帳時會讀錯。
3. 存量漂移(同樣是掛在 `_note_audit_resolve` 上的兄弟檢查)先例是傳自己的 `gate="drift-check"` 並在 `_KNOWN_GATES` 登記。照先例:reread 用自己閘名(例 `reread-check`)並傳給 resolve,事件種類就不必加 `reread-` 前綴。

## F4 候選交集的兩邊路徑形狀與回傳形狀,spec 沒對齊
severity: minor
blocking: 否
引句:「用 `_nodehome_homes`(背後是 `_home_map_from_notes`:Systems 底下、type 是 system、status 是 doing/done/stale 的節點)」
file: `scripts/lumos:23877`
1. `_nodehome_homes` 回的是 `(homes, own)` 二元組(`_home_map_from_notes` 的回傳,23861;evaluate 也是 `homesN, ownN = ...`),不是註解上寫的 `{檔: [家]}`;spec 沒提。
2. homes 的值是家的「圖譜內相對路徑」(`Systems/x.md`,`_nodehome_side` 用 `p[len(vault_rel)+1:]` 切出,23795 起);而 `_notes_status_flipped` 的 touched 是 repo 根路徑(`docs/<圖譜>/Systems/x.md`,`git log ... -- vault_rel`)且比對時要 `nfc()`。spec 直接寫「家 ∩ 被改過的筆記」,實作者若直接交集會恆為空,結果是恆印「這次沒有要對照的家筆記」、rc0,靜默失效。
3. 既有「改到的程式檔 → 家」流程在 `_nodehome_evaluate`(24207)已有 `_nodehome_config`、`_nodehome_side`、`vendored_skip` 那一串前置;spec 只寫「用 `_nodehome_required`」,沒說 cfg、vendored_skip、side 從哪來。建議明寫「複用 nodehome-check 的前置與 `changes` 分類」,並寫死路徑正規化(全轉 repo 根路徑 + nfc)。

## F5 沒有 config 開關,跟三道兄弟檢查的「專案可關」慣例不同
severity: minor
blocking: 否
引句:「`LUMOS_SKIP_REREAD_CHECK=1` 單次不跑。」
file: `scripts/lumos:28832`
1. note-audit、drift、note-shape 都有 `.lumos/config.json` 的 `<名>.gate`(off/warn/block)可整個專案關掉(`_note_audit_config`、`_drift_config`)。reread 只有單次環境變數。
2. pre-push 是 `_VENDORED_TREE_FILES` 會發到消費專案,所以每個消費專案都會在每次推送跑一次 reread-check(掃歷史、算指紋),沒有專案級的關法;doctor 也不唸。誠實界線寫了消費專案 CI 帶不到,但掛鉤帶得到。
3. 至少要有 `reread_check.gate=off` 或在無候選時零成本;或明寫「消費專案在轉擋前刻意不提供開關」與撤除條件。

## F6 範本載入、佔位字、判定者模型另寫一套,沒說要不要抽共用
severity: minor
blocking: 否
引句:「版本常數 `reread-v1` 放程式裡(同 `_NOTE_AUDIT_PROMPT_VERSION` 的做法)。」
file: `scripts/lumos:26162`
1. 既有 `_note_audit_prompt`(26162)包了:找範本(專案優先、退回工具安裝樹)、剝 SPDX 行、剝首個註解、`.replace` 佔位字。spec 要求同樣的剝法,但把佔位字改成「一次掃描」、大小寫也不同(既有 `{{REPO_PATH}}` 全大寫,spec 是 `{{trunc}}`、`{{diff}}` 小寫),等於第二份載入與替換程式碼。
2. 版本常數既有是整數 `_NOTE_AUDIT_PROMPT_VERSION = 1`,spec 用字串 `reread-v1`;判定者模型既有是函式 `_note_audit_judge_model`(dict 查表),spec 說「新常數」。兩處各長一份,日後改「剝註解」或「換模型策略」要改兩處且沒有東西讓它們一起翻紅(記憶裡「散落同步要守衛」的同一形狀)。
3. 建議:把「讀範本+剝頭」抽成一支共用(帶佔位字表與單次掃描),note-audit 的三個固定佔位字改用它並保持輸出逐字相同(S9 類測試釘);模型走同一支 `_note_audit_judge_model`(加參數 kind)。若刻意不共用,spec 要寫明理由。

其餘各節(項目檔工作目錄與 14 天清理、逐件紀錄檔用 `_write_lf` 原子寫入、`_BOOKKEEPING_DIRS` 豁免、只認被推送頂端提交的樹、`_VENDORED_TREE_FILES` 登記、CI 用 `continue-on-error` 加 `|| true`、`note-audit check` 字串避讓):已讀,無 finding。

最高等級:major;blocking 共 2 條
