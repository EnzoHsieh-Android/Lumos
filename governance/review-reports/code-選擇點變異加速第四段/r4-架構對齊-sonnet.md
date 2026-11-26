severity: minor

三問都是對照 `scripts/lumos` 與這輪修補 `r4-repair.patch` 判的。這輪沒有跨層直呼,也沒有引入新字表;有兩個命名上的小不一致,結構都對。

**1. 分層與依賴方向**
- 這輪沒有新增跨層呼叫。
- `_kill_merge_note_unclean` 是新抽出的共用函式,放在 `_kill_merge_breaker` 與 `_kill_merge_trip` 之間,只被 `_kill_merge_breaker` 呼叫(原本三處重複寫的累計邏輯合成一支)。
- 它的參數是 `(mg, plat, why)`,操作 `mg.unclean`、`mg.last_unclean`,跟鄰居 `_kill_merge_trip(mg, plat, n, why)` 同形,也沒有往上呼叫 `cmd_guard_kill`。
- `_choice_merge_shape` 新增的元字元檢查放在原本的引號成對檢查之後、`--tests` 檢查之前,同一支函式內部,層次不變。
- 無 finding。

**2. 命名與錯誤處理**
- 新常數 `_CHOICE_MERGE_NO_RESULTS_WHY`、新函式 `_kill_merge_note_unclean` 都沿用 `_CHOICE_MERGE_*`、`_kill_merge_*` 前綴,錯誤處理與印字(`print(..., file=sys.stderr)`)跟鄰居一致。
- 一處不一致:`_CHOICE_MERGE_NO_RESULTS_WHY` 讓 classify 與 `_kill_merge_base` 共用字串。但同一輪在 `_CHOICE_MERGE_BASE_WHY` 新加的鍵還是手寫字面「逾時(跑到測試後掛住)」,沒用已經存在的 `_CHOICE_MERGE_HANG_WHY`。
- 既有的 `"逾時"`、`"rc 不是 0"` 等鍵本來就是字面字串,所以這只是同一輪內「抽常數」做到一半。
severity: minor
blocking: 否
引句:「_CHOICE_MERGE_BASE_WHY = {"逾時": "合併基準逾時", "逾時(跑到測試後掛住)": "合併基準逾時(跑到測試後掛住)", "rc 不是 0"」
file: `scripts/lumos:28751`(已有 `_CHOICE_MERGE_HANG_WHY` 常數)

**3. 第二種做法**
- 新增的殼層字元字表是 `"&;|<>"`。`scripts/lumos:6507` 已有 `_WIN_CMD_SPECIAL = "&|<>^%\"!"`,`scripts/lumos:29063` 也用它擋 init 路徑,所以這是另一套擋殼層字元的字表。
- 但兩者語意不同,不能直接換用:
  - `_WIN_CMD_SPECIAL` 只在 `_IS_WIN` 才套用,而且是判「測試名」合不合法。
  - 新檢查是判含 `{method}` 的那一段在 POSIX 上能不能切乾淨,需要 `;`,而 `_WIN_CMD_SPECIAL` 沒有 `;`。
- 我 grep 過,專案裡沒有現成的「POSIX 殼層元字元」常數可複用。同一個概念現在有兩張字表,卻沒有常數、也沒有註解說明為什麼跟 `_WIN_CMD_SPECIAL` 不同,這偏離了「全庫只有這兩支,各處不另寫」的慣例(6500 行註解)。
- 我不確定這算 major 還是 minor,標 ⚠ 交編排者:要是認定「同一概念兩張字表」就是第二種做法,則升 major;我判 minor 的理由是語意域不同(Windows 專用的測試名白名單 vs. 切段的邊界判斷)。建議至少抽成具名常數並註明與 `_WIN_CMD_SPECIAL` 的差別。
severity: minor
⚠
blocking: 否
引句:「if any(ch in seg for ch in "&;|<>"):   # 含 {method} 的那一段緊接殼層元字元」
file: `scripts/lumos:6507`

原因字樣常數的寫法沒有出現第二種做法:`_CHOICE_MERGE_NO_RESULTS_WHY` 與 `_CHOICE_MERGE_TRIPPED`、`_CHOICE_MERGE_HANG_WHY` 同為「模組級字串常數加行尾註解」。

不對齊共 2 條,其中 major 0 條。
