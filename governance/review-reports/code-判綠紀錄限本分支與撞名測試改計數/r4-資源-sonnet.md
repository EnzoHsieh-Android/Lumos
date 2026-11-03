severity: minor

資源鏡頭沒有 blocker 或 major。兩條 minor 都是修補前後行為完全相同的原有行為,不是這輪修補引入的。r4 這輪的修補(`_git_partial_clone` 改讀 `-z`、帳被忽略時直接讀工作目錄、回頭條件那支把 None 當判不了)在資源面是正向或中性。

1. 判祖先的 10 秒預算在大 repo 或帳裡有很多已消失的提交時會被吃光,這時過濾被跳過、每次規格閘多等約 10 秒。每個本機不存在的 head_sha 要問兩次 git(`merge-base` 回 128 後再 `cat-file -e`),而上限 `_REDBASE_ANC_CAP` 只數 sha、不數子程序。大 repo 沒有 commit-graph 時,每個「不是祖先」的 sha 本身就要走完整歷史。
引句:「if i >= _REDBASE_ANC_CAP or repo_kind() == "partial":」
severity: minor
blocking: 否
- 輸入一(200 個不存在的 head_sha,帳被忽略,本機 Apple git 2.39.2):走到 `merge-base`、`cat-file` 兩次子程序,約 22 ms 一次。300 筆紀錄量到 8.84 秒,預算 10 秒只差一點,慢 15% 的機器就會跳過較舊的過濾。
- 輸入二(30萬個提交的 repo,無 commit-graph,30 個不是祖先的 sha):每次約 1 秒。呼叫 `_redbase_branch_rows(…, ignored="ignored")` 耗 10.05 秒,35 筆裡 26 筆被判不了而照留,其中 21 筆是真的別條分支紀錄漏過來,stderr 有印「照舊算進來」。有 commit-graph 時同樣 30 個只要 5 秒,全部判對。
- 歸因:有證據的原有漏查。同一支腳本在修前 fe970227 量到 10.09 秒、20 筆誤留,修後 ae9c4d82 量到 10.05 秒、21 筆誤留,差別只在雜訊。
- 計劃天花板三已寫明這個限制,所以降為 minor。
- 建議:用一次 `git cat-file --batch-check` 判存在,或把預算與上限改成數子程序次數。
- 佐證:`scripts/lumos:14501`(上限檢查)與 `scripts/lumos:14509`(`cat-file` 備援)。

2. 帳被忽略時,整本工作目錄的帳一次讀進記憶體,尖峰約檔案大小的 2.2 倍;`loop` 過濾在整批讀完、全部列都建好 Counter 之後才做。
引句:「st, added = _gov_rows_at(rr, None, b'"spec-gate-', _redbase_branch_keep)」
severity: minor
blocking: 否
- 輸入:把 21 MB 的真實治理帳複製 10 份成 215 MB,呼叫 `_redbase_branch_rows(…, ignored="ignored")`。耗時約 3.3 秒、tracemalloc 尖峰 480 MB。1 份 21 MB 時 0.36 秒、48 MB。
- 真實帳(124206 列)裡 spec-gate 的列只有 233 筆、共 166 KB,正常使用走不到這個規模。
- 歸因:有證據的原有漏查。修前 3.29 秒、480 MB,修後 3.42 秒、480 MB,完全相同。
- 佐證:`scripts/lumos:61042` 的 `_gov_rows_at` 先 `read_bytes()` 再 `split(b"\n")`,兩份同時在記憶體。

## 對三問的回答

① 哪個子程序在逾時、Ctrl-C、例外時沒被收掉:沒有找到。
- `_lens_git` 與 `_git_is_shallow` 都用 `subprocess.run(timeout=…)`,逾時與 `KeyboardInterrupt` 都會 kill 自己的子程序。
- 孤兒的來源是 git 為了查不到的物件自己叫起的抓取。修後在讀分岔點那一版的帳之前,與問祖先之前,都先問 `_git_partial_clone`。
- 我拿 `file://` 複製(帶 `promisor=true` 與 `partialclonefilter` 設定、`uploadpack` 換成留記號的腳本)跑修前與修後的 `_redbase_branch_rows`,「帳不是被忽略」與「帳被忽略」兩種都是 0 次抓取。
- 但這個複製的物件其實是全有的:本機 git 2.39 的伺服器回「filtering not recognized」,等於整包複製下來。所以「沒去連遠端」主要靠程式碼路徑加作者測試的 `cat-file` 前置斷言,我沒能自己造出真正缺物件的 blobless 複製。
- `git config -z --get-regexp` 本身不會觸發抓取。
- 邊角:`repo_kind()` 回 "unknown" 時迴圈仍會去問 `merge-base`,與註解「整批不問」不完全一致。我找不到會讓 `git config` 失敗而 `merge-base` 成功的實際場景(deadline 到了兩者都回 None),所以沒標 finding。

