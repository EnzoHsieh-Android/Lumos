val theme: Flow<String> = context.dataStore.data
    .catch { if (it is IOException) emit(emptyPreferences()) else throw it }
    .map { it[KEY] ?: "light" } // GOOD
val t2 = dataStore.data.map { it[KEY] }.catch { emit(null) } // GOOD catch 在下游
fun names(resp: Resp) = resp.data.map { it.name } // GOOD 不是 DataStore
suspend fun t3() = try { dataStore.data.first() } catch (e: IOException) { null } // GOOD
suspend fun t4() = runCatching { dataStore.data.first() }.getOrNull() // GOOD runCatching 已接例外
