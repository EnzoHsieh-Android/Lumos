fun token(): String? = runBlocking { context.dataStore.data.first()[TOKEN] } // BAD
fun theme() = runBlocking(Dispatchers.IO) { // BAD
    prefs.data.firstOrNull()
}
