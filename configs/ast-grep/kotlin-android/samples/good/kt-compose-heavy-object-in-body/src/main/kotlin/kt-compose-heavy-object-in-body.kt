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
