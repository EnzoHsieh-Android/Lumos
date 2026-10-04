severity: major

## F1 spec 沒交代手冊與說明表要跟著改,消費者看不到新旗標
severity: major
blocking: 是 不改的話實作者只改程式與 lifecycle 筆記,新旗標在所有使用者會讀的地方都不存在,「預覽後再套用」這個流程沒人知道。
引句:「lands_in:  - Systems/lumos-cli-lifecycle」
file: `/home/user/Lumos/scripts/lumos:45839`(update 子指令的 help 只有 --source/--no-pull/--allow-stale,沒有 --dry-run;deinit 的 --dry-run 在 45860 附近有 help 字串可抄)
file: `/home/user/Lumos/skills/lumos-project-notes/reference.md:114`(指令表那一列把 update 寫成 `lumos update [--source <path>] [--no-pull]`,並說「跑完記得 git commit」)
file: `/home/user/Lumos/skills/lumos-project-notes/commands/07-安裝維運.md:8`(「工具組舊了」那列只寫 `lumos update [--allow-stale]`,AI 會照這列跑,從不會先預覽)
file: `/home/user/Lumos/docs/command-reference.md:114` 與 `/home/user/Lumos/docs/指令參考.md:114`
spec 全文的 lands_in、做法、驗收條款都沒有任何一條提到 CLI help、reference.md、07-安裝維運.md、兩份指令參考。三個月後的使用者(與讀 skill 的 AI)只會照手冊跑 `lumos update`,直接套用,預覽等於沒交付。要補:help 字串、上述四處文件、一條驗收(例如 help 文字含 --dry-run 的測試)。

## F2 lifecycle 筆記已有與程式不符的舊句,spec 只說「要改」卻沒說改哪、也沒處理
severity: minor
blocking: 否 筆記錯會誤導下個 session,但不影響這次實作的正確性。
引句:「lands_in:  - Systems/lumos-cli-lifecycle」
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:124`(只寫 `update [--source --no-pull]`,沒有 --allow-stale 也沒有 --dry-run)
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:132`(「update/deinit 偵測 root==_lumos_src() 即 return 2」;程式 cmd_update 在來源 repo 走 reinject-only 回 0,第 32 行自己已承認這是新舊未同步)
spec 的 --dry-run 第 6 點(來源 repo 只預覽紀律區塊)正好踩在這句錯的描述上。實作者若照第 132 行寫,會寫出「預覽在來源 repo 回 2」的相反行為。spec 應明講:改 124 行的旗標清單,並順手修 132 行,以程式為準。

## F3 預覽結尾教的 `--no-pull` 套用,漏了 `--source`,且與預覽用的程式碼版本不同
severity: major
blocking: 是 照 spec 實作,用 `--source <路徑>` 預覽的人會被教成「`lumos update --no-pull`」,套用時改讀預設來源(`$LUMOS_HOME` 或 ~/harness/lumos-toolchain),套的不是預覽的那一版,等於回到 spec 想避免的「對不上」。
引句:「結尾印「確認後跑 `lumos update --no-pull` 套用剛才預覽的版本」」
file: `/home/user/Lumos/scripts/lumos:20495`(`_lumos_src(source)`:--source 優先於環境變數)
file: `/home/user/Lumos/scripts/lumos:20912`(cmd_update 的 source 參數)
兩個洞:(a)結尾提示必須回帶使用者實際給的 --source(以及來源是靠 $LUMOS_HOME 解析時的現值),spec 沒寫;(b)預覽是跑在「拉之前載入的舊版 lumos 程式」上,算的是新範本與新工具檔的差異;套用時使用者若用全域 lumos(symlink 指向剛被拉新的來源 clone),跑的是新版 lumos 程式,新版 `_vendor_toolchain` 或 `_reinject_*` 的邏輯可能已變,預覽用的舊邏輯與套用的新邏輯不保證一致。S2/S3 只在同一版程式內比對,抓不到這種跨版本漂移。spec 該承認這點(天花板)或讓提示說明。

## F4 「預覽不改專案」但 `git pull` 會改全域工具與來源 clone,spec 把它說成無害
severity: major
blocking: 是 使用者以為 `--dry-run` 是純唯讀,實際上它升級了整台機器共用的工具;rtb 的「規範檔要先問」精神被弱化,且使用者沒法選擇只預覽不升級(除了預先知道要加 --no-pull)。
引句:「拉的只是工具來源那份 clone,不是專案。」
file: `/home/user/Lumos/scripts/lumos:20870`(`_vendor_toolchain` 的 pull 區段)
file: `/home/user/Lumos/scripts/lumos:20710`(`_pull_source_or_abort`:`git pull --ff-only`,拉不下來時還會對髒的帳本檔做 checkout/聯集合併再 pull,是會改來源 clone 工作樹的)
file: `/home/user/Lumos/docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:128`(全域 lumos 與 skills 是 symlink 指向來源 clone,pull 即全機生效)
後果:對一台機器上所有專案而言,預覽一個專案就把全域 lumos CLI 與 user-scope skills 都換成新版,其他專案的行為隨之改變。spec 的「實務隱患」把這條寫成已排除的「對外送出」,沒有列「全域副作用」。同樣地 S1 只守專案檔與 core.hooksPath,沒守來源 clone 不被動。要嘛預覽預設不拉(用現有來源,另給 --pull 風格選項),要嘛明講並把提示文字寫成「預覽已把來源更新到某版」。另外「預覽成功回 0;拉不下來回 2」也代表預覽在離線或來源髒時會被擋,spec 只一句帶過。

