fun encryptOne(key: SecretKey, data: ByteArray): Pair<ByteArray, ByteArray> {
    val iv = ByteArray(16).also { SecureRandom().nextBytes(it) }
    val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
    cipher.init(Cipher.ENCRYPT_MODE, key, IvParameterSpec(iv)) // GOOD 每次新的 IV
    return iv to cipher.doFinal(data)
}
fun decryptOne(key: SecretKey, iv: ByteArray, data: ByteArray): ByteArray {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv)) // GOOD 用跟密文一起存的 IV
    return cipher.doFinal(data)
}
