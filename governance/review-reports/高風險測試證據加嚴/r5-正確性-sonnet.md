severity: blocker

# 高風險測試證據加嚴 r5:正確性席(sonnet)審查

以下全是「照這份 spec 寫出來,在某個輸入下會判錯」的場景。我逐節讀過,開檔驗過 spec 借用的函式。

這一輪主要結論有三點:
- r4 把重播從推送前搬到 PR 檢查,推送形狀的接縫確實整類消失。merge-base 在 base 前進、rebase、merge main 進 head 這幾種情況下都算得對。
- 新的洞集中在「選要重播哪些」這一步。它按檔案粒度和「計劃有沒有進改檔清單」來選,在這個 repo 與一般消費專案兩種形狀下,方向會反過來。
- 還有補進來的借用段落(靜態檢查、弱證據處理、事件落點)與原文銜接處的不一致。

## 逐條 finding

1. 新計劃把條款綁到「沒改到的檔」裡本來就綠的既有測試,整個基準重播被跳過,gate 放行。
   引句:「前一批已經合進主線、這次沒改到的測試不重播」
severity: blocker
   blocking: 是,該擋的放掉:風險高計劃的新行為條款綁了舊程式上就綠的測試,是這份計劃要抓的頭號假測試,這個輸入下 rc0 且沒有任何事件。
   - 重現:
     - PR 新增一份風險高、`created` 不早於生效日的計劃。
     - 計劃的 `[S1] … [test:t_舊測試]` 沒標 keeps,`t_舊測試` 定義在這個 PR 沒碰的測試檔。
     - 第 3 點選出 0 支,「印一句、不重播」。
     - 靜態檢查也抓不到:`_spec_gate_twoway_static` 只驗 keeps 的測試在計劃建立前存在,`_clause_check_twoway` 只驗存在與不重複。
   - 對照:風險低路徑會在 `_spec_gate_twoway_run_verdict` 把「沒標 keeps 卻綠」擋下。file: `scripts/lumos:14242`、`scripts/lumos:14218`。
   - 根因:「前一批已合進主線」這個豁免只適用於計劃早就在主線上的情況。計劃在這個 PR 才第一次進歷史時,沒有「前一批」可言,所有新行為條款都該重播,不論測試定義在哪個檔。
   - S3 的綁定測試 `t_pr_evidence_only_changed_tests` 會把這個洞寫成驗收。

2. 檔案粒度過度重播,後續 PR 同時碰計劃與同一個測試檔,誤擋已實作完的計劃。
   引句:「定義在這次改檔清單裡的測試檔的那幾支」
severity: major
   blocking: 是,把不該擋的擋下:分岔點本來就含該功能,所有舊測試必綠,必然 rc1。
   - 重現:
     - 計劃 X(風險高、生效日之後)在 PR1 實作完並合併,測試 t_x1..t_xn 都在 `scripts/test_lumos.py`。
     - PR2 修別的 bug,往 `scripts/test_lumos.py` 加一支測試,並改了 X(`lumos set status`、REVISIT、審計紀錄任一個都算)。
     - 第 2 點選出 X;第 3 點把定義在「改到的測試檔」`scripts/test_lumos.py` 裡的 X 所有新行為測試全選進來。
     - 分岔點已含 PR1,t_x1..t_xn 全綠,S6 判 `base-replay-failed`,rc1。
   - 這個 repo 的測試集中在單一檔:`scripts/test_lumos.py` 有 3177 個 `def t_`,幾乎每個 PR 都碰它(`.lumos/config.json` 的 `test.run_cmd` 是 `scripts/test_lumos.py -k {method}`)。
   - 所以同一個根因(檔案粒度),在單檔 repo 是過度重播(本條),在一檔一類別的 Android 專案是重播不足(第 1 條)。
   - 逃生口只有 `base_replay_skip` 或整個 gate 關掉。
   - 要改成「這個 PR 新增或改動的那支測試函式」才重播,或只重播計劃第一次進歷史就在這個 PR 的測試。

