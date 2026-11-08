fun unzipOne(zis: ZipInputStream, destDir: File) {
    var entry = zis.nextEntry
    while (entry != null) {
        val f = File(destDir, entry.name) // BAD 名稱直接組路徑
        f.outputStream().use { zis.copyTo(it) }
        entry = zis.nextEntry
    }
}
fun unzipTwo(zip: ZipFile, destDir: File) {
    for (e in zip.entries()) {
        destDir.resolve(e.name).outputStream().use { out -> zip.getInputStream(e).copyTo(out) } // BAD resolve
    }
}
