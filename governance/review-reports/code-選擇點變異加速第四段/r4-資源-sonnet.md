severity: minor

這輪修補(r4-repair.patch)沒有引入新的資源問題,我也沒找到確定的孤兒程序或預算被吃光的情況,只有一條 minor。

**固定席與殘留段**
- 固定席節點(bound-tests-gate、lumos-cli-read、guard-kill、測試假綠形態、lumos-cli-lifecycle、design-loop 等,以及 pitfalls-code-loop、loop-convergence-recording 兩篇 ★RISK★)都未被本輪修補牴觸。
- 資源鏡頭下,這些節點的合約沒有被這個 diff 動到,所以我沒有逐條展開。
- 派工詞尾端沒有「這次新增的殘留」段,所以沒有殘留問答要答。我也沒有重問或換編號的對象,不涉及「第二個代理是不是另一個代理」。

**finding 1:每次跳開前最多空等 15 次快篩逾時,比修前多 10 次**
- 歸因:有證據的原有漏查。這是第四段計劃的設計取捨(`_CHOICE_MERGE_HANG_BREAKER = 15`),不是 r4 修補造成的。
- 場景:某平台組每個壞法的快篩都在測試後掛住。每次快篩的逾時上限是 `max(5×合併基準耗時, floor)`。
- floor 預設 20 秒(file: `scripts/lumos:28398`)。合併基準約 18 秒時,上限約 90 秒。
- 跳開前最多空等 15×90 秒,約 22 分鐘。修前只數 5 次,約 7.5 分鐘。
- 跳開後每 10 個壞法還有一次試探快篩,掛住時再耗一個上限。這些時間仍受 `max(mg.remaining(), 1.0)` 約束,不會超出 `--max-seconds`。
- 但整個預算被連續掛住吃光時,剩下的壞法會判不到。
- 這是 minor:只多花時間,有上限,而且 15 這個值是設計審已裁的取捨。

severity: minor
blocking: 否

引句:「_CHOICE_MERGE_HANG_BREAKER = 15          # 跑到測試後逾時(多半是壞法讓測試掛住)另外數,連續幾次才跳開」

**已驗主張**
- **子程序回收**
  - `_kill_run`(file: `scripts/lumos:28194`)在逾時和 KeyboardInterrupt 兩條路徑都先收程序群組再 `wait`,並在 finally 清掉 `_KILL_RUN_LIVE` 的登記。
  - 本輪修補沒有新增任何子程序呼叫。
  - 事件初始化腳本放在 `_isolated_worktree` 的上層暫存資料夾 `scratch`(file: `scripts/lumos:28115`),由該函式的 finally 一起刪掉。
- **帶腳本的基準重試**
  - 重試條件只有「找不到 JUnit 結果檔」這一個常數 `_CHOICE_MERGE_NO_RESULTS_WHY`。
  - 逾時不重試。
  - 重試上限是 `min(cap, max(mg.remaining(), 1.0))`,不會比第一次更大,也不會超過剩下的總時限。
- **事件行解析**
  - 我造了一份 278879 位元組的輸出:8000 行 PASSED、3000 行 STARTED,配 170 個名字。`_choice_merge_events` 解完 0.21 秒,`names=[]` 那次只要 0.011 秒。
  - 解析是逐行字串切,工作量是行數 × 名字數 × 不同的完整名數;合併呼叫只帶 lane 的 `--tests`,不同的完整名數受 lane 支數限制。
  - 輸出經 `_kill_cap` 限到 256KB。
- **`_choice_merge_shape` 的新判斷**
  - 含 `&;|<>` 時回 None,結果是不合併、退回逐支,不拋例外。
  - 不引入任何程序或記憶體負擔。
- **斷路器**
  - 新增的 `_kill_merge_note_unclean` 只是把三處重複的累計搬成一個函式。
  - `hang_streak` 在 `_KillMerge.__init__` 初始化。
  - `_kill_merge_trip` 與恢復路徑都把 `streak`、`hang_streak` 歸零。
  - 沒有鍵不存在的取值問題。

**未驗範圍**
- 真實 Gradle 在客戶端被 SIGKILL 後,daemon 是否確實取消掛住的測試執行器,我沒有實測。這是修前就有的行為,與本 diff 無關。
- `_kill_run` 把整份輸出 `buf.read()` 進記憶體後才截斷,輸出量沒有上限。這是修前就有的行為。事件腳本只多加事件行,量級是行數,沒有加 stdout,所以我未列為 finding。
- `_kill_merge_screen` 在快篩期間收到 KeyboardInterrupt 時,不會在 `_kill_merge_restore` 還原被改的檔。工作樹是隔離的,會在 `_isolated_worktree` 的 finally 被刪,所以不外洩。這是修前就有的行為,我沒有單獨驗證它。

**三問**
1. 修補處有沒有引入新問題:沒有。
2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立:成立。
   - 帶事件腳本的基準遇到「找不到 JUnit 結果檔」會重試;其他失敗不重試。
   - 逾時沿原路徑走。
   - 快篩逾時且沒有事件行,仍照舊數 5 次。
   - 有 STARTED 事件行,改數 15 次。
   - 試探恢復後兩個計數都歸零。
3. 新發現在修前、修後各是什麼結果:finding 1 在修前就存在(同樣是 15 的門檻和同一個逾時上限算式),修後沒有變化。

實測只在 /tmp/lumos-seat-work/ 底下做,暫存腳本已刪。

最高 minor,blocking 0 條
