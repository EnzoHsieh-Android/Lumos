package good

object ImageCache {
    private val cache = object : LruCache<String, Bitmap>(maxKb) {
        override fun sizeOf(key: String, value: Bitmap) = value.byteCount / 1024
    }
    private val names = HashMap<String, String>()
    private val fixed: Map<String, Bitmap> = mapOf("a" to placeholder)
    fun show(m: Map<String, Bitmap>) = m.size
}

// 容易誤報:Map 的值是 Job / 載入請求,不是 Bitmap
class ThumbLoader {
    private val pending = HashMap<String, Job>() // GOOD
    private val requests = mutableMapOf<String, BitmapRequest>() // GOOD
}
