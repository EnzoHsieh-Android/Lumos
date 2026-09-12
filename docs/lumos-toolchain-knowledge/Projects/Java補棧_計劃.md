---
type: project
status: doing
created: 2026-09-12
updated: 2026-09-12
aliases:
  - Java 補棧
  - java-idioms
  - java 效能追問
tags:
  - type/project
  - status/doing
  - scope/stack-knowledge
related:
  - "[[Projects/Python補棧_計劃]]"
  - "[[Projects/iOS與Node後端補棧_計劃]]"
  - "[[Systems/效能檢核目錄]]"
  - "[[Systems/linter精選目錄]]"
  - "[[Systems/棧別提問表態閘]]"
  - "[[Systems/arch-alignment-lens]]"
summary: |-
  FLAG:DECISION
  KEY:★立案(2026-09-12 Enzo:「再順便把 Java 接進來」)★——先派乾淨 agent 用原始問題盤點一次:Java 在八格版型裡「檔案層面認得、技術棧層面全空」,只有程式碼副檔名清單那格是滿的;★比 Python 當時多缺一格:測試綁定 profile 也沒有★(TEST_PROFILES 無 java 鍵,最接近的 kotlin-junit 只吃 .kt、正則錨 `fun`)
  KEY:補法照 Python 補棧版型,零新機制——新增 java-junit 測試 profile(JAVA_TEST_RE)、java 七題、`.java`→java-idioms、新 skill java-idioms 23 條、兩份目錄各加 Java 段、題目 id 對照加七列 [test:t_java_profile_discovery] [test:t_java_stack_wiring] [test:t_stack_question_triggers]
  KEY:★一張表同時服務兩種 Java(Enzo 2026-09-12 裁「兩邊都顧,依照情況接特有檢查」)★——通用五題(並行/資源/外呼/記憶體/集合)兩邊都吃得到;平台特有的兩題靠觸發字自己決定出不出現:改 JPA 的檔只亮 java-data、改 Android 的檔只亮 java-android [test:t_java_stack_wiring]
  KEY:★JAVA_TEST_RE 不能照抄 Kotlin 那條★——Kotlin 版用 `[^{]*?` 擋住跨方法體,但 Java 的參數化註解本身帶大括號(`@ValueSource(ints = {1, 2, 3})`),照抄會整支漏掉;改用非貪婪 `.*?`+JUnit 規定測試方法必須回傳 void 這個事實來收斂
  KEY:符號形狀 profile 刻意不新開,繼續借 kotlin(型別 PascalCase、方法 camelCase,形狀完全相同)——一旦 java-junit 存在,反查的搭檔判定就會把 `.java` 的「這個猜得很弱」旗標自動關掉;代價是 init 產出的設定會寫 `symbol_profile: kotlin`,對純 Java 專案讀起來怪但行為正確
  KEY:刻意沒做——設計審(照 iOS/Node 與 Python 兩次先例:散文 skill 走首個接入專案實跑回填,程式部分只加表格條目且有測試與翻紅驗證);本機沒裝 Maven/Gradle,骨架指令與 linter 接法都★沒有實跑核對★
  PRIOR-ART:借 Python 補棧的八格版型與既有 profile 制(零新機制);idioms 版型借 python-idioms;測試 profile 的目錄慣例借 kotlin-junit(同一套 Gradle/Maven 佈局)
  DEP:scripts/lumos(TEST_PROFILES/_SKELETON_RUN_CMD/_STACK_QUESTION_SPECS/_ARCH_IDIOM_SKILL)｜skills/java-idioms｜[[Systems/效能檢核目錄]]、[[Systems/linter精選目錄]]｜ONBOARDING.md｜skills/lumos-design-loop/templates.md
