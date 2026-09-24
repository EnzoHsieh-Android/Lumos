---
name: dart-idioms
description: 寫或審 Dart／Flutter 代碼前必讀——通用不變量層的慣例規則：非同步取消與逾時、串流與控制器一定要關、重活要離開主 isolate、金額不用 double、時間帶時區、例外不吞、集合與熱路徑，另含 Flutter 畫面層的組建成本、清單與生命週期一組平台特有條款。每條附壞例→好例與機檢對照（Dart 分析器的 lint 規則代號，已用本機分析器逐條驗過）。狀態管理選型（Provider／Riverpod／Bloc／GetX）、路由選型、後端選型不在此裁——查該專案圖譜。
---

# Dart／Flutter 慣例（通用不變量層）

**這份文件治的病**：AI 寫出「跑得起來、畫面看起來對，但會愈用愈卡、或在特定時序炸掉」的 Flutter——`StreamSubscription` 沒取消，換頁之後還在收資料並且對著已經不存在的畫面寫狀態；`await` 回來直接用 `context`，而使用者早就按了返回；把整包 JSON 在主 isolate 解析，一萬筆就掉幀；`ListView` 直接塞 `children` 把兩千個項目一次建出來；金額用 `double` 算到差一分錢。這些都不會在單元測試上炸，炸在使用者手上、在網路慢的那一刻、在資料變多之後。

**分層原則**：只寫不隨框架選擇改變的原則。用 Provider 還是 Riverpod 還是 Bloc、用 GoRouter 還是 Navigator 1.0、後端接 REST 還是 GraphQL——查該專案的知識圖譜與 CLAUDE.md（`lumos search <關鍵字>` 起手）。規則用「訂閱要有人取消」「重建範圍要收斂」這種能力措辭，不點名套件；真的只有 Flutter 畫面層成立的集中放在最後一節，並在標題標明。

**機檢欄說明**：`lint:規則名`＝Dart 分析器內建的 lint 規則，寫進專案的 `analysis_options.yaml` 才會生效（`package:flutter_lints` 已經預設開了一部分，但不是全部）；`自訂`＝可寫 ast-grep 規則；`不可機檢`＝只有本文件與審查鏡頭能守——排最前面。

> **誠實邊界（2026-09-13）**：本文件引用的 18 個 lint 規則代號**是用本機 Dart 分析器逐條驗過的**——把它們寫進設定檔跑一次，另外混入一個故意不存在的名字當對照，只有那一個被分析器判為不認得。所以「規則名存在」這件事有機械證據，**但「這條規則抓得到本文件描述的那個壞例」沒有逐條驗過**。
> **也尚未在任何真的 Flutter 專案上用過。** 第一個接入的專案要回填：哪些規則預設沒開、哪些誤報多到要關、哪些坑這份沒收。
> REVISIT:2026-10-13 若仍無 Flutter 消費端，把「未在真專案跑過」這件事再標一次，別讓它靜靜變成看起來可信的文件。

---

## 一、非同步：Dart 是單執行緒的，這一節是本文件存在的理由

### R1. 每一個外呼都要有逾時 ⚠ 不可機檢，生產最常炸
```dart
// ✗ 對方不回，這個 Future 就永遠不完成，載入轉圈轉到天荒地老
final res = await http.get(uri);

// ✓
final res = await http.get(uri).timeout(const Duration(seconds: 10));
```
- Dart 的 `http`、`Dio`、平台通道**預設都不逾時**。沒有逾時的等待不會報錯，只會讓畫面永遠停在載入狀態——使用者看到的是「卡住」，日誌裡什麼都沒有。
- 逾時要有對應的使用者可見結果（重試按鈕、錯誤訊息），不是吞掉換成空清單。

### R2. 丟出去不等的 Future，錯誤會無聲蒸發 `lint:unawaited_futures` `lint:discarded_futures`
```dart
// ✗ 例外掉進 zone 裡，沒有人看到
saveDraft(text);

// ✓ 要嘛等它
await saveDraft(text);
// ✓ 要嘛明講「我知道我不等，錯誤我自己接」
unawaited(saveDraft(text).catchError(reportError));
```
- `unawaited(...)` 不是裝飾，它的意思是「這是刻意的」。**刻意不等，就要自己處理錯誤**，否則跟忘了寫沒有差別。

