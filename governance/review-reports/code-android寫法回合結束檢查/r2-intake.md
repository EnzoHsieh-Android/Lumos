# code-android寫法回合結束檢查 r2 收貨(2026-11-07)

範圍:修補差異 `41f1b9abc..a1456f8f6`,3427 行拆四包:甲(主程式等,916)、乙(鉤子,1193)、丙(測試,1041)、丁(筆記與型錄,277)。七席全新:正確性(甲,角色卡)、邊界(乙)、資源(甲)、合約(丙)、通才(乙丁)、資安(整份,範圍過大)、架構對齊(甲乙 2109,範圍過大)。修正關卡 r1 通過。

## 收貨三道

- 正規化:七份已正規化。
- quote-check:七份對整份 r2-repair.patch 全數錨定。
- refcheck:全對得上。

## 前輪驗收

- 第一輪 35 條:七席各自核對自己那幾條;放行指令注入與白名單佔位符繞過在資安席臨時複本照原攻擊重做,皆已堵住;資源席重跑刪大檔情境,記憶體 4GB → 375MB。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 正確性-F1 | 席位臨時 repo 設 `core.fsmonitor` 為造記號檔的腳本,`_lint_wt_git(R,"status",...)` 後記號檔出現;加 `-c core.fsmonitor=false` 不出現 | HIT |
| 資安-F1 | 席位臨時 repo:嵌套 repo 自己的 `.git/config` 設 clean filter,`lint-new --worktree --json` 後記號檔出現;`git status --ignore-submodules=all` 不出現 | HIT |
| 合約-F2 | 席位獨立 repo 造 `filter.evil.process`,只清 clean 與 required 時 status 照樣執行;測試只設 clean | HIT |
| 合約-F1 | 席位把 `if _STATE["pending"]:` 的補跑換成 pass,`-k slh_r1_spawn_window_term` 仍 3 passed(耗時 2.8→24.8 秒) | HIT |
| 通才-F1 | 讀碼:`_lint_wt_unready`、`_lint_wt_pairs` 的 err、`_lint_wt_blobs` 回 None 三條路徑都是 not-checked、rc3、`undone` 空,鉤子 `_unchecked_kind` 回 None 記 ok | HIT |
| 架構對齊-F1 | 對照 `_lint_cmd_with_files`(自稱唯一實作)與新的 `_lint_wt_argv`:相對路徑改寫同一條規則兩份 | HIT |
| 其餘 minor | 讀碼與席位附的實跑、改壞實驗 | HIT |

## 先查世界

PRIOR-ART:git 執行被打開專案設定裡的指令(同一類第二輪被打穿,依手冊查方向)——git 官方:沒有選項或環境變數能讓 git 不讀 repo 自己的 `.git/config`(`GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` 只管全域與系統層,https://git-scm.com/docs/git );`git status --ignore-submodules=all` 不看子模組的變更(https://git-scm.com/docs/git-status );`core.fsmonitor` 設成指令路徑時 status 會執行它(同頁 UNTRACKED FILES AND PERFORMANCE)。方向:對 — 黑名單關危險設定是唯一能做的層(repo 設定擋不掉),但改成單一來源:主程式只留一份「不信任 repo」的 git `-c` 參數(現有 `_SPEC_FREEZE_GIT_C` 與工作樹模式的過濾器參數合併,內容對齊鉤子 `_hookshared._GIT_UNSAFE_CONFIG`),涵蓋 core.fsmonitor、core.hooksPath、diff.external、每個過濾器的 clean/smudge/process 與 required=false,status 一律加 `--ignore-submodules=all`;天花板:git 新版若新增會執行指令的設定要跟著補,附 REVISIT。
PRIOR-ART:失效分類(同一類第二輪)——不再讓鉤子從 `undone` 的種類猜是不是刻意不查;改由 lint-new 在 JSON 明寫一個欄位標「刻意不查/沒能檢查」,鉤子照欄位記 ok 或 error(外層明示,不靠推測)。
PRIOR-ART:佔位符展開——`_lint_cmd_with_files` 既有宣告唯一實作;抽出共用核心(佔位符 → 檔案清單、相對路徑改寫),字串版與參數清單版都呼叫它。

## 分組與去向(輪內有 major,全數折入)

- 甲 git 不信任參數單一來源:正確性-F1、資安-F1、合約-F2(major)→ 見上;每種執行途徑(fsmonitor、clean、process、子 repo 的過濾器)各一支先紅測試。
- 乙 失效分類明示:通才-F1(major)→ lint-new JSON 加欄位,三條內部失敗路徑標「沒能檢查」,鉤子記 error;補先紅測試。
- 丙 佔位符展開一份:架構對齊-F1(major);架構對齊-F5(minor,用不用 shell 的開關三種寫法)→ 抽共用核心;開關收成一種傳法。
- 丁 測試缺口:合約-F1(major);合約-F3–F8(minor)→ 空窗補跑的測試斷言鉤子在遠小於內層時限內結束;其餘各補先紅斷言或改正循環驗證。
- 戊 其餘 minor:邊界-F1(OverflowError/RecursionError)、邊界-F2(鉤子 SIGINT/SIGHUP 收 lint-new)、資源-F1(改過的大 kt 先問大小,重用 `_nodehome_cat_blobs_capped`)、資源-F2(SARIF 讀取加上限)、資源-F3(暫存 SARIF 過期清理)、通才-F2(無用匯入)、通才-F3(`new_only` 參數)、架構對齊-F2–F4、合約-F9(計劃過期句)、資安-F2(ast-grep 從 PATH 找:寫進天花板,附 REVISIT,不改)。
