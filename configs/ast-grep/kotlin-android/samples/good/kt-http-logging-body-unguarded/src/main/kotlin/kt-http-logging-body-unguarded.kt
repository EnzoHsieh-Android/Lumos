val logger = HttpLoggingInterceptor().apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY else HttpLoggingInterceptor.Level.NONE // GOOD
    redactHeader("Authorization")
}
fun build(): OkHttpClient {
    val b = OkHttpClient.Builder()
    if (BuildConfig.DEBUG) {
        b.addInterceptor(HttpLoggingInterceptor().setLevel(Level.BODY)) // GOOD
    }
    b.addInterceptor(HttpLoggingInterceptor().setLevel(Level.BASIC)) // GOOD 不是 BODY
    return b.build()
}
