fun readOne(ctx: Context): Any? {
    return ObjectInputStream(ctx.openFileInput("state.bin")).use { it.readObject() } // GOOD App 私有檔
}
fun deepCopy(src: Serializable): Any? {
    val bos = ByteArrayOutputStream()
    ObjectOutputStream(bos).use { it.writeObject(src) }
    return ObjectInputStream(ByteArrayInputStream(bos.toByteArray())).readObject() // GOOD 記憶體內深複製
}
