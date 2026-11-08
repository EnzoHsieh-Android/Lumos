fun hashOne(data: ByteArray): ByteArray {
    return MessageDigest.getInstance("SHA-256").digest(data) // GOOD
}
fun hashTwo(data: ByteArray): ByteArray {
    return MessageDigest.getInstance("SHA-512").digest(data) // GOOD
}