### R3. 迴圈裡逐筆 await ＝ 延遲相加 ⚠ 不可機檢
```dart
// ✗ 一百筆就是一百趟來回
for (final id in ids) { results.add(await fetch(id)); }

// ✓ 並行，但要有上限：分批，每批最多 20 個同時飛
final results = <Item>[];
for (var i = 0; i < ids.length; i += 20) {
  final batch = ids.sublist(i, min(i + 20, ids.length));
  results.addAll(await Future.wait(batch.map(fetch)));
}
```
- 判斷順序：先確認彼此沒有資料依賴，再確認**下游吃得下**（對方的速率限制、資料庫連線池），才並行。
- `Future.wait` 沒有上限——一次丟一千個請求會把對方打掛，也會把自己的連線池耗光。要分批或用有上限的池子。

### R4. 重試要有退避與上限，而且不可逆的動作不准盲目重送 ⚠ 不可機檢
- 付款、下單、寄送這類動作重送等於做兩次。要嘛帶冪等鍵讓對方能去重，要嘛就不重試。
- 退避要有隨機抖動，否則所有裝置會在同一秒一起重試，把剛恢復的服務再打掛一次。

---

## 二、資源與生命週期：沒有人幫你關

### R5. 訂閱一定要取消 `lint:cancel_subscriptions`
```dart
// ✗ 換頁之後還在收，而且還握著整個 State 不放
stream.listen(_onData);

// ✓
late final StreamSubscription _sub;
@override void initState() { super.initState(); _sub = stream.listen(_onData); }
@override void dispose() { _sub.cancel(); super.dispose(); }
```
- 沒取消的訂閱是 Flutter 記憶體洩漏的頭號來源：它讓整個 State（連同它引用的所有東西）活得比畫面久。
- 同一條規則適用於 `Timer`、`AnimationController`、`TextEditingController`、`ScrollController`、`FocusNode`——**建立它的人負責釋放它**。

### R6. 自己開的 StreamController 要關 `lint:close_sinks`
- 開了不關，下游永遠等不到結束事件，`await for` 會一直停在那裡。

### R7. `await` 之後再用 context 要先確認畫面還在 `lint:use_build_context_synchronously`
```dart
// ✗ 使用者在等待期間按了返回，這行會對著已經拆掉的畫面操作
await save();
Navigator.of(context).pop();

// ✓
await save();
if (!mounted) return;
Navigator.of(context).pop();
```
- 這是 Flutter 最常見的「偶發崩潰」：測試環境網路快，await 幾乎瞬間回來，怎麼點都不會錯；使用者網路慢，就炸了。

### R8. 檔案與資料庫用非同步 API `lint:avoid_slow_async_io`
- 同步的 `File.readAsStringSync` 會把主 isolate 停住。大檔要串流讀，不要一次讀進記憶體。

---

## 三、重活要離開主 isolate

### R9. 解析、加解密、影像、大排序丟給 compute ⚠ 不可機檢，Dart 特有
```dart
// ✗ 一萬筆 JSON 在主 isolate 解析，畫面直接掉幀
final items = (jsonDecode(body) as List).map(Item.fromJson).toList();

// ✓
final items = await compute(parseItems, body);
```
- **Dart 沒有真正的多執行緒共享記憶體**：主 isolate 被佔住的期間，畫面完全不會更新。這跟有背景執行緒的語言不一樣，是這個棧特有的限制。
- 判斷門檻：會隨資料量成長的工作就要丟出去。固定成本的小事情丟出去反而更慢（isolate 有啟動與傳輸成本）。

---

## 四、數值、時間、序列化

### R10. 金額不准用 double ⚠ 不可機檢
- Dart 的 `double` 是 IEEE 754，`0.1 + 0.2 != 0.3`。金額用最小單位的 `int`（分、毫）或十進位套件，顯示時才轉。
- Dart 的 `int` 在 Web 上是 JavaScript 的數字（安全整數只到 2^53），跨平台的專案要確認範圍。

### R11. 時間一律帶時區，比較前先統一 ⚠ 不可機檢
- `DateTime.now()` 是本機時區。存進資料庫、傳給後端一律用 UTC（`toUtc()`），顯示才轉回本地。
- 兩個 `DateTime` 比較之前要確認 `isUtc` 一致，否則比出來的結果是錯的而且不會報錯。

