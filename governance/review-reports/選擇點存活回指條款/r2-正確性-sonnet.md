severity: major

審查範圍:逐節讀完整份 spec,對照 `scripts/lumos` 與 `scripts/test_quality.py`。內部交叉引用(範圍 9 的有效表、範圍 8 的 `--redo`、`--withdraw`、各 S 條款)都對得上。另外 `NoDtdTreeBuilder` 我實跑過:帶外部 DOCTYPE、內部子集、`SYSTEM` 宣告的字串都丟 `JUnitRejected`,不帶 DOCTYPE 的字串能解析,所以「先剝掉固定那一行再交給它」可行。

1. 範圍 1、WHY(覆蓋掛在既有的單支基準上)的前提不成立。
   - spec 說基準「本來就」每支各跑一次,覆蓋是順便掛上去的。實際上 `cmd_guard_kill` 的基準是惰性的:`if cmd not in baselines` 才量(`scripts/lumos:28498`),而且壞法一被殺掉整組就停,多數測試根本沒量過基準。
   - 只有合併快篩可用時,`_kill_merge_singles` 才會預先量齊;`--no-merge`、`LUMOS_SKIP_CHOICE_MERGE=1`、合併基準不通過時都沒有預先量。
   - 這些情況下覆蓋基準是「額外多跑一整輪全部守的測試」,不是多 1.4 秒。169 支測試約 17 分鐘以上,預設 `--max-seconds` 是 1800(`scripts/lumos:78739`)。
   - spec 沒有 `_kill_merge_singles` 那種「估不夠就收手」的機制。時限在覆蓋基準中途到,依範圍 1 沒跑到的算不明,依 S7 的收法也不寫 reach 事件,壞法一個都沒跑。下次重跑又從頭量同一輪。
   - 速度保證(使用者 2026-11-26 原話)在這些情況下做不到。
引句:「choice-kill 本來就要在原版程式上把每支守的測試各單獨跑一次量基準」
severity: major
blocking: 是

2. 範圍 1 把另一棵工作樹量到的基準交給 `cmd_guard_kill`,會讓壞法逾時被誤判。
   - choice-kill 在自己的 `lumos-kill-` 樹量基準,`cmd_guard_kill` 又在自己的 `_isolated_worktree` 跑壞法。那棵新樹沒有任何建置輸出,第一個壞法的跑法要冷編譯。
   - 壞法逾時是 `max(b_elapsed * 5, floor)`(`scripts/lumos:28547`)。`b_elapsed` 來自另一棵樹、已暖機的約 6 秒基準,上限約 30 秒,冷編譯整個專案遠超過。
   - 結果是 `timed_out_weak`,而它在 `_CHOICE_STOP_ON` 裡屬決定性結果,整個壞法記成 no_result「測試掛住」。
   - 現行流程基準與壞法在同一棵樹,基準先暖機。`_kill_merge_singles` 也特別註明「第一支含冷編譯,不拿來估」,正是這個原因。
   - 合併基準的上限 `_choice_merge_base_cap(sum(基準耗時))`(`scripts/lumos:28852`)同樣會因為匯入的基準沒含冷編譯而太小。
   - spec 的假 Gradle 測試(S5)測不出這個問題。
引句:「這些基準交給 `cmd_guard_kill` 的新選用參數 `baselines`」
severity: major
blocking: 是

3. 〈用詞〉「覆蓋可信」與範圍 2 的報告內容互相矛盾,會讓 `none` 幾乎出不來,斷路器也會誤跳。
   - 〈用詞〉要求「整份報告(全模組)行覆蓋數大於 0」;範圍 2 又說報告「只含改到的檔的類別」。
   - 照字面,一支沒碰到改動檔的測試(多數守的測試都是這樣),報告裡行覆蓋是 0,被判「不可信」。這支測試對所有行算不明。
   - 於是只要有一支測試沒碰到改動檔,而其餘測試都沒經過這一行,這一行就是 `unknown`,永遠分不到 `none`。S2 的「覆蓋都可信」永遠湊不齊。
   - 範圍 1 的斷路器「前 5 支測試都不可信」,在前 5 支恰好是測別處的測試時會誤跳,整次 run 關掉覆蓋。
   - 要偵測 `includeNoLocationClasses` 沒生效,需要另一個真正的「全模組」或哨兵類別,spec 沒給。
