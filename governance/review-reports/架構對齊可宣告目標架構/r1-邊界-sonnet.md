severity: major

我逐節讀完 spec,並對照 repo 查證。以下 13 條是我靠讀碼、`fnmatch` 小實驗和 hook 檔查到的。

## 逐節結論

- frontmatter、白話、問題與最小解:已讀,無 finding。`lands_in` 指的 `Systems/arch-alignment-lens` 存在。
- 做法 1 到 6、驗收條款、回退、實務隱患:見下列 finding。

---

ID: BND-1
severity: major
blocking: 是
引句:「範圍寫在版控的設定檔；`lumos doctor` 每次列出每個宣告範圍與命中的檔數」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26719`(`_review_roles` 讀起點版本的 config)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26629`(理由:「被審的分支不能自己改宣告決定自己拿到哪張卡」)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:28858`(node_home 讀被檢查提交的快照,不讀工作目錄)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26811`(`_stack_questions_config` 直讀工作目錄)

問題:spec 沒說 `arch_targets` 和目標節點規則從哪個版本讀。既有慣例有三種:
- 工作目錄。
- 被審提交的快照。
- 起點(merge-base)版本。

只有 review_roles 這種「決定審查席拿哪張卡」的宣告,明講只信起點。

這份宣告也是決定審查席判準的宣告。若讀工作目錄或終點提交,同一個分支能一次做三件事:
- 在 config 新增 `arch_targets`,範圍設成要審的目錄。
- 在目標節點寫寬鬆規則。
- 提交新寫法。

這樣新寫法就不會被要求「跟鄰居一致」,審查席也只對照分支自己寫的規則。版控只保證「看得到」,並不保證這個宣告的來源可信。「防成為後門」一節只靠印出來和 RETIRE-IF,沒有機械擋。

另外,pre-push 推的 ref 不一定是 checkout 的版本。`_codeloop_guard_verdict` 有 `at_sha` 與 `marker_branch`,工作目錄的未提交 config 編輯會改變推送判準。

判準:spec 必須寫明 config 與節點內容讀哪個版本(起點或終點)。若讀終點,要說明為什麼分支能自己宣告自己的審查基準,並加機械擋,例如宣告變動本身要過人裁。

---

ID: BND-2
severity: major
blocking: 是
引句:「改動檔落在宣告範圍內時，架構對齊段不列鄰居對照檔」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41106`(`if not sibs: continue`)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41109`(`if not out_files: return {}`)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41143`(張力候選只遍歷 `arch["files"]`)

問題:`_arch_alignment_hints` 的輸出以「有同資料夾、同副檔名的鄰居」為進入條件。沒有鄰居的檔會被 `continue` 丟掉,測試檔與非程式副檔名也是。所有檔都被丟掉時整段回 `{}`。

這個 spec 的主要場景是在舊系統裡長出新的 DDD 目錄,例如 `app/Domain/Order/`。新目錄的第一支檔沒有鄰居,走既有路徑就根本不進 arch 段,目標基準也就不會出現。

spec 只描述「落在範圍內就改印」,沒說要改 `_arch_alignment_hints` 的進入條件。S1 的測試只要用「範圍內有鄰居」的 fixture 就會綠,但真實場景失效。

判準:spec 要定義 target 基準的檔是否以「有鄰居」為前提。否則要在 S1 或 S2 補一條「範圍內零鄰居的新檔照樣出現目標基準」,並說明測試檔與非程式檔的處理。

---

ID: BND-3
severity: major
blocking: 是
引句:「不關掉架構對齊、也不做全域開關」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:40547`(`_glob_first_match` 沿用 fnmatch,`**` 匹配任何路徑)
實測:`fnmatch("x.cs","**")` 為 True。

問題:單一 `"paths": ["**"]` 會把整個 repo 的改動檔都換成目標基準。這就是 spec 自己宣告不做的全域開關,只是換了寫法。

spec 的防護只有「印出來」、doctor 列命中檔數、RETIRE-IF 觀察。沒有範圍占比上限,也沒有對 `**`、`*`、`**/*` 這類全覆蓋樣式的拒收。

這與 repo 的取向不合。memory 的「寧可機械擋」、review_roles 的壞宣告整份不用,都傾向機械拒絕。`[retire:人裁]` 是 90 天尺度的回頭條件,擋不住當下的全域關閉。

判準:spec 要擇一:
- 拒收全覆蓋樣式。
- 限制單一範圍占 repo 程式檔的比例。
- 明講「全域可宣告」,並改寫第一段的立場。

---

ID: BND-4
severity: major
blocking: 是
引句:「同一支檔只能落在一個範圍；範圍重疊、節點不存在、節點沒有任何規則，都算宣告錯誤。」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:40535-40553`(fnmatch 語意:`*` 跨 `/`、開頭 `**/` 去掉再試)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26642-26645`(review_roles 對 path 的驗證:拒空白、`./`、`/` 開頭與反斜線)

