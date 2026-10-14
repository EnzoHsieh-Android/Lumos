severity: minor

臨時檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/併發資源-sonnet/`。我用 4e87b682 的 `bypass_reasons` 量時間,用 `_hookevent.record` 做併發與砍程序實驗,修前版本拿來對照。

## Finding

1. `_replace_cmdsubs` 搭配 `_match_paren` 是平方時間,20000 字內最慢的輸入是大量沒配對的 `$(`。
   - 引句:「close = _match_paren(text, i + 1)」
   - 輸入:`"git commit -n; " + "$(" * 9990`(約 2 萬字)。
   - 路徑:每個沒配對的 `$(` 都從該處掃到字串尾,找不到才回 -1,然後外層迴圈只前進一格。
   - 命令:`bypass_reasons(cmd, "/Users/enzo")`,結果 `['commit-n']`,耗時 3.17 秒。
   - 同形的 `"$(("*6000` 要 1.65 秒,`'"$("' * 3000` 要 0.66 秒。
   - 整個程序實測:hook 以 `--budget 5` 執行(註冊表給這支的逾時是 5 秒),從 stdin 進、cwd 是暫存 repo,牆鐘 3.18 秒。正常指令是 0.09 秒。
   - 後果:Claude Code 以 5 秒殺掉 hook 就等於放行,而這個平方形狀已吃掉預算的 64%。
   - 應該是:用一次線性的堆疊配對,或預先算好每個 `(` 的配對位置。
   - 其他形狀(8 種引號、heredoc、註解、`&`、mkdir、remote add、`cd` 重複)在 2 萬字內都在 0.1 秒以下;例外是 heredoc 不終止 0.37 秒(修前量到,修後 0.03 秒)、全是反引號 0.89 秒(修前 0.84 秒,不是這次修補造成)。
   - 歸因:有證據的修復回歸。
     - 修前 `b5be3aad` 同一輸入 0.01 秒。
     - 修後 `4e87b682` 為 3.17 秒。
     - 修前沒有逐個 `$(` 的配對掃描。
   - 我沒有實測更慢的機器。「再慢 1.6 倍就超過 5 秒」是用 3.18 秒推算的。
severity: minor
   - blocking: 否
   - 降級理由:這是問人層,失敗放行是設計決定。輸入也是人為灌的畸形指令,正常指令不會有上千個沒配對的 `$(`。

2. `_hookevent.record` 修剪時,程序在 `mkstemp` 之後、`os.replace` 之前被殺,`.trim` 殘檔沒人清,會越積越多。
   - 引句:「fd, tmp = tempfile.mkstemp(dir=str(d), prefix="hook-events.", suffix=".trim")」
   - 路徑:清理只在 `except OSError` 裡;SIGKILL、SIGTERM 或 hook 逾時被殺不會進去。
   - 重現:在子程序裡把 `os.replace` 換成 `os.kill(os.getpid(), 9)`,連跑 3 次。結果留下 3 個各 218057 位元組的 `hook-events.*.trim`,沒有任何程式會去掃。
   - 整個目錄在 `.gitignore`(`governance/runtime/`),所以不會冒出 `git status` 的雜檔。
   - 殘檔產生的條件很窄,要被殺在修剪那幾毫秒內。
   - 現在固定名字改隨機名,修了 r1 說的「暫存名被佔住就永遠修剪失敗」。代價就是殘檔不再被下一次覆蓋。
   - 建議:修剪前順手清掉 `hook-events.*.trim` 中超過一分鐘的舊檔,或是接受並寫成回頭條件。
   - 歸因:有證據的修復回歸。
     - 修前固定的 `.jsonl.tmp` 會被下次覆蓋。
     - 修後是隨機名,殘檔不會被覆蓋。
severity: minor
   - blocking: 否

## 其他已驗

- **`_git_out` 的上限與快取**:每次 `bypass_reasons` 開頭都重設 `calls` 和 `cache`,沒有跨呼叫殘留,超過 4 次回 `(None, "")`。這部分沒有發現問題。
- **`_inner_budget()` 預算起點**:`entry` 開頭先叫一次,起點在進場、早於 `guard` 裡的 `git rev-parse`。同一程序重複呼叫 `entry` 時,`_BUDGET_START` 是模組全域變數,只設定一次,測試裡的第二次起會一律拿到 1 秒下限。正式環境每個事件各自起一個程序,不受影響。
- **多會談同時修剪**:8 個程序各寫 400 筆,0.21 秒完成,0 行壞 JSON,沒有留下 `.trim`。是否掉行我量不出來,因為修剪本來就會丟舊行。讀取後到 `replace` 之前別人追加的行理論上會被覆蓋,但這是問人層的存活紀錄,我沒有當 finding。
- **檔案權限**:`mkstemp` 建出 0600,修剪後 `hook-events.jsonl` 從 0644 變 0600(實測)。只有單一使用者,不影響。
- **磁碟滿**:修剪寫入拋 `OSError` 時會 `unlink` 暫存檔再走 `except OSError`,不會殘留。我沒有真的造出磁碟滿,只讀程式判斷。
- **⚠ 交編排者**:git 卡住時的最壞總耗時,我沒有實測。從程式推算:`guard` 的 `_root_from_cwd` 最多 3 秒,再加 4 次 `_git_out`,每次下限 1 秒,總計約 7 秒,超過 5 秒的 hook 逾時。同樣只是放行,而且需要 git 真的卡住,所以沒列為 finding。

## 三問

1. **原問題的修復效果**:暫存名衝突已修好,多程序併發修剪實測無壞行、無殘檔。
2. **相鄰呼叫路徑**:正常指令 0.09 秒;`_git_out` 與預算起點正常;唯一退化是 finding 1 的修後新平方成本。
3. **同一案例修前與修後**:
   - 沒配對的 `$(`:修前 0.01 秒,修後 3.17 秒。
   - 修剪中被殺:修前殘檔會被下次覆蓋,修後會累積。

## 固定席節點

- **`Systems/lumos-cli-read`、`lumos-cli-lifecycle`**:其 ★INVARIANT★ 是 `search` 預設排除 superseded、re-inject 只覆蓋 sentinel 之間。`_hookevent.py` 只是列在牽連檔,本席沒讀到 `search` 或 re-inject 相關的 diff。不影響。
- **`design-loop`、`測試假綠形態`、`guard-kill`**:這三條合約分別管設計審的材料格式、還原翻紅釘要有前置斷言、`guard kill` 的 rc 與 JSON。本席沒讀到相關改動。測試假綠那條也適用於 finding 1,即「修了平方成本」的測試要證明測到的輸入真的走到 `_match_paren`。不影響。
- **`pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★)**:牽連檔是 `scripts/lumos`,屬文件註冊組,不在本席範圍。不影響。
- **`Issues/code-loop守衛main-direct盲區`**:牽連的是 `test_lumos.py`,我沒有讀它。不影響本席鏡頭。

最嚴重等級 minor,blocking 共 0 條。
