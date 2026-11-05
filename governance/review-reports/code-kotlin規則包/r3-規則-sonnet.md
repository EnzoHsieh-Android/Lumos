severity: major

# 第 3 輪規則席驗收報告

我拿修補後的規則逐條重跑了 r2 規則A F1–F12 與規則B Finding 1–12 的重現片段,另外補了「綁同一個變數」的對照寫法(好寫法與壞寫法各一段)。`check.py` 實跑結果是「規則 207 條,問題 0 個」。臨時目錄已刪。

**① r2 重現片段的結果**
- 規則A F1–F12 全部修對:壞寫法都報,好寫法都不報。F10、F11、F12 也修對。
- 規則B Finding 5–7、9、11、12 修對。Finding 8、10 修了,但修補本身有新洞,見下面的 finding。

**③ 搬走的三條在 `rules/` 沒有殘影**
- `kt-bg-dispatcher-touches-view`、`kt-worker-retry-unbounded`、`kt-statein-eagerly` 只在 `rules-review/` 命中。
- 我用 `sgconfig.yml` 掃含這三種形狀的檔,沒有任何命中。
- `sgconfig-review.yml` 在同一檔上:
  - 壞寫法有報:外層 Main 夾內層 IO、`mainland…` 派發器、只讀不判斷的 `runAttemptCount`、鄰行借理由的 Eagerly。
  - 好寫法有放行:`Main.immediate`、`Main + CoroutineName`、`d.main()`。

## Finding 1:okhttp 規則漏了 OkHttp 5 的 `r.body.string()`,把原本不報的正確寫法改成報
引句:「- pattern: $V.body().close()」
severity: major
blocking: 是

這一輪把放行從 regex 改成一組 pattern。修補前的 regex 有 `(\?|!!)?`,所以 `r.body.string()` 不報。新的 pattern 清單只有 `body!!`、`body?`、`body()` 三種,沒有「不帶符號」的 `$V.body.string()`、`$V.body.bytes()`、`$V.body.close()`。

OkHttp 5 的 `Response.body` 是非空屬性,這個寫法就是官方標準。

實跑(`kt-okhttp-response-not-closed`,warning,會擋推送):
```kotlin
fun o6(c: OkHttpClient, req: Request): String { val r = c.newCall(req).execute(); return r.body.string() }
fun o7(c: OkHttpClient, req: Request): String { val r = c.newCall(req).execute(); r.body.use { return it.string() } }
```
- 兩行都報。
- `r.body?.string()` 和 `r.body!!.string()` 不報。
- 建議:補上無符號版本。同一組裡 `$V.body?.use { }`、`$V.body!!.use { }` 也缺,實跑 `return r.body?.use { it.string() } ?: ""` 與 `r.body!!.use { return it.string() }` 都誤報(這兩個舊版就缺,不是這輪才壞)。

## Finding 2:DataStore 的 try/runCatching 放行只認「`data.first()`/`data.collect` 或剛好緊接 `.first()`」,中間多一個運算子就誤報
引句:「regex: '\.(first|firstOrNull)$'」
severity: major
blocking: 是

這是 r2 規則B Finding 10 的修補過頭。rule 是 warning,會擋推送。下面這些寫法例外在區塊內就丟出並被接住,修補前版本不報,修補後都報:
```kotlin
suspend fun a1() { try { dataStore.data.map { it[K] }.collect { _ui.value = it } } catch (e: IOException) { } }
suspend fun a9() { try { dataStore.data.map { it[K] }.distinctUntilChanged().first() } catch (e: IOException) { } }
suspend fun a4() { try { dataStore.data.map { it[K] }.single() } catch (e: IOException) { } }
suspend fun a5() { try { dataStore.data.map { it[K] }.toList() } catch (e: IOException) { } }
suspend fun t13() { try { dataStore.data.onEach { }.collect() } catch (e: IOException) { } }
```
- 實跑五行都報。
- 對照:`data.map{}.first()`、`data.collect{}`、`data.first()` 不報,壞寫法 `runCatching { data.map{} }` 與 try 裡只 `map` 還是報。
- 原因:放行只看 `map`/`onEach` 的父節點是不是 `.first`/`.firstOrNull`,而 `map` 後面接 `collect` 或再多一層運算子時,父節點不是它。
- 建議:判「這個 try 區塊或 runCatching 區塊裡有沒有終端操作(first、firstOrNull、single、toList、collect、launchIn 以外)」,不要只看緊鄰的一層。

