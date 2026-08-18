---
type: project
status: doing
created: 2026-08-18
updated: 2026-08-18
tags:
  - type/project
  - status/doing
  - scope/graph-governance
aliases:
  - 派工編制資料化
  - loop roster
---
# 派工編制資料化_計劃

> 白話:每輪對抗審計「該派哪些席」——幾席、什麼鏡頭、哪席要外家、對答案席什麼條件開——目前全住在 skill 散文裡,只有「實際派了誰」有落資料(rN-dispatch*.json)。散文載規則會漂(已兩次自相矛盾),而「應派 vs 實派」全專案零機械對帳。本案把編制宣告成資料:`loop next` 吐應派清單、`loop status --roster` 對帳實派,v1 恆觀測不進閘。

## 緣起(2026-08-18;源自 2026-08-17 graph engineering 靈感掃描第二條)

外界主張「拓撲——誰存在、誰負責什麼——應該是可版控的產物,不是自然長出來的意外」(truefoundry graph engineering enterprise guide)。對照本專案:tier→(席數,cap) 已是 code 資料(`_TIER_PARAMS`),但**席的組成**只在 `lumos-design-loop`/`lumos-code-loop` SKILL.md 散文。

PRIOR-ART: ① 最小解層級——不造新機制:宣告側=`_TIER_PARAMS` 旁加編制表(同型資料常數);吐出側=既有 `loop next`(本來就吐唯一下一動作,加 roster 欄);對帳側=既有 `loop status` 加 opt-in 觀測段(同 seat-check「觀測恆 rc0」慣例)。② 世界解過沒——有:GitHub CODEOWNERS/required reviewers=「應有審查者」宣告成版控資料;OPA/policy-as-code=規則從散文降資料;graph engineering 2026 主張同型。③ 裁定=**borrow-design**(借「編制=版控資料+機械對帳」概念,零依賴自寫;adopt 排除:零依賴家規)。

## 新機制準入三問(Growth test)

1. **真事故?** 三筆:①席次/收斂規則在 skill 散文自相矛盾兩次(code-loop SKILL「standard(K=2)」講反、「連 2 輪」與 panel 節「一乾淨輪」矛盾),均 2026-08-03 才修——散文載規則實證會漂。②2026-08-04 終審 spec 席留痕漏落,事後補(design-loop SKILL 留痕慣例段明記「補漏 2026-08-04 終審 spec 席」)。③外家席換代偏離(Codex 到期退 Gemini、一席兼 finder+否決兩角)純靠自律留痕,工具無感知(memory retrieval-v1-and-codex:「獨立性折損要留痕」)。
2. **風格偏好?** 否——漏派一席=收斂宣稱建立在比宣告少的覆蓋上,是收斂正確性問題非美感。
3. **既有小修蓋得住?** 蓋得住,本案即是小修:兩個既有指令各加一段,一個資料常數,零新子命令、零新留痕格式(消費既有 rN-dispatch*.json)。

## 設計

### S1 編制宣告表 `_TIER_ROSTER`(scripts/lumos,`_TIER_PARAMS` 旁)

以 (loop_kind, tier) 為鍵;loop_kind 由 loop id 前綴判(**`code-` 含連字號**開頭=code,其餘=design——skill 慣例「loop id = code-<topic>」;★已知限制:歷史帳有 `code側刪除傳播守衛`/`codestage` 兩筆不合慣例 id 會被推定為 design,advisory 誤喊可忽略,觀測輸出印「kind=依前綴推定」自曝推定性★)。每個條目帶 `mode`(`panel` | `sequential` | `single`)與席清單;每席 `{slot, family, occupies_w, requirement}`:

- `family`:`claude` | `external`(外家=非 Claude 家族)。
- `occupies_w`:是否佔 panel 寬度 W(否決席/對答案席不佔)。
- `requirement`:`required`(缺=喊 missing)| `required-fail-closed`(缺=喊 missing+提示 fail-closed 紀律)| `note-if-absent`(缺=喊「單家族,收斂宣稱要講小」——design-loop 外家能力宣告制原語意)| `conditional:<條件>`(如 spec-conformance 席=有收斂 spec 才應派;條件真值工具不可判,只印條件供編排者對)。