問題:spec 沒定義 glob 語意,也沒定義「重疊」怎麼判。我在 Python 3.14 用 `fnmatch` 實測:
- `app/Domain/*` 匹配 `app/Domain/a/b.cs`,所以 `*` 等於 `**`。
- `app/Domain/**` 不匹配 `app/Domain` 本身。
- 尾斜線 `app/Domain/` 不匹配任何檔。
- `../x/**` 匹配 `../x/a`。
- 大小寫比對依平台,`App/Domain/**` 配不到 `app/domain/a.cs`。
- 反斜線樣式永遠配不到(git diff 路徑一律 `/`)。
- 絕對路徑樣式永遠配不到。
- 中文路徑可以匹配。

兩個 glob 樣式的交集沒有靜態判法。要判「重疊」只能拿實際檔案去比對,而這會產生兩個問題:
- 在 pitfalls 時只有改動檔可比,「重疊」的判定隨本次改動變動。
- 在 doctor 時要列舉整個 repo(`git ls-files`),判定又隨 repo 內容變動。

同一份 config 因此可能「昨天綠、今天加了一支檔就紅」。既有的 `_glob_first_match` 是「第一條命中算數」,不是報錯。

另有靜默失效:`..`、絕對路徑、反斜線、尾斜線、`paths: []` 都不報錯,只是永遠命中 0 檔,等於「宣告了但沒生效」。doctor 的「命中檔數 0」也沒被列為錯誤。

判準:spec 要寫明:
- glob 方言(複用 `_glob_first_match`,還是 `**` 另算)。
- 路徑正規化與驗證規則,可照 review_roles。
- 重疊的判定母體(改動檔、`git ls-files` 或快照)。
- 空陣列與零命中的處置。

---

ID: BND-5
severity: major
blocking: 是
引句:「lumos doctor 應報錯，pitfalls --diff 應印一行警告並讓該檔退回鄰居基準」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/hooks/pre-push:316-330`(pre-push 跑 `doctor --ci`,失敗就「擋下」)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:1740-1775`(doctor 的硬 issue 動 rc,`warn_soft` 不動 rc)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26811-26830`、`28858-28895`(既有設定欄位壞值:用預設加警告,不擋)

問題:「doctor 報錯」有兩種讀法,後果差很多:
- 硬 issue:pre-push 與 CI 的 `doctor --ci` 都會擋下整個 repo 的推送。
- `warn_soft`:最多印 3 條,`--ci` 才全列,不影響 rc。

spec 沒選。若選硬 issue,筆記節點被改名或刪掉、或新加一支檔造成範圍重疊(見 BND-4),就會擋住所有人的推送。這和「已宣告的專案設定欄位會被忽略,不影響其他閘」以及 pitfalls 的「退回鄰居」寬鬆設計不一致。

既有設定欄位的慣例是壞值用預設加警告,doctor 只用 `warn_soft` 提醒。

判準:spec 要寫明 doctor 這項是 `warn_soft` 還是 hard issue。若選 hard,要說明為何與 stack_questions 與 node_home 的慣例不同,以及 S3 的測試要斷言 rc。

---

ID: BND-6
severity: major
blocking: 是
引句:「逐條貼出規則內容（貼內容不貼路徑）」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41560-41564`(既有對照檔清單 `[:6]`)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41569-41573`(候選 `[:6]`,超過印「…另有 N 條」)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:48725`(check 表態最多列 10 問)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:1763`(doctor 軟段預設 `_SOFT_CAP = 3`)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/hooks/pre-push:413-418`(tier 為 high 時,pitfalls 全文經 `sed` 灌進 stderr)

問題:spec 沒給規則條數上限,也沒說「逐條貼出」是每支檔各貼一次,還是每個節點貼一次。節點有上千條、改動檔有 50 支時,輸出可以達到「規則數 × 檔數」。

現有的所有輸出都有硬上限(6、10、3 加總數)。這一條是唯一沒有預算的。

更下游還有一個缺口:規則怎麼進審查席的派工詞?既有的 `LUMOS-IMPACT` 與 `LUMOS-SPEC` 有 hook 自動附上,「手貼」的實測只有 14/209。spec 的 §3 只是印出,§4 的範本沒有佔位,沒有 hook 注入。大量規則靠編排者手貼,貼漏了審查席就沒有基準。

判準:spec 要定:
- 規則條數上限(超出時印「另有 N 條」並指路 `--json`)。
- 貼出的單位(每節點一次)。
- §7.6 要有佔位符,以及誰負責注入(hook 或手貼)。

---

