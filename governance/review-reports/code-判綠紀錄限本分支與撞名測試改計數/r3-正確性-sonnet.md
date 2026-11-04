severity: major

第 3 輪正確性席報告(修補範圍 6e10ae5b 到 fe970227,即 d4bbaaea 加帳本提交)。

先講結論:這輪的程式修補本身站得住。部分複製改成認三個設定、帳被忽略時不讀分岔點、`_note_reread_branch` 取分支名,我各挑輸入跑過,行為都對。問題有兩類:一是新共用函式的測試只釘住一側,二是驗收條款與筆記跟程式對不上。

## Findings

1. 回頭條件那支 `_drift_born_env_err` 改用 `_git_partial_clone` 後,「只寫 promisor 的部分複製」在回頭條件這側沒有任何測試守著
severity: major
   blocking: 是
   引句:「if _git_partial_clone(root):」
   - 失敗場景:把 `_drift_born_env_err` 改回只看 `extensions.partialClone`(也就是回到 r2 的錯)。`t_drift_born_unknown` 與整個 `-k drift_born` 仍全綠。
   - 原因:`scripts/test_lumos.py` 裡含 partialClone 的測試只有兩處,`t_drift_born_unknown` 只寫 `extensions.partialClone`,`t_redbase_branch_rows_fallback_keeps` 只測規格閘紅燈版那側。promisor 只出現在後者。
   - 最小重現(已當場跑過,跑完已還原,`cmp` 與原檔一致):
     - 把 `scripts/lumos` 的 `_drift_born_env_err` 那兩行換成 `pc = _lens_git(root, "config", "--get", "extensions.partialClone")`,再判 `pc is not None and pc.returncode == 0 and pc.stdout.strip()`。
     - 跑 `python3.14 scripts/test_lumos.py -k drift_born`,結果 26 passed, 0 failed。
     - 跑 `-k redbase`,結果 194 passed, 0 failed。
   - 實際影響:用 `git clone --filter=blob:none` 做出來的真實部分複製,設定只有 `remote.origin.promisor=true` 與 `remote.origin.partialclonefilter=blob:none`。回頭條件那支會把它當完整 repo 去讀舊版本,git 會自動連遠端抓,而且逾時殺不到抓取的子程序。這正是 r2 邊界席與資源席要修的錯。
   - 行為案例 G1 第二列寫「改壞 J6 紅」。我自己的把回頭條件那支改回舊寫法的改壞全綠,那條只守得住「整段拿掉」。
   - 歸因:有證據的修復回歸。
     - 修前 6e10ae5b:`_drift_born_env_err` 對真實 promisor-only 複製(`/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/正確性-sonnet/pcl`)回 `None`。
     - 修後 fe970227:回「partial clone 讀舊版本會去網路抓,不讀」。
     - 行為變了,但這條行為沒有測試。

2. `_git_partial_clone` 解析 `git config --get-regexp` 輸出的方式,遇到兩種輸入會判錯
severity: minor
   blocking: 否
   引句:「key, _sp, val = ln.strip().partition(" ")」
   - (a) 遠端名稱含空白而且 `promisor = false` 時,誤判成部分複製。
     - 輸入:`[remote "my remote"]` 加 `promisor = false`。
     - git 輸出 `remote.my remote.promisor false`,`partition(" ")` 切成 key=`remote.my`、val=`remote.promisor false`。
     - `key.endswith(".promisor")` 不成立,走到 `if val:` 回 True。
     - 效果:過濾整批停用(照留),`_drift_born_env_err` 回 partial。
     - 修前 6e10ae5b 回「還沒有任何提交」(不算部分複製,是對的),修後回 partial。這一條是修復造成的新誤判。
   - (b) 沒寫值的布林 `[remote "origin"] promisor`,漏判。
     - 這種寫法 git 當 true(`git config --type=bool` 實測印 true),但 `--get-regexp` 只印 `remote.origin.promisor`(沒有空白)。
     - val 為空,被 `val not in (...)` 跳過,回 False。
     - 實際影響:規格閘會為判祖先去連遠端。
     - 修前也是判成非部分複製,屬原有漏查。
   - 兩種輸入都要手改 `.git/config` 才會出現,所以給 minor。
   - 附帶的改壞:拿掉 `.promisor` 的值檢查(`promisor=false` 也當部分複製),`-k redbase_branch_rows_fallback` 仍全綠(19 passed)。這個值檢查沒有測試守著。
   - 附帶的改壞:正則只留 promisor 或只留 partialclonefilter 其中一個,測試也都綠。因為真實 clone 兩個都寫(我實測 git 2.39.2 的 `clone --filter` 寫了這兩個、沒有寫 `extensions.partialclone`),這項無實際影響,不另算 finding。

