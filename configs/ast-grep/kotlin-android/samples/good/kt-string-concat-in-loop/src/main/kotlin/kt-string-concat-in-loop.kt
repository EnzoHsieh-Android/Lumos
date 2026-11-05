package good

fun csv(rows: List<Row>): String {
    val s = buildString { for (r in rows) append(r.id).append(',') }
    var n = 0
    for (r in rows) n += r.count { it == "a" }
    var total = 0
    rows.forEach { total += it.size }
    var head = ""
    head += "title"
    return s + head + n + total
}

// 容易誤報:用 joinToString 拼;迴圈裡 += 的是數字
fun joinIds(rows: List<Row>): String {
    var count = 0
    for (r in rows) count += 1 // GOOD
    return rows.joinToString(",") { it.id } + count // GOOD
}