3. 觸發條件看「計劃檔有沒有在改檔清單」,不看「測試檔有沒有改」。實作 PR 不碰計劃就整條不跑。
   引句:「在 head 版本存在的計劃檔」
severity: major
   blocking: 是,該擋的放掉。
   - 重現:
     - PR1 只合計劃(設計先行)。
     - PR2 加程式與測試 `t_s3`(內容 `assert True`),計劃檔一個字沒動。
     - PR2 的改檔清單裡沒有任何 `_計劃.md`,第 2 點選出 0 份計劃,rc0,也沒有事件。
     - 假測試永遠不會被重播。
   - 反過來看,碰了計劃檔的 PR 才被檢查(第 2 條)。
   - 要補一條反向選取:改檔清單裡的測試被哪些風險高計劃的新行為條款綁到,就選那些計劃。

4. 全標 keeps 的計劃在 S8 被永久擋住,跟「全標 keeps 不要求表」矛盾,r4 的死鎖只修了表那一半。
   引句:「全部條款都標 keeps、或標 keeps 的測試在計劃建立前不存在時」
severity: major
   blocking: 是,把不該擋的擋下:純重構、維持既有行為的風險高計劃(例如動到金流節點)沒有合法的過法。
   - 重現:
     - 風險高計劃,所有條款都標 `[keeps]`,測試都是計劃建立前就存在的綠測試。
     - 第 3 點呼叫 `_spec_gate_twoway_static`:`if not [b for b in clauses if b["id"] not in keeps]` 命中,回 (…, True),即「全部條款都標 [keeps]…等於什麼都沒驗」,這算「確定不過」,rc1。
     - 計劃每被任何 PR 碰一次就擋一次。
   - 同一份 spec 的 S14 與 r4 的 G4 結論是「全標 keeps 的計劃不要求表」,明確承認這類計劃存在。
   - `base_replay_skip` 也繞不過,因為它只跳過第 4、5 點,靜態檢查在第 3 點。
   - 出口只剩關掉整個 gate。file: `scripts/lumos:14218`。

5. 把風險低專用的「測試要存在」檢查原樣套到風險高,擋掉「設計先行」的計劃 PR。
   引句:「重播前在 head 那份計劃上呼叫」
severity: major
   blocking: 是,把不該擋的擋下。
   - 現況:`_clause_check_twoway` 只在 `door == "low"` 才呼叫(`scripts/lumos:14788`),所以風險高計劃在設計階段綁還不存在的測試名,今天是合法的。
   - 重現:風險高計劃在設計審後先以文件 PR 合進主線,測試名都還是懸空(之後的批次才寫)。
     - PR 檢查呼叫 `_clause_check_twoway`,懸空得到「風險低的測試要真的存在:先把測試寫出來」,rc1。
     - 這個擋是 spec 新加的,舊流程沒有。
     - 本計劃自己的 S1..S22 都綁了尚未存在的 `t_pr_evidence_*`,以「先合計劃、後合實作」的流程進主線就會被自己擋。
   - 若 spec 的本意是「計劃與測試必須同一個 PR 進來」,要寫明。
   - 同一條也把 S8 的「兩條新行為條款綁同一支測試」這個風險低規則整批套到風險高。這可能是刻意的,但沒有理由紀錄。

6. 弱證據(測試被跳過、沒被收集到、名字撞名)全部當「判不了、不擋」。理由「CI 全套本來就會擋」不成立,明顯的假測試溜過。
   引句:「CI 的全套測試本來就會擋」
