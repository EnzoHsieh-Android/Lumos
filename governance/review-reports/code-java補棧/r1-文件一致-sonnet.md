severity: major

# 文件與圖譜跟程式對不對得上——審查報告(Java 補棧)

鏡頭:文件/圖譜是否與程式實際行為一致、文件自己是否前後矛盾或過度宣稱。
被審材料:`governance/review-reports/code-java補棧/r1-slice-graph.patch`、`r1-slice-skills.patch`。
程式 ground truth 一律用 `importlib.machinery.SourceFileLoader("lum","scripts/lumos").load_module()` 現場讀,或直接 `git show`/跑 `scripts/test_lumos.py` 驗證,不採信文件自己的宣稱。

## 總覽(先講人話)

這批 diff 是「補 Java 技術棧支援」——讓 lumos 認得 Java 的測試、該問的效能問題、寫碼慣例。我把文件寫的每一句能查的都去程式或 git 歷史對過一次。**大部分寫得很準**(七題的觸發字、profile 數量、正則設計理由,逐字比對甚至連空格都對得上,還原成壞版本重驗也翻紅),但抓到兩個真的問題:

1. **新文件自己講的「歷史上漏了幾次」數字,跟它自己下面那張表打架**(major)。
2. **新的 Java 慣例 skill 裡引用了一個不存在的 Error Prone 檢查名稱**,看起來像編出來的,而這份文件才剛承諾「工具名有查過官方頁面」(major)。

以下逐項對照使用者交辦的 6 點。

---

## 逐項查證

### 1. 兩份 README 的「支援的語言」表格

**先講一個材料範圍的問題**:這兩份被審 patch(`r1-slice-graph.patch`、`r1-slice-skills.patch`)裡**完全沒有 `README.md`/`README.en.md` 的 diff**——我用 `grep -n '^diff --git' <patch>` 逐一列出兩份 patch 改到的每一支檔,裡面沒有任何一行是 README。這兩份表格實際落在 commit `ed118929`(在 `LUMOS-IMPACT` 範圍內,但顯然被切進了別的席位的 slice,不在我這兩份材料裡)。

因為使用者明確要我查證這件事,我依規則把它當「查程式/repo 的 ground truth」而非「讀別席報告」處理:直接 `git show HEAD:README.md` / `git show HEAD:README.en.md` 讀現存內容,拿去對 `scripts/lumos` 的 `_STACK_QUESTION_SPECS`、`TEST_PROFILES`、`_ARCH_IDIOM_SKILL`。結果:**九列全部對得上**,包括 Java 那列(測試掃描 ✅、效能追問 ✅ 7 題、慣例 skill ✅、linter 推薦 ⚠️ 未實跑、真專案用過 ❌)與其餘八個語言/平台。沒有查到任何一格「標✅其實沒有」的情形。

這**不算我這份材料裡的缺陷**(因為兩份 patch 根本沒有這段文字可引用),只是提醒:這題的答案要看第三份 slice(程式/README 那份),不在我收到的材料範圍。

### 2. `Systems/效能檢核目錄` 的 Java 段與題目 id 對照七列

逐字比對 `_STACK_QUESTION_SPECS["java"]` 的 `when`(觸發字)與文件裡的七列(`java-concurrency`/`java-resources`/`java-data`/`java-external`/`java-memory`/`java-collections`/`java-android`)。

驗法:
```
python3 - <<'EOF'
import importlib.machinery
lum = importlib.machinery.SourceFileLoader("lum", "scripts/lumos").load_module()
for spec in lum._STACK_QUESTION_SPECS["java"]:
    print(spec["id"], spec["when"], spec.get("when_raw"))
EOF
```
七組 `when` 清單(含順序、跳脫字元 `\b`/`\.` 等)跟 `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md` 表格裡的反引號清單**逐字相同**(markdown 表格用 `\|` 逃逸管線符號,還原後也對得上),`java-data` 的 `when_raw`(SQL 字串樣式)也一致。題數 7 也對。**沒有發現任何一個觸發字寫錯、漏寫或多寫**。這條是 clean。

### 3. `Systems/test-profile-multiplatform` 的「profile 名截至 2026-09-12 共 10 個鍵」

