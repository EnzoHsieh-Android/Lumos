fun unzipOne(zis: ZipInputStream, destDir: File) {
    var entry = zis.nextEntry
    while (entry != null) {
        val f = File(destDir, entry.name)
        if (!f.canonicalPath.startsWith(destDir.canonicalPath + File.separator)) throw SecurityException() // GOOD 官方建議的檢查
        f.outputStream().use { zis.copyTo(it) }
        entry = zis.nextEntry
    }
}
fun unzipTwo(ctx: Context, destDir: File) {
    val zis = ZipInputStream(ctx.assets.open("seed.zip")) // GOOD App 內建資源
    var entry = zis.nextEntry
    while (entry != null) {
        File(destDir, entry.name).outputStream().use { zis.copyTo(it) }
        entry = zis.nextEntry
    }
}