severity: major
   blocking: 是,該擋的放掉:風險高的路徑比風險低更鬆。
   - 重現:
     - 新行為測試加上跳過標記(`@unittest.skip`、`@Ignore`)。
     - `_spec_gate_verdict` 對「那一支被跳過」回 `weak`(`scripts/lumos:15057`)。
     - 分岔點是 weak,head 也是 weak,S7 判不了、不擋。
     - CI 全套把 skipped 當 rc0,綠,不會擋。
   - 對照:風險低的 `_spec_gate_twoway_run_verdict` 對這種情況明確寫「弱證據不算紅」並判不過(`scripts/lumos:14242`)。
   - 同類的輸入還有:測試名是別支測試名的子字串(`-k` 子字串選中多支,`n >= 2 and declared != 1` 也是 weak);篩選選到 0 支。
   - 這些都是「測試沒在跑」的直接證據,不是「證明不了」。head 上的 weak 至少該擋,或在 head 上的弱證據算 CI 已知的漏洞並寫進天花板。

7. 「整支包一層例外即放行」會把已經判定要擋的計劃一起吞掉。
   引句:「任何沒預期的例外都印原因」
severity: major
   blocking: 是,該擋的放掉。
   - 重現:
     - 一個 PR 改兩份計劃 A、B。A 先判出 `base-replay-failed`(待擋)。
     - 處理 B 時丟出例外(例如 `_run_bound_tests` 在同時跑模式把工作執行緒的例外往外丟,`scripts/lumos:69136`;或單一計劃擋下後寫事件丟 OSError)。
     - 外層統一印原因、寫 `pr-evidence-skipped`、rc0,A 的擋被吞。
   - 另一個入口:作者能在同一個 PR 放一份會讓解析或重播丟例外的計劃,讓整個檢查退成 rc0。
   - 要改成逐份計劃各包一層,例外只讓那一份變「判不了」,最後的 rc 由已判定的結果聚合。S4 的測試也要跟著改。

8. 檢查寫的所有事件都落在 CI 暫時工作目錄的治理帳,沒有人讀得到。RETIRE-IF 與 REVISIT 的分母永遠是 0。
   引句:「兩種擋下事件都是 0」
severity: major
   blocking: 是,判錯方向:回頭條件會在沒有任何資料時恆真。
   - 重現:
     - `pr-evidence` 在 CI 的 pull_request 事件跑,workflow 的 `permissions: contents: read`(file: `.github/workflows/ci.yml:15`)。
     - 事件追加到執行器檢出目錄的 `docs/.governance-log.jsonl`,工作結束就丟了,不會進任何分支。
     - 90 天後 `base-replay-failed` 與 `expected-unsigned` 兩種計數必然為 0,RETIRE-IF 第一個條件恆真,會把有在擋的 gate 撤掉。
     - REVISIT 2027-02-04 的「判不了佔比」查不到資料。
     - 「帶計劃與支數,回頭條件數得到分母」的 `base-replay-proven` 也是同一個命運。
   - 連帶:消費專案 CI 若用預設的淺檢出(深度 1),merge-base 算不出,會被當 `pr-evidence-skipped` 靜默 rc0,而這個事件同樣看不到,誰也不知道檢查根本沒在跑。
   - 要嘛 CI 把事件另存(artifact、PR 註解、job summary)並明定回頭條件讀哪裡,要嘛改用 CI 看得到的計數來源。

9. S6 與 S7 的優先順序沒定,「對照組不綠」與「新行為在分岔點綠」同時成立時會判成判不了。
   引句:「分岔點是弱證據或逾時、或平台釘不住版本時」
severity: minor
   blocking: 否:第 5 點條文順序隱含「擋」優先,但 S7 的句子是無條件的。實作者若照 S7 先寫,會把本來該擋的放掉。
   - 場景:一份計劃有一支在分岔點就綠的假測試,同時有一個 keeps 測試因環境或 flaky 在分岔點紅。S7 字面是「判不了、不擋」,S6 是「回 1」。
   - 要在 S7 加「沒有任何新行為測試在分岔點綠時」這個前提。⚠ 兩邊字面都能讀成對。

