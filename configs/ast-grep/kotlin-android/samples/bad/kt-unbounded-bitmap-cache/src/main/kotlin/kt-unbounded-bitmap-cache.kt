package bad

object ImageCache {
    private val cache = HashMap<String, Bitmap>() // BAD
    private val byUrl = mutableMapOf<String, Bitmap>() // BAD
    private val typed: MutableMap<Int, Bitmap> = mutableMapOf() // BAD
    private val concurrent = ConcurrentHashMap<String, Bitmap?>() // BAD
}
