severity: minor

我沒找到 blocker 或 major。我在 `342cf099` 的 `scripts/lumos` 上對大輸入實測,上一輪兩條效能問題都守住了,新增的 git 呼叫也都有上限。以下有三條 finding。

## 上一輪兩條效能問題的驗收

1. **已排除行三次方回溯:已守住,而且守得更廣。**
   - 前置冒號計數搬進了 `_excluded_line` 本身,`_EXCLUDED_RE` 在 `scripts/lumos` 裡只剩這一個呼叫點(另一處只是拿 `.pattern` 算指紋)。
   - 實測 10 萬個空白的輸入,耗時都在 0.02 秒內。輸入有四種:一個冒號、兩個冒號、沒有冒號、10 萬個冒號。
   - 兩個冒號以上時,這條正則一定能匹配成功,所以不會再回溯。
   - 歸因:有證據的修復。
2. **`planned` 集合重算:已守住。**
   - `_planned_ref_tokens` 現在自己去掉結尾斜線。
   - doctor 在迴圈外只算一次,`_refcheck_scan` 也是只算一次。
   - 這個正則只從反引號起頭開始比對,是線性的。

## 逐條資源問題

- **新增 git 呼叫的逾時與 Ctrl-C**
  - `_is_git_worktree`、`_dirty_non_bookkeeping`(走 `_fix_git_z` 到 `_lens_git`)、`_note_text_at_rev` 都有 `timeout=20`。逾時會回 None,不會卡住。
  - `_range_base` 的 `merge-base` 用的是沒有 timeout 的 `subprocess.run`。這支函式本來就沒有逾時,不是這輪新增的。它是本機的 merge-base,不是網路呼叫,Ctrl-C 時 `subprocess.run` 會自己收掉子行程。
- **`_dirty_non_bookkeeping(untracked=True)`**
  - 我造了 9 萬個未追蹤檔,`git status --untracked-files=normal` 只花 0.03 秒,沒有問題。
- **`_summary_write_shape_check`**
  - 用 `_is_git_worktree`(一次 `rev-parse`)取代了第一個 `_nodehome_list`(整個 repo 的 `ls-files -s`),git 呼叫比修前少。
- **doctor S14 讀兩本帳**
  - 我在真實的 20MB 治理帳上跑 `_spec_gate_latest_merged`,耗時 0.24 秒,跑兩次結果一致。
  - 這輪只是在讀到 None 時多印一行,呼叫次數沒變。

## 發現

1. **推送閘對每份 done 候選計劃都重算一次 merge-base,而且連不需要的也算**
   - 位置:`scripts/lumos` 裡 `_spec_gate_push_scan` 的 `done = (...)` 與 `_spec_gate_status_at`。
   - 問題:`_spec_gate_status_at` 現在對三點範圍會跑 `git merge-base`(同一個範圍、結果每次相同,卻沒快取),再加一次 `git show`。
   - 另外 `done` 是對每份 status 為 done 的候選計劃先算好的,但只有 `_live` 為真的才會用到。不 live 的 done 計劃也白跑這兩個 git 呼叫。
   - 實測:真實圖譜有 162 份 done 計劃,用範圍 `HEAD~30...HEAD` 逐份呼叫 `_spec_gate_status_at`,共 12.8 秒,約每份 79 毫秒,其中 merge-base 約 41 毫秒。
   - 實際影響:只有推送範圍同時含很多 done 計劃才會明顯變慢,一般推送不會。
   - 歸因:修前版本沒有 merge-base,這份額外成本是這輪修補帶來的(有證據的修復回歸),但量級很小。

severity: minor
blocking: 否

引句:「base = _range_base(rr, git_range) or ""     # 三點範圍取 merge-base,同 _pq_push_remind(代碼審 r2 G4)」

2. **否定句掃描在單行有大量否定字眼時是二次方(修補沒動它,修前就有)**
   - 位置:`_ns_negation_hits` 對每個命中都呼叫 `_ns_neg_segment`、`_ns_neg_cond_open`,各自從頭掃或切片。
   - 重現:一行重複「尚無,」4000 次,修後耗時 1.38 秒;16000 次是 21.1 秒。
   - 修前版本在同樣輸入下是 1.42 秒和 22.2 秒。「只要尚無就」重複的輸入,修後 15.5 秒、修前 21.2 秒。
   - 新增的 `_ns_neg_cond_paired` 沒有讓它變得更糟。
   - 觸發條件很極端:單行要有數千個否定字眼,真實筆記不會有。
   - 歸因:有證據的原有漏查。

severity: minor
blocking: 否

引句:「if _ns_neg_cond_open(masked[a:m.start()]) or _ns_neg_cond_paired(masked[a:m.start()], masked[m.end():b]):」

3. **補跑紅警告在 git 逾時時靜默不警告**
   - 位置:`_dirty_non_bookkeeping`。逾時時 `_fix_git_z` 回 None,被 `or []` 吞掉,沒有警告也沒有任何提示。
   - 影響:這是個只提醒不擋的警告,逾時最多讓使用者少看到一行。修前是 `st is not None and ...`,行為相同,所以不算回歸。
   - 歸因:未判定(沒有修前修後差異,屬原有行為)。

severity: minor
blocking: 否

引句:「dirty = [x for x in (_fix_git_z(rr, "status", "--porcelain", "-z", "--untracked-files=" + ("normal" if untracked else "no")) or [])」

## 三個必答問題

1. **原問題的修復效果有何行為證據?** 已排除行的回溯與 `planned` 集合重算,我都用大輸入量過,結果在上面「驗收」一節。我沒有替每個修補寫還原後翻紅的測試,也沒跑 `test_lumos.py`。
2. **修補處的正常、錯誤與相鄰路徑是否仍成立?**
   - 資源面成立:`_is_git_worktree` 的 None、True、False 三種結果都導向有限的路徑,git 逾時不會卡住。
   - `cmd_cochange_check` 的空字串 `--diff` 在進入任何 git 呼叫之前就回 2。
3. **新發現的同一案例在修前、修後各是什麼結果?** 只有上面第 1、2 條。第 1 條修前沒有 merge-base 成本,修後有。第 2 條修前修後相同。

## 未驗範圍

- 沒驗 `_ns_neg_cond_paired` 與 Unicode 標點分類的語意正確性,那是別的席的鏡頭。
- 沒在真實的大型 push 閘上量端到端耗時。
- 沒跑 doctor 的完整 S14 渲染,只量了它讀帳的那一段函式。

我造的暫存目錄已用字面絕對路徑刪掉。

最嚴重 severity:minor,blocking 共 0 條。