10. 「用 `_platform_test_index` 找每支測試在哪個檔」,這支函式沒有檔案對照。
    引句:「用 head 那棵樹的 `_platform_test_index` 找每支測試在哪個檔」
severity: minor
    blocking: 否:可用 `_walk_test_files(with_path=True)` 補(file: `scripts/lumos:6735`),不影響 spec 的方向,但選取規則(第 1、2 條的根)還沒定義。
    - 驗證:`_platform_test_index` 回 (pdata, split, default, methods_for, hay_for, loose_for)(file: `scripts/lumos:23525`),`methods_for` 只回名字集合。
    - 同名測試在兩個檔(一個改到、一個沒改到)時,「定義在改檔清單裡」是任一還是全部,spec 沒講。
    - 實跑時 `-k` 子字串會選中兩支,走 weak(判不了),所以不會誤擋,但也不會被檢查。

11. 靜態檢查與門判定讀的是工作目錄(CI 是 merge 提交),不是 head。
    引句:「用 `_note_text_at_rev` 讀 head 版本的計劃文字」
severity: minor
    blocking: 否:兩棵樹在多數 PR 差距很小。
    - `_door_judge(env, note, text)` 的連結節點與合約來自工作目錄的圖譜(file: `scripts/lumos:14007`)。
    - 條款綁定狀態(懸空、real)的測試方法集同樣來自 `_platform_test_index(rr)`。
    - CI 的工作目錄是 `refs/pull/N/merge`,含 main 往前走的內容。
    - 場景:主線在 PR 開出後刪掉或改名了某支被綁的測試,head 仍有。工作目錄版本判懸空,誤擋。
    - spec 沒說這幾步該用 head 那棵樹還是工作目錄。⚠ 要寫明。

12. `base_replay_skip` 是同一個 PR 裡自己寫的欄位,只要字數夠就跳過唯一會擋的重播。
    引句:「是字串、用 `_real_chars` 數至少 10 個字時」
severity: minor
    blocking: 否:這是 spec 有意識的出口,有事件、有世界做法為先例(devops-cli)。
    - 場景:被 S6 擋下後,作者加一行 10 字理由即可過,沒有簽核、沒有互動終端確認。
    - 對照:lint-waive 用 `_waive_origin_tty` 記 human 或 ai 並列在 doctor。
    - 這一道是 d3 的取捨,我只標出它讓「唯一的擋」成為自助可關。
    - 配合第 8 條,連事件都看不到,這個出口實際上沒有任何回頭機制。

13. 覆蓋測試檔「不帶檔案模式」,以 shell 腳本為測試的專案,新測試在分岔點因無執行位元而紅,被當證實。
    引句:「只搬內容、不帶檔案模式」
severity: minor
    blocking: 否:只影響以可執行腳本當測試的消費專案。
    - 場景:`tests/run_x.sh` 以 `./tests/run_x.sh` 執行。分岔點那棵複製出來是 0644,permission denied 得 rc≠0,判紅。
    - 假測試(內容 `exit 0`)就變成「分岔點紅、head 綠」的證實。
    - ⚠ 取決於各專案的 `run_cmd` 形狀。

14. 不設總預算與 CI 工作逾時的關係:逾時是 fail-closed,與「工具壞了不擋所有人」矛盾。
    引句:「整體上限交給 CI 工作的 timeout-minutes」
severity: minor
    blocking: 否:機率低,多見於 Android 冷樹。
    - 單支預設 900 秒、兩棵樹、多份計劃,沒有總預算。
    - `.github/workflows/ci.yml` 的 prep 逾時 15 分、gates 逾時 20 分。
    - 場景:重播吃滿 job 逾時,整個 job 變紅,PR 被擋住,沒有任何「判不了」事件。
    - 這與第 1 點 fail-open 約定相反,也與 spec 自己說「冷樹第一次編譯要幾分鐘」衝突。
    - ⚠ 該寫明是接受的。

