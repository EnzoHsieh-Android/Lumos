val theme: Flow<String> = context.dataStore.data
    .catch { if (it is IOException) emit(emptyPreferences()) else throw it }
    .map { it[KEY] ?: "light" } // GOOD
val t2 = dataStore.data.map { it[KEY] }.catch { emit(null) } // GOOD catch 在下游
fun names(resp: Resp) = resp.data.map { it.name } // GOOD 不是 DataStore
suspend fun t3() = try { dataStore.data.first() } catch (e: IOException) { null } // GOOD
suspend fun t4() = runCatching { dataStore.data.first() }.getOrNull() // GOOD runCatching 已接例外
// 容易誤報(代碼審 r2 規則B Finding 10):區塊內就收集完,例外在區塊裡丟出
suspend fun t5() = try { dataStore.data.map { it[K] }.first() } catch (e: IOException) { null } // GOOD
suspend fun t6() { try { dataStore.data.collect { use(it) } } catch (e: IOException) { } } // GOOD
