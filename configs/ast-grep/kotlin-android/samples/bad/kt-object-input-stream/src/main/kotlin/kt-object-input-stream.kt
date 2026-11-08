fun readOne(socket: Socket): Any? {
    return ObjectInputStream(socket.getInputStream()).readObject() // BAD 網路來的資料
}
fun readTwo(file: File): Any? {
    return java.io.ObjectInputStream(FileInputStream(file)).use { it.readObject() } // BAD 外部檔案
}
