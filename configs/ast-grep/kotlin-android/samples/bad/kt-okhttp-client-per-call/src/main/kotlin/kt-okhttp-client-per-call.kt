class Repo {
    fun fetch(url: String): String {
        val client = OkHttpClient() // BAD
        return client.newCall(Request.Builder().url(url).build()).execute().use { it.body!!.string() }
    }
    fun fetch2(url: String) = OkHttpClient.Builder() // BAD
        .callTimeout(10, TimeUnit.SECONDS)
        .build()
        .newCall(Request.Builder().url(url).build())
}
