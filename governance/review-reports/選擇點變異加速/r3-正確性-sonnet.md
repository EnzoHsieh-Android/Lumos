severity: major

先講結論:我找不到「快篩乾淨、記成全部存活,但逐支流程會判成被殺掉」而又不是 spec 已承認的「測試互相影響」的輸入。乾淨條件要求 rc 為 0、結果資料夾在、每支測試對到恰好一個完整名、沒有 failure 或 error。我逐一試過輸出被管線或 `|| true` 蓋掉、`ignoreFailures`、`failOnNoMatchingTests=false`、@Ignore、glob 多選等情形,這些都會被 XML 檢查擋下,或在逐支流程裡本來就判存活。下面 7 條是我找得到的洞,只有第 1 條會讓照字面實作的結果偏離設計意圖。

## 守衛面逐類結論

- 判錯方向:除第 2、7 條外,無新增。快篩只可能多記存活,不可能多記殺掉。
- 資源:無新增。結果檔大小上限與刪除圍欄已寫。已知的 Gradle 背景程序殘留已由 S17 明文接住。
- 效能:見第 1 條。
- 回滾與相容:見第 5 條。舊版讀不認得的欄位會略過,這點已核對屬實。

## 發現

### 斷路器把「壞法編不過」算成快篩沒跑乾淨
severity: major
blocking: 是

位置:〈做法〉3 斷路器,另見 S4 與 S8。

問題:壞法編不過是這個工具已知的高頻類別。計劃筆記 `Systems/規格閘.md:82` 的 REVISIT 就在盯「編不過比例過三成」。壞法編不過時,合併呼叫 rc 不為 0、沒有任何失敗案例,結果資料夾也不在,這三條正好落在斷路器計數的括號清單裡。spec 沒有把編譯錯誤樣式(`_KILL_COMPILE_RE`)從斷路器分出來。S4 把「輸出符合編譯錯誤樣式」列為走逐支,S8 卻只測逾時與讀不出。

輸入到結果:相鄰的 5 個壞法都是型別前提沒擋住的編不過(同一檔、相鄰行、同類運算子)。每個壞法的快篩都記為「不乾淨而且不是因為有失敗」,第 5 個之後斷路器跳開,這次呼叫剩下的壞法全部不合併,`merge_tripped` 為真。

後果:
- 以編不過比例約三成估,連 5 個編不過在 197 個壞法裡很可能出現。
- 這個專案的加速就此報廢,而且報廢的原因與合併是否划算無關。
- RETIRE-IF ③「斷路器跳開超過三成就拿掉合併」會被這些誤跳污染,進而導致拿掉一個其實有效的機制。

另一個矛盾:斷路器寫「乾淨的一次(不論有沒有失敗)把計數歸零」,但〈用詞〉把「乾淨」定義為沒有任何 failure 或 error。「有失敗但不乾淨」的情形(例如有失敗,同時另有一支對不到名字)該不該歸零,spec 沒說。

引句:「rc 不是 0 但沒有失敗案例、結果資料夾不在)→ 這次呼叫剩下的壞法在這個平台組停用合併」
file: `scripts/lumos:28165`
file: `scripts/lumos:28693`
file: `docs/lumos-toolchain-knowledge/Systems/規格閘.md:82`

### 「判錯方向安全」忽略回報上限,假存活會稀釋真存活
severity: minor
blocking: 否

位置:WHY 的「因」,以及〈實務隱患〉守衛面。

問題:推送閘對存活只擋「回報上限抽中的那批」。上限是有增行的檔數 × 7,從「曾經存活過的行」集合用種子洗牌後取前 N 個。假存活(合併時測試互相影響而漏殺)會進入這個集合,擠掉真存活被抽中的機會。放行過的行也留在種子集合裡。

輸入到結果:某檔有 3 行真存活、多行合併漏殺的假存活。使用者在抽中的假存活上補測試或放行,沒抽中的真存活照樣過閘。這樣算不上「不會讓壞程式過閘」,頂多是「不會讓這一行的好測試被當成沒用」。

另外:合併判的存活與逐支判的存活,在輸出(`存活:沒有測試守著這個選擇`)與帳上對使用者完全同形。spec 的安全論證靠人看存活再決定,但沒有任何提示告訴人哪幾行該先用 `--no-merge --only` 逐支確認。

引句:「判錯的方向安全:合併時測試互相影響讓本該失敗的測試通過,最多把該殺掉的記成存活,存活會被推送閘擋下要人看,不會讓壞程式過閘」
file: `scripts/lumos:78781`
file: `scripts/lumos:78767`
file: `scripts/lumos:78503`

### 基準不綠的測試在「合併判存活」這條路上怎麼交列沒寫,合併基準測試數不足的情形也沒寫
severity: minor
blocking: 否

位置:〈做法〉2、3。

問題一:現行逐支流程對基準不綠的測試記 abort 列。`_choice_kill_judge` 把 abort 的測試從判定拿掉,記進 `aborted`。spec 說合併基準「只含單支基準綠的那幾支」,快篩乾淨時卻寫「每支守的測試各交一列 survived」。
- 照字面,基準不綠的那支也會得到一列 survived,`aborted` 清單遺失。
- 若只對綠的交列,基準不綠的那支沒有列,`_choice_kill_judge` 會把它判成「缺結果」,整個壞法變 no_result。這跟逐支(survived 加 aborted 註記)不一致。