3. 驗收條款 S8 宣稱的行為,程式沒做、綁定測試也沒驗
severity: major
   blocking: 是
   引句:「- [S8] 當淺複製、部分複製、HEAD 解不出、過了截止時間或超過上限而判不了,或判不了治理帳有沒有被忽略時,過濾應把那幾筆紀錄照舊算進來並印一句說明 [test:t_redbase_branch_rows_fallback_keeps]」
   - 失敗場景:「HEAD 解不出」(還沒有提交)與「判不了治理帳有沒有被忽略」兩種情況,程式不印任何說明。
   - 最小重現(已跑):
     - 建一個 `git checkout --orphan` 的 repo,帳裡一筆沒有 ref、head_sha 為 `cd*20` 的判綠。
     - 呼叫 `_redbase_branch_rows(W, "甲", "ignored", 10)`,回 1 筆、stderr 為 `''`。
     - 呼叫 `_redbase_branch_rows(W, "甲", "unknown", 10)`,回 1 筆、stderr 為 `''`。
   - 原因:
     - `_redbase_on_branch` 對 head 為 None 的列用 `sha=None`,走 `v = ... else True`,不算進 `unsure`。
     - `ignored != "ignored"` 時根本不進過濾。
   - 計劃自己的做法 1 e 也寫「b 以外因為判不了而留下的(淺複製、部分複製、git 叫不起來、過了截止時間、超過上限)合計 N 筆」才印,清單裡沒有 HEAD 解不出。所以條款和計劃本文互相矛盾。
   - 綁定測試的缺口:`t_redbase_branch_rows_fallback_keeps` 的分離 HEAD 與無提交 HEAD 案例都沒看 `out`。條款被改寫成保證這兩種會印,測試卻不會因為不印而紅。
   - 歸因:有證據的修復回歸。
     - 修前條款(r3-repair-review.patch 的 `-` 行):「當淺複製、git 叫不起來、過了截止時間或超過上限而判不了時」,與程式一致。
     - 修後把「部分複製、HEAD 解不出、判不了治理帳有沒有被忽略」加進來,但程式行為前後相同,都不印。
     - 要嘛條款收窄,要嘛補印與補斷言。

