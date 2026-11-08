fun encryptOne(key: SecretKey, data: ByteArray): ByteArray {
    val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
    cipher.init(Cipher.ENCRYPT_MODE, key, IvParameterSpec(byteArrayOf(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))) // BAD 全零 IV
    return cipher.doFinal(data)
}
fun encryptTwo(key: SecretKey, data: ByteArray): ByteArray {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.ENCRYPT_MODE, key, GCMParameterSpec(128, "fixed-nonce1".toByteArray())) // BAD 寫死 nonce
    return cipher.doFinal(data)
}
