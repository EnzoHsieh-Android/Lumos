fun a(f: File): Int {
    val ins = FileInputStream(f) // BAD
    return ins.read()
}
fun b(ctx: Context, uri: Uri) = BitmapFactory.decodeStream(ctx.contentResolver.openInputStream(uri)) // BAD
