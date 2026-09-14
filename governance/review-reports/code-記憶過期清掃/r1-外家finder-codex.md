severity: major

1. 預算耗盡會把未驗證的記憶撤章
severity: major
blocking: 是
引句:「elif was and not unknown:」

`check_one` 遇到期限只增加 `skipped`，沒有把該條加入 `unknown`；`apply_one` 因而把空結果當成全部成立。記憶體實驗：已蓋章且仍然過期的檔案，傳入已過期的 deadline，得到 `skipped=1`、`recovered=1`，並宣稱現在又成立了。開啟寫入時會實際撤章。應把未執行結果傳到檔案層，只有所有宣告明確通過才能撤章。
file: `scripts/hooks/claude/memory-sweep.py:344`
file: `scripts/hooks/claude/memory-sweep.py:370`

2. 蓋章與撤章會永久刪除原有內容
severity: major
blocking: 是
引句:「text = re.sub(r"(?m)^  (status|stale_at|stale_by): .*\n", "", text)」

替換作用於整份文字，沒有侷限到清掃器擁有的欄位。實驗中原有的 metadata `status: active` 與正文縮排的 `status: example` 都在蓋章後消失，撤章也無法還原。這不是空白差異，而是原始資料遺失。應使用專屬標記區塊，只移除自身寫入的內容，並保留原有欄位。
file: `scripts/hooks/claude/memory-sweep.py:291`
file: `scripts/hooks/claude/memory-sweep.py:321`

3. git 子程序的逾時沒有服從整體時間預算
severity: major
blocking: 是
引句:「_git("fetch", "-q", up.split("/")[0], cwd=root, timeout=25)」

hook 外層限制是 12 秒，但單次 fetch 可等待 25 秒，其他 git 呼叫預設也可等待 20 秒。deadline 僅在開始一條檢查前確認，沒有傳給子程序；遇到慢速遠端時，外層會先終止程序，無法輸出尚未驗完的提示。應把剩餘預算傳入每次 git 呼叫，並在耗盡後立即進入收尾。
file: `scripts/hooks/claude/memory-sweep.py:179`
file: `scripts/hooks/claude/memory-sweep.py:199`
file: `scripts/hooks/claude/memory-sweep.py:344`

4. fetch 失敗仍以舊遠端資料判定，可能錯誤蓋章
severity: major
blocking: 是
引句:「r = _git("merge-base", "--is-ancestor", sha, up, cwd=root)」

fetch 的回傳值完全被忽略。離線、認證失敗或逾時後，仍用本地殘留的 upstream ref 判定。若提交已從另一台機器推送、本機尚未更新，就會把 `pushed` 判成 False 並蓋章。以替身令 fetch 回傳 128、祖先檢查回傳 1，實測 `_is_pushed` 回傳 False，沒有傳遞 None。應先確認 fetch 成功，否則報驗不了。
file: `scripts/hooks/claude/memory-sweep.py:199`

5. 解析器接受正文範例與缺少 frontmatter 的輸入，寫入時可能中斷整輪
severity: major
blocking: 是
引句:「m = re.search(r"(?m)^verify:\n((?:[ ]+.*\n)+)", text)」

搜尋沒有侷限於 frontmatter，因此正文程式碼範例也會成為檢查。實驗中只有 `verify` 區塊、沒有 `---` 的文字仍成功解析；檢查失敗後呼叫 `stamp`，立即拋出 `ValueError: substring not found`。`sweep` 未隔離這個錯誤，會中止後續檔案且沒有未完成報告。應先驗證 frontmatter 邊界，只解析其內宣告，畸形檔案應報錯並繼續處理其他檔案。
file: `scripts/hooks/claude/memory-sweep.py:259`
file: `scripts/hooks/claude/memory-sweep.py:302`
file: `scripts/hooks/claude/memory-sweep.py:387`

6. 不認得的檢查型別被丟棄，可能造成錯誤撤章
severity: major
blocking: 是
引句:「out.append((claim, k, v))」

解析器只保留 `CHECKS` 中的型別與 `cmd`，其他宣告沒有進入 `run_check` 的 None 路徑。實驗中 `pushd: abcdef0` 得到空清單，沒有任何驗不了提示；若同篇還有另一條合法且通過的檢查，已蓋章的檔案就會被撤章，即使拼錯的那條根本沒驗。應保留未知型別並回報 unknown，缺少檢查內容的 claim 也應如此。
file: `scripts/hooks/claude/memory-sweep.py:272`
file: `scripts/hooks/claude/memory-sweep.py:370`

7. 狀態比對把整篇文字套到每個節點，正確記憶也會報雙重衝突
severity: major
blocking: 是
引句:「if st == "done" and _DONE_WORDS.search(body):」

判斷沒有關聯節點與其描述，而是對每個節點搜尋整篇正文。實驗文字為 `[[Projects/Alpha]] 已完成。` 與 `[[Projects/Beta]] 進行中。`，圖譜分別為 done、doing，結果卻對兩者都報狀態打架。應先把狀態宣稱綁到對應節點；無法確定歸屬時，不應輸出確定的衝突判定。
file: `scripts/hooks/claude/memory-sweep.py:154`
