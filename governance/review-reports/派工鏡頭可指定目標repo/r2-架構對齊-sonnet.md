severity: major

三個 major 都在設計寫法,不在行為:一條是登記清單放新的使用者層根目錄,一條是 fsmonitor 的防護寫成單點補丁,一條是被拒時取角色卡的路徑沒定義。我只讀了計劃、diff 和 lens-repo,沒跑任何程式。diff 只動了計劃筆記本身。

severity: major
blocking: 是 — 登記清單放進專案從未用過的 `~/.config/lumos/`,並另寫一套信任檢查,造出第二種使用者層狀態做法;專案現成的做法也沒被評估。
引句:「把那個專案的根(realpath)追加進使用者層的」
對照:
- `scripts/lumos:47499` — `_home_cache_write` 與 `_mkdir_trusted_under_home`、`_trusted_private_dir`:使用者層狀態放 `~/.cache/lumos/<subdir>/`。逐層建目錄、逐層驗不是 symlink、擁有者是自己、0700、原子寫入。dispatch-lens 的武裝檔、vault-lock、drift-defs、bound-filter 都走這套。
- `scripts/hooks/claude/check-graph-sync.py:857` — `_stop_dir_ok`:掛鉤端同一套威脅模型的檢查。
- `scripts/lumos:25530` — 使用者層的另一個位置是 `~/.claude/hooks`,以及 `LUMOS_HOME` 指的來源位置。
- `scripts/hooks/claude/_hookevent.py:13` — 慣例寫明家目錄只留給 OS 逼你放的東西。
- 全 repo 沒有 `~/.config/lumos` 的任何用法(grep 為零)。

判定理由:
- 計劃第 2 條要求「清單檔(檔與它的資料夾)要屬於自己、不可 group/other 寫」,並說「另寫在新函式裡」,理由只講不改 `_trusted_lumos` 那段逐字複本。
- 但現成的 `_trusted_private_dir` 已經做這件事,而且原本就是掛鉤與主程式共用的威脅模型。這樣會多出第二個目錄信任檢查,還會多一個沒人巡的使用者層根。
- 登記清單是持久信任資料,不是快取,可能是不放 `~/.cache` 的理由。計劃沒寫這個理由,也沒評估 `~/.cache/lumos/projects/`。
- 要嘛改用 `~/.cache/lumos/<subdir>/` 加既有的 `_trusted_private_dir` 與 `_home_cache_write`,要嘛明寫為何非 `~/.config` 不可,並讓檢查函式重用這些。
- 清單遺失時是 fail-closed(當成空清單),所以放 cache 的風險可接受。

severity: major
blocking: 是 — 對同一個防護(git 讀取時不執行設定指令)另開逐點補丁,和專案已定的具名清單加環境變數做法並存;對其他呼叫者也有未評估的影響。
引句:「`_lens_git` 一律帶 `-c core.fsmonitor=false`」
對照:
- `scripts/hooks/claude/check-graph-sync.py:969` 起 — `_GIT_UNSAFE_CONFIG` 清單與 `_harden_git_env`。註解寫明這是「逐個補」被換掉之後的形狀,新發現的項目往清單加一行並補測試。
- 該處清單已有 `core.fsmonitor` 與 `diff.external`,用 `GIT_CONFIG_PARAMETERS` 讓所有子行程繼承。
- `scripts/lumos:47386` — `_lens_git` 有約 30 個呼叫點,含 doctor、pre-push、代碼審範圍。
- `scripts/lumos` 另有 63 處直接寫 `["git", "-C", …]` 的呼叫,不走 `_lens_git`。

判定理由:
- 在 `_lens_git` 內寫死 `-c`,是第二種做法。
- 它讓「派工鏡頭只讀歷史」的理由變成對所有 `_lens_git` 呼叫者生效。這些呼叫者含 `diff HEAD --name-only`(`scripts/lumos:34408`),在開了 fsmonitor 的大 repo 上會變慢。
- 計劃沒評估這個影響。
- 那 63 處直呼的 git 沒被蓋到,所以「讀取時也不會因此執行指令」說大了。`diff.external` 與 textconv 也沒被蓋。
- 較對齊的做法:`dispatch-lens-hook.py` 在叫 lumos 前套同一份 `_GIT_UNSAFE_CONFIG`,涵蓋整條子行程,並讓那份清單成為單一來源。若堅持改 `_lens_git`,要列出對其他呼叫者的影響並補測試。

severity: major
blocking: 是 — 被拒時取角色卡的路徑沒有對應的 lumos 介面,而現有唯一路徑就是計劃自己禁止的「在會談目錄算圖譜」。
引句:「但仍用會談目錄叫一次 lumos 只取角色卡與架構段」
對照:
- `scripts/hooks/claude/dispatch-lens-hook.py:267` — `_extra_text` 只會從 lumos 失敗分支的 JSON 取 `role_text` 與 `arch_text`。
- `scripts/hooks/claude/dispatch-lens-hook.py:448` — `--role-cards` 只在 `rng and wants_role_cards` 時傳。走 `--spec` 的設計審路徑從不傳,所以 S8 對設計審路徑沒有現成做法可套。
- `scripts/lumos:53075` — lumos 沒有只取卡片的旗標。

判定理由:
- 現行機制是呼叫同一個 `dispatch-lens` 並讀它失敗時順帶印出的卡片。
- 要在被拒時只取卡片,有兩條路:加新的 lumos 模式或旗標,或帶原範圍在會談目錄呼叫。
- 計劃沒列新旗標,第 8 點的手冊與 `lands_in` 也沒有。
- 後者會在會談目錄算圖譜,違反同一點的「也不退回會談目錄算」。要在會談目錄跑 git 的是錯範圍或錯計劃。
- 要先定義這條路:新增 lumos 端的卡片專用旗標,並釘進測試與 `FAIL_NOTE`。

severity: minor
blocking: 否 — 掛鉤是獨立複製進 `~/.claude/hooks` 的單檔,不能 import 主程式,所以複製可接受。但缺漂移守衛,而且 `_events_main_trusted` 的方向和前提與掛鉤的需求不同。
引句:「照它的寫法:相對路徑以那個檔所在的資料夾為基準」
對照:
- `scripts/lumos:27051` — `_events_main_trusted` 是反向驗證:給定 root,確認它登記在 `main_root/.git/worktrees/*/gitdir` 裡。
- 它假設 `main_root/.git` 是目錄。
- `scripts/lumos:26910` — 共用資料夾由 `git rev-parse --git-common-dir` 取得。
- `scripts/hooks/claude/check-graph-sync.py:632`、`lumos-entry-hook.py:204`、`dispatch-lens-hook.py:308` — 掛鉤端的 `_trusted_lumos` 已經是有守衛盯著的逐字複本。

判定理由:
- 掛鉤要的是正向列舉,而且會談可能開在工作樹,那時 `.git` 是檔案,要讀 `gitdir:` 與 `commondir` 才找得到共用資料夾。
- 計劃第 6 點又說掛鉤不再跑 git,所以這一步要手讀 `.git` 檔。計劃沒寫怎麼做,而 `commondir` 正是 r1 實測過的攻擊面。
- 這會變成第三份相似的 worktree 解析。建議二選一:抽成掛鉤共用的複本並加漂移守衛,或明寫反向驗證(對方的 `.git` 檔指回登記的共用資料夾)並測試。

不對齊共 4 條,其中 major 3 條(登記清單位置與信任檢查、fsmonitor 防護寫法、被拒時取角色卡的路徑)。
