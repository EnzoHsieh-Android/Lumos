fun save(f: File, json: String) {
    f.writeText(json) // BAD
}
fun save2(path: String, bytes: ByteArray) = File(path).writeBytes(bytes) // BAD
