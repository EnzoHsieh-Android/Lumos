fun save(f: File, json: String) {
    val tmp = File(f.parentFile, f.name + ".tmp")
    tmp.writeText(json) // GOOD 暫存再改名
    tmp.renameTo(f)
}
fun save2(af: AtomicFile, bytes: ByteArray) { // GOOD
    val out = af.startWrite()
    out.write(bytes)
    af.finishWrite(out)
}
