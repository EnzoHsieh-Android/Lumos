severity: major

(以下對照的是 clone-314 的程式碼;spec 引句取自凍結審材 最低python版本改3-14-r1.md)

## 四問

**1. 分層與依賴方向**
- 大體一致:安裝入口維持「薄殼只叫起 lumos」(`install.sh:5` `exec python3 .../scripts/lumos install`、`scripts/install-hooks.sh:6`、`get.sh:45`),版本判斷收進 lumos 單一源,方向與現況同(邏輯在 Python、薄殼不含邏輯)。merge-claude-settings 自己加檢查、退出碼 2,也與它現有的擋下寫法同(`scripts/merge-claude-settings.py:35` 印「擋下:…」後 `sys.exit(2)`)。
- 新共用檔放 `scripts/hooks/`:目錄整夾複製(`scripts/lumos:17180` `_VENDORED_TREE_DIRS`),精確名單另登記(`:17185` `_VENDORED_TREE_FILES`),spec 已寫要一起改。bash 端還有第三處名單:`scripts/hooks/pre-commit:161`、`scripts/hooks/post-commit:69` 的 `scripts/hooks/*` 萬用字元,新檔落在萬用字元內、不用改;此處對齊,無問題。
- 跨層直呼:無。

**2. 命名與錯誤處理**
- `LUMOS_PYTHON`:專案的環境變數一律 `LUMOS_` 前綴(`LUMOS_SKIP_*`、`LUMOS_HOME`、`LUMOS_TTY`),前綴一致。但語意不同:`LUMOS_SKIP_*` 是「跳過某道閘、會留帳」(`scripts/lumos:24366` 一帶,`_gate_event_or_warn` `:985`),`LUMOS_PYTHON` 是選直譯器,不是跳過,不屬同族,不算不一致。
- 回傳碼:lumos 與 merge 擋下回 2(對照 `merge-claude-settings.py:35`)、git 掛鉤擋下回 1,與現有分工一致。
- 說明寫法:現有掛鉤缺環境印「提醒:這台機器找不到 …」放行(`pre-commit:54`、`pre-push:119`);spec 改成「擋下並講清楚」,是裁定過的行為改變,不是風格分歧。
- 見 F2:重跑防無窮迴圈的環境變數沒命名。

**3. 第二種做法**
- 共用 shell 檔被三支掛鉤 source:`scripts/hooks/` 底下現在沒有任何被 source 的檔(grep `source `/`. ` 在 `scripts/hooks/*`、`scripts/*.sh`、`install.sh`、`get.sh` 皆 0 筆);三支掛鉤各自內嵌 `command -v python3 || command -v python`(`pre-commit:50`、`pre-push:70`、`post-commit:95`),「多支掛鉤要維持同一套判定」現況的做法是各自複製加漂移守衛測試(`post-commit:19` 「判定邏輯與 pre-commit 完全對齊」;`t_precommit_whitelist_drift_guard` `scripts/test_lumos.py:3729`)。spec 引入「掛鉤 source 共用檔」這個新機制,鄰居已有同功能做法 → 見 F1。
- lumos 開頭「找不到就用別的直譯器重跑自己」(os.execv / Windows 子行程):現有 lumos 內沒有 os.execv(grep 0 筆),是新機制,但鄰居沒有同功能(沒有任何入口會重跑自己),不算第二種做法。
- `LUMOS_PYTHON` 逃生口:鄰居沒有「換直譯器」的逃生口,`LUMOS_SKIP_*` 是另一種功能;不算第二種。
- Windows 直譯器挑選:`slim/install.py:202` `_pick_windows_interpreter` 只試 `python3`/`python`(且註解自稱與 install.sh/install.ps1「三處一致」),spec 讓 lumos 內另有 `py -3.14` 候選。slim 明確不在範圍,且 spec 說 `lumos.cmd` 不動,所以兩套 Windows 挑法並存是有意的;⚠ 交編排者:這是「兩份 Windows 候選清單」而 spec 的同步測試只守 shell↔lumos 兩份,不含 slim。

