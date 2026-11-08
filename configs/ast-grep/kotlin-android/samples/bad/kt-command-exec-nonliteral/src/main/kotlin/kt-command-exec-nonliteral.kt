fun pingOne(host: String) {
    Runtime.getRuntime().exec("ping -c 1 " + host) // BAD 串接
    Runtime.getRuntime().exec("ping -c 1 $host") // BAD 字串樣板帶插值
    Runtime.getRuntime().exec(String.format("ping -c 1 %s", host)) // BAD String.format
}
fun rootOne(cmd: String) {
    ProcessBuilder("su", "-c", cmd).start() // BAD -c 後面接非字面值
    Runtime.getRuntime().exec(arrayOf("sh", "-c", cmd)) // BAD exec 的陣列參數
}
