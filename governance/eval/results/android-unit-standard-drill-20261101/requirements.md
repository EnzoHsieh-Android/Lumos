# 需求書:現金收支類別管理(CategoryVm)

這份需求書描述「類別管理」對話框背後的 ViewModel 應有的行為。它是寫測試的唯一判準來源:預期值要從這裡推,不要從程式實作抄。需求書沒寫到的情況,不要自己猜一個答案寫進斷言——列進回報的「需求書沒講清楚」清單。

## 名詞

- **類別**:一筆 `Category(name, kind, seq)`。`name` 是名稱,`kind` 是收支別(`"I"` 收入、`"O"` 支出),`seq` 是排序號(字串)。
- **資料來源**:`CategorySource`,三個方法各回傳一條 Flow,Flow 裡發出 `Resource.Success(...)` 或 `Resource.Error(訊息)`(也可能發 `Resource.Loading`,ViewModel 要忽略它)。

## 行為

- **Q1 載入**:呼叫 `loadAll()` 後,`categories` 變成資料來源回傳的清單,順序照回傳的順序;收入與支出都要在,不過濾。
- **Q2 載入失敗**:資料來源回 `Resource.Error(訊息)` 時,`categories` 保持載入前的內容不變,並透過 `error` 通知一次,內容就是那個訊息原文。
- **Q3 建議排序號**:`nextSeq()` 回傳字串,值 = 目前清單裡「能解讀成整數的排序號」的最大值加 10。
  - 不能解讀成整數的排序號(例如 `"A1"`、`""`)忽略不算。
  - 負數也算整數(例如只有 `"-5"` 時回傳 `"5"`)。
  - 清單是空的、或沒有任何能解讀成整數的排序號時,回傳 `"10"`。
- **Q4 新增**:呼叫 `add(name, kind, seq)` 會把這三個值原樣組成一筆類別送給資料來源(一次只送這一筆)。
  - 成功:`addResult` 通知一次 `true`,然後重新載入清單(清單變成重新載入後資料來源給的內容)。
  - 失敗:`addResult` 不通知;`error` 通知一次失敗訊息;不重新載入。
- **Q5 作廢**:呼叫 `delete(seq)` 會把這個排序號送給資料來源作廢(一次只送這一筆)。
  - 成功:`deleteResult` 通知一次 `true`,然後重新載入清單。
  - 失敗:`deleteResult` 不通知;`error` 通知一次失敗訊息;不重新載入。
- **Q6 載入中**:只要還有任何一個請求(載入、新增、作廢)沒結束,`loading` 就是 `true`;全部結束才變回 `false`。兩個請求重疊時,先結束的那個不能把 `loading` 關掉。一開始(還沒有任何請求)是 `false`。
- **Q7 通知是一次性的**:`addResult`、`deleteResult`、`error` 是給畫面顯示提示用的一次性通知;畫面正在收的時候,每個結果只通知一次。

## 公開介面(只有這些可以用;不要讀 ViewModel 的實作檔)

```kotlin
package com.example.pos
interface CategorySource {
    fun loadAll(): Flow<Resource<List<Category>>>
    fun add(items: List<Category>): Flow<Resource<Boolean>>
    fun voidCategories(items: List<VoidCategory>): Flow<Resource<Boolean>>
}

package com.example.pos.category
class CategoryVm(source: CategorySource) : ViewModel() {
    val categories: StateFlow<List<Category>>
    val addResult: SharedFlow<Boolean>
    val deleteResult: SharedFlow<Boolean>
    val error: SharedFlow<String>
    val loading: StateFlow<Boolean>
    fun loadAll(): Job
    fun nextSeq(): String
    fun add(name: String, kind: String, seq: String): Job
    fun delete(seq: String): Job
}
// ViewModel 內部用 viewModelScope 開協程。
// 資料型別:com.example.pos.Category(name, kind, seq)、VoidCategory(seq)
//          com.example.pos.Resource:Success(data)、Error(exception: String)、Loading(isLoading)
```