預設表逐字對齊現行 skill 散文(數字單源=散文現值,落地時逐條抄):

| kind/tier | 佔 W 席 | 不佔 W 席 |
|---|---|---|
| design/light(single) | 通才×1(claude,required) | — |
| design/standard(panel) | 鏡頭席×3(claude,required;r1 其中一席通才) | 外家否決×1(external,note-if-absent) |
| design/high(panel) | 鏡頭席×5(claude,required) | 外家否決×1(external,note-if-absent) |
| code/standard(sequential) | 單 reviewer×1(claude,required) | 外家否決×1(external,note-if-absent:standard 退同門+留痕) |
| code/high(panel) | 鏡頭席×4(claude,required)+外家 finder×1(external,required-fail-closed) | 外家否決×1(external,required-fail-closed)、spec-conformance×1(claude,conditional:有收斂 spec) |

- **防雙真相**:`mode=panel` 的條目(design/standard、design/high、code/high),occupies_w 席數必須等於 `_TIER_PARAMS` 的 width;`mode=single/sequential` 條目(design/light、code/standard)佔 W 席數必須=1——**`_TIER_PARAMS` 的 width 只約束 panel 模式**(pre-flight 抓到的結構事實:code/standard 走單 reviewer 循序,不吃 width=3)。兩型皆測試釘住,漂了翻紅。
- 鏡頭(lens)值域**不進表**:seat-check 已裁定 lens 為觀測欄位、抽象詞無機械 oracle;編制只管「幾席/哪家族/佔不佔 W」這些可機械比對的維度。
- v1 **無 per-repo 覆寫**:編制是 skill 紀律的鏡像,跨 repo 同一份;覆寫需求出現再立案(YAGNI)。

### S2 `loop next` 吐應派清單

- JSON 輸出加 `roster` 欄:該 (kind,tier) 的席清單(slot/family/occupies_w/requirement 原樣)。
- 人讀輸出加「應派」數行。
- kind 判定用 loop id 前綴;`legacy` tier(推導值)沿 `_TIER_PARAMS` 慣例給單席通才(不喊 missing——舊帳無編制概念)。

### S3 `loop status --roster` 實派對帳(opt-in 觀測)

- 帶 `--roster` 且帶 `--repo` 時啟用;逐輪掃 `governance/review-reports/<loop-id>/rN-dispatch*.json`(檔名慣例既有)。**dispatch 檔解析須容納既有帳的三種真實形狀**(pre-flight 實查):①dict 頂層帶 `auditor`(每席一檔,多數)②dict 帶 `seats` 陣列(單檔多席,逐元素取 auditor)③頂層直接是 list(逐元素取 auditor)。取不到 auditor 的元素計 unknown,壞損 JSON 印警告跳過該檔(fail-open)。對編制宣告吐觀測:
  - `seat_shortfall`:實派席數 < 應派 required 席數。
  - `external_missing`:應派 external 席在實派 auditor 中零命中——auditor 字串**先 lower() 再**按家族關鍵字表子串比對(`codex`/`gemini`/`qwen`/`gpt`→external;`sonnet`/`opus`/`haiku`/`claude`→claude;無命中=unknown,列出不判定;大小寫不敏感是硬規格——真實帳已有 `slot5-Codex跨家族` 大寫樣本)。requirement=note-if-absent 時措辭為「單家族,收斂宣稱要講小」;required-fail-closed 時為「缺外家+fail-closed 紀律未滿足」。
  - `conditional` 席:只印「條件:<條件>——應派與否編排者自對」。
  - 該輪無任何 dispatch 檔:印「無派工快照可對帳(舊帳/未落)」,不判 shortfall(fail-open,同 seat-check 歷史母體 vacuous 慣例)。
