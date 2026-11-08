# 判讀準則(android形狀列補規則,2026-11-09 寫定,撈語料結果出來前凍結)

判讀代理拿到每一處:規則 id、檔案路徑、命中行、前後各 20 行。逐處判三選一,附一句理由:

- **TP(真問題)**:命中處就是那條規則出處講的壞寫法。
- **FP(誤報)**:命中處不是那個壞寫法,要寫屬於哪一類(見各條)。
- **UNSURE(判不準)**:前後 40 行看不出關鍵事實(例如接收者的型別)。判不準不算真問題,留在誤報比例的分母。

通則(四條共用,同 [[Projects/Android不接閘資安規則重量_計劃]] 的判準 v2):
- 範例碼只看路徑:路徑含 `/sample/`、`/samples/`、`/example/`、`/examples/`、`/demo/` 的算 FP(範例碼);repo 名帶 demo、example 不算。
- 教材與掃描器固件(路徑含 `fixtures`、`testdata`、`testData`)在抽樣前排除,不進判讀。
- 同一份程式複製到不同 repo(同檔名、命中處前後 20 行去空白後相同)只抽一處。

## kt-map-await-deferred(API-2)
- TP:被 map 的是 `Deferred` 的集合(常見是前面 `map { async { … } }` 產生的,或型別寫明 `List<Deferred<…>>`),在 map 裡逐一 `await()`。刻意要循序等也算 TP:出處說它跟 awaitAll 不等價(要等到失敗的那個才會失敗)。
- FP 類:接收者不是 Deferred(Play services `Task`、`ListenableFuture`、OkHttp `Call`、自訂的 await)、`Flow` 的 map(一筆一筆來,沒有集合可 awaitAll)、範例碼。
- UNSURE:看不出接收者是不是 Deferred。

## kt-compose-dispose-not-needed(UI-33)
- TP:DisposableEffect 裡沒有任何需要解除的東西(只是記 log、送事件、設值),卻寫了空的 `onDispose`;提早返回的 `return@DisposableEffect onDispose { }` 也算(同樣是沒有要清理的東西卻寫空 onDispose)。
- FP 類:區塊裡其實有需要解除的東西,只是名字不在共用註冊判斷的字表裡(例:`start()` 配 `stop()`、`acquire()`、`bind…`、`collect` 一條流)——這種是「該清理卻沒清」,規則訊息叫人改 LaunchedEffect 是錯的方向;範例碼。
- UNSURE:看不出區塊裡呼叫的東西要不要解除。

## kt-hilt-binding-missing-qualifier(ARCH-59)
- TP:同一個 module 裡,報的那個綁定沒有限定詞,而另一個回傳同一型別的綁定有限定詞(@Named 或同檔 @Qualifier 宣告的註解)。
- FP 類:兩個型別其實不同(泛型參數不同、同名不同套件)、另一個其實是多重綁定、範例碼。
- UNSURE:看不出兩個型別是不是同一個。

## kt-hilt-entrypoint-accessor-mismatch(ARCH-62)
- TP:fromX 跟 entry point 的 @InstallIn 元件對不上(對應照 Hilt 原始碼 EntryPointAccessors.kt 的 KDoc:fromApplication→SingletonComponent、fromActivity→ActivityComponent、fromFragment→FragmentComponent、fromView→ViewComponent 或 ViewNoFragmentComponent)。
- FP 類:規則認錯了 entry point(同名的另一個 interface、巢狀類別)、範例碼。
- UNSURE:看不出呼叫用的是哪一個 entry point。
