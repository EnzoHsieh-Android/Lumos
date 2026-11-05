val theme: Flow<String> = context.dataStore.data.map { it[KEY] ?: "light" } // BAD
suspend fun token() = prefsDataStore.data.first()[TOKEN] // BAD
