package good

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Named("plain")
    fun provideClient(): OkHttpClient {
        return OkHttpClient()
    }

    @Provides
    @Named("auth")
    fun provideAuthClient(auth: AuthInterceptor): OkHttpClient {
        return OkHttpClient.Builder().addInterceptor(auth).build()
    }
}

// 容易誤報:多重綁定(@IntoSet)不是限定詞,跟一般綁定並存是合法寫法,這條不報
@Module
@InstallIn(SingletonComponent::class)
object InterceptorModule {
    @Provides
    fun provideLogging(): Interceptor {
        return HttpLoggingInterceptor()
    }

    @Provides
    @IntoSet
    fun provideAuthToSet(): Interceptor {
        return AuthInterceptor()
    }
}

// 容易誤報:@Suppress 不是限定詞,單檔判不準的註解兩邊都不算
@Module
@InstallIn(SingletonComponent::class)
object JsonModule {
    @Provides
    fun provideGson(): Gson {
        return Gson()
    }

    @Provides
    @Suppress("DEPRECATION")
    fun provideLegacyGson(): Gson {
        return GsonBuilder().create()
    }
}
