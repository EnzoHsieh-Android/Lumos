fun oldContext(): SSLContext {
    val a = SSLContext.getInstance("TLSv1") // BAD
    val b = javax.net.ssl.SSLContext.getInstance("SSLv3", "AndroidOpenSSL") // BAD 兩參數版、完整套件名
    return SSLContext.getInstance("TLSv1.1") // BAD
}
fun oldOkHttp(socket: SSLSocket): List<ConnectionSpec> {
    socket.setEnabledProtocols(arrayOf("TLSv1", "TLSv1.2")) // BAD 陣列裡有舊版本
    val spec = ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
        .tlsVersions(TlsVersion.TLS_1_0) // BAD 分行寫的 tlsVersions
        .build()
    return listOf(spec, ConnectionSpec.COMPATIBLE_TLS) // BAD
}
