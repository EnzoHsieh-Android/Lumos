val sharedClient = OkHttpClient.Builder().callTimeout(10, TimeUnit.SECONDS).build() // GOOD 頂層單例

class Repo(private val client: OkHttpClient) {
    private val slow by lazy { client.newBuilder().readTimeout(60, TimeUnit.SECONDS).build() } // GOOD newBuilder 衍生
}

@Module
object NetModule {
    @Provides @Singleton
    fun provideClient(): OkHttpClient = OkHttpClient.Builder().callTimeout(10, TimeUnit.SECONDS).build() // GOOD DI 提供
}

fun createClient(): OkHttpClient { // GOOD 工廠函式,回傳型別就是 OkHttpClient
    return OkHttpClient.Builder().callTimeout(10, TimeUnit.SECONDS).build()
}
