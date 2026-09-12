---
name: java-idioms
description: 寫或審 Java（JVM 後端服務、Android 舊碼、批次與排程程式）代碼前必讀——通用不變量層的慣例規則：並行等待與有界執行緒池、資源一定要關、外呼逾時與重試、金額用 BigDecimal、時間帶時區、例外不吞、集合與熱路徑、邊界驗證與秘密，另含 Android 生命週期與 JPA 交易兩組平台特有條款。每條附壞例→好例與機檢對照（Error Prone／SpotBugs／PMD／NullAway）。框架選擇（Spring vs Quarkus、JPA vs MyBatis、Gradle vs Maven）不在此裁——查該專案圖譜。
---

# Java 慣例（通用不變量層）

**這份文件治的病**：AI 寫出「編得過、測得過，但會在半夜炸」的 Java——`Connection` 沒關把連線池名額耗光、`future.get()` 沒帶逾時讓執行緒永遠卡著、`RestTemplate` 沒設逾時讓一個慢的下游拖垮整台機器、金額用 `double` 算到差一分錢、`SimpleDateFormat` 當靜態欄位在多執行緒下吐出亂七八糟的日期、`catch (Exception e) {}` 把真正的錯吞掉。這些都不會炸在單元測試上，炸在跑了三天之後、在下游抖一下的那一刻。

**分層原則**：只寫不隨框架選擇改變的原則。Spring 還是 Quarkus、JPA 還是 MyBatis、Gradle 還是 Maven——查該專案的知識圖譜與 CLAUDE.md（`lumos search <關鍵字>` 起手）。規則用「交易邊界」「連線池」這種能力措辭，不點名框架；真的只有某平台成立的（Android 生命週期、JPA 代理）集中放在最後兩節，並在標題標明。

**機檢欄說明**：`EP:名稱`＝Error Prone（Google 的編譯期檢查外掛，跟 javac 一起跑）；`SB:代碼`＝SpotBugs（讀 bytecode）；`PMD:規則`＝PMD（讀原始碼）；`NullAway`＝空值分析（Error Prone 外掛）；`自訂`＝可寫 ast-grep 規則；`不可機檢`＝只有本文件與審查鏡頭能守——排最前面。

> **誠實邊界（2026-09-12）**：本文件是官方文件整理。工具名與規則名有查過官方頁面——**但這道自查本身出過一次錯**：2026-09-12 代碼審抓到 R13 曾引用一個 Error Prone 官方清單裡查不到的規則名（已刪除），所以「查過」這句話請當成「查過但不是零失誤」。另外，**本機沒有裝 Maven／Gradle／Error Prone／SpotBugs／PMD，一條都沒有實跑核對過**（對照組：python-idioms 的 28 條 ruff 代號是用本機 `ruff rule` 逐條查過的）。**也尚未在任何真 Java 專案上用過**。第一個接入的專案要回填：哪些規則預設沒開、哪些誤報多到要關、哪些坑這份沒收。
> REVISIT:2026-10-12 若仍無 Java 消費端，把「未實跑」這件事再標一次，別讓它靜靜變成看起來可信的文件。

---

## 一、並行與執行緒（本文件存在的理由之一）

### R1. 互不依賴的等待必須一起飛 ⚠ 不可機檢，頭號條款
```java
// ✗ 笨（延遲相加）
Balance b = client.balance();
List<Position> p = client.positions();

// ✓ 一起飛
CompletableFuture<Balance> bf = CompletableFuture.supplyAsync(client::balance, pool);
CompletableFuture<List<Position>> pf = CompletableFuture.supplyAsync(client::positions, pool);
CompletableFuture.allOf(bf, pf).join();
```
- 判斷順序：先確認沒有資料依賴，再確認沒有共享資源（**同一個交易、同一條連線的查詢不准平行**），才並行。
- `supplyAsync` 不指定執行器會用 `ForkJoinPool.commonPool()`——那是整個 JVM 共用的，拿來做阻塞 IO 會把其他人一起餓死。永遠自己給 pool。

