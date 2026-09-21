severity: blocker

## F1 檢查只認 `.git` 是檔,`.git` 是「指到目錄」的 symlink 一樣會把本體洗掉

severity: blocker
blocking: yes

觀察到什麼:修法的判斷式是 `src_git.is_file()`。Python `Path.is_file()` 會跟隨 symlink 再判斷「解析後的目標是不是一般檔案」。worktree 的 `.git` 之所以被擋,是因為它解析後是「一般檔案」。但如果來源的 `.git` 是一個 **symlink 指向另一個目錄**(例如指到別的 repo 的 `.git` 目錄,常見於「把 `.git` 搬到別處省空間」或任何非標準佈局),`is_file()` 解析後看到的是目錄,回傳 `False`,檢查完全不會觸發,`make_sandbox` 照跑。

`rsync -a`(修法沒有加 `-L`/`--copy-links`)預設**保留 symlink 本體**、不展開內容,所以沙盒副本裡的 `.git` 仍然是同一個 symlink,指向的還是「來源那份真正的 `.git`」。後面三道隔離(拔 remote / 設 hooksPath / 裝 pre-push)全部用 `cwd=str(work)`,但因為 `.git` 是穿透到別處的 symlink,git 判斷「這個 repo 的 `.git` 在哪」時直接找到那個外部目錄,於是拔的、改的還是外部那份。

引句:「src_git = Path(src) / ".git"」

怎麼重現(輸入→錯誤輸出,在 /tmp 自建臨時 repo,沒有碰 /Users/enzo/harness/lumos-toolchain):
1. 建一個「本體」repo `realgit-repo`,`git remote add origin https://example.invalid/real.git`。
2. 建一個「來源」目錄 `src-symlink-git`,把 `realgit-repo` 的檔案複製過去,但 `.git` 改成 `ln -s <realgit-repo>/.git src-symlink-git/.git`(即「來源的 `.git` 是 symlink 指到另一個真 repo 的 `.git` 目錄」)。
3. 用 Python 直接驗證:`Path('src-symlink-git/.git').is_file()` → `False`(修法的檢查不會觸發)。
4. `rsync -a` 複製 `src-symlink-git/` 到 `dest1/`,`dest1/.git` 仍是 symlink,`readlink` 指回 `realgit-repo/.git`。
5. 在 `dest1` 目錄下跑 `git remote`(模擬 make_sandbox 的拔 remote 那段,`cwd=work`)→ 列出 `origin`,逐一 `git remote remove origin`。
6. 回頭看「本體」`realgit-repo` 的 `git remote -v` → **空白**,遠端已被拔光。

實測輸出(節錄):
```
執行前 realgit-repo 的 remote:
origin  https://example.invalid/real.git (fetch)
執行後 realgit-repo(本體)的 remote:
(空白代表本體遠端被拔光 — 印證 symlink .git 繞過現有檢查)
```

為什麼是問題而不是風格:這批修法的訴求正是「隔離的前提是副本有自己的 `.git`,前提不成立就停手」(見 patch 內 `scripts/scenario_probe.py` 新增註解),但實作只堵了「`.git` 是檔」這一種前提不成立的形狀,沒堵「`.git` 是 symlink(不論指到檔還是目錄)」這種同樣違反前提的形狀。造成的傷害跟原始事故一模一樣——本體 remote 被拔光、hooksPath 可能被改到副本目錄——而且觸發方式一樣簡單(只要 `--repo` 指到一個 `.git` 是 symlink 的目錄),不需要額外的環境條件。修法應該檢查「解析後的 `.git`(或它所在的 gitdir)實際位置是不是就在 `src` 底下」,而不是只檢查「是不是一般檔案」;最少也該加 `src_git.is_symlink()` 一併擋下,並在 rsync 前用 `os.path.realpath` 驗證。

file: `scripts/scenario_probe.py:198`
file: `scripts/scenario_probe.py:199`

## F2 沙盒裡所有 git 指令都繼承呼叫者的環境變數,`GIT_DIR`/`GIT_WORK_TREE` 已設時檢查完全不相干、直接落到本體

severity: major
blocking: yes

觀察到什麼:`make_sandbox` 裡呼叫 git 的每一處(拔 remote、查 remote、設 `core.hooksPath`)都只帶了 `cwd=str(work)`,沒有任何一處帶 `env=`。Python `subprocess.run` 在沒有指定 `env` 時,子行程**繼承目前行程的完整環境變數**。如果呼叫 `scenario_probe.py` 的那個殼層/流程剛好帶著 `GIT_DIR`(或 `GIT_WORK_TREE`)——這在同一個 shell 之前跑過 `GIT_DIR=... git ...` 忘記還原、或某支上游腳本 export 過就很容易發生——git 判斷「這個 repo 在哪」時**優先看環境變數,完全不管 `cwd`**,於是即使來源是一個乾乾淨淨、`.git` 是普通目錄的正常 repo(不是 worktree、不是 symlink),沙盒裡的每一道隔離指令照樣會打到 `GIT_DIR` 指到的那個外部 repo。

