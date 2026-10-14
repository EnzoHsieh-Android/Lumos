severity: major

不要用絕對路徑以外的寫法:對照檔是 `/Users/enzo/orca/workspaces/lumos-toolchain/reread-fp/scripts/lumos`,以下行號都在這支檔。

severity: major
blocking: 是 — 照字面實作,所有文字檔的逐檔 diff 都會是空輸出,`v2` 指紋退化成跟程式版本無關的常數。這個做法跟專案兩種既有寫法都不同。
引句:「對清單裡的每一支,單獨跑一次 diff(路徑用 git 原樣路徑、加 `:(literal)` 前綴)」
對照:專案裡「字面路徑」有兩種各自獨立的寫法,計劃把兩種疊在一起。
- ``file: `scripts/lumos:36216` ``:全域 `--literal-pathspecs`,後面接純路徑。
- ``file: `scripts/lumos:18550` ``:只在路徑前加 `:(literal)` 魔法前綴,不開全域旗標。
判定理由:
- 〈做法〉1 同一條裡,選項列了全域 `--literal-pathspecs`,每支檔的 pathspec 又加 `:(literal)`。
- 我在暫存 repo 實測 `git diff HEAD -- a.py` 的行數:只用魔法前綴是 7 行,只用全域旗標是 7 行,兩個一起用是 0 行(rc=0、沒有錯誤訊息)。全域旗標開著時,`:(literal)a.py` 被當成檔名,比對不到任何檔。
- 「0 行輸出」正好是計劃自己在〈做法〉1 要防的「未改」誤判洞。
- 修法:二選一,照 `scripts/lumos:36216` 只留全域旗標加純路徑。S1 到 S3 的夾具會抓到,但現在的文字沒有點名,實作者很可能照字面做。

severity: minor
blocking: 否 — 行為在字面 `HEAD` 時不變,風險是兩種語意並存,可以在實作時改成明確的模式旗標。
引句:「`tip` 是字面 `HEAD` 時行為完全不變」
對照:``file: `scripts/lumos:50959` ``(`_codeloop_default_base`)。
判定理由:
- 同一個參數用「字串剛好等於 HEAD」切換兩種語意:
  - 字面 `HEAD`:看目前簽出的分支登記的上游。
  - 解析過的 sha:看指向該 sha 的本機分支。
- 專案其他吃 `tip` 的函式都只收 sha,例如 `_lens_push_base`(``scripts/lumos:47181``)和 `_note_reread_scan`(``scripts/lumos:36061``)。
- 同一個提交,傳 `"HEAD"` 與傳它的 sha,在有兩條本機分支指向它時會得到不同的遠端選擇,進而可能不同的分岔點。代碼審那邊與回頭重讀那邊對同一頂端會算出不同起點,也沒有測試釘。
- 建議:改成 `tip=None`(維持現行的 symbolic-ref 路徑)對 `tip=<sha>`(points-at 路徑),兩個模式在簽名上看得出來;或者讓代碼審也傳 sha,只留一種語意。

severity: minor
blocking: 否 — 計劃已自己承認並在〈要一起改的說法〉列了 WHY 與 REVISIT 要改的節點,只是放置位置與命名跟既有分層不一致。
引句:「回頭重讀一律傳解析好的提交編號。」
對照:共用的起點邏輯放在推送起點那一區,由多個閘呼叫。
- ``file: `scripts/lumos:47244` ``(`_push_mainlines`)、``scripts/lumos:47361`` (`_push_pick_base`)、``scripts/lumos:47181`` (`_lens_push_base`)。
- `_codeloop_default_base`(``scripts/lumos:50959``)是代碼審自己的函式,目前只有代碼審判定一個呼叫點(``scripts/lumos:51024``)。
判定理由:
- 筆記內容審的回頭重讀(``scripts/lumos:36000`` 一帶)會第一次直接呼叫一支 `_codeloop_` 開頭的函式,並改它的簽名與語意。
- 重用既有函式、不另寫第二套,方向對。但它現在歸代碼審的家,回頭重讀這邊改它,等於讓兩個家共享一支名字屬於其中一家的函式。
- 這也讓同一次 check 裡有兩套起點:候選範圍走 `_note_audit_start`(``scripts/lumos:35432``),指紋走 `_codeloop_default_base`。
- 計劃已用「全部未改退回 `v1`」補這個縫。這跟 ``scripts/lumos:47413`` 說的「兩套並存、收斂路記在 Issue」是同一型,可接受。
- 建議:把共用部分抽成推送起點區的函式(例如 `_lens_default_base(repo, tip)`),`_codeloop_default_base` 留成薄包裝,新舊呼叫者都指向它。