```
python3 - <<'EOF'
import importlib.machinery
lum = importlib.machinery.SourceFileLoader("lum", "scripts/lumos").load_module()
print(len(lum.TEST_PROFILES), sorted(lum.TEST_PROFILES))
print(lum.TEST_PROFILES['node-jest'] is lum.TEST_PROFILES['node-vitest'])
EOF
```
輸出:`10 ['csharp-xunit','dart','java-junit','kotlin-junit','maestro','node-jest','node-vitest','playwright','python','swift-xctest']`,且 `node-vitest is node-jest` → True。跟文件寫的「csharp-xunit/kotlin-junit/java-junit/maestro/playwright/dart/python/swift-xctest/node-jest/node-vitest,其中 node-vitest 是 node-jest 的別名」**數字與名單完全一致**。這條也是 clean。

### 4. `Systems/補新語言SOP` 新文件——內部矛盾(本次最大的發現)

severity: major
**
**blocking: 是**
**引句:「漏了兩次、test-profile-multiplatform」**

`docs/lumos-toolchain-knowledge/Systems/補新語言SOP.md` 的 summary KEY 行寫:「三次補棧裡,效能檢核目錄那串『全表各棧題數』漏了兩次、test-profile-multiplatform 那串『profile 共幾個』漏了三次」(見 `governance/review-reports/code-java補棧/r1-slice-graph.patch:1292`)。

但這篇**自己下面第 9 步的表格**寫的是:

**引句:「讀的人以為沒有這個棧 | 2026-09-11 漏、09-12 補回」**(`r1-slice-graph.patch:1380`,效能檢核目錄那一列——只講了**一次**漏,不是兩次)

**引句:「同上 | 09-08、09-11 都漏，09-12 補回」**(`r1-slice-graph.patch:1381`,test-profile-multiplatform 那一列——講的是**兩次**漏,不是三次)

我用 git 歷史逐一核對,證實表格才是對的、summary 的「兩次/三次」是誇大:

```
# 效能檢核目錄「全表各棧題數」這串字,只在 09-11(Python 進場)漏過一次,09-12(Java)補回
git log -p --follow -- docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md | grep -n "全表 kt=7"
# → 09-08(iOS/Node)那個時間點這行字根本還沒出現(尚未有這個機制),
#   09-11 才第一次漏(仍寫 swift=6/node=5,沒有 py=5),09-12(commit ed118929)一次補齊 py=5+java=7

# test-profile-multiplatform「profile 共幾個」這串字,在 09-08、09-11 兩次都漏、09-12 才補
git show 18e732ff -- docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md | grep "共 6 個"
# → 18e732ff(09-08 iOS/Node 補棧,同一個 commit 新增了 swift-xctest/node-jest 兩個 profile)沒有動這行,仍是「共 6 個」
git show 631d7e3bc93f6f0ce76eb5a25fbaa6360c50a2f9:docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md | grep "共 6 個"
# → 到本次審查基準線(09-11 之後)仍是「共 6 個」,證明 09-11 也漏了
git show ed118929 -- docs/lumos-toolchain-knowledge/Systems/test-profile-multiplatform.md | grep "共 10 個"
# → 09-12(Java)才一次補到「共 10 個」
```

也就是說:**效能檢核目錄那串只漏過 1 次(09-11),不是 2 次;test-profile-multiplatform 那串漏過 2 次(09-08、09-11),不是 3 次**。而且這兩個正確數字(1 次、2 次)恰好就寫在同一篇文件自己的表格裡,以及 `test-profile-multiplatform.md` 自己改動後新增的行內註記裡(`r1-slice-graph.patch:22` 一行寫的正是「2026-09-08 加 swift/node、2026-09-11 加 python 時都漏了」——兩次,不是三次)。summary KEY 行的「兩次/三次」跟同一份文件的另外兩個地方(表格、來源檔案自己的行內註記)都對不上,也跟 git 歷史對不上。

這篇文件存在的理由就是「這件事每次都會漏,所以要有 SOP 逼人照著走」——開頭的統計數字如果是錯的(而且錯的方向是誇大),會讓下一個讀者高估這個散落清單有多不可靠、或誤信「已經漏過三次」這種不存在的歷史事故,判斷力會被帶偏。這是文件寫錯事實,算 major;且會誤導後續維護者的判斷,算 blocking。

### 5. `skills/java-idioms/SKILL.md` 的 23 條

