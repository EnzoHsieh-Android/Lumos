severity: major

審查範圍:逐節讀完 r2 快照全文,對照 `scripts/lumos` 現行讀宣告、取改動檔、派工鏡頭與 doctor 的實作。固定席 `Systems/arch-alignment-lens` 的判斷放在最後。

## Findings

### 1. 改名檔的舊路徑拿不到,且「改名照鄰居審」與「刪清單行就畢業」互相打架

severity: major
blocking: 是(spec 要求的行為在現有函式上做不到,而且兩條規則對同一輸入給出相反答案)

引句:「改名的檔,舊路徑在清單上也照鄰居審」
引句:「少掉的那幾行對應、而且這次範圍內有改動的檔,照它命中的目標節點審」

查證:
- file: `scripts/lumos:57465-57470` 的 `_arch_target_changed_files` 只回 `ref == head` 的新路徑。
- file: `scripts/lumos:37246-37276` 的 `_review_role_changed_files` 把改名配對收在區域變數 `renamed`,只在「新路徑是簿記檔」時才多回舊路徑。三處讀法目前拿不到改名的舊路徑,spec 沒說由哪支函式提供。

輸入:起點版清單有 `app/src/main/java/a/OldVm.kt`。分支把它 `git mv` 成 `NewVm.kt`,同時重構到相似度仍 ≥50%,並照畢業流程把清單那一行刪掉。

預期:這是 spec 要服務的「舊檔重構、當場畢業」,該照目標審。

實際:
- 第 5 點:舊路徑在起點版清單上,所以照鄰居審。
- 第 6 點:少掉的行是 `OldVm.kt`,但改動檔集合裡只有 `NewVm.kt`,「對應」比不上,畢業也不成立。
- 第 7 點:印「改名的舊檔 N 支沒同步改清單」,等於要求作者把新路徑補進清單。這一補就是新增行(見 finding 2)。

唯一不踩雷的改名流程是留著舊行不刪,結果就是照鄰居審。重構常伴隨改名,spec 想堵的「最需要照目標審的那次反而沒審到」在這個輸入上沒有解。

### 2. 改名要求「把清單那一行改成新路徑」,而這就是新增行,會讓整個分支失去畢業

severity: major
blocking: 是(spec 規定的標準改名流程,會觸發 spec 自己的整批不畢業)

引句:「舊檔改名時要在同一個提交把清單那一行改成新路徑,不然架構測試會檢查它」
引句:「宣告有任何不同、清單有新增行、任一版讀不懂、這條路沒有可信起點版,就整批不畢業、全照起點版判」

輸入:同一分支裡刪掉 A 的清單行(重構 A,要畢業),又照第 8 點把改名檔 B 的清單行改成新路徑 `B2`。

預期:A 畢業,照目標審。

實際:頭版清單相對起點版多出 `B2` 這個新增行,A 跟著失去畢業,說明行印「舊檔清單新增 1 行,本次仍照起點版」。

同類的第二條路徑:分支把主線合進來,主線上別人做的改名(同樣是新增行)也會讓本分支整批不畢業。起點版取的是和主線的分岔點(`scripts/lumos:57364`),合進來的主線提交算在 base..head 裡。

spec 沒定義「改名造成的新增行」的特例,也沒說合併主線時怎麼算。

### 3. doctor 的範圍標記比對沒說去哪找架構測試檔

severity: major
blocking: 是(S9 的比對沒有輸入來源,實作者只能猜)

引句:「`lumos doctor` 拿這組目錄跟 arch_targets 裡指向目標節點的 `<目錄>/**` 宣告當集合比,不一致就提醒」

`--test-file` 可自訂(第 2 點),但路徑沒有寫進 `.lumos/config.json`、節點或任何登記處。spec 沒說 doctor 怎麼找到含 `lumos-arch-scope:` 的檔,是掃全部 `*.kt`、預設路徑,還是別的辦法。

輸入:`--test-file feature-core/src/test/java/x/ArchTest.kt`。doctor 看不到這支檔,沒有輸入來源,S9 的提醒行測不出來。

另一個破口:比對對象是「指向目標節點的所有宣告」,不分哪一個節點。專案另有第二個目標節點(例如前端)時,它的 `<目錄>/**` 會被算進集合,誤報不一致。標記行沒有記節點名,無法區分。

### 4. 派工鏡頭的設計審路徑沒有納入舊檔清單

severity: minor
blocking: 否(結果是設計審多給了不適用的規則,不會漏審)

引句:「推送前風險分級、派工鏡頭、代碼審判定三處,在讀宣告的同一版讀舊檔清單」