引句:「整份報告(全模組)行覆蓋數大於 0、而且改到的檔在報告裡有這一行的 `<line>` 紀錄」
severity: major
blocking: 是

4. 範圍 3 依覆蓋選測試時,把覆蓋「不明」的測試排除,會漏掉真正的殺手。
   - 〈用詞〉只處理「其餘測試都沒經過」才算 `unknown`。若測試 tA 的報告顯示經過(斷言很弱),測試 tB 的報告沒產出或讀不了(實際會殺掉這個壞法),分類是 `clause`。
   - 範圍 3 只留「經過那一行」的測試,tB 不在清單裡,壞法在 tA 上存活,被記成存活。
   - 這是錯的結論,而且 `reach_why` 不會留下 tB 被略過的痕跡。S1 與 S3 的案例都沒涵蓋「一支經過、另一支不明」的組合。
引句:「每個壞法交給 `cmd_guard_kill` 的測試清單只留經過那一行的守的測試」
severity: major
blocking: 是

5. 〈實務隱患〉對「行內函式」的補救只涵蓋「報告沒有那一行」,漏了「有紀錄但是 `ci=0`」。⚠ 這條我沒實跑 JaCoCo,交編排者用實驗專案驗。
   - Kotlin `inline fun` 的本體在呼叫端被複製進呼叫端的類別。JaCoCo 不處理 SMAP,所以原函式本體那幾行仍有 `<line>` 紀錄,而且沒被當一般函式呼叫時 `ci=0`。
   - 改壞行內函式的某一行,會被每個呼叫端的測試殺掉,但每支測試在原版報告裡這一行都是 `ci=0`,被分成 `none`,壞法不跑,直接記存活。
   - 這是一個真能被殺掉卻被記存活的壞法,結論由殺掉翻成存活,而且擋推送。
   - 同樣的形狀也出現在 `const val` 之類編譯期被內聯的值,有 `<line>` 但沒有執行。
引句:「例外:靜態初始化與行內函式的行號歸屬不準,報告沒有那一行的紀錄就記不明、照跑全部測試」
severity: major
blocking: 是

6. 範圍 3 讓 `none` 的行不跑壞法就記存活,跟第三道「編不過不是壞法」互相矛盾。
   - 沒有測試經過的行,壞法從沒被編譯過。若那個壞法編不過(型別前提沒擋到),會被記成存活並擋推送,人被要求去補一個永遠不會發生的邊界測試。
   - 〈WHY〉第三道明寫「不選:記成跑不出結果交人處置(讓人查一個不存在的問題)」,範圍 3 恰好製造這個問題。
   - 無效壞法記憶只在有跑的行才會產生資料。spec 沒給 `none` 行的編譯驗證路徑。
引句:「覆蓋分類 `none` 的行不交,choice-kill 直接記 `verdict: "survived"`、`via: "cov"`」
severity: major
blocking: 是

7. 範圍 9 的有效表讓處置一條存活就作廢別條第 1、4 層判讀,跟 WHY 與〈白話〉的承諾矛盾。
   - 第 1、4 層的有效條件是「碰到的每份計劃的條款全文加正文雜湊沒變」。
   - 第 1 層的處置(`situation-rule --clause`)與第 2、3 層的處置,都會在計劃裡新增條款或改動條款綁的測試。
   - 計劃的「條款全文」變了,同一份計劃底下所有其他第 1、4 層判讀全部作廢,下次 `--template` 全部重出。
   - 這正是 WHY(每筆判讀只綁它依據的東西)要避免的 n 個存活重判 n 次的 n² 問題,〈白話〉也寫「依據沒變就一直有效,處置一條不會讓別條作廢」。〈實務隱患〉判讀成本一條同樣宣稱不會重判。
   - S15 只測了「改別條條款不影響第 3 層」,沒測第 1、4 層。
引句:「雜湊(不含 frontmatter 與審計修正紀錄)沒變」
severity: major
blocking: 是

