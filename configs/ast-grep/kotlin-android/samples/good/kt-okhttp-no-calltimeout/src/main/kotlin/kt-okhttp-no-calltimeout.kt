fun plainClient(): OkHttpClient = OkHttpClient.Builder().callTimeout(30, TimeUnit.SECONDS).build() // GOOD

// 容易誤報:callTimeout 夾在一長串設定中間,不在最後一個
fun tunedClient(): OkHttpClient = OkHttpClient.Builder()
    .connectTimeout(10, TimeUnit.SECONDS)
    .callTimeout(30, TimeUnit.SECONDS)
    .readTimeout(10, TimeUnit.SECONDS)
    .build()

// 容易誤報:別的 Builder(Request)的 build() 不是 OkHttpClient
fun request(url: String): Request = Request.Builder().url(url).build()
