fun a(f: File): Int = FileInputStream(f).use { it.read() } // GOOD
fun b(ctx: Context, uri: Uri) = ctx.contentResolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, BitmapFactory.Options().apply { inSampleSize = 4 }) } // GOOD
fun c(f: File) {
    val out = FileOutputStream(f) // GOOD finally close
    try { out.write(1) } finally { out.close() }
}