8. 範圍 5 說 gov「第一次判定」照舊數 `attempt == 1`,但現行判法還要求 `via == "run"`。
   - `_gov_choice_count_verdict` 是 `attempt == 1 and via == "run"` 才算第一次自動跑(`scripts/lumos:17962`)。
   - 範圍 3 的 cov 存活事件帶 `via: "cov"`,不會被數進 `c["first"]`。殺掉率分母漏掉所有沒測試經過的存活,被回報的存活數(RETIRE-IF 分母)與第一次判定的比例從此對不上。
   - spec 也沒寫 cov 事件的 `attempt` 欄值。`self.attempts[key]` 只在 `finish` 路徑遞增。
   - S10 只驗「有 reach、layer 事件時第一次判定不變」,驗不到這個缺口。
引句:「照舊數 `attempt == 1`;換候選的壞法事件帶 `candidate`」
severity: major
blocking: 是

9. 範圍 8 的分份規則沒定義「沒有計劃可歸」與「跨多份計劃」的存活。
   - 規則是同一份計劃的存活放同一份,但 reach 為 `none` 或 `unknown` 的行沒有條款經過,不屬任何計劃。
   - 一行的 `reach_clauses` 可能跨計劃 P 與 Q,也沒說放哪一份。治理帳 `plans` 欄放的是全部進行中計劃,不是條款所屬計劃。
   - S13 只示範「P 22 個、Q 3 個」的乾淨分法。照字面實作,`none` 的行(正好是最需要判讀第 1、2 層的那一批)可能不出現在任何一份材料裡。
引句:「分份:同一份計劃的存活放在同一份、每份最多 20 個存活」
severity: major
blocking: 是

10. 範圍 5 的 `exhausted` 處置分支在現行資料流裡走不到。
    - 範圍 5 要求 `_choice_pick` 帶 `skip`,而且 choice-points、推送前掃描、`situation-rule --point` 都用同一份。
    - `skip` 把所有候選都濾掉時,`_choice_pick` 回 `None`,`_choice_file_points` 設 `status="none"`(`scripts/lumos:78543`)。`_choice_kill_pick`、`_choice_push_judge`、`_situation_rule_point_target` 都只處理 `mutant`、`not_unique`,不會把這一行交給 `_choice_disposition`。
    - 所以「`no_result` 加 `exhausted` 回 `"exhausted"`」從來不會被呼叫到,`exhausted` 事件也沒有讀者。S17 要的「不擋、不重跑」靠 `status=none` 就達成。
    - 範圍 10 印「沒有可用壞法」要走 `mut is None` 那一條(`scripts/lumos:78662`),要改的是那裡,不是處置判定。
引句:「最新一筆壞法事件是 `no_result` 而且同一行同一 blob 有對得上的 `exhausted` 時」
severity: minor
blocking: 否

11. 無效壞法的有效期只綁那一支檔的 blob,編譯能不能過其實取決於整個專案。
    - 型別推論、簽名、其他檔新增的函式,都會讓同一個 `new_sha` 在檔沒變的情況下由編不過變成編得過,或相反。
    - 這一行檔沒變,就一直被當作「沒有可用壞法」不擋,真正有效的壞法被靜默跳過。
    - 〈天花板〉7 只講「錯誤報在別支檔」,沒講記憶過期的問題。
引句:「在那支檔的內容(git blob)下編不過」
severity: minor
blocking: 否

12. 範圍 3「合併快篩只合併選到的測試」與合併快篩的現行結構對不上。
    - 合併快篩的合併指令 `mcmd` 在 `_kill_merge_iter` 對整個平台組只組一次,涵蓋整個 `lane`(`scripts/lumos:29101` 起的 `_kill_merge_base`)。每個壞法共用同一個指令與基準耗時 `m_el`。
    - 「每個壞法只合併選到的子集」要重組合併指令與合併基準,spec 沒說怎麼做。
    - 字面不改的話,合併快篩仍然跑全部測試,速度承諾落空。
引句:「合併快篩只合併選到的測試」
severity: minor
blocking: 否

13. 範圍 7 的「有效 reach」沒有定義,`cov_sha` 也沒有讀者。
    - 〈用詞〉有「判讀有效」,卻沒有「reach 有效」的定義。範圍 7 只說 `unknown` 不算有效,範圍 4 記了 `cov_sha`,沒有任何讀者比對它。
    - 計劃改了條款綁的測試後,choice-points 與 `--reach-only` 仍用舊的 `reach_clauses`,印出過期的條款號。S15 把「改了 S3 文字」寫成改印覆蓋分類加「未判讀」,但印的分類本身可能已過期。