decisions:
  - content: "Java 效能追問用一張表同時服務 Android 舊碼與 JVM 後端:通用五題常駐,平台特有兩題靠觸發字條件出現"
    context: "題目 id 被 t_stack_question_triggers 釘住,換 id 會讓在途分支重新表態,所以方向一開始就要選對(Python 補棧 d1 的同一個教訓)。Java 在這台機器上的兩種用途差很遠:Android 舊碼(跟 Kotlin 混編)與 Spring/JPA 後端。問 Enzo,他裁「兩邊都顧,依照情況接特有檢查」。"
    alternatives_considered:
      - "只收後端題(Spring/JPA/連線池):對後端最載重,但 Android 舊碼大半題用不上,而這台機器上的 Java 大多是 Android 舊碼"
      - "只收 Android 題(Context 洩漏、主執行緒 IO、AsyncTask):跟現有 Kotlin 題組互補,但後端專案幾乎一題都不亮"
      - "兩邊都收成一張大表、全部常駐:覆蓋最廣,但每改一支 Java 檔都亮十題,表態成本高到讓人亂答"
    why_chosen: "觸發字機制本來就是條件式的——題目只在改動行出現對應詞彙時才適用,所以『兩邊都顧』不需要新機制:通用五題(並行、資源關閉、外呼、記憶體、集合)對兩種 Java 都成立,平台特有的 java-data(JPA/交易)與 java-android(生命週期)各自綁自己那組詞。實測:改 findAll 的檔只亮 java-data,改 findViewById 的檔只亮 java-android。"
    trade_offs: "同時帶 JPA 與 Android 的檔(少見但可能,例如 Android 上用 Room 的舊碼)會兩題都亮,多答一題;七題比其他棧多(kt=7、cs=5、node=5、py=5),觸發面寬一點。真正的代價在第一個消費端出現前都只是推測。"
    decided: 2026-09-12
    valid: true
plan_refs: []
---
# Java 補棧（2026-09-12）

> 白話：Enzo 說「再順便把 Java 接進來」。lumos 大部分功能不看語言，綁語言的只有「工具對這個技術棧知道什麼」那一類。Java 的狀況比 Python 當時更空——**連「怎麼認出你的測試」都沒有**，而那一格空著的後果是合約綁不上任何測試，閘會靜默放行。這篇把八格補齊。**全部只在合成樣本上測過，第一個真的用到的專案還沒出現。**

## 盤點：Java 在八格裡的狀態

開工前先派一個乾淨 agent，用原始問題（「這套工具對 Java 專案的支援到什麼程度」）去查一次，不給它我的結論。它的答案跟我自己查的一致，而且多抓到兩格。

| 格子 | 補之前 | 這次 |
|---|---|---|
| 程式碼副檔名清單 | ✅ 已收 `.java` | 不動 |
| 符號形狀 profile | ⚠️ 借 kotlin，而且被標記「猜得很弱」 | 不新開，靠補上測試 profile 讓弱旗標自動關掉 |
| **測試綁定 profile** | ❌ **完全沒有** | 新增 `java-junit`＋`JAVA_TEST_RE` |
| 骨架測試指令 | ❌ | 加一條 Gradle 形（Maven 專案自己換） |
| 效能追問題組 | ❌ | 加 `java` 七題 |
| 副檔名→慣例 skill | ❌ | `.java` → `java-idioms` |
| 慣例 skill | ❌ | 新增 `java-idioms` 23 條 |
| linter 目錄 | ❌ | 加 Java 段（Error Prone／SpotBugs／PMD／NullAway） |
| 效能檢核目錄 | ❌ | 加 Java 段＋題目 id 對照七列 |

**為什麼「測試綁定 profile」是最嚴重的那一格**：合約標記（`★INVARIANT★`）要靠 `[test:測試名]` 綁回真的測試方法，而綁定要先掃得到測試。掃不到的後果不是報錯，是**閘靜默放行**——看起來一切正常，實際上沒有任何東西在守。健檢原本就會唸這句（「掃不到你的測試，合約綁不上任何東西」），但唸完也沒有 Java 專案能填得出 profile 名，因為根本沒有。

## 七題怎麼選的

Enzo 裁「兩邊都顧，依照情況接特有檢查」。作法不需要新機制——題目本來就只在改動行出現對應詞彙時才適用：

- **通用五題（兩種 Java 都吃得到）**
  - `java-concurrency`：互不依賴的等待有沒有一起飛；執行緒池無界（`newCachedThreadPool`）或大小沒算過；`get()`／`join()` 沒帶逾時。
  - `java-resources`：`Connection`／`ResultSet`／`Files.lines` 有沒有 try-with-resources。漏關一條就少一個連線池名額，症狀很晚才出現而且長得像別的病。
  - `java-external`：連線逾時與讀取逾時是兩件事，只設一個等於沒設；不可逆操作重送要有冪等鍵。
  - `java-memory`：整包讀進記憶體、`static` 集合當無上限快取、`ThreadLocal` 用完沒 remove（執行緒池會重用執行緒）。
  - `java-collections`：迴圈裡相接字串、`List.contains` 當成員查找、自動裝箱、Stream 重複遍歷。