問題二:「至少 2 支」是在量基準之前判的。基準拿掉 abort 之後只剩 0 或 1 支綠時,spec 沒有規則。剩 0 支時,指令是空的 `--tests` 段。剩 1 支時,合併等於單支,快篩失敗後再把同一支重跑一次,白付一倍。

另外,S3 與預期值表說「逐支呼叫順序跟 `--no-merge` 相同」,但基準呼叫其實不同:合併模式一開始量齊,`--no-merge` 是用到才量。

引句:「這個平台組這支壞法的每支守的測試各交一列 survived」
file: `scripts/lumos:28461`
file: `scripts/lumos:78214`

### RETIRE-IF ③ 的交叉引用指錯節
severity: minor
blocking: 否

位置:RETIRE-IF ③。

問題:斷路器寫在〈做法〉3 的「斷路器」條,〈做法〉4 是「中斷與時限」。

引句:「累計 10 次以上呼叫裡,斷路器跳開(見〈做法〉4)的超過三成」

### 「既有的 `ran`」不在 ck 子字典裡;judged 對另外兩個寫事件的呼叫端沒說
severity: minor
blocking: 否

位置:〈做法〉5 登記,〈用詞〉判法。

問題一:`_gov_row` 的 `ck` 現有鍵是 file、fp、killing_test、changed、mutant_lines、secs、reasons、site,沒有 `ran`。`ran` 只存在於 run 事件本身與 `_GOV_FIELD_TYPES`。RETIRE-IF ② 與 S11 又要從 `ck` 讀 `ran`。讀成「ran 已經在 ck」的實作者會漏加,S11 的 `gov` 帶出 `ran` 就紅。

問題二:`_choice_event_extra` 還有兩個呼叫端,是 situation-rule 的 `--point` 路徑,會寫 `killed` 事件。這兩處不經 choice-kill 的合併,spec 沒說 `judged` 要不要寫、寫什麼。〈用詞〉卻說「每筆」choice-kill 事件都有。

引句:「與既有的 `ran` 照 `_gov_row` 現有的 choice-kill `ck` 子字典慣例加進去」
file: `scripts/lumos:18553`
file: `scripts/lumos:79107`
file: `scripts/lumos:79240`

### 「弱證據一定是假」漏掉還原後修改時間沒錯開這個來源
severity: minor
blocking: 否

位置:〈做法〉3 合併快篩乾淨那條。

問題:現行 `cmd_guard_kill` 在還原後如果 `_kill_after_write` 失敗,會把 `mt_ok` 設為假,這一支的列也跟著記成 `_mtime_unsure`,算弱證據。這個來源在跑測試之後才知道,不是「上面已排除」的那幾個。照字面把 weak 寫死為假,等於少了一道現行會蓋的保守標記。方向仍是偏保守的反面:快篩的存活列比逐支的存活列更容易不帶弱證據。

引句:「上面已排除所有弱證據來源,所以是假」
file: `scripts/lumos:28517`
file: `scripts/lumos:28562`

### 快篩與逐支的逾時基準不同,同一個變慢的壞法會得到不同判定
severity: minor
blocking: 否

位置:〈做法〉3 合併快篩。

問題:合併快篩的逾時是熱的合併基準 × 5,數量級是分鐘。逐支的逾時是每支單支基準 × 5,下限 20 秒,數量級是 30 秒。壞法讓某支測試變慢到 40 秒但仍通過時,快篩記存活(`judged` 為 merged),逐支流程會記 `timed_out_weak`,即 no_result「測試掛住」。

這不是漏殺,但是「快篩乾淨、逐支判不同」的一類,而且 S18 與 RETIRE-IF ① 只比對「判成殺掉」,抓不到這種不同。

引句:「刪結果資料夾、跑合併指令,逾時上限 = max(合併基準耗時 × 5, 下限)」
file: `scripts/lumos:28504`
file: `scripts/lumos:28523`

## 逐節走查

- 白話、WHY、PRIOR-ART、RETIRE-IF:已讀。引用的檔名與函式都存在,問題見第 2、4 條。
- 舊否決比對、實測、用詞:已讀,無 finding。基準「用到才量、每次呼叫重量」與現況相符。
- 〈做法〉1:已讀,無 finding。`_gradle_task_list`、`_SR_MODULE_PART`、`_gradle_test_module`、`_run_cmd_expand(…, name_filter=)` 都存在。不改 `_gradle_test_module` 的理由與 `_gradle_blocked_tasks` 的用法屬實。
- 〈做法〉2:見第 3 條。
- 〈做法〉3:見第 1、2、5、6、7 條。
- 〈做法〉4:已讀,無 finding。處理器的兩段式、`_KILL_RUN_LIVE`、`_kill_proc_group`、`_situation_rule_force_exit` 都與描述一致。收掉快篩後 `cmd_guard_kill` 回到下一支配方前會經過 `hk.between` 而停,這條路可行。
- 〈做法〉5:見第 5 條。`_GOV_FIELD_TYPES` 沒有同名的衝突欄位。
- 〈做法〉6、落點、不做、預期效益、回退:已讀,無 finding。
- 驗收條款與預期值表:S1 到 S18 共 18 條,與表的 18 列對得上。S4、S8 的對應問題見第 1 條。
- 實務隱患:見第 2 條。

發現共 7 條
