severity: blocker

(圖譜鏡頭:`Systems/guard-kill` 的兩條 INVARIANT(rc 優先序、`--json` 純淨)不受影響。spec 只新增選用的 `prep` 參數,沒交時行為不變,且不碰 rc 與 JSON 輸出,所以判不影響。`Systems/規格閘` 是落點,不是約束。)

**1. 合批編譯檢查沒有先驗未改動的樹,環境壞掉時所有壞法會被判成無效,推送閘因此放行**

〈用詞〉只定義了「對不回就逐個編譯找元凶」。spec 沒有要求先編一次未改動的樹作對照,也沒寫編譯逾時或 rc≠0 但輸出沒有 `e:` 行時怎麼處理。依程式現況,`_KILL_COMPILE_RE` 的 `Execution failed for task ':x:compileXKotlin'` 分支不帶檔名行號,依賴下載失敗、daemon 掛掉、基礎樹本來就編不過都會落進這條。結果是逐個編每個壞法都紅,全部記 `invalid`,整行 `exhausted`,而 `exhausted` 不擋。
- 空輸入(零個壞法):未涵蓋。
- 上百個壞法:每個壞法都被誤判為無效。

severity: blocker
blocking: 是
引句:「對不回的錯誤(在沒有壞法的檔或行)整批改成逐個編譯找出元凶;最後還原。」

**2. 對回壞法只看「檔與行落在壞法改的行範圍」,錯誤歸錯人時有效壞法會被永久記成無效**

編譯錯誤常常不在改壞的那一行,例如改了回傳型別,錯誤出在同檔另一個壞法的行。那個無辜壞法會被記 `invalid`,真正的元凶則進下一批才露出。無效判定沒有任何單獨重編確認。ceiling 7 只說「對不回時本來就會逐個編」,沒涵蓋「對錯人」。同一函式內相鄰行的壞法最容易遇到,一旦候選全被這樣誤殺,該行就變成 `exhausted`,推送閘放行。

severity: major
blocking: 是
引句:「讀編譯錯誤的檔與行,對回壞法(壞法改的行範圍含那一行)」

**3. 準備物件掛在 `_kill_merge_iter` 裡,合併快篩不成立時合批編譯檢查與覆蓋整個被略過**

`cmd_guard_kill` 只在 `merge` 有給時才走 `_kill_merge_iter`(`scripts/lumos:28483`)。`--no-merge`、環境變數 `LUMOS_SKIP_CHOICE_MERGE=1` 都讓 `mctx is None`,`prep` 不會被呼叫。`_kill_merge_ready` 也有多個回 None 的路徑:平台不穩、指令形狀不支援、名稱檢查沒過、守的測試少於 2 支、時限不夠,此時 `_kill_merge_iter` 直接 `yield from c.plist`。spec 只把 `--reach-only` 與 `--no-merge` 列為衝突,一般 run 在這些情況下沒說會怎樣。

- 守的測試只有 1 支:覆蓋與編譯檢查靜默失效。
- 未寫的對照行為:失效後 `no_result`「壞法編不過」舊行為復活。

severity: major
blocking: 是
引句:「guard-kill 在 `_kill_merge_iter` 先量齊基準的同一個位置呼叫它」

**4. 續跑快取鍵少了「壞法行集合」,而且「經過的壞法行」要到分析階段才算得出來**

快取存的是「專案類別有紀錄數、經過的壞法行」,鍵是平台、測試名、測試檔 blob,範圍只到 `at_sha`。但分析在全部基準跑完之後才做,被中斷的 run 根本沒有「經過的壞法行」可存。`.exec` 又放在 `wt.scratch`,中斷後樹被清掉。續跑時壞法集合可能不同:`--max-mutants`、`--only`、候選換過、`--diff` 範圍不同。快取裡沒有的行若被當成「沒經過」,就會記成 `none` 而直接存活。

severity: major
blocking: 是
引句:「每支測試的覆蓋結果(專案類別有紀錄數、經過的壞法行)寫進」

**5. 覆蓋基準沒有預留時間給壞法階段,守的測試一多整次預算被吃光**

