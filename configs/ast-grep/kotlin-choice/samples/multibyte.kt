// 多位元組字元:ast-grep 報的是 UTF-8 位元組位移,lumos 照位元組切原文(中文識別字 tree-sitter-kotlin 認不得,見 error.kt)
package sample

fun calc(é2: Int, limit: Int) {
    val é = "ü價格"; if (é2 > limit) z() // HIT C-1
    val 名 = "價格 " + é2 // HIT C-11
}
