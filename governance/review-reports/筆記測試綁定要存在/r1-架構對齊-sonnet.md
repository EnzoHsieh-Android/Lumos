severity: major

# 設計審 r1 架構對齊-sonnet 報告

(以下 file:line 都指凍結 repo 根下的 `scripts/lumos`;已逐一開檔讀過函式本體。)

## 問 1 分層與依賴方向

大方向對:新規則掛在 note-shape 裡、判存在沿用 `_classify_test_refs`、作廢用 `_ns_superseded`、圍欄與反引號用 `_visible_lines`/`_strip_inline_markup`,沒有反向依賴。「本案是它第三個呼叫者」屬實:現有呼叫者恰為修正關卡的 `scripts/lumos:12366` 與推送前合約測試閘的 `scripts/lumos:40315`。
唯一的分層問題在「新寫的行」怎麼拿:PRIOR-ART 寫提交時用 `_notelines_new`、推送時直呼 `_notelines_range_added`。後者是下層零件,全檔只有 `_notelines_range_cand`(`scripts/lumos:27391`)呼叫它;所有上層呼叫者(`_note_shape_eval` 的 `scripts/lumos:28407`、筆記內容審的 `scripts/lumos:28947`)一律走 `_notelines_new`(它統一處理 staged/範圍、上線點截斷、`_notelines_rows` 區塊判定)。而且 `_note_shape_eval` 只回 `(viol, errs)`,新寫行只經容器參數(`hints`/`tags`/`slots` 的 sink)往外給;沒有容器就拿不到 rows。見 F1。

## 問 2 命名與錯誤處理

命名:`_note_shape_test_refs_parse`、`note_shape.test_refs`、`t_note_shape_test_refs_*`、`t_doctor_note_test_refs` 都跟 `_note_shape_slots_parse`(`scripts/lumos:28113`)、`_note_shape_tag_hints_parse`(`scripts/lumos:27888`)、`t_note_shape_*` 一致。總開關與子開關的合併(`_ns_slots_mode`,`scripts/lumos:28134`:gate off→off、gate warn→warn)計劃只用一句話描述、沒給函式名,實作時容易複製第四份;結構對,不列。
錯誤處理:索引建不起來就跳過並印原因,跟 `_ns_slots_prepare`(`scripts/lumos:28005-28030`)的 fail-open 一致。治理帳的 `extra` 只有一個槽(`_note_shape_report` 的 `kw`,`scripts/lumos:28685` 起),計劃加第二組欄位沒講怎麼併,見 F2。

## 問 3 第二種做法

- 新寫行的取得路徑:見 F1(major)。
- 抽取器:見 F4。
- 測試索引讀哪個版本:見 F5。
- 上線方式(沒有自己的上線記號):見 F6。
- 其餘不算第二種做法:`[test-gone:]` 的提交判定走 `_pin_commit`(`scripts/lumos:27114`,與 `_ns_pin_ok` 同源);開關寫成 block/warn/off 三態、違規另收一份清單、帳本多帶結構欄位,都照格子規則(`_ns_slots_violations`/`_ns_slot_extra`,`scripts/lumos:28307`、`scripts/lumos:28368`)的前例;doctor 段不寫帳照 S17–S19(`scripts/lumos:2513-2550`)。

## 問 4 落點

`lands_in` 列的 `Systems/check-t-sentinel` 不對:該篇管的是 doctor 的 Check T/K(合約綁測試、`★COMBO★`),計劃自己寫「合約行…本案不查」、也不動 Check T。doctor 的 S16–S19 筆記格子提醒段記在 `Systems/lumos-cli-read`(該篇 summary 的 doctor S16 到 S19 那兩條 WHY);紀律範本格子表與 `t_slots_single_table` 記在 `Systems/lumos-cli-lifecycle`;`_classify_test_refs` 的呼叫者清單記在 `Systems/bound-tests-gate`(該篇有一條講它是共用抽出的 WHY)。note-shape 規則與格子鍵放進既有的 `Systems/筆記內容閘` 合理,不必另開。見 F3。