4. 回頭條件計劃的兩句話已經跟程式相反,這次修補沒同步改
severity: minor
   blocking: 否
   引句:「if _git_partial_clone(root):」
   - 佐證:file: `docs/lumos-toolchain-knowledge/Projects/回頭條件寫下時就成立_計劃.md:51` 寫「partial clone(`git config extensions.partialClone` 有值」。
   - 佐證:file: `docs/lumos-toolchain-knowledge/Projects/回頭條件寫下時就成立_計劃.md:101` 寫「partial clone 只看 `extensions.partialClone`,不看各 remote 的 `promisor` 設定(…git 開 partial clone 時兩個都會寫)」。
   - 與事實的差距:
     - 程式現在三個設定都看。
     - 「兩個都會寫」我實測 git 2.39.2 不成立(只寫後兩個)。
   - 這兩句是「已知限制」類敘述,讀的人會以為回頭條件那側仍會漏掉 promisor-only。程式優先,所以不會做錯事,給 minor。
   - 歸因:有證據的修復回歸。修前該句為真(6e10ae5b 的 `_drift_born_env_err` 只看 `extensions.partialClone`),這次修補 d4bbaaea 的筆記 diff 沒動這個檔,現在為假。

## 三問(附證據)

① 原問題修復效果的行為證據
- G1 repair(只寫 promisor 的部分複製要認得、不去連遠端):
  - input:`pc2` 只有 promisor 與 partialclonefilter,uploadpack 換成留記號的腳本。
  - expected:`shas == ["ab"*20]` 且沒有記號檔。
  - case_source:`t_redbase_branch_rows_fallback_keeps`「只寫 promisor 的部分複製」。
  - before:6e10ae5b 沒有此案例。修前碼的行為,我用改壞 D 重現(正則只留 `extensions.partialclone`):該斷言紅,結果 `([], True)`。
  - after:綠(19 passed)。
  - 歸因:修復有效,測試有牙。
- G2 repair(帳被忽略時不算分岔點):
  - input:`rows(d, 30)` 預設 `ignored="ignored"`,並替換 `_lens_fork_point` 計次。
  - expected:`forks == []`。
  - before:改壞 E(還原成 `if head:`)時紅,`forks` 長度為 1。
  - after:綠。
  - 歸因:有牙。
- G3 repair(分離 HEAD 與無提交 HEAD):
  - 改壞 F(拿掉分支名過濾)時 4 條斷言紅。
  - 分離與無提交的案例結果本身就是前置證明(能不能留下 `ev(h0,"other")` 取決於分支名取得與否)。
  - 這兩案例不驗印出,見 finding 3。

② 修補處的正常、錯誤、相鄰呼叫路徑
- 規格閘紅燈版這側:
  - 完整 repo、淺複製、舊式 `extensions.partialClone`、新式 promisor、截止時間用完、上限 200 都成立。
  - `_lens_git_dl` 回 None 時,`_git_partial_clone` 回 None,`repo_kind` 當 unknown 而照留。
  - 帳被忽略時 `_redbase_attach` 先問一次 `_gov_ledger_ignored`,再呼叫 `_redbase_branch_rows`,順序與參數都對得上。
- 回頭條件那側:
  - `_lens_git_dl(deadline=None)` 的逾時等於 `_lens_git` 預設 20 秒,git 失敗回 None 仍當「不是部分複製」,與修前一致。
  - 只有 promisor-only 的結果從「讀舊版本」變成「不讀」,這是預期的方向,但沒測試(finding 1),也沒更新筆記(finding 4)。
- 邊界:
  - 錯誤型別的帳欄位:ref 或 head_sha 不是字串時,`isinstance` 與 `_LENS_SHA_RE.fullmatch` 擋住。
  - 同名 tag:取分支名借 `_note_reread_branch`,不用 `--short`,行為對。
  - ref 寫入端與讀取端用同一支函式,清洗一致。
- 不扣分:帳被忽略但分岔點那一版其實有帳(例如分支自己 `git rm --cached` 帳),現在不再減分岔點那版。這要手動才會出現,我沒有給出具體失敗輸入,不標。

③ 新發現的同一案例,修前與修後(`pcl` 為真實 `clone --filter=blob:none`)

| 案例 | 修前 6e10ae5b | 修後 fe970227 | 歸因 |
|---|---|---|---|
| `pcl` 的 `_drift_born_env_err` | None | partial | 預期的修復,但無測試(finding 1) |
| 遠端名含空白、`promisor=false` | 還沒有任何提交(非部分複製) | partial | 修復造成的新誤判(finding 2a) |
| 沒寫值的 `promisor` | 非部分複製 | 非部分複製 | 原有漏查(finding 2b) |
| orphan 且 `ignored` 的過濾 | 修前沒有這個過濾 | 不印說明 | 條款與程式不一致(finding 3) |

## 圖譜鏡頭(固定席節點)

- `Systems/lumos-cli-read`(search 排除 superseded):不影響,這份 diff 不碰 search。
- `Systems/測試假綠形態`(還原翻紅釘需要前置斷言):
  - 部分複製、同名重開(`★前置★` 檢查祖先 rc 為 1)、撞名效能測試(`★前置★` 檢查索引有建、串接有走)都有前置。
  - 例外是回頭條件那側,新行為完全沒有釘子(finding 1)。這正是該合約要擋的那類缺口。
- `Systems/pitfalls-code-loop`、`design-loop`、`guard-kill`、`loop-convergence-recording`、`lumos-cli-lifecycle`:不影響,這份 diff 不碰 pitfalls 分級、設計審處置閘、guard kill、收斂記帳、re-inject。
- `Systems/reversibility-governance-ledger`:
  - 治理帳事件多寫既有欄位 `ref`,屬新增欄位。
  - 舊讀者不讀 `ref`(我 grep 過 `_spec_gate_gov_index`,沒有讀端用它),舊紀錄沒有 ref 也能被新讀端處理,新舊互讀沒有問題。
- `Systems/規格閘`:已同步,條款 S8 與程式不一致(finding 3)。
- 超出上限只列名的節點:未逐條核對。

## 未驗範圍與其他觀察

- 沒驗真正的 blobless 或 treeless 遠端複製(我用本機 `file://` 的 `--filter` clone,server 不認過濾但設定照樣寫入)。
- 沒驗 Windows、時鐘倒退,也沒驗大 repo 沒有 commit-graph 的耗時。
- 我沒看 r1 與 r2 的席報告。
- 併發類題目依派工規定判範圍外。
- 小觀察,不計 finding:`t_redbase_branch_rows_fallback_keeps` 的淺複製與部分複製案例還在傳 `_t.monotonic() + 30`,但這個參數現在是秒數,傳進去變成極大的預算,實際仍被單次 20 秒上限擋住。沒有失敗輸入,所以只在這裡提。
- 我借用原 repo 做改壞驗證(改 `scripts/lumos` 後立即用 `cmp` 與備份還原),`git status --short scripts` 為空。暫存目錄在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/正確性-sonnet/`,留給編排者收貨後刪。

最嚴重等級是 major,blocking 共 2 條。
