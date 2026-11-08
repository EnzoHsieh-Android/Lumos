fun encryptOne(pub: PublicKey, data: ByteArray): ByteArray {
    val c = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding") // GOOD
    c.init(Cipher.ENCRYPT_MODE, pub)
    return c.doFinal(data)
}
fun encryptTwo(key: SecretKey, data: ByteArray): ByteArray {
    val c = Cipher.getInstance("AES/GCM/NoPadding") // GOOD 不是 RSA
    c.init(Cipher.ENCRYPT_MODE, key)
    return c.doFinal(data)
}