預設 `--max-seconds` 是 1800(`scripts/lumos:82900`)。每支測試掛覆蓋約 6.2 秒,守的測試上千支約要 100 分鐘。spec 只寫「不夠就停」,沒定義「不夠」的門檻,也沒有像 `_kill_merge_ready` 那樣先用 `支數 × 單價 × K` 預判。後果:
- 覆蓋跑到一半就沒時間了,沒跑到的測試算不明,「有任一支不明」讓全部行變 `unknown`,覆蓋白做。
- 壞法階段沒有剩餘時間可跑。
- 合批編譯檢查的批數(一行上百個候選時)也不受總時限約束。

severity: major
blocking: 是
引句:「每支開跑前看 `--max-seconds` 剩下多少,不夠就停,沒跑到的測試算不明」

**6. 「14 天清檔」是對現有程式的錯誤假設**

`_note_audit_work_dir`(`scripts/lumos:56728`)只清頂層的 `d.glob("*.md")`,且該目錄只做符號連結拒用與 `.gitignore`。`choice-cov/<at_sha>/` 的 `.json`、`choice-layer/*.json` 與子目錄都不會被清。回退節 4 也把清理押在這條規則上,實際上沒有人清,暫存會無限累積(使用者正好為此裁過暫存清理規則)。

severity: major
blocking: 是
引句:「符號連結拒用、自帶 `.gitignore`、14 天清檔」

**7. 沒寫「跑每支測試前先刪 AGP 固定位置的舊 `.exec`」,會把上一支的覆蓋複製成這一支的**

PITFALL 已證實檔案固定寫在 `build/outputs/unit_test_code_coverage/<變體>UnitTest/`。如果某支測試沒產出(紅、被篩掉、Gradle UP-TO-DATE 或 FROM-CACHE),「跑完複製出來」就會抄到上一支留下的檔。
- 錯誤歸屬:覆蓋資料被算到錯的測試名下,`none` 與 `clause` 都可能判錯。
- `reach_why`「覆蓋資料沒產出」只有在複製前先清掉舊檔時才抓得到。

severity: major
blocking: 是
引句:「修法:每支跑完從 AGP 的固定位置複製出來」

**8. 「reach 有效」排除 `unknown`,與輸出「覆蓋不明(<原因>)」互相矛盾,`--reach-only` 還會對永遠 unknown 的行重跑**

範圍 6 規定有效 reach 不能是 `unknown`。範圍 10 又說沒有有效 reach 印 `未分類`、有 reach 才印 `覆蓋不明(<原因>)`。所以已記下的 `unknown` reach 永遠印不出 `覆蓋不明`,`reach_why` 整欄是死資料。對 `inline fun`、`const val` 這類永遠 `unknown` 的行,`--reach-only` 每次都把它當「沒有有效 reach」重跑覆蓋基準。S11 的預期值表(「reach `unknown` 那行補」)正好吃這個洞。

severity: major
blocking: 是
引句:「最新一筆 reach 的 `cov_sha` 等於現在算出的值,而且 `reach` 不是 `unknown`。」

**9. `skip` 取「最近一次 run」的 invalid 集合,不累積,候選會在 run 之間來回打轉**

第 1 次 run 記了候選 1 無效。第 2 次 run 以 `skip={1}` 挑到候選 2,又發現它無效並記一筆。第 3 次 run 的「最近一次 run 的 invalid」只剩候選 2,於是回頭挑候選 1,又得重新編譯。若第 2 次 run 沒有新 invalid(例如 `compile_cmd` 關掉),集合就是空的。S17 要求 `choice-points`、`situation-rule --point` 與實跑挑同一個候選,字面實作做不到。回退節 2 說「仍讀帳上 invalid」,與「最近一次 run」互相矛盾。

severity: major
blocking: 是
引句:「`_choice_pick` 多一個 `skip`(這一行最近一次 run 的 invalid `new_sha` 集合)」

**10. `cov_sha` 對 `none` 的行幾乎只剩壞法檔 blob,補測試之後存活會被永遠帶過去**

