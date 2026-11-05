// 語意覆核級已知誤報(代碼審 r3 規則席 Finding 2):try/runCatching 區塊裡接的是 first/firstOrNull 以外的終端操作,
// 收集在區塊內完成,IOException 會在區塊裡丟出;形狀上列舉不完所有終端操作
suspend fun fp1() { try { dataStore.data.map { it[K] }.collect { use(it) } } catch (e: IOException) { } }
suspend fun fp2() = runCatching { dataStore.data.map { it[K] }.toList() }.getOrNull()
suspend fun fp3() = try { dataStore.data.map { it[K] }.single() } catch (e: IOException) { null }
suspend fun fp4() { try { dataStore.data.onEach { log(it) }.collect() } catch (e: IOException) { } }
suspend fun fp5() { try { dataStore.data.map { it[K] }.collectLatest { show(it) } } catch (e: IOException) { } }
// 席位原片段:中間多一層運算子再接 first()
suspend fun a9() { try { dataStore.data.map { it[K] }.distinctUntilChanged().first() } catch (e: IOException) { } }
