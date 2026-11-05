package good

private val DIGITS = Regex("[0-9]+")

@Composable
fun Row1(t: Long, s: String) {
    val fmt = remember { SimpleDateFormat("yyyy-MM-dd", Locale.US) }
    val ok = DIGITS.matches(s)
    Button(onClick = { Regex("x").find(s) }) { }
    val d = remember { DateTimeFormatter.ofPattern("HH:mm") }
}

object Fmt { val df = DecimalFormat("#,##0") }

// 容易誤報(代碼審 r1 M4):繪製 lambda 在 draw 階段跑,不是重組
@Composable
fun Chart() {
    Canvas(Modifier) { val p = Path(); drawPath(p, Color.Red) }
    Box(Modifier.drawBehind { val q = Paint() })
    Box(Modifier.drawWithCache { val path = Path(); onDrawBehind { drawPath(path, Color.Red) } })
}
