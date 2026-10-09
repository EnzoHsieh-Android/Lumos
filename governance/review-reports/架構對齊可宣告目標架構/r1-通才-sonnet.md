severity: major

我沒有收到 hook 附的合約或事故節點,所以那一項略過。下面的行號都是 `/Users/enzo/harness/lumos-toolchain-target-arch` 內的現況。

---

ID: GEN-1
severity: major
blocking: 是
引句:「加目標基準分支——三問改為①有沒有違反宣告的哪一條目標規則（引規則編號）②範圍內新寫的程式彼此一致嗎③有沒有從範圍內直接依賴範圍外舊寫法、而目標規則禁止的。」
審材外佐證 file:
`skills/lumos-design-loop/templates.md:333`
`scripts/lumos:41562`
`scripts/lumos:41112`

問題:基準只能整份派工單選一種。範本只有一個 `{鄰居檔清單}` 佔位,`arch["questions"]` 也是全域一份三問。真實推送常常混合,例如同一個提交改了 `app/Domain/**`,也改了範圍外的舊 Billing 檔,或兩個宣告範圍指向兩個不同節點。
- 整單用目標三問:範圍外的檔沒有「宣告規則」可引,重大偏離(引入第二種做法)抓不到。
- 整單用鄰居三問:範圍內的 DDD 新檔又被判成「第二種做法」major,spec 想解的問題原樣回來。
- 兩個節點的規則全貼進同一單:審查員會把 Domain 的規則套到 Billing 的檔上。

判準:spec 必須寫明每支檔對應哪個基準,以及混合單怎麼派。例如派工詞按檔分組,每組各貼自己的規則。目前沒寫。

---

ID: GEN-2
severity: major
blocking: 是
引句:「templates.md §7.6 應改用違反宣告規則／範圍內一致／依賴範圍外三問」
審材外佐證 file:
`skills/lumos-design-loop/templates.md:324`
`skills/lumos-design-loop/templates.md:341`

問題:§7.6 標明「code-loop 與 design-loop 皆派」,設計審還多問第四問(落點)。設計審沒有 diff,也沒有 `pitfalls --diff` 的 `files`,glob 無檔可比。這時「架構對齊席拿到目標基準」由誰、依什麼判定,spec 沒寫。
- 照現狀,設計審的鄰居清單由編排者自己挑。一份要貫徹 DDD 的新模組設計,會在設計關被判成「跟既有不一樣」。
- 設計關是 spec 的立案動機(新開發想貫徹 DDD)最先碰到的關卡,補了代碼審、漏了設計審,等於在設計關擋掉自己。

判準:spec 要二選一並在 S5 補驗收。
- 一是明講設計審也讀 `arch_targets`,並說明怎麼從計劃的 `lands_in` 或提到的路徑對到範圍。
- 二是明講設計審的架構對齊席不套目標基準,並說明為何可以。

---

ID: GEN-3
severity: major
blocking: 是
引句:「同一支檔只能落在一個範圍；範圍重疊、節點不存在、節點沒有任何規則，都算宣告錯誤。」
審材外佐證 file:
`scripts/lumos:41083`
`scripts/lumos:41409`

問題:範圍的單位是「路徑 glob」,沒有「新檔 vs 既有檔」的區分,也沒有排除語法。`added` 收的是任何有新增行的檔,`_arch_alignment_hints` 也不分新舊。
- 在舊系統長出新模組,典型佈局是新舊混在同一棵樹。要宣告 `app/Domain/**`,就得連 `app/Domain/Legacy/**` 一起納入。
- 想用第二條宣告把 Legacy 切出去,又會撞「範圍重疊=錯誤」。所以舊檔只能被迫納入目標範圍。
- 結果:一個舊檔順手修個小 bug(例如 `app/Domain/Legacy/OrderHelper.cs`),會拿目標規則審,出 major「違反 A3」。作者只能順手重構舊碼,或放寬範圍。
- 寬範圍的代價是舊碼也被取消鄰居一致要求,與「防成為後門」互相矛盾。

判準:spec 要提供排除語法(例如 `exclude`),或定義「只對本次新增的檔套目標基準」。

