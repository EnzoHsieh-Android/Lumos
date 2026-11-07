severity: minor

這輪合約席核對了第五輪 F1–F4,都修好了,抽查的改壞實驗也都翻紅。新找到 1 條 minor,不擋。實驗全在 `git clone --shared` 的臨時複本做,都在前景或通知後收齊,repo 沒動。

**第五輪 F1–F4 在複本照當時的改壞重做**
- **F1 FIFO 守衛**:在 `scripts/lumos` 的 `_impact_wt_nofilter` 做兩種改壞,`t_r5imp_fifo_guard` 都紅,並以逾時收場、沒有卡住整套。
  - 拿掉 pick 迴圈的 `not _st.S_ISREG(...)`:3 條斷言紅。
  - 把補看首行那段的 `elif _st.S_ISREG(...)` 改成 `else`:3 條斷言紅。
- **F2 結尾 CR**:拿掉 `or p.endswith("\r")`,`t_r5imp_cr_name` 紅。
- **F3 刪除檔模式**:把 `head_mode.get(p)` 換成寫死 `"100644"`,`t_r5imp_deleted_exec_mode` 紅(3 條)。
- **F4 + 在前**:`_impact_line_delta` 順序還原,`t_r5query_plus_first` 紅;說明文字改回 difflib,`t_r5query_help_text` 紅。

**鏡頭 1:r5 新測試與守衛的改壞**
這輪新測試名稱是 `t_r5*`,派工詞寫的 `_r2_` 是筆誤,我照 `t_r5*` 抽查。
- `_wt_changed_nofilter` 的旗標判斷,兩份同步改壞:
  - `S` 或小寫改成只認 `S`:`t_r5wt_skip_worktree_unchanged` 紅。
  - 改成只認小寫:`t_r5wt_*` 6 條斷言紅。
  - 拿掉 `if p in hold: continue`:`t_r5wt_*` 6 條斷言紅。
  - 只改主程式、不改鉤子:3 條斷言紅(sparse 與 skip-worktree 兩支都紅)。
- `_clean_path_env` 規則:
  - 拿掉 `isabs`:4 條斷言紅。
  - 全被拿掉時不退 `os.defpath`:4 條斷言紅。
  - 主程式 `main()` 不呼叫:`t_r5path_hooks_verbatim` 與 `t_r5path_attack` 都紅。
  - `check-graph-sync` 入口不呼叫:`t_r5path_hooks_verbatim` 與 `t_r5path_attack` 都紅。
  - `dispatch-lens-hook` 入口不呼叫:`t_r5path_hooks_verbatim` 紅,`t_r5path_attack` 綠。攻擊測試只跑三支鉤子,其餘五支靠語法樹檢查,所以這樣合理。
- 子目錄與取根(`t_r5sub_*`):
  - `_repo_top` 恆回專案根:紅。
  - 活檔不接 `top`:紅。
  - `graph_touched` 改回專案根:紅。
  - `cmd_impact_diff` 不看 `wt_nofilter`:紅(對照組)。
  - `cmd_impact_diff` 恆 False:紅。
- `in_top` 改壞:`ok()` 預設改在 `repo_root` 跑,`t_r5arch` 與 `t_r4wt_*` 都紅。
- `_impact_hunk_query` 提早停:不提早停紅,停太早(`n > 3000`)紅。
- 沒翻紅、但我判斷不算 finding 的改壞:
  - `n += len(out[-1]) + 1` 拿掉 `+ 1` 照綠。`join` 長度只會大於等於總和,所以結果等價。
  - `n > 4000` 改 `n >= 4000` 照綠。只有行長加一的總和剛好等於 4000 才會少 1 個字,沒有實際場景。
  - `src_files` 改回專案根照綠。`_impact_missing` 並沒有用到這個參數,所以等價。
  - `_git_toplevel` 已是根時回 git 的路徑而不是 `repo_root`,照綠。只影響路徑寫法,看不出實際後果。
  - 拿掉 `pfx.returncode` 判斷照綠。pfx 失敗而 top 成功不會發生。

**鏡頭 2:逐字比對加語法樹檢查**
在 `impact-hook.py` 做 6 種改壞,`t_r5path_hooks_verbatim` 全紅:
- 定義改成註解、呼叫留著。
- 別名 `_c()` 呼叫。
- 刪本地定義、改從共用模組匯入。
- 呼叫包進 `try`。
- 呼叫放進條件式。
- 用 `globals().get('_clean_path_env', …)()` 呼叫。

「從 PATH 找 lumos」那一類由 r4 的 `t_r4hook_relative_lumos` 管,這輪沒動它。

**鏡頭 3:計劃、依據來源、家節點與程式對照**
沒有發現筆記與程式相反。
- 〈依據來源〉新增三列的函式與測試名都存在。
- `_clean_path_env` 在主程式 `main()` 與八支鉤子入口第一句,數量吻合。
- POSIX 對 PATH 空項的原文與 `os.get_exec_path` 的說法對得上。
- 「git 2.39 實測穩定」:本機 `git --version` 是 2.39.2。
- 計劃第 8 條、`_git_toplevel` 的回傳語意、`in_top` 的呼叫範圍,都與程式一致。

**F1 子目錄專案裡,兄弟專案刪掉程式碼檔會被誤點名,新做的 `other/b.py` 夾具沒人用**
引句:「旁邊 other/b.py 不屬於這個專案;都提交 → (repo 根, sub)。」
- 場景:用 `_r5sub_mono` 做 monorepo(專案根是 `sub/`),只刪 `other/b.py`,走真鉤子入口 `check-graph-sync.py`。
- 結果:輸出「提醒:工作樹上有 1 個程式碼檔還沒提交,知識筆記沒有跟著動:other/b.py(已刪除)」。
- 對照:改 `other/b.py` 或新增 `other/c.py` 都不點名,因為活檔會經 `is_code_file` 檢查是否在專案底下。
- 原因:引自現檔 `scripts/hooks/claude/check-graph-sync.py:546`,`_entry_is_code` 的已刪除分支只看副檔名或 HEAD 首行,不判在不在專案底下。這是舊行,這輪沒改,但 r5/r6 把狀態表路徑改成從 repo 根算之後,monorepo 子專案才真的走到這條。
- 測試缺口:夾具專門造了 `other/b.py`,`t_r5sub_hook_e2e` 卻只測 `sub/` 內的改動,兄弟專案的刪除沒有案例。
- 後果:Codex 版的收工擋停會因別的專案刪檔,對這個專案擋一次。
severity: minor
blocking: 否

總結:最嚴重是子目錄專案的已刪除分支沒判專案範圍(舊行、測試沒覆蓋),會擋 0 條;r5 的 F1–F4 都已修好,抽查的非等價改壞全部翻紅。

**暫存清理**
- 臨時目錄 `/tmp/lumos-seat-work/code-android寫法回合結束檢查/合約-sonnet` 已用字面路徑刪除。
- 我手跑探針留下的 `gctl-run-tukc86i5` 已刪。
- 批次改壞時其他測試紅留下的 `gctl-run-*`,我沒有逐一記路徑。系統暫存裡也有別的會談的同名目錄,我無法證明哪些是我的,依規定沒有批次刪,留給編排者處理。
