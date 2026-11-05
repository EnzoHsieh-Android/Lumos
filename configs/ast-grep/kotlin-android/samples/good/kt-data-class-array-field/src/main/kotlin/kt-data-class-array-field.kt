package good

data class Packet(val bytes: ByteArray) {
    override fun equals(other: Any?) = other is Packet && bytes.contentEquals(other.bytes)
    override fun hashCode() = bytes.contentHashCode()
}
data class Pixels(val data: List<Int>)
class Raw(val bytes: ByteArray)