### R2. 執行緒池要有界，而且要關 ⚠ 不可機檢，生產最常炸
```java
// ✗ newCachedThreadPool 沒有上限：來多少請求就開多少執行緒
ExecutorService pool = Executors.newCachedThreadPool();

// ✓ 有界，而且滿了要有明確的拒絕策略
ExecutorService pool = new ThreadPoolExecutor(
    8, 8, 0L, TimeUnit.MILLISECONDS,
    new ArrayBlockingQueue<>(500),
    new ThreadPoolExecutor.CallerRunsPolicy());
```
- 大小依**下游能吃多少**算，不是依 CPU 數抄公式：下游是 DB 就看連線池，是外部 API 就看對方的速率限制。
- 自己建的 pool 一定要有人負責 `shutdown()`；長活的放進容器的生命週期管理，短命的用 try-with-resources（Java 19+ `ExecutorService` 實作了 `AutoCloseable`）。

### R3. `get()` / `join()` 一定要有逾時 ⚠ 不可機檢
```java
// ✗ 對方不回，這條執行緒就永遠站在這裡
Result r = future.get();

// ✓
Result r = future.get(5, TimeUnit.SECONDS);   // 或 orTimeout(5, SECONDS)
```
- 沒有逾時的等待會一路往上堆：執行緒用完 → 佇列滿 → 整個服務不回應。這是「一個慢的下游拖垮整台機器」最常見的路徑。
- 機檢：`EP:FutureReturnValueIgnored`（Future 回傳值被丟掉＝例外無聲蒸發）能抓另一半的錯，抓不到「沒帶逾時」。

### R4. 共享可變狀態：先想能不能不共享 ⚠ 不可機檢
- 順序：不可變物件 ＞ 侷限在單一執行緒 ＞ 併發集合（`ConcurrentHashMap`）＞ 細粒度鎖 ＞ 大段 `synchronized`。
- 雙重檢查鎖定的欄位一定要 `volatile`，不然另一條執行緒可能看到「建好一半」的物件。
- 機檢：`EP:GuardedBy`（有標註才驗）、`SB:IS2_INCONSISTENT_SYNC`。標註要自己加，不加等於沒有。

---

## 二、資源一定要關

### R5. try-with-resources，不要 finally 手關 `SB:OBL_UNSATISFIED_OBLIGATION` `PMD:CloseResource`
```java
// ✗ 中間丟例外就漏一條連線；漏久了整個池子拿不到連線
Connection c = ds.getConnection();
PreparedStatement ps = c.prepareStatement(SQL);
ResultSet rs = ps.executeQuery();

// ✓ 反向依序關閉，例外照樣關
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(SQL);
     ResultSet rs = ps.executeQuery()) {
    ...
}
```
- `Files.lines()`、`Files.walk()` 回的是**要關的 Stream**，最常被忘記：`try (Stream<String> lines = Files.lines(p)) { ... }`。
- 這一類的症狀很晚才出現，而且長得像別的病（「資料庫變慢」「服務偶爾沒回應」），所以值得在審查時直接看有沒有 try-with-resources，不要靠事後查。

### R6. 連線池大小是算出來的 ⚠ 不可機檢
- 抄預設的後果分兩頭：太小＝請求排隊等連線；太大＝把資料庫壓垮，而資料庫垮了是全體一起垮。
- 算法要寫進圖譜（實例數 × 每實例池大小 ≤ DB 能承受的連線數），不是留在某個人腦袋裡。

---

## 三、外呼

### R7. 每個外呼都要有連線逾時與讀取逾時 ⚠ 不可機檢，最容易漏
```java
// ✗ HttpURLConnection、RestTemplate 的預設是「無限等」
RestTemplate rt = new RestTemplate();

// ✓
RestTemplate rt = new RestTemplateBuilder()
    .setConnectTimeout(Duration.ofSeconds(2))
    .setReadTimeout(Duration.ofSeconds(5))
    .build();
// java.net.http.HttpClient：connectTimeout 建 client 時給、request 逾時每筆給
```
- 兩個逾時是不同的東西：連線逾時＝握手握不上；讀取逾時＝握上了但對方不吐資料。只設一個等於沒設。

### R8. 重試要有退避與上限，不可逆的操作不盲目重送 ⚠ 不可機檢
- 固定間隔的無限重試在對方剛恢復時會變成自己人的 DDoS（驚群）。要指數退避＋抖動＋次數上限。
- **下單、付款、寄信、發貨這類做了回不去的操作**：重送前一定要有冪等鍵，讓對方能認出「這是同一筆」。否則網路抖一下就變成下兩次單。

---

## 四、正確性地雷（不是效能，是會算錯）

