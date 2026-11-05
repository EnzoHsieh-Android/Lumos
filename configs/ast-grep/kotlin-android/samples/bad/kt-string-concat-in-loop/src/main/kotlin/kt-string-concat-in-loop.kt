package bad

fun csv(rows: List<Row>): String {
    var s = ""
    for (r in rows) s += "${r.id}," // BAD
    rows.forEach { s += it.name + ";" } // BAD
    var i = 0
    while (i < 3) {
        s = s + "x" + i // BAD
        i++
    }
    return s
}
