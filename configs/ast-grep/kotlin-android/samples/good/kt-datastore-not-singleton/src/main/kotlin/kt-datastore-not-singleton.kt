val Context.settings by preferencesDataStore("settings") // GOOD:檔案頂層建一次

// 容易誤報:DI 模組(object)裡用 @Singleton 提供,也是只建一次
object DataStoreModule {
    @Provides
    @Singleton
    fun provideSession(context: Context): DataStore<Preferences> =
        PreferenceDataStoreFactory.create { context.preferencesDataStoreFile("session") }
}