`cov_sha` 只算「經過或可能經過這一行的守的測試」。`none` 的行沒有經過的測試,其中只剩壞法所在檔 blob。這時使用者為這行補了一支測試(第 3 層的修法本身),`cov_sha` 沒變。
- 範圍 6 寫「`cov_sha` 相同才帶過去,否則重跑;其餘照現在」。「其餘」是否仍含現有 `tests_sha` 比對沒說。
- 若新規則取代了 `tests_sha`,新測試殺不到那個壞法,「補到壞法被殺掉才算處置完」就達不到。

⚠ 交編排者:要確認 via cov 是 `tests_sha` 與 `cov_sha` 兩者並用。

severity: major
blocking: 是
引句:「`via: "cov"` 的存活,只有這次也開覆蓋而且 `cov_sha` 相同才帶過去,否則重跑;其餘照現在。」

**11. 只要有一支合理的零專案類別測試,所有行都降成 `unknown`,覆蓋加速整個失效**

分類規則是「有任一支不明就 `unknown`」。可信判準只看「專案類別有紀錄數 > 0」。守的測試上千支時,有一支只驗資源、設定,或只碰 JDK 類別的測試就會是 0。它不會觸發斷路器(只看前 5 支),卻讓 `none` 與 `clause` 都不可能出現,所有壞法跑全部測試。極端情況下,可信與不可信的混合在大專案裡必然出現,spec 沒有「不可信的測試只影響它自己經過的行」之類的降級規則。

severity: major
blocking: 是
引句:「`unknown`(有任一支不明,或這一行在下面例外裡,附原因)」

**12. 抽查的順序與邊界沒定義,「其餘 `none` 改成照跑」與「直接記存活」互相打架**

範圍 3 說 `none` 的行 choice-kill 直接記 `survived`;範圍 5 說抽到被殺掉時,其餘 `none` 要改成照跑。如果 `none` 行是在 recipe 串流途中就寫帳,事後無法改成照跑,spec 沒規定抽查必須先於記帳。`--cov-audit N` 的邊界也沒寫:
- N 大於 `none` 行數:未定義。
- 沒有 `none` 行:未定義。
- 「隨機」沒說種子,因此不可重現。
- 守的測試上千支時,每個被抽到的行要跑全部測試,成本沒進預算。

severity: major
blocking: 是
引句:「這次 run 的 `none` 一律改成照跑(等於斷路)」

**13. 小項:`--no-cov` 沒有定義;撤回事件沒有放理由的欄位;截斷旗標沒進欄位白名單**

- `--no-cov` 在範圍 7、回退節、S11、S21 都被引用,但沒有任何一節定義這個旗標或它的參數。
- `--withdraw` 要 `--reason`,但 layer 事件欄位清單(`file`、`fp`、`layer`、`new_sha`、`judgment`、`judgment_sha`、`deps_sha`、`token`)沒有 `reason`。`layer: 0` 時 `judgment` 與 `new_sha` 該填什麼也沒寫。
- `_gate_event_fit` 截斷時會新增 `reach_clauses_truncated`,這個鍵不在 `reach` 欄位清單與 `_GOV_FIELD_TYPES` 補充裡。

severity: minor
blocking: 否
引句:「跟 `--no-cov`、`--only`、`--max-mutants`、`--no-merge` 同給時 rc2」

**14. 小項:數字邊界措辭不精確**

- 「超過 200 KB」沒說是 1000 還是 1024 進位。
- 引句「10–200 個實字」的下限用 `_real_chars`,上限沒說算實字還是原始長度。含標點的長引句會在兩種算法下結果不同。
- `reach_clauses`「依計劃路徑與條款號排序」沒說條款號是數字序還是字串序(S10 與 S2)。
- 計劃正文的段名與 `#2` 同名後綴,會因為在前面插入同名段而位移,使 `where` 指到錯段。

severity: minor
blocking: 否
引句:「位元組數(UTF-8)超過 200 KB 就把存活數減半再切」

總結:最高等級是 blocker,blocking 共 12 條
