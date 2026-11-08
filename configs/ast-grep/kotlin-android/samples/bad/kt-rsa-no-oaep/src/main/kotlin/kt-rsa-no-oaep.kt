fun encryptOne(pub: PublicKey, data: ByteArray): ByteArray {
    val c = Cipher.getInstance("RSA/ECB/NoPadding") // BAD 無填充
    c.init(Cipher.ENCRYPT_MODE, pub)
    return c.doFinal(data)
}
fun encryptTwo(pub: PublicKey, data: ByteArray): ByteArray {
    val c = javax.crypto.Cipher.getInstance("RSA") // BAD 沒指定填充
    c.init(Cipher.ENCRYPT_MODE, pub)
    return c.doFinal(data)
}
