package bad

@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class AuthClient

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides  // BAD
    fun provideClient(): OkHttpClient {
        return OkHttpClient()
    }

    @AuthClient
    @Provides
    fun provideAuthClient(auth: AuthInterceptor): OkHttpClient {
        return OkHttpClient.Builder().addInterceptor(auth).build()
    }
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepoModule {
    @Binds
    abstract fun bindRepo(impl: RemoteRepo): Repo  // BAD

    @Binds
    @Named("cache")
    abstract fun bindCacheRepo(impl: CacheRepo): Repo
}