我把機檢欄(`EP:`/`SB:`/`PMD:`/`NullAway`)裡點名的檢查代號,一條條拿去核對是不是真的存在(用 WebSearch 查 errorprone.info / spotbugs 官方文件 / pmd 官方規則頁),包括:`EP:FutureReturnValueIgnored`、`EP:GuardedBy`、`EP:EqualsHashCode`、`EP:EmptyCatch`、`SB:OBL_UNSATISFIED_OBLIGATION`、`PMD:CloseResource`、`PMD:AvoidDecimalLiteralsInBigDecimalConstructor`、`SB:RU_INVOKE_RUN`、`PMD:DoNotUseThreads`、`SB:SQL_INJECTION_JDBC`、`SB:IS2_INCONSISTENT_SYNC`、`SB:SBSC_USE_STRINGBUFFER_CONCATENATION`、`PMD:AvoidCatchingGenericException`、`PMD:AvoidInstantiatingObjectsInLoops`——**這些全部查得到、描述也對得上文件裡講的用途**。抓到一個例外:

severity: major
**
**blocking: 是**
**引句:「### R13. 邊界驗證與秘密 `SB:SQL_INJECTION_JDBC` `EP:UnsafeSqlInjection`」**(`governance/review-reports/code-java補棧/r1-slice-skills.patch:165`)

`EP:UnsafeSqlInjection` 這個 Error Prone bug pattern **查不到**。我直接抓 errorprone.info 的完整清單核對:

```
WebFetch https://errorprone.info/bugpatterns
→ "UnsafeSqlInjection" 不在清單裡;清單裡跟 Sql/Injection 相關的只有 FragmentInjection(跟 SQL 無關)
```

`SB:SQL_INJECTION_JDBC` 這個 SpotBugs 檢查是真的、也確實是抓 SQL 注入,但同一行硬湊出的第二個 `EP:UnsafeSqlInjection` 查無此物,像是憑名稱規律(`Unsafe` + 問題名)編出來的。這份文件開頭的「誠實邊界」明寫「工具名與規則名有查過官方頁面」(`r1-slice-skills.patch:7`),這個查不到的檢查名直接打臉這句保證——不是「沒實跑」的誠實邊界問題,是「宣稱查過的東西其實沒查對」。**寫錯的機檢代號會讓真的去配置 Error Prone 的人去找一個不存在的規則、白費工夫**,算 major、算 blocking。

其餘 22 條我抽查的 Java 語言行為描述(`BigDecimal(0.1)` 的精度問題、`BigDecimal.equals` 比 scale、`SimpleDateFormat` 執行緒不安全、Java 19 起 `ExecutorService implements AutoCloseable`、`parallelStream()` 用 `ForkJoinPool.commonPool()`、`@Transactional` 同類自呼叫代理失效)都跟我所知的 Java 行為與官方文件一致,沒有抓到錯誤。也用實際的 `JAVA_TEST_RE`/`KOTLIN_TEST_RE` 做了對照實驗(見下方指令),證實「Java 抄 Kotlin 的 `[^{]*?` 會被參數化註解的大括號斷掉」這個核心論點是真的、不是編的:

```
python3 - <<'EOF'
import re
sample = '''
@ParameterizedTest
@ValueSource(ints = {1, 2, 3})
void testSomething(int x) { assertTrue(x > 0); }
'''
kotlin_style_for_java = re.compile(r"@(?:Test|ParameterizedTest|RepeatedTest)\b[^{]*?\bvoid\s+([A-Za-z_]\w*)\s*\(", re.S)
print(kotlin_style_for_java.findall(sample))   # []  ← 真的斷了,證實文件講的問題存在
EOF
```

**誠實邊界寫得夠不夠清楚**:`skills/java-idioms/SKILL.md` 開頭那段(`r1-slice-skills.patch:7-8`)明講「本機沒有裝 Maven／Gradle／Error Prone／SpotBugs／PMD,一條都沒有實跑核對過」、對照組是 python-idioms 的本機跑法、還帶了 `REVISIT:2026-10-12`。我在這台機器上實測 `which mvn gradle` 確實都找不到、`javac -version` 確實是 JetBrains 附的 17.0.14——這段誠實邊界的每個具體宣稱都對得上實況,寫得清楚,沒有問題。**但正因為它自己講「一條都沒實跑」,`EP:UnsafeSqlInjection` 這種查不到的規則名才更值得注意**——因為文件承諾的不是「沒驗證過會不會執行」,而是「工具名與規則名有查過官方頁面」,這是兩件事,後者這次沒有做到。