② 哪個時間預算在大輸入或慢機器上會擋正常操作或跳過過濾:見 finding 1,只是慢與跳過過濾,不會擋下操作。
- 帳不是被忽略的一般 repo,修後每次多問一次 `git config`,量到約 30 ms(`_git_partial_clone` 0.028→0.033 秒;3215 個提交、21 MB 帳的 repo 上 `_redbase_branch_rows` 從 0.43 秒變 0.49 秒)。
- 它會變慢或卡住只在 git 本身卡住時,上限 20 秒;逾時回 None,走「不讀、印一句」,不會卡住規格閘。
- 規格閘每次還多兩次 `symbolic-ref`(留痕與判綠),各約 25 ms。

③ 哪段把整本大帳讀進記憶體或做二次方工作:見 finding 2。
- 沒有二次方:`_redbase_on_branch` 是線性,`dict.fromkeys(reversed(order))` 去重後最多問 200 個。
- 新測試的成本:`t_redbase_branch_rows_fallback_keeps` 10.4 秒、`t_git_partial_clone_keys` 6.9 秒、`t_spec_gate_redbase_green_other_branch` 15.8 秒、`t_spec_gate_redbase_green_tracked_unfiltered` 4.6 秒、`t_name_collision_scales` 5.5 秒,全過。
- 另外 `t_tq_guard_string_comma_args` 約 17.6 秒,是原有測試加兩案。
- 跑完 `TMPDIR` 裡沒有殘留。測試進程的尖峰約 1 GB 是載入 8.7 萬行測試檔造成的,與新測試無關。

## 修補驗收(repair 與 preserve 分開)

repair:
- `_git_partial_clone` 修前:裸鍵 `promisor`、`promisor = 2` 判成 False(錯),遠端名含空白且 `promisor = false` 判成 True(錯)。修後十個案例全對(也含 `yes`、`0x0`、空字串、只有 filter、只有 extensions)。
- SHA-256 repo、帳被忽略:修前 `_redbase_branch_rows` 回 0 筆並印「讀不出起點那一版」(空樹常數只對 SHA-1 有效);修後回 1 筆。
- 非忽略且部分複製:修後 0.06 秒直接回 `[]`,沒有讀分岔點那一版。

preserve:
- 帳被忽略的完整 repo、真實提交與不存在提交的過濾結果,修前修後一致。
- 帳進版控且不是部分複製時,讀法不變(0.43 秒對 0.49 秒)。

## 圖譜鏡頭(固定席筆記)

- `lumos-cli-read`、`guard-kill`、`lumos-cli-lifecycle`、`design-loop`:這輪改動沒有碰 search、guard kill、re-inject 或處置閘,沒有牽連。
- `測試假綠形態`(還原翻紅釘要配前置斷言):新測試都帶「★前置★」(淺複製建起來且回不是祖先、部分複製查不到的提交會去連遠端、同名重開後不是祖先、S79 的建構次數與串接)。`t_git_partial_clone_keys` 的「判不了」案例以「★對照★」補,成立。
- `pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`(RISK 類):這輪只在規格閘留痕與判綠事件多寫既有的 `ref` 欄位,寫入仍走 `_gate_event` 與 `_ledger_tail_needs_newline`,沒有改寫入端規則。
- 計劃的「效能」與「天花板一至六」段落與我實測的方向與數字吻合(8 秒、1 秒、10 秒)。

## 未驗範圍

- 真實 blobless 或 treeless 遠端複製(缺物件才會觸發抓取)。
- Windows 與 git 2.39 以外的版本。
- 並行寫帳(依規定不考慮)。
- 帳被忽略的專案裡 `_redbase_branch_state` 對每筆留痕讀最多 5 MB 的紅燈版,我沒有量。

我的暫存目錄已用字面路徑刪掉,只剩約 20 MB 的實驗腳本與複本(`/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/資源-sonnet/`);沒有改動 `/Users/enzo/harness/lumos-green-scope` 底下任何檔。

最嚴重等級是 minor,blocking 共 0 條。
