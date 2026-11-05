val theme: Flow<String> = context.dataStore.data.map { it[KEY] ?: "light" } // BAD
suspend fun token() = prefsDataStore.data.first()[TOKEN] // BAD
// 代碼審 r2(規則B Finding 10):runCatching/try 只包到建立或排程流,錯誤在稍後收集時才發生
val flow = runCatching { dataStore.data.map { it[K] } }.getOrNull() // BAD
fun h() { runCatching { viewModelScope.launch { dataStore.data.collect { } } } } // BAD
fun i() = try { dataStore.data.map { it[K] } } catch (e: IOException) { null } // BAD
