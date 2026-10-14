severity: minor

我只讀了 `scripts/lumos`、`scripts/hooks/claude/dispatch-lens-hook.py` 和計劃全文;r4 diff 只改計劃文字,沒有程式碼。計劃的主幹跟既有寫法一致,四條出入都是 minor,沒有引入第二種做法或跨層直呼。主幹對照結果如下。
- 提交編號解析走 `_lens_full_sha`,讀提交裡的檔走 `_nodehome_cat_blobs_capped`,都是借用既有函式。
- 掛鉤只讀 lumos 印的 JSON 欄位,沿用既有的 `_last_json` 與 `lens_fail`(`dispatch-lens-hook.py:238-252`),不判文法、不跑 git。
- 失敗代碼集合有 S11 對照測試守著。
- 讀計劃收斂成一支共用函式,方向正確。
- 計劃有列新子命令的指令總數漂移守衛。

severity: minor
blocking: 否 — 建的物件跟既有不掛 ref 的凍結做法取向相反,但窗口夠一晚用,只需補一句為何跟 `_replay_git_blob` 不同
引句:「不掛 ref 的物件在預設 gc 兩週後才會清」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:1043-1058`(`_replay_git_blob` 的註解寫明,凍結一律取 HEAD 的 blob,因為 `hash-object -w` 落的懸空 blob 兩週可被 GC)
判定理由:專案既有的凍結慣例是只引用已被 tree 引用的物件,刻意不落懸空物件。spec-freeze 偏偏用 `hash-object -w` 加 `commit-tree` 落懸空物件,兩套凍結物件的永續性取向相反,計劃沒有點名這個既有取向、也沒說為什麼這裡可以破例。理由其實成立:設計迴圈只活一晚,不像 replay 要長期回放。建議補一句區分,不改設計。

severity: minor
blocking: 否 — 專案內沒有現成的暫存 index 或 `commit-tree` 寫入做法,這是首例,但計劃沒指定走哪個 git 呼叫包裝
引句:「凍結提交借 git 原生的做法」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:47386`(`_lens_git`,只讀包裝,沒有 `env` 參數);file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:31844`(`write-tree` 只用在真的 index 上,透過 `_nodehome_git`);全檔沒有 `GIT_INDEX_FILE` 或 `commit-tree` 的實際呼叫(31970 只是註解)
判定理由:計劃把這個做法說成借用 `git stash create`,但那不是 lumos 裡的既有寫法。spec-freeze 需要傳 `GIT_INDEX_FILE` 與固定作者環境變數,而現有的 `_lens_git` 和 `_nodehome_git` 都不支援。計劃沒說是擴充這兩個包裝,還是像另外 63 處那樣直接 `_sp.run`。後者會多一個寫入端的 git 呼叫包裝。建議計劃指定:擴充既有包裝加 `env` 參數,或明寫這是首個寫物件的呼叫點。

severity: minor
blocking: 否 — 計劃已自陳是有限破例,且有固定字首與回退時的 grep 檢查
引句:「只用在提交寫法成功與這幾個代碼,note 用固定字首」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/hooks/claude/dispatch-lens-hook.py:244-252`(既有 `_fail_note` 只在 lumos 失敗並帶認得的 `lens_fail` 時記事件)
判定理由:既有慣例是 `_hookevent.mark` 只在吞掉逾時或失敗時呼叫。計劃讓「成功」也記事件,note 又用字首字串當半結構化欄位,等於 note 欄多了第二種用法。計劃為了量測撤除條件,有意做了這個破例。風險是日後讀端把字首當格式去解析。計劃回退節已列「grep 確認無讀端解析」,所以只列 minor。

severity: minor
blocking: 否 — 兩套路徑規則並存是計劃刻意的相容選擇,但沒對照專案既有的路徑正規化工具
引句:「只做字串檢查,不先正規化」
對照:file: `/Users/enzo/orca/workspaces/lumos-toolchain/lens-repo/scripts/lumos:477-483`(`_posix_norm`,既有的 posix 路徑正規化)
判定理由:同一個 `LUMOS-SPEC:` 標記,提交寫法走嚴格字串規則,工作樹寫法走原本寬鬆的解析,同一份文法兩套驗證。工作樹那條不動是為了相容,可以接受。但提交那條的 `.`、`..`、空段、反斜線檢查沒說明為什麼不能復用或對照既有的 `_posix_norm` 做法,只把「不正規化」當設計。建議補一句不復用的理由。

總結:不對齊 4 條(都是 minor),major 0 條。