---

ID: GEN-4
severity: major
blocking: 是
引句:「「當地慣例贏」那句在宣告範圍內，以目標架構節點為當地慣例。」
審材外佐證 file:
`scripts/lumos:41135`
`scripts/lumos:41157`
`scripts/lumos:47462`
`skills/lumos-design-loop/templates.md:345`

問題:spec 只處理了「慣例 skill」,沒處理張力表態(tension)機制,而這個機制的每一環都綁在鄰居上。
- 「可能撞」候選由 `arch["files"]` 裡的 `sibs` 算出。目標範圍內的檔沒有鄰居。
  - 實作若留著舊鄰居算候選,會拿範圍外舊寫法當「既有」,hint 是錯的。
  - 若不算,範圍內就永遠沒有 `hint`。
- tension 表態要求 `existing` 是 path:line 清單,並驗證存在(`scripts/lumos:47462`),不能直接引用規則編號 A3。
- §7.6 的 tension 段(`templates.md:345`)叫審查員「existing 指的檔真的那樣寫嗎(開檔對照)」,目標基準下沒有對應的檔。
- 具體衝突:目標規則「Repository 只存取整包聚合」對上棧別檢核題「不要整包載入/N+1」。
  - 架構席依「major 只給違反宣告規則」,判 major,必須折。
  - 棧別題要不要答 tension、`existing` 填什麼,spec 沒有答案。
  - code-loop 的規則是 major 不能被 tension 吃掉。

判準:spec 要寫明目標範圍內候選怎麼算,以及 `existing` 可以引節點行號。否則張力機制在目標範圍內等於失效。

---

ID: GEN-5
severity: major
blocking: 是
引句:「改印「基準：目標架構 <節點>」並逐條貼出規則內容（貼內容不貼路徑）」
審材外佐證 file:
`skills/lumos-design-loop/templates.md:335`
`scripts/hooks/claude/dispatch-lens-hook.py:25`
`scripts/hooks/pre-push:405`

問題:規則內容要靠編排者從 pitfalls 輸出手貼進派工詞。
- 本專案自己的量測是「手貼實測 209 份只有 14 份貼」(約 7%),所以 hook 才改成自動附。
- dispatch hook 目前只認 `LUMOS-IMPACT` 和 `LUMOS-SPEC` 兩種標記(`dispatch-lens-hook.py:25-26`),spec 沒有新標記、沒有 hook 改動。S5 還是 `[manual:…]`,沒有機器驗收。
- 沒貼規則的審查席,目標三問①要「引規則編號」卻沒有規則可引,只會自己編。
- `逐條` 沒有上限。一個很多條規則的節點,在 20 支檔、多次 pitfalls 輸出(pre-push 至少 3 處)裡會被重複印。人讀輸出沒說去重或截斷。
- 若改 hook,`dispatch-lens-hook.py` 屬 ANCHOR_FILES,要走 anchor approve。spec 沒列。

判準:要嘛規則經 hook 或 `lumos` 指令機械附上(例如新標記),要嘛 S5 加機器驗收「派工詞含規則 id」。另外要有大小上限,以及單一節點只貼一次的規則。

---

ID: GEN-6
severity: major
blocking: 是
引句:「範圍寫在版控的設定檔；`lumos doctor` 每次列出每個宣告範圍與命中的檔數」
審材外佐證 file:
`scripts/lumos:26811`
`scripts/lumos:41083`
`scripts/hooks/pre-push:405`

問題:「防成為後門」的做法只有印出來,沒有任何擋或比對,S4 還明講不改判定。
- 同一次推送裡,作者(或自動開發的 agent)可以同時做三件事:新增 `arch_targets`、新增或改寫目標節點、寫出偏離鄰居的程式。
- pitfalls 依現行慣例從工作目錄讀 `.lumos/config.json`(同 `_stack_questions_config`)。鄰居檔也從磁碟讀。審這次推送的基準,就是這次推送自己寫的宣告。
- 沒有「宣告範圍或規則被本次推送改動」的偵測或提示,也沒有改從 merge-base 版本讀基準的規則。
- 推非目前 checkout 的 ref 時,基準還會來自目前工作目錄的設定,不是被推的提交。pre-push 對每個 ref 跑 pitfalls,卻不切換設定來源。CI 在乾淨 checkout 上也可能得到不同的基準。

