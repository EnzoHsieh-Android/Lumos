// 文法不認得的語法:ERROR 節點(跟它重疊或同一行的選擇點,lumos 略過)
package sample

fun broken(a: Int, b: Int) {
    val ok = a > b // HIT C-1
    if (a > 上限) z() // HIT syntax-error
    val bad = (a + // HIT syntax-error
}
