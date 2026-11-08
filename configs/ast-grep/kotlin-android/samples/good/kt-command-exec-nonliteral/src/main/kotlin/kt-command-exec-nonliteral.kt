fun listOne() {
    Runtime.getRuntime().exec("ls") // GOOD 純字面值
    Runtime.getRuntime().exec(arrayOf("ls", "-l")) // GOOD 字面值陣列
}
fun pingOne(host: String) {
    require(host.matches(Regex("^[a-z0-9.-]+$")))
    ProcessBuilder("ping", "-c", "1", host).start() // GOOD 使用者資料當獨立參數、不經 shell
    ProcessBuilder("su", "-c", "id").start() // GOOD -c 後面是字面值
}
