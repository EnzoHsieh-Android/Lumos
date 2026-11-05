fun plainClient(): OkHttpClient = OkHttpClient.Builder().build() // BAD

// BAD:只設連線與讀取,整個呼叫仍沒上限
fun tunedClient(): OkHttpClient = OkHttpClient.Builder()
    .connectTimeout(10, TimeUnit.SECONDS)
    .readTimeout(10, TimeUnit.SECONDS)
    .build()

// BAD:Retrofit 包著沒設上限的 OkHttpClient,只該在內層 build() 報一次(代碼審 r1 m2)
fun retrofit(): Retrofit = Retrofit.Builder().client(OkHttpClient.Builder().build()).build()