severity: minor
blocking: 否 — 只差在重複釘選項,不影響正確性。
引句:「在現有給判定者組 diff 的 `_NOTE_REREAD_DIFF_ARGS` 旁定義指紋用的那組,由它延伸」
對照:
- ``file: `scripts/lumos:32110` ``(`_ns_diff`):已釘 `--inter-hunk-context=0 --diff-algorithm=myers`、前綴與 `--no-ext-diff --no-textconv`。
- ``scripts/lumos:33718``:同一組又抄了一份。
- ``scripts/lumos:36005``(`_NOTE_REREAD_DIFF_ARGS`):判定者那組沒有釘這兩個。
判定理由:
- 計劃標題寫「選項只有一組」,實際是回頭重讀自己的兩組(判定者用、指紋用),再加專案已有兩份抄寫的 `_ns_diff` 系列。`inter-hunk-context` 與 `myers` 這個釘選意圖會多出第三份。
- `_ns_diff` 內建 `-U0` 且 `diff` 緊接在 `_ns_git` 後面,放不進全域 `-c` 和 `--literal-pathspecs`,所以不能原樣用。
- 建議:把「釘 hunk 切法」那兩個旗標抽成一個常數,三處共用;至少在計劃裡把「選項只有一組」改成實際的兩組加與 `_ns_diff` 的關係。

severity: minor
blocking: 否 — 加法本身合乎既有 `extra` 慣例,只有欄位名與逾時機制需要補一句。
引句:「`fp`(這次候選裡 `v2`、`v1` 各幾篇,`v1` 的再按退回原因分」
對照:
- ``file: `scripts/lumos:1326` ``(`_gate_event_build`):`extra` 是平放的 `ev.update`,欄位名註解特別強調「同一個 gate 的欄位名要對得起來」。
- 同一個 note-reread 事件目前已有 `layer1_fps: [{path, fp}]`(``scripts/lumos:37108``),`fp` 是指紋字串。
判定理由:
- 新頂層 `fp` 是計數物件,跟 `layer1_fps` 裡的 `fp` 字串同名不同型。
- 計劃沒說 `layer1_fps` 現在記 `v2` 還是 `v1`:`_note_reread_fps` 目前回單一值,改成兩種後呼叫端要選哪個沒寫。
- `branch` 放進 note-reread 事件不會被 `_codeloop_ledger_events` 當成留痕,因為它先檢查 `gate == "code-loop"`(``scripts/lumos:49223``)。這點安全,但 ``scripts/lumos:1346`` 的註解曾因此踩過雷,建議計劃明寫「放 `extra`、不用 `ref`」。
- `reminded`、`blocked` 走 `_gate_event_fit`(4096 位元組);`covered`、`none` 現在不帶 `extra`。實作者需要知道新欄位要不要參與截斷。

severity: minor
blocking: 否 — 屬於另一套逾時規則並存,計劃已說明降級語意。
引句:「剩不到 3 秒就不跑,剩下的候選直接用 `v1`」
對照:``file: `scripts/lumos:36061` ``(`_note_reread_scan` 的 `_tick`)與 ``scripts/lumos:35999`` 一帶的 `_note_reread_fail`。既有做法是在呼叫點之間看截止時間,過了就丟 `_NoteRereadStop`,單次 git 用它自己的上限;`_ns_git`(``scripts/lumos:32100``)沒有逾時參數。
判定理由:
- 計劃的每次 git 呼叫逾時取較小值是一個新機制,`_ns_git` 要新增 `timeout` 傳到 `_lens_git`(它已支援,``scripts/lumos:47386``)才做得到。計劃沒寫這個接線,另外三個 `_ns_git` 呼叫者不能被改到。
- 「降級成 `v1` 而不是停下」跟既有 `_tick` 的「停」不同,這是刻意的。但要在計劃裡寫成與 `_tick` 的差別,免得實作者分不清兩者各管哪段。

沒有發現不對齊的部分:
- 給 `_patch_file_changes` 加「不算函式名標頭」參數(``scripts/lumos:25875``):預設值維持舊行為,資安席兩個呼叫點(``scripts/lumos:26039``、``scripts/lumos:26083``)不受影響,符合「先找既有」。
- 新舊兩種指紋都認:沒有專案先例衝突。`_DRIFT_ACK_LEGACY_UNTIL`(``scripts/lumos:37161``)是會到期的舊格式,`v1` 是永久退路,不需要到期日。

總結:不對齊共 6 條,其中 major 1 條(`--literal-pathspecs` 與 `:(literal)` 疊用導致 diff 空輸出)。
