severity: minor

資源鏡頭,第 2 輪修補(修前 55da596f、修後 b76b570e)。

## 結論先講
這輪修補沒有新增會讓正常操作變慢或被擋的東西,新增的 git 呼叫也都有逾時,Ctrl-C 收得掉。上一輪兩條效能問題都修好了。有 1 條小的:同一個三次方回溯還留在另一條路徑上。

## Findings

1. **`_excluded_line` 本身仍是三次方,修補只擋了 lint 那一條入口**
severity: minor
   - blocking: 否
   - 歸因:有證據的原有漏查。修前和修後的 `_excluded_line` 沒改,兩版都一樣慢。
   - 修補在 `_lint_excluded_lines` 先數冒號,少於 2 個就不呼叫解析。但解析函式 `_excluded_line` 還有別的呼叫端:`_door_exclusions`(`scripts/lumos:8211`)。規格閘判門、推送閘重判門都會經過它,那裡沒有擋。
   - 重現輸入:實務隱患節裡有一行 `- 已排除：` 加上冒號後 N 個空白再加 `x`。
   - 修後版本跑 `_door_exclusions`,時間是 N=400 約 0.12s、N=800 約 0.94s、N=1600 約 7.5s,成長約 8 倍/倍數。照這個速度,3000 個空白約 50 秒。
   - 修前版本在同一輸入也是這個速度(`_excluded_line` 沒改)。同一類輸入丟給修前的 lint,N=2000 就跑超過 100 秒沒結束,我手動砍掉。
   - 修補的新測試 `t_lint_excluded_line_many_spaces_fast` 只測 lint。把 lint 那行改回直接呼叫 `_excluded_line` 才會紅;把保護拆掉讓 `_door_exclusions` 變慢,測試照綠。
   - 根因在 `_EXCLUDED_RE` 的 `\s*` 加 `([^:：]+?)` 加 `\s*` 互相回溯。這條規則全域規定要「同族所有路徑補測」,所以我提出。
   - 要在推送時卡住,計劃檔得有一行內部超過約 1000 個空白,正常人寫不出來。威脅模型下嚴重度低。
   - 引句:「ex = _excluded_line(ln) if len(re.findall(r"[:：]", s)) >= 2 else None」

## 三問

**① 新增 git 呼叫:有沒有逾時、Ctrl-C 收不收得掉**
- `_spec_gate_status_at` 用 `_note_text_at_rev`,走 `_lens_git`,預設逾時 20 秒。
- `subprocess.run` 在逾時或收到 KeyboardInterrupt 時都會殺子程序,所以收得掉。
- 補跑紅前查未提交改動的 `git status --porcelain --untracked-files=no` 也走 `_lens_git`。逾時會回 None,只是不印警告,不會卡住。
- 小缺口:`_spec_gate_status_at` 沒走 `_lens_git_dl` 的整體截止時間。git 整個卡死時,每份「已完成且這次推送改到的」計劃最多等 20 秒。這需要 git 本身壞掉,我不另列 finding。

**② 推送閘與 doctor S14 會不會慢到被擋**
- `_spec_gate_status_at` 只對「目前 status 是 done」的候選計劃才呼叫(`and` 短路)。
- 我在本 repo 對 293 份計劃全部呼叫一次,共 6.9 秒,每份約 24ms。這是全部都是候選的最壞情況,實際遠少於此。
- 傳入 `--output=...` 或 `a..b` 這種起點都回 None,不崩。
- doctor S14 改成合讀兩本帳(治理帳 20MB):`_spec_gate_latest_merged` 實測 0.35 秒,其中讀治理帳 0.23 秒。
- 整支 `doctor` 本身要 77 秒(profile 下 105 秒),慢在別處:`_note_shape_eval` 約 30 秒,`discover_test_methods` 約 24 秒。這些不是這輪修補造成的,S14 佔不到 1%。

**③ 二次方以上的工作**
- 已排除行三次方:lint 路徑修好了。100000 個空白的 4 種輸入都在 0.05 秒內。其他路徑見上面 finding 1。
- planned 集合移出迴圈:修好了。`_planned_ref_tokens` 對 16000 筆只要 0.012 秒;病態輸入(反引號、圍欄)也都是線性。
- 兩條新測試都實跑通過:`t_refcheck_planned_many_paths_linear` 是 1.2 秒(上限 4 秒),`t_lint_excluded_line_many_spaces_fast` 是 0.1 秒(上限 1 秒)。
- 順帶看到一個上一輪就有、這輪沒動的小事:`_git_ignored` 把所有缺檔路徑一次放進 argv。三萬條路徑會超過系統參數上限,`_lens_git` 吞掉錯誤回空集合。結果是被 git 忽略的檔案被誤報成「已不存在」。要三萬條以上缺檔路徑才會發生,不報。

## 未驗範圍
- 沒有跑全套測試和真實推送閘。
- 沒有造「多份已完成計劃加 git 卡死」的環境來實測 20 秒逾時疊加。
- 沒有測 200MB 級治理帳,只量到 20MB 是線性。

臨時目錄 `/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/資源-sonnet` 已用字面絕對路徑刪除。

最嚴重 severity:minor。blocking 共 0 條。
