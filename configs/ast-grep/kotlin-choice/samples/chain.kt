// 鏈式寫法另起一行:API 列的錨點是方法名那一段所在行(計劃〈用詞〉選擇點表 API)
package sample

fun chained(query: Flow<String>) {
    val r = query
        .debounce(300)
        .flatMapLatest { repo.search(it) } // HIT C-28
    val s = query
        ?.filter { it.isNotEmpty() } // HIT C-19
}
