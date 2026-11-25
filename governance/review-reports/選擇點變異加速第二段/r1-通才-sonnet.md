severity: major

我逐節讀完整份 spec,spec 對程式碼的假設都對照 `scripts/lumos`、`scripts/test_lumos.py` 和前一份計劃查過。固定席的兩個節點都判「不影響」,理由放在 finding 之後。

已讀無 finding 的節:frontmatter、〈舊否決比對〉、〈實測(來源)〉(數字與白話除第 9 條外一致)、〈用詞〉、〈回退〉、〈人裁紀錄〉。〈預期效益〉的算術(225 個、約 7:2:1)驗過,對得上。`_kill_merge_ready` 之外沒有別處讀 `n_mutants`,〈做法〉2 說「別處不讀」屬實。

---

severity: major
blocking: 是(實作者照 spec 做完,前一份計劃仍有已綁測試的條款與預期值表跟新行為互相矛盾,既有測試轉紅,spec 沒說怎麼處置)
引句:「同一提交改的既有句子:[[Projects/選擇點變異加速_計劃]]」
- 位置:〈落點〉最後一條「同一提交改的既有句子」。
- 問題:清單只列了〈做法〉1「少於 2 個不合併」與 S19 那半、〈做法〉3「其他三類」、〈舊否決比對〉第三條。漏了下列幾處,它們在新行為下都會變假:
  - 前一份計劃 S3 條款寫「壞法階段的逐支呼叫順序與判定 應 跟 `--no-merge` 的壞法階段相同」,綁 `t_choice_kill_merge_failure_goes_single`。新行為下 b、c 失敗時只跑 b(先紅順序),`--no-merge` 跑 a、b,兩邊不同。
  - 預期值表 S3 列寫「逐支 a 存活、b 殺掉、c 略過……`--no-merge` 壞法階段同為 a、b」,同樣變假。
  - 預期值表 S19 列「另一案 `--only f.kt:12` → 不合併」,與新的 S3 直接相反。
  - 〈做法〉5 的 `n_mutants` 句子「給『少於 2 個不合併』用」。
  - 兩支既有測試:`t_choice_kill_merge_failure_goes_single` 的 `ph.get("1") == [..., "alphaCase", "bravoCase"]` 與 `ph.get("1", [])[1:] == ph2.get("1")` 會紅。`t_choice_kill_merge_budget` 的「--only 一行 → 不合併」案會紅。
  - 本案 S2 說「呼叫順序跟 `--no-merge` 相同」只涵蓋沒名單的情形,與前一份 S3 衝突時沒有誰蓋過誰的說明。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:171`(S3 條款)
  - file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:200`(預期值表 S3)
  - file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:216`(預期值表 S19)
  - file: `docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:117`(`n_mutants` 句子)
  - file: `scripts/test_lumos.py:146510-146538`(S3 測試)
  - file: `scripts/test_lumos.py:147087-147112`(S19 測試)

severity: minor
blocking: 否(只是說法過強,不影響實作該怎麼寫)
引句:「判錯的方向:不變。殺掉仍由單支判;名單只改順序。」
- 位置:〈實務隱患〉「判錯的方向:不變」、〈WHY〉第一條「判定照舊」。
- 問題:先紅順序會改變誰先碰到停止集合的成員,判定可能不同。名單裡的 c 單支逾時(`timed_out_weak`)或編不過時,原順序 a 本來會強殺掉,現在變 `no_result`「測試掛住」;反方向,原順序 a 先逾時而記 `no_result`,現在 c 先殺掉而記 killed。spec 只承認 `killing_test` 欄可能不同,沒承認 `verdict` 也可能不同。
- 佐證:
  - file: `scripts/lumos:78458`(`_CHOICE_STOP_ON` 含 `compile_error`、`timed_out_weak`)
  - file: `scripts/lumos:28702-28712`(`_KillHooks.between`:組內第一個停止鍵就略過其餘)
  - file: `scripts/lumos:78651-78678`(`_choice_kill_judge`)

severity: minor
blocking: 否(一個合理實作就能補上,但實作者得自己猜)
引句:「對回合併道裡的測試名(恰好對到一個才算);對不到的不列。」
- 位置:〈做法〉1、〈用詞〉「合併失敗名單」。
- 問題:「恰好對到一個才算」沒講是哪一邊恰好一個。可能的讀法有兩種:
  - 失敗的完整名 f 對到合併道裡恰好一個測試名 m。
  - 測試名 m 在全部結果案例中恰好對到一個完整名。
  兩者在 lane 裡有 `foo` 和 `A.foo` 並存、或參數化測試只有部分參數失敗時結果不同。
- 另外,`_choice_merge_classify` 在「有失敗」分支先 return,`miss`/`hits` 檢查在它之後才做,所以名單不能照搬 pass 路徑的檢查。
- 佐證:file: `scripts/lumos:28866-28871`。

severity: minor
blocking: 否
引句:「`_kill_merge_breaker` 計數時順便加一;帶數字的」
- 位置:〈做法〉4 第一點。
- 問題:`unclean` 的計數放進 `_kill_merge_breaker`,但它的簽名是 `(mg, plat, kind, counts)`,沒有原因;呼叫端 `_kill_merge_screen` 目前用 `_why` 丟掉了。spec 沒寫要改簽名或傳什麼。
- 另有三個沒寫明的缺口:
  - 「最後一次:<原因>」存在哪(每個平台組一個,還是整個物件一個);`unclean` 字典沒有順序,推不出最後一次。
  - 「讀不出或過大」要由 classify 的哪些字串歸併過去。classify 實際回「結果檔讀不出來」「結果檔超過大小上限」,以及 `_secev_junit_facts` 的 `why`(已被併成「結果檔讀不出來」),spec 要的「結果檔讀不出或過大」是新字串。
  - 斷路器是「連續 5 次」,但 `unclean` 是累計。S4 只驗全逾時的案,混合原因沒驗。
- 佐證:file: `scripts/lumos:29033-29041`、`scripts/lumos:29082-29083`、`scripts/lumos:28830-28848`。

severity: minor
blocking: 否
引句:「合併基準不乾淨另記 run 事件的 `merge_base_why`(字串,`_CHOICE_MERGE_BASE_WHY` 那幾種;沒有就空字串)。」
- 位置:〈做法〉4 第二點、S4 的「rc 137 → 合併基準被系統收掉」。
- 問題:`merge_base_why` 限定為 `_CHOICE_MERGE_BASE_WHY` 那幾種,「沒有就空字串」。但基準不乾淨的原因有三類沒進這張表:
  - classify 回的「找不到 JUnit 結果檔」「結果檔讀不出來」「N 支對不到結果檔裡的名字」。現行程式用 `.get(why, why)` 原樣印出,記帳時卻會被記成空字串。這幾種正好是 11-25 那次查不出的候選。
  - 單支基準沒量齊(`_kill_merge_singles` 回 False)、合併道少於 2 支。
  - 條件不合(`mg.plats` 已有「條件不合」「基準」兩種標記,卻沒被利用)。
- 多平台時該欄是單一字串,哪個平台組、第一個還是最後一個,spec 沒寫。
- 佐證:file: `scripts/lumos:28735-28736`、`scripts/lumos:28944-28967`、`scripts/lumos:29106`。

severity: minor
blocking: 否
引句:「`_kill_merge_ready` 因時限門(剩下的總時限 < 支數 × 10 秒 × 1.5)回 None 時,印一行到標準錯誤」
- 位置:〈做法〉3、S7。
- 問題一:提示的時限門在 `_kill_merge_ready` 裡排在名稱檢查之後、`_secev_tq()`、結果資料夾圍欄、指令長度檢查之前。時限門擋下就印「請帶 --max-seconds M」,但就算使用者照辦,後面三道檢查仍可能回 None,這時又是靜默不合併,提示就誤導了人。
- 問題二:M 只算「這次剩下要量齊」,沒加已花掉的時間。`mg.deadline` 從 choice-kill 的 `t0 + max_seconds` 起算,t0 之前還有 ast-grep、git grep 的前置工作,多平台時前一組也會吃時間。帶 `--max-seconds 2600` 時 `remaining()` 實際略小於 2535,可能再次被擋。S7 的兩個值(1800/3000)都不靠近邊界,測不到。
- 佐證:file: `scripts/lumos:28900-28920`、`scripts/lumos:78991`(`_KillMerge(self.t0 + self.max_seconds, ...)`)。

severity: minor
blocking: 否
引句:「被殺得快的單點重跑多付量齊基準(約 169 × 4.5 秒)」
- 位置:〈WHY〉第二條「代價:被殺得快的單一壞法多付量齊基準約 12 分鐘」、〈實務隱患〉「跑太久」。
- 問題:單一壞法最常見的情境是補測試後用 `--only` 重跑(`tests_sha` 變了才重跑)。這種重跑的預期結果本來就偏向「現在被殺」,正好是新規則最吃虧的方向:原本幾秒到一次殺掉,現在要付 12 分鐘量齊基準加一次合併。
- 守的測試越少,代價越小;守 169 支時,預設 1800 秒不夠 2535 的時限門,所以預設旗標下這個回歸不會出現,但帶 `--max-seconds 2600` 以上就會。
- spec 把它當已知代價接受,卻沒有任何針對它的 RETIRE-IF 或回頭條件。兩條 RETIRE-IF 都只看存活誤判與先紅命中率。
- 佐證:file: `scripts/lumos:28900-28920`(拿掉 `n_mutants < 2` 後單一壞法照樣走 `_kill_merge_base`,先量齊全部單支基準)。

severity: minor
blocking: 否
引句:「讀治理帳 run 事件的 `merge_unclean` 計數與 choice-kill 事件,照 RETIRE-IF 判」
- 位置:RETIRE-IF ①、REVISIT、S6。
- 問題:RETIRE-IF ① 要量「合併有失敗的壞法,逐支第一支就殺掉的比例」,S6 要量「被殺的壞法逐支跑了幾次」。但治理帳只有三項能用:
  - 每個壞法那筆的 `judged`(merged/single)。
  - run 的 `ran`、`secs`、`merged`、`single`。
  - 新增的 `merge_unclean`。
  這些分不出「合併有失敗」跟「沒跑乾淨」(兩者 `judged` 都是 single),也沒有每個壞法逐支跑的次數,更看不出名單比對失敗的頻率(「N 支對不到」按設計不計)。
- 結果:兩個回頭條件只能靠前一次實驗那種包住 `_kill_run` 的手工偵測量,spec 沒說要不要把這個計數存進帳。
- 佐證:file: `scripts/lumos:78681-78693`(`_choice_event_extra` 欄位)、`scripts/lumos:79015-79022`(run 事件欄位)。

severity: minor
blocking: 否
引句:「實測五個被殺的壞法,合併之後又逐支跑了 19、19、72、96 次(64–391 秒)」
- 位置:〈白話〉第 1 點。
- 問題:寫「實測五個被殺的壞法……逐支跑了 19、19、72、96 次」,只列四個數字。〈實測〉的 FACT 是「5 個壞法:1 個通過(存活)、4 個有失敗」,所以被殺的是四個不是五個。
- 佐證:spec 第 49 行 FACT 與第 23–24 行白話對照。

---

實務隱患鏡頭逐類結果:
- 帳與判定一致性:`tests_sha` 由 `sorted(keys)` 算出,與順序無關。`attempt`、`aborted` 也與順序無關。`judged` 只看 `merge.survived`,先紅順序只在 single 路徑,所以 `judged` 一致。`killing_test` 與 `verdict` 的可能差異見上面第 2 條 finding。
- 成本:壞法被殺得快的單點重跑見第 7 條 finding。預設 `--max-seconds` 1800 對 169 支仍不合併,只多印一行提示。
- 讀帳者:新欄位不會被 `gov --stats` 或推送閘讀壞,因為 `_gov_event_types_ok` 只檢查已登記的鍵,未知鍵忽略。`_choice_ledger_index` 只認 kind 為 choice-kill 的事件,run 事件不進推送閘。去重鍵 `(commit, nodes, gate, kind, token, check)` 不含 `ck`,所以放進字典值也沒問題。
- 既有 S13 測試的 `vol` 集合:兩邊都寫 `{}` 與空字串,逐字比對仍會相等。
- 錯誤路徑:提示只印到 stderr,不影響 stdout 或 `--json` 純度。

固定席節點:
- `guard-kill` 的兩條 ★INVARIANT★(rc 優先序、`--json` 純度)不受影響。合併與先紅順序只在 choice-kill 傳入 `merge` 時走 `_kill_merge_iter`。獨立的 `lumos guard kill` 不經過它。rc 由 results 彙總,本案只改配方交出順序與 stderr 提示。
- `規格閘` 沒有合約。〈做法〉4 登記 run 事件新欄位的落點正確。

最嚴重 severity 是 major,blocking 共 1 條。
