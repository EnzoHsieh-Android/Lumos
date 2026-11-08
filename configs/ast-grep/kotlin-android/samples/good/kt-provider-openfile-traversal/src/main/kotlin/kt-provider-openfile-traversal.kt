class DocProvider : ContentProvider() {
    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor? {
        val base = context!!.filesDir
        val file = File(base, uri.path!!)
        if (!file.canonicalPath.startsWith(base.canonicalPath + File.separator)) throw SecurityException() // GOOD
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }
}
class FixedProvider : ContentProvider() {
    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor? {
        val file = File(context!!.filesDir, "export.json") // GOOD 固定檔名
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }
}
