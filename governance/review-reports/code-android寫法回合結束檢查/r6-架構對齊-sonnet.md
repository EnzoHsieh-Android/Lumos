severity: minor

第五輪架構對齊席 F1 到 F3 都已處理:F1、F2 改了程式並有測試,F3 用註解寫明理由、沒改程式。這輪另找到 2 條小項。只讀了 `r6-repair.patch`,對照了現檔的 `scripts/lumos` 和鉤子,沒有重跑任何東西,也沒有改 repo。

## 第五輪 F1 到 F3 核對

- **F1(取 repo 根兩份)已修。**
  - 取根收成 `_git_toplevel`。
  - 舊的 `_lint_wt_toplevel` 已刪,全 repo 搜不到殘留引用。
  - lint-new、`_impact_wt_nofilter`、`cmd_impact_diff` 三處都改呼叫它。
  - 鉤子端的 `_wt_changed_nofilter` 是逐字複本、匯入不到,自己取根,符合 `Systems/hook信任邊界` 的既有分流。
- **F2(重綁 `run`)已修。**
  - 改名 `in_top`,兩份複本都改了。
  - 守衛 `t_r5arch_no_run_rebind` 有檢查「不重綁」與「直接呼叫 `run` 只有一次」。
  - 守衛的 `gitfn` 清單也補了 `in_top`。
- **F3(總量記帳、HEAD 模式表)用理由回應,沒改程式。**
  - 補的註解說明:`_nodehome_cat_blobs_capped` 的 `max_total_bytes` 只算上一個提交那一版的宣告大小,工作樹那一版是 `open()` 直接讀。
  - 另一條說明:`_wt_changed_nofilter` 的 `head` 表只留物件編號、不留模式,改回傳形狀要連動兩份複本。
  - 我接受這兩個理由,沒有再列。

## ① 模組邊界

`_git_untrusted_c` 留在主程式、鉤子層不跟著用,結構沒變。鉤子層仍用自己的 `_hookshared._GIT_UNSAFE_CONFIG`。`unchecked_kind` 這輪沒動,`_hookevent.KINDS` 的合約不受影響。

`_clean_path_env` 在主程式 `main()` 與八支鉤子入口各一份,逐字複本,另有守衛 `t_r5path_hooks_verbatim`。我用 grep 對過,有入口的鉤子全部都有,漏的只有兩個模組檔 `_hookshared.py`、`_hookevent.py`,它們沒有入口。這個分流跟既有的 `_trusted_lumos`、`_wt_changed_nofilter` 複本一致,不算第二種做法。

引句:「# ★下面這支是主程式 scripts/lumos 同名函式的逐字複本★(安全邏輯,照 [[Systems/hook信任邊界]];守衛 t_r5path_hooks_verbatim)」

F1
引句:「def _git_toplevel(repo_root):」
- 這條是新引入的第二份「取 repo 根」,不是跨層。
  - `scripts/lumos:69132` 的 `_lens_repo_root(repo)` 本來就做同一件事:用 `_lens_git` 跑 `rev-parse --show-toplevel`,回 Path 或 None。
  - `_git_toplevel` 的差別有兩點:走 `_lint_wt_git`,多帶 `_git_untrusted_c` 的 `-c` 參數;已經是根時回原路徑寫法。
  - 補丁說「取 repo 根收成 `_git_toplevel`」,只收了 lint-new 與影響分析這兩處。
  - `scripts/lumos` 內另有至少八處行內的 `rev-parse --show-toplevel`,例如 69874、69953。
- ⚠ 交編排者:`-c` 參數那一點算不算足以另起一支,我判不準,所以標 minor。
- 結構沒有跨層,是在同一個檔裡多一支同義函式。
- 對照:`scripts/lumos:69132`
severity: minor
blocking: 否

## ② 命名與錯誤處理

`in_top` 的命名清楚,`ok(..., here=False)` 的分派也一眼看得懂。引句:「def in_top(*a, data=None):」

`_git_toplevel` 失敗回 None,各呼叫端自己決定退回或整次放棄,這個語意在補丁註解裡寫清楚了。

引句:「t, pfx = ok("rev-parse", "--show-toplevel", here=True), ok("rev-parse", "--show-prefix", here=True)」

F2
引句:「def _repo_top(project_root: Path) -> Path:」
- 「取 repo 根」在鉤子層的名字和失敗行為不統一。
  - `check-graph-sync.py` 新增 `_repo_top`,失敗時退回 `project_root`。
  - 同目錄的 `stop-lint-hook.py:178`、`ci-status-hook.py:29`、`lumos-entry-hook.py:20` 叫 `_repo_root`。
  - 主程式那邊叫 `_git_toplevel`、失敗回 None。
- 同一個概念在鉤子層出現 `_repo_top` 與 `_repo_root` 兩個名字,失敗行為也不同。
- 這幾支是獨立檔、各有各的呼叫情境,結構沒錯,只是命名沒對齊。
- 對照:`scripts/hooks/claude/stop-lint-hook.py:178`
severity: minor
blocking: 否

## ③ 第二種做法

- **大小上限**:
  - 仍重用 `_nodehome_cat_sizes` 與 `_nodehome_cat_blobs_capped`。
  - 工作樹那一版自記帳的理由這輪有寫明。
  - 引句:「為什麼不用 _nodehome_cat_blobs_capped 既有的 max_total_bytes」
- **暫存清掃**:這輪沒有新增,沒有另起一套。
- **改檔前推播入口**:這輪沒碰,沒有出現第二條路。
- **`_impact_hunk_query` 改成邊累積邊停**:兩條路徑仍共用這一支,沒有分叉。
- **`_clean_path_env` 與既有的逐支解析**:
  - 它跟 `_lint_wt_resolve_tool`、`_trusted_lumos` 的 `_ok` 並存。
  - 補丁和 `Systems/hook信任邊界` 都明寫是縱深,不是第二套取代。

不對齊共 2 條,其中會擋的 0 條
