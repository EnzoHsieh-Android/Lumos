severity: major

## 一、分層與依賴方向

**大致對齊,一處不對齊(併入第三題細節,這裡先點名)。**

- `_excluded_line(line)` 的去前綴規則已把上一輪(本席 r3)的 major 折入:凍結稿第 134 行改成「去前綴借既有條款行解析器同一個前綴正則(`_CLAUSE_LEAD_RE` 那組字元集:空白、`-`/`*`/`+`/`•`/數字與 `)`/`.`/`、`、引用符 `>` 含多層」,對照 `scripts/lumos:4589` 的 `_CLAUSE_LEAD_RE` 字元集 `[\s>*#\-\d.、|+•—·)]`——字元集吻合,判定與證明共用同一支解析的寫法維持,查證屬實。
- 合約行掃描維持借 `cmd_contracts`/`IRREVERSIBLE_RE`/`CHECKPOINT_RE`(`scripts/lumos:3859-3860`),留痕維持走 `cmd_canary` 單一寫入口、`kind` 擴充列舉(`scripts/lumos:27943` 的 `cr.add_argument("kind", ...)`),推送閘範圍限定沿用 `_plans_in_range`——都跟上一輪核過的一樣,沒有退步。
- **`_section_lines(text, 標題)` 沒有借用既有同用途的節範圍抽取邏輯,是本層新開的第三套**:本檔既有 `_FOLD_AUDIT_RECORD_RE`(`scripts/lumos:22510-22511`,`^##\s+(§\d+\s+)?審計修正紀錄.*`)配 `_FOLD_NEXT_H2_RE`(`scripts/lumos:22518`,`^##\s`)在 `_fold_value_drift`(`scripts/lumos:22521` 起)裡就是「從一個容許數字前綴的二級標題,抽到下一個 `##` 標題為止」的節範圍抽取,而且緊挨著 `_fold_mirror_sections` 用的 `_FOLD_MIRROR_HEADING_RE`(`scripts/lumos:21676`,同款 `(§\d+\s+)?` 前綴容忍)。另外 `cmd_pitfalls --check`(`scripts/lumos:21552`)還有第二種、更鬆的「找『實務隱患』節存不存在」正則:`re.search(r"(?m)^##\s+.*" + re.escape(section_title), text)`。凍結稿的 `_section_lines` 是第三套「找 `## 實務隱患` 節」的實作,規則又跟前兩套都不同(去序號前綴+去括號後綴+起點必須是「實務隱患」開頭+到下一個 `##`/`#` 為止+三級標題算節內)——PRIOR-ART 明講「借用不自建」,但這裡沒有借用同檔案裡兩套既有的「節範圍/節存在」判斷,也沒有把三套收斂成一支共用函式。見第三題詳述。

severity: major

引句:「同名節有多個就全部算;fence 內的行照 `_visible_lines` 規則不算(共用函式 `_section_lines(text, 標題)`,S29 綁測試)」

## 二、命名與錯誤處理

**大致對齊,一處低信度疑點。**

- `--finding-severity` 與既有 `--finding-kind` 同形:`scripts/lumos:27943-27945` 兩個旗標並排定義,錯誤訊息都是「要寫成 id=value」+「值只能是…」+「鍵要在發現集合裡」三段同款,凍結稿沒有另開一套。`precision: finding/round` 兩值在 `scripts/lumos:6203-6208` 已是落地程式,不是紙上設計。
- `push-gate-unreviewed`(連字號)已落地一致(`scripts/lumos:7559`),沒有冒號複合詞殘留。
- N≥2 擋下訊息:凍結稿寫「篩選匹配到 N 支,測試名要唯一,換更長的名字」(第 176 行)。核對白話三段式(發生什麼→為何在意→指令獨立一行):「篩選匹配到 N 支」是發生什麼,「測試名要唯一」點了為何在意但沒把「怎麼改」跟前面用指令的形式分行——跟 N==0 那句「擋下並印原因」、`_ran_evidence_check` 的 `fix_hint`(如「把 -quiet 拿掉」,`scripts/lumos:25699`)比,後者是具體操作句,凍結稿這句「換更長的名字」偏泛稱,沒有給「往 `run_cmd` 加什麼」的具體形狀。**這條算風格偏弱、夠不上「第二種做法」,不列 finding**(判準:純風格不列)。
- **`_DOOR_RULE_VERSION`(整數,第 179 行)跟鄰居的版本常數命名不同族**:既有同類「規則改版、失效重算」常數用 `_SCHEMA` 尾碼——`_LENS_SCHEMA = 2`(`scripts/lumos:24359`)、`_FILTER_PROBE_SCHEMA = "v2"`(`scripts/lumos:25677`,同一份「規則改版就換這個字串,舊快取自然 miss」注解語意跟凍結稿寫 `_DOOR_RULE_VERSION`「改到…任一支就 bump」幾乎同一件事)。凍結稿命名成 `_VERSION` 不是 `_SCHEMA`。**⚠低信度**:凍結稿留痕欄位本身就叫 `door_rule`(不是 `door_rule_schema`),常數跟著欄位名走也說得通,`anchor-baseline.json:2` 的頂層鍵也直接叫 `"version"`——不足以判定這是「第二套命名系統」,只夠上 minor,且不確定是否該折。

引句:「改到 `PITFALL_CLASSES`、合約行掃描、已排除規則任一支就 bump,代碼審看」

severity: minor

## 三、第二種做法

**一條 major:支數解析與 `_section_lines` 都是「同一件事在同檔案裡的第 N 套」。**

1. **支數解析沒有收進既有輸出解析 profile 表,是繞開既有紀律另開一條路。** 凍結稿自己已經訂正 PRIOR-ART(第 176 行):r2 說「借 `bound-tests-gate`」是錯的,`_ran_evidence_check`(`scripts/lumos:25726-25738`)只認「有沒有出現『N passed』」、不解析支數,所以「不是借來的」——這句本身查證屬實(讀了 `scripts/lumos:25726-25738` 確認)。但這不代表新判準可以不進既有結構:`_RAN_EVIDENCE`(`scripts/lumos:25695-25716`)是一張**逐棧、逐支經過本機實測驗證**的輸出樣式表(swift-xctest/csharp-xunit/node-jest/python 各一條、附 `measured`/`fix_hint`),旁邊 `_bound_tests_filter_probe` 的大段註解(`scripts/lumos:25754-25760`)明講「這裡不學 lint-check 拆成要旗標才觸發,是因為判準是編排者自己重想的,不是照席位的藥吃」——本檔對「輸出解析新判準要不要收進同一張驗證紀律的表」是有明確前例態度的。凍結稿的支數解析只寫死兩種格式(unittest 的 `Ran N test(s)`、pytest 的 `N failed / N passed`),既不掛進 `_RAN_EVIDENCE` 的逐棧實測紀律,也沒交代 swift-xctest/csharp-xunit/node-jest 這三棧在支數解析(N==1/N==0/N≥2)下走哪條路——**這是同一個問題(「這段測試輸出證明了什麼」)在同一份程式碼裡的第二套判準結構,跟旁邊那套刻意不同源。**
2. **`_section_lines` 是「找 `## 實務隱患` 節」的第三套實作**(細節見第一題):`_FOLD_AUDIT_RECORD_RE`+`_FOLD_NEXT_H2_RE`(節範圍抽取)、`cmd_pitfalls --check` 的鬆散存在性正則(`scripts/lumos:21552`)、與凍結稿新提的 `_section_lines`,三套規則互不相同又各自成立,凍結稿沒有選擇擴充既有兩套之一。

引句:「解析測試工具輸出裡的支數(unittest 的 `Ran N test(s)`、pytest 的 `N failed / N passed` 相加)」

file: `scripts/lumos:25695-25716`(`_RAN_EVIDENCE` 逐棧實測表)、`scripts/lumos:25754-25760`(判準要不要收進同一張表的既有討論)、`scripts/lumos:22510-22518`(`_FOLD_AUDIT_RECORD_RE`/`_FOLD_NEXT_H2_RE` 節範圍抽取先例)、`scripts/lumos:21552`(`cmd_pitfalls --check` 第二種節存在性正則)

severity: major

**另一條 minor:條款區塊指紋的正規化算法沒有指名沿用哪一支。** 凍結稿第 179 行只寫「全部 `[S]` 定義行正規化後串起來的 sha256」,沒說「正規化」指的是本檔僅有的行內可見規則 `_strip_inline_markup`(`scripts/lumos:167`)還是 `normalize_report_text`/`_report_normalize_issues`(`scripts/lumos:5454-5553`)那套嚴重度格式正規化——後者的用途(統一 `severity:` 寫法)跟條款指紋(要對「文字有沒有實質變動」保持穩定,同時要抗 `updated:` 之類跟條款無關的維護)不是同一件事,不適合借;但也沒指名前者。**是規格留白不是引入第二套**,寫不出算法無從判斷是否跟既有分岔,先留紀錄。

引句:「條款區塊的指紋(全部 `[S]` 定義行正規化後串起來的 sha256,不是整檔」

severity: minor

## 四、落點

**對齊。** `Systems/design-loop` 與 `Systems/規格閘` 兩篇的分工延續 r3 已核過的判斷:`scripts/hooks/pre-push`、`scripts/lumos` 多家已是既有常態(`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md` 自己承認落點靠 `lands_in`),凍結稿正文只指回 frontmatter 一處(第 235 行「落點見開頭欄位 `lands_in`」),沒有重複兩種格式。已落地改動(`_ci_step_is_test`、`--finding-severity`、`precision` 欄位)現在確實都在 `scripts/lumos` 程式碼裡跑著,說明文字目前只在「進度」段落與「要動什麼」表格裡交代,`Systems/design-loop`(`docs/lumos-toolchain-knowledge/Systems/design-loop.md`)掛 0 份計劃、`Systems/規格閘` 還不存在——這兩篇落地時要把「已落地改動」寫回哪一篇,凍結稿第 235 行已明確分工(`Systems/規格閘` 管 `cmd_spec_gate`、`_clause_check`、`_excluded_line` 與 pre-push 新段落),`Systems/design-loop` 管處置閘第五步契約行,兩篇夠用,沒有第三種記法。

---

不對齊共 3 條,其中 major 1 條(支數解析與 `_section_lines` 均為既有機制的第二/第三套判準結構,算同一類問題合記 1 條 major)、minor 2 條(`_DOOR_RULE_VERSION` 命名族系⚠低信度、條款指紋正規化算法留白未指名沿用哪支)。