## F1 新寫行直呼下層 `_notelines_range_added`,而且沒有拿 rows 的出口
severity: major
blocking: 是
引句:「新寫的行用筆記內容閘既有的抽取(提交時 `_notelines_new`、推送時 `_notelines_range_added`)」
file: `scripts/lumos:27250`(`_notelines_range_added`,下層,回的是 {路徑: 文字集合}、淨改動路徑、old_by,沒有行號與區塊)
file: `scripts/lumos:27344`(`_notelines_new`,上層,統一處理 staged/範圍並呼叫 `_notelines_range_cand`→`_notelines_range_added`→`_notelines_rows`)
file: `scripts/lumos:27391`(`_notelines_range_added` 全檔唯一呼叫者是 `_notelines_range_cand`)
file: `scripts/lumos:28407`、`scripts/lumos:28947`(兩個上層呼叫者都走 `_notelines_new`)
file: `scripts/lumos:28378-28425`(`_note_shape_eval` 只回 `(viol, errs)`;rows 只經 `hints`/`tags`/`slots` 容器交出,`slots` 容器要掛鉤帶 `--slots` 才建,`scripts/lumos:28005-28030`)
1. 照字面實作:推送時規則自己呼叫 `_notelines_range_added`,拿到的是 {路徑: 行文字集合},沒有行號、沒有區塊(body/summary/decisions/other)、沒有「終點版本還在」的過濾、沒有上線點截斷(`live_mark`);這些都是 `_notelines_new`/`_notelines_range_cand`/`_notelines_rows` 補的。計劃要印「筆記、行號、名稱」、要略過條款定義行與合約行、要知道圍欄,全部得自己重做一份,就是第二套「新寫行」判法。
2. 提交時走 `_notelines_new`、推送時走下層,同一條規則兩條來源,提交與推送的判定會各自漂。
3. 就算兩邊都改走 `_notelines_new`,規則另跑一趟會對同一個範圍多做一次 rev-list 與逐提交 diff(`_notelines_range_added` 的主要成本);既有前例是把容器傳進 `_note_shape_eval`、在同一趟逐篇從 `rows` 收(`_ns_negation_collect`,`scripts/lumos:27858`、`_ns_tag_hints_collect`,`scripts/lumos:27921`,呼叫點 `scripts/lumos:28424`)。格子的 sink 還因為要掛鉤帶 `--slots` 才建,測試綁定規則不能借它(不帶 `--slots` 的推送與一般提交 `slots is None`,`sink["notes"]` 根本沒設)。
4. 判不準的部分 ⚠:計劃沒寫容器要怎麼進 `_note_shape_eval`;這點要在設計裡寫死(新增第四個容器參數,或把 `notes/old_by` 無條件放出),不然實作者會自己選一條,最像的就是上面兩條偏離路徑。

## F2 帳本欄位與單次跳過的 `extra` 只有一個槽,計劃沒講怎麼併
severity: minor
blocking: 否
引句:「單次跳過時也先算一次記進去(照格子的 `_ns_skip_slot_extra`)」
file: `scripts/lumos:28089`(`_ns_skip_slot_extra` 回的 `extra` 直接傳給 `_gate_event_or_warn(..., extra=extra)`,`scripts/lumos:28572-28574`)
file: `scripts/lumos:28685`(`_note_shape_report` 只有 `slot=` 一個附加參數,`kw` 只裝 `_ns_slot_extra`)
file: `scripts/lumos:28368`(`_ns_slot_extra` 的 `check` 欄位用 `"shape+slots"`/`"slots"` 列舉組合)
1. 事件的 `extra` 是單一字典、單次跳過路徑只拿 `_ns_skip_slot_extra` 一份;規則一加就要同時改 `_note_shape_report`(再多一個位置參數)、跳過路徑(要把兩份 extra 合併)與 `check` 欄位的列舉(`shape+slots` 之後再加 `+test_refs` 會是組合爆炸)。
2. 計劃只說「欄位多帶 `test_refs`」,沒說合併規則與 `check` 值。RETIRE-IF 靠這欄抽查,合併寫錯會讓 REVISIT 2026-12-01 量不到。

