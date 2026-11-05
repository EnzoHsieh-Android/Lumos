val Context.settings by preferencesDataStore("settings") // GOOD:檔案頂層建一次

// 容易誤報:DI 模組(object)裡用 @Singleton 提供,也是只建一次
object DataStoreModule {
    @Provides
    @Singleton
    fun provideSession(context: Context): DataStore<Preferences> =
        PreferenceDataStoreFactory.create { context.preferencesDataStoreFile("session") }
}

// 容易誤報:Hilt 模組的 companion object 與 @Module class 裡的 @Provides @Singleton 提供者
@Module
@InstallIn(SingletonComponent::class)
interface DsModule {
    companion object {
        @Provides
        @Singleton
        fun provideDs(@ApplicationContext context: Context): DataStore<Preferences> =
            PreferenceDataStoreFactory.create { context.preferencesDataStoreFile("ds") }
    }
}

@Module
@InstallIn(SingletonComponent::class)
class StoreModule {
    @Provides
    @Singleton
    fun provideStore(@ApplicationContext context: Context): DataStore<Preferences> =
        PreferenceDataStoreFactory.create { context.preferencesDataStoreFile("store") }
}
