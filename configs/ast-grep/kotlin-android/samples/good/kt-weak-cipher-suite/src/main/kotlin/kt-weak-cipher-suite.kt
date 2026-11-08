fun specOne(): ConnectionSpec = ConnectionSpec.Builder(ConnectionSpec.MODERN_TLS)
    .cipherSuites(CipherSuite.TLS_AES_128_GCM_SHA256, CipherSuite.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256) // GOOD
    .build()
fun specTwo(socket: SSLSocket) {
    socket.setEnabledCipherSuites(arrayOf("TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384")) // GOOD
}
