val logger = HttpLoggingInterceptor().setLevel(HttpLoggingInterceptor.Level.BODY) // BAD
fun build() = OkHttpClient.Builder()
    .addInterceptor(HttpLoggingInterceptor().apply { level = Level.BODY }) // BAD
    .build()
