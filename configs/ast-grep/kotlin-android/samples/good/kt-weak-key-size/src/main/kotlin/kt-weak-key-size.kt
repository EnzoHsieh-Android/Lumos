fun genOne(): KeyPair {
    val g = KeyPairGenerator.getInstance("RSA")
    g.initialize(3072) // GOOD
    return g.generateKeyPair()
}
fun genTwo(): SecretKey {
    val kg = KeyGenerator.getInstance("AES")
    kg.init(256) // GOOD
    return kg.generateKey()
}
fun genThree(): KeyPair {
    val g = KeyPairGenerator.getInstance("EC")
    g.initialize(256) // GOOD EC 256 位元夠
    return g.generateKeyPair()
}