file: `scripts/lumos:64862-64880` 的 `_dispatch_lens_spec_arch_text` 是派工鏡頭的第二條路(設計審)。它讀 HEAD 版宣告,拿計劃文字提到的路徑跑 `_arch_target_lens_split`,和代碼審共用同一支比對。第 5 點沒說這條路讀不讀清單。

輸入:計劃提到一支仍在舊檔清單上的舊檔。
- 預期:設計審鏡頭和代碼審一致,照鄰居。
- 實際:若不改這條路,設計審席被告知這支檔要照目標規則,代碼審卻照鄰居。

共用的 `_arch_target_lens_split` 一旦加上清單參數,這條路也必須決定傳不傳。

### 5. ddd=lite 的「提到聚合的規則」少算一條

severity: minor
blocking: 否(S2 的「RULE 行不含『聚合』二字」會抓到,但做法段的數字是錯的)

引句:「現在是 Repository、用例、ViewModel 業務規則、測試邊界四條」

file: `skills/lumos-project-notes/commands/target-arch-android-template.md:58` 的深模組規則寫「模組邊界劃在聚合與用例(深模組)」,也提到聚合,所以是五條。

`interfaces=always` 會把這條整條換掉,但 `interfaces=deep` 加 `ddd=lite` 的組合需要它的無聚合版本。spec 沒列這個變體,實作者照「四條」做會讓 S2 紅。

### 6. 說明行裡的「第一行檔數」在現行輸出中不存在

severity: minor
blocking: 否

引句:「第一行的檔數標明「含畢業 N 支」」

file: `scripts/lumos:57634-57636` 的 `_arch_target_check_lines` 每個目標節點各印一行「架構對齊基準:目標 {node} {n} 支檔」,沒有合計行。節點有兩個以上時,「第一行」指哪一行、「含畢業 N 支」是整體還是每節點,spec 沒說。S6 同樣寫「第一行檔數」。

### 7. `--scope` 檢查漏掉會讓架構測試與宣告靜默失效的輸入

severity: minor
blocking: 否

引句:「不能有反斜線或控制字元、第一段不能有萬用字元、不能少於兩段」

實測 `_arch_targets_config` 照單全收這三種 path(`scripts/lumos:57307`):
- `app/../core/src/**`:合法,但 `_glob_first_match("app/src/main/A.kt", …)` 回 None,永不命中。
- `app//src/**`:同樣合法、永不命中。
- `app/src/m*in/**`:合法,Python 端當萬用字元命中 `app/src/main/A.kt`,Konsist 端依第 8 點「以斜線為界」的前綴字面比對命中 0 支。兩邊語意不同。

「讀出的條數相同」這道檢查看不出這些差異,also 沒要求 scope 至少命中一支 git 追蹤檔。拼錯的 scope 會讓 Konsist 測試一個類別都沒選到而變綠。這正是第 8 點宣稱要避免的「靜默變綠」。

### 8. 舊檔清單的行文法沒定義

severity: minor
blocking: 否

引句:「照字面整行比對,不當萬用字元」

沒說行尾空白、空行、`#` 註解行、開頭 BOM 怎麼處理。讀不懂的判準也沒給清單檔版本。

輸入:Windows 記事本存檔,清單首行帶 BOM。Python 端用 UTF-8 解碼會把 `\ufeff` 留在第一行,字典序第一支舊檔永遠比不到,靜默改成照目標審。同一份清單加一行 `# 備註` 則算「新增行」,整批不畢業。

## 逐節

- 用語、問題與最小解、驗收條款 S1~S10、回退、實務隱患、審計修正紀錄:已讀,上述以外無 finding。
- 開關表六個開關名與選項,和第 2 點旗標、第 10 點「single、all、required、full、deep、any」順序一致。
- 九支新測試數量和回退段一致;64 種組合(2⁶)成立。

## 固定席節點

`Systems/arch-alignment-lens`:不影響其既有行為。理由:
- 現行「只讀起點版」的路徑(`scripts/lumos:57364` 的 `_lens_trusted_ref`、`:57387` 的 `_trusted_decl_ref`)在畢業條件不成立時原樣保留。
- 規則原文仍讀起點版,spec 只新增一個放寬口(宣告不動、清單只刪不加),沒有改動該節點宣稱的合約。
- 但 finding 1、2 會讓這個放寬口在改名情境下實際拿不到效果。

最嚴重 severity:major;blocking 共 3 條(finding 1、2、3)。

引句已逐條用 `grep -cF` 對快照驗過,10 句都各命中 1 次(含半形標點)。