## Finding 3:長壽 scope 規則對 `CoroutineScope(Dispatchers.IO) + job` 這種加法寫法誤報
引句:「# SupervisorJob 先存進同類別的屬性再組 scope;這個 scope 要引用到那個屬性名才算(代碼審 r2 規則B Finding 8)」
severity: minor
blocking: 是

綁定要求 job 變數出現在 `CoroutineScope(...)` 的括號裡。
```kotlin
class S6 {
    private val job = SupervisorJob()
    val scope = CoroutineScope(Dispatchers.IO) + job
}
```
- 實跑 `kt-long-lived-scope-plain-job` 報。
- 這個寫法有 SupervisorJob 但掛在括號外面,修補前版本不報。
- `CoroutineScope(Dispatchers.IO + job)` 與 `CoroutineScope(job + dp)` 都正常不報,所以只是少見寫法的誤報。

## Finding 4:`savedStateHandle` 名單加了 `state` 後,同名的 Map 或 Bundle 也被報
引句:「regex: '^(\w+\.)*_?(savedStateHandle|stateHandle|handle|savedState|state)$'」
severity: minor
blocking: 是

```kotlin
class MapHolder { val state = mapOf("a" to 1); val g = state["a"]!!; val h = state.get("a")!! }
```
- 兩行都報 `kt-savedstate-bang`。
- `state` 是很泛用的名字,規則沒有限制在 ViewModel 或 SavedStateHandle 型別裡。
- `_state.get<String>("x")!!` 也一併被報。
- 取捨:這是 r2 Finding 6 要求加進來的。建議至少限定在 `ViewModel` 類別內,或要求同檔有 `SavedStateHandle` 型別宣告。

## Finding 5:Ktor `HttpClient` 存變數後用 `c.use { }` 關,規則看不出來
引句:「- pattern: $V?.close()」
severity: minor
blocking: 是

```kotlin
suspend fun c() { val c = HttpClient(CIO); c.use { it.get("x") } }
```
- 實跑 `kt-ktor-client-per-call` 報。
- 放行只認 `$V.close()`,沒有 `$V.use { }`。
- `HttpClient(CIO).use { }` 直接接著用則正常不報,所以只有先存變數再 `use` 的寫法漏掉。
- 這在修補前也是一樣的,不是這輪才壞。

## 綁定檢查結論(鏡頭②)

- 沒有放寬過頭的新洞。壞寫法各一段都報:
  - 別的變數的 `isSuccessful`:兩個回應只檢查其中一個,檢查的那個不算。
  - 只拿來印 log 的 `isSuccessful`。
  - 別的 stream、writer 的 `close()`。
  - 別的 Response 的 `body`。
  - 沒用到的 SupervisorJob。
  - 借來的 executor。
- 好寫法都不報:
  - `check`、`require`、`if` 前置擋掉、`&&` 併判。
  - `use`、`close`、`finally`。
  - `Room.queryExecutor`。
  - `heightIn(min, max)`、`::key`、`keyFn`、`items(5)`。
  - `rememberSaveable(saver = …)`。
  - 按鈕裡真的有 Text 標籤。
- 收太緊的只有 Finding 1 到 5 這幾個窄角落。

## 其他小觀察(不開 finding)

- 語意覆核級的 `kt-bg-dispatcher-touches-view` 對具名引數 `withContext(context = Dispatchers.Main)` 會誤報。這是 info,不擋推送,留給盲判。
- `kt-test-multiple-schedulers` 的 Rule 名單改成必須帶 `Dispatcher` 或 `Coroutine`,名叫 `MainRule` 的自訂換 Main 規則會被當成沒換。這個名字少見,不開 finding。

總結:最嚴重的是兩條會擋推送的規則在常見正確寫法上誤報(okhttp 5 的 `body.string()` 與 DataStore 的 try 包 `map{}.collect{}`),其餘三條只是窄角落;r2 的漏報與誤報大多已修對,搬到覆核級的三條在 `rules/` 沒有殘影。