### R12. 從外面來的 JSON 一律當成不可信 ⚠ 不可機檢
```dart
// ✗ 欄位型別跟你想的不一樣就直接爆 type cast
final n = json['count'] as int;

// ✓ 在邊界轉型，轉不了就明確失敗（或回傳解析錯誤給上層決定降級）
final raw = json['count'];
final n = raw is int ? raw : int.tryParse('$raw') ?? (throw FormatException('count 不是整數: $raw'));
```
- 後端把 `int` 改成 `String` 是很常見的事。解析層要有明確的預設值與錯誤路徑，不要讓一個欄位型別變動炸掉整個畫面。
- 機檢：`lint:avoid_dynamic_calls` 能抓一部分「對 dynamic 直接呼叫方法」的寫法。

---

## 五、例外與日誌

### R13. 不准空的 catch `lint:empty_catches`
```dart
// ✗ 真正的錯被吞掉，之後查不到
try { await sync(); } catch (_) {}

// ✓ 至少要記，而且要記得夠查
try { await sync(); } on TimeoutException catch (e, s) { log.warning('同步逾時', e, s); }
```
- 接住例外的三個正當理由：**換成使用者看得懂的訊息**、**降級成可用狀態**、**記錄後重新丟出**。都不是的話就別接。
- 只丟 `Error` 的子類或自訂例外，不要 `throw '字串'`（`lint:only_throw_errors`）。

### R14. 正式版用有等級的 logger，不用 print `lint:avoid_print`

---

## 六、Flutter 畫面層（平台特有，只在有 UI 的專案成立）

### R15. build 是會被反覆呼叫的，裡面不准做重活 ⚠ 不可機檢，頭號條款
```dart
// ✗ 每次重建都新建一個 controller、重新排序整份清單
Widget build(BuildContext context) {
  final sorted = items.toList()..sort(byName);
  final ctrl = TextEditingController();
  ...
}

// ✓ 建立一次的東西放 initState；算出來的東西放 model 或快取
```
- `build` 一秒可能被叫六十次。它應該只做「把現有資料排成畫面」這件事。
- 不會變的子樹用 `const`（`lint:prefer_const_constructors`、`lint:prefer_const_literals_to_create_immutables`）——`const` 的 widget 在重建時會被直接略過，這是零成本的優化。
- `createState` 裡不准有邏輯（`lint:no_logic_in_create_state`）。

### R16. 重建範圍要收斂 ⚠ 不可機檢
- `setState` 會重建整個 State 的 `build`。會變的那一小塊應該拆成自己的 widget，或用 `ValueListenableBuilder` 這類只重建局部的做法。
- 狀態容器的監聽範圍太寬（整個大 store 當依賴，改一個欄位全樹重算）是同一個病的另一種寫法。

### R17. 長清單一定要用 builder ⚠ 不可機檢
```dart
// ✗ 兩千個項目一次全建出來
ListView(children: items.map(buildRow).toList())

// ✓ 只建看得到的
ListView.builder(itemCount: items.length, itemBuilder: (_, i) => buildRow(items[i]))
```
- 長清單上加 `shrinkWrap: true` 會讓它每次量整份，等於抵銷了 builder 的好處。需要巢狀捲動時改用 sliver。
- 項目的 key 要穩定（用資料的 id，不要用索引）——索引當 key 在增刪時會讓狀態接錯項目。widget 的建構式要收 key（`lint:use_key_in_widget_constructors`）。

### R18. 圖片要降解析度 ⚠ 不可機檢
- 一張 4000×3000 的圖顯示在 100×100 的格子裡，記憶體裡仍然是全尺寸。`Image.network`／`Image.asset` 要給 `cacheWidth`／`cacheHeight`。
- 這是清單捲動卡頓與記憶體爆掉最常見的單一原因。

### R19. 留白用 `SizedBox`，不包多餘的 `Container` `lint:avoid_unnecessary_containers` `lint:sized_box_for_whitespace`

---

## 這份文件的天花板

- **只證「這些是公認的坑」，不證「你的專案現在沒有這些坑」**。要知道現在有沒有，去跑分析器，不是讀這份。
- **規則代號存在有機械證據，規則抓得到壞例沒有**。引用的 18 個名字用本機分析器驗過確實被認得，但沒有逐條造壞例確認它真的會亮。
- **零真專案實證**。誤報率、哪幾條在真的程式碼上吵到要關，全都沒有數據。
