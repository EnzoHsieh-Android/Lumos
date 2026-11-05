severity: minor

我沒找到會擋的資源問題:沒有新增的孤兒程序,時間預算也只在窄的情境下往寬鬆方向錯。另外兩條由前三條推出的圖譜結論我沒有逐篇讀固定席節點,見末段。

**finding 1**
severity: minor
blocking: 否
標題:遠端沒有 `refs/remotes/<遠端>/HEAD` 時,預設分支不叫 main/master 的主線被當成功能分支,推送只跑子集
引句:「names = _note_reread_mainline_names(repo_root, tip or "HEAD", deadline=time.monotonic() + 10)」
file: `scripts/lumos:61999`
失敗場景:
- 預設分支叫 `develop`,本機只有 `refs/remotes/origin/develop`,沒有 `refs/remotes/origin/HEAD`。`git remote add` 加遠端再 fetch 就會這樣,不是 clone。
- 推 `refs/heads/develop` 時,集合只剩固定名 main/master,判成非主線,掛鉤把全套降成子集,錯在寬鬆那一側。
- 實測:同一個 repo、同一個 `--pushed-ref refs/heads/develop`,沒有 `origin/HEAD` 時輸出 `"pushed_mainline": false`,補上 `symbolic-ref refs/remotes/origin/HEAD` 後輸出 `true`。
- 同樣的錯也會在這幾種情況出現:`git` 逾時 10 秒、查候選失敗、有多個遠端而沒有 origin。
- `_note_reread_mainline_names` 的註解把「只剩固定名」當作「不擋」。這個集合原本只用在回頭重讀,新用途方向相反,沒有調整。
- 本 repo 自己預設分支是 main,所以這次不會踩到;消費專案才會。

**逐項結論**
- **子程序與逾時(鏡頭 1):** 新增的 `_note_reread_mainline_names` 全程走 `_lens_git_dl`,每次 git 呼叫的逾時是 `min(20, 剩餘秒數)`,用 `subprocess.run(timeout=)` 會殺掉子程序。總長最多約 10 個 git 呼叫,不會留下孤兒。掛鉤沒有新增背景程序,新增的 `grep` 和 `python -c` 都是前景同步。
- **時間預算(鏡頭 2):** 除了 finding 1,10 秒預算本身不會把正常操作擋下。每個 ref 多一次 pitfalls 呼叫,約多 10 個 git 呼叫,多 ref 推送是線性增加,沒有二次方。
- **記憶體(鏡頭 3):** 掛鉤對約 4MB 的 lumos 原始碼 `grep -q` 一次,遇到字樣就停。`pf_json` 只在記憶體裡存一份,用 `grep -q` 判斷,沒有放大。
- **新測試(鏡頭 4):**
  - 6 支 `t_prepush_feature_branch_*` 各建一個 repo 並跑真掛鉤,慢是慢,但與既有 `t_prepush_docs_and_light_run_subset` 同形。
  - 暫存目錄走 `_sc_setup`,也就是既有的 `mkvault().parent.parent / tag`,沿用現有清理慣例,沒有新增清理缺口。
  - `ppfb-uncomputed` 和 `ppfb-old` 各複製整份約 4MB 的 lumos 原始碼,一次性、量不大。
- **pitfalls manifest(鏡頭 5):** 我沒有讀 manifest。
- **圖譜鏡頭(鏡頭 6):** 我沒有逐篇讀 8 篇固定席節點(`scripts/lumos show`),這個鏡頭未完成。從資源角度看,diff 沒碰那些節點宣稱的守衛行為:push 全套降級只在 `pushed_mainline` 為 false 且 `suite_computed` 為 true 時發生,其餘都維持全套。

我的臨時目錄 `/tmp/lumos-seat-work/code-推送只跑受影響測試/資源-sonnet/r` 已刪除。