引句:「對帳上目前是存活、而且沒有有效 reach 的行補 reach 事件」
severity: minor
blocking: 否

14. 範圍 1、2「報告只含改到的檔的類別」沒說 `.kt` 檔怎麼對到 `.class`。
    - 一支 Kotlin 檔會產生 `FooKt`、`Foo`、`Foo$Companion`、`Foo$bar$1` 等多個類別。JaCoCo 報告任務的 `classDirectories` 是檔案樹,過濾不到 `sourcefile` 屬性。
    - 選不全時,落在遺漏類別的行會變成 `unknown`(安全方向),但選擇機制本身沒寫,是可執行性缺口。
引句:「每份報告先看大小(上限 32 MiB,常數 `_CHOICE_COV_FILE_MAX`;只含改到的檔的類別」
severity: minor
blocking: 否

15. 覆蓋只看「壞法行」一行,但壞法的編輯可能散在多行。⚠ 影響要用實例確認。
    - `_choice_anchor_edits`(`scripts/lumos:78316`)的 `!!` 可以插在前一行結尾,`drop_call` 刪到尾隨 lambda 結尾。
    - 範圍 1 與〈用詞〉「經過」只以錨點行 `ci>0` 判斷。編輯區間的其他行沒有納入,JaCoCo 對換行呼叫的行歸屬又不一定落在錨點行,可能被誤分成 `none`。
引句:「每個壞法行一個:`clause`(列出經過的條款)」
severity: minor
blocking: 否

16. 範圍 2 沒寫 `test_quality` 載入失敗的路徑。
    - `scripts/lumos` 是用 `_test_quality_load_bundle`(`scripts/lumos:82307`,有雜湊釘版)載入 `test_quality.py`,載入可能回 `None`。
    - 〈範圍〉4 的 `reach_why` 字串表沒有對應原因,「報告讀不了」不是同一件事。
引句:「再用 `test_quality.py` 既有的拒收 DTD 的解析器(`NoDtdTreeBuilder`)解析」
severity: minor
blocking: 否

17. 〈實務隱患〉「守衛面」引用的條款不對。
    - 文字寫「S9、S16、S19 守住擋不擋」。S19 是「編譯失敗尾段沒有指到被改的檔記 `no_result`」,不是擋不擋的守衛。
    - 真正守「讀者不被新事件改變」的是 S10。
引句:「S9、S16、S19 守住擋不擋」

severity: minor
blocking: 否

固定席節點逐條判:
- `Systems/guard-kill` 的兩條 ★INVARIANT★:`baselines` 是選用參數,沒傳就走原本流程。rc 優先序與 `--json` 純度都不經過這個參數,不影響。但第 2 條的「基準從另一棵樹匯入」會改變 `timed_out_weak` 的出現率,間接影響 rc,已列為第 2 條 finding。
- `Systems/規格閘`(0 條合約):`choice-layer`、`reach` 等新事件落在它的家,不影響既有合約。
- `Systems/bound-tests-gate`、`Systems/lumos-cli-read`、`Systems/lumos-cli-lifecycle`:不碰測試綁定閘、搜尋濾網與 re-inject,不影響。
- `Systems/test-quality-cli`、`Verification/測試品質第四輪修補驗證`:只重用 `NoDtdTreeBuilder`,不改它,檔案雜湊不變,不影響。
- `Systems/pitfalls-code-loop`(★RISK★):這份不碰 `pitfalls` 的分級,不影響。

實務隱患鏡頭逐類:
- 資源與時間:有隱患,見第 1、2、12 條。
- 正確性(誤判存活或殺掉):有隱患,見第 3、4、5、6、15 條。
- 治理帳與統計:有隱患,見第 8、10、13 條。
- 併發與交易:無,單人依序操作(spec 已排除)。
- 金流與對外送出:無,只讀測試覆蓋、不對外送資料。
- 不可逆:無,帳只追加,判讀用補償事件撤回。
- 資安(XML 解析):無,`NoDtdTreeBuilder` 實跑會拒 DTD 與內部子集,32 MiB 大小上限也在解析前檢查。

臨時目錄 `/tmp/lumos-seat-work/選擇點存活回指條款/正確性-sonnet/` 內只留了一支實驗腳本,已用字面絕對路徑刪除,目錄本身是空的。

總結:最高等級是 major,blocking 共 9 條