### R9. 金額用 `BigDecimal`，而且用字串建 ⚠ 不可機檢
```java
// ✗ double 存不下 0.1；new BigDecimal(0.1) 會把 double 的誤差原封不動搬進來
double total = 0.1 + 0.2;                 // 0.30000000000000004
BigDecimal bad = new BigDecimal(0.1);     // 0.1000000000000000055511151231257827...

// ✓
BigDecimal good = new BigDecimal("0.1");
BigDecimal sum = good.add(new BigDecimal("0.2"));
if (sum.compareTo(target) == 0) { ... }   // equals 會比 scale：2.0 不等於 2.00
```
- 除法一定要指定 scale 與 `RoundingMode`，不然除不盡直接丟 `ArithmeticException`。
- 機檢：`PMD:AvoidDecimalLiteralsInBigDecimalConstructor`。

### R10. 時間一律帶時區，不要用 `Date` / `SimpleDateFormat` ⚠ 不可機檢
```java
// ✗ SimpleDateFormat 不是執行緒安全的；當靜態欄位共用會吐出亂掉的日期
static final SimpleDateFormat F = new SimpleDateFormat("yyyy-MM-dd");

// ✓ java.time 全部不可變、執行緒安全
Instant now = Instant.now();                       // 時間點
ZonedDateTime local = now.atZone(ZoneId.of("Asia/Taipei"));   // 要顯示才轉時區
DateTimeFormatter F2 = DateTimeFormatter.ISO_LOCAL_DATE;      // 可安全共用
```
- 儲存與傳輸用 `Instant`（UTC），只有要給人看的時候才轉當地時區。`LocalDateTime` 沒有時區，拿它比較跨時區的事情一定錯。

### R11. 例外不要吞、不要拿來當流程控制 `PMD:AvoidCatchingGenericException` `EP:EmptyCatch`
```java
// ✗ 錯被吃掉，之後查不出來
try { doIt(); } catch (Exception e) { }

// ✓ 要嘛處理、要嘛往上丟，而且帶上原因
try { doIt(); } catch (IOException e) {
    throw new UncheckedIOException("寫入報表失敗: " + path, e);
}
```
- `catch (InterruptedException e)` 一定要 `Thread.currentThread().interrupt()` 把中斷旗標補回去，否則上層的取消機制失效（`SB:RU_INVOKE_RUN`、`PMD:DoNotUseThreads` 只抓到周邊，這條本身不可機檢）。
- 日誌要記整個例外物件（`log.error("msg", e)`），不是 `e.getMessage()`——堆疊被丟掉就等於沒記。

### R12. `equals` / `hashCode` 成對，可變物件不要當 Map 的 key `EP:EqualsHashCode`
- 只改一個 = 放進 `HashMap` 就找不回來。用 record 或 IDE 產，不要手寫一半。
- 物件當 key 之後又改了它的欄位，那筆資料就永遠撈不出來，也不會有任何錯誤訊息。

### R13. 邊界驗證與秘密 `SB:SQL_INJECTION_JDBC`
- SQL 一律 `PreparedStatement` 帶參數，不要字串相接——這是唯一真正擋得住注入的做法。
- 秘密不寫死在程式碼、不進日誌。設定從環境變數或密鑰管理服務讀。
- 外部進來的資料在邊界就驗（長度、範圍、格式），不要讓它帶著進到核心邏輯再炸。

---

## 五、集合與熱路徑

### R14. 迴圈裡不要相接字串 `SB:SBSC_USE_STRINGBUFFER_CONCATENATION`
```java
// ✗ 每圈生一個新字串，n 個字串就是 O(n²)
String s = "";
for (String part : parts) s += part;

// ✓
StringBuilder sb = new StringBuilder();
for (String part : parts) sb.append(part);
```

### R15. 成員查找不要用 List ⚠ 不可機檢
- `list.contains(x)` 是逐個比（O(n)）。在迴圈裡做就是 O(n²)，資料一多就爆。換 `HashSet` / `HashMap`。
- `list.remove(0)` 對 `ArrayList` 是整批往前搬；要當佇列用 `ArrayDeque`。

### R16. 熱路徑注意自動裝箱 ⚠ 不可機檢
- `Integer` 當 `int` 用，每次運算都在配置物件。大迴圈裡用原始型別或 `IntStream`。
- `Map<Long, Long>` 這種在高頻路徑上是純粹的物件產生器，量大時考慮專用的原始型別集合。