判準:至少要寫明基準讀自 merge-base 版或被審提交。宣告或目標節點在本範圍內有改動時,`code-loop check` 要印出「本次改動了宣告」。

---

ID: GEN-7
severity: major
blocking: 是
引句:「若宣告指到不存在的節點、節點沒有任何目標規則或兩個範圍重疊，lumos doctor 應報錯」
審材外佐證 file:
`scripts/lumos:467`
`scripts/lumos:41398`

問題:glob 語意與「重疊」的判定都沒定義,而它們決定哪些檔用哪個基準。
- 沒寫解讀方式:
  - 相對 repo 根還是別的起點。
  - `**` 是否遞迴。
  - `*` 會不會跨 `/`:`fnmatch` 會跨,`PurePath.full_match` 不會。
  - 大小寫:macOS 本機和 Linux CI 的判定可能不同。
  - CJK 檔名的 NFC/NFD 正規化。
- 重疊沒定義:
  - 用檔案集合判定,則宣告時範圍內還沒有檔(正是新模組的情境),doctor 不會報錯。
  - 等第一個命中兩條的檔出現,才在 pitfalls 當下警告並退回鄰居基準。
  - 用 glob 代數判定則在一般情況下無法判定,例如 `a/**/x/**` 對 `**/y/*`。
- 退回只作用於「該檔」,還是整份宣告無效,spec 沒寫。
- pre-push 把 pitfalls 的 stderr 丟掉(`2>/dev/null`,`pre-push:405`),警告看不到。實際只靠 doctor 擋。
- 路徑比對只認新路徑。純改名沒有 `+++` 行,不會進 `added`;刪除同理。N 支檔的計數因此會少算,也應該寫明。
- S3 在沒有這些定義前寫不出紅燈測試。

判準:spec 要指定 glob 實作(建議 `full_match`,大小寫敏感,以 `git ls-files` 為準)、重疊的判定方式與宣告時機,以及警告的通道。

---

ID: GEN-8
severity: minor
blocking: 否
引句:「`--json` 的 `arch_alignment` 每支檔多 `baseline: neighbors|target` 與 `target_node`。範圍外完全照舊。」
審材外佐證 file:
`scripts/lumos:41083`
`scripts/lumos:41110`
`scripts/lumos:41451`
`scripts/lumos:41564`

問題:這句話自相矛盾,實作形狀也沒有交代。
- 現況 `files` 是 `{檔: [對照檔…]}`,值是 list,不能直接「多」欄位,必須改形狀。
- 「每支檔多 baseline」與「範圍外完全照舊」、S2 的「逐字相同」互相抵觸。範圍外也多一個欄位,輸出就不是逐字相同。
- `_arch_alignment_hints` 在 `out_files` 為空時回 `{}`(`41110`),`if arch:` 才印段落和算候選。整次推送都在目標範圍內時(純 DDD 功能分支,最主要的用法),照現行骨架完全不會輸出任何「基準:目標架構」。
- 人讀輸出的 `[:6]` 截斷、`idiom_skills`、`questions` 都是全域一份,沒說怎麼分基準。

判準:spec 要明定 JSON 新形狀,並明講 S2 只比對「沒宣告的專案」的輸出。

---

ID: GEN-9
severity: minor
blocking: 否
引句:「效能：pitfalls 多一次設定讀取與 glob 比對，改動檔數量級，額外成本可忽略。」
審材外佐證 file:
`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:58`
`scripts/lumos:41200`
`scripts/lumos:24191`

