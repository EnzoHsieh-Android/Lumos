severity: minor

審了 r3-repair-code.patch 的程式部分,也用 `f04090128:scripts/lumos` 與 `1d535b07b:scripts/lumos` 對照。dispatch-lens 的鎖檔路徑不存在(`cat` 回 No such file),所以沒有鎖可檢查也沒有東西要刪。

## t1 「已寫過」的帳比對不看段與列,別段別列的人裁會被當成「已經完成」回 0
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前同一情況是拒絕 rc 2,修後變成成功 rc 0)
引句:「這次人裁已經完成,什麼都不用做」
file: `scripts/lumos:_situation_rule_already`(修後 `f04090128` 版;patch 內 `_situation_rule_already(rows, lines, clause, test, ruled)` 與 `_spec_gate_ruled_ids` 呼叫處)

1. `ruled()` 只比計劃、條款編號、條款文字雜湊、測試名。帳上事件的 `seg` 與 `row` 完全不參與。
2. 場景:段 A 的 D-1 已人裁寫回 `S5`(條款文字 C、只綁 T)。同一人再對段 B 的 D-2 下指令,帶同一段條款文字 C 和同一支測試 T,`--file/--old/--new` 是段 B 的壞法。
3. 修前:`test in refs` 命中「已寫過」,拒絕 rc 2。我只讀了 1d535b07b 的程式碼確認這條路,沒有實跑。
4. 修後:在試插階段命中 `_situation_rule_done`,印「✓ …這次人裁已經完成」並回 0。殺傷力驗證沒跑,段 B 的列沒有任何帳,也沒有任何驗證。
5. 影響:範圍 4 的重點是證明這一段在同一列的寫法之間換,這支測試會紅。這條路徑讓作者以為段 B 的人裁已經做完,而實際上段 B 沒被證明。
6. 只靠現有條款本身,規格閘仍然會認那條人裁條款,所以資料不會壞。單人工具威脅模型下嚴重度不高,所以標 minor。
7. 建議:`ruled` 命中後再比 `(seg,row)`。不符就不要說「完成」,改成拒絕,或當成新的人裁照跑。

## t2 `--keep-worktree` 建樹失敗時,仍印「現場保留: <路徑>」,但那個路徑已被刪掉
severity: minor
blocking: 否
歸因:有證據的修復回歸
引句:「建樹失敗的平台照舊印一行(guard kill 每個平台一行,t_isolated_worktree_shared ⑤);那個路徑本來就沒建出來」
file: `scripts/lumos:27864`(on_keep 的 lambda 印 `(--keep-worktree) 現場保留: {p}`)、`scripts/lumos:27573`(`_isolated_worktree` 的 `elif keep and on_keep is not None`)

1. 場景:`guard kill --keep-worktree`,`git worktree add` 失敗(例如 ghead 壞掉)。
2. 修前:`keep` 為真,寫標記(因 parent 目錄已不存在而失敗被吞)、`on_keep` 被呼叫。使用者看到「現場保留: …」,但同樣是路徑不存在。
3. 修後:先 `rmtree(parent)`,再叫 `on_keep(wt.path)`。輸出沒變,依然是一行「現場保留: <剛被刪掉、從未存在的路徑>」。
4. 這是作者為了讓既有測試 ⑤ 的輸出不變而保留的行為。它不是新壞掉的東西,但修補順手把「為了守測試而說謊」寫成明文。使用者會去找一個不存在的目錄。
5. 建議:建樹失敗時 `on_keep` 不叫,或呼叫端依 `_iw.ok` 印「沒建成、無現場可留」。測試 ⑤ 改成檢查「有印出這個平台」即可,不必綁死文案。

## t3 寫計劃到記帳那段(`defer=True`)連拿寫入鎖的最長 60 秒等待也吞掉 Ctrl-C
severity: minor
blocking: 否
歸因:有證據的修復回歸(修前這段沒有 SIGINT 處理,Ctrl-C 會直接中斷;修後 `_situation_rule_commit` 把鎖等待包進 `defer=True`)
引句:「整段(拿鎖之前到記完帳)在 _situation_rule_signals(defer=True) 裡」
file: `scripts/lumos:30684`(`_vault_write_lock` 最多等 60 秒、每 0.05 秒重試)