這條路徑跟 F1、跟原事故完全不同源——它不靠來源 `--repo` 的形狀,單靠「呼叫當下的環境變數」就能讓修法的檢查形同虛設,因為修法檢查的是 `src` 這個路徑的 `.git`,而 git 指令實際會不會落到 `src`/`work` 身上跟 `GIT_DIR` 有沒有設是兩件獨立的事。

引句:「r = subprocess.run(["git", "remote"], cwd=str(work), capture_output=True, text=True)」

怎麼重現(輸入→錯誤輸出,同樣在 /tmp,沒有碰目標 repo):
1. 建「本體」`realgit-repo2`,`remote add origin https://example.invalid/real2.git`。
2. 另建一個完全正常、`.git` 是普通目錄的「來源」`src-normal`(確認 `Path('src-normal/.git').is_file()` 為 `False`,不會被 F1 那道檢查擋)。
3. `rsync -a` 複製成 `dest2`(模擬沙盒副本)。
4. `export GIT_DIR=<realgit-repo2>/.git`。
5. `cd dest2`,跑 `git remote`(cwd 明明是 `dest2`)→ 列出的是 `origin`,但這個 `origin`其實是 `realgit-repo2` 的,不是 `dest2` 自己的(`dest2` 這時甚至還沒 `git init`)。逐一 `git remote remove` 之後,回頭看「本體」`realgit-repo2`。

實測輸出(節錄):
```
在 dest2 目錄下,git remote(繼承 GIT_DIR)列出: origin
執行後 realgit-repo2(本體)的 remote:
(空白代表 GIT_DIR 環境變數繞過 cwd,本體遠端被拔光)
```

為什麼是問題而不是風格:這批修法與對應的 Issue 筆記(`Issues/探針以工作樹為來源會改到本體.md`)把「隔離前提」定義成「來源的 `.git` 是不是目錄」,但真正決定 git 指令落點的還有一層——行程環境變數——而修法與新測試都完全沒碰這層,連「什麼條件算修好」的三條清單裡也沒提到。派工詞明確要求查這個情況(`GIT_DIR` / `GIT_WORK_TREE` 環境變數已設),而且我已經在完全不涉及 worktree/symlink 的正常來源上重現出「本體 remote 被拔光」的同款傷害,判定為真實、未處理的破口。建議至少在 `make_sandbox` 開頭 `unset`(或在所有 `subprocess.run` 呼叫顯式帶 `env=` 且不含 `GIT_DIR`/`GIT_WORK_TREE`)後再往下跑,並在該 Issue 補這一類前提。

file: `scripts/scenario_probe.py:211-215`(拔 remote/設 hooksPath 那幾行皆未帶 `env=`)

## 其他已查、沒發現問題的路徑

- **submodule 來源**:submodule 的 `.git` 同樣是指標檔(`gitdir: ../.git/modules/<名>`),實測 `Path(...).is_file()` 為 `True`,會被現有檢查擋下,不是破口。
- **`git init --separate-git-dir` 建的 repo**:`.git` 一樣是指標檔,實測會被擋下。
- **來源是 bare repo**:`main()` 呼叫 `make_sandbox` 之前就有 `if not (src / ".git").exists(): ... return 2`(既有邏輯,這批沒動),bare repo 沒有 `.git` 這個路徑(內容直接放在根目錄),會在更早一層被擋,不會進到 `make_sandbox`。
- **停手時機**:檢查(`scripts/scenario_probe.py:198-199`)寫在 `tempfile.mkdtemp` 之前,`raise` 時還沒建任何臨時目錄,不會留下沒清掉的殘留。
- **raise 有沒有被吞掉**:`main()` 呼叫 `work = make_sandbox(src, a.arm)` 這行本身不在任何 `try/except` 裡(下面的 `try/finally` 是包在它之後才開始),`RuntimeError` 會直接讓整支腳本以未捕捉例外結束、印出 traceback、非 0 結束碼,不會被靜默吞掉。
- **測試會不會假綠**:把 `scripts/scenario_probe.py:198-199` 那段檢查拿掉後,實際重跑 `t_probe_sandbox_refuses_worktree_source` 的等價邏輯,三個斷言(停手/來源 remote 沒被拔/hooksPath 沒被改)全部翻紅(`raised=""`、`remotes=[]`、`hooksPath` 變成沙盒臨時目錄路徑),不是假綠。測試裡的 `git worktree add` 帶 `check=True`,若該環境跑不起來 worktree 會丟 `CalledProcessError`,`test_lumos.py` 的主迴圈把未捕捉例外算成 `FAILED`(不是 `_SrcOnly` 那條跳過通道),不會靜默跳過。
- **`git clone` 替代方案的可行性**:沒找到反證——`git clone <本體路徑> <目的地>` 對本地路徑會建立一份獨立的 `.git` 目錄(非 worktree 連結),可以再 `checkout` 到想比對的舊 commit,語意上能達成「舊版設定對照組」的目的;沒有查到它會漏掉本體設定或需要額外步驟。