問題:效能估算漏掉讀節點。
- pitfalls 是 vault-free,圖譜明文記著「pitfalls 在 pre-push 熱路徑上不載圖譜」。載入 Env(vault) 實測要 4.7 秒。
- 目標基準需要找到 vault、解析節點、驗證〈目標規則〉一節,spec 的「只讀設定」沒承認這點。
- 單檔讀取很便宜,不是效能問題,是契約問題。pre-push 一次推送會呼叫 pitfalls 數次(`pre-push:405`、`417`、`491`,另有 code-loop check 內的兩次),而 `find_vault` 在沒有 vault 的 repo 回 `None`,這時行為沒寫。
- spec 要明講「只讀單一檔、不經 Env」,以及沒有 vault 時走鄰居基準並警告。

---

ID: GEN-10
severity: minor
blocking: 否
引句:「已宣告的專案設定欄位會被忽略，不影響其他閘」
審材外佐證 file:
`scripts/lumos:26811`
`skills/lumos-design-loop/templates.md:324`

問題:設定欄位被忽略是靜默的,這在消費專案(vendored lumos)會出事。
- 設定讀取各自獨立,只讀自己認得的鍵,未知鍵不警告。
- 舊版 lumos 的消費專案宣告了 `arch_targets`,宣告被忽略,也沒有提示。
- 新版 lumos 搭配舊版 skills(templates.md 沒有目標分支)時,pitfalls 印「基準:目標」,三問卻仍問「跟鄰居一樣嗎」。
- spec 沒有版本互認或能力握手。
- 回退只講「撤回讀取與分支」,沒講只撤其中一半時的狀態。

---

ID: GEN-11
severity: minor
blocking: 否
引句:「每條以 `[A<序號>]` 開頭（A1、A2…在該節點內遞增，跟驗收條款的 `[S<序號>]` 同一種寫法、用 A 區分是架構規則）一行一條」
審材外佐證 file:
`scripts/lumos:6873`
`scripts/lumos:6875`

問題:規則怎麼被辨識與維護沒有講清楚。
- S 條款有一套很長的辨識規則(列表符號、表格、勾選框、引用與定義的區分,`6875-6876`)。A 規則「同一種寫法」,卻沒說是否沿用同一支解析,也沒說程式碼圍欄裡的 `[A1]` 怎麼處理。
- 沒有穩定 id:規則廢止後編號會重排,舊的 finding 引用「違反 A3」就指錯了。重複編號也沒有檢查。
- 〈目標規則〉是正文散文。依專案 CLAUDE.md,這種正文只算線索,沒有 `[confirmed:]` 與過期機制。卻能在審查裡讓席位給出必須折入的 major。
- ② 範圍內新寫的程式彼此一致嗎」沒有嚴重度。「major 只給違反宣告規則或跨層直呼」讓範圍內引入第二種 HTTP client 這類做法不再 major。

---

ID: GEN-12
severity: minor
blocking: 否
引句:「- Systems/arch-alignment-lens」
審材外佐證 file:
`skills/lumos-code-loop/SKILL.md:29`
`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:60`

問題:`lands_in` 只列了一篇,但要改的現況散在別處。
- `SKILL.md:29` 寫死了「pitfalls --diff 會吐同層最像的對照檔」和「引入第二種做法或跨層直呼才算 major」,改後會過期。
- `pitfalls-code-loop.md:60` 記載 `pitfalls --diff --json` 的欄位,加 `baseline` / `target_node` 後會漂移。
- `templates.md` 與 `scripts/lumos`(`arch_alignment` 段)的家也要列。
- 專案鐵則 5 要求改到的每支檔都有家,並寫進 `lands_in`。

---

實務隱患逐類:
- 併發:無。設定與節點唯讀,其他會談若同時改節點,只會讀到新或舊的完整版本(專案寫入慣例是原子替換)。
- 效能:規模上可忽略,但契約問題見 GEN-9。doctor 的「命中檔數」若走檔案系統遍歷,會算進 `bin/obj` 或 `node_modules`,應規定用 `git ls-files`。
- 資源:節點內容無上限地貼進派工詞,見 GEN-5。
- 回滾:見 GEN-10。
- 凍結審材:節點改動不在凍結的 patch 裡,同輪各席讀到的規則可能不同。審查中改節點修規則,要有「重新派工」的規定。這點併在 GEN-6 的處置裡。

總結最嚴重 severity: major；blocking 共 7 條
