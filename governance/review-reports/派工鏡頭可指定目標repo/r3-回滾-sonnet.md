severity: major

## 已讀範圍
計劃全文與這輪改動。對照了 lens-repo 的 `scripts/hooks/claude/dispatch-lens-hook.py`、`scripts/lumos` 的 `cmd_dispatch_lens_spec`、`_lens_emit_with_extra`、`_trusted_lumos`、`_sync_global_hooks`。

做了一個實驗:舊 lumos 收 `<短sha>:docs/…/計劃.md --arch-target --json`,結果 rc=2、標準輸出為空、只有 stderr「計劃筆記不存在」。我沒有另外做新 lumos 的實驗,因為新程式碼還沒寫出來。實驗用 lens-repo 唯讀跑,沒有留暫存。

severity: major
blocking: 是 — 新舊錯開時看不出來,而設計審的整個目的就是讓席位拿到節點,結果會跟今晚一樣靜默放空
引句:「舊版會當成工作樹路徑找不到、照舊不附」
問題:r2 版有「版本錯開看得出來」一條,要求附加段印來源行,並要求範本寫明「沒有來源行就是掛鉤舊」。這輪整條拿掉,沒有補任何替代。新做法讓三樣東西各自分發:範本在 skills(`install.sh`)、掛鉤在 `~/.claude/hooks`(`lumos update`)、lumos 在 PATH 或 `~/harness`(`git pull`)。三樣沒有規定先後。
具體失敗情境:
- 先更新 skills,編排者開始寫 `LUMOS-SPEC: <sha>:<路徑>`,但 lumos 還是舊的。舊 lumos 回 rc2、stdout 為空,掛鉤放行,派工詞什麼都沒附,也沒有說明行,因為舊 lumos 不給失敗代碼。
- 編排者看不到掛鉤改寫後的派工詞,席位也不知道少了什麼,十幾席再次全部沒拿到固定席節點,跟緣起寫的當晚事故一樣。
- 做法 5 的 note 記 `spec_rev` 也救不了,因為量的是新掛鉤,舊掛鉤不記。
建議:補回一個新舊都看得見的訊號,或在計劃寫明升級順序(lumos、掛鉤、範本)並用機械檢查守住。
佐證:file: `lens-repo/scripts/hooks/claude/dispatch-lens-hook.py:509`(rc2 加空輸出本來就是掛鉤判「舊 lumos」的現成訊號,但只用在選配旗標重叫)、file: `lens-repo/scripts/lumos:48689`

severity: major
blocking: 是 — 回退步驟照做回不到原狀,而且不會被發現
引句:「最後一個跑 update 的專案會把它的掛鉤寫進」
問題:計劃把「掛鉤全域一份、lumos 每專案一份」當前提,但實際不是。
- 掛鉤執行的 lumos 是 `_trusted_lumos()` 找到的全域那支:PATH 的 `lumos`,其次 `$LUMOS_HOME`,其次 `~/harness/lumos-toolchain`。它不是會談專案 vendored 的 `scripts/lumos`。本機 `which lumos` 是 `~/.local/bin/lumos`。
- `lumos update` 只用該專案 vendored 的來源覆蓋 `~/.claude/hooks/` 的掛鉤,`_sync_global_hooks` 用 `shutil.copy2` 無條件覆寫,沒有版本比較。
- 所以回退步驟 2 到 3(每個專案 update、核對掛鉤指紋)只退了掛鉤,實際執行的全域 lumos 沒被點名要退。
具體失敗情境:
- 還原提交後,各專案 update 讓掛鉤退回舊版,但 `~/harness/lumos-toolchain` 沒 `git pull`,於是舊掛鉤配新 lumos。這個組合在成功路徑勉強能用,失敗說明行不會出現,指紋核對卻顯示「已回到原狀」。
- 反過來,任何還在新分支或舊工作樹的專案之後跑 `lumos update` 或 `install`,會把已退掉的掛鉤寫回新版,即使最後一個跑的專案是對的也一樣。步驟 3「等每個專案都更新過」沒有機制,也沒有「掛鉤版本大於來源就不覆寫」的保護。
建議:回退清單加「全域 lumos 也要退並核對」,並說明誰最後跑 update 誰贏的競態。
佐證:file: `lens-repo/scripts/lumos:24961`(`_sync_global_hooks` 的無條件 copy2)、file: `lens-repo/scripts/lumos:24890`(`_GLOBAL_CLAUDE_HOOKS`)、file: `lens-repo/scripts/hooks/claude/dispatch-lens-hook.py`(檔內的「只執行可信來源的 lumos」一段,及 `_find_lumos_script`)

severity: minor
blocking: 否 — 只影響過渡期的說明行
引句:「掛鉤自己不解析、不跑 git」
問題:新說明行靠 lumos 印的失敗代碼。舊掛鉤配新 lumos 時,`_fail_note` 因為 `rng` 為空直接回空字串,`LENS_FAIL_REASONS` 也不認 `spec_rev_missing`,所以失敗時舊掛鉤靜默放行,只是少了說明,不會壞。這點計劃沒寫。「失敗代碼表擴充後掛鉤認不認得」只有一半答案:新掛鉤認,舊掛鉤不認也不報錯。
具體失敗情境:使用者只更新 lumos 沒更新掛鉤,提交編號寫法能用,但輸入錯的提交編號沒有任何提示。
建議:把這個過渡行為寫進計劃,別只寫新掛鉤配舊 lumos 那一半。

severity: minor
blocking: 否 — 影響範圍窄
引句:「這三個沿用的代碼在現在的工作樹那條路也印」
問題:工作樹那條路改成印 `{"lens_fail": …}`,但目前 stdout 為空加 rc2 被掛鉤當成「舊 lumos」訊號。對選配旗標重叫那段(`_opt_flags` 重叫)來說這是好事:新 lumos 失敗時不再被誤判成舊版而白跑第二次。反過來,舊 lumos 配 `--arch-target` 的設計審失敗仍會跑兩次 lumos,各自吃預算,可能把第二次的預算耗在已知必敗的呼叫上。
具體失敗情境:舊 lumos、`--arch-target`、錯路徑。這是效能與預算問題,不是正確性問題。
建議:計劃註明即可。

severity: minor
blocking: 否 — 屬於配套補強
引句:「掛鉤事件 note 在用到提交編號寫法時記」
問題:回退後事件帳留著 `spec_rev` 與 `spec_rev <代碼>` 的 note 字串。回退節沒寫這些舊 note 要不要處理,也沒寫有沒有讀端會解析 note。計劃只說 REVISIT 2026-12-15 要數次數,回退後那條 REVISIT 與 RETIRE-IF 會因為一起還原或沒還原而指向不存在的機制。
具體失敗情境:回退提交只還原程式和筆記,2026-12-15 到期時 doctor 要人去數一個已不存在的欄位。
建議:回退步驟加一條「撤掉 REVISIT 與 RETIRE-IF 或標已撤回」,並確認事件帳的 note 沒有被讀端當固定格式解析。

節的結論:
- 進行中迴圈:已寫「手動貼固定席」,但前提是編排者知道漏附,這點回到第一條 finding。
- 工作樹路徑寫法在新舊兩邊行為不變:已讀,無 finding。
- `LUMOS-SPEC:` 標記文法 `(\S+)` 兩邊不變:已讀,無 finding。

總結:最高等級 major,blocking 共 2 條(版本錯開無訊號,以及回退漏掉全域 lumos 加掛鉤被覆寫的競態)。
