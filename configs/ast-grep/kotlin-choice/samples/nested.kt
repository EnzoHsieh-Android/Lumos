// 巢狀運算:外層與內層各自是一個節點(換成別的運算子時要加括號保持結構,計劃〈用詞〉)
package sample

fun nested(x: Int, a: Int, b: Int, limit: Int) {
    val t = x + a * b // HIT C-11 C-13
    if (x.size + 1 > limit) go() // HIT C-1 C-11
    if (a > 0
        && b < 3) go() // HIT C-2
    val s = "x ${a < b}" // HIT C-2
    val u = "id=" + x // HIT C-11
}