## F5 bootstrap 與 init --force 也走 `_vendor_toolchain`,spec 完全沒提
severity: major
blocking: 是 同一個動作(改寫 CLAUDE.md 紀律區塊與覆蓋工具檔)有三個入口,只有 update 能預覽,rtb 的「規範檔改動要使用者同意」在 init --force 照樣被繞過;下個人會問「為什麼 init --force 沒有 --dry-run」。
引句:「做:`lumos update --dry-run`,預覽三件事」
file: `/home/user/Lumos/scripts/lumos:22035`(cmd_init 的 force / 新 vault 分支直接呼叫 `_vendor_toolchain`)
file: `/home/user/Lumos/scripts/lumos:21962`(bootstrap 的 step3 呼叫 cmd_init(force=False, no_pull=True))
file: `/home/user/Lumos/scripts/lumos:22018`(既有 vault 非 force 的 init 只走 `_do_reinject`,從專案內舊範本重算並寫回 CLAUDE.md,也是規範檔改動,沒有預覽)
spec 的「不做」只排除互動問答與部分套用,沒有說 init --force、init(既有 vault)、bootstrap 不在範圍、為什麼不在。至少要在範圍節列出這三條路與不做的理由(或約定它們的預覽就是 update --dry-run),並且 init --force 的 help 與手冊要指向預覽方法。另外把預覽寫成 `_vendor_toolchain` 內的 `dry_run` 參數還是 cmd_update 內獨立路徑,spec 沒決定;做法第 2 點只拆 `_reinject_claude_block`,第 4 點卻要複製 `_vendor_toolchain` 內的清單比對迴圈,兩份比對邏輯日後會漂移(此函式註解 18 行自己提醒過「共用避免漂移」)。

## F6 預覽的差異輸出與「套用時印的內容」互相矛盾,且驗收 S2 的措辭不可驗
severity: minor
blocking: 否 屬於可由實作者合理解決的措辭問題,但測試寫法可能分歧。
引句:「而且 應 跟接著真跑 `lumos update --no-pull` 寫進該檔的內容一致」
file: `/home/user/Lumos/scripts/lumos:20291`(套用時只印 CLAUDE.md 的前 20 行差異,AGENTS 檔不印差異)
做法第 3 點說預覽要印完整差異,但真跑只印 20 行;S2 的「一致」指檔案內容而非輸出,可是 spec 沒說測試怎麼比(把預覽的新區塊文字與真跑後檔案區塊比?還是比差異文字?)。預覽結尾教人「套用」後看到的輸出和預覽看到的又對不上(截 20 行),使用者可能以為出了差異。要明寫比的是哪個物件。

## F7 預覽路徑漏掉 `_vendored_manifest_write`、py314 升級提示與「專案內範本被改過」的情形
severity: minor
blocking: 否 屬於提示完整度與邊界,不會破壞專案檔。
引句:「補設定骨架與忽略規則、設定 hooks 路徑、同步全域 hooks——這些不改規範檔,列一行「套用時還會做」就好。」
file: `/home/user/Lumos/scripts/lumos:20897`(`_py314_upgrade` 與 `_PY314_UPGRADE_NOTICE`,只在 pre-commit 被換新時印)
file: `/home/user/Lumos/scripts/lumos:20906`(`_vendored_manifest_write` 寫指紋檔)
「其餘動作只列名」漏列 vendored manifest 的寫入與 py314 升級提示;「同步全域 hooks」(`_sync_global_from_project`)會改 ~/.claude 的全域 hooks,這是專案外的機器層副作用,只列一行名稱不夠讓使用者同意。另外目標檔若是 AGENTS.override.md 與 AGENTS.md 並存,`_agents_target` 只取前者;預覽要沿用同一函式,spec 只寫了「AGENTS.md 或 AGENTS.override.md」沒說用哪個函式決定。

## 實務隱患逐類
- 預覽與套用不一致:見 F3、F4,spec 自己列的 `--no-pull` 手法有 --source 與跨版本兩個缺口。
- 文件與手冊漂移:見 F1、F2。
- 平行路徑:見 F5。
- 金流、對外送出:無,預覽只印終端;唯一連網是 git pull(但見 F4 的全域副作用)。
- 不可逆:預覽路徑自己不寫專案檔,合理;但來源 clone 被改是不可逆的升級(F4)。
- 守衛面:不改閘判定;但 pre-commit 的 vendored 白名單與本案無關,無。

總結:最嚴重為 major,共 4 條 blocking(F1、F3、F4、F5)。
