severity: minor

第六輪架構對齊席的 F1、F2 都沒改程式。F1 補了一段說明,我接受;F2 只寫了不改名的理由,命名還是兩個,所以我仍列為 minor。這輪另找到 1 條 minor。我讀了 `r7-repair.patch` 的程式與筆記部分,對照了現檔,沒有重跑任何東西,也沒有改 repo。

## 第六輪 F1、F2 核對

- **F1(`_git_toplevel` 與 `_lens_repo_root`)**:這輪的處理是補說明、不併。
  - 引句:「★跟派工鏡頭的 _lens_repo_root 不共用★(代碼審 r6 架構對齊席 F1):那支走 _lens_git、不帶 _git_untrusted_c,沒給 repo 時從目前目錄找、」
  - 理由是兩支的信任前提與回傳寫法不同(一支帶不信任 repo 的 `-c` 參數,一支不帶),我接受,不再列。
- **F2(`_repo_top` 與 `_repo_root` 兩個名字)**:這輪沒改名,只在 docstring 寫理由。
  - 引句:「那幾支失敗時各有各的退法,這支失敗照回 project_root;只是命名沒對齊,不改名(改名要動既有測試與筆記的指名,換不到行為差別)。」
  - 這個理由只說改名麻煩,沒說兩個名字為什麼可以並存。命名沒對齊的狀況跟上輪相同,見下面 F2。

## ① 模組邊界

- `_git_untrusted_c` 仍留在主程式,鉤子層沿用 `_hookshared._GIT_UNSAFE_CONFIG`,這輪沒動這條邊界。
- `unchecked_kind` 與 `_hookevent` 的欄位和事件對應這輪沒碰,合約不受影響。
- `_git_status_entries` 現在是狀態表唯一出口,範圍只在出口判一次,下游不再各補一道。
  - 引句:「改在這個唯一出口整批濾,下游任何分支只看得到專案內的檔;」
  - 這條收斂是對的。
- 路徑過濾這件事,同一檔裡已經有一份判法,見下面 F1。

F1
引句:「def _rel_in_project(relpath: str, project_root: Path, top: Path | None) -> bool:」
- 新函式 `_rel_in_project` 是同一檔裡第二份「路徑在不在專案底下」的判法。
  - 現檔 `is_code_file`(`scripts/hooks/claude/check-graph-sync.py:281`)與 `is_graph_file`(`scripts/hooks/claude/check-graph-sync.py:299`)已經用 `p.resolve().relative_to(project_root.resolve())` 判這件事。
  - 新函式另用 `PurePosixPath` 逐段比前綴。
  - 兩者的前提不同:新函式要判不存在的路徑(被刪的檔、改名前的舊路徑),舊兩支吃絕對路徑。我認為差異有道理,但 docstring 只寫了「不要求這支檔存在」,沒有指名跟 `is_code_file` 的分工。
- 結構沒有跨層,只是同檔多一支同概念函式。
- ⚠ 交編排者:這算不算「第二種做法」我判不準,所以標 minor。
- 對照:`scripts/hooks/claude/check-graph-sync.py:281`
severity: minor
blocking: 否

## ② 命名與錯誤處理

- 三支 shell 掛鉤的 PATH 洗法跟 Python 入口的 `_clean_path_env` 語意一致:只留絕對項,空了退回預設。
- 失敗時兩邊都不崩,錯誤處理方式一致。
  - 引句:「PATH="${_lumos_p:-/usr/bin:/bin}"; export PATH」
- 七份找 python 的啟動器段落同步加了「不是絕對路徑就當找不到」,三支掛鉤與四支安裝腳本寫法一致,沒有分叉。
- 錯誤處理的缺口只剩命名。

F2
引句:「def _repo_top(project_root: Path) -> Path:」
- 這個函式在鉤子層的名字仍是 `_repo_top`,同目錄的 `_repo_root` 在 `scripts/hooks/claude/stop-lint-hook.py:178`、`scripts/hooks/claude/ci-status-hook.py:29`、`scripts/hooks/claude/lumos-entry-hook.py:20`。
- 同一個概念有兩個名字,這輪沒對齊,與上一輪 F2 相同。
- 這幾支的失敗退法各自不同,是獨立檔的設計。結構沒錯,只有命名不一致。
- 對照:`scripts/hooks/claude/stop-lint-hook.py:178`
severity: minor
blocking: 否

## ③ 第二種做法

- **大小上限與暫存清掃**:這輪沒有新增大小上限、讀檔或暫存清掃的程式,沒有另起一套。
- **改檔前推播入口**:這輪沒碰,沒有出現第二條路。
- **狀態表出口**:`_git_status_entries` 回傳前整批濾,刪除分支不另判。
  - 引句:「改名的兩端任一端在專案內就留。路徑照舊從 repo 根算起(同 prek 的 monorepo 做法:專案根不一定是 git 根,」
  - 範圍判定只有出口這一處,沒有留第二條路,這條對齊。
- **PATH 洗法**:shell 掛鉤的洗法是主程式 `_clean_path_env` 的 shell 版,不是另一套取代,筆記也寫成縱深與逐字複本,有守衛 `t_r6sh_path_verbatim`。
- **`_repo_top` 多開一次 git**:docstring 已說明原因是 `_wt_changed_nofilter` 是主程式的逐字複本、改回傳形狀要兩份連動。這延續上輪 F3 的同一類分流,我接受。
- 第二種做法只剩上面 F1 那一處。

不對齊共 2 條,其中會擋的 0 條