## 本鏡頭其他點的答覆(沒有 finding 的)

- **PR 目標分支往前走過、`base.sha` 與 merge-base 不同**:已讀,無 finding。
  - 兩種情形都算得對:head 沒併 main(merge-base 是更早的分岔點),或 head 併了 main(merge-base 落在被併入的主線提交上),diff 都只含這個 PR 的改動。
  - base.sha 在重跑時變舊也沒影響,因為只取 merge-base。
- **一個 PR 改多份計劃**:共用兩棵樹的結構本身沒問題。問題出在第 7 條(例外聚合)。測試在樹上留的檔案會在計劃之間共用,但每支測試各自的 `-k` 篩選不受影響,無新 finding。
- **同名測試在不同檔**:不會誤擋,會走 weak 判不了,同時也繞過檢查。見第 10 條與第 6 條。
- **keeps 與新行為在同一檔**:整檔從 head 覆蓋到分岔點。keeps 若被改動而在分岔點變紅,只會讓「證實」不成立,不影響擋(擋與 keeps 無關),所以不構成繞過。這一條已讀,無 finding。
- **測試檔被刪**:分岔點也刪;被綁的測試在 head 變懸空,走靜態檢查擋下,方向正確。無 finding。
- **PR 來自 fork**:無新 finding。`head.sha` 在合併提交歷史裡拿得到,工作流程 `permissions: contents: read` 沒有祕密可外洩。fork 的測試碼在 CI 執行,與既有 shards 同一種暴露。
  - 備註:`pr-evidence` 與 workflow 都是 PR 自己版本的程式,PR 可以改掉檢查本身。這是 CI 通用屬性,在單人信賴模型下接受。
- **例外即放行吞掉該擋的**:見第 7 條。
- **併發**:無新 finding。
  - 同一 PR 連推由 `concurrency` 取消舊的。
  - 兩個 PR 各自 `mkdtemp`,樹路徑不同。
  - 殘骸清理一天後才清,不會清到正在跑的。
  - 同一個本機同時跑兩次 `pr-evidence`,清理與執行的重疊窗口遠小於一天。
- **效能**:
  - 單支約 2.7 秒,2 棵樹 × 22 支約 2 分鐘,可接受。
  - 但第 2 條會讓這個 repo 的每個碰計劃的 PR 都重播整份計劃,放大 N 倍。
  - 無總預算見第 14 條。
- **資源**:無新 finding。樹與暫存目錄離開時收掉,`TMPDIR` 指到樹下,紅燈現場跟著收。
- **回滾**:無新 finding。三種關法由輕到重寫得清楚,事件追加無害。
  - 例外:第 8 條讓「用事件確認有沒有擋到人」這個回滾判斷依據失效。
- **「唯一會擋的只有舊程式上就綠」的取捨**:會讓明顯假測試溜過的是第 6 條(跳過、沒收集、撞名)與第 1、3 條(根本沒選到)。
  - 「分岔點因匯入或編譯失敗而紅」的假測試已在天花板四承認,留第二批。

## 圖譜鏡頭(固定席)

- `Systems/lumos-cli-lifecycle` 的 ★INVARIANT★(re-inject 只覆蓋 sentinel 之間、之外 byte-equal):不影響。第 10 點只說「重新注入本 repo 的 CLAUDE.md 與 AGENTS.md」,走既有的注入流程,沒有新增覆蓋 sentinel 之外的寫入。
- `Systems/test-quality-cli` / `scripts/test_quality.py` 的部署指紋:不影響。計劃只借不改。
- `Systems/test-quality-evidence`、`Verification/測試品質第四輪修補驗證`:不影響。基準重播不改那條證據線,第 4 條也不動它的 `_RAN_EVIDENCE`。

最嚴重 severity 為 blocker(第 1 條);blocking 共 8 條(blocker 1、major 7),minor 共 6 條(第 9 至 14 條)。
