severity: major

整合/知識同步席,r1 後以程式碼與圖譜對照。最高等級 major,blocking 2 條,其餘 minor。

**Finding 1**
severity: major
blocking: 是 — 新口的信任檢查擋不住「自己擁有、內容不可信」的目標,而派工詞正是可被第三方文字注入的來源;這是計劃自己指出的新差別,防線卻只做了一半。
引句:「路徑、它的父目錄、它的 git 資料夾都屬於自己、都不是別人可寫」
問題:這個檢查只看目錄的擁有者與權限位。`repo_not_lumos` 只要求 `docs/*-knowledge/` 存在,攻擊者的 repo 自帶這個資料夾即可。檢查也沒看 `.git/config` 檔本身的權限,只看目錄。計劃把「自己擁有但內容不可信」歸入殘餘風險,理由是「會談目錄也一樣擋不住」。但會談目錄是使用者自己選的,派工詞不是。審第三方投稿時,編排者常把對方的文字貼進派工詞。
具體失敗情境:被審文字裡有一行 `LUMOS-REPO: /Users/enzo/Downloads/submission`,那是自己解壓的 repo,`.git/config` 設了 `core.fsmonitor`。重複標記只會被拒,不會擋住單一一行。掛鉤檢查通過後,lumos 在那裡跑 `git diff` 之類會刷新索引的指令,就執行了對方的指令。`_lens_git` 沒有 `-c core.fsmonitor=false`。檢查與使用之間也有 TOCTOU:先 realpath 與 stat,稍後 lumos 才重新解析路徑。
建議:加一道出身限制。例如要求目標與會談 repo 同一個 git common dir(工作樹),或在使用者維護的白名單裡。跨 repo 的示範情境才走白名單。同時讓 lumos 的 git 呼叫帶 `-c core.fsmonitor=false`。
file: `scripts/lumos:47386`(`_lens_git` 無硬化旗標)、`scripts/hooks/claude/dispatch-lens-hook.py:422`(repo 目前只來自環境變數或 cwd)

**Finding 2**
severity: major
blocking: 是 — 做法 8 照字面執行,會把仍然有效的決策標成作廢,圖譜的決策查詢會說謊。
引句:「裡同一條 WHY,都標」
問題:
- 我 grep 過,「標記行加 repo 路徑」只出現在派工鏡頭跨repo不再靜默的 WHY 行。
- Systems/codex-harness 的對應 WHY 行(第 42 行)的 `[不選:]` 只有「讀 lumos 的錯誤輸出原文」。它沒有被推翻的那一格,所以計劃說它是「同一條 WHY」不成立。
- 舊計劃的 WHY 行也一樣。它的主決策(算不出範圍時改附說明行)、`_fail_note` 的消毒設計、錯誤輸出原文零輸出的不選,新計劃都沒推翻,甚至沿用並擴充。
- `[status:superseded]` 是整行屬性,標下去會連活的決策一起作廢。
具體失敗情境:下一個 session 用 `lumos decisions` 查「為什麼說明行只准固定字彙」,得到「已被取代」,可能放寬自由文字轉述。
建議:把被推翻的那一格拆成獨立一行再標作廢,其餘整行保留。codex-harness 那行不標作廢,改成補述新增的原因代碼。codex-harness 第 42 行還列舉了六個 lens_fail 代碼,新增的 `spec_missing` 等三個要同步補進去。
file: `docs/lumos-toolchain-knowledge/Systems/codex-harness.md:42`、`docs/lumos-toolchain-knowledge/Projects/派工鏡頭跨repo不再靜默_計劃.md:16`

**Finding 3**
severity: minor
blocking: 否 — 屬文字同步缺口,實作時 grep 補齊即可。但驗收條款沒有任何一條守住手冊與範本。
引句:「那一行旁邊寫明:工作目錄不是會談目錄時」
問題:做法 6 只點名 `templates.md` 與 code-loop 的派工說明,但斷言舊行為的句子遠不止這些。
- `templates.md:109`、`:116`、`:163`、`:335`。第 116 行講「從開在 B 的會談派席」,第 109 行講終點不寫 HEAD。
- `lumos-design-loop/SKILL.md:26`、`lumos-design-loop/reference.md:513`。
- `lumos-code-loop/SKILL.md:32`(「掛鉤在會談的專案目錄解讀」)、`lumos-code-loop/reference.md:587`。
- `lumos-project-notes/commands/05-設計審查迴圈.md:31`。
- `lumos-project-notes/commands/06-代碼審與推送.md` 第 29、30、38 行。
- `lumos-project-notes/reference.md:83`。
- `Systems/design-loop.md:52`。
- 掛鉤自己的 `FAIL_NOTE`(第 62 行)與檔頭 docstring。

另有兩個措辭問題:
- 條件句「工作目錄不是會談目錄時才寫」對編排者無法判斷,它看不到 `CLAUDE_PROJECT_DIR`。昨晚十幾席全沒附就是這個盲點。範本應該無條件寫成「寫你的工作 repo 根」。
- 同一份 `templates.md` 也講 Codex 編排。新句子必須標明 `LUMOS-REPO:` 只對 Claude 路徑有效。

file: `skills/lumos-design-loop/templates.md:116`、`skills/lumos-code-loop/SKILL.md:32`、`skills/lumos-project-notes/commands/06-代碼審與推送.md:29`

