fun newContext(): SSLContext {
    val a = SSLContext.getInstance("TLS") // GOOD 交給系統挑版本
    val b = SSLContext.getInstance("TLSv1.2") // GOOD
    return SSLContext.getInstance("SSL") // GOOD Android 上回傳的仍是 TLS 1.2 以上
}
fun newOkHttp(socket: SSLSocket): List<ConnectionSpec> {
    socket.setEnabledProtocols(arrayOf("TLSv1.2", "TLSv1.3")) // GOOD
    val spec = ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
        .tlsVersions(TlsVersion.TLS_1_3, TlsVersion.TLS_1_2) // GOOD
        .build()
    val suites = ConnectionSpec.COMPATIBLE_TLS.cipherSuites // GOOD 只讀屬性、沒拿來啟用
    println(suites)
    return listOf(spec, ConnectionSpec.MODERN_TLS) // GOOD
}
