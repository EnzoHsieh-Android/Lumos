fun hashOne(pw: String): ByteArray {
    return MessageDigest.getInstance("MD5").digest(pw.toByteArray()) // BAD MD5
}
fun hashTwo(data: ByteArray): ByteArray {
    return java.security.MessageDigest.getInstance("SHA-1").digest(data) // BAD SHA-1
}