## F3 `lands_in` 列了 check-t-sentinel,doctor 段與範本的家另有其篇
severity: minor
blocking: 否
引句:「doctor 多一段全庫提醒(含散文撤除的候選)」
file: `docs/lumos-toolchain-knowledge/Systems/check-t-sentinel.md`(summary 全是 Check T/K/`★COMBO★`)
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:13`(S16 的 WHY)、`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:14`(S17–S19 的 WHY)
file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:15`(紀律範本格子表與 `t_slots_single_table`)
file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:17`(`_classify_test_refs` 抽出的 WHY)
1. 新 doctor 段不是 Check T 的一部分(計劃明寫不查合約行),寫進 check-t-sentinel 會讓那篇管到它不管的東西;鄰居 S16–S19 記在 lumos-cli-read。
2. 計劃動紀律範本格子表(PITFALL 四選一),它的家是 lumos-cli-lifecycle,`lands_in` 沒列。
3. `_classify_test_refs` 多一個呼叫者,bound-tests-gate 該寫一句(related 已列、`lands_in` 沒列)。
4. 另外 doctor 段沒給 S 編號,也沒講 `--ci` 下跑不跑(S17/S18 在 `--ci` 不跑,S19 照跑,`scripts/lumos:2513-2550`);本案段要建測試索引,`--ci` 行為要定。

## F4 另寫一支抽取器 `_note_test_refs`,且把整行丟給 `_classify_test_refs`
severity: minor
blocking: 否
引句:「`_note_test_refs(line)` 對一行(先經 `_strip_inline_markup`)抽出 `[test:…]` 與 `[test-gone:…]`」
file: `scripts/lumos:4736`(`TEST_REF_RE`)、`scripts/lumos:5160`(`invariant_test_refs`,含逗號切分)、`scripts/lumos:5195`(`strip_test_refs`)
file: `scripts/lumos:3764`(`slot_parse`:摘要行 `[鍵:值]` 的既有解析,`test` 已是可重複鍵)
file: `scripts/lumos:12366`(修正關卡逐名呼叫 `_classify_test_refs(f"[test:{t}]", ...)`)
1. 同一種東西(`[test:…]`)現有兩個抽取來源:`TEST_REF_RE`/`invariant_test_refs`(合約與 `resolve_test_refs` 內部用)與 `slot_parse`(摘要行格子)。計劃再加第三個 `_note_test_refs`,卻沒說它底下用 `TEST_REF_RE` 還是 `slot_parse`。摘要行上 `slot_parse`(括號成對)與 `TEST_REF_RE`(`[^\]]+`)對含巢狀方括號的值切法不同,新規則的「新加名稱」與格子規則看到的欄位會不一致。
2. 〈做法〉3 把去反引號後的整行交給 `_classify_test_refs`,而它內部又用 `TEST_REF_RE` 重抽一次;一行裡舊名與新名並存時,整行分類會把舊名的 dangling 一起帶出來,要事後再用名稱濾回去。修正關卡的前例是逐名組成 `[test:名]` 再判。名稱多重集合與分類各抽一次,兩次抽取結果不同就會對不上。⚠ 這點涉及行為對錯(S2 的舊行不擋),交編排者與正確性席判。

## F5 工作目錄髒檢查另寫新函式,鄰居已有「驗提交版本」的解法
severity: minor
blocking: 否
引句:「新寫一支小函式用 `git status --porcelain` 對平台根判」
file: `scripts/lumos:12278`(修正關卡:`_fix_git_z(rr, "status", "--porcelain", "-z", "--untracked-files=no")` 取髒檔並濾掉 `_BOOKKEEPING_FILES`/`_BOOKKEEPING_DIRS`)
file: `scripts/lumos:12300-12311`(同一個函式用 `_isolated_worktree` 把提交版本物化成樹,再對樹建 `_platform_test_index(tree)`,不讀工作目錄)
file: `scripts/lumos:40153`(合約測試閘一側也有 `status --porcelain -z -uall` 的另一份髒檔切法)
1. 計劃問題「筆記讀被檢查版本、測試索引讀工作目錄」在 `_classify_test_refs` 的另一個呼叫者(修正關卡)已經用「物化提交版本」解掉,同函式裡也已有髒檔判法與簿記檔排除表。計劃選的是跟合約測試閘一樣讀工作目錄,再加一支新髒檢查;一旦照字面寫,簿記檔(治理帳、卷證)不排除就會在每次提交時誤報「測試檔有改動」。
2. 計劃的取捨(只提醒、靠單次跳過)可以成立;這條只是指出:新函式要沿用 `_fix_git_z` 與簿記檔排除表,或在設計裡寫明為何不比照修正關卡。⚠ 兩種做法各有道理,不判優劣。

## F6 新規則沒有自己的上線記號,跟兩個鄰居的上線方式不同
severity: minor
blocking: 否
引句:「消費專案 `lumos update` 後,新加壞名字會被擋——本案本意;既有的不擋。」
file: `scripts/lumos:27107`(`_NOTE_SHAPE_GOLIVE_MARK`)、`scripts/lumos:27993`(`_SLOTS_GOLIVE_MARK`)、`scripts/lumos:28005-28030`(`_ns_slots_prepare`:提交看 `--slots`、推送看終點掛鉤歷史的記號,找不到就不跑)
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容閘.md`(summary 的 WHY:程式與掛鉤同一輪 lumos update 到,不靠旗標分開的話程式一上線就全面開擋)
1. 格子規則刻意把「程式上線」與「開擋」用掛鉤記號分開(那條 WHY 的因);本案預設 `block`、程式一到就跑,推送範圍只受既有 note-shape 上線點截斷。升級前用舊掛鉤(只有 note-shape 記號)寫的提交,推送時會被新規則當新寫行檢查;計劃在〈實務隱患〉以「只有真的新加了壞名字才擋」接受這點。
2. 這是跟緊鄰的格子規則不同的上線做法,不是錯;⚠ 判不準是否算偏離,列出供編排者裁。

已讀,無 finding 的節:〈名詞〉、〈範圍〉、〈條款〉、〈回退〉(結構上與鄰居一致;條款命名 `t_note_shape_*` 沿用前綴)。

不對齊共 6 條,其中 major 1 條
最高等級:major,blocking 共 1 條
