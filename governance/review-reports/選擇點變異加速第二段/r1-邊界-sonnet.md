severity: major

審 `選擇點變異加速第二段_計劃` r1 的邊界與極端輸入。spec 的 §1、§3、§4 各有洞,§2 和「已讀,無 finding」的幾節見最後。

本案碰到的風險類:判定語意(殺掉的判定、`stop_group_on`)、時限與斷路器邊界、治理帳欄位、指令長度與名稱檢查的靜默退路、多平台。金流、對外送出、不可逆都在 spec 裡已排除,我複核過,無異議。

### 逐條 finding

**F1 〈做法〉1「先紅順序」會改變判定,與「判法不變/判定相同」矛盾**

severity: major
blocking: 是(判定結果會變,屬 major)

引句:「判定相同;`killing_test` 欄只做紀錄,推送閘不讀它判放行」

- spec 段落:白話第一條 WHY、〈舊否決比對〉第一條、〈實務隱患〉第二條。
- 問題:spec 說重排只改順序、「判定相同」。但停止集合 `_CHOICE_STOP_ON` 含 `timed_out_weak` 和 `compile_error`。這兩種是「先到先決」:`on_row` 遇到就當場 `finish`,同組後面的配方一律略過。
- 重現:守的測試排序是 a、b、c,名單是 c。
  - 現行順序下,a 在壞法裡單支逾時,得 `timed_out_weak`,整個壞法判成 `no_result「測試掛住」`。
  - 先紅順序先跑 c,c 強殺掉,判成 `killed`。
  - 同一個壞法、同一份測試,`--no-merge` 與預設合併給出不同的判定(`no_result` 對 `killed`)。
- 這比「`killing_test` 欄不同」嚴重,因為 `killing_test` 以外的判定欄也會變。
- S1 第三案、S2、S5 只驗 killed 對 killed,沒有「逾時測試排在紅測試前面」的案例。
- 邊界組合沒定義:名單裡某支單支逾時,或單支編不過,先到誰就判誰,spec 沒寫。
- 查證:
  - file: `scripts/lumos:78458`,`_CHOICE_STOP_ON` 含 `timed_out_weak`。
  - file: `scripts/lumos:78970`,`on_row` 的 `decisive` 含逾時。
  - file: `scripts/lumos:78668`,判定函式在 `live` 裡找強 `killed`,找不到才看逾時。因為逾時當場停組,後面的 killed 列根本不存在。
- 修向:要嘛承認判定可能不同、寫進〈實務隱患〉並加案例。要嘛規定先紅順序只在「名單外沒有已知會逾時的測試」時用。要嘛把名單當「先跑的候選」,但 `timed_out_weak` 的停止仍照原順序語意。

**F2 〈做法〉4 `merge_base_why` 對原因字串的對應沒定義,「空字串」同時代表乾淨、沒跑、對不到**

severity: major
blocking: 是(spec 自己的目標「事後查得出原因」落空)

引句:「字串,`_CHOICE_MERGE_BASE_WHY` 那幾種;沒有就空字串」

- spec 段落:〈做法〉4 第二條、S4。
- 問題一:`_choice_merge_classify` 實際回的原因字串是「逾時」「被系統收掉」「找不到 JUnit 結果檔」「結果檔讀不出來」「結果檔超過大小上限」,以及帶數字的「N 支對不到結果檔裡的名字」。`_CHOICE_MERGE_BASE_WHY` 的鍵是「逾時」「rc 不是 0」「有失敗」「編不過」「被系統收掉」。
  - 「找不到 JUnit 結果檔」「結果檔讀不出來」「結果檔超過大小上限」「N 支對不到…」都不在鍵裡。
  - spec 寫「`_CHOICE_MERGE_BASE_WHY` 那幾種;沒有就空字串」,沒說這些沒見過的原因怎麼記。
  - 照字面實作有兩種結果:記成空字串,事後看起來像基準乾淨;或照現行 `.get(why, why)` 記原字串,「N 支對不到」帶數字,基數不受控。
- 問題二:基準沒進到 classify 的路徑也沒有 `why`。
  - 單支基準沒量齊,`_kill_merge_singles` 回 False。
  - 單支綠的不到 2 支,即 `len(lane) < 2`。
  - 第一個訊號中斷。
  - 這些路徑 `merge_base_why` 也是空字串,跟「基準乾淨」無法區分。
- 問題三:多平台時 `merge_base_why` 是單一字串。兩個平台組一個乾淨、一個不乾淨時,後者會被覆蓋或前者蓋掉後者,spec 沒定義。
- 查證:
  - file: `scripts/lumos:28735`,`_CHOICE_MERGE_BASE_WHY` 的鍵。
  - file: `scripts/lumos:28851`,`_choice_merge_classify` 的回傳原因。
  - file: `scripts/lumos:28944`,`_kill_merge_base` 在 classify 之前就回 None 的路徑。
- 修向:給固定列舉含「未知」兜底,並加「沒量基準」這一值,讓空字串只代表基準乾淨。

**F3 〈做法〉3 提示的 M 值照字面做會自我打臉**

severity: minor
blocking: 否(有繞法,但提示內容會錯)

引句:「要合併請帶 --max-seconds <M 無條件進位到百>」

