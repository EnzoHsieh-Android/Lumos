severity: major

D1
severity: major
blocking: 是
引句:「if not flat:   # 給搜尋判斷用:引號內整段保持一個詞、不剝 $——引號裡「提到」lumos search(python -c 腳本、echo、提交訊息)不是真的跑了它」
file: `governance/eval/lens-utilization/recount.py:73`
`flat=False` 讓引號整段變一個 token,導致 `bash -c "lumos search x"`、`sh -c "lumos search x"` 這種「用雙引號包住、但引號內容其實被巢狀 shell 真的執行」的呼叫,`_search_segments` 直接回傳空 list(連 None 都沒有,完全不進 `out`)。重現:`python3 -c` 載入 `recount.py`,`_search_segments('bash -c "lumos search x"')` → `[]`;實際 `bash -c 'bash -c "lumos search x"'` 用假 `lumos` 執行確認真的有跑(印出 `REAL_SEARCH:x`)。修前(未加 flat 參數、整段拆字)的舊邏輯反而抓得到這個 case,是這輪修正的退步;`bash -c` 在這個 repo 逐字稿裡本身就常出現(`grep -c "bash -c" ~/.claude/projects/.../*.jsonl` 多份 >0)。

D2
severity: major
blocking: 是
引句:「heredoc 用原始行判,避開引號跨行把結束標記吃掉。」
file: `governance/eval/lens-utilization/recount.py:876`
`_HEREDOC_START_RE.search(ln)` 在還沒替換引號前的原始行上找 `<<IDENT`,不分辨這串是不是在引號裡——查詢字串本身含字面 `<<EOF` 就會被誤判成開了一個 heredoc,之後所有行(含真的 `lumos search`)被當成 heredoc 內容吞掉,直到(通常永遠不出現)剛好等於該字面單字的一行。重現:`_search_events('lumos search "heredoc <<EOF pattern test"\nlumos search "second real query"', ...)` → 只回傳第一筆,第二筆「second real query」完全消失於 `segs`(不是 undetermined,是整段不存在)。

D3
severity: major
blocking: 是
引句:「r = subprocess.run(["git", "-C", str(d), "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)」
file: `governance/eval/lens-utilization/recount.py:1186`
這行沒有 try/except,若環境沒裝 git(PATH 找不到 `git`)會拋 `FileNotFoundError` 直接把 `write_archive`/`main()` 炸掉;同檔另外兩處呼叫 git 的地方(`repo_paths`、`existed()`)都包了 `try/except Exception: pass`,只有這個新函式沒跟上慣例。重現:`os.environ["PATH"]="/nonexistent-empty-dir"` 後呼叫 `m._committable(Path(".../local/file.json"))` → `CRASHED: FileNotFoundError [Errno 2] No such file or directory: 'git'`。`_committable` 之前 `_atomic_json(weekly, ...)` 已經寫檔成功,但因為這裡沒接住,整個 `write_archive` 連帶 `main()` 沒有優雅降級路徑。

全份最高嚴重度是 major,blocking 共 3 條。
