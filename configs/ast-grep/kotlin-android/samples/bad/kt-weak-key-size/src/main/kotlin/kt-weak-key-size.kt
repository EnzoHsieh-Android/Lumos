fun genOne(): KeyPair {
    val g = KeyPairGenerator.getInstance("RSA")
    g.initialize(1024) // BAD RSA 1024
    return g.generateKeyPair()
}
fun genTwo(): SecretKey {
    val kg = KeyGenerator.getInstance("AES")
    kg.init(64) // BAD 對稱金鑰 64 位元
    return kg.generateKey()
}
