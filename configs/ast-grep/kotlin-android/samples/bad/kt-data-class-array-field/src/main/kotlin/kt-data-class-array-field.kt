package bad

data class Packet(
    val bytes: ByteArray, // BAD
    val ids: Array<String>?, // BAD
)
data class Pixels(val data: IntArray) { // BAD
    fun size() = data.size
}
