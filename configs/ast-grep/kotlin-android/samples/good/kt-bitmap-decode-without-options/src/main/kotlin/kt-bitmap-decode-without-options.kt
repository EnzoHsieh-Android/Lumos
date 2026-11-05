package good

class Thumbs {
    fun thumb(path: String, opts: BitmapFactory.Options) = BitmapFactory.decodeFile(path, opts)
    fun icon(res: Resources) = BitmapFactory.decodeResource(res, R.drawable.big, sampled(4))
    fun fromBytes(b: ByteArray, o: BitmapFactory.Options) = BitmapFactory.decodeByteArray(b, 0, b.size, o)
    fun file(path: String) = File(path).decodeFile()
}

// 容易誤報:兩次 decodeFile 都帶 Options,先 inJustDecodeBounds 量尺寸再按 inSampleSize 解碼
fun decodeSampled(path: String, reqWidth: Int, reqHeight: Int): Bitmap? {
    val opts = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    BitmapFactory.decodeFile(path, opts)
    opts.inSampleSize = sampleSize(opts.outWidth, opts.outHeight, reqWidth, reqHeight)
    opts.inJustDecodeBounds = false
    return BitmapFactory.decodeFile(path, opts) // GOOD
}
