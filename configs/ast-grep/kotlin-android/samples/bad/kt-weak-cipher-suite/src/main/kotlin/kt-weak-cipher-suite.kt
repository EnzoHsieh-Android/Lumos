fun specOne(): ConnectionSpec = ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
    .cipherSuites(CipherSuite.TLS_RSA_WITH_RC4_128_SHA, CipherSuite.TLS_RSA_WITH_3DES_EDE_CBC_SHA) // BAD RC4、3DES
    .build()
fun specTwo(socket: SSLSocket) {
    socket.setEnabledCipherSuites(arrayOf("TLS_RSA_WITH_NULL_SHA256")) // BAD NULL 加密
}