1. 場景:另一程序持有筆記庫寫入鎖,使用者在這邊按 Ctrl-C 想放棄。
2. 修後:SIGINT、SIGTERM、SIGHUP 都只記進 `sigs`,`_vault_write_lock` 照樣睡滿 60 秒。取得鎖後的檢查點才回 rc 2。取不到鎖,最後訊息是「拿不到筆記庫的寫入鎖」,看不出是自己按了中斷。
3. 修前:鎖等待期間 Ctrl-C 會立刻丟出 `KeyboardInterrupt`。
4. 該延後的是 `os.replace` 之後到記帳完成之間。拿鎖前根本沒東西需要保護,可以讓第一個訊號在拿到鎖前直接放行。
5. 單人、鎖爭用罕見,所以只標 minor。

## 附:三問、圖譜鏡頭

**①原問題的修復效果,行為證據**
- `--plan` 大小寫、符號連結:用 `SourceFileLoader` 載修後版跑 `_situation_rule_plan_path_problem`。
  - `Projects/Abc_計劃.md`(同名)回 None。
  - `Projects/abc_計劃.md` 回「跟實際檔名對不上(實際是 Projects/Abc_計劃)」。
  - 結果:拒絕有效,正常路徑照收。
- 單獨 CR:`---\na: 1\n---\nx\ry\n` 被 `_situation_rule_read` 拒絕。LF 檔回 `('---\na: 1\n---\nx\n', None)`,尾端換行保留。`load_raw_for_edit` 用 `split("\n")`,`"\n".join` 能原樣還原。
- BOM 與 CRLF:由 `load_raw_for_edit` 擋。這裡沒另外實跑。
- 訊號、「已寫過」兩種訊息、讀回不一致 rc 1、AI 代跑提醒:只做了靜態追蹤,沒有實跑。對照的測試是 `t_situation_rule_double_signal` 等,我沒有執行(派工詞限制 `-k` 且時間有限)。

**②相鄰呼叫路徑**
- `_spec_gate_ruled_ids` 的新參數 `ai_out` 預設 None。`_expected_requirement` 的其他呼叫端(推送前那一圈 ctx 路徑)不傳,行為不變。
- `_spec_gate_expected_part` 與 `_spec_gate_twoway_gate` 各印一次提醒:前者要 door=high,後者在 door=low 才走,互斥,不會印兩遍。
- `_isolated_worktree` 的呼叫端只有 `scripts/lumos:23256`(修正關卡,不傳 keep)與 `scripts/lumos:27863`(guard kill)。keep=False 與建樹成功的路徑沒變。
- `WriteBlocked` 繼承 `ValueError` 與 `RuntimeError`,所以 `_situation_rule_locked_write` 的 `except RuntimeError` 仍接得到鎖逾時。
- 沒找到「修補弄壞呼叫端或拿掉守衛」的其他證據。被拿掉的 `read_bytes` 與 CRLF 檢查、`test in refs` 的寬鬆比對,都由 `load_raw_for_edit` 與 `set(refs)=={test}` 補回,而且更嚴。

**③新發現的同一案例,修前與修後**
- t1:修前 rc 2(拒絕),修後 rc 0(聲稱完成)。
- t2:修前與修後都印「現場保留」,只是順序變了。
- t3:修前鎖等待可被 Ctrl-C 中斷,修後不行。

**圖譜鏡頭**
- 計劃〈情境題答案要引規格出處與回寫循環〉範圍 4 和 5 以及天花板 7、8:新文字與程式行為一致,即 done 回 0 不跑殺傷力、「先刪再跑」、讀回不一致 rc 1、AI 提醒只提醒不擋。
  - t1 對應計劃寫的「帳已有對得上(計劃、條款編號、條款文字雜湊、測試名)」。這個口徑就是不含段與列,所以是計劃本身沒想到、不是文字與程式不符。
- `Systems/guard-kill.md` 新增 WHY 行:`_situation_rule_signals` 與 `_lint_wt_on_term` 刻意不同、並說明 `os._exit` 不跑 finally。與程式一致。
- `.lumos/lint-waivers.json` 新增 6 條 C901 放行,標 `origin: ai`、`acked: false`,格式與既有條目一致。我用 ruff 按 mccabe 10 查 `f04090128` 版,沒有可靠地對上這 6 個函式的 key。這點不判。
- 其餘固定席筆記沒有附上,未見牽連。

最嚴重:minor;blocking 共 0 條
