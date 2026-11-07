fun keyFromKeystore(): SecretKey {
    val gen = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore") // GOOD 金鑰在 Keystore 產生
    gen.init(KeyGenParameterSpec.Builder("k", KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT).build())
    return gen.generateKey()
}
fun keyFromRuntime(secret: String, raw: ByteArray, x: Byte, y: Byte): List<SecretKeySpec> = listOf(
    SecretKeySpec("$secret&".toByteArray(), "HmacSHA1"), // GOOD 執行時組出來的(OAuth 簽章金鑰)
    SecretKeySpec(raw, "AES"), // GOOD 變數
    SecretKeySpec(byteArrayOf(x, y), "AES"), // GOOD byteArrayOf(變數)
    SecretKeySpec(byteArrayOf(*raw), "AES"), // GOOD 展開
)
