severity: major

## 已讀,無 finding

- 快取鍵:`_lens_cache_path` 用 `realpath(repo 根)|base|head|schema|表態雜湊` 做雜湊,目標 repo 與會談 repo 的鍵不同,不會撞。
- 鎖路徑:鎖是 `<快取檔名>.warming`,放在 `~/.cache/lumos/dispatch-lens/`,跟著快取鍵走,也就跟著目標 repo 走。
- 背景暖機行程:`_lens_spawn_warmer` 把 `--repo` 原樣傳下去,鎖名經環境變數交給背景行程,背景行程只清自己的鎖。

## finding 1

severity: major
blocking: 是 — 信任檢查與 git 在掛鉤預算起算之前執行,時間不計入;卡住時外層會直接砍掉掛鉤,fail-open 與超時說明都跑不到
引句:「前四條都過了,才跑 `git -C <路徑> rev-parse --show-toplevel`(`git` 取自 PATH,跟 lumos 跑 git 一樣)」

問題:
- 材料沒有說這一步的時間上限,也沒說它算不算進預算。
- 掛鉤的 `_inner_budget` 是第一次被呼叫才開始計時(`_BUDGET_START` 起初是 None)。
- 新增的檢查要在 `_lens_timeout()` 第一次被呼叫之前做完,所以它花的時間完全不會從 `_dl` 與 `_run_tmo` 裡扣掉。
- `_dl` 與 `_run_tmo` 夾在外層的 0.9 倍以內。這個上限是假設後面的工作從零開始算出來的。

失敗情境:
- 目標 repo 在慢速掛載(NFS、iCloud)上,或 git 因 `core.fsmonitor`、索引鎖、PATH 上的 git 而卡住。
- 這一步吃掉 20 秒,後面的 lumos 呼叫仍可以跑滿 `_run_tmo` 約 47 秒(外層 60 的 0.9 倍是 54,取兩者較小)。
- 合計超過外層 60 秒,外層以 SIGKILL 砍掉掛鉤。
- 結果是 `except` 與 `_mark("timeout")` 都跑不到,派工詞什麼都沒附,也沒有超時說明。
- 這正是掛鉤檔頭「內層 ≥ 外層會讓 fail-open 結構上跑不到」所說的問題,新路徑又把它帶回來。
- 同一支掛鉤同一輪也會對 3 個以上的席重複付這筆時間。

補救方向:
- 把新增的 git 呼叫改成帶 `timeout`。
- 進入信任檢查前先起算 `_BUDGET_START`,讓這段時間被扣掉。
- 或者直接省掉這次 `rev-parse`,因為 lumos 自己會再算一次 `--show-toplevel`。

佐證:
- file: `scripts/hooks/claude/dispatch-lens-hook.py:133`
- file: `scripts/hooks/claude/dispatch-lens-hook.py:444`
- file: `scripts/lumos:47386`(`_lens_git` 有 20 秒上限,但那是 lumos 內部的)

## finding 2

severity: minor
blocking: 否 — 只是重複計算;範本就是「同一份計劃派多席」的設計審,有原因代碼可查,不會卡死或誤附
引句:「設計審的 `LUMOS-SPEC:` 相對路徑照舊以 repo 根為基準。」

問題:
- 設計審的 `--spec` 路徑沒有快取、沒有鎖、沒有背景暖機,自己的 `_LENS_SPEC_BUDGET` 是固定 30 秒,不看掛鉤傳下去的預算。
- 一次派 N 席、同一個 `LUMOS-REPO:` 時,每席各自做完整的信任檢查、掛鉤的 git 呼叫和 lumos 的 `--spec` 計算,沒有任何共用。
- 這 N 次的總時間不會彼此扣減。
- 掛鉤是依序處理 Agent 呼叫,所以編排者在每席派出前都要等一輪。

失敗情境:
- 同一份計劃連派 10 席。每席的重複計算在大 repo 上是 5 到 30 秒的 `impact`,再加上 finding 1 的檢查時間。
- 派完要好幾分鐘,而且每席的算法是獨立的,行為仍然正確。

補救方向:
- 計劃寫明這是已知的重複成本,或者讓 `--spec` 結果也走快取。

佐證:
- file: `scripts/lumos:48954`
- file: `scripts/lumos:48999`

## finding 3

severity: minor
blocking: 否 — 單人、依序操作的威脅模型下實際觸發機率低
引句:「底下有 `docs/*-knowledge/`(`repo_not_lumos`)。」

問題:
- 信任檢查通過到 lumos 實際跑 git 之間有一段空隙(先檢查,後執行)。
- 背景暖機行程是另一個行程,它會在稍後再次對同一個 `--repo` 路徑跑 `git -C`,這時沒有再做一次信任檢查。
- 暖機最久可跑到鎖的過期時間 900 秒,期間路徑被換成不受信任的內容也不會被重驗。

失敗情境:
- 檢查通過後,目標路徑被換掉(例如換成符號連結或重新 clone)。
- 之後的暖機行程就在沒驗過的內容上跑 git。
- 單人使用、AI 依序操作的威脅模型下,這屬於已接受的殘餘風險。

補救方向:
- 計劃的〈實務隱患〉補一句,說明檢查只管派工當下。

佐證:
- file: `scripts/lumos:48490`(`_lens_spawn_warmer`)

## 總結

最高等級是 major,共 1 條 blocking(finding 1),另 2 條 minor 不 blocking。
