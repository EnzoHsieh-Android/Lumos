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

// 容易誤報(代碼審 r1 m4):用 when 判 DEBUG
val whenLogger = HttpLoggingInterceptor().apply {
    level = when { BuildConfig.DEBUG -> HttpLoggingInterceptor.Level.BODY else -> HttpLoggingInterceptor.Level.NONE } // GOOD
}