- **恆不影響 rc**:觀測段只印字,gate 判定與 exit code 完全不動(v1 advisory;進閘另立案,須再過 design-loop)。
- 不帶 `--roster` 時輸出零變化(既有消費者/測試零擾動)。

### 範圍刀(明確不做)

- **不動收斂閘**:`--disposal`/`--gate`/`--panel` 判定式一字不改。
- **不驗 lens 語意**、不驗 materials(seat-check 責任田)、不驗辯方(辯方 per-finding 非 per-round,無派工快照可對)。
- **不做 per-repo 編制覆寫**、不做編制的 CLI 寫入指令(表=code 常數,改編制=改 code=走 code-loop,天然有審)。
- **不刪 skill 散文**:SKILL.md 席次段落地時加一句「編制數字單源=`loop next` 吐的 roster;本段為解說」——散文降解說,規則權威移資料。

## 測試策略(TDD,先紅後綠)

1. `t_tier_roster_table`:表存在;各 (kind,tier) occupies_w 席數==`_TIER_PARAMS` width(防雙真相釘)。
2. `t_loop_next_roster`:design/standard 與 code/high 的 `loop next --json` 含 roster 欄且席組成正確;**人讀輸出含「應派」行**;legacy 推導不炸。
3. `t_roster_family_classify`:auditor 字串→家族分類(gemini→external、bug-sonnet→claude、未知→unknown)。
4. `t_loop_status_roster_check`:fixture 造 dispatch 檔——外家缺→external_missing 喊;席數短→seat_shortfall 喊;無 dispatch 輪→vacuous 措辭;**conditional 席印「條件:…」行**;三種 dispatch 形狀(頂層 dict/seats 陣列/頂層 list)各一案解析正確;**rc 與不帶 --roster 時完全一致**(advisory 釘);不帶 --roster 輸出零 diff。

## 實務隱患

- **通用三問**:併發——純唯讀(glob+讀 JSON),無寫入無鎖,兩請求同時跑各印各的,無共享狀態。效能——每輪 dispatch 檔個位數、loop 帳千行級,冷路徑(人工收斂時才跑)。資源——讀檔全走 with-open 即開即關,無連線無鎖持有。
- **風險類自答**:本案碰**守衛面**(審查機制周邊)——但 v1 純觀測、不動任何 gate 判定式,爆炸半徑=多印幾行字;誤報最壞後果=編排者多看一眼。已排除:金流(無)、對外送出(無)、prod 不可逆(無——資料表+唯讀觀測,git revert 即回)。
- **編制表與散文漂移**:表落地後散文仍在,兩邊可能再漂——防線=散文段標「單源=roster」+防雙真相測試只釘 width;鏡頭語意漂移無機械守(誠實記入天花板)。
- **auditor 字串分類誤判**:席名慣例 `<鏡頭>-<模型>` 是慣例非強制,野字串→unknown 列出不判定(不誤喊 external_missing 的前提=分類 fail-open)。
- **dispatch 檔名慣例依賴**:對帳靠 `rN-dispatch*.json` glob;慣例改名=觀測靜默失效——測試釘 glob 樣式,skill 慣例段互指。

## 合約候選(收斂時複核,候選≠已標)

- 「`--roster` 觀測恆不影響 loop status rc」——v1 行為邊界,若進閘另案時此條 supersede。

## 審計修正紀錄

- **pre-flight(2026-08-18,機械排乾,不算 loop findings)**:6 命中全修——①家族分類補大小寫不敏感規格(真帳有大寫樣本)②code/standard(1 席)與 _TIER_PARAMS width=3 結構衝突→roster 加 mode 欄,width 自檢只約束 panel 模式③kind 前綴規則對兩筆歷史非慣例 id 誤判→明文已知限制+輸出自曝推定性④dispatch 檔三種真實形狀→解析規格補齊⑤⑥測試策略補人讀輸出與 conditional 席案。
