class DocProvider : ContentProvider() {
    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor? {
        val file = File(context!!.filesDir, uri.path!!) // BAD 直接用呼叫端給的路徑
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }
}
class ImgProvider : ContentProvider() {
    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor? {
        val name = uri.lastPathSegment
        val file = File(context!!.cacheDir, name) // BAD 經區域變數
        return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
    }
}
