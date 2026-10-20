severity: minor

## 資源鏡頭

白話:這批改動沒有留下孤兒程序,也沒有把整本帳讀進記憶體後做二次方工作。我只找到三處「預算管不到、或多花時間」的小問題,都不擋推送。

### 1. 核可鏈驗簽沒有逾時檢查,上限 10000 筆本身就超過 60 秒預算
severity: minor
blocking: 否

引句:「chain = _secapr_verify(new, None, pid, _secinv_today())」

- file: `scripts/lumos:9318`:`_secapr_verify` 逐筆呼叫 `_secapr_entry_status`,再呼叫 `_secapr_verify_sig`,每筆啟一個 ssh-keygen。迴圈裡沒有 `run.tick`,逾時只在驗完後的下一個 tick 才查。
- file: `scripts/lumos:9182`:`_SECAPR_MAX_ENTRIES = 10000`。
- 重現:用 `/private/tmp/claude-501/-Users-enzo-orca-workspaces-lumos-toolchain-Backend-improve/fe5c4f58-e7fb-477f-be55-0823b5438608/scratchpad/ssht/repro.py 500` 建一條「第一筆真簽、後面簽章是假的但 seq 和 prev 都接得上」的鏈,跑 `_secapr_verify`。
  - 輸出:`500 entries 3.23 s ok approval_signature_invalid`,約 6.5 毫秒一筆。
  - 外推:10000 筆約 65 秒,超過 `_SECEV_BUDGET_SEC = 60`(`scripts/lumos:8468`)。
  - 假簽章不會讓鏈斷掉,所以後面每筆都會再啟一次 ssh-keygen。
- 後果:
  - 閘門走到 `evaluation_timeout`,等於整個專案被擋。
  - `cmd_codeloop_security_approval_add` 每追加一筆都從頭重驗整條鏈,成本隨鏈長線性增加。
- 一個人使用時鏈長通常是幾十筆,所以只算 minor。內部不一致是:筆數上限對應的耗時比預算還大。

### 2. candidate 的放置天數每個 candidate 各跑一次 git log,不查預算
severity: minor
blocking: 否

引句:「rr = _secev_git(repo_root, "log", "-1", "--format=%cI", sha, "--", "*" + str(r.get("node") or ""))」

- file: `scripts/lumos:10652`:`_secev_stage_judge` 對每個 candidate 呼叫 `_secev_candidate`,再呼叫 `_secev_candidate_age`。迴圈裡沒有 tick,每次 git 有 20 秒個別逾時,總量不受 60 秒預算管。
- 開頭帶 `*` 的 pathspec 是 glob,git 無法縮小路徑範圍。revision 不是日期、路徑又不在近期歷史時,要走完整段歷史。
- 實測:
  - 本 repo 3035 個提交,查不存在的路徑要 0.11 秒(存在的路徑 0.018 秒)。
  - 按歷史長度線性外推,10 萬提交每次約 3 秒,20 個 candidate 約 60 秒。
  - 這個外推是推算,我沒有實際跑過大 repo。
- 這一步只影響 candidate 的提醒,不影響擋不擋,所以標 minor。

### 3. 沒登記資安護欄的專案每個 ref 也要花約 17 次 git 程序,而且多個 tag 不共用結果
severity: minor
blocking: 否

引句:「沒有登記痕跡回 None、不寫治理帳」

- 實測:對 Backend_improve(13110 個檔)呼叫 `_secev_evaluate(..., "HEAD", pushed_branch="feat")`,結果是 `no_registration`。
  - 先 `ls-tree -r` 整棵樹。
  - 再做約 10 次 remote、symbolic-ref、rev-parse 的主線探測。
  - 最後 3 次 `git grep -l`,分別是 sha 一次、主線一次、FLAG_TAG 一次,每次約 0.085 秒。
  - 合計約 0.5 秒。
- 「沒登記的專案一字不多」只對輸出成立,CPU 和程序數不是零成本。
- file: `scripts/hooks/pre-push:625`:tag 分支在逐 ref 迴圈裡每個 ref 各叫一次 `code-loop check --security-only`,ref 之間沒有快取。`git push --tags` 一次推 100 個 tag,就是 100 次完整判定。
- 預檢可以調整:先做便宜的 `grep` 預檢,再建整棵樹和探測主線。

## 其他必答項

- **pitfalls manifest**:
  - `scripts/lumos:11110` 是 `with open(wt, "ab") as fh:`,誤報。
  - `scripts/lumos:11167` 是 `with open(path, "ab") as fh:`,誤報。
  - 兩處都有 with,handle 一定會關。
- **子程序收乾淨**:
  - ssh-keygen 用 `subprocess.run(..., timeout=20)`,逾時或 Ctrl-C 都會被 kill。暫時目錄用 `TemporaryDirectory`。
  - git 都走 `_secev_git`,逾時 20 秒。
  - 新增程式碼沒有啟動掃描工具或 k6。
- **記憶體與二次方**:
  - 沒有看到二次方工作。
  - blob 讀取有單檔上限(`_nodehome_cat_blobs_capped`、`_SECEV_FILE_MAX` 16MB)。
  - 核可鏈解析上限 10000 筆。
- **中斷就停**:
  - `scripts/hooks/pre-push:628` 的 tag 分支(`--security-only`)在 `|| sec_rc=$?` 之後立刻接 `pp_stop_if_signaled "$sec_rc" ...`,在判斷是否擋下之前,並已列入 `中斷就停:code-loop|安全證據判定(--security-only)` 清單。
  - 分支走的證據閘在 `code-loop check` 裡,已被原有的 `pp_stop_if_signaled "$cl_rc" "code-loop check"` 涵蓋。
  - 刪除 ref 在 `scripts/hooks/pre-push:466` 就 `continue` 跳過,不會進證據閘。
  - 所以所有新增的呼叫點都有接上。
- **圖譜鏡頭**:這次沒有附固定席節點(鏡頭計算超時),也沒有「這次新增的殘留」段,無法逐條判斷,如實標註。

最嚴重 severity: minor,blocking 共 0 條。
