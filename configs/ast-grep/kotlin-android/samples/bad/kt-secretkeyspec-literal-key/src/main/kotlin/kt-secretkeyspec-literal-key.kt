fun keyFromString(): SecretKeySpec =
    SecretKeySpec("0123456789abcdef".toByteArray(), "AES") // BAD 字串字面值轉位元組
fun keyFromBytes(): List<SecretKeySpec> = listOf(
    SecretKeySpec(byteArrayOf(0x48, 0x65, 0x21.toByte()), "AES"), // BAD 整數字面值的 byteArrayOf
    javax.crypto.spec.SecretKeySpec(key = "38346591".encodeToByteArray(), algorithm = "DES"), // BAD 具名參數、完整套件名
)