- **平台特有兩題（靠觸發字條件出現）**
  - `java-data`（後端）：JPA N+1、LAZY 在迴圈裡才載入、`findAll` 無分頁、`@Transactional` 被同類自呼叫（代理不生效，**而且不會有任何錯誤訊息**）、交易裡夾外呼。
  - `java-android`：`Context`／`Activity` 被長活物件握著、主執行緒做磁碟網路、回呼沒跟生命週期綁、`findViewById` 在列表繫結裡反覆呼叫。

觸發字照既有家規「範式詞＋反面詞」：範式詞是那塊地的詞彙（`CompletableFuture`、`@Transactional`、`RecyclerView`），反面詞是同一個顧慮用舊法寫會出現的字（`new Thread(`、`AsyncTask`、`executeQuery(`），讓「用舊寫法寫同一件事」也會亮同一題。

## 測試方法正則為什麼不能照抄 Kotlin 那條

Kotlin 版是「註解 → 中間不跨 `{` → `fun` 方法名」，用 `[^{]*?` 擋住「跨過方法體抓到下一個方法」。Java 照抄會壞，因為**Java 的參數化註解自己就帶大括號**：

```java
@ParameterizedTest
@ValueSource(ints = {1, 2, 3})
void handlesQuantities(int n) { }
```

`[^{]*?` 在 `{1, 2, 3}` 就斷了，這支測試整個漏掉。Java 版改用非貪婪 `.*?`，靠另一個事實收斂：**JUnit 規定測試方法必須回傳 void**，所以「註解之後最近的一個 void 方法名」就是它本人。

代價寫在正則旁邊：萬一有人把 `@Test` 標在非 void 方法上（JUnit 會拒跑那支測試），這條會抓到下一個 void 方法的名字。

## 驗證

- 新測試 `t_java_profile_discovery`：JUnit5 的 `@Test void`、參數化帶大括號、JUnit4 的 `@Test public void` 三種都認得；沒標註的 void 方法不收；註解裡的假測試剝掉；profile 只吃 `.java` 不搶 `.kt`；`init` 猜得到 `java-junit` 且「猜得很弱」旗標關掉。
- 新測試 `t_java_stack_wiring`：七題、`.java`→`java-idioms`、架構對齊會派這份 skill、後端改動只亮 `java-data`、Android 改動只亮 `java-android`、純測試檔不附題、skill 資料夾真的存在。
- 既有 `t_stack_question_triggers`：id 集合加七個 java id、加 java 的命中／不命中樣本。
- **翻紅驗證（2026-09-12 實跑）**：拿掉 `.java→java-idioms` → 2 條翻紅；拿掉 java 七題 → 接線測試 4 條、id 集合測試 2 條翻紅；正則換回 Kotlin 寫法 → 參數化那條翻紅；把 `java-idioms` 資料夾搬走 → 存在性那條翻紅。還原後全綠。
- 一個測試樣本踩到既有設計要記下來：**同一支檔改寫時，被刪掉的那行也算改動行**（「純刪除也要觸發」是刻意的），所以驗「平台特有題各自獨立」的樣本必須分成兩支檔，不然上一版的 `findAll` 會讓 `java-data` 跟著亮。

## 誠實邊界與回頭條件

- **零真專案**：七題的觸發字、skill 的 23 條、linter 接法全部只在合成樣本與官方文件上成立。
- **本機沒有 Java 建置工具**：`javac` 有（JetBrains 附的 JDK 17），但 Maven／Gradle／Error Prone／SpotBugs／PMD 一個都沒裝，所以骨架測試指令與 linter 目錄那段的接法**沒有實跑核對過**，只保證形狀對。對照組：Python 補棧的 28 條 ruff 代號是用本機 `ruff rule` 逐條查過的，這次做不到同一個標準。
- REVISIT:2026-10-12 若仍無 Java 消費端：把「未實跑」這件事在 skill 與兩份目錄再標一次，別讓它靜靜變成看起來可信的文件。
- 第一個接入的 Java 專案跑完一輪真的代碼審後要回來看：哪題從來沒亮過、哪題每次都答「不適用」（死題候選）、哪些坑 skill 沒收、哪些 linter 規則預設沒開或誤報多到要關。
