package bad

class Thumbs {
    fun thumb(path: String) = BitmapFactory.decodeFile(path) // BAD
    fun icon(res: Resources) = BitmapFactory.decodeResource(res, R.drawable.big) // BAD
    fun fromStream(s: InputStream) = BitmapFactory.decodeStream(s) // BAD
    fun fromBytes(b: ByteArray) = BitmapFactory.decodeByteArray(b, 0, b.size) // BAD
}
