fun plainClient(): OkHttpClient = OkHttpClient.Builder().build() // BAD

// BAD:只設連線與讀取,整個呼叫仍沒上限
fun tunedClient(): OkHttpClient = OkHttpClient.Builder()
    .connectTimeout(10, TimeUnit.SECONDS)
    .readTimeout(10, TimeUnit.SECONDS)
    .build()