### R17. Stream 只能走一次，而且別在裡面做 IO ⚠ 不可機檢
- 同一個 Stream 消費兩次會丟 `IllegalStateException`；要用兩次就先收成集合。
- `parallelStream()` 用的是全 JVM 共用的 `ForkJoinPool.commonPool()`——裡面做阻塞 IO 會拖垮整個 JVM 的其他平行工作。要平行就自己給執行器。

---

## 六、Android 特有（只有 Android 專案適用）

### R18. 不要讓長活物件握著 `Context` / `Activity` ⚠ 不可機檢
```java
// ✗ 單例握著 Activity：畫面關了記憶體也收不回
private static Helper instance;
Helper(Context context) { this.context = context; }

// ✓ 要長期存就存 applicationContext
Helper(Context context) { this.context = context.getApplicationContext(); }
```
- 同一類的洩漏：非靜態內部類別（隱含握著外層 Activity）、`Handler` 的匿名類別、註冊了沒解除的監聽器與廣播接收器。

### R19. 主執行緒上不做磁碟、網路、大解析 ⚠ 不可機檢
- 主執行緒被擋超過約 5 秒，系統會判定沒有回應直接殺掉；就算沒到 5 秒，畫面也已經卡住。
- `SharedPreferences.commit()` 是同步寫磁碟，`apply()` 才是非同步。

### R20. 回呼要跟畫面的生命週期綁 ⚠ 不可機檢
- `AsyncTask`（已廢棄）、裸的 `Thread`、沒有解除的回呼，都會在畫面已經關掉之後回來寫 UI。
- `findViewById` 不要在 `getView` / `onBindViewHolder` 裡反覆呼叫——那是每一列都在重新走整棵畫面樹。

---

## 七、JPA / 交易特有（只有用 ORM 的後端適用）

### R21. N+1 查詢 ⚠ 不可機檢（要開 SQL 日誌才看得到）
```java
// ✗ 一筆訂單一次查詢：1 + N 次來回
for (Order o : orderRepo.findAll()) { o.getItems().size(); }

// ✓ 一次撈回來
@Query("select o from Order o join fetch o.items")     // 或 @EntityGraph
```
- 這是後端最常見也最貴的效能問題，而且在測試資料只有三筆的時候完全看不出來。

### R22. `@Transactional` 被同類自呼叫等於沒開 ⚠ 不可機檢
- 交易是靠代理物件攔截外部呼叫來開的。同一個類別裡 `this.doIt()` 直接呼叫不經過代理，標註完全不生效——**而且不會有任何錯誤訊息**。
- 交易裡面不要夾外部呼叫（HTTP、寄信）：交易會被拉長，鎖也跟著撐長；而且外呼成功、交易回滾的時候，那封信已經寄出去了收不回來。

### R23. 大結果集要分頁或串流 ⚠ 不可機檢
- `findAll()` 對一張會長大的表就是一顆定時炸彈。用 `Pageable`，或用串流逐筆處理。

---

## 接線表（怎麼把機檢那半裝起來）

**本機沒有實跑核對過，以下是官方文件的接法，第一個接入的專案要驗一次再回填。**

| 工具 | 裝法 | 進 lumos 的方式 |
|---|---|---|
| Error Prone | Gradle／Maven 的編譯器外掛，跟 javac 一起跑 | 編譯期就擋，不需要另外接 |
| SpotBugs | Gradle／Maven plugin | 可輸出 SARIF，接進 `.lumos/lint.json` 的 `"java"` 鍵 |
| PMD | Gradle／Maven plugin，規則集要自己挑 | 可輸出 SARIF |
| NullAway | Error Prone 的外掛，要標註套件範圍 | 編譯期 |

`.lumos/lint.json` 的鍵就是副檔名，所以 Java 不需要改任何程式：
```json
{"java": ["./gradlew spotbugsMain -PsarifOut={LINT_SARIF_OUT}"]}
```

**其餘的坑靠審查鏡頭**：本文標「⚠ 不可機檢」的條目，載重問題已經由 lumos 的效能檢核機制在三個時機自動推送（動手前、推送前、終審），內容來源是圖譜的 `Systems/效能檢核目錄` Java 段——兩邊有雙向同步義務，改一邊要改另一邊。