### 6. 各篇筆記是否都標了「尚未在真專案跑過」

檢查了 Java 相關四處:
- `Projects/Java補棧_計劃.md`:summary 與內文各標了兩次(「全部只在合成樣本上測過」「零真專案」)。
- `Verification/2026-09-12_Java補棧合成樣本測試.md`:`valid_under` 欄位、白話開場、結尾「這篇不能證明什麼」三處都標了。
- `skills/java-idioms/SKILL.md`:「誠實邊界」段落標了。
- `Systems/效能檢核目錄.md` 的 Java 段標題:「消費端:尚無;2026-09-12 補,★尚未在真專案跑過★」——標了。

severity: minor
**
**blocking: 否**
**引句:「★本機沒裝 Maven／Gradle，一條都沒實跑過★」**(`governance/review-reports/code-java補棧/r1-slice-graph.patch` 內 `Systems/linter精選目錄.md` 的 Java 段標題)

`Systems/linter精選目錄.md` 的 Java 段標題只標了「本機沒裝建置工具、沒實跑過」,沒有像 `效能檢核目錄.md` 那樣同時明講「尚未在真專案跑過」——這是兩件不同的事(前者講「我有沒有跑過這個檢查工具」,後者講「有沒有真專案接進來用過」),`補新語言SOP.md` 第 11 步自己列的checklist 明講「計劃筆記、驗證紀錄、慣例 skill、兩份目錄段落,四個地方都要標」。這裡雖然邏輯上可以推論(沒真專案自然也沒跑過工具),但沒有逐字落實 SOP 自己開的檢查表,算措辭不夠精準的 minor,不影響判斷、不 blocking。

---

## 額外驗證(交叉核對數字類宣稱)

`Verification/2026-09-12_Java補棧合成樣本測試.md` 裡列的鄰居子集測試數,我逐一實跑核對,全部吻合(機械數,非憑印象):

```
python3 scripts/test_lumos.py -k "java"                → 17 passed（文件寫 17）
python3 scripts/test_lumos.py -k "stack_question_triggers" → 51 passed（文件寫 51）
python3 scripts/test_lumos.py -k "stack_question"       → 76 passed（文件寫 76）
python3 scripts/test_lumos.py -k "testmap"              → 73 passed（文件寫 73）
python3 scripts/test_lumos.py -k "profile_discovery"    → 38 passed（文件寫 38）
python3 scripts/test_lumos.py -k "pitfalls_stack"       → 9 passed（文件寫 9）
python3 scripts/test_lumos.py -k "impact_hook_stack"    → 16 passed（文件寫 16）
python3 scripts/test_lumos.py -k "stack_guess"          → 9 passed（文件寫 9）
python3 scripts/test_lumos.py -k "checky_"              → 14 passed（文件寫 14）
```

也核對了全表題數加總(`棧別提問表態閘.md` 寫「全表 id 集合 37→44 題」):
```
python3 -c "
import importlib.machinery
lum = importlib.machinery.SourceFileLoader('lum','scripts/lumos').load_module()
print(sum(len(v) for v in lum._STACK_QUESTION_SPECS.values()))
"
→ 44   # 對得上
```

以及骨架測試指令與 `javac`/`mvn`/`gradle` 是否真的如文件所說「本機有 javac、沒有 Maven/Gradle」:
```
which javac java   → /usr/bin/javac /usr/bin/java
javac -version     → javac 17.0.14（JBR,對應文件講的「JetBrains 附的 JDK 17」）
which mvn gradle    → 都找不到（對應文件講的「一個都沒裝」）
```

這些數字類與環境類宣稱**全部對得上**,顯示這批 diff 的作者確實有做機械查證的紀律,只是在「歷史事故次數的敘述」與「機檢規則名稱」這兩處各栽了一次跟頭。

---

## 結論

最嚴重 severity: **major**;blocking 共 **2** 條(項目 4 的 SOP 自相矛盾、項目 5 的 `EP:UnsafeSqlInjection` 查無此物)。另有 1 條 minor(項目 6 的 linter 目錄誠實邊界措辭)不 blocking。項目 1(README 語言表)不在本次收到的兩份材料範圍內,但另外核對過現存 README 內容與程式一致,未發現缺陷;項目 2、3(效能檢核目錄七列觸發字、test-profile-multiplatform 的 10 個鍵)逐字比對後為 clean。
