severity: minor

我讀完整份 r5-snapshot.patch,並回 `/Users/enzo/harness/lumos-green-scope` 查了這些函式:`_drift_empty_tree`、`_lens_git`、`_lens_git_dl`、`_gate_event_build`、`_gov_rows_at`、`_esc_clean`、`_codeloop_read_from_ledger`。另外在 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/資安-sonnet/` 用 `python3.14 -I` 單獨執行了 `_git_bool`。沒有發現 blocker 或 major,只有三條縱深防禦類的 minor。

## 發現

1. `_git_bool` 遇到超過 4300 位的十進位設定值會丟 ValueError,沒人接
severity: minor
blocking: 否
引句:「return int(num[2:] if base == 16 else num, base) != 0」
- 攻擊路徑:
  - 誰:給使用者一個含 `.git/config` 的陌生 repo 目錄(例如 tarball)的人。
  - 從哪:使用者在該目錄跑 `lumos spec-gate` 或 `lumos drift`。
  - 送什麼:`remote.x.promisor` 設成 5000 位數字。`_GIT_INT_RE` 會放行,Python 3.14 的 `int()` 對十進位超過 4300 位會丟 ValueError。我實測 `"1"*5000` 確實丟出這個錯。
  - 拿到什麼:工具崩出 traceback。
- 方向:`_redbase_attach` 在寫留痕前崩潰,所以不寫留痕、推送閘照擋,是 fail-closed;`drift` 報告只是中斷。沒有直接越權。
- 判定:這是崩潰類縱深問題。clone 本身不會帶 `.git/config`,只有手動傳遞整個目錄才會碰到。建議在 `_git_bool` 外面接 ValueError 回 True(寧可多小心)。
- 查證:`_git_partial_clone` 的兩個呼叫端(`_redbase_branch_rows`、`_drift_born_env_err`)都沒有 try。

2. 治理帳被 git 忽略時,日常的壓提交、rebase、amend 會把自己分支的舊判綠紀錄丟掉
severity: minor
blocking: 否
引句:「head_sha 不是祖先(含提交不存在)而且是完整 repo → 丟」
- 攻擊路徑:
  - 誰:照 CLAUDE.md「推之前壓成一個」流程操作的使用者或 AI。
  - 從哪:`git rebase`、`commit --amend` 或 squash,之後再跑 `lumos spec-gate`。
  - 送什麼:改寫後的歷史。舊判綠紀錄的 `head_sha` 不再是 HEAD 的祖先,而且 repo 是完整的,`_redbase_on_branch` 判「不是祖先」就丟。
  - 拿到什麼:之前判綠過的測試,之後跑紅時照存紅燈版。存下的是實作後的內容,等於紅燈版比對基準被意外換成較弱的版本。這道守衛的防竄改保護因此少一層。
- 改動前沒有這個丟棄行為。計劃與 `_TG_LIMITS` 已把它寫成明確的取捨(「壓過或 rebase 過的分支上舊的判綠紀錄不算」),所以只報 minor。
- 這個取捨的代價限於「帳被忽略」的專案。

3. 部分複製、或判不了是不是部分複製、且帳進版控時,整個判綠觀測關掉,守衛 fail-open
severity: minor
blocking: 否
引句:「部分複製(或判不了是不是)不讀分岔點那一版的治理帳:這次的判綠觀測與去重沒有作用」
- 攻擊路徑:
  - 誰:在 `git clone --filter=blob:none` 這類常見部分複製裡工作,且帳在版控的使用者。
  - 從哪:`lumos spec-gate`,走 `_redbase_branch_rows`。
  - 送什麼:平常操作就夠。`git config` 暫時失敗或逾時回 None,也被當成「部分複製」。
  - 拿到什麼:回傳 `[]`,「判綠過的不存紅燈版」與去重都不生效,效果同第 2 條。
- 計劃已記為天花板三,終端也會印一句,所以只報 minor。
- 可評估用環境變數 `GIT_NO_LAZY_FETCH` 之類的方式禁止自動連遠端,取代整段不讀。我沒有查證它在各 git 版本的支援情況,請當建議看。

## 三類逐項

### ①提示注入
已看,無。
- 新增的 `ref` 欄位(分支名)進治理帳,先經 `_note_reread_show`(`_esc_clean`)清洗。
- `ref` 只用來跟目前分支名比對,不會印進任何派工詞或 hook 附加段。新的 stderr 訊息只印筆數。
- `_gate_event_build` 的 `ref` 欄位不會被 `_codeloop_read_from_ledger` 誤讀,因為它先篩 `gate=="code-loop"`。
- `_spec_gate_record` 傳 `extra` 時排除了 `ref`,不會覆蓋。

### ②讀寫與執行越界
已看,無。
- `_drift_empty_tree`:`hash-object -t tree --stdin` 加空輸入,沒有 `-w` 不寫物件,不套 filter,輸出經 `_LENS_SHA_RE.fullmatch`(40 或 64 位十六進位)驗證才用。
- `merge-base --is-ancestor` 與 `cat-file -e` 的 sha 參數同樣經 `_LENS_SHA_RE` 驗證,不會被當成旗標,也沒有 shell 插值。
- 部分複製時刻意不問本機沒有的提交,避免觸發自動連遠端。
- 帳被忽略時讀工作目錄那份,走 `_gov_rows_at` 的 `is_symlink`、`is_file` 檢查,不跟捷徑。
- 測試裡的 `uploadpack` 假腳本、`touch` 記號、`git clone --no-local` 都只動 `tempfile` 建的臨時目錄與自己產生的路徑,沒有外部輸入進命令,也沒有真密鑰或信箱。patch 裡唯一的網址是文件引用。
- 發現 1 屬崩潰類,不屬越界。

### ③非刻意、一步就能繞過的守衛
有發現,見上面的 2 與 3,都是 minor。
- 淺複製、判不了、逾時、超過上限一律「照留」,方向跟改動前一致,沒有新的放寬。
- 分離 HEAD 與無提交 HEAD 的處理(不比分支名、只看祖先;沒有 HEAD 就不問 git、照留)我看過,沒有一步繞過。
- 帳狀態為 `unknown` 時不過濾,等於改動前的行為,不算新洞。
- 環境變數面:這份 diff 沒有新增 `LUMOS_SKIP_*` 或讀環境變數的路徑。
- `_drift_empty_tree` 在 SHA-256 repo 算不出時退回 SHA-1 空樹,只會變成「讀不出、沒有作用」,是在 SHA-256 repo 失效,不是繞過。

最嚴重等級是 minor,blocking 共 0 條。
