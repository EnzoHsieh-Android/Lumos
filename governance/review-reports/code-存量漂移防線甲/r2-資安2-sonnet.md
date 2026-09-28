severity: clean

## F0 逐類檢查紀錄(無 finding,列出已看過什麼)

severity: clean
blocking: 否 — 沒有可利用的洞

1. **不可信輸入流到危險操作**(命令/路徑/git 選項注入;考卷 JSON、表態檔、設定檔、檔名):
   - `_nodehome_cat_blobs` 的 `git cat-file --batch` 呼叫全程用 `subprocess.run([...], input=...)` 傳 argv 清單,沒有 `shell=True`,repo_root 與 specs 都不會被 shell 重新解讀。
     引句:「r = _sp.run(["git", "-C", str(repo_root), "cat-file", "--batch"],」
     file: `scripts/lumos:249`(凍結 diff 行號;對照 clone-ns 樹上同函式)
   - `_note_status_seq` 新抽出的 `git log --follow ... -z rng -- p` 呼叫在 pathspec 前一律有 `--` 分隔,`p` 只會是先前 `git log --name-only` 列出的真實受管檔案路徑,不是外部字串直接拼接,不構成 git 選項注入(`p` 不可能以 `-` 開頭被當旗標,因為 `--` 已經把後面全部當 pathspec)。
     引句:「lg = _ns_git(repo_root, "log", "--follow", "--format=%H", "--name-only", "-z", rng, "--", p)」
   - `_drift_exam_load` 這輪新加了考卷形狀先驗(`isinstance(qs, list)`、每題 `isinstance(q, dict)`),`_drift_exam_one` 也新加了 `note`/`line` 缺欄位先擋,兩處都是邊界驗證的正向強化(對應 python-idioms R15),不是新洞,是把原本「純量或字串清單直接丟例外」的情況收斂成早退。
     引句:「if not isinstance(qs, list) or not all(isinstance(q, dict) for q in qs):」
   - `cat-file --batch` 的 `timeout` 參數這輪改成可傳入(`timeout=max(1, timeout)`),來源是內部算出的 `deadline - time.monotonic()`,不是任何 CLI/檔案內容可以直接控制的值,`max(1, …)` 也擋掉了負值/零值直接傳給 `subprocess.run(timeout=…)` 的情況;沒有注入或繞過路徑,只影響效能預算,不進本報告(屬 DoS/資源類,依派工單不報)。
   - `_GUARD_TAIL_MARKS_RE = re.compile(r"(?:\s*\[[A-Za-z_-]+:[^\]]*\])*\s*")` 檢查過:每個 `\[...\]` 區塊靠字面 `[`/`]` 界定,彼此不重疊、沒有可回溯的歧義子模式(不是 `(a+)+` 這種型態),用在單行、長度有界的筆記文字上,量測不出 ReDoS 路徑,判斷:⚠ 推論(沒有實測輸入讓它變慢,只是結構性判斷),不升等。

2. **登入與權限**:這份 diff 沒有任何認證/授權相關程式碼(沒有 token 驗證、沒有角色判斷),已看,無。

3. **密鑰與個資**:diff 裡沒有寫死密碼、API key,`secrets.token_hex` 用途是產生表態記錄的識別碼(不是憑證),沒有把任何敏感值印進 log 或治理帳(`_gate_event_or_warn` 只帶路徑與筆數,不帶筆記全文)。已看,無。

4. **加密與傳輸**:這份 diff 不涉及任何網路呼叫或憑證儲存。已看,無。

5. **執行邊界**(推送前掛鉤與 CI、`exam --repo` 指向陌生 repo):
   - `exam` 路徑上所有新舊 git 呼叫(`_note_status_seq`、`_drift_tree_env`、`_drift_vault_rel`、`_nodehome_cat_blobs`)都只讀(`log`/`diff --name-status`/`cat-file --batch`/`rev-list`),沒有任何一處對 `--repo` 指定的目錄下寫入、`commit`、`reset`、`checkout`,符合派工單「只准唯讀」的限制。已看,無。
   - `dre.add_argument("--probes", …)` 這輪整條移除(連同 `cmd_drift_exam` 的 `probes` 參數),是移掉一個「拿檔案內容覆蓋考試素材」的輸入面,屬於縮小攻擊面,不是新增風險。
     引句:「return cmd_drift_exam(args.dr_exam, args.dr_repo, at=args.dr_at,」
   - `_drift_gate_doctor_lines` 讀 `.lumos/config.json` 沿用既有的「`is_file()` 且非 symlink 才讀」寫法,是沿用既有模式(筆記形狀擋/筆記內容審同款),不是這輪新增的防護面,也沒有變弱。
   - Systems 筆記裡新加的 RULE(`drift_check.gate` 讀被推送頂端提交自己的 `.lumos/config.json`,推的人可以在同一個提交把它改成 `off` 放過自己)是**沿用既有程式行為的紀錄**,不是這份 diff 新引入的程式改動——比對 diff,`if mode == "off": … return 0` 那段是既有 context,沒有 `+`/`-`;這輪唯一的變動是把上一輪代碼審(r1 資安席)已經點出的這個限制寫成帶 `[since:][retire:]` 的 RULE 並存查,屬於 CLAUDE.md 要求的「承認風險要附回頭看的條件」,不是本輪新開的洞,也不構成能繞過「範圍外」權限的提升(能動這個提交的人本來就有推送權限,只是讓一個提醒性質的閘失效,閘本身設計上就寫明「只防疏忽、不防存心繞過」,跟同專案其他閘一致)。
     引句:「開關讀被推送頂端提交裡的 .lumos/config.json,推的人可以在同一個提交把 drift_check.gate 改成 off 放過自己」
     ⚠ 推論(不算新洞,只在此記錄已看過、已有出處與回頭條件,不升等為本輪 finding)。

6. **行動端**:不適用,diff 不含行動端程式碼。已看,無。

7. **新依賴**:`_nodehome_cat_blobs` 沿用既有的 `import subprocess as _sp`,`_note_status_seq` 用既有的 `import time as _t`(在 `_drift_check_core` 內,和之前一樣的區域 import 慣例),`_j` 是既有的 `json` 別名,沒有新的第三方套件或新的標準庫危險模組(沒有 `pickle`/`yaml.load`/`eval`/`exec`/`shell=True`)。已看,無。

## 總結
最高等級 clean,blocking 0 條。逐類看過命令/路徑注入、git 選項注入、考卷與表態檔的邊界驗證、cat-file 逾時參數、`exam --repo` 的唯讀邊界、`.lumos/config.json` 自我放行的閘限制(沿用既有行為,本輪只補了有 since/retire 的 RULE 記錄),沒有找到本輪 diff 新引入的可利用漏洞。