**Finding 4**
severity: minor
blocking: 否 — 落點只列一篇,會留下過期的現況句與沒人看守的雙胞胎函式。
引句:「信任檢查仿同一支掛鉤裡」
問題:`lands_in` 只有 Systems/codex-harness,下列各處也要落地。
- `Systems/hook信任邊界` 是信任檢查的單源,`_trusted_lumos` 的註解就指向它。新增的資料夾版信任函式、「路徑來自派工詞」這條新邊界,都該記在那裡。否則下次有人改逐字複本 `_ok`,不會知道旁邊有個必須同步判斷的兄弟。
- `Projects/派工鏡頭注入_計劃` 有兩處會過期:第 28 行 KEY 寫的 `repo=CLAUDE_PROJECT_DIR→cwd`,以及第 110 行〈標記文法定死〉。第 117 行「失敗一律放行、預設靜默」要加註新的說明行來源。
- `Systems/anchor-integrity` 的第六個錨點段,錨它的理由是「改寫派工詞」。現在掛鉤還會依派工詞裡的路徑去執行 git,威脅面變了,該補一句。

file: `docs/lumos-toolchain-knowledge/Systems/hook信任邊界.md:7`(about_code 只有 scripts/lumos)、`docs/lumos-toolchain-knowledge/Systems/anchor-integrity.md:66`

**Finding 5**
severity: minor
blocking: 否 — 新舊錯開的窗口是真的,但後果是安靜地退回舊行為。
引句:「還原提交即回到只用會談目錄;已寫進範本的」
問題:回退段只講還原。真正常見的是前進時的版本錯開。
- skills 靠 symlink 立即生效,範本一更新,編排者就開始寫 `LUMOS-REPO:`。
- 掛鉤複本要重跑 `lumos install` 才更新。複本共有三份:`~/.claude/hooks`、`~/.codex/hooks`、消費專案 `scripts/hooks/claude`(`_VENDORED_TREE_FILES`),守衛測試只看來源樹。
- 舊掛鉤不認這行,直接在會談目錄算,而且不附任何說明。若會談目錄裡剛好有同名但較舊的計劃,就會悄悄附上錯的節點,席位還以為是對的。

建議:新掛鉤與範本之間要有可偵測的信號,例如 `doctor` 或 enforcement 比對安裝複本的指紋。至少在手冊寫明「更新後要重跑 install」。

file: `scripts/lumos:24890`(`_GLOBAL_CLAUDE_HOOKS`)、`scripts/lumos:23881`

**Finding 6**
severity: minor
blocking: 否 — 條款綁定缺口會讓設計審處置閘擋住,但修法簡單。
引句:「當同一份派工詞有兩行」
問題:
- S5 沒有 `[test:]`。處置閘第五步的 fail 條件含「任一條款未標」,見 `scripts/lumos:26109`。S5 還涵蓋路徑含空白,這是實質行為。
- S6 與 S2 共用 `t_dispatch_lens_hook_repo_rejected`,一支測試承擔兩條條款。
- S4 寫「行為應與現在相同」,又要求說明行多一條繞法。既有的 `t_dispatch_lens_hook_fail_reason_notice` 斷言「lumos impact --diff」在輸出裡,改措辭時要同步調整,否則 S4 自己矛盾。
- 沒有條款涵蓋 symlink 路徑、`gitdir:` 檔的相對路徑、`commondir`。

file: `scripts/test_lumos.py:42122`

**Finding 7**
severity: minor
blocking: 否 — 超時時只會被外層砍掉並退回放行,不會出錯,但會浪費預算且無說明。
引句:「擋下的路徑一次 git 都不跑」
問題:通過檢查後,掛鉤自己要跑 `git -C <路徑> rev-parse --show-toplevel`,計劃沒有指定 timeout。
- `_BUDGET_START` 要到第一次呼叫 `_inner_budget` 才開始計時(第 106 行)。新增的 git 呼叫若排在 `_lens_timeout()` 之前,它花掉的時間不會被扣除。
- 這正是註解裡記載過的「內層加起來超過天花板」舊 bug。例如 git 卡 20 秒,之後的 `--deadline` 與外層 timeout 最多再給 54 秒,總和超過外層 60 秒。
- 外層 SIGKILL 時不附說明、不記事件。

建議:給這次 git 呼叫明確 timeout,並在它之前先起算預算。
file: `scripts/hooks/claude/dispatch-lens-hook.py:86`、`scripts/hooks/claude/dispatch-lens-hook.py:106`

已讀,無 finding:
- 逐字複本守衛:`_trusted_lumos` 的區塊提取、注入框區塊、`t_trusted_lumos_rejects_untrusted_locations`。計劃另寫資料夾版、不改 `_ok`,做法正確。只要新函式不放進起訖標記區塊內就不會踩線。
- Codex SubagentStart 路徑:同一支檔但不讀派工詞,不受影響。計劃第 7 點不納入範圍合理。
- 錨點清單與 baseline:計劃已提醒要 `anchor approve`。
- hook 事件格式:`PreToolUse` 的 `updatedInput` 輸出形狀不變。
- 前掃的 9 條修正:未推翻,其中 p3 與 p5 屬實。

總結:最高等級 major,共 2 條 blocking(finding 1、2),另 5 條 minor 不阻擋。
