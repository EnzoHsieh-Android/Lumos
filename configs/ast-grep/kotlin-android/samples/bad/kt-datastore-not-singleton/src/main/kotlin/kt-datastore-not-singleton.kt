class SettingsRepository(private val context: Context) {
    private val store = PreferenceDataStoreFactory.create { context.preferencesDataStoreFile("settings") } // BAD:每個實例各建一個
}

fun openStore(context: Context): DataStore<Preferences> {
    val factory = preferencesDataStore("session") // BAD:函式裡每次呼叫都建
    return factory.getValue(context, Context::javaClass)
}
