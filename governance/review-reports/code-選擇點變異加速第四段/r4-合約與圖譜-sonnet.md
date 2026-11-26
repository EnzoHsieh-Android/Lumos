severity: major

**已驗主張(正向,附證據)**
- 做法 3 的兩個連續計數(`streak`、`hang_streak`)現在由 `_kill_merge_trip` 與恢復路徑共同歸零。`_kill_merge_breaker` 的新註解與 docstring 和程式一致。`_kill_merge_note_unclean` 抽出後,三處呼叫行為與修前相同。
- S3 的「15 次跳開、恢復、再 1 次不跳開」與「3 次後原計數跳開、恢復、14 次不跳開」兩案各自有斷言。`t_choice_kill_merge_hang_breaker` 在我的副本上變異「合併基準逾時加字樣」後仍全綠(21 passed),所以這條沒壞;但它釘住的是 `_kill_merge_trip` 的歸零,不是恢復路徑自己的那行。恢復時 `hang_streak` 本來就已經是 0,那行重複但無害,算過度承諾。
- S2 新增的「快篩有失敗照結果檔名單」案:假 Gradle 的 `__mfail__` 鍵存在。預期呼叫 `[four, c]`,如果程式誤用事件行(a FAILED)會變成先跑 a,所以測試能翻紅。
- S6「重試上限 ≤30」在 `t_choice_kill_merge_events_cmd` 有斷言(`caps[1][0] <= 30.0`)。gov 讀回 `merge_init_off` 的新案存在,也涵蓋缺欄舊帳讀成空字典。
- 前段計劃的「部分被取代」註記位置都對:第一段〈用詞〉斷路器那句、第二段 S2 與 S10、第三段〈用詞〉。

**未驗範圍**
- 沒跑全套測試。
- 沒驗 `_choice_merge_events` 的效能。
- 沒驗 `規格閘.md` 以外的圖譜節點。
- 沒驗 impact 殘留段(本次派工沒有附「這次新增的殘留」段,所以沒有殘留問答可核)。
- 固定席的 INVARIANT 與 guard-kill 的 rc、JSON 合約,我判斷這次只動合併快篩的排序、計數與形狀判斷,沒有改 rc 優先序與 `--json` 輸出,所以不影響。

**Findings**

Finding 1
severity: major
blocking: 是
引句:「合併基準逾時而輸出有 STARTED 事件行時,原因是「合併基準:逾時(跑到測試後掛住)」,見 [[Projects/選擇點變異加速第四段_計劃]]」
- 這句是修補時新加在第二段 S10 的預期值。S10 綁定的 `t_choice_kill_merge_off_reasons` 沒有任何斷言驗它。全 repo 的 `scripts/test_lumos.py` 裡「跑到測試後掛住」只出現在 hang_breaker 的 `hw` 變數與 docstring。
- 新增的唯一斷言是 `t_choice_kill_merge_events_cmd` 裡 `_CHOICE_MERGE_BASE_WHY.get(...)startswith("合併基準")`,只驗字典查表。真正走過的 `merge_off` 與 stderr 路徑沒人跑。
- 最小重現:副本 checkout c5be145,把 `scripts/lumos:29132` 的 `"合併基準:" + (...)` 改成 `("" if why.startswith("逾時(") else "合併基準:") + (...)`。
  - 執行 `python3.14 scripts/test_lumos.py -k choice_kill_merge_off_reasons`、`-k choice_kill_merge_events_cmd`、`-k choice_kill_merge_hang_breaker`,結果 19、23、21 passed,0 failed。
  - 此變異後 merge_off 變成「逾時(跑到測試後掛住)」(缺前綴),與新增註記寫的值不同,測試全綠。
- 反向變異(`_CHOICE_MERGE_BASE_WHY` 拿掉掛住那列)只被 `events_cmd` 的查表斷言抓到,所以那條斷言只守得住表,守不住 `merge_off` 與印出的字樣。
- 歸因:有證據的修復回歸(註記與弱斷言都是修補新增)。
- file: `scripts/lumos:29132`

Finding 2
severity: minor
blocking: 否
引句:「`_choice_merge_shape` 在含 {method} 的那一段緊接殼層元字元(&、;、|、<、>)時判形狀不支援、不合併(切不出乾淨的一段)」
- 這條新規則只存在於 guard-kill 的 WHY 與審計紀錄,三處對不上:
  - 計劃〈做法〉1、驗收條款 S1、預期值表 S1 都沒寫。三個月後讀計劃的人不知道有這條形狀限制,測試卻掛在「S1」標籤下(`t_choice_kill_merge_events_cmd` 的 `S1 \`{method}\` 後面直接接殼層元字元`)。
  - `_choice_merge_shape` 的 docstring「條件:…」那串沒列這一條,與程式不符。
  - 該測試 docstring 的「翻紅釘」也沒列。
- 這是「未定義於條款的行為」,不是行為錯誤。
- 歸因:有證據的修復回歸。
- file: `scripts/lumos:28773`

Finding 3
severity: minor
blocking: 否
引句:「原因由 classify 一處決定(合併基準走同一支,不通過時印的原因跟著變成這個字樣,照原字串帶出)」
- 計劃〈做法〉3 的這句與修補後程式不一致。印出的是 `_CHOICE_MERGE_BASE_WHY` 換字後的「合併基準逾時(跑到測試後掛住)」,不是原字串。
- merge_off 記的是「合併基準:逾時(跑到測試後掛住)」。兩種字樣(印的與記的)計劃都沒寫全,只有第二段 S10 註記寫了 merge_off 那個。
- 計劃〈落點〉也沒列「第二段 S10」被註記。落點只提到第二段 S2。
- 照著落點清單去查註記的人會漏掉 S10。
- 歸因:有證據的修復回歸。
- file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md`(做法 3 第一個項目、〈落點〉第三項)

Finding 4
severity: minor
blocking: 否
引句:「輸出有截斷標記、c 開始沒結束時 c 應 進未知層(順序 b、c、d、a)」
- S2 條款與預期值表第五列都寫 b、c、d、a。
- 測試只在解析層斷言 `hung == []` 與 `failed == [b]`,沒有真跑逐支順序 b、c、d、a。
- 「c 落在未知層而非通過層」只靠解析斷言間接成立。
- 歸因:未判定(原有,不是修補引入)。
- file: `scripts/test_lumos.py:147889`

最高 major,blocking 1 條

**三問**
1. 修補處有沒有引入新問題?有。第 1 條的註記沒有端到端斷言,第 2 條的新規則沒有對應條款。
2. 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?計數歸零、恢復、共用函式抽取三處成立(見已驗主張)。合併基準逾時加字樣這條相鄰路徑沒有端到端測試守住。
3. 新發現在修前、修後各是什麼結果?第 1 條修前沒有這句註記,也就沒有承諾;修後有承諾而沒有斷言。第 2、3 條修前沒有該規則與該字樣,修後只在筆記裡有。第 4 條修前修後都一樣。

暫存已清:我自己的副本 clone 與紅燈留下的 `gctl-run-_5xmyvll` 都已刪。派工給的 `合約與圖譜-sonnet` 目錄本身(原本就是 repo 複本)未動。