ID: BND-7
severity: major
blocking: 是
引句:「當改動檔不在任何宣告範圍內時，pitfalls --diff 的架構對齊段應與沒有宣告時逐字相同」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41115`(`questions` 是整份共用的 `_ARCH_QUESTIONS`)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41558`(印頭一行「拿同層最像的既有檔當對照」)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41143`(張力候選遍歷 `arch["files"]`)

問題:S2 只規定「全部檔都在範圍外」。遷移中的 repo 最常見的是混合改動:一部分檔在範圍內,一部分在範圍外。spec 沒定義這種情況:
- 輸出的 `arch["questions"]` 與 CLI 頭一行是整份共用的,混合時是用鄰居三問、目標三問,還是兩者並列?
- 一份派工單只有一個架構對齊席,§7.6 要選哪個分支?
- 範圍內的檔在 `arch["files"]` 的形狀是移除該鍵、空清單,還是物件?`_tension_candidates_into` 遍歷 `files.items()` 並要求 `sibs`,形狀沒定,會誤處理。
- 全部檔都在範圍內時,頭一行還寫「拿同層最像的既有檔當對照」,是錯的提示。

判準:spec 要明定混合改動的輸出規則(分組列出,各自帶自己的問題),以及 JSON 形狀與張力候選對 target 檔的處理(跳過)。S1、S2 之外補一條混合案例的條款。

---

ID: BND-8
severity: minor
blocking: 否
引句:「宣告錯誤時印一行警告、該檔退回鄰居基準」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26811-26820`(`utf-8` 嚴格讀,壞了用預設加警告)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:28870-28890`(`utf-8-sig` 容忍 BOM)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26631`(review_roles 壞宣告整份不用)

問題:「該檔退回」只涵蓋單項宣告錯誤。以下層級的錯誤沒規定:
- config JSON 壞掉。
- 非 UTF-8 或帶 BOM。
- `arch_targets` 不是清單。
- 項不是物件。
- `paths` 不是字串清單。
- `node` 不是字串。
- 兩項指同一個節點。

既有讀取器對壞值各有不同:`_stack_questions_config` 是「utf-8 嚴格」,`_nodehome_config` 是「utf-8-sig」,review_roles 是「整份不用」。實作者無從選擇。

`node` 的格式也未定,包括有無 `.md`、中文 NFC 或 NFD(macOS 檔名)、大小寫。

判準:spec 要寫明壞值層級的處置(建議照 review_roles「整份不用加一句警告」,或照 stack_questions「用預設」),以及編碼方式,並複用 `_nodehome_config` 的捷徑檔防護。

---

ID: BND-9
severity: minor
blocking: 否
引句:「pitfalls --diff 應印一行警告並讓該檔退回鄰居基準」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/hooks/pre-push:405`、`417`、`491`(三處都是 `2>/dev/null`)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:48218-48224`(check 以子程序跑 pitfalls,stderr 不顯示,stdout 取第一個 `{` 開頭的行)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26823`(既有警告走 stderr 的「提醒:」)

問題:「印一行警告」沒說 stdout 還是 stderr。`--json` 模式下 stdout 必須保持可解析,既有警告走 stderr。但 pre-push 三處呼叫 pitfalls 都 `2>/dev/null`,`code-loop check` 也吃掉子程序的 stderr。

照既有慣例寫成 stderr,宣告錯誤在 hook 與 check 路徑上永遠不可見,只有手動跑 pitfalls 或 doctor 才看得到。這時 S3 的「該檔退回鄰居基準」在 push 路徑上是靜默發生的。

判準:spec 要寫明警告通道,並說明 push 路徑是否可見(或是否靠 doctor 兜底)。若要在 JSON 帶 `arch_warnings` 欄位,要寫出來並加進測試。

---

ID: BND-10
severity: minor
blocking: 否
引句:「pitfalls 多一次設定讀取與 glob 比對，改動檔數量級，額外成本可忽略。」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41200`(「★vault-free★,pitfalls 在 pre-push 熱路徑上不載圖譜」)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41596-41598`(實測 pitfalls 0.18s、impact 4.7s,因此不在 pitfalls 裡跑 impact)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26806-26808`(「不走載 vault 的 helper」)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:29137`(`_nodehome_reader` 可從 git 單檔讀)

問題:這條效能評估漏了三點:
1. pitfalls 要讀目標節點(判「節點是否存在、有幾條規則」,並要貼規則)。這和「不載圖譜」的明文不變量衝突。實作者若用 vault 載入 helper,pre-push 每個 ref 的成本從約 0.2 秒變成數秒。spec 沒指定讀取方式,可用 `_nodehome_reader` 單檔讀。
2. `code-loop check` 對同一個推送最多跑 2 次 pitfalls(推送範圍加 merge-base 範圍,`48218`、`48260`)。
3. doctor 要列「命中檔數」且判重疊,需要整個 repo 的列舉。大 repo 加上 `**` 的成本不是「改動檔數量級」。

我沒有實測。這是讀碼得出的結論。

判準:spec 要寫明節點以哪個 helper 讀(單檔),並把效能欄改成涵蓋這三點。

---

ID: BND-11
severity: minor
blocking: 否
引句:「當派工單的架構對齊席拿到目標基準時，templates.md §7.6 應改用違反宣告規則／範圍內一致／依賴範圍外三問」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/skills/lumos-design-loop/templates.md:324`(§7.6 標題:code-loop 與 design-loop 皆派)
`/Users/enzo/harness/lumos-toolchain-target-arch/skills/lumos-design-loop/templates.md:337`(設計審才問的第 4 問,沒有改動檔清單)

