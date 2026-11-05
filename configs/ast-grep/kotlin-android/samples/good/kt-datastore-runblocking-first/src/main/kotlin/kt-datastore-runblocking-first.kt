suspend fun token(): String? = context.dataStore.data.catch { emit(emptyPreferences()) }.first()[TOKEN] // GOOD suspend
fun main() = runBlocking { println(Resp().data.first()) } // GOOD 不是 DataStore(命令列入口的 runBlocking)