- spec 段落:〈做法〉3、S7。
- 問題:提示叫使用者帶「M 無條件進位到百」。但門檻判的是「剩下」時限,不是 `--max-seconds` 本身。剩下 = `--max-seconds` 減去走到這裡已花的秒數(掃描、AST、前一個平台組)。
- 場景一:守 120 支,M = 120 × 10 × 1.5 = 1800。預設 1800 的剩餘一定小於 1800,門擋下,提示卻說「請帶 --max-seconds 1800」,叫使用者帶他本來就帶的值。
- 場景二:多平台時,提示只算「這個平台組」的支數,但剩餘時限是各組共用的。第二個平台組的 M 沒把前面已花的算進去。
- 場景三:`--max-seconds` 很小(例如 10)或已經耗盡時,R 可能是負數。spec 沒定義「剩 -3 秒」要不要印。
- 查證:file: `scripts/lumos:28900`,`_kill_merge_ready` 的時限門用 `mg.remaining()`;`remaining` 是 `deadline - monotonic`。
- 修向:M 要加上已花的時間,或進位後再加一格;負數剩餘要有固定寫法(例如夾到 0)。

**F4 〈做法〉3 只補時限這一個靜默退路,同一個問題還有四條**

severity: minor
blocking: 否(WHY 的動機只覆蓋了其中一種原因)

引句:「靜默退回逐支讓人以為合併沒效」

- spec 段落:〈白話〉第 3 點、第四條 WHY。
- 問題:WHY 說「靜默退回逐支讓人以為合併沒效」。`_kill_merge_ready` 還有這幾條靜默回 None 的路徑:
  - 指令超過長度上限(合併道很多或名字很長,例如 169 支以上)。
  - 名稱檢查或撞名。
  - `flaky` 或筆記未提交。
  - `tq` 或結果資料夾拿不到。
- `_kill_merge_iter` 只把 `mg.plats[plat]` 記成 `(False, "條件不合")`,沒印任何字。本案拿掉「少於 2 個」之後,單點重跑會更常走到這些。
- 場景:169 支、名字長度讓指令超過 32768 位元組時,使用者仍然是「合併沒效又不印」。
- 查證:file: `scripts/lumos:28900-28920`、`scripts/lumos:29097-29112`。

**F5 〈用詞〉合併失敗名單的「恰好對到一個」沒說分母,參數化測試的失敗會被丟掉**

severity: minor
blocking: 否(不改判,只讓排序失效、退回原順序)

引句:「對回合併道裡的測試名(恰好對到一個才算);對不到的不列。」

- spec 段落:〈用詞〉合併失敗名單、S2「名單一支都對不到」。
- 問題:`_choice_merge_fullname` 會去掉參數尾巴(第一個 `(` 或 `[` 起)。同一支參數化測試的兩個失敗案例會變成同一個完整名。
- 若分母是「失敗名單裡的完整名」,`_choice_merge_hits` 得 2,恰好 1 不成立,該測試被丟出名單,排序失效。
- 若分母是「全部完整名」,連只有一個參數失敗、其餘綠的也算 2。
- spec 沒寫用哪個分母,兩種實作結果不同。本案提到 `_choice_merge_hits`,但 `_choice_merge_classify` 現在拿它判的是「全部 facts」。
- 查證:
  - file: `scripts/lumos:28800`,`_choice_merge_fullname`。
  - file: `scripts/lumos:28809`,`_choice_merge_hits`。

### 逐節狀態

- 〈做法〉2「一個壞法也合併」:已讀,無 finding。
  - 我查了 `n_mutants` 的所有讀取點,只有 `_kill_merge_ready` 讀它。
  - 既有測試是位置參數 `_KillMerge(...,3)`,拿掉判斷不會破壞。
  - 〈實務隱患〉已承認單點被殺得快時多付量齊基準。
- 斷路器剛好第 5 次:已讀,無 finding。
  - `_kill_merge_breaker` 在連續第 5 次計數時跳開,S4 的「逾時: 5」與現行程式一致。
  - `pass` 歸零。
  - 帶數字的「N 支對不到」不計不歸零。
- 名單為空、名單全是合併道內的名字、名單順序與原排序相反:已讀,無 finding。〈用詞〉先紅順序已定義:名單內與名單外各自維持原排序。
- 合併道少於 2 支或只守 1 支:已讀,無 finding。`len(lane) < 2` 回 None 照舊,spec 在〈做法〉2 第三條明寫。

### 固定席節點判斷

- `Systems/guard-kill` 的 INVARIANT「rc 優先序:survived→rc1、drifted/abort/error→rc2、弱證據不放行執行錯誤」:不影響。本案沒碰 `cmd_guard_kill` 的 rc 計算(`scripts/lumos:28609` 起的 verdicts 彙整),重排只改配方交出順序。但 F1 的判定變動發生在 choice-kill 的判定函式,不在 guard kill 的 rc,所以此條合約不破。
- `Systems/guard-kill` 的 INVARIANT「--json 成功跑完時 stdout 恰一行 JSON」:不影響。新增的提示與斷路器訊息一律走標準錯誤,spec 明寫印到 stderr。
- `Systems/規格閘`:本案新增 run 事件欄位 `merge_unclean`、`merge_base_why`,走 `_GOV_FIELD_TYPES`。舊帳沒這兩欄,spec 沒寫舊帳讀成什麼(`judged` 有「缺的舊帳讀成 single」的先例)。這是小疑慮,但舊帳不會因此讀壞,所以不另列。

最嚴重 severity: major,blocking 共 2 條(F1、F2)。
