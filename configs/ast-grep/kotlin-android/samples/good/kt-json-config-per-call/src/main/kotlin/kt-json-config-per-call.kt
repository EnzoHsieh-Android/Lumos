val json = Json { ignoreUnknownKeys = true } // GOOD 頂層
class Api {
    private val j by lazy { Json { ignoreUnknownKeys = true } } // GOOD lazy 屬性
}
@Provides
fun provideJson(): Json = Json { ignoreUnknownKeys = true } // GOOD DI