問題:§7.6 同時用於設計審,而設計審沒有 diff 與改動檔清單,也沒有「落在範圍內」的觸發條件。spec 的三問、S5 與 `lands_in` 都只講改動檔。

設計審派工單怎麼拿到目標基準,是否要從計劃的 `lands_in` 或提到的檔去對範圍?spec 完全沒提。S5 又是 `[manual:]`,沒有機械驗收。

判準:spec 要寫明設計審是否支援目標基準,如果不支援就明講,並在 §7.6 標明該分支只用於代碼審。

---

ID: BND-12
severity: minor
blocking: 否
引句:「當推送範圍內有改動檔用目標基準時，code-loop check 應印出目標節點與命中檔數，不改變放行或擋下的判定。」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41386-41391`(整檔刪除:`cur_file` 改為舊路徑,但不進 `added`)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:41408`(`added` 只收有新增行的檔)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:48230-48246`(check 的 tier 用推送範圍,表態用 merge-base 範圍,兩個範圍不同)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:26747`(角色鏡頭把改名算新路徑、刪除算舊路徑)

問題:「命中檔數」的口徑沒定:
- 改名只看新路徑,把檔搬出範圍就脫離目標基準,搬進範圍就被套用。
- 純刪除與純改名(內容不變)的檔不在 `added`,不計。
- 主線合進分支後,推送範圍會把別人的檔算進本次「N 支檔」。check 自己的表態段特別避免這點(`48230` 註解 r3 邊界席 B1),但 S4 沒說用哪個範圍。
- 前面 BND-2 的無鄰居檔、測試檔、非程式檔是否計入也未定。

這條只是印出,不影響判定,所以 minor。

判準:spec 要寫明「命中檔」是 `added` 的子集、用哪個範圍,以及改名與刪除的處置。

---

ID: BND-13
severity: minor
blocking: 否
引句:「一般 Systems 節點，正文有一節〈目標規則〉」
審材外佐證 file:
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:6945-6960`(`_h2_section_lines` 只認 ATX 的 `##`,fence 內不算)
`/Users/enzo/harness/lumos-toolchain-target-arch/scripts/lumos:6975`(`_clause_structure_verdict` 對重複、遮蔽、看不懂的清單寫法判 fail)

問題:節的層級、`[A<序號>]` 的解析和 `[S<序號>]` 條款解析器的關係都沒定:
- 是複用 `_h2_section_lines`(只認二級標題),還是任意層級的標題?
- 同編號重複定義、編號跳號、`[A1]` 落在 fence 內、同一節點兩個〈目標規則〉節,怎麼處理?
- 「節點沒有任何規則」是沒有這一節,還是節內零條?
- 既有解析器對重複與看不懂的寫法判 fail,不會靜默忽略。spec 沒說要不要沿用。
- 規則行帶 `[test:]` 時,會進既有的測試綁定掃描,doctor 的存在檢查是否適用?(ArchUnit 這類 Java 測試要靠該棧的測試索引才認得到。)

判準:spec 要寫明:複用 `_h2_section_lines` 與條款解析器(並引用),重複與跳號的處置,以及「零規則」的判定。

---

## 實務隱患逐類

- **併發**:無。理由:設定與節點只在指令執行時唯讀,沒有寫入。但 BND-1 的「讀哪個版本」不明,工作目錄讀取在 pre-push 推非 checkout 的 ref 時會有一致性問題。
- **效能**:見 BND-10。
- **資源(輸出量)**:見 BND-6。上限未定,是 spec 的缺口。
- **回滾**:回退節的「欄位被忽略」這條,現有 doctor 沒有檢查 config 未知頂層鍵(我搜過沒有)。所以回滾後宣告靜默失效,審查席又會對遷移中的 DDD 新碼判「跟鄰居不同」。回退節沒提醒這個行為會自動復發的風險,只能算低風險 minor,不另立 finding。

總結最嚴重 severity: major;blocking 共 7 條