**4. 落點**
- lands_in 五篇:`lumos-cli-lifecycle`(講 install/vendored/bootstrap,合理)、`bound-tests-gate`(about_code 有 pre-push 與 ci.yml,合理)、`codex-harness`(about_code 有 merge-claude-settings 與 scripts/lumos,合理)、`測試假綠形態`(是改一條 REVISIT,不是「現況落在哪」,勉強)、`每支檔有家`(是規則節點,about_code 只有 scripts/lumos、pre-commit、pre-push;spec 裡沒有任何要寫進它的現況,見 F3)。
- 新開一篇管共用清單:合理。現有節點沒有一篇專管「挑直譯器」(Systems 下 grep 直譯/python/入口 只有 slim 系兩篇,管的是精簡版)。但 `每支檔有家` 排除「原封不動的工具自裝檔」(`Systems/每支檔有家.md:25`),新共用檔進自裝名單後不強制要家,新開節點是自願的;仍該開,理由是要放 RETIRE-IF 與候選順序的決策脈絡。

## Findings

## F1 掛鉤共用判定改成 source 共用檔,是新機制;現有做法是各掛鉤複製加漂移測試
severity: major
blocking: 是 — 引入第二種「多掛鉤共用判定」的做法,鄰居已有同功能做法,不對齊就是專案裡兩種並存。
引句:「`scripts/hooks/` 底下一支新的共用檔(shell,只給 git 掛鉤 source)」
file: `scripts/hooks/post-commit:19`
1. 現況:pre-commit(`:50`)、pre-push(`:70`)、post-commit(`:95`)各自內嵌判定,對齊靠註解與漂移守衛測試(`scripts/test_lumos.py:3729` `t_precommit_whitelist_drift_guard`、`post-commit:19`「判定邏輯與 pre-commit 完全對齊」)。
2. spec 是第一個讓掛鉤 source 別的檔的設計,且 spec 自己另外還要一支測試守「shell↔Python 兩份順序」,等於同時有「共用檔」與「漂移測試」兩種同步手段。
3. ⚠ 判不準:三支掛鉤加上要印同一大段說明,內嵌複製三份確實比共用檔笨;且掛鉤整夾複製,共用檔會跟著走。若編排者認為這是有意的、值得的新機制,降為 minor,但要在新系統筆記寫「為什麼不沿用複製加漂移測試」(PRIOR-ART 一行目前只講世界做法、沒對照專案內做法)。

## F2 重跑防無窮迴圈的環境變數沒命名,也沒對照專案既有測試接縫命名
severity: minor
blocking: 否 — 命名與筆記精度,不影響結構。
引句:「重跑前設一個環境變數,重跑後的程序若還是舊版就直接報錯,不會無限重跑」
file: `scripts/lumos:24366`
1. 專案內環境變數都有 `LUMOS_` 前綴且在測試/筆記裡有名字(`LUMOS_TTY`、`LUMOS_SIMULATE_WINDOWS` 等);此變數 spec 未命名,[S2] 的測試也無從指定。
2. 影響:實作者自己取名,與 `LUMOS_PYTHON` 並存兩個環境變數卻只文件化一個。

## F3 lands_in 的「每支檔有家」沒有對應的寫回內容
severity: minor
blocking: 否 — 落點精度,錯了只是多寫或漏寫一篇筆記。
引句:「lands_in」下的 Systems/每支檔有家(見 spec 前置欄位,凍結審材未逐字含此行;以下為 ⚠ 說明)
file: `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:25`
1. 該節點管的是「哪些檔需要家」的判定;新共用檔屬「原封不動的工具自裝檔」,不需要家(同節點 `:25` 排除清單),spec 內容也未要求改該判定。
2. ⚠ 引句欄位說明:lands_in 在計劃檔 frontmatter(clone 內 Projects/最低Python版本改3.14_計劃.md:10-15),凍結審材未見;需編排者確認凍結檔是否含,不含則此條改列不成立。
3. `測試假綠形態` 同理只是改一條 REVISIT(spec 第 9 點),不是現況落點,建議歸「連帶更新」而不是 lands_in。

不對齊共 3 條,其中 major 1 條

最高等級 major,blocking 共 1 條
