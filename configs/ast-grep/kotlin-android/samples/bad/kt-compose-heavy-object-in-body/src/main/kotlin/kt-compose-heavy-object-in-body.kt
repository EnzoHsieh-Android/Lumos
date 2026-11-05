package bad

@Composable
fun Row1(t: Long, s: String) {
    val fmt = SimpleDateFormat("yyyy-MM-dd", Locale.US) // BAD
    val ok = Regex("[0-9]+").matches(s) // BAD
    Canvas(Modifier) {
        val p = Paint() // BAD
    }
    val d = DateTimeFormatter.ofPattern("HH:mm") // BAD
    val r = "a+".toRegex() // BAD
}
